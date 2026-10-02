import sys
sys.path.insert(0, '/shared/river/assets/blender')
from vh_base import *

rng.seed(101)
W, D = 7.0, 6.0
ye = D / 2
ze = 2.85
K = 0.78
fr = frames(W, D)
F, Bk, R, L = fr['F'], fr['B'], fr['R'], fr['L']

OPS = {
    'F': [(-0.5, 0.5, Z0, Z0 + 2.05)] + [win_hole(-2.2, 1.65, 1.0, 1.2), win_hole(2.2, 1.65, 1.0, 1.2)],
    'B': [win_hole(-1.8, 1.65, 1.0, 1.2), win_hole(1.8, 1.65, 1.0, 1.2)],
    'R': [win_hole(-0.6, 1.65, 0.9, 1.1), win_hole(1.1, 1.65, 0.9, 1.1)],
    'L': [win_hole(0.4, 1.65, 0.9, 1.1)],
}
plinth(W, D)
for key, Fk, half in (('F', F, W / 2), ('B', Bk, W / 2), ('R', R, D / 2), ('L', L, D / 2)):
    holes = OPS[key]
    plaster_wall(Fk, -half, half, Z0, ze, holes, col=tint(1, 0.97, 0.9, 0.02))
    halftimber(Fk, -half + 0.1, half - 0.1, Z0, ze - 0.0, holes, spacing=1.45, rails=[2.55], braces=True)
corner_posts(W, D, Z0, ze + 0.02, mat='timber_dark')
# gable ends (siding with attic window)
for Fk in (R, L):
    gable_fill(Fk, ye, ze, ze + K * ye, 'lap', holes=[win_hole(0, ze + 0.85, 0.7, 0.8)])
    window(Fk, 0, ze + 0.85, 0.7, 0.8, rows=2, cols=1, shutters=False)
# windows
for (Fk, ops) in ((F, OPS['F']), (Bk, OPS['B']), (R, OPS['R']), (L, OPS['L'])):
    for h in ops:
        if h[2] <= Z0 + 0.01: continue
        uc, zc = (h[0] + h[1]) / 2, (h[2] + h[3]) / 2
        w, hh = h[1] - h[0], h[3] - h[2]
        window(Fk, uc, zc, w, hh, rows=3 if hh > 1.15 else 2, cols=1, shutters=(Fk is F), flowerbox=(Fk is F))
door(F, 0, 1.0, 2.05, mat='paint_door', lintel='timber_beam')
hood(F, 0, 1.9, 2.75, depth=1.0, rise=0.4)
lantern(F, 0.9, 0, 1.95)
# roof
zr0, zs0 = roof_fn(ze, K, ye)
dormer(ye - 0.95, 2.3, 1.5, zs0, K, K2=0.85, hgt=1.3, window_w=0.7, window_h=0.85, flowerbox=True)
dormer(ye - 0.95, -2.3, 1.5, zs0, K, K2=0.85, hgt=1.3, window_w=0.7, window_h=0.85, flowerbox=True)
zr, zs = gable_roof(-W / 2 - 0.45, W / 2 + 0.45, ye, ze, K, oy=0.55, gutters=(-1, 1))
yo = ye + 0.55
for (x, s) in ((W / 2 - 0.3, -1), (-W / 2 + 0.3, 1)):
    downspout(x, s * (yo + 0.1), zs(yo) - 0.16, s * (ye + 0.06), s)
# chimney through the ridge
chimney(-1.6, 0.0, 0.62, 0.62, ze + 0.3, zr + 1.25, kind='brick')
for sy in (-1, 1):
    pass
flashing(-1.6, 0.0, 0.62, 0.62, zr - K * 0.4 - 0.03)
# props
bench(-1.9, -3.4, 0.0, 1.5, 0.0, back=False)
barrel(2.7, -3.55, 0.0, r=0.3, h=0.8)
bucket(2.15, -3.6)
woodpile(3.45, 0.2, math.pi / 2 * 0 + 0.0, 2.6, 1.3, depth=0.5) if False else None
woodpile(W / 2 + 0.02, 0.4, -math.pi / 2, 2.6, 1.25, depth=0.5)
pot(-0.95, -3.45, 0.0)
garden_bed(-W / 2 - 1.9, -W / 2 - 0.8, -1.4, 1.2)
pot(0.95, -3.45, 0.0)
fence(-W / 2 - 0.6, W / 2 + 0.6, -ye - 2.7, gaps=[(-0.55, 0.55)])
for sx in (-1, 1):
    fy = -ye - 2.7
    F2 = Fr((sx * (W / 2 + 0.6), 0, 0), (0, 1, 0), (1, 0, 0))
    for yy in [fy + 0.15 * i for i in range(1, int(2.5 / 0.15))]:
        box('paint_trim', sx * (W / 2 + 0.6) - 0.012, sx * (W / 2 + 0.6) + 0.012, yy - 0.035, yy + 0.035, 0.0, 0.88)
    for xx in (-W / 2 - 0.6, W / 2 + 0.6):
        pass
bush(-W / 2 - 0.3, -ye - 1.4, 0.55, flowers=True)
bush(W / 2 + 0.3, -ye - 1.4, 0.55, flowers=True)
for xx in (-2.8, -1.7, 1.7, 2.8):
    plant_cluster(xx, -ye - 0.55, 0.0, 0.8, 0.35, nflow=10, leaf=0.1, nleaf=7)

cols = [C(-W / 2 - 0.1, W / 2 + 0.1, -D / 2 - 0.1, D / 2 + 0.1, ze, -0.5)]
views = {
    'front34': ((-10.5, -11, 2.4), (0, 0, 2.5), 35),
    'back34': ((10, 11, 3.2), (0, 0, 2.5), 35),
    'front': ((0, -13, 2.0), (0, 0, 2.6), 35),
    'door': ((1.8, -6.0, 1.5), (0, -3.1, 1.4), 30),
    'roof': ((-6, -6, 6.5), (0, 0, 4.5), 40),
    'garden': ((-7.5, -10.5, 2.2), (0, -4.3, 0.9), 35),
}
finish('house_cottage_a', W, D, ze, zr + 0.07, (0, -D / 2), 'home', '오두막 A', cols, views)
