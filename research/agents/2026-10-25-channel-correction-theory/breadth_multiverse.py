"""Amendment 4 (pre-registered at e0c9490): is the breadth result a 50-day artefact? 58 versions of breadth, signed AUC (theory: broader -> correction)
on the 21 decided dips; multiverse luck check on the median AUC. Usage: python breadth_multiverse.py <long folder> <breadth folder> <etfs folder>
-> out/breadth_multiverse.csv, out/breadth_multiverse.json"""
import json
import sys

import numpy as np
import pandas as pd

import dossier as Dz

RNG = np.random.default_rng(20261106)
EXTRA = ["AVGO", "TSLA", "CRM", "NFLX", "BRK-B", "V", "MA", "ABBV", "TMO", "ACN", "LIN", "NKE", "AMGN", "HON", "UPS", "LOW", "SBUX", "GS", "MS", "BLK",
         "SPGI", "INTU", "NOW", "ISRG", "BKNG", "ADP", "DE", "CVS", "MDT", "GILD", "NEE", "DUK", "PM", "CMCSA", "LMT", "RTX", "UNP", "COP", "AXP", "SCHW"]
MEGA = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "AVGO", "TSLA"]
LOOK = [10, 20, 50, 100, 150, 200]


def main(long, bfolder, etfs):
    spx = Dz.close(etfs, "%5EGSPC")
    idx = spx.index[spx.index >= "2020-06-01"]
    P1 = pd.DataFrame({s: Dz.close(long, s).reindex(idx).ffill(limit=3) for s in Dz.PANEL})
    PX = pd.DataFrame({s: Dz.close(bfolder, s).reindex(idx).ffill(limit=3) for s in EXTRA})
    U = {"U1 panel 41": P1, "U2 panel + 40 (81)": pd.concat([P1, PX], axis=1),
         "U3 panel ex-mega (35)": P1.drop(columns=[m for m in MEGA if m in P1]),
         "U4 81 ex-mega (73)": pd.concat([P1, PX], axis=1).drop(columns=MEGA)}
    def share(cond, valid):
        return cond.where(valid).mean(axis=1)
    M = {}
    for u, P in U.items():
        for L in LOOK:
            ma = P.rolling(L, min_periods=L).mean()
            M[(f"above {L}-day", u)] = share(P > ma, ma.notna())
    for u in ["U1 panel 41", "U2 panel + 40 (81)"]:
        P = U[u]
        r20 = P / P.shift(20) - 1
        M[("positive 20-day return", u)] = share(r20 > 0, r20.notna())
        hi = P.rolling(252, min_periods=200).max()
        M[("within 5% of 252-day high", u)] = share(P >= 0.95 * hi, hi.notna())
    ratio = Dz.close(etfs, "RSP").reindex(idx).ffill() / Dz.close(etfs, "SPY").reindex(idx).ffill()
    M[("equal weight vs SPY (percentile)", "RSP/SPY")] = Dz.pct(ratio)
    E = pd.read_csv(Dz.OUT / "dips.csv", parse_dates=["start"])
    dec = E[E.outcome != "open"].reset_index(drop=True)
    y = (dec.outcome == "correction").to_numpy().astype(int)
    today_start = E[E.outcome == "open"].start.iloc[0]
    def sauc(v, yy):
        c, b = v[yy == 1], v[yy == 0]
        return float((c[:, None] > b[None, :]).mean() + 0.5 * (c[:, None] == b[None, :]).mean())
    rows, V = [], []
    for (meas, u), s in M.items():
        for rd in ("5-day mean", "start day"):
            ser = s.rolling(5, min_periods=4).mean() if rd == "5-day mean" else s
            v = ser.reindex(dec.start).to_numpy(float)
            vt = float(ser.loc[today_start])
            vl = float(ser.iloc[-1])
            rows.append({"measure": meas, "universe": u, "reading": rd, "AUC (broader -> correction)": sauc(v, y),
                         "corrections mean": float(np.nanmean(v[y == 1])), "bounces mean": float(np.nanmean(v[y == 0])),
                         "today at dip start": vt, "today percentile among 21 dips": float((v < vt).mean()), "latest (Oct 23)": vl})
            V.append(v)
    R = pd.DataFrame(rows)
    V = np.array(V)
    obs_med = float(R["AUC (broader -> correction)"].median())
    null = np.array([np.median([sauc(v, yy) for v in V]) for yy in (RNG.permutation(y) for _ in range(5000))])
    look = R[(R.measure.str.startswith("above")) & (R.universe == "U1 panel 41") & (R.reading == "5-day mean")]
    a50 = R[(R.measure == "above 50-day") & (R.reading == "5-day mean")].set_index("universe")["AUC (broader -> correction)"]
    c1 = bool(look["AUC (broader -> correction)"].median() >= 0.75 and (look["AUC (broader -> correction)"] >= 0.70).sum() >= 5)
    c2 = bool(all(a50[u] >= 0.70 for u in ["U2 panel + 40 (81)", "U3 panel ex-mega (35)", "U4 81 ex-mega (73)"]))
    c3 = bool((null >= obs_med).mean() < 0.05)
    res = {"versions": int(len(R)), "median AUC, all versions": obs_med, "multiverse p (shuffled medians >= observed)": float((null >= obs_med).mean()),
           "share of versions with AUC >= 0.70": float((R["AUC (broader -> correction)"] >= 0.70).mean()),
           "AUC by lookback (U1, 5-day)": dict(zip(look.measure, look["AUC (broader -> correction)"].round(3))),
           "50-day AUC by universe (5-day)": a50.round(3).to_dict(),
           "alternative measures (5-day)": R[(~R.measure.str.startswith("above")) & (R.reading == "5-day mean")].set_index(["measure", "universe"])["AUC (broader -> correction)"].round(3).to_dict(),
           "checks (lookbacks, universes, multiverse)": [c1, c2, c3], "verdict": "robust, not a magic number" if (c1 and c2 and c3) else "not robust",
           "today: median percentile among the 21 dips across versions": float(R["today percentile among 21 dips"].median()),
           "today: share of versions where today is below every correction's reading": None}
    lowest_corr = []
    for i, r in R.iterrows():
        lowest_corr.append(r["today at dip start"] < np.nanmin(V[i][y == 1]))
    res["today: share of versions where today is below every correction's reading"] = float(np.mean(lowest_corr))
    res["alternative measures (5-day)"] = {f"{k[0]} | {k[1]}": v for k, v in res["alternative measures (5-day)"].items()}
    R.round(4).to_csv(Dz.OUT / "breadth_multiverse.csv", index=False)
    (Dz.OUT / "breadth_multiverse.json").write_text(json.dumps(res, indent=1, default=float))
    return R, res


if __name__ == "__main__":
    R, res = main(*sys.argv[1:4])
    pd.set_option("display.width", 250)
    print(R[R.reading == "5-day mean"][["measure", "universe", "AUC (broader -> correction)", "corrections mean", "bounces mean", "today at dip start", "today percentile among 21 dips"]].round(3).to_string())
    print(json.dumps(res, indent=1, default=float))
