"""M1 as pre-registered (f8629cf): next-month S&P return when the 12-month sign is + minus when it is - , overall and per regime cell.
(momentum.py's first run used strategy-minus-buy-and-hold by mistake; this is the registered statistic.) Usage: python m1_fix.py <long>"""
import json
import sys

import numpy as np
import pandas as pd

import momentum as Mo


def diff(rn, sig, m):
    a, b = rn[m & (sig > 0)], rn[m & (sig < 0)]
    return (a.mean() - b.mean()) if len(a) and len(b) else np.nan, int(len(a)), int(len(b))


def main(long):
    spx = Mo.Dz.close(long, "GSPC")
    R = Mo.market_regimes(spx)
    P = Mo.monthly(spx)
    rn = np.log(P).diff().shift(-1).to_numpy()
    Rm = R.reindex(P.index, method="ffill")
    Rm["trend"] = np.where(P > P.rolling(10).mean(), "above 10m avg", "below 10m avg")
    out = {}
    for lb in (12, 3, 1):
        sig = np.sign(np.log(P).diff(lb)).to_numpy()
        ok = np.isfinite(sig) & np.isfinite(rn)
        obs, nl, ns = diff(rn, sig, ok)
        bs = []
        for _ in range(Mo.NB):
            ii = Mo.blocks(len(rn), 12)
            bs.append(diff(rn[ii], sig[ii], ok[ii])[0])
        bs = np.array(bs)
        row = {"long minus short, %/month": 100 * obs, "months long / short": [nl, ns], "p (<= 0)": float(np.nanmean(bs <= 0))}
        if lb == 12:
            cells = []
            for reg in ("vol", "state", "trend", "era"):
                lab = Rm[reg].to_numpy()
                for c in sorted(set(x for x in lab if isinstance(x, str) and x)):
                    m = ok & (lab == c)
                    v, a, b = diff(rn, sig, m)
                    bb = [diff(rn[ii], sig[ii], m[ii])[0] for ii in (Mo.blocks(len(rn), 12) for _ in range(1000))]
                    cells.append({"regime": reg, "cell": c, "long minus short %/month": 100 * v, "months long / short": [a, b],
                                  "lo90": float(100 * np.nanpercentile(bb, 5)), "hi90": float(100 * np.nanpercentile(bb, 95))})
            row["cells"] = cells
            def con(reg, a_, b_):
                lab = Rm[reg].to_numpy()
                f = lambda ii: diff(rn[ii], sig[ii], ok[ii] & (lab[ii] == a_))[0] - diff(rn[ii], sig[ii], ok[ii] & (lab[ii] == b_))[0]
                o = f(np.arange(len(rn))); bb = np.array([f(Mo.blocks(len(rn), 12)) for _ in range(Mo.NB)])
                p = float(np.nanmean(bb <= 0))
                return {"contrast": f"{a_} minus {b_}", "value %/month": 100 * o, "p (<= 0)": p, "supported": bool(o > 0 and p < 0.05)}
            row["contrasts"] = [con("vol", "high vol", "low vol"), con("state", "bear (24m down)", "bull (24m up)")]
        out[f"{lb}m lookback"] = row
    (Mo.OUT / "m1.json").write_text(json.dumps(out, indent=1, default=float))
    return out


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1, default=float))
