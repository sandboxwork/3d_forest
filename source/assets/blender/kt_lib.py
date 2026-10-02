"""Kitchen+dining geometry toolkit (kt_*).  Everything accumulates into per-material bmeshes in WORLD coords (meters, Z-up).
Advanced Blender machinery used through temp objects: Subsurf / Bevel / Boolean / Array / Curve / Lattice / Displace /
Solidify / Decimate / Screw modifiers, Metaballs, Geometry Nodes (scatter), Cloth simulation.  UV: meters / tile size.
"""
import sys, math, random, os, json
sys.path.insert(0, '/shared/river/assets/blender')
from bl_common import *
from mathutils import noise as mnoise, Euler

F = 0.30          # finished floor z
WY = 3.218        # back wall clear face (baseboard protrudes to 3.22)
TAU = 2 * math.pi
ACC = {}          # matname -> (bm, mat)
TEXSC = {}        # matname -> uv scale (1/tile meters)
SHARPA = {}       # matname -> sharp angle degrees
LIGHTS, COLL, INTER = [], [], []
PARTS = []        # separate objects (animated parts)
rnd = random.Random(11)
M = {}            # name -> material
V = lambda *a: Vector(a)


def C(c):
    if isinstance(c, str):
        return tuple(hex_rgb(c))
    return tuple(c)


def MAT(name, color='#ffffff', tex=None, tile=1.0, sharp=34, **kw):
    m = make_mat(name, color, tex=tex, **kw)
    TEXSC[name] = 1.0 / tile
    SHARPA[name] = sharp
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


def put(mat, src, Mx, col=(1, 1, 1), cfn=None, g=2, uvs=None, skip_down=False, flat=False):
    """copy src bmesh into accumulator of mat, transformed by Mx. g = grain axis idx for box UV."""
    if isinstance(mat, str):
        mat = M[mat]
    bm = get_bm(mat)
    cl = bm.loops.layers.float_color['Col']
    ul = bm.loops.layers.uv['UVMap']
    sul = src.loops.layers.uv.active
    scl = src.loops.layers.float_color.get('Col') if src.loops.layers.float_color else None
    src.normal_update()
    vm = {v: bm.verts.new(Mx @ v.co) for v in src.verts}
    sc = TEXSC.get(mat.name, 1.0) if uvs is None else uvs
    ou, ov = rnd.random(), rnd.random()
    col = C(col)
    upright = (Mx.to_3x3() @ Vector((0, 0, 1))).z > 0.995
    for f in src.faces:
        if skip_down and upright and f.normal.z < -0.97 and (Mx @ f.calc_center_median()).z < 1.9:
            continue
        try:
            nf = bm.faces.new([vm[v] for v in f.verts])
        except ValueError:
            continue
        nf.smooth = not flat
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
                u = co[g]
                v = co[3 - ax - g]
            l[ul].uv = (u * sc + ou, v * sc + ov)
            if cfn:
                c = cfn(Mx @ co)
            elif scl is not None:
                sc_ = ls[scl]
                c = (col[0] * sc_[0], col[1] * sc_[1], col[2] * sc_[2])
            else:
                c = col
            l[cl] = (c[0], c[1], c[2], 1.0)
    return bm


def bev_bm(bm, w, seg=1):
    if w > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:] + bm.faces[:], offset=w, segments=seg, profile=0.5,
                        affect='EDGES', clamp_overlap=True)


def box(mat, c, s, rot=None, bev=0.004, col=(1, 1, 1), cfn=None, g=2, cuts=0, anchor=None, M=None, seg=1, skip_down=True,
        taper=None, flat=False):
    """box centred at c (or, with anchor='b', bottom-centre) size s=(x,y,z). cuts>=4 -> grid subdivision (for AO density).
    taper=(tx,ty): top scaled by (tx,ty)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    if cuts >= 1:
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True)
    for v in bm.verts:
        if taper is not None and v.co.z > 0:
            v.co.x *= taper[0]; v.co.y *= taper[1]
        v.co.x *= s[0]; v.co.y *= s[1]; v.co.z *= s[2]
        if anchor == 'b':
            v.co.z += s[2] / 2
    bev = min(bev, min(s) * 0.34)
    if min(s) < 0.006:
        bev = 0
    if max(s) < 0.1 or min(s) < 0.035:
        seg = 1
    bev_bm(bm, bev, seg)
    put(mat, bm, M if M is not None else xf(c, rot), col, cfn, g, skip_down=skip_down, flat=flat)
    bm.free()


def prof_split(prof, key, values, eps=0.0004):
    """insert crisp split rings into a (r,z) profile where coordinate `key` ('r' or 'z') crosses each value (two rings eps apart)"""
    idx = 0 if key == 'r' else 1
    out = [prof[0]]
    for a, b in zip(prof[:-1], prof[1:]):
        cross = []
        for v in values:
            lo, hi = sorted((a[idx], b[idx]))
            if lo < v < hi and abs(b[idx] - a[idx]) > 1e-9:
                cross.append((v - a[idx]) / (b[idx] - a[idx]))
        for t in sorted(cross, reverse=(b[idx] < a[idx])) if False else sorted(cross):
            for dt in (-1, 1):
                tt = t + dt * eps / max(abs(b[idx] - a[idx]), 1e-6)
                if 0 < tt < 1:
                    out.append((a[0] + (b[0] - a[0]) * tt, a[1] + (b[1] - a[1]) * tt))
        out.append(b)
    return out


def _lathe_bm(prof, seg, uvm=1.0, cap=True):
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    rings = []
    for (r, z) in prof:
        if r < 1e-5:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(TAU * i / seg), r * math.sin(TAU * i / seg), z)) for i in range(seg)])
    for k in range(len(prof) - 1):
        a, b = rings[k], rings[k + 1]
        circ = TAU * max(prof[k][0], prof[k + 1][0], 0.01)
        flatf = abs(prof[k + 1][1] - prof[k][1]) < 0.7 * abs(prof[k + 1][0] - prof[k][0])
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
                if flatf:
                    co = l.vert.co
                    l[ul].uv = (co.x * uvm, co.y * uvm)
                else:
                    l[ul].uv = (prof[k + kk][1] * uvm, ii / seg * circ * uvm)
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
    return bm


lathe_bm = _lathe_bm


def lathe(mat, c, prof, seg=16, rot=None, col=(1, 1, 1), cfn=None, cap=True, uvm=1.0, g=2, M=None, scale=None, auto=True, split=None):
    """prof: [(r,z),...] bottom->top about local z axis.  Segment count auto-reduces for tiny radii."""
    rmax = max(r for r, z in prof) * (max(scale[0], scale[1]) if scale is not None else 1.0)
    if auto:
        if rmax < 0.012:
            seg = min(seg, 6)
        elif rmax < 0.03:
            seg = min(seg, 8)
        elif rmax < 0.06:
            seg = min(seg, 12)
        elif rmax < 0.15:
            seg = min(seg, 20)
    if split:
        prof = prof_split(prof, split[0], split[1])
    bm = _lathe_bm(prof, seg, uvm, cap)
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


def sphere(mat, c, r, seg=14, sq=(1, 1, 1), rot=None, col=(1, 1, 1), cfn=None, rings=8, M=None):
    prof = []
    for i in range(rings + 1):
        a = -math.pi / 2 + math.pi * i / rings
        prof.append((max(math.cos(a) * r, 0.0), math.sin(a) * r))
    lathe(mat, c, prof, seg, rot=rot, col=col, cfn=cfn, cap=False, scale=sq, M=M)


def torus(mat, c, R, r, plane='xy', rot=None, seg=16, rseg=6, col=(1, 1, 1), a0=0, a1=360, M=None, cfn=None):
    pts = arcpts((0, 0, 0), R, a0, a1, max(3, int(seg * abs(a1 - a0) / 360)), plane='xy')
    MM = (M if M is not None else xf(c, rot))
    if plane == 'xz':
        MM = MM @ rotm((90, 0, 0))
    elif plane == 'yz':
        MM = MM @ rotm((0, 90, 0))
    sweep(mat, [(r * math.cos(TAU * k / rseg), r * math.sin(TAU * k / rseg)) for k in range(rseg)], pts, M=MM, col=col,
          closed_path=(abs(a1 - a0) >= 360), cfn=cfn)


def tube(mat, pts, r, seg=8, col=(1, 1, 1), cfn=None, caps=True, taper=None, uvm=1.0, M=None):
    """sweep circle radius r (or list / taper fn(t)) along polyline pts (world, or local if M given)."""
    rr0 = max(r) if isinstance(r, (list, tuple)) else r
    seg = min(seg, 4 if rr0 < 0.003 else (5 if rr0 < 0.006 else (6 if rr0 < 0.012 else (8 if rr0 < 0.03 else seg))))
    n = len(pts)
    if isinstance(r, (list, tuple)):
        rs = list(r)
    elif taper:
        rs = [r * taper(i / (n - 1)) for i in range(n)]
    else:
        rs = [r] * n
    prof = [(math.cos(TAU * k / seg), math.sin(TAU * k / seg)) for k in range(seg)]
    sweep(mat, prof, pts, M=M, col=col, cfn=cfn, scale=[(x, x) for x in rs], caps=caps, uvm=uvm)


def sweep(mat, prof, path, M=None, col=(1, 1, 1), cfn=None, scale=None, caps=True, closed_path=False, up=None, uvm=1.0,
          twist=None, smooth=True, g=2, prof_closed=True, flat=False):
    """extrude 2D profile [(u,v)...] (CCW) along 3D path (Vectors).  scale: list of (su,sv) per path point or fn(t)->(su,sv).
    twist: fn(t)-> radians."""
    pts = [Vector(p) for p in path]
    n = len(pts)
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    tang = []
    for i in range(n):
        if closed_path:
            a = pts[(i - 1) % n]; b = pts[(i + 1) % n]
        else:
            a = pts[max(i - 1, 0)]; b = pts[min(i + 1, n - 1)]
        t = (b - a)
        if t.length < 1e-9:
            t = tang[-1].copy() if tang else Vector((0, 0, 1))
        t.normalize(); tang.append(t)
    upv = Vector(up) if up is not None else (Vector((0, 0, 1)) if abs(tang[0].z) < 0.9 else Vector((1, 0, 0)))
    nrm = upv - tang[0] * upv.dot(tang[0])
    if nrm.length < 1e-6:
        nrm = Vector((1, 0, 0))
    nrm.normalize()
    rings, dists = [], []
    dist = 0.0
    P = len(prof)
    for i in range(n):
        if i > 0:
            dist += (pts[i] - pts[i - 1]).length
        dists.append(dist)
        t = tang[i]
        if up is not None and abs(t.dot(upv)) < 0.98:
            nrm = (upv - t * upv.dot(t)); nrm.normalize()
        else:
            nrm = (nrm - t * nrm.dot(t)); nrm.normalize()
        bn = t.cross(nrm)
        if callable(scale):
            su, sv = scale(i / max(n - 1, 1))
        elif scale:
            su, sv = scale[i]
        else:
            su = sv = 1.0
        tw = twist(i / max(n - 1, 1)) if twist else 0.0
        ct, st = math.cos(tw), math.sin(tw)
        ring = []
        for (pu, pv) in prof:
            uu = (pu * ct - pv * st) * su; vv = (pu * st + pv * ct) * sv
            ring.append(bm.verts.new(pts[i] + nrm * uu + bn * vv))
        rings.append(ring)
    plen = [0.0]
    for k in range(1, P + 1):
        a = prof[(k - 1) % P]; b = prof[k % P]
        plen.append(plen[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    rng_i = range(n if closed_path else n - 1)
    for i in rng_i:
        i2 = (i + 1) % n
        for k in range(P if prof_closed else P - 1):
            k2 = (k + 1) % P
            try:
                f = bm.faces.new([rings[i][k], rings[i][k2], rings[i2][k2], rings[i2][k]])
            except ValueError:
                continue
            f.smooth = smooth and not flat
            d2 = dists[i + 1] if i + 1 < n else dists[i] + (pts[0] - pts[i]).length
            for l, (dd, kk) in zip(f.loops, [(dists[i], k), (dists[i], k + 1), (d2, k + 1), (d2, k)]):
                l[ul].uv = (dd * uvm, plen[kk] * uvm)
    if caps and not closed_path and prof_closed:
        for ring, rev in ((rings[0], True), (rings[-1], False)):
            try:
                f = bm.faces.new(ring[::-1] if rev else ring)
                f.smooth = False
                for l in f.loops:
                    l[ul].uv = (l.vert.co.x * uvm, l.vert.co.y * uvm)
            except ValueError:
                pass
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    elif closed_path and prof_closed:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    put(mat, bm, M if M is not None else Matrix.Identity(4), col, cfn, g)
    bm.free()


def bez(p0, p1, p2, p3, n=12):
    p0, p1, p2, p3 = [Vector(p) for p in (p0, p1, p2, p3)]
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(p0 * (1 - t) ** 3 + p1 * 3 * t * (1 - t) ** 2 + p2 * 3 * t * t * (1 - t) + p3 * t ** 3)
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


def polyline_smooth(pts, n=6):
    """Catmull-Rom resample through pts"""
    P = [Vector(p) for p in pts]
    out = []
    for i in range(len(P) - 1):
        p0 = P[max(i - 1, 0)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(i + 2, len(P) - 1)]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-1])
    return out


# ============================================================ Blender-modifier pipeline
def _tmp_obj(bm, loc=(0, 0, 0)):
    me = bpy.data.meshes.new('_t')
    bm.to_mesh(me)
    ob = bpy.data.objects.new('_t', me)
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _eval_to_bm(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    ev = ob.evaluated_get(dg)
    me2 = bpy.data.meshes.new_from_object(ev, depsgraph=dg)
    bm2 = bmesh.new()
    bm2.from_mesh(me2)
    bpy.data.meshes.remove(me2)
    return bm2


def _kill(ob):
    me = ob.data
    bpy.data.objects.remove(ob)
    if me is not None and me.users == 0:
        if isinstance(me, bpy.types.Mesh):
            bpy.data.meshes.remove(me)


def modbm(bm, mods, loc=(0, 0, 0), free=True):
    """apply modifiers [(TYPE, {props}), ...] to bmesh via temp object -> new bmesh"""
    ob = _tmp_obj(bm, loc)
    for typ, props in mods:
        m = ob.modifiers.new(typ.title(), typ)
        for k, v in props.items():
            setattr(m, k, v)
    out = _eval_to_bm(ob)
    _kill(ob)
    if free:
        bm.free()
    return out


_TEX = {}


def noise_tex(name, scale=0.1, depth=2, kind='CLOUDS', hard=False):
    key = (name, scale, depth, kind)
    t = _TEX.get(key)
    if t is None:
        t = bpy.data.textures.new('n_' + name + str(len(_TEX)), kind)
        t.noise_scale = scale
        if kind == 'CLOUDS':
            t.noise_depth = depth
            t.noise_type = 'HARD_NOISE' if hard else 'SOFT_NOISE'
        _TEX[key] = t
    return t


def disp(bm, strength=0.004, scale=0.05, depth=2, kind='CLOUDS', seed_loc=None, direction='NORMAL', mid=0.5, free=True, hard=False):
    """Displace modifier with noise texture, GLOBAL coords shifted by seed_loc so every call differs"""
    ob = _tmp_obj(bm, seed_loc if seed_loc is not None else (rnd.uniform(-9, 9), rnd.uniform(-9, 9), rnd.uniform(-9, 9)))
    m = ob.modifiers.new('Displace', 'DISPLACE')
    m.texture = noise_tex('d', scale, depth, kind, hard)
    m.strength = strength
    m.mid_level = mid
    m.texture_coords = 'GLOBAL'
    m.direction = direction
    out = _eval_to_bm(ob)
    _kill(ob)
    if free:
        bm.free()
    return out


def boolean(bm, cutters, op='DIFFERENCE', solver='EXACT', free=True):
    """cutters: list of (bmesh, Matrix) in same space as bm.  returns new bmesh"""
    ob = _tmp_obj(bm)
    objs = []
    for cb, cm in cutters:
        co = _tmp_obj(cb)
        co.matrix_world = cm
        objs.append(co)
        m = ob.modifiers.new('B', 'BOOLEAN')
        m.operation = op
        m.solver = solver
        m.object = co
        bpy.context.view_layer.update()
    out = _eval_to_bm(ob)
    for co in objs:
        _kill(co)
    _kill(ob)
    if free:
        bm.free()
    return out


def cube_bm(sx, sy, sz, off=(0, 0, 0), cuts=0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    if cuts:
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True)
    for v in bm.verts:
        v.co = Vector((v.co.x * sx + off[0], v.co.y * sy + off[1], v.co.z * sz + off[2]))
    return bm


def cyl_bm(r, h, seg=12, axis='z', r2=None, off=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    if axis == 'x':
        bmesh.ops.rotate(bm, verts=bm.verts[:], cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, 'Y'))
    elif axis == 'y':
        bmesh.ops.rotate(bm, verts=bm.verts[:], cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, 'X'))
    bmesh.ops.translate(bm, verts=bm.verts[:], vec=off)
    return bm


def sphere_bm(r, seg=10, rings=6, sq=(1, 1, 1), off=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r)
    for v in bm.verts:
        v.co = Vector((v.co.x * sq[0] + off[0], v.co.y * sq[1] + off[1], v.co.z * sq[2] + off[2]))
    return bm


def put_bm(mat, bm, c=None, rot=None, col=(1, 1, 1), cfn=None, M=None, g=2, skip_down=False, free=True, flat=False):
    put(mat, bm, M if M is not None else xf(c or (0, 0, 0), rot), col, cfn, g, skip_down=skip_down, flat=flat)
    if free:
        bm.free()


def subsurf(bm, levels=1, free=True):
    return modbm(bm, [('SUBSURF', {'levels': levels, 'render_levels': levels})], free=free)


def solidify(bm, thick, offset=-1.0, free=True):
    return modbm(bm, [('SOLIDIFY', {'thickness': thick, 'offset': offset})], free=free)


def decimate(bm, ratio, free=True):
    return modbm(bm, [('DECIMATE', {'ratio': ratio})], free=free)


def lattice_bm(bm, res=(3, 3, 4), fn=None, bounds=None, free=True):
    """Lattice modifier: fn(i,j,k,(x,y,z) rest point)-> displacement Vector. bounds=(min,max) vectors for lattice"""
    co = [v.co for v in bm.verts]
    mn = Vector((min(c.x for c in co), min(c.y for c in co), min(c.z for c in co)))
    mx = Vector((max(c.x for c in co), max(c.y for c in co), max(c.z for c in co)))
    if bounds:
        mn, mx = bounds
    mn = mn - Vector((1e-4,) * 3); mx = mx + Vector((1e-4,) * 3)
    lat = bpy.data.lattices.new('lat')
    lat.points_u, lat.points_v, lat.points_w = res
    lob = bpy.data.objects.new('lat', lat)
    bpy.context.scene.collection.objects.link(lob)
    lob.location = (mn + mx) / 2
    lob.scale = (mx - mn)
    bpy.context.view_layer.update()
    for k in range(res[2]):
        for j in range(res[1]):
            for i in range(res[0]):
                p = lat.points[i + j * res[0] + k * res[0] * res[1]]
                rest = Vector((p.co_deform.x, p.co_deform.y, p.co_deform.z))
                d = fn(i, j, k, rest) if fn else Vector()
                p.co_deform = (rest.x + d.x / lob.scale.x, rest.y + d.y / lob.scale.y, rest.z + d.z / lob.scale.z)
    ob = _tmp_obj(bm)
    m = ob.modifiers.new('Lattice', 'LATTICE')
    m.object = lob
    out = _eval_to_bm(ob)
    _kill(ob)
    bpy.data.objects.remove(lob)
    bpy.data.lattices.remove(lat)
    if free:
        bm.free()
    return out


def array_curve(unit_bm, pts, count=None, fit_length=None, spacing=None, twist_alt=0, free=True):
    """Array modifier (fit curve length) + Curve modifier bending along a poly-curve (chains, rope links, bead strings).
    unit_bm along +X from 0..L."""
    cu = bpy.data.curves.new('cv', 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts):
        p.co = (q[0], q[1], q[2], 1)
    cob = bpy.data.objects.new('cv', cu)
    bpy.context.scene.collection.objects.link(cob)
    ob = _tmp_obj(unit_bm)
    L = max(v.co.x for v in unit_bm.verts) - min(v.co.x for v in unit_bm.verts)
    clen = sum((Vector(pts[i + 1]) - Vector(pts[i])).length for i in range(len(pts) - 1))
    a = ob.modifiers.new('Array', 'ARRAY')
    a.fit_type = 'FIT_LENGTH'
    a.fit_length = clen
    a.relative_offset_displace = (spacing if spacing else 1.0, 0, 0)
    c = ob.modifiers.new('Curve', 'CURVE')
    c.object = cob
    c.deform_axis = 'POS_X'
    out = _eval_to_bm(ob)
    _kill(ob)
    bpy.data.objects.remove(cob)
    bpy.data.curves.remove(cu)
    if free:
        unit_bm.free()
    return out


def array_radial(unit_bm, count, axis='Z', free=True, offset_angle=None):
    """Array modifier with an object-offset empty rotated by 360/count (staves, spokes, petals)"""
    emp = bpy.data.objects.new('emp', None)
    bpy.context.scene.collection.objects.link(emp)
    ang = TAU / count if offset_angle is None else math.radians(offset_angle)
    emp.rotation_euler = {'Z': (0, 0, ang), 'X': (ang, 0, 0), 'Y': (0, ang, 0)}[axis]
    ob = _tmp_obj(unit_bm)
    a = ob.modifiers.new('Array', 'ARRAY')
    a.fit_type = 'FIXED_COUNT'
    a.count = count
    a.use_relative_offset = False
    a.use_object_offset = True
    a.offset_object = emp
    out = _eval_to_bm(ob)
    _kill(ob)
    bpy.data.objects.remove(emp)
    if free:
        unit_bm.free()
    return out


def mirror_bm(bm, axis=0, free=True, merge=True):
    return modbm(bm, [('MIRROR', {'use_axis': tuple(i == axis for i in range(3)), 'use_mirror_merge': merge, 'merge_threshold': 0.0005})], free=free)


def screw_bm(profile_pts, angle=360, steps=16, screw_offset=0.0, iterations=1, axis='Z', free=True):
    """Screw modifier ('lathe'): profile polyline [(x,z)] swept around the Z axis (helical if offset)."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, 0, z)) for x, z in profile_pts]
    for a, b in zip(vs[:-1], vs[1:]):
        bm.edges.new((a, b))
    return modbm(bm, [('SCREW', {'angle': math.radians(angle), 'steps': steps, 'render_steps': steps, 'screw_offset': screw_offset,
                                 'iterations': iterations, 'axis': axis, 'use_merge_vertices': True, 'merge_threshold': 0.0002,
                                 'use_smooth_shade': True, 'use_normal_calculate': True})], free=True)


def add_dents(bm, n=4, depth=0.003, rad=0.02, seed=0, zmin=None, zmax=None):
    """hammered-metal dents: n gaussian pockets pushed inward along vertex normals (hand-modelled wear)"""
    rr = random.Random(seed)
    bm.normal_update()
    cand = [v for v in bm.verts if (zmin is None or v.co.z >= zmin) and (zmax is None or v.co.z <= zmax) and (v.co.xy.length > 0.01)]
    if not cand:
        return bm
    for _ in range(n):
        c = rr.choice(cand)
        r_ = rad * rr.uniform(0.6, 1.4)
        d_ = depth * rr.uniform(0.5, 1.3)
        for v in bm.verts:
            dd = (v.co - c.co).length
            if dd < r_ * 2.2:
                v.co -= v.normal * (d_ * math.exp(-(dd / r_) ** 2))
    return bm


def lathe_dent(mat, c, prof, seg=16, rot=None, col=(1, 1, 1), cfn=None, M=None, dents=(4, 0.003, 0.02, 0), cap=False, split=None):
    if split:
        prof = prof_split(prof, split[0], split[1])
    bm = _lathe_bm(prof, seg, 1.0, cap)
    add_dents(bm, *dents)
    put(mat, bm, M if M is not None else xf(c, rot), col, cfn, 2, skip_down=True)
    bm.free()


def lathe_screw(mat, c, prof, steps=14, rot=None, M=None, col=(1, 1, 1), cfn=None, g=2):
    """turned part via the Screw modifier (profile polyline [(r,z)] swept 360 degrees about Z)"""
    bm = screw_bm([(max(r, 0.0002), z) for r, z in prof], 360, steps)
    uv_cyl(bm, axis=2, sc=1.0)
    put(mat, bm, M if M is not None else xf(c, rot), col, cfn, g, skip_down=True)
    bm.free()


def rope_coil(mat, P, R=0.1, r=0.0065, turns=4, steps=14, axis_rot=(0, 0, 0), col=(0.46, 0.34, 0.19)):
    """coil of rope: small circle profile swept helically with the Screw modifier"""
    bm = bmesh.new()
    vs = [bm.verts.new((R + r * math.cos(TAU * k / 6), 0, r * math.sin(TAU * k / 6))) for k in range(6)]
    for i in range(6):
        bm.edges.new((vs[i], vs[(i + 1) % 6]))
    bm = modbm(bm, [('SCREW', {'angle': TAU, 'steps': steps, 'render_steps': steps, 'screw_offset': 2.1 * r, 'iterations': turns, 'axis': 'Z',
                               'use_merge_vertices': False, 'use_smooth_shade': True, 'use_normal_calculate': True})])
    uv_cyl(bm, axis=2, sc=1.0)
    put(mat, bm, xf(P, axis_rot), col)
    bm.free()


# ---------------------------------------------------------------- metaballs
_MB = [0]


def metaball_bm(elements, res=0.006, threshold=0.6):
    """elements [(x,y,z,radius,type,(sx,sy,sz))]  type BALL / CAPSULE / ELLIPSOID / CUBE ; returns bmesh (local)"""
    _MB[0] += 1
    nm = 'mbk%d' % _MB[0]
    mb = bpy.data.metaballs.new(nm)
    mb.resolution = res
    mb.render_resolution = res
    mb.threshold = threshold
    ob = bpy.data.objects.new(nm, mb)
    bpy.context.scene.collection.objects.link(ob)
    for e in elements:
        el = mb.elements.new()
        el.co = (e[0], e[1], e[2])
        el.radius = e[3]
        el.type = e[4] if len(e) > 4 else 'BALL'
        if len(e) > 5:
            el.size_x, el.size_y, el.size_z = e[5]
        el.stiffness = 2.0
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), depsgraph=dg)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bpy.data.objects.remove(ob)
    bpy.data.metaballs.remove(mb)
    return bm


def uv_flat(bm, plane='xy', sc=1.0):
    ul = bm.loops.layers.uv.verify()
    for f in bm.faces:
        for l in f.loops:
            c = l.vert.co
            l[ul].uv = ((c.x, c.y) if plane == 'xy' else (c.x, c.z) if plane == 'xz' else (c.y, c.z))
            l[ul].uv = (l[ul].uv[0] * sc, l[ul].uv[1] * sc)


def uv_cyl(bm, axis=2, sc=1.0, r_ref=None):
    ul = bm.loops.layers.uv.verify()
    for f in bm.faces:
        angs = []
        for l in f.loops:
            c = l.vert.co
            a = math.atan2(c.y, c.x) if axis == 2 else math.atan2(c.z, c.y) if axis == 0 else math.atan2(c.x, c.z)
            angs.append(a)
        if max(angs) - min(angs) > math.pi:
            angs = [a + TAU if a < 0 else a for a in angs]
        for l, a in zip(f.loops, angs):
            c = l.vert.co
            r = r_ref or math.hypot(c.x, c.y)
            l[ul].uv = ((c.z if axis == 2 else c.x if axis in (0, 1) else c.y) * sc, a * r * sc)


def uv_sph(bm, r, sc=1.0):
    ul = bm.loops.layers.uv.verify()
    for f in bm.faces:
        angs = [math.atan2(l.vert.co.y, l.vert.co.x) for l in f.loops]
        if max(angs) - min(angs) > math.pi:
            angs = [a + TAU if a < 0 else a for a in angs]
        for l, a in zip(f.loops, angs):
            l[ul].uv = (l.vert.co.z * sc, a * r * sc)


# ---------------------------------------------------------------- cloth simulation
def cloth_sim(bm, colliders=(), pin=None, frames=60, mass=0.12, tension=18, compression=18, shear=8, bending=2.5, damping=0.4,
              air=2.0, quality=7, thickness=0.0, self_col=False, friction=12.0, dist=0.004, gravity=(0, 0, -9.8), wind=None,
              coll_dist=0.0025, subsurf_levels=0, free=True, settle_extra=0):
    """bm: cloth grid (world coords).  colliders [(bm, Matrix)] in world.  pin: fn(Vector)->bool.  Steps frames headless.
    Returns evaluated bmesh (+optional solidify/subsurf)."""
    sc = bpy.context.scene
    sc.use_gravity = True
    sc.gravity = gravity
    old_end = sc.frame_end
    sc.frame_start = 1
    sc.frame_end = frames + 2
    sc.frame_set(1)
    ob = _tmp_obj(bm)
    if pin is not None:
        vg = ob.vertex_groups.new(name='pin')
        for v in ob.data.vertices:
            if pin(v.co):
                vg.add([v.index], 1.0, 'REPLACE')
    cm = ob.modifiers.new('Cloth', 'CLOTH')
    s = cm.settings
    s.quality = quality
    s.mass = mass
    s.tension_stiffness = tension
    s.compression_stiffness = compression
    s.shear_stiffness = shear
    s.bending_stiffness = bending
    s.tension_damping = damping * 10
    s.compression_damping = damping * 10
    s.shear_damping = damping * 10
    s.bending_damping = 0.5
    s.air_damping = air
    if pin is not None:
        s.vertex_group_mass = 'pin'
        s.pin_stiffness = 1.0
    cs = cm.collision_settings
    cs.use_collision = True
    cs.distance_min = dist
    cs.collision_quality = 4
    cs.use_self_collision = self_col
    if self_col:
        cs.self_distance_min = 0.003
        cs.self_friction = 5
    cobs = []
    for cb, cmx in colliders:
        co = _tmp_obj(cb)
        co.matrix_world = cmx
        cmod = co.modifiers.new('Collision', 'COLLISION')
        co.collision.thickness_outer = coll_dist
        co.collision.thickness_inner = 0.002
        co.collision.cloth_friction = friction
        co.collision.use_culling = False
        cobs.append(co)
    bpy.context.view_layer.update()
    for f in range(1, frames + 1 + settle_extra):
        sc.frame_set(f)
    out = _eval_to_bm(ob)
    sc.frame_set(1)
    for co in cobs:
        _kill(co)
    _kill(ob)
    sc.frame_end = old_end
    mods = []
    if subsurf_levels:
        mods.append(('SUBSURF', {'levels': subsurf_levels, 'render_levels': subsurf_levels}))
    if thickness:
        mods.append(('SOLIDIFY', {'thickness': thickness, 'offset': 0.0}))
    if mods:
        out = modbm(out, mods)
    if free:
        bm.free()
    return out


def cloth_grid(x0, x1, y0, y1, nx, ny, z=0.0, M=None, uvscale=1.0):
    """flat rectangular grid facing +z, uv in meters"""
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    Vt = [[bm.verts.new(((x0 + (x1 - x0) * i / nx), (y0 + (y1 - y0) * j / ny), z)) for j in range(ny + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(ny):
            f = bm.faces.new([Vt[i][j], Vt[i + 1][j], Vt[i + 1][j + 1], Vt[i][j + 1]])
            for l in f.loops:
                l[ul].uv = (l.vert.co.x * uvscale, l.vert.co.y * uvscale)
    if M is not None:
        for v in bm.verts:
            v.co = M @ v.co
    return bm


# ---------------------------------------------------------------- geometry nodes scatter
def gn_scatter(surface_bm, variants, distance=0.05, density=3000, seed=1, scale=(0.9, 1.1), tilt=0.15, zrot=True,
               tint=0.08, surf_M=None, mode='POISSON', count_density=None, lift=0.0, face_up_only=False, hue=None):
    """Scatter instance variants over a surface with a Geometry-Nodes tree (Distribute Points on Faces [Poisson disk],
    Instance on Points, Realize).  variants: list of dict {'parts': [(bm, matname)], 'weight'}.  Returns list of
    (matname, bmesh) with vertex colours baked (Col) incl. per-instance tint."""
    # ---- instance collection
    col = bpy.data.collections.new('sc_inst%d' % rnd.randint(0, 99999))
    bpy.context.scene.collection.children.link(col)
    inst_objs = []
    matnames = []
    for vi, var in enumerate(variants):
        sb = bmesh.new()
        sb.loops.layers.float_color.new('Col')
        cl = sb.loops.layers.float_color['Col']
        mats = []
        for (pb, mn) in var['parts']:
            if mn not in mats:
                mats.append(mn)
        for (pb, mn) in var['parts']:
            off = {v: sb.verts.new(v.co) for v in pb.verts}
            pcl = pb.loops.layers.float_color.get('Col')
            for f in pb.faces:
                try:
                    nf = sb.faces.new([off[v] for v in f.verts])
                except ValueError:
                    continue
                nf.smooth = True
                nf.material_index = mats.index(mn)
                for ls, l in zip(f.loops, nf.loops):
                    l[cl] = tuple(ls[pcl]) if pcl is not None else (1, 1, 1, 1)
        me = bpy.data.meshes.new('iv')
        sb.to_mesh(me); sb.free()
        for mn in mats:
            me.materials.append(M[mn])
        ob = bpy.data.objects.new('iv%d' % vi, me)
        col.objects.link(ob)
        inst_objs.append(ob)
        matnames.append(mats)
    # ---- surface
    surf_me = bpy.data.meshes.new('ss')
    surface_bm.to_mesh(surf_me)
    sob = bpy.data.objects.new('ss', surf_me)
    bpy.context.scene.collection.objects.link(sob)
    ng = bpy.data.node_groups.new('scat', 'GeometryNodeTree')
    ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N, L = ng.nodes, ng.links
    gi = N.new('NodeGroupInput'); go = N.new('NodeGroupOutput')
    dp = N.new('GeometryNodeDistributePointsOnFaces'); dp.distribute_method = 'POISSON' if mode == 'POISSON' else 'RANDOM'
    if mode == 'POISSON':
        dp.inputs['Distance Min'].default_value = distance
        dp.inputs['Density Max'].default_value = density
    else:
        dp.inputs['Density'].default_value = density
    dp.inputs['Seed'].default_value = seed
    ci = N.new('GeometryNodeCollectionInfo'); ci.inputs['Collection'].default_value = col
    ci.inputs['Separate Children'].default_value = True; ci.inputs['Reset Children'].default_value = True
    iop = N.new('GeometryNodeInstanceOnPoints')
    iop.inputs['Pick Instance'].default_value = True
    ri = N.new('FunctionNodeRandomValue'); ri.data_type = 'INT'
    ints = [i for i in ri.inputs if i.type == 'INT']
    ints[0].default_value = 0; ints[1].default_value = len(variants) - 1
    ri.inputs['Seed'].default_value = seed + 5
    rv = N.new('FunctionNodeRandomValue'); rv.data_type = 'FLOAT_VECTOR'
    vecs = [i for i in rv.inputs if i.type == 'VECTOR']
    vecs[0].default_value = (-tilt, -tilt, 0 if zrot else 0)
    vecs[1].default_value = (tilt, tilt, TAU if zrot else 0)
    rv.inputs['Seed'].default_value = seed + 9
    rs = N.new('FunctionNodeRandomValue'); rs.data_type = 'FLOAT'
    fl = [i for i in rs.inputs if i.type == 'VALUE']
    fl[0].default_value = scale[0]; fl[1].default_value = scale[1]
    rs.inputs['Seed'].default_value = seed + 13
    comb = N.new('ShaderNodeCombineXYZ')
    L.new(rs.outputs['Value'], comb.inputs[0]); L.new(rs.outputs['Value'], comb.inputs[1]); L.new(rs.outputs['Value'], comb.inputs[2])
    rt = N.new('FunctionNodeRandomValue'); rt.data_type = 'FLOAT'
    fl2 = [i for i in rt.inputs if i.type == 'VALUE']
    fl2[0].default_value = -tint; fl2[1].default_value = tint
    rt.inputs['Seed'].default_value = seed + 21
    st = N.new('GeometryNodeStoreNamedAttribute'); st.data_type = 'FLOAT'; st.domain = 'INSTANCE'
    st.inputs['Name'].default_value = 'tint'
    rr = N.new('GeometryNodeRealizeInstances')
    L.new(gi.outputs[0], dp.inputs['Mesh'])
    L.new(dp.outputs['Points'], iop.inputs['Points'])
    L.new(ci.outputs['Instances'], iop.inputs['Instance'])
    L.new(ri.outputs['Value'], iop.inputs['Instance Index'])
    L.new(rv.outputs['Value'], iop.inputs['Rotation'])
    L.new(comb.outputs['Vector'], iop.inputs['Scale'])
    L.new(iop.outputs['Instances'], st.inputs['Geometry'])
    L.new(rt.outputs['Value'], st.inputs['Value'])
    L.new(st.outputs['Geometry'], rr.inputs['Geometry'])
    L.new(rr.outputs['Geometry'], go.inputs[0])
    mod = sob.modifiers.new('gn', 'NODES')
    mod.node_group = ng
    if surf_M is not None:
        sob.matrix_world = surf_M
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    me = bpy.data.meshes.new_from_object(sob.evaluated_get(dg), depsgraph=dg)
    # ---- split by material
    # evaluated mesh materials are the union of instance materials in slot order
    slot_names = [m.name if m else None for m in me.materials]
    outs = {}
    tintA = me.attributes.get('tint')
    cA = me.color_attributes.get('Col')
    nverts = len(me.vertices)
    tv = np.zeros(nverts, dtype=np.float32)
    if tintA is not None:
        tintA.data.foreach_get('value', tv) if tintA.domain == 'POINT' else None
    for p in me.polygons:
        mn = slot_names[p.material_index] if p.material_index < len(slot_names) else None
        if mn is None:
            continue
        bm = outs.get(mn)
        if bm is None:
            bm = outs[mn] = bmesh.new()
            bm.loops.layers.float_color.new('Col')
        cl = bm.loops.layers.float_color['Col']
        vs = []
        for vi in p.vertices:
            vs.append(bm.verts.new((surf_M @ me.vertices[vi].co) if surf_M is not None else me.vertices[vi].co))
        try:
            nf = bm.faces.new(vs)
        except ValueError:
            continue
        nf.smooth = True
        for k, li in enumerate(p.loop_indices):
            vi = me.loops[li].vertex_index
            if cA is not None:
                c = cA.data[li].color if cA.domain == 'CORNER' else cA.data[vi].color
            else:
                c = (1, 1, 1, 1)
            t = 1.0 + float(tv[vi])
            h = 1.0
            nf.loops[k][cl] = (c[0] * t, c[1] * t, c[2] * t, 1.0)
    bpy.data.meshes.remove(me)
    bpy.data.objects.remove(sob); bpy.data.meshes.remove(surf_me)
    for ob in inst_objs:
        m_ = ob.data
        bpy.data.objects.remove(ob); bpy.data.meshes.remove(m_)
    bpy.data.collections.remove(col)
    bpy.data.node_groups.remove(ng)
    return outs


def put_outs(outs, Mx=None, col=(1, 1, 1)):
    for mn, bm in outs.items():
        put(mn, bm, Mx if Mx is not None else Matrix.Identity(4), col=col)
        bm.free()


# ============================================================ colour helpers
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


def mixc(a, b, t):
    return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))


def woodcol(base=(1, 1, 1), amp=0.10, s=6.0, seed=0, axis=2):
    def f(p):
        t = fbm(p.x * (1 if axis != 0 else 0.15), p.y * (1 if axis != 1 else 0.15), p.z * (1 if axis != 2 else 0.15), s, seed, 2)
        k = 1 + amp * t
        return (base[0] * k, base[1] * k, base[2] * k)
    return f


def wear_col(base, amp=0.08, s=9.0, seed=0, dirt_low=0.0, zlow=None):
    """noise variation + optional grime near z <= zlow"""
    def f(p):
        k = 1 + amp * fbm(p.x, p.y, p.z, s, seed, 2)
        c = (base[0] * k, base[1] * k, base[2] * k)
        return c
    return f


def fab(base, amp=0.07, s=9.0, seed=0):
    def f(p):
        k = 1 + amp * fbm(p.x, p.y, p.z, s, seed, 2)
        return (base[0] * k, base[1] * k, base[2] * k)
    return f


# ============================================================ meta
def collider(x0, x1, y0, y1, top, bottom=0.30):
    COLL.append({'cx': round((x0 + x1) / 2, 3), 'cz': round(-(y0 + y1) / 2, 3), 'hx': round(abs(x1 - x0) / 2, 3),
                 'hz': round(abs(y1 - y0) / 2, 3), 'top': round(top, 3), 'bottom': bottom})


def light(name, pos, color=(1.0, 0.7, 0.4), intensity=1.0, distance=6.0):
    LIGHTS.append({'name': name, 'pos': [round(pos[0], 3), round(pos[2], 3), round(-pos[1], 3)], 'color': list(color),
                   'intensity': intensity, 'distance': distance})


def interact(name, pos, label):
    INTER.append({'name': name, 'pos': [round(pos[0], 3), round(pos[2], 3), round(-pos[1], 3)], 'label': label})


def finalize(names=None):
    """convert accumulators into objects  static_<mat>"""
    objs = []
    for mn, (bm, mat) in ACC.items():
        bm.normal_update()
        sa = math.radians(SHARPA.get(mn, 34))
        for e in bm.edges:
            if len(e.link_faces) == 2:
                try:
                    if e.calc_face_angle(0.0) > sa:
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
    ACC.clear()
    return objs


def part_begin():
    global ACC
    saved = ACC
    ACC = {}
    return saved


def part_end(saved, name, pivot, parent=None):
    global ACC
    made = []
    for mn, (bm, mat) in ACC.items():
        bm.normal_update()
        sa = math.radians(SHARPA.get(mn, 34))
        for e in bm.edges:
            if len(e.link_faces) == 2:
                try:
                    if e.calc_face_angle(0.0) > sa:
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

    def sphere(s, mat, c, rad, r=None, **kw):
        sphere(mat, None, rad, M=s._m(c, r), **kw)

    def tube(s, mat, pts, rad, **kw):
        tube(mat, pts, rad, M=s.M, **kw)

    def sweep(s, mat, prof, path, **kw):
        sweep(mat, prof, path, M=s.M, **kw)

    def put_bm(s, mat, bm, c=(0, 0, 0), r=None, **kw):
        put_bm(mat, bm, M=s._m(c, r), **kw)

    def torus(s, mat, c, R, r, plane='xy', **kw):
        torus(mat, None, R, r, plane, M=s._m(c, None), **kw)


def face(src, dst):
    dx, dy = dst[0] - src[0], dst[1] - src[1]
    return math.degrees(math.atan2(-dx, dy))


def collider_f(f, W, D, top, off=(0, 0), bottom=0.30):
    a = math.radians(f.rot)
    cx, cy = f.p((off[0], off[1], 0))[:2]
    hx = abs(W / 2 * math.cos(a)) + abs(D / 2 * math.sin(a))
    hy = abs(W / 2 * math.sin(a)) + abs(D / 2 * math.cos(a))
    collider(cx - hx, cx + hx, cy - hy, cy + hy, top, bottom)


def tri_count():
    t = 0
    for mn, (bm, mat) in ACC.items():
        for f in bm.faces:
            t += len(f.verts) - 2
    return t


def tri_report():
    out = {}
    for mn, (bm, mat) in ACC.items():
        out[mn] = sum(len(f.verts) - 2 for f in bm.faces)
    return out
