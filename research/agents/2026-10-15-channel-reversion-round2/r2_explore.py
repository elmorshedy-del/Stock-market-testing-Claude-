"""Round-2 EXPLORATORY analyses E1-E7 (README). No pass/fail; p-values are descriptive. Writes out/explore_r2.json
and out/e1_leadlag.csv.

E7 is post-hoc: it was added after C2 showed the barrier model under-predicts touches by about half.
"""
import json

import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

import r2_lib as L
import r2_tests as R

T = L.T
OUT, DATA, PREV = L.OUT, L.DATA, L.PREV


def monthly_closes():
    tech = pd.read_pickle(PREV / "data" / "monthly_prices.pkl")
    non = pd.read_pickle(DATA / "monthly_prices.pkl")
    p = pd.concat([tech[tech.symbol.isin(L.TECH)], non])
    p = p[~p.partial]
    return p.reset_index().pivot(index="month", columns="symbol", values="close").sort_index()


def p_drift(x0, m, sigma, H):
    """P(min over [0,H] of x0 + m t + sigma W_t <= 0)."""
    x0, m, s = (np.asarray(v, float) for v in (x0, m, sigma))
    sh = s * np.sqrt(H)
    a = norm.cdf((-x0 - m * H) / sh)
    with np.errstate(over="ignore"):
        b = np.exp(np.clip(-2 * m * x0 / s ** 2, -700, 700)) * norm.cdf((-x0 + m * H) / sh)
    return np.clip(np.where(x0 <= 0, 1.0, a + b), 0, 1)


def main():
    rng = np.random.default_rng(L.SEED + 1)
    fracs = rng.uniform(0.1, 0.9, 300)
    ch = L.load_monthly_panels()
    macro, raw, invm = R.monthly_inputs()
    sig, inv_sig = R.r1_signals(raw, invm, 2 / 3)
    c4sig, _ = R.c4_monthly(macro)
    closes = monthly_closes()
    res = {}

    # ---------------- E1 lead-lag around the last top month of each episode
    ep = L.episodes(ch, L.TECH + L.NONTECH, 84, 0.5, 24)
    names = ["FF_HIKE", "Y10_UP", "USD_UP", "M2_SLOW", "MKT_EXT", "MARGIN_FROTH", "LIQ_DRAIN", "TIPS_UP",
             "CREDIT_WIDEN", "GEX_LOW"]
    allsig = {**{n: sig[n] for n in names}, "AVG_CORR": c4sig["AVG_CORR"]}
    vix = pd.read_csv(PREV / "out" / "macro_monthly.csv", parse_dates=["month"], index_col="month").vix
    allsig["VIX_HIGH"] = L.signal(vix)
    rows = []
    for n, s in allsig.items():
        s = s.dropna()
        for k in range(-12, 13):
            for lab, e in (("reverting", ep[ep.event]), ("not", ep[~ep.event])):
                when = e.end + pd.offsets.MonthEnd(k) if k >= 0 else e.end - pd.offsets.MonthEnd(-k)
                v = s.reindex(when.to_numpy()).to_numpy()
                v = v[~np.isnan(v)]
                rows.append({"var": n, "k": k, "group": lab, "on_share": v.mean() if len(v) else np.nan, "n": len(v)})
    ll = pd.DataFrame(rows)
    ll.to_csv(OUT / "e1_leadlag.csv", index=False)
    piv = ll.pivot_table(index=["var", "k"], columns="group", values="on_share").reset_index()
    piv["gap"] = piv.reverting - piv["not"]
    E1 = {}
    for n in allsig:
        g = piv[piv["var"] == n]
        E1[n] = {"gap_before_-6_to_0": float(g[(g.k >= -6) & (g.k <= 0)].gap.mean()),
                 "gap_after_1_to_6": float(g[(g.k >= 1) & (g.k <= 6)].gap.mean()),
                 "gap_after_7_to_12": float(g[(g.k >= 7) & (g.k <= 12)].gap.mean())}
    res["E1"] = {"episodes": int(len(ep)), "reverting": int(ep.event.sum()), "vars": E1}

    # ---------------- E2 trend break in the middle of the channel
    sma10 = closes.rolling(10).mean()
    below = (closes < sma10).astype(float).where(sma10.notna())
    rm = L.rows(ch, L.TECH + L.NONTECH, 84, -99, 24, top_only=False)
    rm = rm[(rm.z >= -0.5) & (rm.z < 0.5) & rm.sig_m.notna() & (rm.x0 > 0)].reset_index(drop=True)
    rm["p_bm"] = L.p_barrier(rm.x0, rm.sig_m, 24)
    lp = np.log(np.clip(rm.p_bm, 1e-4, 1 - 1e-4) / (1 - np.clip(rm.p_bm, 1e-4, 1 - 1e-4))).to_numpy()
    y = rm.y.to_numpy()
    sh = L.Shifter(below, rm)

    def coef(s):
        ok = ~np.isnan(s)
        return LogisticRegression(C=1e6).fit(np.column_stack([lp[ok], s[ok]]), y[ok]).coef_[0, 1]
    arr = np.array([coef(sh.values(0))] + [coef(sh.values(f)) for f in fracs])
    s0 = sh.values(0)
    ok = ~np.isnan(s0)
    res["E2"] = {"n_rows": int(ok.sum()), "rate_below_sma": float(y[ok & (s0 == 1)].mean()),
                 "rate_above_sma": float(y[ok & (s0 == 0)].mean()),
                 "barrier_pred_below": float(rm.p_bm[ok & (s0 == 1)].mean()),
                 "barrier_pred_above": float(rm.p_bm[ok & (s0 == 0)].mean()),
                 "coef_after_barrier": float(arr[0]), "p_shift": L.p_one_sided(arr)}

    # ---------------- E3 crowding
    v84 = ch[(ch.W == 84) & ~ch.partial]
    crowd = v84.groupby("month").apply(lambda g: (g.valid & (g.z >= 0.5)).sum() / max(1, g.valid.sum()))
    crowd = crowd.reindex(macro.index)
    cs = L.signal(crowd)
    rt = L.rows(ch, L.TECH + L.NONTECH, 84, 0.5, 24)
    a3 = L.shift_deltas(rt, cs, fracs)
    sv = L.Shifter(cs, rt).values(0)
    res["E3"] = {"delta": float(a3[0]), "p_shift": L.p_one_sided(a3),
                 "p_on": float(rt.y[sv == 1].mean()), "p_off": float(rt.y[sv == 0].mean()), "n_on": int((sv == 1).sum()),
                 "crowding_now": float(crowd.dropna().iloc[-1]), "crowding_pct_now": float(T.trailing_pct(crowd.dropna()).iloc[-1])}

    # ---------------- E4 stretch x tightening
    comp = sig["COMPOSITE"]
    rt["comp"] = comp.reindex(rt.t).to_numpy()
    out4 = {}
    for lab, g in (("z_0.5_to_1", rt[rt.z < 1]), ("z_ge_1", rt[rt.z >= 1])):
        out4[lab] = {"n": int(len(g)), "rate": float(g.y.mean()),
                     "rate_comp_on": float(g.y[g.comp == 1].mean()) if (g.comp == 1).any() else None,
                     "rate_comp_off": float(g.y[g.comp == 0].mean()) if (g.comp == 0).any() else None,
                     "n_comp_on": int((g.comp == 1).sum())}
    res["E4"] = out4

    # ---------------- E7 (post-hoc) why the barrier model under-predicts: drift and vol after the top
    rt = L.rows(ch, L.TECH + L.NONTECH, 84, 0.5, 24)
    rt = rt[rt.sig_m.notna() & (rt.x0 > 0)].reset_index(drop=True)
    lc = np.log(closes)
    fwd_ret, fwd_vol = [], []
    for _, r in rt.iterrows():
        s = lc[r.symbol]
        i = s.index.get_indexer([r.t])[0]
        seg = s.iloc[i:i + 25].dropna()
        if len(seg) == 25:
            fwd_ret.append((seg.iloc[-1] - seg.iloc[0]) / 24)
            fwd_vol.append(seg.diff().std())
        else:
            fwd_ret.append(np.nan)
            fwd_vol.append(np.nan)
    rt["fwd_drift"] = fwd_ret
    rt["fwd_vol"] = fwd_vol
    rt["gap"] = rt.fwd_drift - rt.b
    rt["vol_ratio"] = rt.fwd_vol / rt.sig_m
    done = rt.dropna(subset=["gap"])
    E7 = {"rows_with_full_24m": int(len(done)),
          "median_channel_slope_per_month": float(done.b.median()),
          "median_realised_drift_per_month": float(done.fwd_drift.median()),
          "median_gap_per_month": float(done.gap.median()), "mean_gap_per_month": float(done.gap.mean()),
          "median_vol_ratio_fwd_over_trailing": float(done.vol_ratio.median())}
    # ex-ante adjusted model: drift gap and vol ratio estimated only from rows whose 24-month window ended before t
    rt = rt.sort_values("t").reset_index(drop=True)
    end_t = rt.t + pd.offsets.MonthEnd(24)
    gaps, vrs = [], []
    order = np.argsort(end_t.to_numpy())
    ends_sorted = end_t.to_numpy()[order]
    gap_sorted, vr_sorted = rt.gap.to_numpy()[order], rt.vol_ratio.to_numpy()[order]
    for t in rt.t.to_numpy():
        j = np.searchsorted(ends_sorted, t, side="right")
        g_ok = gap_sorted[:j][~np.isnan(gap_sorted[:j])]
        v_ok = vr_sorted[:j][~np.isnan(vr_sorted[:j])]
        gaps.append(np.median(g_ok) if len(g_ok) >= 100 else np.nan)
        vrs.append(np.median(v_ok) if len(v_ok) >= 100 else np.nan)
    rt["m_hat"], rt["vr_hat"] = gaps, vrs
    ev = rt.dropna(subset=["m_hat", "vr_hat"]).copy()
    ev["p0"] = L.p_barrier(ev.x0, ev.sig_m, 24)
    ev["p_adj"] = p_drift(ev.x0, ev.m_hat, ev.sig_m * ev.vr_hat, 24)

    def slope_of(p):
        q = np.clip(p, 1e-4, 1 - 1e-4)
        return float(LogisticRegression(C=1e6).fit(np.log(q / (1 - q))[:, None], ev.y).coef_[0, 0])
    E7["evaluated_rows"] = int(len(ev))
    E7["evaluated_from"] = str(ev.t.min().date())
    E7["plain"] = {"mean_pred": float(ev.p0.mean()), "auc": float(roc_auc_score(ev.y, ev.p0)), "slope": slope_of(ev.p0.to_numpy())}
    E7["adjusted"] = {"mean_pred": float(ev.p_adj.mean()), "auc": float(roc_auc_score(ev.y, ev.p_adj)),
                      "slope": slope_of(ev.p_adj.to_numpy())}
    E7["mean_real"] = float(ev.y.mean())
    dec = pd.qcut(ev.p_adj, 10, duplicates="drop")
    E7["adjusted_deciles"] = ev.groupby(dec, observed=True).agg(pred=("p_adj", "mean"), real=("y", "mean"), n=("y", "size")).round(3).reset_index(drop=True).to_dict("records")
    dec0 = pd.qcut(ev.p0, 10, duplicates="drop")
    E7["plain_deciles"] = ev.groupby(dec0, observed=True).agg(pred=("p0", "mean"), real=("y", "mean"), n=("y", "size")).round(3).reset_index(drop=True).to_dict("records")
    E7["m_hat_latest"], E7["vr_hat_latest"] = float(rt.m_hat.dropna().iloc[-1]), float(rt.vr_hat.dropna().iloc[-1])
    res["E7"] = E7

    # ---------------- E6 NVDA today: monthly and weekly channels, plain and adjusted barrier odds
    import build_panel as BP
    import channels_panel as CP
    BP.DATA = PREV / "data"
    d = BP.load_yahoo("NVDA")
    today = d.index[-1]
    wk = d.resample("W-FRI").agg({"high": "max", "low": "min", "close": "last", "adjclose": "last", "volume": "sum"}).dropna(subset=["close"])
    wk["partial"] = wk.index > today
    sig_d = np.log(d.close).diff().iloc[-126:].std()
    E6 = {"close": float(d.close.iloc[-1]), "daily_vol_126": float(sig_d)}
    for Wk in (104, 156):
        f = CP.frame_for("NVDA", wk, Wk).iloc[-1]
        hw = (f.hi - f.lo) / 2
        x0 = (f.z + 1) * hw
        c = f.a + f.b * (len(wk) - 1)
        E6[f"weekly_W{Wk}"] = {"z": float(f.z), "valid": bool(f.valid), "r2": float(f.r2),
                              "lower": float(np.exp(c + f.lo)), "upper": float(np.exp(c + f.hi)),
                              "growth_yr": float(np.exp(52 * f.b) - 1),
                              "p_touch_lower_26w_plain": float(L.p_barrier(x0, sig_d * np.sqrt(5), 26))}
    nv = ch[(ch.symbol == "NVDA") & (ch.W == 84)].sort_values("month").iloc[-1]
    sm = sig_d * np.sqrt(21)
    E6["monthly_W84"] = {"z": float(nv.z), "x0": float(nv.x0),
                         "p_touch_lower_24m_plain": float(L.p_barrier(nv.x0, sm, 24)),
                         "p_touch_lower_24m_adjusted": float(p_drift(nv.x0, E7["m_hat_latest"], sm * E7["vr_hat_latest"], 24)),
                         "p_touch_lower_12m_adjusted": float(p_drift(nv.x0, E7["m_hat_latest"], sm * E7["vr_hat_latest"], 12))}
    res["E6"] = E6
    (OUT / "explore_r2.json").write_text(json.dumps(L.clean(res), indent=1))
    print(json.dumps(L.clean({k: res[k] for k in ("E1", "E2", "E3", "E4")}), indent=1)[:4000])
    print(json.dumps(L.clean({k: v for k, v in E7.items() if "deciles" not in k}), indent=1))
    print(json.dumps(L.clean(E6), indent=1))


if __name__ == "__main__":
    main()
