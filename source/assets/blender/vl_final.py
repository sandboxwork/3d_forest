"""Build one villager, pose-test it, export bundle + meta.   VL=<name> blender -b --python vl_final.py
env: SKIP_PREVIEW=1 to skip renders; SKIP_POSE=1 to skip pose test."""
import sys, os, json
sys.path.insert(0, '/shared/river/assets/blender')
from vl_arch import *

name = os.environ.get('VL', 'man')
cfg = ARCH[name]
c, objs = build(cfg, cfg['garments'])
body_names = [n for n in PARTS]
prop_names = [n for n in objs if n.startswith('tool_') or n == 'cane']
allobjs = [objs[n] for n in PARTS + prop_names]
ntri = tri_count(allobjs)
per = {k: tri_count([o]) for k, o in objs.items()}
print('TRIS', name, ntri, per)

WALK = cfg.get('walk', dict(hip_swing_deg=28, knee_bend_deg=42, arm_swing_deg=24, stride_m=0.72, cycle_s=1.05))
zmax = max((o.matrix_world @ v.co).z for n, o in objs.items() if n in PARTS for v in o.data.vertices)
Hh = c.H
sit = dict(seat_height_m=round(c.z['knee'] - 0.08, 3), pelvis_drop_m=round(c.z['hip'] - c.z['knee'], 3), pelvis_back_m=0.03,
           leg_upper_rot_x_deg=-90, leg_lower_rot_x_deg=90, foot_rot_x_deg=0, torso_rot_x_deg=-5,
           arm_upper_rot_x_deg=-25, arm_lower_rot_x_deg=-60, note='sitting: pelvis goes DOWN by pelvis_drop_m (hip centre ends at knee height, thighs horizontal) and BACK by pelvis_back_m (+Y blender = -Z three); thighs forward = NEGATIVE x-rotation, shins +x; seat surface at seat_height_m')


def v3(v):  # blender -> three
    return [round(v.x, 4), round(v.z, 4), round(-v.y, 4)]


hier = {}
for _n, _o in objs.items():
    if _o.parent is not None:
        hier.setdefault(_o.parent.name, []).append(_n)
meta = dict(forward='-Y blender (+Z three.js)', left_is='+X blender (+X three.js)', root='pelvis', hierarchy=hier, name='villager_' + name, role_ko=cfg['label'], height_m=cfg['H'], height_with_headwear_m=round(zmax, 3), shoulder_height=round(c.z['sh'], 3),
            head_center_height=round(c.head_c.z, 3), eye_height=round(c.head_c.z + c.F['eye_z'] * c.hs, 3),
            units='m', up='Y (three.js, exported)', front='+Z (three.js)', left_side='+X',
            pivots={n: v3(c.piv[n]) for n in c.piv}, parents={n: (objs[n].parent.name if objs[n].parent else None) for n in objs},
            rotation_convention='all parts rotate about their own pivot (origin). Rotation about +X axis (same sign in Blender and three.js): NEGATIVE angle swings a hanging limb FORWARD (+Z three / -Y blender), positive swings it BACKWARD. Knee: positive x bends the shin backward (correct); elbow: negative x bends the forearm forward (correct). Parts whose mass is ABOVE the pivot (torso, neck_head) lean/nod FORWARD with POSITIVE x. Jaw: positive x opens the mouth. Foot: positive x points the toes DOWN.',
            walk=WALK, walk_signs=dict(leg_upper_forward='-x', knee_flex='+x (lower leg)', arm_upper_forward='-x', elbow_flex='-x (lower arm)', jaw_open='+x', foot_toe_up='-x', foot_toe_down='+x', torso_lean_forward='+x', head_nod_down='+x', torso_twist='+/-z', arm_abduct_three_js='left arm outward = +rotation.z, right arm outward = -rotation.z (derived by math, not rendered)'),
            jaw_open_max_deg=10, sit=sit,
            materials_recolorable=['skin', 'hair', 'cloth_main', 'cloth_alt', 'cloth_accent', 'shoes'], eye_materials=['eye_white', 'iris', 'pupil'],
            props=prop_names, prop_note=('hand-held prop parts (' + ', '.join(prop_names) + ') are parented to the grip hand with pivot at the grip; keep that arm (shoulder swing, elbow) near its rest pose while carrying; hide/show the prop part freely.' if prop_names else ''), triangles=ntri, tris_per_part=per,
            clothing_note=cfg.get('note', ''))
if cfg.get('skirt'):
    meta['walk_note'] = 'skirt is rigid on the pelvis: keep hip swing small to avoid legs poking through'

if os.environ.get('SKIP_PREVIEW') != '1':
    preview(c, objs, '/shared/river/assets/preview/vl_%s.png' % name, name)
    for _o in list(bpy.data.objects):
        if _o.type in ('LIGHT', 'CAMERA') or _o.name.startswith('_ground') or _o.name.startswith('Plane'):
            bpy.data.objects.remove(_o)

# ---------------------------------------------------------------- pose tests
def rx(o, deg):
    o.rotation_euler = (math.radians(deg), 0, 0)


ORIG_LOC = {n: o.location.copy() for n, o in objs.items()}


def reset_pose():
    for n, o in objs.items():
        o.rotation_euler = (0, 0, 0)
        o.location = ORIG_LOC[n]


def pose_walk(sgn):
    reset_pose()
    h, k, a = WALK['hip_swing_deg'], WALK['knee_bend_deg'], WALK['arm_swing_deg']
    L, R = ('l', 'r') if sgn > 0 else ('r', 'l')
    rx(objs['leg_%s_upper' % L], -h); rx(objs['leg_%s_lower' % L], 8); rx(objs['foot_%s' % L], 8)
    rx(objs['leg_%s_upper' % R], h * 0.7); rx(objs['leg_%s_lower' % R], k); rx(objs['foot_%s' % R], 20)
    rx(objs['arm_%s_upper' % L], a); rx(objs['arm_%s_lower' % L], -10)
    rx(objs['arm_%s_upper' % R], -a); rx(objs['arm_%s_lower' % R], -35)
    objs['torso'].rotation_euler = (0, 0, math.radians(3 * sgn))


def pose_sit():
    reset_pose()
    p0 = ORIG_LOC['pelvis']
    objs['pelvis'].location = (p0.x, p0.y + 0.03, p0.z - sit['pelvis_drop_m'])
    for t in 'lr':
        rx(objs['leg_%s_upper' % t], -90); rx(objs['leg_%s_lower' % t], 90)
    rx(objs['torso'], -5)
    for t in 'lr':
        rx(objs['arm_%s_upper' % t], -25); rx(objs['arm_%s_lower' % t], -60)
    return p0


def pose_talk():
    reset_pose()
    rx(objs['jaw'], 12)


if os.environ.get('SKIP_POSE') != '1':
    d = Hh * 1.7
    mid = Hh * 0.5
    side_cam = ((d, 0, mid), (0, 0, mid), 50)
    front_cam = ((0, -d, mid), (0, 0, mid), 50)
    # stage the renders in separate passes using one scene: render each pose, tile
    tiles = []
    sc = bpy.context.scene
    imgs = []
    def snap(tag, cam):
        w = bpy.data.worlds.new('W'); sc.world = w
    # use vl_grid on pre-set poses by rendering sequentially with custom loop
    import numpy as _np
    res = (440, 520)
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    bgn = w.node_tree.nodes['Background']; bgn.inputs[0].default_value = (0.62, 0.7, 0.82, 1); bgn.inputs[1].default_value = 0.9
    sd = bpy.data.lights.new('sun', 'SUN'); sd.energy = 3.2
    so = bpy.data.objects.new('sun', sd); so.rotation_euler = (math.radians(55), 0, math.radians(-30)); sc.collection.objects.link(so)
    sd2 = bpy.data.lights.new('fill', 'SUN'); sd2.energy = 1.0
    so2 = bpy.data.objects.new('fill', sd2); so2.rotation_euler = (math.radians(70), 0, math.radians(140)); sc.collection.objects.link(so2)
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    g = bpy.context.object; g.data.materials.append(make_mat('_groundmat', '#6b7a45', rough=0.95))
    cam = bpy.data.cameras.new('cam'); co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
    sc.render.engine = 'CYCLES'; sc.cycles.samples = 20; sc.cycles.device = 'CPU'; sc.cycles.use_denoising = False
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.image_settings.file_format = 'PNG'
    shots = [('walkA', lambda: pose_walk(1), side_cam), ('walkB', lambda: pose_walk(-1), side_cam), ('walkA_front', lambda: pose_walk(1), front_cam),
             ('sit', lambda: pose_sit(), side_cam), ('talk', lambda: pose_talk(), ((c.head_c.x + 0.55, c.head_c.y - 0.45, c.head_c.z), (c.head_c.x, c.head_c.y, c.head_c.z), 85))]
    tiles = []
    for i, (tag, fn, (loc, tg, ln)) in enumerate(shots):
        fn()
        bpy.context.view_layer.update()
        cam.lens = ln; co.location = loc
        co.rotation_euler = (V(tg) - V(loc)).to_track_quat('-Z', 'Y').to_euler()
        fp = '%s/_vlp_%s_%d.png' % (TMP, name, i)
        sc.render.filepath = fp
        bpy.ops.render.render(write_still=True)
        im = bpy.data.images.load(fp)
        a = _np.array(im.pixels[:], dtype=_np.float32).reshape(res[1], res[0], 4)
        tiles.append(a); bpy.data.images.remove(im)
    reset_pose()
    cols = 3; rows = 2
    Hh_, Ww_ = res[1], res[0]
    canvas = _np.ones((rows * Hh_, cols * Ww_, 4), dtype=_np.float32)
    for i, t in enumerate(tiles):
        r, cc = divmod(i, cols)
        canvas[(rows - 1 - r) * Hh_:(rows - r) * Hh_, cc * Ww_:(cc + 1) * Ww_] = t
    im = bpy.data.images.new('grid', cols * Ww_, rows * Hh_)
    im.pixels = canvas.ravel().tolist()
    im.filepath_raw = '/shared/river/assets/preview/vl_%s_pose.png' % name; im.file_format = 'PNG'; im.save()

# ---------------------------------------------------------------- export
reset_pose()
bpy.context.view_layer.update()
out = '/shared/river/assets/out/villager_%s.json' % name
st = export_bundle(out, allobjs, meta=meta)
print('EXPORT', st)
meta['file_kb'] = st['kb']
with open('/shared/river/assets/out/villager_%s.meta.json' % name, 'w') as f:
    json.dump(meta, f, indent=1, ensure_ascii=False)
