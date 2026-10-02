import sys, os
sys.path.insert(0, '/shared/river/assets/blender')
from vp_birds import *
KIND = 'rooster'
ROOS = KIND == 'rooster'
name = 'animal_rooster' if ROOS else 'animal_chicken'
objs, K = build(KIND)
allp = list(objs.values())
def _ext():
    zs=[(o.matrix_world@v.co) for o in allp for v in o.data.vertices]
    return max(v.z for v in zs), min(v.y for v in zs), max(v.y for v in zs), max(abs(v.x) for v in zs)
ZT, Y0, Y1, XM = _ext()
print('EXT', ZT, Y0, Y1, XM)
meta = {
 'species': 'domestic rooster (Gallus gallus domesticus), copper/chestnut' if ROOS else 'domestic hen (Gallus gallus domesticus), brown speckled',
 'forward': '-Y blender (+Z three.js), beak toward -Y', 'left': '+X',
 'origin': 'on the ground, centred under the body; all part origins are joint pivots',
 'scale_hint_m': {'max_height_m': round(ZT, 3), 'length_beak_to_tail_m': round(Y1 - Y0, 3), 'half_width_m': round(XM, 3)},
 'parts': {'root': 'body', 'head': 'head (includes neck, comb, wattles, upper beak, eyes; pivot = neck base)', 'beak_lower': 'beak_lower',
           'tail': 'tail', 'wings': ['wing_l', 'wing_r'], 'legs': {'leg_l': 'foot_l', 'leg_r': 'foot_r'}},
 'hierarchy': {'body': ['head', 'tail', 'wing_l', 'wing_r', 'leg_l', 'leg_r'], 'head': ['beak_lower'], 'leg_l': ['foot_l'], 'leg_r': ['foot_r']},
 'rest_pose': 'standing, wings folded on flanks (authored in geometry), feet on z=0',
 'gait': {'walk_cycle_s': 0.55, 'run_cycle_s': 0.3,
          'phase_offsets': {'leg_l': 0.0, 'leg_r': 0.5},
          'rotation_axis': 'X (positive X rotation about hip swings the foot backward (+Y)); head pivot: positive X pitches the beak downward',
          'swing_deg': {'leg': [-30, 30], 'foot': [-25, 20]},
          'head_bob': 'while walking: head translates/rotates about X +-6 deg in sync, phase locked to leg cycle (forward on stride)',
          'note': 'legs are two-part (leg_* hip, foot_* ankle). Lift foot: foot X rot +20 during back-swing, -25 at forward-swing.'},
 'idle': {'head_bob_deg': 5, 'tail_flick_deg': 6, 'breath': 'scale body Y 1.0..1.01 at 0.4 Hz', 'beak_open_deg': [0, 12]},
 'peck_pose': {'head_rot_x_deg': 62, 'body_rot_x_deg': 18, 'cycle_s': 0.5, 'beak_lower_rot_x_deg': [0, 14]},
 'wing_pose': {'open_euler_xyz_deg_blender': {'wing_l': [0, -90, -90], 'wing_r': [0, 90, 90]},
               'note': 'rotation euler XYZ (Blender) about the shoulder pivot; wings lie folded at rest (identity). Interpolate from identity; flap by oscillating the Y component.'},
}
meta['tris_note'] = 'see bundle'
print(export_bundle(OUT_DIR + '/%s.json' % name, allp, meta))
write_meta(name, meta)
for o in allp:
    print(o.name, tri_count([o]))
print('TOTAL', tri_count(allp))
d = 1.9 * K
tgt = (0, 0, 0.22 * K)
if os.environ.get('POSE') == 'open':
    objs['wing_l'].rotation_euler = (0, math.radians(-90), math.radians(-90)); objs['wing_r'].rotation_euler = (0, math.radians(90), math.radians(90))
    name += '_open'
preview_grid(PREVIEW_DIR + '/vp_%s.png' % name, [((d * .7, -d * .7, 0.45 * K), tgt), ((d, 0, 0.3 * K), tgt), ((0.42 * K, -0.55 * K, 0.50 * K), (0, -0.12 * K, 0.34 * K), 80), ((-d * .6, d * .7, 0.5 * K), tgt)], target=tgt, sun=3.5)
