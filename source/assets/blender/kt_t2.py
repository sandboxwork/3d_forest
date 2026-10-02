import sys, time, os
sys.path.insert(0,'/shared/river/assets/blender')
from kt_lib import *
from kt_mats import init_mats
from kt_ware import *
from kt_food import *
from kt_room import *
t0=time.time()
reset_scene(); init_mats()
z=0
loaf((0,0,z),rot=10,seed=1); 
loaf((0.3,0.0,z),rot=-20,seed=2,kind='boule',L=0.2,W=0.2,H=0.1,score=4)
for i in range(3): bread_slice((0.05+0.02*i,0.17,z+0.0),rot=(0,0,10+5*i),seed=i)
cheese_wedge((0.5,0.0,z),rot=20,seed=2)
butter_block((0.5,0.2,z),rot=15)
for i in range(4): place('food_vc',apple_bm(i),(-0.2+0.08*i,0.0,z),rot=(0,0,i*50))
place('food_vc',pear_bm(1),(-0.2,0.1,z)); place('food_vc',egg_bm(),(-0.1,0.1,z))
place('food_vc',onion_bm(1),(-0.0,0.1,z-0.0)); place('food_vc',tomato_bm(1),(0.08,0.1,z))
place('food_vc',potato_bm(2),(-0.3,0.0,z)); place('food_vc',carrot_bm(0.16,seed=1),(-0.3,0.15,z+0.017),rot=(90,0,20)); place('food_vc',garlic_bm(1),(-0.4,0.1,z)); place('food_vc',lemon_bm(1),(-0.45,0.0,z))
flower_bunch((-0.2,0.35,z),0.05,n=9,seed=3)
herb_bundle((0.35,0.4,0.5),L=0.3,kind='lav',seed=2)
herb_bundle((0.55,0.4,0.5),L=0.3,kind='sage',seed=3)
print('tris',tri_count(), time.time()-t0)
objs=finalize()
for o in objs:
    for p in o.data.polygons: p.use_smooth=True
bpy.ops.mesh.primitive_plane_add(size=6,location=(0,0,-0.001)); g=bpy.context.object
g.data.materials.append(make_mat('_g','#8a6a4a',rough=0.7))
preview_mats(objs)
w=bpy.data.worlds.new('W'); bpy.context.scene.world=w; w.use_nodes=True
w.node_tree.nodes['Background'].inputs[1].default_value=1.0
d=bpy.data.lights.new('sun','SUN'); d.energy=3; o=bpy.data.objects.new('sun',d); o.rotation_euler=(0.8,0.2,0.6); bpy.context.scene.collection.objects.link(o)
cams={'a':((0.1,-0.5,0.55),(0.1,0.1,0.03)),'b':((-0.1,0.15,0.35),(-0.2,0.38,0.12)),'c':((0.6,0.0,0.45),(0.45,0.3,0.05))}
k=os.environ.get('CAM','a'); c=cams[k]
render('/tmp/claude-1001/-shared-river/130188aa-f801-4c92-8245-c0871f14c147/scratchpad/t2%s.png'%k,c[0],c[1],lens=40,res=(1000,640),samples=36)
