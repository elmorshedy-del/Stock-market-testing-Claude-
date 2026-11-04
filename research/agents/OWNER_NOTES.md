# What the owner is trying to get at (keep in view for every study)

*Started 2026-10-29. Add to it; don't rewrite it.*

## Regimes (owner, 2026-10-30: "the option world is different post 2020")
* Test every option-linked idea **per regime**: R0 before 2020, R1 2020–21 (the retail call boom), R2 2022+ (the 0DTE and daily-expiry era). Never pool across eras without showing each one.
* Single-stock options before 2020 need ThetaData Standard; the current plan is Value (2020 onward).

## How to treat the owner's words (owner, 2026-10-30)
* The owner is an observer using loose terms ("forced", "genuine", "vacuum", "house of cards"). **Never adopt the words as definitions.**
* Derive the construct from mechanics and the literature, measure the outcome directly, and test several footprints against it. Say which definition was used and why.
* The 2026-10-29 house-of-cards study took "forced = price up with implied vol up" as given; the owner flagged that. The redo is [permanence](2026-10-30-permanence/).

## The goal
* **Better exits on short-term calls.** The same position kept most of its profit or gave back half or more, depending on a day (or an hour) of exit timing. Sept 2, 2020: exiting at the open vs at the close was the difference.
* **Rules, not hand-drawn lines.**
  * Support and resistance are real ideas (our work agrees: highs and lows cluster at round numbers and gamma walls; the pre-open flip stalls price).
  * Manual line placement and day-early or day-late calls are what fail.
  * Exits should key off mechanical levels and the *state of the flow*.
* **Every test should help a trade, directly or by explaining the mechanics.** Statistics is the referee, not the source of ideas.

## The owner's thesis: "house of cards" (stated 2026-10-29, after the gap studies)
* **What drives it:** some rallies, including the days into a gap-up like Sept 2, 2020, are not lasting price discovery. They are forced inflows, for example dealers hedging customer call buying, rising in a relative liquidity vacuum.
* **How it ends:** at exhaustion the move collapses as fast as it was built, because nothing genuine was holding it.
* **Prediction:** the more forced the run-up, the more violent and quicker the unwind, and the more an exit at the open beats holding.
* **First evidence (descriptive, 2026-10-29):** in the 10 sessions to Sept 1, 2020, the S&P rose +4.0% while VIX also rose +4.6 points. That combination (S&P 10-day ≥ +2% with VIX up) occurs on 3.7% of days since 1990. Spot up with vol up is the footprint of paying up for upside convexity.
* **Related results already in hand:**
  * forced-flow law: moves on low dealer-gamma days are given back;
  * month-end and Russell moves are given back;
  * earnings-morning gap-ups fade (a scheduled forced flow at the open).

## Tested so far
* **[house-of-cards](2026-10-29-house-of-cards/), 2026-10-29:** the thesis leans the right way but is not proven (Holm 0.20 at best).
  * After a forced run (price and implied vol both up for 10 sessions), a 7-day call held from the gap's open to the close has a median of −2.8% vs +3.7% after a genuine run.
  * Violent fades: 18% vs 13%.
  * Forced index rallies give back half more often (Nasdaq-100 56% vs 29%) but are rare.
  * **Exit tilt:** after a forced run, sell into the open; after a genuine run (vol falling), holding is favoured. Forward-check before sizing.
* **[calendar-mechanics](2026-10-29-calendar-mechanics/), 2026-10-29:** earnings-morning gap-ups are violent fades about 1 in 4 times vs about 1 in 7 (confirmed out of sample, Holm 0.031). Exit or protect calls at the open on earnings mornings.
* **[permanence](2026-10-30-permanence/), 2026-10-30 (the rigorous redo):**
  * "Forced vs genuine" was re-defined as transitory vs permanent price impact and measured as the share of a run kept 20 sessions later.
  * Daily footprints (volume, liquidity, overnight share, dealer gamma, breadth) do not predict it across 5,853 runs.
  * Only call-skew richening (traders paying up for upside calls) points the right way (ρ −0.20, p 0.05).
  * Low-volume runs are the fragile ones (cliff 35% vs 28%).
  * The earlier house-of-cards tilt came from a crude measure; treat it as unconfirmed.
* **Options regimes, 2026-10-30:**
  * The earnings-morning fade got stronger after 2020: violent fades 27–30% vs 13–16%, up from 16% vs 11% in 2018–19. This is the strongest exit rule we have.
  * The price-up + IV-up gap-day fade was mostly a 2020–21 thing.
  * In the 0DTE era, call-skew richening during a run predicts that the run fades (ρ −0.33).
  * **Correction:** the 09:35 rule is weaker than first reported. Strong first 5 minutes → higher next 55 minutes 61% (TSLA/AAPL/NVDA/QQQ) or 55% (others), not 72%, and weak since 2020. A mild tilt only.

## Data budget (owner, 2026-11-01)
* "Don't consume databento quota unless it's highly valuable and if so start small and if results are promising u can consume more. Don't consume a lot in one chunk."
* So:
  * check the cost first;
  * pull the smallest slice that can falsify the idea;
  * expand only after a promising result, in small chunks;
  * never one large pull.

* **TSLA reads (owner, 2026-11-02):** "what are the strong points here that we should keep integrated whenever we analyze tsla". Every TSLA analysis follows `TSLA_PLAYBOOK.md`: the 8-step standard read, with each number tagged proven / map / lean, and Tier-4 failures never used as signals. Update the playbook when a test changes a tier.

## Intraday price source (owner, 2026-11-02): "find more up to date source and make that your intra day source always"
* **Primary: the Twelve Data MCP connector.**
  * `get_quote` for a snapshot (last, open, high, low, change %); `get_time_series` with `interval=1min` for bars.
  * **One symbol per call.** Batch `get_price` fails in CSV mode.
  * Checked 2026-11-02 09:51 ET: the latest 1-minute bar was stamped 09:50, about 1 minute behind the clock. Yahoo was stamped 09:49:14, 2–5 minutes behind; that morning's Yahoo reading called TSLA green when it was already red.
  * **Caveat:** Twelve Data volume here is far below TSLA's consolidated volume (≈ 130k shares at 09:50), likely a single venue. **Use it for price, not volume.**
* **Fallback** (connector down, or inside Python scripts that can't call the connector): the Yahoo chart API. **Always print `regularMarketTime` and the lag vs the clock**, and say it's delayed.
* **Rule:** every intraday price quoted to the owner carries its source and timestamp (e.g. "TSLA 399.39, Twelve Data 09:50 ET").
* Not used for live quotes: Databento (data budget), ThetaData (end-of-day / OI tier), Alpha Vantage (25 calls a day).

## Earnings and the vanna/charm unwind (owner, 2026-11-04)
* **The owner's question:** "why wasn't there any gamma or walls slowing it down in July and now there is". The comparison is in [msft-read](2026-11-04-msft-read/) (`compare.py`).
* **Working explanation, from one case (not yet tested):** walls only slow moves that happen during trading, near strikes with real open interest. They fail when:
  * the options sit far from the price (freed);
  * the move comes as an overnight gap;
  * a big IV crush releases put hedges (vanna) and time decay adds to it (charm);
  * customers chase new calls, so dealers end up short gamma.
* **The owner's goal:** use this to trade earnings.
  * Know ahead of the report whether to own the straddle, sell it, or hold the gap for follow-through.
  * Know whether calls or shares are the better tool after the crush.
* **The tests:** TODO EQ0–EQ7. The highest value is EQ1 (straddle P&L by pre-report positioning).
* **Don't contradict what's tested:** earnings gap-ups fade in the first hour on average (calendar-mechanics B2). Moves made on low dealer gamma fade on average (forced-flow). EQ2/EQ3 ask when those averages break, as in July.
