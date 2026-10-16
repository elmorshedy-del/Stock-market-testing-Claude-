"""Pre-registered tests A-D (README). Writes out/results.json and the tables in out/.

python tests.py           everything (Part A needs data/channels_boot.pkl from `channels_panel.py --boot 20`)
"""
import json
import math
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

from fetch_data import STOCKS

HERE = Path(__file__).parent
DATA, OUT = HERE / "data", HERE / "out"
PRIMARY = ["FF_HIKE", "Y10_UP", "CURVE_FLAT", "USD_UP", "M2_SLOW", "MKT_EXT", "MARGIN_FROTH", "COMPOSITE"]
SECONDARY = ["LIQ_DRAIN", "TIPS_UP", "CREDIT_WIDEN", "GEX_LOW", "INV_GLUT"]
BASE = dict(W=84, ztop=0.5, H=24, cut=2 / 3)
SPECS = [dict(W=W, ztop=z, H=H, cut=c) for W, z, H, c in product((60, 84, 120), (0.33, 0.5, 0.67), (12, 24), (2 / 3, 0.5))]
NDRAW = 1000
SEED = 20261015
SPLIT = {"primary": pd.Timestamp("2010-01-01"), "secondary": pd.Timestamp("2018-01-01")}


# ------------------------------------------------------------------ inputs
def load():
    ch = pd.read_pickle(DATA / "channels.pkl")
    macro = pd.read_csv(OUT / "macro_monthly.csv", parse_dates=["month"], index_col="month")
    inv = pd.read_csv(OUT / "inventory_gap.csv", parse_dates=["end", "known"])
    return ch, macro, inv


def trailing_pct(x, win=120, minp=36):
    """Fraction of the trailing `win` values (incl. today) that are <= today's value; NaN if fewer than minp."""
    v = x.to_numpy(float)
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        if np.isnan(v[i]):
            continue
        w = v[max(0, i - win + 1):i + 1]
        w = w[~np.isnan(w)]
        if len(w) >= minp:
            out[i] = (w <= v[i]).mean()
    return pd.Series(out, index=x.index)


def raw_variables(macro, ch, W):
    m = macro.copy()
    # monthly-average rates for the running month are not out yet: carry last month's for the partial row only
    for c in ("ff", "gs10", "gs3m", "curve", "m2_yoy", "margin_yoy"):
        m[c] = m[c].ffill(limit=1)
    v = pd.DataFrame(index=m.index)
    v["FF_HIKE"] = m.ff - m.ff.shift(12)
    v["Y10_UP"] = m.gs10 - m.gs10.shift(6)
    v["CURVE_FLAT"] = -m.curve
    v["USD_UP"] = np.log(m.dxy / m.dxy.shift(6))
    v["M2_SLOW"] = -m.m2_yoy
    ndx = ch[(ch.symbol == "^NDX") & (ch.W == W)].set_index("month").z
    v["MKT_EXT"] = ndx.reindex(v.index)
    v["MARGIN_FROTH"] = m.margin_yoy
    v["LIQ_DRAIN"] = -np.log(m.netliq / m.netliq.shift(6))
    v["TIPS_UP"] = m.tips10 - m.tips10.shift(6)
    v["CREDIT_WIDEN"] = -m.hyg_ief_6m
    v["GEX_LOW"] = -m.gex_bn
    return v


def inv_monthly(inv, months):
    """Per stock: latest inventory gap whose filing date is on or before each month end."""
    out = {}
    for s, g in inv.groupby("symbol"):
        g = g.sort_values("known")
        known = g.known.to_numpy("datetime64[ns]")
        vals = g.inv_gap.to_numpy(float)
        pos = np.searchsorted(known, months.to_numpy("datetime64[ns]"), side="right") - 1
        x = np.where(pos >= 0, vals[np.clip(pos, 0, None)], np.nan)
        # stale after 9 months without a new filing
        age = np.where(pos >= 0, (months.to_numpy("datetime64[ns]") - known[np.clip(pos, 0, None)]).astype("timedelta64[D]").astype(float), np.nan)
        x[age > 270] = np.nan
        out[s] = pd.Series(x, index=months)
    return pd.DataFrame(out)


def signals(raw, invm, cut):
    """Percentile signals (1 = theorised bearish reading in top `cut` region), NaN where undefined."""
    sig = pd.DataFrame(index=raw.index)
    for c in raw.columns:
        p = trailing_pct(raw[c])
        sig[c] = np.where(p.isna(), np.nan, (p >= cut).astype(float))
    prim = [c for c in PRIMARY if c != "COMPOSITE"]
    avail = sig[prim].notna().sum(axis=1)
    on = sig[prim].sum(axis=1)
    sig["COMPOSITE"] = np.where(avail >= 3, (on >= avail / 2).astype(float), np.nan)
    inv_sig = pd.DataFrame({s: (lambda p: np.where(p.isna(), np.nan, (p >= cut).astype(float)))(trailing_pct(invm[s]))
                            for s in invm.columns}, index=invm.index)
    return sig, inv_sig


# ------------------------------------------------------------------ panel rows for one spec
def rows_for(ch, spec, outcome="rev"):
    c = ch[(ch.W == spec["W"]) & ch.symbol.isin(STOCKS) & ch.valid & ~ch.partial & (ch.z >= spec["ztop"])].copy()
    tcol = "t_rev" if outcome == "rev" else "t_brk"
    hit = c[tcol] <= spec["H"]
    resolved = hit | (c.n_fwd >= spec["H"])
    c = c[resolved].copy()
    c["y"] = (c[tcol] <= spec["H"]).astype(float)
    return c[["symbol", "month", "z", "y"]].reset_index(drop=True)


class ShiftIndex:
    """Circular shift of a signal series within its own non-NaN window, by a fraction f of the window length."""

    def __init__(self, series):
        ok = series.notna().to_numpy()
        if not ok.any():
            self.L = 0
            return
        i0, i1 = np.argmax(ok), len(ok) - np.argmax(ok[::-1])
        self.start = series.index[i0]
        self.vals = series.to_numpy(float)[i0:i1]
        self.L = i1 - i0
        self.pos = {m: k for k, m in enumerate(series.index[i0:i1])}

    def positions(self, months):
        return np.array([self.pos.get(m, -1) for m in months])

    def values(self, pos, f):
        k = int(round(f * self.L)) if f else 0
        out = np.full(len(pos), np.nan)
        ok = pos >= 0
        out[ok] = self.vals[(pos[ok] + k) % self.L]
        return out


def delta(y, s):
    ok = ~np.isnan(s)
    y, s = y[ok], s[ok]
    if (s == 1).sum() < 5 or (s == 0).sum() < 5:
        return np.nan
    return y[s == 1].mean() - y[s == 0].mean()


def var_values(name, rows, sig, inv_sig, f, cache):
    """Signal value for each panel row, under shift fraction f (0 = real)."""
    if name == "INV_GLUT":
        if "INV_plan" not in cache:
            plan = []
            for s, idx in rows.groupby("symbol").indices.items():
                if s not in inv_sig.columns:
                    continue
                si = ShiftIndex(inv_sig[s])
                if si.L == 0:
                    continue
                plan.append((idx, si, si.positions(rows.month.to_numpy()[idx])))
            cache["INV_plan"] = plan
        out = np.full(len(rows), np.nan)
        for idx, si, pos in cache["INV_plan"]:
            out[idx] = si.values(pos, f)
        return out
    key = ("M", name)
    if key not in cache:
        cache[key] = ShiftIndex(sig[name])
    si = cache[key]
    pkey = ("P", name, id(rows))
    if pkey not in cache:
        cache[pkey] = si.positions(rows.month.to_numpy())
    return si.values(cache[pkey], f)


# ------------------------------------------------------------------ Part B
def part_b(ch, raw_by_w, invm, fracs, outcome="rev", flip=False):
    res = {}
    spec_rows = {}
    spec_sig = {}
    sig_cache = {}
    for sp in SPECS:
        key = (sp["W"], sp["ztop"], sp["H"], sp["cut"])
        spec_rows[key] = rows_for(ch, sp, outcome)
        sk = (sp["W"], sp["cut"])
        if sk not in sig_cache:
            raw = raw_by_w[sp["W"]] * (-1 if flip else 1)
            im = invm * (-1 if flip else 1)
            sig_cache[sk] = signals(raw, im, sp["cut"])
        spec_sig[key] = sig_cache[sk]
    names = PRIMARY + SECONDARY
    # obs and null deltas per spec
    D = {}   # (name, key) -> array [obs, null...]
    for key, rows in spec_rows.items():
        sig, inv_sig = spec_sig[key]
        cache = {}
        y = rows.y.to_numpy()
        for nme in names:
            arr = np.empty(len(fracs) + 1)
            arr[0] = delta(y, var_values(nme, rows, sig, inv_sig, 0, cache))
            for d, f in enumerate(fracs):
                arr[d + 1] = delta(y, var_values(nme, rows, sig, inv_sig, f, cache))
            D[(nme, key)] = arr
    base_key = (BASE["W"], BASE["ztop"], BASE["H"], BASE["cut"])
    rows = spec_rows[base_key]
    sig, inv_sig = spec_sig[base_key]
    cache = {}
    for nme in names:
        fam = "primary" if nme in PRIMARY else "secondary"
        arr = D[(nme, base_key)]
        obs, null = arr[0], arr[1:]
        null_ok = null[~np.isnan(null)]
        s = var_values(nme, rows, sig, inv_sig, 0, cache)
        ok = ~np.isnan(s)
        y = rows.y.to_numpy()
        early = (rows.month < SPLIT[fam]).to_numpy()
        multi = np.array([D[(nme, k)] for k in spec_rows])           # specs x (1+draws)
        med = np.nanmedian(multi, axis=0)
        res[nme] = {
            "family": fam,
            "n_rows": int(ok.sum()), "n_on": int((s[ok] == 1).sum()),
            "p_rev_on": float(y[ok & (s == 1)].mean()) if (s[ok] == 1).any() else None,
            "p_rev_off": float(y[ok & (s == 0)].mean()) if (s[ok] == 0).any() else None,
            "delta": None if np.isnan(obs) else float(obs),
            "p_shift": float((1 + (null_ok >= obs).sum()) / (1 + len(null_ok))) if not np.isnan(obs) else None,
            "null_mean": float(null_ok.mean()), "null_sd": float(null_ok.std()),
            "delta_early": float(delta(y[early], s[early])) if early.any() else None,
            "delta_late": float(delta(y[~early], s[~early])) if (~early).any() else None,
            "multiverse_median_delta": float(med[0]),
            "multiverse_share_positive": float(np.nanmean(multi[:, 0] > 0)),
            "multiverse_p": float((1 + (med[1:][~np.isnan(med[1:])] >= med[0]).sum()) / (1 + (~np.isnan(med[1:])).sum())),
            "first_month": str(rows.month[ok].min().date()) if ok.any() else None,
            "_null": arr,
        }
    for fam in ("primary", "secondary"):
        fam_names = [n for n in names if res[n]["family"] == fam and res[n]["delta"] is not None]
        Z = np.array([(res[n]["_null"] - res[n]["null_mean"]) / res[n]["null_sd"] for n in fam_names])
        T = np.nanmax(Z, axis=0)
        p = float((1 + (T[1:] >= T[0]).sum()) / (1 + (~np.isnan(T[1:])).sum()))
        for n in fam_names:
            res[n]["family_joint_p"] = p
    nulls = {}
    for n in res:
        r = res[n]
        nulls[n] = r.pop("_null")
        r["passes"] = bool(r["delta"] is not None and r["delta"] > 0 and r["p_shift"] < 0.05
                           and r.get("family_joint_p", 1) < 0.05
                           and (r["delta_early"] or -1) > 0 and (r["delta_late"] or -1) > 0)
        r["fragile"] = bool(r["passes"] and r["multiverse_p"] >= 0.05)
    part_b.nulls = nulls          # obs + null deltas at the base spec, for post-hoc family tests
    return res, spec_rows[base_key], spec_sig[base_key]


# ------------------------------------------------------------------ episodes
def episodes(ch, spec, outcome="rev"):
    c = ch[(ch.W == spec["W"]) & ch.symbol.isin(STOCKS) & ~ch.partial].sort_values(["symbol", "month"]).copy()
    c["top"] = c.valid & (c.z >= spec["ztop"])
    tcol = "t_rev" if outcome == "rev" else "t_brk"
    eps = []
    for s, g in c.groupby("symbol"):
        g = g.reset_index(drop=True)
        mi = g.month.dt.year * 12 + g.month.dt.month
        run = None
        for k in range(len(g)):
            if g.top[k] and run is not None and mi[k] == mi[run[-1]] + 1:
                run.append(k)
            elif g.top[k]:
                if run:
                    eps.append((s, g, run))
                run = [k]
            elif run:
                eps.append((s, g, run))
                run = None
        if run:
            eps.append((s, g, run))
    out = []
    for s, g, run in eps:
        last = g.iloc[run[-1]]
        hit = last[tcol] <= spec["H"]
        if not hit and last.n_fwd < spec["H"]:
            continue
        out.append({"symbol": s, "start": g.month[run[0]], "end": last.month, "months": len(run),
                    "z_max": float(g.z[run].max()), "event": bool(hit),
                    "event_month": last.month + pd.offsets.MonthEnd(int(last[tcol])) if hit else pd.NaT})
    ep = pd.DataFrame(out).sort_values("end").reset_index(drop=True)
    wave, w0 = [], None
    n = 0
    for _, r in ep.iterrows():
        if not r.event:
            wave.append(np.nan)
            continue
        if w0 is None or (r.end - w0).days > 366:
            n += 1
            w0 = r.end
        wave.append(n)
    ep["wave"] = wave
    return ep


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


# ------------------------------------------------------------------ main
def main():
    ch, macro, inv = load()
    rng = np.random.default_rng(SEED)
    fracs = rng.uniform(0.1, 0.9, NDRAW)
    raw_by_w = {W: raw_variables(macro, ch, W) for W in (60, 84, 120)}
    invm = inv_monthly(inv, macro.index)
    results = {"base_spec": BASE, "n_specs": len(SPECS), "n_draws": NDRAW}

    # ---- A: premise vs bootstrap
    rows = rows_for(ch, BASE)
    allrows = ch[(ch.W == 84) & ch.symbol.isin(STOCKS) & ch.valid & ~ch.partial].copy()
    hit = allrows.t_rev <= 24
    allrows = allrows[hit | (allrows.n_fwd >= 24)]
    allrows["y"] = (allrows.t_rev <= 24).astype(float)
    bands = pd.cut(allrows.z, [-np.inf, -0.5, 0, 0.5, np.inf], labels=["<-0.5", "-0.5..0", "0..0.5", ">=0.5"])
    A = {"real_rate_top": float(rows.y.mean()), "n_top_rows": int(len(rows)),
         "rate_by_z_band": allrows.groupby(bands, observed=True).y.agg(["mean", "size"]).round(4).reset_index()
         .astype({"z": str}).to_dict("records")}
    boot_file = DATA / "channels_boot.pkl"
    if boot_file.exists():
        b = pd.read_pickle(boot_file)
        b = b[b.valid & (b.z >= BASE["ztop"])]
        bh = b.t_rev <= 24
        b = b[bh | (b.n_fwd >= 24)]
        b["y"] = (b.t_rev <= 24).astype(float)
        per_path = b.groupby("path").y.mean()
        A.update({"null_rates": per_path.round(4).tolist(), "null_mean": float(per_path.mean()),
                  "null_p95": float(per_path.quantile(0.95)), "null_n_top_rows_per_path": float(b.groupby("path").size().mean())})
        A["passes"] = bool(A["real_rate_top"] - A["null_mean"] >= 0.05 and A["real_rate_top"] > A["null_p95"])
        # same comparison by stock, for the figure
        A["real_by_symbol"] = rows.groupby("symbol").y.mean().round(3).to_dict()
        A["null_by_symbol"] = b.groupby("symbol").y.mean().round(3).to_dict()
    results["A"] = A

    # ---- B: reversion predictors
    B, base_rows, (sig, inv_sig) = part_b(ch, raw_by_w, invm, fracs, "rev")
    results["B"] = B
    ep = episodes(ch, BASE, "rev")
    ep.to_csv(OUT / "episodes_reversion.csv", index=False)
    # episode-level: signal state at the run's last month
    for nme in PRIMARY + SECONDARY:
        vals = []
        for _, r in ep.iterrows():
            if nme == "INV_GLUT":
                v = inv_sig[r.symbol].get(r.end, np.nan) if r.symbol in inv_sig.columns else np.nan
            else:
                v = sig[nme].get(r.end, np.nan)
            vals.append(v)
        ep[nme] = vals
    epi = {}
    for nme in PRIMARY + SECONDARY:
        e = ep.dropna(subset=[nme])
        epi[nme] = {"episodes": int(len(e)), "reverting": int(e.event.sum()),
                    "waves": int(e.loc[e.event, "wave"].nunique()),
                    "on_share_reverting": float(e.loc[e.event, nme].mean()) if e.event.any() else None,
                    "on_share_not": float(e.loc[~e.event, nme].mean()) if (~e.event).any() else None}
    results["B_episodes"] = epi
    results["episode_totals"] = {"episodes": int(len(ep)), "reverting": int(ep.event.sum()),
                                 "waves": int(ep.wave.nunique()),
                                 "wave_years": ep[ep.event].groupby("wave").end.min().dt.strftime("%Y-%m").tolist()}
    ep.to_csv(OUT / "episodes_reversion.csv", index=False)

    # ---- C: breakouts (easing side)
    Cres, _, _ = part_b(ch, raw_by_w, invm, fracs, "brk", flip=True)
    epb = episodes(ch, BASE, "brk")
    epb.to_csv(OUT / "episodes_breakout.csv", index=False)
    results["C"] = {"vars": Cres, "episodes": int(len(epb)), "breakouts": int(epb.event.sum()),
                    "waves": int(epb.wave.nunique()),
                    "wave_years": epb[epb.event].groupby("wave").end.min().dt.strftime("%Y-%m").tolist(),
                    "p_breakout_top": float(rows_for(ch, BASE, "brk").y.mean())}

    # ---- D: NVDA and today
    sig_now = sig.iloc[-1].to_dict()
    raw_now = raw_by_w[84].iloc[-1].to_dict()
    nv = ch[(ch.symbol == "NVDA") & (ch.W == 84)].set_index("month")
    D = {"as_of": str(macro.index[-1].date()), "nvda_now": nv.iloc[-1][["z", "valid", "r2", "growth_yr", "width"]].to_dict(),
         "signals_now": sig_now, "raw_now": raw_now,
         "nvda_inv_glut_now": float(inv_sig["NVDA"].iloc[-1]) if "NVDA" in inv_sig else None}
    for lab, mth in (("top_2018", "2018-09-30"), ("top_2021", "2021-11-30")):
        mth = pd.Timestamp(mth)
        D[lab] = {"nvda": nv.loc[mth, ["z", "valid", "r2", "growth_yr", "width", "t_rev", "t_brk"]].to_dict(),
                  "signals": sig.loc[mth].to_dict(),
                  "inv_glut": float(inv_sig["NVDA"].get(mth, np.nan))}
    comb = base_rows.copy()
    comb["COMPOSITE"] = sig["COMPOSITE"].reindex(comb.month).to_numpy()
    for state in (0.0, 1.0):
        g = comb[comb.COMPOSITE == state]
        lo, hi = wilson(int(g.y.sum()), len(g))
        D[f"p_rev_top_composite_{int(state)}"] = {"n": int(len(g)), "rate": float(g.y.mean()), "ci95": [lo, hi]}
    results["D"] = D

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, float)):
            return None if np.isnan(o) else round(float(o), 5)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, pd.Timestamp):
            return str(o.date())
        return o

    (OUT / "results.json").write_text(json.dumps(clean(results), indent=1))
    sig.to_csv(OUT / "signals_base.csv", float_format="%.0f")
    print(json.dumps(clean({k: results[k] for k in ("A", "episode_totals")}), indent=1)[:3000])


if __name__ == "__main__":
    main()
