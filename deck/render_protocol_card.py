"""Render the run protocol as an ASCII card, in the deck's mockup style.

Rendered as an image rather than typed into a PowerPoint text box: PowerPoint
re-flows and re-kerns text on someone else's machine and shears every box-drawing
line below the first wrap. DejaVu Sans Mono ships with matplotlib and has full
box-drawing coverage at exact cell width.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

OUT = Path("figures")
NAVY, INK, SURFACE = "#003057", "#12141a", "#fcfcfb"

PROTOCOL = r"""
┌──────────────────────────────────────────────────────────────────┐
│  AMBIENT 2 x 3   ·   one continuous recording, three devices     │
├──────────────────────────────────────────────────────────────────┤
│  timer   action                                    cell          │
│  ─────   ──────────────────────────────────────    ────────────  │
│  0:00    Mark sync                                               │
│  0:05    Mark sync                                               │
│  0:10    three raps, 1 s apart          <- fiducial              │
│  0:15    stand still                    <- baro warm-up          │
│                                                                  │
│  1:15    stand still, 90 s                         baseline  M1  │
│  2:45    normal close  x6, 10 s apart              normal    M1  │
│  4:00    slam          x6, 10 s apart              slam      M1  │
│                                                                  │
│  5:15    >>> FLIP THE DEHUMIDIFIER <<<  · settle 30 s            │
│                                                                  │
│  5:45    stand still, 90 s                         baseline  M2  │
│  7:15    slam          x6, 10 s apart              slam      M2  │
│  8:30    normal close  x6, 10 s apart              normal    M2  │
│                                                                  │
│  9:45    STOP & EXPORT  x3                                       │
└──────────────────────────────────────────────────────────────────┘
   M1 / M2 = machine state.  Coin flip decides which comes first.
   Door order flips between halves so "slam" is not always last.
"""

WHY_N6 = r"""
┌──────────────────────────────────────────────────────────────────┐
│  WHY n = 6 PER CELL                                              │
├──────────────────────────────────────────────────────────────────┤
│  An exact permutation test's smallest possible p is fixed by     │
│  the trial count BEFORE any data exists:                         │
│                                                                  │
│      n per group   arrangements   smallest p obtainable          │
│      ───────────   ────────────   ───────────────────────        │
│          2 v 2        C(4,2)=6          0.167    <- the pilot    │
│          3 v 3       C(6,3)=20          0.050                    │
│          4 v 4       C(8,4)=70          0.014                    │
│          6 v 6     C(12,6)=924          0.001    <- frozen       │
│                                                                  │
│  Holm correction over 2 comparisons puts the bar at 0.025.       │
│                                                                  │
│      n=2  ->  0.167 > 0.025   cannot reach it                    │
│      n=3  ->  0.050 > 0.025   cannot reach it                    │
│      n=6  ->  0.001 < 0.025   can                                │
│                                                                  │
│  The pilot could not have returned a significant result no       │
│  matter what the doors did. Six is the smallest n that makes     │
│  the test capable of answering the question we are asking.       │
└──────────────────────────────────────────────────────────────────┘
   To go faster, cut CONDITIONS, not REPLICATES.
   Replicates make a test possible. Conditions make it interesting.
"""

mono = FontProperties(family="DejaVu Sans Mono", size=13)


def render(text: str, name: str, pad: float = 0.35, color: str = INK):
    lines = text.strip("\n").split("\n")
    rows, cols = len(lines), max(len(l) for l in lines)
    w = cols * 13 * 0.602 / 72 + 2 * pad
    h = rows * 13 * 1.24 / 72 + 2 * pad
    fig = plt.figure(figsize=(w, h), dpi=200, facecolor=SURFACE)
    fig.text(pad / w, 1 - pad / h, "\n".join(lines), fontproperties=mono,
             color=color, va="top", ha="left", linespacing=1.18)
    fig.savefig(OUT / f"{name}.png", dpi=200, facecolor=SURFACE)
    plt.close(fig)
    print(f"  figures/{name}.png  ({cols}x{rows} chars)")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    print("rendering protocol cards:")
    render(PROTOCOL, "mockup_protocol", color=NAVY)
    render(WHY_N6, "mockup_why_n6", color=INK)
