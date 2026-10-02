import sys
sys.path.insert(0, '/shared/river/assets/blender')
from birdlib import *

PREVIEW = os.environ.get('PREVIEW', '1') == '1'
POSE = os.environ.get('POSE', '')
reset_scene()

plum = vcol_mat('hawk_plumage', '#ffffff', rough=0.75)
feath = vcol_mat('hawk_flight_feathers', '#ffffff', rough=0.7)
beakm = vcol_mat('hawk_beak', '#ffffff', rough=0.3)
eyem = make_mat('eye', '#3a1f0b', rough=0.05)
pupilm = make_mat('pupil', '#000000', rough=0.08)
talonm = vcol_mat('hawk_feet', '#ffffff', rough=0.45)

BROWN = '#5e4833'; DBROWN = '#3e3022'; PALE = '#e3d6bd'; RUFOUS = '#a9552b'


def bodycol(p, n):
    base = mixc(BROWN, '#6d5640', 0.5 * (fbm(p, 90, 2, 1) * .5 + .5))
    # pale underside with streaked belly band
    under = sstep(0.0, -0.6, n.z)
    c = mixc(base, PALE, under)
    band = sstep(-0.05, 0.05, p.y) * sstep(0.3, 0.15, p.y) * under
    st = fbm(V(p.x * 5, p.y * 1.0, p.z * 1), 55, 2, 4)
    c = mixc(c, DBROWN, max(0, st) * 1.2 * band)
    # feather edging
    d = sub_noise.voronoi(p * 160)[0][0]
    c = mulc(c, 0.88 + 0.12 * (1 - min(1, d * 1.4)))
    # bib/breast lighter streaks
    return c


Z0 = 0.13
pts = [V(0, -0.20, Z0 + 0.02), V(0, -0.10, Z0 + 0.0), V(0, 0.03, Z0), V(0, 0.17, Z0 - 0.005), V(0, 0.29, Z0 - 0.015)]
bb = loft(pts, [0.035, 0.072, 0.08, 0.06, 0.028], [0.045, 0.08, 0.082, 0.065, 0.028], segs=28, res=5)
bb = fuse(bb, voxel=0.0075, smooth_iter=8)
paint(bb, bodycol)
body = part('body', bb, [plum], V(0, 0.02, Z0), noise=dict(amp=0.0015, freq=100, seed=2))

# ---------------- head
HP = V(0, -0.195, Z0 + 0.04)
hd = blob(V(0, -0.225, Z0 + 0.052), (0.038, 0.046, 0.04), segs=24, rings=16)
hd = merge(hd, blob(V(0, -0.255, Z0 + 0.04), (0.025, 0.03, 0.025)), blob(V(0, -0.195, Z0 + 0.035), (0.045, 0.05, 0.05)))
for sx in (1, -1):
    hd = merge(hd, blob(V(sx * 0.03, -0.235, Z0 + 0.075), (0.016, 0.022, 0.008), rot=(0.0, sx * 0.4, 0)))   # brow ridge
hd = fuse(hd, voxel=0.0032, smooth_iter=6)


def headcol(p, n):
    c = mixc(BROWN, '#6d5640', 0.3)
    c = mixc(c, PALE, sstep(-0.2, -0.9, n.z) * sstep(-0.22, -0.25, p.y) * 0.8)
    c = mixc(c, DBROWN, sstep(0.3, 1.0, n.z) * 0.4)
    return c


paint(hd, headcol)
hook = loft([V(0, -0.262, Z0 + 0.04), V(0, -0.282, Z0 + 0.038), V(0, -0.297, Z0 + 0.027), V(0, -0.30, Z0 + 0.008)], [0.0135, 0.012, 0.0085, 0.0015], [0.0165, 0.0135, 0.0095, 0.003], segs=12, res=4, cap_push=0.8)
set_mat_index(hook, 2)
paint(hook, lambda p, n: mixc('#d8b53a', '#2b2e33', sstep(-0.272, -0.287, p.y)))
eyes = []
for sx in (1, -1):
    c = V(sx * 0.0305, -0.232, Z0 + 0.062)
    e = blob(c, (0.0088, 0.0088, 0.0088), segs=12, rings=8); set_mat_index(e, 1)
    pp = blob(c + V(sx * 0.0052, -0.0042, 0), (0.0048, 0.0048, 0.0048), segs=10, rings=8); set_mat_index(pp, 3)
    eyes += [e, pp]
for b in eyes:
    paint(b, lambda p, n: (1, 1, 1))
head = part('head', merge(hd, hook, *eyes), [plum, eyem, beakm, pupilm], HP, parent=body)
lo = loft([V(0, -0.262, Z0 + 0.024), V(0, -0.277, Z0 + 0.021), V(0, -0.288, Z0 + 0.016)], [0.0105, 0.009, 0.004], [0.0075, 0.006, 0.0035], segs=10, res=3, cap_push=0.8)
paint(lo, lambda p, n: mixc('#d8b53a', '#2b2e33', sstep(-0.268, -0.285, p.y)))
beak_l = part('beak_lower', lo, [beakm], V(0, -0.258, Z0 + 0.026), parent=head)

# ---------------- tail (fanned, horizontal)
TP = V(0, 0.27, Z0 - 0.012)
tb = []
nt = 12
for i in range(nt):
    a = math.radians((i - (nt - 1) / 2) * 3.2)
    L = 0.26 - abs(i - (nt - 1) / 2) * 0.004
    base = TP + V(0, 0, 0.0007 * i)
    tb.append(feather(base, base + V(math.sin(a) * L, math.cos(a) * L, -0.015), 0.044,
                      lambda t, lat: mixc(mixc(RUFOUS, '#8a4322', t * 0.4), '#231a14', sstep(0.68, 0.74, t) * (1 - sstep(0.86, 0.92, t))) if t < 0.92 else mixc('#e6d5b5', RUFOUS, 0.2),
                      thick=0.0018, bulge=0.4))
tail = part('tail', merge(*tb), [feath], TP, parent=body)


# ---------------- wings (authored OPEN)
def prim_col(j, n):
    def f(t, lat):
        c = mixc('#4a3b2c', '#6a5640', sstep(0.0, 0.5, t) * 0.4)
        c = mixc(c, '#1e1812', sstep(0.75, 1.0, t))
        bars = 0.5 + 0.5 * math.sin(t * 30 + j)
        c = mixc(c, '#2a2016', bars * 0.35)
        return mixc(c, '#8d7a5f', sstep(0.75, 1.0, abs(lat)) * 0.5)
    return f


def sec_col(i, n):
    def f(t, lat):
        c = mixc('#6a5440', '#8a7358', 0.5)
        bars = 0.5 + 0.5 * math.sin(t * 34 + i * 1.3)
        c = mixc(c, '#3a2c20', bars * 0.35)
        c = mixc(c, '#2a2018', sstep(0.85, 1.0, t) * 0.8)
        return mixc(c, '#a79070', sstep(0.75, 1.0, abs(lat)) * 0.5)
    return f


def build_wing():
    S = V(0.075, -0.03, Z0 + 0.01)
    E = S + V(0.15, 0.02, 0)
    Wr = E + V(0.15, -0.03, 0)
    pl = [0.25, 0.27, 0.295, 0.31, 0.32, 0.325, 0.32, 0.30, 0.275, 0.24]
    P = dict(S=S, E=E, Wr=Wr, bone=0.7, thick=0.0022, hand_len=V(0.06, -0.015, 0),
             n_up=10, up_len=0.19, up_w=0.05, up_covers=[(0.1, 0.003, 10, 0.045, fcol('#7a6347', '#b5a27f')), (0.065, 0.006, 10, 0.04, fcol('#816a4e', '#c0ae8a')), (0.04, 0.009, 10, 0.034, fcol('#8a7456', '#cdbb98'))], up_col=lambda i: fcol('#6a5440', '#9a8566', dark=0.1),
             n_sec=12, sec_len=lambda t: 0.21 + 0.02 * math.sin(t * 2.5), sec_w=0.046, sec_col=sec_col,
             n_prim=10, prim_len=pl, prim_w=0.03, prim_col=prim_col, fan=(34, 4),
             pcov_col=lambda i: fcol('#5a4634', '#8d7a5f'),
             covers=[(0.09, 0.003, 12, 0.045, fcol('#7a6347', '#b5a27f')), (0.06, 0.006, 12, 0.04, fcol('#816a4e', '#c0ae8a')), (0.04, 0.009, 12, 0.034, fcol('#8a7456', '#cdbb98'))])
    return build_wing_bms(P), dict(upper=S, fore=E, hand=Wr)


rig = WingRig()
bm_l, PIV = build_wing(); rig.make('wing_l', 1, bm_l, PIV, std_fold(), body, [feath], open_pose_only=True)
bm_r, PIV = build_wing(); rig.make('wing_r', -1, bm_r, PIV, std_fold(), body, [feath], open_pose_only=True)
FQ = fold_quats(std_fold())

# ---------------- legs tucked
legs = []
for sx, nm in ((1, 'l'), (-1, 'r')):
    hip = V(sx * 0.045, 0.10, Z0 - 0.06); ank = V(sx * 0.045, 0.17, Z0 - 0.095)
    th = loft([hip + V(0, -0.03, 0.02), hip, hip.lerp(ank, 0.5), ank], [0.025, 0.028, 0.016, 0.008], [0.03, 0.032, 0.02, 0.008], segs=12, res=4)
    paint(th, lambda p, n: mixc(BROWN, PALE, sstep(0.02, -0.03, p.z - (Z0 - 0.06)) * 0.5 + 0.2))
    up = part('leg_' + nm, th, [plum], hip, parent=body)
    toes = []
    for ang in (-25, 0, 25):
        a = math.radians(ang)
        d = V(math.sin(a) * sx, 0.9, -0.3).normalized()
        tp = ank + d * 0.048
        toes.append(loft([ank, ank.lerp(tp, 0.5), tp], [0.0065, 0.0055, 0.004], [0.006, 0.005, 0.0035], segs=6, res=2, up=(0, 0, 1)))
        for bmx in toes[-1:]:
            paint(bmx, lambda p, n: hex_rgb('#d9b52b'))
        cl = loft([tp, tp + d * 0.012 + V(0, 0, -0.008), tp + d * 0.018 + V(0, 0, -0.022)], [0.004, 0.003, 0.0008], [0.004, 0.003, 0.0008], segs=6, res=2, up=(1, 0, 0))
        paint(cl, lambda p, n: hex_rgb('#14120f'))
        toes.append(cl)
    d = V(0, -0.9, -0.25).normalized(); tp = ank + d * 0.035
    toes.append(loft([ank, tp], [0.006, 0.004], [0.006, 0.004], segs=6, res=2, up=(0, 0, 1)))
    paint(toes[-1], lambda p, n: hex_rgb('#d9b52b'))
    foot = part('foot_' + nm, merge(*toes), [talonm], ank, parent=up)
    legs += [up, foot]

allp = [body, head, beak_l, tail] + rig.objs + legs
meta = {'species': 'Buzzard / red-tailed-style hawk, soaring (wings authored fully spread)', 'forward': '-Y', 'left': '+X',
        'origin': 'below body centre; body centre at z=0.13 (origin at belly level for placement in sky)',
        'scale_hint_m': {'wingspan': 1.3, 'body_length': 0.5, 'tail_length': 0.26},
        'parts': {'root': 'body', 'head': 'head', 'beak_lower': 'beak_lower', 'tail': 'tail',
                  'wing_l': ['wing_l_upper', 'wing_l_fore', 'wing_l_hand'], 'wing_r': ['wing_r_upper', 'wing_r_fore', 'wing_r_hand'], 'legs': {'leg_l': 'foot_l', 'leg_r': 'foot_r'}},
        'hierarchy': {'body': ['head', 'tail', 'wing_*_upper', 'leg_*'], 'head': ['beak_lower'], 'wing_*_upper': ['wing_*_fore'], 'wing_*_fore': ['wing_*_hand'], 'leg_*': ['foot_*']},
        'rest_pose': 'wings fully SPREAD in the XY plane (soaring). Flap axis: rotate wing_*_upper about blender Y (length axis) = three.js Z; left wing up = negative? (rotate left wing by -a about Y to raise tip). Wing tips: also rotate wing_*_fore/hand about Y by a*0.6/1.0 for phase lag.',
        'soar': {'bank_deg': [-20, 20], 'tail_fan_deg': 10, 'tail_pitch_deg': 6, 'wing_tip_dihedral_deg': 6},
        'flap': {'cycle_s': 0.9, 'upper_deg': [-35, 45], 'fore_deg': [-20, 25], 'hand_deg': [-10, 35], 'note': 'rotations about Y blender (three.js Z); phase lag 0.1 cycle per segment'},
        'wing_fold_pose': fold_meta(FQ),
        'wing_fold_note': 'local quaternions (xyzw three.js) per segment to fold the wing against the body (slerp from identity).',
        'idle': {'head_turn_deg': 40, 'tail_tilt_deg': 8}}
print(export_bundle(OUT_DIR + '/hawk.json', allp, meta))
write_meta('hawk', meta)
print('tris', tri_count(allp))
if POSE == 'fold':
    apply_quats(FQ)
if PREVIEW:
    preview_grid(PREVIEW_DIR + '/hawk%s.png' % ('_fold' if POSE == 'fold' else ''),
                 [((0, -1.6, 0.9), (0, 0, 0.1), 50), ((0, 0.1, 2.2), (0, 0, 0.1), 50), ((0.5, -0.9, 0.35), (0, -0.2, 0.15), 70), ((-1.3, 1.3, 0.6), (0, 0, 0.1), 50)],
                 target=(0, 0, 0.1), ground=False, bg=(0.45, 0.62, 0.85))
