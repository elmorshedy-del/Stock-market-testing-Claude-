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

---

# Results (run ~10:45 ET; Nov 2026 is live and provisional)
Weak start = first 4 sessions ≤ −1.03% (bottom 20%). Tech-rotation start = NDX/SPX ≤ −0.96%. 921 complete months.

**Holm across P1–P4:** P1 fails (adj 1.0), **P2 passes (adj < 0.001)**, P3 fails (adj 0.10), P4 fails (adj 1.0).

## Q1. November
**N1: "even in bear markets Novembers close flat or up"**
* Only partly true.
* All 76 Novembers: 82% closed ≥ −1%, vs 70% for any month.
* The 24 bear Novembers: 71%, no better than an average month.
* Big losers (all bear): 1973 −11.4%, 1987 −8.5%, 2000 −8.0%, 2008 −7.5%, 1974 −5.3%.

**P1: does November rescue a weak start?** Fails.
* After a weak start, the rest of November averaged +0.97% (69% up, n = 13).
* Other months after a weak start: +1.11% (58% up, n = 172).
* Permutation p 0.53.
* November's edge is mostly that it rarely starts weak, not that it repairs a bad start.
* Weak-start Novembers that kept falling: 1973, 1994, 2007, 2008.

**N3: Novembers with a tech-rotation start** (7 cases: 1989, 1993, 1997, 2016, 2018, 2022, 2025)
* The S&P rose over the rest of the month in 7/7 (+0.2% to +8.2%).
* The NDX rose in 6/7.
* But tech's lead over the S&P recovered in only 3/7 (1989, 1993, 2022).
* Across all 99 months with a tech-rotation start, the ratio's rest of month averaged +0.09% (49.5% up), vs +0.28% for all months. No snap-back tendency.

**Exploratory, not pre-registered: extreme tech-rotation starts**
* Today's NDX/SPX start is −3.4%: 2nd percentile of all months, deeper than any November (prior worst: 2022, −2.25%).
* 17 months since 1985 opened ≤ −3%. Eight of them were in 2000–02; July 2026 is one too.
* Over the rest of those months: S&P up only 41% (median −0.19%), NDX up 53%, tech's lead recovered only 41% (median −0.82%).
* Small, overlapping and dot-com-heavy, but it points the other way from the mild-rotation Novembers.

## Q2. Monthly cycle (one observation per month; bull 652 months, bear 260)
S&P average return in bp/day, bull / bear:

| | Days 1–4 | To expiry week | Expiry week | After expiry |
|---|---|---|---|---|
| Bull | 10.8 | 3.3 | 4.8 | 1.8 |
| Bear | 5.7 | −0.7 | −0.2 | 3.0 |

* **P2 passes.** In bull months, days 1–4 beat the rest of the month by 7.9 bp/day (p < 0.001). It holds in both eras: 9.3 bp/day in 1950–99, 5.5 bp/day in 2000–26 (p 0.048). This is the well-known turn-of-month effect, not something new.
* **P3 fails after Holm.** In bull months, moves are only 4.6% bigger in days 1–4 than in expiry week (raw p 0.034, adj 0.10).
  * It is larger after 2000: +6.9% (p 0.05) vs +3.3% in 1950–99 (p 0.14). That is the direction an options-driven story predicts, but it isn't proven.
* **Mechanism, 2012–:** GEX percentile in bull months is 0.57 in days 1–4, 0.62 into and through expiry, and 0.50 after. Options gamma does build into expiry and drop after. The damping of moves it implies is small.
* **P4 fails.** Bear months are not the opposite.
  * Days 1–4 are still their best stretch: +5.1 bp/day over the rest (p 0.87 for the "opposite" claim).
  * Bear-market weakness sits mid-month, into expiry (−0.7 and −0.2 bp/day). Bear months then do better after expiry (+3.0).

## Q3. Weak start → rest of month
* Bull months: +0.63% (58% up, n 111), vs +0.47% for all bull months.
* Bear months: +1.81% (59% up, n 74), vs +0.14%. That is rebound size (bear rallies are big), not reliability.

## Today (live, session 4)
* S&P start about −1.0%, right at the weak-start line (−1.03%); it crossed and recrossed during the morning.
* NDX/SPX start −3.4% (2nd percentile).
* Regime is Bull: S&P was above its 200-day average at the Oct close, 3% off its high.
* Context, descriptive: since Oct 30, AAPL +1.6%, MSFT +3.9%, AMZN +7.0%, GOOGL +1.6%. Meanwhile NVDA −9.0%, AVGO −7.0%, AMD −16.7%, MU −21.1%, ORCL −10.0%, CRWV −22.3%, SMH −11.3%. RSP +1.4%, XLP +4.1%, XLV +3.6%.
* The selling is in chips and AI infrastructure, not in cash-rich megacaps.

**Verdict**
* November seasonality does not rescue a weak start (P1 fails).
* The owner's bull-month cycle is half right: the first days are strongest, but "slowing into expiry" is too small to prove.
* The bear-month "opposite" is wrong: bear weakness is mid-month, not the first week.
* Mild tech-rotation Novembers saw the S&P recover. Extreme rotation starts like today's leaned weaker (exploratory, dot-com-heavy).
