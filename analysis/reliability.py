"""H2 — cross-device agreement (proposal deliverable 4, PREREG §3 H2).

Two devices recording the same physical events, aligned on the sync fiducial and
compared channel by channel. Implements the pre-registered H2 metrics: Pearson r
on a common resampled grid, bias, and each device's at-rest noise floor.

**Alignment is physical, never wall-clock.** `Sample.t` is monotonic from each
device's own recording start, so two files share no origin — an offset of tens of
seconds between them is normal and means nothing. What they do share is the room:
a Mark-sync haptic burst, or a hand rap on the table, is one physical event that
both accelerometers observe. Estimating the lag between those observations is the
whole alignment step, and everything downstream depends on getting it right.

Usage:

    python reliability.py phoneA.json phoneB.json
"""
from __future__ import annotations

import sys
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from events import Session, load_session, find_fiducials
from regimes import resample, vib_series

# H2 thresholds, frozen in PREREG §3.
R_THRESHOLD = 0.9
FIDUCIAL_TOL = 0.5      # s — fiducial trains further apart than this don't pair
XCORR_MAX_LAG = 30.0    # s — search window for the cross-correlation fallback


# --- alignment ---------------------------------------------------------------


def offset_from_fiducials(a: Session, b: Session) -> dict | None:
    """Lag between two sessions from their sync-fiducial trains.

    Preferred method: the fiducial is a *coded* burst (three pulses ~1 s apart),
    so matching the trains rather than a single impulse guards against locking
    onto the wrong spike. Returns the median pairwise offset and the spread
    across pulses — that spread is the honest uncertainty on the alignment, and
    it belongs in the paper next to any r it produces.
    """
    fa, fb = find_fiducials(a), find_fiducials(b)
    if len(fa) < 2 or len(fb) < 2:
        return None
    n = min(len(fa), len(fb))
    # Align on the intervals, not the absolute times: if one device missed the
    # first pulse, matching index-to-index would bias every offset by ~1 s.
    best, best_err = None, np.inf
    for sa in range(len(fa) - n + 1):
        for sb in range(len(fb) - n + 1):
            da = np.diff(fa[sa:sa + n])
            db = np.diff(fb[sb:sb + n])
            err = float(np.mean(np.abs(da - db))) if n > 1 else np.inf
            if err < best_err:
                best_err, best = err, (sa, sb)
    if best is None or best_err > FIDUCIAL_TOL:
        return None
    sa, sb = best
    offs = np.array(fa[sa:sa + n]) - np.array(fb[sb:sb + n])
    return {"method": "fiducial", "offset_s": float(np.median(offs)),
            "spread_s": float(np.std(offs, ddof=1)) if n > 1 else float("nan"),
            "n_pulses": int(n), "interval_mismatch_s": round(best_err, 4)}


def offset_from_xcorr(a: Session, b: Session, hz: float = 20.0) -> dict:
    """Fallback: lag by cross-correlating the two vibration envelopes.

    Used when a fiducial can't be recovered. Weaker — it locks onto whatever
    structure the two records share, which in a quiet room may be nothing — so
    the returned peak correlation should be read as a confidence, not a formality.
    """
    ta, xa = vib_series(a)
    tb, xb = vib_series(b)
    if ta.size < 10 or tb.size < 10:
        return {"method": "xcorr", "offset_s": float("nan"), "peak_r": float("nan")}
    _, ya = resample(ta, xa, hz)
    _, yb = resample(tb, xb, hz)
    ya, yb = ya - ya.mean(), yb - yb.mean()
    c = np.correlate(ya, yb, mode="full")
    denom = np.sqrt((ya ** 2).sum() * (yb ** 2).sum()) or 1.0
    lags = (np.arange(len(c)) - (len(yb) - 1)) / hz
    m = np.abs(lags) <= XCORR_MAX_LAG
    i = int(np.argmax(c[m]))
    return {"method": "xcorr", "offset_s": float(lags[m][i]),
            "peak_r": float(c[m][i] / denom)}


def refine_offset(a: Session, b: Session, seed: float,
                  span: float = 2.0, hz: float = 50.0) -> dict:
    """Refine a coarse offset by maximising envelope correlation near it.

    Pairing individual pulses is brittle: a spurious peak at the start of one
    recording shifts every index by one and drags the estimate by a whole pulse
    interval. Correlating the envelopes does not care which peak is which — it
    only cares that the two records line up — so the fiducial is used for what it
    is good at (getting within a second or so) and the correlation does the rest.
    """
    ta, xa = _series(a, "accelerometer")
    tb, xb = _series(b, "accelerometer")
    if ta.size < 20 or tb.size < 20:
        return {"offset_s": seed, "peak_r": float("nan"), "refined": False}
    xa, xb = np.abs(xa - np.median(xa)), np.abs(xb - np.median(xb))
    best, best_r = seed, -np.inf
    for o in np.arange(seed - span, seed + span, 1.0 / hz):
        lo, hi = max(ta[0], tb[0] + o), min(ta[-1], tb[-1] + o)
        if hi - lo < 2.0:
            continue
        g = np.arange(lo, hi, 1.0 / hz)
        ya, yb = np.interp(g, ta, xa), np.interp(g, tb + o, xb)
        if ya.std() == 0 or yb.std() == 0:
            continue
        r = float(np.corrcoef(ya, yb)[0, 1])
        if r > best_r:
            best_r, best = r, float(o)
    return {"offset_s": best, "peak_r": best_r, "refined": True}


def estimate_offset(a: Session, b: Session) -> dict:
    """Coarse offset from the fiducial (or cross-correlation), then refined.

    Reported `offset_s` is always the refined value; `seed_s` and `method` record
    how it was reached, because which method aligned a pair of devices is part of
    the H2 result and not an implementation detail.
    """
    coarse = offset_from_fiducials(a, b) or offset_from_xcorr(a, b)
    fine = refine_offset(a, b, coarse["offset_s"])
    return {**coarse, "seed_s": coarse["offset_s"],
            "offset_s": fine["offset_s"], "refine_r": fine["peak_r"]}


# --- agreement ---------------------------------------------------------------


@dataclass
class AgreementResult:
    channel: str
    pearson_r: float
    bias: float
    noise_floor_a: float
    noise_floor_b: float
    n: int

    @property
    def passes_h2(self) -> bool:
        return (self.pearson_r >= R_THRESHOLD
                and abs(self.bias) <= max(self.noise_floor_a, self.noise_floor_b))


def noise_floor(at_rest: np.ndarray) -> float:
    """At-rest standard deviation — the channel's noise floor."""
    x = np.asarray(at_rest, float)
    x = x[np.isfinite(x)]
    return float(x.std(ddof=1)) if x.size > 1 else float("nan")


def _series(sess: Session, channel: str) -> tuple[np.ndarray, np.ndarray]:
    if channel == "vibration":
        return vib_series(sess)
    d = sess.channel(channel)
    if d.empty:
        return np.array([]), np.array([])
    if channel in ("accelerometer", "magnetometer"):
        v = np.sqrt(d["v0"] ** 2 + d["v1"] ** 2 + d["v2"] ** 2).to_numpy()
    else:
        v = d["v0"].to_numpy()
    return d["t"].to_numpy(), v


def agreement(a: Session, b: Session, channel: str,
              offset_s: float, hz: float | None = None,
              quiet_window: float = 5.0) -> AgreementResult | None:
    """H2 metrics for one channel across two aligned sessions.

    `offset_s` shifts B onto A's clock. Both are resampled to a common grid over
    their overlapping span, because two devices never deliver samples at the same
    instants even at the same nominal rate.
    """
    ta, xa = _series(a, channel)
    tb, xb = _series(b, channel)
    if ta.size < 10 or tb.size < 10:
        return None
    tb = tb + offset_s
    lo, hi = max(ta[0], tb[0]), min(ta[-1], tb[-1])
    if hi - lo < 2.0:
        return None
    hz = hz or {"accelerometer": 50.0, "magnetometer": 25.0,
                "vibration": 5.0, "barometer": 1.0}.get(channel, 5.0)
    grid = np.arange(lo, hi, 1.0 / hz)
    ya, yb = np.interp(grid, ta, xa), np.interp(grid, tb, xb)
    if ya.size < 3 or np.allclose(ya.std(), 0) or np.allclose(yb.std(), 0):
        return None
    r, _ = stats.pearsonr(ya, yb)
    qa = xa[ta <= ta[0] + quiet_window]
    qb = xb[tb <= tb[0] + quiet_window]
    return AgreementResult(channel, float(r), float((ya - yb).mean()),
                           noise_floor(qa), noise_floor(qb), int(ya.size))


def compare(path_a: str, path_b: str) -> pd.DataFrame:
    a, b = load_session(path_a), load_session(path_b)
    off = estimate_offset(a, b)
    print(f"device A  {a.meta.get('device')}  ·  {a.duration:.1f} s  ·  "
          f"{a.meta.get('placement') or 'placement not recorded'}")
    print(f"device B  {b.meta.get('device')}  ·  {b.duration:.1f} s  ·  "
          f"{b.meta.get('placement') or 'placement not recorded'}")
    print()
    if off["method"] == "fiducial":
        print(f"alignment  fiducial seed {off['seed_s']:+.3f} s from {off['n_pulses']} pulses "
              f"→ refined {off['offset_s']:+.3f} s (envelope r {off['refine_r']:.3f})")
    else:
        print(f"alignment  NO FIDUCIAL — cross-correlation seed {off['seed_s']:+.3f} s "
              f"→ refined {off['offset_s']:+.3f} s (envelope r {off['refine_r']:.3f})")
        print("           [weaker than a fiducial: report the method used]")
    print()

    rows = []
    for ch in ("vibration", "accelerometer", "magnetometer", "barometer"):
        res = agreement(a, b, ch, off["offset_s"])
        if res is None:
            rows.append({"channel": ch, "r": None, "bias": None,
                         "floor_A": None, "floor_B": None, "n": 0,
                         "H2": "no data"})
            continue
        rows.append({"channel": ch, "r": round(res.pearson_r, 4),
                     "bias": round(res.bias, 5),
                     "floor_A": round(res.noise_floor_a, 5),
                     "floor_B": round(res.noise_floor_b, 5),
                     "n": res.n,
                     "H2": "PASS" if res.passes_h2 else "flagged"})
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    print(f"\nH2 threshold: r >= {R_THRESHOLD} AND |bias| <= the larger noise floor.")
    print("A channel that fails is flagged untrustworthy, not dropped — "
          "PREREG §3 H2. Negative results count.")
    return df


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    compare(sys.argv[1], sys.argv[2])
