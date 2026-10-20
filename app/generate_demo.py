
import json
from pathlib import Path

import numpy as np
from scipy.io.wavfile import write

import sys

SAMPLE_RATE = 48000
DURATION = int(sys.argv[1]) if len(sys.argv) > 1 else 30
DURATION = max(5, min(DURATION, 300))
OUTPUT = Path("outputs/demo")
OUTPUT.mkdir(parents=True, exist_ok=True)

length = SAMPLE_RATE * DURATION
stems = {
    "harmony": np.zeros(length, dtype=np.float32),
    "bass": np.zeros(length, dtype=np.float32),
    "melody": np.zeros(length, dtype=np.float32),
    "drums": np.zeros(length, dtype=np.float32),
}

rng = np.random.default_rng(42)
beat = 60 / 100
bar = beat * 4


def add_note(track, start, duration, frequency, volume):
    first = int(start * SAMPLE_RATE)
    count = min(int(duration * SAMPLE_RATE), length - first)
    if count <= 0:
        return

    t = np.arange(count, dtype=np.float32) / SAMPLE_RATE
    fade = np.minimum(1, t / 0.02)
    fade *= np.minimum(1, (duration - t) / 0.08)
    fade = np.clip(fade, 0, 1)

    sound = np.sin(2 * np.pi * frequency * t)
    sound += 0.2 * np.sin(4 * np.pi * frequency * t)
    track[first:first + count] += volume * sound * fade


chords = [
    [261.63, 329.63, 392.00],
    [220.00, 261.63, 329.63],
    [174.61, 220.00, 261.63],
    [196.00, 246.94, 293.66],
]

for bar_number in range(int(DURATION / bar)):
    start = bar_number * bar
    chord = chords[bar_number % len(chords)]

    for frequency in chord:
        add_note(stems["harmony"], start, bar * 0.9,
                 frequency, 0.08)

    for beat_number in range(4):
        beat_start = start + beat_number * beat
        add_note(stems["bass"], beat_start, beat * 0.7,
                 chord[0] / 2, 0.12)

        add_note(stems["melody"], beat_start, beat * 0.5,
                 chord[(beat_number + 1) % 3] * 2, 0.06)

for beat_number in range(int(DURATION / beat)):
    start = beat_number * beat
    first = int(start * SAMPLE_RATE)
    count = min(int(0.12 * SAMPLE_RATE), length - first)
    t = np.arange(count, dtype=np.float32) / SAMPLE_RATE

    if beat_number % 2 == 0:
        sound = np.sin(2 * np.pi * (90 - 200 * t) * t)
        sound *= np.exp(-25 * t)
        stems["drums"][first:first + count] += 0.2 * sound
    else:
        noise = rng.normal(0, 1, count).astype(np.float32)
        noise *= np.exp(-35 * t)
        stems["drums"][first:first + count] += 0.035 * noise

# Intentional fade-out over the final two seconds.
fade_length = 2 * SAMPLE_RATE
fade = np.linspace(1, 0, fade_length, dtype=np.float32)
for track in stems.values():
    track[-fade_length:] *= fade

gains = {
    "harmony": 0.65,
    "bass": 0.70,
    "melody": 0.65,
    "drums": 0.55,
}


def save_wav(path, audio):
    peak = float(np.max(np.abs(audio)))
    if peak > 0:
        audio = audio * min(1.0, 0.89 / peak)
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    write(str(path), SAMPLE_RATE, pcm)


for name, audio in stems.items():
    save_wav(OUTPUT / f"{name}.wav", audio)

mix = sum(stems[name] * gains[name] for name in stems)
save_wav(OUTPUT / "mix.wav", mix)

manifest = {
    "title": "Procedural Background Music Demo",
    "duration_s": DURATION,
    "sample_rate_hz": SAMPLE_RATE,
    "tempo_bpm": 100,
    "key": "C major / A minor",
    "format": "WAV PCM 16-bit",
    "generation_method": "procedural synthesis; no AI model",
    "stems": {
        name: {"file": f"{name}.wav", "gain": gains[name]}
        for name in stems
    },
    "mix": "mix.wav",
    "note": "Prototype using synthesized tones and percussion; "
            "not sampled acoustic instruments. Loudness and "
            "true peak compliance have not been measured."
}

(OUTPUT / "music_manifest.json").write_text(
    json.dumps(manifest, indent=2),
    encoding="utf-8"
)

print("Demo generation complete!")
print("Output folder:", OUTPUT.resolve())
print("Files:", ", ".join(p.name for p in OUTPUT.iterdir()))
print("Duration: 30 seconds | Sample rate: 48000 Hz")
