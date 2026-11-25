"""Apply a scene's ANCHORS (see assets/js/retime.js) to its timed HTML elements.

Reads `const ANCHORS = [[old, new], ...];` from the scene script and rewrites
data-start / data-duration of every element that has them. The authored values are
kept once in data-base-start / data-base-duration, so the tool can be re-run after
the anchors change. A scene without ANCHORS is left alone.
Usage: python3 tools/retime_clips.py compositions/s1-problem.html [...]
"""
import json, re, sys


def mapper(a):
    def f(t):
        if t <= a[0][0]:
            return a[0][1] + (t - a[0][0])
        for i in range(1, len(a)):
            if t <= a[i][0]:
                k = (t - a[i - 1][0]) / (a[i][0] - a[i - 1][0])
                return a[i - 1][1] + k * (a[i][1] - a[i - 1][1])
        return a[-1][1] + (t - a[-1][0])
    return f


def fix_tag(tag, f):
    m_s = re.search(r'\sdata-start="([\d.]+)"', tag)
    m_d = re.search(r'\sdata-duration="([\d.]+)"', tag)
    if not (m_s and m_d):
        return tag
    bs = re.search(r'\sdata-base-start="([\d.]+)"', tag)
    bd = re.search(r'\sdata-base-duration="([\d.]+)"', tag)
    s0 = float(bs.group(1)) if bs else float(m_s.group(1))
    d0 = float(bd.group(1)) if bd else float(m_d.group(1))
    ns, ne = f(s0), f(s0 + d0)
    tag = tag.replace(m_s.group(0), f' data-start="{ns:.2f}"').replace(m_d.group(0), f' data-duration="{ne - ns:.2f}"')
    if not bs:
        tag = tag.replace(f' data-start="{ns:.2f}"', f' data-start="{ns:.2f}" data-base-start="{s0:g}" data-base-duration="{d0:g}"', 1)
    return tag


for path in sys.argv[1:]:
    src = open(path).read()
    m = re.search(r"const ANCHORS = (\[\[.*?\]\]);", src, re.S)
    if not m:
        print(path, "no ANCHORS, skipped")
        continue
    f = mapper(json.loads(m.group(1)))
    body_start = src.index("<template>")
    head, rest = src[:body_start], src[body_start:]
    script_at = rest.index("<script")
    markup, script = rest[:script_at], rest[script_at:]
    markup = re.sub(r"<(?:div|h1|span|p|section)\b[^>]*\sclass=\"[^\"]*\bclip\b[^\"]*\"[^>]*>", lambda mm: fix_tag(mm.group(0), f), markup)
    open(path, "w").write(head + markup + script)
    print(path, "retimed")
