# Is today an "unwind low" like July 29? A pre-registered capitulation signature, tested on all history

**Agent / session:** Claude, for the owner, 2026-11-05 ~10:00 ET. **Pre-registered at commit:** the commit that first adds this README.
**Owner:** "Today can be 'July 29' … can we align enough metrics … that this is the low from where the bounce will happen … not over fitting or forcing a narrative. Just being objective and testing."

## Guard against forcing the narrative
* The criteria below are fixed **before** computing anything, **including July 29's own values**.
* Thresholds are round numbers chosen from mechanism, not tuned.
* July 29 is checked only after the rules are frozen, as one case among all.
* Results are reported with n, base rates and a null. If n is small, the answer is "can't say with confidence."

## Mechanism (from prior work)
* A crowded-book unwind ends when forced sellers are done ([live-read LQ](../2026-11-02-live-read/), [friday-narrative](../2026-11-01-friday-narrative/)).
* Its footprint is violent, concentrated selling in the crowded group while the average stock, fear (VIX) and credit stay calm. That marks positioning, not macro.
* Unwinds end with relief bounces (July: a +12.6-point basket-vs-RSP day).

## Signature at day t's close (SMH = chips/AI, RSP = equal-weight S&P; ratio = SMH/RSP)
| Code | Condition |
|---|---|
| **D** depth | ratio ≥ 25% below its 252-session high |
| **V** violence | ratio 1-day return in its bottom 2% (percentile vs the prior 1,000 sessions; no look-ahead) |
| **B** concentrated | RSP 1-day return ≥ −1.0% and SMH 1-day ≤ −3% |
| **F** fear calm | VIX 1-day change ≤ +10% and VIX ≤ 25 |
| **C** credit calm | HYG/IEF 1-day return ≥ −0.3% |

* **Core event = D & V & B. Full event = core & F & C.**
* Episodes: events within 5 sessions of each other count once (first day).

## Outcomes (t close → t+k close)
* ratio forward 5 and 10 sessions;
* SMH forward 5 and 10 sessions;
* **low marker:** the ratio at t is within 2% of its minimum over t−10…t+10.

## Comparisons and null
* Full event vs (i) all **deep-rotation days** (D alone) and (ii) all days.
* Null: circular shift of the event indicator (shift ≥ 60 sessions, 5,000 draws). One-sided p for "ratio forward 10 > deep-rotation baseline".
* **Pass: p < 0.05 on the ratio's 10-session forward move, with ≥ 8 episodes.** Fewer than 8 episodes → "insufficient evidence", whatever the means say.

## Then, descriptive only
* July 29, 2026 (and Jul 28–31): which conditions it met.
* Today, from live intraday values: **provisional until the close.**
* The catalyst difference: July 29 had MSFT/META earnings that night; today has none of that scale (jobs report Friday).

## Reproduce
`python unwind.py <DIX.csv>` → `out/unwind.json`

---

# Results (09:58 ET; today's row is live and provisional; rerun at the close)
* **Core signature (deep + violent + concentrated): 1 past episode since 2007,** on **2022-07-01**.
  * Ratio +8.9% and SMH +8.4% over the next 10 sessions; it marked the local low.
  * But the 2022 rotation's real trough came in Oct 2022, so it was a bounce, not the bottom.
  * One-episode p 0.02, but with n = 1 the registered rule says **insufficient evidence (needs ≥ 8 episodes).**
* **Full signature (+ fear calm + credit calm): 0 past episodes.**
* **Today (live): core met (D, V, B), full NOT met.**
  * VIX +13% fails the ≤ +10% condition, and HYG/IEF −0.33% just misses the ≥ −0.3% line.
  * Fear and credit are not fully calm, unlike a pure positioning flush.
* **July 29 itself did not match the signature:** D, B and C were met; V and F were not. Jul 28 met V/B/F/C but not D. The July low had a catalyst (MSFT/META earnings that night) and a different shape.
* **Verdict: insufficient evidence** to call today a July-29-type low with confidence. The core conditions are rare and their one precedent bounced, which leans bounce, not bottom. Rerun at the close.
