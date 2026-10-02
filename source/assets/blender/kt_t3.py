import sys
sys.path.insert(0,'/shared/river/assets/blender')
from kt_lib import *
from kt_mats import init_mats
from kt_food import *
reset_scene(); init_mats()
for dist in (0.071,0.09):
    surf = bmesh.new()
    bmesh.ops.create_grid(surf, x_segments=1, y_segments=1, size=1.0)
    for v in surf.verts:
        v.co.x *= 0.43; v.co.y *= 0.29
    print([tuple(v.co) for v in surf.verts])
    vars_=[{'parts':[(apple_bm(j,r=0.034,seg=7),'food_vc')]} for j in range(3)]
    fa=len(vars_[0]['parts'][0][0].faces)
    outs=gn_scatter(surf,vars_,distance=dist,density=900,seed=7,scale=(0.92,1.08),tilt=0.28,tint=0.1)
    nf=sum(len(b.faces) for b in outs.values()); print('dist',dist,'faces',nf,'apples ~',nf/fa)
