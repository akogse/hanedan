"""Simülasyon botu için bölüm planı üretir: yolu en çok gören noktalara karışık kule kurar, yükseltir, dal alır."""
import sys, json, math
lay = json.load(open(sys.argv[1]))
tip = sys.argv[2] if len(sys.argv) > 2 else 'cag2'
def dens(p, step=20):
    out = []
    for (x0, y0), (x1, y1) in zip(p, p[1:]):
        n = max(1, int(math.hypot(x1-x0, y1-y0)/step))
        out += [(x0+(x1-x0)*i/n, y0+(y1-y0)*i/n) for i in range(n)]
    return out
pts = [q for p in lay['paths'] for q in dens(p)]
def cov(sp, r=300): return sum(1 for x, y in pts if math.hypot(x-sp[0], y-sp[1]) < r)
# açgözlü seçim: her yeni kule, henüz iki kulenin görmediği yol noktalarını en çok kapsayan nokta
gor = [0] * len(pts)
order, kalan = [], list(range(len(lay['spots'])))
while kalan:
    def kazanc(i):
        x, y = lay['spots'][i]
        return sum(1 for j, (a, b) in enumerate(pts) if gor[j] < 2 and math.hypot(a-x, b-y) < 290)
    i = max(kalan, key=kazanc)
    order.append(i); kalan.remove(i)
    x, y = lay['spots'][i]
    for j, (a, b) in enumerate(pts):
        if math.hypot(a-x, b-y) < 290: gor[j] += 1
import os
kule = os.environ.get('KULE', 'archer,storm,archer,barracks,fire,alchemist,eagle,rune,frost,ballista,storm,archer,fire,barracks').split(',')
dal = {'storm': 'chainLightning', 'fire': 'hellCatapult', 'barracks': 'guards', 'archer': 'sniper', 'frost': 'blizzard', 'alchemist': 'acid',
       'ballista': 'piercingSpear', 'rune': 'warRune', 'eagle': 'griffinRiders'}
n = min(len(order), len(kule))
plan = []
sec = list(zip(order[:n], kule[:n]))
for sp, k in sec[:4]: plan.append(['build', sp, k])
for sp, k in sec[:4]: plan.append(['up', sp])
for sp, k in sec[4:8]: plan.append(['build', sp, k])
for sp, k in sec[:4]: plan.append(['up', sp])
for sp, k in sec[4:8]: plan.append(['up', sp])
for sp, k in sec[:3]: plan.append(['dal', sp, dal[k]])
for sp, k in sec[8:]: plan.append(['build', sp, k])
for sp, k in sec[4:8]: plan.append(['up', sp])
for sp, k in sec[3:8]: plan.append(['dal', sp, dal[k]])
for sp, k in sec[8:]: plan += [['up', sp], ['up', sp]]
for sp, k in sec[8:]: plan.append(['dal', sp, dal[k]])
print(json.dumps(plan))
