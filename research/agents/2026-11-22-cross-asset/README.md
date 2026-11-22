# Why stocks, gold and bitcoin fell together: the macro and cross-asset variables, checked and built into the model

**Date:** 2026-11-22 (Sunday; data to the Friday 20 November close). **Type:** observation + derivation + one forward forecast.
**Owner's prompt:** they pasted an Arabic newsletter article on the selloff and wrote: "We never rly had these variables studied and integrated in our research."
**What we had before:** one descriptive table on 5 November (`2026-11-05-regime-compare`: Fed funds, 2-year, 10-year nominal and real, inflation, oil, Baa spread, CAPE). Never the yen carry trade, gold and bitcoin against stocks, credit spreads day by day, or forced selling across assets, and none of it was built into the model.
**Not pre-registered.** The sign table in `analysis.py` was written before any episode was computed, in the same script, but it was not pushed first.

## The judgement
* **The selloff has two phases with two different mechanisms.**
  * **Phase 1 (3 September to 5 October): a real-rate shock.** The 10-year rose 54bp to 5.31%, all of it real yield. Bonds, gold and the yen fell and the dollar rose. Stocks ignored it and made a record on 6 October.
  * **Phase 2 (6 October to 20 November): forced selling of everything except Treasuries.** Yields *fell* 40bp and long bonds rose 5%, yet gold fell 16%, bitcoin 31%, the Nikkei 20% and the S&P 12%.
* **The article's main cause, rising yields, fits phase 1 only.** It cannot explain phase 2, when yields fell.
* **Its carry-trade story does not show in the data.** Japanese yields did rise (10-year JGB 1.4% → 3.05%), but the yen did not jump. Dollar/yen went from 157.6 to 159.7.
* **Its explanation for gold ("it pays no yield") is contradicted on the worst days.** On the 8 worst S&P days of phase 2, real yields fell and gold should have risen 1.4%. It fell 12.8%.
* **Its deleveraging spiral is supported.** It is the best fit for phase 2, and gold's correlation with stocks rose from 0.11 to 0.46.
* **5 November and 20 November were different kinds of day.** On 5 November gold *rose* 1%: that was a sector crash, AI repriced. On 20 November gold fell 4.6% with yields down 14bp: that was forced selling. The market moved from the first kind to the second in two weeks.

## The article's claims, checked
| Claim | Data | Verdict |
|---|---|---|
| S&P −11.6%, Nasdaq 100 −19.8%, gold −16%, bitcoin −31.2% | S&P −11.6% and Nasdaq 100 −19.8% from the 6 October peak; gold −16.0% from 30 September; bitcoin −29.6% from 30 September, −32.1% from its peak | Right; the bases are mixed |
| 10-year at 5.31% on 5 October, highest since 2002 | 5.31% on 5 October (FRED and Yahoo) | Right |
| Rising yields pushed all assets down | Yields rose to 5 October, then fell 40bp while everything fell. Stocks rose while yields rose | **Phase 1 only** |
| The rise came from debt risk, Japanese rates and tech borrowing (all term premium) | Term premium (Kim–Wright model) +22bp of the +54bp; the 2-year +50bp. Mostly expected Fed policy | **About 40% at most** |
| Yen carry unwind | Yen weaker; the fingerprint that caught August 2024 at 100% matches phase 2 at 50% | **Not visible** |
| Gold falls because it pays no yield | True in September; false on the big phase-2 days, when yields fell | **Phase 1 only** |
| Deleveraging spiral | Best fingerprint for phase 2; correlations up | **Supported** |
| The Fed will hike, not rescue | 3-month bill 4.12% against SOFR 3.91%; 2-year 4.76%. A hike is priced | **Consistent** |
| Nvidia fell on news about its CEO | Not checked | Not checked |

## The mechanism, from first principles
The price-law model (`2026-11-16-price-law/`) says a move is a push divided by capacity, and forced traders change the capacity. Here the forced trader is a **leveraged holder of many assets at once.**

* A holder with equity E and leverage λ owns several assets with weights w_i. The portfolio returns r_p.
* To keep leverage from rising after a loss, it must sell (λ − 1)·λ·E·|r_p|. This is the same identity as a leveraged fund's daily rebalance.
* It sells every asset in proportion to how much it holds, whatever that asset's own news. **The flow into asset j is w_j·(λ−1)·λ·E·r_p.**
* With linear impact, each asset's return becomes:

> **r_j = own news_j + k_j · r_p**, with k_j = w_j·(λ−1)·λ·E ÷ (asset j's capacity)

* The portfolio feeds on itself: r_p = (average own news) ÷ (1 − n), where n = Σ w_i·k_i. That is a runaway at n = 1 under linear impact; under square-root impact there is none unless capacity collapses.

**What follows (each can be checked):**
1. **Co-held assets fall together on the holder's bad days, whatever their own news.** Gold falls on days when yields fall. Observed: yes.
2. **The worst hit, relative to its own news, is where the holder is large against the asset's capacity:** silver more than gold, Korea and semiconductors more than the S&P. Observed: silver −7.4% against gold −4.6% on 20 November (also consistent with silver's higher volatility).
3. **The currency borrowed in rises as loans are repaid.** That identifies who is deleveraging. Observed: the dollar rose and the yen did not, so the leverage is funded in dollars.
4. **Treasuries are bought, not sold, unless funding itself breaks (March 2020).** Observed: bought. So this is forced selling *without* a funding crisis.
5. **When the forced selling ends, the forced part comes back and the news part does not.** Not yet observable; this is the forward forecast below.

This is known in the literature as contagion through common holders (for example Kyle & Xiong 2001; Brunnermeier & Pedersen 2009). **I have not read those papers in full and have not built on them;** the algebra above is the leveraged-fund identity we already used.

## Method: fingerprints
Each mechanism forces a different party to trade, which fixes the sign of seven assets: stocks, long Treasuries, gold, the dollar, the yen, high-yield credit and bitcoin. The signs were written from that reasoning before any episode was computed:

| Mechanism | Who is forced | Stocks | Bonds | Gold | Dollar | Yen | Credit | Bitcoin |
|---|---|---|---|---|---|---|---|---|
| Rate shock | everyone, through a higher discount rate | ▼ | ▼ | ▼ | ▲ | ▼ | ▼ | ▼ |
| Growth scare | no one; money moves to safety | ▼ | ▲ | ▲ | ▲ | ▲ | ▼ | ▼ |
| Yen-carry unwind | yen borrowers repaying | ▼ | ▲ | – | ▼ | ▲ | ▼ | ▼ |
| Dollar-funded forced selling | leveraged holders selling what they can | ▼ | ▲ | ▼ | ▲ | ▼ | ▼ | ▼ |
| Loss of trust in US assets | foreign holders leaving | ▼ | ▼ | ▲ | ▼ | ▲ | ▼ | – |

Observed signs use a dead band of half a typical move over the window, so small moves count as no sign.

## Results
**Check on four episodes with known causes: 3 of 4 right.**
| Episode | Best fit (share of signs matched) | Known cause | |
|---|---|---|---|
| 21 Feb – 18 Mar 2020 | rate shock (86%) | dash for cash | ✗ |
| 3 Jan – 16 Jun 2022 | rate shock (86%) | Fed hiking cycle | ✓ |
| 31 Jul – 5 Aug 2024 | yen-carry unwind (100%) | BoJ hike, yen-funded positions closed | ✓ |
| 2 – 11 Apr 2025 | loss of trust in US (100%) | tariffs; bonds and dollar sold together | ✓ |
| **3 Sep – 5 Oct 2026** | **rate shock (71%)** | | |
| **6 Oct – 20 Nov 2026** | **dollar-funded forced selling (71%)** | | |

* **The 2020 miss is a gap in the table, not luck:** in the dash for cash even long Treasuries were sold, and the table had no such case. What separates 2020 is the scale: high-yield credit −17% and VIX +59 points. Phase 2: credit −1.2%, VIX +21.
* **Phase 2's runner-up fits are 57%.** The giveaway is two columns together: bonds up with gold down. Only forced selling does both.

**Phase 2, the 8 worst S&P days:** stocks and bitcoin fell on all 8; bonds rose on 7; gold fell on 6. The yen barely moved.

**Gold against what real yields and the dollar predict** (fitted on Jan 2023 – Aug 2026: −0.022% per bp of real yield, −1.07% per 1% of the dollar; residual s.d. 1.17%):

| | Gold actual | Predicted from yields and the dollar |
|---|---|---|
| Phase 1 | −5.9% | −1.6% |
| Phase 2 | −16.3% | +2.0% |
| 8 worst S&P days | −12.8% | +1.4% |
| 20 November alone | −4.6% (4.1 s.d. below) | +0.2% |

Even in phase 1, yields and the dollar explain only about a quarter of gold's fall. Gold's sensitivity to real yields has been weak since 2023.

**Correlation with the S&P, daily:**
| | Jan 2023 – Aug 2026 | Phase 2 |
|---|---|---|
| Gold | 0.11 | 0.46 |
| Bitcoin | 0.32 | 0.68 |
| Long Treasuries | 0.12 | −0.19 |

* I expected the link to be stronger on down days than up days (margin binds on losses). With 34 days it is not: gold 0.16 on down days and 0.44 on up days. Not supported on this sample.
* **Credit:** the high-yield spread widened from 2.65% to 3.52% (92nd percentile of three years; April 2025 reached 4.61%). Stress, not a crisis.

## How these variables enter the model
The state had three variables: positioning, liquidity, forced flow. This adds two layers.

1. **The rate layer (slow):** the real 10-year yield, split into expected policy (the 2-year) and term premium; the hikes priced (3-month bill minus SOFR); the high-yield spread. It sets the discount rate and the cost of carrying leverage.
2. **The common-holder layer (fast):** forced flow across assets. Three live gauges, measurable every day:
   * **the gold residual:** gold's move minus what real yields and the dollar predict. Strongly negative on equity down days means forced selling is under way;
   * **the bonds-up-gold-down count** over the last 10 sessions;
   * **the funding currency:** the dollar rising means dollar-funded deleveraging; a yen jump of 2% or more in three sessions with the Nikkei down 5% or more means a yen-carry unwind has started.

## Forward forecast (logged; scored on the due date)
* **F-XA1: from the 20 November close to the 22 December close, gold outperforms the SOX semiconductor index. Probability 60%** (no-skill baseline 50%).
  * Mechanism: about 18 points of gold's phase-2 fall are unexplained by yields and the dollar, so they are forced; semiconductors carry their own news. When the selling stops, the forced part should come back first.
  * It fails if the forced selling continues through December (both fall), or if semiconductors rebound on news.
* **Watch item W-XA1 (no probability):** the yen-carry fingerprint above.

## Caveats
* Sign fingerprints are coarse: they ignore size, and one mechanism can follow another inside a window. Phase 2 contains 5 November, which was an AI sector shock, not forced selling.
* The gold model is linear and fitted on one regime. The 20 November real-yield change is not yet published and is set to zero, which understates the prediction for that day.
* No positions are observed. "Leveraged common holders" is inferred from prices. Margin debt, hedge-fund gross leverage and futures positioning (CFTC) would test it directly.
* The term-premium split depends on one model (Kim–Wright).

## Next
* **The micro level of 5 and 20 November** (the owner's question of 2026-11-16): ES and NQ futures trades with the aggressor side cost about $4.60 for those two days (quote 2026-11-22); top of book for four days about $29. A calm day (27 October) is already held. Waiting for approval.
* Add the three gauges to the daily state card.

**Files:** `prep.py` (data), `analysis.py` → `out/fingerprints.json`, `figure.py` → `out/cross_asset.png`. Raw data in `data/` (gitignored).
