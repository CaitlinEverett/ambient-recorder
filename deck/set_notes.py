"""Speaker notes: bullets to talk from, and the 8-minute cut.

Written to be said out loud by someone being matter-of-fact. No cold open, no
build-up, no lines that only work if delivered a particular way.

Claims are limited to what exists. On record: six sessions, one iPhone X, four
channels — accelerometer, barometer, magnetometer, derived vibration. No session
anywhere contains a sync, light or micLevel channel, and there is no dual-device
recording. Everything not yet collected is labelled as planned, in the notes as
well as on the slide.

Slides 6 and 8 carry the class-grounded material: per-sensor capability and gotcha
on 6, and the analysis approach on 8 — including why this project stays on the
Sensor Data Analysis rail rather than the Applied ML one, which the required
reading justifies directly.

Footage cues say "a recording session" rather than naming a specific run, so any
B-roll of the app recording is accurate whichever take is used.

Nine slides are hidden (`show="0"`) rather than deleted: that lands the shown deck
at 8:00 and keeps the full 23 for the report appendix and the final presentation,
where the remaining material has room.
"""
from pptx import Presentation

DECK = "Covariate_Demo.pptx"

# The 8-minute cut. Hidden, not deleted — these are the slides whose content is
# either covered in a sentence elsewhere or belongs in the longer final version.
HIDE = {5, 7, 8, 10, 15, 16, 19, 20, 21}

NOTES = {
1: """≈20s  ·  OPEN
• Covariate — a smartphone app that records ambient context and attaches it to an
  experiment record
• the question underneath it: can consumer-electronics-grade sensors do
  science-grade context capture? This is a feasibility study of the hardware class,
  not just of our app
• what follows: why that's hard, how we plan to settle it per sensor, what the
  pilot data shows so far, and what we still have to run
""",

2: """≈38s  ·  WHY RECORD THE ROOM
• the reproducibility problem is usually framed as statistics or incentives. A large
  part of it is simply that conditions weren't written down
• the Reproducibility Project: Cancer Biology is the clearest evidence — **of 193
  experiments they tried to replicate, none was described completely enough to
  design a protocol without contacting the original authors.** Zero out of 193
• and it isn't only description. Crabbe, in Science 1999, ran the same mouse
  behavioural tests in three labs simultaneously, standardising equipment,
  protocol, handling, food, bedding, light cycle, even experimenter behaviour — and
  still got systematically different results. Something unrecorded was doing the work
• a 2018 survey of 200 papers in Nature, Science and Cell found 71% omitted multiple
  parameters governing cell-culture oxygenation. Six percent reported all of them
• everyday version: bread. Proofing temperature changes gas retention, storage
  humidity changes flour moisture, and oven temperature and time alone produce about
  a 1.6× spread in loaf volume. Nobody writes those down either
• most mobile sensing characterises the person holding the phone. We're using the
  same sensors to characterise the room
""",

3: """≈40s  ·  WHY THIS IS HARD
• worth being specific about what's wrong with consumer sensors, because "phones are
  noisy" isn't a research position
• **the raw stream isn't raw** — SensorID, IEEE Security & Privacy 2019, recovers the
  factory calibration coefficients baked into phone firmware. That attack only works
  because the vendor is conditioning the signal before your app sees it
• **self-heating** — a MEMS gyro drifts 317 degrees per hour in its first 400 seconds
  purely from powering on, and takes about 2000 seconds to settle. A phone logging
  continuously spends its first half hour measuring itself. **We think this is our
  barometer warm-up**
• **per-unit drift** — four identical accelerometer units measured −1.2 to +1.4
  millig per degree, against a datasheet typical of ±0.5. So no generic correction
  works; each device needs its own
• **automatic pipelines** — auto-exposure and automatic gain control have to be
  defeated before light or sound is a measurement rather than an output
• **no traceability** — metrologists state it plainly: low-cost sensing lacks an
  unbroken calibration chain to a national standard. So we can claim relative change
  within a session and never an absolute value
• two of our own to add: sensor occlusion — a film on the lens, lint in the mic port,
  a case over the barometer vent — and the OS suspending background apps on long runs
""",

4: """≈40s  ·  ONE TEST PER SENSOR
• given all that, the useful thing to do is design one cheap decisive test per
  channel rather than argue about it
• vibration and accelerometer — a pendulum ladder. Fixed mass, fixed length, marked
  release angles, so impact energy is exact. Passes if the log-log slope's confidence
  interval excludes zero
• barometer — eight hours against a National Weather Service station, plus the
  warm-up curve from the same file. Passes if the slope is near 1 and the constant
  offset implies our actual altitude
• magnetometer — a magnet at four marked distances. A dipole field falls as one over
  r cubed, so we can check the measured exponent against −3
• light and microphone — both need a compiled dev client, so they aren't getting
  answered this term. Saying that is more useful than pretending otherwise
• cross-device — the same events on two devices on one surface
• the whole set is one unattended night plus about 75 minutes
""",

5: """≈30s  ·  AIMS   [hidden in the 8-min cut]
• build the recorder — five channels, one clock, one file per experiment
• reproduce two known sensing techniques on commodity hardware
• evaluate whether the output is trustworthy — sampling health, cross-device
  agreement, whether a logged covariate explains anything
• design constraint: no additional hardware. It has to run on a phone a lab already
  owns
""",

6: """≈45s  ·  IMPLEMENTATION  —  capability and gotcha, per sensor
[CUE — footage of a recording session in the app runs under this]

• React Native under Expo Go. Installs by scanning a QR code
• the Sensors module frames it well: sensor noise, drift and power budgets bound
  everything built above them. So, per channel — what it can do, and what to watch:

• **accelerometer** · 50 Hz, three axes. Can: resolve a millisecond-scale impulse and
  every sync tap. Gotcha: magnitude is dominated by a constant 1 g, so the event is
  1–4% of the reading. Also — for spectra you must never use magnitude, because a
  transverse vibration enters squared and doubles its own frequency
• **barometer** · event-driven, roughly 1 Hz. Can: detect real pressure change over
  minutes to hours. Gotcha: self-heating, and about 1 Hz is far too slow for a
  transient. Nyquist here is half a hertz
• **magnetometer** · 25 Hz. Can: sense large ferrous mass or a magnet up close.
  Gotcha: Earth's field is 25–65 µT and dominates; our event deviations were smaller
  than the baseline spread
• **derived vibration** · 5 Hz, computed. Can: 3.5 to 5 times the SNR of raw accel.
  Gotcha: 200 ms windows are too coarse to resolve ring-down, and the window clock is
  per-device, which is a cross-device problem
• **light and mic** · native modules, dev build only. Both sit behind automatic
  pipelines that have to be locked before the number means anything

• one more, general: our 50 Hz sampling puts Nyquist at 25 Hz, so 60 Hz mains
  machinery folds to 10 Hz and looks like a real structural mode. The analysis flags
  peaks near there and refuses to name them
""",

7: """≈35s  ·  IN USE   [hidden in the 8-min cut]
• this is the recording screen
• sampling health is on screen rather than buried in the export — latest value,
  sample count, drop fraction, per channel, live
• the O1 gate has its own progress bar: under 2% dropped samples over at least 30
  minutes. A session that fails it isn't worth analysing, and you want to know that
  before you walk away for eight hours
• magnetometer is flagged at 3.2% here. That's the display doing its job
• only two controls while recording — Mark Sync and Stop
""",

8: """≈45s  ·  CHANNELS  —  and how we analyse   [hidden in the 8-min cut]
• seven channels in the schema; four have recorded data so far
• on analysis, the course gives two adjacent rails and we're deliberately on one of
  them
• **Sensor Data Analysis** asks how to extract events and features from noisy
  high-rate streams — garbage in, garbage out, at sensor scale. The required reading,
  Bulling, Blanke and Schiele in ACM Computing Surveys, lays out the standard
  pipeline: windowing, features, classifier, evaluation. **We deliberately stop after
  features.** Our 200 ms windows and RMS, peak and energy statistics are steps one
  and two of exactly that pipeline
• **Applied ML** is the other rail, and the required reading there — Plötz, also ACM
  Computing Surveys, on the common pitfalls of pragmatic use — names leakage, poor
  evaluation and label noise. **That's our justification for not classifying.** At six
  sessions and two trials per condition a classifier would be measuring its own
  capacity, not the phenomenon
• where we do classify, in the exploratory analysis, it's a leave-one-out
  1-nearest-neighbour with nothing to fit, for that reason
""",

9: """≈28s  ·  CROSS-DEVICE ALIGNMENT
[CUE — footage of Mark sync firing, with audio: three pulses, one second apart]

• session time is monotonic from each device's own recording start. Two phones share
  no clock origin, so a timestamp alone can't align them
• firing the vibration motor produces an event any phone on the same surface picks up
  through its own accelerometer. One device knows when it emitted; the others have
  something to correlate against
• pulses are a second apart deliberately — slide 15 shows why
• **implemented, not yet exercised. No dual-device recording exists yet.** The
  analysis is written and tested against synthetic data
""",

10: """≈35s  ·  PRIVACY   [hidden in the 8-min cut]
• four properties enforced by the implementation, not by policy — audio never
  recorded, video audio-free by construction, location stored as region plus altitude
  and absent by default, recording session-scoped
• the proposal said this data holds no personal content. We retract that
• occupancy, daily routine, per-device sensor bias and barometric floor level are all
  inferable from an ambient record. The report documents those and the controls
""",

11: """≈35s  ·  CHANGES SINCE THE PROPOSAL
• scope reduced to the channels that run in Expo Go. Light and sound need a compiled
  dev client, and rather than spend schedule on that build step at a second site we
  replaced the Alka-Seltzer study with a door experiment using the remaining channels
• that gap — between working on the developer's device and running at another site —
  is a normal constraint in this area, and it cost us a week
• multi-site study reclassified as a case study. With one participant per site,
  person, city, phone model and building are confounded
• pre-registered: metrics, windows, exclusion rules and trial counts frozen and dated
  in the repository before the data existed
""",

12: """≈50s  ·  PILOT STUDY
[CUE — Chris's narrated door footage. Let it run. Caption over any cut:
 "protocol continues — 4 further trials"]

• run by Christopher Kimberley in Toronto: two baselines, two normal closes, two
  slams. One phone, one room, iPhone X
• he narrates the protocol as he goes, so this is the clearest record of what a
  session actually involves
• six sessions, exported as JSON
• the three results that follow came from those files alone, in a different city,
  without further input from him — which is a small point in favour of the export
  format
""",

13: """≈38s  ·  DERIVED VIBRATION CHANNEL
• top trace is raw accelerometer magnitude during a slam. It peaks at 1.011 g — about
  1% above gravity
• bottom trace is the same sensor and the same samples with a low-pass estimate of
  gravity subtracted: 28 times the noise floor
• across the four door events the derived channel measures 3.5 to 5 times the SNR of
  the raw accelerometer
• this is the main technical result so far
""",

14: """≈40s  ·  EFFECT OF METRIC CHOICE
• same four events, three statistics
• the original write-up used a 200 ms window average. A door impact lasts about 50 ms,
  so how much of it lands inside a given window depends on where the boundary falls
• all three statistics order close below slam. The margin differs: 1.4× for window
  RMS, 2.7× for the energy integral
• at two trials per condition none of this is statistically significant, and it could
  not have been — the smallest p an exact test can return at n=2 is 0.167
• the pre-registration now fixes six trials per condition
""",

15: """≈35s  ·  SYNC FIDUCIAL RECOVERY   [hidden in the 8-min cut]
• the pilot report concluded only one of three sync taps had been recorded, and
  flagged it as a data-quality problem
• all three are present. Every session has three to five clean taps in the 50 Hz raw
  accelerometer
• three raps within a few hundred milliseconds fall into one or two windows of the
  5 Hz derived channel, which is where the original analysis looked
• a reporting artifact rather than a recording failure — and why the in-app sync
  marker spaces its pulses a full second apart
""",

16: """≈35s  ·  UNLABELLED EVENT DETECTION
[CUE — terminal, detect_events() on the six pilot sessions. 18pt minimum]

• everything so far has the same structure: we caused an event and then located it.
  That shows sensitivity, not field performance
• here the detector gets no labels. It sets a threshold from each recording's own
  background
• all four door events recovered, at the times the operator wrote down
• one baseline returned nothing, correctly
• the other returned one candidate at 2.1 times the noise floor — either an unnoticed
  event or a false positive at that threshold. Reported as unresolved
""",

17: """≈40s  ·  MIDWAY HYPOTHESIS
• we're not done collecting, so here is what we currently believe, per channel, and
  what would change our minds. This is on the record before the data that settles it
• **vibration — likely good enough.** 13 to 109 times the noise floor, about 1%
  repeatability within a condition. Changes if the dose ladder isn't monotonic
• **accelerometer — good for timing, not amplitude.** It recovered every fiducial and
  every event, but only moves 1–4% above gravity
• **barometer — not yet trusted.** The session-length rise is identical in a baseline
  and a slam, which is what the self-heating literature predicts. Changes if it tracks
  a weather station over eight hours
• **magnetometer — probably not useful at this scale.** Event deviations were smaller
  than the spread inside a single baseline session
• **light and mic — unknown.** Untested, both need a dev build
• **cross-device — untested.** One device
• so: one channel looks good enough, one is promising, one probably isn't, three are
  unknown. Four runs settle all but the two needing a dev build
""",

18: """≈32s  ·  SCOPE AND LIMITATIONS
• established: detects a real physical event 13 to 109 times above its noise floor,
  repeatable to about 1% within a condition. The instrument's own behaviour is
  characterised. The derived channel outperforms the raw sensor
• not established: one participant per site, so person, city, phone model and building
  are confounded. One operator, one room, one device family. Light and microphone
  untested. Cross-device untested
• this follows our reviewer's assessment of the proposal: three sites with one
  participant each cannot show that logging a covariate reduces between-site variance
• we accept that, and moved the quantitative claims to a within-site design
""",

19: """≈35s  ·  STANDARDISING THE DISTURBANCE   [hidden in the 8-min cut]
[CUE — pendulum footage if available; otherwise hold the diagram]

• the two trials labelled "slam" differed by 3.9×, comparable to the gap between
  slamming and closing. So "hard" isn't usable as a level — the instruction, not the
  sensor, was the uncontrolled variable
• replacement: fixed mass, fixed string length, marked release angles.
  E = mgL(1−cos θ). Five angles give a 22× range
• six trials per level, randomised order — six because at n=2 an exact test cannot
  return a p below 0.167
• **this is a design. It has not been run yet**
""",

20: """≈35s  ·  REMAINING WORK   [hidden in the 8-min cut]
• none of this has been collected yet
• before the report: the overnight run — one night settles the O1 gate, the barometer
  warm-up curve, the weather-station comparison and the fridge duty cycle at once.
  Then the bench ladder, about 45 minutes, and a two-device run, about ten
• after the course: a second Android device family, more sites, and the external
  sensor package
• we'll analyse together and report what's settled, and say plainly what isn't
""",

21: """≈35s  ·  EITHER OUTCOME IS USEFUL   [hidden in the 8-min cut]
• if the sensors pass, ambient context capture is free for anyone with a phone —
  teaching labs, citizen science, opportunistic covariate logging where there is no
  instrumentation
• if they fail, the app is still the experiment-linked recorder, the schema and the
  interface, and the sensing moves to a cheap external package over Bluetooth
• that second case has measured support: the same sound-measurement apps, re-run with
  external calibrated microphones, came within ±1 dB of reference. The built-in signal
  chain was the limit, not the phone
• our ESP32 and BME280 stretch goal is already that architecture
""",

22: """≈12s  ·  CONTRIBUTIONS
• door-slam pilot — protocol, recording, the six sessions — Christopher Kimberley
• recorder, export schema, analysis and study design — mine
""",

23: """≈25s  ·  SUMMARY
• the recorder works, and the derived vibration channel measures a real event 13 to
  109 times above its noise floor
• the pilot is a feasibility result, not a reproducibility result — two trials per
  condition, one operator, one device
• one usability defect worth reporting: all six pilot sessions are stored with
  condition "controlled", including both slams. The app accepted that without warning
• four runs remain, they settle four of six channels, and we'll report what they say
  and what's still open

[CUE — closing frame, then out]
""",
}

prs = Presentation(DECK)
for i, slide in enumerate(prs.slides, 1):
    slide.notes_slide.notes_text_frame.text = NOTES[i].strip()
    if i in HIDE:
        slide._element.set("show", "0")
    else:
        slide._element.attrib.pop("show", None)
prs.save(DECK)

shown = [i for i in NOTES if i not in HIDE]
budget = sum(int(NOTES[i].split("s")[0].strip("≈ ")) for i in shown)
print(f"notes set on {len(NOTES)} slides · {len(HIDE)} hidden ({sorted(HIDE)})")
print(f"8-min cut: {len(shown)} slides, budgeted {budget}s = {budget / 60:.1f} min")
