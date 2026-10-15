"""Turn the raw downloads into two monthly tables, each row stamped with what was KNOWN at that month-end.

  data/monthly_prices.pkl   one row per (symbol, month): high, low, close, adjclose, volume, partial flag
  out/macro_monthly.csv     one row per month: macro and positioning series, publication lags applied
  out/inventory_gap.csv     per stock and month: inventory growth minus revenue growth (SEC, by filing date)
  out/data_coverage.csv     first/last month and data-quality flags per series

Publication lags (value usable at the close of month t):
  fed funds, 10y, 3m (H.15 monthly averages)   month t
  CPI (BLS)                                    month t-1   (CPI for t comes out mid t+1)
  M2 (H.6)                                     month t-1
  FINRA margin debt                            month t-1   (published about 3 weeks after month end)
  Fed balance sheet, TGA, reverse repo (H.4.1) last Wednesday at least 2 days before month end
  prices, VIX, dollar, TIPS yields, S&P GEX    month t (end-of-month value; GEX is the month's mean)
  SEC inventory and revenue                    the filing date of the 10-Q/10-K that reported them
"""
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA, OUT = HERE / "data", HERE / "out"


# ---------------------------------------------------------------- prices
def load_yahoo(sym):
    d = json.loads((DATA / "yahoo" / f"{sym}.json").read_text())["chart"]["result"][0]
    q = d["indicators"]["quote"][0]
    adj = d["indicators"].get("adjclose", [{}])[0].get("adjclose", q["close"])
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York")
    df = pd.DataFrame({"open": q["open"], "high": q["high"], "low": q["low"], "close": q["close"],
                       "adjclose": adj, "volume": q["volume"]}, index=idx.normalize().tz_localize(None))
    df = df[~df.index.duplicated(keep="last")].dropna(subset=["close"])
    df = df[(df.close > 0)]
    # a missing or zero high/low (old Yahoo rows) falls back to the close
    for c in ("high", "low"):
        df[c] = df[c].where(df[c] > 0, df.close)
    df["high"] = df[["high", "close"]].max(axis=1)
    df["low"] = df[["low", "close"]].min(axis=1)
    return df


def to_monthly(df, today):
    m = df.resample("ME").agg({"high": "max", "low": "min", "close": "last", "adjclose": "last",
                               "volume": "sum"}).dropna(subset=["close"])
    m["partial"] = m.index > today          # the current, unfinished month
    m["last_day"] = df["close"].resample("ME").apply(lambda s: s.index[-1]).reindex(m.index)
    return m


# ---------------------------------------------------------------- Fed SDMX
def fed_series(rel, names):
    out = {n: {} for n in names}
    with zipfile.ZipFile(DATA / "fed" / f"{rel}.zip") as z, z.open(f"{rel}_data.xml") as f:
        cur = None
        for ev, el in ET.iterparse(f, events=("start", "end")):
            tag = el.tag.rsplit("}", 1)[-1]
            if ev == "start" and tag == "Series":
                cur = el.get("SERIES_NAME") if el.get("SERIES_NAME") in out else None
            elif ev == "end" and tag == "Obs":
                if cur is not None:
                    v = el.get("OBS_VALUE")
                    if v not in (None, "ND", "NA", ""):
                        out[cur][el.get("TIME_PERIOD")] = float(v)
                el.clear()
            elif ev == "end" and tag == "Series":
                el.clear()
    res = {}
    for n, d in out.items():
        s = pd.Series(d, dtype=float)
        s.index = pd.to_datetime(s.index)
        res[n] = s.sort_index()
    return res


def month_end(s):
    s = s.copy()
    s.index = s.index + pd.offsets.MonthEnd(0)
    return s[~s.index.duplicated(keep="last")]


# ---------------------------------------------------------------- macro
def build_macro(today):
    h15 = fed_series("H15", ["RIFSPFF_N.M", "RIFLGFCY10_N.M", "RIFLGFCM03_N.M"])
    h6 = fed_series("H6", ["M2.M"])
    h41 = fed_series("H41", ["RESPPMA_N.WW", "RESPPLLDT_N.WW", "RESPPLLRD_N.WW"])

    cpi = {}
    for f in sorted((DATA / "bls").glob("cpi_*.json")):
        for r in json.loads(f.read_text())["Results"]["series"][0]["data"]:
            if r["period"].startswith("M") and r["period"] != "M13":
                v = float(r["value"]) if r["value"] not in ("-", "") else np.nan
                cpi[pd.Timestamp(f"{r['year']}-{r['period'][1:]}-01") + pd.offsets.MonthEnd(0)] = v
    # Oct 2025 was never published (2025 funding lapse): fill single gaps geometrically
    cpi = np.exp(np.log(pd.Series(cpi).sort_index()).interpolate(limit=1))

    idx = pd.date_range("1980-01-31", pd.Timestamp(today) + pd.offsets.MonthEnd(0), freq="ME")
    m = pd.DataFrame(index=idx)
    m["ff"] = month_end(h15["RIFSPFF_N.M"])
    m["gs10"] = month_end(h15["RIFLGFCY10_N.M"])
    m["gs3m"] = month_end(h15["RIFLGFCM03_N.M"])
    m["cpi_yoy"] = (100 * np.log(cpi / cpi.shift(12))).reindex(idx).shift(1)     # known one month later
    m["real10"] = m.gs10 - m.cpi_yoy
    m["curve"] = m.gs10 - m.gs3m
    m["m2_yoy"] = (100 * np.log(h6["M2.M"] / h6["M2.M"].shift(12))).pipe(month_end).reindex(idx).shift(1)

    # Fed net liquidity = total assets - Treasury General Account - reverse repo (others), $bn
    w = pd.DataFrame({"assets": h41["RESPPMA_N.WW"], "tga": h41["RESPPLLDT_N.WW"],
                      "rrp": h41["RESPPLLRD_N.WW"]}).dropna()
    netliq = (w.assets - w.tga - w.rrp) / 1000
    m["netliq"] = [netliq[netliq.index <= d - pd.Timedelta(days=2)].iloc[-1]
                   if (netliq.index <= d - pd.Timedelta(days=2)).any() else np.nan for d in idx]
    m.loc[m.index < netliq.index[0] + pd.offsets.MonthEnd(0), "netliq"] = np.nan

    fin = pd.read_excel(DATA / "finra_margin.xlsx")
    fin = fin.rename(columns={fin.columns[0]: "ym", fin.columns[1]: "debit"})
    fin["d"] = pd.to_datetime(fin.ym.astype(str)) + pd.offsets.MonthEnd(0)
    debit = fin.set_index("d").debit.astype(float).sort_index()
    m["margin_yoy"] = (100 * np.log(debit / debit.shift(12))).reindex(idx).shift(1)

    tips = pd.concat([pd.read_csv(f, parse_dates=["Date"]) for f in sorted((DATA / "treasury_real").glob("*.csv"))])
    tips = tips.set_index("Date")["10 YR"].astype(float).sort_index()
    m["tips10"] = tips.resample("ME").last()

    def yclose(sym):
        return load_yahoo(sym).adjclose.resample("ME").last()

    m["dxy"] = yclose("DX-Y.NYB")
    m["vix"] = yclose("^VIX")
    hyg, ief = yclose("HYG"), yclose("IEF")
    m["hyg_ief_6m"] = 100 * (np.log(hyg / hyg.shift(6)) - np.log(ief / ief.shift(6)))
    m["btc"] = yclose("BTC-USD")

    dix = pd.read_csv(DATA / "DIX.csv", parse_dates=["date"]).set_index("date")
    m["gex_bn"] = dix.gex.resample("ME").mean() / 1e9
    m["dix"] = dix.dix.resample("ME").mean()
    m.index.name = "month"
    return m


# ---------------------------------------------------------------- SEC inventory vs revenue
REV_CONCEPTS = ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet",
                "SalesRevenueGoodsNet", "RevenueFromContractWithCustomerIncludingAssessedTax"]


def _first_filed(rows):
    """Point-in-time: for each period keep the value as first reported, with that filing date."""
    df = pd.DataFrame(rows)
    df = df[df.form.isin(["10-Q", "10-K", "10-Q/A", "10-K/A", "10-KT"])]
    if df.empty:
        return df
    df["end"] = pd.to_datetime(df["end"])
    df["filed"] = pd.to_datetime(df["filed"])
    if "start" in df:
        df["start"] = pd.to_datetime(df["start"])
    keys = ["start", "end"] if "start" in df else ["end"]
    return df.sort_values("filed").drop_duplicates(keys, keep="first")


def inventory_gap(sym):
    f = DATA / "sec" / f"{sym}.json"
    if not f.exists():
        return None, None
    d = json.loads(f.read_text())
    gaap = d["facts"].get("us-gaap", {})
    if "InventoryNet" not in gaap:
        return None, d.get("entityName")
    inv = _first_filed(gaap["InventoryNet"]["units"]["USD"])
    rev = []
    for c in REV_CONCEPTS:          # for the same period, whichever concept was FILED first wins (point-in-time):
                                    # the ASC 606 concept re-reports old periods years later as comparatives
        if c in gaap and "USD" in gaap[c]["units"]:
            r = _first_filed(gaap[c]["units"]["USD"])
            if not r.empty and "start" in r:
                r["prio"] = REV_CONCEPTS.index(c)
                rev.append(r)
    if inv.empty or not rev:
        return None, d.get("entityName")
    rev = pd.concat(rev).sort_values(["filed", "prio"]).drop_duplicates(["start", "end"], keep="first")
    rev["days"] = (rev.end - rev.start).dt.days
    q = rev[rev.days.between(80, 100)][["start", "end", "val", "filed"]]
    a = rev[rev.days.between(350, 380)][["start", "end", "val", "filed"]]
    # Q4 = fiscal year minus the three quarters inside it (known when the 10-K is filed)
    q4 = []
    for _, y in a.iterrows():
        inside = q[(q.start >= y.start - pd.Timedelta(days=5)) & (q.end <= y.end - pd.Timedelta(days=60))]
        if len(inside) == 3 and not (abs((q.end - y.end).dt.days) <= 5).any():
            q4.append({"start": inside.end.max() + pd.Timedelta(days=1), "end": y.end,
                       "val": y.val - inside.val.sum(), "filed": max(y.filed, inside.filed.max())})
    q = pd.concat([q, pd.DataFrame(q4)]).sort_values("end").drop_duplicates("end", keep="first")
    q = q.reset_index(drop=True)
    rows = []
    for i in range(len(q)):
        last4 = q.iloc[max(0, i - 3):i + 1]
        if len(last4) < 4 or (last4.end.iloc[-1] - last4.end.iloc[0]).days > 300:
            continue
        ttm, filed_ttm = last4.val.sum(), last4.filed.max()
        e = q.end.iloc[i]
        iv = inv[(inv.end - e).abs().dt.days <= 5]
        if iv.empty:
            continue
        rows.append({"end": e, "ttm_rev": ttm, "inv": iv.val.iloc[0],
                     "known": max(filed_ttm, iv.filed.iloc[0])})
    g = pd.DataFrame(rows)
    if len(g) < 5:
        return None, d.get("entityName")
    out = []
    for i, r in g.iterrows():
        prev = g[(r.end - g.end).dt.days.between(345, 385)]
        if prev.empty or prev.inv.iloc[0] <= 0 or r.inv <= 0 or prev.ttm_rev.iloc[0] <= 0 or r.ttm_rev <= 0:
            continue
        p = prev.iloc[0]
        out.append({"end": r.end, "known": max(r.known, p.known),
                    "inv_yoy": 100 * np.log(r.inv / p.inv), "rev_yoy": 100 * np.log(r.ttm_rev / p.ttm_rev),
                    "inv_to_rev": r.inv / r.ttm_rev})
    out = pd.DataFrame(out)
    out["inv_gap"] = out.inv_yoy - out.rev_yoy
    return out, d.get("entityName")


def main():
    from fetch_data import STOCKS, INDICES
    today = max(load_yahoo(s).index[-1] for s in ("NVDA", "^GSPC"))
    OUT.mkdir(exist_ok=True)

    frames, cov = [], []
    for s in STOCKS + INDICES:
        if not (DATA / "yahoo" / f"{s}.json").exists():
            cov.append({"series": s, "note": "no data"})
            continue
        d = load_yahoo(s)
        mo = to_monthly(d, today)
        r = np.log(mo.close).diff()
        cov.append({"series": s, "first": d.index[0].date(), "last": d.index[-1].date(), "months": len(mo),
                    "max_abs_monthly_logret": round(float(r.abs().max()), 3),
                    "months_abs_logret_gt_0.7": int((r.abs() > 0.7).sum()),
                    "days_zero_range": int((d.high == d.low).sum())})
        mo["symbol"] = s
        frames.append(mo)
    prices = pd.concat(frames)
    prices.index.name = "month"
    prices.to_pickle(DATA / "monthly_prices.pkl")

    macro = build_macro(today)
    macro.to_csv(OUT / "macro_monthly.csv", float_format="%.4f")
    for c in macro.columns:
        s = macro[c].dropna()
        cov.append({"series": c, "first": s.index[0].date(), "last": s.index[-1].date(), "months": len(s)})

    gaps = []
    for s in STOCKS:
        g, name = inventory_gap(s)
        if g is None:
            cov.append({"series": f"sec:{s}", "note": f"no inventory gap ({name})"})
            continue
        g["symbol"] = s
        gaps.append(g)
        cov.append({"series": f"sec:{s}", "first": g.end.min().date(), "last": g.end.max().date(),
                    "months": len(g), "note": name})
    pd.concat(gaps).to_csv(OUT / "inventory_gap.csv", index=False, float_format="%.4f")
    pd.DataFrame(cov).to_csv(OUT / "data_coverage.csv", index=False)
    print("as of", today.date(), "| prices", prices.symbol.nunique(), "symbols |", "macro", macro.shape,
          "| inventory gap", len(gaps), "stocks")


if __name__ == "__main__":
    main()
