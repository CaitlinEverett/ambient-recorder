# Team 42 — Covariate · To-Do

**Live board (canonical):** [GitHub Project #3](https://github.com/users/CaitlinEverett/projects/3)
— grouped by Phase, with Due dates and Owner. This file is a flat mirror for
quick reading and diffs; when they disagree, the Project wins.

**Team:** Caitlin Everett (CE), Chris Kimberley (CK). ★ = CK's extra scope
(offsets the proposal submission, per Ishita's 7/12 note).

## Fixed course deadlines

| Date | Deliverable |
|---|---|
| Sun Jul 12 | Team contract / project plan submitted |
| Tue Jul 14 / 21 / 28 | Weekly update email to Ishita + Teams notes current |
| Mon Jul 27 | Demo |
| Tue Aug 4 | Final report |

## Confirm — due Sun Jul 12 (blocking)

- [ ] **0a** Read full project prompt + submitted proposal, end to end — CK
- [ ] **0b** Confirm device: iPhone or Android? (changes the plan) — CK
- [ ] **0c** Confirm city (multi-site) + can run kitchen protocol Jul 25–26 — CK
- [ ] **0d** Team contract drafted from list + submitted; emailed to Ishita — Both (CE submits)
- [ ] **0e** Send GitHub username to be added to the private repo — CK

## Week 1 — building blocks (Jul 13–19)

- [ ] Jul 13 — Order ESP32 + BME280 parts (★) — CK
- [ ] Jul 14 — Decide framework (Flutter/RN) + stand up toolchain (Flutter/Xcode/Android SDK) — Both
- [ ] Jul 14 — Weekly update email to Ishita — CE
- [ ] **Jul 15 — Vibration meter hack reimplemented (★)** — first checkpoint — CK
- [ ] Jul 17 — Light/noise logger hack reimplemented (★) — CK
- [ ] Jul 19 — Multi-sensor logging harness: 5 channels on shared clock + health — CE
- [ ] Jul 20 — Status lines for Tue update on Teams notes page — CK

## Week 2 — app, pre-registration, data collection (Jul 20–26)

- [ ] Jul 21 — Weekly update email to Ishita — CE
- [ ] Jul 22 — Pre-registration doc: H1–H3, metrics, Table-1 events frozen — CE
- [ ] Jul 23 — Recorder app on the harness: session model, experiment-linked export — CE
- [ ] Jul 24 — ESP32 + BME280 firmware broadcasting temp/humidity/pressure over BLE (★) — CK
- [ ] Jul 25 — Co-located calibration runs: two phones, Table-1 events — Both (CE leads)
- [ ] Jul 26 — Multi-site kitchen runs, controlled + disturbed (each their site) — Both
- [ ] Jul 26 — Barometer vs BME280 cross-check data (★) — CK
- [ ] Jul 27 — Status lines for Tue update — CK

## Week 3 — analysis, demo (Jul 27–31)

- [ ] Jul 26 — Demo video draft (★): app, hacks, live disturbed-run detection — CK
- [ ] **Jul 27 — Demo submitted** — Both (CE reviews)
- [ ] Jul 28 — Weekly update email to Ishita — CE
- [ ] Jul 29 — Labeled dataset packaged for release (★): naming, README, schema — CK
- [ ] Jul 31 — Reliability analysis: inter-device r, bias, noise floor; H1–H3 (results.csv + notebook) — CE

## Wrap — final report (Aug 1–4)

- [ ] Aug 1 — Report sections for Chris-built pieces (★): hacks, ESP32, dataset — CK
- [ ] Aug 2 — Report sections: intro/background, study design, results, discussion — CE
- [ ] Aug 3 — Full report assembled, ACM format; both read end to end — CE
- [ ] **Aug 4 — Final report submitted; app + schema released open-source** — CE

## Notes

- Nothing on CE's critical path (harness → app → analysis → report) depends on a
  ★ item landing first. If a ★ item slips, scope contracts to the proposal's core.
- **Cross-platform pivot (7/12):** recorder moving to a cross-platform UI (Flutter
  recommended) so it runs on either teammate's phone — pending 0b. Sensors stay
  native behind platform channels; the v0.1.1 JSON schema is the contract. Native
  Swift skeleton kept on `main` as a fallback; rewrite on `crossplatform-rewrite`.
  See `docs/architecture.md` (on the branch).
