"""Kitchen + entry"""
from int_lib import *
from int_mats import M
from int_items import *
from int_furn1 import *


def panel_door(f, cx, cz, w, h, mat='wood_blue', y=0.0, knob=True, sign=1, inset=True):
    """door on front plane of frame f (local +y). cx,cz centre; y = front face position."""
    col = (1, 0.97, 0.94)
    t = 0.022
    f.box(M[mat], (cx, y, cz), (w, t, h), bev=0.004, col=col, g=2 if h > w else 0)
    if inset:
        f.box(M[mat], (cx, y + 0.008, cz), (w - 0.1, 0.008, h - 0.1), bev=0.004, col=(0.9, 0.88, 0.85))
        f.box(M[mat], (cx, y + 0.012, cz), (w - 0.14, 0.004, h - 0.14), bev=0.002, col=(1.05, 1.03, 1.0))
    if knob:
        kx = cx + sign * (w / 2 - 0.05)
        f.lathe(M['brass'], (kx, y + 0.011, cz + (0.0 if h < 0.6 else 0.0)), [(0.001, 0), (0.014, 0), (0.008, 0.01), (0.014, 0.022), (0.001, 0.024)], r=(-90, 0, 0), seg=10, cap=False)


def drawer(f, cx, cz, w, h, mat='wood_blue', y=0.0):
    f.box(M[mat], (cx, y, cz), (w, 0.022, h), bev=0.004, col=(1, 0.97, 0.94), g=0)
    f.box(M[mat], (cx, y + 0.011, cz), (w - 0.06, 0.006, h - 0.05), bev=0.003, col=(0.92, 0.9, 0.86), g=0)
    f.tube(M['brass'], [Vector((cx - 0.05, y + 0.02, cz)), Vector((cx - 0.05, y + 0.04, cz)), Vector((cx + 0.05, y + 0.04, cz)), Vector((cx + 0.05, y + 0.02, cz))], 0.005, seg=6)


def cabinet_carcass(f, W, D, H, mat='wood_oak', plinth=0.08):
    col = (0.95, 0.9, 0.85)
    t = 0.022
    f.box(M[mat], (0, 0, plinth / 2), (W - 0.02, D - 0.04, plinth), bev=0.002, col=(0.6, 0.5, 0.45))
    for s in (-1, 1):
        f.box(M[mat], (s * (W / 2 - t / 2), 0, (H + plinth) / 2), (t, D, H - plinth), bev=0.003, col=col, cuts=2)
    f.box(M[mat], (0, -D / 2 + 0.01, (H + plinth) / 2), (W - 2 * t, 0.015, H - plinth), bev=0, col=(0.85, 0.8, 0.75))
    f.box(M[mat], (0, 0, plinth + 0.011), (W - 2 * t, D - 0.04, 0.022), bev=0.002, col=col)


# ====================================================================== stove
def cookstove(pos, rot=180):
    f = Fr(pos, rot, F)
    W, D = 0.74, 0.56
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.lathe(M['iron_cast'], (sx * (W / 2 - 0.045), sy * (D / 2 - 0.045), 0), [(0.02, 0), (0.035, 0.02), (0.022, 0.07), (0.04, 0.14)], seg=8)
    f.box(M['iron_black'], (0, 0, 0.46), (W - 0.04, D - 0.04, 0.64), bev=0.012)
    # side heat shield / ribs
    for s in (-1, 1):
        for k in range(3):
            f.box(M['iron_cast'], (s * (W / 2 - 0.018), 0, 0.3 + k * 0.17), (0.012, D - 0.12, 0.012), bev=0.002)
    f.box(M['iron_cast'], (0, 0, 0.795), (W, D, 0.032), bev=0.008)
    # lids
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 0.17, sy * 0.11 + 0.0
            f.cyl(M['iron_cast'], (x, y, 0.816), 0.082, 0.012, seg=20)
            f.cyl(M['iron_black'], (x, y, 0.824), 0.06, 0.006, seg=18)
            f.box(M['iron_cast'], (x, y, 0.828), (0.03, 0.008, 0.008), bev=0.001)
    # front doors
    yf = D / 2 - 0.02
    f.box(M['iron_cast'], (-0.19, yf + 0.012, 0.6), (0.24, 0.022, 0.26), bev=0.008)
    f.box(M['iron_black'], (-0.19, yf + 0.026, 0.6), (0.17, 0.008, 0.19), bev=0.004)
    for k in range(5):
        f.box(M['ink'], (-0.19, yf + 0.032, 0.54 + k * 0.03), (0.12, 0.002, 0.006), bev=0, col=(0.02, 0.02, 0.02))
    f.box(M['iron_cast'], (0.15, yf + 0.012, 0.47), (0.32, 0.022, 0.4), bev=0.008)
    f.box(M['iron_black'], (0.15, yf + 0.026, 0.47), (0.25, 0.008, 0.33), bev=0.004)
    f.box(M['iron_cast'], (-0.19, yf + 0.012, 0.36), (0.24, 0.022, 0.1), bev=0.006)
    f.tube(M['tin'], [Vector((-0.04, yf + 0.02, 0.36)), Vector((-0.04, yf + 0.05, 0.36)), Vector((0.04, yf + 0.05, 0.36)) - Vector((0.08, 0, 0)) + Vector((0.08, 0, 0)), Vector((-0.34, yf + 0.05, 0.36)) + Vector((0.3, 0, 0)), Vector((-0.34, yf + 0.02, 0.36)) + Vector((0.3, 0, 0))], 0.005, seg=6) if False else None
    f.tube(M['tin'], [Vector((-0.04, yf + 0.02, 0.6)), Vector((-0.04, yf + 0.045, 0.6)), Vector((-0.04, yf + 0.045, 0.66)), Vector((-0.04, yf + 0.02, 0.66))], 0.006, seg=6)
    f.tube(M['tin'], [Vector((0.03, yf + 0.02, 0.32)), Vector((0.03, yf + 0.05, 0.32)), Vector((0.03, yf + 0.05, 0.6)), Vector((0.03, yf + 0.02, 0.6))], 0.007, seg=6)
    f.box(M['tin'], (0.0, yf + 0.004, 0.72), (W - 0.06, 0.012, 0.035), bev=0.004)
    f.box(M['tin'], (0.0, yf + 0.004, 0.2), (W - 0.06, 0.012, 0.02), bev=0.003)
    f.lathe(M['tin'], (0.15, yf + 0.024, 0.66), [(0.001, 0), (0.014, 0), (0.014, 0.02), (0.001, 0.02)], r=(-90, 0, 0), seg=8)
    # warming shelf
    for s in (-1, 1):
        f.tube(M['iron_black'], [Vector((s * (W / 2 - 0.03), -D / 2 + 0.05, 0.81)), Vector((s * (W / 2 - 0.03), -D / 2 + 0.05, 1.22))], 0.012, seg=8)
    f.box(M['iron_black'], (0, -D / 2 + 0.1, 1.22), (W, 0.22, 0.014), bev=0.004)
    f.tube(M['iron_black'], [Vector((-W / 2 + 0.03, -D / 2 + 0.2, 1.23)), Vector((-W / 2 + 0.03, -D / 2 + 0.2, 1.3)), Vector((W / 2 - 0.03, -D / 2 + 0.2, 1.3)), Vector((W / 2 - 0.03, -D / 2 + 0.2, 1.23))], 0.006, seg=6)
    # flue
    fx, fy = 0.0, -D / 2 + 0.11
    f.cyl(M['iron_black'], (fx, fy, 0.82), 0.092, 0.03, seg=16)
    top = 3.17 - F
    f.cyl(M['iron_black'], (fx, fy, (0.83 + top) / 2), 0.072, top - 0.83, seg=16)
    for z in (1.3, 1.9, 2.5):
        f.cyl(M['iron_cast'], (fx, fy, z), 0.082, 0.04, seg=16)
    f.cyl(M['iron_black'], (fx, fy, 2.83 - F + 0.3), 0.092, 0.05, seg=16)
    f.lathe(M['iron_cast'], (fx, fy, 2.6), [(0.078, 0), (0.078, 0.004)], seg=16, cap=False) if False else None
    # damper knob on pipe
    f.box(M['brass'], (fx + 0.072, fy, 1.05 + 0.3), (0.05, 0.012, 0.012), bev=0.002)
    collider_f(f, W, D, F + 0.83)
    return f


def kettle_anchor(tip):
    saved = part_begin()
    box(M['iron_cast'], tip, (0.008, 0.008, 0.008), bev=0)
    part_end(saved, 'kettle_steam_anchor', tip)


# ====================================================================== counter + sink
def kitchen_counter(xc, y_back, W=1.6, D=0.6, H=0.9, sink_world_x=-2.2):
    f = Fr((xc, y_back - D / 2, F), 180)
    cabinet_carcass(f, W, D, H - 0.04, 'wood_white')
    # doors / drawers (front at local y = D/2)
    yf = D / 2 - 0.004
    n = 3
    dw = (W - 0.04) / n
    for i in range(n):
        cx = -W / 2 + 0.02 + dw * (i + 0.5)
        if i == 1:
            drawer(f, cx, H - 0.15, dw - 0.008, 0.16, 'wood_green', yf)
            panel_door(f, cx, 0.36, dw - 0.008, 0.52, 'wood_green', yf, sign=-1)
        else:
            panel_door(f, cx, (H - 0.04 + 0.08) / 2 - 0.02, dw - 0.008, H - 0.16, 'wood_green', yf, sign=1 if i == 0 else -1)
    # worktop with sink cut-out
    sl = -2.2
    lx = xc - sink_world_x   # local x of sink centre (rot 180 flips)
    hw, hd = 0.26, 0.17
    cy = 0.0
    top_z = H - 0.02
    t = 0.04
    wc = dict(g=0, cuts=3)
    f.box(M['wood_oak'], ((-W / 2 - 0.02 + lx - hw) / 2 , 0.02, top_z), (lx - hw + W / 2 + 0.02, D + 0.05, t), bev=0.006, col=(1, 0.96, 0.92), **wc)
    f.box(M['wood_oak'], ((W / 2 + 0.02 + lx + hw) / 2, 0.02, top_z), (W / 2 + 0.02 - lx - hw, D + 0.05, t), bev=0.006, col=(0.95, 0.9, 0.86), **wc)
    yb = -D / 2 - 0.0
    f.box(M['wood_oak'], (lx, (yb + (cy - hd)) / 2 - 0.0, top_z), (2 * hw, (cy - hd) - yb + 0.0, t), bev=0.005, col=(1, 0.95, 0.9), g=0)
    f.box(M['wood_oak'], (lx, ((cy + hd) + (D / 2 + 0.045)) / 2, top_z), (2 * hw, D / 2 + 0.045 - (cy + hd), t), bev=0.005, col=(1, 0.95, 0.9), g=0)
    # basin
    bz = 0.68
    f.box(M['enamel_white'], (lx, cy, bz + 0.01), (2 * hw - 0.02, 2 * hd - 0.02, 0.014), bev=0.004)
    for s in (-1, 1):
        f.box(M['enamel_white'], (lx + s * (hw - 0.008), cy, (bz + top_z) / 2), (0.014, 2 * hd, top_z - bz + 0.02), bev=0.003)
        f.box(M['enamel_white'], (lx, cy + s * (hd - 0.008), (bz + top_z) / 2), (2 * hw, 0.014, top_z - bz + 0.02), bev=0.003)
    f.box(M['water'], (lx, cy, bz + 0.03), (2 * hw - 0.04, 2 * hd - 0.04, 0.004), bev=0)
    f.box(M['tin'], (lx, cy, bz + 0.018), (0.04, 0.04, 0.004), bev=0.001)
    # hand pump at back edge
    py = -D / 2 + 0.04
    base = Vector((lx, py, top_z + t / 2))
    f.cyl(M['iron_black'], (lx, py, base.z + 0.01), 0.055, 0.02, seg=12, bev=0.004)
    f.cyl(M['iron_black'], (lx, py, base.z + 0.16), 0.03, 0.3, seg=12)
    f.cyl(M['iron_black'], (lx, py, base.z + 0.3), 0.038, 0.02, seg=12)
    f.box(M['iron_black'], (lx, py + 0.03, base.z + 0.35), (0.06, 0.12, 0.07), bev=0.008)
    f.tube(M['brass'], [Vector((lx, py + 0.05, base.z + 0.34)), Vector((lx, py + 0.13, base.z + 0.34)), Vector((lx, py + 0.17, base.z + 0.3)), Vector((lx, py + 0.17, base.z + 0.24))], [0.014, 0.012, 0.011, 0.01], seg=8)
    f.tube(M['iron_black'], [Vector((lx, py - 0.01, base.z + 0.37)), Vector((lx, py - 0.1, base.z + 0.36)), Vector((lx, py - 0.17, base.z + 0.3))], 0.008, seg=6)
    f.cyl(M['wood_dark'], (lx, py - 0.18, base.z + 0.3), 0.014, 0.1, seg=8, axis='x')
    f.cyl(M['iron_black'], (lx, py, base.z + 0.36), 0.012, 0.09, axis='x', seg=8)
    collider_f(f, W, D + 0.05, F + H)
    return f


# ====================================================================== hutch / pantry / shelves
def plate_row(f, x0, x1, z, y, n, r=0.11, tint=(1, 1, 1), cols=None):
    for i in range(n):
        x = x0 + (x1 - x0) * i / max(n - 1, 1)
        q = f.p((x, y, 0.0)); q.z = F + z
        c = cols[i % len(cols)] if cols else tint
        plate(q + V(0, 0, 0.0), r=r, col=C(c) if isinstance(c, str) else c, tilt=(-72, 0, f.rot), rim=None)


def hutch(pos, rot, W=1.0, D=0.42, H=2.08):
    f = Fr(pos, rot, F)
    cabinet_carcass(f, W, D, 0.9, 'wood_oak')
    yf = D / 2 - 0.004
    panel_door(f, -W / 4 + 0.01, 0.46, W / 2 - 0.03, 0.66, 'wood_red', yf, sign=1)
    panel_door(f, W / 4 - 0.01, 0.46, W / 2 - 0.03, 0.66, 'wood_red', yf, sign=-1)
    drawer(f, -W / 4 + 0.01, 0.84, W / 2 - 0.03, 0.12, 'wood_red', yf)
    drawer(f, W / 4 - 0.01, 0.84, W / 2 - 0.03, 0.12, 'wood_red', yf)
    f.box(M['wood_dark'], (0, 0.01, 0.92), (W + 0.04, D + 0.03, 0.035), bev=0.006, cuts=3, g=0, col=(1, 0.96, 0.92))
    # upper open part
    uh = H - 0.94
    for s in (-1, 1):
        f.box(M['wood_oak'], (s * (W / 2 - 0.011), -0.05, 0.94 + uh / 2), (0.022, D - 0.14, uh), bev=0.003, col=(0.95, 0.9, 0.86), cuts=2)
    f.box(M['wood_white'], (0, -D / 2 + 0.09, 0.94 + uh / 2), (W - 0.04, 0.012, uh), bev=0, col=(0.9, 0.88, 0.82))
    f.box(M['wood_oak'], (0, -0.05, H - 0.02), (W + 0.03, D - 0.12, 0.04), bev=0.006, col=(1, 0.95, 0.9), g=0, cuts=2)
    f.box(M['wood_oak'], (0, -0.05, H + 0.01), (W + 0.06, D - 0.08, 0.025), bev=0.006, col=(1, 0.95, 0.9), g=0)
    shelves = [1.3, 1.65]
    for z in shelves:
        f.box(M['wood_oak'], (0, -0.05, z), (W - 0.04, D - 0.14, 0.022), bev=0.003, col=(1, 0.95, 0.9), g=0)
        f.box(M['wood_oak'], (0, D / 2 - 0.1, z + 0.02), (W - 0.04, 0.012, 0.03), bev=0.002, col=(1, 0.95, 0.9), g=0)
    # plates standing in rail
    cols = ['#e9e4d8', '#e9e4d8', '#dcd6c6']
    for z in shelves:
        for i in range(5):
            x = -W / 2 + 0.12 + i * 0.19
            q = f.p((x, D / 2 - 0.11, 0)); q.z = F + z + 0.011
            plate(q, r=0.1, col=C(rnd.choice(['#ece7da', '#e0d9c6', '#d7e0dc'])), tilt=(-78, 0, f.rot + 180))
    # top shelf: cups & jugs
    z = 0.94 + 0.035
    for i in range(4):
        q = f.p((-0.35 + i * 0.045, 0.02, 0)); q.z = F + 0.955
        mug(q, col=C(rnd.choice(['#4e7299', '#c44a3a', '#e9e4d8', '#6a8f5a'])), rot=f.rot + 90 * 0, r=0.036, h=0.08)
    q = f.p((0.22, 0.0, 0)); q.z = F + 0.955
    teapot(q, rot=f.rot, col=C('#e9e4d8'))
    # mid shelf: jars / bowls
    for i in range(3):
        q = f.p((-0.3 + i * 0.12, 0.0, 0)); q.z = F + 1.3 + 0.011
        jar(q, r=0.05, h=0.14, content=(0.75, rnd.choice([(0.85, 0.75, 0.4), (0.7, 0.2, 0.15), (0.5, 0.65, 0.25)])), lidcol=(0.7, 0.5, 0.25))
    q = f.p((0.22, 0.0, 0)); q.z = F + 1.3 + 0.011
    bowl(q, r=0.11, h=0.06, col=C('#4e7299'), mat='ceramic_vc')
    q = f.p((0.34, 0.0, 0)); q.z = F + 1.3 + 0.011
    bowl(q, r=0.07, h=0.045, col=C('#e9e4d8'), mat='ceramic_vc')
    # top of hutch: pitcher + basket
    q = f.p((-0.3, -0.05, 0)); q.z = F + H + 0.022
    vase_flowers(q, 'dried', h=0.2, r=0.06, n=7, vcol='#d9c7a0', seed=5)
    q = f.p((0.25, -0.05, 0)); q.z = F + H + 0.022
    basket(q, r=0.12, h=0.12, handle=True, rot=(0, 0, f.rot))
    # cup hooks under shelf
    for i in range(5):
        x = -0.35 + i * 0.17
        q = f.p((x, D / 2 - 0.1, 0)); q.z = F + shelves[0] - 0.015
        sphere(M['brass'], q, 0.008, seg=6, rings=3)
    collider_f(f, W + 0.04, D + 0.04, F + H)
    return f


def pantry(pos, rot, W=0.66, D=0.5, H=2.15):
    f = Fr(pos, rot, F)
    cabinet_carcass(f, W, D, H - 0.06, 'wood_oak', plinth=0.1)
    f.box(M['wood_oak'], (0, 0, H - 0.03), (W + 0.04, D + 0.03, 0.06), bev=0.008, cuts=2, g=0, col=(1, 0.95, 0.9))
    f.box(M['wood_dark'], (0, 0, H + 0.005), (W + 0.07, D + 0.05, 0.03), bev=0.006, g=0)
    yf = D / 2 - 0.004
    panel_door(f, 0, 1.45, W - 0.04, 1.3, 'wood_green', yf, sign=-1)
    panel_door(f, 0, 0.47, W - 0.04, 0.72, 'wood_green', yf, sign=-1)
    # hinges
    for z in (0.8, 1.1, 1.75, 2.0, 0.25, 0.65):
        f.box(M['iron_black'], (W / 2 - 0.05 + 0.018, yf + 0.014, z), (0.1, 0.008, 0.02), bev=0.002)
    # vent grille (perforated)
    for i in range(3):
        for j in range(6):
            f.cyl(M['ink'], (-0.15 + j * 0.06, yf + 0.012, 1.85 + i * 0.05), 0.011, 0.004, axis='y', seg=8, col=(0.02, 0.02, 0.02))
    collider_f(f, W + 0.04, D + 0.03, F + H)
    return f


def wall_shelf(pos, rot, W=0.7, D=0.2, z=0.0, items='dishes', seed=0):
    rr = random.Random(seed)
    f = Fr(pos, rot, None)
    f.box(M['wood_oak'], (0, 0, 0), (W, D, 0.025), bev=0.004, col=(1, 0.95, 0.9), g=0, cuts=2)
    for s in (-1, 1):
        f.box(M['iron_black'], (s * (W / 2 - 0.08), -D / 2 + 0.008, -0.07), (0.012, 0.016, 0.12), bev=0.002)
        f.tube(M['iron_black'], [Vector((s * (W / 2 - 0.08), -D / 2 + 0.01, -0.12)), Vector((s * (W / 2 - 0.08), D / 2 - 0.03, -0.0125))], 0.006, seg=5)
    top = f.p((0, 0, 0.0125))
    x = -W / 2 + 0.07
    while x < W / 2 - 0.06:
        k = rr.choice(['mug', 'jar', 'bowl', 'plate', 'book'])
        q = f.p((x, 0.0, 0.0125))
        if k == 'mug':
            mug(q, col=C(rr.choice(['#4e7299', '#c44a3a', '#e9e4d8', '#c9a040'])), r=0.036, h=0.08, rot=f.rot + 90)
            x += 0.09
        elif k == 'jar':
            jar(q, r=0.04, h=rr.uniform(0.1, 0.16), content=(0.75, rr.choice([(0.85, 0.75, 0.4), (0.7, 0.2, 0.15), (0.5, 0.65, 0.25), (0.6, 0.4, 0.2)])), lidcol=(0.7, 0.5, 0.25))
            x += 0.095
        elif k == 'bowl':
            bowl(q, r=0.075, h=0.05, col=C(rr.choice(['#4e7299', '#e9e4d8', '#b5562f'])), mat='ceramic_vc')
            x += 0.17
        elif k == 'plate':
            qq = f.p((x, D / 2 - 0.05, 0.0125))
            plate(qq, r=0.09, col=C('#ece7da'), tilt=(-78, 0, f.rot + 180))
            x += 0.05
        else:
            x += 0.05
        if x > W / 2 - 0.05:
            break


def pot_rack(cx, cy, z, W=1.25, D=0.5):
    # ceiling hung iron frame
    p = Vector((cx, cy, z))
    for sx in (-1, 1):
        for sy in (-1, 1):
            q = p + V(sx * W / 2, sy * D / 2, 0)
            chain(q.x, q.y, q.z, 3.15, M['iron_black'])
    for sx in (-1, 1):
        box(M['iron_black'], p + V(sx * W / 2, 0, 0), (0.016, D, 0.016), bev=0.003)
    for sy in (-1, 1):
        box(M['iron_black'], p + V(0, sy * D / 2, 0), (W, 0.016, 0.016), bev=0.003)
    box(M['iron_black'], p, (0.012, D, 0.012), bev=0.002) if False else None
    # hooks with pots
    xs = [-0.5, -0.3, -0.1, 0.1, 0.3, 0.5]
    for i, x in enumerate(xs):
        yy = -D / 2 if i % 2 == 0 else D / 2
        hp = p + V(x, yy, -0.008)
        tube(M['iron_black'], [hp, hp + V(0, 0, -0.06), hp + V(0, (0.012 if yy > 0 else -0.012), -0.08)], 0.0035, seg=4)
        hp = hp + V(0, 0, -0.06)
        mode = i % 3
        if mode == 0:
            pot(hp + V(0, 0.0, -0.17 - 0.0), r=0.085, h=0.1, mat='copper', lid=False, handle=False)
            tube(M['copper'], arcpts((hp.x, hp.y, hp.z - 0.06), 0.085, 0, 180, 10, 'xz'), 0.003, 4)
        elif mode == 1:
            # pan hanging on handle: pan disc vertical
            pan(hp + V(0, 0, -0.32), r=0.11, rot=90, tilt=(-90, 0, 0), mat='copper' if i % 2 else 'iron_cast')
        else:
            # ladle / whisk
            tube(M['iron_black'], [hp, hp + V(0, 0, -0.25)], 0.005, seg=5)
            sphere(M['tin'], hp + V(0, 0, -0.28), 0.03, seg=8, rings=5, sq=(1, 1, 0.6))
    # herbs along the second bar
    for i in range(3):
        herb_bundle(p + V(-0.35 + i * 0.35, D / 2 * 0.0, -0.01), L=0.3, kind=['lav', 'herb', 'dry'][i], seed=i + 4)


def coat(pos, rot, col, h=0.95, w=0.42, seed=0, hooded=False):
    """coat hanging from pos (top of shoulders at z=pos.z)."""
    c = C(col)
    cf = fab(c, 0.1, 8, seed)
    Mr = xf(pos, (0, 0, rot))
    cloth_drape(M['fabric_vc'], Mr @ Matrix.Translation((0, 0.0, -0.05)) @ rotm((0, 0, 0)), w, h, nf=4, amp=0.028, col=c, thick=0.05, seed=seed, nx=16, ny=10, cfn=cf)
    f = Fr(pos, rot, None)
    f.pillow(M['fabric_vc'], (0, 0.0, -0.04), (w + 0.08, 0.1, 0.14), n=3, flat=0.2, pinch=0.0, cfn=cf, res=6)
    for s in (-1, 1):
        f.tube(M['fabric_vc'], [Vector((s * (w / 2 + 0.03), 0.0, -0.06)), Vector((s * (w / 2 + 0.065), -0.0, -0.3)), Vector((s * (w / 2 + 0.07), 0.01, -0.6))], [0.052, 0.046, 0.04], seg=8, cfn=cf)
    f.pillow(M['fabric_vc'], (0, 0.045, 0.0), (w * 0.55, 0.09, 0.07), n=2.8, flat=0.0, pinch=0.0, cfn=fab(shade(c, 0.85), 0.1), res=5)
    if hooded:
        f.pillow(M['fabric_vc'], (0, -0.06, 0.06), (0.22, 0.2, 0.2), n=2.6, flat=0.1, pinch=0.0, cfn=cf, res=6)
    for k in range(3):
        f.cyl(M['brass'], (0.0 + 0.02, 0.055, -0.22 - k * 0.15), 0.012, 0.008, axis='y', seg=8)


def umbrella_stand(pos):
    f = Fr(pos, 0, F)
    f.lathe(M['iron_black'], (0, 0, 0), [(0.001, 0), (0.09, 0), (0.1, 0.04), (0.11, 0.3), (0.12, 0.42), (0.11, 0.42), (0.095, 0.4), (0.09, 0.04), (0.001, 0.02)], seg=14, cap=False)
    f.lathe(M['iron_black'], (0, 0, 0.42), [(0.12, 0), (0.125, 0.0), (0.125, 0.012), (0.12, 0.012)], seg=14, cap=False)
    # umbrella
    f.tube(M['wood_dark'], [Vector((0.0, 0.0, 0.0)), Vector((0.0, 0.0, 0.85))], 0.009, seg=6)
    f.lathe(M['fabric_vc'], (0, 0, 0.85), [(0.001, 0.0), (0.03, 0.03), (0.02, 0.36 - 0.0), (0.001, 0.0) ][:2] + [(0.032, 0.03)], seg=10, cap=False, col=C('#2a3a52'))
    f.lathe(M['fabric_vc'], (0, 0, 0.42), [(0.02, 0.0), (0.03, 0.2), (0.032, 0.4), (0.022, 0.42), (0.001, 0.43)], seg=8, cap=False, col=C('#2a3a52'))
    # walking stick
    f.tube(M['wood_oak'], [Vector((0.05, 0.03, 0.0)), Vector((0.06, 0.03, 0.7)), Vector((0.062, 0.03, 0.9)), Vector((0.08, 0.03, 0.95)), Vector((0.1, 0.03, 0.92))], 0.011, seg=6)
    f.tube(M['wood_oak'], [Vector((-0.05, -0.04, 0.0)), Vector((-0.06, -0.04, 0.95))], 0.012, seg=6)
    collider(pos[0] - 0.13, pos[0] + 0.13, pos[1] - 0.13, pos[1] + 0.13, F + 0.45)


def wood_stack(pos, rot, W=0.6, H=0.42, D=0.3):
    """rack with firewood logs"""
    f = Fr(pos, rot, F)
    for s in (-1, 1):
        f.box(M['wood_dark'], (s * (W / 2 - 0.02), 0, H / 2), (0.04, D, H), bev=0.004, cuts=1)
    f.box(M['wood_dark'], (0, 0, 0.02), (W, D, 0.04), bev=0.003)
    rr = random.Random(4)
    for row in range(3):
        for i in range(6):
            x = -W / 2 + 0.07 + i * 0.085 + (0.04 if row % 2 else 0)
            if abs(x) > W / 2 - 0.05:
                continue
            log(f.p((x, 0, 0.09 + row * 0.1)), L=D - 0.02, r=rr.uniform(0.04, 0.05), rot=(0, 0, rot), axis='y')
    collider_f(f, W, D, F + H)
