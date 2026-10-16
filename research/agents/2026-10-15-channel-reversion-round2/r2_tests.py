"""Round-2 pre-registered tests C1-C4 (README). Writes out/results_r2.json.

python r2_tests.py
"""
import json
from itertools import product

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

import r2_lib as L

T = L.T
OUT, DATA, PREV = L.OUT, L.DATA, L.PREV
R1_VARS = ["FF_HIKE", "Y10_UP", "CURVE_FLAT", "USD_UP", "M2_SLOW", "MKT_EXT", "MARGIN_FROTH", "COMPOSITE",
           "LIQ_DRAIN", "TIPS_UP", "CREDIT_WIDEN", "GEX_LOW", "INV_GLUT"]
C4_VARS = ["MARGIN_CREDIT", "TECH_MA", "AVG_CORR", "FAST_HIKE"]
SP_VARS = ["FF_HIKE", "Y10_UP", "CURVE_FLAT", "USD_UP", "M2_SLOW", "MARGIN_FROTH", "LIQ_DRAIN", "TIPS_UP",
           "CREDIT_WIDEN", "GEX_LOW", "DIX_LOW", "VIX_HIGH", "VIX_INVERT"]
MSPECS = [dict(W=W, ztop=z, H=H, cut=c) for W, z, H, c in product((60, 84, 120), (0.33, 0.5, 0.67), (12, 24), (2 / 3, 0.5))]
WSPECS = [dict(W=W, ztop=z, H=H, cut=c) for W, z, H, c in product((104, 156, 260), (0.33, 0.5, 0.67), (13, 26), (2 / 3, 0.5))]


# ------------------------------------------------------------------ signals
def monthly_inputs():
    macro = pd.read_csv(PREV / "out" / "macro_monthly.csv", parse_dates=["month"], index_col="month")
    ch_r1 = pd.read_pickle(PREV / "data" / "channels.pkl")
    inv = pd.read_csv(PREV / "out" / "inventory_gap.csv", parse_dates=["end", "known"])
    raw = T.raw_variables(macro, ch_r1, 84)
    invm = T.inv_monthly(inv, macro.index)
    return macro, raw, invm


def r1_signals(raw, invm, cut):
    sig, inv_sig = T.signals(raw, invm, cut)
    return sig, inv_sig


def c4_monthly(macro, cut=2 / 3):
    idx = macro.index
    import build_panel as BP
    BP.DATA = DATA
    spx = BP.load_yahoo("GSPC_long").close.resample("ME").last()
    fin = pd.read_excel(PREV / "data" / "finra_margin.xlsx")
    fin["d"] = pd.to_datetime(fin.iloc[:, 0].astype(str)) + pd.offsets.MonthEnd(0)
    credit = fin.set_index("d").iloc[:, 3].astype(float).sort_index().dropna()
    mc = np.log(credit / spx.reindex(credit.index))
    mc.index = mc.index + pd.offsets.MonthEnd(1)                   # known at the end of the following month
    raw = pd.DataFrame(index=idx)
    raw["MARGIN_CREDIT"] = mc.reindex(idx)
    sma = spx.rolling(12).mean()
    raw["TECH_MA"] = (spx < sma).astype(float).where(sma.notna()).reindex(idx)
    ac = pd.read_csv(OUT / "avgcorr.csv", parse_dates=["date"], index_col="date").monthly.dropna()
    raw["AVG_CORR"] = ac.reindex(idx)
    ffc = macro.ff.ffill(limit=1)
    raw["FAST_HIKE"] = ((ffc - ffc.shift(12)) >= 1.5).astype(float).where((ffc - ffc.shift(12)).notna())
    sig = pd.DataFrame(index=idx)
    for c in ("MARGIN_CREDIT", "AVG_CORR"):
        sig[c] = L.signal(raw[c], cut=cut)
    for c in ("TECH_MA", "FAST_HIKE"):
        sig[c] = raw[c]
    return sig, raw


def sp_signals(cut=2 / 3):
    raw = pd.read_csv(OUT / "sp_macro_weekly.csv", parse_dates=["week"], index_col="week")
    sig = pd.DataFrame(index=raw.index)
    for c in SP_VARS + ["MARGIN_CREDIT"]:
        sig[c] = L.signal(raw[c], win=260, minp=104, cut=cut)
    sig["TECH_MA"] = raw.TECH_MA
    sig["FAST_HIKE"] = raw.FAST_HIKE
    ac = pd.read_csv(OUT / "avgcorr.csv", parse_dates=["date"], index_col="date").weekly.dropna()
    sig["AVG_CORR"] = L.signal(ac.reindex(raw.index), win=260, minp=104, cut=cut)
    return sig


# ------------------------------------------------------------------ helpers
def summary(rows, sig, arr, split):
    sh = L.Shifter(sig, rows)
    s = sh.values(0)
    y = rows.y.to_numpy()
    ok = ~np.isnan(s)
    early = (rows.t < split).to_numpy()
    return {"n_rows": int(ok.sum()), "n_on": int((s[ok] == 1).sum()),
            "p_on": float(y[ok & (s == 1)].mean()) if (ok & (s == 1)).any() else None,
            "p_off": float(y[ok & (s == 0)].mean()) if (ok & (s == 0)).any() else None,
            "delta": None if np.isnan(arr[0]) else float(arr[0]), "p_shift": L.p_one_sided(arr),
            "delta_early": float(T.delta(y[early], s[early])) if early.any() else None,
            "delta_late": float(T.delta(y[~early], s[~early])) if (~early).any() else None,
            "first": str(rows.t[ok].min().date()) if ok.any() else None}


def multiverse_p(arr_by_spec):
    M = np.array(list(arr_by_spec.values()))
    med = np.nanmedian(M, axis=0)
    null = med[1:][~np.isnan(med[1:])]
    return float(med[0]), float(np.nanmean(M[:, 0] > 0)), float((1 + (null >= med[0]).sum()) / (1 + len(null)))


def calibration_fp(rows, months, n=200, ndraw=200, seed=7):
    draws = np.random.default_rng(seed).uniform(0.1, 0.9, ndraw)
    pv = []
    for rep in range(n):
        g = np.random.default_rng(1000 + rep)
        x = np.zeros(len(months))
        for k in range(1, len(x)):
            x[k] = 0.95 * x[k - 1] + g.normal()
        s = L.signal(pd.Series(x, index=months))
        arr = L.shift_deltas(rows, s, draws)
        pv.append(L.p_one_sided(arr))
    return float(np.nanmean(np.array(pv) < 0.05))


def ep_rates(ep, sig, key_col="end"):
    v = np.array([sig.get(e, np.nan) for e in ep[key_col]])
    e = ep.assign(on=v).dropna(subset=["on"])
    g = e.groupby("on").event.agg(["mean", "size"])
    return {"on": g.loc[1.0].to_dict() if 1.0 in g.index else None, "off": g.loc[0.0].to_dict() if 0.0 in g.index else None,
            "reverting_waves_in_sample": int(e.loc[e.event, "wave"].nunique())}


# ------------------------------------------------------------------ main
def main():
    rng = np.random.default_rng(L.SEED)
    fracs = rng.uniform(0.1, 0.9, L.NDRAW)
    ch = L.load_monthly_panels()
    macro, raw, invm = monthly_inputs()
    res = {"n_draws": L.NDRAW}

    # ---------------- C1
    sig_cut = {c: r1_signals(raw, invm, c) for c in (2 / 3, 0.5)}
    sigM = sig_cut[2 / 3][0]["MARGIN_FROTH"]
    rn = L.rows(ch, L.NONTECH, 84, 0.5, 24)
    arr = L.shift_deltas(rn, sigM, fracs)
    C1 = summary(rn, sigM, arr, pd.Timestamp("2010-01-01"))
    late = rn.t >= pd.Timestamp("2010-01-01")
    s_late = L.Shifter(sigM, rn[late].reset_index(drop=True)).values(0)
    C1["delta_2010plus"] = float(T.delta(rn[late].y.to_numpy(), s_late))
    ep = L.episodes(ch, L.NONTECH, 84, 0.5, 24)
    ep.to_csv(OUT / "c1_episodes_nontech.csv", index=False)
    C1["episodes"] = ep_rates(ep, sigM)
    C1["episode_totals"] = {"episodes": int(len(ep)), "reverting": int(ep.event.sum()), "waves": int(ep.wave.nunique())}
    C1["p_rev_top_all"] = float(rn.y.mean())
    C1["n_stocks_top"] = int(rn.symbol.nunique())
    months = pd.date_range("1981-01-31", macro.index[-1], freq="ME")
    C1["calibration_fp_rate"] = calibration_fp(rn, months)
    by_spec = {}
    for sp in MSPECS:
        r = L.rows(ch, L.NONTECH, sp["W"], sp["ztop"], sp["H"])
        by_spec[tuple(sp.values())] = L.shift_deltas(r, sig_cut[sp["cut"]][0]["MARGIN_FROTH"], fracs)
    C1["multiverse_median_delta"], C1["multiverse_share_pos"], C1["multiverse_p"] = multiverse_p(by_spec)
    thr = 0.01 if C1["calibration_fp_rate"] > 0.10 else 0.05
    ep_on, ep_off = C1["episodes"]["on"], C1["episodes"]["off"]
    C1["p_threshold_used"] = thr
    C1["passes"] = bool(C1["delta"] is not None and C1["delta"] > 0 and C1["p_shift"] < thr
                        and C1["delta_2010plus"] > 0 and ep_on and ep_off and ep_on["mean"] > ep_off["mean"])
    C1["fragile"] = bool(C1["passes"] and C1["multiverse_p"] >= 0.05)
    res["C1"] = C1
    print("C1 done", {k: C1[k] for k in ("delta", "p_shift", "delta_2010plus", "passes")})

    # ---------------- C2
    sig, inv_sig = sig_cut[2 / 3]
    c4sig, c4raw = c4_monthly(macro)
    rt = L.rows(ch, L.TECH + L.NONTECH, 84, 0.5, 24)
    rt = rt[rt.sig_m.notna() & (rt.x0 > 0)].reset_index(drop=True)
    rt["p_bm"] = L.p_barrier(rt.x0, rt.sig_m, 24)
    y = rt.y.to_numpy()
    auc_bm, auc_z = roc_auc_score(y, rt.p_bm), roc_auc_score(y, -rt.z)
    months_u = rt.t.unique()
    g = np.random.default_rng(11)
    by_m = rt.groupby("t").indices
    diffs = []
    for _ in range(1000):
        pick = g.choice(months_u, len(months_u), replace=True)
        idx = np.concatenate([by_m[m] for m in pick])
        yy = y[idx]
        if yy.min() == yy.max():
            continue
        diffs.append(roc_auc_score(yy, rt.p_bm.to_numpy()[idx]) - roc_auc_score(yy, -rt.z.to_numpy()[idx]))
    lp = np.log(np.clip(rt.p_bm, 1e-4, 1 - 1e-4) / (1 - np.clip(rt.p_bm, 1e-4, 1 - 1e-4))).to_numpy()
    slope = LogisticRegression(C=1e6).fit(lp[:, None], y).coef_[0, 0]
    dec = pd.qcut(rt.p_bm, 10, duplicates="drop")
    calib = rt.groupby(dec, observed=True).agg(pred=("p_bm", "mean"), real=("y", "mean"), n=("y", "size")).round(3)
    C2 = {"n_rows": int(len(rt)), "n_stocks": int(rt.symbol.nunique()), "mean_pred": float(rt.p_bm.mean()), "mean_real": float(y.mean()),
          "auc_barrier": float(auc_bm), "auc_z": float(auc_z),
          "auc_diff_ci95": [float(np.quantile(diffs, 0.025)), float(np.quantile(diffs, 0.975))],
          "calibration_slope": float(slope), "calibration_deciles": calib.reset_index(drop=True).to_dict("records"),
          "auc_sigma_alone": float(roc_auc_score(y, rt.sig_m)), "auc_distance_alone": float(roc_auc_score(y, -rt.x0))}
    C2["passes"] = bool(auc_bm >= 0.65 and C2["auc_diff_ci95"][0] > 0 and 0.7 <= slope <= 1.3)
    # all valid rows, not only the top
    ra = L.rows(ch, L.TECH + L.NONTECH, 84, -99, 24, top_only=False)
    ra = ra[ra.sig_m.notna() & (ra.x0 > 0)].reset_index(drop=True)
    ra["p_bm"] = L.p_barrier(ra.x0, ra.sig_m, 24)
    C2["all_rows"] = {"n": int(len(ra)), "auc_barrier": float(roc_auc_score(ra.y, ra.p_bm)),
                      "mean_pred": float(ra.p_bm.mean()), "mean_real": float(ra.y.mean())}
    # each variable after controlling for the barrier probability (logistic; shift null on the signal)
    med = {}
    allsig = {**{v: sig[v] for v in R1_VARS if v != "INV_GLUT"}, "INV_GLUT": inv_sig, **{v: c4sig[v] for v in C4_VARS}}
    draws = fracs[:300]
    for v, s_ in allsig.items():
        sh = L.Shifter(s_, rt)
        def coef(s):
            ok = ~np.isnan(s)
            if (s[ok] == 1).sum() < 10 or (s[ok] == 0).sum() < 10:
                return np.nan
            X = np.column_stack([lp[ok], s[ok]])
            return LogisticRegression(C=1e6).fit(X, y[ok]).coef_[0, 1]
        arr_c = np.array([coef(sh.values(0))] + [coef(sh.values(f)) for f in draws])
        s0 = sh.values(0)
        ok = ~np.isnan(s0)
        med[v] = {"coef_after_control": None if np.isnan(arr_c[0]) else float(arr_c[0]),
                  "p_shift_after_control": L.p_one_sided(arr_c),
                  "raw_delta": float(T.delta(y, s0)),
                  "excess_over_barrier_on": float((y - rt.p_bm.to_numpy())[ok & (s0 == 1)].mean()) if (s0[ok] == 1).any() else None,
                  "excess_over_barrier_off": float((y - rt.p_bm.to_numpy())[ok & (s0 == 0)].mean()) if (s0[ok] == 0).any() else None,
                  "sigma_on": float(rt.sig_m[ok & (s0 == 1)].median()) if (s0[ok] == 1).any() else None,
                  "sigma_off": float(rt.sig_m[ok & (s0 == 0)].median()) if (s0[ok] == 0).any() else None,
                  "x0_on": float(rt.x0[ok & (s0 == 1)].median()) if (s0[ok] == 1).any() else None,
                  "x0_off": float(rt.x0[ok & (s0 == 0)].median()) if (s0[ok] == 0).any() else None}
    C2["after_control"] = med
    C2["n_draws_after_control"] = len(draws)
    res["C2"] = C2
    print("C2 done", {k: C2[k] for k in ("auc_barrier", "auc_z", "auc_diff_ci95", "calibration_slope", "passes")})

    # ---------------- C3 S&P weekly
    spch = pd.read_pickle(DATA / "sp_channels.pkl")
    sps = {c: sp_signals(c) for c in (2 / 3, 0.5)}
    rs = L.rows(spch, ["^GSPC"], 156, 0.5, 26, key="week")
    arrs = {v: L.shift_deltas(rs, sps[2 / 3][v], fracs) for v in SP_VARS}
    fam_p = L.minp_family(arrs)
    eps = L.episodes(spch, ["^GSPC"], 156, 0.5, 26, key="week", wave_gap_days=182)
    eps.to_csv(OUT / "c3_episodes_sp.csv", index=False)
    C3 = {"n_rows": int(len(rs)), "p_rev_top": float(rs.y.mean()), "family_minp": fam_p,
          "episode_totals": {"episodes": int(len(eps)), "reverting": int(eps.event.sum()), "waves": int(eps.wave.nunique())},
          "vars": {}}
    by_spec = {v: {} for v in SP_VARS}
    for sp in WSPECS:
        r = L.rows(spch, ["^GSPC"], sp["W"], sp["ztop"], sp["H"], key="week")
        for v in SP_VARS:
            by_spec[v][tuple(sp.values())] = L.shift_deltas(r, sps[sp["cut"]][v], fracs)
    for v in SP_VARS:
        first = sps[2 / 3][v].first_valid_index()
        split = pd.Timestamp("2010-01-01") if first < pd.Timestamp("2000-01-01") else pd.Timestamp("2018-01-01")
        sm = summary(rs, sps[2 / 3][v], arrs[v], split)
        sm["family_minp"] = fam_p
        sm["multiverse_median_delta"], sm["multiverse_share_pos"], sm["multiverse_p"] = multiverse_p(by_spec[v])
        sm["episodes"] = ep_rates(eps, sps[2 / 3][v])
        sm["underpowered"] = sm["episodes"]["reverting_waves_in_sample"] < 6
        sm["passes"] = bool(sm["delta"] is not None and sm["delta"] > 0 and sm["p_shift"] < 0.05 and fam_p < 0.05
                            and (sm["delta_early"] or -1) > 0 and (sm["delta_late"] or -1) > 0)
        sm["fragile"] = bool(sm["passes"] and sm["multiverse_p"] >= 0.05)
        C3["vars"][v] = sm
    # barrier model on the S&P
    vw = pd.read_csv(OUT / "sp_vol_weekly.csv", parse_dates=["Date"], index_col="Date").sig_w
    rs2 = rs.copy()
    rs2["sig_w"] = vw.reindex(rs2.t).to_numpy()
    rs2["x0"] = (rs2.z + 1) * (rs2.hi - rs2.lo) / 2
    rs2 = rs2[rs2.sig_w.notna() & (rs2.x0 > 0)]
    rs2["p_bm"] = L.p_barrier(rs2.x0, rs2.sig_w, 26)
    C3["barrier"] = {"n": int(len(rs2)), "mean_pred": float(rs2.p_bm.mean()), "mean_real": float(rs2.y.mean()),
                     "auc_barrier": float(roc_auc_score(rs2.y, rs2.p_bm)) if rs2.y.nunique() > 1 else None,
                     "auc_z": float(roc_auc_score(rs2.y, -rs2.z)) if rs2.y.nunique() > 1 else None}
    C3["literature_vars_descriptive"] = {}
    for v in C4_VARS:
        a = L.shift_deltas(rs, sps[2 / 3][v], fracs)
        C3["literature_vars_descriptive"][v] = summary(rs, sps[2 / 3][v], a, pd.Timestamp("2010-01-01"))
    res["C3"] = C3
    print("C3 done: family min-p", fam_p, "rows", len(rs), "rev rate", round(rs.y.mean(), 3))

    # ---------------- C4 pooled monthly
    rp = L.rows(ch, L.TECH + L.NONTECH, 84, 0.5, 24)
    arrs4 = {v: L.shift_deltas(rp, c4sig[v], fracs) for v in C4_VARS}
    fam4 = L.minp_family(arrs4)
    C4 = {"n_rows": int(len(rp)), "family_minp": fam4, "vars": {}}
    c4sig_half = c4_monthly(macro, 0.5)[0]
    for v in C4_VARS:
        split = pd.Timestamp("2018-01-01") if v == "MARGIN_CREDIT" else pd.Timestamp("2010-01-01")
        sm = summary(rp, c4sig[v], arrs4[v], split)
        for pnl, syms in (("tech", L.TECH), ("nontech", L.NONTECH)):
            sub = rp[rp.symbol.isin(syms)].reset_index(drop=True)
            sm[f"delta_{pnl}"] = float(T.delta(sub.y.to_numpy(), L.Shifter(c4sig[v], sub).values(0)))
        bs = {}
        for sp in MSPECS:
            r = L.rows(ch, L.TECH + L.NONTECH, sp["W"], sp["ztop"], sp["H"])
            s_ = c4sig[v] if (sp["cut"] == 2 / 3 or v in ("TECH_MA", "FAST_HIKE")) else c4sig_half[v]
            bs[tuple(sp.values())] = L.shift_deltas(r, s_, fracs)
        sm["multiverse_median_delta"], sm["multiverse_share_pos"], sm["multiverse_p"] = multiverse_p(bs)
        sm["family_minp"] = fam4
        sm["passes"] = bool(sm["delta"] is not None and sm["delta"] > 0 and sm["p_shift"] < 0.05 and fam4 < 0.05
                            and sm["delta_tech"] > 0 and sm["delta_nontech"] > 0
                            and (sm["delta_early"] or -1) > 0 and (sm["delta_late"] or -1) > 0)
        sm["fragile"] = bool(sm["passes"] and sm["multiverse_p"] >= 0.05)
        C4["vars"][v] = sm
    res["C4"] = C4
    print("C4 done: family min-p", fam4)
    (OUT / "results_r2.json").write_text(json.dumps(L.clean(res), indent=1))


if __name__ == "__main__":
    main()
