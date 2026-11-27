"""Make a QR in the same SVG format as the linktrees.link client QR files.

Same layout as assets/qr/chikenhut.svg: 2-unit modules, 8-unit quiet zone, viewBox 0 0 74 74
(version 3, 29×29 modules), so it drops into every mockup and into tools/qr_to_rects.py unchanged.
Usage: python3 tools/make_qr.py URL ERROR_LEVEL OUT.svg     (e.g. https://linktrees.link M assets/qr/sukkar-hel.svg)
"""
import sys
import segno

url, level, out = sys.argv[1:4]
qr = segno.make(url, version=3, error=level.lower(), boost_error=False)
assert qr.version == 3 and qr.error.upper() == level.upper(), (qr.version, qr.error)
rows = list(qr.matrix_iter(scale=1, border=0))
assert len(rows) == 29
parts = [f"M{8 + 2 * c},{8 + 2 * r}l2,0 0,2 -2,0 0,-2z" for r, row in enumerate(rows) for c, v in enumerate(row) if v]
svg = ('<svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 74 74"  preserveAspectRatio="xMinYMin meet">'
       '<rect width="100%" height="100%" fill="white" cx="0" cy="0"/>'
       f'<path d="{" ".join(parts)}" fill="black"/></svg>')
open(out, "w").write(svg)
print(f"{out}: version {qr.version}, error {qr.error.upper()}, mask {qr.mask}, {len(parts)} dark modules")
