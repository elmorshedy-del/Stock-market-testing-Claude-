"""Cross-asset fingerprints. The predicted sign table is written from first principles BEFORE any episode is computed.
Columns: STOCKS (S&P), BONDS (long Treasury price, TLT), GOLD, USD (DXY), YEN (yen vs USD = -USDJPY), CREDIT (HYG), BTC."""
import json
from pathlib import Path
import numpy as np, pandas as pd

H = Path(__file__).resolve().parent; D = H / "data"
COLS = ["STOCKS", "BONDS", "GOLD", "USD", "YEN", "CREDIT", "BTC"]
# Who is forced, and what they must do -> predicted sign of each asset (+1 up, -1 down, 0 no clear sign)
MECH = {
    "Discount-rate shock":        {"why": "real yields rise (inflation, fiscal, term premium); every asset is re-priced at a higher rate",
                                   "sign": [-1, -1, -1, +1, -1, -1, -1]},
    "Growth scare":               {"why": "earnings fear; money moves from risk to safety, no one is forced",
                                   "sign": [-1, +1, +1, +1, +1, -1, -1]},
    "Yen-carry unwind":           {"why": "borrowers in yen buy yen back to repay; the funding currency jumps",
                                   "sign": [-1, +1, 0, -1, +1, -1, -1]},
    "Dollar-funded deleveraging": {"why": "levered holders sell what they can, not what they want, and repay dollars",
                                   "sign": [-1, +1, -1, +1, -1, -1, -1]},
    "Loss of trust in US assets": {"why": "foreigners sell US stocks, bonds and dollars together and buy gold",
                                   "sign": [-1, -1, +1, -1, +1, -1, 0]},
}
EPISODES = {  # (start close, end close, what is known about it)
    "2020 dash for cash":      ("2020-02-21", "2020-03-18", "forced selling of everything for dollars"),
    "2022 rate shock":         ("2022-01-03", "2022-06-16", "Fed hiking cycle, real yields up"),
    "2024 yen-carry unwind":   ("2024-07-31", "2024-08-05", "BoJ hike, yen-funded positions closed"),
    "2025 tariff shock":       ("2025-04-02", "2025-04-11", "tariffs; US bonds and dollar sold together"),
    "2026 phase 1 (Sep 3 - Oct 5)": ("2026-09-03", "2026-10-05", "?"),
    "2026 phase 2 (Oct 6 - Nov 20)": ("2026-10-06", "2026-11-20", "?"),
}

def load():
    c = pd.read_csv(D / "closes.csv", index_col=0, parse_dates=True)
    x = pd.DataFrame({"STOCKS": c.SPX, "BONDS": c.TLT, "GOLD": c.GOLD, "USD": c.DXY, "YEN": 1 / c.USDJPY, "CREDIT": c.HYG,
                      "BTC": c.BTC, "NIKKEI": c.NIKKEI, "SILVER": c.SILVER, "NDX": c.NDX, "US10Y": c.US10Y, "VIX": c.VIX})
    return x[x.STOCKS.notna()].ffill()

def change(x, a, b):
    s = x.loc[:a].iloc[-1]; e = x.loc[:b].iloc[-1]
    out = {k: 100 * (e[k] / s[k] - 1) for k in COLS + ["NIKKEI", "SILVER", "NDX"]}
    out["US10Y_bp"] = 100 * (e.US10Y - s.US10Y); out["VIX_pts"] = e.VIX - s.VIX
    return out

def score(obs, band):
    """Signs of observed moves (0 inside a dead band scaled to each asset's typical move); share of predicted signs matched."""
    sg = [0 if abs(obs[k]) < band[k] else int(np.sign(obs[k])) for k in COLS]
    res = {}
    for m, v in MECH.items():
        p = v["sign"]; n = sum(1 for a, b in zip(p, sg) if a != 0)
        res[m] = sum(1 for a, b in zip(p, sg) if a != 0 and a == b) / n
    return sg, res

if __name__ == "__main__":
    x = load(); r = x[COLS + ["SILVER", "NIKKEI", "NDX"]].pct_change() * 100
    out = {"episodes": {}}
    for name, (a, b, known) in EPISODES.items():
        obs = change(x, a, b); n = len(x.loc[a:b]) - 1
        band = {k: 0.5 * r[k].loc[:"2026-08-31"].std() * np.sqrt(max(n, 1)) for k in COLS}   # half a typical move over the window
        sg, res = score(obs, band); best = max(res, key=res.get)
        out["episodes"][name] = {"start": a, "end": b, "known": known, "days": n, "moves": {k: round(v, 2) for k, v in obs.items()},
                                 "signs": dict(zip(COLS, sg)), "match": {k: round(v, 2) for k, v in res.items()}, "best": best}
        print(f"\n{name}  [{a} → {b}, {n} days]  known: {known}")
        print("   " + "  ".join(f"{k}:{obs[k]:+6.1f}%" for k in COLS) + f"  10y:{obs['US10Y_bp']:+4.0f}bp  Nikkei:{obs['NIKKEI']:+5.1f}%  VIX:{obs['VIX_pts']:+5.1f}")
        print("   signs " + " ".join(f"{k}{'+' if s > 0 else '-' if s < 0 else '0'}" for k, s in zip(COLS, sg)))
        print("   match " + "  ".join(f"{m}: {v:.0%}" for m, v in sorted(res.items(), key=lambda t: -t[1])))
    # ---- phase 2, day by day: the worst S&P days ----
    p2 = r.loc["2026-10-06":"2026-11-20"]; worst = p2.STOCKS.nsmallest(8)
    dyl = (x.US10Y.diff() * 100).loc[worst.index]
    print("\nPhase 2, the 8 worst S&P days:"); print(pd.concat([p2.loc[worst.index, COLS + ["SILVER", "NIKKEI"]].round(1), dyl.round(0).rename("10y_bp")], axis=1).sort_index().to_string())
    frac = {k: float((np.sign(p2.loc[worst.index, k]) == s).mean()) for k, s in zip(COLS, MECH["Dollar-funded deleveraging"]["sign"])}
    print("share of those days matching the deleveraging sign:", {k: f"{v:.0%}" for k, v in frac.items()})
    # ---- gold: what yields alone predict vs what happened ----
    real = pd.read_csv(D / "FRED_DFII10.csv"); real.columns = ["d", "v"]; real["d"] = pd.to_datetime(real.d)
    real = real.set_index("d").v.replace(".", np.nan).astype(float).reindex(x.index).ffill()
    df = pd.DataFrame({"gold": r.GOLD, "dreal": real.diff() * 100, "dusd": r.USD, "stocks": r.STOCKS}).dropna()
    fit = df.loc["2023-01-01":"2026-08-31"]; X = np.c_[np.ones(len(fit)), fit.dreal, fit.dusd]
    beta = np.linalg.lstsq(X, fit.gold, rcond=None)[0]
    pred = beta[0] + beta[1] * df.dreal + beta[2] * df.dusd
    resid_sd = float((fit.gold - X @ beta).std())
    print(f"\nGold model 2023-01..2026-08: gold% = {beta[0]:.3f} {beta[1]:+.3f}·Δreal10y(bp) {beta[2]:+.3f}·DXY%   residual s.d. {resid_sd:.2f}%")
    w = worst.index.intersection(df.index)
    g = pd.DataFrame({"actual": df.gold.loc[w], "predicted_from_yields_and_dollar": pred.loc[w], "dreal_bp": df.dreal.loc[w]}).round(2)
    g["gap_in_sd"] = ((g.actual - g.predicted_from_yields_and_dollar) / resid_sd).round(1)
    print(g.sort_index().to_string()); print("sum over these days: actual %.1f%%, predicted %.1f%%" % (g.actual.sum(), g.predicted_from_yields_and_dollar.sum()))
    for name, (a, b) in {"phase 1": ("2026-09-03", "2026-10-05"), "phase 2": ("2026-10-06", "2026-11-20")}.items():
        s = df.loc[a:b]; print(f"{name}: gold actual {s.gold.sum():+.1f}%  predicted from yields+dollar {pred.loc[s.index].sum():+.1f}%")
    # ---- co-movement on down days vs up days ----
    def corr(a, b, mask): return float(np.corrcoef(a[mask], b[mask])[0, 1])
    rows = []
    for per, (a, b) in {"2023-01..2026-08": ("2023-01-01", "2026-08-31"), "phase 2": ("2026-10-06", "2026-11-20")}.items():
        s = r.loc[a:b].dropna(subset=["STOCKS", "GOLD", "BTC", "BONDS"])
        for k in ["GOLD", "BTC", "BONDS"]:
            dn, up = s.STOCKS < 0, s.STOCKS > 0
            rows.append({"period": per, "asset": k, "corr_all": round(corr(s.STOCKS, s[k], s.STOCKS == s.STOCKS), 2),
                         "corr_down_days": round(corr(s.STOCKS, s[k], dn), 2), "corr_up_days": round(corr(s.STOCKS, s[k], up), 2), "n": len(s)})
    cm = pd.DataFrame(rows); print("\nCorrelation with the S&P (daily):"); print(cm.to_string(index=False))
    out.update({"gold_model": {"const": beta[0], "per_bp_real": beta[1], "per_pct_usd": beta[2], "resid_sd": resid_sd},
                "worst_days": g.reset_index().astype(str).to_dict("records"), "deleveraging_sign_share": frac, "correlations": rows,
                "mechanisms": MECH})
    json.dump(out, open(H / "out" / "fingerprints.json", "w"), indent=1, default=float)
