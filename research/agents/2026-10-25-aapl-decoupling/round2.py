"""Amendment 1: narrowing-rally split of the AAPL alarm, 2011-2022 (out of sample). Usage: python round2.py <data folder>"""
import json
import sys

import numpy as np
import pandas as pd

import decoupling as Dc


def main(folder):
    D = pd.read_csv(Dc.OUT / "daily.csv", index_col=0, parse_dates=True)
    spx = Dc.close(folder, "GSPC").reindex(D.index)
    aapl = Dc.close(folder, "AAPL").reindex(D.index)
    s20, a20 = np.log(spx).diff(20), np.log(aapl).diff(20)
    m = (D.index >= "2011-01-03") & (D.index <= "2022-10-12") & ~D.inside.astype(bool).to_numpy() & D["corr AAPL"].notna().to_numpy()
    alarm = D["alarm AAPL"].astype(bool).to_numpy()
    narrow = alarm & (s20 > 0).to_numpy() & (a20 < s20).to_numpy()
    other = alarm & ~narrow
    ahead = D.ahead.astype(bool).to_numpy()
    res = {}
    for lab, sub in (("narrowing-rally alarm", narrow), ("other alarm days", other)):
        ok = m & (sub | ~alarm)                                  # compare each subset with the no-alarm days
        res[lab] = Dc.diff_test(sub, ahead, ok)
    res["verdict"] = "pass" if (res["narrowing-rally alarm"]["difference"] > 0 and res["narrowing-rally alarm"]["p (one-sided, shift)"] < 0.05
                                and res["narrowing-rally alarm"]["difference"] > res["other alarm days"]["difference"]) else "fail"
    today = D.index[-1]
    res["today"] = {"alarm": bool(alarm[-1]), "S&P 20d return %": float(100 * s20.iloc[-1]), "AAPL 20d return %": float(100 * a20.iloc[-1]),
                    "narrowing rally": bool(narrow[-1])}
    (Dc.OUT / "round2.json").write_text(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1, default=float))
