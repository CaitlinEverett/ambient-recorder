# Covariate

**📋 Project board — Kanban + roadmap, with due dates:** [github.com/CaitlinEverett/projects/3](https://github.com/users/CaitlinEverett/projects/3/views/2?groupedBy%5BcolumnId%5D=368078746) 

**Smartphone ambient-context recorder for experimental reproducibility.**
CS-7470 Mobile & Ubiquitous Computing (GT OMS, Summer 2026) — Team 42:
Caitlin Everett, Christopher Kimberley.

When an experiment fails to reproduce, the cause is often the room, not the
protocol. Covariate turns a phone into an always-on recorder of the invisible
variables — pressure, vibration, light, magnetic field, and sound *level*
(never audio) — on one shared clock, exported as a timestamped record tied to
a specific experiment. The core contribution is a cross-device reliability
study: is a commodity phone trustworthy enough to be metadata?

Full design rationale: [`docs/proposal.docx`](docs/proposal.docx) (submitted
course proposal). Repo: [ambient-recorder](https://github.com/CaitlinEverett/ambient-recorder)
· flat to-do: [`todo.md`](todo.md) · architecture & framework choice:
[`docs/architecture.md`](docs/architecture.md).

## Hypotheses

Fixed before data collection to avoid post-hoc fishing (verbatim from the
proposal; to be frozen in [`docs/prereg-template.md`](docs/prereg-template.md)
by **Wed Jul 22**, before any study runs):

- **H1 — context sensitivity.** In a disturbed run, a channel's activity
  exceeds the same phone's controlled-run 95th-percentile baseline (e.g.
  accelerometer vibration RMS), tested one-sided per device; likewise for the
  light and barometer channels.
- **H2 — cross-device agreement.** For each sensor, two phones on the same event
  agree with **Pearson r ≥ 0.9** and a **bias within the channel's at-rest noise
  floor**. A log two phones disagree about is worse than none; any channel that
  fails H2 is flagged untrustworthy, not dropped.
- **H3 — cross-site reproducibility.** Across three climatically distinct sites
  (Chicago, Brooklyn, Jacksonville), a fixed protocol gives measurably different
  outcomes, and **between-site variance shrinks once a logged covariate is
  included** (e.g. tablet-dissolution time regressed on temperature) — showing
  the log explains part of the non-reproducibility.

## Layout

    project.yml          XcodeGen definition — the .xcodeproj is generated, not committed
    Covariate/
      App/               SwiftUI entry + session UI (native skeleton; RN rewrite incoming)
      Harness/           SharedClock, SensorChannel protocol, Sample, SamplingHealth
      Channels/          barometer, accelerometer, magnetometer, light (camera EXIF), mic level
      Session/           RecordingSession (fan-in), SessionRecord, JSON Exporter
    docs/
      proposal.docx      submitted course proposal — full design rationale
      mockups.md         ASCII UI mockups (four screens + sound cards)
      schema.md          export schema v0.1.1 (release deliverable)
      prereg-template.md H1-H3 pre-registration — freeze before any study data
    analysis/            Python: H2 metrics (Pearson r, bias, noise floor)
    .github/workflows/   macOS CI build — proves every push compiles

## Design

Mockups: [`docs/mockups.md`](docs/mockups.md). Two principles drive the UI.

**The live view is for confidence, not analysis.** During a session a scientist
glances to answer two questions — *is this channel alive and healthy?* and *is
something disturbing my experiment right now?* Precise reading is deferred to the
exported record. That sorts every sensor into one of three visualization
families, by the shape of its data:

| Family | Sensors | Live view | Why |
|---|---|---|---|
| **Meter** | mic level, accelerometer | one-sided level/vibration bar + peak-hold | fast, energetic signals — you want "how much now"; a raw trace isn't glanceable |
| **Trend** | barometer, magnetometer, light | current value + Δ-from-start + sparkline | slow scalars — watch for drift and step-changes (door, HVAC, appliance, lights) |
| **Preview** | reference video (opt-in only) | camera thumbnail + `no audio` + storage | the only place a preview is honest — the user turned it on; confirms framing |

A cross-channel **Disturbance Timeline** on the session-complete screen marks
transients from every channel on one strip, answering the key reproducibility
question: *was my "controlled" run actually controlled?* — which feeds H1/H3.

**Simple, native-rendered data marks.** Structure uses the platform's stock UI
components; the data marks (meters, one-sided sparklines, the loudness heatmap)
are small custom-drawn views — less code than a chart library, and they read like
a lab instrument. Live views repaint at ~4 Hz, not per sample. No gradients,
glows, or spring motion. (Now targeting **React Native** — see
[`docs/architecture.md`](docs/architecture.md).)

**No audio waveform, ever.** No audio is stored, so there is no waveform — and we
never draw anything that *reads* like one, because a mirrored squiggle is the
visual signifier of "we recorded your audio." Sound is shown as a **meter**
(live) and a **loudness heatmap + summary stats** (session). Same rule for light:
the derived brightness scalar, never a camera preview.

## Plan

Session UI splits into three states + a modal: **New Session** (metadata +
pre-flight channel check) → **Recording** (elapsed, O1-gate progress, live
per-channel marks, Mark Sync) → **Session Complete** (per-channel drop vs. gate,
disturbance timeline, export). Two opt-in capture additions (schema v0.1.1):

- **Coarse location** — a one-time fix at session start storing *region +
  altitude only*, never raw coordinates. Altitude contextualizes the barometer;
  region enables weather cross-reference.
- **Reference video** — optional, **audio-free by construction** (shares the
  light channel's camera session, which has no audio input), written as a local
  `.mp4` sidecar referenced from the JSON. Excluded from the released dataset by
  default.

**Analysis** (H2 and reproducibility) is a reproducible pipeline, not a bespoke
app: [`analysis/reliability.py`](analysis/reliability.py) reads the schema'd JSON
and emits `results.csv` — one row per phone-pair × channel (r, bias, noise floor,
pass/fail), the team-shareable "compare in simple terms" table that opens in
Excel/Sheets — plus a notebook (`analysis/compare.ipynb`) that renders a static
HTML report (overlaid two-phone traces, correlation scatter, per-channel bars).

## Build

Requires Xcode 16+ (xcodegen >= 2.45 emits Xcode-16 project format 77) and [XcodeGen](https://github.com/yonaskolb/XcodeGen):

    brew install xcodegen
    xcodegen generate
    open Covariate.xcodeproj

Run on a real device — the simulator has no barometer, magnetometer, camera,
or microphone worth measuring. Mic and camera permission prompts appear on
first session start; the mic is level-only and the camera is metadata-only
unless Reference Video is explicitly enabled (and even then, audio-free).

## Roadmap

- [x] Five channels streaming on a shared monotonic clock
- [x] Sampling-health accounting (drop fraction, max gap) — O1 gate is <2% over ≥30 min
- [x] Experiment-linked JSON export ([`docs/schema.md`](docs/schema.md), v0.1.1)
- [x] CI build verification on macOS runner
- [x] UI mockups + design-system foundation (`Theme.swift`, `AccentColor`)
- [ ] Three-state session UI (New Session / Recording / Complete) + Mark Sync modal
- [ ] Stream samples to disk incrementally (crash-safe long sessions)
- [ ] Sync fiducial capture (tap/flash) for cross-device alignment
- [ ] Per-sensor live views (meters, trend sparklines) + Disturbance Timeline
- [ ] Coarse location fix + audio-free reference video (opt-in, schema v0.1.1)
- [ ] Vibration-meter + light/noise-logger views over the harness (reimplemented hacks — CK)
- [ ] BLE intake for ESP32 + BME280 external module (CK, ★)
- [ ] `results.csv` + `compare.ipynb` reliability report
- [ ] Background-session audit against iOS delivery caps

## Privacy

Three guarantees, stated here, in the channel source, and in the export schema:

1. **No audio, ever — absolute.** The mic channel persists only an RMS number
   computed in place; the optional reference video is audio-free by construction
   (its capture session has no audio input).
2. **The light channel stores only EXIF brightness**, never frames.
3. **Reference video** (opt-in) may store frames, but only as a local audio-free
   sidecar, and it is **excluded from the released dataset by default** —
   footage stays local unless explicitly released.

Location, when enabled, is coarse (region + altitude) and never raw coordinates.
The other channels (pressure, motion, magnetic field) hold no personal content.
