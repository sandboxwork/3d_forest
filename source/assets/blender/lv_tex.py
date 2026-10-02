"""Procedural textures for the living zone (numpy only; saved through bpy images as JPEG).
   Outputs: /shared/river/assets/tex/lv_painting_<n>.jpg (max side 512), lv_page_text.jpg, lv_news.jpg"""
import numpy as np, os, math
OUT = '/shared/river/assets/tex'

# n: (kind, canvas_w_m, canvas_h_m)
PAINT_SPEC = {1: ('lake', 0.80, 0.50), 2: ('flowers', 0.25, 0.35), 3: ('night', 0.26, 0.34), 4: ('forest', 0.76, 0.54),
              5: ('sea', 0.62, 0.40), 6: ('still', 0.34, 0.48), 7: ('cottage', 0.24, 0.24), 8: ('winter', 0.30, 0.40)}


def fnoise(h, w, cut_y, cut_x, seed=0):
    r = np.random.default_rng(seed)
    a = r.standard_normal((h, w))
    F = np.fft.fft2(a)
    fy = np.fft.fftfreq(h)[:, None] * h
    fx = np.fft.fftfreq(w)[None, :] * w
    F *= np.exp(-((fx / max(cut_x, 1e-3)) ** 2 + (fy / max(cut_y, 1e-3)) ** 2))
    a = np.real(np.fft.ifft2(F))
    return (a - a.mean()) / (a.std() + 1e-9)


def fbm(h, w, base, seed, o=4, aniso=1.0):
    t = 0
    amp = 1.0
    for k in range(o):
        t = t + amp * fnoise(h, w, base * (2 ** k), base * (2 ** k) * aniso, seed + k)
        amp *= 0.55
    return t / 1.6


def save(name, rgb):
    import bpy
    rgb = np.clip(rgb, 0, 1)
    h, w = rgb.shape[:2]
    img = bpy.data.images.new(name, w, h, alpha=False)
    a = np.ones((h, w, 4), dtype=np.float32)
    a[..., :3] = rgb[::-1]
    img.pixels.foreach_set(a.ravel())
    img.file_format = 'JPEG'
    sc = bpy.context.scene
    sc.render.image_settings.file_format = 'JPEG'
    sc.render.image_settings.quality = 90
    img.filepath_raw = os.path.join(OUT, name + '.jpg')
    img.save()
    bpy.data.images.remove(img)


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])


class Canvas:
    def __init__(s, w, h, seed=0):
        s.w, s.h = w, h
        s.img = np.zeros((h, w, 3))
        s.Y, s.X = np.mgrid[0:h, 0:w].astype(np.float64)
        s.u = s.X / w; s.v = s.Y / h
        s.seed = seed
        s.rng = np.random.default_rng(seed)

    def grad(s, y0, y1, c0, c1, ex=1.0):
        t = np.clip((s.v - y0) / (y1 - y0), 0, 1) ** ex
        m = (s.v >= y0) & (s.v <= y1)
        col = hexc(c0)[None, None] * (1 - t[..., None]) + hexc(c1)[None, None] * t[..., None]
        s.img = np.where(m[..., None], col, s.img)

    def mask(s, m, col, a=1.0, noise=0.0):
        c = hexc(col) if isinstance(col, str) else np.asarray(col)
        if noise:
            c = c[None, None] * (1 + noise * fnoise(s.h, s.w, 40, 6, int(s.rng.integers(1e6)))[..., None] * 0.25)
        else:
            c = c[None, None]
        mm = (np.clip(m, 0, 1) * a)[..., None]
        s.img = s.img * (1 - mm) + c * mm

    def ell(s, cx, cy, rx, ry, soft=0.01):
        d = np.sqrt(((s.u - cx) / rx) ** 2 + ((s.v - cy) / ry) ** 2)
        return np.clip((1 - d) / (soft / min(rx, ry) + 1e-6), 0, 1)

    def poly(s, pts, soft=0.002):
        # even-odd test vectorised
        px = [p[0] for p in pts]; py = [p[1] for p in pts]
        inside = np.zeros((s.h, s.w), bool)
        n = len(pts)
        for i in range(n):
            x1, y1, x2, y2 = px[i], py[i], px[(i + 1) % n], py[(i + 1) % n]
            cond = ((y1 > s.v) != (y2 > s.v)) & (s.u < (x2 - x1) * (s.v - y1) / (y2 - y1 + 1e-12) + x1)
            inside ^= cond
        m = inside.astype(np.float64)
        k = max(1, int(soft * s.w))
        if k > 1:
            ker = np.ones(k) / k
            m = np.apply_along_axis(lambda r: np.convolve(r, ker, 'same'), 1, m)
        return m

    def ridge(s, base_y, amp, freq, seed, o=4):
        n = fbm(1, s.w * 2, freq, seed, o)[0][:s.w] if False else None
        r = np.random.default_rng(seed)
        x = np.linspace(0, 1, s.w)
        y = np.zeros(s.w)
        a = 1.0
        for k in range(o):
            ph = r.uniform(0, 6.28, 3)
            y += a * (np.sin(x * freq * 2 ** k * 6.28 + ph[0]) * 0.6 + np.sin(x * freq * 2.7 * 2 ** k * 6.28 + ph[1]) * 0.4)
            a *= 0.5
        return base_y - amp * y

    def below(s, ycurve):
        return (s.v > ycurve[None, :]).astype(np.float64)

    def paint_finish(s):
        im = s.img
        # brush strokes: low-freq colour mottling + stroke noise along both directions, canvas weave
        m1 = fbm(s.h, s.w, 6, s.seed + 100, 3)
        st = fnoise(s.h, s.w, 90, 6, s.seed + 101) * 0.5 + fnoise(s.h, s.w, 8, 70, s.seed + 102) * 0.5
        im = im * (1 + 0.05 * m1[..., None]) * (1 + 0.045 * st[..., None])
        weave = 0.5 + 0.5 * np.sin(s.X * 2.2) * np.sin(s.Y * 2.2)
        im = im * (1 - 0.05 * weave[..., None])
        vig = 1 - 0.28 * (((s.u - 0.5) ** 2 + (s.v - 0.5) ** 2) * 2)
        im = im * vig[..., None]
        # varnish warmth
        im = im * np.array([1.04, 1.0, 0.92])[None, None]
        return np.clip(im, 0, 1)


def trees(c, n, y0, hmin, hmax, col, seed, wob=0.01):
    r = np.random.default_rng(seed)
    for i in range(n):
        x = r.uniform(0.02, 0.98); h = r.uniform(hmin, hmax); w = h * r.uniform(0.18, 0.3)
        pts = [(x, y0 - h)]
        for k in range(1, 7):
            t = k / 6
            pts.append((x + w * t * (1 + 0.2 * r.uniform(-1, 1)), y0 - h * (1 - t) ** 0.9 + 0.0 + h * 0.0 - 0.0 + (0.0 if k % 2 else 0.01 * h)))
            pts.append((x + w * t * 0.55, y0 - h * (1 - t) ** 0.9 - h * 0.05))
        pts.append((x + 0.002, y0))
        pts.append((x - 0.002, y0))
        for k in range(6, 0, -1):
            t = k / 6
            pts.append((x - w * t * 0.55, y0 - h * (1 - t) ** 0.9 - h * 0.05))
            pts.append((x - w * t * (1 + 0.2 * r.uniform(-1, 1)), y0 - h * (1 - t) ** 0.9))
        c.mask(c.poly(pts, 0.0015), col, 1.0, 0.3)


def p_lake(c):
    c.grad(0, 0.55, '#f0b070', '#6a86b8', 0.9) if False else None
    c.grad(0, 0.5, '#4f6fae', '#f4b87c', 1.4)
    cl = fbm(c.h, c.w, 5, 11, 4, aniso=2.5)
    c.mask(np.clip((cl - 0.1) * 2.0, 0, 1) * (1 - c.v * 1.2).clip(0, 1), '#f7d7b0', 0.7)
    c.mask(np.clip((fbm(c.h, c.w, 4, 17, 3, 3) - 0.3) * 2, 0, 1) * (c.v < 0.4), '#d98f78', 0.5)
    c.mask(c.ell(0.72, 0.42, 0.13, 0.16, 0.08), '#ffe2b0', 0.6)
    for k, (yb, am, fr, col) in enumerate([(0.44, 0.07, 1.3, '#7b7fa6'), (0.5, 0.06, 1.8, '#5d6b86'), (0.56, 0.04, 2.5, '#3d5463')]):
        rd = c.ridge(yb, am, fr, 30 + k)
        c.mask(c.below(rd) * (c.v < 0.68), col, 1.0, 0.25)
    # lake
    c.grad(0.6, 1.0, '#d6a67c', '#27404a', 0.8)
    sky_ref = np.clip(1 - np.abs(c.u - 0.72) * 3.0, 0, 1) * (c.v > 0.6)
    ripple = 0.5 + 0.5 * np.sin(c.Y * 0.7 + fnoise(c.h, c.w, 30, 4, 5) * 3)
    c.mask(sky_ref * ripple * 0.7, '#ffe0a8', 0.8)
    # shore + trees
    rd = c.ridge(0.66, 0.025, 2.2, 41)
    m = c.below(rd) * (c.v < 0.74)
    c.mask(m, '#26372b', 1.0, 0.35)
    trees(c, 14, 0.7, 0.07, 0.17, '#1c2b22', 7)
    trees(c, 6, 0.99, 0.28, 0.45, '#0f1a15', 9)
    c.mask(c.below(c.ridge(0.9, 0.04, 1.5, 55)) * (c.v > 0.86), '#1d2a1b', 1.0, 0.3)


def p_sea(c):
    c.grad(0, 0.45, '#8aa6c8', '#f2d2a2', 1.2)
    c.mask(np.clip((fbm(c.h, c.w, 6, 3, 3, 2.5) - 0.2) * 2, 0, 1) * (c.v < 0.4), '#f5ece0', 0.7)
    c.mask(c.ell(0.3, 0.42, 0.15, 0.1, 0.1), '#fff1cf', 0.7)
    c.grad(0.45, 1.0, '#6fa0b0', '#1e4458', 0.9)
    for k in range(26):
        y = 0.47 + (k / 26) ** 1.6 * 0.52
        amp = 0.004 + 0.02 * (k / 26)
        wave = np.sin(c.u * (30 - k * 0.6) + k * 1.7 + fnoise(c.h, c.w, 20, 8, k) * 0.6) * amp
        band = np.exp(-((c.v - y - wave) / (0.004 + 0.004 * k / 26)) ** 2)
        c.mask(band * 0.55, '#d8ecee' if k % 3 else '#fff6e0', 0.6)
    refl = np.exp(-((c.u - 0.3) / 0.05) ** 2) * (c.v > 0.46) * (0.5 + 0.5 * np.sin(c.Y * 0.5 + fnoise(c.h, c.w, 40, 5, 9) * 2))
    c.mask(refl, '#ffe8b8', 0.65)
    # sailboat
    hx, hy = 0.7, 0.58
    c.mask(c.poly([(hx - 0.1, hy), (hx + 0.12, hy), (hx + 0.08, hy + 0.03), (hx - 0.07, hy + 0.03)], 0.002), '#3a2c24')
    c.mask(c.poly([(hx, hy - 0.02), (hx, hy - 0.26), (hx + 0.1, hy - 0.04)], 0.002), '#f3ead8')
    c.mask(c.poly([(hx - 0.01, hy - 0.02), (hx - 0.01, hy - 0.2), (hx - 0.09, hy - 0.04)], 0.002), '#e5d3b4')


def p_night(c):
    c.grad(0, 0.75, '#0c1230', '#2d4375', 1.2)
    r = c.rng
    for i in range(160):
        x, y = r.uniform(0, 1), r.uniform(0, 0.6)
        c.mask(c.ell(x, y, 0.004, 0.003, 0.004), '#fff4d0', r.uniform(0.4, 1.0))
    halo = np.exp(-(((c.u - 0.7) ** 2 + (c.v - 0.2) ** 2) / 0.012))
    c.mask(halo * 0.5, '#8ea4d8', 0.6)
    c.mask(c.ell(0.7, 0.2, 0.065, 0.048, 0.03), '#f4f0da')
    c.mask(c.ell(0.68, 0.19, 0.012, 0.009, 0.01), '#cbc8b8', 0.6)
    c.mask(c.below(c.ridge(0.78, 0.04, 1.2, 4)), '#101a2a', 1.0, 0.3)
    c.mask(c.below(c.ridge(0.88, 0.03, 1.6, 7)), '#060a12', 1.0, 0.3)
    # cabin with lit window
    c.mask(c.poly([(0.22, 0.86), (0.22, 0.74), (0.3, 0.68), (0.38, 0.74), (0.38, 0.86)], 0.002), '#1c1f28')
    c.mask(c.poly([(0.27, 0.84), (0.27, 0.77), (0.33, 0.77), (0.33, 0.84)], 0.002), '#ffcf70')
    c.mask(np.exp(-(((c.u - 0.3) ** 2 + (c.v - 0.81) ** 2) / 0.003)) * 0.4, '#ffb050', 0.5)
    trees(c, 10, 0.95, 0.15, 0.32, '#050a0d', 12)


def p_flowers(c):
    c.grad(0, 1, '#d8c9a4', '#a98e66', 1.0)
    c.mask(c.poly([(0, 0.78), (1, 0.74), (1, 1), (0, 1)], 0.003), '#6b4a32', 1.0, 0.3)
    # vase
    c.mask(c.poly([(0.36, 0.78), (0.33, 0.66), (0.4, 0.56), (0.42, 0.5), (0.58, 0.5), (0.6, 0.56), (0.67, 0.66), (0.64, 0.78)], 0.004), '#3e6a8c', 1.0, 0.3)
    c.mask(c.ell(0.43, 0.64, 0.04, 0.07, 0.03), '#8cb6d6', 0.4)
    r = c.rng
    cols = ['#c8403a', '#e8b238', '#f0e6d6', '#b05a9a', '#e07a38', '#d9d46a']
    for i in range(60):
        a = r.uniform(0, 6.28); d = r.uniform(0.0, 0.3)
        x = 0.5 + math.cos(a) * d * 0.9; y = 0.38 - abs(math.sin(a)) * d * 0.8 + 0.05
        cc = cols[int(r.integers(len(cols)))]
        rad = r.uniform(0.035, 0.07)
        c.mask(c.ell(x, y, rad, rad * 1.1, 0.02), cc, 1.0, 0.2)
        c.mask(c.ell(x, y, rad * 0.4, rad * 0.4, 0.02), '#7a4a1a', 0.6)
    for i in range(14):
        x = r.uniform(0.25, 0.75); y = r.uniform(0.3, 0.55)
        c.mask(c.ell(x, y, 0.05, 0.02, 0.01), '#4c7a3a', 0.8)


def p_forest(c):
    c.grad(0, 0.6, '#c8d4c6', '#e8d9a8', 1.0)
    c.mask(fbm(c.h, c.w, 7, 5, 3) > 0.2, '#e8e0c0', 0.3)
    for k, (col, yb) in enumerate([('#8c7a4a', 0.5), ('#a8642c', 0.55), ('#b88a30', 0.6)]):
        rd = c.ridge(yb, 0.04, 2.5 + k, 20 + k)
        c.mask(c.below(rd) * (c.v < 0.7), col, 1.0, 0.45)
    # river
    c.grad(0.7, 1.0, '#8ba2a6', '#3a5560', 0.8)
    c.mask(np.exp(-((c.u - 0.5) ** 2) / 0.3) * (c.v > 0.68) * (0.5 + 0.5 * np.sin(c.Y * 0.6 + fnoise(c.h, c.w, 30, 4, 3) * 2)) * 0.5, '#f0e6c8', 0.6)
    r = c.rng
    # trunks and leaf dabs
    for i in range(18):
        x = r.uniform(0, 1); w = r.uniform(0.006, 0.02) * (1.6 if i % 3 == 0 else 1)
        c.mask(((np.abs(c.u - x) < w) & (c.v < 0.75)).astype(float), '#4a3a2a' if i % 2 else '#6b5a44', 0.9, 0.3)
    for i in range(380):
        x, y = r.uniform(0, 1), r.uniform(0, 0.55)
        cc = ['#c8501c', '#e0a030', '#9a3a1c', '#d8c050', '#7a8a2c'][int(r.integers(5))]
        c.mask(c.ell(x, y, 0.02, 0.014, 0.01), cc, r.uniform(0.5, 0.9), 0.2)
    c.mask(c.below(c.ridge(0.95, 0.02, 2, 31)) * (c.v > 0.9), '#2a3a24', 1.0, 0.3)


def p_still(c):
    c.grad(0, 1, '#241a14', '#3a2a1c', 1.0)
    c.mask(np.exp(-(((c.u - 0.4) ** 2 + (c.v - 0.4) ** 2) / 0.1)) * 0.5, '#9a7a4a', 0.5)
    c.mask(c.poly([(0, 0.74), (1, 0.7), (1, 1), (0, 1)], 0.003), '#4a3322', 1.0, 0.3)
    c.mask(c.ell(0.5, 0.74, 0.5, 0.012, 0.01), '#a88a60', 0.4)
    # jug
    c.mask(c.poly([(0.55, 0.76), (0.52, 0.62), (0.58, 0.5), (0.6, 0.44), (0.72, 0.44), (0.74, 0.5), (0.8, 0.62), (0.78, 0.76)], 0.004), '#5a8aa0', 1.0, 0.3)
    c.mask(c.ell(0.62, 0.6, 0.04, 0.08, 0.03), '#a8d2e0', 0.35)
    for (x, y, rd, cc) in ((0.28, 0.72, 0.09, '#b8302a'), (0.18, 0.74, 0.075, '#c8a030'), (0.38, 0.75, 0.07, '#8a2a20')):
        c.mask(c.ell(x, y, rd, rd, 0.03), cc, 1.0, 0.3)
        c.mask(c.ell(x - rd * 0.3, y - rd * 0.3, rd * 0.35, rd * 0.3, 0.03), '#f0d0a0', 0.4)
    c.mask(c.ell(0.67, 0.37, 0.14, 0.1, 0.05), '#6b8a3a', 0.9, 0.3)
    for i in range(8):
        x = 0.58 + i * 0.03
        c.mask(c.ell(x, 0.34 + 0.02 * (i % 3), 0.03, 0.03, 0.02), ['#e8d8b0', '#c8503a'][i % 2], 0.9)


def p_cottage(c):
    c.grad(0, 0.55, '#a8c8e8', '#f4ead0', 1.0)
    c.mask(np.clip(fbm(c.h, c.w, 5, 4, 3, 2) - 0.2, 0, 1) * 1.5 * (c.v < 0.4), '#ffffff', 0.7)
    c.mask(c.below(c.ridge(0.55, 0.05, 1.5, 3)), '#7fa05a', 1.0, 0.3)
    c.mask(c.below(c.ridge(0.7, 0.03, 2.0, 5)), '#5f8a44', 1.0, 0.3)
    c.mask(c.poly([(0.3, 0.74), (0.3, 0.5), (0.7, 0.5), (0.7, 0.74)], 0.002), '#e0d0b0')
    c.mask(c.poly([(0.26, 0.52), (0.5, 0.3), (0.74, 0.52)], 0.002), '#8c4a34', 1.0, 0.3)
    c.mask(c.poly([(0.44, 0.74), (0.44, 0.6), (0.56, 0.6), (0.56, 0.74)], 0.002), '#5a3a28')
    c.mask(c.poly([(0.34, 0.62), (0.34, 0.54), (0.4, 0.54), (0.4, 0.62)], 0.002), '#3a5a7a')
    c.mask(c.poly([(0.6, 0.62), (0.6, 0.54), (0.66, 0.54), (0.66, 0.62)], 0.002), '#3a5a7a')
    c.mask(c.poly([(0.46, 0.74), (0.54, 0.74), (0.7, 1), (0.3, 1)], 0.003), '#d8c090', 1.0, 0.3)
    r = c.rng
    for i in range(160):
        x, y = r.uniform(0, 1), r.uniform(0.72, 1.0)
        if abs(x - 0.5) < (y - 0.72) * 0.7 + 0.04:
            continue
        c.mask(c.ell(x, y, 0.012, 0.012, 0.005), ['#e85a8a', '#f0d040', '#ffffff', '#a070d0'][int(r.integers(4))], 0.9)


def p_winter(c):
    c.grad(0, 0.6, '#9fb0c4', '#e2e6ea', 1.0)
    c.mask(c.below(c.ridge(0.5, 0.05, 1.4, 8)), '#c8d0da', 1.0, 0.25)
    c.mask(c.below(c.ridge(0.62, 0.03, 2.2, 9)), '#eef0f2', 1.0, 0.2)
    trees(c, 12, 0.72, 0.1, 0.24, '#2c3c38', 21)
    c.mask(c.below(c.ridge(0.72, 0.02, 1.7, 10)), '#f4f6f8', 1.0, 0.15)
    c.grad(0.8, 1.0, '#e6eaee', '#b8c4d2', 1.0)
    trees(c, 5, 1.0, 0.35, 0.55, '#1e2a2a', 29)
    c.mask(c.poly([(0.62, 0.85), (0.62, 0.7), (0.78, 0.7), (0.78, 0.85)], 0.002), '#6a4a34')
    c.mask(c.poly([(0.6, 0.71), (0.7, 0.6), (0.8, 0.71)], 0.002), '#f6f8fa')
    c.mask(c.poly([(0.66, 0.84), (0.66, 0.76), (0.7, 0.76), (0.7, 0.84)], 0.002), '#ffd070')


PAINTERS = {'lake': p_lake, 'sea': p_sea, 'night': p_night, 'flowers': p_flowers, 'forest': p_forest, 'still': p_still, 'cottage': p_cottage, 'winter': p_winter}


def make_paintings():
    for n, (kind, w, h) in PAINT_SPEC.items():
        if w >= h:
            W, H = 512, int(round(512 * h / w))
        else:
            H, W = 512, int(round(512 * w / h))
        c = Canvas(W, H, seed=n * 7)
        PAINTERS[kind](c)
        save('lv_painting_%d' % n, c.paint_finish())
        print('painting', n, kind, W, H)


def text_block(c, x0, x1, y0, y1, lh, seed, ink=(0.12, 0.1, 0.09), indent=True, dens=1.0):
    r = np.random.default_rng(seed)
    y = y0
    first = True
    while y < y1 - lh:
        x = x0 + (lh * 1.4 if (first and indent) else 0)
        end = x1 - (r.uniform(0, 0.25) * (x1 - x0) if r.random() < 0.12 else 0)
        while x < end - 4:
            wl = int(r.integers(2, 9))
            for k in range(wl):
                cw = r.uniform(0.35, 0.7) * lh * 0.45 + 1
                kind = r.random()
                top = 0.0 if kind > 0.78 else 0.28
                bot = 0.72 if kind < 0.9 else 1.0
                ya = int(y + top * lh); yb = int(y + bot * lh)
                xa = int(x); xb = int(x + cw)
                if xb >= end:
                    break
                c[ya:yb + 1, xa:xb + 1] = c[ya:yb + 1, xa:xb + 1] * 0.25 + np.array(ink) * 0.75 * dens + c[ya:yb + 1, xa:xb + 1] * 0.75 * (1 - dens) * 0 if False else np.array(ink) * 0.8 + c[ya:yb + 1, xa:xb + 1] * 0.2
                x += cw + 1.3
            x += lh * 0.38
        y += lh
        first = False if r.random() < 0.9 else True


def make_page_text():
    W, H = 384, 512
    r = np.random.default_rng(3)
    pap = np.ones((H, W, 3)) * np.array([0.96, 0.93, 0.84])
    n = fnoise(H, W, 40, 40, 1)
    pap *= (1 + 0.025 * n[..., None]) * (1 + 0.02 * fnoise(H, W, 4, 100, 2)[..., None])
    gut = np.exp(-(np.arange(W) / (0.05 * W)) ** 2)[None, :, None]
    pap *= 1 - 0.22 * gut
    text_block(pap, int(0.14 * W), int(0.9 * W), int(0.17 * H), int(0.9 * H), 11, 5)
    # chapter header
    hh = int(0.07 * H)
    pap[hh:hh + 3, int(0.36 * W):int(0.66 * W)] = np.array([0.15, 0.12, 0.1])
    pap[hh + 9:hh + 15, int(0.3 * W):int(0.7 * W)] = np.array([0.15, 0.12, 0.1])
    pap[int(0.94 * H):int(0.94 * H) + 6, int(0.5 * W):int(0.54 * W)] = np.array([0.2, 0.17, 0.15])
    pap *= 0.97 + 0.03 * fnoise(H, W, 8, 8, 4)[..., None]
    save('lv_page_text', pap)


def make_news():
    W, H = 512, 512
    pap = np.ones((H, W, 3)) * np.array([0.82, 0.8, 0.72])
    pap *= (1 + 0.04 * fnoise(H, W, 50, 50, 11)[..., None]) * (1 + 0.04 * fnoise(H, W, 5, 5, 12)[..., None])
    ink = (0.1, 0.1, 0.1)
    # masthead
    pap[22:62, 40:472] = pap[22:62, 40:472] * 0.25 + np.array(ink) * 0.7
    pap[22:62, 40:472] += 0.12 * np.random.default_rng(1).standard_normal((40, 432, 1))
    pap[68:71, 30:482] = np.array(ink)
    pap[74:76, 30:482] = np.array(ink)
    # headline
    r = np.random.default_rng(4)
    x = 34
    for k in range(9):
        w = int(r.uniform(22, 44))
        pap[88:124, x:x + w] = np.array(ink) * 0.8 + pap[88:124, x:x + w] * 0.2
        x += w + 12
        if x > 460:
            break
    # photo
    yy, xx = np.mgrid[0:110, 0:150]
    ph = 0.55 + 0.25 * np.sin(xx / 20.0) * np.cos(yy / 17.0) + 0.1 * fnoise(110, 150, 10, 10, 7)
    ph = ph * (0.85 + 0.15 * (np.sin(xx * 1.9) * np.sin(yy * 1.9) > 0))
    pap[140:250, 34:184] = np.clip(ph, 0.2, 0.9)[..., None] * np.array([0.7, 0.68, 0.62])
    # columns
    for ci, (cx0, cx1) in enumerate(((34, 184), (196, 346), (358, 478))):
        text_block(pap, cx0, cx1, 262 if ci == 0 else 140, 498, 7, 20 + ci, indent=False)
    pap[140 + 0:250, 196:346] = pap[140:250, 196:346]
    for yb in (256, ):
        pap[yb:yb + 2, 30:482] = np.array(ink) * 0.8
    pap *= 0.96 + 0.04 * fnoise(H, W, 7, 7, 14)[..., None]
    save('lv_news', pap)


def main():
    os.makedirs(OUT, exist_ok=True)
    make_paintings()
    make_page_text()
    make_news()


if __name__ == '__main__':
    main()
