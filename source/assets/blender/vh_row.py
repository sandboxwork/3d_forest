import sys
sys.path.insert(0, '/shared/river/assets/blender')
from vh_base import *

rng.seed(303)
W, D = 15.0, 6.0
ye = D / 2
ze = 5.35
K = 0.55
fr = frames(W, D)
F, Bk, R, L = fr['F'], fr['B'], fr['R'], fr['L']
UC = [-5.0, 0.0, 5.0]
UTINT = [(1.0, 0.86, 0.62), (0.93, 0.76, 0.74), (0.78, 0.88, 0.94)]
DOORM = ['paint_door', 'door_blue', 'door_ochre']
Z_STR = 2.95
fh, uh = (0.0, 0.0)
OPS = {'F': [], 'B': [], 'R': [], 'L': []}
DOORS = []
for i, uc in enumerate(UC):
    OPS['F'] += [(uc - 1.75, uc - 0.75, Z0, Z0 + 2.05), win_hole(uc + 1.0, 1.65, 1.1, 1.3), win_hole(uc - 1.25, 4.25, 0.95, 1.3), win_hole(uc + 1.0, 4.25, 0.95, 1.3)]
    OPS['B'] += [win_hole(uc - 1.0, 1.65, 1.0, 1.2), (-uc + 0.9, -uc + 1.9, Z0, Z0 + 2.05), win_hole(-uc - 0.2 - 0.0, 4.25, 0.95, 1.3), win_hole(-uc + 1.6, 4.25, 0.95, 1.3)]
OPS['B'] = [h for h in OPS['B']]
OPS['R'] = [win_hole(-0.8, 1.65, 0.95, 1.2), win_hole(0.9, 1.65, 0.95, 1.2), win_hole(-0.8, 4.25, 0.95, 1.25), win_hole(0.9, 4.25, 0.95, 1.25)]
OPS['L'] = list(OPS['R'])
plinth(W, D)
# unit-wise plaster tint
for key, Fk, half in (('F', F, W / 2), ('B', Bk, W / 2), ('R', R, D / 2), ('L', L, D / 2)):
    holes = OPS[key]
    if key in ('F', 'B'):
        for i, uc in enumerate(UC):
            ua, ub = (uc - 2.5, uc + 2.5) if key == 'F' else (-uc - 2.5, -uc + 2.5)
            sub = [h for h in holes if h[0] >= ua - 1e-6 and h[1] <= ub + 1e-6]
            t = UTINT[i]
            plaster_wall(Fk, ua, ub, Z0, ze, sub, col=tint(t[0], t[1], t[2], 0.02))
    else:
        plaster_wall(Fk, -half, half, Z0, ze, holes, col=tint(0.95, 0.9, 0.82, 0.02))
# pilasters, string course, cornice, base band
for Fk in (F, Bk):
    for i in range(4):
        u = -7.5 + 5 * i
        a, b = max(-7.5, u - 0.16), min(7.5, u + 0.16)
        Fk.box('paint_trim', a, b, 0, 0.05, Z0, ze, n=(1, 1, 5), cj=0.03)
    Fk.box('paint_trim', -7.5, 7.5, 0, 0.055, Z_STR - 0.08, Z_STR + 0.08, n=(12, 1, 1))
    Fk.prism('paint_trim', [(0, ze - 0.2), (0.12, ze - 0.2), (0.12, ze - 0.14), (0.04, ze - 0.06), (0.04, ze)], -7.5, 7.5)
    Fk.box('paint_trim', -7.5, 7.5, 0, 0.05, Z0, Z0 + 0.14, n=(12, 1, 1))
for Fk in (R, L):
    for sg in (-1, 1):
        Fk.box('paint_trim', sg * 3.0 - 0.14 if False else (-3.0 if sg < 0 else 2.72), (-2.72 if sg < 0 else 3.0), 0, 0.05, Z0, ze, n=(1, 1, 5))
    Fk.box('paint_trim', -3.0, 3.0, 0, 0.055, Z_STR - 0.08, Z_STR + 0.08)
    holes = [win_hole(0, ze + 0.85, 0.7, 0.8)]
    gable_fill(Fk, ye, ze, ze + K * ye, 'lap', holes=holes)
    window(Fk, 0, ze + 0.85, 0.7, 0.8, rows=2, cols=1, shutters=False)
# windows & doors
for (Fk, key) in ((F, 'F'), (Bk, 'B'), (R, 'R'), (L, 'L')):
    for h in OPS[key]:
        uc, zc = (h[0] + h[1]) / 2, (h[2] + h[3]) / 2
        w, hh = h[1] - h[0], h[3] - h[2]
        if h[2] <= Z0 + 0.01:
            if Fk is F:
                idx = min(range(3), key=lambda i: abs(UC[i] - 1.25 - uc))
                door(Fk, uc, w, hh, mat=DOORM[idx], lintel=None, glazed=(idx == 1))
                hood(Fk, uc, 1.45, 2.78, depth=0.8, rise=0.3)
            else:
                door(Fk, uc, w, hh, mat='door_wood', lintel=None)
        else:
            lower = zc < 3.0
            window(Fk, uc, zc, w, hh, rows=3 if hh > 1.15 else 2, cols=1, shutters=(Fk is F), flowerbox=(Fk is F and (lower or rng.random() < 0.4)))
# roof
zr, zs = gable_roof(-W / 2 - 0.4, W / 2 + 0.4, ye, ze, K, oy=0.6, gutters=(-1, 1), wr=(0.22, 0.4), exp=0.18, Ls=0.42)
yo = ye + 0.6
for (x, s) in ((W / 2 - 0.3, -1), (-W / 2 + 0.3, 1), (-2.5, 1), (2.5, -1), (-W / 2 + 0.3, -1), (W / 2 - 0.3, 1)):
    downspout(x, s * (yo + 0.1), zs(yo) - 0.16, s * (ye + 0.06), s)
# chimneys
for i, uc in enumerate(UC):
    chimney(uc + (0.8 if i != 1 else -0.8), 0.0, 0.7, 0.62, ze + 0.2, zr + 1.3, kind='brick')
    flashing(uc + (0.8 if i != 1 else -0.8), 0.0, 0.7, 0.62, zr - K * 0.35 - 0.03)
# props: flower pots at doors, benches, barrels
for i, uc in enumerate(UC):
    ud = uc - 1.25
    pot(ud - 0.95, -ye - 0.55, 0.0)
    pot(ud + 0.95, -ye - 0.55, 0.0) if i == 1 else None
    lantern(F, ud + 0.85, 0, 1.95) if i != 1 else lantern(F, ud + 0.85, 0, 1.95)
bench(UC[0] + 1.0, -ye - 0.35, 0.0, 1.4, 0.0)
barrel(UC[1] + 1.8, -ye - 0.4, 0.0, 0.3, 0.8)
crate(UC[2] + 1.9, -ye - 0.35, 0.0, 0.6, 0.45, 0.4)
bench(UC[2] - 1.6 + 0.0, -ye - 0.35, 0.0, 1.2, 0.0)
barrel(-W / 2 + 0.5, ye + 0.45, 0.0, 0.3, 0.8)
woodpile(2.5, ye + 0.05, 0.0, 2.4, 1.2, depth=0.5)
ladder(W / 2 - 1.5, ye + 0.15, 0.0, 3.4, math.pi) if False else None

cols = [C(-W / 2 - 0.1, W / 2 + 0.1, -D / 2 - 0.1, D / 2 + 0.1, ze, -0.5)]
views = {
    'front34': ((-18, -15, 2.6), (0, 0, 3.0), 35),
    'back34': ((17, 14, 3.6), (0, 0, 3.0), 35),
    'front': ((0, -21, 2.0), (0, 0, 3.0), 35),
    'door': ((-1.5, -7.5, 1.7), (-0.5, -3.1, 2.0), 32),
}
finish('house_row', W, D, ze, zr + 0.07, (UC[0] - 1.25, -D / 2), 'home', '연립주택', cols, views)
