"""Speaker notes, and a runtime estimate computed from them.

Written flat and declarative — short sentences, no rhetorical transitions, no
throat-clearing. Read aloud by someone short on time who wants the point to land,
so the affect carries the argument rather than decorating it.

WHY THE LENGTH CHANGED. Earlier passes carried a hand-written `≈12s` marker per
slide and summed them. Those numbers were estimates nobody ever checked against
the words underneath, and they were wrong by a factor of three: 2,054 words
"budgeted" at 351 seconds is 351 words per minute, which is roughly twice human
speech. The real runtime was near twelve minutes against a strict eight-minute
cap. The markers are gone. Runtime is now derived from the word count at a
declared speaking rate, so it cannot drift from the text again.

WPM is set to a brisk-but-natural read. PAUSE_S is the dead air per slide
transition. Both are stated rather than assumed so the estimate can be argued
with, and CAP_S leaves margin under the rubric's 8:00.

The narrative arc, which the slide order follows:
  phones are cheap and experiments fail  ->  so we built a recorder  ->  here is
  the simplest experiment that could test it  ->  here is what we learned,
  including how hard the designing was  ->  it was not a wash  ->  what we
  believe right now  ->  what we would build with more time  ->  come help.

`LEAN= python3 build_deck.py` writes the full version, with the cut slides, for
the written report.
"""
import re
import sys

from pptx import Presentation

DECK = "Covariate_Demo.pptx"

WPM = 173        # measured against the synthesised read, not guessed
PAUSE_S = 0.7    # dead air per slide advance
CAP_S = 465      # 7:45, under the rubric's strict 8:00

NOTES = {

1: """OPEN

Covariate. CS-7470, Team 42 — Caitlin Everett and Christopher Kimberley.

Phones are cheap, most of us carry one, and a lot of experiments don't reproduce.

We're not running experiments on the phone. It records the room while an experiment
happens.
""",

2: """SHORT VERSION — 1 of 3: WHAT WE DID

We built an app in Expo Go, added two native sensors it doesn't ship with, and ran the
simplest experiment there is: close a door 24 times, gently then hard, two phones
recording.

The interesting channel isn't sensed — it's computed. An accelerometer at rest reads
one g, not zero, because gravity is always in the number, and a door close is one
percent on top. So we estimate gravity, subtract it, and measure what's left.
""",

3: """SHORT VERSION — 2 of 3: IT WORKED

It separated cleanly. Every hard close peaked higher than every gentle one, no
overlap. On the microphone, 12.3 decibels higher. On the derived vibration channel,
2.6 times higher.

Both channels. Both phones.
""",

4: """SHORT VERSION — 3 of 3: WHAT'S LEFT

The two phones disagree about absolutes, so we report change within a session. One
channel returned nothing for eight minutes while the app called it healthy. And we have
only tested a few devices.

Promising, bounded, unfinished.
""",

5: """DIVIDER

"Aims and objectives."
""",

6: """WHY RECORD THE ROOM — 1 of 3

Two people run the same protocol and get different answers. The difference usually isn't
the protocol. It's everything around it that nobody wrote down.

Accredited labs record it. Everyone without a compliance budget records nothing.
""",

7: """+ THE EDGE EFFECT — 2 of 3

Cells in the outer wells of a 96-well plate read up to 35% lower than the wells in the
middle.

Evaporation and a temperature gradient across the room. Not a technique problem — a
room problem.
""",

8: """+ THE ISOS CONSENSUS — 3 of 3

Perovskite solar results weren't comparable between labs. So the field wrote a
consensus statement, in Nature Energy, on what has to be recorded.

The fix wasn't a better measurement. It was deciding what goes in the record.
""",

9: """AIMS AND OBJECTIVES

Three objectives. Build an ambient-context recorder — six channels, one
clock, one file bound to a named experiment. Reproduce two known sensing techniques on
commodity hardware. Evaluate whether it's trustworthy.

One constraint: no extra hardware. It runs on a phone a lab already owns, or nobody uses
it.
""",

10: """DIVIDER

"Project presentation."
""",

11: """IMPLEMENTATION

React Native: one TypeScript codebase, native views on both platforms.

Expo Go is the part that matters. Free container app from the App Store — point it at a
QR code and it runs your JavaScript. But it ships a fixed set of native modules, and
your code can only reach those.

Accelerometer, magnetometer and barometer are in it, and we derive vibration from the
accelerometer. Microphone level and iOS ambient light are not — those meant Swift,
Kotlin and a compiled build. So four channels install in thirty seconds; all six need a
toolchain.
""",

12: """IN USE

The spec, the sensor check with all six modules present, a session six seconds in with
every channel on one clock, and the export — one JSON file, 182 kilobytes.

Calibrate is twenty seconds at rest, measuring each channel's own bias and noise.
""",

13: """DIVIDER

"Changes to the plan."
""",

14: """CHANGES SINCE THE PROPOSAL

Four, each forced by something we hit.

We proposed an Alka-Seltzer study and it was basically approved. It needed light and
sound level — both native modules, and Expo Go can't load them. So we swapped to door
closes, which the four Expo Go channels can see. Then the dev client built and all six
came back, turning a dropped feature into a result about deployment.

Third, the multi-site study became a case study: three sites with one person each
confound too much.

Fourth, unplanned: we started measuring the instrument, not the room.
""",

15: """DIVIDER

"Results."
""",

16: """THE EXPERIMENT, LINE BY LINE

The protocol as actually run. Two factors — dehumidifier off or on, and the door doing
nothing, a normal close, or a slam. Six trials of each.

The door trials are the measurement. The dehumidifier is the ambient condition nobody
writes in a methods section.
""",

17: """PILOT STUDY   [16 s clip auto-plays]

First half is Chris's pilot in Toronto — two baselines, two normal closes, two slams,
on an iPhone X. The blue marker on the door edge is his repeatability control.

Second half is Chicago, eight weeks later, different hardware, different building, at
about 80 times speed. Every result after this came out of those exported files.
""",

18: """WHAT THE INSTRUMENT MEASURED

On the acoustic channel the slams peaked 12.3 decibels higher; on the derived vibration
channel, 2.6 times higher.

The average isn't the point. The overlap is, and there isn't any — not one normal close
reached the level of any slam, on either device. And it replicated: the second device
gave 2.77 against our 2.60.
""",

19: """TWO PHONES, ONE TABLE

They agree about change: Pearson r of 0.97 on both channels, against a threshold set at
0.90 beforehand, with event timing matched to 33 milliseconds and no sync marker.

They disagree about everything absolute. Same table, same second: barometers 0.675
hectopascals apart. One read the magnetic field at 664 microtesla and the other at 41 —
a magnet was stuck to it.
""",

20: """DIVIDER

"Reflection."
""",

21: """DESIGNING IT WAS HARDER THAN RUNNING IT

The hardest part wasn't the code. It was designing an experiment that could answer
anything, in a house, on a deadline.

An exact permutation test's smallest possible p is fixed by the trial count before any
data exists. Two per condition floors at 0.167; six gets to 0.001, against a corrected
bar of 0.025. So at two trials the test cannot reach significance no matter what the
doors do.

The pilot couldn't have found anything, and we didn't notice until we analysed it. When
the schedule tightens, cut conditions, not replicates.
""",

22: """WHAT WE GOT WRONG

Three. Two are about our own product, not our data.

We built an instrument that doesn't insist. Every context field is optional, so
sessions save with none of them — including distance from phone to door, which is the
biggest single thing determining amplitude. Nobody operated it wrong. The tool never
made it easy to.

Second, six sensors appeared to disagree with their own spec, all overshooting by the
same factor. Six independent sensors don't agree on an error. A shared denominator
does: our timer was counting timer firings, not seconds.

""",

23: """EITHER OUTCOME IS USEFUL

None of that makes it a wash.

If the sensors pass, ambient context capture is free for anyone with a phone.

If they fail, the app is still the experiment-linked recorder and the sensing moves to
cheap external hardware over Bluetooth.
""",

24: """MIDWAY HYPOTHESIS

What we believe right now, per channel, stated so it can be wrong.

Vibration is likely good enough — 13 to 109 times the floor. The barometer isn't
trusted yet: its session-long rise looked the same in baseline and in slam, which says
we measured the device, not the room.
""",

25: """WHAT HAPPENS NEXT

Left column is this week: the other machine state, the magnet off and six more closes,
a distance ladder that makes Toronto and Chicago comparable.

Right column is the version worth building. Baseline every device on the market: every
calibration run contributes a noise floor keyed to device model, so the app can tell any
phone whether it resolves the effect you declared — and refuse the ones that can't.
""",

26: """WORKS CITED


Claude — Sonnet and Opus — was a learning aid, coding mentor and analysis partner
throughout. Every measurement run by us, every conclusion checked by us.
""",

27: """CONTRIBUTIONS

Chris wrote the derived sensor code, designed the pilot protocol, and ran the six test
sessions. Product and study design, the live tests, the export schema and the analysis
are mine.
""",

28: """SUMMARY

The recorder works. All six channels run.

This is a feasibility result, not a reproducibility result — the best we could do in a
tight window.

Whether a phone is a good enough instrument is still open. Whether it's a good enough
recorder is not.

The code and the data are public. Scan the code. If you run this in your room, we want
the data.
""",

}


def spoken(body):
    """The words actually said: no slide header, no bracketed stage cues."""
    lines = body.strip().split("\n")
    if lines and not lines[0].startswith(" "):
        lines = lines[1:]                      # the header line
    text = "\n".join(lines).strip()
    return re.sub(r"\[[^\]]*\]", "", text).strip()


# --- apply -------------------------------------------------------------------
if __name__ == "__main__":
    prs = Presentation(DECK)
    n = len(prs.slides._sldIdLst)
    if set(NOTES) != set(range(1, n + 1)):
        sys.exit(f"notes cover {min(NOTES)}..{max(NOTES)} but the deck has {n} slides")

    for i, slide in enumerate(prs.slides, 1):
        slide.notes_slide.notes_text_frame.text = NOTES[i].strip()
        slide._element.set("show", "1")
    prs.save(DECK)

    # --- runtime, derived from the words ------------------------------------
    words = sum(len(spoken(b).split()) for b in NOTES.values())
    speech = words / WPM * 60
    total = speech + PAUSE_S * n

    over = [i for i, b in NOTES.items()
            if len(spoken(b).split()) / WPM * 60 > 32]
    print(f"{n} slides, all shown · {words} spoken words at {WPM} wpm")
    print(f"runtime {int(total // 60)}:{total % 60:04.1f}  "
          f"(speech {speech:.0f}s + {PAUSE_S * n:.0f}s of slide advances)  "
          f"cap {CAP_S // 60}:{CAP_S % 60:02d}, margin {CAP_S - total:.0f}s")
    if over:
        print(f"slides over 32 s of continuous talking: {over}")
    if total > CAP_S:
        sys.exit("OVER — trim before filming")
    if total < 300:
        sys.exit("UNDER 5:00 — the rubric wants at least five minutes")
