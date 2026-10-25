"""Amendment 1 (pre-registered at 604dbb0, margin added before computing): dip anatomy inside the channel.
Each first close >= 2% below the running high -> correction (-5% first) or bounce (new high first). Which indicators separate them?
Usage: python dips.py <etfs folder>  -> out/dips.csv, out/dip_profiles.csv, out/dips.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import dossier as Dz

MACRO = Dz.AG / "2026-10-15-channel-reversion-macro" / "out" / "macro_monthly.csv"


def margin_daily(idx, spx):
    m = pd.read_csv(MACRO, parse_dates=["month"]).set_index("month")
    sm = spx.resample("ME").last()
    sy = 100 * (sm / sm.shift(12) - 1)
    g = m.margin_yoy.dropna()
    rel = (g - sy.reindex(g.index)).dropna()
    def lagged(s):
        return pd.Series([s[s.index <= d - pd.offsets.MonthEnd(2)].iloc[-1] if (s.index <= d - pd.offsets.MonthEnd(2)).any() else np.nan for d in idx], index=idx)
    return lagged(g), lagged(rel)


def episodes(spx):
    v, idx = spx.to_numpy(), spx.index
    start = idx.get_loc(idx[idx >= Dz.CH0][0])
    out, i, H, Hd, armed = [], start, v[start], idx[start], True
    while i < len(v):
        if v[i] > H:
            H, Hd, armed = v[i], idx[i], True
        elif armed and v[i] <= 0.98 * H:
            j, res = i + 1, "open"
            while j < len(v):
                if v[j] > H:
                    res = "bounce"; break
                if v[j] <= 0.95 * H:
                    res = "correction"; break
                j += 1
            out.append({"high date": Hd.date(), "start": idx[i].date(), "outcome": res, "decided": idx[j].date() if j < len(v) else None,
                        "depth at start %": round(100 * (v[i] / H - 1), 2)})
            armed = False
            if res == "bounce":
                i = j
                continue
        i += 1
    return pd.DataFrame(out)


def main(etfs):
    D = pd.read_csv(Dz.OUT / "daily.csv", index_col=0, parse_dates=True)
    spx = Dz.close(etfs, "%5EGSPC").reindex(D.index)
    D["margin debt growth"], D["margin debt vs prices"] = margin_daily(D.index, spx)
    dist = D.pop("dist")
    D = D.drop(columns=["similarity"], errors="ignore")
    idx = D.index
    ref = (idx >= Dz.CH0) & (idx <= Dz.CH1) & (dist >= -0.03).to_numpy()
    mu, sd = D[ref].mean(), D[ref].std()
    Z5 = (D.rolling(5, min_periods=4).mean() - mu) / sd
    E = episodes(spx[spx.index >= "2022-01-01"])
    E["start"] = pd.to_datetime(E["start"])
    prof = pd.DataFrame({f"{r.outcome[:4]} {r['high date']}": Z5.loc[r.start] for _, r in E.iterrows()})
    corr_cols = [c for c in prof.columns if c.startswith("corr")]
    boun_cols = [c for c in prof.columns if c.startswith("boun")]
    open_cols = [c for c in prof.columns if c.startswith("open")]
    major = [c for c in corr_cols if any(m in c for m in Dz.MAJOR)]
    rows = []
    for k in prof.index:
        b = prof.loc[k, boun_cols].astype(float)
        cvals = prof.loc[k, corr_cols].astype(float)
        med = b.median()
        diff = cvals.mean() - b.mean()
        side = 1 if diff > 0 else -1
        beyond = (side * (cvals - med) > 0)
        ok = bool(beyond.sum() >= 5 and all(side * (prof.loc[k, major].astype(float) - med) > 0) and abs(diff) >= 0.5)
        rows.append({"indicator": k, "separates": ok, "direction in corrections": "higher" if side > 0 else "lower",
                     "corrections beyond bounce median": int(beyond.sum()), "majors beyond": int(sum(side * (prof.loc[k, major].astype(float) - med) > 0)),
                     "mean z corrections": float(cvals.mean()), "mean z bounces": float(b.mean()), "difference": float(diff),
                     "today (open episode) z": float(prof.loc[k, open_cols[-1]]) if open_cols else None,
                     "today on the correction side": bool(side * (float(prof.loc[k, open_cols[-1]]) - med) > 0) if open_cols else None})
    R = pd.DataFrame(rows).sort_values("difference", key=lambda s: -s.abs())
    E.to_csv(Dz.OUT / "dips.csv", index=False)
    prof.round(3).to_csv(Dz.OUT / "dip_profiles.csv")
    R.round(3).to_csv(Dz.OUT / "dip_separation.csv", index=False)
    sep = R[R.separates]
    res = {"episodes": E.outcome.value_counts().to_dict(), "correction high dates": E[E.outcome == "correction"]["high date"].astype(str).tolist(),
           "separating indicators": sep[["indicator", "direction in corrections", "corrections beyond bounce median", "difference", "today (open episode) z",
                                         "today on the correction side"]].to_dict("records"),
           "today's episode": E[E.outcome == "open"].astype(str).to_dict("records")}
    (Dz.OUT / "dips.json").write_text(json.dumps(res, indent=1, default=str))
    return E, R, res


if __name__ == "__main__":
    E, R, res = main(sys.argv[1])
    pd.set_option("display.width", 250)
    print(E.to_string())
    print(R.round(2).to_string())
    print(json.dumps(res, indent=1, default=str))
