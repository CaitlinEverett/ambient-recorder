"""Figures for the Covariate demo video and final report, from the real pilot data.

Renders 1920x1080 PNGs (video-safe) plus PDFs for the report. Palette is the
validated categorical default: blue / orange / aqua, all-pairs CVD-checked.
Every series is direct-labelled, so identity never rests on colour alone.
"""
from __future__ import annotations

import glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from events import (load_session, vib_energy, vib_peak, vib_rms_peak,
                    accel_excess, baseline_floor, accel_excess_series)

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e2e1dd"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
EV = {"BASE1": 10.54, "CLOSE1": 8.92, "CLOSE2": 8.79, "SLAM1": 7.69, "SLAM2": 7.83}

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "text.color": INK,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.edgecolor": GRID, "grid.color": GRID, "font.size": 15,
    "axes.spines.top": False, "axes.spines.right": False,
})

S = {p.split("_")[-1][:-5]: load_session(p) for p in sorted(glob.glob("door/*.json"))}
FLOOR = {k: float(np.median([baseline_floor(S[b], k) for b in ("BASE1", "BASE2")]))
         for k in ("energy", "peak", "rms", "accel")}


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(f"figures/{name}.{ext}", dpi=160 if ext == "png" else None,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"  figures/{name}.png")


# --- Fig 1 — the metric choice changes the conclusion -------------------------
# Form: magnitude comparison across two conditions, three ways of measuring the
# same events. Log y because the quantities span two decades; each trial is a
# point rather than a bar, because with n=2 a bar would imply a distribution
# that does not exist.

def fig_metrics():
    """Honest version: at n=2 all three statistics order the conditions correctly.
    What differs is the MARGIN — and margin is what survives more trials."""
    metrics = [(vib_rms_peak, "rms", "peak window RMS", "what the pilot report used"),
               (vib_peak, "peak", "peak sample", "alignment-invariant"),
               (vib_energy, "energy", "energy integral", "\u03a3 rms\u00b2\u00b7\u0394t")]
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 6.0), sharey=True)
    for ax, (fn, fk, title, sub) in zip(axes, metrics):
        vals = {c: [fn(S[f"{c}{i}"], EV[f"{c}{i}"]) for i in (1, 2)]
                for c in ("CLOSE", "SLAM")}
        base = float(np.mean(vals["CLOSE"]))          # normalise: close = 1.0
        v = {c: [x / base for x in vals[c]] for c in vals}
        gap = min(v["SLAM"]) / max(v["CLOSE"])        # quietest slam vs loudest close
        for x, (cond, col) in enumerate([("CLOSE", BLUE), ("SLAM", ORANGE)]):
            ax.plot([x, x], [min(v[cond]), max(v[cond])], color=col, lw=10, alpha=.20,
                    solid_capstyle="round", zorder=1)
            ax.scatter([x, x], v[cond], s=130, color=col, zorder=3,
                       edgecolor=SURFACE, linewidth=2)
        ax.axhspan(max(v["CLOSE"]), min(v["SLAM"]), color=AQUA, alpha=.13, zorder=0)
        ax.annotate("", xy=(1.42, min(v["SLAM"])), xytext=(1.42, max(v["CLOSE"])),
                    arrowprops=dict(arrowstyle="<->", color=AQUA, lw=1.8))
        ax.text(1.47, np.sqrt(max(v["CLOSE"]) * min(v["SLAM"])), f"{gap:.2f}\u00d7",
                color="#0f7a55", fontsize=15, fontweight="bold", va="center")
        ax.set_title(f"{title}\n{sub}", fontsize=14, color=INK, pad=10)
        ax.set_xticks([0, 1]); ax.set_xticklabels(["close", "slam"], fontsize=15)
        ax.set_xlim(-.5, 2.05); ax.set_yscale("log")
        ax.grid(axis="y", lw=.8, alpha=.5); ax.set_axisbelow(True)
    axes[0].set_ylabel("relative to the mean close event", fontsize=13.5)
    axes[0].axhline(1.0, color=GRID, lw=1, zorder=0)
    fig.suptitle("Same four door events, three statistics \u2014 the separation margin differs by 2\u00d7",
                 fontsize=18, fontweight="bold", y=1.02)
    fig.text(0, -.06,
             "Each dot is one trial (n=2 per condition); the bar spans the two, the green band "
             "and arrow mark the gap between the loudest close and the quietest slam.\n"
             "All three statistics order the conditions correctly here \u2014 but peak window RMS "
             "leaves a 1.4\u00d7 margin where the energy integral leaves 2.7\u00d7. At n=2 none of this "
             "is significant:\nthe smallest p an exact test can return with two trials per condition "
             "is 0.167. Margin is what survives more trials, which is why the protocol now fixes n=6.",
             fontsize=12, color=INK2, va="top")
    save(fig, "fig1_metric_choice")


# --- Fig 2 — the derived channel vs the raw sensor it comes from --------------
# Small multiples, never a dual axis: the two panels are different quantities in
# different units and share only their time base.

def fig_derived(sess="SLAM1"):
    s, te = S[sess], EV[sess]
    t0, t1 = te - 2.0, te + 3.0
    ta, ex = accel_excess_series(s)
    m = (ta >= t0) & (ta <= t1)
    v = s.channel("vibration"); vm = (v["t"] >= t0) & (v["t"] <= t1)

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11.5, 6.4), sharex=True,
                                 gridspec_kw={"hspace": .28})
    a1.plot(ta[m], ex[m] + 1.0, color=INK2, lw=1.4)
    a1.axhline(1.0, color=GRID, lw=1)
    a1.set_ylabel("raw |a|   (g)", fontsize=13)
    a1.set_title("Raw accelerometer magnitude — the event is a rounding error on top of gravity",
                 fontsize=13.5, color=INK, loc="left", pad=8)
    a1.text(t1, 1.0 + (ex[m].max()) * .55, f"peak {(1+ex[m].max()):.3f} g\n"
            f"{ex[m].max()*100:.1f}% above 1 g", ha="right", fontsize=12, color=INK2)

    a2.plot(v["t"][vm], v["v1"][vm], color=BLUE, lw=2.2)
    a2.axhline(FLOOR["peak"], color=ORANGE, lw=1.6, ls="--")
    a2.text(t0 + .1, FLOOR["peak"] * 1.35, "baseline noise floor", color=ORANGE, fontsize=12)
    pk = float(v["v1"][vm].max())
    a2.annotate(f"{pk / FLOOR['peak']:.0f}× the floor", xy=(te, pk),
                xytext=(te + .75, pk * .82), fontsize=13.5, color=BLUE, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=BLUE, lw=1.4))
    a2.set_ylabel("derived vibration\npeak   (g)", fontsize=13)
    a2.set_xlabel("session time (s)", fontsize=13)
    a2.set_title("Derived vibration channel — same sensor, same samples, gravity subtracted",
                 fontsize=13.5, color=BLUE, loc="left", pad=8)
    for a in (a1, a2):
        a.grid(axis="y", lw=.8, alpha=.5); a.set_axisbelow(True); a.set_xlim(t0, t1)
    fig.suptitle("The hack: a derived channel outperforms the raw sensor it is derived from",
                 fontsize=17, fontweight="bold", y=1.0)
    save(fig, "fig2_derived_vs_raw")


# --- Fig 3 — the sync fiducial was never lost --------------------------------

def fig_fiducial(sess="CLOSE2"):
    s = S[sess]
    ta, ex = accel_excess_series(s)
    m = ta <= 5.0
    v = s.channel("vibration"); vm = v["t"] <= 5.0

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11.5, 6.0), sharex=True,
                                 gridspec_kw={"hspace": .3})
    a1.plot(ta[m], ex[m], color=BLUE, lw=1.3)
    a1.set_ylabel("accelerometer\n|a| − 1  (g)", fontsize=13)
    a1.set_title("50 Hz accelerometer — every tap resolved", fontsize=13.5,
                 color=BLUE, loc="left", pad=8)
    a2.plot(v["t"][vm], v["v0"][vm], color=ORANGE, lw=2.2, marker="o", ms=5)
    a2.set_ylabel("vibration channel\nRMS  (g)", fontsize=13)
    a2.set_xlabel("session time (s)", fontsize=13)
    a2.set_title("5 Hz derived channel — the same taps, collapsed into single 200 ms windows",
                 fontsize=13.5, color=ORANGE, loc="left", pad=8)
    for a in (a1, a2):
        a.grid(axis="y", lw=.8, alpha=.5); a.set_axisbelow(True); a.set_xlim(0, 5)
    fig.suptitle("The sync taps were never lost — they were looked for in the wrong channel",
                 fontsize=17, fontweight="bold", y=1.0)
    fig.text(0, -.03,
             "The pilot report concluded only one of three sync taps was recorded. Three raps "
             "inside a few hundred milliseconds fall into one or two\n200 ms windows of the 5 Hz "
             "derived channel. The 50 Hz raw accelerometer had them the whole time — a reporting "
             "artifact, not a data-quality failure.",
             fontsize=11.5, color=INK2, va="top")
    save(fig, "fig3_fiducial")


if __name__ == "__main__":
    import os
    os.makedirs("figures", exist_ok=True)
    print("rendering:")
    fig_metrics(); fig_derived(); fig_fiducial()
