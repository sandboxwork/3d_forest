import sys, os
sys.path.insert(0, '/shared/river/assets/blender')
from vl_arch import *
name = os.environ.get('VL', 'man')
cfg = ARCH[name]
c, objs = build(cfg, cfg['garments'])
print('TRIS', name, tris(objs), {k: tri_count([o]) for k, o in objs.items()})
preview(c, objs, '/shared/river/assets/preview/vl_%s.png' % name, name)
