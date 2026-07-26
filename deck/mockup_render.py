"""Render the ASCII UI mockups from docs/mockups.md as clean images for the deck.

The mockups are box-drawing characters, so this needs a monospace font with full
box-drawing coverage and exact cell alignment — anything proportional turns the
frames into confetti. DejaVu Sans Mono ships with matplotlib and has the glyphs.

Rendered as an image rather than retyped as slide text because PowerPoint will
re-flow and re-kern a text box and break the alignment on someone else's machine.
"""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

SRC = Path("/mnt/user-data/uploads/ubicomp/ambient-recorder/docs/mockups.md")
OUT = Path("figures")
NAVY, INK, SURFACE = "#003057", "#12141a", "#fcfcfb"

blocks = re.findall(r"```\n(.*?)```", SRC.read_text(encoding="utf-8"), re.S)
mono = FontProperties(family="DejaVu Sans Mono", size=13)


# Two glyphs in the source mockups have no DejaVu Sans Mono coverage and render
# as tofu boxes. Substituted with ASCII of the same cell width so the frames stay
# aligned — swapping in a wider glyph would shear every line below it.
GLYPH_FIX = {"\u2913": "v", "\u2934": "^"}


def render(text: str, name: str, pad: float = 0.35, color: str = INK):
    for a, b in GLYPH_FIX.items():
        text = text.replace(a, b)
    lines = text.rstrip("\n").split("\n")
    rows, cols = len(lines), max(len(l) for l in lines)
    # 13pt DejaVu Sans Mono: advance width is 0.602 em, line height ~1.18 em.
    w = cols * 13 * 0.602 / 72 + 2 * pad
    h = rows * 13 * 1.18 / 72 + 2 * pad
    fig = plt.figure(figsize=(w, h), dpi=200, facecolor=SURFACE)
    fig.text(pad / w, 1 - pad / h, "\n".join(lines), fontproperties=mono,
             color=color, va="top", ha="left", linespacing=1.18)
    fig.savefig(OUT / f"{name}.png", dpi=200, facecolor=SURFACE)
    plt.close(fig)
    print(f"  figures/{name}.png  ({cols}x{rows} chars)")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    print("rendering mockups:")
    render(blocks[0], "mockup_setup", color=INK)      # experiment + pre-flight
    render(blocks[1], "mockup_recording", color=NAVY)  # live, with the O1 gate
    render(blocks[3], "mockup_complete", color=INK)    # session summary
