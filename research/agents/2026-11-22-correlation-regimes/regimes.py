"""Correlation regimes on big scales: rolling 3-year correlations of weekly S&P returns with bonds, the dollar, the yen, credit, Japan and gold."""
import json
import numpy as np, pandas as pd
from common import H, y, f, gold_monthly, bond_ret, fisher_ci

W = 156  # weeks = 3 years
if __name__ == "__main__":
    wk = lambda s: s.resample("W-FRI").last()
    spx = np.log(wk(y("SPX"))).diff()
    pairs = {
        "Treasuries (10y)": bond_ret(wk(f("DGS10")), 52),
        "Dollar (DXY)": np.log(wk(y("DXY"))).diff(),
        "Yen": -np.log(wk(f("DEXJPUS"))).diff(),
        "Credit (Baa spread narrowing)": -wk(f("BAA10Y")).diff(),
        "Japan stocks (Nikkei)": np.log(wk(y("NIKKEI"))).diff(),
        "Gold": np.log(wk(y("GOLDF"))).diff(),
        "Bitcoin": np.log(wk(y("BTC"))).diff(),
    }
    res, summ = {}, {}
    for k, s in pairs.items():
        df = pd.concat([spx, s], axis=1, keys=["spx", "x"]).dropna()
        rc = df.spx.rolling(W).corr(df.x).dropna(); lo, hi = fisher_ci(rc, W)
        res[k] = pd.DataFrame({"r": rc, "lo": lo, "hi": hi})
        cur = rc.iloc[-1]; pct = (rc < cur).mean()
        dec = rc.groupby((rc.index.year // 10) * 10).mean().round(2).to_dict()
        # regimes: stretches where the 95% band sits entirely above or below zero
        sign = np.where(lo > 0, 1, np.where(hi < 0, -1, 0)); sg = pd.Series(sign, index=rc.index)
        runs = sg.ne(sg.shift()).cumsum(); reg = [(g.index[0].strftime("%Y-%m"), g.index[-1].strftime("%Y-%m"), int(g.iloc[0])) for _, g in sg.groupby(runs) if len(g) >= 26 and g.iloc[0] != 0]
        summ[k] = {"start": rc.index[0].strftime("%Y-%m"), "now": round(float(cur), 2), "now_ci": [round(float(lo.iloc[-1]), 2), round(float(hi.iloc[-1]), 2)],
                   "percentile_now": round(float(pct), 2), "by_decade": dec, "regimes_ci_excludes_zero": reg}
        print(f"\n{k}: from {summ[k]['start']}; now {cur:+.2f} [{lo.iloc[-1]:+.2f},{hi.iloc[-1]:+.2f}], percentile {100*pct:.0f}")
        print("   by decade:", dec)
        print("   regimes (≥ 6 months with the band clear of zero):", reg)
    # long gold: monthly London fix, 36-month windows, 1975+
    gm = np.log(gold_monthly()).diff(); sm = np.log(y("SPX").resample("ME").last()).diff()
    dm = pd.concat([sm, gm], axis=1, keys=["spx", "gold"]).loc["1975":].dropna()
    rg = dm.spx.rolling(36).corr(dm.gold).dropna(); lo, hi = fisher_ci(rg, 36)
    res["Gold (monthly, 1975+)"] = pd.DataFrame({"r": rg, "lo": lo, "hi": hi})
    print("\nGold monthly 36m: by decade", rg.groupby((rg.index.year // 10) * 10).mean().round(2).to_dict(), " now", round(rg.iloc[-1], 2))
    pd.concat(res, axis=1).to_csv(H / "out" / "rolling_corr.csv")
    json.dump(summ, open(H / "out" / "regimes.json", "w"), indent=1)
