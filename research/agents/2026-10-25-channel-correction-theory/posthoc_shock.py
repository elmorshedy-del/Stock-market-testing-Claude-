"""POST HOC (descriptive, after Amendment 2): which shock drove each correction? USD/JPY and TLT from the high to the trough.
yen shock: USD/JPY <= -2% (yen up); rates shock: TLT <= -2% with USD/JPY up; otherwise other. Usage: python posthoc_shock.py <etfs folder>"""
import json
import sys

import numpy as np
import pandas as pd

import dossier as Dz
import yen as Yn


def main(etfs):
    Y = pd.read_csv(Dz.OUT / "yen_episodes.csv")
    tlt = Dz.close(etfs, "TLT")
    spx = Dz.close(etfs, "%5EGSPC")
    out = {}
    for _, r in Y[Y.outcome == "correction"].iterrows():
        hi = pd.Timestamp(r.episode.split(" ")[1])
        tr = pd.Timestamp(r.trough)
        t = float(100 * (tlt.asof(tr) / tlt.asof(hi) - 1))
        jy = float(r["USD/JPY % high -> trough"])
        kind = "yen shock" if jy <= -2 else ("rates shock" if t <= -2 and jy > 0 else "other")
        out[r.episode] = {"S&P depth %": round(float(r["S&P depth % (high -> trough)"]), 1), "USD/JPY %": round(jy, 1), "TLT %": round(t, 1), "kind": kind}
    (Dz.OUT / "shock_types.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1))
