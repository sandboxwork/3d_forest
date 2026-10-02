"""Shared materials + helpers for meadow flowers."""
from flora_lib import *


def init_mats():
    mat('stem_green', '#7aa23f', rough=0.6, sss=0.1)
    mat('stem_grey', '#8aa066', rough=0.65)
    mat('leaf_green', '#5e9a34', rough=0.5, sss=0.15)
    mat('leaf_dark', '#3f7a2a', rough=0.5)
    mat('leaf_grey', '#8fae84', rough=0.6)
    mat('sepal_green', '#6c9a3a', rough=0.55)
    mat('petal_white', '#fdfcf6', rough=0.6, sss=0.25)
    mat('petal_yellow', '#f6d21c', rough=0.45, sss=0.2)
    mat('petal_yellow_glossy', '#ffd81a', rough=0.25, sss=0.2)
    mat('petal_orange', '#f58a14', rough=0.55, sss=0.2)
    mat('petal_red', '#e6281a', rough=0.6, sss=0.25)
    mat('petal_pink', '#f08ab5', rough=0.6, sss=0.25)
    mat('petal_magenta', '#d6348f', rough=0.6, sss=0.2)
    mat('petal_purple', '#7a4cc4', rough=0.6, sss=0.2)
    mat('petal_blue', '#4a78ea', rough=0.6, sss=0.2)
    mat('petal_violet', '#6a52d8', rough=0.6, sss=0.2)
    mat('disc_yellow', '#f4c21a', rough=0.75)
    mat('disc_brown', '#4a2a14', rough=0.8)
    mat('anther_dark', '#2a1c26', rough=0.5)
    mat('stamen_yellow', '#f4d23a', rough=0.6)
    mat('seed_white', '#f1f0ea', rough=0.7)
    mat('bract_dark', '#4c3a2a', rough=0.7)
    mat('bark_cane', '#6a4a36', rough=0.7)
    mat('soil', '#3c2a1e', rough=0.95)


def gstem(g, pts, r0, r1, sides=5, c0='#567a2c', c1='#7aa23f', m='stem_green', cap=True, swell=0.0):
    n = len(pts)
    t = np.linspace(0, 1, n)
    r = r0 + (r1 - r0) * t ** 0.8
    if swell:
        r = r * (1 + swell * np.exp(-(t / 0.12) ** 2))
    g.add(m, tube(pts, r, sides=sides, cols=grad(t, [(0, c0), (1, c1)]), cap=cap))


def side_branch(pts, t, rng, length, out=0.5, az=None):
    pos, tan = pathpt(pts, t)
    az = rng.uniform(0, TAU) if az is None else az
    rad = np.array([math.cos(az), math.sin(az), 0.0]); Z = np.array([0, 0, 1.0])
    p0 = pos
    p3 = p0 + rad * length * out + Z * length * (1 - out * 0.4)
    p1 = p0 + rad * length * out * 0.6 + Z * length * 0.12
    p2 = p3 - Z * length * 0.35 - rad * length * 0.05
    n = 5 if LOD == 0 else 3
    return bez(p0, p1, p2, p3, n)


def head_frame(pts, nod=0.0, nod_az=None, rng=None, yaw=0.0):
    pos, tan = pathpt(pts, 1.0)
    pos = pts[-1]
    if nod:
        az = rng.uniform(0, TAU) if nod_az is None else nod_az
        side = np.array([math.cos(az), math.sin(az), 0.0])
        tan = unit(tan * math.cos(nod) + side * math.sin(nod))
    return frame_z(pos, tan, yaw if yaw else (rng.uniform(0, TAU) if rng is not None else 0))


def lance_leaves(g, pts, rng, n, L, W, t0=0.1, t1=0.7, m='leaf_green', elev=0.55, **bk):
    for i in range(n):
        t = t0 + (t1 - t0) * (i + rng.uniform(-0.2, 0.2)) / max(1, n - 1)
        s = 1 - 0.55 * t
        az = i * 2.4 + rng.uniform(-0.3, 0.3)
        kw = dict(a=0.7, b=0.8, bend=-0.35, fold=0.25, nu=6, nv=2, cols=[(0, '#3d6a24'), (1, '#6aa03a')], mid=0.3)
        kw.update(bk)
        p = blade(L * s * rng.uniform(0.85, 1.1), W * s, **{k: rv(v, rng) for k, v in kw.items()})
        leaf_on_path(g, m, pts, t, az, elev + rng.uniform(-0.15, 0.15), p)


def feather_leaf(L, W, rng, nb=7, m_thick=0.0012, spread=1.3, bend=-0.25):
    """finely dissected leaf: fan of thin blades -> list of (patch, xf)"""
    out = []
    for i in range(nb):
        f = (i - (nb - 1) / 2) / max(1, (nb - 1) / 2)
        ang = f * spread * 0.5
        M = Rz(-ang)
        p = blade(L * (1 - 0.35 * abs(f)) * rng.uniform(0.85, 1.1), W, nu=3, nv=2, a=0.5, b=0.8, bend=bend + rng.uniform(-0.15, 0.15),
                  cols=[(0, '#45783a'), (1, '#6ea04a')], fold=0.2)
        out.append((p, M))
    return out
