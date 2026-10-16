"""Exploratory (no pass/fail): the stacked rule, SPY's own gamma around 2020-2026 corrections, today's readings.
Writes out/explore_mv.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
R1 = HERE.parent / "2026-10-15-channel-reversion-macro"
sys.path.insert(0, str(R1))
import tests as T  # noqa: E402

DATA, OUT = HERE / "data", HERE / "out"
MS = HERE.parent.parent / "microstructure" / "out"
TOP = 1 / 6          # centred percentile >= +1/6 <=> top third of the trailing 5 years
MACRO_BEAR = ["M_FF_HIKE", "M_Y10_UP", "M_CURVE_FLAT", "M_USD_UP", "M_M2_SLOW", "M_MARGIN_FROTH", "M_LIQ_DRAIN",
              "M_TIPS_UP", "M_CREDIT_WIDEN", "M_NFCI"]


def stack_signals(X, raw):
    avail = X[MACRO_BEAR].notna().sum(axis=1)
    on = (X[MACRO_BEAR] >= TOP).sum(axis=1)
    macro = pd.Series(np.where(avail >= 4, (on >= avail / 2).astype(float), np.nan), index=X.index)
    trig_parts = pd.concat([X.O_VIX_TERM >= TOP, X.O_GEX <= -TOP, X.O_PC_EQUITY >= TOP], axis=1)
    trig_avail = X[["O_VIX_TERM", "O_GEX", "O_PC_EQUITY"]].notna().any(axis=1)
    trigger = trig_parts.any(axis=1).astype(float).where(trig_avail)
    stretched = ((raw.R_RSI_W >= 70) | (raw.S_CHAN_Z >= 0.5) | (X.R_DIST_SMA40 >= TOP)).astype(float).where(raw.R_RSI_W.notna())
    return macro, trigger, stretched


def shift_test(sig, y, ndraw=1000, seed=7):
    si = T.ShiftIndex(sig)
    ok = y.notna()
    rows = pd.DataFrame({"t": y.index[ok], "y": y[ok].to_numpy()})
    pos = si.positions(rows.t.to_numpy())
    fr = np.random.default_rng(seed).uniform(0.1, 0.9, ndraw)
    yy = rows.y.to_numpy()
    arr = np.array([T.delta(yy, si.values(pos, 0))] + [T.delta(yy, si.values(pos, f)) for f in fr])
    null = arr[1:][~np.isnan(arr[1:])]
    s0 = si.values(pos, 0)
    return {"rate_on": float(np.nanmean(yy[s0 == 1])) if (s0 == 1).any() else None,
            "rate_off": float(np.nanmean(yy[s0 == 0])) if (s0 == 0).any() else None,
            "weeks_on": int((s0 == 1).sum()), "delta": float(arr[0]),
            "p_shift": float((1 + (null >= arr[0]).sum()) / (1 + len(null)))}


def main():
    X = pd.read_pickle(DATA / "features_X.pkl")
    raw = pd.read_pickle(DATA / "features_raw.pkl")
    res = {}
    macro, trigger, stretched = stack_signals(X, raw)
    y = raw.Y_CORR[raw.index >= "1992-01-01"]
    combos = {"macro": macro, "trigger": trigger, "stretched": stretched,
              "macro_and_trigger": (macro * trigger), "trigger_and_stretched": (trigger * stretched),
              "macro_and_stretched": (macro * stretched), "all_three": (macro * trigger * stretched)}
    res["stack_Y_CORR"] = {k: shift_test(v.reindex(y.index), y) for k, v in combos.items()}
    res["stack_Y_CORR"]["base_rate"] = float(y.dropna().mean())
    yb = raw.Y_BEAR[raw.index >= "1992-01-01"]
    res["stack_Y_BEAR"] = {k: shift_test(v.reindex(yb.index), yb) for k, v in combos.items()}
    res["stack_now"] = {k: (None if np.isnan(v.iloc[-1]) else float(v.iloc[-1])) for k, v in combos.items()}

    # SPY's own gamma around 2020-2026 corrections (descriptive)
    g = pd.read_csv(MS / "td_gamma_SPY.csv", parse_dates=["date"]).set_index("date")
    mb = pd.read_csv(MS / "mech_book_SPY.csv", parse_dates=["date"]).set_index("date")
    d = pd.DataFrame(index=g.index)
    d["below_flip"] = (g.spot < g.flip_classic).astype(float)
    d["flip_dist"] = g.spot / g.flip_classic - 1
    d["gex_pct"] = T.trailing_pct(g.gex_classic, 252, 120)
    d["share_1d"] = g.gamma_share_1d
    d["put_call_oi"] = g.put_oi / g.call_oi
    d["iv_minus_rv"] = mb.atm_iv.reindex(g.index) - mb.rv20.reindex(g.index)
    d["near_oi_5"] = mb.near5.reindex(g.index)
    wk = d.resample("W-FRI").last()
    yw = raw.Y_CORR.reindex(wk.index)
    pre = wk[yw == 1]
    non = wk[yw == 0]
    starts, gap = [], 99
    for t, v in yw.items():
        if v == 1 and gap >= 4:
            starts.append(t)
        gap = 0 if v == 1 else gap + 1
    res["spy_gamma"] = {"first_warning_weeks": [str(s.date()) for s in starts],
                        "weeks_before_a_10pct_fall_mean": pre.mean().round(4).to_dict(),
                        "other_weeks_mean": non.mean().round(4).to_dict(),
                        "n_before": int(len(pre)), "n_other": int(len(non)), "now": wk.iloc[-1].round(4).to_dict()}
    # today's readings of every feature (raw and percentile)
    last = raw.index[-1]
    res["now_raw"] = raw.loc[last].drop(["last_day", "partial", "Y_CORR", "Y_BEAR", "Y_CHAN"]).astype(float).round(4).to_dict()
    res["now_pct"] = (X.loc[last] + 0.5).round(3).to_dict()

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, list):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, float)):
            return None if np.isnan(o) else round(float(o), 4)
        return o
    (OUT / "explore_mv.json").write_text(json.dumps(clean(res), indent=1))
    print(json.dumps(clean({k: res[k] for k in ("stack_Y_CORR", "stack_now", "spy_gamma")}), indent=1))


if __name__ == "__main__":
    main()
