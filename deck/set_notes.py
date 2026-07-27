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

Phones are cheap, most of us carry one, and a lot of experiments don't reproduce. To be
clear, we're not running experiments on the phone — it records the room while the
experiment happens.

""",

2: """SHORT VERSION — 1 of 3: WHAT WE DID

We designed a very simple app and a very simple experiment: two screens, and a door
opened and closed 24 times, gently then hard, two phones recording all six channels.

A door is really a sound and a shake, so the two channels that carried it were sound
level and vibration. Another experiment would lean on a different pair — an HVAC cycle
is pressure; a photostability run is light.

And vibration isn't sensed, it's computed. An accelerometer at rest reads one g, not
zero, because gravity is always in the number, and a door close is one percent on top of
that.
""",

3: """SHORT VERSION — 2 of 3: IT WORKED

Soft closes and slams separated cleanly, and it wasn't close — the quietest slam still
beat the loudest gentle close. On the microphone, 12.3 decibels louder; on vibration,
2.6 times bigger.
""",

4: """SHORT VERSION — 3 of 3: WHAT'S LEFT

The two phones disagree about absolutes, so we report change within a session. One
channel returned nothing for eight minutes while the app called it healthy. And we have
only tested a few devices.

Promising, bounded, and definitely just the start of something interesting.
""",

5: """CHRIS, RUNNING THE APP   [12 s clip auto-plays]

Chris running it, before any door has moved. Six channels reading live.
""",

6: """DIVIDER

"Aims and objectives."
""",

7: """WHY RECORD THE ROOM — 1 of 3

Two people run the same protocol and get different answers. The difference usually isn't
the protocol. It's everything around it that nobody wrote down.

""",

8: """+ THE EDGE EFFECT — 2 of 3

Cells in the outer wells of a 96-well plate read up to 35% lower than the wells in the
middle. Evaporation and a temperature gradient across the room. Not a technique problem
— a room problem.
""",

9: """+ THE ISOS CONSENSUS — 3 of 3

Perovskite solar results weren't comparable between labs. So the field wrote a consensus
statement, in Nature Energy, on what has to be recorded.

""",

10: """AIMS AND OBJECTIVES

Three objectives, on screen. Build the recorder, reproduce two known sensing techniques
on commodity hardware, and work out whether any of it can be trusted.

One constraint: no extra hardware. It runs on a phone a lab already owns, or nobody uses
it.
""",

11: """DIVIDER

"Project presentation."
""",

12: """IMPLEMENTATION

Expo Go is the part that matters. Free container app from the App Store — point it at a
QR code and it runs your JavaScript. But it ships a fixed set of native modules, and
your code can only reach those. Microphone level and iOS light are outside it, so those
meant Swift, Kotlin and a compiled build.

""",

13: """IN USE

It sits on a table while an experiment runs, works like a stopwatch, and spits out one
JSON file.

Calibrate is twenty seconds at rest, measuring each channel's own bias and noise. That
step may be what makes this usable by citizen scientists and labs on a budget.
""",

14: """WHY THIS IS HARD

We knew going in — as probably many of you have — that phone sensors have failure modes.
Here are a few, and what we wanted to know was how they land on a result.

One that surprised us: the stream isn't raw. Factory calibration is baked into firmware,
so you're reading a number the vendor already conditioned.
""",

15: """DIVIDER

"Changes to the plan."
""",

16: """CHANGES SINCE THE PROPOSAL

We had to change course a bit. We originally proposed an Alka-Seltzer study, and it was basically approved. It needed
light and sound level — both native modules, and Expo Go can't load them. So we swapped
to door closes, which the four Expo Go channels can see. Then the dev client built and
all six came back.

And the multi-site study shrank, wisely, into a single-site case study — three sites with one
person each confound too much.
""",

17: """DIVIDER

"Results."
""",

18: """THE EXPERIMENT, LINE BY LINE

We tried to follow our own protocol carefully: one continuous recording rather than six
sessions, so every cell lands on the same clock and thermal state.

A door still isn't perfect, but it exercises most of the sensors — and we understand a
lot better now how careful we have to be with consumer hardware.
""",

19: """PILOT STUDY   [16 s clip auto-plays]

Chris in Toronto on
an iPhone X, then Chicago eight weeks later on different hardware.

The blue marker on his door edge is a repeatability control: same closed position every
trial.
""",

20: """WHAT THE INSTRUMENT MEASURED

Charts in the paper. The slams came in 12.3 decibels louder on the microphone and 2.6
times bigger on vibration. But the averages matter less than the fact that nothing
overlapped — the quietest slam still beat the loudest gentle close, on both phones.

And it replicated: the second phone gave 2.77 where ours gave 2.60.
""",

21: """TWO PHONES, ONE TABLE


Two findings, pointing opposite ways.

The phones agree about change. Plot one phone's 24 events against the other's and it's
basically a straight line — a correlation of 0.97, against a bar we set at 0.90 before
collecting anything.

They flatly disagree about absolute values. Same table, same second, the barometers are
0.675 hectopascals apart — five metres of altitude between two phones lying next to each
other.

So a phone can tell you what changed, relative to itself — not what the room actually
was.
""",

22: """DIVIDER

"Reflection."
""",

23: """DESIGNING IT WAS HARDER THAN RUNNING IT

The hardest part wasn't the code, though Apple doesn't make it easy to work with its
sensors. It was designing an experiment that could answer anything, in a house, on a
deadline.

The table is why. A permutation test's smallest possible p is fixed by the trial count
before any data exists, and at two or three trials it can't clear our bar no matter
what the doors do.

So the rule we stuck to: when the schedule tightens, cut conditions, not replicates.
""",

24: """THINGS WE ARE STILL WORKING ON

Three, and two are about our own product.

The UI could guide people to better choices. Every context field is optional, so sessions
save with none of them — including distance from phone to door, which turns out to be the
biggest single thing determining how big an event looks. Nobody operated it wrong; the
tool never made it easy to.

Second, six sensors appeared to disagree with their own spec. Six independent sensors
don't agree on an error — a shared denominator does. Our timer was counting timer
firings, not seconds.
""",

25: """EITHER OUTCOME IS USEFUL

None of this makes it a wash. If the sensors pass, ambient context capture is free for
anyone with a phone. If they fail, the app is still the experiment-linked recorder and
the sensing moves to cheap external hardware over Bluetooth.
""",

26: """MIDWAY HYPOTHESIS

Channel by channel, and we'd like to be wrong about some of it. Vibration is likely good
enough: 13 to 109 times its own noise floor. The barometer we
don't trust yet — its slow rise over the session looked the same whether we were slamming
the door or standing still.
""",

27: """WHAT HAPPENS NEXT

Left column is this week.

Right column is the version worth building. Baseline every device on the market: every
calibration run contributes a noise floor keyed to device model, so the app can tell any
phone whether it resolves the effect you declared — and refuse the ones that can't.
""",

28: """WORKS CITED

Claude — Sonnet and Opus — was a learning aid, coding mentor and analysis partner
throughout. Every measurement run by us, every conclusion checked by us.
""",

29: """CONTRIBUTIONS

Chris wrote the derived sensor code, designed the pilot protocol, and ran the six test
sessions. Product and study design, the live tests, the export schema and the analysis
are mine.
""",

30: """SUMMARY

The recorder works. But this is a feasibility result, not a reproducibility result — the best we could do in a
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
