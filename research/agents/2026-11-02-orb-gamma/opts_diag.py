"""EXPLORATORY diagnosis: why options lose the share edge. Decompose the ATM next-expiry option return (mid to mid, no spread) into
leverage x stock move + convexity + a zero-move drift (time decay + implied-vol change). -> out/opts_diag.json"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; OP = HERE / "data" / "opt"; O = HERE / "out"
HM = list(pd.date_range("09:30", "15:59", freq="1min").strftime("%H:%M"))
T = pd.read_parquet(O / "opts_trades.parquet"); px = pd.read_parquet(HERE / "data" / "TSLA_rth_d2.parquet").set_index(["date", "hm"]).close
rows = []
for d, r in T.dropna(subset=["next_strike"]).iterrows():
    o = pd.read_parquet(OP / f"{d:%Y%m%d}_next.parquet"); o["hm"] = pd.to_datetime(o.timestamp.astype(str).str[:19]).dt.strftime("%H:%M")
    q = o[(o.strike == r.next_strike) & (o.right == ("CALL" if r.side > 0 else "PUT"))].set_index("hm")
    t_in = HM[min(HM.index(r.entry_hm) + 1, 389)]; t_out = HM[min(HM.index(r.exit_hm) + 1, 389)] if r.stopped else "15:55"
    if t_in not in q.index or t_out not in q.index: continue
    mi = (q.loc[t_in, "bid"] + q.loc[t_in, "ask"]) / 2; mo = (q.loc[t_out, "bid"] + q.loc[t_out, "ask"]) / 2
    s_in = px.get((d, HM[HM.index(t_in) - 1]), np.nan); s_out = px.get((d, HM[HM.index(t_out) - 1]), np.nan)
    if mi > 0 and s_in > 0: rows.append({"date": d, "opt_mid_ret": mo / mi - 1, "opt_fill_ret": r.next_ret, "stock_ret_dir": r.side * (s_out / s_in - 1),
                                         "dte": (pd.Timestamp(q.expiration.iloc[0]) - d).days, "hours": (HM.index(t_out) - HM.index(t_in)) / 60})
X = pd.DataFrame(rows); s = X.stock_ret_dir
A = np.column_stack([np.ones(len(X)), s, s ** 2]); coef = np.linalg.lstsq(A, X.opt_mid_ret, rcond=None)[0]
res = {"trades": len(X), "mean option return, filled at ask/bid %": round(float(X.opt_fill_ret.mean() * 100), 1), "mean option return, mid to mid %": round(float(X.opt_mid_ret.mean() * 100), 1),
       "spread cost per round trip (mean fill - mid) %": round(float((X.opt_fill_ret - X.opt_mid_ret).mean() * 100), 1),
       "fit: zero-move drift per trade % (time decay + IV change)": round(float(coef[0] * 100), 1), "fit: leverage (option % per 1% stock move)": round(float(coef[1] / 100 * 100), 1),
       "fit: convexity coefficient": round(float(coef[2]), 1), "mean directional stock move during the trade %": round(float(s.mean() * 100), 3),
       "median days to expiry": float(X.dte.median()), "median hours held": round(float(X.hours.median()), 1),
       "drift by days to expiry (%, n)": {int(k): [round(float(g.opt_mid_ret.mean() * 100 - coef[1] * g.stock_ret_dir.mean() * 100 - coef[2] * (g.stock_ret_dir ** 2).mean() * 100), 1), int(len(g))] for k, g in X.groupby(X.dte.clip(upper=5))}}
json.dump(res, open(O / "opts_diag.json", "w"), indent=1); print(json.dumps(res, indent=1))
