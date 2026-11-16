# Garcia-Ares & Muravyev (2025). Option returns: a tale of the expiration rollover day. Working paper, version of 20 June 2025
**Read:** the full main text (sections 1–7); tables through the text, not cell by cell; Internet Appendix not read. 2026-11-16. A working paper, not peer reviewed.
**Question it serves:** PRICE (is it priced; when to buy), TIME. Mechanism tags: FORCED, POS.

## Claim
* **Single-stock options get cheaper on two days a month:** the third-Friday expiry and, above all, the Monday after. Investors who are short options (covered-call writers) roll: they buy back the expiring option and sell the next one. Market makers lower the price to absorb the selling.
* **Those two days account for the whole of the average loss from buying options,** and for half or more of 18 published option-return "anomalies". Outside them, average option returns are slightly positive.

## Data
* OptionMetrics, all U.S. optionable stocks above $5, Jan 1996–Dec 2021. One call and one put per stock per month, nearest the money, more than a month to expiry (about 50 days at entry, about 20 at exit).
* Signed option volume by trader type from four Nasdaq exchanges (ISE from May 2005; PHLX 2009; NOM 2011; GEMX 2013), to Dec 2021.

## Method
* Delta-hedged call return with daily rebalancing, scaled by the size of the hedged position (delta × stock price − call price), with the forward-looking-bias correction of Duarte et al. (2022).
* The calendar-month return is split into three parts: month-end to the day before expiry; the day before expiry to two days after; the rest.
* Customer order imbalance = (buys − sells) ÷ trades, by non-market-makers, in event time around expiry, split into opening and closing trades.
* Decile sorts on the post-expiry Monday imbalance; then on 18 anomaly signals, with and without the rollover days.

## Results
* **Order imbalance in non-expiring options:** normally about +1%; **−12% on the post-expiry Monday,** and still negative for several days. Closing buys in the expiring options surge just before and on expiry Friday; opening sells in the next month hit on Monday.
* **Delta-hedged call returns:**

  | Window | Return |
  |---|---|
  | Calendar month | −0.20% |
  | Month-end to the day before expiry | +0.19% |
  | Day before expiry to two days after | **−0.43%** |
  | Rest of the month | about zero |

  Puts: −0.22% for the month, −0.37% in the rollover window, +0.19% before, −0.04% after.
* "Call option prices remain low for the remainder of the month": the drop is not reversed quickly.
* **Sorting on the Monday imbalance:** stocks with heavy selling have significantly negative monthly option returns; stocks where customers were buying have strongly positive ones. The effect comes from opening sales.
* **Strongest for at-the-money and out-of-the-money options;** weak in-the-money. Same pattern in straddles, in weekly and daily returns, and across the sample period.
* **Mondays:** the known "options lose over weekends" effect is concentrated in the Monday after expiry. Without those Mondays the average daily return is not significant.
* **Anomalies:** the average long-short option anomaly earns −0.64% a month (t = −7.8); −0.36% of it (t = −13.7) in the two rollover days. In S&P 500 stocks: −0.10% for the month (t = −1.8) and −0.14% (t = −11.2) in the rollover days, so the rollover is all of it.
* Unreported: selling a call on Thursday and buying it back on Monday, hedged, is profitable after costs in the top decile for S&P 500 stocks.

## Caveats
* **The authors':** four exchanges only; over-the-counter flow is missing.
* **Mine:**
  * Returns are a percentage of the hedged position, not of the option premium. On my arithmetic for a 50-day at-the-money call on a 45%-volatility stock, the hedged position is about seven times the premium, so −0.43% is roughly a 3% fall in the premium, or about 3% off implied volatility (for example 45.0 to 43.7). That conversion is mine, not the paper's.
  * It is an average over thousands of stocks in which customers are net *sellers* of options. A stock where customers are net *buyers* of calls should show the opposite sign on the same days. The paper's own decile sort says so.
  * Sample ends in 2021. Weekly expiries in single stocks spread the roll over more dates than in 1996–2010; the paper says the pattern holds through the sample but shows no post-2020 split in the main text.
  * Monthly expiry only. Nothing on index options.

## What it means for us
* **This is the cleanest "forced flow moves the option price" result we have read, and it is about the day you buy.** Mechanism, in our gate's terms:
  * who is forced: option writers whose position is expiring;
  * who takes the other side: market makers with limited room for inventory;
  * why the price has not adjusted: the flow is concentrated on two days and market makers must be paid to hold it.
* **It corrects my step-1 hypothesis.** I wrote that options should be cheapest after a big expiry because positioning clears. The literature says they are cheaper after expiry in single stocks, but because writers *re-sell* then, not because gamma cleared. Same calendar, different cause, and the cause tells us when it flips.
* **For TSLA the sign is an open, testable question.** If TSLA is a writers' market, calls a month or two out get about 3% cheaper between the Thursday before monthly expiry and the Monday after, and stay cheaper. If it is a call-buyers' market (retail rolling long calls), they get dearer on those days. Either answer is a rule for which day to buy.
* **It supports the wider reading from the other six papers:** who is on the other side sets whether an option is cheap or dear. The size of the next move is the smaller part of the story.

## How we would replicate or extend it on our data
* For TSLA and SPY: implied volatility of a fixed contract, 30–60 days out and near the money, from the Thursday close before each monthly expiry to the Monday close after, against all other two-day windows. Needs daily option quotes (SPY: in `Market_Data` since Dec 2022; TSLA: to be pulled).

## Open questions
* Is there an index version? Funds that write index calls roll on a published schedule.
* Does the size of the drop scale with how much open interest expires?
