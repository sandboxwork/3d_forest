"""Add '<part>_lod1' decimated parts to a bundle JSON that lacks them.
   blender -b --python lodify.py -- <bundle> [ratio]   (reads/writes /shared/river/assets/out/<bundle>.json)"""
import sys, json, base64
sys.path.insert(0, '/shared/river/assets/blender')
from bl_common import *
argv = sys.argv[sys.argv.index('--') + 1:]
name = argv[0]; ratio = float(argv[1]) if len(argv) > 1 else 0.3; SUF = argv[2] if len(argv) > 2 else '_lod1'; MINT = float(argv[3]) if len(argv) > 3 else 260.0
SRC = '_lod1'
path = OUT_DIR + '/' + name + '.json'
B = json.load(open(path))
have = {p['name'] for p in B['parts']}
reset_scene()
mats = {}
def get_mat(n):
    if n in mats: return mats[n]
    d = B['mats'][n]
    m = make_mat(n, d['color'], rough=d['rough'], metal=d['metal'], alpha=d['alpha'], tex=d.get('tex') or None, uvscale=d.get('uvscale', 1.0), double=d.get('double', False),
                 emit=d.get('emit'), emit_strength=d.get('emitStrength', 0.0))
    mats[n] = m; return m
def arr(s, dt): return np.frombuffer(base64.b64decode(s), dtype=dt)
objs = []; added = 0
for part in B['parts']:
    nm = part['name']
    if nm.endswith('_lod1') or nm.endswith('_lod2') or (nm + SUF) in have: continue
    tris_total = sum(s['tris'] for s in part['subs'])
    if tris_total < 500: continue
    bm_parts = []
    ob = None
    me = bpy.data.meshes.new(nm + SUF)
    verts, faces, uvs, cols, matidx = [], [], [], [], []
    off = 0; slots = []
    for si, s in enumerate(part['subs']):
        pos = arr(s['pos'], np.float32).reshape(-1, 3); uv = arr(s['uv'], np.float32).reshape(-1, 2)
        idx = arr(s['idx'], np.uint16 if s.get('idx16') else np.uint32).reshape(-1, 3)
        col = arr(s['col'], np.float32).reshape(-1, 3) if s.get('col') else np.ones((len(pos), 3), np.float32)
        b = np.stack([pos[:, 0], -pos[:, 2], pos[:, 1]], 1)       # three -> blender
        verts.append(b); uvs.append(uv); cols.append(col); faces.append(idx + off); matidx += [si] * len(idx); off += len(pos); slots.append(s['mat'])
    V = np.concatenate(verts); F = np.concatenate(faces); UV = np.concatenate(uvs); C = np.concatenate(cols)
    me.from_pydata(V.tolist(), [], F.tolist()); me.update()
    uvl = me.uv_layers.new(name='UV'); loop_v = np.empty(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', loop_v)
    uvl.data.foreach_set('uv', UV[loop_v].ravel())
    ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT'); rgba = np.concatenate([C, np.ones((len(C), 1), np.float32)], 1); ca.data.foreach_set('color', rgba.ravel())
    me.polygons.foreach_set('material_index', np.array(matidx, np.int32)); me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=2e-4); bm.to_mesh(me); bm.free()
    for p_ in me.polygons: p_.use_smooth = True
    ob = bpy.data.objects.new(nm + SUF, me); bpy.context.scene.collection.objects.link(ob)
    for mn in slots: ob.data.materials.append(get_mat(mn))
    r = max(0.02, min(0.9, max(ratio, MINT / max(tris_total, 1))))
    md = ob.modifiers.new('dec', 'DECIMATE'); md.decimate_type = 'COLLAPSE'; md.ratio = r; md.use_collapse_triangulate = True
    ob.location = (0, 0, 0)
    bpy.context.view_layer.objects.active = ob; apply_modifiers(ob)
    ob['pivot'] = part['pivot']; objs.append(ob); added += 1
print('lod parts', added)
tmp = OUT_DIR + '/_lod_tmp.json'
st = export_bundle(tmp, objs)
L = json.load(open(tmp))
piv = {o.name: o['pivot'] for o in objs}
for p in L['parts']:
    p['parent'] = None; p['pivot'] = list(piv.get(p['name'], [0, 0, 0]))
B['parts'] += L['parts']
for k, v in L['mats'].items(): B['mats'].setdefault(k, v)
json.dump(B, open(path, 'w'), separators=(',', ':'))
print(st, 'total parts', len(B['parts']))
