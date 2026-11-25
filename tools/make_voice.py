"""Generate the voiceover with edge-tts, one file per scene, plus word timings.

Reads audio/vo_script.json and writes:
  audio/vo/<scene>.mp3          one clip per scene (Laith, rate from the script)
  audio/vo/<scene>.words.json   word timings in seconds [{text, start, end}]
  renders/voice-sample-amany.mp3  opening line in ar-SY-AmanyNeural, cut to 15 s

The session's HTTPS proxy re-terminates TLS, so the proxy CA bundle is trusted
explicitly and the proxy URL is passed to edge-tts.
Usage: python3 tools/make_voice.py [scene ...]
"""
import asyncio, json, os, subprocess, sys
from pathlib import Path

import certifi
CA = "/root/.ccr/ca-bundle.crt"
if os.path.exists(CA):
    certifi.where = lambda: CA
import edge_tts
import edge_tts.communicate as _c
_c.certifi.where = certifi.where

ROOT = Path(__file__).resolve().parent.parent
PROXY = os.environ.get("HTTPS_PROXY") or None


async def synth(text, voice, rate, out_mp3, out_words=None):
    com = edge_tts.Communicate(text, voice, rate=rate, proxy=PROXY, boundary="WordBoundary")
    words = []
    with open(out_mp3, "wb") as f:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                s = chunk["offset"] / 1e7
                words.append({"text": chunk["text"], "start": round(s, 3), "end": round(s + chunk["duration"] / 1e7, 3)})
    if out_words:
        Path(out_words).write_text(json.dumps(words, ensure_ascii=False, indent=1))
    return words


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


async def main(only):
    cfg = json.loads((ROOT / "audio/vo_script.json").read_text())
    outdir = ROOT / "audio/vo"
    outdir.mkdir(parents=True, exist_ok=True)
    for scene, text in cfg["lines"].items():
        if only and scene not in only:
            continue
        mp3 = outdir / f"{scene}.mp3"
        await synth(text, cfg["voice"], cfg["rate"], mp3, outdir / f"{scene}.words.json")
        print(f"{scene}: {duration(mp3):.2f}s")
    if not only or "amany" in only:
        tmp = outdir / "amany-s1-full.mp3"
        await synth(cfg["lines"]["s1"] + " " + cfg["lines"]["s2"], "ar-SY-AmanyNeural", cfg["rate"], tmp)
        dst = ROOT / "renders/voice-sample-amany.mp3"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-t", "15", "-af", "afade=t=out:st=14.4:d=0.6",
                        "-c:a", "libmp3lame", "-b:a", "128k", str(dst)], check=True)
        tmp.unlink()
        print(f"amany sample: {duration(dst):.2f}s")


asyncio.run(main(set(sys.argv[1:])))
