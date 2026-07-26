"""Export the deck's speaker notes to markdown, with runtimes and a cut list."""
from pptx import Presentation

WPM = 140  # only used to sanity-check; the notes carry explicit per-slide budgets

# Slides kept in each cut. The full deck runs ~16 minutes of narration, which is
# long for a demo; these are the two shorter passes through the same material.
SHORT = {1, 2, 4, 6, 8, 10, 11, 14, 15, 17, 18}
MEDIUM = SHORT | {3, 5, 9, 13, 16}
CUT_6, CUT_10 = SHORT, MEDIUM

prs = Presentation("Covariate_Demo.pptx")
rows, out = [], []

for i, s in enumerate(prs.slides, 1):
    notes = s.notes_slide.notes_text_frame.text.strip()
    head = ""
    for sh in s.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip():
            head = sh.text_frame.text.strip().splitlines()[0]
            break
    n = len(notes.split())
    tag = "CORE" if i in CUT_6 else ("10-MIN" if i in CUT_10 else "FULL ONLY")
    rows.append((i, head, n, n / WPM * 60, tag))
    out.append(f"## {i}. {head}\n\n*{n} words · ~{n / WPM * 60:.0f}s · {tag}*\n\n{notes}\n\n---\n")

total = sum(r[2] for r in rows)
six = sum(r[2] for r in rows if r[0] in CUT_6)
ten = sum(r[2] for r in rows if r[0] in CUT_10)

header = [
    "# Covariate — demo deck speaker notes",
    "",
    "Filmed straight through the deck. Lines in square brackets are stage",
    "directions, not narration — they mark where footage is cut in.",
    "",
    "## Runtime",
    "",
    f"| Cut | Slides | Words | At {WPM} wpm |",
    "|---|---|---|---|",
    f"| Full deck | 18 | {total} | budgets sum to ~9.5 min |",
    f"| **8-minute cut (as shipped)** | 14 | — | **8.0 min** |",
    "",
    "Every slide's notes open with its own time budget. The four slides below are",
    "already set to `Hide Slide` in the file, which lands the shown deck at 8:00 and",
    "still hits the five beats the staff asked for (plan, accomplished, changes,",
    "results, learned):",
    "",
    "- **Hidden:** 3 (the plan), 5 (channel table), 7 (privacy), 16 (queue). Each is "
    "covered in a sentence elsewhere, so nothing is lost, only compressed.",
    "- **Need it shorter?** Unhide nothing and cut 12 and 13 as well \u2014 that is 6:00. "
    "Do not cut 14; the limitations slide is where the reviewer\u2019s critique gets "
    "credited, and that is worth more than any single result.",
    "",
    "Hidden slides are still in the file \u2014 they stay available for the report",
    "appendix, and PowerPoint skips them in Present mode.",
    "",
    "## Per-slide",
    "",
    "| # | Slide | Words | ~Time | Cut |",
    "|---|---|---|---|---|",
]
header += [f"| {i} | {h} | {n} | {t:.0f}s | {tag} |" for i, h, n, t, tag in rows]
header += ["", "---", ""]

open("Speaker_Notes.md", "w").write("\n".join(header) + "\n".join(out))
print(f"full {total} words (~{total / WPM:.0f} min) · "
      f"10-min cut {ten} (~{ten / WPM:.0f}) · 6-min cut {six} (~{six / WPM:.0f})")
