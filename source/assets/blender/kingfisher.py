import sys
sys.path.insert(0, '/shared/river/assets/blender')
from birdlib import *

PREVIEW = os.environ.get('PREVIEW', '1') == '1'
POSE = os.environ.get('POSE', '')
reset_scene()

plum = vcol_mat('kingfisher_plumage', '#ffffff', rough=0.72)
eyem = make_mat('eye', '#0c0705', rough=0.05)
pupilm = make_mat('pupil', '#000000', rough=0.08)
beakm = vcol_mat('beak_horn', '#ffffff', rough=0.35)
legm = make_mat('legs_skin', '#8c6e5b', rough=0.55)
feath = vcol_mat('kingfisher_flight_feathers', '#ffffff', rough=0.68)

OLIVE = '#2f8fb5'
ORANGE = '#e8742a'
WHITE = '#efe9da'
GREYB = '#8d8f88'
WINGB = '#2a7ea3'


def sstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def plumage(p, n):
    c = mixc('#2f86b0', '#3fb3b5', 0.5 * (fbm(p, 150, 2, 1) * .5 + .5))
    c = mixc(c, '#3aa89e', sstep(0.3, 1.0, n.z) * 0.5)
    orange = max(sstep(0.35, -0.2, n.z), sstep(-0.2, -0.6, n.y)) * sstep(-0.025, -0.045, -p.y - 0.0) 
    orange = max(sstep(0.25, -0.25, n.z), sstep(-0.3, -0.7, n.y)) * sstep(0.058, 0.03, p.y)
    c = mixc(c, ORANGE, orange)
    c = mixc(c, '#f3eee0', max(0, 1 - (V(0, p.y, p.z) - V(0, -0.04, 0.085)).length / 0.012) * sstep(-0.3, -0.8, n.y) * 0.0)
    d = sub_noise.voronoi(p * 300)[0][0]
    return mulc(c, 0.92 + 0.1 * (1 - min(1, d * 1.3)))


# ---------------- body
body_pts = [V(0, -0.038, 0.090), V(0, -0.022, 0.087), V(0, 0.004, 0.080), V(0, 0.030, 0.073), V(0, 0.050, 0.068), V(0, 0.058, 0.066)]
bb = loft(body_pts, [0.014, 0.024, 0.026, 0.020, 0.010, 0.004], [0.018, 0.029, 0.031, 0.023, 0.012, 0.005], segs=24, res=4)
bb = merge(bb, blob(V(0, -0.028, 0.102), (0.016, 0.02, 0.016)))   # neck base
bb = fuse(bb, voxel=0.0016, smooth_iter=8)
paint(bb, plumage)
body = part('body', bb, [plum], V(0, 0.0, 0.07), noise=dict(amp=0.0004, freq=300, seed=1))

# ---------------- head
HP = V(0, -0.034, 0.100)
hd = blob(V(0, -0.047, 0.112), (0.0195, 0.0225, 0.0195), segs=24, rings=16)
hd = merge(hd, blob(V(0, -0.058, 0.108), (0.011, 0.012, 0.011)))
hd = fuse(hd, voxel=0.0011, smooth_iter=6)


def headcol(p, n):
    c = mixc('#2d8fb4', '#2aa59b', 0.4 * (fbm(p, 200, 2, 3) * .5 + .5))
    c = mixc(c, '#e8742a', sstep(-0.045, -0.06, p.y) * sstep(0.1, 0.0, (p.z - 0.112) * 0 + (0.108 - p.z)) * 0.0)
    # orange ear patch and white neck patch
    c = mixc(c, '#e8742a', max(0, 1 - (V(abs(p.x), p.y, p.z) - V(0.0155, -0.049, 0.108)).length / 0.012))
    c = mixc(c, '#f3eee0', max(0, 1 - (V(abs(p.x), p.y, p.z) - V(0.013, -0.04, 0.098)).length / 0.009))
    c = mixc(c, '#f0ead8', sstep(-0.7, -1.0, n.z) * 0.6)
    return c


paint(hd, headcol)
up_beak = loft([V(0, -0.0575, 0.109), V(0, -0.0775, 0.1085), V(0, -0.098, 0.106)], [0.0066, 0.0038, 0.0008], [0.0062, 0.0036, 0.0010], segs=10, res=3, cap_push=0.8)
set_mat_index(up_beak, 2)
paint(up_beak, lambda p, n: hex_rgb('#15120f'))
eyes = eye_pair(None, (0.0145, -0.0525, 0.1165), 0.0052)
for b in eyes:
    paint(b, lambda p, n: (1, 1, 1))
head = part('head', merge(hd, up_beak, *eyes), [plum, eyem, beakm, pupilm], HP)
lb = loft([V(0, -0.0575, 0.1035), V(0, -0.078, 0.1025), V(0, -0.094, 0.1025)], [0.0054, 0.0032, 0.0008], [0.0040, 0.0028, 0.0008], segs=10, res=3, cap_push=0.8)
paint(lb, lambda p, n: mixc('#d86a30', '#15120f', sstep(-0.065, -0.085, p.y)))
beak_l = part('beak_lower', lb, [beakm], V(0, -0.0565, 0.1035), parent=head)

# ---------------- tail
TP = V(0, 0.048, 0.069)
tb = []
nt = 10
for i in range(nt):
    a = math.radians((i - (nt - 1) / 2) * 2.6)
    L = 0.036 - abs(i - (nt - 1) / 2) * 0.0008
    tip = TP + V(math.sin(a) * L, math.cos(a) * L, -0.012 - abs(math.sin(a)) * 0.0)
    tb.append(feather(TP + V(0, 0, 0.0005 * i), tip, 0.0105, lambda t, lat: mixc('#2a7ea3', '#1c5f7d', t * 0.6), thick=0.0008, curve=(0, 0, 0.0015)))
tail = part('tail', merge(*tb), [feath], TP, parent=body)


# ---------------- wings (open-pose geometry, then folded)
def fcol(base, edge='#b59a70', dark=0.0):
    def f(t, lat):
        c = mixc(base, edge, sstep(0.72, 1.0, abs(lat)) * 0.7)
        return mulc(c, 1.0 - dark * t)
    return f


def build_wing():
    up_parts = [loft([S - V(0.006, 0, 0), S, E], [0.0045, 0.005, 0.0035], [0.004, 0.0045, 0.0032], segs=10, res=3, up=(0, 0, 1))]
    paint(up_parts[0], lambda p, n: hex_rgb('#2a6f90'))
    for i in range(9):
        t = i / 8
        b = S.lerp(E, t) + V(0, 0.002, 0.002 + 0.0006 * (i % 3))
        up_parts.append(feather(b, b + V(0.004, 0.034 - 0.002 * (i % 4), -0.004), 0.010, fcol('#2b86ad', dark=0.2), thick=0.001, normal=(0, 0, 1)))
    fore_parts = [loft([E, E.lerp(Wr, 0.5), Wr], [0.0038, 0.0035, 0.003], [0.0034, 0.0032, 0.003], segs=8, res=3)]
    paint(fore_parts[0], lambda p, n: hex_rgb('#2a6f90'))
    nsec = 7
    for i in range(nsec):
        t = i / (nsec - 1)
        b = E.lerp(Wr, t) + V(0, 0.003, -0.001 * i)
        L = 0.046 + 0.004 * math.sin(t * 2.5)
        a = math.radians(-6 + 4 * (1 - t))
        fore_parts.append(feather(b, b + V(math.sin(a) * L, math.cos(a) * L, -0.006), 0.0115, fcol('#2a7ea3', '#2a9a9a', dark=0.25), thick=0.0009))
    for row, (ln, dz, cnt) in enumerate(((0.024, 0.0012, 7), (0.016, 0.0024, 7), (0.010, 0.0036, 7))):
        for i in range(cnt):
            t = i / (cnt - 1)
            b = E.lerp(Wr, t) + V(0, -0.002 + row * 0.0, dz)
            fore_parts.append(feather(b, b + V(0.0, ln, dz * 0.4), 0.0095 - row * 0.001, fcol('#2d97a8' if row else '#2b86ad', '#3fb3b5'), thick=0.0008))
    hand_parts = [loft([Wr, Wr + V(0.012, -0.004, 0), Wr + V(0.022, -0.008, 0)], [0.0042, 0.0035, 0.002], [0.0038, 0.003, 0.002], segs=8, res=3)]
    paint(hand_parts[0], lambda p, n: hex_rgb('#26607a'))
    npr = 9
    for j in range(npr):
        t = j / (npr - 1)
        phi = math.radians(16 - 10 * t)
        L = [0.050, 0.056, 0.062, 0.066, 0.067, 0.066, 0.063, 0.058, 0.052][j] * 1.0
        b = Wr + V(0.0025 * (npr - j) * 0.35 + 0.006 * (1 - t) * 0, -0.0012 * (npr - j) * 0.3 + 0.003, -0.0008 * j)
        hand_parts.append(feather(b, b + V(math.cos(phi) * L, math.sin(phi) * L, -0.003), 0.0092, fcol('#2a5f7a', '#3a7d94', dark=0.35), thick=0.0008, bulge=0.3))
    for i in range(6):
        t = i / 5
        phi = math.radians(45 - 35 * t)
        b = Wr + V(0.003, 0.0, 0.0015 + 0.0005 * i)
        hand_parts.append(feather(b, b + V(math.cos(phi) * 0.026, math.sin(phi) * 0.026, 0), 0.008, fcol('#2b86ad', '#3fb3b5'), thick=0.0008))
    hand_parts.append(feather(Wr + V(0.0, -0.002, 0.002), Wr + V(0.013, -0.006, 0.002), 0.004, fcol('#5a4a35', '#8a7a5a'), thick=0.0006))

    return {'upper': merge(*up_parts), 'fore': merge(*fore_parts), 'hand': merge(*hand_parts)}


S = V(0.029, -0.012, 0.088); E = V(0.055, -0.002, 0.088); Wr = V(0.081, -0.016, 0.088)
W = {'upper': cyc_fold((0, 1, -0.05), (-1, 0, 0)),
     'fore': cyc_fold((0, -1, -0.10), (1, 0, 0)),
     'hand': cyc_fold((0, 1, -0.22), (-1, 0, 0))}
rig = WingRig()
PIV = {'upper': S, 'fore': E, 'hand': Wr}
wl = rig.make('wing_l', 1, build_wing(), PIV, W, body, [feath])
wr = rig.make('wing_r', -1, build_wing(), PIV, W, body, [feath])

# ---------------- legs
legs = []
for sx, nm in ((1, 'l'), (-1, 'r')):
    hip = V(sx * 0.013, 0.004, 0.066); ank = V(sx * 0.0145, -0.003, 0.0235)
    th = loft([hip + V(0, 0, 0.008), hip, hip.lerp(ank, 0.3)], [0.0062, 0.0045, 0.0024], [0.0062, 0.0048, 0.0026], segs=10, res=3)
    ts = loft([hip.lerp(ank, 0.3), hip.lerp(ank, 0.65), ank], [0.0022, 0.0017, 0.0019], [0.0022, 0.0017, 0.0019], segs=8, res=3, up=(0, -1, 0))
    paint(th, plumage); paint(ts, lambda p, n: hex_rgb('#d8552e'))
    leg = part('leg_' + nm, merge(th, ts), [plum], hip, parent=body)
    toes = []
    for dv, ln in (((0.35, -1, 0), 0.017), ((-0.35, -1, 0), 0.017), ((0.0, -1, 0), 0.019), ((0, 1, 0), 0.013)):
        tb_ = toe(ank, V(dv[0] * sx, dv[1], -0.22), ln, 0.0013)
        paint(tb_, lambda p, n: hex_rgb('#d8552e'))
        toes.append(tb_)
    foot = part('foot_' + nm, merge(*toes), [plum], ank, parent=leg)
    legs += [leg, foot]

body.location.z -= 0.012
bpy.context.view_layer.update()
allp = [body, head, beak_l, tail] + rig.objs + legs
meta = {'species': 'Common kingfisher (Alcedo atthis), perched', 'forward': '-Y', 'left': '+X',
        'scale_hint_m': {'length': 0.165, 'height_perched': 0.12, 'wingspan_open': 0.25},
        'parts': {'root': 'body', 'head': 'head', 'beak_lower': 'beak_lower', 'tail': 'tail',
                  'wing_l': ['wing_l_upper', 'wing_l_fore', 'wing_l_hand'], 'wing_r': ['wing_r_upper', 'wing_r_fore', 'wing_r_hand'],
                  'legs': {'leg_l': 'foot_l', 'leg_r': 'foot_r'}},
        'hierarchy': {'body': ['head', 'tail', 'wing_*_upper', 'leg_*'], 'head': ['beak_lower'], 'wing_*_upper': ['wing_*_fore'], 'wing_*_fore': ['wing_*_hand'], 'leg_*': ['foot_*']},
        'rest_pose': 'wings FOLDED against body (Z-fold authored into geometry). Rotations are applied to parts at runtime.',
        'wing_open_pose': wing_meta(rig),
        'wing_open_note': 'Set each wing part local rotation (quaternion xyzw in three.js coords, or blender euler XYZ deg) to fully open the wing (span along +-X, dorsal up). Blend linearly (slerp) between identity (folded) and this quaternion per segment. Flapping: then rotate wing_*_upper about the body Y axis (blender) = Z axis three.js, +-35deg (left wing raise = rotate by -angle about blender Y... verify sign) after open quat.',
        'idle': {'head_turn_deg': 35, 'head_bob_deg': 8, 'tail_bob_deg': 10, 'beak_open_deg': 12, 'jaw': 'beak_lower rotate about X'},
        'hop': {'legs': 'rotate leg_* about X +-25deg; feet compensate'}}
print(export_bundle(OUT_DIR + '/kingfisher.json', allp, meta))
write_meta('kingfisher', meta)
print('tris', tri_count(allp))
if POSE == 'open':
    apply_open(rig)
if PREVIEW:
    preview_grid(PREVIEW_DIR + '/kingfisher%s.png' % ('_open' if POSE == 'open' else ''),
                 [((0.30, 0, 0.09), (0, 0.0, 0.07), 50), ((0.3, -0.3, 0.17), (0, 0.0, 0.07), 50), ((0.1, -0.20, 0.14), (0, -0.05, 0.105), 50), ((0, 0.4, 0.3), (0, 0, 0.06), 50)],
                 target=(0, 0, 0.08))
