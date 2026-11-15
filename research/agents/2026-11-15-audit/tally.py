"""Audit 2026-11-15: classify the 81 agent studies by topic and outcome (the classification is the auditor's reading of each
INDEX verdict), and score the forecasts that came due. Writes out/audit.json."""
import json
from pathlib import Path
H = Path(__file__).resolve().parent
# outcome: R robust (replicated / out-of-sample, or p <= 0.005 with controls) | L lean (passed once at p ~0.01-0.05, partial, one day, post hoc)
#          N null (primary failed, nothing passed) | D no test (live read, map, forensics, literature)
S = {
 "Chart lines & channels": {"channel-reversion-macro": "N", "channel-reversion-round2": "N", "owner-channel-gamma": "D", "spy-channel": "D",
    "channel-microstructure": "N", "channel-correction-theory": "N", "spy-channel-reversion": "N", "channels-deep": "N", "channel-physics": "N"},
 "Indicators, analogs,\nseasonality, models": {"sp-multivariate": "L", "technical-indicators": "L", "kronos-tsla": "L", "spx-year-analogs": "N",
    "momentum-reversal": "L", "july-october-forensics": "N", "july-october-machine": "D", "yearend-forecast": "D", "2000-lens": "D", "ai-rotation": "D",
    "november-cycle": "L", "regime-compare": "D", "speed-extremes": "N", "unwind-low": "N"},
 "Dealer gamma &\noption positioning": {"dealer-sign": "R", "flip-during-bursts": "D", "gaps-and-walls": "N", "named-moves-gamma": "D", "pierce-and-reclaim": "N",
    "spy-gamma-levels": "N", "positioning-tests": "R", "flip-wicks": "L", "tsla-freed-dpi": "D", "gamma-phase-diagram": "R", "rsi-gamma-precedents": "D",
    "wall-short": "N", "tsla-breaking-point": "N", "tsla-options-signal": "N", "tsla-wall-flow": "D"},
 "Forced flows,\ngaps & exits": {"forced-flow": "R", "tsla-gap-states": "L", "gap-teardown": "N", "open-fade": "N", "calendar-mechanics": "R", "gap-context": "N",
    "house-of-cards": "N", "permanence": "N", "orb-gamma": "L", "forced-flows": "N"},
 "Order flow &\nliquidity": {"spy-intraday-levels": "L", "spy-intraday-multiday": "D", "order-flow": "N", "flow-physics": "L", "friday-narrative": "L",
    "informed-flow": "N", "deferred-days": "L", "liquidity-cycle": "N", "liquidity-landscape": "D"},
 "Macro, politics\n& events": {"election-vol": "L", "polymarket-fed": "L", "tsla-politics": "N", "macro-trigger": "L", "two-day-thesis": "L"},
 "Single-stock quirks": {"spcx-tsla-lead-lag": "N", "aapl-decoupling": "N", "aapl-quirks": "L", "intraday-hours": "L"},
 "Laws & literature": {"hft-papers": "D", "literature-laws": "D", "paper-unified-flow": "D", "aftershocks": "R", "signature-test": "L", "crash-law": "R"},
 "Live desk & reviews": {"ladder-status": "D", "live-read 10-27": "D", "live-read 10-28": "D", "live-read 10-30": "D", "live-read 11-02": "D", "week-review": "D",
    "note-check": "D", "msft-read": "D", "post-election-map": "D"},
}
tally = {t: {k: sum(v == k for v in d.values()) for k in "RLND"} for t, d in S.items()}
tot = {k: sum(x[k] for x in tally.values()) for k in "RLND"}
assert sum(tot.values()) == 81, tot

# ---- forecasts that came due (prices: Yahoo daily, pulled 2026-11-15) ----
def brier(p, y): return (p - y) ** 2
# Nov 2 live read (2026-11-02-live-read): (id, options-implied map, my call, outcome)
LR = [("S1 Mon close > 755.72", .65, .65, 0), ("S2 Mon close in 751-766", .68, .70, 1), ("S3 trades >= 766.4 by Fri", .62, .65, 1),
      ("S4 Fri close >= 766.4", .32, .35, 0), ("S5 trades <= 750 by Fri", .60, .50, 1), ("S6 Fri close > 755.72", .56, .60, 0),
      ("S7 Fri close <= 740.6", .15, .12, 1), ("S8 VIX close <= 16.5 any day", None, .25, 0),
      ("T1 Mon close > 399.81", .59, .62, 1), ("T2 Mon close in 395-410", None, .60, 1), ("T3 trades >= 420 by Fri", .46, .45, 0),
      ("T4 Fri close >= 420", .24, .20, 0), ("T5 trades <= 380 by Fri", .37, .30, 1), ("T6 Fri close > 399.81", .52, .57, 0)]
both = [x for x in LR if x[1] is not None]
score = {"n with a benchmark": len(both), "Brier, options-implied map": round(sum(brier(m, y) for _, m, _, y in both) / len(both), 3),
         "Brier, my calls (same 12)": round(sum(brier(c, y) for _, _, c, y in both) / len(both), 3), "Brier, coin flip": 0.25,
         "Brier, my calls (all 14)": round(sum(brier(c, y) for _, _, c, y in LR) / len(LR), 3),
         "outcomes": {i: bool(y) for i, _, _, y in LR},
         "week data": "SPY closes 752.10/754.35/766.81/733.00/735.29, week high 775.64, low 732.71; TSLA closes 403.82/398.50/385.19/343.69/358.22, high 414.23, low 338.15; VIX min close 16.61"}
other = {"year-end forecast, Nov 13 checkpoint": {"forecast median": 764, "25-75%": [751, 778], "10-90%": [734, 794], "actual SPY close": 754.37, "inside 25-75%": True},
         "aftershocks, next 5 sessions (Nov 6-12)": {"Hawkes forecast": 0.63, "range": [0, 2], "constant rate": 0.55, "actual big days (|r| >= 1.71%)": 1, "which": "Nov 9 (+2.35%)"},
         "level calls": {"Oct 30 flush low called 750-754": "hit (750.36)", "Nov 5 crash low vs the SPY pocket mapped on Nov 2 (730-745)": "inside (low 732.71, close 733.00), bounced",
                         "TSLA floor mapped at 372-381": "missed (low 338.15)", "channel 'bounce' call of Oct 25": "failed Nov 5"}}
json.dump({"studies": S, "tally by topic": tally, "totals": tot, "tests run": tot["R"] + tot["L"] + tot["N"], "Nov 2 live-read forecasts": score, "other due items": other},
          open(H / "out" / "audit.json", "w"), indent=1)
print(tot, "tests run:", tot["R"] + tot["L"] + tot["N"]); print(json.dumps({k: v for k, v in score.items() if k != "outcomes"}, indent=1))
for t, x in tally.items(): print(f"{t.replace(chr(10), ' '):42} {x}")
