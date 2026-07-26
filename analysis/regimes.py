"""Analysis regimes beyond event detection.

`events.py` answers one question — did a thing happen, and how big was it.
That is a single regime, and the P1–P4 protocols all live inside it. This module
adds the other five the recorder's channels can support:

    spectral      what a surface's response looks like in frequency, not amplitude
    periodicity   duty cycles and rhythms hiding in long unattended records
    stability     how long you must average before noise stops dominating
    blind         finding events nobody labelled, then scoring against a sealed log
    external      validating a channel against an authoritative outside reference

**Everything here is EXPLORATORY** with respect to `docs/prereg.md`, which fixes a
confirmatory family of H1/H3a/H4/H5 and admits nothing later into it. Results from
this module are reported as exploratory and labelled as such, or promoted by a
dated addendum written *before* the data they govern is collected. Do not quietly
add them to the confirmatory family — the whole point of §5 is that the family was
fixed in advance.

Protocols that feed these: P5–P10 in `Protocols_Analysis_Regimes.md`.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import signal, stats

from events import Session, load_session, vib_energy

# --- shared helpers ----------------------------------------------------------


def resample(t: np.ndarray, x: np.ndarray, hz: float) -> tuple[np.ndarray, np.ndarray]:
    """Linear-interpolate an irregular series onto an even grid.

    Phone sensor delivery is jittery even when the nominal rate is fixed
    (Peguero et al. 2016) — requested rates are not delivered rates. Every
    spectral and stability method below assumes even spacing, so this is not a
    convenience, it is a correctness requirement.
    """
    if len(t) < 2:
        return np.array([]), np.array([])
    grid = np.arange(float(t[0]), float(t[-1]), 1.0 / hz)
    return grid, np.interp(grid, t, x)


def accel_axes_dynamic(sess: Session) -> tuple[np.ndarray, np.ndarray]:
    """(t, [dx, dy, dz]) — per-axis acceleration with gravity linearly detrended.

    **Spectral analysis must never run on acceleration MAGNITUDE.** This is not a
    style preference, it is arithmetic. A phone lying flat carries ~1 g on z, so
    a small vibration `s` along x gives

        |a| = sqrt(s^2 + 1) ~= 1 + s^2/2

    — the transverse component enters *squared*. Square a sinusoid and you get a
    tone at twice the frequency (and an amplitude that scales quadratically), so
    a real 7 Hz vibration is reported at 14 Hz by any magnitude-based spectrum.
    A 60 Hz appliance would be read at 120 Hz, alias to 20 Hz instead of 10 Hz,
    and be attributed to the wrong harmonic. The error is invisible: the spectrum
    looks clean, the peak is sharp, and the number is simply wrong by 2x.

    `events.accel_excess_series` has the same problem twice over — it is both a
    magnitude and rectified — which is fine, because event detection only asks
    "how far from rest", never "at what frequency".

    Working per axis avoids it entirely: each axis is linear in the motion, so
    frequencies survive. Gravity is removed by linear detrending rather than mean
    subtraction, so slow orientation drift over a long record comes out too.
    """
    a = sess.channel("accelerometer")
    if a.empty:
        return np.array([]), np.zeros((0, 3))
    axes = np.column_stack([a["v0"].to_numpy(), a["v1"].to_numpy(), a["v2"].to_numpy()])
    return a["t"].to_numpy(), axes


def vib_series(sess: Session) -> tuple[np.ndarray, np.ndarray]:
    """(t, rms) from the derived vibration channel."""
    v = sess.channel("vibration")
    if v.empty:
        return np.array([]), np.array([])
    return v["t"].to_numpy(), v["v0"].to_numpy()


# --- 1. spectral -------------------------------------------------------------

# The accelerometer is configured at 50 Hz, so the usable band ends at the
# Nyquist frequency of 25 Hz. Anything above it does not vanish — it folds back
# and appears as a spurious lower-frequency peak. Mains-driven machinery at
# 60 Hz aliases to |60 - 50| = 10 Hz; its second harmonic at 120 Hz folds to
# 20 Hz. Both land squarely inside the band and look entirely real. Any peak
# reported near those frequencies must be treated as unidentifiable without an
# independent check, and the honest version of this analysis says so rather than
# claiming to have measured a compressor.
NYQUIST_HZ = 25.0
ALIAS_SUSPECTS = {10.0: "60 Hz mains folded by 50 Hz sampling",
                  20.0: "120 Hz (2nd harmonic) folded by 50 Hz sampling"}


def psd(sess: Session, t0: float | None = None, t1: float | None = None,
        nperseg: int = 256) -> tuple[np.ndarray, np.ndarray]:
    """Welch PSD summed over the three accelerometer axes, g^2/Hz.

    Summing the per-axis spectra keeps the result orientation-independent without
    ever forming a magnitude — see `accel_axes_dynamic` for why that distinction
    decides whether the frequency axis is correct.
    """
    t, axes = accel_axes_dynamic(sess)
    if t.size == 0:
        return np.array([]), np.array([])
    if t0 is not None:
        m = (t >= t0) & (t <= (t1 if t1 is not None else t[-1]))
        t, axes = t[m], axes[m]
    if t.size < 4:
        return np.array([]), np.array([])
    total = None
    for k in range(3):
        grid, x = resample(t, axes[:, k], 50.0)
        if grid.size < 16:
            return np.array([]), np.array([])
        f, pk = signal.welch(signal.detrend(x, type="linear"), fs=50.0,
                             nperseg=int(min(nperseg, grid.size)))
        total = pk if total is None else total + pk
    return f, total


def spectral_peaks(f: np.ndarray, p: np.ndarray, n: int = 3,
                   fmin: float = 1.0) -> list[dict]:
    """Top-n PSD peaks above fmin, each flagged if it sits on an alias suspect."""
    if f.size == 0:
        return []
    m = f >= fmin
    f, p = f[m], p[m]
    idx, _ = signal.find_peaks(p)
    if idx.size == 0:
        return []
    order = idx[np.argsort(p[idx])[::-1]][:n]
    out = []
    for i in sorted(order, key=lambda j: f[j]):
        peak = {"freq_hz": round(float(f[i]), 2), "power": float(p[i]),
                "prominence_vs_median": float(p[i] / np.median(p)), "alias_warning": None}
        for a, why in ALIAS_SUSPECTS.items():
            if abs(peak["freq_hz"] - a) < 1.0:
                peak["alias_warning"] = why
        out.append(peak)
    return out


def spectral_centroid(f: np.ndarray, p: np.ndarray, fmin: float = 1.0) -> float:
    """Power-weighted mean frequency, Hz. A one-number summary of 'brightness'."""
    if f.size == 0:
        return float("nan")
    m = f >= fmin
    return float(np.sum(f[m] * p[m]) / np.sum(p[m])) if p[m].sum() > 0 else float("nan")


def decay_tau(sess: Session, t_e: float, window: float = 2.0) -> float:
    """Exponential decay constant of the vibration envelope after an impulse, s.

    A ringing surface and a dead one can deliver identical peak amplitude and be
    told apart entirely by how long they ring — so tau is information the energy
    integral throws away. Fitted as an OLS line through log(rms) from the peak
    onward, over samples still above the pre-event floor.
    """
    t, rms = vib_series(sess)
    if t.size == 0:
        return float("nan")
    m = (t >= t_e - 0.25) & (t <= t_e + window)
    ts, xs = t[m], rms[m]
    if ts.size < 4:
        return float("nan")
    k = int(np.argmax(xs))
    ts, xs = ts[k:], xs[k:]
    floor = float(np.median(rms[t < t_e - 1.0])) if (t < t_e - 1.0).any() else 0.0
    keep = xs > max(floor * 2.0, 1e-9)
    if keep.sum() < 4:
        return float("nan")
    r = stats.linregress(ts[keep] - ts[keep][0], np.log(xs[keep]))
    return float(-1.0 / r.slope) if r.slope < 0 else float("nan")


# --- 2. periodicity ----------------------------------------------------------


def dominant_period(t: np.ndarray, x: np.ndarray,
                    min_period: float = 60.0,
                    max_period: float | None = None) -> dict:
    """Strongest repeat interval in a long record, by autocorrelation.

    Aimed at machinery duty cycles — a compressor that runs 8 minutes in every
    30 is a periodic disturbance the occupant has completely stopped noticing,
    which is the project's thesis sitting in the kitchen.
    """
    if t.size < 10:
        return {"period_s": float("nan"), "strength": float("nan")}
    hz = 1.0
    grid, xs = resample(t, x, hz)
    span = grid[-1] - grid[0]
    max_period = max_period or span / 3.0
    if span < 3 * min_period:
        return {"period_s": float("nan"), "strength": float("nan"),
                "note": f"record is {span:.0f} s; need >= {3*min_period:.0f} s"}
    xs = xs - xs.mean()
    ac = np.correlate(xs, xs, mode="full")[len(xs) - 1:]
    ac /= ac[0] if ac[0] != 0 else 1.0
    lags = np.arange(len(ac)) / hz
    band = (lags >= min_period) & (lags <= max_period)
    if not band.any():
        return {"period_s": float("nan"), "strength": float("nan")}
    i = int(np.argmax(ac[band]))
    return {"period_s": round(float(lags[band][i]), 1),
            "strength": round(float(ac[band][i]), 3),
            "searched_s": (min_period, round(float(max_period), 1))}


def duty_cycle(t: np.ndarray, x: np.ndarray, k: float = 3.0) -> dict:
    """On/off statistics for a two-state disturbance.

    'On' is any sample more than k robust standard deviations above the median —
    MAD-based, so a machine that is on half the time doesn't drag the threshold
    up to meet itself.
    """
    if t.size < 10:
        return {}
    med = float(np.median(x))
    mad = float(np.median(np.abs(x - med))) or 1e-12
    on = x > med + k * 1.4826 * mad
    runs, cur, start = [], on[0], t[0]
    for i in range(1, len(on)):
        if on[i] != cur:
            runs.append((cur, float(t[i] - start)))
            cur, start = on[i], t[i]
    runs.append((cur, float(t[-1] - start)))
    on_d = [d for s, d in runs if s]
    off_d = [d for s, d in runs if not s]
    return {"on_fraction": round(float(on.mean()), 4),
            "n_on_periods": len(on_d),
            "mean_on_s": round(float(np.mean(on_d)), 1) if on_d else float("nan"),
            "mean_off_s": round(float(np.mean(off_d)), 1) if off_d else float("nan"),
            "threshold": med + k * 1.4826 * mad}


# --- 3. stability ------------------------------------------------------------


def allan_deviation(x: np.ndarray, tau0: float,
                    taus: np.ndarray | None = None) -> pd.DataFrame:
    """Overlapping Allan deviation — the metrologist's averaging-time curve.

    Answers a question no single-number noise floor can: *how long should a
    measurement be?* White noise falls as tau^-0.5, so averaging helps; drift
    rises as tau^+0.5, so averaging hurts. The minimum between them is the
    optimal integration time, and it is a per-channel property of the device.

    This is the same tool used to specify oscillators and inertial sensors, and
    it connects directly to the metrology framing in the Background — ISO/IEC
    17025 and NISTIR 6969 both assume you know how stable your instrument is
    over the duration of a measurement.
    """
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 16:
        return pd.DataFrame(columns=["tau_s", "adev", "n_pairs"])
    if taus is None:
        mmax = n // 4
        ms = np.unique(np.round(np.logspace(0, math.log10(max(mmax, 2)), 25)).astype(int))
    else:
        ms = np.unique((np.asarray(taus) / tau0).round().astype(int))
    rows = []
    for m in ms[ms >= 1]:
        k = n // m
        if k < 3:
            continue
        avgs = x[: k * m].reshape(k, m).mean(axis=1)
        d = np.diff(avgs)
        rows.append({"tau_s": float(m * tau0),
                     "adev": float(np.sqrt(0.5 * np.mean(d ** 2))),
                     "n_pairs": int(len(d))})
    return pd.DataFrame(rows)


def optimal_averaging_time(adev: pd.DataFrame) -> dict:
    """The tau at which Allan deviation bottoms out, and the noise floor there."""
    if adev.empty:
        return {}
    i = int(adev["adev"].idxmin())
    return {"tau_s": float(adev.loc[i, "tau_s"]),
            "adev_at_min": float(adev.loc[i, "adev"]),
            "adev_at_1s": float(adev.iloc[0]["adev"])}


# --- 4. blind detection ------------------------------------------------------


def detect_events(sess: Session, k: float = 6.0,
                  refractory: float = 3.0, skip: float = 30.0) -> list[float]:
    """Find events with NO labels — the detector never sees the truth log.

    Threshold is median + k*MAD of the whole record's vibration RMS, so it is
    set by the session's own quiet background rather than by anything the
    analyst knows about when things happened. `skip` drops the opening seconds
    where the sync fiducial lives.
    """
    t, rms = vib_series(sess)
    if t.size == 0:
        return []
    m = t >= skip
    t, rms = t[m], rms[m]
    if t.size < 10:
        return []
    med = float(np.median(rms))
    mad = float(np.median(np.abs(rms - med))) or 1e-12
    thresh = med + k * 1.4826 * mad
    out: list[float] = []
    for i in range(len(t)):
        if rms[i] > thresh and (not out or t[i] - out[-1] > refractory):
            out.append(float(t[i]))
    return out


def score_detections(predicted: list[float], truth: list[float],
                     tol: float = 2.0) -> dict:
    """Precision / recall / F1 / timing error against a sealed truth log.

    Greedy nearest-match within tol. This is the metric that separates 'we
    detected the event we caused' from 'the recorder found what nobody told it',
    and only the second one is evidence the thing works in the field.
    """
    pred, tru = sorted(predicted), sorted(truth)
    used, errs = set(), []
    for p in pred:
        cands = [(abs(p - x), j) for j, x in enumerate(tru)
                 if j not in used and abs(p - x) <= tol]
        if cands:
            d, j = min(cands)
            used.add(j)
            errs.append(p - tru[j])
    tp = len(used)
    fp, fn = len(pred) - tp, len(tru) - tp
    prec = tp / len(pred) if pred else float("nan")
    rec = tp / len(tru) if tru else float("nan")
    f1 = (2 * prec * rec / (prec + rec)) if tp else 0.0
    return {"tp": tp, "fp": fp, "fn": fn,
            "precision": round(prec, 3) if pred else None,
            "recall": round(rec, 3) if tru else None,
            "f1": round(f1, 3),
            "median_timing_error_s": round(float(np.median(errs)), 3) if errs else None,
            "max_timing_error_s": round(float(np.max(np.abs(errs))), 3) if errs else None}


# --- 5. classification -------------------------------------------------------


FEATURES = ["log_energy", "log_peak", "decay_tau", "centroid", "peak_freq", "rise_ratio"]


def event_features(sess: Session, t_e: float) -> dict:
    """Feature vector for telling *kinds* of event apart, not merely detecting them.

    Deliberately spans regimes: amplitude (energy, peak), time (decay, rise) and
    frequency (centroid, peak). Amplitude alone cannot separate a light tap
    nearby from a heavy one far away; the time and frequency terms can.
    """
    e = vib_energy(sess, t_e)
    p = sess.channel("vibration")
    w = p[(p["t"] >= t_e - 0.25) & (p["t"] <= t_e + 0.75)]
    pk = float(w["v1"].max()) if not w.empty else float("nan")
    # Wider than the energy window on purpose: decay and spectral shape live in
    # the ring-down, which outlasts the 1 s the amplitude metrics care about.
    f, pw = psd(sess, t_e - 0.25, t_e + 1.75, nperseg=128)
    peaks = spectral_peaks(f, pw, n=1)
    pre = p[(p["t"] >= t_e - 1.25) & (p["t"] < t_e - 0.25)]
    return {
        "log_energy": math.log10(e) if e and e > 0 else float("nan"),
        "log_peak": math.log10(pk) if pk and pk > 0 else float("nan"),
        "decay_tau": decay_tau(sess, t_e),
        "centroid": spectral_centroid(f, pw),
        "peak_freq": peaks[0]["freq_hz"] if peaks else float("nan"),
        "rise_ratio": float(pk / pre["v1"].max()) if not pre.empty and pre["v1"].max() > 0 else float("nan"),
    }


def loo_1nn(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, pd.DataFrame, float]:
    """Leave-one-out 1-nearest-neighbour on z-scored features.

    Deliberately the dumbest defensible classifier. With tens of trials per class
    anything with fitted parameters would mostly measure its own capacity; a
    1-NN has none to fit, so the confusion matrix reports how separable the
    features are rather than how flexible the model is. No new dependency.
    """
    X = np.asarray(X, float)
    keep = np.isfinite(X).all(axis=1)
    X, y = X[keep], np.asarray(y)[keep]
    if len(X) < 3:
        return np.array([]), pd.DataFrame(), float("nan")
    Z = (X - X.mean(0)) / np.where(X.std(0) == 0, 1, X.std(0))
    pred = np.empty(len(Z), dtype=y.dtype)
    for i in range(len(Z)):
        d = np.sqrt(((Z - Z[i]) ** 2).sum(1))
        d[i] = np.inf
        pred[i] = y[int(np.argmin(d))]
    labels = sorted(set(y.tolist()))
    cm = pd.DataFrame(0, index=labels, columns=labels)
    for a, b in zip(y, pred):
        cm.loc[a, b] += 1
    cm.index.name, cm.columns.name = "actual", "predicted"
    return pred, cm, float((pred == y).mean())


def chance_rate(y) -> float:
    """Majority-class rate — the number an accuracy must beat to mean anything."""
    v = pd.Series(list(y)).value_counts()
    return float(v.iloc[0] / v.sum()) if len(v) else float("nan")


# --- 6. external reference ---------------------------------------------------


def compare_to_reference(sess: Session, ref: pd.DataFrame,
                         warmup: float = 60.0) -> dict:
    """Validate the phone barometer against a weather-station pressure record.

    `ref` needs columns `t` (seconds since this session's start) and `hPa`.
    Source: api.weather.gov `/stations/<ID>/observations`, field
    `barometricPressure` in Pa (divide by 100). That field is the altimeter
    setting — station pressure already reduced to sea level — so the phone's raw
    reading will sit *below* it by a roughly constant amount set by elevation.

    That offset is the interesting part, not an error to correct away. Near sea
    level 1 hPa is about 8.3 m, so the mean offset implies an altitude, and the
    phone can be checked against the known elevation of the room it is sitting
    in. A slope near 1 says the phone tracks real synoptic pressure change; the
    offset says it knows where it is. This is the only channel in the project
    with an authoritative external reference — everything else is checked
    against itself.
    """
    b = sess.channel("barometer")
    if b.empty or ref.empty:
        return {}
    b = b[b["t"] >= warmup]
    if b.empty:
        return {}
    phone = np.interp(ref["t"].to_numpy(), b["t"].to_numpy(), b["v0"].to_numpy())
    station = ref["hPa"].to_numpy()
    m = np.isfinite(phone) & np.isfinite(station)
    if m.sum() < 3:
        return {"note": f"only {int(m.sum())} overlapping points; need >= 3"}
    r = stats.linregress(station[m], phone[m])
    offset = float(np.mean(phone[m] - station[m]))
    return {"n": int(m.sum()),
            "slope": round(float(r.slope), 4),
            "r2": round(float(r.rvalue ** 2), 4),
            "mean_offset_hPa": round(offset, 3),
            "implied_altitude_m": round(-offset * 8.3, 1),
            "residual_sd_hPa": round(float(np.std(phone[m] - (r.slope * station[m] + r.intercept))), 4)}


def load_nws_observations(path: str, session_start_iso: str) -> pd.DataFrame:
    """Parse a saved api.weather.gov observations JSON into (t, hPa).

    Fetch with a User-Agent naming you and a contact address — the API requires
    one and rejects requests without it:

        curl -H 'User-Agent: covariate-cs7470 (you@example.edu)' \\
          'https://api.weather.gov/stations/KMDW/observations?limit=48' > station.json
    """
    import json
    from datetime import datetime

    start = datetime.fromisoformat(session_start_iso.replace("Z", "+00:00"))
    obs = json.loads(open(path).read()).get("features", [])
    rows = []
    for o in obs:
        p = o["properties"]
        v = (p.get("barometricPressure") or {}).get("value")
        if v is None:
            continue
        ts = datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00"))
        rows.append({"t": (ts - start).total_seconds(), "hPa": v / 100.0})
    return pd.DataFrame(rows).sort_values("t").reset_index(drop=True)


# --- CLI ---------------------------------------------------------------------


def report(path: str) -> None:
    """Run every regime that the session is long enough to support."""
    sess = load_session(path)
    print(f"{sess.meta.get('experimentID')}  ·  {sess.duration/60:.1f} min"
          f"  ·  {sess.meta.get('placement') or 'placement not recorded'}\n")

    f, p = psd(sess)
    if f.size:
        print(f"SPECTRAL  (usable band 0–{NYQUIST_HZ:.0f} Hz)")
        print(f"  centroid {spectral_centroid(f, p):.2f} Hz")
        for pk in spectral_peaks(f, p, n=3):
            warn = f"   ⚠ {pk['alias_warning']}" if pk["alias_warning"] else ""
            print(f"  peak {pk['freq_hz']:6.2f} Hz  ×{pk['prominence_vs_median']:.0f} median{warn}")

    t, rms = vib_series(sess)
    if t.size:
        print("\nPERIODICITY")
        d = dominant_period(t, rms)
        if d.get("note"):
            print(f"  {d['note']}")
        else:
            print(f"  dominant period {d['period_s']:.0f} s  (autocorr {d['strength']:.2f})")
        dc = duty_cycle(t, rms)
        if dc:
            print(f"  on {dc['on_fraction']*100:.1f}% of the record"
                  f"  ·  {dc['n_on_periods']} on-periods"
                  f"  ·  mean on {dc['mean_on_s']:.0f} s / off {dc['mean_off_s']:.0f} s")

        print("\nSTABILITY  (Allan deviation, vibration RMS)")
        ad = allan_deviation(resample(t, rms, 5.0)[1], 0.2)
        o = optimal_averaging_time(ad)
        if o:
            print(f"  adev at 1 s   {o['adev_at_1s']:.3e} g")
            print(f"  minimum       {o['adev_at_min']:.3e} g at tau = {o['tau_s']:.1f} s")
            print(f"  -> averaging beyond {o['tau_s']:.1f} s stops helping; drift takes over")

        print("\nBLIND DETECTION  (no labels used)")
        ev = detect_events(sess)
        print(f"  {len(ev)} candidate events"
              f"{'  ' + str([round(e, 1) for e in ev[:12]]) if ev else ''}"
              f"{' …' if len(ev) > 12 else ''}")
        print("  score against the sealed log with score_detections(ev, truth)")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    report(sys.argv[1])
