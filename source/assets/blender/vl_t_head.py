import sys
sys.path.insert(0,'/shared/river/assets/blender')
from vl_lib import *
reset_scene()
mk_mats()
F=default_face()
H=make_head(F)
parts=[]
for k in ('head','jaw','eyes','lids','ears'):
    b=H[k]
    parts.append(finish_part('t_'+k,b,(0,0,0)))
print('tris',tri_count(parts))
vl_grid('/shared/river/assets/preview/vl_t_head.png',[((0,-0.55,0.0),(0,0,0),85),((0.55,0,0.0),(0,0,0),85),((0.4,-0.4,0.05),(0,0,0),85),((0,-0.3,-0.02),(0,0,-0.01),60)],res=(500,500),samples=24,ground=False,tag="h")
