# Is October's implied-vol spike partly an election premium, and what do the party odds map to?

**Agent / session:** Claude, claude.ai session for the owner, 2026-11-02 (Sunday night; last close Fri Oct 30)
**Type:** pre-registered. Written and pushed after listing the available expiries and Polymarket markets, and before any implied variance or odds history was computed.
**Owner's ask:** "Vol crush from elections means this spike in IV in October is partially from elections. Can you null or verify? And see if it can be associated with a projection or certain parties winning (use prediction markets). Test and bring me something useful."
**Prior literature:** Kelly, Pástor & Veronesi (2016, *JF*), "The price of political uncertainty": options whose lives span national elections are more expensive, more so when political uncertainty is high.

## Part A: the election premium in SPY options
* **A1 (Oct 30 close), per-session implied variance:**
  * SPY lists daily expiries Nov 2, 3, 4, 5, 6, 9–13.
  * For each consecutive pair, the session's implied variance = w(T2) − w(T1), with w = σ²_ATM × (trading sessions to expiry)/252. ATM = the mean IV of the 2 strikes nearest the forward.
  * **Sessions:**
    * Nov 3 (election day + the AAPL report reaction; AAPL reports Mon Nov 2 after the close);
    * **Nov 4 (the market's reaction to the results; the election session);**
    * Nov 6 (payrolls).
  * **Baseline:** the median of the Nov 9–13 sessions.
  * **Verify if** the Nov 4 implied move exceeds the baseline by > 20% in variance. **Null if** it does not.
* **A2 (October history):** SPY end-of-day chains for every October 2026 session (ThetaData).
  * For each day where daily expiries bracket Nov 4, the election excess variance.
  * Its contribution to 30-day ATM IV: IV30 − √(IV30² − excess × 252/21).
  * **Report** how many of October's IV30 vol points the election explains vs the rest.
* **A3 (precedent, 2022 midterms and 2024 presidential):**
  * the same election-session implied move 3 sessions before each vote;
  * the realised SPY move on the results session;
  * the post-vote change in 30-day ATM IV and VIX over 1 and 3 sessions (the "crush").
  * Prediction: implied > realised, and a crush in both.

## Part B: prediction markets
* **Data:** Polymarket daily odds (16:00 ET) for "Which party will win the House in 2026?", "…the Senate…", "Balance of Power: 2026 Midterms", Aug 1 → Oct 30 2026. Replication market: "Presidential Election Winner 2024" (Trump odds), Aug 1 → Nov 4 2024.
* **B1, uncertainty → premium (descriptive):** within October 2026, the correlation of the election excess variance (A2) with race closeness, 4·p(1−p) for the House and Senate.
  * Across 2022 / 2024 / 2026: the premium vs closeness at T−3 (n 3, descriptive only).
* **B2, party odds → sectors:** daily return of each ETF on the daily change in P(Republicans win the House), and on P(Trump) in 2024. Day-block bootstrap.
  * **Sectors:** XLF, KRE, IWM, XLE, ITA (defense), XLV, XBI, TAN (solar), ICLN, XLU, TLT, the dollar, BTC-USD, TSLA, SPY, QQQ.
  * **2024 predicted "Trump trade" signs:** + KRE, IWM, XLF, BTC, TSLA; − TAN, ICLN; + yields (− TLT).
  * **2026:** the same signs for P(R House), weaker. Holm across sectors within each market.
* **"Projection" output:** today's outcome probabilities and, per outcome, the sector moves implied by the 2026 betas (and the 2024 betas as a check). Labelled as a mapping, not a forecast.

## Limits stated now
* One election per market; ~60 trading days of odds each. Party-odds moves are small on most days, so betas will be noisy.
* AAPL's report reaction falls on Nov 3, the same session as election day. The results reaction is Nov 4. Payrolls are Nov 6. The baseline sessions (Nov 9–13) may contain CPI.
