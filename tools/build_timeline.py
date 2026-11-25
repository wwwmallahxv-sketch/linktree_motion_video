"""Lay out the scene slots for the music-only cut and write the music track.

Scene lengths are set for reading (every caption holds at least 2.5 s). Each cut is then
snapped to the nearest beat of assets/music.mp3 (beat times from `hyperframes beats`, cached in
tools/music_beats.json), and index.html gets the slot times, the root duration and a single
music track with a fade-in and a fade-out.
Usage: python3 tools/build_timeline.py
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# reading-time length of each scene, seconds
SCENES = [("s1", 10.5), ("s2", 6.2), ("s3", 11.0), ("s4", 19.0), ("s5", 15.5),
          ("s6", 25.2), ("s7", 10.5), ("s8", 11.0), ("s9", 9.5)]
MUSIC_OFFSET = 9.0      # the track's full beat starts at 9.0 s (quiet intro skipped)
MUSIC_VOLUME = 0.7      # ≈ -3 dB: the track is mastered loud (≈ -11 LUFS); this sits near -14 LUFS
FADE_IN, FADE_OUT = 1.2, 2.8


def main():
    beats = [b - MUSIC_OFFSET for b in json.loads((ROOT / "tools/music_beats.json").read_text())["beats"] if b >= MUSIC_OFFSET]
    snap = lambda t: min(beats, key=lambda b: abs(b - t))
    cuts, t = [0.0], 0.0
    for _, d in SCENES[:-1]:
        t += d
        cuts.append(round(snap(t), 3))
    total = round(cuts[-1] + SCENES[-1][1], 2)
    p = ROOT / "index.html"
    html = p.read_text()
    html = re.sub(r'(id="root"[^>]*?data-duration=")[\d.]+(")', rf"\g<1>{total}\2", html, count=1, flags=re.S)
    for i, (sid, _) in enumerate(SCENES):
        start = cuts[i]
        end = cuts[i + 1] if i + 1 < len(cuts) else total
        pat = re.compile(rf'(<div id="{sid}" [^>]*?data-start=")[\d.]+(" data-duration=")[\d.]+(")', re.S)
        html, n = pat.subn(rf"\g<1>{start}\g<2>{round(end - start, 3)}\3", html)
        assert n == 1, sid
        print(f"{sid}: {start:7.3f} → {end:7.3f}  ({end - start:.2f}s)")
    music = (f'      <audio id="music" src="assets/music.mp3" data-start="0" data-duration="{total}" data-media-start="{MUSIC_OFFSET}"'
             f' data-track-index="4" data-volume="{MUSIC_VOLUME}" data-fade-in="{FADE_IN}" data-fade-out="{FADE_OUT}"></audio>\n')
    html, n = re.subn(r'      <audio id="voiceover"[\s\S]*?</audio>\n', "", html)
    html, n2 = re.subn(r'      <audio id="music"[\s\S]*?</audio>\n', music, html)
    assert n2 == 1
    p.write_text(html)
    print(f"total {total}s; beat-snapped cuts; music at {MUSIC_VOLUME}, fade in {FADE_IN}s / out {FADE_OUT}s")


main()
