"""Event metrics and pre-registered tests for Covariate sessions.

Implements the frozen analysis in docs/prereg.md. Every metric, window, and test
here is specified in that document; this module is the executable form of it and
should not acquire options that the pre-registration does not name.

Two entry points:

    python events.py session covariate_pendulum-45_2026-07-26T....json
    python events.py batch manifest.csv

`session` prints a per-session summary: channel health against the O1 gate,
detected fiducials, and metrics for every event found.

`batch` runs the pre-registered tests across a set of sessions described by a
manifest (see MANIFEST_COLUMNS below), applies the frozen exclusion rules, and
writes exclusions.csv alongside the manifest.

Frozen constants carry a PREREG comment naming the section they come from. Do
not change one without a dated addendum to the pre-registration.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from bisect import bisect_left, bisect_right
from dataclasses import dataclass, field
from datetime import datetime
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

# --- frozen analysis constants (docs/prereg.md) ------------------------------

VIB_PRE = 0.25            # PREREG §2.4 — event window opens 0.25 s before t_e
VIB_POST = 0.75           # PREREG §2.4 — and closes 0.75 s after
BARO_WARMUP_DISCARD = 60.0  # PREREG §2.3 — first 60 s dropped, barometer only
BARO_POST = 180.0         # PREREG §2.4 — pressure plateau window
BARO_PRE_MEDIAN = 20.0    # PREREG §2.4 — pre-event pressure reference
MAG_PRE, MAG_POST = 0.5, 1.5   # PREREG §2.4
MAG_PRE_MEDIAN = 10.0     # PREREG §2.4
EVENT_REFINE_WINDOW = 2.0     # PREREG §2.2 — ±2 s around the noted clock time
FIDUCIAL_SEARCH = 30.0        # PREREG §2.2 — fiducials live in the first 30 s
FIDUCIAL_MIN_GAP, FIDUCIAL_MAX_GAP = 0.5, 2.0   # PREREG §2.2
FLOOR_WINDOW = 1.0        # PREREG §2.4 — baseline floor computed on 1 s windows
FLOOR_FIDUCIAL_GUARD = 2.0    # PREREG §2.4 — floor windows avoid fiducials by 2 s
O1_DROP_GATE = 0.02       # PREREG §O1
O1_MIN_SECONDS = 30 * 60  # PREREG §O1
EXCLUDE_DROP_GATE = 0.05  # PREREG §2.5

MANIFEST_COLUMNS = [
    "file",        # path to the session JSON, relative to the manifest
    "protocol",    # pendulum | door | co2 | magnet | ambient
    "condition",   # controlled | disturbed
    "level",       # numeric dose (angle deg, gram, cm) or blank for controlled
    "event_times",  # ';'-separated. "12.4" = session-relative s; "14:03:22" = clock
    "exclude",     # blank, or a reason string -> trial dropped under PREREG §2.5
]


# --- loading -----------------------------------------------------------------


@dataclass
class Session:
    path: Path
    meta: dict
    health: list[dict]
    samples: pd.DataFrame  # columns: t, channel, v0, v1, v2

    @property
    def started(self) -> datetime:
        return datetime.fromisoformat(self.meta["startedAtWall"].replace("Z", "+00:00"))

    @property
    def duration(self) -> float:
        return float(self.samples["t"].max()) if len(self.samples) else 0.0

    def channel(self, name: str) -> pd.DataFrame:
        d = self.samples[self.samples["channel"] == name]
        return d.sort_values("t").reset_index(drop=True)

    def health_for(self, channel: str) -> dict | None:
        for h in self.health:
            if h["channel"] == channel:
                return h
        return None


def load_session(path: str | Path) -> Session:
    p = Path(path)
    record = json.loads(p.read_text())
    rows = []
    for s in record["samples"]:
        row = {"t": s["t"], "channel": s["channel"]}
        for i, v in enumerate(s["values"]):
            row[f"v{i}"] = v
        rows.append(row)
    df = pd.DataFrame(rows)
    for col in ("v0", "v1", "v2"):
        if col not in df.columns:
            df[col] = np.nan
    return Session(p, record["meta"], record.get("health", []), df)


# --- event localisation (PREREG §2.2) ----------------------------------------


def accel_excess_series(sess: Session) -> tuple[np.ndarray, np.ndarray]:
    """(t, |a| - 1) from the 50 Hz accelerometer, in g.

    Gravity is removed as a constant 1 g rather than by low-pass filtering. The
    recorder's own vibration channel does the filtered version; this is the raw
    comparison metric H4 tests against, and must stay naive on purpose.
    """
    a = sess.channel("accelerometer")
    if a.empty:
        return np.array([]), np.array([])
    mag = np.sqrt(a["v0"] ** 2 + a["v1"] ** 2 + a["v2"] ** 2).to_numpy()
    return a["t"].to_numpy(), np.abs(mag - 1.0)


def refine_event(sess: Session, t_hint: float,
                 window: float = EVENT_REFINE_WINDOW) -> float | None:
    """Snap a noted time to the nearest accelerometer impulse within ±window."""
    t, ex = accel_excess_series(sess)
    if t.size == 0:
        return None
    lo, hi = bisect_left(t.tolist(), t_hint - window), bisect_right(t.tolist(), t_hint + window)
    if hi <= lo:
        return None
    seg = ex[lo:hi]
    return float(t[lo + int(np.argmax(seg))])


def find_fiducials(sess: Session, search: float = FIDUCIAL_SEARCH) -> list[float]:
    """Detect the 3-impulse sync fiducial in the 50 Hz accelerometer.

    Deliberately NOT run on the 5 Hz vibration channel: three raps inside one
    200 ms window collapse into a single sample there, which is the most likely
    explanation for the Week-2 pilot seeing one spike where three were tapped.
    """
    t, ex = accel_excess_series(sess)
    if t.size == 0:
        return []
    m = t <= search
    t, ex = t[m], ex[m]
    if t.size < 10:
        return []
    # Threshold from the robust spread of the search region, not its mean, so a
    # few large impulses don't inflate the very statistic meant to detect them.
    med = float(np.median(ex))
    mad = float(np.median(np.abs(ex - med))) or 1e-9
    thresh = med + 6.0 * 1.4826 * mad

    peaks: list[float] = []
    i = 0
    while i < len(t):
        if ex[i] < thresh:
            i += 1
            continue
        j = i
        while j + 1 < len(t) and t[j + 1] - t[i] < FIDUCIAL_MIN_GAP:
            j += 1
        peaks.append(float(t[i + int(np.argmax(ex[i:j + 1]))]))
        i = j + 1

    # Keep the longest run whose spacing sits inside the frozen tap interval.
    best: list[float] = []
    run: list[float] = []
    for p in peaks:
        if run and not (FIDUCIAL_MIN_GAP <= p - run[-1] <= FIDUCIAL_MAX_GAP):
            if len(run) > len(best):
                best = run
            run = []
        run.append(p)
    return run if len(run) > len(best) else best


# --- metrics (PREREG §2.4) ---------------------------------------------------


def _window(df: pd.DataFrame, t0: float, t1: float) -> pd.DataFrame:
    return df[(df["t"] >= t0) & (df["t"] <= t1)]


def vib_energy(sess: Session, t_e: float,
               pre: float = VIB_PRE, post: float = VIB_POST) -> float:
    """PRIMARY metric. E_vib = Sum rms^2 * dt over the event window, g^2*s.

    Invariant to where the recorder's 200 ms window boundary falls relative to a
    short impulse, which peak-of-window-RMS is not.
    """
    v = sess.channel("vibration")
    if v.empty:
        return float("nan")
    w = _window(v, t_e - pre, t_e + post)
    if w.empty:
        return float("nan")
    idx = w.index
    prev_t = v["t"].reindex(idx - 1).to_numpy()
    dt = w["t"].to_numpy() - prev_t
    nominal = 0.2  # 200 ms window; used only where a preceding sample is absent
    dt = np.where(np.isfinite(dt) & (dt > 0), dt, nominal)
    return float(np.sum(w["v0"].to_numpy() ** 2 * dt))


def vib_peak(sess: Session, t_e: float,
             pre: float = VIB_PRE, post: float = VIB_POST) -> float:
    """SECONDARY metric. max of the per-window peak (values[1]), g."""
    v = sess.channel("vibration")
    w = _window(v, t_e - pre, t_e + post) if not v.empty else v
    return float(w["v1"].max()) if not w.empty else float("nan")


def vib_rms_peak(sess: Session, t_e: float,
                 pre: float = VIB_PRE, post: float = VIB_POST) -> float:
    """The pilot's statistic — max window RMS. Retained only so H5 can test it."""
    v = sess.channel("vibration")
    w = _window(v, t_e - pre, t_e + post) if not v.empty else v
    return float(w["v0"].max()) if not w.empty else float("nan")


def accel_excess(sess: Session, t_e: float,
                 pre: float = VIB_PRE, post: float = VIB_POST) -> float:
    """H4 comparison metric. max(|a| - 1) over the event window, g."""
    t, ex = accel_excess_series(sess)
    if t.size == 0:
        return float("nan")
    m = (t >= t_e - pre) & (t <= t_e + post)
    return float(np.max(ex[m])) if m.any() else float("nan")


def baro_delta(sess: Session, t_e: float) -> float:
    """max |P(t) - P_pre| over the plateau window, hPa. Sign retained."""
    b = sess.channel("barometer")
    if b.empty:
        return float("nan")
    b = b[b["t"] >= BARO_WARMUP_DISCARD]  # PREREG §2.3
    pre = _window(b, t_e - BARO_PRE_MEDIAN, t_e)
    post = _window(b, t_e, t_e + BARO_POST)
    if pre.empty or post.empty:
        return float("nan")
    p0 = float(pre["v0"].median())
    d = post["v0"].to_numpy() - p0
    return float(d[np.argmax(np.abs(d))])


def mag_delta(sess: Session, t_e: float) -> float:
    """max |‖B‖ - ‖B‖_pre| over the event window, uT."""
    m = sess.channel("magnetometer")
    if m.empty:
        return float("nan")
    norm = np.sqrt(m["v0"] ** 2 + m["v1"] ** 2 + m["v2"] ** 2)
    d = pd.DataFrame({"t": m["t"], "b": norm})
    pre = _window(d, t_e - MAG_PRE_MEDIAN, t_e)
    win = _window(d, t_e - MAG_PRE, t_e + MAG_POST)
    if pre.empty or win.empty:
        return float("nan")
    return float(np.max(np.abs(win["b"].to_numpy() - float(pre["b"].median()))))


def baseline_floor(sess: Session, metric: str = "energy") -> float:
    """Median metric over 1 s windows of a controlled session (PREREG §2.4).

    Windows within FLOOR_FIDUCIAL_GUARD of a detected fiducial are skipped — the
    sync taps are deliberate impulses and would otherwise inflate the floor that
    every SNR in the paper is divided by.
    """
    fids = find_fiducials(sess)
    dur = sess.duration
    if dur <= FLOOR_WINDOW:
        return float("nan")
    fn = {"energy": vib_energy, "peak": vib_peak,
          "rms": vib_rms_peak, "accel": accel_excess}[metric]
    vals = []
    centre = FLOOR_WINDOW / 2
    while centre < dur - FLOOR_WINDOW / 2:
        if all(abs(centre - f) > FLOOR_FIDUCIAL_GUARD for f in fids):
            v = fn(sess, centre, pre=FLOOR_WINDOW / 2, post=FLOOR_WINDOW / 2)
            if math.isfinite(v):
                vals.append(v)
        centre += FLOOR_WINDOW
    return float(np.median(vals)) if vals else float("nan")


# --- tests (PREREG §3, §5) ---------------------------------------------------


def exact_permutation_p(a, b, alternative: str = "greater") -> float:
    """One-tailed exact permutation test on the difference of means.

    Enumerates every split, so the returned p is exact rather than sampled. The
    smallest value it can return is 1/C(n_a+n_b, n_a) — 0.167 at n=2 per group,
    which is why the pre-registration fixes n=6 (PREREG §1).
    """
    a, b = np.asarray(a, float), np.asarray(b, float)
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return float("nan")
    pool = np.concatenate([a, b])
    obs = a.mean() - b.mean()
    idx = range(na + nb)
    count = 0
    total = 0
    for combo in combinations(idx, na):
        mask = np.zeros(na + nb, bool)
        mask[list(combo)] = True
        d = pool[mask].mean() - pool[~mask].mean()
        total += 1
        if (d >= obs - 1e-15) if alternative == "greater" else (d <= obs + 1e-15):
            count += 1
    return count / total


def min_attainable_p(na: int, nb: int) -> float:
    """The floor on any exact one-tailed p at these group sizes (PREREG §1)."""
    return 1.0 / math.comb(na + nb, na)


def holm(pvals: dict[str, float]) -> dict[str, float]:
    """Holm-Bonferroni adjusted p-values over the frozen confirmatory family."""
    items = sorted((p, k) for k, p in pvals.items() if math.isfinite(p))
    n = len(items)
    out, running = {}, 0.0
    for i, (p, k) in enumerate(items):
        running = max(running, min(1.0, (n - i) * p))
        out[k] = running
    for k, p in pvals.items():
        out.setdefault(k, float("nan"))
    return out


@dataclass
class Fit:
    slope: float
    intercept: float
    ci: tuple[float, float]
    r2: float
    n: int


def loglog_fit(x, y) -> Fit:
    """OLS of log10(y) on log10(x) with a 95% CI on the slope (PREREG H3a)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
    lx, ly = np.log10(x[m]), np.log10(y[m])
    if len(lx) < 3:
        return Fit(float("nan"), float("nan"), (float("nan"), float("nan")), float("nan"), int(m.sum()))
    r = stats.linregress(lx, ly)
    crit = stats.t.ppf(0.975, len(lx) - 2)
    return Fit(float(r.slope), float(r.intercept),
               (float(r.slope - crit * r.stderr), float(r.slope + crit * r.stderr)),
               float(r.rvalue ** 2), int(len(lx)))


def cv(values) -> float:
    """Coefficient of variation, sigma/mu (PREREG H5)."""
    v = np.asarray(values, float)
    v = v[np.isfinite(v)]
    return float(v.std(ddof=1) / v.mean()) if len(v) > 1 and v.mean() != 0 else float("nan")


def impact_energy(mass_kg: float, length_m: float, angle_deg: float) -> float:
    """Pendulum impact energy, J. E = m*g*L*(1 - cos theta)."""
    return mass_kg * 9.80665 * length_m * (1 - math.cos(math.radians(angle_deg)))


# --- health / O1 -------------------------------------------------------------


def o1_report(sess: Session) -> pd.DataFrame:
    rows = []
    for h in sess.health:
        rate = h.get("nominalRate")
        first, last = h.get("firstT"), h.get("lastT")
        span = (last - first) if (first is not None and last is not None) else 0.0
        realised = h["sampleCount"] / span if span > 0 else float("nan")
        rows.append({
            "channel": h["channel"],
            "n": h["sampleCount"],
            "nominal_Hz": rate,
            "realised_Hz": round(realised, 2) if math.isfinite(realised) else None,
            "maxGap_s": round(h.get("maxGap", float("nan")), 3),
            "dropFraction": round(h.get("dropFraction", float("nan")), 4),
            "O1_pass": (None if not rate else h.get("dropFraction", 1) < O1_DROP_GATE),
        })
    df = pd.DataFrame(rows)
    return df.sort_values("channel").reset_index(drop=True) if not df.empty else df


# --- manifest / batch --------------------------------------------------------


def _parse_event_times(sess: Session, field_value: str) -> list[float]:
    """Accept session-relative seconds ("12.4") or wall clock ("14:03:22")."""
    out = []
    for raw in str(field_value or "").split(";"):
        raw = raw.strip()
        if not raw:
            continue
        if ":" in raw:
            parts = [int(p) for p in raw.split(":")]
            while len(parts) < 3:
                parts.append(0)
            start = sess.started
            noted = start.replace(hour=parts[0], minute=parts[1], second=parts[2], microsecond=0)
            out.append((noted - start).total_seconds())
        else:
            out.append(float(raw))
    return out


@dataclass
class Trial:
    file: str
    protocol: str
    condition: str
    level: float | None
    t_event: float
    metrics: dict = field(default_factory=dict)


def load_manifest(path: str | Path) -> tuple[list[Trial], list[dict]]:
    """Read the manifest, apply the frozen exclusions, return (trials, excluded)."""
    mpath = Path(path)
    trials: list[Trial] = []
    excluded: list[dict] = []
    with mpath.open() as fh:
        for row in csv.DictReader(fh):
            fp = (mpath.parent / row["file"]).resolve()
            if row.get("exclude", "").strip():
                excluded.append({"file": row["file"], "reason": row["exclude"].strip()})
                continue
            if not fp.exists():
                excluded.append({"file": row["file"], "reason": "file not found"})
                continue
            sess = load_session(fp)

            # PREREG §2.5 — health-based exclusion, decided before any metric runs.
            bad = [h["channel"] for h in sess.health
                   if h.get("dropFraction", 0) > EXCLUDE_DROP_GATE]
            if bad:
                excluded.append({"file": row["file"],
                                 "reason": f"dropFraction>{EXCLUDE_DROP_GATE} on {','.join(bad)}"})
                continue
            if not find_fiducials(sess):
                excluded.append({"file": row["file"], "reason": "no fiducial detected"})
                continue

            lvl = row.get("level", "").strip()
            for t_hint in _parse_event_times(sess, row.get("event_times", "")):
                t_e = refine_event(sess, t_hint) or t_hint
                tr = Trial(row["file"], row["protocol"], row["condition"],
                           float(lvl) if lvl else None, t_e)
                tr.metrics = {
                    "E_vib": vib_energy(sess, t_e),
                    "peak": vib_peak(sess, t_e),
                    "rms_peak": vib_rms_peak(sess, t_e),
                    "accel_excess": accel_excess(sess, t_e),
                    "baro_delta": baro_delta(sess, t_e),
                    "mag_delta": mag_delta(sess, t_e),
                }
                trials.append(tr)
    return trials, excluded


def trials_frame(trials: list[Trial]) -> pd.DataFrame:
    return pd.DataFrame([{**{"file": t.file, "protocol": t.protocol,
                             "condition": t.condition, "level": t.level,
                             "t_event": round(t.t_event, 3)}, **t.metrics}
                         for t in trials])


# --- CLI ---------------------------------------------------------------------


def cmd_session(path: str) -> None:
    sess = load_session(path)
    m = sess.meta
    print(f"{m.get('experimentID')}  ·  {m.get('condition')}  ·  {m.get('site')}")
    print(f"{m.get('device')} / {m.get('osVersion')}  ·  schema {m.get('schemaVersion')}")
    print(f"duration {sess.duration:.1f} s  ·  {len(sess.samples)} samples")
    if m.get("notes"):
        print(f"notes: {m['notes']}")
    print()
    print("channel health (O1 gate: dropFraction < 0.02)")
    print(o1_report(sess).to_string(index=False))
    if sess.duration < O1_MIN_SECONDS:
        print(f"  [O1 not assessable: session is {sess.duration/60:.1f} min, gate needs >= 30 min]")
    print()
    fids = find_fiducials(sess)
    print(f"fiducials detected: {len(fids)}  {[round(f, 2) for f in fids]}")
    if len(fids) < 3:
        print("  [expected 3 taps ~1 s apart — check tap spacing, PREREG §2.2]")
    print()
    floor_e = baseline_floor(sess, "energy")
    print(f"baseline floor  E_vib {floor_e:.3e} g^2*s"
          f"  ·  accel {baseline_floor(sess, 'accel'):.3e} g")


def cmd_batch(path: str) -> None:
    trials, excluded = load_manifest(path)
    df = trials_frame(trials)
    out = Path(path).parent
    if excluded:
        pd.DataFrame(excluded).to_csv(out / "exclusions.csv", index=False)
    print(f"{len(trials)} trials  ·  {len(excluded)} excluded"
          f"{' -> exclusions.csv' if excluded else ''}")
    if df.empty:
        return
    print()
    print(df.to_string(index=False))

    pend = df[(df["protocol"] == "pendulum") & (df["condition"] == "disturbed")]
    ctrl = df[(df["protocol"] == "pendulum") & (df["condition"] == "controlled")]

    # H3a — dose-response. Level is release angle; energy needs m and L, which
    # live in the session notes, so the fit is reported against (1 - cos theta),
    # proportional to impact energy and therefore identical in log-log slope.
    if not pend.empty and pend["level"].notna().any():
        x = 1 - np.cos(np.radians(pend["level"].to_numpy(float)))
        fit = loglog_fit(x, pend["E_vib"].to_numpy())
        print(f"\nH3a  log10(E_vib) ~ log10(1-cos θ):  slope {fit.slope:.3f}"
              f"  95% CI [{fit.ci[0]:.3f}, {fit.ci[1]:.3f}]  R² {fit.r2:.3f}  n={fit.n}")
        print(f"     prediction: CI excludes 0 -> "
              f"{'MET' if fit.ci[0] > 0 else 'NOT MET'}")

    # H4 — derived channel vs raw accelerometer, paired within trial.
    if not pend.empty and not ctrl.empty:
        fe, fa = ctrl["E_vib"].median(), ctrl["accel_excess"].median()
        snr_v = pend["E_vib"] / fe
        snr_a = pend["accel_excess"] / fa
        d = np.log10(snr_v) - np.log10(snr_a)
        d = d[np.isfinite(d)]
        if len(d) >= 6:
            w = stats.wilcoxon(d, alternative="greater")
            print(f"\nH4   median log10 SNR advantage {np.median(d):+.2f} "
                  f"({10**np.median(d):.1f}x)  Wilcoxon p={w.pvalue:.4f}  n={len(d)}")

    # H5 — metric repeatability across levels.
    if not pend.empty and pend["level"].notna().any():
        rows = [{"level": lv,
                 "CV_E_vib": cv(g["E_vib"]), "CV_peak": cv(g["peak"]),
                 "CV_rms_peak": cv(g["rms_peak"])}
                for lv, g in pend.groupby("level")]
        h5 = pd.DataFrame(rows)
        print("\nH5   within-level coefficient of variation")
        print(h5.to_string(index=False))
        print(f"     prediction: CV(rms_peak) > CV(E_vib) -> "
              f"{'MET' if h5['CV_rms_peak'].mean() > h5['CV_E_vib'].mean() else 'NOT MET'}")

    # H1 — per level, disturbed vs controlled.
    if not ctrl.empty:
        print("\nH1   disturbed vs controlled, exact permutation (one-tailed)")
        raw = {}
        for lv, g in pend.groupby("level"):
            p = exact_permutation_p(g["E_vib"], ctrl["E_vib"])
            raw[f"H1@{lv}"] = p
            print(f"     level {lv}: p={p:.4g}  (floor at this n: "
                  f"{min_attainable_p(len(g), len(ctrl)):.2e})")
        adj = holm(raw)
        print("     Holm-adjusted: " + "  ".join(f"{k}={v:.4f}" for k, v in adj.items()))


def main() -> None:
    if len(sys.argv) < 3 or sys.argv[1] not in {"session", "batch"}:
        print(__doc__)
        sys.exit(1)
    (cmd_session if sys.argv[1] == "session" else cmd_batch)(sys.argv[2])


if __name__ == "__main__":
    main()
