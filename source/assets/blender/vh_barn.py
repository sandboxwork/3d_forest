import sys
sys.path.insert(0, '/shared/river/assets/blender')
from vh_base import *

rng.seed(808)
W, D = 12.0, 9.0
ze = 4.3
K = 0.6
hx = W / 2
fr = frames(W, D)
F, Bk, R, L = fr['F'], fr['B'], fr['R'], fr['L']
zr = ze + K * hx + 0.14
DW, DH = 3.6, 3.5        # big door opening
OPS = {
    'F': [(-DW / 2, DW / 2, Z0, Z0 + DH), win_hole(0, 5.35, 1.5, 1.15)],
    'B': [(2.5, 3.5, Z0, Z0 + 2.1), win_hole(-2.5, 2.2, 0.7, 0.7)],
    'R': [win_hole(-2.0, 2.3, 0.7, 0.7), win_hole(2.4, 2.3, 0.7, 0.7)],
    'L': [win_hole(-2.4, 2.3, 0.7, 0.7), win_hole(2.0, 2.3, 0.7, 0.7)],
}
PL = 0.5


def louver_vent(Fk, uc, zc, w, h):
    Fk.box('soot', uc - w / 2, uc + w / 2, -0.12, -0.06, zc - h / 2, zc + h / 2)
    n = int(h / 0.06)
    for i in range(n):
        zb = zc - h / 2 + i * h / n
        Fk.prism('timber_dark', [(-0.1, zb), (0.03, zb + 0.03), (0.03, zb + 0.045), (-0.1, zb + 0.015)], uc - w / 2, uc + w / 2, caps=(False, False))
    Fk.box('timber_dark', uc - w / 2 - 0.05, uc - w / 2, -0.1, 0.05, zc - h / 2 - 0.05, zc + h / 2 + 0.05)
    Fk.box('timber_dark', uc + w / 2, uc + w / 2 + 0.05, -0.1, 0.05, zc - h / 2 - 0.05, zc + h / 2 + 0.05)
    Fk.box('timber_dark', uc - w / 2, uc + w / 2, -0.1, 0.05, zc + h / 2, zc + h / 2 + 0.05)
    Fk.box('timber_dark', uc - w / 2, uc + w / 2, -0.1, 0.07, zc - h / 2 - 0.05, zc - h / 2)


plinth(W, D, hs=(0.2, 0.3))
for key, Fk, half in (('F', F, W / 2), ('B', Bk, W / 2), ('R', R, D / 2), ('L', L, D / 2)):
    holes = OPS[key]
    core(Fk, -half, half, Z0, ze, holes)
    vboards(Fk, -half + 0.2, half - 0.2, Z0 - 0.05, ze, holes, mat='siding_dark', bw=0.26)
    Fk.box('timber_dark', -half, half, 0.0, 0.07, Z0 + 0.02, Z0 + 0.22, n=(8, 1, 1), cj=0.1)           # sill plate
    Fk.box('timber_dark', -half, half, 0.0, 0.08, ze - 0.14, ze + 0.0, n=(8, 1, 1), cj=0.1)          # top plate
    Fk.box('timber_dark', -half, half, 0.0, 0.06, 2.2 if False else 2.15, 2.15 + 0.14, n=(8, 1, 1), cj=0.1) if key in ('R', 'L') else None
corner_posts(W, D, Z0, ze + 0.02, mat='timber_dark', sz=0.24)
# gables
Fk = F
za = ze + K * hx
gable_fill(F, hx, ze, za, 'board', holes=[OPS['F'][1]], col=(1, 1, 1))
gable_fill(Bk, hx, ze, za, 'board', holes=[])
louver_vent(Bk, 0.0, ze + 1.2, 0.8, 0.9)
# big doors framing: heavy posts and header, track rail
F.box('timber_dark', -DW / 2 - 0.3, -DW / 2, -0.08, 0.14, Z0, Z0 + DH + 0.25, n=(1, 1, 5), cj=0.12)
F.box('timber_dark', DW / 2, DW / 2 + 0.3, -0.08, 0.14, Z0, Z0 + DH + 0.25, n=(1, 1, 5), cj=0.12)
F.box('timber_dark', -DW / 2 - 0.3, DW / 2 + 0.3, -0.08, 0.14, Z0 + DH, Z0 + DH + 0.3, n=(8, 1, 1), cj=0.12)
F.box('timber_beam', -DW / 2 - 0.45, DW / 2 + 0.45, -0.1, 0.16, Z0 + DH + 0.3, Z0 + DH + 0.45, n=(8, 1, 1), cj=0.12)
# interior: dark space + hay bales visible through the doors
F.box('soot', -DW / 2 + 0.0, DW / 2, -0.7, -0.5, Z0, Z0 + DH)
F.box('soot', -DW / 2 - 0.02, -DW / 2 + 0.0, -0.7, -0.04, Z0, Z0 + DH)
F.box('soot', DW / 2, DW / 2 + 0.02, -0.7, -0.04, Z0, Z0 + DH)
F.box('soot', -DW / 2, DW / 2, -0.7, -0.04, Z0 + DH - 0.02, Z0 + DH)
F.box('dirt', -DW / 2, DW / 2, -3.0, -0.04, Z0 - 0.02, Z0 + 0.0, n=(4, 4, 1), cj=0.2, skip=('bottom',))
for (u, n, z, rot) in ((-1.1, -1.0, Z0, 0.1), (-0.2, -1.05, Z0, -0.05), (0.7, -1.0, Z0, 0.08), (-0.6, -1.0, Z0 + 0.4, 0.0), (0.3, -1.05, Z0 + 0.4, -0.1), (-1.3, -1.8, Z0, 0.3)):
    p = F.P(u, n, z)
    hay_bale(p.x, p.y, z, 0.9, 0.45, 0.4, rot)
# door leaves (hinged at the outer edges); right leaf ajar
def door_leaf(hinge_x, direction, ang):
    """direction: +1 leaf extends to +x from hinge, -1 to -x"""
    with placed((hinge_x, -D / 2, 0), ang):
        Fl = Fr((0, 0, 0), (direction, 0, 0), (0, -1, 0))
        w = DW / 2 - 0.02
        n0, n1 = -0.06, 0.0
        npl = 8
        for i in range(npl):
            ua = 0.0 + w * i / npl
            ub = ua + w / npl - 0.004
            Fl.box('paint_door', ua, ub, n0, n1 + 0.06, Z0, Z0 + DH - 0.02, col=tint(1, 1, 1, 0.07), cj=0.05, n=(1, 1, 5))
        # frame + X brace on the face
        for (u0, u1) in ((0, 0.18), (w - 0.18, w)):
            Fl.box('paint_door', u0, u1, 0.06, 0.1, Z0, Z0 + DH - 0.02, col=(0.95, 0.95, 0.95), cj=0.04)
        for zz in (Z0, Z0 + DH - 0.2, Z0 + DH / 2 - 0.1):
            Fl.box('paint_door', 0, w, 0.06, 0.1, zz + (0.0 if zz == Z0 else 0.0), zz + 0.2, col=(0.95, 0.95, 0.95), cj=0.04)
        a = Fl.P(0.18, 0.1, Z0 + 0.2); bpt = Fl.P(w - 0.18, 0.1, Z0 + DH / 2 - 0.1)
        for (p0, p1) in ((Fl.P(0.18, 0.1, Z0 + 0.2), Fl.P(w - 0.18, 0.1, Z0 + DH / 2 - 0.1)), (Fl.P(0.18, 0.1, Z0 + DH / 2 + 0.1), Fl.P(w - 0.18, 0.1, Z0 + DH - 0.2)),
                         (Fl.P(w - 0.18, 0.1, Z0 + 0.2), Fl.P(0.18, 0.1, Z0 + DH / 2 - 0.1)), (Fl.P(w - 0.18, 0.1, Z0 + DH / 2 + 0.1), Fl.P(0.18, 0.1, Z0 + DH - 0.2))):
            dv = p1 - p0
            perp = dv.cross(Fl.N).normalized()
            obox('paint_door', p0 - perp * 0.08, dv, Fl.N, perp, dv.length, 0.04, 0.16, col=(0.95, 0.95, 0.95), cj=0.04)
        # iron strap hinges + handle
        for zz in (Z0 + 0.5, Z0 + DH - 0.55):
            Fl.box('iron', 0.0, w * 0.5, 0.1, 0.116, zz - 0.04, zz + 0.04)
        cx = w - 0.3
        Fl.box('iron', cx - 0.03, cx + 0.03, 0.1, 0.12, 1.1, 1.5)
        ring(Fl, cx, 0.125, 1.3, 0.07, 0.01)
door_leaf(-DW / 2, +1, 0.0)
door_leaf(DW / 2, -1, 0.62)
# hay loft hatch: dark interior, hay spilling out, shutter leaves, hoist beam
lh = OPS['F'][1]
uc_h, zc_h = (lh[0] + lh[1]) / 2, (lh[2] + lh[3]) / 2
wl, hl = lh[1] - lh[0], lh[3] - lh[2]
F.box('soot', lh[0], lh[1], -0.6, -0.1, lh[2], lh[3])
F.box('timber_dark', lh[0] - 0.12, lh[1] + 0.12, -0.06, 0.12, lh[3], lh[3] + 0.14, n=(4, 1, 1), cj=0.1)
F.box('timber_dark', lh[0] - 0.12, lh[0], -0.06, 0.12, lh[2], lh[3], n=(1, 1, 2), cj=0.1)
F.box('timber_dark', lh[1], lh[1] + 0.12, -0.06, 0.12, lh[2], lh[3], n=(1, 1, 2), cj=0.1)
F.box('timber_dark', lh[0] - 0.18, lh[1] + 0.18, -0.06, 0.22, lh[2] - 0.12, lh[2], n=(4, 1, 1), cj=0.1)
hay_heap(F, lh[0] + 0.03, lh[1] - 0.03, lh[2] + 0.0, lh[3] - 0.06, n0=-0.5, n1=-0.16, nstrand=70)
for k in range(10):   # strands spilling over the sill
    p = F.P(uc_h + rng.uniform(-0.6, 0.6), 0.1 + rng.uniform(0, 0.15), lh[2] - 0.06)
    d = F.N * rng.uniform(0.05, 0.12) + V3((rng.uniform(-0.05, 0.05), 0, -rng.uniform(0.15, 0.4)))
    cyl('hay', p, p + d, 0.005, segs=3, caps=(False, False), col=tint(1.1, 1.0, 0.7, 0.12))
# hoist beam from apex with pulley and rope
zb_ = za - 0.55
F.box('timber_beam', -0.1, 0.1, -1.55, 0.3, zb_ - 0.0, zb_ + 0.2, n=(1, 6, 1), cj=0.1)
cyl('timber_dark', F.P(0.0, -0.1, zb_ - 0.8), F.P(0.0, -1.4, zb_), 0.05, segs=5)
pul = F.P(0.0, -1.4, zb_ - 0.22)
cyl('iron', pul + V3((-0.05, 0, 0)), pul + V3((0.05, 0, 0)), 0.1, segs=14)
cyl('iron', pul + V3((-0.07, 0, 0)), pul + V3((0.07, 0, 0)), 0.02, segs=6)
cyl('rope', pul + V3((0, 0, -0.1)), pul + V3((0, 0, -1.6)), 0.012, segs=4)
tube('iron', [pul + V3((0, 0, -1.6 - 0.1 * math.sin(t))) + V3((0, 0.1 * (1 - math.cos(t)) * 0 + 0.07 * math.sin(t), 0)) for t in [i * 0.4 for i in range(8)]], 0.01, segs=4, pn=(1, 0, 0))
ladder(-3.3, -D / 2 - 0.12, 0.0, 5.3, 0.0, lean=-0.35, wdt=0.5) if False else None
# side windows
for (Fk, key) in ((R, 'R'), (L, 'L'), (Bk, 'B')):
    for h in OPS[key]:
        uc, zc = (h[0] + h[1]) / 2, (h[2] + h[3]) / 2
        if h[2] <= Z0 + 0.01:
            door(Fk, uc, h[1] - h[0], h[3] - h[2], mat='door_wood', step=False, lintel='timber_beam')
        else:
            window(Fk, uc, zc, h[1] - h[0], h[3] - h[2], rows=2, cols=1, shutters=True, casing_w=0.07)
# roof: ridge along Y (rotated), big shingles
with placed((0, 0, 0), math.pi / 2):
    zr_, zs_ = gable_roof(-D / 2 - 0.55, D / 2 + 0.55, hx, ze, K, oy=0.7, gutters=(-1, 1), exp=0.21, Ls=0.48, wr=(0.26, 0.46), colk=1.1)
# cupola on the ridge
cy_c = 0.5
box('timber_dark', -0.5, 0.5, cy_c - 0.5, cy_c + 0.5, zr - 0.2, zr + 0.2, n=(2, 2, 1), cj=0.1)
for sd in range(4):
    with placed((0, cy_c, 0), sd * math.pi / 2):
        Fc = Fr((0, -0.5, 0), (1, 0, 0), (0, -1, 0))
        Fc.box('timber_dark', -0.5, 0.5, 0, 0.04, zr + 0.2, zr + 0.28)
        louver_vent(Fc, 0.0, zr + 0.65, 0.62, 0.55)
        Fc.box('timber_dark', -0.5, -0.43, -0.02, 0.06, zr + 0.2, zr + 1.05)
        Fc.box('timber_dark', 0.43, 0.5, -0.02, 0.06, zr + 0.2, zr + 1.05)
pyramid_roof(0, cy_c, 0.65, 0.65, zr + 1.05, zr + 1.95, exp=0.12, Ls=0.26, wr=(0.14, 0.24), overhang=0.12)
cyl('iron', (0, cy_c, zr + 1.95), (0, cy_c, zr + 2.5), 0.015, segs=5)
blob('brass', (0, cy_c, zr + 2.1), 0.05, rows=3, segs=8)
# downspout stand-in: rain barrels at the corners
barrel(-W / 2 + 0.7, -D / 2 - 0.5, 0.0, 0.32, 0.85)
barrel(W / 2 - 0.7, -D / 2 - 0.5, 0.0, 0.32, 0.85)
# yard: hay bales, pitchforks, wheel, haystack, cart bits
for (x, y, z, r) in ((W / 2 + 0.7, -2.2, 0.0, 0.1), (W / 2 + 0.7, -1.2, 0.0, -0.05), (W / 2 + 0.7, -0.2, 0.0, 0.08), (W / 2 + 0.7, -1.7, 0.4, 0.0), (W / 2 + 0.75, -0.7, 0.4, 0.12)):
    hay_bale(x, y, z, 0.9, 0.45, 0.4, r + math.pi / 2)
haystack(-W / 2 - 1.5, 1.0, 1.0, 1.7)
# pitchfork leaning on the wall
with placed((-W / 2 - 0.15, -2.8, 0.0), 0.0):
    cyl('door_wood', (0, 0, 0.0), (0.15, 0, 1.75), 0.018, segs=5)
    for k in (-1, 0, 1):
        cyl('iron', (0.15 + 0.0, k * 0.05, 1.75), (0.17, k * 0.05, 2.1), 0.006, segs=4)
    box('iron', 0.13, 0.19, -0.06, 0.06, 1.72, 1.77)
# cart wheel against the front wall
with placed((-4.6, -D / 2 - 0.12, 0.0), 0.0):
    wc = V3((0, 0, 0.55))
    tube('iron', [wc + V3((0.52 * math.cos(t), 0.0, 0.52 * math.sin(t))) for t in [i * 2 * math.pi / 20 for i in range(20)]], 0.018, segs=5, closed=True, pn=(0, 1, 0))
    tube('timber_dark', [wc + V3((0.46 * math.cos(t), 0.0, 0.46 * math.sin(t))) for t in [i * 2 * math.pi / 14 for i in range(14)]], 0.035, segs=5, closed=True, pn=(0, 1, 0))
    for k in range(8):
        a = k * math.pi / 4
        cyl('timber_dark', wc, wc + V3((0.45 * math.cos(a), 0, 0.45 * math.sin(a))), 0.02, segs=5)
    cyl('timber_dark', wc + V3((0, -0.05, 0)), wc + V3((0, 0.06, 0)), 0.065, segs=8)
bucket(3.8, -D / 2 - 0.4)

cols = [C(-W / 2 - 0.1, W / 2 + 0.1, -D / 2 - 0.1, D / 2 + 0.1, ze, -0.5), C(W / 2 + 0.25, W / 2 + 1.2, -2.7, 0.3, 0.9, 0), C(-W / 2 - 2.6, -W / 2 - 0.4, -0.7, 2.7, 1.8, 0)]
views = {
    'front34': ((-14, -14, 2.8), (0, 0, 3.4), 35),
    'back34': ((15, 14, 4.0), (0, 0, 3.4), 35),
    'front': ((0, -21, 2.0), (0, 0, 3.8), 35),
    'doors': ((2.5, -10, 2.0), (0, -4.5, 2.2), 32),
    'loft': ((-3.5, -9, 5.6), (0, -4.5, 5.4), 32),
}
finish('barn', W, D, ze, zr + 2.5, (0, -D / 2), 'barn', '헛간', cols, views)
