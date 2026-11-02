# Live read, Mon Nov 2 (08:25 ET): SPY and TSLA for today, election Tuesday and the week, with projections

* **Owner, 2026-11-02 (pre-market):**
  * "where is spy standing as of now and what are your predictions for today and tomorrow and rest of week and different projections and for tsla too"
  * Follow-up: "does tsla have these 'pockets' to the upside same way spy did, and does this pocket for spy that sent it down last week work in reverse too?"
* **This is a live read plus forecasts, not a new test.**
  * The forecasts below are written and pushed **before the 09:30 open**, to be scored on Nov 2, 3, 4 and 6.
  * Each probability is my judgment. It starts from the options-implied map and adds the tilts from tested rules, which are named with their strength.
* **Data:**
  * ThetaData OI dated **Nov 2 (= Friday Oct 30 close positions, fresh)**, plus the Oct 30 closing chains for IVs.
  * Yahoo 5-minute bars incl. pre-market (ES, NQ, RTY futures, SPY, TSLA at 08:20 ET; VIX in global trading hours).
  * Breadth, ladder and SqueezeMetrics readings as of Friday Oct 30 (from [week-review](../2026-10-31-week-review/)). There has been no session since.
* **Reproduce:**
  * `python maps_now.py <td>`: engine code unchanged from week-review/maps_mon.py; OI file swapped to Nov 2.
  * `python curves_ext.py <td> <TSLA oi Oct 20–30>`
  * `python project.py`

## Now (08:20 ET)
* **Futures:** ES 7,640 (+0.36% vs Friday 16:00), NQ +0.63%, RTY +0.53%.
* **Pre-market:** SPY **758.60** (Friday 755.72), TSLA **402.22** (Friday 399.81).
* **Other:** VIX 19.47 (global trading hours; Friday 19.4). 10-year 4.93%.
* **Calendar:**

| Day | Events | SPY priced move | TSLA priced move |
|---|---|---|---|
| Mon Nov 2 | ISM manufacturing 10:00; **AAPL reports after the close**; SPY 0DTE holds 15.8% of SPY gamma, TSLA's Nov 2 expiry 18.4% | | |
| Tue Nov 3 | Vote day + AAPL reaction | 0.98% | 3.26%/day over Tue–Wed |
| **Wed Nov 4** | **Results** | 1.08% | (same pair) |
| Thu Nov 5 | | 0.94% | 2.48%/day over Thu–Fri |
| Fri Nov 6 | Payrolls | 1.06% | (same pair) |

## SPY checklist
* **Breadth (Friday):**
  * 63% of the panel above the 50-day (normal near a high).
  * The equal-weight panel beat the S&P by +4.0 pts over 20 sessions; the RSP − QQQ 20-session spread is a record +12 pts.
  * 68% of names rose over 5 sessions. Pairwise correlation 0.09: dispersion, not contagion.
  * Read: rotation, not liquidation. (D2 said a record divergence alone predicts nothing.)
* **Gamma (fresh Nov 2 OI):**
  * Flip **766.4**, down from 774.1 on stale OI, because Friday's put buying moved the map. SPY at 758.6 is **1.0% below the flip**.
  * Total gamma: −$7.6bn per 1% at 758.6 and −$10.5bn at 755.7.
  * Call wall 800, put wall **750**. Top negative strikes 750, 740, 730, 735; positive strikes 800, 780, 756, 790.
  * **The pocket:** total gamma −$20 to −21bn per 1% across **730–745** (floor about 743.6), −16 at 750, −8 at 758, −0.4 at 766, +5.9 at 775, +8.5 at 780, peak +12.5 at 800.
* **Ladder:** R4 fired Friday (up-leg within 20 sessions 70% / 74% vs 50% / 58% on any day; *odds edge, no payoff edge in spreads*).
* **SqueezeMetrics:** GEX $1.06bn (6th pct), DIX 43.8%.

### Owner's Q2: does the pocket work in reverse? **Yes, and historically more so.**
* **Mechanics:** below the flip, dealers are short gamma. They sell into drops and buy into rallies, so both directions are amplified.
  * The amplification is **lopsided right now**. Falling from 758 into 745 crosses −8 → −21 ($bn per 1%), the strongest. Rising from 758 to 766 crosses −8 → 0, so it fades as SPY climbs.
* **History (microstructure REPORT §4z, SPY, volatility controlled, next 3 sessions):** below its flip, SPY's **up-bursts are 2.8× more likely (p < 0.001)**; down-bursts are not raised (0.7×, p 0.13).
  * The extra big moves from below the flip are **snap-backs, not breakdowns**. QQQ: up 3.8× (p < 0.001), down 1.3× (p 0.12).
  * **Tag: proven** (passed after the §4z timing fix; 2021–26).
* **Past the flip, damping starts:** gamma turns positive at 766 and thickens to 780 (+8.5). A snap-back should **slow at 766–780**, not run through it. This matches the call-wall soft ceiling (proven for SPY/QQQ), with the wall far away at 800.

### SPY forecasts (scored on the stated dates)
Map = options-implied paths from 758.60, Gaussian, no drift. My call adds the tilts:
* below-flip snap-back (proven);
* month-end give-back of about +0.6% over 5 sessions (p 0.026 pooled; **not** significant in 2020–26);
* midterm election week up in 74% of cases (n 19, descriptive);
* the half-month effect;
* the election premium is small (election-vol null), so **no scheduled VIX crush**.

| # | Forecast | Map | **My call** |
|---|---|---|---|
| S1 | Mon close > 755.72 | 65% | **65%** |
| S2 | Mon close inside 751–766 | 68% | **70%** |
| S3 | Trades ≥ 766.4 (the flip) by Fri Nov 6 | 62% | **65%** |
| S4 | Fri Nov 6 close ≥ 766.4 | 32% | **35%** |
| S5 | Trades ≤ 750 (the put wall) by Fri | 60% | **50%** |
| S6 | Fri Nov 6 close > 755.72 | 56% | **60%** |
| S7 | Any Fri close ≤ 740.6 (channel kill line) this week | 15% | **12%** |
| S8 | VIX closes ≤ 16.5 on any day through Nov 6 | – | **25%** |

**Scenarios to Friday (my weights):**
* **A. Snap-back, 40%:** SPY reclaims 766 by Wed/Thu (post-vote relief, AAPL fine), then stalls at 770–780 as gamma turns positive. Friday 765–778.
* **B. Chop, 38%:** 748–766, with wide days both ways inside the short-gamma zone. Friday 750–765.
* **C. Flush, 22%:** loses 750 and drops into the 730–745 pocket, where dealer selling is strongest. Tests ~740.
  * A close ≤ 740.6 kills the channel dip rule.
  * The trigger would be the AI selling spreading: GEX < 0 with correlation rising (P2).

## TSLA (8-step read, TSLA_PLAYBOOK)
1. **State:**
   * 402.2 pre-market, **6.1% above its own flip (376.8; the engine's flip 381.2)**, so dealers are long gamma: +$0.47bn per 1% at 402, 65th pct.
   * Freed: near-price OI at the **23rd pct** (was 4th); still in the bottom third, so **freed is on**.
   * Full setup (freed + below flip): **off**.
   * Gamma slope: rising steeply above. **[map]**
2. **Levels:**
   * Call wall **400**: the biggest positive strike, and Friday's biggest call add (+15.6k). It is today's pin candidate (18% of TSLA gamma expires today).
   * Put wall **380**, up from 350 (+5.5k puts).
   * Negative strikes 397.5, 380, 390. Short-gamma zone 372–381.
   * Calls added Friday: 400, 410, 435, 415, 422.5. Net Friday adds: +96k calls vs +57k puts. **[map]**
3. **Calendar:** Monday (see below); vote and results over Tue–Wed, priced at 3.26% per day vs 2.57% normal. **[map]**
4. **Market:** SPY is below its flip. **SPY drags TSLA about 2× on S&P down days of −1% or worse [proven #6].**
5. **Flow:** Friday's tape not pulled (Databento budget). Last read: the Oct 26–27 burst, buying aggression 90th pct. **[lean]**
6. **Setups:**
   * **Monday up-only burst effect** (REPORT §4o, the most robust calendar finding; Friday up-bursts suppressed). **[proven-ish]**
   * Freed means up-bursts 1.8× **[proven #1]**.
   * No RSI washout and no 20-day low.
7. **Top watch:**
   * IV rose with price (37 → 41%), but skew is put-bid (25-delta risk reversal −4.8), the opposite of the flat skew seen at tops.
   * 1 of 5 top elements: **no top profile**. **[lean]**
8. **Tags:** as marked. Eras: 2021–26. Open interest lags one session; Databento and Yahoo closes differ on some days.

### Owner's Q1: does TSLA have SPY-style pockets to the upside? **No negative pocket above; it has a "plateau".**
* **Total gamma (positive = damping):**

| Price | 380 | 390 | 400 | 410 | 420 | 430 | 440 | 450 |
|---|---|---|---|---|---|---|---|---|
| $bn per 1% | ~0 | 0.15 | 0.39 | 0.72 | 0.84 | 0.86 | 0.87 | 0.97 |

  The peak is about 455.
* **400 → 420:** damping thickens fast. Rallies should **grind** here (stair-step, not snap). This matches the wall-flow read ("stall near 420").
* **420 → 440:** a **plateau**. Damping stops increasing, so once through 420 the move to ~440 is lighter. This is the closest thing TSLA has to an upside "pocket", though it is still damped, not amplified.
* **The amplifying pocket is below:** under ~381 gamma turns negative (−0.1 at 370, −0.2 at 340).
  * TSLA's own history says that below its flip the extra moves are also **up** (snap-backs 1.45×, p 0.04) [proven #2 context].

### TSLA forecasts
| # | Forecast | Map | **My call** |
|---|---|---|---|
| T1 | Mon close > 399.81 | 59% | **62%** (Monday effect, freed) |
| T2 | Mon close within 395–410 (the 400 pin) | – | **60%** |
| T3 | Trades ≥ 420 by Fri Nov 6 | 46% | **45%** (damping 400–420 offsets the freed up-lean) |
| T4 | Fri Nov 6 close ≥ 420 | 24% | **20%** |
| T5 | Trades ≤ 380 by Fri | 37% | **30%** |
| T6 | Fri Nov 6 close > 399.81 | 52% | **57%** |

**Scenarios to Friday:**
* **A. Grind up, 40%:** holds 400, stair-steps to 410 and then 420. Friday 410–425; through 420, a light run to ~435–440 is possible.
* **B. Pin, 35%:** 392–412 around the 400 strike. Friday 395–410.
* **C. Drag, 25%:** an SPY flush with the 2× drag. TSLA 380–390, where the put wall and flip zone (377–381) should hold first; below that, the small negative pocket to ~372.
* **Election (from tsla-politics, lean):** a Talarico win (75%) is mostly priced. A Paxton upset maps to a large TSLA up-day (CI wide). TSLA's ~1-vol-point election premium should bleed out after Nov 4.

## Scoring
* Score S1, S2, T1 and T2 after Monday's close; S3–S8 and T3–T6 on Fri Nov 6 (TODO LR1).
* Report Brier scores for my calls vs the map, so the tilts are tested over time.
