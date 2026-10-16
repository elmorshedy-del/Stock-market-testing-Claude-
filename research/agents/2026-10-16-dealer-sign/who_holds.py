"""Who took which side on Cboe, by participant, gamma-weighted with our own ThetaData chain for the same day."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/stock-market-testing-claude-/research/microstructure")
import os; os.chdir("/home/user/stock-market-testing-claude-/research/microstructure")
import td_gamma as t

path, day = sys.argv[1], pd.Timestamp(sys.argv[2])
d = pd.read_csv(path, low_memory=False)
d["cp"] = d.call_or_put.str.upper().str[0]
d["expiration"] = pd.to_datetime(d.expiration_date.astype(str))
d["strike"] = d.strike_price.astype(float)
groups = {"customer": "cust_", "pro customer": "procust_", "firm": "firm_", "broker-dealer": "bd_", "market maker": "mm_"}
def net(x, pre):
    b = [c for c in x.columns if c.startswith(pre) and c.endswith("_vol") and "_buy_" in c]
    s = [c for c in x.columns if c.startswith(pre) and c.endswith("_vol") and "_sell_" in c]
    return x[b].sum(axis=1) - x[s].sum(axis=1)
def opening(x, pre, side):
    c = [c for c in x.columns if c.startswith(pre) and c.endswith("_vol") and f"open_{side}" in c]
    return x[c].sum(axis=1)
def gamma(S, K, T, iv):
    from scipy.stats import norm
    d1 = (np.log(S / K) + 0.5 * iv ** 2 * T) / (iv * np.sqrt(T))
    return norm.pdf(d1) / (S * iv * np.sqrt(T))
for sym in sys.argv[3:]:
    x = d[d.underlying == sym].copy()
    if not len(x):
        print(sym, "not in file"); continue
    for k, pre in groups.items():
        x[k] = net(x, pre)
    try:
        eod, oi = t.read(sym, "eod"), t.read(sym, "oi")
        e = eod[eod.date == day].copy(); e["mid"] = (e.bid + e.ask) / 2
        key = ["expiration", "strike", "cp"]
        o0 = oi[oi.date == day].rename(columns={"open_interest": "oi"})
        g = t.chain_day(e.merge(o0[["date"] + key + ["oi"]], on=["date"] + key, how="left").fillna({"oi": 0}))
        S = float(g.underlying_close.iloc[0])
        g["gam"] = gamma(S, g.K.to_numpy(), g["T"].to_numpy(), g.iv.to_numpy()) * 100 * S * S * 0.01     # $ gamma per 1% per contract
        x = x.merge(g[["expiration", "strike", "cp", "gam", "oi"]], on=["expiration", "strike", "cp"], how="left")
        cover = x.gam.notna().mean()
    except Exception as ex:
        print(sym, "chain unavailable:", ex); x["gam"], S, cover = np.nan, np.nan, 0
    print(f"\n{sym} {day.date()}  spot {S:.2f}  contracts matched to our chain {100 * cover:.0f}%")
    rows = []
    for cp in ("C", "P"):
        y = x[x.cp == cp]
        r = {"side": "calls" if cp == "C" else "puts"}
        for k in groups:
            r[f"{k} net contracts"] = int(y[k].sum())
        r["customer+pro opening buys"] = int((opening(y, "cust_", "buy") + opening(y, "procust_", "buy")).sum())
        r["customer+pro opening sells"] = int((opening(y, "cust_", "sell") + opening(y, "procust_", "sell")).sum())
        if y.gam.notna().any():
            r["MM net gamma $M/1%"] = round(float((y["market maker"] * y.gam).sum() / 1e6), 2)
            r["customer+pro net gamma $M/1%"] = round(float(((y["customer"] + y["pro customer"]) * y.gam).sum() / 1e6), 2)
        rows.append(r)
    print(pd.DataFrame(rows).set_index("side").T.to_string())
    print("classic convention expects: customers net SELL calls (dealers long call gamma) and net BUY puts (dealers short put gamma)")
