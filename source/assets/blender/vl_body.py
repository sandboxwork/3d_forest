"""vl_body: skeleton context, body shells, hands, feet for the villager characters."""
import sys
sys.path.insert(0, '/shared/river/assets/blender')
from vl_lib import *

LM = {
    'adult': dict(sh=.815, neck=.80, waist=.605, hip=.525, crotch=.47, knee=.285, ankle=.04, elbow=.633, wrist=.485),
    'child': dict(sh=.765, neck=.745, waist=.575, hip=.50, crotch=.455, knee=.265, ankle=.045, elbow=.575, wrist=.445),
}
# (zfrac(adult), hw, yf, yb) at H = 1.75
RING = [(.455, .170, .102, .102), (.51, .188, .110, .118), (.605, .152, .098, .098), (.675, .158, .104, .100),
        (.725, .168, .116, .098), (.775, .172, .100, .090), (.808, .166, .084, .080), (.826, .118, .070, .066),
        (.840, .064, .060, .058)]
WF = {'m': [1, 1, 1, 1, 1, 1, 1, 1, 1], 'f': [1.0, 1.07, .86, .88, .92, .92, .88, .9, .93],
      'c': [1.0, 1.0, .98, .92, .9, .92, .92, 1.0, 1.05]}
DF = {'m': [1, 1, 1, 1, 1, 1, 1, 1, 1], 'f': [1, 1.0, .95, 1.0, 1.08, 1.0, 1, 1, 1],
      'c': [1.1, 1.12, 1.12, 1.08, 1.0, 1.0, 1.0, 1.0, 1.0]}


class Ctx:
    pass


def make_ctx(cfg):
    c = Ctx()
    c.cfg = cfg
    H = cfg['H']
    c.H = H
    c.sc = H / 1.75
    c.kind = cfg.get('kind', 'adult')
    c.sex = cfg['sex']
    c.z = {k: v * H for k, v in LM[c.kind].items()}
    c.stoop = cfg.get('stoop', 0.0)
    b = cfg.get('build', {})
    c.b = b
    wm = b.get('w', 1.0); dm = b.get('d', 1.0)
    key = 'c' if c.kind == 'child' else c.sex
    zh, zs = c.z['hip'], c.z['sh']
    rz, rhw, ryf, ryb = [], [], [], []
    for i, (zf, hw, yf, yb) in enumerate(RING):
        rz.append(zh + (zf - .525) / (.815 - .525) * (zs - zh))
        k = c.sc if c.kind == 'adult' else c.sc * 1.0
        mid = b.get('belly', 0.0) * math.exp(-((i - 2.0) / 1.2) ** 2)
        rhw.append(hw * k * WF[key][i] * wm)
        ryf.append(yf * k * DF[key][i] * dm + mid * c.sc)
        ryb.append(yb * k * DF[key][i] * dm)
    c.rz, c.rhw, c.ryf, c.ryb = np.array(rz), np.array(rhw), np.array(ryf), np.array(ryb)
    c.head_h = cfg.get('head_h', H / (5.5 if c.kind == 'child' else 7.5))
    c.hs = c.head_h / 0.2335
    c.F = cfg['face']
    # spine offsets (stoop = forward shift of the shoulder line)
    c.hs_z = c.hs
    c.sw = {'m': 0.165, 'f': 0.145, 'c': 0.150}[key] * c.sc * b.get('sh', 1.0) * (1.0 if c.kind == 'adult' else 0.97)
    c.neck_r = {'m': .057, 'f': .047, 'c': .040}[key] * (c.sc if c.kind == 'adult' else c.sc * 1.05) * b.get('neck', 1.0)
    c.hip_x = {'m': 0.092, 'f': 0.098, 'c': 0.080}[key] * c.sc * b.get('hipx', 1.0)
    c.arm_r = b.get('arm', 1.0) * c.sc * {'m': 1.1, 'f': 0.92, 'c': 0.85}[key]
    c.leg_r = b.get('leg', 1.0) * c.sc * {'m': 1.05, 'f': 0.97, 'c': 0.85}[key]
    c.nb = V(0, c.ys(c.z['neck']), c.z['neck'])
    c.nb.y += 0.0
    c.head_c = V(0, c.nb.y - 0.012 * c.hs - c.stoop * 0.55, H - F_top(c) * c.hs)
    c.key = key
    import vl_lib
    vl_lib.STATE['head_c'] = c.head_c
    arm(c)
    legs(c)
    return c


def F_top(c):
    return c.F['Ht']


def _ys(c, z):
    return -c.stoop * smooth(c.z['hip'], c.z['sh'], z) ** 1.6


Ctx.ys = lambda self, z: _ys(self, z)


def prof(c, z):
    return (float(np.interp(z, c.rz, c.rhw)), float(np.interp(z, c.rz, c.ryf)), float(np.interp(z, c.rz, c.ryb)))


def shell(c, z0, z1, off=0.0, n=8, offd=None, zpow=1.0):
    """pts, rw, rd for a tube following the torso profile between z0 and z1 (bottom->top), offset by off (m)."""
    offd = off if offd is None else offd
    pts, rw, rd = [], [], []
    for i in range(n):
        t = i / (n - 1)
        z = z0 + (z1 - z0) * t
        hw, yf, yb = prof(c, z)
        pts.append(V(0, (yb - yf) / 2 + c.ys(z), z))
        rw.append(hw + off)
        rd.append((yf + yb) / 2 + offd)
    return pts, rw, rd


# ------------------------------------------------------------------ arms / legs joints
def arm(c):
    b = c.b
    c.arms = {}
    abd = math.radians(b.get('abd', 9))
    for side in (1, -1):
        flex = math.radians(c.cfg.get('elbow_flex', {}).get(side, 10))
        fwd1 = math.radians(c.cfg.get('arm_fwd', {}).get(side, 4))
        zs = c.z['sh']
        S = V(side * c.sw, c.ys(zs) + 0.0, zs - 0.05 * c.sc)
        L1 = (S.z - c.z['elbow']) * 1.02
        L2 = (c.z['elbow'] - c.z['wrist']) * 1.05
        a1 = abd if not c.cfg.get('abd_side') else math.radians(c.cfg['abd_side'][side])
        d1 = V(side * math.sin(a1), -math.sin(fwd1), -math.cos(a1) * math.cos(fwd1)).normalized()
        E = S + d1 * L1
        a2 = math.radians(c.cfg.get('abd2', {}).get(side, 6))
        d2 = V(side * math.sin(a2), -math.sin(flex + fwd1), -math.cos(flex + fwd1) * math.cos(a2)).normalized()
        W = E + d2 * L2
        c.arms[side] = dict(S=S, E=E, W=W, d1=d1, d2=d2)


def legs(c):
    c.legs = {}
    for side in (1, -1):
        hx = c.hip_x
        Hj = V(side * hx, 0.0, c.z['hip'])
        K = V(side * (hx + 0.004), -0.006, c.z['knee'])
        A = V(side * (hx + 0.012), 0.004, c.z['ankle'])
        c.legs[side] = dict(H=Hj, K=K, A=A)


def side_tag(side):
    return 'l' if side > 0 else 'r'


# ------------------------------------------------------------------ hand
def hand_frame(c, side, f_dir, scale=None):
    s = scale if scale is not None else c.sc * (1.08 if c.key == 'm' else (0.95 if c.key == 'f' else 0.8)) * c.b.get('hand', 1.0)
    f = f_dir.normalized()
    p = V(-side, 0, 0)
    p = (p - f * p.dot(f)).normalized()
    e_t = (f.cross(p) * (-side)).normalized()
    return f, p, e_t, s


def grip_point(c, side):
    W = c.arms[side]['W']
    f, p, e_t, s = c.hf[side]
    return W + f * 0.056 * s + p * 0.018 * s


def hand_geom(c, side, W, f_dir, mode='relaxed', scale=None, thumb_open=0.0, glove=None):
    """Hand mesh (skin) in world coords. W: wrist point, f_dir: finger direction. mode relaxed|fist|grip.
    palm faces the body (toward -side*X) for relaxed. Returns bmesh."""
    f, p, e_t, s = hand_frame(c, side, f_dir, scale)
    out = []

    def pt(u, v, w):
        return W + f * u + e_t * v + p * w

    # palm
    pm = loft([pt(-0.012 * s, 0, 0), pt(0.02 * s, 0, 0.001), pt(0.058 * s, 0, 0), pt(0.092 * s, 0, 0)],
              [0.029 * s, 0.037 * s, 0.043 * s, 0.043 * s], [0.014 * s, 0.017 * s, 0.017 * s, 0.014 * s], segs=8, res=1,
              up=p, cap0=True, cap1=True, cap_push=0.4)
    out.append(pm)
    curls = {'relaxed': (14, 22, 16), 'fist': (80, 85, 55), 'grip': (62, 70, 50)}[mode]
    spread = [-3, -1, 2, 6]
    vo = [0.0305, 0.0105, -0.0095, -0.0275]
    ln = [0.074, 0.082, 0.077, 0.06]
    for i in range(4):
        cs = [math.radians(a * (1.0 + 0.12 * (i - 1.5) * (0 if mode == 'relaxed' else 0.4))) for a in curls]
        pts = [pt(0.088 * s, vo[i] * s, 0.0)]
        ang = 0.0
        d_lat = e_t * math.sin(math.radians(spread[i]))
        pos = pts[0]
        seg_l = [ln[i] * s * k for k in (0.44, 0.31, 0.25)]
        for j in range(3):
            ang += cs[j]
            d = f * math.cos(ang) + p * math.sin(ang) + d_lat
            pos = pos + d.normalized() * seg_l[j]
            pts.append(pos)
        rr = [0.0092 * s, 0.0082 * s, 0.0072 * s, 0.006 * s]
        out.append(loft(pts, rr, [r * 0.92 for r in rr], segs=6, res=1, up=p, cap0=False, cap1=True, cap_push=0.9))
    # thumb
    tb = pt(0.030 * s, 0.027 * s, 0.012 * s)
    to = math.radians(20 + 25 * thumb_open)
    cur = {'relaxed': 18, 'fist': 40, 'grip': 30}[mode]
    d1 = (f * 0.80 + e_t * (0.42 + thumb_open * 0.3) + p * 0.24).normalized()
    t1 = tb + d1 * 0.029 * s
    d2 = (d1 * math.cos(math.radians(cur)) + p * math.sin(math.radians(cur)) + f * 0.1).normalized()
    t2 = t1 + d2 * 0.025 * s
    d3 = (d2 * math.cos(math.radians(cur)) + p * math.sin(math.radians(cur))).normalized()
    t3 = t2 + d3 * 0.021 * s
    out.append(loft([tb, t1, t2, t3], [0.0125 * s, 0.0108 * s, 0.0092 * s, 0.0078 * s],
                    [0.0112 * s, 0.0098 * s, 0.0085 * s, 0.0072 * s], segs=6, res=1, up=p, cap0=True, cap1=True, cap_push=0.9))
    # thenar / palm pad bulge
    out.append(blob(pt(0.04 * s, 0.024 * s, 0.014 * s), (0.026 * s, 0.015 * s, 0.011 * s), segs=8, rings=6))
    bm = merge(*out)
    setm(bm, 'skin')
    return bm, (f, p, e_t)


# ------------------------------------------------------------------ foot
def foot_geom(c, side, kind='boot'):
    """returns dict of bmeshes: 'foot' (in foot part) for shoe body + sole.  Materials 'shoes' (or skin)."""
    A = c.legs[side]['A']
    s = c.sc * c.b.get('foot', 1.0) * (1.0 if c.kind == 'adult' else 0.95)
    tw = math.radians(c.cfg.get('toe_out', 8))
    d = V(side * math.sin(tw), -math.cos(tw), 0)
    base = V(A.x, A.y, 0)
    heel_back, toe_fwd = 0.072 * s, 0.205 * s
    if c.key == 'f':
        heel_back, toe_fwd = 0.066 * s, 0.185 * s
    ts = [-heel_back, -0.035 * s, 0.045 * s, 0.12 * s, 0.17 * s, toe_fwd]
    cz = [0.056, 0.062, 0.056, 0.047, 0.040, 0.033]
    hh = [0.044, 0.050, 0.044, 0.035, 0.029, 0.021]
    wd = [0.036, 0.042, 0.049, 0.050, 0.047, 0.034]
    pts = [base + d * t + V(0, 0, z) for t, z in zip(ts, cz)]
    for i in range(len(pts)):
        pass
    body = loft(pts, [w * s for w in wd], [h * s for h in hh], segs=10, res=2, up=(0, 0, 1), cap0=True, cap1=True, cap_push=0.7, power=2.4)
    sole_pts = [base + d * t + V(0, 0, 0.009) for t in (ts[0] - 0.003, ts[1], ts[3], toe_fwd + 0.004)]
    sole = loft(sole_pts, [0.038 * s, 0.0485 * s, 0.0515 * s, 0.037 * s], [0.0105] * 4, segs=10, res=2, up=(0, 0, 1),
                cap0=True, cap1=True, cap_push=0.5, power=3.2)
    heel = box(base + d * (-heel_back * 0.55) + V(0, 0, 0.018), (0.07 * s, 0.05 * s, 0.032), bevel=0.006)
    rot_about(heel, 'Z', math.atan2(d.x, -d.y) * -1 if False else 0.0)
    parts = [body, sole]
    if kind in ('boot', 'shoe'):
        bm = merge(*parts)
        setm(bm, 'shoes')
        return bm
    # bare / skin foot
    bm = merge(body)
    setm(bm, 'skin')
    return bm
