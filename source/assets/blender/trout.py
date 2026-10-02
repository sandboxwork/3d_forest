import sys
sys.path.insert(0, '/shared/river/assets/blender')
from fishlib import *
reset_scene()
skin = vcol_mat('trout_skin', '#ffffff', rough=0.3, metal=0.18)
finm = vcol_mat('trout_fin', '#ffffff', rough=0.4, alpha=0.6, double=True)
eyem = make_mat('eye', '#9a7a2a', rough=0.05)
pupilm = make_mat('pupil', '#020202', rough=0.05)
mouthm = make_mat('mouth', '#3a1a1a', rough=0.4)

st = [(-0.178, 0.002, 0.002, -0.002), (-0.170, 0.0075, 0.0075, -0.002), (-0.152, 0.0140, 0.0175, -0.001), (-0.12, 0.0195, 0.029, -0.001),
      (-0.07, 0.0225, 0.0365, -0.002), (0.0, 0.0215, 0.035, -0.002), (0.05, 0.0165, 0.028, -0.001), (0.09, 0.010, 0.0185, 0.0), (0.127, 0.0062, 0.0130, 0.0)]
body = stations_loft(st, segs=44, res=12)
# eyes
eyes = []
for sx in (1, -1):
    ec = V(sx * 0.0128, -0.1455, 0.0075)
    e = blob(ec, (0.0034, 0.0048, 0.0048), segs=14, rings=10); set_mat_index(e, 1)
    pu = blob(ec + V(sx * 0.0026, -0.0005, 0), (0.0012, 0.0031, 0.0031), segs=10, rings=8); set_mat_index(pu, 2)
    eyes += [e, pu]
# gill cover + lower jaw bump
gills = []
for sx in (1, -1):
    gills.append(blob(V(sx * 0.0135, -0.128, -0.003), (0.0045, 0.020, 0.024), segs=16, rings=10))
body = merge(body, *gills)
body = fuse(body, voxel=0.0028, smooth_iter=10, smooth_f=0.6)
body = merge(body, *eyes)


def col(p, n):
    y = p.y
    zn = p.z / 0.034
    b = n.z
    c = mixc('#a09c5a', '#46532f', (b - 0.3) * 2.0)          # side -> back
    c = mixc(c, '#e7e2c6', (-b - 0.25) * 2.4)                 # belly
    if -0.13 < y < 0.11:
        w = math.exp(-((b + 0.05) / 0.2) ** 2) * min(1.0, (y + 0.13) * 30) * min(1.0, (0.1 - y) * 30)
        c = mixc(c, '#d0607a', w * 0.75)
        c = mixc(c, '#b7c0b0', w * 0.2)
    # silver sheen on flanks
    sil = max(0, 1 - abs(b + 0.15) * 2.2)
    c = mixc(c, '#dfe3cf', sil * 0.4)
    sp = mnoise.noise(V(p.x * 150, p.y * 150, p.z * 150))
    if sp > 0.3 and b > -0.35 and y > -0.15:
        c = mixc(c, '#14140d', min(1, (sp - 0.3) * 8) * (0.9 if b > 0.1 else 0.6))
    rp = mnoise.noise(V(p.x * 120 + 9, p.y * 120, p.z * 120))
    if rp > 0.5 and abs(b) < 0.55 and y > -0.1:
        c = mixc(c, '#c0322a', min(1, (rp - 0.5) * 9) * 0.9)
    if -0.138 < y < -0.128 and b > -0.5:
        c = mulc(c, 0.6)   # gill edge
    if y < -0.16:
        c = mixc(c, '#2f2f22', 0.5)
    if y < -0.165 and b < 0.0:
        c = mixc(c, '#d9d0b8', 0.3)
    return mulc(c, 0.92 + 0.15 * (fbm(p, 200, 1, 3) * .5 + .5))


bo = part('body', body, [skin, eyem, pupilm], (0, 0, 0), colorfn=col)


def fincol(base, tip, edge='#f1ece0'):
    def f(p, n):
        return mixc(base, tip, 0.0)
    return f


def fcol(kind):
    def f(p, n):
        d = math.sin(p.y * 400 + p.z * 400 + p.x * 400)
        if kind == 'orange':
            c = mixc('#e0914a', '#d9d4c0', 0.5)
        elif kind == 'dark':
            c = '#c4bf9c'
            if mnoise.noise(V(p.x * 120, p.y * 120, p.z * 120)) > 0.45: c = '#3a3a28'
        else:
            c = '#6a6a48'
        return mulc(c, 0.85 + 0.15 * d)
    return f


# tail
def tail_len(u):
    return 0.056 - 0.013 * (1 - abs(2 * u - 1)) ** 1.5 + 0.01 * abs(2 * u - 1)


tb = fin_fan((0, 0.118, -0.0115), (0, 0.118, 0.0115), (0, 1, -0.75), (0, 1, 0.75), tail_len, cols=10, rows=6, nrm=(1, 0, 0), ridge=0.0006)
tail = part('tail', tb, [finm], (0, 0.118, 0), parent=bo, colorfn=fcol('dark'))
# dorsal
db = fin_fan((0, -0.042, 0.0345), (0, 0.004, 0.032), (0, 0.15, 1), (0, 0.85, 0.5), lambda u: 0.034 * (1 - 0.6 * u), cols=9, rows=5, nrm=(1, 0, 0))
dorsal = part('fin_dorsal', db, [finm], (0, -0.02, 0.034), parent=bo, colorfn=fcol('dark'))
# adipose
ab = blob((0, 0.072, 0.0205), (0.0014, 0.0085, 0.006), segs=8, rings=6)
adip = part('fin_adipose', ab, [finm], (0, 0.072, 0.017), parent=bo, colorfn=fcol('orange'))
# anal
anb = fin_fan((0, 0.047, -0.0275), (0, 0.072, -0.0195), (0, 0.2, -1), (0, 0.9, -0.45), lambda u: 0.026 * (1 - 0.55 * u), cols=7, rows=5, nrm=(1, 0, 0))
anal = part('fin_anal', anb, [finm], (0, 0.055, -0.025), parent=bo, colorfn=fcol('orange'))
fins = [tail, dorsal, adip, anal]
for sx, s in ((1, 'l'), (-1, 'r')):
    pb = fin_fan((sx * 0.0195, -0.106, -0.0135), (sx * 0.0195, -0.096, -0.0145), (sx * 0.5, 0.45, -0.5), (sx * 0.85, 0.9, -0.3), lambda u: 0.036 * (1 - 0.35 * u), cols=7, rows=5, nrm=(0, 0, 1))
    fins.append(part('fin_pectoral_' + s, pb, [finm], (sx * 0.0195, -0.101, -0.0138), parent=bo, colorfn=fcol('orange')))
    vb = fin_fan((sx * 0.008, -0.01, -0.0335), (sx * 0.008, -0.002, -0.0340), (sx * 0.3, 0.5, -0.8), (sx * 0.7, 0.9, -0.5), lambda u: 0.026 * (1 - 0.4 * u), cols=6, rows=5, nrm=(0, 0, 1))
    fins.append(part('fin_pelvic_' + s, vb, [finm], (sx * 0.008, -0.006, -0.0337), parent=bo, colorfn=fcol('orange')))
allp = [bo] + fins
meta = {'species': 'brown/rainbow trout', 'fish': True, 'body_length_m': 0.35,
        'axes': 'nose -Y, tail +Y, dorsal +Z, origin mid-body; export pivots in three.js coords (x,z,-y)',
        'wiggle': {'axis': 'blender Y (three.js -Z... three Z = -Y)', 'head_y': -0.176, 'tail_y': 0.175, 'note': 'in three.js coords the nose is at z=+0.176, tail at z=-0.175; amplitude grows from 0 at head to max at tail'},
        'parts': {'root': 'body', 'tail': 'tail', 'dorsal': 'fin_dorsal', 'adipose': 'fin_adipose', 'anal': 'fin_anal', 'pectoral': ['fin_pectoral_l', 'fin_pectoral_r'], 'pelvic': ['fin_pelvic_l', 'fin_pelvic_r']},
        'animation': {'tail_swing_deg': 28, 'tail_axis': 'Z (yaw)', 'tail_hz': 2.5, 'pectoral_flap_deg': 20, 'pectoral_axes': 'Z for l/r', 'scale_hint_m': {'length': 0.35, 'depth': 0.073}}}
print(export_bundle(OUT_DIR + '/trout.json', allp, meta)); write_meta('trout', meta)
print('tris', tri_count(allp))
preview_grid(PREVIEW_DIR + '/trout.png', [((0.55, 0, 0.12), (0, 0, 0)), ((0.35, -0.5, 0.25), (0, 0, 0)), ((0.12, -0.3, 0.05), (0, -0.14, 0), 60), ((-0.3, 0.55, 0.3), (0, 0.05, 0))], target=(0, 0, 0), ground=False, bg=(0.25, 0.4, 0.5))
