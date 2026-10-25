"""Diagnostic after Amendment 1 (A1 still -0.82): does the minute-level trade sign agree with the option's OWN price move in that minute?
Genuine buy pressure lifts the price, so corr(sign, own mid change) should be > 0. Option prices only, no SPY returns.
Usage: python sign_check.py  -> out/sign_check.json"""
import json

import numpy as np
import pandas as pd

import flows as Fl


def main():
    files = sorted(Fl.SRC.glob("*.csv.gz"))[::24]
    out = {"centred (t-1,t) [Amendment 1]": [], "forward (t,t+1) [run 0]": []}
    for f in files:
        piv, strikes, call, cols = Fl.M.load_day(pd.Timestamp(f.name[:8]))
        bid, ask, vol, vwap = (piv[k].to_numpy() for k in ("bid", "ask", "volume", "vwap"))
        ok = (bid > 0) & (ask > 0)
        mid = np.where(ok, (bid + ask) / 2, np.nan)
        half = np.where(ok, (ask - bid) / 2, np.nan)
        prev = np.vstack([np.full((1, mid.shape[1]), np.nan), mid[:-1]])
        nxt = np.vstack([mid[1:], np.full((1, mid.shape[1]), np.nan)])
        hp = np.vstack([np.full((1, mid.shape[1]), np.nan), half[:-1]])
        hn = np.vstack([half[1:], np.full((1, mid.shape[1]), np.nan)])
        dmid = mid - prev                                                   # the trade minute's own mid change (start -> end)
        for lab, c, h in (("centred (t-1,t) [Amendment 1]", (prev + mid) / 2, (hp + half) / 2), ("forward (t,t+1) [run 0]", (mid + nxt) / 2, (half + hn) / 2)):
            with np.errstate(invalid="ignore", divide="ignore"):
                s = np.clip((vwap - c) / h, -1, 1)
            m = (vol > 0) & np.isfinite(s) & np.isfinite(dmid) & (h > 0)
            out[lab].append(float(np.corrcoef(s[m], np.sign(dmid[m]))[0, 1]))
    res = {k: {"mean corr(sign, own mid change)": float(np.mean(v)), "days negative": int(sum(x < 0 for x in v)), "days": len(v)} for k, v in out.items()}
    (Fl.OUT / "sign_check.json").write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
