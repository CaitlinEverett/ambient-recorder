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
        ("Two of five channels need a compiled dev client.",
         "Light and sound level are native modules, so they don't run in Expo Go.\n"
         "We scoped the study to the channels that install by scanning a QR code —\n"
         "and treat that friction as a finding, not an inconvenience."),
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


# --- front half: plan, architecture, channels, privacy -----------------------

def card_plan():
    fig, ax = _card()
    rule(ax, .86, color=BLUE)
    ax.text(.08, .755, "The plan", fontsize=30, fontweight="bold", color=INK)
    items = [
        ("Build", "an ambient-context recorder: pressure, motion, magnetic field,\n"
                  "light and sound level on one clock, exported as a file bound to\n"
                  "a named experiment"),
        ("Reproduce", "two known sensing techniques on commodity hardware, and see\n"
                      "what survives the move off instrument-grade sensors"),
        ("Evaluate", "whether any of it is trustworthy — sampling health, agreement\n"
                     "between devices, and whether a logged covariate explains\n"
                     "variation between runs"),
    ]
    y = .615
    for i, (head, body) in enumerate(items):
        ax.text(.085, y, head, fontsize=17, color=[BLUE, ORANGE, AQUA][i],
                fontweight="bold", va="top")
        ax.text(.27, y, body, fontsize=13.5, color=INK2, va="top", linespacing=1.5)
        y -= .185
    ax.text(.08, .105, "Constraint, chosen deliberately:  no special hardware.",
            fontsize=15, color=INK, fontweight="bold")
    ax.text(.08, .055, "A phone every lab already owns, or it doesn't get used.",
            fontsize=13.5, color=INK2)
    save(fig, "card_plan")


def card_architecture():
    fig, ax = _card()
    rule(ax, .875, color=BLUE)
    ax.text(.08, .775, "What we built", fontsize=30, fontweight="bold", color=INK)

    layers = [
        (BLUE,   "Direct sensors",  "expo-sensors",
         "accelerometer 50 Hz  ·  magnetometer 25 Hz  ·  barometer"),
        (ORANGE, "Native modules",  "Swift on iOS, Kotlin on Android",
         "camera-EXIF light  ·  microphone LEVEL only — audio is never recorded"),
        (AQUA,   "Derived channel", "computed from the raw stream",
         "vibration: gravity removed, RMS + peak over a 200 ms window"),
        (INK2,   "Session record",  "one session, one JSON file",
         "metadata  ·  per-channel sampling health  ·  every sample on one clock"),
    ]
    y = .625
    for col, name, how, what in layers:
        ax.add_patch(Rectangle((.085, y - .020), .006, .088, color=col,
                               transform=ax.transAxes))
        ax.text(.115, y + .038, name, fontsize=17, color=INK, fontweight="bold")
        ax.text(.315, y + .038, how, fontsize=13, color=col, style="italic")
        ax.text(.115, y - .004, what, fontsize=13, color=INK2)
        y -= .152
    ax.text(.08, .055, "React Native under Expo Go — a teammate joins by scanning a QR code.",
            fontsize=14, color=INK)
    save(fig, "card_architecture")


def card_channels():
    fig, ax = _card()
    rule(ax, .885, color=ORANGE)
    ax.text(.08, .785, "Channels", fontsize=30, fontweight="bold", color=INK)
    rows = [
        ("accelerometer", "[x, y, z]", "g", "50 Hz", BLUE),
        ("magnetometer", "[x, y, z]", "\u00b5T", "25 Hz", BLUE),
        ("barometer", "[pressure, rel. altitude]", "hPa, m", "event-driven", BLUE),
        ("vibration", "[rms, peak]", "g", "5 Hz  \u00b7  derived", AQUA),
        ("light", "[brightness]", "EV", "5 Hz  \u00b7  dev build", ORANGE),
        ("micLevel", "[rms]", "dBFS", "10 Hz  \u00b7  dev build", ORANGE),
        ("sync", "[pulse, of]", "\u2014", "on demand  \u00b7  fiducial", AQUA),
    ]
    ax.text(.10, .675, "channel", fontsize=12.5, color=INK2)
    ax.text(.33, .675, "values", fontsize=12.5, color=INK2)
    ax.text(.60, .675, "units", fontsize=12.5, color=INK2)
    ax.text(.76, .675, "rate", fontsize=12.5, color=INK2)
    y = .60
    for name, vals, units, rate, col in rows:
        ax.text(.10, y, name, fontsize=15, color=col, fontweight="bold",
                family="monospace")
        ax.text(.33, y, vals, fontsize=14, color=INK2, family="monospace")
        ax.text(.60, y, units, fontsize=14, color=INK2)
        ax.text(.76, y, rate, fontsize=13.5, color=INK2)
        y -= .073
    ax.text(.08, .055,
            "Sound is a level, never a waveform \u2014 there is no audio to draw one from.",
            fontsize=14, color=INK)
    save(fig, "card_channels")


def card_privacy():
    fig, ax = _card()
    rule(ax, .875, color=AQUA)
    ax.text(.08, .775, "Built in, not promised", fontsize=30, fontweight="bold", color=INK)
    items = [
        "Audio is never recorded. The microphone channel stores a level in dBFS.",
        "Reference video is audio-free by construction \u2014 the flag is invariantly false.",
        "Location, if enabled at all, is a reverse-geocoded region and an altitude.\nNever coordinates. Absent by default.",
        "Recording is session-scoped and user-initiated. There is no background collection.",
    ]
    y = .625
    for t in items:
        ax.text(.085, y, "\u2713", fontsize=17, color=AQUA, fontweight="bold", va="top")
        ax.text(.125, y, t, fontsize=14.5, color=INK2, va="top", linespacing=1.5)
        y -= .135
    ax.text(.08, .085,
            "Longitudinal ambient data is still data about a household.",
            fontsize=15, color=INK, fontweight="bold")
    ax.text(.08, .035,
            "Occupancy, routine, device fingerprint, floor of a building \u2014 the report says so.",
            fontsize=13.5, color=INK2)
    save(fig, "card_privacy")


# --- the idea ----------------------------------------------------------------

def card_idea():
    """Why this belongs in a ubicomp course rather than a stats one."""
    fig, ax = _card()
    rule(ax, .905, color=AQUA)
    ax.text(.08, .825, "The idea", fontsize=28, fontweight="bold", color=INK)

    ax.text(.08, .715, "Ubicomp asks what the sensors say about the person.",
            fontsize=19, color=INK2, va="top")
    ax.text(.08, .655, "We asked what they say about the room \u2014 and whether",
            fontsize=19, color=INK, va="top", fontweight="bold")
    ax.text(.08, .600, "that is worth writing down.",
            fontsize=19, color=INK, va="top", fontweight="bold")

    beats = [
        (BLUE, "The deployment problem is already solved.",
         "Weiser's calm technology arrived as a phone in every pocket. The hard part is not\n"
         "getting a sensor into the room \u2014 it is what to do with the one already there."),
        (ORANGE, "Context-awareness, pointed the other way.",
         "Activity recognition senses a person to serve that person. Here the sensing serves a\n"
         "record \u2014 an experiment that has to survive being repeated somewhere else, later."),
        (AQUA, "The hack is a derived channel.",
         "Gravity is a large constant; a door closing is a rounding error beside it. Subtract the\n"
         "constant and the same sensor gains two orders of magnitude \u2014 no new hardware."),
    ]
    y = .475
    for col, head, body in beats:
        ax.add_patch(Rectangle((.085, y - .088), .006, .105, color=col,
                               transform=ax.transAxes))
        ax.text(.115, y, head, fontsize=15, color=INK, fontweight="bold", va="top")
        ax.text(.115, y - .040, body, fontsize=12.5, color=INK2, va="top",
                linespacing=1.5)
        y -= .140
    save(fig, "card_idea")


# --- limitations -------------------------------------------------------------

def card_limitations():
    """The reviewer's critique, adopted rather than defended against."""
    fig, ax = _card()
    rule(ax, .905, color=ORANGE)
    ax.text(.08, .825, "What this is \u2014 and isn't", fontsize=28,
            fontweight="bold", color=INK)

    ax.text(.085, .700, "A FEASIBILITY STUDY", fontsize=14.5, color=AQUA,
            fontweight="bold", va="top")
    left = ["Detects a real event at 13\u2013109\u00d7 its noise floor",
            "Repeatable to ~1% within a condition",
            "Instrument characterised \u2014 warm-up, drift,\nsampling health",
            "A derived channel beats its raw sensor, 3\u20135\u00d7"]
    y = .625
    for t in left:
        ax.text(.085, y, "\u2713", fontsize=13.5, color=AQUA, fontweight="bold", va="top")
        ax.text(.118, y, t, fontsize=13, color=INK2, va="top", linespacing=1.45)
        y -= .085

    ax.text(.545, .700, "NOT A GENERALISATION", fontsize=14.5, color=ORANGE,
            fontweight="bold", va="top")
    right = ["One participant per site \u2014 person, city,\nphone and building are confounded",
             "One operator, one room, one device family",
             "Light and sound level untested \u2014 dev build",
             "Cross-device agreement: one pair, one site"]
    y = .625
    for t in right:
        ax.text(.545, y, "\u2014", fontsize=13.5, color=ORANGE, va="top")
        ax.text(.578, y, t, fontsize=13, color=INK2, va="top", linespacing=1.45)
        y -= .085

    ax.add_patch(Rectangle((.08, .245), .84, .003, color="#e2e1dd",
                           transform=ax.transAxes))
    ax.text(.08, .195,
            "Our reviewer said it first: three sites with one participant each cannot show that a",
            fontsize=14, color=INK, va="top")
    ax.text(.08, .143,
            "logged covariate reduces between-site variance. They were right \u2014 so the quantitative",
            fontsize=14, color=INK, va="top")
    ax.text(.08, .091,
            "claims moved to a within-site design, and the multi-site work stays a case study.",
            fontsize=14, color=INK, va="top")
    save(fig, "card_limitations")


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
    card_title(); card_idea(); card_plan(); card_architecture(); card_channels()
    card_privacy(); card_limitations()
    card_changed(); card_next(); card_contributions(); card_reenactment()
