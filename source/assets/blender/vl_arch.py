import sys
sys.path.insert(0, '/shared/river/assets/blender')
from vl_chars import *


def common_legs(c, B, **kw):
    for s in (1, -1):
        leg_parts(c, s, B, **kw)


def head_add(c, B, bm, part='neck_head'):
    B[part].append(place_head(c, bm))


def face_basics(c, B, brow=None, lipkw=None):
    head_add(c, B, X.brows(c, **(brow or {})))
    lh, lj = X.lips(c, **(lipkw or {}))
    head_add(c, B, lh); head_add(c, B, lj, 'jaw')


def side_hair(c, B, line, thick=0.011, top_extra=0.006, seed=2, clump=0.5, mat='hair', **kw):
    head_add(c, B, X.hair_cap(c, line, thick=thick, top_extra=top_extra, seed=seed, clump=clump, mat=mat, **kw))


SHORT_LINE = [(0, .060), (35, .052), (60, .042), (85, .034), (100, .028), (115, 0.0), (140, -.04), (180, -.062)]


# ---------------------------------------------------------------- MAN (worker)
def man_garments(c, B):
    B['torso'].append(setm(shirt_shell(c), 'cloth_main'))
    B['torso'].append(setm(collar(c), 'cloth_main'))
    B['torso'].append(chest_skin(c))
    B['torso'].append(setm(vest_shell(c), 'cloth_accent'))
    for z in np.linspace(c.z['waist'] + 0.02, c.rz[6] - 0.04, 4):
        B['torso'].append(button(front_pos(c, z, 0.034), 0.0075, 'brass'))
    B['torso'].append(belt(c, z=c.z['waist'] - 0.035))
    B['torso'].append(pouch(c, c.z['waist'] - 0.06, c.sw * 0.95 + 0.075, angle=0.0, side=True))
    B['pelvis'].append(trousers_pelvis(c))
    for s in (1, -1):
        arm_parts(c, s, B, sleeve='rolled')
    common_legs(c, B, legwear='trousers', shoes='boot')
    face_basics(c, B)
    side_hair(c, B, SHORT_LINE, thick=0.011, top_extra=0.007, seed=2)
    head_add(c, B, X.fringe(c))
    head_add(c, B, X.flat_cap(c, 'cloth_alt'))
    return {}


# ---------------------------------------------------------------- WOMAN
def woman_garments(c, B):
    sh = shirt_shell(c, z0=c.z['waist'] - 0.04, off=0.014)
    bust(sh, c, 0.011)
    B['torso'].append(setm(sh, 'cloth_main'))
    B['torso'].append(setm(collar(c, up=0.022, flare=0.006), 'cloth_main'))
    B['torso'].append(chest_skin(c))
    bd = vest_shell(c, z0=c.z['waist'] - 0.06, off=0.030, vopen=0.0, vdepth=1.0, th=0.006)
    bust(bd, c, 0.013)
    B['torso'].append(setm(bd, 'cloth_accent'))
    B['pelvis'].append(setm(skirt(c, c.z['ankle'] + 0.07, 0.34 * c.sc, 0.30 * c.sc, folds=11, amp=0.016), 'cloth_alt'))
    zw = c.z['waist'] - 0.01
    pb = panel(c, [(c.rz[5] + 0.0, 0.07), (c.rz[4], 0.075), (c.rz[3], 0.1), (zw, 0.138)], ysurf_torso(c), off=0.05, bow=0.0, mat='cloth_main', folds=0.0015, stitch=False)
    bust(pb, c, 0.014)
    B['torso'].append(pb)
    zb = c.z['knee'] - 0.1
    B['pelvis'].append(panel(c, [(zw, 0.138), (c.rz[1], 0.19), ((c.rz[1] + zb) / 2, 0.215), (zb, 0.24)], ysurf_lower(c), off=0.032, bow=0.012, mat='cloth_main', folds=0.006))
    B['torso'].append(suspenders(c, x_front=0.065, x_back=0.075, width=0.018, off=0.03))
    B['torso'].append(belt(c, z=zw, width=0.03, off=0.03, thick=0.006, buckle=False, mat='cloth_accent'))
    for s in (1, -1):
        arm_parts(c, s, B, sleeve='long')
    common_legs(c, B, legwear='none', shoes='shoe', thigh_cover='cloth_alt')
    face_basics(c, B, lipkw=dict(w=0.0175, up_h=0.0046, lo_h=0.0058))
    head_add(c, B, X.headscarf(c))
    for sg in (1, -1):
        head_add(c, B, X.lock([V(sg * 0.058, -0.052, 0.050), V(sg * 0.071, -0.040, 0.030), V(sg * 0.075, -0.022, 0.008)], 0.009, 0.0025, segs=5, res=2))
    return {}



def child_face(**kw):
    d = dict(W=0.083, Df=0.093, Db=0.104, jaw=0.36, brow=0.45, nose=0.62, nose_w=0.85, lip=1.15, chin=0.55, cheek=1.7, ear=1.0, eye_z=-0.012, eye_x=0.034)
    d.update(kw)
    return default_face(**d)


# ---------------------------------------------------------------- ELDER MAN
def elder_m_garments(c, B):
    B['torso'].append(setm(shirt_shell(c, z0=c.rz[1] - 0.06, off=0.013), 'cloth_accent'))
    B['torso'].append(setm(collar(c, open_v=True), 'cloth_accent'))
    B['torso'].append(chest_skin(c))
    cg = vest_shell(c, z0=c.rz[1] - 0.12, off=0.032, vopen=0.038, vdepth=0.0, th=0.007, seed=6, flare=0.012)
    B['torso'].append(setm(cg, 'cloth_main'))
    for z in np.linspace(c.z['waist'] - 0.07, c.rz[6] - 0.08, 4):
        B['torso'].append(button(front_pos(c, z, 0.043), 0.0085, 'wood'))
    B['torso'].append(belt(c, z=c.z['waist'] - 0.02, width=0.032, off=0.05, buckle=True))
    B['pelvis'].append(trousers_pelvis(c))
    for s in (1, -1):
        arm_parts(c, s, B, sleeve='long', sleeve_mat='cloth_main')
    common_legs(c, B, legwear='trousers', shoes='shoe')
    face_basics(c, B, brow=dict(width=0.0045, thick=0.0034, arch=0.005, z0=0.029, mat='hair'), lipkw=dict(w=0.017, up_h=0.0035, lo_h=0.0045))
    side_hair(c, B, [(0, .084), (30, .080), (60, .056), (85, .026), (105, -0.008), (140, -.05), (180, -.068)], thick=0.010, top_extra=0.0, seed=7, clump=0.7)
    hd, jw = X.facial_hair(c, 'beard', thick=0.013, length=0.05, seed=3)
    head_add(c, B, hd); head_add(c, B, jw, 'jaw')
    head_add(c, B, X.beard_locks(c, n=5, length=0.06, seed=3, width=0.025, r=0.012), 'jaw')
    for s in (1, -1):
        E = c.arms[s]['E']
        B['arm_%s_upper' % side_tag(s)].append(patch(V(E.x + s * 0.008, E.y + rad_arm(c, 'el') + 0.014, E.z + 0.015), 0.06, 0.07, 'leather', normal_y=1))
    G = grip_point(c, -1)
    return {'cane': (X.cane(c, G), G, 'hand_r')}


# ---------------------------------------------------------------- ELDER WOMAN
def elder_f_garments(c, B):
    sh = shirt_shell(c, z0=c.z['waist'] - 0.04, off=0.014)
    bust(sh, c, 0.012)
    B['torso'].append(setm(sh, 'cloth_main'))
    B['torso'].append(setm(collar(c, up=0.025, flare=0.006), 'cloth_main'))
    B['torso'].append(chest_skin(c))
    B['pelvis'].append(setm(skirt(c, c.z['ankle'] + 0.07, 0.30 * c.sc, 0.27 * c.sc, folds=10, amp=0.013, seed=5), 'cloth_main'))
    zw = c.z['waist'] - 0.01
    zb = c.z['knee'] - 0.14
    B['pelvis'].append(panel(c, [(zw, 0.13), (c.rz[1], 0.17), ((c.rz[1] + zb) / 2, 0.19), (zb, 0.21)], ysurf_lower(c), off=0.03, bow=0.01, mat='cloth_alt', folds=0.005, seed=3))
    B['torso'].append(shawl(c, drop_back=0.40, drop_side=0.26, drop_front=0.29, gap=0.14, off=0.034, color_mat='cloth_accent'))
    for s in (1, -1):
        arm_parts(c, s, B, sleeve='long')
    common_legs(c, B, legwear='none', shoes='shoe', sock='cloth_alt', thigh_cover='cloth_main')
    face_basics(c, B, brow=dict(width=0.003, thick=0.0024, arch=0.006, mat='hair'), lipkw=dict(w=0.016, up_h=0.0035, lo_h=0.0046))
    side_hair(c, B, [(0, .068), (35, .062), (60, .05), (85, .03), (105, 0.0), (140, -.05), (180, -.07)], thick=0.010, top_extra=0.004, seed=4, clump=0.4)
    # bun
    head_add(c, B, X.bun(V(0, 0.082, 0.045), 0.046))
    return {}


# ---------------------------------------------------------------- BOY
def boy_garments(c, B):
    B['torso'].append(setm(shirt_shell(c, z0=c.rz[1] - 0.02, off=0.011), 'cloth_main'))
    B['torso'].append(setm(collar(c, open_v=True, up=0.02, flare=0.008), 'cloth_main'))
    B['torso'].append(chest_skin(c))
    B['torso'].append(suspenders(c, x_front=0.065, x_back=0.06, width=0.022, off=0.022))
    for z in np.linspace(c.z['waist'] + 0.0, c.rz[6] - 0.03, 3):
        B['torso'].append(button(front_pos(c, z, 0.02), 0.0055, 'teeth'))
    B['pelvis'].append(trousers_pelvis(c))
    for s in (1, -1):
        arm_parts(c, s, B, sleeve='rolled')
    common_legs(c, B, legwear='shorts', shoes='shoe', sock='cloth_alt', shorts_len=0.62, trouser_mat='cloth_alt')
    face_basics(c, B, brow=dict(width=0.0028, thick=0.0022, arch=0.005, mat='hair'))
    side_hair(c, B, [(0, .056), (35, .050), (60, .040), (85, .03), (100, .02), (115, -0.01), (140, -.045), (180, -.065)], thick=0.011, top_extra=0.008, seed=8, clump=0.7)
    head_add(c, B, X.fringe(c, n=7, span=0.05, drop=0.018, r=0.0105, seed=9))
    head_add(c, B, X.flat_cap(c, 'cloth_accent'))
    return {}


# ---------------------------------------------------------------- GIRL
def girl_garments(c, B):
    sh = shirt_shell(c, z0=c.z['waist'] - 0.02, off=0.011)
    B['torso'].append(setm(sh, 'cloth_main'))
    B['torso'].append(setm(collar(c, open_v=False, up=0.02, flare=0.008), 'cloth_main'))
    B['torso'].append(chest_skin(c))
    B['pelvis'].append(setm(skirt(c, c.z['knee'] - 0.05, 0.22 * c.sc * 1.2, 0.20 * c.sc * 1.2, folds=9, amp=0.011, seed=3), 'cloth_main'))
    zw = c.z['waist'] - 0.01
    B['torso'].append(panel(c, [(c.rz[5], 0.06), (c.rz[4], 0.065), (c.rz[3], 0.085), (zw, 0.105)], ysurf_torso(c), off=0.028, bow=0.0, mat='cloth_alt', folds=0.0012))
    zb = c.z['knee'] - 0.1
    B['pelvis'].append(panel(c, [(zw, 0.105), (c.rz[1], 0.14), (zb, 0.17)], ysurf_lower(c), off=0.03, bow=0.01, mat='cloth_alt', folds=0.004))
    B['torso'].append(suspenders(c, x_front=0.055, x_back=0.055, width=0.016, off=0.028, mat='cloth_alt'))
    B['torso'].append(belt(c, z=zw, width=0.026, off=0.03, thick=0.005, buckle=False, mat='cloth_accent'))
    for s in (1, -1):
        arm_parts(c, s, B, sleeve='short')
    common_legs(c, B, legwear='none', shoes='shoe', sock='cloth_main', thigh_cover='cloth_main')
    face_basics(c, B, brow=dict(width=0.0026, thick=0.002, arch=0.005, mat='hair'))
    side_hair(c, B, [(0, .058), (35, .056), (60, .044), (85, .032), (105, 0.0), (140, -.04), (180, -.06)], thick=0.010, top_extra=0.005, seed=9, clump=0.4)
    head_add(c, B, X.fringe(c, n=7, span=0.04, drop=0.012, r=0.009, seed=2))
    # pigtails with ribbons
    for sg in (1, -1):
        base = V(sg * 0.074, 0.02, 0.005)
        pts = [base + V(sg * 0.004, 0.0, 0.0), base + V(sg * 0.026, 0.01, -0.03), base + V(sg * 0.036, 0.016, -0.085), base + V(sg * 0.032, 0.02, -0.15), base + V(sg * 0.026, 0.02, -0.19)]
        head_add(c, B, X.lock(pts, 0.019, 0.004, segs=8, res=3))
        rb = blob(base + V(sg * 0.026, 0.01, -0.03), (0.014, 0.014, 0.012), segs=8, rings=5)
        head_add(c, B, setm(rb, 'cloth_accent'))
        for sg2 in (1, -1):
            bw = blob(base + V(sg * 0.026 + sg2 * 0.013, 0.012, -0.03), (0.011, 0.005, 0.0075), rot=(0, sg2 * 0.4, 0), segs=8, rings=5)
            head_add(c, B, setm(bw, 'cloth_accent'))
    return {}


# ---------------------------------------------------------------- SMITH
def smith_garments(c, B):
    B['torso'].append(setm(shirt_shell(c, z0=c.rz[1] - 0.03, off=0.014), 'cloth_main'))
    B['torso'].append(setm(collar(c, open_v=True), 'cloth_main'))
    B['torso'].append(chest_skin(c))
    zw = c.z['waist'] - 0.02
    B['torso'].append(panel(c, [(c.rz[6] - 0.02, 0.085), (c.rz[5], 0.095), (c.rz[4], 0.13), (c.rz[3], 0.15), (zw, 0.16)], ysurf_torso(c), off=0.045, bow=0.0, mat='leather', th=0.006, folds=0.002))
    B['torso'].append(suspenders(c, x_front=0.085, x_back=0.09, width=0.026, off=0.04, mat='leather'))
    B['torso'].append(belt(c, z=zw, width=0.05, off=0.058, thick=0.008, buckle=True))
    zb = c.z['knee'] - 0.04
    B['pelvis'].append(panel(c, [(zw, 0.16), (c.rz[1], 0.2), ((c.rz[1] + zb) / 2, 0.215), (zb, 0.225)], ysurf_lower(c), off=0.026, bow=0.012, mat='leather', th=0.006, folds=0.004, seed=5))
    B['pelvis'].append(trousers_pelvis(c))
    B['torso'].append(pouch(c, c.z['waist'] - 0.07, c.sw * 1.05 + 0.10, angle=0.0, w=0.07, h=0.08, side=True))
    for s in (1, -1):
        arm_parts(c, s, B, sleeve='rolled', forearm_scale=1.2)
    common_legs(c, B, legwear='trousers', shoes='boot')
    face_basics(c, B, brow=dict(width=0.0042, thick=0.003, arch=0.004, mat='hair'))
    side_hair(c, B, SHORT_LINE, thick=0.009, top_extra=0.004, seed=11, clump=0.6)
    hd, jw = X.facial_hair(c, 'beard', thick=0.011, length=0.025, seed=6)
    head_add(c, B, hd); head_add(c, B, jw, 'jaw')
    G = grip_point(c, -1)
    return {'tool_hammer': (X.hammer(c, G), G, 'hand_r')}


# ---------------------------------------------------------------- BAKER
def baker_garments(c, B):
    B['torso'].append(setm(shirt_shell(c, z0=c.rz[1] - 0.03, off=0.012), 'cloth_accent'))
    B['torso'].append(setm(collar(c, open_v=True), 'cloth_accent'))
    B['torso'].append(chest_skin(c))
    zw = c.z['waist'] - 0.02
    B['torso'].append(panel(c, [(c.rz[6] - 0.03, 0.075), (c.rz[5], 0.085), (c.rz[4], 0.12), (c.rz[3], 0.15), (zw, 0.165)], ysurf_torso(c), off=0.04, bow=0.0, mat='cloth_main', folds=0.002))
    B['torso'].append(suspenders(c, x_front=0.07, x_back=0.08, width=0.02, off=0.04, mat='cloth_main'))
    B['torso'].append(belt(c, z=zw, width=0.022, off=0.046, thick=0.004, buckle=False, mat='cloth_main'))
    zb = c.z['knee'] - 0.06
    B['pelvis'].append(panel(c, [(zw, 0.165), (c.rz[1], 0.2), ((c.rz[1] + zb) / 2, 0.215), (zb, 0.23)], ysurf_lower(c), off=0.026, bow=0.014, mat='cloth_main', folds=0.005, seed=2))
    B['pelvis'].append(trousers_pelvis(c))
    for s in (1, -1):
        arm_parts(c, s, B, sleeve='short', sleeve_mat='cloth_accent')
    common_legs(c, B, legwear='trousers', shoes='shoe')
    face_basics(c, B, brow=dict(width=0.0036, thick=0.0028, arch=0.006, mat='hair'), lipkw=dict(w=0.019, up_h=0.0045, lo_h=0.0058))
    side_hair(c, B, SHORT_LINE, thick=0.009, top_extra=0.0, seed=12, clump=0.5)
    head_add(c, B, X.baker_cap(c))
    G = grip_point(c, 1)
    return {'tool_basket': (X.basket(c, G, 1), G, 'hand_l')}


# ---------------------------------------------------------------- FARMER
def farmer_garments(c, B):
    B['torso'].append(setm(shirt_shell(c, z0=c.rz[1] - 0.03, off=0.014), 'cloth_main'))
    B['torso'].append(setm(collar(c, open_v=True), 'cloth_main'))
    B['torso'].append(chest_skin(c))
    B['torso'].append(suspenders(c, x_front=0.08, x_back=0.075, width=0.026, off=0.03))
    B['torso'].append(belt(c, z=c.z['waist'] - 0.035, off=0.032))
    B['neck_head'].append(neckerchief(c))
    B['pelvis'].append(trousers_pelvis(c))
    for s in (1, -1):
        arm_parts(c, s, B, sleeve='rolled')
    common_legs(c, B, legwear='trousers', shoes='boot')
    face_basics(c, B, brow=dict(width=0.0037, thick=0.0028, arch=0.007, mat='hair'))
    side_hair(c, B, SHORT_LINE, thick=0.010, top_extra=0.004, seed=13, clump=0.6)
    head_add(c, B, X.straw_hat(c))
    L = c.legs[-1]
    pc = L['H'].lerp(L['K'], 0.62)
    B['leg_r_upper'].append(patch(V(pc.x - 0.005, pc.y - (0.0785 * c.leg_r + 0.0095), pc.z), 0.065, 0.075, 'leather'))
    L = c.legs[1]
    pc = L['K'] + V(0, 0, -0.12)
    B['leg_l_lower'].append(patch(V(pc.x, pc.y - (0.062 * c.leg_r + 0.0095), pc.z), 0.055, 0.07, 'leather'))
    G = grip_point(c, -1)
    return {'tool_fork': (X.pitchfork(c, G), G, 'hand_r')}


ARCH = {}
ARCH['man'] = dict(H=1.75, sex='m', kind='adult', face=default_face(), garments=man_garments,
                   mats=dict(skin='#d6a07c', hair='#4a3426', main='#cdc4ae', alt='#6c5f50', acc='#5f6b4a'),
                   label='마을 남자 (일꾼)')
ARCH['woman'] = dict(skirt=True, walk=dict(hip_swing_deg=15, knee_bend_deg=22, arm_swing_deg=18, stride_m=0.45, cycle_s=1.0), H=1.64, sex='f', kind='adult', face=default_face(W=0.077, jaw=0.34, brow=0.55, nose=0.82, nose_w=0.85, lip=1.2, chin=0.75, cheek=1.2, ear=0.9),
                     garments=woman_garments, build=dict(w=0.98, d=0.98),
                     mats=dict(skin='#e0ad8c', hair='#7a4f2a', main='#d9d3c3', alt='#4f6f8a', acc='#a1463a'),
                     label='마을 여인')
ARCH['elder_m'] = dict(walk=dict(hip_swing_deg=17, knee_bend_deg=26, arm_swing_deg=8, stride_m=0.42, cycle_s=1.45), H=1.68, sex='m', kind='adult', stoop=0.07, face=default_face(age=1.0, brow=1.25, nose=1.12, nose_w=1.1, chin=0.9, jaw=0.34, ear=1.15, lip=0.8),
                       garments=elder_m_garments, build=dict(w=0.94, d=1.0, belly=0.02, arm=0.92, leg=0.92),
                       elbow_flex={-1: 62, 1: 12}, hand_mode={-1: 'grip'}, hand_dir={-1: V(0, -.97, -.24)},
                       mats=dict(skin='#cc9878', hair='#b9b7b2', main='#8a7a63', alt='#4d4a45', acc='#d7d0c0', main_tex=('pbr_fabric_wool', 0.3)),
                       label='노인 (할아버지)')
ARCH['elder_f'] = dict(skirt=True, walk=dict(hip_swing_deg=12, knee_bend_deg=18, arm_swing_deg=8, stride_m=0.32, cycle_s=1.5), H=1.55, sex='f', kind='adult', stoop=0.045, face=default_face(W=0.076, age=0.8, brow=0.6, nose=0.9, nose_w=0.95, lip=0.85, chin=0.8, cheek=0.9, jaw=0.34, ear=1.05),
                       garments=elder_f_garments, build=dict(w=0.98, d=1.02, belly=0.015),
                       mats=dict(skin='#d2a080', hair='#bdbab4', main='#6b5a74', alt='#a39a86', acc='#7d5a46'),
                       label='노인 (할머니)')
ARCH['boy'] = dict(walk=dict(hip_swing_deg=30, knee_bend_deg=44, arm_swing_deg=28, stride_m=0.5, cycle_s=0.8), H=1.25, sex='m', kind='child', face=child_face(), garments=boy_garments, build=dict(w=0.98, d=0.96),
                   head_h=0.225, mats=dict(skin='#dba384', hair='#7a5430', main='#d8d0b8', alt='#6b5b46', acc='#8a5a3a'),
                   label='소년')
ARCH['girl'] = dict(skirt=True, walk=dict(hip_swing_deg=20, knee_bend_deg=32, arm_swing_deg=22, stride_m=0.38, cycle_s=0.8), H=1.2, sex='f', kind='child', face=child_face(lip=1.25, nose=0.55, brow=0.35, W=0.082), garments=girl_garments, build=dict(w=0.96, d=0.94),
                    head_h=0.22, mats=dict(skin='#e2ab8c', hair='#8a5a2c', main='#e3d7bd', alt='#5a7a9a', acc='#b2483c'),
                    label='소녀')
ARCH['smith'] = dict(walk=dict(hip_swing_deg=25, knee_bend_deg=38, arm_swing_deg=14, stride_m=0.72, cycle_s=1.15), H=1.82, sex='m', kind='adult', face=default_face(W=0.085, brow=1.4, nose=1.05, nose_w=1.15, chin=1.25, jaw=0.2, cheek=0.9, ear=1.0),
                     garments=smith_garments, build=dict(w=1.13, d=1.12, arm=1.22, leg=1.12, belly=0.012, sh=1.06, neck=1.15, hand=1.1),
                     elbow_flex={-1: 58, 1: 12}, hand_mode={-1: 'grip'}, hand_dir={-1: V(0, -.97, -.24)},
                     mats=dict(skin='#c99070', hair='#2f2118', main='#7b7064', alt='#4b4038', acc='#6a3a2a'),
                     label='대장장이')
ARCH['baker'] = dict(walk=dict(hip_swing_deg=24, knee_bend_deg=36, arm_swing_deg=18, stride_m=0.62, cycle_s=1.1), H=1.70, sex='m', kind='adult', face=default_face(W=0.087, Df=0.095, jaw=0.18, cheek=1.6, chin=0.7, lip=1.15, brow=0.8, nose=0.95, nose_w=1.2, ear=0.95),
                     garments=baker_garments, build=dict(w=1.07, d=1.1, belly=0.045, arm=1.05, leg=1.05),
                     elbow_flex={1: 14, -1: 10}, hand_mode={1: 'grip'}, abd_side={1: 16, -1: 9}, hand_dir={},
                     mats=dict(skin='#e0a888', hair='#8b6a40', main='#ece7da', alt='#5d5348', acc='#8aa0b8'),
                     label='제빵사')
ARCH['farmer'] = dict(H=1.78, sex='m', kind='adult', face=default_face(age=0.35, brow=1.1, nose=1.05, chin=1.05, jaw=0.3, cheek=1.05),
                      garments=farmer_garments, build=dict(w=1.02, d=1.0, arm=1.08),
                      elbow_flex={-1: 52, 1: 12}, hand_mode={-1: 'grip'}, hand_dir={-1: V(0, -.97, -.24)},
                      mats=dict(skin='#c88e68', hair='#5b4228', main='#d3cbb6', alt='#6a5c48', acc='#8f3f33'),
                      label='농부')
