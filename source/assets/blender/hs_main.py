import sys
sys.path.insert(0, '/shared/river/assets/blender')
from hs_build import *
import hs_build, hs_lib, json, os

STEPS = os.environ.get('HS_STEPS', 'all')

def run(name):
    f = getattr(hs_build, name, None)
    if f is None:
        print('MISSING', name); return
    f()

order = ['foundation', 'walls', 'roof', 'chimney', 'interior', 'fireplace', 'ceiling', 'windows_all', 'doors_all', 'porch',
         'exterior_details', 'outbuildings']
for n in order:
    if STEPS == 'all' or n in STEPS.split(','):
        run(n)

STATIC = hs_lib.CUR
objs = []
# glass part
with part() as GD:
    for g in GLASS_OPS:
        g()
if GD:
    objs.append(make_part('glass', GD, ['glass']))
for mn in MATNAMES:
    if mn in STATIC and mn != 'glass':
        objs.append(make_part('static_' + mn, {mn: STATIC[mn]}, [mn], bevel=(None if os.environ.get('HS_NOBEV') else (BEV.get(mn, 0.0) or None))))
for extra in hs_build.EXTRA_OBJS:
    objs.append(extra)

bpy.ops.wm.save_as_mainfile(filepath='/shared/river/assets/blender/house_shell.blend')
tot = 0
for o in objs:
    n = sum(len(p.vertices) - 2 for p in o.data.polygons)
    tot += n
    print('%-28s tris~%d' % (o.name, n))
print('TOTAL tris~', tot)
if os.environ.get('HS_EXPORT', '1') == '1':
    st = export_bundle(OUT_DIR + '/house_shell.json', objs, meta={'name': 'house_shell'})
    print(st)
