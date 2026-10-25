"""Part A (pre-registered at 8c1dce0): who buys AAPL during the day? A0 quirk check, A1 segment location, A2 gap reversal, A3 close-pressure reversal.
Usage: python part_a.py <hourly folder>  -> out/part_a.json"""
import json
import sys

import numpy as np
import pandas as pd

import segments as G

NB = 2000
RNG = np.random.default_rng(20261031)
ann = lambda x: float(252 * 100 * x)


def main(folder):
    names = ["AAPL"] + G.PEERS
    P = G.panel(folder, names)
    days = sorted(set.intersection(*[set(P[s].index) for s in names]))
    X = {s: P[s].reindex(days) for s in names}
    n = len(days)
    seg = ["on", "first", "mid", "last"]
    A = {k: {s: X[s][k].to_numpy() for s in names} for k in seg + ["on_next"]}
    res = {"sessions": n, "first / last day": [str(days[0].date()), str(days[-1].date())]}
    def diff(fn, ii):
        return fn("AAPL", ii) - np.mean([fn(s, ii) for s in G.PEERS])
    gap = lambda s, ii: np.nanmean(A["first"][s][ii] + A["mid"][s][ii] + A["last"][s][ii] - A["on"][s][ii])
    al = np.arange(n)
    bsets = [G.blocks(RNG, n) for _ in range(NB)]
    obs = diff(gap, al)
    bs = np.array([diff(gap, ii) for ii in bsets])
    res["A0 intraday minus overnight: AAPL minus peers (annualized %)"] = {"value": ann(obs), "p (<= 0)": float((bs <= 0).mean()),
                                                                           "AAPL": ann(gap("AAPL", al)), "peers": {s: ann(gap(s, al)) for s in G.PEERS}}
    res["A1 segment means (annualized %)"] = {}
    for k in seg:
        fn = lambda s, ii, k=k: np.nanmean(A[k][s][ii])
        o = diff(fn, al)
        b = np.array([diff(fn, ii) for ii in bsets])
        res["A1 segment means (annualized %)"][k] = {"AAPL": ann(fn("AAPL", al)), "peer average": float(np.mean([ann(fn(s, al)) for s in G.PEERS])),
                                                    "AAPL minus peers": ann(o), "p (two-sided)": float(2 * min((b <= 0).mean(), (b >= 0).mean()))}
    def slope_test(xk, yk):
        fn = lambda s, ii: G.slope(A[xk][s][ii], A[yk][s][ii])
        o = diff(fn, al)
        b = np.array([diff(fn, ii) for ii in bsets])
        return {"AAPL slope": fn("AAPL", al), "peer slopes": {s: fn(s, al) for s in G.PEERS}, "AAPL minus peer average": float(o), "p (>= 0)": float((b >= 0).mean())}
    res["A2 first hour on overnight gap"] = slope_test("on", "first")
    res["A3 next overnight on last half hour"] = slope_test("last", "on_next")
    a1 = res["A1 segment means (annualized %)"]
    sig = lambda k: a1[k]["AAPL minus peers"] > 0 and a1[k]["p (two-sided)"] < 0.05
    res["verdicts"] = {
        "H-gap": "supported" if sig("first") and res["A2 first hour on overnight gap"]["AAPL minus peer average"] < 0 and res["A2 first hour on overnight gap"]["p (>= 0)"] < 0.05 else "not supported",
        "H-close": "supported" if sig("last") and res["A3 next overnight on last half hour"]["AAPL minus peer average"] < 0 and res["A3 next overnight on last half hour"]["p (>= 0)"] < 0.05 else "not supported",
        "H-spread": "supported" if sig("mid") and not sig("first") and not sig("last") else "not supported"}
    (G.OUT / "part_a.json").write_text(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1, default=float))
