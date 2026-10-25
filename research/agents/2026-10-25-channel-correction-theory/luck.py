"""Strict reading of the pre-registered dip rule (8 corrections found, so 'at least 5 of 6' scales to at least 7 of 8, all 3 main corrections included)
plus a luck check: shuffle the outcome labels across the 21 decided episodes 2,000 times and count the indicators that pass by chance.
Usage: python luck.py <etfs folder>  -> out/luck.json"""
import json
import sys

import numpy as np
import pandas as pd

import dossier as Dz

RNG = np.random.default_rng(20261103)


def passes(P, lab, major_mask, need=7):
    out = []
    for k in P.index:
        v = P.loc[k].to_numpy(dtype=float)
        if np.isnan(v).any():
            continue
        c, b = v[lab], v[~lab]
        med, diff = np.median(b), c.mean() - b.mean()
        side = 1 if diff > 0 else -1
        if (side * (c - med) > 0).sum() >= need and np.all(side * (v[major_mask] - med) > 0) and abs(diff) >= 0.5:
            out.append(k)
    return out


def main(etfs):
    P = pd.read_csv(Dz.OUT / "dip_profiles.csv", index_col=0)
    P = P[[c for c in P.columns if not c.startswith("open")]]
    lab = np.array([c.startswith("corr") for c in P.columns])
    major = np.array([any(m in c for m in Dz.MAJOR) for c in P.columns])
    obs = passes(P, lab, major)
    null = []
    for _ in range(2000):
        perm = RNG.permutation(len(lab))
        lp = lab[perm]
        mp = np.zeros(len(lab), bool)
        mp[RNG.choice(np.nonzero(lp)[0], 3, replace=False)] = True          # 3 'main' events drawn among the shuffled corrections
        null.append(len(passes(P, lp, mp)))
    null = np.array(null)
    b = P.loc["share of panel above 50-day"]
    split = {"breadth z > 0.2": {"corrections": int(((b > 0.2) & lab).sum()), "bounces": int(((b > 0.2) & ~lab).sum())},
             "breadth z <= 0.2": {"corrections": int(((b <= 0.2) & lab).sum()), "bounces": int(((b <= 0.2) & ~lab).sum())}}
    res = {"strict rule (>= 7 of 8, 3 of 3 main)": obs, "expected number passing by chance": float(null.mean()),
           "P(>= observed count by chance)": float((null >= len(obs)).mean()), "P(breadth alone passes by chance) proxy: share of shuffles with >= 1 pass": float((null >= 1).mean()),
           "post hoc breadth split (threshold read off the data)": split}
    (Dz.OUT / "luck.json").write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1))


def auc_check():
    """Effect-size luck check: Mann-Whitney AUC (corrections vs bounces, either direction) for each indicator; family-wise p = share of
    shuffles whose BEST indicator reaches the observed AUC."""
    P = pd.read_csv(Dz.OUT / "dip_profiles.csv", index_col=0)
    P = P[[c for c in P.columns if not c.startswith("open")]].dropna()
    lab = np.array([c.startswith("corr") for c in P.columns])
    V = P.to_numpy(dtype=float)
    def aucs(l):
        c, b = V[:, l], V[:, ~l]
        a = (c[:, :, None] > b[:, None, :]).mean(axis=(1, 2))
        return np.maximum(a, 1 - a)
    obs = pd.Series(aucs(lab), index=P.index).sort_values(ascending=False)
    best = np.array([aucs(RNG.permutation(lab)).max() for _ in range(5000)])
    res = {"AUC by indicator (top 6)": obs.head(6).round(3).to_dict(),
           "family-wise p (best of all indicators by chance >= observed)": {k: float((best >= v).mean()) for k, v in obs.head(3).items()}}
    (Dz.OUT / "luck_auc.json").write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[2] == "auc":
    print(json.dumps(auc_check(), indent=1))
