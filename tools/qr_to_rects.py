"""Turn the real linktrees.link QR SVG (2-unit modules on a 74 viewBox) into an
inline SVG with one <rect> per dark module, so the QR can draw itself in.
Finder patterns (the three corner squares) get class "qf", the rest "qm".
Usage: python3 tools/qr_to_rects.py assets/qr/chikenhut.svg > assets/qr/chikenhut-modules.svg"""
import re, sys
src = open(sys.argv[1]).read()
cells = sorted({(int(x), int(y)) for x, y in re.findall(r"M(\d+),(\d+)l2,0", src)})
xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
x0, y0 = min(xs), min(ys)
n = (max(xs) - x0) // 2 + 1
def finder(cx, cy):
    return (cx < 7 and cy < 7) or (cx >= n - 7 and cy < 7) or (cx < 7 and cy >= n - 7)
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-4 -4 {n+8} {n+8}" shape-rendering="crispEdges">',
       f'<rect class="qbg" x="-4" y="-4" width="{n+8}" height="{n+8}" fill="#fff"/>']
mods = []
for x, y in cells:
    cx, cy = (x - x0) // 2, (y - y0) // 2
    mods.append((cx, cy, "qf" if finder(cx, cy) else "qm"))
# draw order: finders first, then by distance from centre outward
c = (n - 1) / 2
mods.sort(key=lambda m: (m[2] != "qf", (m[0]-c)**2 + (m[1]-c)**2))
for cx, cy, k in mods:
    out.append(f'<rect class="{k}" x="{cx}" y="{cy}" width="1.02" height="1.02"/>')
out.append("</svg>")
print("\n".join(out))
sys.stderr.write(f"{n}x{n} modules, {len(mods)} dark\n")
