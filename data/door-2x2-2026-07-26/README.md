# Two-device door run — 2026-07-26 evening (Chicago; filenames are UTC)

Session exports from the paired iPhone X + iPad Pro recording that produced the
report's cross-device results (Section 5.2 of the final report).

- `covariate_door_close_...T04-01-37-274Z.json` and `...T04-01-37-350Z.json` —
  the main paired sessions, started by hand 76 ms apart, one per device.
  24 door events, half with a dehumidifier running (the 2x2 design).
- `covariate_door_close_...T03-51-09-631Z.json` and `...T03-51-09-714Z.json` —
  a short paired check run recorded just before the main sessions.
- `covariate_door_close_...T03-47-46-663Z.json` and
  `covariate_door_slam_...T02-27-15-412Z.json` — single-device setup runs.

These recordings predate the elapsed-timer fix (e34eb0c); see the report's
Sections 5.2 and 5.5 for how that is handled. Analysis: `analysis/reliability.py`.
