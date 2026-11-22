# The discovery system: how we surface relationships and predictors

**Adopted 2026-11-22**, at the owner's request: "There must be a rigorous system we follow to surface relationships. And predictors." Before it, each study was one hand-built idea with its own ad hoc test. This system replaces that for any search for relationships. Mechanism-first work (`2026-11-16-price-law/`) stays; it now acts as the filter that turns a discovered candidate into a trusted law.

## The idea in one paragraph
Let the data propose and let discipline dispose. Build a large, deliberate set of candidate variables: levels, speeds, accelerations and co-movements, at several time scales. Search them with methods that can see nonlinear and conditional links. Then kill almost everything with controls that measure how much "skill" pure chance would produce in the same search. Only what survives out of sample, across eras and against those nulls, and then gets a mechanism, is believed.

## The eight stages
1. **Fix the question.**
   * The target is a future quantity at a stated horizon. Examples: realized volatility over the next 4 weeks; the worst drawdown over the next 13 weeks; whether a fall of 10% or more happens within 13 weeks; the return over 4 or 13 weeks.
   * The benchmark is the forecast that needs no work: the last value, the base rate, the average. Skill means beating the benchmark.
2. **Point-in-time data.** Every input is used only from the day it was known. Monthly releases are lagged; weekly indexes are lagged to their release day. A look-ahead leak invalidates everything downstream.
3. **Lock a holdout before looking.** The most recent years are sealed (the lockbox). Discovery uses only earlier data. The lockbox is opened once, for the final candidate list, and the result is reported whatever it is.
4. **Build the hypothesis space systematically, not by taste.** For each base series:
   * level and its z-score against the last 3 years;
   * change over 1, 4, 13 and 52 weeks;
   * speed: the change divided by its normal size (how fast relative to usual);
   * acceleration: the latest 4-week change minus the one before.

   Plus co-movement (rolling correlations of stocks with bonds, gold, the dollar, the yen, oil, credit and Japan, at 13 and 52 weeks, and how fast those correlations are changing) and system measures (the share of all cross-asset movement explained by one common factor; volatility ratios; drawdown from the high). The count of candidates is recorded, because every candidate is a chance to be fooled.
5. **Search with several lenses.**
   * *Screen:* rank correlation of every candidate with every target.
   * *Nonlinear:* distance correlation, which catches U-shapes and thresholds that a correlation misses.
   * *Environments:* gradient-boosted trees, which split the data into conditions by themselves, explained with SHAP. SHAP interaction values show which variables matter only in which environments.
   * *Lead and lag:* PCMCI, which tests whether X helps predict Y after accounting for Y's own past and other drivers.
   * *Formulas:* symbolic regression, later, on survivors only, to look for a compact law.
6. **Measure what chance would produce.**
   * *Autocorrelation-preserving nulls:* slide the target in time against the features (circular shift) hundreds of times and rerun the same search. Real skill must beat the 95th percentile of this null. This prices in the whole search, not just one test.
   * *Purged walk-forward:* fit only on the past, skip a gap the length of the horizon, predict the next year, roll forward. Never random K-fold on time series.
   * *Multiple testing:* Benjamini–Hochberg false-discovery control across every feature × target pair.
7. **Demand stability.**
   * The same sign in each decade.
   * Survival when settings change (window lengths, thresholds): a multiverse check.
   * Replication on a second market where possible (for example the Nikkei, or TSLA).
8. **Mechanism, then confirm.**
   * A survivor is only a candidate until it has a mechanism: who is forced to trade, and why the price has not adjusted.
   * The confirmatory test is pre-registered with its exact rule, then run once on the lockbox and logged forward on the scoreboard.

## What is reported, always
* The number of candidates searched.
* Skill out of sample against the benchmark, with the null's 95th percentile beside it.
* The effect in the owner's units (volatility points, drawdown odds, option P&L).
* What failed.

## What this system does not allow
* Choosing variables after looking at the result.
* Reporting in-sample fits as findings.
* Pooling across eras without checking that the relationship holds in each.
* Opening the lockbox twice.
