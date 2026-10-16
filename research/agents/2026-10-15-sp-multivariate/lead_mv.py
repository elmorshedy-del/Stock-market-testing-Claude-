"""POST-HOC timing check: does the momentum/RSI warning come before the top or after the drop has started?
Writes out/lead_mv.json.

For every distinct 10%+ S&P decline 2000-2026 (zigzag on daily closes: peak-to-trough legs of 10%+, split by 10%+
rebounds), find the first week from 13 weeks before the peak to the trough when the walk-forward
model's probability is at least 2x the training base rate, and report how much of the decline had already happened.
Also: of all weeks flagged that way, the share followed by a 10%+ fall within 13 weeks (precision).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA, OUT = HERE / "data", HERE / "out"


def declines(close, low=None, thr=0.10):
    """Zigzag on daily closes: every peak-to-trough leg that falls >= thr, with legs split by >= thr rebounds."""
    c = close.to_numpy(float)
    idx = close.index
    out = []
    mode, ext_i = "up", 0
    for i in range(1, len(c)):
        if mode == "up":
            if c[i] > c[ext_i]:
                ext_i = i
            elif c[i] / c[ext_i] - 1 <= -thr:
                peak_i, mode, ext_i = ext_i, "down", i
        else:
            if c[i] < c[ext_i]:
                ext_i = i
            elif c[i] / c[ext_i] - 1 >= thr:
                out.append((idx[peak_i], idx[ext_i], float(c[ext_i] / c[peak_i] - 1)))
                mode, ext_i = "up", i
    if mode == "down":
        out.append((idx[peak_i], idx[ext_i], float(c[ext_i] / c[peak_i] - 1)))
    return out


def main():
    raw = pd.read_pickle(DATA / "features_raw.pkl")
    P = pd.read_pickle(DATA / "preds.pkl")
    g = P[(P.outcome == "Y_CORR") & (P.model == "GBM") & (P.year != "now")]
    piv = g.pivot_table(index="week", columns="spec", values="p")
    clim = g[g.spec == "VOL"].set_index("week").clim
    import features_mv as F
    F.BP.DATA = F.R2 / "data"
    d = F.BP.load_yahoo("GSPC_long")
    d = d[d.index >= "1999-06-01"]
    evs = declines(d.close, d.low.where(d.low > 0, d.close))
    evs = [e for e in evs if e[0] >= pd.Timestamp("2000-01-01")]
    res = {"events": []}
    for spec in ("VOL", "V+R", "FULL"):
        flag = piv[spec] >= 2 * clim.reindex(piv.index)
        y = raw.Y_CORR.reindex(piv.index)
        ok = y.notna() & flag
        res[f"precision_{spec}"] = {"flagged_weeks": int(flag.sum()), "followed_by_10pct": float(y[ok].mean()),
                                   "base_rate": float(y.dropna().mean())}
    for peak, trough, depth in evs:
        row = {"peak": str(peak.date()), "trough": str(trough.date()), "depth": round(depth, 3)}
        pk_close = d.close.loc[peak]
        for spec in ("VOL", "V+R", "FULL"):
            flag = piv[spec] >= 2 * clim.reindex(piv.index)
            win = flag[(flag.index >= peak - pd.Timedelta(weeks=13)) & (flag.index <= trough)]
            first = win[win].index.min() if win.any() else None
            if first is None:
                row[spec] = None
                continue
            c_first = d.close[d.close.index <= first].iloc[-1]
            before_peak = first <= peak
            done = 0.0 if before_peak else float(c_first / pk_close - 1)       # fall already taken at the warning
            row[spec] = {"first_warning": str(first.date()), "weeks_vs_peak": int(round((first - peak).days / 7)),
                         "already_down": round(done, 3),
                         "share_of_fall_still_ahead": round(float(1 - done / depth), 2),
                         "rise_to_peak_after_warning": round(float(pk_close / c_first - 1), 3) if before_peak else 0.0}
        res["events"].append(row)
    ev = res["events"]
    for spec in ("VOL", "V+R", "FULL"):
        w = [e[spec] for e in ev if e[spec]]
        res[f"summary_{spec}"] = {"events": len(ev), "warned": len(w),
                                  "warned_before_peak": sum(x["weeks_vs_peak"] <= 0 for x in w),
                                  "median_already_down": float(np.median([x["already_down"] for x in w])) if w else None,
                                  "median_share_still_ahead": float(np.median([x["share_of_fall_still_ahead"] for x in w])) if w else None,
                                  "median_rise_missed_when_early": float(np.median([x["rise_to_peak_after_warning"] for x in w if x["weeks_vs_peak"] <= 0])) if any(x["weeks_vs_peak"] <= 0 for x in w) else None}
    (OUT / "lead_mv.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != "events"}, indent=1))
    for e in ev:
        print(e["peak"], e["trough"], e["depth"], "| V+R", e["V+R"], "| VOL", e["VOL"] and e["VOL"]["weeks_vs_peak"])


if __name__ == "__main__":
    main()
