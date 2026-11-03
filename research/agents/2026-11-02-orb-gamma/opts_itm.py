"""EXPLORATORY (not pre-registered): A5 with in-the-money strikes (k strikes ITM) for the next expiry and 0DTE. -> out/opts_itm.json"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; OP = HERE / "data" / "opt"; O = HERE / "out"
HM = list(pd.date_range("09:30", "15:59", freq="1min").strftime("%H:%M"))
T = pd.read_parquet(O / "opts_trades.parquet")
rth = pd.read_parquet(HERE / "data" / "TSLA_rth_d2.parquet")
px = rth.set_index(["date", "hm"]).open
res = {}
for tag in ("next", "0dte"):
    for k in (0, 2, 4):
        out = []
        for d, r in T.iterrows():
            f = OP / f"{d:%Y%m%d}_{tag}.parquet"
            if not f.exists(): continue
            o = pd.read_parquet(f); o["hm"] = pd.to_datetime(o.timestamp.astype(str).str[:19]).dt.strftime("%H:%M")
            right = "CALL" if r.side > 0 else "PUT"; q0 = o[o.right == right]
            e = px.get((d, r.entry_hm), np.nan)
            ks = np.sort(q0.strike.unique()); atm = int(np.argmin(np.abs(ks - e)))
            idx = atm - k if r.side > 0 else atm + k
            if idx < 0 or idx >= len(ks): continue
            q = q0[q0.strike == ks[idx]].set_index("hm")
            i = HM.index(r.entry_hm); t_in = HM[min(i + 1, 389)]
            t_out = HM[min(HM.index(r.exit_hm) + 1, 389)] if r.stopped else "15:55"
            if t_in not in q.index or t_out not in q.index: continue
            ask, bid = float(q.loc[t_in, "ask"]), float(q.loc[t_out, "bid"])
            if ask > 0 and bid >= 0: out.append((d, bid / ask - 1, ask / e))
        s = pd.DataFrame(out, columns=["date", "ret", "prem"]).set_index("date")
        res[f"{tag} {k} strikes ITM"] = {"trades": len(s), "mean %": round(float(s.ret.mean() * 100), 1), "median %": round(float(s.ret.median() * 100), 1),
                                          "win %": round(float((s.ret > 0).mean() * 100), 1), "premium % of stock": round(float(s.prem.median() * 100), 2),
                                          "t-stat": round(float(s.ret.mean() / (s.ret.std() / np.sqrt(len(s)))), 2),
                                          "by year mean %": {int(y): round(float(s.ret[s.index.year == y].mean() * 100), 1) for y in sorted(set(s.index.year))}}
        print(tag, k, res[f"{tag} {k} strikes ITM"], flush=True)
json.dump(res, open(O / "opts_itm.json", "w"), indent=1)
