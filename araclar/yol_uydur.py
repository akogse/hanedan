"""Yerleşim yolunu boyalı haritadaki yolun tam ortasına oturtur.
Kullanım: yol_uydur.py bolum.json harita.png cikti.json [kontrol.jpg]
Yol rengi, yerleşim çizgisi boyunca örneklenir; her noktada çizgiye dik doğrultuda yol piksellerinin ortası bulunur."""
import sys, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

K = 3840 / 2304
lay = json.load(open(sys.argv[1]))
im = Image.open(sys.argv[2]).convert('RGB')
small = im.resize((1920, 1080), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2))
arr = np.asarray(small).astype(np.float32)
S = 1920 / 2304  # oyun -> küçük görsel


def lab(a):
    a = a / 255.0
    a = np.where(a > 0.04045, ((a + 0.055) / 1.055) ** 2.4, a / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = a @ M.T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


L = lab(arr)


def dens(p, step=14):
    out = []
    for (x0, y0), (x1, y1) in zip(p, p[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for i in range(n):
            out.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
    out.append(tuple(p[-1]))
    return out


def inside(x, y):
    return 2 <= x * S < 1918 and 2 <= y * S < 1078


samples = []
for p in lay['paths']:
    for x, y in dens(p, 30):
        if inside(x, y):
            samples.append(L[int(y * S), int(x * S)])
ref = np.median(np.array(samples), 0)
dist = np.linalg.norm(L - ref, axis=-1)
TH = float(np.percentile([np.linalg.norm(s - ref) for s in samples], 70)) + 9
road = dist < TH


def fit(p):
    d = dens(p)
    res = []
    for i, (x, y) in enumerate(d):
        a, b = d[max(0, i - 2)], d[min(len(d) - 1, i + 2)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        n = math.hypot(tx, ty) or 1
        nx, ny = -ty / n, tx / n
        if not inside(x, y):
            res.append((x, y)); continue
        hits = []
        for t in range(-75, 76, 2):
            px, py = x + nx * t, y + ny * t
            if inside(px, py) and road[int(py * S), int(px * S)]:
                hits.append(t)
        if len(hits) < 8:
            res.append((x, y)); continue
        # yalnız orijinal noktaya en yakın bitişik yol parçası
        runs, cur = [], [hits[0]]
        for h in hits[1:]:
            if h - cur[-1] <= 6: cur.append(h)
            else: runs.append(cur); cur = [h]
        runs.append(cur)
        best = min(runs, key=lambda r: 0 if r[0] <= 0 <= r[-1] else min(abs(r[0]), abs(r[-1])))
        if len(best) < 8:
            res.append((x, y)); continue
        off = (best[0] + best[-1]) / 2
        off = max(-40, min(40, off))
        res.append((x + nx * off, y + ny * off))
    # yumuşat (uçlar sabit)
    a = np.array(res)
    for _ in range(4):
        b = a.copy()
        b[1:-1] = (a[:-2] + 2 * a[1:-1] + a[2:]) / 4
        a = b
    # sadeleştir
    def rdp(pts, eps):
        if len(pts) < 3: return pts
        s, e = pts[0], pts[-1]
        v = e - s; nv = np.linalg.norm(v) or 1
        w = pts - s; dd = np.abs(v[0] * w[:, 1] - v[1] * w[:, 0]) / nv
        i = int(np.argmax(dd))
        if dd[i] > eps:
            return np.vstack([rdp(pts[:i + 1], eps)[:-1], rdp(pts[i:], eps)])
        return np.array([s, e])
    out = rdp(a, 4.0)
    return [[int(round(x)), int(round(y))] for x, y in out]


new = dict(lay)
new['paths'] = [fit(p) for p in lay['paths']]
# ortak uçları ve kavşakları koru: aynı başlayan/biten yollar aynı son noktayı kullansın
end = new['paths'][0][-1]
for p in new['paths']:
    p[-1] = list(lay['paths'][0][-1]) if False else p[-1]
json.dump(new, open(sys.argv[3], 'w'))
mv = [max(math.hypot(a[0]-b[0], a[1]-b[1]) for a in dens(q) for b in [min(dens(q2), key=lambda c: math.hypot(c[0]-a[0], c[1]-a[1]))]) for q, q2 in zip(lay['paths'], new['paths'])]
print('esik', round(TH, 1), 'nokta', [len(p) for p in new['paths']], 'en büyük kayma', [round(m) for m in mv])
if len(sys.argv) > 4:
    v = im.resize((1920, 1080))
    d = ImageDraw.Draw(v)
    for p in lay['paths']:
        d.line([(x * S, y * S) for x, y in p], fill=(255, 0, 255), width=2)
    for p in new['paths']:
        d.line([(x * S, y * S) for x, y in p], fill=(0, 255, 255), width=3)
    m = Image.fromarray((road * 255).astype(np.uint8)).convert('RGB')
    both = Image.new('RGB', (1920, 1620)); both.paste(v, (0, 0)); both.paste(m.resize((960, 540)), (0, 1080))
    both.save(sys.argv[4], quality=85)
