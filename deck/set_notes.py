"""Speaker notes: bullets to talk from, and the 8-minute cut.

Written to be said out loud by someone being matter-of-fact. No cold open, no
build-up, no lines that only work if delivered a particular way.

Claims are limited to what exists. On record: six sessions, one iPhone X, four
channels — accelerometer, barometer, magnetometer, derived vibration. No session
anywhere contains a sync, light or micLevel channel, and there is no dual-device
recording. So Mark sync is described as implemented rather than demonstrated on
data, cross-device agreement is untested, and the pendulum ladder is a design.

Footage cues say "a recording session" rather than naming a specific run, so any
B-roll of the app recording is accurate regardless of which take is used.

Four slides are hidden (`show="0"`) rather than deleted, which lands the shown
deck at 8:00 and keeps the full version for the report appendix.
"""
from pptx import Presentation

DECK = "Covariate_Demo.pptx"
HIDE = {3, 5, 7, 16}          # aims, channel table, privacy, remaining work

NOTES = {
1: """≈20s  ·  OPEN
• Covariate — a smartphone app that records ambient context and attaches it to an
  experiment record
• problem: experiments fail to reproduce, and the conditions that might explain it
  were never written down. Temperature, vibration, light, who was in the room
• premise: the phone already in the room can log some of that, at no extra cost
• what follows: what we built, what changed since the proposal, what the pilot
  data shows, and what it doesn't
""",

2: """≈45s  ·  WHY RECORD THE ROOM
• most mobile sensing characterises the person holding the phone. We're using the
  same sensors to characterise the room
• deployment isn't the obstacle here — a decent sensor package is already in most
  rooms where experiments happen. The open question is what useful measurement you
  can actually take with it
• the output is metadata attached to an experiment someone may try to repeat, not
  an adaptation for a user. That changes what's worth logging
• the technical contribution is the derived channel — gravity is a constant 1 g,
  a door closing moves the accelerometer about 1%. Remove the constant and measured
  SNR goes up 3.5 to 5×
""",

3: """≈30s  ·  AIMS   [hidden in the 8-min cut]
• build the recorder — five channels, one clock, one file per experiment
• reproduce two known sensing techniques on commodity hardware
• evaluate whether the output is trustworthy — sampling health, cross-device
  agreement, whether a logged covariate explains anything
• design constraint: no additional hardware. It has to run on a phone a lab
  already owns
""",

4: """≈50s  ·  IMPLEMENTATION
[CUE — footage of a recording session in the app runs under this]

• React Native under Expo Go. Installs by scanning a QR code — no provisioning
  profile, which matters if a second person is going to record anything
• direct sensors from Expo: accelerometer at 50 Hz, magnetometer at 25, barometer
  event-driven
• light and microphone level are native modules we wrote — Swift and Kotlin —
  because Expo doesn't expose them. They need a compiled dev client, and the app
  reports that rather than failing quietly
• microphone stores a level in dBFS. No audio is recorded
• vibration is derived from the raw accelerometer stream — more on that shortly
• one session is one JSON file: metadata, per-channel sampling health, and every
  sample on a shared clock
• sessions also carry a placement field — where the phone physically sat. Same
  event on a benchtop and on the floor below differ by more than doubling the force
""",

5: """≈40s  ·  CHANNELS   [hidden in the 8-min cut]
• seven channels in the schema. Four have recorded data so far
• light and micLevel are implemented but need the dev build, so nothing has been
  collected on them yet
• vibration is derived; sync is the alignment marker
• microphone stores a level, so there's no waveform to display and we don't display
  one
""",

6: """≈35s  ·  CROSS-DEVICE ALIGNMENT
[CUE — footage of Mark sync firing, with audio: three pulses, one second apart]

• session time is monotonic from each device's own recording start. Two phones
  share no clock origin, so a timestamp on its own can't align them
• firing the vibration motor produces an event any phone on the same surface picks
  up through its own accelerometer. One device knows when it emitted; the others
  have something to correlate against
• pulses are spaced a second apart deliberately — slide 12 shows why
• **state plainly: implemented, not yet exercised. We have no dual-device recording
  yet.** The analysis for it is written and tested against synthetic data
""",

7: """≈35s  ·  PRIVACY   [hidden in the 8-min cut]
• four properties enforced by the implementation, not by policy — audio never
  recorded, video audio-free by construction, location stored as region plus
  altitude and absent by default, recording session-scoped
• the proposal said this data holds no personal content. We retract that
• occupancy, daily routine, per-device sensor bias and barometric floor level are
  all inferable from an ambient record. The report documents those and the controls
""",

8: """≈45s  ·  CHANGES SINCE THE PROPOSAL
• scope reduced to the channels that run in Expo Go. Light and sound need a
  compiled dev client, and rather than spend schedule on that build step at a
  second site we replaced the Alka-Seltzer study with a door experiment using the
  remaining channels
• that gap — between working on the developer's device and running at another
  site — is a normal constraint in this area, and it cost us a week
• multi-site study reclassified as a case study. With one participant per site,
  person, city, phone model and building are confounded
• pre-registered: metrics, windows, exclusion rules and trial counts frozen and
  dated in the repository before the data existed
""",

9: """≈15s  ·  PILOT STUDY
[CUE — door experiment footage, 10–15s]

• run by Christopher Kimberley in Toronto: two baselines, two normal closes, two
  slams. One phone, one room, iPhone X
• six sessions, exported as JSON
• the three results that follow came from those files alone, in a different city,
  without further input from him
""",

10: """≈40s  ·  DERIVED VIBRATION CHANNEL
• top trace is raw accelerometer magnitude during a slam. It peaks at 1.011 g —
  about 1% above gravity
• gravity is a constant 1 g, so the event is small relative to what's already there
• bottom trace is the same sensor and the same samples with a low-pass estimate of
  gravity subtracted: 28 times the noise floor
• across the four door events the derived channel measures 3.5 to 5 times the SNR
  of the raw accelerometer
• this is the main technical result so far
""",

11: """≈45s  ·  EFFECT OF METRIC CHOICE
• same four events, three statistics
• the original write-up used a 200 ms window average. A door impact lasts about
  50 ms, so how much of it lands inside a given window depends on where the
  boundary falls
• all three statistics order close below slam. The margin differs: 1.4× for window
  RMS, 2.7× for the energy integral
• at two trials per condition none of this is statistically significant, and it
  could not have been — the smallest p an exact test can return at n=2 is 0.167
• the pre-registration now fixes six trials per condition
""",

12: """≈35s  ·  SYNC FIDUCIAL RECOVERY
• the pilot report concluded that only one of three sync taps had been recorded,
  and flagged it as a data-quality problem
• all three are present. Every session has three to five clean taps in the 50 Hz
  raw accelerometer
• three raps within a few hundred milliseconds fall into one or two windows of the
  5 Hz derived channel, which is where the original analysis looked
• so it was a reporting artifact rather than a recording failure
• it's also why the in-app sync marker spaces its pulses a full second apart
""",

13: """≈35s  ·  UNLABELLED EVENT DETECTION
[CUE — terminal, detect_events() on the six pilot sessions. 18pt minimum]

• everything so far has the same structure: we caused an event and then located it.
  That shows sensitivity, not field performance
• here the detector gets no labels. It sets a threshold from each recording's own
  background
• all four door events recovered, at the times the operator wrote down
• one baseline returned nothing, correctly
• the other returned one candidate at 2.1 times the noise floor — either an
  unnoticed event or a false positive at that threshold. Reported as unresolved
""",

14: """≈40s  ·  SCOPE AND LIMITATIONS
• established: the recorder detects a real physical event 13 to 109 times above its
  noise floor, repeatable to about 1% within a condition. The instrument's own
  behaviour is characterised — warm-up, drift, sampling health. The derived channel
  outperforms the raw sensor
• not established: one participant per site, so person, city, phone model and
  building are confounded. One operator, one room, one device family. Light and
  microphone untested. Cross-device agreement untested — we have one device
• this follows our reviewer's assessment of the proposal: three sites with one
  participant each cannot show that logging a covariate reduces between-site
  variance
• we accept that, and moved the quantitative claims to a within-site design
""",

15: """≈40s  ·  STANDARDISING THE DISTURBANCE
[CUE — pendulum footage if available; otherwise hold the diagram]

• the two trials labelled "slam" differed by 3.9×, which is comparable to the gap
  between slamming and closing
• so "hard" isn't usable as a level. The instruction, not the sensor, was the
  uncontrolled variable
• the replacement: fixed mass, fixed string length, marked release angles.
  E = mgL(1−cos θ). Five angles give a 22× range in impact energy
• six trials per level, randomised order — six because at n=2 an exact test cannot
  return a p below 0.167
• **be explicit: this is a design. It has not been run yet.** The pre-registered
  collection happens this week
""",

16: """≈35s  ·  REMAINING WORK   [hidden in the 8-min cut]
• none of this has been collected yet
• pendulum ladder — the pre-registered spine
• overnight ambient runs, three nights, aimed at the refrigerator duty cycle
• a blind detection trial: four hours of ordinary activity with the log sealed
  before analysis
• twelve hours of barometer against a National Weather Service station — the only
  channel we can check against an external reference
""",

17: """≈12s  ·  CONTRIBUTIONS
• door-slam pilot — protocol, recording, the six sessions — Christopher Kimberley
• recorder, export schema, analysis and study design — mine
""",

18: """≈25s  ·  SUMMARY
• the recorder works, and the derived vibration channel measures a real event 13 to
  109 times above its noise floor
• the pilot is a feasibility result, not a reproducibility result — two trials per
  condition, one operator, one device
• one usability defect worth reporting: all six pilot sessions are stored with
  condition "controlled", including both slams. The app accepted that without
  warning, which is a problem for a tool whose purpose is recording context
• the pre-registered study runs this week

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
