"""Kronos zero-shot check on TSLA (README.md, pre-registered at d43d835). Copies the design of microstructure §4ab.
Stage 1 forecasts (slow, CPU) -> out/paths_<model>.csv.gz; stage 2 scores them -> out/kronos.json, out/kronos.png.
Needs the Kronos repo (git clone https://github.com/shiyu-coder/Kronos) and torch, einops, huggingface_hub, safetensors.
Usage: python kronos_check.py forecast <kronos_repo> <TSLA_10y.json> small|base
       python kronos_check.py score <TSLA_10y.json>"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
MICRO = HERE.parents[1] / "microstructure"
START, LAST, END = "2025-10-01", "2026-10-09", "2026-10-23"
CTX, H, K, BATCH = 400, 10, 8, 16
EVERY = {"small": 1, "base": 5}
NAMES = {"small": "NeoQuasar/Kronos-small", "base": "NeoQuasar/Kronos-base", "base_rest": "NeoQuasar/Kronos-base"}
NSHIFT, MINSHIFT, NBOOT, BLOCK = 1000, 20, 2000, 20
RNG = np.random.default_rng(20261024)
COLS = ["open", "high", "low", "close", "volume"]
BLUE, ORANGE, GREEN, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"


def bars(path):
    d = json.loads(Path(path).read_text())["chart"]["result"][0]
    q = d["indicators"]["quote"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None)
    b = pd.DataFrame({k: q[k] for k in COLS}, index=idx).dropna()
    b = b[~b.index.duplicated(keep="last")]
    return b[b.index <= END]


def forecast(repo, path, which):
    sys.path.insert(0, repo)
    import torch
    from model import Kronos, KronosPredictor, KronosTokenizer
    torch.manual_seed(20261024)
    torch.set_num_threads(4)
    p = KronosPredictor(Kronos.from_pretrained(NAMES[which]), KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base"),
                        device="cpu", max_context=512)
    b = bars(path)
    allo = [i for i in range(CTX, len(b)) if pd.Timestamp(START) <= b.index[i] <= pd.Timestamp(LAST)]
    if which == "base_rest":                                # Amendment 1: the origins Kronos-base has not seen
        io = [i for i in allo if i not in set(allo[::EVERY["base"]])]
    else:
        io = allo[::EVERY[which]]
        io.append(len(b) - 1)                               # today's forecast (Oct 23 close), descriptive only
    jobs = [(i, k) for i in io for k in range(K)]
    rows = []
    for s in range(0, len(jobs), BATCH):
        chunk = jobs[s:s + BATCH]
        dfs, xts, yts = [], [], []
        for i, _ in chunk:
            x = b.iloc[i - CTX + 1:i + 1]
            fut = b.index[i + 1:i + 1 + H]
            if len(fut) < H:
                fut = fut.append(pd.bdate_range(b.index[-1] + pd.Timedelta(days=1), periods=H - len(fut)))
            dfs.append(x[COLS]), xts.append(pd.Series(x.index)), yts.append(pd.Series(fut))
        out = p.predict_batch(dfs, xts, yts, pred_len=H, T=1.0, top_p=0.9, sample_count=1, verbose=False)
        for (i, k), o in zip(chunk, out):
            for h in range(H):
                rows.append((b.index[i], k, h + 1, *o.iloc[h][["open", "high", "low", "close"]].to_numpy()))
        print(f"{which}: {min(s + BATCH, len(jobs))}/{len(jobs)}", flush=True)
    P = pd.DataFrame(rows, columns=["origin", "path", "h", "open", "high", "low", "close"])
    P.to_csv(OUT / f"paths_{which}.csv.gz", index=False)


def shift_p(pred, act):
    obs = np.corrcoef(pred, act)[0, 1]
    n = len(pred)
    null = np.array([np.corrcoef(np.roll(pred, s), act)[0, 1] for s in RNG.integers(MINSHIFT, n - MINSHIFT, NSHIFT)])
    return float(obs), float((null >= obs).mean())


def block_boot_diff(a, b_, y):
    """P(corr(a, y) <= corr(b, y)) under a moving-block bootstrap of origins."""
    n = len(y)
    starts = np.arange(n - BLOCK + 1)
    d = np.empty(NBOOT)
    for j in range(NBOOT):
        idx = np.concatenate([np.arange(s, s + BLOCK) for s in RNG.choice(starts, int(np.ceil(n / BLOCK)))])[:n]
        d[j] = np.corrcoef(a[idx], y[idx])[0, 1] - np.corrcoef(b_[idx], y[idx])[0, 1]
    return float(np.mean(d)), float((d <= 0).mean())


def score_model(which, b, P=None):
    P = pd.read_csv(OUT / f"paths_{which}.csv.gz", parse_dates=["origin"]) if P is None else P
    P = P[P.origin <= LAST]
    c, lc = b.close, np.log(b.close)
    r = lc.diff().abs()
    g = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
    iv = g.atm_iv_30d.reindex(b.index).ffill()
    o = sorted(P.origin.unique())
    pos = np.array([b.index.get_loc(t) for t in o])
    res = {"origins": len(o)}
    for h in (5, 10):
        m = P[P.h == h].groupby("origin").close.mean().reindex(o).to_numpy()
        pred = np.log(m) - lc.iloc[pos].to_numpy()
        act = lc.iloc[pos + h].to_numpy() - lc.iloc[pos].to_numpy()
        cr, p = shift_p(pred, act)
        res[f"direction {h}d"] = {"corr": cr, "p_shift": p, "hit rate": float(np.mean(np.sign(pred) == np.sign(act))),
                                  "always-long hit rate": float(np.mean(act > 0)), "MAE kronos %": float(100 * np.abs(pred - act).mean()),
                                  "MAE zero %": float(100 * np.abs(act).mean()), "mean predicted %": float(100 * pred.mean())}
    # volatility: mean |log return| along each path (first step from the origin close), averaged over paths
    P = P.sort_values(["origin", "path", "h"])
    prev = P.groupby(["origin", "path"]).close.shift(1)
    P["prev"] = prev.fillna(P.origin.map(c))
    P["absr"] = np.abs(np.log(P.close / P.prev))
    pv = P.groupby(["origin", "path"]).absr.mean().groupby("origin").mean().reindex(o).to_numpy()
    av = np.array([r.iloc[i + 1:i + 1 + H].mean() for i in pos])
    l22 = np.array([r.iloc[i - 21:i + 1].mean() for i in pos])
    har = np.array([(r.iloc[i] + r.iloc[i - 4:i + 1].mean() + r.iloc[i - 21:i + 1].mean()) / 3 for i in pos])
    ivp = iv.iloc[pos].to_numpy() * np.sqrt(2 / np.pi) / np.sqrt(252)
    vol = {}
    for lab, f in (("kronos", pv), ("last 22 days", l22), ("1/5/22 blend", har), ("option IV", ivp)):
        vol[lab] = {"corr": float(np.corrcoef(f, av)[0, 1]), "MAE %": float(100 * np.abs(f - av).mean()), "mean %": float(100 * f.mean())}
    vol["realized mean %"] = float(100 * av.mean())
    vol["kronos minus option IV corr"], vol["p (bootstrap, kronos not better)"] = block_boot_diff(pv, ivp, av)
    res["volatility 10d"] = vol
    s1 = P[P.h == 1]
    pr = np.log(s1.high / s1.low).groupby(s1.origin).mean().reindex(o).to_numpy()
    rng = np.log(b.high / b.low)
    ar = rng.iloc[pos + 1].to_numpy()
    lr = np.array([rng.iloc[i - 21:i + 1].mean() for i in pos])
    res["next-day range"] = {"corr kronos": float(np.corrcoef(pr, ar)[0, 1]), "corr last 22 days": float(np.corrcoef(lr, ar)[0, 1]),
                             "mean predicted %": float(100 * pr.mean()), "mean realized %": float(100 * ar.mean())}
    return res


def today(which, b):
    P = pd.read_csv(OUT / f"paths_{which}.csv.gz", parse_dates=["origin"])
    P = P[P.origin == b.index[-1]]
    w = P.pivot(index="path", columns="h", values="close").to_numpy()
    return {"from": str(b.index[-1].date()), "close": float(b.close.iloc[-1]),
            "median": np.median(w, axis=0).round(2).tolist(), "p10": np.percentile(w, 10, axis=0).round(2).tolist(),
            "p90": np.percentile(w, 90, axis=0).round(2).tolist(), "paths": int(len(w))}


def figure(b, res, td):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
    f, (a, z) = plt.subplots(1, 2, figsize=(15, 5.6), gridspec_kw={"width_ratios": [1.15, 1], "wspace": 0.22})
    hist = b.close.iloc[-40:]
    x0 = np.arange(-len(hist) + 1, 1)
    a.plot(x0, hist, color=INK, lw=1.5)
    for which, col in (("small", BLUE), ("base", ORANGE)):
        t = td.get(which)
        if not t:
            continue
        xs = np.arange(0, 11)
        med = [t["close"]] + t["median"]
        a.fill_between(xs, [t["close"]] + t["p10"], [t["close"]] + t["p90"], color=col, alpha=0.15, lw=0)
        a.plot(xs, med, color=col, lw=2)
        a.text(10.3, med[-1], f"Kronos-{which}: ${med[-1]:.0f}\n(10-90%: ${t['p10'][-1]:.0f}-{t['p90'][-1]:.0f})", fontsize=8.5, color=INK, va="center")
    a.axvline(0, color=GRID, lw=6, zorder=0)
    a.set_xlim(-40, 16)
    a.set_xlabel("sessions from the Oct 23 close")
    a.set_ylabel("TSLA")
    a.set_title(f"What Kronos forecasts from the Oct 23 close (${b.close.iloc[-1]:.2f}), {td['small']['paths']} sampled paths per model\n"
                "Read it with the test on the right: a forecast is only as good as its record", loc="left", fontsize=9.5, color=INK)
    s = res["small"]
    sb = res.get("base, all 258 origins (descriptive)")
    bv = []
    if sb:
        bv = [sb["direction 10d"]["corr"], sb["direction 5d"]["corr"], sb["direction 10d"]["hit rate"] - sb["direction 10d"]["always-long hit rate"],
              sb["volatility 10d"]["kronos"]["corr"], sb["next-day range"]["corr kronos"]]
    labels, kv, base = [], [], []
    for lab, k, bb in (("10-day direction\ncorrelation", s["direction 10d"]["corr"], 0.0),
                       ("5-day direction\ncorrelation", s["direction 5d"]["corr"], 0.0),
                       ("10-day hit rate\nminus always-long", s["direction 10d"]["hit rate"] - s["direction 10d"]["always-long hit rate"], 0.0),
                       ("10-day vol: correlation\n(baseline = option IV)", s["volatility 10d"]["kronos"]["corr"], s["volatility 10d"]["option IV"]["corr"]),
                       ("next-day range: correlation\n(baseline = last 22 days)", s["next-day range"]["corr kronos"], s["next-day range"]["corr last 22 days"])):
        labels.append(lab), kv.append(k), base.append(bb)
    y = np.arange(len(labels))[::-1]
    series = [(0.27, kv, BLUE, "Kronos-small (pre-registered)")] + ([(0.0, bv, ORANGE, "Kronos-base, all 258 origins")] if bv else []) + [(-0.27, base, MUTED, "baseline to beat")]
    for off, vals, col, lab in series:
        z.barh(y + off, vals, height=0.25, color=col, alpha=0.6 if col == MUTED else 1, label=lab)
        for yy, v in zip(y, vals):
            z.text(v + (0.008 if v >= 0 else -0.008), yy + off, f"{v:+.2f}", va="center", ha="left" if v >= 0 else "right", fontsize=7.5, color=INK)
    z.axvline(0, color=INK, lw=0.8)
    z.set_yticks(y, labels)
    z.legend(loc="upper left", bbox_to_anchor=(0.0, -0.07), ncol=3, frameon=False, fontsize=8)
    lo = min(min(kv), min(base), min(bv or [0]), 0) - 0.12
    hi = max(max(kv), max(base), max(bv or [0]), 0) + 0.22
    z.set_xlim(lo, hi)
    d10, v10 = s["direction 10d"], s["volatility 10d"]
    z.set_title(f"The test: {s['origins']} daily origins, Oct 2025 - Oct 2026 (after Kronos was released)\n"
                f"Kronos-small: 10-day direction p {d10['p_shift']:.2f} (shift null); vol vs option IV p {v10['p (bootstrap, kronos not better)']:.2f}",
                loc="left", fontsize=9.5, color=INK)
    c = res.get("amendment 1: Kronos-base on its 206 unseen origins")
    ph = res.get("post-hoc (not pre-registered): Kronos-base vs momentum / moving-average features")
    if c and ph:
        z.text(0.02, -0.16, f"Kronos-base, 206 unseen origins (Amendment 1): 10-day hit rate {100 * c['hit rate']:.0f}% vs {100 * c['always-long hit rate']:.0f}% always-long "
               f"(p {c['p hit (shift)']:.3f}), correlation {c['corr']:+.2f} (p {c['p corr (shift)']:.3f}): passes.\n"
               f"But after five plain momentum / moving-average distance features its partial correlation is {ph['partial corr after the 5 features']:+.2f} (p {ph['p (shift)']:.2f}): "
               "it mostly re-learns\nthe pull back toward the 50-day average, which worked this year (one year is the only clean test period).",
               transform=z.transAxes, fontsize=8.3, color=INK, va="top")
    f.savefig(OUT / "kronos.png", dpi=140, bbox_inches="tight", facecolor=SURF)


def confirm(b):
    """Amendment 1: Kronos-base on its 206 unseen origins."""
    P = pd.read_csv(OUT / "paths_base_rest.csv.gz", parse_dates=["origin"])
    lc = np.log(b.close)
    m = P[P.h == H].groupby("origin").close.mean()
    pos = np.array([b.index.get_loc(t) for t in m.index])
    pred = np.log(m.to_numpy()) - lc.iloc[pos].to_numpy()
    act = lc.iloc[pos + H].to_numpy() - lc.iloc[pos].to_numpy()
    n = len(pred)
    hit = lambda x: np.mean(np.sign(x) == np.sign(act))
    shifts = RNG.integers(10, n - 10, NSHIFT)
    nh = np.array([hit(np.roll(pred, s)) for s in shifts])
    nc = np.array([np.corrcoef(np.roll(pred, s), act)[0, 1] for s in shifts])
    cr = float(np.corrcoef(pred, act)[0, 1])
    out = {"origins": n, "hit rate": float(hit(pred)), "always-long hit rate": float(np.mean(act > 0)),
           "p hit (shift)": float((nh >= hit(pred)).mean()), "corr": cr, "p corr (shift)": float((nc >= cr).mean()),
           "share predicted down": float(np.mean(pred < 0)), "mean predicted %": float(100 * pred.mean())}
    up = pred > np.median(pred)
    out["realized when forecast in top half %"], out["realized when forecast in bottom half %"] = float(100 * act[up].mean()), float(100 * act[~up].mean())
    out["verdict"] = "pass" if (out["hit rate"] > out["always-long hit rate"] and out["p hit (shift)"] < 0.05 and cr > 0 and out["p corr (shift)"] < 0.05) else "fail"
    return out


def posthoc(b):
    """Not pre-registered: is Kronos-base's 10-day signal more than plain momentum / moving-average distance?"""
    P = pd.concat([pd.read_csv(OUT / f"paths_{w}.csv.gz", parse_dates=["origin"]) for w in ("base", "base_rest")])
    m = P[(P.h == H) & (P.origin <= LAST)].groupby("origin").close.mean().sort_index()
    lc = np.log(b.close)
    pos = np.array([b.index.get_loc(t) for t in m.index])
    pred = np.log(m.to_numpy()) - lc.iloc[pos].to_numpy()
    act = lc.iloc[pos + H].to_numpy() - lc.iloc[pos].to_numpy()
    feats = {f"past {n}d return": lc.iloc[pos].to_numpy() - lc.iloc[pos - n].to_numpy() for n in (5, 10, 20)}
    for n in (20, 50):
        feats[f"close vs {n}d average"] = lc.iloc[pos].to_numpy() - np.log(b.close.rolling(n).mean().iloc[pos].to_numpy())
    X = np.column_stack([np.ones(len(act))] + list(feats.values()))
    res = lambda y: y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
    rp, ra = res(pred), res(act)
    obs = float(np.corrcoef(rp, ra)[0, 1])
    rng = np.random.default_rng(3)
    null = np.array([np.corrcoef(np.roll(rp, s), ra)[0, 1] for s in rng.integers(10, len(rp) - 10, NSHIFT)])
    out = {"origins": len(pred), "partial corr after the 5 features": obs, "p (shift)": float((null >= obs).mean())}
    for k, v in feats.items():
        out[f"corr(base forecast, {k})"] = float(np.corrcoef(v, pred)[0, 1])
        out[f"corr({k}, outcome)"] = float(np.corrcoef(v, act)[0, 1])
    out["50d-average reversal rule hit rate"] = float(np.mean(np.sign(-feats["close vs 50d average"]) == np.sign(act)))
    q = pd.DataFrame({"p": pred, "a": act}, index=m.index).groupby(m.index.to_period("Q"))
    out["by quarter"] = {str(k): {"n": len(d), "hit rate": float(np.mean(np.sign(d.p) == np.sign(d.a))), "corr": float(np.corrcoef(d.p, d.a)[0, 1])}
                         for k, d in q if len(d) > 10}
    return out


def score(path):
    b = bars(path)
    res, td = {}, {}
    for which in ("small", "base"):
        if (OUT / f"paths_{which}.csv.gz").exists():
            res[which] = score_model(which, b)
            td[which] = today(which, b)
    d = res["small"]["direction 10d"]
    v = res["small"]["volatility 10d"]
    res["verdict (pre-registered)"] = {
        "direction": "pass" if (d["p_shift"] < 0.05 and d["hit rate"] > d["always-long hit rate"]) else "fail",
        "volatility": "pass" if v["p (bootstrap, kronos not better)"] < 0.05 else "fail"}
    res["today"] = td
    if (OUT / "paths_base_rest.csv.gz").exists():
        res["amendment 1: Kronos-base on its 206 unseen origins"] = confirm(b)
        allb = pd.concat([pd.read_csv(OUT / f"paths_{w}.csv.gz", parse_dates=["origin"]) for w in ("base", "base_rest")])
        res["base, all 258 origins (descriptive)"] = score_model("base", b, allb)
        res["post-hoc (not pre-registered): Kronos-base vs momentum / moving-average features"] = posthoc(b)
    (OUT / "kronos.json").write_text(json.dumps(res, indent=1))
    figure(b, res, td)
    return res


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    if sys.argv[1] == "forecast":
        forecast(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(json.dumps(score(sys.argv[2]), indent=1))
