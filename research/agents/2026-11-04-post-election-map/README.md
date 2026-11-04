# Post-election map for Wed Nov 4 (a map, not a test)

**Agent / session:** Claude, claude.ai session for the owner, Tue Nov 3, about 22:30 ET (election night).
**Owner's ask:** the exact SPY pocket and critical levels (which level triggers the scare, and where the flush snaps back); the exact TSLA flip for tomorrow; the odds of reaching it if vol rises; whether the burst setup is reachable; TSLA mapped from SPY's levels.

**Inputs:**
* **Positions:** OI dated Nov 3, i.e. Monday's closing positions. Tuesday's positions publish about 6-7am ET; refresh before the open.
* **Implied vols:** Tuesday's closing chains.
* **Engine:** imported unchanged (flip-wicks `flipmap`, microstructure `hd_gamma` / `td_gamma`), classic dealer convention.
* **Run:** `python map.py <td dir>` → `out/map.json`; `python figure.py` → `out/post_election_map.png`.

**SPY**
* Flip **768.8** including Wednesday's 0DTE (770.0 excluding it). It moved up from 766.4.
* Put wall **740**, down from 750. Call wall 800.
* Total gamma, $bn per 1% move:

  | SPY | 765 | 760 | 755 | 750 | 745 | 740 | 735 | 730 | 725 | 720 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | Gamma | −3.3 | −7.5 | −11.2 | −14.1 | −16.9 | −19.2 | **−20.0** | −19.5 | −18.1 | −16.6 |

  The **trough is at 734.5**. The core pocket (at or below 85% of the trough's depth) is **725-745**.
* Largest negative-gamma strikes near spot: 750 (−1.65), 740 (−1.54), 745 (−1.19), 730 (−1.02), 735 (−0.78).
* Futures-implied open: 745.9 (ES 7,512 vs 7,597 at 16:00).
* Price levels: the Aug/Sep/Oct lows sit at 748.8 / 749.6 / 750.4; the 200-day average is 729.5; July's low was 729.1.

**TSLA**
* Flip **376.8** (engine `day_metrics`); 382.5 including Wednesday's 0DTE (`fine_flip`), 376.2 excluding it.
* Long gamma above about 382, short gamma below. Call wall 400.
* **Freed at hypothetical Wednesday closes:**
  * yes at 395 / 388 / 385 / 382;
  * **380 (4th pct)**, 378 (10th), 375 (6th), 372 (9th);
  * no at 398.5 or 391.6.
* **So the full setup (freed + close below the flip) needs a close ≤ about 376.** "Freed + within 1% of the flip" starts at about 380.
* **Implied odds by Wednesday's close,** from the after-hours 391.64 (IV 62.4%, Nov 6 at-the-money), first at that IV, then with IV +10 points:

  | Close at or below | 385 | 380 | 375 |
  |---|---|---|---|
  | At IV | 33% | 22% | 13.5% |
  | IV +10 points | 35% | 25% | 17% |

* **Mapped from SPY with the proven 2× rule** (S&P down days):

  | SPY | 750 | 745.9 | 740 | 734.5 | 730 | 725 |
  |---|---|---|---|---|---|---|
  | TSLA | ≈394 | 390 | 383 | **377 (its flip)** | **373 (full-setup zone)** | 367 |
