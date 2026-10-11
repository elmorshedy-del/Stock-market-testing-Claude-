"""Calibrate tick-based trade signing against Cboe Open-Close customer flow (REPORT 4r, item 3).

Inputs (kept outside the repo): Databento OPRA.PILLAR tcbbo files for one day,
<dir>/db_data/{TSLA,SPY}_tcbbo_YYYYMMDD.dbn.zst, and the Cboe Open-Close EOD CSV for the same day.
Requires `pip install databento` (Python >= 3.10); the API key is read from DATABENTO_API_KEY
only when downloading, never stored here.
Usage: python flow_calibration.py <dir> <cboe_eod.csv>
"""
import sys
import numpy as np
import pandas as pd
import databento as db

S, cboe_csv = sys.argv[1], sys.argv[2]
cb = pd.read_csv(cboe_csv)
out = []
for und in ("TSLA", "SPY"):
    t = db.DBNStore.from_file(f"{S}/db_data/{und}_tcbbo_20250328.dbn.zst").to_df()
    sym = t.symbol.str.split().str[-1]
    t["exp"] = pd.to_datetime("20" + sym.str[:6], format="%Y%m%d")
    t["cp"] = sym.str[6]
    t["K"] = sym.str[7:].astype(int) / 1000
    t = t.sort_values("ts_event")
    mid = (t.bid_px_00 + t.ask_px_00) / 2
    q = np.select([t.price >= t.ask_px_00, t.price <= t.bid_px_00, t.price > mid, t.price < mid], [1, -1, 1, -1], 0)
    q = np.where(t.bid_px_00.isna() | t.ask_px_00.isna(), 0, q)
    tick = np.sign(t.groupby("instrument_id").price.diff().fillna(0)).to_numpy()
    t["s_quote"] = q
    t["s_lr"] = np.where(q != 0, q, tick)                     # Lee-Ready style: quote rule, tick rule at the mid
    t["at_touch"] = (t.price >= t.ask_px_00) | (t.price <= t.bid_px_00)
    t["venue"] = np.where(t.publisher_id == 22, "XCBO", "other")
    t["big"] = t["size"] >= 50
    for v, g in (("XCBO", t[t.venue == "XCBO"]), ("ALL", t)):
        agg = g.assign(nq=g.s_quote * g["size"], nl=g.s_lr * g["size"], unsigned=(g.s_lr == 0) * g["size"]).groupby(
            ["exp", "cp", "K"]).agg(vol=("size", "sum"), net_quote=("nq", "sum"), net_lr=("nl", "sum"), unsigned=("unsigned", "sum"))
        agg.columns = [f"{c}_{v}" for c in agg.columns]
        out.append((und, v, agg))
    print(und, "trades", len(t), "XCBO share of volume %.1f%%" % (100 * t[t.venue == "XCBO"]["size"].sum() / t["size"].sum()),
          "| at-mid/unsigned by quote rule %.1f%%" % (100 * t[t.s_quote == 0]["size"].sum() / t["size"].sum()))

res = []
for und in ("TSLA", "SPY"):
    c = cb[cb.underlying_symbol == und].copy()
    c["exp"] = pd.to_datetime(c.expiration_date)
    c["K"], c["cp"] = c.strike_price, c.call_put_flag
    cols = c.columns
    pick = lambda pre, side: [x for x in cols if x.startswith(pre) and side in x and x.endswith("_vol")]
    cust_b = pick("cust_", "_buy") + pick("procust_", "_buy")
    cust_s = pick("cust_", "_sell") + pick("procust_", "_sell")
    pub_b = cust_b + pick("firm_", "_buy") + pick("bd_", "_buy")
    pub_s = cust_s + pick("firm_", "_sell") + pick("bd_", "_sell")
    c["cust_net"] = c[cust_b].sum(axis=1) - c[cust_s].sum(axis=1)
    c["public_net"] = c[pub_b].sum(axis=1) - c[pub_s].sum(axis=1)
    c["mm_net"] = c.mm_buy_vol - c.mm_sell_vol
    c["oi_chg"] = c.open_interest - c.previous_open_interest
    c = c.set_index(["exp", "cp", "K"])
    for u, v, agg in out:
        if u == und:
            c = c.join(agg, how="left")
    c = c.fillna(0)
    c["und"] = und
    res.append(c.reset_index())
r = pd.concat(res)
r.to_csv(f"{S}/calib_series.csv", index=False)
for und, c in r.groupby("und"):
    c = c[c.total_exchange_vol > 0]
    print(f"\n{und}: {len(c)} sampled series traded on Cboe; Cboe-reported volume {c.total_exchange_vol.sum():,.0f} vs Databento XCBO volume {c.vol_XCBO.sum():,.0f}")
    for lab, y in (("customer net", "cust_net"), ("all non-MM net", "public_net")):
        for x in ("net_quote_XCBO", "net_lr_XCBO", "net_lr_ALL"):
            w = c[y].abs() + c[x].abs()
            agree = ((np.sign(c[x]) == np.sign(c[y])) * w).sum() / w.sum()
            print(f"   {lab:15s} vs {x:15s}: corr {c[x].corr(c[y]):+.2f}, rank corr {c[x].rank().corr(c[y].rank()):+.2f}, "
                  f"volume-weighted sign agreement {agree:.0%}")
    for cp, g in c.groupby("cp"):
        print(f"   {cp}: Cboe customer net {g.cust_net.sum():+,.0f} | non-MM net {g.public_net.sum():+,.0f} | MM net {g.mm_net.sum():+,.0f} || "
              f"rebuilt XCBO net {g.net_lr_XCBO.sum():+,.0f} | rebuilt all-venue net {g.net_lr_ALL.sum():+,.0f} (vol {g.vol_ALL.sum():,.0f})")

for und, c in r.groupby("und"):
    c = c[c.total_exchange_vol > 0]
    allb = [x for x in c.columns if x.endswith("_buy_vol")]
    alls = [x for x in c.columns if x.endswith("_sell_vol")]
    print(f"\n{und}: Cboe sum of buy vols {c[allb].sum().sum():,.0f}, sell vols {c[alls].sum().sum():,.0f}, total_exchange_vol {c.total_exchange_vol.sum():,.0f}, Databento XCBO {c.vol_XCBO.sum():,.0f}, all venues {c.vol_ALL.sum():,.0f}, total_industry_vol {c.total_industry_vol.sum():,.0f}")
    print((c.vol_XCBO / c.total_exchange_vol).describe().round(2).to_dict())
