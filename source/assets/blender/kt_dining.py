"""Dining set: plank table with breadboard ends and turned legs, 4 chairs, cloth-simulated runner, tableware, candle, lantern."""
from kt_lib import *
from kt_ware import *
from kt_food import *

TBL_POS = (-3.0, -2.6)
TBL_W, TBL_D, TBL_H = 1.35, 0.88, 0.76


def plank_bm(sx, sy, sz, bev=0.003, seg=2, maxlen=0.1, dent=0.0010, dscale=0.1, seed=None):
    bm = cube_bm(sx, sy, sz)
    bev_bm(bm, bev, seg)
    # subdivide long edges (anisotropic) so noise dents and AO vertex colours have density
    for axis in (0, 1, 2):
        es = [e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co)[axis]) > maxlen * 1.2 and
              abs((e.verts[0].co - e.verts[1].co)[axis]) > 0.9 * (e.verts[0].co - e.verts[1].co).length]
        if es:
            ln = max(abs((e.verts[0].co - e.verts[1].co)[axis]) for e in es)
            bmesh.ops.subdivide_edges(bm, edges=es, cuts=max(1, int(ln / maxlen) - 1 + 1), use_grid_fill=True)
    if dent:
        bm = disp(bm, dent, dscale, 3, seed_loc=None if seed is None else (seed * 3.7, seed * 1.3, 0.5), direction='Z')
    return bm


def turned(f, x, y, z0, prof, mat='wood_oak', seg=14, col=(1, 1, 1), cfn=None):
    f.lathe(mat, (x, y, z0), prof, seg=seg, col=col, cfn=cfn, cap=True)


def table_leg_profile(h, r=0.034):
    """turned leg (bottom->top): foot, ring, stretcher block, vase, ring, top square block handled separately"""
    s = r / 0.034
    return [(0.021 * s, 0), (0.027 * s, 0.006 * s), (0.029 * s, 0.016 * s), (0.02 * s, 0.03 * s), (0.017 * s, 0.04 * s), (0.026 * s, 0.062 * s), (0.03 * s, 0.085 * s), (0.026 * s, 0.108 * s),
            (0.02 * s, 0.123 * s), (0.026 * s, 0.128 * s), (0.026 * s, 0.136 * s),  # collar -> stretcher block begins at 0.14
            ]


def table_leg(f, x, y, h=0.72, mat='wood_oak', col=(1, 1, 1), seed=0):
    s = 1.0
    # lower foot (turned)
    prof1 = [(0.02, 0), (0.026, 0.006), (0.0285, 0.016), (0.0195, 0.032), (0.0165, 0.042), (0.025, 0.064), (0.0295, 0.088), (0.0255, 0.11), (0.021, 0.125), (0.0275, 0.132), (0.0275, 0.145)]
    lathe_screw(mat, None, prof1, 14, M=f.M @ Matrix.Translation((x, y, 0.0)), col=col)
    # square stretcher block
    f.box(mat, (x, y, 0.145 + 0.045), (0.056, 0.056, 0.09), bev=0.003, col=col, seg=2, g=2, skip_down=False)
    # long turned shaft with vase swell
    pr = [(0.0275, 0.0), (0.0235, 0.012), (0.0215, 0.05), (0.0235, 0.14), (0.029, 0.2), (0.031, 0.235), (0.0285, 0.27), (0.0235, 0.31), (0.021, 0.33), (0.0275, 0.345), (0.0275, 0.355),
          (0.0245, 0.362), (0.0245, 0.37)]
    lathe_screw(mat, None, pr, 14, M=f.M @ Matrix.Translation((x, y, 0.235)), col=col)
    # top square block (apron joint)
    f.box(mat, (x, y, 0.235 + 0.37 + 0.057), (0.066, 0.066, 0.114), bev=0.0035, col=col, seg=2, g=2, skip_down=False)
    # chamfer bead under the block
    f.cyl(mat, (x, y, 0.235 + 0.37 + 0.004), 0.034, 0.008, seg=14, col=shade(col, 0.95))


def dowel(f, x, y, z, axis='x', r=0.006, L=0.004, col=(0.8, 0.7, 0.55)):
    """round peg end flush with surface"""
    f.cyl('wood_dark', (x, y, z), r, L, axis=axis, seg=8, col=col)


def dining_table(pos=(-3.0, -2.6), rot=0):
    f = Fr((pos[0], pos[1], F), rot)
    W, D, H = TBL_W, TBL_D, TBL_H
    zt = H - 0.04
    n = 5
    pw = [0.168, 0.185, 0.172, 0.18, 0.175]
    sc = D / sum(pw)
    pw = [w * sc for w in pw]
    L = W - 0.19
    y = -D / 2
    rr = random.Random(3)
    tint = [(1.0, 0.97, 0.92), (0.93, 0.88, 0.82), (1.03, 1.0, 0.95), (0.96, 0.92, 0.86), (1.0, 0.95, 0.9)]
    for i in range(n):
        w = pw[i]
        yc = y + w / 2
        y += w
        bm = plank_bm(L, w - 0.0035, 0.04, bev=0.0032, seg=2, maxlen=0.14, dent=0.0004, dscale=0.25, seed=i + 1)
        dz = rr.uniform(-0.0006, 0.0006)
        cf = woodcol(tint[i], 0.12, 6, i, 0)
        put('wood_oak', bm, f.M @ Matrix.Translation((0, yc, zt + 0.02 + dz)), cfn=lambda p, cf=cf, i=i: cf(p), g=0)
        bm.free()
    # breadboard ends (grain across), with tongue & visible dowel pegs
    for s in (-1, 1):
        bm = plank_bm(0.088, D, 0.04, bev=0.0035, seg=2, maxlen=0.14, dent=0.0006, dscale=0.2, seed=20 + s)
        put('wood_oak', bm, f.M @ Matrix.Translation((s * (W / 2 - 0.044), 0, zt + 0.02)), cfn=woodcol((0.97, 0.92, 0.86), 0.12, 6, 7, 1), g=1)
        bm.free()
        # seam shadow line (dark gap)
        f.box('wood_dark', (s * (L / 2 + 0.0004), 0, zt + 0.0195), (0.002, D - 0.004, 0.039), bev=0, col=(0.3, 0.22, 0.15), skip_down=False)
        for k in range(4):
            yy = -D / 2 + 0.11 + k * (D - 0.22) / 3
            dowel(f, s * (L / 2 + 0.043 - 0.0), yy, zt + 0.0405, axis='z', r=0.0065, L=0.003, col=(0.62, 0.48, 0.34))
    # apron (rails) with bead moulding and scalloped lower edge on long sides
    ax = W / 2 - 0.075
    ay = D / 2 - 0.075
    for sy in (-1, 1):
        bm = plank_bm(W - 0.15, 0.024, 0.098, bev=0.003, seg=2, maxlen=0.09, dent=0.0003, dscale=0.2, seed=30 + sy)
        for v in bm.verts:   # gentle scallop on bottom edge
            if v.co.z < -0.04:
                v.co.z += 0.012 * (0.5 + 0.5 * math.cos(v.co.x * 2 * math.pi / 0.22))
        put('wood_oak', bm, f.M @ Matrix.Translation((0, sy * ay, zt - 0.05 - 0.0)), col=(0.93, 0.88, 0.82), g=0, skip_down=False)
        bm.free()
        f.box('wood_oak', (0, sy * (ay + 0.0145), zt - 0.016), (W - 0.15, 0.007, 0.012), bev=0.0025, seg=2, col=(1, 0.95, 0.9), g=0)   # bead
    for sx in (-1, 1):
        bm = plank_bm(0.024, D - 0.15, 0.098, bev=0.003, seg=2, maxlen=0.09, dent=0.0003, dscale=0.2, seed=40 + sx)
        put('wood_oak', bm, f.M @ Matrix.Translation((sx * ax, 0, zt - 0.05)), col=(0.9, 0.85, 0.8), g=1, skip_down=False)
        bm.free()
        f.box('wood_oak', (sx * (ax + 0.0145), 0, zt - 0.016), (0.007, D - 0.15, 0.012), bev=0.0025, seg=2, col=(1, 0.95, 0.9), g=1)
    # corner brackets (triangular blocks) under top
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.box('wood_oak', (sx * (ax - 0.05), sy * (ay - 0.05), zt - 0.02), (0.05, 0.05, 0.03), bev=0.003, col=(0.7, 0.6, 0.5), skip_down=False)
    # legs
    for sx in (-1, 1):
        for sy in (-1, 1):
            table_leg(f, sx * (W / 2 - 0.075), sy * (D / 2 - 0.075), col=(1, 0.96, 0.9), seed=sx * 3 + sy)
    # stretchers (H frame): two long side stretchers + central cross stretcher, round tenons pegged
    zs = 0.19
    for sy in (-1, 1):
        f.box('wood_oak', (0, sy * (D / 2 - 0.075), zs), (W - 0.2, 0.028, 0.04), bev=0.004, seg=2, col=(0.92, 0.86, 0.8), g=0, skip_down=False)
        for sx in (-1, 1):
            dowel(f, sx * (W / 2 - 0.075), sy * (D / 2 - 0.075 + 0.0), zs, axis='y', r=0.0055, L=0.062, col=(0.6, 0.46, 0.32)) if False else None
            f.cyl('wood_dark', (sx * (W / 2 - 0.075 - 0.0), sy * (D / 2 - 0.075 + 0.0), zs), 0.0055, 0.064, axis='y', seg=8, col=(0.6, 0.46, 0.32))
    f.box('wood_oak', (0, 0, zs), (0.04, D - 0.2, 0.04), bev=0.004, seg=2, col=(0.9, 0.84, 0.78), g=1, skip_down=False)
    f.cyl('wood_oak', (0, 0, zs), 0.0235, 0.058, axis='x', seg=10, col=(0.9, 0.84, 0.78)) if False else None
    collider_f(f, W, D, F + H)
    return f


# ====================================================================== chairs
def back_y(z, base=-0.175):
    t = max(0.0, (z - 0.46) / 0.47)
    return base - 0.065 * t ** 1.5 - (0.0 if z < 0.46 else 0.0)


def chair_back_post(f, x, mat='wood_oak', col=(1, 1, 1), seed=0):
    zs = [0.0, 0.2, 0.46, 0.62, 0.78, 0.94]
    pts = [Vector((x, back_y(z), z)) for z in zs]
    pts = polyline_smooth(pts, 3)
    prof = [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]
    n = len(pts)

    def sc(t):
        z = pts[min(int(t * (n - 1)), n - 1)].z
        w = 0.034 if z < 0.5 else 0.034 - 0.006 * (z - 0.5) / 0.44
        # taper toward the foot
        if z < 0.12:
            w = 0.024 + (0.034 - 0.024) * z / 0.12
        return (w, 0.03)
    f.sweep(mat, prof, pts, scale=sc, col=col, up=(1, 0, 0), g=2)
    # top finial knob
    f.sphere(mat, (x, back_y(0.94) - 0.002, 0.955), 0.017, col=col, sq=(1, 1, 1.2) if False else (1, 1, 1)) if False else None
    f.lathe(mat, (x, back_y(0.94) - 0.0015, 0.935), [(0.012, 0), (0.016, 0.006), (0.017, 0.016), (0.011, 0.026), (0.001, 0.032)], seg=10, col=col, cap=False)


def crest_rail_bm(w=0.37, h=0.1, t=0.024, style=0, seed=0):
    """carved crest rail: arched top, piercings (boolean difference), bevelled, rosette relief is added separately"""
    nx = 22
    bm = bmesh.new()
    top, bot = [], []
    for i in range(nx + 1):
        u = -1 + 2 * i / nx
        x = u * w / 2
        zt = h * (0.74 + 0.26 * (1 - u * u) ** 0.8)
        if style == 1:
            zt += 0.016 * math.cos(u * math.pi * 3) ** 2 * (1 - abs(u))
        top.append(bm.verts.new((x, -t / 2, zt)))
        bot.append(bm.verts.new((x, -t / 2, 0)))
    for i in range(nx):
        bm.faces.new([bot[i], bot[i + 1], top[i + 1], top[i]])
    # fill: single quad strip -> extrude in y
    r = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    for v in [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]:
        v.co.y += t
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # piercings
    cuts = []
    if style == 0:   # three round holes + two small
        for (cx, cz, rr_) in ((0, h * 0.5, 0.0155), (-0.095, h * 0.46, 0.0095), (0.095, h * 0.46, 0.0095)):
            cb = cyl_bm(rr_, t * 3, 14, axis='y')
            cuts.append((cb, Matrix.Translation((cx, 0, cz))))
    else:   # heart-ish: two overlapping circles + diamond
        for (cx, cz, rr_) in ((-0.012, h * 0.55, 0.0135), (0.012, h * 0.55, 0.0135)):
            cb = cyl_bm(rr_, t * 3, 14, axis='y')
            cuts.append((cb, Matrix.Translation((cx, 0, cz))))
        db = cube_bm(0.034, t * 3, 0.034)
        cuts.append((db, Matrix.Translation((0, 0, h * 0.5)) @ Matrix.Rotation(math.radians(45), 4, 'Y')))
        for sx in (-1, 1):
            cb = cyl_bm(0.0075, t * 3, 10, axis='y')
            cuts.append((cb, Matrix.Translation((sx * 0.105, 0, h * 0.5))))
    bm = boolean(bm, cuts, solver='EXACT')
    for cb, _ in cuts:
        cb.free()
    bm = modbm(bm, [('BEVEL', {'width': 0.0022, 'segments': 2, 'limit_method': 'ANGLE', 'angle_limit': math.radians(35)})])
    return bm


def rosette(f, M0, r=0.026, petals=10, h=0.004, col=(0.85, 0.78, 0.7), mat='wood_oak'):
    """carved rosette: lathe with radial petal modulation"""
    bm = bmesh.new()
    seg = petals * 3
    prof = [(0.0, 0.0), (r * 0.25, 0.0), (r * 0.5, 0.0), (r * 0.75, 0.0), (r * 1.0, 0.0)]
    ul = bm.loops.layers.uv.new('UVMap')
    rings = []
    for k, rf in enumerate((0.0, 0.2, 0.45, 0.7, 0.92, 1.0)):
        if rf == 0:
            rings.append([bm.verts.new((0, 0, h))])
            continue
        ring = []
        for i in range(seg):
            a = TAU * i / seg
            petal = 0.5 + 0.5 * math.cos(petals * a)
            rad = r * rf * (1 + 0.12 * petal * (0.4 + rf) * (1 if rf < 0.99 else 0.9))
            zz = h * (1.0 - 0.6 * rf * rf) * (0.75 + 0.25 * petal) if rf < 1 else 0.0
            ring.append(bm.verts.new((rad * math.cos(a), rad * math.sin(a), zz)))
        rings.append(ring)
    for k in range(len(rings) - 1):
        a, b = rings[k], rings[k + 1]
        for i in range(seg):
            j = (i + 1) % seg
            if len(a) == 1:
                bm.faces.new([a[0], b[j], b[i]])
            else:
                bm.faces.new([a[i], a[j], b[j], b[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    put(mat, bm, M0, col=col)
    bm.free()


def splat_bm(h=0.27, w0=0.07, t=0.014, seed=0):
    """vase-shaped pierced splat"""
    pts_r, pts_l = [], []
    ns = 16
    for i in range(ns + 1):
        s = i / ns
        z = s * h
        w = w0 * (0.55 + 0.5 * math.sin(s * math.pi * 1.0) ** 0.9) * (0.75 + 0.25 * math.cos(s * math.pi * 2.0))
        pts_r.append((w, z)); pts_l.append((-w, z))
    P = pts_r + pts_l[::-1]
    bm = bmesh.new()
    f = bm.faces.new([bm.verts.new((x, -t / 2, z)) for x, z in P])
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]:
        v.co.y += t
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    cuts = []
    for (cz, ra) in ((h * 0.32, 0.016), (h * 0.62, 0.012)):
        cb = cyl_bm(ra, t * 3, 12, axis='y')
        cuts.append((cb, Matrix.Translation((0, 0, cz))))
    db = cube_bm(0.03, t * 3, 0.03)
    cuts.append((db, Matrix.Translation((0, 0, h * 0.47)) @ Matrix.Rotation(math.radians(45), 4, 'Y')))
    bm = boolean(bm, cuts, solver='EXACT')
    for cb, _ in cuts:
        cb.free()
    return modbm(bm, [('BEVEL', {'width': 0.0016, 'segments': 1, 'limit_method': 'ANGLE', 'angle_limit': math.radians(35)})])


def woven_seat(f, w=0.33, d=0.31, z=0.43, seed=0, col=(0.85, 0.7, 0.5), pitch=0.0285):
    """over/under woven cord seat: ribbons following sine heights"""
    amp = 0.0028
    nx = int(w / pitch)
    ny = int(d / pitch)
    # dark backing
    f.box('wood_dark', (0, 0.005, z - 0.003), (w + 0.01, d + 0.01, 0.004), bev=0, col=(0.25, 0.2, 0.15), skip_down=False)
    prof = [(-0.5, 0.0), (0.5, 0.0)]
    for i in range(nx):
        x = -w / 2 + (i + 0.5) * w / nx
        pts = []
        ns = ny * 2 + 1
        for j in range(ns + 1):
            y = -d / 2 + d * j / ns
            h = amp * math.cos(math.pi * j + math.pi * (i % 2))
            sag = -0.006 * (1 - (2 * y / d) ** 2) * 0.0 - 0.008 * (1 - (2 * x / w) ** 2)
            pts.append(Vector((x, y + 0.005, z + h + sag + 0.0035)))
        wr = pitch * 0.46
        _ribbon(f, pts, wr, col, seed + i, axis_perp=(1, 0, 0))
    for j in range(ny):
        y = -d / 2 + (j + 0.5) * d / ny
        pts = []
        ns = nx * 2 + 1
        for i in range(ns + 1):
            x = -w / 2 + w * i / ns
            h = -amp * math.cos(math.pi * i + math.pi * (j % 2)) * 1.0
            sag = -0.008 * (1 - (2 * x / w) ** 2)
            pts.append(Vector((x, y + 0.005, z + h + sag + 0.0035)))
        _ribbon(f, pts, pitch * 0.46, col, seed + 100 + j, axis_perp=(0, 1, 0))


def _ribbon(f, pts, hw, col, seed, axis_perp=(1, 0, 0)):
    """flat ribbon strand with slightly rounded cross-section"""
    prof = [(0.0, -hw), (0.0026, 0.0), (0.0, hw)]
    # simple strip: ordered across width; use sweep with open profile
    c = jit(col, 0.08)
    sweep('wicker', prof, [f.p(p) for p in pts], col=c, caps=False, prof_closed=False, up=(0, 0, 1), g=0)


def seat_plank(f, z=0.445, w=0.43, d=0.40, seed=0, col=(1, 0.95, 0.9)):
    """saddle plank seat made of 3 boards with gaps, dished with noise + rounded front edge"""
    bws = [0.14, 0.15, 0.14]
    x = -sum(bws) / 2 - 0.004
    for i, bw in enumerate(bws):
        bm = plank_bm(bw - 0.003, d, 0.028, bev=0.004, seg=2, maxlen=0.085, dent=0.0004, dscale=0.2, seed=50 + seed * 3 + i)
        for v in bm.verts:
            xx = x + bw / 2 + v.co.x
            if v.co.z > 0:
                v.co.z -= 0.009 * (1 - (v.co.y / (d / 2) + 0.15) ** 2) * (1 - (xx / (w / 2)) ** 2) * 0.9
                if v.co.y > d / 2 - 0.02:
                    v.co.z -= 0.0035
        put('wood_oak', bm, f.M @ Matrix.Translation((x + bw / 2, 0.0, z)), col=jit(col, 0.05), g=1, skip_down=False)
        bm.free()
        x += bw + 0.004


def chair(pos, rot, style=0, seat='woven', pad=None, seed=0):
    f = Fr((pos[0], pos[1], F), rot)
    mat = 'wood_oak'
    col = (1, 0.95, 0.9)
    sh = 0.46
    # back posts (curved, raked)
    for sx in (-1, 1):
        chair_back_post(f, sx * 0.185, col=col)
    # front legs (turned)
    for sx in (-1, 1):
        x, y = sx * 0.185, 0.17
        f.lathe(mat, (x, y, 0.0), [(0.015, 0), (0.0195, 0.008), (0.017, 0.026), (0.0225, 0.056), (0.019, 0.12), (0.015, 0.21), (0.0195, 0.26), (0.022, 0.30), (0.0185, 0.335), (0.0235, 0.352), (0.0235, 0.363)], seg=12, col=col)
        f.box(mat, (x, y, 0.363 + 0.04), (0.045, 0.045, 0.08), bev=0.003, seg=2, col=col, skip_down=False, g=2)
        f.cyl(mat, (x, y, 0.363 + 0.0), 0.025, 0.006, seg=12, col=col)
    # seat rails
    for sy, ln in ((0.17, 0.33), (-0.175, 0.33)):
        f.box(mat, (0, sy, sh - 0.058), (ln, 0.028, 0.06), bev=0.003, seg=2, col=col, g=0, skip_down=False)
    for sx in (-1, 1):
        f.box(mat, (sx * 0.185, -0.003, sh - 0.058), (0.028, 0.32, 0.06), bev=0.003, seg=2, col=col, g=1, skip_down=False)
    # stretchers (round, tenoned)
    for z in (0.17,):
        for sx in (-1, 1):
            f.cyl(mat, (sx * 0.185, -0.003, z), 0.0105, 0.32, axis='y', seg=8, col=col)
        f.cyl(mat, (0, 0.17, z + 0.03), 0.0095, 0.35, axis='x', seg=8, col=col)
        f.cyl(mat, (0, -0.178, z + 0.03), 0.0095, 0.35, axis='x', seg=8, col=col)
    # pegs at joints
    for sx in (-1, 1):
        for (yy, zz) in ((0.17, sh - 0.058), (-0.178, sh - 0.058)):
            f.cyl('wood_dark', (sx * 0.2, yy, zz), 0.004, 0.003, axis='x', seg=6, col=(0.5, 0.38, 0.28))
    # back: crest rail, mid rail, slats / splat
    ytop = back_y(0.89)
    cr = crest_rail_bm(w=0.336, h=0.10, t=0.022, style=style % 2)
    zc = 0.82
    ang = -math.degrees(math.atan2(back_y(0.95) - back_y(0.82), 0.13)) * 0.0
    Mc = f.M @ Matrix.Translation((0, back_y(zc + 0.04) + 0.0, zc)) @ Matrix.Rotation(math.radians(-8), 4, 'X')
    put(mat, cr, Mc, col=col, g=0)
    cr.free()
    rosette(f, Mc @ Matrix.Translation((0, 0.0105, 0.082)) @ Matrix.Rotation(math.radians(-90), 4, 'X'), r=0.022, petals=8, h=0.0035, col=(0.85, 0.78, 0.7)) if style % 2 == 0 else None
    for sx in (-1, 1):   # small ball finials atop crest ends
        pass
    zm = 0.58
    mr = Matrix.Translation((0, back_y(zm), zm)) @ Matrix.Rotation(math.radians(-6.5), 4, 'X')
    f.box(mat, (0, back_y(zm), zm), (0.336, 0.022, 0.05), r=(-6.5, 0, 0), bev=0.004, seg=2, col=col, g=0, skip_down=False)
    if style % 2 == 0:
        for i in range(3):
            x = (i - 1) * 0.1
            # slats: tapered and slightly curved
            f.box(mat, (x, back_y(0.7) - 0.0, 0.7), (0.05, 0.014, 0.25), r=(-7, 0, 0), bev=0.003, seg=2, col=col, g=2, skip_down=False, taper=(0.82, 1.0))
    else:
        sp = splat_bm()
        put(mat, sp, f.M @ Matrix.Translation((0, back_y(0.6), 0.6 - 0.0)) @ Matrix.Rotation(math.radians(-7), 4, 'X'), col=col, g=2)
        sp.free()
        for sx in (-1, 1):
            f.cyl(mat, (sx * 0.115, back_y(0.7), 0.7), 0.0105, 0.23, seg=8, col=col, r=(-7, 0, 0))
    # seat
    if seat == 'woven':
        # frame inside rails + weave
        woven_seat(f, w=0.335, d=0.305, z=sh - 0.036, seed=seed, col=(0.78, 0.62, 0.4))
        # seat frame top rim (slightly proud boards)
        f.box(mat, (0, 0.17, sh - 0.028), (0.37, 0.034, 0.016), bev=0.003, col=col, skip_down=False, g=0)
        f.box(mat, (0, -0.175, sh - 0.028), (0.37, 0.034, 0.016), bev=0.003, col=col, skip_down=False, g=0)
        for sx in (-1, 1):
            f.box(mat, (sx * 0.185, 0, sh - 0.028), (0.034, 0.37, 0.016), bev=0.003, col=col, skip_down=False, g=1)
    else:
        seat_plank(f, z=sh - 0.014, seed=seed)
    if pad:
        # quilted seat pad (subsurf'd cube, buttons, tie strings)
        pb = cube_bm(0.37, 0.36, 0.035, off=(0, 0, 0.0175), cuts=2)
        pb = modbm(pb, [('SUBSURF', {'levels': 1, 'render_levels': 1})])
        for v in pb.verts:
            v.co.z += 0.003 * math.sin(v.co.x * 90) * math.sin(v.co.y * 90) * (1 if v.co.z > 0.02 else 0)
        put('linen_vc', pb, f.M @ Matrix.Translation((0, 0.005, sh - 0.005)), col=C(pad), cfn=fab(C(pad), 0.07, 14, seed))
        pb.free()
        for sx in (-1, 1):
            for sy in (-1, 1):
                f.sphere('wood_dark', (sx * 0.09, 0.005 + sy * 0.09, sh + 0.031), 0.004, seg=6, rings=3, col=(0.35, 0.2, 0.12))
        # ties
        for sx in (-1, 1):
            f.tube('linen_vc', [Vector((sx * 0.165, -0.15, sh + 0.025)), Vector((sx * 0.19, -0.19, sh + 0.0)), Vector((sx * 0.2, -0.2, sh - 0.05))], 0.0035, seg=5, col=C(pad))
    collider_f(f, 0.44, 0.44, F + 0.47)
    return f


# ====================================================================== runner (cloth simulation)
def runner_cloth(f, L=1.8, Wd=0.34, nx=44, ny=9, seed=1):
    ztop = TBL_H + 0.075
    zt_ = F + TBL_H
    bm = cloth_grid(-L / 2, L / 2, -Wd / 2, Wd / 2, nx, ny, z=zt_ + 0.05, uvscale=1.0)
    for v in bm.verts:   # slight random wrinkle seed so it drapes naturally
        v.co.z += 0.004 * mnoise.noise(Vector((v.co.x * 7, v.co.y * 9, seed)))
        v.co.x += 0.0
    # table top collider (box incl. slightly rounded edge) in world coords
    tb = cube_bm(TBL_W, TBL_D, 0.04, off=(0, 0, 0))
    bev_bm(tb, 0.004, 2)
    Mt = f.M @ Matrix.Translation((0, 0, TBL_H - 0.02))
    # move cloth into world
    for v in bm.verts:
        v.co = f.M @ v.co
    cl = cloth_sim(bm, colliders=[(tb, Mt)], pin=None, frames=45, mass=0.1, tension=40, compression=40, shear=20, bending=1.0, quality=8,
                   friction=18.0, dist=0.0035, coll_dist=0.003, subsurf_levels=0)
    tb.free()
    return cl


def runner(f, seed=1):
    cl = runner_cloth(f, seed=seed)
    inv = f.M.inverted()
    base = (0.93, 0.9, 0.82)
    red = (0.45, 0.1, 0.07)
    blue = (0.2, 0.3, 0.5)

    def cf(p):
        l = inv @ p
        e = abs(l.x)
        c = base
        k = 1 + 0.05 * fbm(p.x, p.y, p.z, 12, 1, 2)
        for (a, b, cc) in ((0.78, 0.8, red), (0.82, 0.835, red), (0.84, 0.85, blue), (0.86, 0.9, base), (0.885, 0.9, red)):
            if a <= e < b:
                c = cc
        if abs(l.y) > 0.155 and abs(l.y) < 0.165:
            c = blue
        return (c[0] * k, c[1] * k, c[2] * k)
    put('linen_vc', cl, Matrix.Identity(4), cfn=cf, g=0)
    cl.free()


# ====================================================================== table setting
def board(f, c, size=(0.36, 0.2), rot=0, handle=True, round_=False, mat='wood_oak', seed=0, z=0.0):
    """cutting/bread board: rounded rectangle slab, chamfered, with hanging hole; z = table surface (local)"""
    sx, sy = size
    bm = cube_bm(sx, sy, 0.022, off=(0, 0, 0.011))
    # round the corners via bevel on vertical edges
    bmesh.ops.bevel(bm, geom=[e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co).z) > 0.01], offset=0.03 if not round_ else min(sx, sy) * 0.45, segments=4, affect='EDGES')
    bev_bm(bm, 0.0025, 2)
    if handle:
        cb = cyl_bm(0.008, 0.06, 12)
        bm = boolean(bm, [(cb, Matrix.Translation((sx / 2 - 0.028, 0, 0.011)))])
        cb.free()
    for axis in (0, 1):
        es = [e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co)[axis]) > 0.09 and abs((e.verts[0].co - e.verts[1].co)[axis]) > 0.9 * (e.verts[0].co - e.verts[1].co).length]
        if es:
            bmesh.ops.subdivide_edges(bm, edges=es, cuts=2, use_grid_fill=True)
    bm = disp(bm, 0.0008, 0.05, 2)
    put(mat, bm, f.M @ Matrix.Translation((c[0], c[1], z)) @ rotm((0, 0, rot)), col=(0.95, 0.9, 0.82), cfn=None, g=0)
    bm.free()


def napkin(f, c, rot=0, z=0.0, col=(0.85, 0.82, 0.74), stripe=(0.3, 0.4, 0.6), size=(0.15, 0.1), layers=3):
    pb = cube_bm(size[0], size[1], 0.003 * layers + 0.004, off=(0, 0, (0.003 * layers + 0.004) / 2), cuts=2)
    pb = modbm(pb, [('SUBSURF', {'levels': 1, 'render_levels': 1})])
    for v in pb.verts:
        v.co.z += 0.0015 * math.sin(v.co.x * 70) * math.cos(v.co.y * 60 + 1) * (1 if v.co.z > 0.004 else 0)
    inv_rot = rotm((0, 0, rot)).inverted()

    def cf(p):
        l = f.M.inverted() @ p
        l = Vector(l) - Vector((c[0], c[1], 0))
        l = inv_rot @ l
        k = 1 + 0.04 * fbm(p.x * 20, p.y * 20, 0, 1, 3, 2)
        cc = col
        if abs(abs(l.x) - size[0] * 0.38) < 0.003:
            cc = stripe
        return (cc[0] * k, cc[1] * k, cc[2] * k)
    put('linen_vc', pb, f.M @ Matrix.Translation((c[0], c[1], z)) @ rotm((0, 0, rot)), cfn=cf, g=0)
    pb.free()


def salt_pepper(f, c, rot=0, z=0.0, kind='salt'):
    Mx = f.M @ Matrix.Translation((c[0], c[1], z)) @ rotm((0, 0, rot))
    g = G('white') if kind == 'salt' else G('brown')
    prof = [(0.001, 0), (0.015, 0), (0.0175, 0.004), (0.017, 0.02), (0.0125, 0.042), (0.0105, 0.05), (0.0115, 0.053), (0.0105, 0.056)]
    lathe('ceramic', None, prof, 14, M=Mx, col=g, cap=False)
    lathe('brass', None, [(0.0108, 0.052), (0.0112, 0.056), (0.0105, 0.062), (0.007, 0.0665), (0.001, 0.067)], 12, M=Mx, cap=False)
    for k in range(4):
        a = TAU * k / 4
        cyl('ink', None, 0.0008, 0.001, seg=4, M=Mx @ Matrix.Translation((0.0035 * math.cos(a), 0.0035 * math.sin(a), 0.0662)))


def butter_dish(f, c, rot=0, z=0.0):
    Mx = f.M @ Matrix.Translation((c[0], c[1], z)) @ rotm((0, 0, rot))
    lathe('ceramic', None, [(0.001, 0.003), (0.052, 0.003), (0.054, 0.0), (0.06, 0.0), (0.075, 0.006), (0.082, 0.011), (0.075, 0.0125), (0.062, 0.0085), (0.001, 0.0075)], 22, M=Mx, col=G('cream'), cap=False)
    butter_block(Mx @ Vector((0, 0, 0.0085)), rot=rot + 20, L=0.1, W=0.052, H=0.034)
    # small butter knife leaning
    knife(Mx @ Vector((0.03, -0.08, 0.0)), rot=rot + 70, L=0.15, hand=0.07, rivets=2)


def table_setting(f):
    zt = F + TBL_H
    zc = zt + 0.0035      # runner surface

    def W(x, y, z):
        p = f.p((x, y, 0)); p.z = z
        return p
    # --- places: (x, y, direction-to-diner)
    places = [((-0.34, 0.215), (0, 1)), ((0.34, 0.215), (0, 1)), ((-0.50, -0.01), (-1, 0)), ((0.50, -0.01), (1, 0))]
    rr = random.Random(5)
    for i, ((px, py), dv) in enumerate(places):
        onrun = abs(py) < 0.17
        z0 = zc if onrun else zt
        fx, fy = -dv[0], -dv[1]
        rotc = f.rot + math.degrees(math.atan2(-fx, fy))
        base = W(px, py, z0)
        plate(base, r=0.118, glaze='cream', rim=['blue', 'cobalt', 'blue', 'cobalt'][i], rot=(0, 0, f.rot + rr.uniform(0, 360)), seg=24, chip=(40 if i == 1 else None))
        if i in (0, 3):    # soup bowl on the plate
            bowl(base + Vector((0, 0, 0.0185)), r=0.068, h=0.045, glaze='cream', rim='blue', rot=(0, 0, rr.uniform(0, 360)), seg=26,
                 contents=('soup', (0.62, 0.4, 0.16)) if i == 0 else None)
        wdv = f.M.to_3x3() @ Vector((dv[0], dv[1], 0))
        wf = -wdv
        wr = Vector((wf.y, -wf.x, 0))
        cz0 = z0
        fork(base + wr * (-0.16) - wdv * 0.09, rot=rotc + 180, L=0.18)
        knife(base + wr * 0.145 + wdv * 0.10, rot=rotc, L=0.2)
        spoon(base + wr * 0.172 - wdv * 0.085, rot=rotc + 180 + rr.uniform(-4, 4), L=0.17)
        gp = base + wr * 0.115 + wf * 0.15
        goblet(gp, r=0.031, h=0.105, kind='tumbler' if i % 2 == 0 else 'wine', fill='water' if i % 2 == 0 else (0.35, 0.04, 0.08), fill_h=0.6 if i % 2 == 0 else 0.4)
        # napkin to the left of the fork (tucked) on two places
        if i in (0, 2):
            nc = base + wr * (-0.26) + wdv * 0.0
            lc = f.M.inverted() @ nc
            napkin(f, (lc.x, lc.y), rot=(rotc - f.rot), z=zt - F, stripe=(0.3, 0.4, 0.6))
    # --- centre of table
    cp = W(0.0, 0.015, zc)
    jug(cp, r=0.062, h=0.19, glaze='blue', rot=(0, 0, f.rot + 10), seg=26)
    flower_bunch(cp + Vector((0, 0, 0.175)), 0.05, n=17, seed=4, spread=0.085, up=0.08)
    # bread board with a loaf, slices and knife
    board(f, (0.3, -0.3), (0.38, 0.2), rot=8, z=TBL_H, seed=1)
    bpz = zt + 0.022
    loaf(W(0.26, -0.3, bpz), rot=f.rot + 14, L=0.2, W=0.1, H=0.09, seed=2, score=3)
    for k in range(3):
        bread_slice(W(0.405 - 0.028 * k, -0.34 + 0.015 * k, bpz), rot=(0, 0, f.rot + 12 - 16 * k), seed=k)
    knife(W(0.17, -0.2, bpz), rot=f.rot + 100, L=0.24, hand=0.11)
    crumbs(f.M @ Matrix.Translation((0.3, -0.3, TBL_H + 0.0228)) @ Matrix.Rotation(math.radians(8), 4, 'Z'), 0.17, 0.085, n=46, seed=3)
    crumbs(f.M @ Matrix.Translation((0.36, -0.2, TBL_H + 0.0035 + 0.0012)), 0.06, 0.05, n=10, seed=5)
    # cheese on its own round board
    board(f, (-0.3, -0.3), (0.26, 0.2), rot=-12, round_=True, z=TBL_H, mat='wood_dark', seed=2)
    cheese_wedge(W(-0.3, -0.31, bpz), rot=f.rot - 25, seed=3)
    cheese_wedge(W(-0.37, -0.25, bpz), rot=f.rot + 150, R=0.05, ang=55, H=0.05, seed=5, holes=3)
    knife(W(-0.2, -0.2, bpz), rot=f.rot + 60, L=0.21, hand=0.1)
    butter_dish(f, (-0.12, -0.115), rot=15, z=zc - F)
    salt_pepper(f, (0.12, -0.08), z=zc - F, kind='salt')
    salt_pepper(f, (0.16, -0.095), z=zc - F, kind='pepper', rot=30)
    # candlesticks near the ends
    for sx in (-1, 1):
        nm = 'lamp_kit_1' if sx < 0 else 'lamp_kit_2'
        candlestick(W(sx * 0.30, 0.04, zc), h=0.15, cl=0.14 if sx < 0 else 0.1, name=nm, inten=0.55, dist=3.5)
    # apples in a small bowl
    bp2 = W(0.58, -0.3, zt)
    bowl(bp2, r=0.075, h=0.055, glaze='ochre', rot=(0, 0, 20), seg=22)
    for k in range(4):
        a = TAU * k / 4
        place('food_vc', apple_bm(40 + k), bp2 + Vector((0.025 * math.cos(a), 0.025 * math.sin(a), 0.026 + (0.02 if k == 3 else 0.0))), rot=(0, 0, k * 70))


def blanket_on_chair(pos, rot, seed=3):
    """knitted wool blanket thrown over a chair back: cloth simulation with simplified chair colliders"""
    f = Fr((pos[0], pos[1], F), rot)
    by = back_y(0.9)
    cl = cloth_grid(-0.24, 0.24, by - 0.3, by + 0.46, 12, 18, z=1.1, M=f.M)
    for v in cl.verts:
        l_ = f.M.inverted() @ v.co
        v.co += f.M.to_3x3() @ Vector((0, 0, 0.004 * mnoise.noise(Vector((l_.x * 9, l_.y * 9, seed))) - 0.05 * (1 - (l_.y - by) ** 2 / 0.2) * 0.0))
    cols = []

    def box_c(sx, sy, sz, x, y, z, rx=0.0):
        b = cube_bm(sx, sy, sz)
        return (b, f.M @ Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rx), 4, 'X'))
    cols = [box_c(0.43, 0.41, 0.045, 0, 0.0, 0.44), box_c(0.38, 0.035, 0.14, 0, back_y(0.88), 0.88, -8), box_c(0.35, 0.03, 0.34, 0, back_y(0.68), 0.68, -7),
            box_c(0.036, 0.04, 0.95, -0.185, back_y(0.5), 0.475), box_c(0.036, 0.04, 0.95, 0.185, back_y(0.5), 0.475)]
    out = cloth_sim(cl, colliders=cols, frames=80, mass=0.25, tension=12, compression=12, shear=4, bending=0.25, quality=9, friction=5, dist=0.006, coll_dist=0.005)
    for b, _ in cols:
        b.free()
    inv = f.M.inverted()

    def cf(p):
        l = inv @ p
        k = 1 + 0.06 * fbm(p.x * 20, p.y * 20, p.z * 20, 1, seed, 2)
        base = (0.72, 0.62, 0.48)
        bands = int((l.y + 3) * 9) % 6
        c = (0.55, 0.2, 0.12) if bands in (0, 1) else ((0.26, 0.3, 0.38) if bands == 3 else base)
        return (c[0] * k, c[1] * k, c[2] * k)
    put('wool_vc', out, Matrix.Identity(4), cfn=cf, g=0)
    out.free()


def hanging_lantern():
    ctr = Vector((TBL_POS[0], TBL_POS[1], 0))
    nm = lantern((ctr.x, ctr.y, 2.2), h=0.3, w=0.16, chain_to=3.14, name='lamp_kit_3', inten=1.7, dist=8.0)
    # ceiling hook plate
    cyl('iron_black', (ctr.x, ctr.y, 3.14), 0.035, 0.012, seg=10)
    return nm


def build():
    dining_table(TBL_POS, 0)
    f = Fr((TBL_POS[0], TBL_POS[1], F), 0)
    chair((-3.35, -1.85), 180, style=0, seat='woven', pad=None, seed=1)
    chair((-2.65, -1.85), 175, style=0, seat='woven', pad='#b5562f', seed=2)
    chair((-4.0, -2.6), -90, style=1, seat='plank', pad='#c9a14a', seed=3)
    chair((-2.0, -2.6), 88, style=1, seat='plank', pad=None, seed=4)
    runner(f, seed=1)
    table_setting(f)
    blanket_on_chair((-2.0, -2.6), 88)
    hanging_lantern()
    interact('dining_table', (TBL_POS[0], TBL_POS[1], F + 0.95), '들꽃이 놓인 식탁')
