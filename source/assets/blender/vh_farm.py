import sys
sys.path.insert(0, '/shared/river/assets/blender')
from vh_base import *

rng.seed(606)
W, D = 10.0, 8.0
ye = D / 2
ze = 5.5
ZF = 3.0
K = 0.78
fr = frames(W, D)
F, Bk, R, L = fr['F'], fr['B'], fr['R'], fr['L']
zr, zs = roof_fn(ze, K, ye)
LOW = {
    'F': [(-0.55, 0.55, Z0, Z0 + 2.15), win_hole(-3.4, 1.8, 1.1, 1.3), win_hole(3.4, 1.8, 1.1, 1.3), win_hole(-1.85, 1.8, 0.8, 1.1), win_hole(1.85, 1.8, 0.8, 1.1)],
    'B': [win_hole(-3.3, 1.8, 1.0, 1.25), win_hole(-1.2, 1.8, 1.0, 1.25), (1.7, 2.65, Z0, Z0 + 2.1), win_hole(3.6, 1.8, 1.0, 1.25)],
    'R': [win_hole(-1.6, 1.8, 1.0, 1.25), win_hole(1.6, 1.8, 1.0, 1.25)],
    'L': [win_hole(2.6, 1.8, 1.0, 1.25)],
}
UP = {
    'F': [win_hole(u, 4.3, 0.95, 1.3) for u in (-3.4, 0.0, 3.4)],
    'B': [win_hole(u, 4.3, 0.95, 1.3) for u in (-3.3, -1.1, 1.1, 3.3)],
    'R': [win_hole(u, 4.3, 0.95, 1.3) for u in (-1.6, 1.6)],
    'L': [win_hole(u, 4.3, 0.95, 1.3) for u in (-1.6, 1.6)],
}
plinth(W, D, hs=(0.2, 0.28))
for key, Fk, half in (('F', F, W / 2), ('B', Bk, W / 2), ('R', R, D / 2), ('L', L, D / 2)):
    stone_wall(Fk, -half + 0.35, half - 0.35, Z0, ZF, LOW[key], thick=0.28)
quoins(W, D, Z0, ZF)
# belt course
for key, Fk, half in (('F', F, W / 2), ('B', Bk, W / 2), ('R', R, D / 2), ('L', L, D / 2)):
    Fk.box('timber_dark', -half - 0.04, half + 0.04, -0.0, 0.1, ZF - 0.02, ZF + 0.18, n=(8, 1, 1), cj=0.12, seed=half)
    # timber upper floor
    core(Fk, -half, half, ZF + 0.16, ze, UP[key])
    siding(Fk, -half + 0.2, half - 0.2, ZF + 0.15 + 0.0, ze, UP[key])
corner_posts(W, D, ZF + 0.15, ze + 0.02, mat='timber_dark', sz=0.2)
for Fk in (R, L):
    za = ze + K * ye
    hole = [win_hole(0, ze + 1.0, 0.75, 1.0)]
    gable_fill(Fk, ye, ze, za, 'lap', holes=hole if Fk is R else [])
    if Fk is R: window(Fk, 0, ze + 1.0, 0.75, 1.0, rows=3, cols=1, shutters=True)
    # collar tie beam
    Fk.box('timber_dark', -ye + 0.4, ye - 0.4, 0, 0.06, ze + 0.05, ze + 0.2)
# windows & doors
for (Fk, key) in ((F, 'F'), (Bk, 'B'), (R, 'R'), (L, 'L')):
    for h in LOW[key]:
        uc, zc = (h[0] + h[1]) / 2, (h[2] + h[3]) / 2
        w, hh = h[1] - h[0], h[3] - h[2]
        if h[2] <= Z0 + 0.01:
            door(Fk, uc, w, hh, mat='paint_door' if Fk is F else 'door_wood', lintel='stone_wall', step=(Fk is not F), reveal=True)
        else:
            window(Fk, uc, zc, w, hh, rows=3 if hh > 1.15 else 2, cols=1, shutters=(Fk is F), flowerbox=(Fk is F), lintel='stone_wall')
    for h in UP[key]:
        uc, zc = (h[0] + h[1]) / 2, (h[2] + h[3]) / 2
        window(Fk, uc, zc, h[1] - h[0], h[3] - h[2], rows=3, cols=1, shutters=(Fk is F), flowerbox=(Fk is F and abs(uc) > 1))
# porch
porch(0.0, 3.8, 1.9, -ye, zdeck=Z0 + 0.02, zr_wall=2.85, zr_front=2.45, steps_w=1.5)
lantern(F, 0.95, 0, 2.0)
# dormers (2 front, 1 back) + roof
dormer(ye - 1.4, -2.2, 1.8, zs, K, K2=0.85, hgt=1.4, window_w=0.8, window_h=0.95, flowerbox=True)
dormer(ye - 1.4, 2.2, 1.8, zs, K, K2=0.85, hgt=1.4, window_w=0.8, window_h=0.95, flowerbox=True)
with placed((0, 0, 0), math.pi):
    dormer(ye - 1.4, 0.0, 1.8, zs, K, K2=0.85, hgt=1.4, window_w=0.8, window_h=0.95)
zr, zs = gable_roof(-W / 2 - 0.15, W / 2 + 0.6, ye, ze, K, oy=0.65, gutters=(-1, 1), exp=0.2, Ls=0.46, wr=(0.24, 0.42), gaps=[(-2.1, 2.1)], colk=1.1)
yo = ye + 0.65
for (x, s) in ((W / 2 - 0.4, -1), (W / 2 - 0.4, 1), (-W / 2 + 0.6, 1)):
    downspout(x, s * (yo + 0.1), zs(yo) - 0.16, s * (ye + 0.06), s)
# big stone chimney on the left gable
chimney(-W / 2 - 0.5, 0.0, 1.2, 2.3, -0.5, 1.5, 'stone', register=False, cap=False)
chimney(-W / 2 - 0.45, 0.0, 0.95, 1.8, 1.3, 3.8, 'stone', register=False, cap=False)
chimney(-W / 2 - 0.42, 0.0, 0.8, 1.45, 3.6, zr + 1.4, 'stone')
# yard
well(6.6, -5.3)
trough(-5.9, -ye - 1.3, 1.9, 0.0)
haystack(-7.2, 1.3, 1.1, 1.9)
hay_bale(-6.7, -1.2, 0.0, 0.9, 0.45, 0.4, 0.3); hay_bale(-6.6, -1.25, 0.4, 0.9, 0.45, 0.4, -0.1)
barrel(3.0, -ye - 0.5, 0.0, 0.3, 0.8); crate(-3.0, -ye - 0.4, 0.0, 0.6, 0.45, 0.4, 0.1)
milk_can(-2.6, -ye - 0.9); milk_can(-2.2, -ye - 0.85); milk_can(-2.4, -ye - 1.2)
woodpile(0.0, ye + 0.05, 0.0, 3.2, 1.4, depth=0.5)
ladder(W / 2 + 0.0, 1.2, 0.0, 3.0, -math.pi / 2) if False else None
stump(-3.5, ye + 1.2)
bucket(2.8, ye + 0.5)

cols = [C(-W / 2 - 0.1, W / 2 + 0.1, -D / 2 - 0.1, D / 2 + 0.1, ze, -0.5), C(-W / 2 - 1.15, -W / 2 - 0.1, -1.2, 1.2, zr + 1.4, -0.5),
        C(-1.9, 1.9, -D / 2 - 1.9, -D / 2, 1.0, 0), C(5.7, 7.5, -6.1, -4.5, 1.0, 0)]
views = {
    'front34': ((-13, -14, 2.8), (0, 0, 3.8), 35),
    'back34': ((13, 14, 3.8), (0, 0, 3.8), 35),
    'front': ((0, -20, 2.2), (0, 0, 4.2), 35),
    'yard': ((10, -11, 2.2), (4, -3, 2.0), 35),
    'porch': ((-3.5, -9.5, 1.8), (0, -4.5, 1.8), 32),
}
finish('house_farm', W, D, ze, zr + 0.07, (0, -D / 2), 'home', '농가', cols, views)
