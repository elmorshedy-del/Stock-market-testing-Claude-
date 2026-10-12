"""Does Google's TimesFM (2.5, 200M, zero-shot) add anything to this research? (REPORT 4ab)
Three jobs, each against the simple baseline it has to beat, scored only on origins after the model's
release (Oct 2025 onward), so its pretraining could not have seen the outcomes.
  1. direction  10-session return of TSLA / MSFT / SPY from 512 days of log prices   vs zero
  2. vol        mean |daily return| over the next 10 sessions from 512 days of |returns|
                vs the last 22 days' mean, a 1/5/22-day blend, and the options' own 30-day ATM IV
  3. release    will S&P dealer gamma (SqueezeMetrics percentile) reach its bottom third within
                10 sessions?  vs the historical frequency for today's level (fit on pre-Oct-2025 data)
Needs: torch (CPU) and timesfm in their own environment, e.g.
  python -m venv tfm_env && tfm_env/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu && tfm_env/bin/pip install timesfm pandas
Usage: tfm_env/bin/python timesfm_check.py
"""
import numpy as np
import pandas as pd
import timesfm

from common import DATA, OUT, load_bars

CTX, H, START = 512, 10, "2025-10-01"


def model():
    m = timesfm.TimesFM_2p5_200M_torch.from_pretrained("google/timesfm-2.5-200m-pytorch")
    m.compile(timesfm.ForecastConfig(max_context=CTX, max_horizon=16, normalize_inputs=True,
                                     use_continuous_quantile_head=True, fix_quantile_crossing=True))
    return m


def origins(idx):
    return [i for i in range(CTX, len(idx) - H) if idx[i] >= pd.Timestamp(START)]


def run(m, series, idx_list):
    pt, qs = [], []
    for k in range(0, len(idx_list), 64):
        batch = [series[i - CTX + 1:i + 1] for i in idx_list[k:k + 64]]
        p, q = m.forecast(horizon=H, inputs=batch)
        pt.append(p), qs.append(q)
    return np.concatenate(pt), np.concatenate(qs)


def auc(score, y):
    pos, neg = score[y == 1], score[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    return float(np.mean([(p > neg).mean() + 0.5 * (p == neg).mean() for p in pos]))


def direction(m):
    rows = []
    for sym in ("TSLA", "MSFT", "SPY"):
        c = load_bars(sym).close
        lc = np.log(c.to_numpy())
        io = origins(c.index)
        p, _ = run(m, lc, io)
        pred = p[:, -1] - lc[io]
        act = np.array([lc[i + H] - lc[i] for i in io])
        rows.append({"sym": sym, "origins": len(io), "corr(pred, actual)": np.corrcoef(pred, act)[0, 1],
                     "hit rate": np.mean(np.sign(pred) == np.sign(act)), "up share (always-long hit rate)": np.mean(act > 0),
                     "MAE timesfm %": 100 * np.abs(pred - act).mean(), "MAE zero %": 100 * np.abs(act).mean()})
    return pd.DataFrame(rows)


def vol(m):
    rows = []
    for sym in ("TSLA", "MSFT", "SPY"):
        c = load_bars(sym).close
        a = np.abs(np.r_[0.0, np.diff(np.log(c.to_numpy()))])
        io = origins(c.index)
        p, _ = run(m, a, io)
        pred = p.mean(axis=1)
        act = np.array([a[i + 1:i + 1 + H].mean() for i in io])
        last22 = np.array([a[i - 21:i + 1].mean() for i in io])
        har = np.array([(a[i] + a[i - 4:i + 1].mean() + a[i - 21:i + 1].mean()) / 3 for i in io])
        src = OUT / (f"mech_book_{sym}.csv" if sym == "SPY" else f"td_gamma_{sym}.csv")
        b = pd.read_csv(src, parse_dates=["date"]).set_index("date")
        iv = (b["atm_iv"] if sym == "SPY" else b["atm_iv_30d"]).reindex(c.index).ffill().to_numpy()
        ivp = iv[io] * np.sqrt(2 / np.pi) / np.sqrt(252)            # mean |daily return| implied by the option price
        r = {"sym": sym, "origins": len(io)}
        for lab, f in (("timesfm", pred), ("last 22 days", last22), ("1/5/22 blend", har), ("option IV", ivp)):
            r[f"corr {lab}"] = np.corrcoef(f, act)[0, 1]
            r[f"MAE {lab}"] = 100 * np.abs(f - act).mean()
        rows.append(r)
    return pd.DataFrame(rows)


def release(m):
    d = pd.read_csv(DATA / "DIX.csv", parse_dates=["date"]).set_index("date")
    g = d.gex.rolling(252).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True).dropna()
    v, idx = g.to_numpy(), g.index
    y = np.array([float(np.min(v[i + 1:i + 1 + H]) <= 1 / 3) if i + H < len(v) else np.nan for i in range(len(v))])
    io = origins(idx)
    _, q = run(m, v, io)
    # share of the model's quantile paths (10%..90%) whose minimum over the horizon reaches the bottom third
    score_t = (q[:, :, 1:].min(axis=1) <= 1 / 3).mean(axis=1)
    train = (idx < pd.Timestamp(START)) & ~np.isnan(y)
    bins = np.linspace(0, 1, 11)
    freq = pd.Series(y[train]).groupby(np.digitize(v[train], bins)).mean()
    score_b = freq.reindex(np.digitize(v[io], bins)).to_numpy()
    yy = y[io]
    ok = ~np.isnan(yy)
    out = {"origins": int(ok.sum()), "released share": yy[ok].mean()}
    for lab, s in (("timesfm", score_t), ("level frequency", score_b)):
        out[f"AUC {lab}"] = auc(s[ok], yy[ok])
        out[f"Brier {lab}"] = float(np.mean((s[ok] - yy[ok]) ** 2))
    _, qn = m.forecast(horizon=H, inputs=[v[-CTX:]])
    out["today: timesfm score"] = float((qn[0, :, 1:].min(axis=0) <= 1 / 3).mean())
    out["today: level frequency"] = float(freq.get(np.digitize(v[-1], bins), np.nan))
    out["today level"] = float(v[-1])
    return pd.Series(out)


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    m = model()
    print("1. direction, 10 sessions\n" + direction(m).round(3).to_string(index=False))
    print("\n2. volatility, mean |daily return| over the next 10 sessions (MAE in % points)\n" + vol(m).round(3).to_string(index=False))
    print("\n3. S&P gamma reaches its bottom third within 10 sessions\n" + release(m).round(3).to_string())
