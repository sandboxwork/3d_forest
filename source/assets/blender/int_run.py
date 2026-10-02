import sys, os, time
sys.path.insert(0, '/shared/river/assets/blender')
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
from int_scene import *
from int_decor import decorate
from int_room import *
t0 = time.time()
reset_scene()
build_all()
decorate()
print('build', time.time() - t0)
objs, r = export_all(write=not argv)
print(r, 'lights', len(LIGHTS), 'coll', len(COLL))
VIEWS = {
 'a': ((1.0, -2.7, 2.0), (-3.2, 1.0, 1.2)),
 'b': ((-3.6, -2.7, 2.0), (1.0, 1.2, 1.0)),
 'c': ((0.8, 2.3, 2.0), (-3.2, -2.4, 1.1)),
 'd': ((-1.2, 0.2, 2.0), (-1.5, 3.2, 1.4)),
 'e': ((2.6, -2.9, 2.0), (3.6, 2.6, 1.0)),
 'f': ((3.8, 2.6, 2.0), (2.0, -2.2, 1.0)),
 'g': ((3.0, -0.3, 2.0), (1.7, 0.3, 1.4)),
 'h': ((0.3, 0.0, 2.0), (-4.2, 0.0, 1.3)),
 'i': ((-3.8, 2.8, 2.0), (1.0, -1.5, 1.0)),
 'j': ((1.0, 1.0, 2.0), (4.2, -0.5, 1.0)),
 'k': ((-1.0, -1.2, 1.7), (-3.1, -2.6, 1.0)),
 'l': ((-2.0, -0.3, 1.5), (-4.0, -0.2, 0.9)),
 'm': ((-2.4, -1.5, 1.3), (-4.0, -0.3, 0.85)),
 'n': ((-2.4, 1.5, 1.6), (-4.0, 0.8, 1.3)),
 'top': ((0.0, 0.0, 9.0), (0.0, 0.01, 0.0)),
}
if argv:
    room = build_room()
    if argv[0] == 'top':
        for o in room:
            if o.name == '_ce' or o.name == '_bm':
                o.hide_render = True
    preview_mats(objs + room)
    lightpts = [(l['pos'][0], -l['pos'][2], l['pos'][1], 12) for l in LIGHTS]
    setup_lights(lightpts)
    cam, tgt = VIEWS[argv[0]]
    lens = 24 if argv[0] != 'top' else 30
    res = (960, 640) if len(argv) < 2 else (int(argv[1]), int(int(argv[1]) * 2 / 3))
    render('/shared/river/assets/preview/int_%s.png' % argv[0], cam, tgt, lens=lens, res=res, samples=32)
print('done', time.time() - t0)
