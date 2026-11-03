"""A5: the TSLA 5-min breakout traded with options instead of shares.
Same entries/stops as S1_5_close on the underlying. Buy the ATM call (long break) or put (short break) at the ASK of the quote at the
start of the next minute; sell at the BID at the start of the minute after the underlying stop, else at the 15:55 quote.
Two expiries: 'next' (nearest expiry >= 1 day out) and '0dte' (only on days with a same-day expiry).
Usage: python opts.py -> out/opts.json"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; D = HERE / "data"; OP = D / "opt"; O = HERE / "out"; C = 0.01; M = 5
HM = pd.date_range("09:30", "15:59", freq="1min").strftime("%H:%M"); EXIT_HM = "15:55"; EXIT_I = list(HM).index(EXIT_HM)


def trade(x):
    """Underlying S1_5 trade: side, entry minute i, entry px, exit minute j (bar where the stop hit, or EXIT_I), share pnl bp (exit at the stop or 15:55 close)."""
    hi, lo = x[:M, 1].max(), x[:M, 2].min()
    up = np.flatnonzero(x[M:330, 1] > hi + 0.01); dn = np.flatnonzero(x[M:330, 2] < lo - 0.01)
    iu = up[0] + M if len(up) else None; idn = dn[0] + M if len(dn) else None
    if iu is None and idn is None: return None
    if idn is None or (iu is not None and iu < idn): side, i = 1, iu
    elif iu is None or idn < iu: side, i = -1, idn
    else: return None
    y = x if side > 0 else -x[:, [0, 2, 1, 3]]; H, L = (hi, lo) if side > 0 else (-lo, -hi)
    e = max(H + 0.01, y[i, 0]); ein = e + C; stop = L
    if y[i, 3] <= stop: return side, i, abs(e), i, (min(stop, y[i, 3]) - 2 * C - ein) / abs(ein) * 1e4
    for j in range(i + 1, EXIT_I + 1):
        o, h, l, c = y[j]
        if l <= stop: return side, i, abs(e), j, (min(stop, o) - 2 * C - ein) / abs(ein) * 1e4
    return side, i, abs(e), EXIT_I, (y[EXIT_I, 3] - C - ein) / abs(ein) * 1e4


rth = pd.read_parquet(D / "TSLA_rth_d2.parquet"); rows = []
for d, g in rth.groupby("date"):
    g = g.set_index("hm").reindex(HM)
    if g.open.isna().iloc[:30].any(): continue
    x = g[["open", "high", "low", "close"]].ffill().to_numpy(); t = trade(x)
    if t is None: continue
    side, i, e, j, sh = t
    rec = {"date": d, "side": side, "entry_hm": HM[i], "exit_hm": HM[j], "stopped": j < EXIT_I, "shares_bp": sh}
    for tag in ("next", "0dte"):
        f = OP / f"{d:%Y%m%d}_{tag}.parquet"
        if not f.exists(): continue
        o = pd.read_parquet(f); o["hm"] = pd.to_datetime(o.timestamp.astype(str).str[:19]).dt.strftime("%H:%M")
        r = o[o.right == ("CALL" if side > 0 else "PUT")]
        if r.empty: continue
        k = r.strike.unique()[np.argmin(np.abs(r.strike.unique() - e))]; q = r[r.strike == k].set_index("hm")
        t_in = HM[min(i + 1, 389)]; t_out = HM[min(j + 1, 389)] if j < EXIT_I else EXIT_HM
        if t_in not in q.index or t_out not in q.index: continue
        ask, bid = float(q.loc[t_in, "ask"]), float(q.loc[t_out, "bid"])
        if not (ask > 0) or not (bid >= 0): continue
        mid_in = (float(q.loc[t_in, "bid"]) + ask) / 2
        rec[f"{tag}_strike"] = k; rec[f"{tag}_ask_in"] = ask; rec[f"{tag}_bid_out"] = bid
        rec[f"{tag}_ret"] = bid / ask - 1; rec[f"{tag}_spread_pct_in"] = (ask - float(q.loc[t_in, "bid"])) / mid_in if mid_in > 0 else np.nan
        rec[f"{tag}_prem_pct_of_stock"] = ask / e
    rows.append(rec)
T = pd.DataFrame(rows).set_index("date"); T.to_parquet(O / "opts_trades.parquet")


def summ(r, sh):
    r = r.dropna(); s = sh.reindex(r.index)
    return {"trades": int(len(r)), "mean return on premium %": round(float(r.mean() * 100), 1), "median %": round(float(r.median() * 100), 1),
            "win %": round(float((r > 0).mean() * 100), 1), "avg win %": round(float(r[r > 0].mean() * 100), 1), "avg loss %": round(float(r[r < 0].mean() * 100), 1),
            "best / worst %": [round(float(r.max() * 100), 0), round(float(r.min() * 100), 0)],
            "same days, shares bp/trade": round(float(s.mean()), 1), "by year mean %": {int(y): round(float(r[r.index.year == y].mean() * 100), 1) for y in sorted(set(r.index.year))}}


res = {"days with a trade": len(T), "rule": "ATM call/put, buy ask (next-minute quote), sell bid at the stop or 15:55"}
for tag in ("next", "0dte"):
    if f"{tag}_ret" in T:
        res[tag] = summ(T[f"{tag}_ret"], T.shares_bp)
        res[tag]["median entry spread % of mid"] = round(float(T[f"{tag}_spread_pct_in"].median() * 100), 1)
        res[tag]["median premium % of stock price"] = round(float(T[f"{tag}_prem_pct_of_stock"].median() * 100), 2)
        for nm, sel in (("stopped trades", T.stopped), ("held to 15:55", ~T.stopped)):
            rr = T.loc[sel, f"{tag}_ret"].dropna(); res[tag][f"{nm}: n, mean %"] = [int(len(rr)), round(float(rr.mean() * 100), 1)]
json.dump(res, open(O / "opts.json", "w"), indent=1, default=str); print(json.dumps(res, indent=1, default=str))
