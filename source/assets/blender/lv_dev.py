"""dev harness: blender -b --python lv_dev.py -- <group> <res> name:cx,cy,cz,tx,ty,tz,lens ... [--noroom] [--hq]"""
import sys, time
sys.path.insert(0, '/shared/river/assets/blender')
argv = sys.argv[sys.argv.index('--') + 1:]
from lv_mats import *
from lv_room import *
import lv_items, lv_seat, lv_tables, lv_books
t0 = time.time()
reset_scene()
init_mats()
grp = argv[0]
resx = int(argv[1])
views = [a for a in argv[2:] if ':' in a]
room = '--noroom' not in argv
samples = 64 if '--hq' in argv else 28
exec(open('/shared/river/assets/blender/lv_dev_groups.py').read())
print('build', time.time() - t0)
objs = finalize() + PARTS
for o in objs:
    for p in o.data.polygons:
        p.use_smooth = True
if room:
    build_room()
else:
    g = make_mat('_g', '#a89070', rough=0.7)
    _box('_gr', (0, 0, F - 0.05), (12, 12, 0.1), g)
preview_mats(objs + STAND)
setup_lights([(l['pos'][0], -l['pos'][2], l['pos'][1], 12) for l in LIGHTS])
for v in views:
    nm, rest = v.split(':')
    c = [float(x) for x in rest.split(',')]
    render('/shared/river/assets/preview/lvd_%s_%s.png' % (grp, nm), c[:3], c[3:6], lens=c[6] if len(c) > 6 else 30, res=(resx, int(resx * 2 / 3)), samples=samples)
print('polys', sum(len(o.data.polygons) for o in objs), 'time', time.time() - t0)
