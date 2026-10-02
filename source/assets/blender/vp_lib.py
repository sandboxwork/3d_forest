"""Village props toolkit (vp_*).  Builds on kt_lib (accumulator geometry with box/lathe/sweep/tube/modifier helpers).
All geometry of a prop is authored in PROP-LOCAL coords (Z up, front = -Y, origin on the ground at the prop centre).
Usage in a prop module:

    from vp_lib import *
    @prop('barrel_a', 'barrel')
    def barrel_a():
        lathe('oak', ...); collider(...)
        sub('well_bucket', pivot=(0,0,1.2), fn=lambda: ...)     # animated sub part, parented to the prop's main part
"""
import sys, os, math, random, json
sys.path.insert(0, '/shared/river/assets/blender')
from kt_lib import *
import kt_lib
from kt_mats import PBR_TINT, HI_FALLBACK

TEXDIR = '/shared/river/assets/tex/'
REG = {}        # name -> (fn, ko, kind)
DEFER = []      # sub parts queued while a prop builds
CUR = {}        # per-prop scratch (lights, camera hints)
PROP_RND = random.Random(5)


def prop(name, ko, kind='static', cam=None, ao_len=0.14):
    def deco(fn):
        REG[name] = dict(fn=fn, ko=ko, kind=kind, cam=cam, ao_len=ao_len)
        return fn
    return deco


def sub(name, pivot, fn, parent=None):
    """queue an animated sub part. fn() adds geometry (prop-local coords) to a fresh accumulator."""
    DEFER.append((name, tuple(pivot), fn, parent))


def set_light(pos, color=(1.0, 0.7, 0.4)):
    CUR['light'] = {'pos': [round(pos[0], 3), round(pos[2], 3), round(-pos[1], 3)], 'color': list(color)}


def H(h):
    return tuple(hex_rgb(h))


def init_vp_mats():
    def m(name, color='#ffffff', **kw):
        return MAT(name, color, **kw)
    # weathered woods: tint comes from vertex colours
    m('pine', '#ffffff', tex='pbr_wood_pine', tile=0.6, rough=0.85, sharp=40)
    m('oak', '#ffffff', tex='pbr_wood_oak', tile=0.5, rough=0.8, sharp=40)
    m('dark', '#ffffff', tex='pbr_wood_dark', tile=0.6, rough=0.75, sharp=40)
    m('iron', '#ffffff', tex='pbr_iron', tile=0.4, rough=0.6, metal=0.9, sharp=42)
    m('iron_dark', '#8a8a90', tex='pbr_iron', tile=0.3, rough=0.55, metal=0.9, sharp=42)
    m('copper', '#ffd9c8', tex='pbr_brass_copper', tile=0.3, rough=0.4, metal=1.0, sharp=45)
    m('brass', '#ffffb0', tex='pbr_brass_copper', tile=0.3, rough=0.35, metal=1.0, sharp=45)
    m('stone', '#ffffff', tex='pbr_stone_fireplace', tile=1.5, rough=0.95, sharp=60)
    m('ceramic', '#ffffff', tex='pbr_ceramic', tile=0.2, rough=0.4, sharp=55)
    m('terracotta', '#e2906a', tex='pbr_ceramic', tile=0.2, rough=0.9, sharp=55)
    m('linen', '#ffffff', tex='pbr_fabric_linen', tile=0.25, rough=1.0, sharp=70, double=True)
    m('burlap', '#ffffff', tex='pbr_fabric_burlap', tile=0.25, rough=1.0, sharp=70, double=True)
    m('wicker', '#ffffff', tex='pbr_wicker', tile=0.2, rough=0.9, sharp=70)
    m('rope', '#ffffff', rough=1.0, sharp=70)
    m('straw', '#ffffff', rough=1.0, sharp=80, double=True)
    m('bark', '#ffffff', tex='bark', tile=1.0, rough=1.0, sharp=70)
    m('leaf', '#ffffff', rough=0.7, sharp=90, double=True)
    m('plain', '#ffffff', rough=0.8, sharp=70)
    m('plain_gloss', '#ffffff', rough=0.35, sharp=70)
    m('soil', '#ffffff', rough=1.0, sharp=70)
    m('food', '#ffffff', rough=0.55, sharp=70)
    m('fish', '#ffffff', rough=0.3, sharp=70)
    m('glass', '#e9f3f0', rough=0.08, alpha=0.2, double=True, sharp=60)
    m('flame', '#ffcf70', emit='#ff9a30', emit_strength=6.0, rough=0.5, sharp=90)
    m('water', '#5d8a92', rough=0.06, sharp=90)


def interp_path(vals, res):
    n = len(vals); out = []
    for i in range(n - 1):
        p0 = vals[max(i - 1, 0)]; p1 = vals[i]; p2 = vals[i + 1]; p3 = vals[min(i + 2, n - 1)]
        for k in range(res):
            t = k / res
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(vals[-1])
    return out


# --------------------------------------------------------------- extra geometry helpers
def beam(mat, a, b, w, t, up=(0, 0, 1), bev=0.004, col=(1, 1, 1), cfn=None, off=0.0, flat=False, skip_down=False):
    """box between points a and b (ends flat); cross-section w (along 'side') x t (along up). grain along its length."""
    a = Vector(a); b = Vector(b)
    d = b - a
    L = d.length
    x = d.normalized()
    u = Vector(up)
    z = (u - x * u.dot(x))
    if z.length < 1e-6:
        z = Vector((0, 1, 0)) - x * x.y
    z.normalize()
    y = z.cross(x)
    Mx = Matrix(((x.x, y.x, z.x, 0), (x.y, y.y, z.y, 0), (x.z, y.z, z.z, 0), (0, 0, 0, 1)))
    c = (a + b) / 2 + z * off
    Mx = Matrix.Translation(c) @ Mx
    box(mat, None, (L, w, t), M=Mx, bev=bev, col=col, cfn=cfn, g=0, skip_down=skip_down, flat=flat)


def rock(mat, c, size, seed=0, rot=None, col=(1, 1, 1), cfn=None, cuts=2, round_=0.55, jitter=0.12, flat=False, bev=0.0):
    """rounded lumpy rubble block, size=(x,y,z)."""
    r = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    if cuts:
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True)
    for v in bm.verts:
        p = v.co.copy()
        L = p.length
        q = p.normalized() * 0.5 * (0.5 + 0.5 * 1.0)
        p = p.lerp(p.normalized() * 0.5 * 1.02, round_)
        p = Vector((p.x * (1 + r.uniform(-jitter, jitter)), p.y * (1 + r.uniform(-jitter, jitter)), p.z * (1 + r.uniform(-jitter, jitter) * 0.6)))
        v.co = Vector((p.x * size[0], p.y * size[1], p.z * size[2]))
    put(mat, bm, xf(c, rot), col, cfn, 2, flat=flat)
    bm.free()


def ribbon(mat, p0, p1, w0, w1=None, col=(1, 1, 1), bend=(0, 0, 0), nseg=1, up=(0, 1, 0), flat=True):
    """flat double-sided strip from p0 to p1 (width w0->w1) with optional bend offset at the middle."""
    w1 = w0 if w1 is None else w1
    p0 = Vector(p0); p1 = Vector(p1)
    d = (p1 - p0)
    x = d.normalized()
    s = Vector(up).cross(x)
    if s.length < 1e-4:
        s = Vector((1, 0, 0)).cross(x)
    s.normalize()
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    rows = []
    for i in range(nseg + 1):
        t = i / nseg
        c = p0.lerp(p1, t) + Vector(bend) * math.sin(math.pi * t)
        w = (w0 + (w1 - w0) * t) / 2
        rows.append((bm.verts.new(c - s * w), bm.verts.new(c + s * w)))
    for i in range(nseg):
        f = bm.faces.new((rows[i][0], rows[i][1], rows[i + 1][1], rows[i + 1][0]))
        f.smooth = False
        for l, (u, v) in zip(f.loops, ((0, i / nseg), (1, i / nseg), (1, (i + 1) / nseg), (0, (i + 1) / nseg))):
            l[ul].uv = (u, v)
    put(mat, bm, Matrix.Identity(4), col, None, 2, flat=flat)
    bm.free()


def leafquad(mat, c, size, rot, col=(1, 1, 1), tip=0.0):
    """small diamond-ish leaf quad (4-6 verts) centred at c, rot=(rx,ry,rz) rad -> Euler"""
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    L, W = size
    pts = [(0, 0, -L * 0.5), (W * 0.5, 0, -L * 0.1), (W * 0.35, 0, L * 0.3), (0, 0, L * 0.5), (-W * 0.35, 0, L * 0.3), (-W * 0.5, 0, -L * 0.1)]
    vs = [bm.verts.new(p) for p in pts]
    f = bm.faces.new(vs)
    f.smooth = False
    for l in f.loops:
        l[ul].uv = (l.vert.co.x / W + 0.5, l.vert.co.z / L + 0.5)
    for v in bm.verts:
        v.co.y += tip * (abs(v.co.x) / W) * L
    put(mat, bm, Matrix.Translation(Vector(c)) @ Euler(rot, 'XYZ').to_matrix().to_4x4(), col, None, 2, flat=True)
    bm.free()


def nail(c, d=(0, -1, 0), r=0.007, col=(0.12, 0.11, 0.1), mat='iron_dark'):
    d = Vector(d).normalized()
    z = d
    x = Vector((0, 0, 1)).cross(z)
    if x.length < 1e-4:
        x = Vector((1, 0, 0))
    x.normalize()
    y = z.cross(x)
    Mx = Matrix(((x.x, y.x, z.x, c[0]), (x.y, y.y, z.y, c[1]), (x.z, y.z, z.z, c[2]), (0, 0, 0, 1)))
    lathe(mat, None, [(0.0, 0.0), (r, 0.0), (r * 0.8, r * 0.5), (0, r * 0.7)], seg=6, col=col, M=Mx, cap=False, auto=False)


def jitter_col(base, amp=0.1, r=None):
    r = r or PROP_RND
    k = 1 + r.uniform(-amp, amp)
    return (base[0] * k, base[1] * k, base[2] * k)


def wood_cfn(base, amp=0.12, s=7.0, seed=0, grime_z=0.35, grime=0.5, dirt=(0.20, 0.17, 0.12), axis=2):
    """weathered wood colour: base tint x noise, darker toward the ground (damp/dirt)"""
    def f(p):
        t = fbm(p.x * (1 if axis != 0 else 0.2), p.y * (1 if axis != 1 else 0.2), p.z * (1 if axis != 2 else 0.2), s, seed, 3)
        k = 1 + amp * t
        c = (base[0] * k, base[1] * k, base[2] * k)
        if grime_z > 0 and p.z < grime_z:
            g = (1 - p.z / grime_z) * grime
            c = mixc(c, dirt, g)
        return c
    return f


def stone_cfn(base_a, base_b, s=5.0, seed=0, moss=0.0, grime_z=0.3):
    def f(p):
        t = fbm(p.x, p.y, p.z, s, seed, 3) * 0.5 + 0.5
        c = mixc(base_a, base_b, t)
        t2 = fbm(p.x, p.y, p.z, s * 6, seed + 3, 2)
        k = 1 + 0.18 * t2
        c = (c[0] * k, c[1] * k, c[2] * k)
        if moss > 0 and p.z < grime_z + 0.2:
            m = max(0.0, (fbm(p.x, p.y, p.z, 9, seed + 5, 2) * 0.5 + 0.5) - 0.5) * 2 * moss * (1 - p.z / (grime_z + 0.2))
            c = mixc(c, (0.20, 0.30, 0.10), min(1.0, m))
        return c
    return f


def cloth_sag_grid(x0, x1, y0, y1, nx, ny, zfn):
    """grid bmesh with heights from zfn(x,y) -> z; UV in meters"""
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    vs = [[bm.verts.new((x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny, zfn(x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny))) for j in range(ny + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(ny):
            f = bm.faces.new((vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1]))
            f.smooth = True
            for l in f.loops:
                l[ul].uv = (l.vert.co.x, l.vert.co.y)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


# --------------------------------------------------------------- AO
def ao_prepare(objs, maxlen=0.14, minarea=0.008):
    for ob in objs:
        if ob.name.startswith('_'):
            continue
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        for _ in range(2):
            edges = set()
            for f in bm.faces:
                if f.calc_area() < minarea:
                    continue
                for e in f.edges:
                    if e.calc_length() > maxlen * 1.3:
                        edges.add(e)
            if not edges:
                break
            groups = {}
            for e in edges:
                n = max(1, int(math.ceil(e.calc_length() / maxlen)) - 1)
                groups.setdefault(min(n, 5), []).append(e)
            for n, es in groups.items():
                es = [e for e in es if e.is_valid]
                if es:
                    bmesh.ops.subdivide_edges(bm, edges=es, cuts=n, use_grid_fill=True)
            bm.normal_update()
        bm.to_mesh(ob.data)
        bm.free()


def ao_bake(objs, samples=32, dist=0.7, strength=0.85, gamma=0.9, skip_mats=('flame', 'glass', 'water')):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = False
    w = bpy.data.worlds.new('AOW')
    sc.world = w
    w.use_nodes = True
    w.light_settings.distance = dist
    sc.render.bake.target = 'VERTEX_COLORS'
    gnd = bpy.data.objects.get('_gnd')
    if gnd is None:
        bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
        gnd = bpy.context.object
        gnd.name = '_gnd'
    gnd.hide_render = False
    targets = []
    for ob in objs:
        if ob.type != 'MESH':
            continue
        ca = ob.data.color_attributes.new('AO', 'FLOAT_COLOR', 'POINT')
        ob.data.color_attributes.active_color = ca
        targets.append(ob)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in targets:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = targets[0]
    bpy.context.view_layer.update()
    bpy.ops.object.bake(type='AO')
    for ob in targets:
        me = ob.data
        nv = len(me.vertices)
        a = np.zeros(nv * 4, dtype=np.float32)
        me.color_attributes['AO'].data.foreach_get('color', a)
        ao = np.clip(a.reshape(-1, 4)[:, 0], 0, 1) ** gamma
        skip = [s.material.name in skip_mats for s in ob.material_slots if s.material]
        fac = (1.0 - strength) + strength * ao
        li = np.zeros(len(me.loops), dtype=np.int32)
        me.loops.foreach_get('vertex_index', li)
        ca = me.color_attributes['Col']
        col = np.zeros(len(me.loops) * 4, dtype=np.float32)
        ca.data.foreach_get('color', col)
        col = col.reshape(-1, 4)
        mi = np.zeros(len(me.polygons), dtype=np.int32)
        me.polygons.foreach_get('material_index', mi)
        ls = np.zeros(len(me.polygons), dtype=np.int32)
        me.polygons.foreach_get('loop_start', ls)
        lt = np.zeros(len(me.polygons), dtype=np.int32)
        me.polygons.foreach_get('loop_total', lt)
        fl = fac[li].copy()
        for pi in range(len(mi)):
            if mi[pi] < len(skip) and skip[mi[pi]]:
                fl[ls[pi]:ls[pi] + lt[pi]] = 1.0
        col[:, :3] *= fl[:, None]
        ca.data.foreach_set('color', col.ravel())
        me.color_attributes.active_color = ca
        me.color_attributes.remove(me.color_attributes['AO'])
    gnd.hide_render = True


# --------------------------------------------------------------- build driver
def bbox_of(objs):
    mn = Vector((1e9, 1e9, 1e9)); mx = Vector((-1e9, -1e9, -1e9))
    for ob in objs:
        for v in ob.data.vertices:
            p = ob.matrix_world @ v.co
            for i in range(3):
                mn[i] = min(mn[i], p[i]); mx[i] = max(mx[i], p[i])
    return mn, mx


def tri_total(objs):
    t = 0
    for o in objs:
        o.data.calc_loop_triangles()
        t += len(o.data.loop_triangles)
    return t


def build_prop(name, ao=True, ao_len=0.14):
    spec = REG[name]
    kt_lib.ACC.clear(); kt_lib.COLL.clear(); kt_lib.PARTS.clear(); DEFER.clear(); CUR.clear()
    PROP_RND.seed(sum(ord(c)*(i+7) for i,c in enumerate(name)) & 0xffff)
    kt_lib.rnd.seed(sum(ord(c)*(i+7) for i,c in enumerate(name)) & 0xffff)
    saved = part_begin()
    spec['fn']()
    colliders = list(kt_lib.COLL)
    main = part_end(saved, name, (0, 0, 0))
    objs = [main]
    queue = list(DEFER); DEFER.clear()
    byname = {name: main}
    while queue:
        sn, piv, fn, par = queue.pop(0)
        s2 = part_begin()
        fn()
        so = part_end(s2, sn, piv)
        set_parent(so, byname.get(par or name, main))
        byname[sn] = so
        objs.append(so)
        queue += list(DEFER); DEFER.clear()
    for o in objs:
        for p in o.data.polygons:
            p.use_smooth = True if p.use_smooth else False
    mn, mx = bbox_of(objs)
    tris0 = tri_total(objs)
    if ao:
        ao_prepare(objs, maxlen=max(spec.get('ao_len', ao_len), float(os.environ.get('AO_MIN', '1.0'))))
        ao_bake(objs)
    meta = {'w': round(mx.x - mn.x, 3), 'd': round(mx.y - mn.y, 3), 'h': round(mx.z, 3), 'colliders': colliders,
            'ko': spec['ko'], 'kind': spec['kind']}
    if 'light' in CUR:
        meta['light'] = CUR['light']
    meta['bbox'] = [[round(c, 3) for c in mn], [round(c, 3) for c in mx]]
    return objs, meta, spec


# --------------------------------------------------------------- preview
def preview_wire(objs):
    from kt_room import preview_mats
    preview_mats(objs)
    # runtime built-in textures that don't exist as jpg: tint by colour only
    for ob in objs:
        for s in ob.material_slots:
            m = s.material
            if m and m.get('tex') == 'bark':
                b = m.node_tree.nodes.get('Principled BSDF')


def preview_render(path, objs_visible, all_objs, views, res=(560, 420), samples=40, bg=(0.62, 0.72, 0.88), sun=4.0):
    sc = bpy.context.scene
    for o in all_objs:
        o.hide_render = o not in objs_visible
    if not sc.world or sc.world.name.startswith('AOW'):
        w = bpy.data.worlds.new('PW'); sc.world = w; w.use_nodes = True
        b = w.node_tree.nodes['Background']; b.inputs[0].default_value = (bg[0], bg[1], bg[2], 1); b.inputs[1].default_value = 0.9
    if not bpy.data.objects.get('_sun'):
        sd = bpy.data.lights.new('sun', 'SUN'); sd.energy = sun; sd.angle = math.radians(4)
        so = bpy.data.objects.new('_sun', sd); so.rotation_euler = (math.radians(52), 0, math.radians(-38))
        sc.collection.objects.link(so)
    g = bpy.data.objects.get('_gnd')
    if g is None:
        bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0)); g = bpy.context.object; g.name = '_gnd'
    if not g.data.materials:
        g.data.materials.append(make_mat('_groundmat', '#5e6e3c', rough=0.95))
    g.hide_render = False
    cam = bpy.data.objects.get('_cam')
    if cam is None:
        cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('_cam', cd); sc.collection.objects.link(cam)
    sc.camera = cam
    sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.device = 'CPU'
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6; sc.cycles.transparent_max_bounces = 16
    sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.04
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.image_settings.file_format = 'PNG'
    sc.view_settings.exposure = 0.0
    names = [x.identifier for x in sc.view_settings.bl_rna.properties['view_transform'].enum_items]
    sc.view_settings.view_transform = 'AgX' if 'AgX' in names else 'Filmic'
    tiles = []
    for i, v in enumerate(views):
        loc, tg, ln = v
        cam.data.lens = ln; cam.data.clip_start = 0.03
        cam.location = loc
        cam.rotation_euler = (Vector(tg) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        fp = '/tmp/_vpv_%d.png' % i
        sc.render.filepath = fp
        bpy.ops.render.render(write_still=True)
        im = bpy.data.images.load(fp)
        a = np.array(im.pixels[:], dtype=np.float32).reshape(res[1], res[0], 4)
        tiles.append(a); bpy.data.images.remove(im)
    cols = 2 if len(tiles) > 1 else 1
    rows = (len(tiles) + cols - 1) // cols
    H_, W_ = res[1], res[0]
    canvas = np.ones((rows * H_, cols * W_, 4), dtype=np.float32)
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        canvas[(rows - 1 - r) * H_:(rows - r) * H_, c * W_:(c + 1) * W_] = t
    im = bpy.data.images.new('grid', cols * W_, rows * H_)
    im.pixels = canvas.ravel().tolist()
    im.filepath_raw = path; im.file_format = 'PNG'; im.save()
    bpy.data.images.remove(im)


def default_views(meta, spec):
    mn, mx = meta['bbox']
    cx = (mn[0] + mx[0]) / 2; cy = (mn[1] + mx[1]) / 2
    ext = max(mx[0] - mn[0], mx[1] - mn[1], mx[2])
    cz = mx[2] * 0.45
    d = ext * 1.5 + 0.8
    views = [((cx + d * 0.7, cy - d * 0.8, cz + ext * 0.45), (cx, cy, cz), 40),
             ((cx - d * 0.8, cy + d * 0.7, cz + ext * 0.45), (cx, cy, cz), 40)]
    if spec.get('cam'):
        views = spec['cam'](meta) if callable(spec['cam']) else spec['cam']
    return views
