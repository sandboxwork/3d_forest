import sys
sys.path.insert(0, '/shared/river/assets/blender')
from vh_base import *

rng.seed(1010)
W, D = 8.0, 14.0
NY0, NY1 = -2.6, 7.0                 # nave y range
NCY = (NY0 + NY1) / 2
NL = NY1 - NY0
TW, TY0, TY1 = 5.0, -7.0, -2.4       # tower
TCY = (TY0 + TY1) / 2
TD = TY1 - TY0
ze = 4.7
K = 0.9
hx = W / 2
ZT = 10.6                            # tower top (spire base)
frN = frames(W, NL, cy=NCY)
frT = frames(TW, TD, cy=TCY)
NF, NB, NR, NL_ = frN['F'], frN['B'], frN['R'], frN['L']
TF, TB, TR, TL = frT['F'], frT['B'], frT['R'], frT['L']
zr = ze + K * hx + 0.14

# --- windows layout (y positions of lancets / buttresses along the nave)
WY = [-0.6, 2.0, 4.6]
BY = [0.7, 3.3, 5.9]
WL_W, WL_Z0, WL_ZS = 0.95, 1.5, 3.0
holes_side = [(y - NCY - WL_W / 2, y - NCY + WL_W / 2, WL_Z0, WL_ZS + 0.866 * WL_W) for y in WY]
# right frame u = y - NCY ; left frame u = -(y - NCY)
holes_R = holes_side
holes_L = [(-h[1], -h[0], h[2], h[3]) for h in holes_side]

# plinths
with placed((0, 0, 0)):
    plinth(W, NL, ztop=Z0, out=0.14, skip=('F',)) if False else None
with placed((0, NCY, 0)):
    plinth(W, NL, out=0.12, hs=(0.22, 0.3), skip=('F',))
with placed((0, TCY, 0)):
    plinth(TW, TD, out=0.14, hs=(0.22, 0.3), skip=('B',))
# nave walls
stone_wall(NR, -NL / 2 + 0.3, NL / 2 - 0.3, Z0, ze, holes_R, thick=0.4, hs=(0.28, 0.4), ws=(0.5, 0.95))
stone_wall(NL_, -NL / 2 + 0.3, NL / 2 - 0.3, Z0, ze, holes_L, thick=0.4, hs=(0.28, 0.4), ws=(0.5, 0.95))
with placed((0, NCY, 0)):
    quoins(W, NL, Z0, ze, sz=0.5)
# nave back gable
stone_wall(NB, -hx + 0.3, hx - 0.3, Z0, ze, [], thick=0.4, hs=(0.28, 0.4), ws=(0.5, 0.95))
gable_fill(NB, hx, ze, ze + K * hx, 'stone', holes=[(-0.55, 0.55, ze + 1.2, ze + 2.3)])
round_window(NB, 0, ze + 1.75, 0.55)
# nave front wall remnants beside the tower
stone_wall(NF, -hx + 0.3, hx - 0.3, Z0, ze, [], thick=0.4, hs=(0.28, 0.4), ws=(0.5, 0.95))
gable_fill(NF, hx, ze, ze + K * hx, 'stone')
# nave lancets
for (Fk, hl) in ((NR, holes_R), (NL_, holes_L)):
    for h in hl:
        lancet(Fk, (h[0] + h[1]) / 2, WL_W, WL_Z0, WL_ZS)
# buttresses (stepped), placed on both long walls
for y in BY + [NY0 + 0.35, NY1 - 0.35]:
    for sx in (-1, 1):
        x_out = sx * hx
        box('stone_wall', min(x_out - 0.05, x_out + sx * 0.62), max(x_out - 0.05, x_out + sx * 0.62), y - 0.3, y + 0.3, -0.45, 2.7, n=(2, 2, 6), cj=0.08, col=(1.25, 1.2, 1.15))
        box('stone_wall', min(x_out - 0.05, x_out + sx * 0.4), max(x_out - 0.05, x_out + sx * 0.4), y - 0.24, y + 0.24, 2.7, 4.05, n=(2, 2, 4), cj=0.08, col=(1.3, 1.25, 1.2))
        # sloped cap
        Fb = Fr((x_out, y, 0), (0, 1, 0), (sx, 0, 0))
        Fb.prism('stone_wall', [(-0.05, 4.05), (0.4, 4.05), (-0.05, 4.4)], -0.24, 0.24, col=(1.35, 1.3, 1.25))
        box('stone_wall', min(x_out - 0.05, x_out + sx * 0.66), max(x_out - 0.05, x_out + sx * 0.66), y - 0.34, y + 0.34, 2.64, 2.72, cj=0.06, col=(1.4, 1.35, 1.3))
# eaves course (stone corbel table)
for sx in (-1, 1):
    box('stone_wall', sx * hx - 0.1 if sx < 0 else sx * hx - 0.1, sx * hx + 0.14 if sx > 0 else sx * hx + 0.1, NY0, NY1, ze - 0.2, ze, n=(1, 8, 1), cj=0.08, col=(1.3, 1.25, 1.2)) if False else None
# --- tower
HT_F = [(-0.9, 0.9, Z0, 2.25 + 0.866 * 1.8)]          # arched door (w=1.8)
stone_wall(TF, -TW / 2 + 0.3, TW / 2 - 0.3, Z0, ZT, [HT_F[0], (-0.5, 0.5, 6.2 - 0.5, 6.2 + 0.5)] + [(-0.5, 0.5, 8.0, 8.0 + 0.9 + 0.866 * 1.0 + 0.1)], thick=0.45, hs=(0.3, 0.45), ws=(0.55, 1.0), dk=1.0)
# side faces of the tower (visible part only: y from -7.0 to -2.6)
side_holes = [(-0.6, 0.6, 8.0, 8.0 + 0.9 + 0.866 * 1.2 + 0.1)]
for (Fk) in (TR, TL):
    stone_wall(Fk, -TD / 2 + 0.3, TD / 2 - 0.3, Z0, ZT, side_holes + [(-0.2, 0.2, 5.4, 6.7)], thick=0.45, hs=(0.3, 0.45), ws=(0.55, 1.0))
stone_wall(TB, -TW / 2 + 0.3, TW / 2 - 0.3, 5.0, ZT, [(-0.5, 0.5, 8.0, 9.2)], thick=0.45, hs=(0.3, 0.45), ws=(0.55, 1.0))
with placed((0, TCY, 0)):
    quoins(TW, TD, Z0, ZT, sz=0.55, th=0.32)
# tower string courses and corner buttresses
for (Fk, half) in ((TF, TW / 2), (TR, TD / 2), (TL, TD / 2), (TB, TW / 2)):
    for zc in (5.0, 7.6, ZT - 0.15):
        Fk.box('stone_wall', -half - 0.1, half + 0.1, 0.0, 0.12, zc, zc + 0.14, n=(8, 1, 1), cj=0.06, col=(1.4, 1.35, 1.3))
for sx in (-1, 1):
    box('stone_wall', sx * (TW / 2) - 0.0 if sx > 0 else sx * (TW / 2) - 0.6, sx * (TW / 2) + 0.6 if sx > 0 else sx * (TW / 2) + 0.0, TY0 - 0.6, TY0 + 0.0, -0.45, 4.2, n=(2, 2, 5), cj=0.08, col=(1.28, 1.22, 1.18)) if False else None
# tower: door, windows
arch_surround(TF, 0, 1.8, Z0, 2.25, ring_w=0.22, out=0.07)
# door leaves following the arch
def arch_door():
    w, zsp, z0 = 1.8, 2.25, Z0
    F = TF
    npl = 14
    inner = w - 0.12
    for i in range(npl):
        ua = -inner / 2 + inner * i / npl
        ub = ua + inner / npl - 0.004
        def post(v, i_, j_, k_, F=F):
            if k_ == 4:
                u = (v.co - F.O).dot(F.U)
                v.co.z = arch_z(u, w, zsp) - 0.05
        F.box('paint_door', ua, ub, -0.18, -0.12, z0, z0 + 1.0, col=tint(1, 1, 1, 0.07), cj=0.04, n=(1, 1, 4), post=post)
    F.box('soot', -0.006, 0.006, -0.19, -0.11, z0 + 0.03, z0 + 2.2)
    for zz in (z0 + 0.5, z0 + 1.6):
        for sx in (-1, 1):
            F.box('iron', 0 if sx > 0 else -0.8, 0.8 if sx > 0 else 0, -0.12, -0.104, zz - 0.04, zz + 0.04)
    for sx in (-1, 1):
        ring(F, sx * 0.16, -0.11, 1.15, 0.07, 0.01)
        F.box('iron', sx * 0.16 - 0.05, sx * 0.16 + 0.05, -0.115, -0.105, 1.05, 1.25)
    # inner dark behind + threshold
    F.poly('soot', arch_outline(F, 0, w, z0, zsp, 0.0), -0.3, -0.2)
    F.box('stone_foundation', -0.95, 0.95, -0.2, 0.25, z0 - 0.04, z0 + 0.03, col=(1.3, 1.25, 1.2))
arch_door()
stone_steps(TF, 0.0, 2.8, nsteps=3, rise=0.15, tread=0.36, ztop=Z0)
lantern(TF, -1.5, 0, 1.8)
lantern(TF, 1.5, 0, 1.8)
round_window(TF, 0, 6.2, 0.5)
# tower slit windows (sides)
for Fk in (TR, TL):
    lancet(Fk, 0.0, 0.4, 5.4, 6.2, sill=True) if False else None
# belfry louvered arches
def belfry(Fk, uc, w=1.0, z0=8.0, zsp=8.9):
    arch_surround(Fk, uc, w, z0, zsp, ring_w=0.16, out=0.05)
    ztop = zsp + 0.866 * w
    Fk.poly('soot', arch_outline(Fk, uc, w, z0, zsp, 0.0), -0.45, -0.2)
    z = z0 + 0.1
    while z < ztop - 0.15:
        halfw = w / 2 - 0.0 if z <= zsp else (arch_pts(w, zsp)[0][0] if False else None)
        if z <= zsp:
            ua, ub = uc - w / 2 + 0.03, uc + w / 2 - 0.03
        else:
            zz = z - zsp
            if zz >= 0.866 * w - 0.03: break
            # left arc u at height z : u = w/2 - sqrt(w^2 - zz^2)  relative to uc+... (centre at +w/2)
            d = math.sqrt(max(0.0, w * w - zz * zz))
            ua = uc + w / 2 - d + 0.04
            ub = uc - w / 2 + d - 0.04
        if ub - ua > 0.08:
            Fk.prism('timber_dark', [(-0.17, z), (0.0, z + 0.07), (0.0, z + 0.1), (-0.17, z + 0.03)], ua, ub, caps=(False, False))
        z += 0.12
    reg_window(Fk, uc, (z0 + ztop) / 2) if False else None
belfry(TF, 0.0)
belfry(TB, 0.0)
belfry(TR, 0.0, w=1.2, z0=8.0, zsp=8.9) if False else None
for Fk in (TR, TL):
    belfry(Fk, 0.0, w=1.2, z0=8.0, zsp=8.9)
# small lancet slits on the tower side, stage 2
for Fk in (TR, TL):
    Fk.box('soot', -0.1, 0.1, -0.3, -0.1, 5.4, 6.4)
    Fk.box('stone_wall', -0.2, 0.2, -0.2, 0.05, 5.3, 5.4, col=(1.4, 1.35, 1.3))
    Fk.box('stone_wall', -0.2, -0.1, -0.2, 0.05, 5.4, 6.7, col=(1.4, 1.35, 1.3))
    Fk.box('stone_wall', 0.1, 0.2, -0.2, 0.05, 5.4, 6.7, col=(1.4, 1.35, 1.3))
    Fk.box('stone_wall', -0.2, 0.2, -0.2, 0.05, 6.4, 6.7, col=(1.4, 1.35, 1.3))
    Fk.box('window_glow', -0.1, 0.1, -0.12, -0.1, 5.4, 6.4)
    reg_window(Fk, 0.0, 5.9)
# --- roofs
with placed((0, NCY, 0), math.pi / 2):
    zr_, zs_ = gable_roof(-NL / 2 - 0.1, NL / 2 + 0.45, hx, ze, K, oy=0.6, gutters=(-1, 1), mat='roof_slate', exp=0.2, Ls=0.45, wr=(0.28, 0.44), colk=1.2, barge=True)
# corbel/cornice stone course under the tower spire
for (Fk, half) in ((TF, TW / 2), (TR, TD / 2), (TL, TD / 2), (TB, TW / 2)):
    Fk.box('stone_wall', -half - 0.18, half + 0.18, 0.0, 0.2, ZT, ZT + 0.16, n=(8, 1, 1), cj=0.06, col=(1.4, 1.35, 1.3))
with placed((0, TCY, 0)):
    pyramid_roof(0, 0, TW / 2 + 0.25, TD / 2 + 0.25, ZT + 0.12, ZT + 6.3, mat='roof_slate', exp=0.2, Ls=0.45, wr=(0.26, 0.42), colk=1.2, overhang=0.12, deck_t=0.1)
    zt = ZT + 6.4
    cyl('iron', (0, 0, zt - 0.1), (0, 0, zt + 1.25), 0.02, segs=6)
    blob('brass', (0, 0, zt + 0.75), 0.09, rows=3, segs=8)
    blob('brass', (0, 0, zt + 1.28), 0.06, rows=3, segs=8)
    Fv = Fr((0, 0, 0), (1, 0, 0), (0, -1, 0))
    Fv.poly('iron', [(-0.55, zt + 1.0 - 0.015), (0.35, zt + 1.0 - 0.015), (0.35, zt + 1.0 - 0.075), (0.62, zt + 1.0), (0.35, zt + 1.0 + 0.075), (0.35, zt + 1.0 + 0.015), (-0.55, zt + 1.0 + 0.015)], -0.006, 0.006)
    Fv.poly('iron', [(-0.55, zt + 1.0 + 0.015), (-0.7, zt + 1.0 + 0.15), (-0.38, zt + 1.0 + 0.15), (-0.28, zt + 1.0 + 0.015)], -0.006, 0.006)
    Fv.poly('iron', [(-0.55, zt + 1.0 - 0.015), (-0.7, zt + 1.0 - 0.15), (-0.38, zt + 1.0 - 0.15), (-0.28, zt + 1.0 - 0.015)], -0.006, 0.006)
# flashing where the nave roof meets the tower
# downspouts
yo_ = hx + 0.6
for (x, s) in ((hx + 0.05, 1), (-hx - 0.05, -1)):
    pass
# props
bush(-4.9, 1.0, 0.7, flowers=True); bush(4.9, 3.9, 0.8, flowers=False); bush(-4.8, 5.4, 0.6); bush(4.8, -0.2, 0.6, flowers=True)
bench(-3.5, -7.6, 0.0, 1.6, 0.0, back=True)
bench(3.5, -7.6, 0.0, 1.6, 0.0, back=True)
barrel(4.4, -6.6, 0.0, 0.3, 0.8)
# grave-free yard: low stone border
cols = [C(-hx - 0.1, hx + 0.1, NY0, NY1 + 0.1, ze, -0.5), C(-TW / 2 - 0.1, TW / 2 + 0.1, TY0 - 0.1, TY1, ZT, -0.5), C(-1.4, 1.4, TY0 - 1.2, TY0 - 0.1, 0.45, 0)]
views = {
    'front34': ((-19, -30, 5.0), (0, -1.5, 8.0), 35),
    'back34': ((14, 22, 4.0), (0, 0, 4.8), 35),
    'front': ((0, -34, 3.0), (0, 0, 7.5), 35),
    'door': ((-2.5, -12.5, 2.0), (0, -7.0, 2.4), 32),
    'tower': ((-6, -14, 9.0), (0, -4.7, 9.0), 35),
    'side': ((16, 1, 2.4), (0, 1.5, 4.0), 35),
}
finish('church', W, D, ze, ZT + 6.4 + 1.5, (0, TY0), 'church', '교회', cols, views)
