"""Daily SPY 0DTE customer order flow (README.md, pre-registered at 4bbbd47), using spy-intraday-multiday's loader, parity spot and
signing (imported unchanged). Writes aggregates only (the minute data are licensed and stay in the private repo).
Usage: OMP_NUM_THREADS=1 python flows.py <etfs folder> [--days N]  -> out/daily_flow.csv"""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
SRC = Path("/home/user/spy-options-data/minute")
MULTI = HERE.parent / "2026-10-16-spy-intraday-multiday"
sys.path.insert(0, str(MULTI))
import multiday as M                               # noqa: E402  (original, imported unchanged; it imports td_gamma)

M.MIN = SRC
I0935, I1200, I1559 = M.MINUTES.index("09:35"), M.MINUTES.index("12:00"), M.MINUTES.index("15:59")


def spy_close(etfs):
    d = json.loads((Path(etfs) / "SPY.json").read_text())["chart"]["result"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None)
    s = pd.Series(d["indicators"]["quote"][0]["close"], index=idx, dtype=float).dropna()
    return s[~s.index.duplicated(keep="last")].sort_index()


def day(args):
    d, s0 = args
    try:
        piv, strikes, call, cols = M.load_day(d)
    except Exception:
        return None
    bid, ask = piv["bid"].to_numpy(), piv["ask"].to_numpy()
    ok = (bid > 0) & (ask > 0)
    mid = np.where(ok, (bid + ask) / 2, np.nan)
    half = np.where(ok, (ask - bid) / 2, np.nan)
    if np.isfinite(mid[350:]).sum() < 50 or not np.isfinite(s0):
        return None
    S = M.parity_spot(mid, strikes, call, s0)
    vol, vwap = piv["volume"].to_numpy(), piv["vwap"].to_numpy()
    # Amendment 1: a quote row stamped t is the END of minute t, so the trade minute spans rows t-1 (start) and t (end)
    mid_avg = np.nanmean(np.stack([mid, np.vstack([mid[:1], mid[:-1]])]), axis=0)
    half_avg = np.nanmean(np.stack([half, np.vstack([half[:1], half[:-1]])]), axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        s = np.clip((vwap - mid_avg) / half_avg, -1, 1)
    s = np.where((vol > 0) & np.isfinite(s) & (half_avg > 0), s, 0.0)
    n = len(M.MINUTES)
    Tm = np.array([(n - i - 1) / M.YEAR for i in range(n)]).clip(min=1 / M.YEAR)
    Smat = np.repeat(S[:, None], len(cols), axis=1)
    Kmat = np.repeat(strikes[None, :], n, axis=0)
    Tmat = np.repeat(Tm[:, None], len(cols), axis=1)
    Cmat = np.repeat(call[None, :], n, axis=0)
    has = np.isfinite(mid) & (mid > 0) & np.isfinite(Smat)
    ivm = np.full(mid.shape, np.nan)
    if has.any():
        ivm[has] = M.t.implied_vol(mid[has], Smat[has], Kmat[has], Tmat[has], Cmat[has])
    good = np.isfinite(ivm) & (ivm > 0.01) & (ivm < 3)
    iv = np.where(good, ivm, 0.2)
    delta = np.where(good, M.bs_delta(Smat, Kmat, Tmat, iv, Cmat), 0.0)
    gam = np.where(good, M.gamma(Smat, Kmat, Tmat, iv), 0.0)
    sv = s * np.nan_to_num(vol)
    F = (sv * delta * 100).sum(axis=1)
    Gm = (sv * gam * 100).sum(axis=1)
    callsv, putsv = sv[:, call].sum(axis=1), sv[:, ~call].sum(axis=1)
    seg = lambda x, a, b: float(np.nansum(x[a:b]))
    return {"date": d, "s0935": float(S[I0935]), "s1200": float(S[I1200]), "s1559": float(S[I1559]),
            "F_am": seg(F, 0, I1200), "F_pm": seg(F, I1200, n), "F_day": seg(F, 0, n), "G_am": seg(Gm, 0, I1200), "G_day": seg(Gm, 0, n),
            "call_signed_am": seg(callsv, 0, I1200), "put_signed_am": seg(putsv, 0, I1200), "call_signed_day": seg(callsv, 0, n), "put_signed_day": seg(putsv, 0, n),
            "volume_day": float(np.nansum(vol))}


def main(etfs, ndays=None):
    OUT.mkdir(exist_ok=True)
    files = sorted(SRC.glob("*.csv.gz"))
    if ndays:
        files = files[-ndays:]
    spy = spy_close(etfs)
    args = []
    for f in files:
        d = pd.Timestamp(f.name[:8])
        prev = spy[spy.index < d]
        args.append((d, float(prev.iloc[-1]) if len(prev) else np.nan))
    with Pool(4) as p:
        rows = [r for r in p.imap(day, args, chunksize=4) if r]
    D = pd.DataFrame(rows).set_index("date").sort_index()
    D.to_csv(OUT / ("daily_flow.csv" if not ndays else "daily_flow_smoke.csv"))
    return D


if __name__ == "__main__":
    nd = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else None
    D = main(sys.argv[1], nd)
    print(len(D)); print(D.tail(5).round(2).to_string())
