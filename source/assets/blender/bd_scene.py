"""Scene assembly for the bedroom/entry/decor build. Parts register in REG and can be built selectively for previews."""
from bd_lib import *
import bd_lib
import bd_bed, bd_bedcloth, bd_furn, bd_furn2, bd_furn3, bd_entry, bd_decor, bd_items as I
import bd_hw

REG = {}
ORDER = []
BED_POS = (3.02, 2.18)


def part(fn):
    k = fn.__name__.replace('part_', '')
    REG[k] = fn
    ORDER.append(k)
    return fn


@part
def part_bed():
    f = Fr(BED_POS, 180, F)
    bd_bed.build_frame(f)
    bd_bedcloth._cnt('frame')
    bd_bed.build_mattress(f)
    bd_bedcloth._cnt('mattress')
    info = bd_bedcloth.build_linens(f)
    bd_bedcloth.folded_blanket(f, info['quilt_surf'])
    collider_f(f, 1.64, 2.06, F + 0.70, name='bed')
    interact('bed', (BED_POS[0], BED_POS[1] - 0.2, F + 0.75), '조각보 이불이 덮인 침대')
    return f, info


@part
def part_wardrobe():
    f = bd_furn.wardrobe((1.965, -2.35), -90)
    interact('wardrobe', (1.965, -2.35, F + 1.3), '조각된 옷장 - 문이 살짝 열려 있다')
    return f


@part
def part_dresser():
    f = bd_furn2.dresser((1.93, 0.95), -90)
    interact('dresser', (1.93, 0.95, F + 1.2), '거울 달린 서랍장')
    return f


@part
def part_bedsides():
    bd_furn2.bedside((1.96, 3.03), 180, side=1, W=0.44)
    bd_furn2.bedside((4.04, 3.03), 180, side=-1, W=0.40)
    interact('bedside_lamp', (1.96, 3.0, F + 0.95), '침대 옆 석유 램프')
    interact('bedside_candle', (4.04, 3.0, F + 0.8), '침대 옆 촛불과 책')


@part
def part_desk():
    f = bd_furn2.desk((3.95, -0.9), 90)
    bd_furn2.desk_chair((3.3, -0.95), -85)
    interact('desk', (3.95, -0.9, F + 0.95), '편지와 잉크가 놓인 책상')
    return f


@part
def part_trunk():
    bd_furn3.trunk((3.02, 0.66), 180)
    interact('trunk', (3.02, 0.66, F + 0.55), '쇠띠를 두른 침대 발치 트렁크')


@part
def part_rocker():
    bd_furn3.rocking_chair((3.6, -2.55), 30)
    interact('rocking_chair', (3.6, -2.55, F + 0.8), '뜨개 숄이 걸린 흔들의자')


@part
def part_washstand():
    bd_furn3.washstand((2.85, -2.99), 0)
    interact('washstand', (2.85, -2.9, F + 1.05), '도자기 세면대와 물주전자')


@part
def part_shelf():
    f = bd_furn3.wall_shelf((4.25, -1.95, 1.62), 90, W=0.62, D=0.17, trinkets=True)
    interact('shelf', (4.1, -1.95, 1.75), '작은 장식품 선반')


@part
def part_entry():
    bd_entry.build_entry()
    interact('coat_rack', (0.98, -3.0, 1.6), '외투와 모자가 걸린 코트 랙')
    interact('entry_lantern', (1.2, -2.1, 1.4), '현관 선반 위의 등불과 우편물')
    interact('boot_tray', (1.2, -2.35, 0.6), '장화 트레이')
    interact('hat_rail', (1.3, -2.2, 1.95), '밀짚모자와 가방이 걸린 모자걸이')
    interact('welcome_mat', (0.0, -2.78, 0.4), '환영 매트')
    interact('umbrella_stand', (1.2, -1.85, 0.9), '우산꽂이')


@part
def part_rugs():
    bd_decor.braided_oval_rug(3.0, 0.35, 1.02, 0.7, 0)
    bd_decor.rag_runner(1.97, 1.95, 0.46, 1.1, 0)
    bd_decor.rag_runner(2.85, -2.45, 0.7, 0.42, 0)
    I.slippers((2.1, 1.35, F + 0.012), rot=70)


@part
def part_curtains():
    spec = [
        (1, (-2.9, -3.25), 0, 1.30, 'burlap', (0.92, 0.82, 0.62), 'wood'),
        (2, (2.9, -3.25), 0, 1.32, 'linen_curtain', (0.66, 0.74, 0.66), 'wood'),
        (3, (-2.2, 3.25), 180, 1.52, 'burlap', (0.9, 0.84, 0.7), 'iron'),
        (4, (2.2, 3.25), 180, 1.30, 'linen_curtain', (0.9, 0.86, 0.76), 'wood'),
        (5, (4.25, -0.9), 90, 1.42, 'linen_curtain', (0.78, 0.7, 0.52), 'wood'),
        (6, (4.25, 1.6), 90, 1.42, 'linen_curtain', (0.82, 0.8, 0.72), 'wood'),
    ]
    for (n, wp, rot, hem, mat, col, rod) in spec:
        zr = 2.84 if n >= 5 else 2.88
        bd_decor.curtain(n, wp, rot, hem, mat_name=mat, col=col, rod_z=zr, rod_style=rod)


@part
def part_pictures():
    D = bd_decor.picture
    D((2.95, 3.25, 2.12), 180, 0.30, 0.40, 1, 'dark')
    D((3.75, 3.25, 2.12), 180, 0.30, 0.40, 2, 'dark')
    D((3.35, 3.25, 2.55), 180, 0.62, 0.46, 3, 'gilt')
    D((1.65, -1.3, 2.45), -90, 0.40, 0.30, 4, 'oak')
    D((4.25, 0.35, 2.3), 90, 0.40, 0.30, 5, 'dark')
    D((1.65, 1.0, 2.5), -90, 0.30, 0.38, 6, 'gilt')
    D((3.95, -3.25, 1.78), 0, 0.36, 0.36, 7, 'white')
    D((4.25, -2.0, 2.15), 90, 0.50, 0.40, 8, 'oak')
    D((3.95, -3.25, 2.3), 0, 0.28, 0.36, 9, 'dark')


@part
def part_sconces():
    interact('sconce_bedroom', (4.1, 0.35, 1.9), '벽에 걸린 촛대 등')
    interact('sconce_entry', (1.3, -1.45, 2.0), '현관 벽 촛대 등')
    bd_decor.sconce((4.25, 0.35, 1.72), 90, name=None, inten=0.8, dist=5.0)
    bd_decor.sconce((1.4, -1.45, 1.85), 90, name=None, inten=0.8, dist=5.0)


@part
def part_plants():
    bd_decor.pothos_hanging(2.75, -1.55, 2.955, drop=0.75, seed=3)
    # fern on a wicker stool by the right-far window
    f = Fr((4.0, 1.62, F), 0, F)
    f.cyl(M['wicker'], (0, 0, 0.2), 0.17, 0.4, seg=20, cap=False, r2=0.15)
    for k in range(10):
        f.torus(M['wicker'], (0, 0, 0.04 + k * 0.04), 0.16, 0.008, plane='xy', seg=24, rseg=5, col=(0.9, 0.75, 0.5))
    f.cyl(M['wicker'], (0, 0, 0.405), 0.185, 0.02, seg=24, col=(0.9, 0.75, 0.5), bev=0.005)
    top = bd_decor.terracotta_pot(f.p((0, 0, 0.41)), r=0.085, h=0.15, col=(0.78, 0.46, 0.32))
    bd_decor.fern(top, n=16, seed=2, h=0.4)
    collider(3.82, 4.2, 1.44, 1.8, F + 0.45); COLL[-1]['name'] = 'fern_stand'
    interact('fern', (4.0, 1.62, F + 0.75), '고사리가 놓인 등나무 받침대')
    # geranium in a larger pot on the floor
    top = bd_decor.terracotta_pot((4.0, 0.95, F), r=0.1, h=0.2, col=(0.8, 0.5, 0.36))
    bd_decor.geranium(top, seed=5, h=0.3)
    collider(3.9, 4.1, 0.85, 1.05, F + 0.55); COLL[-1]['name'] = 'geranium_pot'
    interact('geranium', (4.0, 0.95, F + 0.6), '붉은 제라늄 화분')
    interact('pothos', (2.75, -1.55, 2.3), '들보에 매달린 포토스 화분')
    # window sill still-lifes (stool top z=1.46 front/back, 1.53 right)
    S = bd_decor.sill_plants
    for (wp, rot, z, items) in (((-2.9, -3.25), 0, 1.46, ('succulent', 'jar', 'candle')), ((2.9, -3.25), 0, 1.46, ('herb', 'shell', 'bottle')),
                                ((-2.2, 3.25), 180, 1.46, ('jar', 'succulent', 'shell')), ((2.2, 3.25), 180, 1.46, ('candle', 'bottle', 'succulent')),
                                ((4.25, -0.9), 90, 1.53, ('jar', 'herb')), ((4.25, 1.6), 90, 1.53, ('succulent', 'candle'))):
        f = Fr((wp[0], wp[1], 0), rot, 0.0)
        S(f, 0.0, items, z=z, y=0.04, spread=0.5 if len(items) > 2 else 0.3)


@part
def part_dried():
    D = bd_decor.dried_bundle
    z = 2.955
    for (x, y, kind, L, s) in ((2.75, 2.4, 'lavender', 0.32, 1), (2.75, 0.2, 'wheat', 0.34, 2), (2.75, -2.9, 'eucalyptus', 0.34, 3), (3.85, -2.9, 'hydrangea', 0.26, 4),
                               (3.85, 1.4, 'statice', 0.28, 6), (0.55, -3.0, 'lavender', 0.3, 7), (0.55, -2.55, 'wheat', 0.32, 8)):
        D((x, y, z), kind, L, s, tilt=(0, 0, s * 37))


@part
def part_pegs():
    f, xs = bd_decor.peg_rail((1.65, -1.3, 1.85), -90, n=3, W=0.62)
    bd_decor.hang_on_peg(f, xs[0], 'pg_robe', dict(hang=1.05, sh=0.17, hem=1.35, hb=0.07, phase=0.5, col=(0.45, 0.35, 0.5), mat='wool'))
    bd_decor.hang_on_peg(f, xs[2], 'pg_dress', dict(hang=0.9, sh=0.16, hem=1.4, hb=0.06, phase=1.9, col=(0.85, 0.8, 0.68), mat='linen'))


@part
def part_trim():
    for y in (-0.9175, 0.1175):
        bd_decor.plinth_block(1.65, y, -90)
        bd_decor.plinth_block(1.4, y, 90)
    for x in (-0.555, 0.555):
        bd_decor.plinth_block(x, -3.25, 0)
    bd_decor.base_accent(3.0, 3.25, 180, 2.5)          # behind the bed head
    bd_decor.base_accent(1.65, 0.95, -90, 1.3)         # behind the dresser
    bd_decor.base_accent(1.65, -2.35, -90, 1.5)        # behind the wardrobe
    bd_decor.base_accent(4.25, -0.9, 90, 1.5)          # behind the desk
    bd_decor.base_accent(2.85, -3.25, 0, 1.2)          # behind the washstand


def acc_tris():
    t = 0
    for mn, (bm, mat) in bd_lib.ACC.items():
        t += sum(len(f.verts) - 2 for f in bm.faces)
    return t + sum(sum(len(f.verts) - 2 for f in o.data.polygons) if False else 0 for o in bd_lib.PARTS)


def build_all(parts=None):
    for k in ORDER:
        if parts is None or k in parts:
            t0 = acc_tris()
            by0 = {mn: sum(len(f.verts) - 2 for f in bm.faces) for mn, (bm, mat) in bd_lib.ACC.items()}
            REG[k]()
            by1 = {mn: sum(len(f.verts) - 2 for f in bm.faces) for mn, (bm, mat) in bd_lib.ACC.items()}
            d = {mn: by1[mn] - by0.get(mn, 0) for mn in by1 if by1[mn] - by0.get(mn, 0) > 0}
            top = sorted(d.items(), key=lambda t: -t[1])[:5]
            print('PART', k, acc_tris() - t0, top)


def tri_count(objs):
    t = 0
    for o in objs:
        me = o.data
        me.calc_loop_triangles()
        t += len(me.loop_triangles)
    return t


def final_export(objs, room):
    import bd_room
    stat = [o for o in objs if o.name.startswith('static_')]
    parts = [o for o in objs if not o.name.startswith('static_')]
    r = bd_room.build_room()
    bake_list = stat + [p for p in parts if p.name.startswith('curtain_')]
    bd_room.bake_ao(bake_list, samples=64)
    meta = {'lights': LIGHTS, 'colliders': COLL, 'interactables': INTER}
    out = OUT_DIR + '/house_int_bedroom.json'
    res = export_bundle(out, stat + parts, meta={'name': 'house_int_bedroom'})
    with open(OUT_DIR + '/house_int_bedroom.meta.json', 'w') as fh:
        json.dump(meta, fh, indent=1, ensure_ascii=False)
    print('EXPORT', res)
    for o in stat + parts:
        print('  ', o.name, tri_count([o]))
