"""Title / plan / contributions cards for the demo video.

Exactly 1920x1080 so they drop into a timeline without scaling. Same palette and
type as the figures, so cards and charts read as one deck rather than as slides
pasted between graphs.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

SURFACE, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
W, H, DPI = 1920, 1080, 160


def _card():
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI, facecolor=SURFACE)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    return fig, ax


def save(fig, name):
    fig.savefig(f"figures/{name}.png", dpi=DPI, facecolor=SURFACE)
    plt.close(fig)
    print(f"  figures/{name}.png  ({W}x{H})")


def rule(ax, y, x0=.08, x1=.30, color=ORANGE):
    ax.add_patch(Rectangle((x0, y), x1 - x0, .006, color=color, transform=ax.transAxes))


# --- contributions -----------------------------------------------------------

def card_contributions():
    fig, ax = _card()
    rule(ax, .78)
    ax.text(.08, .66, "Contributions", fontsize=31, fontweight="bold", color=INK)
    ax.text(.08, .50, "Christopher Kimberley", fontsize=18, color=ORANGE, fontweight="bold")
    ax.text(.08, .425, "the door-slam pilot — protocol, recording, and the six sessions",
            fontsize=15, color=INK2)
    ax.text(.08, .295, "Caitlin Everett", fontsize=18, color=BLUE, fontweight="bold")
    ax.text(.08, .220, "the recorder, the export schema, the analysis, and the study design",
            fontsize=15, color=INK2)
    save(fig, "card_contributions")


# --- what changed ------------------------------------------------------------

def card_changed():
    fig, ax = _card()
    rule(ax, .86)
    ax.text(.08, .755, "What changed", fontsize=30, fontweight="bold", color=INK)
    items = [
        ("A teammate's phones wouldn't run a dev build.",
         "The Alka-Seltzer study was replaced by a door experiment using only\n"
         "the sensors Expo Go exposes. Device heterogeneity turned out to be a\n"
         "first-order constraint, not a footnote."),
        ("Three sites with one participant each can't support a variance claim.",
         "Participant, location, phone model and building are fully confounded.\n"
         "The multi-site study is now explicitly a case study; the quantitative\n"
         "claims moved to a within-site design with enough trials to carry them."),
        ("We pre-registered.",
         "Metrics, windows, exclusion rules and trial counts are frozen in the\n"
         "repository, dated, before the data existed."),
    ]
    y = .615
    for i, (head, body) in enumerate(items):
        ax.text(.085, y, f"{i+1}", fontsize=16, color=[ORANGE, BLUE, AQUA][i],
                fontweight="bold", ha="center")
        ax.text(.115, y, head, fontsize=16, color=INK, fontweight="bold")
        ax.text(.115, y - .055, body, fontsize=13, color=INK2, va="top", linespacing=1.45)
        y -= .205
    save(fig, "card_changed")


# --- what's queued -----------------------------------------------------------

def card_next():
    fig, ax = _card()
    rule(ax, .87, color=AQUA)
    ax.text(.08, .765, "Queued this week", fontsize=30, fontweight="bold", color=INK)
    items = [
        ("Pendulum dose ladder", "5 levels × 6 trials, randomised order, empty room",
         "the confirmatory spine"),
        ("Overnight ambient runs", "8+ hours unattended, three nights",
         "the refrigerator duty cycle — a disturbance nobody notices"),
        ("Blind detection trial", "4 hours of ordinary activity, log sealed before analysis",
         "does it find events nobody labelled?"),
        ("Barometer vs. weather station", "12 hours against a National Weather Service record",
         "the only channel we can check outside our own project"),
    ]
    y = .625
    for head, what, why in items:
        ax.add_patch(Rectangle((.085, y - .012), .006, .078, color=AQUA,
                               transform=ax.transAxes))
        ax.text(.115, y + .030, head, fontsize=16, color=INK, fontweight="bold")
        ax.text(.115, y - .008, what, fontsize=12.5, color=INK2)
        ax.text(.115, y - .046, why, fontsize=12.5, color=AQUA, style="italic")
        y -= .152
    save(fig, "card_next")


# --- title -------------------------------------------------------------------

def card_title():
    fig, ax = _card()
    ax.text(.08, .60, "Covariate", fontsize=52, fontweight="bold", color=INK)
    ax.text(.083, .505, "recording the room, so experiments reproduce",
            fontsize=19, color=INK2)
    rule(ax, .455, x1=.22)
    ax.text(.08, .345, "CS-7470 Mobile & Ubiquitous Computing  ·  Team 42",
            fontsize=14, color=INK2)
    ax.text(.08, .295, "Caitlin Everett · Christopher Kimberley",
            fontsize=14, color=INK2)
    save(fig, "card_title")


# --- re-enactment label ------------------------------------------------------

def card_reenactment():
    """Lower-third disclosure for any shot filmed after the fact.

    A re-enactment cut over narration is ordinary demo craft. Presenting one as
    the run that produced the numbers is not, and the distinction costs one line
    of text on screen.
    """
    fig, ax = _card()
    ax.add_patch(Rectangle((0, 0), 1, .155, color=INK, alpha=.88,
                           transform=ax.transAxes))
    ax.text(.06, .088, "RE-ENACTMENT", fontsize=16, color=ORANGE, fontweight="bold")
    ax.text(.06, .042, "filmed separately for illustration — not the recorded session",
            fontsize=13, color="#e9e8e4")
    save(fig, "card_reenactment")


if __name__ == "__main__":
    import os
    os.makedirs("figures", exist_ok=True)
    print("rendering cards:")
    card_title(); card_changed(); card_next(); card_contributions(); card_reenactment()
