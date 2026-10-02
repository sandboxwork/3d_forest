"""Shared Blender helpers for riverside_forest assets.

Run with:  ~/.cache/motion-video-deps/blender/bin/blender -b --python <script.py>

Conventions (IMPORTANT, the HTML runtime relies on them):
  * Units = meters. Build in Blender Z-up; exporter converts to three.js Y-up: (x,y,z)->(x,z,-y).
    So Blender -Y is "forward" (three.js +Z is Blender -Y)... keep it simple: author the model with
    its FRONT facing Blender -Y  (== three.js +Z) and its length along Blender X.
  * Asset origin at the ground, centered under the body.
  * Every exported object = one "part". Its Blender object ORIGIN is its animation PIVOT
    (legs: hip joint, head: neck base, wing: shoulder, tail: tail root, door: hinge edge ...).
    Parent objects with obj.parent = other_part to build a skeleton; rest pose must be authored
    with no rotation on parts (rotations/scales are baked into the geometry on export).
  * Materials via make_mat(). Color/roughness/metallic/emission/alpha are exported.
    Optional custom props: tex (name of runtime procedural texture or bundled texture), uvscale, double.
  * Vertex colors (color attribute 'Col') are exported if present and multiply the base color at runtime.
"""
import bpy, bmesh, json, base64, math, os, sys
import numpy as np
from mathutils import Vector, Matrix

OUT_DIR = '/shared/river/assets/out'
PREVIEW_DIR = '/shared/river/assets/preview'


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    return sc


def hex_rgb(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    # sRGB -> linear
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]


def make_mat(name, color, rough=0.6, metal=0.0, emit=None, emit_strength=0.0, alpha=1.0,
             tex=None, uvscale=1.0, double=False, spec=0.5):
    """color: '#rrggbb' (sRGB) or linear [r,g,b]."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    lin = hex_rgb(color) if isinstance(color, str) else list(color)
    bsdf.inputs['Base Color'].default_value = (lin[0], lin[1], lin[2], 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    bsdf.inputs['Alpha'].default_value = alpha
    if emit is not None:
        e = hex_rgb(emit) if isinstance(emit, str) else list(emit)
        bsdf.inputs['Emission Color'].default_value = (e[0], e[1], e[2], 1)
        bsdf.inputs['Emission Strength'].default_value = emit_strength
    m['tex'] = tex or ''
    m['uvscale'] = float(uvscale)
    m['double'] = bool(double)
    m['rgb'] = lin
    return m


def new_obj(name, bm_or_mesh, mat=None, parent=None, origin=None, loc=(0, 0, 0)):
    """Create a mesh object from a bmesh/mesh. origin: world point that becomes the pivot."""
    if isinstance(bm_or_mesh, bmesh.types.BMesh):
        me = bpy.data.meshes.new(name)
        bm_or_mesh.to_mesh(me)
        bm_or_mesh.free()
    else:
        me = bm_or_mesh
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if mat is not None:
        ob.data.materials.append(mat)
    ob.location = loc
    if origin is not None:
        set_origin(ob, origin)
    if parent is not None:
        set_parent(ob, parent)
    return ob


def set_origin(ob, world_point):
    """Move object origin to world_point without moving geometry."""
    wp = Vector(world_point)
    off = ob.matrix_world.inverted() @ wp
    ob.data.transform(Matrix.Translation(-off))
    ob.matrix_world.translation = wp
    bpy.context.view_layer.update()


def set_parent(ob, parent):
    mw = ob.matrix_world.copy()
    ob.parent = parent
    ob.matrix_parent_inverse = parent.matrix_world.inverted()
    ob.matrix_world = mw


def shade_smooth(ob, angle=None):
    me = ob.data
    for p in me.polygons:
        p.use_smooth = True
    if angle is not None and hasattr(me, 'set_sharp_from_angle'):
        me.set_sharp_from_angle(angle=angle)


def add_modifier(ob, kind, **kw):
    m = ob.modifiers.new(kind.title(), kind)
    for k, v in kw.items():
        setattr(m, k, v)
    return m


def apply_modifiers(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev)
    old = ob.data
    ob.modifiers.clear()
    ob.data = me
    if old.users == 0:
        bpy.data.meshes.remove(old)
    return ob


def _b64(a):
    return base64.b64encode(a.tobytes()).decode('ascii')


def _conv(v):  # Blender Z-up -> three.js Y-up
    return (v[0], v[2], -v[1])


def export_bundle(path, objs, meta=None, quant=True):
    """Export objects to JSON bundle. Returns stats dict.
    JSON: {meta, mats:{name:{...}}, parts:[{name,parent,pivot:[x,y,z],subs:[{mat,pos,nrm,uv,col,idx,n,tris}]}]}
    pos/nrm Float32 (base64, little endian); uv Float32; col Float32 rgb or ''; idx Uint32 or Uint16 (idx16 flag)."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    mats_out, parts, tri_total = {}, [], 0
    names = {o.name for o in objs}
    for ob in objs:
        if ob.type != 'MESH':
            continue
        ev = ob.evaluated_get(dg)
        me = bpy.data.meshes.new_from_object(ev, depsgraph=dg)
        M = ob.matrix_world.copy()
        piv = M.translation.copy()
        R = M.copy(); R.translation = (0, 0, 0)
        nrmM = R.to_3x3().inverted().transposed()
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        bm.to_mesh(me); bm.free()
        me.calc_loop_triangles()
        try:
            cn = [Vector(n.vector) for n in me.corner_normals]
        except Exception:
            me.calc_normals_split(); cn = [l.normal.copy() for l in me.loops]
        uvl = me.uv_layers.active
        ca = me.color_attributes.get('Col') or me.color_attributes.active_color
        subs = {}
        for lt in me.loop_triangles:
            mi = lt.material_index
            mat = ob.material_slots[mi].material if mi < len(ob.material_slots) and ob.material_slots[mi].material else None
            key = mat.name if mat else '_default'
            S = subs.setdefault(key, {'map': {}, 'pos': [], 'nrm': [], 'uv': [], 'col': [], 'idx': []})
            for li in lt.loops:
                v = me.loops[li].vertex_index
                n = (nrmM @ cn[li]).normalized()
                uv = tuple(uvl.data[li].uv) if uvl else (0.0, 0.0)
                col = tuple(ca.data[li].color[:3] if ca.domain == 'CORNER' else ca.data[v].color[:3]) if ca else ()
                k = (v, round(n.x, 3), round(n.y, 3), round(n.z, 3), round(uv[0], 4), round(uv[1], 4), tuple(round(c, 3) for c in col))
                ix = S['map'].get(k)
                if ix is None:
                    ix = len(S['pos']); S['map'][k] = ix
                    p = R @ me.vertices[v].co
                    S['pos'].append(_conv(p)); S['nrm'].append(_conv(n)); S['uv'].append(uv)
                    if col: S['col'].append(col)
                S['idx'].append(ix)
        sub_out = []
        for key, S in subs.items():
            if key != '_default' and key not in mats_out:
                m = bpy.data.materials[key]
                b = m.node_tree.nodes.get('Principled BSDF')
                mo = {'color': list(m.get('rgb', [0.8, 0.8, 0.8])), 'rough': 0.6, 'metal': 0.0, 'alpha': 1.0,
                      'tex': m.get('tex', ''), 'uvscale': m.get('uvscale', 1.0), 'double': bool(m.get('double', False))}
                if b:
                    mo['rough'] = b.inputs['Roughness'].default_value; mo['metal'] = b.inputs['Metallic'].default_value
                    mo['alpha'] = b.inputs['Alpha'].default_value
                    es = b.inputs['Emission Strength'].default_value
                    if es > 0:
                        ec = b.inputs['Emission Color'].default_value
                        mo['emit'] = [ec[0], ec[1], ec[2]]; mo['emitStrength'] = es
                mats_out[key] = mo
            pos = np.array(S['pos'], dtype=np.float32); nrm = np.array(S['nrm'], dtype=np.float32)
            uv = np.array(S['uv'], dtype=np.float32)
            idx = np.array(S['idx'], dtype=np.uint16 if len(pos) < 65535 else np.uint32)
            # flip winding because of the Z-up -> Y-up (x,z,-y) conversion keeps handedness? it is a proper rotation, keep.
            so = {'mat': key, 'n': int(len(pos)), 'tris': int(len(idx) // 3), 'pos': _b64(pos), 'nrm': _b64(nrm),
                  'uv': _b64(uv), 'idx': _b64(idx), 'idx16': idx.dtype == np.uint16}
            if S['col']:
                so['col'] = _b64(np.array(S['col'], dtype=np.float32))
            sub_out.append(so); tri_total += so['tris']
        bpy.data.meshes.remove(me)
        parts.append({'name': ob.name, 'parent': ob.parent.name if ob.parent and ob.parent.name in names else None,
                      'pivot': [round(c, 5) for c in _conv(piv)], 'subs': sub_out})
    data = {'meta': meta or {}, 'mats': mats_out, 'parts': parts}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, separators=(',', ':'))
    return {'path': path, 'parts': len(parts), 'tris': tri_total, 'kb': os.path.getsize(path) // 1024}


def setup_preview_world(sun_energy=3.0):
    sc = bpy.context.scene
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.55, 0.65, 0.8, 1); bg.inputs[1].default_value = 1.0
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = sun_energy
    so = bpy.data.objects.new('sun', sun); so.rotation_euler = (math.radians(50), 0, math.radians(35))
    sc.collection.objects.link(so)
    return so


def render_preview(path, objs, cam_loc, target=(0, 0, 0.5), res=(720, 480), samples=24, lens=50, ground=True):
    """Cycles CPU preview. cam_loc/target in Blender coords. Saves PNG to path."""
    sc = bpy.context.scene
    setup_preview_world()
    if ground:
        bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
        g = bpy.context.object; g.name = '_ground'
        g.data.materials.append(make_mat('_groundmat', '#6b7a45', rough=0.95))
    cam = bpy.data.cameras.new('cam'); cam.lens = lens
    co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co)
    co.location = cam_loc
    d = Vector(target) - Vector(cam_loc)
    co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = co
    sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.device = 'CPU'
    sc.cycles.use_denoising = False
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = path; sc.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)
    return path
