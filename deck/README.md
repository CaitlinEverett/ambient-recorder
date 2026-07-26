# Demo deck

`../../Covariate_Demo.pptx` — built on the Georgia Tech 2022 template, 18 slides,
four hidden so the shown deck runs 8:00. Speaker notes are riffable bullets with a
per-slide time budget, not a script.

## Rebuild

    ../analysis/.venv/bin/python build_deck.py    # slides, from gt.pptx + figures/
    ../analysis/.venv/bin/python set_notes.py     # notes + the 8-min hide set
    ../analysis/.venv/bin/python export_notes.py  # -> ../../Speaker_Notes.md

`build_deck.py` expects the GT template at `gt.pptx` in the working directory.
Run the three in that order; `set_notes.py` overwrites whatever notes
`build_deck.py` wrote.

## Design decisions

**Brand colours for furniture, validated palette inside the figures.** GT navy
and Tech gold carry titles, hexes and rules. They do not carry data series: run
through the categorical-palette checks, navy and GT teal fall below the chroma
floor (they read gray) and Tech gold falls outside the lightness band at about
2:1 on white. Brand colours are picked for a logo on a building, not for telling
four lines apart at 12pt. Gold fills shapes; DEEPGOLD (#7A5C00) is the darkened
step for the few places a gold-family text colour is wanted.

**The hexagon is the motif**, taken from the template's own shape language rather
than invented -- the GT deck already uses hex clusters. Numbered hexes carry list
items; initials carry the contributions slide.

**Dark navy opens and closes, white in between**, so the deck has a shape rather
than eighteen identical pages.

**Figures are rendered twice.** `figures.py` with `DECK = True` writes
`deck_*.png` without the suptitle or the footnote: the slide already carries a
title, and a chart repeating it puts the same sentence on screen twice. The
footnotes render at roughly 7pt once scaled into a slide -- that content moved to
the speaker notes. The `pdf` variants keep both, for the report.

**Images are fitted to their band, not set by width.** These figures run 1.7-2.1
aspect, so a 10.5in width is 5-6in tall against about 4.5in of usable height.
Three charts ran off the bottom of the slide and over the GT logo before this was
fixed -- caught by rendering and looking, not by reading the code.

## The 8-minute cut

Hidden (not deleted, so the full deck survives for the report appendix): 3 the
plan, 5 the channel table, 7 privacy, 16 the queue. Each is covered in a sentence
elsewhere.

For 6:00, also cut 12 and 13. Do not cut 14 -- the limitations slide is where the
reviewer's critique gets credited by name, which is worth more than any single
result.
