# Does November rescue a weak start? And is there a monthly cycle that flips in bear markets?

**Agent / session:** Claude, for the owner, 2026-11-05 ~10:30 ET (session 4 of November). **Pre-registered at commit:** the commit that first adds this README.

**Owner:**
* "Even in bear markets Novembers close almost flat or up. Was there any November following this same pattern of breakdown and especially rotation out of tech … be smart with it."
* "In bull markets it's usually first weeks the strongest then moves slow down as monthly options pile up. Is this just the opposite: the typical month but bear market?"

## Data
* Yahoo daily: ^GSPC (1950–), ^NDX (1985–).
* SqueezeMetrics GEX (2011–) for the options mechanism.
* Today's row is live intraday and **provisional**.

## Definitions (fixed before computing)
**Month timing**
* Session k = the k-th trading day of the month.
* **Start** = last close of the prior month → close of session 4. Today is session 4 of November.
* **Rest** = session-4 close → the month's last close.
* **Weak start** = start return in the bottom 20% of all months, 1950–Oct 2026.
* **Tech-rotation start** = NDX/SPX ratio start return in the bottom 20% of all months (1985–).

**Regime**, set at the prior month's last close
* **Bull:** S&P ≥ its 200-day average.
* **Bear:** below it.
* Secondary check: drawdown from the 252-session high ≥ 20%.

**Month segments**
* S1 = sessions 1–4.
* S2 = session 5 → the Friday before expiry week.
* S3 = expiry week (Monday → 3rd Friday; the prior session if that Friday is a holiday).
* S4 = after expiry → month end.

**Movement size** = mean |daily return| in the segment ÷ mean |daily return| over the 60 sessions before the month starts.

## Questions and tests
**Q1. November** (owner's claim first, then the smart version)
* N1, descriptive: share of Novembers ≥ −1% (flat or up), all and in Bear months, with the list of losers.
* **P1:** after a weak start, is November's rest of month better than the rest of month in other months?
  * Difference in means; 10,000 permutations of month labels within weak-start months; one-sided.
  * Needs ≥ 8 weak-start Novembers.
* N3, descriptive: Novembers with a tech-rotation start (1985–), with the rest-of-month result for SPX, NDX and the ratio.

**Q2. Monthly cycle**, with one observation per month (no daily-level overcounting)
* **P2, Bull, returns:** S1 mean daily return > the rest-of-month mean daily return (owner: "first weeks the strongest").
* **P3, Bull, movement:** movement size in S1 > S3 (owner: "moves slow down as options pile up").
* **P4, Bear, the opposite:** S1 mean daily return < the rest-of-month mean daily return.
* Test for each: t-test on per-month differences, plus a bootstrap over months (10,000); one-sided.
* Robustness: the same in 1950–1999 vs 2000–2026. Listed options grew hugely after 2000; if "options pile up" is the mechanism, it should be stronger later.

**Mechanism, descriptive, 2011–:** mean GEX percentile by segment, Bull vs Bear. If options pile up into expiry, GEX should rise S1 → S3 and fall in S4.

**Q3, descriptive:** a weak start, then the rest of the month, by regime. Where today sits.

## Pass rule
* Holm across P1–P4; pass at adjusted p < 0.05.
* Every number is reported with its n.
* Small n means "can't say".

## Reproduce
`python cycle.py <DIX.csv>` → `out/cycle.json`, `out/months.csv`
