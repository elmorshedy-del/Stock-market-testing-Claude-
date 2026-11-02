# Does TSLA price a Republican win, and which races matter to Tesla's business?

**Agent / session:** Claude, claude.ai session for the owner, 2026-11-02 (last close Fri Oct 30)
**Type:** pre-registered.
* **Seen before writing:** the list of Polymarket race markets with their current odds (needed to pick markets), and a news search on Tesla's policy exposure.
* **Not yet computed:** no odds history and no TSLA relationship.

**Owner's ask:** "Any particular senator or state or outcome important to TSLA as a business? I think red is better for TSLA, but even though they are falling way behind, TSLA doesn't seem to be really caring."
**Builds on:** [election-vol](../2026-11-02-election-vol/). Its two results here:
* 2026 TSLA beta to P(R House) was +4.7% per +10 pts (p 0.29), and to P(R Senate) +0.4% (p 0.89).
* TSLA options price an election premium of 1.2 extra normal days over Nov 3–4.

## Questions
1. Does TSLA's own move (net of the market) track Republican odds, in total or in the races tied to Tesla's business?
2. If the answer is "no", is that because TSLA doesn't care, or because a daily test can't see it? Calibrate on 2024, when TSLA clearly priced Trump (+13.8% on Nov 6).
3. Where does TSLA's political sensitivity actually come from: Congress, or Musk's standing with the White House?

## Data
* **Polymarket hourly prices** (CLOB prices-history), read at 16:00 ET each trading day, Aug 10 → Oct 30 2026. The window starts after all the primaries listed here.
* **Markets (P = the Republican's "Yes" price):**
  * party control: P(R House) and P(R Senate), from "Which party will win the House/Senate in 2026?";
  * Texas Senate: Paxton (R) vs Talarico (D). Tesla's HQ state; Musk put ~$168M into pro-Paxton groups (SLF → Texas PAC, Lone Star Liberty);
  * Texas governor: Abbott (R) vs Hinojosa (D). State robotaxi rules and Giga Texas;
  * Nevada governor: Lombardo (R) vs Ford (D). Giga Nevada and a robotaxi permit;
  * Arizona governor: Biggs (R) vs Hobbs (D). Robotaxi permits;
  * Michigan Senate: Rogers (R) vs El-Sayed (D). An open seat; Sen. Peters, the AV-bill sponsor, is retiring;
  * California governor: Hilton (R) vs Becerra (D). California is the DMV/CPUC driverless-permit regulator and Tesla's largest US market.
* **2024 calibration:** P(Trump) from "Presidential Election Winner 2024", Aug 1 → Nov 4 2024.
* **Prices:** TSLA and QQQ daily closes (Yahoo).
* **Options:** TSLA end-of-day chains (ThetaData, already on disk, $0).

## Tests
* **Residual return.** Each day, TSLA's return minus β × QQQ's return. β is the OLS slope over the 250 sessions ending Aug 7 2026, or Jul 31 2024 for the 2024 window. The regressor is the daily change in P, in points.
* **P1 (primary): Texas Senate.** The slope of TSLA's residual return on the daily change in P(Paxton).
  * Owner's prediction: positive ("red is better").
  * Inference: 5-day block bootstrap (2,000 draws), two-sided p.
* **P2 (secondary):** the same regression for the other 7 markets. Holm correction across all 8 (P1 + P2).
* **P3, power and attribution:**
  * for each market, the slope detectable with 80% power, (1.96 + 0.84) × bootstrap SE;
  * the total change in P over the window × the slope (with its 95% CI), compared with TSLA's actual cumulative residual. This answers "how much of TSLA's move since August could be politics".
* **P4, 2024 calibration:**
  * the same regression on daily P(Trump) changes, Aug 1 → Nov 4 2024;
  * TSLA's residual on Nov 6 2024;
  * **the check:** does the daily-beta method detect TSLA's political pricing in a year when it was clearly there?
* **P5, options (the Friday close before each vote):**
  * TSLA's election-window excess variance, in normal-day units: Nov 1 2024 (the expiry pair spans Nov 4–8; FOMC on Nov 7 is a disclosed confound) vs Oct 30 2026 (1.21, from election-vol);
  * the 2024 realised results-day residual vs what was priced;
  * baseline = the median per-session variance of the next three weekly pairs.
* **P6, descriptive:** TSLA's residual, in units of its trailing 60-day residual standard deviation, on Musk–White House days:
  * 2024-11-06 (Trump wins);
  * 2025-06-05 (Trump–Musk feud goes public);
  * 2025-07-07 (first session after the "America Party" announcement).
  * 2026-10-21/22 (Musk's "live by the sword" reply to Democrats' probe plans) is excluded, because it is confounded by Tesla's Q3 report.

## Predictions written now
* **P1/P2:** null (|slope| below the detectable size). The reason: a daily test is underpowered against TSLA's ~2.5% residual noise.
* **P4:** the 2024 daily slope is also not significant, even though Nov 6 2024 was a large positive residual. If so, "TSLA doesn't seem to care" is not evidence either way.
* **P5:** the 2026 premium is smaller than 2024's.
* **P6:** Musk–White House days are multi-σ residuals (|z| ≥ 3), larger than any Congress-odds day.

## Limits stated now
* One election per year, and ~58 sessions per window. The race markets are thin compared with the chamber markets; thin markets add noise, which biases slopes toward 0.
* Business relevance is argued from sources (Tesla 10-Q, bill trackers, news). It is not tested.
