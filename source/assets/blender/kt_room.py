"""Temporary stand-in room (walls/floor/ceiling with window holes) + preview rendering + AO-occluder.  NEVER exported."""
from kt_lib import *
from kt_mats import PBR_TINT, HI_FALLBACK

TEXDIR = '/shared/river/assets/tex/'
STAND = []


def _box(name, c, s, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c)
    o = bpy.context.object
    o.scale = s
    o.name = name
    o.data.materials.append(mat)
    STAND.append(o)
    return o


def _objtex(m, texname, tile, tint, rough=0.9):
    """stand-in material using object-space mapping"""
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(b.outputs[0], out.inputs[0])
    b.inputs['Roughness'].default_value = rough
    p = TEXDIR + texname + '.jpg'
    if os.path.exists(p):
        tc = nt.nodes.new('ShaderNodeNewGeometry'); mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (1 / tile, 1 / tile, 1 / tile)
        it = nt.nodes.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(p)
        it.projection = 'BOX'; it.projection_blend = 0.1
        nt.links.new(tc.outputs['Position'], mp.inputs[0]); nt.links.new(mp.outputs[0], it.inputs[0])
        mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1
        mx.inputs[6].default_value = tint + (1,)
        nt.links.new(it.outputs[0], mx.inputs[7]); nt.links.new(mx.outputs[2], b.inputs['Base Color'])
    else:
        b.inputs['Base Color'].default_value = tint + (1,)


def build_room(beams=True):
    wall = bpy.data.materials.new('_wall'); _objtex(wall, 'pbr_plaster', 1.0, (0.95, 0.93, 0.9))
    fl = bpy.data.materials.new('_floor'); _objtex(fl, 'pbr_wood_floor', 1.0, (1, 1, 1), 0.6)
    beam = bpy.data.materials.new('_beam'); _objtex(beam, 'pbr_wood_dark', 0.6, (1, 1, 1), 0.7)
    ceil = bpy.data.materials.new('_ceil'); _objtex(ceil, 'pbr_wood_pine', 0.6, (0.9, 0.9, 0.9), 0.8)
    trim = make_mat('_trim', '#cfc8b8', rough=0.7)
    wain = bpy.data.materials.new('_wain'); _objtex(wain, 'pbr_wood_pine', 0.6, (0.9, 0.78, 0.6), 0.6)
    _box('_fl', (0, 0, F - 0.05), (9, 7, 0.1), fl)
    _box('_ce', (0, 0, 3.15 + 0.05), (9, 7, 0.1), ceil)
    if beams:
        for x in (-3.85, -2.75, -1.65, -0.55, 0.55, 2.75, 3.85):
            _box('_bm', (x, 0, 3.055), (0.15, 6.5, 0.19), beam)
        _box('_bm', (0, 0, 3.04), (8.5, 0.2, 0.22), beam)
    T = 0.25
    wins_front = [(-2.9, 1.0, 1.43, 2.68), (2.9, 1.0, 1.43, 2.68), (0.0, 1.0, F, 2.3)]
    wins_back = [(-2.2, 1.0, 1.43, 2.68), (2.2, 1.0, 1.43, 2.68)]

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
        # wainscot band + baseboard + chair rail
        _box('_wn', (0, yc - sign * 0.01, (F + 1.1) / 2), (8.5, 0.02, 1.1 - F), wain)
        _box('_bb', (0, yc - sign * 0.015, F + 0.07), (8.5, 0.03, 0.14), trim)
        _box('_cr', (0, yc - sign * 0.02, 1.13), (8.5, 0.04, 0.06), trim)
        for (xc, w, zs, ze) in wins:   # window frames (stool) + glass-less opening
            _box('_st', (xc, yc - sign * 0.04, zs - 0.005), (w + 0.2, 0.09, 0.04), trim)
    wall_y(-3.25, wins_front, -1)
    wall_y(3.25, wins_back, 1)

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
        _box('_bb', (xc - sign * 0.015, 0, F + 0.07), (0.03, 7, 0.14), trim)
        _box('_wn', (xc - sign * 0.01, 0, (F + 1.1) / 2), (0.02, 7, 1.1 - F), wain)
    wall_x(4.25, [(-0.9, 0.9, 1.5, 2.7), (1.6, 0.9, 1.5, 2.7)], 1)
    wall_x(-4.25, [], -1)
    # partition x in [1.4,1.65] with door y -0.875..0.075
    _box('_p', (1.525, -2.0625, (F + 3.15) / 2), (0.25, 2.375, 3.15 - F), wall)
    _box('_p', (1.525, 1.6625, (F + 3.15) / 2), (0.25, 3.175, 3.15 - F), wall)
    _box('_p', (1.525, -0.4, (2.3 + 3.15) / 2), (0.25, 0.95, 3.15 - 2.3), wall)
    # fireplace breast (left wall) as simple stone block
    stone = make_mat('_stone', '#7d7770', rough=0.95)
    _box('_fp', (-4.0, 0.0, (F + 3.15) / 2), (0.5, 1.8, 3.15 - F), stone)
    return STAND


def preview_mats(objs, ao_attr=None):
    """attach texture / vertex colour / normal / roughness nodes for Cycles preview (not exported)."""
    seen = set()
    for ob in objs:
        for slot in ob.material_slots:
            m = slot.material
            if m is None or m.name in seen or m.name.startswith('_'):
                continue
            seen.add(m.name)
            m.use_backface_culling = False
            nt = m.node_tree
            b = nt.nodes.get('Principled BSDF')
            if b is None:
                continue
            base = tuple(b.inputs['Base Color'].default_value)
            vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Col'
            mixc_ = nt.nodes.new('ShaderNodeMix'); mixc_.data_type = 'RGBA'; mixc_.blend_type = 'MULTIPLY'
            mixc_.inputs[0].default_value = 1.0
            mixc_.inputs[6].default_value = base
            nt.links.new(vc.outputs['Color'], mixc_.inputs[7])
            last = mixc_.outputs[2]
            tx = m.get('tex', '')
            p = TEXDIR + tx + '.jpg' if tx else ''
            rough = b.inputs['Roughness'].default_value
            if tx and os.path.exists(p):
                it = nt.nodes.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(p)
                it.extension = 'REPEAT'
                uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'UVMap'
                nt.links.new(uvn.outputs['UV'], it.inputs['Vector'])
                m2 = nt.nodes.new('ShaderNodeMix'); m2.data_type = 'RGBA'; m2.blend_type = 'MULTIPLY'
                m2.inputs[0].default_value = 1.0
                nt.links.new(last, m2.inputs[6]); nt.links.new(it.outputs['Color'], m2.inputs[7])
                last = m2.outputs[2]
                pr = TEXDIR + tx + '_r.jpg'
                if os.path.exists(pr):
                    ir = nt.nodes.new('ShaderNodeTexImage'); ir.image = bpy.data.images.load(pr); ir.image.colorspace_settings.name = 'Non-Color'
                    nt.links.new(uvn.outputs['UV'], ir.inputs['Vector'])
                    nt.links.new(ir.outputs['Color'], b.inputs['Roughness'])
                pn = TEXDIR + tx + '_n.jpg'
                if os.path.exists(pn):
                    inn = nt.nodes.new('ShaderNodeTexImage'); inn.image = bpy.data.images.load(pn); inn.image.colorspace_settings.name = 'Non-Color'
                    nt.links.new(uvn.outputs['UV'], inn.inputs['Vector'])
                    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 1.1
                    nt.links.new(inn.outputs['Color'], nm.inputs['Color'])
                    nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
            nt.links.new(last, b.inputs['Base Color'])
            if b.inputs['Alpha'].default_value < 0.99 and m.name not in ('shadow', 'soot', 'damp'):
                b.inputs['Alpha'].default_value = 1.0
                b.inputs['Transmission Weight'].default_value = 0.95
                b.inputs['Roughness'].default_value = 0.05
                b.inputs['IOR'].default_value = 1.45
            if b.inputs['Emission Strength'].default_value > 0:
                b.inputs['Emission Strength'].default_value = 25.0


def setup_lights(extra_points=(), sun=True):
    sc = bpy.context.scene
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.6, 0.72, 0.9, 1); bg.inputs[1].default_value = 1.0

    def area(name, loc, rot, size, e, col=(1, 0.96, 0.9)):
        d = bpy.data.lights.new(name, 'AREA'); d.energy = e; d.size = size[0]; d.size_y = size[1]; d.shape = 'RECTANGLE'; d.color = col
        o = bpy.data.objects.new(name, d); o.location = loc; o.rotation_euler = [math.radians(a) for a in rot]
        sc.collection.objects.link(o)
    for x in (-2.9, 2.9):
        area('wf', (x, -3.85, 2.05), (-90, 0, 0), (1.0, 1.25), 200)
    for x in (-2.2, 2.2):
        area('wb', (x, 3.85, 2.05), (90, 0, 0), (1.0, 1.25), 240)
    for y in (-0.9, 1.6):
        area('wr', (4.85, y, 2.1), (0, 90, 0), (0.9, 1.2), 220)
    if sun:
        d = bpy.data.lights.new('sun', 'SUN'); d.energy = 3.0; d.angle = math.radians(3)
        o = bpy.data.objects.new('sun', d); o.rotation_euler = (math.radians(58), 0, math.radians(18))
        sc.collection.objects.link(o)
    for (x, y) in ((-2.5, 0), (0.5, 0), (3, 0), (-2.5, -2.5), (-2.5, 2.3)):
        d = bpy.data.lights.new('fill', 'POINT'); d.energy = 260; d.shadow_soft_size = 0.4; d.color = (1, 0.85, 0.65)
        o = bpy.data.objects.new('fill', d); o.location = (x, y, 2.75); sc.collection.objects.link(o)
    for (x, y, z, e) in extra_points:
        d = bpy.data.lights.new('lp', 'POINT'); d.energy = e; d.shadow_soft_size = 0.04; d.color = (1, 0.65, 0.35)
        o = bpy.data.objects.new('lp', d); o.location = (x, y, z); sc.collection.objects.link(o)


def render(path, cam_loc, target, lens=24, res=(960, 640), samples=48, exposure=0.55):
    sc = bpy.context.scene
    cam = bpy.data.cameras.new('cam'); cam.lens = lens; cam.clip_start = 0.03
    co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co)
    co.location = cam_loc
    d = Vector(target) - Vector(cam_loc)
    co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = co
    sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.device = 'CPU'
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.transparent_max_bounces = 32
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.03
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = path; sc.render.image_settings.file_format = 'PNG'
    sc.view_settings.exposure = exposure
    names = [x.identifier for x in sc.view_settings.bl_rna.properties['view_transform'].enum_items]
    sc.view_settings.view_transform = 'AgX' if 'AgX' in names else 'Filmic'
    bpy.ops.render.render(write_still=True)
