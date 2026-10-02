"""Verification renders FROM THE EXPORTED BUNDLE (house_int_living.json): decode meshes, rebuild in Blender, render in a stand-in room.
blender -b --python lv_verify.py -- <res> view...   (views from lv_prev.VIEWS)"""
import sys, json, base64, time, os
sys.path.insert(0, '/shared/river/assets/blender')
import bpy, bmesh, numpy as np, math
from mathutils import Vector, Matrix
from bl_common import reset_scene, make_mat, hex_rgb
import lv_room
from lv_room import build_room, setup_lights, render, preview_mats, TEXDIR
argv = sys.argv[sys.argv.index('--') + 1:]
from lv_prev_views import VIEWS
res = int(argv[0]) if argv and argv[0].isdigit() else 900
names = [a for a in argv if a in VIEWS]
T0 = time.time()
reset_scene()
data = json.load(open('/shared/river/assets/out/house_int_living.json'))
meta = json.load(open('/shared/river/assets/out/house_int_living.meta.json'))
mats = {}
for k, m in data['mats'].items():
    mt = make_mat(k, list(m['color']), rough=m['rough'], metal=m['metal'], alpha=m['alpha'], tex=m['tex'], uvscale=m['uvscale'], double=m['double'],
                  emit=m.get('emit'), emit_strength=m.get('emitStrength', 0.0))
    mats[k] = mt


def dec(s, dtype):
    return np.frombuffer(base64.b64decode(s), dtype=dtype)


objs = []
tri_total = 0
for part in data['parts']:
    px, py, pz = part['pivot']              # three coords
    loc = Vector((px, -pz, py))             # back to blender
    me = bpy.data.meshes.new(part['name'])
    allv, allf, alluv, allcol, alln, matidx = [], [], [], [], [], []
    off = 0
    for si, sub in enumerate(part['subs']):
        n = sub['n']
        pos = dec(sub['pos'], np.float32).reshape(n, 3)
        nrm = dec(sub['nrm'], np.float32).reshape(n, 3)
        uv = dec(sub['uv'], np.float32).reshape(n, 2)
        idx = dec(sub['idx'], np.uint16 if sub['idx16'] else np.uint32).reshape(-1, 3)
        col = dec(sub['col'], np.float32).reshape(n, 3) if sub.get('col') else np.ones((n, 3), np.float32)
        # three (x,y,z) -> blender (x,-z,y)
        bpos = np.stack([pos[:, 0], -pos[:, 2], pos[:, 1]], 1)
        bn = np.stack([nrm[:, 0], -nrm[:, 2], nrm[:, 1]], 1)
        allv.append(bpos); alln.append(bn); alluv.append(uv); allcol.append(col)
        allf.append(idx + off); matidx += [si] * len(idx)
        off += n
        tri_total += len(idx)
    V = np.concatenate(allv); Fc = np.concatenate(allf)
    me.vertices.add(len(V)); me.vertices.foreach_set('co', V.ravel())
    me.loops.add(len(Fc) * 3); me.polygons.add(len(Fc))
    me.loops.foreach_set('vertex_index', Fc.ravel())
    me.polygons.foreach_set('loop_start', np.arange(len(Fc), dtype=np.int32) * 3)
    me.polygons.foreach_set('loop_total', np.full(len(Fc), 3, np.int32))
    me.polygons.foreach_set('material_index', np.array(matidx, np.int32))
    me.update(calc_edges=True)
    uvs = np.concatenate(alluv)
    ul = me.uv_layers.new(name='UVMap')
    ul.data.foreach_set('uv', uvs[Fc.ravel()].ravel())
    cols = np.concatenate(allcol)
    ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'CORNER')
    cc = np.ones((len(Fc) * 3, 4), np.float32); cc[:, :3] = cols[Fc.ravel()]
    ca.data.foreach_set('color', cc.ravel())
    try:
        me.normals_split_custom_set_from_vertices([tuple(x) for x in np.concatenate(alln)])
    except Exception as e:
        print('normals', e)
    ob = bpy.data.objects.new(part['name'], me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    for sub in part['subs']:
        ob.data.materials.append(mats[sub['mat']])
    for p in me.polygons:
        p.use_smooth = True
    objs.append(ob)
print('loaded', len(objs), 'objects', tri_total, 'tris', time.time() - T0)
room = build_room()
for o in room:
    if 'top' in names and o.name in ('_ce', '_bm'):
        o.hide_render = True
lp = [(l['pos'][0], -l['pos'][2], l['pos'][1], 12) for l in meta['lights']]
setup_lights(lp)
preview_mats(objs + room)
samples = 64 if '--hq' in argv else 28
for n in names:
    c, t, lens = VIEWS[n]
    render('/shared/river/assets/preview/lvx_%s.png' % n, c, t, lens=lens, res=(res, int(res * 2 / 3)), samples=samples)
print('DONE', time.time() - T0)
