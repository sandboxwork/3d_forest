"""vl_cloth: garments & accessories for the villagers (all built in world coords)."""
import sys
sys.path.insert(0, '/shared/river/assets/blender')
from vl_body import *


def trim(bm, keep):
    dele = [f for f in bm.faces if not keep(f.calc_center_median())]
    bmesh.ops.delete(bm, geom=dele, context='FACES')
    return bm


def solid(bm, th):
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=th)
    return bm


def radial_folds(bm, cx, cy, n, amp, z_top, z_hem, seed=0, power=1.0, base=0.15, swirl=0.0):
    def fn(p, nrm):
        th = math.atan2(p.y - cy, p.x - cx)
        g = base + (1 - base) * smooth(z_top, z_hem, p.z) ** power
        ph = n * th + 1.3 * mnoise.noise(V(p.x * 3 + seed, p.y * 3, p.z * 2.5)) + swirl * p.z
        return amp * g * (math.sin(ph) * 0.7 + 0.3 * math.sin(2.3 * ph + 1.0))
    return displace(bm, fn)


def axial_wrinkles(bm, origin, axis, amp, freq, t0, width, seed=0, skew=0.0):
    ax = V(axis).normalized()
    o = V(origin)

    def fn(p, nrm):
        t = (p - o).dot(ax)
        g = math.exp(-((t - t0) / width) ** 2)
        return amp * g * math.sin(freq * t + 2.0 * mnoise.noise(V(p.x * 6 + seed, p.y * 6, p.z * 6)) + skew * (p.x + p.y))
    return displace(bm, fn)


def torso_creases(bm, c, amp=0.0035, seed=0):
    zw = c.z['waist']

    def fn(p, nrm):
        th = math.atan2(p.y, p.x)
        a = 0.0
        # horizontal creases above the belt, strongest on the front/sides
        a += math.exp(-((p.z - (zw + 0.03)) / 0.045) ** 2) * math.sin((p.z - zw) * 95 + 2.5 * mnoise.noise(V(p.x * 8 + seed, p.y * 8, 0)))
        # vertical hang folds below the chest
        a += 0.6 * smooth(zw + 0.2, zw - 0.1, p.z) * math.sin(th * 9 + 2 * mnoise.noise(V(p.x * 4, p.y * 4, p.z * 3)))
        return amp * a
    return displace(bm, fn)


def button(pos, r=0.0068, mat='teeth', normal=(0, -1, 0)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=r)
    for v in bm.verts:
        v.co.y *= 0.45
    translate(bm, pos)
    setm(bm, mat)
    return bm


def front_pos(c, z, off=0.0):
    hw, yf, yb = prof(c, z)
    return V(0, (yb - yf) / 2 + c.ys(z) - ((yf + yb) / 2 + off) , z)


def stitches(c, z0, z1, n, x, off, mat='leather', size=(0.0016, 0.0016, 0.0085)):
    out = []
    for i in range(n):
        z = z0 + (z1 - z0) * i / (n - 1)
        p = front_pos(c, z, off)
        p.x = x
        out.append(box(p + V(0, 0.0006, 0), size))
    bm = merge(*out)
    return setm(bm, mat)


# ---------------------------------------------------------------- torso garments
def shirt_shell(c, z0=None, off=0.015, neck_open=0.0, hem_liner=0.02, n=9, seed=1):
    z0 = c.rz[1] - 0.02 if z0 is None else z0
    z1 = c.rz[8]
    pts, rw, rd = shell(c, z0, z1, off, n)
    rw[-1] = c.neck_r + 0.012
    rd[-1] = c.neck_r + 0.012
    rw[-2] = max(rw[-2] * 0.95, c.neck_r + 0.02)
    for i in range(n):
        ex = 0.016 * (1 - i / (n - 1)) ** 1.3
        rw[i] += ex; rd[i] += ex
    bm = cloth_tube(pts, rw, rd, segs=16, res=2, hem0=True, hem1=True, thick=0.004, liner=hem_liner,
                    pre=lambda b: torso_creases(b, c, 0.003, seed))
    return bm


def collar(c, open_v=True, up=0.02, flare=0.012):
    zt = c.rz[8] - 0.004
    y0 = c.ys(zt) + 0.0
    pts = [V(0, y0 + 0.002, zt - 0.012), V(0, y0, zt + up)]
    r0 = c.neck_r + 0.014
    bm = cloth_tube(pts, [r0, r0 + flare], [r0 * 1.02, r0 * 1.02 + flare], segs=16, res=2, hem1=True, thick=0.0035, liner=0.015)
    if open_v:
        trim(bm, lambda p: not (p.y < y0 - 0.02 and abs(p.x) < 0.02 + (zt + up - p.z) * 0.15 + 0.005))
    return bm


def chest_skin(c):
    z0 = c.rz[3]
    z1 = c.rz[8]
    pts, rw, rd = shell(c, z0, z1, -0.014, 7)
    rw[-1] = c.neck_r * 1.0; rd[-1] = c.neck_r * 1.0
    bm = tube(pts, rw, rd, segs=12, res=1, caps=(True, True))
    return setm(bm, 'skin')


def vest_shell(c, z0=None, off=0.021, vopen=0.045, vdepth=0.2, th=0.006, seed=3, flare=0.018):
    z0 = c.rz[1] + 0.0 if z0 is None else z0
    z1 = c.rz[7] + 0.002
    pts, rw, rd = shell(c, z0, z1, off, 10)
    for i in range(len(rw)):
        ex = flare * (1 - i / (len(rw) - 1)) ** 2.0
        rw[i] += ex; rd[i] += ex
    bm = tube(pts, rw, rd, segs=20, res=2, caps=(False, False))
    zt = z1
    zb = z0

    def keep(p):
        # V opening in front: half width grows toward the neck
        k = (p.z - zb) / (zt - zb)
        front = p.y < pts[0].y - 0.01
        w = vopen * (0.35 + 1.1 * k ** 1.7)
        if k < vdepth:
            w = vopen * 0.35
        return not (front and abs(p.x) < w)
    trim(bm, keep)
    torso_creases(bm, c, 0.0025, seed)
    rim(bm, th)
    return bm


def belt(c, z=None, width=0.042, off=0.026, thick=0.007, buckle=True, mat='leather'):
    z = c.z['waist'] - 0.012 if z is None else z
    hw, yf, yb = prof(c, z)
    pts = [V(0, (yb - yf) / 2 + c.ys(z), z - width / 2), V(0, (yb - yf) / 2 + c.ys(z), z + width / 2)]
    r = [hw + off, hw + off]
    rd = [(yf + yb) / 2 + off, (yf + yb) / 2 + off]
    bm = cloth_tube(pts, r, rd, segs=20, res=1, hem0=True, hem1=True, thick=thick, liner=0.004)
    setm(bm, mat)
    out = [bm]
    if buckle:
        fp = V(0, (yb - yf) / 2 + c.ys(z) - ((yf + yb) / 2 + off + thick * 0.4), z)
        bk = box(fp, (0.036, 0.007, width * 0.9), bevel=0.003)
        setm(bk, 'brass')
        inner = box(fp + V(0, -0.003, 0), (0.02, 0.006, width * 0.55), bevel=0.0015)
        setm(inner, 'leather')
        out += [bk, inner]
    return merge(*out)


def pouch(c, z, x, w=0.06, h=0.07, d=0.035, mat='leather', angle=0.0, side=False):
    hw, yf, yb = prof(c, z)
    y = (yb - yf) / 2 + c.ys(z) - ((yf + yb) / 2 + 0.04)
    if side:
        y = (yb - yf) / 2 + c.ys(z) - 0.03
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= w; v.co.y *= d; v.co.z *= h
        if v.co.z < 0:
            v.co.x *= 0.88
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=0.008, segments=2, affect='EDGES')
    # flap
    fl = box((0, -d * 0.5 - 0.002, h * 0.3), (w * 1.02, 0.006, h * 0.45), bevel=0.003)
    bm = merge(bm, fl)
    rot_about(bm, 'Y', angle)
    translate(bm, V(x, y - 0.0, z - h * 0.35))
    return setm(bm, mat)


def shawl(c, drop_back=0.30, drop_side=0.2, drop_front=0.16, off=0.026, color_mat='cloth_accent', seed=5, nth=26, nv=6, gap=0.32):
    z1 = c.rz[7] + 0.004
    bm = bmesh.new()
    V_ = []
    for ri in range(nv):
        v = ri / (nv - 1)
        row = []
        for i in range(nth):
            th = gap / 2 + (2 * math.pi - gap) * i / (nth - 1)
            d = drop_front + (drop_back - drop_front) * (0.5 - 0.5 * math.cos(th)) ** 0.9
            z = z1 - v * d
            hw, yf, yb = prof(c, z)
            rw = hw + off + 0.006 * v
            rd = (yf + yb) / 2 + off + 0.006 * v
            yc = (yb - yf) / 2 + c.ys(z)
            row.append(bm.verts.new(V(rw * math.sin(th), yc - rd * math.cos(th), z)))
        V_.append(row)
    for ri in range(nv - 1):
        for i in range(nth - 1):
            bm.faces.new((V_[ri][i], V_[ri][i + 1], V_[ri + 1][i + 1], V_[ri + 1][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    fix_outward(bm)
    radial_folds(bm, 0, prof(c, z1)[2] / 2, 8, 0.0045, z1, z1 - drop_back, seed=seed, base=0.3)
    rim(bm, 0.006)
    return setm(bm, color_mat)


def apron_bib(c, z0, z1, hw_top=0.075, off=0.03, mat='cloth_alt', th=0.005):
    pts, rw, rd = shell(c, z0, z1, off, 6)
    bm = tube(pts, rw, rd, segs=24, res=3, caps=(False, False))
    ycen = pts[0].y

    def keep(p):
        if p.y > ycen - 0.01:
            return False
        k = (p.z - z0) / (z1 - z0)
        return abs(p.x) < hw_top + (1 - k) * 0.075
    trim(bm, keep)
    solid(bm, -th)
    return setm(bm, mat)


def apron_skirt(c, z0, z1, off=0.04, spread=0.05, mat='cloth_alt', th=0.005, seed=7, front_ang=1.25):
    """Front-only hanging panel from waist (z0) down to z1."""
    hw, yf, yb = prof(c, z0)
    hw2, yf2, yb2 = prof(c, c.rz[1])
    n = 6
    pts, rw, rd = [], [], []
    for i in range(n):
        t = i / (n - 1)
        z = z0 + (z1 - z0) * t
        zz = max(z, c.rz[1])
        h2, f2, b2 = prof(c, zz)
        pts.append(V(0, (b2 - f2) / 2 + c.ys(z) * (1 - t) - (spread * t) * 0.15, z))
        rw.append(h2 + off + spread * t * 0.8)
        rd.append((f2 + b2) / 2 + off + spread * t * 0.8)
    bm = cloth_tube(pts, rw, rd, segs=26, res=3, hem0=False, hem1=False)
    ycen = pts[0].y

    def keep(p):
        if p.y > ycen - 0.005:
            return False
        ang = abs(math.atan2(p.x, -(p.y - ycen)))
        return ang < front_ang
    trim(bm, keep)
    radial_folds(bm, 0, ycen, 6, 0.0035, z0, z1, seed=seed, base=0.2)
    solid(bm, -th)
    return setm(bm, mat)


def skirt(c, z_hem, rx_hem, ry_hem, z_top=None, seed=2, folds=9, amp=0.012, mat='cloth_alt'):
    z_top = c.z['waist'] if z_top is None else z_top
    hw, yf, yb = prof(c, z_top)
    hwh, yfh, ybh = prof(c, c.rz[1])
    zk = z_hem + (z_top - z_hem) * 0.5
    pts = [V(0, 0, z_top + 0.02 * c.sc), V(0, 0, z_top - 0.05 * c.sc), V(0, 0, c.rz[1]), V(0, 0, zk), V(0, 0, z_hem)]
    rw = [hw + 0.014, hw + 0.02, hwh + 0.03, hwh + (rx_hem - hwh) * 0.45 + 0.03, rx_hem]
    rd = [(yf + yb) / 2 + 0.014, (yf + yb) / 2 + 0.02, (yfh + ybh) / 2 + 0.03, (yfh + ybh) / 2 + (ry_hem - (yfh + ybh) / 2) * 0.45 + 0.03, ry_hem]
    for p, (a, b) in zip(pts, [(0, 0)] * 5):
        pass
    pts[0].y = (yb - yf) / 2; pts[1].y = (yb - yf) / 2; pts[2].y = (ybh - yfh) / 2
    bm = cloth_tube(pts, rw, rd, segs=30, res=2, hem0=False, hem1=True, thick=0.005, liner=0.03,
                    pre=lambda b: radial_folds(b, 0, 0.0, folds, amp, z_top, z_hem, seed=seed, power=1.2))
    c.skirt_prof = (np.array([p.z for p in pts][::-1]), np.array(rw[::-1]), np.array(rd[::-1]), np.array([p.y for p in pts][::-1]))
    return setm(bm, mat)


def trousers_pelvis(c, z_bottom=None, off=0.0075, seed=4):
    z_bottom = c.z['crotch'] - 0.03 if z_bottom is None else z_bottom
    z_top = c.z['waist'] + 0.02
    pts, rw, rd = shell(c, z_bottom, z_top, off, 7)
    bm = cloth_tube(pts, rw, rd, segs=18, res=3, hem0=False, hem1=False, caps=(True, False))
    # hip folds
    def fn(p, n):
        th = math.atan2(p.y, p.x)
        return 0.0025 * smooth(c.z['waist'], c.z['crotch'], p.z) * math.sin(th * 6 + 3 * mnoise.noise(V(p.x * 5, p.y * 5, p.z * 4)))
    displace(bm, fn)
    return setm(bm, 'cloth_alt')


# ---------------------------------------------------------------- sleeves & legs
def rad_arm(c, key):
    r = c.arm_r
    return {'sh': 0.052 * r, 'mid': 0.047 * r, 'el': 0.040 * r, 'fa': 0.040 * r, 'wr': 0.0265 * r}[key]


def arm_parts(c, side, B, sleeve='long', cuff='plain', sleeve_mat='cloth_main', seed=0, forearm_scale=1.0, bare_scale=1.0):
    a = c.arms[side]
    S, E, W, d1, d2 = a['S'], a['E'], a['W'], a['d1'], a['d2']
    t = side_tag(side)
    sk = c.arm_r
    th = 0.0085
    fs = forearm_scale
    # --- upper arm skin
    up_pts = [S, S.lerp(E, 0.5), E]
    ub = tube(up_pts, [rad_arm(c, 'sh') * 0.95, rad_arm(c, 'mid') * bare_scale, rad_arm(c, 'el') * bare_scale],
              [rad_arm(c, 'sh') * 0.9, rad_arm(c, 'mid') * 0.95 * bare_scale, rad_arm(c, 'el') * 0.95 * bare_scale], segs=10, res=2)
    setm(ub, 'skin')
    parts_u = [ub]
    # --- lower arm skin
    lo_pts = [E, E.lerp(W, 0.4), W]
    lb = tube(lo_pts, [rad_arm(c, 'el') * 0.98, rad_arm(c, 'fa') * 0.98 * fs, rad_arm(c, 'wr')],
              [rad_arm(c, 'el') * 0.95, rad_arm(c, 'fa') * 0.9 * fs, rad_arm(c, 'wr') * 0.85], segs=10, res=2)
    setm(lb, 'skin')
    parts_l = [lb]
    if sleeve != 'none':
        ru = [rad_arm(c, 'sh') + th + 0.004, rad_arm(c, 'mid') + th, rad_arm(c, 'el') + th]
        if sleeve == 'short':
            tt = 0.62
            pts = [S, S.lerp(E, 0.3), S.lerp(E, tt)]
            ru = [ru[0], ru[1] + 0.002, ru[1] + 0.006]
            sb = cloth_tube(pts, ru, [r * 0.97 for r in ru], segs=14, res=2, hem1=True, caps=(True, False), thick=0.004)
        else:
            sb = tube([S, S.lerp(E, 0.5), E], ru, [r * 0.97 for r in ru], segs=14, res=2, caps=(True, True))
        axial_wrinkles(sb, E, d1, 0.0028, 85, 0.0, 0.1, seed + 1)
        parts_u.append(setm(sb, sleeve_mat))
        if sleeve == 'long' or sleeve == 'rolled':
            rl = [rad_arm(c, 'el') + th, (rad_arm(c, 'fa') + th - 0.001) * fs, (rad_arm(c, 'wr') + th * 0.55) * (fs ** 0.5)]
            if sleeve == 'long':
                pts = [E, E.lerp(W, 0.5), W.lerp(E, 0.04)]
                lb2 = cloth_tube(pts, [rl[0], rl[1], rl[2] + 0.004], [r * 0.97 for r in [rl[0], rl[1], rl[2] + 0.004]], segs=14, res=2,
                                 hem1=True, caps=(True, False), thick=0.004, liner=0.025,
                                 pre=lambda b: axial_wrinkles(b, E, d2, 0.0028, 80, 0.07, 0.08, seed + 2))
                parts_l.append(setm(lb2, sleeve_mat))
            else:
                # rolled: sleeve to ~ 30% of forearm then a thick roll ring
                end = 0.30
                pts = [E, E.lerp(W, 0.15), E.lerp(W, end)]
                rr = [rl[0], rl[1] + 0.003, rl[1] + 0.0035]
                lb2 = tube(pts, rr, [r * 0.97 for r in rr], segs=14, res=2, caps=(True, False))
                axial_wrinkles(lb2, E, d2, 0.003, 70, 0.06, 0.07, seed + 2)
                parts_l.append(setm(lb2, sleeve_mat))
                p0 = E.lerp(W, end - 0.03); p1 = E.lerp(W, end + 0.1)
                R0 = rl[1] + 0.0035
                roll_r = [R0 + 0.002, R0 + 0.014, R0 + 0.014, R0 + 0.002]
                roll = cloth_tube([p0, p0.lerp(p1, 0.3), p0.lerp(p1, 0.7), p1], roll_r, [r * 0.97 for r in roll_r], segs=14, res=2,
                                  hem0=True, hem1=True, thick=0.006, liner=0.006,
                                  pre=lambda b: axial_wrinkles(b, E, d2, 0.0018, 120, 0.2, 0.05, seed + 3))
                parts_l.append(setm(roll, sleeve_mat))
    if sleeve != 'none' and sleeve != 'short':
        er = (rad_arm(c, 'el') + th) * 0.97
        parts_l.append(setm(blob(E, (er, er, er), segs=10, rings=7), sleeve_mat))
    B['arm_%s_upper' % t].extend(parts_u)
    B['arm_%s_lower' % t].extend(parts_l)
    # shoulder blob in the torso to round the joint
    ro = (rad_arm(c, 'sh') + (th + 0.004 if sleeve != 'none' else 0)) * 0.9
    sb = blob(S + V(0, 0, 0.004), (ro, ro * 0.97, ro * 0.88), segs=12, rings=8)
    B['torso'].append(setm(sb, sleeve_mat if sleeve != 'none' else 'skin'))


def leg_parts(c, side, B, legwear='trousers', hem_z=None, shoes='boot', sock=None, shorts_len=0.55, seed=0, trouser_mat='cloth_alt', thigh_cover=None):
    L = c.legs[side]
    Hj, K, A = L['H'], L['K'], L['A']
    t = side_tag(side)
    r = c.leg_r
    ru = [0.092 * r, 0.082 * r, 0.067 * r]
    rl = [0.066 * r, 0.058 * r, 0.037 * r]
    uskin = tube([Hj, Hj.lerp(K, 0.5), K], ru, [x * 1.02 for x in ru], segs=10, res=2)
    setm(uskin, 'skin')
    parts_u = [uskin]
    lskin = tube([K, K.lerp(A, 0.35), A + V(0, 0, 0.01)], [rl[0], rl[1], rl[2]], [x * 1.05 for x in rl], segs=10, res=2)
    setm(lskin, 'skin')
    parts_l = [lskin]
    th = 0.0075
    if legwear in ('trousers', 'shorts'):
        if legwear == 'trousers':
            tt = 1.0
        else:
            tt = shorts_len
        pts = [Hj + V(0, 0, 0.0), Hj.lerp(K, 0.3), Hj.lerp(K, 0.6), Hj.lerp(K, tt)]
        rr = [(ru[0] + th + 0.004) * 0.88, ru[0] * 0.93 + th, ru[1] * 0.96 + th, np.interp(tt, [0, 0.5, 1.0], ru) + th + (0.012 if legwear == 'shorts' else 0.0)]
        d = (K - Hj).normalized()

        def _pre_u(b):
            axial_wrinkles(b, Hj, d, 0.0032, 70, (K - Hj).length * 0.92, 0.07, seed + 3)
            axial_wrinkles(b, Hj, d, 0.0025, 55, 0.04, 0.06, seed + 4)
        ub = cloth_tube(pts, rr, [x * 1.02 for x in rr], segs=14, res=2, hem1=(legwear == 'shorts'), caps=(True, legwear != 'shorts'), thick=0.005, liner=0.03, pre=_pre_u)
        parts_u.append(setm(ub, trouser_mat))
        if legwear == 'trousers':
            hz = (A.z + 0.07 * c.sc) if hem_z is None else hem_z
            kp = K
            hem_p = V(K.x + (A.x - K.x) * (K.z - hz) / (K.z - A.z), K.y + (A.y - K.y) * (K.z - hz) / (K.z - A.z), hz)
            mid = K.lerp(hem_p, 0.5)
            rr = [ru[2] + th, rl[1] + th + 0.0005, rl[2] + th + 0.017 * c.sc]
            d2 = (hem_p - K).normalized()

            def _pre_l(b):
                axial_wrinkles(b, K, d2, 0.0035, 75, 0.02, 0.07, seed + 5)
                axial_wrinkles(b, K, d2, 0.0045, 60, (hem_p - K).length * 0.93, 0.06, seed + 6)
            lb = cloth_tube([K, mid, hem_p], rr, [x * 1.04 for x in rr], segs=14, res=3, hem1=True, caps=(True, False), thick=0.005, liner=0.03, pre=_pre_l)
            parts_l.append(setm(lb, trouser_mat))
    if legwear == 'trousers':
        # knee blob: closes the gap on the outside of the bend
        kr = (ru[2] + th) * 0.97
        parts_l.append(setm(blob(K, (kr, kr * 1.02, kr * 0.98), segs=12, rings=8), trouser_mat))
    if thigh_cover:
        # skirt-wearers: cloth sleeve around the thigh, hidden inside the skirt at rest, covers the leg when it swings out / sits
        rr = [ru[0] * 0.92 + th + 0.012, ru[1] + th + 0.012, ru[2] + th + 0.012]
        tc = cloth_tube([Hj, Hj.lerp(K, 0.5), K], rr, [x * 1.02 for x in rr], segs=12, res=2, caps=(True, True))
        parts_u.append(setm(tc, thigh_cover))
        kr = (ru[2] + th + 0.012) * 0.98
        parts_l.append(setm(blob(K, (kr, kr, kr * 0.97), segs=10, rings=7), thigh_cover))
    if shoes in ('boot',):
        # boot shaft in the lower leg
        zb = A.z + 0.19 * c.sc
        p_top = V(K.x + (A.x - K.x) * (K.z - zb) / (K.z - A.z), K.y + (A.y - K.y) * (K.z - zb) / (K.z - A.z), zb)
        rs = [0.046 * r + 0.0, 0.049 * r + 0.002]
        sh = cloth_tube([A + V(0, 0.0, -0.012), p_top], [0.047 * r, 0.052 * r], [0.049 * r, 0.052 * r], segs=14, res=1, hem1=True, caps=(True, False), thick=0.005, liner=0.015)
        parts_l.append(setm(sh, 'shoes'))
    elif shoes == 'shoe':
        def rl_at(z):
            tt = max(0.0, min(1.0, (K.z - z) / (K.z - A.z)))
            return float(np.interp(tt, [0, 0.35, 1.0], rl))
        zb = A.z + 0.05 * c.sc
        zt = A.z - 0.012
        p_top = V(A.x, A.y, zb)
        sh = cloth_tube([V(A.x, A.y, zt), p_top], [rl_at(zt) + 0.011, rl_at(zb) + 0.012], [(rl_at(zt) + 0.011) * 1.05, (rl_at(zb) + 0.012) * 1.05], segs=12, res=1, hem1=True, caps=(True, False), thick=0.004, liner=0.012)
        parts_l.append(setm(sh, 'shoes'))
    if sock:
        def rl_at2(z):
            tt = max(0.0, min(1.0, (K.z - z) / (K.z - A.z)))
            return float(np.interp(tt, [0, 0.35, 1.0], rl))
        zb = A.z + 0.12 * c.sc
        zlow = A.z + 0.02
        pb = V(K.x + (A.x - K.x) * (K.z - zlow) / (K.z - A.z), K.y + (A.y - K.y) * (K.z - zlow) / (K.z - A.z), zlow)
        p_top = V(K.x + (A.x - K.x) * (K.z - zb) / (K.z - A.z), K.y + (A.y - K.y) * (K.z - zb) / (K.z - A.z), zb)
        r0, r1 = rl_at2(zlow) + 0.0065, rl_at2(zb) + 0.0065
        sb = cloth_tube([pb, p_top], [r0, r1], [r0 * 1.06, r1 * 1.06], segs=12, res=1, hem1=True, caps=(True, False), thick=0.004, liner=0.02)
        parts_l.append(setm(sb, sock))
    B['leg_%s_upper' % t].extend(parts_u)
    B['leg_%s_lower' % t].extend(parts_l)
    fb = foot_geom(c, side, 'boot' if shoes else 'bare')
    B['foot_%s' % t].append(fb)
    # hip blob in pelvis (round the joint)
    ro = (ru[0] + th) * 0.93
    B['pelvis'].append(setm(blob(Hj, (ro, ro, ro), segs=12, rings=8), trouser_mat if legwear != 'none' else 'skin'))


def bust(bm, c, amp=0.016, z=None):
    z = c.rz[4] if z is None else z
    ycen = (prof(c, z)[2] - prof(c, z)[1]) / 2

    def fn(p, n):
        if n.y > -0.05:
            return 0.0
        return amp * (g2(abs(p.x), p.z, 0.058 * c.sc / 1.0, z, 0.045, 0.05)) * smooth(-0.05, -0.6, n.y)
    return displace(bm, fn)


def suspenders(c, x_front=0.075, x_back=0.065, mat='cloth_accent', width=0.028, off=0.03):
    out = []
    zw = c.z['waist'] - 0.04
    zt = c.rz[7] + 0.004
    for sg in (1, -1):
        pts = []
        # front: from the waist up the chest
        for z in np.linspace(zw, c.rz[6], 4):
            hw, yf, yb = prof(c, z)
            x = sg * x_front
            yc = (yb - yf) / 2 + c.ys(z)
            rd = (yf + yb) / 2 + off
            rw = hw + off
            y = yc - rd * math.sqrt(max(0.0, 1 - (x / rw) ** 2))
            pts.append(V(x, y, z))
        hw, yf, yb = prof(c, zt)
        x = sg * (x_front * 1.0)
        yc = (yb - yf) / 2 + c.ys(zt)
        pts.append(V(x, yc - 0.02, zt + 0.012))
        pts.append(V(x * 0.95, yc + 0.03, zt + 0.006))
        for z in np.linspace(c.rz[6], zw, 4):
            hw, yf, yb = prof(c, z)
            x = sg * x_back
            yc = (yb - yf) / 2 + c.ys(z)
            rd = (yf + yb) / 2 + off
            rw = hw + off
            y = yc + rd * math.sqrt(max(0.0, 1 - (x / rw) ** 2))
            pts.append(V(x, y, z))
        rb = ribbon(pts, width, 0.004, axis=(1, 0, 0))
        out.append(setm(rb, mat))
        # buckle clips at the front bottom
        out.append(setm(box(pts[0] + V(0, -0.004, 0.012), (0.026, 0.006, 0.02), bevel=0.002), 'brass'))
    return merge(*out)


def neckerchief(c, mat='cloth_accent', z=None, tail=0.1):
    z = c.rz[8] + 0.012 if z is None else z
    y0 = c.ys(z) + 0.004
    pts = [V(0, y0, z - 0.012), V(0, y0 - 0.002, z + 0.018)]
    r0 = c.neck_r + 0.012
    bm = cloth_tube(pts, [r0 + 0.003, r0 + 0.001], [r0 * 1.04, r0 * 1.02], segs=16, res=1, hem0=True, hem1=True, thick=0.006, liner=0.003,
                    pre=lambda b: radial_folds(b, 0, y0, 6, 0.0025, z + 0.02, z - 0.02, base=1.0))
    out = [bm]
    kn = blob(V(0.012, y0 - r0 - 0.012, z), (0.018, 0.012, 0.015), segs=8, rings=6)
    out.append(kn)
    for sg, ln in ((1, tail), (-1, tail * 0.75)):
        t = loft([V(sg * 0.01 + 0.01, y0 - r0 - 0.014, z - 0.006), V(sg * 0.026 + 0.01, y0 - r0 - 0.026, z - ln * 0.5), V(sg * 0.03 + 0.01, y0 - r0 - 0.032, z - ln)],
                 [0.014, 0.019, 0.013], [0.0035, 0.0035, 0.003], segs=8, res=2, up=(0, -1, 0), cap0=True, cap1=True, cap_push=0.3)
        out.append(t)
    return setm(merge(*out), mat)


def ysurf_torso(c, off=0.0):
    def f(z, x):
        hw, yf, yb = prof(c, z)
        yc = (yb - yf) / 2 + c.ys(z)
        rd = (yf + yb) / 2 + off
        rw = hw + off
        return yc - rd * math.sqrt(max(0.0, 1 - (min(abs(x), rw * 0.985) / rw) ** 2))
    return f


def ysurf_lower(c, off=0.0):
    """front surface of what is under a panel hanging from the waist (skirt if present, else trousers/thighs)."""
    sk = getattr(c, 'skirt_prof', None)

    def f(z, x):
        if sk is not None and z <= sk[0][-1]:
            zs, rws, rds, ycs = sk
            rw = float(np.interp(z, zs, rws)); rd = float(np.interp(z, zs, rds)); yc = float(np.interp(z, zs, ycs))
            return yc - rd * math.sqrt(max(0.0, 1 - (min(abs(x), rw * 0.985) / rw) ** 2)) - off
        if z >= c.rz[1]:
            return ysurf_torso(c, 0.0)(z, x) - off
        # thigh front
        return -(0.104 * c.sc + 0.0) - off
    return f


def panel(c, rows, ysurf, nx=9, off=0.012, bow=0.012, mat='cloth_alt', th=0.004, folds=0.0035, seed=1, nfold=6, stitch=True):
    """Hanging front panel (apron etc.). rows: [(z, halfwidth)] top->bottom."""
    bm = bmesh.new()
    V_ = []
    nr = len(rows)
    for ri, (z, hw) in enumerate(rows):
        row = []
        for i in range(nx):
            u = 2 * i / (nx - 1) - 1
            x = hw * u
            y = ysurf(z, x) - off - bow * (1 - u * u) * (ri / max(1, nr - 1))
            row.append(bm.verts.new(V(x, y, z)))
        V_.append(row)
    for ri in range(nr - 1):
        for i in range(nx - 1):
            bm.faces.new((V_[ri][i], V_[ri + 1][i], V_[ri + 1][i + 1], V_[ri][i + 1]))
    # subdivide once for smoother cloth
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=True, use_smooth_even=True)
    ztop = rows[0][0]; zbot = rows[-1][0]

    def fn(p, n):
        k = smooth(ztop, zbot, p.z)
        return folds * k * math.sin(p.x * 55 / 1.0 * 0.5 * nfold / 6 + 2.0 * mnoise.noise(V(p.x * 6 + seed, p.z * 3, 0)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    displace(bm, fn)
    zmin = min(v.co.z for v in bm.verts)
    bot = sorted([v for v in bm.verts if v.co.z < zmin + 0.0015], key=lambda v: v.co.x)
    bm.normal_update()
    sp = [V(v.co.x, v.co.y, zmin + 0.016) for v in bot]
    sn = [v.normal.copy() for v in bot]
    rim(bm, th)
    setm(bm, mat)
    if stitch and len(sp) > 2:
        bm = merge(bm, stitch_quads(sp, sn, length=0.014, width=0.0024, every=2, lift=0.0008))
    return bm


def stitch_quads(pts, nrms, length=0.011, width=0.0022, every=2, lift=0.0007, mat='leather'):
    bm = bmesh.new()
    for i in range(0, len(pts) - 1, every):
        a, b = V(pts[i]), V(pts[i + 1])
        d = b - a
        if d.length < 1e-5:
            continue
        dirn = d.normalized()
        n = V(nrms[i]).normalized()
        side = n.cross(dirn).normalized()
        half = min(length, d.length * 0.9) / 2
        mid = (a + b) / 2 + n * lift
        vs = [bm.verts.new(mid + dirn * sx * half + side * sy * width / 2) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        try:
            bm.faces.new(vs)
        except ValueError:
            pass
    return setm(bm, mat)


def patch(center, w, h, mat='cloth_accent', normal_y=-1, th=0.004, stitch=True):
    out = [setm(box(center, (w, th, h), bevel=0.0012), mat)]
    if stitch:
        pts, nr = [], []
        y = center.y + normal_y * (th / 2)
        x0, x1, z0, z1 = center.x - w / 2 + 0.006, center.x + w / 2 - 0.006, center.z - h / 2 + 0.006, center.z + h / 2 - 0.006
        n = 6
        path = [(x0 + (x1 - x0) * i / n, z0) for i in range(n + 1)] + [(x1, z0 + (z1 - z0) * i / n) for i in range(1, n + 1)] + \
               [(x1 - (x1 - x0) * i / n, z1) for i in range(1, n + 1)] + [(x0, z1 - (z1 - z0) * i / n) for i in range(1, n)]
        pts = [V(px, y, pz) for px, pz in path]
        nr = [V(0, normal_y, 0)] * len(pts)
        out.append(stitch_quads(pts, nr, length=0.012, width=0.0024, every=1, lift=0.0006, mat='leather'))
    return merge(*out)
