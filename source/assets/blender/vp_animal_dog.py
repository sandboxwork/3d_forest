import sys; sys.path.insert(0, "/shared/river/assets/blender")
from vp_mammals import *

TAN = '#b07a45'; BROWN = '#5c3b22'; CREAM = '#eadcc0'


def coat(p, n):
    c = TAN
    nz = fbm(p, 10, 3, 4) * 0.5 + 0.5
    dor = sstep(0.2, 0.85, n.z) * sstep(0.1, 0.35, nz + 0.2 * n.z) * sstep(0.62, 0.52, abs(p.x) * 4 + 0.2)
    c = mixc(c, BROWN, dor * 0.85 * sstep(-0.33, -0.08, p.y))
    c = mixc(c, mixc(TAN, CREAM, 0.6), sstep(0.2, -0.5, n.z) * 0.8)
    chest = sstep(-0.18, -0.25, p.y) * sstep(0.5, 0.36, p.z) * sstep(0.1, 0.03, abs(p.x))
    c = mixc(c, '#f3ecdc', chest)
    c = mixc(c, '#f1e9d8', sstep(0.12, 0.06, p.z))                       # socks
    c = mixc(c, '#f1e9d8', sstep(0.0, -0.15, n.y) * sstep(0.45, 0.3, p.z) * sstep(-0.15, -0.28, p.y) * 0.5)
    return mulc(c, 0.9 + 0.2 * (fbm(p, 55, 2, 2) * .5 + .5))


def headcol(p, n, q, uu):
    c = mixc(TAN, BROWN, sstep(0.05, 0.0, q) * 0.0 + sstep(0.0, 0.5, n.z) * sstep(0.0, 0.12, uu + 0.02) * 0.35)
    c = mixc(c, '#35261c', sstep(0.13, 0.2, q) * 0.8 * sstep(-0.01, 0.02, uu + 0.03))
    c = mixc(c, '#f1e8d4', sstep(0.03, 0.0, abs(p.x)) * sstep(0.0, 0.05, q) * sstep(0.13, 0.2, q) * 0.0 + sstep(0.012, 0.0, abs(p.x)) * sstep(0.0, 0.03, uu) * 0.8)
    c = mixc(c, CREAM, sstep(-0.025, -0.04, uu) * 0.8)
    return mulc(c, 0.9 + 0.2 * (fbm(p, 60, 2, 3) * .5 + .5))


CFG = dict(
    name='dog', k=0.58, hoof_col='#2a211b', nose_col='#141010', eye_col='#3a2210', coat=coat, headcol=headcol, rough=0.85, foot='paw',
    jawcol=lambda p, n, q, uu: mixc('#eadcc0', '#2c2018', sstep(0.12, 0.2, q) * 0.5),
    earcol=lambda p, n, inner, t: mixc('#7a5238', '#4a2f1b', t * 0.5),
    pawcol=lambda p, n: mixc('#f1e9d8', '#c9bba2', sstep(0.02, 0.0, p.z) * 0.5),
    body=dict(ys=[-0.32, -0.22, -0.05, 0.12, 0.26, 0.36, 0.40], zc=[0.42, 0.42, 0.40, 0.42, 0.42, 0.43, 0.42],
              rx=[0.06, 0.09, 0.095, 0.08, 0.085, 0.075, 0.04], rz=[0.10, 0.15, 0.16, 0.115, 0.125, 0.11, 0.06],
              blobs=[((0.06, 0.26, 0.40), (0.05, 0.11, 0.12), (0, 0, 0)), ((0.06, -0.18, 0.40), (0.04, 0.1, 0.12), (0, 0, 0))],
              voxel=0.0095, smooth=8, pivz=0.40, noise=dict(amp=0.0012, freq=40, seed=1)),
    neck=dict(pts=[(0, -0.15, 0.47), (0, -0.25, 0.53), (0, -0.34, 0.595)], rx=[0.07, 0.06, 0.05], rz=[0.082, 0.07, 0.06], pivot=(0, -0.19, 0.51),
              noise=dict(amp=0.0015, freq=40, seed=2)),
    head=dict(P0=(0, -0.37, 0.615), D=(0, -0.93, -0.36), ts=[-0.04, 0.02, 0.07, 0.12, 0.17, 0.225],
              rx=[0.045, 0.054, 0.05, 0.038, 0.032, 0.03], rz=[0.052, 0.058, 0.05, 0.036, 0.03, 0.026], ups=[0, 0, 0, -0.004, -0.008, -0.006],
              blobs=[(0.06, -0.012, 0.04, (0.022, 0.05, 0.035), (0.3, 0, 0)), (0.1, 0.03, 0.025, (0.02, 0.025, 0.012), (-0.3, 0, 0)),
                     (0.17, -0.014, 0.018, (0.014, 0.035, 0.014), (0, 0, 0))],
              voxel=0.0045, nose=(0.228, -0.004, 0.019, 0.012, 0.014), nostril=(0.238, 0.0, 0.009, 0.0042),
              eye=(0.1, 0.022, 0.034, 0.0095), pupil=(0.9, 0.9, 0.9)),
    jaw=dict(t=0.06, u=-0.024, ts=[-0.005, 0.04, 0.09, 0.14, 0.175], rx=[0.022, 0.026, 0.023, 0.019, 0.016], rz=[0.015, 0.018, 0.015, 0.012, 0.011], droop=-0.002),
    ear=dict(base=(0.015, 0.05, 0.038), tip=(0.045, 0.03, -0.115), nrm=(1.0, -0.1, 0.35), w=0.04, th=0.004, bulge=0.3, curve=(0.012, 0.0, 0.0)),
    tail=dict(pts=[(0, 0.36, 0.44), (0, 0.45, 0.48), (0, 0.51, 0.56), (0, 0.51, 0.64)], rx=[0.03, 0.026, 0.021, 0.008], rz=[0.03, 0.026, 0.021, 0.008]),
    tailcol=lambda p, n: mixc(mixc(BROWN, TAN, sstep(0.45, 0.6, p.z)), '#f1e9d8', sstep(0.6, 0.66, p.z)),
    legs=dict(
        front=dict(hip=(0.07, -0.21, 0.38), mid=(0.065, -0.225, 0.29), knee=(0.062, -0.235, 0.20), fet=(0.058, -0.225, 0.065), toe=(0.058, -0.25, 0.0),
                   ur=([0.05, 0.036, 0.027], [0.06, 0.04, 0.03]), lr=([0.026, 0.02, 0.02], [0.03, 0.022, 0.02]), paw=(0.027, 0.045, 0.025)),
        hind=dict(hip=(0.065, 0.30, 0.39), mid=(0.075, 0.25, 0.27), knee=(0.06, 0.38, 0.17), fet=(0.055, 0.36, 0.062), toe=(0.055, 0.34, 0.0),
                  ur=([0.05, 0.046, 0.026], [0.07, 0.06, 0.032]), lr=([0.026, 0.019, 0.019], [0.032, 0.022, 0.02]), paw=(0.026, 0.045, 0.025))))

res = build(CFG)
meta = make_meta(CFG, 'village dog (tan mutt)', 0.55, 0.85, 0.85, cycle=(0.9, 0.5),
                 swing={'upper': [-30, 30], 'lower_fore': [0, 50], 'lower_hind': [-55, 10], 'paw': [-15, 20]},
                 graze={'neck_rot_x_deg': 35, 'head_rot_x_deg': 20, 'jaw_chew_deg': [0, 10], 'note': 'sniffing pose; positive X rotation pitches the free end downward'},
                 idle={'head_bob_deg': 5, 'ear_flick_deg': 15, 'tail_wag_deg': 25, 'tail_wag_axis': 'Z (side to side), ~4 Hz when happy', 'breath': 'scale body Y 1.0..1.015 at 0.5 Hz'})
finish(CFG, res, 'dog', meta,
       [((2.4, 0.2, 0.7), (0, 0, 0.35)), ((0.2, -2.4, 0.8), (0, 0, 0.35)), ((1.8, -1.8, 1.0), (0, 0, 0.35)), ((0.7, -1.2, 0.75), (0, -0.3, 0.52), 60)],
       (0, 0, 0.35))
