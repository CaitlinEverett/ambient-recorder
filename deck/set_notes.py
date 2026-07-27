"""Speaker notes and the time budget, keyed to the video grading rubric.

The rubric caps length at 8 minutes and calls the maximum strict, so every slide
carries a second budget and the total is asserted at the bottom — the build fails
rather than quietly running long. Notes are bullets to talk from, not a script to
read; reading a script on camera is audible.

This is the LEAN deck: cut slides are absent from the file rather than hidden, so
what is open while filming is only what will be narrated. `LEAN= python3
build_deck.py` writes the full 35-slide version for the written report.
"""
import re
import sys

from pptx import Presentation

DECK = "Covariate_Demo.pptx"

NOTES = {

# -- open --------------------------------------------------------------------
1: """≈15s  ·  OPEN

• Covariate. A feasibility study: can consumer-grade phone sensors capture ambient
  experimental context well enough to be worth attaching to a record?
• CS-7470, Team 42. Caitlin Everett and Christopher Kimberley.
• Flat statement of what comes next — aims, what we built, what changed, what we
  measured, what we think now.
""",

# -- section 1 · AIMS AND OBJECTIVES -----------------------------------------
2: """≈3s  ·  DIVIDER

• Say it out loud: "Aims and objectives."
""",

3: """≈14s  ·  WHY RECORD THE ROOM  (1 of 3 — no papers yet)

• Two people run the same written protocol and get different answers.
• The difference usually isn't in the protocol. It's in everything around it that
  nobody wrote down.
• Bread is the everyday version — same recipe, different kitchen, different loaf.
  Nobody writes down the humidity.
""",

4: """≈12s  ·  + COLLBERG & PROEBSTING  (2 of 3)

• Start in our own field, so it isn't somebody else's problem. Collberg and
  Proebsting went after 601 papers from eight ACM conferences and five journals.
• They tried to get the code and build it. Succeeded for 32.3%.
• Most published computer systems work can't be repeated from what was written
  down — and that's the field with version control.
""",

5: """≈12s  ·  + THE ISOS CONSENSUS  (3 of 3)

• The interesting case is what a field does once it admits this.
• Perovskite solar cells: results weren't comparable between labs, because everyone
  tested under different ambient conditions and reported different parameters.
  Nature Energy, 2020 — a consensus statement across the field.
• The fix wasn't a better measurement. It was agreeing on which conditions have to
  be written down: temperature, humidity, illumination, atmosphere, bias.
• That's the whole argument in one citation. The ambient conditions were always
  affecting the result. They just weren't in the record until somebody decided they
  had to be.
""",

6: """≈32s  ·  AIMS AND OBJECTIVES  (as proposed)

• Three objectives, as we proposed them.
• BUILD — an ambient-context recorder. Pressure, motion, magnetic field, light,
  sound level, on one clock, exported as a file bound to a named experiment.
• REPRODUCE — two known sensing techniques on commodity hardware, and see what
  survives the move off instrument-grade sensors.
• EVALUATE — whether any of it is trustworthy. Sampling health, agreement between
  devices, whether a logged covariate explains variation between runs.
• Constraint we set ourselves: no additional hardware. It runs on a phone a lab
  already owns, or nobody uses it.
• This was always framed as a feasibility study. Our TA held us to that and was
  right to.
""",

# -- section 2 · PROJECT PRESENTATION ----------------------------------------
7: """≈3s  ·  DIVIDER

• "Project presentation."
""",

8: """≈26s  ·  IMPLEMENTATION

• React Native. Four kinds of channel.
• DIRECT — expo-sensors. Accelerometer, magnetometer, barometer. No build step.
• DERIVED — vibration. The one piece of real engineering. Gravity is a constant
  1 g and a door close is about 1% on top of it; estimate gravity, subtract it,
  then RMS and peak over a window.
• NATIVE — light and microphone level. Swift and Kotlin, because Expo exposes
  neither. Sound is stored as a LEVEL — no audio is recorded, so there's no
  waveform to leak. That's the code, not a policy.
• RECORD — one session, one JSON file. Metadata, placement, sampling health, one
  clock, aligned across devices by a haptic fiducial.
• The deployment boundary: four channels install by scanning a QR code. All six
  need a compiled dev client. The hardware is universal; access to it isn't.
""",

9: """≈8s  ·  IN USE — 1 of 4: DESIGNED

• Before any of it existed, this was the spec — an ASCII mockup of the recording
  screen.
• Sampling health on screen, not buried in the export. The operator should know a
  session is failing before they walk away from it.
""",

10: """≈9s  ·  IN USE — 2 of 4: BUILT

• The real thing. This is the sensor check: every module the device actually
  offers, with its rate and its current reading.
• All six present, including the two native modules. There's also a calibrate step
  — twenty seconds at rest — that measures each channel's own bias and noise.
• That matters because none of this is traceable to a standard. Knowing your own
  noise floor is the substitute.
""",

11: """≈12s  ·  IN USE — 3 of 4: RECORDING

• Six seconds into a session. Six channels, live, on one clock.
• Accelerometer, magnetometer, barometer, light, microphone level, and the derived
  vibration channel — each with its running sample count and realised rate.
• Two weeks ago this was four channels and a note saying the other two needed a
  build we hadn't done.
""",

12: """≈8s  ·  IN USE — 4 of 4: EXPORTED

• Stop and export. One session, one JSON file, 182 kilobytes.
• It leaves the phone through the normal share sheet — AirDrop, mail, files.
  Nothing proprietary, no account, no server. The file is the deliverable.
""",

13: """≈28s  ·  WHY THIS IS HARD

• Why this is a study and not a product announcement. Consumer sensors have
  documented, named failure modes.
• The raw stream isn't raw — SensorID, IEEE S&P 2019, recovers factory calibration
  baked into firmware. You're reading a vendor-conditioned number.
• Self-heating — a MEMS gyro drifts 317 degrees an hour in its first 400 seconds
  from power-on alone. A phone logging continuously starts by measuring itself.
• Per-unit thermal drift — four identical units, −1.2 to +1.4 mg per degree against
  a ±0.5 spec. No generic correction exists.
• Automatic pipelines — auto-exposure and AGC sit between the world and the number.
• Device heterogeneity — you can predict the OS from sensor quality metrics alone
  at 98% accuracy. Hold that one; we hit it ourselves in a few slides.
• No traceability — no calibration chain to a national standard. Relative change
  within a session, never an absolute value.
• Plus two of our own: occlusion — lens film, lint in the mic port, a case over the
  barometer vent — and the OS suspending background apps on long runs.
""",

# -- section 3 · CHANGES TO THE PLAN -----------------------------------------
14: """≈3s  ·  DIVIDER

• "Changes to the plan."
""",

15: """≈36s  ·  CHANGES SINCE THE PROPOSAL

• Four.
• ONE — scope was cut to four channels, then won back to six. Light and sound need
  a compiled dev client, so the pilot ran without them and we dropped the
  Alka-Seltzer study. The dev client now builds and all six record. A dropped
  feature turned into a measured deployment boundary.
• TWO — the multi-site study is now explicitly a case study. Our TA pointed out
  that three sites with one person each can't support a between-site variance
  claim; person, city, phone and building are confounded. Correct. The quantitative
  claims moved to a within-site design.
• THREE — the team went from two to one, and the protocol followed. The pendulum
  ladder got displaced by an ambient-condition experiment — a loud dehumidifier,
  switched on and off, identical door protocol under both. That tests the project's
  actual claim rather than characterising the instrument.
• FOUR — we pre-registered. Metrics, windows, exclusions, trial counts, frozen in
  the repo, dated, before the data existed.
""",

# -- section 4 · RESULTS -----------------------------------------------------
16: """≈3s  ·  DIVIDER

• "Results."
""",

17: """≈30s  ·  ALL SIX CHANNELS, ONE CLOCK

• Six-second session on the dev client. This is the live readout, enlarged.
• Then the thing we weren't looking for. 502 accelerometer samples in six seconds
  is 84 hertz. We requested 50. Magnetometer: 42, we requested 25. Both overshoot
  by the same factor, 1.68.
• The pilot phone didn't do that. Measured straight out of Chris's exported files:
  50.2 and 25.1. Nominal, both channels, same code.
• So device heterogeneity stopped being a citation and became two of our own phones
  disagreeing about what "50 hertz" means.
• And it moves the derived channel. Vibration comes out at 8 hertz here and 5 in
  the pilot — which tells us the 200-millisecond window is counted in SAMPLES, not
  milliseconds. On this device it's really about 119 milliseconds.
• A constant we froze in the pre-registration turns out to be device-dependent.
  That's a finding, and it's also a bug, and we found it by reading our own numbers.
""",

18: """≈36s  ·  PILOT STUDY   [footage runs here]

• The pilot: two baselines, two normal door closes, two slams. One phone, one room,
  Toronto. Chris ran it and narrates it.
• [CUE] Let the footage run. Caption over any cut: "protocol continues — 4 further
  trials."
• Coming out of it: the derived vibration channel separated slams from baseline at
  13 to 109 times the session noise floor.
• And a correction to our own pilot report — it said the sync taps were lost. They
  weren't. Re-running the detector at 50 Hz found 3 to 5 in all six sessions. A
  reporting artifact, not a data loss.
• THIS SLIDE IS THE TIME LEVER. Going long? Shorten the footage here.
""",

19: """≈25s  ·  DERIVED VIBRATION CHANNEL

• Raw accelerometer against the derived channel, same events.
• Gravity dominates: a door close is about 1% on top of a constant 1 g. Subtract
  the constant and the same samples give 3.5 to 5 times the signal-to-noise. No new
  hardware.
• One trap, because we walked into it. You can't take a spectrum of the
  acceleration MAGNITUDE — magnitude is the square root of signal-squared plus one,
  so a transverse vibration enters squared and comes out at double its frequency.
  We planted 7 Hz and the magnitude spectrum returned 14. Per-axis and detrended:
  7.03.
• The kind of mistake that produces a confident wrong number.
""",

20: """≈20s  ·  EFFECT OF METRIC CHOICE

• Same four events, three metrics — window energy, peak, RMS.
• All three order the conditions correctly. What differs is the margin: 1.38 times,
  1.94, 2.70.
• Metric choice doesn't change the direction here. It changes how much room you
  have before noise eats the result. That's why the metric is frozen in the
  pre-registration instead of picked after looking.
• Honest note: we first wrote that one of the three failed to separate them. Then
  we rendered the figure and it hadn't. We fixed the claim.
""",

# -- section 5 · REFLECTION --------------------------------------------------
21: """≈3s  ·  DIVIDER

• "Reflection." Say it — this is where the marks are.
""",

22: """≈30s  ·  MIDWAY HYPOTHESIS

• What we believe right now, per channel, and what would change our minds. Stated
  before the data, so it can be wrong.
• VIBRATION — likely good enough. 13 to 109 times the floor. Falsified if the dose
  ladder isn't monotonic.
• ACCELEROMETER — good for timing, not amplitude. Recovered every fiducial; events
  sit 1 to 4% above gravity.
• BAROMETER — not yet trusted. The session-long rise looked identical in baseline
  and slam, which says we're measuring the device, not the room.
• MAGNETOMETER — probably not useful at this scale. The noise is bigger than the
  signal. A clean negative is still a result.
• LIGHT — sampling but not yet reporting. 87 samples in six seconds and the EV
  field still renders as a dash. Something between the module and the display isn't
  finished.
• MIC LEVEL — recording. Minus 62 dBFS, 82 samples, exported.
• CROSS-DEVICE — already returning a result: our two phones differ by 1.68× in
  realised rate.
""",

23: """≈30s  ·  WHAT WE GOT WRONG

• Three, and the third is about our own product.
• ONE — the pilot could not have succeeded. Two trials per condition. An exact
  permutation test on n equals two has a minimum attainable p of 0.167, so no
  arrangement of that data could have cleared 0.05. We designed a study whose result
  was fixed before we collected anything, and didn't notice until we tried to
  analyse it. Six per condition puts the floor at 0.001.
• TWO — there is no single best channel. The derived channel wins on sensitivity
  and loses on cross-device agreement, because each device runs its own window
  clock. Sensitivity and comparability trade against each other.
• THREE — the app let us mislabel every session, silently. All six pilot sessions
  are stored as condition "controlled". Including both slams. We're building an
  instrument to record what nobody wrote down, and it accepted a whole dataset
  written down wrong without a word. Found by using our own tool.
""",

24: """≈20s  ·  EITHER OUTCOME IS USEFUL

• Why the question is worth asking whichever way it goes.
• IF THE SENSORS PASS — ambient context capture is free for anyone with a phone.
  Teaching labs, citizen science, anywhere with no instrumentation budget.
• IF THEY FAIL — the app is still the experiment-linked recorder: the schema, the
  UI, the sampling-health gate. The sensing moves to a cheap external package over
  BLE, and the phone's own sensors stop being confounding variables.
• That second case has support. The same phone sound-level apps, re-run with
  external calibrated microphones, came within ±1 dB of reference. The built-in
  signal chain was the limit, not the phone.
• So the real question isn't "does the phone work." It's "what's the cheapest thing
  that does, and can this app host it."
""",

25: """≈12s  ·  CONTRIBUTIONS

• Chris ran the door pilot — protocol, recording, the six sessions.
• The recorder, export schema, analysis and study design are mine.
""",

26: """≈12s  ·  SUMMARY

• The recorder works. All six channels record and export.
• A feasibility result, not a reproducibility result — the honest version of what
  one term buys.
• Whether a phone is a good enough INSTRUMENT is still open. Whether it's a good
  enough RECORDER isn't.
• Pre-registered study runs this week.
• [CUE] Cut to the opening frame — phone on the counter, hold two seconds, out.
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

prs.save(DECK)
print(f"{n} slides, all shown")
print(f"budget {total}s = {total // 60}:{total % 60:02d}   cap 8:00, margin {480 - total}s")
if total > 470:
    sys.exit("OVER BUDGET — trim before filming")
