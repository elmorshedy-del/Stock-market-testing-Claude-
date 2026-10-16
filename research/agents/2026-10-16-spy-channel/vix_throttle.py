"""Follow-up 2: VIX as the throttle. Verifies REPORT §4d's claim ("within high-VIX days P(elevator) runs 29% -> 5% from
low to high GEX; in low-VIX markets it is ~0 whatever GEX does"), which was stated without a script, using release.py's
own frame and outcome (next-10-day S&P return in its top decile). The VIX split is the sample's own terciles (2012+),
a choice made here after the fact and reported with the median split alongside. Then each touch of the owner's channel
and today are placed in their cell.
Usage: OMP_NUM_THREADS=1 python vix_throttle.py -> out/vix_throttle.csv, out/vix_throttle.png"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import spy_channel as S

sys.path.insert(0, str(S.MICRO))
os.chdir(S.MICRO)
from release import frame as rframe, gex_study    # noqa: E402  (originals, imported unchanged)
import established_rules as E                      # noqa: E402


def table():
    _, x = gex_study(rframe())
    x["elev"] = (x.fwd > x.fwd.quantile(0.9)).astype(float)
    x["gq"], gedges = pd.qcut(x.gex_pct, 5, labels=False, retbins=True)
    vcut = x.VIX.quantile([1 / 3, 2 / 3]).to_numpy()
    x["vt"] = np.digitize(x.VIX, vcut)
    rows = []
    for start, era in ((None, "2012+"), ("2019-10-01", "2019Q4+")):
        m = (x.index >= start) if start else np.ones(len(x), bool)
        for (g, v), s in x[m].groupby(["gq", "vt"]).elev:
            rows.append({"era": era, "GEX quintile": int(g), "VIX tercile": int(v), "P(top-decile 10-day rise)": s.mean(), "days": len(s)})
        med = x.VIX.median()
        for hi, s in x[m].groupby([x.gq[m], x.VIX[m] >= med]).elev:
            rows.append({"era": era + " median split", "GEX quintile": int(hi[0]), "VIX tercile": int(hi[1]), "P(top-decile 10-day rise)": s.mean(), "days": len(s)})
    return pd.DataFrame(rows), gedges, vcut, x


def place(gedges, vcut):
    f = E.build_fresh()
    D, L, spy, vix, dix, fits, cal = S.frame()
    T = S.touches(D)
    pts = []
    for _, t in T.iterrows():
        d = pd.Timestamp(t["first touch"])
        pts.append((f"{d:%b %d}", f.gex_pct.loc[d], f.VIX.loc[d], "upper line" if t["reached the upper line"] is not None else ("now" if t.ongoing else "stalled")))
    last = f.index[-1]
    pts.append((f"now ({last:%b %d})", f.gex_pct.loc[last], f.VIX.loc[last], "now"))
    out = []
    for lab, g, v, res in pts:
        gq = int(np.clip(np.searchsorted(gedges, g, side="right") - 1, 0, 4))
        out.append({"day": lab, "GEX pct": round(float(g), 2), "VIX": round(float(v), 1), "GEX quintile": gq, "VIX tercile": int(np.digitize(v, vcut)), "outcome": res})
    return pd.DataFrame(out)


def figure(Tb, P, gedges, vcut):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": S.MUTED, "axes.labelcolor": S.MUTED, "xtick.color": S.MUTED, "ytick.color": S.MUTED,
                         "figure.facecolor": S.SURF, "axes.facecolor": S.SURF, "axes.spines.top": False, "axes.spines.right": False})
    f, axs = plt.subplots(1, 2, figsize=(15, 5.8), gridspec_kw={"wspace": 0.12})
    vlab = [f"VIX < {vcut[0]:.1f}", f"VIX {vcut[0]:.1f}-{vcut[1]:.1f}", f"VIX > {vcut[1]:.1f}"]
    glab = [f"{gedges[i]:.2f}-{gedges[i + 1]:.2f}" for i in range(5)]
    for ax, era in zip(axs, ("2012+", "2019Q4+")):
        t = Tb[Tb.era == era].pivot(index="GEX quintile", columns="VIX tercile", values="P(top-decile 10-day rise)")
        n = Tb[Tb.era == era].pivot(index="GEX quintile", columns="VIX tercile", values="days")
        im = ax.imshow(100 * t.to_numpy(), cmap="Blues", vmin=0, vmax=35, aspect="auto", origin="lower")
        for i in range(5):
            for j in range(3):
                v, k = t.iloc[i, j] if j in t.columns else np.nan, n.iloc[i, j] if j in n.columns else 0
                if v == v:
                    ax.text(j, i + 0.2, f"{100 * v:.0f}%  ({int(k)} days)", ha="center", va="center", fontsize=8.5, color="white" if v > 0.2 else S.INK)
        ax.set_xticks(range(3), vlab)
        ax.set_yticks(range(5), [f"GEX pct {g}" for g in glab])
        ax.set_title(f"{era}: chance the next 10 days are a top-decile S&P rise (base 10%)", loc="left", fontsize=10, color=S.INK)
        if era == "2012+":
            for (gq, vt), grp in P.groupby(["GEX quintile", "VIX tercile"]):
                for k, (_, p) in enumerate(grp.iterrows()):
                    col = {"upper line": S.GREEN, "stalled": S.MUTED, "now": S.ORANGE}[p.outcome]
                    dx = (k - (len(grp) - 1) / 2) * 0.27
                    ax.scatter([vt + dx], [gq - 0.12], s=50, color=col, edgecolor=S.INK, lw=0.6, zorder=5)
                    ax.text(vt + dx, gq - 0.33, p.day.split(" (")[0], fontsize=7.5, color="white" if Tb.query("era == '2012+' and `GEX quintile` == @gq and `VIX tercile` == @vt")["P(top-decile 10-day rise)"].iloc[0] > 0.2 else S.INK, ha="center")
    axs[1].set_yticklabels([])
    f.suptitle("VIX is the throttle: low S&P gamma only turns into a sprint when VIX is up. Dots: touches of your lower line "
               "(green reached the upper line, grey stalled, orange now)", x=0.01, ha="left", fontsize=11, color=S.INK, weight="bold", y=1.0)
    f.savefig(S.OUT / "vix_throttle.png", dpi=145, bbox_inches="tight", facecolor=S.SURF)


if __name__ == "__main__":
    Tb, gedges, vcut, x = table()
    P = place(gedges, vcut)
    Tb.to_csv(S.OUT / "vix_throttle.csv", index=False)
    P.to_csv(S.OUT / "vix_throttle_touches.csv", index=False)
    figure(Tb, P, gedges, vcut)
    pd.set_option("display.width", 200)
    print("GEX quintile edges", np.round(gedges, 3), "| VIX terciles", np.round(vcut, 2), "| sample", x.index[0].date(), x.index[-1].date())
    for era in ("2012+", "2019Q4+", "2012+ median split"):
        print(era, "\n", (100 * Tb[Tb.era == era].pivot(index="GEX quintile", columns="VIX tercile", values="P(top-decile 10-day rise)")).round(1).to_string())
    print(P.to_string(index=False))
