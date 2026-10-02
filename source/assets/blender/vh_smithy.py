import sys
sys.path.insert(0, '/shared/river/assets/blender')
from vh_base import *

rng.seed(707)
W, D = 9.0, 7.5
MW = 6.0               # main block width
MCX = -1.5             # main block centre x
ye = D / 2
ze = 3.3
K = 0.7
fr = frames(MW, D, cx=MCX)
F, Bk, R, L = fr['F'], fr['B'], fr['R'], fr['L']
half_x = MW / 2
zr = ze + K * half_x + 0.14
OPS = {
    'F': [(-0.7, 0.7, Z0, Z0 + 2.25), win_hole(-2.0, 1.75, 0.9, 1.1), win_hole(2.0, 1.75, 0.9, 1.1)],
    'B': [win_hole(-1.5, 1.8, 0.9, 1.1), win_hole(1.5, 1.8, 0.9, 1.1)],
    'R': [(-0.5 + 0.6, 0.5 + 0.6, Z0, Z0 + 2.1)],
    'L': [win_hole(-1.8, 1.8, 0.9, 1.1), win_hole(1.8, 1.8, 0.9, 1.1)],
}
ZB = 1.35   # stone to board transition


def anvil(x, y, z, rot=0.0, s=1.0):
    with placed((x, y, z), rot):
        Fa = Fr((0, 0, 0), (1, 0, 0), (0, -1, 0))
        pts = [(-0.14, 0.0), (0.14, 0.0), (0.11, 0.07), (0.07, 0.12), (0.07, 0.2), (0.3, 0.215), (0.36, 0.25), (0.34, 0.27), (-0.24, 0.27), (-0.24, 0.215), (-0.07, 0.2), (-0.07, 0.12), (-0.11, 0.07)]
        pts = [(a * s, b * s) for a, b in pts]
        Fa.poly('iron', pts, -0.075 * s, 0.075 * s, col=(0.9, 0.9, 0.95))
        # polished face
        box('iron', -0.24 * s, 0.1 * s, -0.075 * s, 0.075 * s, 0.268 * s, 0.274 * s, col=(1.6, 1.6, 1.7))
        # hardy hole
        box('soot', -0.16 * s, -0.12 * s, -0.02 * s, 0.02 * s, 0.268 * s, 0.276 * s)


def hammer(x, y, z, rot=0.0, tilt=0.0):
    with placed((x, y, z), rot):
        cyl('door_wood', (-0.18, 0, 0.02), (0.14, 0, 0.02), 0.014, segs=5)
        box('iron', 0.1, 0.17, -0.025, 0.025, -0.0, 0.05)


def tongs(x, y, z, rot=0.0, L=0.55, hang=True):
    with placed((x, y, z), rot):
        for sy in (-1, 1):
            tube('iron', [V3((0, sy * 0.012, 0)), V3((0, sy * 0.015, -0.2 * L)), V3((0, sy * 0.004, -L))], 0.007, segs=4, pn=(1, 0, 0))
        cyl('iron', (0, -0.02, -0.08), (0, 0.02, -0.08), 0.01, segs=5)


def horseshoe(x, y, z, rot=0.0, s=1.0):
    with placed((x, y, z), rot):
        pts = [V3((0.065 * s * math.cos(t), 0.0, -0.075 * s * math.sin(t) + 0.0)) for t in [math.radians(a) for a in range(-40, 221, 20)]]
        pts = [V3((0.065 * s * math.sin(t), 0, 0.07 * s * math.cos(t))) for t in [math.radians(a) for a in range(-130, 131, 20)]]
        tube('iron', pts, 0.009 * s, segs=4, pn=(0, 1, 0))


def bellows(x, y, z, rot):
    with placed((x, y, z), rot):
        # lower board, upper board (tilted), leather sides, nozzle, handle; nozzle points to local +x
        hexa('timber_beam', [(-0.9, -0.2, 0.0), (0.0, -0.06, 0.0), (0.0, 0.06, 0.0), (-0.9, 0.2, 0.0), (-0.9, -0.2, 0.05), (0.0, -0.06, 0.05), (0.0, 0.06, 0.05), (-0.9, 0.2, 0.05)], col=tint(1, 1, 1, 0.1))
        ang = math.radians(15)
        ca, sa = math.cos(ang), math.sin(ang)
        def up(px, py, pz): return (px * ca + pz * sa * 0 - 0.0, py, pz + (px + 0.0) * -sa * -1.0 * -1)
        top = []
        for (px, py) in ((-0.9, -0.2), (0.0, -0.06), (0.0, 0.06), (-0.9, 0.2)):
            top.append((px, py, 0.05 + 0.2 * (-px / 0.9) + 0.0))
        hexa('timber_beam', [(a, b, c + 0.0) for (a, b, c) in top] + [(a, b, c + 0.05) for (a, b, c) in top], col=tint(1, 1, 1, 0.1))
        # leather folds
        Fa = Fr((0, 0, 0), (1, 0, 0), (0, -1, 0))
        for sy, wd in ((-1, 0.2), (1, 0.2)):
            pts = [(-0.9, 0.05), (0.0, 0.05), (-0.9, 0.25)]
            yy = sy * 0.06
            bm = B('leather')
            poly_pts = [V3((-0.9, sy * 0.2, 0.05)), V3((0.0, sy * 0.06, 0.05)), V3((-0.0, sy * 0.06, 0.05)), V3((-0.9, sy * 0.2, 0.25))]
            # triangular side panel
            setbm(bm)
            vs = [bm.verts.new(p) for p in (V3((-0.9, sy * 0.2, 0.05)), V3((0.0, sy * 0.06, 0.05)), V3((-0.9, sy * 0.2, 0.25)))]
            f = bm.faces.new(vs); f.normal_update()
            if f.normal.dot(V3((0, sy, 0))) < 0: f.normal_flip()
            paint([f], (1, 0.9, 0.8), 0.1)
            vs2 = [bm.verts.new(p) for p in (V3((-0.9, sy * 0.2, 0.05)), V3((0.0, sy * 0.06, 0.05)), V3((-0.9, sy * 0.2, 0.25)))]
            f2 = bm.faces.new(vs2); f2.normal_update()
            if f2.normal.dot(V3((0, -sy, 0))) < 0: f2.normal_flip()
            paint([f2], (0.8, 0.7, 0.6), 0.1)
        cyl('iron', (0.0, 0, 0.055), (0.55, 0, 0.1), 0.03, segs=8, s1=0.6)
        cyl('timber_dark', (-0.9, 0, 0.27), (-1.6, 0, 0.55), 0.022, segs=6)
        cyl('timber_dark', (-0.9, 0, 0.1), (-0.9, 0, 0.0), 0.0, segs=3) if False else None


def hearth(cx, cy):
    """forge hearth against the back wall (y=+3.75 side) with sloped hood."""
    hx, hy = 1.0, 0.8
    # base: stone block
    pal = PAL_STONE
    box('mortar', cx - hx + 0.03, cx + hx - 0.03, cy - hy + 0.03, cy + hy, 0.0, 0.84)
    fs = [Fr((cx, cy - hy, 0), (1, 0, 0), (0, -1, 0)), Fr((cx + hx, cy, 0), (0, 1, 0), (1, 0, 0)), Fr((cx - hx, cy, 0), (0, -1, 0), (-1, 0, 0))]
    masonry(fs[0], 'stone_chimney', -hx, hx, -0.05, 0.84, -0.1, 0.03, pal=pal, hs=(0.14, 0.22), ws=(0.25, 0.5), m=1, k=0.6)
    masonry(fs[1], 'stone_chimney', -hy, hy, -0.05, 0.84, -0.1, 0.03, pal=pal, hs=(0.14, 0.22), ws=(0.25, 0.5), m=1, k=0.6)
    masonry(fs[2], 'stone_chimney', -hy, hy, -0.05, 0.84, -0.1, 0.03, pal=pal, hs=(0.14, 0.22), ws=(0.25, 0.5), m=1, k=0.6)
    # top slab with fire bed recess
    box('stone_chimney', cx - hx - 0.04, cx + hx + 0.04, cy - hy - 0.04, cy + hy, 0.84, 0.9, n=(6, 3, 1), cj=0.06, skip=('top',))
    for (x0, x1, y0, y1) in ((cx - hx - 0.04, cx + hx + 0.04, cy - hy - 0.04, cy - 0.35), (cx - hx - 0.04, cx - 0.55, cy - 0.35, cy + hy), (cx + 0.55, cx + hx + 0.04, cy - 0.35, cy + hy),
                             (cx - 0.55, cx + 0.55, cy + 0.35, cy + hy)):
        box('stone_chimney', x0, x1, y0, y1, 0.9, 0.94, cj=0.06)
    box('coal', cx - 0.55, cx + 0.55, cy - 0.35, cy + 0.35, 0.84, 0.9)
    box('forge_glow', cx - 0.4, cx + 0.4, cy - 0.25, cy + 0.25, 0.9, 0.925, n=(6, 4, 1), cj=0.3, freq=6.0)
    for i in range(14):
        blob('forge_glow' if i % 3 == 0 else 'coal', (cx + rng.uniform(-0.45, 0.45), cy + rng.uniform(-0.3, 0.3), 0.93), rng.uniform(0.03, 0.06), col=tint(1, 1, 1, 0.3), rows=2, segs=5, squash=0.7, jit=0.4)
    # tuyere + hood
    cyl('iron', (cx + 0.9, cy + 0.2, 0.98), (cx + 0.2, cy + 0.1, 0.95), 0.03, segs=8)
    zh0, zh1 = 1.75, 2.75
    p0 = [(cx - 1.15, cy - 0.95, zh0), (cx + 1.15, cy - 0.95, zh0), (cx + 1.15, 3.74, zh0), (cx - 1.15, 3.74, zh0)]
    p1 = [(cx - 0.5, cy + 0.1, zh1), (cx + 0.5, cy + 0.1, zh1), (cx + 0.5, 3.74, zh1), (cx - 0.5, 3.74, zh1)]
    # hood walls (hollow-ish: front and sides as slanted slabs)
    hexa('stone_chimney', p0 + p1, col=(0.95, 0.9, 0.85), cj=0.1, skip=('bottom',))
    box('timber_beam', cx - 1.2, cx + 1.2, cy - 1.0, cy - 0.85, zh0 - 0.12, zh0 + 0.04, n=(6, 1, 1), cj=0.1)   # mantel beam
    box('soot', cx - 1.0, cx + 1.0, cy - 0.84, cy - 0.8, zh0 - 0.08, zh0 + 0.0) if False else None
    for xx in (cx - 1.0, cx + 1.0):
        box('timber_dark', xx - 0.05, xx + 0.05, cy - 0.97, cy - 0.87, zh0 + 0.04, zh0 + 0.5) if False else None
    # tools hanging from the mantel
    for i, xx in enumerate((cx - 0.8, cx - 0.5, cx - 0.2, cx + 0.2, cx + 0.5, cx + 0.8)):
        if i % 2 == 0:
            tongs(xx, cy - 1.02, zh0 - 0.12, 0.0, L=0.5 + 0.1 * (i % 3))
        else:
            hammer(xx + 0.05, cy - 1.02, zh0 - 0.35, math.pi / 2)
            cyl('iron', (xx, cy - 1.02, zh0 - 0.12), (xx, cy - 1.02, zh0 - 0.3), 0.004, segs=3)


plinth(MW, D, ztop=Z0, out=0.1) if False else None
# --- main block: plinth with offset centre
with placed((MCX, 0, 0)):
    plinth(MW, D)
HOLES = {'F': OPS['F'], 'B': OPS['B'], 'R': OPS['R'], 'L': OPS['L']}
for key, Fk, half in (('F', F, MW / 2), ('B', Bk, MW / 2), ('R', R, D / 2), ('L', L, D / 2)):
    holes = HOLES[key]
    stone_wall(Fk, -half + 0.3, half - 0.3, Z0, ZB, holes, thick=0.28)
    core(Fk, -half, half, ZB, ze, holes)
    vboards(Fk, -half + 0.2, half - 0.2, ZB - 0.0, ze, holes, mat='siding_dark', bw=0.22)
    Fk.box('timber_dark', -half, half, 0.0, 0.07, ZB - 0.05, ZB + 0.06, n=(6, 1, 1), cj=0.1)       # sill rail on top of the stone
quoins_c = []
with placed((MCX, 0, 0)):
    quoins(MW, D, Z0, ZB + 0.05, sz=0.5)
with placed((MCX, 0, 0)):
    corner_posts(MW, D, ZB, ze + 0.02, mat='timber_dark', sz=0.2)
for Fk in (F, Bk):
    hole = [win_hole(0, ze + 0.95, 0.8, 0.8)] if Fk is F else []
    gable_fill(Fk, half_x, ze, ze + K * half_x, 'board', holes=hole)
    if Fk is F:
        window(Fk, 0, ze + 0.95, 0.8, 0.8, rows=2, cols=1, shutters=True, sill=False)
for (Fk, key) in ((F, 'F'), (Bk, 'B'), (R, 'R'), (L, 'L')):
    for h in OPS[key]:
        uc, zc = (h[0] + h[1]) / 2, (h[2] + h[3]) / 2
        w, hh = h[1] - h[0], h[3] - h[2]
        if h[2] <= Z0 + 0.01:
            if Fk is F:
                door(Fk, uc, w, hh, mat='paint_door', lintel='timber_beam', step=True)
            else:
                door(Fk, uc, w, hh, mat='door_wood', lintel='timber_beam', step=False)
        else:
            window(Fk, uc, zc, w, hh, rows=2, cols=1, shutters=(Fk is F), flowerbox=False)
            for k in range(-2, 3):
                Fk.box('iron', uc + k * 0.17 - 0.008, uc + k * 0.17 + 0.008, -0.1, -0.08, zc - hh / 2 + 0.02, zc + hh / 2 - 0.02) if False else None
# roof of the main block (ridge along y): built in rotated frame
with placed((MCX, 0, 0), math.pi / 2):
    zr_, zs_ = gable_roof(-ye - 0.45, ye + 0.45, half_x, ze, K, oy=0.55, gutters=(-1, 1), exp=0.15, Ls=0.36, wr=(0.18, 0.32))
zs = zs_
# --- lean-to forge shed (right side): floor slabs, back wall, posts, roof
LX0, LX1 = MCX + MW / 2, 4.5
for ix in range(6):
    for iy in range(15):
        cx_ = LX0 + 0.3 + ix * 0.55 + rng.uniform(-0.02, 0.02)
        cy_ = -3.75 + 0.25 + iy * 0.5 + rng.uniform(-0.02, 0.02)
        if cx_ > LX1 + 0.1: continue
        rbox('stone_foundation', (cx_, cy_, 0.0), (0.53, 0.49, 0.12), col=tint(1.2, 1.15, 1.1, 0.12), m=1, k=0.6, noise=0.05)
# back wall (stone) of the lean-to
Fbk = Fr((LX1, 3.75, 0), (-1, 0, 0), (0, 1, 0))
cx_l = (LX0 + LX1) / 2
Fb2 = Fr((cx_l, 3.75, 0), (-1, 0, 0), (0, 1, 0))
hw_ = (LX1 - LX0) / 2
stone_wall(Fb2, -hw_ + 0.0, hw_ + 0.2, Z0 - 0.3, 3.0, [], thick=0.3, hs=(0.2, 0.3))
# right-side half wall near the back
Fr_side = Fr((LX1, 0, 0), (0, 1, 0), (1, 0, 0))
stone_wall(Fr_side, 1.0, 3.75, Z0 - 0.3, 1.1, [], thick=0.3, hs=(0.2, 0.3))
box('stone_wall', LX1 - 0.34, LX1 + 0.04, 0.96, 3.79, 1.08, 1.16, n=(1, 6, 1), cj=0.06)
# lean-to posts + beams
zroof = lambda x: 3.0 - (x - LX0) * 0.14
for (px, py) in ((LX1 - 0.12, -3.6), (LX1 - 0.12, -0.9)):
    box('timber_dark', px - 0.1, px + 0.1, py - 0.1, py + 0.1, 0.0, zroof(px) - 0.28, n=(1, 1, 4), cj=0.1)
box('timber_beam', LX1 - 0.2, LX1 + 0.0, -3.8, 0.0, zroof(LX1 - 0.1) - 0.28, zroof(LX1 - 0.1) - 0.1, n=(1, 8, 1), cj=0.1)
# knee braces
for (py, sg) in ((-3.6, 1), (-0.9, 1)):
    cyl('timber_dark', (LX1 - 0.22, py + 0.0, zroof(LX1) - 0.9), (LX1 - 0.22, py + 0.6, zroof(LX1) - 0.32), 0.04, segs=5)
    cyl('timber_dark', (LX1 - 0.22, py, zroof(LX1) - 0.9), (LX1 - 0.22, py - 0.6, zroof(LX1) - 0.32), 0.04, segs=5)
# lean-to roof plane (slope along x): rotated frame: local x' -> world y, local y' -> world -x
with placed((0, 0, 0), math.pi / 2):
    roof_plane(-3.95, 3.95, (-(LX1 + 0.5), zroof(LX1 + 0.5) + 0.0), (-(LX0 + 0.35), 3.0 + 0.0), exp=0.14, Ls=0.34, wr=(0.18, 0.32), rafters=False, barge=(True, True))
# rafters under lean-to roof
for py in [-3.6 + 0.6 * i for i in range(12)]:
    cyl('timber_dark', (LX0 + 0.1, py, 2.9), (LX1 + 0.4, py, zroof(LX1 + 0.4) - 0.14), 0.04, segs=5)
# --- hearth, anvil, bellows, quench barrel
HX, HY = 3.2, 3.75 - 0.8
hearth(HX, HY)
chimney(HX, 3.75 - 0.45, 1.0, 0.8, 2.6, zr + 0.9, 'stone')
stump(HX - 0.2, 0.4, 0.3, 0.62)
anvil(HX - 0.2, 0.4, 0.62, 0.0, 1.05)
hammer(HX - 0.5, 0.45, 0.9, 0.5)
bellows(LX1 - 0.55, 2.3, 0.82, math.pi * 0.5 * 0 + math.pi)  # nozzle toward -x? adjusted below
barrel(LX1 - 0.5, -0.55, 0.0, 0.3, 0.85)
lathe('soot', (LX1 - 0.5, -0.55, 0.8), [(0, 0.26), (0.004, 0.26)], segs=14)
# coal heap + sacks + iron bars
for i in range(30):
    blob('coal', (3.75 + rng.uniform(-0.3, 0.3), 3.1 + rng.uniform(-0.3, 0.3) - 0.2, 0.06 + rng.uniform(0, 0.14)), rng.uniform(0.05, 0.09), col=tint(1, 1, 1, 0.4), rows=2, segs=5, jit=0.4, squash=0.7)
for k in range(4):
    cyl('iron', (LX0 + 0.35, -3.1 + k * 0.1, 0.05 + 0.03 * k), (LX0 + 1.5, -3.1 + k * 0.1, 0.05 + 0.03 * k), 0.016, segs=5)
sack(LX0 + 0.5, 1.2, 0.0, 1.0, col=(0.9, 0.85, 0.8)); sack(LX0 + 0.5, 1.6, 0.0, 0.95, col=(0.85, 0.8, 0.75))
# horseshoes + wheel rim on the main right wall
for k in range(5):
    horseshoe(LX0 + 0.03, -2.5 + k * 0.3, 2.0 - 0.0 + 0.0 + (0.1 if k % 2 else 0.0), math.pi / 2 * 0 + math.pi / 2, 1.1)
# --- front: sign, props
def anvil_emblem(Fk, u, n, z, bw, bh):
    pts = [(-0.1, -0.14), (0.1, -0.14), (0.07, -0.08), (0.07, -0.03), (0.2, -0.01), (0.27, 0.03), (0.17, 0.06), (-0.2, 0.06), (-0.2, 0.0), (-0.07, -0.03), (-0.07, -0.08)]
    pts = [(u + a, z + b + 0.02) for a, b in pts]
    Fk.poly('iron', pts, n + 0.03, n + 0.07, col=(0.9, 0.9, 0.95))
hanging_sign(F, 2.6, 2.7, board_w=0.7, board_h=0.55, arm=0.95, emblem=anvil_emblem, board_mat='timber_beam', drop=0.28)
lantern(F, -1.1, 0, 2.0)
barrel(-3.6 + MCX + 3.0, -ye - 0.5, 0.0, 0.3, 0.8)
crate(MCX - 2.7, -ye - 0.5, 0.0, 0.6, 0.45, 0.45, 0.2)
# cart wheel leaning against left wall
Fw = Fr((MCX - MW / 2, 0, 0), (0, -1, 0), (-1, 0, 0))
cyl('timber_beam', (MCX - MW / 2 - 0.12, 1.0, 0.7), (MCX - MW / 2 - 0.12, 1.0, 0.7), 0.0, segs=3) if False else None
woodpile(MCX - MW / 2 - 0.02, -0.5, math.pi / 2, 2.6, 1.3, depth=0.5) if False else None
woodpile(MCX - MW / 2 - 0.02, 1.0, math.pi / 2 * -1 + math.pi, 2.6, 1.3, depth=0.5)
bucket(MCX + 2.3, -ye - 0.4)

cols = [C(MCX - MW / 2 - 0.1, MCX + MW / 2 + 0.1, -D / 2 - 0.1, D / 2 + 0.1, ze, -0.5), C(LX0, LX1 + 0.1, 3.4, 3.85, 3.0, -0.5), C(HX - 1.0, HX + 1.0, HY - 0.8, 3.75, 2.8, 0),
        C(LX1 - 0.4, LX1 + 0.1, 0.9, 3.85, 1.2, 0), C(LX1 - 0.25, LX1 + 0.0, -3.7, -3.5, 2.3, 0), C(HX - 0.5, HX + 0.1, 0.1, 0.7, 0.9, 0)]
views = {
    'front34': ((-12.5, -12, 2.6), (0.3, 0, 2.6), 35),
    'forge': ((9.5, -8.5, 2.0), (3.2, 1.0, 1.5), 35),
    'back34': ((10, 12, 3.8), (0, 0, 2.6), 35),
    'hearth': ((4.0, -2.0, 1.7), (3.2, 3.0, 1.2), 32),
}
finish('smithy', W, D, ze, zr + 0.07, (MCX, -D / 2), 'work', '대장간', cols, views)
