# Is the state priced? The derivation, written before any data

**Date:** 2026-11-16. **Type:** derivation for the owner to challenge (queue step 1 in [MAP.md](../MAP.md)).
**Status:** no data touched; nothing pre-registered; no test will be registered until the owner has challenged this page.
**Basis:** seven papers read in full, with cards in `memory/papers/` (listed at the end).

## The judgement
* **An option is cheap or dear mainly because of who is on the other side of it. How big the next move will be is the smaller part.**
* Our strong result holds: low dealer gamma goes with bigger moves. But the dealers who make those moves bigger are the same people who set the option's price, and they charge for it.
* **So the derived sign is the reverse of the natural hunch.** Buying options should be a *worse* deal when dealers are short gamma (after a selloff) and a fair or better deal when dealers are long gamma (calm markets).
* **One place should favour the buyer on both counts:** the days right after a monthly expiry, in a market where customers are option sellers. Whether TSLA is such a market is unknown, and measuring it is the best test this reading produced.

## The decision this serves
When to own a naked call, when to use a spread, when to wait, and which day to buy.

## The mechanism: three facts
1. **Who is forced to trade.** Dealers hedge. When they are short gamma they must buy rises and sell falls, so moves get bigger. When they are long gamma they do the opposite, so moves get smaller.
   * Size: about 12% of a stock's daily absolute return per standard deviation of dealer gamma (1990–2001, true positions); 5–25 basis points per standard deviation in 2010–2020; in the S&P 500, about 7% lower intraday volatility on days with heavy dealer long gamma, and at most +3.3 volatility points on the worst short-gamma day of 2020–2023.
   * It is a flow divided by the market's capacity to absorb it, so it is larger where liquidity is thinner.
2. **Who takes the other side, and what they charge.** Dealers cannot hedge an option perfectly (prices gap; volatility itself moves). They are paid for the risk left over. When customers make them sell options, the price goes up. When customers sell options to them, the price goes down.
   * Size: about 1.7 volatility points, a third of the index-option premium, in 1997–2001; one standard deviation of demand moved the premium by half a standard deviation; the effect doubled after dealers had lost money.
   * S&P 500 options stopped being overpriced on average around 2012, when dealers stopped being net short them.
   * In single stocks, option prices fall on the third Friday and the Monday after, when option writers roll: −0.43% of the hedged position in two days, which I work out to about 3% of the premium.
3. **Who knows what.** Only dealers see dealer positions. The party that sets the option price is the party whose hedging makes the move. So the part of the bigger move that can be forecast from positioning should already be in the price.

**In one line:**

> implied move = the dealers' forecast of the move + a base premium + a charge that rises when dealers are short
>
> buyer's edge = realized − implied = (a surprise that averages zero) − base premium − that charge

The forecast cancels. What is left moves with the charge. **The buyer's edge rises with dealer gamma.**

## What this predicts (sign, rough size and failure condition fixed here)
| | Prediction | Rough size | It fails if |
|---|---|---|---|
| **P1. State** | Realized ÷ implied is higher when dealer gamma is high than when it is low, inside the same band of VIX | A gap of 0.05 to 0.15 between the top and bottom third of gamma days (the 1997–2001 estimates scaled down, because the index premium has since shrunk by more than half) | The ratio is flat (the state is exactly priced), or it is higher in low gamma (the hunch was right and fact 2 is weak today) |
| **P2. Expiry, writers' market** | Options one to two months out get cheaper from the Thursday before monthly expiry to the Monday after, and stay cheaper. The move in the following week is not smaller. So a call bought after that Monday beats one bought the Thursday before | About 3% of the premium | There is no drop, or realized volatility falls by as much |
| **P3. Expiry, buyers' market** | Where customers are net buyers of calls, the same two days push the price **up** | Same order, opposite sign | The sign is the measurement. It tells us who is on the other side in TSLA |

* **P1 is the old question with its sign corrected.** It also explains a result we already have. The founding report's ladder (§4i) found that naked calls bought on the low-gamma rungs lost 1–6% while call spreads made 10–18%, and that naked calls paid only after the volatility crush. That is fact 2 seen in our own numbers.
* **P2 and P3 are new.** They come from an expiry, which changes positioning on a known date with no price move. That is what separates "positioning" from "we just had a selloff", which otherwise always arrive together.

## What the papers already settle (not to be re-tested)
* Dealer gamma changes the size of moves. Three datasets with true positions agree. The effect is modest.
* S&P 500 options are no longer overpriced on average. The VIX now runs about 10% above realized volatility, down from about 25%.
* **In short-dated S&P options, customers sell at the money.** Market makers are long gamma in 88% of ten-minute intervals (2018–2024). The public "GEX" measure assumes customers sell calls and buy puts. At the short end that sign is wrong.
* Dealer long gamma builds through the week before an expiry and vanishes at the close.

## What is ours to test, in this order
1. **Calibrate (no state involved).** On our S&P data, realized ÷ implied since 2012 should average 0.9–1.0. If it does not, our measure of the implied move is wrong and has to be fixed first. Reproduce the gamma → range result with a signed and an unsigned gamma measure.
2. **Look first.** Ten individual cases before any statistic: five entries after selloffs, five in calm markets, with the option's price path.
3. **The expiry test (P2, P3).** Implied volatility of a fixed contract 30–60 days out, Thursday close to Monday close across each monthly expiry, against all other two-day windows.
   * SPY: 47 expiries in the option quotes we hold (Dec 2022–Oct 2026). TSLA: its chains have to be pulled again, about 80 expiries since 2020.
   * Power: against a two-day change with a standard deviation of about 5–6% (my guess, to be replaced by the measured figure), a 3% shift gives t ≈ 3.4 for SPY and above 5 for TSLA. Adequate.
4. **P1 in the owner's units.** Fold it into the structure table (queue step 2): naked call against spread, by state, in real option prices.
   * Power, honestly: as a ratio test on five-session windows, P1 can detect a gap of about 0.14 before May 2022 and about 0.21 after (assuming a standard deviation of 0.45 for the log ratio, a guess). That is at or above the top of the predicted range, so a ratio test alone would most likely come back "no clear difference". What it can do is rule out a large gap in the wrong direction, which is the decision that matters: do not buy naked calls into fear. This is why P1 goes into the structure table and the expiry test goes first.

## What this changes in the map
* **Step 1's wording was half wrong.** I wrote that options should be cheapest after a big expiry "because positioning clears". The papers say they do get cheaper then in single stocks, but because writers sell again, and the sign flips where customers are buyers.
* **The open item on which gamma measure to trust (N1):** signed open-interest proxies are unreliable for short-dated S&P options. Test an unsigned one.
* **Regime dates to respect, never pooled across:** about 2012 (dealers stop being short index options) and May 2022 (daily expiries).

## Where I may be wrong: for the owner to challenge
1. **I assume dealers price what they know.** If quotes follow recent realized volatility with a lag, there is a short window, the first day or two after positioning turns, in which low gamma is not yet priced. Your screen time can say whether that window exists.
2. **We see only the sum.** With our data the dealers' forecast and their charge cannot be separated. P1 tests the sum.
3. **TSLA is not the average stock.** Every paper here is about the index or the average of thousands of stocks. TSLA has heavy retail call buying. P3 exists because I do not know its sign.
4. **The sizes are small.** A few percent of premium. For a naked call, direction dominates. This matters most for structure (spread or naked) and for the day of purchase, less for whether a trade wins.
5. **From your experience:** has buying calls into fear cost you through the volatility crush more than buying in quiet markets? Do TSLA calls look cheaper or dearer on the Monday after monthly expiry?

## Papers read in full for this (cards in `memory/papers/`)
| Paper | What it gives |
|---|---|
| Gârleanu, Pedersen & Poteshman (2009), *Demand-Based Option Pricing* | Fact 2: the price depends on dealer inventory, in proportion to risk that cannot be hedged |
| Ni, Pearson, Poteshman & White (2021; 2006 draft read), *Does Option Trading Have a Pervasive Impact…* | Fact 1 in single stocks, with true positions |
| Barbon & Buraschi (2021), *Gamma Fragility* | Fact 1 in 2010–2020; the effect scales with illiquidity |
| Amaya, Garcia-Ares, Pearson & Vasquez (2025), *0DTE Index Options and Market Volatility* | Fact 1 in the S&P is small with true positions |
| Adams, Dim, Eraker, Fontaine, Ornthanalai & Vilkov (2026), *Do S&P 500 Options Increase Market Volatility?* | Market makers are usually long gamma; customers sell at the money; gamma builds into expiry |
| Dew-Becker & Giglio (2026), *The decline of the S&P 500 variance risk premium* | The index-option premium vanished when dealers stopped being short |
| Garcia-Ares & Muravyev (2025), *Option returns: a tale of the expiration rollover day* | Option prices fall on roll days; the sign follows who is rolling |

Not read in full, not built on: Baltussen, Da, Lammers & Martens (2021); Chen, Joslin & Ni (2019); Lipson, Tomio & Zhang (2023).

**Files:** `figure.py` → `out/derivation.png` (a diagram of the predictions; it contains no data).
