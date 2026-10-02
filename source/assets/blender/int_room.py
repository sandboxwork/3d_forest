"""Temporary stand-in room + preview rendering (never exported)."""
from int_lib import *

STAND = []


def _box(name, c, s, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c)
    o = bpy.context.object
    o.scale = s
    o.name = name
    o.data.materials.append(mat)
    STAND.append(o)
    return o


def build_room():
    wall = make_mat('_wall', '#d9cfba', rough=0.9)
    wood = make_mat('_floor', '#8a6440', rough=0.6)
    beam = make_mat('_beam', '#4e3520', rough=0.7)
    stone = make_mat('_stone', '#7d7770', rough=0.95)
    ceil = make_mat('_ceil', '#b89a70', rough=0.8)
    # floor / ceiling
    _box('_fl', (0, 0, F - 0.05), (9, 7, 0.1), wood)
    _box('_ce', (0, 0, 3.15 + 0.05), (9, 7, 0.1), ceil)
    for x in [-3.85, -2.75, -1.65, -0.55, 0.55, 1.65, 2.75, 3.85]:
        _box('_bm', (x, 0, 3.05), (0.16, 6.5, 0.2), beam)
    T = 0.25
    # walls with window holes: build as strips
    def wall_y(yc, wins, sign):
        # wall along x at y=yc (thickness T outward), windows list of (xc, w, zs, ze)
        xs = [-4.5]
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
    wall_x(4.25, [(-0.9, 0.9, 1.5, 2.7), (1.6, 0.9, 1.5, 2.7)], 1)
    _box('_wl', (-4.25 - T / 2, 0, (F + 3.15) / 2), (T, 7, 3.15 - F), wall)
    # partition with door
    _box('_p', (1.525, -2.0625, (F + 3.15) / 2), (0.25, 2.375, 3.15 - F), wall)
    _box('_p', (1.525, 1.6625, (F + 3.15) / 2), (0.25, 3.175, 3.15 - F), wall)
    _box('_p', (1.525, -0.4, (2.15 + 3.15) / 2), (0.25, 0.95, 3.15 - 2.15), wall)
    # fireplace breast + hearth
    # hollow fireplace: two piers, lintel, hearth slab (opening 1.1 wide, z F..1.3)
    _box('_fp', (-4.0, -0.825, (F + 3.15) / 2), (0.5, 0.55 + 0.0, 3.15 - F), stone)
    _box('_fp', (-4.0, 0.825, (F + 3.15) / 2), (0.5, 0.55, 3.15 - F), stone)
    _box('_fp', (-4.0, -1.35, (F + 3.15) / 2), (0.5, 0.5, 3.15 - F), stone)
    _box('_fp', (-4.0, 1.35, (F + 3.15) / 2), (0.5, 0.5, 3.15 - F), stone)
    _box('_fp', (-4.0, 0.0, (1.3 + 3.15) / 2), (0.5, 1.1, 3.15 - 1.3), stone)
    _box('_hs', (-3.98, 0.0, F + 0.05), (0.55, 2.0, 0.1), stone)
    _box('_hs', (-4.1, 0.0, F + 0.14), (0.3, 1.1, 0.06), make_mat('_ash', '#2a2522', rough=1.0))
    return STAND


def preview_mats(objs):
    """attach texture / vertex colour nodes for Cycles preview only."""
    seen = set()
    for ob in objs:
        for slot in ob.material_slots:
            m = slot.material
            if m is None or m.name in seen:
                continue
            seen.add(m.name)
            m.use_backface_culling = not bool(m.get('double', False))
            nt = m.node_tree
            b = nt.nodes.get('Principled BSDF')
            if b is None:
                continue
            base = tuple(b.inputs['Base Color'].default_value)
            vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Col'
            mixc = nt.nodes.new('ShaderNodeMix'); mixc.data_type = 'RGBA'; mixc.blend_type = 'MULTIPLY'
            mixc.inputs[0].default_value = 1.0
            mixc.inputs[6].default_value = base
            nt.links.new(vc.outputs['Color'], mixc.inputs[7])
            last = mixc.outputs[2]
            tx = m.get('tex', '')
            if tx:
                p = '/shared/river/assets/tex/%s.jpg' % tx
                if os.path.exists(p):
                    it = nt.nodes.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(p)
                    it.extension = 'REPEAT'
                    uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'UVMap'
                    nt.links.new(uvn.outputs['UV'], it.inputs['Vector'])
                    m2 = nt.nodes.new('ShaderNodeMix'); m2.data_type = 'RGBA'; m2.blend_type = 'MULTIPLY'
                    m2.inputs[0].default_value = 1.0
                    nt.links.new(last, m2.inputs[6]); nt.links.new(it.outputs['Color'], m2.inputs[7])
                    last = m2.outputs[2]
            nt.links.new(last, b.inputs['Base Color'])
            if m['double'] if 'double' in m else False:
                pass
            if b.inputs['Alpha'].default_value < 0.99:
                # glass-like for preview
                b.inputs['Alpha'].default_value = 1.0
                b.inputs['Transmission Weight'].default_value = 0.9
                b.inputs['Roughness'].default_value = 0.05


def setup_lights(extra_points=()):
    sc = bpy.context.scene
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.6, 0.72, 0.9, 1); bg.inputs[1].default_value = 1.0
    # daylight panels at windows (facing inside)
    def area(name, loc, rot, size, e, col=(1, 0.96, 0.9)):
        d = bpy.data.lights.new(name, 'AREA'); d.energy = e; d.size = size[0]; d.size_y = size[1]; d.shape = 'RECTANGLE'; d.color = col
        o = bpy.data.objects.new(name, d); o.location = loc; o.rotation_euler = [math.radians(a) for a in rot]
        sc.collection.objects.link(o)
    for x in (-2.9, 2.9):
        area('wf', (x, -3.75, 2.05), (-90, 0, 0), (1.0, 1.25), 260)   # facing +y? area faces -Z local; rot -90 about x -> faces +y
    for x in (-2.2, 2.2):
        area('wb', (x, 3.75, 2.05), (90, 0, 0), (1.0, 1.25), 260)
    for y in (-0.9, 1.6):
        area('wr', (4.75, y, 2.1), (0, 90, 0), (0.9, 1.2), 220)
    # ceiling fill
    for (x, y) in ((-2.5, 0), (0.5, 0), (3, 0)):
        d = bpy.data.lights.new('fill', 'POINT'); d.energy = 420; d.shadow_soft_size = 0.4; d.color = (1, 0.82, 0.6)
        o = bpy.data.objects.new('fill', d); o.location = (x, y, 2.7); sc.collection.objects.link(o)
    for (x, y, z, e) in extra_points:
        d = bpy.data.lights.new('lp', 'POINT'); d.energy = e; d.shadow_soft_size = 0.05; d.color = (1, 0.65, 0.35)
        o = bpy.data.objects.new('lp', d); o.location = (x, y, z); sc.collection.objects.link(o)


def render(path, cam_loc, target, lens=24, res=(960, 640), samples=32):
    sc = bpy.context.scene
    cam = bpy.data.cameras.new('cam'); cam.lens = lens; cam.clip_start = 0.05
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
    sc.view_settings.exposure = 1.6
    sc.view_settings.view_transform = 'Filmic' if 'Filmic' in [x.identifier for x in sc.view_settings.bl_rna.properties['view_transform'].enum_items] else 'AgX'
    bpy.ops.render.render(write_still=True)
