"""Hanging herbs/braids, pot rack contents, cloth-simulated towels/apron/bread cloth, broom, window-sill herbs, shelf & top-of-furniture clutter."""
from kt_lib import *
from kt_ware import *
from kt_food import *
from kt_pots import *
from kt_counter import paint, jar_at, tin_can, lid_screw, label_on
from kt_storage import shelf_unit, wicker_basket, basket_with, plates_standing, sack_bm, tray, bucket

BEAM_Z = 2.96


def beam_hook(x, y, drop=0.0, mat='iron_black'):
    """wrought hook: small backplate screwed into the beam, eye bolt"""
    box(mat, (x, y, BEAM_Z - 0.004), (0.03, 0.03, 0.008), bev=0.002, seg=2)
    for sx in (-1, 1):
        dome(mat, (x + sx * 0.011, y, BEAM_Z - 0.0085), (0, 0, -1), r=0.0035)
    torus(mat, (x, y, BEAM_Z - 0.026), 0.011, 0.0028, plane='xz', seg=8, rseg=3, rot=(0, 0, 0))


def hanging_herb(x, y, kind, seed, L=0.32, n=7):
    beam_hook(x, y)
    top = Vector((x, y, BEAM_Z - 0.075))
    # twine hanging loop from the hook down to the tie
    tube('rope', [Vector((x, y, BEAM_Z - 0.036)), Vector((x, y, BEAM_Z - 0.075))], 0.0016, seg=4, col=(0.46, 0.34, 0.19))
    herb_bundle(top, L=L, kind=kind, n=n, seed=seed)


def braid(x, y, kind='onion', n=7, seed=1, L=0.55):
    """braided stalks with bulbs"""
    rr = random.Random(seed)
    beam_hook(x, y)
    top = Vector((x, y, BEAM_Z - 0.06))
    tube('rope', [Vector((x, y, BEAM_Z - 0.036)), top], 0.0016, seg=4, col=(0.46, 0.34, 0.19))
    # three braided strands (dry straw-coloured stems)
    for s in range(3):
        pts = []
        for i in range(14):
            t = i / 13
            amp = 0.011 * (1 - 0.2 * t)
            ph = s * TAU / 3
            pts.append(top + Vector((amp * math.sin(t * 20 + ph), amp * math.cos(t * 20 + ph), -t * L)))
        tube('herb_vc', pts, 0.0055 if kind == 'onion' else 0.0042, seg=4, col=jit((0.62, 0.5, 0.25), 0.1), taper=lambda t: 1.0 - 0.3 * t)
    for i in range(n):
        t = 0.08 + 0.9 * i / max(n - 1, 1)
        side = 1 if i % 2 == 0 else -1
        a = side * math.pi / 2 + rr.uniform(-0.4, 0.4)
        base = top + Vector((0.014 * math.cos(a), 0.014 * math.sin(a), -t * L))
        if kind == 'onion':
            c = (0.42, 0.2, 0.06) if i % 3 else (0.5, 0.3, 0.12)
            bm = onion_bm(seed * 11 + i, r=0.033 * rr.uniform(0.9, 1.1), col=c)
            r_ = 0.033
            ctr = base + Vector((0.032 * math.cos(a), 0.032 * math.sin(a), -0.036))
            place('food_vc', bm, ctr, rot=(180 + rr.uniform(-18, 18) * 0, 0, rr.uniform(0, 360)))
            # papery neck joins the braid
            tube('herb_vc', [base, base.lerp(ctr, 0.8) + Vector((0, 0, 0.035))], 0.004, seg=4, caps=False, col=(0.55, 0.42, 0.2))
        else:
            bm = garlic_bm(seed * 11 + i, r=0.025)
            ctr = base + Vector((0.022 * math.cos(a), 0.022 * math.sin(a), -0.04))
            place('food_vc', bm, ctr, rot=(180, 0, rr.uniform(0, 360)))
            tube('herb_vc', [base, ctr + Vector((0, 0, 0.04))], 0.0035, seg=4, caps=False, col=(0.7, 0.62, 0.45))
    # dried tail
    for k in range(3):
        a = k * 2.1
        tube('herb_vc', [top + Vector((0, 0, -L)), top + Vector((0.012 * math.cos(a), 0.012 * math.sin(a), -L - 0.07))], 0.003, seg=4, caps=False, col=(0.6, 0.5, 0.25))


def apple_ring_string(x, y, z0, dx=0.5, n=14):
    """dried apple rings on a string between two hooks"""
    a = Vector((x, y, z0)); b = Vector((x + dx, y, z0))
    pts = []
    for i in range(13):
        t = i / 12
        pts.append(a.lerp(b, t) + Vector((0, 0, -0.07 * math.sin(math.pi * t))))
    tube('rope', pts, 0.0012, seg=3, caps=False, col=(0.46, 0.34, 0.19))
    for i in range(n):
        t = (i + 0.5) / n
        p = pts[int(t * 12)] if False else a.lerp(b, t) + Vector((0, 0, -0.07 * math.sin(math.pi * t)))
        torus('food_vc', p, 0.017, 0.0055, plane='xz', seg=12, rseg=5, col=jit((0.82, 0.68, 0.4), 0.15), rot=(0, 0, rnd.uniform(-20, 20)))


def chili_string(x, y, z0, n=9):
    top = Vector((x, y, z0))
    tube('rope', [top, top + Vector((0, 0, -0.26))], 0.002, seg=4, col=(0.46, 0.34, 0.19))
    for i in range(n):
        t = i / n
        a = i * 2.4
        base = top + Vector((0.01 * math.cos(a), 0.01 * math.sin(a), -t * 0.24 - 0.02))
        lathe('food_vc', base, [(0.001, 0.0), (0.007, -0.006), (0.0065, -0.045), (0.0035, -0.075), (0.001, -0.085)], 8, col=jit((0.7, 0.07, 0.04), 0.2), cap=False, auto=False, rot=(0, rnd.uniform(-25, 25), a * 57))


# ====================================================================== cloth-sim items
def towel_over_rod(rod_a, rod_b, cx, width=0.32, front=0.28, back=0.24, col=(0.88, 0.84, 0.74), stripe=(0.55, 0.15, 0.1), seed=1):
    """tea towel draped over a rod (cloth simulation with the rod as collider)"""
    a, b = Vector(rod_a), Vector(rod_b)
    y0 = a.y
    zr = a.z
    Ltot = front + back
    nx, ny = 11, 18
    bm = cloth_grid(cx - width / 2, cx + width / 2, y0 - front, y0 + back, nx, ny, z=zr + 0.03, uvscale=1.0)
    for v in bm.verts:
        v.co.z += 0.003 * mnoise.noise(Vector((v.co.x * 9, v.co.y * 12, seed)))
        v.co.x += 0.012 * mnoise.noise(Vector((v.co.x * 5 + 3, v.co.y * 4, seed + 1)))   # slight sideways waviness -> soft vertical folds
        v.co.y += 0.01 * mnoise.noise(Vector((v.co.x * 6, v.co.y * 3 + 7, seed + 2)))
    rod = cyl_bm(0.0085, 0.9, 8, axis='x')
    col_mesh = [(rod, Matrix.Translation(Vector((cx, y0, zr))))]
    # stove top + warming shelf rail below: simple slab colliders so the towel can't poke through
    slab = cube_bm(0.9, 0.5, 0.02)
    cl = cloth_sim(bm, colliders=col_mesh + [(slab, Matrix.Translation(Vector((cx, y0 - 0.0 + 0.0, zr - 0.35 - 0.0))))] if False else col_mesh, frames=60, mass=0.15, tension=15, compression=15, shear=4, bending=0.15, quality=8,
                   friction=8, dist=0.0035, coll_dist=0.003)
    rod.free(); slab.free()

    def cf(p):
        k = 1 + 0.05 * fbm(p.x * 10, p.y * 10, p.z * 10, 1, seed, 2)
        c = col
        yy = p.y - y0
        for pos in (-0.22, -0.185, 0.185, 0.22):
            if abs(abs(p.z - zr) * 0.0 + yy - pos) < 0.008 and False:
                c = stripe
        # stripes by distance along the hang (arc length approx): bands near both ends
        s = (zr - p.z) if yy < 0 else (zr - p.z)
        if abs(s - 0.2) < 0.012 or abs(s - 0.17) < 0.006:
            c = stripe
        return (c[0] * k, c[1] * k, c[2] * k)
    put('linen_vc', cl, Matrix.Identity(4), cfn=cf, g=0)
    cl.free()


def apron_on_hook(hook, plane_x, cy, z_top, col=(0.78, 0.74, 0.62), seed=2, flip=1):
    """apron hanging by its neck strap from a wall hook (cloth sim; wall slab collider)"""
    hx, hy, hz = hook
    W, Hh = 0.5, 0.72
    ny, nx = 26, 20
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    V_ = [[None] * (ny + 1) for _ in range(nx + 1)]
    for i in range(nx + 1):
        for j in range(ny + 1):
            u = i / nx - 0.5
            v = j / ny
            V_[i][j] = bm.verts.new((plane_x, cy + u * W * (1.0 if v < 0.72 else 1.0), z_top - v * Hh))
    for i in range(nx):
        for j in range(ny):
            # bib (top 28%) narrower: keep only faces whose centre lies inside the apron outline
            u = (i + 0.5) / nx - 0.5
            v = (j + 0.5) / ny
            half = 0.5 if v > 0.28 else (0.26 / W) * 0.5 + (0.5 - (0.26 / W) * 0.5) * max(0.0, (v - 0.12) / 0.16) ** 2
            if abs(u) <= half + 0.0:
                f = bm.faces.new([V_[i][j], V_[i + 1][j], V_[i + 1][j + 1], V_[i][j + 1]])
                for l in f.loops:
                    l[ul].uv = (l.vert.co.y, l.vert.co.z)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    for v in bm.verts:
        v.co.x += 0.004 * mnoise.noise(Vector((v.co.y * 12, v.co.z * 12, seed)))
    wall = cube_bm(0.1, 3.0, 2.5)
    pin_z = z_top - 0.06
    cl = cloth_sim(bm, colliders=[(wall, Matrix.Translation(Vector((plane_x + 0.026 + 0.05, cy, 1.5))))], pin=lambda p: (p.z > pin_z and abs(p.y - cy) < 0.05), frames=60, mass=0.2,
                   tension=30, compression=30, shear=12, bending=1.2, quality=8, friction=15, dist=0.004, coll_dist=0.003, gravity=(0, 0, -9.8))
    wall.free()

    def cf(p):
        k = 1 + 0.05 * fbm(p.x * 8, p.y * 8, p.z * 8, 1, seed, 2)
        c = col
        if abs(p.z - (z_top - 0.55)) < 0.012:
            c = (0.3, 0.38, 0.55)
        if p.z < z_top - Hh + 0.04 and p.z > z_top - Hh + 0.028:
            c = (0.3, 0.38, 0.55)
        return (c[0] * k, c[1] * k, c[2] * k)
    put('linen_vc', cl, Matrix.Identity(4), cfn=cf, g=0)
    cl.free()
    # neck strap loop + hook, waist ties
    sweep('linen_vc', [(0.007 * math.cos(TAU * k / 6), 0.0022 * math.sin(TAU * k / 6)) for k in range(6)],
          [Vector((plane_x - 0.003, cy - 0.08, z_top - 0.1)), Vector((plane_x - 0.012, cy - 0.04, z_top + 0.0)), Vector((plane_x - 0.015, cy, hz + 0.0)), Vector((plane_x - 0.012, cy + 0.04, z_top + 0.0)),
           Vector((plane_x - 0.003, cy + 0.08, z_top - 0.1))], col=col)
    hook_peg(plane_x, cy, hz)


def hook_peg(x, y, z, L=0.07):
    """wall hook: plate + curved iron hook pointing out of the wall (-x direction)"""
    box('iron_black', (x + L * 0.0 + 0.045, y, z - 0.01), (0.012, 0.03, 0.07), bev=0.002, seg=2)
    tube('iron_black', [Vector((x + 0.04, y, z)), Vector((x + 0.0, y, z + 0.004)), Vector((x - 0.032, y, z + 0.012)), Vector((x - 0.04, y, z + 0.035))], 0.0045, seg=6)
    sphere('iron_black', Vector((x - 0.04, y, z + 0.038)), 0.0065, seg=6, rings=4)


def bread_in_cloth(P, rot=0):
    """loaf partly wrapped in a linen cloth (cloth drops on the loaf collider)"""
    lb = loaf_bm(0.27, 0.11, 0.085, seed=7, score=3, res=0.008)
    Mx = xf(P, (0, 0, rot))
    cl_ = cloth_grid(-0.2, 0.2, -0.17, 0.17, 24, 20, z=0.2, M=Mx)
    for v in cl_.verts:
        v.co.z += 0.003 * mnoise.noise(Vector((v.co.x * 11, v.co.y * 11, 4)))
    # collider: slimmed copy so cloth drapes over the middle section
    lbc = lb.copy()
    for v in lbc.verts:
        v.co.x *= 1.0
    plank = cube_bm(0.5, 0.4, 0.01, off=(0, 0, -0.005))
    out = cloth_sim(cl_, colliders=[(lbc, Mx), (plank, Mx)], frames=50, mass=0.1, tension=25, compression=25, shear=8, bending=0.8, quality=8, friction=15, dist=0.003, coll_dist=0.003)
    lbc.free(); plank.free()
    # loaf pokes out at both ends
    put('crust', lb, Mx, g=0)
    lb.free()
    put('linen_vc', out, Matrix.Identity(4), cfn=fab((0.9, 0.86, 0.78), 0.06, 12, 3), g=0)
    out.free()


# ====================================================================== broom + dustpan
def broom(x, y, z_top, rot=0):
    """corn broom hanging head-down on the partition: turned handle, bound brush of individual straws, twine wraps, hanging hole"""
    # vertical axis along z; wall is at +x (x=1.4), handle sits at x
    L = 1.22
    zb = z_top - L
    # handle
    prof = [(0.0125, 0), (0.0132, 0.1), (0.0125, 0.9), (0.0135, 1.0), (0.011, 1.15), (0.016, 1.17), (0.0155, 1.2), (0.0125, 1.22)]
    lathe('wood_oak', Vector((x, y, zb + 0.28)), [(a, b - 0.28 if False else b) for a, b in prof], 8, col=(0.95, 0.85, 0.7), cap=True) if False else None
    cyl('wood_oak', Vector((x, y, zb + 0.28 + 0.46)), 0.0125, 0.92, seg=8, col=(0.95, 0.86, 0.72))
    sphere('wood_oak', Vector((x, y, z_top + 0.0)), 0.016, seg=8, rings=5, col=(0.9, 0.8, 0.66), sq=(1, 1, 1.3))
    # hole + thong
    torus('rope', Vector((x, y, z_top - 0.03)), 0.014, 0.0025, plane='xz' if False else 'yz', seg=10, rseg=4, col=(0.5, 0.35, 0.2))
    # brush: flared bundle of individual straws (tapered tubes) - 54 straws
    rr = random.Random(3)
    zt_ = zb + 0.42
    for i in range(84):
        a = TAU * i / 84 + rr.uniform(-0.1, 0.1)
        rad = rr.uniform(0.0, 1.0) ** 0.5
        r0 = 0.012 * rad
        # flatten the brush in y (broad side along y)
        r1 = 0.03 + 0.03 * rad
        sx_ = math.cos(a); sy_ = math.sin(a)
        p0 = Vector((x + r0 * 0.6 * sx_, y + r0 * sy_, zt_ + 0.0))
        p1 = Vector((x + r1 * 0.5 * sx_, y + (r1 * 1.8 + 0.015) * sy_, zt_ - 0.1))
        p2 = Vector((x + (r1 * 0.55) * sx_, y + (r1 * 2.7 + 0.02) * sy_, zb + rr.uniform(-0.01, 0.02)))
        tube('straw', [p0, p1, p2], 0.0026, seg=3, caps=False, col=jit((0.55, 0.4, 0.17), 0.15))
    # sewn flat-broom stitched band + bindings
    for k in range(4):
        torus('rope', Vector((x, y, zt_ - 0.015 * k + 0.0)), 0.021 + 0.0 * k, 0.0034, plane='xy', seg=12, rseg=4, col=jit((0.38, 0.26, 0.14), 0.1))
    for k in range(3):
        torus('rope', Vector((x, y, zt_ - 0.09 - 0.012 * k)), 0.034, 0.0028, plane='xy', seg=14, rseg=4, col=(0.36, 0.25, 0.14))
    collider(x - 0.03, x + 0.03, y - 0.06, y + 0.06, z_top, F) if False else None


def dustpan(x, y, z):
    """tin dustpan hanging on a nail on the partition"""
    # flat scoop in the y-z plane, lip toward the floor, handle ring at top
    pts = [(0, 0), (0.24, 0), (0.28, 0.02), (0.28, 0.12), (0.0, 0.12)]
    # scoop plate (sloped) built as extruded polygon
    bm = bmesh.new()
    P = [(-0.12, 0.0), (0.12, 0.0), (0.105, 0.26), (-0.105, 0.26)]
    f = bm.faces.new([bm.verts.new((px, 0, pz)) for px, pz in P])
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]:
        v.co.y += 0.002
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # raised sides
    for sx in (-1, 1):
        sb = bmesh.new()
        PP = [(sx * 0.12, 0.0, 0.0), (sx * 0.105, 0.0, 0.26), (sx * 0.105, 0.045, 0.26), (sx * 0.12, 0.03, 0.0)]
        sb.faces.new([sb.verts.new(c) for c in PP])
        put('tin', sb, Matrix.Translation((x, y, z - 0.26)) @ Matrix.Rotation(math.radians(90), 4, 'Z') @ Matrix.Rotation(math.radians(14), 4, 'X'), g=0)
        sb.free()
    bm = modbm(bm, [('BEVEL', {'width': 0.0012, 'segments': 1, 'limit_method': 'ANGLE', 'angle_limit': math.radians(30)})])
    Mx = Matrix.Translation((x, y, z - 0.26)) @ Matrix.Rotation(math.radians(90), 4, 'Z') @ Matrix.Rotation(math.radians(14), 4, 'X')
    put('tin', bm, Mx, g=0)
    bm.free()


# ====================================================================== sill herbs
def herb_pot(P, kind, seed, rot=0):
    rr = random.Random(seed)
    Mx = xf(P, (0, 0, rot))
    r, h = 0.043, 0.075
    prof = [(0.001, 0.0), (r * 0.62, 0.0), (r * 0.66, 0.004), (r * 0.8, h * 0.5), (r * 0.96, h * 0.82), (r * 0.98, h * 0.83), (r * 1.08, h * 0.86), (r * 1.1, h * 0.99), (r * 1.02, h), (r * 0.94, h * 0.94), (r * 0.9, h * 0.9), (0.001, h * 0.9)]
    lathe('terracotta', None, prof, 16, M=Mx, cap=False, cfn=lambda p: (1 - 0.18 * fbm(p.x * 40, p.y * 40, p.z * 40, 1, seed, 2),) * 3)
    lathe('terracotta', None, [(0.001, 0.0), (r * 0.8, 0.0), (r * 0.9, 0.006), (r * 1.1, 0.011), (r * 1.1, 0.0)][::-1] if False else [(0.001, -0.004), (r * 0.8, -0.004), (r * 1.0, -0.002), (r * 1.15, 0.004), (r * 1.15, 0.0)], 16, M=Mx, cap=False) if False else None
    lathe('soil', None, [(0.001, h * 0.9), (r * 0.9, h * 0.9), (r * 0.88, h * 0.88)], 12, M=Mx, cap=False)
    # leaves: Geometry-Nodes scatter over a small dome (Poisson disk)
    dome_s = bmesh.new()
    bmesh.ops.create_icosphere(dome_s, subdivisions=2, radius=0.03)
    bmesh.ops.delete(dome_s, geom=[v for v in dome_s.verts if v.co.z < -0.002], context='VERTS')
    variants = []
    if kind == 'basil':
        for k in range(3):
            variants.append({'parts': [(leaf_bm(0.04, 0.028, curl=0.25, n=3, fold=0.2, col=(0.2 + 0.03 * k, 0.45, 0.1)), 'herb_vc')]})
        dist = 0.016
    elif kind == 'parsley':
        for k in range(3):
            variants.append({'parts': [(leaf_bm(0.032, 0.02, curl=0.35, n=3, fold=0.35, col=(0.12, 0.38 + 0.04 * k, 0.08)), 'herb_vc')]})
        dist = 0.013
    elif kind == 'chive':
        for k in range(3):
            variants.append({'parts': [(leaf_bm(0.09 + 0.02 * k, 0.003, curl=0.25, n=4, fold=0.0, col=(0.25, 0.5, 0.15)), 'herb_vc')]})
        dist = 0.008
    else:  # thyme / rosemary sprigs
        for k in range(3):
            variants.append({'parts': [(leaf_bm(0.045, 0.007, curl=0.12, n=3, fold=0.1, col=(0.3, 0.42, 0.22)), 'herb_vc')]})
        dist = 0.01
    outs = gn_scatter(dome_s, variants, distance=dist, density=40000, seed=seed + 5, scale=(0.8, 1.2), tilt=0.9, tint=0.15, surf_M=Mx @ Matrix.Translation((0, 0, h * 0.9 + 0.0)))
    put_outs(outs, Matrix.Identity(4))
    for v in variants:
        for (bb, mn) in v['parts']:
            bb.free()
    dome_s.free()


def sill_herbs():
    zs = 1.4625     # top of the interior sill stool
    ysill = WY - 0.015
    for k, (x, kind) in enumerate(((-2.62, 'basil'), (-2.5, 'parsley'), (-1.98, 'chive'), (-1.86, 'thyme'))):
        herb_pot(Vector((x, ysill, zs)), kind, seed=k + 1, rot=rnd.uniform(0, 360))
    # small saucer-lamp / glass of cuttings
    goblet(Vector((-2.38, ysill - 0.0, zs)), r=0.026, h=0.085, kind='tumbler', fill='water', fill_h=0.55)
    for i in range(3):
        tube('herb_vc', [Vector((-2.38 + 0.004 * i, ysill + 0.002, zs + 0.02)), Vector((-2.38 + 0.01 * (i - 1), ysill + 0.006, zs + 0.12))], 0.0012, seg=3, col=(0.25, 0.4, 0.15))
        place('herb_vc', leaf_bm(0.03, 0.018, curl=0.2, n=3, col=(0.2, 0.45, 0.12)), Vector((-2.38 + 0.01 * (i - 1), ysill + 0.006, zs + 0.12)), rot=(-30, 0, i * 120))


# ====================================================================== shelf & furniture-top clutter
def shelves_stuff():
    # lower shelf (z=1.85) - standing plates and stacked bowls, jars
    g = Fr((-1.42, WY, F + 1.85 - F + 0.012), 0)
    g.pos.z = 1.85 + 0.012 + 0.012
    base_z = 1.85 + 0.012
    f0 = Fr((-1.42, WY, F), 0)
    for k in range(4):
        P = f0.p((-0.19 + 0.12 * k, -0.045, 0)); P.z = base_z + 0.1 * math.cos(math.radians(12)) + 0.004
        plate(P, r=0.1, glaze='cream', rim=['blue', 'green', 'red', 'cobalt'][k], rot=(-90 + 12, 0, 180), seg=14, lod=1)
    P = f0.p((0.12, -0.11, 0)); P.z = base_z
    for k in range(3):
        bowl(P + Vector((0, 0, 0.0 + k * 0.024)), r=0.07 - 0.004 * k, h=0.045, glaze='cream', rim='blue', seg=12)
    balance_scale(f0.p((0.2, -0.1, 0)) + Vector((0, 0, base_z - f0.p((0, 0, 0)).z)), rot=0)
    # upper shelf (z=2.25) - mugs hung, jugs, candle, tins, recipe books
    base2 = 2.25 + 0.012
    for k in range(4):
        hk = f0.p((-0.2 + 0.1 * k, -0.04, 0)); 
        cyl('brass', Vector((hk.x, hk.y, 2.25 - 0.012)) + Vector((0, 0, 0)), 0.0025, 0.012, seg=5)
        mug(Vector((hk.x, hk.y, 2.25 - 0.012 - 0.07)), glaze=['red', 'cream', 'blue', 'cream'][k], rim=['cream', 'blue', None, 'blue'][k], r=0.032, h=0.062, rot=(0, 0, 90), seg=12)
    jug(f0.p((-0.15, -0.11, 0)) + Vector((0, 0, base2 - f0.p((0, 0, 0)).z)), r=0.05, h=0.16, glaze='cream', rot=(0, 0, 180), seg=16)
    tin_can(f0.p((0.05, -0.1, 0)) + Vector((0, 0, base2 - f0.p((0, 0, 0)).z)), 0.04, 0.12, (1, 1), rot=20)
    tin_can(f0.p((0.14, -0.08, 0)) + Vector((0, 0, base2 - f0.p((0, 0, 0)).z)), 0.036, 0.1, (2, 0), rot=60)
    for k in range(3):   # a few recipe books
        bm = cube_bm(0.04 - 0.004 * k, 0.12, 0.17 - 0.015 * k, off=(0, 0, (0.17 - 0.015 * k) / 2))
        bev_bm(bm, 0.002, 1)
        put('leather_vc', bm, Matrix.Translation(f0.p((0.21 + 0.043 * k, -0.1, 0))) @ Matrix.Translation((0, 0, base2 - F)) @ Matrix.Rotation(math.radians(-6 * k), 4, 'Y'), col=[(0.4, 0.15, 0.1), (0.15, 0.3, 0.35), (0.55, 0.45, 0.2)][k])
        bm.free()


def hutch_top():
    f = Fr((-0.4, WY - 0.21, F), 180)
    zt = F + 2.08 + 0.083
    # big wicker basket with dried flowers, a copper jug and a tureen
    wicker_basket(Vector((f.p((-0.28, -0.03, 0)).x, f.p((-0.28, -0.03, 0)).y, zt)), 0.14, 0.12, seed=2, handle=True, rot=f.rot)
    P = f.p((0.05, -0.03, 0)); P.z = zt
    lathe('copper', P, [(0.001, 0), (0.05, 0), (0.06, 0.03), (0.062, 0.08), (0.05, 0.14), (0.034, 0.17), (0.04, 0.19), (0.038, 0.2), (0.03, 0.18)], 18, cap=False)
    tube('copper', [P + Vector((-0.04, 0, 0.17)), P + Vector((-0.085, 0, 0.14)), P + Vector((-0.085, 0, 0.06)), P + Vector((-0.055, 0, 0.03))], 0.006, seg=6)
    vase = Vector((f.p((0.3, -0.03, 0)).x, f.p((0.3, -0.03, 0)).y, zt))
    jug(vase, r=0.05, h=0.2, glaze='teal', rot=(0, 0, f.rot), seg=16)
    for i in range(7):
        a = TAU * i / 7
        tube('herb_vc', [vase + Vector((0, 0, 0.19)), vase + Vector((0.04 * math.cos(a), 0.04 * math.sin(a), 0.32))], 0.0015, seg=3, col=(0.62, 0.55, 0.3))
        sphere('herb_vc', vase + Vector((0.04 * math.cos(a), 0.04 * math.sin(a), 0.325)), 0.009, seg=5, rings=3, col=jit((0.75, 0.55, 0.3), 0.2))


def pot_rack_stuff():
    cx, cy, zr = -2.2, 2.86, 2.55
    W, D = 1.2, 0.42
    pot_rack(cx, cy, zr, W=W, D=D)
    # hung items: saucepans by their handle holes (handle pointing up), frying pans, ladle etc.
    rr = random.Random(7)
    items = [(-0.45, -D / 2, 'sauce', 0.085, 'copper'), (-0.22, -D / 2, 'sauce', 0.07, 'copper'), (0.02, -D / 2, 'pan', 0.12, 'iron_cast'), (0.3, -D / 2, 'sauce', 0.06, 'copper'),
             (0.5, -D / 2, 'ladle', 0, ''), (-0.35, D / 2, 'pan', 0.1, 'iron_cast'), (-0.1, D / 2, 'sauce', 0.075, 'copper'), (0.15, D / 2, 'skim', 0, ''), (0.4, D / 2, 'wood', 0, '')]
    for (dx, dy, kind, rad, mat) in items:
        hook = Vector((cx + dx, cy + dy, zr))
        s_hook(hook + Vector((0, 0, 0.0)))
        hz = zr - 0.045
        if kind == 'sauce':
            hl = 0.2
            h_ = 0.07 + rad * 0.3
            # world pan frame: handle points +z, pan axis -x
            tilt = (0, -90, 0)
            Rr = rotm(tilt)
            off = Rr @ Vector((rad + hl, 0, h_ * 0.84))
            P = Vector((cx + dx, cy + dy, hz)) - off
            saucepan(P, r=rad, h=h_, mat=mat, handle_len=hl, tilt=tilt, seed=int(rad * 100))
        elif kind == 'pan':
            tilt = (0, -90, 0)
            Rr = rotm(tilt)
            off = Rr @ Vector((rad + 0.238, 0, 0.034))
            P = Vector((cx + dx, cy + dy, hz)) - off
            frying_pan(P, r=rad, tilt=tilt, seed=int(rad * 100))
        elif kind == 'ladle':
            ladle(Vector((cx + dx, cy + dy, hz - 0.085)), rot=(0, 0, 0)) if False else None
            Mt = xf(Vector((cx + dx, cy + dy, hz)), (-90 + 0, 0, 0))
            ladle(Vector((cx + dx, cy + dy, hz)) + Vector((0, 0, 0)), rot=(-90, 0, 90), L=0.32)
        elif kind == 'skim':
            skimmer(Vector((cx + dx, cy + dy, hz)), rot=(-90, 0, 90), L=0.33)
        else:
            wooden_spoon(Vector((cx + dx, cy + dy, hz)), rot=(-90, 0, 90), L=0.3)
    # dried-herb bunch on the rack front
    tube('rope', [Vector((cx - 0.55, cy - D / 2, zr + 0.02)), Vector((cx - 0.55, cy - D / 2, zr - 0.05))], 0.002, seg=4)


def build():
    # hanging herbs and braids from the real beam positions (x = -1.65, -0.55, 0.55; bottom z = 2.96)
    hanging_herb(-1.65, 2.35, 'lav', 21)
    hanging_herb(-1.65, 1.95, 'sage', 22, L=0.3)
    hanging_herb(-0.55, 2.65, 'herb', 23, L=0.34)
    hanging_herb(-0.55, 2.2, 'wheat', 24, L=0.36, n=9)
    hanging_herb(0.55, 2.55, 'dry', 25, L=0.3)
    hanging_herb(-2.75, 2.45, 'rose', 26, L=0.28)
    braid(0.55, 2.0, 'onion', 7, seed=1)
    braid(-1.65, 2.7, 'garlic', 8, seed=2, L=0.5)
    braid(-0.55, 1.75, 'onion', 6, seed=3, L=0.5)
    apple_ring_string(-2.75, 1.85, BEAM_Z - 0.05, 0.45, 12) if False else None
    chili_string(0.55, 1.65, BEAM_Z - 0.04)
    pot_rack_stuff()
    sill_herbs()
    shelves_stuff()
    hutch_top()
    # cloth items
    sf = Fr((-3.5, 2.935, F), 180)
    a = sf.p((-0.42, -0.075, 1.17)); b = sf.p((0.42, -0.075, 1.17))
    towel_over_rod(a, b, cx=-3.22, width=0.32, front=0.3, back=0.22, seed=3)
    towel_over_rod(a, b, cx=-3.74, width=0.28, front=0.22, back=0.17, seed=5, col=(0.82, 0.86, 0.9), stripe=(0.25, 0.35, 0.55))
    apron_on_hook((1.36, 1.95, 1.9), plane_x=1.335, cy=1.95, z_top=1.88)
    hf = Fr((-0.4, WY - 0.21, F), 180)
    bread_in_cloth(hf.p((0.3, -0.04, 0)) + Vector((0, 0, F + 0.94 + 0.0 - F + 0.0 + 0.0 + 0.0 - 0.0)) * 0 + Vector((0, 0, F + 0.9 + 0.04)) - Vector((0, 0, 0)) if False else Vector((hf.p((0.3, -0.04, 0)).x, hf.p((0.3, -0.04, 0)).y, F + 0.94)), rot=hf.rot + 10)
    # broom and dustpan on wall hooks of the partition
    hook_peg(1.36, 2.4, 1.78)
    hook_peg(1.36, 2.85, 1.35)
    rope_coil('rope', Vector((1.325, 2.85, 1.31)), R=0.085, r=0.0065, turns=5, steps=14, axis_rot=(0, 90, 0))
    hook_peg(1.36, 2.62, 1.55)
    broom(1.322, 2.4, 1.8)
    dustpan(1.327, 2.63, 1.52)
