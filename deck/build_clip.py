"""Rebuild the two-site pilot clip as continuous fast motion.

The earlier cut was assembled from keyframe-only decodes, which spaces frames
irregularly and reads as stop motion rather than fast forward. Here both halves
are resampled evenly: `setpts` compresses time by a fixed factor and `fps=24`
resamples on a regular grid, so the motion is continuous at speed.

Sources are the 8x/4x proxies, so the effective speeds are the product.
"""
import subprocess
from pathlib import Path

SRC = Path("/mnt/user-data/uploads/experiment results/proxy")
OUT = Path("media")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

W, H, FPS = 540, 960, 24

# (proxy file, proxy speed already applied, target seconds, caption)
HALVES = [
    ("doorslam_4x.mp4", 4, 7.5, "Toronto  -  C. Kimberley"),
    ("dji_8x.mp4", 8, 8.5, "Chicago  -  C. Everett"),
]


def label(caption: str) -> str:
    # Navy plate behind the text so the caption survives a light doorway.
    return (
        f"drawtext=fontfile={FONT}:text='{caption}':"
        f"fontcolor=white:fontsize=30:x=(w-text_w)/2:y=h-96:"
        f"box=1:boxcolor=0x003057@0.92:boxborderw=16"
    )


def half(name: str, seconds: float, caption: str, dst: Path):
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(SRC / name)],
        capture_output=True, text=True, check=True).stdout.strip())
    factor = dur / seconds
    # Motion blur before decimation. Dropping frames at 10x leaves a person
    # teleporting between positions, which is the stop-motion feel; averaging
    # each output frame over the source frames it replaces turns the same
    # footage into streaks, which is what a time lapse is supposed to look
    # like. tmix is a rolling mean, so the window is the speed factor.
    blur = max(2, round(factor))
    vf = (f"tmix=frames={blur},setpts=PTS/{factor:.5f},fps={FPS},"
          f"scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H},{label(caption)}")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(SRC / name),
         "-vf", vf, "-an", "-c:v", "libx264", "-preset", "slow",
         "-crf", "26", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         str(dst)], check=True)
    return factor


if __name__ == "__main__":
    tmp = Path("/tmp/vf")
    tmp.mkdir(exist_ok=True)
    parts = []
    for i, (name, proxy, secs, cap) in enumerate(HALVES):
        dst = tmp / f"h{i}.mp4"
        f = half(name, secs, cap, dst)
        parts.append(dst)
        print(f"  {name}: {f:.2f}x on top of {proxy}x proxy "
              f"= {f * proxy:.0f}x real time -> {secs}s")

    lst = tmp / "concat.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", str(lst), "-c", "copy", str(OUT / "pilot_two_sites.mp4")],
        check=True)

    # Poster frame: a moment from Chris's half, so the still on the slide is
    # the collaborator's footage rather than a black frame.
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-ss", "2.5", "-i",
         str(OUT / "pilot_two_sites.mp4"), "-frames:v", "1", "-q:v", "3",
         str(OUT / "pilot_poster.jpg")], check=True)

    size = (OUT / "pilot_two_sites.mp4").stat().st_size
    print(f"  media/pilot_two_sites.mp4  {size / 1024:.0f} KB")
