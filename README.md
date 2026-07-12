# Covariate

**Smartphone ambient-context recorder for experimental reproducibility.**
CS-7470 Mobile & Ubiquitous Computing (GT OMS, Summer 2026) — Team 42:
Caitlin Everett, Christopher Kimberley.

When an experiment fails to reproduce, the cause is often the room, not the
protocol. Covariate turns a phone into an always-on recorder of the invisible
variables — pressure, vibration, light, magnetic field, and sound *level*
(never audio) — on one shared clock, exported as a timestamped record tied to
a specific experiment. The core contribution is a cross-device reliability
study: is a commodity phone trustworthy enough to be metadata?

Full design: the project proposal (course submission). Work split and due
dates: `Team42_ToDo` (Teams notes page).

## Layout

    project.yml          XcodeGen definition — the .xcodeproj is generated, not committed
    Covariate/
      App/               SwiftUI entry + skeleton session UI
      Harness/           SharedClock, SensorChannel protocol, Sample, SamplingHealth
      Channels/          barometer, accelerometer, magnetometer, light (camera EXIF), mic level
      Session/           RecordingSession (fan-in), SessionRecord, JSON Exporter
    docs/
      schema.md          export schema v0.1.0 (release deliverable)
      prereg-template.md H1-H3 pre-registration — freeze before any study data
    analysis/            Python: H2 metrics (Pearson r, bias, noise floor)
    .github/workflows/   macOS CI build — proves every push compiles

## Build

Requires Xcode 15+ and [XcodeGen](https://github.com/yonaskolb/XcodeGen):

    brew install xcodegen
    xcodegen generate
    open Covariate.xcodeproj

Run on a real device — the simulator has no barometer, magnetometer, camera,
or microphone worth measuring. Mic and camera permission prompts appear on
first session start; the mic is level-only and the camera is metadata-only by
construction (see channel source headers).

## Skeleton status & near-term roadmap

- [x] Five channels streaming on a shared monotonic clock
- [x] Sampling-health accounting (drop fraction, max gap) — O1 gate is <2% over ≥30 min
- [x] Experiment-linked JSON export (docs/schema.md)
- [x] CI build verification on macOS runner
- [ ] Stream samples to disk incrementally (crash-safe long sessions)
- [ ] Sync fiducial capture (tap/flash) for cross-device alignment
- [ ] Vibration-meter + light/noise-logger views over the harness (reimplemented hacks — CK)
- [ ] BLE intake for ESP32 + BME280 external module (CK, ★)
- [ ] Background-session audit against iOS delivery caps

## Privacy

The microphone channel reduces audio buffers to a single RMS number in place;
nothing is ever written that could contain audio. The light channel reads EXIF
brightness metadata only; no photos or video are captured or stored.
