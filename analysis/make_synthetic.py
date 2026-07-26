"""Generate synthetic Covariate sessions to exercise analysis/events.py.

Not test data for the paper — a harness so the analysis is known to run before
real data exists. Ground truth: vibration energy scales as impact energy^0.8,
so a correct H3a fit should recover a slope near 0.8.
"""
import json, math, random
from pathlib import Path

random.seed(7)
OUT = Path("synth"); OUT.mkdir(exist_ok=True)

ACC_HZ, MAG_HZ, VIB_HZ, BARO_HZ = 50, 25, 5, 1
TRUE_SLOPE = 0.8   # amplitude exponent; E_vib ~ amp^2 so the expected H3a slope is 1.6


def impulse(t, t0, amp, tau=0.05):
    return amp * math.exp(-(t - t0) / tau) if 0 <= t - t0 < 6 * tau else 0.0


def session(name, condition, duration, events, amp, fid_t=(3.0, 4.0, 5.0), notes=""):
    samples, health = [], {}

    def add(ch, t, vals):
        samples.append({"t": round(t, 4), "channel": ch, "values": [round(v, 6) for v in vals]})
        h = health.setdefault(ch, {"n": 0, "first": t, "last": t, "gap": 0.0})
        h["gap"] = max(h["gap"], t - h["last"]); h["last"] = t; h["n"] += 1

    n = int(duration * ACC_HZ)
    win_sq, win_pk, win_t = 0.0, 0.0, 0.0
    win_n = 0
    for i in range(n):
        t = i / ACC_HZ
        shake = random.gauss(0, 0.0015)
        for t0 in fid_t:
            shake += impulse(t, t0, 0.35)
        for t0 in events:
            shake += impulse(t, t0, amp)
        gx, gy = random.gauss(0, 0.0008), random.gauss(0, 0.0008)
        add("accelerometer", t, [gx + shake, gy, 1.0 + shake * 0.6])

        # mirror the app's 200 ms vibration window
        win_sq += shake ** 2; win_pk = max(win_pk, abs(shake)); win_n += 1
        if t - win_t >= 1 / VIB_HZ:
            add("vibration", t, [math.sqrt(win_sq / win_n), win_pk])
            win_sq, win_pk, win_n, win_t = 0.0, 0.0, 0, t

        if i % (ACC_HZ // MAG_HZ) == 0:
            add("magnetometer", t, [22 + random.gauss(0, .3), -8 + random.gauss(0, .3), 41 + random.gauss(0, .3)])
        if i % (ACC_HZ // BARO_HZ) == 0:
            warm = 0.45 * (1 - math.exp(-t / 2.5))   # the pilot's warm-up transient
            add("barometer", t, [1006.2 + warm + random.gauss(0, .01), warm * 8])

    rec = {
        "meta": {"schemaVersion": "0.1.3", "experimentID": name, "condition": condition,
                 "site": "chicago-kitchen", "device": "synthetic", "osVersion": "n/a",
                 "appVersion": "synth", "startedAtWall": "2026-07-26T14:00:00.000Z",
                 "endedAtWall": "2026-07-26T14:02:00.000Z", "notes": notes},
        "health": [{"channel": c,
                    "sampleCount": h["n"], "firstT": h["first"], "lastT": h["last"],
                    "maxGap": round(h["gap"], 4),
                    "nominalRate": {"accelerometer": 50, "magnetometer": 25,
                                    "vibration": 5, "barometer": None}[c],
                    "dropFraction": 0.004}
                   for c, h in health.items()],
        "samples": samples,
    }
    (OUT / f"{name}.json").write_text(json.dumps(rec))
    return f"{name}.json"


rows = [",".join(["file", "protocol", "condition", "level", "event_times", "exclude"])]

# controlled runs
for k in range(1, 4):
    ev = [15 + 15 * i for i in range(6)]
    f = session(f"pend-ctrl-{k}", "controlled", 110, ev, 0.0)
    rows.append(f"{f},pendulum,controlled,,{';'.join(str(e) for e in ev)},")

# dose ladder: amplitude ~ (1-cos theta) ** TRUE_SLOPE
for ang in (15, 30, 45, 60, 75):
    e_imp = 1 - math.cos(math.radians(ang))
    amp = 0.09 * (e_imp / 0.5) ** TRUE_SLOPE
    # sub-window jitter: events must NOT land on the same 200 ms window phase
    # every time, or the harness cannot exercise the effect H5 exists to test.
    ev = [round(15 + 15 * i + random.uniform(0, 0.2), 3) for i in range(6)]
    f = session(f"pend-{ang}", "disturbed", 110, ev,
                amp * random.uniform(.95, 1.05), notes=f"m=0.40kg L=0.50m theta={ang}")
    rows.append(f"{f},pendulum,disturbed,{ang},{';'.join(str(e) for e in ev)},")

# one excluded trial, to exercise the exclusion path
f = session("pend-45-bumped", "disturbed", 110, [15], 0.05)
rows.append(f"{f},pendulum,disturbed,45,15,phone bumped mid-trial")

(OUT / "manifest.csv").write_text("\n".join(rows) + "\n")
print(f"wrote {len(rows)-1} manifest rows to {OUT}/manifest.csv")
