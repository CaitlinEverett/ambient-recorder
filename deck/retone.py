"""Plain-language pass over build_deck.py, plus a claims audit.

Two problems with the first version.

TONE. Titles were written for effect rather than for description — "The hack",
"The taps were never lost", "'Hard' isn't a measurement". Same for the body: a lot
of X-isn't-Y antithesis, one-line fragments for emphasis, and a closing slide built
around a flourish. Every title here is now what the slide contains.

CLAIMS. The deck implied work that has not been done. On record there are six
sessions, one iPhone X, four channels — accelerometer, barometer, magnetometer and
the derived vibration channel. There is no session containing a sync, light or
micLevel channel anywhere, and no dual-device recording. So: Mark sync is described
as implemented rather than demonstrated on data; cross-device agreement is untested
rather than thin; the pendulum ladder is a design rather than a result; and footage
cues say "a recording session" instead of implying the specific run that produced
the numbers.
"""
import sys
from pathlib import Path

p = Path("build_deck.py")
s = p.read_text()


def sub(old, new, n=1):
    global s
    if s.count(old) != n:
        sys.exit(f"NO MATCH ({s.count(old)}):\n{old[:220]}")
    s = s.replace(old, new)


# --- 1 · title ---------------------------------------------------------------
sub('''text(s, 0.85, 3.65, 11.5, 0.6, "recording the room, so experiments reproduce",
     size=22, color=GOLD)''',
    '''text(s, 0.85, 3.65, 11.5, 0.6,
     "A smartphone recorder for ambient experimental context",
     size=22, color=GOLD)''')

# --- 2 · why record the room -------------------------------------------------
sub('title(s, "The idea", "why this belongs in a ubiquitous-computing course")',
    'title(s, "Why record the room", "the case for this in a ubiquitous-computing course")')
sub('''text(s, 0.85, 1.95, 11.4, 0.9, [
    ("Ubicomp asks what the sensors say about the person.", {"size": 19, "color": MUTED}),
    ("We asked what they say about the room — and whether that is worth writing down.",
     {"size": 19, "bold": True, "color": NAVY}),
], space=4)''',
    '''text(s, 0.85, 1.95, 11.4, 0.9, [
    ("Most mobile sensing work uses a phone's sensors to characterise the person carrying it.",
     {"size": 18, "color": MUTED}),
    ("We use them to characterise the room, and attach the result to an experiment record.",
     {"size": 18, "bold": True, "color": NAVY}),
], space=4)''')
sub('''hex_rows(s, [
    ("The deployment problem is already solved.",
     "Weiser's calm technology arrived as a phone in every pocket. The hard part is no longer "
     "getting a sensor into the room — it is deciding what to do with the one already there."),
    ("Context-awareness, pointed the other way.",
     "Activity recognition senses a person to serve that person. Here the sensing serves a "
     "record — an experiment that has to survive being repeated by somebody else, later."),
    ("The hack is a derived channel.",
     "Gravity is a large constant; a door closing is a rounding error beside it. Subtract the "
     "constant and the same sensor gains two orders of magnitude — no new hardware."),
], top=3.30, gap=1.28)''',
    '''hex_rows(s, [
    ("Deployment is not the obstacle.",
     "A capable sensor package is already present in most rooms where experiments happen. "
     "The open question is what useful measurement can be taken with it."),
    ("The sensing serves a record, not a user.",
     "Activity recognition senses a person in order to adapt to that person. Here the output "
     "is metadata attached to an experiment that someone may try to repeat later."),
    ("The derived channel is the contribution.",
     "Gravity is a constant 1 g; a door closing perturbs the accelerometer by about 1%. "
     "Removing the constant raises the measured signal-to-noise by 3.5 to 5 times."),
], top=3.30, gap=1.28)''')

# --- 3 · aims ----------------------------------------------------------------
sub('title(s, "The plan", "three parts, and one constraint we chose on purpose")',
    'title(s, "Aims", "three, and one design constraint")')
sub('''    ("Constraint, chosen deliberately:  no special hardware.", {"size": 17, "bold": True, "color": NAVY}),
    ("A phone every lab already owns, or it doesn't get used.", {"size": 15, "color": MUTED}),''',
    '''    ("Design constraint: no additional hardware.", {"size": 17, "bold": True, "color": NAVY}),
    ("The recorder has to run on a phone a lab already owns.", {"size": 15, "color": MUTED}),''')

# --- 4 · implementation ------------------------------------------------------
sub('title(s, "What we built", "React Native under Expo Go — a teammate joins by scanning a QR code")',
    'title(s, "Implementation", "React Native under Expo Go; installs by scanning a QR code")')

# --- 5 · channels ------------------------------------------------------------
sub('title(s, "Channels", "seven, of which two are ours rather than the platform’s")',
    'title(s, "Channels", "four have recorded data so far; light and micLevel need a dev build")')
sub('''text(s, 0.85, 6.62, 11.0, 0.4,
     "Sound is a level, never a waveform — there is no audio to draw one from.",
     size=15, color=NAVY, bold=True)''',
    '''text(s, 0.85, 6.62, 11.0, 0.4,
     "The microphone channel stores a level in dBFS. No audio is recorded, so no waveform "
     "is displayed.", size=15, color=NAVY, bold=True)''')

# --- 6 · cross-device alignment ---------------------------------------------
sub('title(s, "Mark sync", "the alignment marker is physical on purpose")',
    'title(s, "Cross-device alignment", "implemented; no dual-device recording collected yet")')
sub('''cue(s, "▶  App screen recording — press Mark sync",
    "three haptic pulses, one second apart · record it WITH audio, "
    "then the export and the JSON meta / health blocks")''',
    '''cue(s, "▶  Footage: a recording session in the app",
    "show Mark sync firing — three haptic pulses, one second apart, recorded with audio — "
    "then the export and the JSON meta / health blocks")''')
sub('''text(s, 1.2, 5.6, 11.0, 1.1,
     "Session time is monotonic from each device's own recording start, so two phones share "
     "no clock. A button that only wrote a timestamp would align nothing — driving the "
     "vibration motor makes an event every phone on the surface hears through its own "
     "accelerometer.", size=15, color=MUTED, line=1.25)''',
    '''text(s, 1.15, 5.55, 11.1, 1.2,
     "Session time is monotonic from each device's own recording start, so two phones share no "
     "clock origin. A timestamp alone therefore cannot align them. Firing the vibration motor "
     "produces an event that any phone resting on the same surface registers through its own "
     "accelerometer, giving one device a known emission time and the others a signal to "
     "correlate against.", size=15, color=MUTED, line=1.25)''')

# --- 7 · privacy -------------------------------------------------------------
sub('title(s, "Built in, not promised", "privacy properties that are structural, not policy")',
    'title(s, "Privacy properties", "enforced by the implementation rather than by policy")')
sub('''    ("Longitudinal ambient data is still data about a household.",
     {"size": 17, "bold": True, "color": NAVY}),
    ("Occupancy, routine, device fingerprint, floor of a building — the report says so.",
     {"size": 14.5, "color": MUTED}),''',
    '''    ("Ambient sensor records can still identify a household.",
     {"size": 17, "bold": True, "color": NAVY}),
    ("Occupancy, daily routine, per-device sensor bias and barometric floor level are all "
     "inferable. The report documents these and the controls applied.",
     {"size": 14.5, "color": MUTED}),''')

# --- 8 · changes -------------------------------------------------------------
sub('title(s, "What changed", "a scoping decision, a demotion, and a freeze")',
    'title(s, "Changes since the proposal")')
sub('''    ("Two of five channels need a compiled dev client.",
     "Light and sound level are native modules, so they don't run in Expo Go. We scoped the "
     "study to the channels that install by scanning a QR code — and treat that friction as a "
     "finding, not an inconvenience."),''',
    '''    ("Scope reduced to the channels that run in Expo Go.",
     "Light and sound level are native modules and require a compiled dev client. Rather than "
     "spend schedule on that build step at a second site, we replaced the Alka-Seltzer "
     "dissolution study with a door experiment using only the remaining channels."),''')
sub('''    ("Three sites with one participant each can't support a variance claim.",
     "Person, city, phone model and building are fully confounded. The multi-site study is now "
     "explicitly a case study; the quantitative claims moved to a within-site design with "
     "enough trials to carry them."),''',
    '''    ("Multi-site study reclassified as a case study.",
     "With one participant per site, person, city, phone model and building are confounded. "
     "The quantitative claims moved to a within-site design with a trial count that can "
     "support them."),''')

# --- 9 · pilot ---------------------------------------------------------------
sub('title(s, "The pilot", "two baselines, two normal door closes, two slams — one phone, one room")',
    'title(s, "Pilot study", "two baselines, two normal door closes, two slams; one phone, one room")')
sub('''cue(s, "▶  Door experiment footage",
    "Christopher Kimberley's recording, Toronto · 10–15 seconds")''',
    '''cue(s, "▶  Footage: door experiment",
    "Christopher Kimberley, Toronto · 10–15 seconds")''')
sub('''text(s, 1.2, 5.6, 11.0, 0.8,
     "Six sessions on an iPhone X. Every session labelled, exported, and handed over as JSON — "
     "which is what made the reanalysis on the next three slides possible at all.",
     size=15, color=MUTED, line=1.25)''',
    '''text(s, 1.15, 5.55, 11.1, 0.9,
     "Six sessions on an iPhone X, exported as JSON. The three results that follow were "
     "obtained from those files alone, in a different city, without further input from the "
     "person who recorded them.", size=15, color=MUTED, line=1.25)''')

# --- 10-12 · results ---------------------------------------------------------
sub('title(s, "The hack", "a derived channel outperforms the raw sensor it is derived from")',
    'title(s, "Derived vibration channel", "signal-to-noise compared with the raw accelerometer")')
sub('title(s, "The statistic changes the margin", "same four events, measured three ways")',
    'title(s, "Effect of metric choice", "the same four events, measured three ways")')
sub('title(s, "The taps were never lost", "a reporting artifact, not a data-quality failure")',
    'title(s, "Sync fiducial recovery", "the pilot report\'s missing taps were a reporting artifact")')

# --- 13 · unlabelled detection -----------------------------------------------
sub('title(s, "Detection without labels", "the detector never sees the truth log")',
    'title(s, "Unlabelled event detection", "run on the six pilot sessions; the detector receives no labels")')
sub('''cue(s, "▶  Terminal — detect_events()",
    "18pt minimum · run it live on Chris's six files")''',
    '''cue(s, "▶  Terminal: detect_events() on the pilot sessions",
    "18pt minimum")''')
sub('''text(s, 1.2, 5.5, 11.0, 1.2, [
    ("Finds all four door events at the operator's noted times. Nothing in one baseline. "
     "One marginal candidate in the other, at 2.1× the floor — a real unnoticed event, or a "
     "false positive at our threshold. We report it either way.", {"size": 15, "color": MUTED}),
], line=1.25)''',
    '''text(s, 1.15, 5.45, 11.1, 1.3, [
    ("All four door events were recovered at the times the operator recorded. One baseline "
     "returned no candidates. The other returned a single candidate at 2.1 times the noise "
     "floor, which is either an unnoticed event or a false positive at the chosen threshold; "
     "it is reported as unresolved.", {"size": 15, "color": MUTED}),
], line=1.25)''')

# --- 14 · scope and limitations ----------------------------------------------
sub('title(s, "What this is — and isn\'t", "a feasibility study that succeeds as one")',
    'title(s, "Scope and limitations", "a feasibility study, and what it does not establish")')
sub('text(s, 0.85, 2.15, 5.4, 0.35, "A FEASIBILITY STUDY", size=15, bold=True, color=TEAL)',
    'text(s, 0.85, 2.15, 5.4, 0.35, "ESTABLISHED", size=15, bold=True, color=TEAL)')
sub('text(s, 7.05, 2.15, 5.3, 0.35, "NOT A GENERALISATION", size=15, bold=True, color=DEEPGOLD)',
    'text(s, 7.05, 2.15, 5.3, 0.35, "NOT ESTABLISHED", size=15, bold=True, color=DEEPGOLD)')
sub('"Cross-device agreement: one pair, one site"',
    '"Cross-device agreement — untested; one device"')
sub('''text(s, 0.85, 5.75, 11.4, 1.2,
     "Our reviewer said it first: three sites with one participant each cannot show that a "
     "logged covariate reduces between-site variance. They were right — so the quantitative "
     "claims moved to a within-site design, and the multi-site work stays a case study.",
     size=15, color=NAVY, line=1.3)''',
    '''text(s, 0.85, 5.75, 11.4, 1.2,
     "This follows our reviewer's assessment of the proposal: three sites with one participant "
     "each cannot demonstrate that logging a covariate reduces between-site variance. We accept "
     "that, and have moved the quantitative claims to a within-site design.",
     size=15, color=NAVY, line=1.3)''')

# --- 15 · standardising the disturbance --------------------------------------
sub('title(s, "\'Hard\' isn\'t a measurement", "two trials labelled slam differed by nearly 4×")',
    'title(s, "Standardising the disturbance", "designed, not yet run; two trials labelled slam differed by 3.9×")')

# --- 16 · remaining work -----------------------------------------------------
sub('title(s, "Queued this week", "what turns a feasibility read into a result")',
    'title(s, "Remaining work", "none of the following has been collected yet")')

# --- 18 · summary ------------------------------------------------------------
sub('''text(s, 0.85, 2.80, 11.5, 2.6, [
    ("We're building a tool to record what nobody wrote down.",
     {"size": 32, "bold": True, "color": WHITE, "space": 20}),
    ("Every session in our own pilot is labelled “controlled” — including both slams.",
     {"size": 23, "color": GOLD, "space": 20}),
    ("The app let us mislabel the entire dataset without a word. That's a finding about "
     "the product, and it's in the report.",
     {"size": 17, "color": RGBColor(0xC8, 0xD2, 0xDC)}),
], line=1.25)''',
    '''title(s, "Summary", dark=True)
text(s, 0.85, 2.35, 11.5, 3.4, [
    ("The recorder works, and the derived vibration channel measures a real physical event "
     "at 13 to 109 times its own noise floor.",
     {"size": 20, "color": WHITE, "space": 16}),
    ("The pilot is a feasibility result, not a reproducibility result. It has two trials per "
     "condition, one operator and one device.",
     {"size": 20, "color": WHITE, "space": 16}),
    ("One usability defect worth reporting: all six pilot sessions are stored with condition "
     "\\"controlled\\", including both slams. The app accepted the mislabelling without warning.",
     {"size": 20, "color": GOLD, "space": 16}),
    ("The pre-registered study runs this week.",
     {"size": 20, "color": WHITE}),
], line=1.3)''')

p.write_text(s)
print("build_deck.py retoned")
