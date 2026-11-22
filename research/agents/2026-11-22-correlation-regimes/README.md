# Correlation regimes on big scales, and the slow state before big falls (interrupted; superseded by the discovery system)

**Date:** 2026-11-22. **Owner's prompt:** "maybe the state of how things get triggered are on bigger scales. I think how things correlate here needs more careful statistical analysis." The owner then redirected to a general system (`../DISCOVERY.md`, `../2026-11-22-discovery/`). What was computed before the redirect is kept here. Not pre-registered; descriptive.

## Re-check of the cross-asset study's correlation claim (`recheck.py`)
* The gold–S&P daily correlation went from +0.11 to +0.46 (difference p = 0.034). After adjusting for the doubling of S&P variance (Forbes & Rigobon 2002), +0.34, p = 0.19. Bitcoin: p 0.006 → 0.14. **Mostly what higher volatility does by itself.**
* A 34-day gold–S&P correlation of +0.46 is at the 93rd percentile of all windows since 2000. The highest was June 2026 (+0.84), **before** the selloff.

## Three-year correlations of weekly S&P returns (`regimes.py`)
* **Treasuries:** positive 1970–1999; negative 2002–2022; positive Nov 2023 – Jun 2025; now −0.05 [−0.21, +0.11].
* **Dollar:** negative since March 2020 (now −0.14).
* **Credit:** +0.45 (85th percentile); positive since 2015.
* **Nikkei:** +0.60. **Gold** (futures): +0.21, positive since 2020. **Bitcoin:** +0.27.

## State before the 13 falls of 15%+ since 1963, against 216 near-high months not followed by a fall (`state.py`)
* Only a flat yield curve survived correction: 1 of 13 events had a curve above the control median (p 0.003, Holm 0.042).
* Sep 2026 against the control months:
  * CAPE: highest (100th percentile);
  * excess earnings yield: 6th percentile;
  * 12-month rise in the 10-year: 93rd;
  * NFCI leverage: 91st (but NFCI is not point-in-time; see the discovery README);
  * yield curve: 31st, not flat.
* With 13 events, power is low.
