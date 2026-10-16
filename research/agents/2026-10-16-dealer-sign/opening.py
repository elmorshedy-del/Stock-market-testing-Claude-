import sys, pandas as pd
d = pd.read_csv(sys.argv[1], low_memory=False)
d["cp"] = d.call_or_put.str.upper().str[0]
for sym in sys.argv[2:]:
    x = d[d.underlying == sym]
    rows = []
    for who, pres in (("customer+pro", ("cust_", "procust_")), ("firm", ("firm_",)), ("broker-dealer", ("bd_",))):
        for cp in "CP":
            y = x[x.cp == cp]
            r = {"who": who, "side": "calls" if cp == "C" else "puts"}
            for act in ("open_buy", "open_sell", "close_buy", "close_sell"):
                r[act] = int(sum(y[[c for c in y.columns if c.startswith(p) and c.endswith(f"{act}_vol")]].sum().sum() for p in pres))
            r["new longs (open buy - close sell)"] = r["open_buy"] - r["close_sell"]
            r["new shorts (open sell - close buy)"] = r["open_sell"] - r["close_buy"]
            rows.append(r)
    print(f"\n{sym}\n", pd.DataFrame(rows).to_string(index=False))
