# Analysis

Python analysis for the pre-registered H1-H3 tests (see docs/prereg-template.md).

    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    python reliability.py path/to/covariate_<id>_<stamp>.json

`reliability.py` holds the H2 metric definitions (Pearson r, bias, noise floor).
Alignment/windowing arrive with the Week-2 calibration data.
