"""Features M0-M10 + minute anatomy per event from data/<sym>_<date>_{trades,mbp10,imb}.parquet (pre-registered metrics).
Times are seconds after midnight ET (numeric, for speed); events run in parallel. Usage: python features.py -> out/features.csv, out/anatomy.csv"""
from multiprocessing import Pool
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; D = HERE / "data"
ET = "America/New_York"
H = lambda hm: int(hm[:2]) * 3600 + int(hm[3:5]) * 60          # "09:30" -> seconds after midnight
O, F5, END = H("09:30"), H("09:35"), H("10:30")


def secs(ts, day):
    mid = pd.Timestamp(f"{day.date()} 00:00", tz=ET).value
    return (pd.to_datetime(ts, utc=True).values.astype("int64") - mid) / 1e9


def feats(r):
    tag = f"{r.sym}_{r.date:%Y%m%d}"; out = {"sym": r.sym, "date": r.date, "cls": r.cls, "scope": r.scope if isinstance(r.scope, str) else "",
                                             "sig": r.sig, "gap_sig": r.gap / r.sig, "r2": r.r2}
    ft = D / f"{tag}_trades.parquet"
    if not ft.exists(): return None, None
    t = pd.read_parquet(ft, columns=["ts_event", "price", "size", "side"]); t = t[t["size"] > 0]
    sec = secs(t.ts_event, r.date); px = t.price.to_numpy(float); sz = t["size"].to_numpy(np.int64)
    s = np.where(t.side.to_numpy() == "B", 1, np.where(t.side.to_numpy() == "A", -1, 0))
    pm, rth = sec < O, sec >= O
    if rth.sum() < 50: return None, None
    o = px[rth][0]; out["open_px"] = o
    if pm.sum() > 20:
        ppx = px[pm]; k = int(np.argmax(ppx))
        out["pm_high"] = float(ppx[k]); out["pm_high_min_after_4am"] = (sec[pm][k] - H("04:00")) / 60
        out["M1 premarket drift (last vs high, sig)"] = (ppx[-1] / ppx.max() - 1) / r.sig
        bv, sv = sz[pm & (s > 0)].sum(), sz[pm & (s < 0)].sum()
        out["M2a premarket buy share"] = bv / (bv + sv) if bv + sv else np.nan
        out["M2b premarket retail-size share"] = sz[pm & (sz < 100)].sum() / sz[pm].sum()
        out["premarket volume"] = int(sz[pm].sum())
    f5 = rth & (sec < F5)
    bv, sv = sz[f5 & (s > 0)].sum(), sz[f5 & (s < 0)].sum()
    p935 = px[f5][-1]; last = px[rth & (sec < END)][-1]
    out["M6 first-5m delta %"] = 100 * (bv - sv) / (bv + sv) if bv + sv else np.nan
    out["M8 first-5m progress per 1k bought (sig)"] = ((p935 / o - 1) / r.sig) / (bv / 1000) if bv else np.nan
    out["M10 first-5m retail-size share"] = sz[f5 & (sz < 100)].sum() / sz[f5].sum()
    out["first-5m volume"] = int(sz[f5].sum())
    out["ret 09:35->10:30 (sig)"] = (last / p935 - 1) / r.sig
    out["ret 09:30->09:35 (sig)"] = (p935 / o - 1) / r.sig
    fi = D / f"{tag}_imb.parquet"
    if fi.exists():
        im = pd.read_parquet(fi); im["sec"] = secs(im.ts_event, r.date)
        im = im[(im.auction_type == "O") & (im.sec < O)]
        if len(im):
            z = im.iloc[-1]; sgn = 1 if z.side == "B" else (-1 if z.side == "A" else 0)
            out["M3 opening imbalance / paired"] = sgn * float(z.total_imbalance_qty) / max(float(z.paired_qty), 1.0)
            out["opening paired shares"] = float(z.paired_qty)
            w = im[im.sec >= H("09:25")]   # exploratory (not pre-registered): the last messages are often balanced
            sg = w.side.map({"B": 1, "A": -1}).fillna(0)
            out["M3x mean imbalance 09:25-09:30 / paired (exploratory)"] = float((sg * w.total_imbalance_qty / w.paired_qty.clip(lower=1)).mean()) if len(w) else np.nan
    mb = None
    fb = D / f"{tag}_mbp10.parquet"
    if fb.exists():
        cols = ["ts_event"] + [f"{a}_{b}_{i:02d}" for a in ("bid", "ask") for b in ("px", "sz") for i in range(10)]
        b = pd.read_parquet(fb, columns=cols); bsec = secs(b.ts_event, r.date); keep = bsec >= O
        if keep.sum() > 100:
            bsec = bsec[keep]
            bp = b[[f"bid_px_{i:02d}" for i in range(10)]].to_numpy(float)[keep]; ap = b[[f"ask_px_{i:02d}" for i in range(10)]].to_numpy(float)[keep]
            bs = b[[f"bid_sz_{i:02d}" for i in range(10)]].to_numpy(float)[keep]; a_s = b[[f"ask_sz_{i:02d}" for i in range(10)]].to_numpy(float)[keep]
            del b
            mid = (bp[:, 0] + ap[:, 0]) / 2; ok = (bp[:, 0] > 0) & (ap[:, 0] > bp[:, 0])
            bd = np.where(bp >= (mid * 0.995)[:, None], bs, 0).sum(1); ad = np.where((ap <= (mid * 1.005)[:, None]) & (ap > 0), a_s, 0).sum(1)
            spr = 1e4 * (ap[:, 0] - bp[:, 0]) / np.where(mid > 0, mid, np.nan)
            isec = np.floor(bsec[ok]).astype(int); vals = np.c_[mid[ok], spr[ok], bd[ok], ad[ok]]
            # last book state in each second, forward-filled onto a 1-second grid
            last_idx = len(isec) - 1 - np.unique(isec[::-1], return_index=True)[1]; u = isec[last_idx]
            grid = np.arange(O, u.max() + 1); pos = np.searchsorted(u, grid, side="right") - 1
            g = pd.DataFrame(vals[last_idx][np.clip(pos, 0, None)], columns=["mid", "spr_bp", "bid_d", "ask_d"]); g["sec"] = grid; g = g[pos >= 0]
            w5 = g[g.sec < F5]
            out["M7 first-5m book imbalance"] = float(((w5.bid_d - w5.ask_d) / (w5.bid_d + w5.ask_d)).mean())
            out["M7b first-5m ask depth $"] = float((w5.ask_d * w5.mid).mean()); out["M7c first-5m bid depth $"] = float((w5.bid_d * w5.mid).mean())
            out["M9 first-5m spread bp"] = float(w5.spr_bp.median())
            g["m"] = ((g.sec - O) // 60).astype(int)
            mb = g.groupby("m")[["spr_bp", "bid_d", "ask_d"]].mean(); mb["imb"] = (mb.bid_d - mb.ask_d) / (mb.bid_d + mb.ask_d)
    m = np.floor((sec - O) / 60).astype(int)
    an = pd.DataFrame({"m": m, "px": px, "vol": sz, "sv": sz * s}).groupby("m").agg(px=("px", "last"), vol=("vol", "sum"), delta=("sv", "sum"))
    an["ret_sig"] = (an.px / o - 1) / r.sig
    if mb is not None: an = an.join(mb, how="left")
    an = an.reset_index().rename(columns={"m": "min_from_open"}).assign(sym=r.sym, date=r.date, cls=r.cls, scope=out["scope"])
    return out, an


def safe(d):
    r = SimpleNamespace(**d)
    try:
        return feats(r)
    except Exception as e:
        print("feat err", r.sym, r.date.date(), str(e)[:100], flush=True); return None, None


if __name__ == "__main__":
    smp = pd.read_csv(HERE / "out" / "sample.csv", parse_dates=["date"])
    with Pool(3) as p:
        res = p.map(safe, smp.to_dict(orient="records"), chunksize=4)
    rows = [f for f, a in res if f]; ans = [a for f, a in res if f]
    F = pd.DataFrame(rows); F.to_csv(HERE / "out" / "features.csv", index=False)
    pd.concat(ans).to_csv(HERE / "out" / "anatomy.csv", index=False)
    print(F.groupby("cls").size().to_dict(), "features rows", len(F))
