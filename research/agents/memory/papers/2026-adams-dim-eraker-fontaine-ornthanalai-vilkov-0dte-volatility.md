# Adams, Dim, Eraker, Fontaine, Ornthanalai & Vilkov (2026). Do S&P 500 Options Increase Market Volatility? Evidence from 0DTEs. Working paper (subsumes Dim, Eraker & Vilkov, "0DTEs: Trading, Gamma Risk and Volatility Propagation", SSRN 4692190)
**Read:** the full main text (sections 1–5); the Internet Appendix tables were not read. 2026-11-16. A working paper, not peer reviewed.
**Question it serves:** SIZE (how big), TIME (when). Mechanism tags: POS, FLOW.

## Claim
* **Same-day options make the S&P 500 calmer, on average.** On days when a 0DTE contract expires, intraday volatility is about 7% lower.
* **The cause is positions built on earlier days.** Market makers arrive at expiry day already long gamma, from options bought from customers over the previous week. Trading on the day itself adds almost nothing.
* **Market-maker gamma predicts the next hour:** lower volatility, stronger order-flow reversal in the E-mini future, and reversal instead of momentum in returns.

## Data
* Cboe Open-Close Volume Summary for SPX options at 10-minute intervals, by participant type (customer, professional customer, firm, broker-dealer; market makers are the remainder), Jan 2018–Dec 2024. Cboe's C1 exchange only.
* E-mini futures: one-minute quotes, and trades signed at bid or ask from CME. SPY and the cash index as checks.

## Method
* **Net gamma** = the percentage of all S&P 500 shares that market makers must sell to stay hedged after a 1% rise in the index. Positive means they trade against the move.
* **Identification:** before 19 May 2022, 0DTE contracts expired every Monday, Wednesday and Friday but only on *some* Tuesdays and Thursdays (month-end, quarter-end, holiday shifts). Those exceptions are set by the calendar, so they are close to a natural experiment. 10-minute realized volatility is regressed on a 0DTE dummy with year × week × time-of-day and day-of-week × year fixed effects.
* **Check:** after May 2022 every day has a 0DTE, so the Tuesday/Thursday difference should vanish (difference-in-differences, 2018–2024).
* **Two-stage estimate:** 0DTE presence → net gamma → volatility.
* **Split of 0DTE gamma:** "stale" (positions held at 4 pm the day before) and "new" (opened on expiry day).
* **Intraday predictive regressions** with date fixed effects: next-interval volatility, signed E-mini order flow, and momentum returns by gamma quartile.

## Results
* **Volatility:** −61 basis points of annualized 10-minute volatility on 0DTE days, against a mean of 9.10%, so about −7%. Tuesdays and Thursdays were more volatile than other days before 2022; the gap closed when daily expiries began.
* **Market makers are long gamma most of the time:** positive in 88% of 10-minute intervals; every monthly average is positive.

  | Net gamma (percent of S&P shares per 1% move) | Before May 2022 | After |
  |---|---|---|
  | Total | 0.88 | 1.42 |
  | From 0DTE | 0.23 | 0.54 |
  | From other maturities | 0.64 | 0.87 |
  | 0DTE, stale positions | 0.29 | 0.39 |
  | 0DTE, new positions | 0.08 | 0.16 |

* **When stale positions were opened:** about half one day before expiry; close to 90% in the week before.
* **What customers hold in 0DTE:** short at-the-money and slightly out-of-the-money options, long far out-of-the-money ones (iron condors and butterflies). Their net gamma is strongly negative, so market makers' is positive.
* **Netting:** about 1 million 0DTE contracts trade a day, but customers' net imbalance in at-the-money 0DTE is under 5,000 contracts by the close.
* **Effect of a 0DTE day on gamma:** 0DTE gamma +27.5 basis points (stale +25, new +3); other maturities −14; total +15.
* **Multiplier:** 1 basis point more net gamma → about 4 basis points less annualized intraday volatility (two-stage coefficient −4.04).
* **Intraday:** one intraday standard deviation of net gamma (0.54) → about −22 basis points of volatility in the next 10 minutes; the effect decays to zero in about an hour (cumulative −2.0 per unit over the hour).
* **Order flow:** after a 14 basis point fall, buying exceeds selling in the next 10 minutes; with net gamma one standard deviation higher the response is 36–40% larger. Significant for 30 minutes.
* **Momentum:** in the lowest gamma quartile, 1–2 hour momentum earns about +0.7 basis points; in the highest it earns −1 to −2 (reversal). The gap is 1–3 basis points and significant.
* The authors note this is not tradable by outsiders because market-maker gamma "is not observable to other investors".

## Caveats
* **The authors':** they cannot tie E-mini orders to option market makers; the result is an average and may not hold in every market condition or for single stocks; the intraday part is predictive, not causal.
* **Mine:**
  * An average effect of −7% says nothing about the tail. The days we care most about are the ones where gamma is negative, about 12% of intervals.
  * Only one exchange's SPX options. SPY options, E-mini options and over-the-counter positions are outside.
  * The exception Tuesdays and Thursdays are month-ends, quarter-ends and days next to holidays. The diff-in-diff helps, but those days are not ordinary days.
  * **The level of net gamma needs a unit check.** "About 1% of S&P 500 shares per 1% move", read literally, is several hundred billion dollars per 1%, about a hundred times public estimates and far more than the order-flow response the paper itself measures. Use the signs and relative sizes; do not use the level until the unit is confirmed.
  * Date fixed effects remove the day's volatility level. As in Amaya et al., the estimate is the within-day part.

## What it means for us
* **Our gamma sign convention is wrong at the short end for the S&P.** We (and the public GEX series) assume customers sell calls and buy puts. In 0DTE and the last week before expiry, customers sell at-the-money options of both kinds. Market makers are long gamma near the money on both sides. This is true-position evidence, twice (this paper and Amaya et al.).
* **Timing fact for the expiry mechanism:** dealer long gamma *peaks into* each expiry (positions bought over the prior week become very high-gamma) and vanishes at 4 pm. Before 2022 that cycle was weekly and monthly. Since May 2022 it is daily. Our founding-report rule "gamma builds into monthly expiry, then resets" is the monthly layer of the same thing, and it should be weaker now than in 2011–2021.
* **Who is on the other side, and why it matters for price:** customers are net *sellers* of short-dated at-the-money options. By the demand-pressure logic (Gârleanu et al.) that should make those options cheap, not dear. It fits Dew-Becker & Giglio's finding that the index option premium is gone.
* **The dealer sets the option price and also knows the position.** Outsiders cannot observe it. So the prior from mechanism is that the effect of dealer gamma on volatility is already in the option price, and the open question is only the premium on top.
* **A new, cheap intraday tool:** in high-gamma states fade the last hour's move; in low-gamma states follow it. The measured edge is 1–3 basis points per trade, too small for options, but it is the same mechanism as our robust "moves on low-gamma days are given back".

## How we would replicate or extend it on our data
* Not replicable without the Cboe open-close data. A daily version of that file would let us build true market-maker gamma for SPX; cost not yet checked.
* What we *can* do: stop treating short-dated SPY open interest with the calls-minus-puts sign. Test whether an unsigned measure (total near-the-money gamma expiring within a week) explains the next day's range better than the signed one.

## Open questions
* What is the sign and size of market-maker gamma on the days we call "short-gamma pocket" days? Our pocket map worked for levels on 30 October and 5 November; it may be working for a different reason than the one we gave.
* Do single stocks with heavy retail call buying (TSLA) show the opposite sign, as Lipson, Tomio & Zhang suggest? (Not read.)
