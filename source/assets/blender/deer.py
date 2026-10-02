import sys
sys.path.insert(0, '/shared/river/assets/blender')
from animlib import *

KIND = os.environ.get('KIND', 'doe')   # doe | stag
PREVIEW = os.environ.get('PREVIEW', '1') == '1'
STAG = KIND == 'stag'
reset_scene()
random.seed(3)

S = 1.12 if STAG else 1.0   # stag is bigger
NK = 1.35 if STAG else 1.0  # neck thickness

# ---- materials
fur = vcol_mat('deer_fur', '#ffffff', rough=0.92)
hoofm = make_mat('hoof_horn', '#1b1612', rough=0.4)
eyem = make_mat('eye', '#1d0f07', rough=0.05, spec=0.9)
pupilm = make_mat('pupil', '#000000', rough=0.1)
nosem = make_mat('nose_wet', '#17110f', rough=0.18)
antm = vcol_mat('antler_bone', '#ffffff', rough=0.6)

TOP = '#b08559' if not STAG else '#95694a'
TOP2 = '#6b472b' if not STAG else '#4c3422'
BELLY = '#dcc9a6'
STRIPE = '#4d341f'
RUMP = '#ead8b2'
LEG = '#8d6f4f' if not STAG else '#5d4632'


def sc(v):  # scale about origin in xy and z
    return V((v[0] * S, v[1] * S, v[2] * S))


def coat(p, n):
    """Body coat colour from world position/normal."""
    belly = max(0.0, -n.z * 1.4 - 0.15) + max(0, (0.72 - p.z) * 2.5)
    c = mixc(TOP, BELLY, belly)
    # darker dorsal band
    dor = max(0.0, n.z - 0.55) * (1.0 - min(1.0, abs(p.x) / (0.14 * S)))
    c = mixc(c, STRIPE, dor * 0.6)
    # shoulder/haunch darker top variation
    c = mixc(c, TOP2, 0.18 * (fbm(p, 6, 3, 1) * 0.5 + 0.5))
    # rump patch
    if p.y > 0.66 * S and p.z < 0.93 * S:
        c = mixc(c, RUMP, min(1.0, (p.y - 0.66 * S) * 14) * (0.9 if n.z < 0.6 else 0.35))
    # legs lower: darker/greyer
    if p.z < 0.55 * S:
        c = mixc(c, LEG, min(1.0, (0.55 * S - p.z) * 5) * 0.8)
    if p.z < 0.12 * S:
        c = mixc(c, '#33281f', 0.6)
    # mottling / sheen
    k = 0.86 + 0.16 * (fbm(p, 40, 2, 2) * 0.5 + 0.5) + 0.14 * (fbm(V(p.x * 3.5, p.y * 0.7, p.z * 3.5), 30, 2, 8) * 0.5 + 0.5)
    if not STAG:
        # faint dapple
        sp = fbm(p, 55, 1, 4)
        if sp > 0.42 and n.z > 0.2:
            c = mixc(c, '#d8b98f', 0.18)
    return mulc(c, k)


# ================= BODY =================
ys = [-0.60, -0.44, -0.20, 0.05, 0.28, 0.48, 0.64, 0.75]
zc = [0.80, 0.80, 0.795, 0.80, 0.82, 0.835, 0.845, 0.845]
rxs = [0.09, 0.15, 0.17, 0.17, 0.165, 0.155, 0.115, 0.05]
rzs = [0.16, 0.25, 0.255, 0.245, 0.225, 0.205, 0.16, 0.08]
if STAG:
    rxs = [r * 1.08 for r in rxs]; rzs = [r * 1.06 for r in rzs]
pts = [sc((0, y, z)) for y, z in zip(ys, zc)]
body = loft(pts, [r * S for r in rxs], [r * S for r in rzs], segs=36, res=4)
blobs = [body]
for sx in (1, -1):
    blobs.append(blob(sc((sx * 0.10, 0.48, 0.80)), (0.090 * S, 0.21 * S, 0.245 * S), rot=(0, 0, sx * 0.05)))   # haunch
    blobs.append(blob(sc((sx * 0.11, -0.36, 0.77)), (0.075 * S, 0.17 * S, 0.21 * S)))                      # shoulder
    blobs.append(blob(sc((sx * 0.07, -0.33, 0.97)), (0.06 * S, 0.14 * S, 0.08 * S)))                         # withers
bodybm = merge(*blobs)
bodybm = fuse(bodybm, voxel=0.0155 * S, smooth_iter=10)
body_ob = part('body', bodybm, [fur], (0, 0.0, 0.80 * S), colorfn=coat, noise=dict(amp=0.0025, freq=35, seed=1))
# ground origin: body pivot is at centre of mass slightly above ground. keep parts hierarchy rooted at body.

# ================= NECK =================
nb = sc((0, -0.47, 0.94))
np_pts = [sc((0, -0.42, 0.90)), sc((0, -0.49, 0.96)), sc((0, -0.62, 1.15)), sc((0, -0.74, 1.30))]
neck = loft(np_pts, [0.10 * S * NK, 0.145 * S * NK, 0.098 * S * NK, 0.066 * S * NK],
            [0.11 * S * NK, 0.17 * S * NK, 0.122 * S * NK, 0.082 * S * NK], segs=28, res=6)
if STAG:
    # mane ruff: extra thick shaggy hair under and around neck
    ruff = loft([sc((0, -0.47, 0.98)), sc((0, -0.62, 1.12)), sc((0, -0.74, 1.27))],
                [0.13 * S, 0.12 * S, 0.085 * S], [0.12 * S, 0.12 * S, 0.095 * S], segs=24, res=5)
    for v in ruff.verts:
        v.co.z -= 0.04 * S
    neck = merge(neck, ruff)
    neck = fuse(neck, voxel=0.016, smooth_iter=8)


def neckcol(p, n):
    c = coat(p, n)
    t = (p.z - 0.9 * S) / (0.5 * S)
    # throat lighter, darker toward head
    if n.z < -0.2:
        c = mixc(c, '#d9c4a0', 0.4 * (n.z * -1))
    if STAG:
        fade = max(0.0, min(1.0, (-0.42 * S - p.y) / (0.18 * S)))
        c = mixc(c, '#3a271a', (0.3 + 0.25 * (fbm(p, 30, 2, 5) * 0.5 + 0.5)) * fade)
    return c


neck_ob = part('neck', neck, [fur], nb, parent=body_ob, colorfn=neckcol, noise=dict(amp=0.003, freq=30, seed=2))

# ================= HEAD =================
P0 = sc((0, -0.745, 1.315))
D = V((0, -0.88, -0.475)).normalized()
U = V((0, -0.475, 0.88)).normalized()


def hp(t, u=0.0, x=0.0):
    return P0 + D * (t * S) + U * (u * S) + V((x * S, 0, 0))


ts = [-0.05, 0.02, 0.10, 0.18, 0.26, 0.31, 0.335]
hrx = [0.054, 0.063, 0.057, 0.040, 0.030, 0.026, 0.024]
hrz = [0.068, 0.080, 0.070, 0.050, 0.038, 0.033, 0.029]
ups = [0.0, 0.0, -0.003, -0.012, -0.020, -0.022, -0.020]
head_pts = [hp(t, u) for t, u in zip(ts, ups)]
headbm = loft(head_pts, [r * S for r in hrx], [r * S for r in hrz], segs=24, res=6)
# cheek / brow bumps
parts_h = [headbm]
for sx in (1, -1):
    parts_h.append(blob(hp(0.06, -0.015, sx * 0.045), (0.028 * S, 0.06 * S, 0.05 * S), rot=(0.4, 0, 0)))  # cheek muscle
    parts_h.append(blob(hp(0.105, 0.04, sx * 0.048), (0.022 * S, 0.03 * S, 0.014 * S), rot=(-0.4, 0, 0)))  # brow ridge
headbm = merge(*parts_h)
headbm = fuse(headbm, voxel=0.0068 * S, smooth_iter=6, smooth_f=0.5)
# nose pad
nose = blob(hp(0.331, -0.019), (0.024 * S, 0.016 * S, 0.016 * S), rot=(math.atan2(-D.z, -D.y) * 0 + 0.35, 0, 0))
set_mat_index(nose, 2)
extra = [nose]
for sx in (1, -1):
    # nostrils
    nn = blob(hp(0.343, -0.014, sx * 0.0125), (0.0055 * S, 0.008 * S, 0.0045 * S), rot=(0.35, 0, sx * 0.3))
    set_mat_index(nn, 3); extra.append(nn)
    # eyes
    ec = hp(0.105, 0.012, sx * 0.050)
    eb = blob(ec, (0.0135 * S, 0.0155 * S, 0.0155 * S), segs=16, rings=12); set_mat_index(eb, 1); extra.append(eb)
    pb = blob(ec + V((sx * 0.0115 * S, -0.004 * S, 0)), (0.003 * S, 0.0075 * S, 0.0042 * S), segs=10, rings=8); set_mat_index(pb, 3); extra.append(pb)
    # tear gland dark line
    # lips: thin dark line under nose via colors
headbm = merge(headbm, *extra)


def headcol(p, n):
    q = (p - P0).dot(D) / S   # along head
    c = mixc('#8a6039' if not STAG else '#6a4630', '#3f2d21', max(0, (q - 0.12) * 4))
    if n.z < -0.3 or (p - P0).dot(U) / S < -0.045:   # underside / chin lighter
        c = mixc(c, '#d8c7a7', 0.6)
    if q > 0.28:
        c = mixc(c, '#231a15', 0.6)
    # white muzzle ring around nose
    uu = (p - P0).dot(U) / S
    c = mixc(c, '#efe6d2', max(0.0, 1 - abs(q - 0.305) / 0.03) * max(0.0, min(1.0, (-0.012 - uu) / 0.01)) * 0.7)
    # eye ring
    e = hp(0.105, 0.012, 0.05 * (1 if p.x > 0 else -1))
    c = mixc(c, '#d9c6a3', max(0.0, 1 - (p - e).length / (0.04 * S)) ** 1.5 * 0.7)
    return mulc(c, 0.9 + 0.2 * (fbm(p, 50, 2, 3) * 0.5 + 0.5))


head_ob = part('head', headbm, [fur, eyem, nosem, pupilm], P0, parent=neck_ob, colorfn=headcol,
               noise=dict(amp=0.0012, freq=70, seed=4))
# re-materialise indices: fur=0, eye=1, nose=2, pupil=3 -> index 3 is pupil and nostril dark. ok.

# ---- jaw
JH = hp(0.075, -0.048)
jpts = [JH + D * (t * S) + U * (-0.002 * S * t / 0.05) for t in (-0.01, 0.03, 0.09, 0.15, 0.21, 0.245)]
jawbm = loft(jpts, [0.030 * S, 0.033 * S, 0.028 * S, 0.023 * S, 0.020 * S, 0.018 * S], [0.026 * S, 0.028 * S, 0.022 * S, 0.017 * S, 0.014 * S, 0.013 * S], segs=16, res=5)
jaw_ob = part('jaw', jawbm, [fur], JH, parent=head_ob,
              colorfn=lambda p, n: mulc(mixc('#cdb998', '#4a382b', max(0, n.z) * 0.6 + max(0, ((p - P0).dot(D) / S - 0.26) * 6)), 1.0))

# ---- ears
ear_obs = []
for sx, nm in ((1, 'ear_l'), (-1, 'ear_r')):
    base = hp(0.012, 0.066, sx * 0.045)
    tip = base + V(sx * 0.15 * S, 0.05 * S, 0.12 * S)
    nrm = V(sx * 0.55, -0.80, 0.25)
    e = leaf_shape(base, tip, 0.058 * S, 0.0045 * S, bulge=0.45, segs=12, curve=(sx * 0.02 * S, 0.0, -0.01 * S), res=4, up=nrm)
    # cup the ear a bit
    for v in e.verts:
        d = (v.co - base)
        v.co += nrm.normalized() * (0.012 * S) * (1 - abs(d.length / (tip - base).length - 0.5) * 2) * 0.0
    eo = part(nm, e, [fur], base, parent=head_ob,
              colorfn=lambda p, n, nrm=nrm: mixc(mixc('#8a6039' if not STAG else '#6a4630', '#2c2019', max(0, ((p - base).length / (tip - base).length - 0.75)) * 3)
                                                   if n.dot(nrm) < 0 else '#d8c2a5', '#efe3cf', 0.0))
    ear_obs.append(eo)

# ---- antlers (stag)
if STAG:
    def antler_side(sx, nm):
        b0 = hp(0.015, 0.078, sx * 0.042)
        beam = [V((0, 0, 0)), V((0.05, 0.05, 0.15)), V((0.13, 0.13, 0.33)), V((0.21, 0.14, 0.52)), V((0.27, 0.07, 0.72)), V((0.30, -0.05, 0.90)), V((0.29, -0.20, 1.02))]
        bp = [b0 + V(p.x * sx, p.y, p.z) for p in [q * 1.0 for q in beam]]
        parts = [loft(bp, [0.034, 0.026, 0.024, 0.021, 0.017, 0.014, 0.006], segs=10, res=6, cap_push=0.8)]

        def at(fr):
            i = fr * (len(bp) - 1); k = min(int(i), len(bp) - 2); return bp[k].lerp(bp[k + 1], i - k)

        def tine(fr, dirv, L, r0=0.012, curve=(0, 0, 0.06), n=4):
            s = at(fr)
            dv = V(dirv[0] * sx, dirv[1], dirv[2]).normalized()
            c = V(curve[0] * sx, curve[1], curve[2])
            tp = [s - dv * 0.01, s + dv * L * 0.33 + c * 0.2, s + dv * L * 0.66 + c * 0.6, s + dv * L + c]
            return loft(tp, [r0, r0 * 0.75, r0 * 0.5, 0.0035], segs=8, res=4, cap_push=1.0)
        parts.append(tine(0.12, (0.25, -0.75, 0.55), 0.30, 0.013, (0, -0.02, 0.09)))     # brow
        parts.append(tine(0.26, (0.35, -0.55, 0.65), 0.28, 0.012, (0.01, -0.03, 0.10)))   # bez
        parts.append(tine(0.46, (0.55, -0.25, 0.75), 0.30, 0.011, (0.0, -0.02, 0.09)))    # trez
        # crown (top)
        parts.append(tine(0.80, (0.5, 0.6, 0.65), 0.26, 0.010, (0.0, 0.0, 0.05)))
        parts.append(tine(0.88, (0.7, -0.2, 0.75), 0.24, 0.009, (0.02, 0.0, 0.05)))
        parts.append(tine(0.95, (0.5, -0.5, 0.65), 0.20, 0.008, (0.0, 0.0, 0.05)))
        bm = merge(*parts)
        z0 = b0.z
        ao = part(nm, bm, [antm], b0, parent=head_ob,
                  colorfn=lambda p, n: mulc(mixc('#6e5539', '#eadfc2', (p.z - z0) / 0.7 * 1.5 - 0.1), 1.0 + 0.25 * (fbm(p, 120, 2, 7) * .5 + .5)),
                  noise=dict(amp=0.0016, freq=200, seed=9))
        return ao
    ear_obs += [antler_side(1, 'antler_l'), antler_side(-1, 'antler_r')]

# ================= TAIL =================
tr = sc((0, 0.72, 0.93))
tail_pts = [tr, sc((0, 0.775, 0.90)), sc((0, 0.80, 0.83)), sc((0, 0.805, 0.77))]
tailbm = loft(tail_pts, [0.040 * S, 0.034 * S, 0.028 * S, 0.012 * S], [0.030 * S, 0.034 * S, 0.028 * S, 0.012 * S], segs=14, res=4)
tail_ob = part('tail', tailbm, [fur], tr, parent=body_ob,
               colorfn=lambda p, n: mixc(mixc('#5a3d27', '#ecdcbb', max(0, -n.z) * 1.5 + max(0, n.y) * 0.5), '#ecdcbb', 0.5) if True else None)

# ================= LEGS =================
leg_objs = []


def leg(prefix, sx, joints, upper_r, lower_r, hoof_r, hind):
    """joints: hip, mid(optional stifle), knee, fetlock, toe; all for +x; mirrored by sx."""
    hip, knee, fet, toe = joints['hip'], joints['knee'], joints['fet'], joints['toe']
    mid = joints.get('mid')

    def m(v):
        return V((v[0] * sx * S, v[1] * S, v[2] * S))
    up_pts = [m(hip)] + ([m(mid)] if mid else [m(tuple((a + b) / 2 for a, b in zip(hip, knee)))]) + [m(knee)]
    ub = loft(up_pts, [r * S for r in upper_r[0]], [r * S for r in upper_r[1]], segs=18, res=6, up=(0, -1, 0))
    uo = part(prefix + '_upper', ub, [fur], m(hip), parent=body_ob, colorfn=coat, noise=dict(amp=0.0015, freq=40, seed=5))
    lp = [m(knee), m(tuple((a + b) / 2 for a, b in zip(knee, fet))), m(fet), m(fet) + V(0, -0.012 * S, -0.045 * S)]
    lb = loft(lp, [r * S for r in lower_r[0]] + [lower_r[0][2] * S * 0.85], [r * S for r in lower_r[1]] + [lower_r[1][2] * S * 0.85], segs=14, res=6, up=(0, -1, 0))
    # carpal/hock knob
    kn = blob(m(knee), (lower_r[0][0] * 1.15 * S, lower_r[1][0] * 1.25 * S, 0.03 * S), rot=(0, 0, 0), segs=12, rings=8)
    lb = merge(lb, kn)
    lo = part(prefix + '_lower', lb, [fur], m(knee), parent=uo, colorfn=coat)
    hp_ = [m(fet) + V(0, -0.008 * S, -0.038 * S), m(toe) + V(0, 0, 0.022 * S), m(toe)]
    hb = loft(hp_, [hoof_r[0] * S, hoof_r[1] * S, hoof_r[2] * S], [hoof_r[3] * S, hoof_r[4] * S, hoof_r[5] * S], segs=12, res=4, up=(0, -1, 0), power=2.4, cap_push=0.25)
    # dewclaws
    for dx in (-1, 1):
        hb = merge(hb, blob(m(fet) + V(dx * 0.012 * S, 0.02 * S * (1 if hind else 1) * -1 * -1, -0.03 * S), (0.008 * S, 0.012 * S, 0.012 * S), segs=8, rings=6))
    ho = part(prefix + '_hoof', hb, [hoofm], m(fet), parent=lo)
    leg_objs.extend([uo, lo, ho])


for sx, side in ((1, 'l'), (-1, 'r')):
    leg('leg_f' + side, sx,
        dict(hip=(0.105, -0.36, 0.76), knee=(0.092, -0.415, 0.435), fet=(0.088, -0.405, 0.115), toe=(0.088, -0.440, 0.006)),
        ([0.068, 0.048, 0.030], [0.085, 0.056, 0.036]), ([0.028, 0.019, 0.019], [0.030, 0.022, 0.020]),
        (0.019, 0.023, 0.026, 0.020, 0.026, 0.030), False)
    leg('leg_h' + side, sx,
        dict(hip=(0.10, 0.47, 0.78), mid=(0.10, 0.40, 0.57), knee=(0.085, 0.60, 0.415), fet=(0.085, 0.575, 0.115), toe=(0.085, 0.545, 0.006)),
        ([0.085, 0.058, 0.032], [0.135, 0.090, 0.044]), ([0.026, 0.019, 0.018], [0.032, 0.022, 0.020]),
        (0.019, 0.023, 0.026, 0.020, 0.026, 0.030), True)

allparts = [body_ob, neck_ob, head_ob, jaw_ob, tail_ob] + ear_obs + leg_objs
name = 'stag' if STAG else 'deer'

meta = {
    'species': 'red deer stag' if STAG else 'red deer doe (summer coat)',
    'forward': '-Y blender (+Z three.js)', 'scale_hint_m': {'shoulder_height': round(1.05 * S, 2), 'length': round(1.45 * S, 2), 'head_height_alert': round(1.5 * S, 2)},
    'parts': {'root': 'body', 'neck': 'neck', 'head': 'head', 'jaw': 'jaw', 'ears': ['ear_l', 'ear_r'], 'tail': 'tail',
              'antlers': ['antler_l', 'antler_r'] if STAG else [], 'left_is': '+X blender (+X three.js)'},
    'hierarchy': {'body': ['neck', 'tail', 'leg_*_upper'], 'neck': ['head'], 'head': ['jaw', 'ear_l', 'ear_r'] + (['antler_l', 'antler_r'] if STAG else []),
                  'leg_xx_upper': ['leg_xx_lower'], 'leg_xx_lower': ['leg_xx_hoof']},
    'gait': {'walk_cycle_s': 1.3 if not STAG else 1.4, 'trot_cycle_s': 0.7,
             'legs': {'leg_fl': ['upper', 'lower', 'hoof'], 'leg_fr': ['upper', 'lower', 'hoof'], 'leg_hl': ['upper', 'lower', 'hoof'], 'leg_hr': ['upper', 'lower', 'hoof']},
             'walk_order': ['leg_hl', 'leg_fl', 'leg_hr', 'leg_fr'], 'phase_offsets': {'leg_hl': 0.0, 'leg_fl': 0.25, 'leg_hr': 0.5, 'leg_fr': 0.75},
             'rotation_axis': 'X (positive X rotation swings the lower end of a limb backward (+Y), i.e. foot goes back)',
             'swing_deg': {'upper': [-28, 28], 'lower_fore': [0, 55], 'lower_hind': [-60, 10], 'hoof': [-15, 20]},
             'note': 'Forelegs: carpus flexion = +X rot of lower (foot goes back/up). Hind: hock flexion = -X rot of lower (foot goes forward under belly) in swing; upper swings +/-X about hip.'},
    'idle': {'head_bob_deg': 4, 'ear_flick_deg': 18, 'tail_flick_deg': 12, 'breath': 'scale body Y 1.0..1.012 at 0.3 Hz'},
    'grazing_pose': {'neck_rot_x_deg': 62, 'head_rot_x_deg': 25, 'jaw_chew_deg': [0, 8], 'front_leg_upper_rot_x_deg': [0, 0],
                     'note': 'positive X rotation about pivot pitches the free end downward (nose goes down)'},
    'alert_pose': {'neck_rot_x_deg': -8, 'head_rot_x_deg': -5, 'ears_out_deg': 20},
    'pivots': 'each part origin = joint; see bundle parts[].pivot (three.js coords)',
}
print(export_bundle(OUT_DIR + '/%s.json' % name, allparts, meta))
write_meta(name, meta)
print('tris', tri_count(allparts))
if os.environ.get('POSE') == 'graze':
    neck_ob.rotation_euler.x = math.radians(62); head_ob.rotation_euler.x = math.radians(25); jaw_ob.rotation_euler.x = math.radians(-6)
    name += '_graze'
if PREVIEW:
    preview_grid(PREVIEW_DIR + '/%s.png' % name, [((3.4*S, 0.3, 1.0*S), (0,0,0.78*S)), ((2.4*S, -2.4*S, 1.3*S), (0,0,0.8*S)), ((0.9*S, -2.2*S, 1.9*S), (0,-0.8*S,1.5*S), 60), ((-2.6*S, 2.6*S, 1.4*S), (0,0,0.8*S))], target=(0, 0, 0.78 * S))
