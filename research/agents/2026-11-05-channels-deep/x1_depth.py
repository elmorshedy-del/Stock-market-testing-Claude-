"""X1 (exploratory, added after P0-P4 were pre-registered; not a test). Base rate for the owner's question at today's depth:
of every S&P decline from a record close that reached today's closing depth, how many went on to -10% and to -20% before a new record?
Each episode is listed individually. Usage: python x1_depth.py"""
import json, importlib.util, numpy as np, pandas as pd
from pathlib import Path
H = Path(__file__).resolve().parent; O = H / "out"
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
s = lc.yahoo("^GSPC", "1927-12-01").close; v = s.values; ix = s.index
rec_now = int(np.argmax(v)); depth_now = v[-1] / v[rec_now] - 1; th = -depth_now
eps = []; rec = 0; lo = 0; hit = None
for i in range(1, len(v)):
    if v[i] > v[rec]:
        if hit is not None: eps.append({"record": str(ix[rec].date()), "month": int(ix[rec].month), "sessions to reach today's depth": int(hit - rec), "final depth %": round(100 * (v[lo] / v[rec] - 1), 1),
                                        "trough": str(ix[lo].date()), "sessions to new record": int(i - rec)})
        rec = i; lo = i; hit = None
    else:
        if v[i] < v[lo]: lo = i
        if hit is None and v[i] <= v[rec] * (1 - th): hit = i
E = pd.DataFrame(eps); E = E[E.record >= "1950-01-01"]
fast = E[E["sessions to reach today's depth"] <= int(len(v) - 1 - rec_now)]
summ = lambda d: {"n": int(len(d)), "reached -10%": int((d["final depth %"] <= -10).sum()), "reached -20%": int((d["final depth %"] <= -20).sum()), "stopped above -10%": int((d["final depth %"] > -10).sum())}
out = {"today": {"close": round(float(v[-1]), 2), "record": round(float(v[rec_now]), 2), "record date": str(ix[rec_now].date()), "depth %": round(100 * depth_now, 2), "sessions since record": int(len(v) - 1 - rec_now)},
       "since 1950, every decline from a record that reached today's depth": summ(E),
       "same, but it reached today's depth at least as fast as now": summ(fast), "episodes": E.to_dict("records")}
json.dump(out, open(O / "x1_depth.json", "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in out.items() if k != "episodes"}, indent=1))
print(E.to_string(index=False))
