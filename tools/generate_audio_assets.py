"""Generate lightweight Sword Phantasia audio cues without APIs or downloads."""

from array import array
from pathlib import Path
import math
import wave


OUT = Path(__file__).resolve().parents[1] / "assets" / "audio"
RATE = 22050


def render(name, notes, seconds=6.0, volume=.16):
    total = int(RATE * seconds)
    samples = array("h")
    for index in range(total):
        time = index / RATE
        beat = int(time / .75) % len(notes)
        frequency = notes[beat]
        local = (time % .75) / .75
        envelope = min(1.0, local * 8) * max(.18, 1 - local * .70)
        base = math.sin(2 * math.pi * frequency * time)
        harmony = .35 * math.sin(2 * math.pi * frequency * 1.5 * time)
        pulse = .18 * math.sin(2 * math.pi * (frequency / 2) * time)
        samples.append(int(32767 * volume * envelope * (base + harmony + pulse) / 1.53))
    OUT.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT / name), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(RATE)
        output.writeframes(samples.tobytes())


def cue(name, start, end, seconds=.32, volume=.28):
    total = int(RATE * seconds)
    samples = array("h")
    for index in range(total):
        time = index / RATE
        ratio = index / max(1, total - 1)
        frequency = start + (end - start) * ratio
        envelope = math.sin(math.pi * ratio) ** 1.4
        samples.append(int(32767 * volume * envelope * math.sin(2 * math.pi * frequency * time)))
    OUT.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT / name), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(RATE)
        output.writeframes(samples.tobytes())


if __name__ == "__main__":
    render("bgm_menu.wav", (110.0, 146.8, 164.8, 130.8), 6.0, .12)
    render("amb_frontier.wav", (146.8, 164.8, 196.0, 174.6), 6.0, .10)
    render("amb_mosswood.wav", (98.0, 116.5, 130.8, 110.0), 6.0, .09)
    render("amb_crypt.wav", (82.4, 98.0, 87.3, 73.4), 6.0, .09)
    render("amb_throne.wav", (65.4, 77.8, 92.5, 69.3), 6.0, .11)
    cue("ui_select.wav", 330, 660)
    cue("victory.wav", 392, 988, .75, .24)
    print(f"Generated offline audio in {OUT}")
