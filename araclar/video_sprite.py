"""Video (magenta or green bg) -> keyed RGBA sprite sheet + manifest entry.
usage: sheet.py video.mp4 out.webp N body_h [--kenar SOL,SAG,UST,ALT] [--karisim]
--kenar: efekt video kenarına değip kesiliyorsa, o kenardan verilen px (1920x1080 ölçeğinde) içeriye
  doğru saydamlığı yumuşakça sıfıra indirir; düz kesik çizgi yerine sönümlenme görünür.
  Kule gövdesi çoğu videoda üst/alt kenara 20-40 px yakın: önce gövde payını ölçün, ona dokunmayın.
--altin: yarı saydam ve pembeye kaymış efekt piksellerini (altın ışıltı magentayla karışınca oluşur)
  parlaklığı koruyarak altın tonuna çevirir. Yalnızca altın/sarı efektli kulelerde kullanın.
--beyaz: aynı düzeltme, nötr beyaz/gri tonla (buhar, duman, bulut).
--karisim: saydamlığı perde renginin baskınlığından hesaplar (buhar, duman, bulut gibi yarı saydam
  beyaz/koyu efektlerde pembe/mor hale kalmaz). Kulenin kendisinde magenta/mor yoksa kullanın."""
import sys, json, subprocess, math, tempfile, glob, os
import numpy as np
from PIL import Image
from scipy import ndimage

args = [a for a in sys.argv[1:]]
FEATHER = None
if '--kenar' in args:
    i = args.index('--kenar'); FEATHER = [int(v) for v in args[i + 1].split(',')]; del args[i:i + 2]
    assert len(FEATHER) == 4
MIX = '--karisim' in args
if MIX: args.remove('--karisim')
GOLD = '--altin' in args
if GOLD: args.remove('--altin')
WHITE = '--beyaz' in args
if WHITE: args.remove('--beyaz')
vid, out, N, BODY = args[0], args[1], int(args[2]), int(args[3])
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', vid]))
tmp = tempfile.mkdtemp()
# N evenly spaced frames over the clip (last frame == first for loops, so it is excluded)
subprocess.check_call(['ffmpeg', '-v', 'error', '-i', vid, '-vf', f'fps={N}/{dur},scale=1920:1080:flags=area', '-frames:v', str(N), f'{tmp}/f_%03d.png'])
paths = sorted(glob.glob(f'{tmp}/f_*.png'))
assert len(paths) == N, (len(paths), N)
frames = [np.asarray(Image.open(p).convert('RGB')).astype(np.float32) for p in paths]

f0 = frames[0]
corners = np.concatenate([f0[:20, :20].reshape(-1, 3), f0[:20, -20:].reshape(-1, 3), f0[-20:, :20].reshape(-1, 3), f0[-20:, -20:].reshape(-1, 3)])
K = np.median(corners, 0)
MAGENTA = K[0] > 180 and K[2] > 180 and K[1] < 80
GREEN = K[1] > 180 and K[0] < 90 and K[2] < 90
assert MAGENTA or GREEN, K
def _r(dist, px):
    if px <= 0: return np.ones_like(dist, dtype=np.float32)
    t = np.clip(dist / px, 0, 1); return t * t * (3 - 2 * t)  # smoothstep
if FEATHER:
    L, R, T, B = FEATHER
    xs_, ys_ = np.arange(1920, dtype=np.float32), np.arange(1080, dtype=np.float32)
    ramp = (_r(ys_, T) * _r(1079 - ys_, B))[:, None] * (_r(xs_, L) * _r(1919 - xs_, R))[None, :]

def key(img):
    d = np.sqrt(((img - K) ** 2).sum(-1))
    a = np.clip((d - 70) / 90, 0, 1)
    if MIX:  # perde baskınlığı: magenta için min(r,b)-g, yeşil için g-max(r,b)
        if MAGENTA: dom, kd = np.minimum(img[..., 0], img[..., 2]) - img[..., 1], min(K[0], K[2]) - K[1]
        else: dom, kd = img[..., 1] - np.maximum(img[..., 0], img[..., 2]), K[1] - max(K[0], K[2])
        am = np.clip((1 - dom / kd - 0.08) / 0.84, 0, 1)
        a = am
    lab, n = ndimage.label(a > 0.02)
    if n:
        core = ndimage.sum(a > 0.5, lab, range(1, n + 1))
        keep = np.zeros(n + 1, bool); keep[1:] = core >= 400  # drop specks and faint haze
        a = a * keep[lab]
    # unmix the magenta from semi-transparent edge pixels
    safe = np.maximum(a, 1e-3)[..., None]
    rgb = np.clip((img - (1 - safe) * K) / safe, 0, 255)
    edge = (a < 0.999)[..., None]
    rgb = np.where(edge, rgb, img)
    if MAGENTA:  # residual spill: magenta = r,b both above g
        sp = np.clip(np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1] - (0 if MIX else 25), 0, None) * (a < 0.999)
        rgb[..., 0] -= sp; rgb[..., 2] -= sp
    else:  # green spill: g above both r,b
        sp = np.clip(rgb[..., 1] - np.maximum(rgb[..., 0], rgb[..., 2]) - (0 if MIX else 10), 0, None) * (a < 0.999)
        rgb[..., 1] -= sp
    if (GOLD or WHITE) and MAGENTA:
        semi = (a > 0) & (rgb[..., 2] > rgb[..., 1] * 0.9) & (rgb[..., 0] > rgb[..., 1] + 15)
        lum = (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2])[..., None]
        tone = np.array([1.18, 0.98, 0.62] if GOLD else [1.0, 1.0, 1.0], np.float32)  # lum(tone)≈1
        rgb = np.where(semi[..., None], np.clip(lum * tone, 0, 255), rgb)
    if FEATHER: a = a * ramp
    return np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8)

rgba = [key(f) for f in frames]
body = rgba[0][..., 3] > 128
ys, xs = np.where(body)
bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
union = np.zeros(body.shape, bool)
for r in rgba: union |= r[..., 3] > 20
uy, ux = np.where(union)
P = 6
cx0, cx1 = max(ux.min() - P, 0), min(ux.max() + 1 + P, 1920)
cy0, cy1 = max(uy.min() - P, 0), min(uy.max() + 1 + P, 1080)
s = BODY / (by1 - by0)
cols = math.ceil(math.sqrt(N)); rows = math.ceil(N / cols)
while True:
    fw, fh = round((cx1 - cx0) * s), round((cy1 - cy0) * s)
    if fw * cols <= 4096 and fh * rows <= 4096: break
    s *= 0.95
sheet = Image.new('RGBA', (fw * cols, fh * rows), (0, 0, 0, 0))
for k, r in enumerate(rgba):
    im = Image.fromarray(r[cy0:cy1, cx0:cx1], 'RGBA')
    # premultiplied resize avoids dark halos
    im = im.convert('RGBa').resize((fw, fh), Image.LANCZOS).convert('RGBA')
    sheet.paste(im, ((k % cols) * fw, (k // cols) * fh))
sheet.save(out, 'WEBP', quality=88, method=6)
entry = dict(frameWidth=fw, frameHeight=fh, frames=N,
             originX=round(((bx0 + bx1) / 2 - cx0) / (cx1 - cx0), 4),
             originY=round((by1 - cy0) / (cy1 - cy0), 4),
             bodyHeight=round((by1 - by0) * s, 1))
print(json.dumps(entry))
for p in paths: os.remove(p)
os.rmdir(tmp)
