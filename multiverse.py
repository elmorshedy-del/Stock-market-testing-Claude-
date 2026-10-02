"""Multiverse / specification-curve test of the gamma entry signal.

Every analyst choice becomes a dimension; all combinations are run:
  GEX threshold   g in {0.10, 0.20, 0.30, 0.40}
  DIX filter      dx in {none, >0.5, >0.8}
  horizon         H in {10, 20, 30} trading days
  era             all 2012+, 2019Q4+, 2022-05+
  outcome         excess S&P return | P(up-leg within H) - base rate
-> 4*3*3*3*2 = 216 specifications.

Statistic per spec: mean outcome on first-on event days (>= 10 days apart)
minus the era's all-day mean. Null: circularly shift the GEX/DIX series by a
random offset (keeps their persistence and seasonality, destroys their timing
relative to prices), rerun the WHOLE multiverse, repeat. That answers
"how many specs look this good by luck?" and gives one joint p-value.
"""
import itertools

import numpy as np
import pandas as pd

from forecast import build

GS, DXS, HS = (0.10, 0.20, 0.30, 0.40), (None, 0.5, 0.8), (10, 20, 30)
ERAS = {"2012+": "2012-01-01", "2019Q4+": "2019-10-01", "2022-05+": "2022-05-11"}
N_NULL, GAP = 300, 10


def first_on(c, gap=GAP):
    out, last = np.zeros(len(c), bool), -10**9
    for i in np.where(c & ~np.r_[False, c[:-1]])[0]:
        if i - last >= gap:
            out[i], last = True, i
    return out


def prep(f):
    c = f.c.to_numpy()
    fwd = {h: np.r_[np.log(c[h:] / c[:-h]), np.full(h, np.nan)] for h in HS}
    f10 = fwd[10]
    top = np.nanquantile(f10, 0.9)
    big = np.r_[f10 > top]
    leg = {}
    for h in HS:   # an up-leg starts within the next h days
        w = np.lib.stride_tricks.sliding_window_view(np.r_[big[1:], np.zeros(h, bool)], h)
        leg[h] = np.r_[w.any(axis=1)[:len(c)].astype(float)]
        leg[h][np.isnan(fwd[h])] = np.nan
    return fwd, leg


def run(gp, dp, fwd, leg, era_mask):
    res = []
    for g, dx, h, (era, m) in itertools.product(GS, DXS, HS, era_mask.items()):
        cond = (gp <= g) & m
        if dx is not None:
            cond &= dp > dx
        ev = first_on(cond)
        for name, y in (("excess_ret", fwd[h]), ("p_leg", leg[h])):
            yy = y[ev & ~np.isnan(y)]
            base = np.nanmean(y[m])
            res.append((g, dx, h, era, name, len(yy), (yy.mean() - base) if len(yy) >= 5 else np.nan))
    return pd.DataFrame(res, columns=["gex", "dix", "H", "era", "outcome", "n", "effect"])


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    f = build()
    fwd, leg = prep(f)
    gp, dp = f.gex_pct.to_numpy(), f.dix_pct.to_numpy()
    era_mask = {k: np.asarray(f.index >= v) for k, v in ERAS.items()}
    real = run(gp, dp, fwd, leg, era_mask)
    rng = np.random.default_rng(0)
    null_eff, null_pos = [], []
    for _ in range(N_NULL):
        s = rng.integers(60, len(gp) - 60)
        nl = run(np.roll(gp, s), np.roll(dp, s), fwd, leg, era_mask)
        null_eff.append(nl.effect.to_numpy())
    null_eff = np.array(null_eff)
    # per-spec p-value vs its own shifted null; joint test on the median standardized effect
    p = (null_eff >= real.effect.to_numpy()).mean(axis=0)
    real["p"] = p
    z = (real.effect - np.nanmean(null_eff, 0)) / np.nanstd(null_eff, 0)
    zn = (null_eff - np.nanmean(null_eff, 0)) / np.nanstd(null_eff, 0)
    joint_p = (np.nanmedian(zn, axis=1) >= np.nanmedian(z)).mean()
    share_sig = (real.p < 0.05).mean()
    null_share = np.mean([(np.mean(null_eff >= row, axis=0) < 0.05).mean() for row in null_eff[:100]])
    print(f"specifications: {len(real)}  (valid {real.effect.notna().sum()})")
    print(f"share with positive effect: {(real.effect > 0).mean():.2f}")
    print(f"share significant at 5%: {share_sig:.2f}   (expected by luck ~0.05; shifted-null average {null_share:.2f})")
    print(f"JOINT p-value (median standardized effect vs shifted nulls): {joint_p:.3f}")
    # Benjamini-Hochberg FDR 10%
    ps = np.sort(real.p.dropna().to_numpy())
    k = np.where(ps <= 0.10 * np.arange(1, len(ps) + 1) / len(ps))[0]
    print(f"specs surviving FDR 10%: {k[-1] + 1 if len(k) else 0}")
    real["dix"] = real.dix.map(lambda v: "none" if v is None or v != v else f">{v}")
    print("\nby outcome: share positive / share p<0.05 / FDR survivors")
    print(real.groupby("outcome").agg(n_specs=("p", "size"), pos=("effect", lambda x: (x > 0).mean()),
                                      sig=("p", lambda x: (x < 0.05).mean())).round(2).to_string())
    print("\nwhich choices matter, per outcome (mean effect | share p<0.05):")
    for col in ("gex", "dix", "H", "era"):
        g = real.groupby(["outcome", real[col].astype(str)]).agg(effect=("effect", "mean"), sig=("p", lambda x: (x < 0.05).mean()))
        print(f"\n[{col}]\n" + g.unstack(0).round(3).to_string())
    real.to_csv("out/multiverse.csv", index=False)
