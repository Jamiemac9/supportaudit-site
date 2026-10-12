#!/usr/bin/env python3
"""Generate SEA Audit logo SVGs (text converted to outlines) from the self-hosted font."""
import os, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, 'src/assets/fonts')
OUT = os.path.join(ROOT, 'src/assets/img')
os.makedirs(OUT, exist_ok=True)

def text_path(text, weight, size, x0, baseline, tracking=-0.035):
    f = TTFont(os.path.join(FONTS, f'schibsted-grotesk-latin-{weight}-normal.woff2'))
    gs = f.getGlyphSet(); cmap = f.getBestCmap(); upm = f['head'].unitsPerEm
    s = size / upm; x = x0; d = []
    for ch in text:
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        tp = TransformPen(pen, (s, 0, 0, -s, x, baseline))
        gs[g].draw(tp)
        d.append(pen.getCommands())
        x += gs[g].width * s + tracking * size
    return ' '.join(d), x

def tiles(x, y, size, gap, r):
    t = (size - gap) / 2
    cols = ['#E8B84A', '#43B581', '#F0954A', '#E35D5D']
    pos = [(0, 0), (t + gap, 0), (0, t + gap), (t + gap, t + gap)]
    return ''.join(f'<rect x="{x+px:.2f}" y="{y+py:.2f}" width="{t:.2f}" height="{t:.2f}" rx="{r}" fill="{c}"/>' for (px, py), c in zip(pos, cols))

def logo(fg, fg2, name):
    H = 64; m = 44
    sea, x = text_path('SEA', 800, 46, 56, 48)
    aud, x2 = text_path('Audit', 500, 46, x + 11, 48)
    w = x2 + 4
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {H}" width="{w:.0f}" height="{H}" role="img" aria-label="SEA Audit">'
           f'<title>SEA Audit</title>{tiles(2, 12, 40, 4, 4)}'
           f'<path d="{sea}" fill="{fg}"/><path d="{aud}" fill="{fg2}"/></svg>')
    open(os.path.join(OUT, name), 'w').write(svg)
    return w

logo('#EEF3F7', '#AEBBC8', 'logo.svg')
logo('#06101C', '#465567', 'logo-on-light.svg')
mark = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#050E19"/>'
        + tiles(13, 13, 38, 4, 3.5) + '</svg>')
open(os.path.join(OUT, 'favicon.svg'), 'w').write(mark)
open(os.path.join(OUT, 'mark.svg'), 'w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">' + tiles(0, 0, 40, 4, 4) + '</svg>')
print('logos written')
