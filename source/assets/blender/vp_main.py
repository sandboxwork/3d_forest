"""Driver: blender -b --python vp_main.py -- [names=a,b | all] [noao] [nopreview] [export] [res=560]
Builds village props (modules vp_p*.py register via @prop), bakes AO per prop, optionally exports the bundle and renders previews."""
import sys, os, json, time, importlib
sys.path.insert(0, '/shared/river/assets/blender')
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
from vp_lib import *
import vp_lib
MODS = ['vp_p1', 'vp_p2', 'vp_p2b', 'vp_p3', 'vp_p3b', 'vp_p4', 'vp_p5']
names = None
for a in argv:
    if a.startswith('names='):
        names = a[6:].split(',')
DO_AO = 'noao' not in argv
DO_PREV = 'nopreview' not in argv
DO_EXPORT = 'export' in argv
res_w = 560
for a in argv:
    if a.startswith('res='):
        res_w = int(a[4:])
reset_scene()
init_vp_mats()
for m in MODS:
    if os.path.exists('/shared/river/assets/blender/%s.py' % m):
        try:
            importlib.import_module(m)
        except Exception as ex:
            print('IMPORT FAIL', m, repr(ex))
todo = [n for n in REG if (names is None or n in names)]
t0 = time.time()
built = {}
allobjs = []
for n in todo:
    objs, meta, spec = build_prop(n, ao=DO_AO)
    built[n] = (objs, meta, spec)
    allobjs += objs
    for o in objs:
        o.hide_render = True
    meta['tris'] = tri_total(objs)
    print('   per-obj', [(o.name, tri_total([o])) for o in objs])
    print('BUILT %-18s tris %6d  parts %s  size %.2f x %.2f x %.2f  %.0fs' % (n, meta['tris'], [o.name for o in objs], meta['w'], meta['d'], meta['h'], time.time() - t0))
if DO_EXPORT:
    for o in allobjs:
        o.hide_render = False
    mp = {n: m for n, (o, m, s) in built.items()}
    r = export_bundle(OUT_DIR + '/village_props.json', allobjs, meta={'name': 'village_props', 'frame': 'part-local, three x=bx y=bz z=-by'})
    print('EXPORT', r)
    meta_out = {'name': 'village_props', 'frame': 'three.js part-local (x=bx, y=bz, z=-by); origin on ground at prop centre',
                'parts': {}, 'stats': r}
    for n, (objs, meta, spec) in built.items():
        e = {'w': meta['w'], 'd': meta['d'], 'h': meta['h'], 'colliders': meta['colliders'], 'ko': meta['ko'], 'kind': meta['kind'],
             'tris': meta['tris'], 'subparts': [o.name for o in objs[1:]]}
        if 'light' in meta:
            e['light'] = meta['light']
        meta_out['parts'][n] = e
    with open(OUT_DIR + '/village_props.meta.json', 'w') as f:
        json.dump(meta_out, f, indent=1, ensure_ascii=False)
if DO_PREV:
    preview_wire(allobjs)
    for n, (objs, meta, spec) in built.items():
        views = default_views(meta, spec)
        preview_render(PREVIEW_DIR + '/vp_%s.png' % n, objs, allobjs, views, res=(res_w, int(res_w * 0.75)))
        print('PREVIEW', n, round(time.time() - t0))
print('done', round(time.time() - t0))
