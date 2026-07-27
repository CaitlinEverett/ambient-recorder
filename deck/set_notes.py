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

WPM = 150        # measured off the first take: 1,902 words in 13:38 is 140
PAUSE_S = 0.7    # dead air per slide advance
CAP_S = 450      # 7:30, so a slow slide doesn't spend the whole margin

NOTES = {

1: """OPEN

Hi — I'm Caitlin Everett, presenting for Group 42. My teammate is Chris Kimberley, and we
built an app called Covariate.

One question: can the sensors in an ordinary phone record the conditions a science
experiment ran under, well enough to be worth trusting?
""",

2: """SHORT VERSION — 1 of 3: WHAT WE DID

A very simple app and a very simple experiment: two screens, and a door opened and closed
24 times, gently then hard, with two phones recording all six channels.

A door is really just a sound and a shake, so the channels that carried it were sound
level and vibration. And vibration isn't sensed, it's computed — as many of you know —. An accelerometer at rest reads one g, not zero, and a door
close is one percent on top.
""",

3: """SHORT VERSION — 2 of 3: IT WORKED

Soft closes and slams separated very cleanly, and it wasn't even close — the quietest slam
beat the loudest gentle close. On the microphone, 12.3 decibels louder. On vibration, 2.6
times bigger.
""",

4: """SHORT VERSION — 3 of 3: WHAT'S LEFT

The phones disagree about absolute values, so we only report change within a session. One
channel returned nothing for eight minutes while the app called it healthy. And we've only
tested a few devices.
""",

5: """CHRIS, RUNNING THE APP   [13 s clip auto-plays]

Chris running it in Toronto. Six channels reading live — then he starts the recording.
""",

6: """DIVIDER

So what were our aims and objectives?
""",

7: """WHY RECORD THE ROOM — 1 of 3

Two people can run the same protocol and get totally different answers. The difference
usually isn't the protocol. It's everything around it that people forgot to write down.
""",

8: """+ THE EDGE EFFECT — 2 of 3

Cells in the outer wells of a well plate read up to 35% lower than the ones in the middle.
Evaporation, and a temperature gradient across the room. Not a technique problem.
""",

9: """+ THE ISOS CONSENSUS — 3 of 3

Perovskite solar results weren't comparable between labs at all. So the field wrote a
consensus statement, in Nature Energy, on what has to be recorded for a result to count.
""",

10: """AIMS AND OBJECTIVES

Three. Build a recorder, reproduce two known sensing techniques on commodity hardware, and
work out whether the data we get back can be trusted.

One constraint: no extra hardware — could the equipment fancy labs use be matched by
what's already in our pockets? 
""",

11: """DIVIDER

"Project presentation."
""",

12: """IMPLEMENTATION

Expo Go is the part we interfaced with most — point it at a QR code and it runs your
JavaScript. But it ships a fixed set of native modules, and your code can only reach
those. Microphone level and iOS light are outside that set, so those meant Swift and a
developer account.

There's also a calibration step, twenty seconds at rest. Every phone is different, so what
matters is the delta between calibration and the real reading.
""",

13: """WHY THIS IS HARD

Consumer hardware has a lot of failure modes. The one that surprised us: the streams
aren't raw. Factory calibration is baked into firmware, so you're reading a number the
vendor already conditioned.

We ran the experiment with more and less background noise, and the gain had already been
factored out — we couldn't tell the difference.
""",

14: """DIVIDER

"Changes to the plan."
""",

15: """CHANGES SINCE THE PROPOSAL

We originally proposed an Alka-Seltzer study. It needed sound and light, Expo Go wasn't loading them, so we
swapped to door closes.

We eventually got all six working, but we'd already pivoted — and the multi-site study
shrank, wisely, into a single site.
""",

16: """DIVIDER

"Results."
""",

17: """THE EXPERIMENT, LINE BY LINE

We followed our own protocol carefully — one continuous recording rather than six sessions,
so every condition lands on the same clock and thermal state. It wasn't perfect, but we
could read events off spikes rather than off exact timing.
""",

18: """PILOT STUDY   [16 s clip auto-plays]

Sped way up,. You can see the knock we used as a marker, and the doors
opening and closing — Chris in Toronto, then Chicago on different hardware.
""",

19: """WHAT THE INSTRUMENT MEASURED

Slams came in 12.3 decibels louder and 2.6 times bigger on vibration. What matters is that
nothing overlapped — the quietest slam beat the loudest gentle close,. As
simple as that is, it was a good sign.

And it replicated: the second phone gave 2.77 where the first gave 2.60. Pretty close. Not
perfect.
""",

20: """TWO PHONES, ONE TABLE

The other interesting one: the phones agree about change — within about three percent —
but disagree fundamentally about absolute values. Same table, same second, the two
barometers were far enough apart to be five metres of altitude.

So a phone tells you what changed, relative to itself. Not what the room actually was.
""",

21: """DIVIDER

"Reflection."
""",

22: """DESIGNING IT WAS HARDER THAN RUNNING IT

The hardest part wasn't the code, though Apple doesn't make it easy. It was designing an
experiment that could answer anything, in a house, on a deadline.

We also couldn't reach any statistical significance without a lot of repetition. That's
why we closed the door twenty-four times.
""",

23: """THINGS WE ARE STILL WORKING ON

We know the UI could guide people to better choices — most context fields are optional, so
sessions save with none of them.

We know the six sensors don't always support each other. One of those turned out to be us:
our own timer was counting its own firings instead of seconds. And there's no single best
channel yet.

""",

24: """EITHER OUTCOME IS USEFUL

If the sensors pass, that's interesting — consumer electronics would be good enough for
real experiments, which opens a lot of us up to citizen science.

If they fail, still interesting. The sensing moves into something like a sled, and the
interface is still a stopwatch on a countertop.
""",

25: """MIDWAY HYPOTHESIS

Channel by channel. Vibration we think is good — 13 to 109 times its own noise floor. The
barometer we don't trust yet: its slow rise looked the same whether we were slamming the
door or standing still.
""",

26: """WHAT HAPPENS NEXT

This week, a few more runs — getting rid of the magnet that confounded one of mine, and an
overnight run to see what two devices pick up over hours.

Longer term, the version worth building baselines every device on the market, so the app
can tell any phone whether it resolves the effect you care about.
""",

27: """WORKS CITED

We want to acknowledge the work we've cited, and Claude — Sonnet and Opus — used
throughout as a learning aid and analysis partner. Every measurement run by us, every
conclusion checked by us.
""",

28: """CONTRIBUTIONS

I want to thank my partner for working on this so diligently. Chris wrote the derived
sensor code, designed the pilot protocol, and ran the six test sessions. Study design, the
live tests and the analysis are mine.
""",

29: """SUMMARY

The recorder works. Whether a phone is a good enough instrument is still open — whether
it's a good enough recorder isn't.

We're posting the code and the data publicly, so please download, fork, and help improve
Covariate. Thank you so much.
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
