import sys; sys.path.insert(0, "/shared/river/assets/blender")
from vp_mammals import *

ORANGE = '#cf8d4c'; STR = '#7a4220'; WHITE = '#f1e9da'


def stripes(p, w=60.0):
    return sstep(0.25, 0.55, math.sin(p.y * w + 3.0 * fbm(p, 14, 2, 3)))


def coat(p, n):
    c = ORANGE
    s = stripes(p) * sstep(0.0, 0.5, n.z * 0.6 + 0.5 - sstep(0.1, 0.06, p.z) * 0.0) * sstep(0.04, 0.14, p.z)
    c = mixc(c, STR, s * 0.5)
    dor = sstep(0.55, 0.95, n.z) * sstep(0.03, 0.0, abs(p.x)) * 0.5
    c = mixc(c, STR, dor)
    c = mixc(c, WHITE, sstep(0.0, -0.6, n.z) * 0.9)
    c = mixc(c, WHITE, sstep(-0.09, -0.13, p.y) * sstep(0.2, 0.12, p.z) * 0.8)
    c = mixc(c, WHITE, sstep(0.05, 0.02, p.z))
    return mulc(c, 0.92 + 0.16 * (fbm(p, 120, 2, 2) * .5 + .5))


def headcol(p, n, q, uu):
    c = mixc(ORANGE, STR, sstep(0.3, 0.7, math.sin(p.x * 260 + 1.0)) * sstep(0.02, 0.0, abs(p.x) - 0.02) * sstep(-0.01, 0.02, uu) * 0.0
             + sstep(0.35, 0.8, math.sin(p.x * 220)) * sstep(0.03, 0.0, q - 0.02) * 0.7 * sstep(0.0, 0.02, uu))
    c = mixc(c, WHITE, sstep(0.05, 0.09, q) * sstep(0.04, 0.0, uu) * 0.9)
    c = mixc(c, WHITE, sstep(-0.01, -0.025, uu) * 0.9)
    return mulc(c, 0.92 + 0.14 * (fbm(p, 150, 2, 3) * .5 + .5))


def whiskers(hp, D, U):
    bm = bmesh.new()
    bms = []
    for sx in (1, -1):
        for i, (du, ang, dr) in enumerate([(0.006, 0.15, 0.0), (0.0, 0.0, -0.02), (-0.006, -0.15, -0.045)]):
            b0 = hp(0.058, -0.006 + du, 0.014 * sx)
            dv = V(sx * math.cos(ang), -math.sin(ang) * 0.6 - 0.15, dr)
            pts = [b0, b0 + dv * 0.025 + V(0, 0, 0.002), b0 + dv * 0.05 + V(0, 0, -0.002), b0 + dv * 0.075 + V(0, 0, -0.01)]
            bms.append(loft(pts, [0.0007, 0.0006, 0.0005, 0.0002], segs=3, res=2, cap0=False, cap1=False))
    return None, merge(*bms), None


CFG = dict(
    name='cat', k=0.27, hoof_col='#2a211b', nose_col='#d98f8a', eye_col='#9bb94e', coat=coat, headcol=headcol, rough=0.9, foot='paw',
    jawcol=lambda p, n, q, uu: WHITE,
    earcol=lambda p, n, inner, t: mixc('#e6a9a0', ORANGE, t * 0.5) if inner else mixc(ORANGE, STR, t * 0.4),
    pawcol=lambda p, n: WHITE,
    head_extra=whiskers,
    body=dict(ys=[-0.17, -0.11, -0.02, 0.06, 0.12, 0.17, 0.195], zc=[0.18, 0.18, 0.175, 0.175, 0.18, 0.185, 0.18],
              rx=[0.035, 0.052, 0.058, 0.05, 0.056, 0.05, 0.03], rz=[0.055, 0.075, 0.08, 0.065, 0.07, 0.062, 0.04],
              blobs=[((0.035, 0.125, 0.17), (0.03, 0.06, 0.06), (0, 0, 0)), ((0.03, -0.1, 0.18), (0.025, 0.05, 0.06), (0, 0, 0))],
              voxel=0.0055, smooth=8, pivz=0.17, noise=dict(amp=0.0006, freq=120, seed=1)),
    neck=dict(pts=[(0, -0.09, 0.2), (0, -0.14, 0.225), (0, -0.18, 0.245)], rx=[0.044, 0.038, 0.032], rz=[0.052, 0.044, 0.036], pivot=(0, -0.1, 0.205)),
    head=dict(P0=(0, -0.195, 0.255), D=(0, -0.93, -0.3), ts=[-0.03, 0.0, 0.025, 0.045, 0.062, 0.073],
              rx=[0.034, 0.044, 0.045, 0.037, 0.027, 0.022], rz=[0.032, 0.04, 0.04, 0.032, 0.024, 0.02], ups=[0, 0, 0, -0.002, -0.004, -0.004],
              blobs=[(0.06, -0.012, 0.016, (0.014, 0.022, 0.016), (0, 0, 0))],
              voxel=0.003, nose=(0.073, 0.002, 0.008, 0.006, 0.0055), nostril=(0.078, 0.0, 0.0035, 0.0018),
              eye=(0.03, 0.016, 0.028, 0.0095), pupil=(0.6, 0.8, 2.0)),
    jaw=dict(t=0.035, u=-0.016, ts=[-0.003, 0.015, 0.032, 0.046, 0.054], rx=[0.014, 0.018, 0.016, 0.012, 0.01], rz=[0.008, 0.01, 0.009, 0.007, 0.006], droop=-0.001),
    ear=dict(base=(0.014, 0.034, 0.024), tip=(0.014, 0.0, 0.05), nrm=(0.3, -1.0, 0.1), w=0.025, th=0.0025, bulge=0.12, curve=(0, 0, 0)),
    tail=dict(pts=[(0, 0.175, 0.19), (0, 0.255, 0.20), (0, 0.32, 0.255), (0, 0.35, 0.34), (0, 0.345, 0.43), (0, 0.31, 0.475)],
              rx=[0.018, 0.017, 0.015, 0.014, 0.0135, 0.011], rz=[0.018, 0.017, 0.015, 0.014, 0.0135, 0.011]),
    tailcol=lambda p, n: mixc(ORANGE, STR, sstep(0.3, 0.6, math.sin(p.y * 160 + p.z * 160)) * 0.8 + sstep(0.42, 0.46, p.z) * 0.6),
    legs=dict(
        front=dict(hip=(0.04, -0.10, 0.17), mid=(0.038, -0.104, 0.13), knee=(0.037, -0.106, 0.085), fet=(0.034, -0.1, 0.03), toe=(0.034, -0.11, 0.0),
                   ur=([0.022, 0.017, 0.013], [0.028, 0.019, 0.014]), lr=([0.012, 0.0095, 0.009], [0.014, 0.011, 0.01]), paw=(0.0135, 0.022, 0.0125)),
        hind=dict(hip=(0.042, 0.115, 0.18), mid=(0.046, 0.09, 0.115), knee=(0.036, 0.16, 0.075), fet=(0.032, 0.145, 0.028), toe=(0.032, 0.13, 0.0),
                  ur=([0.03, 0.022, 0.012], [0.04, 0.03, 0.014]), lr=([0.012, 0.009, 0.0085], [0.015, 0.0105, 0.0095]), paw=(0.0135, 0.022, 0.0125))))

res = build(CFG)
meta = make_meta(CFG, 'domestic tabby cat', 0.25, 0.5, 0.4, cycle=(0.7, 0.4),
                 swing={'upper': [-32, 32], 'lower_fore': [0, 55], 'lower_hind': [-60, 10], 'paw': [-15, 20]},
                 graze={'neck_rot_x_deg': 30, 'head_rot_x_deg': 25, 'jaw_chew_deg': [0, 8], 'note': 'drinking/eating pose; positive X rotation pitches the free end downward'},
                 idle={'head_bob_deg': 4, 'ear_flick_deg': 20, 'tail_sway_deg': 18, 'tail_sway_axis': 'Z, slow sway ~0.5 Hz', 'breath': 'scale body Y 1.0..1.02 at 0.6 Hz'})
finish(CFG, res, 'cat', meta,
       [((1.3, 0.1, 0.4), (0, 0.05, 0.2)), ((0.1, -1.3, 0.45), (0, 0, 0.2)), ((1.0, -1.0, 0.6), (0, 0, 0.2)), ((0.35, -0.7, 0.4), (0, -0.15, 0.22), 60)],
       (0, 0, 0.2))
