"""Sterrenborg logo generator.

Tekent de vijf hoofdsterren van Cassiopeia op hun echte hemelposities (J2000),
met de stergrootte afgeleid van de schijnbare helderheid, en zet het woordmerk
'Sterrenborg' als omlijnde paden (Spectral 500), zodat de SVG's zonder font werken.

Gebruik:  python3 tools/make-logo.py   (vanuit de sitemap; schrijft naar ./logo/)
Vereist:  fonttools, brotli, cairosvg; font-bestand in fonts/spectral/files/
"""
import math, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "logo")
os.makedirs(OUT, exist_ok=True)
FONT = os.path.join(ROOT, "fonts/spectral/files/spectral-latin-500-normal.woff")

# naam, RA (graden), declinatie (graden), magnitude
STARS = [
    ("Segin",   28.599, 63.670, 3.37),
    ("Ruchbah", 21.454, 60.235, 2.68),
    ("Navi",    14.177, 60.717, 2.15),
    ("Schedar", 10.127, 56.537, 2.24),
    ("Caph",     2.295, 59.150, 2.27),
]

COLORS = {
    "licht":  {"ink": "#141B2E", "star": "#B8862A", "line": "#141B2E"},
    "donker": {"ink": "#EEF0F5", "star": "#E9B949", "line": "#EEF0F5"},
}


def star_points(scale=10.0):
    """Gnomonische benadering rond dec 60: x = -RA*cos(dec0). Hemelbeeld (oost links)."""
    c = math.cos(math.radians(60))
    pts = []
    for name, ra, dec, mag in STARS:
        pts.append((name, -ra * c, -dec, mag))
    # Cassiopeia draait om de Poolster; kantel naar de klassieke W-stand:
    # Segin en Caph op gelijke hoogte.
    (_, x0, y0, _), (_, x1, y1, _) = pts[0], pts[-1]
    a = -math.atan2(y1 - y0, x1 - x0)
    ca, sa = math.cos(a), math.sin(a)
    pts = [(n, x * ca - y * sa, x * sa + y * ca, m) for n, x, y, m in pts]
    minx = min(p[1] for p in pts); miny = min(p[2] for p in pts)
    return [(n, (x - minx) * scale, (y - miny) * scale, m) for n, x, y, m in pts]


def star_path(cx, cy, r, inner=0.45, rot=-90):
    d = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * inner
        a = math.radians(rot + i * 36)
        d.append(f"{cx + rr * math.cos(a):.2f},{cy + rr * math.sin(a):.2f}")
    return "M" + " L".join(d) + " Z"


def constellation(col, ox=0, oy=0, scale=10.0, rmax=9.5, lines=True, lw=1.1):
    pts = star_points(scale)
    parts = []
    if lines:
        pl = " ".join(f"{x + ox:.2f},{y + oy:.2f}" for _, x, y, _ in pts)
        parts.append(f'<polyline points="{pl}" fill="none" stroke="{col["line"]}" '
                     f'stroke-width="{lw}" stroke-opacity=".45" stroke-linejoin="round"/>')
    for n, x, y, m in pts:
        r = rmax * 10 ** (-0.16 * (m - 2.15))
        parts.append(f'<path d="{star_path(x + ox, y + oy, r)}" fill="{col["star"]}"><title>{n}</title></path>')
    w = max(p[1] for p in pts); h = max(p[2] for p in pts)
    return "\n".join(parts), w, h


def wordmark(text, size, col, x0, baseline, tracking=0.01):
    f = TTFont(FONT)
    upm = f["head"].unitsPerEm
    gs = f.getGlyphSet(); cmap = f.getBestCmap(); hmtx = f["hmtx"]
    s = size / upm
    x = x0; out = []
    for ch in text:
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        tp = TransformPen(pen, (s, 0, 0, -s, x, baseline))
        gs[g].draw(tp)
        out.append(pen.getCommands())
        x += hmtx[g][0] * s + tracking * size
    return f'<path d="{" ".join(out)}" fill="{col["ink"]}"/>', x - tracking * size - x0


def shield(col, w, h):
    # heraldisch schild: rechte bovenrand, zijkanten, punt onder
    return (f'<path d="M0,0 H{w} V{h*0.52} C{w},{h*0.8} {w*0.72},{h*0.93} {w/2},{h} '
            f'C{w*0.28},{h*0.93} 0,{h*0.8} 0,{h*0.52} Z" fill="none" stroke="{col["ink"]}" stroke-width="3"/>')


def rampart(col, w, y, lw=3):
    # borgmuur met kantelen als horizonlijn
    step = w / 9; hgt = step * 0.55
    d = f"M0,{y + hgt}"
    for i in range(9):
        x = i * step
        if i % 2 == 0:
            d += f" H{x + step} "
        else:
            d += f" V{y} H{x + step} V{y + hgt}"
    return f'<path d="{d}" fill="none" stroke="{col["ink"]}" stroke-width="{lw}" stroke-linejoin="miter"/>'


def svg(w, h, body, bg=None):
    rect = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" '
            f'width="{w:.0f}" height="{h:.0f}">{rect}{body}</svg>')


def mark(variant, col):
    """Geeft (body, w, h) van het beeldmerk."""
    if variant == "sterrenbeeld":
        body, w, h = constellation(col, 12, 12)
        return body, w + 24, h + 24
    if variant == "wapen":
        W, H = 170, 190
        c, cw, ch = constellation(col, 0, 0, scale=9.0, rmax=9)
        ox = (W - cw) / 2; oy = 52
        c, _, _ = constellation(col, ox, oy, scale=9.0, rmax=9)
        return f'<g transform="translate(4,4)">{shield(col, W, H)}{c}</g>', W + 8, H + 8
    if variant == "borg":
        c, cw, ch = constellation(col, 12, 10)
        W = cw + 24
        return c + rampart(col, W - 8, ch + 34, 3).replace("M0,", "M4,", 1), W, ch + 34 + 24
    raise ValueError(variant)


def lockup(variant, col, bg=None):
    mb, mw, mh = mark(variant, col)
    size = 64
    gap = 26
    wm, ww = wordmark("Sterrenborg", size, col, 0, 0)
    H = max(mh, 90)
    my = (H - mh) / 2
    base = H / 2 + size * 0.34
    body = (f'<g transform="translate(0,{my:.1f})">{mb}</g>'
            f'<g transform="translate({mw + gap:.1f},{base:.1f})">{wm}</g>')
    return svg(mw + gap + ww + 6, H, body, bg)


if __name__ == "__main__":
    import cairosvg
    files = []
    for v in ("sterrenbeeld", "wapen", "borg"):
        for theme, col in COLORS.items():
            s = lockup(v, col)
            p = os.path.join(OUT, f"sterrenborg-{v}-{theme}.svg")
            open(p, "w").write(s); files.append(p)
            mb, mw, mh = mark(v, col)
            p2 = os.path.join(OUT, f"beeldmerk-{v}-{theme}.svg")
            open(p2, "w").write(svg(mw, mh, mb)); files.append(p2)
    # favicon: sterrenbeeld zonder lijnen, groot
    col = COLORS["licht"]
    c, w, h = constellation({"line": "#fff", "star": "#E9B949"}, 0, 0, scale=3.3, rmax=6, lines=False)
    S = w + 30
    fav = svg(S, S, f'<rect width="100%" height="100%" rx="{S*0.2:.1f}" fill="#141B2E"/>'
                    f'<g transform="translate(15,{(S - h) / 2:.1f})">{c}</g>')
    open(os.path.join(OUT, "favicon.svg"), "w").write(fav)
    for p in files + [os.path.join(OUT, "favicon.svg")]:
        cairosvg.svg2png(url=p, write_to=p[:-4] + ".png", output_width=None, scale=3 if "favicon" not in p else 8)
    print("\n".join(sorted(os.listdir(OUT))))
