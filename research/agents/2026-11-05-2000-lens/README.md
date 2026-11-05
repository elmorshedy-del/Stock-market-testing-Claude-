# 2000 vs now: a wide-lens read (descriptive; no test, at the owner's request)

**Agent / session:** Claude, for the owner, 2026-11-05 afternoon.

**Owner:** "Tell me about the 2000 red November … Was the year trajectory similar? Similar breadth rotation? Types of fall. Relative macro? … Don't set up a test."

**Status:** reasoning plus data. No hypothesis test. One historical episode, so read it as a map, not a forecast.

## Data
* **Yahoo:** ^NDX, ^SOX, ^NYA, ^RUT, ^GSPC, ^VIX, sector SPDRs (launched Dec 1998).
* **FRED:** DFF, DGS2, DGS10, T10Y2Y, BAA10Y, BAMLH0A0HYM2 (3 years only), WTI, UNRATE, core CPI y/y.
* Raw files are kept out of git. `figure.py` rebuilds `out/2000_vs_now.png` from them.

## What the data says
**Year shape**
* In 2000 the NDX top was Mar 27 (4,705). It hit a May 23 low (3,023, −36%), made a lower high in September (4,099), and broke the May low in November (Nov 30: 2,507). NDX was −29% from its peak by Nov 5 and fell another −24.5% by Nov 30.
* In 2026 the NDX made a June high (30,661), a Jul 29 low (27,192), and a *higher* high on Oct 6 (31,224). Today (27,113, live) it sits at the July low, −13% from the peak.

**Chips led the way down in both years**
* SOX peaked Mar 10, 2000, made a lower high Jun 21 (−5%), and was −43% by Nov 5 and −59% by Nov 30.
* SOX peaked Jun 22, 2026, made a lower high Oct 6 (−10%), and is −36% today, 97 sessions from the peak. In 2000 it was about −20% at the same age, so this one is faster.

**Rotation**
* 2000, from the NDX peak to Nov 3: staples +30%, utilities +29%, financials +19%, energy +12%; tech −31%; average NYSE stock +2%.
* 2026, from the NDX peak to today: health care +13%, staples +13%, financials +8%, utilities +6%; tech −18%; NYSE +1%.
* Same shape, compressed into one month instead of seven.

**What November 2000 added: contagion**
* From Nov 3 to Nov 30, 2000 everything fell except staples (+5%) and utilities (+1%).
* NDX −24.5%, SOX −27.5%, Russell −12%, S&P −7.8%. The average NYSE stock also fell (−4.8%).

**Macro**
| | Nov 2000 | Oct–Nov 2026 |
|---|---|---|
| Fed | done hiking at 6.5%; 2y 5.88 < fed funds 6.51, so pricing cuts | **hiked Sep 17** (3.63 → 3.88); 2y 4.74 > fed funds, so pricing more hikes |
| 10y | falling (6.7 → 5.7) | rising (4.2 → 5.1) |
| Curve | inverted | positive |
| Baa−10y spread | **widening** (1.67 → 2.56) | **tight** (1.67 → 1.46) |
| HY OAS | — | 2.7 → 3.2 in Oct, a first uptick from very tight |
| Oil | $34 (+36% y/y) | $102 (+70% YTD) |
| Core CPI | 2.6% | 2.6% |
| Unemployment | 3.9% | 4.2% |

## Reading
* **What rhymes:**
  * The rotation out of a capex-boom tech complex into defensives, while the average stock holds.
  * Chips leading the way down (peak, lower high, collapse).
  * An oil shock alongside a tightening Fed.
  * VIX in the mid-20s.
* **What differs:**
  * The index made a new high one month ago (2000's November came 8 months after the top, after a failed lower high).
  * Credit is tight (2000's spreads had widened about 0.9 pt by November).
  * Yields are rising, not falling. The pressure is the discount rate and positioning, not an earnings collapse with credit closing.
* **Phase:**
  * The macro and the index structure look like **spring 2000**: the Fed tightening, rates high, the first break, and a rotation that protected the average stock.
  * They do not look like **November 2000**, when the Fed was done, yields were falling on a growth scare, credit was cracking, earnings warnings were spreading, and contagion hit the average stock.
  * Chips alone are further along.
* **What turned spring 2000 into November 2000 (watch list):**
  * supplier earnings warnings and capex cuts;
  * credit spreads widening (HY OAS ticked up in October);
  * the average stock (NYA/RSP) breaking down.
* **History note:** after the spring-2000 break, the NDX rallied +36% (May 23 → September) before the real breakdown. "A big bounce is likely" and "the top may be in" were both true then.
