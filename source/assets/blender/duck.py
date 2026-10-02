import sys
sys.path.insert(0, '/shared/river/assets/blender')
from birdlib import *

PREVIEW = os.environ.get('PREVIEW', '1') == '1'
POSE = os.environ.get('POSE', '')
reset_scene()

plum = vcol_mat('mallard_body_plumage', '#ffffff', rough=0.75)
irid = vcol_mat('mallard_head_iridescent', '#ffffff', rough=0.35, metal=0.12)
feath = vcol_mat('mallard_flight_feathers', '#ffffff', rough=0.68)
billm = vcol_mat('bill_yellow', '#ffffff', rough=0.4)
eyem = make_mat('eye', '#140a04', rough=0.05)
pupilm = make_mat('pupil', '#000000', rough=0.08)
feetm = vcol_mat('feet_orange', '#ffffff', rough=0.55)

CHEST = '#6a3628'; GREY = '#c2beb5'; BACK = '#9a8e79'; BLACKC = '#171a1c'; WHITE = '#f2f0ea'
GREEN = '#1f8a48'; BLUEG = '#1f6e8c'


def vermic(p, base, amt=0.22):
    v = fbm(V(p.x * 1.0, p.y * 1.0, p.z * 3.0), 260, 2, 3)
    return mulc(base, 1.0 - amt * (v * 0.5 + 0.5))


def bodycol(p, n):
    top = sstep(0.2, 0.9, n.z)
    c = mixc(GREY, vermic(p, BACK, 0.3), top * sstep(-0.12, -0.02, p.y) * 0.95)
    c = mixc(c, vermic(p, GREY, 0.35), (1 - top) * sstep(-0.12, -0.02, p.y))
    # chest (front)
    ch = 1 - sstep(-0.185, -0.135, p.y)
    c = mixc(c, CHEST, ch)
    # white band between chest and grey
    c = mixc(c, WHITE, max(0, 1 - abs(p.y + 0.128) / 0.02) * 0.8)
    # black tail end
    bl = sstep(0.19, 0.23, p.y)
    c = mixc(c, BLACKC, bl)
    # white flank stripe below wing
    return mulc(c, 0.95 + 0.1 * (fbm(p, 90, 2, 5) * 0.5 + 0.5))


# ---------------- body
pts = [V(0, -0.255, 0.098), V(0, -0.20, 0.090), V(0, -0.11, 0.075), V(0, 0.02, 0.070), V(0, 0.14, 0.082), V(0, 0.23, 0.112), V(0, 0.285, 0.14)]
rx = [0.03, 0.078, 0.108, 0.113, 0.092, 0.042, 0.010]
rz = [0.04, 0.078, 0.092, 0.092, 0.078, 0.042, 0.012]
bb = loft(pts, rx, rz, segs=32, res=5)
bb = merge(bb, blob(V(0, -0.15, 0.085), (0.075, 0.09, 0.075)))
bb = fuse(bb, voxel=0.0082, smooth_iter=10)
paint(bb, bodycol)
body = part('body', bb, [plum], V(0, 0, 0.08), noise=dict(amp=0.0012, freq=120, seed=2))

# ---------------- neck (green above the collar)
NP = V(0, -0.15, 0.115)
np_ = [V(0, -0.11, 0.10), V(0, -0.15, 0.125), V(0, -0.195, 0.175), V(0, -0.215, 0.23), V(0, -0.225, 0.28)]
nb = loft(np_, [0.05, 0.045, 0.033, 0.027, 0.025], [0.05, 0.045, 0.033, 0.027, 0.025], segs=20, res=5)
for f in nb.faces:
    z = sum(v.co.z for v in f.verts) / len(f.verts)
    f.material_index = 1 if z > 0.218 else 0


def neckcol(p, n):
    if p.z > 0.218:
        return mixc(GREEN, BLUEG, sstep(0.0, 1.0, n.x * n.y * -3 + 0.3) * 0.5)
    c = mixc(CHEST, WHITE, sstep(0.2, 0.215, p.z) * 0.0)
    c = mixc(CHEST, WHITE, 1 - min(1, abs(p.z - 0.208) / 0.012))
    return c if p.z > 0.15 else mixc(CHEST, vermic(p, GREY), 0.0)


paint(nb, neckcol)
neck = part('neck', nb, [plum, irid], NP, parent=body, noise=dict(amp=0.0008, freq=150, seed=3))

# ---------------- head
HP = V(0, -0.225, 0.275)
hd = blob(V(0, -0.236, 0.292), (0.03, 0.043, 0.031), segs=24, rings=16)
hd = merge(hd, blob(V(0, -0.255, 0.284), (0.022, 0.03, 0.022)), blob(V(0, -0.228, 0.285), (0.032, 0.03, 0.028)))
hd = fuse(hd, voxel=0.0028, smooth_iter=6)


def headcol(p, n):
    return mixc(GREEN, BLUEG, sstep(-0.2, 0.9, n.x * 1.0 * (1 if p.x > 0 else -1) * 0 + (-n.y) * 0.6 + n.z * 0.4) * 0.6)


paint(hd, headcol)
for f in hd.faces:
    f.material_index = 0
bill = loft([V(0, -0.262, 0.290), V(0, -0.29, 0.285), V(0, -0.32, 0.279), V(0, -0.349, 0.272)], [0.0165, 0.0185, 0.0195, 0.0165], [0.0135, 0.0105, 0.0085, 0.0055], segs=16, res=4, cap_push=0.5)
set_mat_index(bill, 2)


def billcol(p, n):
    c = mixc('#b9b534', '#d6cf44', sstep(-0.27, -0.33, p.y))
    c = mixc(c, '#1c1a14', sstep(-0.338, -0.349, p.y))
    # nostril streak
    return c


paint(bill, billcol)
eyes = eye_pair(None, (0.0245, -0.247, 0.3), 0.0062)
for b in eyes:
    paint(b, lambda p, n: (1, 1, 1))
head = part('head', merge(hd, bill, *eyes), [irid, eyem, billm, pupilm][:0] + [irid, eyem, billm, pupilm], HP, parent=neck)
jaw = loft([V(0, -0.262, 0.279), V(0, -0.29, 0.276), V(0, -0.32, 0.272), V(0, -0.343, 0.268)], [0.0145, 0.0175, 0.018, 0.0145], [0.0062, 0.0055, 0.0045, 0.0032], segs=14, res=4, cap_push=0.5)
paint(jaw, lambda p, n: mixc('#b7b234', '#1c1a14', sstep(-0.335, -0.343, p.y)))
bill_l = part('bill_lower', jaw, [billm], V(0, -0.255, 0.282), parent=head)

# ---------------- tail
TP = V(0, 0.235, 0.105)
tb = []
nt = 11
for i in range(nt):
    a = math.radians((i - (nt - 1) / 2) * 6.0)
    L = 0.092 - abs(i - (nt - 1) / 2) * 0.004
    base = TP + V(0, 0, 0.0005 * i)
    tip = base + V(math.sin(a) * L, math.cos(a) * L, 0.035)
    tb.append(feather(base, tip, 0.016, lambda t, lat: mixc('#c8c4ba', '#eeece6', t), thick=0.0014, curve=(0, 0, 0.008)))
for sx in (1, -1):   # drake curl feathers
    cp = [TP + V(sx * 0.008, 0.02, 0.0), TP + V(sx * 0.014, 0.065, 0.02), TP + V(sx * 0.02, 0.085, 0.06), TP + V(sx * 0.014, 0.065, 0.085), TP + V(sx * 0.004, 0.045, 0.07)]
    c = loft(cp, [0.007, 0.0075, 0.007, 0.005, 0.0012], [0.0035, 0.0035, 0.003, 0.0025, 0.0012], segs=6, res=5, up=(1, 0, 0))
    paint(c, lambda p, n: hex_rgb('#14181a'))
    tb.append(c)
tail = part('tail', merge(*tb), [feath], TP, parent=body)


# ---------------- wings
def spec_col(i, n):
    def f(t, lat):
        if 2 <= i <= 8:
            c = hex_rgb('#26409c')
            c = mixc(c, '#0e1014', sstep(0.62, 0.70, t))
            c = mixc(c, WHITE, sstep(0.76, 0.82, t))
            c = mixc(c, '#b0a797', sstep(0.93, 1.0, t) * 0.6)
            return mulc(c, 1.0)
        return mixc('#7a6f5f', '#b7ae9f', sstep(0.7, 1.0, abs(lat)) * 0.5)
    return f


def build_wing():
    S = V(0.122, -0.075, 0.128)
    E = S + V(0.09, 0.01, 0)
    Wr = E + V(0.13, -0.02, 0)
    P = dict(S=S, E=E, Wr=Wr, bone=0.5, thick=0.0018, hand_len=V(0.06, -0.015, 0),
             n_up=9, up_len=0.085, up_w=0.03, up_col=lambda i: fcol('#8a7f6d', '#c9c0ae', dark=0.2),
             n_sec=11, sec_len=lambda t: 0.115 + 0.01 * math.sin(t * 2.5), sec_w=0.031, sec_col=spec_col,
             n_prim=10, prim_len=[0.13, 0.145, 0.16, 0.175, 0.185, 0.19, 0.188, 0.18, 0.168, 0.15], prim_w=0.022,
             prim_col=lambda j, n: fcol('#6a6052', '#a79d8b', dark=0.25), fan=(18, 6),
             pcov_col=lambda i: fcol('#7d7261', '#b5ac9a'),
             covers=[(0.05, 0.003, 11, 0.03, fcol('#8d816d', '#d3cab8')), (0.035, 0.006, 11, 0.026, fcol('#94897a', '#dad1bf')), (0.02, 0.009, 11, 0.022, fcol('#9b907f', '#e2dac8'))])
    return build_wing_bms(P), dict(upper=S, fore=E, hand=Wr)


rig = WingRig()
bm_l, PIV = build_wing()
rig.make('wing_l', 1, bm_l, PIV, std_fold(), body, [feath])
bm_r, PIV = build_wing()
rig.make('wing_r', -1, bm_r, PIV, std_fold(), body, [feath])

# ---------------- legs (mostly submerged)
legs = []
for sx, nm in ((1, 'l'), (-1, 'r')):
    hip = V(sx * 0.05, 0.05, 0.05); ank = V(sx * 0.055, 0.06, -0.075)
    th = loft([hip + V(0, 0, 0.03), hip, hip.lerp(ank, 0.45), ank], [0.028, 0.022, 0.012, 0.008], [0.035, 0.028, 0.013, 0.007], segs=12, res=4, up=(0, -1, 0))
    paint(th, lambda p, n: mixc(GREY, '#e08a2c', sstep(0.0, -0.03, p.z)))
    leg = part('leg_' + nm, th, [feetm], hip, parent=body)
    toes = []
    for ang in (-28, 0, 28):
        a = math.radians(ang)
        d = V(math.sin(a) * sx, -math.cos(a), -0.03)
        tp = ank + d * 0.075
        toes.append(loft([ank, ank.lerp(tp, 0.5), tp], [0.0075, 0.006, 0.005], [0.005, 0.004, 0.003], segs=6, res=2, up=(0, 0, 1)))
    # web
    web = bmesh.new()
    va = web.verts.new(ank + V(0, 0, 0.0))
    vl = web.verts.new(ank + V(math.sin(math.radians(-28)) * sx, -math.cos(math.radians(-28)), -0.03) * 0.072)
    vm = web.verts.new(ank + V(0, -1, -0.03) * 0.078)
    vr = web.verts.new(ank + V(math.sin(math.radians(28)) * sx, -math.cos(math.radians(28)), -0.03) * 0.072)
    for tri in ((va, vl, vm), (va, vm, vr)):
        web.faces.new(tri)
    sol = bmesh.ops.solidify(web, geom=web.faces[:], thickness=0.0015)
    bmesh.ops.recalc_face_normals(web, faces=web.faces[:])
    toes.append(web)
    for t_ in toes:
        paint(t_, lambda p, n: hex_rgb('#e0852a'))
    foot = part('foot_' + nm, merge(*toes), [feetm], ank, parent=leg)
    legs += [leg, foot]

allp = [body, neck, head, bill_l, tail] + rig.objs + legs
meta = {'species': 'Mallard drake (Anas platyrhynchos), floating', 'forward': '-Y', 'left': '+X', 'origin': 'waterline under body centre (z=0 is water surface)',
        'scale_hint_m': {'length': 0.58, 'wingspan_open': 0.95, 'head_top_above_water': 0.32, 'body_width': 0.23},
        'parts': {'root': 'body', 'neck': 'neck', 'head': 'head', 'bill_lower': 'bill_lower', 'tail': 'tail',
                  'wing_l': ['wing_l_upper', 'wing_l_fore', 'wing_l_hand'], 'wing_r': ['wing_r_upper', 'wing_r_fore', 'wing_r_hand'],
                  'legs': {'leg_l': 'foot_l', 'leg_r': 'foot_r'}},
        'hierarchy': {'body': ['neck', 'tail', 'wing_*_upper', 'leg_*'], 'neck': ['head'], 'head': ['bill_lower'], 'wing_*_upper': ['wing_*_fore'], 'wing_*_fore': ['wing_*_hand'], 'leg_*': ['foot_*']},
        'rest_pose': 'wings FOLDED on the flanks (fold authored in geometry). legs hang below waterline (feet at z~-0.075) - hide or keep under water; paddling = rotate leg_* about X +-30deg, foot_* about X.',
        'standing': 'to stand on land lift the whole asset by 0.14 m (ankle z=-0.075, toes ~ -0.11 below origin)',
        'wing_open_pose': wing_meta(rig),
        'wing_open_note': 'per-segment local rotation quaternion (xyzw, three.js coords) that fully spreads the wing (span along +-X, dorsal up). slerp from identity (folded). Flap: rotate wing_*_upper about three.js Z (blender Y) after open.',
        'idle': {'neck_s_bob_deg': 6, 'head_dip_deg': 70, 'note': 'dabbling: rotate neck about X +70deg (head down, tail up by tilting body -X 25deg)', 'tail_wag_deg': 15, 'bill_open_deg': 10},
        'swim': {'bob_amp_m': 0.006, 'wake': 'body rocks +-2deg roll'}}
print(export_bundle(OUT_DIR + '/duck.json', allp, meta))
write_meta('duck', meta)
print('tris', tri_count(allp))
if POSE == 'open':
    apply_open(rig)
if PREVIEW:
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0)); bpy.context.object.data.materials.append(make_mat('_water', '#3d6b78', rough=0.2))
    preview_grid(PREVIEW_DIR + '/duck%s.png' % ('_open' if POSE == 'open' else ''),
                 [((1.3, 0, 0.3), (0, 0, 0.12), 50), ((0.8, -1.0, 0.5), (0, 0, 0.12), 50), ((0.35, -0.75, 0.42), (0, -0.23, 0.28), 60), ((-0.9, 1.0, 0.7), (0, 0, 0.1), 50)],
                 target=(0, 0, 0.1), ground=False, bg=(0.55, 0.65, 0.8))
