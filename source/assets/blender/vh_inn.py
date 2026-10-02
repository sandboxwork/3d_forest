import sys
sys.path.insert(0, '/shared/river/assets/blender')
from vh_base import *

rng.seed(505)
W, D = 12.0, 9.0
ye = D / 2
ze = 5.6
K = 0.72
ZF = 2.95     # first floor line
J = 0.35      # jetty
fr = frames(W, D)
F, Bk, R, L = fr['F'], fr['B'], fr['R'], fr['L']
F2 = F.shifted(J)
PLc = (1.0, 0.95, 0.82)
zr, zs = roof_fn(ze, K, ye)

LOW = {
    'F': [(-0.8, 0.8, Z0, Z0 + 2.2), win_hole(-2.7, 1.75, 1.1, 1.3), win_hole(2.7, 1.75, 1.1, 1.3), win_hole(-4.75, 1.75, 1.0, 1.3), win_hole(4.75, 1.75, 1.0, 1.3)],
    'B': [win_hole(-4.2, 1.75, 1.0, 1.25), win_hole(-1.8, 1.75, 1.0, 1.25), (0.4, 1.3, Z0, Z0 + 2.05), win_hole(3.0, 1.75, 1.0, 1.25), win_hole(4.9, 1.75, 1.0, 1.25)],
    'R': [win_hole(-2.5, 1.75, 1.0, 1.25), win_hole(0.0, 1.75, 1.0, 1.25), win_hole(2.5, 1.75, 1.0, 1.25)],
    'L': [win_hole(-2.5, 1.75, 1.0, 1.25), win_hole(0.0, 1.75, 1.0, 1.25), win_hole(2.5, 1.75, 1.0, 1.25)],
}
UP = {
    'F': [win_hole(u, 4.35, 0.95, 1.25) for u in (-4.6, -2.7, 0.0, 2.7, 4.6)],
    'B': [win_hole(u, 4.35, 0.95, 1.25) for u in (-4.6, -2.3, 0.0, 2.3, 4.6)],
    'R': [win_hole(u, 4.35, 0.95, 1.25) for u in (-2.8, -0.2, 2.4)],
    'L': [win_hole(u, 4.35, 0.95, 1.25) for u in (-2.8, -0.2, 2.4)],
}
plinth(W, D)
# --- ground floor: plaster
for key, Fk, half in (('F', F, W / 2), ('B', Bk, W / 2), ('R', R, D / 2), ('L', L, D / 2)):
    plaster_wall(Fk, -half, half, Z0, ZF, LOW[key], col=tint(*PLc, 0.02))
    Fk.box('paint_trim', -half, half, 0, 0.05, Z0, Z0 + 0.14, n=(8, 1, 1))
for sx in (-1, 1):
    for Fk in (F, Bk):
        pass
box('paint_trim', -W / 2 - 0.02, -W / 2 + 0.2, -D / 2 - 0.02, -D / 2 + 0.2, Z0, ZF, cj=0.03)
for sx in (-1, 1):
    for sy in (-1, 1):
        x0, x1 = (W / 2 - 0.2, W / 2 + 0.02) if sx > 0 else (-W / 2 - 0.02, -W / 2 + 0.2)
        y0, y1 = (D / 2 - 0.2, D / 2 + 0.02) if sy > 0 else (-D / 2 - 0.02, -D / 2 + 0.2)
        box('paint_trim', x0, x1, y0, y1, Z0, ZF, n=(1, 1, 3), cj=0.03)
# --- jetty structure
for u in [-5.7 + 0.55 * i for i in range(22)]:
    F.box('timber_beam', u - 0.065, u + 0.065, 0.0, J + 0.02, ZF - 0.18, ZF - 0.0, cj=0.1, seed=u)
F.box('timber_dark', -W / 2 - 0.02, W / 2 + 0.02, J - 0.0, J + 0.0 + 0.02, ZF - 0.0, ZF + 0.12, n=(8, 1, 1))
box('timber_dark', -W / 2, W / 2, -D / 2 - J, -D / 2, ZF - 0.04, ZF + 0.02, n=(8, 1, 1), cj=0.1)
F.box('timber_dark', -W / 2, W / 2, 0.0, 0.2, ZF - 0.34, ZF - 0.18, n=(10, 1, 1), cj=0.12)       # bressummer under the jetty
# --- upper floor: plaster + timber frame (front wall shifted by jetty)
UF = {'F': (F2, -W / 2 - 0.0, W / 2), 'B': (Bk, -W / 2, W / 2)}
ZEF = zs(ye + J) - 0.2          # front wall top (the jetty wall sits lower on the roof slope)
for key, (Fk, a, b) in UF.items():
    zt_ = ZEF if key == 'F' else ze
    plaster_wall(Fk, a, b, ZF, zt_, UP[key], col=tint(*PLc, 0.02))
    halftimber(Fk, a + 0.1, b - 0.1, ZF + 0.0, zt_, UP[key], spacing=1.35, rails=[3.25], braces=True, depth=0.05)
for key, Fk in (('R', R), ('L', L)):
    half_a, half_b = -(D / 2 + J), D / 2
    sgn = 1
    # side walls: R frame u along +y; L frame u along -y  => jetty extension at the front is at u<0 for R, u>0 for L
    if key == 'R':
        a, b = -(D / 2 + J), D / 2
    else:
        a, b = -D / 2, D / 2 + J
    if key == 'R':
        segs_ = [(a, -D / 2, ZEF), (-D / 2, b, ze)]
    else:
        segs_ = [(a, D / 2, ze), (D / 2, b, ZEF)]
    for (sa, sb, zt_) in segs_:
        hh = [h for h in UP[key] if h[1] > sa and h[0] < sb]
        plaster_wall(Fk, sa, sb, ZF, zt_, hh, col=tint(0.98, 0.93, 0.8, 0.02))
        halftimber(Fk, sa + 0.1, sb - 0.1, ZF, zt_, hh, spacing=1.45, rails=[3.25], braces=(sb - sa) > 3, depth=0.05)
# upper corner posts
for sx in (-1, 1):
    for sy in (-1, 1):
        x0, x1 = (W / 2 - 0.2, W / 2 + 0.03) if sx > 0 else (-W / 2 - 0.03, -W / 2 + 0.2)
        yy = -D / 2 - J if sy < 0 else D / 2
        y0, y1 = ((yy - 0.03, yy + 0.2) if sy < 0 else (yy - 0.2, yy + 0.03))
        box('timber_dark', x0, x1, y0, y1, ZF, (ZEF if sy < 0 else ze) + 0.02, n=(1, 1, 3), cj=0.1)
# --- gables (plaster + timber)
for Fk in (R, L):
    za = ze + K * ye
    hole = [win_hole(0, ze + 1.0, 0.8, 0.9)]
    gable_fill(Fk, ye, ze, za, 'plaster', holes=hole, col=tint(0.98, 0.93, 0.8, 0.02))
    rf = lambda zb, zt, za=za: (-((za - zt) / K - 0.0), (za - zt) / K)
    halftimber(Fk, -ye + 0.1, ye - 0.1, ze, za - 0.08, hole, spacing=1.5, rails=[ze + 2.0], braces=False, depth=0.05,
               topfn=lambda u, za=za: za - K * abs(u) - 0.12)
    window(Fk, 0, ze + 1.0, 0.8, 0.9, rows=2, cols=1, shutters=False)
# --- windows & doors
for (Fk, key) in ((F, 'F'), (Bk, 'B'), (R, 'R'), (L, 'L')):
    for h in LOW[key]:
        uc, zc = (h[0] + h[1]) / 2, (h[2] + h[3]) / 2
        w, hh = h[1] - h[0], h[3] - h[2]
        if h[2] <= Z0 + 0.01:
            door(Fk, uc, w, hh, mat='paint_door' if Fk is F else 'door_wood', lintel='timber_beam' if Fk is F else None, hardware=True, step=False)
            if Fk is F: double_door_extras(Fk, uc, w, Z0, hh)
        else:
            window(Fk, uc, zc, w, hh, rows=3 if hh > 1.15 else 2, cols=1, shutters=(Fk is F), flowerbox=(Fk is F))
for (Fk, key) in ((F2, 'F'), (Bk, 'B'), (R, 'R'), (L, 'L')):
    for h in UP[key]:
        uc, zc = (h[0] + h[1]) / 2, (h[2] + h[3]) / 2
        w, hh = h[1] - h[0], h[3] - h[2]
        window(Fk, uc, zc, w, hh, rows=3, cols=1, shutters=(Fk is F2), flowerbox=(Fk is F2))
# --- entrance steps, lanterns, sign
stone_steps(F, 0.0, 2.2, nsteps=2, rise=0.17, tread=0.4, ztop=Z0)
lantern(F, -1.3, 0, 1.9)
lantern(F, 1.3, 0, 1.9)
def mug(Fk, u, n, z, bw, bh):
    c = Fk.P(u, n + 0.045, z)
    lathe('brass', c + V3((0, 0, -0.17)), [(0, 0.11), (0.02, 0.12), (0.3, 0.1), (0.31, 0.1)], segs=14, col=(1.1, 1, 0.9))
    lathe('chalk', c + V3((0, 0, 0.12)), [(0, 0.1), (0.03, 0.115), (0.06, 0.1), (0.07, 0.06)], segs=12)
    ring_pts = [c + V3((0.0, 0.0, 0.0)) + Fk.U * (0.1 + 0.075 * math.sin(t)) + V3((0, 0, 0.0)) + V3((0, 0, 0.075 * (math.cos(t) - 1) * -0.0)) for t in []]
    pts = [c + Fk.U * (0.1 + 0.09 * math.sin(t)) + V3((0, 0, 0.0)) + V3((0, 0, 0.06 * math.cos(t) - 0.0)) for t in [i * math.pi / 8 for i in range(9)]]
    tube('brass', [p + V3((0, 0, 0.0)) for p in pts], 0.012, segs=5, pn=Fk.N)
hanging_sign(F2, -5.35, 4.3, board_w=0.85, board_h=0.7, arm=1.25, emblem=mug, board_mat='timber_beam', drop=0.28)
# --- dormers + roof
dormer(ye - 1.2, -3.0, 1.9, zs, K, K2=0.8, hgt=1.35, window_w=0.9, window_h=0.95, flowerbox=True)
dormer(ye - 1.2, 3.0, 1.9, zs, K, K2=0.8, hgt=1.35, window_w=0.9, window_h=0.95, flowerbox=True)
with placed((0, 0, 0), math.pi):
    dormer(ye - 1.2, -3.0, 1.7, zs, K, K2=0.8, hgt=1.3, window_w=0.8, window_h=0.9)
    dormer(ye - 1.2, 3.0, 1.7, zs, K, K2=0.8, hgt=1.3, window_w=0.8, window_h=0.9)
zr, zs = gable_roof(-W / 2 - 0.6, W / 2 + 0.6, ye, ze, K, oy=0.9, gutters=(-1, 1), exp=0.2, Ls=0.46, wr=(0.24, 0.42), colk=1.1)
yo = ye + 0.9
for (x, s) in ((W / 2 - 0.4, -1), (-W / 2 + 0.4, 1), (W / 2 - 0.4, 1)):
    downspout(x, s * (yo + 0.1), zs(yo) - 0.16, s * (ye + (J if s < 0 else 0) + 0.06), s)
# chimneys
for cx in (-3.9, 3.9):
    chimney(cx, 0.0, 1.0, 0.75, ze + 0.5, zr + 1.5, kind='brick')
    flashing(cx, 0.0, 1.0, 0.75, zr - K * 0.4 - 0.03)
# --- terrace: tables, benches, barrels, hay-bale-free
for tx in (-3.9, 3.6):
    table(tx, -D / 2 - J - 1.5, 0.0, 1.5, 0.75, 0.78, 0.0)
    bench(tx, -D / 2 - J - 2.15, 0.0, 1.5, 0.0)
    bench(tx, -D / 2 - J - 0.85, 0.0, 1.5, 0.0)
barrel(-5.5, -D / 2 - 0.55, 0.0, 0.32, 0.85)
barrel(-5.1, -D / 2 - 0.45, 0.0, 0.32, 0.85) if False else None
barrel(5.4, -D / 2 - 0.55, 0.0, 0.32, 0.85)
crate(5.5, -D / 2 - 1.3, 0.0, 0.6, 0.45, 0.4, 0.3)
barrel(-4.6, D / 2 + 0.5, 0.0, 0.32, 0.85)
barrel(-4.0, D / 2 + 0.5, 0.0, 0.32, 0.85)
woodpile(1.5, D / 2 + 0.05, 0.0, 2.8, 1.4, depth=0.5)
pot(-1.5, -D / 2 - 0.4)
pot(1.5, -D / 2 - 0.4)
bucket(0.2, D / 2 + 0.5)

cols = [C(-W / 2 - 0.1, W / 2 + 0.1, -D / 2 - J, D / 2 + 0.1, ze, -0.5), C(-4.65, -3.15, -D / 2 - J - 2.5, -D / 2 - J - 0.5, 1.0, 0),
        C(2.85, 4.35, -D / 2 - J - 2.5, -D / 2 - J - 0.5, 1.0, 0)]
views = {
    'front34': ((-14, -15, 2.8), (0, 0, 3.4), 35),
    'back34': ((14, 15, 3.8), (0, 0, 3.4), 35),
    'front': ((0, -22, 2.4), (0, 0, 3.6), 35),
    'door': ((-3.5, -10.5, 2.0), (-0.5, -5.0, 2.8), 32),
    'sign': ((-8.0, -9.0, 4.2), (-5.4, -5.0, 4.0), 32),
}
finish('inn', W, D, ze, zr + 0.07, (0, -D / 2), 'inn', '여관', cols, views)
