"""Tableware, cutlery, glass, candles, flowers..  all functions place geometry into the global accumulators (kt_lib)."""
from kt_lib import *

GLAZE = {'cream': '#ece4d0', 'blue': '#3d5f8e', 'cobalt': '#2a4a85', 'red': '#a8392c', 'green': '#4e6e4a', 'ochre': '#c49a45',
         'brown': '#6b4528', 'white': '#f2eee4', 'teal': '#3f7770', 'rose': '#c98a7a'}


def G(k):
    return C(GLAZE[k]) if k in GLAZE else C(k)


def radial_cfn(Mx, bands, base, jitter=0.0, seed=0):
    """colour by local radius / height: bands = [(r0, r1, colour), ...] on local xy radius; speckle optional"""
    inv = Mx.inverted()

    def f(p):
        l = inv @ p
        r = math.hypot(l.x, l.y)
        c = base
        for (r0, r1, cc) in bands:
            if r0 <= r < r1:
                c = cc
        if jitter:
            k = 1 + jitter * fbm(l.x, l.y, l.z, 60, seed, 1)
            c = (c[0] * k, c[1] * k, c[2] * k)
        return c
    return f


def zband_cfn(Mx, bands, base, jitter=0.0, seed=0):
    inv = Mx.inverted()

    def f(p):
        l = inv @ p
        c = base
        for (z0, z1, cc) in bands:
            if z0 <= l.z < z1:
                c = cc
        if jitter:
            k = 1 + jitter * fbm(l.x, l.y, l.z, 40, seed, 1)
            c = (c[0] * k, c[1] * k, c[2] * k)
        return c
    return f


# ---------------------------------------------------------------- plates & bowls
def plate(pos, r=0.12, glaze='cream', rim='blue', rot=None, seg=22, stack=1, deep=False, tilt=None, used=False, lod=0, chip=None):
    """lod 0 hero (full profile), 1 mid, 2 far (coarse).  rim band on crisp split rings"""
    Mx = xf(pos, rot)
    g = G(glaze)
    rc = G(rim) if rim else g
    for s in range(stack):
        if deep:
            prof = [(0.001, 0.012), (r * 0.45, 0.012), (r * 0.5, 0.0), (r * 0.58, 0.0), (r * 0.62, 0.006), (r * 0.9, 0.028), (r, 0.032),
                    (r, 0.0355), (r * 0.965, 0.0365), (r * 0.9, 0.0335), (r * 0.64, 0.0105), (r * 0.45, 0.0085), (0.001, 0.0082)]
        elif lod == 0:
            prof = [(0.001, 0.0075), (r * 0.5, 0.0085), (r * 0.52, 0.0), (r * 0.58, 0.0), (r * 0.6, 0.0035), (r * 0.8, 0.010), (r * 0.97, 0.0175),
                    (r, 0.0185), (r, 0.0215), (r * 0.965, 0.0225), (r * 0.82, 0.0185), (r * 0.64, 0.0095), (r * 0.5, 0.0072), (0.001, 0.0066)]
        elif lod == 1:
            prof = [(0.001, 0.0072), (r * 0.52, 0.0, ), (r * 0.6, 0.0), (r * 0.97, 0.0175), (r, 0.0185), (r, 0.0215), (r * 0.965, 0.0225), (r * 0.64, 0.0095), (0.001, 0.0066)]
        else:
            prof = [(0.001, 0.0), (r * 0.6, 0.0), (r, 0.0185), (r, 0.0215), (r * 0.64, 0.0095), (0.001, 0.0085)]
        M2 = Mx @ Matrix.Translation((0, 0, s * 0.0108))
        if lod >= 2:
            bands = [(r * 0.93, r * 1.2, rc)] if rim else []
            spl = ('r', [r * 0.93]) if rim else None
        else:
            bands = [(r * 0.86, r * 0.885, rc), (r * 0.935, r * 1.2, rc)] if rim else []
            spl = ('r', [r * 0.86, r * 0.885, r * 0.935]) if rim else None
        cfn = radial_cfn(M2, bands, g, 0.03, s)
        if chip is not None and s == 0:
            # hand-modelled chip: notch pulled out of the rim, bare brown earthenware showing
            prof2 = prof_split(prof, spl[0], spl[1]) if spl else prof
            bm = lathe_bm(prof2, seg, 1.0, False)
            ca = math.radians(chip)
            for v in bm.verts:
                a = math.atan2(v.co.y, v.co.x)
                da = abs((a - ca + math.pi) % TAU - math.pi)
                if da < TAU / seg * 1.1 and math.hypot(v.co.x, v.co.y) > r * 0.9 and v.co.z > 0.012:
                    v.co.x *= 0.955; v.co.y *= 0.955; v.co.z -= 0.0035
            inv = M2.inverted()

            def cfn2(p, c0=cfn):
                l = inv @ p
                a = math.atan2(l.y, l.x)
                da = abs((a - ca + math.pi) % TAU - math.pi)
                if da < TAU / seg * 1.1 and math.hypot(l.x, l.y) > r * 0.9 and l.z > 0.012 and False:
                    return (0.45, 0.28, 0.16)
                return c0(p)
            put('ceramic', bm, M2, cfn=cfn2, skip_down=True)
            bm.free()
        else:
            lathe('ceramic', None, prof, seg, M=M2, cfn=cfn, cap=False, split=spl)


def bowl(pos, r=0.08, h=0.05, glaze='cream', rim=None, rot=None, seg=20, contents=None, M=None, speckle=0.0, stripe=None):
    Mx = M if M is not None else xf(pos, rot)
    g = G(glaze)
    t = 0.0035
    prof = [(0.001, 0.0035), (r * 0.36, 0.0035), (r * 0.38, 0.0), (r * 0.46, 0.0), (r * 0.5, 0.004), (r * 0.8, h * 0.45), (r * 0.97, h * 0.85),
            (r, h), (r - t * 0.4, h + 0.001), (r - t, h - 0.002), (r * 0.92, h * 0.82), (r * 0.74, h * 0.42), (r * 0.4, 0.008), (0.001, 0.0065)]
    if seg <= 16:
        prof = [(0.001, 0.0), (r * 0.42, 0.0), (r * 0.5, 0.004), (r * 0.95, h * 0.85), (r, h), (r - t, h - 0.002), (r * 0.7, h * 0.4), (0.001, 0.0065)]
        seg = min(seg, 14)
    bands = []
    spl = None
    cf = None
    if rim:
        bands.append((r * 0.93, r * 1.2, G(rim)))
        cf = radial_cfn(Mx, bands, g, speckle, 3)
        spl = ('r', [r * 0.93])
    elif stripe:
        zb = [(h * 0.55, h * 0.64, G(stripe)), (h * 0.7, h * 0.78, G(stripe))]
        cf = zband_cfn(Mx, zb, g, speckle, 4)
        spl = ('z', [h * 0.55, h * 0.64, h * 0.7, h * 0.78])
    else:
        cf = radial_cfn(Mx, [], g, speckle if speckle else 0.03, 3)
    lathe('ceramic', None, prof, seg, M=Mx, cfn=cf, cap=False, split=spl)
    if contents:
        kind, col = contents[0], contents[1]
        zt = h * 0.7
        rr = r * (0.97 - 0.19 * (1 - 0.7))
        rr = r * 0.82
        if kind == 'soup':
            lathe('liquid', None, [(0.001, zt), (rr, zt), (rr, zt - 0.002)], 20, M=Mx, col=col, cap=False)
        elif kind == 'heap':   # porridge / flour mound
            prof2 = [(0.001, zt + h * 0.2), (rr * 0.5, zt + h * 0.16), (rr * 0.9, zt + h * 0.04), (rr, zt - 0.004)]
            lathe('food_matte', None, prof2, 18, M=Mx, col=col, cap=False)
        elif kind == 'water':
            lathe('water', None, [(0.001, zt), (rr, zt), (rr, zt - 0.002)], 20, M=Mx, col=(1, 1, 1), cap=False)


def mug(pos, glaze='blue', r=0.04, h=0.09, rot=None, fill=None, seg=18, rim=None, M=None, enamel=False, handle_side=1):
    Mx = M if M is not None else xf(pos, rot)
    g = G(glaze)
    t = 0.0032
    prof = [(0.001, 0.004), (r * 0.82, 0.004), (r * 0.84, 0.0), (r * 0.9, 0.0), (r * 0.98, 0.006), (r * 1.04, h * 0.5), (r, h - 0.003), (r, h), (r - t * 0.5, h + 0.0008),
            (r - t, h - 0.002), (r * 0.95, h * 0.5), (r * 0.8, 0.008), (0.001, 0.0075)]
    lowlod = seg <= 16
    if lowlod:
        prof = [(0.001, 0.0), (r * 0.88, 0.0), (r * 1.03, h * 0.5), (r, h), (r - t, h - 0.002), (r * 0.9, h * 0.4), (0.001, 0.0075)]
        seg = min(seg, 12)
    bands = [(0, 9, g)]
    cf = zband_cfn(Mx, [(h - 0.012, h + 0.01, G(rim))] if rim else [], g, 0.03, 2)
    lathe('ceramic', None, prof, seg, M=Mx, cfn=cf, cap=False, split=('z', [h - 0.012]) if rim else None)
    hp = bez((r * 1.0, 0, h * 0.82), (r * 1.7, 0, h * 0.95), (r * 1.85, 0, h * 0.25), (r * 1.0, 0, h * 0.2), 5 if lowlod else 9)
    hp = [Vector((handle_side * p.x, p.y, p.z)) for p in hp]
    npf = 4 if lowlod else 8
    sweep('ceramic', [(0.0042 * math.cos(TAU * k / npf), 0.0031 * math.sin(TAU * k / npf)) for k in range(npf)], hp, M=Mx, cfn=cf, up=(0, 1, 0))
    if fill:
        lathe('liquid', None, [(0.001, h * 0.82), (r * 0.9, h * 0.82), (r * 0.9, h * 0.8)], 14, M=Mx, col=fill, cap=False)


def cup_saucer(pos, glaze='cream', rim='blue', rot=None, fill=None, seg=14):
    plate(pos, r=0.07, glaze=glaze, rim=rim, rot=rot, seg=min(seg, 14), lod=2)
    Mx = xf(pos, rot) @ Matrix.Translation((0, 0, 0.0095))
    # teacup: wider, shallower
    g = G(glaze)
    r, h = 0.039, 0.055
    prof = [(0.001, 0.0), (r * 0.55, 0.0), (r * 0.9, h * 0.35), (r * 1.04, h), (r * 0.98, h - 0.002), (r * 0.86, h * 0.35), (0.001, 0.0065)]
    cf = zband_cfn(Mx, [(h * 0.82, h + 0.01, G(rim))] if rim else [], g, 0.03, 5)
    lathe('ceramic', None, prof, seg, M=Mx, cfn=cf, cap=False, split=('z', [h * 0.82]) if rim else None)
    hp = bez((r * 0.98, 0, h * 0.85), (r * 1.7, 0, h * 0.9), (r * 1.55, 0, h * 0.25), (r * 0.88, 0, h * 0.3), 8)
    sweep('ceramic', [(0.0035 * math.cos(TAU * k / 6), 0.0028 * math.sin(TAU * k / 6)) for k in range(6)], hp, M=Mx, cfn=cf, up=(0, 1, 0))
    if fill:
        lathe('liquid', None, [(0.001, h * 0.78), (r * 0.9, h * 0.78), (r * 0.9, h * 0.76)], 14, M=Mx, col=fill, cap=False)


def goblet(pos, r=0.032, h=0.11, kind='tumbler', fill=None, fill_h=0.5, rot=None, seg=16):
    Mx = xf(pos, rot)
    if kind == 'tumbler':
        prof = [(0.001, 0.0), (r * 0.7, 0.0), (r * 0.74, 0.0015), (r * 0.76, 0.012), (r * 0.9, h * 0.4), (r, h - 0.002), (r, h), (r - 0.0022, h), (r - 0.0022, h - 0.002),
                (r * 0.88 - 0.0022, h * 0.4), (r * 0.72, 0.012), (0.001, 0.0095)]
        fh = 0.0095 + (h - 0.0095) * fill_h
    else:   # wine goblet
        prof = [(0.001, 0.0), (r * 1.0, 0.0), (r * 1.05, 0.002), (r * 0.7, 0.006), (r * 0.18, 0.012), (r * 0.12, h * 0.38), (r * 0.2, h * 0.43),
                (r * 0.8, h * 0.52), (r * 1.15, h * 0.72), (r * 1.1, h * 0.97), (r * 1.1 - 0.0016, h * 0.97), (r * 1.05 - 0.0016, h * 0.7), (r * 0.7, h * 0.54), (0.001, h * 0.5)]
        fh = h * 0.7
    lathe('glass', None, prof, seg, M=Mx, cap=False)
    if fill:
        rr = r * (0.88 - 0.0022 / r) if kind == 'tumbler' else r * 1.0
        mat = 'liquid' if fill != 'water' else 'water'
        lathe(mat, None, [(0.001, fh), (rr * 0.98, fh), (rr, fh - 0.003), (rr * 0.8, 0.0125)], seg, M=Mx, col=(1, 1, 1) if fill == 'water' else fill, cap=False)


# ---------------------------------------------------------------- jug, teapot, pitcher
def jug(pos, r=0.07, h=0.2, glaze='blue', rot=None, seg=22, band=True):
    Mx = xf(pos, rot)
    g = G(glaze)
    prof = [(0.001, 0.003), (r * 0.7, 0.004), (r * 0.72, 0.0), (r * 0.8, 0.0), (r * 0.95, 0.012), (r * 1.1, h * 0.28), (r * 1.18, h * 0.46), (r * 1.1, h * 0.68),
            (r * 0.78, h * 0.86), (r * 0.62, h * 0.93), (r * 0.7, h * 0.985), (r * 0.7, h), (r * 0.62, h - 0.002), (r * 0.56, h * 0.9), (r * 0.7, h * 0.7), (0.001, h * 0.6)]
    cf = zband_cfn(Mx, [(h * 0.4, h * 0.45, G('cream')), (h * 0.55, h * 0.58, G('cream')), (h * 0.95, h * 1.1, G('cream'))] if band else [], g, 0.04, 7)
    prof = prof_split(prof, 'z', [h * 0.4, h * 0.45, h * 0.55, h * 0.58, h * 0.95]) if band else prof
    bm = lathe_bm(prof, seg)
    # pinched spout: pull rim vertices at +x outward & up
    for v in bm.verts:
        zf = v.co.z / h
        if zf > 0.86 and v.co.x > 0:
            w = math.exp(-((math.atan2(v.co.y, v.co.x)) / 0.55) ** 2)
            v.co.x += 0.03 * w * (zf - 0.86) / 0.14 * 1.5
            v.co.z += 0.008 * w * (zf - 0.86) / 0.14
    put('ceramic', bm, Mx, cfn=cf)
    bm.free()
    hp = bez((-r * 0.95, 0, h * 0.82), (-r * 1.9, 0, h * 0.95), (-r * 2.1, 0, h * 0.25), (-r * 1.12, 0, h * 0.28), 12)
    sweep('ceramic', [(0.0075 * math.cos(TAU * k / 8), 0.0042 * math.sin(TAU * k / 8)) for k in range(8)], hp, M=Mx, cfn=cf, up=(0, 1, 0),
          scale=lambda t: (1 + 0.3 * math.sin(t * math.pi), 1))


def teapot(pos, rot=None, glaze='white', r=0.075, seg=20):
    Mx = xf(pos, rot)
    g = G(glaze)
    h = r * 1.25
    prof = [(0.001, 0.0), (r * 0.5, 0.0), (r * 0.62, 0.004), (r * 0.9, h * 0.2), (r * 1.0, h * 0.45), (r * 0.9, h * 0.75), (r * 0.62, h * 0.92), (r * 0.55, h * 0.94),
            (r * 0.5, h * 0.9), (r * 0.5, h * 0.84), (0.001, h * 0.84)]
    cf = zband_cfn(Mx, [(h * 0.5, h * 0.56, G('blue')), (h * 0.35, h * 0.4, G('blue'))], g, 0.03, 9)
    lathe('ceramic', None, prof, seg, M=Mx, cfn=cf, cap=False, split=('z', [h * 0.5, h * 0.56, h * 0.35, h * 0.4]))
    # lid + knob
    lathe('ceramic', None, [(r * 0.56, h * 0.94), (r * 0.5, h * 0.99), (r * 0.25, h * 1.04), (r * 0.08, h * 1.07), (r * 0.12, h * 1.1), (r * 0.1, h * 1.14), (0.001, h * 1.15)], 14, M=Mx, cfn=cf, cap=False)
    sp = bez((r * 0.8, 0, h * 0.28), (r * 1.3, 0, h * 0.3), (r * 1.4, 0, h * 0.75), (r * 1.85, 0, h * 0.95), 10)
    sweep('ceramic', [(1 * math.cos(TAU * k / 8), 1 * math.sin(TAU * k / 8)) for k in range(8)], sp, M=Mx, cfn=cf,
          scale=[(r * (0.17 - 0.09 * (i / 10)), r * (0.17 - 0.09 * (i / 10))) for i in range(11)], caps=False)
    hp = bez((-r * 0.85, 0, h * 0.8), (-r * 1.7, 0, h * 0.95), (-r * 1.8, 0, h * 0.2), (-r * 0.9, 0, h * 0.25), 10)
    sweep('ceramic', [(0.0065 * math.cos(TAU * k / 8), 0.004 * math.sin(TAU * k / 8)) for k in range(8)], hp, M=Mx, cfn=cf, up=(0, 1, 0))
    return Mx @ Vector((r * 1.85, 0, h * 0.95))


# ---------------------------------------------------------------- cutlery
def _flat_poly(pts, thick, bev=0.0):
    """closed 2D polygon (x,y) -> extruded thin plate, z 0..thick"""
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, 0)) for x, y in pts]
    f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    top = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    for v in top:
        v.co.z = thick
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def spoon(pos, rot=0, L=0.17, mat='steel', tilt=None, bowl_len=0.05, wood=False):
    Mx = xf(pos, (tilt if tilt is not None else (0, 0, rot)) if not isinstance(rot, tuple) else rot)
    bw = 0.0175
    # bowl: dished ellipse
    prof = [(0.001, -0.0052), (0.35, -0.0048), (0.7, -0.003), (1.0, 0.0), (1.0, 0.0012), (0.7, -0.0017), (0.35, -0.0036), (0.001, -0.0040)]
    prof = [(a * bw if a > 0.01 else 0.001, z) for a, z in prof]
    lathe(mat, None, prof, 14, M=Mx @ Matrix.Translation((0, bowl_len * 0.5 + 0.0, 0.0052 + 0.0)), scale=(1.0, bowl_len / 2 / bw, 1.0), cap=False, auto=False)
    # handle
    hp = [Vector((0, bowl_len + 0.0, 0.001)), Vector((0, bowl_len + 0.03, 0.003)), Vector((0, L * 0.7, 0.007)), Vector((0, L, 0.011))]
    hp = polyline_smooth(hp, 4)
    n = len(hp)
    sweep(mat, [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)], hp, M=Mx, scale=[(0.0024, 0.007 + 0.009 * (i / n) ** 2) for i in range(n)], up=(0, 0, 1))


def fork(pos, rot=0, L=0.18, mat='steel'):
    Mx = xf(pos, rot)
    hp = polyline_smooth([Vector((0, 0.05, 0.002)), Vector((0, 0.09, 0.004)), Vector((0, L * 0.75, 0.008)), Vector((0, L, 0.011))], 4)
    n = len(hp)
    sweep(mat, [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)], hp, M=Mx, scale=[(0.0024, 0.0075 + 0.008 * (i / n) ** 2) for i in range(n)], up=(0, 0, 1))
    # head with 4 tines
    for i in range(4):
        x = (i - 1.5) * 0.0052
        tp = [Vector((x * 0.9, 0.05, 0.002)), Vector((x, 0.035, 0.0025)), Vector((x * 1.05, 0.015, 0.0035)), Vector((x * 1.05, -0.002, 0.004))]
        sweep(mat, [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)], tp, M=Mx, scale=[(0.0022, 0.0034)] * 4, up=(0, 0, 1))
    box(mat, None, (0.024, 0.008, 0.0042), M=Mx @ Matrix.Translation((0, 0.05, 0.002)), bev=0.0008)


def knife(pos, rot=0, L=0.2, hand=0.095, wood='wood_dark', brass=True, rivets=3, M=None):
    Mx = M if M is not None else xf(pos, rot)
    bl = L - hand
    pts = [(-0.0045, 0), (0.0045, 0), (0.0065, 0.004), (0.0062, bl * 0.5), (0.005, bl * 0.9), (0.0, bl), (-0.0035, bl * 0.7), (-0.0045, bl * 0.2)]
    pts = [(x, y + hand) for x, y in pts]
    bm = _flat_poly([(y - hand, x) for x, y in [(p[0], p[1]) for p in pts]], 0.0018) if False else None
    bm = bmesh.new()
    # blade: polygon in (x,y) with thickness taper (spine thick, edge thin) -> build via wedge sections
    spine = [(-0.0035, 0.0), (0.0, 0.0)]
    verts = []
    prof_pts = [(0.0058, hand), (0.0062, hand + bl * 0.3), (0.0056, hand + bl * 0.75), (0.0035, hand + bl * 0.92), (0.0, hand + bl)]
    prof_y = [p[1] for p in prof_pts]
    # spine side at x=-0.0045 (back) edge side at +x
    rows = []
    for (w, y) in prof_pts:
        rows.append(y)
    # simple: two triangular-prism strips
    vs_back_t, vs_back_b, vs_edge = [], [], []
    xs_back = -0.0048
    edge_x = [0.0058, 0.0062, 0.0056, 0.0035, 0.0]
    ysp = [hand, hand + bl * 0.3, hand + bl * 0.75, hand + bl * 0.92, hand + bl]
    sp_x = [-0.0048, -0.0048, -0.0045, -0.0035, -0.0003]
    for i in range(5):
        vs_back_t.append(bm.verts.new((sp_x[i], ysp[i], 0.0018)))
        vs_back_b.append(bm.verts.new((sp_x[i], ysp[i], -0.0018)))
        vs_edge.append(bm.verts.new((edge_x[i], ysp[i], 0.0)))
    for i in range(4):
        for (a, b, c, d) in ((vs_back_t, vs_back_b, vs_edge, None),):
            pass
        bm.faces.new([vs_back_t[i], vs_back_t[i + 1], vs_edge[i + 1], vs_edge[i]])             # top bevel
        bm.faces.new([vs_back_b[i], vs_edge[i], vs_edge[i + 1], vs_back_b[i + 1]])             # bottom bevel
        bm.faces.new([vs_back_t[i], vs_back_b[i], vs_back_b[i + 1], vs_back_t[i + 1]])         # spine
    bm.faces.new([vs_back_t[0], vs_edge[0], vs_back_b[0]])
    bm.faces.new([vs_back_t[4], vs_back_b[4], vs_edge[4]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    put('steel', bm, Mx)
    bm.free()
    # bolster + handle scales + rivets
    box('steel', None, (0.0125, 0.012, 0.0075), M=Mx @ Matrix.Translation((0, hand + 0.002, 0)), bev=0.002)
    for s in (-1, 1):
        sw = [(-0.0065, 0), (0.0065, 0), (0.0075, hand * 0.45), (0.0065, hand * 0.9), (0.0, hand), (-0.0065, hand * 0.9), (-0.0075, hand * 0.45)]
        hb = _flat_poly(sw, 0.0036)
        put(wood, hb, Mx @ Matrix.Translation((0, 0, s * 0.0018 + (0.0 if s > 0 else -0.0036))), g=1)
        hb.free()
    if rivets:
        for i in range(rivets):
            cyl('brass', None, 0.0022, 0.0105, axis='z', seg=8, M=Mx @ Matrix.Translation((0, 0.012 + i * (hand - 0.024) / max(rivets - 1, 1), 0)))


def cutlery_setting(pos, rot, n=1):
    """fork left, knife+spoon right of a place at pos (plate centre); rot = facing"""
    Mx = xf(pos, rot)
    fork(Mx @ Vector((-0.12, -0.2, 0.0)), rot=rot, L=0.17)
    knife(Mx @ Vector((0.105, -0.19, 0.0)), rot=rot, L=0.2)
    spoon(Mx @ Vector((0.135, -0.19, 0.0)), rot=rot, L=0.17)


# ---------------------------------------------------------------- candle / lantern
_LAMP = [0]


def flame_part(pos, sc=1.0, name=None, inten=0.8, dist=5.0, color=(1.0, 0.68, 0.36), light_on=True):
    _LAMP[0] += 1
    n = name or 'lamp_kit_%d' % _LAMP[0]
    saved = part_begin()
    prof = [(0, -0.013), (0.0055, -0.009), (0.0085, -0.002), (0.0065, 0.010), (0.003, 0.021), (0, 0.030)]
    lathe('flame', pos, [(r * sc, z * sc) for r, z in prof], seg=8, cap=False)
    part_end(saved, n, pos)
    if light_on:
        light(n, pos, color, inten, dist)
    return n


def candlestick(pos, h=0.16, cl=0.12, flame=True, name=None, inten=0.7, dist=4.5, wax_burn=True, tall=True):
    """turned brass stick + beeswax candle with drips"""
    p = Vector(pos)
    prof = [(0.001, 0), (0.042, 0.0), (0.046, 0.004), (0.04, 0.012), (0.018, 0.02), (0.012, 0.03), (0.016, 0.036), (0.011, 0.044), (0.0095, h * 0.55), (0.014, h * 0.62),
            (0.0105, h * 0.7), (0.011, h * 0.85), (0.016, h * 0.93), (0.021, h), (0.0185, h + 0.004), (0.015, h + 0.004)]
    lathe('brass', p, prof, 14, cap=True)
    # drip pan cup at top
    cr = 0.0112
    top = h + 0.003
    lathe('wax', p + Vector((0, 0, top)), [(cr, 0), (cr * 1.0, cl * 0.97), (cr * 0.92, cl * 0.995), (cr * 0.55, cl), (0.001, cl - 0.001)], 12, cap=False,
          cfn=lambda q: (1.0, 0.94 - 0.03 * fbm(q.x, q.y, q.z, 80, 1, 1), 0.78))
    # wax drips (tubes down the side)
    for i in range(3):
        a = rnd.uniform(0, TAU)
        ln = rnd.uniform(0.015, 0.04)
        x0 = cr * 1.02
        tube('wax', [p + Vector((x0 * math.cos(a), x0 * math.sin(a), top + cl - 0.002)), p + Vector((x0 * 1.18 * math.cos(a), x0 * 1.18 * math.sin(a), top + cl - ln * 0.6)),
                     p + Vector((x0 * 1.1 * math.cos(a), x0 * 1.1 * math.sin(a), top + cl - ln))], [0.0016, 0.0022, 0.0030], seg=5)
    # wick
    tube('ink', [p + Vector((0, 0, top + cl - 0.001)), p + Vector((0.0008, 0, top + cl + 0.007))], 0.0008, seg=4)
    if flame:
        return flame_part(p + Vector((0, 0, top + cl + 0.013)), 1.0, name=name, inten=inten, dist=dist)


def lantern(pos, h=0.3, w=0.16, chain_to=None, name=None, inten=1.6, dist=8.0, hang=True):
    """hanging iron/brass lantern with glass panes, dome, ring, rivets, candle.  pos = bottom centre."""
    p = Vector(pos)
    hw = w / 2
    # base plate and legs
    box('iron_black', p + Vector((0, 0, 0.008)), (w, w, 0.016), bev=0.003)
    box('iron_black', p + Vector((0, 0, 0.02)), (w * 0.9, w * 0.9, 0.012), bev=0.002)
    for sx in (-1, 1):
        for sy in (-1, 1):
            q = p + Vector((sx * (hw - 0.008), sy * (hw - 0.008), 0))
            tube('iron_black', [q + Vector((0, 0, 0.026)), q + Vector((0, 0, h - 0.045))], 0.0045, seg=6)
            # rivets
            for z in (0.03, h * 0.5, h - 0.05):
                sphere('iron_black', q + Vector((0, 0, z)), 0.0042, seg=6, rings=3)
    # glass panes
    for (dx, dy, sx_, sy_) in ((0, -1, w - 0.02, 0.003), (0, 1, w - 0.02, 0.003), (-1, 0, 0.003, w - 0.02), (1, 0, 0.003, w - 0.02)):
        box('glass', p + Vector((dx * (hw - 0.007), dy * (hw - 0.007), h * 0.5 - 0.005)), (sx_, sy_, h - 0.09), bev=0, skip_down=False)
    # horizontal bars
    for z in (0.038, h - 0.04):
        for (sx_, sy_, dx, dy) in ((w - 0.006, 0.007, 0, 1), (w - 0.006, 0.007, 0, -1), (0.007, w - 0.006, 1, 0), (0.007, w - 0.006, -1, 0)):
            box('iron_black', p + Vector((dx * (hw - 0.005), dy * (hw - 0.005), z)), (sx_, sy_, 0.009), bev=0.0015)
    # roof: pyramid dome + chimney + ring
    roof = [(0.001, h - 0.03), (hw * 1.5, h - 0.03), (hw * 1.45, h - 0.018), (hw * 0.9, h + 0.02), (hw * 0.5, h + 0.045), (hw * 0.28, h + 0.05), (hw * 0.3, h + 0.06), (hw * 0.18, h + 0.075), (0.001, h + 0.075)]
    lathe('iron_black', p, roof, 4, rot=(0, 0, 45), cap=False, auto=False)
    lathe('iron_black', p, [(hw * 0.2, h + 0.07), (hw * 0.2, h + 0.1), (hw * 0.12, h + 0.104), (0.001, h + 0.104)], 10, cap=False)
    torus('iron_black', p + Vector((0, 0, h + 0.12)), 0.022, 0.0035, plane='xz', seg=14, rseg=6)
    top = p + Vector((0, 0, h + 0.145))
    if chain_to is not None:
        n_links = int((chain_to - top.z) / 0.028)
        link_chain(top, Vector((top.x, top.y, chain_to)))
    # candle inside
    cyl('wax', p + Vector((0, 0, 0.026 + 0.045)), 0.013, 0.09, seg=10, cfn=None)
    cyl('brass', p + Vector((0, 0, 0.028)), 0.02, 0.004, seg=10)
    return flame_part(p + Vector((0, 0, 0.026 + 0.09 + 0.013)), 1.5, name=name, inten=inten, dist=dist)


def _link_unit(r, L, NR=8, NP=3):
    """two interlocked links along +X (first in XY plane, second in XZ)"""
    unit = bmesh.new()
    prof = [(r * math.cos(TAU * j / NP), r * math.sin(TAU * j / NP)) for j in range(NP)]
    for k in range(2):
        P = []
        for i in range(NR):
            rx, ry = L * 0.5 * math.cos(TAU * i / NR), L * 0.22 * math.sin(TAU * i / NR)
            P.append(Vector((rx + L * 0.5 + L * 0.82 * k, ry if k == 0 else 0, ry if k == 1 else 0)))
        rings = []
        for i in range(NR):
            t_ = (P[(i + 1) % NR] - P[(i - 1) % NR]).normalized()
            ref = Vector((0, 0, 1)) if k == 0 else Vector((0, 1, 0))
            nrm = (ref - t_ * ref.dot(t_)).normalized()
            bn = t_.cross(nrm)
            rings.append([unit.verts.new(P[i] + nrm * pu + bn * pv) for pu, pv in prof])
        for i in range(NR):
            for j in range(NP):
                unit.faces.new([rings[i][j], rings[i][(j + 1) % NP], rings[(i + 1) % NR][(j + 1) % NP], rings[(i + 1) % NR][j]])
    bmesh.ops.recalc_face_normals(unit, faces=unit.faces[:])
    return unit


def link_chain(a, b, r=0.0028, L=0.038, mat='iron_black', sag=0.0):
    """chain of interlocked links: Array modifier (fit to curve length) + Curve modifier bending along the path"""
    a, b = Vector(a), Vector(b)
    if (b - a).length < 0.04:
        return
    unit = _link_unit(r, L)
    mid = (a + b) * 0.5 + Vector((0, 0, -sag))
    ch = array_curve(unit, [a, mid, b], spacing=0.9)
    put(mat, ch, Matrix.Identity(4))
    ch.free()
