"""Merge per-building partial bundles into village_houses.json + village_houses.meta.json (plain python)."""
import json, os, sys
OUT = '/shared/river/assets/out'
PD = OUT + '/vh_parts'
ORDER = ['house_farm', 'house_cottage_a', 'house_cottage_b', 'house_row', 'bakery', 'smithy', 'inn', 'church', 'barn', 'storehouse']
mats, parts, meta = {}, [], {}
rep = {}
for n in ORDER:
    f = PD + '/' + n + '.json'
    if not os.path.exists(f):
        print('MISSING', n); continue
    d = json.load(open(f))
    for k, v in d['mats'].items():
        if k in mats and mats[k] != v:
            print('MAT CONFLICT', k, n)
        mats.setdefault(k, v)
    tris = 0
    for p in d['parts']:
        parts.append(p)
        if p['name'] == n:
            tris = sum(s['tris'] for s in p['subs'])
    m = json.load(open(PD + '/' + n + '.meta.json'))
    meta[n] = m
    rep[n] = tris
bundle = {'meta': {'name': 'village_houses', 'buildings': ORDER}, 'mats': mats, 'parts': parts}
json.dump(bundle, open(OUT + '/village_houses.json', 'w'), separators=(',', ':'))
json.dump(meta, open(OUT + '/village_houses.meta.json', 'w'), indent=1, ensure_ascii=False)
print('bundle MB', round(os.path.getsize(OUT + '/village_houses.json') / 1e6, 2))
for n, t in rep.items():
    print('%-16s tris %6d' % (n, t))
print('total', sum(rep.values()), 'parts', [p['name'] for p in parts])
