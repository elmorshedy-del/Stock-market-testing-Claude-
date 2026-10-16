# Who is on the other side of TSLA options? A second free day of Cboe Open-Close data

**Agent / session:** Claude, claude.ai session for the owner, 2026-10-16
**Type:** data check (descriptive, 1 day), the first step of the data audit the owner asked for. Builds on microstructure §4r item 3 (the Mar 28 2025 sample).
**Verdict:**
* **For TSLA puts, the engine's classic convention looks right.** Customers mostly hold long puts, so dealers are short them.
* **For TSLA calls it is in doubt.**
  * Customers' call activity is about 6 to 1 on the long side: they buy to open and sell to close. So customers mostly hold *long* calls, and the other side (market makers, plus funds that write calls) is mostly *short*.
  * The classic convention assumes dealers are long calls.
  * Two days are not enough to settle it. They point the same way as the Mar 2025 day, where customers net bought 19.4k calls.

## Data
* **The file:** Cboe's free Open-Close sample, `Cboe_OpenClose_2026-09-30_15_20_1.csv.gz` from datashop.cboe.com, kept in `data/` (gitignored).
  * It is licensed for internal use only, so only derived totals appear here.
  * Per the 10-minute spec, volumes are cumulative from the open, so this file covers Sep 30 2026 from 09:30 to 15:20, about 90% of the session.
  * It has 2,642 underlyings, with every trade classified by participant (customer, pro customer, firm, broker-dealer, market maker), buy or sell, and opening or closing (market makers have no open/close split).
* **Gamma weights:** our own ThetaData end-of-day chain for the same day. 69–82% of contracts matched.
* **Scripts:** `who_holds.py` (net flow and gamma by participant) and `opening.py` (opening vs closing by participant).

## Results (Sep 30 2026)

**Net flow on the day:**

| | TSLA calls | TSLA puts | SPY calls | SPY puts |
|---|---|---|---|---|
| Customer + pro, net contracts | −3,372 | +2,317 | −31,756 | −15,801 |
| Firm, net | −3,748 | +3,798 | −47 | +106 |
| Market maker, net | **+7,921** (+$3.7M gamma per 1%) | **−6,915** (−$3.5M) | +31,798 (+$131M) | +15,814 (+$7M) |

* **On net flow alone, TSLA matched the classic convention that day:** market makers bought calls and sold puts.
* **The opening/closing split shows what positions customers hold:**

| TSLA, customer + pro | Open buy | Close sell | Open sell | Close buy |
|---|---|---|---|---|
| Calls | 78,769 | 79,649 | 14,117 | 11,625 |
| Puts | 57,086 | 50,187 | 10,063 | 5,481 |

* **Customer activity sits on the long side for both calls and puts:**
  * Opening buys and closing sells are 158k contracts in calls, against 26k on the short side.
  * The day's net call selling was customers closing longs they already held.
* **Firms (funds) opened 4,021 short calls and 4,035 long puts:** call writing and hedging.
* **SPY shows the same customer pattern** (309k long-side vs 62k short-side in calls).

## What this means for the repository
1. **Correction:** `engines/gamma/verify.py` B3 ("dealer sign, empirically") checks our SPY gamma against SqueezeMetrics, and SqueezeMetrics uses the same classic convention.
   * B3 shows the engine reproduces their model. It does not show where dealers are actually positioned.
   * The real evidence for the S&P is behavioural: SqueezeMetrics' GEX predicts next-10-day realized vol and up-legs in every era (§4d, §4g, §4j). That holds whatever convention produced it.
2. **What depends on the convention:**
   * Results built on **near-price OI** ("freed") do not depend on it.
   * Results built on the **sign** do: "below the flip" and the own-gamma percentile.
   * Those edges were scored against prices, so they remain real as statements about the option map. But the reading "dealers are short gamma below the flip" may be wrong for TSLA calls.
3. **What would settle it:**
   * **Free:** a behaviour test of each convention. Does high gamma come before calmer next days and pinning into expiry, per stock, controlling for recent vol, under the classic convention versus all-short?
   * **Paid:** Cboe Open-Close history (Cboe's filings put an ad-hoc month at about $1,000; the current price needs a quote). Enough months to rebuild who holds TSLA's open interest. Most TSLA OI expires within about 3 months, so 3–6 months of history would cover most of today's positions.
   * Cboe's exchanges carry only part of TSLA option volume, so the data is a large sample, not the whole market.

## Reproduce
```bash
python3 who_holds.py data/Cboe_OpenClose_2026-09-30_15_20_1.csv.gz 2026-09-30 TSLA SPY MSFT QQQ   # needs the ThetaData chains
python3 opening.py data/Cboe_OpenClose_2026-09-30_15_20_1.csv.gz TSLA SPY
```
