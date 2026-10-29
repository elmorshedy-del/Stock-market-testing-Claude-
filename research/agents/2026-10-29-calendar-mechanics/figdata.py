"""Descriptive inputs for the figure (not tests): late-September contrast with year-block CIs by market and era; GEX dose scatter rows.
Usage: python figdata.py <scratchpad> -> out/figdata.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

S = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent; CX = S / "ctx"
sys.path.insert(0, str(HERE)); rng = np.random.default_rng(1)
from partA_lib import yahoo, tag   # noqa: E402

out = {"late_sep": []}
spx = tag(yahoo(S / "long" / "GSPC.json"))
groups = [("S&P 1928-49", spx, 1928, 1949), ("S&P 1950-82", spx, 1950, 1982), ("S&P 1983-2025", spx, 1983, 2025)]
for f, nm, lo in (("%5EGDAXI.json", "DAX 1988-2025", 1988), ("%5EFTSE.json", "FTSE 1984-2025", 1984), ("%5EN225.json", "Nikkei 1970-2025", 1970)):
    groups.append((nm, tag(yahoo(CX / "intl" / f)), lo, 2025))
for nm, d, lo, hi in groups:
    x = d[(d.yr >= lo) & (d.yr <= hi)]; yrs = x.yr.unique(); G = {y: x[x.yr == y] for y in yrs}
    f = lambda z: 1e4 * (z[z.late_sep].r.mean() - z[~z.late_sep].r.mean())
    bs = [f(pd.concat([G[y] for y in rng.choice(yrs, len(yrs))])) for _ in range(2000)]
    out["late_sep"].append({"group": nm, "est": f(x), "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5)), "years": int(len(yrs))})
json.dump(out, open(HERE / "out" / "figdata.json", "w"), indent=1, default=float)
print(pd.DataFrame(out["late_sep"]).round(1).to_string(index=False))
