"""Set dressing: everything small. Called after furniture placement."""
from int_scene import *

TZ = lambda z: z  # abs z already


def antlers(pos, rot, sc=1.0):
    f = Fr(pos, rot, None)
    # plaque
    f.lathe(M['wood_dark'], (0, -0.0, 0), [(0.001, 0), (0.11, 0.0), (0.12, 0.012), (0.1, 0.025), (0.001, 0.03)], r=(90, 0, 0) if False else (-90, 0, 0), seg=16, cap=False, col=(0.8, 0.7, 0.6), scale=(1.0, 1.25, 1.0))
    for s in (-1, 1):
        main = [Vector((s * 0.04, -0.05, 0.03)), Vector((s * 0.1, -0.1, 0.1)), Vector((s * 0.2, -0.13, 0.22)), Vector((s * 0.26, -0.11, 0.4)), Vector((s * 0.24, -0.06, 0.55))]
        f.tube(M['wood_pine'], [Vector((q.x, q.y, q.z)) for q in main], [0.022, 0.019, 0.016, 0.012, 0.006], seg=6, col=(0.85, 0.78, 0.65))
        for (a, b, L) in ((1, 1, 0.14), (2, 1, 0.16), (3, 1, 0.12)):
            base = main[a + 1]
            tip = base + Vector((s * 0.02, -0.04 - 0.02 * a, L * 0.9))
            f.tube(M['wood_pine'], [base, (base + tip) / 2 + Vector((s * 0.03, -0.01, 0)), tip], [0.011, 0.008, 0.003], seg=5, col=(0.85, 0.78, 0.65))


def rod_rack(pos, rot):
    """fishing rods on two fork brackets; local x across (length along x)"""
    f = Fr(pos, rot, None)
    for x in (-0.75, 0.75):
        f.box(M['wood_dark'], (x, 0.0, 0.0), (0.06, 0.03, 0.22), bev=0.004)
        for z in (-0.06, 0.06):
            f.tube(M['wood_dark'], [Vector((x, 0.0, z)), Vector((x, -0.08, z + 0.012))], 0.013, seg=6)
            f.tube(M['wood_dark'], [Vector((x + 0.03, -0.08, z + 0.012)), Vector((x + 0.03, -0.08, z + 0.05))], 0.008, seg=5)
    for k, z in enumerate((-0.06, 0.06)):
        L = 2.1 if k == 0 else 1.9
        pts = [Vector((-L / 2 + L * i / 10, -0.08 + 0.0, z + 0.03 + 0.002 * i)) for i in range(11)]
        f.tube(M['wood_oak'] if k == 0 else M['wood_pine'], pts, [0.011 - 0.0085 * (i / 10) for i in range(11)], seg=6)
        # cork grip and reel
        f.cyl(M['wood_pine'], (-L / 2 + 0.15, -0.08, z + 0.03), 0.016, 0.2, axis='x', seg=8, col=(0.75, 0.6, 0.45))
        f.cyl(M['brass'], (-L / 2 + 0.33, -0.08, z + 0.03 - 0.03), 0.025, 0.016, axis='y', seg=12)
        f.cyl(M['iron_black'], (-L / 2 + 0.33, -0.08, z + 0.03 - 0.03), 0.015, 0.03, axis='y', seg=8)
        # guides
        for i in range(2, 10, 2):
            f.tube(M['iron_black'], [pts[i] + Vector((0, 0, 0.0)), pts[i] + Vector((0, 0, 0.022))], 0.0012, seg=4)
    # landing net
    f.tube(M['wood_oak'], [Vector((0.25, -0.1, 0.11)), Vector((0.25, -0.1, -0.35))], 0.011, seg=6) if False else None


def crane_kettle(post, arm_end, kettle_pos):
    """iron crane in the firebox (world coords, abs z)."""
    p = Vector(post)
    e = Vector(arm_end)
    top = p.z + 0.55
    tube(M['iron_black'], [Vector((p.x, p.y, p.z)), Vector((p.x, p.y, top))], 0.012, seg=8)
    box(M['iron_black'], Vector((p.x, p.y, p.z + 0.01)), (0.05, 0.05, 0.02), bev=0.003)
    tube(M['iron_black'], [Vector((p.x, p.y, top - 0.05)), Vector((e.x, e.y, top - 0.0))], 0.009, seg=6)
    tube(M['iron_black'], [Vector((p.x, p.y, top - 0.36)), Vector((e.x, e.y, top - 0.02))], 0.006, seg=5)   # brace
    sphere(M['iron_black'], Vector((p.x, p.y, top + 0.012)), 0.018, seg=8, rings=4)
    # hook chain down to kettle bail
    k = Vector(kettle_pos)
    chain(e.x, e.y, top - 0.02, k.z + 0.2, M['iron_black'])
    kettle(k, rot=200, r=0.1, mat='iron_cast')


def tea_set(cx, cy, z, rot=0):
    f = Fr((cx, cy, z), rot, None)
    f.box(M['wood_walnut'], (0, 0, 0.012), (0.42, 0.27, 0.024), bev=0.004, cuts=2, g=0)
    for s in (-1, 1):
        f.box(M['wood_walnut'], (s * 0.19, 0, 0.032), (0.03, 0.25, 0.022), bev=0.003)
        f.box(M['wood_walnut'], (0, s * 0.12, 0.032), (0.36, 0.02, 0.022), bev=0.003)
    teapot(f.p((-0.08, 0.02, 0.024)), rot=rot + 20, col=C('#e9e4d8'))
    for x, y in ((0.1, 0.07), (0.11, -0.07)):
        q = f.p((x, y, 0.024))
        plate(q, r=0.055, col=C('#e9e4d8'))
        mug(q + V(0, 0, 0.012), col=C('#e9e4d8'), r=0.032, h=0.055, rot=rot + 30, fill=C('#6a3b1a'))
    bowl(f.p((-0.15, -0.08, 0.024)), r=0.04, h=0.035, col=C('#4e7299'), mat='ceramic_vc', inner=('food_vc', (0.95, 0.9, 0.8), 0.7))


def runner(cx, cy, z, L=1.5, W=0.36, tw=0.675):
    cl = C('#d8c9a6')
    def zf(x, y):
        d = max(0, abs(x) - tw)
        return z + 0.004 + 0.002 * math.sin(x * 25) - d * 6.0
    cloth(M['fabric_vc'], -L / 2, L / 2, -W / 2, W / 2, 36, 8, zf, lambda x, y: zf(x, y) - 0.004, cfn=lambda p: stripe_runner(p, cx, cy), M=Matrix.Translation((cx, cy, 0)), solid=False)


def stripe_runner(p, cx, cy):
    y = p.y - cy
    base = (0.72, 0.60, 0.40)
    if abs(abs(y) - 0.14) < 0.012 or abs(abs(y) - 0.165) < 0.006:
        base = (0.45, 0.08, 0.06)
    k = 1 + 0.06 * nz(p.x * 30, p.y * 30)
    return (base[0] * k, base[1] * k, base[2] * k)


def tea_towel(pos, rot, col='#d8d0bc'):
    cloth_drape(M['fabric_vc'], xf(pos, (0, 0, rot)), 0.26, 0.3, nf=3, amp=0.008, col=C(col), thick=0.004, nx=8, ny=5, cfn=lambda p: (0.85, 0.8, 0.7) if abs(math.sin(p.z * 40)) > 0.85 else (0.8, 0.75, 0.68))


def utensil_crock(pos):
    lathe(M['ceramic_vc'], pos, [(0.001, 0), (0.045, 0), (0.05, 0.03), (0.055, 0.14), (0.052, 0.15), (0.045, 0.14), (0.001, 0.01)], 14, cap=False, col=C('#7f93a0'))
    rr = random.Random(3)
    for i in range(5):
        a = rr.uniform(0, TAU)
        tip = Vector(pos) + V(math.cos(a) * 0.05, math.sin(a) * 0.05, 0.27)
        tube(M['wood_oak'], [Vector(pos) + V(0, 0, 0.04), tip], 0.007, seg=5)
        sphere(M['wood_oak'], tip, 0.022, seg=7, rings=4, sq=(1, 0.6, 0.35) if i % 2 else (0.5, 0.5, 1.4))


def paper_stack(pos, rot, n=6, size=(0.21, 0.297)):
    z = 0
    for i in range(n):
        box(M['paper'], Vector(pos) + V(0, 0, z + 0.0008), (size[0], size[1], 0.0016), (0, 0, rot + rnd.uniform(-6, 6)), bev=0, col=(0.95, 0.92, 0.85))
        z += 0.0016
    # handwriting lines on top sheet
    Mr = xf(pos, (0, 0, rot))
    for i in range(10):
        box(M['ink'], Mr @ Vector((0, size[1] * (0.38 - i * 0.07), z + 0.0012)), (size[0] * 0.7 * (0.6 + 0.4 * rnd.random()), 0.0025, 0.0004), (0, 0, rot), bev=0, col=(0.2, 0.18, 0.2))


def jewelry_box(pos, rot):
    f = Fr(pos, rot, None)
    f.box(M['wood_walnut'], (0, 0, 0.03), (0.2, 0.13, 0.06), bev=0.004, cuts=1)
    f.box(M['wood_walnut'], (0, 0, 0.068), (0.205, 0.135, 0.018), bev=0.004)
    f.box(M['brass'], (0, -0.067, 0.05), (0.02, 0.006, 0.02), bev=0.001)


def towel_fold(pos, rot, col='#d8d0bc'):
    f = Fr(pos, rot, None)
    f.pillow(M['fabric_vc'], (0, 0, 0.03), (0.3, 0.2, 0.06), n=5, flat=0, pinch=0, cfn=fab(C(col), 0.05), res=4)


def hanging_dress(pos, rot, col='#c8b48a'):
    c = C(col)
    cf = fab(c, 0.1, 8, 4)
    f = Fr(pos, rot, None)
    # hanger + blouse + skirt
    f.tube(M['wood_dark'], [Vector((-0.2, 0, -0.06)), Vector((0, 0, 0.0)), Vector((0.2, 0, -0.06))], 0.005, seg=5)
    cloth_drape(M['fabric_vc'], f.M @ Matrix.Translation((0, 0, -0.07)), 0.36, 0.85, nf=6, amp=0.03, col=c, thick=0.012, seed=2, nx=16, ny=10, cfn=cf)


def shoe_pair(pos, rot):
    boot(Vector(pos), rot=rot, col='#3b2a1f', h=0.28)
    boot(Vector(pos) + V(0.16 * math.cos(math.radians(rot)), 0.16 * math.sin(math.radians(rot)), 0), rot=rot + 10, col='#3b2a1f', h=0.28)


def decorate():
    rr = random.Random(21)
    # -------------------------------------------------- fireplace: crane + kettle (speculative firebox geometry)
    crane_kettle((-3.84, -0.56, F), (-4.0, -0.40, F), (-4.0, -0.40, F + 0.52))
    # mantel items (mantel top z=1.535)
    mz = 1.535
    candle_holder((-3.93, -0.85, mz), h=0.26, col='brass', cl=0.2, sc=1.2, inten=0.9, dist=5.0)
    candle_holder((-3.93, 0.85, mz), h=0.26, col='brass', cl=0.17, sc=1.2, inten=0.9, dist=5.0)
    candle_holder((-4.0, -0.62, mz), h=0.14, col='pewter', cl=0.12, sc=1.0, inten=0.5, dist=4.0)
    vase_flowers((-3.97, 0.3, mz), 'dried', h=0.24, r=0.06, n=8, vcol='#3e6a66', seed=12)
    photo_frame(V(-3.95, -0.3, mz), 90, w=0.14, h=0.19, tilt=-12, seed=1, fcol='wood_dark')
    photo_frame(V(-3.93, -0.05, mz), 100, w=0.11, h=0.15, tilt=-12, seed=2, fcol='brass')
    bowl(V(-3.95, 0.62, mz), r=0.08, h=0.05, col=C('#4e7299'), mat='ceramic_vc', inner=('food_vc', (0.6, 0.35, 0.15), 0.7))
    for i, (w, h) in enumerate(((0.16, 0.22), (0.15, 0.2), (0.14, 0.18))):
        book_flat(V(-4.0, 0.55 - 0.0, mz + i * 0.0 + (0.0 if i == 0 else [0, 0.035, 0.065][i])), (0.2, 0.15, 0.03), rotz=10 * i)
    # -------------------------------------------------- coffee table items
    tz = F + 0.42
    tea_set(-1.75, 0.65, tz, rot=90)
    book_open(V(-1.72, 0.05, tz), rotz=75, w=0.11, d=0.16, col='#5b3a26')
    reading_glasses(V(-1.66, 0.12, tz + 0.016), rot=40)
    candle_holder((-1.95, 0.32, tz), h=0.1, col='brass', cl=0.09, sc=1.0, inten=0.7, dist=4.5)
    # side table lamp
    oil_lamp((-3.4, 1.85, F + 0.58), sc=1.2, inten=1.3, dist=6.5)
    book_flat(V(-3.3, 1.72, F + 0.58), (0.17, 0.12, 0.03), rotz=20)
    mug(V(-3.5, 1.95, F + 0.58), col=C('#c44a3a'), r=0.034, h=0.08, rot=20, fill=C('#3a1f0e'))
    # -------------------------------------------------- walls: pictures, antlers, rods
    picture((1.385, 1.6, 1.95), -90, 0.95, 0.62, 'land', 3, fcol='wood_walnut', mat=(0.92, 0.88, 0.8))
    picture((1.39, 0.75, 1.9), -90, 0.32, 0.42, 'flowers', 5, fcol='wood_oak')
    picture((1.39, 2.45, 1.85), -90, 0.3, 0.4, 'night', 6, fcol='wood_dark')
    antlers((1.35, 1.0, 2.35), -90)
    picture((-4.23, -2.3, 1.85), 90, 0.75, 0.5, 'sea', 8, fcol='wood_walnut')
    rod_rack((-4.22, -2.4, 2.55), 90)
    picture((-1.85, -3.235, 1.75), 180, 0.42, 0.56, 'land', 9, fcol='wood_oak', mat=(0.9, 0.86, 0.78))
    picture((-4.0, -3.235, 1.9), 180, 0.3, 0.3, 'flowers', 10, fcol='wood_dark')
    picture((-0.4, 3.235, 2.5), 0, 0.5, 0.35, 'rand', 11, fcol='wood_white') if False else None
    # -------------------------------------------------- entry
    hanging_hook_row((1.0, -3.225, 1.9), 3, 0.17, rot=180)
    coat((0.83, -3.15, 1.86), 0, '#3f5a3f', seed=1, hooded=True)
    coat((1.0, -3.15, 1.84), 0, '#8a3a2e', h=0.85, seed=2)
    # straw hat on third hook
    lathe(M['straw'], V(1.17, -3.135, 1.86), [(0.001, 0), (0.09, 0.0), (0.16, 0.0), (0.16, 0.012), (0.08, 0.02), (0.075, 0.04), (0.07, 0.11), (0.001, 0.115)], 14, cap=False, rot=(-85, 0, 0))
    shoe_pair((0.95, -2.95, F), 75)
    boot(V(0.72, -2.7, F), rot=20, col='#5a3a24', h=0.22)
    umbrella_stand((1.22, -3.0))
    # -------------------------------------------------- dining table
    dz = F + 0.76
    runner(-3.0, -2.6, dz)
    for (px, py, rz) in ((-3.35, -2.25, 0), (-2.65, -2.25, 0), (-3.52, -2.6, 0), (-2.48, -2.6, 0)):
        plate(V(px, py, dz + 0.006), r=0.12, col=C('#ece7da'))
    for (px, py) in ((-3.35, -2.25), (-2.48, -2.6)):
        bowl(V(px, py, dz + 0.014), r=0.075, h=0.05, col=C('#4e7299'), mat='ceramic_vc', inner=('food_vc', (0.85, 0.6, 0.3), 0.6))
    for (px, py) in ((-2.65, -2.25), (-3.52, -2.6)):
        for k in range(2):
            apple(V(px + 0.02 * k, py + 0.01, dz + 0.03 + 0.03 * k), r=0.035)
    for (px, py) in ((-3.22, -2.38), (-2.78, -2.38), (-3.42, -2.78), (-2.58, -2.78)):
        lathe(M['glass'], V(px, py, dz), [(0.02, 0), (0.03, 0.004), (0.034, 0.1), (0.031, 0.1)], 12, cap=False)
    vase_flowers(V(-3.0, -2.6, dz + 0.004), 'wild', h=0.2, r=0.06, n=8, vcol='#6c8fa5', seed=7)
    cutting_board(V(-3.25, -2.78, dz), 10, (0.36, 0.2))
    loaf(V(-3.25, -2.78, dz + 0.024), rot=10, L=0.26, w=0.11, h=0.075)
    knife(V(-3.0, -2.75, dz), rot=80, L=0.22)
    cheese(V(-2.75, -2.85, dz + 0.0), rot=30)
    box(M['wood_oak'], V(-2.75, -2.85, dz + 0.005), (0.18, 0.18, 0.01), bev=0.003)
    candle_holder((-2.85, -2.5, dz), h=0.12, col='pewter', cl=0.1, sc=1.0, inten=0.6, dist=4.0)
    # pendant lantern
    lantern((-3.0, -2.6, 2.3), h=0.3, w=0.16, chain_to=3.17, sc=1.6, inten=1.8, dist=8.0)
    # -------------------------------------------------- kitchen items
    cz = F + 0.9
    # stove top
    tip = kettle(V(-3.68, 2.83, F + 0.811), rot=180, r=0.11, mat='iron_cast')
    kettle_anchor(tip + V(-0.0, -0.0, 0.03))
    pot(V(-3.33, 3.05, F + 0.811), r=0.1, h=0.12, mat='copper', lid=True, rot=(0, 0, 180))
    pot(V(-3.33, 2.82, F + 0.811), r=0.075, h=0.09, mat='iron_cast', lid=True, rot=(0, 0, 180))
    bowl(V(-3.5, 3.1, F + 1.222 + 0.0), r=0.09, h=0.05, col=C('#e9e4d8'), mat='ceramic_vc')
    for i in range(3):
        mug(V(-3.74 + i * 0.1, 3.1, F + 1.222), col=C(rr.choice(['#c44a3a', '#4e7299', '#e9e4d8'])), r=0.032, h=0.07, rot=180)
    # counter left slab
    cutting_board(V(-2.85, 2.9, cz), 8, (0.4, 0.26))
    for i, c in enumerate([(0.95, 0.5, 0.15), (0.95, 0.5, 0.15), (0.95, 0.5, 0.15)]):
        carrot(V(-2.95 + 0.04 * i, 2.85 + 0.03 * i, cz + 0.022 + 0.013), rot=(90, 0, 70 + 10 * i), L=0.16)
    for i in range(3):
        onion(V(-2.72 + 0.05 * i, 2.98, cz + 0.022 + 0.03), r=0.03)
    knife(V(-2.75, 2.75, cz + 0.022), rot=35, L=0.22)
    bowl(V(-2.68, 3.1, cz), r=0.09, h=0.06, col=C('#d9c7a0'), mat='ceramic_vc', inner=('food_vc', (0.9, 0.85, 0.5), 0.5))
    utensil_crock(V(-2.98, 3.14, cz))
    # sink side: soap, brush, towel
    box(M['wax'], V(-2.45, 3.0, cz + 0.015), (0.06, 0.04, 0.03), bev=0.006, col=(0.85, 0.8, 0.7))
    # right slab
    for i in range(3):
        jar(V(-1.75 + i * 0.1, 3.14, cz), r=0.045, h=0.15 - 0.01 * i, content=(0.8, rr.choice([(0.85, 0.75, 0.4), (0.7, 0.2, 0.15), (0.5, 0.65, 0.25)])), lidcol=(0.72, 0.5, 0.25))
    lantern((-1.56, 3.06, cz + 0.17), h=0.3, w=0.14, chain_to=None, sc=1.3, inten=1.2, dist=7.0)
    bowl(V(-1.75, 2.82, cz), r=0.12, h=0.07, col=C('#b5562f'), mat='ceramic_vc')
    heap_apples(V(-1.75, 2.82, cz + 0.03), 0.04, 0.04, 0.0, n=7, seed=5)
    cutting_board(V(-1.6, 2.85, cz), -15, (0.34, 0.22))
    loaf(V(-1.6, 2.86, cz + 0.024), rot=-15, L=0.27, w=0.12, h=0.08)
    plate(V(-2.0, 2.78, cz), r=0.1, col=C('#ece7da'))
    cheese(V(-2.0, 2.78, cz + 0.018), rot=0)
    tea_towel((-2.45, 2.62, cz + 0.0), 0) if False else None
    # over the barrel
    bucket(V(-1.2, 2.93, F + 0.8 + 0.0), r=0.12, h=0.22, water=True, handle=True) if False else None
    bucket(V(-1.0, 2.42, F), r=0.14, h=0.27, water=True)
    # floor goodies
    c = crate(V(-0.35, 2.45, F), (0.5, 0.36, 0.26), rot=6)
    heap_apples(V(-0.35, 2.45, F + 0.17), 0.18, 0.12, 0.0, n=15, seed=8)
    bp = basket(V(0.45, 2.42, F), r=0.2, h=0.22, handle=True)
    for i in range(9):
        sphere(M['food_vc'], V(0.45 + rr.uniform(-0.12, 0.12), 2.42 + rr.uniform(-0.12, 0.12), F + 0.2 + rr.uniform(0, 0.04)), 0.032, seg=6, rings=4, sq=(1.2, 1.0, 0.85), col=jit((0.62, 0.5, 0.3), 0.15))
    basket(V(-0.85, 2.2, F), r=0.14, h=0.14, handle=False)
    # herbs, braids hanging from beams
    for i, (hx, hy) in enumerate([(-0.9, 2.3), (-0.4, 2.6), (0.3, 2.55), (0.8, 2.4), (-2.6, 2.3), (-3.5, 2.2), (-1.6, 2.2)][:6]):
        herb_bundle(V(hx, hy, 3.12), L=0.32 + 0.05 * (i % 3), kind=['lav', 'herb', 'dry', 'wheat', 'chili', 'lav', 'herb'][i], seed=20 + i, hang_to=None)
    braid(V(0.05, 2.72, 3.12), 'onion', n=7, seed=1)
    braid(V(-1.4, 2.35, 3.12), 'garlic', n=8, seed=2)
    braid(V(-2.0, 2.55, 3.12), 'onion', n=6, seed=3)
    herb_bundle(V(1.0, -2.8, 3.12), L=0.3, kind='lav', seed=31)
    herb_bundle(V(-0.4, -1.2, 3.12), L=0.3, kind='dry', seed=32)
    # -------------------------------------------------- bedroom
    bz = F + 0.62
    oil_lamp((1.97, 3.03, bz), sc=1.2, inten=1.1, dist=5.5)
    book_flat(V(2.12, 3.0, bz), (0.17, 0.12, 0.03), rotz=-15)
    lathe(M['glass'], V(1.85, 2.92, bz), [(0.02, 0), (0.03, 0.004), (0.034, 0.1), (0.031, 0.1)], 12, cap=False)
    candle_holder((4.05, 3.05, bz), h=0.14, col='brass', cl=0.12, sc=1.1, inten=0.9, dist=5.0)
    book_flat(V(4.0, 2.9, bz), (0.18, 0.13, 0.03), rotz=10)
    book_flat(V(4.0, 2.9, bz + 0.03), (0.16, 0.12, 0.025), rotz=-5)
    reading_glasses(V(3.92, 2.92, bz + 0.056), rot=20)
    # dresser
    dtz = F + 0.9
    jewelry_box((1.88, 0.62, dtz), 90)
    bottle(V(1.9, 1.2, dtz), r=0.03, h=0.2, col=(0.35, 0.55, 0.65), alpha_mat='glass_amber', cork=True)
    bottle(V(1.85, 1.12, dtz), r=0.025, h=0.15, col=(0.6, 0.35, 0.5), alpha_mat='glass_amber', cork=True)
    candle_holder((1.88, 0.92, dtz), h=0.12, col='brass', cl=0.09, sc=1.0, inten=0.6, dist=4.0)
    photo_frame(V(1.75, 0.78, dtz), 90, w=0.13, h=0.17, tilt=-12, seed=3)
    photo_frame(V(1.75, 1.38, dtz), 90, w=0.12, h=0.16, tilt=-12, seed=4, fcol='wood_walnut')
    towel_fold((1.95, 1.15, dtz), 90)
    vase_flowers(V(1.85, 0.45 + 0.08, dtz), 'lav', h=0.14, r=0.035, n=7, vcol='#d9c7a0', seed=3)
    # desk
    sz = F + 0.76
    paper_stack((3.9, -0.65, sz + 0.004), 100)
    paper_stack((3.88, -1.12, sz + 0.004), 80, n=3)
    inkwell(V(3.92, -0.95, sz)); feather_quill(V(3.93, -0.98, sz + 0.03), 160)
    oil_lamp((4.1, -0.45, sz), sc=1.2, inten=1.2, dist=6.0)
    book_open(V(3.75, -1.32, sz + 0.0), rotz=100, w=0.1, d=0.15, col='#3a4a5a')
    for i in range(3):
        book_flat(V(3.75, -0.42, sz + 0.03 * i), (0.22, 0.16, 0.03), rotz=rr.uniform(-10, 10))
    coin_pile(V(3.7, -0.9, sz))
    # trunk top
    towel_fold((3.0, 0.92, F + 0.46), 0, col='#8c3a2e')
    # shelf above headboard + bed wall decor
    wall_shelf((3.3, 3.15, 2.1), 180, W=0.9, D=0.2, seed=6)
    picture((1.68, -1.0, 2.0), 90, 0.4, 0.5, 'land', 12, fcol='wood_oak')
    picture((4.23, 0.35, 2.05), -90, 0.5, 0.36, 'sea', 13, fcol='wood_walnut')
    picture((4.23, -2.3, 1.9), -90, 0.42, 0.56, 'flowers', 14, fcol='wood_oak', mat=(0.9, 0.86, 0.78))
    picture((2.0, -3.235, 1.9), 180, 0.3, 0.4, 'night', 15, fcol='wood_dark')
    picture((3.85, -3.235, 1.75), 180, 0.26, 0.26, 'land', 16, fcol='wood_white')
    picture((3.05, 3.235, 2.6), 0, 0.5, 0.0001, 'land', 1, fcol='wood_dark') if False else None
    hanging_hook_row((1.655, -1.4, 1.85), 2, 0.22, rot=90)
    hanging_dress((1.56, -1.4, 1.8), 90, '#b8a27a') if False else None
    coat((1.56, -1.3, 1.82), 90, '#6f5a7a', h=0.8, w=0.38, seed=6)
    coat((1.56, -1.52, 1.82), 90, '#9a7a4a', h=0.7, w=0.34, seed=7)
    slippers(V(2.02, 1.72, F), rot=70)
    slippers(V(2.55, 0.35, F), rot=-30, col='#3a5a6a')
    # rocking chair extras
    f = Fr((3.8, -2.7, F), face((3.8, -2.7), (2.8, -1.8)), None)
    f.cloth(M['knit_vc'], -0.22, 0.22, -0.3, 0.3, 10, 12, lambda x, y: 0.5 + 0.02 * math.sin(y * 14 + x * 5) - max(0, y - 0.18) * 1.0 + (0.0), 0.44, cfn=lambda p: (0.7, 0.62, 0.45) if int(p.x * 25 + 50) % 3 else (0.3, 0.42, 0.42), M=Matrix.Translation((0, 0.05, 0.0)))
    # curtains
    curtain(1, -2.9, -3.235, 2.78, 1.3, 1.42, 180, tied=True, col='#c9b79a', rod_y=0.05)
    curtain(2, 2.9, -3.235, 2.78, 1.3, 2.4, 180, tied=True, col='#9fb3a8', rod_y=0.05)
    curtain(3, 4.235, -0.9, 2.8, 1.15, 2.4, -90, tied=True, col='#9fb3a8', rod_y=0.05)
    curtain(4, 4.235, 1.6, 2.8, 1.15, 1.35, -90, tied=True, col='#9fb3a8', rod_y=0.05)
    curtain(5, 2.2, 3.235, 2.78, 1.3, 1.42, 0, tied=True, col='#c9b79a', rod_y=0.05)
    curtain(6, -2.2, 3.235, 2.78, 1.3, 1.0, 0, tied=True, col='#d9d0bc', rod_y=0.05)
    add_interactables()


def add_interactables():
    I = interact
    I('fireplace_kettle', (-4.0, -0.40, F + 0.62), '벽난로에 걸린 무쇠 주전자')
    I('mantel', (-3.95, 0.0, 1.75), '벽난로 선반 - 촛대와 사진들')
    I('bookshelf', (-3.75, 2.0, 1.5), '빼곡한 책장')
    I('sofa', (0.8, 1.25, 0.95), '푹신한 소파와 담요')
    I('armchair_yellow', (-2.55, 1.75, 1.0), '노란 안락의자')
    I('armchair_teal', (-2.6, -0.75, 1.0), '청록빛 안락의자')
    I('tea_set', (-1.75, 0.65, F + 0.55), '식어가는 찻주전자')
    I('open_book', (-1.72, 0.05, F + 0.5), '펼쳐진 책과 돋보기 안경')
    I('dining_table', (-3.0, -2.6, F + 0.9), '들꽃이 놓인 식탁')
    I('stove', (-3.5, 2.95, F + 0.95), '주철 요리 난로')
    I('stove_kettle', (-3.68, 2.83, F + 1.0), '김이 나는 주전자')
    I('sink_pump', (-2.2, 3.1, F + 1.25), '손 펌프가 달린 싱크대')
    I('hutch', (-0.4, 3.0, F + 1.4), '접시가 가득한 찬장')
    I('pantry', (0.5, 2.8, F + 1.2), '식료품 저장장')
    I('apple_crate', (-0.35, 2.45, F + 0.35), '사과 상자')
    I('flour_sack', (1.08, 3.0, F + 0.6), '밀가루 포대')
    I('hanging_herbs', (-0.4, 2.6, 2.8), '천장에 매달린 말린 허브')
    I('longcase_clock', (-1.0, -2.95, F + 1.6), '괘종시계')
    I('coats', (0.9, -3.1, 1.8), '문 옆 외투와 밀짚모자')
    I('antlers', (1.35, 1.0, 2.35), '사슴뿔 장식')
    I('rod_rack', (-4.2, -2.4, 2.55), '낚싯대 걸이')
    I('bed', (3.05, 2.2, F + 0.7), '조각보 이불이 덮인 침대')
    I('bedside_lamp', (1.97, 3.03, F + 0.8), '침대 옆 오일 램프')
    I('wardrobe', (1.93, -2.35, F + 1.2), '조각이 새겨진 옷장')
    I('dresser', (1.9, 0.95, F + 1.1), '거울 달린 서랍장')
    I('desk', (3.95, -0.9, F + 0.95), '편지와 잉크가 놓인 책상')
    I('trunk', (3.05, 0.92, F + 0.5), '침대 발치의 트렁크')
    I('rocking_chair', (3.8, -2.7, F + 0.7), '흔들의자')
