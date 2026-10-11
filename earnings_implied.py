"""Implied vs realized earnings moves for Tesla reports, from DoltHub's free
end-of-day option chains (post-no-preference/options: bid/ask/IV per contract,
no open interest).

DoltHub keeps only expiries ~2+ weeks out, so the earnings-day move is backed out
of the term structure of the first two expiries after the report (both contain
the event): base variance b^2 = (s2^2*T2 - s1^2*T1)/(T2 - T1), event variance
E = s1^2*T1 - b^2*T1 (T in trading days / 252). Implied |move| = sqrt(E)*sqrt(2/pi).
ATM = the strike where call - put mid is smallest (spot from put-call parity;
DoltHub strikes are unadjusted for splits, ratios are not).

Usage: python earnings_implied.py
"""
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
from scipy.stats import binom

from common import DATA, load_bars
from tsla_eras import REACTIONS_2020

API = "https://www.dolthub.com/api/v1alpha1/post-no-preference/options/master?"
CACHE = DATA / "dolt"


def query(sql, key):
    path = CACHE / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text())
    CACHE.mkdir(parents=True, exist_ok=True)
    req = Request(API + urlencode({"q": sql}), headers={"User-Agent": "Mozilla/5.0"})
    rows = json.loads(urlopen(req, timeout=120).read())["rows"]
    if rows:
        path.write_text(json.dumps(rows))
    return rows


def chain(sym, day, max_days=60):
    end = (pd.Timestamp(day) + pd.Timedelta(days=max_days)).date()
    rows = query(f"SELECT date, expiration, strike, call_put, bid, ask, vol FROM option_chain WHERE act_symbol='{sym}' "
                 f"AND date='{day}' AND expiration <= '{end}'", f"{sym}_{day}_{max_days}")
    d = pd.DataFrame(rows)
    if d.empty:
        return d
    for c in ("strike", "bid", "ask", "vol"):
        d[c] = pd.to_numeric(d[c])
    d["expiration"] = pd.to_datetime(d.expiration)
    d["mid"] = (d.bid + d.ask) / 2
    return d


def straddle(d, exp):
    g = d[d.expiration == exp].pivot_table(index="strike", columns="call_put", values=["mid", "vol"])
    g = g.dropna()
    if g.empty:
        return np.nan, np.nan, np.nan
    par = g[("mid", "Call")] - g[("mid", "Put")]                # C - P ~ S - K near expiry
    k = (par.abs()).idxmin()
    spot = k + par[k]
    return g.loc[k, ("mid", "Call")] + g.loc[k, ("mid", "Put")], spot, g.loc[k, ("vol", "Call")] / 2 + g.loc[k, ("vol", "Put")] / 2


def event_move(d, asof, day0):
    exps = sorted(d.expiration[d.expiration >= pd.Timestamp(day0)].unique())[:2]
    if len(exps) < 2:
        return {}
    pts = []
    for exp in exps:
        px, spot, iv = straddle(d, exp)
        T = np.busday_count(pd.Timestamp(asof).date(), pd.Timestamp(exp).date()) / 252
        pts.append((pd.Timestamp(exp).date(), iv, T, spot))
    (e1, s1, T1, spot), (e2, s2, T2, _) = pts
    b2 = (s2 ** 2 * T2 - s1 ** 2 * T1) / (T2 - T1)
    E = s1 ** 2 * T1 - b2 * T1
    return {"expiries": f"{e1}/{e2}", "spot": spot, "iv1": s1, "iv2": s2, "base_iv": np.sqrt(max(b2, 0)),
            "implied_pct": 100 * np.sqrt(max(E, 0)) * np.sqrt(2 / np.pi)}


def past_reports(sym="TSLA", reactions=REACTIONS_2020):
    c = load_bars(sym).close
    rows = []
    for rx in reactions:
        i = c.index.searchsorted(pd.Timestamp(rx))
        if i >= len(c):
            continue
        eve, day0 = c.index[i - 1], c.index[i]
        d = chain(sym, eve.date())
        row = {"reaction": day0.date(), "eve": eve.date()}
        if not d.empty:
            row.update(event_move(d, eve.date(), day0))
        actual = np.log(c.iloc[i] / c.iloc[i - 1])
        row.update({"actual_pct": 100 * actual, "next10_pct": 100 * np.log(c.iloc[min(i + 10, len(c) - 1)] / c.iloc[i])})
        rows.append(row)
    e = pd.DataFrame(rows)
    e["ratio"] = e.actual_pct.abs() / e.implied_pct
    return e


def upcoming(sym, asof, reaction_day):
    return event_move(chain(sym, asof), asof, reaction_day)


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    e = past_reports()
    print(e.drop(columns=["spot"]).round(2).to_string(index=False))
    ok = e.dropna(subset=["ratio"])
    k = int((ok.ratio > 1).sum())
    print(f"\nreports {len(ok)}: mean implied {ok.implied_pct.mean():.1f}%, mean |actual| {ok.actual_pct.abs().mean():.1f}%, "
          f"median actual/implied {ok.ratio.median():.2f}; moved MORE than implied {k}/{len(ok)} "
          f"(p vs 50% = {binom.sf(k - 1, len(ok), 0.5):.2f})")
    print(f"   when the move beat the implied: next 10d continued in the same direction "
          f"{(np.sign(ok[ok.ratio > 1].actual_pct) == np.sign(ok[ok.ratio > 1].next10_pct)).mean():.0%}; "
          f"when it fell short: {(np.sign(ok[ok.ratio <= 1].actual_pct) == np.sign(ok[ok.ratio <= 1].next10_pct)).mean():.0%}")
    up = upcoming("TSLA", "2026-10-09", "2026-10-22")
    print(f"\nNEXT REPORT (Oct 21 after close -> Oct 22), as of 2026-10-09: implied earnings-day |move| "
          f"{up.get('implied_pct', np.nan):.1f}% (expiries {up.get('expiries')}, base IV {up.get('base_iv', np.nan):.2f}); "
          f"history: actual/implied median {ok.ratio.median():.2f}")
