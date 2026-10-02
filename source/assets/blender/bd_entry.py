"""Entryway by the front door: coat rack with cloth-simulated coats/scarf, hats, boot tray + boots, umbrella stand, console shelf with
keys/mail/lantern, welcome mat, hat rail. Door path x in [-0.6, 0.6] stays clear (nothing but the flat mat)."""
from bd_lib import *
from bd_hw import *
from bd_cloth import *
import bd_garment as G
import bd_items as I
from bd_furn3 import wall_shelf

GLY = {
    'W': ["X...X", "X...X", "X...X", "X.X.X", "X.X.X", "XX.XX", "X...X"],
    'E': ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "XXXXX"],
    'L': ["X....", "X....", "X....", "X....", "X....", "X....", "XXXXX"],
    'C': [".XXXX", "X....", "X....", "X....", "X....", "X....", ".XXXX"],
    'O': [".XXX.", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    'M': ["X...X", "XX.XX", "X.X.X", "X.X.X", "X...X", "X...X", "X...X"],
}


def welcome_mat(cx, cy, W=0.9, D=0.52):
    """coir mat: woven slab with border stripes, bevelled edge and raised WELCOME lettering"""
    f = Fr((cx, cy, F), 0, F)
    f.box(M['burlap'], (0, 0, 0.0095), (W, D, 0.019), bev=0.006, seg=2, col=(0.72, 0.56, 0.38), g=0, skip_down=True)
    # border rope (raised tube loop)
    pts = []
    rr = 0.035
    for (cxx, cyy, a0) in ((W / 2 - rr - 0.03, D / 2 - rr - 0.03, 0), (-W / 2 + rr + 0.03, D / 2 - rr - 0.03, 90), (-W / 2 + rr + 0.03, -D / 2 + rr + 0.03, 180), (W / 2 - rr - 0.03, -D / 2 + rr + 0.03, 270)):
        for i in range(7):
            a = math.radians(a0 + 90 * i / 6)
            pts.append(Vector((cxx + rr * math.cos(a), cyy + rr * math.sin(a), 0.02)))
    f.tube(M['rug'], pts, 0.006, seg=6, col=(0.3, 0.2, 0.14), closed=True)
    # lettering
    cell = 0.0105
    gap = 0.0125
    x0 = -(6 * 5 * cell + 5 * 0.012) / 2
    for li, ch in enumerate('WELCOM' + 'E'):
        if li == 6:
            pass
    word = 'WELCOME'
    total = len(word) * 5 * cell + (len(word) - 1) * 0.01
    x = -total / 2
    for ch in word:
        g = GLY.get(ch) or GLY['E']
        for ry, row in enumerate(g):
            for rx, v in enumerate(row):
                if v == 'X':
                    f.box(M['rug'], (x + rx * cell + cell / 2, (3 - ry) * cell + 0.0, 0.0215), (cell * 0.95, cell * 0.95, 0.005), bev=0.0008, col=(0.22, 0.15, 0.1), g=0)
        x += 5 * cell + 0.01
    return f


def coat_rack(pos, rot=0):
    f = Fr(pos, rot, F)
    mat = M['wood_dark']
    col = (1.0, 0.92, 0.85)
    # base: turned foot + four curved legs
    f.lathe(mat, (0, 0, 0), profile_pts([(0.0005, 0.0), (0.07, 0.0), (0.075, 0.02), (0.05, 0.05), (0.04, 0.12)], 3), seg=20, cap=False, col=col)
    for k in range(4):
        a = k * TAU / 4 + math.pi / 4
        path = []
        for t in np.linspace(0, 1, 10):
            r = 0.04 + 0.19 * t
            path.append(Vector((math.cos(a) * r, math.sin(a) * r, 0.14 * (1 - t) ** 1.6 + 0.02 - 0.0 + 0.0)))
        f.tube(mat, path, [0.028 - 0.016 * t for t in np.linspace(0, 1, 10)], seg=10, col=col, flat=(1.0, 0.8))
        f.sphere(mat, (math.cos(a) * 0.235, math.sin(a) * 0.235, 0.022), 0.017, seg=10, col=col)
    # post (turned)
    post_prof = profile_pts([(0.0005, 0.1), (0.03, 0.1), (0.034, 0.14), (0.026, 0.2), (0.022, 0.4), (0.026, 0.7), (0.034, 0.76), (0.026, 0.8), (0.02, 0.9), (0.02, 1.2), (0.026, 1.3), (0.021, 1.38), (0.019, 1.5),
                             (0.027, 1.58), (0.02, 1.64), (0.034, 1.71), (0.04, 1.76), (0.03, 1.81), (0.016, 1.84), (0.0005, 1.86)], 3)
    f.lathe(mat, (0, 0, 0), post_prof, seg=18, cap=False, col=col)
    # pegs: two tiers, each a turned peg angled up, ending in a knob
    tiers = [(1.50, [10, 100, 190, 280]), (1.70, [55, 145, 235, 325])]
    pegs = []
    for z, angs in tiers:
        for a_ in angs:
            a = math.radians(a_)
            d = Vector((math.cos(a), math.sin(a), 0))
            p0 = Vector((0, 0, z)) + d * 0.02
            dd = (d * math.cos(math.radians(22)) + Vector((0, 0, math.sin(math.radians(22))))).normalized()
            L = 0.145
            pts = [p0 + dd * (L * t) for t in np.linspace(0, 1, 7)]
            f.tube(mat, pts, [0.0095, 0.0095, 0.0085, 0.0085, 0.0095, 0.012, 0.0125], seg=10, col=col)
            f.sphere(mat, pts[-1] + dd * 0.004, 0.0145, seg=12, col=(1.1, 1.0, 0.92))
            pegs.append((z, a_, p0 + dd * L * 0.78))
    collider_f(f, 0.5, 0.5, F + 1.88, name='coat_rack')
    return f, pegs


def hang_coat(rackf, peg, name, sp, hood=False):
    """put a cloth-simulated coat (on a wooden hanger) on a rack peg. peg=(z,angle,local point)"""
    z, a_, p = peg
    pos = rackf.p(p)
    # frame: shoulder line tangent to the rack (perpendicular to the peg direction); garment front faces away from the post
    fg = Fr(pos + Vector((0, 0, 0.03)), rackf.rot + a_ - 90 + 90 * 0, pos.z + 0.03)
    # garment frame y(front) must point radially outward: frame +y local -> rotate so +y = peg dir.  Fr rot r maps local +y to (-sin r, cos r); want (cos a, sin a) => r = a - 90... -> rot=a_-90
    fg = Fr(pos + Vector((0, 0, 0.03)), rackf.rot + a_ - 90, pos.z + 0.03)
    g = G.body_sim(name, 'coat', hang_h=sp['hang'], sh_w=sp['sh'], hem_scale=sp['hem'], phase=sp['phase'], amp=0.1, hb=sp['hb'])
    G.put_garment(fg, g, M[sp['mat']], cfn=fab(sp['col'], 0.08, 14, hash(name) % 7))
    G.hanger(fg, (0, 0, 0.0), sh_w=sp['sh'] * 1.02)
    sls = []
    for side in (-1, 1):
        sl = G.sleeve_sim(name + ('_sl%d' % side), side, g['v'], g['f'], sh_w=sp['sh'], length=sp['hang'] * 0.58, r0=0.045, r1=0.034)
        G.put_garment(fg, sl, M[sp['mat']], cfn=fab(sp['col'], 0.08, 14, hash(name) % 7 + 3))
        sls.append(sl)
    G.details(fg, g, sls, M[sp['mat']], sp['col'], pockets=True)
    G.buttons(fg, g, 5, x=0.0, z0=0.1, z1=sp['hang'] * 0.65, col=(0.12, 0.09, 0.07), r=0.011)
    # collar: rolled tube around the neckline
    v = g['v']
    ring = v[:18]
    G.collar = None
    pts = [Vector(q) + Vector((0, 0.0, 0.006)) for q in ring] + [Vector(ring[0]) + Vector((0, 0, 0.006))]
    fg.tube(M[sp['mat']], pts, 0.014, seg=8, col=tuple(c * 0.85 for c in sp['col']), closed=False, caps=False)
    return fg


def scarf_on_peg(rackf, peg, name='scarf', l1=0.5, l2=0.82, W=0.15):
    """wool scarf thrown over a peg (cloth sim), two ends of different length"""
    z, a_, p = peg
    pos = rackf.p(p)
    a = math.radians(rackf.rot + a_)
    d = Vector((math.cos(a), math.sin(a), 0))       # peg direction
    t = Vector((-math.sin(a), math.cos(a), 0))      # across the peg
    rr = 0.026
    arc = math.pi * rr
    L = l1 + arc + l2
    nx, ny = 6, 46
    verts = []
    for j in range(ny + 1):
        s = L * j / ny
        if s < l1:
            tt, zz = -rr, -(l1 - s)
        elif s < l1 + arc:
            ang = math.pi - (s - l1) / rr
            tt, zz = rr * math.cos(ang), rr * math.sin(ang)
        else:
            tt, zz = rr, -(s - l1 - arc)
        for i in range(nx + 1):
            w = -W / 2 + W * i / nx
            verts.append(tuple(pos + d * (w - 0.055) + t * tt + Vector((0, 0, zz + 0.004))))
    verts = np.array(verts, np.float32)
    faces = []
    for j in range(ny):
        for i in range(nx):
            k = j * (nx + 1) + i
            faces.append((k, k + 1, k + nx + 2, k + nx + 1))
    uvs = np.array([(W * (k % (nx + 1)) / nx, L * (k // (nx + 1)) / ny) for k in range(len(verts))], np.float32)
    Mx = Matrix.Translation(pos + d * (-0.055)) @ Matrix.Rotation(a, 4, 'Z')
    cols = [cyl_collider(None, 0.0125, 0.16, axis='x', Mx=Mx)]
    res = simulate('bd_' + name, verts, faces, frames=60, colliders=cols, preset='silk', collision_dist=0.006, damping_scale=2.0)
    for c in cols:
        c.free()
    bm2 = solid_bm(res, faces, uvs, 0.007, 0.0)
    put(M['wool'], bm2, Matrix.Identity(4), cfn=lambda q: (0.62, 0.2, 0.18) if int(abs(q.z) * 100 / 1.0) % 14 < 9 else (0.9, 0.82, 0.62), skip_down=False)
    bm2.free()
    # fringe at both ends
    for j in (0, ny):
        for i in range(0, nx + 1):
            q = Vector(res[j * (nx + 1) + i])
            sg = 1 if j == 0 else 1
            tube(M['wool'], [q, q + Vector((0, 0, -0.025)), q + Vector((0.004, 0, -0.045))], 0.0016, seg=4, col=(0.9, 0.82, 0.62), caps=False)


def hat_felt(pos, tilt=(0, 0, 0), col=(0.28, 0.24, 0.2)):
    Mx = xf(pos, tilt)
    prof = profile_pts([(0.0005, 0.13), (0.05, 0.132), (0.075, 0.12), (0.082, 0.07), (0.08, 0.03), (0.15, 0.0), (0.17, -0.012), (0.17, -0.004), (0.15, 0.01), (0.085, 0.022), (0.086, 0.07)], 3)
    bm = lathe(None, None, [(r, z) for r, z in prof], seg=32, cap=False, ret=True)
    # LATTICE modifier: pinch the crown (centre dent) and tilt the brim a little
    bm2 = lattice_deform(bm, (0, 0, 0.06), (0.36, 0.36, 0.16), {(1, 1, 2): (0, 0, -0.16), (0, 1, 1): (0, 0, 0.05), (2, 1, 1): (0, 0, -0.05), (1, 0, 0): (0, 0.03, 0)})
    bm.free()
    put(M['wool'], bm2, Mx, col=col)
    bm2.free()
    torus(M['leather'], None, 0.0835, 0.0075, plane='xy', Mx=Mx @ Matrix.Translation((0, 0, 0.038)), seg=32, rseg=6, col=(0.14, 0.1, 0.08))
    box(M['brass'], None, (0.014, 0.003, 0.012), Mx=Mx @ Matrix.Translation((0.083, 0, 0.038)), bev=0.0005)


def straw_hat(pos, tilt=(0, 0, 0)):
    Mx = xf(pos, tilt)
    prof = profile_pts([(0.0005, 0.115), (0.07, 0.115), (0.08, 0.1), (0.083, 0.04), (0.17, 0.012), (0.2, 0.0), (0.2, -0.006), (0.17, 0.004), (0.087, 0.03)], 3)
    lathe(M['wicker'], None, prof, seg=36, cap=False, Mx=Mx, col=(1.0, 0.92, 0.7))
    torus(M['linen'], None, 0.085, 0.009, plane='xy', Mx=Mx @ Matrix.Translation((0, 0, 0.045)), seg=32, rseg=6, col=(0.55, 0.2, 0.18))
    for r in (0.12, 0.15, 0.18):
        torus(M['wicker'], None, r, 0.0018, plane='xy', Mx=Mx @ Matrix.Translation((0, 0, 0.012 - (r - 0.1) * 0.12 + 0.003)), seg=36, rseg=4, col=(0.85, 0.72, 0.5))


def satchel(pos, rot, col=(0.42, 0.26, 0.15)):
    Mx = xf(pos, (0, 0, rot))
    box(M['leather'], None, (0.3, 0.1, 0.22), Mx=Mx @ Matrix.Translation((0, 0, -0.12)), bev=0.012, seg=3, col=col, g=0)
    box(M['leather'], None, (0.3, 0.103, 0.1), Mx=Mx @ Matrix.Translation((0, 0.0, -0.045)), bev=0.01, seg=2, col=tuple(c * 0.9 for c in col), g=0)
    for sx in (-1, 1):
        box(M['leather'], None, (0.022, 0.108, 0.17), Mx=Mx @ Matrix.Translation((sx * 0.08, 0.0, -0.08)), bev=0.002, col=tuple(c * 0.8 for c in col))
        box(M['brass'], None, (0.022, 0.006, 0.026), Mx=Mx @ Matrix.Translation((sx * 0.08, 0.055, -0.17)), bev=0.002)
    pts = [Mx @ Vector(p) for p in catmull([(-0.14, 0, -0.03), (-0.15, 0, 0.05), (-0.08, 0, 0.14), (0.0, 0, 0.16), (0.08, 0, 0.14), (0.15, 0, 0.05), (0.14, 0, -0.03)], 4)]
    tube(M['leather'], pts, 0.007, seg=8, col=tuple(c * 0.85 for c in col), flat=(1.0, 0.45))


def boot_tray(pos, rot, L=0.72, W=0.34):
    f = Fr(pos, rot, F)
    mat = M['wood_dark']
    col = (1.0, 0.92, 0.85)
    # slatted wooden frame with zinc tray inside, river pebbles
    h = 0.05
    f.box(M['iron'], (0, 0, 0.012), (L - 0.04, W - 0.04, 0.012), bev=0.002, col=(0.7, 0.72, 0.75), g=0)
    for sy in (-1, 1):
        f.box(mat, (0, sy * (W / 2 - 0.016), h / 2), (L, 0.032, h), bev=0.004, col=col, g=0)
    for sx in (-1, 1):
        f.box(mat, (sx * (L / 2 - 0.016), 0, h / 2), (0.032, W - 0.06, h), bev=0.004, col=col, g=1)
    # pebbles
    r = random.Random(4)
    for _ in range(46):
        x = r.uniform(-L / 2 + 0.05, L / 2 - 0.05); y = r.uniform(-W / 2 + 0.05, W / 2 - 0.05)
        f.sphere(M['stone'], (x, y, 0.025), r.uniform(0.014, 0.024), seg=8, rings=4, sq=(1, r.uniform(0.7, 1), 0.55), rot=(0, 0, r.uniform(0, 180)),
                 col=jit((0.62, 0.6, 0.57), 0.2))
    return f


def umbrella_stand(pos, col=(0.2, 0.26, 0.34)):
    f = Fr(pos, 0, F)
    prof = profile_pts([(0.0005, 0.0), (0.085, 0.0), (0.1, 0.02), (0.105, 0.2), (0.115, 0.5), (0.12, 0.62), (0.112, 0.625), (0.103, 0.5), (0.095, 0.03), (0.0005, 0.02)], 3)
    f.lathe(M['ceramic'], (0, 0, 0), prof, seg=28, cap=False, col=col)
    # glaze bands & drip tray
    for z, w in ((0.58, 0.01), (0.05, 0.006)):
        f.torus(M['brass'], (0, 0, z), 0.108 + 0.004 * z, 0.0035, plane='xy', seg=32, rseg=5, col=(0.85, 0.7, 0.4))
    f.lathe(M['iron'], (0, 0, 0), profile_pts([(0.11, 0.0), (0.125, 0.004), (0.13, 0.012), (0.12, 0.012)], 1), seg=28, cap=False)
    I.umbrella(f.p((0.0, 0.0, 0.07)), tilt=(3, 5, 0), col=(0.1, 0.12, 0.2), L=0.78)
    I.umbrella(f.p((0.04, 0.03, 0.07)), tilt=(-8, -3, 30), col=(0.45, 0.12, 0.12), L=0.74)
    I.umbrella(f.p((-0.04, 0.02, 0.07)), tilt=(4, -7, 60), col=(0.2, 0.3, 0.18), L=0.7)
    # walking cane
    cane = [f.p((-0.03, -0.04, 0.12 + 0.005 * t)) + Vector((0.0, 0.0, 0)) for t in range(1)]
    pts = [f.p((-0.045 + 0.02 * t, -0.04 - 0.01 * t, 0.12 + 0.75 * t)) for t in np.linspace(0, 1, 6)]
    tube(M['wood_dark'], pts, 0.0095, seg=8, col=(0.7, 0.5, 0.35))
    top = pts[-1]
    tube(M['wood_dark'], [top, top + Vector((0.01, 0, 0.04)), top + Vector((0.05, 0, 0.065)), top + Vector((0.09, 0, 0.04)), top + Vector((0.09, 0, 0.0))], 0.0105, seg=8, col=(0.7, 0.5, 0.35))
    cyl(M['brass'], pts[0] + Vector((0, 0, 0.01)), 0.011, 0.025, seg=8)
    collider_f(f, 0.3, 0.3, F + 0.95, name='umbrella_stand')
    return f




COATS = {
    'A': dict(hang=1.02, sh=0.19, hem=1.2, hb=0.08, phase=0.4, col=(0.2, 0.32, 0.24), mat='wool'),
    'B': dict(hang=0.9, sh=0.18, hem=1.15, hb=0.075, phase=1.4, col=(0.5, 0.36, 0.22), mat='wool'),
}


def key_board(f, c, n=5):
    """wooden key board with brass hooks and key rings (local frame f, c = board centre on the wall plane)"""
    x, y, z = c
    f.box(M['wood_dark'], (x, y + 0.009, z), (0.26, 0.018, 0.1), bev=0.004, col=(1.0, 0.92, 0.85), g=0)
    f.box(M['wood_dark'], (x, y + 0.02, z + 0.056), (0.28, 0.022, 0.016), bev=0.004, col=(1.05, 0.97, 0.9), g=0)
    for i in range(n):
        hx = x - 0.1 + i * 0.05
        f.cyl(M['brass'], (hx, y + 0.022, z - 0.01), 0.0045, 0.02, axis='y', seg=8)
        f.sphere(M['brass'], (hx, y + 0.033, z - 0.01), 0.0065, seg=8)
        if i in (0, 2, 3):
            I.keys_ring(f.p((hx, y + 0.034, z - 0.018)), 0)


def mail_rack(f, c):
    x, y, z = c
    mat = M['wood_dark']
    f.box(mat, (x, y, z + 0.003), (0.22, 0.09, 0.008), bev=0.002, col=(1.0, 0.92, 0.85), g=0)
    for k in range(4):
        f.box(mat, (x - 0.1 + k * 0.0667, y, z + 0.06), (0.006, 0.09, 0.115 - 0.01 * (k % 2)), bev=0.001, col=(1.0, 0.92, 0.85), g=2)
    f.box(mat, (x, y + 0.045, z + 0.03), (0.22, 0.006, 0.055), bev=0.001, col=(0.95, 0.86, 0.78), g=0)
    f.box(mat, (x, y - 0.045, z + 0.06), (0.22, 0.006, 0.115), bev=0.001, col=(0.8, 0.7, 0.6), g=0)
    r = random.Random(2)
    for k in range(3):
        for j in range(r.randint(1, 3)):
            ox = x - 0.067 + k * 0.0667 + 0.0
            f.box(M['paper'], (ox + 0.003 * j, y + 0.0, z + 0.07 + r.uniform(-0.005, 0.01)), (0.058, 0.0016, 0.1 + 0.01 * j), rot=(0, r.uniform(-4, 4), r.uniform(-3, 3)), bev=0, col=jit((0.94, 0.9, 0.78), 0.05), g=2, skip_down=False)


def build_entry():
    welcome_mat(0.0, -2.78)
    rf, pegs = coat_rack((0.98, -3.0), 0)
    # pegs: (z, angle, local pt); tier2 peg at 55 and 145 degrees carry coats
    p2 = [p for p in pegs if abs(p[0] - 1.70) < 0.01]
    p1 = [p for p in pegs if abs(p[0] - 1.50) < 0.01]
    byang = {round(p[1]): p for p in pegs}
    hang_coat(rf, byang[55], 'rc_coatA', COATS['A'])
    hang_coat(rf, byang[145], 'rc_coatB', COATS['B'])
    scarf_on_peg(rf, byang[10], 'rc_scarf')
    # satchel hung by its strap on the 100 deg peg (z=1.50)
    z, a_, p = byang[100]
    pp = rf.p(p)
    satchel(pp + Vector((0, 0.0, -0.01)), rf.rot + a_ - 90 + 0)
    # felt hat on the post top
    hat_felt(rf.p((0.0, 0.0, 1.80)), tilt=(6, -4, 20), col=(0.3, 0.26, 0.22))
    # boots on the tray (toes toward -x)
    bt = boot_tray((1.2, -2.35), 90)
    for k, (dy, dx, tl) in enumerate(((0.12, 0.0, None), (-0.04, 0.0, None))):
        pass
    I.boot(bt.p((-0.2, 0.0, 0.03)), rot=-90, col='#4a3322', h=0.29)
    I.boot(bt.p((-0.04, 0.03, 0.03)), rot=-96, col='#4a3322', h=0.29)
    # second pair: one boot lying on its side
    I.boot(bt.p((0.2, 0.03, 0.095)), rot=-80, col='#2c2118', h=0.25, tilt=(0, 78, 0))
    I.boot(Vector((0.95, -2.3, F)) , rot=-35 + 180, col='#6b4a2e', h=0.2, s=0.9) if False else None
    I.slippers((0.92, -2.2, F + 0.001), rot=100)
    umbrella_stand((1.2, -1.85))
    # console shelf on the partition (entry side face at x = 1.4)
    cf = wall_shelf((1.4, -2.2, 1.05), 90, W=0.7, D=0.2, trinkets=False)
    I.lantern(cf.p((0.2, 0.1, 0.011)), h=0.3, w=0.14, inten=1.5, dist=7.0, hang=True)
    mail_rack(cf, (-0.16, 0.1, 0.011))
    # coin / key bowl
    cf.lathe(M['ceramic'], (-0.27, 0.12, 0.011), profile_pts([(0.0005, 0.0), (0.03, 0.0), (0.06, 0.02), (0.065, 0.034), (0.058, 0.034), (0.05, 0.022), (0.025, 0.006), (0.0005, 0.006)], 2), seg=20, cap=False, col=(0.3, 0.45, 0.65))
    for k in range(5):
        cf.cyl(M['brass'], (-0.27 + 0.014 * math.cos(k * 1.3), 0.12 + 0.014 * math.sin(k * 1.3), 0.02 + 0.002 * k), 0.008, 0.002, seg=8, col=(1, 0.9, 0.6))
    # folded newspaper
    cf.box(M['paper'], (0.02, 0.08, 0.017), (0.2, 0.13, 0.012), bev=0.003, col=(0.86, 0.82, 0.72), g=0)
    for k in range(5):
        cf.box(M['ink'], (0.02, 0.08 + (k - 2) * 0.02, 0.0238), (0.16, 0.0025, 0.0004), bev=0, col=(0.2, 0.2, 0.2), skip_down=False)
    key_board(cf, (0.0, 0.0, 0.2))
    # hat rail above, with a straw hat and a canvas bag
    rf2 = Fr((1.4, -2.2, 1.78), 90, 1.78)
    rf2.box(M['wood_dark'], (0, 0.014, 0.0), (0.72, 0.028, 0.07), bev=0.005, col=(1.0, 0.92, 0.85), g=0)
    rf2.box(M['wood_dark'], (0, 0.03, 0.036), (0.74, 0.02, 0.012), bev=0.004, col=(1.05, 0.97, 0.9), g=0)
    for k, x in enumerate((-0.26, -0.09, 0.09, 0.26)):
        rf2.lathe(M['wood_dark'], (x, 0.028, 0.0), profile_pts([(0.0005, 0.0), (0.012, 0.0), (0.009, 0.01), (0.006, 0.05), (0.012, 0.075), (0.0005, 0.082)], 2), r=(-90, 0, 0), seg=10, cap=False, col=(1.05, 0.97, 0.9))
    straw_hat(rf2.p((-0.26, 0.095, -0.02)), tilt=(0, 0, 0)) if False else None
    sh_pos = rf2.p((-0.09, 0.1, -0.015))
    straw_hat(sh_pos, tilt=(-90, 0, rf2.rot + 0 + 0)) if False else None
    Mh = rf2._m((-0.09, 0.03, -0.02), (-90, 0, 0))
    lathe(M['wicker'], None, profile_pts([(0.0005, 0.115), (0.07, 0.115), (0.08, 0.1), (0.083, 0.04), (0.17, 0.012), (0.2, 0.0), (0.2, -0.006), (0.17, 0.004), (0.087, 0.03)], 3), seg=36, cap=False, Mx=Mh @ Matrix.Translation((0, 0, 0.0)) , col=(1.0, 0.92, 0.7))
    torus(M['linen'], None, 0.085, 0.009, plane='xy', Mx=Mh @ Matrix.Translation((0, 0, 0.045)), seg=32, rseg=6, col=(0.55, 0.2, 0.18))
    satchel(rf2.p((0.26, 0.05, -0.0)), rf2.rot, col=(0.5, 0.42, 0.28))
    I.keys_ring(rf2.p((0.09, 0.04, -0.035)), 0)
    collider(0.76, 1.22, -3.25, -2.8, F + 1.9)   # (replaced below by name)
    COLL.pop()
    return rf
