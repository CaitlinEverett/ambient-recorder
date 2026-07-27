"""Turn the speaker notes into something a voice can read.

Two outputs.

`Narration.txt` is for a screen reader or Speechify: nothing but the words, in
order, with a slide marker line between them. No stage cues, no headers, no
budget arithmetic — anything a reader would say out loud that shouldn't be said
out loud has been removed here rather than trusted to the listener.

`Narration.mp3` is the same text spoken by a local neural TTS at the rate the
script is budgeted for, so the runtime estimate can be heard rather than
believed. It is a pacing reference, not a performance: the voice is even where a
person would push and drop.

Numbers are respelled for the synthesiser. "12.3 dB" reads correctly; "2 x 3",
"r of 0.97" and "p" do not, and a unit symbol read letter by letter breaks the
sentence more than a long word does.
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from set_notes import NOTES, WPM, PAUSE_S, spoken   # noqa: E402

MODEL = "/tmp/en_US-lessac-medium.onnx"
WAV, MP3, TXT = Path("/tmp/narration.wav"), Path("Narration.mp3"), Path("Narration.txt")

# Piper's default length_scale is 1.0 at roughly 175 wpm for this voice. Scaling
# inversely holds the spoken rate at whatever the script is budgeted for, so the
# audio length is a real check on the estimate rather than an unrelated number.
LENGTH_SCALE = 175 / WPM

SPEAKABLE = [
    (r"\bCS-7470\b", "C S seven four seven zero"),
    (r"\b2 ?[x×] ?3\b", "two by three"),
    (r"\bPearson r of\b", "Pearson correlation of"),
    (r"\bp is fixed\b", "p value is fixed"),
    (r"\bbar is 0\.025\b", "bar is zero point zero two five"),
    (r"\b0\.167\b", "zero point one six seven"),
    (r"\b0\.001\b", "zero point zero zero one"),
    (r"\b0\.97\b", "zero point nine seven"),
    (r"\b0\.90\b", "zero point nine zero"),
    (r"\b0\.675\b", "zero point six seven five"),
    (r"\b2\.77\b", "two point seven seven"),
    (r"\b2\.60\b", "two point six zero"),
    (r"\b2\.6 times\b", "two point six times"),
    (r"\b12\.3 decibels\b", "twelve point three decibels"),
    (r"\bJSON\b", "jason"),
    (r"\bTypeScript\b", "type script"),
    (r"\bQR code\b", "Q R code"),
    (r"\biOS\b", "i O S"),
    (r"\bAPI\b", "A P I"),
    (r"\b35%", "thirty-five percent"),
    (r"\bTA\b", "T A"),
    (r"\bg,", "gee,"),
    (r"—", ","),
    (r"\s+", " "),
]


def say(text: str) -> str:
    for pat, rep in SPEAKABLE:
        text = re.sub(pat, rep, text)
    return text.strip()


def main():
    parts, lines = [], []
    for i in sorted(NOTES):
        body = spoken(NOTES[i])
        if not body:
            continue
        head = NOTES[i].strip().split("\n")[0]
        lines.append(f"[{i:02d}] {head}\n\n{body}\n")
        parts.append(say(body))

    TXT.write_text("\n".join(lines))
    words = sum(len(p.split()) for p in parts)
    print(f"{TXT}  ·  {words} words")

    if not Path(MODEL).exists():
        print("no TTS voice at " + MODEL + " — text only")
        return

    # A blank line between slides becomes a pause in the synthesised audio,
    # standing in for the slide advance the estimate budgets for.
    script = ("\n\n" + " " * 0).join(parts)
    subprocess.run(
        [sys.executable, "-m", "piper", "-m", MODEL, "-f", str(WAV),
         "--length-scale", f"{LENGTH_SCALE:.3f}", "--sentence-silence", "0.16"],
        input=script, text=True, check=True, capture_output=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(WAV),
         "-af", f"apad=pad_dur={PAUSE_S}", "-b:a", "96k", str(MP3)], check=True)

    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(MP3)], capture_output=True, text=True,
        check=True).stdout)
    print(f"{MP3}  ·  {int(dur // 60)}:{dur % 60:04.1f} spoken "
          f"({words / dur * 60:.0f} wpm)")


if __name__ == "__main__":
    main()
