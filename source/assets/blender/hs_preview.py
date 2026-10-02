import sys, os, math
sys.path.insert(0, '/shared/river/assets/blender')
from bl_common import *
bpy.ops.wm.open_mainfile(filepath=os.environ.get('HS_BLEND', '/shared/river/assets/blender/house_shell.blend'))
sc = bpy.context.scene
for m in bpy.data.materials:
    if not m.use_nodes: continue
    nt = m.node_tree
    b = nt.nodes.get('Principled BSDF')
    if not b: continue
    if m.name == 'glass':
        b.inputs['Alpha'].default_value = 0.25
        continue
    ca = nt.nodes.new('ShaderNodeVertexColor'); ca.layer_name = 'Col'
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = 1.0
    mix.inputs[6].default_value = tuple(m['rgb']) + (1,)
    nt.links.new(ca.outputs['Color'], mix.inputs[7])
    nt.links.new(mix.outputs[2], b.inputs['Base Color'])
mode = os.environ.get('HS_VIEWS', 'ext')
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.55, 0.68, 0.85, 1); bg.inputs[1].default_value = 1.0
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 4.0
so = bpy.data.objects.new('sun', sun); so.rotation_euler = (math.radians(55), 0, math.radians(-30)); sc.collection.objects.link(so)
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
g = bpy.context.object; g.data.materials.append(make_mat('_gm', '#62763f', rough=0.95))
bpy.data.materials['_gm'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.12, 0.2, 0.05, 1)
if mode.startswith('int'):
    for loc, e in (((-1.5, 0, 2.7), 250), ((3.0, 0, 2.7), 120)):
        l = bpy.data.lights.new('pl', 'POINT'); l.energy = e; l.shadow_soft_size = 0.3
        lo = bpy.data.objects.new('pl', l); lo.location = loc; sc.collection.objects.link(lo)
VIEWS = {
 'front': ((0, -14, 1.7), (0, 0, 2.6), 35),
 'front34': ((-10, -10, 1.7), (0, 0, 2.6), 35),
 'back34': ((9, 10, 1.7), (-0.5, 0, 2.4), 35),
 'side': ((14, 0.5, 1.7), (0, 0, 2.6), 35),
 'left34': ((-11, 7, 2.0), (-2, 0, 3.0), 35),
 'top': ((-9, -12, 14), (0, 0, 2.5), 35),
 'porch': ((-3.2, -9.3, 1.7), (0, -4.2, 1.6), 28),
 'fire': ((0.8, 0.3, 1.6), (-4.25, 0.0, 1.3), 24),
 'tofront': ((-1.0, 2.6, 1.6), (0, -3.5, 1.4), 22),
 'tobed': ((-3.3, -2.8, 1.6), (1.6, -0.4, 1.2), 22),
 'bed': ((4.0, 2.9, 1.7), (1.5, -1.5, 1.2), 22),
 'ceil': ((-3.8, 2.8, 1.5), (1.0, -1.0, 3.0), 24),
 'back': ((0, 12, 1.7), (0, 4, 1.2), 35),
 'wood': ((2.5, 7.8, 1.7), (0, 4.2, 1.0), 35),
 'door': ((0.4, -6.2, 1.6), (0, -3.5, 1.5), 28),
 'win': ((-2.0, -6.0, 1.7), (-2.9, -3.5, 2.0), 35),
 'garden': ((9.5, -4, 1.7), (5.4, 0.2, 0.3), 35),
}
for nme in os.environ.get('HS_NAMES', 'front').split(','):
    if ':' in nme:
        nme, spec = nme.split(':')
        v = [float(t) for t in spec.split('_')]
        cl, tg, ln = tuple(v[0:3]), tuple(v[3:6]), v[6]
    else:
        cl, tg, ln = VIEWS[nme]
    cam = bpy.data.cameras.new('cam'); cam.lens = ln; cam.clip_end = 200
    co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co)
    co.location = cl
    co.rotation_euler = (Vector(tg) - Vector(cl)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = co
    sc.render.engine = 'CYCLES'; sc.cycles.samples = int(os.environ.get('HS_SAMPLES', 24)); sc.cycles.device = 'CPU'
    try: sc.cycles.use_denoising = True
    except Exception: pass
    sc.render.resolution_x, sc.render.resolution_y = (int(os.environ.get('HS_W', 960)), int(os.environ.get('HS_H', 640)))
    sc.render.filepath = '/shared/river/assets/preview/hs_%s.png' % nme
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(co)
