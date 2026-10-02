import sys
sys.path.insert(0, '/shared/river/assets/blender')
from animlib import *

PREVIEW = os.environ.get('PREVIEW', '1') == '1'
reset_scene()
fur = vcol_mat('fox_fur', '#ffffff', rough=0.92)
eyem = make_mat('eye', '#b07a12', rough=0.05)
pupilm = make_mat('pupil', '#000000', rough=0.1)
nosem = make_mat('nose_wet', '#0c0a09', rough=0.15)
whisk = make_mat('whisker', '#ece6da', rough=0.5)
clawm = make_mat('claw', '#2a2521', rough=0.5)

ORANGE = '#d4732d'; ORANGE2 = '#b5531e'; WHITE = '#f1ebe0'; BLACK = '#1c1714'


def coat(p, n):
    belly = max(0.0, -n.z * 1.3 - 0.2) + max(0, (0.22 - p.z) * 3)
    c = mixc(ORANGE, ORANGE2, 0.4 * (fbm(p, 7, 2, 1) * .5 + .5) + max(0, n.z - 0.6) * (1 - min(1, abs(p.x) / 0.06)) * 0.5)
    # white chest/throat: front underside
    wt = max(0.0, -n.z * 1.2 + 0.1) * max(0, 1 - max(0, abs(p.x) - 0.03) * 30) * max(0, min(1, (p.y + 0.05) * -8))
    c = mixc(c, WHITE, min(1, wt * 1.2 + (0.0)))
    c = mixc(c, '#e9ddc8', min(1, belly * 0.8))
    # black socks
    if p.z < 0.2:
        c = mixc(c, BLACK, min(1, (0.2 - p.z) * 20))
    # guard hair streaks
    k = 0.85 + 0.15 * (fbm(V(p.x * 4, p.y * 0.7, p.z * 4), 30, 2, 8) * .5 + .5) + 0.12 * (fbm(p, 100, 2, 2) * .5 + .5)
    return mulc(c, k)


# ---- body
ys = [-0.27, -0.20, -0.08, 0.06, 0.18, 0.28, 0.34]
zc = [0.305, 0.300, 0.295, 0.297, 0.305, 0.31, 0.31]
rx = [0.045, 0.072, 0.078, 0.072, 0.078, 0.06, 0.03]
rz = [0.070, 0.105, 0.105, 0.095, 0.095, 0.08, 0.04]
bm = loft([V(0, y, z) for y, z in zip(ys, zc)], rx, rz, segs=30, res=4)
bl = [bm]
for sx in (1, -1):
    bl.append(blob((sx * 0.055, 0.2, 0.29), (0.05, 0.1, 0.11)))
    bl.append(blob((sx * 0.048, -0.17, 0.29), (0.04, 0.085, 0.10)))
bm = fuse(merge(*bl), voxel=0.0075, smooth_iter=10)
body = part('body', bm, [fur], (0, 0, 0.30), colorfn=coat, noise=dict(amp=0.0015, freq=90, seed=1))

# ---- neck
nb = V(0, -0.215, 0.33)
nk = loft([V(0, -0.17, 0.31), V(0, -0.24, 0.35), V(0, -0.30, 0.40)], [0.05, 0.05, 0.04], [0.065, 0.06, 0.05], segs=22, res=5)
neck_ob = part('neck', nk, [fur], nb, parent=body, colorfn=lambda p, n: mixc(coat(p, n), WHITE, max(0, -n.z) * 0.8),
               noise=dict(amp=0.002, freq=70, seed=2))

# ---- head
P0 = V(0, -0.305, 0.425)
D = V(0, -0.94, -0.3).normalized(); U = V(0, -0.3, 0.94).normalized()


def hp(t, u=0.0, x=0.0):
    return P0 + D * t + U * u + V(x, 0, 0)


ts = [-0.04, 0.02, 0.07, 0.12, 0.16, 0.185]
hrx = [0.042, 0.046, 0.04, 0.027, 0.0185, 0.0145]
hrz = [0.046, 0.05, 0.043, 0.030, 0.022, 0.0175]
ups = [0, 0, -0.002, -0.006, -0.008, -0.009]
hb = [loft([hp(t, u) for t, u in zip(ts, ups)], hrx, hrz, segs=22, res=6)]
for sx in (1, -1):
    hb.append(blob(hp(0.045, -0.018, sx * 0.038), (0.022, 0.03, 0.028)))   # cheek ruff
    hb.append(blob(hp(0.075, 0.022, sx * 0.028), (0.012, 0.028, 0.008), rot=(-0.3, 0, 0)))  # brow
hb = fuse(merge(*hb), voxel=0.0042, smooth_iter=6, smooth_f=0.5)
ex = []
nose = blob(hp(0.186, -0.0075), (0.0125, 0.008, 0.0095), rot=(0.3, 0, 0)); set_mat_index(nose, 2); ex.append(nose)
for sx in (1, -1):
    ec = hp(0.088, 0.013, sx * 0.0285)
    eb = blob(ec, (0.0075, 0.0105, 0.0085)); set_mat_index(eb, 1); ex.append(eb)
    pb = blob(ec + V(sx * 0.0058, -0.005, 0.0), (0.0018, 0.0088, 0.0024), segs=8, rings=6); set_mat_index(pb, 3); ex.append(pb)   # vertical slit pupil
    pb.transform(Matrix.Identity(4)) if False else None
    for k in range(5):
        a = (k - 2) * 0.16
        s0 = hp(0.15, -0.01 + (k - 2) * 0.0015, sx * 0.012)
        d = V(sx * 0.55, -0.6 + 0.0, (k - 2) * 0.1).normalized()
        w = loft([s0, s0 + d * 0.03 + V(0, 0, 0.003), s0 + d * 0.065 + V(0, 0, -0.006)], [0.0004, 0.0003, 0.0001], segs=4, res=2, cap_push=1)
        set_mat_index(w, 4); ex.append(w)
hb = merge(hb, *ex)


def hcol(p, n):
    t = (p - P0).dot(D)
    u = (p - P0).dot(U)
    c = mixc(ORANGE, ORANGE2, 0.3)
    c = mixc(c, WHITE, max(0, min(1, (-0.012 - u) * 90)) * 0.95)                  # white lower lip/cheek
    c = mixc(c, WHITE, max(0, abs(p.x) - 0.025) * 30 * max(0, min(1, (t - 0.02) * 15)) * (1 if u < 0.005 else 0))
    c = mixc(c, BLACK, max(0, min(1, (t - 0.15) * 40)) * 0.6)                      # dark muzzle tip
    # dark whisker-spot band above lip
    c = mixc(c, BLACK, max(0, 1 - abs(u + 0.004) / 0.008) * max(0, min(1, (t - 0.09) * 20)) * max(0, min(1, (0.17 - t) * 40)) * 0.6)
    # dark eye liner
    e = hp(0.088, 0.013, 0.0285 * (1 if p.x > 0 else -1))
    c = mixc(c, BLACK, max(0, 1 - (p - e).length / 0.022) * 0.7)
    return mulc(c, 0.92 + 0.15 * (fbm(p, 120, 2, 3) * .5 + .5))


head = part('head', hb, [fur, eyem, nosem, pupilm, whisk], P0, parent=neck_ob, colorfn=hcol, noise=dict(amp=0.0007, freq=140, seed=4))

JH = hp(0.05, -0.027)
jb = loft([JH + D * t for t in (-0.005, 0.03, 0.08, 0.125)], [0.022, 0.0215, 0.015, 0.0095], [0.014, 0.014, 0.0105, 0.008], segs=12, res=4)
jaw = part('jaw', jb, [fur], JH, parent=head, colorfn=lambda p, n: mixc(WHITE, '#d8cdb8', 0.2))

ears = []
for sx, nm in ((1, 'ear_l'), (-1, 'ear_r')):
    base = hp(0.0, 0.040, sx * 0.027)
    tip = base + V(sx * 0.02, 0.012, 0.098)
    nrm = V(sx * 0.55, -0.8, 0.25)
    e = leaf_shape(base, tip, 0.030, 0.0035, bulge=0.1, segs=12, curve=(0, 0, 0), res=4, up=nrm)
    ears.append(part(nm, e, [fur], base, parent=head,
                     colorfn=lambda p, n, nrm=nrm: mixc('#e7d8c0', ORANGE2, 0.0) if n.dot(nrm) > 0 and ((p - base).length < 0.075) and abs((p - base).x) < 0.012 else BLACK if n.dot(nrm) < 0 else mixc('#d8c8b0', BLACK, max(0, ((p - base).length - 0.05) * 30)),
                     noise=dict(amp=0.0008, freq=100, seed=7)))

# ---- tail
tr = V(0, 0.325, 0.325)
tpts = [tr, V(0, 0.40, 0.32), V(0, 0.51, 0.27), V(0, 0.63, 0.20), V(0, 0.74, 0.135)]
tb = loft(tpts, [0.028, 0.048, 0.06, 0.05, 0.012], [0.028, 0.048, 0.06, 0.05, 0.012], segs=22, res=6, cap_push=1.2)
tb = fuse(tb, voxel=0.0065, smooth_iter=4)


def tcol(p, n):
    t = (p.y - tr.y) / 0.42
    c = mixc(ORANGE, ORANGE2, 0.4 + 0.5 * max(0, n.z))
    c = mixc(c, '#e8d7be', max(0, -n.z) * 0.4)
    c = mixc(c, '#3a2a22', max(0, min(1, (t - 0.45) * 3)) * 0.25 * (fbm(p, 40, 2, 6) * .5 + .5))
    c = mixc(c, WHITE, max(0, min(1, (t - 0.72) * 14)))
    return mulc(c, 0.9 + 0.2 * (fbm(V(p.x * 4, p.y * .5, p.z * 4), 40, 2, 9) * .5 + .5))


tail = part('tail', tb, [fur], tr, parent=body, colorfn=tcol, noise=dict(amp=0.004, freq=60, seed=5))

# ---- legs
legs = []


def lg(name, pts, rx_, rz_, pivot, parent, col=coat, up=(0, -1, 0), extra=None):
    b = loft(pts, rx_, rz_, segs=14, res=5, up=up)
    if extra is not None:
        b = merge(b, extra)
    return part(name, b, [fur], pivot, parent=parent, colorfn=col, noise=dict(amp=0.0012, freq=90, seed=3))


for sx, s in ((1, 'l'), (-1, 'r')):
    m = lambda x, y, z: V(sx * x, y, z)
    # fore
    sh = m(0.05, -0.17, 0.30); ca = m(0.048, -0.185, 0.14); fe = m(0.046, -0.185, 0.04); pw = m(0.046, -0.215, 0.012)
    fu = lg('leg_f%s_upper' % s, [sh, (sh + ca) / 2, ca], [0.038, 0.027, 0.0155], [0.05, 0.03, 0.019], sh, body)
    fl = lg('leg_f%s_lower' % s, [ca, (ca + fe) / 2, fe], [0.0155, 0.0115, 0.012], [0.019, 0.013, 0.014], ca, fu)
    pb = loft([fe + V(0, 0, 0.012), (fe + pw) / 2 + V(0, -0.002, 0.0), pw], [0.013, 0.0145, 0.011], [0.015, 0.0165, 0.012], segs=12, res=4, up=(0, 0, 1))
    pb = merge(pb, *[blob(pw + V(dx * 0.007, -0.0, 0.0), (0.0055, 0.014, 0.008), segs=8, rings=6) for dx in (-1, 0, 1)])
    pa = part('leg_f%s_paw' % s, pb, [fur], fe, parent=fl, colorfn=lambda p, n: mixc(BLACK, '#3a3029', 0.3))
    # hind: thigh (hip->hock via stifle), lower (hock->fetlock), paw
    hip = m(0.05, 0.20, 0.31); st = m(0.055, 0.16, 0.20); hk = m(0.05, 0.255, 0.125); fe2 = m(0.048, 0.245, 0.04); pw2 = m(0.048, 0.215, 0.012)
    hu = lg('leg_h%s_thigh' % s, [hip, st, hk], [0.055, 0.04, 0.018], [0.08, 0.055, 0.022], hip, body)
    hl = lg('leg_h%s_lower' % s, [hk, (hk + fe2) / 2, fe2], [0.016, 0.0115, 0.012], [0.02, 0.014, 0.014], hk, hu)
    pb2 = loft([fe2 + V(0, 0, 0.012), (fe2 + pw2) / 2, pw2], [0.013, 0.0145, 0.011], [0.015, 0.0165, 0.012], segs=12, res=4, up=(0, 0, 1))
    pb2 = merge(pb2, *[blob(pw2 + V(dx * 0.007, 0, 0), (0.0055, 0.014, 0.008), segs=8, rings=6) for dx in (-1, 0, 1)])
    ha = part('leg_h%s_paw' % s, pb2, [fur], fe2, parent=hl, colorfn=lambda p, n: mixc(BLACK, '#3a3029', 0.3))
    legs += [fu, fl, pa, hu, hl, ha]

allparts = [body, neck_ob, head, jaw] + ears + [tail] + legs
meta = {
    'species': 'red fox (Vulpes vulpes)', 'forward': '-Y', 'left_is': '+X',
    'scale_hint_m': {'shoulder_height': 0.40, 'body_length': 0.68, 'tail_length': 0.42, 'total_length': 1.05},
    'parts': {'root': 'body', 'neck': 'neck', 'head': 'head', 'jaw': 'jaw', 'ears': ['ear_l', 'ear_r'], 'tail': 'tail'},
    'hierarchy': {'body': ['neck', 'tail', 'leg_f*_upper', 'leg_h*_thigh'], 'neck': ['head'], 'head': ['jaw', 'ear_l', 'ear_r'],
                  'leg_f*_upper': ['leg_f*_lower'], 'leg_f*_lower': ['leg_f*_paw'], 'leg_h*_thigh': ['leg_h*_lower'], 'leg_h*_lower': ['leg_h*_paw']},
    'gait': {'walk_cycle_s': 0.9, 'trot_cycle_s': 0.5, 'legs': {k: ['upper/thigh', 'lower', 'paw'] for k in ('leg_fl', 'leg_fr', 'leg_hl', 'leg_hr')},
             'trot_pairs': [['leg_fl', 'leg_hr'], ['leg_fr', 'leg_hl']], 'walk_phase': {'leg_hl': 0.0, 'leg_fl': 0.25, 'leg_hr': 0.5, 'leg_fr': 0.75},
             'swing_deg': {'upper': [-30, 30], 'lower': [0, 50], 'paw': [-20, 20]}, 'axis': 'X'},
    'spine': {'body_bob_m': 0.015, 'tail_sway_deg': 10, 'tail_follow': 'tail rot_z lags body yaw'},
    'idle': {'head_sniff_deg': 6, 'ear_swivel_deg': 15, 'tail_sway_deg': 6},
    'pose_hints': {'sniff_ground': {'neck_rot_x_deg': 35, 'head_rot_x_deg': 20}, 'pounce': {'body_pitch_deg': 15, 'neck_rot_x_deg': 40}},
}
print(export_bundle(OUT_DIR + '/fox.json', allparts, meta))
write_meta('fox', meta)
print('tris', tri_count(allparts))
if PREVIEW:
    preview_grid(PREVIEW_DIR + '/fox.png', [((1.6, 0.1, 0.5), (0, 0.1, 0.3), 50), ((1.0, -1.3, 0.7), (0, 0.1, 0.28), 50),
                                            ((0.35, -0.75, 0.55), (0, -0.3, 0.42), 65), ((-1.2, 1.4, 0.7), (0, 0.1, 0.28), 50)], target=(0, 0, 0.3))
