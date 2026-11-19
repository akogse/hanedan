"""Kule saldırı sayfalarını bekleme sayfasına hizalar: ilk karedeki gövde tabanı ve genişliği eşlenir."""
import re, json, sys
import numpy as np
from PIL import Image
from scipy import ndimage
src = open('kaynak/oyun.js').read()
ent = {}
for m in re.finditer(r'\n    ([a-z0-9_]+): \{\n      url: "assets/(anim_[^"]+)",\n      frameWidth: (\d+),\n      frameHeight: (\d+),\n      frames: (\d+),\n      originX: ([\d.]+),\n      originY: ([\d.]+),\n      bodyHeight: ([\d.]+),', src):
    k, u, fw, fh, n, ox, oy, bh = m.groups()
    ent[k] = dict(url=u, fw=int(fw), fh=int(fh), ox=float(ox), oy=float(oy), bh=float(bh))
def body(k):
    e = ent[k]; im = np.array(Image.open('assets/' + e['url']).convert('RGBA'))[:e['fh'], :e['fw'], 3] > 128
    lab, n = ndimage.label(im)
    if not n: return None
    sz = ndimage.sum(im, lab, range(1, n + 1)); big = lab == (np.argmax(sz) + 1)
    ys, xs = np.where(big)
    # taban: en alt satırların orta noktası; genişlik: alt %25'teki kaide genişliği
    y1 = ys.max(); low = big[int(y1 - (y1 - ys.min()) * 0.25):y1 + 1]
    lx = np.where(low.any(0))[0]
    return dict(bx=(lx.min() + lx.max()) / 2, by=y1, bw=lx.max() - lx.min() + 1, h=y1 - ys.min())
out = []
for k in sorted(ent):
    if '_saldiri' not in k or not k.startswith('kule_'): continue
    base = re.sub(r'_saldiri(_sag|_sol)?$', '', k) + '_bekle'
    if base not in ent: continue
    a, b = body(base), body(k)
    if not a or not b: continue
    ea, eb = ent[base], ent[k]
    # bekleme: ekranda taban noktası (origin'e göre), ölçek = görünen/bodyHeight
    sa = 1 / ea['bh']; sb_need = sa * a['bw'] / b['bw']  # kaide genişliği eşit olacak ölçek
    bh_new = 1 / sb_need
    ax = (a['bx'] - ea['ox'] * ea['fw']) * sa; ay = (a['by'] - ea['oy'] * ea['fh']) * sa
    # saldırıda aynı taban noktası: (b.bx - ox*fw)*sb = ax  -> ox
    ox = (b['bx'] - ax / sb_need) / eb['fw']; oy = (b['by'] - ay / sb_need) / eb['fh']
    d = abs(ox - eb['ox']) * eb['fw'] * sb_need * 270 + abs(oy - eb['oy']) * eb['fh'] * sb_need * 270 + abs(bh_new / eb['bh'] - 1) * 100
    out.append((round(d, 1), k, round(eb['ox'], 4), round(ox, 4), round(eb['oy'], 4), round(oy, 4), eb['bh'], round(bh_new, 1)))
for o in sorted(out, reverse=True)[:40]: print(o)
if '--yaz' in sys.argv:
    for d, k, ox0, ox, oy0, oy, bh0, bh in out:
        if d < 3: continue
        pat = re.compile(r'(\n    ' + k + r': \{\n      url: "[^"]+",\n      frameWidth: \d+,\n      frameHeight: \d+,\n      frames: \d+,\n      originX: )[\d.]+(,\n      originY: )[\d.]+(,\n      bodyHeight: )[\d.]+')
        src, n = pat.subn(lambda m: m.group(1) + str(ox) + m.group(2) + str(oy) + m.group(3) + str(bh), src)
        assert n == 1, k
    open('kaynak/oyun.js', 'w').write(src); print('yazıldı')
