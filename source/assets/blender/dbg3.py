import sys; sys.path.insert(0,'/shared/river/assets/blender')
from int_scene import *
from int_room import *
reset_scene(); init_mats()
mirror_oval((1.67, 0.95, 1.95), -90)
objs=finalize()
preview_mats(objs)
m=bpy.data.materials['mirror']
b=m.node_tree.nodes['Principled BSDF']
for k in ('Base Color','Metallic','Roughness','Alpha','IOR','Specular IOR Level','Transmission Weight','Coat Weight','Emission Strength'):
    i=b.inputs[k]; print(k, i.default_value if not hasattr(i.default_value,'__len__') else tuple(i.default_value), [l.from_node.name for l in i.links])
m2=bpy.data.materials['wood_oak']
print(m.blend_method if hasattr(m,'blend_method') else '', m.surface_render_method)
