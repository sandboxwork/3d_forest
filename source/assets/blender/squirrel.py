import sys
sys.path.insert(0, '/shared/river/assets/blender')
from animlib import *

PREVIEW = os.environ.get('PREVIEW', '1') == '1'
reset_scene()
fur = vcol_mat('squirrel_fur', '#ffffff', rough=0.9)
eyem = make_mat('eye', '#140a06', rough=0.04)
pupilm = make_mat('pupil', '#000000', rough=0.1)
nosem = make_mat('nose_wet', '#3b2622', rough=0.2)
whisk = make_mat('whisker', '#e5ddcf', rough=0.5)
RED = '#b4582b'; RED2 = '#8f3f1c'; WH = '#efe7d8'


def coat(p, n):
    belly = max(0.0, -n.z * 1.4 - 0.1) + (max(0, (0.05 - p.z) * 10) if abs(p.x) < 0.02 else 0)
    c = mixc(RED, RED2, 0.35 * (fbm(p, 12, 2, 1) * .5 + .5) + max(0, n.z - 0.5) * 0.3)
    c = mixc(c, WH, min(1, belly))
    k = 0.88 + 0.12 * (fbm(p, 140, 2, 2) * .5 + .5) + 0.1 * (fbm(V(p.x * 4, p.y * .7, p.z * 4), 60, 2, 3) * .5 + .5)
    return mulc(c, k)


ys = [-0.10, -0.06, 0.0, 0.06, 0.11, 0.135]
zc = [0.105, 0.108, 0.108, 0.105, 0.098, 0.09]
rx = [0.03, 0.04, 0.042, 0.042, 0.038, 0.022]
rz = [0.045, 0.06, 0.06, 0.056, 0.05, 0.03]
bl = [loft([V(0, y, z) for y, z in zip(ys, zc)], rx, rz, segs=24, res=4)]
for sx in (1, -1):
    bl.append(blob((sx * 0.03, 0.085, 0.088), (0.026, 0.05, 0.05)))
bm = fuse(merge(*bl), voxel=0.0048, smooth_iter=8)
body = part('body', bm, [fur], (0, 0, 0.09), colorfn=coat, noise=dict(amp=0.0008, freq=200, seed=1))

P0 = V(0, -0.095, 0.14)
D = V(0, -0.93, -0.2).normalized(); U = V(0, -0.2, 0.93).normalized()
hp = lambda t, u=0.0, x=0.0: P0 + D * t + U * u + V(x, 0, 0)
ts = [-0.02, 0.01, 0.035, 0.06, 0.08]
hb = [loft([hp(t) for t in ts], [0.026, 0.03, 0.028, 0.019, 0.011], [0.028, 0.032, 0.03, 0.021, 0.013], segs=18, res=5)]
for sx in (1, -1):
    hb.append(blob(hp(0.03, -0.012, sx * 0.02), (0.014, 0.02, 0.016)))
hb = fuse(merge(*hb), voxel=0.0026, smooth_iter=6, smooth_f=0.5)
ex = []
nose = blob(hp(0.083, -0.003), (0.0065, 0.004, 0.0055)); set_mat_index(nose, 2); ex.append(nose)
for sx in (1, -1):
    ec = hp(0.03, 0.012, sx * 0.0225)
    e = blob(ec, (0.0075, 0.008, 0.0085)); set_mat_index(e, 1); ex.append(e)
    pu = blob(ec + V(sx * 0.0045, -0.002, 0), (0.002, 0.0045, 0.0045), segs=8, rings=6); set_mat_index(pu, 3); ex.append(pu)
    for k in range(4):
        s0 = hp(0.07, -0.004 + k * 0.001, sx * 0.007)
        d = V(sx * 0.5, -0.6, (k - 1.5) * 0.12).normalized()
        w = loft([s0, s0 + d * 0.022, s0 + d * 0.05 + V(0, 0, -0.004)], [0.0003, 0.00025, 0.0001], segs=4, res=2, cap_push=1)
        set_mat_index(w, 4); ex.append(w)
hb = merge(hb, *ex)


def hcol(p, n):
    c = coat(p, n)
    u = (p - P0).dot(U); t = (p - P0).dot(D)
    c = mixc(c, WH, max(0, min(1, (-0.006 - u) * 120)) * 0.9)
    e = hp(0.03, 0.012, 0.0225 * (1 if p.x > 0 else -1))
    c = mixc(c, WH, max(0, 1 - (p - e).length / 0.016) * 0.8)
    return c


head = part('head', hb, [fur, eyem, nosem, pupilm, whisk], P0, parent=body, colorfn=hcol, noise=dict(amp=0.0005, freq=250, seed=4))

JH = hp(0.022, -0.02)
jb = loft([JH + D * t for t in (0.0, 0.02, 0.045, 0.06)], [0.014, 0.014, 0.0095, 0.0055], [0.008, 0.008, 0.006, 0.005], segs=10, res=4)
jaw = part('jaw', jb, [fur], JH, parent=head, colorfn=lambda p, n: WH)

ears = []
for sx, nm in ((1, 'ear_l'), (-1, 'ear_r')):
    base = hp(0.0, 0.026, sx * 0.016)
    tip = base + V(sx * 0.008, 0.004, 0.03)
    e = leaf_shape(base, tip, 0.015, 0.0025, bulge=0.3, segs=10, res=3, up=V(sx * 0.4, -0.9, 0.2))
    # ear tuft
    tuft = loft([tip - V(0, 0, 0.008), tip + V(sx * 0.002, 0.004, 0.012), tip + V(sx * 0.004, 0.006, 0.02)], [0.005, 0.0045, 0.0008], [0.002, 0.002, 0.0005], segs=6, res=3, cap_push=1)
    ears.append(part(nm, merge(e, tuft), [fur], base, parent=head, colorfn=lambda p, n: mixc(RED2, '#2d1a10', max(0, (p.z - base.z - 0.022) * 50)),
                     noise=dict(amp=0.0003, freq=200, seed=7)))

tr = V(0, 0.12, 0.095)
tpts = [tr, V(0, 0.17, 0.12), V(0, 0.225, 0.18), V(0, 0.235, 0.26), V(0, 0.19, 0.32), V(0, 0.12, 0.335), V(0, 0.075, 0.31)]
trx = [0.022, 0.04, 0.06, 0.07, 0.066, 0.05, 0.014]
trz = [0.022, 0.032, 0.042, 0.045, 0.042, 0.032, 0.014]
tb = fuse(loft(tpts, trx, trz, segs=20, res=6, cap_push=1.2), voxel=0.0055, smooth_iter=4)


def tcol(p, n):
    t = (p.y - tr.y)
    c = mixc(RED, '#d0a070', 0.35 + 0.25 * (fbm(p, 50, 2, 6) * .5 + .5))
    c = mixc(c, RED2, max(0, n.z) * 0.2)
    c = mixc(c, WH, max(0, min(1, (p.z - 0.3) * 10)) * 0.25)
    return mulc(c, 0.88 + 0.22 * (fbm(V(p.x * 3, p.y, p.z * 3), 90, 2, 9) * .5 + .5))


tail = part('tail', tb, [fur], tr, parent=body, colorfn=tcol, noise=dict(amp=0.0025, freq=90, seed=5))

legs = []


def lg(name, pts, rx_, rz_, pivot, parent, up=(0, -1, 0)):
    return part(name, loft(pts, rx_, rz_, segs=12, res=5, up=up), [fur], pivot, parent=parent, colorfn=coat, noise=dict(amp=0.0005, freq=200, seed=3))


for sx, s in ((1, 'l'), (-1, 'r')):
    m = lambda x, y, z: V(sx * x, y, z)
    sh = m(0.03, -0.055, 0.085); el = m(0.034, -0.045, 0.045); wr = m(0.03, -0.07, 0.016); pw = m(0.03, -0.09, 0.006)
    fu = lg('leg_f%s_upper' % s, [sh, (sh + el) / 2, el], [0.018, 0.013, 0.009], [0.022, 0.015, 0.011], sh, body)
    fl = lg('leg_f%s_lower' % s, [el, (el + wr) / 2, wr], [0.0085, 0.0075, 0.0065], [0.0095, 0.008, 0.007], el, fu)
    pb = loft([wr, (wr + pw) / 2, pw], [0.007, 0.0085, 0.0075], [0.008, 0.008, 0.005], segs=8, res=3, up=(0, 0, 1))
    pb = merge(pb, *[blob(pw + V(d * 0.004, -0.008, 0.0), (0.0018, 0.008, 0.0025), segs=6, rings=4) for d in (-1, 0, 1)])
    pa = part('leg_f%s_paw' % s, pb, [fur], wr, parent=fl, colorfn=coat)
    hip = m(0.032, 0.085, 0.09); kn = m(0.038, 0.05, 0.05); hk = m(0.034, 0.115, 0.02); toe = m(0.034, 0.05, 0.006)
    th = lg('leg_h%s_thigh' % s, [hip, (hip + kn) / 2, kn], [0.026, 0.021, 0.011], [0.036, 0.028, 0.014], hip, body)
    lo = lg('leg_h%s_lower' % s, [kn, (kn + hk) / 2, hk], [0.011, 0.009, 0.0075], [0.013, 0.01, 0.008], kn, th)
    fb = loft([hk, (hk + toe) / 2, toe], [0.013, 0.014, 0.011], [0.008, 0.007, 0.0045], segs=8, res=4, up=(0, 0, 1))
    fb = merge(fb, *[blob(toe + V(d * 0.004, -0.008, 0.0), (0.0018, 0.008, 0.0025), segs=6, rings=4) for d in (-1, 0, 1)])
    ft = part('leg_h%s_foot' % s, fb, [fur], hk, parent=lo, colorfn=coat)
    legs += [fu, fl, pa, th, lo, ft]

allparts = [body, head, jaw] + ears + [tail] + legs
meta = {
    'species': 'red squirrel (Sciurus vulgaris)', 'forward': '-Y', 'left_is': '+X',
    'scale_hint_m': {'body_length': 0.23, 'height_to_back': 0.15, 'height_with_tail': 0.37, 'tail_length': 0.22},
    'parts': {'root': 'body', 'head': 'head', 'jaw': 'jaw', 'ears': ['ear_l', 'ear_r'], 'tail': 'tail'},
    'hierarchy': {'body': ['head', 'tail', 'leg_f*_upper', 'leg_h*_thigh'], 'head': ['jaw', 'ear_l', 'ear_r'],
                  'leg_f*_upper': ['leg_f*_lower'], 'leg_f*_lower': ['leg_f*_paw'], 'leg_h*_thigh': ['leg_h*_lower'], 'leg_h*_lower': ['leg_h*_foot']},
    'gait': {'bound_cycle_s': 0.35, 'note': 'bounding: fore pair then hind pair in phase; arch body via thigh/upper rot_x +-35deg; tail trails: tail rot_x small sway',
             'axis': 'X', 'swing_deg': {'upper': [-40, 40], 'lower': [0, 60], 'paw': [-20, 20]}},
    'idle': {'tail_flick_deg': 10, 'head_turn_deg': 25, 'ear_twitch_deg': 10, 'nibble': {'head_rot_x_deg': 10, 'jaw_deg': [0, 6], 'fore_upper_rot_x_deg': -50}},
    'pivots': 'part origin = joint',
}
print(export_bundle(OUT_DIR + '/squirrel.json', allparts, meta))
write_meta('squirrel', meta)
print('tris', tri_count(allparts))
if PREVIEW:
    preview_grid(PREVIEW_DIR + '/squirrel.png', [((0.75, 0.05, 0.25), (0, 0.05, 0.16), 50), ((0.5, -0.65, 0.38), (0, 0.04, 0.16), 50),
                                                 ((0.12, -0.3, 0.2), (0, -0.09, 0.14), 70), ((-0.5, 0.6, 0.35), (0, 0.05, 0.16), 50)], target=(0, 0, 0.16))
