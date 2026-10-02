import sys
sys.path.insert(0, '/shared/river/assets/blender')
from vh_base import *

rng.seed(404)
W, D = 8.0, 7.0
ye = D / 2
ze = 3.1
K = 0.8
fr = frames(W, D)
F, Bk, R, L = fr['F'], fr['B'], fr['R'], fr['L']
PL = (1.0, 0.9, 0.7)
OPS = {
    'F': [win_hole(-1.9, 1.75, 2.0, 1.3), (1.5, 2.5, Z0, Z0 + 2.1), win_hole(3.25, 1.7, 0.7, 1.1)],
    'B': [win_hole(-2.2, 1.65, 1.0, 1.2), win_hole(0.6, 1.65, 1.0, 1.2), (2.4, 3.3, Z0, Z0 + 2.05)],
    'R': [win_hole(-1.5, 1.65, 0.9, 1.15)],
    'L': [win_hole(-1.3, 1.65, 0.9, 1.15), win_hole(1.3, 1.65, 0.9, 1.15)],
}


def dome(c, rx, ry, rz, rows=6, segs=18, col=(1, 1, 1)):
    """brick dome (upper half ellipsoid), per-face brick colours."""
    bm = B('brick'); setbm(bm)
    c = V3(c)
    rings = []
    for r in range(rows + 1):
        a = (math.pi / 2) * r / rows
        rr = math.cos(a); z = math.sin(a)
        if r == rows:
            rings.append([bm.verts.new(c + V3((0, 0, rz)))])
        else:
            rings.append([bm.verts.new(c + V3((rx * rr * math.cos(2 * math.pi * i / segs), ry * rr * math.sin(2 * math.pi * i / segs), rz * z))) for i in range(segs)])
    cl = bm.loops.layers.float_color['Col']
    for r in range(rows):
        A, Bq = rings[r], rings[r + 1]
        for i in range(segs):
            j = (i + 1) % segs
            f = addface(bm, [A[i], A[j], Bq[j], Bq[i]] if len(Bq) > 1 else [A[i], A[j], Bq[0]], c - V3((0, 0, 0.2)))
            k = rng.uniform(0.75, 1.1)
            cc = rng.choice([(1.0, 0.82, 0.72), (0.9, 0.68, 0.56), (1.1, 0.95, 0.85), (0.8, 0.6, 0.5)])
            for l in f.loops:
                l[cl] = (cc[0] * k * col[0], cc[1] * k * col[1], cc[2] * k * col[2], 1.0)


def awning(Fk, u0, u1, zw, zf, depth, nstr=10):
    sw = (u1 - u0) / nstr
    for k in range(nstr):
        ua, ub = u0 + k * sw, u0 + (k + 1) * sw
        col = (0.78, 0.16, 0.12) if k % 2 == 0 else (0.95, 0.92, 0.82)
        a = Fk.P(ua, 0.02, zw); 
        slope = Fk.P(ua, depth, zf) - a
        obox('canvas', a, Fk.U, slope, Fk.U.cross(slope).normalized() * (1 if (Fk.U.cross(slope).z > 0) else -1), sw - 0.002, slope.length, 0.012, col=col, cj=0.04)
        # valance flap with scalloped lower edge
        Fk.poly('canvas', [(ua, zf - 0.0), (ub - 0.002, zf), (ub - 0.002, zf - 0.17), ((ua + ub) / 2, zf - 0.24), (ua, zf - 0.17)], depth - 0.005, depth + 0.012, col=col, cj=0.04)
    for u in (u0 + 0.05, u1 - 0.05):
        cyl('iron', Fk.P(u, 0.0, zw - 0.12), Fk.P(u, depth - 0.02, zf - 0.1), 0.012, segs=5)
        cyl('iron', Fk.P(u, 0.0, zw), Fk.P(u, depth, zf - 0.02), 0.012, segs=5)


def pretzel(Fk, u, n, z, bw, bh):
    P = lambda a, b: Fk.P(u + a, n + 0.04, z + b)
    lob = [P(0.2 * math.sin(t), 0.1 * math.sin(2 * t) + 0.05) for t in [i * 2 * math.pi / 28 for i in range(29)]]
    tube('rope', lob, 0.026, segs=6, pn=Fk.N, caps=True, col=(1.0, 0.7, 0.4))
    arc = [P(0.2 * math.cos(t), 0.05 - 0.2 * math.sin(t)) for t in [math.pi * i / 14 for i in range(15)]]
    tube('rope', arc, 0.026, segs=6, pn=Fk.N, col=(1.0, 0.7, 0.4))
    tube('rope', [P(-0.2, 0.05), P(-0.2, 0.05)] if False else [P(0.2 * math.sin(t), 0.1 * math.sin(2 * t) + 0.05) for t in (0.9, 1.0)], 0.0, segs=3) if False else None
    for sx in (-1, 1):
        for k in range(5):
            blob('chalk', P(sx * 0.2 + rng.uniform(-0.02, 0.02) , 0.05 - 0.2 * rng.random() * 0 + (rng.random() - 0.5) * 0.0), 0.012) if False else None


def loaf(x, y, z, s=1.0, rot=0.0):
    with placed((x, y, z), rot):
        fs = lathe('bread', (0, 0, 0), [(0, 0.05), (0.02, 0.11), (0.07, 0.13), (0.12, 0.1), (0.14, 0.05)], segs=8, col=tint(1, 1, 1, 0.15), cj=0.1)
        vs = {v for f in fs for v in f.verts}
        for v in vs:
            v.co.x *= 1.9 * s; v.co.y *= 0.8 * s; v.co.z *= s


def basket(x, y, z, r=0.2, h=0.14, bread=True):
    lathe('wicker', (x, y, z), [(0, r * 0.8), (0.01, r * 0.82), (h, r), (h + 0.015, r)], segs=12, col=tint(1, 1, 1, 0.1), cj=0.1)
    lathe('wicker', (x, y, z + h - 0.02), [(0, r * 0.93), (0.01, r * 0.93)], segs=12, col=(0.5, 0.4, 0.3))
    if bread:
        for i in range(3):
            loaf(x + rng.uniform(-r * 0.4, r * 0.4), y + rng.uniform(-r * 0.4, r * 0.4), z + h - 0.03, 0.6, rng.uniform(0, 6))


plinth(W, D)
for key, Fk, half in (('F', F, W / 2), ('B', Bk, W / 2), ('R', R, D / 2), ('L', L, D / 2)):
    plaster_wall(Fk, -half, half, Z0, ze, OPS[key], col=tint(*PL, 0.02))
corner_posts(W, D, Z0, ze + 0.02, mat='paint_trim', sz=0.22, proud=0.025)
for Fk, half in ((F, W / 2), (Bk, W / 2)):
    Fk.prism('paint_trim', [(0, ze - 0.2), (0.12, ze - 0.2), (0.12, ze - 0.14), (0.04, ze - 0.06), (0.04, ze)], -half, half)
    Fk.box('paint_trim', -half, half, 0, 0.05, Z0, Z0 + 0.14, n=(6, 1, 1))
for Fk in (R, L):
    hole = [win_hole(0, ze + 0.9, 0.7, 0.8)]
    gable_fill(Fk, ye, ze, ze + K * ye, 'lap', holes=hole)
    window(Fk, 0, ze + 0.9, 0.7, 0.8, rows=2, cols=1, shutters=False)
for (Fk, key) in ((F, 'F'), (Bk, 'B'), (R, 'R'), (L, 'L')):
    for h in OPS[key]:
        uc, zc = (h[0] + h[1]) / 2, (h[2] + h[3]) / 2
        w, hh = h[1] - h[0], h[3] - h[2]
        if h[2] <= Z0 + 0.01:
            door(Fk, uc, w, hh, mat='paint_door', glazed=(Fk is F), lintel=None)
        elif Fk is F and w > 1.5:
            window(Fk, uc, zc, w, hh, rows=3, cols=2, shutters=False, flowerbox=False)
        else:
            window(Fk, uc, zc, w, hh, rows=3 if hh > 1.15 else 2, cols=1, shutters=(Fk is not R and Fk is not L), flowerbox=(Fk is F))
# shop counter shelf + goods
sx0, sx1 = -3.0, -0.8
F.box('timber_beam', sx0, sx1, 0.0, 0.42, 1.04, 1.1, n=(4, 1, 1), cj=0.08)
F.box('timber_beam', sx0 - 0.02, sx1 + 0.02, 0.39, 0.43, 0.96, 1.1)
for u in (sx0 + 0.2, sx1 - 0.2, (sx0 + sx1) / 2):
    cyl('timber_dark', F.P(u, 0.03, 0.55), F.P(u, 0.36, 1.03), 0.028, segs=5)
    F.box('timber_dark', u - 0.04, u + 0.04, 0.0, 0.04, 0.5, 1.05)
basket(*F.P(-2.55, 0.2, 1.1)[:2], 1.1, 0.18, 0.15)
basket(*F.P(-1.25, 0.2, 1.1)[:2], 1.1, 0.16, 0.13)
for k in range(5):
    loaf(*F.P(-2.0 + k * 0.17, 0.2 + (k % 2) * 0.05, 1.1)[:2], 1.1, 0.9, rng.uniform(-0.3, 0.3) + math.pi / 2 * (k % 2))
awning(F, -3.15, -0.65, 2.7, 2.35, 1.05)
# hanging pretzel sign
def pretzel_emblem(Fk, u, n, z, bw, bh):
    pretzel(Fk, u, n, z, bw, bh)
hanging_sign(F, 3.4, 2.75, board_w=0.6, board_h=0.6, arm=1.0, emblem=pretzel_emblem, board_mat='timber_beam', drop=0.28)
lantern(F, 0.6, 0, 1.95)
# dormer (attic window) + roof
zr, zs = None, None
zr_, zs_ = ze + K * ye + 0.14, (lambda y, zr=ze + K * ye + 0.14: zr - K * abs(y))
dormer(ye - 1.0, 0.0, 1.9, zs_, K, K2=0.8, hgt=1.35, window_w=0.9, window_h=0.95, flowerbox=True)
dormer(ye - 1.0, -2.6, 1.3, zs_, K, K2=0.8, hgt=1.3, window_w=0.6, window_h=0.8) if False else None
zr, zs = gable_roof(-W / 2 - 0.45, W / 2 + 0.2, ye, ze, K, oy=0.55, gutters=(-1, 1))
yo = ye + 0.55
for (x, s) in ((-W / 2 + 0.3, -1), (-W / 2 + 0.3, 1)):
    downspout(x, s * (yo + 0.1), zs(yo) - 0.16, s * (ye + 0.06), s)
# oven on the right wall: platform, dome, mouth, chimney
ox0, ox1, oy0, oy1 = W / 2 + 0.02, W / 2 + 1.7, -0.5, 1.6
box('mortar', ox0, ox1 - 0.05, oy0 + 0.05, oy1 - 0.05, -0.3, 0.88)
for (x0, x1, y0, y1) in ((ox0, ox1, oy0, oy0 + 0.0), ):
    pass
pal = PAL_STONE
fo = [Fr((ox1 - 0.05, (oy0 + oy1) / 2, 0), (0, 1, 0), (1, 0, 0)), Fr(((ox0 + ox1) / 2, oy0 + 0.05, 0), (1, 0, 0), (0, -1, 0)), Fr(((ox0 + ox1) / 2, oy1 - 0.05, 0), (-1, 0, 0), (0, 1, 0))]
masonry(fo[0], 'stone_wall', -(oy1 - oy0) / 2, (oy1 - oy0) / 2, -0.3, 0.88, -0.1, 0.03, pal=pal, hs=(0.17, 0.25), ws=(0.3, 0.5), m=1, k=0.6)
masonry(fo[1], 'stone_wall', -(ox1 - ox0) / 2, (ox1 - ox0) / 2, -0.3, 0.88, -0.1, 0.03, pal=pal, hs=(0.17, 0.25), ws=(0.3, 0.5), m=1, k=0.6)
masonry(fo[2], 'stone_wall', -(ox1 - ox0) / 2, (ox1 - ox0) / 2, -0.3, 0.88, -0.1, 0.03, pal=pal, hs=(0.17, 0.25), ws=(0.3, 0.5), m=1, k=0.6)
box('stone_wall', ox0, ox1 + 0.04, oy0 - 0.04, oy1 + 0.04, 0.86, 0.94, n=(4, 4, 1), cj=0.06)
cx_o, cy_o = (ox0 + ox1) / 2 + 0.05, (oy0 + oy1) / 2 + 0.2
dome((cx_o, cy_o, 0.94), 0.72, 0.8, 0.78, rows=6, segs=20)
# mouth (arched opening on the front -y side)
mz = 1.2
box('soot', cx_o - 0.22, cx_o + 0.22, cy_o - 0.86, cy_o - 0.64, 0.97, mz)
box('stone_wall', cx_o - 0.3, cx_o - 0.22, cy_o - 0.88, cy_o - 0.62, 0.94, mz + 0.05)
box('stone_wall', cx_o + 0.22, cx_o + 0.3, cy_o - 0.88, cy_o - 0.62, 0.94, mz + 0.05)
box('stone_wall', cx_o - 0.3, cx_o + 0.3, cy_o - 0.88, cy_o - 0.62, mz, mz + 0.08)
# oven chimney
chimney(W / 2 + 0.55, 0.9, 0.6, 0.6, 1.6, zr + 0.5, kind='brick', name='oven')
# main ridge chimney
chimney(-1.8, 0.0, 1.0, 0.7, ze + 0.3, zr + 1.35, kind='brick')
flashing(-1.8, 0.0, 1.0, 0.7, zr - K * 0.4 - 0.03)
# props
for (x, y, s) in ((2.45, -ye - 0.5, 1.0), (2.85, -ye - 0.55, 0.9)):
    sack(x, y, 0.0, s, col=(1.15, 1.1, 1.0), rot=0)
sack(3.05, -ye - 0.9, 0.0, 0.95, col=(1.1, 1.05, 0.95))
barrel(0.6, -ye - 0.5, 0.0, 0.3, 0.8)
crate(-3.6, -ye - 0.5, 0.0, 0.55, 0.45, 0.4, 0.2)
bench(-0.0, -ye - 0.35, 0.0, 1.3, 0.0) if False else None
woodpile(-1.0, ye + 0.05, 0.0, 2.2, 1.3, depth=0.5)
pot(1.15, -ye - 0.4)
bucket(-0.6, -ye - 0.4)

cols = [C(-W / 2 - 0.1, W / 2 + 0.1, -D / 2 - 0.1, D / 2 + 0.1, ze, -0.5), C(W / 2, W / 2 + 1.75, oy0, oy1, 1.8, -0.3),
        C(-3.2, -0.6, -D / 2 - 0.5, -D / 2, 1.1, 0)]
views = {
    'front34': ((-10.5, -11.5, 2.4), (0.5, 0, 2.7), 35),
    'back34': ((10, 11.5, 3.2), (0, 0, 2.7), 35),
    'shop': ((-3.5, -7.2, 1.8), (-1.5, -3.5, 1.7), 35),
    'oven': ((7.5, -5.5, 2.2), (4.6, 0.4, 1.6), 35),
}
finish('bakery', W, D, ze, zr + 0.07, (2.0, -D / 2), 'shop', '빵집', cols, views)
