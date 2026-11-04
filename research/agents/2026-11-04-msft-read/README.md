# MSFT live read, Wed Nov 4 (a map and state check, not a test)

**Agent / session:** Claude, claude.ai session for the owner, Wed Nov 4, about 10:15 ET.
**Owner's ask:** MSFT levels, plus where MSFT stands against the July-burst comparison and the next-burst conditions already on file.

**Inputs:**
* OI dated Nov 4 (Tuesday's closing positions) and Tuesday's closing chains (ThetaData). Engine `flipmap` imported unchanged.
* SqueezeMetrics DIX/GEX to Nov 3.
* Yahoo daily bars, live MSFT price (Twelve Data checked).

**Run:** `python msft_read.py <td dir> <DIX.csv> <live price>` → `out/msft_read.json`; `python figure.py <td dir>` → `out/msft_levels.png`.

**Today:** MSFT 554.5, **+6.4%** (open 543.70, high 557.25, low 542.64). It's a record: the old closing high was 543.45 on Oct 13. AAPL is +5% too, while semis are −1%. The platforms-up, chips/AI-infrastructure-down split from the premarket is still in place.

## Levels (Tuesday's positions)

| Kind | Level | Detail |
|---|---|---|
| Ceiling / magnet | **575** | Call wall: **148k calls ≤ 45 days**, the biggest dealer-gamma strike (+$0.41bn) and peak total gamma (~571, $2.36bn per 1%) |
| Above | 580 | 41k calls |
| Above | 600 | |
| Above | 625 | 104k calls |
| Near | 557.25 | Today's high |
| Near | 560 | |
| Support | **550** | Strike (+$0.22bn) and round number |
| Support | **543.5** | Old record close and today's open |
| Support | 540 | |
| Support | 525 | 66.5k calls |
| Support | 521 | Tuesday's close, the gap fill |
| Support | **500** | Put wall, 33k puts |
| Flip | **478.5** | 14% below the price |

* **Dealer gamma at the price is +$2.29bn per 1%,** close to its peak. MSFT is deep in long gamma, so dealers damp moves. Call gamma damping MSFT's next-day range is a tested result (dealer-sign B).
* **Gamma by expiry:** Dec 18 31%, Nov 20 24%, Jan 15 20%, Nov 6 12.5%.

## Burst conditions on file

**1. The release setup** (REPORT §4aa): MSFT's 20-day lead over SPY in the top third of its trailing year, while S&P dealer gamma (GEX) is in its bottom third. In that state MSFT had an up-leg within 10 sessions 50% of the time (24% otherwise), with a +2.7% average return.
* **S&P GEX:** $3.06bn on Nov 3, the **17th percentile**. ✓
* **MSFT's 20-day lead at Tuesday's close:** +1.6%, the 65th percentile. That is just under the 67th-percentile line, so it was **off by a hair**.
* **At today's price:** +6.0%, the **85th percentile.** ✓ (10-day lead: 88th; 40-day: 85th.)
* **So it turns ON at today's close** if MSFT holds most of today's gain and S&P GEX stays in its bottom third. Today's GEX prints tonight.
* **Caveat (technical-indicators, p 0.053, a lead):** when MSFT was this stretched, the setup worked about half as often (28–30% vs 62–64%). MSFT is now **+26.2% above its 200-day average (100th percentile of its year), RSI 64**, about as stretched as on Oct 15.

**2. The July pattern** (REPORT §4c): about a 30% drawdown (under-owned and hedged), falling vol, and a forced-flow date.
* **Not on.** MSFT is at a record and +57% from its June 25 low (352.83), so it is not under-owned.
* Vol is falling (VIX 20.8 → 18.3).
* The next forced-flow dates are Nov 20 (monthly expiry) and Dec 18 (quarterly).

**Other on-file leans:**
* **Forced-flow rule:** moves made with high own dealer gamma extend (+8% over 10 sessions); low-gamma moves fade. Today's move is the high-gamma kind.
* **Record call OI** before weaker months: −1.6 points (p 0.25), a lean.
