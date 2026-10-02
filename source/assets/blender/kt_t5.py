import sys
sys.path.insert(0,'/shared/river/assets/blender')
from kt_lib import *
from kt_mats import init_mats
import kt_lib, kt_dining
reset_scene(); init_mats()
def vol(fs):
    v=0
    for f in fs:
        vs=[x.co for x in f.verts]
        for i in range(1,len(vs)-1): v+=vs[0].dot(vs[i].cross(vs[i+1]))/6
    return v
for rot in (0,180,90):
    kt_lib.ACC.clear()
    f=Fr((0,0,F),rot)
    f.cyl('wood_dark',(0.2,0.17,0.4),0.004,0.003,axis='x',seg=6,col=(0.5,0.38,0.28))
    bm=kt_lib.ACC['wood_dark'][0]
    print('rot',rot,'faces',len(bm.faces),'vol',round(vol(bm.faces)*1e12,3), 'det', round(f.M.determinant(),3))
    for fc in list(bm.faces)[:3]:
        print('  n', tuple(round(x,2) for x in fc.normal), 'c', tuple(round(x,3) for x in fc.calc_center_median()))
