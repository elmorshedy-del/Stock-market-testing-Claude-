"""POST HOC (after round 3; descriptive only, no test): the trader's question for today.
The S&P is ~2.5% below its 252-day high. Given a 1.5-3.5% dip from the high, how often does it extend to -5% before a new high,
with vs without the AAPL alarm? Usage: python posthoc3.py <US data folder>"""
import json
import sys

import numpy as np
import pandas as pd

import decoupling as Dc


def main(folder):
    D = pd.read_csv(Dc.OUT / "daily.csv", index_col=0, parse_dates=True)
    spx = Dc.close(folder, "GSPC").reindex(D.index)
    v = spx.to_numpy()
    H = spx.rolling(252, min_periods=60).max().to_numpy()
    dist = v / H - 1
    alarm = D["alarm AAPL"].astype(bool).to_numpy() & D["corr AAPL"].notna().to_numpy()
    hit = np.full(len(v), np.nan)
    for t in range(len(v)):
        if not (-0.035 <= dist[t] <= -0.015):
            continue
        for j in range(t + 1, len(v)):
            if v[j] > H[t]:
                hit[t] = 0
                break
            if v[j] <= 0.95 * H[t]:
                hit[t] = 1
                break
    out = {}
    for lab, a in {"1990-2026": "1990-01-02", "2011-2026": "2011-01-03", "channel 2022-2026": "2022-10-13"}.items():
        m = (D.index >= a) & np.isfinite(hit)
        on, off = m & alarm, m & ~alarm
        ep = lambda mask: int((mask & ~np.r_[False, mask[:-1]]).sum())                 # separate runs of qualifying days
        out[lab] = {"P(dip extends to -5% first | alarm)": float(hit[on].mean()), "days, episodes (alarm)": [int(on.sum()), ep(on)],
                    "P(dip extends to -5% first | no alarm)": float(hit[off].mean()), "days, episodes (no alarm)": [int(off.sum()), ep(off)]}
    out["today"] = {"date": str(D.index[-1].date()), "distance %": float(100 * dist[-1]), "alarm": bool(alarm[-1])}
    (Dc.OUT / "posthoc3.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1))
