"""Features M0-M10 + minute anatomy per event from data/<sym>_<date>_{trades,mbp10,imb}.parquet (pre-registered metrics).
Usage: python features.py  -> out/features.csv, out/anatomy.csv"""
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; D = HERE / "data"
smp = pd.read_csv(HERE / "out" / "sample.csv", parse_dates=["date"])
ET = "America/New_York"


def feats(r):
    tag = f"{r.sym}_{r.date:%Y%m%d}"; out = {"sym": r.sym, "date": r.date, "cls": r.cls, "scope": getattr(r, "scope", ""), "sig": r.sig, "gap_sig": r.gap / r.sig, "r2": r.r2}
    ft = D / f"{tag}_trades.parquet"
    if not ft.exists(): return None, None
    t = pd.read_parquet(ft); t = t[t["size"] > 0].copy()
    t["et"] = t.ts_event.dt.tz_convert(ET); t["hm"] = t.et.dt.strftime("%H:%M:%S")
    t["s"] = np.where(t.side == "B", 1, np.where(t.side == "A", -1, 0)); t["size"] = t["size"].astype(np.int64)
    pm = t[t.hm < "09:30:00"]; rth = t[t.hm >= "09:30:00"]
    if len(rth) < 50: return None, None
    o = float(rth.price.iloc[0]); out["open_px"] = o
    if len(pm) > 20:
        out["pm_high"] = float(pm.price.max()); out["pm_high_min_after_4am"] = (pm.loc[pm.price.idxmax(), "et"] - pm.et.iloc[0].normalize() - pd.Timedelta("4h")).total_seconds() / 60
        out["M1 premarket drift (last vs high, sig)"] = (pm.price.iloc[-1] / pm.price.max() - 1) / r.sig
        bv, sv = pm["size"][pm.s > 0].sum(), pm["size"][pm.s < 0].sum()
        out["M2a premarket buy share"] = bv / (bv + sv) if bv + sv else np.nan
        out["M2b premarket retail-size share"] = pm["size"][pm["size"] < 100].sum() / pm["size"].sum()
        out["premarket volume"] = int(pm["size"].sum())
    f5 = rth[rth.hm < "09:35:00"]
    bv, sv = f5["size"][f5.s > 0].sum(), f5["size"][f5.s < 0].sum()
    out["M6 first-5m delta %"] = 100 * (bv - sv) / (bv + sv) if bv + sv else np.nan
    out["M8 first-5m progress per 1k bought (sig)"] = ((f5.price.iloc[-1] / o - 1) / r.sig) / (bv / 1000) if bv else np.nan
    out["M10 first-5m retail-size share"] = f5["size"][f5["size"] < 100].sum() / f5["size"].sum()
    out["first-5m volume"] = int(f5["size"].sum())
    p935 = float(f5.price.iloc[-1]); last = rth[rth.hm < "10:30:00"].price.iloc[-1]
    out["ret 09:35->10:30 (sig)"] = (last / p935 - 1) / r.sig
    out["ret 09:30->09:35 (sig)"] = (p935 / o - 1) / r.sig
    # imbalance
    fi = D / f"{tag}_imb.parquet"
    if fi.exists():
        im = pd.read_parquet(fi); im["et"] = im.ts_event.dt.tz_convert(ET)
        im = im[(im.auction_type == "O") & (im.et.dt.strftime("%H:%M:%S") < "09:30:00")]
        if len(im):
            z = im.iloc[-1]; sgn = 1 if z.side == "B" else (-1 if z.side == "A" else 0)
            out["M3 opening imbalance / paired"] = sgn * float(z.total_imbalance_qty) / max(float(z.paired_qty), 1.0)
            out["opening paired shares"] = float(z.paired_qty)
            w = im[im.et.dt.strftime("%H:%M:%S") >= "09:25:00"]   # exploratory (not pre-registered): the last messages are often balanced
            sg = w.side.map({"B": 1, "A": -1}).fillna(0)
            out["M3x mean imbalance 09:25-09:30 / paired (exploratory)"] = float((sg * w.total_imbalance_qty / w.paired_qty.clip(lower=1)).mean()) if len(w) else np.nan
    # book
    fb = D / f"{tag}_mbp10.parquet"
    if fb.exists():
        b = pd.read_parquet(fb); b["et"] = b.ts_event.dt.tz_convert(ET)
        b = b[b.et.dt.strftime("%H:%M:%S") >= "09:30:00"].set_index("et")
        if len(b) > 100:
            bp = b[[f"bid_px_{i:02d}" for i in range(10)]].to_numpy(float); ap = b[[f"ask_px_{i:02d}" for i in range(10)]].to_numpy(float)
            bs = b[[f"bid_sz_{i:02d}" for i in range(10)]].to_numpy(float); a_s = b[[f"ask_sz_{i:02d}" for i in range(10)]].to_numpy(float)
            mid = (bp[:, 0] + ap[:, 0]) / 2
            ok = (bp[:, 0] > 0) & (ap[:, 0] > bp[:, 0])
            bd = np.where(bp >= (mid * 0.995)[:, None], bs, 0).sum(1); ad = np.where((ap <= (mid * 1.005)[:, None]) & (ap > 0), a_s, 0).sum(1)
            bk = pd.DataFrame({"mid": mid, "spr_bp": 1e4 * (ap[:, 0] - bp[:, 0]) / mid, "bid_d": bd, "ask_d": ad}, index=b.index)[ok]
            bk = bk.resample("1s").last().ffill()
            w5 = bk[bk.index.strftime("%H:%M:%S") < "09:35:00"]
            out["M7 first-5m book imbalance"] = float(((w5.bid_d - w5.ask_d) / (w5.bid_d + w5.ask_d)).mean())
            out["M7b first-5m ask depth $"] = float((w5.ask_d * w5.mid).mean()); out["M7c first-5m bid depth $"] = float((w5.bid_d * w5.mid).mean())
            out["M9 first-5m spread bp"] = float(w5.spr_bp.median())
            mb = bk.resample("1min").mean(); mb["imb"] = (mb.bid_d - mb.ask_d) / (mb.bid_d + mb.ask_d)
        else:
            mb = None
    else:
        mb = None
    # anatomy per minute
    t["m"] = t.et.dt.floor("1min")
    an = t.groupby("m").agg(px=("price", "last"), vol=("size", "sum"), delta=("size", lambda x: 0))
    an["delta"] = t.assign(sv=t["size"] * t.s).groupby("m").sv.sum()
    an["ret_sig"] = (an.px / o - 1) / r.sig
    an["min_from_open"] = ((an.index - an.index[0].normalize() - pd.Timedelta("9h30min")).total_seconds() / 60).astype(int)
    if mb is not None:
        an = an.join(mb[["spr_bp", "imb", "bid_d", "ask_d"]], how="left")
    an = an.reset_index(drop=True).assign(sym=r.sym, date=r.date, cls=r.cls, scope=out["scope"])
    return out, an


rows, ans = [], []
for r in smp.itertuples():
    try:
        f, a = feats(r)
    except Exception as e:
        print("feat err", r.sym, r.date.date(), str(e)[:100]); continue
    if f: rows.append(f); ans.append(a)
F = pd.DataFrame(rows); F.to_csv(HERE / "out" / "features.csv", index=False)
pd.concat(ans).to_csv(HERE / "out" / "anatomy.csv", index=False)
print(F.groupby("cls").size().to_dict(), "features rows", len(F))
