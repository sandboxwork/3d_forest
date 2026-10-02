"""Driver. Usage:
  blender -b --python bd_main.py -- build            # full build + AO bake + export
  blender -b --python bd_main.py -- prev <view> [W] [parts]   # preview render (parts: comma list or 'all')
"""
import sys, time, importlib
sys.path.insert(0, '/shared/river/assets/blender')
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
from bd_lib import *
import bd_lib
from bd_mats import init_mats, PREV
import bd_room

t0 = time.time()

VIEWS = {
    # name: (cam, target, lens)  -- all cameras stand in free floor space, eye ~1.65 m, 24 mm lens unless close-up
    'bedA': ((1.9, -0.3, 1.65), (3.4, 2.4, 0.9), 24),
    'bedB': ((3.0, -0.2, 1.65), (3.0, 2.6, 0.7), 24),
    'bedC': ((4.0, 0.5, 1.65), (2.3, 2.6, 0.8), 24),
    'bedD': ((1.95, 1.8, 1.65), (3.6, 2.3, 0.8), 24),
    'bedclose': ((3.0, 0.1, 1.5), (3.0, 1.9, 0.55), 30),
    'bedhead': ((3.0, 0.7, 1.9), (3.0, 3.0, 1.2), 28),
    'bedtop': ((3.0, 2.2, 3.0), (3.0, 2.2, 0.5), 28),
    'ward': ((3.0, -1.5, 1.65), (1.75, -2.35, 1.1), 24),
    'wardclose': ((3.0, -2.0, 1.4), (1.8, -2.35, 1.05), 32),
    'dress': ((3.2, -0.1, 1.6), (1.75, 0.95, 1.0), 24),
    'dressclose': ((2.9, 0.95, 1.45), (1.75, 0.95, 1.05), 32),
    'desk': ((2.4, -1.9, 1.6), (4.1, -0.9, 0.9), 24),
    'deskclose': ((3.2, -0.1, 1.5), (4.0, -0.9, 0.85), 32),
    'deskwin': ((2.9, -1.3, 1.6), (4.2, -0.9, 1.3), 28),
    'entry': ((-0.2, -1.2, 1.65), (0.9, -3.0, 1.0), 24),
    'entry2': ((0.1, -1.9, 1.65), (1.2, -3.1, 0.9), 24),
    'entry3': ((0.7, -1.5, 1.65), (1.3, -2.6, 1.2), 24),
    'entryclose': ((0.35, -2.4, 1.5), (1.1, -3.1, 1.0), 30),
    'rocker': ((2.6, -1.3, 1.5), (3.8, -2.7, 0.8), 28),
    'trunk': ((3.0, -0.4, 1.5), (3.02, 0.66, 0.5), 30),
    'bedroom_e': ((4.05, 2.2, 1.65), (2.0, -0.5, 1.1), 24),
    'bedroom_n': ((2.2, -0.5, 1.7), (3.0, 3.2, 1.3), 24),
    'bedroom_s': ((3.0, 0.4, 1.65), (3.2, -3.2, 1.2), 24),
    'win_fl': ((-2.9, -1.4, 1.6), (-2.9, -3.25, 1.7), 28),
    'win_fr': ((2.9, -1.4, 1.6), (2.9, -3.25, 1.7), 28),
    'win_re': ((3.95, -0.3, 1.6), (4.25, 1.6, 1.8), 28),
    'win_rn': ((3.0, -0.5, 1.6), (4.25, -0.9, 1.8), 28),
    'win_br': ((1.95, 1.8, 1.6), (2.2, 3.25, 1.8), 28),
    'win_bl': ((-2.2, 1.6, 1.6), (-2.2, 3.25, 1.7), 28),
    'living_w': ((-0.3, -0.5, 1.65), (-3.5, 2.5, 1.5), 24),
    'living_e': ((-3.8, -0.5, 1.65), (0.3, -3.2, 1.5), 24),
    'top': ((1.5, 0.0, 9.0), (1.5, 0.01, 0.0), 30),
    'topb': ((2.9, 0.4, 6.0), (2.9, 0.41, 0.0), 30),
    'door': ((0.0, -1.0, 1.65), (0.0, -3.2, 1.2), 24),
    'washst': ((3.0, -1.8, 1.5), (2.85, -3.0, 1.0), 28),
    'plants': ((2.3, 0.1, 1.65), (4.1, 1.3, 1.4), 24),
    'lamp': ((1.95, 2.0, 1.4), (1.96, 3.03, 1.1), 36),
    'ceil': ((3.0, 0.2, 1.7), (3.0, 1.8, 3.0), 24),
    'shelf': ((3.2, -1.7, 1.6), (4.25, -1.95, 1.7), 30),
    'pic': ((3.0, 0.6, 1.9), (3.35, 3.25, 2.4), 30),
    'slip': ((2.5, 0.75, 1.1), (2.1, 1.35, 0.3), 40),
    'tray': ((0.55, -1.75, 1.2), (1.2, -2.4, 0.4), 36),
    'pothos': ((3.5, -0.5, 1.9), (2.75, -1.55, 2.0), 32),
    'fernv': ((3.5, 0.55, 1.2), (4.0, 1.62, 0.95), 30),
    'sill': ((2.9, -2.3, 1.7), (2.9, -3.25, 1.5), 40),
    'hats': ((0.45, -1.9, 1.9), (0.98, -3.0, 1.75), 36),
    'robe': ((2.7, -0.2, 1.6), (1.65, -1.3, 1.1), 30),
    'pic2': ((3.35, 2.1, 2.5), (3.35, 3.25, 2.55), 50),
    'pic3': ((3.6, -1.9, 1.9), (3.95, -3.25, 2.0), 40),
    'pegs': ((2.5, -0.4, 1.7), (1.65, -1.3, 1.4), 28),
    'ward_open': ((3.2, -2.6, 1.5), (1.9, -2.2, 1.2), 30),
}


def build_scene(parts):
    reset_scene()
    init_mats()
    bd_lib.ACC.clear(); bd_lib.LIGHTS.clear(); bd_lib.COLL.clear(); bd_lib.INTER.clear(); bd_lib.PARTS.clear()
    import bd_scene
    importlib.reload(bd_scene)
    bd_scene.build_all(parts)
    return bd_scene


AO_SUB = {'wood_pine': 0.12, 'wood_oak': 0.12, 'wood_dark': 0.12, 'paint': 0.12, 'plaster': 0.2, 'rug': 0.15, 'ceramic': 0.1, 'stone': 0.15, 'leather': 0.15, 'wicker': 0.15, 'linen': 0.14, 'wool': 0.14, **{'bd_painting_%d' % i: 0.07 for i in range(1, 10)}}


def finish_objs(subdiv=None):
    if subdiv is None:
        k = float(os.environ.get('SUBDIV', 1.0))
        subdiv = {a: b * k for a, b in AO_SUB.items()} if k > 0 else None
    statics = finalize(subdiv=subdiv)
    for o in statics + bd_lib.PARTS:
        for p in o.data.polygons:
            p.use_smooth = True
    return statics + bd_lib.PARTS


if argv and argv[0] == 'prev':
    view = argv[1]
    res_w = int(argv[2]) if len(argv) > 2 else 960
    parts = argv[3].split(',') if len(argv) > 3 and argv[3] != 'all' else None
    ao = ('ao' in argv)
    sc = build_scene(parts)
    objs = finish_objs()
    room = bd_room.build_room()
    if ao:
        bd_room.bake_ao(objs, samples=24)
    bd_room.preview_mats(objs)
    lamps = [(l['pos'][0], -l['pos'][2], l['pos'][1], 10) for l in bd_lib.LIGHTS]
    bd_room.setup_lights(lamps)
    cam, tgt, lens = VIEWS[view]
    out = '/shared/river/assets/preview/bd_%s.png' % view
    if 'tmp' in argv:
        out = '/tmp/claude-1001/-shared-river/130188aa-f801-4c92-8245-c0871f14c147/scratchpad/bd_%s.png' % view
    for o in room:
        if view in ('top', 'topb') and o.name in ('_ce', '_bm'):
            o.hide_render = True
    bd_room.render(out, cam, tgt, lens=lens, res=(res_w, int(res_w * 2 / 3)), samples=int(os.environ.get('SAMPLES', 32)))
    tris = sum(len(o.data.polygons) for o in objs)
    print('preview', out, 'time', time.time() - t0)

elif argv and argv[0] == 'prevm':
    views = argv[1].split(',')
    res_w = int(argv[2]) if len(argv) > 2 else 960
    parts = argv[3].split(',') if len(argv) > 3 and argv[3] != 'all' else None
    ao = ('ao' in argv)
    sc = build_scene(parts)
    objs = finish_objs()
    room = bd_room.build_room()
    if ao:
        stat = [o for o in objs if o.name.startswith('static_')] + [o for o in objs if o.name.startswith('curtain_')]
        bd_room.bake_ao(stat, samples=int(os.environ.get('AOS', 32)))
    bd_room.preview_mats(objs)
    lamps = [(l['pos'][0], -l['pos'][2], l['pos'][1], 10) for l in bd_lib.LIGHTS]
    bd_room.setup_lights(lamps)
    for view in views:
        cam, tgt, lens = VIEWS[view]
        out = '/shared/river/assets/preview/bd_%s.png' % view
        if 'tmp' in argv:
            out = '/tmp/claude-1001/-shared-river/130188aa-f801-4c92-8245-c0871f14c147/scratchpad/bd_%s.png' % view
        for o in room:
            o.hide_render = bool(view in ('top', 'topb') and o.name in ('_ce', '_bm'))
        for c_ in [o for o in bpy.data.objects if o.type == 'CAMERA']:
            bpy.data.objects.remove(c_)
        bd_room.render(out, cam, tgt, lens=lens, res=(res_w, int(res_w * 2 / 3)), samples=int(os.environ.get('SAMPLES', 32)))
        print('RENDERED', out, time.time() - t0)
        if 'bf' in argv:
            bd_room.backface_check(view, cam, tgt, lens, (480, 320))
        try:
            im_ = bpy.data.images.load(out, check_existing=False)
            a_ = np.array(im_.pixels[:], np.float32).reshape(-1, 4)
            mg = float(((a_[:, 0] > 0.7) & (a_[:, 2] > 0.7) & (a_[:, 1] < 0.35)).mean())
            print('MAGENTA', view, round(mg * 100, 4), '%')
            bpy.data.images.remove(im_)
        except Exception as e_:
            print('mag err', e_)

elif argv and argv[0] == 'dry':
    parts = argv[1].split(',') if len(argv) > 1 and argv[1] != 'all' else None
    sc = build_scene(parts)
    objs = finish_objs()
    import bd_scene
    for o in objs:
        print('OBJ', o.name, bd_scene.tri_count([o]))
    print('TRIS', bd_scene.tri_count(objs), 'time', time.time() - t0)
    for k, v in sorted(bd_lib.PROF.items(), key=lambda t: -t[1])[:45]:
        print('PROF', k, v)

elif argv and argv[0] == 'build':
    sc = build_scene(None)
    objs = finish_objs()
    import bd_scene
    bd_scene.final_export(objs, bd_room)
    print('built', time.time() - t0)
