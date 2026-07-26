# Pilot — door open / close / slam, 2026-07-25

Six sessions, one iPhone X (iOS 16.7.16), one room, one operator (CK).
Schema v0.1.1. Two baselines, two normal door closes, two hard slams.
Protocol: phone flat on a stable surface, 3-tap sync fiducial, door action,
short hold, stop and export.

**Status: exploratory.** Collected before `docs/prereg.md` was frozen. It
generated hypotheses (H4, H5) and one frozen preprocessing rule (the barometer
warm-up discard); it is not evidence for any of them. Nothing here belongs in
the confirmatory family.

## Reanalysis, 2026-07-26

Reproduce with `analysis/figures.py` and `analysis/events.py`. Event times were
recovered blind — `regimes.detect_events` with no labels — and match the
operator's noted times.

| session | event t (s) | vib peak (g) | raw max(|a|-1) (g) | notes |
|---|---|---|---|---|
| BASE1 | 10.54 | 0.0032 | 0.0031 | marginal candidate at 2.1x floor; real event or false positive, unresolved |
| BASE2 | — | — | — | detector returns nothing, correctly |
| CLOSE1 | 8.92 | 0.0210 | 0.0080 | |
| CLOSE2 | 8.79 | 0.0224 | 0.0081 | |
| SLAM1 | 7.69 | 0.0433 | 0.0111 | |
| SLAM2 | 7.83 | 0.1695 | 0.0613 | 3.9x SLAM1 on peak; the operator's arm, not the sensor |

Baseline floors (median over both baselines): peak 1.54e-3 g, energy 5.93e-7
g^2*s, raw accel 2.00e-3 g.

**Findings that survived checking:**

1. **The derived vibration channel beats the raw accelerometer it derives from**
   by 3.4-5.1x in SNR. Raw magnitude peaks at 1.011 g during a slam - 1.1% above
   gravity - because gravity is a large constant the transient has to compete
   with. Subtracting it is the whole trick. (fig2)
2. **Metric choice changes the margin, not the ordering.** All three statistics
   put close below slam. The gap between the loudest close and the quietest slam
   is 1.38x on window RMS, 1.94x on peak, 2.70x on the energy integral. The
   original write-up used window RMS, a 200 ms average that dilutes a ~50 ms
   impact by wherever the window boundary falls. (fig1)
3. **At n=2 none of this is significant** and could not have been: the smallest
   p an exact permutation test can return with two per condition is 0.167.
   `docs/prereg.md` now fixes n=6.
4. **The sync taps were never lost.** The original write-up reported one of three
   visible. All six sessions carry 3-5 clean taps in the 50 Hz accelerometer;
   three raps inside a few hundred ms collapse into one or two windows of the
   5 Hz derived channel, which is where they were looked for. (fig3)
5. **Barometer: warm-up, not signal.** The rise over a session is +0.15 hPa in a
   baseline and +0.15 hPa in a slam - indistinguishable - on 12-17 samples per
   session. Frozen as a 60 s discard rule, not reported as a result.
6. **Magnetometer: clean null.** Event-window deviations (0.31-0.56 uT) are
   smaller than the spread within a single baseline session (1.03 uT). Expected;
   no ferrous mass moves near the phone. Reported as a negative result.
7. **Ring-down is 164-321 ms**, measurable on the 50 Hz accelerometer and not at
   all on the 5 Hz derived channel - an argument for exporting both.

## Known defect in this dataset

**Every session is labelled `condition: controlled`, including both slams.** The
app accepted the whole dataset mislabelled without warning. Left uncorrected here
so the defect is on the record; the manifest carries the true condition. This is
a product finding, not a transcription error - a recorder built to capture what
nobody wrote down allowed something not to be written down.
