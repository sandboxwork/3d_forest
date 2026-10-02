"""bd_lib: geometry toolkit for the bedroom / entryway / decor upgrade (copy+extension of int_lib).
Everything accumulates into per-material bmeshes in WORLD (house-local, Blender Z-up) coordinates.
UV convention: 1 UV unit = one texture tile; TEXSC[mat] = 1 / tile_size_in_meters. Wood grain runs along U
(pbr_wood_* images have horizontal grain), so wood boxes map  u = distance along grain, v = across.
"""
import sys, math, random, os, json
sys.path.insert(0, '/shared/river/assets/blender')
from bl_common import *
from mathutils import noise as mnoise, Euler
from mathutils.bvhtree import BVHTree

F = 0.30          # finished floor z
TAU = 2 * math.pi
ACC = {}          # matname -> (bm, mat)
TEXSC = {}        # matname -> uv per meter
LIGHTS, COLL, INTER = [], [], []
PARTS = []        # separate objects (animated parts)
M = {}            # materials by short name
rnd = random.Random(11)
GRAIN_U = True
PROF = {}
AMIN = 0.03
QUAL = 0.62        # global tessellation scale (triangle budget)
WOODS = set()     # material names whose grain direction matters (U along grain)
SOLID = []        # (bm-free) occluders registered for AO / cloth collision: list of objects
V = lambda *a: Vector(a)


def C(c):
    if isinstance(c, str):
        return tuple(hex_rgb(c))
    return tuple(c)


def MAT(name, color='#ffffff', tex=None, tile=None, **kw):
    m = make_mat(name, color, tex=tex, **kw)
    TEXSC[name] = (1.0 / tile) if tile else 1.0
    if tex and tex.startswith('pbr_wood'):
        WOODS.add(name)
    M[name] = m
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


def put(mat, src, Mx, col=(1, 1, 1), cfn=None, g=None, uvs=None, skip_down=True, uvfix=None, smooth=True):
    """Copy src bmesh into accumulator of mat, transformed by Mx.
    g: grain axis (0/1/2 local) or None -> auto (longest bbox dimension). UV from src if it has a UV layer else box-mapped."""
    bm = get_bm(mat)
    cl = bm.loops.layers.float_color['Col']
    ul = bm.loops.layers.uv['UVMap']
    sul = src.loops.layers.uv.active
    scl = src.loops.layers.float_color.get('Col') if hasattr(src.loops.layers, 'float_color') else None
    src.normal_update()
    vm = {v: bm.verts.new(Mx @ v.co) for v in src.verts}
    if uvs is None:
        sc = TEXSC.get(mat.name, 1.0)
    else:
        sc = uvs
    ou, ov = (rnd.random(), rnd.random()) if sc != 1.0 or uvs is None else (0.0, 0.0)
    if uvs == 1.0 or mat.name == 'quilt' or mat.name.startswith('bd_painting'):
        ou = ov = 0.0
    col = C(col)
    upright = (Mx.to_3x3() @ Vector((0, 0, 1))).z > 0.995
    if g is None:
        mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
        for v in src.verts:
            for i in range(3):
                mn[i] = min(mn[i], v.co[i]); mx[i] = max(mx[i], v.co[i])
        d = mx - mn
        g = max(range(3), key=lambda i: d[i])
    wood = mat.name in WOODS
    try:
        fr_ = sys._getframe(1)
        while fr_ and fr_.f_code.co_filename.endswith('bd_lib.py'):
            fr_ = fr_.f_back
        key_ = '%s:%s' % (os.path.basename(fr_.f_code.co_filename)[:-3], fr_.f_code.co_name)
        PROF[key_] = PROF.get(key_, 0) + sum(len(ff.verts) - 2 for ff in src.faces)
    except Exception:
        pass
    for f in src.faces:
        if skip_down and upright and f.normal.z < -0.97 and (Mx @ f.calc_center_median()).z < 1.5:
            continue
        try:
            nf = bm.faces.new([vm[v] for v in f.verts])
        except ValueError:
            continue
        nf.smooth = smooth
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
                a_ = co[g]
                b_ = co[3 - ax - g]
                if GRAIN_U and wood:
                    u, v = a_, b_
                else:
                    u, v = b_, a_
            l[ul].uv = (u * sc + ou, v * sc + ov)
            if cfn:
                c = cfn(Mx @ co)
            elif scl is not None:
                c = tuple(ls[scl][:3])
                c = (c[0] * col[0], c[1] * col[1], c[2] * col[2])
            else:
                c = col
            l[cl] = (c[0], c[1], c[2], 1.0)
    return bm


def bev_bm(bm, w, seg=1):
    if w > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:] + bm.faces[:], offset=w, segments=seg, profile=0.5,
                        affect='EDGES', clamp_overlap=True)


def box(mat, c, s, rot=None, bev=0.004, col=(1, 1, 1), cfn=None, g=None, anchor=None, Mx=None, seg=None, skip_down=True):
    """box centred at c (or with anchor='b' bottom-centre) size s=(x,y,z)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= s[0]; v.co.y *= s[1]; v.co.z *= s[2]
        if anchor == 'b':
            v.co.z += s[2] / 2
    bev = min(bev, min(s) * 0.34)
    if min(s) < 0.012:
        bev = 0
    if seg is None:
        seg = 2 if bev >= 0.012 else 1
    bev_bm(bm, bev, seg)
    put(mat, bm, Mx if Mx is not None else xf(c, rot), col, cfn, g, skip_down=skip_down)
    bm.free()


def profile_pts(pts, n=6):
    """Catmull-Rom smoothing of a list of (r,z) key points -> denser polyline."""
    n = max(1, int(round(n * 0.6)))
    P = [Vector((p[0], p[1], 0)) for p in pts]
    out = []
    for i in range(len(P) - 1):
        p0 = P[max(i - 1, 0)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(i + 2, len(P) - 1)]
        for k in range(n):
            t = k / n
            a = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
            out.append((max(a.x, 0.0), a.y))
    out.append((max(P[-1].x, 0.0), P[-1].y))
    return out


def lathe(mat, c, prof, seg=None, rot=None, col=(1, 1, 1), cfn=None, cap=True, uvm=1.0, g=None, Mx=None, scale=None, smooth=True, noise=0.0, ret=False):
    """prof: [(r,z),...] bottom->top about local z axis. seg None -> automatic from radius."""
    prof = list(prof)
    imax = max(range(len(prof)), key=lambda i: prof[i][0])
    a_, b_ = prof[max(imax - 1, 0)], prof[min(imax + 1, len(prof) - 1)]
    if (b_[1] - a_[1]) < -1e-6:      # outermost point traversed downward -> outside is on the left -> flip so normals point outward
        prof = prof[::-1]
    rmax = max(r for r, z in prof) * (max(scale[0], scale[1]) if scale is not None else 1.0)
    if seg is None:
        seg = 6 if rmax < 0.008 else 8 if rmax < 0.02 else 12 if rmax < 0.05 else 16 if rmax < 0.12 else 24 if rmax < 0.4 else 32
    else:
        seg = max(6, 2 * int(round(seg * QUAL / 2)))
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    rings = []
    for (r, z) in prof:
        if r < 1e-5:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(TAU * i / seg), r * math.sin(TAU * i / seg), z)) for i in range(seg)])
    arc = [0.0]
    for k in range(1, len(prof)):
        arc.append(arc[-1] + math.hypot(prof[k][0] - prof[k - 1][0], prof[k][1] - prof[k - 1][1]))
    for k in range(len(prof) - 1):
        a, b = rings[k], rings[k + 1]
        circ = TAU * max(prof[k][0], prof[k + 1][0], 0.01)
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
            f.smooth = smooth
            for l, (kk, ii) in zip(f.loops, idx):
                l[ul].uv = (ii / seg * circ * uvm, arc[k + kk] * uvm)
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
    if noise:
        for v in bm.verts:
            v.co += Vector((nz(v.co.x, v.co.y, v.co.z, 40, 1), nz(v.co.x, v.co.y, v.co.z, 40, 2), nz(v.co.x, v.co.y, v.co.z, 40, 3))) * noise
    if ret:
        return bm
    MM = Mx if Mx is not None else xf(c, rot)
    if scale is not None:
        MM = MM @ Matrix.Diagonal((scale[0], scale[1], scale[2], 1.0))
    put(mat, bm, MM, col, cfn, g, smooth=smooth)
    bm.free()


def cyl(mat, c, r, h, axis='z', seg=None, r2=None, col=(1, 1, 1), cfn=None, cap=True, bev=0.0, rot=None, uvm=1.0, Mx=None):
    r2 = r if r2 is None else r2
    prof = [(r, -h / 2), (r2, h / 2)]
    if bev > 0:
        b = min(bev, r * 0.5, h * 0.3)
        prof = [(r - b, -h / 2), (r, -h / 2 + b), (r2, h / 2 - b), (r2 - b, h / 2)]
    R = {'z': (0, 0, 0), 'x': (0, 90, 0), 'y': (-90, 0, 0)}[axis]
    lathe(mat, c, prof, seg, col=col, cfn=cfn, cap=cap, uvm=uvm, Mx=(Mx if Mx is not None else xf(c, rot)) @ rotm(R))


def sphere(mat, c, r, seg=None, sq=(1, 1, 1), rot=None, col=(1, 1, 1), cfn=None, rings=None, Mx=None, noise=0.0):
    if seg is None:
        seg = 8 if r < 0.01 else 12 if r < 0.04 else 16 if r < 0.1 else 24
    else:
        seg = max(6, int(round(seg * 0.7)))
    if rings is None:
        rings = max(3, seg // 2)
    prof = []
    for i in range(rings + 1):
        a = -math.pi / 2 + math.pi * i / rings
        prof.append((max(math.cos(a) * r, 0.0), math.sin(a) * r))
    lathe(mat, c, prof, seg, rot=rot, col=col, cfn=cfn, cap=False, scale=sq, Mx=Mx, noise=noise)


def tube(mat, pts, r, seg=None, col=(1, 1, 1), cfn=None, caps=True, taper=None, uvm=1.0, flat=None, closed=False):
    """sweep circle radius r (number, list, or taper fn) along polyline pts. flat=(a,b) elliptical section scale."""
    pts = [Vector(p) for p in pts]
    n = len(pts)
    rr0 = max(r) if isinstance(r, (list, tuple)) else r
    if seg is None:
        seg = 5 if rr0 < 0.004 else 6 if rr0 < 0.008 else 8 if rr0 < 0.02 else 12
    else:
        seg = max(4 if rr0 < 0.006 else 5, int(round(seg * 0.75)))
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    tang = []
    for i in range(n):
        if closed:
            a = pts[(i - 1) % n]; b = pts[(i + 1) % n]
        else:
            a = pts[max(i - 1, 0)]; b = pts[min(i + 1, n - 1)]
        t = (b - a)
        if t.length < 1e-9:
            t = Vector((1, 0, 0))
        t.normalize(); tang.append(t)
    ref = Vector((0, 0, 1)) if abs(tang[0].z) < 0.9 else Vector((1, 0, 0))
    nrm = tang[0].cross(ref).normalized()
    rings, dists = [], []
    dist = 0.0
    for i in range(n):
        if i > 0:
            dist += (pts[i] - pts[i - 1]).length
        dists.append(dist)
        t = tang[i]
        nrm = (nrm - t * nrm.dot(t))
        if nrm.length < 1e-6:
            nrm = t.cross(Vector((0, 0, 1)))
        nrm.normalize()
        bn = t.cross(nrm)
        rr = r[i] if isinstance(r, (list, tuple)) else (r * taper(i / max(n - 1, 1)) if taper else r)
        fa, fb = flat if flat else (1.0, 1.0)
        ring = [bm.verts.new(pts[i] + (nrm * math.cos(TAU * k / seg) * fa + bn * math.sin(TAU * k / seg) * fb) * rr) for k in range(seg)]
        rings.append(ring)
    rng_ = range(n if closed else n - 1)
    for i in rng_:
        i2 = (i + 1) % n
        for k in range(seg):
            k2 = (k + 1) % seg
            try:
                f = bm.faces.new([rings[i][k], rings[i][k2], rings[i2][k2], rings[i2][k]])
            except ValueError:
                continue
            f.smooth = True
            rr0_ = r[0] if isinstance(r, (list, tuple)) else r
            d0 = dists[i]; d1 = dists[i + 1] if i + 1 < n else d0 + (pts[0] - pts[-1]).length
            for l, (dd, kk) in zip(f.loops, [(d0, k), (d0, k + 1), (d1, k + 1), (d1, k)]):
                l[ul].uv = (kk / seg * TAU * rr0_ * uvm, dd * uvm)
    if caps and not closed:
        for ring, rev in ((rings[0], True), (rings[-1], False)):
            try:
                f = bm.faces.new(ring[::-1] if rev else ring)
                for l in f.loops:
                    l[ul].uv = (0, 0)
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    put(mat, bm, Matrix.Identity(4), col, cfn, g=0)
    bm.free()


def bez(p0, p1, p2, p3, n=12):
    p0, p1, p2, p3 = [Vector(p) for p in (p0, p1, p2, p3)]
    return [p0 * (1 - t) ** 3 + p1 * 3 * t * (1 - t) ** 2 + p2 * 3 * t * t * (1 - t) + p3 * t ** 3 for t in [i / n for i in range(n + 1)]]


def catmull(pts, n=6, closed=False):
    P = [Vector(p) for p in pts]
    m = len(P)
    out = []
    rng_ = range(m) if closed else range(m - 1)
    for i in rng_:
        p0 = P[(i - 1) % m] if closed else P[max(i - 1, 0)]
        p1 = P[i]; p2 = P[(i + 1) % m]
        p3 = P[(i + 2) % m] if closed else P[min(i + 2, m - 1)]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    if not closed:
        out.append(P[-1])
    return out


def arcpts(c, r, a0, a1, n=12, plane='xy'):
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


def torus(mat, c, R, r, plane='xy', rot=None, seg=24, rseg=8, col=(1, 1, 1), a0=0, a1=360, Mx=None):
    seg = max(8, int(seg * 0.7)); rseg = max(4, int(rseg * 0.7))
    n = max(int((a1 - a0) / 360 * seg), 3)
    pts = arcpts((0, 0, 0), R, a0, a1, n, plane)
    M_ = Mx if Mx is not None else xf(c, rot)
    tube(mat, [M_ @ p for p in pts], r, seg=rseg, col=col, caps=(a1 - a0) < 360, closed=(a1 - a0) >= 360 - 1e-6)


def poly_prism(mat, pts2d, thick, Mx, col=(1, 1, 1), bev=0.0, cfn=None, g=None, plane='xz', skip_down=True, seg=1):
    """extrude a 2D polygon (list of (a,b)) by thick, centred. plane 'xz': polygon in local x,z, thickness along y;
    'xy': polygon in x,y thickness along z; 'yz': y,z thick along x."""
    bm = bmesh.new()
    def P(a, b, t):
        return {'xz': (a, t, b), 'xy': (a, b, t), 'yz': (t, a, b)}[plane]
    vb = [bm.verts.new(P(a, b, -thick / 2)) for a, b in pts2d]
    vt = [bm.verts.new(P(a, b, thick / 2)) for a, b in pts2d]
    try:
        bm.faces.new(vb[::-1]); bm.faces.new(vt)
    except ValueError:
        pass
    n = len(pts2d)
    for i in range(n):
        j = (i + 1) % n
        try:
            bm.faces.new([vb[i], vb[j], vt[j], vt[i]])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if bev > 0:
        bev_bm(bm, min(bev, thick * 0.4), seg)
    put(mat, bm, Mx, col, cfn, g, skip_down=skip_down)
    bm.free()


def modmesh(bm, mods, extra_objs=None):
    """Apply Blender modifiers to a bmesh via a temp object. mods: [(TYPE, {prop: value}), ...]. Returns a NEW bmesh (src untouched)."""
    me = bpy.data.meshes.new('_tmp')
    bm.to_mesh(me)
    ob = bpy.data.objects.new('_tmp', me)
    bpy.context.scene.collection.objects.link(ob)
    for typ, props in mods:
        m = ob.modifiers.new(typ.title(), typ)
        for k, v in props.items():
            setattr(m, k, v)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me2 = bpy.data.meshes.new_from_object(ev, depsgraph=dg)
    out = bmesh.new()
    out.from_mesh(me2)
    bpy.data.objects.remove(ob)
    bpy.data.meshes.remove(me)
    bpy.data.meshes.remove(me2)
    return out


def bm_box(sx, sy, sz, cuts=0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= sx; v.co.y *= sy; v.co.z *= sz
    return bm


def nz(x, y, z=0.0, s=1.0, seed=0):
    return mnoise.noise(Vector((x * s + seed * 13.1, y * s + seed * 7.7, z * s)))


def fbm(x, y, z=0.0, s=1.0, seed=0, o=3):
    a, t, f = 1.0, 0.0, 1.0
    for _ in range(o):
        t += a * nz(x, y, z, s * f, seed)
        a *= 0.5; f *= 2.1
    return t


def jit(c, a=0.06):
    k = 1 + rnd.uniform(-a, a)
    return (c[0] * k, c[1] * k, c[2] * k)


def shade(c, k):
    return (c[0] * k, c[1] * k, c[2] * k)


def mulc(a, b):
    return (a[0] * b[0], a[1] * b[1], a[2] * b[2])


def woodcol(base=(1, 1, 1), amp=0.10, s=6.0, seed=0):
    def f(p):
        t = fbm(p.x * 0.4, p.y * 0.4, p.z, s, seed, 2)
        k = 1 + amp * t
        return (base[0] * k, base[1] * k, base[2] * k)
    return f


def fab(base, amp=0.07, s=9.0, seed=0):
    def f(p):
        k = 1 + amp * fbm(p.x, p.y, p.z, s, seed, 2)
        return (base[0] * k, base[1] * k, base[2] * k)
    return f


def collider(x0, x1, y0, y1, top, bottom=0.30):
    COLL.append({'cx': round((x0 + x1) / 2, 3), 'cz': round(-(y0 + y1) / 2, 3), 'hx': round(abs(x1 - x0) / 2, 3),
                 'hz': round(abs(y1 - y0) / 2, 3), 'top': round(top, 3), 'bottom': bottom})


def collider_f(f, W, D, top, off=(0, 0), name=None):
    a = math.radians(f.rot)
    cx, cy = f.p((off[0], off[1], 0))[:2]
    hx = abs(W / 2 * math.cos(a)) + abs(D / 2 * math.sin(a))
    hy = abs(W / 2 * math.sin(a)) + abs(D / 2 * math.cos(a))
    collider(cx - hx, cx + hx, cy - hy, cy + hy, top)
    if name:
        COLL[-1]['name'] = name


def light(name, pos, color=(1.0, 0.7, 0.4), intensity=1.0, distance=6.0):
    LIGHTS.append({'name': name, 'pos': [round(pos[0], 3), round(pos[2], 3), round(-pos[1], 3)], 'color': list(color),
                   'intensity': intensity, 'distance': distance})


def interact(name, pos, label):
    INTER.append({'name': name, 'pos': [round(pos[0], 3), round(pos[2], 3), round(-pos[1], 3)], 'label': label})


SHARP = {'linen': 70, 'linen_curtain': 85, 'wool': 70, 'burlap': 70, 'quilt': 85, 'glass': 60, 'glass_amber': 60, 'wax': 70,
         'leaf': 80, 'petal': 85, 'water': 90, 'brass': 40, 'copper': 40, 'iron': 40, 'paper': 90, 'flame': 90, 'mirror': 90,
         'ceramic': 50, 'leather': 55, 'rug': 70, 'soil': 80, 'straw': 80, 'book_cloth': 40, 'wicker': 65, 'paint': 45}


def fix_inverted(bm):
    """flip closed shells whose signed volume is negative (inside-out lathe/box/tube results)"""
    bm.faces.ensure_lookup_table()
    seen = set()
    n_flipped = 0
    for f in list(bm.faces):
        if f.index in seen:
            continue
        stack = [f]; seen.add(f.index); isl = []
        while stack:
            c = stack.pop(); isl.append(c)
            for e in c.edges:
                for g in e.link_faces:
                    if g.index not in seen:
                        seen.add(g.index); stack.append(g)
        if not all(len(e.link_faces) == 2 for ff in isl for e in ff.edges):
            continue
        vol = 0.0
        for ff in isl:
            vs = [v.co for v in ff.verts]
            for k in range(1, len(vs) - 1):
                vol += vs[0].dot(vs[k].cross(vs[k + 1])) / 6.0
        if vol < 0:
            for ff in isl:
                ff.normal_flip()
            n_flipped += 1
    return n_flipped


def split_long_edges(bm, L, amin=0.0):
    """subdivide edges longer than L that belong to faces larger than amin (m^2) -- more vertices for per-vertex AO on big flat panels"""
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
    for it in range(5):
        bm.faces.ensure_lookup_table()
        sel = set()
        for fc in bm.faces:
            if fc.calc_area() > amin:
                for e in fc.edges:
                    if (e.verts[0].co - e.verts[1].co).length > L:
                        sel.add(e)
        if not sel:
            break
        bmesh.ops.subdivide_edges(bm, edges=list(sel), cuts=1, use_grid_fill=False, use_single_edge=False)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method='BEAUTY', ngon_method='BEAUTY')


def finalize(sharp_deg=32, subdiv=None):
    """convert accumulators into objects (static_<mat>)."""
    objs = []
    for mn, (bm, mat) in list(ACC.items()):
        fix_inverted(bm)
        bm.normal_update()
        for e in bm.edges:
            if len(e.link_faces) == 2:
                try:
                    if e.calc_face_angle(0.0) > math.radians(SHARP.get(mn, sharp_deg)):
                        e.smooth = False
                except Exception:
                    pass
        Ls = subdiv.get(mn) if isinstance(subdiv, dict) else subdiv
        if Ls:
            split_long_edges(bm, Ls, AMIN)
        me = bpy.data.meshes.new('static_' + mn)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new('static_' + mn, me)
        bpy.context.scene.collection.objects.link(ob)
        ob.data.materials.append(mat)
        objs.append(ob)
    ACC.clear()
    return objs


def part_begin():
    global ACC
    saved = ACC
    ACC = {}
    return saved


def part_end(saved, name, pivot, subdiv=None):
    """turn current ACC into one object `name` with origin at pivot (multi-material). Restores previous ACC."""
    global ACC
    made = []
    for mn, (bm, mat) in ACC.items():
        fix_inverted(bm)
        bm.normal_update()
        for e in bm.edges:
            if len(e.link_faces) == 2:
                try:
                    if e.calc_face_angle(0.0) > math.radians(SHARP.get(mn, 32)):
                        e.smooth = False
                except Exception:
                    pass
        if subdiv:
            split_long_edges(bm, subdiv)
        me = bpy.data.meshes.new(name + '_' + mn)
        bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new(name + '_' + mn, me)
        bpy.context.scene.collection.objects.link(ob)
        ob.data.materials.append(mat)
        made.append(ob)
    ACC = saved
    if not made:
        return None
    ob = made[0]
    if len(made) > 1:
        # join (retain separate material slots)
        for o in made:
            o.select_set(False)
        for o in made:
            o.select_set(True)
        bpy.context.view_layer.objects.active = ob
        with bpy.context.temp_override(active_object=ob, selected_editable_objects=made, object=ob):
            bpy.ops.object.join()
    ob.name = name
    ob.data.name = name
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
        box(mat, None, size, Mx=s._m(c, r), **kw)

    def cyl(s, mat, c, rad, h, axis='z', r=None, **kw):
        cyl(mat, None, rad, h, axis=axis, Mx=s._m(c, r), **kw)

    def lathe(s, mat, c, prof, r=None, **kw):
        lathe(mat, None, prof, Mx=s._m(c, r), **kw)

    def sphere(s, mat, c, rad, r=None, **kw):
        sphere(mat, None, rad, Mx=s._m(c, r), **kw)

    def tube(s, mat, pts, rad, **kw):
        tube(mat, [s.p(q) for q in pts], rad, **kw)

    def torus(s, mat, c, R, rad, plane='xy', r=None, **kw):
        torus(mat, None, R, rad, plane, Mx=s._m(c, r), **kw)

    def prism(s, mat, pts2d, thick, c=(0, 0, 0), r=None, **kw):
        poly_prism(mat, pts2d, thick, s._m(c, r), **kw)

    def put(s, mat, bm, c=(0, 0, 0), r=None, **kw):
        put(mat, bm, s._m(c, r), **kw)


# ---------------------------------------------------------------- surface sampling (for placing things on cloth etc.)
class Surf:
    def __init__(s, objs):
        """BVH over evaluated world-space meshes (list of bpy objects)"""
        verts, tris = [], []
        dg = bpy.context.evaluated_depsgraph_get()
        for o in objs:
            ev = o.evaluated_get(dg)
            me = ev.to_mesh()
            base = len(verts)
            verts += [o.matrix_world @ v.co for v in me.vertices]
            me.calc_loop_triangles()
            tris += [tuple(base + i for i in t.vertices) for t in me.loop_triangles]
            ev.to_mesh_clear()
        s.bvh = BVHTree.FromPolygons(verts, tris)

    def z(s, x, y, z0=5.0):
        h = s.bvh.ray_cast(Vector((x, y, z0)), Vector((0, 0, -1)))
        return h[0].z if h[0] else None

    def hit(s, x, y, z0=5.0):
        h = s.bvh.ray_cast(Vector((x, y, z0)), Vector((0, 0, -1)))
        return (h[0], h[1]) if h[0] else (None, None)

    def near(s, p, d=0.3):
        r = s.bvh.find_nearest(Vector(p), d)
        return (r[0], r[1]) if r[0] else (None, None)


def mesh_obj_from_arrays(name, verts, faces, uv=None, colattr=None, mat=None, link=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.update()
    ob = bpy.data.objects.new(name, me)
    if link:
        bpy.context.scene.collection.objects.link(ob)
    if mat:
        me.materials.append(mat)
    return ob


def bm_from_obj(ob, apply_world=True):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev, depsgraph=dg)
    bm = bmesh.new(); bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    if apply_world:
        bmesh.ops.transform(bm, matrix=ob.matrix_world, verts=bm.verts)
    return bm


def surf_arrays(verts, faces):
    """BVH from numpy arrays (local coords) -> object with z()/hit()"""
    class S_:
        pass
    o = S_()
    o.bvh = BVHTree.FromPolygons([tuple(v) for v in verts], [tuple(f) for f in faces])
    def z(x, y, z0=5.0):
        h = o.bvh.ray_cast(Vector((x, y, z0)), Vector((0, 0, -1)))
        return h[0].z if h[0] else None
    def hit(x, y, z0=5.0, d=(0, 0, -1)):
        h = o.bvh.ray_cast(Vector((x, y, z0)), Vector(d))
        return (h[0], h[1]) if h[0] else (None, None)
    o.z = z; o.hit = hit
    return o


def gn_leaves(vines, leaf_bm, spacing=0.07, s0=1.0, s1=0.5, seed=0, roll=True):
    """Geometry-nodes leaf scatter: instance `leaf_bm` (leaf pointing +Z, base at origin) along polylines `vines`
    (list of point lists, world/local coords) -> returns realised bmesh. Rotation follows the curve tangent with a random roll."""
    cu = bpy.data.curves.new('_vine', 'CURVE'); cu.dimensions = '3D'
    for pts in vines:
        sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
        for i, p in enumerate(pts):
            sp.points[i].co = (p[0], p[1], p[2], 1.0)
    co = bpy.data.objects.new('_vine', cu); bpy.context.scene.collection.objects.link(co)
    me = bpy.data.meshes.new('_leaf'); leaf_bm.to_mesh(me)
    lo = bpy.data.objects.new('_leaf', me); bpy.context.scene.collection.objects.link(lo)
    ng = bpy.data.node_groups.new('LeavesGN', 'GeometryNodeTree')
    ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    n = ng.nodes; L = ng.links
    gi = n.new('NodeGroupInput'); go = n.new('NodeGroupOutput')
    rs = n.new('GeometryNodeResampleCurve'); rs.inputs['Mode'].default_value = 'Length'; rs.inputs['Length'].default_value = spacing
    tan = n.new('GeometryNodeInputTangent')
    ob = n.new('GeometryNodeObjectInfo'); ob.inputs['Object'].default_value = lo
    iop = n.new('GeometryNodeInstanceOnPoints')
    al = n.new('FunctionNodeAlignRotationToVector')
    sparam = n.new('GeometryNodeSplineParameter')
    mr = n.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = s0; mr.inputs['To Max'].default_value = s1
    cx = n.new('ShaderNodeCombineXYZ')
    rnd_s = n.new('FunctionNodeRandomValue'); rnd_s.data_type = 'FLOAT'; rnd_s.inputs['Min'].default_value = 0.8; rnd_s.inputs['Max'].default_value = 1.2
    rnd_s.inputs['Seed'].default_value = seed
    mul = n.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
    rnd_r = n.new('FunctionNodeRandomValue'); rnd_r.data_type = 'FLOAT'; rnd_r.inputs['Min'].default_value = 0.0; rnd_r.inputs['Max'].default_value = 6.283
    rnd_r.inputs['Seed'].default_value = seed + 7
    cz = n.new('ShaderNodeCombineXYZ')
    rot = n.new('GeometryNodeRotateInstances')
    rl = n.new('GeometryNodeRealizeInstances')
    L.new(gi.outputs[0], rs.inputs['Curve'])
    L.new(rs.outputs['Curve'], iop.inputs['Points'])
    L.new(ob.outputs['Geometry'], iop.inputs['Instance'])
    L.new(tan.outputs[0], al.inputs['Vector'])
    L.new(al.outputs[0], iop.inputs['Rotation'])
    L.new(sparam.outputs['Factor'], mr.inputs['Value'])
    L.new(mr.outputs['Result'], mul.inputs[0]); L.new(rnd_s.outputs['Value'], mul.inputs[1])
    L.new(mul.outputs[0], cx.inputs['X']); L.new(mul.outputs[0], cx.inputs['Y']); L.new(mul.outputs[0], cx.inputs['Z'])
    L.new(cx.outputs[0], iop.inputs['Scale'])
    L.new(iop.outputs['Instances'], rot.inputs['Instances'])
    if roll:
        L.new(rnd_r.outputs['Value'], cz.inputs['Z'])
        L.new(cz.outputs[0], rot.inputs['Rotation'])
    L.new(rot.outputs['Instances'], rl.inputs['Geometry']); L.new(rl.outputs[0], go.inputs[0])
    m = co.modifiers.new('GN', 'NODES'); m.node_group = ng
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); ev = co.evaluated_get(dg)
    me2 = bpy.data.meshes.new_from_object(ev, depsgraph=dg)
    out = bmesh.new(); out.from_mesh(me2)
    bpy.data.objects.remove(co); bpy.data.objects.remove(lo)
    bpy.data.meshes.remove(me); bpy.data.meshes.remove(me2); bpy.data.curves.remove(cu); bpy.data.node_groups.remove(ng)
    return out


def leaf_bm(L=0.06, W=0.035, curl=0.25, heart=True, stem=0.012, n=4, seed=0, col_base=(0.5, 0.65, 0.3)):
    """single leaf mesh pointing +Z (base at origin, stem offset in +X), midrib arch + side droop; UV 0..1"""
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    rows = []
    for i in range(n + 1):
        t = i / n
        if heart:
            w = W * (math.sin(math.pi * t ** 0.62) ** 0.85) * (1.0 - 0.1 * t) + 0.002
        else:
            w = W * math.sin(t * math.pi) ** 0.75
        z = stem + L * t
        x = curl * L * t * t
        rows.append([(x - w, 0.0, z), (x, 0.0, z), (x + w, 0.0, z)])
    vs = []
    for i, r in enumerate(rows):
        t = i / n
        dr = -curl * 0.4 * math.sin(t * 3.0) * 0 + 0
        v0 = bm.verts.new((r[0][0], -0.5 * (r[1][0] - r[0][0]) - 0.0, r[0][2] - 0.0))
        v1 = bm.verts.new((r[1][0], -0.25 * L * t * t, r[1][2]))
        v2 = bm.verts.new((r[2][0], -0.5 * (r[2][0] - r[1][0]), r[2][2]))
        vs.append((v0, v1, v2))
    for i in range(n):
        a, b = vs[i], vs[i + 1]
        for (p0, p1, q1, q0, u0, u1) in ((a[0], a[1], b[1], b[0], 0.0, 0.5), (a[1], a[2], b[2], b[1], 0.5, 1.0)):
            try:
                f_ = bm.faces.new([p0, p1, q1, q0]); f_.smooth = True
                for l, (uu, vv) in zip(f_.loops, [(u0, i / n), (u1, i / n), (u1, (i + 1) / n), (u0, (i + 1) / n)]):
                    l[ul].uv = (uu, vv)
            except ValueError:
                pass
    # offset so stem sits at +X: shift whole leaf so base at origin and leaf sticks out
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


# ---------------------------------------------------------------- modifier-driven modelling helpers
_NOISE_TEX = {}


def noise_tex(scale=0.05):
    t = _NOISE_TEX.get(scale)
    if t is None:
        t = bpy.data.textures.new('_noise%g' % scale, 'CLOUDS')
        t.noise_scale = scale
        t.noise_depth = 2
        _NOISE_TEX[scale] = t
    return t


def soft_box(mat, Mx, size, col=(1, 1, 1), cfn=None, disp=0.003, level=1, bevel=0.3, g=0, tex_scale=0.06):
    """soft, puffy block (cushions, folded linen): bevelled cube -> SUBSURF -> DISPLACE(noise) via real Blender modifiers"""
    bm = bm_box(size[0], size[1], size[2])
    bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:] + bm.faces[:], offset=min(size) * bevel, segments=1, profile=0.5, affect='EDGES', clamp_overlap=True)
    mods = [('SUBSURF', dict(levels=level, render_levels=level, subdivision_type='CATMULL_CLARK'))]
    if disp:
        mods.append(('DISPLACE', dict(texture=noise_tex(tex_scale), strength=disp, mid_level=0.5)))
    out = modmesh(bm, mods)
    bm.free()
    put(mat, out, Mx, col, cfn, g, skip_down=True)
    out.free()


def array_put(mat, unit_bm, count, offset, Mx, col=(1, 1, 1), cfn=None, g=None, skip_down=True):
    """ARRAY modifier: `count` copies of unit_bm spaced by a constant offset (local), then put with Mx"""
    out = modmesh(unit_bm, [('ARRAY', dict(count=count, use_relative_offset=False, use_constant_offset=True, constant_offset_displace=tuple(offset)))])
    put(mat, out, Mx, col, cfn, g, skip_down=skip_down)
    out.free()


def curve_bar(mat, path_pts, width, thick, Mx, col=(1, 1, 1), cfn=None, segs=40, g=0):
    """flat bar bent along a curve with the CURVE modifier (e.g. rocker runners). path_pts: local points (x forward). bar lies along +X from the first point"""
    pts = [Vector(p) for p in path_pts]
    L = sum((b - a).length for a, b in zip(pts[:-1], pts[1:]))
    cu = bpy.data.curves.new('_bend', 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p.x, p.y, p.z, 1.0)
    co = bpy.data.objects.new('_bend', cu); bpy.context.scene.collection.objects.link(co)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = (v.co.x + 0.5) * L; v.co.y *= thick; v.co.z *= width
    bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if abs(e.verts[0].co.x - e.verts[1].co.x) > L * 0.5], cuts=segs, use_grid_fill=True)
    me = bpy.data.meshes.new('_bar'); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('_bar', me); bpy.context.scene.collection.objects.link(ob)
    m = ob.modifiers.new('Curve', 'CURVE'); m.object = co; m.deform_axis = 'POS_X'
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); ev = ob.evaluated_get(dg)
    me2 = bpy.data.meshes.new_from_object(ev, depsgraph=dg)
    out = bmesh.new(); out.from_mesh(me2)
    for o_ in (ob, co):
        bpy.data.objects.remove(o_)
    bpy.data.meshes.remove(me); bpy.data.meshes.remove(me2); bpy.data.curves.remove(cu)
    bev_bm(out, min(width, thick) * 0.2, 1)
    put(mat, out, Mx, col, cfn, g, skip_down=False)
    out.free()


def lattice_deform(bm, center, size, moves, res=(3, 3, 3)):
    """LATTICE modifier: lattice of `res` points over a box (center,size); moves = {(i,j,k): (dx,dy,dz)} control point offsets (in lattice-local units)"""
    lat = bpy.data.lattices.new('_lat'); lat.points_u, lat.points_v, lat.points_w = res
    lo = bpy.data.objects.new('_lat', lat); bpy.context.scene.collection.objects.link(lo)
    lo.location = center; lo.scale = size
    for (i, j, k), d in moves.items():
        pt = lat.points[i + j * res[0] + k * res[0] * res[1]]
        pt.co_deform = (pt.co[0] + d[0], pt.co[1] + d[1], pt.co[2] + d[2])
    out = modmesh(bm, [('LATTICE', dict(object=lo))])
    bpy.data.objects.remove(lo); bpy.data.lattices.remove(lat)
    return out
