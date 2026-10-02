from water_common import *


# ---------------------------------------------------------------- ferns
def frond(g, m, rng, pts, nrm, npair, Lmax, Wp, prof=None, ang=1.05, sub=None, t0=0.1, t1=0.97, nu=3, serr=0.0, rachis_r=(0.0028, 0.0007),
          cols=None, bendp=(-0.3, -0.1), rach=True):
    n = len(pts)
    if rach:
        t = np.linspace(0, 1, n)
        g.add('fern_rachis', tube(pts, rachis_r[0] + (rachis_r[1] - rachis_r[0]) * t, sides=3, cols=grad(t, [(0, '#6a7a3a'), (1, '#8ab04a')]), lod=False))
    prof = prof or (lambda t: math.sin(PI * min(1, (t - 0.0) * 0.98)) ** 0.7 * 0.9 + 0.1)
    cols = cols or [(0, '#4e8a30'), (0.5, '#6ea83a'), (1, '#8cc04a')]
    for i in range(npair):
        t = t0 + (t1 - t0) * (i + 0.5) / npair
        pos, tan = pathpt(pts, t)
        lat = np.cross(tan, nrm)
        if np.linalg.norm(lat) < 1e-3:
            continue
        lat = unit(lat)
        size = prof(t) * (1 - 0.4 * max(0, t - 0.85) / 0.15 * 0)
        for s in (1, -1):
            ydir = unit(lat * s * math.cos(ang) + tan * math.sin(ang))
            M = orient(pos, ydir, nrm)
            if sub is not None:
                sub(g, M, size, s)
            else:
                g.add(m, blade(Lmax * size * rng.uniform(0.9, 1.1), Wp * (0.5 + 0.5 * size), nu=nu, nv=2, a=0.5, b=0.6, serr=serr, bend=bendp,
                               cols=cols, mid=0.3, fold=0.25, lod=False, wave=0.1, wavef=1.5), M)
    # terminal pinna
    tp = pts[-1]
    tn = pathpt(pts, 1.0)[1]
    g.add(m, blade(Lmax * 0.35, Wp * 0.6, nu=3, nv=2, a=0.5, b=0.8, cols=cols, lod=False, bend=(-0.3, -0.1)), orient(tp, tn, nrm))


def fern_lady(v, rng):
    g = Geo()
    nf = {'a': 8, 'b': 7, 'c': 9}[v]
    a0 = rng.uniform(0, TAU)
    for i in range(nf):
        az = a0 + TAU * i / nf + rng.normal(0, 0.25)
        d = np.array([math.cos(az), math.sin(az), 0.0]); Z = np.array([0, 0, 1.0])
        L = rng.uniform(0.55, 0.8)
        p0 = d * 0.012
        p3 = d * L * 0.6 + Z * L * rng.uniform(0.6, 0.85)
        pts = bez(p0, p0 + d * 0.03 + Z * L * 0.6, p3 - Z * L * 0.35 - d * L * 0.1, p3, 10) + 0
        pts[:, 2] -= 0
        pl = 15 if v != 'b' else 13
        frond(g, 'fern_frond', rng, pts, Z, pl, 0.17, 0.045, t0=0.25, nu=3, prof=lambda t: (math.sin(PI * (t - 0.12) / 0.92) ** 0.6 * 0.95 if t > 0.12 else 0.2) + 0.05, ang=1.15,
              cols=[(0, '#4a8a30'), (0.4, '#68a638'), (1, '#8ac048')])
        # stipe darker part below pinnae handled by rachis
    return g


def bracken_sub(rng):
    def sub(g, M, size, s):
        pos = M[:3, 3]; yd = M[:3, 1]; nrm = M[:3, 2]
        Ls = 0.5 * size + 0.03
        p1 = pos + yd * Ls * 0.35 + nrm * 0.0
        pts = bez(pos, pos + yd * Ls * 0.4, pos + yd * Ls * 0.7 + nrm * 0.01, pos + yd * Ls + nrm * (-0.02), 4)
        frond(g, 'fern_frond', rng, pts, nrm, 6, 0.095 * (0.5 + size), 0.028, t0=0.08, t1=0.95, nu=3, serr=0.0,
              prof=lambda t: math.sin(PI * min(1, t * 0.96)) ** 0.6 * 0.9 + 0.1, ang=1.1, rachis_r=(0.0013, 0.0004),
              cols=[(0, '#4a8a2c'), (0.5, '#66a436'), (1, '#86bc46')])
    return sub


def fern_bracken(v, rng):
    g = Geo()
    nf = {'a': 2, 'b': 2, 'c': 2}[v]
    a0 = rng.uniform(0, TAU)
    for i in range(nf):
        az = a0 + TAU * i / nf + rng.normal(0, 0.4)
        d = np.array([math.cos(az), math.sin(az), 0.0]); Z = np.array([0, 0, 1.0])
        h = rng.uniform(0.55, 0.75) * (0.8 if v == 'c' and i else 1)
        ext = rng.uniform(0.45, 0.6)
        pts = bez(d * 0.01, d * 0.01 + Z * h * 0.7, d * ext * 0.35 + Z * h * 1.05, d * ext + Z * h * 0.78, 12)
        frond(g, 'fern_frond', rng, pts, Z, 8, 0.0, 0.0, t0=0.52, t1=0.96, sub=bracken_sub(rng), rachis_r=(0.0042, 0.0012), ang=1.2,
              prof=lambda t: (math.sin(PI * (t - 0.45) / 0.6) ** 0.7 * 0.95 + 0.1) if t > 0.45 else 0.1)
    return g


# ---------------------------------------------------------------- horsetail
def horsetail(v, rng):
    g = Geo()
    n = {'a': 10, 'b': 8, 'c': 12}[v]
    for i in range(n):
        ang = rng.uniform(0, TAU); rr = rng.uniform(0, 0.08)
        base = np.array([rr * math.cos(ang), rr * math.sin(ang), 0])
        h = rng.uniform(0.22, 0.5)
        pts = stem_path(h, rng, lean=rng.uniform(0.03, 0.12), sway=0.02, n=7) + base
        t = np.linspace(0, 1, len(pts))
        g.add('horsetail_stem', tube(pts, 0.0028 - 0.0012 * t, sides=4, cols=grad(t, [(0, '#7aa050'), (1, '#a8c878')]), lod=False))
        nn = 5
        for k in range(nn):
            tt = 0.12 + 0.8 * k / nn
            pos, tan = pathpt(pts, tt)
            r = 0.0032 - 0.0012 * tt
            xf = frame_z(pos, tan, 0)
            g.add('horsetail_node', revolve(lambda u: (r * (1.0 + 0.25 * (1 - u)), 0.012 * u - 0.002), 1, 6, lobe=lambda u, th: 1 + 0.25 * np.abs(np.cos(th * 3)) * u,
                                           lod=False), xf)
            ln = h * 0.25 * (1 - 0.6 * tt) * rng.uniform(0.7, 1.2)
            if tt > 0.85:
                continue
            for q in range(6):
                az = q * TAU / 6 + k * 0.4
                lat = np.cos(az) * xf[:3, 0] + np.sin(az) * xf[:3, 1]
                yd = unit(lat * 0.9 + tan * 0.45)
                p = blade(ln, 0.0022, nu=2, nv=2, widthfn=lambda u: 1 - 0.7 * u, bend=(-0.5, 0.0), cols=[(0, '#7aa050'), (1, '#98c068')], lod=False)
                g.add('horsetail_stem', p, orient(pos + lat * r, yd, tan))
        if v == 'c' and i % 4 == 0:
            top = pts[-1]
            g.add('horsetail_cone', ellipsoid(0.0055, 0.0055, 0.014, nu=4, nseg=8, cols=lambda u, th: grad(u, [(0, '#6a4a30'), (1, '#9a7a58')]), lod=False), T(top[0], top[1], top[2] + 0.008))
    return g


# ---------------------------------------------------------------- sedge / grass
def tuft(g, rng, n, Lr, W, rad=0.04, elev=(1.0, 1.45), bend=(-1.4, -0.5), m='w_grass', cols=None, nu=6, dry=0.0, fold=0.35):
    a0 = rng.uniform(0, TAU)
    for i in range(n):
        az = a0 + i * 2.39996 + rng.normal(0, 0.15)
        rr = rng.uniform(0, rad)
        L = rng.uniform(Lr[0], Lr[1])
        mat_ = m
        cc = cols
        if dry and rng.rand() < dry:
            cc = [(0, '#8a8a48'), (0.5, '#b0a45a'), (1, '#c8b870')]
        p = grass_blade(L, W * rng.uniform(0.8, 1.2), rng, bend=bend, cols=cc, nu=nu, fold=fold)
        blade_at(g, m, p, (rr * math.cos(az), rr * math.sin(az), 0), az + rng.normal(0, 0.1), rng.uniform(*elev))


def sedge(v, rng):
    g = Geo()
    if v == 'a':
        tuft(g, rng, 34, (0.3, 0.55), 0.011, rad=0.05, bend=(-1.7, -0.8), cols=[(0, '#2f5e20'), (0.5, '#4a8a2c'), (1, '#7aa440')], nu=7)
    elif v == 'b':
        tuft(g, rng, 42, (0.25, 0.5), 0.009, rad=0.06, elev=(0.8, 1.3), bend=(-1.9, -0.9), cols=[(0, '#34642a'), (0.5, '#558e30'), (1, '#88a84a')], nu=7)
    elif v == 'c':
        tuft(g, rng, 30, (0.35, 0.65), 0.013, rad=0.05, elev=(1.1, 1.5), bend=(-1.3, -0.6), cols=[(0, '#3a6a28'), (0.5, '#5a9436'), (1, '#9ab44a')], nu=7, dry=0.12)
    else:
        tuft(g, rng, 38, (0.3, 0.6), 0.01, rad=0.06, bend=(-1.6, -0.7), cols=[(0, '#2f5e22'), (0.5, '#4c8a2e'), (1, '#6e9e3c')], nu=7)
    # flowering stems with sedge spikelets
    for k in range(3 if v != 'b' else 5):
        h = rng.uniform(0.45, 0.75)
        pts = stem_path(h, rng, lean=0.2, sway=0.03, n=7)
        t = np.linspace(0, 1, len(pts))
        g.add('w_stem', tube(pts, 0.0014 - 0.0006 * t, sides=3, cols=grad(t, [(0, '#5a8a38'), (1, '#88a848')]), lod=False))
        xf = frame_z(pts[-1], pathpt(pts, 1.0)[1], rng.uniform(0, TAU))
        for q in range(4):
            az = q * 1.6
            lat = np.array([math.cos(az), math.sin(az), 0])
            M = orient(np.array([0, 0, -0.01]) + lat * 0.002, unit(lat * 0.6 + np.array([0, 0, 1.0])), np.array([0, 0, 1.0]))
            g.add('w_seed', ellipsoid(0.0035, 0.0035, 0.014, nu=3, nseg=5, cols=lambda u, th: grad(u, [(0, '#6a5a2c'), (1, '#a08a48')]), lod=False), xf @ M @ T(0, 0.004, 0.01))
    return g


def grass_tuft(v, rng):
    g = Geo()
    spec = {'a': (55, (0.18, 0.4), 0.0055, 0.05, 0.05), 'b': (70, (0.12, 0.3), 0.0045, 0.06, 0.15), 'c': (45, (0.25, 0.5), 0.007, 0.05, 0.0),
            'd': (60, (0.15, 0.45), 0.005, 0.07, 0.2)}[v]
    cols = {'a': [(0, '#3a6a24'), (0.45, '#5f9a35'), (1, '#9ab84e')], 'b': [(0, '#4a7a2a'), (0.5, '#72a83c'), (1, '#a8c058')],
            'c': [(0, '#34622a'), (0.5, '#58923a'), (1, '#88ac4a')], 'd': [(0, '#3e6a26'), (0.5, '#669e38'), (1, '#b4b860')]}[v]
    tuft(g, rng, spec[0], spec[1], spec[2], rad=spec[3], elev=(0.9, 1.5), bend=(-1.3, -0.3), cols=cols, nu=5, dry=spec[4], fold=0.3)
    return g


def grass_seed(v, rng):
    g = Geo()
    tuft(g, rng, 26, (0.3, 0.6), 0.008, rad=0.05, bend=(-1.5, -0.6), cols=[(0, '#3a6a24'), (0.45, '#5f9a35'), (1, '#98b44a')], nu=6)
    ns = {'a': 6, 'b': 8, 'c': 5}[v]
    for k in range(ns):
        h = rng.uniform(0.7, 1.1) * (1 if v != 'c' else 0.8)
        ang = rng.uniform(0, TAU); rr = rng.uniform(0, 0.05)
        pts = stem_path(h, rng, lean=rng.uniform(0.1, 0.22), sway=0.03, n=8, dirang=ang) + np.array([rr * math.cos(ang), rr * math.sin(ang), 0])
        t = np.linspace(0, 1, len(pts))
        g.add('w_stem', tube(pts, 0.0017 - 0.0009 * t, sides=4, cols=grad(t, [(0, '#5a8a38'), (0.7, '#9ab058'), (1, '#b8a860')]), lod=False))
        # one or two stem leaves
        for q in range(2):
            p = grass_blade(rng.uniform(0.15, 0.3), 0.007, rng, bend=(-1.0, -0.4), nu=5)
            leaf_on_path(g, 'w_grass', pts, 0.2 + 0.2 * q, k + q * 3, 0.7, p)
        top = pts[-1]; tan = pathpt(pts, 1.0)[1]
        xf = frame_z(top, tan, rng.uniform(0, TAU))
        if v == 'b':  # dense spike (timothy type)
            ax = np.array([[0, 0, 0], [0, 0, 0.05], [0.004, 0, 0.1]])
            g.add('w_seed', tube(ax, [0.0055, 0.0055, 0.0015], sides=6, cols=grad(np.linspace(0, 1, 3), [(0, '#8aa048'), (1, '#c8b868')]), lod=False), xf)
            for q in range(14):
                az = q * 2.4; tt = q / 14
                lat = np.array([math.cos(az), math.sin(az), 0])
                M = orient(np.array([0, 0, 0.004 + 0.092 * tt]), unit(lat * 0.35 + np.array([0, 0, 1.0])), np.array([0, 0, 1.0]))
                g.add('w_seed', blade(0.016, 0.003, nu=2, nv=2, widthfn=lambda u: 1 - u ** 2, lod=False, cols=[(0, '#9a8a48'), (1, '#d8c880')]), xf @ M @ T(lat[0] * 0.004, lat[1] * 0.004, 0))
        else:  # open panicle
            ax = np.array([[0, 0, 0], [0, 0, 0.05], [0.004, 0, 0.11]])
            nb = 7 if v == 'a' else 9
            for q in range(nb):
                tt = 0.12 + 0.8 * q / nb
                az = q * 2.4
                lat = np.array([math.cos(az), math.sin(az), 0])
                p0 = np.array([0, 0, 0.11 * tt])
                bl = 0.055 * (1 - 0.5 * tt)
                br = bez(p0, p0 + lat * bl * 0.3 + np.array([0, 0, bl * 0.4]), p0 + lat * bl * 0.8 + np.array([0, 0, bl * 0.55]), p0 + lat * bl + np.array([0, 0, bl * 0.35]), 4)
                g.add('w_seed', tube(br, np.linspace(0.0007, 0.0003, 4), sides=3, lod=False, cols=[lin('#b0a060')] * 4), xf)
                for s_ in range(3):
                    f = 0.55 + 0.22 * s_
                    pos, tn = pathpt(br, f)
                    M = orient(pos, unit(tn + np.array([0, 0, -0.3])), np.array([0, 0, 1.0]))
                    g.add('w_seed', ellipsoid(0.0022, 0.0012, 0.0065, nu=2, nseg=5, cols=lambda u, th: grad(u, [(0, '#7a8a48'), (1, '#c8b070')]), lod=False), xf @ M @ T(0, 0, 0.003) @ Rx(PI / 2 * 0.0))
            g.add('w_stem', tube(ax, [0.0012, 0.001, 0.0005], sides=3, lod=False), xf)
    return g


# ---------------------------------------------------------------- mushrooms
def mush(g, xf, rng, sh, sr, R, H, cap_m, cap_cols, stem_m='mush_white', stem_cols=None, under_m='mush_white', under_cols=None, bulb=0.0,
         ring=None, warts=0, wart_m='mush_white', lean=0.0, sr_top=None, nseg=32, stripes=False, scales=0.0, sides=14):
    sr_top = sr_top or sr * 0.75
    n = 7
    t = np.linspace(0, 1, n)
    pts = np.stack([lean * sh * t ** 2, np.zeros(n), sh * t], 1)
    rad = sr_top + (sr - sr_top) * (1 - t) ** 1.5 + bulb * np.exp(-(t / 0.14) ** 2)
    rad[0] = rad[0]
    sc = stem_cols or [(0, '#d8d0b8'), (1, '#f2eee2')]
    g.add(stem_m, tube(pts, rad, sides=sides, cols=grad(t, sc), cap=False, lod=False), xf)
    tan = unit(pts[-1] - pts[-2])
    cx = xf @ frame_z(pts[-1] - tan * 0.002, tan, 0)
    # cap
    def prof(u):
        ph = u * PI / 2
        return R * np.cos(ph) ** 0.85, H * np.sin(ph) ** 0.8 - 0.06 * H * (1 - u) ** 5
    def lobe(u, th):
        return 1 + 0.03 * np.sin(th * 5 + 1.3) * (1 - u) + 0.02 * np.sin(th * 3 + 0.4)
    g.add(cap_m, revolve(prof, 9, nseg, lobe=lobe, cols=cap_cols, lod=False), cx)
    # underside with gill stripes
    def uprof(u):
        return sr_top + (R * 0.985 - sr_top) * u, H * 0.25 * (1 - u) ** 1.4 - 0.05 * H * u ** 3
    uc = under_cols or (lambda u, th: grad(u, [(0, '#e8e0c8'), (1, '#f4f0e0')]) * (0.93 + 0.07 * np.cos(th * nseg / 2 * 1.0))[..., None])
    g.add(under_m, revolve(uprof, 3, nseg, cols=uc, lod=False), cx)
    if ring:
        rz, rw = ring
        pp, tn = pathpt(pts, rz)
        rr = float(np.interp(rz, t, rad))
        rx = xf @ frame_z(pp, tn, 0)
        g.add('mush_white', revolve(lambda u: (rr + rw * u, -rw * 0.95 * u ** 1.1 + 0.004), 2, 16, lobe=lambda u, th: 1 + 0.12 * np.sin(th * 9) * u,
                                   cols=lambda u, th: grad(u, [(0, '#f4f0e4'), (1, '#dcd6c4')]), lod=False), rx)
    for k in range(warts):
        e = rng.uniform(0.18, 1.3)
        th = rng.uniform(0, TAU)
        x = R * math.cos(e) ** 0.85 * math.cos(th); y = R * math.cos(e) ** 0.85 * math.sin(th); z = H * math.sin(e) ** 0.8
        nrm = unit(np.array([x / R ** 2, y / R ** 2, z / H ** 2 * 0.8]))
        w = rng.uniform(0.0045, 0.0085) * (R / 0.07) * (1 - 0.3 * e / 1.3)
        cone = revolve(lambda u, w=w: (w * (1 - u ** 1.2) + 0.0002, w * 0.45 * u), 2, 6, lobe=lambda u, th: 1 + 0.15 * np.sin(th * 3), lod=False,
                       cols=lambda u, th: grad(u, [(0, '#f8f4ea'), (1, '#e6dfcc')]))
        g.add(wart_m, cone, cx @ frame_z(np.array([x, y, z - w * 0.12]), nrm, 0))
    return cap_m


def fly_agaric(v, rng):
    g = Geo()
    red = lambda u, th: grad(u, [(0, '#b81a10'), (0.5, '#d42a1a'), (1, '#dc3820')]) * (0.96 + 0.04 * np.sin(th * 11 + u * 7))[..., None]
    red_young = lambda u, th: grad(u, [(0, '#c02214'), (1, '#d83020')])
    under = lambda u, th: grad(u, [(0, '#e8e0c4'), (1, '#f6f0dc')]) * (0.88 + 0.12 * np.cos(th * 14))[..., None]
    if v == 'a':
        mush(g, np.eye(4), rng, 0.11, 0.013, 0.068, 0.05, 'mush_red', red, bulb=0.012, ring=(0.68, 0.018), warts=34, under_cols=under, lean=0.1, stripes=True)
    elif v == 'b':
        mush(g, np.eye(4), rng, 0.085, 0.012, 0.042, 0.042, 'mush_red', red_young, bulb=0.014, ring=(0.62, 0.012), warts=26, under_cols=under)
    elif v == 'c':
        mush(g, T(0, 0, 0), rng, 0.13, 0.014, 0.078, 0.052, 'mush_red', red, bulb=0.013, ring=(0.7, 0.02), warts=38, under_cols=under, lean=0.12)
        mush(g, T(0.14, 0.05, 0) @ Rz(1.0), rng, 0.075, 0.011, 0.05, 0.03, 'mush_red', red, bulb=0.01, ring=(0.66, 0.012), warts=22, under_cols=under, lean=-0.15)
        mush(g, T(-0.08, 0.09, 0), rng, 0.05, 0.009, 0.03, 0.03, 'mush_red', red_young, bulb=0.009, warts=14, under_cols=under)
    else:
        mush(g, np.eye(4), rng, 0.15, 0.015, 0.085, 0.045, 'mush_red', red, bulb=0.014, ring=(0.72, 0.022), warts=40, under_cols=under, lean=-0.08)
    return g


def porcini(v, rng):
    g = Geo()
    cap = lambda u, th: grad(u, [(0, '#b07a42'), (0.4, '#8a5a2c'), (1, '#6a4020')]) * (0.94 + 0.06 * np.sin(th * 7 + u * 3))[..., None]
    pore = lambda u, th: grad(u, [(0, '#c8b870'), (1, '#e0d898')])
    stem = [(0, '#d8c498'), (0.5, '#e6d6b0'), (1, '#f0e4c8')]
    if v == 'a':
        mush(g, np.eye(4), rng, 0.09, 0.02, 0.078, 0.042, 'mush_brown', cap, stem_m='mush_stem_cream', stem_cols=stem, under_m='mush_pore', under_cols=pore, bulb=0.022, sr_top=0.017, lean=0.06)
    elif v == 'b':
        mush(g, np.eye(4), rng, 0.11, 0.022, 0.09, 0.05, 'mush_brown', cap, stem_m='mush_stem_cream', stem_cols=stem, under_m='mush_pore', under_cols=pore, bulb=0.022, sr_top=0.018, lean=-0.1)
        mush(g, T(0.1, -0.03, 0) @ Rz(2.0), rng, 0.06, 0.014, 0.05, 0.03, 'mush_brown', cap, stem_m='mush_stem_cream', stem_cols=stem, under_m='mush_pore', under_cols=pore, bulb=0.013, sr_top=0.011, lean=0.2)
    else:
        mush(g, np.eye(4), rng, 0.065, 0.017, 0.05, 0.048, 'mush_brown', cap, stem_m='mush_stem_cream', stem_cols=stem, under_m='mush_pore', under_cols=pore, bulb=0.018, sr_top=0.014)
        mush(g, T(-0.07, 0.04, 0), rng, 0.04, 0.01, 0.03, 0.03, 'mush_brown', cap, stem_m='mush_stem_cream', stem_cols=stem, under_m='mush_pore', under_cols=pore, bulb=0.01, sr_top=0.008, lean=0.1)
        mush(g, T(0.05, 0.06, 0), rng, 0.05, 0.012, 0.038, 0.03, 'mush_brown', cap, stem_m='mush_stem_cream', stem_cols=stem, under_m='mush_pore', under_cols=pore, bulb=0.012, sr_top=0.01, lean=-0.2)
    return g


def chanterelle_one(g, xf, rng, h, R, lean=0.0):
    nz = make_noise(rng.randint(999))
    ph0 = rng.uniform(0, TAU)
    def prof(u):
        # stem base -> funnel -> rim -> inner cup
        r = np.where(u < 0.5, 0.006 + 0.004 * (u / 0.5) ** 2 + (R - 0.01) * (np.maximum(u - 0.3, 0) / 0.2) ** 2 * 0.0, 0)
        a = np.minimum(u / 0.55, 1.0)
        rr = 0.007 + 0.004 * a ** 1.5 + (R - 0.011) * np.maximum(0, (u - 0.25) / 0.3) ** 1.7 * (u < 0.55) + (R) * (u >= 0.55) * 0
        rr = np.where(u < 0.55, rr, R - (R - 0.014) * ((u - 0.55) / 0.45) ** 1.6 * 0.85)
        z = np.where(u < 0.55, h * 0.85 * (u / 0.55) ** 0.9, h * 0.85 + h * 0.15 * ((u - 0.55) / 0.45) ** 0.8 - h * 0.1 * ((u - 0.55) / 0.45))
        return rr, z
    def lobe(u, th):
        return 1 + (0.12 * np.sin(th * 3 + ph0) + 0.08 * np.sin(th * 5 + 1.0 + ph0 * 2) + 0.05 * np.sin(th * 7 + 2)) * np.clip((u - 0.3) * 3, 0, 1)
    def cols(u, th):
        c = grad(u, [(0, '#f0c050'), (0.4, '#ec9f18'), (0.55, '#f4ac20'), (1, '#c8780e')])
        return c * (0.9 + 0.1 * np.cos(th * 28) * np.clip(u * 2, 0, 1))[..., None]
    g.add('mush_chant', revolve(prof, 12, 32, lobe=lobe, cols=cols, lod=False), xf @ Rx(lean) @ Rz(ph0))


def chanterelle(v, rng):
    g = Geo()
    cfg = {'a': [(0.0, 0.0, 0.06, 0.038, 0.0), (0.06, 0.03, 0.045, 0.03, 0.2), (-0.04, 0.05, 0.05, 0.03, -0.15)],
           'b': [(0.0, 0.0, 0.075, 0.045, 0.05), (0.07, -0.02, 0.05, 0.032, -0.25), (-0.05, -0.04, 0.04, 0.026, 0.3), (0.03, 0.06, 0.035, 0.022, 0.1)],
           'c': [(0.0, 0.0, 0.055, 0.034, 0.0), (0.045, 0.025, 0.04, 0.024, 0.25)]}[v]
    for (x, y, h, R, lean) in cfg:
        chanterelle_one(g, T(x, y, 0) @ Rz(rng.uniform(0, TAU)), rng, h, R, lean)
    return g


def honey(v, rng):
    g = Geo()
    n = {'a': 8, 'b': 10, 'c': 12}[v]
    for i in range(n):
        az = rng.uniform(0, TAU)
        d = np.array([math.cos(az), math.sin(az), 0.0])
        s = rng.uniform(0.55, 1.0)
        R = 0.03 * s; sh = rng.uniform(0.05, 0.11) * (0.7 + 0.3 * s)
        base = d * rng.uniform(0, 0.035)
        lean = rng.uniform(0.1, 0.3)
        xf = T(base[0], base[1], 0) @ Rz(az) @ Ry(0)  # stem leans along local +x
        cap = lambda u, th: grad(u, [(0, '#a07a42'), (0.5, '#c29a58'), (1, '#8a6434')]) * (0.93 + 0.07 * np.sin(th * 13))[..., None]
        under = lambda u, th: grad(u, [(0, '#e8dcc0'), (1, '#d8c8a0')]) * (0.9 + 0.1 * np.cos(th * 12))[..., None]
        mush(g, xf, rng, sh, 0.0045 * (0.7 + s * 0.4), R, R * 0.55, 'mush_honey', cap, stem_m='mush_honey_stem', stem_cols=[(0, '#7a6440'), (0.5, '#b89a68'), (1, '#d0b888')],
             under_m='mush_white', under_cols=under, ring=(0.75, 0.006) if R > 0.022 else None, lean=lean, sr_top=0.0035, nseg=16, sides=7)
    return g


DEFS = [
    dict(sp='fern_lady', fn=fern_lady, variants=['a', 'b', 'c'], ko='레이디펀(개고사리류)', weight=0.7, habitat='shade', sway=0.3),
    dict(sp='fern_bracken', fn=fern_bracken, variants=['a', 'b', 'c'], ko='고사리', weight=0.6, habitat='forest_edge', sway=0.3),
    dict(sp='horsetail', fn=horsetail, variants=['a', 'b', 'c'], ko='쇠뜨기', weight=0.5, habitat='wet', sway=0.4),
    dict(sp='sedge', fn=sedge, variants=['a', 'b', 'c', 'd'], ko='사초', weight=0.8, habitat='water_edge', sway=0.5),
    dict(sp='grass_tuft', fn=grass_tuft, variants=['a', 'b', 'c', 'd'], ko='풀(볏과 풀)', weight=1.0, habitat='meadow', sway=0.55),
    dict(sp='grass_seed', fn=grass_seed, variants=['a', 'b', 'c'], ko='키 큰 풀(이삭)', weight=0.7, habitat='meadow', sway=0.6),
    dict(sp='mushroom_fly_agaric', fn=fly_agaric, variants=['a', 'b', 'c', 'd'], ko='광대버섯', weight=0.25, habitat='forest_edge', sway=0.0),
    dict(sp='mushroom_porcini', fn=porcini, variants=['a', 'b', 'c'], ko='그물버섯(포르치니)', weight=0.25, habitat='forest_edge', sway=0.0),
    dict(sp='mushroom_chanterelle', fn=chanterelle, variants=['a', 'b', 'c'], ko='살구버섯(꾀꼬리버섯)', weight=0.25, habitat='forest_edge', sway=0.0),
    dict(sp='mushroom_honey', fn=honey, variants=['a', 'b', 'c'], ko='뽕나무버섯', weight=0.25, habitat='shade', sway=0.0),
]
