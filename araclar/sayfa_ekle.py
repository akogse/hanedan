"""Sprite sayfalarını oyun.js animasyon listesine ekler; bağlantı noktasını sabit kule görseline hizalar.
Kullanım: python3 sayfa_ekle.py oyun.js manifest.txt"""
import sys, json, re
p, man = sys.argv[1], sys.argv[2]
s = open(p, encoding='utf-8').read()
anchor = '    kule_ayaz_1_bekle: {\n'
assert s.count(anchor) == 1
add = ''
for line in sorted(open(man)):
    if line.startswith('FAIL'):
        print('ATLANDI', line.strip()); continue
    key, js = line.split(' ', 1)
    m = json.loads(js)
    if f'    {key}: {{\n' in s:
        print('zaten var', key); continue
    base = re.match(r'(kule_[a-z_]+?(?:_dal_[a-z]+|_\d))', key).group(1)
    oy = float(re.search(base + r': \{ w: \d+, ox: [\d.]+, oy: ([\d.]+) \}', s).group(1))
    fh, bh = m['frameHeight'], m['bodyHeight']
    origin_y = round((m['originY'] * fh - bh + oy * bh) / fh, 4)
    add += (f'    {key}: {{\n      url: "assets/anim_{key}.webp",\n      frameWidth: {m["frameWidth"]},\n'
            f'      frameHeight: {fh},\n      frames: {m["frames"]},\n      originX: {m["originX"]},\n'
            f'      originY: {origin_y},\n      bodyHeight: {bh},\n    }},\n')
    print('eklendi', key)
s = s.replace(anchor, add + anchor)
open(p, 'w', encoding='utf-8').write(s)
