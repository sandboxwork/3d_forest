"""Usage: blender -b --python kt_run.py -- <modules,comma> <view|none> [width] [samples]
modules: dining, stove, counter, storage, hang, props   (or 'all')"""
import sys, os, time, importlib
sys.path.insert(0, '/shared/river/assets/blender')
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
from kt_lib import *
from kt_mats import init_mats
from kt_room import *
import kt_lib

PROF = os.environ.get('PROF')
MODS = (argv[0] if argv else 'dining').split(',')
VIEW = argv[1] if len(argv) > 1 else 'a'
WIDTH = int(argv[2]) if len(argv) > 2 else 960
SAMPLES = int(argv[3]) if len(argv) > 3 else 40

from kt_views import VIEWS

import types
STATS = {}
if PROF:
    _wr = {}
    def _wrap(fn):
        if fn in _wr:
            return _wr[fn]
        def w(*a, **k):
            t = tri_count()
            r = fn(*a, **k)
            d = tri_count() - t
            st = STATS.setdefault(fn.__module__ + '.' + fn.__name__, [0, 0])
            st[0] += 1; st[1] += d
            return r
        w.__name__ = fn.__name__; w.__module__ = fn.__module__
        _wr[fn] = w
        return w
    def _patch():
        mods = [m for n, m in list(sys.modules.items()) if n.startswith('kt_') and n not in ('kt_run',)]
        for m in mods:
            for n, v in list(vars(m).items()):
                if isinstance(v, types.FunctionType) and v.__module__.startswith('kt_') and v.__module__ != 'kt_run' and not n.startswith('_') and n not in ('tri_count', 'tri_report', 'put', 'get_bm', 'C', 'xf', 'rotm'):
                    if v.__module__ in ('kt_lib',) and n in ('box', 'lathe', 'sphere', 'cyl', 'tube', 'sweep', 'torus', 'put_bm', 'bev_bm', 'light', 'collider', 'interact', 'woodcol', 'fab', 'jit', 'shade', 'mixc', 'fbm', 'nz', 'cube_bm', 'cyl_bm', 'sphere_bm', 'modbm', 'disp', 'boolean', 'lathe_bm', 'prof_split', 'array_curve', 'array_radial', 'cloth_sim', 'cloth_grid', 'gn_scatter', 'put_outs', 'metaball_bm', 'subsurf', 'bez', 'arcpts', 'polyline_smooth'):
                        continue
                    setattr(m, n, _wrap(v))
t0 = time.time()
reset_scene()
init_mats()
for m in MODS:
    importlib.import_module('kt_' + m)
if PROF:
    _patch()
for m in MODS:
    mod = importlib.import_module('kt_' + m)
    mod.build()
    print('built', m, 'tris', tri_count(), round(time.time() - t0, 1))
print('TRIS', tri_report())
if PROF:
    for k, (n, d) in sorted(STATS.items(), key=lambda kv: -kv[1][1])[:70]:
        print('PROF %-40s calls %4d tris %7d  avg %6d' % (k, n, d, d // max(n, 1)))
objs = finalize() + kt_lib.PARTS
for o in objs:
    for p in o.data.polygons:
        p.use_smooth = True
if VIEW != 'none':
    room = build_room()
    preview_mats(objs + room)
    lightpts = [(l['pos'][0], -l['pos'][2], l['pos'][1], 9) for l in LIGHTS]
    setup_lights(lightpts)
    for vw in VIEW.split(','):
        cam, tgt = VIEWS[vw]
        lens = 24
        res = (WIDTH, int(WIDTH * 2 / 3))
        out = '/shared/river/assets/preview/kt_%s%s.png' % (vw, os.environ.get('SUF', ''))
        render(out, cam, tgt, lens=lens, res=res, samples=SAMPLES)
        print('rendered', vw, round(time.time() - t0, 1))
print('done', round(time.time() - t0, 1))
