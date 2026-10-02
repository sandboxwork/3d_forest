"""Trunk, rocking chair (+knitted shawl sim), washstand (+towel sim), wall shelf with trinkets."""
from bd_lib import *
from bd_hw import *
from bd_bed import fielded_panel, spiral, leaf2d, boolean_diff
from bd_furn import bracket_foot
from bd_cloth import *
import bd_items as I


def trunk(pos, rot, W=1.0, D=0.48, H=0.46):
    f = Fr(pos, rot, F)
    mat = M['wood_dark']
    col = (1.0, 0.92, 0.84)
    iron = M['iron']
    bh = 0.3
    # base: stacked planks (visible seams) with iron-banded corners
    nb = 4
    for i in range(nb):
        hb = bh / nb
        f.box(mat, (0, 0, 0.03 + hb * (i + 0.5) - 0.0 + 0.0), (W, D, hb - 0.003), bev=0.003, col=jit(col, 0.06), g=0)
    f.box(mat, (0, 0, 0.0225 + 0.0), (W - 0.04, D - 0.04, 0.03), bev=0.003, col=(0.7, 0.62, 0.55), g=0)
    # block feet
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.box(mat, (sx * (W / 2 - 0.045), sy * (D / 2 - 0.045), 0.02), (0.08, 0.08, 0.04), bev=0.005, col=(0.8, 0.72, 0.64))
    # lid: arched cross-section (yz), extruded along x
    rise = H - bh - 0.03
    R = (D * D / 4 + rise * rise) / (2 * rise)
    n = 16
    outer, inner = [], []
    th0 = math.asin((D / 2) / R)
    for i in range(n + 1):
        a = -th0 + 2 * th0 * i / n
        outer.append((R * math.sin(a), (R * math.cos(a)) - R + rise))
    for i in range(n, -1, -1):
        a = -th0 + 2 * th0 * i / n
        inner.append(((R - 0.02) * math.sin(a), ((R - 0.02) * math.cos(a)) - R + rise))
    zl = 0.03 + bh
    f.prism(mat, outer + inner, W, c=(0, 0, zl), plane='yz', col=col, bev=0.003, g=0)
    # iron bands: ring segments + vertical straps on the body
    for x in (-W / 2 + 0.07, 0.0, W / 2 - 0.07):
        outer_b, inner_b = [], []
        for i in range(n + 1):
            a = -th0 + 2 * th0 * i / n
            outer_b.append(((R + 0.004) * math.sin(a), ((R + 0.004) * math.cos(a)) - R + rise))
        for i in range(n, -1, -1):
            a = -th0 + 2 * th0 * i / n
            inner_b.append(((R - 0.001) * math.sin(a), ((R - 0.001) * math.cos(a)) - R + rise))
        f.prism(iron, outer_b + inner_b, 0.042, c=(x, 0, zl), plane='yz', bev=0.0008)
        # vertical strap on front/back faces + wrap-around
        for sy in (-1, 1):
            f.box(iron, (x, sy * (D / 2 + 0.002), 0.03 + bh / 2), (0.042, 0.005, bh), bev=0.0008)
        # rivets along the strap
        for k in range(0, 5, 2):
            for sy in (-1, 1):
                f.sphere(iron, (x, sy * (D / 2 + 0.0055), 0.07 + k * 0.058), 0.0045, seg=6, rings=3, sq=(1, 0.55, 1))
        for i in range(2, n - 1, 5):
            a = -th0 + 2 * th0 * i / n
            f.sphere(iron, (x - 0.014, (R + 0.0045) * math.sin(a), zl + ((R + 0.0045) * math.cos(a)) - R + rise), 0.0042, seg=8, rings=4)
            f.sphere(iron, (x + 0.014, (R + 0.0045) * math.sin(a), zl + ((R + 0.0045) * math.cos(a)) - R + rise), 0.0042, seg=8, rings=4)
    # corner brackets on the box
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.box(iron, (sx * (W / 2 - 0.0), sy * (D / 2 - 0.0), 0.075), (0.012, 0.07, 0.11), bev=0.001) if False else None
            f.box(iron, (sx * (W / 2 + 0.0015), sy * (D / 2 - 0.035), 0.075), (0.004, 0.07, 0.11), bev=0.001)
            f.box(iron, (sx * (W / 2 - 0.035), sy * (D / 2 + 0.0015), 0.075), (0.07, 0.004, 0.11), bev=0.001)
    # hasp, lock plate, keyhole (front = +y local)
    yf = D / 2 + 0.003
    f.box(iron, (0, yf, 0.03 + bh - 0.03), (0.07, 0.006, 0.14), bev=0.002)
    f.box(M['brass'], (0, yf + 0.004, 0.03 + bh * 0.55), (0.07, 0.006, 0.09), bev=0.002)
    escutcheon(f, (0, yf + 0.0075, 0.03 + bh * 0.55), h=0.06, w=0.034, face=1)
    f.box(iron, (0, yf + 0.003, zl + 0.04), (0.04, 0.004, 0.12), bev=0.0008)
    f.cyl(iron, (0, yf + 0.006, zl + 0.01), 0.012, 0.01, axis='y', seg=10)
    # leather end handles with iron staples
    for sx in (-1, 1):
        x = sx * (W / 2 + 0.003)
        f.box(iron, (x, 0, 0.19), (0.004, 0.05, 0.016), bev=0.001)
        pts = [Vector(p) for p in [(x, -0.07, 0.19), (x + sx * 0.03, -0.06, 0.18), (x + sx * 0.05, -0.04, 0.165), (x + sx * 0.052, 0.0, 0.158), (x + sx * 0.05, 0.04, 0.165), (x + sx * 0.03, 0.06, 0.18), (x, 0.07, 0.19)]]
        f.tube(M['leather'], [Vector(q) for q in catmull([(p.x, p.y, p.z) for p in pts], 3)], 0.011, seg=8, col=(0.45, 0.28, 0.17), flat=(1.0, 0.6))
        for yy in (-0.07, 0.07):
            f.cyl(iron, (x, yy, 0.19), 0.008, 0.01, axis='x', seg=8)
    collider_f(f, W + 0.12, D + 0.04, F + H + 0.01, name='trunk')
    # contents on top: folded quilt + book
    soft_box(M['wool'], f._m((-0.22, 0.0, H + 0.02)), (0.4, 0.3, 0.04), col=(0.7, 0.3, 0.25), disp=0.003)
    soft_box(M['wool'], f._m((-0.22, 0.0, H + 0.057)), (0.38, 0.28, 0.036), col=(0.88, 0.82, 0.68), disp=0.003)
    soft_box(M['wool'], f._m((-0.22, 0.0, H + 0.09)), (0.36, 0.27, 0.034), col=(0.32, 0.4, 0.5), disp=0.003)
    return f


# ---------------------------------------------------------------- rocking chair
def rocker_proxies(f):
    out = []
    out.append(box_collider((0, 0.0, 0.43), (0.5, 0.46, 0.04)))
    out.append(box_collider((0, -0.22, 0.75), (0.46, 0.04, 0.6), bev=0.0))
    for sx in (-1, 1):
        out.append(box_collider((sx * 0.25, 0.05, 0.66), (0.05, 0.42, 0.04)))
        out.append(box_collider((sx * 0.24, 0.2, 0.55), (0.03, 0.03, 0.22)))
    out.append(box_collider((0, 0, -0.05), (3, 3, 0.1)))
    out.append(box_collider((0, 0.0, 0.2), (0.5, 0.45, 0.4)))
    return out


def rocking_chair(pos, rot, shawl=True):
    f = Fr(pos, rot, F)
    mat = M['wood_dark']
    col = (1.0, 0.92, 0.84)
    R_ = 0.9
    # rockers: curved runner profile
    for sx in (-1, 1):
        x = sx * 0.25
        top, bot = [], []
        for i in range(21):
            y = -0.5 + 1.0 * i / 20
            zc = 0.075 - (R_ - math.sqrt(R_ * R_ - y * y)) * -1.0 * 0 + 0.0
            z0 = 0.075 + (R_ - math.sqrt(max(R_ * R_ - (y * 1.0) ** 2, 0))) * -1.0
            zb = 0.07 * 0 + (1 - math.sqrt(1 - min((y / 0.52) ** 2, 0.999))) * 0.0
            bot.append((y, 0.14 * (y / 0.5) ** 2 * 0.55 + 0.0))
        curve_bar(mat, [(y + 0.5, 0.0, z) for y, z in bot], 0.03, 0.032, f._m((x, -0.5, 0.0), (0, 0, 90)) @ Matrix.Translation((0, 0, 0.015)), col=col)
        # the rocker tips curl up with a small turned knob
        for sy in (-1, 1):
            f.sphere(mat, (x, sy * 0.5, 0.14 * 0.55 + 0.03), 0.016, seg=10, col=col)
        # legs: tapered/turned, splayed outward
        for yy, top_z in ((0.2, 0.43), (-0.2, 0.43)):
            zb = 0.14 * (yy / 0.5) ** 2 * 0.55 + 0.03
            path = [Vector((x * (1 + 0.04 * t), yy, zb + (top_z - zb) * t)) for t in np.linspace(0, 1, 10)]
            rr = [0.015, 0.016, 0.02, 0.017, 0.014, 0.014, 0.02, 0.017, 0.015, 0.016]
            f.tube(mat, path, rr, seg=10, col=col)
        f.tube(mat, [Vector((sx * 0.235, -0.2, 0.2)), Vector((sx * 0.235, 0.2, 0.2))], 0.0085, seg=8, col=col)
    f.tube(mat, [Vector((-0.235, 0.0, 0.21)), Vector((0.235, 0.0, 0.21))], 0.008, seg=8, col=col)
    # saddle seat (oval dish)
    prof = profile_pts([(0.0005, -0.01), (0.12, -0.014), (0.2, -0.006), (0.25, 0.012), (0.26, 0.03), (0.0005, 0.0)], 3)
    f.lathe(mat, (0, 0.0, 0.41), prof, seg=32, cap=False, col=col, scale=(1.0, 0.92, 1.0))
    f.box(mat, (0, 0.0, 0.402), (0.46, 0.42, 0.02), bev=0.005, col=col)
    # back posts + spindles + crest rail
    for sx in (-1, 1):
        path = [Vector((sx * 0.215, -0.19 - 0.12 * t, 0.43 + 0.62 * t)) for t in np.linspace(0, 1, 12)]
        f.tube(mat, path, [0.017, 0.017, 0.017, 0.02, 0.017, 0.016, 0.016, 0.019, 0.016, 0.015, 0.016, 0.014], seg=10, col=col)
        f.sphere(mat, (sx * 0.215, -0.31, 1.05), 0.022, seg=12, col=col)
    for i in range(7):
        x = -0.15 + i * 0.05
        path = [Vector((x, -0.2 - 0.06 * t - 0.0, 0.44 + 0.4 * t)) for t in np.linspace(0, 1, 8)]
        f.tube(mat, path, [0.0085, 0.0085, 0.011, 0.0085, 0.0085, 0.0085, 0.0085, 0.0075], seg=8, col=col)
    crest = [Vector((x, -0.285 - 0.02 * (1 - (x / 0.23) ** 2), 1.0 + 0.04 * (1 - (x / 0.23) ** 2) + 0.0)) for x in np.linspace(-0.23, 0.23, 14)]
    f.tube(mat, crest, 0.0, seg=12) if False else None
    f.prism(mat, [(x, 0.95 + 0.035 * (1 - (x / 0.23) ** 2)) for x in np.linspace(-0.23, 0.23, 14)] + [(x, 1.04 + 0.045 * (1 - (x / 0.23) ** 2)) for x in np.linspace(0.23, -0.23, 14)],
            0.026, c=(0, -0.285, 0), plane='xz', col=col, bev=0.006, seg=2)
    f.sphere(mat, (0, -0.268, 1.045), 0.02, seg=10, sq=(1.3, 0.5, 1), col=(1.1, 1.0, 0.9))
    f.tube(mat, [Vector((-0.2, -0.25, 0.77)), Vector((0.2, -0.25, 0.77))], 0.011, seg=8, col=col)
    # arms with turned posts and scrolled ends
    for sx in (-1, 1):
        arm = [Vector((sx * 0.25, -0.18 + 0.52 * t, 0.66 + 0.012 * math.sin(t * 3) - 0.01 * t)) for t in np.linspace(0, 1, 10)]
        f.tube(mat, arm, [0.016, 0.017, 0.018, 0.018, 0.018, 0.018, 0.018, 0.02, 0.022, 0.024], seg=10, col=col, flat=(1.0, 0.8))
        f.sphere(mat, (sx * 0.25, 0.34, 0.655), 0.024, seg=12, sq=(1, 1.2, 0.8), col=col)
        f.tube(mat, [Vector((sx * 0.25, 0.22, 0.655)), Vector((sx * 0.25, 0.22, 0.52)), Vector((sx * 0.24, 0.2, 0.43))], [0.013, 0.014, 0.012], seg=8, col=col) if False else None
        f.lathe(mat, (sx * 0.245, 0.2, 0.43), profile_pts([(0.0005, 0), (0.014, 0.0), (0.011, 0.04), (0.017, 0.08), (0.012, 0.13), (0.014, 0.2), (0.0005, 0.24)], 2), seg=10, col=col, cap=False)
        f.tube(mat, [Vector((sx * 0.215, -0.18, 0.43)), Vector((sx * 0.215, -0.18, 0.66))], 0.0, seg=6) if False else None
    # knitted seat cushion + back cushion (wool)
    soft_box(M['wool'], f._m((0, 0.0, 0.44)), (0.46, 0.43, 0.055), col=(0.62, 0.3, 0.26), disp=0.004)
    f.box(M['wool'], (0, 0.0, 0.46), (0.3, 0.3, 0.004), bev=0.0008, col=(0.9, 0.84, 0.7), g=0) if False else None
    # yarn ball + needles on the seat
    f.sphere(M['wool'], (0.1, 0.08, 0.5), 0.045, seg=14, col=(0.84, 0.7, 0.46))
    for k in range(7):
        a = k * 0.9
        f.tube(M['wool'], [Vector((0.1 + 0.046 * math.cos(a + t), 0.08 + 0.046 * math.sin(a + t) * 0.0 + 0.0, 0.5 + 0.046 * math.sin(a * 0.5 + t * 2))) for t in np.linspace(0, 0.8, 5)], 0.0012, seg=4, col=(0.7, 0.55, 0.35), caps=False) if False else None
    for sx in (-1, 1):
        f.cyl(M['wood_pine'], (-0.02 + sx * 0.02, 0.1, 0.475), 0.003, 0.26, axis='y', seg=6, rot=(0, 0, 9 * sx), col=(0.9, 0.8, 0.6))
    if shawl:
        shawl_sim(f)
    collider_f(f, 0.64, 1.05, F + 0.62, name='rocking_chair')
    return f


def shawl_sim(f):
    """knitted shawl draped over the chair back (cloth sim)"""
    nx, ny = 30, 18
    sx_, sy_ = 1.1, 0.72

    def fz(x, y):
        return (x * 1.0, y * 1.0 - 0.08, 1.16 + 0.006 * math.sin(x * 11) + 0.0)
    v, fcs, uv = grid(nx, ny, sx_, sy_, fz)
    cols = rocker_proxies(f)
    # back rail collider (the crest) so the shawl rests on it
    cols.append(box_collider((0, -0.285, 1.0), (0.46, 0.05, 0.1)))
    cols.append(box_collider((0, -0.25, 0.77), (0.42, 0.03, 0.04)))
    res = simulate('bd_shawl', v, fcs, frames=90, colliders=cols, preset='wool', collision_dist=0.008, damping_scale=1.5)
    for c in cols:
        c.free()
    bm2 = solid_bm(res, fcs, uv, 0.012, 0.0)
    def cfn(p):
        q = f.M.inverted() @ p
        stripe = int(abs(q.x) / 0.07) % 3 == 0
        base = (0.5, 0.32, 0.27)
        k = 1.0 + 0.06 * nz(p.x * 30, p.y * 30, p.z * 30)
        c = (0.78, 0.62, 0.4) if stripe else base
        return (c[0] * k, c[1] * k, c[2] * k)
    f.put(M['wool'], bm2, cfn=cfn, skip_down=False)
    bm2.free()
    # fringe tassels along the free lower edge
    nxq = nx + 1
    prev = None
    for i in range(0, nx + 1, 2):
        p = Vector(res[i])             # j=0 row (lowest in y == hanging edge after sim)
        for j_ in (0,):
            pass
    # fringe: thin tubes hanging off the two long free edges of the sim result
    for edge_row in (0, ny):
        for i in range(0, nx + 1, 2):
            p = Vector(res[edge_row * nxq + i])
            if p.z < 0.25:
                continue
            for dx in (-0.004, 0.004):
                f.tube(M['wool'], [p + Vector((dx, 0, 0.0)), p + Vector((dx * 1.5, 0.0, -0.02)), p + Vector((dx * 2.2, 0.003, -0.04))], 0.0018, seg=4, col=(0.78, 0.62, 0.4), caps=False)


# ---------------------------------------------------------------- washstand
def washstand(pos, rot, W=0.86, D=0.46, H=0.86, items=True):
    f = Fr(pos, rot, F)
    mat = M['wood_pine']
    col = (1.0, 0.93, 0.85)
    colp = (0.85, 0.78, 0.7)
    # tapered turned legs
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (W / 2 - 0.03), sy * (D / 2 - 0.03)
            f.lathe(mat, (x, y, 0.0), profile_pts([(0.0005, 0), (0.014, 0.0), (0.018, 0.03), (0.014, 0.06), (0.017, 0.18), (0.021, 0.3), (0.02, 0.5), (0.026, 0.6), (0.03, 0.66), (0.03, H - 0.06)], 3), seg=14, col=col, cap=True)
    # carcass: back, sides, cupboard, drawer
    for sx in (-1, 1):
        f.box(mat, (sx * (W / 2 - 0.03), 0, 0.37), (0.016, D - 0.06, 0.5), bev=0.002, col=colp, g=2)
    f.box(mat, (0, -D / 2 + 0.03, 0.4), (W - 0.06, 0.016, 0.6), bev=0.002, col=colp, g=2)
    f.box(mat, (0, 0, 0.1), (W - 0.06, D - 0.06, 0.016), bev=0.002, col=col, g=0)
    f.box(mat, (0, 0, 0.62), (W - 0.06, D - 0.06, 0.016), bev=0.002, col=col, g=0)
    # drawer under top
    yfp = D / 2 - 0.03
    f.box(mat, (0, yfp, H - 0.1), (W - 0.1, 0.02, 0.1), bev=0.003, col=col, g=0)
    f.box(mat, (0, yfp + 0.0105, H - 0.1), (W - 0.18, 0.004, 0.055), bev=0.0015, col=(1.06, 0.98, 0.9), g=0)
    knob(f, (-0.12, yfp + 0.012, H - 0.1), axis='y', r=0.014, sign=1)
    knob(f, (0.12, yfp + 0.012, H - 0.1), axis='y', r=0.014, sign=1)
    # cupboard door (left) fielded panel + open shelf (right) with chamber pot
    dw = 0.34
    f.box(mat, (-W / 4 - 0.02, yfp, 0.36), (dw, 0.02, 0.46), bev=0.003, col=col, g=2)
    fielded_panel(f, -W / 4 - 0.02, 0.36, dw - 0.06, 0.36, yfp + 0.0, 1, mat=mat, col=col)
    knob(f, (-W / 4 - 0.02 + dw / 2 - 0.04, yfp + 0.012, 0.37), axis='y', r=0.013, sign=1)
    f.box(mat, (W / 4 + 0.08, 0, 0.36), (0.012, D - 0.06, 0.48), bev=0.002, col=colp, g=2)    # divider
    f.box(mat, (W / 4 + 0.12, 0.0, 0.32), (0.3, D - 0.06, 0.014), bev=0.002, col=col, g=0)
    # towel bars (turned, on bracket arms at both sides)
    for sx in (-1, 1):
        for k in (-1, 1):
            f.box(mat, (sx * (W / 2 + 0.025), k * 0.12, 0.62), (0.05, 0.02, 0.025), bev=0.003, col=col)
            f.cyl(mat, (sx * (W / 2 + 0.05), k * 0.12, 0.62), 0.012, 0.03, axis='x', seg=10)
        f.cyl(mat, (sx * (W / 2 + 0.05), 0, 0.64), 0.0095, 0.3, axis='y', seg=10, col=col)
        f.sphere(mat, (sx * (W / 2 + 0.05), 0.16, 0.64), 0.016, seg=10, col=col)
        f.sphere(mat, (sx * (W / 2 + 0.05), -0.16, 0.64), 0.016, seg=10, col=col)
    # top slab (ceramic-like marble) with basin hole, splash back
    top_poly = bm_box(W + 0.04, D + 0.03, 0.03)
    cut = bmesh.new()
    bmesh.ops.create_cone(cut, cap_ends=True, segments=36, radius1=0.16, radius2=0.16, depth=0.2, matrix=Matrix.Translation((0.0, 0.0, 0.0)))
    top_bm = boolean_diff(top_poly, cut)
    top_poly.free(); cut.free()
    bev_bm(top_bm, 0.004, 1)
    f.put(M['ceramic'], top_bm, c=(0, 0.0, H - 0.015), col=(0.9, 0.9, 0.88), g=0)
    top_bm.free()
    # splashback with scalloped top
    sp = [(-W / 2 - 0.02, 0.0)]
    pts = [(-W / 2 - 0.02, 0.0), (W / 2 + 0.02, 0.0), (W / 2 + 0.02, 0.17)]
    for i in range(1, 12):
        t = i / 12
        pts.append((W / 2 + 0.02 - t * (W + 0.04), 0.17 + 0.035 * abs(math.sin(t * math.pi * 5)) ** 0.7 + 0.05 * math.sin(t * math.pi)))
    pts.append((-W / 2 - 0.02, 0.17))
    f.prism(M['ceramic'], pts, 0.02, c=(0, -D / 2 + 0.01, H), plane='xz', col=(0.88, 0.9, 0.88), bev=0.003)
    f.prism(mat, [(x * 0.95, z * 0.8 - 0.0) for x, z in pts][:4] + [(-W / 2 * 0.95, 0.0)], 0.012, c=(0, -D / 2 - 0.004, H), plane='xz', col=colp) if False else None
    # porcelain basin sunk in the hole
    prof = profile_pts([(0.0005, -0.1), (0.07, -0.098), (0.12, -0.07), (0.155, -0.02), (0.165, 0.0), (0.185, 0.004), (0.188, 0.012), (0.176, 0.016), (0.158, 0.008), (0.15, -0.008), (0.1, -0.06), (0.0005, -0.085)], 3)
    f.lathe(M['ceramic'], (0, 0.0, H), prof, seg=36, cap=False, col=(0.96, 0.97, 0.97))
    lathe(M['water'], None, [(0.0005, 0.0), (0.11, 0.0)], seg=32, cap=False, Mx=f._m((0, 0, H - 0.062)), col=(0.7, 0.85, 0.9)) if False else None
    # blue rim line decoration
    f.torus(M['ceramic'], (0, 0.0, H + 0.006), 0.172, 0.0022, plane='xy', seg=48, rseg=4, col=(0.25, 0.42, 0.7))
    if items:
        washstand_items(f, W, D, H)
    collider_f(f, W + 0.2, D + 0.08, F + H + 0.2, name='washstand')
    return f


def jug(f, c, r=0.085, h=0.26):
    x, y, z = c
    prof = profile_pts([(0.0005, 0.0), (r * 0.8, 0.0), (r * 0.95, 0.015), (r, h * 0.3), (r * 0.9, h * 0.62), (r * 0.62, h * 0.78), (r * 0.55, h * 0.85), (r * 0.7, h * 0.95), (r * 0.62, h)], 3)
    def cfn(p):
        q = f.M.inverted() @ p
        zz = q.z - z
        band = abs(zz - h * 0.62) < 0.008 or abs(zz - h * 0.28) < 0.006
        return (0.28, 0.45, 0.72) if band else (0.97, 0.97, 0.95)
    f.lathe(M['ceramic'], (x, y, z), prof, seg=28, cap=False, cfn=cfn)
    # spout
    f.tube(M['ceramic'], [Vector((x - r * 0.45, y, z + h * 0.95)), Vector((x - r * 0.75, y, z + h * 1.0)), Vector((x - r * 0.95, y, z + h * 1.02))], [r * 0.45, r * 0.3, r * 0.14], seg=10, col=(0.97, 0.97, 0.95))
    # handle
    pts = bez((x + r * 0.62, y, z + h * 0.92), (x + r * 1.7, y, z + h * 0.95), (x + r * 1.7, y, z + h * 0.2), (x + r * 0.98, y, z + h * 0.2), 12)
    f.tube(M['ceramic'], pts, 0.0105, seg=10, col=(0.97, 0.97, 0.95), flat=(1.0, 0.7))
    # flower sprig decor
    for k in range(6):
        a = k * TAU / 6
        f.sphere(M['ceramic'], (x + math.cos(a) * r * 0.99, y + math.sin(a) * r * 0.99, z + h * 0.45), 0.012, seg=8, sq=(1, 1, 0.1), rot=(0, 0, 0), col=(0.85, 0.5, 0.55)) if False else None


def washstand_items(f, W, D, H):
    z = H
    jug(f, (0.27, 0.0, z), 0.07, 0.27)
    # soap dish + soap bar, toothbrush mug
    f.lathe(M['ceramic'], (-0.3, 0.12, z), profile_pts([(0.0005, 0.0), (0.04, 0.0), (0.055, 0.012), (0.05, 0.014), (0.03, 0.004)], 2), seg=20, cap=False, col=(0.95, 0.95, 0.93), scale=(1.0, 0.7, 1.0))
    f.box(M['wax'], (-0.3, 0.12, z + 0.018), (0.06, 0.036, 0.024), bev=0.008, seg=2, col=(0.95, 0.92, 0.8))
    f.lathe(M['ceramic'], (-0.3, -0.08, z), profile_pts([(0.0005, 0.0), (0.03, 0.0), (0.033, 0.01), (0.034, 0.09), (0.03, 0.09), (0.028, 0.01), (0.0005, 0.004)], 2), seg=18, cap=False, col=(0.9, 0.92, 0.96))
    for k in range(2):
        a = k * 1.5
        f.tube(M['wood_pine'], [Vector((-0.3 + 0.006 * math.cos(a), -0.08 + 0.006 * math.sin(a), z + 0.01)), Vector((-0.3 + 0.012 * math.cos(a), -0.08 + 0.012 * math.sin(a), z + 0.14))], 0.0035, seg=6, col=(0.85, 0.7, 0.5))
    # candle on the splashback side
    I.chamberstick(f.p((0.33, -0.16, z + 0.0)), lit=False, cl=0.09)
    # folded towel on the shelf and the towel on the bar (cloth sim)
    soft_box(M['linen'], f._m((W / 4 + 0.12, 0.0, 0.34)), (0.26, 0.28, 0.03), col=(0.9, 0.9, 0.86), disp=0.002)
    soft_box(M['linen'], f._m((W / 4 + 0.12, 0.0, 0.37)), (0.24, 0.26, 0.03), col=(0.62, 0.7, 0.8), disp=0.002)
    # chamber pot on the lower shelf
    f.lathe(M['ceramic'], (W / 4 + 0.12, 0.0, 0.1 + 0.008), profile_pts([(0.0005, 0.0), (0.07, 0.0), (0.095, 0.03), (0.1, 0.07), (0.098, 0.09), (0.11, 0.095), (0.105, 0.1), (0.09, 0.093), (0.088, 0.075)], 2), seg=24, cap=False, col=(0.95, 0.95, 0.93))
    towel_sim(f, W)


def towel_sim(f, W):
    sx = 1
    barx = sx * (W / 2 + 0.05)
    nx, ny = 14, 30
    ty = 0.0

    def fz(x, y):
        return (barx + (x) * 1.0, ty + (x) * 0 + 0.0 + 0.0, 0.64 + 0.03 + (y + 0.0) * 0.0 + 0.35) if False else (barx + y * 0.0 + x * 0, x * 1.0, 0.64 + 0.025 + y)
    # towel hangs over the bar along the bar axis (y): span across the bar in x: rows along x
    v = []
    uv = []
    verts = []
    for j in range(ny + 1):
        for i in range(nx + 1):
            xx = -0.17 + 0.34 * i / nx          # across the bar axis (along y)
            yy = -0.3 + 0.6 * j / ny            # length over the bar (x direction in world frame)
            verts.append((barx + yy * 0.0 + (yy), xx, 0.64 + 0.0125 + 0.0 + (0.004 * math.sin(xx * 25))))
            uv.append((i / nx * 0.34, j / ny * 0.6))
    verts = np.array(verts, np.float32)
    faces = []
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    cols = [cyl_collider((barx, 0, 0.64), 0.0095, 0.3, axis='y')] + [box_collider((0, 0, 0.3), (W, 0.5, 0.6))]
    res = simulate('bd_towel', verts, faces, frames=70, colliders=cols, preset='linen', collision_dist=0.006, damping_scale=1.5)
    for c in cols:
        c.free()
    bm2 = solid_bm(res, faces, np.array(uv, np.float32), 0.006, 0.0)
    f.put(M['linen'], bm2, cfn=lambda p: (0.9, 0.9, 0.86) if int((f.M.inverted() @ p).y / 0.05) % 6 else (0.42, 0.55, 0.72), skip_down=False)
    bm2.free()


# ---------------------------------------------------------------- wall shelf with trinkets
def wall_shelf(pos, rot, W=0.62, D=0.17, z=0.0, trinkets=True, mat_name='wood_pine'):
    """pos = world (x,y,z) of the shelf board centre at the wall; rot = facing direction like Fr"""
    f = Fr(pos, rot, None)
    mat = M[mat_name]
    col = (1.0, 0.93, 0.85)
    f.box(mat, (0, D / 2, 0.0), (W, D, 0.022), bev=0.004, col=col, g=0)
    f.box(mat, (0, D - 0.004, 0.006), (W, 0.014, 0.008), bev=0.002, col=(1.05, 0.97, 0.9), g=0) if False else None
    # front lip moulding
    f.box(mat, (0, D + 0.003, -0.008), (W + 0.016, 0.012, 0.02), bev=0.003, col=(1.05, 0.97, 0.9), g=0)
    # scroll brackets
    for sx in (-1, 1):
        pts = [(0.0, 0.0), (0.0, -0.13)]
        for i in range(1, 9):
            t = i / 8
            pts.append((0.1 * (1 - math.cos(t * math.pi / 2)) * 0 + 0.145 * (1 - math.sin((1 - t) * math.pi / 2)) * 0 + 0.145 * t ** 1.4 * 0 + 0.0, 0))
        poly = [(0.0, 0.0), (0.0, -0.14), (0.02, -0.14), (0.02, -0.12), (0.03, -0.08), (0.06, -0.05), (0.1, -0.03), (0.145, -0.012), (0.145, 0.0)]
        f.prism(mat, [(y_, z_) for y_, z_ in poly], 0.014, c=(sx * (W / 2 - 0.08), 0, -0.011), plane='yz', col=col, bev=0.0015, g=2)
    # plate rail
    f.box(mat, (0, 0.012, 0.12), (W, 0.014, 0.012), bev=0.002, col=col, g=0)
    if trinkets:
        z0 = 0.011
        # ceramic songbird
        pos_ = f.p((-W * 0.3, D * 0.5, z0))
        sphere(M['ceramic'], pos_ + Vector((0, 0, 0.026)), 0.026, seg=14, sq=(0.8, 1.2, 0.9), col=(0.4, 0.6, 0.75))
        sphere(M['ceramic'], pos_ + Vector((0, -0.018 * 0, 0.058)), 0.017, seg=12, col=(0.4, 0.6, 0.75))
        box(M['brass'], pos_ + Vector((0, -0.02, 0.058)), (0.004, 0.015, 0.004), bev=0)
        # shells + jar of buttons + tiny frame + candle
        for k in range(3):
            sphere(M['ceramic'], f.p((-W * 0.05 + k * 0.045, D * 0.35 + 0.02 * (k % 2), z0 + 0.012)), 0.017, seg=10, sq=(1.2, 0.9, 0.55), rot=(0, 0, 25 * k), col=(0.93, 0.82, 0.75))
        j0 = f.p((W * 0.15, D * 0.5, z0))
        lathe(M['glass'], j0, profile_pts([(0.0005, 0.0), (0.04, 0.0), (0.043, 0.004), (0.043, 0.09), (0.032, 0.1), (0.032, 0.108)], 2), seg=16, cap=False)
        for k in range(9):
            sphere(M['ceramic'], j0 + Vector((0.016 * math.cos(k * 2.4) * (0.5 + 0.5 * ((k * 7) % 3) / 2), 0.016 * math.sin(k * 2.4), 0.012 + 0.007 * k)), 0.0085, seg=8, sq=(1, 1, 0.4),
                   col=[(0.8, 0.2, 0.2), (0.2, 0.4, 0.7), (0.9, 0.8, 0.3), (0.3, 0.6, 0.4)][k % 4])
        lathe(M['brass'], j0 + Vector((0, 0, 0.108)), profile_pts([(0.033, 0.0), (0.035, 0.01), (0.0005, 0.012)], 1), seg=16, cap=False)
        I.chamberstick(f.p((W * 0.36, D * 0.5, z0)), lit=True, inten=0.6, dist=4.0, cl=0.08)
        # tiny silhouette frame leaning on the wall
        fp = f.p((W * 0.28 - 0.12, 0.03, z0))
        Mx = xf(fp, (0, 0, rot)) @ rotm((-10, 0, 0))
        box(M['wood_dark'], None, (0.09, 0.012, 0.11), Mx=Mx @ Matrix.Translation((0, 0, 0.055)), bev=0.002, col=(0.8, 0.7, 0.6))
        box(M['bd_painting_6'], None, (0.07, 0.002, 0.09), Mx=Mx @ Matrix.Translation((0, 0.0066, 0.055)), bev=0, uvs=1.0, col=(1, 1, 1), g=1) if False else None
    return f
