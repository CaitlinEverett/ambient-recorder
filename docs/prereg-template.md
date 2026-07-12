# Pre-registration — H1-H3 (freeze before ANY study data is collected)

Status: TEMPLATE — due Wed Jul 22 (Caitlin), committed before calibration runs.
Once frozen, this file is amended only by addendum, never edited.

## H1 — context sensitivity
Per device, one-sided test: disturbed-run channel activity exceeds the same
phone's controlled-run 95th-percentile baseline.
- Channels & metrics: accelerometer vibration RMS (window: __ s), light level,
  barometer transient magnitude. FROZEN VALUES: __
- Baseline source: first controlled run.

## H2 — cross-device agreement
Per sensor, two phones on the same Table-1 event: Pearson r >= 0.9 AND bias
within the channel's at-rest noise floor.
- Alignment: shared timing fiducial (tap/flash) at session start; report
  measured offset. Resampling method for correlation: __
- A channel failing H2 is flagged untrustworthy, not dropped (negative results count).

## H3 — cross-site reproducibility
Fixed protocol across three sites gives measurably different outcomes; between-
site variance shrinks when a logged covariate is included.
- Primary regression: tablet dissolution time ~ water temperature. FROZEN: __
- Sites: Chicago (CE), __ (CK), __ (third per proposal).

## Table 1 — ground-truth events (freeze before disturbed runs)
| event | channels exercised | metric |
|---|---|---|
| door open/close | barometer | transient magnitude, agreement |
| timed vibration (phone motor on table) | accelerometer | RMS, agreement |
| light on/off | light | step size, agreement |
| tone at fixed volume/distance | micLevel | level, agreement |
| magnet pass at fixed distance | magnetometer | peak, agreement |
