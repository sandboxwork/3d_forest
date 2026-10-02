"""Village props batch 1: well_stone, barrel_a, barrel_stack, bucket..."""
from vp_parts import *


def stone_ring(r_in, r_out, z0, courses, hc, n0, seed, mat='stone', ca=H('#8d877c'), cb=H('#b0a58e'), moss=0.5, cap=True):
    """courses of rubble stones forming a ring wall"""
    rr = random.Random(seed)
    cf = stone_cfn(ca, cb, 4.0, seed, moss=moss)
    for c in range(courses):
        n = n0 + (c % 2)
        z = z0 + c * hc + hc / 2
        off = rr.uniform(0, TAU)
        for i in range(n):
            a = off + TAU * (i + rr.uniform(-0.08, 0.08)) / n
            rm = (r_in + r_out) / 2 + rr.uniform(-0.02, 0.02)
            tw = TAU * rm / n * rr.uniform(0.95, 1.12)
            c_ = (math.cos(a) * rm, math.sin(a) * rm, z + rr.uniform(-0.01, 0.01))
            rock(mat, c_, (r_out - r_in + rr.uniform(0, 0.05), tw, hc * rr.uniform(0.95, 1.1)), seed=seed * 100 + c * 31 + i,
                 rot=(0, 0, a), cfn=cf, cuts=1, round_=0.35, jitter=0.1)
    if cap:
        zc = z0 + courses * hc
        n = n0 + 1
        off = rr.uniform(0, TAU)
        for i in range(n):
            a = off + TAU * i / n
            rm = (r_in + r_out) / 2
            tw = TAU * rm / n * 1.08
            rock(mat, (math.cos(a) * rm, math.sin(a) * rm, zc + 0.04), (r_out - r_in + 0.09, tw, 0.11), seed=seed * 7 + i,
                 rot=(0, 0, a), cfn=cf, cuts=1, round_=0.18, jitter=0.07)


@prop('well_stone', '돌 우물', ao_len=0.25, cam=lambda m: [((4.2, -5.0, 2.6), (0, 0, 1.6), 38), ((-4.4, 4.0, 3.0), (0, 0, 1.6), 38),
                                                ((0.0, -2.4, 1.7), (0, 0, 1.5), 45), ((1.4, -1.6, 3.2), (0, 0.0, 1.3), 45)])
def well_stone():
    RIN, ROUT = 0.62, 0.92
    HW = 0.95
    stone_ring(RIN, ROUT, 0.0, 3, 0.30, 12, 3)
    # dark depth disc + inner shaft wall hint
    lathe('soil', (0, 0, 0), [(RIN + 0.02, HW - 0.5), (0.0, HW - 0.5)], seg=24, cap=False, col=(0.05, 0.05, 0.05))
    lathe('water', (0, 0, 0), [(RIN, HW - 0.38), (0.0, HW - 0.38)], seg=24, cap=False, col=(0.15, 0.22, 0.25))
    # posts
    wcol = GREY_W
    for sx in (-1, 1):
        x = sx * 0.78
        for sy in (0,):
            beam('oak', (x, 0, HW + 0.02), (x, 0, 2.72), 0.13, 0.13, bev=0.008, col=wcol, cfn=wood_cfn(wcol, 0.15, 6, 4 + sx, grime_z=0.0))
            # iron strap near the axle
            box('iron_dark', (x + sx * 0.067, 0, 2.0), (0.012, 0.16, 0.12), bev=0.002, col=IRON_C)
            # braces
            beam('oak', (x, -0.0, 1.05), (x * 0.0 + sx * 0.0, 0, 1.05), 0.0001, 0.0001) if False else None
    # axle (windlass)
    f_ax = FM(Matrix.Translation((0, 0, 2.0)))
    f_ax.cyl('oak', (0, 0, 0), 0.065, 1.7, axis='x', seg=14, col=OAK_D, bev=0.01)
    # crank on +x side
    f_ax.box('iron_dark', (0.97, 0, -0.06), (0.025, 0.04, 0.2), col=IRON_C, bev=0.004, M=None) if False else None
    beam('iron_dark', (0.95, 0, 2.0), (0.95, 0, 1.8), 0.035, 0.022, bev=0.004, col=IRON_C, up=(1, 0, 0))
    beam('iron_dark', (0.95, 0, 1.8), (1.12, 0, 1.8), 0.03, 0.025, bev=0.004, col=IRON_C, up=(0, 1, 0))
    cyl('oak', (1.17, 0, 1.8), 0.025, 0.14, axis='x', seg=10, col=OAK_D, bev=0.004)
    # rope winding on axle
    rope_helix(Matrix.Translation((0, 0, 2.0)), 0.078, -0.25, 0.2, 5.5, r=0.011)
    # rope from axle down to the bucket pivot
    bz = 1.62
    rope_line([(0.0, -0.08, 2.0 - 0.08), (0.0, -0.09, 1.85), (0.0, -0.04, 1.72), (0.0, 0.0, bz)], r=0.011)
    # roof: gable along x, ridge at z=2.95
    zE, zR = 2.7, 3.22
    XL = 1.18
    YE = 0.95
    # roof boards under shingles (two slopes)
    for sy in (-1, 1):
        A = (-XL, sy * YE, zE); B = (XL, sy * YE, zE); C = (XL, sy * 0.02, zR); D = (-XL, sy * 0.02, zR)
        # underlying plank deck
        Av, Bv, Cv, Dv = [Vector(v) for v in (A, B, C, D)]
        ang = math.atan2(zR - zE, YE)
        mid = (Av + Bv + Cv + Dv) / 4
        Mx = Matrix.Translation(mid) @ Matrix.Rotation(-sy * ang * -1 if sy > 0 else ang, 4, 'X') if False else None
        slope_len = math.hypot(YE, zR - zE)
        rx = math.atan2(zR - zE, YE)
        Mdeck = Matrix.Translation(mid + Vector((0, 0, -0.025))) @ Matrix.Rotation(-sy * rx, 4, 'X')
        box('dark', None, (2 * XL + 0.06, slope_len + 0.08, 0.04), M=Mdeck, bev=0.004, col=H('#6a5239'), g=0, skip_down=False)
        # shingles
        shingle_panel('oak', A, B, C, D, rows=8, per_row=9, w=0.29, lth=0.3, thick=0.014, col=H('#7c6446'), seed=7 + sy, tilt=0.18)
    # ridge cap boards
    beam('oak', (-XL - 0.04, 0, zR + 0.015), (XL + 0.04, 0, zR + 0.015), 0.16, 0.035, bev=0.006, col=H('#6a5239'))
    # gable end trims (barge boards)
    for sx in (-1, 1):
        for sy in (-1, 1):
            beam('oak', (sx * (XL + 0.04), sy * (YE + 0.04), zE - 0.04), (sx * (XL + 0.04), sy * 0.0, zR + 0.02), 0.05, 0.03, bev=0.004, col=H('#8b7352'), up=(1, 0, 0))
    # diagonal braces post -> tie beam
    for sx in (-1, 1):
        beam('oak', (sx * 0.78, 0, 2.15), (sx * 0.78 - sx * 0.0, 0, 2.15), 0.01, 0.01) if False else None
        for sy in (-1, 1):
            beam('oak', (sx * 0.78, 0, 2.05), (sx * 0.78, sy * 0.42, 2.66), 0.07, 0.07, bev=0.006, col=wcol)
    # tie beam + king post (visible under roof)
    beam('oak', (-XL + 0.1, 0, 2.68), (XL - 0.1, 0, 2.68), 0.1, 0.09, bev=0.006, col=wcol)
    for sy in (-1, 1):
        beam('oak', (-0.78, 0, 2.66), (-0.78, sy * 0.5, 2.66), 0.08, 0.08, bev=0.006, col=wcol)
        beam('oak', (0.78, 0, 2.66), (0.78, sy * 0.5, 2.66), 0.08, 0.08, bev=0.006, col=wcol)
    # stone ring base footing (flagstones around)
    rr = random.Random(2)
    cf = stone_cfn(H('#7d776d'), H('#a29780'), 3.0, 8, moss=0.7)
    for i in range(13):
        a = TAU * i / 13 + 0.1
        rm = ROUT + 0.28
        rock('stone', (math.cos(a) * rm, math.sin(a) * rm, 0.025), (0.42, 0.40, 0.07), seed=300 + i, rot=(0, 0, a + rr.uniform(-.2, .2)), cfn=cf, cuts=1, round_=0.25)
    # colliders: ring + posts approximated by one cylinder-ish box
    collider(-ROUT, ROUT, -ROUT, ROUT, 3.22, 0.0)

    # bucket sub part (pivot at the bail top)
    def bucket_geo():
        bucket(Matrix.Translation((0, 0, bz - 0.42)), r_top=0.17, r_bot=0.135, h=0.28, N=10, col=OAK_W, water=False)
    sub('well_bucket', (0, 0, bz), bucket_geo)


@prop('barrel_a', '나무 통')
def barrel_a():
    barrel(Matrix.Translation((0, 0, 0)), r_mid=0.30, r_end=0.25, h=0.9, N=10, open_top=False, hoops=4, col=OAK_W, seed=2)
    collider(-0.3, 0.3, -0.3, 0.3, 0.9, 0.0)


# ----------------------------------------------------------------------------------------------------- barrel stack
@prop('barrel_stack', '쌓은 통', cam=lambda m: [((2.6, -3.0, 1.9), (0, 0, 0.7), 40), ((-2.8, 2.6, 2.0), (0, 0, 0.7), 40), ((1.0, -2.0, 1.2), (0, -0.2, 0.9), 45), ((0.2, -1.4, 2.6), (0, 0, 0.4), 45)])
def barrel_stack():
    def lying(c, ax=0.0, seed=0, h=0.9, col=OAK_W):
        M0 = Matrix.Translation(c) @ Matrix.Rotation(math.radians(ax), 4, 'Z') @ Matrix.Rotation(math.radians(90), 4, 'Y') @ Matrix.Translation((0, 0, -h / 2))
        barrel(M0, r_mid=0.30, r_end=0.25, h=h, N=10, hoops=4, col=col, seed=seed)
    # three lying barrels: pyramid (axes along X, in -Y/+Y rows)
    lying((0.0, 0.32, 0.30), 0, 1, col=OAK_W)
    lying((0.0, -0.32, 0.30), 0, 2, col=H('#8d6f4d'))
    lying((0.0, 0.0, 0.30 + 0.52), 0, 3, col=H('#a98860'))
    for sx in (-1, 1):
        box('oak', (sx * 0.30, 0, 0.05), (0.07, 1.3, 0.1), bev=0.006, col=DARK_W, g=1)
        for sy in (-1, 1):
            rock('oak', (sx * 0.30, sy * 0.58, 0.10), (0.1, 0.1, 0.1), seed=sx + sy, col=DARK_W, cuts=0)
    # two standing barrels, one open with apples
    M1 = Matrix.Translation((1.05, -0.2, 0))
    barrel(M1, r_mid=0.30, r_end=0.25, h=0.9, N=10, hoops=4, col=H('#9a7a55'), seed=5, open_top=True)
    cf = lambda p: mixc(H('#b8392b'), H('#d8c040'), (fbm(p.x, p.y, p.z, 12, 3) * 0.5 + 0.5) ** 2)
    rr = random.Random(4)
    for i in range(9):
        a = rr.uniform(0, TAU); d = rr.uniform(0, 0.17)
        sphere('food', (1.05 + math.cos(a) * d, -0.2 + math.sin(a) * d, 0.9 - 0.11 + rr.uniform(0, 0.03)), 0.045, seg=6, rings=4, col=jitter_col(H('#b8392b'), 0.2, rr) if i % 3 else H('#c9b23c'))
    barrel(Matrix.Translation((0.78, 0.55, 0)), r_mid=0.30, r_end=0.25, h=0.9, N=10, hoops=3, col=H('#7f6445'), seed=9, hoop_col=H('#6a4a30'), hoop_mat='dark')
    collider(-0.9, 1.4, -0.7, 0.9, 1.1, 0.0)


# ----------------------------------------------------------------------------------------------------- crates
def crate(M0, sx=0.6, sy=0.4, sz=0.4, col=PINE_W, seed=0, open_top=True, slats=3):
    f = FM(M0)
    r = random.Random(seed)
    p = 0.035
    for ix in (-1, 1):
        for iy in (-1, 1):
            f.box('pine', (ix * (sx / 2 - p / 2), iy * (sy / 2 - p / 2), sz / 2), (p, p, sz), bev=0.004, col=jitter_col(col, 0.12, r), cfn=None, g=2, skip_down=False)
    sh = (sz - 0.04) / slats
    for k in range(slats):
        z = 0.02 + sh * (k + 0.5)
        c = jitter_col(col, 0.14, r)
        # long sides
        for iy in (-1, 1):
            f.box('pine', (0, iy * (sy / 2 - 0.009), z), (sx - 0.01, 0.018, sh - 0.012), bev=0.0, col=c, g=0, skip_down=False)
        for ix in (-1, 1):
            f.box('pine', (ix * (sx / 2 - 0.009), 0, z), (0.018, sy - 0.07, sh - 0.012), bev=0.0, col=jitter_col(col, 0.14, r), g=1, skip_down=False)
    for k in range(3):
        f.box('pine', (0, -sy / 2 + sy * (k + 0.5) / 3, 0.012), (sx - 0.04, sy / 3 - 0.01, 0.02), bev=0.0, col=jitter_col(col, 0.14, r), g=0, skip_down=False)
    if not open_top:
        for k in range(3):
            f.box('pine', (0, -sy / 2 + sy * (k + 0.5) / 3, sz + 0.01), (sx, sy / 3 - 0.008, 0.02), bev=0.0, col=jitter_col(col, 0.14, r), g=0, skip_down=False)


def cabbage(c, R, seed=0):
    rr = random.Random(seed)
    prof = []
    for k in range(9):
        a = -math.pi / 2 + math.pi * k / 8 * 0.97
        prof.append((max(math.cos(a) * R, 0.0), math.sin(a) * R * 0.9))
    bm = lathe_bm(prof, 16, 2.0, False)
    for v in bm.verts:
        a = math.atan2(v.co.y, v.co.x)
        k = 1 + 0.07 * math.sin(a * 6 + v.co.z * 30 + seed) + 0.04 * math.sin(a * 3 - v.co.z * 20)
        v.co.x *= k; v.co.y *= k
    base = H('#7da64e')
    put_bm('food', bm, c=c, cfn=lambda p, c=c, R=R: mixc(H('#a8cc78'), shade(base, 0.8), min(1.0, max(0.0, (p - Vector(c)).length / R * 0.9 + 0.12 * fbm(p.x, p.y, p.z, 30, 1, 2)))))


def sack(c, r=0.22, h=0.5, seed=0, col=H('#b59a68'), rot=0.0, slump=0.12):
    rr = random.Random(seed)
    prof = [(0.0, 0.0), (r * 0.7, 0.0), (r * 0.98, h * 0.08), (r * 1.05, h * 0.3), (r * 0.98, h * 0.55), (r * 0.7, h * 0.78), (r * 0.32, h * 0.92), (r * 0.17, h * 0.95), (r * 0.22, h * 1.0), (r * 0.38, h * 1.06), (r * 0.3, h * 1.1)]
    bm = lathe_bm(prof, 18, 2.5, True)
    for v in bm.verts:
        a = math.atan2(v.co.y, v.co.x)
        k = 1 + 0.05 * math.sin(a * 3 + seed) + 0.04 * math.sin(a * 5 + v.co.z * 9)
        v.co.x *= k; v.co.y *= k * (1 + slump * (1 - v.co.z / h))
    put_bm('burlap', bm, c=c, rot=(0, 0, rot), cfn=lambda p, cl=col: jitter_col(cl, 0.0) if False else mixc(cl, shade(cl, 0.7), (fbm(p.x, p.y, p.z, 14, seed, 2) * 0.5 + 0.5)), skip_down=True)
    # tie
    cyl('rope', (c[0], c[1], c[2] + h * 0.93), r * 0.2, 0.025, seg=8, col=ROPE_C)


@prop('crate_stack', '나무 상자 더미', ao_len=0.3, cam=lambda m: [((2.4, -2.6, 1.6), (0, 0, 0.5), 40), ((-2.5, 2.3, 1.7), (0, 0, 0.5), 40), ((0.6, -1.5, 1.0), (0, 0, 0.5), 45), ((0.5, -1.2, 1.9), (-0.2, 0, 0.5), 50)])
def crate_stack():
    r = random.Random(3)
    cols = [PINE_W, H('#a68b64'), H('#b8a07a'), H('#8f7b5c')]
    # bottom row
    crate(Matrix.Translation((-0.35, -0.05, 0.0)), 0.7, 0.5, 0.42, cols[0], 1, open_top=False)
    crate(Matrix.Translation((0.40, -0.02, 0.0)) @ Matrix.Rotation(0.08, 4, 'Z'), 0.7, 0.5, 0.42, cols[1], 2, open_top=True)
    crate(Matrix.Translation((-0.25, 0.0, 0.42)) @ Matrix.Rotation(-0.06, 4, 'Z'), 0.6, 0.45, 0.36, cols[2], 3, open_top=False)
    crate(Matrix.Translation((0.55, 0.0, 0.42)) @ Matrix.Rotation(0.2, 4, 'Z'), 0.5, 0.4, 0.3, cols[3], 4, open_top=True)
    crate(Matrix.Translation((-0.2, 0.02, 0.78)) @ Matrix.Rotation(0.1, 4, 'Z'), 0.5, 0.38, 0.3, cols[0], 5, open_top=False)
    crate(Matrix.Translation((-1.05, 0.2, 0.0)) @ Matrix.Rotation(0.3, 4, 'Z'), 0.55, 0.4, 0.34, cols[2], 6, open_top=True)
    # cabbages in the open crate at right (top at z=0.42)
    for i, (x, y) in enumerate([(0.30, -0.08), (0.52, 0.04), (0.38, 0.1), (0.5, -0.12)]):
        cabbage((x + 0.02, y, 0.42 - 0.08 + 0.14), 0.12, i)
    # apples in the crate on top
    for i in range(9):
        a = r.uniform(0, TAU); d = r.uniform(0, 0.12)
        sphere('food', (0.55 + math.cos(a) * d * 1.3, 0.0 + math.sin(a) * d, 0.42 + 0.17), 0.035, seg=8, rings=6, col=jitter_col(H('#a8321f'), 0.2, r))
    # in front crate, potatoes
    for i in range(14):
        a = r.uniform(0, TAU); d = r.uniform(0, 0.17)
        sphere('food', (-1.05 + math.cos(a) * d * 1.1 + 0.02, 0.2 + math.sin(a) * d * 0.8, 0.26), 0.04, seg=7, rings=5, sq=(1.2, 1, 0.8), col=jitter_col(H('#a58a5a'), 0.15, r))
    # sacks
    sack((1.25, -0.1, 0.0), 0.26, 0.62, 1, H('#c4ae80'), 0.3)
    sack((1.2, 0.45, 0.0), 0.22, 0.5, 2, H('#bba478'), -0.4)
    sack((-1.6, -0.35, 0.0), 0.24, 0.55, 3, H('#c8b283'), 0.9)
    collider(-1.4, 1.5, -0.45, 0.65, 1.1, 0.0)


# ----------------------------------------------------------------------------------------------------- firewood
def log_bm(L, rad, seed, ends=True, seg=7):
    rr = random.Random(seed)
    prof = [(0.0, -L / 2), (rad * 0.6, -L / 2), (rad, -L / 2 + 0.005), (rad, L / 2 - 0.005), (rad * 0.6, L / 2), (0.0, L / 2)]
    bm = lathe_bm(prof, seg, 1.0, False)
    for v in bm.verts:
        v.co.x *= 1 + rr.uniform(-0.04, 0.04); v.co.y *= 1 + rr.uniform(-0.04, 0.04)
    return bm


@prop('woodpile_stack', '장작더미', cam=lambda m: [((2.4, -2.7, 1.6), (0, 0, 0.6), 40), ((-2.4, 2.4, 1.6), (0, 0, 0.6), 40), ((0.5, -1.8, 0.9), (0, 0, 0.6), 45), ((-0.5, 0.0, 1.6), (0, 0, 0.0), 40)])
def woodpile_stack():
    r = random.Random(11)
    W, rows = 1.7, 7
    L = 0.55
    base_c = [H('#b89870'), H('#a88a62'), H('#c2a47a'), H('#96774f'), H('#8c6e4a')]
    # bottom pallets/rails
    for sx in (-1, 1):
        beam('oak', (sx * 0.35 + 0.0, -0.45, 0.05), (sx * 0.35, 0.45, 0.05), 0.1, 0.1, bev=0.006, col=DARK_W)
    for i, x in enumerate((-W / 2 - 0.06, W / 2 + 0.06)):
        beam('oak', (x, -0.27, 0.0), (x, -0.27, 1.25), 0.09, 0.09, bev=0.006, col=GREY_W, cfn=wood_cfn(GREY_W, 0.15, 6, 20 + i))
        beam('oak', (x, 0.27, 0.0), (x, 0.27, 1.25), 0.09, 0.09, bev=0.006, col=GREY_W, cfn=wood_cfn(GREY_W, 0.15, 6, 30 + i))
    z = 0.13
    for row in range(rows):
        rad_a = 0.07
        n = int((W - 0.0) / (rad_a * 2 * 0.97))
        x = -W / 2 + (rad_a if row % 2 == 0 else rad_a * 2)
        while x < W / 2 - rad_a * 0.8:
            rad = rad_a * r.uniform(0.78, 1.08)
            col = jitter_col(r.choice(base_c), 0.1, r)
            lg = log_bm(L * r.uniform(0.95, 1.05), rad, r.randint(0, 999))
            c = (x + r.uniform(-0.01, 0.01), r.uniform(-0.02, 0.02), z + rad * 0.95)
            put_bm('oak', lg, M=Matrix.Translation(c) @ Matrix.Rotation(math.radians(90), 4, 'X') @ Matrix.Rotation(r.uniform(0, TAU), 4, 'Z'),
                   cfn=None, col=col, g=2, skip_down=False)
            x += rad * 2 * 0.98
        z += rad_a * 1.78
    # extra: end grain colour handled by vertex colour jitter. a few split logs and chips on the ground, axe
    for i in range(8):
        rad = 0.045 * r.uniform(0.8, 1.2)
        lg = log_bm(0.5, rad, i + 100)
        put_bm('oak', lg, M=Matrix.Translation((r.uniform(-1.3, 1.3), r.uniform(-0.9, -0.5), rad)) @ Matrix.Rotation(math.radians(90), 4, 'X') @ Matrix.Rotation(r.uniform(0, TAU), 4, 'Z') @ Matrix.Rotation(r.uniform(-1, 1), 4, 'X'), col=jitter_col(base_c[0], 0.1, r), skip_down=False) if False else None
    # chopping block with axe in front
    cyl('oak', (1.45, -0.75, 0.2), 0.22, 0.4, seg=14, col=H('#8a6c48'), bev=0.01)
    beam('oak', (1.45, -0.75, 0.40), (1.60, -0.80, 0.78), 0.035, 0.03, bev=0.004, col=H('#8a6a44'), up=(0, 0, 1)) if False else None
    beam('oak', (1.40, -0.76, 0.41), (1.62, -0.80, 0.92), 0.03, 0.028, bev=0.004, col=H('#7e5f3a'), up=(0, 1, 0))
    box('iron_dark', (1.35, -0.76, 0.46), (0.13, 0.025, 0.13), M=Matrix.Translation((1.35, -0.76, 0.455)) @ Matrix.Rotation(0.2, 4, 'Z'), col=IRON_C, bev=0.004)
    collider(-1.0, 1.0, -0.4, 0.4, 1.25, 0.0)


# ----------------------------------------------------------------------------------------------------- hay
STRAW_COLS = [H('#d8b968'), H('#c9a655'), H('#e3c97d'), H('#b8934a'), H('#d1b162')]


def hay_cfn(seed=0, streak=18.0):
    def f(p):
        a = math.atan2(p.y, p.x)
        t = fbm(math.cos(a) * 2.5, math.sin(a) * 2.5, p.z * 0.6, streak, seed, 2) * 0.5 + 0.5
        t2 = fbm(p.x, p.y, p.z, 7, seed + 1, 3) * 0.5 + 0.5
        c = mixc(H('#b38e48'), H('#e0c277'), t * 0.6 + t2 * 0.5)
        return c
    return f


def straw_whisks(cfn_center, n, surf_fn, L=(0.22, 0.42), w=0.014, seed=0, down=0.55, col_fn=None):
    """scatter ribbon strands; surf_fn(rng) -> (point, outward normal)"""
    rr = random.Random(seed)
    for i in range(n):
        p, nrm = surf_fn(rr)
        d = (nrm + Vector((rr.uniform(-.5, .5), rr.uniform(-.5, .5), -down * rr.uniform(0.4, 1.2)))).normalized()
        ln = rr.uniform(*L)
        q = Vector(p) + d * ln
        col = col_fn(p, rr) if col_fn else jitter_col(rr.choice(STRAW_COLS), 0.1, rr)
        ribbon('straw', Vector(p) - d * 0.03, q, w, w * 0.25, col=col, bend=(rr.uniform(-.05, .05), rr.uniform(-.05, .05), -0.04), nseg=2, up=(0, 0, 1))


def straw_cover(sampler, n, L=(0.3, 0.5), w=(0.035, 0.06), lift=0.012, seed=0, jit=0.5, dark_fn=None, tip=0.03, cols=None):
    """lay overlapping flat strands (shingle-like) over a surface. sampler(rr)->(point, outward normal)"""
    rr = random.Random(seed)
    cols = cols or STRAW_COLS
    for i in range(n):
        p, nrm = sampler(rr)
        nrm = Vector(nrm).normalized()
        g = Vector((0, 0, -1))
        t = g - nrm * g.dot(nrm)
        if t.length < 0.15:
            t = Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), 0)); t = t - nrm * t.dot(nrm)
        t.normalize()
        side = nrm.cross(t)
        d = (t + side * rr.uniform(-jit, jit)).normalized()
        ln = rr.uniform(*L)
        p0 = Vector(p) + nrm * lift * rr.uniform(0.5, 1.5)
        p1 = p0 + d * ln + nrm * tip * rr.uniform(0.3, 1.2)
        wd = rr.uniform(*w)
        c = jitter_col(rr.choice(cols), 0.1, rr)
        if dark_fn:
            c = mixc(c, dark_fn(p)[0], dark_fn(p)[1])
        ribbon('straw', p0, p1, wd, wd * 0.5, col=c, nseg=1, up=nrm)


@prop('hay_stack', '건초더미', ao_len=0.5, cam=lambda m: [((5.0, -5.5, 3.0), (0, 0, 1.2), 38), ((-5.0, 4.8, 3.2), (0, 0, 1.2), 38), ((2.2, -2.9, 1.6), (0, 0, 1.4), 45), ((0.0, -3.2, 3.8), (0, 0, 2.0), 40)])
def hay_stack():
    R0, Ht = 1.45, 3.0
    prof = [(0.0, 0.0)]
    # rounded cone: wide skirt, belly, then steep cone to the top
    pts = [(1.40, 0.0), (1.52, 0.18), (1.50, 0.55), (1.34, 1.0), (1.08, 1.5), (0.78, 2.0), (0.46, 2.45), (0.22, 2.8), (0.08, 3.05), (0.0, 3.12)]
    pts_i = interp_path([Vector((r, z, 0)) for r, z in pts], 3)
    prof = [(p.x, p.y) for p in pts_i]
    bm = lathe_bm([(0.0, 0.0)] + prof, 32, 1.0, False)
    for v in bm.verts:
        a = math.atan2(v.co.y, v.co.x)
        k = 1 + 0.045 * math.sin(a * 3 + 1.3) + 0.03 * math.sin(a * 7 + v.co.z * 2.5) + 0.02 * math.sin(a * 13 - v.co.z * 4)
        v.co.x *= k; v.co.y *= k
    bm = disp(bm, strength=0.07, scale=0.55, depth=2, seed_loc=(2, 3, 1))
    bm = disp(bm, strength=0.025, scale=0.16, depth=1, seed_loc=(5, 1, 2))
    put_bm('straw', bm, cfn=lambda p: shade(hay_cfn(2, 14)(p), 0.62), skip_down=True)

    def surf(rr):
        k = rr.uniform(0.02, 0.97) ** 0.9
        i = int(k * (len(prof) - 1))
        r, z = prof[i]
        a = rr.uniform(0, TAU)
        p = Vector((math.cos(a) * r, math.sin(a) * r, z))
        r2, z2 = prof[min(i + 1, len(prof) - 1)]
        r1, z1 = prof[max(i - 1, 0)]
        sl = Vector((r2 - r1, z2 - z1)).normalized()
        nrm2 = Vector((sl.y, -sl.x))
        return p, Vector((math.cos(a) * nrm2.x, math.sin(a) * nrm2.x, nrm2.y))
    dk = lambda p: (H('#8d7238'), max(0.0, 0.5 - p.z * 0.9))
    straw_cover(surf, 1500, L=(0.35, 0.6), w=(0.03, 0.055), lift=0.02, seed=3, jit=0.35, dark_fn=dk, tip=0.04)
    straw_whisks(None, 120, surf, L=(0.15, 0.3), w=0.012, seed=4, down=0.6)
    # top tuft + tie
    for i in range(40):
        a = TAU * i / 40 + random.random() * 0.2
        p = Vector((math.cos(a) * 0.05, math.sin(a) * 0.05, 3.0))
        q = p + Vector((math.cos(a) * 0.20, math.sin(a) * 0.20, 0.22 + random.random() * 0.2))
        ribbon('straw', p, q, 0.016, 0.004, col=jitter_col(random.choice(STRAW_COLS), 0.1), bend=(math.cos(a) * 0.05, math.sin(a) * 0.05, -0.1), nseg=2)
    tube('rope', [Vector((math.cos(a) * 0.075, math.sin(a) * 0.075, 3.03 + a * 0.004)) for a in [i * 0.5 for i in range(0, 14)]], 0.012, seg=6, col=ROPE_C)
    # bottom rope net hint and bits of hay on ground
    collider(-1.5, 1.5, -1.5, 1.5, 3.1, 0.0)


@prop('hay_bale', '건초 곤포', ao_len=0.4, cam=lambda m: [((1.9, -2.2, 1.3), (0, 0, 0.25), 40), ((-1.8, 1.8, 1.2), (0, 0, 0.25), 40), ((0.6, -1.0, 0.7), (0, 0, 0.25), 45), ((0.0, -0.9, 1.2), (0, 0, 0.2), 45)])
def hay_bale():
    r = random.Random(5)
    L, W, Hh = 0.9, 0.46, 0.36
    n = 7
    flake = lambda p: mixc(shade(hay_cfn(1, 40)(p), 0.55), shade(hay_cfn(1, 40)(p), 0.3), max(0.0, 1 - abs(((p.z / Hh * n) % 1.0) - 0.5) * 2 - 0.0) ** 6 * 0.0 + 0.35 * max(0.0, abs(((p.z / Hh * n) % 1.0) - 0.5) * 2 - 0.75) * 4)
    box('straw', (0, 0, Hh / 2), (L, W, Hh), bev=0.02, cuts=3, cfn=flake, g=0, skip_down=False, seg=2)

    def laid(face, nn, Lr, wr, seed):
        def sm(rr):
            if face == 'top':
                return Vector((rr.uniform(-L / 2 + 0.02, L / 2 - 0.02), rr.uniform(-W / 2 + 0.01, W / 2 - 0.01), Hh)), Vector((0, 0, 1))
            if face == 'front':
                return Vector((rr.uniform(-L / 2 + 0.02, L / 2 - 0.02), -W / 2, rr.uniform(0.02, Hh - 0.01))), Vector((0, -1, 0))
            return Vector((rr.uniform(-L / 2 + 0.02, L / 2 - 0.02), W / 2, rr.uniform(0.02, Hh - 0.01))), Vector((0, 1, 0))
        rr = random.Random(seed)
        for i in range(nn):
            p, nrm = sm(rr)
            ln = rr.uniform(*Lr)
            sgn = 1 if rr.random() < 0.5 else -1
            ln = min(ln, max(0.05, (L / 2 + 0.02 - p.x * sgn)))
            d = Vector((sgn, rr.uniform(-0.05, 0.05), rr.uniform(-0.03, 0.03))).normalized()
            if face != 'top':
                d.z = rr.uniform(-0.04, 0.04)
            side = nrm.cross(d).normalized()
            p0 = Vector(p) + nrm * rr.uniform(0.003, 0.012)
            ribbon('straw', p0, p0 + d * ln + nrm * 0.006, rr.uniform(*wr), rr.uniform(*wr) * 0.7, col=jitter_col(rr.choice(STRAW_COLS), 0.1, rr), nseg=1, up=nrm)
    laid('top', 330, (0.2, 0.45), (0.012, 0.02), 1)
    laid('front', 240, (0.2, 0.45), (0.012, 0.02), 2)
    laid('back', 240, (0.2, 0.45), (0.012, 0.02), 3)
    # cut straw ends on both ends: short stubs
    rr = random.Random(9)
    for sx in (-1, 1):
        for i in range(70):
            p = Vector((sx * L / 2, rr.uniform(-W / 2 + 0.02, W / 2 - 0.02), rr.uniform(0.02, Hh - 0.02)))
            q = p + Vector((sx * rr.uniform(0.01, 0.045), rr.uniform(-0.02, 0.02), rr.uniform(-0.02, 0.02)))
            ribbon('straw', p, q, 0.012, 0.006, col=jitter_col(rr.choice(STRAW_COLS), 0.12, rr), nseg=1, up=(1, 0, 0) if False else (0, 0, 1))
    # twine bands
    for x in (-0.24, 0.24):
        pts = []
        for (y, z) in [(-W / 2 - 0.012, 0.0), (-W / 2 - 0.014, Hh), (W / 2 + 0.014, Hh), (W / 2 + 0.012, 0.0)]:
            pts.append(Vector((x, y, z)))
        path = [Vector((x, -W / 2 - 0.014, 0.0)), Vector((x, -W / 2 - 0.016, Hh / 2)), Vector((x, -W / 2 - 0.016, Hh)), Vector((x, 0, Hh + 0.012)), Vector((x, W / 2 + 0.016, Hh)), Vector((x, W / 2 + 0.016, Hh / 2)), Vector((x, W / 2 + 0.014, 0.0)), Vector((x, 0, -0.005))]
        tube('rope', polyline_smooth(path + [path[0]], 4), 0.005, seg=5, col=H('#b57f3b'))
    # loose strands around
    def surf(rr):
        s = rr.choice(['top', 'front', 'back', 'left', 'right'])
        if s == 'top':
            return Vector((rr.uniform(-L / 2, L / 2), rr.uniform(-W / 2, W / 2), Hh)), Vector((0, 0, 1))
        if s == 'front':
            return Vector((rr.uniform(-L / 2, L / 2), -W / 2, rr.uniform(0.02, Hh))), Vector((0, -1, 0))
        if s == 'back':
            return Vector((rr.uniform(-L / 2, L / 2), W / 2, rr.uniform(0.02, Hh))), Vector((0, 1, 0))
        if s == 'left':
            return Vector((L / 2, rr.uniform(-W / 2, W / 2), rr.uniform(0.02, Hh))), Vector((1, 0, 0))
        return Vector((-L / 2, rr.uniform(-W / 2, W / 2), rr.uniform(0.02, Hh))), Vector((-1, 0, 0))
    straw_whisks(None, 70, surf, L=(0.06, 0.16), w=0.01, seed=7, down=0.3)
    collider(-0.46, 0.46, -0.24, 0.24, 0.37, 0.0)


# ----------------------------------------------------------------------------------------------------- hay cart
def pitchfork(base, tip_dir, L=1.5, col=OAK_W):
    base = Vector(base); d = Vector(tip_dir).normalized()
    top = base + d * L
    tube('oak', [base, base + d * L * 0.5, top], 0.017, seg=7, col=col)
    # head
    side = d.cross(Vector((0, 1, 0)))
    if side.length < 0.1:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize()
    beam('iron_dark', top - side * 0.1, top + side * 0.1, 0.014, 0.014, bev=0.002, col=IRON_C, up=d)
    for k in (-1, 0, 1):
        s = top + side * (0.1 * k)
        tube('iron_dark', [s, s + d * 0.12, s + d * 0.28 + side * (0.01 * k)], [0.0085, 0.0075, 0.0035], seg=5, col=IRON_C)


@prop('hay_cart', '건초 수레', kind='animated', ao_len=0.3, cam=lambda m: [((4.2, -4.8, 2.6), (0, -0.5, 0.9), 38), ((-4.5, 3.6, 2.6), (0, 0, 0.9), 38), ((2.2, -0.2, 0.9), (0, 0.15, 0.55), 40), ((0.8, -3.6, 1.6), (0, -1.5, 0.7), 40)])
def hay_cart():
    r = random.Random(8)
    AY, AZ = 0.15, 0.55
    wcol = H('#8b7b66')
    # axle
    beam('oak', (-1.02, AY, AZ), (1.02, AY, AZ), 0.1, 0.1, bev=0.01, col=DARK_W)
    for sx in (-1, 1):
        cyl('iron_dark', (sx * 1.065, AY, AZ), 0.034, 0.05, axis='x', seg=10, col=IRON_C)
    # bed frame
    for sx in (-1, 1):
        beam('oak', (sx * 0.72, -1.05, 0.80), (sx * 0.72, 1.45, 0.80), 0.09, 0.1, bev=0.008, col=wcol, cfn=wood_cfn(wcol, 0.15, 5, 40 + sx, axis=1, grime_z=0.0))
        box('iron_dark', (sx * 0.72, AY, 0.745), (0.115, 0.07, 0.05), col=IRON_C, bev=0.003)
    for y in (-1.0, -0.4, 0.15, 0.7, 1.35):
        beam('oak', (-0.78, y, 0.88), (0.78, y, 0.88), 0.07, 0.07, bev=0.006, col=wcol, cfn=wood_cfn(wcol, 0.15, 5, int(y * 10) + 3, grime_z=0.0))
    # bearer block over axle
    beam('oak', (-0.7, AY, 0.69), (0.7, AY, 0.69), 0.14, 0.09, bev=0.006, col=DARK_W)
    # floor planks
    pl = 0.16
    for i in range(9):
        x = -0.69 + (i + 0.5) * 1.38 / 9
        c = jitter_col(wcol, 0.12, r)
        beam('pine', (x, -1.1, 0.935), (x, 1.5, 0.935), 1.38 / 9 - 0.008, 0.032, bev=0.004, col=c, cfn=wood_cfn(c, 0.12, 6, i, axis=1, grime_z=0.0))
    # stakes + rails (ladder sides)
    ys = [-1.0, -0.5, 0.0, 0.5, 1.0, 1.45]
    for sx in (-1, 1):
        for y in ys:
            beam('oak', (sx * 0.78, y, 0.82), (sx * 0.78, y, 1.52), 0.055, 0.05, bev=0.005, col=jitter_col(wcol, 0.1, r), up=(0, 1, 0))
        for z in (1.05, 1.28, 1.5):
            beam('oak', (sx * 0.805, -1.05, z), (sx * 0.805, 1.5, z), 0.045, 0.05, bev=0.005, col=jitter_col(wcol, 0.1, r), up=(1, 0, 0), cfn=wood_cfn(wcol, 0.13, 6, int(z * 10) + sx, axis=1, grime_z=0.0))
    # front & rear ladders (slanted)
    for y, lean in ((-1.07, -0.22), (1.55, 0.22)):
        for x in (-0.7, -0.35, 0.0, 0.35, 0.7):
            beam('oak', (x, y, 0.93), (x, y + lean, 1.62), 0.045, 0.045, bev=0.004, col=jitter_col(wcol, 0.1, r), up=(0, 1, 0))
        for z, f in ((1.1, 0.25), (1.35, 0.55), (1.58, 0.95)):
            beam('oak', (-0.76, y + lean * f * 0.8, z), (0.76, y + lean * f * 0.8, z), 0.04, 0.045, bev=0.004, col=jitter_col(wcol, 0.1, r), up=(0, 1, 0))
    # shafts
    for sx in (-1, 1):
        pts = [Vector((sx * 0.45, 0.2, 0.84)), Vector((sx * 0.43, -1.0, 0.80)), Vector((sx * 0.40, -2.0, 0.72)), Vector((sx * 0.38, -3.0, 0.64))]
        tube('oak', polyline_smooth(pts, 4), 0.038, taper=lambda t: 1 - 0.35 * t, seg=9, col=H('#9a8a6f'))
        box('iron_dark', (sx * 0.4, -2.0, 0.745), (0.05, 0.06, 0.12), col=IRON_C, bev=0.003)
    beam('oak', (-0.44, -2.95, 0.64), (0.44, -2.95, 0.64), 0.05, 0.05, bev=0.005, col=DARK_W)
    beam('oak', (-0.44, -2.1, 0.77), (0.44, -2.1, 0.77), 0.05, 0.05, bev=0.005, col=DARK_W)
    # prop stick
    beam('oak', (0.0, -2.6, 0.0), (0.0, -2.52, 0.72), 0.045, 0.045, bev=0.004, col=GREY_W, up=(0, 1, 0))
    # hay load
    bm = sphere_bm(1.0, 24, 14)
    for v in bm.verts:
        v.co = Vector((v.co.x * 0.84, v.co.y * 1.3, max(v.co.z, -0.12) * 0.5 if v.co.z < 0 else v.co.z * 0.95))
    bm = disp(bm, strength=0.08, scale=0.5, depth=2, seed_loc=(1, 4, 2))
    bm = disp(bm, strength=0.03, scale=0.14, depth=1, seed_loc=(6, 2, 4))
    Mh = Matrix.Translation((0, 0.2, 1.05))
    put_bm('straw', bm, M=Mh, cfn=lambda p: shade(hay_cfn(5, 12)(p), 0.62), skip_down=False)

    def surf(rr):
        th = rr.uniform(0.05, math.pi * 0.5 * 0.97); ph = rr.uniform(0, TAU)
        p = Vector((math.sin(th) * math.cos(ph) * 0.84, math.sin(th) * math.sin(ph) * 1.3, math.cos(th) * 0.95))
        n = Vector((p.x / 0.84 ** 2, p.y / 1.3 ** 2, p.z / 0.95 ** 2)).normalized()
        return p + Vector((0, 0.2, 1.05)), n
    straw_cover(surf, 1100, L=(0.22, 0.4), w=(0.03, 0.05), lift=0.02, seed=9, jit=0.8, tip=0.05)
    straw_whisks(None, 80, surf, L=(0.12, 0.25), w=0.012, seed=10, down=0.4)
    # pitchfork stuck in hay
    pitchfork((0.55, -0.5, 1.5), (0.35, -0.55, -0.6), L=1.45) if False else pitchfork((0.35, -0.2, 1.55), (0.45, -0.3, 0.8), L=1.2)
    # colliders
    collider(-1.05, 1.05, -1.2, 1.7, 1.9, 0.0)
    collider(-0.5, 0.5, -3.1, -1.2, 0.85, 0.5)

    def wheel_geo(sx):
        def f():
            M0 = Matrix.Translation((sx * 0.995, AY, AZ)) @ Matrix.Rotation(math.radians(90), 4, 'Y')
            wheel(M0, R=0.55, hub_r=0.075, width=0.075, spokes=12, col=H('#8b7b66'))
            # hub nut/linchpin
            f_ = FM(M0)
            f_.cyl('iron_dark', (0, 0, sx * 0.07 if False else 0.095), 0.03, 0.02, axis='z', seg=8, col=IRON_C)
        return f
    sub('cart_wheel_l', (0.995, AY, AZ), wheel_geo(1))
    sub('cart_wheel_r', (-0.995, AY, AZ), wheel_geo(-1))


@prop('water_trough', '물구유', cam=lambda m: [((2.8, -2.6, 1.6), (0, 0, 0.35), 40), ((-2.6, 2.4, 1.6), (0, 0, 0.35), 40), ((0.8, -1.5, 0.9), (0, 0, 0.35), 45), ((0.2, -0.7, 1.7), (0, 0, 0.3), 45)])
def water_trough():
    r = random.Random(4)
    Lx, Wy, Hh = 1.9, 0.66, 0.58
    wc = H('#8c8374')
    mossy = lambda base: (lambda p: mixc(wood_cfn(base, 0.15, 7, 5, grime_z=0.0)(p), H('#4a5a2c'), max(0.0, 1 - abs(p.z - 0.36) / 0.12) * 0.35 * (fbm(p.x, p.y, p.z, 8, 2, 2) * 0.5 + 0.5)))
    # long side boards (3 each), end boards, bottom
    for sy in (-1, 1):
        for k in range(3):
            z = 0.12 + k * 0.155 + 0.075
            c = jitter_col(wc, 0.1, r)
            beam('oak', (-Lx / 2 + 0.05, sy * (Wy / 2 - 0.025), z), (Lx / 2 - 0.05, sy * (Wy / 2 - 0.025), z), 0.05, 0.15, bev=0.005, col=c, cfn=mossy(c), up=(0, 0, 1))
    for sx in (-1, 1):
        for k in range(3):
            z = 0.12 + k * 0.155 + 0.075
            c = jitter_col(wc, 0.1, r)
            beam('oak', (sx * (Lx / 2 - 0.025), -Wy / 2, z), (sx * (Lx / 2 - 0.025), Wy / 2, z), 0.05, 0.15, bev=0.005, col=c, cfn=mossy(c), up=(1, 0, 0))
    for i in range(5):
        y = -Wy / 2 + (i + 0.5) * Wy / 5
        beam('dark', (-Lx / 2 + 0.05, y, 0.095), (Lx / 2 - 0.05, y, 0.095), Wy / 5 - 0.004, 0.04, bev=0.003, col=jitter_col(DARK_W, 0.1, r))
    # feet / legs
    for sx in (-1, 1):
        for sy in (-1, 1):
            beam('oak', (sx * (Lx / 2 - 0.1), sy * (Wy / 2 - 0.04), 0.0), (sx * (Lx / 2 - 0.1), sy * (Wy / 2 - 0.04), 0.34), 0.08, 0.08, bev=0.006, col=DARK_W, cfn=None)
    # iron bands
    for sx in (-0.62, 0.0, 0.62):
        x = sx * 1.0 * (Lx / 2 - 0.1) / 0.62 * 0.62 * 0.0 + sx
        for sy in (-1, 1):
            box('iron_dark', (x, sy * (Wy / 2 + 0.003), 0.31), (0.05, 0.012, 0.54), bev=0.003, col=IRON_C)
        box('iron_dark', (x, 0, 0.0 + 0.575), (0.045, Wy + 0.02, 0.012), bev=0.003, col=IRON_C)
    # rim cap (top rail) boards
    for sy in (-1, 1):
        beam('oak', (-Lx / 2 - 0.01, sy * (Wy / 2 - 0.02), 0.585), (Lx / 2 + 0.01, sy * (Wy / 2 - 0.02), 0.585), 0.085, 0.025, bev=0.005, col=jitter_col(wc, 0.1, r))
    for sx in (-1, 1):
        beam('oak', (sx * (Lx / 2 - 0.02), -Wy / 2, 0.585), (sx * (Lx / 2 - 0.02), Wy / 2, 0.585), 0.085, 0.025, bev=0.005, col=jitter_col(wc, 0.1, r), up=(1, 0, 0))
    # water surface with gentle ripples
    wg = cloth_sag_grid(-Lx / 2 + 0.05, Lx / 2 - 0.05, -Wy / 2 + 0.05, Wy / 2 - 0.05, 20, 8, lambda x, y: 0.47 + 0.004 * math.sin(x * 9 + y * 4) * math.cos(y * 7))
    put_bm('water', wg, col=H('#5c7f86'), skip_down=False)
    # stone slabs
    cf = stone_cfn(H('#837d72'), H('#a79b84'), 3.0, 4, moss=0.5)
    rock('stone', (0.0, 0.0, -0.02), (2.4, 1.1, 0.1), seed=3, cfn=cf, cuts=3, round_=0.15)
    # wooden ladle floating + bucket beside
    beam('oak', (0.25, 0.1, 0.475), (0.5, 0.18, 0.475), 0.02, 0.012, bev=0.002, col=OAK_D)
    cyl('oak', (0.22, 0.09, 0.47), 0.045, 0.03, seg=10, col=OAK_D)
    bucket(Matrix.Translation((1.25, -0.5, 0.0)) @ Matrix.Rotation(0.4, 4, 'Z'), r_top=0.17, r_bot=0.135, h=0.28, N=12, col=H('#8a7a62'), handle=True, seed=3)
    collider(-1.2, 1.2, -0.45, 0.45, 0.6, 0.0)
