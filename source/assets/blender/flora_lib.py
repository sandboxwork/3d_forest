"""Procedural flora toolkit on top of bl_common (numpy based geometry builders).

Conventions: Blender Z-up, plant rooted at origin, growing +Z.
Patch = (V Nx3, F list of tuples, C Nx3 absolute LINEAR colours, UV Nx2)
Geo.add(mat, patch, xf) converts absolute colours to tints relative to the material base colour
(runtime multiplies vertex colour with material colour), clamped to [0,1].
"""
import sys, math, json, os, time
sys.path.insert(0, '/shared/river/assets/blender')
from bl_common import *
import numpy as np

PI = math.pi
TAU = 2 * math.pi
LOD = 0
RNG = np.random.RandomState(0)


def set_lod(n):
    global LOD
    LOD = n


def lr(n, lo=1):
    return n if LOD == 0 else max(lo, int(round(n * 0.5 + 0.01)))


def lre(n):
    if LOD == 0:
        return n
    return max(2, 2 * int(round(n * 0.25)))


def lc(n, f=0.55, lo=1):
    """count reduction for lod"""
    return n if LOD == 0 else max(lo, int(round(n * f)))


# ---------------------------------------------------------------- colour
def lin(h):
    return np.array(hex_rgb(h))


def grad(t, stops):
    """t: array; stops: [(pos,'#hex'),...] -> array(...,3) linear colours"""
    t = np.asarray(t, float)
    pos = [s[0] for s in stops]
    cols = np.array([hex_rgb(s[1]) for s in stops])
    return np.stack([np.interp(t, pos, cols[:, k]) for k in range(3)], -1)


MATS = {}


def mat(name, hexcol, rough=0.6, double=True, emit=None, emit_strength=0.0, sss=0.0, alpha=1.0):
    m = make_mat(name, hexcol, rough=rough, double=double, emit=emit, emit_strength=emit_strength, alpha=alpha)
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_name = 'Col'
    bc = nt.nodes.new('ShaderNodeRGB'); bc.outputs[0].default_value = b.inputs['Base Color'].default_value
    vm = nt.nodes.new('ShaderNodeVectorMath'); vm.operation = 'MULTIPLY'
    nt.links.new(at.outputs['Color'], vm.inputs[0])
    nt.links.new(bc.outputs[0], vm.inputs[1])
    nt.links.new(vm.outputs[0], b.inputs['Base Color'])
    if sss > 0:
        try:
            b.inputs['Subsurface Weight'].default_value = sss
            b.inputs['Subsurface Radius'].default_value = (0.3, 0.3, 0.3)
        except Exception:
            pass
    MATS[name] = np.maximum(np.array(m['rgb']), 1e-3)
    return m


# ---------------------------------------------------------------- transforms
def T(x, y=0.0, z=0.0):
    if not np.isscalar(x):
        x, y, z = x
    M = np.eye(4); M[:3, 3] = (x, y, z); return M


def Rx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1.0]])


def Ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1.0]])


def Rz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1.0]])


def Sc(x, y=None, z=None):
    if y is None: y = z = x
    return np.diag([x, y, z, 1.0])


def mm(*ms):
    r = np.eye(4)
    for m in ms:
        r = r @ m
    return r


def unit(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v


def orient(pos, ydir, zhint):
    Y = unit(ydir)
    Z = np.asarray(zhint, float) - Y * np.dot(zhint, Y)
    if np.linalg.norm(Z) < 1e-6:
        Z = np.cross(Y, [1, 0, 0] if abs(Y[0]) < 0.9 else [0, 1, 0])
    Z = unit(Z)
    X = np.cross(Y, Z)
    M = np.eye(4); M[:3, 0] = X; M[:3, 1] = Y; M[:3, 2] = Z; M[:3, 3] = pos
    return M


def frame_z(pos, zdir, yaw=0.0):
    Z = unit(zdir)
    ref = np.array([0, 1.0, 0]) if abs(Z[1]) < 0.95 else np.array([1.0, 0, 0])
    X = unit(np.cross(ref, Z)); Y = np.cross(Z, X)
    M = np.eye(4); M[:3, 0] = X; M[:3, 1] = Y; M[:3, 2] = Z; M[:3, 3] = pos
    return M @ Rz(yaw)


def xfv(M, V):
    return V @ M[:3, :3].T + M[:3, 3]


# ---------------------------------------------------------------- patches
def grid(P, C=None, wrap=False, flip=False):
    P = np.asarray(P, float)
    nu1, nv1, _ = P.shape
    V = P.reshape(-1, 3)
    F = []
    nvq = nv1 if wrap else nv1 - 1
    for i in range(nu1 - 1):
        for j in range(nvq):
            j2 = (j + 1) % nv1
            q = (i * nv1 + j, i * nv1 + j2, (i + 1) * nv1 + j2, (i + 1) * nv1 + j)
            F.append(q[::-1] if flip else q)
    uu, vv = np.meshgrid(np.linspace(0, 1, nu1), np.linspace(0, 1, nv1), indexing='ij')
    UV = np.stack([vv.ravel(), uu.ravel()], 1)
    if C is None:
        C = np.ones_like(V) * -1
    else:
        C = np.asarray(C, float).reshape(-1, 3)
    return (V, F, C, UV)


def cat(patches):
    Vs, Fs, Cs, Us = [], [], [], []
    off = 0
    for V, F, C, UV in patches:
        Vs.append(V); Cs.append(C); Us.append(UV)
        Fs += [tuple(i + off for i in f) for f in F]
        off += len(V)
    return (np.concatenate(Vs), Fs, np.concatenate(Cs), np.concatenate(Us))


def rv(x, rng):
    if isinstance(x, tuple) and len(x) == 2 and all(isinstance(k, (int, float)) for k in x):
        return rng.uniform(x[0], x[1])
    return x


class Geo:
    def __init__(self):
        self.items = []

    def add(self, m, patch, xf=None):
        V, F, C, UV = patch
        if xf is not None:
            V = xfv(xf, V)
        base = MATS[m]
        C = np.where(C < 0, 1.0, np.clip(C / base, 0, 1.0))
        self.items.append((m, V, F, C, UV))

    def tris(self):
        return sum(len(f) - 2 for it in self.items for f in it[2])

    def bounds(self):
        V = np.concatenate([it[1] for it in self.items])
        r = np.hypot(V[:, 0], V[:, 1])
        return float(V[:, 2].max()), float(np.percentile(r, 97)), float(r.max()), V

    def to_obj(self, name):
        order = []
        for it in self.items:
            if it[0] not in order: order.append(it[0])
        Vs, Fs, Cs, Us, Mi = [], [], [], [], []
        off = 0
        for m, V, F, C, UV in self.items:
            Vs.append(V); Cs.append(C); Us.append(UV)
            Fs += [tuple(i + off for i in f) for f in F]
            Mi += [order.index(m)] * len(F)
            off += len(V)
        V = np.concatenate(Vs); C = np.concatenate(Cs); UV = np.concatenate(Us)
        me = bpy.data.meshes.new(name)
        me.from_pydata(V.tolist(), [], Fs)
        for m in order:
            me.materials.append(bpy.data.materials[m])
        me.polygons.foreach_set('material_index', np.array(Mi, dtype=np.int32))
        try:
            me.polygons.foreach_set('use_smooth', np.ones(len(me.polygons), dtype=bool))
        except Exception:
            pass
        uvl = me.uv_layers.new(name='UVMap')
        lv = np.zeros(len(me.loops), dtype=np.int32)
        me.loops.foreach_get('vertex_index', lv)
        uvl.data.foreach_set('uv', UV[lv].ravel())
        ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
        rgba = np.concatenate([C, np.ones((len(C), 1))], 1)
        ca.data.foreach_set('color', rgba.ravel())
        me.update()
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        return ob


# ---------------------------------------------------------------- noise
def make_noise(seed, k=5):
    r = np.random.RandomState(seed)
    d = r.normal(size=(k, 3)); d /= np.linalg.norm(d, axis=1, keepdims=True)
    ph = r.uniform(0, TAU, k); fr = r.uniform(0.7, 1.5, k)

    def f(P, freq=1.0):
        P = np.asarray(P)
        s = 0
        for i in range(k):
            s = s + np.sin((P @ d[i]) * freq * fr[i] * TAU + ph[i])
        return s / math.sqrt(k)
    return f


# ---------------------------------------------------------------- surfaces
def _cum(f, u):
    return np.concatenate([[0], np.cumsum(0.5 * (f[1:] + f[:-1]) * np.diff(u))])


def blade(L, W, nu=4, nv=2, a=0.8, b=0.5, bend=0.0, bend2=0.0, cup=0.0, fold=0.0, wave=0.0, wavef=3.0, wph=0.0,
          serr=0.0, notch=0.0, twist=0.0, side=0.0, cols=None, mid=0.0, edge=0.0, widthfn=None, noise=None, nz=0.0,
          veinN=0, vein=0.0, lod=True, flip=False, cfn=None, baseW=0.0, nzf=None):
    """Thin curved leaf/petal. Base at origin, length along +Y, normal +Z. Returns patch."""
    L, W, a, b, bend, bend2, cup, fold, wave, serr, notch, twist, side, mid, edge, nz = [rv(x, RNG) for x in (L, W, a, b, bend, bend2, cup, fold, wave, serr, notch, twist, side, mid, edge, nz)]
    if lod:
        nu, nv = lr(nu), lre(nv)
    nv = max(2, nv + (nv % 2))
    u1 = np.linspace(0, 1, nu + 1)
    v1 = np.linspace(-1, 1, nv + 1)
    U, Vv = np.meshgrid(u1, v1, indexing='ij')
    u = u1
    if widthfn is not None:
        w = widthfn(u)
    else:
        us = a / (a + b)
        w = (np.maximum(u, 1e-6) ** a * (1 - u) ** b) / (us ** a * (1 - us) ** b)
    w = np.maximum(w, baseW)
    if serr:
        par = (np.arange(nu + 1) % 2).astype(float)
        w = w * (1 - serr * par * (u > 0.08) * (u < 0.97))
    wu = w[:, None]
    xn = Vv * wu
    x = xn * (W / 2)
    ang = bend * u + bend2 * u * u
    fy = L * np.cos(ang); fz = L * np.sin(ang)
    py = _cum(fy, u); pz = _cum(fz, u)
    ze = cup * (W / 2) * xn ** 2 + fold * (W / 2) * np.abs(xn)
    if wave:
        ze = ze + wave * (W / 2) * np.abs(xn) * np.sin(wavef * TAU * U + wph)
    if noise is not None and nz and nzf is not None:
        ze = ze + nz * (W / 2) * noise(np.stack([xn * 1.2, U * 1.2, np.zeros_like(x)], -1), nzf)
    elif noise is not None and nz:
        ze = ze + nz * (W / 2) * noise(np.stack([x * 30, U * L * 30, np.zeros_like(x)], -1), 0.1)
    ze = ze * np.minimum(1, U * 4 + 0.05)
    if twist:
        ph = twist * U
        x, ze = x * np.cos(ph) - ze * np.sin(ph), x * np.sin(ph) + ze * np.cos(ph)
    if side:
        x = x + side * L * U ** 2
    dy = -notch * L * U ** 6 * np.exp(-(Vv / 0.3) ** 2) if notch else 0
    A = ang[:, None]
    Px = x
    Py = py[:, None] - ze * np.sin(A) + dy
    Pz = pz[:, None] + ze * np.cos(A)
    P = np.stack([Px, Py, Pz], -1)
    if cfn is not None:
        C = cfn(U, Vv, xn)
    elif cols is not None:
        C = grad(U, cols)
    else:
        C = None
    if C is not None:
        f = 1.0
        if mid:
            f = f + mid * np.exp(-(xn / 0.10) ** 2)
        if edge:
            f = f - edge * np.abs(xn) ** 2
        if veinN and vein:
            f = f - vein * np.maximum(0, np.cos(TAU * (U * veinN - np.abs(xn) * 0.6))) ** 6
        C = C * np.asarray(f)[..., None]
    return grid(P, C, flip=flip)


def revolve(prof, nu, nseg, lobe=None, cols=None, flip=False, lod=True, close_top=False):
    if lod:
        nu, nseg = lr(nu), lr(nseg, 3)
    u = np.linspace(0, 1, nu + 1)[:, None]
    th = np.linspace(0, TAU, nseg, endpoint=False)[None, :]
    r, z = prof(u)
    r = np.broadcast_to(r, (nu + 1, 1)) * np.ones((1, nseg))
    if lobe is not None:
        r = r * lobe(u, th)
    zz = np.broadcast_to(z, (nu + 1, 1)) * np.ones((1, nseg))
    P = np.stack([r * np.cos(th), r * np.sin(th), zz], -1)
    C = cols(u * np.ones_like(th), th * np.ones_like(u)) if cols is not None else None
    return grid(P, C, wrap=True, flip=flip)


def ellipsoid(rx, ry, rz, nu=5, nseg=8, cols=None, lobe=None, lod=True):
    def prof(u):
        ph = -PI / 2 + PI * u
        return rx * np.cos(ph), rz * np.sin(ph)
    p = revolve(prof, nu, nseg, lobe=lobe, cols=cols, lod=lod)
    V = p[0].copy(); V[:, 1] *= ry / rx
    return (V, p[1], p[2], p[3])


def dome(R, H, nu=4, nseg=12, cols=None, lobe=None, lod=True):
    def prof(u):
        ph = u * PI / 2
        return R * np.cos(ph), H * np.sin(ph)
    return revolve(prof, nu, nseg, lobe=lobe, cols=cols, lod=lod)


def lobed_disc(R, lobes=5, rings=2, segs=15, depth=0.25, cup=0.0, cols=None, wave=0.0, sharp=1.0, lod=True, rot=0.0, ruffle=0.0):
    """flat/cupped disc with scalloped outline; normal +Z, centre at origin"""
    def prof(u):
        return R * u, cup * R * u ** 2

    def lobe(u, th):
        k = (0.5 - 0.5 * np.cos(lobes * (th + rot))) ** sharp
        return 1 - depth * k * np.minimum(1, u * 1.6) ** 2
    p = revolve(prof, rings, segs, lobe=lobe, cols=cols, flip=True, lod=lod)
    if wave or ruffle:
        V = p[0].copy()
        r = np.hypot(V[:, 0], V[:, 1]) / R
        th = np.arctan2(V[:, 1], V[:, 0])
        V[:, 2] += wave * R * r ** 2 * np.cos(lobes * th * 2 + 1)
        p = (V, p[1], p[2], p[3])
    return p


def tube(pts, radii, sides=5, cols=None, cap=True, squash=1.0, lod=True, cap_start=False):
    pts = np.asarray(pts, float)
    n = len(pts)
    radii = np.broadcast_to(np.asarray(radii, float), (n,)).copy()
    if lod:
        sides = max(3, lr(sides, 3))
    Tg = np.gradient(pts, axis=0)
    Tg = Tg / np.maximum(np.linalg.norm(Tg, axis=1, keepdims=True), 1e-9)
    ref = np.array([1.0, 0, 0]) if abs(Tg[0][0]) < 0.9 else np.array([0, 1.0, 0])
    N = unit(np.cross(Tg[0], ref))
    ang = np.linspace(0, TAU, sides, endpoint=False)
    rings = []
    for i in range(n):
        if i > 0:
            N = N - Tg[i] * np.dot(N, Tg[i]); N = unit(N)
        B = np.cross(Tg[i], N)
        rings.append(pts[i] + radii[i] * (np.cos(ang)[:, None] * N + np.sin(ang)[:, None] * B * squash))
    P = np.array(rings)
    C = None
    if cols is not None:
        c = np.asarray(cols, float)
        if c.ndim == 1:
            c = np.tile(c, (n, 1))
        C = np.repeat(c[:, None, :], sides, 1)
    V, F, Cc, UV = grid(P, C, wrap=True)
    if cap:
        ci = len(V)
        V = np.concatenate([V, pts[-1:] + Tg[-1] * max(radii[-1], 1e-4) * 0.6])
        last = (n - 1) * sides
        for j in range(sides):
            F.append((last + j, last + (j + 1) % sides, ci))
        Cc = np.concatenate([Cc, Cc[last:last + 1]]); UV = np.concatenate([UV, [[0.5, 1.0]]])
    if cap_start:
        ci = len(V)
        V = np.concatenate([V, pts[:1] - Tg[0] * max(radii[0], 1e-4) * 0.3])
        for j in range(sides):
            F.append(((j + 1) % sides, j, ci))
        Cc = np.concatenate([Cc, Cc[0:1]]); UV = np.concatenate([UV, [[0.5, 0.0]]])
    return (V, F, Cc, UV)


def bez(p0, p1, p2, p3, n):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = [np.asarray(p, float) for p in (p0, p1, p2, p3)]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def stem_path(h, rng, lean=0.06, sway=0.03, n=8, dirang=None, sway_freq=None):
    a = rng.uniform(0, TAU) if dirang is None else dirang
    d = np.array([math.cos(a), math.sin(a), 0]); pp = np.array([-math.sin(a), math.cos(a), 0])
    n = max(3, lr(n, 3)) if LOD else n
    t = np.linspace(0, 1, n)
    sf = sway_freq if sway_freq is not None else rng.uniform(0.8, 1.7)
    lat = lean * h * t ** 1.7
    lat2 = sway * h * np.sin(t * PI * sf + rng.uniform(0, TAU)) * t
    pts = lat[:, None] * d + lat2[:, None] * pp
    pts[:, 2] = h * t * (1 - 0.3 * lean * t)
    pts[:, 2] *= h / pts[-1, 2]
    return pts


def pathpt(pts, t):
    pts = np.asarray(pts)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)]); s /= s[-1]
    pos = np.array([np.interp(t, s, pts[:, k]) for k in range(3)])
    eps = 0.01
    p2 = np.array([np.interp(min(1, t + eps), s, pts[:, k]) for k in range(3)])
    p1 = np.array([np.interp(max(0, t - eps), s, pts[:, k]) for k in range(3)])
    return pos, unit(p2 - p1)


def stem_frame(tan):
    ref = np.array([0, 0, 1.0]) if abs(tan[2]) < 0.95 else np.array([1.0, 0, 0])
    e1 = unit(np.cross(tan, ref)); e2 = np.cross(tan, e1)
    return e1, e2


def leaf_on_path(g, m, pts, t, az, elev, patch, roll=0.0, scale=None):
    pos, tan = pathpt(pts, t)
    e1, e2 = stem_frame(tan)
    radial = math.cos(az) * e1 + math.sin(az) * e2
    ydir = math.cos(elev) * radial + math.sin(elev) * tan
    nrm = tan * math.cos(elev) - radial * math.sin(elev)
    M = orient(pos, ydir, nrm) @ Ry(roll)
    if scale is not None:
        M = M @ Sc(scale)
    g.add(m, patch, M)
    return M


def petal_ring(g, m, n, L, W, rng, r0=0.0, z0=0.0, elev=0.2, elev_j=0.05, yaw0=None, xf=None, jit=0.12,
               lj=0.1, wj=0.1, roll=0.0, **bk):
    xf = np.eye(4) if xf is None else xf
    yaw0 = rng.uniform(0, TAU) if yaw0 is None else yaw0
    for i in range(n):
        ang = yaw0 + TAU * i / n + rng.uniform(-jit, jit) * TAU / n
        el = rv(elev, rng) + rng.normal(0, elev_j)
        radial = np.array([math.cos(ang), math.sin(ang), 0.0])
        Z = np.array([0, 0, 1.0])
        ydir = math.cos(el) * radial + math.sin(el) * Z
        nrm = -math.sin(el) * radial + math.cos(el) * Z
        M = orient(r0 * radial + np.array([0, 0, z0]), ydir, nrm)
        if roll:
            M = M @ Ry(rng.normal(0, roll))
        kw = {k: rv(v, rng) for k, v in bk.items()}
        p = blade(L * rng.uniform(1 - lj, 1 + lj), W * rng.uniform(1 - wj, 1 + wj), **kw)
        g.add(m, p, xf @ M)


def rosette(g, m, n, L, W, rng, elev=(0.25, 0.7), r0=0.004, xf=None, **bk):
    xf = np.eye(4) if xf is None else xf
    a0 = rng.uniform(0, TAU)
    for i in range(n):
        ang = a0 + TAU * i / n + rng.uniform(-0.3, 0.3)
        el = rv(elev, rng)
        radial = np.array([math.cos(ang), math.sin(ang), 0.0]); Z = np.array([0, 0, 1.0])
        ydir = math.cos(el) * radial + math.sin(el) * Z
        nrm = -math.sin(el) * radial + math.cos(el) * Z
        M = orient(r0 * radial, ydir, nrm)
        kw = {k: rv(v, rng) for k, v in bk.items()}
        g.add(m, blade(L * rng.uniform(0.75, 1.15), W * rng.uniform(0.85, 1.1), **kw), xf @ M)


# ---------------------------------------------------------------- run/preview
class Preview:
    def __init__(self, water=False, fast=True):
        sc = bpy.context.scene
        self.sc = sc
        w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
        bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.5, 0.62, 0.8, 1); bg.inputs[1].default_value = 1.0
        sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.5
        so = bpy.data.objects.new('sun', sun); so.rotation_euler = (math.radians(48), math.radians(8), math.radians(30))
        sc.collection.objects.link(so)
        bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
        g = bpy.context.object; g.name = '_ground'
        g.data.materials.append(make_mat('_groundmat', '#2f6fa0' if water else '#66703f', rough=0.3 if water else 0.95))
        cam = bpy.data.cameras.new('cam'); cam.lens = 50
        self.cam = bpy.data.objects.new('cam', cam); sc.collection.objects.link(self.cam)
        sc.camera = self.cam
        sc.render.engine = 'CYCLES'; sc.cycles.samples = 14; sc.cycles.device = 'CPU'
        try:
            sc.cycles.use_denoising = True
        except Exception:
            pass
        sc.cycles.max_bounces = 3
        sc.view_settings.view_transform = 'Standard'
        sc.render.image_settings.file_format = 'PNG'

    def shoot(self, path, objs, res=(900, 520), close=False, yaw=0.0, cam_h=0.45, cdist=None, tgt=None, celev=None):
        sc = self.sc
        # layout in a row
        rad = []
        hs = []
        for o in objs:
            V = np.array([v.co[:] for v in o.data.vertices])
            rad.append(max(0.03, np.percentile(np.hypot(V[:, 0], V[:, 1]), 96)))
            hs.append(V[:, 2].max())
        gap = 0.06 * max(rad)
        tot = sum(2 * r for r in rad) + gap * (len(objs) - 1)
        x = -tot / 2
        for o, r in zip(objs, rad):
            o.location = (x + r, 0, 0); x += 2 * r + gap
        H = max(hs)
        if close:
            o0 = objs[0]
            V = np.array([v.co[:] for v in o0.data.vertices])
            top = V[V[:, 2] > H * 0.72]
            c = top.mean(0) + np.array(o0.location)
            sz = max(np.ptp(top[:, 0]), np.ptp(top[:, 1]), np.ptp(top[:, 2]), 0.03)
            d = sz * 2.6 if cdist is None else cdist
            tg = c if tgt is None else tgt
            ce = 0.35 if celev is None else celev
            cl = (tg[0], tg[1] - d * math.cos(ce), tg[2] + d * math.sin(ce) * 1.0)
        else:
            d = max(tot / 0.72, H / 0.40) * 1.12
            tg = np.array([0, 0, H * 0.46]) if tgt is None else tgt
            cl = (0, -d * math.cos(0.18), tg[2] + d * math.sin(0.18) + (cam_h - 0.45) * 0.0)
        self.cam.location = cl
        dvec = Vector(tg) - Vector(cl)
        self.cam.rotation_euler = dvec.to_track_quat('-Z', 'Y').to_euler()
        sc.render.resolution_x, sc.render.resolution_y = res
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        return path


def run_group(bundle, DEFS, argv=None):
    """DEFS: list of dict(sp=, fn=, variants=['a','b'], ko=, weight=, habitat=, sway=, lod=bool)
    args: --only a,b  --preview  --close  --noexport  --water  --nolod"""
    argv = sys.argv[sys.argv.index('--') + 1:] if argv is None and '--' in sys.argv else (argv or [])
    only = None
    if '--only' in argv:
        only = argv[argv.index('--only') + 1].split(',')
    do_prev = '--preview' in argv
    do_close = '--close' in argv
    do_export = ('--noexport' not in argv) and only is None or '--export' in argv
    nolod = '--nolod' in argv
    allobjs = []
    meta_parts = {}
    meta_species = {}
    report = []
    by_sp = {}
    t0 = time.time()
    for d in DEFS:
        if only and d['sp'] not in only:
            continue
        meta_species[d['sp']] = {'ko': d['ko'], 'variants': [], 'weight': d.get('weight', 0.5), 'habitat': d.get('habitat', 'meadow')}
        for v in d['variants']:
            for lod in ([0, 1] if d.get('lod') and not nolod else [0]):
                set_lod(lod)
                name = f"{d['sp']}_{v}" + ('_lod1' if lod else '')
                seed = (hash(d['sp']) % 1000) * 7 + ord(v[0]) if False else sum(ord(c) for c in d['sp']) * 13 + ord(v[0]) * 101
                rng = np.random.RandomState(seed)
                globals()['RNG'] = np.random.RandomState(seed + 7)
                g = d['fn'](v, rng)
                ob = g.to_obj(name)
                h, r97, rmax, _ = g.bounds()
                tr = g.tris()
                meta_parts[name] = {'species': d['sp'], 'variant': v, 'lod': lod, 'ko': d['ko'], 'height_m': round(h, 3),
                                    'radius_m': round(r97, 3), 'weight': d.get('weight', 0.5) * (1 if not lod else 1),
                                    'habitat': d.get('habitat', 'meadow'),
                                    'sway': {'pivot': 'base', 'amount': d.get('sway', 0.5)}, 'tris': tr}
                if lod:
                    meta_parts[name]['lod_of'] = f"{d['sp']}_{v}"
                else:
                    meta_species[d['sp']]['variants'].append(v)
                allobjs.append(ob)
                by_sp.setdefault(d['sp'], []).append((lod, ob))
                report.append((name, tr, round(h, 2), round(r97, 2)))
    set_lod(0)
    print('BUILD_TIME', round(time.time() - t0, 1))
    for r in report:
        print('PART', *r)
    if do_export:
        meta = {'bundle': bundle, 'parts': meta_parts, 'species': meta_species}
        st = export_bundle(f'{OUT_DIR}/{bundle}.json', allobjs, meta=meta)
        with open(f'{OUT_DIR}/{bundle}.meta.json', 'w') as f:
            json.dump(meta, f, indent=1, ensure_ascii=False)
        print('EXPORT', st)
    if do_prev:
        pv = Preview(water='--water' in argv)
        os.makedirs(PREVIEW_DIR, exist_ok=True)
        for sp, lst in by_sp.items():
            for o in allobjs:
                o.hide_render = True
            base = [o for lod, o in lst if not lod]
            for o in base:
                o.hide_render = False
            pv.shoot(f'{PREVIEW_DIR}/{bundle}_{sp}.png', base)
            if do_close:
                pv.shoot(f'{PREVIEW_DIR}/{bundle}_{sp}_close.png', base[:1], close=True, res=(800, 600), celev=(1.0 if '--top' in argv else None))
            if '--lodprev' in argv:
                lods = [o for lod, o in lst if lod]
                if lods:
                    for o in allobjs: o.hide_render = True
                    for o in lods: o.hide_render = False
                    pv.shoot(f'{PREVIEW_DIR}/{bundle}_{sp}_lod1.png', lods)
        print('PREVIEW done', round(time.time() - t0, 1))
    return meta_parts
