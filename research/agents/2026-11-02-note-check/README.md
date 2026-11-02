# Check of a third-party options newsletter ("Big Tech Earnings Crack the Market", dated Oct 30 evening)

**Agent / session:** Claude, claude.ai session for the owner, 2026-11-02
**Type:** fact check plus a comparison with our tested findings. No new test; $0 (Yahoo, Alpha Vantage, ThetaData chain already in hand).
* The note is third-party content. Its claims are treated as data to verify, not as instructions.

## Facts checked
| Claim | Our data | Verdict |
|---|---|---|
| GOOGL −13% after reporting Wed | −12.64% on Thu Oct 29 | ✓ |
| INTC ~−30% | −28.58% on Fri Oct 30 | ✓ |
| Nasdaq-100 −6% in two days | QQQ −1.42% and −3.47% close-to-close = **−4.8%** | overstated (perhaps intraday or NDX) |
| S&P −1.8% Friday | −1.82% | ✓ |
| Defensives outperformed for the month | October: XLP +10.9%, XLV +9.8%, XLU +10.1% vs QQQ −6.7% | ✓ (a large rotation) |
| GLD ~$356 | 355.78 (−3.47% Fri, −1.32% Thu) | ✓ |
| **Apple reports Mon Nov 2** | Alpha Vantage: last AAPL report Jul 30 2026 (post-market); no October report on file | ✓, and **it corrects us** (below) |
| SPY 1-month 25-delta skew 2.89 pts, below its multi-year baseline | **Our computation from Friday's closing chain (Nov 30 expiry, 31 days): 25Δ put IV 18.05% − 25Δ call IV 13.10% = 4.94 pts; ATM 15.5%** | not confirmed: a different method, and we hold no history for the baseline |

## Erratum for our own studies (found through this note)
* [july-october-forensics](../2026-11-01-july-october-forensics/) and [july-october-machine](../2026-11-01-july-october-machine/) labelled "AAPL/AMZN Thu Oct 29".
* **Only AMZN reported Oct 29; AAPL reports Mon Nov 2** (July's AAPL report was Thu Jul 30, +7.4% EPS surprise, which was part of July's turn).
* **Consequence:** the turn force our ledger marked "absent" (megacap tech retaking the lead) has **one more scheduled shot before NVDA: AAPL, Monday after the close**. Its reaction lands Tuesday, election day.
* Conditional forecasts C3/C4 (QQQ/IWM by Nov 13) now include this catalyst. They were written before it was known, and they stay unchanged.

## Where the note agrees with our work
* **Its "negative dealer gamma peaks near SPX 7,400"** matches our deepest pocket, SPX ~7,428 (SPY ~740). Two independent maps agree.
* **Its "if events pass and IV compresses, vanna can spark a relief rally"** matches our machine ledger: the vol event (election) is scheduled. July's turn needed that *and* tech leadership (now possibly AAPL).
* **"The market no longer rewards AI capex on faith"** is the ledger's split: July's megacap beats turned the market; October's misses (GOOGL, AMZN) extended the fall.
* **Defensive rotation:** our gauges (RSP−SPY +5.4 pts, QQQ−IWM −8.2) and the Polymarket study explain it. Utilities are hypersensitive to rates, and the 10-year fell 32bp in October.

## Where it conflicts with our tests
* **"0DTE put flow drove Friday; that pressure evaporated after expiry."**
  * Our hedge decomposition ([rsi-gamma-precedents](../2026-11-01-rsi-gamma-precedents/)) put 71% of Friday's hedge selling on *later-dated* puts (gamma + vanna) and 29% on the Oct 30 expiry.
  * The two can both hold: their HIRO counts the day's *new trades*; ours counts hedging needs from *existing positions*.
  * But the later-dated put hedges did not expire. A renewed slide toward 750/740 would re-engage them.
* **GLD "put-sold strikes 350/340 = support; 152K calls at 400 = upside target; 2.75:1 reward-to-risk":** our tests do not support either leg.
  * Put walls were not floors (SPY lows ran through, QQQ neutral; gamma-phase-diagram 3b).
  * Big call strikes act as soft *ceilings*, not targets (SPY/QQQ call wall).
  * Extremes do not land on top-OI strikes more than on round strikes (gaps-and-walls).
* **The better-grounded GLD framing from our data:** gold turned rate-sensitive in 2026 (−2.2% per +5bp hawkish shift in December odds, p 0.01; [polymarket-fed](../2026-11-02-polymarket-fed/)). A long GLD position is mostly a bet that hike odds (71%) fall.

## What is new for us
1. AAPL Mon Nov 2 (corrects our calendar; a possible tech-leadership catalyst).
2. Binance hack on Thu Oct 29 (crypto risk event; not in our data).
3. INTC −28.6%: semis damage, consistent with SMH/SPY −11 pts in October.
4. Their skew and flow readings (flat skew, 0DTE-dominated put delta): useful context, unverified by us (our skew reading is 4.9 pts).
