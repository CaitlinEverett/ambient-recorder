"""Ground-truth checks for regimes.py. Every planted value must be recovered.

Run: python test_regimes.py
"""
import json, math, random, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from events import load_session                       # noqa: E402
import regimes as R                                    # noqa: E402

random.seed(11); np.random.seed(11)
OUT = Path("synth"); OUT.mkdir(exist_ok=True)
ACC_HZ, VIB_HZ, BARO_HZ = 50, 5, 1
fails = []


def check(name, ok, detail):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        fails.append(name)


def write(name, duration, accel_fn, baro_fn=None, meta_extra=None):
    samples, health = [], {}

    def add(ch, t, vals):
        samples.append({"t": round(t, 4), "channel": ch, "values": [float(v) for v in vals]})
        h = health.setdefault(ch, {"n": 0, "first": t, "last": t, "gap": 0.0})
        h["gap"] = max(h["gap"], t - h["last"]); h["last"] = t; h["n"] += 1

    n = int(duration * ACC_HZ)
    sq = pk = 0.0; cnt = 0; wt = 0.0
    for i in range(n):
        t = i / ACC_HZ
        s = accel_fn(t)
        add("accelerometer", t, [s, 0.0, 1.0])
        sq += s * s; pk = max(pk, abs(s)); cnt += 1
        if t - wt >= 1 / VIB_HZ:
            add("vibration", t, [math.sqrt(sq / cnt), pk]); sq = pk = 0.0; cnt = 0; wt = t
        if baro_fn and i % (ACC_HZ // BARO_HZ) == 0:
            add("barometer", t, [baro_fn(t), 0.0])
    rec = {"meta": {"schemaVersion": "0.1.3", "experimentID": name, "condition": "controlled",
                    "site": "synth", "device": "synthetic", "osVersion": "n/a", "appVersion": "t",
                    "startedAtWall": "2026-07-26T14:00:00.000Z",
                    "endedAtWall": "2026-07-26T15:00:00.000Z", "notes": "",
                    **(meta_extra or {})},
           "health": [{"channel": c, "sampleCount": h["n"], "firstT": h["first"],
                       "lastT": h["last"], "maxGap": h["gap"],
                       "nominalRate": {"accelerometer": 50, "vibration": 5, "barometer": None}[c],
                       "dropFraction": 0.0} for c, h in health.items()],
           "samples": samples}
    p = OUT / f"{name}.json"; p.write_text(json.dumps(rec)); return p


print("\n1. SPECTRAL — plant a 7 Hz tone, recover it")
p = write("t-spec", 60, lambda t: 0.02 * math.sin(2 * math.pi * 7.0 * t) + random.gauss(0, .001))
f, pw = R.psd(load_session(p))
pk = R.spectral_peaks(f, pw, n=1)
check("peak freq", pk and abs(pk[0]["freq_hz"] - 7.0) < 0.6, f"planted 7.0 Hz, found {pk[0]['freq_hz'] if pk else None} Hz")
c = R.spectral_centroid(f, pw)
check("centroid", 5 < c < 10, f"{c:.2f} Hz (single 7 Hz tone)")

print("\n1b. ALIASING — plant 60 Hz, confirm it folds to 10 Hz and is flagged")
p = write("t-alias", 60, lambda t: 0.02 * math.sin(2 * math.pi * 60.0 * t) + random.gauss(0, .0005))
f, pw = R.psd(load_session(p))
pk = R.spectral_peaks(f, pw, n=1)
check("alias fold", pk and abs(pk[0]["freq_hz"] - 10.0) < 1.0, f"60 Hz appears at {pk[0]['freq_hz'] if pk else None} Hz")
check("alias flagged", pk and pk[0]["alias_warning"], f"warning = {pk[0]['alias_warning'] if pk else None}")

print("\n2. DECAY — plant tau = 0.30 s ring-down")
TAU = 0.30
p = write("t-decay", 30, lambda t: (0.05 * math.exp(-(t - 10) / TAU) * math.sin(2 * math.pi * 9 * t)
                                    if 10 <= t < 12 else random.gauss(0, .0004)))
tau = R.decay_tau(load_session(p), 10.05)
check("decay tau", math.isfinite(tau) and abs(tau - TAU) / TAU < 0.45, f"planted {TAU}s, recovered {tau:.3f}s")

print("\n3. PERIODICITY — compressor: 300 s period, 120 s on (40% duty)")
PERIOD, ON = 300.0, 120.0
p = write("t-duty", 3000, lambda t: (0.02 if (t % PERIOD) < ON else 0.0) + abs(random.gauss(0, .0015)))
s = load_session(p); tv, rv = R.vib_series(s)
d = R.dominant_period(tv, rv)
check("period", abs(d["period_s"] - PERIOD) < 15, f"planted {PERIOD:.0f}s, found {d['period_s']:.0f}s")
dc = R.duty_cycle(tv, rv)
check("duty", abs(dc["on_fraction"] - ON / PERIOD) < 0.06, f"planted {ON/PERIOD:.2f}, found {dc['on_fraction']:.2f}")
check("on-duration", abs(dc["mean_on_s"] - ON) < 25, f"planted {ON:.0f}s, found {dc['mean_on_s']:.0f}s")

print("\n4. ALLAN — white noise must fall as tau^-0.5")
x = np.random.normal(0, 1.0, 8000)
ad = R.allan_deviation(x, 0.2)
lf = np.polyfit(np.log10(ad["tau_s"][:12]), np.log10(ad["adev"][:12]), 1)[0]
check("white-noise slope", abs(lf + 0.5) < 0.12, f"expected -0.50, got {lf:+.3f}")
xd = np.cumsum(np.random.normal(0, 1.0, 8000))          # random walk -> +0.5
lf2 = np.polyfit(np.log10(R.allan_deviation(xd, .2)["tau_s"][:12]),
                 np.log10(R.allan_deviation(xd, .2)["adev"][:12]), 1)[0]
check("random-walk slope", abs(lf2 - 0.5) < 0.20, f"expected +0.50, got {lf2:+.3f}")

print("\n5. BLIND DETECTION — 8 events at unknown times, detector gets no labels")
truth = sorted(random.sample(range(60, 580, 7), 8))
p = write("t-blind", 600, lambda t: sum(0.05 * math.exp(-(t - e) / .05) for e in truth if 0 <= t - e < .4)
          + random.gauss(0, .0008))
found = R.detect_events(load_session(p))
sc = R.score_detections(found, [float(x) for x in truth], tol=2.0)
check("recall", sc["recall"] == 1.0, f"{sc['tp']}/{len(truth)} found, {sc['fp']} false positives")
check("timing", sc["max_timing_error_s"] is not None and sc["max_timing_error_s"] < 1.0,
      f"max |Δt| = {sc['max_timing_error_s']}s")

print("\n6. CLASSIFICATION — 3 event types separable by decay + frequency, NOT amplitude")
X, y = [], []
for lbl, (freq, tau, amp) in {"thud": (4, .12, .05), "ring": (14, .55, .05), "tap": (9, .05, .05)}.items():
    for k in range(8):
        te = 20.0 + random.uniform(-1, 1)   # one event per session, jittered
        pth = write(f"t-cls-{lbl}-{k}", 30,
                    lambda t, f=freq, T=tau, A=amp, e=te: (A * math.exp(-(t - e) / T) * math.sin(2 * math.pi * f * t)
                                                           if 0 <= t - e < 3 else random.gauss(0, .0004)))
        X.append(list(R.event_features(load_session(pth), te + .05).values())); y.append(lbl)
Xa = np.array(X, float)
Xa = Xa[:, [i for i in range(Xa.shape[1]) if np.isfinite(Xa[:, i]).all()]]
_, cm, acc = R.loo_1nn(Xa, np.array(y))
check("accuracy", acc > R.chance_rate(y) + .25, f"{acc:.2f} vs {R.chance_rate(y):.2f} chance")
print(cm.to_string())

print("\n7. EXTERNAL REFERENCE — plant a 21.7 hPa offset (=> ~180 m)")
import pandas as pd
OFFSET = -21.7
p = write("t-baro", 3600, lambda t: random.gauss(0, .0005),
          baro_fn=lambda t: 1013.0 + OFFSET + 2.0 * math.sin(2 * math.pi * t / 7200))
ref = pd.DataFrame({"t": np.arange(120, 3600, 300.0)})
ref["hPa"] = 1013.0 + 2.0 * np.sin(2 * np.pi * ref["t"] / 7200)
r = R.compare_to_reference(load_session(p), ref)
check("slope", abs(r["slope"] - 1.0) < 0.02, f"expected 1.00, got {r['slope']}")
check("offset", abs(r["mean_offset_hPa"] - OFFSET) < 0.1, f"expected {OFFSET}, got {r['mean_offset_hPa']}")
check("altitude", abs(r["implied_altitude_m"] - 180) < 12, f"expected ~180 m, got {r['implied_altitude_m']} m")

print("\n" + ("ALL CHECKS PASSED" if not fails else f"FAILED: {', '.join(fails)}"))
sys.exit(1 if fails else 0)
