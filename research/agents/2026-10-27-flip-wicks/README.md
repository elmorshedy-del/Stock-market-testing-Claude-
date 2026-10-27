# Does SPY wick at its gamma flip, and pin at the close? Motivating days, then a pre-registered test

* **Owner, 2026-10-27:** "Spy wicked this price level multiple times. I think it was the flip. Can we understand why it behaved this way at it, with supporting data, especially at close. That doesn't seem post hoc."
* **Prior work:**
  * [spy-gamma-levels](../2026-10-25-spy-gamma-levels/) (rallies above the flip hold);
  * [spy-intraday-levels](../2026-10-16-spy-intraday-levels/): on one partial day, intraday turns were no closer to option levels than to round strikes, p 0.54–0.67;
  * [dealer-sign](../2026-10-16-dealer-sign/): the classic convention is supported for calls; call gamma damps SPY's range;
  * [positioning-tests](../2026-10-26-positioning-tests/) P4b: round numbers hold resting orders;
  * Ni, Pearson & Poteshman (2005, *JFE*): stocks pin to strikes at expiry when hedgers are net long options.

## The pre-open map (`flipmap.py`)
* **Built only from what is known before day D's open:**
  * positions = OI dated D (the prior close's positions);
  * IVs and spot = the prior session's closing chain.
* **Same-day (0DTE) expiries are kept,** with time to expiry measured from 9:30. Our earlier maps dropped them, so their flip ran $2–4 higher.
* Engine code is imported unchanged. The one addition is a $0.05 search inside the engine's 0.5%-wide flip interval.

## Motivating days, descriptive (`recent.py`; `out/recent.json`). These days are EXCLUDED from the test below.
| Day | Pre-open flip (incl 0DTE) | Open | High | High − flip | Close − flip |
|---|---|---|---|---|---|
| Oct 14 | 777.19 | 774.92 | 776.35 | **−0.84** | −7.58 |
| Oct 15 | 772.37 | 766.25 | 772.87 | **+0.50** | −0.66 |
| Oct 16 | 773.75 | 773.24 | 773.25 | **−0.50** | −10.44 |
| Oct 19 | 770.48 | 767.23 | 770.46 | **−0.02** | −3.94 |
| Oct 20 | 771.76 | 765.86 | 772.29 | **+0.53** | −2.74 |
| Oct 21 | 772.55 | 771.17 | 774.44 | +1.89 | +0.58 |
| Oct 22 | 773.57 | 766.39 | 767.71 | −5.86 | −9.58 |
| Oct 23 | 771.39 | 759.90 | 763.47 | −7.92 | −11.48 |
| Oct 26 | 770.88 | 762.25 | 767.73 | −3.15 | −5.65 |
| Oct 27 | 770.34 | 767.34 | 771.14 | **+0.80** | −0.62 |

* **Six of the 7 days that reached the flip** saw the high stop within $0.84 of it, and 5 of those 6 closed back below it. The flip without 0DTE (772.6–777.4) fits worse.
* **Oct 27, as the day ran down** (same positions; the 0DTE time to expiry shrinks):
  * The flip moved from 770.34 (9:30) to 770.14 (12:00), 769.67 (15:00), 769.57 (15:45) and 768.12 (15:55).
  * Total dealer gamma at 770 went from −$0.63bn (9:30) to +$0.54bn (15:00), +$1.54bn (15:45) and +$4.1bn (15:55).
  * The late session was **long gamma** around 770, so dealers sold rallies and bought dips.
* **Oct 27 0DTE open interest:**
  * Calls 770: 9,041; 775: 8,082; 768: 7,766; 767: 7,433.
  * Puts 767: 20,530; 765: 12,455.
  * The close, 769.72, came $0.28 from the 770 strike.
* **Hypothesis from these days:**
  1. Below the flip, dealers chase, so price is carried up to the flip.
  2. Above it, they fade, so price stalls and wicks back.
  3. Into the close, 0DTE gamma concentrates and the session turns long gamma, so price pins to the big 0DTE call strike.
* These are post hoc readings of 10 days. The tests below decide whether they are real.

## Pre-registration (written before any historical computation)
**Sample:** SPY, 2020-01-02 to 2026-10-12 (everything before the motivating days). Daily OHLC from Yahoo (unadjusted for dividends, matching strikes).

**H1. The flip as a ceiling from below (and a floor from above)** (`history.py`).
* **Level** L = the pre-open flip including 0DTE.
* **Up-approach days:** open < L. A day "reaches" when high ≥ L·(1 − b).
  * **Stall** = high ≤ L·(1 + b): the day stops inside the band instead of running through.
  * **Reject** = close < L.
* **Down-approach mirror:** open > L; reach = low ≤ L·(1 + b); stall = low ≥ L·(1 − b); hold = close > L.
* **Null:** circularly shift each day's relative level (L / open − 1) by k sessions, k in [20, N − 20], 500 shifts. This keeps how far levels sit from the open and destroys their link to that day's positions. Statistic: real share minus the null mean. p = share of null ≥ real, one-sided.
* **Primary:** up-approach Stall and Reject at **b = 0.15%**. **Passes if both p < 0.05.**
  * Stated plainly: b = 0.15% and "incl 0DTE" were chosen after seeing the table above. Hence the multiverse.
* **Multiverse:** b ∈ {0.05, 0.10, 0.15, 0.25, 0.40}% × {up, down} × {stall, reject/hold} × {incl, excl 0DTE} = 40 cells. Joint p from the median z across cells under the same shifts.
* **Splits (descriptive):**
  * 2020–22 vs 2023–26 (the daily-0DTE era);
  * whether L is within $0.50 of a $5 multiple (the round-number confound, P4b).

**H2. Closing pin to the big 0DTE strike** (`pin.py`).
* **Sample:** days with a same-day expiry, 2023-11-27 to 2026-10-12 (SPY hourly bars give the 15:30 price, the open of the 15:30 bar).
* **Candidates:** integer strikes within ±$3 of the 15:30 price. K* = the candidate with the largest 0DTE OI (calls + puts, prior close's positions).
* **Outcome:** close within $0.50 of the strike.
* **Statistic:** hit rate at K* minus hit rate at the other candidates in the same $1 distance bucket from the 15:30 price, weighted by K* counts. Bootstrap by day, 2,000 draws.
* **Prediction:** > 0. **Passes if p < 0.05.**
* **Sign split (tests the convention):** K* call-heavy (classic: dealers long → pin) vs put-heavy (classic: dealers short → no pin). Prediction: the pin is stronger when call-heavy.

**What would falsify the owner's reading:** H1 at or below the null means the flip wicks were coincidence (or round numbers). H2 at or below zero means the close behaviour was not a pin.
