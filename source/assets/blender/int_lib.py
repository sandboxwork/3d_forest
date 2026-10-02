"""Geometry toolkit for house_interior. Everything accumulates into per-material bmeshes in WORLD coords."""
import sys, math, random
sys.path.insert(0, '/shared/river/assets/blender')
from bl_common import *
from mathutils import noise as mnoise, Euler

F = 0.30          # finished floor z
ACC = {}          # matname -> (bm, mat)
TEXSC = {}        # matname -> uv scale (tex tiles per meter)
LIGHTS, COLL, INTER = [], [], []
PARTS = []        # separate objects (animated parts)
rnd = random.Random(11)


def C(c):
    if isinstance(c, str):
        return tuple(hex_rgb(c))
    return tuple(c)


def MAT(name, color='#ffffff', tex=None, tsc=1.0, **kw):
    m = make_mat(name, color, tex=tex, **kw)
    TEXSC[name] = tsc
    return m


def get_bm(mat):
    e = ACC.get(mat.name)
    if e is None:
        bm = bmesh.new()
        bm.loops.layers.float_color.new('Col')
        bm.loops.layers.uv.new('UVMap')
        e = (bm, mat)
        ACC[mat.name] = e
    return e[0]


def rotm(rot):
    if rot is None:
        return Matrix.Identity(4)
    if isinstance(rot, (int, float)):
        rot = (0, 0, rot)
    return Euler([math.radians(a) for a in rot], 'XYZ').to_matrix().to_4x4()


def xf(c, rot=None):
    return Matrix.Translation(Vector(c)) @ rotm(rot)


def put(mat, src, M, col=(1, 1, 1), cfn=None, g=2, uvs=None, skip_down=False):
    """copy src bmesh into accumulator of mat, transformed by M. g = grain axis idx for box UV."""
    bm = get_bm(mat)
    cl = bm.loops.layers.float_color['Col']
    ul = bm.loops.layers.uv['UVMap']
    sul = src.loops.layers.uv.active
    src.normal_update()
    vm = {v: bm.verts.new(M @ v.co) for v in src.verts}
    sc = TEXSC.get(mat.name, 1.0) if uvs is None else uvs
    ou, ov = rnd.random(), rnd.random()
    col = C(col)
    upright = (M.to_3x3() @ Vector((0, 0, 1))).z > 0.995
    for f in src.faces:
        if skip_down and upright and f.normal.z < -0.97 and (M @ f.calc_center_median()).z < 1.9:
            continue
        try:
            nf = bm.faces.new([vm[v] for v in f.verts])
        except ValueError:
            continue
        nf.smooth = True
        n = f.normal
        ax = 0 if abs(n.x) >= abs(n.y) and abs(n.x) >= abs(n.z) else (1 if abs(n.y) >= abs(n.z) else 2)
        for ls, l in zip(f.loops, nf.loops):
            co = ls.vert.co
            if sul is not None:
                u, v = ls[sul].uv
            elif ax == g:
                o = [i for i in range(3) if i != g]
                u, v = co[o[0]], co[o[1]]
            else:
                v = co[g]
                u = co[3 - ax - g]
            l[ul].uv = (u * sc + ou, v * sc + ov)
            c = cfn(M @ co) if cfn else col
            l[cl] = (c[0], c[1], c[2], 1.0)


def bev_bm(bm, w):
    if w > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:] + bm.faces[:], offset=w, segments=1, profile=0.5,
                        affect='EDGES', clamp_overlap=True)


def box(mat, c, s, rot=None, bev=0.004, col=(1, 1, 1), cfn=None, g=2, cuts=0, anchor=None, M=None):
    """box centred at c (or, with anchor='b', bottom-centre) size s=(x,y,z)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    if cuts >= 4:
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
    for v in bm.verts:
        v.co.x *= s[0]; v.co.y *= s[1]; v.co.z *= s[2]
        if anchor == 'b':
            v.co.z += s[2] / 2
    bev = min(bev, min(s) * 0.34)
    if min(s) < 0.045:
        bev = 0
    bev_bm(bm, bev)
    put(mat, bm, M if M is not None else xf(c, rot), col, cfn, g, skip_down=True)
    bm.free()


def lathe(mat, c, prof, seg=16, rot=None, col=(1, 1, 1), cfn=None, cap=True, uvm=1.0, g=2, M=None, scale=None):
    """prof: [(r,z),...] bottom->top about local z axis."""
    rmax = max(r for r, z in prof) * (max(scale[0], scale[1]) if scale is not None else 1.0)
    if rmax < 0.05:
        seg = min(seg, 7)
    elif rmax < 0.15:
        seg = min(seg, 10)
    elif rmax < 0.3:
        seg = min(seg, 14)
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    rings = []
    for (r, z) in prof:
        if r < 1e-5:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)])
    for k in range(len(prof) - 1):
        a, b = rings[k], rings[k + 1]
        circ = 2 * math.pi * max(prof[k][0], prof[k + 1][0], 0.01)
        for i in range(seg):
            j = (i + 1) % seg
            if len(a) == 1 and len(b) == 1:
                continue
            if len(a) == 1:
                vs = [a[0], b[j], b[i]]; idx = [(0, i), (1, i + 1), (1, i)]
            elif len(b) == 1:
                vs = [a[i], a[j], b[0]]; idx = [(0, i), (0, i + 1), (1, i)]
            else:
                vs = [a[i], a[j], b[j], b[i]]; idx = [(0, i), (0, i + 1), (1, i + 1), (1, i)]
            try:
                f = bm.faces.new(vs)
            except ValueError:
                continue
            f.smooth = True
            for l, (kk, ii) in zip(f.loops, idx):
                l[ul].uv = (ii / seg * circ * uvm, prof[k + kk][1] * uvm)
    if cap:
        for k, top in ((0, False), (len(prof) - 1, True)):
            if prof[k][0] > 1e-5:
                ring = rings[k]
                try:
                    f = bm.faces.new(ring if top else ring[::-1])
                except ValueError:
                    continue
                for l in f.loops:
                    co = l.vert.co
                    l[ul].uv = (co.x * uvm, co.y * uvm)
    MM = M if M is not None else xf(c, rot)
    if scale is not None:
        MM = MM @ Matrix.Diagonal((scale[0], scale[1], scale[2], 1.0))
    put(mat, bm, MM, col, cfn, g, skip_down=True)
    bm.free()


def cyl(mat, c, r, h, axis='z', seg=14, r2=None, col=(1, 1, 1), cfn=None, cap=True, bev=0.0, rot=None, uvm=1.0, M=None):
    """cylinder centred at c. axis z/x/y."""
    r2 = r if r2 is None else r2
    prof = [(r, -h / 2), (r2, h / 2)]
    if bev > 0:
        b = min(bev, r * 0.5, h * 0.3)
        prof = [(r - b, -h / 2), (r, -h / 2 + b), (r2, h / 2 - b), (r2 - b, h / 2)]
    R = {'z': (0, 0, 0), 'x': (0, 90, 0), 'y': (-90, 0, 0)}[axis]
    lathe(mat, c, prof, seg, col=col, cfn=cfn, cap=cap, uvm=uvm, M=(M if M is not None else xf(c, rot)) @ rotm(R))


def sphere(mat, c, r, seg=14, sq=(1, 1, 1), rot=None, col=(1, 1, 1), cfn=None, rings=8):
    prof = []
    for i in range(rings + 1):
        a = -math.pi / 2 + math.pi * i / rings
        prof.append((max(math.cos(a) * r, 0.0), math.sin(a) * r))
    lathe(mat, c, prof, seg, rot=rot, col=col, cfn=cfn, cap=False, scale=sq)


def tube(mat, pts, r, seg=8, col=(1, 1, 1), cfn=None, caps=True, taper=None, uvm=1.0):
    rr0 = max(r) if isinstance(r, (list, tuple)) else r
    seg = min(seg, 4 if rr0 < 0.004 else (5 if rr0 < 0.008 else (6 if rr0 < 0.02 else 8)))
    """sweep circle radius r (or list / taper fn(t)) along polyline pts (Vectors, world)."""
    pts = [Vector(p) for p in pts]
    n = len(pts)
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    tang = []
    for i in range(n):
        a = pts[max(i - 1, 0)]; b = pts[min(i + 1, n - 1)]
        t = (b - a); t.normalize(); tang.append(t)
    ref = Vector((0, 0, 1)) if abs(tang[0].z) < 0.9 else Vector((1, 0, 0))
    nrm = tang[0].cross(ref).normalized()
    rings = []
    dist = 0.0
    dists = []
    for i in range(n):
        if i > 0:
            dist += (pts[i] - pts[i - 1]).length
        dists.append(dist)
        t = tang[i]
        nrm = (nrm - t * nrm.dot(t)); nrm.normalize()
        bn = t.cross(nrm)
        rr = r[i] if isinstance(r, (list, tuple)) else (r * taper(i / (n - 1)) if taper else r)
        ring = [bm.verts.new(pts[i] + (nrm * math.cos(2 * math.pi * k / seg) + bn * math.sin(2 * math.pi * k / seg)) * rr) for k in range(seg)]
        rings.append(ring)
    for i in range(n - 1):
        for k in range(seg):
            k2 = (k + 1) % seg
            try:
                f = bm.faces.new([rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]])
            except ValueError:
                continue
            f.smooth = True
            for l, (ii, kk) in zip(f.loops, [(i, k), (i, k + 1), (i + 1, k + 1), (i + 1, k)]):
                rr0 = r[0] if isinstance(r, (list, tuple)) else r
                l[ul].uv = (kk / seg * 2 * math.pi * rr0 * uvm, dists[ii] * uvm)
    if caps:
        for ring, rev in ((rings[0], True), (rings[-1], False)):
            try:
                f = bm.faces.new(ring[::-1] if rev else ring)
                for l in f.loops:
                    l[ul].uv = (0, 0)
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    put(mat, bm, Matrix.Identity(4), col, cfn)
    bm.free()


def bez(p0, p1, p2, p3, n=12):
    p0, p1, p2, p3 = [Vector(p) for p in (p0, p1, p2, p3)]
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(p0 * (1 - t) ** 3 + p1 * 3 * t * (1 - t) ** 2 + p2 * 3 * t * t * (1 - t) + p3 * t ** 3)
    return out


def arcpts(c, r, a0, a1, n=12, plane='xy', z=0.0):
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        if plane == 'xy':
            out.append(Vector((c[0] + r * math.cos(a), c[1] + r * math.sin(a), c[2])))
        elif plane == 'xz':
            out.append(Vector((c[0] + r * math.cos(a), c[1], c[2] + r * math.sin(a))))
        else:
            out.append(Vector((c[0], c[1] + r * math.cos(a), c[2] + r * math.sin(a))))
    return out


def cloth(mat, x0, x1, y0, y1, nx, ny, ztop, zbot=None, col=(1, 1, 1), cfn=None, M=None, edge=None, solid=True):
    """slab with top surface height ztop(x,y) (local), flat bottom zbot (or ztop-0.02). Local coords, transformed by M."""
    M = M or Matrix.Identity(4)
    bm = bmesh.new()
    T = [[None] * (ny + 1) for _ in range(nx + 1)]
    B = [[None] * (ny + 1) for _ in range(nx + 1)]
    for i in range(nx + 1):
        for j in range(ny + 1):
            x = x0 + (x1 - x0) * i / nx; y = y0 + (y1 - y0) * j / ny
            zt = ztop(x, y)
            zb = zbot(x, y) if callable(zbot) else (zbot if zbot is not None else zt - 0.02)
            T[i][j] = bm.verts.new((x, y, zt))
            if solid or i in (0, nx) or j in (0, ny):
                B[i][j] = bm.verts.new((x, y, min(zb, zt - 0.004)))
    def q(a, b, c, d):
        try:
            bm.faces.new([a, b, c, d])
        except ValueError:
            pass
    for i in range(nx):
        for j in range(ny):
            q(T[i][j], T[i + 1][j], T[i + 1][j + 1], T[i][j + 1])
            if solid:
                q(B[i][j + 1], B[i + 1][j + 1], B[i + 1][j], B[i][j])
    for i in range(nx):
        q(B[i][0], B[i + 1][0], T[i + 1][0], T[i][0])
        q(T[i][ny], T[i + 1][ny], B[i + 1][ny], B[i][ny])
    for j in range(ny):
        q(T[0][j], T[0][j + 1], B[0][j + 1], B[0][j])
        q(B[nx][j], B[nx][j + 1], T[nx][j + 1], T[nx][j])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    put(mat, bm, M, col, cfn)
    bm.free()


def pillow(mat, c, size, rot=None, n=3.0, res=6, col=(1, 1, 1), cfn=None, flat=0.85, pinch=0.25, noise_amp=0.0, M=None):
    """rounded-box cushion. size=(sx,sy,sz) full dims."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=max(1, res - 5), use_grid_fill=True)
    for v in bm.verts:
        p = v.co.copy()
        L = (abs(p.x) ** n + abs(p.y) ** n + abs(p.z) ** n) ** (1 / n)
        q = p / L if L > 1e-6 else p
        # taper thickness toward edges
        e = max(abs(q.x), abs(q.y))
        zf = 1.0 - flat * (e ** 5) * 0.6
        q.z *= zf
        # centre pinch (button)
        q.z *= 1.0 - pinch * math.exp(-(q.x ** 2 + q.y ** 2) / 0.03) * (1 if q.z > 0 else 1)
        if noise_amp:
            nv = mnoise.noise(Vector((q.x * 2.3 + rnd.random() * 0 + (M.translation.x if M is not None else c[0]) * 7, q.y * 2.3 + (M.translation.y if M is not None else c[1]) * 7, q.z * 2.3)))
            q += q.normalized() * nv * noise_amp
        v.co = Vector((q.x * size[0] / 2, q.y * size[1] / 2, q.z * size[2] / 2))
    put(mat, bm, M if M is not None else xf(c, rot), col, cfn, 2)
    bm.free()


def grid_mesh(mat, x0, x1, y0, y1, nx, ny, fn, col=(1, 1, 1), cfn=None, M=None, double=False):
    """single-sided surface z=fn(x,y) in local coords (facing +z)."""
    M = M or Matrix.Identity(4)
    bm = bmesh.new()
    V = [[bm.verts.new((x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny, fn(x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny))) for j in range(ny + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(ny):
            try:
                bm.faces.new([V[i][j], V[i + 1][j], V[i + 1][j + 1], V[i][j + 1]])
            except ValueError:
                pass
    put(mat, bm, M, col, cfn)
    bm.free()


def nz(x, y, z=0.0, s=1.0, seed=0):
    return mnoise.noise(Vector((x * s + seed * 13.1, y * s + seed * 7.7, z * s)))


def fbm(x, y, z=0.0, s=1.0, seed=0, o=3):
    a, t, f = 1.0, 0.0, 1.0
    for _ in range(o):
        t += a * nz(x, y, z, s * f, seed)
        a *= 0.5; f *= 2.1
    return t


def jit(c, a=0.06):
    """colour multiplier jitter."""
    k = 1 + rnd.uniform(-a, a)
    return (c[0] * k, c[1] * k, c[2] * k)


def shade(c, k):
    return (c[0] * k, c[1] * k, c[2] * k)


def woodcol(base=(1, 1, 1), amp=0.10, s=6.0, seed=0, axis=2):
    def f(p):
        t = fbm(p.x * (1 if axis != 0 else 0.15), p.y * (1 if axis != 1 else 0.15), p.z * (1 if axis != 2 else 0.15), s, seed, 2)
        k = 1 + amp * t
        return (base[0] * k, base[1] * k, base[2] * k)
    return f


def collider(x0, x1, y0, y1, top, bottom=0.30):
    COLL.append({'cx': round((x0 + x1) / 2, 3), 'cz': round(-(y0 + y1) / 2, 3), 'hx': round(abs(x1 - x0) / 2, 3),
                 'hz': round(abs(y1 - y0) / 2, 3), 'top': round(top, 3), 'bottom': bottom})


def light(name, pos, color=(1.0, 0.7, 0.4), intensity=1.0, distance=6.0):
    """pos in BLENDER coords"""
    LIGHTS.append({'name': name, 'pos': [round(pos[0], 3), round(pos[2], 3), round(-pos[1], 3)], 'color': list(color),
                   'intensity': intensity, 'distance': distance})


def interact(name, pos, label):
    INTER.append({'name': name, 'pos': [round(pos[0], 3), round(pos[2], 3), round(-pos[1], 3)], 'label': label})


SHARP = {'food_vc': 75, 'herb_vc': 80, 'fabric_vc': 55, 'curtain_vc': 85, 'knit_vc': 60, 'fur': 75, 'ceramic_vc': 55,
         'ceramic_white': 55, 'glass': 60, 'glass_amber': 60, 'wax': 70, 'rope': 60, 'sack': 65, 'wicker': 65, 'copper': 55,
         'brass': 48, 'pewter': 55, 'water': 90, 'log_bark': 65, 'leather_vc': 55, 'iron_cast': 45, 'tin': 55, 'terracotta': 65,
         'canvas_vc': 90, 'paint_vc': 90, 'paper': 90, 'straw': 75, 'flame': 90, 'mirror': 90, 'enamel_white': 40}


def finalize(sharp_deg=32, names=None):
    """convert accumulators into objects"""
    objs = []
    for mn, (bm, mat) in ACC.items():
        bm.normal_update()
        for e in bm.edges:
            if len(e.link_faces) == 2:
                try:
                    if e.calc_face_angle(0.0) > math.radians(SHARP.get(mn, sharp_deg)):
                        e.smooth = False
                except Exception:
                    pass
        me = bpy.data.meshes.new('static_' + mn)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new('static_' + mn, me)
        bpy.context.scene.collection.objects.link(ob)
        ob.data.materials.append(mat)
        objs.append(ob)
    return objs


def part_begin():
    """redirect accumulation into a fresh dict so a separate object can be made."""
    global ACC
    saved = ACC
    ACC = {}
    return saved


def part_end(saved, name, pivot, parent=None):
    global ACC
    made = []
    for mn, (bm, mat) in ACC.items():
        bm.normal_update()
        for e in bm.edges:
            if len(e.link_faces) == 2:
                try:
                    if e.calc_face_angle(0.0) > math.radians(SHARP.get(mn, 32)):
                        e.smooth = False
                except Exception:
                    pass
        me = bpy.data.meshes.new(name + '_m')
        bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        ob.data.materials.append(mat)
        ob.location = (0, 0, 0)
        made.append(ob)
    ACC = saved
    ob = made[0]
    for o in made[1:]:
        # several materials: join into first
        with bpy.context.temp_override(active_object=ob, selected_editable_objects=[ob, o], object=ob):
            bpy.ops.object.join()
    bpy.context.view_layer.update()
    set_origin(ob, pivot)
    PARTS.append(ob)
    return ob


class Fr:
    """local frame: pos = origin (world), rot = z rotation degrees. local coords (x,y,z)."""
    def __init__(s, pos, rot=0.0, z=None):
        p = Vector((pos[0], pos[1], pos[2] if len(pos) > 2 else 0.0))
        if z is not None:
            p.z = z
        s.pos = p
        s.rot = rot
        s.M = xf(p, (0, 0, rot))

    def p(s, l):
        return s.M @ Vector(l)

    def _m(s, c, r=None):
        return s.M @ Matrix.Translation(Vector(c)) @ rotm(r)

    def box(s, mat, c, size, r=None, **kw):
        box(mat, None, size, M=s._m(c, r), **kw)

    def cyl(s, mat, c, rad, h, axis='z', r=None, **kw):
        cyl(mat, None, rad, h, axis=axis, M=s._m(c, r), **kw)

    def lathe(s, mat, c, prof, r=None, **kw):
        lathe(mat, None, prof, M=s._m(c, r), **kw)

    def pillow(s, mat, c, size, r=None, **kw):
        pillow(mat, None, size, M=s._m(c, r), **kw)

    def tube(s, mat, pts, rad, **kw):
        tube(mat, [s.p(q) for q in pts], rad, **kw)

    def cloth(s, mat, *a, **kw):
        kw['M'] = s.M @ (kw.get('M') or Matrix.Identity(4))
        cloth(mat, *a, **kw)


def chain(x, y, z0, z1, mat, r=0.0035):
    """simple chain: thin tube with a few bead links"""
    tube(mat, [Vector((x, y, z0)), Vector((x, y, z1))], r, seg=4, caps=False)
    n = int(abs(z1 - z0) / 0.06)
    for i in range(n):
        sphere(mat, Vector((x, y, min(z0, z1) + 0.03 + i * 0.06)), r * 2.2, seg=5, rings=3, sq=(1, 0.6, 1.3))
