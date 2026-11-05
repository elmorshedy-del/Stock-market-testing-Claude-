"""One-page figure for the two-day thesis. Usage: python figure.py <dl_dir> <label>"""
import sys, json, importlib.util, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
dl, label = sys.argv[1], sys.argv[2]; H = Path(__file__).resolve().parent; O = H / "out"
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
T = json.load(open(O / f"tests_{label}.json")); A4 = json.load(open(O / f"a4_{label}.json")); A2 = json.load(open(O / f"a2_{label}.json"))
X = pd.read_csv(O / f"cross_section_{label}.csv", index_col=0); Ad = pd.read_parquet(f"{dl}/daily_adj.parquet").sort_index(); Ad = Ad[~Ad.index.duplicated(keep="last")]; R = Ad.pct_change()
rest = X.index[X.b_AI < X.b_AI.quantile(0.70)]; ai10 = X.index[X.b_AI >= X.b_AI.quantile(0.90)]
days = [("Mon Nov 2\n(Iran talks)", "2026-11-02", "Mon Nov 2"), ("Tue Nov 3\n(election day)", "2026-11-03", "Tue Nov 3 (election day)"), ("Wed Nov 4\nDay 1", "2026-11-04", "Wed Nov 4 (Day 1)"), ("Thu Nov 5\nDay 2", "2026-11-05", "Thu Nov 5 (Day 2)")]
fig = plt.figure(figsize=(16, 11), dpi=150); gs = fig.add_gridspec(2, 2, hspace=0.36, wspace=0.22)
# A: four days
a = fig.add_subplot(gs[0, 0]); x = np.arange(4)
ai_load = [A4[f"C2 cross-section {k}"]["AI"][0] for _, _, k in days]
restr = [100 * R.loc[pd.Timestamp(d), rest].mean() for _, d, _ in days]; aidr = [100 * R.loc[pd.Timestamp(d), ai10].mean() for _, d, _ in days]; oil = [100 * R.loc[pd.Timestamp(d), "USO"] for _, d, _ in days]
a.bar(x - 0.27, aidr, 0.26, color="#c62828", label="AI suppliers (top 10% AI exposure), EW %")
a.bar(x, restr, 0.26, color="#2e7d32", label="rest of the S&P (bottom 70%), EW %")
a.bar(x + 0.27, oil, 0.26, color="#424242", alpha=0.75, label="oil (USO) %")
for i in range(4):
    for off, v in ((-0.27, aidr[i]), (0, restr[i]), (0.27, oil[i])): a.text(i + off, v + (0.3 if v >= 0 else -0.3), f"{v:+.1f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=7.5)
a.axhline(0, color="k", lw=0.8); a.set_xticks(x); a.set_xticklabels([d[0] for d in days], fontsize=9); a.set_ylabel("% move")
a.legend(frameon=False, fontsize=8, loc="lower left"); a.set_ylim(min(aidr + oil) - 3, max(restr + oil + [3]) + 2.5)
spr = [ai_ - re_ for ai_, re_ in zip(aidr, restr)]
a.text(0.99, 0.02, "AI minus rest: " + "  ".join(f"{v:+.1f}" for v in spr), transform=a.transAxes, ha="right", fontsize=8.5, fontweight="bold")
a.set_title("A. One seesaw, four days: AI and oil together, the rest opposite;\n    Thursday broke it (no oil cushion)", loc="left", fontweight="bold", fontsize=11)
# B: Day 1 anomaly scatter
b = fig.add_subplot(gs[0, 1]); px = pd.DataFrame({s: lc.yahoo(s, "2022-12-01").close for s in ("RSP", "SMH")}).dropna(); rr = px.pct_change().dropna()
hist = rr[(rr.index >= "2023-01-01") & (rr.index <= "2026-10-30")]
b.scatter(100 * hist.SMH, 100 * hist.RSP, s=6, color="#bdbdbd", alpha=0.6, label="every day 2023 → Oct 2026")
g = np.linspace(-12.5, 8, 100); rc = A2["B4 recent 2023-2026"]; s1, s2 = rc["slope above -4%"], rc["extra slope below -4%"]
yb = s1 * np.maximum(g / 100, -0.04) + s2 * np.minimum(g / 100 + 0.04, 0); b.plot(g, 100 * yb, color="#1565c0", lw=1.6, label="normal relationship (with tail)")
for lab, d, col in (("Mon Nov 2", "2026-11-02", "#ef6c00"), ("Day 1 (Wed)", "2026-11-04", "#2e7d32"), ("Day 2 (Thu)", "2026-11-05", "#c62828")):
    t = pd.Timestamp(d)
    if t in rr.index: b.scatter(100 * rr.SMH.loc[t], 100 * rr.RSP.loc[t], s=90, color=col, zorder=5, edgecolor="k"); b.annotate(lab, (100 * rr.SMH.loc[t], 100 * rr.RSP.loc[t]), xytext=(8, 4), textcoords="offset points", fontsize=9, fontweight="bold", color=col)
b.axhline(0, color="k", lw=0.6); b.axvline(0, color="k", lw=0.6); b.set_xlabel("chips (SMH) daily %"); b.set_ylabel("equal-weight S&P (RSP) daily %"); b.set_xlim(-12.5, 8); b.set_ylim(-6, 5)
z1, z2 = rc["Day1"]["z"], rc["Day2"]["z"]
b.text(0.02, 0.97, f"Day 1: z {z1:+.1f} (rare: the broad market rose while chips fell)\nDay 2: z {z2:+.1f} (ordinary for this chip drop in the 2023–26 regime)", transform=b.transAxes, va="top", fontsize=9, bbox=dict(fc="white", ec="#ccc"))
b.legend(frameon=False, fontsize=8, loc="lower right")
b.set_title("B. Day 1 was the anomaly; Day 2 was the rule", loc="left", fontweight="bold", fontsize=11)
# C: cross-section loadings
c = fig.add_subplot(gs[1, 0]); ks = ["AI", "OIL", "RATE", "MKT", "MOM"]; lab = {"AI": "AI-supplier\nexposure", "OIL": "oil\nexposure", "RATE": "bond (rates)\nexposure", "MKT": "market\nbeta", "MOM": "12-month\nwinners"}
d1 = T["D1 model B"]["coef % per 1 SD (t)"]; d2 = T["D2 model B"]["coef % per 1 SD (t)"]; xx = np.arange(len(ks))
c.bar(xx - 0.2, [d1[k][0] for k in ks], 0.38, color="#2e7d32", label=f"Day 1 (R² {T['D1 model B']['R2']:.2f})"); c.bar(xx + 0.2, [d2[k][0] for k in ks], 0.38, color="#c62828", label=f"Day 2 (R² {T['D2 model B']['R2']:.2f})")
for i, k in enumerate(ks):
    for off, v in ((-0.2, d1[k]), (0.2, d2[k])): c.text(i + off, v[0] + (0.08 if v[0] >= 0 else -0.08), f"t {v[1]:+.0f}", ha="center", va="bottom" if v[0] >= 0 else "top", fontsize=7.5)
c.axhline(0, color="k", lw=0.8); c.set_xticks(xx); c.set_xticklabels([lab[k] for k in ks], fontsize=9); c.set_ylabel("% return per 1 SD of exposure (500 stocks)")
c.legend(frameon=False, fontsize=8.5, loc="lower right")
c.set_title("C. Day 1: AI shock + oil/rates cushion. Day 2: AI shock + selling\n    by market beta and of crowded winners, no cushion", loc="left", fontweight="bold", fontsize=11)
# D: intraday Day 2
d = fig.add_subplot(gs[1, 1]); M5 = pd.read_parquet(f"{dl}/m5.parquet").reset_index(); M5 = M5[M5.ts.dt.date == pd.Timestamp("2026-11-05").date()]
M5 = M5[(M5.ts.dt.time >= pd.Timestamp("09:30").time()) & (M5.ts.dt.time < pd.Timestamp("16:00").time())].assign(ts=lambda q: q.ts.dt.floor("5min"))
Cc = M5.pivot_table(index="ts", columns="sym", values="close", aggfunc="last"); Oo = M5.pivot_table(index="ts", columns="sym", values="open", aggfunc="first").iloc[0]
pth = lambda nm: (Cc[[s for s in nm if s in Cc]].div(Oo[[s for s in nm if s in Cc]]) - 1).mean(axis=1)
P = pd.DataFrame({"AI_cum": pth(ai10), "rest_cum": pth(rest)}).dropna()
tt = [t.strftime("%H:%M") for t in P.index]; xi = np.arange(len(P))
d.plot(xi, 100 * P.AI_cum, color="#c62828", lw=2, label="AI suppliers (top 10%)"); d.plot(xi, 100 * P.rest_cum, color="#2e7d32", lw=2, label="rest of the S&P (bottom 70%)")
for col, ser in (("#c62828", P.AI_cum), ("#2e7d32", P.rest_cum)):
    i = int(np.argmin(ser.values)); d.scatter(i, 100 * ser.iloc[i], color=col, s=40, zorder=5); d.annotate(f"low {tt[i]}", (i, 100 * ser.iloc[i]), xytext=(5, -12), textcoords="offset points", fontsize=8.5, color=col)
tk = [i for i, t in enumerate(tt) if t.endswith(":00")]; d.set_xticks(tk); d.set_xticklabels([tt[i] for i in tk], fontsize=8.5); d.axhline(0, color="k", lw=0.6)
d.set_ylabel("% from the open (equal weight)"); d.legend(frameon=False, fontsize=8.5, loc="lower left")
d.set_title("D. Day 2 intraday: the rest sold as a basket 10:00–13:00, then stopped;\n    AI fell, bounced, and fell again into the close", loc="left", fontweight="bold", fontsize=11)
for ax in (a, b, c, d): ax.spines[["top", "right"]].set_visible(False)
two = lambda names: 100 * ((1 + R.loc[pd.Timestamp("2026-11-04"), names]) * (1 + R.loc[pd.Timestamp("2026-11-05"), names]) - 1).mean()
fig.suptitle(f"Same relative shock both days (AI build-out about −9% vs the rest); only the cushion changed. Two days net: AI {two(ai10):+.1f}%, rest of the S&P {two(rest):+.1f}%.", x=0.01, ha="left", fontsize=13, fontweight="bold")
fig.text(0.01, 0.005, f"Passed: H1 (Day-1 AI/oil/rates), H3 (crowded winners outside AI, Day 2), H4 (beta selling, Day 2), Day-1 anomaly (B1/B4), Day-2 basket co-movement 98th pct (B5), Monday same pattern (C2). Rejected: momentum crash (H2), reversal (H5), AI-first timing (H6, L), rotation-zone threshold (A3), AI war shelter (C1); funding leg suggestive (A5 p 0.065). Yahoo data; {label}.", fontsize=7.2, color="#555")
plt.savefig(O / f"two_day_thesis_{label}.png", bbox_inches="tight"); print("ok")
