import sys; sys.path.insert(0,'/shared/river/assets/blender')
from bl_common import *
reset_scene()
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0,0,0.5)); a=bpy.context.object; a.name='ball'; a.data.materials.append(make_mat('red','#cc3322'))
bpy.ops.mesh.primitive_cube_add(size=0.3, location=(0.6,0,0.15)); b=bpy.context.object; b.name='box'; b.data.materials.append(make_mat('blue','#2244cc')); set_parent(b,a)
shade_smooth(a)
print(export_bundle(OUT_DIR+'/_selftest.json',[a,b]))
render_preview(PREVIEW_DIR+'/_selftest.png',[a,b],(3,-3,1.6),res=(480,320),samples=8)
