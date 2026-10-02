"""Village props batch 3: fences, gate, stone wall, garden, coop, dog house, scarecrow, beehives, apple tree, rowboat."""
from vp_parts import *

def mulc_t(c, k):
    return (min(1.0, c[0] * k), min(1.0, c[1] * k), min(1.0, c[2] * k))


import vp_lib as _vpl
_orig_ao_prepare = _vpl.ao_prepare


def _ao_prepare_p3(objs, maxlen=0.14, minarea=0.008):
    # props in this module may request coarser AO subdivision (keeps tri counts down): CUR['ao_len']
    ml = CUR.get('ao_len', maxlen)
    return _orig_ao_prepare(objs, maxlen=ml, minarea=(minarea if ml <= maxlen else 0.03))


_vpl.ao_prepare = _ao_prepare_p3

LEAF_G = [H('#4c7a2c'), H('#5e8f35'), H('#78a040'), H('#3f6a26')]


def picket(x, y, h, w, col, seed, tipc=0.1, t=0.022, rz=0.0, bev=True):
    c = jitter_col(col, 0.1, random.Random(seed))
    cf = wood_cfn(c, 0.12, 8, seed, grime_z=0.25, axis=2)
    bm = bmesh.new()
    prof = [(-w / 2, 0.0), (w / 2, 0.0), (w / 2, h - tipc), (0.0, h), (-w / 2, h - tipc)] if tipc > 0 else [(-w / 2, 0.0), (w / 2, 0.0), (w / 2, h), (-w / 2, h)]
    fr = [bm.verts.new((px, -t / 2, pz)) for px, pz in prof]
    bk = [bm.verts.new((px, t / 2, pz)) for px, pz in prof]
    n = len(prof)
    bm.faces.new(fr[::-1])
    bm.faces.new(bk)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((fr[j], fr[i], bk[i], bk[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if bev:
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=0.0025, segments=1, affect='EDGES')
    put('pine', bm, xf((x, y, 0), (0, 0, rz)), c, cf, 2)
    bm.free()


@prop('wooden_fence_a', '나무 울타리', cam=lambda m: [((2.6, -2.6, 1.3), (0, 0, 0.5), 40), ((-2.4, 2.2, 1.3), (0, 0, 0.5), 40), ((0.5, -1.1, 0.8), (0.3, 0, 0.6), 45), ((-1.2, -0.9, 0.5), (-0.9, 0, 0.5), 45)])
def wooden_fence_a():
    CUR['ao_len'] = 0.3
    rr = random.Random(11)
    pc = H('#948768')
    for x in (-0.94, 0.0, 0.94):
        h = 1.02 + rr.uniform(-0.03, 0.03)
        c = jitter_col(GREY_W, 0.1, rr)
        beam('oak', (x, 0.03, 0), (x, 0.03, h), 0.11, 0.10, bev=0.008, col=c, cfn=wood_cfn(c, 0.15, 6, int(x * 10) + 3, grime_z=0.3))
        # chamfered top
        box('oak', (x, 0.03, h + 0.012), (0.09, 0.08, 0.03), bev=0.006, col=c, taper=(0.7, 0.7), skip_down=False)
    # two rails behind pickets (slightly bowed, half split)
    for z in (0.32, 0.78):
        c = jitter_col(GREY_W, 0.08, rr)
        beam('oak', (-1.0, 0.075, z + 0.008), (1.0, 0.075, z - 0.006), 0.04, 0.085, bev=0.006, col=c, cfn=wood_cfn(c, 0.15, 5, int(z * 10), grime_z=0.0, axis=0))
    n = 12
    for i in range(n):
        x = -0.94 + 1.88 * i / (n - 1) + rr.uniform(-0.01, 0.01)
        h = 0.92 + rr.uniform(-0.05, 0.04)
        picket(x, 0.0, h, 0.1 + rr.uniform(-0.01, 0.01), pc, 40 + i, bev=False)
        nail((x, -0.012, 0.78 + rr.uniform(-0.012, 0.012)), (0, -1, 0), r=0.006)
    collider(-1.0, 1.0, -0.08, 0.12, 1.05, 0.0)


@prop('fence_gate', '울타리 대문', kind='animated', cam=lambda m: [((2.6, -2.4, 1.3), (0, 0, 0.55), 40), ((-2.2, 2.2, 1.3), (0, 0, 0.55), 40), ((-0.2, -1.5, 0.9), (-0.45, 0, 0.9), 45), ((1.6, -1.0, 0.9), (0.6, 0, 0.9), 45)])
def fence_gate():
    CUR['ao_len'] = 0.3
    rr = random.Random(21)
    HGT = 1.1
    PX = 0.72
    for sx in (-1, 1):
        c = jitter_col(GREY_W, 0.1, rr)
        beam('oak', (sx * PX, 0, 0), (sx * PX, 0, HGT + 0.1), 0.14, 0.14, bev=0.01, col=c, cfn=wood_cfn(c, 0.15, 6, 5 + sx, grime_z=0.35))
        box('oak', (sx * PX, 0, HGT + 0.12), (0.15, 0.15, 0.04), bev=0.008, col=c, taper=(0.75, 0.75), skip_down=False)
        # stub fence rails outward
        for z in (0.35, 0.8):
            beam('oak', (sx * PX, 0.09, z), (sx * 1.0, 0.09, z), 0.035, 0.08, bev=0.005, col=c, cfn=wood_cfn(c, 0.15, 5, 9, grime_z=0.0, axis=0))
        for i in range(2):
            picket(sx * (0.85 + i * 0.1), 0.0, 0.95 - i * 0.02, 0.09, H('#a89878'), 60 + i + (sx + 1) * 5)
    # latch on right post
    box('iron_dark', (0.69, -0.085, 0.82), (0.07, 0.015, 0.04), col=IRON_C, bev=0.003)
    box('iron_dark', (0.63, -0.075, 0.82), (0.07, 0.012, 0.02), col=IRON_C, bev=0.002)
    # gate stop block / hinge pin plates on left post
    for z in (0.35, 0.85):
        box('iron_dark', (-0.72, -0.082, z), (0.04, 0.012, 0.04), col=IRON_C, bev=0.002)
    collider(-1.0, -0.64, -0.08, 0.1, 1.2, 0.0)
    collider(0.64, 1.0, -0.08, 0.1, 1.2, 0.0)

    hx = -0.60

    def door():
        gc = H('#a09070')
        W = 1.18  # from hinge at x=-0.60 to x=0.58
        for z in (0.30, 0.62, 0.94):
            c = jitter_col(gc, 0.1, rr)
            beam('pine', (hx + 0.02, 0, z), (hx + 1.18, 0, z), 0.03, 0.09, bev=0.004, col=c, cfn=wood_cfn(c, 0.12, 6, int(z * 100), grime_z=0.0, axis=0))
        for x in (hx + 0.05, hx + 0.60, hx + 1.15):
            c = jitter_col(gc, 0.1, rr)
            beam('pine', (x, -0.028, 0.14), (x, -0.028, 1.05), 0.075, 0.03, bev=0.004, col=c, cfn=wood_cfn(c, 0.12, 6, int(x * 90), grime_z=0.2, axis=2), up=(0, 1, 0))
        # diagonal brace
        beam('pine', (hx + 0.1, -0.058, 0.20), (hx + 1.1, -0.058, 0.98), 0.07, 0.03, bev=0.004, col=jitter_col(gc, 0.1, rr), up=(0, 1, 0))
        for x in (hx + 0.05, hx + 1.15):
            for z in (0.30, 0.94):
                nail((x, -0.044, z), (0, -1, 0), r=0.007)
        # vertical pale infill
        for i in range(6):
            x = hx + 0.17 + i * 0.185
            picket(x, 0.012, 0.98 - 0.0 * i, 0.075, H('#aa9a7a'), 80 + i, tipc=0.0) if False else None
        # iron strap hinges
        for z in (0.30, 0.94):
            beam('iron_dark', (hx - 0.01, -0.07, z), (hx + 0.38, -0.07, z), 0.03, 0.012, bev=0.002, col=IRON_C, up=(0, 1, 0))
            cyl('iron_dark', (hx - 0.012, -0.075, z), 0.018, 0.04, axis='z', seg=8, col=IRON_C)
        # latch bar
        beam('iron_dark', (hx + 0.9, -0.06, 0.64), (hx + 1.22, -0.06, 0.64), 0.02, 0.012, bev=0.002, col=IRON_C, up=(0, 1, 0))
    sub('fence_gate_door', (hx, 0, 0), door)


@prop('stone_wall_a', '돌담', cam=lambda m: [((2.8, -2.6, 1.5), (0, 0, 0.4), 40), ((-2.4, 2.2, 1.5), (0, 0, 0.4), 40), ((0.6, -1.2, 0.9), (0.3, 0, 0.5), 45), ((0, -1.4, 1.9), (0, 0, 0.5), 45)])
def stone_wall_a():
    CUR['ao_len'] = 0.3
    rr = random.Random(31)
    cf = stone_cfn(H('#c4bcad'), H('#e2d4b8'), 4.0, 5, moss=0.7)
    HC = [0.17, 0.16, 0.15, 0.15, 0.14, 0.13]
    z = 0.0
    for ci, hc in enumerate(HC):
        for row, yc in enumerate((-0.14, 0.14)):
            x = -1.0 - rr.uniform(0, 0.15)
            k = 0
            while x < 1.0:
                ln = rr.uniform(0.26, 0.46)
                xc = x + ln / 2
                if xc - ln / 2 > 1.0:
                    break
                ln_c = min(ln, 1.06 - x)
                xc = x + ln_c / 2
                if xc - ln_c / 2 > 1.0:
                    break
                tw = rr.uniform(0.25, 0.32)
                rock('stone', (xc, yc + rr.uniform(-0.02, 0.02), z + hc / 2 + rr.uniform(-0.004, 0.01)), (ln_c * 1.03, tw, hc * rr.uniform(1.0, 1.15)),
                     seed=ci * 200 + row * 50 + k, rot=(rr.uniform(-0.04, 0.04), rr.uniform(-0.04, 0.04), rr.uniform(-0.1, 0.1)), cfn=cf, cuts=1, round_=0.28, jitter=0.1)
                x += ln_c * 0.97
                k += 1
        z += hc * 0.95
    # capstones standing on edge
    x = -1.0
    k = 0
    while x < 0.95:
        ln = rr.uniform(0.22, 0.32)
        rock('stone', (x + ln / 2, rr.uniform(-0.02, 0.02), z + 0.09), (ln, rr.uniform(0.42, 0.5), rr.uniform(0.17, 0.24)), seed=900 + k,
             rot=(0, rr.uniform(-0.06, 0.06), rr.uniform(-0.12, 0.12)), cfn=cf, cuts=1, round_=0.3, jitter=0.1)
        x += ln * 0.92
        k += 1
    # little grass/earth lip at base
    collider(-1.05, 1.05, -0.27, 0.27, 0.95, 0.0)


def leaf_at(mat, base, az, tilt, size, col, tip=0.0):
    """leaf with its base at 'base', leaning by 'tilt' (rad from vertical) toward azimuth az (rad, 0=+x)."""
    L = size[0]
    d = Vector((math.cos(az) * math.sin(tilt), math.sin(az) * math.sin(tilt), math.cos(tilt)))
    c = Vector(base) + d * (L / 2)
    # rotate: leaf long axis z -> d.  Euler: tilt about y-axis then azimuth about z
    leafquad(mat, c, size, (0, tilt, az), col=col, tip=tip) if False else None
    M = Matrix.Rotation(az, 4, 'Z') @ Matrix.Rotation(tilt, 4, 'Y')
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    Lh, W = size
    pts = [(0, 0, -Lh * 0.5), (W * 0.5, 0, -Lh * 0.1), (W * 0.35, 0, Lh * 0.3), (0, 0, Lh * 0.5), (-W * 0.35, 0, Lh * 0.3), (-W * 0.5, 0, -Lh * 0.1)]
    vs = [bm.verts.new(p) for p in pts]
    f = bm.faces.new(vs)
    f.smooth = False
    for l in f.loops:
        l[ul].uv = (l.vert.co.x / W + 0.5, l.vert.co.z / Lh + 0.5)
    for v in bm.verts:   # cup/droop
        v.co.y += tip * ((v.co.z / Lh + 0.5) ** 2) * Lh
    put(mat, bm, Matrix.Translation(c) @ M, col, None, 2, flat=True)
    bm.free()


def cabbage(x, y, r, seed):
    rr = random.Random(seed)
    sphere('leaf', (x, y, r * 0.95), r, seg=10, rings=6, sq=(1, 1, 0.9), col=H('#9bb56a'))
    n = 6
    for i in range(n):
        az = TAU * i / n + rr.uniform(-0.2, 0.2)
        tl = 0.55 + 0.12 * (i % 2) + rr.uniform(-0.1, 0.1)
        c = mixc(H('#5f8a4c'), H('#7da05c'), rr.random())
        leaf_at('leaf', (x + math.cos(az) * r * 0.5, y + math.sin(az) * r * 0.5, r * 0.25), az, tl + 0.5, (r * 2.4, r * 2.2), c, tip=0.12)
    for i in range(3):
        az = TAU * i / 3 + 0.3
        leaf_at('leaf', (x, y, r * 0.5), az, 0.35, (r * 1.9, r * 1.6), mixc(H('#86a860'), H('#a2c070'), rr.random()), tip=0.1)


def lettuce(x, y, r, seed):
    rr = random.Random(seed)
    for k in range(3):
        n = 5 + k * 2
        for i in range(n):
            az = TAU * i / n + k * 0.4 + rr.uniform(-0.15, 0.15)
            c = mixc(H('#7fae45'), H('#b9d36a'), (3 - k) / 3 * 0.5 + rr.random() * 0.4)
            leaf_at('leaf', (x, y, r * 0.15 + k * r * 0.18), az, 0.25 + k * 0.28, (r * (2.0 - k * 0.4), r * (1.7 - k * 0.2)), c, tip=0.18)


def carrot(x, y, seed):
    rr = random.Random(seed)
    lathe('food', None, [(0.0, -0.015), (0.016, 0.0), (0.017, 0.012), (0.0, 0.012)], seg=8, M=xf((x, y, 0.1)), col=H('#d9772a'), cap=False, auto=False)
    for i in range(5):
        az = TAU * i / 5 + rr.uniform(-0.2, 0.2)
        tl = 0.25 + rr.uniform(0, 0.5)
        p0 = Vector((x, y, 0.11))
        d = Vector((math.cos(az) * math.sin(tl), math.sin(az) * math.sin(tl), math.cos(tl)))
        L = rr.uniform(0.2, 0.3)
        c = mixc(H('#4d8a33'), H('#6aa83e'), rr.random())
        ribbon('leaf', p0, p0 + d * L, 0.03, 0.012, col=c, bend=(0, 0, -0.03), nseg=3, up=(0, 0, 1))


def bean_tripod(cx, cy, seed, H_=1.75, R0=0.3):
    rr = random.Random(seed)
    top = Vector((cx, cy, H_))
    for i in range(3):
        a = TAU * i / 3 + 0.4
        b0 = Vector((cx + math.cos(a) * R0, cy + math.sin(a) * R0, 0.0))
        tube('pine', [b0, b0.lerp(top, 0.5), top + Vector((math.cos(a) * 0.015, math.sin(a) * 0.015, 0.1))], 0.013, seg=6, col=jitter_col(H('#8b7455'), 0.15, rr))
        # vine spiral
        pts = []
        for k in range(14):
            t = k / 13
            p = b0.lerp(top, t * 0.92)
            ang = 7.0 * t * math.pi * 2 / 3 + a
            pts.append(p + Vector((math.cos(ang), math.sin(ang), 0)) * 0.025)
        tube('leaf', pts, 0.0045, seg=4, col=H('#4a7a2a'))
        for k in range(6):
            t = 0.1 + 0.85 * rr.random()
            p = b0.lerp(top, t * 0.92)
            az = rr.uniform(0, TAU)
            leaf_at('leaf', p, az, 1.0 + rr.uniform(-0.2, 0.3), (0.1, 0.09), mixc(H('#3f7a2a'), H('#6a9a3a'), rr.random()), tip=0.1)
        for k in range(2):
            t = 0.25 + 0.5 * rr.random()
            p = b0.lerp(top, t * 0.92) + Vector((0.03, 0, 0))
            tube('leaf', [p, p + Vector((0.01, 0.01, -0.09)), p + Vector((0.0, 0.02, -0.17))], 0.006, seg=5, col=H('#78a63f'))
    # cord at top
    cyl('rope', (cx, cy, H_ + 0.02), 0.03, 0.05, axis='z', seg=8, col=ROPE_C)


@prop('garden_plot_a', '채소밭', cam=lambda m: [((3.6, -4.2, 2.6), (0, 0, 0.5), 38), ((-3.6, 3.6, 2.6), (0, 0, 0.5), 38), ((-0.4, -1.8, 0.9), (-0.4, 0, 0.2), 45), ((2.0, -1.4, 1.4), (1.0, 0, 0.9), 45)])
def garden_plot_a():
    CUR['ao_len'] = 0.35
    rr = random.Random(41)
    HX, HY = 1.5, 1.0
    soilc = H('#3a2a1c')
    sf = lambda p: mixc(soilc, H('#54402b'), 0.5 + 0.5 * fbm(p.x, p.y, p.z, 9, 3, 2))
    box('soil', (0, 0, 0.04), (2 * HX - 0.12, 2 * HY - 0.12, 0.08), bev=0.0, cuts=3, cfn=sf, skip_down=False)
    # rows
    for yy in (-0.6, 0.0, 0.6):
        sphere('soil', (-0.35, yy, 0.05), 1.0, seg=14, rings=6, sq=(0.95, 0.2, 0.075), cfn=sf)
    for i in range(5):
        cabbage(-1.05 + i * 0.4 + rr.uniform(-0.03, 0.03), -0.6 + rr.uniform(-0.02, 0.02), 0.11 + rr.uniform(-0.01, 0.02), 100 + i)
    for i in range(9):
        carrot(-1.2 + i * 0.2 + rr.uniform(-0.02, 0.02), 0.0 + rr.uniform(-0.02, 0.02), 200 + i)
    for i in range(5):
        lettuce(-1.1 + i * 0.37, 0.6 + rr.uniform(-0.02, 0.02), 0.075 + rr.uniform(0, 0.015), 300 + i)
    for i in range(12):
        rock('soil', (rr.uniform(-1.3, 1.3), rr.uniform(-0.85, 0.85), 0.07), (0.05, 0.05, 0.035), seed=i, cfn=lambda p: soilc, cuts=0, round_=0.6)
    bean_tripod(1.0, -0.45, 1)
    bean_tripod(1.0, 0.45, 2)
    # fence: low pickets, posts, rail
    pc = H('#948768')
    FH = 0.52
    sides = [((-HX, -HY), (HX, -HY), 0), ((HX, -HY), (HX, HY), 90), ((HX, HY), (-HX, HY), 180), ((-HX, HY), (-HX, -HY), 270)]
    for (a, b, ang) in sides:
        a = Vector((a[0], a[1], 0)); b = Vector((b[0], b[1], 0))
        L = (b - a).length
        n = int(L / 0.16)
        for i in range(n):
            p = a.lerp(b, (i + 0.5) / n)
            hh = FH + rr.uniform(-0.03, 0.03)
            picket(p.x, p.y, hh, 0.085, pc, 500 + i + int(ang), tipc=0.07, rz=ang, bev=False)
        # rail on inside
        inward = Vector((-(b - a).y, (b - a).x, 0)).normalized()
        for z in (0.16, 0.38):
            beam('oak', a + inward * 0.03 + Vector((0, 0, z)), b + inward * 0.03 + Vector((0, 0, z)), 0.03, 0.05, bev=0.004, col=GREY_W, cfn=wood_cfn(GREY_W, 0.12, 5, 3, grime_z=0))
    for (px, py) in [(-HX, -HY), (HX, -HY), (HX, HY), (-HX, HY), (0, -HY), (0, HY)]:
        h = 0.68
        beam('oak', (px, py, 0), (px, py, h), 0.07, 0.07, bev=0.006, col=GREY_W, cfn=wood_cfn(GREY_W, 0.15, 6, 2, grime_z=0.25))
    collider(-HX, HX, -HY - 0.03, -HY + 0.03, 0.55, 0.0)
    collider(-HX, HX, HY - 0.03, HY + 0.03, 0.55, 0.0)
    collider(-HX - 0.03, -HX + 0.03, -HY, HY, 0.55, 0.0)
    collider(HX - 0.03, HX + 0.03, -HY, HY, 0.55, 0.0)


def shingles0(mat, A, B, C, D, rows, per_row, w, lth, thick, col, seed=0, tilt=0.12):
    r = random.Random(seed)
    A, B, C, D = [Vector(v) for v in (A, B, C, D)]
    xdir = (B - A).normalized()
    slope_up = ((C + D) / 2 - (A + B) / 2).normalized()
    zdir = xdir.cross(slope_up).normalized()
    if zdir.z < 0:
        zdir = -zdir
    ydir2 = zdir.cross(xdir)
    Mb = Matrix(((xdir.x, ydir2.x, zdir.x, 0), (xdir.y, ydir2.y, zdir.y, 0), (xdir.z, ydir2.z, zdir.z, 0), (0, 0, 0, 1)))
    for i in range(rows):
        t = i / max(1, rows - 1)
        lo = A.lerp(D, t); hi = B.lerp(C, t)
        for j in range(per_row):
            u = (j + 0.5 + (0.5 if i % 2 else 0.0) + r.uniform(-0.1, 0.1)) / per_row
            if u > 1.02:
                continue
            c = lo.lerp(hi, min(1.0, u))
            tl = Euler((math.radians(tilt * 20 * (1 + r.uniform(-0.3, 0.3))) + 0.04, 0, math.radians(r.uniform(-2, 2))), 'XYZ').to_matrix().to_4x4()
            Mx = Matrix.Translation(c + zdir * (0.004 * (i % 2) + 0.001 * r.random())) @ Mb @ tl
            box(mat, None, (w * r.uniform(0.92, 1.0), lth, thick), M=Mx, bev=0.0, col=jitter_col(col, 0.16, r), g=1, skip_down=False)


def roof_slopes(xl, yE, zE, zR, col=H('#7c6446'), rows=8, per_row=9, w=0.24, lth=0.24, seed=3, deck_col=H('#6a5239'), ridge=True, ridge_len=None):
    """gable roof along x with shingles on both slopes."""
    slope_len = math.hypot(yE, zR - zE)
    rx = math.atan2(zR - zE, yE)
    for sy in (-1, 1):
        A = (-xl, sy * yE, zE); B = (xl, sy * yE, zE); C = (xl, 0.0, zR); D = (-xl, 0.0, zR)
        mid = (Vector(A) + Vector(B) + Vector(C) + Vector(D)) / 4
        Mdeck = Matrix.Translation(mid + Vector((0, 0, -0.02))) @ Matrix.Rotation(-sy * rx, 4, 'X')
        box('dark', None, (2 * xl + 0.04, slope_len + 0.06, 0.035), M=Mdeck, bev=0.0, col=deck_col, g=0, skip_down=False)
        shingles0('oak', A, B, C, D, rows, per_row, w, lth, 0.013, col, seed + sy, 0.18)
    if ridge:
        beam('oak', (-xl - 0.02, 0, zR + 0.012), (xl + 0.02, 0, zR + 0.012), 0.14, 0.03, bev=0.005, col=deck_col)


def vboards(mat, x0, x1, y, z0, z1, bw=0.12, gap=0.004, col=PINE_W, seed=0, hfn=None, skip=None, t=0.022, rz=0.0):
    """vertical boards across x0..x1 at depth y from z0 to z1 (or per-board top via hfn(x))"""
    rr = random.Random(seed)
    n = max(1, int(round((x1 - x0) / bw)))
    w = (x1 - x0) / n
    for i in range(n):
        x = x0 + (i + 0.5) * w
        top = hfn(x) if hfn else z1
        for (a, b) in (skip(x, w) if skip else [(z0, top)]):
            if b - a < 0.02:
                continue
            c = jitter_col(col, 0.1, rr)
            box(mat, (x, y, (a + b) / 2), (w - gap, t, b - a), bev=0.0, col=c, cfn=wood_cfn(c, 0.12, 8, seed + i, grime_z=0.25, axis=2), g=2, skip_down=False)


@prop('chicken_coop', '닭장', cam=lambda m: [((3.2, -3.4, 2.2), (0.1, -0.2, 0.8), 38), ((-3.2, 2.8, 2.2), (0, 0, 0.8), 38), ((-0.4, -2.2, 1.0), (-0.3, -0.8, 0.8), 45), ((2.0, -0.9, 1.2), (1.0, 0, 0.7), 45)])
def chicken_coop():
    CUR['ao_len'] = 0.35
    rr = random.Random(51)
    XL, YL = 0.8, 0.55
    ZF = 0.56      # floor top
    ZW = 1.12      # eave wall top
    ZR = 1.42
    wc = H('#9a8c6c')
    # legs
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = jitter_col(GREY_W, 0.1, rr)
            beam('oak', (sx * 0.72, sy * 0.47, 0), (sx * 0.72, sy * 0.47, ZF), 0.08, 0.08, bev=0.006, col=c, cfn=wood_cfn(c, 0.15, 6, 3, grime_z=0.3))
    # floor frame
    for sy in (-1, 1):
        beam('oak', (-XL, sy * 0.47, ZF - 0.07), (XL, sy * 0.47, ZF - 0.07), 0.07, 0.1, bev=0.005, col=GREY_W)
    for sx in (-1, 1):
        beam('oak', (sx * 0.72, -YL, ZF - 0.07), (sx * 0.72, YL, ZF - 0.07), 0.07, 0.1, bev=0.005, col=GREY_W)
    plank_row('pine', -XL - 0.03, XL + 0.03, 0.0, ZF - 0.03, 1, 0.03, 1.2, col=wc) if False else None
    box('pine', (0, 0, ZF - 0.015), (2 * XL + 0.04, 2 * YL + 0.04, 0.03), bev=0.004, col=H('#8a7a5c'), cfn=wood_cfn(H('#8a7a5c'), 0.12, 6, 1, grime_z=0), g=0, skip_down=False)
    # walls: front with pop hole
    hole = (-0.44, -0.16)
    holez = (ZF + 0.08, ZF + 0.50)

    def skip_front(x, w):
        if x + w / 2 > hole[0] and x - w / 2 < hole[1]:
            return [(ZF, holez[0]), (holez[1], ZW)]
        return [(ZF, ZW)]
    vboards('pine', -XL, XL, -YL, ZF, ZW, 0.13, col=wc, seed=1, skip=skip_front)
    vboards('pine', -XL, XL, YL, ZF, ZW, 0.13, col=wc, seed=2)
    for sx in (-1, 1):
        # side walls (gable boards run vertical, tops follow roof line)
        hf = lambda y: ZW + (ZR - ZW) * (1 - abs(y) / YL) * 0.96
        for i in range(8):
            y = -YL + (i + 0.5) * (2 * YL / 8)
            top = ZW + (ZR - ZW - 0.04) * (1 - abs(y) / YL)
            c = jitter_col(wc, 0.1, rr)
            if sx == 1 and abs(y) < 0.3:
                top = min(top, ZW)
            box('pine', (sx * XL, y, (ZF + top) / 2), (0.022, 2 * YL / 8 - 0.004, top - ZF), bev=0.0, col=c, cfn=wood_cfn(c, 0.12, 8, i, grime_z=0.25, axis=2), g=2, skip_down=False)
    # corner trims
    for sx in (-1, 1):
        for sy in (-1, 1):
            beam('oak', (sx * XL, sy * YL, ZF), (sx * XL, sy * YL, ZW), 0.05, 0.05, bev=0.004, col=GREY_W, cfn=wood_cfn(GREY_W, 0.12, 6, 3, grime_z=0.2))
    # horizontal battens at wall top and mid
    for z in (ZF + 0.04, ZW - 0.04):
        beam('oak', (-XL, -YL - 0.015, z), (XL, -YL - 0.015, z), 0.03, 0.045, bev=0.004, col=GREY_W, cfn=wood_cfn(GREY_W, 0.12, 6, 2, grime_z=0, axis=0))
    # pop hole frame
    for (a, b, s) in (((hole[0] - 0.02, -YL - 0.02, holez[0] - 0.015), (hole[1] + 0.02, -YL - 0.02, holez[0] - 0.015), 0), ((hole[0] - 0.02, -YL - 0.02, holez[1] + 0.015), (hole[1] + 0.02, -YL - 0.02, holez[1] + 0.015), 0)):
        beam('oak', a, b, 0.03, 0.04, bev=0.003, col=GREY_W, up=(0, 0, 1))
    for x in (hole[0] - 0.02, hole[1] + 0.02):
        beam('oak', (x, -YL - 0.02, holez[0]), (x, -YL - 0.02, holez[1]), 0.04, 0.03, bev=0.003, col=GREY_W, up=(0, 1, 0))
    # roof
    roof_slopes(XL + 0.14, YL + 0.16, ZW - 0.02, ZR + 0.02, col=H('#7c6446'), rows=6, per_row=7, w=0.27, lth=0.3, seed=5)
    # barge boards
    for sx in (-1, 1):
        for sy in (-1, 1):
            beam('oak', (sx * (XL + 0.14), sy * (YL + 0.17), ZW - 0.06), (sx * (XL + 0.14), 0, ZR + 0.04), 0.04, 0.03, bev=0.003, col=H('#8b7352'), up=(1, 0, 0))
    # nesting box lean-to on +x side
    nx0, nx1 = XL, XL + 0.36
    ny = 0.28
    for sy in (-1, 1):
        box('pine', ((nx0 + nx1) / 2, sy * ny, ZF + 0.18), (nx1 - nx0, 0.022, 0.36), bev=0.003, col=wc, cfn=wood_cfn(wc, 0.12, 8, 7, grime_z=0.2, axis=0), g=0, skip_down=False)
    box('pine', (nx1, 0, ZF + 0.18), (0.022, 2 * ny, 0.36), bev=0.003, col=wc, cfn=wood_cfn(wc, 0.12, 8, 8, grime_z=0.2), g=1, skip_down=False)
    box('pine', ((nx0 + nx1) / 2, 0, ZF - 0.01), (nx1 - nx0 + 0.04, 2 * ny + 0.04, 0.03), bev=0.004, col=H('#8a7a5c'), g=0, skip_down=False)
    # hinged lid (sloped) with handle batten
    lid_M = Matrix.Translation(((nx0 + nx1) / 2 + 0.01, 0, ZF + 0.38)) @ Matrix.Rotation(math.radians(12), 4, 'Y')
    box('pine', None, (nx1 - nx0 + 0.1, 2 * ny + 0.1, 0.024), M=lid_M, bev=0.004, col=H('#9a8a6a'), cfn=None, g=0, skip_down=False)
    for sy in (-1, 1):
        beam('iron_dark', (nx0 + 0.02, sy * (ny - 0.02), ZF + 0.395), (nx0 + 0.16, sy * (ny - 0.02), ZF + 0.395), 0.025, 0.008, bev=0.0015, col=IRON_C)
    # ramp
    ry0, ry1 = -YL - 0.05, -1.45
    rz0, rz1 = holez[0] - 0.02, 0.02
    rx = -0.30
    Mr = xf(((rx), (ry0 + ry1) / 2, (rz0 + rz1) / 2), (math.degrees(math.atan2(rz0 - rz1, abs(ry1 - ry0))) * 1.0, 0, 0))
    ang = math.atan2(rz0 - rz1, abs(ry1 - ry0))
    Mr = Matrix.Translation((rx, (ry0 + ry1) / 2, (rz0 + rz1) / 2)) @ Matrix.Rotation(ang, 4, 'X')
    rl = math.hypot(ry1 - ry0, rz0 - rz1)
    box('pine', None, (0.3, rl, 0.03), M=Mr, bev=0.004, col=H('#9a8a6a'), cfn=wood_cfn(H('#9a8a6a'), 0.12, 6, 12, grime_z=0), g=1, skip_down=False)
    for k in range(7):
        t = (k + 0.7) / 7.2
        cy = ry0 + (ry1 - ry0) * t
        cz = rz0 + (rz1 - rz0) * t + 0.022
        box('oak', (rx, cy, cz), (0.28, 0.025, 0.018), bev=0.002, col=GREY_W, skip_down=False, rot=(math.degrees(ang), 0, 0))
    for sx in (-1, 1):
        beam('oak', (rx + sx * 0.14, ry0, rz0 + 0.015), (rx + sx * 0.14, ry1, rz1 + 0.015), 0.02, 0.05, bev=0.003, col=GREY_W, up=(0, 0, 1))
    # perch on -x side
    for sy in (-0.3, 0.3):
        beam('oak', (-XL, sy, 0.66), (-XL - 0.2, sy, 0.78), 0.03, 0.03, bev=0.003, col=GREY_W)
    tube('pine', [Vector((-XL - 0.2, -0.45, 0.8)), Vector((-XL - 0.2, 0.45, 0.8))], 0.022, seg=8, col=H('#8b7455'))
    # a latch for cleaning door (back)
    box('iron_dark', (0.12, YL + 0.02, ZF + 0.3), (0.12, 0.012, 0.025), col=IRON_C, bev=0.002)
    for x in (-0.22, 0.46):
        nail((x, YL + 0.016, ZF + 0.3), (0, 1, 0), r=0.007)
    # a bit of straw on the ramp threshold
    for i in range(12):
        ribbon('straw', (rx + rr.uniform(-0.12, 0.12), ry0 - 0.1, 0.12 + 0.2), (rx + rr.uniform(-0.12, 0.12), ry0 - rr.uniform(0.0, 0.2), 0.22), 0.01, col=STRAW_C) if False else None
    collider(-XL - 0.25, XL + 0.4, -YL - 0.02, YL + 0.02, 1.45, 0.0)
    collider(-0.45, -0.15, -1.45, -YL, 0.25, 0.0)


def hboards_y(mat, x, y0, y1, z0, nrows, bh, col, seed, t=0.022):
    rr = random.Random(seed)
    for i in range(nrows):
        z = z0 + i * (bh + 0.004) + bh / 2
        c = jitter_col(col, 0.1, rr)
        beam(mat, (x, y0, z), (x, y1, z), t, bh, bev=0.0, col=c, cfn=wood_cfn(c, 0.12, 7, seed + i, grime_z=0.2, axis=1))


@prop('dog_house', '개집', cam=lambda m: [((1.9, -2.2, 1.4), (0, 0, 0.4), 38), ((-1.9, 1.8, 1.4), (0, 0, 0.4), 38), ((0.2, -1.4, 0.55), (0, -0.4, 0.3), 45), ((1.0, -1.0, 0.45), (0.5, -0.7, 0.1), 45)])
def dog_house():
    CUR['ao_len'] = 0.3
    rr = random.Random(61)
    XL, YL = 0.40, 0.52
    Z0 = 0.09
    bh = 0.0725
    NR = 9
    wc = H('#8f8268')
    # skids + floor
    for sx in (-1, 1):
        beam('oak', (sx * 0.34, -0.58, 0.03), (sx * 0.34, 0.58, 0.03), 0.07, 0.06, bev=0.005, col=GREY_W)
    box('pine', (0, 0, Z0 - 0.015), (0.8, 1.04, 0.03), bev=0.0, col=H('#7a6a50'), g=1, skip_down=False)
    for sx in (-1, 1):
        hboards_y('pine', sx * XL, -YL, YL, Z0, NR, bh, wc, 3 + sx)
    # back wall
    for i in range(NR):
        z = Z0 + i * (bh + 0.004) + bh / 2
        c = jitter_col(wc, 0.1, rr)
        beam('pine', (-XL, YL, z), (XL, YL, z), 0.022, bh, bev=0.0, col=c, cfn=wood_cfn(c, 0.12, 7, 20 + i, grime_z=0.2, axis=0))
    zc, hr = 0.30, 0.17

    def hw_at(z):
        if z < zc:
            return hr
        if z < zc + hr:
            return math.sqrt(max(0.0, hr * hr - (z - zc) ** 2))
        return 0.0
    ZW = Z0 + NR * (bh + 0.004)
    for i in range(NR + 4):
        z0 = Z0 + i * (bh + 0.004)
        z = z0 + bh / 2
        hwin = (XL + 0.02) - (max(0, z0 - ZW + 0.004) / 0.26) * (XL + 0.02)   # gable half width
        if hwin < 0.03:
            break
        hwz = hw_at(z)
        for ysd in (-1, 1):
            yy = ysd * YL
            c = jitter_col(wc, 0.1, rr)
            if ysd == -1 and hwz > 0:
                beam('pine', (-hwin, yy, z), (-hwz, yy, z), 0.022, bh, bev=0.0, col=c, cfn=wood_cfn(c, 0.12, 7, 40 + i, grime_z=0.2, axis=0))
                beam('pine', (hwz, yy, z), (hwin, yy, z), 0.022, bh, bev=0.0, col=jitter_col(wc, 0.1, rr), cfn=wood_cfn(c, 0.12, 7, 60 + i, grime_z=0.2, axis=0))
            elif ysd == -1 or i >= NR:
                beam('pine', (-hwin, yy, z), (hwin, yy, z), 0.022, bh, bev=0.0, col=c, cfn=wood_cfn(c, 0.12, 7, 80 + i, grime_z=0.2, axis=0))
    # arch trim
    path = []
    ty = -YL - 0.03
    rt = hr + 0.03
    path += [Vector((-rt, ty, Z0)), Vector((-rt, ty, zc))]
    for k in range(1, 12):
        a = math.pi - math.pi * k / 12
        path.append(Vector((math.cos(a) * rt, ty, zc + math.sin(a) * rt)))
    path += [Vector((rt, ty, zc)), Vector((rt, ty, Z0))]
    sweep('oak', [(-0.015, -0.025), (0.015, -0.025), (0.015, 0.025), (-0.015, 0.025)], polyline_smooth(path, 2), up=(0, 1, 0), col=H('#8a6a46'), caps=True)
    # corner posts
    for sx in (-1, 1):
        for sy in (-1, 1):
            beam('oak', (sx * (XL + 0.005), sy * (YL + 0.005), Z0), (sx * (XL + 0.005), sy * (YL + 0.005), ZW + 0.02), 0.045, 0.045, bev=0.004, col=GREY_W)
    # roof: gable along y, plank roof
    ang = math.atan2(0.26, XL)
    L = (XL + 0.1) / math.cos(ang) + 0.02
    for sx in (-1, 1):
        n = 6
        pw = 1.16 / n
        for k in range(n):
            y = -0.58 + (k + 0.5) * pw
            c = jitter_col(H('#7a6448'), 0.12, rr)
            cz = ZW + 0.26 - (0.5 * 0.5) * math.tan(ang) * 0.0
            Mx = Matrix.Translation((sx * (XL + 0.1) / 2, y, ZW + 0.26 + 0.02 - ((XL + 0.1) / 2) * math.tan(ang))) @ Matrix.Rotation(sx * ang, 4, 'Y')
            box('oak', None, (L, pw - 0.006, 0.026), M=Mx, bev=0.0, col=c, g=0, skip_down=False, cfn=wood_cfn(c, 0.12, 7, 90 + k, grime_z=0, axis=0))
        # battens
        for yy in (-0.57, 0.57):
            Mx = Matrix.Translation((sx * (XL + 0.1) / 2, yy, ZW + 0.26 + 0.045 - ((XL + 0.1) / 2) * math.tan(ang))) @ Matrix.Rotation(sx * ang, 4, 'Y')
            box('oak', None, (L, 0.04, 0.02), M=Mx, bev=0.002, col=GREY_W, g=0, skip_down=False)
    beam('oak', (0, -0.6, ZW + 0.285), (0, 0.6, ZW + 0.285), 0.12, 0.035, bev=0.005, col=H('#5f4a34'), up=(0, 0, 1))
    # nails on roof / wall
    for i in range(5):
        nail((-0.18 + i * 0.09, -YL - 0.016, ZW + 0.02 + 0.02 * (2 - abs(i - 2)) * 0), (0, -1, 0), r=0.006)
    # bowl with food
    lathe('plain_gloss', (0.62, -0.78, 0), [(0, 0.004), (0.08, 0.004), (0.115, 0.04), (0.125, 0.062), (0.118, 0.062), (0.105, 0.04), (0.07, 0.012), (0, 0.012)], seg=20, col=H('#6f8a9a'), cap=False, auto=False)
    lathe('food', (0.62, -0.78, 0), [(0.0, 0.04), (0.098, 0.04)], seg=16, col=H('#6a4a2a'), cap=False, auto=False)
    # bone
    bx, by = -0.62, -0.72
    cyl('plain', (bx, by, 0.02), 0.011, 0.13, axis='x', seg=8, col=H('#e6dcc2'))
    for sx in (-1, 1):
        for sy in (-1, 1):
            sphere('plain', (bx + sx * 0.068, by + sy * 0.012, 0.022), 0.015, seg=8, rings=5, col=H('#e6dcc2'))
    collider(-0.45, 0.45, -0.55, 0.55, 0.95, 0.0)


@prop('beehive_stand', '벌통 받침대', cam=lambda m: [((2.8, -2.8, 1.8), (0, 0, 0.6), 38), ((-2.6, 2.4, 1.8), (0, 0, 0.6), 38), ((0.4, -1.4, 0.8), (0.2, 0, 0.55), 45), ((-0.6, -1.0, 0.7), (-0.5, 0, 0.5), 45)])
def beehive_stand():
    CUR['ao_len'] = 0.3
    rr = random.Random(71)
    BX, BY = 0.9, 0.33
    ZT = 0.42
    gc = GREY_W
    for sx in (-1, 1):
        for sy in (-1, 1):
            zt = 1.03 if sy == -1 else 1.23
            c = jitter_col(gc, 0.1, rr)
            beam('oak', (sx * (BX - 0.04), sy * (BY - 0.02), 0), (sx * (BX - 0.04), sy * (BY - 0.02), zt), 0.08, 0.08, bev=0.006, col=c, cfn=wood_cfn(c, 0.15, 6, 3, grime_z=0.3))
    for sy in (-1, 1):
        beam('oak', (-BX, sy * BY, ZT - 0.07), (BX, sy * BY, ZT - 0.07), 0.05, 0.09, bev=0.005, col=gc)
        beam('oak', (-BX, sy * BY, 0.18), (BX, sy * BY, 0.18), 0.04, 0.06, bev=0.005, col=gc)
    for sx in (-1, 1):
        beam('oak', (sx * (BX - 0.04), -BY, 0.18), (sx * (BX - 0.04), BY, 0.18), 0.04, 0.06, bev=0.005, col=gc)
        beam('oak', (sx * (BX - 0.04), -BY + 0.02, 0.3), (sx * (BX - 0.04), BY - 0.02, 0.62), 0.03, 0.04, bev=0.003, col=gc) if False else None
    # top boards
    for i in range(4):
        y = -0.3 + i * 0.2
        c = jitter_col(H('#8f8268'), 0.1, rr)
        beam('pine', (-BX - 0.05, y, ZT), (BX + 0.05, y, ZT), 0.19, 0.035, bev=0.004, col=c, cfn=wood_cfn(c, 0.12, 6, 11 + i, grime_z=0, axis=0))
    # roof: three boards sloping to the front
    ZF_, ZB_ = 1.0, 1.2
    ang = math.atan2(ZB_ - ZF_, 0.62)
    for i in range(6):
        x = -1.05 + (i + 0.5) * 0.35
        c = jitter_col(H('#7a6448'), 0.12, rr)
        Mx = Matrix.Translation((x, 0.0 - 0.03, (ZF_ + ZB_) / 2 + 0.018)) @ Matrix.Rotation(ang, 4, 'X')
        box('oak', None, (0.345, 0.95 / math.cos(ang) * 0.95, 0.03), M=Mx, bev=0.003, col=c, g=1, skip_down=False, cfn=wood_cfn(c, 0.12, 7, 30 + i, grime_z=0, axis=1))
    for x in (-1.0, 0.0, 1.0):
        Mx = Matrix.Translation((x, -0.03, (ZF_ + ZB_) / 2 + 0.04)) @ Matrix.Rotation(ang, 4, 'X')
        box('oak', None, (0.06, 0.88, 0.03), M=Mx, bev=0.003, col=gc, g=1, skip_down=False)
    # skeps
    for si, sx in enumerate((-0.52, 0.0, 0.52)):
        sc = mixc(H('#c7a55c'), H('#b89448'), rr.random())
        prof = []
        bands = 9
        import math as _m
        def dome(t):   # t 0..1 -> (r, z)
            z = 0.43 * t
            r = 0.235 * _m.sqrt(max(0.0, 1 - (t ** 2.1))) * (1 - 0.05 * t) + 0.0
            return r, z
        nstep = bands * 2
        prof = [(0.0, 0.0), (0.2, 0.0)]
        for k in range(nstep + 1):
            t = k / nstep
            r, z = dome(t * 0.985)
            ph = (k % 2) / 2.0
            bump = 0.011 * _m.sin(_m.pi * ph) ** 0.8
            prof.append((max(0.004, r + bump), z))
        sf = lambda p, sc=sc, sx=sx: mulc_t(sc, 0.9 + 0.2 * (fbm(p.x, p.y, p.z, 40, 2, 2) * 0.5 + 0.5))
        lathe('straw', (sx, 0, ZT + 0.0175), prof, seg=16, cap=False, auto=False, cfn=sf)
        # binding spirals
        for s0 in range(1):
            pts = []
            for k in range(22):
                t = 0.02 + 0.9 * k / 21
                r, z = dome(t)
                a = s0 * TAU / 3 + t * 7.5
                pts.append(Vector((sx + _m.cos(a) * (r + 0.008), _m.sin(a) * (r + 0.008), ZT + 0.0175 + z)))
            tube('rope', pts, 0.0055, seg=4, col=H('#6a4a28'))
        # entrance (arched dark notch) and landing
        sphere('dark', (sx, -0.236, ZT + 0.07), 0.055, seg=12, rings=8, sq=(0.75, 0.14, 0.9), col=H('#120c07'))
        box('pine', (sx, -0.32, ZT + 0.022), (0.14, 0.14, 0.012), bev=0.002, col=H('#8f8268'), skip_down=False)
        # top knot
        sphere('straw', (sx, 0, ZT + 0.0175 + 0.43), 0.03, seg=8, rings=5, col=H('#a98a45'))
        # hackle cap
        for k in range(14):
            a = TAU * k / 14
            ribbon('straw', (sx + _m.cos(a) * 0.01, _m.sin(a) * 0.01, ZT + 0.0175 + 0.42), (sx + _m.cos(a) * 0.17, _m.sin(a) * 0.17, ZT + 0.0175 + 0.27), 0.03, 0.014, col=mixc(H('#d2b062'), H('#a98a45'), rr.random()), bend=(0, 0, 0.01), nseg=2, up=(0, 0, 1)) if False else None
    collider(-1.0, 1.0, -0.4, 0.4, 1.2, 0.0)


def straw_tuft(p, d, n, L, rr, spread=0.5, mat='straw'):
    p = Vector(p); d = Vector(d).normalized()
    for i in range(n):
        dd = (d + Vector((rr.uniform(-spread, spread), rr.uniform(-spread, spread), rr.uniform(-spread, spread) * 0.8))).normalized()
        l = L * rr.uniform(0.6, 1.1)
        c = mixc(H('#d6b560'), H('#a58a48'), rr.random())
        ribbon(mat, p, p + dd * l, 0.011, 0.004, col=c, bend=(0, 0, -l * 0.18), nseg=2, up=(0.3, 0.7, 0.2))


@prop('scarecrow', '허수아비', cam=lambda m: [((2.4, -3.2, 2.0), (0, 0, 1.1), 36), ((-2.4, 2.8, 2.0), (0, 0, 1.1), 36), ((0.3, -1.5, 1.8), (0, 0, 1.7), 45), ((1.4, -1.2, 1.6), (0.6, 0, 1.45), 45)])
def scarecrow():
    rr = random.Random(81)
    ZA = 1.5   # arm height
    # post and cross arm
    tube('pine', [Vector((0, 0.02, 0)), Vector((0.0, 0.02, 1.0)), Vector((0, 0.02, 1.88))], 0.04, seg=8, col=H('#7c6a50'))
    beam('oak', (-0.88, 0.02, ZA), (0.88, 0.02, ZA), 0.05, 0.05, bev=0.006, col=H('#7c6a50'))
    rope_line([(-0.05, -0.03, ZA + 0.04), (0.05, -0.03, ZA - 0.04), (-0.05, -0.03, ZA - 0.04), (0.05, -0.03, ZA + 0.04)], r=0.008) if False else None
    # shirt torso (lathe, slightly oval)
    shirt = H('#b4786a')
    sf = lambda p: mixc(shirt, H('#4f5c66'), 0.5 + 0.5 * fbm(p.x, p.y, p.z, 8, 4, 2)) if p.z > 1.0 else shirt
    prof = [(0.0, 0.88), (0.17, 0.9), (0.2, 1.0), (0.22, 1.2), (0.23, 1.38), (0.2, 1.52), (0.12, 1.6), (0.06, 1.63)]
    lathe('linen', (0, 0.02, 0), prof, seg=18, cap=False, auto=False, cfn=sf, scale=(1.0, 0.7, 1.0))
    # ragged hem strips
    for i in range(16):
        a = TAU * i / 16
        x, y = math.cos(a) * 0.17, 0.02 + math.sin(a) * 0.12
        ln = rr.uniform(0.1, 0.22)
        ribbon('linen', (x, y, 0.9), (x * 1.08, y * 1.1 + rr.uniform(-0.02, 0.02), 0.9 - ln), 0.045, 0.03, col=mixc(shirt, H('#3b464e'), rr.random() * 0.4), bend=(math.cos(a) * 0.03, math.sin(a) * 0.02, 0), nseg=2, up=(0, 0, 1))
    # patches
    box('linen', (0.12, -0.065, 1.2), (0.14, 0.018, 0.14), bev=0.003, col=H('#5f7fa0'), rot=(0, 0, 8), skip_down=False)
    box('linen', (-0.1, -0.07, 1.04), (0.1, 0.012, 0.09), bev=0.003, col=H('#b8a060'), rot=(0, 0, -6), skip_down=False)
    # rope belt
    lathe('rope', (0, 0.02, 0), [(0.176, 1.02), (0.188, 1.02), (0.19, 1.06), (0.178, 1.06)], seg=18, cap=False, auto=False, col=ROPE_C, scale=(1.0, 0.7, 1.0))
    # sleeves along arm
    for sx in (-1, 1):
        a0 = Vector((sx * 0.14, 0.02, ZA + 0.04))
        a1 = Vector((sx * 0.74, 0.02, ZA - 0.03))
        d = (a1 - a0)
        Ms = Matrix.Translation(a0) @ Matrix.Rotation(sx * math.pi / 2, 4, 'Y') @ Matrix.Rotation(math.radians(-5) * sx, 4, 'X')
        # lathe axis z -> along x
        sleeve_prof = [(0.09, 0.0), (0.085, 0.2), (0.075, 0.45), (0.074, 0.6)]
        lathe('linen', None, sleeve_prof, seg=12, M=Matrix.Translation(a0) @ Matrix.Rotation(sx * math.pi / 2, 4, 'Y'), cap=True, auto=False,
              cfn=lambda p: mixc(shirt, H('#4f5c66'), 0.5 + 0.5 * fbm(p.x, p.y, p.z, 9, 6, 2)))
        # cuff tatters + straw hands
        for i in range(7):
            a = TAU * i / 7
            ribbon('linen', (sx * 0.74, 0.02 + math.cos(a) * 0.05, ZA - 0.03 + math.sin(a) * 0.05), (sx * (0.8 + rr.uniform(0, 0.05)), 0.02 + math.cos(a) * 0.07, ZA - 0.03 + math.sin(a) * 0.07 - rr.uniform(0.04, 0.1)), 0.035, 0.02, col=shirt, up=(1, 0, 0))
        straw_tuft((sx * 0.74, 0.02, ZA - 0.03), (sx, 0, -0.1), 16, 0.18, rr, 0.4)
    # trousers
    pant = H('#8a7456')
    for sx in (-1, 1):
        lathe('burlap', (sx * 0.07, 0.02, 0.0), [(0.0, 0.42), (0.085, 0.44), (0.09, 0.7), (0.095, 0.93), (0.0, 0.94)], seg=12, cap=False, auto=False,
              cfn=lambda p: mixc(pant, H('#5e4c36'), 0.5 + 0.5 * fbm(p.x, p.y, p.z, 9, 8, 2)))
        straw_tuft((sx * 0.07, 0.02, 0.44), (0, 0, -1), 14, 0.1, rr, 0.5)
        for i in range(6):
            a = TAU * i / 6
            ribbon('burlap', (sx * 0.07 + math.cos(a) * 0.085, 0.02 + math.sin(a) * 0.085, 0.44), (sx * 0.07 + math.cos(a) * 0.1, 0.02 + math.sin(a) * 0.1, 0.44 - rr.uniform(0.04, 0.1)), 0.04, 0.02, col=pant, up=(0, 0, 1))
    box('burlap', (0.1, -0.075, 0.72), (0.1, 0.012, 0.1), bev=0.003, col=H('#6c8a58'), skip_down=False)
    # straw from hem, collar
    straw_tuft((0, 0.0, 0.9), (0, 0, -1), 22, 0.2, rr, 0.8)
    straw_tuft((0, 0.02, 1.62), (0, 0, 1), 26, 0.12, rr, 0.6)
    # head: burlap sack
    hc = (0, 0.02, 1.78)
    bf = lambda p: mixc(H('#b4966a'), H('#8f7448'), 0.5 + 0.5 * fbm(p.x, p.y, p.z, 14, 2, 2))
    prof = [(0.0, -0.13), (0.07, -0.125), (0.115, -0.07), (0.135, 0.0), (0.12, 0.08), (0.08, 0.13), (0.03, 0.15), (0.0, 0.155)]
    lathe('burlap', hc, prof, seg=16, cap=False, auto=False, cfn=bf, scale=(1.0, 0.95, 1.0))
    # tied-off knot
    sphere('burlap', (0, 0.02, 1.935), 0.03, seg=8, rings=5, col=H('#a58858'))
    for k in range(5):
        ribbon('burlap', (0, 0.02, 1.935), (rr.uniform(-0.05, 0.05), 0.02 + rr.uniform(-0.05, 0.05), 1.99 + rr.uniform(0, 0.03)), 0.02, 0.008, col=H('#a58858'))
    # neck rope
    lathe('rope', hc, [(0.07, -0.115), (0.085, -0.115), (0.087, -0.095), (0.07, -0.095)], seg=12, cap=False, auto=False, col=ROPE_C)
    # eyes (stitched buttons), nose bump, mouth stitches
    for sx in (-1, 1):
        sphere('plain', (sx * 0.05, -0.1, 1.82), 0.022, seg=10, rings=6, sq=(1, 0.5, 1), col=H('#1b1612'))
        sphere('plain', (sx * 0.05, -0.115, 1.822), 0.008, seg=6, rings=4, col=H('#d8d0c0'))
    sphere('burlap', (0, -0.125, 1.775), 0.03, seg=10, rings=6, sq=(0.9, 1.0, 1.1), col=H('#a88c5e'))
    mp = [Vector((-0.07 + 0.14 * k / 8, -0.115 + 0.01 * math.sin(math.pi * k / 8) * 0, 1.715 + 0.02 * (math.cos(math.pi * k / 8 * 2 - math.pi) * 0.5 + 0.5) * 0.0 - 0.02 * math.sin(math.pi * k / 8))) for k in range(9)]
    tube('rope', mp, 0.0035, seg=4, col=H('#2a1e14'))
    for k in range(5):
        x = -0.06 + 0.03 * k
        tube('rope', [Vector((x, -0.118, 1.71)), Vector((x, -0.118, 1.74))], 0.003, seg=4, col=H('#2a1e14'))
    # straw hat
    hatc = lambda p: mixc(H('#c8a65a'), H('#9a7e3c'), 0.5 + 0.5 * fbm(p.x, p.y, p.z, 30, 3, 2))
    hz = 1.88
    brim = [(0.0, 0.0), (0.16, 0.0), (0.26, -0.01), (0.38, -0.045), (0.43, -0.09), (0.42, -0.095), (0.37, -0.055), (0.26, -0.022), (0.16, -0.015), (0.0, -0.015)]
    lathe('straw', (0, 0.02, hz), [(0.13, 0.0), (0.13, 0.1), (0.115, 0.14), (0.06, 0.155), (0.0, 0.16)], seg=20, cap=False, auto=False, cfn=hatc)
    lathe('straw', (0.03, 0.02, hz - 0.02), [(0.12, 0.0), (0.2, 0.01), (0.3, -0.005), (0.4, -0.04), (0.44, -0.085), (0.435, -0.095), (0.39, -0.055), (0.3, -0.022), (0.2, -0.018), (0.12, -0.02)], seg=28, cap=False, auto=False, cfn=hatc, scale=(1.0, 0.9, 1.0))
    lathe('linen', (0, 0.02, hz), [(0.131, 0.015), (0.138, 0.015), (0.138, 0.05), (0.131, 0.05)], seg=20, cap=False, auto=False, col=H('#7a3f32'))
    # frayed brim straw
    for i in range(16):
        a = TAU * i / 16
        straw_tuft((0.03 + math.cos(a) * 0.43, 0.02 + math.sin(a) * 0.4, hz - 0.1), (math.cos(a), math.sin(a), -0.3), 1, 0.06, rr, 0.3)
    # crow on right arm
    cx, cy, cz = 0.55, 0.02, ZA + 0.04
    bcol = H('#16161a')
    sphere('plain_gloss', (cx, cy, cz + 0.09), 0.065, seg=12, rings=8, sq=(0.75, 1.5, 1.0), col=bcol, rot=(math.radians(-25), 0, 0))
    sphere('plain_gloss', (cx, cy - 0.095, cz + 0.17), 0.04, seg=10, rings=6, col=bcol)
    lathe('plain', None, [(0.016, 0.0), (0.011, 0.04), (0.0, 0.09)], seg=6, M=Matrix.Translation((cx, cy - 0.125, cz + 0.17)) @ Matrix.Rotation(math.radians(100), 4, 'X'), col=H('#2a2a2e'), cap=False, auto=False)
    ribbon('plain_gloss', (cx, cy + 0.05, cz + 0.07), (cx, cy + 0.2, cz + 0.02), 0.06, 0.04, col=bcol, nseg=1, up=(1, 0, 0))
    for dx in (-0.02, 0.02):
        tube('plain', [Vector((cx + dx, cy - 0.01, cz + 0.05)), Vector((cx + dx, cy - 0.01, cz + 0.0))], 0.004, seg=4, col=H('#3a3a3a'))
    sphere('plain', (cx + 0.025, cy - 0.11, cz + 0.178), 0.007, seg=6, rings=4, col=H('#d8d0b0'))
    collider(-0.9, 0.9, -0.12, 0.16, 2.1, 0.0)


def leaf4(mat, c, size, rot, col):
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    L, W = size
    pts = [(0, 0, -L * 0.5), (W * 0.5, 0, 0), (0, 0, L * 0.5), (-W * 0.5, 0, 0)]
    f = bm.faces.new([bm.verts.new(p) for p in pts])
    f.smooth = False
    for l in f.loops:
        l[ul].uv = (l.vert.co.x / W + 0.5, l.vert.co.z / L + 0.5)
    put(mat, bm, Matrix.Translation(Vector(c)) @ Euler(rot, 'XYZ').to_matrix().to_4x4(), col, None, 2, flat=True)
    bm.free()


# ------------------------------------------------------------------ apple tree
@prop('apple_tree_small', '사과나무', cam=lambda m: [((5.5, -6.5, 2.6), (0, 0, 1.9), 36), ((-6.0, 5.0, 2.8), (0, 0, 1.9), 36), ((1.6, -2.4, 1.8), (0.2, 0, 1.6), 45), ((0.3, -1.1, 0.8), (0.1, 0, 0.5), 45)])
def apple_tree_small():
    CUR['ao_len'] = 0.8
    rr = random.Random(91)
    barkc = H('#6e5e4c')
    clusters = []     # (pos, dirvec, radius)
    tips = []

    def tube_path(pts, r0, r1, seg):
        n = len(pts)
        tube('bark', pts, r0, seg=seg, col=barkc, cfn=lambda p: mixc(barkc, H('#4a3d30'), 0.5 + 0.5 * fbm(p.x, p.y, p.z, 7, 3, 2)), taper=lambda t: 1 - (1 - r1 / r0) * t, uvm=1.0, caps=True)

    def grow(p, d, L, r0, depth, up_bias):
        n = 3 if depth < 3 else 2
        pts = [Vector(p)]
        dd = Vector(d).normalized()
        for i in range(n):
            dd = (dd + Vector((rr.uniform(-0.28, 0.28), rr.uniform(-0.28, 0.28), rr.uniform(-0.1, 0.1) + up_bias))).normalized()
            pts.append(pts[-1] + dd * (L / n))
        r1 = r0 * (0.55 if depth < 3 else 0.4)
        tube_path(pts, r0, r1, 7 if r0 > 0.03 else (5 if r0 > 0.012 else 4))
        if depth >= 2:
            tips.append((pts[-1], dd))
            if depth == 2:
                tips.append((pts[-2], dd))
        if depth < 3:
            nc = 3 if depth == 0 else 2
            for k in range(nc):
                t = 0.45 + 0.5 * (k + rr.random() * 0.5) / nc
                i = min(n - 1, int(t * n))
                base = pts[i].lerp(pts[i + 1], t * n - i)
                side = Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-0.1, 0.5)))
                cd = (dd * 0.7 + side).normalized()
                grow(base, cd, L * rr.uniform(0.55, 0.75), r0 * rr.uniform(0.5, 0.62), depth + 1, up_bias * 0.4 - 0.02)
            if depth <= 1:
                grow(pts[-1], dd, L * 0.5, r0 * 0.55, depth + 1, up_bias * 0.6)
    # trunk (leaning slightly, flared base)
    tpts = [Vector((0, 0, -0.05)), Vector((0.0, 0.0, 0.25)), Vector((0.03, 0.02, 0.6)), Vector((0.02, 0.04, 0.95)), Vector((0.0, 0.04, 1.12))]
    tube_path(polyline_smooth(tpts, 2), 0.18, 0.1, 12)
    # root flare
    for k in range(4):
        a = TAU * k / 4 + 0.3
        pts = [Vector((math.cos(a) * 0.28, math.sin(a) * 0.28, 0.0)), Vector((math.cos(a) * 0.17, math.sin(a) * 0.17, 0.1)), Vector((math.cos(a) * 0.1, math.sin(a) * 0.1, 0.35))]
        tube_path(pts, 0.04, 0.025, 6)
    top = Vector((0.0, 0.04, 1.02))
    for k in range(5):
        a = TAU * k / 5 + rr.uniform(-0.3, 0.3)
        d = Vector((math.cos(a) * 0.8, math.sin(a) * 0.8, 0.8 + rr.uniform(-0.1, 0.25)))
        grow(top + Vector((0, 0, rr.uniform(-0.05, 0.1))), d, rr.uniform(1.2, 1.45), 0.085, 0, 0.1)
    # centre leader
    grow(top, Vector((0.05, 0.0, 1.0)), 1.3, 0.075, 1, 0.1)
    # ----- leaves
    leafn = 0
    nleaf = 1050
    per = max(4, nleaf // max(1, len(tips)))
    for (tp, d) in tips:
        base_c = mixc(H('#4a7d2c'), H('#7aa03e'), rr.random())
        for k in range(per):
            off = Vector((rr.gauss(0, 0.15), rr.gauss(0, 0.15), rr.gauss(0, 0.11))) + d * rr.uniform(-0.15, 0.2)
            pos = tp + off
            if pos.z < 1.2:
                continue
            c = mixc(base_c, H('#9db44a') if rr.random() < 0.2 else H('#2f5a22'), rr.random() * 0.35)
            c = jitter_col(c, 0.08, rr)
            leaf4('leaf', pos, (rr.uniform(0.14, 0.19), rr.uniform(0.08, 0.105)), (rr.uniform(0, math.pi), rr.uniform(0, math.pi), rr.uniform(0, TAU)), c)
            leafn += 1
    # ----- apples
    n_ap = 0
    for (tp, d) in tips:
        if rr.random() < 0.13 and tp.z > 1.5:
            ap = tp + Vector((rr.uniform(-0.18, 0.18), rr.uniform(-0.18, 0.18), -rr.uniform(0.06, 0.18)))
            col = H('#b8312a') if rr.random() < 0.65 else H('#a8b840')
            col = jitter_col(col, 0.12, rr)
            sphere('plain_gloss', ap, 0.042, seg=6, rings=4, sq=(1, 1, 0.92), col=col, cfn=lambda p, col=col, ap=ap: mixc(col, H('#d8a040'), max(0.0, 0.5 + (p.x - ap.x) / 0.1) * 0.25))
            tube('bark', [ap + Vector((0, 0, 0.03)), ap + Vector((0.0, 0.0, 0.07)), tp.lerp(ap, 0.1) + Vector((0, 0, 0.02))], 0.0025, seg=4, col=H('#4a3d2a'))
            n_ap += 1
    # fallen apples
    for i in range(7):
        a = rr.uniform(0, TAU)
        r = rr.uniform(0.4, 1.4)
        col = H('#b8312a') if rr.random() < 0.6 else H('#a8b840')
        sphere('plain_gloss', (math.cos(a) * r, math.sin(a) * r, 0.036), 0.042, seg=6, rings=4, sq=(1, 1, 0.9), col=jitter_col(col, 0.12, rr))
    # a few fallen leaves
    for i in range(14):
        a = rr.uniform(0, TAU)
        r = rr.uniform(0.3, 1.6)
        leafquad('leaf', (math.cos(a) * r, math.sin(a) * r, 0.006), (0.1, 0.06), (math.pi / 2 + rr.uniform(-0.1, 0.1), 0, rr.uniform(0, TAU)), col=mixc(H('#a8a040'), H('#7a6a30'), rr.random()))
    print('apple tree leaves', leafn, 'apples', n_ap, 'tips', len(tips))
    collider(-0.22, 0.22, -0.22, 0.22, 3.5, 0.0)


# ------------------------------------------------------------------ rowboat
BL = 1.8      # half length
def hull_B(s):   # half beam at station s (-1..1)
    return 0.66 * max(0.0, 1 - abs(s) ** 2.3) ** 0.62


def hull_zb(s):
    return 0.17 + 0.16 * s * s


def hull_zt(s):
    return 0.17 + 0.62 + 0.22 * abs(s) ** 2.2 + 0.0 * s


def hull_pt(s, f, off=0.0):
    """outer hull point (y>=0 side) at station s and height fraction f (0 keel..1 sheer), offset along outward normal"""
    zb, zt = hull_zb(s), hull_zt(s)
    B = hull_B(s)
    y = B * math.sin(f * math.pi / 2) ** 0.75 * (1 + 0.08 * f)
    z = zb + (zt - zb) * f
    # approx outward normal in section
    dy = B * 0.75 * math.sin(f * math.pi / 2) ** -0.25 * math.cos(f * math.pi / 2) * math.pi / 2 if 0 < f < 1 else 0
    dz = (zt - zb)
    n = Vector((0, dz, -dy)).normalized() if f > 0.02 else Vector((0, 0.3, -1)).normalized()
    return Vector((BL * s, y, z)) + n * off


def strake_bm(sy, f0, f1, t=0.022, nst=16, s0=-1.0, s1=1.0, o_lo=0.011, o_hi=-0.004):
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    rings = []
    for i in range(nst + 1):
        s = s0 + (s1 - s0) * i / nst
        # shorten at stem so strakes meet the post
        s = max(-0.985, min(0.985, s))
        p_ol = hull_pt(s, f0, o_lo); p_oh = hull_pt(s, f1, o_hi)
        p_il = hull_pt(s, f0, o_lo - t); p_ih = hull_pt(s, f1, o_hi - t)
        ring = []
        for p in (p_ol, p_oh, p_ih, p_il):
            ring.append(bm.verts.new((p.x, p.y * sy, p.z)))
        rings.append(ring)
    for i in range(nst):
        for k in range(4):
            k2 = (k + 1) % 4
            f = bm.faces.new((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]))
            f.material_index = k
            f.smooth = True
            for l in f.loops:
                l[ul].uv = (l.vert.co.x, l.vert.co.z)
    for ring, rev in ((rings[0], True), (rings[-1], False)):
        f = bm.faces.new(ring[::-1] if rev else ring)
        f.material_index = 4
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def split_faces(bm, keep):
    b2 = bm.copy()
    dele = [f for f in b2.faces if f.material_index not in keep]
    bmesh.ops.delete(b2, geom=dele, context='FACES_ONLY')
    return b2


@prop('rowboat', '나룻배', cam=lambda m: [((4.6, -4.4, 2.6), (0, 0, 0.5), 36), ((-4.4, 3.8, 2.8), (0, 0, 0.5), 36), ((0.3, -3.0, 1.6), (0.0, 0.0, 0.35), 45), ((0.5, 0.0, 3.8), (0.2, 0.0, 0.2), 45)])
def rowboat():
    rr = random.Random(101)
    paint = H('#6f8c86')
    paint2 = H('#7d4a3a')
    bare = H('#9a845f')
    N = 6
    for sy in (-1, 1):
        for k in range(N):
            f0 = k / N * 0.97 + 0.03 * (1 if k > 0 else 0)
            f0 = k / N
            f1 = (k + 1) / N
            bm = strake_bm(sy, f0, f1)
            seedc = rr.random()
            pc = paint if k < N - 1 else paint2
            pc = jitter_col(pc, 0.08, rr)
            cf_o = lambda p, pc=pc: mixc(pc, H('#4a4a40'), max(0, 0.5 + 0.5 * fbm(p.x, p.y, p.z, 10, 3, 3) - 0.35) * 0.6 + max(0.0, (0.3 - p.z) * 1.5))
            cf_i = lambda p: mixc(bare, H('#6a5a40'), 0.5 + 0.5 * fbm(p.x, p.y, p.z, 8, 7, 2))
            b_out = split_faces(bm, (0, 3, 1))
            b_in = split_faces(bm, (2, 4))
            bm.free()
            put('pine', b_out, Matrix.Identity(4), (1, 1, 1), cf_o, 0)
            put('pine', b_in, Matrix.Identity(4), (1, 1, 1), cf_i, 0)
            b_out.free(); b_in.free()
    # keel
    kp = [Vector((BL * s, 0, hull_zb(s) - 0.012)) for s in [x / 7 * 0.98 for x in range(-7, 8)]]
    sweep('dark', [(-0.04, -0.03), (0.04, -0.03), (0.04, 0.03), (-0.04, 0.03)], kp, up=(0, 0, 1), col=H('#3b2e22'), caps=True, uvm=1.0)
    # stem / stern posts
    for sx in (-1, 1):
        pp = []
        for k in range(9):
            t = k / 8
            s = 0.93 + 0.07 * t
            z = hull_zb(0.93) + (hull_zt(1.0) + 0.04 - hull_zb(0.93)) * t ** 0.9
            pp.append(Vector((sx * (BL * 0.93 + (BL * 0.07 + 0.02) * t ** 1.8), 0, z)))
        sweep('oak', [(-0.03, -0.045), (0.03, -0.045), (0.03, 0.045), (-0.03, 0.045)], pp, up=(0, 1, 0), col=H('#5e4c36'), caps=True)
    # gunwales (outer rail + inner rail)
    for sy in (-1, 1):
        for (off, w, hh, c) in ((0.02, 0.05, 0.03, H('#6a5a44')), (-0.045, 0.04, 0.025, H('#7a6848'))):
            pts = []
            for i in range(17):
                s = -0.975 + 1.95 * i / 16
                p = hull_pt(s, 1.0, off)
                pts.append(Vector((p.x, p.y * sy, p.z + 0.012)))
            sweep('oak', [(-w / 2, -hh / 2), (w / 2, -hh / 2), (w / 2, hh / 2), (-w / 2, hh / 2)], pts, up=(0, 0, 1), col=c, caps=True)
    # ribs
    for xi in range(-4, 5):
        s = xi * 0.21
        if abs(s) > 0.9:
            continue
        pts = []
        for k in range(15):
            f = 0.0 + 0.96 * k / 14
            for sy in (1,):
                pass
        left = [hull_pt(s, 0.96 * k / 5, -0.03) for k in range(6)]
        path = [Vector((p.x, -p.y, p.z)) for p in left[::-1]] + [Vector((p.x, p.y, p.z)) for p in left[1:]]
        sweep('oak', [(-0.02, -0.015), (0.02, -0.015), (0.02, 0.015), (-0.02, 0.015)], path, up=(1, 0, 0), col=jitter_col(H('#8a7450'), 0.1, rr), caps=True)
    # floorboards
    for yi, w in ((-0.2, 0.17), (0.0, 0.2), (0.2, 0.17)):
        zf = hull_zb(0.0) + 0.045
        pts = [Vector((BL * s, yi, hull_zb(s) + 0.05)) for s in [x / 3 * 0.7 for x in range(-3, 4)]]
        sweep('pine', [(-w / 2 + 0.005, -0.012), (w / 2 - 0.005, -0.012), (w / 2 - 0.005, 0.012), (-w / 2 + 0.005, 0.012)], pts, up=(0, 0, 1), col=jitter_col(H('#8f7a56'), 0.1, rr), caps=True)
    # thwarts + knees
    for xs in (-0.85, 0.05, 0.85):
        s = xs / BL
        zt_ = hull_zb(s) + 0.37
        hw = hull_pt(s, (zt_ - hull_zb(s)) / (hull_zt(s) - hull_zb(s)), -0.04).y
        box('pine', (xs, 0, zt_), (0.24, 2 * hw, 0.03), bev=0.004, col=H('#8a7550'), cfn=wood_cfn(H('#8a7550'), 0.12, 6, int(xs * 10) + 20, grime_z=0, axis=1), g=1, skip_down=False)
        for sy in (-1, 1):
            beam('oak', (xs - 0.1, sy * (hw - 0.06), zt_ - 0.03), (xs - 0.1, sy * (hw - 0.01), zt_ - 0.15), 0.03, 0.05, bev=0.003, col=H('#6f5c40'), up=(1, 0, 0)) if False else None
            fk = (zt_ - 0.07 - hull_zb(s)) / (hull_zt(s) - hull_zb(s))
            yk = hull_pt(s, fk, -0.05).y - 0.012
            box('oak', (xs, sy * yk, zt_ - 0.07), (0.2, 0.035, 0.1), bev=0.004, col=H('#6f5c40'), skip_down=False)
    # rowlocks (thole pins + blocks)
    for (xs, sy) in ((-0.2, 1), (-0.2, -1), (0.45, 1), (0.45, -1)):
        s = xs / BL
        p = hull_pt(s, 1.0, 0.0)
        box('oak', (xs, sy * (p.y - 0.045), p.z + 0.035), (0.14, 0.03, 0.04), bev=0.004, col=H('#6a5a44'), skip_down=False)
        for dx in (-0.045, 0.045):
            cyl('plain', (xs + dx, sy * (p.y - 0.045), p.z + 0.1), 0.012, 0.13, axis='z', seg=8, col=H('#3a3a3e'))
    # bow ring + rope
    pz = hull_zt(1.0)
    torus('iron_dark', (BL + 0.03, 0, pz - 0.14), 0.035, 0.007, plane='xz', seg=14, rseg=5, col=IRON_C)
    rp = [Vector((BL + 0.03, 0, pz - 0.14)), Vector((BL - 0.05, 0.02, pz - 0.25)), Vector((BL - 0.35, 0.06, hull_zb(0.8) + 0.12)), Vector((BL - 0.6, 0.05, hull_zb(0.7) + 0.075))]
    rope_line(rp, r=0.013)
    coil_rope(Matrix.Translation((BL - 0.8, 0.02, hull_zb(0.55) + 0.04)), 0.14, r=0.013, turns=3)
    # oars lying across on thwarts
    for k, (yy, dirv) in enumerate(((0.26, 1), (-0.26, -1))):
        zt_ = hull_zb(0.0) + 0.37 + 0.03
        x0, x1 = -1.1, 1.25
        if dirv < 0:
            x0, x1 = -1.25, 1.1
        a = Vector((x0, yy, zt_ + 0.012 + 0.01)); b = Vector((x1, yy, zt_ + 0.012 + 0.01))
        # loom
        tube('pine', [a, a.lerp(b, 0.5), b], 0.019, seg=8, col=H('#a08a62'), taper=lambda t: 1.0)
        # leather sleeve
        mid = a.lerp(b, 0.55 if dirv > 0 else 0.45)
        cyl('plain', (mid.x, mid.y, mid.z), 0.026, 0.24, axis='x', seg=10, col=H('#4b3523'))
        # blade at +dirv end
        bx = x1 if dirv > 0 else x0
        sgn = 1 if dirv > 0 else -1
        box('pine', (bx - sgn * 0.27, yy, zt_ + 0.022), (0.56, 0.13, 0.016), bev=0.004, col=H('#b09a70'), cfn=wood_cfn(H('#b09a70'), 0.1, 6, 5 + k, grime_z=0), g=0, skip_down=False, taper=None)
        box('pine', (bx - sgn * 0.5, yy, zt_ + 0.022), (0.2, 0.05, 0.02), bev=0.003, col=H('#a08a62'), skip_down=False)
        # grip
        cyl('plain', (a.x if dirv > 0 else b.x, yy, zt_ + 0.022), 0.024, 0.16, axis='x', seg=10, col=H('#7a6342'))
    # support logs
    for xs in (-0.75, 0.75):
        cyl('bark', (xs, 0, 0.075), 0.085, 1.0, axis='y', seg=12, col=H('#5e5040'))
        box('oak', (xs + 0.15, 0.0, 0.03), (0.1, 0.12, 0.06), bev=0.004, col=H('#5e5040'), rot=(0, 0, 0), skip_down=False)
    collider(-1.85, 1.85, -0.7, 0.7, 0.95, 0.0)
