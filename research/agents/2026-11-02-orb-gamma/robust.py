"""Exploratory robustness of the S1_5_close breakout (labelled exploratory): costs, outlier days, news-gap days, drawdowns, months,
and the clean vs flagged-day split. -> out/robust.json"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; D = HERE / "data"; O = HERE / "out"; K = "S1_5_close"


def pnl(df):
    d = df[K + "_dir"].to_numpy(); return pd.Series(np.where(d > 0, df[K + "_L"].fillna(0), np.where(d < 0, df[K + "_S"].fillna(0), 0.0)), index=df.index), d


def stats(lab):
    df = pd.read_parquet(O / f"days_{lab}.parquet"); p, d = pnl(df); tr = d != 0
    y = pd.read_csv(D / f"{lab.replace('_d2', '')}_yahoo_daily.csv", index_col=0, parse_dates=True)
    gap = (df.open / y.close.shift(1).reindex(df.index) - 1).abs() * 1e4
    eq = p.cumsum(); dd = (eq - eq.cummax()).min(); m = p.groupby(p.index.to_period("M")).sum()
    cost = lambda c: (p - np.where(tr, 2 * c / df.px935 * 1e4, 0)).mean()   # extra cents per side on top of the base 1c
    big = gap >= gap.quantile(0.9)
    A = pd.read_csv(O / (f"audit_days_{lab.replace('_d2', '')}.csv" if lab.replace("_d2", "") != "SPY" else "audit_days.csv"), parse_dates=["date"]).set_index("date").status.reindex(df.index)
    return {"days": len(df), "mean bp/day": round(float(p.mean()), 2), "median trade bp": round(float(p[tr].median()), 1),
            "mean with +2c / +5c / +10c per side": [round(float(cost(c)), 2) for c in (0.02, 0.05, 0.10)],
            "mean without the 10 best days": round(float(p.drop(p.nlargest(10).index).mean()), 2),
            "mean without top-decile |gap| days (news proxy)": round(float(p[~big].mean()), 2), "mean on top-decile |gap| days": round(float(p[big].mean()), 2),
            "max drawdown (cum bp, 1x)": round(float(dd), 0), "share of positive months": round(float((m > 0).mean()), 2), "worst month bp": round(float(m.min()), 0),
            "clean days mean / flagged (D2) days mean": [round(float(p[A == "clean"].mean()), 2), round(float(p[A == "bad_D2"].mean()), 2) if (A == "bad_D2").any() else None]}


res = {lab: stats(lab) for lab in ["TSLA2020", "TSLA2020_d2", "TSLA", "TSLA_d2", "NVDA_d2", "AMD_d2", "NFLX_d2", "META_d2", "AMZN_d2", "UNH_d2", "JPM_d2", "SPY_d2", "QQQ_d2"]}
json.dump(res, open(O / "robust.json", "w"), indent=1, default=str)
for k, v in res.items(): print(f"{k:12s}", json.dumps(v))
