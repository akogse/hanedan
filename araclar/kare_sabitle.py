"""Saldırı/bekleme sayfalarında kamera kayması: her karede kaide (alt kısım) ilk kareye göre kayıyor/büyüyorsa
kareyi kaide sabit kalacak şekilde kaydırıp ölçekler. Kullanım: kare_sabitle.py [--yaz] [anahtar_filtresi]"""
import re, sys, math
import numpy as np
from PIL import Image
from scipy import ndimage
src = open('kaynak/oyun.js').read()
ent = {}
for m in re.finditer(r'\n    ([a-z0-9_]+): \{\n      url: "assets/(anim_[^"]+)",\n      frameWidth: (\d+),\n      frameHeight: (\d+),\n      frames: (\d+),', src):
    k, u, fw, fh, n = m.groups(); ent[k] = (u, int(fw), int(fh), int(n))
flt = [a for a in sys.argv[1:] if not a.startswith('--')]
def kaide(a):
    m = a > 128
    lab, n = ndimage.label(m)
    if not n: return None
    sz = ndimage.sum(m, lab, range(1, n + 1)); big = lab == (np.argmax(sz) + 1)
    ys, xs = np.where(big); y1 = ys.max(); h = y1 - ys.min()
    low = big[int(y1 - h * 0.2):y1 + 1]; lx = np.where(low.any(0))[0]
    return np.array([(lx.min() + lx.max()) / 2, y1, lx.max() - lx.min() + 1])
for k, (u, fw, fh, n) in sorted(ent.items()):
    if not k.startswith('kule_') or (flt and not any(f in k for f in flt)): continue
    im = Image.open('assets/' + u).convert('RGBA'); cols = im.width // fw
    cells = [im.crop(((i % cols) * fw, (i // cols) * fh, (i % cols + 1) * fw, (i // cols + 1) * fh)) for i in range(n)]
    ks = [kaide(np.array(c)[..., 3]) for c in cells]
    if ks[0] is None: continue
    dx = [abs(q[0] - ks[0][0]) for q in ks if q is not None]; dy = [abs(q[1] - ks[0][1]) for q in ks if q is not None]
    sc = [q[2] / ks[0][2] for q in ks if q is not None]
    worst = max(max(dx), max(dy)) / fh * 270 * 2
    print(f'{worst:6.1f} {k:45s} dx{max(dx):5.0f} dy{max(dy):5.0f} ölçek {min(sc):.2f}-{max(sc):.2f}')
    if '--yaz' in sys.argv and worst > 6:
        out = Image.new('RGBA', im.size, (0, 0, 0, 0))
        for i, (c, q) in enumerate(zip(cells, ks)):
            if q is None: out.paste(c, ((i % cols) * fw, (i // cols) * fh)); continue
            s = ks[0][2] / q[2] if abs(q[2] / ks[0][2] - 1) > 0.04 else 1.0
            c2 = c.convert('RGBa').resize((max(1, round(fw * s)), max(1, round(fh * s))), Image.LANCZOS).convert('RGBA') if s != 1 else c
            ox = ks[0][0] - q[0] * s; oy = ks[0][1] - q[1] * s
            cell = Image.new('RGBA', (fw, fh), (0, 0, 0, 0)); cell.alpha_composite(c2, (0, 0)) if False else None
            cell.paste(c2, (round(ox), round(oy)), c2)
            out.paste(cell, ((i % cols) * fw, (i // cols) * fh))
        out.save('assets/' + u, 'WEBP', quality=88, method=6); print('   -> sabitlendi')
