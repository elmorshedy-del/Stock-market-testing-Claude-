"""Test #4 (crash law): Parts A-C as pre-registered in README.md (commit 77fea8a)."""
import json
from pathlib import Path
import numpy as np, pandas as pd

H = Path(__file__).resolve().parent
D, O = H / "data", H / "out"; O.mkdir(exist_ok=True)
K, K_SE = 5.00, 0.38          # KO2023 Eq. 15
Y_KO, Y_ALT = 2 * 12.08e-4 * 50 * 10, 0.9   # KO2023 Eq. 17 -> Y = 1.208; sensitivity 0.9
RNG = np.random.default_rng(20261106)

g = pd.read_csv(D / "GSPC_ohlcv.csv", index_col=0, parse_dates=True)
sx = pd.read_csv(D / "STOXX50E.csv", index_col=0, parse_dates=True)
gd = pd.read_csv(D / "GDPDEF.csv"); gd["observation_date"] = pd.to_datetime(gd["observation_date"]); gd = gd.set_index("observation_date")["GDPDEF"]
G2005 = gd["2005"].mean()
def defl(t):  # 2005 dollars per nominal dollar
    return G2005 / gd[gd.index <= pd.Timestamp(t)].iloc[-1]

lr = np.log(g.close).diff()


# ---------- impact laws ----------
def lin_x(Q_over_V, PVg, sig, k=K):          # log fall
    return (k / 1e4) * (PVg / 40e6) ** (1 / 3) * (sig / 0.02) ** (4 / 3) * Q_over_V / 0.01
def lin(Q_over_V, PVg, sig, k=K): return 1 - np.exp(-lin_x(Q_over_V, PVg, sig, k))
def sqrt_(Q_over_V, sig, Y=Y_KO): return Y * sig * np.sqrt(Q_over_V)


def state(series_close, vol, t0, pre=5, norm=(26, 6)):
    """sigma_now (sessions t0-5..t0-1), sigma_norm (t0-26..t0-6), volume ratio now/norm (1 if no volume)."""
    i = series_close.index.get_indexer([pd.Timestamp(t0)], method="bfill")[0]
    r = np.log(series_close).diff()
    s_now = r.iloc[i - pre:i].std(); s_norm = r.iloc[i - norm[0]:i - norm[1] + 1].std()
    if vol is None or (vol.iloc[i - norm[0]:i] <= 0).any():
        vr = 1.0
    else:
        vr = vol.iloc[i - pre:i].mean() / vol.iloc[i - norm[0]:i - norm[1] + 1].mean()
    return s_now, s_norm, vr, series_close.index[i - pre].date(), series_close.index[i - 1].date()


# ---------- Part A ----------
EV = [  # name, Q, V (same currency), sigma, PV*g in 2005 $, actual, window start, close series, volume series, KO LIN
    ("1929 crash", 1.181e9, 444.97e6, 0.0200, 444.97e6 * 9.42, 0.25, "1929-10-24", g.close, None, 46.43),
    ("1987 crash", 13.75e9, 20.57e9, 0.0135, 20.57e9 * 1.54, 0.32, "1987-10-15", g.close, g.volume, 16.77),
    ("1987 Soros", 309.6e6, 13.52e9, 0.0863, 13.52e9 * 1.54, 0.22, "1987-10-22", g.close, g.volume, 6.27),
    ("2008 SocGen", 50e9, 180.49e9, 0.0110, 180.49e9 * 1.4690 * 0.92, 0.0944, "2008-01-21", sx.close, None, 10.79),
    ("2010 flash crash", 4.37e9, 293e9, 0.0107, 293e9 * 0.90, 0.0512, "2010-05-06", g.close, g.volume, 0.61),
]
A = []
for nm, Q, V, sig, PVg, act, t0, cl, vo, ko in EV:
    q = Q / V
    p_lin, p_sq = lin(q, PVg, sig), sqrt_(q, sig)
    s_now, s_norm, vr, a, b = state(cl, vo, t0)
    p_now = sqrt_(q / vr, s_now)
    xa = -np.log(1 - act)
    A.append({"event": nm, "actual %": round(100 * act, 2), "Q % of ADV": round(100 * q, 2),
              "LIN %": round(100 * p_lin, 2), "KO published LIN %": ko, "replicates (|diff| <= 0.3pp)": bool(abs(100 * p_lin - ko) <= 0.3),
              "SQRT %": round(100 * p_sq, 2), "SQRT-now %": round(100 * p_now, 2),
              "sigma now / KO sigma": round(s_now / sig, 2), "volume now / normal": round(vr, 2), "state window": f"{a}..{b}",
              "LIN sale needed (x documented)": round(xa / lin_x(q, PVg, sig), 2),
              "SQRT sale needed (x documented)": round((act / p_sq) ** 2, 1),
              "SQRT-now sale needed (x documented)": round((act / p_now) ** 2, 1),
              "SQRT-now sale needed (% of ADV)": round(100 * q * (act / p_now) ** 2, 1)})
A = pd.DataFrame(A)
print(A.to_string())

# ---------- Part B ----------
sh = pd.read_csv(H.parent / "2026-11-06-signature-test" / "out" / "shocks.csv")
sh = sh[sh["index"] == "S&P 500"].copy(); sh["date"] = pd.to_datetime(sh["date"])
dv = g.volume * g.close
w = g.index[g.index.get_indexer([pd.Timestamp("2010-05-06")])[0] - 21: g.index.get_indexer([pd.Timestamp("2010-05-06")])[0]]
c = 161.41e9 / dv.loc[w].mean()
w87 = g.index[(g.index >= "1987-09-15") & (g.index <= "1987-10-14")]
x87 = c * dv.loc[w87].mean()
crosscheck = {"proxy stock $vol Sep15-Oct14 1987 ($bn, nominal)": round(float(x87) / 1e9, 2), "KO NYSE ($bn)": 10.20,
              "ratio": round(float(x87) / 10.20e9, 2), "within 2x": bool(0.5 <= x87 / 10.20e9 <= 2),
              "action": "FAILED -> pre-registered fallback: PV from KO's 1987 and 2010 whole-market anchors, log-linear in time"}
print("cross-check", crosscheck)

# Pre-registered fallback (cross-check failed): whole-market PV(t) = KO anchors (1987-10-14: $20.57bn; 2010-05-05: $293bn, nominal,
# futures + stocks), log-linear in time, extended linearly in log outside the anchors. Sensitivity: proxy re-scaled at both anchors.
T87, T10 = pd.Timestamp("1987-10-14"), pd.Timestamp("2010-05-05")
def pv_anchor(t):
    a = (pd.Timestamp(t) - T87).days / (T10 - T87).days
    return float(np.exp(np.log(20.57e9) + a * (np.log(293e9) - np.log(20.57e9))))
i87 = g.index.get_indexer([pd.Timestamp("1987-10-15")])[0]
c87 = 20.57e9 / dv.iloc[i87 - 21:i87].mean(); c10 = 293e9 / dv.loc[w].mean()
def c_two(t):  # proxy scale interpolated in log-time between the anchors, held flat outside
    a = min(max((pd.Timestamp(t) - T87).days / (T10 - T87).days, 0), 1)
    return float(np.exp(np.log(c87) + a * (np.log(c10) - np.log(c87))))
rows = []
for _, s in sh.iterrows():
    t = s["date"]; i = g.index.get_indexer([t])[0]
    if i < 27 or (g.volume.iloc[i - 26:i + 1] <= 0).any():
        continue
    f = -lr.iloc[i]
    s_norm = lr.iloc[i - 26:i - 5].std(); s_now = lr.iloc[i - 5:i].std()
    Vn = g.volume.iloc[i - 26:i - 5].mean(); Vw = g.volume.iloc[i - 5:i].mean(); Vd = g.volume.iloc[i]
    PV = pv_anchor(g.index[i - 6]) * defl(t)
    PV2 = c_two(t) * dv.iloc[i - 26:i - 5].mean() * defl(t)
    row = {"date": t.date(), "cls": s["cls"], "fall %": round(100 * f, 2), "sigma_norm %": round(100 * s_norm, 3),
           "sigma_now %": round(100 * s_now, 3), "V_day/V_norm": round(Vd / Vn, 2), "PV 2005 $bn": round(PV / 1e9, 1), "PV proxy 2005 $bn": round(PV2 / 1e9, 1)}
    for Y, tag in ((Y_KO, ""), (Y_ALT, " (Y=0.9)")):
        row["F_sqrt" + tag] = (f / (Y * s_norm)) ** 2 * Vn / Vd
        row["F_now" + tag] = (f / (Y * s_now)) ** 2 * Vw / Vd
    for kk, tag in ((K, ""), (K - 2 * K_SE, " (k-2se)"), (K + 2 * K_SE, " (k+2se)")):
        row["F_lin" + tag] = 0.01 * f / ((kk / 1e4) * (PV / 40e6) ** (1 / 3) * (s_norm / 0.02) ** (4 / 3)) * Vn / Vd
    row["F_lin (proxy, 2 anchors)"] = 0.01 * f / ((K / 1e4) * (PV2 / 40e6) ** (1 / 3) * (s_norm / 0.02) ** (4 / 3)) * Vn / Vd
    for m, tag in ((3, " (PVx3)"), (1 / 3, " (PV/3)")):
        row["F_lin" + tag] = 0.01 * f / ((K / 1e4) * (m * PV / 40e6) ** (1 / 3) * (s_norm / 0.02) ** (4 / 3)) * Vn / Vd
    rows.append(row)
B = pd.DataFrame(rows)
B.to_csv(O / "days.csv", index=False)


def share(x, cond):
    v = cond(np.asarray(x)).astype(float); bs = [v[RNG.integers(0, len(v), len(v))].mean() for _ in range(10000)]
    return {"share": round(v.mean(), 3), "90% CI": [round(np.percentile(bs, 5), 3), round(np.percentile(bs, 95), 3)]}

HB = {"n days": len(B), "dates span": [str(B.date.min()), str(B.date.max())],
      "HB1 F_sqrt > 1": share(B.F_sqrt, lambda a: a > 1), "HB2 F_now > 1": share(B.F_now, lambda a: a > 1),
      "HB3 F_lin <= 0.25": share(B.F_lin, lambda a: a <= 0.25),
      "medians": {k: round(float(B[k].median()), 3) for k in B.columns if k.startswith("F_")},
      "sensitivity shares": {"F_sqrt>1 (Y=0.9)": round(float((B["F_sqrt (Y=0.9)"] > 1).mean()), 3),
                             "F_now>1 (Y=0.9)": round(float((B["F_now (Y=0.9)"] > 1).mean()), 3),
                             **{f"F_lin<=0.25{t}": round(float((B['F_lin' + t] <= 0.25).mean()), 3) for t in (" (k-2se)", " (k+2se)", " (PVx3)", " (PV/3)", " (proxy, 2 anchors)")}},
      "by M3 class (median F_now / share F_now>1 / median sigma_now/sigma_norm)": {
          cl: [round(float(gp.F_now.median()), 2), round(float((gp.F_now > 1).mean()), 2), round(float((gp["sigma_now %"] / gp["sigma_norm %"]).median()), 2), len(gp)]
          for cl, gp in B.groupby("cls")}}
HB["verdicts"] = {"HB1 (baseline)": bool(HB["HB1 F_sqrt > 1"]["share"] > 0.5), "HB2": bool(HB["HB2 F_now > 1"]["share"] > 0.5), "HB3": bool(HB["HB3 F_lin <= 0.25"]["share"] > 0.5)}
print(json.dumps(HB, indent=1))

# ---------- Part C ----------
ff = json.load(open(H.parent / "2026-11-06-forced-flows" / "out" / "ff.json"))
psi = {d["u"]: d["psi = sum L(L-1)A / V"] for d in ff["H-FF3 per underlying"]}
nov5 = {d["u"]: d for d in ff["Nov 5 decomposition"]}
sigd = {u: v["sigma %"] / 100 for u, v in ff["today's 15:30 rule: predicted 15:30->close % given the move so far"].items()}
gnow = defl("2026-07-01")
C = {"complex boundary": {}, "whole-market boundary": {}, "Nov 5 check (predicted close move % from the LETF flow vs actual 15:30->close)": {}}
Vu = {u: abs(nov5[u]["forced close rebalancing $bn"]) * 1e9 / (nov5[u]["as % of daily $ volume"] / 100) for u in ("SPX", "NDX", "SEMIS")}
beta = {u: nov5[u]["full-day move %"] / nov5["SPX"]["full-day move %"] for u in Vu}
for u in Vu:
    out = {}
    for x in (0.01, 0.03, 0.05):
        q = psi[u] * x
        out[f"x={int(100*x)}%"] = {"LETF sale % of complex volume": round(100 * q, 2),
                                   "LIN gain": round(lin(q, Vu[u] * gnow, sigd[u]) / x, 2), "SQRT gain": round(sqrt_(q, sigd[u]) / x, 2)}
    C["complex boundary"][u] = {"psi": round(psi[u], 3), "sigma %": round(100 * sigd[u], 2), "daily $vol $bn": round(Vu[u] / 1e9, 1), **out}
PVm = Vu["SPX"] * 1.82
sm = sigd["SPX"]
for x in (0.01, 0.03, 0.05):
    Qd = sum(psi[u] * Vu[u] * beta[u] * x for u in Vu)
    C["whole-market boundary"][f"S&P fall {int(100*x)}%"] = {"LETF sale $bn": round(Qd / 1e9, 1), "% of market volume": round(100 * Qd / PVm, 2),
                                                          "LIN gain": round(lin(Qd / PVm, PVm * gnow, sm) / x, 2), "SQRT gain": round(sqrt_(Qd / PVm, sm) / x, 2)}
C["whole-market boundary"]["assumptions"] = {"market $vol = SPX constituents x 1.82 ($bn)": round(PVm / 1e9, 0), "market sigma %": round(100 * sm, 2),
                                            "complex betas (Nov 5 moves / SPX)": {u: round(b, 2) for u, b in beta.items()}}
Qtot = sum(abs(nov5[u]["forced close rebalancing $bn"]) for u in Vu) * 1e9
for u in Vu:
    q = abs(nov5[u]["forced close rebalancing $bn"]) * 1e9 / Vu[u]
    C["Nov 5 check (predicted close move % from the LETF flow vs actual 15:30->close)"][u] = {
        "actual": nov5[u]["actual 15:30->close %"], "LIN complex": round(-100 * lin(q, Vu[u] * gnow, sigd[u]), 2),
        "SQRT complex": round(-100 * sqrt_(q, sigd[u]), 2)}
C["Nov 5 check (predicted close move % from the LETF flow vs actual 15:30->close)"]["whole market (3 complexes summed)"] = {
    "actual SPX": nov5["SPX"]["actual 15:30->close %"], "LIN market": round(-100 * lin(Qtot / PVm, PVm * gnow, sm), 2),
    "SQRT market": round(-100 * sqrt_(Qtot / PVm, sm), 2), "LETF sale % of market volume": round(100 * Qtot / PVm, 2)}
print(json.dumps(C, indent=1))

json.dump({"pre-registered at": "77fea8a", "Part A": A.to_dict(orient="records"), "Part B cross-check": crosscheck, "Part B": HB, "Part C": C,
           "constants": {"k": K, "k s.e.": K_SE, "Y (KO Eq.17)": round(Y_KO, 3), "Y alt": Y_ALT, "c (proxy scale)": c, "g 2026": round(gnow, 3)}},
          open(O / "crash.json", "w"), indent=1, default=str)
