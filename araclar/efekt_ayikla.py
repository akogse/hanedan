"""Flow saldırı videosundan kuleden bağımsız ışık efekti ayıklar (buz patlaması, şimşek, alev, zehir parıltısı).
Yöntem: her karenin (perde ayıklanmış, önceden çarpılmış) renginden ilk karenin (kule dinlenirken) rengi çıkarılır;
geriye yalnızca EKLENEN ışık kalır. Sayfa siyah zeminlidir ve oyunda ADD karışımıyla basılır (siyah = görünmez).
kullanım: efekt_ayikla.py video.mp4 cikti.webp KARE [--aralik bas-son] [--esik 18] [--boy 512]
  --aralik: saniye; verilmezse hareketin en yoğun olduğu ±1.2 sn
  --boy: çıktı karesinin uzun kenarı (px)
Çıktı satırı: manifest (frameWidth, frameHeight, frames, cx, cy: efekt merkezi, kare içinde 0-1)."""
import sys, json, subprocess, tempfile, glob, os, math
import numpy as np
from PIL import Image

a = sys.argv[1:]
def opt(k, d=None, f=str):
    if k in a:
        i = a.index(k); v = a[i + 1]; del a[i:i + 2]; return f(v)
    return d
ARALIK = opt('--aralik'); ESIK = opt('--esik', 18, float); BOY = opt('--boy', 512, int)
vid, out, N = a[0], a[1], int(a[2])
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', vid]))
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', vid, '-vf', 'scale=192:108,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
g = np.frombuffer(raw, np.uint8).reshape(-1, 108, 192).astype(np.float32)
fps_v = len(g) / dur
mo = np.convolve(np.abs(np.diff(g, axis=0)).mean((1, 2)), np.ones(5) / 5, 'same')
if ARALIK: t0, t1 = map(float, ARALIK.split('-'))
else:
    pt = np.argmax(mo) / fps_v; t0, t1 = max(0, pt - 1.2), min(dur, pt + 1.2)
tmp = tempfile.mkdtemp()
# dinlenme karesi: videonun ilk karesi
subprocess.check_call(['ffmpeg', '-v', 'error', '-i', vid, '-vf', 'scale=1920:1080:flags=area', '-frames:v', '1', f'{tmp}/r.png'])
subprocess.check_call(['ffmpeg', '-v', 'error', '-ss', f'{t0:.3f}', '-t', f'{t1 - t0:.3f}', '-i', vid, '-vf', f'fps={N}/{t1 - t0},scale=1920:1080:flags=area', '-frames:v', str(N), f'{tmp}/f_%03d.png'])
paths = sorted(glob.glob(f'{tmp}/f_*.png'))
def yukle(p): return np.asarray(Image.open(p).convert('RGB')).astype(np.float32)
r0 = yukle(f'{tmp}/r.png')
cor = np.concatenate([r0[:20, :20].reshape(-1, 3), r0[:20, -20:].reshape(-1, 3), r0[-20:, :20].reshape(-1, 3), r0[-20:, -20:].reshape(-1, 3)])
K = np.median(cor, 0)
def premul(img):
    d = np.sqrt(((img - K) ** 2).sum(-1)); al = np.clip((d - 70) / 90, 0, 1)
    safe = np.maximum(al, 1e-3)[..., None]
    rgb = np.clip((img - (1 - safe) * K) / safe, 0, 255)
    # magenta taşması
    sp = np.clip(np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1] - 25, 0, None) * (al < 0.999)
    rgb[..., 0] -= sp; rgb[..., 2] -= sp
    return rgb * al[..., None], al
R, A0 = premul(r0)
# kulenin gövdesi: dinlenme karesinde opak olan yer (biraz genişletilmiş). Gövde üstünde yalnızca güçlü parlama kalır,
# kulenin ışığının hafifçe değişmesi ya da kıpırdaması efekt sanılmasın.
from scipy import ndimage
GOVDE = ndimage.binary_dilation(A0 > 0.5, iterations=6)
isik = []
for p in paths:
    f, _ = premul(yukle(p))
    d = np.clip(f - R, 0, 255)
    m_ = d.max(-1)
    d[m_ < ESIK] = 0  # titreme ve sıkıştırma gürültüsü
    # gövde üstünde: 70'in altındaki artış silinir, üstü yumuşakça kalır
    k = np.clip((m_ - 70) / 60, 0, 1)
    d = np.where(GOVDE[..., None], d * k[..., None], d)
    isik.append(d)
os.system(f'rm -rf {tmp}')
top = np.zeros(isik[0].shape[:2], bool)
for d in isik: top |= d.max(-1) > ESIK * 1.5
ys, xs = np.where(top)
P = 10
x0, x1 = max(0, xs.min() - P), min(1920, xs.max() + P); y0, y1 = max(0, ys.min() - P), min(1080, ys.max() + P)
s = BOY / max(x1 - x0, y1 - y0)
fw, fh = round((x1 - x0) * s), round((y1 - y0) * s)
cols = math.ceil(math.sqrt(N)); rows = math.ceil(N / cols)
while fw * cols > 4096 or fh * rows > 4096: s *= 0.95; fw, fh = round((x1 - x0) * s), round((y1 - y0) * s)
sheet = Image.new('RGB', (fw * cols, fh * rows), (0, 0, 0))
for k, d in enumerate(isik):
    im = Image.fromarray(d[y0:y1, x0:x1].astype(np.uint8), 'RGB').resize((fw, fh), Image.LANCZOS)
    sheet.paste(im, ((k % cols) * fw, (k // cols) * fh))
sheet.save(out, 'WEBP', quality=90, method=6)
# efekt merkezi: toplam ışığın ağırlık merkezi
W = sum(d.max(-1) for d in isik)[y0:y1, x0:x1]
yy, xx = np.mgrid[0:W.shape[0], 0:W.shape[1]]
print(json.dumps(dict(frameWidth=fw, frameHeight=fh, frames=N, cx=round(float((W * xx).sum() / W.sum() / W.shape[1]), 3), cy=round(float((W * yy).sum() / W.sum() / W.shape[0]), 3), aralik=f'{t0:.2f}-{t1:.2f}')))
