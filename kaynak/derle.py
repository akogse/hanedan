"""kaynak/oyun.js + kaynak/sablon.html -> index.html. Kullanim: python3 kaynak/derle.py"""
import os, re
k = os.path.dirname(os.path.abspath(__file__))
kok = os.path.dirname(k)
sablon = open(os.path.join(k, 'sablon.html'), encoding='utf-8').read()
oyun = open(os.path.join(k, 'oyun.js'), encoding='utf-8').read()
assert '</script' not in oyun.lower()
assert sablon.count('/*OYUN_KODU*/') == 1
# üst düzey ad çakışması kontrolü: derlenmiş kodda adlar kısa; yeni bir "var X" eskisinin üstüne yazmasın
from collections import Counter
adlar, blok = [], None
for satir in oyun.split('\n'):
    if blok:
        if satir == '}': blok = None
        continue
    m = re.match(r'^(class|function) ([A-Za-z_$][\w$]*)', satir)
    if m:
        adlar.append(m.group(2)); blok = not satir.rstrip().endswith('}'); continue
    m = re.match(r'^(?:var|let|const) ([A-Za-z_$][\w$]*)', satir) or re.match(r'^  ([A-Za-z_$][\w$]*) =', satir)
    if m: adlar.append(m.group(1))
cift = [a for a, n in Counter(adlar).items() if n > 1]
assert not cift, f"ayni ust duzey ad birden fazla tanimlanmis: {cift}"
open(os.path.join(kok, 'index.html'), 'w', encoding='utf-8').write(sablon.replace('/*OYUN_KODU*/', oyun))
# servis calisani onbellek surumunu her derlemede yenile
sw = os.path.join(kok, 'sw.js'); t = open(sw).read()
import time
t = re.sub(r"const V = 'hanedan-\d+'", f"const V = 'hanedan-{int(time.time())}'", t)
open(sw, 'w').write(t)
print('index.html derlendi')
