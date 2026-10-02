from meadow_common import *

_done = [False]


def ensure():
    if 'petal_cosmos' in MATS:
        return
    mat('petal_cosmos', '#f7a6cb', rough=0.6, sss=0.25)
    mat('petal_cosmos_mag', '#e03a93', rough=0.6, sss=0.2)
    mat('petal_echinacea', '#d95aa6', rough=0.6, sss=0.15)
    mat('cone_orange', '#c2571a', rough=0.75)
    mat('petal_fmn', '#7aa8f4', rough=0.6, sss=0.2)
    mat('petal_yarrow_pink', '#ee9fc2', rough=0.65)
    mat('petal_yarrow_yellow', '#f2dc6a', rough=0.65)
    mat('petal_rose', '#f7b1cc', rough=0.6, sss=0.3)
    mat('rose_hip', '#c8281a', rough=0.35)
    mat('umbel_seed', '#9a8a5a', rough=0.7)
    mat('petal_marigold', '#f58a14', rough=0.55, sss=0.2)


def fan_patch(L, W, rng, nb=7, spread=1.3, bend=-0.25, thin=False):
    ps = []
    for i in range(nb):
        f = (i - (nb - 1) / 2) / max(1, (nb - 1) / 2)
        V, F, C, UV = blade(L * (1 - 0.3 * abs(f)) * rng.uniform(0.85, 1.1), W, nu=2, nv=2, a=0.5, b=0.8, bend=bend + rng.uniform(-0.15, 0.15),
                            cols=[(0, '#4a7c3a'), (1, '#74a84c')], fold=0.2)
        ps.append((xfv(Rz(-f * spread * 0.5), V), F, C, UV))
    return cat(ps)


def feathers(g, pts, rng, n, L, W, t0, t1, nb=7, elev=0.7, m='leaf_green'):
    for i in range(n):
        t = t0 + (t1 - t0) * i / max(1, n - 1)
        s = 1 - 0.5 * t
        leaf_on_path(g, m, pts, t, i * 2.4 + rng.uniform(-.3, .3), elev + rng.uniform(-.2, .2), fan_patch(L * s, W, rng, nb))


def basal_feathers(g, rng, n, L, W, nb=7):
    a0 = rng.uniform(0, TAU)
    for i in range(n):
        a = a0 + i * TAU / n
        el = rng.uniform(0.3, 0.7)
        rad = np.array([math.cos(a), math.sin(a), 0])
        g.add('leaf_green', fan_patch(L * rng.uniform(.8, 1.1), W, rng, nb, bend=-0.4),
              orient(rad * 0.004, rad * math.cos(el) + np.array([0, 0, math.sin(el)]), [0, 0, 1.0]))


# ------------------------------------------------------------------ COSMOS
def cosmos_head(g, xf, rng, m, cols, n=8, L=0.04, open_=1.0):
    petal_ring(g, m, n, L, 0.038, rng, r0=0.004, z0=0.0, elev=(0.02, 0.2) if open_ > .5 else 0.45, elev_j=0.04, xf=xf,
               a=0.6, b=0.28, nu=5, nv=4, bend=(-0.25, 0.1), cup=0.25, wave=0.12, wavef=1.2, notch=0.05, serr=0.0,
               cols=cols, edge=0.05, lj=0.06, wj=0.08, jit=0.05)
    g.add('disc_yellow', dome(0.0075, 0.0055, nu=3, nseg=12, cols=lambda u, th: grad(u, [(0, '#c08a10'), (0.6, '#eab616'), (1, '#f2c92a')])), xf @ T(0, 0, -0.0004))
    petal_ring(g, 'sepal_green', 8, 0.008, 0.004, rng, r0=0.002, z0=-0.003, elev=-0.7, xf=xf, a=0.6, b=0.5, nu=2, nv=2, bend=0.2,
               cols=[(0, '#4c7a2a'), (1, '#7fa84a')])


def cosmos(v, rng):
    ensure(); g = Geo()
    h = {'a': 1.0, 'b': 1.15, 'c': 0.85, 'd': 1.05}[v] * rng.uniform(.95, 1.05)
    m, cols = {'a': ('petal_cosmos', [(0, '#c21f6e'), (0.3, '#ee7fb0'), (1, '#f8b7d3')]),
               'b': ('petal_white', [(0, '#d6b0c0'), (0.3, '#fbf4f7'), (1, '#ffffff')]),
               'c': ('petal_cosmos_mag', [(0, '#7a0f4a'), (0.35, '#d22a82'), (1, '#ea5aa4')]),
               'd': ('petal_cosmos', [(0, '#b81a66'), (0.3, '#f08ab8'), (1, '#fbc4da')])}[v]
    pts = stem_path(h, rng, lean=0.1, sway=0.04, n=9)
    gstem(g, pts, 0.0024, 0.0012, sides=5)
    cosmos_head(g, head_frame(pts, nod=0.45, rng=rng), rng, m, cols, n=8 if v != 'd' else 9)
    for k, (t, ln, nod) in enumerate([(0.62, 0.30, 0.6), (0.42, 0.22, 0.4)]):
        bp = side_branch(pts, t, rng, ln, out=0.55)
        gstem(g, bp, 0.0013, 0.0008, sides=4)
        if v == 'd' and k == 1:
            bx = head_frame(bp, nod=0.3, rng=rng)
            g.add('sepal_green', ellipsoid(0.008, 0.008, 0.009, nu=4, nseg=8, cols=lambda u, th: grad(u, [(0, '#527d2c'), (0.7, '#7da84a'), (1, '#d890b0')])), bx @ T(0, 0, 0.005))
        else:
            cosmos_head(g, head_frame(bp, nod=nod, rng=rng), rng, m, cols, n=8, L=0.034)
    feathers(g, pts, rng, 10, 0.1, 0.0028, 0.06, 0.8, nb=9, elev=0.75)
    basal_feathers(g, rng, 3, 0.08, 0.0028)
    return g


# ------------------------------------------------------------------ ECHINACEA
def echinacea(v, rng):
    ensure(); g = Geo()
    h = {'a': 0.8, 'b': 0.9, 'c': 0.7, 'd': 0.85}[v] * rng.uniform(.95, 1.05)
    pts = stem_path(h, rng, lean=0.07, sway=0.03, n=8)
    gstem(g, pts, 0.0032, 0.002, sides=5, c0='#4e6a2a', c1='#6a7f3a')
    xf = head_frame(pts, nod={'a': 0.25, 'b': 0.45, 'c': 0.1, 'd': 0.35}[v], rng=rng)
    n = {'a': 14, 'b': 12, 'c': 15, 'd': 13}[v]
    petal_ring(g, 'petal_echinacea', n, 0.05, 0.0125, rng, r0=0.012, z0=0.002, elev=(-0.15, -0.05), elev_j=0.06, xf=xf, a=0.55, b=0.35,
               nu=6, nv=2, bend=(-1.2, -0.6), cup=0.35, twist=(-0.4, 0.4), notch=0.06, serr=0.0,
               cols=[(0, '#9a2a66'), (0.3, '#d45aa4'), (1, '#e889c2')], edge=0.05, lj=0.12, wj=0.1, mid=-0.05, jit=0.1)
    nz = make_noise(rng.randint(999))

    def lobe(u, th):
        return 1 + 0.07 * np.sin(th * 16 + u * 22) * (u > .1) + 0.04 * nz(np.stack(np.broadcast_arrays(np.cos(th), np.sin(th), u), -1) * 3)

    def cols(u, th):
        c = grad(u, [(0, '#5a2210'), (0.3, '#a8440f'), (0.8, '#e0781c'), (1, '#e9921e')])
        return c * (0.88 + 0.12 * np.sin(th * 16 + u * 22)[..., None])
    def cprof(u):
        return 0.021 * (1 - u ** 1.7) + 0.0008, 0.036 * u ** 0.75
    cone = revolve(cprof, 8, 20, lobe=lobe, cols=cols)
    g.add('cone_orange', cone, xf @ T(0, 0, -0.006))
    petal_ring(g, 'sepal_green', 10, 0.013, 0.005, rng, r0=0.005, z0=-0.004, elev=-0.5, xf=xf, a=0.6, b=0.5, nu=2, nv=2, cols=[(0, '#4c7a2a'), (1, '#7fa84a')])
    lance_leaves(g, pts, rng, 4, 0.12, 0.028, t0=0.1, t1=0.5, a=0.55, b=0.8, fold=0.3, serr=0.1, nu=8, cols=[(0, '#3a6424'), (1, '#5c8f32')])
    rosette(g, 'leaf_green', 4, 0.15, 0.04, rng, elev=(0.2, 0.55), a=0.6, b=0.7, nu=8, nv=2, bend=(-0.5, -0.2), fold=0.25,
            cols=[(0, '#355f22'), (1, '#5a8e32')], mid=0.3)
    return g


# ------------------------------------------------------------------ QUEEN ANNE'S LACE
def umbel(g, base, rng, R, nrays, seedmode=False, floret=0.0052, cup=0.0):
    m_fl = 'umbel_seed' if seedmode else 'petal_white'
    for i in range(nrays):
        f = (i + 0.5) / nrays
        r = R * math.sqrt(f); a = i * 2.39996
        z = 0.06 - 0.0 + (0.0 if not seedmode else 0) + cup * (r / R) ** 2 - 0.012 * (r / R) ** 2
        z = 0.045 + (cup * (r / R) ** 1.5 if cup else -0.01 * (r / R) ** 2)
        end = np.array([r * math.cos(a), r * math.sin(a), z])
        d = unit(end)
        ray = blade(np.linalg.norm(end), 0.0011, nu=1, nv=2, a=0.3, b=0.3, lod=False, cols=[(0, '#7a9a4a'), (1, '#a8b878')], widthfn=lambda u: np.ones_like(u))
        g.add('stem_green', ray, base @ orient(np.zeros(3), d, [0, 0, 1.0]))
        nf = 9 if not seedmode else 4
        sm = 1.0
        for k in range(nf):
            ka = k * 2.39996 + i; kr = 0.0135 * math.sqrt((k + 0.3) / nf) * (1 if nf > 1 else 0)
            p = end + np.array([kr * math.cos(ka), kr * math.sin(ka), 0.004 - (kr / 0.0135) ** 2 * 0.003])
            fr = floret * rng.uniform(0.85, 1.15)
            if seedmode:
                g.add(m_fl, ellipsoid(0.0016, 0.0016, 0.0024, nu=2, nseg=5, lod=False, cols=lambda u, th: grad(u, [(0, '#6a5a3a'), (1, '#b0a070')])), base @ T(p) @ Rx(rng.uniform(-.6, .6)))
            else:
                g.add(m_fl, lobed_disc(fr, lobes=5, rings=1, segs=8, depth=0.3, cup=0.3, lod=False,
                                       cols=lambda u, th: grad(u, [(0, '#e8e6c0'), (0.35, '#fbfbf2'), (1, '#ffffff')])),
                      base @ T(p) @ Rx(rng.uniform(-.35, .35)) @ Rz(rng.uniform(0, TAU)))


def queen_annes_lace(v, rng):
    ensure(); g = Geo()
    h = {'a': 0.95, 'b': 0.8, 'c': 1.05, 'd': 0.7}[v] * rng.uniform(.95, 1.05)
    pts = stem_path(h, rng, lean=0.06, sway=0.025, n=9)
    gstem(g, pts, 0.0028, 0.0014, sides=5, c0='#5a7a30', c1='#8aaa50')
    seed = v == 'b'
    base = frame_z(pts[-1], pathpt(pts, 1.0)[1], rng.uniform(0, TAU))
    umbel(g, base, rng, R=0.07 if v != 'd' else 0.055, nrays=26 if v != 'd' else 20, seedmode=seed, cup=0.03 if seed else 0)
    if seed:
        pass
    elif v in ('a', 'c'):
        g.add('petal_purple', lobed_disc(0.0035, lobes=5, rings=1, segs=10, lod=False, cols=lambda u, th: grad(u, [(0, '#3a1030'), (1, '#7a2a60')])), base @ T(0, 0, 0.05))
    if v in ('c', 'd', 'b'):
        bp = side_branch(pts, 0.6, rng, 0.25, out=0.45)
        gstem(g, bp, 0.0016, 0.001, sides=4)
        b2 = frame_z(bp[-1], pathpt(bp, 1.0)[1], 0)
        umbel(g, b2, rng, R=0.04, nrays=12, seedmode=seed, cup=0.02 if seed else 0)
    # 3-pronged bracts
    petal_ring(g, 'leaf_green', 9, 0.05, 0.0025, rng, r0=0.002, z0=0.0, elev=(0.3, 0.9), xf=base, a=0.5, b=0.8, nu=3, nv=2, cols=[(0, '#5a8a3a'), (1, '#8ab860')], bend=-0.2)
    feathers(g, pts, rng, 5, 0.12, 0.0035, 0.1, 0.6, nb=9, elev=0.65)
    basal_feathers(g, rng, 4, 0.14, 0.0035, nb=9)
    return g


# ------------------------------------------------------------------ CHAMOMILE
def chamomile_head(g, xf, rng, n=14, s=1.0):
    petal_ring(g, 'petal_white', n, 0.011 * s, 0.0042 * s, rng, r0=0.004 * s, z0=-0.0005, elev=(-0.55, -0.2), elev_j=0.08, xf=xf, a=0.5, b=0.4,
               nu=3, nv=2, bend=(-0.25, 0.05), cup=0.3, notch=0.05, cols=[(0, '#ece6b0'), (0.3, '#fbf9ee'), (1, '#ffffff')], jit=0.15, lj=0.12)
    g.add('disc_yellow', dome(0.0058 * s, 0.0078 * s, nu=4, nseg=12, cols=lambda u, th: grad(u, [(0, '#b8860c'), (0.5, '#eeb914'), (1, '#f6cf2e')]),
                              lobe=lambda u, th: 1 + 0.06 * np.sin(th * 11 + u * 10)), xf @ T(0, 0, -0.002))


def chamomile(v, rng):
    ensure(); g = Geo()
    h = {'a': 0.36, 'b': 0.42, 'c': 0.30, 'd': 0.38}[v] * rng.uniform(.95, 1.05)
    pts = stem_path(h, rng, lean=0.12, sway=0.05, n=8)
    gstem(g, pts, 0.0014, 0.0008, sides=4)
    chamomile_head(g, head_frame(pts, nod=0.35, rng=rng), rng, n=lc(14, 1), s=1.0)
    for k, (t, ln) in enumerate([(0.5, 0.18), (0.3, 0.14), (0.68, 0.1)][:{'a': 3, 'b': 3, 'c': 2, 'd': 3}[v]]):
        bp = side_branch(pts, t, rng, ln, out=0.6)
        gstem(g, bp, 0.0009, 0.0006, sides=4)
        if v == 'd' and k == 2:
            bx = head_frame(bp, nod=0.2, rng=rng)
            g.add('sepal_green', ellipsoid(0.0045, 0.0045, 0.005, nu=3, nseg=8, cols=lambda u, th: grad(u, [(0, '#527d2c'), (1, '#8ab04e')])), bx @ T(0, 0, 0.003))
        else:
            chamomile_head(g, head_frame(bp, nod=rng.uniform(.3, .7), rng=rng), rng, n=12, s=0.9)
    feathers(g, pts, rng, 6, 0.045, 0.002, 0.08, 0.75, nb=5, elev=0.7)
    basal_feathers(g, rng, 4, 0.055, 0.002, nb=5)
    return g


# ------------------------------------------------------------------ YARROW
def yarrow(v, rng):
    ensure(); g = Geo()
    h = {'a': 0.72, 'b': 0.85, 'c': 0.62, 'd': 0.78}[v] * rng.uniform(.95, 1.05)
    mname = {'a': 'petal_white', 'b': 'petal_white', 'c': 'petal_yarrow_pink', 'd': 'petal_yarrow_yellow'}[v]
    ctr = {'a': '#fbfbf2', 'b': '#fbfbf2', 'c': '#f6cfe0', 'd': '#f7e89a'}[v]
    pts = stem_path(h, rng, lean=0.05, sway=0.02, n=9)
    gstem(g, pts, 0.0022, 0.0012, sides=5, c0='#567a30', c1='#8aa858')
    top = pts[-1]
    ncl = {'a': 6, 'b': 7, 'c': 5, 'd': 6}[v]
    for i in range(ncl):
        f = (i + 0.3) / ncl
        r = 0.05 * math.sqrt(f) if i else 0; a = i * 2.4
        cp = top + np.array([r * math.cos(a), r * math.sin(a), 0.03 - 0.02 * (r / 0.05) ** 2])
        sp = bez(top - np.array([0, 0, 0.03]), top + np.array([0, 0, 0.0]), cp - np.array([0, 0, 0.02]), cp, 4)
        gstem(g, sp, 0.0009, 0.0006, sides=3, cap=False)
        for k in range(lc(38, 1)):
            ka = k * 2.39996; kr = 0.03 * math.sqrt((k + 0.5) / 38)
            p = cp + np.array([kr * math.cos(ka), kr * math.sin(ka), 0.003 - 0.006 * (kr / 0.03) ** 2])
            fr = 0.0046 * rng.uniform(0.85, 1.1)
            g.add(mname, lobed_disc(fr, lobes=5, rings=1, segs=8, depth=0.35, cup=0.25, lod=False,
                                    cols=(lambda ct: lambda u, th: grad(u, [(0, '#d8c070'), (0.3, ct), (1, ct)]))(ctr)),
                  T(p) @ Rx(rng.uniform(-.4, .4)) @ Rz(rng.uniform(0, TAU)))
    feathers(g, pts, rng, 12, 0.09, 0.0028, 0.1, 0.85, nb=11, elev=0.9, m='leaf_dark')
    basal_feathers(g, rng, 5, 0.14, 0.0028, nb=13)
    return g


# ------------------------------------------------------------------ MARIGOLD
def marigold_head(g, xf, rng, m, hexes, s=1.0, dense=1.0):
    rings = [(24, 0.030, 0.06), (18, 0.026, 0.22), (13, 0.021, 0.42), (8, 0.016, 0.7)]
    for k, (n, L, el) in enumerate(rings):
        petal_ring(g, m, n, L * s, 0.0078 * s, rng, r0=0.004 * s, z0=0.0015 * k * s, elev=(el - 0.04, el + 0.06), elev_j=0.05, xf=xf, a=0.55, b=0.15,
                   nu=3, nv=4, bend=(-0.3, 0.2), cup=0.2, notch=0.0, wave=0.05, wavef=1.5, cols=[(0, hexes[0]), (0.35, hexes[1]), (1, hexes[2])],
                   edge=0.05, jit=0.15, lj=0.1, wj=0.12)
    g.add('disc_yellow', dome(0.006 * s, 0.004 * s, nu=2, nseg=8, cols=lambda u, th: grad(u, [(0, hexes[0]), (1, hexes[1])])), xf @ T(0, 0, 0.0055 * s))
    petal_ring(g, 'sepal_green', 14, 0.013 * s, 0.0032 * s, rng, r0=0.003, z0=-0.004, elev=-0.35, xf=xf, a=0.6, b=0.5, nu=2, nv=2, cols=[(0, '#4c7a2a'), (1, '#7fa84a')], bend=0.25)


def marigold(v, rng):
    ensure(); g = Geo()
    h = {'a': 0.38, 'b': 0.44, 'c': 0.33, 'd': 0.4}[v] * rng.uniform(.95, 1.05)
    m, hx = {'a': ('petal_marigold', ('#b84a08', '#ee7d10', '#f9a020')), 'b': ('petal_yellow', ('#d8920c', '#f5c412', '#fbdc3a')),
             'c': ('petal_marigold', ('#a83a06', '#e0640c', '#f48a16')), 'd': ('petal_marigold', ('#9a3a08', '#f08a16', '#fbb530'))}[v]
    pts = stem_path(h, rng, lean=0.1, sway=0.04, n=7)
    gstem(g, pts, 0.0025, 0.0016, sides=5, c0='#6a8a3a', c1='#8aaa50')
    marigold_head(g, head_frame(pts, nod=0.3, rng=rng), rng, m, hx, s=1.0)
    bp = side_branch(pts, 0.45, rng, 0.14, out=0.6)
    gstem(g, bp, 0.0016, 0.001, sides=4)
    if v in ('a', 'b', 'c'):
        marigold_head(g, head_frame(bp, nod=0.5, rng=rng), rng, m, hx, s=0.78)
    else:
        bx = head_frame(bp, nod=0.2, rng=rng)
        g.add('sepal_green', ellipsoid(0.01, 0.01, 0.011, nu=4, nseg=8, cols=lambda u, th: grad(u, [(0, '#527d2c'), (0.8, '#7da84a'), (1, '#f0a030')])), bx @ T(0, 0, 0.006))
    lance_leaves(g, pts, rng, 6, 0.085, 0.021, t0=0.05, t1=0.6, m='leaf_grey', a=0.85, b=0.5, bend=-0.25, fold=0.2, nu=6,
                 cols=[(0, '#4a7e34'), (1, '#6fa64a')], elev=0.8)
    rosette(g, 'leaf_grey', 4, 0.09, 0.022, rng, elev=(0.3, 0.6), a=0.85, b=0.5, nu=6, nv=2, bend=(-0.4, -0.15), fold=0.2, cols=[(0, '#4a7e34'), (1, '#6fa64a')], mid=0.25)
    return g


# ------------------------------------------------------------------ FORGET-ME-NOT
def forget_me_not(v, rng):
    ensure(); g = Geo()
    ns = {'a': 6, 'b': 8, 'c': 5, 'd': 7}[v]
    blue = ['#7ea6ee', '#6f9cf2', '#8db2f5', '#7aa8f4'][ord(v) - 97]
    for i in range(ns):
        a = i * 2.4 + rng.uniform(-.3, .3)
        hh = rng.uniform(0.09, 0.16)
        p0 = np.array([0.01 * math.cos(a), 0.01 * math.sin(a), 0])
        d = np.array([math.cos(a), math.sin(a), 0])
        pts = bez(p0, p0 + np.array([0, 0, hh * .5]) + d * 0.02, p0 + d * hh * 0.35 + np.array([0, 0, hh * .8]), p0 + d * hh * 0.5 + np.array([0, 0, hh * .85]), 6 if not LOD else 3)
        gstem(g, pts, 0.0011, 0.0007, sides=4, c0='#6a8a3a', c1='#88a850')
        nfl = rng.randint(8, 13)
        for k in range(nfl):
            t = 0.3 + 0.65 * k / nfl
            pos, tan = pathpt(pts, t)
            nrm = unit(np.array([0, 0, 0.85]) + d * 0.35 + rng.normal(0, .3, 3) * np.array([1, 1, 0.4]))
            pos = pos + nrm * 0.003
            fl = 0.0068 * (1.0 if k < nfl - 1 else 0.6) * rng.uniform(.9, 1.1)
            g.add('petal_fmn', lobed_disc(fl, lobes=5, rings=2, segs=15, depth=0.05, cup=0.25, lod=False, sharp=1.0,
                                          cols=(lambda b: lambda u, th: grad(u, [(0, '#f8f2b0'), (0.22, '#f4f0d0'), (0.36, b), (1, b)]))(blue)),
                  frame_z(pos, nrm, rng.uniform(0, TAU)))
            g.add('petal_yellow', lobed_disc(fl * 0.3, lobes=5, rings=1, segs=10, depth=0.0, lod=False, cols=lambda u, th: np.ones(u.shape + (3,)) * lin('#f6d21c')),
                  frame_z(pos + nrm * 0.0004, nrm, 0))
        for k in range(3):
            t = 0.92 + 0.08 * k
            pos, tan = pathpt(pts, min(t, 1.0))
            g.add('petal_pink', ellipsoid(0.0018, 0.0018, 0.0024, nu=2, nseg=5, lod=False, cols=lambda u, th: np.ones(u.shape + (3,)) * lin('#ee90c0')),
                  T(pos + np.array([rng.normal(0, .003), rng.normal(0, .003), 0.003])))
    # leaves
    for i in range(14):
        a = i * 2.4
        el = rng.uniform(0.1, 0.7)
        rad = np.array([math.cos(a), math.sin(a), 0])
        p = blade(rng.uniform(0.04, 0.07), 0.013, nu=4, nv=2, a=0.7, b=0.7, bend=(-0.5, -0.1), fold=0.3, cols=[(0, '#3a6a28'), (1, '#6aa03c')], mid=0.25)
        g.add('leaf_green', p, orient(rad * 0.01, rad * math.cos(el) + np.array([0, 0, math.sin(el)]), [0, 0, 1.0]))
    return g


# ------------------------------------------------------------------ WILD ROSE
def pinnate_leaf(rng, s=1.0):
    ps = []
    for y, ang, sz in [(0.012, 1.0, 0.75), (0.012, -1.0, 0.75), (0.035, 0.95, 0.95), (0.035, -0.95, 0.95), (0.058, 0.0, 1.05)]:
        V, F, C, UV = blade(0.038 * sz * s, 0.021 * sz * s, nu=4, nv=2, a=0.7, b=0.55, serr=0.12, bend=(-0.25, 0.0), fold=0.25, lod=False,
                            cols=[(0, '#2f5e22'), (1, '#4f8a30')], mid=0.3, edge=0.1)
        ps.append((xfv(T(0, y, 0) @ Rz(-ang), V), F, C, UV))
    rach = tube(np.array([[0, 0, 0], [0, 0.03, 0.001], [0, 0.06, 0]]), 0.0008, sides=3, cols=lin('#5a7a30'), lod=False)
    ps.append(rach)
    return cat(ps)


def rose_flower(g, xf, rng, s=1.0):
    petal_ring(g, 'petal_rose', 5, 0.026 * s, 0.03 * s, rng, r0=0.003 * s, z0=0.0, elev=(0.25, 0.5), elev_j=0.05, xf=xf, a=0.6, b=0.28,
               nu=4, nv=4, bend=(-0.2, 0.25), cup=0.4, notch=0.14, wave=0.08, wavef=1.0, cols=[(0, '#fffbe8'), (0.3, '#f9d0df'), (0.7, '#f095b8'), (1, '#e8709f')],
               edge=-0.03, jit=0.05, lj=0.05, wj=0.05)
    g.add('stamen_yellow', dome(0.0075 * s, 0.003 * s, nu=2, nseg=16, cols=lambda u, th: grad(u, [(0, '#e0b020'), (1, '#f4d23a')]),
                                lobe=lambda u, th: 1 + 0.12 * np.sin(th * 18)), xf @ T(0, 0, 0.001 * s))
    g.add('anther_dark', dome(0.0025 * s, 0.002 * s, nu=1, nseg=8), xf @ T(0, 0, 0.0035 * s))
    petal_ring(g, 'sepal_green', 5, 0.018 * s, 0.005 * s, rng, r0=0.002, z0=-0.002, elev=(-0.9, -0.6), xf=xf, a=0.5, b=0.7, nu=3, nv=2, cols=[(0, '#4c7a2a'), (1, '#7fa84a')], serr=0.0)


def rose_wild(v, rng):
    ensure(); g = Geo()
    sc = {'a': 1.0, 'b': 0.85, 'c': 1.1, 'd': 0.95}[v]
    ncane = {'a': 6, 'b': 5, 'c': 7, 'd': 6}[v]
    tips = []
    for i in range(ncane):
        a = i * TAU / ncane + rng.uniform(-.3, .3)
        d = np.array([math.cos(a), math.sin(a), 0])
        hh = 0.62 * sc * rng.uniform(.75, 1.1)
        out = rng.uniform(0.18, 0.36) * sc
        p0 = d * 0.02
        pts = bez(p0, p0 + np.array([0, 0, hh * 0.6]), d * out * 1.3 + np.array([0, 0, hh * 0.95]), d * out * 1.5 + np.array([0, 0, hh * 0.8]), 8 if not LOD else 4)
        gstem(g, pts, 0.0045, 0.0014, sides=4, c0='#5a3a28', c1='#6f8a3a', m='bark_cane')
        for k in range(10):
            t = 0.1 + 0.85 * k / 9
            pos, tan = pathpt(pts, t)
            e1, e2 = stem_frame(tan)
            az = k * 2.4 + i
            r = math.cos(az) * e1 + math.sin(az) * e2
            g.add('bark_cane', blade(0.007, 0.0045, nu=1, nv=2, lod=False, a=0.3, b=0.6, bend=0.4, widthfn=lambda u: 1 - u, cols=[(0, '#6a4a36'), (1, '#b09070')]),
                  orient(pos, r * 0.6 + tan * -0.3, tan))
        nl = 6
        for k in range(nl):
            t = 0.25 + 0.75 * k / (nl - 1)
            leaf_on_path(g, 'leaf_green', pts, t, k * 2.4 + i * 1.3, rng.uniform(0.6, 1.1), pinnate_leaf(rng, sc), roll=rng.uniform(-.3, .3))
        tips.append(pts)
    # blooms on tips
    nb = {'a': 6, 'b': 5, 'c': 7, 'd': 3}[v]
    for i in range(nb):
        pts = tips[i % len(tips)]
        pos, tan = pathpt(pts, 1.0 if i < len(tips) else 0.85)
        tilt = unit(tan * 0.6 + np.array([rng.normal(0, .3), rng.normal(0, .3), 0.8]))
        xf = frame_z(pos + tilt * 0.008, tilt, rng.uniform(0, TAU))
        rose_flower(g, xf, rng, s=rng.uniform(1.25, 1.5))
    # buds
    for i in range(2 + (v == 'b')):
        pts = tips[(i + 2) % len(tips)]
        pos, tan = pathpt(pts, 0.97)
        bx = frame_z(pos, unit(tan + np.array([0, 0, .6])), 0)
        g.add('sepal_green', ellipsoid(0.007, 0.007, 0.012, nu=4, nseg=8, cols=lambda u, th: grad(u, [(0, '#527d2c'), (0.6, '#7da84a'), (1, '#f08ab0')])), bx @ T(0, 0, 0.009))
    if v in ('c', 'd'):
        for i in range(5 if v == 'd' else 3):
            pts = tips[(i + 1) % len(tips)]
            pos, tan = pathpt(pts, 0.9)
            px = frame_z(pos + np.array([0, 0, -0.02]) , [rng.normal(0, .4), rng.normal(0, .4), -1], 0)
            g.add('rose_hip', ellipsoid(0.0085, 0.0085, 0.012, nu=4, nseg=8, cols=lambda u, th: grad(u, [(0, '#8a1a10'), (0.5, '#d42a1a'), (1, '#e8462a')])), px @ T(0, 0, 0.008))
            g.add('sepal_green', lobed_disc(0.008, lobes=5, rings=1, segs=10, depth=0.4, lod=False, cols=lambda u, th: np.ones(u.shape + (3,)) * lin('#5a6a30')), px @ T(0, 0, 0.02))
    return g


DEFS = [
    dict(sp='rose_wild', fn=rose_wild, variants=['a', 'b', 'c', 'd'], ko='들장미', weight=0.35, habitat='forest_edge', sway=0.3),
    dict(sp='forget_me_not', fn=forget_me_not, variants=['a', 'b', 'c', 'd'], ko='물망초', weight=0.5, habitat='wet', sway=0.4),
    dict(sp='cosmos', fn=cosmos, variants=['a', 'b', 'c', 'd'], ko='코스모스', weight=0.5, habitat='path', sway=0.7),
    dict(sp='echinacea', fn=echinacea, variants=['a', 'b', 'c', 'd'], ko='에키네시아', weight=0.3, habitat='garden', sway=0.4),
    dict(sp='queen_annes_lace', fn=queen_annes_lace, variants=['a', 'b', 'c', 'd'], ko='야생당근(퀸앤스레이스)', weight=0.55, habitat='meadow', sway=0.6),
    dict(sp='chamomile', fn=chamomile, variants=['a', 'b', 'c', 'd'], ko='카모마일', weight=0.6, habitat='path', sway=0.6),
    dict(sp='yarrow', fn=yarrow, variants=['a', 'b', 'c', 'd'], ko='서양톱풀', weight=0.6, habitat='meadow', sway=0.5),
    dict(sp='marigold', fn=marigold, variants=['a', 'b', 'c', 'd'], ko='금잔화', weight=0.4, habitat='garden', sway=0.5),
]
