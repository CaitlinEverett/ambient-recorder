# Covariate export schema (v0.1.1)

One session -> one JSON file: `covariate_<experimentID>_<ISO8601>.json`.
This schema is a release deliverable (proposal deliverable 6) and the unit of
the labeled dataset (deliverable 3). Changes bump `meta.schemaVersion`.

> **Interface note (Chris):** v0.1.1 is **additive and backward-compatible** —
> two new *optional* `meta` fields (`location`, `video`). Nothing was renamed or
> removed; a v0.1.0 reader ignores them. See the changelog at the bottom.

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
| `startedAtWall`, `endedAtWall` | ISO 8601 | wall anchors. Cross-device alignment uses the physical sync fiducial (tap/flash), not wall clocks |
| `notes` | string | free text |
| `location` | object? | **v0.1.1, optional.** Coarse fix at session start (see below). Absent unless the user opts in |
| `video` | object? | **v0.1.1, optional.** Pointer to the audio-free reference-video sidecar (see below). Absent unless the user opts in |

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
| `t` | number | seconds since session anchor, monotonic shared clock |
| `channel` | string | see channel table |
| `values` | number[] | channel-specific, below |

## Channels

| channel | values | units |
|---|---|---|
| `barometer` | `[pressure, relativeAltitude]` | kPa, m |
| `accelerometer` | `[x, y, z]` | g |
| `magnetometer` | `[x, y, z]` | uT |
| `light` | `[brightnessValue]` | EXIF BrightnessValue (~log2 luminance, unitless) |
| `micLevel` | `[rms]` | dBFS. Level only — audio is never recorded |
| `external` | `[temperature, humidity, pressure]` | C, %RH, hPa (ESP32+BME280, stretch) |

## ChannelHealth

| field | meaning |
|---|---|
| `sampleCount` | samples received |
| `firstT`, `lastT` | first/last sample time on shared clock |
| `maxGap` | largest inter-sample gap, s |
| `nominalRate` | configured rate, Hz (null = event-driven) |
| `dropFraction` | derived: 1 - count/expected. O1 gate: < 0.02 over >= 30 min |

## Changelog

- **v0.1.1** — additive, backward-compatible. Adds optional `meta.location`
  (coarse region + altitude, opt-in) and optional `meta.video` (pointer to an
  audio-free reference-video sidecar, opt-in). Existing fields unchanged.
- **v0.1.0** — initial schema: `meta`, `health[]`, `samples[]`.
