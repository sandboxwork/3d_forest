"""Temporary stand-in room (never exported) + preview rendering + AO helpers for the bedroom build."""
from bd_lib import *
from bd_mats import PREV

STAND = []
TEXDIR = '/shared/river/assets/tex'


def _box(name, c, s, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c)
    o = bpy.context.object
    o.scale = s
    o.name = name
    o.data.materials.append(mat)
    STAND.append(o)
    return o


def build_room(with_trim=True):
    wall = make_mat('_wall', '#d9cfba', rough=0.9)
    wood = make_mat('_floor', '#9a7048', rough=0.6)
    beam = make_mat('_beam', '#4e3520', rough=0.7)
    ceil = make_mat('_ceil', '#b89a70', rough=0.8)
    wain = make_mat('_wain', '#bf9d72', rough=0.7)
    trim = make_mat('_trim', '#e9e4d3', rough=0.5)
    _box('_fl', (0, 0, F - 0.05), (9, 7, 0.1), wood)
    _box('_ce', (0, 0, 3.15 + 0.05), (9, 7, 0.1), ceil)
    for x in [-3.85, -2.75, -1.65, -0.55, 0.55, 1.65, 2.75, 3.85]:
        _box('_bm', (x, 0, 3.05), (0.15, 6.5, 0.2), beam)
    T = 0.25

    def wall_y(yc, wins, sign):
        segs = []
        cur = -4.5
        for (xc, w, zs, ze) in sorted(wins):
            segs.append((cur, xc - w / 2)); cur = xc + w / 2
        segs.append((cur, 4.5))
        for a, b in segs:
            if b > a:
                _box('_w', ((a + b) / 2, yc + sign * T / 2, (F + 3.15) / 2), (b - a, T, 3.15 - F), wall)
        for (xc, w, zs, ze) in wins:
            _box('_w', (xc, yc + sign * T / 2, (F + zs) / 2), (w, T, zs - F), wall)
            _box('_w', (xc, yc + sign * T / 2, (ze + 3.15) / 2), (w, T, 3.15 - ze), wall)
            if with_trim:
                # casing + stool (sill)
                _box('_t', (xc - w / 2 - 0.04, yc - sign * 0.011, (zs + ze) / 2), (0.085, 0.022, ze - zs), trim)
                _box('_t', (xc + w / 2 + 0.04, yc - sign * 0.011, (zs + ze) / 2), (0.085, 0.022, ze - zs), trim)
                _box('_t', (xc, yc - sign * 0.011, ze + 0.04), (w + 0.17, 0.022, 0.085), trim)
                if zs > 1.0:
                    _box('_t', (xc, yc - sign * 0.0375, zs + 0.015), (w + 0.22, 0.075, 0.03), trim)
    wall_y(-3.25, [(-2.9, 1.0, 1.43, 2.68), (2.9, 1.0, 1.43, 2.68), (0.0, 1.0, F, 2.3)], -1)
    wall_y(3.25, [(-2.2, 1.0, 1.43, 2.68), (2.2, 1.0, 1.43, 2.68)], 1)

    def wall_x(xc, wins, sign):
        segs = []
        cur = -3.5
        for (yc, w, zs, ze) in sorted(wins):
            segs.append((cur, yc - w / 2)); cur = yc + w / 2
        segs.append((cur, 3.5))
        for a, b in segs:
            if b > a:
                _box('_w', (xc + sign * T / 2, (a + b) / 2, (F + 3.15) / 2), (T, b - a, 3.15 - F), wall)
        for (yc, w, zs, ze) in wins:
            _box('_w', (xc + sign * T / 2, yc, (F + zs) / 2), (T, w, zs - F), wall)
            _box('_w', (xc + sign * T / 2, yc, (ze + 3.15) / 2), (T, w, 3.15 - ze), wall)
            if with_trim:
                _box('_t', (xc - sign * 0.011, yc - w / 2 - 0.04, (zs + ze) / 2), (0.022, 0.085, ze - zs), trim)
                _box('_t', (xc - sign * 0.011, yc + w / 2 + 0.04, (zs + ze) / 2), (0.022, 0.085, ze - zs), trim)
                _box('_t', (xc - sign * 0.011, yc, ze + 0.04), (0.022, w + 0.17, 0.085), trim)
                _box('_t', (xc - sign * 0.0375, yc, zs + 0.015), (0.075, w + 0.22, 0.03), trim)
    wall_x(4.25, [(-0.9, 0.9, 1.5, 2.6), (1.6, 0.9, 1.5, 2.6)], 1)
    _box('_wl', (-4.25 - T / 2, 0, (F + 3.15) / 2), (T, 7, 3.15 - F), wall)
    # partition with doorway (y -0.875..0.075, to z=2.3)
    _box('_p', (1.525, -2.0625, (F + 3.15) / 2), (0.25, 2.375, 3.15 - F), wall)
    _box('_p', (1.525, 1.6625, (F + 3.15) / 2), (0.25, 3.175, 3.15 - F), wall)
    _box('_p', (1.525, -0.4, (2.3 + 3.15) / 2), (0.25, 0.95, 3.15 - 2.3), wall)
    if with_trim:
        # wainscot (flush, 1.1 high), baseboard 0.142 high x 0.024, chair rail 0.04 deep
        def strip(c, s, m):
            _box('_t', c, s, m)
        # front/back walls (skip door/window spans roughly; fine for stand-in)
        for (yy, sg) in ((-3.25, 1), (3.25, -1)):
            strip((0, yy + sg * 0.012, F + 0.071), (8.5, 0.024, 0.142), trim)
            strip((0, yy + sg * 0.02, 1.13), (8.5, 0.04, 0.05), trim)
            strip((0, yy + sg * 0.001, (F + 1.1) / 2), (8.5, 0.002, 1.1 - F), wain)
        for (xx, sg) in ((-4.25, 1), (4.25, -1)):
            strip((xx + sg * 0.012, 0, F + 0.071), (0.024, 6.5, 0.142), trim)
            strip((xx + sg * 0.02, 0, 1.13), (0.04, 6.5, 0.05), trim)
            strip((xx + sg * 0.001, 0, (F + 1.1) / 2), (0.002, 6.5, 1.1 - F), wain)
        for sg, xx in ((1, 1.65), (-1, 1.4)):
            strip((xx + sg * 0.012, 0, F + 0.071), (0.024, 6.5, 0.142), trim)
            strip((xx + sg * 0.02, 0, 1.13), (0.04, 6.5, 0.05), trim)
    # front door slab (closed) for visual reference of door width (door is in the shell, preview only)
    dm = make_mat('_door', '#7a2f2a', rough=0.6)
    _box('_door', (0, -3.24, (F + 2.3) / 2 + 0.05), (1.0, 0.04, 2.1), dm)
    return STAND


def _img(name):
    p = '%s/%s.jpg' % (TEXDIR, name)
    if not os.path.exists(p):
        return None
    im = bpy.data.images.get(name + '.jpg') or bpy.data.images.load(p)
    return im


def preview_mats(objs, use_tex=True):
    """attach texture / vertex colour nodes for Cycles preview only (export does not use these nodes)."""
    seen = set()
    for ob in objs:
        for slot in ob.material_slots:
            m = slot.material
            if m is None or m.name in seen or m.name.startswith('_'):
                continue
            seen.add(m.name)
            nt = m.node_tree
            b = nt.nodes.get('Principled BSDF')
            if b is None:
                continue
            base = tuple(b.inputs['Base Color'].default_value)
            pv = PREV.get(m.name)
            tx = m.get('tex', '')
            im = _img(tx) if (tx and use_tex) else None
            vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Col'
            mixc = nt.nodes.new('ShaderNodeMix'); mixc.data_type = 'RGBA'; mixc.blend_type = 'MULTIPLY'
            mixc.inputs[0].default_value = 1.0
            if im is None and pv:
                lin = hex_rgb(pv) if isinstance(pv, str) else pv
                if m.name == 'leaf' or m.name == 'petal' or m.name == 'felt':
                    lin = (1, 1, 1)
                base = (lin[0], lin[1], lin[2], 1)
            mixc.inputs[6].default_value = base
            nt.links.new(vc.outputs['Color'], mixc.inputs[7])
            last = mixc.outputs[2]
            if im is not None:
                it = nt.nodes.new('ShaderNodeTexImage'); it.image = im; it.extension = 'REPEAT'
                uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'UVMap'
                nt.links.new(uvn.outputs['UV'], it.inputs['Vector'])
                m2 = nt.nodes.new('ShaderNodeMix'); m2.data_type = 'RGBA'; m2.blend_type = 'MULTIPLY'
                m2.inputs[0].default_value = 1.0
                nt.links.new(last, m2.inputs[6]); nt.links.new(it.outputs['Color'], m2.inputs[7])
                last = m2.outputs[2]
                imn = _img(tx + '_n')
                if imn is not None:
                    imn.colorspace_settings.name = 'Non-Color'
                    itn = nt.nodes.new('ShaderNodeTexImage'); itn.image = imn
                    nt.links.new(uvn.outputs['UV'], itn.inputs['Vector'])
                    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 0.6
                    nt.links.new(itn.outputs['Color'], nm.inputs['Color'])
                    nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
                imr = _img(tx + '_r')
                if imr is not None:
                    imr.colorspace_settings.name = 'Non-Color'
                    itr = nt.nodes.new('ShaderNodeTexImage'); itr.image = imr
                    nt.links.new(uvn.outputs['UV'], itr.inputs['Vector'])
                    nt.links.new(itr.outputs['Color'], b.inputs['Roughness'])
            # backfacing marker (inverted normals show magenta) for non-double materials
            if not bool(m.get('double', False)):
                geo = nt.nodes.new('ShaderNodeNewGeometry')
                mixb = nt.nodes.new('ShaderNodeMix'); mixb.data_type = 'RGBA'
                nt.links.new(geo.outputs['Backfacing'], mixb.inputs[0])
                nt.links.new(last, mixb.inputs[6])
                mixb.inputs[7].default_value = (1, 0, 1, 1)
                last = mixb.outputs[2]
            nt.links.new(last, b.inputs['Base Color'])
            if b.inputs['Alpha'].default_value < 0.99:
                b.inputs['Alpha'].default_value = 1.0
                b.inputs['Transmission Weight'].default_value = 1.0
                b.inputs['Roughness'].default_value = 0.0
                b.inputs['IOR'].default_value = 1.02


def setup_lights(lamps=(), day=1.0):
    sc = bpy.context.scene
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.6, 0.72, 0.9, 1); bg.inputs[1].default_value = 1.0 * day

    def area(name, loc, rot, size, e, col=(1, 0.96, 0.9)):
        d = bpy.data.lights.new(name, 'AREA'); d.energy = e * day; d.size = size[0]; d.size_y = size[1]; d.shape = 'RECTANGLE'; d.color = col
        o = bpy.data.objects.new(name, d); o.location = loc; o.rotation_euler = [math.radians(a) for a in rot]
        sc.collection.objects.link(o)
    for x in (-2.9, 2.9):
        area('wf', (x, -3.75, 2.05), (-90, 0, 0), (1.0, 1.25), 260)
    for x in (-2.2, 2.2):
        area('wb', (x, 3.75, 2.05), (90, 0, 0), (1.0, 1.25), 260)
    for y in (-0.9, 1.6):
        area('wr', (4.75, y, 2.1), (0, 90, 0), (0.9, 1.2), 220)
    for (x, y) in ((-2.5, 0), (0.5, 0), (3, 0)):
        d = bpy.data.lights.new('fill', 'POINT'); d.energy = 380; d.shadow_soft_size = 0.4; d.color = (1, 0.82, 0.6)
        o = bpy.data.objects.new('fill', d); o.location = (x, y, 2.7); sc.collection.objects.link(o)
    for (x, y, z, e) in lamps:
        d = bpy.data.lights.new('lp', 'POINT'); d.energy = e; d.shadow_soft_size = 0.04; d.color = (1, 0.65, 0.35)
        o = bpy.data.objects.new('lp', d); o.location = (x, y, z); sc.collection.objects.link(o)


def render(path, cam_loc, target, lens=24, res=(960, 640), samples=32):
    sc = bpy.context.scene
    cam = bpy.data.cameras.new('cam'); cam.lens = lens; cam.clip_start = 0.03
    co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co)
    co.location = cam_loc
    d = Vector(target) - Vector(cam_loc)
    co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = co
    sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.device = 'CPU'
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.05
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = path; sc.render.image_settings.file_format = 'PNG'
    sc.view_settings.exposure = float(os.environ.get('EXPO', 0.5))
    try:
        sc.view_settings.view_transform = 'AgX'
    except Exception:
        pass
    bpy.ops.render.render(write_still=True)


# ------------------------------------------------------------------------------------ AO bake to vertex colours
def bake_ao(objs, distance=0.6, samples=48, strength=0.78, floor=0.22):
    """Cycles AO bake per object into a POINT colour attribute, then multiply into the corner 'Col' attribute.
    Everything currently linked to the scene (stand-in room + furniture) acts as occluder."""
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = samples
    sc.render.bake.target = 'VERTEX_COLORS'
    sc.render.bake.use_selected_to_active = False
    sc.render.bake.use_clear = True
    w = bpy.data.worlds.new('AOW') if bpy.context.scene.world is None else bpy.context.scene.world
    sc.world = w; w.use_nodes = True
    w.light_settings.distance = distance
    try:
        w.light_settings.use_ambient_occlusion = True
    except Exception:
        pass
    ghosts = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(('static_glass', 'static_water', 'lamp_bd'))]
    for o in ghosts:
        o.hide_render = True          # transparent / emissive things must not occlude (AO would darken everything behind glass)
    for ob in objs:
        if ob.type != 'MESH' or not len(ob.data.vertices) or ob in ghosts:
            continue
        me = ob.data
        # make sure a clean AO attribute exists
        if 'AO' in me.color_attributes:
            me.color_attributes.remove(me.color_attributes['AO'])
        ao = me.color_attributes.new('AO', 'FLOAT_COLOR', 'POINT')
        me.color_attributes.active_color = ao
        for o in bpy.context.view_layer.objects:
            o.select_set(False)
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.bake(type='AO')
        nv = len(me.vertices)
        a = np.zeros(nv * 4, dtype=np.float32)
        me.color_attributes['AO'].data.foreach_get('color', a)
        aov = a.reshape(-1, 4)[:, 0]
        nl = len(me.loops)
        vi = np.zeros(nl, dtype=np.int32)
        me.loops.foreach_get('vertex_index', vi)
        col = me.color_attributes.get('Col')
        if col is None:
            col = me.color_attributes.new('Col', 'FLOAT_COLOR', 'CORNER')
        c = np.zeros(nl * 4, dtype=np.float32)
        col.data.foreach_get('color', c)
        c = c.reshape(-1, 4)
        k = floor + (1 - floor) * np.clip(aov[vi], 0, 1) ** 1.2
        k = 1 - strength * (1 - k)
        c[:, :3] *= k[:, None]
        col.data.foreach_set('color', c.ravel())
        me.color_attributes.remove(me.color_attributes['AO'])
        me.color_attributes.active_color = me.color_attributes['Col']
        me.update()
    for o in ghosts:
        o.hide_render = False


def backface_check(view, cam_loc, target, lens, res=(480, 320)):
    """debug pass: every surface emits green (front-facing) or red (back-facing, NOT double-sided materials); reports red fraction"""
    sc = bpy.context.scene
    dm = bpy.data.materials.new('_dbg'); dm.use_nodes = True
    nt = dm.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    geo = nt.nodes.new('ShaderNodeNewGeometry'); em = nt.nodes.new('ShaderNodeEmission'); out = nt.nodes.new('ShaderNodeOutputMaterial')
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs[6].default_value = (0, 1, 0, 1); mix.inputs[7].default_value = (1, 0, 0, 1)
    nt.links.new(geo.outputs['Backfacing'], mix.inputs[0]); nt.links.new(mix.outputs[2], em.inputs['Color']); nt.links.new(em.outputs[0], out.inputs[0])
    # double-sided mats should be exempt -> only red when the object's own material is not double: handled by overriding only non-double objects
    saved = {}
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            saved[ob.name] = [s.material for s in ob.material_slots]
            for s in ob.material_slots:
                if s.material is None or not bool(s.material.get('double', False)):
                    s.material = dm
                else:
                    s.material = bpy.data.materials.get('_dbg_ok') or _ok_mat()
    old = (sc.render.resolution_x, sc.render.resolution_y, sc.cycles.samples, sc.cycles.use_denoising, sc.view_settings.view_transform, sc.view_settings.exposure, sc.render.filepath)
    cam = [o for o in bpy.data.objects if o.type == 'CAMERA']
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.cycles.samples = 2; sc.cycles.use_denoising = False
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = 0
    sc.render.filepath = '/tmp/_bf.png'
    bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load('/tmp/_bf.png', check_existing=False)
    a = np.array(im.pixels[:], np.float32).reshape(-1, 4)
    red = float(((a[:, 0] > 0.6) & (a[:, 1] < 0.3)).mean())
    print('BACKFACE', view, round(red * 100, 3), '%')
    bpy.data.images.remove(im)
    for ob in bpy.data.objects:
        if ob.name in saved:
            for s, m in zip(ob.material_slots, saved[ob.name]):
                s.material = m
    sc.render.resolution_x, sc.render.resolution_y, sc.cycles.samples, sc.cycles.use_denoising, sc.view_settings.view_transform, sc.view_settings.exposure, sc.render.filepath = old
    sc.view_settings.view_transform = 'AgX'
    bpy.data.materials.remove(dm)


def _ok_mat():
    m = bpy.data.materials.new('_dbg_ok'); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    em = nt.nodes.new('ShaderNodeEmission'); out = nt.nodes.new('ShaderNodeOutputMaterial')
    em.inputs['Color'].default_value = (0, 0, 1, 1)
    nt.links.new(em.outputs[0], out.inputs[0])
    return m
