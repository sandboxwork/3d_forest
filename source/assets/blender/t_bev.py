import sys
sys.path.insert(0,'/shared/river/assets/blender')
from hs_build import *
import hs_lib
window(FRONT,0.0,2.05,1.0,1.25)
S=hs_lib.CUR
import bpy
for bw in (0.004,):
    o=make_part('t',{'trim_paint':S['trim_paint']},['trim_paint'],bevel=bw)
    # count faces with normal pointing toward mesh centroid locally? just report
    me=o.data
    me.calc_loop_triangles()
    print(len(me.polygons))
    # check for tiny faces
    small=[p for p in me.polygons if p.area<1e-6]
    print('small faces',len(small))
    # check normals consistency: faces whose normal.dot(center - bbox center)<0 among "outer" ones not reliable
    import bmesh
    bm=bmesh.new(); bm.from_mesh(me)
    bad=0
    for f in bm.faces:
        if len(f.verts)==3 and f.calc_area()<2e-5: bad+=1
    print('tiny tri',bad)
