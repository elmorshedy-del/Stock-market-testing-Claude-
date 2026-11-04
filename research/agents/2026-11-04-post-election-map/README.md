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

## Refresh v2: Wed Nov 4, 08:00 ET (Tuesday's closing positions)
*Owner: "Everything changed over night."* `map_v2.py` is `map.py` with OI dated Nov 4 (Tuesday's closing positions) and premarket references (SPY 760.1, TSLA 376.0). `map.py` is unchanged. `figure_v2.py` → `out/what_changed.png`.

**What happened overnight** (Yahoo 5-min bars; Twelve Data checked AMD)
* **The SPY scare came and went in futures.**
  * ES fell to about 7,490 at 22:05 ET. That is SPY ≈ 744.2, the top of the core pocket.
  * It then rallied +2.6% to SPY ≈ 763.2 by 06:45.
  * Cash trading never tested 740 or 735.
  * Reasons in the coverage (Reuters, Investing.com):
    * divided government;
    * the new Congress does not sit until January;
    * the dollar and long yields fell;
    * VIX −12% to 18.3.
* **TSLA decoupled from SPY.** At 08:00 it was −5.6% against Tuesday's 398.50 close, while SPY was +0.8%. The cause was Musk-specific political risk: Texas lost, Congress gone, scrutiny of a SpaceX merger. That made the 2× S&P drag rule irrelevant. TP1 had estimated about −5% for a Talarico win; TSLA is tracking that estimate (scored at the close).
* **AI started selling good news at 07:00.**
  * AMD went from +7.4% (its earnings beat) to −1.2% / −2.4%, Twelve Data extended price 478.
  * NVDA went from +1.9% to −1.6%, and SMH from 527 to 511.
  * Solar and the Dow are strong. That is rotation, not liquidation: RSP was +0.8%.

**SPY (Tuesday positions)**
* Flip **765.9** including 0DTE (768.5 excluding it), down from 768.8.
* Put wall 740, call wall 800.
* Trough at **735** (−21.2 $bn per 1%); the core pocket is about 723–745.
* Steepest drop above the trough: 757.5.
* Short gamma below 765.5. The biggest negative strikes are 750 (−1.39) and 740 (−1.23).
* Wednesday 0DTE OI: 770 calls 13.4k, 760 calls 10.1k, 755 calls/puts 9.6k / 9.7k.

**TSLA (Tuesday positions)**
* Engine flip **377.5** (was 376.8); `fine_flip` 376.9 excluding 0DTE, 386.1 including it.
* Short gamma below 386.
* Biggest negative strikes: 380 (−0.067), then 370. Wednesday 0DTE puts: 380 5.2k, 385 3.0k, 375 2.5k.
* **Freed at every hypothetical close ≤ 390** (near-OI pct 4–28%); 6th pct at 376.
* **So the full setup (freed and a close below 377.5) is live today.** From 376 at the Nov 6 ATM IV of 67%, P(close ≤ 377.5) ≈ 52%.
* Its 20-day closing low is 354.7, so a close near 376 is not a new 20-day low (playbook rule 8 not triggered).
* Late-October gap: from 372.2 (Oct 23 close) to 391.6.

### v2 note: how much of TSLA's drop is the Musk/Texas story? (08:24 ET, `decomp.py` → `out/decomp.json`, `out/tsla_decomp.png`)
* **Model:** TSLA = 1.43 × QQQ + 0.01 × AI-infrastructure factor.
  * The factor is the mean QQQ-residual of CRWV, ORCL, VST, PLTR and IREN.
  * Fit on 250 daily returns to Nov 3; R² 0.42; residual sd 2.16%.
* **Over the past year TSLA has had no link to the AI-infrastructure trade** beyond QQQ (residual correlation 0.01). Its residuals also do not correlate with SpaceX's (−0.05 over 99 days). Today's joint drop is a one-off political shock, not a normal "Musk factor".
* **Today, log % since Tue close:**

  | Part | % |
  |---|---|
  | TSLA total | −4.73 |
  | QQQ part | +0.35 |
  | AI-infrastructure part | −0.06 (factor −7.1% today) |
  | **Leftover, Musk/Texas** | **−5.02 (−2.3 residual sd)** |

* **Timing agrees.** 20:00→04:00: NQ +2.0%, TSLA −2.1%. 04:00→07:00: NQ flat, TSLA −2%. 07:00→08:00, during the AI fade: TSLA flat to up.

## v3: TSLA at the Nov 4 close (`tsla_close_state.py`, `figure_tsla_checklist.py` → `out/tsla_close_state.json`, `out/tsla_flip_grid.json`, `out/tsla_checklist.png`)
*Owner: "what conditions it hit and which not and how far … could have today options and iv crush actually put it below its last computed flip."*

**Official state** (engine definition: OI dated Nov 4 + the Nov 4 closing chain):
* flip **377.6**, close 385.19 (**+2.0% above**);
* near-price OI at the 24th pct (**freed**), own gamma at the 30th pct;
* **not a full setup.**

**IV crush:** TSLA's 30-day ATM IV only fell from 45.2% to 43.3% (VIX fell 20%), moving the flip from 377.5 to 377.6. No effect.

**Today's trading** (decides tomorrow's state; the real positions publish about 6–7am Nov 5). Scenarios add a share of today's volume as new OI:
* **Mixed opening** (calls and puts in proportion): flip 378–380, and freed turns off from about 10% of the volume.
* **Put-only opening:** the flip passes the close at about 20% of put volume (385.9), but freed turns off at about 15%.
* **No scenario gives both conditions at once.**
* **Call-only opening:** the flip falls (373.6 at 10%).

**Other conditions:**

| Condition | Now | Needs | Status |
|---|---|---|---|
| RSI | 51 (61st pct) | ≤ 38.3 for washed-out | ✗ |
| ATR% | 4.1% (63rd pct) | not low | ✓ |
| 20-day closing low | — | 354.72 | not near |
| S&P gamma | 17th pct (Nov 3) | reset | ✓ |
| R4 / T5 | SPY −0.7% from its 10-day high | R4 needs ≥ 2% off | off, pending tonight's GEX |
| R7 | VIX −21.5% vs its 10-day max | ≥ 25% off (VIX ≤ 15.86) | ✗ |
| TSLA's own DPI | 76th pct | top third | ✓ lean |
