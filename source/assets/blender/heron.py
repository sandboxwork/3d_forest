import sys
sys.path.insert(0, '/shared/river/assets/blender')
from birdlib import *

PREVIEW = os.environ.get('PREVIEW', '1') == '1'
POSE = os.environ.get('POSE', '')
reset_scene()

plum = vcol_mat('heron_plumage', '#ffffff', rough=0.75)
feath = vcol_mat('heron_flight_feathers', '#ffffff', rough=0.7)
billm = vcol_mat('heron_bill', '#ffffff', rough=0.35)
eyem = make_mat('eye', '#f1c21b', rough=0.05)
pupilm = make_mat('pupil', '#000000', rough=0.08)
legm = vcol_mat('heron_legs', '#ffffff', rough=0.5)

GREY = '#93a0a8'; DGREY = '#6f7a84'; WHITE = '#f1f0ea'; BLACK = '#1b1e23'; PALE = '#d9dde0'


def bodycol(p, n):
    back = sstep(0.0, 0.8, n.z) + sstep(0.0, 0.8, n.x * n.x) * 0.2
    c = mixc(WHITE, GREY, min(1, back * 1.0))
    c = mixc(c, '#c9d0d4', sstep(-0.3, -1.0, n.z) * 0.6)
    # dark streaks on breast
    st = fbm(V(p.x * 6, p.y * 1.0, p.z * 1.0), 70, 2, 2)
    c = mixc(c, '#3a4048', max(0, st - 0.25) * 1.3 * sstep(0.2, -0.6, n.y) * (1 - back))
    # black shoulder patch
    c = mixc(c, BLACK, max(0, 1 - (V(abs(p.x), p.y, p.z) - V(0.06, -0.06, 0.74)).length / 0.06) * 0.9)
    return mulc(c, 0.93 + 0.14 * (fbm(p, 120, 2, 4) * .5 + .5))


# ---------------- body
pts = [V(0, -0.13, 0.80), V(0, -0.06, 0.74), V(0, 0.06, 0.655), V(0, 0.17, 0.585), V(0, 0.24, 0.55)]
bb = loft(pts, [0.04, 0.075, 0.086, 0.058, 0.012], [0.05, 0.09, 0.095, 0.062, 0.015], segs=28, res=6)
bb = fuse(bb, voxel=0.0075, smooth_iter=10)
paint(bb, bodycol)
body = part('body', bb, [plum], V(0, 0.02, 0.64), noise=dict(amp=0.0015, freq=100, seed=2))

# ---------------- neck (3 segments, S-curve)
A = V(0, -0.125, 0.80); B = V(0, -0.21, 0.88); C = V(0, -0.225, 0.965); D = V(0, -0.165, 1.03); Ee = V(0, -0.165, 1.105); F = V(0, -0.205, 1.165)


def neckcol(p, n):
    c = mixc(WHITE, PALE, 0.3)
    # dark streak line along the front of the neck
    fr = sstep(-0.3, -0.9, n.y) * (1 - min(1, abs(p.x) / 0.012))
    c = mixc(c, '#2c3138', fr * 0.85)
    # grey darkening up top behind
    c = mixc(c, '#9aa4ac', sstep(0.3, 0.9, n.y) * 0.5)
    return mulc(c, 0.95 + 0.1 * (fbm(p, 150, 2, 6) * .5 + .5))


def seg(name, pts_, rad, parent, pivot):
    bm = loft(pts_, rad, rad, segs=14, res=6, cap_push=0.9)
    paint(bm, neckcol)
    return bm


n1 = loft([A + V(0, 0.03, -0.03), A, B, C], [0.03, 0.028, 0.022, 0.0195], segs=14, res=6, cap_push=0.9)
paint(n1, neckcol)
# long lanceolate plumes hanging at base of neck
pl = []
for i in range(9):
    x = (i - 4) * 0.008
    base = V(x, -0.17 + 0.004 * abs(i - 4), 0.83 - 0.01 * (i % 2))
    pl.append(feather(base, base + V(x * 1.2, -0.04, -0.22 - 0.02 * (4 - abs(i - 4)) * 0.3), 0.007, lambda t, lat: mixc(WHITE, '#b7c0c6', t * 0.7), thick=0.0008, normal=(1, 0, 0), bulge=0.25))
neck1 = part('neck_1', merge(n1, *pl), [plum], A, parent=body)
n2 = loft([C + V(0, 0.008, -0.03), C, D, Ee], [0.0195, 0.0185, 0.0175, 0.0165], segs=14, res=6, cap_push=0.9)
paint(n2, neckcol)
neck2 = part('neck_2', n2, [plum], C, parent=neck1)
n3 = loft([Ee + V(0, 0.0, -0.025), Ee, F], [0.0165, 0.0165, 0.017], segs=14, res=5, cap_push=0.9)
paint(n3, neckcol)
neck3 = part('neck_3', n3, [plum], Ee, parent=neck2)

# ---------------- head
HP = F
D_ = V(0, -0.97, -0.24).normalized()
U_ = V(0, -0.24, 0.97).normalized()


def hp(t, u=0, x=0):
    return HP + D_ * t + U_ * u + V(x, 0, 0)


hd = loft([hp(-0.03), hp(0.0), hp(0.04), hp(0.085)], [0.016, 0.021, 0.0185, 0.0125], [0.02, 0.0235, 0.0185, 0.013], segs=16, res=5)


def headcol(p, n):
    q = (p - HP).dot(D_)
    u = (p - HP).dot(U_)
    c = V(1, 1, 1)
    c = mixc(WHITE, '#d7dde1', 0.0)
    # black crown band from eye to nape
    band = sstep(0.008, 0.016, u) * sstep(0.095, 0.06, q) + sstep(-0.01, 0.0, -q) * 0.0
    c = mixc(c, BLACK, min(1, band * 1.2) if u > 0.006 else 0)
    # grey nape
    c = mixc(c, '#8c969e', sstep(0.02, -0.03, q) * 0.7)
    return c


paint(hd, headcol)
crest = []
for i, (dx, l) in enumerate(((0.004, 0.13), (-0.004, 0.11), (0.0, 0.15))):
    b = hp(0.0, 0.02, dx)
    crest.append(feather(b, b + V(dx * 2, 0.11 * l / 0.13 + 0.03, -0.02 - 0.006 * i), 0.0035, lambda t, lat: hex_rgb('#15181d'), thick=0.0006, normal=(1, 0, 0), bulge=0.3, curve=(0, 0, 0.012)))
for b in crest:
    pass
up_bill = loft([hp(0.07, -0.004), hp(0.12, -0.007), hp(0.19, -0.010), hp(0.235, -0.012)], [0.0135, 0.0105, 0.0062, 0.0012], [0.0145, 0.0115, 0.007, 0.0016], segs=12, res=4, cap_push=0.8)
set_mat_index(up_bill, 2)
paint(up_bill, lambda p, n: mixc('#d8a537', '#e3b84a', sstep(0.0, 0.1, (p - HP).dot(D_) - 0.07)) if n.z < 0.7 else mixc('#7a6536', '#d8a537', 0.45))
eyes = eye_pair(None, (0.0155, -0.022, 0.0), 0.0052)
ex = []
for sx in (1, -1):
    ex.append(blob(hp(0.045, 0.004, sx * 0.0145), (0.0052, 0.0052, 0.0052), segs=12, rings=8))
    ex[-1] = None
eyes = []
for sx in (1, -1):
    e = blob(hp(0.048, 0.006, sx * 0.0148), (0.0058, 0.0058, 0.0058), segs=12, rings=8); set_mat_index(e, 1)
    p = blob(hp(0.048, 0.006, sx * 0.0148) + V(sx * 0.0033, -0.0028, 0), (0.0033, 0.0033, 0.0033), segs=10, rings=8); set_mat_index(p, 3)
    eyes += [e, p]
for b in eyes:
    paint(b, lambda p, n: (1, 1, 1))
for b in crest:
    set_mat_index(b, 0)
head = part('head', merge(hd, up_bill, *eyes, *crest), [plum, eyem, billm, pupilm], HP, parent=neck3)
lo = loft([hp(0.065, -0.014), hp(0.12, -0.016), hp(0.185, -0.0145), hp(0.228, -0.0135)], [0.0095, 0.0075, 0.0045, 0.001], [0.007, 0.0055, 0.0035, 0.001], segs=10, res=4, cap_push=0.8)
paint(lo, lambda p, n: hex_rgb('#d8a537'))
bill_l = part('bill_lower', lo, [billm], hp(0.065, -0.014), parent=head)

# ---------------- tail
TP = V(0, 0.2, 0.575)
tb = []
for i in range(10):
    a = math.radians((i - 4.5) * 2.5)
    L = 0.14 - abs(i - 4.5) * 0.004
    base = TP + V(0, 0, 0.0005 * i)
    tb.append(feather(base, base + V(math.sin(a) * L, math.cos(a) * L * 0.93, -0.06), 0.022, lambda t, lat: mixc('#8e99a1', '#606b75', t * 0.8), thick=0.0012))
tail = part('tail', merge(*tb), [feath], TP, parent=body)


# ---------------- wings
def build_wing():
    S = V(0.085, -0.055, 0.735)
    E = S + V(0.17, 0.01, 0)
    Wr = E + V(0.17, -0.02, 0)
    pl = [0.23, 0.25, 0.27, 0.29, 0.30, 0.30, 0.29, 0.275, 0.26, 0.24]
    P = dict(S=S, E=E, Wr=Wr, bone=0.6, thick=0.0018, hand_len=V(0.075, -0.015, 0),
             n_up=9, up_len=0.11, up_w=0.04, up_col=lambda i: fcol('#98a3aa', '#b9c2c7', dark=0.15),
             n_sec=12, sec_len=lambda t: 0.19 + 0.02 * math.sin(t * 2.5), sec_w=0.042, sec_col=lambda i, n: fcol('#7d8891', '#a9b3ba', dark=0.3),
             n_prim=10, prim_len=pl, prim_w=0.03, prim_col=lambda j, n: fcol('#2a2f36', '#4d555e', dark=0.2), fan=(16, 5),
             pcov_col=lambda i: fcol('#535b64', '#7d8891'),
             covers=[(0.08, 0.003, 12, 0.042, fcol('#a2acb3', '#ccd3d8')), (0.055, 0.006, 12, 0.036, fcol('#abb5bb', '#d6dce0')), (0.035, 0.009, 12, 0.03, fcol('#b5bec4', '#e0e5e8'))])
    return build_wing_bms(P), dict(upper=S, fore=E, hand=Wr)


rig = WingRig()
bm_l, PIV = build_wing(); rig.make('wing_l', 1, bm_l, PIV, std_fold(), body, [feath])
bm_r, PIV = build_wing(); rig.make('wing_r', -1, bm_r, PIV, std_fold(), body, [feath])

# ---------------- legs
legs = []
LEGC = '#8f8c52'
for sx, nm in ((1, 'l'), (-1, 'r')):
    hip = V(sx * 0.045, 0.06, 0.58); knee = V(sx * 0.05, 0.085, 0.37); toeb = V(sx * 0.052, 0.06, 0.108)
    up = loft([hip + V(0, 0, 0.02), hip, hip.lerp(knee, 0.5), knee], [0.03, 0.026, 0.017, 0.0115], [0.032, 0.027, 0.016, 0.011], segs=12, res=5, up=(0, -1, 0))
    paint(up, lambda p, n: mixc(mixc(WHITE, GREY, 0.4), LEGC, sstep(0.46, 0.40, p.z)))
    upper = part('leg_upper_' + nm, up, [plum], hip, parent=body)
    lw = loft([knee, knee.lerp(toeb, 0.5), toeb], [0.0115, 0.0085, 0.0075], [0.011, 0.0075, 0.0065], segs=10, res=5, up=(0, -1, 0))
    kn = blob(knee, (0.0125, 0.013, 0.013), segs=10, rings=8)
    lw = merge(lw, kn)
    paint(lw, lambda p, n: hex_rgb(LEGC))
    lower = part('leg_lower_' + nm, lw, [legm], knee, parent=upper)
    toes = []
    for ang, ln in ((-32, 0.095), (0, 0.11), (32, 0.095)):
        a = math.radians(ang)
        d = V(math.sin(a) * sx, -math.cos(a), -0.12)
        tp = toeb + d.normalized() * ln
        tp.z = 0.084
        toes.append(loft([toeb, toeb.lerp(tp, 0.5), tp], [0.0075, 0.0055, 0.0042], [0.0065, 0.0045, 0.0035], segs=6, res=3, up=(0, 0, 1)))
    hp_ = toeb + V(0, 0.07, -0.022); hp_.z = 0.084
    toes.append(loft([toeb, hp_], [0.0065, 0.004], [0.0055, 0.0032], segs=6, res=2, up=(0, 0, 1)))
    for t_ in toes:
        paint(t_, lambda p, n: hex_rgb('#7d7a48'))
    foot = part('foot_' + nm, merge(*toes), [legm], toeb, parent=lower)
    legs += [upper, lower, foot]

body.location.z -= 0.08
bpy.context.view_layer.update()
allp = [body, neck1, neck2, neck3, head, bill_l, tail] + rig.objs + legs
meta = {'species': 'Grey heron (Ardea cinerea), standing', 'forward': '-Y', 'left': '+X', 'origin': 'ground under body centre',
        'scale_hint_m': {'standing_height_to_crown': 1.1, 'bill_length': 0.15, 'wingspan_open': 1.7, 'body_length': 0.4},
        'parts': {'root': 'body', 'neck': ['neck_1', 'neck_2', 'neck_3'], 'head': 'head', 'bill_lower': 'bill_lower', 'tail': 'tail',
                  'wing_l': ['wing_l_upper', 'wing_l_fore', 'wing_l_hand'], 'wing_r': ['wing_r_upper', 'wing_r_fore', 'wing_r_hand'],
                  'legs': {'l': ['leg_upper_l', 'leg_lower_l', 'foot_l'], 'r': ['leg_upper_r', 'leg_lower_r', 'foot_r']}},
        'hierarchy': {'body': ['neck_1', 'tail', 'wing_*_upper', 'leg_upper_*'], 'neck_1': ['neck_2'], 'neck_2': ['neck_3'], 'neck_3': ['head'], 'head': ['bill_lower'],
                      'leg_upper_*': ['leg_lower_*'], 'leg_lower_*': ['foot_*'], 'wing_*_upper': ['wing_*_fore'], 'wing_*_fore': ['wing_*_hand']},
        'rest_pose': 'standing, wings folded (geometry), S-curved neck. Strike pose: rotate neck_1 about X by -25 deg (forward/up), neck_2 +35, neck_3 -25 (straightens S), then dart forward.',
        'strike': {'neck_1_rot_x_deg': -20, 'neck_2_rot_x_deg': 30, 'neck_3_rot_x_deg': -40, 'head_rot_x_deg': 10},
        'walk': {'cycle_s': 2.4, 'leg_upper_rot_x_deg': [-25, 25], 'leg_lower_rot_x_deg': [0, -40], 'foot_rot_x_deg': [-20, 20], 'note': 'slow deliberate stepping, lift foot high, knee joint bends backward (lower: negative X rotation folds foot back)'},
        'wing_open_pose': wing_meta(rig),
        'wing_open_note': 'per-segment local quaternion xyzw (three.js) to spread the wing fully; slerp from identity. Flap: rotate wing_*_upper about three.js Z.',
        'idle': {'head_turn_deg': 25, 'neck_breath': 1.0, 'crest_wind': 'none'}}
print(export_bundle(OUT_DIR + '/heron.json', allp, meta))
write_meta('heron', meta)
print('tris', tri_count(allp))
if POSE == 'open':
    apply_open(rig)
if PREVIEW:
    preview_grid(PREVIEW_DIR + '/heron%s.png' % ('_open' if POSE == 'open' else ''),
                 [((2.6, 0, 0.75), (0, 0, 0.62), 50), ((1.6, -2.0, 1.0), (0, 0, 0.6), 50), ((0.6, -0.9, 1.25), (0, -0.2, 1.1), 60), ((-2.0, 1.8, 1.2), (0, 0, 0.6), 50)],
                 target=(0, 0, 0.6))
