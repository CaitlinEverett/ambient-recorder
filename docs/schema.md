# Covariate export schema (v0.1.3)

One session -> one JSON file: `covariate_<experimentID>_<ISO8601>.json`.
This schema is a release deliverable (proposal deliverable 6) and the unit of
the labeled dataset (deliverable 3). Changes bump `meta.schemaVersion`.

> **Interface note:** every version since v0.1.0 has been **additive and
> backward-compatible**. Nothing has been renamed or removed; a v0.1.0 reader
> ignores the newer optional fields. See the changelog at the bottom.

## Envelope

| field | type | meaning |
|---|---|---|
| `meta` | object | session metadata (below) |
| `health` | ChannelHealth[] | per-channel sampling-health record |
| `samples` | Sample[] | every reading, all channels interleaved, ordered by arrival |

## meta

| field | type | meaning |
|---|---|---|
| `schemaVersion` | string | this document's version |
| `experimentID` | string | links the session to a notebook experiment |
| `condition` | string | `controlled` / `disturbed` (pre-registered) |
| `site` | string | e.g. `chicago-kitchen` |
| `device`, `osVersion`, `appVersion` | string | provenance |
| `startedAtWall`, `endedAtWall` | ISO 8601 | wall anchors. Cross-device alignment uses the physical sync fiducial, not wall clocks |
| `notes` | string | free text |
| `placement` | string? | **v0.1.3, optional.** Where the phone physically sat (see below) |
| `location` | object? | **v0.1.1, optional.** Coarse fix at session start. Absent unless the user opts in |
| `video` | object? | **v0.1.1, optional.** Pointer to the audio-free reference-video sidecar. Absent unless the user opts in |

### meta.placement (v0.1.3, optional)

Free text describing the surface the phone rested on and its position relative
to the event — e.g. `oak benchtop, 30cm from impact point`.

This is not decoration. The coupling between a mechanical event and the
accelerometer depends on what the phone is sitting on; the same event recorded
on a benchtop and on the floor below it can differ by more than one step of a
deliberate dose ladder. **A session without `placement` is not comparable to one
recorded elsewhere**, and the field exists so that fact is recorded rather than
assumed.

### meta.location (v0.1.1, optional)

Coarse and dataset-safe by design — **never raw coordinates**.

| field | type | meaning |
|---|---|---|
| `region` | string | reverse-geocoded, e.g. `Chicago, IL, US` |
| `altitudeM` | number? | meters ASL; contextualizes the barometer baseline |
| `accuracy` | string | granularity actually stored, e.g. `city` |

### meta.video (v0.1.1, optional)

Pointer to a sibling `.mp4`/`.mov` file; the video itself is not embedded.

| field | type | meaning |
|---|---|---|
| `filename` | string | sibling file next to this JSON |
| `codec`, `resolution` | string | e.g. `hevc`, `1920x1080` |
| `fps` | number | frames per second |
| `hasAudio` | bool | **always `false`** — audio-free by construction (privacy invariant a) |

## Sample

| field | type | meaning |
|---|---|---|
| `t` | number | seconds since session anchor, monotonic |
| `channel` | string | see channel table |
| `values` | number[] | channel-specific, below |

`t` is monotonic **within one session on one device**. It is not a shared clock
and carries no common origin across devices — see the sync fiducial below.

## Channels

| channel | values | units | rate |
|---|---|---|---|
| `barometer` | `[pressure, relativeAltitude]` | kPa, m | event-driven |
| `accelerometer` | `[x, y, z]` | g | 50 Hz |
| `magnetometer` | `[x, y, z]` | uT | 25 Hz |
| `vibration` | `[rms, peak]` | g, g | 5 Hz |
| `light` | `[brightnessValue]` | EXIF BrightnessValue (~log2 luminance, unitless) | 5 Hz |
| `micLevel` | `[rms]` | dBFS. Level only — audio is never recorded | 10 Hz |
| `sync` | `[pulseIndex, pulseCount]` | 1-based index within the burst, and burst length | event-driven |
| `external` | `[temperature, humidity, pressure]` | C, %RH, hPa (ESP32+BME280, stretch) | event-driven |

### vibration (derived)

Not a sensor — a derived channel. Every raw accelerometer sample is fed through
a low-pass gravity estimate; the residual dynamic component is summarised over a
200 ms rolling window as `rms` (root-mean-square magnitude over the window) and
`peak` (largest single-sample magnitude in the window). Both are in g.

**Use `peak`, or an integral of `rms²`, for short impulses.** `rms` is a window
average, so a ~50 ms impact is diluted by however much of the 200 ms window it
occupies — and that depends on where the window boundary happens to fall.
`peak` is the maximum over raw samples, so the true peak lands in exactly one
window and survives intact. The analysis code's primary statistic is the
window-alignment-invariant energy integral; see `analysis/events.py`.

### sync (fiducial)

Emitted by the operator pressing **Mark sync**, which fires a burst of
`pulseCount` haptic pulses one second apart and writes one `sync` sample as each
pulse fires.

The marker is deliberately **physical**. A button that only wrote a timestamp
would be useless for cross-device alignment, because `t` has no shared origin
between devices. Driving the vibration motor produces an event that every phone
on the same surface observes through its own accelerometer, while the emitting
phone records exactly when it fired — one device gets ground truth, the others
get a signal to cross-correlate against.

The one-second spacing is load-bearing: pulses closer together than the 200 ms
vibration window collapse into a single sample and become indistinguishable from
one impulse. A manual three-rap on the surface is an equally valid fiducial and
requires no app support — space those a second apart too.

`sync` has a `nominalRate` of `null`. It is emitted on demand, so a
`dropFraction` derived from expected-versus-actual count would be meaningless
for this channel.

## ChannelHealth

| field | meaning |
|---|---|
| `sampleCount` | samples received |
| `firstT`, `lastT` | first/last sample time on the session clock |
| `maxGap` | largest inter-sample gap, s |
| `nominalRate` | configured rate, Hz (null = event-driven) |
| `dropFraction` | derived: 1 - count/expected. O1 gate: < 0.02 over >= 30 min. Always 0 where `nominalRate` is null |

## Changelog

- **v0.1.3** — additive, backward-compatible. Adds optional `meta.placement`;
  documents the `vibration` derived channel (present since the vibration-monitor
  merge but never written down here); adds the `sync` fiducial channel with
  `nominalRate: null`.
- **v0.1.2** — adds `vibration` and `sync` to `ChannelId`.
- **v0.1.1** — additive, backward-compatible. Adds optional `meta.location`
  (coarse region + altitude, opt-in) and optional `meta.video` (pointer to an
  audio-free reference-video sidecar, opt-in). Existing fields unchanged.
- **v0.1.0** — initial schema: `meta`, `health[]`, `samples[]`.
