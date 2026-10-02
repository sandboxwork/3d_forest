import sys
sys.path.insert(0, '/shared/river/assets/blender')
import hs_lib
from hs_lib import *
import importlib

reset_scene()
hs_lib.CUR = {}

# ------------------------------------------------------------------ materials
MATDEF = [
    ('stone_foundation', '#8f8b80', 0.92, 0, {}),
    ('stone_chimney', '#9b958a', 0.92, 0, {}),
    ('stone_fireplace', '#a39c8f', 0.9, 0, {}),
    ('hearth_stone', '#7e7a72', 0.85, 0, {}),
    ('stone_garden', '#8a877c', 0.93, 0, {}),
    ('mortar', '#a9a293', 1.0, 0, {}),
    ('siding_wood', '#8c7556', 0.88, 0, {}),
    ('trim_paint', '#e9e4d3', 0.55, 0, {}),
    ('timber_dark', '#5d4532', 0.82, 0, {}),
    ('timber_beam', '#6e4f35', 0.78, 0, {}),
    ('roof_shingle', '#7a6650', 0.9, 0, {}),
    ('roof_deck', '#4f3d2d', 0.9, 0, {}),
    ('zinc', '#a9afb0', 0.42, 0.85, {}),
    ('brass', '#c29a45', 0.32, 1.0, {}),
    ('iron', '#2a2826', 0.55, 0.8, {}),
    ('glass', '#c5dde2', 0.05, 0.0, dict(alpha=0.25)),
    ('floor_planks', '#a4764a', 0.62, 0, {}),
    ('wainscot', '#bf9d72', 0.55, 0, {}),
    ('plaster_wall', '#eae2cf', 0.96, 0, {}),
    ('ceiling_planks', '#b6926a', 0.7, 0, {}),
    ('paint_shutter', '#4d6a50', 0.6, 0, {}),
    ('door_paint', '#7d3329', 0.55, 0, {}),
    ('door_wood', '#8e6b47', 0.6, 0, {}),
    ('soot', '#171412', 1.0, 0, {}),
    ('fire_embers', '#ff5a1a', 0.9, 0, dict(emit='#ff4a10', emit_strength=3.0)),
    ('charred_wood', '#2a231f', 0.95, 0, {}),
    ('soil', '#3b2e22', 1.0, 0, {}),
    ('bark', '#56402d', 0.95, 0, dict(tex='bark')),
    ('endgrain', '#c8a06a', 0.85, 0, {}),
    ('shed_wood', '#6d5b49', 0.9, 0, {}),
    ('deck_planks', '#947656', 0.75, 0, {}),
]
MAT = {}
for n, c, r, m, kw in MATDEF:
    MAT[n] = make_mat(n, c, rough=r, metal=m, **kw)
MATNAMES = [m[0] for m in MATDEF]

BEV = {'timber_dark': 0.008, 'timber_beam': 0.012, 'trim_paint': 0.004, 'floor_planks': 0.0025, 'ceiling_planks': 0.0025,
       'paint_shutter': 0.003, 'door_paint': 0.004, 'door_wood': 0.004, 'deck_planks': 0.003, 'shed_wood': 0.004,
       'wainscot': 0.0, 'brass': 0.0, 'zinc': 0.0}

# ------------------------------------------------------------------ frames & constants
K = 0.5714       # roof slope
FRONT = Fr((0, -3.5, 0), (1, 0, 0), (0, -1, 0))
BACK = Fr((0, 3.5, 0), (-1, 0, 0), (0, 1, 0))
RIGHT = Fr((4.5, 0, 0), (0, 1, 0), (1, 0, 0))
LEFT = Fr((-4.5, 0, 0), (0, -1, 0), (-1, 0, 0))
G_FRONT = Fr((0, -3.25, 0), (1, 0, 0), (0, 1, 0))
G_BACK = Fr((0, 3.25, 0), (-1, 0, 0), (0, -1, 0))
G_RIGHT = Fr((4.25, 0, 0), (0, 1, 0), (-1, 0, 0))
G_LEFT = Fr((-4.25, 0, 0), (0, -1, 0), (1, 0, 0))
PB = Fr((1.65, 0, 0), (0, 1, 0), (1, 0, 0))     # partition, bedroom face
PL = Fr((1.4, 0, 0), (0, 1, 0), (-1, 0, 0))     # partition, living face (u = +y too)
Z0, ZE = 0.30, 3.2

GLASS_OPS = []
EXTRA_OBJS = []


def tint(r=1, g=1, b=1, j=0.08):
    k = 1 + rng.uniform(-j, j)
    return (r * k * rng.uniform(0.97, 1.03), g * k * rng.uniform(0.97, 1.03), b * k * rng.uniform(0.96, 1.04))


def wall_pieces(u0, u1, z0, z1, ops):
    out = []
    cur = u0
    for (a, b, c, d) in sorted(ops):
        if a > cur: out.append((cur, a, z0, z1))
        if c > z0: out.append((a, b, z0, c))
        if d < z1: out.append((a, b, d, z1))
        cur = b
    if cur < u1: out.append((cur, u1, z0, z1))
    return out


# openings in each exterior frame's u coordinate  (u0,u1,z0,z1)
def win(uc, zc, w, h): return (uc - w / 2, uc + w / 2, zc - h / 2, zc + h / 2)


OPS = {
    'front': [(-0.5, 0.5, 0.38, 2.43), win(-2.9, 2.05, 1.0, 1.25), win(2.9, 2.05, 1.0, 1.25)],
    'back': [win(2.2, 2.05, 1.0, 1.25), win(-2.2, 2.05, 1.0, 1.25)],
    'right': [win(-0.9, 2.05, 0.9, 1.1), win(1.6, 2.05, 0.9, 1.1)],
    'left': [],
}
FIRE_HOLE = (-0.6, 0.6, 0.40, 1.40)
WALLS = {'front': (FRONT, G_FRONT, -4.5, 4.5, 4.25), 'back': (BACK, G_BACK, -4.5, 4.5, 4.25),
         'right': (RIGHT, G_RIGHT, -3.27, 3.27, 3.25), 'left': (LEFT, G_LEFT, -3.27, 3.27, 3.25)}


# ------------------------------------------------------------------ foundation
def foundation():
    box('mortar', -4.54, 4.54, -3.54, 3.54, -0.6, 0.262)
    pal = [(1, 1, 1), (0.88, 0.86, 0.8), (1.06, 1.0, 0.94), (0.78, 0.76, 0.72), (1.0, 0.93, 0.84), (0.93, 0.95, 0.92)]
    for F, (a, b) in ((FRONT, (-4.62, 4.62)), (BACK, (-4.62, 4.62)), (RIGHT, (-3.44, 3.44)), (LEFT, (-3.44, 3.44))):
        masonry(F, 'stone_foundation', a, b, -0.45, 0.30, -0.08, 0.10, pal=pal, hs=(0.17, 0.25), ws=(0.3, 0.62), gap=0.016, m=1, k=0.6, noise=0.09, rough=0.02)


# ------------------------------------------------------------------ walls (exterior shell)
def siding(F, u0, u1, z0, z1, holes=(), rangefn=None, mat='siding_wood'):
    h, pitch = 0.16, 0.14
    nrows = int((z1 - z0 - 0.02) / pitch) + 1
    for r in range(nrows):
        zb = z0 + r * pitch
        zt = min(zb + h, z1)
        if zt - zb < 0.04: break
        a, b = rangefn(zb, zt) if rangefn else (u0, u1)
        if b - a < 0.05: continue
        for (p, q) in free_intervals(a, b, zb, zt, holes):
            u = p
            for w in split_widths(q - p, 1.1, 2.4):
                # half of rows: first board shortened to stagger butt joints
                pts = [(-0.03, zb), (0.0, zb), (0.0, zb + 0.012), (-0.022, zt), (-0.03, zt)]
                c = tint(1, 1, 1, 0.16)
                F.prism(mat, pts, u, u + w - 0.0025, col=c, cj=0.05)
                u += w


def walls():
    for name, (F, G, u0, u1, gi) in WALLS.items():
        ops = list(OPS[name])
        cops = ops + ([FIRE_HOLE] if name == 'left' else [])
        for (a, b, c, d) in wall_pieces(u0, u1, 0.262, ZE, cops):
            F.box('plaster_wall', a, b, -0.23, -0.03, c, d, sub=0.45, cj=0.035, freq=1.4)
        cu0, cu1 = (-4.36, 4.36) if name in ('front', 'back') else (-3.36, 3.36)
        siding(F, cu0, cu1, Z0, ZE, ops)
    # corner posts
    for sx in (-1, 1):
        for sy in (-1, 1):
            x0, x1 = (4.33, 4.53) if sx > 0 else (-4.53, -4.33)
            y0, y1 = (3.33, 3.53) if sy > 0 else (-3.53, -3.33)
            box('timber_dark', x0, x1, y0, y1, Z0, ZE + 0.08, n=(1, 1, 6), cj=0.1, freq=1.0)
    # gable triangles (closed) with lap siding
    for sx in (-1, 1):
        F = RIGHT if sx > 0 else LEFT
        xa, xb = (4.27, 4.47) if sx > 0 else (-4.47, -4.27)
        prism('plaster_wall', [(-3.5, ZE), (3.5, ZE), (0, 5.2)], (xa, 0, 0), V3((0, 1, 0)), V3((0, 0, 1)), V3((1, 0, 0)), xb - xa)
        siding(F, -3.4, 3.4, ZE, 5.2, (), rangefn=lambda zb, zt: (-((5.2 - (zb + zt) / 2) / K - 0.06), (5.2 - (zb + zt) / 2) / K - 0.06))
    # under-eave top plate wedges
    for sy in (-1, 1):
        prism('roof_deck', [(sy * 3.5, ZE), (sy * 3.25, ZE), (sy * 3.25, 5.2 - K * 3.25)], (-4.5, 0, 0), V3((0, 1, 0)), V3((0, 0, 1)), V3((1, 0, 0)), 9.0)


# ------------------------------------------------------------------ roof
def shingles(xa, xb, Ey, Ez, d, nn, slen, exp=0.14, Ls=0.34, wr=(0.17, 0.3), mat='roof_shingle'):
    p = -0.045
    ci = 0
    E = V3((0, Ey, Ez))
    while p < slen - 0.04:
        x = xa - rng.uniform(0.0, wr[1])
        rowk = rng.uniform(0.95, 1.05)
        while x < xb:
            w = rng.uniform(*wr)
            x0 = max(x, xa); x1 = min(x + w - 0.006, xb)
            x += w
            if x1 - x0 < 0.04: continue
            pj = p + rng.uniform(-0.007, 0.007)
            p1 = min(pj + Ls, slen + 0.05)
            b0 = 0.004
            tb = rng.uniform(0.017, 0.024)
            th = 0.004

            def Pt(xx, pp, off): return E + V3((xx, 0, 0)) + d * pp + nn * off

            pts = [Pt(x0, pj, b0), Pt(x1, pj, b0), Pt(x1, p1, b0), Pt(x0, p1, b0),
                   Pt(x0, pj, b0 + tb), Pt(x1, pj, b0 + tb), Pt(x1, p1, b0 + th), Pt(x0, p1, b0 + th)]
            k = rowk * (1 + rng.uniform(-0.18, 0.18))
            c = (k * rng.uniform(0.92, 1.06), k * rng.uniform(0.9, 1.04), k * rng.uniform(0.85, 1.05))
            fs = hexa(mat, pts, c, 0.0, skip=('bottom', 'b', 'l', 'r'))
            # darker towards the head (shadowed by the course above)
            cl = hs_lib._CURBM[0].loops.layers.float_color['Col']
            for f in fs:
                for l in f.loops:
                    t = (l.vert.co - (E + V3((x0, 0, 0)) + d * pj)).dot(d) / max(Ls, 1e-3)
                    g = 1.0 - 0.28 * max(0.0, min(1.0, t))
                    cc = l[cl]
                    l[cl] = (cc[0] * g, cc[1] * g, cc[2] * g, 1.0)
        p += exp
        ci += 1


def roof():
    al = math.atan(K)
    ca, sa = math.cos(al), math.sin(al)
    for s in (-1, 1):
        prism('roof_deck', [(0, 5.2), (s * 3.95, 5.2 - K * 3.95), (s * 3.95, 5.3 - K * 3.95), (0, 5.3)], (-4.9, 0, 0),
              V3((0, 1, 0)), V3((0, 0, 1)), V3((1, 0, 0)), 9.8)
        Ey, Ez = s * 3.95, 5.3 - K * 3.95
        d = V3((0, -s * ca, sa)); nn = V3((0, s * sa, ca))
        shingles(-4.9, 4.9, Ey, Ez, d, nn, 3.95 / ca)
        # fascia + barge boards
        E = V3((0, Ey, Ez))
        obox('trim_paint', E + d * (-0.03) + nn * (-0.16) + V3((-4.93, 0, 0)), V3((1, 0, 0)), d, nn, 9.86, 0.03, 0.23)
        for sx in (-1, 1):
            x = 4.9 if sx > 0 else -4.93
            obox('trim_paint', E + d * (-0.03) + nn * (-0.15) + V3((x, 0, 0)), V3((1, 0, 0)), d, nn, 0.03, 3.95 / ca + 0.06, 0.21)
        # rafter tails
        x = -4.3
        while x < 4.4:
            if not (s < 0 and abs(x) < 2.55):
                obox('timber_dark', E + d * 0.0 + nn * (-0.225) + V3((x - 0.04, 0, 0)), V3((1, 0, 0)), d, nn, 0.08, 0.52, 0.12, cj=0.06)
            x += 0.6
    # ridge cap
    zs = 5.3 - K * 0.3 + 0.042
    prism('timber_dark', [(-0.3, zs - 0.012), (0.3, zs - 0.012), (0.3, zs + 0.02), (0, 5.405), (-0.3, zs + 0.02)], (-4.94, 0, 0), V3((0, 1, 0)), V3((0, 0, 1)), V3((1, 0, 0)), 9.88)
    # gable trim: little brackets at apex
    for sx in (-1, 1):
        x = 4.905 if sx > 0 else -4.935
        box('trim_paint', x, x + 0.03, -0.14, 0.14, 5.2, 5.43)


# ------------------------------------------------------------------ chimney (exterior)
def chimney():
    pal = [(1, 1, 1), (0.9, 0.87, 0.8), (1.06, 1.02, 0.95), (0.8, 0.78, 0.74), (1.0, 0.92, 0.82)]
    M = 'stone_chimney'
    TOP = 7.0
    # core
    box('mortar', -5.0, -4.45, -0.72, 0.72, -0.6, TOP)
    box('mortar', -5.22, -4.45, -0.92, 0.92, -0.6, 1.0)
    # base (wider, weathered) faces
    masonry(LEFT, M, -0.93, 0.93, -0.45, 0.95, 0.45, 0.72, pal=pal, hs=(0.2, 0.28), ws=(0.3, 0.6), m=2, k=0.6, rough=0.03)
    FS_R = Fr((0, 0.93, 0), (-1, 0, 0), (0, 1, 0))
    FS_L = Fr((0, -0.93, 0), (-1, 0, 0), (0, -1, 0))
    for F in (FS_R, FS_L):
        masonry(F, M, 4.5, 5.22, -0.45, 0.95, -0.2, 0.0, pal=pal, hs=(0.2, 0.28), ws=(0.3, 0.55), m=2, k=0.6)
    # shoulder slab
    box(M, -5.27, -4.5, -0.97, 0.97, 0.95, 1.04, n=(3, 4, 1), cj=0.08)
    # shaft
    masonry(LEFT, M, -0.75, 0.75, 1.04, TOP, 0.3, 0.52, pal=pal, hs=(0.13, 0.3), ws=(0.2, 0.62), m=1, k=0.6, rough=0.025, noise=0.12)
    FS2R = Fr((0, 0.75, 0), (-1, 0, 0), (0, 1, 0))
    FS2L = Fr((0, -0.75, 0), (-1, 0, 0), (0, -1, 0))
    for F in (FS2R, FS2L):
        masonry(F, M, 4.5, 5.03, 1.04, TOP, -0.2, 0.0, pal=pal, hs=(0.13, 0.3), ws=(0.2, 0.55), m=1, k=0.6, noise=0.12)
    # corbelled cap
    box(M, -5.1, -4.5, -0.82, 0.82, TOP, TOP + 0.09, n=(3, 4, 1), cj=0.06)
    box(M, -5.14, -4.46, -0.86, 0.86, TOP + 0.09, TOP + 0.17, n=(3, 4, 1), cj=0.06)
    # flue opening ring
    for (x0, x1, y0, y1) in ((-5.14, -4.46, -0.86, -0.46), (-5.14, -4.46, 0.46, 0.86), (-5.14, -4.92, -0.46, 0.46), (-4.68, -4.46, -0.46, 0.46)):
        box(M, x0, x1, y0, y1, TOP + 0.17, TOP + 0.3, cj=0.06)
    box('soot', -4.92, -4.68, -0.46, 0.46, TOP + 0.1, TOP + 0.28)
    # lead flashing band where it meets gable roof eaves
    # (simple raised collar)


# ------------------------------------------------------------------ interior finishes
def wainscot(G, u0, u1, holes=()):
    nrows = 6
    hh = (1.10 - Z0) / nrows
    for r in range(nrows):
        zb = Z0 + r * hh
        zt = zb + hh
        pts = [(-0.02, zb), (-0.0045, zb), (0.0, zb + 0.006), (0.0, zt - 0.006), (-0.0045, zt), (-0.02, zt)]
        for (p, q) in free_intervals(u0, u1, zb, zt, holes):
            u = p
            for w in split_widths(q - p, 1.4, 2.8):
                c = tint(1, 1, 1, 0.12)
                G.prism('wainscot', pts, u, u + w - 0.002, col=c, cj=0.05)
                u += w
    # baseboard & chair rail
    for (p, q) in free_intervals(u0, u1, Z0, Z0 + 0.14, holes):
        G.box('trim_paint', p, q, 0.0, 0.024, Z0, Z0 + 0.13)
        G.box('trim_paint', p, q, 0.0, 0.03, Z0 + 0.13, Z0 + 0.142)
    for (p, q) in free_intervals(u0, u1, 1.10, 1.16, holes):
        G.prism('trim_paint', [(-0.02, 1.10), (0.04, 1.10), (0.04, 1.125), (0.025, 1.16), (-0.02, 1.16)], p, q)


def casing(F, a, b, zb, zt, wd=0.085, th=0.022, sill=False, base_from_floor=False, col=(1, 1, 1)):
    F.box('trim_paint', a - wd, a, 0, th, zb, zt)
    F.box('trim_paint', b, b + wd, 0, th, zb, zt)
    F.box('trim_paint', a - wd, b + wd, 0, th, zt, zt + wd)
    F.box('trim_paint', a - wd - 0.02, b + wd + 0.02, 0, th + 0.012, zt + wd, zt + wd + 0.025)   # head cap


def interior():
    # floor
    box('mortar', -4.26, 4.26, -3.26, 3.26, 0.255, 0.27)
    for (xa, xb) in ((-4.26, 1.4), (1.65, 4.26)):
        x = xa
        while x < xb - 0.02:
            w = min(rng.uniform(0.15, 0.23), xb - x)
            if xb - x - w < 0.1: w = xb - x
            c = tint(1, 1, 1, 0.16)
            wear = rng.uniform(0.9, 1.1)
            # run boards along Y in two pieces (butt joint)
            cut = rng.uniform(-1.8, 1.8)
            for (y0, y1) in ((-3.26, cut), (cut, 3.26)):
                box('floor_planks', x + 0.002, x + w - 0.002, y0 + 0.001, y1 - 0.001, 0.27, 0.30, col=c, n=(1, 3, 1), cj=0.09, freq=2.2, seed=x * 3.1, skip=('bottom',))
                for yy in [y0 + 0.08 + 1.8 * i for i in range(0, 4) if y0 + 0.08 + 1.8 * i < y1 - 0.05]:
                    nailhead('iron', x + 0.03, yy, 0.30)
                    nailhead('iron', x + w - 0.03, yy, 0.30)
            x += w
    # wall finishes
    for name, (F, G, u0, u1, gi) in WALLS.items():
        ops = list(OPS[name])
        holes = [(a, b, c, d) for (a, b, c, d) in ops if c < 1.2]
        if name == 'left':
            holes.append((-0.6, 0.6, Z0, 1.4))
        wainscot(G, -gi, gi, holes)
        # linings + casings
        for (a, b, c, d) in ops:
            door = (name == 'front' and c < 0.5)
            zb = 0.30 if door else c
            G.box('trim_paint', a, a + 0.02, -0.25, 0, c, d)
            G.box('trim_paint', b - 0.02, b, -0.25, 0, c, d)
            G.box('trim_paint', a, b, -0.25, 0, d - 0.02, d)
            if not door:
                G.box('trim_paint', a, b, -0.25, 0, c, c + 0.02)
                casing(G, a, b, c, d)
                # stool + apron
                G.box('trim_paint', a - 0.11, b + 0.11, 0.0, 0.075, c - 0.002, c + 0.03)
                G.box('trim_paint', a - 0.05, b + 0.05, 0.0, 0.024, c - 0.085, c - 0.002)
            else:
                casing(G, a, b, 0.30, d)
    # partition
    pholes = [(-0.875, 0.075, 0.26, 2.30)]
    for (a, b, c, d) in wall_pieces(-3.27, 3.27, 0.262, 3.15, pholes):
        PB.box('plaster_wall', a, b, -0.23, -0.02, c, d, sub=0.45, cj=0.035, freq=1.4)
    for F in (PB, PL):
        ph = [(-0.875, 0.075, 0.30, 2.30)]
        wainscot(F, -3.25, 3.25, ph)
        a, b, c, d = -0.875, 0.075, 0.30, 2.30
        F.box('trim_paint', a, a + 0.02, -0.25, 0, c, d)
        F.box('trim_paint', b - 0.02, b, -0.25, 0, c, d)
        F.box('trim_paint', a, b, -0.25, 0, d - 0.02, d)
        casing(F, a, b, 0.30, d)
    # doorway threshold
    PB.box('door_wood', -0.875, 0.075, -0.25, 0, 0.27, 0.305)
    # front door threshold + casings
    FRONT.box('door_wood', -0.5, 0.5, -0.25, 0.14, 0.262, 0.37, sub=None)
    casing(FRONT, -0.5, 0.5, 0.30, 2.43, wd=0.11, th=0.028)
    for (a, b) in ((-0.5, -0.48), (0.48, 0.5)):
        FRONT.box('trim_paint', a, b, -0.25, 0, 0.37, 2.43)
    FRONT.box('trim_paint', -0.5, 0.5, -0.25, 0, 2.41, 2.43)
    # interior crown / cove at ceiling
    for name, (F, G, u0, u1, gi) in WALLS.items():
        G.prism('trim_paint', [(0, 3.15), (0.06, 3.15), (0, 3.08)], -gi, gi)
    # ceiling beams handled in ceiling()


# ------------------------------------------------------------------ fireplace
FL = Fr((-4.25, 0, 0), (0, 1, 0), (1, 0, 0))   # u = +y, n = into the room (+x)


def fireplace():
    pal = [(1, 1, 1), (0.9, 0.87, 0.8), (1.06, 1.02, 0.95), (0.82, 0.8, 0.76), (1.0, 0.92, 0.82)]
    M = 'stone_fireplace'
    # hearth: flagstones
    y = -1.15
    rows = [(0.0, 0.25), (0.25, 0.5)]
    for (n0, n1) in rows:
        u = -1.15
        for w in split_widths(2.3, 0.45, 0.8):
            c = rng.choice(pal)
            FL.stone_at('hearth_stone', u + w / 2, (n0 + n1) / 2 + (0.0 if n1 < 0.5 else 0.0), 0.375, w - 0.012, (n1 - n0) - 0.012 + (0.02 if n1 >= 0.5 else 0), 0.15, col=c, m=1, k=0.7, noise=0.03, cj=0.06)
            u += w
    # breast core (mortar) w/ opening
    FL.box('mortar', -1.1, -0.55, 0, 0.44, 0.44, 1.5)
    FL.box('mortar', 0.55, 1.1, 0, 0.44, 0.44, 1.5)
    FL.box('mortar', -1.1, 1.1, 0, 0.44, 1.35, 1.5)
    # stone facing on the front plane and sides
    masonry(FL, M, -1.1, 1.1, 0.45, 1.5, 0.30, 0.46, holes=[(-0.55, 0.55, 0.44, 1.36)], pal=pal, hs=(0.12, 0.2), ws=(0.17, 0.36), m=2, k=0.6, gap=0.014, rough=0.02, noise=0.12)
    SR = Fr((-4.25, 1.1, 0), (1, 0, 0), (0, 1, 0))
    SL = Fr((-4.25, -1.1, 0), (1, 0, 0), (0, -1, 0))
    for F in (SR, SL):
        masonry(F, M, 0.0, 0.46, 0.45, 1.5, -0.12, 0.0, pal=pal, hs=(0.12, 0.2), ws=(0.17, 0.36), m=1, k=0.6, noise=0.12)
    # lintel beam + mantel shelf + corbels
    FL.box('timber_beam', -0.72, 0.72, 0.32, 0.52, 1.33, 1.46, n=(1, 1, 1), cj=0.1)
    FL.box('timber_beam', -1.25, 1.25, 0.0, 0.66, 1.50, 1.60, n=(8, 1, 1), cj=0.12, freq=1.2,
           post=lambda v, i, j, k: setattr(v, 'co', v.co + V3((0, 0, 0.003 * math.sin(v.co.y * 9)))))
    for su in (-1, 1):
        FL.box('timber_beam', su * 1.12 - 0.06, su * 1.12 + 0.06, 0.40, 0.62, 1.30, 1.50)
    # plaster chimney breast up to ceiling (tapered)
    FL.prism('plaster_wall', [(0, 1.6), (0.34, 1.6), (0.34, 2.0), (0.22, 3.15), (0, 3.15)], -0.95, 0.95)
    for su in (-1, 1):
        # tapered side returns
        bm = B('plaster_wall'); setbm(bm)
    
    # firebox lining (sooty)
    FL.box('soot', -0.6, 0.6, -0.225, -0.2, 0.40, 1.40)          # back
    FL.box('soot', -0.6, 0.6, -0.225, 0.46, 0.40, 0.45)          # floor
    FL.box('soot', -0.6, -0.54, -0.225, 0.46, 0.40, 1.40)        # left side
    FL.box('soot', 0.54, 0.6, -0.225, 0.46, 0.40, 1.40)
    FL.box('soot', -0.6, 0.6, -0.225, 0.46, 1.34, 1.40)          # top
    # sooty streak above opening (on lintel beam face handled by colour)
    # fire bed, logs, andirons  -> separate part
    with part() as FD:
        FL.box('fire_embers', -0.42, 0.42, -0.12, 0.34, 0.45, 0.50, n=(6, 3, 1), cj=0.45, freq=5.0,
               post=lambda v, i, j, k: setattr(v, 'co', v.co + V3((0, 0, 0.012 * nz3(v.co, 14)))))
        logs = [(-0.12, 0.05, 0.575, 0.0, 0.065), (0.12, 0.03, 0.56, 0.0, 0.06), (0.0, 0.03, 0.66, 0.0, 0.055)]
        for (u, n0, z, _, r) in logs:
            p0 = FL.P(u, 0.36 if z < 0.6 else 0.30, z)
            p1 = FL.P(u, -0.12, z)
            cyl('charred_wood', p0, p1, r, segs=8, col=(1, 1, 1), cj=0.25, jit=0.25)
        for su in (-1, 1):
            FL.box('iron', su * 0.45 - 0.02, su * 0.45 + 0.02, -0.1, 0.32, 0.50, 0.53)
            FL.box('iron', su * 0.45 - 0.02, su * 0.45 + 0.02, 0.30, 0.34, 0.45, 0.80)
    EXTRA_OBJS.append(make_part('fire_embers', FD, ['fire_embers', 'charred_wood', 'iron']))


# ------------------------------------------------------------------ ceiling
def ceiling():
    box('timber_dark', -4.27, 4.27, -3.27, 3.27, 3.175, 3.2)
    y = -3.25
    while y < 3.25 - 0.02:
        w = min(rng.uniform(0.15, 0.2), 3.25 - y)
        if 3.25 - y - w < 0.1: w = 3.25 - y
        c = tint(1, 1, 1, 0.12)
        cut = rng.uniform(-1.5, 1.5)
        for (x0, x1) in ((-4.26, cut), (cut, 4.26)):
            box('ceiling_planks', x0 + 0.001, x1 - 0.001, y + 0.002, y + w - 0.002, 3.15, 3.175, col=c, n=(3, 1, 1), cj=0.08, freq=2.0, seed=y * 4, skip=('top',))
        y += w

    def hewn(v, i, j, k):
        if k == 0:
            v.co.x += 0.008 * nz3(v.co, 5.0)
            v.co.z += 0.006 * nz3(v.co, 6.0, 3.0)
        elif i in (0, 1):
            v.co.x += 0.004 * nz3(v.co, 4.0, 7.0)

    for x in (-3.85, -2.75, -1.65, -0.55, 0.55, 2.75, 3.85):
        box('timber_beam', x - 0.075, x + 0.075, -3.26, 3.26, 2.96, 3.15, n=(1, 26, 1), cj=0.12, freq=1.6, seed=x, post=hewn)
        # corbel brackets at walls
    box('timber_beam', -4.26, 4.26, -0.10, 0.10, 2.93, 3.15, n=(40, 1, 1), cj=0.14, freq=1.3, post=lambda v, i, j, k: (setattr(v.co, 'y', v.co.y + 0.006 * nz3(v.co, 4.0)) if k == 0 else None))


# ------------------------------------------------------------------ windows
def window(F, uc, zc, w, h):
    a, b = uc - w / 2, uc + w / 2
    c, d = zc - h / 2, zc + h / 2
    ia, ib, ic, id_ = a + 0.02, b - 0.02, c + 0.02, d - 0.02
    mid = (ia + ib) / 2
    n0, n1 = -0.17, -0.12
    for (sa, sb) in ((ia, mid), (mid, ib)):
        st = 0.04
        F.box('trim_paint', sa, sa + st, n0, n1, ic, id_)
        F.box('trim_paint', sb - st, sb, n0, n1, ic, id_)
        F.box('trim_paint', sa + st, sb - st, n0, n1, ic, ic + 0.05)
        F.box('trim_paint', sa + st, sb - st, n0, n1, id_ - 0.045, id_)
        F.box('trim_paint', (sa + sb) / 2 - 0.009, (sa + sb) / 2 + 0.009, n0 + 0.012, n1 - 0.012, ic, id_)
    for t in (1 / 3, 2 / 3):
        zz = ic + (id_ - ic) * t
        F.box('trim_paint', ia, ib, n0 + 0.012, n1 - 0.012, zz - 0.009, zz + 0.009)
    # brass latch
    F.box('brass', mid - 0.03, mid + 0.03, n1, n1 + 0.012, zc - 0.02, zc + 0.02)
    GLASS_OPS.append(lambda F=F, ia=ia, ib=ib, ic=ic, id_=id_: F.box('glass', ia + 0.035, ib - 0.035, -0.153, -0.147, ic + 0.035, id_ - 0.035))
    # exterior casing, drip cap, sill, apron
    casing(F, a, b, c, d, wd=0.09, th=0.024)
    F.prism('trim_paint', [(-0.03, c - 0.05), (0.11, c - 0.05), (0.11, c - 0.035), (0.0, c + 0.005), (-0.03, c + 0.005)], a - 0.08, b + 0.08)
    F.box('trim_paint', a - 0.02, b + 0.02, 0, 0.024, c - 0.11, c - 0.05)


def shutter(name, F, hinge_u, dirn, z0, z1, wid=0.57):
    ua, ub = sorted((hinge_u, hinge_u + dirn * wid))
    zm = (z0 + z1) / 2
    with part() as D:
        st = 0.065
        P = 'paint_shutter'
        F.box(P, ua, ua + st, 0.0, 0.03, z0, z1)
        F.box(P, ub - st, ub, 0.0, 0.03, z0, z1)
        F.box(P, ua + st, ub - st, 0.0, 0.03, z0, z0 + 0.085)
        F.box(P, ua + st, ub - st, 0.0, 0.03, z1 - 0.085, z1)
        F.box(P, ua + st, ub - st, 0.0, 0.03, zm - 0.04, zm + 0.04)
        for (f0, f1) in ((z0 + 0.085, zm - 0.04), (zm + 0.04, z1 - 0.085)):
            nL = int((f1 - f0) / 0.05)
            for i in range(nL):
                zb = f0 + i * (f1 - f0) / nL
                F.prism(P, [(0.004, zb), (0.028, zb + 0.03), (0.028, zb + 0.043), (0.004, zb + 0.013)], ua + st - 0.003, ub - st + 0.003, col=tint(1, 1, 1, 0.05))
        he = hinge_u
        for zz in (z0 + 0.2, z1 - 0.2):
            uu0, uu1 = (he, he + dirn * 0.3)
            F.box('iron', min(uu0, uu1), max(uu0, uu1), 0.03, 0.036, zz - 0.022, zz + 0.022)
            cyl('iron', F.P(he, 0.015, zz - 0.06), F.P(he, 0.015, zz + 0.06), 0.01, segs=6)
    return make_part(name, D, ['paint_shutter', 'iron'], pivot=F.P(hinge_u, 0.015, zm), bevel=0.003)


def flowerbox(F, uc, c):
    z1 = c - 0.17; z0 = z1 - 0.22
    u0, u1 = uc - 0.56, uc + 0.56
    n0, n1 = 0.035, 0.26
    P = 'paint_shutter'
    F.box(P, u0, u1, n1 - 0.02, n1, z0, z1, cj=0.03)
    F.box(P, u0, u1, n0, n0 + 0.02, z0, z1)
    F.box(P, u0, u0 + 0.02, n0, n1, z0, z1)
    F.box(P, u1 - 0.02, u1, n0, n1, z0, z1)
    F.box(P, u0, u1, n0, n1, z0, z0 + 0.02)
    F.box('soil', u0 + 0.02, u1 - 0.02, n0 + 0.02, n1 - 0.02, z0 + 0.02, z1 - 0.045, n=(10, 1, 3) if abs(F.U.x) > 0 else (1, 10, 3), cj=0.15, freq=9.0,
          post=lambda v, i, j, k: setattr(v, 'co', v.co + V3((0, 0, 0.012 * nz3(v.co, 18)))) if v.co.z > z1 - 0.06 else None)
    for su in (-0.42, 0.42):
        F.prism('iron', [(0.0, z0 - 0.16), (0.0, z0), (0.235, z0)], uc + su - 0.012, uc + su + 0.012)


def windows_all():
    FR = [(FRONT, -2.9, 2.05, 1.0, 1.25), (FRONT, 2.9, 2.05, 1.0, 1.25), (BACK, 2.2, 2.05, 1.0, 1.25), (BACK, -2.2, 2.05, 1.0, 1.25),
          (RIGHT, -0.9, 2.05, 0.9, 1.1), (RIGHT, 1.6, 2.05, 0.9, 1.1)]
    for (F, uc, zc, w, h) in FR:
        window(F, uc, zc, w, h)
    # shutters + flower boxes on the front windows (shutters rest open, flat against the wall, hinge at window side)
    for tag, uc in (('fl', -2.9), ('fr', 2.9)):
        c, d = 2.05 - 0.625, 2.05 + 0.625
        hu_in = uc + 0.5 + 0.095    # hinge on casing edge, right side
        hu_out = uc - 0.5 - 0.095
        EXTRA_OBJS.append(shutter('shutter_%s_r' % tag, FRONT, hu_in, +1, c - 0.03, d + 0.03))
        EXTRA_OBJS.append(shutter('shutter_%s_l' % tag, FRONT, hu_out, -1, c - 0.03, d + 0.03))
        flowerbox(FRONT, uc, c)
    # round attic window (right gable) and louvered vent (left gable)
    F = RIGHT
    cz = 4.25; R = 0.27
    for i in range(18):
        a0 = 2 * math.pi * i / 18; a1 = 2 * math.pi * (i + 1) / 18
        ctr = F.P(0, -0.02, cz)
        pA = F.P(R * math.cos(a0), -0.02, cz + R * math.sin(a0)); pB = F.P(R * math.cos(a1), -0.02, cz + R * math.sin(a1))
        t = pB - pA
        rh = (pA + pB) / 2 - ctr
        rh.normalize()
        obox('trim_paint', pA - rh * 0.035, t, F.N, rh, t.length * 1.03, 0.05, 0.07)
    cyl('soot', F.P(0, -0.08, cz), F.P(0, -0.03, cz), R - 0.02, segs=24)
    GLASS_OPS.append(lambda: cyl('glass', F.P(0, -0.0, cz), F.P(0, 0.005, cz), R - 0.0, segs=24))
    F.box('trim_paint', -R, R, -0.01, 0.03, cz - 0.012, cz + 0.012)
    F.box('trim_paint', -0.012, 0.012, -0.01, 0.03, cz - R, cz + R)
    # vent
    F = LEFT
    vu, vz = -1.7, 3.95   # u = -y  => y = +1.7
    F.box('soot', vu - 0.25, vu + 0.25, -0.04, 0.0, vz - 0.18, vz + 0.18)
    for zz in [vz - 0.17 + 0.045 * i for i in range(8)]:
        F.prism('trim_paint', [(-0.01, zz), (0.03, zz + 0.03), (0.03, zz + 0.042), (-0.01, zz + 0.012)], vu - 0.25, vu + 0.25)
    F.box('trim_paint', vu - 0.29, vu - 0.25, 0, 0.035, vz - 0.22, vz + 0.22)
    F.box('trim_paint', vu + 0.25, vu + 0.29, 0, 0.035, vz - 0.22, vz + 0.22)
    F.box('trim_paint', vu - 0.29, vu + 0.29, 0, 0.035, vz - 0.22, vz - 0.18)
    F.box('trim_paint', vu - 0.29, vu + 0.29, 0, 0.035, vz + 0.18, vz + 0.22)


# ------------------------------------------------------------------ doors
def door_front():
    F = FRONT
    with part() as D:
        nb0, nb1 = -0.165, -0.115
        for i in range(8):
            ua = -0.48 + 0.12 * i
            ub = ua + 0.12 - 0.003
            c = tint(1, 1, 1, 0.07)
            if i in (3, 4):
                F.box('door_paint', ua, ub, nb0, nb1, 0.38, 1.55, col=c, cj=0.04, n=(1, 1, 3))
                F.box('door_paint', ua, ub, nb0, nb1, 1.95, 2.41, col=c, cj=0.04)
            else:
                F.box('door_paint', ua, ub, nb0, nb1, 0.38, 2.41, col=c, cj=0.04, n=(1, 1, 6))
        # pane frame + muntins
        for (u0, u1, z0, z1) in ((-0.15, -0.12, 1.52, 1.98), (0.12, 0.15, 1.52, 1.98), (-0.12, 0.12, 1.52, 1.55), (-0.12, 0.12, 1.95, 1.98)):
            F.box('door_wood', u0, u1, -0.175, -0.105, z0, z1)
        F.box('door_wood', -0.12, -0.005, -0.15, -0.13, 1.745, 1.755)
        F.box('door_wood', 0.005, 0.12, -0.15, -0.13, 1.745, 1.755)
        F.box('door_wood', -0.005, 0.005, -0.15, -0.13, 1.55, 1.745)
        F.box('door_wood', -0.005, 0.005, -0.15, -0.13, 1.755, 1.95)
        F.box('glass', -0.12, 0.12, -0.143, -0.137, 1.55, 1.95)
        # inside battens + brace
        F.box('door_wood', -0.48, 0.48, -0.197, -0.165, 0.55, 0.69)
        F.box('door_wood', -0.48, 0.48, -0.197, -0.165, 2.12, 2.26)
        a = F.P(-0.44, -0.197, 0.62); bpt = F.P(0.44, -0.197, 2.19)
        dv = bpt - a
        perp = dv.cross(F.N).normalized()
        obox('door_wood', a - perp * 0.05 + F.N * (-0.004), dv, F.N, perp, dv.length, 0.036, 0.10)
        # hardware outside
        for zz in (0.62, 1.40, 2.18):
            F.box('brass', -0.49, -0.12, -0.115, -0.108, zz - 0.028, zz + 0.028)
            cyl('brass', F.P(-0.497, -0.14, zz - 0.055), F.P(-0.497, -0.14, zz + 0.055), 0.014, segs=8)
            cyl('brass', F.P(-0.15, -0.108, zz), F.P(-0.15, -0.100, zz), 0.011, segs=8)
        F.box('brass', 0.32, 0.40, -0.115, -0.108, 0.93, 1.17)
        cyl('brass', F.P(0.36, -0.108, 1.05), F.P(0.36, -0.07, 1.05), 0.011, segs=8)
        cyl('brass', F.P(0.36, -0.07, 1.05), F.P(0.20, -0.07, 1.05), 0.009, segs=8)
        F.box('brass', 0.31, 0.41, -0.115, -0.106, 0.74, 0.88)
        F.box('iron', 0.355, 0.365, -0.106, -0.103, 0.785, 0.835)
        # inside
        F.box('brass', 0.32, 0.40, -0.172, -0.165, 0.93, 1.17)
        cyl('brass', F.P(0.36, -0.172, 1.05), F.P(0.36, -0.205, 1.05), 0.011, segs=8)
        cyl('brass', F.P(0.36, -0.205, 1.05), F.P(0.22, -0.205, 1.05), 0.009, segs=8)
        F.box('iron', 0.3, 0.42, -0.2, -0.197, 0.72, 0.9)
    return make_part('door_front', D, ['door_paint', 'door_wood', 'brass', 'iron', 'glass'], pivot=F.P(-0.497, -0.14, 1.405), bevel=0.0035)


def door_bedroom():
    F = PB
    with part() as D:
        n0, n1 = -0.145, -0.105
        z0, z1 = 0.32, 2.28
        ua, ub = -0.855, 0.053
        P = 'door_wood'
        F.box(P, ua, ua + 0.1, n0, n1, z0, z1, cj=0.05)
        F.box(P, ub - 0.1, ub, n0, n1, z0, z1, cj=0.05)
        um = (ua + ub) / 2
        F.box(P, um - 0.05, um + 0.05, n0, n1, z0, z1)
        for (ra, rb) in ((ua + 0.1, um - 0.05), (um + 0.05, ub - 0.1)):
            F.box(P, ra, rb, n0, n1, z1 - 0.1, z1)
            F.box(P, ra, rb, n0, n1, 1.03, 1.16)
            F.box(P, ra, rb, n0, n1, z0, z0 + 0.16)
        for (pu0, pu1) in ((ua + 0.1, um - 0.05), (um + 0.05, ub - 0.1)):
            for (pz0, pz1) in ((z0 + 0.16, 1.03), (1.16, z1 - 0.1)):
                F.box(P, pu0 - 0.004, pu1 + 0.004, -0.13, -0.12, pz0 - 0.004, pz1 + 0.004, col=(0.92, 0.92, 0.92), cj=0.05)
                # bolection moulding frame
                F.box(P, pu0, pu1, -0.12, -0.105, pz0, pz0 + 0.015)
                F.box(P, pu0, pu1, -0.12, -0.105, pz1 - 0.015, pz1)
                F.box(P, pu0, pu0 + 0.015, -0.12, -0.105, pz0 + 0.015, pz1 - 0.015)
                F.box(P, pu1 - 0.015, pu1, -0.12, -0.105, pz0 + 0.015, pz1 - 0.015)
        for zz in (0.5, 1.3, 2.05):
            cyl('brass', F.P(0.057, -0.125, zz - 0.05), F.P(0.057, -0.125, zz + 0.05), 0.009, segs=8)
            F.box('brass', 0.0, 0.055, -0.105, -0.099, zz - 0.04, zz + 0.04)
        for (nn_, sg) in ((-0.105, 1), (-0.145, -1)):
            F.box('brass', -0.80, -0.74, nn_ if sg > 0 else nn_ - 0.007, nn_ + 0.007 if sg > 0 else nn_, 0.97, 1.13)
            cyl('brass', F.P(-0.77, nn_, 1.05), F.P(-0.77, nn_ + sg * 0.035, 1.05), 0.010, segs=8)
            cyl('brass', F.P(-0.77, nn_ + sg * 0.035, 1.05), F.P(-0.63, nn_ + sg * 0.035, 1.05), 0.008, segs=8)
    return make_part('door_bedroom', D, ['door_wood', 'brass'], pivot=F.P(0.057, -0.125, 1.30), bevel=0.003)


def doors_all():
    EXTRA_OBJS.append(door_front())
    EXTRA_OBJS.append(door_bedroom())


# ------------------------------------------------------------------ porch
def porch_post(x, y, ztop, plinth=0.12):
    z0 = 0.52
    box('trim_paint', x - 0.075, x + 0.075, y - 0.075, y + 0.075, z0, z0 + plinth)
    box('trim_paint', x - 0.062, x + 0.062, y - 0.062, y + 0.062, z0 + plinth, z0 + plinth + 0.05)
    H = ztop - 0.1 - (z0 + plinth + 0.05)
    prof = [(0.0, 0.048), (0.03 * H, 0.052), (0.05 * H, 0.038), (0.30 * H, 0.04), (0.36 * H, 0.056), (0.42 * H, 0.04),
            (0.84 * H, 0.04), (0.9 * H, 0.054), (0.94 * H, 0.04), (1.0 * H, 0.05)]
    lathe('trim_paint', (x, y, z0 + plinth + 0.05), prof, segs=14)
    box('trim_paint', x - 0.07, x + 0.07, y - 0.07, y + 0.07, ztop - 0.1, ztop)


def porch():
    # deck boards along X
    y = -5.8
    yb = -3.5
    i = 0
    while y < yb - 0.01:
        w = min(0.138, yb - y)
        c = tint(1, 1, 1, 0.14)
        box('deck_planks', -2.2, 2.2, y + 0.003, y + w - 0.003, 0.49, 0.52, col=c, n=(8, 1, 1), cj=0.08, freq=1.8, seed=y * 7, skip=('bottom',))
        for xx in [-2.1 + 0.55 * k for k in range(9)]:
            nailhead('iron', xx, y + 0.03, 0.52)
            nailhead('iron', xx, y + w - 0.03, 0.52)
        y += w
    # frame under deck
    for xx in [-2.15 + 0.55 * k for k in range(9)]:
        box('timber_dark', xx - 0.04, xx + 0.04, -5.8, -3.5, 0.3, 0.49)
    x = -2.26
    while x < 2.26 - 0.05:
        box('timber_dark', x, x + 0.108, -5.86, -5.81, 0.03, 0.52, col=tint(1, 1, 1, 0.14), cj=0.04)
        x += 0.12
    for sx in (-1, 1):
        yy = -5.81
        while yy < -3.55:
            x0, x1 = (2.2, 2.25) if sx > 0 else (-2.25, -2.2)
            box('timber_dark', x0, x1, yy, yy + 0.108, 0.03, 0.52, col=tint(1, 1, 1, 0.14), cj=0.04)
            yy += 0.12
    box('soot', -2.19, 2.19, -5.79, -3.5, 0.0, 0.3, skip=('bottom',))
    # steps
    def tread(x0, x1, y0, y1, top, blockbot):
        box('timber_dark', x0 + 0.02, x1 - 0.02, y0 + 0.03, y1 - 0.0, blockbot, top - 0.035)
        yy = y0 - 0.03
        ws = [(y0 - 0.03, (y0 + y1) / 2), ((y0 + y1) / 2, y1)]
        for (a, b) in ws:
            box('deck_planks', x0, x1, a + 0.003, b - 0.003, top - 0.035, top, col=tint(1, 1, 1, 0.1), n=(4, 1, 1), cj=0.06, skip=('bottom',))
    tread(-0.85, 0.85, -6.1, -5.8, 0.35, -0.05)
    tread(-0.85, 0.85, -6.4, -6.1, 0.17, -0.1)
    # posts + roof
    fr_y, rr_y = -5.75, -3.72
    porch_post(-2.1, fr_y, 2.43)
    porch_post(2.1, fr_y, 2.43)
    porch_post(-2.1, rr_y, 2.746)
    porch_post(2.1, rr_y, 2.746)
    kp = 0.155
    bp = math.atan(kp)
    cb, sb = math.cos(bp), math.sin(bp)
    # roof slab (y,z profile), top surface z = 3.0 - kp*(|y|-3.5)
    zt = lambda yy: 3.0 - kp * (abs(yy) - 3.5)
    ytip = -5.95
    prism('roof_deck', [(-3.5, zt(-3.5) - 0.1), (ytip, zt(ytip) - 0.1), (ytip, zt(ytip)), (-3.5, zt(-3.5))], (-2.3, 0, 0), V3((0, 1, 0)), V3((0, 0, 1)), V3((1, 0, 0)), 4.6)
    d = V3((0, cb, sb)); nn = V3((0, -sb, cb))
    shingles(-2.3, 2.3, ytip, zt(ytip), d, nn, (5.95 - 3.5) / cb, exp=0.135, Ls=0.3)
    E = V3((0, ytip, zt(ytip)))
    obox('trim_paint', E + d * (-0.03) + nn * (-0.13) + V3((-2.33, 0, 0)), V3((1, 0, 0)), d, nn, 4.66, 0.03, 0.20)
    for sx in (-1, 1):
        x = 2.3 if sx > 0 else -2.33
        obox('trim_paint', E + d * (-0.03) + nn * (-0.13) + V3((x, 0, 0)), V3((1, 0, 0)), d, nn, 0.03, (5.95 - 3.5) / cb + 0.06, 0.18)
    # beams
    box('timber_beam', -2.25, 2.25, -5.85, -5.65, 2.43, 2.55, n=(10, 1, 1), cj=0.12)
    box('timber_beam', -2.25, 2.25, -3.64, -3.5, 2.72, 2.92, n=(10, 1, 1), cj=0.12)
    for sx in (-1, 1):
        xc = 2.1 * sx
        # sloped side beam along the roof slope, under the slab
        O = V3((xc - 0.07, -5.85, 2.43)) 
        obox('timber_beam', O, V3((1, 0, 0)), V3((0, cb, sb)), V3((0, -sb, cb)), 0.14, 2.42, 0.12, cj=0.1)
    # railings
    z0 = 0.52
    def rail_y(x, ya, yb):
        box('trim_paint', x - 0.032, x + 0.032, ya, yb, z0 + 0.92, z0 + 0.99)
        box('trim_paint', x - 0.022, x + 0.022, ya, yb, z0 + 0.12, z0 + 0.17)
        yy = ya + 0.09
        while yy < yb - 0.05:
            box('trim_paint', x - 0.016, x + 0.016, yy - 0.016, yy + 0.016, z0 + 0.17, z0 + 0.92)
            yy += 0.115
    def rail_x(y, xa, xb):
        box('trim_paint', xa, xb, y - 0.032, y + 0.032, z0 + 0.92, z0 + 0.99)
        box('trim_paint', xa, xb, y - 0.022, y + 0.022, z0 + 0.12, z0 + 0.17)
        xx = xa + 0.09
        while xx < xb - 0.05:
            box('trim_paint', xx - 0.016, xx + 0.016, y - 0.016, y + 0.016, z0 + 0.17, z0 + 0.92)
            xx += 0.115
    for sx in (-1, 1):
        rail_y(2.1 * sx, -5.75 + 0.07, -3.72 - 0.07)
        if sx > 0: rail_x(fr_y, 0.98, 2.03)
        else: rail_x(fr_y, -2.03, -0.98)
    # bench against the wall (right of the door)
    for k in range(3):
        box('deck_planks', 0.78, 2.0, -3.93 + k * 0.135, -3.93 + (k + 1) * 0.135 - 0.006, 0.95, 0.985, col=tint(1, 1, 1, 0.1), n=(6, 1, 1), cj=0.06)
    for xx in (0.88, 1.9):
        box('timber_dark', xx - 0.03, xx + 0.03, -3.92, -3.54, 0.52, 0.95)
        box('timber_dark', xx - 0.03, xx + 0.03, -3.56, -3.52, 0.95, 1.4)
    for k in range(2):
        box('deck_planks', 0.78, 2.0, -3.545, -3.525, 1.08 + k * 0.14, 1.20 + k * 0.14, cj=0.05)


# ------------------------------------------------------------------ gutters
def exterior_details():
    al = math.atan(K); ca, sa = math.cos(al), math.sin(al)
    r = 0.065
    semi = [(r * math.cos(t), r * math.sin(t)) for t in [math.pi + math.pi * i / 10 for i in range(11)]]
    for s in (-1, 1):
        Ey, Ez = s * 3.95, 5.3 - K * 3.95
        cy = s * (3.95 + 0.03 + r + 0.005)
        cz = Ez - 0.03
        # half round gutter: y offset uses absolute; build profile pts (y,z)
        pts = [(cy + s * a, cz + b) for (a, b) in semi]
        prism('zinc', pts, (-4.88, 0, 0), V3((0, 1, 0)), V3((0, 0, 1)), V3((1, 0, 0)), 9.76)
        # bracket straps
        x = -4.4
        while x < 4.5:
            prism('iron', [(cy + s * a * 1.08, cz + b * 1.08 - 0.004) for (a, b) in semi], (x - 0.012, 0, 0), V3((0, 1, 0)), V3((0, 0, 1)), V3((1, 0, 0)), 0.024)
            x += 0.9
    # downspouts
    for (x, s) in ((4.72, -1), (-4.72, 1)):
        y = s * (3.95 + 0.03 + r + 0.005)
        cyl('zinc', (x, y, 3.0 - 0.08), (x, y, 0.42), 0.036, segs=12)
        cyl('zinc', (x, y, 0.42), (x, y + s * 0.15, 0.30), 0.036, segs=12)
        cyl('zinc', (x, y + s * 0.15, 0.30), (x, y + s * 0.28, 0.24), 0.036, segs=12)
        cyl('zinc', (x, y, 2.98), (x, y, 2.9), 0.06, segs=12, s1=0.6)
        for zz in (0.8, 1.6, 2.4):
            # wall strap reaching the house corner post
            box('iron', x - 0.02, x + 0.02, (y if s > 0 else y - 0.0) - 0.04, (y + s * 0.0) + 0.04, zz, zz + 0.03)
        # splash block
        box('stone_garden', x - 0.22, x + 0.22, y + s * 0.18 - 0.14, y + s * 0.18 + 0.14 + s * 0.26, -0.02, 0.05, n=(3, 3, 1), cj=0.08)


# ------------------------------------------------------------------ log builder
def log_axis(p0, p1, r, segs=7, span=None, a0=0.0, rings=(0.0, 0.5, 1.0), ringcols=(0.72, 1.05, 0.85), bark='bark', cut='endgrain',
             capboth=False, jit=0.12, col=(1, 1, 1)):
    p0 = V3(p0); p1 = V3(p1)
    ax = (p1 - p0); L = ax.length; ax.normalize()
    t = V3((0, 0, 1)) if abs(ax.z) < 0.9 else V3((1, 0, 0))
    e1 = ax.cross(t).normalized(); e2 = ax.cross(e1).normalized()
    full = span is None
    m = segs if full else max(2, int(segs * span / (2 * math.pi)))
    angs = [a0 + (2 * math.pi * i / segs if full else span * i / m) for i in range(segs if full else m + 1)]
    rj = [1 + jit * (rng.random() - .5) for _ in angs]
    bb = B(bark); ba = B(cut)

    def ring(base, rr, bm):
        return [bm.verts.new(base + (e1 * math.cos(a) + e2 * math.sin(a)) * rr * rj[i]) for i, a in enumerate(angs)]

    setbm(bb)
    o0 = ring(p0, r, bb); o1 = ring(p1, r, bb)
    cen = (p0 + p1) / 2
    fs = []
    n = len(angs)
    for i in range(n if full else n - 1):
        j = (i + 1) % n
        fs.append(addface(bb, [o0[i], o0[j], o1[j], o1[i]], cen))
    paint(fs, col, 0.12)
    # caps
    def cap(base, front):
        setbm(ba)
        cl = ba.loops.layers.float_color['Col']
        rs = []
        for ri, rf in enumerate(rings):
            if rf == 0.0 and full:
                rs.append([ba.verts.new(base)])
            elif rf == 0.0:
                rs.append([ba.verts.new(base)] * 1)
            else:
                rs.append(ring(base, r * rf, ba))
        fl = []
        for ri in range(len(rings) - 1):
            A = rs[ri]; Bq = rs[ri + 1]
            for i in range(n if full else n - 1):
                j = (i + 1) % n
                if len(A) == 1:
                    fl.append((addface(ba, [A[0], Bq[i], Bq[j]], cen), ri, ri + 1))
                else:
                    fl.append((addface(ba, [A[i], A[j], Bq[j], Bq[i]], cen), ri, ri + 1))
        for f, r0_, r1_ in fl:
            for l in f.loops:
                d = (l.vert.co - base).length / max(r, 1e-6)
                # which ring does this vertex belong to
                k = min(range(len(rings)), key=lambda q: abs(rings[q] - d))
                c = ringcols[k] if k < len(ringcols) else 0.9
                c *= 1.0 + 0.08 * (rng.random() - .5)
                l[cl] = (col[0] * c * 1.0, col[1] * c * 0.98, col[2] * c * 0.9, 1.0)
        return rs
    cap(p1, True)
    if capboth: cap(p0, False)
    if not full:
        # flat cut faces from axis to arc ends
        setbm(ba)
        for idx in (0, n - 1):
            a = angs[idx]
            dirv = (e1 * math.cos(a) + e2 * math.sin(a))
            q = [ba.verts.new(p0), ba.verts.new(p1), ba.verts.new(p1 + dirv * r * rj[idx]), ba.verts.new(p0 + dirv * r * rj[idx])]
            f = addface(ba, q, cen)
            # orient the face away from the sector interior
            mid = (angs[0] + angs[-1]) / 2
            inward = (e1 * math.cos(mid) + e2 * math.sin(mid)) * r * 0.4
            f.normal_update()
            if f.normal.dot(f.calc_center_median() - (cen + inward)) < 0: f.normal_flip()
            paint([f], (0.95, 0.85, 0.7), 0.1)


def outbuildings():
    # ---- woodpile with lean-to shed on the back wall (y=+3.5)
    xa, xb = -1.45, 1.45
    wood = 'shed_wood'
    for sx in (-1, 1):
        x = sx * 1.38
        box(wood, x - 0.055, x + 0.055, 4.78, 4.88, 0.0, 2.02, n=(1, 1, 5), cj=0.1)
        box(wood, x - 0.05, x + 0.05, 3.52, 3.62, 0.0, 2.3)  # back posts against wall
    box(wood, xa - 0.1, xb + 0.1, 4.75, 4.91, 1.96, 2.1, n=(10, 1, 1), cj=0.1)
    box(wood, xa - 0.1, xb + 0.1, 3.5, 3.6, 2.22, 2.36, n=(10, 1, 1), cj=0.1)
    kp = 0.167; bp = math.atan(kp); cb, sb = math.cos(bp), math.sin(bp)
    prism('roof_deck', [(3.5, 2.27), (5.05, 2.27 - kp * 1.55 + 0.0), (5.05, 2.33 - kp * 1.55), (3.5, 2.33)], (-1.6, 0, 0), V3((0, 1, 0)), V3((0, 0, 1)), V3((1, 0, 0)), 3.2)
    Ez = 2.33 - kp * 1.55
    shingles(-1.6, 1.6, 5.05, Ez, V3((0, -cb, sb)), V3((0, sb, cb)), 1.55 / cb, exp=0.13, wr=(0.14, 0.24))
    # rafters visible (tails)
    x = -1.5
    while x < 1.55:
        obox(wood, V3((x - 0.035, 3.6, 2.27 - 0.1)), V3((1, 0, 0)), V3((0, cb, -sb)) * 1.0, V3((0, sb, cb)), 0.07, 1.4 / cb, 0.1)
        x += 0.5
    # the stack itself
    row = 0
    z = 0.085
    while z < 1.62:
        x = xa + 0.06 + (0.07 if row % 2 else 0.0)
        while True:
            r = rng.uniform(0.058, 0.084)
            if x + r > xb - 0.05: break
            ln = rng.uniform(0.40, 0.52)
            y0 = 3.56
            y1 = y0 + ln
            zc = z + r * 0.4 + rng.uniform(-0.005, 0.01)
            if rng.random() < 0.28:
                log_axis((x, y0, zc), (x, y1, zc), r * 1.12, segs=8, span=math.pi * rng.choice([1.0, 0.5]), a0=rng.uniform(0, 6.28), col=tint(1, 1, 1, 0.1))
            else:
                log_axis((x, y0, zc), (x, y1, zc), r, segs=8, col=tint(1, 1, 1, 0.12))
            x += 2 * r + 0.006
        z += 0.142
        row += 1
    # loose logs on the ground beside the pile
    for (x, y, rot) in ((1.62, 4.2, 0.3), (1.75, 4.45, -0.4), (-1.65, 4.3, 0.15)):
        d = V3((math.cos(rot), math.sin(rot), 0)) * 0.26
        log_axis(V3((x, y, 0.08)) - d, V3((x, y, 0.08)) + d, 0.075, segs=8, capboth=True)
    # chopping block + axe
    bx, by = -2.6, 4.7
    log_axis((bx, by, -0.02), (bx, by, 0.44), 0.23, segs=14, rings=(0.0, 0.25, 0.5, 0.75, 1.0), ringcols=(0.7, 1.05, 0.82, 1.0, 0.78), jit=0.1)
    # axe stuck in the block
    cyl('door_wood', (bx + 0.02, by, 0.47), (bx + 0.36, by, 1.22), 0.019, segs=8, col=(1.0, 0.85, 0.65), cj=0.1)
    prism('iron', [(-0.085, 0.0), (0.085, 0.0), (0.03, 0.11), (-0.03, 0.11)], (bx + 0.02, by - 0.05, 0.47), V3((1, 0, 0)), V3((0, 0, 1)), V3((0, 1, 0)), 0.1)
    # chips
    for i in range(7):
        a = rng.uniform(0, 6.28); d = rng.uniform(0.28, 0.6)
        box('endgrain', bx + math.cos(a) * d - 0.03, bx + math.cos(a) * d + 0.03, by + math.sin(a) * d - 0.015, by + math.sin(a) * d + 0.015, 0.0, 0.012, col=tint(1, 1, 1, 0.15))
    # ---- stone-ringed garden bed beside the house
    ix0, ix1, iy0, iy1 = 4.95, 5.95, -1.7, 2.3
    box('soil', ix0 - 0.02, ix1 + 0.02, iy0 - 0.02, iy1 + 0.02, 0.0, 0.16, n=(5, 20, 1), cj=0.2, freq=6.0,
        post=lambda v, i, j, k: setattr(v, 'co', v.co + V3((0, 0, 0.035 * nz3(v.co, 9.0) + 0.02))) if k == 1 else None, skip=('bottom',))
    perim = []
    def ringline(xa_, ya_, xb_, yb_, thick):
        L = math.hypot(xb_ - xa_, yb_ - ya_)
        ux, uy = (xb_ - xa_) / L, (yb_ - ya_) / L
        for w in split_widths(L, 0.24, 0.42):
            pass
        t = 0.0
        for w in split_widths(L, 0.24, 0.42):
            cx, cy = xa_ + ux * (t + w / 2), ya_ + uy * (t + w / 2)
            h = rng.uniform(0.17, 0.25)
            size = (abs(ux) * (w - 0.015) + abs(uy) * thick, abs(uy) * (w - 0.015) + abs(ux) * thick, h)
            rbox('stone_garden', (cx + rng.uniform(-0.01, 0.01), cy + rng.uniform(-0.02, 0.02), h / 2 - 0.03), size, col=rng.choice([(1, 1, 1), (0.88, 0.86, 0.8), (1.05, 1.0, 0.93), (0.8, 0.78, 0.74)]), m=2, k=0.55, noise=0.1)
            t += w
    tk = 0.2
    ringline(ix0 - tk / 2, iy0 - tk, ix0 - tk / 2, iy1 + tk, tk)
    ringline(ix1 + tk / 2, iy0 - tk, ix1 + tk / 2, iy1 + tk, tk)
    ringline(ix0, iy0 - tk / 2, ix1, iy0 - tk / 2, tk)
    ringline(ix0, iy1 + tk / 2, ix1, iy1 + tk / 2, tk)
