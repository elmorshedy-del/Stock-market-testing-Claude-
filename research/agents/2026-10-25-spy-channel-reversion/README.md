# What warns that the S&P is about to revert inside its rising channel?

**Agent / session:** Claude, claude.ai session for the owner, 2026-10-25
**Type:** pre-registered test of 24 candidate warnings in four families, with family-wise error control. This file was pushed before any outcome was computed.
**Builds on:**
* sp-multivariate (10% corrections, weekly: only a broken trend warned; options and volatility structure added nothing after 2019);
* forced-flow (forced moves fade);
* spy-channel (the owner's 2026 channel).

**Verdict:** (after the run)

## Question
* Since the Oct 2022 low the S&P has risen in a channel, with reversions inside it: Jul–Oct 2023, Apr 2024, Jul–Aug 2024, Feb–Apr 2025 and Feb–Mar 2026.
* What, observable beforehand, warns of the next one?
  * microstructure and forced flow;
  * momentum and trend;
  * volatility structure;
  * other ETFs that turn first.
* **Why not test on the channel alone:** this channel has about 5 reversions, too few for a test. The test uses every day since mid-2011 on which the S&P was near its highs. The 2022–2026 reversions and today's readings are then shown descriptively.

## Design
* **Data:**
  * Yahoo daily ^GSPC, SPY, ^VIX, ^VIX3M, ^VIX9D, ^VVIX, ^SKEW, and the ETFs HYG, IEF, IWM, RSP, SMH, XLY, XLP, TLT, UUP, KRE, BTC-USD. Dividend-adjusted closes are used for the ETFs.
  * SqueezeMetrics GEX and DIX.
  * Everything is as known at day t's close.
* **Universe:** trading days from 2011-06-01 to 2026-09-24 on which the S&P closed **within 5% of its 252-day high** (near the top of the channel). All days are also reported.
* **Outcome (primary):** within the next 20 sessions, the S&P closes at least **5% below day t's close**.
* **Outcome (secondary):** at least 8% below.

**Predictors.** Each has its direction fixed here; "risk when" means a higher risk of a reversion. Percentiles are trailing 252-day.

| Family | Predictor | Risk when |
|---|---|---|
| **M** microstructure / forced flow | M1 S&P dealer gamma (GEX) percentile | low |
| | M2 10-day change in the GEX percentile | falling (pin released) |
| | M3 DIX percentile | low (less dark-pool buying) |
| | M4 20-day realized-volatility percentile | low (volatility-target funds at maximum exposure) |
| | M5 VIX minus 20-day realized volatility | high (hedging demand) |
| **T** momentum / trend | T1 close vs its 50-day average | low (trend broken) |
| | T2 20-day return | low |
| | T3 RSI(14) | **high (overbought hypothesis)** |
| | T4 sessions since the 252-day high | many (stalling) |
| **V** volatility structure | V1 VIX ÷ VIX3M | high |
| | V2 VIX9D ÷ VIX | high |
| | V3 VVIX percentile | high |
| | V4 SKEW percentile | high |
| | V5 10-day correlation of S&P returns with VIX changes | high (VIX not falling on up days) |
| | V6 10-day change in VIX | rising |
| **X** other ETFs (20-day relative return) | X1 HYG vs IEF (credit) | low |
| | X2 IWM vs SPY (small caps) | low |
| | X3 RSP vs SPY (equal weight, breadth) | low |
| | X4 SMH vs SPY (semis, leadership) | low |
| | X5 XLY vs XLP (discretionary vs staples) | low |
| | X6 KRE vs SPY (regional banks) | low |
| | X7 TLT 20-day return | low (yields rising) |
| | X8 UUP 20-day return | high (dollar rising) |
| | X9 BTC 20-day return (2014+) | low |

**Statistics:**
* Each predictor's **AUC** for the primary outcome on the universe days, in its pre-set direction.
* **Family-wise null:** circular shifts of the outcome against all predictors at once. 2,000 shifts, minimum shift 60 days. The p-value uses the maximum AUC across the 24 predictors per shift (Westfall–Young).
* **A predictor passes** if its family-wise p < 0.05.

**Composite ("a group of setups"):**
* Family scores are the mean of the sign-aligned trailing percentiles; the setup score is the mean of the four family scores. Its AUC is tested with the same shift null.
* **Walk-forward logistic regression** (L2, C = 0.3; refit yearly; tested 2016–2026) on all 24 predictors, compared with two single-variable baselines: VIX alone and T1 alone.
* **Pass for the combination:** AUC above the better baseline by at least 0.03, with a calendar-year bootstrap 95% interval above 0.

**Descriptive:**
* each family's reading in the 20 sessions before every 2022–2026 reversion of 5% or more from a high;
* today's readings.

**Prediction (written before the run):**
* T1/T2 (broken trend) pass, as in sp-multivariate.
* Credit (X1) may pass.
* T3 (overbought) fails or points the other way.
* Microstructure and volatility structure are weak after 2019.
* The combination does not beat the best single predictor.

## Threats to validity
* **Few independent episodes.** Roughly 25–35 reversions of 5% or more since 2011. Overlapping 20-day outcomes are handled by the shift null.
* **The near-high universe is a choice.** All-days results are reported alongside it.
* **ETF relative returns are noisy proxies** for the flows they stand in for.
