"""Cookware, utensils and small metalwork helpers."""
from kt_lib import *
from kt_ware import *
from kt_food import *


def orient(p, n, roll=0.0):
    """matrix at p with local +z along n"""
    n = Vector(n).normalized()
    q = Vector((0, 0, 1)).rotation_difference(n)
    return Matrix.Translation(Vector(p)) @ q.to_matrix().to_4x4() @ Matrix.Rotation(roll, 4, 'Z')


def dome(mat, p, n, r=0.004, h=None, col=(1, 1, 1), seg=6):
    h = r * 0.75 if h is None else h
    lathe(mat, None, [(r, 0.0), (r * 0.72, h * 0.72), (0.001, h)], 4, M=orient(p, n), col=col, cap=False, auto=False)


def rivet_line(mat, a, b, n, nrm, r=0.0035, col=(1, 1, 1)):
    a, b = Vector(a), Vector(b)
    for i in range(n):
        t = i / max(n - 1, 1)
        dome(mat, a + (b - a) * t, nrm, r=r, col=col)


def bail(Mx, r, z, ear_dx, sag=0.0, rad=0.0042, mat='iron_black', grip=False):
    """bail handle arc from ear (-ear_dx) over the top to (+ear_dx), in local XZ plane of Mx"""
    pts = []
    for i in range(15):
        a = math.pi * i / 14
        pts.append(Vector((-ear_dx * math.cos(a), 0, z + math.sin(a) * r)))
    sweep(mat, [(rad * math.cos(TAU * k / 6), rad * math.sin(TAU * k / 6)) for k in range(6)], pts, M=Mx)
    if grip:
        gp = [pts[6], pts[7], pts[8]]
        sweep('wood_dark', [(0.0095 * math.cos(TAU * k / 8), 0.0095 * math.sin(TAU * k / 8)) for k in range(8)], [Vector((-0.045, 0, z + r * 0.97)), Vector((0.045, 0, z + r * 0.97))], M=Mx)


def ear(Mx, p, side=1, mat='iron_black'):
    box(mat, None, (0.012, 0.014, 0.022), M=Mx @ Matrix.Translation(p), bev=0.003)
    cyl(mat, None, 0.0055, 0.018, axis='y', seg=8, M=Mx @ Matrix.Translation(p + Vector((side * 0.002, 0, 0.0))))


# ====================================================================== kettle (copper, swan-neck spout)
def kettle(pos, rot=0, r=0.115, mat='copper', lid=True, seed=0):
    """returns world position of spout tip"""
    Mx = xf(pos, (0, 0, rot))
    h = r * 1.0
    prof = [(0.001, 0.0), (r * 0.74, 0.0), (r * 0.78, 0.004), (r * 0.82, 0.01), (r * 0.99, h * 0.12), (r * 1.06, h * 0.32), (r * 1.0, h * 0.55), (r * 0.86, h * 0.76), (r * 0.64, h * 0.92),
            (r * 0.55, h * 0.97), (r * 0.53, h * 1.02), (r * 0.5, h * 1.02), (r * 0.5, h * 0.98)]

    def cf(p):
        l = Mx.inverted() @ p
        t = 0.5 + 0.5 * fbm(l.x * 12, l.y * 12, l.z * 12, 1, seed, 2)
        sooty = max(0.0, 1.0 - l.z / (h * 0.6)) * 0.55
        c = (0.95 - 0.18 * t, 0.85 - 0.15 * t, 0.8 - 0.1 * t)
        return tuple(c[i] * (1 - sooty * (0.75 if i else 0.7)) for i in range(3))
    lathe_dent(mat, None, prof, 28, M=Mx, cfn=cf, dents=(5, 0.0035, 0.022, 3), split=('z', [h * 0.12, h * 0.55]))
    # soldered seam band + rivets
    torus('copper', None, r * 1.052, 0.0032, plane='xy', seg=28, rseg=5, M=Mx @ Matrix.Translation((0, 0, h * 0.34)))
    for k in range(18):
        a = TAU * k / 18
        dome(mat, Mx @ Vector((r * 1.056 * math.cos(a), r * 1.056 * math.sin(a), h * 0.2)), Mx.to_3x3() @ Vector((math.cos(a), math.sin(a), 0)), r=0.0028)
    # lid with knob
    lathe(mat, None, [(r * 0.52, h * 1.0), (r * 0.5, h * 1.02), (r * 0.36, h * 1.07), (r * 0.14, h * 1.1), (r * 0.1, h * 1.11), (0.001, h * 1.11)], 20, M=Mx, cfn=cf, cap=False)
    lathe('wood_dark', None, [(0.012, h * 1.1), (0.0095, h * 1.13), (0.015, h * 1.16), (0.013, h * 1.19), (0.001, h * 1.2)], 10, M=Mx, col=(0.5, 0.35, 0.25), cap=False)
    # spout: swan neck
    sp = bez((r * 0.88, 0, h * 0.2), (r * 1.55, 0, h * 0.28), (r * 1.55, 0, h * 0.8), (r * 2.05, 0, h * 1.0), 14)
    n = len(sp)
    sc = [(r * (0.2 - 0.12 * (i / (n - 1)) ** 0.8),) * 2 for i in range(n)]
    sweep(mat, [(math.cos(TAU * k / 10), math.sin(TAU * k / 10)) for k in range(10)], sp, M=Mx, scale=sc, cfn=cf, caps=False)
    # spout lip
    lathe(mat, None, [(r * 0.09, 0), (r * 0.085, 0.004), (r * 0.075, 0.004)], 10, M=Mx @ Matrix.Translation(sp[-1]) @ Matrix.Rotation(math.radians(-40), 4, 'Y'), cap=False)
    # handle: bail with wooden grip on pivot ears
    for s in (-1, 1):
        ear(Mx, Vector((0, s * r * 0.98, h * 0.92)), side=s)
    pts = []
    for i in range(17):
        a = math.pi * i / 16
        pts.append(Vector((0.0, -r * 0.98 * math.cos(a), h * 0.92 + math.sin(a) * r * 1.0)))
    sweep('iron_black', [(0.0045 * math.cos(TAU * k / 6), 0.0045 * math.sin(TAU * k / 6)) for k in range(6)], pts, M=Mx)
    sweep('wood_dark', [(0.0105 * math.cos(TAU * k / 8), 0.0105 * math.sin(TAU * k / 8)) for k in range(8)], pts[6:11], M=Mx, col=(0.55, 0.4, 0.3))
    tip = Mx @ Vector(sp[-1])
    return tip


def kettle_anchor(tip):
    saved = part_begin()
    box('iron_cast', tip, (0.008, 0.008, 0.008), bev=0)
    part_end(saved, 'kettle_steam_anchor', tip)


# ====================================================================== cast iron pots
def dutch_pot(pos, r=0.1, h=0.12, rot=0, lid=True, legs=False, mat='iron_cast', soot=0.5, seed=0):
    Mx = xf(pos, (0, 0, rot))
    hz = h
    prof = [(0.001, 0.0), (r * 0.9, 0.0), (r * 0.97, 0.008), (r * 1.04, hz * 0.45), (r * 1.02, hz * 0.88), (r * 1.06, hz * 0.94), (r * 1.08, hz * 0.99), (r * 1.0, hz * 1.0), (r * 0.98, hz * 0.95)]

    def cf(p):
        l = Mx.inverted() @ p
        k = 1 + 0.12 * fbm(l.x * 22, l.y * 22, l.z * 22, 1, seed, 2)
        s = 1 - soot * max(0.0, 1.0 - l.z / (hz * 0.7))
        return (k * s, k * s, k * s)
    lathe_dent(mat, None, prof, 22, M=Mx, cfn=cf, dents=(3, 0.0025, 0.02, seed))
    if legs:
        for k in range(3):
            a = TAU * k / 3
            lathe(mat, None, [(0.011, 0), (0.008, -0.015), (0.005, -0.03)], 6, M=Mx @ Matrix.Translation((r * 0.7 * math.cos(a), r * 0.7 * math.sin(a), 0.002)), cap=True)
    for s in (-1, 1):
        ear(Mx, Vector((0, s * r * 1.06, hz * 0.85)), side=s, mat=mat)
    pts = []
    for i in range(15):
        a = math.pi * i / 14
        pts.append(Vector((0, -r * 1.06 * math.cos(a), hz * 0.85 + math.sin(a) * r * 1.05)))
    sweep('iron_black', [(0.0048 * math.cos(TAU * k / 6), 0.0048 * math.sin(TAU * k / 6)) for k in range(6)], pts, M=Mx)
    if lid:
        lathe(mat, None, [(r * 1.02, hz * 0.99), (r * 1.0, hz * 1.02), (r * 0.7, hz * 1.07), (r * 0.25, hz * 1.12), (r * 0.14, hz * 1.13), (0.001, hz * 1.13)], 20, M=Mx, cfn=cf, cap=False)
        lathe(mat, None, [(0.012, hz * 1.12), (0.007, hz * 1.14), (0.016, hz * 1.17), (0.001, hz * 1.19)], 8, M=Mx, cap=False)


def saucepan(pos, r=0.075, h=0.085, rot=0, mat='copper', handle_len=0.2, lid=False, seed=0, tilt=None):
    Mx = xf(pos, tilt if tilt is not None else (0, 0, rot))
    prof = [(0.001, 0.0), (r * 0.96, 0.0), (r, 0.004), (r * 1.0, h * 0.97), (r * 1.04, h), (r * 0.99, h + 0.001), (r * 0.96, h * 0.96), (r * 0.94, 0.008), (0.001, 0.007)]

    def cf(p):
        l = Mx.inverted() @ p
        k = 1 + 0.12 * fbm(l.x * 20, l.y * 20, l.z * 20, 1, seed, 2)
        s = 1 - 0.55 * max(0.0, 1 - l.z / (h * 0.6)) * 0.8
        return (k * s, k * s * 0.96, k * s * 0.92)
    lathe_dent(mat, None, prof, 22, M=Mx, cfn=cf, dents=(3, 0.003, 0.018, seed))
    # long iron handle with riveted plate and hanging hole
    hp = [Vector((r * 0.95, 0, h * 0.82)), Vector((r + 0.03, 0, h * 0.84)), Vector((r + handle_len * 0.6, 0, h * 0.86)), Vector((r + handle_len, 0, h * 0.84))]
    hp = polyline_smooth(hp, 4)
    n = len(hp)
    sweep('iron_black', [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)], hp, M=Mx, scale=lambda t: (0.005 + 0.002 * t, 0.02 - 0.01 * t), up=(0, 0, 1))
    for i in range(2):
        dome('iron_black', Mx @ Vector((r + 0.011 + 0.014 * i, 0, h * 0.82 + 0.0055)), Mx.to_3x3() @ Vector((0, 0, 1)), r=0.0034)
    cyl('wood_dark', Mx @ Vector((r + handle_len - 0.02, 0, h * 0.84)), 0.008, 0.03, axis='x', seg=8, rot=(0, 0, rot)) if False else None
    if lid:
        lathe(mat, None, [(r * 1.02, h), (r * 1.0, h + 0.004), (r * 0.5, h + 0.016), (0.001, h + 0.02)], 18, M=Mx, cfn=cf, cap=False)
        sphere('wood_dark', Mx @ Vector((0, 0, h + 0.026)), 0.011, seg=8, rings=4, col=(0.5, 0.35, 0.25))


def frying_pan(pos, r=0.12, rot=0, mat='iron_cast', tilt=None, seed=0, handle_dir=1):
    Mx = xf(pos, tilt if tilt is not None else (0, 0, rot))
    h = 0.035

    def cf(p):
        l = Mx.inverted() @ p
        k = 1 + 0.1 * fbm(l.x * 20, l.y * 20, l.z * 20, 1, seed, 2)
        return (k, k, k)
    lathe(mat, None, [(0.001, 0.0), (r * 0.78, 0.0), (r * 0.92, 0.008), (r, h * 0.9), (r * 1.03, h), (r * 0.99, h + 0.001), (r * 0.94, h * 0.9), (r * 0.8, 0.008), (0.001, 0.007)], 24, M=Mx, cfn=cf, cap=False)
    hp = [Vector((r * 0.95, 0, 0.026)), Vector((r + 0.03, 0, 0.032)), Vector((r + 0.12, 0, 0.034)), Vector((r + 0.24, 0, 0.034))]
    hp = polyline_smooth(hp, 3)
    sweep(mat, [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)], hp, M=Mx, scale=lambda t: (0.012 - 0.003 * t, 0.026 - 0.012 * t), up=(0, 0, 1), cfn=cf)
    # hanging hole ring
    torus(mat, None, 0.007, 0.003, plane='xz', seg=10, rseg=5, M=Mx @ Matrix.Translation((r + 0.238, 0, 0.034)) @ Matrix.Rotation(math.radians(90), 4, 'X'))
    # pour lips
    return Mx


# ====================================================================== utensils
def wooden_spoon(pos, rot=None, L=0.3, bowl_len=0.07, mat='wood_oak', col=(1, 0.92, 0.82)):
    Mx = xf(pos, rot)
    bw = 0.024
    prof = [(0.001, -0.0105), (0.4, -0.0098), (0.8, -0.0065), (1.0, 0.0), (1.0, 0.002), (0.8, -0.0045), (0.4, -0.0078), (0.001, -0.0085)]
    prof = [(a * bw if a > 0.01 else 0.001, z) for a, z in prof]
    lathe(mat, None, prof, 12, M=Mx @ Matrix.Translation((0, bowl_len / 2, 0.0105)), scale=(1.0, bowl_len / 2 / bw, 1.0), col=col, cap=False, auto=False)
    hp = [Vector((0, bowl_len * 0.9, 0.003)), Vector((0, bowl_len + 0.04, 0.004)), Vector((0, L * 0.7, 0.007)), Vector((0, L, 0.009))]
    hp = polyline_smooth(hp, 3)
    sweep(mat, [(math.cos(TAU * k / 8), math.sin(TAU * k / 8)) for k in range(8)], hp, M=Mx, scale=lambda t: (0.0065 + 0.004 * t, 0.0045 + 0.002 * t), col=col)


def ladle(pos, rot=None, L=0.32, mat='iron_black', bowl_r=0.04):
    Mx = xf(pos, rot)
    lathe(mat, None, [(0.001, 0.0), (bowl_r * 0.6, 0.004), (bowl_r * 0.95, 0.018), (bowl_r, 0.032), (bowl_r - 0.002, 0.033), (bowl_r * 0.9 - 0.0015, 0.018), (bowl_r * 0.55, 0.0045), (0.001, 0.0025)], 14,
          M=Mx @ Matrix.Translation((0, bowl_r + 0.0, 0.0)), cap=False)
    hp = bez((0, bowl_r * 1.9, 0.03), (0, bowl_r * 2.5, 0.07), (0, L * 0.6, 0.1), (0, L, 0.085), 8)
    sweep(mat, [(math.cos(TAU * k / 6), math.sin(TAU * k / 6)) for k in range(6)], hp, M=Mx, scale=lambda t: (0.0045, 0.0045))
    torus(mat, None, 0.007, 0.0025, plane='yz', M=Mx @ Matrix.Translation((0, L + 0.004, 0.085)), seg=8, rseg=5)


def skimmer(pos, rot=None, L=0.33, r=0.05):
    Mx = xf(pos, rot)
    prof = [(0.001, 0.0), (r * 0.7, 0.004), (r, 0.012), (r - 0.002, 0.0135), (r * 0.9, 0.012), (r * 0.7, 0.006), (0.001, 0.0035)]
    lathe('brass', None, prof, 16, M=Mx @ Matrix.Translation((0, r, 0.0)), cap=False)
    for k in range(7):   # perforations: tiny dark discs
        a = TAU * k / 7
        for rr_ in (0.012, 0.028):
            cyl('ink', None, 0.0035, 0.0012, seg=6, M=Mx @ Matrix.Translation((rr_ * math.cos(a + rr_ * 20), r + rr_ * math.sin(a + rr_ * 20), 0.0075)))
    hp = bez((0, r * 2, 0.012), (0, r * 2.6, 0.06), (0, L * 0.6, 0.1), (0, L, 0.085), 8)
    sweep('iron_black', [(math.cos(TAU * k / 6), math.sin(TAU * k / 6)) for k in range(6)], hp, M=Mx, scale=lambda t: (0.0042, 0.0042))
    sweep('wood_dark', [(math.cos(TAU * k / 8), math.sin(TAU * k / 8)) for k in range(8)], [Vector((0, L - 0.07, 0.092)), Vector((0, L + 0.04, 0.083))], M=Mx, scale=lambda t: (0.01, 0.01))


def rolling_pin(pos, rot=0, L=0.3, r=0.03, mat='wood_oak'):
    Mx = xf(pos, (0, 0, rot))
    prof = [(0.0, 0.0), (0.012, 0.0), (0.012, 0.015), (0.0095, 0.02), (0.0085, 0.07), (0.0105, 0.08), (r, 0.085), (r + 0.001, 0.09), (r + 0.001, L - 0.09), (r, L - 0.085), (0.0105, L - 0.08),
            (0.0085, L - 0.07), (0.0095, L - 0.02), (0.012, L - 0.015), (0.012, L), (0.0001, L)]
    pr = [(a if a > 0 else 0.001, z) for a, z in prof]
    lathe(mat, None, pr, 18, M=Mx @ Matrix.Translation((0, 0, r + 0.001)) @ Matrix.Rotation(math.radians(90), 4, 'Y') @ Matrix.Translation((0, 0, -L / 2)), col=(1, 0.93, 0.85), cap=False)


def mortar_pestle(pos, r=0.065, rot=0, mat='stone'):
    Mx = xf(pos, (0, 0, rot))
    prof = [(0.001, 0.0), (r * 0.62, 0.0), (r * 0.7, 0.004), (r * 0.78, 0.018), (r * 0.96, 0.05), (r * 1.0, 0.075), (r * 1.0, 0.082), (r * 0.9, 0.083), (r * 0.84, 0.078), (r * 0.76, 0.05), (r * 0.5, 0.022), (0.001, 0.016)]
    lathe(mat, None, prof, 22, M=Mx, col=(0.95, 0.93, 0.9), cap=False)
    # spout notch
    # pestle leaning inside
    pe = bez((0, 0, 0), (0, 0, 0.05), (0, 0, 0.1), (0, 0, 0.16), 4)
    pM = Mx @ Matrix.Translation((0.015, 0.01, 0.02)) @ Matrix.Rotation(math.radians(22), 4, 'Y') @ Matrix.Rotation(math.radians(8), 4, 'X')
    lathe(mat, None, [(0.001, 0.0), (0.014, 0.003), (0.0175, 0.012), (0.012, 0.045), (0.0085, 0.1), (0.0095, 0.15), (0.013, 0.17), (0.014, 0.19), (0.011, 0.205), (0.001, 0.208)], 12, M=pM, col=(0.9, 0.88, 0.84), cap=False)


def balance_scale(pos, rot=0, mat='brass'):
    """kitchen balance scale: base, pillar, beam, two chains and pans, weights"""
    Mx = xf(pos, (0, 0, rot))
    lathe('iron_black', None, [(0.001, 0.0), (0.06, 0.0), (0.063, 0.006), (0.055, 0.018), (0.03, 0.03), (0.016, 0.04), (0.012, 0.06), (0.01, 0.2), (0.014, 0.206), (0.012, 0.22), (0.0, 0.226)], 16, M=Mx, cap=False)
    # beam
    box('brass', None, (0.28, 0.01, 0.008), M=Mx @ Matrix.Translation((0, 0, 0.215)) @ Matrix.Rotation(math.radians(2.5), 4, 'Y'), bev=0.0015, seg=2)
    sphere('brass', Mx @ Vector((0, 0, 0.225)), 0.011, seg=8, rings=5)
    for s in (-1, 1):
        zb = 0.215 + s * 0.14 * math.sin(math.radians(-2.5)) * -1 * 0
        top = Mx @ Vector((s * 0.14, 0, 0.212 + (-s * 0.0061)))
        zp = 0.115 + (s * 0.006)
        bot = Mx @ Vector((s * 0.14, 0, zp))
        for k in range(3):
            a = TAU * k / 3
            tube('brass', [top, Mx @ Vector((s * 0.14 + 0.05 * math.cos(a), 0.05 * math.sin(a), zp + 0.004))], 0.0012, seg=3, caps=False)
        lathe('brass', None, [(0.052, 0.0), (0.05, 0.003), (0.03, 0.01), (0.001, 0.012)], 18, M=Matrix.Translation(bot) @ Matrix.Rotation(math.radians(180), 4, 'X') @ Matrix.Translation((0, 0, -0.0)), cap=False) if False else \
            lathe('brass', None, [(0.001, 0.0), (0.045, 0.004), (0.052, 0.012), (0.05, 0.013), (0.043, 0.008), (0.001, 0.0045)], 18, M=Matrix.Translation(bot + Vector((0, 0, -0.012))), cap=False)
    # weights on the left pan
    for i, rr_ in enumerate((0.014, 0.011, 0.008)):
        lathe('brass', None, [(rr_, 0), (rr_, rr_ * 1.2), (rr_ * 0.7, rr_ * 1.3), (rr_ * 0.4, rr_ * 1.6), (0.001, rr_ * 1.7)], 10, M=Mx @ Matrix.Translation((-0.14 + 0.02 * (i - 1), 0.012 * (i - 1), 0.115 - 0.006 - 0.0)), cap=False)


# ====================================================================== hanging pot rack
def pot_rack(cx, cy, z_bot, W=1.2, D=0.4, hang_h=0.5, ceil=3.15):
    """iron rack hung from the ceiling on chains with S-hooks, hanging copper pots, pans, ladles"""
    rr = random.Random(9)
    zr = z_bot
    # frame: two long rails + two cross bars (round bar), corner bosses
    for sy in (-1, 1):
        tube('iron_black', [Vector((cx - W / 2, cy + sy * D / 2, zr)), Vector((cx + W / 2, cy + sy * D / 2, zr))], 0.009, seg=8)
    for sx in (-1, 1):
        tube('iron_black', [Vector((cx + sx * W / 2, cy - D / 2, zr)), Vector((cx + sx * W / 2, cy + D / 2, zr))], 0.009, seg=8)
        for sy in (-1, 1):
            sphere('iron_black', Vector((cx + sx * W / 2, cy + sy * D / 2, zr)), 0.014, seg=8, rings=5)
    # twisted centre bar
    tube('iron_black', [Vector((cx - W / 2, cy, zr)), Vector((cx + W / 2, cy, zr))], 0.007, seg=6)
    # chains up to ceiling hooks
    for sx in (-1, 1):
        for sy in (-1, 1):
            link_chain(Vector((cx + sx * W / 2, cy + sy * D / 2, zr + 0.01)), Vector((cx + sx * W * 0.45, cy + sy * D * 0.45, ceil - 0.005)), r=0.0028, L=0.03)
            cyl('iron_black', (cx + sx * W * 0.45, cy + sy * D * 0.45, ceil - 0.004), 0.014, 0.008, seg=8)
    return zr


def s_hook(p, h=0.07, r=0.0025, mat='iron_black'):
    p = Vector(p)
    pts = []
    for i in range(10):
        a = math.pi * 1.2 * i / 9
        pts.append(p + Vector((0.012 * math.sin(a), 0, -0.012 * (1 - math.cos(a)) * 0 + 0.012 * math.cos(a) - 0.012)))
    tube(mat, [p, p + Vector((0.006, 0, -0.012)), p + Vector((0, 0, -0.03)), p + Vector((-0.008, 0, -0.045)), p + Vector((-0.002, 0, -0.058))], r, seg=4, caps=True)
