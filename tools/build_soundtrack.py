"""Build the v4 soundtrack: music + sound effects timed to preview-v1's animations.

The picture is NOT touched: this writes a standalone audio file that is later muxed onto the
rendered video with `ffmpeg -c:v copy`. Cue times are scene-local seconds read from the v1
composition scripts (compositions/*.html at commit 49e9bf8); scene starts are read from index.html.

Sounds: assets/sfx/*.mp3 (HyperFrames bundled library, Pixabay Content License, no attribution),
plus two tones synthesised here (a phone ring and a camera-focus beep). Music: assets/music.mp3
("Lo-Fi 04" by Lily J, Mixkit Stock Music Free License).

Usage: python3 tools/build_soundtrack.py OUT.wav [cues.md]
"""
import re, subprocess, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
MUSIC_OFFSET = 9.0          # skip the track's quiet intro
MUSIC_GAIN = 0.55           # ≈ -5 dB: the track is mastered loud
FADE_IN, FADE_OUT = 1.5, 3.0

# (scene, local second, sound, gain, what it marks) — local seconds from the v1 scene scripts
CUES = [
    # 1 · the problem (s1-problem.html): bubbles at times[] = 0.85, 1.7, 2.45, 3.1; links sent 4.95 + i*0.28;
    #     chips fly 6.55 + i*0.22; phone drops 8.9
    ("s1", 0.85, "ping", 0.16, "customer message: «شو رقمك؟»"),
    ("s1", 1.70, "ping", 0.16, "customer message: «وين موقعك؟»"),
    ("s1", 2.45, "ping", 0.16, "customer message: «عندك إنستغرام؟»"),
    ("s1", 3.10, "ping", 0.16, "customer message"),
    ("s1", 4.95, "click-soft", 0.22, "owner sends link 1"),
    ("s1", 5.23, "click-soft", 0.22, "owner sends link 2"),
    ("s1", 5.51, "click-soft", 0.22, "owner sends link 3"),
    ("s1", 5.79, "click-soft", 0.22, "owner sends link 4"),
    ("s1", 6.07, "click-soft", 0.22, "owner sends link 5"),
    ("s1", 6.50, "whoosh-short", 0.24, "link chips fly out of the phone"),
    ("s1", 8.90, "whoosh", 0.20, "phone drops away (scene change)"),
    # 2 · the answer (s2-answer.html): chips pulled 0.25, flash 1.15, pill 1.2, logo 1.95, pill returns 7.1
    ("s2", 0.25, "whoosh-short", 0.22, "link chips pulled together"),
    ("s2", 1.15, "pop", 0.32, "links merge into one (snap)"),
    ("s2", 1.95, "sparkle", 0.12, "Linktrees.link logo"),
    ("s2", 7.10, "whoosh-short", 0.18, "hand-off to the address bar (scene change)"),
    # 3 · your link (s3-link.html): keystrokes chikenhut 1.05 + i*0.1, yourshop 5.2 + i*0.09, yourname 7.6 + i*0.09;
    #     label 2.25; link copies land in the apps 10.0 / 10.3 / 10.6; whip 11.45
    *[("s3", round(1.05 + i * 0.10, 2), "key-press", 0.16, f"typing «chikenhut» ({c})") for i, c in enumerate("chikenhut")],
    ("s3", 2.25, "pop", 0.18, "«اسم محلك» tag"),
    *[("s3", round(5.20 + i * 0.09, 2), "key-press", 0.14, f"typing «yourshop» ({c})") for i, c in enumerate("yourshop")],
    *[("s3", round(7.60 + i * 0.09, 2), "key-press", 0.14, f"typing «yourname» ({c})") for i, c in enumerate("yourname")],
    ("s3", 10.00, "click-soft", 0.20, "link lands in WhatsApp"),
    ("s3", 10.30, "click-soft", 0.20, "link lands in Instagram"),
    ("s3", 10.60, "click-soft", 0.20, "link lands in Facebook"),
    ("s3", 11.45, "whoosh", 0.20, "whip up (scene change)"),
    # 4 · what's on the page (s4-page.html): taps 4.45 / 8.0 / 11.05 / 14.0; chat 5.25 / 5.85; rings from 8.4;
    #     card 11.2; toast 11.95; pin 14.65 (bounce lands ≈ 14.85); socials 17.75 + i*0.18
    ("s4", 0.00, "whoosh-short", 0.18, "phone rises"),
    ("s4", 4.45, "click", 0.26, "WhatsApp icon tapped"),
    ("s4", 5.25, "pop", 0.16, "chat message"),
    ("s4", 5.85, "ping", 0.14, "restaurant replies"),
    ("s4", 8.00, "click", 0.26, "call button tapped"),
    ("s4", 8.40, "ring", 0.18, "phone ringing (1st ring)"),
    ("s4", 9.55, "ring", 0.14, "phone ringing (2nd ring, cut as the call screen closes)"),
    ("s4", 11.05, "click", 0.26, "save-contact button tapped"),
    ("s4", 11.20, "whoosh-short", 0.16, "contact card drops into the phone"),
    ("s4", 11.95, "chime", 0.14, "«انحفظ الرقم»"),
    ("s4", 14.00, "click", 0.26, "«فتح في الخرائط» tapped"),
    ("s4", 14.85, "pop", 0.26, "map pin drops"),
    ("s4", 17.75, "pop", 0.16, "Instagram icon"),
    ("s4", 17.93, "pop", 0.16, "Facebook icon"),
    ("s4", 18.11, "pop", 0.16, "WhatsApp icon"),
    # 5 · made for you (s5-custom.html): re-skin swaps 0.9 / 1.9 / 2.9; signal 6.4; fast 7.4; pen 9.3; new icon 9.85;
    #     «تم التعديل» 10.25; exit 11.5
    ("s5", 0.90, "sparkle", 0.10, "re-skin shimmer: Devmmnd look"),
    ("s5", 1.90, "sparkle", 0.10, "re-skin shimmer: Courseing look"),
    ("s5", 2.90, "sparkle", 0.10, "re-skin shimmer: back to Chiken Hut"),
    ("s5", 6.40, "glitch-3", 0.10, "«نت ضعيف» badge"),
    ("s5", 7.40, "ping", 0.16, "«فتحت فوراً» badge"),
    ("s5", 9.85, "pop", 0.16, "new account added"),
    ("s5", 10.25, "chime", 0.12, "«تم التعديل»"),
    ("s5", 11.50, "whoosh", 0.18, "into the QR section (scene change)"),
    # 6 · the QR code (s6-qr.html): card 0.0; carry 3.2; whips 6.75 / 12.8 / 15.3; dip cut 9.8; size 17.6, zoom 18.6;
    #     hand 19.75; viewfinder locks 20.95; page opens 21.6
    ("s6", 0.00, "pop", 0.18, "QR card appears"),
    ("s6", 3.20, "whoosh", 0.18, "QR flies onto the table tent"),
    ("s6", 6.75, "whoosh-short", 0.18, "whip to the glass door"),
    ("s6", 9.80, "whoosh-short", 0.16, "cut to the menu"),
    ("s6", 12.80, "whoosh-short", 0.18, "whip to the business cards"),
    ("s6", 15.30, "whoosh-short", 0.18, "whip to the bag"),
    ("s6", 18.60, "whoosh-cinematic", 0.16, "zoom: any size"),
    ("s6", 19.75, "whoosh-short", 0.16, "hand raises the phone"),
    ("s6", 20.95, "focus", 0.20, "camera focus beep (viewfinder locks)"),
    ("s6", 21.60, "chime", 0.20, "success: the page opens"),
    # 7 · real examples (s7-examples.html): phones slide in i*2.1; grid 8.9; phones drop 14.5
    ("s7", 0.00, "whoosh-short", 0.14, "Chiken Hut page slides in"),
    ("s7", 2.10, "whoosh-short", 0.14, "Devmmnd page slides in"),
    ("s7", 4.20, "whoosh-short", 0.14, "Courseing page slides in"),
    ("s7", 6.30, "whoosh-short", 0.14, "students' group page slides in"),
    ("s7", 8.90, "whoosh", 0.14, "pages settle into the grid"),
    ("s7", 14.50, "whoosh-short", 0.16, "grid drops away (scene change)"),
    # 8 · where to use it (s8-where.html): drops 1.1 / 2.9 / 4.7 / 6.6, each tile bumps at +0.45; exit 9.35
    ("s8", 1.55, "pop", 0.22, "link lands: Instagram bio tile"),
    ("s8", 3.35, "pop", 0.22, "link lands: WhatsApp status tile"),
    ("s8", 5.15, "pop", 0.22, "link lands: Google Maps tile"),
    ("s8", 7.05, "pop", 0.22, "QR stand lands: cash-register tile"),
    ("s8", 9.35, "whoosh", 0.16, "to the call to action (scene change)"),
    # 9 · call to action (s9-cta.html): logo 0.15
    ("s9", 0.15, "impact-bass-1", 0.22, "soft ending hit on the logo"),
]


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()


def tone_ring():
    """Classic phone ringback: 440 + 480 Hz, 1.0 s, soft edges."""
    t = np.arange(int(SR * 1.0)) / SR
    s = 0.5 * (np.sin(2 * np.pi * 440 * t) + np.sin(2 * np.pi * 480 * t))
    env = np.minimum(1, np.minimum(t / 0.03, (1.0 - t) / 0.08))
    return np.repeat((s * env * 0.6)[:, None], 2, axis=1).astype(np.float32)


def tone_focus():
    """Camera autofocus confirmation: two short 1.9 kHz beeps."""
    t = np.arange(int(SR * 0.07)) / SR
    b = np.sin(2 * np.pi * 1900 * t) * np.minimum(1, np.minimum(t / 0.005, (0.07 - t) / 0.02))
    gap = np.zeros(int(SR * 0.06))
    s = np.concatenate([b, gap, b]) * 0.7
    return np.repeat(s[:, None], 2, axis=1).astype(np.float32)


def main(out, cues_md=None):
    html = (ROOT / "index.html").read_text()
    starts = {m.group(1): float(m.group(2)) for m in re.finditer(r'<div\s+id="(s\d)"[^>]*?data-start="([\d.]+)"', html, re.S)}
    total = float(re.search(r'id="root"[^>]*?data-duration="([\d.]+)"', html, re.S).group(1))
    n = int(round(total * SR))
    mix = np.zeros((n, 2), np.float32)

    music = decode(ROOT / "assets/music.mp3")[int(MUSIC_OFFSET * SR):][:n]
    env = np.ones(len(music), np.float32)
    fi, fo = int(FADE_IN * SR), int(FADE_OUT * SR)
    env[:fi] = np.linspace(0, 1, fi) ** 2
    env[-fo:] = np.linspace(1, 0, fo) ** 1.5
    mix[: len(music)] += music * env[:, None] * MUSIC_GAIN

    sounds = {"ring": tone_ring(), "focus": tone_focus()}
    rows = []
    for scene, local, name, gain, what in sorted(CUES, key=lambda c: starts[c[0]] + c[1]):
        if name not in sounds:
            sounds[name] = decode(ROOT / f"assets/sfx/{name}.mp3")
        s = sounds[name]
        t = starts[scene] + local
        i = int(round(t * SR))
        seg = s[: max(0, n - i)]
        # a sound never runs past its scene's end (e.g. the 2nd ring is cut as the call screen closes)
        if name == "ring" and scene == "s4" and local > 9:
            seg = seg[: int(0.42 * SR)].copy()
            seg[-int(0.08 * SR):] *= np.linspace(1, 0, int(0.08 * SR))[:, None]
        mix[i:i + len(seg)] += seg * gain
        rows.append((t, name, gain, what))

    peak = float(np.abs(mix).max())
    if peak > 0.89:                      # gentle safety: keep true peak under about -1 dBFS
        mix *= 0.89 / peak
    pcm = (np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", str(out)], input=pcm, check=True)
    print(f"{out}: {total}s, {len(rows)} cues, peak before safety {20 * np.log10(peak):.1f} dBFS")
    if cues_md:
        lines = ["| Time | Sound | Level | On screen |", "|---|---|---|---|"]
        for t, name, gain, what in rows:
            lines.append(f"| {int(t // 60)}:{t % 60:05.2f} | {name} | {gain:.2f} | {what} |")
        Path(cues_md).write_text("\n".join(lines) + "\n")


main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
