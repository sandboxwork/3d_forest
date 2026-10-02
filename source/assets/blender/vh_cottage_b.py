import sys
sys.path.insert(0, '/shared/river/assets/blender')
from vh_base import *

rng.seed(202)
W, D = 8.0, 6.5
ye = D / 2
ze = 2.7
K = 0.62
fr = frames(W, D)
F, Bk, R, L = fr['F'], fr['B'], fr['R'], fr['L']
DOORH = 2.05
OPS = {
    'F': [(-0.5, 0.5, Z0, Z0 + DOORH), win_hole(-2.7, 1.55, 1.0, 1.25), win_hole(2.7, 1.55, 1.0, 1.25)],
    'B': [(1.9, 2.8, Z0, Z0 + DOORH), win_hole(-2.4, 1.55, 1.0, 1.25), win_hole(0.0, 1.55, 1.0, 1.25)],
    'R': [win_hole(-1.0, 1.55, 0.9, 1.1), win_hole(1.4, 1.55, 0.9, 1.1)],
    'L': [win_hole(-1.9, 1.55, 0.9, 1.1), win_hole(1.9, 1.55, 0.9, 1.1)],
}
plinth(W, D)
for key, Fk, half in (('F', F, W / 2), ('B', Bk, W / 2), ('R', R, D / 2), ('L', L, D / 2)):
    holes = OPS[key]
    core(Fk, -half, half, Z0, ze, holes)
    siding(Fk, -half + 0.15, half - 0.15, SZ0, ze, holes)
corner_posts(W, D, SZ0, ze + 0.02, mat='paint_trim')
# eave frieze board
for key, Fk, half in (('F', F, W / 2), ('B', Bk, W / 2)):
    Fk.box('paint_trim', -half - 0.02, half + 0.02, 0, 0.03, ze - 0.12, ze + 0.02)
for Fk in (R, L):
    hole = [win_hole(0, ze + 0.78, 0.6, 0.6)] if Fk is R else []
    gable_fill(Fk, ye, ze, ze + K * ye, 'lap', holes=hole)
window(R, 0, ze + 0.78, 0.6, 0.6, rows=2, cols=1, shutters=False)
for (Fk, ops) in ((F, OPS['F']), (Bk, OPS['B']), (R, OPS['R']), (L, OPS['L'])):
    for h in ops:
        uc, zc = (h[0] + h[1]) / 2, (h[2] + h[3]) / 2
        w, hh = h[1] - h[0], h[3] - h[2]
        if h[2] <= Z0 + 0.01:
            door(Fk, uc, w, hh, mat='paint_door' if Fk is F else 'door_wood', step=(Fk is not F), lintel=None)
        else:
            window(Fk, uc, zc, w, hh, rows=3 if hh > 1.15 else 2, cols=1, shutters=(Fk is F or Fk is Bk), flowerbox=(Fk is F))
# roof (left side tight against the stone chimney)
zr, zs = gable_roof(-W / 2 - 0.15, W / 2 + 0.5, ye, ze, K, oy=0.55, gutters=(-1, 1), gaps=[(-1.95, 1.95)])
yo = ye + 0.55
for (x, s) in ((W / 2 - 0.3, -1), (W / 2 - 0.3, 1)):
    downspout(x, s * (yo + 0.1), zs(yo) - 0.16, s * (ye + 0.06), s)
# stone chimney on the left gable
chimney(-W / 2 - 0.4, 0.0, 1.0, 1.9, -0.5, 1.1, 'stone', register=False, cap=False)
chimney(-W / 2 - 0.36, 0.0, 0.72, 1.3, 0.95, zr + 1.05, 'stone')
# porch
porch(0.0, 3.4, 1.9, -ye, zdeck=0.37, zr_wall=2.95, zr_front=2.5, steps_w=1.4)
lantern(F, 1.35, 0, 1.9)
# bench on porch, pots
bench(1.2, -ye - 0.3, 0.37, 1.2, 0.0, back=True)
pot(-1.4, -ye - 0.4, 0.37)
# back door step + props
barrel(-3.2, ye + 0.45, 0.0, 0.3, 0.8)
woodpile(3.45, ye + 0.05, 0.0, 1.1, 1.3, depth=0.5)
stump(-1.0, ye + 1.2)
cyl('door_wood', (-0.98, ye + 1.2, 0.44), (-0.7, ye + 1.2, 1.1), 0.018, segs=6)
prism('iron', [(-0.085, 0.0), (0.085, 0.0), (0.03, 0.11), (-0.03, 0.11)], (-0.98, ye + 1.15, 0.44), V3((1, 0, 0)), V3((0, 0, 1)), V3((0, 1, 0)), 0.1)
garden_bed(W / 2 + 0.7, W / 2 + 1.8, -1.9, 1.4)
bucket(-2.0, -ye - 0.5)

cols = [C(-W / 2 - 0.1, W / 2 + 0.1, -D / 2 - 0.1, D / 2 + 0.1, ze, -0.5), C(-W / 2 - 0.85, -W / 2 - 0.1, -0.95, 0.95, zr + 1.0, -0.5),
        C(-1.8, 1.8, -D / 2 - 1.9, -D / 2, 0.37 + 1.0, 0)]
views = {
    'front34': ((-11, -12, 2.4), (0, 0, 2.5), 35),
    'back34': ((11, 12, 3.2), (0, 0, 2.5), 35),
    'porch': ((-2.5, -9, 1.6), (0, -4, 1.5), 32),
    'chimney': ((-11, 1.5, 2.5), (-4, 0, 2.5), 35),
}
finish('house_cottage_b', W, D, ze, zr + 0.07, (0, -D / 2), 'home', '오두막 B', cols, views)
