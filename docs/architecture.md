# Cross-platform architecture (pivot, 2026-07-12)

The recorder moves from native-SwiftUI-only to a **cross-platform UI** so it runs
on whatever phone each teammate has (Chris's device is unconfirmed — to-do 0b).
**Framework: Flutter recommended** (better sensor/native-channel story); React
Native is possible. Chosen by Caitlin with the tradeoffs below understood.

`main` keeps the native Swift skeleton as a **stable fallback** until the
cross-platform build is verified green. This rewrite lives on `crossplatform-rewrite`.

## Non-negotiable: sensors stay native, behind platform channels

The cross-platform layer is **UI + orchestration only**. Every sensor channel is
implemented in native code and exposed to Dart/JS through a platform channel
(Flutter `EventChannel` / RN native module), emitting `Sample(t, channel,
values[])` per schema **v0.1.1**. This is not optional:

1. **Privacy invariant.** Mic RMS-only / no-audio-to-disk must be enforced inside
   the native audio callback and stay auditable. A generic audio plugin that
   ships buffers over a bridge or records to a file cannot guarantee it.
2. **Measurement fidelity.** H2 (r ≥ 0.9) and O1 (< 2% drop) *are* measurements
   of sensor agreement and health. Sampling must use native sensor APIs at
   controlled rates, timestamped natively — not resampled through a bridge that
   adds jitter. Bridge jitter would corrupt the exact quantity under study.
3. **The light channel is platform-specific regardless.** iOS: the EXIF
   BrightnessValue hack (unitless EV). Android: `Sensor.TYPE_LIGHT` (lux). No
   shared implementation exists. **Units differ — the schema/analysis must record
   which light source produced each `light` channel.**

**The existing Swift channels (`Covariate/Channels/*`) are reused as the iOS
backend behind the platform channel — not thrown away.** Android needs equivalent
Kotlin implementations (barometer, accelerometer, magnetometer, light, mic-RMS),
each preserving the same privacy guarantees.

## H2 caveat this pivot introduces

H2 isolates *hardware* agreement. Running the co-located reliability pair across
two different operating systems injects an OS confound. So, before the co-located
runs (Sat 7/25) and stated in the pre-registration:

- Run the H2 pair on **two of the same platform** where possible (e.g. two
  iPhones), **or**
- Treat OS as a documented variable and report iOS↔Android agreement **separately**
  as a heterogeneity result (the Stisen "smart devices are different" angle) —
  not as the clean H2 number.

## Repo restructure (Flutter)

    lib/            Dart: three screens, Sample/Channel/SessionRecord model, platform-channel client
    ios/Runner/     iOS host + Swift sensor backend (reuse Covariate/Channels)
    android/        Android host + Kotlin sensor backend
    analysis/       unchanged — reads JSON
    docs/           unchanged — the schema is the cross-platform contract

`docs/schema.md` (v0.1.1) is the contract and does **not** change with the
framework. `project.yml` (XcodeGen) and the xcodebuild CI are replaced by a
`flutter build` CI covering iOS + Android.

## Verification gap (this session)

No Flutter / Xcode / Android SDK on the authoring machine — scaffolding here is
**unverified**. Build and verification happen on a machine with the SDKs (yours,
or a Claude Code run that installs them). Treat every file on this branch as
"compiles-by-inspection only" until CI on the new pipeline goes green.
