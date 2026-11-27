"""Café soundtrack = soundtrack-v4, unchanged, plus one key-press for the 10th letter of «sukkar-hel».

The v4 mix is decoded sample-for-sample and only the new key-press is added at 0:19.95
(scene 3 local 1.95 = 1.05 + 9 × 0.1), at the same level (0.16) as the other typing cues.
Usage: python3 tools/build_soundtrack_cafe.py
"""
import subprocess
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
T, GAIN = 19.95, 0.16


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<i2").reshape(-1, 2).astype(np.int32)


base = decode(ROOT / "audio/soundtrack-v4.flac")
key = decode(ROOT / "assets/sfx/key-press.mp3")
out = base.copy()
i = int(round(T * SR))
seg = np.round(key[: len(out) - i] * GAIN).astype(np.int32)
out[i:i + len(seg)] += seg
assert np.abs(out).max() <= 32767, "would clip"
pcm = out.astype("<i2").tobytes()
dst = ROOT / "audio/soundtrack-cafe.flac"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "flac", str(dst)], input=pcm, check=True)
print(f"{dst}: key-press added at {T}s ({len(seg) / SR:.2f}s long)")
