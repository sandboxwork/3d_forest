"""Cycles preview: 3x3 tiled plane with albedo+normal+roughness through Principled BSDF.  blender -b --python tx_preview.py -- name [name...]"""
import bpy, sys, os, math
T = '/shared/river/assets/tex'; P = '/shared/river/assets/preview'
METAL = {'pbr_iron': 1.0, 'pbr_brass_copper': 1.0}
GLASS = {'pbr_glass_dirty'}
names = sys.argv[sys.argv.index('--') + 1:]
for name in names:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 20
    sc.cycles.use_denoising = False
    sc.render.resolution_x = 640; sc.render.resolution_y = 400
    sc.view_settings.view_transform = 'Standard'
    bpy.ops.mesh.primitive_plane_add(size=3)
    pl = bpy.context.object
    m = bpy.data.materials.new('m'); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); bs = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(bs.outputs[0], out.inputs[0])
    uv = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (3, 3, 3)
    nt.links.new(uv.outputs['UV'], mp.inputs[0])
    def img(suffix, cs):
        n = nt.nodes.new('ShaderNodeTexImage')
        n.image = bpy.data.images.load(f'{T}/{name}{suffix}.jpg'); n.image.colorspace_settings.name = cs
        n.extension = 'REPEAT'; n.interpolation = 'Linear'
        nt.links.new(mp.outputs[0], n.inputs[0]); return n
    a = img('', 'sRGB'); nn = img('_n', 'Non-Color'); rr = img('_r', 'Non-Color')
    nt.links.new(a.outputs[0], bs.inputs['Base Color'])
    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 1.0
    nt.links.new(nn.outputs[0], nm.inputs['Color']); nt.links.new(nm.outputs[0], bs.inputs['Normal'])
    sp = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(rr.outputs[0], sp.inputs[0])
    nt.links.new(sp.outputs[1], bs.inputs['Roughness'])
    bs.inputs['Metallic'].default_value = METAL.get(name, 0.0)
    pl.data.materials.append(m)
    cam = bpy.data.objects.new('c', bpy.data.cameras.new('c')); sc.collection.objects.link(cam); sc.camera = cam
    cam.location = (0, -2.6, 2.3); cam.rotation_euler = (math.radians(48), 0, 0); cam.data.lens = 30
    sun = bpy.data.objects.new('s', bpy.data.lights.new('s', 'SUN')); sc.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(62), 0, math.radians(35)); sun.data.energy = 3.0
    w = bpy.data.worlds.new('w'); w.use_nodes = True; sc.world = w
    w.node_tree.nodes['Background'].inputs[0].default_value = (0.75, 0.8, 0.9, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.8
    sc.render.filepath = f'{P}/tx_{name}.png'; sc.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)
    print('PREVIEW', name)
