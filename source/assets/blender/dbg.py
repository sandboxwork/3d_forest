import sys; sys.path.insert(0,'/shared/river/assets/blender')
from int_scene import *
from int_room import *
reset_scene(); init_mats()
mirror_oval((1.67, 0.95, 1.95), -90)
objs=finalize()
for o in objs:
    me=o.data
    print(o.name, len(me.polygons), [ (round(p.normal.x,2),round(p.normal.y,2),round(p.normal.z,2)) for p in me.polygons[:3]] if o.name=='static_mirror' else '')
print([ (m.name, m.get('rgb')) for m in bpy.data.materials if m.name=='mirror'])
objs=objs+PARTS
room=build_room(); preview_mats(objs+room)
for m in bpy.data.materials: m.use_backface_culling=False
setup_lights([(2.5,0.95,1.9,200)])
render('/shared/river/assets/preview/dbg.png',(2.8,0.95,1.95),(1.67,0.95,1.95),lens=35,res=(500,400),samples=16)
