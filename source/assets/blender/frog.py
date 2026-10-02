import sys
sys.path.insert(0, '/shared/river/assets/blender')
from fishlib import *
reset_scene()
skin = vcol_mat('frog_skin', '#ffffff', rough=0.32, metal=0.0)
irism = make_mat('eye', '#c79a1c', rough=0.05)
pupilm = make_mat('pupil', '#010101', rough=0.05)
webm = vcol_mat('frog_web', '#ffffff', rough=0.4, double=True)
nosem = make_mat('nostril', '#1a2410', rough=0.3)


def obl(center, axes, radii, segs=14, rings=10):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0)
    a, b, c = [V(x).normalized() for x in axes]
    M = Matrix(((a.x * radii[0], b.x * radii[1], c.x * radii[2]), (a.y * radii[0], b.y * radii[1], c.y * radii[2]), (a.z * radii[0], b.z * radii[1], c.z * radii[2])))
    for v in bm.verts:
        v.co = M @ v.co + V(center)
    return bm


ST = [(-0.048, .003, .003, .026), (-0.040, .013, .009, .027), (-0.028, .022, .0125, .0295), (-0.012, .0255, .019, .031),
      (0.012, .030, .027, .034), (0.035, .025, .027, .030), (0.050, .012, .016, .022), (0.056, .004, .007, .018)]
body = stations_loft(ST, segs=28, res=6)
body = merge(body, *[blob(V(sx * 0.0165, -0.026, 0.0385), (0.009, 0.011, 0.0065)) for sx in (1, -1)])   # eye sockets
body = fuse(body, voxel=0.0016, smooth_iter=8, smooth_f=0.6)
ex = []
for sx in (1, -1):
    ec = V(sx * 0.0140, -0.027, 0.0425)
    e = blob(ec, (0.0072, 0.0072, 0.0072), segs=16, rings=12); set_mat_index(e, 1)
    d = V(sx * 0.5, -0.45, 0.75).normalized()
    t = d.cross(V(0, 0, 1)).normalized(); w = d.cross(t).normalized()
    pu = obl(ec + d * 0.0064, (t, w, d), (0.0034, 0.0013, 0.0010), segs=12, rings=8); set_mat_index(pu, 2)
    ex += [e, pu]
    nn = blob(V(sx * 0.0035, -0.0455, 0.0292), (0.0013, 0.0013, 0.0013), segs=6, rings=4); set_mat_index(nn, 3); ex.append(nn)
body = merge(body, *ex)
bar_col = lambda p, n: None


def back_col(p, n):
    b = n.z
    c = mixc('#b9c35a', '#5f9330', (b + 0.05) * 2.0)
    c = mixc(c, '#ebe6bf', (-b - 0.3) * 2.5)
    blot = fbm(V(p.x * 1.2, p.y, p.z), 70, 2, 4)
    c = mixc(c, '#2c4a16', max(0, blot - 0.08) * 4 * max(0, min(1, b + 0.2)))
    ay = abs(p.x)
    c = mixc(c, '#c6d352', max(0, 1 - abs(ay - 0.0205) / 0.0035) * 0.8 * (1 if -0.03 < p.y < 0.045 and b > 0.2 else 0))
    c = mixc(c, '#d9dc7a', max(0, 1 - ay / 0.0022) * 0.7 * (1 if b > 0.6 and p.y > -0.03 else 0))
    tp = V(p.x - (0.0265 if p.x > 0 else -0.0265), p.y + 0.002, p.z - 0.0345).length
    c = mixc(c, '#8d7a3a', max(0, 1 - tp / 0.0055) * 0.6)
    if p.y < -0.040 and n.z < 0.1:
        c = mixc(c, '#c7b87a', 0.4)
    c = mixc(c, '#2a2a14', max(0, mnoise.noise(V(p.x * 400, p.y * 400, p.z * 400)) - 0.55) * 4 * (1 if -0.1 < b < 0.4 else 0))
    return mulc(c, 0.9 + 0.2 * (fbm(p, 200, 1, 3) * .5 + .5))


bo = part('body', body, [skin, irism, pupilm, nosem], (0, 0, 0.02), colorfn=back_col)

# throat pouch (vocal sac), pivot at chin
tb = blob(V(0, -0.032, 0.0115), (0.0115, 0.0145, 0.0075), segs=14, rings=10)
throat = part('throat', tb, [skin], V(0, -0.03, 0.02), parent=bo, colorfn=lambda p, n: mixc('#ddd8a8', '#a8a070', max(0, n.z) * 0.3 + 0.1 * fbm(p, 120, 1, 2)))


def leg_col(start, bandfreq=240):
    def f(p, n):
        c = back_col(p, n)
        d = (p - start).length
        bar = 0.5 + 0.5 * math.sin(d * bandfreq)
        c = mixc(c, '#2f4a1a', 0.45 * max(0, bar - 0.4) * max(0, min(1, n.z + 0.4)))
        if n.z < -0.3:
            c = mixc(c, '#e8e2b8', 0.7)
        return c
    return f


parts_all = [bo, throat]
for sx, s in ((1, 'l'), (-1, 'r')):
    m = lambda x, y, z, sx=sx: V(sx * x, y, z)
    # ---- hind leg
    hip, knee, ank, toe = m(0.026, 0.030, 0.024), m(0.050, -0.006, 0.013), m(0.041, 0.056, 0.0065), m(0.062, 0.020, 0.001)
    th = loft([hip, m(0.040, 0.012, 0.0195), knee], [0.0135, 0.0115, 0.0075], [0.0135, 0.0115, 0.0075], segs=14, res=6, cap_push=0.7)
    hu = part('leg_h%s_upper' % s, th, [skin], hip, parent=bo, colorfn=leg_col(hip))
    sh = loft([knee, m(0.0465, 0.025, 0.010), ank], [0.0078, 0.0068, 0.0042], [0.0078, 0.0068, 0.0042], segs=12, res=6, cap_push=0.7)
    hl = part('leg_h%s_lower' % s, sh, [skin], knee, parent=hu, colorfn=leg_col(knee))
    # foot: metatarsus + 5 toes + web
    fw = V(ank); ft = (toe - ank); ft.z = 0; fdir = ft.normalized()
    perp = fdir.cross(V(0, 0, 1)).normalized()
    meta_t = loft([ank, ank + fdir * 0.013 + V(0, 0, 0.0005)], [0.0042, 0.0034], [0.0035, 0.0028], segs=8, res=3)
    fparts = [meta_t]; tips = []
    lens = [0.014, 0.022, 0.031, 0.040, 0.026]
    for k in range(5):
        a = (k - 2) * 0.17
        dv = (fdir * math.cos(a) + perp * math.sin(a)).normalized()
        st0 = ank + fdir * 0.012 + perp * (k - 2) * 0.0024
        tip = st0 + dv * lens[k] + V(0, 0, -0.0015)
        fparts.append(loft([st0, st0 + dv * lens[k] * 0.5, tip], [0.0030, 0.0024, 0.0014], [0.0020, 0.0016, 0.0010], segs=6, res=3, cap_push=0.9))
        fparts.append(blob(tip, (0.0022, 0.0022, 0.0014), segs=6, rings=4))
        tips.append(tip)
    # web: fan from ankle region to toe tips (single sheet)
    web = bmesh.new()
    rows = 3
    base_pts = [ank + fdir * 0.012 + perp * (k - 2) * 0.0024 + V(0, 0, -0.0008) for k in range(5)]
    grid = []
    for k in range(5):
        row = [web.verts.new(base_pts[k].lerp(tips[k] - (tips[k] - base_pts[k]).normalized() * 0.0, j / rows * 0.92)) for j in range(rows + 1)]
        grid.append(row)
    for k in range(4):
        for j in range(rows):
            web.faces.new((grid[k][j], grid[k + 1][j], grid[k + 1][j + 1], grid[k][j + 1]))
    fb = merge(*fparts)
    webmesh = web
    fb = merge(fb, webmesh)
    for f in fb.faces[-(4 * rows):]:
        f.material_index = 1
    ft_ob = part('leg_h%s_foot' % s, fb, [skin, webm], ank, parent=hl, colorfn=lambda p, n: mixc(back_col(p, n), '#7d8f3a', 0.3))
    # ---- front leg
    sho, elb, wri = m(0.024, -0.013, 0.027), m(0.032, -0.018, 0.010), m(0.026, -0.030, 0.0035)
    ua = loft([sho, m(0.029, -0.015, 0.018), elb], [0.0085, 0.0070, 0.0055], [0.0085, 0.0070, 0.0055], segs=10, res=5, cap_push=0.7)
    au = part('arm_%s_upper' % s, ua, [skin], sho, parent=bo, colorfn=leg_col(sho))
    la = loft([elb, m(0.029, -0.024, 0.006), wri], [0.0055, 0.0048, 0.0040], [0.0055, 0.0048, 0.0040], segs=10, res=5, cap_push=0.7)
    hand = [la]
    for k in range(4):
        a = (k - 1.5) * 0.30
        st0 = wri + V(0, 0, 0)
        dv = V(math.sin(a) * sx * 1.0, -math.cos(a), -0.02).normalized()
        L = 0.013 if k in (0, 3) else 0.016
        p1 = st0 + dv * L + V(0, 0, -0.0015)
        hand.append(loft([st0 + dv * 0.002, st0 + dv * L * 0.5, p1], [0.0020, 0.0016, 0.0011], [0.0016, 0.0013, 0.0009], segs=6, res=3, cap_push=0.9))
        hand.append(blob(p1, (0.0017, 0.0017, 0.0012), segs=6, rings=4))
    al = part('arm_%s_lower' % s, merge(*hand), [skin], elb, parent=au, colorfn=leg_col(elb))
    parts_all += [hu, hl, ft_ob, au, al]

meta = {'species': 'green frog (Pelophylax)', 'scale_hint_m': {'length': 0.09, 'height_sitting': 0.05, 'eyes_top_z': 0.053},
        'axes': 'nose -Y, left = +X, origin on ground under body; parts have pivots at joints', 'left_is': '+X',
        'parts': {'root': 'body', 'throat': 'throat (pivot at chin; scale 1..1.6 to pulse vocal sac)', 'hind_legs': {'leg_hl': ['upper', 'lower', 'foot'], 'leg_hr': ['upper', 'lower', 'foot']},
                  'front_legs': {'arm_l': ['upper', 'lower'], 'arm_r': ['upper', 'lower']}},
        'hierarchy': {'body': ['throat', 'leg_h*_upper', 'arm_*_upper'], 'leg_h*_upper': ['leg_h*_lower'], 'leg_h*_lower': ['leg_h*_foot'], 'arm_*_upper': ['arm_*_lower']},
        'hop': {'note': 'rest pose is crouched: thigh forward-out, shin folded back. Extend: rotate upper about X by +50deg (knee swings back), lower about X by -70deg, foot about X by +40deg; body pitch up 15deg; duration 0.5s; sign to be verified at runtime',
                'airborne_deg': {'upper_x': 55, 'lower_x': -85, 'foot_x': 45}},
        'idle': {'throat_pulse_hz': 1.2, 'throat_scale': [1.0, 1.35]}}
print(export_bundle(OUT_DIR + '/frog.json', parts_all, meta)); write_meta('frog', meta)
print('tris', tri_count(parts_all))
preview_grid(PREVIEW_DIR + '/frog.png', [((0.22, 0.0, 0.08), (0, 0, 0.025)), ((0.0, -0.22, 0.12), (0, 0, 0.025)), ((0.08, -0.12, 0.09), (0, -0.02, 0.03), 70), ((-0.15, 0.2, 0.15), (0, 0, 0.025))], target=(0, 0, 0.025), res=(480, 340))
