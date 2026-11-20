"""Animasyon sayfalarında karenin kenarına dayanıp kesilen efektleri (yıldırım, buz, alev, kanat) yumuşatır:
kenara değen içerik olan kenarlarda, karenin dış şeridinde saydamlık dışa doğru sıfıra iner. Sert kesik çizgi kaybolur.
kullanım: python3 araclar/kenar_yumusat.py [anahtar_öneki ...]   (önek verilmezse bütün kule sayfaları)"""
import re, sys, os, numpy as np
from PIL import Image
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src = open('kaynak/oyun.js', encoding='utf-8').read()
ets = re.findall(r'^\s+"?(\w+)"?: \{\s*url: "(assets/[^"]+)",\s*frameWidth: (\d+),\s*frameHeight: (\d+),\s*frames: (\d+)', src, re.M)
onek = sys.argv[1:] or ['kule_']
ESIK = 30
for k, u, fw, fh, n in ets:
    if not any(k.startswith(o) for o in onek) or '/k/' in u or k.endswith('_bekle'): continue  # bekleme karesi = gövde
    fw, fh, n = int(fw), int(fh), int(n)
    im = Image.open(u).convert('RGBA'); a = np.asarray(im).copy()
    cols = a.shape[1] // fw
    kenar = {'ust': 0, 'sol': 0, 'sag': 0, 'alt': 0}
    for i in range(n):
        r, c = divmod(i, cols); f = a[r * fh:(r + 1) * fh, c * fw:(c + 1) * fw, 3]
        kenar['ust'] = max(kenar['ust'], (f[:3] > 40).sum()); kenar['alt'] = max(kenar['alt'], (f[-3:] > 40).sum())
        kenar['sol'] = max(kenar['sol'], (f[:, :3] > 40).sum()); kenar['sag'] = max(kenar['sag'], (f[:, -3:] > 40).sum())
    kes = [e for e, v in kenar.items() if v > ESIK and e != 'alt']
    if not kes: continue
    m = np.ones((fh, fw), np.float32)
    ty, tx = max(4, int(fh * 0.12)), max(4, int(fw * 0.08))
    yy = np.arange(fh)[:, None]; xx = np.arange(fw)[None, :]
    if 'ust' in kes: m = np.minimum(m, np.clip(yy / ty, 0, 1) ** 1.5)
    if 'sol' in kes: m = np.minimum(m, np.clip(xx / tx, 0, 1) ** 1.5)
    if 'sag' in kes: m = np.minimum(m, np.clip((fw - 1 - xx) / tx, 0, 1) ** 1.5)
    # kulenin kendisi (ilk karede, dinlenirken görünen gövde: tepe küresi, bayraklar) solmaz; yalnız saldırıyla eklenen ışık solar
    from scipy import ndimage
    govde = ndimage.binary_dilation(a[0:fh, 0:fw, 3] > 128, iterations=3)
    m = np.where(govde, 1.0, m)
    for i in range(n):
        r, c = divmod(i, cols); sl = a[r * fh:(r + 1) * fh, c * fw:(c + 1) * fw, 3]
        sl[:] = (sl * m).astype(np.uint8)
    Image.fromarray(a, 'RGBA').save(u, 'WEBP', quality=90, method=4)
    print(k, kes)
