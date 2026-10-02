from meadow_common import *


def _m():
    mat('petal_foxglove', '#f2a2d4', rough=0.55, sss=0.25)
    mat('petal_foxglove_white', '#fbf5f0', rough=0.55, sss=0.25)
    mat('petal_tulip_red', '#f23a26', rough=0.38, sss=0.2)
    mat('petal_tulip_yellow', '#fbd012', rough=0.38, sss=0.2)
    mat('leaf_tulip', '#7fb07a', rough=0.42)
    mat('petal_sunflower', '#ffc812', rough=0.5, sss=0.2)
    mat('disc_sunflower', '#6a4a20', rough=0.85)
    mat('petal_bluebell', '#8474f0', rough=0.5, sss=0.25)
    mat('leaf_bluebell', '#4f9a3a', rough=0.35)
    mat('petal_lupine', '#b48ae8', rough=0.55, sss=0.2)
    mat('petal_lupine_pink', '#f27ab4', rough=0.55, sss=0.2)
    mat('petal_lupine_blue', '#6a84f2', rough=0.55, sss=0.2)
    mat('leaf_lupine', '#5a9a40', rough=0.5)
    mat('stem_hairy', '#86a84a', rough=0.75)
    mat('leaf_hairy', '#4c8230', rough=0.75)


def mix(a, b, k):
    k = np.asarray(k)[..., None]
    return a * (1 - k) + b * k


def petiole_leaf(g, m, pts, t, az, elev, patch_fn, petlen, rng, droop=0.5, r=0.0025, leaf_tilt=0.0):
    """petiole tube from stem then leaf patch at its end (leaf lies roughly horizontal)."""
    pos, tan = pathpt(pts, t)
    e1, e2 = stem_frame(tan)
    radial = math.cos(az) * e1 + math.sin(az) * e2
    d0 = unit(radial * math.cos(elev) + tan * math.sin(elev))
    p1 = pos + d0 * petlen * 0.45
    p3 = pos + radial * petlen * 0.8 + np.array([0, 0, petlen * (math.sin(elev) * 0.6 - droop * 0.4)])
    p2 = p3 - unit(radial + np.array([0, 0, 0.2])) * petlen * 0.2
    pp = bez(pos, p1, p2, p3, 4 if LOD == 0 else 3)
    g.add('stem_hairy', tube(pp, np.linspace(r, r * 0.6, len(pp)), sides=3, cols=lin('#6d9038'), cap=False))
    yd = unit(np.array([radial[0], radial[1], 0.0]) + np.array([0, 0, -droop * 0.25 + 0.15]))
    g.add(m, patch_fn, orient(p3, yd, np.array([0, 0, 1.0])) @ Rx(leaf_tilt))


# ================================================================= FOXGLOVE
def fox_bell(R, Lb, white, rng, nu=6, nseg=10):
    def prof(u):
        r = 0.0028 + R * (np.sin(PI / 2 * u) ** 1.6) * (1 + 0.14 * np.sin(PI * u)) * 0.9 + R * 0.14 * u ** 9
        return r, Lb * u

    def lobe(u, th):
        return 1 + 0.07 * u ** 7 * np.cos(5 * th) - 0.05 * u ** 8

    ph = rng.uniform(0, 6)

    def cols(u, th):
        if white:
            base = grad(u, [(0, '#b7c98c'), (0.25, '#f2eee0'), (1, '#fffaf6')])
            dark = lin('#6a2a48')
        else:
            base = grad(u, [(0, '#9a8a50'), (0.2, '#c458a0'), (0.75, '#dd74bb'), (1, '#f0a2d4')])
            dark = lin('#5a0e3a')
        sp = np.exp(-((u - 0.8) / 0.14) ** 2) * (0.5 + 0.5 * np.cos(th * 6 + ph)) ** 3
        return mix(base, dark, sp * 0.85)
    return revolve(prof, nu, nseg, lobe=lobe, cols=cols)


def foxglove(v, rng):
    _m()
    g = Geo()
    white = v == 'c'
    pm = 'petal_foxglove_white' if white else 'petal_foxglove'
    h, nb, lean = {'a': (1.30, 16, 0.07), 'b': (1.48, 20, 0.05), 'c': (1.15, 14, 0.09), 'd': (1.38, 18, 0.06)}[v]
    h *= rng.uniform(0.96, 1.04)
    pts = stem_path(h, rng, lean=lean, sway=0.02, n=12)
    gstem(g, pts, 0.0075, 0.0030, sides=6, c0='#5a7a30', c1='#8aa85a', m='stem_hairy')
    rosette(g, 'leaf_hairy', 7, 0.26, 0.095, rng, elev=(0.2, 0.6), a=0.8, b=0.55, nu=12, nv=4, serr=0.12, wave=0.1, wavef=4, fold=0.18,
            bend=(-0.75, -0.35), cols=[(0, '#3c6a26'), (0.6, '#527f34'), (1, '#6a9a44')], mid=0.4, edge=0.1, veinN=7, vein=0.3, baseW=0.12)
    for i in range(4):
        t = 0.1 + 0.11 * i
        s = 1 - 0.6 * t
        p = blade(0.15 * s, 0.05 * s, nu=8, nv=2, a=0.6, b=0.7, serr=0.1, bend=-0.4, fold=0.2, cols=[(0, '#3c6a26'), (1, '#6a9a44')], mid=0.3)
        leaf_on_path(g, 'leaf_hairy', pts, t, i * 2.4, 0.7, p)
    base_az = rng.uniform(0, TAU)
    t0, t1 = 0.40, 0.93
    nb = lc(nb, 1)
    for i in range(nb):
        f = i / max(1, nb - 1)
        t = t0 + (t1 - t0) * f
        s = 1.0 - 0.45 * f
        pos, tan = pathpt(pts, t)
        e1, e2 = stem_frame(tan)
        az = base_az + rng.uniform(-0.9, 0.9)
        radial = math.cos(az) * e1 + math.sin(az) * e2
        axis = unit(radial * 0.95 - np.array([0, 0, 1.0]) * (0.55 - 0.25 * f))
        xf = frame_z(pos + radial * 0.0035, axis, rng.uniform(0, TAU))
        g.add(pm, fox_bell(0.0235 * s, 0.058 * s, white, rng, nu=7, nseg=12), xf)
        petal_ring(g, 'sepal_green', 5, 0.012 * s, 0.006 * s, rng, r0=0.002, z0=0.001, elev=0.5, xf=xf, a=0.6, b=0.6, nu=2, nv=2, bend=0.2,
                   cols=[(0, '#5c8a30'), (1, '#8aac50')])
    # buds at tip
    for i in range(lc(6, 0.5)):
        f = 1 + i * 0.012
        t = 0.94 + i * 0.012
        pos, tan = pathpt(pts, min(t, 1.0))
        e1, e2 = stem_frame(tan)
        az = base_az + rng.uniform(-1.2, 1.2)
        radial = math.cos(az) * e1 + math.sin(az) * e2
        axis = unit(radial * 0.6 + tan * 0.7)
        s = 0.5 - 0.06 * i
        g.add('sepal_green', ellipsoid(0.005 * s * 2, 0.005 * s * 2, 0.011 * s * 2, nu=3, nseg=6,
                                       cols=lambda u, th: grad(u, [(0, '#6a9a3a'), (0.6, '#8ab04e'), (1, '#c8a0b0')])), frame_z(pos + radial * 0.003, axis) @ T(0, 0, 0.006))
    g.add('sepal_green', ellipsoid(0.004, 0.004, 0.010, nu=3, nseg=6, cols=lambda u, th: grad(u, [(0, '#6a9a3a'), (1, '#b8b090')])), frame_z(pts[-1], pathpt(pts, 1.0)[1]) @ T(0, 0, 0.005))
    return g


# ================================================================= TULIP
def tulip(v, rng):
    _m()
    g = Geo()
    red = v in 'ab'
    pm = 'petal_tulip_red' if red else 'petal_tulip_yellow'
    h, elev, bend, bend2, nod = {'a': (0.42, 0.55, 1.0, 0.0, 0.1), 'b': (0.48, 0.8, 0.45, 0.35, 0.2),
                                 'c': (0.38, 0.5, 1.15, 0.0, 0.05), 'd': (0.45, 0.4, 1.0, -0.75, 0.3)}[v]
    h *= rng.uniform(0.96, 1.04)
    pts = stem_path(h, rng, lean=0.12, sway=0.03, n=8)
    gstem(g, pts, 0.0042, 0.0034, sides=6, c0='#5f8a4a', c1='#7fae68', m='stem_grey')
    xf = head_frame(pts, nod=nod, rng=rng)
    flame = v == 'd'

    def cfn_for(ring):
        def cfn(U, V, xn):
            if red:
                c = grad(U, [(0, '#9a2a18'), (0.12, '#d42418'), (0.6, '#f03c28'), (1, '#f85a3a')])
            else:
                c = grad(U, [(0, '#c8b840'), (0.12, '#f0c818'), (0.6, '#fbd414'), (1, '#ffe03a')])
            if flame:
                k = np.exp(-(xn / 0.5) ** 2) * np.clip((U - 0.15) * 1.6, 0, 1) * (0.5 + 0.5 * np.cos(xn * 9 + ring))
                c = mix(c, lin('#e8401a'), k * 0.85)
            return c * (1 - 0.12 * np.abs(xn) ** 3)[..., None]
        return cfn
    for ring in range(2):
        for i in range(3):
            ang = TAU * (i / 3 + ring / 6) + rng.uniform(-0.1, 0.1)
            el = elev + (0.1 if ring else 0) + rng.normal(0, 0.04)
            radial = np.array([math.cos(ang), math.sin(ang), 0.0]); Z = np.array([0, 0, 1.0])
            yd = math.cos(el) * radial + math.sin(el) * Z
            nr = -math.sin(el) * radial + math.cos(el) * Z
            M = orient(radial * 0.004, yd, nr)
            W = 0.034 * (1.0 if ring else 0.9)
            p = blade(0.056 * rng.uniform(0.95, 1.05) * (0.97 if ring else 1.0), W, nu=8, nv=6, a=0.75, b=0.42, bend=bend, bend2=bend2,
                      cup=0.7, wave=0.03 if flame else 0.0, wavef=2, cfn=cfn_for(i + ring * 3), mid=0.04, edge=0.0, notch=0.0, baseW=0.05)
            g.add(pm, p, xf @ M)
    # pistil + stamens
    g.add('sepal_green', ellipsoid(0.0038, 0.0038, 0.0095, nu=3, nseg=6, cols=lambda u, th: grad(u, [(0, '#8aa84a'), (1, '#c8d070')])), xf @ T(0, 0, 0.0085))
    g.add('stamen_yellow', lobed_disc(0.0055, lobes=3, rings=1, segs=6, depth=0.3, cols=lambda u, th: np.ones(u.shape + (3,)) * lin('#e8d860')), xf @ T(0, 0, 0.019))
    for i in range(6):
        ang = TAU * i / 6 + 0.3
        rr = 0.007
        p0 = np.array([rr * 0.5 * math.cos(ang), rr * 0.5 * math.sin(ang), 0.0])
        p1 = np.array([rr * math.cos(ang), rr * math.sin(ang), 0.022])
        pp = np.linspace(p0, p1, 3)
        pp = np.array([xfv(xf, q[None])[0] for q in pp])
        g.add('stamen_yellow', tube(pp, [0.0007, 0.0006, 0.0006], sides=3, cols=lin('#e8e0a0'), cap=False))
        ax = unit(pp[-1] - pp[-2])
        g.add('anther_dark', ellipsoid(0.0012, 0.0012, 0.0042, nu=2, nseg=4), frame_z(pp[-1] + ax * 0.002, ax))
    # leaves (sheathing, folded, arched)
    nl = lc(3, 1.0) + (1 if v in 'bd' else 0)
    for i in range(nl):
        t = 0.03 + 0.12 * i
        s = 1 - 0.3 * i
        p = blade(0.33 * s, 0.062 * s, nu=10, nv=4, a=0.55, b=0.9, fold=0.4, cup=0.0, wave=0.12, wavef=4.5, bend=-0.15, bend2=-0.6, side=0.05,
                  cols=[(0, '#4f7a48'), (0.4, '#6a9a62'), (1, '#86b47c')], mid=0.2, baseW=0.35, edge=0.08)
        leaf_on_path(g, 'leaf_tulip', pts, t, i * 3.1 + rng.uniform(-0.3, 0.3), 1.05 - 0.15 * i, p)
    return g


# ================================================================= SUNFLOWER
def sunflower(v, rng):
    _m()
    g = Geo()
    h, nod, az0 = {'a': (1.05, 0.8, 0), 'b': (1.25, 0.55, 1), 'c': (0.85, 1.0, 2), 'd': (1.15, 0.35, 3)}[v]
    h *= rng.uniform(0.96, 1.04)
    pts = stem_path(h, rng, lean=0.10, sway=0.015, n=10)
    # curved neck at the top
    gstem(g, pts, 0.0115, 0.0075, sides=6, c0='#5a7a30', c1='#7f9a48', m='stem_hairy')
    xf = head_frame(pts, nod=nod, rng=rng)
    # head sits slightly ahead of the stem tip
    xf = xf @ T(0, 0, 0.006)
    sc = 1.0
    petal_ring(g, 'petal_sunflower', lc(17, 1.0), 0.046, 0.0145, rng, r0=0.040, z0=-0.0015, elev=(-0.05, 0.12), elev_j=0.05, xf=xf, a=0.55, b=0.8,
               nu=4, nv=2, bend=(-0.4, 0.05), twist=(-0.4, 0.4), cup=0.35, wave=0.04, wavef=1.5,
               cols=[(0, '#c07808'), (0.25, '#f2a80c'), (1, '#ffcf1a')], mid=-0.08, edge=0.05, jit=0.2, lj=0.12)
    petal_ring(g, 'petal_sunflower', lc(17, 1.0), 0.042, 0.0138, rng, r0=0.038, z0=-0.0035, elev=(0.1, 0.3), elev_j=0.05, xf=xf, a=0.55, b=0.8,
               nu=4, nv=2, bend=(-0.4, 0.05), twist=(-0.4, 0.4), cup=0.35, cols=[(0, '#b87008'), (0.25, '#ee9e0a'), (1, '#fbc414')], mid=-0.08,
               edge=0.05, yaw0=0.18, jit=0.2, lj=0.12)
    ph = rng.uniform(0, 6)

    def cols(u, th):
        r = 1 - u
        base = grad(u, [(0, '#b4741c'), (0.12, '#5a3a14'), (0.5, '#3a2010'), (0.9, '#4a3a14'), (1, '#5e5a1c')])
        pat = np.sin(13 * th + 9 * r + ph) * np.sin(21 * th - 9 * r)
        return base * (1 + 0.45 * pat[..., None] * (u > 0.1)[..., None]) * np.where(u > 0.05, 1, 1)[..., None]

    def lobe(u, th):
        return 1 + 0.012 * np.sin(21 * th - 12 * u) * np.sin(13 * th + 12 * u)
    g.add('disc_sunflower', dome(0.042, 0.011, nu=8, nseg=40, cols=cols, lobe=lobe), xf @ T(0, 0, -0.003))
    g.add('sepal_green', ellipsoid(0.040, 0.040, 0.012, nu=4, nseg=14, cols=lambda u, th: grad(u, [(0, '#3a5a20'), (1, '#5a7a2c')])), xf @ T(0, 0, -0.012))
    for ring, (n, L, r0) in enumerate([(lc(14, 0.6), 0.032, 0.03), (lc(12, 0.6), 0.026, 0.02)]):
        petal_ring(g, 'sepal_green', n, L, 0.015, rng, r0=r0, z0=-0.012 - ring * 0.004, elev=-0.35 - 0.3 * ring, xf=xf, a=0.45, b=1.1, nu=4, nv=2,
                   bend=(-0.3, 0.3), cols=[(0, '#3c6a24'), (1, '#6a9a3a')], mid=0.2, jit=0.3)
    # leaves
    nl = 7
    for i in range(nl):
        t = 0.10 + 0.72 * i / (nl - 1)
        s = 1.0 - 0.6 * t
        p = blade(0.24 * s, 0.2 * s, nu=10, nv=6, a=0.33, b=0.75, serr=0.12, bend=-0.5, fold=0.12, cup=-0.05,
                  cols=[(0, '#3a6a22'), (0.4, '#4c8230'), (1, '#6a9c3c')], mid=0.3, edge=0.1, veinN=6, vein=0.3, baseW=0.1)
        petiole_leaf(g, 'leaf_hairy', pts, t, i * 2.4 + rng.uniform(-0.2, 0.2), 0.9, p, 0.09 * s + 0.03, rng, droop=0.8, r=0.0028)
    return g


# ================================================================= BLUEBELL
def bluebell_bell(s, rng, nu=5, nseg=12):
    Lb = 0.024 * s

    def prof(u):
        r = 0.0035 * s + 0.0030 * s * np.sin(PI * u * 0.85) + 0.0075 * s * u ** 6
        return r, Lb * (u - 0.1 * u ** 6)

    def lobe(u, th):
        return 1 + 0.22 * u ** 4 * np.cos(6 * th)
    cols = lambda u, th: grad(u, [(0, '#b8b0f4'), (0.4, '#7a68e8'), (1, '#6454dc')]) * (1 - 0.08 * (0.5 + 0.5 * np.cos(6 * th))[..., None] * u[..., None])
    return revolve(prof, nu, nseg, lobe=lobe, cols=cols)


def bluebell(v, rng):
    _m()
    g = Geo()
    ns, h, nb = {'a': (2, 0.34, 7), 'b': (3, 0.38, 8), 'c': (4, 0.32, 7), 'd': (3, 0.36, 9)}[v]
    for si in range(ns):
        a0 = TAU * si / ns + rng.uniform(-0.4, 0.4)
        off = np.array([math.cos(a0), math.sin(a0), 0]) * (0.012 if ns > 1 else 0)
        hh = h * rng.uniform(0.85, 1.1)
        d = np.array([math.cos(a0 + rng.uniform(-0.5, 0.5)), math.sin(a0 + rng.uniform(-0.5, 0.5)), 0.0])
        n = 10 if LOD == 0 else 5
        pts = bez(off, off + [0, 0, hh * 0.6], off + d * hh * 0.1 + [0, 0, hh * 0.98], off + d * hh * 0.42 + [0, 0, hh * 0.86], n)
        gstem(g, pts, 0.0026, 0.0014, sides=4, c0='#6a8a3a', c1='#a0a864')
        az0 = math.atan2(d[1], d[0])
        for i in range(nb):
            f = i / max(1, nb - 1)
            t = 0.45 + 0.52 * f
            s = 1.0 - 0.45 * f
            pos, tan = pathpt(pts, t)
            e1, e2 = stem_frame(tan)
            az = az0 + rng.uniform(-0.6, 0.6)
            # pedicel bends outward then down
            radial = unit(d * 0.8 + (math.cos(az) * e1 + math.sin(az) * e2) * 0.4)
            p0 = pos
            p2 = pos + radial * 0.013 * s + np.array([0, 0, -0.002])
            pp = np.array([p0, (p0 + p2) / 2 + [0, 0, 0.003], p2])
            g.add('stem_green', tube(pp, [0.0008, 0.0007, 0.0007], sides=3, cols=lin('#8a9a60'), cap=False))
            axis = unit(radial * 0.25 + np.array([0, 0, -1.0]) * 0.95)
            xf = frame_z(p2, axis, rng.uniform(0, TAU))
            g.add('petal_bluebell', bluebell_bell(s, rng), xf)
        # terminal buds
        for k in range(2):
            tp = pts[-1] + d * 0.004 * k
            g.add('petal_bluebell', ellipsoid(0.0028, 0.0028, 0.008, nu=3, nseg=6, cols=lambda u, th: grad(u, [(0, '#6a9a3a'), (1, '#b8b0f0')])),
                  frame_z(tp, unit(d * 0.7 + [0, 0, 0.3])) @ T(0, 0, 0.004))
    nl = lc(7, 0.8) + ns
    rosette(g, 'leaf_bluebell', nl, 0.27, 0.016, rng, elev=(0.55, 1.15), r0=0.01, a=0.3, b=0.55, nu=10, nv=2, fold=0.55, bend=(-0.9, -0.45), bend2=(-0.8, -0.3),
            cols=[(0, '#2f6a2a'), (0.5, '#4a9a38'), (1, '#6ab04a')], mid=0.3, baseW=0.45, twist=(-0.3, 0.3))
    return g


# ================================================================= LUPINE
def lupine(v, rng):
    _m()
    g = Geo()
    pm, pal, wing, n_fl, h, sp_len = {
        'a': ('petal_lupine', ['#7a45c6', '#a07ae0'], '#a688e6', 78, 0.90, 0.26),
        'b': ('petal_lupine_pink', ['#d0508c', '#f4a0c8'], '#f6b0d2', 70, 0.82, 0.24),
        'c': ('petal_lupine_blue', ['#3a56d0', '#8aa0f4'], '#f4f4fa', 84, 0.95, 0.28),
        'd': ('petal_lupine', ['#8a50d0', '#f0a8d8'], '#f0d0f0', 72, 0.86, 0.25)}[v]
    wm = 'petal_white' if v == 'c' else pm
    h *= rng.uniform(0.96, 1.04)
    pts = stem_path(h, rng, lean=0.05, sway=0.015, n=10)
    gstem(g, pts, 0.0062, 0.0030, sides=5, c0='#5a7a30', c1='#8aa85a', m='stem_hairy')
    # raceme
    t0 = 1 - sp_len / h
    n_fl = lc(n_fl, 0.9)
    ga = 2.39996
    for i in range(n_fl):
        f = i / (n_fl - 1)
        t = t0 + (1 - t0) * f ** 0.92
        s = (1.0 - 0.55 * f ** 1.5) * 1.7
        az = i * ga
        pos, tan = pathpt(pts, t)
        e1, e2 = stem_frame(tan)
        radial = math.cos(az) * e1 + math.sin(az) * e2
        ydir = unit(radial * 0.85 + tan * (0.35 + 0.5 * f))
        M = orient(pos + radial * 0.002, ydir, tan)
        col0 = grad(f, [(0, pal[0]), (1, pal[1])])
        cf = lambda U, V, xn, c0=col0: np.ones(U.shape + (3,)) * c0 * (0.85 + 0.15 * U[..., None])
        # banner (upright, folded back)
        g.add(pm, blade(0.013 * s, 0.013 * s, nu=2, nv=2, a=0.5, b=0.4, cup=0.5, bend=-0.3, cfn=cf, notch=0.05), M @ T(0, 0.004 * s, 0.001) @ Rx(0.75))
        # wings
        wc = grad(f, [(0, wing), (1, wing)])
        cfw = lambda U, V, xn, c0=wc: np.ones(U.shape + (3,)) * c0 * (0.8 + 0.2 * U[..., None])
        g.add(wm, blade(0.012 * s, 0.011 * s, nu=2, nv=2, a=0.6, b=0.5, fold=0.6, cup=0.0, cfn=cfw), M @ Rx(-0.05))
        # keel
        g.add('petal_white' if v == 'c' else pm, ellipsoid(0.0026 * s, 0.0026 * s, 0.0075 * s, nu=2, nseg=4, lod=False), M @ Rx(-PI / 2) @ T(0, 0, 0.0) @ Sc(1) @ T(0, 0, 0.0) if False else M @ T(0, 0.004 * s, -0.0015) @ Rx(-PI / 2))
        g.add('sepal_green', lobed_disc(0.0035 * s, lobes=3, rings=1, segs=6, depth=0.1, cols=lambda u, th: np.ones(u.shape + (3,)) * lin('#7a9a4a')), M @ Rx(PI / 2) @ T(0, 0, -0.001))
    # spike tip
    g.add(pm, ellipsoid(0.004, 0.004, 0.012, nu=3, nseg=6, cols=lambda u, th: grad(u, [(0, '#8aa858'), (1, pal[1])])), frame_z(pts[-1], pathpt(pts, 1)[1]) @ T(0, 0, 0.007))
    # palmate leaves
    nl = 8
    for i in range(nl):
        basal = i < 6
        t = 0.0 if basal else 0.18 + 0.12 * (i - 6)
        az = i * 2.0 + rng.uniform(-0.3, 0.3)
        s = rng.uniform(0.85, 1.15) * (1 if basal else 0.65)
        plen = (0.26 if basal else 0.12) * s
        pos, tan = pathpt(pts, max(t, 0.02))
        e1, e2 = stem_frame(tan)
        radial = math.cos(az) * e1 + math.sin(az) * e2
        ela = 0.9 if basal else 0.6
        p3 = pos + radial * plen * 0.75 + np.array([0, 0, plen * 0.65 if basal else plen * 0.3])
        p1 = pos + np.array([0, 0, plen * 0.5]) if basal else pos + radial * plen * 0.3 + [0, 0, 0.03]
        p2 = p3 - unit(radial + np.array([0, 0, 0.6])) * plen * 0.25
        pp = bez(pos + radial * 0.006, p1, p2, p3, 5 if LOD == 0 else 3)
        g.add('leaf_lupine', tube(pp, np.linspace(0.0028, 0.0016, len(pp)), sides=3, cols=lin('#7a9a4a'), cap=False))
        nlf = 9
        M0 = orient(p3, unit(np.array([radial[0], radial[1], 0.0])), np.array([0, 0, 1.0]))
        for k in range(nlf):
            f = (k - (nlf - 1) / 2) / ((nlf - 1) / 2)
            phi = f * 2.3
            Ll = 0.105 * s * (1 - 0.3 * abs(f)) * rng.uniform(0.9, 1.1)
            lp = blade(Ll, 0.02 * s, nu=5, nv=2, a=0.75, b=0.5, fold=0.3, bend=(-0.45, -0.1), cols=[(0, '#3c6a26'), (1, '#6a9c42')], mid=0.3)
            g.add('leaf_lupine', lp, M0 @ Rz(-phi) @ Rx(0.12) @ T(0, 0.004, 0))
    return g


DEFS = [
    dict(sp='foxglove', fn=foxglove, variants=['a', 'b', 'c', 'd'], ko='디기탈리스(폭스글러브)', weight=0.35, habitat='forest_edge', sway=0.35),
    dict(sp='tulip', fn=tulip, variants=['a', 'b', 'c', 'd'], ko='튤립', weight=0.25, habitat='garden', sway=0.45),
    dict(sp='sunflower', fn=sunflower, variants=['a', 'b', 'c', 'd'], ko='해바라기', weight=0.3, habitat='garden', sway=0.3),
    dict(sp='bluebell', fn=bluebell, variants=['a', 'b', 'c', 'd'], ko='블루벨', weight=0.45, habitat='shade', sway=0.5),
    dict(sp='lupine', fn=lupine, variants=['a', 'b', 'c', 'd'], ko='루피너스', weight=0.35, habitat='meadow', sway=0.35),
]
