"""Bedroom furniture"""
from int_lib import *
from int_mats import M
from int_items import *
from int_furn1 import *
from int_furn2 import *


def patch_col(p, cx=0, cy=0, sz=0.17, pal=None, seed=0):
    pal = pal or ['#9c3d34', '#d8c8a2', '#3f6b73', '#c99a3e', '#6d8a5a', '#e9e0cc', '#7a5a7e', '#b8603c']
    i = math.floor((p.x - cx) / sz); j = math.floor((p.y - cy) / sz)
    h = (i * 73856093 ^ j * 19349663 ^ seed * 83492791) & 0xffff
    c = C(pal[h % len(pal)])
    fx = ((p.x - cx) / sz) % 1.0; fy = ((p.y - cy) / sz) % 1.0
    # inner pattern
    k = 1.0
    if min(fx, fy, 1 - fx, 1 - fy) < 0.045:
        k = 0.55
    elif ((h >> 4) % 3 == 0) and abs(fx - 0.5) + abs(fy - 0.5) < 0.28:
        c = C(pal[(h >> 3) % len(pal)]) ; k = 1.0
    elif ((h >> 6) % 4 == 0) and abs(fx - fy) < 0.07:
        k = 0.7
    k *= 1 + 0.06 * nz(p.x * 40, p.y * 40)
    return (c[0] * k, c[1] * k, c[2] * k)


def bed(pos, rot=180):
    f = Fr(pos, rot, F)
    W, L = 1.62, 2.02
    m = 'wood_pine'
    col = (1, 0.95, 0.88)
    # posts
    for sx in (-1, 1):
        for sy, ph in ((-1, 1.12), (1, 0.72)):
            x, y = sx * (W / 2 - 0.03), sy * (L / 2 - 0.03)
            f.box(M[m], (x, y, ph / 2), (0.07, 0.07, ph), bev=0.006, col=col, cuts=2)
            f.lathe(M[m], (x, y, ph), [(0.032, 0), (0.038, 0.02), (0.022, 0.04), (0.03, 0.06), (0.001, 0.09)], seg=8, cap=False, col=col)
    # rails
    for sx in (-1, 1):
        f.box(M[m], (sx * (W / 2 - 0.03), 0, 0.3), (0.045, L - 0.1, 0.17), bev=0.005, col=col, g=1, cuts=3)
    # headboard
    f.box(M[m], (0, -L / 2 + 0.03, 0.94), (W - 0.08, 0.04, 0.3), bev=0.005, col=col, g=0, cuts=4)
    f.box(M[m], (0, -L / 2 + 0.03, 0.66), (W - 0.08, 0.04, 0.22), bev=0.005, col=col, g=0, cuts=3)
    for i in range(9):
        f.box(M[m], (-W / 2 + 0.1 + i * (W - 0.2) / 8, -L / 2 + 0.03, 0.8), (0.03, 0.03, 0.16), bev=0.004, col=col)
    f.box(M[m], (0, -L / 2 + 0.03, 1.1), (W - 0.02, 0.055, 0.045), bev=0.008, col=col, g=0)
    # footboard
    f.box(M[m], (0, L / 2 - 0.03, 0.5), (W - 0.08, 0.04, 0.26), bev=0.005, col=col, g=0, cuts=3)
    f.box(M[m], (0, L / 2 - 0.03, 0.66), (W - 0.02, 0.05, 0.05), bev=0.008, col=col, g=0)
    # slats
    f.box(M['wood_dark'], (0, 0, 0.35), (W - 0.12, L - 0.14, 0.02), bev=0.002)
    # mattress
    f.pillow(M['fabric_vc'], (0, 0.0, 0.46), (W - 0.1, L - 0.12, 0.26), n=6, flat=0.0, pinch=0.0, col=(0.93, 0.9, 0.84), res=10, noise_amp=0.004)
    # sheet edge visible + quilt
    qx0, qx1 = -0.82, 0.82
    qy0, qy1 = -0.52, L / 2 + 0.03
    top0 = 0.60
    def qz(x, y):
        z = top0 + 0.02 + 0.012 * math.sin(x * 14 + y * 5) + 0.014 * math.sin(y * 9 - x * 3) + 0.02 * fbm(x * 2, y * 2, 0, 2.2, 3, 2)
        # quilted stitching dimples
        z -= 0.004 * (abs(math.sin(x / 0.17 * math.pi)) < 0.06) + 0.004 * (abs(math.sin(y / 0.17 * math.pi)) < 0.06)
        ex = max(0, abs(x) - (W / 2 - 0.12))
        ey = max(0, y - (L / 2 - 0.26))
        z -= ex * 3.2 + ey * 3.2
        # folded-back top edge near head
        if y < qy0 + 0.25:
            z += 0.035 * math.sin((y - qy0) / 0.25 * math.pi) * (1 if y > qy0 else 0)
        return max(z, 0.33)
    f.cloth(M['fabric_vc'], qx0 - 0.04, qx1 + 0.04, qy0, qy1, 30, 40, qz, lambda x, y: 0.3, cfn=lambda p: patch_col(f.M.inverted() @ p, -0.82, -0.52, 0.18, seed=2), M=Matrix.Identity(4), solid=False)
    # sheet turned over at head
    f.cloth(M['fabric_vc'], -0.7, 0.7, -0.78, -0.5, 14, 4, lambda x, y: 0.627 + 0.03 * math.sin((y + 0.78) / 0.28 * math.pi) + 0.008 * math.sin(x * 20), lambda x, y: 0.6, col=(0.93, 0.9, 0.82), cfn=lambda p: (0.92 + 0.04 * nz(p.x * 20, p.y * 20), 0.89 + 0.04 * nz(p.x * 20, p.y * 20), 0.82), M=Matrix.Identity(4))
    # pillows
    for sx in (-1, 1):
        f.pillow(M['fabric_vc'], (sx * 0.4, -L / 2 + 0.28, 0.74), (0.62, 0.4, 0.17), r=(-8, 0, sx * 2), n=2.6, flat=0.9, pinch=0.35, col=(0.95, 0.92, 0.86), res=9, noise_amp=0.01)
    f.pillow(M['fabric_vc'], (0.3, -L / 2 + 0.2, 0.86), (0.4, 0.22, 0.4), r=(-25, 0, 10), n=2.6, flat=0.9, pinch=0.4, cfn=fab(C('#b5562f'), 0.12, 12, 3), res=9, noise_amp=0.01)
    # folded wool blanket at foot
    f.cloth(M['knit_vc'], -0.6, 0.6, L / 2 - 0.42, L / 2 - 0.12, 12, 4, lambda x, y: 0.66 + 0.02 * math.sin(x * 12) + 0.01 * nz(x * 8, y * 8), lambda x, y: 0.6,
            cfn=lambda p: (0.5, 0.1, 0.08) if int((f.M.inverted() @ p).x / 0.08 + 50) % 4 == 0 else (0.75, 0.68, 0.5), M=Matrix.Identity(4))
    collider_f(f, W + 0.02, L + 0.02, F + 0.66)
    return f


def bedside(pos, rot=180):
    f = Fr(pos, rot, F)
    W, D, H = 0.42, 0.36, 0.62
    m = 'wood_oak'
    col = (1, 0.95, 0.9)
    f.box(M[m], (0, 0, H - 0.015), (W + 0.03, D + 0.03, 0.03), bev=0.005, col=col, cuts=2, g=0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.lathe(M[m], (sx * (W / 2 - 0.03), sy * (D / 2 - 0.03), 0), [(0.012, 0), (0.02, 0.2), (0.017, 0.33), (0.026, 0.4)], seg=8, col=col)
    f.box(M[m], (0, 0, H - 0.115), (W - 0.02, D - 0.02, 0.15), bev=0.004, col=col, g=0)
    f.box(M[m], (0, D / 2 - 0.004, H - 0.115), (W - 0.06, 0.012, 0.12), bev=0.003, col=(0.92, 0.88, 0.82), g=0)
    f.lathe(M['brass'], (0, D / 2 + 0.002, H - 0.115), [(0.001, 0), (0.014, 0), (0.008, 0.012), (0.014, 0.026), (0.001, 0.028)], r=(-90, 0, 0), seg=8, cap=False)
    f.box(M[m], (0, 0, 0.2), (W - 0.04, D - 0.04, 0.02), bev=0.003, col=col, g=0)
    collider_f(f, W + 0.03, D + 0.03, F + H)
    return f


def wardrobe(pos, rot=-90, W=1.15, D=0.56, H=2.05):
    f = Fr(pos, rot, F)
    m = 'wood_walnut'
    col = (1, 0.93, 0.88)
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.lathe(M[m], (sx * (W / 2 - 0.06), sy * (D / 2 - 0.06), 0), [(0.03, 0), (0.05, 0.03), (0.04, 0.07), (0.05, 0.1)], seg=10, col=col)
    f.box(M[m], (0, 0, 0.14), (W, D, 0.08), bev=0.008, col=col, g=0)
    f.box(M[m], (0, 0, 0.14 + (H - 0.3) / 2 + 0.04), (W - 0.04, D - 0.04, H - 0.3), bev=0.006, col=col, cuts=3)
    # crown
    f.box(M[m], (0, 0, H - 0.1), (W + 0.04, D + 0.03, 0.06), bev=0.008, col=col, g=0)
    f.box(M[m], (0, 0, H - 0.05), (W + 0.08, D + 0.06, 0.05), bev=0.01, col=col, g=0)
    f.box(M[m], (0, 0, H - 0.01), (W + 0.02, D + 0.0, 0.04), bev=0.008, col=col, g=0)
    yf = D / 2 - 0.02
    dh = H - 0.46
    zc = 0.22 + dh / 2 + 0.06
    for s in (-1, 1):
        cx = s * (W / 4 - 0.005)
        dw = W / 2 - 0.05
        f.box(M[m], (cx, yf + 0.01, zc), (dw, 0.022, dh), bev=0.005, col=col, cuts=2, g=2)
        # raised panels with carved border
        for (pz, ph) in ((zc + dh * 0.22, dh * 0.5), (zc - dh * 0.3, dh * 0.3)):
            f.box(M[m], (cx, yf + 0.022, pz), (dw - 0.1, 0.012, ph - 0.05), bev=0.004, col=(0.85, 0.78, 0.72), g=2)
            f.box(M[m], (cx, yf + 0.03, pz), (dw - 0.16, 0.008, ph - 0.11), bev=0.004, col=(1.05, 0.98, 0.92), g=2)
        # carved rosette + vines
        rz = zc + dh * 0.22
        f.lathe(M[m], (cx, yf + 0.034, rz), [(0.001, 0), (0.05, 0.0), (0.05, 0.004), (0.03, 0.008), (0.012, 0.014), (0.001, 0.016)], r=(-90, 0, 0), seg=16, cap=False, col=(1.1, 1.02, 0.95))
        for k in range(8):
            a = k * TAU / 8
            f.cyl(M[m], (cx + math.cos(a) * 0.07, yf + 0.036, rz + math.sin(a) * 0.07), 0.009, 0.006, axis='y', seg=6, col=(1.12, 1.05, 0.98))
        f.tube(M[m], [Vector((cx + (-0.1 + 0.2 * i / 8) * 1.0, yf + 0.036, zc + dh * 0.42 - 0.025 + 0.012 * math.sin(i * 2))) for i in range(9)], 0.005, seg=5, col=(1.1, 1.03, 0.96))
        # handle
        hx = cx - s * (dw / 2 - 0.05)
        f.cyl(M['brass'], (-s * 0.02 + s * 0.0 + (s * -0.04), yf + 0.03, zc), 0.0, 0.0) if False else None
        f.lathe(M['brass'], (s * 0.04 - s * 0.0, yf + 0.02, zc), [(0.001, 0), (0.016, 0), (0.008, 0.012), (0.018, 0.026), (0.001, 0.03)], r=(-90, 0, 0), seg=10, cap=False)
    # drawer below
    f.box(M[m], (0, yf + 0.01, 0.34), (W - 0.06, 0.022, 0.16), bev=0.005, col=col, g=0)
    f.box(M[m], (0, yf + 0.022, 0.34), (W - 0.14, 0.008, 0.09), bev=0.003, col=(0.85, 0.78, 0.72), g=0)
    for s in (-1, 1):
        f.tube(M['brass'], [Vector((s * 0.2 - 0.05, yf + 0.03, 0.34)), Vector((s * 0.2 - 0.05, yf + 0.05, 0.34)), Vector((s * 0.2 + 0.05, yf + 0.05, 0.34)), Vector((s * 0.2 + 0.05, yf + 0.03, 0.34))], 0.005, seg=6)
    f.box(M['brass'], (0.0, yf + 0.024, zc), (0.008, 0.003, 0.05), bev=0)
    collider_f(f, W + 0.06, D + 0.06, F + H + 0.04)
    return f


def mirror_oval(pos, rot, a=0.28, b=0.42, fw=0.04):
    f = Fr(pos, rot, None)
    pts = [Vector((a * math.cos(t), 0.0, b * math.sin(t))) for t in [i * TAU / 40 for i in range(41)]]
    f.tube(M['wood_walnut'], pts, [fw / 2] * 41, seg=8, caps=False)
    f.lathe(M['mirror'], (0, 0.004, 0), [(0.001, 0), (1.0, 0.0)], r=(-90, 0, 0), seg=40, cap=False, scale=(a, b, 1), col=(0.85, 0.9, 0.92)) if False else None
    # mirror as flat disc facing +y local... build lathe axis z -> rotate 90 about x so axis goes to -y..; use r=(90,0,0) for normal -y? keep both sides
    f.lathe(M['mirror'], (0, 0.004, 0), [(1.0, 0.0), (0.0, 0)], r=(-90, 0, 0), seg=40, cap=False, scale=(a, b, 1))
    # hanger
    f.tube(M['iron_black'], [Vector((-0.1, -0.004, b * 0.9)), Vector((0, -0.01, b + 0.14)), Vector((0.1, -0.004, b * 0.9))], 0.002, seg=4)
    f.cyl(M['brass'], (0, -0.012, b + 0.14), 0.006, 0.012, axis='y', seg=6)


def dresser(pos, rot=-90, W=1.0, D=0.48, H=0.9):
    f = Fr(pos, rot, F)
    m = 'wood_white'
    col = (1, 0.97, 0.93)
    cabinet_carcass(f, W, D, H - 0.04, m, plinth=0.1)
    f.box(M['wood_oak'], (0, 0.01, H - 0.02), (W + 0.04, D + 0.03, 0.04), bev=0.007, col=(1, 0.95, 0.9), cuts=3, g=0)
    yf = D / 2 - 0.004
    hs = [0.6, 0.41, 0.22]
    for z in [0.72, 0.51, 0.3]:
        pass
    dzs = [(0.73, 0.16), (0.56, 0.16), (0.39, 0.16), (0.22, 0.14)]
    for z, h in dzs:
        drawer(f, 0, z, W - 0.06, h, m, yf)
    collider_f(f, W + 0.04, D + 0.03, F + H)
    return f


def desk(pos, rot=90, W=1.15, D=0.6, H=0.76):
    f = Fr(pos, rot, F)
    m = 'wood_oak'
    col = (1, 0.95, 0.9)
    f.box(M[m], (0, 0, H - 0.02), (W, D, 0.04), bev=0.006, col=col, cuts=5, g=0)
    f.box(M['leather_vc'], (-0.12, 0.0, H + 0.0015), (0.56, 0.36, 0.003), bev=0, col=C('#3f5a3f'))
    # pedestal with drawers on the left
    px = -W / 2 + 0.22
    f.box(M[m], (px, 0, (H - 0.04) / 2), (0.4, D - 0.06, H - 0.04), bev=0.004, col=col, g=2, cuts=2)
    for i, z in enumerate([0.64, 0.46, 0.28]):
        drawer(f, px, z, 0.36, 0.15, m, D / 2 - 0.035)
    for sy in (-1, 1):
        turned_leg(f, W / 2 - 0.05, sy * (D / 2 - 0.05), H - 0.04, r=0.028, top_block=0.08, style=1)
    f.box(M[m], (W / 2 - 0.05, 0, H - 0.08), (0.02, D - 0.1, 0.08), bev=0.003)
    f.box(M[m], (0.12, -D / 2 + 0.04, H - 0.08), (W - 0.5, 0.02, 0.08), bev=0.003)
    collider_f(f, W + 0.02, D + 0.02, F + H)
    return f


def trunk(pos, rot=0, W=1.0, D=0.48, H=0.46):
    f = Fr(pos, rot, F)
    col = (1, 0.93, 0.85)
    f.box(M['wood_dark'], (0, 0, 0.17), (W, D, 0.3), bev=0.008, col=col, cuts=3)
    n = 9
    R = D / 2
    for i in range(n):
        a0 = math.pi * i / n; a1 = math.pi * (i + 1) / n
        am = (a0 + a1) / 2
        seg = 2 * R * math.sin(math.pi / n / 2) * 1.05
        f.box(M['wood_dark'], (0, math.cos(am) * R * 0.98, 0.32 + math.sin(am) * (H - 0.32) * 1.0), (W - 0.02, seg, 0.02), r=(math.degrees(am) - 90 + 0, 0, 0) if False else (-(90 - math.degrees(am)) if False else math.degrees(am) - 90, 0, 0), bev=0.002, col=col)
    for x in (-W / 2 + 0.07, W / 2 - 0.07, 0.0):
        f.box(M['iron_black'], (x, 0, 0.17), (0.04, D + 0.008, 0.302), bev=0.002)
        for i in range(n):
            a0 = math.pi * i / n; a1 = math.pi * (i + 1) / n
            am = (a0 + a1) / 2
            seg = 2 * R * math.sin(math.pi / n / 2) * 1.05
            f.box(M['iron_black'], (x, math.cos(am) * R * 0.98, 0.32 + math.sin(am) * (H - 0.32) + 0.002), (0.04, seg, 0.024), r=(math.degrees(am) - 90, 0, 0), bev=0.001)
    f.box(M['brass'], (0, -D / 2 - 0.002 + D, 0.27), (0.05, 0.012, 0.06), bev=0.003)
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.box(M['iron_black'], (sx * (W / 2 - 0.01), sy * (D / 2 - 0.01), 0.04), (0.05, 0.05, 0.05), bev=0.004)
    collider_f(f, W + 0.02, D + 0.02, F + H)
    return f


def small_wall_cabinet(pos, rot, W=0.5, H=0.4, D=0.2):
    f = Fr(pos, rot, None)
    f.box(M['wood_blue'], (0, 0, 0), (W, D, H), bev=0.004, col=(1, 0.97, 0.94), cuts=2)
    f.box(M['wood_blue'], (0, D / 2 + 0.005, 0), (W - 0.06, 0.01, H - 0.06), bev=0.003, col=(0.92, 0.9, 0.86))
    f.box(M['wood_blue'], (0, 0, H / 2 + 0.012), (W + 0.04, D + 0.03, 0.024), bev=0.004)
    f.lathe(M['brass'], (W / 2 - 0.06, D / 2 + 0.01, 0), [(0.001, 0), (0.012, 0), (0.007, 0.01), (0.012, 0.02), (0.001, 0.022)], r=(-90, 0, 0), seg=8, cap=False)
