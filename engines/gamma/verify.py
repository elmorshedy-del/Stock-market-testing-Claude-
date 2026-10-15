"""Independent checks of the gamma engine. Run it instead of trusting the README.

Part A needs no data: synthetic option chains with a known answer.
  A1  implied vol: price options at a known vol, solve it back
  A2  spot from put-call parity recovers the true spot
  A3  sign convention: calls add dealer gamma, puts subtract (classic)
  A4  GEX units: equals the finite-difference change in dealer $ delta for a 1% move
  A5  flip: lies between a put-heavy strike below and a call-heavy strike above, with GEX < 0 under it and > 0 over it
Part B needs downloaded ThetaData files (td_pull.py) in STUDY/data/thetadata and outputs in STUDY/out.
  B1  rebuilding the last two months reproduces the saved out/td_gamma_{SYM}.csv
  B2  open interest dated t is the PRIOR close: the OI change from t to t+1 tracks day t's volume, not day t+1's
  B3  dealer sign, empirically: SPY gamma under the classic convention tracks SqueezeMetrics' published GEX
      (needs out/td_gamma_SPY.csv and data/DIX.csv); the all-short convention should track it worse

Usage: python verify.py                         # part A only
       python verify.py --study ../../research/microstructure --sym TSLA
Exit code 1 if any check fails.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import td_gamma as t
from hd_gamma import flip
from options_flow import exposures, greeks

RESULTS = []


def check(name, ok, got, expected):
    RESULTS.append((name, "PASS" if ok else "FAIL", got, expected))


def chain(S=100.0, vol=0.35, days=(7, 30, 60), strikes=np.arange(70, 131, 2.5), oi_call=None, oi_put=None):
    rows = []
    for d in days:
        for K in strikes:
            for cp in "CP":
                oi = (oi_call if cp == "C" else oi_put)
                rows.append({"K": K, "strike": K, "cp": cp, "T": d / 365, "iv": vol, "exp": pd.Timestamp("2026-01-01") + pd.Timedelta(days=d),
                             "oi": float(oi(K) if callable(oi) else 1000)})
    g = pd.DataFrame(rows)
    g["mid"] = t.bs_price(S, g.K.to_numpy(), g["T"].to_numpy(), vol, (g.cp == "C").to_numpy())
    g["date"], g["expiration"] = pd.Timestamp("2026-01-01"), g.exp
    return g


def part_a():
    S, vol = 100.0, 0.35
    g = chain(S, vol)
    otm = ((g.cp == "C") & (g.K >= S)) | ((g.cp == "P") & (g.K < S))
    q = g[otm & (g.mid > 0.01)]
    iv = t.implied_vol(q.mid.to_numpy(), S, q.K.to_numpy(), q["T"].to_numpy(), (q.cp == "C").to_numpy())
    err = np.nanmax(np.abs(iv - vol))
    check("A1 implied vol round trip", err < 1e-3, f"max error {err:.2e}", "< 1e-3")

    s_hat = t.spot_from_parity(g)
    check("A2 spot from put-call parity", abs(s_hat / S - 1) < 0.002, f"{s_hat:.3f} vs {S}",
          "within 0.2% (parity ignores discounting: bias about K*r*T)")

    calls, puts = g[g.cp == "C"], g[g.cp == "P"]
    gc, gp = exposures(calls, S, "classic").gex.sum(), exposures(puts, S, "classic").gex.sum()
    check("A3 sign: calls +, puts - (classic)", gc > 0 and gp < 0, f"calls {gc:+.3g}, puts {gp:+.3g}", "calls > 0, puts < 0")

    one = calls[(calls.K == 100) & (calls["T"] == 30 / 365)].copy()
    one["oi"] = 1.0
    gex = exposures(one, S, "classic").gex.sum()
    d0, *_ = greeks(S, one.K.to_numpy(), one["T"].to_numpy(), one.iv.to_numpy(), np.array([True]))
    d1, *_ = greeks(S * 1.0001, one.K.to_numpy(), one["T"].to_numpy(), one.iv.to_numpy(), np.array([True]))
    fd = (d1 - d0)[0] / 0.0001 * 0.01 * 100 * S          # dealer $ delta change for a 1% move, one long call contract
    check("A4 GEX units = $ delta change per 1% move", abs(gex / fd - 1) < 0.01, f"{gex:.2f} vs finite difference {fd:.2f}", "within 1%")

    g = chain(S, vol, oi_call=lambda K: 5000 if K == 110 else 100, oi_put=lambda K: 5000 if K == 90 else 100)
    f = flip(g, S)
    below, above = exposures(g, f * 0.98, "classic").gex.sum(), exposures(g, f * 1.02, "classic").gex.sum()
    check("A5 flip between put and call walls", 90 < f < 110 and below < 0 < above,
          f"flip {f:.2f}; GEX 2% under {below:+.3g}, 2% over {above:+.3g}", "90 < flip < 110, sign change across it")


def part_b(study, sym):
    t.DIR = Path(study) / "data" / "thetadata"
    out = Path(study) / "out"
    eod, oi = t.read(sym, "eod"), t.read(sym, "oi")
    if oi.empty:
        check("B data present", False, f"no {sym} files in {t.DIR}", "run td_pull.py first")
        return
    saved = out / f"td_gamma_{sym}.csv"
    if saved.exists():
        months = sorted(eod.date.dt.to_period("M").unique())[-2:]
        keep_e, keep_o = eod.date.dt.to_period("M").isin(months), oi.date.dt.to_period("M").isin(months)
        t.read = (lambda e, o: (lambda s, k: e if k == "eod" else o))(eod[keep_e], oi[keep_o])
        new = t.build(sym).set_index("date")
        old = pd.read_csv(saved, parse_dates=["date"]).set_index("date").reindex(new.index)
        cols = ["gex_classic", "flip_classic", "near_oi_share", "call_wall", "put_wall"]
        diff = (new[cols] - old[cols]).abs().max().max()
        check(f"B1 rebuild reproduces {saved.name}", diff < 1e-6, f"{len(new)} days, max abs diff {diff:.2e}", "0")

    key = ["expiration", "strike", "cp"]
    o = oi.rename(columns={next(c for c in oi.columns if "open_interest" in c): "oi"})
    o = o[o.date >= o.date.max() - pd.Timedelta(days=60)]
    p = o.pivot_table(index=key, columns="date", values="oi")
    v = eod[eod.date >= o.date.min()].pivot_table(index=key, columns="date", values="volume").reindex(p.index)
    days = [d for d in p.columns if d in v.columns]
    rows = []
    for a, b, c in zip(days, days[1:], days[2:]):
        d_oi = (p[b] - p[a]).abs()
        rows.append({"same day": d_oi.corr(v[a], method="spearman"), "next day": d_oi.corr(v[b], method="spearman")})
    r = pd.DataFrame(rows).mean()
    check("B2 OI dated t = prior close", r["same day"] > r["next day"] + 0.1,
          f"rank corr of OI change (t->t+1) with volume on t {r['same day']:.2f}, on t+1 {r['next day']:.2f}",
          "volume on t clearly higher")

    spy, dix = out / "td_gamma_SPY.csv", Path(study) / "data" / "DIX.csv"
    if spy.exists() and dix.exists():
        m = pd.read_csv(spy, parse_dates=["date"]).set_index("date")
        sq = pd.read_csv(dix, parse_dates=["date"]).set_index("date").gex
        j = m[["gex_classic", "gex_short"]].join(sq.rename("sqz"), how="inner").loc["2021":]
        pc = lambda s: s.rolling(252, min_periods=120).rank(pct=True)
        c, s_ = j.gex_classic.corr(j.sqz), j.gex_short.corr(j.sqz)
        cp = pc(j.gex_classic).corr(pc(j.sqz))
        check("B3 classic sign matches SqueezeMetrics", c > 0.3 and c > s_ + 0.3,
              f"levels: classic {c:.2f}, all-short {s_:.2f}; percentiles (classic) {cp:.2f}; n={len(j)}",
              "classic clearly positive and above all-short (reported: 0.67 levels, 0.83 percentiles)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", help="folder holding data/thetadata and out/ (e.g. ../../research/microstructure)")
    ap.add_argument("--sym", default="TSLA")
    a = ap.parse_args()
    part_a()
    if a.study:
        part_b(a.study, a.sym)
    w = max(len(r[0]) for r in RESULTS)
    for name, status, got, exp in RESULTS:
        print(f"{status}  {name:<{w}}  {got}   [expected {exp}]")
    sys.exit(any(r[1] == "FAIL" for r in RESULTS))
