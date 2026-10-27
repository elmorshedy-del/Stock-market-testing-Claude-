"""A5: does the closing-auction imbalance published at 15:50 push the 15:50 -> close move? Pre-registered @ bdc698c.
Usage: python a5_imbalance.py <folder with SYM_5m.json, SYM_1d.json>  -> out/a5.json, out/a5_rows.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent; Y = Path(sys.argv[1])
SYMS = ["SPY", "TSLA", "GOOGL", "AMZN", "NVDA", "AVGO", "MSFT", "AAPL", "META", "QQQ"]


def bars(sym, kind):
    r = json.loads((Y / f"{sym}_{kind}.json").read_text())["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    idx = pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York")
    return pd.DataFrame({k: q[k] for k in ("open", "close", "volume")}, index=idx).dropna(subset=["close"])


imb = pd.concat([pd.read_parquet(HERE / "data" / "SPY_imbalance.parquet"), pd.read_parquet(HERE / "data" / "NAS_imbalance.parquet")], ignore_index=True)
imb["et"] = pd.to_datetime(imb.ts_event, utc=True).dt.tz_convert("America/New_York")
imb = imb[(imb.auction_type == "C") & (imb.et.dt.strftime("%H:%M:%S") >= "15:50:00")]
imb["d"] = imb.et.dt.date
first = imb.sort_values("et").groupby(["symbol", "d"]).head(1)
rows = []
for sym in SYMS:
    b5 = bars(sym, "5m"); b5 = b5.between_time("09:30", "15:59"); bd = bars(sym, "1d")
    bd.index = bd.index.date
    for _, r in first[first.symbol == sym].iterrows():
        day = r.et.date(); t = b5[b5.index.date == day]
        p50 = t.loc[t.index.strftime("%H:%M") == "15:50", "open"]
        if not len(p50) or day not in bd.index:
            continue
        sgn = 1 if r.side == "B" else (-1 if r.side == "A" else 0)
        dollars = sgn * float(r.total_imbalance_qty) * float(r.ref_price)
        dvol = float(bd.loc[day, "volume"] * bd.loc[day, "close"])
        rows.append({"sym": sym, "day": str(day), "imb $m": dollars / 1e6, "imb % of day $vol": 100 * dollars / dvol,
                     "ret 15:50-close %": 100 * (t.close.iloc[-1] / p50.iloc[0] - 1), "msg time": r.et.strftime("%H:%M:%S")})
df = pd.DataFrame(rows)
rho, _ = spearmanr(df["imb % of day $vol"], df["ret 15:50-close %"])
rng = np.random.default_rng(0); days = df.day.unique(); g = {d: x for d, x in df.groupby("day")}
bs = np.array([spearmanr(*pd.concat([g[d] for d in rng.choice(days, len(days))])[["imb % of day $vol", "ret 15:50-close %"]].T.to_numpy())[0] for _ in range(2000)])
per = {s: round(float(spearmanr(x["imb % of day $vol"], x["ret 15:50-close %"])[0]), 3) for s, x in df.groupby("sym") if len(x) > 5}
big = df["imb % of day $vol"].abs() >= df["imb % of day $vol"].abs().quantile(0.8)
hit = float((np.sign(df.loc[big, "imb % of day $vol"]) == np.sign(df.loc[big, "ret 15:50-close %"])).mean())
res = {"symbol-days": int(len(df)), "days": int(len(days)), "Spearman rho (pooled)": round(float(rho), 3), "p (bootstrap by day, rho <= 0)": round(float(np.mean(bs <= 0)), 4),
       "90% CI": [round(float(np.quantile(bs, 0.05)), 3), round(float(np.quantile(bs, 0.95)), 3)], "passes (rho > 0, p < 0.05)": bool(rho > 0 and np.mean(bs <= 0) < 0.05),
       "per symbol rho": per, "largest-fifth imbalances: share where close moved WITH the imbalance": round(hit, 3), "n largest fifth": int(big.sum()),
       "Oct 26 rows": df[df.day == "2026-10-26"].round(3).to_dict(orient="records")}
df.to_csv(HERE / "out" / "a5_rows.csv", index=False)
(HERE / "out" / "a5.json").write_text(json.dumps(res, indent=1))
print(json.dumps({k: v for k, v in res.items() if k != "Oct 26 rows"}, indent=1))
