"""Living / dining / kitchen furniture"""
from int_lib import *
from int_mats import M
from int_items import *


def face(src, dst):
    dx, dy = dst[0] - src[0], dst[1] - src[1]
    return math.degrees(math.atan2(-dx, dy))


def fab(base, amp=0.07, s=9.0, seed=0):
    def f(p):
        k = 1 + amp * fbm(p.x, p.y, p.z, s, seed, 2)
        return (base[0] * k, base[1] * k, base[2] * k)
    return f


def turned_leg(f, x, y, h, r=0.03, mat='wood_oak', top_block=0.1, z0=0.0, col=(1, 1, 1), style=0):
    """turned leg in frame f: x,y local, from z0 to z0+h"""
    hb = top_block
    f.box(M[mat], (x, y, z0 + h - hb / 2), (r * 1.9, r * 1.9, hb), bev=0.003, col=col)
    hh = h - hb
    if style == 0:
        pr = [(r * 0.55, 0), (r * 0.78, 0.02), (r * 0.85, 0.05), (r * 0.6, 0.09), (r * 0.72, 0.16), (r * 0.6, hh * 0.45), (r * 0.78, hh * 0.52), (r * 0.6, hh * 0.6),
              (r * 0.85, hh * 0.72), (r * 0.72, hh * 0.85), (r * 0.9, hh)]
    else:
        pr = [(r * 0.5, 0), (r * 0.7, hh * 0.3), (r * 0.9, hh)]
    f.lathe(M[mat], (x, y, z0), [(a, b) for a, b in pr], seg=10, col=col, cap=True)


# ====================================================================== dining
def dining_table(pos, rot=0):
    f = Fr(pos, rot, F)
    W, D, H = 1.35, 0.88, 0.76
    wc = woodcol((1, 1, 1), 0.10, 7, 2, 0)
    f.box(M['wood_oak'], (0, 0, H - 0.02), (W, D, 0.04), bev=0.008, cuts=6, cfn=None, col=(1, 0.97, 0.94), g=0)
    # plank seams
    for i in (-1, 1):
        f.box(M['wood_dark'], (0, i * D / 6, H - 0.0005), (W - 0.01, 0.003, 0.002), bev=0, col=(0.7, 0.6, 0.5))
    # aprons
    for sy in (-1, 1):
        f.box(M['wood_oak'], (0, sy * (D / 2 - 0.07), H - 0.095), (W - 0.14, 0.022, 0.1), bev=0.004, col=(0.95, 0.9, 0.85), g=0)
    for sx in (-1, 1):
        f.box(M['wood_oak'], (sx * (W / 2 - 0.07), 0, H - 0.095), (0.022, D - 0.14, 0.1), bev=0.004, col=(0.95, 0.9, 0.85), g=1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            turned_leg(f, sx * (W / 2 - 0.07), sy * (D / 2 - 0.07), H - 0.04, r=0.036, top_block=0.12)
    # stretcher
    f.box(M['wood_oak'], (0, 0, 0.14), (W - 0.16, 0.03, 0.03), bev=0.005, g=0)
    collider_f(f, W, D, F + H)
    return f


def collider_f(f, W, D, top, off=(0, 0)):
    # axis aligned bound of rotated rect
    a = math.radians(f.rot)
    cx, cy = f.p((off[0], off[1], 0))[:2]
    hx = abs(W / 2 * math.cos(a)) + abs(D / 2 * math.sin(a))
    hy = abs(W / 2 * math.sin(a)) + abs(D / 2 * math.cos(a))
    collider(cx - hx, cx + hx, cy - hy, cy + hy, top)


def dining_chair(pos, rot=0, cushion=None, mat='wood_oak'):
    f = Fr(pos, rot, F)
    sh = 0.46
    wd = 0.42
    col = (1, 0.96, 0.92)
    # legs: back ones tall posts
    for sx in (-1, 1):
        turned_leg(f, sx * 0.19, 0.18, sh - 0.03, r=0.022, mat=mat, top_block=0.06, style=1, col=col)
        # back post
        f.box(M[mat], (sx * 0.19, -0.18, 0.46), (0.038, 0.034, 0.92), bev=0.004, col=col, g=2, r=(-4, 0, 0))
    # seat
    f.box(M[mat], (0, 0, sh - 0.012), (wd + 0.03, 0.42, 0.03), bev=0.006, col=col, cuts=2, g=0)
    # stretchers
    for z in (0.16,):
        f.box(M[mat], (0, 0.18, z), (wd - 0.02, 0.02, 0.02), bev=0.003, col=col)
        f.box(M[mat], (0, -0.18, z), (wd - 0.02, 0.02, 0.02), bev=0.003, col=col)
        for sx in (-1, 1):
            f.box(M[mat], (sx * 0.19, 0, z), (0.02, 0.34, 0.02), bev=0.003, col=col)
    # back slats and rail
    f.box(M[mat], (0, -0.21, 0.86), (wd - 0.02, 0.028, 0.09), bev=0.006, col=col, r=(-4, 0, 0))
    for i in range(3):
        x = (i - 1) * 0.095
        f.box(M[mat], (x, -0.2, 0.68), (0.045, 0.014, 0.3), bev=0.003, col=col, r=(-4, 0, 0))
    f.box(M[mat], (0, -0.2, 0.52), (wd - 0.02, 0.022, 0.05), bev=0.004, col=col, r=(-4, 0, 0))
    if cushion:
        f.pillow(M['fabric_vc'], (0, 0.0, sh + 0.012), (0.4, 0.4, 0.05), col=cushion, cfn=fab(C(cushion), 0.06) if False else None, flat=0.3, pinch=0.1)
    collider_f(f, 0.44, 0.44, F + 0.47)
    return f


def side_chair_rot(pos_chair, target):
    return face(pos_chair, target)


# ====================================================================== seating
def sofa(pos, rot, L=1.9, col='#b7a98f', cush2='#b5562f', cush3='#d0a23e', throw=True):
    f = Fr(pos, rot, F)
    c = C(col)
    cf = fab(c, 0.07, 7, 1)
    D = 0.88
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.lathe(M['wood_dark'], (sx * (L / 2 - 0.08), sy * (D / 2 - 0.08), 0), [(0.02, 0), (0.028, 0.03), (0.022, 0.08), (0.03, 0.12)], seg=8)
    f.pillow(M['fabric_vc'], (0, 0, 0.24), (L, D, 0.24), n=5, flat=0.0, pinch=0, cfn=lambda p: cf(p), res=8)
    # back
    f.pillow(M['fabric_vc'], (0, -0.33, 0.55), (L, 0.22, 0.6), n=4, flat=0.1, pinch=0.0, cfn=cf, res=8)
    # arms
    for s in (-1, 1):
        f.pillow(M['fabric_vc'], (s * (L / 2 - 0.09), 0.0, 0.42), (0.19, D, 0.40), n=3.2, flat=0.0, pinch=0, cfn=cf, res=8)
        f.lathe(M['fabric_vc'], (s * (L / 2 - 0.09), 0.0, 0.59), [(0.001, -D / 2 + 0.03), (0.1, -D / 2 + 0.03)], seg=4, cap=False, col=c) if False else None
    w = (L - 0.38) / 3
    for i in range(3):
        x = (i - 1) * w
        f.pillow(M['fabric_vc'], (x, 0.1, 0.42), (w - 0.012, 0.62, 0.17), n=3.5, flat=0.4, pinch=0.3, cfn=cf, res=7, noise_amp=0.008)
        f.pillow(M['fabric_vc'], (x, -0.17, 0.66), (w - 0.012, 0.19, 0.46), r=(-14, 0, 0), n=3.2, flat=0.6, pinch=0.25, cfn=cf, res=7, noise_amp=0.008)
    # scatter pillows
    def sp(x, rz, colr, tilt):
        cc = C(colr)
        f.pillow(M['fabric_vc'], (x, -0.05, 0.6), (0.4, 0.14, 0.4), r=(-22, rz * 0.3, rz), n=2.6, flat=0.85, pinch=0.45, cfn=fab(cc, 0.12, 14, 3), res=8, noise_amp=0.012)
    sp(-L / 2 + 0.3, 12, cush2, 0)
    sp(-L / 2 + 0.62, -8, cush3, 0)
    sp(L / 2 - 0.3, -15, '#5f7d73', 0)
    if throw:
        tc = lambda p: tartan(p)
        f.cloth(M['knit_vc'], -0.26, 0.26, -0.3, 0.46, 12, 16,
                lambda x, y: 0.52 + 0.012 * math.sin(y * 18 + x * 6) + (0.18 if y < -0.1 else 0) * 0 - max(0, y - 0.3) * 0.8 + 0.12 * max(0, -0.1 - y) * 0 + max(0, (-0.12 - y)) * 0.85 + 0.014 * nz(x * 8, y * 8),
                lambda x, y: 0.5 + max(0, y - 0.3) * -0.8 - 0.02, cfn=tc, M=Matrix.Translation((L / 2 - 0.62, 0.12, 0.0)) @ rotm((0, 0, 8)))
    collider_f(f, L + 0.02, D + 0.02, F + 0.47)
    return f


def tartan(p):
    a = 0.5 + 0.5 * math.sin(p.x * 52); b = 0.5 + 0.5 * math.sin(p.y * 52 + p.x * 3)
    base = (0.55, 0.06, 0.05)
    if a > 0.82:
        base = (0.03, 0.12, 0.06)
    if b > 0.85:
        base = (0.85, 0.75, 0.45)
    k = 0.85 + 0.15 * (a * 0.5 + b * 0.5)
    return (base[0] * k, base[1] * k, base[2] * k)


def armchair(pos, rot, col='#c08a3e', w=0.84, cushion='#7d8e9c'):
    f = Fr(pos, rot, F)
    c = C(col)
    cf = fab(c, 0.07, 8, 2)
    D = 0.86
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.lathe(M['wood_walnut'], (sx * (w / 2 - 0.08), sy * (D / 2 - 0.08), 0), [(0.018, 0), (0.028, 0.04), (0.02, 0.1), (0.028, 0.14)], seg=8)
    f.pillow(M['fabric_vc'], (0, 0, 0.27), (w, D, 0.26), n=5, flat=0, pinch=0, cfn=cf, res=8)
    f.pillow(M['fabric_vc'], (0, -0.33, 0.62), (w, 0.2, 0.7), r=(-8, 0, 0), n=3.6, flat=0.1, pinch=0, cfn=cf, res=8)
    for s in (-1, 1):
        f.pillow(M['fabric_vc'], (s * (w / 2 - 0.085), 0.02, 0.47), (0.17, D - 0.06, 0.4), n=3.2, flat=0.0, pinch=0, cfn=cf, res=8)
    f.pillow(M['fabric_vc'], (0, 0.08, 0.45), (w - 0.3, 0.6, 0.17), n=3.5, flat=0.4, pinch=0.3, cfn=cf, res=8, noise_amp=0.008)
    f.pillow(M['fabric_vc'], (0, -0.2, 0.68), (w - 0.3, 0.2, 0.44), r=(-16, 0, 0), n=3.2, flat=0.6, pinch=0.25, cfn=cf, res=8, noise_amp=0.008)
    cc = C(cushion)
    f.pillow(M['fabric_vc'], (0.14, -0.04, 0.66), (0.38, 0.13, 0.38), r=(-24, 0, -14), n=2.6, flat=0.85, pinch=0.45, cfn=fab(cc, 0.1, 14, 3), res=8, noise_amp=0.01)
    collider_f(f, w + 0.02, D + 0.02, F + 0.5)
    return f


def rocking_chair(pos, rot):
    f = Fr(pos, rot, F)
    mat = 'wood_walnut'
    col = (1, 0.95, 0.9)
    # rockers
    for sx in (-1, 1):
        pts = [Vector((sx * 0.25, y, 0.03 + 0.06 * (y / 0.5) ** 2 * 0.8 * 0 + 0.07 * (1 - math.cos(y * 2.2)))) for y in [(-0.46 + 0.92 * i / 14) for i in range(15)]]
        f.tube(M[mat], pts, 0.0, caps=True) if False else None
        pts2 = [Vector((sx * 0.25, y, 0.035 + 0.11 * (y / 0.46) ** 2)) for y in [(-0.46 + 0.92 * i / 14) for i in range(15)]]
        f.tube(M[mat], pts2, 0.016, seg=6, col=col)
        # legs to seat
        for yy, top in ((0.2, 0.44), (-0.2, 0.44)):
            z0 = 0.035 + 0.11 * (yy / 0.46) ** 2
            f.box(M[mat], (sx * 0.23, yy, (z0 + top) / 2), (0.032, 0.032, top - z0), bev=0.004, col=col)
        f.box(M[mat], (sx * 0.23, 0.0, 0.26), (0.02, 0.4, 0.02), bev=0.003, col=col)
        # arm
        f.box(M[mat], (sx * 0.23, 0.05, 0.66), (0.04, 0.42, 0.028), bev=0.006, col=col)
        f.box(M[mat], (sx * 0.23, 0.22, 0.56), (0.028, 0.03, 0.22), bev=0.004, col=col)
        # back post
        f.box(M[mat], (sx * 0.2, -0.22, 0.75), (0.032, 0.032, 0.78), bev=0.004, col=col, r=(-10, 0, 0))
    f.box(M[mat], (0, 0.0, 0.43), (0.5, 0.46, 0.028), bev=0.006, col=col)
    for i in range(5):
        f.box(M[mat], (0, -0.23 - i * 0.012 + 0.0, 0.62 + i * 0.1), (0.4, 0.016, 0.06), bev=0.004, col=col, r=(-10, 0, 0))
    f.box(M[mat], (0, -0.3, 1.05), (0.44, 0.02, 0.1), bev=0.006, col=col, r=(-10, 0, 0))
    f.pillow(M['fabric_vc'], (0, 0.0, 0.46), (0.46, 0.44, 0.06), col=C('#9a4d3a'), cfn=fab(C('#9a4d3a'), 0.1, 10, 4), flat=0.3, pinch=0.2)
    f.pillow(M['fabric_vc'], (0, -0.2, 0.75), (0.36, 0.06, 0.42), r=(-10, 0, 0), col=C('#9a4d3a'), cfn=fab(C('#9a4d3a'), 0.1, 10, 4), flat=0.3, pinch=0.2)
    collider_f(f, 0.62, 0.95, F + 0.6)
    return f


def stool(pos, h=0.45, r=0.17, mat='wood_oak'):
    f = Fr(pos, 0, F)
    f.cyl(M[mat], (0, 0, h - 0.02), r, 0.04, seg=16, bev=0.008, col=(1, 0.95, 0.9))
    for i in range(3):
        a = i * TAU / 3 + 0.3
        f.tube(M[mat], [Vector((math.cos(a) * r * 0.5, math.sin(a) * r * 0.5, h - 0.03)), Vector((math.cos(a) * r * 0.85, math.sin(a) * r * 0.85, 0.0))], 0.02, seg=7)
    return f


def coffee_table(pos, rot=0):
    f = Fr(pos, rot, F)
    W, D, H = 0.95, 0.52, 0.42
    f.box(M['wood_walnut'], (0, 0, H - 0.02), (W, D, 0.04), bev=0.008, cuts=5, g=0)
    f.box(M['wood_walnut'], (0, 0, 0.13), (W - 0.12, D - 0.1, 0.022), bev=0.004, cuts=3, g=0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            turned_leg(f, sx * (W / 2 - 0.05), sy * (D / 2 - 0.05), H - 0.04, r=0.025, mat='wood_walnut', top_block=0.07, style=1)
    for sy in (-1, 1):
        f.box(M['wood_walnut'], (0, sy * (D / 2 - 0.05), H - 0.065), (W - 0.1, 0.02, 0.05), bev=0.003, g=0)
    for sx in (-1, 1):
        f.box(M['wood_walnut'], (sx * (W / 2 - 0.05), 0, H - 0.065), (0.02, D - 0.1, 0.05), bev=0.003, g=1)
    collider_f(f, W, D, F + H)
    return f


def side_table(pos, r=0.22, h=0.58):
    f = Fr(pos, 0, F)
    f.cyl(M['wood_oak'], (0, 0, h - 0.02), r, 0.035, seg=20, bev=0.008, col=(1, 0.95, 0.9))
    for i in range(3):
        a = i * TAU / 3 + 0.5
        pts = [Vector((math.cos(a) * r * 0.55, math.sin(a) * r * 0.55, h - 0.04)), Vector((math.cos(a) * r * 0.85, math.sin(a) * r * 0.85, 0.0))]
        f.tube(M['wood_oak'], pts, [0.018, 0.013], seg=7)
    f.cyl(M['wood_oak'], (0, 0, 0.2), r * 0.72, 0.018, seg=18)
    collider_f(f, 2 * r, 2 * r, F + h)
    return f


# ====================================================================== rugs, sheepskin
def braided_rug(cx, cy, a, b, rot=0, rings=None, z=0.0):
    """oval braided rug with concentric colour rings + tassel-free. flat slab with slight bumps."""
    cols = rings or ['#8c3a2e', '#d9c7a0', '#3f5f55', '#c7a04a', '#8c3a2e', '#d9c7a0', '#5a4632', '#b8a27a', '#3f5f55', '#d9c7a0']
    cl = [C(c) for c in cols]
    n = 56
    def cf(p):
        q = Matrix.Rotation(-math.radians(rot), 3, 'Z') @ Vector((p.x - cx, p.y - cy, 0))
        rr = math.sqrt((q.x / a) ** 2 + (q.y / b) ** 2)
        if rr > 1.0:
            rr = 1.0
        k = int(rr * len(cl) * 0.98)
        c = cl[min(k, len(cl) - 1)]
        # braid texture
        ang = math.atan2(q.y / b, q.x / a)
        br = 1 + 0.12 * math.sin(ang * 60 + rr * 40) * 0.8 + 0.06 * nz(p.x * 25, p.y * 25)
        edge = (rr * len(cl) * 0.98) % 1.0
        br *= 0.85 + 0.25 * math.sin(edge * math.pi)
        return (c[0] * br, c[1] * br, c[2] * br)
    bm = bmesh.new()
    # polar grid
    R = 9; S = 48
    ctr = bm.verts.new((0, 0, 0.012))
    rows = []
    for i in range(1, R + 1):
        t = i / R
        row = []
        for j in range(S):
            th = j / S * TAU
            zz = 0.012 * (1 - 0.35 * t) + 0.004 * math.sin(th * 60 + t * 80) * (1 if t < 0.97 else 0) + (-0.006 if t > 0.97 else 0) * 0
            if i == R:
                zz = 0.004
            row.append(bm.verts.new((a * t * math.cos(th), b * t * math.sin(th), zz)))
        rows.append(row)
    for j in range(S):
        k = (j + 1) % S
        try:
            bm.faces.new([ctr, rows[0][k], rows[0][j]][::-1] if False else [ctr, rows[0][j], rows[0][k]])
        except ValueError:
            pass
    for i in range(R - 1):
        for j in range(S):
            k = (j + 1) % S
            try:
                bm.faces.new([rows[i][j], rows[i + 1][j], rows[i + 1][k], rows[i][k]])
            except ValueError:
                pass
    # side skirt + bottom
    skirt = [bm.verts.new((v.co.x, v.co.y, 0.0)) for v in rows[-1]]
    for j in range(S):
        k = (j + 1) % S
        try:
            bm.faces.new([rows[-1][j], rows[-1][k], skirt[k], skirt[j]])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    put(M['knit_vc'], bm, xf((cx, cy, F + z + 0.001), (0, 0, rot)), (1, 1, 1), cfn=lambda p: cf(p))
    bm.free()


def rect_rug(cx, cy, W, D, rot=0, stripes=None, border='#7b3b2c', field='#d8c8a6', fringe=True, pattern='diamond'):
    cb, cfld = C(border), C(field)
    acc = [C(c) for c in (stripes or ['#3f5f55', '#c7a04a', '#8c3a2e'])]
    inv = Matrix.Rotation(-math.radians(rot), 3, 'Z')
    def cf(p):
        q = inv @ Vector((p.x - cx, p.y - cy, 0))
        u = q.x / (W / 2); v = q.y / (D / 2)
        du = (1 - abs(u)) * W / 2; dv = (1 - abs(v)) * D / 2
        d = min(du, dv)
        w = 0.35 * (0.9 + 0.1 * nz(p.x * 3, p.y * 3))
        th = 1 + 0.07 * nz(p.x * 40, p.y * 40)
        if d < 0.04:
            c = acc[2]
        elif d < 0.08:
            c = cfld
        elif d < 0.16:
            c = cb
        elif d < 0.2:
            c = acc[1]
        elif d < 0.24:
            c = cfld
        else:
            # diamond pattern
            uu = (q.x / 0.3) ; vv = (q.y / 0.3)
            dd = abs((uu % 1.0) - 0.5) + abs((vv % 1.0) - 0.5)
            c = acc[0] if dd < 0.22 else (acc[1] if dd < 0.3 else cfld)
            if dd < 0.1:
                c = cb
        return (c[0] * th, c[1] * th, c[2] * th)
    M_ = xf((cx, cy, F + 0.001), (0, 0, rot))
    cloth(M['knit_vc'], -W / 2, W / 2, -D / 2, D / 2, 32, 24, lambda x, y: 0.014 + 0.003 * nz(x * 20, y * 20) - (0.004 if (abs(x) > W / 2 - 0.02 or abs(y) > D / 2 - 0.02) else 0), 0.0, cfn=cf, M=M_, solid=False)
    if fringe:
        for s in (-1, 1):
            box(M['rope'], M_ @ Vector((s * (W / 2 + 0.03), 0, 0.004)), (0.06, D - 0.02, 0.004), (0, 0, rot), bev=0, col=(0.85, 0.8, 0.68), cuts=0)
            for i in range(0, int(D / 0.12)):
                y = -D / 2 + 0.06 + i * 0.12
                box(M['rope'], M_ @ Vector((s * (W / 2 + 0.035), y, 0.006)), (0.07, 0.004, 0.003), (0, 0, rot + rnd.uniform(-8, 8)), bev=0, col=(0.6, 0.55, 0.45))


def sheepskin(cx, cy, rot=0, sz=(0.62, 0.9)):
    cf = lambda p: (0.9 + 0.08 * nz(p.x * 18, p.y * 18), 0.86 + 0.08 * nz(p.x * 18, p.y * 18), 0.78 + 0.07 * nz(p.x * 18, p.y * 18))
    bm = bmesh.new()
    S = 28; R = 6
    ctr = bm.verts.new((0, 0, 0.022))
    rows = []
    for i in range(1, R + 1):
        t = i / R
        row = []
        for j in range(S):
            th = j / S * TAU
            wob = 1 + 0.12 * math.sin(th * 3 + 1) + 0.08 * math.sin(th * 5) + 0.05 * nz(math.cos(th) * 2, math.sin(th) * 2, 3)
            row.append(bm.verts.new((sz[0] / 2 * t * math.cos(th) * wob, sz[1] / 2 * t * math.sin(th) * wob, 0.022 * (1 - t ** 3) + 0.003 + 0.008 * nz(t * math.cos(th) * 8, t * math.sin(th) * 8))))
        rows.append(row)
    for j in range(S):
        k = (j + 1) % S
        bm.faces.new([ctr, rows[0][j], rows[0][k]])
    for i in range(R - 1):
        for j in range(S):
            k = (j + 1) % S
            bm.faces.new([rows[i][j], rows[i + 1][j], rows[i + 1][k], rows[i][k]])
    sk = [bm.verts.new((v.co.x, v.co.y, 0.0)) for v in rows[-1]]
    for j in range(S):
        k = (j + 1) % S
        bm.faces.new([rows[-1][j], rows[-1][k], sk[k], sk[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    put(M['fur'], bm, xf((cx, cy, F + 0.012), (0, 0, rot)), (1, 1, 1), cfn=cf)
    bm.free()
    # fluffy tufts along the edge
    for i in range(22):
        th = rnd.uniform(0, TAU)
        x = math.cos(th) * sz[0] * 0.5 * (0.9 + 0.15 * rnd.random()); y = math.sin(th) * sz[1] * 0.5 * (0.9 + 0.15 * rnd.random())
        q = xf((cx, cy, F + 0.015), (0, 0, rot)) @ Vector((x, y, 0))
        box(M['fur'], q + V(0, 0, 0.012), (0.004, 0.004, 0.028), (rnd.uniform(-40, 40), rnd.uniform(-40, 40), 0), bev=0, col=(0.94, 0.9, 0.82))


# ====================================================================== bookshelf
def bookshelf(pos, rot, W=1.3, D=0.32, H=2.2, seed=5, curios=True):
    rr = random.Random(seed)
    f = Fr(pos, rot, F)
    mat = 'wood_dark'
    col = (1, 0.96, 0.92)
    t = 0.022
    # sides, back, top, base
    for s in (-1, 1):
        f.box(M[mat], (s * (W / 2 - t / 2), 0, H / 2), (t, D, H), bev=0.004, col=col, g=2, cuts=3)
    f.box(M['wood_walnut'], (0, -D / 2 + 0.01, H / 2), (W - 2 * t, 0.014, H), bev=0, col=(0.9, 0.85, 0.8), g=2, cuts=2)
    f.box(M[mat], (0, 0, H - 0.02), (W + 0.04, D + 0.03, 0.04), bev=0.006, col=col, g=0, cuts=3)
    f.box(M[mat], (0, 0.0, H + 0.015), (W + 0.06, D + 0.05, 0.02), bev=0.005, col=col, g=0)
    f.box(M[mat], (0, D / 2 - 0.01, 0.055), (W, 0.022, 0.11), bev=0.004, col=col, g=0)   # plinth
    f.box(M[mat], (0, 0, 0.03), (W - 2 * t, D - 0.03, 0.03), bev=0.003, col=col, g=0)
    levels = [0.12, 0.47, 0.81, 1.15, 1.49, 1.83]
    tops = levels[1:] + [H - 0.04]
    for i, z in enumerate(levels):
        if i > 0:
            f.box(M[mat], (0, 0.0, z - 0.011), (W - 2 * t, D - 0.03, 0.022), bev=0.003, col=col, g=0, cuts=3)
            f.box(M[mat], (0, D / 2 - 0.022, z - 0.011), (W - 2 * t, 0.02, 0.03), bev=0.003, col=col, g=0)
        # content
        zb = z
        clear = tops[i] - z - 0.03
        x = -W / 2 + t + 0.01
        x_end = W / 2 - t - 0.01
        curio_slots = rr.sample(range(6), 2) if curios else []
        blk = 0
        while x < x_end - 0.03:
            if rr.random() < 0.07 and curios and x < x_end - 0.2:
                # curio
                kind = rr.choice(['jar', 'frame', 'vase', 'candle', 'shell', 'bird', 'plant', 'globe'])
                w = 0.14
                cx_ = x + w / 2
                q = f.p((cx_, 0.0, z + zb * 0))
                q.z = F + zb
                if kind == 'jar':
                    jar(q, r=0.05, h=min(0.17, clear - 0.05), content=(0.7, rr.choice([(0.85, 0.5, 0.2), (0.6, 0.15, 0.1), (0.4, 0.6, 0.2)])), lidcol=(0.75, 0.6, 0.3))
                elif kind == 'frame':
                    photo_frame(q, rot, w=0.13, h=0.17, tilt=-10, seed=rr.randint(0, 9))
                elif kind == 'vase':
                    vase_flowers(q, kind=rr.choice(['dried', 'lav']), h=min(0.18, clear * 0.5), r=0.045, n=6, vcol=rr.choice(['#b5562f', '#3e6a66', '#d9c7a0']), seed=rr.randint(0, 99))
                elif kind == 'candle':
                    candle_holder(q, h=0.12, candle=True, cl=0.1, flame_it=False)
                elif kind == 'shell':
                    lathe(M['ceramic_white'], q + V(0, 0, 0.0), [(0.001, 0), (0.05, 0.0), (0.06, 0.03), (0.04, 0.06), (0.001, 0.07)], 10, cap=False, rot=(0, 0, rr.uniform(0, 360)), col=(0.95, 0.85, 0.8))
                elif kind == 'bird':
                    sphere(M['wood_oak'], q + V(0, 0, 0.05), 0.035, seg=8, rings=5, sq=(0.8, 1.3, 1.0))
                    sphere(M['wood_oak'], q + V(0, -0.04 if True else 0, 0.09), 0.02, seg=8, rings=4)
                    box(M['brass'], q + V(0, -0.06, 0.09), (0.005, 0.02, 0.005), bev=0)
                elif kind == 'plant':
                    f2 = q
                    bowl(q, r=0.055, h=0.07, mat='terracotta')
                    for k in range(9):
                        a = rr.uniform(0, TAU)
                        tube(M['herb_vc'], [q + V(0, 0, 0.06), q + V(math.cos(a) * 0.04, math.sin(a) * 0.04, 0.12 + rr.random() * 0.03), q + V(math.cos(a) * 0.09, math.sin(a) * 0.09, 0.09 + rr.random() * 0.04)], 0.002, 4, col=(0.25, 0.45, 0.2), caps=False)
                        sphere(M['herb_vc'], q + V(math.cos(a) * 0.09, math.sin(a) * 0.09, 0.09), 0.015, seg=5, rings=3, sq=(1, 1, 0.3), col=(0.22, 0.45, 0.18))
                elif kind == 'globe':
                    cyl(M['brass'], q + V(0, 0, 0.005), 0.04, 0.01, seg=12)
                    cyl(M['brass'], q + V(0, 0, 0.03), 0.006, 0.05, seg=6)
                    sphere(M['paint_vc'], q + V(0, 0, 0.1), 0.06, seg=16, rings=10, col=(0.3, 0.45, 0.35), cfn=lambda p: (0.25, 0.45, 0.5) if nz(p.x * 30, p.y * 30, p.z * 30) > 0.05 else (0.6, 0.55, 0.3))
                x += w + 0.02
                continue
            # run of books
            nb = rr.randint(3, 7)
            lean_end = rr.random() < 0.5
            for k in range(nb):
                w = rr.uniform(0.022, 0.05)
                if x + w > x_end:
                    break
                h = rr.uniform(0.18, min(0.33, clear - 0.015))
                d = rr.uniform(0.17, 0.25)
                q = f.p((x + w / 2, D / 2 - d / 2 - 0.03, 0))
                q.z = F + zb
                lean = 0
                if k == nb - 1 and lean_end:
                    lean = 0  # straight
                book(q, (w, d, h), rotz=rot + 180, lean=0, col=None, gold=True)
                x += w + 0.001
            if rr.random() < 0.5:
                # a horizontal stack
                if x < x_end - 0.3:
                    n = rr.randint(2, 4)
                    zz = 0
                    for k in range(n):
                        bw, bd, bh = rr.uniform(0.2, 0.26), rr.uniform(0.15, 0.2), rr.uniform(0.025, 0.05)
                        q = f.p((x + 0.14, 0.02, 0)); q.z = F + zb + zz + 0.002
                        book_flat(q - V(bw / 2 * 0, 0, 0), (bw, bd, bh), rotz=rot + rr.uniform(-8, 8) + 90 + 180)
                        zz += bh
                    x += 0.30
    collider_f(f, W, D + 0.05, F + H)
    return f


# ====================================================================== fire tools etc
def fireplace_set(base):
    """tool stand, log basket: base = world pos of the tool stand"""
    f = Fr(base, 0, F)
    # stand
    f.cyl(M['iron_black'], (0, 0, 0.012), 0.11, 0.024, seg=14, bev=0.005)
    f.cyl(M['iron_black'], (0, 0, 0.36), 0.008, 0.7, seg=6)
    f.lathe(M['iron_black'], (0, 0, 0.72), [(0.001, 0), (0.02, 0.01), (0.014, 0.03), (0.001, 0.04)], seg=8)
    tube(M['iron_black'], arcpts(f.p((0, 0, 0.66)), 0.05, 0, 360, 10, 'xy'), 0.004, 5)
    # poker
    f.tube(M['iron_black'], [Vector((0.02, 0.0, 0.08)), Vector((0.03, 0.01, 0.35)), Vector((0.03, 0.01, 0.6)), Vector((0.022, 0.012, 0.66))], 0.0065, seg=6)
    f.tube(M['iron_black'], [Vector((0.022, 0.012, 0.66)), Vector((0.05, 0.03, 0.66)), Vector((0.06, 0.05, 0.63))], 0.005, seg=5)
    # tongs
    f.tube(M['iron_black'], [Vector((-0.03, 0.0, 0.1)), Vector((-0.035, -0.012, 0.35)), Vector((-0.02, -0.01, 0.62)), Vector((-0.01, -0.005, 0.7))], 0.007, seg=6)
    f.tube(M['iron_black'], [Vector((-0.03, 0.03, 0.1)), Vector((-0.03, 0.02, 0.35)), Vector((-0.012, 0.0, 0.62))], 0.006, seg=5)
    # shovel
    f.tube(M['iron_black'], [Vector((0.0, -0.03, 0.08)), Vector((0.0, -0.04, 0.4)), Vector((0.0, -0.035, 0.66))], 0.006, seg=5)
    f.box(M['iron_black'], (0.0, -0.03, 0.09), (0.07, 0.008, 0.09), bev=0.002)
    f.tube(M['wood_dark'], [Vector((0.02, 0.05, 0.6)), Vector((0.03, 0.05, 0.7))], 0.012, seg=6)
    # bellows
    g = Fr(f.p((0.42, -0.1, 0)), 25, F)
    bl = g
    g.box(M['wood_walnut'], (0, -0.1, 0.17), (0.27, 0.22, 0.025), r=(0, 0, 0), bev=0.004)
    # bellows: two wooden boards + leather accordion
    def bw(zc):
        pass
    g.box(M['wood_walnut'], (0, 0, 0.15), (0.26, 0.3, 0.02), r=(0, 0, 0), bev=0.006)
    g.box(M['wood_walnut'], (0, 0.0, 0.05), (0.26, 0.3, 0.02), r=(-4, 0, 0), bev=0.006)
    g.lathe(M['leather_vc'], (0, 0.0, 0.055), [(0.12, 0), (0.15, 0.02), (0.11, 0.045), (0.15, 0.07), (0.11, 0.09), (0.12, 0.095)], seg=10, cap=False, col=C('#6a4a2e'), ) if False else None
    g.cloth(M['leather_vc'], -0.12, 0.12, -0.14, 0.14, 4, 4, lambda x, y: 0.15, 0.06, col=C('#6a4a2e'))
    for sx in (-1, 1):
        g.box(M['brass'], (sx * 0.13, 0, 0.1), (0.008, 0.26, 0.11), bev=0.002)
    g.tube(M['iron_black'], [Vector((0, 0.15, 0.1)), Vector((0, 0.36, 0.06)), Vector((0, 0.42, 0.055))], 0.013, seg=8)
    g.tube(M['wood_walnut'], [Vector((0, -0.15, 0.17)), Vector((0, -0.3, 0.2)), Vector((0, -0.36, 0.21))], 0.014, seg=6)


def log_basket(pos, rot=0, r=0.27):
    f = Fr(pos, rot, F)
    basket(f.p((0, 0, 0)), r=r, h=0.36, handle=True, rot=(0, 0, rot))
    # logs
    rr = random.Random(9)
    for i in range(7):
        a = rr.uniform(-0.7, 0.7)
        x = (i - 3) * 0.07 + rr.uniform(-0.02, 0.02)
        L = rr.uniform(0.34, 0.42)
        q = f.p((x, rr.uniform(-0.02, 0.02), 0.26 + rr.uniform(0, 0.08)))
        log(q, L=L, r=rr.uniform(0.05, 0.065), rot=(rr.uniform(-8, 8), 0, rot + rr.uniform(-8, 8)), axis='y')
    for i in range(4):
        q = f.p((rr.uniform(-0.12, 0.12), rr.uniform(-0.1, 0.1), 0.05 + 0.1 * i))
        log(q, L=0.36, r=0.055, rot=(0, 0, rot + 90 + rr.uniform(-15, 15)), axis='y')
    collider_f(f, 2 * r, 2 * r, F + 0.36)


def clock_longcase(pos, rot):
    f = Fr(pos, rot, F)
    W, D, H = 0.46, 0.26, 2.05
    m = 'wood_walnut'
    col = (1, 0.95, 0.9)
    f.box(M[m], (0, 0, 0.09), (W + 0.04, D + 0.03, 0.18), bev=0.006, col=col, g=0, cuts=1)
    f.box(M[m], (0, 0, 0.5), (W - 0.06, D - 0.03, 0.6), bev=0.005, col=col, cuts=2)
    # trunk glass window with dark interior
    f.box(M['wood_walnut'], (0, -D / 2 + 0.02, 1.13), (W - 0.1, 0.02, 0.72), bev=0.004, col=(0.5, 0.42, 0.36))
    for s_ in (-1, 1):
        f.box(M['wood_walnut'], (s_ * (W / 2 - 0.045), 0, 1.13), (0.03, D - 0.04, 0.72), bev=0.004, col=col)
    f.box(M['glass'], (0, D / 2 - 0.012, 1.13), (W - 0.12, 0.004, 0.7), bev=0)
    for z_ in (0.78, 1.49):
        f.box(M['wood_walnut'], (0, D / 2 - 0.012, z_), (W - 0.1, 0.02, 0.03), bev=0.003, col=col)
    # waist
    f.box(M[m], (0, 0, 1.52), (W + 0.02, D, 0.06), bev=0.008, col=col)
    # hood
    f.box(M[m], (0, 0, 1.78), (W, D, 0.5), bev=0.006, col=col)
    f.box(M[m], (0, 0, 2.06), (W + 0.04, D + 0.03, 0.05), bev=0.008, col=col)
    # dial
    f.cyl(M['brass'], (0, D / 2 + 0.002, 1.79), 0.15, 0.008, axis='y', seg=28)
    f.cyl(M['paper'], (0, D / 2 + 0.007, 1.79), 0.135, 0.004, axis='y', seg=28, col=(0.95, 0.92, 0.85))
    for i in range(12):
        a = i * TAU / 12
        f.box(M['ink'], (math.sin(a) * 0.11, D / 2 + 0.011, 1.79 + math.cos(a) * 0.11), (0.006, 0.002, 0.018), r=(0, -math.degrees(a), 0), bev=0, col=(0.05, 0.05, 0.05))
    f.box(M['ink'], (0.02, D / 2 + 0.012, 1.81), (0.008, 0.003, 0.085), r=(0, -30, 0), bev=0, col=(0.03, 0.03, 0.03))
    f.box(M['ink'], (-0.01, D / 2 + 0.012, 1.78), (0.005, 0.003, 0.11), r=(0, 70, 0), bev=0, col=(0.03, 0.03, 0.03))
    # columns/finial
    for s in (-1, 1):
        f.lathe(M['brass'], (s * (W / 2 - 0.02), D / 2 - 0.02, 2.085), [(0.001, 0), (0.02, 0.0), (0.012, 0.03), (0.001, 0.06)], seg=8, cap=False)
    # pendulum window dark backing is inside; pendulum part separate
    saved = part_begin()
    pivot = f.p((0, 0.0, 1.3))
    g = Fr(pivot, rot, None)
    g.tube(M['brass'], [Vector((0, 0, 0)), Vector((0, 0, -0.42))], 0.0025, seg=6)
    g.cyl(M['brass'], (0, 0, -0.45), 0.055, 0.008, axis='y', seg=20)
    g.cyl(M['brass'], (0, 0, -0.45), 0.03, 0.012, axis='y', seg=16)
    g.box(M['brass'], (0, 0, -0.012), (0.014, 0.008, 0.024), bev=0.001)
    part_end(saved, 'clock_pendulum', pivot)
    # weights
    for s in (-1, 1):
        f.cyl(M['pewter'], (s * 0.1, 0.0, 0.85 + s * 0.03), 0.028, 0.22, seg=10)
    collider_f(f, W + 0.04, D + 0.03, F + 2.1)
    return f
