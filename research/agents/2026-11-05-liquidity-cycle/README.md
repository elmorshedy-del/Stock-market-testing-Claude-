# Does liquidity predict, on larger frames, and is there a cycle? (SPY, TSLA)

**Agent / session:** Claude, claude.ai session for the owner. **Started:** 2026-11-05. **Pre-registered at commit:** the commit that first adds this README.
**Type:** extension + new question.
**Owner (Nov 5):** "does this also work on larger frames and does it have predictive powers like is there a cycle for example that's followed."

## Prior work
* [flow-physics](../2026-10-27-flow-physics/) A1.
  * SPY's daily move is not explained by net aggression (ρ −0.12, 16 days). TSLA's is (ρ +0.48, 26 days).
  * Book thinness (Kyle λ) vs dealer gamma: ρ −0.37, p 0.16.
  * Re-check on Nov 4: λ vs the size of SPY's day was ρ +0.10 (p 0.72). So **"SPY is liquidity-led" is unproven**; it rests on elimination.
* [gamma-phase-diagram](../2026-11-01-gamma-phase-diagram/): below the pre-open flip, the day's range is ×1.33; the flip adds little after 09:45.
* REPORT §4p: S&P legs follow a GEX reset (88–90%). Gamma builds, then resets in a median of 11 days.
* REPORT §4i/§4l: the ladder (R1–R7).

## Not tested here, and why
* **Aggressive flow at scale.** Signing minute bars from their own price change (bulk volume classification) makes "flow" a function of the return. Any flow-vs-move link would then be partly built in. A fair test needs real aggressor-signed trades (Databento; about $0.37/day for ES), so it is parked.

## Q1. Does yesterday's thinness predict the size of the next 1 / 5 / 20 days, beyond the obvious baseline?
* **Data:**
  * SPY Arca 1-minute bars, 2020-01 to 2026-10 (in hand).
  * TSLA Nasdaq 2020–23 plus EQUS 2024–26 bars. Venues differ, so only trailing-year percentiles are used.
  * VIX; TSLA ATM 30-day IV (`microstructure/out/td_gamma_TSLA.csv`); SqueezeMetrics S&P GEX.
* **Thinness L_t:** per day, Σ|5-minute log return| ÷ Σ dollar volume (intraday Amihud). Its 5-day mean is then expressed as a trailing-252 percentile, known at the close of t.
* **Outcome:** the log mean daily high–low range over days t+1…t+k, for k = 1, 5, 20.
* **Baseline:** log implied vol (VIX for SPY, own ATM IV for TSLA) plus log range on day t, the 5-day mean range and the 20-day mean range.
* **Added:** L_t. A second model adds the S&P GEX percentile for SPY, or TSLA's own near-price OI percentile.
* **Split:** fit 2020–2023, test 2024–2026 (out of sample).
* **Statistic:** the out-of-sample R² gain over the baseline. 90% CI by 20-day block bootstrap of the test errors.
* **Circularity, stated:** L contains |return|, but the baseline already holds the ranges. Any gain is the part of thinness that range alone doesn't carry, i.e. low volume for the move made.
* **Pass:**
  * **Q1-SPY:** gain > 0 at k = 5 (primary), 90% CI above 0.
  * **Q1-split:** SPY's gain minus TSLA's gain > 0 (CI above 0). This tests the claim "liquidity matters more for SPY".
  * k = 1 and 20 are reported, not scored.
* **What would prove the claim wrong:** no gain beyond IV + range for SPY, or a gain as large for TSLA.

## Q2. Is there a liquidity cycle, does it follow its order, and does the phase predict? (S&P, 2012-01 to 2026-11)
* **Phase at each close** (first match wins, so phases don't overlap; gp = S&P GEX trailing-252 percentile, SqueezeMetrics):

  | Phase | Rule |
  |---|---|
  | **RECOVERY** | min(gp over the last 15 sessions) ≤ 0.20 **and** VIX ≤ 0.85 × its 10-day max |
  | **THIN** | gp ≤ 0.20 |
  | **THINNING** | gp ≤ 0.50 **and** gp fell by ≥ 0.25 over the last 10 sessions |
  | **CALM** | gp ≥ 0.50 |
  | OTHER | everything else |

* **Canonical order:** CALM → THINNING → THIN → RECOVERY → CALM.
* **D1 order:**
  * Merge consecutive same-phase days into episodes, drop OTHER, merge again.
  * Statistic: the share of transitions that go to the canonical next phase.
  * Null: shuffle the episode sequence 10,000× (keeps the episode counts).
  * **Pass: p < 0.05.** The full transition matrix is reported.
* **D2 forecast:**
  * By phase vs all days: the forward 20-day S&P return, the up-leg odds (a top-decile 10-day return, ≥ +3.5%, starting within 20 sessions; REPORT §4p) and the forward 10-day mean range.
  * Null: circular shift of the phase series against outcomes (shifts ≥ 60 sessions, 2,000 draws). Holm across the 4 phases × 3 outcomes.
  * **Predictions:** RECOVERY → higher forward return and up-leg odds; THIN → higher forward range; CALM → lower range.
* **D3 (descriptive):** median episode length per phase, and the time to complete a full cycle.
* **D4 (descriptive):** phase shares by sessions to the next monthly expiry.
* **Cross-check (METHOD 11), descriptive, 2020–26:** SPY intraday thinness (L) by phase. If the cycle is a liquidity cycle, L should be highest in THIN and lowest in CALM.
* **Caveat:** D2 overlaps the ladder (R1–R7 already lift up-leg odds). The new pieces are D1 (sequence) and D3 (timing).
* **Today:** which phase the latest close is in.

## Reproduce
`python size.py <bars dir> <DIX.csv>` → `out/q1.json`; `python cycle.py <DIX.csv> <bars dir>` → `out/q2.json`; `python figure.py` → `out/liquidity_cycle.png`.
