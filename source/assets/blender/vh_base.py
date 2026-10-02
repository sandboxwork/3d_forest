"""vh_base: finishing helper shared by building scripts."""
import sys, os, json
sys.path.insert(0, '/shared/river/assets/blender')
from bl_common import reset_scene
reset_scene()
from vh_parts import *
import vh_lib

PARTS_DIR = OUT_DIR + '/vh_parts'


def C(x0, x1, y0, y1, top, bottom=0.0):
    """blender rect (x0..x1, y0..y1) -> three collider box (cz=-y)"""
    return {"cx": round((x0 + x1) / 2, 3), "cz": round(-(y0 + y1) / 2, 3), "hx": round(abs(x1 - x0) / 2, 3), "hz": round(abs(y1 - y0) / 2, 3),
            "top": round(top, 3), "bottom": round(bottom, 3)}


def finish(name, W, D, h_eave, h_ridge, door, role, ko, colliders, views=None, bevel=True, **bakekw):
    """door: (x, y) in blender coords of the door position at the wall plane."""
    import time
    t0 = time.time()
    chim = list(REG['chimneys'])
    ob = make_part(name, vh_lib.CUR, bevel=bevel, **bakekw)
    objs = [ob]
    smokes = []
    for i, c in enumerate(chim):
        sn = name + '_smoke' + ('' if i == 0 else str(i + 1))
        # c is in three coords; convert back to blender
        p = (c['x'], -c['z'], c['y'])
        objs.append(smoke_part(sn, p))
    tris = tri_count(ob)
    meta = {"w": W, "d": D, "h_eave": h_eave, "h_ridge": h_ridge, "door": {"x": round(door[0], 3), "z": round(-door[1], 3)},
            "colliders": colliders, "windows": REG['windows'], "chimney": chim[0] if chim else None, "smoke": chim[0] if chim else None,
            "role": role, "ko": ko}
    if len(chim) > 1:
        meta["smokes"] = chim
    os.makedirs(PARTS_DIR, exist_ok=True)
    st = export_bundle(PARTS_DIR + '/' + name + '.json', objs, meta={'name': name})
    json.dump(meta, open(PARTS_DIR + '/' + name + '.meta.json', 'w'), indent=1)
    print('BUILD %s tris=%d (export tris %d) windows=%d chimneys=%d json=%dKB build+bake %.1fs' % (name, tris, st['tris'], len(REG['windows']), len(chim), st['kb'], time.time() - t0))
    if views and os.environ.get('VH_RENDER', '1') == '1':
        sel = os.environ.get('VH_VIEWS')
        v = {k: views[k] for k in (sel.split(',') if sel else views) if k in views}
        render_views(objs, v, name, samples=int(os.environ.get('VH_SAMPLES', 32)))
    return ob, meta
