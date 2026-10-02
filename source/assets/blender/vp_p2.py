"""Village props batch 2 (stalls etc.)"""
from vp_h2 import *

TOPZ = 0.96
STALL_CAM = lambda m: [((3.6, -4.6, 2.3), (0, 0, 1.3), 40), ((-3.6, 4.2, 2.6), (0, 0, 1.4), 40),
                       ((0.9, -2.3, 1.7), (0, -0.6, 1.0), 45), ((-0.9, -2.0, 1.5), (-0.2, -0.65, 1.0), 45)]


@prop('market_stall_a', '과일 채소 가판대', ao_len=2.0, cam=STALL_CAM)
def market_stall_a():
    stall_frame(H('#b59a72'), 1, (H('#b8403a'), H('#e9dcc0')))
    r = random.Random(1)
    # crate of apples
    S = (0.52, 0.4, 0.22)
    f = crate((-1.0, -0.68, TOPZ), 3, S, seed=1)
    cols = [H('#b8342a'), H('#c9a02e'), H('#9c2a1e'), H('#7da13a')]
    mk = lambda p, rad: apple(p, rad, jitter_col(cols[r.randrange(4)] if r.random() < 0.6 else cols[0], 0.15))
    box('soil', f.p((0, 0, 0.1)), (0.46, 0.34, 0.12), rot=(0, 0, 3), col=(0.08, 0.05, 0.04), skip_down=True)
    fill_layer(f, S, 0.17, 0.045, mk)
    # crate of plums / tomatoes
    f = crate((-0.38, -0.68, TOPZ), -4, S, seed=2)
    box('soil', f.p((0, 0, 0.1)), (0.46, 0.34, 0.12), rot=(0, 0, -4), col=(0.08, 0.05, 0.04))
    tm = lambda p, rad: tomato(p, rad, jitter_col(H('#c4301f'), 0.12))
    fill_layer(f, S, 0.16, 0.045, tm)
    # pear basket
    f = wicker_basket((0.28, -0.68, TOPZ), R=0.22, h=0.24, rot=0, handle=True, seed=3, rows=3, NW=22)
    pc = [H('#b8b648'), H('#c8b24a'), H('#a2a83a')]
    for i in range(6):
        a = TAU * i / 6
        pear((0.28 + math.cos(a) * 0.1, -0.68 + math.sin(a) * 0.1, TOPZ + 0.14 + r.uniform(0, .02)), 0.035, jitter_col(pc[i % 3], 0.1), rot=(r.uniform(-30, 30), r.uniform(-30, 30), 0))
    for i in range(2):
        pear((0.28 + r.uniform(-0.05, 0.05), -0.68 + r.uniform(-0.05, 0.05), TOPZ + 0.2), 0.035, jitter_col(pc[i % 3], 0.1), rot=(r.uniform(-30, 30), r.uniform(-30, 30), 0))
    # cabbages
    for i, (x, y) in enumerate(((0.85, -0.7), (1.05, -0.58))):
        cabbage((x, y, TOPZ + 0.085), 0.1, jitter_col(H('#7fa352'), 0.12))
    # carrots bunch and onions
    carrot_bunch((0.0, -0.45, TOPZ), 8, 5)
    # onions basket on left back
    f = crate((-1.15, -0.45, TOPZ), 0, (0.3, 0.2, 0.1), seed=5)
    for i in range(2):
        onion((-1.15 + r.uniform(-0.1, 0.1), -0.45 + r.uniform(-0.06, 0.06), TOPZ + 0.07 + r.uniform(0, 0.03)), 0.03, jitter_col(H('#c28a3a'), 0.15))
    # ground crates (potatoes), sack
    for (x, y, z, rot) in ((-1.0, 0.45, 0.0, 10), (-0.4, 0.5, 0.0, -6)):
        f = crate((x, y, z), rot, (0.5, 0.38, 0.22), seed=int(x * 9))
        box('soil', f.p((0, 0, 0.1)), (0.46, 0.34, 0.12), rot=(0, 0, rot), col=(0.12, 0.09, 0.06))
        if z == 0.0:
            fill_layer(f, (0.5, 0.38, 0.22), 0.17, 0.09, lambda p, rad: potato(p, rad, jitter_col(H('#a8885a'), 0.12)))
    # shelf goods: jars + baskets
    for i in range(0):
        x = -1.0 + i * 0.9
        lathe('ceramic', (x, 0.8, 1.07), [(0, 0), (0.05, 0), (0.055, 0.05), (0.05, 0.14), (0.03, 0.17), (0.035, 0.19), (0.0, 0.19)], seg=12, col=jitter_col(H('#c9b28a') if i % 2 else H('#8a6a48'), 0.1), cap=False, auto=False)
    for i in range(1):
        wicker_basket((0.0, 0.8, 1.545), R=0.14, h=0.12, handle=False, seed=i, rows=0)
    # sack of grain on ground (burlap) near right post
    lathe('burlap', (1.15, 0.4, 0), [(0.0, 0), (0.17, 0.0), (0.2, 0.08), (0.2, 0.35), (0.14, 0.52), (0.07, 0.6), (0.09, 0.64), (0.0, 0.64)], seg=14, col=H('#b49a6a'), cap=False, auto=False)
    cyl('rope', (1.15, 0.4, 0.55), 0.08, 0.025, seg=10, col=ROPE_C)


@prop('market_stall_b', '빵 생선 가판대', ao_len=2.0, cam=STALL_CAM)
def market_stall_b():
    stall_frame(H('#8a6e4c'), 7, (H('#4c7a47'), H('#e6dcc2')), hang_rod=True)
    r = random.Random(2)
    crust = H('#b7783d')

    def boule(c, rad, rot=0.0):
        cfn = lambda p, c=c: mixc(crust, H('#e9c88a'), max(0.0, 0.5 - abs(math.sin((p.x - c[0]) * 30 + (p.y - c[1]) * 30)) * 3) * (1 if p.z > c[2] + 0.02 else 0)) if False else mixc(mixc(crust, H('#8a5226'), max(0, (p.z - c[2]) / rad) * 0.35), H('#e8cf9c'), 0.5 * max(0, 1 - abs(((p.x - c[0]) + (p.y - c[1])) * 28 % 1.0 - 0.5) * 7) * (1 if p.z > c[2] + 0.45 * rad else 0))
        sphere('food', c, rad, seg=12, rings=7, sq=(1, 1, 0.62), cfn=cfn, rot=(0, 0, rot))

    def loaf(c, rot):
        crust2 = jitter_col(crust, 0.1)
        cfn = lambda p, c=c: mixc(crust2, H('#e8cf9c'), 0.55 * max(0, 1 - abs((((p.x - c[0]) * math.cos(math.radians(rot)) + (p.y - c[1]) * math.sin(math.radians(rot))) * 22) % 1.0 - 0.5) * 6) * (1 if p.z > c[2] + 0.03 else 0))
        sphere('food', c, 0.15, seg=14, rings=8, sq=(1.05, 0.55, 0.38), cfn=cfn, rot=(0, 0, math.radians(rot)))
    # wooden tray with boules
    box('pine', (-0.95, -0.68, TOPZ + 0.015), (0.7, 0.42, 0.03), bev=0.004, col=H('#a58a62'))
    for sx in (-1, 1):
        box('pine', (-0.95 + sx * 0.34, -0.68, TOPZ + 0.045), (0.02, 0.42, 0.04), bev=0.003, col=H('#a58a62'))
    for sy in (-1, 1):
        box('pine', (-0.95, -0.68 + sy * 0.2, TOPZ + 0.045), (0.7, 0.02, 0.04), bev=0.003, col=H('#a58a62'))
    for i, (dx, dy) in enumerate(((-0.2, -0.08), (0.05, -0.1), (0.25, -0.06), (-0.1, 0.1), (0.15, 0.09))):
        boule((-0.95 + dx, -0.68 + dy, TOPZ + 0.04), 0.085, r.uniform(0, 3))
    # long loaves
    for i in range(3):
        loaf((-0.45 + 0.0, -0.6 - 0.04 + i * 0.12, TOPZ + 0.06 + i * 0.0), r.uniform(-12, 12))
    # basket of baguettes standing
    wicker_basket((0.1, -0.62, TOPZ), R=0.15, h=0.3, taper=0.8, handle=False, seed=4, stakes=18, rows=3, NW=22)
    for i in range(7):
        a = TAU * i / 7
        c = (0.1 + math.cos(a) * 0.045, -0.62 + math.sin(a) * 0.045, TOPZ + 0.05)
        lathe('food', c, [(0.0, 0.0), (0.02, 0.01), (0.03, 0.15), (0.03, 0.4), (0.022, 0.52), (0.0, 0.54)], seg=8,
              cfn=lambda p, c=c: mixc(crust, H('#e6c88a'), 0.5 * max(0, 1 - abs(((p.z * 20) + (math.atan2(p.y - c[1], p.x - c[0]))) % 1.0 - 0.5) * 6)), cap=False, rot=(r.uniform(-7, 7), r.uniform(-7, 7), 0), auto=False)
    # rolls on cloth
    box('linen', (0.55, -0.55, TOPZ + 0.004), (0.34, 0.34, 0.008), bev=0.001, col=H('#d8cfba'), rot=(0, 0, 8))
    for i in range(3):
        a = TAU * i / 3
        sphere('food', (0.55 + math.cos(a) * 0.09, -0.55 + math.sin(a) * 0.09, TOPZ + 0.035), 0.04, seg=9, rings=5, sq=(1.2, 1, 0.75), col=jitter_col(crust, 0.12), rot=(0, 0, a))
    sphere('food', (0.55, -0.55, TOPZ + 0.05), 0.04, seg=9, rings=5, sq=(1.2, 1, 0.75), col=jitter_col(crust, 0.12))
    # fish slab with ice
    box('stone', (1.05, -0.68, TOPZ + 0.02), (0.62, 0.44, 0.04), bev=0.006, col=H('#8a8780'), cfn=stone_cfn(H('#7d7a74'), H('#9a968c'), 4, 3))
    for i in range(3):
        rock('plain_gloss', (1.05 + r.uniform(-0.26, 0.26), -0.68 + r.uniform(-0.17, 0.17), TOPZ + 0.045), (0.05, 0.05, 0.035), seed=i, col=(0.8, 0.88, 0.92), cuts=1, rot=(0, 0, r.uniform(0, 3)))
    for i in range(3):
        M0 = xf((0.83 + 0.0, -0.8 + i * 0.075, TOPZ + 0.085), (r.uniform(-10, 10), 0, r.uniform(-14, 14) + 10 * (-1) ** i))
        fish(M0, L=0.27, Hh=0.06, Wd=0.032, back=H('#4a6070'), belly=H('#d8dcd8'), bend=0.05)
    M0 = xf((1.3, -0.56, TOPZ + 0.085), (0, 0, 190))
    fish(M0, L=0.22, Hh=0.07, Wd=0.034, back=H('#6a6a4a'), belly=H('#d2cfb0'), bend=-0.05)
    # hanging dried fish on rod
    for i in range(1):
        x = -0.4 + r.uniform(-0.04, 0.04)
        top = 2.12
        tube('rope', [Vector((x, -0.7, 2.17)), Vector((x, -0.7, top))], 0.004, seg=4, col=ROPE_C)
        M0 = Matrix.Translation((x, -0.7, top)) @ rotm((0, 90, 0))
        fish(M0, L=0.28, Hh=0.055, Wd=0.026, back=H('#8a7a5a'), belly=H('#b8a47a'), seed=i)
    # sausage string on hooks
    pts = [Vector((-1.4 + 2.8 * i / 20, -0.7, 2.18 - 0.1 * math.sin(math.pi * i / 20))) for i in range(21)]
    # sausages hanging: three bunches
    for bx in (0.1,):
        for k in range(4):
            x = bx + k * 0.05
            tube('rope', [Vector((x, -0.7, 2.17)), Vector((x, -0.7, 2.0))], 0.003, seg=4, col=ROPE_C)
            lathe('food', (x, -0.7, 1.72), [(0, 0), (0.016, 0.01), (0.022, 0.07), (0.022, 0.2), (0.016, 0.26), (0.0, 0.27)], seg=8, col=jitter_col(H('#7a3a28'), 0.15), cap=False, auto=False)
            cyl('rope', (x, -0.7, 1.99), 0.008, 0.01, seg=5, col=ROPE_C)
    # shelf: baskets with bread, crocks
    for i in range(1):
        wicker_basket((0.0, 0.8, 1.055), R=0.16, h=0.14, handle=False, seed=i + 9, rows=0)
        for j in range(2):
            sphere('food', (-1.1 + i * 0.5 + r.uniform(-0.05, 0.05), 0.8 + r.uniform(-0.05, 0.05), 1.18), 0.055, seg=8, rings=5, sq=(1, 1, 0.7), col=jitter_col(crust, 0.12))
    for i in range(1):
        lathe('ceramic', (-0.5, 0.8, 1.555), [(0, 0), (0.07, 0), (0.08, 0.08), (0.075, 0.18), (0.085, 0.2), (0.0, 0.2)], seg=12, col=jitter_col(H('#7a5a3a'), 0.12), cap=False, auto=False)
    # ground: barrel of salt fish + crate
    barrel(Matrix.Translation((1.1, 0.4, 0)), r_mid=0.24, r_end=0.2, h=0.7, N=9, open_top=True, hoops=3, col=H('#8a7050'), seed=3)
    
    
    


def pot_jug(c, h, r, col, mat='terracotta', neck=0.4, handle=True, seed=0):
    prof = [(0, 0), (r * 0.6, 0), (r * 0.85, h * 0.07), (r, h * 0.35), (r * 0.9, h * 0.6), (r * neck * 1.1, h * 0.82), (r * neck, h * 0.92), (r * neck * 1.25, h), (r * neck * 1.0, h)]
    lathe(mat, c, prof, seg=10, col=col, cap=False, auto=False)
    lathe(mat, c, [(r * neck * 1.05, h), (r * neck * 0.8, h - 0.015), (0, h - 0.03)], seg=8, col=mixc(col, (0.1, 0.06, 0.04), 0.5), cap=False, auto=False)
    if handle:
        pts = []
        for i in range(10):
            a = math.pi * i / 9
            pts.append(Vector((c[0] + r * neck * 1.1 + math.sin(a) * r * 0.75, c[1], c[2] + h * 0.88 - (1 - math.cos(a)) * 0.5 * h * 0.5)))
        tube(mat, pts, 0.01, seg=6, col=col)


def bowl(c, r, h, col, mat='terracotta'):
    prof_o = [(0, 0), (r * 0.45, 0), (r * 0.6, h * 0.1), (r * 0.9, h * 0.6), (r, h)]
    lathe(mat, c, prof_o, seg=12, col=col, cap=False, auto=False)
    lathe(mat, c, [(r, h), (r - 0.008, h), (r * 0.88 - 0.008, h * 0.6), (r * 0.58, h * 0.14), (0, h * 0.1)], seg=12, col=mixc(col, (0.9, 0.85, 0.75), 0.25) if mat == 'ceramic' else mixc(col, (0.2, 0.1, 0.05), 0.25), cap=False, auto=False)


@prop('market_stall_c', '도자기 가판대', ao_len=2.0, cam=STALL_CAM)
def market_stall_c():
    stall_frame(H('#9a8e7a'), 13, (H('#37588a'), H('#d9ae52')), hang_rod=True)
    r = random.Random(3)
    tc = [H('#c9754a'), H('#b8603a'), H('#d08a5c')]
    cc = [H('#d8cfb4'), H('#5a7f8a'), H('#3f5f86'), H('#a88a52')]
    # bowl stacks
    for k, x in enumerate((-1.1, -0.75)):
        for i in range(3):
            bowl((x + r.uniform(-.004, .004), -0.7, TOPZ + i * 0.04), 0.1, 0.07, jitter_col(cc[k + 1] if k else cc[0], 0.05), mat='ceramic')
    # jugs
    for i, x in enumerate((-0.3, -0.05, 0.2)):
        pot_jug((x, -0.72 + 0.04 * (i % 2), TOPZ), 0.25 - 0.03 * (i % 2), 0.09, jitter_col(tc[i % 3], 0.08), seed=i)
    # glazed pots
    for i, x in enumerate((0.55, 0.8)):
        pot_jug((x, -0.7, TOPZ), 0.2, 0.1, cc[1 + i], mat='ceramic', neck=0.7, handle=False)
        pot_jug((x + 0.12 * (1 - i), -0.52, TOPZ), 0.12, 0.07, cc[3 - i], mat='ceramic', neck=0.6, handle=False)
    # plate stack on edge
    for i in range(4):
        lathe('ceramic', (1.1, -0.65, TOPZ + i * 0.012), [(0, 0), (0.1, 0.0), (0.13, 0.02), (0.13, 0.025), (0.09, 0.012), (0, 0.006)], seg=12, col=jitter_col(cc[0], 0.04), cap=False, auto=False)
    # cheese: whole wheels + a cut one
    cfn = lambda p: mixc(H('#d9a93f'), H('#b9842a'), min(1, max(0, (0.5 - abs(p.z - TOPZ - 0.06) * 10))) * 0.2)
    for i, (x, y) in enumerate(((1.1, -0.45), (1.35, -0.7))):
        cyl('food', (x, y, TOPZ + 0.05), 0.14, 0.1, seg=14, col=jitter_col(H('#d9a93f'), 0.08), bev=0.012)
    cyl('food', (1.1, -0.45, TOPZ + 0.15), 0.12, 0.09, seg=14, col=H('#e0b34a'), bev=0.012)
    cyl('food', (1.0, -0.88, TOPZ + 0.05), 0.12, 0.1, seg=14, col=H('#c99a3a'), bev=0.01)
    # cheese wedge cut
    bm = prism([(0, 0), (0.12, -0.04), (0.12, 0.04)], 0.1, bev=0.004)
    put_bm('food', bm, c=(1.2, -0.88, TOPZ + 0.05), rot=(0, 0, 20), col=H('#f0cc6a'))
    # wicker basket with eggs? herbs bundles hanging
    for i in range(6):
        x = -1.2 + i * 0.48
        rope_line([(x, -0.7, 2.2), (x, -0.7, 2.1)], r=0.004)
        for k in range(5):
            a = TAU * k / 5 + i
            p0 = Vector((x, -0.7, 2.1)); p1 = Vector((x + math.cos(a) * 0.04 + r.uniform(-.01, .01), -0.7 + math.sin(a) * 0.04, 1.85 + r.uniform(0, 0.08)))
            col = [H('#6a8a40'), H('#8a9a58'), H('#5a7a3a'), H('#a89a5a')][i % 4]
            ribbon('leaf', p0, p1, 0.02, 0.07, col=jitter_col(col, 0.15), nseg=2, up=(0, 1, 0), bend=(0.01, 0, 0))
    # shelves: jugs and pots
    for i in range(4):
        pot_jug((-1.2 + i * 0.75, 0.8, 1.07), 0.2 + 0.04 * (i % 3), 0.07 + 0.01 * (i % 2), jitter_col(tc[i % 3] if i % 2 else cc[(i // 2) % 4], 0.08), mat='terracotta' if i % 2 else 'ceramic', handle=(i % 3 == 0))
    for i in range(4):
        bowl((-1.1 + i * 0.7, 0.8, 1.555), 0.12, 0.08, jitter_col(tc[i % 3], 0.08))
    # big floor pots
    for (x, y, h_, rr) in ((-1.1, 0.35, 0.55, 0.22), (-0.55, 0.45, 0.42, 0.18), (1.1, 0.45, 0.6, 0.24)):
        pot_jug((x, y, 0), h_, rr, jitter_col(tc[int(x * 5) % 3], 0.06), neck=0.62, handle=False)
        for sx in (-1, 1):
            tube('terracotta', [Vector((x + sx * rr * 0.45 * 0.62, y, h_ * 0.9)), Vector((x + sx * rr * 0.9, y, h_ * 0.78)), Vector((x + sx * rr * 0.98, y, h_ * 0.6))], 0.014, seg=6, col=tc[0])
import vp_p2b
