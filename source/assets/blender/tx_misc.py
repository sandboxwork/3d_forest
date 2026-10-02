"""plaster, fabrics, leather, iron, stone, rug, ceramic, wicker, copper, paper, book cloth, glass"""
import sys
sys.path.insert(0, '/shared/river/assets/blender')
from tx_lib import *

N = 512


def plaster():
    x, y = grid(N)
    mott = fbm(N, 101, 2.5, 5)
    # trowel strokes: two orientations chosen by low-freq mask
    s1 = noise(N, 102, 3, 22, hp=0.15, ang=0.35)
    s2 = noise(N, 103, 22, 3, hp=0.15, ang=-0.25)
    m = sstep(-1.2, 1.2, noise(N, 104, 2.0, 2.0))
    trowel = s1 * m + s2 * (1 - m)
    grain = noise(N, 105, 110, 110, hp=0.2)
    pits = sstep(2.6, 3.4, noise(N, 106, 170, 170))
    # hairline cracks
    wx = x + 16 * noise(N, 107, 5, 5) + 2.2 * noise(N, 108, 40, 40)
    wy = y + 16 * noise(N, 109, 5, 5) + 2.2 * noise(N, 110, 40, 40)
    d1, d2, rid, _, _ = vor(N, 3, 3, 111, wx, wy, jit=1.0)
    e = d2 - d1
    inter = sstep(-0.2, 0.7, noise(N, 112, 3, 3))
    crack = (1 - sstep(0.4, 2.6, e)) * inter
    h = 0.5 + 0.05 * trowel + 0.08 * mott + 0.10 * grain - 0.35 * pits - 0.6 * crack
    base = np.array([0.86, 0.815, 0.73], f32)
    warm = np.array([0.84, 0.76, 0.64], f32)
    t = sstep(-1.0, 1.0, mott)
    a = mix(base, warm, t * 0.6)
    a = a * (1 + 0.012 * trowel[..., None] + 0.02 * grain[..., None])
    a = a * (1 - 0.30 * pits[..., None]) * (1 - 0.35 * crack[..., None])
    rough = 0.9 + 0.04 * trowel + 0.03 * mott - 0.05 * crack
    save('pbr_plaster', a, normal_from_height(h, 14.0), rough)


def weave(nt, seed, pw=0.7, a_ov=0.3, gapthr=0.0, wob=0.0, slub=0.4, fibre=0.4, nty=None):
    """Plain weave. Returns h, tone (-1..1), topv (1 where warp thread on top), gapmask (1 in holes)"""
    x, y = grid(N)
    u = x / N * nt
    v = y / N * nt
    if wob:
        u = u + wob * noise(N, seed, 4, 10)
        v = v + wob * noise(N, seed + 1, 10, 4)
    iu = np.floor(u).astype(int) % nt
    iv = np.floor(v).astype(int) % nt
    fu = u - np.floor(u)
    fv = v - np.floor(v)
    par = (iu + iv) % 2
    r = np.random.default_rng(seed)
    ru = r.standard_normal(nt)
    rv = r.standard_normal(nt)

    def prof(f):
        p = np.sin(np.pi * f)
        if gapthr > 0:
            p = np.clip((p - gapthr) / (1 - gapthr), 0, 1)
        return p ** pw

    pu, pv = prof(fu), prof(fv)
    qv = (2 * fv - 1) ** 2
    qu = (2 * fu - 1) ** 2
    top = (par == 0)
    hv = pu * np.where(top, 1 - a_ov * qv, 0.4 + a_ov * qv)   # vertical thread (runs along y), cross-profile in u
    hh = pv * np.where(top, 0.4 + a_ov * qu, 1 - a_ov * qu)   # horizontal thread
    h = np.maximum(hv, hh)
    topv = (hv >= hh).astype(f32)
    # lengthwise slub / fibre
    sl_v = noise(N, seed + 2, nt * 0.3, 3)       # varies slowly along y? (x fast)
    sl_h = noise(N, seed + 3, 3, nt * 0.3)
    fb_v = noise(N, seed + 4, nt * 5, 6, hp=0.1)  # fibres run along y
    fb_h = noise(N, seed + 5, 6, nt * 5, hp=0.1)
    tone_v = 0.5 * ru[iu] + slub * sl_v + fibre * fb_v
    tone_h = 0.5 * rv[iv] + slub * sl_h + fibre * fb_h
    tone = np.where(topv > 0, tone_v, tone_h)
    fine = np.where(topv > 0, fb_v, fb_h)
    gap = np.clip(1 - h * 2.2, 0, 1)
    return h, tone, topv, gap, fine


def linen():
    h, tone, topv, gap, fine = weave(56, 201, pw=0.8, a_ov=0.32, slub=0.7, fibre=0.55, wob=0.12)
    base = np.array([0.80, 0.72, 0.59], f32)
    a = base * (1 + 0.075 * tone[..., None]) * (0.55 + 0.45 * np.clip(h * 1.4, 0, 1))[..., None] ** 0.6
    hh = h * 0.9 + 0.05 * fine
    save('pbr_fabric_linen', a, normal_from_height(hh, 7.0), 0.88 + 0.06 * tone * 0.5 - 0.1 * h * 0)


def burlap():
    h, tone, topv, gap, fine = weave(18, 301, pw=0.9, a_ov=0.35, gapthr=0.28, wob=0.12, slub=0.5, fibre=0.3)
    base = np.array([0.62, 0.47, 0.29], f32)
    a = base * (1 + 0.10 * tone[..., None]) * (0.3 + 0.7 * np.clip(h * 1.5, 0, 1))[..., None] ** 0.9
    hh = h + 0.08 * fine
    save('pbr_fabric_burlap', a, normal_from_height(hh, 8.0), 0.95 - 0.05 * h)


def wicker():
    h, tone, topv, gap, fine = weave(8, 701, pw=0.35, a_ov=0.38, gapthr=0.10, wob=0.12, slub=0.8, fibre=1.2)
    streak = noise(N, 702, 25, 25)
    base = np.array([0.68, 0.50, 0.29], f32)
    dark = np.array([0.42, 0.28, 0.14], f32)
    a = mix(base, dark, sstep(-0.6, 1.8, -tone * 0.5 + 0.2 * streak)) * (0.35 + 0.65 * np.clip(h * 1.5, 0, 1))[..., None] ** 0.8
    hh = h + 0.12 * fine
    save('pbr_wicker', a, normal_from_height(hh, 8.0), 0.72 + 0.08 * tone * 0.3 - 0.04 * h)


def wool():
    x, y = grid(N)
    cols, rows = 12, 15
    cw, ch = N / cols, N / rows
    U = x / cw
    V = y / ch
    H = np.zeros((N, N), f32)
    T = np.zeros((N, N), f32)   # along-strand coordinate for twist
    best = np.full((N, N), -1.0, f32)
    # two legs of V per stitch: from (0,1) to (0.5,0) and (1,1) to (0.5,0) in cell coords; v up in cell = -image row
    rad = 0.30
    for dv in (-1, 0, 1):
        for du in (-1, 0, 1):
            cu = np.floor(U) + du
            cv = np.floor(V) + dv
            lu = U - cu
            lv = V - cv
            for leg in (0, 1):
                p0 = np.array([0.0 if leg == 0 else 1.0, -0.05])
                p1 = np.array([0.5, 1.05])
                # image-space: V grows downward; V-shape opening up => leg tops at v=0, bottoms at v=1
                dxy = np.stack([lu - p0[0], lv - p0[1]], -1)
                seg = p1 - p0
                tt = np.clip((dxy @ seg) / (seg @ seg), 0, 1)
                px = p0[0] + tt * seg[0]
                py = p0[1] + tt * seg[1]
                dd = np.sqrt(((lu - px) * 1.0) ** 2 + ((lv - py) * 0.8) ** 2)
                hh = np.sqrt(np.clip(1 - (dd / rad) ** 2, 0, 1))
                # later rows (dv) overlap: small depth bias by cell row so layering is consistent
                hh = hh * (1 - 0.18 * (dv + 1) / 2 * 0) + 0.0
                sign = (lu - px) if leg == 0 else -(lu - px)
                tw = np.sin(2 * np.pi * (tt * 3.0 + (lu - px) * 2.2 * (1 if leg == 0 else -1)))
                better = hh > best
                best = np.where(better, hh, best)
                H = np.where(better, hh + 0.12 * tw * hh, H)
                T = np.where(better, tt, T)
    fuzz = noise(N, 401, 70, 70, hp=0.2)
    fuzz2 = noise(N, 402, 40, 40)
    h = H ** 1.3 + 0.035 * fuzz * (0.4 + H)
    base = np.array([0.80, 0.74, 0.64], f32)
    heather = noise(N, 403, 60, 60)
    a = base * (1 + 0.06 * fuzz2[..., None] + 0.05 * heather[..., None]) * (0.18 + 0.82 * np.clip(H * 1.1, 0, 1) ** 1.3)[..., None] ** 0.8
    save('pbr_fabric_wool', a, normal_from_height(h, 9.0), 0.95 - 0.05 * H)


def leather():
    x, y = grid(N)
    wx = x + 3 * noise(N, 501, 40, 40)
    wy = y + 3 * noise(N, 502, 40, 40)
    d1, d2, rid, _, _ = vor(N, 46, 46, 503, wx, wy, jit=0.95)
    e = d2 - d1
    cell = sstep(0, 5.0, e)
    net = 1 - sstep(0.4, 3.0, e)
    n1 = noise(N, 504, 2.6, 4.5, ang=0.6)
    n2 = noise(N, 505, 5, 12, ang=-0.4)
    cr1 = 0.8 * np.exp(-(n1 / 0.16) ** 2)
    cr2 = np.exp(-(n2 / 0.12) ** 2) * sstep(0.0, 1.0, noise(N, 506, 3, 3))
    crease = np.maximum(cr1, 0.7 * cr2)
    pores = sstep(2.5, 3.2, noise(N, 507, 190, 190))
    wear = sstep(-0.2, 1.3, fbm(N, 508, 2.2, 4))
    h = 0.4 + 0.5 * cell - 0.35 * crease - 0.25 * pores + 0.1 * fbm(N, 509, 6, 3) * 0.3
    dark = np.array([0.22, 0.12, 0.065], f32)
    mid = np.array([0.40, 0.235, 0.125], f32)
    worn = np.array([0.52, 0.35, 0.21], f32)
    a = mix(dark, mid, 0.55 + 0.25 * rid)
    a = mix(a, worn, wear * 0.35 * (0.5 + 0.5 * cell))
    a = a * (1 - 0.3 * crease[..., None]) * (1 - 0.45 * net[..., None]) * (1 - 0.3 * pores[..., None])
    rough = 0.52 + 0.28 * wear + 0.15 * net + 0.1 * crease
    save('pbr_leather', a, normal_from_height(h, 11.0), rough)


def iron():
    x, y = grid(N)
    cast = noise(N, 601, 130, 130, hp=0.1)
    mid = fbm(N, 602, 6, 4)
    low = fbm(N, 603, 2.5, 4)
    d1, d2, rid, _, _ = vor(N, 44, 44, 604, jit=1.0)
    pit = (rid > 0.55) * (1 - sstep(0, 1.2 + 3.5 * rid, d1))
    d1b, d2b, ridb, _, _ = vor(N, 9, 9, 605, jit=1.0)
    bigpit = (ridb > 0.8) * (1 - sstep(0, 2.5 + 7 * ridb, d1b))
    rust = sstep(0.8, 1.6, low + 0.5 * mid) * sstep(0.2, 1.4, noise(N, 606, 45, 45))
    h = 0.5 + 0.40 * cast + 0.18 * mid + 0.05 * low - 0.8 * pit - 0.7 * bigpit
    base = np.array([0.24, 0.24, 0.25], f32)
    a = base * (1 + 0.14 * mid[..., None] + 0.16 * cast[..., None] + 0.10 * low[..., None])
    a = mix(a, [0.33, 0.17, 0.09], rust * 0.5) * (1 - 0.55 * (pit + bigpit).clip(0, 1)[..., None])
    rough = 0.58 + 0.12 * mid + 0.08 * cast + 0.25 * (pit + bigpit).clip(0, 1) + 0.15 * rust
    save('pbr_iron', a, normal_from_height(h, 10.0), rough)


def brass():
    x, y = grid(N)
    brush = noise(N, 801, 6, 330, hp=0.04)
    brush2 = noise(N, 802, 14, 140, hp=0.05)
    low = fbm(N, 803, 2.5, 4)
    dent = fbm(N, 804, 4, 3)
    tarn = sstep(0.2, 1.5, fbm(N, 805, 3.5, 4) + 0.3 * noise(N, 806, 40, 40))
    mixc = 0.25 + 0.5 * sstep(-1.5, 1.5, low)
    cu = np.array([0.80, 0.52, 0.34], f32)
    br = np.array([0.80, 0.60, 0.32], f32)
    a = mix(cu, br, mixc)
    a = a * (1 + 0.06 * brush[..., None] + 0.04 * brush2[..., None])
    a = mix(a, [0.45, 0.30, 0.18], tarn * 0.4)
    h = 0.5 + 0.12 * brush + 0.08 * brush2 + 0.15 * dent
    rough = 0.40 + 0.05 * brush + 0.03 * brush2 + 0.12 * tarn + 0.03 * low
    save('pbr_brass_copper', a, normal_from_height(h, 4.0), rough)


def stone():
    x, y = grid(N)
    wx = x + 12 * noise(N, 901, 5, 5) + 2 * noise(N, 902, 40, 40)
    wy = y + 12 * noise(N, 903, 5, 5) + 2 * noise(N, 904, 40, 40)
    d1, d2, rid, cx, cy = vor(N, 5, 4, 905, wx, wy, jit=0.85, sx=1.0, sy=1.25)
    e = d2 - d1
    thr = 11 + 3 * noise(N, 906, 14, 14)
    mort = 1 - sstep(thr - 2, thr + 3, e)
    surf = sstep(thr, thr + 18, e)
    rough_s = fbm(N, 907, 10, 5)
    chip = noise(N, 908, 60, 60)
    tilt = ((x - cx + N / 2) % N - N / 2) * (rid - 0.5) * 0.004
    h = 0.15 + 0.55 * surf ** 0.7 + 0.14 * rough_s * surf + 0.05 * chip * surf + tilt * surf - 0.1 * mort
    h = h + 0.05 * noise(N, 909, 120, 120) * mort
    pal = np.array([[0.46, 0.44, 0.41], [0.48, 0.42, 0.35], [0.52, 0.47, 0.38], [0.36, 0.34, 0.33], [0.42, 0.40, 0.37]], f32)
    idx = np.minimum((rid * len(pal)).astype(int), len(pal) - 1)
    col = pal[idx]
    col = col * (1 + 0.12 * rough_s[..., None] + 0.05 * chip[..., None])
    soot = sstep(-0.3, 1.4, fbm(N, 910, 2.5, 4)) * 0.45
    col = col * (1 - soot[..., None] * 0.7)
    mc = np.array([0.66, 0.62, 0.54], f32) * (1 + 0.10 * noise(N, 911, 150, 150)[..., None]) * (1 - 0.4 * soot[..., None])
    a = np.where(mort[..., None] > 0.5, mc, col)
    a = mix(a, mc * 0.6 * 0 + a, 0)  # no-op, keep clarity
    ao = 0.65 + 0.35 * sstep(0, 22, e)
    a = a * ao[..., None]
    save('pbr_stone_fireplace', a, normal_from_height(h, 9.0), 0.88 + 0.1 * rough_s * 0.5 - 0.0 * soot)


def rug():
    x, y = grid(N)
    rows, K = 4, 8
    Hh = N // rows
    row = np.floor(y / Hh).astype(int)
    b = (y - row * Hh) / Hh * 2 - 1
    ab = np.abs(b)
    phase = x / (N / K) - 0.42 * ab + 0.5 * (row % 2)
    phase = phase + 0.05 * noise(N, 1001, 8, 8)
    tl = phase - np.floor(phase)
    lid = np.floor(phase).astype(int) % K
    r = np.random.default_rng(1002)
    pal = np.array([[0.74, 0.67, 0.54], [0.50, 0.26, 0.20], [0.26, 0.30, 0.38], [0.60, 0.47, 0.24],
                    [0.40, 0.40, 0.28], [0.34, 0.26, 0.19], [0.66, 0.59, 0.47]], f32)
    choose = r.integers(0, len(pal), size=(rows, K, 2))
    side = (b > 0).astype(int)
    ci = choose[row, lid, side]
    col = pal[ci] * (0.9 + 0.2 * r.random(size=(rows, K, 2))[row, lid, side])[..., None]
    prof_b = np.sqrt(np.clip(1 - ab ** 2.2, 0, 1))
    lobe = np.sin(np.pi * tl) ** 0.55
    twist = np.sin(2 * np.pi * (tl * 2.0 + b * 1.3 + 3 * ab)) * 0.5 + 0.5
    fib = noise(N, 1003, 90, 90, hp=0.15)
    fib2 = noise(N, 1004, 14, 60, hp=0.05, ang=0.5)
    h = prof_b * (0.3 + 0.7 * lobe) + 0.05 * twist * prof_b + 0.06 * fib + 0.04 * fib2
    sh = (0.25 + 0.75 * np.clip(prof_b * (0.35 + 0.65 * lobe) * 1.6, 0, 1))
    a = col * sh[..., None] ** 0.8 * (1 + 0.1 * fib2[..., None] + 0.05 * (twist - 0.5)[..., None])
    save('pbr_rug_braided', a, normal_from_height(h, 7.0), 0.93 - 0.05 * fib * 0.3)


def ceramic():
    x, y = grid(N)
    wx = x + 5 * noise(N, 1101, 12, 12)
    wy = y + 5 * noise(N, 1102, 12, 12)
    d1, d2, rid, _, _ = vor(N, 22, 22, 1103, wx, wy, jit=1.0)
    e = d2 - d1
    inter = sstep(-0.9, 0.5, noise(N, 1104, 4, 4))
    craze = (1 - sstep(0.3, 1.6, e)) * (0.35 + 0.65 * (rid > 0.25)) * inter
    pool = fbm(N, 1105, 3, 4)
    peel = noise(N, 1106, 90, 90, hp=0.1)
    speck = sstep(2.9, 3.5, noise(N, 1107, 200, 200))
    base = np.array([0.90, 0.88, 0.82], f32)
    a = base * (1 + 0.012 * pool[..., None])
    a = mix(a, [0.60, 0.55, 0.45], craze * 0.55)
    a = a * (1 - 0.45 * speck[..., None])
    h = 0.5 + 0.06 * peel + 0.02 * pool - 0.5 * craze
    rough = 0.20 + 0.04 * pool + 0.03 * peel + 0.3 * craze
    save('pbr_ceramic', a, normal_from_height(h, 3.0), rough, size=256)


def paper():
    fibres = 0
    for i, ang in enumerate((0.1, 0.9, 1.7, 2.5)):
        fibres = fibres + noise(N, 1201 + i, 130, 6, hp=0.1, ang=ang)
    fibres /= 2
    mott = fbm(N, 1210, 3, 5)
    fox = sstep(1.9, 3.0, noise(N, 1211, 28, 28)) * sstep(-0.2, 0.8, fbm(N, 1212, 2, 3))
    grain = noise(N, 1213, 120, 120, hp=0.2)
    base = np.array([0.89, 0.83, 0.68], f32)
    a = base * (1 + 0.035 * mott[..., None] + 0.03 * fibres[..., None])
    a = mix(a, [0.62, 0.45, 0.25], fox * 0.55)
    a = a * (1 - 0.06 * sstep(0.5, 2.0, mott)[..., None])
    h = 0.5 + 0.12 * fibres + 0.06 * grain + 0.07 * mott
    save('pbr_paper', a, normal_from_height(h, 2.5), 0.86 + 0.04 * fibres * 0.3, size=256)


def book_cloth():
    h, tone, topv, gap, fine = weave(44, 1301, pw=0.8, a_ov=0.3, slub=0.3, fibre=0.35)
    x, y = grid(N)
    L = 4
    l1 = np.abs(np.mod(L * (x + y) / N, 1) - 0.5)
    l2 = np.abs(np.mod(L * (x - y) / N, 1) - 0.5)
    ln = np.minimum(l1, l2)
    line = 1 - sstep(0.0, 0.085, ln)
    dot = 1 - sstep(0.02, 0.1, np.sqrt((np.mod(L * x / N * 2, 1) - 0.5) ** 2 + (np.mod(L * y / N * 2, 1) - 0.5) ** 2))
    emb = np.clip(line + 0.0 * dot, 0, 1)
    hh = 0.55 * h + 0.9 * emb * 0.5 + 0.35 * dot
    base = np.array([0.50, 0.30, 0.25], f32)
    a = base * (1 + 0.07 * tone[..., None]) * (0.75 + 0.25 * np.clip(h * 1.4, 0, 1))[..., None]
    a = a * (1 + 0.12 * emb[..., None] - 0.0)
    save('pbr_book_cloth', a, normal_from_height(hh, 6.0), 0.82 - 0.12 * emb, size=512)


def glass():
    sm = fbm(N, 1401, 3, 5)
    streak = noise(N, 1402, 3, 40, hp=0.05, ang=0.3)
    fing = sstep(0.2, 1.6, fbm(N, 1403, 5, 4) + 0.3 * streak)
    dust = sstep(2.4, 3.4, noise(N, 1404, 160, 160))
    a = np.ones((N, N, 3), f32) * (0.93 - 0.06 * fing[..., None] - 0.05 * dust[..., None]) * np.array([1, 1, 0.97], f32)
    rough = 0.06 + 0.32 * fing + 0.25 * dust + 0.05 * sstep(0, 2, streak)
    h = 0.5 + 0.02 * sm + 0.05 * fing
    save('pbr_glass_dirty', a, normal_from_height(h, 1.5), rough, size=256)


if __name__ == '__main__':
    which = sys.argv[sys.argv.index('--') + 1:]
    for w in which:
        globals()[w]()
