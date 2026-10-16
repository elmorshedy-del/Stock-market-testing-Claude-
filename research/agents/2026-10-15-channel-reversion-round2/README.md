# Round 2: does anything predict the swing to the lower channel line? Fresh stocks, the S&P zoomed in, and why it fails

**Agent / session:** Claude (Opus 5.5), claude.ai session for the owner, 2026-10-15
**Started:** 2026-10-15   **Pre-registered at commit:** see the first commit that adds this file (no results at that commit)
**Type:** replication on fresh data + new question + method improvement
**Verdict:** *(filled in at the end)*

## Why this round

Round 1 (`research/agents/2026-10-15-channel-reversion-macro`, commit 97ef918) found:
* top-of-channel → lower line within 24 months happens about as often as in random walks with each stock's own drift
  and volatility (41.6% vs 36%, p 0.13);
* none of 13 macro, liquidity, leverage, credit, gamma or inventory variables passed;
* one lead: **margin debt surging** (60% vs 26% of top months reverted, shift p 0.02, but only measurable after 2010);
* the textbook Fed-tightening readings pointed the wrong way.

The owner asked for: (1) the margin-debt lead tested on stocks it has never seen, (2) the S&P 500 added and zoomed in,
so the variables that failed get a fairer test with many more swings, (3) my own theories for why it fails, tested,
(4) ideas from the literature.

## Literature that shaped the hypotheses (searched before any round-2 result)

* **Goyal & Welch (2008), Goyal, Welch & Zafirov (2024, RFS):** almost no macro/valuation variable predicts the equity
  premium out of sample; a few survive (short interest, technical indicators, T-bill rate, average correlation,
  equity issuance). Round 1's null result is the expected one.
* **Deuskar, Kumar & Poland (2017), "Margin Credit and Stock Return Predictability":** the *credit* side of margin
  accounts (excess debt capacity that leveraged longs choose not to use) predicts returns and crashes out of sample;
  plain margin *debt* is popular but weak out of sample. → new variable `MARGIN_CREDIT`.
* **Neely, Rapach, Tu & Zhou (2014):** price-trend rules (price vs 12-month moving average, 12-month momentum) catch the
  decline near cycle peaks better than macro variables. → `TECH_MA`.
* **Pollet & Wilson (2010):** average pairwise correlation of stocks tracks aggregate risk and predicts the market.
  → `AVG_CORR`.
* **Fed hiking studies (Truist, Dimensional, NDR/Schwab 2026):** stocks rose in 11 of 12 hiking cycles; what matters is
  the **pace** (fast cycles, deeper drawdowns). → explains round 1's sign; new variable `FAST_HIKE`.
* **Bear-market prediction (Chen 2009; Chen, Chen & Chou 2017; Tokic & Jackson 2023):** credit spreads and the yield
  curve help a few months ahead; the depth of a drawdown is driven by credit stress that arrives *after* the drawdown
  starts. → motivates the lead–lag check E1 (signals that only light up after the turn look predictive in hindsight).

## My theory for why it fails (tested as C2)

**The swing to the lower line is a race between distance and volatility.** If price wanders around the channel's
trend, the chance it touches the lower line within H months is roughly the chance a random walk with zero drift
(relative to the line) covers the distance x₀ = log(close) − log(lower line): **P = 2·Φ(−x₀ / (σ·√H))**, σ the stock's
recent volatility. Anything that does not change x₀ or σ cannot predict the touch. Fed hiking happens in calm, growing
markets (low σ), which would explain why it *lowered* the reversion rate in round 1.

## Data (built before any outcome was computed)

* **Fresh stocks:** 93 large US non-tech names in 9 sectors (`build.py`; BK failed to download), monthly bars adjusted
  for dividends and distributions (Yahoo's split-only close turns spin-offs such as MO 2008 and KR's 1988
  recapitalisation into fake crashes). No overlap with round 1's tech universe.
* **S&P 500:** Yahoo ^GSPC daily from 1928 (before 1962 Yahoo has closes only, so weekly lows are close-based), weekly
  bars to Fridays (`sp_build.py`).
* **Signals:** round-1 macro table reused; weekly versions built with the known-at rules in `sp_build.py`; ex-ante
  volatility and average correlation from daily returns (`extra_signals.py`); FINRA free credit balances in margin
  accounts start Feb 2010.
* Seen before writing this file: download coverage, the large-move audit that led to adjusted bars, the share of
  valid channels per window, summary stats of average correlation. No outcome, rate or variable-outcome relation.

## Shared definitions

Monthly panels: channel fit as round 1 (`fit_channel` of the owner's study, W = 84 months, q = 0.05, valid if slope > 0
and R² ≥ 0.80), top = z ≥ 0.5, outcome = a monthly low reaches the channel's lower line (frozen at t) within H = 24
months. Signals "on" = top third of the trailing 120 months (≥ 36 months of history) unless binary by definition.
Null = circular time shift of the signal within its own window, the same shift fraction for every variable in a draw,
1,000 draws, seed 20261016. Multiverse = W {60, 84, 120} × top z {0.33, 0.5, 0.67} × H {12, 24} × cut {top third,
above median} (36 specifications).

S&P weekly: W = 156 weeks (multiverse 104/156/260), top z ≥ 0.5, H = 26 weeks (multiverse 13/26), weekly lows,
percentiles over the trailing 260 weeks (≥ 104).

**Family test change (decided before any S&P result):** round 1's family test (maximum standardised difference)
misbehaved when variables had very different sample sizes (round 1 post-hoc P1). Round 2 uses the **min-p
(Westfall–Young)** family test throughout.

## Confirmatory tests and frozen pass/fail criteria

### C1. Margin debt on fresh stocks
Panel: the 93 non-tech stocks. Signal `MARGIN_FROTH` exactly as round 1. Statistic Δ = P(reversion | top, on) −
P(reversion | top, off). **Pass if all hold:** (1) Δ > 0 with shift p < 0.05; (2) Δ > 0 in the 2010+ subset (where round
1's lead lived); (3) at the episode level, episodes whose last top month has the signal on reverted more often than
those with it off. If the no-effect calibration check on this panel (200 persistent random signals) shows more than 10%
false positives at p < 0.05, criterion (1) tightens to p < 0.01. Multiverse p ≥ 0.05 → reported as **fragile**.
**Fail** → the round-1 lead was chance or tech-specific.

### C2. The barrier theory
Rows: valid-channel stock-months with price above the lower line, tech + non-tech panels, W = 84, H = 24.
P_BM = 2Φ(−x₀/(σ√24)), σ = std of the last 126 daily log returns × √21 (known at t).
**Theory supported if all hold, on top-state rows:** (1) AUC of P_BM ≥ 0.65; (2) AUC(P_BM) − AUC(z) > 0 with a 95%
month-block bootstrap interval above zero; (3) calibration slope (logit y on logit P_BM) between 0.7 and 1.3.
Also reported (no pass/fail): each round-1 variable's effect after controlling for P_BM (logistic, shift-null p), and
volatility with the signal on vs off.

### C3. S&P 500 zoomed in (weekly)
Variables (high = theorised bearish): `FF_HIKE`, `Y10_UP`, `CURVE_FLAT`, `USD_UP`, `M2_SLOW`, `MARGIN_FROTH`,
`LIQ_DRAIN`, `TIPS_UP`, `CREDIT_WIDEN`, `GEX_LOW`, `DIX_LOW`, `VIX_HIGH`, `VIX_INVERT` (VIX / VIX3M).
**A variable passes if:** shift p < 0.05, family min-p < 0.05 (13 variables), Δ > 0 in both halves (split 2010-01-01
for series starting before 2000, 2018-01-01 otherwise). Multiverse p ≥ 0.05 → fragile. Waves (reversion episodes whose
runs end within 26 weeks of each other count as one) are reported with every result. If fewer than 6 reversion waves
fall inside a variable's sample, its result is labelled underpowered whatever the p-value.

### C4. Literature variables (pooled tech + non-tech monthly panel)
`MARGIN_CREDIT` = log(free credit balances in margin accounts / S&P 500 level), known at the end of the following month,
high = bearish; `TECH_MA` = S&P 500 below its 12-month average (binary); `AVG_CORR` = average pairwise correlation of
daily returns across the universe, trailing 63 sessions, high = bearish; `FAST_HIKE` = fed funds up ≥ 1.5 points in 12
months (binary).
**A variable passes if:** shift p < 0.05, family min-p < 0.05 (4 variables), Δ > 0 separately in the tech and the
non-tech panel, Δ > 0 in both halves (split 2010; `MARGIN_CREDIT` 2018). Also shown on the S&P weekly (descriptive).

## Exploratory (no pass/fail; labelled as such in the results)

* **E1 Lead–lag:** share of each signal on from 12 months before to 12 months after the last top month, reverting vs
  non-reverting episodes. Does it light up before the turn, or only after?
* **E2 Trend break:** among middle-of-channel rows (−0.5 ≤ z < 0.5), does being below the stock's own 10-month average
  add to P_BM? (logistic, per-stock shift null)
* **E3 Crowding:** share of the universe at the top of its channel at the same time, as a signal.
* **E4 Stretch × tightening:** top rows with z ≥ 1 and round 1's composite on vs off.
* **E5 Volatility and the Fed-hike sign:** σ with `FF_HIKE`, `CURVE_FLAT`, `M2_SLOW` on vs off; their Δ within P_BM
  terciles.
* **E6 NVDA zoomed in:** NVDA on 2- and 3-year weekly channels today, with P_BM for the next 26 weeks.

## Results

*(after the run)*
