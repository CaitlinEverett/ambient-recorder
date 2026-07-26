"""Add the feasibility-arc slides to build_deck.py.

Five insertions, placed to carry the argument the deck was missing: consumer
hardware has nameable failure modes, so here is one decisive test per sensor, here
is what we currently believe per channel, and here is why either outcome is useful.
Plus the ASCII UI mockup, which is the only artefact showing what the thing looks
like to use.

Chris's demo slide is widened to let the footage run rather than be clipped to ten
seconds.
"""
import sys
from pathlib import Path

p = Path("build_deck.py")
s = p.read_text()


def sub(old, new, n=1):
    global s
    if s.count(old) != n:
        sys.exit(f"NO MATCH ({s.count(old)}):\n{old[:200]}")
    s = s.replace(old, new)


# --- a two-column compact row helper, for the test/verdict tables -------------
sub('''def picture(slide, name, top=2.05, bottom=6.60, max_w=11.3):''',
    '''def table(slide, cols, rows, top=2.30, row_h=0.62, size=13.5, head_size=12):
    """Simple column-positioned table. Columns are (label, x, width) in inches."""
    for label, x, _ in cols:
        text(slide, x, top, 3.0, 0.3, label, size=head_size, color=MUTED)
    y = top + 0.42
    for r in rows:
        for (_, x, w), cell in zip(cols, r):
            body, colour, bold = (cell if isinstance(cell, tuple) else (cell, MUTED, False))
            text(slide, x, y, w, row_h, body, size=size, color=colour,
                 bold=bold, line=1.2)
        y += row_h
    return y


def picture(slide, name, top=2.05, bottom=6.60, max_w=11.3):''')


# =============================================================================
# NEW · after slide 2 (why record the room) — why this is hard
# =============================================================================
ANCHOR_3 = '''# =============================================================================
# 3 — the plan
# ============================================================================='''
sub(ANCHOR_3, '''# =============================================================================
# NEW — why consumer hardware makes this hard
# =============================================================================
s = new_slide()
title(s, "Why this is hard", "documented failure modes of consumer-grade sensors")
table(s,
      [("failure mode", 0.85, 3.5), ("evidence", 4.5, 4.4), ("consequence for us", 9.1, 3.4)],
      [(("The raw stream isn't raw", NAVY, True),
        "SensorID recovers factory calibration\\nbaked into firmware (IEEE S&P 2019)",
        "we read a vendor-conditioned value,\\nnot a physical quantity"),
       (("Self-heating", NAVY, True),
        "MEMS gyro drifts 317 °/h in its first\\n400 s from power-on alone (2019)",
        "a phone logging continuously starts\\nby measuring itself"),
       (("Per-unit thermal drift", NAVY, True),
        "four identical units: −1.2 to +1.4 mg/°C\\nagainst a ±0.5 spec (2022)",
        "no generic correction exists;\\nevery device needs its own"),
       (("Automatic pipelines", NAVY, True),
        "ambient-light cosine response off\\n−33.87%; colorimetry needs locked ISO",
        "auto-exposure and AGC must be\\ndefeated before light or sound counts"),
       (("Device heterogeneity", NAVY, True),
        "quality metrics alone predict the OS at\\n0.98 accuracy (Sensors 2024)",
        "a multi-device study measures\\ndevices as much as rooms"),
       (("No traceability", NAVY, True),
        "low-cost sensing lacks an unbroken\\ncalibration chain to an NMI (2020)",
        "relative change within a session;\\nnever an absolute value")],
      top=2.15, row_h=0.79, size=12.5)
text(s, 0.85, 6.95, 11.4, 0.4,
     "Plus two of our own: sensor occlusion — lens film, lint in the mic port, a case "
     "over the barometer vent — and OS suspension of background apps on long runs.",
     size=13, color=NAVY)
notes(s, "PLACEHOLDER")


# =============================================================================
# NEW — one decisive test per sensor
# =============================================================================
s = new_slide()
title(s, "One test per sensor", "each cheap, onsite, and sufficient to settle that channel")
table(s,
      [("channel", 0.85, 2.4), ("question", 3.3, 3.3), ("test", 6.7, 3.2),
       ("passes if", 10.0, 2.7)],
      [(("vibration / accel", NAVY, True), "tracks a graded mechanical dose?",
        "pendulum ladder, 5 levels × 6", "log-log slope CI excludes 0"),
       (("barometer", NAVY, True), "measuring air, or itself?",
        "8 h vs. a weather station,\\nplus the warm-up curve", "slope ≈ 1; offset\\nimplies true altitude"),
       (("magnetometer", NAVY, True), "usable at bench distance?",
        "magnet at 5 / 10 / 20 / 30 cm", "detectable at ≥ 10 cm;\\nexponent near −3"),
       (("light", DEEPGOLD, True), "measurement or auto-exposure?",
        "lamp step, exposure locked\\nand unlocked", "monotonic with lux,\\nAE-independent"),
       (("micLevel", DEEPGOLD, True), "level, or AGC output?",
        "fixed tone, fixed distance,\\nvarying background", "tracks the source,\\nnot the background"),
       (("cross-device", NAVY, True), "do two models agree?",
        "same events, two devices,\\none surface", "r ≥ 0.9; bias within\\nthe noise floor")],
      top=2.20, row_h=0.78, size=12.5)
text(s, 0.85, 6.95, 11.4, 0.4,
     "Gold rows need a compiled dev client and will not be answered this term. "
     "The rest run in one night and about 75 minutes.", size=13, color=NAVY)
notes(s, "PLACEHOLDER")


''' + ANCHOR_3)


# =============================================================================
# NEW · the UI mockup, after implementation (slide 4)
# =============================================================================
ANCHOR_5 = '''# =============================================================================
# 5 — channels
# ============================================================================='''
sub(ANCHOR_5, '''# =============================================================================
# NEW — what it looks like to use
# =============================================================================
s = new_slide()
title(s, "In use", "recording screen: live values, sampling health, and the O1 gate")
slide_pic = picture(s, "mockup_recording.png", top=1.95, bottom=7.05, max_w=4.2)
text(s, 6.4, 2.25, 6.1, 4.4, [
    ("Sampling health is on screen, not buried in the export.",
     {"size": 17, "bold": True, "color": NAVY, "space": 10}),
    ("Every channel shows its latest value, its sample count and its drop fraction "
     "while recording. The O1 gate — under 2% dropped samples over at least 30 "
     "minutes — has its own progress bar, because a session that fails it is not "
     "worth analysing and the operator should know before walking away.",
     {"size": 14.5, "color": MUTED, "space": 14}),
    ("The magnetometer row here is flagged at 3.2%. That is the display doing its job.",
     {"size": 14.5, "color": DEEPGOLD, "space": 14}),
    ("Mark Sync and Stop are the only two controls available while recording.",
     {"size": 14.5, "color": MUTED}),
], line=1.3)
notes(s, "PLACEHOLDER")


''' + ANCHOR_5)


# =============================================================================
# Chris's demo — give the footage room
# =============================================================================
sub('''cue(s, "▶  Footage: door experiment",
    "Christopher Kimberley, Toronto · 10–15 seconds")''',
    '''cue(s, "▶  Footage: door experiment, narrated by Christopher Kimberley",
    "let it run · caption over any cut: “protocol continues — 4 further trials”")''')


# =============================================================================
# NEW · midway hypothesis, before scope and limitations
# =============================================================================
ANCHOR_14 = '''# =============================================================================
# 14 — limitations
# ============================================================================='''
sub(ANCHOR_14, '''# =============================================================================
# NEW — midway hypothesis
# =============================================================================
s = new_slide()
title(s, "Midway hypothesis", "what we currently believe per channel, and what would change it")
table(s,
      [("channel", 0.85, 2.3), ("current position", 3.2, 3.1), ("on what evidence", 6.4, 3.2),
       ("would change if", 9.7, 3.0)],
      [(("vibration", TEAL, True), ("likely good enough", TEAL, True),
        "13–109× noise floor; ~1%\\nwithin-condition repeatability",
        "the dose ladder is not\\nmonotonic"),
       (("accelerometer", TEAL, True), ("good for timing,\\nnot amplitude", TEAL, True),
        "recovered every fiducial and\\nevent; 1–4% above gravity",
        "fiducials fail to align\\ntwo devices"),
       (("barometer", DEEPGOLD, True), ("not yet trusted", DEEPGOLD, True),
        "session rise identical in\\nbaseline and slam",
        "it tracks a weather\\nstation over 8 h"),
       (("magnetometer", DEEPGOLD, True), ("probably not useful\\nat this scale", DEEPGOLD, True),
        "event deviation 0.31–0.56 µT;\\nbaseline spread 1.03 µT",
        "the magnet ladder is\\ndetectable at 10 cm"),
       (("light · micLevel", MUTED, True), ("unknown", MUTED, True),
        "untested — both need a\\ncompiled dev client",
        "we get a dev build\\nrunning"),
       (("cross-device", MUTED, True), ("untested", MUTED, True),
        "one device",
        "the two-device run\\nreturns r ≥ 0.9")],
      top=2.15, row_h=0.76, size=12.5)
text(s, 0.85, 6.90, 11.4, 0.5,
     "One channel looks good enough, one is promising, one probably is not, and three are "
     "unknown. Four runs settle all but the two that need a dev build.",
     size=14, color=NAVY, line=1.25)
notes(s, "PLACEHOLDER")


''' + ANCHOR_14)


# =============================================================================
# NEW · if the sensors are not good enough, before contributions
# =============================================================================
ANCHOR_17 = '''# =============================================================================
# 17 — contributions
# ============================================================================='''
sub(ANCHOR_17, '''# =============================================================================
# NEW — if the sensors are not good enough
# =============================================================================
s = new_slide()
title(s, "Either outcome is useful", "the phone is the recorder; whether it is also the sensor is the question")
for i, (col, head, body) in enumerate([
    (TEAL, "If the sensors pass",
     "Ambient context capture becomes free for anyone with a phone — usable in "
     "teaching labs, in citizen science, and as opportunistic covariate logging where "
     "no instrumentation exists."),
    (DEEPGOLD, "If they fail",
     "The app remains the experiment-linked recorder, the schema and the UI, and the "
     "sensing moves to a cheap external package over BLE. Our ESP32 + BME280 stretch "
     "goal is already this architecture."),
]):
    x = 0.85 + i * 6.05
    hexagon(s, x, 2.30, 0.56, "✓" if i == 0 else "→", fill=col, size=14)
    text(s, x, 3.12, 5.5, 0.4, head, size=20, bold=True, color=NAVY)
    text(s, x, 3.62, 5.5, 1.6, body, size=14.5, color=MUTED, line=1.35)

text(s, 0.85, 5.60, 11.5, 1.4, [
    ("The second case has measured support.",
     {"size": 16, "bold": True, "color": NAVY, "space": 8}),
    ("The same sound-measurement apps, re-run with external calibrated microphones, came "
     "within ±1 dB of reference (Kardous & Shaw, JASA 2016) — the built-in signal chain "
     "was the limit, not the phone. A phone with an external microphone can then meet "
     "IEC 61672 Class 2.", {"size": 14.5, "color": MUTED}),
], line=1.3)
notes(s, "PLACEHOLDER")


''' + ANCHOR_17)

p.write_text(s)
print("build_deck.py: 5 slides added")
