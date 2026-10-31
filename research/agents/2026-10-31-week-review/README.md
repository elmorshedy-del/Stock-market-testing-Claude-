# Week review (Oct 26–30): scorecard of Friday's calls, the "stealth bear market" note, and the week ahead

* **Owner, 2026-10-31:** pasted a third-party note: "the 'stealth' bear market is in full swing … Nasdaq 100 erased −$4 trillion in 25 days … the 'S&P 500 Excluding AI' hit a record high … AI stocks fell over −13% in October while the S&P 500 excluding AI gained +8% … ~58% of the S&P 500 is down −20% or more … we believe the market is ultimately setting up for its next leg higher."
  * The owner's ask: "This week ended very interestingly. Do a full analysis based on all our strong points."
* The note is third-party content. Its claims are checked against our data where possible, never taken as given.
* **Plan:**
  * (1) Score the pre-stated calls from [2026-10-30-live-read](../2026-10-30-live-read/) against Friday's tape.
  * (2) Check the note's claims on our data.
  * (3) Read the week ahead from every tested rule: ladder, channel dip rule, month-end give-back, election VIX, TSLA states.
  * (4) One new pre-registered test, D2, below.

## Pre-registration D2 (written and pushed before computing): what follows a record tech-vs-rest divergence?
* **Why:** the note's thesis is that a stealth bear in AI inside a bull in everything else sets up "the next leg higher". Our channel theory says the same thing in mechanical terms. Rotation inside the index (money moving, not leaving) is the bounce signature, and synchronized selling is the correction signature.
* **Data:** Yahoo adjusted daily closes for RSP (equal-weight S&P, 2003-05+), QQQ (Nasdaq-100) and ^GSPC.
* **Signal:**
  * spread = RSP 20-session return − QQQ 20-session return.
  * **Event:** spread ≥ its 97.5th percentile, computed only on data before that day (expanding window, at least 500 days of history), **and** RSP within 2% of its 252-day closing high.
  * Only the first day counts, and events must be at least 20 sessions apart.
* **Outcomes:**
  * (a) S&P 20-session forward return.
  * (b) P(an S&P up-leg starts within 20 sessions). Up-leg = a top-decile 10-session S&P rise, the ladder's definition.
  * (c) QQQ 20-session forward return: does tech rebound?
* **Baselines:**
  * All days.
  * Matched dip days: S&P ≥ 2% below its 10-day high. This separates the divergence from the dip itself.
* **Statistics:** event means vs baseline. p from 5,000 random draws of the same number of baseline days, each at least 20 sessions apart. 90% bootstrap CIs over events. Every n is reported.
* **Prediction:**
  * (a) and (b) above both baselines; the rotation theory says bounce.
  * (c) no prediction; tech could keep lagging.
  * Confidence is low: expect roughly 10–25 events.
* **Regimes:** results split pre-2020 / 2020–21 / 2022+ per OWNER_NOTES, descriptive given the n.
* **Today's value** is reported, not used to tune anything.
