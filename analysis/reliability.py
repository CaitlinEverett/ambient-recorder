"""Cross-device reliability metrics (proposal deliverable 4).

Loads two Covariate session JSONs recorded side by side, aligns them on the
sync fiducial, and computes per-channel Pearson r, bias, and noise floor —
the H2 pre-registered metrics.

Skeleton: interfaces and metric definitions only; alignment and windowing land
in Week 2 with the calibration data.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


def load_session(path: str | Path) -> tuple[dict, pd.DataFrame]:
    """Return (meta, samples) with samples as columns [t, channel, v0, v1, v2]."""
    record = json.loads(Path(path).read_text())
    rows = [
        {"t": s["t"], "channel": s["channel"],
         **{f"v{i}": v for i, v in enumerate(s["values"])}}
        for s in record["samples"]
    ]
    return record["meta"], pd.DataFrame(rows)


@dataclass
class AgreementResult:
    channel: str
    pearson_r: float
    bias: float          # mean(a - b) after alignment
    noise_floor_a: float # at-rest std, device A
    noise_floor_b: float
    n: int

    @property
    def passes_h2(self) -> bool:
        return self.pearson_r >= 0.9 and abs(self.bias) <= max(
            self.noise_floor_a, self.noise_floor_b
        )


def agreement(a: pd.Series, b: pd.Series,
              noise_a: float, noise_b: float, channel: str) -> AgreementResult:
    """H2 metrics for two aligned, equal-length series of one channel."""
    if len(a) != len(b) or len(a) < 2:
        raise ValueError("series must be aligned and equal length (n >= 2)")
    r, _ = stats.pearsonr(a, b)
    return AgreementResult(
        channel=channel,
        pearson_r=float(r),
        bias=float((a - b).mean()),
        noise_floor_a=noise_a,
        noise_floor_b=noise_b,
        n=len(a),
    )


def noise_floor(at_rest: pd.Series) -> float:
    """At-rest standard deviation — the channel's noise floor."""
    return float(at_rest.std(ddof=1))


# TODO(week2): fiducial detection + cross-device alignment (report offset)
# TODO(week2): resample-to-common-grid before correlation
# TODO(week3): H1 baseline/exceedance tests; H3 covariate regression

if __name__ == "__main__":
    import sys
    meta, df = load_session(sys.argv[1])
    print(f"{meta['experimentID']} @ {meta['site']} ({meta['condition']})")
    print(df.groupby("channel").agg(n=("t", "count"),
                                    t_min=("t", "min"), t_max=("t", "max")))
