# Pre-registration — Covariate H1–H5

**Status: FROZEN 2026-07-26, before any Week-3 data collection.**
Supersedes `prereg-template.md`. Amended only by dated addendum appended below —
never by editing text above the addendum line.

Frozen by: Caitlin Everett (Team 42, CS-7470).
Data collected under this document: protocols P0–P4 in `Protocols_Week3_Household.md`.

---

## 0. Why this document exists, and what changed

The Week-2 door pilot (6 sessions, iPhone X, one site) was **exploratory**. It
generated three observations that were not predicted in advance:

1. the derived `vibration` channel detected door events at 13–109× baseline while raw
   accelerometer magnitude moved only 1–4% above gravity;
2. a smooth 6–8 s barometric rise appeared in every session including both baselines,
   i.e. sensor warm-up, not signal;
3. within-condition variance for "slam" (5.97×) exceeded the close-vs-slam gap (1.39×).

Exploratory findings are hypotheses, not results. **This document converts them into
confirmatory tests on data that does not yet exist.** Observations (1) and (3) become
H4 and H5 below. Observation (2) becomes a frozen preprocessing rule (§2.3), not a
result — a preprocessing choice made after seeing data is only legitimate if it is
frozen before the *next* data.

H3 has also been restructured. The original H3 asked a three-site, one-participant-per-site
design to support a claim about between-site variance reduction. It cannot: participant,
location, device model, housing, and ambient conditions are fully confounded at n=1 per
site. H3 is therefore split into **H3a** (within-site dose–response, powered, carries the
quantitative claim) and **H3b** (multi-site, explicitly descriptive). This change was
made in response to reviewer feedback and *before* collecting the data it governs.

---

## 1. Sample size, frozen in advance

For an exact permutation / Mann–Whitney test the smallest attainable one-tailed
p-value is `1 / C(n₁+n₂, n₁)`:

| n per group | splits | min attainable p |
|---|---|---|
| 2 | 6 | 0.167 — significance impossible |
| 3 | 20 | 0.050 — only under perfect separation |
| 4 | 70 | 0.014 |
| **6** | **924** | **0.001** |

**Frozen: n = 6 trials per condition** for all vibration and magnetometer protocols;
**n = 4 per dose** for the CO₂ protocol (slower per trial, larger effect, and the
dose–response regression rather than a pairwise test carries the inference there).

**Stopping rule: fixed n. No optional stopping, no peeking, no adding trials after
inspecting results.** If a trial is excluded under §2.5, it is *not* replaced; the
reduced n is reported.

---

## 2. Preprocessing — frozen before data

### 2.1 Channels and units

| channel | values | rate |
|---|---|---|
| `accelerometer` | `[x, y, z]` g | 50 Hz |
| `vibration` | `[rms, peak]` g | 5 Hz (200 ms window, gravity-removed) |
| `magnetometer` | `[x, y, z]` µT | 25 Hz |
| `barometer` | `[pressure, relAltitude]` hPa, m | event-driven |

### 2.2 Event localisation

Events are located from the experimenter's written clock times, refined to the nearest
local maximum of `accelerometer` magnitude-minus-gravity within ±2 s of the noted time.
Refinement uses the **50 Hz accelerometer**, never the 5 Hz `vibration` channel.

Sync fiducials are detected the same way: three impulses ≥0.5 s and ≤2.0 s apart within
the first 30 s of a session.

### 2.3 Barometer warm-up exclusion

**The first 60 s of every session is discarded from all barometer analysis.** Justified
by the pilot's warm-up transient appearing in baseline sessions where nothing occurred.
Barometer-bearing protocols record ≥60 s of lead-in before the first event.

This rule does not apply to accelerometer, vibration, or magnetometer channels.

### 2.4 Primary and secondary metrics

**Vibration — primary metric, event energy:**

```
E_vib = Σ rms_i² · Δt_i      over  t ∈ [t_e − 0.25 s, t_e + 0.75 s]
```

units g²·s, where `Δt_i` is the interval to the preceding `vibration` sample. Chosen
because it is invariant to where the 200 ms window boundary falls relative to a short
impulse; a peak-of-window-RMS statistic is not, and window-boundary luck is a plausible
mechanism for the pilot's 5.97× within-slam spread.

**Vibration — secondary metric, event peak:** `max(values[1])` over the same window.

**Baseline floor:** median `E_vib` over all 1 s windows in the matched controlled run,
excluding any window within 2 s of a fiducial. **SNR** = `E_vib(event) / floor`.

**Raw accelerometer comparison metric (for H4):** `max(|a| − 1) ` over the event window,
in g, where `|a| = √(x²+y²+z²)`. Its floor is the median of the same statistic over 1 s
windows of the matched controlled run.

**Barometer:** `ΔP = max |P(t) − P_pre|` over `[t_e, t_e + 180 s]`, where `P_pre` is the
median pressure over the 20 s preceding `t_e`. Sign retained and reported.

**Magnetometer:** `ΔB = max |‖B(t)‖ − ‖B‖_pre|` over `[t_e − 0.5, t_e + 1.5]`, `‖B‖_pre`
the median over the preceding 10 s.

### 2.5 Exclusion rules — frozen, applied blind to outcome

A trial is excluded if and only if:

- the experimenter's contemporaneous notes record the phone being moved, touched, or
  bumped during the trial window;
- a noted external disturbance (person entering, vehicle, appliance start) overlaps
  `[t_e − 1 s, t_e + 2 s]`;
- the session's `health[].dropFraction` for the channel under test exceeds 0.05;
- no fiducial is detectable in the session;
- for pendulum trials, the release was noted as pushed rather than clean, or the
  weight struck twice.

Exclusions are applied from the notes and health record **before** any metric is
computed, are logged with reason in `analysis/exclusions.csv`, and are reported in the
paper with their count. **No exclusion may be made on the basis of a metric value.**

### 2.6 Run order

Dose levels are run in **randomised order**, not monotonically. A monotonic order
confounds dose with any drift in temperature, technique, apparatus, or sensor state.
The realised order is recorded in each session's `notes`.

---

## 3. Hypotheses

### H1 — Context sensitivity (per device)

Disturbed-run event energy exceeds the same phone's matched controlled-run baseline.

- **Metric:** `E_vib` (§2.4).
- **Test:** one-tailed exact permutation test, disturbed vs controlled, n=6 each.
- **Threshold:** p < 0.05 after Holm correction (§5).
- **Also reported:** SNR, and the fraction of disturbed trials exceeding the controlled
  run's 95th percentile.

### H2 — Cross-device agreement

Two phones recording the same physical event agree.

- **Alignment:** the physical fiducial (§2.2), not wall-clock. Measured offset reported.
  Where the in-app Mark Sync marker is available it provides the ground-truth timestamp
  on the emitting device; the receiving device is aligned by cross-correlation of its
  accelerometer against the emitted pattern.
- **Metric:** Pearson r on the resampled common grid (linear interpolation to 50 Hz for
  accel, 5 Hz for vibration), plus bias = mean(a − b).
- **Threshold:** r ≥ 0.9 **and** |bias| ≤ max(noise floor of the two devices).
- **A channel failing H2 is flagged untrustworthy, not dropped. Negative results count.**
- **Honest scope note, frozen now:** as of freezing, only one device reliably runs the
  app; the teammate's devices did not complete tooling setup. If no dual-device data is
  obtained, **H2 is reported as untested, not as unsupported, and not quietly dropped.**

### H3a — Within-site dose–response (primary quantitative claim)

Vibration energy increases monotonically and predictably with calibrated impact energy.

- **Design:** pendulum ladder, `E_impact = m·g·L·(1 − cos θ)`, 5 levels × 6 trials, one
  site, one device, one surface, randomised order.
- **Model:** OLS of `log₁₀ E_vib` on `log₁₀ E_impact`, n=30.
- **Pre-registered prediction:** slope > 0, and the 95% CI on the slope excludes 0.
- **Reported:** slope with 95% CI, R², residual plot, and the **detection floor** —
  the lowest impact energy whose 6 trials still separate from the controlled run at
  p < 0.05.
- Directionality is predicted; the *value* of the slope is estimated, not predicted.

### H3b — Multi-site (descriptive, explicitly not a variance claim)

A fixed protocol run at multiple sites produces visibly different ambient traces, and
the logged covariates differ in identifiable ways.

- **Claimed:** the recorder runs on heterogeneous devices at heterogeneous sites;
  ambient baselines differ; the covariates that differ can be named.
- **Explicitly NOT claimed:** that including a logged covariate reduces general
  between-site variance. With one participant per site, participant, device model,
  building, and ambient conditions are fully confounded, and no design of this size can
  separate them.
- **Reported as:** a case series with per-site descriptive statistics. No inferential
  test is run and no p-value is reported for H3b.

### H4 — Derived-channel advantage (confirmatory; exploratory in the pilot)

The derived `vibration` channel detects mechanical events at a higher signal-to-noise
ratio than the raw accelerometer it is derived from.

- **Metric:** `SNR_vib` vs `SNR_accel` (§2.4), computed per trial on the same events.
- **Test:** one-tailed Wilcoxon signed-rank on the paired per-trial difference
  `log₁₀(SNR_vib) − log₁₀(SNR_accel)`, across all pendulum trials at all levels.
- **Pre-registered prediction:** the difference is positive — the derived channel wins.
- **Mechanism under test:** gravity subtraction removes a large constant offset that
  otherwise buries a small transient. This is the project's central "hack" claim and it
  is here tested on data collected after the prediction was written down.

### H5 — Metric robustness (confirmatory; exploratory in the pilot)

An alignment-invariant statistic is more repeatable than a window-average statistic.

- **Metric:** within-condition coefficient of variation (CV = σ/µ) across the 6 trials
  at each pendulum level, computed for (a) `E_vib`, (b) `max(peak)`, (c) `max(rms)`.
- **Test:** Friedman test across the three statistics over the 5 levels; Wilcoxon
  signed-rank for the pairwise contrast (c) vs (a).
- **Pre-registered prediction:** CV(`max peak`) is the smallest of the three — the
  sample-level peak, which no window boundary can dilute, is the most repeatable
  statistic. The ordering of `E_vib` against `max rms` is **not** predicted.
- **Basis, stated honestly:** a synthetic harness (`analysis/make_synthetic.py`,
  with sub-window jitter on event times) reproduces the alignment effect and gives
  CV(`peak`) < CV(`rms`) < CV(`E_vib`) — the energy integral pays for its
  robustness by integrating a full second of noise. This is a simulation with an
  invented noise structure, not evidence, and it is the reason the prediction names
  only `peak`. `E_vib` remains the primary metric for H1/H3a on physical-
  interpretability grounds; if H5 shows `peak` is materially more repeatable on real
  data, switching primary metrics requires a dated addendum, not a quiet edit.
- If the prediction fails, the pilot's 5.97× within-slam spread is attributable to
  genuine variation in the teammate's arm rather than to metric choice, and the
  paper says so.

### O1 — Sampling health (objective, not a hypothesis)

`dropFraction < 0.02` for every channel over a session of ≥30 minutes.

- **Design:** P0, three unattended sessions ≥45 min at different times of day.
- **Reported:** per-channel `dropFraction`, `maxGap`, and the realised rate against
  `NOMINAL_RATE`, for every session.
- This is a pass/fail engineering gate, reported whether it passes or fails.

---

## 4. Operational definitions

**Controlled** — no deliberate manipulation; occupant still; same surface, same room,
same session length, same device placement as the matched disturbed run; recorded in
the same session block.

**Disturbed** — exactly one manipulation from the table below, at exactly one named
level.

| Disturbance | Standardised by | Levels | n/level | Expected to respond | Expected null |
|---|---|---|---|---|---|
| Pendulum impact | fixed m, L; marked release angle | 5 (15–75°) | 6 | vibration | magnetometer, barometer |
| Door close | marked opening angle, released from rest | 3 | 6 | vibration | magnetometer |
| CO₂ evolution | NaHCO₃ mass on scale; fixed vinegar volume; sealed rigid vessel | 5 (0.05–0.8 g) | 4 | barometer | vibration, magnetometer |
| Magnet pass | fixed magnet; marked distance; constant traverse | 4 (5–30 cm) | 6 | magnetometer | vibration, barometer |
| Ambient (passive) | none; ≥45 min unattended | 1 | 3 sessions | — (characterises floor) | — |

**Expected-null channels are analysed and reported.** A channel that fires when it
should not is as informative as one that fires when it should, and reporting both makes
every run a two-sided test of the recorder rather than a one-sided search for signal.

---

## 5. Multiple comparisons

The confirmatory family is: H1 (per protocol), H3a, H4, H5, plus the expected-null
channel tests. **Holm–Bonferroni correction is applied within this family**, and the
family is fixed by this document — no test added later enters it, and any later test is
reported as exploratory and labelled as such.

H3b and O1 are descriptive and carry no p-values.

---

## 6. What would falsify the project's central claim

Stated in advance, so the paper can be honest either way:

- If **H4 fails** — the derived channel does not beat raw accelerometer SNR — the
  headline "hack" claim is unsupported and the paper reports that.
- If **H3a's slope CI includes 0**, the vibration channel does not track calibrated
  impact energy, and its use as a quantitative covariate is not justified.
- If **O1 fails** at ≥30 min, the recorder is not fit for the long-session use it is
  designed for, and that is a deliverable failure, reported as one.
- If the expected-null channels respond, either the manipulation is not single-variable
  or the recorder is cross-talking; both are reportable defects.

---

## Addenda

*(Append dated, signed amendments below this line. Never edit above it.)*
