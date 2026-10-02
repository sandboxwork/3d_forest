"""Cast-iron wood cookstove with pipe, kettle & pots, firewood stack, hearth slab."""
from kt_lib import *
from kt_ware import *
from kt_food import *
from kt_pots import *

STOVE_POS = (-3.5, 2.935)
SW, SD = 0.76, 0.56
TOP = 0.82          # local top of hot plate (above floor)


def iron_cf(f, seed=0, soot=0.5, base=(1, 1, 1)):
    inv = f.M.inverted()

    def cf(p):
        l = inv @ p
        k = 1 + 0.1 * fbm(l.x * 14, l.y * 14, l.z * 14, 1, seed, 2)
        # soot toward top surface and around the flue
        s = 1.0
        if l.z > 0.7:
            s *= 1 - soot * min(1.0, (l.z - 0.7) / 0.14) * 0.7
        d = math.hypot(l.x - 0.0, l.y + 0.15)
        if l.z > 0.7 and d < 0.2:
            s *= 0.75
        return (base[0] * k * s, base[1] * k * s, base[2] * k * s)
    return cf


def stove_door(f, cx, cz, w, h, y=0.26, border=0.014, hinge='left', rivets=True, cf=None, vents=False, ring=False, seed=0):
    """cast door: plate + raised border frame + embossed medallion; hinges, latch, rivets, optional vent slits"""
    t = 0.018
    plate = cube_bm(w, t, h)
    bev_bm(plate, 0.004, 2)
    if vents:
        cuts = []
        for k in range(5):
            cb = cube_bm(w * 0.5, t * 3, 0.006)
            cuts.append((cb, Matrix.Translation((0, 0, h * 0.18 - k * 0.0125 + 0.012))))
        plate = boolean(plate, cuts)
        for cb, _ in cuts:
            cb.free()
    put('iron_cast', plate, f.M @ Matrix.Translation((cx, y + t / 2 - 0.004, cz)), cfn=cf)
    plate.free()
    if vents:   # dark inner behind slits
        f.box('iron_black', (cx, y + 0.0, cz + h * 0.18 + 0.012 - 0.025), (w * 0.52, 0.004, 0.065), bev=0, col=(0.03, 0.03, 0.03), skip_down=False)
    yf = y + t - 0.004
    bw = border
    for (dx, dz, sx, sz) in ((0, h / 2 - bw / 2 - 0.006, w - 0.024, bw), (0, -h / 2 + bw / 2 + 0.006, w - 0.024, bw), (-w / 2 + bw / 2 + 0.006, 0, bw, h - 0.024), (w / 2 - bw / 2 - 0.006, 0, bw, h - 0.024)):
        f.box('iron_cast', (cx + dx, yf + 0.003, cz + dz), (sx, 0.007, sz), bev=0.0022, seg=2, cfn=cf)
    # inner bevel rail
    f.box('iron_black', (cx, yf + 0.0015, cz), (w - 0.06, 0.003, h - 0.06), bev=0.0015, cfn=cf, skip_down=False) if not vents else None
    # medallion
    if not vents and not ring and w > 0.2:
        mr = min(w, h) * 0.2
        lathe('iron_cast', None, [(mr, 0.0), (mr * 0.96, 0.004), (mr * 0.8, 0.006), (mr * 0.55, 0.005), (mr * 0.4, 0.0075), (mr * 0.18, 0.009), (0.001, 0.0105)], 20, M=f.M @ Matrix.Translation((cx, yf + 0.0, cz - 0.0)) @ Matrix.Rotation(math.radians(-90), 4, 'X') @ Matrix.Rotation(math.radians(180), 4, 'X'), cap=False, cfn=cf) if False else None
        lathe('iron_cast', None, [(mr, 0.0), (mr * 0.96, 0.004), (mr * 0.8, 0.006), (mr * 0.55, 0.005), (mr * 0.4, 0.0075), (mr * 0.18, 0.009), (0.001, 0.0105)], 20,
              M=f.M @ Matrix.Translation((cx, yf + 0.0, cz)) @ Matrix.Rotation(math.radians(-90), 4, 'X'), cap=False, cfn=cf)
        for k in range(8):   # petal ribs
            a = TAU * k / 8
            f.box('iron_cast', (cx + mr * 0.62 * math.cos(a), yf + 0.006, cz + mr * 0.62 * math.sin(a)), (0.007, 0.005, mr * 0.5), bev=0.0015, r=(0, math.degrees(-a) + 90, 0), cfn=cf, skip_down=False)
    # hinges + latch
    hx = cx - w / 2 if hinge == 'left' else cx + w / 2
    sgn = -1 if hinge == 'left' else 1
    for zz in (cz + h * 0.32, cz - h * 0.32):
        f.cyl('iron_black', (hx + sgn * 0.002, yf + 0.003, zz), 0.0095, 0.045, axis='z', seg=8, cfn=cf)
        f.box('iron_black', (hx - sgn * 0.022, yf + 0.0015, zz), (0.045, 0.004, 0.026), bev=0.0015, cfn=cf)
        f.cyl('brass', (hx + sgn * 0.002, yf + 0.003, zz + 0.0255), 0.0072, 0.006, seg=8)
        dome('iron_black', f.p((hx - sgn * 0.034, yf + 0.0035, zz)), f.M.to_3x3() @ Vector((0, 1, 0)), r=0.0035)
        dome('iron_black', f.p((hx - sgn * 0.012, yf + 0.0035, zz)), f.M.to_3x3() @ Vector((0, 1, 0)), r=0.0035)
    lx = cx + w / 2 - 0.03 if hinge == 'left' else cx - w / 2 + 0.03
    f.cyl('iron_black', (lx, yf + 0.012, cz), 0.0065, 0.012, axis='y', seg=8)
    f.box('tin', (lx - (0.014 if hinge == 'left' else -0.014), yf + 0.019, cz), (0.045, 0.006, 0.012), bev=0.003, seg=2, r=(0, 0, 14))
    f.sphere('tin', (lx + (0.017 if hinge == 'left' else -0.017) - 0.0, yf + 0.019, cz + 0.002), 0.0085, seg=8, rings=5)
    if rivets:
        for sx in (-1, 1):
            for sz in (-1, 1):
                dome('iron_black', f.p((cx + sx * (w / 2 - 0.012), yf + 0.0075, cz + sz * (h / 2 - 0.012))), f.M.to_3x3() @ Vector((0, 1, 0)), r=0.0038)
    if ring:
        torus('iron_black', None, 0.016, 0.0036, plane='xz', M=f.M @ Matrix.Translation((cx, yf + 0.016, cz + h * 0.15)) @ Matrix.Rotation(math.radians(90), 4, 'X') @ Matrix.Rotation(math.radians(8), 4, 'Y'), seg=14, rseg=6)
        f.box('iron_black', (cx, yf + 0.006, cz + h * 0.15 + 0.012), (0.03, 0.01, 0.014), bev=0.003, cfn=cf)


def hot_lid(f, x, y, ajar=0.0, cf=None, r=0.082):
    zt = TOP + 0.006
    # collar ring (casting) with a dark hole beneath
    lathe('iron_cast', None, [(r + 0.012, 0.0), (r + 0.011, 0.005), (r + 0.006, 0.007), (r + 0.003, 0.0045), (r + 0.001, 0.0)], 24, M=f.M @ Matrix.Translation((x, y, TOP)), cfn=cf, cap=False)
    lathe('ink', None, [(r - 0.001, TOP - 0.01), (r - 0.001, TOP + 0.004), (0.001, TOP + 0.004)], 20, M=f.M @ Matrix.Translation((x, y, 0)), col=(0.02, 0.02, 0.02), cap=False)
    # inner removable ring + lid
    lathe('iron_cast', None, [(r * 0.5, 0.0), (r * 0.52, 0.005), (r * 0.45, 0.008), (r * 0.42, 0.004)], 16, M=f.M @ Matrix.Translation((x, y, zt - 0.0)), cfn=cf, cap=False)
    if ajar:
        Mx = f.M @ Matrix.Translation((x + r * 0.9, y, zt + 0.002)) @ Matrix.Rotation(math.radians(ajar), 4, 'Y') @ Matrix.Translation((-r * 0.9, 0, 0))
    else:
        Mx = f.M @ Matrix.Translation((x, y, zt))
    prof = [(0.001, 0.012), (r * 0.18, 0.0125), (r * 0.2, 0.0105), (r * 0.5, 0.009), (r * 0.52, 0.0115), (r * 0.62, 0.0105), (r * 0.64, 0.008), (r * 0.9, 0.0055), (r, 0.003), (r + 0.002, 0.0), (r * 0.98, -0.0035)]
    lathe('iron_cast', None, prof, 28, M=Mx, cfn=cf, cap=False)
    # lifter slot + central handle boss
    box('ink', None, (0.03, 0.006, 0.0025), M=Mx @ Matrix.Translation((0.0, 0.0, 0.0125)), bev=0)
    cyl('iron_cast', None, 0.014, 0.003, seg=10, M=Mx @ Matrix.Translation((0, 0, 0.0125)), cfn=cf)


def flue_pipe(f, x=0.0, y=-0.15, rad=0.0725, top_z=2.85, jog=0.09, jog_z=1.72, cf=None):
    """sheet-metal flue: collar, damper, seam ridges, crimped joints with clamps, 45-degree S-jog elbows, ceiling collar"""
    # collar on the hot plate
    lathe('iron_cast', None, [(rad + 0.03, 0.0), (rad + 0.026, 0.008), (rad + 0.012, 0.022), (rad + 0.004, 0.05), (rad + 0.0, 0.06)], 22, M=f.M @ Matrix.Translation((x, y, TOP)), cfn=cf, cap=False)
    z0 = TOP + 0.06

    def pipe(z_a, z_b, xx, seam_ang=2.2):
        n = 14
        f.cyl('iron_cast', (xx, y, (z_a + z_b) / 2), rad, z_b - z_a, seg=n, cfn=cf, cap=False)
        # rolled seam
        a = seam_ang
        tube('iron_cast', [f.p((xx + (rad + 0.002) * math.cos(a), y + (rad + 0.002) * math.sin(a), z_a)), f.p((xx + (rad + 0.002) * math.cos(a), y + (rad + 0.002) * math.sin(a), z_b))], 0.0032, seg=4, cfn=None, col=(0.8, 0.8, 0.8))
    def band(zz, xx, w=0.022):
        f.cyl('iron_cast', (xx, y, zz), rad + 0.004, w, seg=14, cfn=cf, cap=True)
        for k in range(2):
            a = TAU * (0.1 + 0.5 * k)
            dome('iron_cast', f.p((xx + (rad + 0.005) * math.cos(a), y + (rad + 0.005) * math.sin(a), zz)), f.M.to_3x3() @ Vector((math.cos(a), math.sin(a), 0)), r=0.0045)
    # lower run with damper box
    pipe(z0, 1.02, x)
    f.cyl('iron_cast', (x, y, 1.065), rad + 0.012, 0.09, seg=14, cfn=cf)
    f.cyl('brass', (x + rad + 0.012 + 0.02, y, 1.065), 0.0045, 0.05, axis='x', seg=6)
    f.box('brass', (x + rad + 0.042, y, 1.065), (0.036, 0.007, 0.012), bev=0.003, seg=2)
    # damper butterfly visible? (handle only)
    band(1.02, x); band(1.11, x)
    pipe(1.11, jog_z - 0.02, x)
    band(1.45, x)
    # S-jog (two 45 deg elbows) shifting the pipe by `jog` along local x
    ang = math.radians(45)
    L1 = jog / math.sin(ang)
    pts = [Vector((x, y, jog_z - 0.1)), Vector((x, y, jog_z - 0.04))]
    # elbow 1
    el1 = bez(Vector((x, y, jog_z - 0.04)), Vector((x, y, jog_z - 0.0)), Vector((x + jog * 0.15, y, jog_z + 0.05)), Vector((x + jog * 0.5, y, jog_z + jog * 0.5 + 0.05)), 8)
    el2 = bez(Vector((x + jog * 0.5, y, jog_z + jog * 0.5 + 0.05)), Vector((x + jog * 0.85, y, jog_z + jog * 0.95 + 0.05)), Vector((x + jog, y, jog_z + jog + 0.08)), Vector((x + jog, y, jog_z + jog + 0.14)), 8)
    path = [f.p(p) for p in el1 + el2[1:]]
    n = len(path)
    prof = [(math.cos(TAU * k / 14), math.sin(TAU * k / 14)) for k in range(14)]
    sweep('iron_cast', prof, path, scale=lambda t: (rad * (1.0 + 0.02 * math.sin(t * 40)), rad * (1.0 + 0.02 * math.sin(t * 40))), cfn=cf, caps=False)
    torus('iron_cast', None, rad + 0.003, 0.0035, plane='xy', M=f.M @ Matrix.Translation(el1[0]), seg=14, rseg=5)
    torus('iron_cast', None, rad + 0.003, 0.0035, plane='xy', M=f.M @ Matrix.Translation(el2[-1]), seg=14, rseg=5)
    zb = jog_z + jog + 0.14
    xj = x + jog
    pipe(zb, top_z - 0.3, xj)
    band(zb + 0.01, xj)
    band(top_z - 0.3, xj)
    pipe(top_z - 0.3, top_z + 0.02, xj, seam_ang=2.0)
    # strap bracket to the wall (wall is local -y side)
    ywall = -(SD / 2 + 0.02)
    zbk = 2.25
    for sgn in (1,):
        f.box('iron_cast', (xj, (y - rad + ywall) / 2 - 0.0, zbk), (0.022, abs(y - rad - ywall) + 0.01, 0.006), bev=0.002, cfn=cf)
        torus('iron_cast', None, rad + 0.006, 0.0042, plane='xy', M=f.M @ Matrix.Translation((xj, y, zbk)), seg=14, rseg=5)
        f.box('iron_cast', (xj, ywall + 0.004, zbk), (0.05, 0.008, 0.05), bev=0.003, cfn=cf)
        for sx in (-1, 1):
            for sz in (-1, 1):
                dome('iron_cast', f.p((xj + sx * 0.017, ywall + 0.008 + 0.0, zbk + sz * 0.017)), f.M.to_3x3() @ Vector((0, 1, 0)), r=0.004)
    # ceiling escutcheon
    lathe('iron_cast', None, [(rad + 0.05, top_z + 0.005), (rad + 0.045, top_z - 0.01), (rad + 0.02, top_z - 0.04), (rad + 0.004, top_z - 0.07)], 18, M=f.M @ Matrix.Translation((xj, y, 0)), cap=False, cfn=cf)
    return (xj, y)


def warming_shelf(f, cf=None):
    zs = 1.22
    pipe_x, pipe_y = 0.0, -0.15
    # shelf plate with circular cut-out for the flue (boolean)
    pl = cube_bm(SW, 0.2, 0.012)
    bev_bm(pl, 0.003, 2)
    cb = cyl_bm(0.085, 0.05, 20)
    pl = boolean(pl, [(cb, Matrix.Translation((pipe_x, pipe_y + 0.19, 0)))])
    cb.free()
    put('iron_black', pl, f.M @ Matrix.Translation((0, -0.19, zs)), cfn=cf)
    pl.free()
    # front nickel rail with scalloped drop
    f.box('tin', (0, -0.09, zs + 0.0), (SW, 0.006, 0.026), bev=0.002, seg=2)
    for k in range(int(SW / 0.05)):
        x = -SW / 2 + 0.025 + k * 0.05
        f.sphere('tin', (x, -0.09, zs - 0.012), 0.0095, seg=8, rings=4, sq=(1, 0.5, 0.8))
    # towel rod below the front with end finials
    f.tube('tin', [Vector((-SW / 2 - 0.02, -0.075, zs - 0.05)), Vector((SW / 2 + 0.02, -0.075, zs - 0.05))], 0.0075, seg=8)
    for s in (-1, 1):
        f.sphere('tin', (s * (SW / 2 + 0.024), -0.075, zs - 0.05), 0.0125, seg=8, rings=5)
        f.box('iron_black', (s * (SW / 2 - 0.03), -0.075 + 0.02, zs - 0.025), (0.01, 0.05, 0.03), bev=0.002)
        f.tube('tin', [Vector((s * (SW / 2 - 0.03), -0.075, zs - 0.05)), Vector((s * (SW / 2 - 0.03), -0.075, zs - 0.012))], 0.0045, seg=6)
    # back rail
    f.tube('tin', [Vector((-SW / 2, -0.285, zs + 0.0)), Vector((-SW / 2, -0.285, zs + 0.09)), Vector((SW / 2, -0.285, zs + 0.09)), Vector((SW / 2, -0.285, zs))], 0.006, seg=6)
    # posts with turned finials + scroll brackets
    for s in (-1, 1):
        px = s * (SW / 2 - 0.025)
        f.lathe('iron_black', (px, -0.25, TOP + 0.002), [(0.016, 0.0), (0.011, 0.012), (0.008, 0.03), (0.0085, 0.2), (0.012, 0.215), (0.0085, 0.225), (0.0085, 0.39), (0.0135, 0.4), (0.0105, 0.41), (0.016, 0.425), (0.006, 0.44), (0.001, 0.445)], seg=10, cfn=cf)
        sc = bez((px, -0.25, zs - 0.12), (px, -0.2, zs - 0.12), (px, -0.16, zs - 0.07), (px, -0.12, zs - 0.012), 8)
        f.tube('iron_black', [Vector(p) for p in sc], 0.0055, seg=6, cfn=cf)
        f.sphere('iron_black', (px, -0.12, zs - 0.012), 0.0075, seg=6, rings=4)
    return zs


def cookstove(pos=STOVE_POS, rot=180):
    f = Fr((pos[0], pos[1], F), rot)
    cf = iron_cf(f, 1)
    cf2 = iron_cf(f, 2, soot=0.8)
    W, D = SW, SD
    y0 = D / 2
    # --- hearth slab (fieldstone) under and in front of the stove
    hs = cube_bm(0.96, 0.82, 0.022, off=(0, 0, 0.011))
    bev_bm(hs, 0.004, 2)
    for axis in (0, 1):
        es = [e for e in hs.edges if abs((e.verts[0].co - e.verts[1].co)[axis]) > 0.12 and abs((e.verts[0].co - e.verts[1].co)[axis]) > 0.9 * (e.verts[0].co - e.verts[1].co).length]
        if es:
            bmesh.ops.subdivide_edges(hs, edges=es, cuts=5, use_grid_fill=True)
    put('stone', hs, f.M @ Matrix.Translation((0.0, 0.1, 0.0)), col=(0.9, 0.88, 0.85), g=0, skip_down=True)
    hs.free()
    # --- cabriole legs
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (W / 2 - 0.05), sy * (D / 2 - 0.05)
            path = bez((x, y, 0.02), (x + sx * 0.012, y + sy * 0.012, 0.05), (x - sx * 0.008, y - sy * 0.008, 0.11), (x, y, 0.17), 8)
            f.sweep('iron_cast', [(math.cos(TAU * k / 8), math.sin(TAU * k / 8)) for k in range(8)], path, scale=lambda t: (0.018 + 0.012 * t ** 1.5 + 0.01 * math.sin(t * math.pi) ** 2, 0.018 + 0.012 * t ** 1.5 + 0.01 * math.sin(t * math.pi) ** 2), cfn=cf)
            f.lathe('iron_cast', (x, y, 0.0), [(0.019, 0.0), (0.026, 0.004), (0.028, 0.012), (0.02, 0.022), (0.017, 0.03)], seg=10, cfn=cf)
    # --- base: skirt with ash drawer
    f.box('iron_cast', (0, 0, 0.17 + 0.07), (W - 0.01, D - 0.02, 0.14), bev=0.006, seg=2, cfn=cf, skip_down=False)
    f.box('iron_cast', (0, 0, 0.176), (W + 0.02, D + 0.01, 0.014), bev=0.004, seg=2, cfn=cf, skip_down=False)   # foot moulding
    f.box('iron_cast', (0, 0, 0.30), (W + 0.015, D + 0.005, 0.012), bev=0.004, seg=2, cfn=cf, skip_down=False)
    # --- main body
    f.box('iron_cast', (0, 0, 0.30 + 0.245), (W - 0.02, D - 0.03, 0.49), bev=0.006, seg=2, cfn=cf, skip_down=False)
    # corner pilasters (round columns with caps) on the front corners
    for sx in (-1, 1):
        x = sx * (W / 2 - 0.012)
        f.lathe('iron_cast', (x, y0 - 0.014, 0.30), [(0.02, 0.0), (0.0235, 0.012), (0.0185, 0.02), (0.0185, 0.46), (0.0235, 0.47), (0.0225, 0.49)], seg=10, cfn=cf)
        f.box('iron_cast', (x, y0 - 0.02, 0.30 + 0.245), (0.012, 0.012, 0.49), bev=0.002, cfn=cf, skip_down=False) if False else None
    # side panels: raised frame + medallion
    for sx in (-1, 1):
        xs = sx * (W / 2 - 0.012)
        for (dy, dz, sy_, sz_) in ((0, 0.22, 0.4, 0.012), (0, -0.22, 0.4, 0.012), (-0.2, 0, 0.012, 0.44), (0.2, 0, 0.012, 0.44)):
            f.box('iron_cast', (xs + sx * 0.004, dy, 0.30 + 0.245 + dz), (0.007, sy_, sz_), bev=0.002, cfn=cf, skip_down=False)
        lathe('iron_cast', None, [(0.09, 0.0), (0.085, 0.004), (0.065, 0.006), (0.05, 0.0055), (0.03, 0.0085), (0.001, 0.011)], 20, M=f.M @ Matrix.Translation((xs + sx * 0.002, 0, 0.30 + 0.245)) @ Matrix.Rotation(math.radians(90 * sx), 4, 'Y'), cap=False, cfn=cf)
        # heat ribs
        for k in range(5):
            f.box('iron_cast', (xs + sx * 0.006, 0.0, 0.30 + 0.095 + k * 0.07), (0.005, 0.3, 0.004), bev=0.001, cfn=cf, skip_down=False) if False else None
    # --- doors on the front
    stove_door(f, -0.245, 0.62, 0.255, 0.235, y0 - 0.026, hinge='left', cf=cf, seed=1)                 # fire door
    stove_door(f, -0.245, 0.385, 0.255, 0.14, y0 - 0.026, hinge='left', cf=cf, vents=True, ring=True)  # ash door
    stove_door(f, 0.125, 0.51, 0.45, 0.4, y0 - 0.026, hinge='left', cf=cf, rivets=True)               # oven door
    # divider between firebox and oven + nickel rails
    f.box('iron_cast', (-0.108, y0 - 0.014, 0.30 + 0.245), (0.014, 0.02, 0.49), bev=0.003, cfn=cf, skip_down=False)
    f.box('tin', (0, y0 - 0.004, 0.292), (W - 0.04, 0.012, 0.016), bev=0.003, seg=2)       # lower nickel rail
    f.box('tin', (0, y0 - 0.004, TOP - 0.016), (W - 0.03, 0.012, 0.02), bev=0.003, seg=2)   # upper rail
    # oven door furniture: handle bar on brackets + thermometer + latch
    yo = y0 - 0.026 + 0.018 + 0.005
    for sx in (-1, 1):
        f.tube('tin', [Vector((0.125 + sx * 0.14, yo, 0.65)), Vector((0.125 + sx * 0.14, yo + 0.022, 0.65))], 0.005, seg=6)
    f.tube('tin', [Vector((0.125 - 0.15, yo + 0.022, 0.65)), Vector((0.125 + 0.15, yo + 0.022, 0.65))], 0.0065, seg=8)
    f.tube('wood_dark', [Vector((0.125 - 0.07, yo + 0.022, 0.65)), Vector((0.125 + 0.07, yo + 0.022, 0.65))], 0.0095, seg=8, col=(0.55, 0.4, 0.3))
    # thermometer dial
    tmM = f.M @ Matrix.Translation((0.125, yo + 0.0, 0.565)) @ Matrix.Rotation(math.radians(-90), 4, 'X')
    lathe('brass', None, [(0.0345, 0.0), (0.0345, 0.008), (0.031, 0.01), (0.029, 0.007)], 18, M=tmM, cap=False)
    lathe('ceramic', None, [(0.029, 0.007), (0.001, 0.007)], 16, M=tmM, col=(0.95, 0.93, 0.85), cap=False)
    for k in range(9):
        a = math.radians(-60 + k * 30 + 90)
        box('ink', None, (0.0028, 0.012, 0.0014), M=tmM @ Matrix.Translation((0.022 * math.cos(a), 0.022 * math.sin(a), 0.0075)) @ Matrix.Rotation(a - math.pi / 2, 4, 'Z'), bev=0)
    box('ink', None, (0.0018, 0.026, 0.0012), M=tmM @ Matrix.Translation((0, 0, 0.0082)) @ Matrix.Rotation(math.radians(-25), 4, 'Z') @ Matrix.Translation((0, 0.008, 0)), bev=0)
    cyl('brass', None, 0.0035, 0.002, seg=8, M=tmM @ Matrix.Translation((0, 0, 0.0085)))
    # oven door latch (turn button on the right edge)
    f.box('iron_black', (0.125 + 0.19, yo + 0.006, 0.51), (0.014, 0.012, 0.075), bev=0.003, cfn=cf)
    f.cyl('brass', (0.125 + 0.19, yo + 0.014, 0.51), 0.008, 0.01, axis='y', seg=8)
    # maker's plate under oven door (cast lettering lines)
    f.box('brass', (0.125, yo + 0.0, 0.38), (0.12, 0.004, 0.034), bev=0.002)
    for k in range(3):
        f.box('ink', (0.125, yo + 0.0035, 0.372 + k * 0.011), (0.1 - 0.02 * (k % 2), 0.0015, 0.0035), bev=0, skip_down=False)
    # --- top plate
    tp = cube_bm(W + 0.04, D + 0.01, 0.03, off=(0, 0, 0.015))
    bev_bm(tp, 0.005, 2)
    for axis in (0, 1):
        es = [e for e in tp.edges if abs((e.verts[0].co - e.verts[1].co)[axis]) > 0.1 and abs((e.verts[0].co - e.verts[1].co)[axis]) > 0.9 * (e.verts[0].co - e.verts[1].co).length]
        if es:
            bmesh.ops.subdivide_edges(tp, edges=es, cuts=6, use_grid_fill=True)
    tp = disp(tp, 0.0005, 0.03, 3, direction='Z')
    put('iron_cast', tp, f.M @ Matrix.Translation((0, 0, TOP - 0.03)), cfn=cf2, g=0, skip_down=False)
    tp.free()
    # rim lip along back and sides
    f.box('iron_cast', (0, -D / 2 - 0.005 + 0.012, TOP + 0.014), (W + 0.04, 0.014, 0.034), bev=0.003, seg=2, cfn=cf2, skip_down=False)
    for sx in (-1, 1):
        f.box('iron_cast', (sx * (W / 2 + 0.014), 0, TOP + 0.007), (0.012, D, 0.016), bev=0.003, cfn=cf2, skip_down=False)
    # lids
    for (x, y) in ((-0.225, 0.095), (0.12, 0.095), (-0.225, -0.13), (0.12, -0.13)):
        hot_lid(f, x, y, ajar=7.0 if (x, y) == (0.12, -0.13) else 0.0, cf=cf2, r=0.082 if x < 0 else 0.086)
    # lid lifter hanging on the side hook
    f.tube('iron_black', [Vector((W / 2 + 0.03, 0.12, 0.74)), Vector((W / 2 + 0.03, 0.12, 0.64))], 0.003, seg=4)
    f.tube('iron_black', [Vector((W / 2 + 0.03, 0.12, 0.64)), Vector((W / 2 + 0.034, 0.12, 0.5)), Vector((W / 2 + 0.034, 0.12, 0.46))], 0.0035, seg=5)
    f.box('iron_black', (W / 2 + 0.014, 0.12, 0.745), (0.03, 0.012, 0.012), bev=0.002)
    # rivets along top plate front edge & seams
    for k in range(14):
        x = -W / 2 + 0.03 + k * (W - 0.06) / 13
        dome('iron_black', f.p((x, y0 + 0.002, TOP - 0.02)), f.M.to_3x3() @ Vector((0, 1, 0)), r=0.0036)
    for sx in (-1, 1):
        for k in range(7):
            dome('iron_black', f.p((sx * (W / 2 + 0.017), -0.2 + k * 0.067, TOP + 0.006)), f.M.to_3x3() @ Vector((sx, 0, 0)) + Vector((0, 0, 0.0)), r=0.0036)
    # --- flue + shelf
    flue_pipe(f, cf=cf2)
    warming_shelf(f, cf=cf2)
    # soot patch on the wall behind: very thin dark smear plane (vertex alpha not available -> use darkened plaster tone)
    collider_f(f, W + 0.04, D + 0.02, F + TOP)
    interact('stove', (pos[0], pos[1], F + 0.95), '주철 요리 난로')
    return f


def stove_props(f=None):
    """kettle, pots, pan on top of the stove; mugs and bowl on the warming shelf"""
    f = Fr((STOVE_POS[0], STOVE_POS[1], F), 180)
    rr = random.Random(3)
    zt = F + TOP + 0.006
    tip = kettle(f.p((0.12, 0.095, 0)) + Vector((0, 0, zt - F)), rot=f.rot + 200, r=0.1, mat='copper', seed=1) if False else None
    # copper kettle over the front right lid, spout pointing away from the player
    P = f.p((0.12, 0.09, 0)); P.z = zt
    tip = kettle(P, rot=f.rot - 40, r=0.105, mat='copper', seed=3)
    kettle_anchor(tip + Vector((0, 0, 0.02)))
    # cast pot on the back-left lid
    P = f.p((-0.225, -0.13, 0)); P.z = zt
    dutch_pot(P, r=0.085, h=0.11, rot=f.rot + 35, lid=True, soot=0.6, seed=2)
    # saucepan on front-left lid, handle toward the front
    P = f.p((-0.225, 0.095, 0)); P.z = zt
    saucepan(P, r=0.07, h=0.085, rot=f.rot + 20, mat='copper', lid=False, handle_len=0.2)
    # frying pan hanging across the back lid right
    P = f.p((0.13, -0.15, 0)); P.z = zt + 0.002
    frying_pan(P, r=0.105, rot=f.rot + 100, seed=4)
    # --- warming shelf items (shelf z local 1.22)
    zs = F + 1.22 + 0.006
    for k, (g, rm) in enumerate((('red', None), ('blue', 'cream'), ('cream', 'blue'))):
        P = f.p((-0.28 + 0.065 * k, -0.19, 0)); P.z = zs
        mug(P, glaze=g, rim=rm, r=0.04, h=0.085, rot=(0, 0, f.rot + 80 + 25 * k), fill=None, seg=14)
    P = f.p((0.2, -0.19, 0)); P.z = zs
    bowl(P, r=0.085, h=0.055, glaze='cream', rim='blue', rot=(0, 0, 10), seg=16)
    # bread dough rising under a cloth
    P = f.p((0.2, -0.19, 0)); P.z = zs + 0.012
    for k in range(2):
        pass
    # tea towel over the rod (cloth sim) is added in kt_hang


def wood_stack(pos=(-3.55, 2.2), rot=0, W=0.6, H=0.42, D=0.3):
    """split firewood: individual logs (lathe with irregular radius, split wedge faces, ring ends) in staggered rows"""
    f = Fr((pos[0], pos[1], F), rot)
    rr = random.Random(12)
    rows = 4
    # simple low retaining frame: two stakes + bottom bearers
    for sx in (-1, 1):
        f.box('wood_dark', (sx * (W / 2 + 0.012), 0, H / 2 + 0.005), (0.024, 0.04, H + 0.02), bev=0.004, col=(0.7, 0.6, 0.5), g=2)
    for sy in (-1, 1):
        f.box('wood_dark', (0, sy * (D / 2 - 0.04), 0.012), (W + 0.04, 0.045, 0.024), bev=0.004, col=(0.7, 0.6, 0.5), g=0)
    nlog = 0
    z = 0.024
    for row in range(rows):
        r_ = 0.052 + 0.006 * (row % 2)
        nrow = int((W - 0.01) / (2 * r_ * 0.98))
        off = (0.5 if row % 2 else 0.0) * r_
        for i in range(nrow + (0 if row % 2 else 0)):
            x = -W / 2 + r_ + off + i * (2 * r_ * 0.98)
            if x > W / 2 - r_ * 0.6:
                continue
            rad = r_ * rr.uniform(0.82, 1.0)
            L = D * rr.uniform(0.92, 1.0)
            yy = rr.uniform(-0.012, 0.012)
            # log body
            seg = 9
            bm = bmesh.new()
            ul = bm.loops.layers.uv.new('UVMap')
            cl = bm.loops.layers.float_color.new('Col')
            nz_ = 4
            rings = []
            for j in range(nz_ + 1):
                yv = -L / 2 + L * j / nz_
                ring = []
                for k in range(seg):
                    a = TAU * k / seg
                    # split logs are D-shaped: flatten one side
                    rk = rad * (1 + 0.08 * math.sin(a * 3 + row + i) + 0.04 * math.sin(yv * 15 + i))
                    xk = rk * math.cos(a); zk = rk * math.sin(a)
                    if row % 3 == i % 3:
                        zk = max(zk, -rad * 0.55)
                    ring.append(bm.verts.new((xk, yv, zk)))
                rings.append(ring)
            for j in range(nz_):
                for k in range(seg):
                    fc = bm.faces.new([rings[j][k], rings[j][(k + 1) % seg], rings[j + 1][(k + 1) % seg], rings[j + 1][k]])
                    for l in fc.loops:
                        l[ul].uv = (l.vert.co.y * 2.0, (math.atan2(l.vert.co.z, l.vert.co.x)) * rad * 2.0)
                        k_ = 1 + 0.2 * fbm(l.vert.co.x * 30, l.vert.co.y * 12, l.vert.co.z * 30, 1, i + row, 2)
                        l[cl] = (0.5 * k_, 0.38 * k_, 0.27 * k_, 1)
            bm.normal_update()
            put('wood_dark', bm, f.M @ Matrix.Translation((x, yy, z + rad * 1.0)) @ Matrix.Rotation(rr.uniform(0, TAU), 4, 'Y') if False else f.M @ Matrix.Translation((x, yy, z + rad)), g=0)
            bm.free()
            # end-grain discs (light with ring pattern via colour bands)
            for sgn in (-1, 1):
                e = lathe_bm([(0.001, 0), (rad * 0.45, 0), (rad * 0.47, 0.0), (rad * 1.0, 0.0)], seg, cap=False)
                cl2 = e.loops.layers.float_color.new('Col')
                for fc in e.faces:
                    for l in fc.loops:
                        rd = math.hypot(l.vert.co.x, l.vert.co.y) / rad
                        c = (0.85, 0.65, 0.4) if rd < 0.6 else (0.7, 0.5, 0.3)
                        l[cl2] = (c[0] * 0.8, c[1] * 0.8, c[2] * 0.8, 1)
                put('wood_pine', e, f.M @ Matrix.Translation((x, yy + sgn * L / 2, z + rad)) @ Matrix.Rotation(math.radians(-90 * sgn), 4, 'X'), g=0, flat=True)
                e.free()
            nlog += 1
        z += r_ * 1.75
    # kindling bundle and a few loose small sticks
    for k in range(7):
        a = rr.uniform(-0.3, 0.3)
        tube('wood_pine', [f.p((-W / 2 - 0.08 + 0.01 * k, -0.1 + 0.03 * k, 0.015 + 0.006 * (k % 3))), f.p((-W / 2 - 0.08 + 0.01 * k + 0.2 * math.cos(a), -0.1 + 0.03 * k + 0.3 * math.sin(a), 0.015 + 0.006 * (k % 3)))], 0.008, seg=5, col=(0.8, 0.6, 0.4))
    collider_f(f, W, D, F + H)
    interact('firewood', (pos[0], pos[1], F + 0.4), '장작더미')
    return f


def build():
    cookstove()
    stove_props()
    wood_stack()
