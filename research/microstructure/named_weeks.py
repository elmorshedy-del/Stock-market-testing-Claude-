"""The TSLA moves named in the conversation, dissected into days (REPORT 4ac).
The dates you gave were the Monday of the week each move happened, not the burst day. This lays every
week of each move out as a calendar row (Mon..Fri daily % change, and the week's total), from the week
before your week to the end of the move, so you can see which day actually carried it.
R = report reaction day (tsla_eras.REACTIONS_2020); other event days are labelled where they are certain.
Usage: python named_weeks.py      -> out/named_weeks_TSLA.png, out/named_weeks_TSLA.csv
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

from common import OUT, load_bars
from tsla_eras import REACTIONS_2020

INK, MUTED, SURF = "#0b0b0b", "#52514e", "#fcfcfb"
CMAP = LinearSegmentedColormap.from_list("updown", ["#c0392b", "#f3d6d2", "#fcfcfb", "#cfeedd", "#138a5e"])
# (name, the week you named, first and last week shown)
MOVES = [("Oct 2021", "2021-10-11", "2021-10-04", "2021-11-05"), ("Jan 2023 (off the bottom)", "2023-01-09", "2023-01-02", "2023-02-17"),
         ("May 2023", "2023-05-15", "2023-05-08", "2023-06-16"), ("Jun-Jul 2024", "2024-06-24", "2024-06-17", "2024-07-12"),
         ("Oct-Nov 2024 (red week between)", "2024-10-21", "2024-10-14", "2024-11-15"), ("Apr-May 2025", "2025-04-21", "2025-04-14", "2025-05-23"),
         ("Sep 2025 (smaller, then big)", "2025-09-01", "2025-08-25", "2025-09-26"), ("Oct 2025 (a window you asked about)", "2025-10-06", "2025-09-29", "2025-10-24")]
EVENTS = {"2021-10-25": "Hertz", "2024-07-02": "deliv.", "2024-11-06": "elect."}
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]


def table():
    c = load_bars("TSLA").close
    r = 100 * c.pct_change()
    rx = {c.index[c.index.searchsorted(pd.Timestamp(d))].strftime("%Y-%m-%d") for d in REACTIONS_2020}
    rows = []
    for name, named, a, b in MOVES:
        z = r.loc[a:b]
        big = z.idxmax()
        for d, v in z.items():
            mon = d - pd.Timedelta(days=d.weekday())
            key = d.strftime("%Y-%m-%d")
            rows.append({"move": name, "week_of": mon.date(), "named_week": mon == pd.Timestamp(named), "date": d.date(),
                         "weekday": d.strftime("%a"), "pct": v, "biggest_in_move": d == big,
                         "event": "R" if key in rx else EVENTS.get(key, "")})
    return pd.DataFrame(rows)


def figure(t):
    f, axs = plt.subplots(4, 2, figsize=(14, 15.5))
    for a, (name, named, _, _) in zip(axs.ravel(), MOVES):
        z = t[t.move == name]
        weeks = sorted(z.week_of.unique())
        M = np.full((len(weeks), 6), np.nan)
        lab = [["" for _ in range(6)] for _ in weeks]
        c = load_bars("TSLA").close
        for i, w in enumerate(weeks):
            s = z[z.week_of == w]
            for _, row in s.iterrows():
                j = DAYS.index(row.weekday)
                M[i, j] = row.pct
                lab[i][j] = f"{row.pct:+.1f}" + (f"\n{row.event}" if row.event else "")
            d0, d1 = pd.Timestamp(s.date.iloc[0]), pd.Timestamp(s.date.iloc[-1])
            wk = 100 * (c.loc[d1] / c.shift(1).loc[d0] - 1)
            M[i, 5] = wk / 2.5                      # week total drawn on a compressed scale so days stay readable
            lab[i][5] = f"{wk:+.1f}%"
        a.imshow(np.clip(M, -10, 10), cmap=CMAP, vmin=-10, vmax=10, aspect="auto")
        for i in range(len(weeks)):
            for j in range(6):
                if np.isnan(M[i, j]):
                    a.text(j, i, "holiday" if j < 5 else "", ha="center", va="center", fontsize=7, color=MUTED)
                    continue
                strong = abs(M[i, j]) >= 7 if j < 5 else abs(M[i, j]) * 2.5 >= 15
                a.text(j, i, lab[i][j], ha="center", va="center", fontsize=8.5 if j < 5 else 9,
                       color=SURF if strong else INK, weight="bold" if j == 5 else "normal")
        big = z[z.biggest_in_move].iloc[0]
        bi, bj = weeks.index(big.week_of), DAYS.index(big.weekday)
        a.add_patch(plt.Rectangle((bj - 0.5, bi - 0.5), 1, 1, fill=False, ec=INK, lw=2.4))
        a.set_xticks(range(6), DAYS + ["week"])
        a.xaxis.tick_top()
        a.set_yticks(range(len(weeks)), [("▶ " if pd.Timestamp(w) == pd.Timestamp(named) else "") + f"wk of {pd.Timestamp(w):%b %d %Y}"
                                         for w in weeks], fontsize=8.5)
        for tl, w in zip(a.get_yticklabels(), weeks):
            if pd.Timestamp(w) == pd.Timestamp(named):
                tl.set_weight("bold")
        a.axvline(4.5, color=SURF, lw=4)
        a.tick_params(length=0)
        for s in a.spines.values():
            s.set_visible(False)
        a.set_title(f"{name}: biggest day {big.weekday} {pd.Timestamp(big.date):%b %d} ({big.pct:+.1f}%)", loc="left", fontsize=10, color=INK, pad=22)
    tb = t[t.biggest_in_move].weekday.value_counts().reindex(DAYS, fill_value=0)
    t5 = t[t.pct >= 5].weekday.value_counts().reindex(DAYS, fill_value=0)
    f.suptitle("The TSLA moves you named, day by day (daily % change; ▶ = the week you named; box = the move's biggest day; "
               "R = report reaction)\n"
               f"Biggest day of each move: {', '.join(f'{d} {n}' for d, n in tb.items())}.   "
               f"Days of +5% or more inside these windows: {', '.join(f'{d} {n}' for d, n in t5.items())}.\n"
               "The day that made each move was usually an event (a report, deliveries, the election, news), and it fell on any weekday.",
               x=0.01, ha="left", fontsize=10.5, color=INK, weight="bold")
    f.tight_layout(rect=(0, 0, 1, 0.955))
    f.savefig(OUT / "named_weeks_TSLA.png", dpi=150, facecolor=SURF)


if __name__ == "__main__":
    t = table()
    t.to_csv(OUT / "named_weeks_TSLA.csv", index=False)
    figure(t)
    print(t[t.biggest_in_move][["move", "date", "weekday", "pct", "event"]].round(1).to_string(index=False))
    print("+5% days by weekday:", t[t.pct >= 5].weekday.value_counts().reindex(DAYS, fill_value=0).to_dict())
    print("+5% days on the first trading day of their week:",
          int(t[t.pct >= 5].apply(lambda x: t[(t.week_of == x.week_of)].date.min() == x.date, axis=1).sum()), "of", int((t.pct >= 5).sum()))
    print("saved", OUT / "named_weeks_TSLA.png")
