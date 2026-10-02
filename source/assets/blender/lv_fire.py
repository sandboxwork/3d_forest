"""Fireplace set, bellows, logs, crane+kettle, mantel decor, sheepskin hearth rug."""
from lv_books import *

IRON = lambda: M['iron_black']


def log_piece(c, d, L, r, seed=0, split=False, bark_col=(0.2, 0.15, 0.11), end_col=(0.6, 0.42, 0.24), crook=None):
    """firewood log: dense cylinder -> LATTICE modifier (crooked trunk) -> DISPLACE modifier (clouds bark relief) on top of fissures;
    ring end-grain caps; optional split (half round) with a planed face."""
    rr = random.Random(seed)
    c = Vector(c); d = Vector(d).normalized()
    NL, NA = 10, 16
    sd = rr.uniform(0, 100)
    a0, a1 = (0, TAU) if not split else (0.25, math.pi + 0.25)
    nA = NA if not split else NA // 2 + 1
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    rows = []
    for i in range(NL + 1):
        t = i / NL
        z = (t - 0.5) * L
        row = []
        for j in range(nA):
            a = a0 + (a1 - a0) * (j / (NA if not split else nA - 1))
            fis = 0.05 * math.sin(a * 7 + 2 * mnoise.noise(Vector((a * 1.3, t * 3, sd))) * 3) + 0.04 * mnoise.noise(Vector((a * 2.2 + sd, t * 6, 1.0)))
            rad = r * (1 + fis + 0.015 * math.sin(t * 5 + sd)) * (1.0 - 0.07 * (t < 0.03 or t > 0.97))
            row.append(bm.verts.new((math.cos(a) * rad, math.sin(a) * rad, z)))
        rows.append(row)
    nseg = nA if not split else nA - 1
    for i in range(NL):
        for j in range(nseg):
            j2 = (j + 1) % nA
            try:
                fc = bm.faces.new([rows[i][j], rows[i + 1][j], rows[i + 1][j2], rows[i][j2]][::-1])
            except ValueError:
                continue
            fc.smooth = True
            for l, uv in zip(fc.loops, [(j / nseg, i / NL), (j / nseg, (i + 1) / NL), ((j + 1) / nseg, (i + 1) / NL), ((j + 1) / nseg, i / NL)][::-1]):
                l[ul].uv = (uv[0] * 2 * math.pi * r, uv[1] * L)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # modifiers: crook via lattice, bark relief via displace
    lo, lat = make_lattice((r * 3.0, r * 3.0, L * 1.02), (2, 2, 4))
    cr = rr.uniform(-0.12, 0.12) * L if crook is None else crook
    ph = rr.uniform(0, 3)
    for i_, p_ in enumerate(lat.points):
        k = i_ // 4
        p_.co_deform.x += cr * math.sin(k / 3 * math.pi) / (r * 3.0)
        p_.co_deform.y += 0.3 * cr * math.sin(k / 3 * math.pi + ph) / (r * 3.0)
    tx = get_tex('lv_bark_noise', 'CLOUDS', noise_scale=0.06, noise_depth=2)
    bm = modbm(bm, [('LATTICE', dict(object=lo)), ('DISPLACE', dict(strength=0.0065, mid_level=0.45, texture=tx, direction='NORMAL'))])
    bpy.data.objects.remove(lo); bpy.data.lattices.remove(lat)
    Mx = Matrix.Translation(c) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    cb = C(bark_col)
    Mi = Mx.inverted()
    def bcf(p):
        l = Mi @ p
        k = 0.7 + 0.5 * (0.5 + 0.5 * math.sin(math.atan2(l.y, l.x) * 7 + 3 * mnoise.noise(Vector((l.x * 18, l.y * 18, l.z * 18)))))
        k *= 1 + 0.2 * nz(p.x * 30, p.y * 30, p.z * 30)
        return (cb[0] * k, cb[1] * k, cb[2] * k)
    put(M['bark'], bm, Mx, cb, bcf, 2)
    # end grain caps built from the deformed end rings
    vs = list(bm.verts)
    ec = C(end_col)
    for sgn, base in ((-1, 0), (1, NL * nA)):
        ring = vs[base:base + nA]
        cen = sum((v.co for v in ring), Vector()) / nA
        bm2 = bmesh.new()
        ctr = bm2.verts.new(cen)
        rg = [bm2.verts.new(cen + (v.co - cen) * 0.97) for v in ring]
        rg2 = [bm2.verts.new(cen + (v.co - cen) * 0.66) for v in ring]
        n_ = len(rg)
        for j in range(n_ if not split else n_ - 1):
            j2 = (j + 1) % n_
            q = [rg[j], rg[j2], rg2[j2], rg2[j]]
            q2 = [ctr, rg2[j], rg2[j2]]
            bm2.faces.new(q if sgn > 0 else q[::-1])
            bm2.faces.new(q2 if sgn > 0 else q2[::-1])
        def ecf(p, cen=cen):
            l = Mi @ p
            rad = math.hypot(l.x, l.y) / r
            ring_ = 0.5 + 0.5 * math.sin(rad * 30 + 2 * nz(p.x * 20, p.y * 20, p.z * 20))
            k = 0.78 + 0.28 * ring_ - 0.18 * (rad > 0.9)
            return (ec[0] * k, ec[1] * k, ec[2] * k)
        if not split:
            for fc in bm2.faces:
                pass
        put(M['endgrain'], bm2, Mx, ec, ecf, 2)
        bm2.free()
    if split:
        # planed flat face between the two arc edges
        bm3 = bmesh.new()
        e0 = [bm3.verts.new(rows_v.co) for rows_v in [vs[i * nA] for i in range(NL + 1)]]
        e1 = [bm3.verts.new(rows_v.co) for rows_v in [vs[i * nA + nA - 1] for i in range(NL + 1)]]
        for i in range(NL):
            try:
                bm3.faces.new([e0[i], e1[i], e1[i + 1], e0[i + 1]])
            except ValueError:
                pass
        bmesh.ops.recalc_face_normals(bm3, faces=bm3.faces[:])
        # make normals face away from the bark (toward -y local of the half circle centre)
        for fc in bm3.faces:
            nv = fc.normal
            ctr_ = fc.calc_center_median()
            if nv.dot(Vector((-math.sin(a0 + (a1 - a0) / 2), math.cos(a0 + (a1 - a0) / 2), 0))) < 0 and False:
                fc.normal_flip()
        def pcf(p):
            l = Mi @ p
            k = 0.85 + 0.2 * math.sin(l.x * 400 + 2 * nz(l.z * 30, 0.0, 1.0)) + 0.05 * nz(p.x * 50, p.y * 50, p.z * 50)
            return (ec[0] * k, ec[1] * k, ec[2] * k)
        put(M['endgrain'], bm3, Mx, ec, pcf, 2)
        bm3.free()
    bm.free()


def log_basket(pos, rot=0, r=0.27):
    f = Fr(pos, rot, F_)
    rr = random.Random(9)
    basket_woven(f.p(V(0, 0, 0)), r=r, h=0.34, rot=rot, seed=7, handle=True)
    # logs: leaning bundle
    for i in range(9):
        a = rr.uniform(0, TAU); rad = rr.uniform(0.0, r * 0.62)
        lean = rr.uniform(4, 22); la = rr.uniform(0, TAU)
        L = rr.uniform(0.34, 0.46); lr = rr.uniform(0.04, 0.062)
        base = f.p(V(math.cos(a) * rad, math.sin(a) * rad, 0.07))
        d = Vector((math.sin(math.radians(lean)) * math.cos(la), math.sin(math.radians(lean)) * math.sin(la), math.cos(math.radians(lean))))
        log_piece(base + d * L / 2, d, L, lr, seed=i + 3, split=(i % 4 == 3))
    for i in range(3):
        a = rr.uniform(0, TAU)
        d = Vector((math.cos(a), math.sin(a), rr.uniform(0.1, 0.3))).normalized()
        base = f.p(V(rr.uniform(-0.06, 0.06), rr.uniform(-0.06, 0.06), 0.3 + 0.0))
        log_piece(base, d, rr.uniform(0.28, 0.36), rr.uniform(0.04, 0.055), seed=20 + i)
    # kindling sticks and bark curls on the floor
    for i in range(7):
        a = rr.uniform(0, TAU); dd = rr.uniform(0.28, 0.42)
        p0 = f.p(V(math.cos(a) * dd, math.sin(a) * dd, 0.006))
        da = rr.uniform(0, TAU)
        tube(M['bark'], [p0, p0 + V(math.cos(da) * 0.1, math.sin(da) * 0.1, 0.002)], [0.006, 0.0045], seg=5, col=(0.45, 0.35, 0.26))
    collider_f(f, 2 * r + 0.05, 2 * r + 0.05, F_ + 0.5)
    return f


def twisted_rod(M0, L, r, turns=6, mat='iron_black', col=(0.2, 0.2, 0.22), n=36):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(M0 @ V(r * 0.5 * math.cos(t * turns * TAU), r * 0.5 * math.sin(t * turns * TAU), t * L))
    tube(M[mat], pts, r * 0.55, seg=5, col=col, caps=True)


def chain_links(p0, p1, n, r=0.0035, size=0.022, col=(0.18, 0.18, 0.2)):
    d = (p1 - p0)
    L = d.length
    dn = d.normalized()
    up = V(0, 0, 1) if abs(dn.z) < 0.9 else V(1, 0, 0)
    xa = dn.cross(up).normalized(); ya = dn.cross(xa)
    for i in range(n):
        c = p0 + dn * (L * (i + 0.5) / n)
        ax = xa if i % 2 == 0 else ya
        pts = []
        for k in range(13):
            a = k / 12 * TAU
            pts.append(c + dn * (math.cos(a) * L / n * 0.62) + ax * (math.sin(a) * size * 0.35))
        tube(M['iron_black'], pts, r, seg=5, col=col, caps=False)


def kettle_cast(p, rot=0, r=0.105, steam_name='kettle_steam_anchor'):
    """cast iron round-bellied kettle with spout, bail handle, lid; hung pose. returns spout tip world pos"""
    f = Fr(p, rot, None)
    s = r / 0.105
    cc = (0.32, 0.32, 0.34)
    body = [(0.001, 0.0), (0.06 * s, 0.0), (0.085 * s, 0.01 * s), (0.103 * s, 0.045 * s), (0.105 * s, 0.075 * s), (0.092 * s, 0.108 * s), (0.07 * s, 0.128 * s),
            (0.058 * s, 0.135 * s), (0.062 * s, 0.14 * s), (0.056 * s, 0.1425 * s), (0.052 * s, 0.136 * s), (0.052 * s, 0.12 * s)]
    f.lathe(M['iron_cast'], (0, 0, 0), body, seg=32, col=cc, cfn=lambda q: shade(cc, 0.8 + 0.3 * nz(q.x * 25, q.y * 25, q.z * 25) + 0.15 * (1 if (q.z - p.z) < 0.03 else 0)))
    f.lathe(M['iron_cast'], (0, 0, 0), [(0.001, 0.138 * s), (0.056 * s, 0.138 * s), (0.056 * s, 0.142 * s), (0.04 * s, 0.152 * s), (0.015 * s, 0.158 * s), (0.012 * s, 0.168 * s), (0.02 * s, 0.176 * s), (0.001, 0.178 * s)], seg=22, col=cc)
    # spout
    sp = bez((0.09 * s, 0, 0.03 * s), (0.14 * s, 0, 0.05 * s), (0.15 * s, 0, 0.1 * s), (0.175 * s, 0, 0.145 * s), 10)
    f.tube(M['iron_cast'], sp, [0.028 * s, 0.026 * s, 0.024 * s, 0.021 * s, 0.018 * s, 0.016 * s, 0.0145 * s, 0.013 * s, 0.0125 * s, 0.012 * s, 0.0118 * s], seg=12, col=cc)
    tip = f.p(V(0.175 * s, 0, 0.145 * s))
    # bail handle
    f.tube(M['iron_black'], [V(-0.1 * s * math.cos(math.radians(a)), 0, 0.1 * s + 0.12 * s * math.sin(math.radians(a))) for a in range(0, 181, 12)] if False else
           [V(-0.103 * s, 0, 0.095 * s)] + [V(-0.1 * s * math.cos(math.radians(a)), 0, 0.12 * s + 0.115 * s * math.sin(math.radians(a))) for a in range(10, 171, 10)] + [V(0.103 * s, 0, 0.095 * s)],
           0.0042, seg=6, col=(0.2, 0.2, 0.22))
    for sx in (-1, 1):
        f.box(M['iron_black'], (sx * 0.105 * s, 0, 0.095 * s), (0.008, 0.016, 0.02), bev=0.001, col=(0.2, 0.2, 0.22))
    # handle grip (wood) - wrapped at the top
    f.lathe(M['wood_dark'], (0, 0, 0.235 * s), [(0.0001, -0.03), (0.0065, -0.03), (0.0075, -0.02), (0.0075, 0.02), (0.0065, 0.03), (0.0001, 0.03)], seg=8, r=(0, 90, 0), col=(0.35, 0.22, 0.14), cap=False)
    return tip


def crane_kettle(swing=18.0):
    """swinging fireplace crane in the firebox (iron), kettle on a pot chain. no contact with the ember bed."""
    px, py = -4.12, -0.52
    z0 = 0.45
    ztop = 1.26
    ic = (0.2, 0.2, 0.22)
    # floor pintle plate + post
    cyl(M['iron_black'], Vector((px, py, z0 + 0.006)), 0.03, 0.012, seg=14, col=ic)
    tube(M['iron_black'], [Vector((px, py, z0 + 0.01)), Vector((px, py, ztop))], 0.0125, seg=10, col=ic)
    for z in (0.62, 0.95, ztop - 0.04):
        cyl(M['iron_black'], Vector((px, py, z)), 0.0185, 0.022, seg=12, col=ic)
    sphere(M['iron_black'], Vector((px, py, ztop + 0.012)), 0.019, seg=10, rings=6, col=ic)
    # wall bracket strap (to the firebox side wall at y=-0.54)
    box(M['iron_black'], Vector((px, py - 0.022, ztop - 0.04)), (0.04, 0.016, 0.07), bev=0.002, col=ic)
    for dx in (-0.012, 0.012):
        sphere(M['brass'] if False else M['iron_black'], Vector((px + dx, py - 0.03, ztop - 0.04)), 0.0045, seg=6, rings=3, col=(0.3, 0.3, 0.32))
    # arm (swung out by `swing` degrees from the +y direction toward +x)
    a = math.radians(swing)
    dirv = Vector((math.sin(a), math.cos(a), 0))
    La = 0.56
    za = ztop - 0.1
    p0 = Vector((px, py, za)); p1 = p0 + dirv * La
    tube(M['iron_black'], [p0, p0 + dirv * La * 0.5, p1], 0.0085, seg=8, col=ic)
    tube(M['iron_black'], [Vector((px, py, za - 0.4)) + dirv * 0.01, p0 + dirv * La * 0.62 + V(0, 0, -0.006)], 0.0058, seg=6, col=ic)   # diagonal brace
    box(M['iron_black'], Vector((px, py, za - 0.4)) + dirv * 0.01, (0.03, 0.02, 0.03), bev=0.002, col=ic)
    cyl(M['iron_black'], p0 + V(0, 0, 0.0), 0.016, 0.02, seg=10, col=ic)
    # end hook + trammel chain
    sphere(M['iron_black'], p1, 0.0105, seg=8, rings=5, col=ic)
    hook_top = p1 + V(0, 0, -0.012)
    kz = 0.97
    chain_end = Vector((p1.x, p1.y, kz + 0.255))
    chain_links(hook_top, chain_end, 6, r=0.0032, size=0.026)
    # S hook
    tube(M['iron_black'], [chain_end + V(0, 0, 0.0), chain_end + V(0.012, 0, -0.015), chain_end + V(0.0, 0, -0.03), chain_end + V(-0.012, 0, -0.04)], 0.0035, seg=5, col=ic)
    kp = Vector((p1.x, p1.y, kz))
    tip = kettle_cast(kp, rot=-(swing) + 90 + 180 + 0, r=0.105)
    return tip, kp


# ------------------------------------------------------------------ tools
def poker(base, tilt=(0, 0, 0)):
    M0 = Matrix.Translation(base) @ rotm(tilt)
    ic = (0.2, 0.2, 0.22)
    L = 0.5
    tube(M['iron_black'], [M0 @ V(0, 0, 0.0), M0 @ V(0, 0, L * 0.5), M0 @ V(0, 0, L)], [0.0012, 0.0052, 0.0052], seg=6, col=ic)
    twisted_rod(M0 @ Matrix.Translation((0, 0, L * 0.62)), L * 0.34, 0.013, 5)
    tube(M['iron_black'], [M0 @ V(0, 0, L * 0.96)] + [M0 @ V(0.02 * math.sin(a), 0, L + 0.02 * (1 - math.cos(a))) for a in [i * math.pi / 8 for i in range(1, 17)]], 0.0052, seg=6, col=ic) if False else None
    ring = [M0 @ V(0.022 * math.cos(a), 0, L + 0.022 + 0.022 * math.sin(a)) for a in [i * TAU / 20 for i in range(21)]]
    tube(M['iron_black'], ring, 0.0052, seg=6, col=ic, caps=False)
    # hooked tip
    tube(M['iron_black'], [M0 @ V(0, 0, 0.0), M0 @ V(0.0, 0, 0.0)], 0.001, seg=3) if False else None
    tube(M['iron_black'], [M0 @ V(0, 0, 0.06), M0 @ V(0.012, 0, 0.026), M0 @ V(0.026, 0, 0.012)], [0.0052, 0.0035, 0.002], seg=5, col=ic)


def tongs(base, tilt=(0, 0, 0)):
    M0 = Matrix.Translation(base) @ rotm(tilt)
    ic = (0.2, 0.2, 0.22)
    L = 0.42
    for s in (-1, 1):
        pts = [M0 @ V(s * 0.004, 0.0, 0.0), M0 @ V(s * 0.012, 0, 0.05), M0 @ V(s * 0.009, 0, 0.2), M0 @ V(0, 0, L * 0.62), M0 @ V(-s * 0.017, 0, L * 0.8), M0 @ V(-s * 0.024, 0, L * 0.92), M0 @ V(-s * 0.012, 0, L * 0.99)]
        tube(M['iron_black'], pts, [0.0045, 0.0042, 0.0048, 0.0048, 0.0048, 0.0048, 0.004], seg=6, col=ic)
        f_ = M0 @ V(s * 0.004, 0, 0.0)
        box(M['iron_black'], None, (0.014, 0.003, 0.03), M=M0 @ Matrix.Translation((s * 0.008, 0, 0.018)), bev=0.0005, col=ic)
    cyl(M['iron_black'], M0 @ V(0, 0, L * 0.62), 0.0075, 0.016, axis='y', seg=10, col=(0.3, 0.3, 0.32), M=None) if False else None
    lathe(M['iron_black'], None, [(0.001, -0.008), (0.0075, -0.008), (0.0075, 0.008), (0.001, 0.008)], seg=10, M=M0 @ Matrix.Translation((0, 0, L * 0.62)) @ rotm((90, 0, 0)), col=(0.3, 0.3, 0.32), cap=False)
    # handle loops
    for s in (-1, 1):
        ring = [M0 @ V(-s * 0.026 + s * 0.0 + 0.011 * math.cos(a) * -s, 0, L * 0.995 + 0.012 + 0.012 * math.sin(a)) for a in [i * TAU / 14 for i in range(15)]]
        tube(M['iron_black'], ring, 0.0035, seg=5, col=ic, caps=False)


def shovel(base, tilt=(0, 0, 0)):
    M0 = Matrix.Translation(base) @ rotm(tilt)
    ic = (0.2, 0.2, 0.22)
    L = 0.48
    # blade: slab with perforations via boolean modifier
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * 0.085, v.co.y * 0.1, v.co.z * 0.0035))
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=6, use_grid_fill=True)
    for v in bm.verts:
        v.co.z += -0.012 * (v.co.x / 0.0425) ** 2 + 0.0   # scooped
        v.co.x *= 1 - 0.18 * (v.co.y / 0.05 > 0.2) * ((v.co.y / 0.05) - 0.2)
    # perforations: boolean difference with a group of cylinders
    cut = bmesh.new()
    k = 0
    for ix in range(-2, 3):
        for iy in range(-2, 3):
            if (ix + iy) % 2 == 0 and abs(ix) + abs(iy) < 4:
                bmesh.ops.create_cone(cut, cap_ends=True, segments=8, radius1=0.0045, radius2=0.0045, depth=0.05,
                                      matrix=Matrix.Translation((ix * 0.017, iy * 0.018 + 0.0, 0.0)))
    cobj = obj_from_bm('_cut', cut)
    bo = modbm(bm, [('BOOLEAN', dict(operation='DIFFERENCE', object=cobj, solver='EXACT'))])
    bpy.data.objects.remove(cobj)
    put(M['iron_black'], bo, M0 @ Matrix.Translation((0, 0.0, 0.052)) @ rotm((-5, 0, 0)) @ rotm((0, 0, 0)) @ rotm((0, 0, 0)) @ Matrix.Rotation(0, 4, 'Z') @ Matrix.Rotation(math.radians(90), 4, 'X') @ Matrix.Identity(4), ic, g=2)
    bo.free()
    tube(M['iron_black'], [M0 @ V(0, 0, 0.1), M0 @ V(0, 0, L * 0.5), M0 @ V(0, 0, L * 0.9)], 0.0052, seg=6, col=ic)
    twisted_rod(M0 @ Matrix.Translation((0, 0, L * 0.55)), L * 0.22, 0.012, 4)
    ring = [M0 @ V(0.0, 0.021 * math.cos(a), L * 0.9 + 0.021 + 0.021 * math.sin(a)) for a in [i * TAU / 20 for i in range(21)]]
    tube(M['iron_black'], ring, 0.0052, seg=6, col=ic, caps=False)
    box(M['iron_black'], None, (0.004, 0.04, 0.03), M=M0 @ Matrix.Translation((0, 0, 0.1)), bev=0.001, col=ic)


def hearth_brush(base, tilt=(0, 0, 0)):
    M0 = Matrix.Translation(base) @ rotm(tilt)
    rr = random.Random(5)
    # bristle head (hanging down): tufts
    for i in range(46):
        a = rr.uniform(0, TAU); rd = rr.uniform(0.0, 0.027)
        L = rr.uniform(0.09, 0.115)
        x0 = rd * math.cos(a); y0 = rd * math.sin(a)
        sp = 0.18 * rd / 0.027
        tube(M['foliage'], [M0 @ V(x0, y0, 0.12), M0 @ V(x0 * 1.1, y0 * 1.1, 0.12 - L * 0.5), M0 @ V(x0 * (1 + sp * 2), y0 * (1 + sp * 2), 0.12 - L)], [0.0011, 0.0013, 0.0007], seg=3,
             col=(0.32 + 0.12 * rr.random(), 0.26 + 0.08 * rr.random(), 0.17), caps=False)
    # binding ring and handle
    lathe(M['wood_dark'], None, [(0.0001, 0.115), (0.022, 0.118), (0.03, 0.14), (0.034, 0.15), (0.03, 0.158), (0.012, 0.162), (0.0001, 0.162)], seg=14, M=M0, col=(0.35, 0.22, 0.14), cap=False)
    lathe(M['brass'], None, [(0.0305, 0.122), (0.0315, 0.13), (0.03, 0.134)], seg=14, M=M0, cap=False)
    lathe(M['wood_dark'], None, [(0.0001, 0.155), (0.012, 0.16), (0.011, 0.19), (0.016, 0.205), (0.011, 0.22), (0.009, 0.3), (0.012, 0.32), (0.009, 0.335), (0.0001, 0.34)], seg=10, M=M0, col=(0.35, 0.22, 0.14), cap=False)
    tube(M['iron_black'], [M0 @ V(0, 0, 0.335), M0 @ V(0, 0, 0.36)], 0.0015, seg=4, col=(0.2, 0.2, 0.22))


def tool_stand(base, rot=0):
    f = Fr(base, rot, F_)
    ic = (0.2, 0.2, 0.22)
    # weighted base: disc + foot ring + fluted baluster stem
    f.lathe(M['iron_black'], (0, 0, 0), [(0.001, 0), (0.095, 0), (0.1, 0.004), (0.098, 0.012), (0.08, 0.02), (0.05, 0.03), (0.025, 0.04), (0.018, 0.06), (0.026, 0.07), (0.016, 0.085), (0.013, 0.12), (0.0105, 0.4), (0.0105, 0.62), (0.015, 0.64), (0.02, 0.66), (0.012, 0.68), (0.001, 0.69)], seg=20, col=ic)
    for z in (0.16, 0.5):
        f.lathe(M['iron_black'], (0, 0, z), [(0.0105, -0.012), (0.018, -0.006), (0.021, 0), (0.018, 0.006), (0.0105, 0.012)], seg=14, col=ic, cap=False)
    f.lathe(M['brass'], (0, 0, 0.7), [(0.001, -0.008), (0.014, -0.006), (0.018, 0.006), (0.014, 0.018), (0.001, 0.022)], seg=14, cap=False)
    # top handle ring
    tube(M['iron_black'], [f.p(V(0.0, 0.0, 0.72 + 0.0) + V(0.04 * math.sin(a), 0, 0.04 * (1 - math.cos(a)) * 0.5 + 0.0)) for a in [i * math.pi / 8 for i in range(-8, 9)]], 0.0045, seg=5, col=ic) if False else None
    tube(M['iron_black'], [f.p(V(0.0, 0.0, 0.7) + V(0.035 * math.cos(a), 0.0, 0.035 * math.sin(a) + 0.03)) for a in [i * TAU / 18 for i in range(19)]], 0.0045, seg=5, col=ic, caps=False)
    # four hooks
    hooks = []
    for i in range(4):
        a = i * TAU / 4 + 0.4
        sp = [V(0.0, 0.0, 0.645), V(math.cos(a) * 0.04, math.sin(a) * 0.04, 0.657), V(math.cos(a) * 0.075, math.sin(a) * 0.075, 0.649), V(math.cos(a) * 0.082, math.sin(a) * 0.082, 0.63)]
        tube(M['iron_black'], [f.p(q) for q in sp], 0.0042, seg=5, col=ic)
        hooks.append((math.cos(a) * 0.082, math.sin(a) * 0.082))
    # tools hanging from hooks: tools' handle loops at the hooks, tips down
    tl = [poker, tongs, shovel, hearth_brush]
    for i, (hx, hy) in enumerate(hooks):
        top = f.p(V(hx, hy, 0.63))
        # hang with a slight outward lean: handles up, tip down -> flip tools (rotate 180 about x so +z points down)
        lean = 6 + 3 * i
        ang = math.degrees(math.atan2(hy, hx))
        if tl[i] is hearth_brush:
            base_ = top + V(0, 0, -0.0)
            tl[i](base_ + V(0, 0, -0.34), tilt=(0, 0, 0))
        else:
            # tool origin at its tip; hang upside-down means tip at the bottom: standard orientation (tip at z=0 bottom, handle up)
            L = {poker: 0.522, tongs: 0.45, shovel: 0.5}[tl[i]]
            tl[i](top + V(0, 0, -L - 0.0), tilt=(lean * math.sin(math.radians(ang)) * 0.0, lean * 0.0, 0))
    collider(f.pos.x - 0.12, f.pos.x + 0.12, f.pos.y - 0.12, f.pos.y + 0.12, F_ + 0.75)
    return f


def bellows(base, rot=0, open_=0.045):
    """leather bellows with turned handle + brass nozzle; lying flat. base = world pos of rear pivot (board bottom)"""
    f = Fr(base, rot, None)
    # outline (pear shaped), nozzle toward +y
    def outline(sc=1.0):
        pts = []
        R = 0.105
        for i in range(0, 13):
            a = math.pi + math.pi * i / 12     # back semicircle
            pts.append((R * math.cos(a), R + R * math.sin(a) * 1.0 * -1.0 * -1.0))
        pts = []
        for i in range(13):
            a = math.pi * i / 12
            pts.append((-R * math.cos(a), R - R * math.sin(a)))   # from (-R,R) round the back (y=0) to (R,R)
        # taper to nozzle
        pts += [(0.07, 0.2), (0.04, 0.3), (0.018, 0.38)]
        pts = pts + [(-0.018, 0.38), (-0.04, 0.3), (-0.07, 0.2)]
        return [(x * sc, y * sc if False else y) for x, y in pts]
    ol = outline()
    n = len(ol)
    zb = 0.0; th = 0.011
    woodc = (0.42, 0.27, 0.17)
    for k, (zz, tilt) in enumerate(((0.0, 0.0), (open_, 0.0))):
        bm = bmesh.new()
        rim = [bm.verts.new((x, y, zz + th * 0.0)) for (x, y) in ol]
        top = [bm.verts.new((x, y, zz + th)) for (x, y) in ol]
        # lift the tip of the upper board for an open pose
        if k == 1:
            for v in rim + top:
                v.co.z += 0.06 * (v.co.y / 0.38) ** 1.5 * 0.0
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([rim[i], rim[j], top[j], top[i]])
        c1 = bm.verts.new((0, 0.1, zz)); c2 = bm.verts.new((0, 0.1, zz + th))
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([c1, rim[j], rim[i]])
            bm.faces.new([c2, top[i], top[j]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        put(M['wood_walnut'], bm, f.M, woodc, wood_vc(woodc, 0.2, 9, 3 + k, axis=1), 2)
        bm.free()
        # brass studs around the board edge
        for i in range(0, n, 1):
            x, y = ol[i]
            if i % 1 == 0 and not (13 <= i <= 22 and False):
                sphere(M['brass'], f.p(V(x * 0.9, y + (0.0 if y > 0.2 else 0.0) , zz + th + 0.001)), 0.0042, seg=6, rings=3, sq=(1, 1, 0.5)) if k == 1 else None
    # decorative brass plate in the centre of the upper board (engraved look)
    for k in range(1):
        pass
    # leather bellows body: lofted accordion between boards
    K = 14
    folds = 3
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    rowsv = []
    for kk in range(K + 1):
        t = kk / K
        z = th + t * (open_ - th + 0.0)
        inset = 0.0 + 0.012 * abs(math.sin(t * math.pi * folds))
        # spread outline outward at fold crests
        spread = 1.0 - 0.0
        row = []
        for (x, y) in ol:
            # distance from board centre
            cx_, cy_ = 0.0, 0.14
            vx, vy = x - cx_, y - cy_
            ln = math.hypot(vx, vy) + 1e-9
            sc_ = 1.0 - inset * 0.0
            row.append(bm.verts.new((x * (0.93 - inset * 6.0 * 0.0 + 0.07 * (abs(math.sin(t * math.pi * folds)) ** 0.7) * 0.0) - 0.0, y, z)))
        rowsv.append(row)
    # radial pinch/expand: recompute rows properly
    bm.clear()
    rowsv = []
    for kk in range(K + 1):
        t = kk / K
        z = th + t * (open_ - th)
        crest = abs(math.sin(t * math.pi * folds))
        fx = 0.86 + 0.14 * crest
        row = []
        for (x, y) in ol:
            row.append(bm.verts.new((x * fx, 0.1 + (y - 0.1) * (0.98 if y < 0.3 else 1.0), z)))
        rowsv.append(row)
    for kk in range(K):
        for i in range(n):
            j = (i + 1) % n
            try:
                fc = bm.faces.new([rowsv[kk][i], rowsv[kk][j], rowsv[kk + 1][j], rowsv[kk + 1][i]])
                fc.smooth = True
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    lc = C('#5a3a22')
    put(M['leather'], bm, f.M, lc, lambda p: shade(lc, 0.85 + 0.3 * nz(p.x * 30, p.y * 30, p.z * 60)), 2)
    bm.free()
    # leather edge nailing: brass studs along the board edges (both boards)
    for zz in (th + 0.001, open_ - 0.001):
        for i in range(0, n):
            x, y = ol[i]
            sphere(M['brass'], f.p(V(x * 0.94, 0.1 + (y - 0.1) * 0.97, zz)), 0.0036, seg=5, rings=2, sq=(1, 1, 0.55))
    # nozzle (brass tube + flared tip) and wooden handle (turned) at the rear
    f.lathe(M['brass'], (0, 0.37, open_ * 0.5 + 0.0), [(0.0001, -0.0), (0.019, 0.0), (0.017, 0.0)], seg=6, cap=False) if False else None
    nz_pts = [V(0, 0.36, open_ * 0.5 + 0.005), V(0, 0.42, open_ * 0.5 + 0.004), V(0, 0.5, open_ * 0.5 + 0.003)]
    f.tube(M['brass'], nz_pts, [0.019, 0.011, 0.0065], seg=12, col=(1, 0.95, 0.85))
    f.lathe(M['brass'], (0, 0.5, open_ * 0.5 + 0.003), [(0.0065, -0.004), (0.0085, 0.0), (0.007, 0.007)], r=(-90, 0, 0), seg=12, cap=False) if False else None
    f.lathe(M['brass'], (0, 0.36, open_ * 0.5 + 0.005), [(0.021, 0.0), (0.022, 0.006), (0.018, 0.012)], r=(-90, 0, 0), seg=14, cap=False) if False else None
    hp = [V(0, 0.0, open_ * 0.5), V(0, -0.1, open_ * 0.5), V(0, -0.2, open_ * 0.5)]
    f.lathe(M['wood_walnut'], (0, -0.0, open_ * 0.5), [(0.001, 0.0), (0.012, 0.0), (0.016, 0.03), (0.011, 0.06), (0.012, 0.11), (0.018, 0.14), (0.014, 0.165), (0.001, 0.17)], r=(90, 0, 0), seg=12, col=woodc)
    # leather hinge flap at the rear
    f.box(M['leather'], (0, 0.002, open_ / 2 + th / 2), (0.1, 0.012, open_ + th), bev=0.002, col=lc)
    return f


# ------------------------------------------------------------------ mantel decor
def mantel_clock(pos, rot=0):
    """arched wooden mantel clock with brass dial"""
    f = Fr(pos, rot, None)
    wc = (0.34, 0.21, 0.13)
    vc = wood_vc(wc, 0.18, 9, 61, axis=2)
    W, D, H = 0.2, 0.09, 0.2
    f.box(M['wood_walnut'], (0, 0, 0.012), (W + 0.02, D + 0.014, 0.024), bev=0.003, cfn=vc, g=0)
    for s in (-1, 1):
        f.lathe(M['brass'], (s * (W / 2 - 0.012), D / 2 - 0.01, 0.0), [(0.001, 0.0), (0.011, 0.0), (0.012, 0.008), (0.008, 0.012)], seg=10, cap=True)
    f.box(M['wood_walnut'], (0, 0, 0.024 + H / 2 - 0.02), (W, D, H - 0.04), bev=0.004, cfn=vc, g=2)
    # arched top (half cylinder)
    f.lathe(M['wood_walnut'], (0, 0, 0.024 + H - 0.04), [(0.001, 0.0), (W / 2, 0.0), (W / 2 * 0.98, 0.02), (W / 2 * 0.7, 0.05), (W / 2 * 0.3, 0.065), (0.001, 0.07)], seg=22, cfn=vc, scale=(1.0, D / W, 1.0), cap=False)
    zc = 0.024 + H * 0.52
    f.lathe(M['brass'], (0, D / 2 + 0.0, zc), [(0.001, 0.0), (0.074, 0.0), (0.076, 0.003), (0.072, 0.007), (0.001, 0.007)], r=(-90, 0, 0), seg=28, cap=False)
    f.lathe(M['paper'], (0, D / 2 + 0.0065, zc), [(0.001, 0.0), (0.068, 0.0), (0.068, 0.001), (0.001, 0.001)], r=(-90, 0, 0), seg=28, col=(0.94, 0.9, 0.8), cap=False)
    for i in range(12):
        a = i * TAU / 12
        f.box(M['ink'], (math.sin(a) * 0.056, D / 2 + 0.0085, zc + math.cos(a) * 0.056), (0.003, 0.001, 0.009 if i % 3 == 0 else 0.006), r=(0, -math.degrees(a), 0), bev=0, col=(0.05, 0.05, 0.05))
    f.box(M['ink'], (0.012, D / 2 + 0.0095, zc + 0.017), (0.0035, 0.0012, 0.04), r=(0, -25, 0), bev=0, col=(0.03, 0.03, 0.03))
    f.box(M['ink'], (-0.016, D / 2 + 0.0105, zc + 0.002), (0.0025, 0.0012, 0.052), r=(0, 100, 0), bev=0, col=(0.03, 0.03, 0.03))
    f.lathe(M['brass'], (0, D / 2 + 0.0112, zc), [(0.001, 0.0), (0.004, 0.0), (0.004, 0.002), (0.001, 0.002)], r=(-90, 0, 0), seg=8, cap=False)
    # glass bezel ring
    f.tube(M['brass'], [V(0.077 * math.sin(a), D / 2 + 0.0095, zc + 0.077 * math.cos(a)) for a in [i * TAU / 28 for i in range(29)]], 0.0028, seg=6, caps=False)
    # brass finial
    f.lathe(M['brass'], (0, 0, 0.024 + H + 0.03), [(0.001, 0.0), (0.008, 0.004), (0.004, 0.012), (0.007, 0.02), (0.001, 0.026)], seg=10, cap=False)
    # side handles
    for s in (-1, 1):
        f.tube(M['brass'], [V(s * (W / 2), 0, zc + 0.02), V(s * (W / 2 + 0.014), 0, zc + 0.014), V(s * (W / 2 + 0.014), 0, zc - 0.012), V(s * (W / 2), 0, zc - 0.018)], 0.0022, seg=5)
    return f


def stag_figurine(pos, rot=0, col='#e4dccb'):
    p = Vector(pos); f = Fr(p, rot, None)
    c = C(col)
    cm = M['ceramic']
    f.lathe(cm, (0, 0, 0), [(0.001, 0), (0.04, 0), (0.044, 0.005), (0.04, 0.009), (0.001, 0.009)], seg=18, col=shade(c, 0.9), scale=(1.0, 0.6, 1.0))
    sphere(cm, f.p(V(0, 0, 0.065)), 0.03, seg=14, rings=9, sq=(0.75, 1.3, 0.8), col=c, rot=(0, 0, rot))
    for sx, sy in ((-0.011, -0.022), (0.011, -0.022), (-0.011, 0.024), (0.011, 0.024)):
        f.tube(cm, [V(sx, sy, 0.055), V(sx * 1.1, sy * 1.05, 0.03), V(sx * 1.1, sy * 1.05, 0.009)], [0.0058, 0.0042, 0.0038], seg=6, col=c)
    f.tube(cm, [V(0, -0.025, 0.075), V(0, -0.05, 0.1), V(0, -0.058, 0.123)], [0.011, 0.0085, 0.0075], seg=8, col=c)
    sphere(cm, f.p(V(0, -0.064, 0.127)), 0.0105, seg=10, rings=6, sq=(0.85, 1.2, 0.9), col=c, rot=(0, 0, rot))
    for s in (-1, 1):
        f.tube(cm, [V(s * 0.006, -0.062, 0.135), V(s * 0.016, -0.066, 0.155), V(s * 0.012, -0.07, 0.172)], [0.0022, 0.0018, 0.001], seg=4, col=(0.7, 0.6, 0.45))
        f.tube(cm, [V(s * 0.0145, -0.066, 0.152), V(s * 0.026, -0.068, 0.165)], [0.0015, 0.001], seg=4, col=(0.7, 0.6, 0.45))
        sphere(M['ink'], f.p(V(s * 0.0065, -0.0725, 0.13)), 0.0014, seg=5, rings=3)
    sphere(M['ink'], f.p(V(0, -0.0745, 0.1245)), 0.0016, seg=5, rings=3)


def pocket_watch(pos, rot=0):
    f = Fr(pos, rot, None)
    f.lathe(M['brass'], (0, 0, 0.0), [(0.001, 0.0), (0.021, 0.0), (0.0225, 0.004), (0.021, 0.009), (0.001, 0.009)], seg=22, cap=False)
    f.lathe(M['paper'], (0, 0, 0.0092), [(0.001, 0.0), (0.0185, 0.0)], seg=20, col=(0.95, 0.92, 0.82), cap=False)
    f.lathe(M['brass'], (0, 0, 0.0095), [(0.001, 0.0), (0.0195, 0.0), (0.0195, 0.0005)], seg=22, cap=False)
    f.tube(M['brass'], [V(0, 0.0215, 0.004), V(0, 0.027, 0.004)], 0.004, seg=6)
    f.tube(M['brass'], [V(0.007 * math.cos(a), 0.034 + 0.007 * math.sin(a), 0.004) for a in [i * TAU / 12 for i in range(13)]], 0.0013, seg=4, caps=False)
    pts = [V(0.0, 0.034, 0.004)]
    for i in range(1, 9):
        pts.append(V(0.01 * i * (1 if i % 2 else -0.3), 0.034 + 0.012 * i, 0.002 + 0.0006 * (i % 2)))
    f.tube(M['brass'], pts, 0.0009, seg=4)


def mantel_decor(rr_seed=4):
    mz = 1.60
    rr = random.Random(rr_seed)
    xm = -3.78
    res = {}
    # candlesticks with real melted wax, both lit
    top1 = candlestick((xm, -1.0, mz), h=0.27, kind='brass', cl=0.2, lit=True, wax=True, seed=3, inten=0.9, dist=5.0, name='lamp_liv_3')
    top2 = candlestick((xm, 1.0, mz), h=0.27, kind='brass', cl=0.15, lit=True, wax=True, seed=8, inten=0.9, dist=5.0, name='lamp_liv_4')
    candlestick((xm - 0.03, -0.78, mz), h=0.14, kind='pewter', cl=0.09, lit=False, wax=True, seed=11)
    # mantel clock
    mantel_clock((xm - 0.02, -0.38, mz), -90)
    # photographs
    photo_frame(V(xm + 0.02, 0.03, mz), -90 + 8, w=0.14, h=0.19, tilt=12, seed=1, fmat='wood_dark', fcol=(0.5, 0.33, 0.22))
    photo_frame(V(xm - 0.02, 0.24, mz), -90 - 6, w=0.1, h=0.14, tilt=12, seed=2, fmat='brass', fcol=(1.0, 0.95, 0.8))
    # dried flowers
    vase_dried(V(xm - 0.03, 0.62, mz), h=0.2, r=0.055, seed=12, vcol='#3e6a66', stems=16)
    # figurines
    stag_figurine(V(xm - 0.03, -0.62, mz), -90 + 20, '#e4dccb')
    figurine_bird(V(xm + 0.06, 0.82, mz), -90 - 30, '#8aa0b0')
    # small bowl with keys, pocket watch, matchbox
    bowl(V(xm + 0.02, 0.43, mz), r=0.05, h=0.03, col=C('#4e7299'))
    for k in range(3):
        a = k * 2.1
        tube(M['iron_black'], [V(xm + 0.02 + 0.015 * math.cos(a), 0.43 + 0.015 * math.sin(a), mz + 0.022), V(xm + 0.02 + 0.0, 0.43 + 0.0, mz + 0.026)], 0.0014, seg=4, col=(0.3, 0.3, 0.3))
    pocket_watch(V(xm + 0.12, -0.15, mz + 0.0), 20)
    box(M['wood_pine'], None, (0.05, 0.035, 0.015), M=Matrix.Translation((xm + 0.12, 0.42, mz + 0.0075)) @ rotm((0, 0, 12)), bev=0.001, col=(0.8, 0.6, 0.4))
    return top1, top2


# ------------------------------------------------------------------ sheepskin
def sheepskin(cx, cy, rot=0, sz=(0.62, 0.9), strands=2400, seed=3):
    rr = random.Random(seed)
    f = Fr((cx, cy, F_), rot, None)
    a_, b_ = sz[0] / 2, sz[1] / 2
    def edge(th):
        return 1 + 0.1 * math.sin(th * 3 + 1) + 0.07 * math.sin(th * 5 + 2) + 0.06 * math.cos(th * 7) + 0.1 * (math.cos(th * 4 + 0.5) ** 8)
    def inside(x, y):
        th = math.atan2(y / b_, x / a_)
        rr_ = math.hypot(x / a_, y / b_)
        return rr_ < edge(th) * 0.97
    # skin disc
    bm = bmesh.new()
    S, R = 36, 6
    ctr = bm.verts.new((0, 0, 0.012))
    rows = []
    for i in range(1, R + 1):
        t = i / R
        row = []
        for j in range(S):
            th = j / S * TAU
            row.append(bm.verts.new((a_ * t * math.cos(th) * edge(th) * 0.98, b_ * t * math.sin(th) * edge(th) * 0.98, 0.012 * (1 - t ** 3) + 0.004)))
        rows.append(row)
    for j in range(S):
        bm.faces.new([ctr, rows[0][j], rows[0][(j + 1) % S]])
    for i in range(R - 1):
        for j in range(S):
            k = (j + 1) % S
            bm.faces.new([rows[i][j], rows[i + 1][j], rows[i + 1][k], rows[i][k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    put(M['fur'], bm, f.M, (0.55, 0.5, 0.42), lambda p: (0.5 + 0.06 * nz(p.x * 20, p.y * 20, 1), 0.46 + 0.06 * nz(p.x * 20, p.y * 20, 1), 0.38), 2)
    bm.free()
    # fur: curved two-segment locks with blunt tips, direction field + curl, root dark -> tip light
    bm = bmesh.new()
    cl = bm.loops.layers.float_color.new('Col')
    ul = bm.loops.layers.uv.new('UVMap')
    n = 0
    tries = 0
    while n < strands and tries < strands * 3:
        tries += 1
        x = rr.uniform(-a_ * 1.1, a_ * 1.1); y = rr.uniform(-b_ * 1.1, b_ * 1.1)
        if not inside(x, y):
            continue
        ang = 0.9 * math.sin(x * 9 + 1) + 0.9 * math.cos(y * 7) + 1.2 * mnoise.noise(Vector((x * 7, y * 7, 3.0))) + math.atan2(y, x) * 0.3
        t_edge = math.hypot(x / a_, y / b_) / edge(math.atan2(y / b_, x / a_))
        Ls = rr.uniform(0.032, 0.05) * (1.0 + 0.3 * max(0, t_edge - 0.8) * 3) if n % 3 else rr.uniform(0.016, 0.026)
        lift = rr.uniform(0.25, 0.8)
        curl = rr.uniform(-0.9, 0.9)
        dx, dy = math.cos(ang), math.sin(ang)
        wdt = 0.0042
        px, py = -dy, dx
        z0 = 0.012
        pts = []
        # three stations: root, mid, tip with curl rotating the direction sideways
        a1 = ang + curl * 0.35; a2 = ang + curl * 0.9
        r0 = Vector((x, y, z0))
        m = r0 + Vector((math.cos(a1) * Ls * 0.5, math.sin(a1) * Ls * 0.5, Ls * lift * 0.6))
        tp = m + Vector((math.cos(a2) * Ls * 0.45, math.sin(a2) * Ls * 0.45, Ls * (lift * 0.45 - 0.22)))
        tp.z = max(tp.z, z0 + 0.004)
        sd1 = Vector((-math.sin(a1), math.cos(a1), 0)) * wdt * 0.8
        sd0 = Vector((px, py, 0)) * wdt
        sd2 = Vector((-math.sin(a2), math.cos(a2), 0)) * wdt * 0.3
        vs = [bm.verts.new(q) for q in (r0 - sd0, r0 + sd0, m + sd1, m - sd1, tp + sd2, tp - sd2)]
        try:
            f1 = bm.faces.new([vs[0], vs[1], vs[2], vs[3]])
            f2 = bm.faces.new([vs[3], vs[2], vs[4], vs[5]])
        except ValueError:
            continue
        ccol = 0.82 + 0.16 * rr.random() - 0.1 * (t_edge > 0.9)
        base_c = (0.93 * ccol, 0.88 * ccol, 0.78 * ccol)
        for fc, cols in ((f1, (0.5, 0.5, 0.85, 0.85)), (f2, (0.85, 0.85, 1.08, 1.08))):
            for l, k in zip(fc.loops, cols):
                l[cl] = (base_c[0] * k, base_c[1] * k, base_c[2] * k, 1.0)
        n += 1
    bm2 = get_bm(M['fur'])
    c2 = bm2.loops.layers.float_color['Col']
    u2 = bm2.loops.layers.uv['UVMap']
    Mx = f.M
    vm = {v: bm2.verts.new(Mx @ v.co) for v in bm.verts}
    for fc in bm.faces:
        try:
            nf = bm2.faces.new([vm[v] for v in fc.verts])
        except ValueError:
            continue
        nf.smooth = True
        for ls, l in zip(fc.loops, nf.loops):
            l[c2] = ls[cl]
            l[u2].uv = (ls.vert.co.x, ls.vert.co.y)
    bm.free()


def scatter_chips(cx, cy, r_out=0.6, density=70.0, seed=3, z=F_ + 0.0015, sc=(0.7, 1.5)):
    """Geometry Nodes scatter of bark flakes / wood chips on the floor around the log basket."""
    sb = bmesh.new()
    bmesh.ops.create_circle(sb, cap_ends=True, cap_tris=False, segments=24, radius=r_out)
    ib = bmesh.new()
    pts = [(-0.014, -0.007, 0.0), (0.014, -0.006, 0.0), (0.012, 0.006, 0.002), (-0.012, 0.007, 0.001)]
    vs = [ib.verts.new(p) for p in pts]
    mid = ib.verts.new((0, 0, 0.0035))
    for i in range(4):
        ib.faces.new([vs[i], vs[(i + 1) % 4], mid])
    bm = gn_scatter(sb, ib, density=density, seed=seed, scale=sc, tilt=0.18)
    rr = random.Random(seed)
    def cf(p):
        k = 0.7 + 0.5 * nz(p.x * 40, p.y * 40, 3.0)
        return (0.22 * k, 0.15 * k, 0.09 * k)
    put(M['foliage'], bm, Matrix.Translation((cx, cy, z)), (1, 1, 1), cf, 2)
    bm.free()
