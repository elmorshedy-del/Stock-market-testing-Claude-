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
