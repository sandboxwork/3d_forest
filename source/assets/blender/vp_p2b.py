"""Batch 2b: laundry_line, signpost, street_lamp, bench_a, anvil_block, millstone_stack, fishing_dock_basket"""
from vp_h2 import *


# ------------------------------------------------------------------ laundry line
def hang_cloth(x0, x1, ztop, length, ycen, col, seed, folds=6, amp=0.025, cols2=None, mat='linen', sagfn=None):
    """vertical sheet hanging from the line between x0..x1."""
    w = x1 - x0

    def fn(u, v):
        x = x0 + w * u
        zt = ztop + (sagfn(x) if sagfn else 0.0)
        z = zt - length * v
        y = ycen + amp * math.sin(u * folds * math.pi + seed) * (0.3 + v) + 0.01 * math.sin(v * 5 + u * 3)
        return (x, y, z)
    bm = pgrid(max(6, int(w * 10)), 6, fn, su=w, sv=length)
    cf = lambda p: (lambda k: (col[0] * k, col[1] * k, col[2] * k))(1 + 0.08 * fbm(p.x, p.y, p.z, 4, seed, 2) + 0.05 * math.sin(p.x * (folds * 3.14159) * 1.0 + seed))
    put_bm(mat, bm, cfn=cols2 or cf, g=1)


def peg(x, y, z, col=H('#a58a62')):
    for s in (-1, 1):
        box('pine', (x + s * 0.007, y, z), (0.008, 0.012, 0.075), bev=0.001, col=col, rot=(0, 0, 0), skip_down=False)
    box('iron_dark', (x, y, z + 0.0), (0.022, 0.016, 0.006), bev=0.0, col=IRON_C)


@prop('laundry_line', '빨랫줄', ao_len=1.5, cam=lambda m: [((5.5, -4.5, 2.0), (0, 0, 1.4), 38), ((-4.8, 4.0, 2.0), (0, 0, 1.4), 38),
                                              ((1.2, -2.4, 1.6), (0.3, 0, 1.5), 40), ((-1.6, -2.5, 1.5), (-1.2, 0, 1.5), 40)])
def laundry_line():
    PW = H('#8a7a62')
    for sx in (-2, 2):
        beam('oak', (sx, 0, 0), (sx, 0, 2.3), 0.11, 0.11, bev=0.008, up=(0, 1, 0), col=PW, cfn=wood_cfn(PW, 0.15, 6, 3 + sx, grime_z=0.3))
        # top cap and hook, stone base
        box('oak', (sx, 0, 2.31), (0.15, 0.15, 0.04), bev=0.008, col=PW)
        for sy in (-1, 1):
            beam('oak', (sx, 0, 0.0), (sx, sy * 0.38, 0.0), 0.0001, 0.0001) if False else None
        # diagonal braces
        beam('oak', (sx, 0, 0.9), (sx - math.copysign(0.35, sx), 0, 0.0), 0.07, 0.06, bev=0.005, col=PW, up=(0, 1, 0)) if False else None
        # ground stones around the post
        for i in range(3):
            a = TAU * i / 3 + sx
            rock('stone', (sx + math.cos(a) * 0.13, math.sin(a) * 0.13, 0.04), (0.12, 0.1, 0.1), seed=i + sx, cfn=stone_cfn(H('#7d776d'), H('#a29780'), 4, 2), cuts=1)
        # iron ring
        FM(Matrix.Translation((sx + (-0.07 if sx > 0 else 0.07), 0, 2.15))).torus('iron_dark', (0, 0, 0), 0.035, 0.007, plane='yz', col=IRON_C)
    # line: sagging rope between ring points
    zl = 2.12

    def sag(x):
        t = (x + 1.93) / 3.86
        return -0.22 * 4 * t * (1 - t) * 1.0 if 0 <= t <= 1 else 0.0
    pts = [Vector((-1.93 + 3.86 * i / 40, 0, zl + sag(-1.93 + 3.86 * i / 40))) for i in range(41)]
    tube('rope', pts, 0.007, seg=5, col=ROPE_C, cfn=rope_twist_cfn(ROPE_C, 0.02), caps=True)

    def zline(x):
        return zl + sag(x)
    # big linen sheet (white)
    hang_cloth(-1.55, -0.55, zline(-1.05) + 0.015, 1.15, 0.0, H('#e6e0d0'), 1, folds=7, sagfn=lambda x: zline(x) - zline(-1.05))
    # coloured blanket
    def stripe(p):
        k = 1 if int((p.x + 5) * 9) % 4 else 0.7
        c = H('#a8473a') if k == 1 else H('#e0d4b4')
        return (c[0] * (0.92 + 0.08 * math.sin(p.z * 20)), c[1], c[2])
    hang_cloth(0.15, 1.0, zline(0.58) + 0.015, 0.95, 0.03, H('#a8473a'), 3, folds=5, cols2=stripe, sagfn=lambda x: zline(x) - zline(0.58))
    # shirts (torso + sleeves)
    def shirt(xc, col, seed, yc=0.0):
        zt = zline(xc)
        w = 0.5
        # torso hangs from shoulders (line at top)
        hang_cloth(xc - 0.2, xc + 0.2, zt - 0.02, 0.62, yc, col, seed, folds=3, amp=0.03)
        # sleeves: angled panels out from the shoulders
        for s in (-1, 1):
            def fn(u, v, s=s):
                x0 = xc + s * 0.2
                x = x0 + s * (0.14 + 0.1 * v) * (u * 0.0 + 1.0) * u
                z = zt - 0.02 - 0.08 * v * 0.5 - u * 0.18 - v * 0.07
                return (x, yc + 0.012 * math.sin(v * 4), z - 0.0 - (0.0))
            bm = pgrid(5, 6, lambda u, v, s=s: (xc + s * (0.2 + 0.2 * u), yc + 0.01 * math.sin(v * 3 + u * 2), zt - 0.02 - 0.20 * u - 0.12 * v * (1 - 0.3 * u) - 0.03 * u), su=0.2, sv=0.12)
            put_bm('linen', bm, col=col, g=1)
        # collar notch dark
        peg(xc - 0.19, yc, zt + 0.0)
        peg(xc + 0.19, yc, zt + 0.0)
    shirt(-0.1, H('#7a8fa8'), 2)
    shirt(1.45, H('#c4b48a'), 5, 0.01)
    # socks pair + small cloth
    for i, x in enumerate((-1.75, -1.68)):
        hang_cloth(x - 0.025, x + 0.025, zline(x) - 0.01, 0.2, 0.0, H('#6a5a8a') if i else H('#8a4a4a'), 7 + i, folds=2, amp=0.005)
        peg(x, 0, zline(x))
    # napkins / towel
    hang_cloth(1.7, 1.9, zline(1.8) - 0.0, 0.35, 0.0, H('#b0a590'), 9, folds=2, sagfn=lambda x: zline(x) - zline(1.8))
    # pegs on sheets
    for x in (-1.5, -0.62, 0.2, 0.92, 1.72, 1.88):
        peg(x, 0, zline(x) + 0.0)
    collider(-2.1, -1.9, -0.1, 0.1, 2.3, 0.0)
    collider(1.9, 2.1, -0.1, 0.1, 2.3, 0.0)


# ------------------------------------------------------------------ signpost
def arrow_bm(L, h, tip, t, nu=26, nv=4):
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    x0 = -0.18
    xb = L - tip
    V_ = {}
    for s_, zz in ((1, t / 2), (-1, -t / 2)):
        for i in range(nu + 1):
            x = x0 + (L - x0) * i / nu
            hh = h / 2 if x <= xb else h / 2 * max(0.0, (L - x) / tip)
            for j in range(nv + 1):
                if i == nu and j > 0:
                    V_[(s_, i, j)] = V_[(s_, i, 0)]
                    continue
                y = -hh + 2 * hh * j / nv if i < nu else 0.0
                V_[(s_, i, j)] = bm.verts.new((x, y, zz))
    def face(vs, flip):
        vs2 = []
        for v in vs:
            if not vs2 or vs2[-1] is not v:
                vs2.append(v)
        if vs2[0] is vs2[-1]:
            vs2.pop()
        if len(vs2) < 3:
            return
        try:
            f = bm.faces.new(vs2[::-1] if flip else vs2)
            f.smooth = False
        except ValueError:
            pass
    for s_ in (1, -1):
        for i in range(nu):
            for j in range(nv):
                face([V_[(s_, i, j)], V_[(s_, i + 1, j)], V_[(s_, i + 1, j + 1)], V_[(s_, i, j + 1)]], s_ < 0)
    # rim: bottom/top edges and left end
    for i in range(nu):
        face([V_[(1, i, 0)], V_[(-1, i, 0)], V_[(-1, i + 1, 0)], V_[(1, i + 1, 0)]], False)
        face([V_[(1, i, nv)], V_[(1, i + 1, nv)], V_[(-1, i + 1, nv)], V_[(-1, i, nv)]], False)
    for j in range(nv):
        face([V_[(1, 0, j)], V_[(1, 0, j + 1)], V_[(-1, 0, j + 1)], V_[(-1, 0, j)]], False)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f_ in bm.faces:
        for l_ in f_.loops:
            l_[ul].uv = (l_.vert.co.x, l_.vert.co.y)
    return bm


def arrow_board(c, yaw, length, h, col, pointing=1, seed=0, tilt=0.0):
    """blank arrow board centred at post: board spans from the post outwards along local +x (pointing=1) or -x."""
    tip = h * 0.55
    L = length
    bm = arrow_bm(L, h, tip, 0.032)
    cf = wood_cfn(col, 0.2, 7, seed, grime_z=0.0, axis=0)
    Mx = xf(c, (90, 0, yaw))
    put_bm('plain', bm, M=Mx, cfn=cf, g=0)
    # nails
    Mi = xf(c, (0, 0, yaw))
    for dx in (-0.08, 0.02):
        for dz in (-h * 0.28, h * 0.28):
            nail(Mi @ Vector((dx, -0.0165, dz)), d=Mi.to_3x3() @ Vector((0, -1, 0)), r=0.007)
    # cut-line on the grain (bevel-ish dark edge)


@prop('signpost', '이정표', ao_len=0.35, cam=lambda m: [((3.6, -4.2, 2.4), (0, 0, 1.9), 38), ((-3.4, 3.4, 2.6), (0, 0, 1.9), 38),
                                         ((0.5, -2.4, 2.4), (0, 0, 2.4), 45), ((-1.5, -2.0, 2.6), (0, 0, 2.5), 45)])
def signpost():
    PW = H('#8a7456')
    beam('oak', (0, 0, 0), (0, 0, 3.0), 0.13, 0.13, bev=0.01, up=(0, 1, 0), col=PW, cfn=lambda p: wood_cfn(PW, 0.16, 6, 4, grime_z=0.4)(p))
    box('oak', (0, 0, 3.02), (0.15, 0.15, 0.03), bev=0.01, col=PW)
    # chamfered cap pyramid
    lathe('plain', (0, 0, 3.035), [(0.075, 0), (0.06, 0.03), (0.0, 0.07)], seg=4, rot=(0, 0, 45), col=PW, cap=False, auto=False)
    # stone footing
    for i in range(7):
        a = TAU * i / 7
        rock('stone', (math.cos(a) * 0.17, math.sin(a) * 0.17, 0.07), (0.17, 0.15, 0.16), seed=i, rot=(0, 0, a), cfn=stone_cfn(H('#7d776d'), H('#a29780'), 4, 2, moss=0.4), cuts=2)
    arrow_board((0, -0.08, 2.65), -8, 0.95, 0.2, H('#9a8466'), seed=1)
    arrow_board((0, -0.08, 2.35), 188, 0.85, 0.19, H('#8a7658'), seed=2)
    arrow_board((0, -0.08, 2.05), 25, 0.75, 0.18, H('#a28e6c'), seed=3)
    # iron straps behind boards
    collider(-0.15, 0.15, -0.15, 0.15, 3.0, 0.0)


# ------------------------------------------------------------------ street lamp
@prop('street_lamp', '가로등', kind='light', ao_len=0.35, cam=lambda m: [((2.8, -3.6, 2.6), (0.2, 0, 1.8), 38), ((-3.0, 3.0, 2.8), (0.2, 0, 1.8), 38),
                                                        ((1.1, -1.5, 3.4), (0.4, 0, 3.1), 45), ((0.4, -1.1, 2.9), (0.45, 0, 3.0), 55)])
def street_lamp():
    PW = H('#6e5c46')
    # tapered post
    f = FM(Matrix.Identity(4))
    lathe('dark', (0, 0, 0), [(0.0, 0.0), (0.12, 0.0), (0.12, 0.08), (0.075, 0.13), (0.065, 2.95), (0.07, 3.03), (0.0, 3.03)], seg=8, rot=(0, 0, 22.5), col=PW, cap=False, auto=False,
          cfn=wood_cfn(PW, 0.15, 6, 4, grime_z=0.5, axis=2))
    # stone plinth
    box('stone', (0, 0, 0.14), (0.34, 0.34, 0.28), bev=0.015, col=H('#8a847a'), cfn=stone_cfn(H('#7d776d'), H('#a29780'), 4, 2, moss=0.4))
    # iron bands
    for z in (0.5, 1.5, 2.75):
        lathe('iron_forged', (0, 0, z), [(0.075, 0), (0.082, 0.0), (0.082, 0.05), (0.075, 0.05)], seg=8, rot=(0, 0, 22.5), col=FORGED, cap=False, auto=False)
    # bracket arm with scroll
    arm = [Vector((0.06, 0, 2.87)), Vector((0.25, 0, 2.95)), Vector((0.45, 0, 3.03)), Vector((0.62, 0, 3.05))]
    tube('iron_forged', polyline_smooth(arm, 5), 0.014, seg=8, col=FORGED)
    # diagonal brace with scroll
    br = [Vector((0.07, 0, 2.45)), Vector((0.2, 0, 2.7)), Vector((0.35, 0, 2.91)), Vector((0.5, 0, 3.02))]
    tube('iron_forged', polyline_smooth(br, 5), 0.011, seg=6, col=FORGED)
    sc = []
    for i in range(22):
        a = math.pi * 1.2 * i / 21
        rr = 0.075 * (1 - i / 26)
        sc.append(Vector((0.2 + math.cos(a + 1.2) * rr, 0, 2.71 + math.sin(a + 1.2) * rr)))
    tube('iron_forged', sc, 0.007, seg=5, col=FORGED)
    # lantern hanging from the arm end at x=0.62
    LX = 0.62
    chain_top = 3.05
    for k in range(5):
        torus('iron_forged', (LX, 0, 3.02 - k * 0.032), 0.012, 0.0035, plane='xz' if k % 2 else 'yz', seg=8, rseg=4, col=FORGED)
    z0 = 2.6   # lantern base
    # cage: base plate, 4 corner posts, top roof, glass panes
    box('iron_forged', (LX, 0, z0 + 0.02), (0.24, 0.24, 0.04), bev=0.006, col=FORGED)
    lathe('iron_forged', (LX, 0, z0), [(0.0, 0.0), (0.06, -0.0), (0.045, -0.04), (0.0, -0.05)], seg=8, col=FORGED, cap=False, auto=False)
    for sx in (-1, 1):
        for sy in (-1, 1):
            beam('iron_forged', (LX + sx * 0.105, sy * 0.105, z0 + 0.04), (LX + sx * 0.085, sy * 0.085, z0 + 0.38), 0.016, 0.016, bev=0.002, col=FORGED, up=(1, 0, 0))
    for (dx, dy, sx_, sy_) in ((0.0, -0.095, 0.18, 0.004), (0.0, 0.095, 0.18, 0.004), (-0.095, 0.0, 0.004, 0.18), (0.095, 0.0, 0.004, 0.18)):
        box('glass', (LX + dx * 0.97, dy * 0.97, z0 + 0.21), (sx_ if sx_ > 0.01 else 0.004, sy_ if sy_ > 0.01 else 0.004, 0.33), bev=0.0, col=(1, 1, 1), skip_down=False, flat=True)
    # horizontal bands
    for z in (z0 + 0.12, z0 + 0.3):
        box('iron_forged', (LX, 0, z), (0.2, 0.2, 0.008), bev=0.0, col=FORGED) if False else None
    box('iron_forged', (LX, 0, z0 + 0.4), (0.25, 0.25, 0.025), bev=0.005, col=FORGED)
    lathe('iron_forged', (LX, 0, z0 + 0.41), [(0.17, 0.0), (0.14, 0.04), (0.07, 0.1), (0.03, 0.12), (0.0, 0.13)], seg=4, rot=(0, 0, 45), col=FORGED, cap=False, auto=False)
    cyl('iron_forged', (LX, 0, z0 + 0.56), 0.022, 0.03, seg=8, col=FORGED)
    torus('iron_forged', (LX, 0, z0 + 0.562), 0.02, 0.005, plane='xz', col=FORGED, seg=8, rseg=4)
    # candle + flame
    cyl('wax', (LX, 0, z0 + 0.09), 0.025, 0.1, seg=10, col=H('#e8dcb8')) if False else cyl('plain', (LX, 0, z0 + 0.09), 0.025, 0.1, seg=10, col=H('#e8dcb8'))
    lathe('flame', (LX, 0, z0 + 0.15), [(0.0, 0.0), (0.014, 0.012), (0.02, 0.035), (0.012, 0.07), (0.0, 0.1)], seg=10, col=(1, 1, 1), cap=False, auto=False)
    set_light((LX, 0, z0 + 0.2), (1.0, 0.72, 0.4))
    collider(-0.17, 0.17, -0.17, 0.17, 2.9, 0.0)


# ------------------------------------------------------------------ bench
@prop('bench_a', '나무 벤치', ao_len=0.35, cam=lambda m: [((2.4, -2.6, 1.4), (0, 0, 0.45), 40), ((-2.4, 2.2, 1.5), (0, 0, 0.45), 40),
                                          ((0.9, -1.2, 0.8), (0.4, 0, 0.45), 45), ((-1.1, -1.2, 0.8), (-0.6, 0, 0.4), 45)])
def bench_a():
    PW = H('#a08a68')
    cf = lambda s: wood_cfn(PW, 0.16, 7, s, grime_z=0.25)
    # seat: 2 thick planks
    for k, y in enumerate((-0.095, 0.095)):
        beam('pine', (-0.84, y, 0.455), (0.84, y, 0.455), 0.18, 0.045, bev=0.007, col=jitter_col(PW, 0.08), cfn=cf(k), up=(0, 0, 1))
    # backrest: 2 slats
    for k, z in enumerate((0.72, 0.88)):
        beam('pine', (-0.8, 0.205, z), (0.8, 0.205, z), 0.025, 0.12, bev=0.005, col=jitter_col(PW, 0.08), cfn=cf(5 + k), up=(0, 0, 1))
    # back posts angled
    for sx in (-1, 1):
        beam('pine', (sx * 0.72, 0.15, 0.0), (sx * 0.72, 0.22, 0.98), 0.06, 0.05, bev=0.006, col=PW, cfn=cf(9), up=(1, 0, 0)) if False else beam('pine', (sx * 0.72, 0.17, 0.0), (sx * 0.72, 0.23, 0.98), 0.055, 0.055, bev=0.006, col=PW, cfn=cf(9), up=(1, 0, 0))
        # front legs splayed
        beam('pine', (sx * 0.72, -0.17, 0.0), (sx * 0.70, -0.15, 0.43), 0.055, 0.055, bev=0.006, col=PW, cfn=cf(11), up=(1, 0, 0))
        # side apron
        beam('pine', (sx * 0.72 + sx * 0.0, -0.17, 0.4), (sx * 0.72, 0.17, 0.4), 0.03, 0.09, bev=0.004, col=PW, up=(0, 0, 1), cfn=cf(12))
        # stretcher
    beam('pine', (-0.72, 0.0, 0.2), (0.72, 0.0, 0.2), 0.05, 0.05, bev=0.005, col=PW, cfn=cf(13))
    for sx in (-1, 1):
        beam('pine', (sx * 0.74, -0.2, 0.2), (sx * 0.74, 0.18, 0.2), 0.04, 0.04, bev=0.004, col=PW, cfn=cf(14), up=(1, 0, 0)) if False else None
        # pegs
        for z in (0.43,):
            nail((sx * 0.72, -0.02, 0.48), d=(0, 0, 1), r=0.01)
    for sx in (-0.6, 0.6):
        for y in (-0.095, 0.095):
            nail((sx, y, 0.4775), d=(0, 0, 1), r=0.009)
    collider(-0.85, 0.85, -0.25, 0.28, 0.5, 0.0)


# ------------------------------------------------------------------ anvil on stump
@prop('anvil_block', '모루와 그루터기', ao_len=0.35, cam=lambda m: [((1.8, -2.0, 1.3), (0, 0, 0.7), 40), ((-1.8, 1.6, 1.4), (0, 0, 0.7), 40),
                                                   ((0.7, -1.0, 1.1), (0, 0, 0.82), 45), ((-0.8, -0.9, 1.0), (0.1, 0, 0.85), 45)])
def anvil_block():
    # stump (irregular, with bark flares and axe marks)
    prof = [(0.0, 0.0), (0.32, 0.0), (0.355, 0.04), (0.28, 0.12), (0.255, 0.3), (0.25, 0.55), (0.265, 0.62), (0.0, 0.62)]
    bm = _stump(prof)
    bark = lambda p: mixc(H('#4e3d2c'), H('#6b5540'), (fbm(p.x * 2, p.y * 2, p.z * 14, 1.0, 3, 2) * 0.5 + 0.5)) if p.z < 0.61 else mixc(H('#a58a62'), H('#8a6e4a'), 0.5 + 0.5 * math.sin(math.hypot(p.x, p.y) * 70 + fbm(p.x, p.y, 0, 7, 2, 2) * 3))
    put_bm('bark', bm, cfn=bark, g=2)
    # iron band
    lathe('iron_forged', (0, 0, 0.5), [(0.247, 0.0), (0.257, 0.0), (0.257, 0.04), (0.247, 0.04)], seg=24, col=FORGED, cap=False, auto=False)
    # anvil
    zt = 0.62
    ia = H('#5a5a62')
    ic = lambda p: mixc(H('#5a5a62'), H('#7a7a84'), 0.5 + 0.5 * fbm(p.x, p.y, p.z, 12, 2, 2))
    # body (side profile in XZ, extruded in Y)
    body = [(-0.2, 0.30), (-0.2, 0.2), (-0.12, 0.17), (-0.07, 0.12), (-0.07, 0.04), (0.0, 0.0), (0.0, 0.0), (0.07, 0.04), (0.07, 0.12), (0.12, 0.17), (0.2, 0.2), (0.2, 0.30)]
    # convex pieces: waist (tapered), face block, base
    put_bm('iron_forged', prism([(-0.24, 0.0), (0.24, 0.0), (0.2, 0.06), (-0.2, 0.06)], 0.22, bev=0.006), M=xf((0, 0, zt), (90, 0, 0)) @ Matrix.Translation((0, 0.0, 0)), cfn=ic)
    put_bm('iron_forged', prism([(-0.09, 0.0), (0.09, 0.0), (0.12, 0.14), (-0.12, 0.14)], 0.14, bev=0.006), M=xf((0, 0, zt + 0.06), (90, 0, 0)), cfn=ic)
    put_bm('iron_forged', prism([(-0.19, 0.0), (0.19, 0.0), (0.21, 0.07), (-0.21, 0.07)], 0.17, bev=0.004), M=xf((0, 0, zt + 0.2), (90, 0, 0)), cfn=ic)
    put_bm('iron_forged', prism([(-0.21, 0.0), (0.2, 0.0), (0.2, 0.05), (-0.21, 0.05)], 0.12, bev=0.004), M=xf((0, 0, zt + 0.27), (90, 0, 0)), cfn=ic) if False else None
    # horn (cone toward -x)
    lathe('iron_forged', (-0.19, 0, zt + 0.235), [(0.075, 0.0), (0.06, -0.12), (0.03, -0.24), (0.0, -0.3)], seg=12, rot=(0, -90, 0), col=ia, cap=False, auto=False, cfn=ic) if False else None
    Mh = xf((-0.2, 0, zt + 0.225), (0, -90, 0))
    lathe('iron_forged', None, [(0.06, 0.0), (0.045, 0.1), (0.025, 0.2), (0.008, 0.26)], seg=12, M=Mh, col=ia, cap=False, auto=False, cfn=ic)
    # heel block
    box('iron_forged', (0.24, 0.0, zt + 0.235), (0.1, 0.16, 0.07), bev=0.008, col=ia, cfn=ic)
    # hardy hole
    box('plain', (0.17, 0.0, zt + 0.272), (0.025, 0.025, 0.004), bev=0.0, col=(0.02, 0.02, 0.02))
    # hammer on the stump edge
    hm = (0.18, 0.25, 0.69)
    beam('oak', (0.1, 0.22, 0.705), (0.3, 0.3, 0.705), 0.03, 0.03, bev=0.006, col=H('#8a6a46'), cfn=wood_cfn(H('#8a6a46'), 0.12, 20, 4, grime_z=0), up=(0, 0, 1))
    box('iron_forged', (0.04, 0.2, 0.715), (0.05, 0.05, 0.12), rot=(0, 0, 25), bev=0.005, col=ia, cfn=ic)
    # tongs lying
    for s in (-1, 1):
        pts = [Vector((-0.1, -0.28 + s * 0.012, 0.7)), Vector((-0.2, -0.3 + s * 0.02, 0.705)), Vector((-0.34, -0.33 + s * 0.045, 0.705)), Vector((-0.44, -0.36 + s * 0.09, 0.705))]
        tube('iron_forged', polyline_smooth(pts, 4), 0.009, seg=6, col=ia)
    cyl('iron_forged', (-0.14, -0.285, 0.708), 0.014, 0.03, axis='z', seg=8, col=ia)
    # iron chips / scale around
    for i in range(8):
        a = i * 0.9
        rock('iron_forged', (math.cos(a) * 0.5 + 0.1, math.sin(a) * 0.5, 0.012), (0.05, 0.04, 0.02), seed=i, col=H('#33302c'), cuts=1)
    collider(-0.42, 0.42, -0.42, 0.42, 0.95, 0.0)


def _stump(prof, seg=28):
    bm = lathe_bm(prof, seg, 1.0, True)
    rr = random.Random(4)
    for v in bm.verts:
        a = math.atan2(v.co.y, v.co.x)
        r = math.hypot(v.co.x, v.co.y)
        if r > 0.05:
            k = 1 + 0.045 * math.sin(a * 5 + 1.0) + 0.03 * math.sin(a * 9) + 0.02 * mnoise.noise(Vector((v.co.x * 9, v.co.y * 9, v.co.z * 6)))
            # root flare lumps
            fl = max(0.0, 1 - v.co.z / 0.18) * 0.1 * max(0.0, math.sin(a * 4.0 + 0.5)) ** 2
            v.co.x *= (k + fl); v.co.y *= (k + fl)
    bm.normal_update()
    return bm


# ------------------------------------------------------------------ millstones
def millstone_geo(c, R=0.62, t=0.19, groove=True, seed=0, tilt=None):
    cf = stone_cfn(H('#b2aca0'), H('#cfc3a6'), 3.0, seed, moss=0.3)
    f = FM(tilt if tilt is not None else Matrix.Translation(c))
    # side
    prof = [(0.1, 0.0), (R - 0.01, 0.0), (R, 0.012), (R + 0.004, t * 0.5), (R, t - 0.012), (R - 0.01, t)]
    bmside = lathe_bm(prof, 32, 1.0, False)
    for v in bmside.verts:
        a = math.atan2(v.co.y, v.co.x)
        r_ = math.hypot(v.co.x, v.co.y)
        if r_ > R - 0.05:
            k = 1 + 0.006 * mnoise.noise(Vector((v.co.x * 14, v.co.y * 14, v.co.z * 30 + seed)))
            v.co.x *= k; v.co.y *= k
    put_bm('stone', bmside, M=f.M, cfn=cf, g=2)
    # top face with furrows (polar grid) -- carved radial/curved furrows
    nr, ns = (6, 48) if groove else (2, 32)

    def fn(u, v):
        r_ = 0.075 + (R - 0.01 - 0.075) * u
        a = TAU * v
        z = t
        if groove and u > 0.03:
            ph = ((a / TAU * 16) + 0.9 * (r_ / R) * 1.0) % 1.0
            d = 0.0
            if ph < 0.22:
                d = 0.016 * math.sin(ph / 0.22 * math.pi) ** 0.7
            z -= d * min(1.0, u * 4)
            z -= 0.0012 * mnoise.noise(Vector((math.cos(a) * r_ * 30, math.sin(a) * r_ * 30, seed)))
        return (math.cos(a) * r_, math.sin(a) * r_, z)
    bm = pgrid(nr, ns, fn, su=1, sv=1)
    # reverse faces so normal points up
    bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    ul_ = bm.loops.layers.uv.active
    for f_ in bm.faces:
        for l_ in f_.loops:
            l_[ul_].uv = (l_.vert.co.x, l_.vert.co.y)
    put_bm('stone', bm, M=f.M, cfn=lambda p: cf(p), g=2)
    # eye hole wall + inner hole
    lathe('stone', None, [(0.075, t), (0.07, t * 0.5), (0.07, 0.0)], seg=16, M=f.M, col=H('#6a655c'), cap=False, auto=False)
    lathe('stone', None, [(0.075, t), (0.09, t - 0.012), (0.1, t - 0.01)], seg=16, M=f.M, col=H('#8a847a'), cap=False, auto=False) if False else None
    # bottom
    lathe('stone', None, [(0.1, 0.0), (0.0 + 0.0, 0.0)], seg=3, M=f.M, col=cf(Vector((0, 0, 0))), cap=False, auto=False) if False else None


@prop('millstone_stack', '맷돌 더미', ao_len=2.0, cam=lambda m: [((2.4, -3.0, 1.6), (0, 0, 0.4), 40), ((-2.8, 2.4, 1.6), (0, 0, 0.4), 40),
                                                 ((0.6, -1.6, 1.4), (0, 0, 0.5), 45), ((1.3, -0.6, 1.9), (0.2, 0.2, 0.45), 45)])
def millstone_stack():
    for i, (dx, dy, rz) in enumerate(((0.0, 0.0, 0.0), (0.02, -0.015, 24), (-0.015, 0.02, 41))):
        millstone_geo((dx, dy, i * 0.205), R=0.62 - 0.01 * i, t=0.19, groove=(i == 2), seed=i, tilt=xf((dx, dy, i * 0.205), (0, 0, rz)))
    # leaning stone against the stack on the +x/-y side: tilted about local y, rests on ground at x=0.62+
    a = math.radians(66)
    Rm = 0.5
    Mt = xf((1.0, -0.55, 0.0), (0, 0, 20)) @ Matrix.Translation((0, 0, 0.02)) @ Matrix.Rotation(-(math.pi / 2 - a), 4, 'Y') @ Matrix.Translation((0, 0, 0.0))
    # stone local: disk around z with thickness t; rotate so axis points along -x tilt
    Mt = xf((0.98, -0.3, 0.0), (0, 0, 20)) @ Matrix.Rotation(math.radians(72), 4, 'Y') @ Matrix.Translation((0, 0, -0.03))
    millstone_geo(None, R=Rm, t=0.17, groove=True, seed=7, tilt=Mt)
    # small rock chocks
    for i, (x, y) in enumerate(((1.15, -0.5), (1.1, -0.1))):
        rock('stone', (x, y, 0.05), (0.2, 0.16, 0.1), seed=30 + i, cfn=stone_cfn(H('#7d776d'), H('#a29780'), 4, 2), cuts=2)
    # moss / dirt near ground handled by AO
    collider(-0.65, 0.65, -0.65, 0.65, 0.62, 0.0)
    collider(0.7, 1.25, -0.8, 0.0, 0.8, 0.0)


# ------------------------------------------------------------------ fishing basket
@prop('fishing_dock_basket', '생선 바구니', ao_len=1.5, cam=lambda m: [((1.7, -2.0, 1.2), (0.1, 0, 0.2), 40), ((-1.6, 1.8, 1.1), (0.0, 0, 0.2), 40),
                                                       ((0.5, -0.9, 0.75), (0.0, -0.05, 0.25), 45), ((-0.3, -0.85, 0.65), (-0.1, -0.1, 0.2), 45)])
def fishing_dock_basket():
    # basket
    f = wicker_basket((0, 0, 0), R=0.3, h=0.36, taper=0.72, stakes=26, rows=3, handle=False, seed=5, col=(0.8, 0.62, 0.38))
    # inner fish mound
    lathe('plain', (0, 0, 0), [(0.0, 0.2), (0.24, 0.2), (0.27, 0.3)], seg=16, cap=False, col=(0.1, 0.08, 0.06), auto=False)
    r = random.Random(6)
    cols = [(H('#4a6070'), H('#d8dcd8')), (H('#5a6a50'), H('#d8d6b8')), (H('#40505e'), H('#e0e2e0')), (H('#6a6a5a'), H('#d6d0b6'))]
    N = 5
    for i in range(N):
        a = TAU * i / N + r.uniform(-0.2, 0.2)
        rr = r.uniform(0.0, 0.14)
        M0 = xf((math.cos(a) * rr, math.sin(a) * rr, 0.3 + (i % 2) * 0.05), (r.uniform(-8, 8), r.uniform(-8, 12), math.degrees(a) + r.uniform(-50, 50)))
        b, bl = cols[i % 4]
        fish(M0 @ Matrix.Translation((-0.14, 0, 0)), L=0.3, Hh=0.075, Wd=0.04, back=b, belly=bl, bend=r.uniform(-0.08, 0.08), seed=i)
    # a fish hanging over the rim with tail out
    M0 = xf((0.28, -0.1, 0.34), (0, 22, -70))
    fish(M0, L=0.32, Hh=0.08, Wd=0.042, back=H('#4a6070'), belly=H('#dde0dc'), bend=0.05)
    # loose fish on the ground
    for i, (x, y, rot) in enumerate(((-0.55, -0.35, 30), (0.5, -0.5, 100))):
        M0 = xf((x, y, 0.025), (0, 0, rot)) @ Matrix.Rotation(math.radians(80), 4, 'X') if False else xf((x, y, 0.028), (0, 0, rot))
        fish(M0, L=0.28, Hh=0.07, Wd=0.038, back=cols[i + 1][0], belly=cols[i + 1][1], bend=0.06)
    # rope coil
    pts = []
    for i in range(0, 5 * 20 + 1):
        a = TAU * i / 20
        k = i / 20
        pts.append(Vector((0.6 + math.cos(a) * (0.2 - 0.012 * k), 0.3 + math.sin(a) * (0.2 - 0.012 * k), 0.016 + 0.003 * k)))
    tube('rope', pts, 0.014, seg=6, col=ROPE_C, cfn=rope_twist_cfn(ROPE_C, 0.04), caps=True)
    pts = [Vector((0.6, 0.3, 0.0)), Vector((0.45, 0.2, 0.02)), Vector((0.35, 0.05, 0.02))]
    # net draped over the left side of the basket and on the ground
    rr = random.Random(9)
    ncol = H('#8f7e5e')
    nx, ny = 11, 8
    x0, x1, y0, y1 = -0.95, -0.25, -0.1, 0.55

    def nz(x, y):
        # drape: lumpy sheet that climbs the basket side
        d = math.hypot(x - 0.0, y - 0.0)
        z = 0.03 + 0.03 * math.sin(x * 11 + y * 7)
        if d < 0.5:
            z = max(z, 0.36 * (1 - (d - 0.3) / 0.2) if d > 0.3 else 0.36)
        return z
    for i in range(nx + 1):
        pts = [Vector((x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny, 0.0)) for j in range(ny + 1)]
        pts = [Vector((p.x, p.y, nz(p.x, p.y))) for p in pts]
        tube('rope', pts, 0.003, seg=4, col=ncol, caps=False) if False else ribbon_line(pts, ncol)
    for j in range(ny + 1):
        pts = [Vector((x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny, 0.0)) for i in range(nx + 1)]
        pts = [Vector((p.x, p.y, nz(p.x, p.y))) for p in pts]
        ribbon_line(pts, ncol)
    # floats (cork) on net edge
    for i in range(0, nx + 1, 3):
        x = x0 + (x1 - x0) * i / nx
        sphere('plain', (x, y0, nz(x, y0) + 0.01), 0.018, seg=6, rings=4, sq=(1, 1.4, 0.9), col=H('#b99a62'))
    collider(-0.35, 0.35, -0.35, 0.35, 0.4, 0.0)


def ribbon_line(pts, col):
    for a, b in zip(pts[:-1], pts[1:]):
        ribbon('rope', a, b, 0.007, 0.007, col=col, up=(0, 0, 1))
