import sys
sys.path.insert(0, '/shared/river/assets/blender')
from fishlib import *
reset_scene()
skin = vcol_mat('minnow_skin', '#ffffff', rough=0.25, metal=0.3)
finm = vcol_mat('minnow_fin', '#ffffff', rough=0.5, alpha=0.55, double=True)
eyem = make_mat('eye', '#c9b060', rough=0.05)
pupilm = make_mat('pupil', '#020202', rough=0.05)
st = [(-0.035, .0007, .0007, 0), (-0.032, .0024, .0027, 0), (-0.024, .0042, .0052, 0.0002), (-0.008, .0052, .0075, 0.0004),
      (0.008, .0048, .0072, 0.0003), (0.022, .0030, .0045, 0.0002), (0.031, .0017, .0028, 0.0002)]
body = stations_loft(st, segs=16, res=5)
ex = []
for sx in (1, -1):
    ec = V(sx * 0.0036, -0.0255, 0.0018)
    e = blob(ec, (0.0012, 0.0016, 0.0016), segs=8, rings=6); set_mat_index(e, 1)
    pu = blob(ec + V(sx * 0.0010, -0.0002, 0), (0.0005, 0.001, 0.001), segs=6, rings=4); set_mat_index(pu, 2)
    ex += [e, pu]
body = merge(body, *ex)


def col(p, n):
    b = n.z
    c = mixc('#b9c3b0', '#4b5a3a', (b - 0.25) * 2.2)
    c = mixc(c, '#f4f2ea', (-b - 0.2) * 2.5)
    st_ = math.exp(-((p.z - 0.0005) / 0.0011) ** 2)
    if p.y > -0.022:
        c = mixc(c, '#1b2024', st_ * 0.75 * min(1, (p.y + 0.022) * 150))
    c = mixc(c, '#fbf7ea', max(0, 1 - abs(p.z + 0.0015) / 0.002) * 0.3 * (1 if p.y > -0.02 else 0))
    if p.y < -0.029:
        c = mulc(c, 0.6)
    return c


bo = part('body', body, [skin, eyem, pupilm], (0, 0, 0), colorfn=col)
fc = lambda p, n: mixc('#d8d2c0', '#e6b47a', 0.3)
fins = []
fins.append(part('tail', fin_fan((0, 0.029, -0.0018), (0, 0.029, 0.0018), (0, 1, -0.9), (0, 1, 0.9), lambda u: 0.014 - 0.005 * (1 - abs(2 * u - 1)), cols=3, rows=2, nrm=(1, 0, 0), ridge=0.0001), [finm], (0, 0.029, 0), parent=bo, colorfn=fc))
fins.append(part('fin_dorsal', fin_fan((0, -0.006, 0.0072), (0, 0.006, 0.0062), (0, 0.2, 1), (0, 0.9, 0.5), lambda u: 0.0085 * (1 - 0.4 * u), cols=3, rows=2, nrm=(1, 0, 0), ridge=0.0001), [finm], (0, 0, 0.007), parent=bo, colorfn=fc))
for sx, s in ((1, 'l'), (-1, 'r')):
    fins.append(part('fin_pectoral_' + s, fin_fan((sx * 0.004, -0.0205, -0.0035), (sx * 0.004, -0.0185, -0.004), (sx * 0.5, 0.5, -0.4), (sx * 0.85, 0.9, -0.2), lambda u: 0.009, cols=3, rows=2, nrm=(0, 0, 1), ridge=0.0001), [finm], (sx * 0.004, -0.0195, -0.0037), parent=bo, colorfn=fc))
allp = [bo] + fins
meta = {'species': 'minnow (school fish)', 'fish': True, 'body_length_m': 0.07,
        'axes': 'nose -Y, tail +Y, dorsal +Z, origin mid-body', 'wiggle': {'head_y': -0.035, 'tail_y': 0.043, 'note': 'blender Y; amplitude 0 at head to max at tail; use fast 5-7 Hz'},
        'parts': {'root': 'body', 'tail': 'tail', 'dorsal': 'fin_dorsal', 'pectoral': ['fin_pectoral_l', 'fin_pectoral_r']},
        'animation': {'tail_swing_deg': 30, 'tail_hz': 6}}
print(export_bundle(OUT_DIR + '/minnow.json', allp, meta)); write_meta('minnow', meta)
print('tris', tri_count(allp))
preview_grid(PREVIEW_DIR + '/minnow.png', [((0.14, 0, 0.03), (0, 0, 0)), ((0.09, -0.12, 0.06), (0, 0, 0)), ((0.03, -0.08, 0.015), (0, -0.03, 0), 60), ((-0.1, 0.12, 0.08), (0, 0.0, 0))], target=(0, 0, 0), ground=False, bg=(0.25, 0.4, 0.5), res=(400, 300))
