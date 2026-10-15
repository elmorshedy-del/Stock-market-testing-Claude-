"""Dealer-positioning map from an option-chain snapshot: GEX, vanna, charm,
gamma flip, walls, max pain, implied moves.

Sign conventions (no free data says who is long or short, so both are shown):
  classic : dealers long calls / short puts (customers overwrite calls, buy puts)
  short   : dealers short both (customers net buy calls and puts, typical of
            momentum/meme regimes like MU 2026)
IVs are re-solved from last trade prices because snapshot IVs are stale or
broken pre-market; then smoothed per expiry from OTM quotes (sticky strike).
"""
import json

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.stats import norm

from common import DATA

R, Qd = 0.04, 0.0005


def bs(S, K, T, s, cp):
    d1 = (np.log(S / K) + (R - Qd + 0.5 * s * s) * T) / (s * np.sqrt(T))
    d2 = d1 - s * np.sqrt(T)
    if cp == "C":
        return S * np.exp(-Qd * T) * norm.cdf(d1) - K * np.exp(-R * T) * norm.cdf(d2)
    return K * np.exp(-R * T) * norm.cdf(-d2) - S * np.exp(-Qd * T) * norm.cdf(-d1)


def greeks(S, K, T, s, is_call):
    sq = np.sqrt(T)
    d1 = (np.log(S / K) + (R - Qd + 0.5 * s * s) * T) / (s * sq)
    d2 = d1 - s * sq
    pdf = norm.pdf(d1)
    delta = np.where(is_call, norm.cdf(d1), norm.cdf(d1) - 1)
    gamma = pdf / (S * s * sq)
    vanna = -pdf * d2 / s                                   # dDelta/dSigma
    charm = -pdf * (2 * (R - Qd) * T - d2 * s * sq) / (2 * T * s * sq)  # dDelta/dT (per year, call≈put)
    return delta, gamma, vanna, charm


def solve_iv(price, S, K, T, cp):
    intrinsic = max(0.0, (S - K) if cp == "C" else (K - S))
    if not np.isfinite(price) or price <= intrinsic + 1e-3:
        return np.nan
    try:
        return brentq(lambda v: bs(S, K, T, v, cp) - price, 1e-3, 8.0)
    except ValueError:
        return np.nan


def load_chain(sym="MU"):
    snap = json.loads((DATA / f"{sym}_options.json").read_text())
    q = snap["quote"]
    S, t0 = q["regularMarketPrice"], q["regularMarketTime"]
    rows = []
    for ch in snap["chains"]:
        exp = ch["expirationDate"] + 20 * 3600          # 16:00 ET close
        T = max((exp - t0) / (365 * 86400), 1 / (365 * 24))
        for cp, key in (("C", "calls"), ("P", "puts")):
            for o in ch[key]:
                rows.append({"exp": pd.Timestamp(ch["expirationDate"], unit="s").date(), "T": T,
                             "K": o["strike"], "cp": cp, "oi": o.get("openInterest", 0) or 0,
                             "vol": o.get("volume", 0) or 0, "last": o.get("lastPrice", np.nan),
                             "traded": o.get("lastTradeDate", 0)})
    df = pd.DataFrame(rows)
    # only fresh prints (same session as spot) are used to solve IV
    fresh = (t0 - df.traded) < 6 * 3600
    otm = ((df.cp == "C") & (df.K >= S)) | ((df.cp == "P") & (df.K < S))
    df["iv_raw"] = [solve_iv(p, S, k, T, cp) if f and o else np.nan
                    for p, k, T, cp, f, o in zip(df["last"], df.K, df["T"], df.cp, fresh, otm)]
    ivs = []
    for exp, g in df.groupby("exp"):
        pts = g.dropna(subset=["iv_raw"]).groupby("K").iv_raw.median()
        pts = pts[(pts > 0.05) & (pts < 4)]
        if len(pts) >= 3:
            iv = np.interp(g.K, pts.index, pts.rolling(3, center=True, min_periods=1).median())
        else:
            iv = np.full(len(g), np.nan)
        ivs.append(pd.Series(iv, index=g.index))
    df["iv"] = pd.concat(ivs)
    df["iv"] = df["iv"].fillna(df.groupby("exp")["iv"].transform("median")).fillna(df["iv"].median())
    return S, t0, q, df


def exposures(df, S, convention="classic"):
    is_call = (df.cp == "C").to_numpy()
    d, g, va, ch = greeks(S, df.K.to_numpy(), df["T"].to_numpy(), df.iv.to_numpy(), is_call)
    if convention == "classic":
        sign = np.where(is_call, 1.0, -1.0)
    else:
        sign = -np.ones(len(df))
    n = df.oi.to_numpy() * 100 * sign
    return pd.DataFrame({
        "K": df.K, "exp": df.exp, "cp": df.cp,
        "gex": g * n * S * S * 0.01,          # $ dealer delta change per 1% move
        "vanna": va * n * S * 0.01,           # $ dealer delta change per +1 vol pt
        "charm": -ch * n * S / 365,           # $ dealer delta change per calendar day passing
        "dex": d * n * S,                     # $ dealer delta
    })


def gex_profile(df, S, convention, lo=0.75, hi=1.25, n=201):
    grid = np.linspace(lo * S, hi * S, n)
    tot = np.array([exposures(df, s, convention).gex.sum() for s in grid])
    flips = [(grid[i] + grid[i + 1]) / 2 for i in range(n - 1) if np.sign(tot[i]) != np.sign(tot[i + 1])]
    return grid, tot, flips


def max_pain(g):
    ks = np.sort(g.K.unique())
    c, p = g[g.cp == "C"], g[g.cp == "P"]
    pain = [(np.clip(k - c.K, 0, None) * c.oi).sum() + (np.clip(p.K - k, 0, None) * p.oi).sum() for k in ks]
    return float(ks[int(np.argmin(pain))])


def implied_move(df, S):
    out = {}
    for exp, g in df.groupby("exp"):
        atm = g.iloc[(g.K - S).abs().argsort()[:2]]
        T = g["T"].iloc[0]
        iv = float(atm.iv.mean())
        out[str(exp)] = {"atm_iv": iv, "move_1sd_pct": 100 * iv * np.sqrt(T), "days": T * 365}
    return out


def summary(sym="MU", near_days=45):
    S, t0, q, df = load_chain(sym)
    near = df[df["T"] * 365 <= near_days]
    res = {"spot": S, "asof": pd.Timestamp(t0, unit="s", tz="UTC").tz_convert("America/New_York").isoformat(),
           "total_oi_calls": int(df[df.cp == "C"].oi.sum()), "total_oi_puts": int(df[df.cp == "P"].oi.sum())}
    for conv in ("classic", "short"):
        e = exposures(df, S, conv)
        en = exposures(near, S, conv)
        bys = en.groupby("K")[["gex", "vanna", "charm"]].sum()
        grid, tot, flips = gex_profile(df, S, conv)
        res[conv] = {
            "net_gex_per_1pct": float(e.gex.sum()), "net_vanna_per_volpt": float(e.vanna.sum()),
            "net_charm_per_day": float(e.charm.sum()), "net_dex": float(e.dex.sum()),
            "gamma_flips": [float(x) for x in flips],
            "top_pos_gex_strikes": bys.gex.nlargest(5).round(-5).to_dict(),
            "top_neg_gex_strikes": bys.gex.nsmallest(5).round(-5).to_dict(),
        }
        res[conv]["profile"] = (grid.tolist(), tot.tolist())
    cn = near[near.cp == "C"].groupby("K").oi.sum()
    pn = near[near.cp == "P"].groupby("K").oi.sum()
    res["call_wall_oi"] = float(cn.idxmax()); res["put_wall_oi"] = float(pn.idxmax())
    res["call_oi_top"] = cn.nlargest(6).to_dict(); res["put_oi_top"] = pn.nlargest(6).to_dict()
    res["max_pain"] = {str(e): max_pain(g) for e, g in near.groupby("exp")}
    res["implied_move"] = implied_move(df, S)
    res["pcr_oi_near"] = float(pn.sum() / cn.sum())
    return res, df


if __name__ == "__main__":
    r, df = summary()
    for conv in ("classic", "short"):
        r[conv].pop("profile")
    print(json.dumps(r, indent=1, default=str))
