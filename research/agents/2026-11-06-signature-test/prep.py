"""Prep only (no outcomes by class): rebuild the aftershock study's shock set and check the published 54 / 28."""
import importlib.util, json, numpy as np, pandas as pd
from pathlib import Path
H = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
(H / "data").mkdir(exist_ok=True)
SYMS = {"S&P 500": ("^GSPC", "1950-01-01"), "Nasdaq-100": ("^NDX", "1985-10-01"), "SOX": ("^SOX", "1994-05-01")}

def load(nm):
    sym, st = SYMS[nm]; f = H / "data" / f"{sym.strip('^')}.csv"
    if f.exists(): return pd.read_csv(f, index_col=0, parse_dates=True)["close"]
    s = lc.yahoo(sym, st).close.dropna(); s = s[s > 0]; s.to_frame("close").to_csv(f); return s

def shocks(close, mult=6, iso=21):
    r = np.log(close).diff().dropna(); sc = r.abs().rolling(1260, min_periods=1260).median().shift(1)
    ok = sc.notna(); r, sc = r[ok], sc[ok]; big = (r.abs() >= mult * sc).values; down = ((r <= -mult * sc)).values
    out = [i for i in np.where(down)[0] if not big[max(0, i - iso):i].any()]
    return r, sc, out

def new_leg(close, r, i, horizon):
    c = close.reindex(r.index).values; low = c[i:i + 6].min(); later = c[i + 6:i + 6 + horizon]
    return bool((later < 0.98 * low).any()) if len(later) == horizon else None

if __name__ == "__main__":
    rep = {}
    for nm in SYMS:
        close = load(nm); r, sc, sh = shocks(close)
        # sanity: flag absurd daily moves (Yahoo errors seen before)
        bad = r[r.abs() > 0.25]
        rep[nm] = {"first/last": [str(r.index[0].date()), str(r.index[-1].date())], "n down shocks (6x, iso 21)": len(sh),
                   "days |r|>25%": [f"{d.date()} {v:+.3f}" for d, v in bad.items()],
                   "last 3 shocks": [f"{r.index[i].date()} {r.iloc[i]:+.4f} ({r.iloc[i] / -sc.iloc[i]:.1f}x)" for i in sh[-3:]]}
        if nm == "S&P 500":
            for hz in (84, 88, 63):
                legs = [new_leg(close, r, i, hz) for i in sh]; done = [x for x in legs if x is not None]
                rep[nm][f"new legs, horizon {hz} after day 5"] = f"{sum(done)} of {len(done)}"
    print(json.dumps(rep, indent=1))
