"""Cycles ambient-occlusion BAKING into vertex colours (contact shadows) for the merged static meshes.
 - adaptive subdivision of large faces so the per-vertex AO has resolution
 - stand-in room (floor/walls/ceiling/beams) is present as occluder (never exported)
 - AO is multiplied into the 'Col' colour attribute"""
from kt_lib import *

SKIP = {'glass', 'glass_green', 'water', 'liquid', 'flame'}


def ao_subdivide(bm, maxlen=0.17, minarea=0.01):
    """subdivide long edges of big faces (grid fill) so vertex AO can resolve contact shadows"""
    for _ in range(2):
        edges = set()
        for f in bm.faces:
            if f.calc_area() < minarea or f.normal.z < -0.95:
                continue
            for e in f.edges:
                if e.calc_length() > maxlen * 1.25:
                    edges.add(e)
        if not edges:
            break
        # group by required cut counts
        groups = {}
        for e in edges:
            n = max(1, int(math.ceil(e.calc_length() / maxlen)) - 1)
            groups.setdefault(min(n, 6), []).append(e)
        for n, es in groups.items():
            es = [e for e in es if e.is_valid]
            if es:
                bmesh.ops.subdivide_edges(bm, edges=es, cuts=n, use_grid_fill=True, use_single_edge=False)
        bm.normal_update()


def prepare(objs, maxlen=0.17, minarea=0.01, skip_mats=('linen_vc',)):
    before = 0
    after = 0
    for ob in objs:
        mn = ob.name.replace('static_', '')
        me = ob.data
        before += sum(len(p.vertices) - 2 for p in me.polygons)
        if mn in SKIP or mn in skip_mats:
            after += sum(len(p.vertices) - 2 for p in me.polygons)
            continue
        bm = bmesh.new()
        bm.from_mesh(me)
        ao_subdivide(bm, maxlen, minarea)
        bm.to_mesh(me)
        bm.free()
        after += sum(len(p.vertices) - 2 for p in me.polygons)
    return before, after


def edge_wear(objs, mats=('wood_pine',), strength=0.75):
    """worn paint: convex bevel edges of painted pine blend back to bare wood (curvature from edge dihedral angles)"""
    n_tot = 0
    for ob in objs:
        mn = ob.name.replace('static_', '')
        if mn not in mats:
            continue
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        cl = bm.loops.layers.float_color['Col']
        for v in bm.verts:
            conv = 0.0
            for e in v.link_edges:
                if len(e.link_faces) == 2:
                    try:
                        conv = max(conv, e.calc_face_angle_signed(0.0))
                    except Exception:
                        pass
            if conv < 0.3:
                continue
            t = min(1.0, (conv - 0.3) / 0.5)
            p = v.co
            nse = 0.5 + 0.5 * mnoise.noise(Vector((p.x * 38, p.y * 38, p.z * 38)))
            w = t * (0.25 + 0.75 * nse) * strength
            for l in v.link_loops:
                c = l[cl]
                if not (c[2] > c[0] * 1.15 or c[0] < 0.4):
                    continue
                bare = (0.92, 0.84, 0.72)
                l[cl] = (c[0] * (1 - w) + bare[0] * w, c[1] * (1 - w) + bare[1] * w, c[2] * (1 - w) + bare[2] * w, 1.0)
                n_tot += 1
        bm.to_mesh(ob.data)
        bm.free()
    return n_tot


def bake(objs, occluders=(), samples=48, dist=0.55, strength=0.9, gamma=0.85):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = False
    w = bpy.data.worlds.new('AOW')
    sc.world = w
    w.use_nodes = True
    w.light_settings.distance = dist
    sc.render.bake.target = 'VERTEX_COLORS'
    targets = []
    for ob in objs:
        mn = ob.name.replace('static_', '')
        if ob.type != 'MESH':
            continue
        if mn in SKIP:
            ob.hide_render = True
            continue
        if not ob.name.startswith('static_'):
            continue
        targets.append(ob)
        ca = ob.data.color_attributes.new('AO', 'FLOAT_COLOR', 'POINT')
        ob.data.color_attributes.active_color = ca
    # animated parts (flames) do not occlude
    bpy.ops.object.select_all(action='DESELECT')
    for ob in targets:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = targets[0]
    bpy.context.view_layer.update()
    bpy.ops.object.bake(type='AO')
    stats = []
    for ob in targets:
        me = ob.data
        nv = len(me.vertices)
        a = np.zeros(nv * 4, dtype=np.float32)
        me.color_attributes['AO'].data.foreach_get('color', a)
        ao = a.reshape(-1, 4)[:, 0]
        # contrast shaping
        ao = np.clip(ao, 0, 1) ** gamma
        fac = (1.0 - strength) + strength * ao
        li = np.zeros(len(me.loops), dtype=np.int32)
        me.loops.foreach_get('vertex_index', li)
        ca = me.color_attributes['Col']
        col = np.zeros(len(me.loops) * 4, dtype=np.float32)
        ca.data.foreach_get('color', col)
        col = col.reshape(-1, 4)
        col[:, :3] *= fac[li][:, None]
        ca.data.foreach_set('color', col.ravel())
        me.color_attributes.active_color = ca
        me.color_attributes.remove(me.color_attributes['AO'])
        stats.append((ob.name, float(ao.mean())))
    return stats
