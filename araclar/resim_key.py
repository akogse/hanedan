"""Düz magenta arka planlı görseli şeffaf PNG/WebP'ye çevirir (video_sprite ile aynı ayrıştırma).
Kullanım: resim_key.py girdi.png cikti.webp [max_kenar]"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
src, out = sys.argv[1], sys.argv[2]
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 512
img = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
c = np.concatenate([img[:12, :12].reshape(-1, 3), img[:12, -12:].reshape(-1, 3), img[-12:, :12].reshape(-1, 3), img[-12:, -12:].reshape(-1, 3)])
K = np.median(c, 0)
assert K[0] > 180 and K[2] > 180 and K[1] < 90, K
d = np.sqrt(((img - K) ** 2).sum(-1))
a = np.clip((d - 70) / 90, 0, 1)
lab, n = ndimage.label(a > 0.02)
if n:
    core = ndimage.sum(a > 0.5, lab, range(1, n + 1))
    keep = np.zeros(n + 1, bool); keep[1:] = core >= 60
    a = a * keep[lab]
safe = np.maximum(a, 1e-3)[..., None]
rgb = np.clip((img - (1 - safe) * K) / safe, 0, 255)
rgb = np.where((a < 0.999)[..., None], rgb, img)
sp = np.clip(np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1] - 25, 0, None) * (a < 0.999)
rgb[..., 0] -= sp; rgb[..., 2] -= sp
im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8), 'RGBA')
bb = im.getbbox(); im = im.crop((max(bb[0]-4,0), max(bb[1]-4,0), min(bb[2]+4,im.width), min(bb[3]+4,im.height)))
im = im.convert('RGBa'); im.thumbnail((mx, mx), Image.LANCZOS); im = im.convert('RGBA')
im.save(out, quality=90, method=6)
print(out, im.size)
