# Permanent vs transitory rallies: which footprints say a run won't hold? (pre-registration)

* **Owner:**
  * 2026-10-29: Sept 2, 2020's run "wasn't driven by the kind of price discovery that lasts… forced inflows… a relative vacuum… a house of cards."
  * 2026-10-30: "You used genuine and forced like I gave them to you rather than inferring the more rigorous one… you are responsible for the better handling."
* **The construct, from the literature, not the owner's words:**
  * A price move has a **permanent** part (information: the market reprices and stays) and a **transitory** part (price pressure from trades that are not about value: hedging, liquidations, rebalancing, attention). The transitory part reverses when the pressure stops.
  * Sources: Hasbrouck 1991; Harris-Gurel 1986; Coval-Stafford 2007; Lou 2012; on volume, Campbell, Grossman & Wang 1993 and Llorente, Michaely, Saar & Wang 2002 (hedging- or liquidity-driven moves come with high volume and reverse; informed moves continue).
  * "House of cards" = a run that is mostly transitory.
* **Design:**
  * Do not label runs in advance. Measure **permanence** directly.
  * Test footprints that the mechanisms predict, all known at the run's end, as predictors of low permanence.
  * Use a large panel for power, and check replication across two halves of history.
* **What changes vs [house-of-cards](../2026-10-29-house-of-cards/):** the outcome is measured, not assumed. There are several mechanism-specific footprints instead of one proxy. Call skew replaces ATM implied vol, which cannot tell call demand from fear. There are about 40× more events. Ranks and % units avoid the σ-scaling artifact seen in gap-context F2.

## Events
* **Stock runs:** 42 large caps (the panel, daily OHLCV, Yahoo), 1990–2025.
  * A run end is a session whose 10-session return is in the stock's own top decile and is the highest close of those 10 sessions.
  * Events per stock are at least 20 sessions apart.
* **Index runs:** S&P 500 1990–2025 and Nasdaq-100 2001–2025, same rule.

## Outcome (fixed)
* **Permanence P20** = (close at t+20 − close at t−10) / (close at t − close at t−10): the share of the run still there 20 sessions later. 1 means all of it held; 0 means all of it was given back.
* **Also reported:** P10, the worst give-back within 10 sessions, and the "cliff" (half the run given back within 10 sessions).

## Footprints (measured over the 10 run sessions) and predictions
| | footprint | mechanism | prediction |
|---|---|---|---|
| X1 | abnormal volume: mean volume over the run ÷ the prior 60 sessions | liquidity- or hedging-driven trades come with volume and reverse (CGW 1993; LMSW 2002; large caps have low information asymmetry) | higher means lower P20 |
| X2 | thinning liquidity: mean Amihud (\|return\| ÷ $ volume) over the run ÷ the prior 60 sessions | the move needed little volume: a relative vacuum | higher means lower P20 |
| X3 | overnight share: Σ overnight log returns ÷ Σ total log returns over the run (clipped to [−1, 2]) | gains made at the open, attention-driven, revert (Berkman et al. 2012) | higher means lower P20 |
| X4 | call-skew change: 30-day 25-delta call IV − 25-delta put IV, change over the run (TSLA, NVDA, QQQ, MSFT, MU, 2020-02 – 2026-10) | paying up for upside convexity: dealers short calls hedge by buying, and unwind later | higher means lower P20 |
| X5 | index dealer gamma: share of run sessions with SqueezeMetrics GEX below its trailing-252-day 20th percentile (S&P runs 2011–2025) | dealers least long gamma, so moves are amplified (forced-flow law) | higher means lower P20 |
| X6 | index breadth: share of the 42-stock panel with a positive 10-session return at the run's end (S&P runs) | a narrow rally rests on few names | lower means lower P20 |

* **Tests:**
  * Spearman of the footprint, ranked within stock, with P20.
  * Date-cluster bootstrap (10,000), two-sided.
  * **Holm across X1–X6. Pass at Holm p < 0.05.**
  * For X1–X3 a pass also needs the same sign in 1990–2007 and 2008–2025.

## The exit translation (family E, Holm across the footprints that pass)
* For stock gap-ups ≥ 0.5σ in the first 3 sessions after a run end: the gap day's open → close return (σ) by the footprint's tercile.
* Prediction: the transitory tercile is lower.
* This answers "sell at the open or hold" for gaps that cap a run.

## Also reported
* The reconstructed footprints for Sept 2, 2020 (S&P, NDX, AAPL, NVDA, MSFT, AMZN).
* The current state of TSLA, NVDA, QQQ, SPY.
* The old house-of-cards proxy (ATM IV up) on the same runs, for comparison.

## Limits stated in advance
* Yahoo volume is consolidated, so it includes off-exchange trading. The panel is large caps only. X4 covers 2020 onward for 5 names. P20 includes market drift after the run (a market-adjusted P20 is reported as secondary).
