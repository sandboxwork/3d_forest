import sys, time
sys.path.insert(0,'/shared/river/assets/blender')
from kt_lib import *
from kt_mats import init_mats
from kt_ware import *
from kt_room import *
t0=time.time()
reset_scene(); init_mats()
z=0
plate((0,0,z),r=0.12,rim='blue')
plate((0.3,0,z),r=0.12,glaze='cream',rim='green',stack=3)
bowl((0.0,0.3,z),r=0.08,h=0.05,glaze='blue',contents=('soup',(0.7,0.4,0.15)))
bowl((0.25,0.3,z),r=0.08,h=0.05,glaze='cream',rim='cobalt',contents=('heap',(0.8,0.7,0.5)))
mug((0.5,0.3,z),glaze='red',rim='cream')
cup_saucer((0.6,0,z),fill=(0.3,0.15,0.05))
goblet((-0.2,0,z),fill='water'); goblet((-0.3,0,z),kind='wine',fill=(0.4,0.05,0.1),r=0.035,h=0.15)
jug((-0.3,0.3,z))
teapot((-0.1,0.5,z))
fork((0.2,-0.2,z),rot=0); knife((0.27,-0.2,z),rot=0); spoon((0.34,-0.2,z),rot=0)
candlestick((0.8,0.3,z))
lantern((-0.6,0.3,z),chain_to=0.8)
print('tris',tri_count(), time.time()-t0)
objs=finalize()
for o in objs:
    for p in o.data.polygons: p.use_smooth=True
room=[]
bpy.ops.mesh.primitive_plane_add(size=6,location=(0,0,-0.001)); g=bpy.context.object
gm=make_mat('_g','#8a6a4a',rough=0.7); g.data.materials.append(gm)
preview_mats(objs)
w=bpy.data.worlds.new('W'); bpy.context.scene.world=w; w.use_nodes=True
w.node_tree.nodes['Background'].inputs[1].default_value=1.0
d=bpy.data.lights.new('sun','SUN'); d.energy=3; o=bpy.data.objects.new('sun',d); o.rotation_euler=(0.8,0.2,0.6); bpy.context.scene.collection.objects.link(o)
import os
cams={'a':((0.1,-0.75,0.75),(0.1,0.15,0.08)),'b':((0.3,-0.55,0.3),(0.3,-0.2,0.0)),'c':((0.2,0.0,0.55),(0.75,0.3,0.12)),'d':((-0.2,-0.4,0.6),(-0.6,0.3,0.4))}
k=os.environ.get('CAM','a'); c=cams[k]
render('/tmp/claude-1001/-shared-river/130188aa-f801-4c92-8245-c0871f14c147/scratchpad/t1%s.png'%k,c[0],c[1],lens=40,res=(1000,640),samples=36)
print('done',time.time()-t0)
