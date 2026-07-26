# Analysis

Python analysis for the pre-registered tests in `docs/prereg.md`.

    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt

## events.py — the pre-registered analysis

Every window, metric, and test in `events.py` is specified in `docs/prereg.md`
and carries a `PREREG` comment naming the section it comes from. Changing one
without a dated addendum to the pre-registration defeats the point of having
frozen it.

    python events.py session path/to/covariate_<id>_<stamp>.json
    python events.py batch manifest.csv

`session` prints channel health against the O1 gate (`dropFraction < 0.02` over
>= 30 min), the detected sync fiducials, and the session's baseline floor. Run
it on every session as it comes off the phone — it is the fastest way to catch a
run that has to be discarded while the apparatus is still set up.

`batch` runs H1, H3a, H4 and H5 across a set of sessions, applies the frozen
exclusion rules, and writes `exclusions.csv` next to the manifest.

### manifest.csv

    file,protocol,condition,level,event_times,exclude
    PEND-45-01.json,pendulum,disturbed,45,14:03:22;14:03:37;14:03:52,
    PEND-CTRL-01.json,pendulum,controlled,,60;75;90,
    PEND-45-02.json,pendulum,disturbed,45,14:11:04,phone bumped mid-trial

- `level` — the dose: release angle in degrees, grams of NaHCO3, centimetres.
  Blank for controlled runs.
- `event_times` — `;`-separated. Bare numbers are session-relative seconds;
  anything with a colon is read as wall clock and converted using the session's
  `startedAtWall`. Write clock times in the field notes; they work directly.
- `exclude` — any non-empty reason drops the trial under PREREG 2.5. Fill this
  in from the field notes **before** running the analysis. Exclusions decided
  after seeing a metric are not exclusions, they are results-shopping.

## make_synthetic.py — the test harness

Generates synthetic sessions with known ground truth, so the analysis is known
to run correctly before any real data exists.

    python make_synthetic.py && python events.py batch synth/manifest.csv

Ground truth: impulse amplitude scales as `(1 - cos theta) ** 0.8`, and `E_vib`
goes as amplitude squared, so a correct H3a fit recovers a slope near 1.6
(deflated at the lowest doses, where the noise floor contributes). Event times
carry sub-window jitter on purpose — without it, events land on the same 200 ms
window phase every time and the harness cannot exercise the alignment effect H5
exists to test.

The harness is a simulation with an invented noise structure. It verifies that
the code runs and that the estimators recover a known slope. It is not evidence
about the physical system, and no result from it belongs in the paper.

## regimes.py — the other five analysis regimes

`events.py` covers one regime: did a discrete thing happen, and how big was it.
`regimes.py` adds spectral, periodicity, stability, blind detection,
classification, and external-reference validation. Protocols that feed them are
P5-P11 in `../../Protocols_Analysis_Regimes.md`.

    python regimes.py path/to/session.json     # every regime the session supports
    python test_regimes.py                     # 15 ground-truth checks

**Everything in regimes.py is EXPLORATORY** with respect to `docs/prereg.md`,
whose confirmatory family (H1/H3a/H4/H5) was fixed in advance and admits nothing
afterwards. Report these results labelled as exploratory, or promote one by dated
addendum written before the data it governs is collected.

`test_regimes.py` plants known values and requires them back: a 7 Hz tone, a
0.30 s decay, a 300 s / 40%-duty compressor cycle, textbook Allan slopes of -0.5
and +0.5, 8 unlabelled events, three event classes separable only by frequency and
decay, and a 21.7 hPa barometric offset implying 180 m. Run it after any change.

### Two traps it exists to catch

**Never take a spectrum of acceleration magnitude.** A flat phone holds ~1 g on z,
so a vibration `s` along x gives `|a| = sqrt(s^2+1) ~= 1 + s^2/2` — the motion
enters squared, and squaring a sinusoid doubles its frequency. A real 7 Hz
vibration reads as 14 Hz, with a clean-looking sharp peak. `regimes.py` works per
axis and sums the spectra; the test asserts 7 Hz in, 7 Hz out. `events.py`'s
`accel_excess_series` is both a magnitude and rectified, which is fine there
because detection only asks "how far from rest", never "at what frequency".

**Nyquist is 25 Hz.** 60 Hz machinery folds to 10 Hz and its second harmonic to
20 Hz, both inside the band and both looking real. `spectral_peaks()` flags peaks
near those frequencies and declines to name them.

## reliability.py — H2 metric definitions

Pearson r, bias, and noise floor for cross-device agreement. Alignment against
the sync fiducial lands with the first dual-device session.
