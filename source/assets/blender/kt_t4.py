import sys, time, os
sys.path.insert(0,'/shared/river/assets/blender')
from kt_lib import *
from kt_mats import init_mats
from kt_ware import *
from kt_food import *
from kt_room import *
reset_scene(); init_mats()
z=0
loaf((0,0,z),rot=10,seed=1,L=0.28,W=0.12,H=0.09,score=3)
loaf((0.3,0.0,z),rot=-20,seed=2,kind='boule',L=0.2,W=0.2,H=0.1,score=4)
for i in range(3): bread_slice((0.0+0.03*i,0.17,z+0.0),rot=(0,0,10+8*i),seed=i)
jug((-0.3,0.2,z),r=0.062,h=0.19,glaze='blue')
flower_bunch((-0.3,0.2,z+0.175),0.05,n=13,seed=4,spread=0.075,up=0.09)
objs=finalize()
for o in objs:
    for p in o.data.polygons: p.use_smooth=True
bpy.ops.mesh.primitive_plane_add(size=6,location=(0,0,-0.001)); g=bpy.context.object
g.data.materials.append(make_mat('_g','#8a6a4a',rough=0.7))
preview_mats(objs)
w=bpy.data.worlds.new('W'); bpy.context.scene.world=w; w.use_nodes=True
w.node_tree.nodes['Background'].inputs[1].default_value=0.6
d=bpy.data.lights.new('sun','SUN'); d.energy=3; o=bpy.data.objects.new('sun',d); o.rotation_euler=(0.8,0.2,0.6); bpy.context.scene.collection.objects.link(o)
cams={'a':((0.12,-0.42,0.3),(0.12,0.05,0.04)),'b':((-0.3,-0.5,0.45),(-0.3,0.2,0.3))}
for k in ('a','b'):
    c=cams[k]
    render('/tmp/claude-1001/-shared-river/130188aa-f801-4c92-8245-c0871f14c147/scratchpad/t4%s.png'%k,c[0],c[1],lens=45,res=(900,600),samples=32)
