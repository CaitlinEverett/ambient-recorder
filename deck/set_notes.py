"""Replace the deck's speaker notes with riffable bullets, and set the 8-minute cut.

The first pass wrote notes as full prose — 2,233 words, about sixteen minutes read
aloud, and nothing anyone would actually talk from. These are bullets: the number
to say, the point to make, and the phrasing only where a sentence has to land a
particular way. Each slide leads with its time budget so the whole thing adds up
to eight minutes without anyone timing it.

Four slides are hidden rather than deleted (`show="0"`), so the full deck survives
for the report appendix.
"""
from pptx import Presentation

DECK = "Covariate_Demo.pptx"
HIDE = {3, 5, 7, 16}          # plan, channel table, privacy, queue — the 8-min cut

NOTES = {
1: """≈20s  ·  COLD OPEN
[CUE — phone on the quiet counter, hold 3s before you talk]

• "This is a quiet room. Nothing is happening in it."
• …except the fridge cycled twice, a door closed down the hall, and the floor's
  still ringing from a truck outside
• none of that gets written down. Experiment fails to reproduce tomorrow — none of
  it's in the notebook either
• Covariate records the room, so there's something to look at when it doesn't
""",

2: """≈45s  ·  THE IDEA
• ubicomp usually asks what sensors say about the *person*
• we asked what they say about the *room* — and whether that's worth writing down
• **deployment's already solved** — Weiser's calm tech showed up as a phone in
  every pocket. Hard part isn't getting a sensor in the room, it's what to do with
  the one that's already there
• **context-awareness pointed the other way** — activity recognition senses a
  person to serve that person. Here it serves a *record*, one that has to survive
  someone else repeating it later
• **the hack is a derived channel** — gravity's a big constant, a door closing is a
  rounding error next to it. Subtract the constant, same sensor gains two orders of
  magnitude. No new hardware
""",

3: """≈30s  ·  THE PLAN   [hidden in the 8-min cut]
• build the recorder — five channels, one clock, one file per experiment
• reproduce two known sensing techniques on commodity hardware
• evaluate whether any of it's trustworthy — sampling health, cross-device
  agreement, does a logged covariate explain anything
• constraint we picked on purpose: **no special hardware.** A phone every lab
  already owns, or it doesn't get used
""",

4: """≈50s  ·  WHAT WE BUILT
[CUE — app screen recording runs under this; talk over it]

• React Native under Expo Go — teammate joins by scanning a QR code. No install,
  no provisioning profile. That's the whole premise
• **direct sensors** from Expo — accel 50 Hz, magnetometer 25, barometer
• **native modules we wrote** — Swift and Kotlin — for light and mic level, because
  Expo doesn't expose them. Those need a compiled dev build, and the app says so
  instead of pretending
• mic stores a *level*, never audio. So there's no waveform to draw and we don't
  draw one
• **derived channel** — vibration — computed off the raw accel stream. Coming back
  to that one
• every session = one JSON file: metadata, per-channel sampling health, every
  sample on a shared clock
• and a **placement** field — where the phone physically sat. Required, because the
  same event on a benchtop vs. the floor below differs by more than doubling the
  force
""",

5: """≈40s  ·  CHANNELS   [hidden in the 8-min cut]
• seven channels, units and rates
• two say "dev build" — the native ones. Honest about what's actually running
• vibration is derived, sync is the alignment fiducial — both ours, not the
  platform's
• bottom line's a design rule not a caption: sound is a level, never a waveform.
  Drawing a squiggle would misrepresent the privacy guarantee
""",

6: """≈35s  ·  MARK SYNC
[CUE — play the Mark sync clip WITH SOUND. Three buzzes, a second apart]

• session time is monotonic from each phone's own start — two phones share no clock
  at all. A 40-second offset between two files is normal and means nothing
• so a button that only wrote a timestamp would align nothing
• buzzing the motor makes an event **every phone on the surface hears** through its
  own accelerometer. One device gets ground truth, the others get something to
  correlate against
• one-second spacing is load-bearing — you'll see why in two slides
""",

7: """≈35s  ·  PRIVACY   [hidden in the 8-min cut]
• four properties that are structural, not policy — audio never recorded, video
  audio-free by construction, location is a region + altitude and absent by
  default, recording is session-scoped
• then the honest part: our proposal said this data holds no personal content.
  **We retract that.**
• longitudinal ambient data is data about a household — occupancy, routine, device
  fingerprint, floor of a building. All of that's in the report now, with what we
  do about it
""",

8: """≈45s  ·  WHAT CHANGED
• **scoping call we'd make again** — two of five channels are native modules, so
  they need a compiled dev client. Getting a second site through that extra build
  step was friction we chose not to spend the schedule on. Dropped the
  Alka-Seltzer study, ran a door experiment that needs only what installs from a
  QR code
• worth naming as a finding, not an inconvenience — the gap between "works on my
  device" and "runs at another site" is the constraint this whole field lives
  inside
• **reviewer was right** — three sites with one participant each can't support a
  between-site variance claim. Person, city, phone model, building: all
  confounded. Multi-site is now explicitly a case study
• **we pre-registered** — metrics, windows, exclusion rules, trial counts, frozen
  and dated in the repo before the data existed
""",

9: """≈15s  ·  THE PILOT
[CUE — Chris's door footage, 10–15s]

• Christopher Kimberley ran this in Toronto — 2 baselines, 2 normal closes, 2
  slams. One phone, one room, iPhone X
• everything on the next three slides comes out of those six files
• worth noticing on its own: somebody else's recordings, another city, reanalysed
  from scratch without asking him a single question. The export format did its job
""",

10: """≈40s  ·  THE HACK
• top trace — raw accelerometer during a slam. Peaks at **1.011 g**. One percent
  above gravity
• because gravity is a constant 1 g sitting on top of everything and the event is a
  rounding error next to it
• bottom — same sensor, same samples, low-pass estimate of gravity subtracted out.
  **28× the noise floor**
• across the four door events the derived channel beats the raw one it comes from
  by **3.5 to 5×** in SNR
• that's the hack. Subtracting a large constant is what lets a small transient be
  seen at all
""",

11: """≈45s  ·  THE STATISTIC CHANGES THE MARGIN
• same four events, measured three ways
• the original write-up used a 200 ms window average — and a ~50 ms door impact
  gets diluted by wherever that window boundary happens to land
• all three orderings are correct. But window RMS leaves a **1.4× margin** between
  close and slam where the energy integral leaves **2.7×**
• margin is what survives more trials
• and at two trials per condition none of this is significant — it *couldn't* be.
  Smallest p an exact test can return at n=2 is **0.167**
• the design could not have reached significance on any data at all. That's now a
  rule: six per condition, minimum
""",

12: """≈35s  ·  THE TAPS WERE NEVER LOST
• pilot write-up said only one of three sync taps got recorded — flagged as a data
  quality problem
• they were all there. Every session has 3 to 5 clean taps in the **50 Hz raw
  accelerometer**
• three raps inside a few hundred ms fall into one or two windows of the 5 Hz
  derived channel — which is where we looked
• reporting artifact, not a data failure — and exactly the kind of thing that gets
  written into a paper if nobody re-runs it
• also why the in-app sync marker spaces its pulses a full second apart
""",

13: """≈35s  ·  DETECTION WITHOUT LABELS
[CUE — terminal, run detect_events live. 18pt minimum]

• everything so far has the same shape: we caused an event, then found it. Proves
  sensitivity, says nothing about field performance — the analyst always knew where
  to look
• so: **the detector gets no labels.** Sets its own threshold from each recording's
  quiet background
• finds all four door events, at the times Chris wrote down
• finds nothing in one baseline — correctly
• one marginal candidate in the other, ~2× the floor. Either a real event nobody
  noticed or a false positive at our threshold. We report it either way
""",

14: """≈40s  ·  WHAT THIS IS — AND ISN'T
• left side: what it can claim. Feasibility study, and it succeeds as one — detects
  a real event 13–109× above its noise floor, repeatable to ~1%, instrument
  characterised, derived channel beats raw
• right side: what it can't. One participant per site, so person/city/phone/building
  all confounded. One operator, one room, one device family. Light and mic
  untested. Cross-device has one pair behind it
• **our reviewer said it first** — three sites with one participant each cannot show
  a logged covariate reduces between-site variance
• they were right. So the quantitative claims moved to a within-site design, and
  the multi-site work stays a case study
""",

15: """≈40s  ·  'HARD' ISN'T A MEASUREMENT
[CUE — pendulum footage: wide shot, then close on the release]

• biggest lesson came from the slams — two trials both labelled "slam" differed by
  nearly **4×**. Comparable to the gap between slamming and closing
• "hard" isn't a measurement, it's a mood. And we'd built a study on top of one
• so the disturbance gets a number — fixed mass, fixed string, marked release
  angles. E = mgL(1−cos θ). Five angles span **22×**
• six trials per level, randomised order. Six because at n=2 an exact test can't
  return a p below 0.167
• and say it: **this take is a demonstration.** I'm talking next to the phone, which
  our own frozen protocol excludes. The dataset run happens this week, empty room
""",

16: """≈35s  ·  QUEUED   [hidden in the 8-min cut]
• pendulum ladder — the confirmatory spine, everything quantitative rests on it
• overnight runs, 3 nights — after the fridge duty cycle. A compressor cycling
  every half hour is exactly the invisible variable we're arguing about
• blind detection trial — 4 hours of normal activity, log sealed before analysis
• 12-hour barometer run against a National Weather Service station — the only
  channel we can check against anything outside our own project. The offset should
  imply our own altitude, which we can check
""",

17: """≈12s  ·  CONTRIBUTIONS
• door-slam pilot — protocol, recording, the six sessions — Christopher Kimberley
• recorder, export schema, analysis, study design — mine
""",

18: """≈25s  ·  CLOSE
• here's the one that stung
• all six pilot sessions are labelled **"controlled"** — including both slams
• our own app let us mislabel the entire dataset without a word
• we're building a tool to record what nobody wrote down, and it let us not write
  something down
• that's a real finding about the product, and it's in the report

[CUE — cut back to the opening frame, phone on the counter. Hold 2s, out]
""",
}

prs = Presentation(DECK)
for i, slide in enumerate(prs.slides, 1):
    slide.notes_slide.notes_text_frame.text = NOTES[i].strip()
    # Hide rather than delete: the full deck stays available for the appendix.
    if i in HIDE:
        slide._element.set("show", "0")
    else:
        slide._element.attrib.pop("show", None)
prs.save(DECK)

shown = [i for i in NOTES if i not in HIDE]
budget = sum(int(NOTES[i].split("s")[0].strip("≈ ")) for i in shown)
print(f"notes set on {len(NOTES)} slides · {len(HIDE)} hidden ({sorted(HIDE)})")
print(f"8-min cut: {len(shown)} slides, budgeted {budget}s = {budget / 60:.1f} min")
