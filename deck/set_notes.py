"""Speaker notes and the time budget, keyed to the video grading rubric.

Written flat and declarative — short sentences, no rhetorical transitions, no
throat-clearing. They are read aloud by someone short on time who wants the point
to land, so the affect has to carry the argument rather than decorate it. Detail a
listener needs to follow the narrative stays; anything that only signals effort is
gone.

The narrative arc, which the slide order now follows:
  phones are cheap and experiments fail  ->  so we built a recorder  ->  here is
  the simplest experiment that could test it  ->  here is what we learned,
  including how hard the designing was  ->  it was not a wash  ->  what we believe
  right now  ->  what we would build with more time  ->  come help.

The rubric caps length at 8 minutes and calls the maximum strict, so every slide
carries a second budget and the total is asserted at the bottom — the build fails
rather than quietly running long.

`LEAN= python3 build_deck.py` writes the full version, with the cut slides, for
the written report.
"""
import re
import sys

from pptx import Presentation

DECK = "Covariate_Demo.pptx"

NOTES = {

1: """≈12s  ·  OPEN

Covariate. CS-7470, Team 42 — Caitlin Everett and Christopher Kimberley.

Phones are cheap, most of us already carry one, and a lot of experiments don't
reproduce. So we wanted to know whether the sensors already inside an ordinary
phone are good enough to record the conditions an experiment ran under.

To be clear: we are not using the phone to run experiments. It records the
conditions in the room while an experiment happens.
""",

# -- the short version --------------------------------------------------------
2: """≈13s  ·  SHORT VERSION — 1 of 3: WHAT WE DID

We built an app in Expo Go, and added two native sensors Expo Go doesn't ship with.
Then we designed about the simplest experiment there is: close a door 24 times,
gently and then hard, with two phones on the table recording six channels at once.

The interesting channel isn't sensed. It's computed. An accelerometer at rest reads
one g, not zero, because gravity is always in the number. A door close is about one
percent on top of that. So we estimate gravity, subtract it, and measure what's
left.
""",

3: """≈9s  ·  SHORT VERSION — 2 of 3: IT WORKED

It separated cleanly. Every hard close produced a larger peak than every gentle one,
with no overlap. On the microphone, hard closes peaked 12.3 decibels higher. On the
derived vibration channel, 2.6 times higher, in g.

Both channels. Both phones. Same answer.
""",

4: """≈9s  ·  SHORT VERSION — 3 of 3: WHAT'S LEFT

The two phones disagree about absolute values — pressure, loudness, magnetic field.
So we report change within a session, not absolutes.

One channel returned nothing for eight minutes while the app called it healthy. And
we have only tested a few devices.

Promising, bounded, unfinished.
""",

# -- section 1 · AIMS AND OBJECTIVES -----------------------------------------
5: """≈3s  ·  DIVIDER

"Aims and objectives."
""",

6: """≈11s  ·  WHY RECORD THE ROOM — 1 of 3

Two people run the same written protocol and get different answers. The difference
usually isn't in the protocol. It's in everything around it that nobody wrote down.

Some labs do record it, because they have to. Accredited labs run validated
monitoring systems. Everyone without a compliance budget records nothing.
""",

7: """≈10s  ·  + THE EDGE EFFECT — 2 of 3

Cells cultured in the outer wells of a 96-well plate read up to 35% lower than the
wells in the middle. Same cells, same protocol, same plate.

The cause is evaporation and a temperature gradient across the room. Not a technique
problem. A room problem, and a thermometer would have caught it.
""",

8: """≈11s  ·  + THE ISOS CONSENSUS — 3 of 3

Perovskite solar cell results weren't comparable between labs, because everyone
tested under different ambient conditions and reported different parameters. So the
field wrote a consensus statement, in Nature Energy, agreeing on what has to be
recorded: temperature, humidity, illumination, atmosphere, electrical bias.

The fix wasn't a better measurement. It was deciding which conditions go in the
record.
""",

9: """≈15s  ·  AIMS AND OBJECTIVES

Three objectives, as we proposed them.

BUILD an ambient-context recorder — pressure, motion, magnetic field, light and
sound level, all on one clock, exported as a file bound to a named experiment.

REPRODUCE two known sensing techniques on commodity hardware.

EVALUATE whether any of it is trustworthy.

One constraint: no additional hardware. It runs on a phone a lab already owns, or
nobody uses it.
""",

# -- section 2 · PROJECT PRESENTATION ----------------------------------------
10: """≈3s  ·  DIVIDER

"Project presentation."
""",

11: """≈18s  ·  IMPLEMENTATION

React Native. One TypeScript codebase, real native views on both platforms.

Expo Go is the part that matters. It's a pre-built container app you install free
from the App Store, point at a QR code, and it runs your JavaScript — no Xcode, no
developer account, no cable. But it ships a fixed set of native modules, and your
code can only reach hardware inside that set.

Accelerometer, magnetometer and barometer are in it. Vibration we derive from the
accelerometer in JavaScript, so that's free too.

Microphone level isn't in it. Ambient light on iOS isn't either — Apple exposes no
general-purpose light sensor to apps, so ours goes through camera exposure metadata.
Both meant writing Swift and Kotlin, and that means a compiled build.

Four channels install in thirty seconds. All six need a toolchain.
""",

12: """≈6s  ·  IN USE — 1 of 4: DESIGNED

Before any of it existed, this was the specification. An ASCII mockup of the
recording screen, with sampling health on screen rather than buried in the export.
""",

13: """≈8s  ·  IN USE — 2 of 4: BUILT

The real thing. This is the sensor check: every module the device actually offers,
its rate, its current reading. All six present.

There's also a calibrate step — twenty seconds at rest — that measures each
channel's own bias and noise. None of this traces to a standard, so knowing your own
noise floor is the substitute.
""",

14: """≈7s  ·  IN USE — 3 of 4: RECORDING

Six seconds into a session. Six channels live on one clock, each showing its running
sample count and realised rate.

Two weeks ago this was four channels and a note saying the other two needed a build
we hadn't done.
""",

15: """≈6s  ·  IN USE — 4 of 4: EXPORTED

Stop and export. One session, one JSON file, 182 kilobytes. It leaves through the
normal share sheet — no account, no server. The file is the deliverable.
""",

16: """≈14s  ·  WHY THIS IS HARD

Consumer sensors have documented failure modes, which is why this is a study rather
than a product announcement.

The raw stream isn't raw — factory calibration is baked into firmware, so you're
reading a vendor-conditioned number. A MEMS sensor drifts measurably in its first
few minutes from self-heating alone, so a phone logging continuously starts by
measuring itself. Identical units differ in thermal drift, so no generic correction
exists. Auto-exposure and automatic gain control sit between the world and the
number.

And there's no calibration chain back to a national standard. Relative change within
a session. Never an absolute.
""",

# -- section 3 · CHANGES TO THE PLAN -----------------------------------------
17: """≈3s  ·  DIVIDER

"Changes to the plan."
""",

18: """≈19s  ·  CHANGES SINCE THE PROPOSAL

Four, and each was forced by something we hit.

We proposed an Alka-Seltzer dissolution study and it was basically approved. It
needed light and sound level. Both are native modules, and Expo Go can't load them.
So we swapped to door closes — an event the four Expo Go channels can actually see.

Then the dev client built and all six came back. A dropped feature turned into a
measured result about deployment.

Third, the multi-site study became a case study. Our TA pointed out that three sites
with one person each confound person, city, phone and building. That was correct.

Fourth, the one we didn't plan. We started measuring the instrument instead of the
room.
""",

# -- section 4 · RESULTS -----------------------------------------------------
19: """≈3s  ·  DIVIDER

"Results."
""",

20: """≈14s  ·  THE EXPERIMENT, LINE BY LINE

The card is the protocol as actually run.

Two factors: the dehumidifier off or on, and the door doing nothing, a normal close,
or a slam. Six trials of each. The door trials are the measurement. The dehumidifier
is the ambient condition nobody writes in a methods section.

One continuous recording instead of six sessions, so every cell lands on the same
clock and the same thermal state.
""",

21: """≈18s  ·  PILOT STUDY   [16 s clip auto-plays]

The clip starts by itself.

First half is Chris's pilot in Toronto — two baselines, two normal closes, two slams,
on an iPhone X. The blue marker on the door edge is his repeatability control: the
same closed position every trial.

Second half is the same action in Chicago, eight weeks later, on different hardware,
in a different building. That half runs at about 80 times real speed.

Six sessions, exported as JSON. Every result after this came from those files alone,
in a different city, with no further input from the person who recorded them.
""",

22: """≈18s  ·  WHAT THE INSTRUMENT MEASURED

Twenty-four door trials. Two devices, one table, the same ten minutes.

Twelve normal closes, twelve slams. On the acoustic channel the slams peaked 12.3
decibels higher. On the derived vibration channel, 2.6 times higher.

The average isn't the point. The overlap is, and there isn't any. Not one normal
close reached the level of any slam, on either channel, on either device. That puts
the smallest attainable p at one in two and a half million.

And it replicated. The second device gave 2.77 against our 2.60. Different hardware,
same conclusion, same ten minutes.
""",

23: """≈17s  ·  TWO PHONES, ONE TABLE

The same 24 events, two devices, two opposite findings.

They agree about change. Pearson r of 0.97 on both channels, against a threshold we
set at 0.90 before collecting anything, with event timing matched to 33 milliseconds
and no sync marker.

That contradicted our own prediction. On synthetic data the derived channel failed
cross-device agreement at 0.857. On real data it matched the raw channel.

They disagree about everything absolute. Same table, same second: barometers 0.675
hectopascals apart, resting sound level 7.8 decibels apart, noise floors across four
devices spanning 2.4 times. One read the magnetic field at 664 microtesla and the
other at 41, because a magnet was stuck to it. No other channel noticed.
""",

# -- section 5 · REFLECTION --------------------------------------------------
24: """≈3s  ·  DIVIDER

"Reflection." Say it — this is where the marks are.
""",

25: """≈15s  ·  DESIGNING IT WAS HARDER THAN RUNNING IT

The hardest part of this project wasn't the code. It was designing an experiment
that could answer anything, in a house, on a deadline.

An exact permutation test's smallest possible p is fixed by the trial count before
any data exists. Two per condition floors at 0.167. Three at 0.05. Six at 0.001. Our
corrected bar is 0.025.

So at two or three trials the test cannot reach significance no matter what the doors
do. The pilot's problem was never that it found nothing. It couldn't have found
anything, and we didn't notice until we tried to analyse it.

The rule we took from it: when the schedule tightens, cut conditions, not replicates.
""",

26: """≈18s  ·  WHAT WE GOT WRONG

Three, and two are about our own product rather than our data.

We built an instrument that doesn't insist. Condition defaults to "controlled", and
site, notes and placement are all optional, so a session saves with none of them and
the app never asks. Every session we've recorded came out that way. Distance from
phone to door is the biggest single thing determining amplitude, and it's in none of
the files.

Nobody operated it wrong. The tool never made it easy to operate right, and that's
the first thing we're fixing.

Second, six sensors appeared to disagree with their own spec, every channel
overshooting by the same factor. Six independent sensors don't agree on an error. A
shared denominator does. Our elapsed timer was counting timer firings instead of
seconds.

Third, there's no single best channel. Sensitivity and cross-device comparability
trade against each other, and we didn't expect that.
""",

27: """≈12s  ·  EITHER OUTCOME IS USEFUL

None of that makes it a wash.

If the sensors pass, ambient context capture is free for anyone with a phone —
teaching labs, citizen science, anywhere without an instrumentation budget.

If they fail, the app is still the experiment-linked recorder, and the sensing moves
to a cheap external package over Bluetooth. That case has support: the same phone
apps, re-run with external calibrated microphones, came within a decibel of
reference.
""",

28: """≈15s  ·  MIDWAY HYPOTHESIS

What we believe right now, per channel, stated so it can be wrong.

Vibration is likely good enough — 13 to 109 times the floor. The accelerometer is
good for timing, not amplitude. The barometer isn't trusted yet: its session-long
rise looked identical in baseline and in slam, which says we measured the device
rather than the room. The magnetometer is probably not useful at this scale — the
noise is bigger than the signal.

Light samples but doesn't report. Microphone level records. And cross-device is
already returning a result we didn't expect.
""",

29: """≈15s  ·  WHAT HAPPENS NEXT

Left column is this week. Five small things: the other machine state to finish the
two-by-three, the magnet off and six more closes, a log line to find out what the
light module actually returns, an overnight run against a weather station, and a
distance ladder that finally makes Toronto and Chicago comparable.

Right column is the version worth building. Baseline every device on the market.
Every calibration run contributes a noise floor keyed to device model, so the app can
tell any phone whether it resolves the effect you declared — and refuse the ones that
can't.

First column is homework. Second is why the homework is worth doing.
""",

30: """≈7s  ·  WORKS CITED

Leave it up while you finish the previous thought.

Claude — Sonnet and Opus — was used throughout as a learning aid, coding mentor and
analysis partner. Every measurement was run by us, and every conclusion checked by
us.
""",

31: """≈8s  ·  CONTRIBUTIONS

Chris wrote the derived sensor code, designed the door-slam pilot protocol, and ran
the recording and the six test sessions.

Product and study design, the live tests, the export schema and the analysis are
mine.
""",

32: """≈11s  ·  SUMMARY

The recorder works. All six channels run.

This is a feasibility result rather than a reproducibility result — the best we could
do in a tight window.

Whether a phone is a good enough instrument is still open. Whether it's a good enough
recorder is not.

The code and the data are public. That code goes to the repository. If you want to
run this in your room, on your hardware, we'd like the data.
""",
}

# --- apply -------------------------------------------------------------------
prs = Presentation(DECK)
n = len(prs.slides._sldIdLst)
if set(NOTES) != set(range(1, n + 1)):
    sys.exit(f"notes cover {min(NOTES)}..{max(NOTES)} but the deck has {n} slides")

for i, slide in enumerate(prs.slides, 1):
    slide.notes_slide.notes_text_frame.text = NOTES[i].strip()
    slide._element.set("show", "1")

# --- budget ------------------------------------------------------------------
total = 0
for i, body in NOTES.items():
    m = re.search(r"≈(\d+)s", body)
    if not m:
        sys.exit(f"slide {i} carries no budget marker")
    total += int(m.group(1))

words = sum(len(b.split()) for b in NOTES.values())
prs.save(DECK)
print(f"{n} slides, all shown · {words} words of narration")
print(f"budget {total}s = {total // 60}:{total % 60:02d}   cap 8:00, margin {480 - total}s")
if total > 470:
    sys.exit("OVER BUDGET — trim before filming")
if total < 300:
    sys.exit("UNDER 5:00 — the rubric wants at least five minutes")
