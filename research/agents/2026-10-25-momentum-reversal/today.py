"""Today's momentum ranking among the 81 large caps (descriptive): 12-1 month momentum at the last month-end and the latest close.
Usage: python today.py <long> <breadth>  -> out/today.json"""
import json
import sys

import numpy as np
import pandas as pd

import momentum as Mo


def main(long, bfold):
    names = Mo.Dz.PANEL + Mo.EXTRA
    C = pd.DataFrame({s: (Mo.Dz.close(long, s) if s in Mo.Dz.PANEL else Mo.Dz.close(bfold, s)) for s in names}).ffill(limit=3)
    last = C.index[-1]
    m12 = C.iloc[-1 - 21] / C.iloc[-1 - 252] - 1                            # t-12 to t-1 months, on daily closes
    q = m12.rank(pct=True)
    res = {"as of": str(last.date()), "top third (winners)": (100 * m12[q > 2 / 3].sort_values(ascending=False)).round(1).to_dict(),
           "bottom third (losers)": (100 * m12[q <= 1 / 3].sort_values()).round(1).to_dict()}
    (Mo.OUT / "today.json").write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    r = main(*sys.argv[1:3])
    print("winners:", list(r["top third (winners)"].items())[:10]); print("losers:", list(r["bottom third (losers)"].items())[:10])
