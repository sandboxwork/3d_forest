"""Temporary stand-in room + preview rendering for the living zone (NEVER exported)."""
from lv_lib import *

STAND = []
TEXDIR = '/shared/river/assets/tex/'


def _box(name, c, s, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c)
    o = bpy.context.object
    o.scale = s
    o.name = name
    o.data.materials.append(mat)
    STAND.append(o)
    return o


def _img(mat, fname, scale=1.0, mix=None):
    p = TEXDIR + fname + '.jpg'
    if not os.path.exists(p):
        return
    nt = mat.node_tree
    b = nt.nodes.get('Principled BSDF')
    it = nt.nodes.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(p)
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale, scale, scale)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], it.inputs['Vector'])
    it.projection = 'BOX'; it.projection_blend = 0.2
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1
    mx.inputs[6].default_value = b.inputs['Base Color'].default_value
    nt.links.new(it.outputs['Color'], mx.inputs[7])
    nt.links.new(mx.outputs[2], b.inputs['Base Color'])


def build_room():
    wall = make_mat('_wall', '#f0e8d6', rough=0.9); _img(wall, 'hi_plaster', 1.0)
    wood = make_mat('_floor', '#c09a68', rough=0.55); _img(wood, 'hi_wood', 1.0)
    beam = make_mat('_beam', '#5b4128', rough=0.7)
    stone = make_mat('_stone', '#9a9388', rough=0.95)
    ceil = make_mat('_ceil', '#b89a70', rough=0.8)
    wains = make_mat('_wains', '#b8946a', rough=0.6); _img(wains, 'hi_wood', 1.0)
    soot = make_mat('_soot', '#1d1a18', rough=1.0)
    F_ = F
    _box('_fl', (0, 0, F_ - 0.05), (9, 7, 0.1), wood)
    _box('_ce', (0, 0, 3.15 + 0.05), (9, 7, 0.1), ceil)
    for x in [-3.85, -2.75, -1.65, -0.55, 0.55, 2.75, 3.85]:
        _box('_bm', (x, 0, 3.05), (0.15, 6.5, 0.2), beam)
    _box('_bm', (0, 0, 3.04), (8.5, 0.2, 0.22), beam)
    T = 0.25

    def wall_y(yc, wins, sign):
        segs = []; cur = -4.5
        for (xc, w, zs, ze) in sorted(wins):
            segs.append((cur, xc - w / 2)); cur = xc + w / 2
        segs.append((cur, 4.5))
        for a, b in segs:
            if b > a:
                _box('_w', ((a + b) / 2, yc + sign * T / 2, (F_ + 3.15) / 2), (b - a, T, 3.15 - F_), wall)
        for (xc, w, zs, ze) in wins:
            _box('_w', (xc, yc + sign * T / 2, (F_ + zs) / 2), (w, T, zs - F_), wall)
            _box('_w', (xc, yc + sign * T / 2, (ze + 3.15) / 2), (w, T, 3.15 - ze), wall)
    wall_y(-3.25, [(-2.9, 1.0, 1.43, 2.68), (2.9, 1.0, 1.43, 2.68), (0.0, 1.0, F_, 2.3)], -1)
    wall_y(3.25, [(-2.2, 1.0, 1.43, 2.68), (2.2, 1.0, 1.43, 2.68)], 1)

    def wall_x(xc, wins, sign):
        segs = []; cur = -3.5
        for (yc, w, zs, ze) in sorted(wins):
            segs.append((cur, yc - w / 2)); cur = yc + w / 2
        segs.append((cur, 3.5))
        for a, b in segs:
            if b > a:
                _box('_w', (xc + sign * T / 2, (a + b) / 2, (F_ + 3.15) / 2), (T, b - a, 3.15 - F_), wall)
        for (yc, w, zs, ze) in wins:
            _box('_w', (xc + sign * T / 2, yc, (F_ + zs) / 2), (T, w, zs - F_), wall)
            _box('_w', (xc + sign * T / 2, yc, (ze + 3.15) / 2), (T, w, 3.15 - ze), wall)
    wall_x(4.25, [(-0.9, 0.9, 1.5, 2.7), (1.6, 0.9, 1.5, 2.7)], 1)
    # left wall: solid except fireplace (handled below)
    _box('_wl', (-4.25 - T / 2, -2.25, (F_ + 3.15) / 2), (T, 2.0, 3.15 - F_), wall)
    _box('_wl', (-4.25 - T / 2, 2.25, (F_ + 3.15) / 2), (T, 2.0, 3.15 - F_), wall)
    _box('_wl', (-4.25 - 0.6 / 2, 0.0, (F_ + 3.15) / 2), (0.6, 2.5, 3.15 - F_), stone)
    # partition with doorway (doorway centred y=-0.4, 0.95 wide)
    _box('_p', (1.525, -2.0625, (F_ + 3.15) / 2), (0.25, 2.375, 3.15 - F_), wall)
    _box('_p', (1.525, 1.6625, (F_ + 3.15) / 2), (0.25, 3.175, 3.15 - F_), wall)
    _box('_p', (1.525, -0.4, (2.15 + 3.15) / 2), (0.25, 0.95, 3.15 - 2.15), wall)
    # wainscot (visual only)
    # fireplace: piers + lintel + breast
    _box('_fp', (-4.0, -0.825, 0.9), (0.5, 0.55, 1.1), stone)
    _box('_fp', (-4.0, 0.825, 0.9), (0.5, 0.55, 1.1), stone)
    _box('_fp', (-3.97, -1.125, 0.9), (0.55, 0.06, 1.1), stone) if False else None
    _box('_fp', (-4.0, -1.2, 0.9), (0.5, 0.3, 1.1), stone)
    _box('_fp', (-4.0, 1.2, 0.9), (0.5, 0.3, 1.1), stone)
    _box('_fp', (-4.0, 0.0, 1.405), (0.5, 1.1, 0.12), stone)
    _box('_hs', (-4.0, 0.0, 0.375), (0.5, 2.3, 0.15), make_mat('_hearth', '#7e7a72', rough=0.85))
    _box('_mt', (-3.92, 0.0, 1.55), (0.66, 2.5, 0.1), beam)
    # chimney breast above mantel (plaster, x -4.25..-3.91)
    # chimney breast (plaster), tapering: (n,z) = (0,1.6) (0.34,1.6) (0.34,2.0) (0.22,3.15) (0,3.15), y in +-0.95
    bmb = bmesh.new()
    prof = [(0, 1.6), (0.34, 1.6), (0.34, 2.0), (0.22, 3.15), (0, 3.15)]
    for yy in (-0.95, 0.95):
        pass
    vb = [[bmb.verts.new((-4.25 + n_, y_, z_)) for (n_, z_) in prof] for y_ in (-0.95, 0.95)]
    bmb.faces.new(vb[0][::-1]); bmb.faces.new(vb[1])
    for i in range(len(prof)):
        j = (i + 1) % len(prof)
        bmb.faces.new([vb[0][i], vb[0][j], vb[1][j], vb[1][i]])
    bmesh.ops.recalc_face_normals(bmb, faces=bmb.faces[:])
    mb = bpy.data.meshes.new('_br'); bmb.to_mesh(mb); bmb.free()
    ob_ = bpy.data.objects.new('_br', mb); bpy.context.scene.collection.objects.link(ob_); ob_.data.materials.append(wall); STAND.append(ob_)
    _box('_sootbox', (-4.37, 0.0, 0.9), (0.25, 1.1, 0.9), soot)
    # embers (emissive)
    em = make_mat('_ember', '#ff5a1a', rough=0.9, emit='#ff4a10', emit_strength=6.0)
    _box('_em', (-4.14, 0.0, 0.475), (0.46, 0.84, 0.05), em)
    for o in STAND:
        o.hide_select = True
    return STAND


def preview_mats(objs):
    """attach texture / vertex colour nodes for Cycles preview only. pbr_* stand-ins map onto hi_* if pbr is missing."""
    STAND_IN = {'pbr_wood': 'hi_wood', 'pbr_fabric_linen': 'hi_weave', 'pbr_fabric_wool': 'hi_knit', 'pbr_fabric_burlap': 'hi_weave',
                'pbr_leather': 'hi_leather', 'pbr_book_cloth': 'hi_weave', 'pbr_iron': 'hi_metal', 'pbr_wicker': 'hi_wicker',
                'pbr_plaster': 'hi_plaster', 'pbr_rug': 'hi_knit', 'pbr_paper': None}
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
            p = None
            if tx:
                if os.path.exists(TEXDIR + tx + '.jpg'):
                    p = TEXDIR + tx + '.jpg'
                else:
                    for k, v in STAND_IN.items():
                        if tx.startswith(k) and v:
                            p = TEXDIR + v + '.jpg'; break
            if p and os.path.exists(p):
                it = nt.nodes.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(p)
                it.extension = 'REPEAT'
                uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'UVMap'
                nt.links.new(uvn.outputs['UV'], it.inputs['Vector'])
                m2 = nt.nodes.new('ShaderNodeMix'); m2.data_type = 'RGBA'; m2.blend_type = 'MULTIPLY'
                m2.inputs[0].default_value = 1.0
                nt.links.new(last, m2.inputs[6]); nt.links.new(it.outputs['Color'], m2.inputs[7])
                last = m2.outputs[2]
            nt.links.new(last, b.inputs['Base Color'])
            if b.inputs['Alpha'].default_value < 0.99 and m.name.startswith('glass'):
                b.inputs['Alpha'].default_value = 1.0
                b.inputs['Transmission Weight'].default_value = 0.92
                b.inputs['Roughness'].default_value = 0.03
                b.inputs['IOR'].default_value = 1.45


def setup_lights(extra_points=(), day=1.0):
    sc = bpy.context.scene
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.55, 0.68, 0.95, 1); bg.inputs[1].default_value = 1.2 * day
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 2.6 * day; sun.angle = 0.05; sun.color = (1, 0.93, 0.8)
    so = bpy.data.objects.new('sun', sun); so.rotation_euler = (math.radians(55), math.radians(10), math.radians(-35))
    sc.collection.objects.link(so)

    def area(name, loc, rot, size, e, col=(1, 0.96, 0.9)):
        d = bpy.data.lights.new(name, 'AREA'); d.energy = e * day; d.size = size[0]; d.size_y = size[1]; d.shape = 'RECTANGLE'; d.color = col
        o = bpy.data.objects.new(name, d); o.location = loc; o.rotation_euler = [math.radians(a) for a in rot]
        sc.collection.objects.link(o)
    for x in (-2.9, 2.9):
        area('wf', (x, -3.55, 2.05), (90, 0, 0), (1.0, 1.25), 450)
    for x in (-2.2, 2.2):
        area('wb', (x, 3.55, 2.05), (-90, 0, 0), (1.0, 1.25), 450)
    for y in (-0.9, 1.6):
        area('wr', (4.55, y, 2.1), (0, 90, 0), (0.9, 1.2), 380)
    for (x, y) in ((-2.5, 0), (0.5, 0)):
        d = bpy.data.lights.new('fill', 'POINT'); d.energy = 260; d.shadow_soft_size = 0.5; d.color = (1, 0.86, 0.66)
        o = bpy.data.objects.new('fill', d); o.location = (x, y, 2.8); sc.collection.objects.link(o)
    # fire glow
    d = bpy.data.lights.new('fire', 'POINT'); d.energy = 90; d.shadow_soft_size = 0.2; d.color = (1, 0.45, 0.15)
    o = bpy.data.objects.new('fire', d); o.location = (-3.9, 0, 0.8); sc.collection.objects.link(o)
    for (x, y, z, e) in extra_points:
        d = bpy.data.lights.new('lp', 'POINT'); d.energy = e; d.shadow_soft_size = 0.04; d.color = (1, 0.68, 0.38)
        o = bpy.data.objects.new('lp', d); o.location = (x, y, z); sc.collection.objects.link(o)


def render(path, cam_loc, target, lens=24, res=(960, 640), samples=32, exposure=0.5):
    sc = bpy.context.scene
    if sc.camera is None:
        cam = bpy.data.cameras.new('cam'); cam.lens = lens; cam.clip_start = 0.03
        co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co)
        sc.camera = co
    co = sc.camera
    co.data.lens = lens
    co.location = cam_loc
    d = Vector(target) - Vector(cam_loc)
    co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.device = 'CPU'
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 5
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.03
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = path; sc.render.image_settings.file_format = 'PNG'
    sc.view_settings.exposure = exposure
    names = [x.identifier for x in sc.view_settings.bl_rna.properties['view_transform'].enum_items]
    sc.view_settings.view_transform = 'AgX' if 'AgX' in names else 'Filmic'
    bpy.ops.render.render(write_still=True)
