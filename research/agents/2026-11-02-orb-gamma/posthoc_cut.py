"""POST-HOC (derived from the A4 diagnostics, so labelled post hoc): at +30 min after entry, exit only if the trade is <= -kR."""
import json
from pathlib import Path

import numpy as np

import exits as ex   # reuses day_paths, sim, summ, boot_diff (exits.py's main block is guarded below)

C = 0.01


def sim_cut(x, k, T=30):
    hi, lo = x[:5, 1].max(), x[:5, 2].min()
    up = np.flatnonzero(x[5:330, 1] > hi + 0.01); dn = np.flatnonzero(x[5:330, 2] < lo - 0.01)
    iu = up[0] + 5 if len(up) else None; idn = dn[0] + 5 if len(dn) else None
    if iu is None and idn is None: return 0.0
    if idn is None or (iu is not None and iu < idn): side, i = 1, iu
    elif iu is None or idn < iu: side, i = -1, idn
    else: return 0.0
    y = x if side > 0 else -x[:, [0, 2, 1, 3]]; H, L = (hi, lo) if side > 0 else (-lo, -hi)
    e = max(H + 0.01, y[i, 0]); ein = e + C; stop = L; R = ein - stop
    if y[i, 3] <= stop: return (min(stop, y[i, 3]) - 2 * C - ein) / abs(ein) * 1e4
    for j in range(i + 1, 390):
        o, h, l, c = y[j]
        if l <= stop: return (min(stop, o) - 2 * C - ein) / abs(ein) * 1e4
        if j - i == T and (c - C - ein) / R <= -k: return (c - C - ein) / abs(ein) * 1e4
    return (y[389, 3] - C - ein) / abs(ein) * 1e4


res = {}
for lab in ["TSLA", "TSLA2020"]:
    P = ex.day_paths(lab); b = np.array([ex.sim(x, "base")[0] for x in P.values()])
    for k in (0.5, 0.3):
        p = np.array([sim_cut(x, k) for x in P.values()])
        res[f"{lab} cut@30min if <= -{k}R"] = {**ex.summ(p), "mean diff vs base, 90% CI": ex.boot_diff(p, b)}
json.dump(res, open(Path(__file__).resolve().parent / "out" / "posthoc_cut.json", "w"), indent=1)
for k, v in res.items(): print(k, v)
