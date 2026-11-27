"""Swap the Chiken Hut brand content for the fictional café «سكّر وهيل» everywhere except scene 7.

Only brand content changes: names, tagline, phone, address, handle, slug, logo/cover images, QR,
menu items and brand colours. Layout, sizes, positions, timing and animation are untouched
(the one exception: the typed slug in scene 3 has 10 letters instead of 9, so it types one more key).
Scene 7 and the shared .t-chikenhut theme it uses are not modified.
Run once on the v1 sources (49e9bf8 state): python3 tools/rebrand_cafe.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME, TAG, PHONE, CITY, HANDLE, SLUG = "سكّر وهيل", "قهوة وحلويات", "0900 000 000", "حلب", "sukkar.w.hel", "sukkar-hel"
LOGO, COVER, QR = "assets/brand-cafe/logo.svg", "assets/brand-cafe/cover.svg", "assets/qr/sukkar-hel.svg"
# brand red palette → café palette (coffee brown, cream, cardamom)
COLORS = {"#dc2626": "#6B4A3A", "#991b1b": "#4A3228", "#b91c1c": "#4A3228", "#450a0a": "#3B2A22", "#7f1d1d": "#4A3228",
          "#1c0606": "#1E1410", "#fecaca": "#E3D5C5", "#fee2e2": "#E4EBDF", "#fdf2f2": "#F6EFE6"}


def edit(path, pairs, recolor_selectors=()):
    p = ROOT / path
    s = p.read_text()
    for a, b in pairs:
        n = s.count(a)
        assert n == 1, f"{path}: expected 1 match, found {n}: {a[:70]}"
        s = s.replace(a, b)
    # recolour only the named brand CSS rules (whole lines starting with the selector)
    lines = s.split("\n")
    for i, line in enumerate(lines):
        if any(line.lstrip().startswith(sel) for sel in recolor_selectors):
            for old, new in COLORS.items():
                line = line.replace(old, new)
            lines[i] = line
    p.write_text("\n".join(lines))


# shared stylesheet: a new café theme (the Chiken Hut theme stays for scene 7)
edit("assets/css/common.css", [(
    ".lp.t-chikenhut { --cream: #fdf2f2; --sand: #fee2e2; --line: #fecaca; --ink: #450a0a; --muted2: #991b1b; --brand: #dc2626; --brand-dark: #b91c1c; }",
    ".lp.t-chikenhut { --cream: #fdf2f2; --sand: #fee2e2; --line: #fecaca; --ink: #450a0a; --muted2: #991b1b; --brand: #dc2626; --brand-dark: #b91c1c; }\n"
    "/* fictional café brand «سكّر وهيل»: cream, coffee brown, cardamom green */\n"
    ".lp.t-cafe { --cream: #F6EFE6; --sand: #E4EBDF; --line: #E3D5C5; --ink: #3B2A22; --muted2: #6B4A3A; --brand: #6B4A3A; --brand-dark: #4A3228; }")])

# scene 3: the typed slug (10 letters)
s3 = ROOT / "compositions/s3-link.html"
t = s3.read_text()
old = "".join(f'<span id="s3-a{i}" class="ch">{c}</span>' for i, c in enumerate("chikenhut"))
new = "".join(f'<span id="s3-a{i}" class="ch">{c}</span>' for i, c in enumerate(SLUG))
assert t.count(old) == 1
t = t.replace(old, new).replace('type("a", 9, 1.05, 0.1);', 'type("a", 10, 1.05, 0.1);').replace('erase("a", 9, 4.6, 0.05);', 'erase("a", 10, 4.6, 0.05);')
t = t.replace("// cycle: chikenhut → yourshop → yourname", f"// cycle: {SLUG} → yourshop → yourname")
s3.write_text(t)

page_pairs = lambda pre="": [
    (f'class="cover fade" style="background-image:url(\'assets/clients/chikenhut-cover.png\')"', f'class="cover fade" style="background-image:url(\'{COVER}\')"'),
]

edit("compositions/s4-page.html", [
    ('url("assets/clients/chikenhut-logo.jpg") center / cover; }\n    #s4-chat .hd .n', f'url("{LOGO}") center / cover; }}\n    #s4-chat .hd .n'),
    ('#s4-call .av { background: url("assets/clients/chikenhut-logo.jpg") center / cover; }', f'#s4-call .av {{ background: url("{LOGO}") center / cover; }}'),
    ('border: 4px solid #fee2e2; background: url("assets/clients/chikenhut-logo.jpg") center / cover; }', f'border: 4px solid #fee2e2; background: url("{LOGO}") center / cover; }}'),
    ('<div id="s4-page" class="lp t-chikenhut">', '<div id="s4-page" class="lp t-cafe">'),
    ("<div id=\"s4-cover\" class=\"cover fade\" style=\"background-image:url('assets/clients/chikenhut-cover.png')\"></div>", f"<div id=\"s4-cover\" class=\"cover fade\" style=\"background-image:url('{COVER}')\"></div>"),
    ("<div id=\"s4-avatar\" class=\"avatar\" style=\"background-image:url('assets/clients/chikenhut-logo.jpg')\"></div>", f"<div id=\"s4-avatar\" class=\"avatar\" style=\"background-image:url('{LOGO}')\"></div>"),
    ('<div id="s4-name" class="name ltrname">Chiken Hut</div>', f'<div id="s4-name" class="name">{NAME}</div>'),
    ('<i class="ico i-tag"></i>مطعم وجبات سريعة</span>', f'<i class="ico i-tag"></i>{TAG}</span>'),
    ('<div class="s ltr">0993354919</div>', f'<div class="s ltr">{PHONE}</div>'),
    ('<div class="v">حلب-الجميلية-جانب جامع الصديق</div>', f'<div class="v">{CITY}</div>'),
    ('<div class="n">Chiken Hut</div><div class="m">متصل الآن</div>', f'<div class="n">{NAME}</div><div class="m">متصل الآن</div>'),
    ('<div class="av"></div>\n            <div class="n">Chiken Hut</div>', f'<div class="av"></div>\n            <div class="n">{NAME}</div>'),
    ('<div class="num">0993354919</div>', f'<div class="num">{PHONE}</div>'),
    ('<div class="lg"></div>\n            <div class="n">Chiken Hut</div>', f'<div class="lg"></div>\n            <div class="n">{NAME}</div>'),
    ('<span class="v">0993354919</span>', f'<span class="v">{PHONE}</span>'),
    ('<span>حلب - الجميلية</span>', f'<span>{CITY}</span>'),
    ('<div id="s4-pinlabel">Chiken Hut</div>', f'<div id="s4-pinlabel">{NAME}</div>'),
    ('<div class="a">أسرع طريق لعند Chiken Hut</div>', f'<div class="a">أسرع طريق لعند {NAME}</div>'),
    ('tl.fromTo("#s4-wa .ico", { color: "#450a0a" }', 'tl.fromTo("#s4-wa .ico", { color: "#3B2A22" }'),
    ('tl.fromTo(b + " .ico", { color: "#450a0a" }', 'tl.fromTo(b + " .ico", { color: "#3B2A22" }'),
    ('{ color: "#450a0a", duration: 0.4 }, 19.0);', '{ color: "#3B2A22", duration: 0.4 }, 19.0);'),
], recolor_selectors=("#s4-call {", "#s4-card {", "box-shadow: 0 40px 80px", "#s4-card .tt", "#s4-card .lg", "#s4-card .n", "#s4-card .f", "#s4-pin {", "#s4-pinlabel"))

edit("compositions/s5-custom.html", [
    ('<div id="s5-page" class="lp t-chikenhut">', '<div id="s5-page" class="lp t-cafe">'),
    ("<div id=\"s5-cv1\" class=\"cover fade\" style=\"background-image:url('assets/clients/chikenhut-cover.png')\"></div>", f"<div id=\"s5-cv1\" class=\"cover fade\" style=\"background-image:url('{COVER}')\"></div>"),
    ("<div id=\"s5-av1\" style=\"background-image:url('assets/clients/chikenhut-logo.jpg')\"></div>", f"<div id=\"s5-av1\" style=\"background-image:url('{LOGO}')\"></div>"),
    ('<span id="s5-n1">Chiken Hut</span>', f'<span id="s5-n1" dir="rtl">{NAME}</span>'),
    ('<i class="ico i-tag"></i>مطعم وجبات سريعة</span>', f'<i class="ico i-tag"></i>{TAG}</span>'),
    ('<div class="s ltr">0993354919</div>', f'<div class="s ltr">{PHONE}</div>'),
    ('<div class="v">حلب-الجميلية-جانب جامع الصديق</div>', f'<div class="v">{CITY}</div>'),
    ('linktrees.link/<span class="slug">chikenhut</span>', f'linktrees.link/<span class="slug">{SLUG}</span>'),
    ('// live re-skin: Chiken Hut → Devmmnd → Courseing → back to Chiken Hut', f'// live re-skin: {NAME} → Devmmnd → Courseing → back to {NAME}'),
    ('ch:  { "--cream": "#fdf2f2", "--sand": "#fee2e2", "--line": "#fecaca", "--ink": "#450a0a", "--muted2": "#991b1b", "--brand": "#dc2626", "--brand-dark": "#b91c1c" },',
     'ch:  { "--cream": "#F6EFE6", "--sand": "#E4EBDF", "--line": "#E3D5C5", "--ink": "#3B2A22", "--muted2": "#6B4A3A", "--brand": "#6B4A3A", "--brand-dark": "#4A3228" },'),
])

# scene 6: QR, logo, tent, sticker, menu, cards, bag, scan
p6 = ROOT / "compositions/s6-qr.html"
t = p6.read_text()
new_svg = (ROOT / "assets/qr/sukkar-hel-modules.svg").read_text().strip().replace('<svg xmlns="http://www.w3.org/2000/svg"', '<svg id="s6-qrsvg" xmlns="http://www.w3.org/2000/svg"', 1)
m = re.search(r'<svg id="s6-qrsvg"[\s\S]*?</svg>', t)
assert m
t = t[:m.start()] + new_svg + t[m.end():]
p6.write_text(t)
menu_old = "".join(f'          <div class="it"><span class="dot"></span>{x}</div>\n' for x in ["بروستد", "برغر دجاج", "كرسبي", "بطاطا", "مشروبات"])
menu_new = "".join(f'          <div class="it"><span class="dot"></span>{x}</div>\n' for x in ["قهوة عربية", "لاتيه", "كرواسون", "معمول", "كنافة"])
edit("compositions/s6-qr.html", [
    ('.s6-qr { background: #fff url("assets/qr/chikenhut.svg") center / 92% no-repeat; }', f'.s6-qr {{ background: #fff url("{QR}") center / 92% no-repeat; }}'),
    ('.s6-logo { background: url("assets/clients/chikenhut-logo.jpg") center / cover; border-radius: 50%; }', f'.s6-logo {{ background: url("{LOGO}") center / cover; border-radius: 50%; }}'),
    ('<div class="band"><div class="s6-logo"></div>Chiken Hut</div>', f'<div class="band"><div class="s6-logo"></div><span dir="rtl">{NAME}</span></div>'),
    ('<div id="s6-found"><i class="ico i-link"></i>linktrees.link/chikenhut</div>', f'<div id="s6-found"><i class="ico i-link"></i>linktrees.link/{SLUG}</div>'),
    ('<div class="lp t-chikenhut">', '<div class="lp t-cafe">'),
    ("<div class=\"cover fade\" style=\"background-image:url('assets/clients/chikenhut-cover.png')\"></div>", f"<div class=\"cover fade\" style=\"background-image:url('{COVER}')\"></div>"),
    ("<div class=\"avatar\" style=\"background-image:url('assets/clients/chikenhut-logo.jpg')\"></div>", f"<div class=\"avatar\" style=\"background-image:url('{LOGO}')\"></div>"),
    ('<div class="name ltrname">Chiken Hut</div>', f'<div class="name">{NAME}</div>'),
    ('<div><span class="tagline"><i class="ico i-tag"></i>مطعم وجبات سريعة</span></div>', f'<div><span class="tagline"><i class="ico i-tag"></i>{TAG}</span></div>'),
    ('<div class="s ltr">0993354919</div>', f'<div class="s ltr">{PHONE}</div>'),
    ('<div class="v">حلب-الجميلية-جانب جامع الصديق</div>', f'<div class="v">{CITY}</div>'),
    ('<div class="t2">Chiken Hut</div>', f'<div class="t2" dir="rtl">{NAME}</div>'),
    (menu_old, menu_new),
    ('وشوف صفحتنا<small>linktrees.link/chikenhut</small>', f'وشوف صفحتنا<small>linktrees.link/{SLUG}</small>'),
    ('<div class="nm">Chiken Hut</div><div class="tg">مطعم وجبات سريعة</div>', f'<div class="nm" dir="rtl">{NAME}</div><div class="tg">{TAG}</div>'),
    ('كل طرق التواصل<small>linktrees.link/chikenhut</small>', f'كل طرق التواصل<small>linktrees.link/{SLUG}</small>'),
    ('linktrees.link/<span class="slug">chikenhut</span>', f'linktrees.link/<span class="slug">{SLUG}</span>'),
    ('#s6-menu .it .dot { width: 18px; height: 18px; border-radius: 50%; background: #dc2626; flex: none; }', '#s6-menu .it .dot { width: 18px; height: 18px; border-radius: 50%; background: #8BA888; flex: none; }'),
], recolor_selectors=("#s6-tent .back", "#s6-tent .band", "#s6-tent .cap", "box-shadow: 0 8px 18px rgba(0,0,0,0.35), inset", "#s6-sticker .t1", "#s6-sticker .t2",
                       "#s6-menu .hd {", "#s6-menu .it {", "#s6-menu .ft {", "#s6-menu .ft .tx", "#s6-bc1 .s6-bc", "#s6-bc2 .tx",
                       "font-family: var(--font); font-weight: 700; font-size: 26px; color: #450a0a", "#s6-cam-tent .band", "#s6-hp-page {"))

edit("compositions/s8-where.html", [
    ('#s8-ig .ring div { width: 100%; height: 100%; border-radius: 50%; border: 5px solid #fff; background: url("assets/clients/chikenhut-logo.jpg") center / cover; }',
     f'#s8-ig .ring div {{ width: 100%; height: 100%; border-radius: 50%; border: 5px solid #fff; background: url("{LOGO}") center / cover; }}'),
    ('border: 3px solid #25d366; background: url("assets/clients/chikenhut-logo.jpg") center / cover; }', f'border: 3px solid #25d366; background: url("{LOGO}") center / cover; }}'),
    ('background: #fff url("assets/qr/chikenhut.svg") center / 100% no-repeat; }', f'background: #fff url("{QR}") center / 100% no-repeat; }}'),
    ('<div class="hn">chickenhut.aleppo</div>', f'<div class="hn">{HANDLE}</div>'),
    ('<div class="bio">مطعم وجبات سريعة · حلب</div>', f'<div class="bio">{TAG} · {CITY}</div>'),
    ('style="top:360px"><i class="ico i-link"></i>linktrees.link/chikenhut</div>', f'style="top:360px"><i class="ico i-link"></i>linktrees.link/{SLUG}</div>'),
    ('<div class="n">Chiken Hut</div><div class="t">قبل شوي</div>', f'<div class="n" dir="rtl">{NAME}</div><div class="t">قبل شوي</div>'),
    ('style="top:390px;background:#25d366"><i class="ico i-link"></i>linktrees.link/chikenhut</div>', f'style="top:390px;background:#25d366"><i class="ico i-link"></i>linktrees.link/{SLUG}</div>'),
    ('<div class="nm">Chiken Hut</div>', f'<div class="nm" dir="rtl">{NAME}</div>'),
    ('<div class="ty">مطعم وجبات سريعة</div>', f'<div class="ty">{TAG}</div>'),
    ('<div class="row"><i class="ico i-location-dot"></i>حلب - الجميلية</div>', f'<div class="row"><i class="ico i-location-dot"></i>{CITY}</div>'),
    ('style="top:430px;background:#1a73e8"><i class="ico i-link"></i>linktrees.link/chikenhut</div>', f'style="top:430px;background:#1a73e8"><i class="ico i-link"></i>linktrees.link/{SLUG}</div>'),
], recolor_selectors=("#s8-cr .stand .b", "#s8-cr .stand .t"))
print("rebranded")
