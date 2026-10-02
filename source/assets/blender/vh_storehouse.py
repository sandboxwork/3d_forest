import sys
sys.path.insert(0, '/shared/river/assets/blender')
from vh_base import *

rng.seed(909)
W, D = 7.0, 6.0
ye = D / 2
FL = 0.8                # floor level (raised)
ze = 3.4
K = 0.68
fr = frames(W, D)
F, Bk, R, L = fr['F'], fr['B'], fr['R'], fr['L']
zr, zs = roof_fn(ze, K, ye)
OPS = {
    'F': [(-0.85, 0.85, FL, FL + 2.05), win_hole(-2.5, FL + 1.5, 0.7, 0.8), win_hole(2.5, FL + 1.5, 0.7, 0.8)],
    'B': [win_hole(-1.6, FL + 1.5, 0.7, 0.8), win_hole(1.6, FL + 1.5, 0.7, 0.8)],
    'R': [win_hole(0.0, FL + 1.5, 0.7, 0.8)],
    'L': [win_hole(0.0, FL + 1.5, 0.7, 0.8)],
}


def staddle(x, y):
    lathe('stone_wall', (x, y, -0.05), [(0, 0.17), (0.05, 0.15), (0.3, 0.115), (0.46, 0.105), (0.5, 0.12)], segs=9, col=tint(1.3, 1.25, 1.15, 0.12), cj=0.15)
    lathe('stone_wall', (x, y, 0.5), [(0, 0.12), (0.02, 0.3), (0.08, 0.34), (0.14, 0.2), (0.17, 0.0)], segs=11, col=tint(1.35, 1.3, 1.2, 0.1), cj=0.12)


# staddle stones + frame under the floor
sxs = [-3.0, -1.0, 1.0, 3.0]
sys_ = [-2.55, 0.0, 2.55]
for x in sxs:
    for y in sys_:
        staddle(x, y)
for y in sys_:
    box('timber_dark', -W / 2 - 0.05, W / 2 + 0.05, y - 0.1, y + 0.1, 0.64, FL - 0.08, n=(8, 1, 1), cj=0.12, seed=y)
for x in sxs:
    box('timber_beam', x - 0.07, x + 0.07, -D / 2 - 0.05, D / 2 + 0.05, FL - 0.08, FL + 0.04, n=(1, 8, 1), cj=0.12, seed=x)
# floor boards visible at the front edge
box('deck_planks', -W / 2 - 0.05, W / 2 + 0.05, -D / 2 - 0.2, D / 2 + 0.05, FL + 0.04, FL + 0.08, n=(8, 6, 1), cj=0.1, skip=('bottom',))
# walls: vertical planks over a frame
for key, Fk, half in (('F', F, W / 2), ('B', Bk, W / 2), ('R', R, D / 2), ('L', L, D / 2)):
    holes = OPS[key]
    core(Fk, -half, half, FL + 0.08, ze, holes)
    vboards(Fk, -half + 0.2, half - 0.2, FL + 0.04, ze, holes, mat='siding_dark', bw=0.22, batten=False, tcol=(1.05, 1.0, 0.95))
    Fk.box('timber_dark', -half - 0.02, half + 0.02, 0.0, 0.1, FL + 0.04, FL + 0.2, n=(6, 1, 1), cj=0.12)
    Fk.box('timber_dark', -half - 0.02, half + 0.02, 0.0, 0.1, ze - 0.2, ze, n=(6, 1, 1), cj=0.12)
    nposts = max(2, int(round(2 * half / 1.8)))
    for i in range(nposts + 1):
        u = -half + 2 * half * i / nposts
        for (c, d) in free_z(u - 0.07, u + 0.07, FL + 0.2, ze - 0.2, holes):
            Fk.box('timber_dark', u - 0.07, u + 0.07, 0.0, 0.07, c, d, n=(1, 1, 3), cj=0.12, seed=u)
corner_posts(W, D, FL + 0.04, ze + 0.02, mat='timber_dark', sz=0.2, proud=0.02)
# gables
for Fk in (R, L):
    gable_fill(Fk, ye, ze, ze + K * ye, 'board', holes=[win_hole(0, ze + 0.9, 0.5, 0.6)] if Fk is R else [])
    if Fk is R: window(Fk, 0, ze + 0.9, 0.5, 0.6, rows=2, cols=1, shutters=False, sill=False)
# windows, loading door
for (Fk, key) in ((F, 'F'), (Bk, 'B'), (R, 'R'), (L, 'L')):
    for h in OPS[key]:
        uc, zc = (h[0] + h[1]) / 2, (h[2] + h[3]) / 2
        w, hh = h[1] - h[0], h[3] - h[2]
        if h[2] <= FL + 0.01:
            door(Fk, uc, w, hh, mat='paint_door', z0=FL, step=False, lintel='timber_beam')
            # wide plank landing + sill
            Fk.box('timber_beam', uc - w / 2 - 0.2, uc + w / 2 + 0.2, 0.0, 0.18, FL - 0.02, FL + 0.06, n=(3, 1, 1), cj=0.1)
        else:
            window(Fk, uc, zc, w, hh, rows=2, cols=1, shutters=True, casing_w=0.07)
# loading stair (front): landing + stringers + treads + rails
lx0, lx1 = -0.95, 0.95
N = 5
rise = (FL + 0.06) / N
y0 = -ye
for i in range(N):
    z_top = rise * (i + 1)
    ytread = y0 - 0.1 - (N - 1 - i) * 0.3
    box('timber_beam', lx0, lx1, ytread - 0.32, ytread, z_top - 0.05, z_top, col=tint(1, 1, 1, 0.1), n=(3, 1, 1), cj=0.06)
    box('timber_dark', lx0 + 0.02, lx1 - 0.02, ytread - 0.26, ytread - 0.02, z_top - 0.12 if False else 0.0, z_top - 0.05) if False else None
for sx in (lx0, lx1):
    a = V3((sx, y0 - 0.1 - 4 * 0.3 - 0.32, 0.0)); b = V3((sx, y0 - 0.1, FL))
    cyl('timber_dark', a + V3((0, 0, 0.05)), b - V3((0, 0, 0.0)), 0.07, segs=5)
    cyl('timber_dark', a + V3((0, 0, 0.0)), a + V3((0, 0, 0.0)) + V3((0, 0, 0.0)), 0.0, segs=3) if False else None
    # handrail
    cyl('timber_beam', V3((sx, y0 - 1.65, 0.95)), V3((sx, y0 - 0.0, FL + 0.9)), 0.035, segs=5)
    cyl('timber_dark', V3((sx, y0 - 1.65, 0.0)), V3((sx, y0 - 1.65, 0.95)), 0.04, segs=5)
    cyl('timber_dark', V3((sx, y0 - 0.15, FL)), V3((sx, y0 - 0.15, FL + 0.9)), 0.04, segs=5)
# roof + hoist hood
dormer(ye + 0.55 - 0.05, 0.0, 1.5, zs, K, K2=0.85, hgt=1.45, window_w=0.9, window_h=0.95, opening=True, ov=0.25)
zr, zs = gable_roof(-W / 2 - 0.55, W / 2 + 0.55, ye, ze, K, oy=0.55, gutters=(), exp=0.15, Ls=0.36, wr=(0.18, 0.32), colk=1.1)
# gutters only outside the hood
# hoist beam out of the hood apex, with pulley, rope and hook
yf = ye + 0.5
zb_ = zs(yf) + 1.45 + 0.1
zhood_top = zs(yf) + 1.45 + 0.85 * (0.75 + 0.25) - 0.05
bx = F.P(0, -0.0, 0)
beam_z = zs(yf) + 1.35
box('timber_beam', -0.08, 0.08, -yf - 1.35, -yf + 1.2, beam_z + 0.1, beam_z + 0.3, n=(1, 6, 1), cj=0.1)
cyl('timber_dark', (0, -yf - 1.2, beam_z + 0.1), (0, -yf - 0.2, beam_z - 0.65), 0.045, segs=5)
pul = V3((0, -yf - 1.2, beam_z - 0.1))
cyl('iron', pul + V3((-0.045, 0, 0)), pul + V3((0.045, 0, 0)), 0.09, segs=14)
cyl('iron', pul + V3((-0.07, 0, 0)), pul + V3((0.07, 0, 0)), 0.018, segs=6)
cyl('rope', pul + V3((0, 0.02, -0.08)), pul + V3((0, 0.02, -2.4)), 0.011, segs=4)
tube('iron', [pul + V3((0, 0.02, -2.4 - 0.12 * math.sin(t))) + V3((0, 0.08 * (1 - math.cos(t)), 0)) for t in [i * 0.5 for i in range(9)]], 0.009, segs=4, pn=(1, 0, 0))
sack(0, -yf - 1.2 + 0.02, 0.0 + 1.55 if False else 1.2, 0.8, col=(1.1, 1.0, 0.9)) if False else None
# chimney-less; add a lightning of mouse guards? (flat discs on the stones are the caps already)
# props: sacks on the landing, barrels, crates, ladder
sack(-0.55, -ye + 0.12, FL + 0.06, 0.9, col=(1.1, 1.05, 0.95)); sack(-0.25, -ye + 0.14, FL + 0.06, 0.85, col=(1.0, 0.95, 0.9))
barrel(-3.7, -ye - 0.35, 0.0, 0.32, 0.85); barrel(3.8, -ye - 0.4, 0.0, 0.32, 0.85)
crate(2.4, -ye - 0.7, 0.0, 0.7, 0.5, 0.45, 0.2); crate(2.45, -ye - 0.7, 0.45, 0.6, 0.45, 0.4, -0.1)
hay_bale(-2.3, -ye - 0.7, 0.0, 0.9, 0.45, 0.4, 0.1)
sack(-3.0, ye + 0.5, 0.0, 1.0); sack(-2.7, ye + 0.45, 0.0, 0.95); sack(-2.85, ye + 0.8, 0.0, 1.0)
woodpile(2.0, ye + 0.05, 0.0, 2.6, 1.3, depth=0.5)
bucket(0.3, ye + 0.5)
handcart(-1.6, -ye - 1.9, 0.5)
barrel(3.2, ye + 0.5, 0.0, 0.3, 0.8)
bush(-4.4, 1.0, 0.6)
bush(4.4, -1.5, 0.55)
# diagonal braces on the gable walls
for Fk, half in ((R, D / 2), (L, D / 2)):
    for sg in (-1, 1):
        pa = Fk.P(sg * (half - 0.35), 0.0, FL + 0.3); pb = Fk.P(sg * (half - 1.4), 0.0, ze - 0.35)
        dv = pb - pa
        perp = dv.cross(Fk.N).normalized()
        obox('timber_dark', pa - perp * 0.06, dv, Fk.N, perp, dv.length, 0.1, 0.12, cj=0.1)

cols = [C(-W / 2 - 0.1, W / 2 + 0.1, -D / 2 - 0.1, D / 2 + 0.1, ze, 0.45), C(-0.95, 0.95, -D / 2 - 1.75, -D / 2 - 0.1, FL, 0)] + \
       [C(x - 0.3, x + 0.3, y - 0.3, y + 0.3, 0.6, 0) for x in sxs for y in sys_ if False]
views = {
    'front34': ((-10.5, -11.5, 2.2), (0, 0, 2.6), 35),
    'back34': ((10, 11, 3.0), (0, 0, 2.6), 35),
    'hoist': ((-3.5, -9.0, 4.0), (0, -3.8, 4.2), 32),
    'stones': ((-6, -5.5, 0.7), (0, 0, 0.6), 35),
    'cart': ((-5.5, -8.5, 1.6), (-1.5, -4.5, 0.8), 32),
}
finish('storehouse', W, D, ze, zr + 0.07, (0, -D / 2), 'store', '창고', cols, views)
