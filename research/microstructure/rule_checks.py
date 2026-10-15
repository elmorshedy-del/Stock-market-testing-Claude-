"""Re-test the rules in docs/conventions.md on this study's data, instead of taking them on trust.
  R1  same-day timing leak: counting day t's own move invents an edge       (edge_lab C1)
  R2  the null must keep the signal's persistence: a random-day null over-rejects (edge_lab P1 vs F1)
  R3  how big an edge the method can see, and why a few hand-picked events can't be resolved (edge_lab P4)
  R4  week-start dates read as event days look like a weekday effect        (edge_lab C2)
  R5  SPY closes carry quarterly dividend drops on expiry Fridays, so use ^GSPC for S&P returns
R1-R4 rerun edge_lab.py --quick (20 replicates, about 10 seconds; the full run is the frozen record, see edge_lab_controls.md).
Each line prints PASS when the data still support the rule; a FAIL means the rule needs revisiting, not that the check is wrong.
Usage: python rule_checks.py
"""
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd

from common import OUT, load_bars


def edge_rules():
    env = dict(os.environ, OMP_NUM_THREADS="1")
    subprocess.run([sys.executable, "edge_lab.py", "--quick"], check=True, env=env, stdout=subprocess.DEVNULL)
    d = json.loads((OUT / "edge_lab_quick.json").read_text())
    c1, p1, f1, c2, p4 = d["C1 timing leak"], d["P1 false-positive rate"], d["F1 iid null breaks P1"], d["C2 date convention"], \
        d["P4 lift detected 80% of the time (pts)"]
    a, c = p4["a: freed & below flip (real persistence), 3 sessions"], p4["c: 7 hand-picked events, 10 sessions"]
    return [
        ("R1 same-day leak invents an edge", c1["leaky lift"] > c1["forward lift"] + 0.05 and c1["leaky p"] < 0.05 <= c1["forward p"],
         f"dip trigger -> down-bursts: lift {100 * c1['leaky lift']:+.0f} pts counting day t (p {c1['leaky p']:.2f}), "
         f"{100 * c1['forward lift']:+.0f} pts from t+1 (p {c1['forward p']:.2f})"),
        ("R2 random-day null over-rejects", f1["rate"] > p1["rate"],
         f"false positives at p<0.05: time-shift null {100 * p1['rate']:.0f}%, random-day null {100 * f1['rate']:.0f}% "
         "(quick run: 20 replicates, so noisy; the full run gave 2.8% vs 8.8%)"),
        ("R3 few events can't be resolved", c is None or c > 2 * (a or 0),
         f"lift needed for 80% detection: about 60 real episodes {a if a is None else round(a)} pts; 7 hand-picked events "
         f"{'never reached' if c is None else round(c)}"),
        ("R4 week-start dates fake a weekday effect", c2["detector on week-start"] and not c2["detector on actual"],
         f"one weekday holds {100 * c2['week-start max weekday share']:.0f}% of week-start dates vs "
         f"{100 * c2['actual max weekday share']:.0f}% of the actual biggest days (n={c2['n dates']})"),
    ]


def spy_dividend():
    s, g = load_bars("SPY").close, load_bars("^GSPC").close
    idx = s.index.intersection(g.index)
    gap = 100 * (s.reindex(idx).pct_change() - g.reindex(idx).pct_change())
    d = pd.Series(idx, index=idx)
    q = (d.dt.weekday == 4) & d.dt.day.between(15, 21) & d.dt.month.isin([3, 6, 9, 12])
    on, off = gap[q].loc["2005":], gap[~q].loc["2005":]
    return [("R5 SPY dividend drop on quarterly expiry Fridays", on.mean() < -0.2 and abs(off.mean()) < 0.05,
             f"SPY minus ^GSPC return: {on.mean():+.2f} pts on quarterly expiry Fridays (n={len(on)}, {100 * (on < 0).mean():.0f}% negative), "
             f"{off.mean():+.3f} pts on other days")]


if __name__ == "__main__":
    rows = edge_rules() + spy_dividend()
    w = max(len(r[0]) for r in rows)
    for name, ok, got in rows:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<{w}}  {got}")
    sys.exit(not all(ok for _, ok, _ in rows))
