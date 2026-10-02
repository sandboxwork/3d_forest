"""pbr_wood_floor, pbr_wood_pine, pbr_wood_oak, pbr_wood_dark  (grain runs along image x)"""
import sys
sys.path.insert(0, '/shared/river/assets/blender')
from tx_lib import *

N = 512


def wood_fields(seed, v, xpx, ypx, H, rf, wa, wb, knots, fine=1.0, pore=0.0, rc=1.0):
    """v: 0..1 across board (ring coordinate). Returns c (0 light..1 dark), h, pores, core."""
    wn = noise(N, seed + 1, 1.6, 2.6)
    wn2 = noise(N, seed + 2, 5, 12)
    wn3 = noise(N, seed + 6, 18, 60)
    phase = rf * v + wa * wn + wb * wn2 + 0.05 * wb * wn3 + (seed % 7) * 0.37
    core = np.zeros((N, N), f32)
    kh = np.zeros((N, N), f32)
    for (kx, ky, R) in knots:
        dx = np.mod(xpx - kx + N / 2, N) - N / 2
        dy = np.mod(ypx - ky + H / 2, H) - H / 2
        d = np.sqrt((dx / 1.7) ** 2 + dy ** 2)
        w = np.exp(-(d / R) ** 2)
        phase = phase * (1 - w) + w * (d / R * 3.2) + 1.4 * (dy / R) * np.exp(-(d / (2.4 * R)) ** 2)
        core = np.maximum(core, np.exp(-(d / (0.5 * R)) ** 2))
        kh = np.maximum(kh, np.exp(-(d / (1.1 * R)) ** 2))
    t = np.mod(phase, 1.0)
    lw = (t ** 3) * (1 - sstep(0.93, 1.0, t))
    s = noise(N, seed + 3, 7, 240, hp=0.04)
    s2 = noise(N, seed + 5, 3, 90, hp=0.05)
    pn = noise(N, seed + 4, 90, 420, hp=0.1)
    pores = sstep(1.2, 2.3, pn) * pore
    c = lw * 0.62 * rc + 0.11 * fine * s + 0.09 * fine * s2 + 0.35 * core + 0.30 * pores
    h = 0.45 + 0.20 * lw + 0.07 * fine * s + 0.04 * s2 - 0.22 * pores + 0.2 * kh
    return np.clip(c, 0, 1), h, pores, core


def planks(seed, rows, ppr, pal, rf, wa, wb, gap, bevel, nknots, tv, jgap, pore, rc=1.0, fine=1.0,
           rough0=0.7, wear=0.4, rng_extra=None):
    r = np.random.default_rng(seed)
    x, y = grid(N)
    H = N // rows
    row = np.floor(y / H).astype(int)
    ypx = y - row * H
    v = ypx / H
    albedo = np.zeros((N, N, 3), f32)
    h = np.zeros((N, N), f32)
    rough = np.zeros((N, N), f32)
    edge = np.full((N, N), 1e3, f32)
    jedge = np.full((N, N), 1e3, f32)
    for ri in range(rows):
        np_ = ppr if np.ndim(ppr) == 0 else ppr[ri]
        xa = r.random() * N
        joints = [xa]
        if np_ == 2:
            joints.append((xa + N * (0.42 + 0.16 * r.random())) % N)
        rm = row == ri
        # piece id by joints
        if np_ == 1:
            pid = np.zeros((N, N), int)
        else:
            s0 = np.mod(x - joints[0], N)
            span = (joints[1] - joints[0]) % N
            pid = (s0 >= span).astype(int)
            for j in joints:
                dj = np.abs(np.mod(x - j + N / 2, N) - N / 2)
                jedge = np.where(rm, np.minimum(jedge, dj), jedge)
        for pi in range(np_):
            m = rm & (pid == pi)
            sd = seed * 100 + ri * 10 + pi
            kn = []
            for k in range(r.poisson(nknots) if nknots else 0):
                kn.append((r.random() * N, H * (0.2 + 0.6 * r.random()), 10 + 14 * r.random()))
            rfp = rf * (0.8 + 0.5 * r.random()) if rows > 1 else rf
            c, hh, pores, core = wood_fields(sd, v, x, ypx, H, rfp, wa, wb, kn, fine, pore, rc)
            tone = 1 + tv * (r.random() * 2 - 1)
            hue = tv * 0.25 * (r.random() * 2 - 1)
            cl = np.array(pal[0], f32) * [1 + hue, 1, 1 - hue] * tone
            cd = np.array(pal[1], f32) * [1 + hue, 1, 1 - hue] * tone
            col = mix(cl, cd, c)
            albedo = np.where(m[..., None], col, albedo)
            h = np.where(m, hh, h)
            rough = np.where(m, rough0 + 0.12 * (c - 0.3) + 0.1 * pores, rough)
    # board edges
    ex = np.minimum(ypx, H - ypx) if rows > 1 else np.full((N, N), 1e3, f32)
    if rows > 1:
        g = np.maximum(gap / 2, 0.01)
        eprof = sstep(g, g + bevel, ex)
        jprof = sstep(jgap / 2, jgap / 2 + max(bevel * 0.6, 1.0), jedge)
        prof = np.minimum(eprof, jprof)
        shadow = 1 - sstep(0, g + bevel * 1.4, np.minimum(ex, jedge))
        albedo = albedo * (1 - 0.6 * shadow[..., None] ** 1.2) * 1.0
        h = h * (0.25 + 0.75 * prof) * 1.0 - 0.9 * (1 - prof)
        rough = rough * prof + 1.0 * (1 - prof)
    # wear: low freq light patches + scratches
    w = fbm(N, seed + 900, 2.5, 4)
    wearm = sstep(0.0, 1.4, w) * wear
    grey = albedo.mean(-1, keepdims=True)
    albedo = albedo * (1 - 0.35 * wearm[..., None]) + 0.35 * wearm[..., None] * (grey * 1.15 + 0.03)
    sc = noise(N, seed + 901, 10, 400, hp=0.03)
    scr = sstep(2.6, 3.4, sc)
    albedo = albedo * (1 - 0.15 * scr[..., None]) + 0.0
    h = h - 0.08 * scr + 0.05 * wearm * noise(N, seed + 902, 60, 60)
    rough = rough + 0.06 * w * 0.5
    return albedo, h, rough


def floor():
    pal = ((0.60, 0.47, 0.34), (0.35, 0.25, 0.16))
    a, h, r = planks(11, 4, [2, 1, 2, 1], pal, rf=7, wa=1.0, wb=0.20, gap=4, bevel=5, nknots=0.9, tv=0.14,
                     jgap=3, pore=0.5, rough0=0.74, wear=0.5)
    save('pbr_wood_floor', a, normal_from_height(h, 7.0), r)


def pine():
    pal = ((0.88, 0.70, 0.45), (0.66, 0.43, 0.21))
    a, h, r = planks(23, 4, 1, pal, rf=6, wa=0.6, wb=0.12, gap=3, bevel=6, nknots=0.8, tv=0.07,
                     jgap=0, pore=0.0, rough0=0.58, wear=0.3, rc=1.1)
    save('pbr_wood_pine', a, normal_from_height(h, 6.0), r)


def oak():
    pal = ((0.62, 0.43, 0.24), (0.34, 0.20, 0.10))
    a, h, r = planks(37, 1, 1, pal, rf=30, wa=0.9, wb=0.2, gap=0, bevel=0, nknots=0, tv=0.0,
                     jgap=0, pore=1.0, rough0=0.45, wear=0.15, rc=0.9, fine=1.1)
    save('pbr_wood_oak', a, normal_from_height(h, 5.0), r)


def dark():
    pal = ((0.27, 0.155, 0.085), (0.095, 0.054, 0.032))
    a, h, r = planks(51, 1, 1, pal, rf=11, wa=0.9, wb=0.2, gap=0, bevel=0, nknots=0, tv=0.0,
                     jgap=0, pore=0.4, rough0=0.66, wear=0.25, rc=1.3)
    # adze marks: elongated scooped facets (grain along x, strokes across)
    x, y = grid(N)
    wx = x + 10 * noise(N, 61, 6, 6)
    wy = y + 10 * noise(N, 62, 6, 6)
    d1, d2, rid, cx, cy = vor(N, 7, 3, 63, wx, wy, jit=0.9, sx=1.0, sy=0.38)
    e = d2 - d1
    bowl = -(d1 / 70.0) ** 2
    facet = 0.5 * rid + bowl * 0.5
    ridge = sstep(0, 10, e)
    hadze = facet * ridge + 0.1 * ridge
    # long cracks along grain
    crk = np.exp(-(noise(N, 65, 4, 18, hp=0.1) / 0.09) ** 2) * sstep(0.3, 1.2, noise(N, 66, 3, 3))
    h2 = h * 0.45 + hadze * 0.9 - 0.6 * crk
    a = a * (0.86 + 0.22 * sstep(0, 0.7, hadze - hadze.min())[..., None])
    a = a * (1 - 0.55 * crk[..., None])
    r = r + 0.1 * (1 - ridge) + 0.2 * crk
    save('pbr_wood_dark', a, normal_from_height(h2, 12.0), r)


if __name__ == '__main__':
    which = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['floor', 'pine', 'oak', 'dark']
    for w in which:
        globals()[w]()
