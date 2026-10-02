"""Preview renders of the full living zone inside a stand-in room (NOT exported).
blender -b --python lv_prev.py -- [--nosim] [--ao] [--hq] <res> view1 view2 ..."""
import sys, time
sys.path.insert(0, '/shared/river/assets/blender')
argv = sys.argv[sys.argv.index('--') + 1:]
import lv_build
from lv_build import *
from lv_room import *
from lv_prev_views import VIEWS
res = int(argv[0]) if argv and argv[0].isdigit() else 960
names = [a for a in argv if a in VIEWS]
objs = main()
room = build_room()
for o in room:
    if '--top' in argv and o.name in ('_ce', '_bm'):
        o.hide_render = True
    if 'top' in names and o.name in ('_ce', '_bm'):
        o.hide_render = True
setup_lights([(l['pos'][0], -l['pos'][2], l['pos'][1], 12) for l in LIGHTS])
if '--ao' in argv:
    st = bake_ao([o for o in objs if o.name.startswith('static_') and not any(k in o.name for k in ('glass', 'lv_painting', 'fur', 'contact_shadow'))], samples=48)
    print('AO baked', st[:6])
preview_mats(objs + room)
samples = 64 if '--hq' in argv else 28
for n in names:
    c, t, lens = VIEWS[n]
    render('/shared/river/assets/preview/lv_%s.png' % n, c, t, lens=lens, res=(res, int(res * 2 / 3)), samples=samples)
print('DONE', time.time() - T0)
