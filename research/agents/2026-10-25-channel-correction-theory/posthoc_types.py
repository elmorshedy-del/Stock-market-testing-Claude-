"""POST HOC (after nothing lined up across all three corrections; descriptive): are there correction TYPES, and which one does today resemble?
(1) cosine similarity between the 10-day pre-top z-profiles of the 6 events and today; (2) the same line-up rule on an earlier window
(sessions t-30..t-11) in case warnings lead by more than 10 sessions. Usage: python posthoc_types.py  -> out/types.json"""
import json

import numpy as np
import pandas as pd

import dossier as Dz


def main():
    prof = pd.read_csv(Dz.OUT / "profile.csv", index_col=0)
    cols = Dz.MAJOR + Dz.MINOR + ["today (Oct 12-23)"]
    X = prof[cols].drop(index=["SPY dealer gamma percentile"])
    cos = lambda a, b: float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
    S = pd.DataFrame([[cos(X[a].to_numpy(), X[b].to_numpy()) for b in cols] for a in cols], index=cols, columns=cols)
    D = pd.read_csv(Dz.OUT / "daily.csv", index_col=0, parse_dates=True)
    I = D.drop(columns=["dist", "similarity"], errors="ignore")
    idx = I.index
    ch = (idx >= Dz.CH0) & (idx <= Dz.CH1)
    ref = ch & (D["dist"] >= -0.03).to_numpy()
    mu, sd = I[ref].mean(), I[ref].std()
    early = {}
    for e in Dz.MAJOR + Dz.MINOR:
        i = idx.get_loc(pd.Timestamp(e))
        early[e] = ((I.iloc[i - 30:i - 10].mean() - mu) / sd)
    E = pd.DataFrame(early)
    lined = {}
    for k in E.index:
        v = E.loc[k].to_numpy()
        for sg in (1, -1):
            if np.all(sg * v[:3] >= 0.5) and np.sum(sg * v >= 0.5) >= 5:
                lined[k] = "high" if sg > 0 else "low"
    near = [k for k in E.index if max(np.sum(E.loc[k].to_numpy()[:3] >= 0.5), np.sum(E.loc[k].to_numpy()[:3] <= -0.5)) == 3]
    res = {"similarity matrix (10-day pre-top profiles, 23 indicators)": S.round(2).to_dict(),
           "today most similar to": S["today (Oct 12-23)"].drop("today (Oct 12-23)").sort_values(ascending=False).round(2).to_dict(),
           "earlier window (t-30..t-11): lined up": lined, "earlier window: 3 of 3 majors same sign": near,
           "earlier window profile": E.round(2).to_dict()}
    (Dz.OUT / "types.json").write_text(json.dumps(res, indent=1))
    return S, E, res


if __name__ == "__main__":
    S, E, res = main()
    pd.set_option("display.width", 250)
    print(S.round(2).to_string()); print(E.round(2).to_string())
    print(json.dumps({k: res[k] for k in ["today most similar to", "earlier window (t-30..t-11): lined up", "earlier window: 3 of 3 majors same sign"]}, indent=1))
