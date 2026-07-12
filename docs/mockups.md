# Covariate — UI mockups

Low-fidelity ASCII layouts for the session UI. These are **intent, not spec** —
exact spacing, wording, and SF Symbols are the implementer's call. They encode
the design decisions recorded in the handoff prompt (three-state session flow,
native-first with simple `Canvas` data marks, coarse location, audio-free
reference video, and — critically — **no audio waveform, ever**).

Legend: `●` filled/active · `○` inactive/needs-permission · `▓░` meter fill ·
`▁▂▃` one-sided sparkline (never mirrored) · `⚑` flagged event.

---

## 1 · New Session (idle)

Experiment metadata + a **pre-flight channel check** so a denied permission is
caught *before* a long run, not discovered as a red row after. Start is disabled
until an Experiment ID is set.

```
┌───────────────────────────────────┐
│ Covariate                    ⚙    │
├───────────────────────────────────┤
│  EXPERIMENT                       │
│  ┌─────────────────────────────┐  │
│  │ ID   yeast-rise-03          │  │
│  └─────────────────────────────┘  │
│  Condition    [ Controlled  ▾ ]   │
│  ┌─────────────────────────────┐  │
│  │ Site chicago-kitchen        │  │
│  └─────────────────────────────┘  │
│  ┌─────────────────────────────┐  │
│  │ Notes  proofing 24C         │  │
│  └─────────────────────────────┘  │
│                                   │
│  CAPTURE                          │
│   Location fix      [ Region ▾ ]  │
│    Chicago, IL · alt 181 m        │
│   Reference video   [   On  ◉ ]   │
│    ● no audio · 1080p · sidecar   │
│                                   │
│  CHANNELS   (pre-flight check)    │
│   ● barometer         ready       │
│   ● accelerometer     ready 50Hz  │
│   ● magnetometer      ready 25Hz  │
│   ○ light          tap to grant   │
│   ○ mic level       tap to grant  │
│   – external BLE     not paired   │
│                                   │
│  ╔═════════════════════════════╗  │
│  ║      ▶   Start Session      ║  │
│  ╚═════════════════════════════╝  │
│   (disabled until ID is set)      │
└───────────────────────────────────┘
```

---

## 2 · Recording (live)

The glanceable screen: elapsed time, the **O1 gate drawn as progress toward the
30-min minimum**, worst live drop-fraction with a green/orange/red state, a
"streaming to disk" indicator, and the two session actions. Per-channel mini-viz
matches each sensor's data shape (see §5).

```
┌───────────────────────────────────┐
│ ● REC   yeast-rise-03             │
├───────────────────────────────────┤
│        controlled · chicago-kit   │
├───────────────────────────────────┤
│             00:12:47              │
│              elapsed              │
│                                   │
│  O1 gate ▓▓▓▓▓▓▓░░░░░░  12/30 min │
│  ⤓ streaming to disk · crash-safe │
├───────────────────────────────────┤
│  ch       latest      n     drop  │
│  ───────────────────────────────  │
│  baro    100.63 kPa   761     –   │
│  accel     0.02 g   38.2k   0.1%  │
│  mag      47.6 µT    17.1k  3.2% ⚠│
│  light     6.2 EV     3.8k   1.1% │
│  mic      -46 dBFS    7.6k   0.3% │
│  ───────────────────────────────  │
│  worst 3.2% · gate <2%   ⚠ 1 over │
├───────────────────────────────────┤
│  ┌────────────┐  ┌─────────────┐  │
│  │  ⚑  Mark   │  │   ■  Stop   │  │
│  │    Sync    │  │  & Export   │  │
│  └────────────┘  └─────────────┘  │
└───────────────────────────────────┘
```

---

## 3 · Mark Sync (fiducial)

Cross-device alignment (H2) needs a physical event both phones' logs can locate
independently — wall clocks won't agree. Mechanism still open: **lean tap (accel
spike)** over flash (light channel), because accel is the most reliable channel
and lighting varies across the H3 sites.

```
┌───────────────────────────────────┐
│ Mark Sync                    ✕    │
├───────────────────────────────────┤
│  Hold both phones together and    │
│  tap Mark on each within ~2 s.    │
│                                   │
│  ┌─────────────────────────────┐  │
│  │             3               │  │
│  │      screen flashes white   │  │
│  │      + logs an accel spike  │  │
│  └─────────────────────────────┘  │
│                                   │
│  Both logs can locate this event  │
│  independently → aligns H2 pair.  │
│                                   │
│  Fiducials this session:  2       │
│    #1  t = 0.42 s                 │
│    #2  t = 764.81 s               │
│                                   │
│  ╔═════════════════════════════╗  │
│  ║       ⚑   Mark  Now         ║  │
│  ╚═════════════════════════════╝  │
└───────────────────────────────────┘
```

---

## 4 · Session Complete (export)

Per-channel drop vs. the 2% gate as pass/warn/fail, with a gate failure **framed
as a finding** (likely iOS throttling, proposal Challenge 3), not a crash.

```
┌───────────────────────────────────┐
│ Session Complete                  │
├───────────────────────────────────┤
│  yeast-rise-03 · controlled       │
│  duration  31:04     (≥30 min ✓)  │
├───────────────────────────────────┤
│  channel         drop     gate    │
│  ───────────────────────────────  │
│  barometer         –       n/a    │
│  accelerometer    0.1%      ✓     │
│  magnetometer     3.2%      ✗     │
│  light            1.1%      ✓     │
│  mic level        0.3%      ✓     │
├───────────────────────────────────┤
│  ⚠ magnetometer over the 2% gate. │
│    Likely iOS delivery throttling │
│    (proposal Challenge 3) — this  │
│    is a finding, not a crash.     │
├───────────────────────────────────┤
│  record                           │
│   session_yeast-rise-03_...z.json │
│   2.9 MB · 68,412 samples · 2 fid │
│                                   │
│  ┌────────────┐  ┌─────────────┐  │
│  │  ⤴ Export  │  │  + New      │  │
│  │   / Share  │  │   Session   │  │
│  └────────────┘  └─────────────┘  │
└───────────────────────────────────┘
```

---

## 5 · Sound level — no waveform, ever

No audio is stored, so there is no waveform to show. More importantly, do not
draw anything that *reads* like one — a mirrored two-sided squiggle is the visual
signifier of "we recorded your audio" and contradicts privacy invariant (a). Use
the grammar of a **meter** (live) and a **loudness heatmap + stats** (session).

```
A · LIVE  (Recording screen)          B · SUMMARY  (Complete / detail)
┌─────────────────────────────────┐   ┌─────────────────────────────────────┐
│ Sound level · mic  (no audio)   │   │ Sound level — session summary       │
├─────────────────────────────────┤   ├─────────────────────────────────────┤
│  now  -46 dBFS        peak -9   │   │  loudness timeline   (0 → 31 min)   │
│  ▓▓▓▓▓▓▓▓░░░░░░░░░░░░  level     │   │  ░░▒▒▒▒▓▒▒░░▒██▒▒░░▒▒▒▓█▒▒░░▒▒▒▒▒   │
│  -70 ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈ -10 dBFS  │   │  ░ quiet ▒ ambient ▓ raised █ loud  │
│                                 │   ├─────────────────────────────────────┤
│  last 30 s  (level history)     │   │  median ambient    -46 dBFS         │
│  ▁▁▂▂▂▃▂▂▂▂▇▅▃▂▂▁▁▂▂▃▂▂▂▃▂▂     │   │  95th percentile   -34 dBFS         │
│              ▲ blender, 8s      │   │  loudest           -9 dBFS @ 12:41  │
│                                 │   │  time > -30 dBFS    4.2%            │
│  RMS envelope only — no signal  │   │  transients        2 flagged ⚑     │
│  is kept that a waveform could  │   ├─────────────────────────────────────┤
│  be drawn from.                 │   │  No waveform — only RMS level was   │
└─────────────────────────────────┘   │  ever recorded (privacy inv. a).    │
                                       └─────────────────────────────────────┘
```

The "last 30 s" bar sparkline is safe **only if drawn strictly one-sided** (bars
rising from a baseline, never mirrored below). If in doubt, drop it and let the
heatmap carry the over-time story.
```
