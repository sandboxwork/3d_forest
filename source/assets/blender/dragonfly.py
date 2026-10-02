import sys
sys.path.insert(0, '/shared/river/assets/blender')
from fishlib import *
reset_scene()
bodym = vcol_mat('dragonfly_body', '#ffffff', rough=0.3, metal=0.25)
eyem = vcol_mat('dragonfly_eye', '#ffffff', rough=0.12, metal=0.1)
wingm = make_mat('wing_membrane', '#e4edf2', rough=0.15, alpha=0.3, double=True)
veinm = make_mat('wing_vein', '#2c2519', rough=0.5)
ZB = 0.030


def col_thorax(p, n):
    c = mixc('#6aa62c', '#c7d65a', max(0, -n.z) * 0.8)
    st = 0.5 + 0.5 * math.sin((p.y * 0.8 + abs(p.x) * 1.4) * 900)
    c = mixc(c, '#1f2412', max(0, st - 0.65) * 1.5 * (1 if abs(p.x) > 0.0015 else 0))
    c = mixc(c, '#1f2412', max(0, 1 - abs(p.x) / 0.0007) * 0.8 * (1 if n.z > 0.5 else 0))
    return c


def col_abd(p, n):
    t = (p.y - 0.003) / 0.055
    seg = t * 10
    fr = seg - math.floor(seg)
    c = mixc('#2b72cc', '#3a8bdc', 0.3)
    if seg < 1.0:
        c = mixc('#6aa62c', '#2b72cc', seg)
    c = mixc(c, '#14161b', max(0, 1 - abs(p.x) / 0.0006) * 0.85 * (1 if n.z > 0.4 else 0))
    c = mixc(c, '#14161b', max(0, fr - 0.86) * 6 + max(0, 0.08 - fr) * 6)
    if t > 0.95:
        c = mixc(c, '#1a1a1a', 0.7)
    return c


# ---- thorax (root part) + legs
thx = blob(V(0, -0.004, ZB), (0.0043, 0.0075, 0.0052), segs=16, rings=12)
hump = blob(V(0, -0.003, ZB + 0.0012), (0.0030, 0.0055, 0.0040), segs=12, rings=8)
thx = fuse(merge(thx, hump), voxel=0.0006, smooth_iter=6)
legs = []
for k, yy in enumerate((-0.0085, -0.0035, 0.0010)):
    for sx in (1, -1):
        spread = 0.0055 + 0.0015 * k
        c0 = V(sx * 0.0018, yy, ZB - 0.004)
        kn = c0 + V(sx * spread, -0.003 + (0.002 * k if k == 2 else 0) * -1 + (0.0055 if k == 2 else -0.001), 0.0015 - 0.0005 * k)
        if k == 2:
            kn = c0 + V(sx * 0.0065, 0.0035, 0.0005)
        ft = kn + V(sx * 0.0030, -0.0060 if k < 2 else -0.004, -0.0065)
        tp = ft + V(sx * 0.0010, -0.0025, -0.0012)
        legs.append(loft([c0, kn, ft, tp], [0.0006, 0.00055, 0.00042, 0.00025], segs=5, res=3, cap_push=0.9))
legs = merge(*legs)
thorax = merge(thx, legs)
body = part('body', thorax, [bodym], (0, -0.004, ZB), colorfn=lambda p, n: col_thorax(p, n) if p.z > ZB - 0.0042 else '#221c14')

# ---- abdomen
N = 44
pts = []; rr = []
for i in range(N):
    t = i / (N - 1)
    pts.append(V(0, 0.003 + 0.055 * t, ZB - 0.0012 - 0.0028 * t * t))
    base = 0.0032 - 0.0013 * math.sin(min(1, t * 6) * math.pi / 2) - 0.0002 * t
    if t > 0.05 and t < 0.16: base *= 0.78
    rng = 1 + 0.10 * abs(math.cos(math.pi * t * 10))
    rr.append(max(0.0012, base) * rng * (1 - max(0, t - 0.94) * 6))
abd = loft(pts, rr, [r * 0.95 for r in rr], segs=10, res=1, cap_push=0.6)
ce = []
for sx in (1, -1):
    ce.append(loft([pts[-1], pts[-1] + V(sx * 0.0007, 0.0030, -0.0003), pts[-1] + V(sx * 0.0012, 0.0055, -0.0008)], [0.0004, 0.0003, 0.00015], segs=5, res=2))
abd = merge(abd, *ce)
abdo = part('abdomen', abd, [bodym], (0, 0.003, ZB - 0.0012), parent=body, colorfn=col_abd)

# ---- head
HP = V(0, -0.0112, ZB + 0.0004)
hd = blob(V(0, -0.0148, ZB + 0.0004), (0.0040, 0.0030, 0.0034), segs=14, rings=10)
fr = blob(V(0, -0.0178, ZB - 0.0006), (0.0034, 0.0018, 0.0028), segs=12, rings=8)
mand = blob(V(0, -0.0190, ZB - 0.0030), (0.0024, 0.0012, 0.0012), segs=8, rings=6)
hd = merge(hd, fr, mand)
ey = []
for sx in (1, -1):
    e = blob(V(sx * 0.0032, -0.0150, ZB + 0.0012), (0.0030, 0.0036, 0.0033), segs=16, rings=12); set_mat_index(e, 1); ey.append(e)
hd = merge(hd, *ey)


def hcol(p, n):
    # eyes: distinguish by distance from face centre via x
    if abs(p.x) > 0.0028 and p.y < -0.0115:
        u = (p.z - ZB) / 0.0035
        c = mixc('#2a66c4', '#46a04e', -u * 0.9 + 0.35)
        return mulc(c, 0.85 + 0.3 * (fbm(p, 900, 1, 3) * .5 + .5))
    c = mixc('#6aa62c', '#e8e8c0', max(0, -(p.y + 0.0170)) * 400)
    return c


head = part('head', hd, [bodym, eyem], HP, parent=body, colorfn=hcol)


# ---- wings
def wing(name, sx, root, L, C, hind):
    g = bmesh.new()
    NS, NC = 22, 6
    rows = []

    def w(s):
        a = min(1.0, 0.38 + s * 3.2)
        return C * a * max(0.0, 1 - s ** 4.5) ** 0.5

    def le(s):
        return -0.0012 * math.sin(math.pi * min(1, s * 1.3) * 0.6) + (0.0016 * s * s)

    def zz(s, v):
        return 0.0012 * s - 0.0012 * math.sin(math.pi * v) * s * 0.5

    def P(s, v):
        ww = w(s) * (1.0 + (0.35 * (1 - min(1, s * 3.4)) * v if hind else 0))
        return V(sx * s * L, le(s) + ww * v - (0.0 if not hind else 0.0), zz(s, v))
    for i in range(NS + 1):
        s = min(1.0, i / NS * 0.995 + 0.0)
        rows.append([g.verts.new(P(s, j / NC)) for j in range(NC + 1)])
    for i in range(NS):
        for j in range(NC):
            g.faces.new((rows[i][j], rows[i + 1][j], rows[i + 1][j + 1], rows[i][j + 1]))
    bmesh.ops.recalc_face_normals(g, faces=g.faces[:])
    veins = []
    vs = [0.0, 0.10, 0.28, 0.5, 0.74, 1.0]
    for k, v in enumerate(vs):
        pts = [P(min(1, i / 14 * 0.97), v) for i in range(15)]
        r = 0.00042 if k == 0 else 0.00018
        pts = [p for p in pts]
        veins.append(loft(pts, [r * (1 - 0.6 * i / 14) for i in range(15)], segs=4, res=1, cap_push=0.5))
    for i in range(1, 14):
        s = i / 14 * 0.97
        for k in range(len(vs) - 1):
            if (i + k) % 2 == 0:
                veins.append(loft([P(s, vs[k]), P(s + 0.012, vs[k + 1])], [0.00011, 0.00011], segs=3, res=1, cap0=False, cap1=False))
    # pterostigma near tip on leading edge
    ps = blob(P(0.86, 0.04), (0.0021, 0.0007, 0.00035), segs=8, rings=6)
    ps = xform(ps, Matrix.Identity(4))
    veins.append(ps)
    vm = merge(*veins)
    for f in vm.faces: f.material_index = 1
    mm = merge(g, vm)
    return part(name, mm, [wingm, veinm], root, parent=body)


wings = []
for sx, s in ((1, 'l'), (-1, 'r')):
    wings.append(wing('wing_f' + s, sx, V(sx * 0.0030, -0.0050, ZB + 0.0040), 0.0245 * 2, 0.0088, False))
    wings.append(wing('wing_h' + s, sx, V(sx * 0.0030, 0.0008, ZB + 0.0040), 0.0240 * 2, 0.0110, True))
allp = [body, abdo, head] + wings
meta = {'species': 'emperor/hawker dragonfly (blue abdomen)', 'scale_hint_m': {'length': 0.075, 'wingspan': 0.104, 'hover_height': 0.03},
        'axes': 'nose -Y, left +X; origin on ground under body (thorax at z=0.03)',
        'parts': {'root': 'body (thorax+legs)', 'abdomen': 'abdomen (pivot at thorax rear; pitch about X for flight/curl)', 'head': 'head (pivot at neck)',
                  'wings': {'fore_l': 'wing_fl', 'fore_r': 'wing_fr', 'hind_l': 'wing_hl', 'hind_r': 'wing_hr'}},
        'flight': {'wing_beat_hz': 28, 'flap_axis': 'Y (roll about fore-aft axis; left wing rotate +Y deg? flap: left wing rot_y = +a, right wing rot_y = -a)', 'flap_amplitude_deg': 35,
                   'fore_hind_phase_offset': 0.5, 'hover_bob_m': 0.01, 'abdomen_pitch_deg': [-6, 6]},
        'note': 'wings rest spread flat (z pivot at top of thorax), ~0.05 m long each; membrane alpha 0.3 double-sided; veins opaque sub-mesh'}
print(export_bundle(OUT_DIR + '/dragonfly.json', allp, meta)); write_meta('dragonfly', meta)
print('tris', tri_count(allp))
preview_grid(PREVIEW_DIR + '/dragonfly.png', [((0.0, -0.01, 0.22), (0, 0, 0.03)), ((0.2, 0.0, 0.07), (0, 0, 0.03)), ((0.04, -0.07, 0.05), (0, -0.012, 0.03), 70), ((0.12, -0.15, 0.1), (0, 0, 0.03))], target=(0, 0, 0.03), ground=False, bg=(0.35, 0.5, 0.65), res=(480, 340))
