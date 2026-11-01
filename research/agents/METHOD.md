# How we test: a physicist's protocol for a chaotic market

*Written 2026-11-01 at the owner's request: "Be like a physicist or scientist dealing with a chaotic system with many variables… Identify exactly how they think and think like them." Every study follows it. Add to it; don't rewrite it.*

1. **Predict statistics, not paths.**
   * A chaotic system loses point predictability fast, as weather does after a few days.
   * What stays predictable is the *distribution*: range, volatility, the odds of touching a level, continuation vs reversal odds.
   * Forecasts are probabilities, judged by calibration ("when we said 60%, it happened ~60%").
2. **Mechanism first, then a derived prediction.**
   * Start from a constraint the market cannot escape: an accounting identity (the order book), a hedging obligation (dealers' delta), a boundary condition (expiry at 16:00, the closing auction), a scheduled flow (month-end).
   * Derive the sign, and a magnitude bracket, **before** looking at the data.
3. **Find the control parameter; draw the phase diagram.**
   * Many variables matter, but a few switch the *regime*. Dealer gamma, for example, flips the market between damped and amplified.
   * Test the system's **response** (variance, autocorrelation, impact) as a function of that parameter. Look for a dose–response and a sign change at the critical point (the flip).
4. **Simpson's paradox in phase space.**
   * Pooling two regimes with opposite responses gives a near-zero average.
   * A "weak" pooled effect (the 09:35 rule, last-half-hour momentum) may be two strong, opposite effects mixed together. Split by regime before declaring it dead.
5. **Dimensionless variables.**
   * Measure moves in natural units: the day's expected move from VIX, the implied move, ATR.
   * Measure distances to levels in the same units, so days with different volatility are comparable and the result can't be a vol-level artefact.
6. **Separate timescales.**
   * Microstructure noise (seconds), hedging feedback (minutes to hours), regime (days to weeks).
   * Coarse-grain to the timescale of the mechanism being tested.
7. **Calibrate the instrument on a known law first.**
   * Before a new claim, reproduce an established one with the same data and code (e.g. gamma regime → realized volatility).
   * If the known law fails, the instrument is broken, not the market.
8. **Natural experiments over correlations.**
   * Use days where the control parameter changes for reasons unrelated to the outcome: expiries, index events, scheduled releases.
   * Compare like with like.
9. **Nulls that keep the structure.**
   * Use circular shifts, block bootstraps and surrogate series that preserve persistence and clustering. Naive shuffles flatter results in persistent data.
10. **A small budget of hypotheses.**
    * Few, pre-registered, with a multiverse of reasonable variants reported in full.
    * No dragnet. Holm across the family.
11. **Cross-check two observables of one mechanism.**
    * If feedback is real, it must show up in *both* the variance and the autocorrelation, with mutually consistent sizes. One observable alone can be a coincidence.
12. **Report what failed and why it matters.**
    * A failed prediction narrows the mechanism. Every null is written down, with its denominator.
13. **Follow the anomaly, with discipline** (owner, 2026-11-01: "be curious and persistent … investigate it … space to wander and question").
    * When a test throws up something unexpected, chase it. Many real findings were found while looking for something else.
    * But chase it the way a scientist does:
      * (a) label it **exploratory** the moment it is seen;
      * (b) rule out artefacts first (data errors, units, one outlier period, a timing bug);
      * (c) state a mechanism that would produce it;
      * (d) derive a second, independent prediction from that mechanism;
      * (e) confirm on data that played no part in finding it (a held-out period, another instrument, a later date), pre-registered.
    * An anomaly that survives (b)–(e) becomes a finding. One that doesn't is written down as a curiosity, with why it failed.

### What rule 13 means, anchored to history (owner, 2026-11-01: "anchor that curiosity part to historical examples")
**The curiosity that paid off, and the persistence each case needed:**
| Case | The anomaly noticed in passing | What made it a discovery |
|---|---|---|
| **Röntgen, 1895** | While testing cathode rays in a covered tube, a fluorescent screen across the room glowed | Seven weeks of systematic characterisation (what it passes through, what casts shadows) before publishing **X-rays**: steps (b)–(d) |
| **Becquerel, 1896** | He expected sunlight to make uranium salts expose plates. On cloudy days he developed the unexposed plates anyway, and they were fogged | Checking the "control" that wasn't supposed to matter revealed **radioactivity**. *Look at the boring baseline* |
| **Fleming, 1928** | A mould contaminating a culture plate had cleared the bacteria around it | He noticed (a) and published, but did not persist. It took Florey and Chain a decade later to purify **penicillin**. *Curiosity without persistence stalls* |
| **Lorenz, 1961** | Re-running a weather model from a printout rounded to 3 decimals instead of 6 gave a completely different forecast | He refused to call it a computer glitch, traced it to sensitive dependence, and founded **chaos theory**. *The "error" was the finding*, and it is why markets are forecast as distributions |
| **Mandelbrot, 1963** | Cotton-price changes had far too many large moves for the Gaussian model | He measured the tails across scales and found **scaling (fat tails)** in markets. *An anomaly in the dull statistics overturned a whole model* |
| **Penzias & Wilson, 1964** | A persistent hiss in a radio antenna | They cleaned out pigeon droppings and ruled out every instrument cause (b). Then they matched Dicke's prediction (c): the **cosmic microwave background**, later confirmed by its blackbody spectrum (d–e) |
| **Bell Burnell, 1967** | A quarter-inch of "scruff" on ~400 feet of chart paper | She refused to dismiss it, timed the pulses, ruled out man-made interference, then found a **second** source (e): **pulsars** |
| **Rubin, 1970s** | Galaxy rotation curves stayed flat where they should fall | She measured galaxy after galaxy until the pattern was undeniable: **dark matter**. *Persistence across many independent cases* |

**The cautionary cases, which are why steps (b)–(e) exist:**
| Case | What went wrong | The safeguard |
|---|---|---|
| **N-rays, 1903 (Blondlot)** | Observers "saw" rays that didn't exist. When Robert Wood secretly removed the prism, they still saw them | Blind tests; pre-registration |
| **Cold fusion, 1989** | An exciting excess heat that others could not reproduce | Independent replication (e) |
| **OPERA "faster-than-light" neutrinos, 2011** | A loose fibre-optic connector produced a timing artefact | Hunt for the boring explanation first (b); the team asked others to find their error |
| **Market anomalies (January and weekend effects, many published factors)** | Many shrink or vanish after discovery. McLean & Pontiff (2016) find returns about 30–60% lower after publication | Hold-out periods, era splits, mechanism-backed predictions (c–e) |

**So in our loop:** when a test shows something odd, the Lorenz/Bell Burnell instinct is to stop and look rather than move on. The Penzias/OPERA discipline is to kill the artefacts first. A finding needs a second, independent footprint (Bell Burnell's second pulsar, the CMB's spectrum) before it changes a trade.
14. **Pilot first, scale on promise, with a pre-set sequential rule** (owner's data budget, 2026-11-01).
    * Start with the cheapest data that can *falsify* the idea.
    * If it survives, expand in small chunks, and decide the stopping rule **before** looking: e.g. combine chunks by Stouffer z; confirm at z ≥ 3, abandon if the running estimate sits on the wrong side after a set amount of data.
    * Expanding only when results look good, without a pre-set rule, is optional stopping. It manufactures significance.
