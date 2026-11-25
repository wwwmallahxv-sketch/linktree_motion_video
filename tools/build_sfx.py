"""Place sound effects on the on-screen actions.

Sounds come from the HyperFrames media-use bundled library (Pixabay Content License: commercial
use, no attribution) and are copied into assets/sfx/. Each cue is written against its scene's
local time, so a re-timed scene keeps its sounds in sync; the scene start is read from index.html.
The <audio> tracks are written between the SFX markers in index.html, on lanes 5+ (a new lane only
where two sounds overlap).
Usage: python3 tools/build_sfx.py
"""
import re, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / ".claude/skills/media-use/audio/assets/sfx"

# (scene, local second, sound, volume, what it marks)
CUES = [
    # 1 · the problem
    ("s1", 3.60, "notification", 0.30, "first customer question arrives"),
    ("s1", 4.40, "pop", 0.35, "question bubble"),
    ("s1", 5.20, "pop", 0.35, "question bubble"),
    ("s1", 5.90, "pop", 0.35, "question bubble"),
    ("s1", 7.00, "click-soft", 0.35, "owner sends a link"),
    ("s1", 7.23, "click-soft", 0.35, "owner sends a link"),
    ("s1", 7.46, "click-soft", 0.35, "owner sends a link"),
    ("s1", 7.68, "click-soft", 0.35, "owner sends a link"),
    ("s1", 7.91, "click-soft", 0.35, "owner sends a link"),
    ("s1", 8.25, "whoosh-short", 0.35, "links fly out of the phone"),
    ("s1", 9.45, "whoosh", 0.30, "phone drops away"),
    # 2 · the answer
    ("s2", 0.20, "whoosh-short", 0.35, "links pulled together"),
    ("s2", 1.15, "ping", 0.35, "links snap into one"),
    ("s2", 1.70, "impact-bass-1", 0.45, "logo lands"),
    ("s2", 2.60, "sparkle", 0.28, "Linktrees.link wordmark"),
    ("s2", 5.50, "whoosh-short", 0.30, "hand-off to the address bar"),
    # 3 · your link
    ("s3", 1.00, "typing", 0.30, "chikenhut typed"),
    ("s3", 2.40, "pop", 0.35, "«اسم محلك» tag"),
    ("s3", 4.20, "typing", 0.25, "yourshop typed"),
    ("s3", 5.90, "typing", 0.25, "yourname typed"),
    ("s3", 7.65, "pop", 0.35, "app icons appear"),
    ("s3", 8.69, "click-soft", 0.40, "link lands in WhatsApp"),
    ("s3", 8.98, "click-soft", 0.40, "link lands in Instagram"),
    ("s3", 9.27, "click-soft", 0.40, "link lands in Facebook"),
    ("s3", 9.30, "chime", 0.25, "all sent"),
    ("s3", 10.10, "whoosh", 0.30, "whip up to the phone"),
    # 4 · what's on the page
    ("s4", 0.05, "whoosh-short", 0.30, "phone rises"),
    ("s4", 4.07, "click", 0.40, "WhatsApp tapped"),
    ("s4", 4.84, "pop", 0.30, "customer message"),
    ("s4", 5.40, "notification", 0.30, "restaurant replies"),
    ("s4", 7.27, "click", 0.40, "call button pressed"),
    ("s4", 7.80, "ping", 0.22, "dialing"),
    ("s4", 8.60, "ping", 0.18, "dialing"),
    ("s4", 10.43, "click", 0.40, "save button pressed"),
    ("s4", 10.67, "whoosh-short", 0.30, "contact card drops in"),
    ("s4", 11.58, "chime", 0.28, "«انحفظ الرقم»"),
    ("s4", 13.56, "click", 0.40, "«فتح في الخرائط» pressed"),
    ("s4", 14.19, "pop", 0.35, "map pin drops"),
    ("s4", 14.51, "whoosh-short", 0.20, "route draws"),
    ("s4", 16.85, "pop", 0.32, "Instagram icon"),
    ("s4", 17.06, "pop", 0.32, "Facebook icon"),
    ("s4", 17.27, "pop", 0.32, "WhatsApp icon"),
    # 5 · made for you
    ("s5", 1.10, "whoosh-short", 0.22, "re-skin: Devmmnd look"),
    ("s5", 2.20, "whoosh-short", 0.22, "re-skin: Courseing look"),
    ("s5", 3.35, "whoosh-short", 0.22, "re-skin: back to Chiken Hut"),
    ("s5", 4.10, "whoosh", 0.28, "three looks side by side"),
    ("s5", 6.70, "glitch-3", 0.22, "«نت ضعيف»"),
    ("s5", 7.60, "ping", 0.32, "«فتحت فوراً»"),
    ("s5", 10.20, "pop", 0.32, "edit pen"),
    ("s5", 10.75, "pop", 0.35, "new account added"),
    ("s5", 11.30, "chime", 0.28, "«تم التعديل»"),
    ("s5", 13.20, "click-soft", 0.35, "the same link"),
    ("s5", 14.30, "sparkle", 0.25, "link glows: unchanged"),
    ("s5", 15.20, "whoosh", 0.30, "into the QR section"),
    # 6 · the QR code
    ("s6", 0.00, "pop", 0.35, "QR card appears"),
    ("s6", 0.80, "sparkle", 0.30, "QR draws itself"),
    ("s6", 3.07, "ping", 0.30, "scan line"),
    ("s6", 4.20, "whoosh", 0.30, "QR flies onto the table tent"),
    ("s6", 7.30, "whoosh-short", 0.30, "whip to the menu"),
    ("s6", 10.20, "whoosh-short", 0.30, "whip to the glass door"),
    ("s6", 13.10, "whoosh-short", 0.30, "whip to the business cards"),
    ("s6", 16.00, "whoosh-short", 0.30, "whip to the bag"),
    ("s6", 18.80, "pop", 0.32, "QR returns"),
    ("s6", 19.60, "whoosh-cinematic", 0.30, "zoom: any size"),
    ("s6", 21.70, "whoosh-short", 0.30, "hand raises the phone"),
    ("s6", 23.00, "ping", 0.38, "camera locks on the QR"),
    ("s6", 23.30, "pop", 0.30, "link found"),
    ("s6", 23.60, "chime", 0.30, "the page opens"),
    # 7 · real examples
    ("s7", 0.00, "whoosh-short", 0.28, "first pair rises"),
    ("s7", 0.50, "pop", 0.32, "chikenhut link"),
    ("s7", 1.10, "pop", 0.32, "devmmnd link"),
    ("s7", 3.40, "whoosh", 0.26, "second pair"),
    ("s7", 4.20, "pop", 0.32, "courseing link"),
    ("s7", 4.80, "pop", 0.32, "students' group link"),
    ("s7", 7.00, "whoosh", 0.26, "grid forms"),
    ("s7", 8.10, "ping", 0.30, "«رابط واحد لكل شي»"),
    # 8 · where to use it
    ("s8", 0.10, "whoosh-short", 0.26, "tiles appear"),
    ("s8", 1.30, "pop", 0.38, "link drops into the Instagram bio"),
    ("s8", 3.65, "pop", 0.38, "link drops into WhatsApp status"),
    ("s8", 6.00, "pop", 0.38, "link drops into Google Maps"),
    ("s8", 7.85, "pop", 0.38, "QR stand by the register"),
    ("s8", 10.40, "whoosh", 0.30, "to the call to action"),
    # 9 · call to action
    ("s9", 0.10, "impact-bass-1", 0.45, "logo lands"),
    ("s9", 0.60, "sparkle", 0.25, "wordmark"),
    ("s9", 3.20, "pop", 0.32, "QR card"),
    ("s9", 4.20, "notification", 0.32, "WhatsApp button"),
]


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip())


def main():
    out = ROOT / "assets/sfx"
    out.mkdir(parents=True, exist_ok=True)
    names = sorted({c[2] for c in CUES})
    lengths = {}
    for n in names:
        shutil.copyfile(LIB / f"{n}.mp3", out / f"{n}.mp3")
        lengths[n] = duration(out / f"{n}.mp3")
    shutil.copyfile(LIB / "CREDITS.md", out / "CREDITS.md")

    p = ROOT / "index.html"
    html = p.read_text()
    starts = {m.group(1): float(m.group(2)) for m in re.finditer(r'<div id="(s\d)" [^>]*?data-start="([\d.]+)"', html, re.S)}
    total = float(re.search(r'id="root"[^>]*?data-duration="([\d.]+)"', html, re.S).group(1))

    lanes_end = []  # end time of the last clip on each sfx lane
    tags = []
    for i, (scene, local, name, vol, what) in enumerate(sorted(CUES, key=lambda c: starts[c[0]] + c[1])):
        t = round(starts[scene] + local, 3)
        d = round(min(lengths[name], total - t), 3)
        lane = next((k for k, e in enumerate(lanes_end) if e <= t), None)
        if lane is None:
            lanes_end.append(0)
            lane = len(lanes_end) - 1
        lanes_end[lane] = t + d
        tags.append(f'      <audio id="sfx-{i + 1:02d}" src="assets/sfx/{name}.mp3" data-start="{t}" data-duration="{d}" '
                    f'data-track-index="{5 + lane}" data-volume="{vol}" data-audio-group="sfx"></audio> <!-- {what} -->')
    block = "      <!-- SFX:BEGIN (generated by tools/build_sfx.py) -->\n" + "\n".join(tags) + "\n      <!-- SFX:END -->\n"
    if "<!-- SFX:BEGIN" in html:
        html = re.sub(r"      <!-- SFX:BEGIN[\s\S]*?<!-- SFX:END -->\n", block, html)
    else:
        html = html.replace('      <audio id="music"', block + '      <audio id="music"', 1)
    p.write_text(html)
    print(f"{len(tags)} cues on {len(lanes_end)} lanes, {len(names)} sounds: {', '.join(names)}")


main()
