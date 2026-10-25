"""POST HOC (after round 2 failed; descriptive only, no test): where does the 2011-2022 signal sit?
Splits the AAPL alarm days by S&P 20-day direction and by who leads. Usage: python posthoc2.py <data folder>"""
import json
import sys

import numpy as np
import pandas as pd

import decoupling as Dc


def main(folder):
    D = pd.read_csv(Dc.OUT / "daily.csv", index_col=0, parse_dates=True)
    spx = Dc.close(folder, "GSPC").reindex(D.index)
    aapl = Dc.close(folder, "AAPL").reindex(D.index)
    s20, a20 = np.log(spx).diff(20).to_numpy(), np.log(aapl).diff(20).to_numpy()
    dist = (spx / spx.rolling(252, min_periods=60).max() - 1).to_numpy()
    m = (D.index >= "2011-01-03") & (D.index <= "2022-10-12") & ~D.inside.astype(bool).to_numpy() & D["corr AAPL"].notna().to_numpy()
    alarm, ahead = D["alarm AAPL"].astype(bool).to_numpy(), D.ahead.astype(bool).to_numpy()
    cells = {"S&P up, AAPL lags (narrowing)": (s20 > 0) & (a20 < s20), "S&P up, AAPL leads": (s20 > 0) & (a20 >= s20),
             "S&P down, AAPL holds up better": (s20 <= 0) & (a20 >= s20), "S&P down, AAPL falls more": (s20 <= 0) & (a20 < s20)}
    out = {}
    for k, c in cells.items():
        on, off = m & alarm & c, m & ~alarm & c
        out[k] = {"alarm days": int(on.sum()), "P(top in 30 | alarm, this cell)": float(ahead[on].mean()),
                  "P(top in 30 | no alarm, same cell)": float(ahead[off].mean()), "median distance to 252d high %, alarm": float(100 * np.nanmedian(dist[on]))}
    out["all no-alarm days"] = float(ahead[m & ~alarm].mean())
    out["median distance to 252d high %: alarm / no alarm"] = [float(100 * np.nanmedian(dist[m & alarm])), float(100 * np.nanmedian(dist[m & ~alarm]))]
    (Dc.OUT / "posthoc2.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1))
