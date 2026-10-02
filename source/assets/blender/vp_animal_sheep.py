import sys; sys.path.insert(0, "/shared/river/assets/blender")
from vp_mammals import *
import numpy as np

WOOL = '#e9e1cf'; DARK = '#33281f'
rnd = random.Random(21)
BY = [-0.40, -0.30, -0.12, 0.08, 0.26, 0.38, 0.44]
BZ = [0.60, 0.58, 0.56, 0.55, 0.56, 0.57, 0.56]
BRX = [0.10, 0.15, 0.17, 0.17, 0.165, 0.14, 0.07]
BRZ = [0.13, 0.18, 0.20, 0.20, 0.19, 0.16, 0.09]


def coat(p, n):
    c = mixc(WOOL, '#cfc3a8', 0.5 * (fbm(p, 9, 3, 7) * .5 + .5))
    r = math.sqrt((p.x / 0.2) ** 2 + ((p.z - 0.57) / 0.24) ** 2)
    c = mulc(c, 0.72 + 0.34 * min(1.0, r * r * 0.9))
    c = mixc(c, '#b0a48a', sstep(0.42, 0.33, p.z) * 0.7)
    if p.z < 0.36:
        c = mixc(c, DARK, sstep(0.36, 0.28, p.z) * (1.0 if abs(p.y) > 0.25 or p.z < 0.3 else 0.6))
    return c


def lumps(rng_y, n, rad, ang=(-0.4, math.pi + 0.4), spread=1.0, shrink=0.93):
    out = []
    for _ in range(n):
        y = rnd.uniform(*rng_y)
        a = rnd.uniform(*ang)
        rx = float(np.interp(y, BY, BRX)); rz = float(np.interp(y, BY, BRZ)); zc = float(np.interp(y, BY, BZ))
        c = V(rx * math.cos(a) * shrink, y, zc + rz * math.sin(a) * shrink)
        r = rnd.uniform(rad[0], rad[1])
        out.append(blob(c, (r, r * rnd.uniform(0.9, 1.3), r * rnd.uniform(0.85, 1.0)), rot=(rnd.uniform(0, 3), rnd.uniform(0, 3), rnd.uniform(0, 3)), segs=8, rings=5))
    return out


def post_body(bm):
    # rows of lumps to guarantee even coverage + random extras
    ls = lumps((-0.40, 0.44), 230, (0.055, 0.085))
    return merge(bm, *ls)


def post_neck(bm):
    ls = []
    for i in range(34):
        t = rnd.uniform(0.0, 1.0); a = rnd.uniform(0, 2 * math.pi)
        c = V(0, -0.30 - 0.2 * t, 0.64 + 0.04 * t + 0.0) + V(0.09 * math.cos(a), 0, 0.10 * math.sin(a))
        r = rnd.uniform(0.045, 0.07)
        ls.append(blob(c, (r, r * 1.1, r), rot=(rnd.uniform(0, 3), 0, rnd.uniform(0, 3)), segs=8, rings=5))
    return merge(bm, *ls)


def headcol(p, n, q, uu):
    c = mixc('#3b2f28', '#2a201b', 0.5 + 0.5 * fbm(p, 30, 2, 3))
    c = mixc(c, '#5a4a40', sstep(0.12, 0.2, q) * 0.7)
    if q < 0.05 and uu > 0.02:
        c = mixc(c, WOOL, 0.8)   # woolly topknot
    return c


CFG = dict(
    name='sheep', k=0.72, hoof_col='#241d19', nose_col='#4a3a36', eye_col='#d3b75a', coat=coat, headcol=headcol, rough=0.95,
    jawcol=lambda p, n, q, uu: mixc('#35291f', '#6a5a52', sstep(0.1, 0.18, q)),
    earcol=lambda p, n, inner, t: mixc('#7a6458', '#33271f', t * 0.5) if inner else '#33271f',
    body=dict(ys=BY, zc=BZ, rx=BRX, rz=BRZ, voxel=0.02, smooth=8, pivz=0.56, segs=24, noise=None),
    neck=dict(pts=[(0, -0.28, 0.62), (0, -0.38, 0.66), (0, -0.46, 0.69)], rx=[0.11, 0.095, 0.07], rz=[0.13, 0.11, 0.085], pivot=(0, -0.30, 0.64)),
    head=dict(P0=(0, -0.50, 0.70), D=(0, -0.88, -0.47), ts=[-0.04, 0.02, 0.08, 0.14, 0.19, 0.225],
              rx=[0.04, 0.05, 0.046, 0.036, 0.03, 0.028], rz=[0.056, 0.066, 0.058, 0.044, 0.036, 0.03],
              ups=[0, 0, 0, -0.004, -0.01, -0.01],
              blobs=[(0.07, -0.01, 0.035, (0.02, 0.04, 0.03), (0, 0, 0)), (0.02, 0.04, 0.0, (0.035, 0.04, 0.03), (0, 0, 0))],
              voxel=0.0055, nose=(0.222, -0.008, 0.024, 0.012, 0.017), nostril=(0.232, -0.002, 0.012, 0.0055),
              eye=(0.09, 0.016, 0.046, 0.0105), pupil=(1.6, 0.5, 1.0)),
    jaw=dict(t=0.06, u=-0.035, ts=[-0.005, 0.04, 0.09, 0.14, 0.17], rx=[0.02, 0.024, 0.021, 0.018, 0.016], rz=[0.014, 0.016, 0.014, 0.012, 0.011], droop=-0.002),
    ear=dict(base=(0.0, 0.035, 0.045), tip=(0.12, 0.03, -0.035), nrm=(0.2, -0.3, 0.9), w=0.032, th=0.004, bulge=0.4, curve=(0, 0, -0.01)),
    tail=dict(pts=[(0, 0.39, 0.60), (0, 0.46, 0.55), (0, 0.49, 0.46), (0, 0.49, 0.40)],
              rx=[0.05, 0.05, 0.045, 0.03], rz=[0.05, 0.05, 0.045, 0.03]),
    tailcol=lambda p, n: mulc(mixc(WOOL, '#cfc3a8', 0.4), 0.9),
    legs=dict(
        front=dict(hip=(0.10, -0.27, 0.48), knee=(0.09, -0.285, 0.28), fet=(0.085, -0.275, 0.10), toe=(0.085, -0.30, 0.004),
                   ur=([0.05, 0.036, 0.026], [0.06, 0.042, 0.03]), lr=([0.026, 0.02, 0.019], [0.028, 0.022, 0.021]),
                   hoof=(0.017, 0.02, 0.022, 0.02, 0.025, 0.03)),
        hind=dict(hip=(0.10, 0.30, 0.48), mid=(0.10, 0.27, 0.38), knee=(0.085, 0.37, 0.28), fet=(0.08, 0.35, 0.10), toe=(0.08, 0.33, 0.004),
                  ur=([0.06, 0.04, 0.026], [0.08, 0.052, 0.03]), lr=([0.026, 0.02, 0.019], [0.03, 0.023, 0.021]),
                  hoof=(0.017, 0.02, 0.022, 0.02, 0.025, 0.03))),
    post_body=post_body, post_neck=post_neck)

res = build(CFG)
meta = make_meta(CFG, 'domestic sheep (blackface, woolly)', 0.72, 1.1, 0.95, cycle=(1.0, 0.55),
                 swing={'upper': [-26, 26], 'lower_fore': [0, 50], 'lower_hind': [-55, 8], 'hoof': [-12, 18]},
                 graze={'neck_rot_x_deg': 40, 'head_rot_x_deg': 25, 'jaw_chew_deg': [0, 9], 'note': 'positive X rotation pitches the free end downward'},
                 idle={'head_bob_deg': 3, 'ear_flick_deg': 20, 'tail_flick_deg': 10, 'breath': 'scale body Y 1.0..1.012 at 0.3 Hz'})
finish(CFG, res, 'sheep', meta,
       [((3.0, 0.2, 0.8), (0, 0, 0.5)), ((0.2, -3.0, 0.9), (0, 0, 0.5)), ((2.2, -2.2, 1.3), (0, 0, 0.5)), ((1.0, -1.5, 0.95), (0, -0.4, 0.62), 60)],
       (0, 0, 0.5))
