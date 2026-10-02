import sys
sys.path.insert(0, '/shared/river/assets/blender')
from fishlib import *
reset_scene()
skin = vcol_mat('carp_skin', '#ffffff', rough=0.3, metal=0.22)
finm = vcol_mat('carp_fin', '#ffffff', rough=0.4, alpha=0.6, double=True)
eyem = make_mat('eye', '#b08a30', rough=0.05)
pupilm = make_mat('pupil', '#020202', rough=0.05)
barm = vcol_mat('carp_barbel', '#ffffff', rough=0.5)

st = [(-0.225, .002, .002, -.004), (-0.217, .009, .009, -.005), (-0.195, .019, .024, -.004), (-0.15, .030, .045, -.001), (-0.09, .036, .062, .003),
      (-0.02, .037, .066, .005), (0.05, .030, .055, .003), (0.11, .017, .032, .002), (0.15, .009, .019, .001), (0.168, .007, .015, .001)]
body = stations_loft(st, segs=48, res=12)
gills = [blob(V(sx * 0.026, -0.135, -0.008), (0.006, 0.026, 0.034), segs=16, rings=10) for sx in (1, -1)]
lips = blob(V(0, -0.222, -0.006), (0.011, 0.008, 0.007), segs=12, rings=8)
body = merge(body, *gills, lips)
body = fuse(body, voxel=0.0036, smooth_iter=10, smooth_f=0.6)
extra = []
for sx in (1, -1):
    ec = V(sx * 0.0188, -0.183, 0.013)
    e = blob(ec, (0.0050, 0.0068, 0.0068), segs=14, rings=10); set_mat_index(e, 1)
    pu = blob(ec + V(sx * 0.0040, -0.0008, 0), (0.0016, 0.0040, 0.0040), segs=10, rings=8); set_mat_index(pu, 2)
    extra += [e, pu]
body = merge(body, *extra)
bars = []
for sx in (1, -1):
    bars.append(loft([V(sx * 0.010, -0.219, -0.008), V(sx * 0.016, -0.232, -0.014), V(sx * 0.018, -0.241, -0.022)], [0.0015, 0.0011, 0.0005], segs=6, res=4))
    bars.append(loft([V(sx * 0.011, -0.212, -0.004), V(sx * 0.018, -0.222, -0.006), V(sx * 0.024, -0.228, -0.012)], [0.0012, 0.0009, 0.0004], segs=6, res=4))
bars = merge(*bars)
for f in bars.faces: f.material_index = 3


def lattice(p):
    zc = 0.004
    th = math.atan2(p.z - zc, p.x)
    a = th * 0.05 / 0.0135
    b = p.y / 0.0135
    row = round(a)
    off = 0.5 if int(row) % 2 else 0.0
    bx = b + off
    fx = bx - round(bx); fy = a - row
    d = math.sqrt(fx * fx + fy * fy)
    return d


def col(p, n):
    y = p.y
    bk = n.z
    patch = fbm(p, 9, 3, 11)
    gold = mixc('#d29a34', '#e56a1c', (patch + 0.2) * 1.4)
    c = mixc(gold, '#f0e6cf', (fbm(p, 9, 2, 5) - 0.02) * 6.0)       # white patches
    c = mixc(c, mulc(gold, 0.55), (bk - 0.45) * 1.6)                    # darker back
    c = mixc(c, '#f2e8c8', (-bk - 0.35) * 2.0)                        # pale belly
    if fbm(p, 14, 2, 21) > 0.30:
        c = mixc(c, '#15110e', 0.85)                                    # kohaku sumi patches
    d = lattice(p)
    c = mulc(c, 0.78 + 0.28 * (1 - min(1, d * 1.7)))
    if -0.108 < y < -0.096 and bk > -0.6:
        c = mulc(c, 0.85)
    if y < -0.19:
        c = mixc(c, '#c88a4a', 0.4)
    return c


bo = part('body', body, [skin, eyem, pupilm, barm], (0, 0, 0), colorfn=col)


def fcol(kind):
    def f(p, n):
        c = '#e87a30' if kind == 'or' else '#c9a65a'
        return mulc(c, 0.8 + 0.2 * math.sin(p.y * 300 + p.z * 300))
    return f


def tail_len(u):
    return 0.075 - 0.02 * (1 - abs(2 * u - 1)) ** 1.5 + 0.012 * abs(2 * u - 1)


fins = []
fins.append(part('tail', fin_fan((0, 0.160, -0.013), (0, 0.160, 0.013), (0, 1, -0.85), (0, 1, 0.85), tail_len, cols=11, rows=6, nrm=(1, 0, 0), ridge=0.0007), [finm], (0, 0.16, 0), parent=bo, colorfn=fcol('or')))
fins.append(part('fin_dorsal', fin_fan((0, -0.075, 0.064), (0, 0.06, 0.056), (0, 0.15, 1), (0, 0.75, 0.6), lambda u: 0.052 - 0.028 * u, cols=14, rows=6, nrm=(1, 0, 0)), [finm], (0, -0.04, 0.062), parent=bo, colorfn=fcol('g')))
fins.append(part('fin_anal', fin_fan((0, 0.085, -0.043), (0, 0.108, -0.032), (0, 0.2, -1), (0, 0.85, -0.5), lambda u: 0.034 - 0.012 * u, cols=7, rows=5, nrm=(1, 0, 0)), [finm], (0, 0.095, -0.04), parent=bo, colorfn=fcol('or')))
for sx, s in ((1, 'l'), (-1, 'r')):
    fins.append(part('fin_pectoral_' + s, fin_fan((sx * 0.032, -0.125, -0.022), (sx * 0.033, -0.113, -0.026), (sx * 0.5, 0.4, -0.5), (sx * 0.85, 0.9, -0.3), lambda u: 0.055 * (1 - 0.3 * u), cols=8, rows=5, nrm=(0, 0, 1)), [finm], (sx * 0.032, -0.119, -0.024), parent=bo, colorfn=fcol('or')))
    fins.append(part('fin_pelvic_' + s, fin_fan((sx * 0.012, -0.03, -0.060), (sx * 0.012, -0.018, -0.062), (sx * 0.3, 0.5, -0.8), (sx * 0.7, 0.9, -0.5), lambda u: 0.04 * (1 - 0.4 * u), cols=7, rows=5, nrm=(0, 0, 1)), [finm], (sx * 0.012, -0.024, -0.061), parent=bo, colorfn=fcol('or')))
allp = [bo] + fins
meta = {'species': 'common carp / koi (golden-orange)', 'fish': True, 'body_length_m': 0.45,
        'axes': 'nose -Y, tail +Y, dorsal +Z, origin mid-body',
        'wiggle': {'head_y': -0.225, 'tail_y': 0.235, 'note': 'blender Y; in three.js the nose is +Z. wiggle amplitude 0 at head growing to tail; body ~0.14 m deep'},
        'parts': {'root': 'body', 'tail': 'tail', 'dorsal': 'fin_dorsal', 'anal': 'fin_anal', 'pectoral': ['fin_pectoral_l', 'fin_pectoral_r'], 'pelvic': ['fin_pelvic_l', 'fin_pelvic_r'], 'barbels': 'sub-mesh of body (material carp_barbel)'},
        'animation': {'tail_swing_deg': 22, 'tail_axis': 'Z (yaw)', 'tail_hz': 1.6, 'pectoral_flap_deg': 15}}
print(export_bundle(OUT_DIR + '/carp.json', allp, meta)); write_meta('carp', meta)
print('tris', tri_count(allp))
preview_grid(PREVIEW_DIR + '/carp.png', [((0.7, 0, 0.15), (0, 0, 0)), ((0.45, -0.6, 0.35), (0, 0, 0)), ((0.1, -0.4, 0.06), (0, -0.2, 0), 60), ((-0.4, 0.7, 0.4), (0, 0.05, 0))], target=(0, 0, 0), ground=False, bg=(0.25, 0.4, 0.5))
