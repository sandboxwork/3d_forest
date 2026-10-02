import sys
sys.path.insert(0, '/shared/river/assets/blender')
from animlib import *

PREVIEW = os.environ.get('PREVIEW', '1') == '1'
reset_scene()

fur = vcol_mat('rabbit_fur', '#ffffff', rough=0.93)
eyem = make_mat('eye', '#20110a', rough=0.05)
pupilm = make_mat('pupil', '#000000', rough=0.1)
nosem = make_mat('nose_wet', '#b98580', rough=0.2)
clawm = make_mat('claw', '#5a4a3c', rough=0.5)
whisk = make_mat('whisker', '#e8e4da', rough=0.5)
inner = make_mat('ear_inner_skin', '#d9a59a', rough=0.7)

BACK = '#a08560'; BACK2 = '#6b5339'; BELLY = '#e2d6bf'; NAPE = '#b0703e'


def coat(p, n):
    belly = max(0.0, -n.z * 1.3 - 0.1) + max(0, (0.06 - p.z) * 8)
    c = mixc(BACK, BELLY, belly)
    # agouti ticking
    t = fbm(p, 160, 2, 3)
    c = mixc(c, BACK2, 0.22 * (t * 0.5 + 0.5) + 0.15 * max(0, n.z) * (fbm(V(p.x * 4, p.y, p.z * 4), 25, 2, 5) * 0.5 + 0.5))
    # rusty nape
    c = mixc(c, NAPE, max(0, 1 - abs(p.y + 0.12) / 0.06) * max(0, n.z) * 0.7)
    # paler legs/feet
    if p.z < 0.05:
        c = mixc(c, '#a58e6c', 0.4)
    return mulc(c, 0.9 + 0.2 * (fbm(p, 90, 2, 8) * 0.5 + 0.5))


# ---- body
chest = blob((0, -0.055, 0.125), (0.062, 0.085, 0.095))
mid = blob((0, 0.015, 0.125), (0.075, 0.11, 0.105))
rump = blob((0, 0.085, 0.115), (0.085, 0.105, 0.11), rot=(0.2, 0, 0))
bm = merge(chest, mid, rump, blob((0.072, 0.075, 0.095), (0.04, 0.08, 0.075)), blob((-0.072, 0.075, 0.095), (0.04, 0.08, 0.075)))
bm = fuse(bm, voxel=0.0055, smooth_iter=10)
body = part('body', bm, [fur], (0, 0.0, 0.10), colorfn=coat, noise=dict(amp=0.0012, freq=120, seed=1))

# ---- head
P0 = V(0, -0.125, 0.195)
hb = [blob(P0 + V(0, -0.028, -0.004), (0.037, 0.05, 0.04)),
      blob(P0 + V(0, -0.072, -0.018), (0.027, 0.04, 0.028)),
      blob(P0 + V(0, -0.0, 0.0), (0.042, 0.04, 0.043))]
for sx in (1, -1):
    hb.append(blob(P0 + V(sx * 0.03, -0.075, -0.03), (0.018, 0.028, 0.016)))   # cheeks/whisker pads
hb = merge(*hb)
hb = fuse(hb, voxel=0.0028, smooth_iter=8)
ex = []
nose = blob(P0 + V(0, -0.108, -0.014), (0.0095, 0.006, 0.0075)); set_mat_index(nose, 2); ex.append(nose)
for sx in (1, -1):
    ec = P0 + V(sx * 0.031, -0.045, 0.012)
    e = blob(ec, (0.0085, 0.009, 0.01)); set_mat_index(e, 1); ex.append(e)
    pu = blob(ec + V(sx * 0.0058, -0.003, 0.0), (0.0025, 0.005, 0.006), segs=8, rings=6); set_mat_index(pu, 3); ex.append(pu)
    nn = blob(P0 + V(sx * 0.0045, -0.113, -0.013), (0.0022, 0.0025, 0.003), segs=6, rings=4); set_mat_index(nn, 3); ex.append(nn)
    # whiskers
    for k in range(4):
        a = (k - 1.5) * 0.14
        s = V(sx * 0.014, -0.096, -0.020 + k * 0.0015)
        d = V(sx * math.cos(a) * 0.6, -0.5 + math.sin(a) * 0.3, 0.12 * (k - 1.5) * -0.3).normalized()
        w = loft([P0 + s, P0 + s + d * 0.03 + V(0, 0, 0.004), P0 + s + d * 0.07 + V(0, 0, -0.004)], [0.0005, 0.0004, 0.0001], segs=4, res=2, cap_push=1)
        set_mat_index(w, 4); ex.append(w)
hb = merge(hb, *ex)


def hcol(p, n):
    c = coat(p, n)
    q = -(p.y - P0.y)
    c = mixc(c, '#e8ddc6', max(0, min(1, (q - 0.06) * 25)) * max(0.0, 0.6 - n.z * 0.7))   # pale muzzle
    e = V(P0.x + (0.031 if p.x > 0 else -0.031), P0.y - 0.045, P0.z + 0.012)
    c = mixc(c, '#ece3cc', max(0, 1 - (p - e).length / 0.022) ** 1.5 * 0.8)
    return c


head = part('head', hb, [fur, eyem, nosem, pupilm, whisk], P0, parent=body, colorfn=hcol, noise=dict(amp=0.0006, freq=200, seed=4))

jb = loft([P0 + V(0, -0.04, -0.03), P0 + V(0, -0.075, -0.037), P0 + V(0, -0.098, -0.03)], [0.016, 0.013, 0.007], [0.009, 0.0085, 0.006], segs=10, res=4)
jaw = part('jaw', jb, [fur], P0 + V(0, -0.035, -0.03), parent=head, colorfn=lambda p, n: mixc('#e6dcc6', '#c9bba0', 0.3))

# ---- ears
ears = []
for sx, nm in ((1, 'ear_l'), (-1, 'ear_r')):
    base = P0 + V(sx * 0.022, 0.012, 0.038)
    tip = base + V(sx * 0.025, 0.028, 0.115)
    nrm = V(sx * 0.7, -0.6, 0.0)
    e = leaf_shape(base, tip, 0.0235, 0.0028, bulge=0.4, segs=12, curve=(sx * 0.008, 0.0, 0), res=5, up=nrm)
    for v in e.verts:   # slight cup
        t = (v.co - base).length / (tip - base).length
        v.co += nrm.normalized() * 0.007 * math.sin(math.pi * t) * 0.0
    ears.append(part(nm, e, [fur], base, parent=head,
                     colorfn=lambda p, n, nrm=nrm, base=base, tip=tip: mixc(mixc(BACK, '#2b2218', max(0, (p - base).length / (tip - base).length - 0.8) * 4),
                                                                         '#d8b5a0', 0.6) if n.dot(nrm) > 0 else mixc(BACK, '#2b2218', max(0, (p - base).length / (tip - base).length - 0.8) * 4)))

# ---- tail (cotton)
tr = V(0, 0.185, 0.13)
tb = merge(blob(tr + V(0, 0.022, 0.0), (0.03, 0.03, 0.03)), blob(tr + V(0, 0.03, 0.012), (0.024, 0.024, 0.026)))
tb = fuse(tb, voxel=0.004, smooth_iter=6)
tail = part('tail', tb, [fur], tr, parent=body,
            colorfn=lambda p, n: mixc('#f3eee2', '#6a5a45', max(0, n.z) * max(0, 0.5 - (p.y - 0.19) * 10) * 0.6) if True else None,
            noise=dict(amp=0.0015, freq=90, seed=6))

# ---- legs
legs = []


def seg(name, pts, rx, rz, pivot, parent, mat=fur, up=(0, -1, 0), col=coat, segs=14, **kw):
    b = loft(pts, rx, rz, segs=segs, res=5, up=up, **kw)
    return part(name, b, [mat], pivot, parent=parent, colorfn=col, noise=dict(amp=0.0008, freq=120, seed=3))


for sx, s in ((1, 'l'), (-1, 'r')):
    m = lambda x, y, z: V(sx * x, y, z)
    # hind: thigh -> knee (forward), tibia -> heel, foot flat forward
    hip = m(0.068, 0.085, 0.115); knee = m(0.078, 0.0, 0.06); heel = m(0.066, 0.13, 0.022); toe = m(0.066, -0.055, 0.01)
    tb_ = merge(loft([hip, (hip + knee) / 2 + V(0, 0.01, 0.0), knee], [0.05, 0.04, 0.022], [0.062, 0.045, 0.028], segs=16, res=5, up=(0, -1, 0)),
                blob(hip + V(0, 0.015, -0.005), (0.042, 0.065, 0.07)))
    th = part('leg_h%s_thigh' % s, tb_, [fur], hip, parent=body, colorfn=coat, noise=dict(amp=0.0008, freq=120, seed=3))
    lw = seg('leg_h%s_lower' % s, [knee, (knee + heel) / 2 + V(0, -0.005, 0.0), heel], [0.02, 0.017, 0.012], [0.024, 0.02, 0.013], knee, th)
    ft = seg('leg_h%s_foot' % s, [heel + V(0, 0.003, 0.0), (heel + toe) / 2, toe], [0.021, 0.02, 0.016], [0.013, 0.012, 0.009], heel, lw, up=(0, 0, 1))
    # fore: upper (shoulder -> elbow), lower (forearm -> wrist), paw
    sh = m(0.045, -0.06, 0.12); el = m(0.05, -0.06, 0.055); wr = m(0.045, -0.085, 0.022); pw = m(0.045, -0.12, 0.008)
    fu = seg('leg_f%s_upper' % s, [sh, (sh + el) / 2, el], [0.03, 0.024, 0.016], [0.035, 0.026, 0.018], sh, body)
    fl = seg('leg_f%s_lower' % s, [el, (el + wr) / 2, wr], [0.014, 0.011, 0.0105], [0.016, 0.0125, 0.012], el, fu)
    pb = loft([wr + V(0, 0, 0.0), (wr + pw) / 2, pw], [0.0105, 0.0115, 0.0095], [0.011, 0.0105, 0.008], segs=10, res=4, up=(0, 0, 1))
    pp = part('leg_f%s_paw' % s, pb, [fur], wr, parent=fl, colorfn=coat)
    legs += [th, lw, ft, fu, fl, pp]

allparts = [body, head, jaw] + ears + [tail] + legs
meta = {
    'species': 'European wild rabbit (Oryctolagus cuniculus)', 'pose': 'sitting upright/crouched, alert',
    'forward': '-Y', 'left_is': '+X', 'scale_hint_m': {'length': 0.4, 'height_sitting': 0.27, 'ear_length': 0.12},
    'parts': {'root': 'body', 'head': 'head', 'jaw': 'jaw', 'ears': ['ear_l', 'ear_r'], 'tail': 'tail'},
    'hierarchy': {'body': ['head', 'tail', 'leg_h*_thigh', 'leg_f*_upper'], 'head': ['jaw', 'ear_l', 'ear_r'],
                  'leg_h*_thigh': ['leg_h*_lower'], 'leg_h*_lower': ['leg_h*_foot'], 'leg_f*_upper': ['leg_f*_lower'], 'leg_f*_lower': ['leg_f*_paw']},
    'hop': {'cycle_s': 0.55, 'body_arc_height_m': 0.18, 'distance_m': 0.35,
            'note': 'Sitting rest pose. For a hop: body pitch nose-down/up via whole-asset rotation X; hind thigh rot_x: sit (0) -> extend (-55deg swings foot back/up), hind lower rot_x +50, foot rot_x -40; fore upper rot_x +20 reaches forward. Tuck back in flight.',
            'sign': 'rotation about X: positive rotates the free end of a part that points up toward +Y (back)... verify visually; front/hind swing ranges given are hints'},
    'idle': {'ear_twitch_deg': 12, 'ear_independent': True, 'nose_twitch': 'head rot_x +-2deg at 6Hz', 'breath': 'body scale 1..1.02 at 1Hz', 'graze': {'head_rot_x_deg': 35}},
    'pivots': 'part origin = joint',
}
print(export_bundle(OUT_DIR + '/rabbit.json', allparts, meta))
write_meta('rabbit', meta)
print('tris', tri_count(allparts))
if PREVIEW:
    preview_grid(PREVIEW_DIR + '/rabbit.png', [((0.9, 0.05, 0.3), (0, 0, 0.15), 50), ((0.65, -0.8, 0.45), (0, 0, 0.14), 50),
                                               ((0.22, -0.42, 0.26), (0, -0.12, 0.19), 70), ((-0.7, 0.7, 0.4), (0, 0, 0.14), 50)], target=(0, 0, 0.15))
