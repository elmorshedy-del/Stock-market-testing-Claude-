# What moves the price: a model built from the mechanism

**Date:** 2026-11-16. **Type:** derivation (equations and their consequences). **No data touched; nothing pre-registered.**
**Why this exists:** the owner rejected the step-1 work of the same day ("This isn't really the kind of research I want"). Asked what missed, they chose *not from first principles* and *wrong subject*. This page is the replacement: a model of the price itself, built from the mechanism, for the owner to challenge.

## The judgement
* **A price move is an outside push divided by the market's capacity to absorb it.**
* **Some traders are forced to trade when the price moves.** They do not add a push of their own. They change the capacity: they add to it when they trade against the move and take from it when they follow the move.
* **Solved two ways, the model gives two different laws, and they disagree in ways data can settle.** One says positioning multiplies every move and can cause a runaway by itself. The other says positioning adds a fixed amount, matters most on quiet days, and cannot cause a runaway unless capacity itself collapses.
* **A first estimate from the formula, before any data:** in the S&P 500, forced hedging is of the order of 1% of a day's volume per ordinary daily move. That is too small to change the day's move by more than a few percent. If our data shows more, the cause is something else that arrives together with low gamma, or capacity is far smaller than volume suggests. The second possibility is the crash mechanism.

## Three postulates
1. **The price moves only when someone trades.** A net flow of Q dollars moves the log price by x = I(Q). I is the impact law.
2. **Some traders must trade a known amount when the price moves.** Their flow is Q_h = −G·x.
   * G is in dollars per unit of return. It is the sum over everyone who trades mechanically: option dealers (plus or minus), leveraged funds (always minus), funds that rebalance to fixed weights (plus), stop-losses and margin calls (minus).
   * G > 0: they sell rises and buy falls. G < 0: they buy rises and sell falls.
3. **The price settles where all the flow has been absorbed:** x = I(Q_ext − G·x), where Q_ext is the outside push (news and everyone trading by choice).

Everything below is algebra on these three lines.

## Solving it
### Law A: linear impact, x = Q / L
L is liquidity: the dollars of net flow needed to move the price by one unit.

> **x = Q_ext / (L + G)**

* **Gamma is liquidity.** It sits in the same place in the formula, in the same unit, and the two add.
* Positive G makes the market deeper. Negative G makes it shallower.
* Written as a multiplier: x = x₀ / (1 − n), with n = −G / L, the share of each move that the forced traders regenerate. Every move, large or small, is scaled by the same factor.
* **It breaks at L + G = 0** (n = 1). Negative gamma has eaten all the liquidity and the price runs away until G or L changes.

### Law B: square-root impact, x = Y·σ·√(Q / V)
σ is daily volatility, V daily dollar volume, Y a constant near 1. This is the impact law the trading data supports for large orders (cards: Bucci 2019, Donier–Bonart 2015), and it fitted the known forced flow at the 5 November close.

Squaring and solving the quadratic:

> **x = ½ · [ √(m\*² + 4·m₀²) − s·m\* ]**
>
> m₀ = Y·σ·√(Q_ext / V) is the move the push would make alone.
> m\* = Y²·σ²·|G| / V is the **gamma move**. s = +1 for G > 0, −1 for G < 0.

* **One number controls everything:** γ = |G|·σ / V, the forced flow from one ordinary daily move as a share of a day's volume. Then m\* = Y²·γ·σ.
* **Big push (m₀ much larger than m\*):** x ≈ m₀ ∓ m\*/2. Positioning adds or subtracts a fixed amount. Its share of the move shrinks as the day gets bigger.
* **Small push, negative gamma:** x ≈ m\*. There is a floor. A move smaller than the gamma move cannot hold; any small trigger grows to m\*.
* **Small push, positive gamma:** x ≈ m₀² / m\*. Small pushes are crushed. This is pinning.
* **Symmetry:** the damping factor under positive gamma is exactly one over the amplification factor under equal negative gamma.
* **No runaway.** Impact per extra dollar falls as the flow grows, so the loop converges. A crash needs m\* itself to grow, through σ² / V.

## Where the two laws disagree (each line can be tested)
| | Law A (linear) | Law B (square root) |
|---|---|---|
| Quiet days against big days | Low-gamma days move a constant **multiple** of high-gamma days, at every size | A constant **amount** more, about m\*. The ratio goes to 1 on big days |
| The smallest moves | Scaled like all others | Negative gamma: a floor near m\*, few very quiet days. Positive gamma: an excess of very quiet days |
| Damping against amplification | Not mirror images: 1/(1+n) against 1/(1−n) | Exact mirror images |
| Across assets | Effect ≈ 2.5·γ of the move | Effect ≈ γ of an ordinary daily move, as an amount |
| Runaway from positioning alone | Yes, when L + G = 0 | Never. Capacity has to collapse first |

Both laws agree on one thing with no free parameter: **the effect scales with γ.** Measure γ for SPY and TSLA and the ratio of their effects is predicted.

## The estimate before data
* Public estimates put S&P dealer gamma at a few billion dollars per 1% move. E-mini futures alone trade several hundred billion dollars a day. So γ is of the order of 1% on an ordinary day.
* Law B: m\* ≈ 1% of an ordinary daily move, about one basis point. Law A, with the linear impact constant from Kyle and Obizhaeva (2.5): n ≈ 3%.
* **Both say the mechanical effect in the S&P is a few percent at most.** The two papers that use true dealer positions found 1–7%.
* **These inputs are rough and not yet measured by us.** Computing γ from our own data is the first step.
* Where γ becomes large: a stock whose option market is big next to its share volume; the last hour before expiry, when the gamma of at-the-money options grows without limit; a market whose liquidity has dried up.

## What the model says about what we already found
* **Why size is predictable and direction is not.** Direction lives in the push, the numerator, which is news and choice. Size lives in the capacity, the denominator, which is positioning and liquidity and can be seen in advance. This is the pattern the audit found across all the work.
* **The crash-law test.** It found that ordinary impact cannot turn any plausible selling into an index crash, so the response per dollar must jump about tenfold on those days. Law B says the same thing from the other side: positioning alone cannot do it; σ² / V has to explode.
* **The pocket map.** G changes with the price. The model says moves speed up where G is most negative and stall where it is most positive. That is what the map of levels was drawing.
* **Our gamma result may be mostly something else.** If the mechanism can deliver only a few percent in the S&P, a larger gap between low-gamma and high-gamma days has to come from what travels with low gamma: a market that has just fallen and is already volatile.

## What is known and what is mine
* **Law A is old.** It goes back to models from the 1990s (Frey and Stremme; Platen and Schweizer). I know them through the summary in Ni, Pearson, Poteshman and White; I have not read the originals.
* **Law B is my own algebra, done today.** I have not seen it in the papers I have read. It may exist elsewhere.
* **Not yet in the model:**
  1. **Time.** Forced traders act with a delay, which turns the same loop into momentum under negative gamma and reversal under positive gamma.
  2. **G as a function of the price,** which gives the levels.
  3. **Capacity that responds to the move itself:** volatility rises and depth falls as the price moves. This is the missing equation, and it is where crashes live.

## First steps, if the owner agrees (nothing is run before that)
1. **Measure γ** for SPY and TSLA, today and through time. One number each.
2. **Look before testing:** ten days, five quiet and five large, in low and high gamma. Is the gap a constant amount or a constant multiple?
3. Only then write the test that separates Law A from Law B, and register it.

## Where I may be wrong
1. **Postulate 2 assumes forced traders act fully and at once.** If dealers hedge only part of their gamma, G is smaller than the positions imply.
2. **G is not observed.** We have open interest and an assumed sign, and the reading showed the usual sign assumption is wrong for short-dated S&P options.
3. **Neither impact law may hold for a whole day's forced flow.** The square-root law is established for single large orders; using it for the sum of all hedging is an assumption.
4. **The estimate of γ could be off by a large factor** in either direction. One paper (Adams et al. 2026) reports market-maker gamma as about 1% of all S&P 500 shares per 1% move. Read literally that is about a hundred times the public estimates and would make the gamma move larger than an ordinary day. I think it is a unit convention, because the order-flow response the same paper measures is thousands of times smaller, but it has to be checked before γ is trusted.

**Files:** `figure.py` → `out/price_law.png` (the two laws drawn from their formulas; no data).
