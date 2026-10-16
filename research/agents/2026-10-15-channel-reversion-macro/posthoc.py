"""POST-HOC checks (not pre-registered; reported as such). Writes out/posthoc.json.

P1  family joint p by min-p (Westfall-Young) instead of max standardised delta, for parts B and C
P2  Part A with 100 bootstrap paths (20 pre-registered + 80 from `channels_panel.py --boot 80 --seed 2 ...`)
P3  who drives the strongest leads: MARGIN_FROTH and INV_GLUT (reversion), easing COMPOSITE (breakout), by episode
P4  NVDA today: lower/mid/upper line, and how long a flat price takes to reach the lower line
P5  conditional rates for NVDA's current band (z between -0.5 and 0) and the 1998-2000 vs today macro readings
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

import tests as T

HERE = Path(__file__).parent
DATA, OUT = HERE / "data", HERE / "out"


def minp_joint(nulls, names):
    p_obs, p_null = [], []
    for n in names:
        a = nulls[n]
        obs, nul = a[0], a[1:]
        ok = ~np.isnan(nul)
        if np.isnan(obs) or ok.sum() < 50:
            continue
        nul = nul[ok]
        p_obs.append((1 + (nul >= obs).sum()) / (1 + len(nul)))
        srt = np.sort(nul)
        # p of each null draw within its own null: share of draws >= it
        pd_ = 1 - np.searchsorted(srt, a[1:], side="left") / len(srt)
        pd_[~ok] = np.nan
        p_null.append(pd_)
    P = np.array(p_null)
    m = np.nanmin(P, axis=0)
    return float((1 + (m <= min(p_obs)).sum()) / (1 + (~np.isnan(m)).sum())), float(min(p_obs))


def main():
    ch, macro, inv = T.load()
    rng = np.random.default_rng(T.SEED)
    fracs = rng.uniform(0.1, 0.9, T.NDRAW)
    raw_by_w = {W: T.raw_variables(macro, ch, W) for W in (60, 84, 120)}
    invm = T.inv_monthly(inv, macro.index)
    res = {}

    # P1
    Bres, rows_b, (sig_b, inv_b) = T.part_b(ch, raw_by_w, invm, fracs, "rev")
    nb = T.part_b.nulls
    Cres, rows_c, (sig_c, inv_c) = T.part_b(ch, raw_by_w, invm, fracs, "brk", flip=True)
    nc = T.part_b.nulls
    res["P1"] = {}
    for lab, nulls, R in (("reversion", nb, Bres), ("breakout", nc, Cres)):
        for fam, names in (("primary", T.PRIMARY), ("secondary", T.SECONDARY)):
            p, pmin = minp_joint(nulls, names)
            res["P1"][f"{lab}_{fam}"] = {"minp_joint_p": p, "smallest_single_p": pmin,
                                        "prereg_maxz_joint_p": R[names[0]].get("family_joint_p")}

    # P2
    real = T.rows_for(ch, T.BASE).y.mean()
    paths = []
    for f in ("channels_boot.pkl", "channels_boot_extra.pkl"):
        if (DATA / f).exists():
            b = pd.read_pickle(DATA / f)
            b = b[b.valid & (b.z >= 0.5)]
            b = b[(b.t_rev <= 24) | (b.n_fwd >= 24)]
            r = (b.t_rev <= 24).groupby(b.path).mean()
            paths += r.tolist()
    paths = np.array(paths)
    res["P2"] = {"real": float(real), "n_paths": len(paths), "null_mean": float(paths.mean()),
                 "null_p95": float(np.quantile(paths, 0.95)), "paths_ge_real": int((paths >= real).sum()),
                 "p": float((1 + (paths >= real).sum()) / (1 + len(paths)))}

    # P3
    ep = pd.read_csv(OUT / "episodes_reversion.csv", parse_dates=["start", "end"])
    epb = pd.read_csv(OUT / "episodes_breakout.csv", parse_dates=["start", "end"])
    def tag(e, sig, inv_sig, name):
        v = []
        for _, r in e.iterrows():
            if name == "INV_GLUT":
                v.append(inv_sig[r.symbol].get(r.end, np.nan) if r.symbol in inv_sig.columns else np.nan)
            else:
                v.append(sig[name].get(r.end, np.nan))
        return np.array(v)
    P3 = {}
    for name in ("MARGIN_FROTH", "INV_GLUT", "MKT_EXT"):
        e = ep.copy()
        e["on"] = tag(e, sig_b, inv_b, name)
        e = e.dropna(subset=["on"])
        e["era"] = np.where(e.end < pd.Timestamp("2010-01-01"), "pre2010", "2010+")
        P3[f"rev_{name}"] = (e.groupby(["era", "on"]).event.agg(["mean", "size"]).round(3)
                             .reset_index().astype({"on": int}).to_dict("records"))
    e = epb.copy()
    e["on"] = tag(e, sig_c, inv_c, "COMPOSITE")
    e = e.dropna(subset=["on"])
    P3["brk_easing_COMPOSITE_by_episode"] = e.groupby("on").event.agg(["mean", "size"]).round(3).reset_index().to_dict("records")
    on_ev = e[(e.on == 1) & e.event]
    P3["brk_easing_COMPOSITE_on_and_broke"] = {"episodes": int(len(on_ev)), "waves": int(on_ev.wave.nunique()),
                                               "years": sorted(on_ev.end.dt.year.unique().tolist()),
                                               "symbols": sorted(on_ev.symbol.unique().tolist())}
    rc = rows_c.copy()
    rc["on"] = sig_c["COMPOSITE"].reindex(rc.month).to_numpy()
    on_rows = rc[rc.on == 1]
    P3["brk_easing_COMPOSITE_rows_by_year"] = on_rows.groupby(on_rows.month.dt.year).y.agg(["mean", "size"]).round(3).reset_index().to_dict("records")
    res["P3"] = P3

    # P4
    nv = ch[(ch.symbol == "NVDA") & (ch.W == 84)].sort_values("month")
    now = nv.iloc[-1]
    prices = pd.read_pickle(DATA / "monthly_prices.pkl")
    mo = prices[prices.symbol == "NVDA"].sort_index()
    i = len(mo) - 1
    centre = now.a + now.b * i
    lines = np.exp([centre + now.lo, centre, centre + now.hi])
    px = float(mo.close.iloc[-1])
    months_flat = (np.log(px) - (centre + now.lo)) / now.b
    res["P4"] = {"as_of": str(mo.last_day.iloc[-1].date()), "close": px, "lower": lines[0], "mid": lines[1], "upper": lines[2],
                 "z": float(now.z), "line_growth_per_year": float(np.exp(12 * now.b) - 1),
                 "months_until_flat_price_meets_lower_line": float(months_flat)}
    for W in (60, 120):
        x = ch[(ch.symbol == "NVDA") & (ch.W == W)].sort_values("month").iloc[-1]
        res["P4"][f"z_W{W}"] = float(x.z)

    # P5
    allr = ch[(ch.W == 84) & ch.symbol.isin(T.STOCKS) & ch.valid & ~ch.partial].copy()
    allr = allr[(allr.t_rev <= 24) | (allr.n_fwd >= 24)]
    allr["y"] = (allr.t_rev <= 24).astype(float)
    allr["yb"] = (allr.t_brk <= 24).astype(float)
    band = allr[(allr.z >= -0.5) & (allr.z < 0)].copy()
    band["COMPOSITE"] = sig_b["COMPOSITE"].reindex(band.month).to_numpy()
    band["fast"] = band.growth_yr >= 0.5
    out = {}
    for lab, g in (("all", band), ("fast_channels_growth_ge_50pct", band[band.fast]),
                   ("composite_on", band[band.COMPOSITE == 1]), ("composite_off", band[band.COMPOSITE == 0])):
        lo, hi = T.wilson(int(g.y.sum()), len(g))
        out[lab] = {"n_rows": int(len(g)), "stocks": int(g.symbol.nunique()), "p_lower_line_24m": float(g.y.mean()),
                    "ci95": [lo, hi], "p_breakout_24m": float(g.yb.mean())}
    res["P5_band_-0.5_0"] = out
    m = macro.copy()
    m["ff_chg12"] = m.ff - m.ff.shift(12)
    keep = ["ff", "ff_chg12", "gs10", "cpi_yoy", "real10", "curve", "m2_yoy", "margin_yoy", "dxy", "vix", "tips10"]
    ndx = ch[(ch.symbol == "^NDX") & (ch.W == 84)].set_index("month").z
    tab = m[keep].copy()
    tab["ndx_z"] = ndx.reindex(tab.index)
    dates = ["1998-09-30", "1999-06-30", "1999-12-31", "2000-02-29", "2018-09-30", "2021-11-30", "2024-06-30", "2026-09-30", "2026-10-31"]
    res["P5_macro_table"] = tab.loc[[pd.Timestamp(d) for d in dates]].round(2).reset_index().astype({"month": str}).to_dict("records")

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, float)):
            return None if np.isnan(o) else round(float(o), 4)
        if isinstance(o, np.integer):
            return int(o)
        return o
    (OUT / "posthoc.json").write_text(json.dumps(clean(res), indent=1))
    print(json.dumps(clean(res), indent=1))


if __name__ == "__main__":
    main()
