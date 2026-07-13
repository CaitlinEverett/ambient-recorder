# Round 2 — sensor fusion + the science sled (vision / future work)

Earmarked ideas beyond the core study. **None of this blocks the current build**
(5 phone channels → session export → analysis). Captured so it isn't lost, and
it doubles as the report's "future work" section.

---

## Earmarked big stretch goals (native / Pro-device / hardware)

- **LiDAR room scan** (Apple RoomPlan / ARKit) — one scan per site as *spatial
  context* for H3 (room volume, surfaces, bench-to-vent/window proximity).
  iOS **Pro only**, custom native module + dev client. Store dimensions / a USDZ
  mesh reference in the session record; not real-time.
- **Reference video** — audio-free `.mp4` sidecar (`expo-camera`).
- **Distributed multi-kitchen census** — crowdsourced contributions, **moderated +
  consented + IRB-reviewed** (see the covariate.science landing page).

---

## Sensor fusion — the interesting "flavors"

Two distinct moves:
1. **Fuse to characterize context better** — richer covariates (heat maps, room
   acoustics, air bundle). The phone stays an *ambient logger*.
2. **Fuse to make the phone the measuring instrument** — vision times the assay,
   colorimetry reads the reaction. The phone stops logging *around* the
   experiment and starts *measuring* it. This is the bigger leap.

`plain` = deterministic math · `ML` = a learned model.

### Heat-first
- **Thermal (IR) + LiDAR/depth → 3D bench heat map.** `plain` (project thermal
  pixels onto the depth mesh). Spatially-resolved temperature — hot/cold spots,
  drafts, a reaction's exotherm. Temperature is the dominant covariate for the
  dissolution assay; this makes it *spatial*. **Note:** light ≠ heat — brightness
  + LiDAR gives a *lit* 3D model; you need an IR/thermal sensor for actual heat.
- **Thermal time-series → outcome.** `plain` — does a thermal excursion predict a
  bad run.

### Sight-first (phone-as-instrument)
- **Vision → automatic assay event detection.** `ML` — the camera detects
  "tablet dropped in," "bubbling started," "fully dissolved," and timestamps them,
  fused with the ambient channels. Automates the tedious Table-1 event marking and
  removes human-timing error. **Highest-value fusion for this study.**
- **Camera colorimetry / turbidity + light calibration → read the reaction.**
  `plain`/`ML` — measure color-change or cloudiness under characterized light. The
  phone becomes a colorimeter/turbidimeter.

### Sound-first
- **Mic spectrum + accelerometer vibration → disturbance-source classifier.**
  `ML` — fuse the acoustic signature with the structural vibration to *label*
  disturbances: HVAC, door, footsteps, appliance. Turns raw H1 spikes into a
  labeled disturbance timeline.
- **Mic + room geometry (LiDAR) → reverberation estimate → correct sound level.**
  `plain` (Sabine: volume + surfaces → RT60). Makes cross-site sound comparable.

### Light-first
- **Spectral light (AS7341) → light *quality*.** `plain` — daylight vs LED vs
  fluorescent have different spectra; matters for anything photosensitive, and
  validates the phone's camera-EXIF brightness hack against a real reference.

### Motion-first
- **Accel + gyro + mag → orientation/AHRS + "is the bench level & stable."**
  `plain` (Kalman/Madgwick) — foundational sanity + a stability covariate.
- **Vibration FFT + mic → appliance fingerprinting.** `ML` — identify *which*
  machine is running from its combined vibro-acoustic signature.

---

## The science sled (round 2 hardware)

### Job
Repeatable phone pose + protect internal-sensor fidelity + add the covariates the
phone physically can't sense.

### Protect / keep clean the phone's internal sensors
- **Vibration:** couple the phone *rigidly to the bench* (you want to measure
  bench vibration), but *isolate it from sled-borne* vibration (fans, cables) —
  no rattling in the mount.
- **Thermal:** keep the phone cool — thermal throttling *is* sensor throttling
  (the O1 gate). Don't enclose it; mount external temp sensors **away** from the
  phone's own heat.
- **Magnetic:** non-ferrous frame (aluminium/plastic); keep motors, magnets, and
  power cables away from the magnetometer; ferrite chokes on any power leads.
- **Optical / acoustic:** camera (light channel) and mic port unobstructed; shield
  the mic from direct sled-fan noise.
- **Repeatable geometry:** one defined cradle so *every run and every site* has the
  identical sensor pose — this kills a large, silent source of H2/H3 variance.

### Add external sensors — the clean architecture
One **ESP32-S3 hub** reads a stack of I²C sensors and streams a single,
timestamped frame to the phone. Three transports:

- **BLE** — wireless, low-power, `react-native-ble-plx`. **The reliable path on
  iPhone** (this is how the planned ESP32+BME280 connects). Start here.
- **USB-C** — wired, powered, higher bandwidth. **Easier on Android** (USB-host/OTG
  is open); on **iOS, USB serial/UVC is restricted** (MFi), so treat USB-C as an
  Android convenience or for MFi thermal cams, not the iPhone default.
- **RF (ESP-NOW / LoRa)** — a *multi-node room mesh*: sensor nodes at the vent,
  window, and bench report to the hub → spatial environmental gradients across the
  room (great H3 site characterization). Advanced; later.

### Sensor menu (by covariate)
| Covariate | Part | Notes |
|---|---|---|
| Temp / humidity / pressure | BME280, SHT4x, TMP117 | BME280 already planned; TMP117 for high-accuracy temp |
| CO₂ (true NDIR) | SCD41 | respiration / combustion / occupancy |
| VOC index | SGP40 | air quality |
| Thermal field | MLX90640 (32×24 IR) or FLIR-One (USB-C, MFi on iOS) | the "heat map" input |
| Light quality | AS7341 (spectral), LTR-390 (UV), TSL2591 (lux reference) | validates the phone's EXIF-light hack |
| Airflow | hot-wire wind sensor (e.g. Modern Device Rev P) | key for the drying/evaporation test |
| Depth (no LiDAR) | VL53L5CX (8×8 ToF) | cheap spatial depth if the phone lacks LiDAR |
| Sync | LED / flash / tap fiducial | aligns phone-clock ↔ hub-clock |

### Why it serves the science
Repeatable pose + protected internal sensors + the missing covariates (humidity,
CO₂, VOC, airflow, precise & spatial temperature, spectral light) turn the phone
from an ambient logger into a proper **multi-covariate bench instrument** — and
site differences (H3) get characterized in far more detail than five phone
channels alone can manage.
