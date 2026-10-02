"""Longcase clock, antlers, rod rack, paintings, wall shelf, curtain."""
from lv_fire import *
from lv_tex import PAINT_SPEC


def rot_from_normal(nx, ny):
    return math.degrees(math.atan2(-nx, ny))


# ------------------------------------------------------------------ longcase clock
def clock_longcase(pos, rot):
    f = Fr(pos, rot, F_)
    W, D, H = 0.46, 0.26, 2.05
    m = M['wood_dark']
    wc = (0.5, 0.27, 0.15)
    vv = wood_vc(wc, 0.2, 8, 71, axis=2)
    vh = wood_vc(wc, 0.2, 8, 72, axis=0)
    bw = (0.55, 0.55, 0.5)
    # --- plinth: moulded base on bracket feet
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.lathe(m, (sx * (W / 2 - 0.0), sy * (D / 2 - 0.0), 0.0), [(0.001, 0), (0.035, 0), (0.04, 0.012), (0.03, 0.03), (0.026, 0.04)], seg=14, cfn=vv) if False else None
    f.box(m, (0, 0, 0.032), (W + 0.04, D + 0.03, 0.03), bev=0.003, cfn=vh, g=0)
    f.box(m, (0, 0, 0.11), (W + 0.006, D, 0.13), bev=0.003, cfn=vv, g=2)
    moulding(m, f.M @ Matrix.Translation((0, 0, 0.0)), rrect(W + 0.075, D + 0.065, 0.004, 1), [(-0.0375, 0.0), (-0.032, 0.0), (-0.028, 0.012), (-0.034, 0.02), (-0.038, 0.024)] if False else [(-0.03, 0.0), (0.0, 0.0), (0.004, 0.006), (0.0, 0.013), (-0.03, 0.016)], cfn=vh, g=0) if False else None
    moulding(m, f.M @ Matrix.Translation((0, 0, 0.17)), rrect(W + 0.034, D + 0.028, 0.004, 1), [(-0.02, 0.0), (0.0, 0.0), (0.007, 0.006), (0.009, 0.012), (0.004, 0.02), (-0.008, 0.026), (-0.02, 0.028)], cfn=vh, g=0)
    # carved shell/rosette on the plinth front panel
    for k in range(9):
        a = math.radians(-70 + k * 17.5)
        f.tube(m, [V(0, -(-D / 2) * 0 + D / 2 + 0.003, 0.085), V(0.045 * math.sin(a), D / 2 + 0.004, 0.085 + 0.045 * math.cos(a))], [0.0035, 0.0045], seg=5, col=(0.4, 0.25, 0.16))
    f.lathe(m, (0, D / 2 + 0.001, 0.085), [(0.0001, 0.0), (0.012, 0.0), (0.012, 0.003), (0.006, 0.007), (0.0001, 0.008)], r=(-90, 0, 0), seg=14, col=(0.4, 0.25, 0.16), cap=False)
    # --- trunk: hollow case (side walls, back, front stiles + rails) with a boolean-cut door (round lenticle hole)
    tw, td, z0, z1 = W - 0.07, D - 0.04, 0.19, 1.50
    zmid = (z0 + z1) / 2
    for s in (-1, 1):
        f.box(m, (s * (tw / 2 - 0.012), 0, zmid), (0.024, td, z1 - z0), bev=0.002, cfn=vv, g=2)
    f.box(m, (0, -td / 2 + 0.006, zmid), (tw, 0.012, z1 - z0), bev=0.002, col=(0.14, 0.09, 0.06), g=2)
    f.box(m, (0, 0, z0 + 0.01), (tw, td, 0.02), bev=0.002, col=(0.14, 0.09, 0.06), g=0)
    yf = D / 2 - 0.02          # front plane of the stiles/door
    # front frame: stiles + rails around the door opening
    dz0, dz1 = 0.30, 1.42
    dw = 0.25
    for s in (-1, 1):
        f.box(m, (s * (dw / 2 + 0.03), yf, zmid), (0.06, 0.02, z1 - z0), bev=0.002, cfn=vv, g=2)
    f.box(m, (0, yf, (z1 + dz1) / 2), (dw, 0.02, z1 - dz1), bev=0.002, cfn=vh, g=0)
    f.box(m, (0, yf, (z0 + dz0) / 2), (dw, 0.02, dz0 - z0), bev=0.002, cfn=vh, g=0)
    for s in (-1, 1):
        # reeded quarter columns at the front corners
        f.lathe(m, (s * (W / 2 - 0.026), D / 2 - 0.03, 0.19), [(0.0001, 0.0), (0.022, 0.0), (0.022, 0.012), (0.017, 0.016), (0.017, 1.28), (0.022, 1.284), (0.022, 1.296), (0.0001, 1.3)], seg=14, cfn=vv, cap=False)
        for k in range(8):
            a = k * TAU / 8
            f.tube(m, [V(s * (W / 2 - 0.026) + 0.0182 * math.cos(a), D / 2 - 0.03 + 0.0182 * math.sin(a), 0.21), V(s * (W / 2 - 0.026) + 0.0182 * math.cos(a), D / 2 - 0.03 + 0.0182 * math.sin(a), 1.47)], 0.0016, seg=4, col=(0.28, 0.17, 0.1), caps=False)
    # door slab with the lenticle hole cut by a Boolean modifier
    zl = 0.98
    dbm = bmesh.new()
    bmesh.ops.create_cube(dbm, size=1.0)
    for v in dbm.verts:
        v.co = Vector((v.co.x * dw, v.co.y * 0.018, v.co.z * (dz1 - dz0)))
    bmesh.ops.subdivide_edges(dbm, edges=dbm.edges[:], cuts=3, use_grid_fill=True)
    cut = bmesh.new()
    bmesh.ops.create_cone(cut, cap_ends=True, segments=26, radius1=0.056, radius2=0.056, depth=0.1, matrix=Matrix.Translation((0, 0, zl - (dz0 + dz1) / 2)) @ Matrix.Rotation(math.radians(90), 4, 'X'))
    cobj = obj_from_bm('_cut', cut)
    dbm = modbm(dbm, [('BOOLEAN', dict(operation='DIFFERENCE', object=cobj, solver='EXACT'))])
    bpy.data.objects.remove(cobj)
    put(m, dbm, f.M @ Matrix.Translation((0, yf + 0.0, (dz0 + dz1) / 2)), (0.4, 0.25, 0.16), vv, 2)
    dbm.free()
    # raised moulding around the door
    Mf = f.M @ Matrix.Translation((0, yf + 0.009, (dz0 + dz1) / 2)) @ Matrix.Rotation(math.radians(90), 4, 'X') @ Matrix.Scale(-1, 4, (0, 0, 1))
    bmv = sweep_bm(rrect(dw - 0.04, dz1 - dz0 - 0.04, 0.05, 5), [(0.016, 0.0), (0.012, 0.004), (0.006, 0.006), (0.0, 0.0045), (-0.004, 0.0)], True, 1.0, flip=True)
    put(m, bmv, Mf, (0.42, 0.26, 0.17), vh, 2, uv_abs=True)
    bmv.free()
    # lenticle: brass bezel + glass bubble
    f.tube(M['brass'], [V(0.058 * math.cos(a), yf + 0.011, zl + 0.058 * math.sin(a)) for a in [i * TAU / 30 for i in range(31)]], 0.0045, seg=7, caps=False)
    f.lathe(M['glass'], (0, yf + 0.0, zl), [(0.056, 0.0), (0.05, 0.007), (0.03, 0.0125), (0.001, 0.0135)], r=(-90, 0, 0), seg=26, cap=False)
    # escutcheon + knob + hinges
    f.box(M['brass'], (0.095, yf + 0.0115, 0.86), (0.016, 0.0015, 0.03), bev=0.0004)
    f.box(M['ink'], (0.095, yf + 0.0125, 0.86), (0.003, 0.0005, 0.01), bev=0)
    for z in (0.45, 1.3):
        f.box(M['brass'], (-0.128, yf + 0.0105, z), (0.02, 0.0015, 0.05), bev=0.0004)
        for dz in (-0.02, 0.0, 0.02):
            sphere(M['brass'], f.p(V(-0.128, yf + 0.011, z + dz)), 0.0022, seg=5, rings=3)
    # dark interior so the pendulum bob reads behind the lenticle
    f.box(M['ink'], (0, yf - 0.03, zl), (0.14, 0.01, 0.14), bev=0.0, col=(0.03, 0.02, 0.015))
    f.box(m, (0, 0.0, 1.512), (W - 0.03, D - 0.02, 0.024), bev=0.002, cfn=vh, g=0)
    # --- waist moulding
    moulding(m, f.M @ Matrix.Translation((0, 0, 1.5)), rrect(W - 0.0, D - 0.004, 0.004, 1), [(-0.03, 0.0), (0.0, 0.0), (0.008, 0.008), (0.012, 0.016), (0.004, 0.024), (-0.03, 0.028)], cfn=vh, g=0)
    # --- hood
    hz0 = 1.53
    hh = 0.45
    # hollow hood: floor plate over the waist, side walls, back, ceiling plate; dial sits inside, behind a glass door
    f.box(m, (0, 0.0, hz0 - 0.01), (W - 0.02, D - 0.03, 0.02), bev=0.002, cfn=vh, g=0)
    for s in (-1, 1):
        f.box(m, (s * (W / 2 - 0.02), -0.005, hz0 + hh / 2), (0.02, D - 0.03, hh), bev=0.002, cfn=vv, g=2)
    f.box(m, (0, -D / 2 + 0.03, hz0 + hh / 2), (W - 0.04, 0.012, hh), bev=0.002, col=(0.12, 0.08, 0.05), g=2)
    f.box(m, (0, -0.005, hz0 + hh + 0.01), (W - 0.02, D - 0.03, 0.02), bev=0.002, cfn=vh, g=0)
    f.box(M['ink'], (0, 0.0, hz0 + hh / 2), (W - 0.08, 0.1, hh - 0.04), bev=0.0, col=(0.04, 0.03, 0.02))
    # hood front frame around dial opening
    for s in (-1, 1):
        f.box(m, (s * (W / 2 - 0.04), D / 2 - 0.02, hz0 + hh / 2), (0.05, 0.02, hh), bev=0.002, cfn=vv, g=2)
        # turned columns flanking the dial
        f.lathe(M['brass'], (s * (W / 2 - 0.044), D / 2 + 0.002, hz0 + 0.02), [(0.001, 0.0), (0.0125, 0.0), (0.0125, 0.01), (0.009, 0.014), (0.009, 0.1), (0.012, 0.104), (0.009, 0.108), (0.009, 0.3), (0.0125, 0.304), (0.0125, 0.32), (0.009, 0.325), (0.001, 0.326)], seg=12, cap=False)
    f.box(m, (0, D / 2 - 0.02, hz0 + 0.02), (W - 0.02 - 0.1, 0.02, 0.04), bev=0.002, cfn=vh, g=0)
    f.box(m, (0, D / 2 - 0.02, hz0 + hh - 0.02), (W - 0.02 - 0.1, 0.02, 0.04), bev=0.002, cfn=vh, g=0)
    f.box(m, (0, D / 2 - 0.08, hz0 + hh / 2), (W - 0.1, 0.006, hh - 0.08), bev=0.0, col=(0.12, 0.09, 0.06), g=2)
    # glass door
    f.box(M['glass'], (0, D / 2 - 0.006, hz0 + hh / 2), (W - 0.1, 0.003, hh - 0.08), bev=0)
    # dial: square brass plate (arched top) with silvered chapter ring
    f.box(M['brass'], (0, D / 2 - 0.0535, zc + 0.02 if False else hz0 + 0.225 + 0.015), (0.32, 0.004, 0.4), bev=0.0, col=(1, 0.88, 0.62))
    zc = hz0 + 0.225
    f.cyl(M['brass'], (0, D / 2 - 0.05, zc), 0.145, 0.006, axis='y', seg=36, col=(1, 0.93, 0.7))
    f.cyl(M['paper'], (0, D / 2 - 0.0465, zc), 0.128, 0.002, axis='y', seg=36, col=(0.9, 0.9, 0.86))
    f.cyl(M['brass'], (0, D / 2 - 0.046, zc), 0.082, 0.0015, axis='y', seg=28, col=(1, 0.9, 0.65))
    for i in range(60):
        a = i * TAU / 60
        big = (i % 5 == 0)
        f.box(M['ink'], (math.sin(a) * 0.121, D / 2 - 0.0455, zc + math.cos(a) * 0.121), (0.0012 if not big else 0.003, 0.0007, 0.004 if not big else 0.012), r=(0, -math.degrees(a), 0), bev=0, col=(0.05, 0.05, 0.05))
    for i in range(12):
        a = i * TAU / 12
        for k in range(1 if i % 4 else 2):
            f.box(M['ink'], (math.sin(a) * 0.1 + 0.002 * (k - 0.5) * math.cos(a) * 0, D / 2 - 0.0455, zc + math.cos(a) * 0.1), (0.003, 0.0007, 0.014 if i % 3 == 0 else 0.01), r=(0, -math.degrees(a) + (0 if k == 0 else 0), 0), bev=0, col=(0.04, 0.04, 0.04))
    # hour (spade) and minute (pierced) hands
    f.box(M['ink'], (0.016, D / 2 - 0.0435, zc + 0.026), (0.004, 0.0012, 0.055), r=(0, -32, 0), bev=0, col=(0.03, 0.03, 0.03))
    sphere(M['ink'], f.p(V(0.03, D / 2 - 0.0435, zc + 0.052)), 0.007, seg=8, rings=5, sq=(1, 0.2, 1.3), col=(0.03, 0.03, 0.03))
    f.box(M['ink'], (-0.035, D / 2 - 0.0425, zc - 0.012), (0.0028, 0.0012, 0.105), r=(0, 108, 0), bev=0, col=(0.03, 0.03, 0.03))
    f.lathe(M['brass'], (0, D / 2 - 0.0425, zc), [(0.001, 0.0), (0.007, 0.0), (0.0065, 0.0022), (0.001, 0.0025)], r=(-90, 0, 0), seg=10, cap=False)
    # subdial (seconds) and moon-phase arch
    f.cyl(M['paper'], (0, D / 2 - 0.0452, zc - 0.05), 0.02, 0.0015, axis='y', seg=16, col=(0.85, 0.85, 0.8))
    f.box(M['ink'], (0.005, D / 2 - 0.0442, zc - 0.05 + 0.008), (0.0012, 0.0008, 0.016), bev=0, col=(0.03, 0.03, 0.03))
    # arch window with moon dial
    f.box(M['brass'], (0, D / 2 - 0.05, zc + 0.19), (0.29, 0.006, 0.07), bev=0.002, col=(1, 0.93, 0.7))
    f.lathe(M['brass'], (0, D / 2 - 0.05, zc + 0.155), [(0.0001, 0.0), (0.145, 0.0), (0.13, 0.04), (0.08, 0.075), (0.0001, 0.095)], r=(-90, 0, 0), seg=26, cap=False, scale=(1, 1, 1)) if False else None
    f.lathe(M['ceramic'], (0, D / 2 - 0.0465, zc + 0.188), [(0.001, 0.0), (0.06, 0.0), (0.06, 0.002), (0.001, 0.002)], r=(-90, 0, 0), seg=24, cap=False,
            cfn=lambda p: (0.12, 0.2, 0.42) if (math.hypot(p.x - f.p(V(0, 0, 0)).x, 1) > 0 and ((p - f.p(V(0.0, 0, zc + 0.188))).length > 0.0)) and nz(p.x * 90, p.z * 90, 1.0) > -0.35 else (0.95, 0.85, 0.4))
    f.cyl(M['gilt'], (-0.02, D / 2 - 0.0445, zc + 0.19), 0.017, 0.0012, axis='y', seg=14)
    # spandrel ornaments (brass leaf scrolls in the dial corners)
    for sx in (-1, 1):
        for sz in (-1, 1):
            pts_ = [V(sx * 0.11, D / 2 - 0.0475, zc + sz * 0.11), V(sx * 0.125, D / 2 - 0.0475, zc + sz * 0.1), V(sx * 0.135, D / 2 - 0.0475, zc + sz * 0.118), V(sx * 0.12, D / 2 - 0.0475, zc + sz * 0.135), V(sx * 0.105, D / 2 - 0.0475, zc + sz * 0.128), V(sx * 0.098, D / 2 - 0.0475, zc + sz * 0.115)]
            f.tube(M['gilt'], pts_, 0.0032, seg=5, caps=True)
            sphere(M['gilt'], f.p(V(sx * 0.1, D / 2 - 0.0475, zc + sz * 0.1)), 0.006, seg=7, rings=4, sq=(1, 0.4, 1))
    # --- hood top: broken-arch (swan neck) pediment + shell + finials
    ht = hz0 + hh
    moulding(m, f.M @ Matrix.Translation((0, 0, ht)), rrect(W + 0.04, D + 0.01, 0.004, 1), [(-0.02, 0.0), (0.0, 0.0), (0.012, 0.01), (0.014, 0.02), (0.005, 0.032), (-0.02, 0.035)], cfn=vh, g=0)
    for s in (-1, 1):
        pts_ = []
        for k in range(14):
            t = k / 13
            pts_.append(V(s * (0.03 + 0.2 * t), D / 2 - 0.004, ht + 0.035 + 0.09 * math.sin(t * math.pi * 0.7) ** 0.9 + 0.0 + 0.02 * t))
        f.tube(m, pts_, [0.012 - 0.003 * math.sin(k / 13 * math.pi) for k in range(14)], seg=8, cfn=vh)
        # rosette termination
        f.lathe(M['brass'], (s * 0.032, D / 2 + 0.002, ht + 0.05), [(0.0001, 0.0), (0.024, 0.0), (0.026, 0.003), (0.014, 0.006), (0.0001, 0.01)], r=(-90, 0, 0), seg=16, cap=False)
    f.box(m, (0, -0.005, ht + 0.06), (W - 0.1, D - 0.06, 0.05), bev=0.003, cfn=vh, g=0)
    # carved fan/shell in the pediment
    for k in range(11):
        a = math.radians(-75 + k * 15)
        f.tube(m, [V(0, D / 2 - 0.02, ht + 0.05), V(0.075 * math.sin(a), D / 2 - 0.012, ht + 0.05 + 0.075 * math.cos(a))], [0.003, 0.0075], seg=5, col=(0.42, 0.26, 0.16))
    # finials: three turned brass urns
    for (x, h_) in ((-0.17, 0.12), (0.0, 0.17), (0.17, 0.12)):
        f.lathe(M['brass'], (x, D / 2 - 0.03, ht + 0.09), [(0.001, 0.0), (0.016, 0.0), (0.012, 0.008), (0.018, 0.02), (0.01, 0.035), (0.0075, 0.05), (0.011, 0.056), (0.005, 0.066), (0.0035, 0.09 * h_ / 0.12), (0.001, 0.1 * h_ / 0.12)], seg=12, cap=False)
    # --- movement visible behind glass is implied; weights not visible. pendulum is a separate animated part.
    saved = part_begin()
    pivot = f.p(V(0, -0.02, 1.32))
    g = Fr(pivot, rot, None)
    g.tube(M['brass'], [V(0, 0, 0), V(0, 0, -0.18), V(0, 0, -0.34)], 0.0025, seg=6)
    g.tube(M['brass'], [V(0, 0, 0.0), V(0.0, 0.0, 0.0)], 0.001, seg=3) if False else None
    g.lathe(M['brass'], (0, 0, -0.395), [(0.001, -0.004), (0.058, -0.004), (0.06, 0.0), (0.058, 0.004), (0.001, 0.004)], r=(90, 0, 0), seg=28, cap=False)
    g.lathe(M['brass'], (0, 0, -0.395), [(0.001, -0.012), (0.03, -0.01), (0.03, 0.01), (0.001, 0.012)], r=(90, 0, 0), seg=18, cap=False, col=(0.85, 0.7, 0.4))
    g.box(M['brass'], (0, 0, -0.004), (0.018, 0.006, 0.01), bev=0.001)
    g.box(M['brass'], (0, 0, -0.34), (0.014, 0.004, 0.01), bev=0.001)
    part_end(saved, 'clock_pendulum', pivot)
    collider_f(f, W + 0.075, D + 0.07, F_ + 2.2)
    return f


# ------------------------------------------------------------------ antlers
def antlers(pos, rot, S=0.97):
    f = Fr(pos, rot, None)
    f.M = f.M @ Matrix.Scale(S, 4)
    f.p = lambda l, M_=f.M: M_ @ Vector(l)
    # carved oak shield plaque
    outline = []
    for i in range(30):
        t = i / 30
        a = t * TAU
        x = 0.1 * math.sin(a) * (1 + 0.08 * math.cos(2 * a))
        y = 0.0
        outline.append(a)
    sh = []
    N = 40
    for i in range(N):
        a = i * TAU / N
        # heater shield: wide top, pointed bottom
        x = 0.11 * math.sin(a) * (1.0 if math.cos(a) > 0 else (0.45 + 0.55 * (1 + math.cos(a)) / 1.0 * 0.0 + 0.55 * (math.cos(a) + 1) * 0.0))
        c = math.cos(a)
        w_ = 0.11 * (1.0 if c > 0 else (1 + c * 0.0))
        xx = w_ * math.sin(a) * (1 if c >= 0 else (1 + c) ** 0.55)
        zz = 0.125 * c if c >= 0 else 0.17 * c
        sh.append(Vector((xx, zz, 0)))
    # path in local XY (x,z) -> sweep in XY then rotate so that +z of sweep = local +y (out of wall)
    Mp = f.M @ Matrix.Rotation(math.radians(90), 4, 'X') @ Matrix.Scale(-1, 4, (0, 0, 1))
    bm = sweep_bm([q for q in sh], [(-0.012, 0.0), (0.0, 0.0), (0.006, 0.006), (0.009, 0.012), (0.004, 0.018), (-0.012, 0.022)], True, 1.0, flip=True)
    put(M['wood_dark'], bm, Mp, (0.45, 0.28, 0.17), wood_vc((0.42, 0.26, 0.16), 0.2, 9, 81, 2), 2, uv_abs=True)
    bm.free()
    # panel fill
    bm = bmesh.new()
    ctr = bm.verts.new((0, 0, 0.018))
    ring = [bm.verts.new((q.x * 0.9, q.y * 0.9, 0.019)) for q in sh]
    for i in range(N):
        bm.faces.new([ctr, ring[i], ring[(i + 1) % N]])
    put(M['wood_dark'], bm, Mp @ Matrix.Identity(4), (0.5, 0.31, 0.19), wood_vc((0.46, 0.28, 0.17), 0.2, 9, 82, 2), 2)
    bm.free()
    # carved scalloped rim dots
    for i in range(0, N, 2):
        q = sh[i]
        sphere(M['wood_dark'], f.p(V(q.x * 0.95, 0.02, q.y * 0.95)), 0.0045, seg=6, rings=3, col=(0.4, 0.25, 0.15))
    # skull cap (bone)
    bone = (0.82, 0.76, 0.62)
    sphere(M['endgrain'], f.p(V(0, 0.045, 0.04)), 0.055, seg=14, rings=8, sq=(1.0, 0.8, 1.0), col=bone)
    f.lathe(M['endgrain'], (0, 0.025, 0.02), [(0.0001, 0.0), (0.05, 0.0), (0.054, 0.006), (0.04, 0.03), (0.0001, 0.04)], r=(-90, 0, 0), seg=14, cap=False, col=bone) if False else None
    # antlers: each side: main beam with brow, bez, trez tines and crown
    for s in (-1, 1):
        rr = random.Random(7 + s)
        beam = [V(s * 0.03, 0.05, 0.075), V(s * 0.075, 0.075, 0.115), V(s * 0.14, 0.1, 0.17), V(s * 0.19, 0.13, 0.25), V(s * 0.205, 0.15, 0.34), V(s * 0.215, 0.16, 0.43),
                V(s * 0.2, 0.15, 0.52), V(s * 0.17, 0.13, 0.6), V(s * 0.135, 0.11, 0.665)]
        radii = [0.024, 0.022, 0.019, 0.0165, 0.015, 0.0135, 0.0115, 0.009, 0.005]
        # pearling: radius bumps
        beam_s = []
        rad_s = []
        for i in range(len(beam) - 1):
            for k in range(3):
                t = k / 3
                beam_s.append(beam[i] * (1 - t) + beam[i + 1] * t)
                rad_s.append(radii[i] * (1 - t) + radii[i + 1] * t)
        beam_s.append(beam[-1]); rad_s.append(radii[-1])
        pc = lambda q: (0.78 + 0.1 * nz(q.x * 60, q.y * 60, q.z * 60), 0.7 + 0.08 * nz(q.x * 60, q.y * 60, q.z * 60), 0.54 + 0.06 * nz(q.x * 60, q.y * 60, q.z * 60))
        f.tube(M['endgrain'], beam_s, [r * (1 + 0.09 * math.sin(i * 2.7)) for i, r in enumerate(rad_s)], seg=8, cfn=lambda p, f=f: (lambda t: (0.55 + 0.35 * t, 0.46 + 0.35 * t, 0.34 + 0.3 * t))(clamp((f.M.inverted() @ p).z / 0.66)))
        # tines
        tines = [(1, V(s * 0.04, -0.05, 0.11), 0.2, 0.012), (2, V(s * 0.04, -0.04, 0.16), 0.24, 0.0105), (3, V(s * 0.05, -0.03, 0.14), 0.2, 0.0095), (4, V(s * 0.04, -0.02, 0.12), 0.16, 0.0085), (5, V(s * 0.03, 0.0, 0.1), 0.12, 0.0075)]
        for (ib, off, L, rb) in tines:
            b = beam[min(ib + 1, len(beam) - 1)]
            tip = b + V(off.x * 1.0 * (L / 0.12) * 0.6 + s * 0.015, off.y * (L / 0.12), off.z * (L / 0.12) * 0.9)
            mid = (b + tip) / 2 + V(s * 0.015, 0.0, 0.0)
            f.tube(M['endgrain'], [b + V(0, 0, 0), mid, tip], [rb, rb * 0.75, 0.0025], seg=6, cfn=lambda p, f=f: (lambda t: (0.55 + 0.35 * t, 0.46 + 0.35 * t, 0.34 + 0.3 * t))(clamp((f.M.inverted() @ p).z / 0.66)))
        # crown points
        top = beam[-1]
        for k in range(3):
            a = -0.6 + 0.6 * k
            tip = top + V(s * 0.05 * math.cos(a + 1), 0.03 * math.sin(a), 0.1 + 0.02 * k)
            f.tube(M['endgrain'], [top, (top + tip) / 2 + V(0, 0.01, 0), tip], [0.0045, 0.0035, 0.002], seg=5, col=(0.88, 0.8, 0.66))
        # burr (coronet) at the base
        f.lathe(M['endgrain'], (s * 0.03, 0.05, 0.075), [(0.0001, -0.01), (0.03, -0.004), (0.034, 0.004), (0.026, 0.012), (0.0001, 0.016)], r=(-90, 0, 0), seg=12, cap=False, col=(0.7, 0.62, 0.5)) if False else None
        sphere(M['endgrain'], f.p(V(s * 0.03, 0.055, 0.073)), 0.03, seg=12, rings=6, sq=(1, 0.8, 0.7), col=(0.7, 0.62, 0.48))


# ------------------------------------------------------------------ fishing rod rack
def rod_rack(pos, rot, L0=2.0):
    """pos: wall point, rot: Fr rot (local -y = into room; rods run along local x)."""
    f = Fr(pos, rot, None)
    wc = (0.4, 0.26, 0.16)
    vv = wood_vc(wc, 0.2, 8, 91, axis=2)
    # backboard rails with carved ends + brass screws
    for z in (-0.06, 0.06):
        pass
    for x in (-0.62, 0.62):
        f.box(M['wood_dark'], (x, -0.012, 0.0), (0.075, 0.024, 0.24), bev=0.003, cfn=vv, g=2)
        # top/bottom carved ends (little scalloped tips)
        for dz in (-0.12, 0.12):
            f.lathe(M['wood_dark'], (x, -0.012, dz), [(0.001, 0), (0.0375, 0), (0.0375, 0.0)], seg=3, cap=False) if False else None
            f.cyl(M['wood_dark'], (x, -0.012, dz), 0.0375, 0.024, axis='y', seg=14, col=(0.42, 0.27, 0.16))
        for dz in (-0.1, 0.1):
            f.cyl(M['brass'], (x, -0.026, dz), 0.0055, 0.003, axis='y', seg=10)
            f.box(M['ink'], (x, -0.0275, dz), (0.007, 0.0006, 0.0012), bev=0, r=(0, 35, 0))
        # two turned pegs per bracket (forks) + upturned tips
        for z in (-0.06, 0.06):
            f.lathe(M['wood_dark'], (x, -0.024, z), [(0.0001, 0.0), (0.016, 0.0), (0.012, 0.008), (0.009, 0.03), (0.01, 0.07), (0.012, 0.09), (0.011, 0.1), (0.0001, 0.104)], r=(90, 0, 0), seg=12, cap=False, col=(0.42, 0.27, 0.16)) if False else None
            f.tube(M['wood_dark'], [V(x, -0.024, z), V(x, -0.07, z), V(x, -0.098, z + 0.006)], [0.014, 0.011, 0.0095], seg=10, col=(0.42, 0.27, 0.16))
            f.tube(M['wood_dark'], [V(x + 0.0, -0.098, z + 0.006), V(x + 0.0, -0.1, z + 0.03)], [0.0095, 0.0085], seg=8, col=(0.42, 0.27, 0.16))
            f.lathe(M['wood_dark'], (x, -0.1, z + 0.03), [(0.0085, 0.0), (0.0105, 0.006), (0.0001, 0.012)], r=(0, 0, 0), seg=8, cap=False, col=(0.42, 0.27, 0.16)) if False else None
    # rods
    specs = [(-0.06, 2.1, 'wood_oak', (0.7, 0.5, 0.28), 0.0), (0.06, 1.9, 'wood_pine', (0.82, 0.66, 0.4), 0.0)]
    for k, (z, L, mt, rc, off) in enumerate(specs):
        x0 = -L / 2 + 0.05 * (k - 0.5)
        n = 26
        yb = -0.092
        pts = [V(x0 + L * i / n, yb, z + 0.03 + 0.003 * (i / n) ** 2 + 0.0 + (0.0 if i < n * 0.9 else 0.006 * ((i / n - 0.9) / 0.1) ** 2)) for i in range(n + 1)]
        rad = [0.0125 - 0.0098 * (i / n) ** 0.8 for i in range(n + 1)]
        f.tube(M[mt], pts, rad, seg=7, col=rc, cfn=lambda p: shade(rc, 0.9 + 0.2 * nz(p.x * 60, p.y * 60, p.z * 60)))
        # cork grip + reel seat + ferrule + thread wraps
        f.lathe(M['wood_pine'], (x0 + 0.04, yb, z + 0.03), [(0.0001, 0.0), (0.0125, 0.0), (0.0155, 0.02), (0.0165, 0.1), (0.0145, 0.2), (0.0125, 0.24), (0.0001, 0.245)], r=(0, 90, 0), seg=12, col=(0.76, 0.58, 0.4), cfn=lambda p: shade((0.76, 0.58, 0.4), 0.85 + 0.3 * nz(p.x * 120, p.y * 120, p.z * 120)), cap=False)
        f.lathe(M['brass'], (x0 + 0.285, yb, z + 0.03), [(0.0125, 0.0), (0.016, 0.003), (0.016, 0.07), (0.0125, 0.075)], r=(0, 90, 0), seg=12, cap=False)
        f.lathe(M['brass'], (x0 + 0.02, yb, z + 0.03), [(0.0001, 0.0), (0.0145, 0.0), (0.0165, 0.012), (0.0001, 0.015)], r=(0, 90, 0), seg=12, cap=False)
        f.lathe(M['brass'], (x0 + L * 0.5, yb, z + 0.03), [(0.0085, 0.0), (0.0105, 0.004), (0.0105, 0.05), (0.0085, 0.054)], r=(0, 90, 0), seg=10, cap=False)
        for t_ in (0.2, 0.34, 0.5, 0.64, 0.78):
            q = int(t_ * n)
            xq = x0 + L * q / n
            f.lathe(M['ink'], (xq, yb, pts[q].z), [(rad[q] * 1.1, 0.0), (rad[q] * 1.15, 0.006), (rad[q] * 1.1, 0.012)], r=(0, 90, 0), seg=8, cap=False, col=(0.4, 0.08, 0.08)) if False else None
            f.lathe(M['yarn'], (xq, yb, pts[q].z - 0.0), [(rad[q] * 1.12, -0.0), (rad[q] * 1.16, 0.005), (rad[q] * 1.12, 0.01)], r=(0, 90, 0), seg=8, cap=False, col=(0.55, 0.1, 0.1))
            # guide ring
            ctr = V(xq + 0.005, yb, pts[q].z + rad[q] + 0.012)
            f.tube(M['iron_black'], [ctr + V(0.0, 0.011 * math.cos(a), 0.011 * math.sin(a)) for a in [i * TAU / 10 for i in range(11)]], 0.0009, seg=4, col=(0.5, 0.5, 0.52), caps=False)
            f.tube(M['iron_black'], [V(xq + 0.005, yb, pts[q].z + rad[q]), ctr + V(0, 0, -0.011)], 0.0008, seg=3, col=(0.5, 0.5, 0.52))
        # reel (brass spool) under the grip
        rx = x0 + 0.3
        rc = V(rx, yb, z + 0.03 - 0.034)
        f.lathe(M['brass'], rc, [(0.0001, -0.013), (0.032, -0.013), (0.034, -0.01), (0.034, 0.01), (0.032, 0.013), (0.0001, 0.013)], r=(90, 0, 0), seg=26, cap=False, col=(1, 0.9, 0.7))
        f.lathe(M['iron_black'], rc, [(0.0001, -0.015), (0.015, -0.015), (0.015, 0.015), (0.0001, 0.015)], r=(90, 0, 0), seg=14, cap=False)
        f.tube(M['iron_black'], [rc + V(0.0, 0.016, 0.0), rc + V(0.0, 0.02, 0.025), rc + V(0.0, 0.016, 0.03)], 0.0025, seg=5, col=(0.25, 0.25, 0.28))
        f.cyl(M['wood_dark'], rc + V(0.0, 0.016, 0.03), 0.006, 0.014, axis='y', seg=8, col=(0.5, 0.3, 0.18))
        f.box(M['brass'], (rx, yb, z + 0.03 - 0.012), (0.012, 0.012, 0.03), bev=0.001, col=(1, 0.9, 0.7))
        # line from spool to first guide (a thin tube)
        for ang in range(0, 360, 45):
            a = math.radians(ang)
            f.tube(M['brass'], [rc + V(0.005 * math.cos(a), 0.014, 0.0) * 0 + V(0.0, 0.0155 * math.cos(a), 0.0155 * math.sin(a)) * 0 + V(0.0, 0.0, 0.0), rc], 0.0003, seg=3) if False else None
    # landing net hanging on a hook
    nx_, nz_ = 0.0, -0.15
    hoop_c = V(0.38, -0.05, -0.22)
    hp = [hoop_c + V(0.0, 0.16 * math.sin(a) * 0.0, 0.0) for a in [0]]
    # (net hoop in the xz plane, hanging below the rods)
    hoop = [V(0.33 + 0.12 * math.cos(a), -0.075, -0.2 + 0.15 * math.sin(a)) for a in [i * TAU / 28 for i in range(29)]]
    f.tube(M['wood_oak'], hoop, 0.0065, seg=6, col=(0.7, 0.5, 0.3), caps=False)
    f.tube(M['wood_oak'], [V(0.33, -0.075, -0.05), V(0.33, -0.065, 0.1), V(0.33, -0.05, 0.14)], 0.009, seg=6, col=(0.7, 0.5, 0.3))
    # net threads
    ctrl = V(0.33, -0.075, -0.52)
    for i in range(0, 28, 2):
        a = hoop[i]
        f.tube(M['yarn'], [a, (a + ctrl) / 2 + V(0, -0.02 * 0, 0), ctrl], 0.0009, seg=3, col=(0.78, 0.7, 0.55), caps=False)
    for lv in (0.35, 0.65):
        ring = []
        for i in range(29):
            a = hoop[i % 28]
            q = a * (1 - lv) + ctrl * lv
            ring.append(q)
        f.tube(M['yarn'], ring, 0.0008, seg=3, col=(0.78, 0.7, 0.55), caps=False)
    # creel (wicker fish basket) hanging on a leather strap
    cc0 = f.p(V(-0.32, -0.12, -0.46))
    basket_woven(cc0, r=0.085, h=0.17, seed=5, handle=False)
    lathe(M['wicker'], cc0, [(0.0001, 0.17), (0.09, 0.17), (0.0875, 0.18), (0.0001, 0.19)], seg=16, col=(0.8, 0.6, 0.36), cap=False)
    f.tube(M['leather'], [V(-0.32 - 0.08, -0.12, -0.3), V(-0.32, -0.11, -0.06), V(-0.32 + 0.08, -0.12, -0.3)], 0.004, seg=5, col=(0.4, 0.26, 0.15))
    f.box(M['brass'], (-0.32, -0.095, -0.07), (0.016, 0.006, 0.016), bev=0.001)


# ------------------------------------------------------------------ paintings & frames
def frame_profile(style):
    if style == 'gilt':
        return [(0.0, 0.0), (0.0, 0.004), (0.006, 0.008), (0.012, 0.016), (0.016, 0.026), (0.026, 0.03), (0.034, 0.024), (0.04, 0.012), (0.044, 0.0)][::-1], 'gilt', (1.0, 0.9, 0.62), 0.044
    if style == 'walnut':
        return [(0.0, 0.0), (0.0, 0.012), (0.006, 0.02), (0.016, 0.024), (0.03, 0.022), (0.036, 0.012), (0.036, 0.0)][::-1], 'wood_walnut', (0.42, 0.26, 0.17), 0.036
    if style == 'oak':
        return [(0.0, 0.0), (0.0, 0.01), (0.004, 0.016), (0.012, 0.018), (0.024, 0.014), (0.03, 0.006), (0.03, 0.0)][::-1], 'wood_oak', (0.7, 0.5, 0.3), 0.03
    return [(0.0, 0.0), (0.0, 0.008), (0.01, 0.014), (0.022, 0.014), (0.028, 0.006), (0.028, 0.0)][::-1], 'wood_painted', (0.86, 0.82, 0.72), 0.028


def painting(pos, normal, n, style='gilt', tilt=0.0):
    """framed painting n at pos (world centre of the canvas) on a wall whose outward normal is `normal` (2D)."""
    kind, cw, ch = PAINT_SPEC[n]
    rot = rot_from_normal(normal[0], normal[1])
    f = Fr(pos, rot, None)
    if tilt:
        f.M = f.M @ rotm((tilt, 0, 0))
        f.p = lambda l, M_=f.M: M_ @ Vector(l)
    # local axes: x width, y out of the wall (towards the room), z up.  frame profile built in XZ plane, thickness along y.
    prof, mname, mcol, fw = frame_profile(style)
    mat = M[mname]
    if mname == 'gilt':
        vc = lambda p: shade(mcol, 0.85 + 0.25 * nz(p.x * 50, p.y * 50, p.z * 50))
    elif mname == 'wood_painted':
        def vc(p, n=n):
            ch = fbm(p.x * 55, p.y * 55, p.z * 55, 1.0, n, 2)
            if ch > 0.2:
                return (0.42, 0.31, 0.21)       # chipped paint exposing bare wood
            k = 0.94 + 0.1 * nz(p.x * 30, p.y * 30, p.z * 30)
            return (mcol[0] * k, mcol[1] * k, mcol[2] * k)
    else:
        vc = wood_vc(mcol, 0.14, 9, 90 + n, axis=2)
    # the rect path lives in local XY of a frame whose z is +y_local; build with matrix mapping sweep (x,y,z)->(x, z->y_out, y->z)
    Mf = f.M @ Matrix.Rotation(math.radians(90), 4, 'X')   # sweep-space (x,y,z) -> local (x, -z, y)... y_out = -z
    path = rrect(cw + 0.006, ch + 0.006, 0.003, 1)
    # outward is +a; profile height b is along sweep z => local -y.  we want the frame to project towards +y_local, so flip z.
    Mf = f.M @ Matrix.Rotation(math.radians(90), 4, 'X') @ Matrix.Scale(-1, 4, (0, 0, 1))
    bm = sweep_bm(path, [(-a_ if False else -a, b) for (a, b) in [(-0.0, 0.0)]] if False else [(a + 0.0, b) for (a, b) in prof], True, uvm=1.0, flip=True)
    put(mat, bm, Mf, mcol, vc, 2, uv_abs=True)
    bm.free()
    # rear closing (back board) and slip liner
    f.box(M['wood_pine'], (0, 0.004, 0), (cw + 0.01, 0.008, ch + 0.01), bev=0, col=(0.3, 0.22, 0.16))
    # gilt liner slip
    bm = sweep_bm(rrect(cw + 0.004, ch + 0.004, 0.002, 1), [(0.0, 0.0), (0.0, 0.012), (-0.004, 0.012), (-0.004, 0.0)], True, 1.0, flip=True)
    put(M['gilt'], bm, Mf, (1, 0.9, 0.62), None, 2, uv_abs=True)
    bm.free()
    # canvas: slightly bulging grid with UV 0..1
    pm = painting_mat(n)
    nx, ny = 10, 10
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    Vv = [[bm.verts.new((-cw / 2 + cw * i / nx, 0.0095 + 0.002 * math.sin(i / nx * math.pi) * math.sin(j / ny * math.pi), -ch / 2 + ch * j / ny)) for j in range(ny + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(ny):
            fc = bm.faces.new([Vv[i][j], Vv[i][j + 1], Vv[i + 1][j + 1], Vv[i + 1][j]])
            fc.smooth = True
            for l, uv in zip(fc.loops, [(i / nx, j / ny), (i / nx, (j + 1) / ny), ((i + 1) / nx, (j + 1) / ny), ((i + 1) / nx, j / ny)]):
                l[ul].uv = uv
    put(pm, bm, f.M, (1, 1, 1), None, 2, uv_abs=True)
    bm.free()
    # corner rosettes (gilt) and hanging wire with hook
    if style == 'gilt':
        for sx in (-1, 1):
            for sz in (-1, 1):
                f.lathe(M['gilt'], (sx * (cw / 2 + 0.024), 0.026, sz * (ch / 2 + 0.024)), [(0.0001, 0.0), (0.011, 0.0), (0.011, 0.002), (0.006, 0.006), (0.0001, 0.008)], r=(-90, 0, 0), seg=10, cap=False) if False else None
                sphere(M['gilt'], f.p(V(sx * (cw / 2 + 0.024), 0.028, sz * (ch / 2 + 0.024))), 0.009, seg=8, rings=4, sq=(1, 0.5, 1), col=(1, 0.9, 0.62))
    top = ch / 2 + 0.02
    f.tube(M['brass'], [V(-cw / 2 + 0.03, 0.011, top - 0.035 + 0.0), V(0, 0.011, top + 0.06), V(cw / 2 - 0.03, 0.011, top - 0.035)], 0.0008, seg=3, col=(0.8, 0.7, 0.4))
    f.tube(M['brass'], [V(0.0, 0.0, top + 0.06), V(0.0, 0.012, top + 0.06)], 0.002, seg=4) if False else None
    sphere(M['brass'], f.p(V(0, 0.004, top + 0.062)), 0.003, seg=6, rings=3)
    return f


# ------------------------------------------------------------------ wall shelf with knick-knacks
def wall_shelf(pos, rot, W=0.72, D=0.2, seed=3):
    """pos = wall mounting point (centre, shelf top z). local +y points into the room."""
    f = Fr(pos, rot, None)
    rr = random.Random(seed)
    vc = wood_vc((0.55, 0.36, 0.2), 0.16, 8, 101 + seed, axis=0)
    mat = M['wood_oak']
    f.box(mat, (0, D / 2, -0.0125), (W, D, 0.025), bev=0.003, cfn=vc, g=0, cuts=2)
    moulding(mat, f.M @ Matrix.Translation((0, D / 2, -0.025)), rrect(W, D, 0.005, 1), [(-0.008, 0.0), (0.0, 0.0), (0.006, 0.006), (0.004, 0.014), (-0.008, 0.025)], cfn=vc, g=0) if False else None
    f.box(mat, (0, D - 0.004, -0.04), (W - 0.01, 0.02, 0.03), bev=0.003, cfn=vc, g=0)
    # back gallery rail with small turned balusters
    f.box(mat, (0, 0.012, 0.045), (W, 0.014, 0.012), bev=0.002, cfn=vc, g=0)
    for i in range(int(W / 0.05)):
        x = -W / 2 + 0.035 + i * 0.05
        f.lathe(mat, (x, 0.012, 0.0), [(0.0001, 0.0), (0.005, 0.0), (0.004, 0.012), (0.006, 0.02), (0.004, 0.03), (0.005, 0.039), (0.0001, 0.039)], seg=8, col=(0.55, 0.36, 0.2)) if False else f.lathe(mat, (x, 0.012, 0.0), [(0.0001, 0.0), (0.005, 0.0), (0.004, 0.012), (0.006, 0.02), (0.004, 0.03), (0.005, 0.039), (0.0001, 0.039)], seg=8, col=(0.55, 0.36, 0.2))
    # carved scroll brackets
    for s in (-1, 1):
        x = s * (W / 2 - 0.07)
        sp = []
        for k in range(18):
            t = k / 17
            a = t * math.pi * 2.0
            r_ = 0.06 * (1 - t * 0.78)
            sp.append(V(x, 0.02 + 0.12 * (1 - t) ** 0.6 * 0 + r_ * math.cos(a + 3.2) + 0.075, -0.03 - 0.1 * (1 - t * 0.6) * 0 - 0.075 + r_ * math.sin(a + 3.2) + 0.0))
        f.tube(mat, sp, [0.011 - 0.007 * i / 17 for i in range(18)], seg=7, col=(0.55, 0.36, 0.2))
        f.box(mat, (x, 0.012, -0.075), (0.022, 0.016, 0.1), bev=0.002, col=(0.55, 0.36, 0.2))
        f.box(mat, (x, 0.08, -0.04), (0.022, 0.12, 0.012), bev=0.002, col=(0.55, 0.36, 0.2), g=1)
        for dz in (-0.1, -0.05):
            f.cyl(M['brass'], (x, 0.0, dz), 0.0045, 0.004, axis='y', seg=8)
    # knick-knacks on top
    zt = 0.0
    items = ['teacup', 'bird', 'jar', 'books', 'frame', 'candle', 'vase', 'shells', 'bowl']
    rr.shuffle(items)
    x = -W / 2 + 0.07
    for it in items[:6]:
        if x > W / 2 - 0.05:
            break
        q = f.p(V(x, 0.1 + rr.uniform(-0.02, 0.03), 0.0))
        rz = f.rot
        if it == 'teacup':
            saucer(q, rz, seed=4); teacup(q + V(0, 0, 0.0055), rot=rz + 40, seed=2, tea=False); x += 0.13
        elif it == 'bird':
            figurine_bird(q, rz + 180 + rr.uniform(-25, 25), col=rr.choice(['#c8b080', '#8aa0b0', '#b07050'])); x += 0.11
        elif it == 'jar':
            jar(q, r=0.04, h=0.12, content=(0.7, rr.choice([(0.8, 0.5, 0.2), (0.6, 0.18, 0.12)])), lidcol=(0.75, 0.6, 0.3)); x += 0.11
        elif it == 'books':
            zz = book_flat_stack(Matrix.Translation(q) @ rotm((0, 0, rz + 180)), 3, rr, rot=rr.uniform(-6, 6)); x += 0.27
        elif it == 'frame':
            photo_frame(q, rz + 180, w=0.11, h=0.15, tilt=11, seed=rr.randint(0, 99), fcol=(0.5, 0.33, 0.22)); x += 0.13
        elif it == 'candle':
            candlestick(q, h=0.12, kind='pewter', cl=0.08, lit=False, wax=True, seed=rr.randint(0, 99)); x += 0.1
        elif it == 'vase':
            vase_dried(q, h=0.14, r=0.035, seed=rr.randint(0, 99), vcol=rr.choice(['#b5562f', '#4a5f8a', '#d9c7a0']), stems=7); x += 0.13
        elif it == 'shells':
            for k in range(2):
                lathe(M['ceramic'], q + V(0.025 * k, 0.0, 0.0), [(0.001, 0), (0.022, 0.0), (0.026, 0.01), (0.014, 0.022), (0.001, 0.025)], seg=12, cap=False, col=(0.95, 0.88, 0.8), rot=(0, 0, rr.uniform(0, 360)), scale=(1, 0.8, 0.9))
            x += 0.11
        else:
            bowl(q, r=0.06, h=0.035, col=C('#4e7299')); x += 0.14
    return f


# ------------------------------------------------------------------ curtains (cloth-simulated, animated part)
def curtain_window(n, cx, cy, zt, w, drop, rot, col='#c9b79a', tied=True, nframes=80):
    """rod + rings (static) and two cloth-simulated panels (separate part 'curtain_liv_<n>', pivot at the rod)."""
    f = Fr((cx, cy, zt), rot, None)
    rod_y = -0.055   # for rot=180 on the front wall, local -y is into the room
    mw = M['wood_dark']
    f.cyl(mw, (0, rod_y, 0), 0.0115, w + 0.16, axis='x', seg=12, col=(0.42, 0.27, 0.17))
    for s in (-1, 1):
        f.lathe(mw, (s * (w / 2 + 0.09), rod_y, 0), [(0.0001, -0.012), (0.012, -0.01), (0.02, 0.0), (0.02, 0.01), (0.011, 0.02), (0.0001, 0.026)], r=(0, 90 * s, 0), seg=14, col=(0.42, 0.27, 0.17), cap=False)
        f.box(M['iron_black'], (s * (w / 2 + 0.03), rod_y / 2, 0.0), (0.014, abs(rod_y), 0.014), bev=0.002, col=(0.25, 0.25, 0.27))
        f.box(M['iron_black'], (s * (w / 2 + 0.03), 0.0, 0.0), (0.03, 0.006, 0.05), bev=0.001, col=(0.25, 0.25, 0.27))
    saved = part_begin()
    base = C(col)
    cfn_base = fab(base, 0.09, 9, n)
    NX, NY = 24, 20
    pw = w * 0.36
    for side in (-1, 1):
        # pleated panel: fabric width 1.9x the panel width, gathered at the top
        fw_ = pw * 1.9
        bm = bmesh.new()
        Vv = [[None] * (NY + 1) for _ in range(NX + 1)]
        npl = 6
        for i in range(NX + 1):
            u = i / NX
            xlin = -pw / 2 + pw * u
            for j in range(NY + 1):
                v = j / NY
                amp = 0.03 * (1 - 0.55 * v)
                y = amp * math.sin(u * npl * math.pi * 2 + side)
                # fabric arc length: path stretched in x by gather ratio
                Vv[i][j] = bm.verts.new((xlin, rod_y - 0.02 + y, -0.02 - drop * v))
        for i in range(NX):
            for j in range(NY):
                bm.faces.new([Vv[i][j], Vv[i + 1][j], Vv[i + 1][j + 1], Vv[i][j + 1]])
        Mp = f.M @ Matrix.Translation((side * (w / 2 - pw / 2 + 0.0), 0, 0))
        for v in bm.verts:
            v.co = Mp @ v.co
        # cloth sim: pin the top row. rest lengths come from the initial (gathered, wavy) shape -> keeps folds
        def pin(v):
            return 1.0 if (v.co - f.p(V(0, 0, 0))).z > -0.03 else 0.0
        pos = cloth_sim(bm, pin, [], frames=nframes, quality=7, mass=0.22, tension=12, compression=12, shear=6, bending=0.15, damping=1.2, self_col=True, thickness=0.01, extra=None) if SIM else [v.co.copy() for v in bm.verts]
        for v, p_ in zip(bm.verts, pos):
            v.co = p_
        # tie-back pinch toward the outer side at ~60% drop
        zt_back = f.pos.z - drop * 0.62
        outer = f.p(V(side * (w / 2 + 0.02), 0, 0))
        if tied:
            for v in bm.verts:
                dz = v.co.z - zt_back
                g = math.exp(-(dz / 0.16) ** 2)
                v.co.x += (outer.x - v.co.x) * 0.0
                lv = f.M.inverted() @ v.co
                lv.x += (side * (w / 2 + 0.05) - lv.x) * 0.55 * g
                lv.y += (rod_y - 0.012 - lv.y) * 0.5 * g
                v.co = f.M @ lv
        bm = modbm(bm, [('SOLIDIFY', dict(thickness=0.003, offset=0.0))])
        put(M['curtain'], bm, Matrix.Identity(4), (1, 1, 1), lambda p: cfn_base(p), 2)
        bm.free()
        # rings on the rod
        for k in range(10):
            xr = side * (w / 2 - pw + pw * k / 9.0 * 1.0 - pw * 0.0) + (0 if True else 0)
            xr = side * (w / 2 - pw / 2) - pw / 2 + pw * k / 9
            tube(M['brass'], [f.p(V(xr + 0.0045 * math.cos(a) * 0.0, rod_y + 0.016 * math.sin(a), 0.016 * math.cos(a) + 0.0)) for a in [i * TAU / 12 for i in range(13)]], 0.0016, seg=4, col=(1, 0.9, 0.7), caps=False)
        # tie-back cord with tassel
        if tied:
            pass
    part_end(saved, 'curtain_liv_%d' % n, f.p(V(0, rod_y, 0)))
    # tie-back sash (static): cord loop + tassel at each side + hook
    if tied:
        for side in (-1, 1):
            zc = f.pos.z - drop * 0.62
            c0 = f.M @ V(side * (w / 2 + 0.07), rod_y + 0.02, 0)
            hook = Vector((c0.x, c0.y, zc))
            f.box(M['brass'], (side * (w / 2 + 0.17), 0.0, zc - f.pos.z), (0.012, 0.014, 0.012), bev=0.002) if False else None
            sphere(M['brass'], f.M @ V(side * (w / 2 + 0.16), -0.012, zc - f.pos.z), 0.011, seg=8, rings=5, sq=(1, 0.5, 1))
            tube(M['yarn'], [f.M @ V(side * (w / 2 + 0.16), 0.016, zc - f.pos.z), f.M @ V(side * (w / 2 + 0.11), rod_y + 0.035, zc - f.pos.z + 0.0), f.M @ V(side * (w / 2 + 0.0), rod_y + 0.04, zc - f.pos.z - 0.025)], 0.0035, seg=5, col=(0.7, 0.55, 0.35), caps=False) if False else None
            # tassel hanging below the pinch
            tp = f.M @ V(side * (w / 2 + 0.05), rod_y - 0.045, zc - f.pos.z - 0.0)
            tube(M['yarn'], [tp, tp + V(0, 0, -0.05)], 0.004, seg=5, col=(0.72, 0.58, 0.36), caps=True)
            sphere(M['yarn'], tp + V(0, 0, -0.055), 0.008, seg=7, rings=4, col=(0.72, 0.58, 0.36))
            for k in range(10):
                a = k / 10 * TAU
                tube(M['yarn'], [tp + V(0.003 * math.cos(a), 0.003 * math.sin(a), -0.058), tp + V(0.006 * math.cos(a), 0.006 * math.sin(a), -0.1)], 0.0013, seg=3, col=(0.7, 0.55, 0.34), caps=False)
