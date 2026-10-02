import sys, os, json
sys.path.insert(0, '/shared/river/assets/blender')
from int_lib import *
from int_mats import *
from int_items import *
from int_furn1 import *
from int_furn2 import *
from int_furn3 import *
import int_lib


def curtain(n, cx, cy, zt, w, drop, rot, tied=True, col='#b9a98a', rod_y=0.06):
    """curtain on rod; local -y = into room."""
    rod_y = -abs(rod_y)
    f = Fr((cx, cy, zt), rot, None)
    # rod + finials + rings (static)
    f.cyl(M['wood_dark'], (0, rod_y, 0), 0.011, w + 0.14, axis='x', seg=8)
    for s in (-1, 1):
        f.lathe(M['wood_dark'], (s * (w / 2 + 0.085), rod_y, 0), [(0.001, -0.012), (0.018, 0), (0.018, 0.012), (0.001, 0.024)], r=(0, 0, 0) if False else (0, 90 * s, 0), seg=8, cap=False)
        f.box(M['iron_black'], (s * (w / 2 + 0.03), rod_y / 2, 0.0), (0.012, rod_y, 0.012), bev=0.002) if False else None
        f.box(M['iron_black'], (s * (w / 2 + 0.02), rod_y / 2 + 0.0, 0.0), (0.012, abs(rod_y), 0.014), bev=0.002)
    saved = part_begin()
    cc = C(col)
    for s in (-1, 1):
        g = Fr(f.p((s * w * 0.3, rod_y, -0.02)), rot, None)
        pw = w * 0.42
        cf = fab(cc, 0.1, 9, n + (1 if s > 0 else 0))
        # panel narrower at tie-back height
        def build(nx=10, ny=7):
            bm = bmesh.new()
            Vt = [[None] * (ny + 1) for _ in range(nx + 1)]
            for i in range(nx + 1):
                for j in range(ny + 1):
                    v = j / ny
                    z = -drop * v
                    pinch = 1.0
                    off = 0.0
                    if tied:
                        pinch = 1.0 - 0.55 * math.exp(-((v - 0.55) / 0.12) ** 2)
                        off = -s * 0.25 * pw * (max(0, v - 0.45) ** 1.5) * 1.3
                    x = (-pw / 2 + pw * i / nx) * pinch + off
                    y = 0.028 * math.sin((i / nx) * 4.5 * TAU + n) * (0.5 + 0.5 * v) + 0.02 * (1 - math.cos(v * math.pi)) * 0.3
                    Vt[i][j] = bm.verts.new((x, y, z))
            for i in range(nx):
                for j in range(ny):
                    try:
                        bm.faces.new([Vt[i][j], Vt[i + 1][j], Vt[i + 1][j + 1], Vt[i][j + 1]])
                    except ValueError:
                        pass
            return bm
        bm = build()
        put(M['curtain_vc'], bm, g.M, (1, 1, 1), cfn=cf)
        bm.free()
    part_end(saved, 'curtain_%d' % n, f.p((0, rod_y, 0)))


def picture(pos, rot, w, h, kind, seed, fcol='wood_dark', mat=None):
    frame_picture(pos, (0, 0, rot), w, h, kind=kind, fcol=fcol, seed=seed, mat_col=mat)


def build_all(only=None):
    LAMPN[0] = 0
    init_mats()
    # ------------------------------------------------ rugs
    braided_rug(-1.85, 0.3, 1.5, 1.05, rot=0)
    rect_rug(-3.0, -2.3, 2.1, 1.35, rot=0, stripes=['#6b5a3c', '#a88a5a', '#7b3b2c'], border='#5d4a30', field='#c9b48a', fringe=True)
    rect_rug(3.0, 1.4, 2.2, 1.9, rot=0, stripes=['#5b7a73', '#c99a3e', '#8c3a2e'], border='#6b3a34', field='#d8c8a6')
    # door mat
    box(M['rope'], (0.0, -2.85, F + 0.012), (0.85, 0.5, 0.022), bev=0.006, col=(0.78, 0.66, 0.45), cuts=2)
    sheepskin(-3.2, -0.25, 25)
    sheepskin(3.0, -0.2, -20, (0.55, 0.85))

    # ------------------------------------------------ living
    sofa((0.88, 1.25, F), 90)
    coffee_table((-1.75, 0.35, F), 90)
    armchair((-2.55, 1.75, F), face((-2.55, 1.75), (-1.75, 0.45)), col='#c08a3e', cushion='#7d8e9c')
    armchair((-2.6, -0.75, F), face((-2.6, -0.75), (-1.75, 0.25)), col='#6f8a8c', cushion='#d8b25a')
    side_table((-3.4, 1.85))
    bookshelf((-4.09, 2.0, F), -90)
    fireplace_set((-3.5, 1.1, F))
    log_basket((-3.5, -1.25, F), 0)
    clock_longcase((-1.0, -3.1, F), 0)

    # mantel
    box(M['wood_walnut'], (-3.98, 0.0, 1.5), (0.55, 2.1, 0.07), bev=0.008, col=(1, 0.92, 0.85), cuts=4, g=1)
    box(M['wood_walnut'], (-3.72, 0.0, 1.44), (0.04, 2.0, 0.07), bev=0.006, col=(0.9, 0.82, 0.75))

    # ------------------------------------------------ dining
    dining_table((-3.0, -2.6, F), 0)
    dining_chair((-3.35, -1.85, F), 180, cushion='#b5562f')
    dining_chair((-2.65, -1.85, F), 175, cushion='#b5562f')
    dining_chair((-4.0, -2.6, F), -90)
    dining_chair((-2.0, -2.6, F), 88, cushion='#d0a23e')

    # ------------------------------------------------ kitchen
    cookstove((-3.5, 2.95, F), 180)
    kitchen_counter(-2.25, 3.25)
    barrel((-1.2, 2.93, F), r=0.26, h=0.8, tap=False)
    hutch((-0.4, 3.04, F), 180)
    pantry((0.5, 3.0, F), 180)
    sack((1.08, 3.0, F), r=0.19, h=0.62, col=(0.96, 0.92, 0.8), rot=10)
    sack((1.12, 2.68, F), r=0.17, h=0.5, col=(0.9, 0.86, 0.74), rot=-30)
    pot_rack(-2.2, 2.95, 2.5)
    wall_shelf((-1.42, 3.15, 1.85), 180, W=0.56, D=0.2, seed=2)
    wall_shelf((-1.42, 3.15, 2.25), 180, W=0.56, D=0.2, seed=3)
    wood_stack((-3.55, 2.2, F), 0)
    bucket((-0.85, 2.4, F), water=True)

    # ------------------------------------------------ bedroom
    bed((3.05, 2.22, F), 180)
    bedside((1.97, 3.03, F), 180)
    bedside((4.05, 3.03, F), 180)
    wardrobe((1.93, -2.35, F), -90)
    dresser((1.9, 0.95, F), -90)
    mirror_oval((1.67, 0.95, 1.95), -90)
    desk((3.95, -0.9, F), 90)
    dining_chair((3.3, -0.9, F), -90, cushion='#6f8a8c', mat='wood_walnut')
    trunk((3.05, 0.92, F), 0)
    rocking_chair((3.8, -2.7, F), face((3.8, -2.7), (2.8, -1.8)))
    return


def dump_meta(path):
    meta = {'lights': LIGHTS, 'colliders': COLL, 'interactables': INTER}
    with open(path, 'w') as fh:
        json.dump(meta, fh, indent=1, ensure_ascii=False)


def export_all(write=True):
    objs = finalize() + int_lib.PARTS
    for o in objs:
        for p in o.data.polygons:
            p.use_smooth = True
    if not write:
        return objs, {}
    r = export_bundle(OUT_DIR + '/house_interior.json', objs, meta={'name': 'house_interior'})
    strip_white_cols(OUT_DIR + '/house_interior.json')
    r['kb'] = os.path.getsize(OUT_DIR + '/house_interior.json') // 1024
    dump_meta(OUT_DIR + '/house_interior.meta.json')
    return objs, r


def strip_white_cols(path):
    import base64
    import numpy as np
    d = json.load(open(path))
    dropped = 0
    for p in d['parts']:
        for s in p['subs']:
            if s.get('col'):
                a = np.frombuffer(base64.b64decode(s['col']), dtype=np.float32)
                if np.abs(a - 1.0).max() < 0.02 or not s['mat'].endswith('_vc'):
                    del s['col']; dropped += 1
    json.dump(d, open(path, 'w'), separators=(',', ':'))
    print('dropped white col arrays:', dropped)
