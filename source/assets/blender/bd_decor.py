"""Room-wide decor: cloth-simulated curtains (curtain_1..6), framed pictures, sconces, plants, dried flowers, rugs, peg-hung clothes."""
from bd_lib import *
from bd_hw import *
from bd_cloth import *
import bd_garment as G
import bd_items as I


# ------------------------------------------------------------------------------------------------ curtains
def _arc_amp(span_period, cloth_period):
    """amplitude A of y = A sin(2 pi x / p) so that arc length per period == cloth_period"""
    p = span_period
    best, bd = 0.0, 1e9
    xs = np.linspace(0, p, 200)
    for A in np.linspace(0, p * 0.9, 400):
        y = A * np.sin(TAU * xs / p)
        L = np.sum(np.hypot(np.diff(xs), np.diff(y)))
        if abs(L - cloth_period) < bd:
            bd, best = abs(L - cloth_period), A
    return best


def curtain(n, wall_pt, rot, hem_z, mat_name='linen_curtain', col=(0.9, 0.85, 0.72), rod_z=2.88, rod_style='wood', span=0.56, tie_z=None, win_half=0.5):
    """n: 1..6. wall_pt = (x,y) of the window centre on the wall plane; rot = Fr rotation so that local +y points into the room.
    Builds: static rod+brackets+finials (into static accumulators) and part curtain_<n> (panels, rings, tie-back cords)."""
    f = Fr((wall_pt[0], wall_pt[1], 0.0), rot, 0.0)
    ry = 0.115
    mat_rod = M['wood_dark'] if rod_style == 'wood' else M['iron']
    col_rod = (1.0, 0.93, 0.85)
    L = 1.62
    f.cyl(mat_rod, (0, ry, rod_z), 0.0115, L, axis='x', seg=14, col=col_rod)
    for sx in (-1, 1):
        # finial: turned acorn
        f.lathe(M['brass'] if rod_style == 'wood' else M['iron'], (sx * (L / 2 + 0.005), ry, rod_z),
                profile_pts([(0.0005, 0.0), (0.017, 0.0), (0.02, 0.01), (0.014, 0.022), (0.022, 0.04), (0.026, 0.055), (0.018, 0.075), (0.0005, 0.088)], 3), r=(0, 90 * sx, 0), seg=14, cap=False)
        # wall brackets (arm + backplate)
        bx = sx * 0.66
        f.box(M['iron'], (bx, ry / 2, rod_z - 0.012), (0.014, ry, 0.014), bev=0.002, col=(0.8, 0.8, 0.8))
        f.cyl(M['iron'], (bx, 0.006, rod_z - 0.012), 0.03, 0.012, axis='y', seg=14, bev=0.003)
        f.torus(M['iron'], (bx, ry, rod_z), 0.0145, 0.0035, plane='yz', seg=16, rseg=6, a0=0, a1=360)
    # ---- the animated part
    saved = part_begin()
    cloth_w = span * 1.7
    nx, ny = 24, 16
    top_z = rod_z - 0.034
    drop = top_z - hem_z
    period_c = cloth_w / 6.0
    period_s = span / 6.0
    A = _arc_amp(period_s, period_c)
    tzf = tie_z if tie_z is not None else 0.56
    jt = int(round(tzf * ny))
    rng = random.Random(n * 17)
    for side in (-1, 1):
        name = 'cur%d_%s' % (n, 'L' if side < 0 else 'R')
        # panel centre on the rod (local x): inner edge near the window centre, panel spans [0.07,0.07+span] from centre
        xc = side * (0.085 + span / 2)
        verts, uv = [], []
        for j in range(ny + 1):
            t = j / ny
            for i in range(nx + 1):
                x = xc + (i / nx - 0.5) * span * (1.0 + 0.12 * t)
                ph = (i / nx) * 6.0 * TAU + side * 0.8
                amp = A * (1.0 + 0.2 * math.sin(t * 3.0 + n + i * 0.05))
                y = ry + amp * math.sin(ph) * (0.75 + 0.25 * t)
                verts.append((x, y, top_z - drop * t))
                uv.append((i / nx * cloth_w, t * drop))
        verts = np.array(verts, np.float32)
        faces = []
        for j in range(ny):
            for i in range(nx):
                a = j * (nx + 1) + i
                faces.append((a, a + 1, a + nx + 2, a + nx + 1))
        pins = list(range(nx + 1))
        # tie-back band (2 rows) pulled toward the outer side
        target = verts.copy()
        bw = 0.15
        tcx = side * (0.085 + span * 0.78)
        for jj in (jt, jt + 1):
            for i in range(nx + 1):
                k = jj * (nx + 1) + i
                target[k] = (tcx + (i / nx - 0.5) * bw, ry - 0.005 + 0.012 * math.sin(i * 1.7 + n), verts[k][2])
                pins.append(k)
        res = simulate(name, verts, faces, pins=pins, frames=95, colliders=[box_collider((0, -0.15, 1.4), (6, 0.3, 4.0))], preset='curtain', collision_dist=0.008,
                       shape_target=target, shape_frames=(1, 36), damping_scale=1.8)
        bm = cloth_to_bm(res, faces, np.array(uv, np.float32))
        put(M[mat_name], bm, f.M, cfn=fab(col, 0.1, 6, n + (3 if side > 0 else 0)), skip_down=False)
        bm.free()
        # rings at the crest pins
        for i in range(0, nx + 1, 4):
            p = Vector(verts[i])
            x_ = p.x
            f.torus(M['brass'] if rod_style == 'wood' else M['iron'], (x_, ry, rod_z), 0.0205, 0.0024, plane='yz', seg=14, rseg=5)
        # tie-back cord: loop around the gathered band + tassel + wall hook
        row = res[jt * (nx + 1):(jt + 1) * (nx + 1)]
        cxm = float(row[:, 0].mean()); cym = float(row[:, 1].mean()); czm = float(row[:, 2].mean() - 0.01)
        rx = float(row[:, 0].max() - row[:, 0].min()) / 2 + 0.014
        ryy = max(float(row[:, 1].max() - row[:, 1].min()) / 2 + 0.014, 0.03)
        pts = [Vector((cxm + rx * math.cos(a), cym + ryy * math.sin(a), czm)) for a in np.linspace(0, TAU, 18, endpoint=False)]
        f.tube(M['linen'], pts, 0.0055, seg=6, col=(0.55, 0.42, 0.28), closed=True)
        hx, hy = side * (0.085 + span * 0.78) + side * 0.12, 0.012
        hook_pts = [Vector((cxm + side * rx, cym, czm)), Vector((hx, hy + 0.05, czm + 0.01)), Vector((hx, hy + 0.01, czm + 0.012))]
        f.tube(M['linen'], [Vector(q) for q in catmull([(p.x, p.y, p.z) for p in hook_pts], 2)], 0.0035, seg=5, col=(0.55, 0.42, 0.28), caps=False)
        f.lathe(M['brass'], (hx, 0.0, czm + 0.012), profile_pts([(0.0005, 0.0), (0.02, 0.0), (0.022, 0.006), (0.012, 0.012), (0.008, 0.03), (0.012, 0.045), (0.016, 0.05)], 2), r=(-90, 0, 0), seg=12, cap=False)
        # tassel at the cord end
        tp = Vector((cxm + side * rx, cym + 0.0, czm))
        f.sphere(M['linen'], tp + Vector((side * 0.0, 0, -0.05)), 0.009, seg=8, col=(0.55, 0.42, 0.28))
        f.lathe(M['linen'], tp + Vector((0, 0, -0.058)), [(0.0035, 0.0), (0.0085, -0.014), (0.011, -0.04), (0.0, -0.05)], seg=8, cap=False, col=(0.6, 0.46, 0.3))
        f.tube(M['linen'], [tp, tp + Vector((0, 0, -0.045))], 0.0022, seg=4, col=(0.55, 0.42, 0.28))
    ob = part_end(saved, 'curtain_%d' % n, f.p((0, ry, rod_z)))
    return ob


# ------------------------------------------------------------------------------------------------ pictures
def picture(pos, rot, w, h, idx, style='gilt', mat_w=0.05, name=None):
    """framed picture on a wall. pos = point on the wall (centre), rot = Fr rotation so that local +y points into the room."""
    f = Fr(pos, rot, pos[2])
    fm = {'gilt': (M['brass'], (1.0, 0.82, 0.5)), 'dark': (M['wood_dark'], (0.85, 0.75, 0.68)), 'oak': (M['wood_oak'], (1.0, 0.9, 0.78)), 'white': (M['paint'], (0.95, 0.92, 0.85))}[style]
    mat, col = fm
    fw = 0.04
    d = 0.026
    # back
    f.box(M['wood_pine'], (0, 0.004, 0), (w, 0.008, h), bev=0.001, col=(0.6, 0.5, 0.4), g=0)
    # mat board + picture
    pw, ph = w - 2 * fw, h - 2 * fw
    f.box(M['paper'], (0, 0.012, 0), (pw, 0.004, ph), bev=0.0005, col=(0.95, 0.92, 0.84), g=0, skip_down=False)
    iw, ih = pw - 2 * mat_w, ph - 2 * mat_w
    # painting quad with UV 0..1
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    vv = [bm.verts.new((-iw / 2, 0.0, -ih / 2)), bm.verts.new((iw / 2, 0.0, -ih / 2)), bm.verts.new((iw / 2, 0.0, ih / 2)), bm.verts.new((-iw / 2, 0.0, ih / 2))]
    fc = bm.faces.new(vv)
    for l, uv in zip(fc.loops, [(1, 0), (0, 0), (0, 1), (1, 1)]):
        l[ul].uv = uv
    bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    f.put(M['bd_painting_%d' % idx], bm, c=(0, 0.0145, 0), uvs=1.0, skip_down=False)
    bm.free()
    # bevel of the mat opening
    for (cx, cz, sx_, sz_) in ((0, ih / 2 + 0.002, iw + 0.004, 0.003), (0, -ih / 2 - 0.002, iw + 0.004, 0.003), (-iw / 2 - 0.002, 0, 0.003, ih + 0.004), (iw / 2 + 0.002, 0, 0.003, ih + 0.004)):
        f.box(M['paper'], (cx, 0.0155, cz), (sx_, 0.003, sz_), bev=0.0006, col=(1.0, 0.98, 0.92), skip_down=False)
    # glass
    f.box(M['glass'], (0, 0.021, 0), (pw, 0.0012, ph), bev=0, skip_down=False)
    # moulded frame: outer fillet, ogee body, inner lip (4 bars each)
    for (cx, cz, sx_, sz_, g_) in ((0, h / 2 - fw / 2, w, fw, 0), (0, -h / 2 + fw / 2, w, fw, 0), (-w / 2 + fw / 2, 0, fw, h - 2 * fw, 2), (w / 2 - fw / 2, 0, fw, h - 2 * fw, 2)):
        f.box(mat, (cx, d / 2, cz), (sx_, d, sz_), bev=0.006, seg=1, col=col, g=g_)
        # raised inner bead
        ix = cx * 0.0 + (0 if sx_ > sz_ else (-1 if cx < 0 else 1) * (fw * 0.0))
    for (cx, cz, sx_, sz_) in ((0, ph / 2 + 0.003, pw + 0.006, 0.008), (0, -ph / 2 - 0.003, pw + 0.006, 0.008), (-pw / 2 - 0.003, 0, 0.008, ph), (pw / 2 + 0.003, 0, 0.008, ph)):
        f.box(mat, (cx, 0.0235, cz), (sx_, 0.007, sz_), bev=0.002, col=tuple(c * 1.1 for c in col), skip_down=False)
    # hanging wire + nail
    f.tube(M['iron'], [Vector((-w * 0.35, 0.006, h / 2 - 0.03)), Vector((0, 0.013, h / 2 + 0.06)), Vector((w * 0.35, 0.006, h / 2 - 0.03))], 0.0009, seg=4)
    f.cyl(M['iron'], (0, 0.008, h / 2 + 0.06), 0.003, 0.016, axis='y', seg=6)
    return f


# ------------------------------------------------------------------------------------------------ sconce
def sconce(pos, rot, name=None, inten=0.8, dist=5.0):
    f = Fr(pos, rot, pos[2])
    mat = M['brass']
    col = (1.0, 0.92, 0.72)
    # back plate (shield) + rosette
    pl = [(math.cos(a) * 0.045, math.sin(a) * 0.08) for a in np.linspace(0, TAU, 24, endpoint=False)]
    f.prism(mat, pl, 0.006, c=(0, 0.003, 0), plane='xz', bev=0.002, col=col)
    f.lathe(mat, (0, 0.006, 0), profile_pts([(0.0005, 0.012), (0.018, 0.01), (0.026, 0.004), (0.03, 0.0)], 2), r=(-90, 0, 0), seg=18, cap=False, col=col)
    # S-curved arm
    arm = [Vector(p) for p in catmull([(0, 0.014, 0.0), (0, 0.05, -0.012), (0, 0.1, 0.012), (0, 0.15, 0.0), (0, 0.17, -0.02)], 5)]
    f.tube(mat, arm, [0.007 - 0.002 * i / 20 for i in range(len(arm))], seg=10, col=col)
    # scroll curl under the arm
    sp = [Vector((0.0, 0.015 + 0.075 * (1 - math.cos(a)) * 0 + 0.07 * math.sin(a) * 0.0 + 0.05 * (a / 4.5) * 0 + 0.03 * math.sin(a * 0.6), -0.03 - 0.03 * a / 4.5 + 0.0)) for a in np.linspace(0, 4.5, 12)]
    f.tube(mat, [Vector((0, 0.02 + 0.045 * t, -0.07 * math.sin(t * 2.7) - 0.0)) for t in np.linspace(0, 1, 10)], 0.0035, seg=6, col=col)
    # drip pan + cup + candle
    cp = (0, 0.17, -0.02)
    f.lathe(mat, cp, profile_pts([(0.0005, 0.0), (0.03, 0.0), (0.04, 0.006), (0.036, 0.01), (0.014, 0.006), (0.012, 0.018), (0.016, 0.03), (0.011, 0.034)], 3), seg=20, cap=False, col=col)
    cw = f.p((0, 0.17, -0.02 + 0.034))
    I.candle(cw, 0.11, 0.0105, True, inten, dist, name=name, sc=1.0)
    # glass chimney (hurricane)
    lathe(M['glass'], cw, profile_pts([(0.025, 0.0), (0.03, 0.02), (0.027, 0.07), (0.02, 0.12), (0.022, 0.165), (0.026, 0.18)], 3), seg=20, cap=False)
    return f


# ------------------------------------------------------------------------------------------------ plants
def terracotta_pot(pos, r=0.07, h=0.12, col=(0.78, 0.45, 0.3), saucer=True, soil=True):
    p = Vector(pos)
    prof = profile_pts([(0.0005, 0.0), (r * 0.72, 0.0), (r * 0.78, 0.006), (r * 0.9, h * 0.8), (r * 0.94, h * 0.84), (r * 1.06, h * 0.88), (r * 1.07, h), (r * 0.98, h), (r * 0.96, h * 0.9), (r * 0.85, h * 0.8), (r * 0.7, 0.012), (0.0005, 0.012)], 2)
    lathe(M['ceramic'], p + Vector((0, 0, 0.012 if saucer else 0)), prof, seg=20, cap=False, col=col, noise=0.0006)
    if saucer:
        lathe(M['ceramic'], p, profile_pts([(0.0005, 0.0), (r * 0.78, 0.0), (r * 1.0, 0.004), (r * 1.2, 0.014), (r * 1.18, 0.016), (r * 0.9, 0.008), (0.0005, 0.008)], 2), seg=24, cap=False, col=col)
    if soil:
        lathe(M['soil'], p + Vector((0, 0, 0.012 + h * 0.84)), [(0.0005, 0.0), (r * 0.92, 0.0)], seg=16, cap=False, col=(0.8, 0.7, 0.62), noise=0.002) if False else None
        cyl(M['soil'], p + Vector((0, 0, 0.012 + h * 0.82)), r * 0.92, 0.01, seg=16, col=(1, 1, 1))
    return p + Vector((0, 0, 0.012 + h * 0.84))


def fern(pos, r=0.12, n=15, seed=1, h=0.55):
    rg = random.Random(seed)
    p0 = Vector(pos)
    for i in range(n):
        a = i * 2.4 + rg.uniform(-0.2, 0.2)
        L = rg.uniform(0.38, 0.62) * h / 0.55
        lift = rg.uniform(0.15, 0.7)
        d = Vector((math.cos(a), math.sin(a), 0))
        pts = []
        for t in np.linspace(0, 1, 14):
            out = L * 0.75 * (t ** 0.9) * math.cos(lift * 0.5)
            z = L * 0.5 * (math.sin(t * math.pi * 0.55 * (1.0 + lift * 0.4))) * (1.0 - 0.5 * t * (1 - lift)) - L * 0.35 * t * t
            pts.append(p0 + d * out + Vector((0, 0, z * 1.1)))
        tube(M['leaf'], pts, [0.0025 * (1 - 0.7 * t) + 0.0006 for t in np.linspace(0, 1, 14)], seg=4, col=(0.35, 0.5, 0.22), caps=False)
        # leaflet pairs in the frond plane
        side = Vector((-d.y, d.x, 0))
        for k in range(3, 14, 2):
            t = k / 13
            c = pts[k]
            tang = (pts[min(k + 1, 13)] - pts[k - 1]).normalized()
            ln = 0.06 * math.sin(min(t * 1.2, 1) * math.pi * 0.9) ** 0.8 * (L / 0.5) + 0.01
            wd = ln * 0.16
            for sgn in (-1, 1):
                dirv = (tang * 0.55 + side * sgn * 0.85 - Vector((0, 0, 0.25))).normalized()
                base = c
                tip = base + dirv * ln
                mid1 = base + dirv * ln * 0.35 + tang.cross(dirv).normalized() * wd
                mid2 = base + dirv * ln * 0.35 - tang.cross(dirv).normalized() * wd
                bm = bmesh.new()
                ul = bm.loops.layers.uv.new('UVMap')
                vs = [bm.verts.new(q) for q in (base, mid1, tip, mid2)]
                fc = bm.faces.new(vs)
                fc.smooth = True
                for l, uv in zip(fc.loops, [(0.5, 0), (1, 0.35), (0.5, 1), (0, 0.35)]):
                    l[ul].uv = uv
                put(M['leaf'], bm, Matrix.Identity(4), col=jit((0.3 + 0.12 * t, 0.5 + 0.1 * t, 0.2 + 0.06 * t), 0.12), uvs=1.0, skip_down=False)
                bm.free()


def geranium(pos, seed=2, n_leaf=11, h=0.3):
    rg = random.Random(seed)
    p0 = Vector(pos)
    for i in range(n_leaf):
        a = i * 2.39996
        rr = 0.03 + 0.07 * rg.random()
        base = p0 + Vector((math.cos(a) * 0.012, math.sin(a) * 0.012, 0.0))
        top = p0 + Vector((math.cos(a) * rr, math.sin(a) * rr, h * (0.5 + 0.5 * rg.random())))
        pts = [Vector(q) for q in bez(base, base + Vector((0, 0, h * 0.4)), top - Vector((0, 0, h * 0.2)), top, 6)]
        tube(M['leaf'], pts, 0.0028, seg=4, col=(0.35, 0.5, 0.25), caps=False)
        # round scalloped leaf
        lf = leaf_bm(L=0.075, W=0.052, curl=0.0, heart=True, stem=0.0, n=3)
        ang = a + rg.uniform(-0.3, 0.3)
        Mx = Matrix.Translation(top) @ rotm((0, 0, math.degrees(ang) - 90)) @ rotm((rg.uniform(60, 110), 0, 0)) @ Matrix.Diagonal((1.0, 1.0, 1.0, 1.0))
        put(M['leaf'], lf, Mx, col=jit((0.22, 0.38, 0.14), 0.15), uvs=1.0, skip_down=False)
        lf.free()
    # flower clusters
    for k in range(4):
        a = k * 1.7 + 0.5
        top = p0 + Vector((math.cos(a) * 0.06, math.sin(a) * 0.06, h * 1.05 + 0.03 * k))
        base = p0 + Vector((0, 0, 0.0))
        tube(M['leaf'], [Vector(q) for q in bez(base, base + Vector((0, 0, h * 0.5)), top - Vector((0, 0, 0.1)), top, 7)], 0.0024, seg=4, col=(0.4, 0.5, 0.25), caps=False)
        for j in range(11):
            b = j * 2.4
            q = top + Vector((math.cos(b) * 0.02 * (0.4 + 0.6 * (j % 3) / 2), math.sin(b) * 0.02 * (0.4 + 0.6 * (j % 3) / 2), 0.012 * ((j % 4) / 3) + 0.0))
            sphere(M['petal'], q, 0.0125, seg=7, rings=3, sq=(1, 1, 0.55), col=jit((0.82, 0.1, 0.15), 0.12))
            sphere(M['petal'], q + Vector((0, 0, 0.004)), 0.0045, seg=5, rings=3, col=(1.0, 0.85, 0.3))


def pothos_hanging(x, y, z_top, drop=0.7, seed=3):
    """macrame-hung terracotta planter from a beam with pothos vines (leaves via geometry nodes)"""
    rg = random.Random(seed)
    # hook + ring at the beam
    cyl(M['iron'], V(x, y, z_top - 0.005), 0.0035, 0.03, seg=6)
    torus(M['iron'], V(x, y, z_top - 0.05), 0.022, 0.0028, plane='xz', seg=16, rseg=5)
    pot_c = V(x, y, z_top - drop)
    r = 0.085
    # ropes
    for k in range(4):
        a = k * TAU / 4 + 0.4
        pts = [V(x, y, z_top - 0.072), pot_c + V(math.cos(a) * r * 0.5, math.sin(a) * r * 0.5, 0.2), pot_c + V(math.cos(a) * r * 1.0, math.sin(a) * r * 1.0, 0.08), pot_c + V(math.cos(a) * r * 0.75, math.sin(a) * r * 0.75, -0.02)]
        tube(M['linen'], [Vector(q) for q in catmull([(p.x, p.y, p.z) for p in pts], 5)], 0.0022, seg=5, col=(0.82, 0.74, 0.58), caps=False)
    # knots down the ropes
    for k in range(4):
        a = k * TAU / 4 + 0.4
        sphere(M['linen'], pot_c + V(math.cos(a) * r * 1.0, math.sin(a) * r * 1.0, 0.075), 0.007, seg=6, col=(0.8, 0.7, 0.55))
    # basket ring around the pot + pot
    torus(M['linen'], pot_c + V(0, 0, 0.0), r * 0.99, 0.006, plane='xy', seg=24, rseg=6, col=(0.8, 0.7, 0.55))
    top = terracotta_pot(pot_c + V(0, 0, -0.07), r=0.075, h=0.14, col=(0.78, 0.46, 0.32), saucer=False)
    # vines
    vines = []
    for k in range(7):
        a = k * 2.399 + 0.3
        L = rg.uniform(0.45, 1.05)
        pts = []
        start = pot_c + V(math.cos(a) * 0.07, math.sin(a) * 0.07, 0.05)
        for t in np.linspace(0, 1, 16):
            out = 0.07 + 0.085 * math.sin(min(t * 2.2, 1.0) * math.pi / 2) + 0.03 * math.sin(t * 5 + k)
            pts.append(pot_c + V(math.cos(a + 0.2 * t) * out, math.sin(a + 0.2 * t) * out, 0.05 - L * t * (0.6 + 0.5 * t) - 0.06 * math.sin(t * 3.0)))
        vines.append(pts)
        tube(M['leaf'], pts, 0.0028, seg=4, col=(0.35, 0.42, 0.2), caps=False)
    lf = leaf_bm(L=0.056, W=0.036, curl=0.0, heart=True, stem=0.01, n=6)
    for v in lf.verts:
        v.co.x += 0.0   # petiole offset handled by stem
    inst = gn_leaves(vines, lf, spacing=0.08, s0=1.1, s1=0.55, seed=seed)
    lf.free()
    # colour each leaf with a variegated green
    cl = inst.loops.layers.float_color.new('Col')
    for fc in inst.faces:
        for l in fc.loops:
            h = fbm(l.vert.co.x * 8, l.vert.co.y * 8, l.vert.co.z * 8, 2.0, 5, 2)
            g = (0.18 + 0.08 * h, 0.4 + 0.1 * h, 0.12 + 0.03 * h)
            if (int((l.vert.co.x * 50 + l.vert.co.y * 70)) % 5) == 0:
                g = (0.55, 0.62, 0.25)   # variegated yellow-green leaf
            l[cl] = (g[0], g[1], g[2], 1.0)
    # make sure UV layer exists
    if not inst.loops.layers.uv.active:
        inst.loops.layers.uv.new('UVMap')
    put(M['leaf'], inst, Matrix.Identity(4), uvs=1.0, skip_down=False)
    inst.free()


def sill_plants(f, x, items=('succulent', 'jar', 'candle'), z=0.0, y=0.04, spread=0.3):
    """small things on a window stool; f = wall frame (local x along the wall, local +y into the room, z absolute)"""
    xs = [x - spread / 2 + spread * k / max(len(items) - 1, 1) for k in range(len(items))]
    for it, xx in zip(items, xs):
        p = f.p((xx, y, z))
        if it == 'succulent':
            q = terracotta_pot(p, r=0.028, h=0.05, col=(0.82, 0.62, 0.48), saucer=False)
            for k in range(12):
                a = k * 2.399
                rr = 0.004 + 0.009 * (k / 12)
                lf = leaf_bm(L=0.032, W=0.011, curl=0.0, heart=False, stem=0.0, n=3)
                Mx = Matrix.Translation(q + Vector((math.cos(a) * rr, math.sin(a) * rr, 0.0))) @ rotm((0, 0, math.degrees(a) - 90)) @ rotm((-(35 + 45 * (k / 12)) * -1 + 0, 0, 0))
                put(M['leaf'], lf, Mx, col=jit((0.4, 0.58, 0.45), 0.1), uvs=1.0, skip_down=False); lf.free()
        elif it == 'jar':
            lathe(M['glass'], p, profile_pts([(0.0005, 0.0), (0.03, 0.0), (0.033, 0.004), (0.033, 0.075), (0.026, 0.085), (0.026, 0.095)], 2), seg=14, cap=False)
            lathe(M['water'], p, [(0.0005, 0.004), (0.029, 0.004), (0.03, 0.05), (0.0005, 0.05)], seg=12, cap=False, col=(0.85, 0.92, 0.9))
            # cuttings: stems with a few leaves
            for k in range(3):
                a = k * 2.1
                st = [p + Vector((math.cos(a) * 0.006, math.sin(a) * 0.006, 0.01)), p + Vector((math.cos(a) * 0.012, math.sin(a) * 0.012, 0.07)), p + Vector((math.cos(a) * 0.03, math.sin(a) * 0.03, 0.13))]
                tube(M['leaf'], [Vector(q) for q in catmull([(s.x, s.y, s.z) for s in st], 3)], 0.0018, seg=4, col=(0.4, 0.5, 0.25), caps=False)
                lf = leaf_bm(L=0.05, W=0.03, curl=0.0, heart=True, stem=0.0, n=4)
                put(M['leaf'], lf, Matrix.Translation(st[-1]) @ rotm((70, 0, math.degrees(a))), col=(0.25, 0.45, 0.18), uvs=1.0, skip_down=False); lf.free()
        elif it == 'candle':
            lathe(M['glass'], p, profile_pts([(0.0005, 0.0), (0.03, 0.0), (0.033, 0.004), (0.033, 0.06), (0.03, 0.062)], 2), seg=14, cap=False, col=(0.9, 0.7, 0.55))
            I.candle(p + Vector((0, 0, 0.004)), 0.05, 0.016, lit=False)
        elif it == 'shell':
            sphere(M['ceramic'], p + Vector((0, 0, 0.012)), 0.022, seg=12, sq=(1.2, 0.9, 0.55), col=(0.95, 0.88, 0.82))
        elif it == 'bottle':
            I.perfume_bottle(p, 2, (0.4, 0.62, 0.7), 0.1)
        elif it == 'herb':
            q = terracotta_pot(p, r=0.03, h=0.055, col=(0.8, 0.5, 0.36), saucer=False)
            for k in range(7):
                a = k * 2.399
                top = q + Vector((math.cos(a) * 0.012, math.sin(a) * 0.012, 0.05 + 0.01 * (k % 3)))
                tube(M['leaf'], [q, top], 0.0015, seg=4, col=(0.35, 0.5, 0.2), caps=False)
                for pr in range(2):
                    lf = leaf_bm(L=0.028, W=0.014, curl=0.0, heart=False, stem=0.0, n=3)
                    put(M['leaf'], lf, Matrix.Translation(top) @ rotm((60 + 20 * pr, 0, math.degrees(a) + 180 * pr)), col=jit((0.3, 0.55, 0.2), 0.1), uvs=1.0, skip_down=False); lf.free()


def _along(pos, dirv):
    q = Vector(dirv).normalized().to_track_quat('Z', 'Y')
    return Matrix.Translation(pos) @ q.to_matrix().to_4x4()


def dried_bundle(pos, kind='lavender', L=0.32, seed=0, tilt=(0, 0, 0)):
    """flowers hung upside-down from a beam: stems converge at the tie point `pos` (top)"""
    rg = random.Random(seed)
    Mx = xf(pos, tilt)
    n = {'hydrangea': 3, 'eucalyptus': 6}.get(kind, 8)
    cols = {'lavender': (0.5, 0.4, 0.68), 'wheat': (0.8, 0.65, 0.3), 'hydrangea': (0.62, 0.66, 0.8), 'eucalyptus': (0.45, 0.6, 0.55), 'rose': (0.7, 0.3, 0.35), 'statice': (0.85, 0.75, 0.4)}
    c0 = cols.get(kind, cols['lavender'])
    cyl(M['linen'], None, 0.014, 0.022, seg=8, Mx=Mx @ Matrix.Translation((0, 0, -0.03)), col=(0.7, 0.58, 0.4))
    tube(M['linen'], [Mx @ Vector((0, 0, 0.0)), Mx @ Vector((0.01, 0, 0.04)), Mx @ Vector((0.0, 0, 0.08))], 0.0015, seg=4, col=(0.7, 0.58, 0.4))
    for i in range(n):
        a = i * 2.399 + rg.uniform(0, 1)
        sp = (0.025 + 0.05 * rg.random()) if kind != 'hydrangea' else 0.04 + 0.05 * rg.random()
        l_ = L * rg.uniform(0.75, 1.0)
        end = Vector((math.cos(a) * sp, math.sin(a) * sp, -l_))
        mid = Vector((math.cos(a) * sp * 0.4, math.sin(a) * sp * 0.4, -l_ * 0.5))
        pts = [Mx @ Vector(q) for q in bez((0, 0, -0.03), Vector((0, 0, -0.03)) + mid * 0.5, mid + (end - mid) * 0.3, end, 4)]
        tube(M['leaf'], pts, 0.0013, seg=4, col=(0.45, 0.4, 0.22), caps=False)
        tip = pts[-1]
        back = (pts[-2] - pts[-1]).normalized()      # pointing back up the stem
        up_m = _along(tip, back)
        if kind == 'lavender' or kind == 'statice':
            ln = 0.06 if kind == 'lavender' else 0.035
            lathe(M['petal'], None, [(0.0005, 0.0), (0.0042, 0.006), (0.0052, 0.03 if kind == 'lavender' else 0.02), (0.003, ln * 0.85), (0.0005, ln)], seg=6, cap=False, Mx=up_m, col=jit(c0, 0.1))
        elif kind == 'wheat':
            lathe(M['petal'], None, [(0.0005, 0.0), (0.004, 0.01), (0.0048, 0.03), (0.003, 0.05), (0.0005, 0.06)], seg=6, cap=False, Mx=up_m, col=jit(c0, 0.08))
            for k in range(4):
                tube(M['leaf'], [tip + back * 0.02, tip + back * 0.075 + Vector((math.cos(k * 1.6) * 0.012, math.sin(k * 1.6) * 0.012, 0))], 0.0006, seg=3, col=jit(c0, 0.1), caps=False)
        elif kind == 'hydrangea':
            sphere(M['petal'], tip + back * 0.03, 0.04, seg=10, sq=(1, 1, 0.75), col=jit(c0, 0.06), noise=0.005)
            for k in range(5):
                bvec = Vector((rg.gauss(0, 1), rg.gauss(0, 1), rg.gauss(0, 1))).normalized() * 0.032
                sphere(M['petal'], tip + back * 0.03 + bvec, 0.012, seg=6, rings=3, col=jit((c0[0] * 1.05, c0[1], c0[2] * 1.05), 0.12))
        elif kind == 'eucalyptus':
            for k in range(6):
                q = tip + back * (0.03 * k + 0.02)
                for s in (-1, 1):
                    lf = leaf_bm(L=0.03, W=0.02, curl=0.0, heart=False, stem=0.0, n=2)
                    put(M['leaf'], lf, Matrix.Translation(q) @ rotm((90 * s + 30, 0, math.degrees(a) + 90 * s)), col=jit(c0, 0.1), uvs=1.0, skip_down=False); lf.free()
        else:
            sphere(M['petal'], tip, 0.012, seg=8, rings=4, col=jit(c0, 0.1))


# ------------------------------------------------------------------------------------------------ rugs
def braided_oval_rug(cx, cy, a, b, rot=0.0, rings=None):
    f = Fr((cx, cy, F), rot, F)
    pal = [(0.62, 0.22, 0.18), (0.88, 0.76, 0.52), (0.28, 0.4, 0.36), (0.55, 0.38, 0.24), (0.9, 0.84, 0.7), (0.2, 0.3, 0.45)]
    prof = [(0.0005, 0.011)]
    nr = 18
    for i in range(1, nr + 1):
        t = i / nr
        prof.append((t, 0.011 - 0.004 * t * t * 0 + 0.0))
    prof.append((1.03, 0.006)); prof.append((1.04, 0.0))

    def cfn(p):
        q = f.M.inverted() @ p
        rr = math.sqrt((q.x / a) ** 2 + (q.y / b) ** 2)
        k = int(rr * 22)
        c = pal[(k // 1) % len(pal)] if rr < 0.84 else pal[(k + 2) % len(pal)]
        br = 0.9 + 0.1 * math.sin(math.atan2(q.y / b, q.x / a) * 38 + k * 1.7)
        return (c[0] * br, c[1] * br, c[2] * br)
    f.lathe(M['rug'], (0, 0, 0), prof, seg=40, cap=False, scale=(a, b, 1.0), cfn=cfn)
    # raised braided bands at the border
    for (k, rr_) in enumerate((0.9, 0.95, 0.99)):
        pts = [Vector((math.cos(t) * a * rr_, math.sin(t) * b * rr_, 0.011)) for t in np.linspace(0, TAU, 80, endpoint=False)]
        f.tube(M['rug'], pts, 0.0085, seg=5, closed=True, col=pal[(k * 2 + 1) % len(pal)], flat=(1.0, 0.75))
    return f


def rag_runner(cx, cy, W, Lg, rot=0.0, cols=((0.6, 0.25, 0.2), (0.9, 0.82, 0.6), (0.3, 0.4, 0.45))):
    f = Fr((cx, cy, F), rot, F)
    f.box(M['rug'], (0, 0, 0.006), (W, Lg, 0.012), bev=0.003, seg=2, col=(0.9, 0.85, 0.75), g=1, skip_down=True)

    def cfn(p):
        q = f.M.inverted() @ p
        k = int((q.x + W / 2) / 0.035)
        c = cols[k % len(cols)] if abs(q.x) < W / 2 - 0.05 else cols[0]
        return c
    f.box(M['rug'], (0, 0, 0.0125), (W - 0.01, Lg - 0.01, 0.002), bev=0, cfn=cfn, g=1, skip_down=False)
    for k in range(int(W / 0.016)):
        x = -W / 2 + 0.008 + k * 0.016
        for sy in (-1, 1):
            f.tube(M['linen'], [Vector((x, sy * (Lg / 2 - 0.002), 0.008)), Vector((x + 0.002, sy * (Lg / 2 + 0.03), 0.006))], 0.0016, seg=3, col=(0.9, 0.84, 0.7), caps=False)
    return f


# ------------------------------------------------------------------------------------------------ misc
def plinth_block(x, y, rot, h=0.24, w=0.1):
    """decorative plinth block at a casing foot: x,y = centre on the wall plane, rot = Fr rot (local +y into the room); sits on the floor"""
    f = Fr((x, y, F), rot, F)
    f.box(M['paint'], (0, 0.02, h / 2), (w, 0.04, h), bev=0.004, seg=2, col=(0.95, 0.93, 0.86), g=2)
    f.box(M['paint'], (0, 0.03, h - 0.008), (w + 0.012, 0.05, 0.018), bev=0.003, col=(0.97, 0.95, 0.88), g=0)
    f.cyl(M['paint'], (0, 0.0435, h / 2), 0.026, 0.006, axis='y', seg=14, bev=0.002, col=(0.9, 0.87, 0.8))
    f.sphere(M['paint'], (0, 0.047, h / 2), 0.01, seg=10, sq=(1, 0.5, 1), col=(0.97, 0.95, 0.88))


def peg_rail(pos, rot, n=4, W=0.7, z=0.0):
    f = Fr(pos, rot, pos[2])
    f.box(M['wood_dark'], (0, 0.014, 0.0), (W, 0.028, 0.075), bev=0.005, col=(1.0, 0.92, 0.85), g=0)
    f.box(M['wood_dark'], (0, 0.03, 0.04), (W + 0.02, 0.02, 0.014), bev=0.004, col=(1.05, 0.97, 0.9), g=0)
    xs = [-W / 2 + 0.1 + k * (W - 0.2) / (n - 1) for k in range(n)]
    for x in xs:
        f.lathe(M['wood_dark'], (x, 0.028, 0.0), profile_pts([(0.0005, 0.0), (0.013, 0.0), (0.0095, 0.012), (0.0075, 0.06), (0.0125, 0.085), (0.0005, 0.093)], 2), r=(-90, 0, 0), seg=10, cap=False, col=(1.05, 0.97, 0.9))
    return f, xs


def hang_on_peg(f_wall, x, name, sp, drop_z=0.0):
    """cloth-simulated garment on a wooden hanger hooked on a peg of a wall rail (garment faces into the room)"""
    p = f_wall.p((x, 0.075, -0.0))
    fg = Fr(p + Vector((0, 0, 0.035)), f_wall.rot, p.z + 0.035)
    g = G.body_sim(name, 'coat', hang_h=sp['hang'], sh_w=sp['sh'], hem_scale=sp['hem'], phase=sp['phase'], amp=0.1, hb=sp['hb'])
    G.put_garment(fg, g, M[sp['mat']], cfn=fab(sp['col'], 0.08, 14, hash(name) % 7))
    G.hanger(fg, (0, 0, 0.0), sh_w=sp['sh'] * 1.02)
    sls = []
    for side in (-1, 1):
        sl = G.sleeve_sim(name + ('_sl%d' % side), side, g['v'], g['f'], sh_w=sp['sh'], length=sp['hang'] * 0.56, r0=0.04, r1=0.032)
        G.put_garment(fg, sl, M[sp['mat']], cfn=fab(sp['col'], 0.08, 14, hash(name) % 7 + 3))
        sls.append(sl)
    G.details(fg, g, sls, M[sp['mat']], sp['col'], pockets=(sp['mat'] == 'wool'))
    return fg


def base_accent(x, y, rot, length, label=None):
    """taller baseboard cap moulding + shoe moulding laid along a wall behind a big piece of furniture.
    (x,y) = centre on the wall plane, rot = Fr rotation (local +y into the room), local x along the wall."""
    f = Fr((x, y, F), rot, F)
    cap = [(0.0, 0.0), (0.012, 0.0), (0.024, 0.006), (0.03, 0.016), (0.03, 0.024), (0.018, 0.03), (0.0, 0.034)]
    f.prism(M['paint'], cap, length, c=(0, 0.024, 0.142), plane='yz', col=(0.96, 0.94, 0.88), g=0)
    shoe = [(0.0, 0.0), (0.03, 0.0), (0.03, 0.006), (0.018, 0.012), (0.008, 0.026), (0.0, 0.03)]
    f.prism(M['paint'], shoe, length, c=(0, 0.027, 0.0), plane='yz', col=(0.93, 0.9, 0.84), g=0)
    # little rosette stops at the ends
    for sx in (-1, 1):
        f.box(M['paint'], (sx * (length / 2 + 0.006), 0.026, 0.07), (0.014, 0.06, 0.145), bev=0.003, col=(0.97, 0.95, 0.9), g=2)
        f.cyl(M['paint'], (sx * (length / 2 + 0.014), 0.026, 0.07), 0.016, 0.004, axis='x', seg=10, col=(0.9, 0.87, 0.8))
