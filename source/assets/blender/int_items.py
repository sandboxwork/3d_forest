from int_lib import *
from int_mats import M

LAMPN = [0]
TAU = 2 * math.pi


def V(*a):
    return Vector(a)


# ------------------------------------------------------------------ flames / lights
def flame(pos, sc=1.0, inten=1.0, dist=5.0, color=(1.0, 0.68, 0.36), light_on=True, name=None):
    LAMPN[0] += 1
    n = name or 'lamp_%d' % LAMPN[0]
    saved = part_begin()
    prof = [(0, -0.013), (0.0055, -0.009), (0.0085, -0.002), (0.0065, 0.010), (0.003, 0.021), (0, 0.030)]
    lathe(M['flame'], pos, [(r * sc, z * sc) for r, z in prof], seg=8, cap=False)
    part_end(saved, n, pos)
    if light_on:
        light(n, pos, color, inten, dist)
    return n


# ------------------------------------------------------------------ small props
BOOKCOLS = ['#7a2f2a', '#2f4a63', '#3d5a3a', '#8a6a2e', '#4a2f4f', '#a04b2e', '#2c3f45', '#6b5a3c', '#8c3b3b', '#36506b',
            '#5d6b3a', '#b08d4a', '#4b3a2c', '#7b4b62', '#c2b090', '#2e2e38', '#9a5b3a', '#3e6a66']


def book(pos, size, rotz=0, col=None, lean=0, gold=True, face=(0, -1), pages=False):
    """standing book, pos = bottom centre; size=(thickness w, depth d, height h); spine faces local -y."""
    w, d, h = size
    col = C(col or rnd.choice(BOOKCOLS))
    col = jit(col, 0.12)
    rot = (lean, 0, rotz)
    M_ = xf(pos, rot)
    p = Vector(pos)
    R = rotm(rot)
    def at(l):  # local offset -> world
        return M_ @ Vector(l)
    box(M['cover_vc'], at((0, 0, h / 2)), (w, d, h), rot, bev=0, col=col)
    if pages:
        box(M['page'], at((0, d / 2 + 0.0008, h / 2)), (w - 0.008, 0.004, h - 0.01), rot, bev=0)
    if gold and rnd.random() < 0.6:
        box(M['brass'], at((0, -d / 2 - 0.0006, h * rnd.choice([0.2, 0.8]))), (w + 0.0012, 0.0015, 0.008), rot, bev=0)


def book_flat(pos, size, rotz=0, col=None):
    w, d, h = size  # w along x, d along y, h thickness
    col = jit(C(col or rnd.choice(BOOKCOLS)), 0.1)
    rot = (0, 0, rotz)
    M_ = xf(pos, rot)
    at = lambda l: M_ @ Vector(l)
    box(M['cover_vc'], at((0, 0, 0.002)), (w, d, 0.004), rot, bev=0, col=col)
    box(M['cover_vc'], at((0, 0, h - 0.002)), (w, d, 0.004), rot, bev=0, col=col)
    box(M['cover_vc'], at((-w / 2 + 0.002, 0, h / 2)), (0.004, d, h), rot, bev=0, col=col)
    box(M['page'], at((0.002, 0, h / 2)), (w - 0.008, d - 0.004, h - 0.008), rot, bev=0)


def book_open(pos, rotz=0, w=0.15, d=0.21, col='#6b3a2a'):
    rot = (0, 0, rotz)
    M_ = xf(pos, rot)
    at = lambda l: M_ @ Vector(l)
    box(M['cover_vc'], at((0, 0, 0.002)), (2 * w + 0.006, d + 0.006, 0.004), rot, bev=0, col=C(col))
    for s in (-1, 1):
        # page stacks with slight curve: two stepped boxes + tilted top
        box(M['page'], at((s * (w / 2 + 0.002), 0, 0.012)), (w - 0.006, d - 0.004, 0.016), rot, bev=0)
        rr = (0, -s * 7, rotz)
        box(M['page'], M_ @ Vector((s * (w / 2 + 0.002), 0, 0.022)), (w - 0.008, d - 0.006, 0.004), (0, -s * 4, rotz), bev=0)
    # text lines
    for s in (-1, 1):
        for i in range(5):
            box(M['ink'], at((s * (w / 2 + 0.004), d * (0.36 - i * 0.14), 0.0262)), (w * 0.72 * (0.7 + 0.3 * rnd.random()), 0.0025, 0.0004), rot, bev=0, col=(0.25, 0.22, 0.2))


def torus(mat, c, R, r, plane='xy', rot=None, seg=16, rseg=6, col=(1, 1, 1), a0=0, a1=360):
    n = int((a1 - a0) / 360 * seg)
    pts = arcpts((0, 0, 0), R, a0, a1, max(n, 3), 'xy' if plane == 'xy' else ('xz' if plane == 'xz' else 'yz'))
    M_ = xf(c, rot)
    pts = [M_ @ p for p in pts]
    tube(mat, pts, r, seg=rseg, col=col, caps=(a1 - a0) < 360)


def mug(pos, col=(1, 1, 1), r=0.04, h=0.09, mat='ceramic_vc', handle=True, rot=0, fill=None):
    prof = [(r * 0.85, 0), (r, 0.004), (r * 1.02, h * 0.5), (r, h), (r * 0.88, h), (r * 0.82, 0.008), (0.001, 0.006)]
    lathe(M[mat], pos, prof, 14, col=col, cap=False)
    if fill:
        lathe(M['water'], pos, [(r * 0.88, h * 0.82), (0.001, h * 0.82)], 14, cap=False, col=fill)
    if handle:
        a = math.radians(rot)
        dx, dy = math.cos(a), math.sin(a)
        c0 = Vector(pos) + V(dx * r * 0.98, dy * r * 0.98, h * 0.75)
        c1 = Vector(pos) + V(dx * r * 0.98, dy * r * 0.98, h * 0.2)
        pts = bez(c0, c0 + V(dx * 0.035, dy * 0.035, 0.012), c1 + V(dx * 0.035, dy * 0.035, -0.012), c1, 8)
        tube(M[mat], pts, 0.0055, 6, col=col)


def plate(pos, r=0.12, col=(1, 1, 1), mat='ceramic_white', tilt=None, rim=(0.75, 0.75, 0.9)):
    prof = [(0.001, 0.0), (r * 0.55, 0.0), (r * 0.98, 0.016), (r, 0.019), (r * 0.56, 0.004), (0.001, 0.004)]
    lathe(M[mat], pos, prof, 18, col=col, cap=False, rot=tilt)


def bowl(pos, r=0.08, h=0.05, col=(1, 1, 1), mat='ceramic_white', rot=None, inner=None):
    prof = [(0.001, 0), (r * 0.45, 0.0), (r * 0.8, h * 0.35), (r, h), (r * 0.96, h), (r * 0.75, h * 0.42), (r * 0.42, 0.006), (0.001, 0.006)]
    lathe(M[mat], pos, prof, 16, col=col, cap=False, rot=rot)
    if inner:
        im, ic, hh = inner
        lathe(M[im], pos, [(r * (0.7 + 0.25 * hh), h * hh), (0.001, h * hh)], 16, cap=False, col=ic)


def teapot(pos, rot=0, col=(1, 1, 1), mat='ceramic_vc', r=0.075):
    Mr = xf(pos, (0, 0, rot))
    at = lambda l: Mr @ Vector(l)
    prof = [(0.001, 0), (r * 0.55, 0.0), (r * 0.95, r * 0.25), (r, r * 0.75), (r * 0.9, r * 1.35), (r * 0.6, r * 1.6), (r * 0.45, r * 1.62)]
    lathe(M[mat], pos, prof, 16, rot=(0, 0, rot), col=col, cap=False)
    lathe(M[mat], at((0, 0, r * 1.58)), [(0.001, 0), (r * 0.5, 0.0), (r * 0.42, 0.012), (r * 0.12, 0.022), (0.004, 0.03)], 14, col=col, cap=False)
    # spout
    pts = [at(p) for p in bez((r * 0.8, 0, r * 0.35), (r * 1.3, 0, r * 0.4), (r * 1.5, 0, r * 0.9), (r * 1.85, 0, r * 1.25), 8)]
    tube(M[mat], pts, [0.014, 0.012, 0.011, 0.009, 0.008, 0.007, 0.007, 0.006, 0.006], 8, col=col)
    pts = [at(p) for p in bez((-r * 0.85, 0, r * 1.25), (-r * 1.6, 0, r * 1.5), (-r * 1.6, 0, r * 0.4), (-r * 0.85, 0, r * 0.3), 10)]
    tube(M[mat], pts, 0.0075, 6, col=col)


def jar(pos, r=0.045, h=0.11, glassmat='glass', content=None, lid=True, lidcol=(0.7, 0.55, 0.3), label=None, seg=14):
    prof = [(r * 0.9, 0), (r, 0.004), (r, h * 0.78), (r * 0.6, h * 0.88), (r * 0.5, h)]
    lathe(M[glassmat], pos, prof, seg, cap=False)
    if content:
        ch, cc = content
        lathe(M['food_vc'], pos, [(0.001, 0.004), (r * 0.92, 0.004), (r * 0.92, h * ch), (0.001, h * ch)], seg, col=cc, cap=False)
    if lid:
        cyl(M['wood_oak'] if lidcol is None else M['brass'], Vector(pos) + V(0, 0, h + 0.006), r * 0.55, 0.014, seg=12, col=lidcol)
    if label:
        cyl(M['paper'], Vector(pos) + V(0, 0, h * 0.4), r * 1.012, h * 0.3, seg=seg, cap=False, col=label)


def bottle(pos, r=0.03, h=0.26, col=(0.25, 0.45, 0.3), alpha_mat='glass_amber', liquid=0.6, cork=True):
    prof = [(r * 0.9, 0), (r, 0.004), (r, h * 0.55), (r * 0.85, h * 0.68), (r * 0.36, h * 0.78), (r * 0.33, h * 0.95), (r * 0.4, h)]
    lathe(M[alpha_mat], pos, prof, 12, cap=False, col=col)
    if cork:
        cyl(M['wood_pine'], Vector(pos) + V(0, 0, h + 0.008), r * 0.36, 0.022, seg=8)


def candle_holder(pos, h=0.12, col='brass', candle=True, cl=0.12, flame_it=True, sc=1.0, inten=0.6, dist=4.0, name=None):
    mat = M[col]
    prof = [(0.001, 0), (0.04, 0.0), (0.045, 0.006), (0.03, 0.012), (0.012, 0.02), (0.009, 0.05), (0.014, 0.06), (0.009, 0.068), (0.008, h * 0.75),
            (0.022, h * 0.86), (0.012, h * 0.88)]
    lathe(mat, pos, prof, 14, cap=False)
    base = Vector(pos) + V(0, 0, h * 0.86)
    if candle:
        cyl(M['wax'], base + V(0, 0, cl / 2), 0.011, cl, seg=10, r2=0.0105)
        # drip
        sphere(M['wax'], base + V(0.006, 0, cl * 0.93), 0.0055, seg=6, rings=4, sq=(1, 1, 1.6))
        box(M['ink'], base + V(0, 0, cl + 0.004), (0.0016, 0.0016, 0.009), bev=0, col=(0.1, 0.08, 0.06))
        if flame_it:
            return flame(base + V(0, 0, cl + 0.022), sc, inten, dist, name=name)


def oil_lamp(pos, sc=1.0, inten=1.0, dist=6.0, lit=True, tall=0.0):
    p = Vector(pos)
    # brass foot + amber glass reservoir + collar + chimney
    prof = [(0.001, 0), (0.05, 0.0), (0.052, 0.006), (0.035, 0.014), (0.018, 0.022), (0.014, 0.045), (0.02, 0.05)]
    lathe(M['brass'], p, prof, 16, cap=False)
    res = [(0.02, 0.05), (0.04, 0.062), (0.052, 0.09), (0.05, 0.115), (0.035, 0.14), (0.02, 0.15)]
    lathe(M['glass_amber'], p, res, 16, cap=False)
    lathe(M['wax'], p, [(0.001, 0.055), (0.045, 0.085), (0.046, 0.11), (0.03, 0.128), (0.001, 0.13)], 14, cap=False, col=(0.95, 0.8, 0.45))
    lathe(M['brass'], p, [(0.02, 0.148), (0.022, 0.152), (0.028, 0.162), (0.022, 0.172), (0.02, 0.182)], 14, cap=False)
    # chimney glass
    lathe(M['glass'], p, [(0.018, 0.178), (0.027, 0.2), (0.029, 0.225), (0.022, 0.26), (0.018, 0.29), (0.016, 0.3)], 14, cap=False)
    box(M['wax'], p + V(0, 0, 0.19), (0.022, 0.004, 0.012), bev=0, col=(0.9, 0.85, 0.7))
    return flame(p + V(0, 0, 0.212), sc * 1.3, inten, dist) if lit else None


def lantern(pos, h=0.3, w=0.14, hang=True, sc=1.3, inten=1.4, dist=7.0, chain_to=None, name=None, mat='iron_black'):
    """cage lantern; pos = centre of body. optional chain up to z=chain_to."""
    p = Vector(pos)
    hw = w / 2
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        box(M[mat], p + V(sx * hw, sy * hw, 0), (0.01, 0.01, h), bev=0.002)
    box(M[mat], p + V(0, 0, -h / 2 - 0.005), (w + 0.02, w + 0.02, 0.014), bev=0.003)
    box(M[mat], p + V(0, 0, -h / 2 + 0.03), (w * 0.6, w * 0.6, 0.008), bev=0.002)
    for z in (h / 2 - 0.02,):
        for s in (1, -1):
            box(M[mat], p + V(0, s * hw, z), (w, 0.008, 0.012), bev=0.002)
            box(M[mat], p + V(s * hw, 0, z), (0.008, w, 0.012), bev=0.002)
    # roof
    lathe(M[mat], p + V(0, 0, h / 2), [(w * 0.85, 0.0), (w * 0.88, 0.012), (w * 0.4, 0.06), (0.012, 0.085), (0.001, 0.09)], 4, rot=(0, 0, 45), cap=False)
    tube(M[mat], arcpts((p.x, p.y, p.z + h / 2 + 0.085), 0.03, 0, 180, 8, 'xz'), 0.004, 6)
    # glass panes
    for s in (1, -1):
        box(M['glass'], p + V(0, s * (hw - 0.002), 0), (w - 0.012, 0.002, h - 0.03), bev=0)
        box(M['glass'], p + V(s * (hw - 0.002), 0, 0), (0.002, w - 0.012, h - 0.03), bev=0)
    # candle stub
    cyl(M['wax'], p + V(0, 0, -h / 2 + 0.06), 0.022, 0.09, seg=10)
    if chain_to is not None:
        chain(p.x, p.y, p.z + h / 2 + 0.115, chain_to, M[mat])
    return flame(p + V(0, 0, -h / 2 + 0.135), sc, inten, dist, name=name)


def vase_flowers(pos, kind='wild', h=0.2, r=0.05, n=5, vcol='#6c8fa5', seed=1):
    rr = random.Random(seed)
    p = Vector(pos)
    prof = [(0.001, 0), (r * 0.6, 0), (r, h * 0.3), (r * 0.85, h * 0.6), (r * 0.42, h * 0.85), (r * 0.5, h), (r * 0.46, h)]
    lathe(M['ceramic_vc'], p, prof, 14, cap=False, col=C(vcol))
    top = p + V(0, 0, h)
    fcols = {'wild': ['#e8d44d', '#f0f0f0', '#c97ad0', '#ef8a5a', '#f4c2d0'], 'dried': ['#c9a66b', '#b98552', '#d8c58a', '#8d6b4a'], 'lav': ['#8c6fc2', '#7a5fb5']}[kind]
    for i in range(n):
        a = rr.uniform(0, TAU); sp = rr.uniform(0.02, 0.12 if kind != 'lav' else 0.08)
        L = rr.uniform(0.18, 0.32)
        tip = top + V(math.cos(a) * sp * 1.5, math.sin(a) * sp * 1.5, L)
        pts = bez(top + V(0, 0, -0.02), top + V(0, 0, L * 0.4), tip - V(math.cos(a) * sp * 0.5, math.sin(a) * sp * 0.5, L * 0.3), tip, 4)
        tube(M['herb_vc'], pts, 0.0018, 4, col=(0.22, 0.4, 0.15) if kind != 'dried' else (0.55, 0.45, 0.25), caps=False)
        fc = C(rr.choice(fcols))
        if kind == 'wild':
            sphere(M['food_vc'], tip, 0.017, seg=6, rings=3, col=fc, sq=(1, 1, 0.4))
            sphere(M['food_vc'], tip, 0.007, seg=5, rings=3, col=(0.9, 0.7, 0.1))
        elif kind == 'dried':
            sphere(M['food_vc'], tip, 0.014, seg=6, rings=4, col=fc, sq=(1, 1, 0.8))
        else:
            for k in range(5):
                sphere(M['food_vc'], tip - V(0, 0, k * 0.012), 0.006, seg=5, rings=3, col=fc)
        lp = pts[3]
        sphere(M['herb_vc'], lp + V(0.01 * math.cos(a + 1.5), 0.01 * math.sin(a + 1.5), 0), 0.012, seg=5, rings=3, col=(0.25, 0.45, 0.18), sq=(1, 0.3, 0.6))


def apple(pos, col='#b53a2a', r=0.038, tilt=None):
    col = jit(C(col), 0.15)
    prof = [(0.001, -r * 0.85), (r * 0.8, -r * 0.5), (r, r * 0.15), (r * 0.6, r * 0.8), (0.001, r * 0.65)]
    lathe(M['food_vc'], pos, prof, 7, cap=False, col=col, rot=tilt)


def pear(pos, col='#c9b94a', r=0.035):
    col = jit(C(col), 0.1)
    prof = [(0.001, -r * 1.3), (r * 0.6, -r * 1.2), (r * 1.0, -r * 0.6), (r * 0.8, 0.0), (r * 0.5, r * 0.6), (r * 0.35, r * 1.1), (0.001, r * 1.3)]
    lathe(M['food_vc'], pos, prof, 10, cap=False, col=col)


def onion(pos, col='#c78a3a', r=0.03):
    prof = [(0.001, -r), (r * 0.6, -r * 0.85), (r, -r * 0.1), (r * 0.8, r * 0.6), (r * 0.25, r * 1.2), (0.001, r * 1.5)]
    lathe(M['food_vc'], pos, prof, 8, cap=False, col=jit(C(col), 0.12))


def garlic(pos, r=0.022):
    prof = [(0.001, -r), (r * 0.7, -r * 0.85), (r, -r * 0.1), (r * 0.7, r * 0.7), (r * 0.15, r * 1.5), (0.001, r * 1.7)]
    lathe(M['food_vc'], pos, prof, 7, cap=False, col=(0.93, 0.9, 0.82))


def carrot(pos, rot=None, L=0.16):
    prof = [(0.001, -L / 2), (0.004, -L * 0.3), (0.011, L * 0.2), (0.014, L / 2 - 0.01), (0.012, L / 2)]
    lathe(M['food_vc'], pos, prof, 7, rot=rot, col=(0.95, 0.5, 0.15), cap=True)
    lathe(M['herb_vc'], Vector(pos), [(0.001, 0), (0.005, 0.0)], 4, cap=False)


def loaf(pos, rot=0, L=0.3, w=0.12, h=0.08):
    col = lambda p: (0.50 - 0.10 * max(0, abs(nz(p.x * 30, p.y * 30)) - 0.2), 0.24 - 0.06 * abs(nz(p.x * 25, p.y * 25, 1)), 0.07)
    lathe(M['food_vc'], pos, [(0.001, 0), (0.5, 0.0), (0.9, 0.3), (1.0, 0.6), (0.78, 0.9), (0.3, 1.0), (0.001, 1.0)], 14, rot=(0, 0, rot), cfn=col, cap=False, scale=(L / 2, w / 2, h))
    # score cuts
    M_ = xf(pos, (0, 0, rot))
    for i in range(4):
        x = -L * 0.3 + i * L * 0.2
        box(M['food_vc'], M_ @ Vector((x, 0, h * 0.97)), (0.012, w * 0.6, 0.004), (0, 0, rot + 35), bev=0, col=(0.95, 0.8, 0.5))


def cheese(pos, rot=0):
    lathe(M['food_vc'], pos, [(0.001, 0), (0.07, 0), (0.07, 0.05), (0.001, 0.05)], 16, cap=False, col=(0.93, 0.76, 0.3), rot=(0, 0, rot))


def knife(pos, rot=0, L=0.2):
    M_ = xf(pos, (0, 0, rot))
    at = lambda l: M_ @ Vector(l)
    box(M['pewter'], at((L * 0.3, 0, 0.002)), (L * 0.6, 0.022, 0.0025), (0, 0, rot), bev=0, col=(1, 1, 1))
    box(M['wood_walnut'], at((-L * 0.25, 0, 0.007)), (L * 0.4, 0.02, 0.014), (0, 0, rot), bev=0.004)


def cutting_board(pos, rot=0, size=(0.4, 0.26)):
    box(M['wood_pine'], Vector(pos) + V(0, 0, 0.011), (size[0], size[1], 0.022), (0, 0, rot), bev=0.005, cuts=3, cfn=woodcol((1, 1, 1), 0.1, 10, 4, 0))


def basket(pos, r=0.22, h=0.25, handle=True, fill=None, rot=None, open_top=True):
    prof = [(0.001, 0), (r * 0.72, 0.0), (r * 0.9, h * 0.35), (r, h), (r * 0.97, h), (r * 0.88, h * 0.4), (r * 0.7, 0.012), (0.001, 0.012)]
    lathe(M['wicker'], pos, prof, 20, cap=False, rot=rot)
    # rim band
    lathe(M['wicker'], Vector(pos) + V(0, 0, h - 0.008), [(r * 0.93, 0), (r * 1.02, 0), (r * 1.02, 0.016), (r * 0.93, 0.016)], 20, cap=False, rot=rot)
    if handle:
        Mr = xf(pos, rot)
        pts = [Mr @ Vector(p) for p in arcpts((0, 0, h), r * 0.97, 0, 180, 12, 'xz')]
        pts = [Mr @ (Vector((0, 0, h)) + V(math.cos(a) * r * 0.97, 0, math.sin(a) * r * 1.0)) for a in [math.radians(i * 180 / 12) for i in range(13)]]
        tube(M['wicker'], pts, 0.012, 6)


def log(pos, L=0.4, r=0.055, rot=None, axis='y', col=None):
    cyl(M['log_bark'], pos, r, L, axis=axis, seg=10, cfn=None, col=col or jit((0.85, 0.75, 0.65), 0.15), rot=rot, uvm=1.0)
    for s in (-1, 1):
        off = {'x': (s * L / 2, 0, 0), 'y': (0, s * L / 2, 0), 'z': (0, 0, s * L / 2)}[axis]
        c = xf(pos, rot) @ Vector(off)
        cyl(M['wood_pine'], c, r * 0.93, 0.004, axis=axis, seg=10, rot=rot, col=(0.75, 0.55, 0.35))


def sack(pos, r=0.22, h=0.6, col=(1, 1, 1), rot=0, slump=0.18, tie=True):
    p = Vector(pos)
    prof = []
    for i in range(0, 11):
        t = i / 10
        rad = r * (0.72 + 0.28 * math.sin(min(t * 1.25, 1) * math.pi / 2)) if t < 0.7 else r * (1.0 - (t - 0.7) / 0.3 * 0.75)
        rad = max(rad, 0.001) if t < 1 else 0.001
        prof.append((rad * (1.0 - 0.0), t * h))
    prof[-1] = (0.01, h + 0.03)
    def cf(pp):
        k = 1 + 0.06 * nz(pp.x * 9, pp.y * 9, pp.z * 9)
        return (col[0] * k, col[1] * k, col[2] * k)
    lathe(M['sack'], p, prof, 14, rot=(0, 0, rot), cfn=cf, cap=True)
    if tie:
        tube(M['rope'], arcpts((p.x, p.y, p.z + h * 0.86), r * 0.46, 0, 360, 10, 'xy'), 0.006, 5)


def bucket(pos, r=0.14, h=0.27, mat='wood_oak', water=None, hoops=True, handle=True, open_top=True):
    p = Vector(pos)
    r2 = r * 1.15
    n = 14
    for i in range(n):
        a = i / n * TAU
        # staves
        c = p + V(math.cos(a) * (r + r2) / 2 * 0.985, math.sin(a) * (r + r2) / 2 * 0.985, h / 2)
        tilt = math.degrees(math.atan2(r2 - r, h))
        bx = box(M[mat], c, (TAU * r / n * 1.02, 0.014, h), (0, 0, math.degrees(a) + 90), bev=0.0015, col=jit((1, 1, 1), 0.1))
    cyl(M[mat], p + V(0, 0, 0.01), r * 0.96, 0.02, seg=n)
    if hoops:
        for z, rr in ((0.12 * h, r + (r2 - r) * 0.12), (0.72 * h, r + (r2 - r) * 0.72)):
            lathe(M['iron_black'], p + V(0, 0, z), [(rr + 0.012, -0.012), (rr + 0.014, 0.0), (rr + 0.012, 0.012)], n, cap=False)
    if water:
        cyl(M['water'], p + V(0, 0, h * 0.85), r2 * 0.92, 0.002, seg=n)
    if handle:
        pts = [p + V(math.cos(a) * r2 * 0.95, 0, h + math.sin(a) * r2 * 1.0) for a in [math.radians(i * 180 / 12) for i in range(13)]]
        tube(M['iron_black'], pts, 0.004, 5)


def barrel(pos, r=0.3, h=0.85, lid=True, tap=False, water=True):
    p = Vector(pos)
    prof = [(r * 0.78, 0.0)] + [(r * (0.8 + 0.2 * math.sin(math.pi * i / 8)), h * i / 8) for i in range(1, 8)] + [(r * 0.78, h)]
    def cf(pp):
        a = math.atan2(pp.y - p.y, pp.x - p.x)
        k = 1 + 0.08 * math.sin(a * 22) + 0.04 * nz(pp.x * 5, pp.y * 5, pp.z * 5)
        return (k, k * 0.93, k * 0.85)
    lathe(M['wood_dark'], p, prof, 28, cfn=cf, cap=True, uvm=1.0)
    for f in (0.12, 0.3, 0.7, 0.88):
        rr = r * (0.8 + 0.2 * math.sin(math.pi * f)) + 0.005
        lathe(M['iron_black'], p + V(0, 0, h * f), [(rr, -0.014), (rr + 0.006, -0.012), (rr + 0.006, 0.012), (rr, 0.014)], 28, cap=False)
    if water:
        cyl(M['water'], p + V(0, 0, h - 0.06), r * 0.72, 0.002, seg=24)
    if tap:
        box(M['brass'], p + V(r * 0.95, 0, h * 0.2), (0.07, 0.02, 0.02), bev=0.004)


def crate(pos, size=(0.5, 0.36, 0.26), rot=0, fill=None, mat='wood_pine'):
    sx, sy, sz = size
    p = Vector(pos)
    M_ = xf(p, (0, 0, rot))
    at = lambda l: M_ @ Vector(l)
    t = 0.014
    rr = (0, 0, rot)
    box(M[mat], at((0, 0, t / 2)), (sx, sy, t), rr, bev=0.002, col=jit((1, 0.95, 0.9), 0.08), cuts=1)
    for sgn in (-1, 1):
        for k in range(3):
            z = (k + 0.5) * (sz / 3)
            box(M[mat], at((sgn * (sx / 2 - t / 2), 0, z + 0.004)), (t, sy, sz / 3 - 0.012), rr, bev=0.0015, col=jit((1, 0.95, 0.9), 0.1))
            box(M[mat], at((0, sgn * (sy / 2 - t / 2), z + 0.004)), (sx - 2 * t, t, sz / 3 - 0.012), rr, bev=0.0015, col=jit((1, 0.95, 0.9), 0.1))
    for sx_ in (-1, 1):
        for sy_ in (-1, 1):
            box(M[mat], at((sx_ * (sx / 2 - 0.02), sy_ * (sy / 2 - 0.02), sz / 2)), (0.03, 0.03, sz), rr, bev=0.003, col=(0.8, 0.7, 0.6))
    return at


def heap_apples(pos, sx, sy, z, n=30, seed=3, col=None):
    rr = random.Random(seed)
    for i in range(n):
        x = rr.uniform(-sx, sx); y = rr.uniform(-sy, sy)
        c = col or rr.choice(['#b53a2a', '#c4422c', '#d6a93a', '#a83226', '#89a83a'])
        apple(Vector(pos) + V(x, y, z + rr.uniform(0, 0.03)), c, r=rr.uniform(0.032, 0.04), tilt=(rr.uniform(-20, 20), rr.uniform(-20, 20), 0))


def herb_bundle(pos, L=0.35, kind='lav', n=6, seed=1, hang_to=None, spread=0.04):
    """bundle hanging upside down from pos (top). hang_to=z of ceiling."""
    rr = random.Random(seed)
    p = Vector(pos)
    cols = {'lav': (0.58, 0.5, 0.7), 'herb': (0.35, 0.5, 0.22), 'dry': (0.6, 0.5, 0.3), 'chili': (0.8, 0.12, 0.08), 'wheat': (0.85, 0.7, 0.35)}
    base = cols[kind]
    for i in range(n):
        a = rr.uniform(0, TAU); s = rr.uniform(0, spread)
        end = p + V(math.cos(a) * s * 2.2, math.sin(a) * s * 2.2, -L * rr.uniform(0.8, 1.05))
        pts = bez(p, p + V(0, 0, -L * 0.25), end + V(-math.cos(a) * s, -math.sin(a) * s, L * 0.3), end, 3)
        c = jit(base, 0.15)
        tube(M['herb_vc'], pts, 0.0028, 4, col=c, caps=False)
        if kind in ('lav', 'wheat'):
            sphere(M['herb_vc'], end + V(0, 0, 0.008), 0.007, seg=5, rings=3, col=c, sq=(1, 1, 3.0))
        elif kind == 'chili':
            sphere(M['herb_vc'], end, 0.011, seg=5, rings=3, col=c, sq=(0.6, 0.6, 2.4))
        else:
            sphere(M['herb_vc'], end, 0.014, seg=5, rings=3, col=c, sq=(1, 1, 0.5))
    cyl(M['rope'], p + V(0, 0, -0.05), 0.022, 0.012, seg=6, cap=False)
    if hang_to:
        tube(M['rope'], [p, V(p.x, p.y, hang_to)], 0.002, 4, caps=False)


def braid(pos, kind='onion', n=8, seed=2, top=None):
    """hanging braid of onions or garlic from pos (top)."""
    rr = random.Random(seed)
    p = Vector(pos)
    z = 0.0
    rope = []
    for i in range(n):
        side = 1 if i % 2 == 0 else -1
        c = p + V(side * 0.02, rr.uniform(-0.008, 0.008), -0.06 - i * (0.06 if kind == 'onion' else 0.045))
        if kind == 'onion':
            onion(c, r=rr.uniform(0.028, 0.034))
        else:
            garlic(c, r=rr.uniform(0.02, 0.025))
        rope.append(c)
    tube(M['straw'], [p, p + V(0, 0, -0.06)] + [q + V(-0.02 if i % 2 == 0 else 0.02, 0, 0.03) for i, q in enumerate(rope)], 0.0035, 5, caps=False)
    if top:
        tube(M['rope'], [p, V(p.x, p.y, top)], 0.002, 4, caps=False)


def kettle(pos, rot=0, r=0.11, mat='iron_cast', steam=False, lid_col=None):
    """round kettle/pot with spout and bail. returns spout tip world pos."""
    Mr = xf(pos, (0, 0, rot))
    at = lambda l: Mr @ Vector(l)
    prof = [(0.001, 0), (r * 0.72, 0.0), (r * 0.98, r * 0.25), (r, r * 0.55), (r * 0.8, r * 0.95), (r * 0.52, r * 1.05), (r * 0.46, r * 1.05)]
    lathe(M[mat], pos, prof, 18, rot=(0, 0, rot), cap=False)
    lathe(M[mat], at((0, 0, r * 1.0)), [(r * 0.5, 0), (r * 0.44, 0.004), (r * 0.2, r * 0.22), (0.008, r * 0.3)], 14, cap=False)
    sphere(M[mat], at((0, 0, r * 1.32)), 0.014, seg=8, rings=4)
    pts = [at(p) for p in bez((r * 0.85, 0, r * 0.3), (r * 1.35, 0, r * 0.45), (r * 1.6, 0, r * 0.9), (r * 2.0, 0, r * 1.25), 8)]
    tube(M[mat], pts, [r * 0.17, r * 0.15, r * 0.13, r * 0.115, r * 0.1, r * 0.09, r * 0.085, r * 0.08, r * 0.08], 8)
    # bail handle
    hp = [at((math.sin(a) * r * 0.98 * 0.0 + r * 0.0, math.cos(a) * r * 1.0, r * 0.95 + math.sin(a) * r * 0.9)) for a in [math.radians(i * 180 / 14) for i in range(15)]]
    hp = [at((0, math.cos(math.radians(a)) * r * 1.0, r * 0.95 + math.sin(math.radians(a)) * r * 0.9)) for a in [i * 180 / 14 for i in range(15)]]
    tube(M['iron_black'], hp, 0.0055, 5)
    return pts[-1]


def pot(pos, r=0.1, h=0.12, mat='copper', lid=True, rot=None, handle=True, hang=False):
    p = Vector(pos)
    prof = [(0.001, 0), (r * 0.94, 0), (r, 0.004), (r * 1.0, h * 0.95), (r * 1.06, h), (r * 1.0, h), (r * 0.97, h * 0.96), (r * 0.94, 0.008), (0.001, 0.008)]
    lathe(M[mat], p, prof, 18, cap=False, rot=rot)
    Mr = xf(p, rot)
    at = lambda l: Mr @ Vector(l)
    if lid:
        lathe(M[mat], at((0, 0, h)), [(r * 1.04, 0), (r * 1.0, 0.008), (r * 0.5, 0.022), (0.01, 0.028)], 18, cap=False, rot=rot)
        sphere(M['wood_dark'], at((0, 0, h + 0.034)), 0.012, seg=8, rings=4)
    if handle:
        box(M['iron_black'], at((r * 1.25, 0, h * 0.85)), (r * 0.6, 0.016, 0.008), rot, bev=0.002)
        box(M['iron_black'], at((-r * 1.02, 0, h * 0.85)), (0.02, 0.05, 0.008), rot, bev=0.002)


def pan(pos, r=0.12, rot=0, mat='iron_cast', tilt=None, hang=False):
    p = Vector(pos)
    lathe(M[mat], p, [(0.001, 0), (r * 0.85, 0), (r, 0.03), (r * 0.97, 0.03), (r * 0.8, 0.008), (0.001, 0.008)], 18, cap=False, rot=tilt)
    Mr = xf(p, tilt) @ rotm((0, 0, rot))
    box(M[mat], Mr @ Vector((r + 0.12, 0, 0.022)), (0.26, 0.026, 0.012), None, bev=0.004) if False else None
    tmp = Mr
    # handle as box transformed
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.26; v.co.y *= 0.026; v.co.z *= 0.011
    put(M[mat], bm, tmp @ Matrix.Translation((r + 0.11, 0, 0.022)), (1, 1, 1))
    bm.free()


def spoon(pos, rot=0, L=0.25, mat='wood_oak', tilt=None):
    Mr = xf(pos, (0, 0, rot)) if tilt is None else xf(pos, tilt)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= L * 0.75; v.co.y *= 0.012; v.co.z *= 0.007
    put(M[mat], bm, Mr @ Matrix.Translation((L * 0.375, 0, 0)), (1, 1, 1)); bm.free()
    lathe(M[mat], pos, [(0.001, 0), (0.02, 0.0), (0.022, 0.006), (0.001, 0.008)], 10, M=Mr @ Matrix.Translation((-0.02, 0, 0)), cap=False, scale=(1.0, 0.75, 1.0))


def frame_picture(pos, rot, w, h, kind='land', fcol='wood_dark', fw=0.035, seed=0, inner_mat='canvas_vc', mat_col=None):
    """wall frame centred at pos; local +y is wall normal direction(away from wall?). Frame lies in local XZ plane facing -y (towards viewer at -y)."""
    rr = random.Random(seed)
    Mr = xf(pos, rot)
    at = lambda l: Mr @ Vector(l)
    d = 0.022
    f = M[fcol]
    box(f, at((0, 0, h / 2 - fw / 2)), (w, d, fw), rot, bev=0.004, cfn=woodcol((1, 1, 1), 0.08, 8, seed, 0))
    box(f, at((0, 0, -h / 2 + fw / 2)), (w, d, fw), rot, bev=0.004)
    box(f, at((-w / 2 + fw / 2, 0, 0)), (fw, d, h - 2 * fw), rot, bev=0.004)
    box(f, at((w / 2 - fw / 2, 0, 0)), (fw, d, h - 2 * fw), rot, bev=0.004)
    iw, ih = w - 2 * fw, h - 2 * fw
    if mat_col:
        mm = 0.04
        box(M['paper'], at((0, -d / 2 + 0.0075, 0)), (iw, 0.003, ih), rot, bev=0, col=mat_col)
        iw -= 2 * mm; ih -= 2 * mm
    # canvas grid in local XY (faces +z) -> after rotate 90 about x: faces -y
    Mi = Mr @ Matrix.Translation((0, -d / 2 + 0.0055, 0)) @ rotm((90, 0, 0))
    inv = Mi.inverted()
    pal = rr.choice(['land', 'sea', 'night', 'flowers']) if kind == 'rand' else kind

    def pcol(p):
        q = inv @ p
        u = q.x / iw + 0.5; v = q.y / ih + 0.5
        return paint_fn(pal, u, v, rr_seed=seed)
    grid_mesh(M[inner_mat] if inner_mat in M else M['canvas_vc'], -iw / 2, iw / 2, -ih / 2, ih / 2, max(6, min(16, int(iw * 22))), max(6, min(16, int(ih * 22))), lambda x, y: 0.0, cfn=pcol, M=Mi)


def paint_fn(kind, u, v, rr_seed=0):
    def mix(a, b, t):
        t = max(0, min(1, t)); return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))
    L = lambda h: C(h)
    n = nz(u * 4, v * 4, rr_seed)
    if kind == 'land':
        hill = 0.38 + 0.12 * math.sin(u * 5 + rr_seed) + 0.05 * n
        hill2 = 0.26 + 0.1 * math.sin(u * 3 + 2 + rr_seed) + 0.04 * n
        if v > hill:
            return mix(L('#e9c98f'), L('#6f9fc7'), (v - hill) / 0.5)
        if v > hill2:
            return mix(L('#4f7a3c'), L('#7ba14f'), (v - hill2) / 0.2 + 0.3 * n)
        return mix(L('#2f4f2a'), L('#a08a4a'), v / 0.3 + 0.3 * n)
    if kind == 'sea':
        hor = 0.45
        if v > hor:
            return mix(L('#f2d7a0'), L('#7aa6cf'), (v - hor) / 0.5)
        return mix(L('#2f6f8f'), L('#8ac2d0'), v / hor + 0.15 * math.sin(v * 60 + n * 3))
    if kind == 'night':
        if v > 0.3:
            s = L('#1a2448') if v > 0.5 else L('#3a3f6a')
            if abs(nz(u * 40, v * 40, 3)) > 0.62:
                return (1.0, 0.95, 0.7)
            r2 = (u - 0.72) ** 2 + (v - 0.75) ** 2
            if r2 < 0.012:
                return L('#f4ecc0')
            return s
        return mix(L('#15201a'), L('#2a3a2a'), v / 0.3 + 0.2 * n)
    # flowers
    base = mix(L('#d8c9a0'), L('#e6d7b0'), v)
    for k in range(9):
        cx = (abs(nz(k, 1.7, rr_seed)) * 1.6) % 1.0
        cy = (abs(nz(k, 4.3, rr_seed)) * 1.6) % 0.7 + 0.15
        if (u - cx) ** 2 + (v - cy) ** 2 < 0.004:
            return [L('#c4453a'), L('#e0a030'), L('#7a4a9a')][k % 3]
    if 0.0 < v < 0.25 and (u * 7) % 1 < 0.3:
        return L('#4f7a3c')
    return base


def photo_frame(pos, rot, w=0.12, h=0.16, tilt=12, seed=0, fcol='wood_oak'):
    """small standing photo frame on a shelf. pos = bottom centre."""
    Mr = xf(pos, (0, 0, rot))
    at = lambda l: Mr @ Vector(l)
    rr = (tilt, 0, rot)
    fw = 0.012
    Mf = xf(pos, rr)
    atf = lambda l: Mf @ Vector(l)
    f = M[fcol]
    box(f, atf((0, 0, h / 2)), (w, 0.012, h), rr, bev=0.002)
    iw, ih = w - 2 * fw, h - 2 * fw
    Mi = Mf @ Matrix.Translation((0, -0.0065, h / 2)) @ rotm((90, 0, 0))
    inv = Mi.inverted()
    kind = ['land', 'sea', 'night', 'flowers'][seed % 4]
    def pcol(p):
        q = inv @ p
        r_ = paint_fn(kind, q.x / iw + 0.5, q.y / ih + 0.5, seed)
        g = 0.3 * r_[0] + 0.5 * r_[1] + 0.2 * r_[2]
        return (g * 1.0, g * 0.9, g * 0.75) if seed % 2 == 0 else r_
    grid_mesh(M['canvas_vc'], -iw / 2, iw / 2, -ih / 2, ih / 2, 6, 6, lambda x, y: 0.0, cfn=pcol, M=Mi)
    box(f, atf((0, 0.04, h * 0.45)), (0.03, 0.006, h * 0.85), (tilt + 20, 0, rot), bev=0.001) if False else None
    box(f, Mf @ Vector((0, 0.03, h * 0.48)), (0.012, 0.006, h * 0.9), (tilt + 28, 0, rot), bev=0.001)


def reading_glasses(pos, rot=0):
    Mr = xf(pos, (0, 0, rot))
    at = lambda l: Mr @ Vector(l)
    for s in (-1, 1):
        pts = [at((s * 0.03 + 0.022 * math.cos(a), 0.022 * math.sin(a), 0.0)) for a in [i * TAU / 14 for i in range(15)]]
        tube(M['iron_black'], pts, 0.0011, 4, caps=False)
        circle_fill = at((s * 0.03, 0, 0.0005))
        cyl(M['glass'], circle_fill, 0.0215, 0.0008, seg=12)
        tube(M['iron_black'], [at((s * 0.052, 0.0, 0.001)), at((s * 0.056, 0.05, 0.004)), at((s * 0.056, 0.095, 0.0))], 0.0011, 4)
    tube(M['iron_black'], [at((-0.008, 0.01, 0.0)), at((0, 0.014, 0.003)), at((0.008, 0.01, 0.0))], 0.001, 4, caps=False)


def feather_quill(pos, rot=0):
    Mr = xf(pos, (0, 0, rot))
    at = lambda l: Mr @ Vector(l)
    tube(M['paper'], [at((0, 0, 0.004)), at((0.12, 0.01, 0.022)), at((0.28, 0.05, 0.03))], 0.0016, 4)
    grid_mesh(M['paper'], 0.0, 0.2, -0.018, 0.018, 8, 2, lambda x, y: 0.0, cfn=lambda p: (0.92, 0.9, 0.85), M=Mr @ Matrix.Translation((0.1, 0.012, 0.022)) @ rotm((0, -6, 12)))


def inkwell(pos):
    lathe(M['glass'], pos, [(0.001, 0), (0.028, 0), (0.03, 0.005), (0.03, 0.035), (0.014, 0.045), (0.014, 0.05)], 12, cap=False)
    lathe(M['ink'], pos, [(0.001, 0.004), (0.026, 0.004), (0.026, 0.028), (0.001, 0.028)], 12, cap=False)


def coin_pile(pos):
    for i in range(5):
        cyl(M['brass'], Vector(pos) + V(rnd.uniform(-0.01, 0.01), rnd.uniform(-0.01, 0.01), 0.002 + i * 0.0025), 0.011, 0.002, seg=8)


def slippers(pos, rot=0, col='#8a3a3a'):
    for s in (-1, 1):
        Mr = xf(Vector(pos) + V(0, 0, 0), (0, 0, rot)) @ Matrix.Translation((s * 0.075, 0, 0))
        lathe(M['fur'], pos, [(0.001, 0), (0.45, 0.0), (1.0, 0.25), (0.95, 0.65), (0.55, 1.0), (0.001, 1.0)], 10, M=Mr @ Matrix.Translation((0, 0, 0)), cap=False, scale=(0.045, 0.11, 0.05), col=(0.92, 0.9, 0.86))
        lathe(M['leather_vc'], pos, [(0.001, 0), (0.9, 0.0), (1.0, 0.1), (0.9, 0.2), (0.001, 0.2)], 10, M=Mr @ Matrix.Translation((0, -0.002, -0.004)), cap=False, scale=(0.05, 0.118, 0.012), col=C(col))


def boot(pos, rot=0, col='#3b2a1f', h=0.3, s=1.0, tilt=None):
    Mr = xf(pos, (0, 0, rot) if tilt is None else tilt)
    at = lambda l: Mr @ Vector(l)
    c = C(col)
    # sole
    lathe(M['leather_vc'], pos, [(0.001, 0), (0.9, 0.0), (1.0, 0.5), (0.001, 0.5)], 12, M=Mr @ Matrix.Translation((0, 0.02 * s, 0)), cap=False, scale=(0.05 * s, 0.14 * s, 0.03), col=shade(c, 0.5))
    lathe(M['leather_vc'], pos, [(0.001, 0.0), (0.85, 0.0), (1.0, 0.12), (0.9, 0.35), (0.001, 0.4)], 12, M=Mr @ Matrix.Translation((0, 0.03 * s, 0.014)), cap=False, scale=(0.048 * s, 0.135 * s, 0.05), col=c)
    # shaft
    lathe(M['leather_vc'], pos, [(0.046 * s, 0.0), (0.047 * s, h * 0.5), (0.052 * s, h), (0.048 * s, h)], 12, M=Mr @ Matrix.Translation((0, -0.05 * s, 0.03)), cap=False, col=c)
    lathe(M['leather_vc'], pos, [(0.046 * s, 0.0), (0.05 * s, 0.0), (0.05 * s, 0.05)], 12, M=Mr @ Matrix.Translation((0, -0.05 * s, 0.03)), cap=False, col=shade(c, 0.6))
    lathe(M['leather_vc'], pos, [(0.05 * s, 0.0), (0.05 * s, 0.05)], 12, M=Mr @ Matrix.Translation((0, 0.0, 0.0)), cap=False, col=shade(c, 0.5), scale=(1, 0.0001, 1))


def hanging_hook_row(pos, n, spacing, rot=0, mat='iron_black'):
    Mr = xf(pos, (0, 0, rot))
    box(M['wood_dark'], pos, (n * spacing + 0.06, 0.03, 0.07), (0, 0, rot), bev=0.006, cfn=woodcol((1, 1, 1), 0.1, 8, 3, 0))
    for i in range(n):
        x = (i - (n - 1) / 2) * spacing
        pts = [Mr @ Vector(p) for p in [(x, -0.012, 0), (x, -0.06, 0.0), (x, -0.085, 0.02), (x, -0.09, 0.05)]]
        tube(M[mat], pts, 0.005, 6)
        sphere(M[mat], pts[-1] + V(0, 0, 0.005), 0.008, seg=6, rings=4)
        box(M[mat], Mr @ Vector((x, -0.012, 0)), (0.018, 0.004, 0.018), (0, 0, rot), bev=0.001)


def cloth_drape(mat, M_, w, h, nf=5, amp=0.03, col=(1, 1, 1), thick=0.01, seed=0, nx=10, ny=7, cfn=None):
    """single-sided vertical hanging cloth in local XZ plane, hangs down from z=0, folds along x (use a double-sided material)."""
    mat = M['curtain_vc']
    bm = bmesh.new()
    V_ = [[None] * (ny + 1) for _ in range(nx + 1)]
    for i in range(nx + 1):
        for j in range(ny + 1):
            x = -w / 2 + w * i / nx; z = -h * j / ny
            y = amp * math.sin(x / w * nf * TAU + seed) * (0.6 + 0.4 * (-z / h)) + 0.3 * amp * math.sin(z * 9 + x * 4)
            V_[i][j] = bm.verts.new((x, y, z))
    for i in range(nx):
        for j in range(ny):
            try:
                bm.faces.new([V_[i][j], V_[i + 1][j], V_[i + 1][j + 1], V_[i][j + 1]])
            except ValueError:
                pass
    put(mat, bm, M_, col, cfn)
    bm.free()
