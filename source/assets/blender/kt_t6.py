import sys
sys.path.insert(0,'/shared/river/assets/blender')
from kt_lib import *
from kt_mats import init_mats
from kt_room import *
import kt_lib, kt_decals
reset_scene(); init_mats()
kt_decals.init_decal_mats()
for i,L in enumerate((1,2,3,4,5,6)):
    kt_decals.soft_shadow(-5+i*1.0, 0, 0.4, 0.3, spread=0.2, layers=L)
objs=finalize()
bpy.ops.mesh.primitive_plane_add(size=20,location=(0,0,F))
g=bpy.context.object; g.data.materials.append(make_mat('_g','#c8a070',rough=0.7))
preview_mats(objs)
w=bpy.data.worlds.new('W'); bpy.context.scene.world=w; w.use_nodes=True
w.node_tree.nodes['Background'].inputs[1].default_value=1.0
render('/tmp/claude-1001/-shared-river/130188aa-f801-4c92-8245-c0871f14c147/scratchpad/t6.png',(-2.5,0,5),(-2.5,0,0.3),lens=24,res=(480,320),samples=12)
