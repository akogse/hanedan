"""Telefon için küçük animasyon sayfaları üretir (bellek!). Her sayfa, oyunda ekranda en fazla göründüğü boyutun
ORAN katı çözünürlüğe indirilir; zaten küçük olanlara dokunulmaz. Çıktı: assets/k/<ad>.webp ve oyun.js içindeki
KUCUK tablosu (// KUCUK-BAS ... // KUCUK-SON arası). Oyun, ekranı küçük cihazda (q <= 1.5) bu tabloyu kullanır.
kullanım: python3 araclar/kucult.py   (yeni sayfa eklendikçe yeniden çalıştır; değişmeyenleri atlar)"""
import re, os, json
from PIL import Image
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(KOK)
ORAN = 1.6  # mantıksal piksel başına kaynak piksel (telefon q≈1.2, yakınlaştırma payıyla)
src = open('kaynak/oyun.js', encoding='utf-8').read()
zt = dict(re.findall(r'^\s+"?(\w+)"?:\s*"(assets/[^"]+)"', src[:src.index('\n  et = {')], re.M))
xt = {}
for k, body in re.findall(r'^  (\w+): \{([^}]*)\}', src[src.index('var xt = {'):src.index('var xt = {') + 40000], re.M):
    w = re.search(r'\bw: ([\d.]+)', body); h = re.search(r'\bh: ([\d.]+)', body)
    xt[k] = (float(w.group(1)) if w else None, float(h.group(1)) if h else None)
ets = re.findall(r'^\s+"?(\w+)"?: \{\s*url: "(assets/[^"]+)",\s*frameWidth: (\d+),\s*frameHeight: (\d+),\s*frames: (\d+),[^}]*?bodyHeight: ([\d.]+)', src, re.M)
os.makedirs('assets/k', exist_ok=True)
tablo, once, sonra = {}, 0, 0
for key, url, fw, fh, n, bh in ets:
    fw, fh, bh = int(fw), int(fh), float(bh)
    s = max((x for x in xt if key.startswith(x + '_')), key=len, default=None)
    if not s or not os.path.exists(url): continue
    w_, h_ = xt[s]
    if h_: goz = h_
    elif w_ and s in zt and os.path.exists(zt[s]):
        iw, ih = Image.open(zt[s]).size; goz = w_ * ih / iw
    else: continue
    f = ORAN * goz / bh
    if os.environ.get('TANI'): print(key, round(f, 2))
    if f > 0.85: continue  # kazanç az
    nfw, nfh = max(8, round(fw * f)), max(8, round(fh * f))
    im = Image.open(url); W, H = im.size; cols, rows = W // fw, H // fh
    hedef = 'assets/k/' + os.path.basename(url)
    if not (os.path.exists(hedef) and os.path.getmtime(hedef) >= os.path.getmtime(url) and Image.open(hedef).size == (cols * nfw, rows * nfh)):
        im.convert('RGBA').resize((cols * nfw, rows * nfh), Image.LANCZOS).save(hedef, 'WEBP', quality=88, method=4)
    tablo[key] = [hedef, nfw, nfh]
    once += W * H * 4; sonra += cols * nfw * rows * nfh * 4
# --- tek görseller (zt): ekranda en büyük göründükleri ölçek araclar/gorunum.json'da (t_gorunum ölçümü).
# Oyun bu görselleri küçük yükler ama dokuyu ASIL boyutuyla tanıtır (addImage kancası): yerleşim hiç değişmez.
HARIC = {'panel_kucuk', 'harita_zemin_yol', 'harita_zemin_cim', 'harita_zemin_parsomen', 'z_xp_dolgu', 'sv_boss_dolgu', 'parcacik', 'brf_kahraman_yuva_secili'}
gor = json.load(open('araclar/gorunum.json'))['gor'] if os.path.exists('araclar/gorunum.json') else {}
tablog, g_once, g_sonra = {}, 0, 0
for key, url in zt.items():
    if key in HARIC or not os.path.exists(url) or url.startswith('assets/k/'): continue
    im = Image.open(url); W, H = im.size
    if key in gor: f = min(1, 1.5 * gor[key])
    elif max(W, H) <= 1100: f = min(1, 768 / max(W, H))  # ölçülmemiş: 768 px'e kadar (512 mantıksal px'e dek keskin)
    else: continue
    if f > 0.8: continue
    nw, nh = max(4, round(W * f)), max(4, round(H * f))
    hedef = 'assets/k/' + os.path.basename(url)
    if not (os.path.exists(hedef) and os.path.getmtime(hedef) >= os.path.getmtime(url) and Image.open(hedef).size == (nw, nh)):
        im.convert('RGBA').resize((nw, nh), Image.LANCZOS).save(hedef, 'WEBP', quality=90, method=4)
    tablog[key] = [hedef, W, H]
    g_once += W * H * 4; g_sonra += nw * nh * 4
print(f'{len(tablog)} görsel küçültüldü: {g_once / 2**20:.0f} MB -> {g_sonra / 2**20:.0f} MB (çözülmüş)')
satirlarg = ',\n'.join(f'  {k}: ["{v[0]}", {v[1]}, {v[2]}]' for k, v in sorted(tablog.items()))
satirlar = ',\n'.join(f'  {k}: ["{v[0]}", {v[1]}, {v[2]}]' for k, v in sorted(tablo.items()))
blok = f'// KUCUK-BAS (araclar/kucult.py üretir, elle düzenleme)\nvar KUCUK = {{\n{satirlar}\n}};\nvar KUCUKG = {{\n{satirlarg}\n}};\n// KUCUK-SON'
src = re.sub(r'// KUCUK-BAS.*?// KUCUK-SON', lambda m: blok, src, flags=re.S)
open('kaynak/oyun.js', 'w', encoding='utf-8').write(src)
print(f'{len(tablo)} sayfa küçültüldü: {once / 2**20:.0f} MB -> {sonra / 2**20:.0f} MB (çözülmüş)')
