import sys, os
sys.path.insert(0, '/shared/river/assets/blender')
from vl_arch import *
name = os.environ.get('VL', 'farmer')
cfg = ARCH[name]
c, objs = build(cfg, cfg['garments'])
H = c.H
zw = c.z['waist']
hr = c.arms[-1]['W']
hl = c.arms[1]['W']
views = [((0.55, -0.9, zw), (0, 0, zw), 85), ((-0.5, -0.5, zw + 0.1), (0, 0, zw), 80),
         ((hr.x - 0.35, hr.y - 0.45, hr.z + 0.05), (hr.x, hr.y, hr.z), 70), ((hl.x + 0.35, hl.y - 0.45, hl.z + 0.05), (hl.x, hl.y, hl.z), 70),
         ((0.6, -0.6, 0.15), (0, 0, 0.1), 70), ((0.0, -0.9, 1.25 * H / 1.75), (0, 0, 1.25 * H / 1.75), 70)]
vl_grid('/shared/river/assets/preview/vl_%s_detail.png' % name, views, res=(480, 480), samples=20, cols=3, tag='d' + name)
