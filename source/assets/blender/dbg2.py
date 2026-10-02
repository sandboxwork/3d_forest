import sys; sys.path.insert(0,'/shared/river/assets/blender')
from int_scene import *
reset_scene(); init_mats()
mirror_oval((1.67, 0.95, 1.95), -90)
objs=finalize()
for o in objs:
    if o.name=='static_mirror':
        me=o.data
        ca=me.color_attributes['Col']
        print(ca.domain, [tuple(round(x,2) for x in ca.data[i].color) for i in range(3)])
        xs=[v.co for v in me.vertices]
        print(min(v.x for v in xs),max(v.x for v in xs),min(v.y for v in xs),max(v.y for v in xs),min(v.z for v in xs),max(v.z for v in xs))
        print(me.uv_layers[0].data[0].uv[:], len(me.polygons))
