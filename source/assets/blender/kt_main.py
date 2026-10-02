"""Final build: kitchen + dining -> /shared/river/assets/out/house_int_kitchen.json (+ .meta.json)
Run: blender -b --python kt_main.py -- [noao] [views=a,b,c] [res=960]"""
import sys, os, json, time
sys.path.insert(0, '/shared/river/assets/blender')
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
from kt_lib import *
from kt_mats import init_mats
from kt_room import *
from kt_views import VIEWS
import kt_lib, kt_ao
import kt_dining, kt_stove, kt_counter, kt_storage, kt_hang, kt_decals, kt_meta

DO_AO = 'noao' not in argv
WRITE = 'nowrite' not in argv
views = []
res_w = 960
for a in argv:
    if a.startswith('views='):
        views = a[6:].split(',')
    if a.startswith('res='):
        res_w = int(a[4:])
t0 = time.time()
reset_scene()
init_mats()
for m in (kt_dining, kt_stove, kt_counter, kt_storage, kt_hang, kt_decals, kt_meta):
    m.build()
    print('built', m.__name__, tri_count(), round(time.time() - t0, 1))
objs = finalize()
parts = list(kt_lib.PARTS)
for o in objs:
    for p in o.data.polygons:
        p.use_smooth = True
room = build_room()
if DO_AO:
    b, a = kt_ao.prepare(objs)
    print('AO subdivision tris', b, '->', a, round(time.time() - t0, 1))
    for o in parts:
        o.hide_render = True
    st = kt_ao.bake(objs, samples=40)
    print('AO baked', round(time.time() - t0, 1), [(n, round(v, 2)) for n, v in st][:40])
    for o in parts:
        o.hide_render = False
    for o in objs:
        o.hide_render = False
export = objs + parts
meta = {'name': 'house_int_kitchen', 'lights': LIGHTS, 'colliders': COLL, 'interactables': INTER}
if WRITE:
    r = export_bundle(OUT_DIR + '/house_int_kitchen.json', export, meta={'name': 'house_int_kitchen', 'frame': 'house-local, three x=bx y=bz z=-by'})
    print('EXPORT', r)
    meta['stats'] = {'tris': r['tris'], 'parts': r['parts'], 'kb': r['kb']}
    with open(OUT_DIR + '/house_int_kitchen.meta.json', 'w') as fh:
        json.dump(meta, fh, indent=1, ensure_ascii=False)
if views:
    preview_mats(objs + parts + room)
    lightpts = [(l['pos'][0], -l['pos'][2], l['pos'][1], 9) for l in LIGHTS]
    setup_lights(lightpts)
    for vw in views:
        cam, tgt = VIEWS[vw]
        for o in room:
            if o.name.startswith('_ce') or o.name.startswith('_bm'):
                o.hide_render = (vw == 'top')
        render('/shared/river/assets/preview/ktf_%s.png' % vw, cam, tgt, lens=24, res=(res_w, int(res_w * 2 / 3)), samples=40)
        print('rendered', vw, round(time.time() - t0, 1))
print('done', round(time.time() - t0, 1))
