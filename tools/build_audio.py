"""Assemble the voiceover, lay out scene slots from it, and write the music duck envelope.

Inputs : audio/vo/<scene>.mp3 + .words.json (from tools/make_voice.py), assets/music.mp3
Outputs: assets/voiceover.mp3      all lines placed on one track, loudness-normalised
         audio/timing.json         scene slots + each scene's word timings (scene-local seconds)
         index.html                scene host data-start/data-duration, root duration, audio tracks
Usage  : python3 tools/build_audio.py
"""
import json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENES = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9"]
LEAD = 0.6            # music alone before the first word
PRE = 0.45            # a scene starts this long before its line
GAP = {"s5": 0.9, "s6": 1.0}   # pause after a line (default below); a bit longer around the QR hero
GAP_DEFAULT = 0.75
TAIL = 3.2            # end card holds after the last word
MUSIC_OFFSET = 9.0    # skip the track's quiet intro: the full beat starts at 9.0 s
BED_FULL, BED_DUCK = 0.5, 0.2   # music gain with no voice / under the voice


def run(*a):
    subprocess.run(a, check=True)


def main():
    lines, t = [], LEAD
    for s in SCENES:
        words = json.loads((ROOT / f"audio/vo/{s}.words.json").read_text())
        speech_end = words[-1]["end"]
        lines.append({"scene": s, "vo_start": round(t, 3), "speech_end": speech_end, "words": words})
        t += speech_end + GAP.get(s, GAP_DEFAULT)
    total = round(lines[-1]["vo_start"] + lines[-1]["speech_end"] + TAIL, 2)

    # scene slots: each starts PRE before its line; s1 starts at 0
    for i, L in enumerate(lines):
        L["start"] = 0.0 if i == 0 else round(L["vo_start"] - PRE, 2)
    for i, L in enumerate(lines):
        end = lines[i + 1]["start"] if i + 1 < len(lines) else total
        L["duration"] = round(end - L["start"], 2)
        L["vo_local"] = round(L["vo_start"] - L["start"], 3)
        L["words_local"] = [{"text": w["text"], "start": round(w["start"] + L["vo_local"], 2), "end": round(w["end"] + L["vo_local"], 2)} for w in L["words"]]

    # one voiceover track: each clip delayed to its slot, then loudness-normalised
    inputs, filt = [], []
    for i, L in enumerate(lines):
        inputs += ["-i", str(ROOT / f"audio/vo/{L['scene']}.mp3")]
        ms = int(L["vo_start"] * 1000)
        filt.append(f"[{i}:a]aresample=48000,adelay={ms}|{ms}[a{i}]")
    mix = "".join(f"[a{i}]" for i in range(len(lines)))
    filt.append(f"{mix}amix=inputs={len(lines)}:normalize=0,apad=whole_dur={total},atrim=0:{total},loudnorm=I=-16:TP=-1.5:LRA=11[out]")
    run("ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[out]",
        "-ar", "48000", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "160k", str(ROOT / "assets/voiceover.mp3"))

    # music envelope: full in the open, ducked while the voice speaks, swell on the end card, fade out
    pts = [{"t": 0, "v": BED_FULL}]
    for L in lines:
        a, b = L["vo_start"], L["vo_start"] + L["speech_end"]
        pts += [{"t": round(max(a - 0.35, 0), 2), "v": BED_FULL if pts[-1]["v"] == BED_FULL else BED_DUCK},
                {"t": round(a, 2), "v": BED_DUCK}, {"t": round(b + 0.15, 2), "v": BED_DUCK}]
        nxt = lines[lines.index(L) + 1]["vo_start"] if L is not lines[-1] else None
        if nxt is None or nxt - b > 1.6:      # a real pause: let the bed come back up
            pts += [{"t": round(b + 0.6, 2), "v": BED_FULL}]
    pts += [{"t": round(total - 1.6, 2), "v": BED_FULL}, {"t": total, "v": 0}]
    pts = [p for i, p in enumerate(pts) if i == 0 or p["t"] > pts[i - 1]["t"]]
    automation = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": pts}]}, separators=(",", ":"))

    timing = {"total": total, "scenes": [{k: L[k] for k in ("scene", "start", "duration", "vo_local", "speech_end", "words_local")} for L in lines]}
    (ROOT / "audio/timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1))

    # index.html: scene slots, root duration, audio tracks
    p = ROOT / "index.html"
    html = p.read_text()
    html = re.sub(r'(id="root"[^>]*?data-duration=")[\d.]+(")', rf'\g<1>{total}\2', html, count=1, flags=re.S)
    for L in lines:
        pat = re.compile(rf'(<div id="{L["scene"]}" [^>]*?data-start=")[\d.]+(" data-duration=")[\d.]+(")', re.S)
        html, n = pat.subn(rf'\g<1>{L["start"]}\g<2>{L["duration"]}\3', html)
        assert n == 1, L["scene"]
    audio = (f'      <audio id="voiceover" src="assets/voiceover.mp3" data-start="0" data-duration="{total}" data-track-index="3" data-volume="1"></audio>\n'
             f'      <audio id="music" src="assets/music.mp3" data-start="0" data-duration="{total}" data-media-start="{MUSIC_OFFSET}" data-track-index="4" data-volume="1"\n'
             f'        data-automation="{automation.replace(chr(34), "&quot;")}"></audio>\n')
    html = re.sub(r'      <!-- Audio[\s\S]*?-->\n|      <audio id="voiceover"[\s\S]*?</audio>\n      <audio id="music"[\s\S]*?</audio>\n', audio, html, count=1)
    p.write_text(html)

    print(f"total {total}s")
    for L in lines:
        print(f'{L["scene"]}: start {L["start"]:6.2f}  dur {L["duration"]:5.2f}  voice {L["vo_local"]:.2f}–{L["vo_local"] + L["speech_end"]:.2f} (local)')


main()
