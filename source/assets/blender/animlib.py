"""animlib: lofting / blobs / coat painting / preview helpers on top of bl_common.
Usage:  import sys; sys.path.insert(0,'/shared/river/assets/blender'); from animlib import *
All geometry is authored in WORLD coords (Z up, nose -Y), then finish_part() turns a bmesh into an object
whose origin is moved to the pivot (set_origin) and parents it.
"""
import sys
sys.path.insert(0, '/shared/river/assets/blender')
from bl_common import *
from mathutils import noise as mnoise
import random

def V(*a):
    return Vector(a[0] if len(a) == 1 else a)


def lerp(a, b, t):
    return a + (b - a) * t


def cr(p0, p1, p2, p3, t):
    """Catmull-Rom for scalars or Vectors."""
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)


def interp_path(vals, res):
    """Interpolate list of scalars/vectors with catmull-rom, res samples per span."""
    n = len(vals)
    out = []
    for i in range(n - 1):
        p0 = vals[max(i - 1, 0)]; p1 = vals[i]; p2 = vals[i + 1]; p3 = vals[min(i + 2, n - 1)]
        for k in range(res):
            out.append(cr(p0, p1, p2, p3, k / res))
    out.append(vals[-1])
    return out


def loft(pts, rx, rz=None, segs=14, res=4, up=(0, 0, 1), cap0=True, cap1=True, power=2.0, cap_push=0.6, off=None, twist=None):
    """Tube through pts (list of xyz) with elliptical cross-section.
    rx: half-width (along 'side'), rz: half-height (along 'up'). lists same length as pts (or scalar).
    power: superellipse exponent (2=ellipse, >2 boxier). off: optional per-point (side,up) offsets.
    Returns bmesh."""
    n = len(pts)
    pts = [V(p) for p in pts]
    rx = [rx] * n if not isinstance(rx, (list, tuple)) else list(rx)
    rz = rx if rz is None else ([rz] * n if not isinstance(rz, (list, tuple)) else list(rz))
    P = interp_path(pts, res); RX = interp_path(rx, res); RZ = interp_path(rz, res)
    m = len(P)
    bm = bmesh.new()
    rings = []
    upv = V(up)
    prev_side = None
    for i in range(m):
        if i == 0:
            t = (P[1] - P[0])
        elif i == m - 1:
            t = (P[-1] - P[-2])
        else:
            t = (P[i + 1] - P[i - 1])
        t.normalize()
        side = t.cross(upv)
        if side.length < 1e-4:
            side = t.cross(V((1, 0, 0)))
        side.normalize()
        if prev_side is not None and side.dot(prev_side) < 0:
            side = -side
        prev_side = side
        u = side.cross(t).normalized()
        if u.dot(upv) < 0 and upv.length > 0:
            pass
        ring = []
        for j in range(segs):
            a = 2 * math.pi * j / segs
            c, s = math.cos(a), math.sin(a)
            pc = math.copysign(abs(c) ** (2 / power), c)
            ps = math.copysign(abs(s) ** (2 / power), s)
            ring.append(bm.verts.new(P[i] + side * (RX[i] * pc) + u * (RZ[i] * ps)))
        rings.append(ring)
    for i in range(m - 1):
        for j in range(segs):
            a, b = rings[i][j], rings[i][(j + 1) % segs]
            c, d = rings[i + 1][(j + 1) % segs], rings[i + 1][j]
            try:
                bm.faces.new((a, b, c, d))
            except ValueError:
                pass
    for (cap, idx, sgn) in ((cap0, 0, -1), (cap1, m - 1, 1)):
        if not cap:
            continue
        t = (P[1] - P[0]) if idx == 0 else (P[-1] - P[-2])
        t.normalize()
        cen = bm.verts.new(P[idx] + t * sgn * min(RX[idx], RZ[idx]) * cap_push * -1 * -1 if False else P[idx] + t * (-1 if idx == 0 else 1) * min(RX[idx], RZ[idx]) * cap_push)
        ring = rings[idx]
        for j in range(segs):
            a, b = ring[j], ring[(j + 1) % segs]
            try:
                bm.faces.new((b, a, cen) if idx == 0 else (a, b, cen))
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def blob(center, radii, rot=(0, 0, 0), segs=16, rings=10):
    """Ellipsoid at center with radii (x,y,z) and euler rot (radians)."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0)
    for v in bm.verts:
        v.co.x *= radii[0]; v.co.y *= radii[1]; v.co.z *= radii[2]
    if any(rot):
        bmesh.ops.rotate(bm, verts=bm.verts[:], cent=(0, 0, 0), matrix=Matrix.Rotation(rot[2], 3, 'Z') @ Matrix.Rotation(rot[1], 3, 'Y') @ Matrix.Rotation(rot[0], 3, 'X'))
    bmesh.ops.translate(bm, verts=bm.verts[:], vec=center)
    return bm


def merge(*bms):
    """Merge several bmeshes into the first (keeps face material_index)."""
    tgt = bmesh.new()
    for b in bms:
        me = bpy.data.meshes.new('_t')
        b.to_mesh(me)
        b.free()
        tgt.from_mesh(me)
        bpy.data.meshes.remove(me)
    return tgt


def set_mat_index(bm, idx):
    for f in bm.faces:
        f.material_index = idx
    return bm


def xform(bm, mat):
    bmesh.ops.transform(bm, matrix=mat, verts=bm.verts[:])
    return bm


def mirror_x(bm):
    """Return a mirrored (x -> -x) copy as new bmesh."""
    b2 = bm.copy()
    for v in b2.verts:
        v.co.x = -v.co.x
    bmesh.ops.reverse_faces(b2, faces=b2.faces[:])
    return b2


def smooth_bm(bm, iters=1, factor=0.5):
    for _ in range(iters):
        bmesh.ops.smooth_vert(bm, verts=bm.verts[:], factor=factor, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    return bm


def subdiv(bm, levels=1):
    for _ in range(levels):
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=True, use_smooth_even=True)
        bmesh.ops.triangulate(bm, faces=bm.faces[:]) if False else None
    return bm


def fur_noise(bm, amp=0.003, freq=60.0, seed=0, freq2=None, amp2=0.0):
    """Displace along normals with fine noise (fur/feather bumpiness)."""
    bm.normal_update()
    for v in bm.verts:
        p = v.co * freq + V((seed * 7.1, seed * 3.3, seed * 1.7))
        d = mnoise.noise(p) * amp
        if freq2:
            d += mnoise.noise(v.co * freq2 + V((seed, 0, 0))) * amp2
        v.co += v.normal * d
    return bm


def fbm(p, f=1.0, oct=3, seed=0):
    s = 0.0; a = 1.0; tot = 0.0
    q = V(p) * f + V((seed * 11.3, seed * 5.7, seed * 2.9))
    for _ in range(oct):
        s += mnoise.noise(q) * a; tot += a; a *= 0.5; q = q * 2.1
    return s / tot  # approx -1..1


def paint(bm, fn, name='Col'):
    """Assign vertex (point-domain) colors. fn(co(world), normal) -> (r,g,b) in sRGB hex str or linear tuple."""
    bm.normal_update()
    lay = bm.verts.layers.color.get(name) or bm.verts.layers.color.new(name)
    for v in bm.verts:
        c = fn(v.co.copy(), v.normal.copy())
        if isinstance(c, str):
            c = hex_rgb(c)
        v[lay] = (c[0], c[1], c[2], 1.0)
    return bm


def mixc(a, b, t):
    t = max(0.0, min(1.0, t))
    if isinstance(a, str): a = hex_rgb(a)
    if isinstance(b, str): b = hex_rgb(b)
    return [a[i] + (b[i] - a[i]) * t for i in range(3)]


def mulc(c, k):
    if isinstance(c, str): c = hex_rgb(c)
    return [min(1.0, x * k) for x in c]


def vcol_mat(name, color='#ffffff', **kw):
    """make_mat + preview wiring so the 'Col' attribute multiplies base color in Cycles previews.
    Export still reads the principled default (color) + vertex colors multiply at runtime."""
    m = make_mat(name, color, **kw)
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    ca = nt.nodes.new('ShaderNodeVertexColor'); ca.layer_name = 'Col'
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'
    mx.inputs[0].default_value = 1.0
    mx.inputs[6].default_value = b.inputs['Base Color'].default_value
    nt.links.new(ca.outputs['Color'], mx.inputs[7])
    nt.links.new(mx.outputs[2], b.inputs['Base Color'])
    return m


def part(name, bm, mats, pivot, parent=None, colorfn=None, smooth=True, noise=None):
    """Finish a bmesh into a part. mats: a material or list (index via face.material_index)."""
    if noise:
        fur_noise(bm, **noise)
    if colorfn:
        paint(bm, colorfn)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    for m in (mats if isinstance(mats, (list, tuple)) else [mats]):
        ob.data.materials.append(m)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    bpy.context.view_layer.update()
    set_origin(ob, pivot)
    if parent is not None:
        set_parent(ob, parent)
    return ob


def tri_count(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    t = 0
    for o in objs:
        if o.type == 'MESH':
            me = o.data
            me.calc_loop_triangles()
            t += len(me.loop_triangles)
    return t


def leaf_shape(base, tip, width, thick, bulge=0.4, segs=8, curve=(0, 0, 0), res=3, up=(0, 0, 1)):
    """Flat leaf/feather/ear/fin style blade: loft from base to tip with width profile (sin) and thin thickness."""
    base = V(base); tip = V(tip)
    n = 6
    pts = []; rx = []; rz = []
    for i in range(n):
        t = i / (n - 1)
        pts.append(base.lerp(tip, t) + V(curve) * math.sin(math.pi * t))
        w = width * (math.sin(math.pi * min(1, t * (1 / (bulge * 2 + 0.0001)) if t < bulge else 1 - (t - bulge) / (1 - bulge)) * 0.5) ** 0.8 if 0 < t < 1 else 0.0)
        if t >= bulge:
            w = width * max(0.0, math.cos((t - bulge) / (1 - bulge) * math.pi / 2)) ** 0.7
        else:
            w = width * (0.35 + 0.65 * math.sin(t / bulge * math.pi / 2))
        rx.append(max(w, 0.0005)); rz.append(thick)
    return loft(pts, rx, rz, segs=segs, res=res, up=up)


# ---------------------------------------------------------------- preview

def preview_grid(path, views, res=(480, 340), samples=20, target=(0, 0, 0.5), lens=50, sun=3.0, ground=True, bg=(0.55, 0.65, 0.8)):
    """Render several views (list of (cam_loc, target or None, lens or None)) and tile into one PNG (2 columns)."""
    sc = bpy.context.scene
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    b = w.node_tree.nodes['Background']; b.inputs[0].default_value = (bg[0], bg[1], bg[2], 1); b.inputs[1].default_value = 1.0
    sd = bpy.data.lights.new('sun', 'SUN'); sd.energy = sun
    so = bpy.data.objects.new('sun', sd); so.rotation_euler = (math.radians(50), 0, math.radians(35))
    sc.collection.objects.link(so)
    if ground:
        bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
        g = bpy.context.object; g.name = '_ground'
        g.data.materials.append(make_mat('_groundmat', '#6b7a45', rough=0.95))
    cam = bpy.data.cameras.new('cam')
    co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co)
    sc.camera = co
    sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.device = 'CPU'
    sc.cycles.use_denoising = False
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.image_settings.file_format = 'PNG'
    tiles = []
    for i, v in enumerate(views):
        loc = v[0]; tg = v[1] if len(v) > 1 and v[1] is not None else target; ln = v[2] if len(v) > 2 and v[2] else lens
        cam.lens = ln
        co.location = loc
        co.rotation_euler = (V(tg) - V(loc)).to_track_quat('-Z', 'Y').to_euler()
        fp = '/tmp/_pv_%d.png' % i
        sc.render.filepath = fp
        bpy.ops.render.render(write_still=True)
        im = bpy.data.images.load(fp)
        a = np.array(im.pixels[:], dtype=np.float32).reshape(res[1], res[0], 4)
        tiles.append(a); bpy.data.images.remove(im)
    cols = 2
    rows = (len(tiles) + 1) // 2
    H, W = res[1], res[0]
    canvas = np.ones((rows * H, cols * W, 4), dtype=np.float32)
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        canvas[(rows - 1 - r) * H:(rows - r) * H, c * W:(c + 1) * W] = t
    im = bpy.data.images.new('grid', cols * W, rows * H)
    im.pixels = canvas.ravel().tolist()
    im.filepath_raw = path; im.file_format = 'PNG'; im.save()
    return path


def std_views(size=1.6, h=0.5, dist=None):
    """side(+X), front(-Y), 3/4, back-3/4 camera locations around an asset of given size centred at (0,0,h)."""
    d = dist or size * 1.9
    t = (0, 0, h)
    return [((d, 0, h + size * 0.1), t), ((0, -d, h + size * 0.15), t),
            ((d * .72, -d * .72, h + size * 0.35), t), ((-d * .7, d * .7, h + size * 0.3), t)]


def write_meta(name, meta):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, name + '.meta.json'), 'w') as f:
        json.dump(meta, f, indent=1)


def fuse(bm, voxel=0.012, smooth_iter=8, smooth_f=0.6):
    """Voxel-remesh a bmesh of overlapping blobs/lofts into one fused surface, then smooth. Returns new bmesh."""
    me = bpy.data.meshes.new('_fuse'); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('_fuse', me); bpy.context.scene.collection.objects.link(ob)
    m = ob.modifiers.new('rm', 'REMESH'); m.mode = 'VOXEL'; m.voxel_size = voxel
    try:
        m.adaptivity = 0.0
    except Exception:
        pass
    m2 = ob.modifiers.new('sm', 'SMOOTH'); m2.factor = smooth_f; m2.iterations = smooth_iter
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me2 = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), depsgraph=dg)
    bpy.data.objects.remove(ob); bpy.data.meshes.remove(me)
    out = bmesh.new(); out.from_mesh(me2); bpy.data.meshes.remove(me2)
    return out
