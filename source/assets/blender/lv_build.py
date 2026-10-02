"""Build the LIVING zone: /shared/river/assets/out/house_int_living.json (+ .meta.json)
Run: blender -b --python lv_build.py [-- --nosim --noao --preview <view> ...]"""
import sys, time, os, json
sys.path.insert(0, '/shared/river/assets/blender')
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
if '--nosim' in argv:
    os.environ['LV_NOSIM'] = '1'
from lv_wall import *
import lv_seat, lv_rug, lv_tables, lv_books, lv_fire, lv_wall, lv_items

T0 = time.time()
STATS = {}


def face(src, dst):
    dx, dy = dst[0] - src[0], dst[1] - src[1]
    return math.degrees(math.atan2(-dx, dy))


def tick(name):
    print('  [%5.1fs] %s  (faces so far %d)' % (time.time() - T0, name, sum(len(b.faces) for b, _ in ACC.values())))


def build_zone():
    LAMPN[0] = 0
    init_mats()
    # ------------------------------------------------------------------ rugs
    lv_rug.braided_rug(-1.85, 0.3, 1.5, 1.05, 0); tick('rug')
    lv_fire.sheepskin(-3.5, -0.18, 7, sz=(0.52, 0.82)); tick('sheepskin')
    # ------------------------------------------------------------------ seating
    lv_items.contact_shadow(0.88, 1.25, 1.96, 0.94, 90, rr=0.1)
    lv_seat.sofa((0.88, 1.25, F), 90); tick('sofa')
    lv_seat.armchair_yellow((-2.55, 1.75, F), face((-2.55, 1.75), (-1.75, 0.45))); tick('armchair yellow')
    lv_seat.armchair_teal((-2.6, -0.75, F), face((-2.6, -0.75), (-1.75, 0.25))); tick('armchair teal')
    # ------------------------------------------------------------------ coffee table + things on it
    lv_tables.coffee_table((-1.75, 0.35, F), 90)
    cf = Fr((-1.75, 0.35, F), 90, None)
    tz = 0.42
    lv_items.tea_set(*cf.p(V(0.2, 0.0, 0))[:2], F + tz, 90)
    lv_items.book_open(cf.p(V(-0.2, 0.02, tz)), 90 + 8)
    lv_items.reading_glasses(cf.p(V(-0.24, 0.045, tz + 0.0115)), 90 + 70)
    lv_items.candlestick(cf.p(V(-0.4, -0.2, tz)), h=0.11, kind='brass', cl=0.1, lit=True, wax=True, seed=21, inten=0.7, dist=4.5, name='lamp_liv_2')
    lv_tables.newspaper(cf.M @ Matrix.Translation((0.0, 0.0, 0.1355)) @ rotm((0, 0, 90)), seed=2)
    lv_items.bowl(cf.p(V(0.0, -0.17, tz)), r=0.045, h=0.03, col=C('#4e7299'))
    tick('coffee table set')
    # ------------------------------------------------------------------ side table + lamp
    lv_tables.side_table((-3.4, 1.85))
    lv_items.contact_shadow(-3.4, 1.85, 0.38, 0.38, 0, rr=0.19, spread=0.025)
    sz = F + 0.58
    lv_items.oil_lamp((-3.4, 1.85, sz + 0.0005), sc=1.2, name='lamp_liv_1', inten=1.3, dist=6.5)
    lv_books.book_flat_stack(Matrix.Translation((-3.27, 1.74, sz + 0.0)) @ rotm((0, 0, 20)), 2, random.Random(3))
    lv_items.teacup((-3.55, 1.97, sz + 0.0055), rot=40, tea=True, seed=5)
    lv_items.saucer((-3.55, 1.97, sz + 0.0), 40, seed=5)
    tick('side table')
    # ------------------------------------------------------------------ bookshelf
    lv_items.contact_shadow(-4.07, 2.0, 1.36, 0.36, -90, rr=0.03, spread=0.03)
    sh = lv_books.bookshelf((-4.09, 2.0, F), -90)
    STATS['books'] = sh[1]
    tick('bookshelf')
    # ------------------------------------------------------------------ fireplace
    lv_fire.tool_stand((-3.5, 1.1, F), 0)
    lv_fire.bellows((-3.64, 0.93, F + 0.0), 180)
    lv_fire.log_basket((-3.5, -1.25, F), 0)
    lv_fire.scatter_chips(-3.5, -1.25, 0.62, 60.0, 3)
    lv_items.contact_shadow(-3.5, -1.25, 0.56, 0.56, 0, rr=0.28, spread=0.03)
    lv_items.contact_shadow(-3.5, 1.1, 0.22, 0.22, 0, rr=0.11, spread=0.02)
    tip, kp = lv_fire.crane_kettle(18.0)
    STATS['kettle'] = (tuple(kp), tuple(tip))
    tick('fire set')
    lv_fire.mantel_decor()
    tick('mantel')
    # kettle steam anchor part
    saved = part_begin()
    bmx = bmesh.new()
    vs = [bmx.verts.new(q) for q in (tip + V(0, 0, 0.0), tip + V(0.002, 0, 0.0), tip + V(0, 0.002, 0.001))]
    bmx.faces.new(vs)
    # tiny, invisible-ish triangle in the iron material (anchor for steam)
    bm0 = get_bm(M['iron_black'])
    cl0 = bm0.loops.layers.float_color['Col']
    vv = [bm0.verts.new(q) for q in (tip, tip + V(0.002, 0, 0.0), tip + V(0, 0.002, 0.001))]
    fc = bm0.faces.new(vv)
    for l in fc.loops:
        l[cl0] = (0.2, 0.2, 0.22, 1)
    bmx.free()
    part_end(saved, 'kettle_steam_anchor', tip)
    # ------------------------------------------------------------------ wall pieces
    lv_items.contact_shadow(-1.0, -3.08, 0.56, 0.36, 0, rr=0.02, spread=0.03)
    lv_wall.clock_longcase((-1.0, -3.1, F), 0); tick('clock')
    lv_wall.antlers((1.4, 1.25, 2.36), 90); tick('antlers')
    lv_wall.rod_rack((-4.235, -2.15, 2.62), 90); tick('rod rack')
    lv_wall.painting((1.385, 1.25, 1.83), (-1, 0), 1, 'gilt')
    lv_wall.painting((1.385, 0.42, 1.9), (-1, 0), 2, 'oak')
    lv_wall.painting((1.385, 2.2, 1.9), (-1, 0), 3, 'walnut')
    lv_wall.painting((-3.9465, 0.0, 2.35), (1, 0), 4, 'gilt', tilt=6.0)
    lv_wall.painting((-4.235, -2.3, 1.85), (1, 0), 5, 'walnut')
    lv_wall.painting((-1.85, -3.235, 1.75), (0, 1), 6, 'gilt')
    lv_wall.painting((-4.0, -3.235, 1.9), (0, 1), 7, 'white')
    lv_wall.painting((1.385, -1.9, 2.1), (-1, 0), 8, 'oak')
    tick('paintings')
    lv_wall.wall_shelf((1.4, -1.9, 1.45), 90, W=0.72, D=0.2, seed=3); tick('wall shelf')
    # newspaper on the floor by the sofa + knitting basket by the teal chair
    lv_tables.newspaper(Matrix.Translation((0.56, -0.25, F + 0.0)) @ rotm((0, 0, 100)), seed=5, nsheets=3)
    lv_tables.knitting_basket((-2.0, -0.62, F)); tick('knitting basket')
    collider(-2.2, -1.8, -0.82, -0.42, F + 0.22)
    lv_wall.curtain_window(1, -2.9, -3.235, 2.8, 1.3, 1.5, 180, '#c9b79a'); tick('curtain')


def register_meta():
    INTER.clear()
    I = interact
    I('fireplace_kettle', (-4.0, -0.2, F + 0.75), '벽난로에 걸린 무쇠 주전자')
    I('mantel', (-3.8, 0.0, 1.85), '벽난로 선반 - 촛대와 괘종 시계')
    I('bookshelf', (-3.85, 2.0, 1.5), '빼곡한 책장')
    I('sofa', (0.8, 1.25, 0.95), '푹신한 소파와 담요')
    I('armchair_yellow', (-2.55, 1.75, 1.0), '노란 안락의자')
    I('armchair_teal', (-2.6, -0.75, 1.0), '청록빛 안락의자')
    I('tea_set', (-1.75, 0.55, F + 0.55), '식어가는 찻주전자')
    I('open_book', (-1.9, 0.15, F + 0.5), '펼쳐진 책과 돋보기 안경')
    I('oil_lamp', (-3.4, 1.85, F + 0.95), '오일 램프')
    I('longcase_clock', (-1.0, -2.95, F + 1.6), '괘종시계')
    I('antlers', (1.35, 1.25, 2.5), '사슴뿔 장식')
    I('rod_rack', (-4.2, -2.15, 2.6), '낚싯대 걸이')
    I('hearth_tools', (-3.5, 1.1, F + 0.5), '벽난로 도구 세트')
    I('log_basket', (-3.5, -1.25, F + 0.4), '장작 바구니')
    I('knitting_basket', (-2.0, -0.62, F + 0.3), '뜨개질 바구니')
    I('painting_lake', (1.35, 1.25, 1.83), '호수 풍경화')
    I('painting_forest', (-3.9, 0.0, 2.35), '가을 숲 풍경화')
    I('wall_shelf', (1.3, -1.9, 1.6), '작은 장식품 선반')
    I('newspaper', (-1.75, 0.35, F + 0.2), '접힌 신문')
    I('sheepskin', (-3.5, -0.18, F + 0.1), '양가죽 깔개')


def meta_extra():
    return {'name': 'house_int_living', 'frame': 'three x = Blender x, y = Blender z, z = -Blender y'}


def main():
    reset_scene()
    build_zone()
    register_meta()
    objs = finalize() + PARTS
    for o in objs:
        for p in o.data.polygons:
            p.use_smooth = True
    return objs


def export_all(objs, ao=True, ao_samples=64):
    from lv_room import build_room, STAND
    if ao:
        room = build_room()
        statics = [o for o in objs if o.name.startswith('static_') and not any(k in o.name for k in ('glass', 'lv_painting', 'fur', 'contact_shadow'))]
        for o in objs:
            if 'glass' in o.name or o.name.startswith('lamp_liv') or o.name == 'kettle_steam_anchor':
                o.hide_render = True
        st = bake_ao(statics, samples=ao_samples, dist=0.8, strength=1.0, floor=0.22, gamma=1.0)
        print('AO baked %d objects' % len(st))
        for n_, m_, mn_ in st[:60]:
            print('    AO %-26s mean %.3f min %.3f' % (n_, m_, mn_))
        for o in objs:
            o.hide_render = False
        for o in room:
            bpy.data.objects.remove(o)
    out = OUT_DIR + '/house_int_living.json'
    # sort: static first, then animated parts
    r = export_bundle(out, objs, meta={'name': 'house_int_living', 'frame': 'house-local; three x=bx, y=bz, z=-by'})
    meta = {'lights': LIGHTS, 'colliders': COLL, 'interactables': INTER,
            'anchors': [{'name': 'kettle_steam_anchor', 'pos': [round(STATS['kettle'][1][0], 3), round(STATS['kettle'][1][2], 3), round(-STATS['kettle'][1][1], 3)]}],
            'parts': [o.name for o in objs if not o.name.startswith('static_')],
            'books': STATS.get('books'), 'tris': r['tris']}
    with open(OUT_DIR + '/house_int_living.meta.json', 'w') as fh:
        json.dump(meta, fh, indent=1, ensure_ascii=False)
    return r, meta


if __name__ == '__main__':
    objs = main()
    print('built in %.1fs; objects %d; tris %d' % (time.time() - T0, len(objs), sum(len(p.vertices) - 2 for o in objs for p in o.data.polygons)))
    for o in sorted(objs, key=lambda o: -len(o.data.polygons))[:40]:
        print('   %-28s polys %6d' % (o.name, len(o.data.polygons)))
    if '--export' in argv:
        r, meta = export_all(objs, ao=('--noao' not in argv))
        print('EXPORT', r)
        print('lights', len(meta['lights']), 'colliders', len(meta['colliders']), 'interactables', len(meta['interactables']), 'books', meta['books'])


