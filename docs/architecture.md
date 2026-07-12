# Cross-platform architecture (pivot, 2026-07-12)

The recorder moves from native-SwiftUI-only to a **cross-platform UI** so it runs
on whatever phone each teammate has (Chris's device is unconfirmed — to-do 0b).
**Framework: React Native + TypeScript** (chosen 2026-07-12). Flutter was the
technical runner-up; React Native wins here for the reasons below.

Repo: [CaitlinEverett/ambient-recorder](https://github.com/CaitlinEverett/ambient-recorder) ·
Board: [Project #3](https://github.com/users/CaitlinEverett/projects/3) ·
To-do: [`todo.md`](../todo.md) · Schema: [`schema.md`](schema.md).

`main` keeps the native Swift skeleton as a **stable fallback** until the
cross-platform build is verified green. This rewrite lives on `crossplatform-rewrite`.

## Why React Native over Flutter (for this project)

- **Fidelity is a native concern, not a framework one.** The recording engine —
  sensor capture, monotonic timestamping, health accounting, and incremental
  disk-streaming — lives in **native code** (Swift/Kotlin). Every `Sample.t` is
  stamped in the native callback *before* it crosses the bridge, so the recorded
  series H2/O1 depend on are bridge-independent. The JS layer only drives UI and
  session orchestration. This neutralizes the main reason to prefer Flutter
  (cleaner streaming channels) — so the tie breaks on ergonomics.
- **Familiarity wins the tie.** On a 3-week, 2-person clock, the team's JS/TS
  fluency outweighs Flutter's marginal edge. Dart is easy, but it's still a new
  language for both of us, and time spent learning it is time not spent on the
  study.
- **Knowingly traded away:** Flutter's marginally cleaner `EventChannel` streaming
  and its single, more consistent toolchain. Acceptable given the native engine.
- **Stack specifics:** TypeScript (type-safe across the native boundary — the
  schema is the contract); the **New Architecture** (TurboModules / JSI) for the
  native sensor modules to minimize bridge overhead. Bare React Native, or Expo
  with prebuild / a dev client if we want nicer tooling — we need custom native
  modules either way, so Expo-managed alone is out.

## Non-negotiable: the recording engine stays native

The JS layer is **UI + orchestration only.** Sensor capture, timestamping, health,
and disk-streaming are native, exposed to TypeScript through a native module
(TurboModule with an event emitter) that streams `Sample(t, channel, values[])`
per schema **v0.1.1**. Not optional:

1. **Privacy invariant.** Mic RMS-only / no-audio-to-disk must be enforced inside
   the native audio callback and stay auditable. A generic JS audio library that
   ships buffers over the bridge or records to a file cannot guarantee it.
2. **Measurement fidelity.** H2 (r ≥ 0.9) and O1 (< 2% drop) *are* measurements of
   sensor agreement and health. Sampling uses native sensor APIs at controlled
   rates and is **timestamped natively before crossing the bridge**, so bridge
   latency delays only when the UI *sees* a sample, never the recorded `t`.
3. **The light channel is platform-specific regardless.** iOS: the EXIF
   BrightnessValue hack (unitless EV). Android: `Sensor.TYPE_LIGHT` (lux). No
   shared implementation exists. **Units differ — the schema/analysis must record
   which light source produced each `light` channel.**

**The existing Swift channels (`Covariate/Channels/*`) are reused as the iOS
native module — not thrown away.** Android needs equivalent Kotlin implementations
(barometer, accelerometer, magnetometer, light, mic-RMS), each preserving the same
privacy guarantees.

## H2 caveat this pivot introduces

H2 isolates *hardware* agreement. Running the co-located reliability pair across
two different operating systems injects an OS confound. So, before the co-located
runs (Sat 7/25) and stated in the pre-registration:

- Run the H2 pair on **two of the same platform** where possible (e.g. two
  iPhones), **or**
- Treat OS as a documented variable and report iOS↔Android agreement **separately**
  as a heterogeneity result (the Stisen "smart devices are different" angle) —
  not as the clean H2 number.

## Repo restructure (React Native)

    src/            TypeScript: three screens, Sample/Channel/SessionRecord types, native-module client
    ios/            iOS host + Swift native module (reuse Covariate/Channels)
    android/        Android host + Kotlin native module
    analysis/       unchanged — reads JSON
    docs/           unchanged — the schema is the cross-platform contract

`docs/schema.md` (v0.1.1) is the contract and does **not** change with the
framework. `project.yml` (XcodeGen) and the xcodebuild CI are replaced by a React
Native build CI (iOS + Android; e.g. an Expo/EAS build or `react-native` native builds).

## Verification gap (this session)

No React Native toolchain / Xcode / Android SDK on the authoring machine —
scaffolding here is **unverified**. Build and verification happen on a machine with
the SDKs (yours, or a runner that installs them). Treat every file on this branch
as "type-checks-by-inspection only" until CI on the new pipeline goes green.
