"""Build the Covariate demo deck on the Georgia Tech 2022 template.

Design decisions worth stating, because they are the ones a reader would query:

* **Brand colours for furniture, validated palette inside the figures.** GT navy
  (#003057) and Tech gold (#EAAA00) carry titles, hexes and rules. They do NOT
  carry data series: run through the categorical-palette checks, navy and GT teal
  fall below the chroma floor (they read gray) and Tech gold falls outside the
  lightness band and under 3:1 on white. Brand colours are chosen for a logo on a
  building, not for telling four lines apart at 12pt. The figures keep the
  already-validated blue/orange/aqua.
* **The hexagon is the motif**, taken from the template's own shape language
  rather than invented — GT's deck already uses hex clusters. It numbers list
  items and holds stat callouts, which keeps the deck recognisably Georgia Tech
  and not recognisably generic.
* **Dark navy for opening, section and closing slides; white for content.** The
  sandwich, so the deck has a shape rather than eighteen identical pages.
* No accent stripes, no rules under titles.

Speaker notes carry the full narration, so the deck can be filmed straight
through. `[CUE]` lines mark where footage is cut in.
"""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

TEMPLATE, OUT = "gt.pptx", "Covariate_Demo.pptx"
FIG = Path("figures")

NAVY = RGBColor(0x00, 0x30, 0x57)
GOLD = RGBColor(0xEA, 0xAA, 0x00)
OLDGOLD = RGBColor(0xB3, 0xA3, 0x69)
TEAL = RGBColor(0x00, 0x8C, 0x95)
INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x54, 0x58, 0x59)
# GT gold measures about 2:1 on white. It fills shapes; it never sets type on a
# light surface. DEEPGOLD is the darkened step for the cases where a gold-family
# text colour is genuinely wanted.
DEEPGOLD = RGBColor(0x7A, 0x5C, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
PALE = RGBColor(0xF2, 0xF3, 0xF4)

W, H = 13.333, 7.5
FONT = "Arial"

prs = Presentation(TEMPLATE)
# Drop the template's own 22 example slides; keep its layouts, theme and logo.
sld_lst = prs.slides._sldIdLst
for sld in list(sld_lst):
    # Drop the relationship as well as the list entry. Removing only the entry
    # leaves the slide parts in the package: python-pptx then reuses their
    # numbers for new slides, and the saved zip carries two members called
    # slide18.xml. PowerPoint reads that as a corrupt file.
    prs.part.drop_rel(sld.rId)
    sld_lst.remove(sld)

PLAIN = prs.slide_layouts[2]      # Title - Plain: GT logo, subtle background
TITLE_TT = prs.slide_layouts[3]   # Title - Tech Tower


# --- helpers -----------------------------------------------------------------


def _clear_placeholders(slide):
    """Template title layouts carry two placeholders; we position our own text."""
    for ph in list(slide.placeholders):
        ph._element.getparent().remove(ph._element)


def new_slide(layout=PLAIN, dark=False):
    s = prs.slides.add_slide(layout)
    _clear_placeholders(s)
    if dark:
        bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W), Inches(H))
        bg.fill.solid(); bg.fill.fore_color.rgb = NAVY
        bg.line.fill.background(); bg.shadow.inherit = False
        s.shapes._spTree.remove(bg._element)
        s.shapes._spTree.insert(2, bg._element)   # behind everything, above bg art
    return s


def text(slide, x, y, w, h, runs, size=16, color=INK, bold=False,
         align=PP_ALIGN.LEFT, space=6, line=1.0):
    """runs: str, or list of (text, {overrides}) tuples, one paragraph each."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    items = [runs] if isinstance(runs, str) else runs
    for i, item in enumerate(items):
        body, over = (item, {}) if isinstance(item, str) else item
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = over.get("align", align)
        p.space_after = Pt(over.get("space", space))
        p.line_spacing = over.get("line", line)
        r = p.add_run(); r.text = body
        f = r.font
        f.name = FONT
        f.size = Pt(over.get("size", size))
        f.bold = over.get("bold", bold)
        f.color.rgb = over.get("color", color)
        f.italic = over.get("italic", False)
    return tb


def hexagon(slide, x, y, side, label, fill=NAVY, fg=WHITE, size=15):
    """The motif. Small GT hex holding a numeral, letter or short stat."""
    sh = slide.shapes.add_shape(MSO_SHAPE.HEXAGON, Inches(x), Inches(y),
                                Inches(side), Inches(side * 0.88))
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.fill.background(); sh.shadow.inherit = False
    tf = sh.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label
    r.font.name = FONT; r.font.size = Pt(size); r.font.bold = True
    r.font.color.rgb = fg
    return sh


def title(slide, t, sub=None, dark=False):
    text(slide, 0.85, 0.62, 11.6, 1.0, t, size=36, bold=True,
         color=WHITE if dark else NAVY)
    if sub:
        text(slide, 0.85, 1.42, 11.6, 0.5, sub, size=16,
             color=RGBColor(0xC8, 0xD2, 0xDC) if dark else MUTED)


def hex_rows(slide, items, top=2.25, gap=1.18, x=0.85, wide=11.4, fill=NAVY):
    """Numbered hex + bold head + body. The deck's workhorse layout."""
    y = top
    for i, (head, body) in enumerate(items, 1):
        hexagon(slide, x, y - 0.04, 0.62, str(i), fill=fill)
        text(slide, x + 0.92, y, wide - 0.92, 0.4, head, size=19, bold=True, color=NAVY)
        text(slide, x + 0.92, y + 0.38, wide - 0.92, 0.7, body, size=14.5,
             color=MUTED, line=1.25)
        y += gap


def picture(slide, name, top=2.05, bottom=6.60, max_w=11.3):
    """Scale a figure to fit its band and centre it.

    Setting width alone is what pushed three charts off the bottom of the slide
    and over the Georgia Tech logo: these figures run 1.7-2.1 in aspect, so a
    10.5 in width is 5-6 in tall against about 4.5 in of usable height. Fit to
    whichever dimension binds, then centre what is left over.
    """
    from PIL import Image
    path = FIG / name
    iw, ih = Image.open(path).size
    avail_h = bottom - top
    w = min(max_w, avail_h * iw / ih)
    h = w * ih / iw
    return slide.shapes.add_picture(str(path), Inches((W - w) / 2),
                                    Inches(top + (avail_h - h) / 2), Inches(w))


def cue(slide, label, detail):
    """A footage marker: what to play here, sized to be obvious while filming."""
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.4),
                                 Inches(2.9), Inches(8.5), Inches(2.1))
    box.fill.solid(); box.fill.fore_color.rgb = PALE
    box.line.color.rgb = OLDGOLD; box.line.width = Pt(1.5)
    box.shadow.inherit = False
    box.text_frame.text = ""
    text(slide, 2.9, 3.35, 7.5, 0.6, label, size=24, bold=True, color=NAVY,
         align=PP_ALIGN.CENTER)
    text(slide, 2.9, 4.05, 7.5, 0.8, detail, size=14, color=MUTED,
         align=PP_ALIGN.CENTER, line=1.25)


def notes(slide, s):
    slide.notes_slide.notes_text_frame.text = s.strip()


# =============================================================================
# 1 — title
# =============================================================================
s = new_slide(TITLE_TT, dark=True)
text(s, 0.85, 2.45, 11.5, 1.2, "Covariate", size=60, bold=True, color=WHITE)
text(s, 0.85, 3.65, 11.5, 0.6, "recording the room, so experiments reproduce",
     size=22, color=GOLD)
text(s, 0.85, 4.85, 11.5, 1.0, [
    ("CS-7470  Mobile & Ubiquitous Computing  ·  Team 42", {"size": 15}),
    ("Caitlin Everett  ·  Christopher Kimberley", {"size": 15}),
], color=RGBColor(0xC8, 0xD2, 0xDC))
notes(s, """
[CUE — open on the phone lying flat on a quiet kitchen counter, hold 3 seconds]

This is a quiet room. Nothing is happening in it.

Except the refrigerator cycled twice, someone closed a door down the hall, and the
floor is still ringing from a truck outside. None of that gets written down. If an
experiment ran on this bench today and failed to reproduce tomorrow, none of it
would be in the notebook either.

Covariate is a phone app that records the room, so that when an experiment doesn't
reproduce, there is something to look at.
""")

# =============================================================================
# 2 — the idea
# =============================================================================
s = new_slide()
title(s, "The idea", "why this belongs in a ubiquitous-computing course")
text(s, 0.85, 1.95, 11.4, 0.9, [
    ("Ubicomp asks what the sensors say about the person.", {"size": 19, "color": MUTED}),
    ("We asked what they say about the room — and whether that is worth writing down.",
     {"size": 19, "bold": True, "color": NAVY}),
], space=4)
hex_rows(s, [
    ("The deployment problem is already solved.",
     "Weiser's calm technology arrived as a phone in every pocket. The hard part is no longer "
     "getting a sensor into the room — it is deciding what to do with the one already there."),
    ("Context-awareness, pointed the other way.",
     "Activity recognition senses a person to serve that person. Here the sensing serves a "
     "record — an experiment that has to survive being repeated by somebody else, later."),
    ("The hack is a derived channel.",
     "Gravity is a large constant; a door closing is a rounding error beside it. Subtract the "
     "constant and the same sensor gains two orders of magnitude — no new hardware."),
], top=3.30, gap=1.28)
notes(s, """
Why this belongs in a mobile and ubiquitous computing course rather than a
statistics one.

Ubicomp usually asks what the sensors can tell you about the person holding them.
We asked what they can tell you about the room — and whether that's worth writing
down.

Three reasons that's interesting here. First, the deployment problem is already
solved. Weiser's calm technology arrived as a phone in every pocket, so the hard
part is no longer getting a sensor into the room — it's deciding what to do with
the one that is already there.

Second, it points context-awareness the other way. Activity recognition senses a
person in order to serve that person. Here the sensing serves a record — an
experiment that has to survive being repeated by somebody else, somewhere else,
later.

And third, the hack is a derived channel. Gravity is a large constant, and a door
closing is a rounding error beside it. Subtract the constant and the same sensor
gains two orders of magnitude. No new hardware — just a different question asked
of the same samples.
""")

# =============================================================================
# 3 — the plan
# =============================================================================
s = new_slide()
title(s, "The plan", "three parts, and one constraint we chose on purpose")
rows = [
    ("Build", "an ambient-context recorder: pressure, motion, magnetic field, light and sound "
              "level on one clock, exported as a file bound to a named experiment"),
    ("Reproduce", "two known sensing techniques on commodity hardware, and see what survives "
                  "the move off instrument-grade sensors"),
    ("Evaluate", "whether any of it is trustworthy — sampling health, agreement between "
                 "devices, and whether a logged covariate explains variation between runs"),
]
y = 2.35
for i, (head, body) in enumerate(rows):
    hexagon(s, 0.85, y - 0.05, 0.66, head[0], fill=[NAVY, TEAL, OLDGOLD][i])
    text(s, 1.85, y, 10.4, 0.4, head, size=21, bold=True, color=NAVY)
    text(s, 1.85, y + 0.42, 10.4, 0.7, body, size=15, color=MUTED, line=1.25)
    y += 1.30
text(s, 0.85, 6.30, 11.4, 0.8, [
    ("Constraint, chosen deliberately:  no special hardware.", {"size": 17, "bold": True, "color": NAVY}),
    ("A phone every lab already owns, or it doesn't get used.", {"size": 15, "color": MUTED}),
], space=3)
notes(s, """
The plan had three parts.

Build an ambient-context recorder — pressure, motion, magnetic field, light and
sound level, on one clock, exported as a file bound to a named experiment.

Reproduce two known sensing techniques on commodity hardware, and see what
survives the move off instrument-grade sensors.

And evaluate whether any of it is trustworthy: sampling health, agreement between
devices, and whether a logged covariate actually explains variation between runs.

The constraint was chosen deliberately — no special hardware. A phone every lab
already owns, or it doesn't get used.
""")

# =============================================================================
# 4 — what we built
# =============================================================================
s = new_slide()
title(s, "What we built", "React Native under Expo Go — a teammate joins by scanning a QR code")
layers = [
    (NAVY, "1", "Direct sensors", "expo-sensors",
     "accelerometer 50 Hz  ·  magnetometer 25 Hz  ·  barometer"),
    (NAVY, "2", "Native modules", "Swift on iOS, Kotlin on Android",
     "camera-EXIF light  ·  microphone LEVEL only — audio is never recorded"),
    (TEAL, "3", "Derived channel", "computed from the raw stream",
     "vibration: gravity removed, RMS + peak over a 200 ms window"),
    (OLDGOLD, "4", "Session record", "one session, one JSON file",
     "metadata  ·  per-channel sampling health  ·  every sample on one clock"),
]
y = 2.42
for col, num, name, how, what in layers:
    hexagon(s, 0.85, y - 0.02, 0.56, num, fill=col, size=13)
    text(s, 1.66, y, 3.3, 0.35, name, size=18, bold=True, color=NAVY)
    text(s, 5.05, y + 0.04, 7.2, 0.35, how, size=13.5, color=DEEPGOLD, bold=True)
    text(s, 1.66, y + 0.42, 10.6, 0.35, what, size=14, color=MUTED)
    y += 1.06
notes(s, """
[CUE — this is where the app screen recording goes; talk over it]

It's React Native running under Expo Go, so a teammate joins by scanning a QR
code. No install, no provisioning profile. That matters, because the whole premise
is a device every lab already has.

Four kinds of channel. Direct sensors come straight from Expo — accelerometer at
fifty hertz, magnetometer at twenty-five, barometer event-driven.

Light and sound level are native modules we wrote ourselves: Swift on iOS, Kotlin
on Android, because Expo doesn't expose them. Sound is stored as a level in
decibels — no audio is ever recorded, so there is no waveform to draw and we don't
draw one.

Then the derived channel — vibration — computed from the raw accelerometer stream.
I'll come back to that one.

And every session is one JSON file: metadata, a per-channel sampling-health
record, and every sample on a shared clock.

Every session also carries a placement — where the phone physically sat. That's
required, because the same event recorded on a benchtop and on the floor below it
differ by more than doubling the force that caused it.
""")

# =============================================================================
# 5 — channels
# =============================================================================
s = new_slide()
title(s, "Channels", "seven, of which two are ours rather than the platform’s")
cols = [("channel", 0.85), ("values", 4.15), ("units", 7.25), ("rate", 9.05)]
for name, x in cols:
    text(s, x, 2.15, 3.2, 0.3, name, size=12.5, color=MUTED)
rows = [
    ("accelerometer", "[x, y, z]", "g", "50 Hz", NAVY),
    ("magnetometer", "[x, y, z]", "µT", "25 Hz", NAVY),
    ("barometer", "[pressure, rel. altitude]", "hPa, m", "event-driven", NAVY),
    ("vibration", "[rms, peak]", "g", "5 Hz  ·  derived", TEAL),
    ("light", "[brightness]", "EV", "5 Hz  ·  dev build", DEEPGOLD),
    ("micLevel", "[rms]", "dBFS", "10 Hz  ·  dev build", DEEPGOLD),
    ("sync", "[pulse, of]", "—", "on demand  ·  fiducial", TEAL),
]
y = 2.62
for ch, vals, units, rate, col in rows:
    text(s, 0.85, y, 3.2, 0.32, ch, size=15.5, bold=True, color=col)
    text(s, 4.15, y, 3.0, 0.32, vals, size=14, color=MUTED)
    text(s, 7.25, y, 1.7, 0.32, units, size=14, color=MUTED)
    text(s, 9.05, y, 3.5, 0.32, rate, size=14, color=MUTED)
    y += 0.55
text(s, 0.85, 6.62, 11.0, 0.4,
     "Sound is a level, never a waveform — there is no audio to draw one from.",
     size=15, color=NAVY, bold=True)
notes(s, """
The seven channels, with their units and rates.

Two of them — light and microphone level — say "dev build". Those are the native
modules, and they only run in a compiled dev client, not in Expo Go. The app
reports that honestly rather than pretending.

Vibration is marked derived, and sync is the alignment fiducial. Both are ours
rather than the platform's.

And the line at the bottom is a design rule, not a caption: sound is a level,
never a waveform, because there is no audio to draw one from. Drawing a squiggle
would misrepresent the privacy guarantee.
""")

# =============================================================================
# 6 — the sync fiducial (video cue)
# =============================================================================
s = new_slide()
title(s, "Mark sync", "the alignment marker is physical on purpose")
cue(s, "▶  App screen recording — press Mark sync",
    "three haptic pulses, one second apart · record it WITH audio, "
    "then the export and the JSON meta / health blocks")
text(s, 1.2, 5.6, 11.0, 1.1,
     "Session time is monotonic from each device's own recording start, so two phones share "
     "no clock. A button that only wrote a timestamp would align nothing — driving the "
     "vibration motor makes an event every phone on the surface hears through its own "
     "accelerometer.", size=15, color=MUTED, line=1.25)
notes(s, """
[CUE — play the Mark sync clip, with sound. Three buzzes, one second apart.]

Mark sync fires three haptic pulses a second apart and writes each one into the
record as it fires.

It's physical on purpose. Session time is monotonic from each phone's own
recording start, so two devices share no clock at all — an offset of tens of
seconds between two files is normal and means nothing. A button that only wrote a
timestamp would align nothing.

Driving the vibration motor makes an event that every phone on the same surface
hears through its own accelerometer. One device gets ground truth about when it
fired; the others get a signal to cross-correlate against.

The one-second spacing is load-bearing, and I'll show you why in a minute.
""")

# =============================================================================
# 7 — privacy
# =============================================================================
s = new_slide()
title(s, "Built in, not promised", "privacy properties that are structural, not policy")
items = [
    "Audio is never recorded. The microphone channel stores a level in dBFS.",
    "Reference video is audio-free by construction — the flag is invariantly false.",
    "Location, if enabled at all, is a reverse-geocoded region and an altitude.\nNever coordinates. Absent by default.",
    "Recording is session-scoped and user-initiated. There is no background collection.",
]
y = 2.35
for t in items:
    hexagon(s, 0.85, y - 0.02, 0.42, "✓", fill=TEAL, size=13)
    text(s, 1.55, y, 10.8, 0.7, t, size=15.5, color=MUTED, line=1.25)
    y += 0.92
text(s, 0.85, 6.15, 11.4, 0.9, [
    ("Longitudinal ambient data is still data about a household.",
     {"size": 17, "bold": True, "color": NAVY}),
    ("Occupancy, routine, device fingerprint, floor of a building — the report says so.",
     {"size": 14.5, "color": MUTED}),
], space=3)
notes(s, """
Four privacy properties that are structural rather than promised.

Audio is never recorded — the microphone channel stores a level. Reference video
is audio-free by construction; the flag is invariantly false. Location, if it's
enabled at all, is a reverse-geocoded region and an altitude, never coordinates,
and it's absent by default. And recording is session-scoped and user-initiated —
there is no background collection.

But the honest line is the one at the bottom. Our proposal originally said this
data holds no personal content, and we retract that. A longitudinal ambient record
is data about a household. Vibration and light reveal occupancy and routine;
per-device sensor bias is a fingerprint; absolute pressure implies a floor of a
building. The report says all of that, along with what we do about it.
""")

# =============================================================================
# 8 — what changed
# =============================================================================
s = new_slide()
title(s, "What changed", "a scoping decision, a demotion, and a freeze")
hex_rows(s, [
    ("Two of five channels need a compiled dev client.",
     "Light and sound level are native modules, so they don't run in Expo Go. We scoped the "
     "study to the channels that install by scanning a QR code — and treat that friction as a "
     "finding, not an inconvenience."),
    ("Three sites with one participant each can't support a variance claim.",
     "Person, city, phone model and building are fully confounded. The multi-site study is now "
     "explicitly a case study; the quantitative claims moved to a within-site design with "
     "enough trials to carry them."),
    ("We pre-registered.",
     "Metrics, windows, exclusion rules and trial counts are frozen in the repository, dated, "
     "before the data existed."),
], top=2.35, gap=1.42, fill=OLDGOLD)
notes(s, """
Three things changed.

First, a scoping decision we'd make again. Two of our five channels — light and
sound level — are native modules, so they only run in a compiled dev client, not
in Expo Go. Getting a second site recording through that extra build step was
friction we chose not to spend the schedule on, so we dropped the Alka-Seltzer
dissolution study and ran a door experiment that needs only what installs by
scanning a QR code.

That's worth naming as a finding rather than an inconvenience. The gap between
"works on my device" and "runs at another site" is exactly the constraint mobile
and ubiquitous systems live inside, and we spent a week of the schedule learning
it firsthand.

Second, our reviewer pointed out that three sites with one participant each can't
support a claim about between-site variance — person, city, phone model and
building are completely confounded. So the multi-site study is now explicitly a
case study, and the quantitative claims moved to a within-site design with enough
trials to carry them.

Third, we pre-registered. Metrics, windows, exclusion rules and trial counts are
frozen in the repository, dated, before the data existed.
""")

# =============================================================================
# 9 — the pilot (video cue)
# =============================================================================
s = new_slide()
title(s, "The pilot", "two baselines, two normal door closes, two slams — one phone, one room")
cue(s, "▶  Door experiment footage",
    "Christopher Kimberley's recording, Toronto · 10–15 seconds")
text(s, 1.2, 5.6, 11.0, 0.8,
     "Six sessions on an iPhone X. Every session labelled, exported, and handed over as JSON — "
     "which is what made the reanalysis on the next three slides possible at all.",
     size=15, color=MUTED, line=1.25)
notes(s, """
[CUE — play Chris's door-experiment footage, 10 to 15 seconds]

The pilot was run by Christopher Kimberley in Toronto: two baselines, two normal
door closes, two hard slams. One phone, one room, six sessions on an iPhone X.

Everything on the next three slides comes out of those six files. That's worth
noting on its own — the export format did its job. Somebody else's recordings, in
another city, reanalysed from scratch without asking him a single question.
""")

# =============================================================================
# 10 — the hack (fig2)
# =============================================================================
s = new_slide()
title(s, "The hack", "a derived channel outperforms the raw sensor it is derived from")
picture(s, "deck_fig2_derived_vs_raw.png")
notes(s, """
Here's the derived channel, on a real slam.

The top trace is raw accelerometer magnitude. It peaks at 1.011 g — one percent
above gravity — because gravity is a constant one g sitting on top of everything
and the event is a rounding error next to it.

The bottom trace is the same sensor and the same samples, with a low-pass estimate
of gravity subtracted out. Twenty-eight times the noise floor.

Across the four door events the derived channel beats the raw sensor it comes from
by three-and-a-half to five times in signal-to-noise. That's the hack: subtracting
a large constant is what lets a small transient be seen at all.
""")

# =============================================================================
# 11 — metric choice (fig1)
# =============================================================================
s = new_slide()
title(s, "The statistic changes the margin", "same four events, measured three ways")
picture(s, "deck_fig1_metric_choice.png")
notes(s, """
Then a result about our own analysis.

These are the same four events measured three ways. The statistic the original
write-up used is a two-hundred-millisecond window average — and a
fifty-millisecond door impact gets diluted by wherever that window boundary
happens to fall.

All three orderings are correct. But the window average leaves a 1.4-times margin
between close and slam, where the energy integral leaves 2.7. Margin is what
survives more trials.

And with two trials per condition, none of it is significant — it could not have
been. The smallest p-value an exact permutation test can return at n equals two is
0.167. The design could not have reached significance on any data at all.

That's now a rule in the protocol: six trials per condition, minimum.
""")

# =============================================================================
# 12 — fiducial (fig3)
# =============================================================================
s = new_slide()
title(s, "The taps were never lost", "a reporting artifact, not a data-quality failure")
picture(s, "deck_fig3_fiducial.png")
notes(s, """
One more, and this is the one I'd want a reviewer to see.

The pilot write-up concluded that only one of three sync taps had been recorded —
flagged as a data-quality problem.

They were all there. Three raps inside a few hundred milliseconds fall into one or
two windows of the five-hertz derived channel, which is where we looked. The
fifty-hertz raw accelerometer had them the whole time.

A reporting artifact, not a data failure — and exactly the kind of thing that gets
written into a paper if nobody re-runs the analysis. It's also why the in-app sync
marker spaces its pulses a full second apart.
""")

# =============================================================================
# 13 — blind detection (terminal cue)
# =============================================================================
s = new_slide()
title(s, "Detection without labels", "the detector never sees the truth log")
cue(s, "▶  Terminal — detect_events()",
    "18pt minimum · run it live on Chris's six files")
text(s, 1.2, 5.5, 11.0, 1.2, [
    ("Finds all four door events at the operator's noted times. Nothing in one baseline. "
     "One marginal candidate in the other, at 2.1× the floor — a real unnoticed event, or a "
     "false positive at our threshold. We report it either way.", {"size": 15, "color": MUTED}),
], line=1.25)
notes(s, """
[CUE — terminal, run the blind detection live]

Last result, and it's the one that changes what we're allowed to claim.

Everything before this has the same shape: we caused an event, then we found it.
That demonstrates sensitivity and nothing about field performance, because the
analyst always knew where to look.

So: the detector gets no labels. It sets its own threshold from each recording's
quiet background and returns candidate events.

It finds all four door events, at the times Chris wrote down. It finds nothing in
one baseline — correctly. And it returns one marginal candidate in the other, at
about twice the noise floor, which is either a real event nobody noticed or a
false positive at our threshold. We report it either way.
""")

# =============================================================================
# 14 — limitations
# =============================================================================
s = new_slide()
title(s, "What this is — and isn't", "a feasibility study that succeeds as one")
text(s, 0.85, 2.15, 5.4, 0.35, "A FEASIBILITY STUDY", size=15, bold=True, color=TEAL)
for i, t in enumerate(["Detects a real event at 13–109× its\nnoise floor",
                       "Repeatable to ~1% within a condition",
                       "Instrument characterised — warm-up,\ndrift, sampling health",
                       "A derived channel beats its raw\nsensor, 3–5×"]):
    text(s, 0.85, 2.74 + i * 0.80, 0.3, 0.3, "✓", size=14, bold=True, color=TEAL)
    text(s, 1.30, 2.74 + i * 0.80, 4.6, 0.7, t, size=14, color=MUTED, line=1.25)

text(s, 7.05, 2.15, 5.3, 0.35, "NOT A GENERALISATION", size=15, bold=True, color=DEEPGOLD)
for i, t in enumerate(["One participant per site — person, city,\nphone and building are confounded",
                       "One operator, one room, one device family",
                       "Light and sound level untested — dev build",
                       "Cross-device agreement: one pair, one site"]):
    text(s, 7.05, 2.74 + i * 0.80, 0.3, 0.3, "—", size=14, bold=True, color=DEEPGOLD)
    text(s, 7.50, 2.74 + i * 0.80, 4.6, 0.7, t, size=14, color=MUTED, line=1.25)

text(s, 0.85, 5.75, 11.4, 1.2,
     "Our reviewer said it first: three sites with one participant each cannot show that a "
     "logged covariate reduces between-site variance. They were right — so the quantitative "
     "claims moved to a within-site design, and the multi-site work stays a case study.",
     size=15, color=NAVY, line=1.3)
notes(s, """
What this work is, and what it isn't.

On the left, what it can claim. It's a feasibility study, and it succeeds as one:
a commodity phone detects a real physical event at thirteen to a hundred and nine
times its own noise floor, repeatably to about one percent within a condition. We
characterised the instrument itself — warm-up, drift, sampling health. And the
derived channel beats the raw sensor it comes from.

On the right, what it can't. One participant per site, so person, city, phone
model and building are all confounded. One operator, one room, one device family.
Light and sound level untested, because they need a dev build. Cross-device
agreement has one pair of devices behind it, at one site.

Our reviewer said it first: three sites with one participant each cannot show that
a logged covariate reduces between-site variance. They were right — so we moved
the quantitative claims to a within-site design and left the multi-site work as
what it is, a case study.
""")

# =============================================================================
# 15 — what we learned / the pendulum
# =============================================================================
s = new_slide()
title(s, "'Hard' isn't a measurement", "two trials labelled slam differed by nearly 4×")
picture(s, "deck_fig4_pendulum_design.png")
notes(s, """
[CUE — cut in the pendulum footage here: wide shot, then the close on the release]

The biggest lesson came from the slams. Two trials both labelled "slam" differed
by nearly a factor of four — comparable to the gap between slamming and closing.
"Hard" isn't a measurement, it's a mood, and we'd built a study on top of one.

So the disturbance gets a number. A fixed mass on a fixed string, released from
marked angles. Impact energy is m g L times one minus cosine theta — exact, and
five angles span a twenty-two-fold range.

Six trials at each of five levels, in randomised order. Six, because at two trials
per condition an exact test cannot return a p-value below 0.167.

What you're watching is a demonstration take — I'm talking next to the phone,
which our own frozen protocol excludes. The dataset run happens this week, in an
empty room.
""")

# =============================================================================
# 16 — queued
# =============================================================================
s = new_slide()
title(s, "Queued this week", "what turns a feasibility read into a result")
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
y = 2.30
for i, (head, what, why) in enumerate(items, 1):
    hexagon(s, 0.85, y - 0.02, 0.52, str(i), fill=TEAL, size=13)
    text(s, 1.66, y, 10.6, 0.32, head, size=18, bold=True, color=NAVY)
    text(s, 1.66, y + 0.36, 10.6, 0.32, what, size=14, color=MUTED)
    text(s, 1.66, y + 0.70, 10.6, 0.32, why, size=14, color=TEAL,
         bold=False)
    y += 1.16
notes(s, """
What's queued for the rest of the week.

The pendulum dose ladder — five levels, six trials each, randomised order, empty
room. That's the confirmatory spine; everything quantitative rests on it.

Overnight ambient runs, eight hours or more, three nights. That's aimed at the
refrigerator duty cycle — a compressor cycling every half hour is precisely the
invisible variable we're arguing about, and nobody in the room notices it.

A blind detection trial: four hours of ordinary activity with the log sealed
before the analysis runs.

And a twelve-hour barometer run checked against a National Weather Service
station. That's the only channel we can validate against anything outside our own
project — and the residual offset should imply our own altitude, which we can
check against the known elevation of the room.
""")

# =============================================================================
# 17 — contributions
# =============================================================================
s = new_slide(dark=True)
title(s, "Contributions", "who did what", dark=True)
for i, (initials, name, role) in enumerate([
        ("CK", "Christopher Kimberley",
         "the door-slam pilot — protocol, recording, and the six sessions"),
        ("CE", "Caitlin Everett",
         "the recorder, the export schema, the analysis, and the study design")]):
    yy = 3.05 + i * 1.60
    hexagon(s, 0.85, yy - 0.04, 0.68, initials, fill=GOLD, fg=NAVY, size=15)
    text(s, 1.90, yy, 10.5, 0.4, name, size=22, bold=True, color=WHITE)
    text(s, 1.90, yy + 0.52, 10.5, 0.5, role, size=16,
         color=RGBColor(0xC8, 0xD2, 0xDC))
notes(s, """
Who did what. The door-slam pilot — the protocol, the recording, and the six
sessions — is Christopher Kimberley's. The recorder, the export schema, the
analysis and the study design are mine.
""")

# =============================================================================
# 18 — close
# =============================================================================
s = new_slide(dark=True)
text(s, 0.85, 2.80, 11.5, 2.6, [
    ("We're building a tool to record what nobody wrote down.",
     {"size": 32, "bold": True, "color": WHITE, "space": 20}),
    ("Every session in our own pilot is labelled “controlled” — including both slams.",
     {"size": 23, "color": GOLD, "space": 20}),
    ("The app let us mislabel the entire dataset without a word. That's a finding about "
     "the product, and it's in the report.",
     {"size": 17, "color": RGBColor(0xC8, 0xD2, 0xDC)}),
], line=1.25)
notes(s, """
And the one that stung.

All six of those pilot sessions are labelled "controlled" — including both slams.
Our own app let us mislabel the entire dataset without a word of complaint.

We're building a tool to record what nobody wrote down, and it let us not write
something down. That's a real finding about the product, and it's in the report.

[CUE — cut back to the opening frame: the phone on the quiet counter. Hold two
seconds, then out.]
""")

prs.save(OUT)
print(f"wrote {OUT} — {len(prs.slides.__iter__.__self__._sldIdLst)} slides")
