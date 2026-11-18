"""Çizilecek harita için yerleşim görseli (3840x2160). Kullanım: harita_rehber.py bolum.json cikti.png
JSON: paths, spots, mines, castle, river:[x,w], bridge:[x0,y0,x1,y1], hill:[x,y,r]  (oyun koordinatları 2304x1296)"""
import sys, json, numpy as np
from PIL import Image, ImageDraw
c = json.load(open(sys.argv[1])); k = 3840 / 2304
def spline(P, step=4):
    P = [np.array(p, float) for p in P]; out = []
    for i in range(len(P) - 1):
        p0, p1, p2, p3 = P[max(0, i - 1)], P[i], P[i + 1], P[min(len(P) - 1, i + 2)]
        for t in np.linspace(0, 1, max(4, int(np.linalg.norm(p2 - p1) // step)), endpoint=False):
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-1]); return np.array(out)
im = Image.new('RGB', (3840, 2160), (78, 104, 58)); d = ImageDraw.Draw(im)
if 'hill' in c:
    x, y, r = c['hill']; d.ellipse([(x - r) * k, (y - r * 0.7) * k, (x + r) * k, (y + r * 0.7) * k], fill=(104, 122, 76), outline=(130, 140, 100), width=10)
if 'river' in c:
    x, w = c['river']; d.rectangle([x * k, 0, (x + w) * k, 2160], fill=(52, 92, 128))
for P in c['paths']:
    for x, y in spline(P): d.ellipse([(x - 59) * k, (y - 59) * k, (x + 59) * k, (y + 59) * k], fill=(176, 140, 96))
if 'bridge' in c:
    x0, y0, x1, y1 = c['bridge']; d.rectangle([x0 * k, y0 * k, x1 * k, y1 * k], fill=(140, 138, 130), outline=(90, 90, 90), width=10)
for x, y in c['spots']:
    x, y = x * k, (y + 22) * k; d.ellipse([x - 145, y - 82, x + 145, y + 82], fill=(150, 150, 145), outline=(70, 70, 70), width=8)
for x, y in c.get('mines', []):
    x, y = x * k, (y + 22) * k; d.ellipse([x - 145, y - 82, x + 145, y + 82], fill=(196, 160, 70), outline=(110, 80, 20), width=8)
cx, cy = c['castle'][0] * k, c['castle'][1] * k; d.rectangle([cx - 140, cy - 300, 3840, cy + 60], fill=(96, 92, 100))
im.save(sys.argv[2])
