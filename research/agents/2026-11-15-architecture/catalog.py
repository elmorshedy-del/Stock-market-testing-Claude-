"""New architecture (2026-11-15): every study since 2026-10-02 refiled under the decision question it informs.
Source of truth for CATALOG.md and the knowledge-map figure. Classification is the auditor's reading of each logged verdict.
book: SIZE LEVEL DIR TIME PRICE EXIT RISK | DESK THEORY BUILD
mech: POS positioning | FLOW flow & liquidity | FORCED forced flows, events & gaps | VOL volatility dynamics | HIST price history & sentiment | MACRO macro, politics, single-stock stories
ev:   R robust | L lean | N null | D no test
next: rule (in the playbook; forward-log) | refine (one better test; note says how) | park (needs data or more events) | close (do not revisit) | ref (reference)"""
import json, re
from pathlib import Path
H = Path(__file__).resolve().parent; AG = H.parent
BOOKS = {"SIZE": "1. How big will the next move be?", "LEVEL": "2. Where does it stall, turn or speed up?", "DIR": "3. Which way?",
         "TIME": "4. When does it start, and how long does it last?", "PRICE": "5. Is the option cheap or dear for that? Which structure?",
         "EXIT": "6. When to get out?", "RISK": "7. What breaks it?", "DESK": "Live desk and reviews", "THEORY": "Theory library", "BUILD": "Tools, data and method"}
MECH = {"POS": "positioning", "FLOW": "flow & liquidity", "FORCED": "forced flows, events, gaps", "VOL": "volatility dynamics", "HIST": "price history & sentiment",
        "MACRO": "macro, politics, stock stories", "-": ""}
# (id, book, mech, ev, next, note-on-next, manual result or None)
A = [
 ("2026-10-15-channel-reversion-macro", "LEVEL", "HIST", "N", "close", "", "Monthly channels: a fall from the top to the lower line is not beyond a random walk; none of 13 macro variables passes"),
 ("2026-10-15-channel-reversion-round2", "LEVEL", "HIST", "N", "close", "", "Nothing passes on 93 fresh stocks or the S&P since 1928; distance in volatility units beats channel position"),
 ("2026-10-15-sp-multivariate", "RISK", "HIST", "L", "park", "momentum/RSI flags 10% corrections (AUC 0.68); watch forward only", None),
 ("2026-10-16-dealer-sign", "SIZE", "POS", "R", "rule", "", "Call gamma damps the next day's range (TSLA, MSFT, NVDA, SPY, QQQ); put gamma amplifies it in SPY/QQQ"),
 ("2026-10-16-flip-during-bursts", "TIME", "POS", "D", "ref", "", None),
 ("2026-10-16-gaps-and-walls", "LEVEL", "POS", "N", "close", "", "TSLA opens, highs and lows land on top open-interest strikes no more than on equally round strikes"),
 ("2026-10-16-named-moves-gamma", "DIR", "POS", "D", "ref", "", None),
 ("2026-10-16-owner-channel-gamma", "LEVEL", "HIST", "D", "ref", "", "The owner's TSLA channel tracks its gamma state; lines are drawn in hindsight (descriptive)"),
 ("2026-10-16-pierce-and-reclaim", "DIR", "POS", "N", "close", "the full setup itself reproduced (39% vs 17%)", "Dipping below the flip and closing back above it is not the full setup (23% up vs 28% down)"),
 ("2026-10-16-spcx-tsla-lead-lag", "DIR", "MACRO", "N", "close", "", None),
 ("2026-10-16-spy-channel", "LEVEL", "HIST", "D", "ref", "", "The owner's SPY channel tracks the S&P gamma cycle (descriptive)"),
 ("2026-10-16-spy-intraday-levels", "DIR", "FLOW", "L", "park", "one day; needs signed option trades (TODO T1)", "Signed 0DTE option flow led SPY's next 5 minutes on one day (p 0.027); turns no closer to option levels than to round strikes"),
 ("2026-10-16-spy-intraday-multiday", "DIR", "FLOW", "D", "park", "not run; moved to another thread", None),
 ("2026-10-16-technical-indicators", "DIR", "HIST", "L", "rule", "keep only the RSI washout; the rest is closed", "TSLA RSI in its bottom tenth → up-burst within 10 sessions 57% vs 40% (p 0.001); 143 of 144 other indicator statistics fail"),
 ("2026-10-17-channel-microstructure", "LEVEL", "HIST", "N", "close", "", None),
 ("2026-10-24-forced-flow", "EXIT", "FORCED", "R", "rule", "", "Moves made on low dealer-gamma days are given back (−18% in 10 sessions); high-gamma moves extend (+8%). p 0.002, both halves, 5 of 6 tickers"),
 ("2026-10-24-kronos-tsla", "DIR", "HIST", "L", "close", "mostly 50-day reversion", None),
 ("2026-10-24-spx-year-analogs", "DIR", "HIST", "N", "close", "", None),
 ("2026-10-25-aapl-decoupling", "RISK", "HIST", "N", "close", "", None),
 ("2026-10-25-aapl-quirks", "DIR", "MACRO", "L", "close", "not something the owner trades", None),
 ("2026-10-25-channel-correction-theory", "TIME", "HIST", "N", "close", "breadth separator was best-of-26; its live call failed Nov 5", None),
 ("2026-10-25-intraday-hours", "TIME", "HIST", "L", "close", "", None),
 ("2026-10-25-momentum-reversal", "DIR", "HIST", "L", "close", "real but about 1 bp/week net", None),
 ("2026-10-25-order-flow", "DIR", "FLOW", "N", "park", "minute-bar signing was backwards; needs trade-level data (T1)", None),
 ("2026-10-25-spy-channel-reversion", "TIME", "HIST", "N", "close", "", None),
 ("2026-10-25-spy-gamma-levels", "LEVEL", "POS", "N", "ref", "the map is used daily", "The SPY levels map (flip, walls, pocket); the flip does not separate bought dips from corrections (AUC 0.47)"),
 ("2026-10-26-ladder-status", "DESK", "-", "D", "ref", "", None),
 ("2026-10-26-positioning-tests", "LEVEL", "POS", "R", "rule", "", "Day highs stall just under round numbers and lows just above (p 2e-15); the correlation rule holds only in true short gamma"),
 ("2026-10-26-tsla-gap-states", "DIR", "FORCED", "L", "park", "", None),
 ("2026-10-27-flip-wicks", "LEVEL", "POS", "L", "rule", "weak", "The pre-open flip is a stall level (highs stop there 42% vs 38%; joint p < 0.002), but the primary test failed; no closing pin"),
 ("2026-10-27-flow-physics", "DIR", "FLOW", "L", "refine", "feeds the liquidity pilot; the closing-imbalance feed costs about $20", "Closing imbalance predicts the last 10 minutes (ρ 0.37); SPY looked liquidity-led, TSLA flow-led (16 days)"),
 ("2026-10-27-live-read", "DESK", "-", "D", "ref", "", None),
 ("2026-10-28-gap-teardown", "DIR", "FORCED", "N", "close", "", None),
 ("2026-10-28-live-read", "DESK", "-", "D", "ref", "", None),
 ("2026-10-28-open-fade", "EXIT", "FORCED", "N", "close", "", None),
 ("2026-10-28-tsla-freed-dpi", "SIZE", "POS", "D", "ref", "", None),
 ("2026-10-29-calendar-mechanics", "EXIT", "FORCED", "R", "rule", "", "Earnings-reaction gap-ups fade in the first hour (−0.31σ; violent fades 25% vs 15%), confirmed out of sample (Holm 0.031)"),
 ("2026-10-29-gap-context", "EXIT", "FORCED", "N", "close", "", None),
 ("2026-10-29-house-of-cards", "EXIT", "FORCED", "N", "close", "replaced by forced-flow's gamma definition, which is robust", None),
 ("2026-10-30-live-read", "DESK", "-", "D", "ref", "", None),
 ("2026-10-30-permanence", "EXIT", "FORCED", "N", "close", "one lead (call-skew richening, ρ −0.20) is parked", None),
 ("2026-10-31-week-review", "DESK", "-", "D", "ref", "", None),
 ("2026-11-01-friday-narrative", "SIZE", "FLOW", "L", "ref", "one day; a template for case studies", None),
 ("2026-11-01-gamma-phase-diagram", "LEVEL", "POS", "R", "rule", "", "The prior day's call wall is a soft ceiling (the high stops there 43% vs 31%; QQQ too); distance to the flip scales the move (z ≈ 7)"),
 ("2026-11-01-informed-flow", "DIR", "FLOW", "N", "close", "", None),
 ("2026-11-01-july-october-forensics", "TIME", "HIST", "N", "close", "", None),
 ("2026-11-01-july-october-machine", "DIR", "HIST", "D", "close", "score its forecasts once (MC1)", None),
 ("2026-11-01-rsi-gamma-precedents", "SIZE", "POS", "D", "ref", "", None),
 ("2026-11-01-wall-short", "PRICE", "POS", "N", "refine", "shorting shares failed; the option version (sell a call spread at the wall, GW5) is untested", None),
 ("2026-11-01-yearend-forecast", "DIR", "HIST", "D", "rule", "base rates only; scoring continues Nov 30 and Dec 31", None),
 ("2026-11-02-election-vol", "PRICE", "MACRO", "L", "close", "event passed; score EV1 once", None),
 ("2026-11-02-hft-papers", "THEORY", "-", "D", "ref", "", None),
 ("2026-11-02-live-read", "DESK", "-", "D", "ref", "", None),
 ("2026-11-02-note-check", "DESK", "-", "D", "ref", "", None),
 ("2026-11-02-orb-gamma", "PRICE", "HIST", "L", "rule", "forward paper log only (OG2); no more backtests", "5-minute opening-range breakout: fails on SPY; TSLA passes out of sample (+29.5 bp/day, p 0.018); no exit rule improves it"),
 ("2026-11-02-polymarket-fed", "DIR", "MACRO", "L", "close", "", None),
 ("2026-11-02-tsla-breaking-point", "EXIT", "POS", "N", "park", "composite top score (BP1) not built", None),
 ("2026-11-02-tsla-options-signal", "DIR", "POS", "N", "close", "", None),
 ("2026-11-02-tsla-politics", "DIR", "MACRO", "N", "close", "score TP1 once", None),
 ("2026-11-02-tsla-wall-flow", "LEVEL", "POS", "D", "ref", "", None),
 ("2026-11-04-deferred-days", "DIR", "FLOW", "L", "ref", "closing imbalance confirmed on a second day; exhaustion from bars failed again", None),
 ("2026-11-04-msft-read", "DESK", "-", "D", "ref", "", None),
 ("2026-11-04-post-election-map", "DESK", "-", "D", "ref", "", None),
 ("2026-11-05-2000-lens", "RISK", "HIST", "D", "close", "", None),
 ("2026-11-05-ai-rotation", "TIME", "MACRO", "D", "ref", "", None),
 ("2026-11-05-channel-physics", "LEVEL", "HIST", "N", "close", "", None),
 ("2026-11-05-channels-deep", "LEVEL", "HIST", "N", "close", "", None),
 ("2026-11-05-liquidity-cycle", "SIZE", "FLOW", "N", "refine", "a daily proxy failed; needs real depth and trades (liquidity pilot)", None),
 ("2026-11-05-macro-trigger", "SIZE", "MACRO", "L", "refine", "re-pose as a pricing test: is the release-day implied move too low when gamma is low?", "Low gamma makes the S&P's reaction per unit of data surprise bigger (Holm 0.047); relief asymmetry and follow-through fail"),
 ("2026-11-05-november-cycle", "DIR", "HIST", "L", "close", "", None),
 ("2026-11-05-regime-compare", "RISK", "HIST", "D", "close", "", None),
 ("2026-11-05-speed-extremes", "TIME", "VOL", "N", "close", "", None),
 ("2026-11-05-two-day-thesis", "RISK", "MACRO", "L", "ref", "", None),
 ("2026-11-05-unwind-low", "TIME", "VOL", "N", "close", "", None),
 ("2026-11-06-aftershocks", "SIZE", "VOL", "R", "rule", "the volatility clock; scoring continues Dec 7 and Feb 5", "Big-move days cluster: each triggers 0.87–0.95 more; about 9 in 10 big days are aftershocks"),
 ("2026-11-06-crash-law", "RISK", "FLOW", "R", "refine", "its Part D is the liquidity pilot", "Normal-liquidity impact cannot make an index crash (needs more selling than the day's volume on 54 of 54 days); the response to selling must jump"),
 ("2026-11-06-forced-flows", "DIR", "FORCED", "N", "close", "", None),
 ("2026-11-06-liquidity-landscape", "LEVEL", "FLOW", "D", "refine", "a plan only; becomes the liquidity pilot", None),
 ("2026-11-06-literature-laws", "THEORY", "-", "D", "ref", "", None),
 ("2026-11-06-paper-unified-flow", "THEORY", "-", "D", "ref", "", None),
 ("2026-11-06-signature-test", "TIME", "VOL", "L", "close", "its live forecast is scored around March 2027", None),
]
F = [  # founding report, research/microstructure/REPORT.md
 ("§1 computing the lines", "BUILD", "-", "D", "ref", "", "Channel lines drawn by an algorithm"),
 ("§2 why channels look respected", "LEVEL", "HIST", "D", "ref", "", "The lower line is roughly the 50-day average drawn as a straight line"),
 ("§3 do lines matter beyond chance", "LEVEL", "HIST", "N", "close", "", "Across 40 stocks and about 2,000 touches, rejection at lines is within random-path noise"),
 ("§4 predicting breakouts", "LEVEL", "HIST", "L", "close", "later channel tests found no tradable edge", "Walk-forward model, out-of-sample AUC 0.62: counter-trend lines break 62%, with-trend 46%"),
 ("§4b level hopping", "LEVEL", "HIST", "N", "close", "it said on Oct 2 that the options edge is realized vs implied volatility; never followed up", "Levels carry almost no information beyond volatility"),
 ("§4c MSFT's two up-weeks", "DESK", "-", "D", "ref", "", ""),
 ("§4d what frees the market", "SIZE", "POS", "R", "rule", "", "Low S&P dealer gamma is the variable that matters for big up-legs; calendar and VIX triggers alone barely do"),
 ("§4e earnings and positioning", "DIR", "FORCED", "L", "refine", "re-pose as a pricing test (EQ1: straddle P&L by positioning)", "How crowded a stock is going into earnings shapes the drift after (690 reactions, 38 stocks)"),
 ("§4f gamma release + vol crush rule", "PRICE", "POS", "L", "refine", "re-run with real option prices; forward log", "Out of sample 2019–26: 15 trades, 73% hit, S&P +2.9% a trade; calls lumpy and not beyond the 95th percentile of random entries"),
 ("§4g era check", "BUILD", "-", "D", "ref", "", "End-of-day gamma cannot see same-day (0DTE) positions"),
 ("§4h the gamma path", "TIME", "POS", "L", "rule", "", "Gamma builds into monthly expiry and drops about 17 percentile points on expiry day"),
 ("§4i the entry ladder", "TIME", "POS", "L", "refine", "real option prices and a forward log (F2); most rung intervals overlap the base", "P(up-leg within 20 days) 65–79% on the rungs vs 50–58% any day. Naked calls bought early lose; call spreads gain 10–18%; naked calls pay only after the vol crush (R7)"),
 ("§4j multiverse on S&P gamma", "SIZE", "POS", "R", "rule", "", "Joint p < 0.003 over 216 specifications: low gamma predicts that a big move starts, not a higher average return"),
 ("§4k S&P gamma for TSLA", "SIZE", "POS", "N", "close", "use each stock's own positioning", "S&P gamma says nothing about TSLA (joint p 0.74)"),
 ("§4l TSLA bursts, event by event", "TIME", "POS", "D", "ref", "", ""),
 ("§4m TSLA today", "DESK", "-", "D", "ref", "", ""),
 ("§4n TSLA Q4 catch-ups", "DIR", "HIST", "D", "close", "", ""),
 ("§4o TSLA option regimes", "TIME", "FORCED", "L", "park", "", "Monday up-bursts are more common (weekly-expiry mechanics); corrected in §4ac"),
 ("§4p after the leg: the reset", "EXIT", "POS", "L", "refine", "test the reset as an exit rule in option P&L", "Legs end as gamma rebuilds to pinned levels; a reset precedes the next leg"),
 ("§4q scorecard", "DESK", "-", "D", "ref", "", "Oct 1–8: 6 calls held, 3 partly, 1 missed"),
 ("§4r free data, tested", "BUILD", "-", "D", "ref", "", "Gamma rebuilt from open interest is trustworthy"),
 ("§4s TSLA's own gamma", "DIR", "POS", "R", "rule", "", "Freed (little open interest near the price) → up-bursts 3.8× with controls (p < 0.001); below its flip moves get bigger and are snap-backs"),
 ("§4t TSLA up-bursts, one by one", "TIME", "POS", "D", "ref", "", ""),
 ("§4u today vs past run-ups", "DESK", "-", "D", "ref", "", ""),
 ("§4v the named TSLA moves", "DIR", "POS", "D", "ref", "", ""),
 ("§4w TSLA full setup", "DIR", "POS", "R", "rule", "", "Freed + below its own flip: 39% up-bursts vs 17% down within 3 sessions (reproduced)"),
 ("§4x analog outlook", "DIR", "HIST", "D", "close", "", ""),
 ("§4y the mechanics that push price", "DIR", "FORCED", "D", "ref", "", "A list of flows that can be computed before they happen"),
 ("§4z multiverse on own positioning", "DIR", "POS", "R", "rule", "", "Own-positioning up-legs +27 points, beyond luck in 89% of specifications (joint p < 0.003)"),
 ("§4aa is MSFT held back", "TIME", "POS", "L", "park", "", "'Freed' means S&P dealers short gamma, not thin open interest at SPY's price"),
 ("§4ab TimesFM", "DIR", "HIST", "N", "close", "", "A price-series model adds nothing; the edges are in structure"),
 ("§4ac named moves, day by day", "DIR", "POS", "D", "ref", "", ""),
 ("§4ad the edge lab", "BUILD", "-", "D", "ref", "use it as the power check before any test", "Detection limits: how big an edge must be before a backtest can see it"),
 ("§4ae update Oct 15", "DESK", "-", "D", "ref", "", ""),
 ("§5 MU snapshot", "DESK", "-", "D", "ref", "", ""),
]
assert len(A) == 81, len(A)

def index_results():
    out = {}
    for l in open(AG / "INDEX.md"):
        if not l.startswith("| 20"): continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        m = re.search(r"\[([^\]]+)\]", c[1]);
        if not m or len(c) < 5: continue
        v = re.sub(r"\*\*", "", c[4]); v = re.sub(r"\s+", " ", v)
        out.setdefault(m.group(1), v)
    return out

def build():
    idx = index_results(); rows = []
    for (i, b, m, e, n, note, res) in A:
        r = res or idx.get(i, "")
        if len(r) > 170: r = r[:167].rsplit(" ", 1)[0] + "…"
        rows.append({"id": i, "era": "studies", "book": b, "mech": m, "ev": e, "next": n, "note": note, "result": r})
    for (i, b, m, e, n, note, res) in F:
        rows.append({"id": i, "era": "founding", "book": b, "mech": m, "ev": e, "next": n, "note": note, "result": res})
    return rows

if __name__ == "__main__":
    R = build()
    tally = {b: {k: sum(1 for r in R if r["book"] == b and r["ev"] == k) for k in "RLND"} for b in BOOKS}
    nxt = {b: {k: sum(1 for r in R if r["book"] == b and r["next"] == k) for k in ("rule", "refine", "park", "close", "ref")} for b in BOOKS}
    grid = {m: {b: {k: sum(1 for r in R if r["book"] == b and r["mech"] == m and r["ev"] == k) for k in "RLND"} for b in list(BOOKS)[:7]} for m in list(MECH)[:6]}
    json.dump({"rows": R, "tally": tally, "next": nxt, "grid": grid, "n": len(R)}, open(H / "out" / "catalog.json", "w"), indent=1)
    EV = {"R": "robust", "L": "lean", "N": "null", "D": "no test"}
    md = ["# Catalog: every study since 2026-10-02, filed by the question it informs", "",
          "Generated by `2026-11-15-architecture/catalog.py`. Do not edit by hand; change the script and re-run. The map that explains the questions is [MAP.md](MAP.md).", "",
          "* **Evidence:** robust (replicated or out-of-sample, or p ≤ 0.005 with controls), lean (passed once, partial, or one day), null, no test.",
          "* **Next:** rule (in the playbook; log it forward), refine (worth one better test), park (needs data or more events), close (do not revisit), ref (reference).",
          "* Founding-report sections (§) are in `research/microstructure/REPORT.md`.", ""]
    for b, title in BOOKS.items():
        rs = [r for r in R if r["book"] == b]
        t = tally[b]; md += [f"## {title}", f"{len(rs)} items: {t['R']} robust, {t['L']} lean, {t['N']} null, {t['D']} no test.", "",
                             "| Study | Mechanism | Evidence | Result | Next |", "|---|---|---|---|---|"]
        for r in sorted(rs, key=lambda r: ("RLND".index(r["ev"]), r["id"])):
            name = f"[{r['id'][11:]}]({r['id']}/)" if r["era"] == "studies" else r["id"]
            nx = r["next"] + (f": {r['note']}" if r["note"] else "")
            md.append(f"| {name} | {MECH[r['mech']]} | {EV[r['ev']]} | {r['result'].replace('|', '/')} | {nx} |")
        md.append("")
    open(AG / "CATALOG.md", "w").write("\n".join(md))
    print(len(R), "items")
    for b in BOOKS: print(f"{b:7} {tally[b]}  next {nxt[b]}")
