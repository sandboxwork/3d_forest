"""Procedural artwork for the bedroom: bd_painting_1..9.jpg (512px) + bd_quilt.jpg (512px). Pure numpy, saved via bpy.
Run: blender -b --python bd_gen_tex.py"""
import bpy, numpy as np, os, math
OUT = '/shared/river/assets/tex'
S = 1024          # supersampled canvas
R = np.random.default_rng(5)


def fnoise(su, sv, seed=0, shape=(S, S)):
    r = np.random.default_rng(seed)
    w = r.standard_normal(shape)
    Fq = np.fft.fft2(w)
    fy = np.fft.fftfreq(shape[0])[:, None] * shape[0]
    fx = np.fft.fftfreq(shape[1])[None, :] * shape[1]
    a = np.real(np.fft.ifft2(Fq * np.exp(-((fx / su) ** 2 + (fy / sv) ** 2))))
    return (a - a.mean()) / (a.std() + 1e-9)


def blur(a, r):
    sh = a.shape
    fy = np.fft.fftfreq(sh[0])[:, None]
    fx = np.fft.fftfreq(sh[1])[None, :]
    k = np.exp(-(fx ** 2 + fy ** 2) * (2 * (math.pi * r) ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(a) * k))


class Canvas:
    def __init__(s, bg, w=S, h=S):
        s.w, s.h = w, h
        s.img = np.zeros((h, w, 3), np.float32)
        s.img[:] = bg
        s.Y, s.X = np.mgrid[0:h, 0:w].astype(np.float32)

    def paint(s, mask, col, wash=0.0, edge=0.0, seed=0):
        """composite colour through float mask (0..1). wash: pigment mottling; edge: edge darkening (watercolour)."""
        col = np.asarray(col, np.float32)
        a = mask.astype(np.float32)
        c = np.broadcast_to(col, s.img.shape).copy()
        if wash:
            n = fnoise(14, 14, seed + 3, (s.h, s.w)) * 0.5 + fnoise(60, 60, seed + 4, (s.h, s.w)) * 0.3
            c *= (1 + wash * n)[..., None]
        if edge:
            bl = blur(a, 5)
            ed = np.clip(a - bl, 0, 1)
            c *= (1 - edge * ed * 2.5)[..., None]
        s.img = s.img * (1 - a[..., None]) + c * a[..., None]

    # --- primitives, all return masks over bbox-limited computation
    def poly(s, pts):
        pts = np.asarray(pts, np.float32)
        x0, y0 = np.floor(pts.min(0)).astype(int) - 2
        x1, y1 = np.ceil(pts.max(0)).astype(int) + 2
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, s.w), min(y1, s.h)
        m = np.zeros((s.h, s.w), np.float32)
        if x1 <= x0 or y1 <= y0:
            return m
        X = s.X[y0:y1, x0:x1]; Y = s.Y[y0:y1, x0:x1]
        ins = np.zeros(X.shape, bool)
        n = len(pts)
        for i in range(n):
            xa, ya = pts[i]; xb, yb = pts[(i + 1) % n]
            if ya == yb:
                continue
            cond = ((ya > Y) != (yb > Y)) & (X < (xb - xa) * (Y - ya) / (yb - ya) + xa)
            ins ^= cond
        m[y0:y1, x0:x1] = ins
        return m

    def ellipse(s, cx, cy, rx, ry, rot=0.0):
        x0, x1 = int(max(cx - max(rx, ry) - 2, 0)), int(min(cx + max(rx, ry) + 2, s.w))
        y0, y1 = int(max(cy - max(rx, ry) - 2, 0)), int(min(cy + max(rx, ry) + 2, s.h))
        X = s.X[y0:y1, x0:x1] - cx; Y = s.Y[y0:y1, x0:x1] - cy
        c, sn = math.cos(rot), math.sin(rot)
        u = X * c + Y * sn; v = -X * sn + Y * c
        m = np.zeros((s.h, s.w), np.float32)
        m[y0:y1, x0:x1] = np.clip((1 - np.sqrt((u / rx) ** 2 + (v / ry) ** 2)) * min(rx, ry) * 0.7 + 0.5, 0, 1)
        return m

    def stroke(s, pts, w0, w1=None):
        """thick polyline with tapering width -> mask (distance field to segments)"""
        w1 = w0 if w1 is None else w1
        pts = np.asarray(pts, np.float32)
        x0, y0 = np.floor(pts.min(0) - max(w0, w1) - 2).astype(int)
        x1, y1 = np.ceil(pts.max(0) + max(w0, w1) + 2).astype(int)
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, s.w), min(y1, s.h)
        m = np.zeros((s.h, s.w), np.float32)
        if x1 <= x0 or y1 <= y0:
            return m
        X = s.X[y0:y1, x0:x1]; Y = s.Y[y0:y1, x0:x1]
        best = np.zeros(X.shape, np.float32)
        n = len(pts) - 1
        for i in range(n):
            a = pts[i]; b = pts[i + 1]
            d = b - a
            L2 = float(d @ d) + 1e-9
            t = np.clip(((X - a[0]) * d[0] + (Y - a[1]) * d[1]) / L2, 0, 1)
            dist = np.hypot(X - (a[0] + t * d[0]), Y - (a[1] + t * d[1]))
            w = (w0 + (w1 - w0) * ((i + t) / n)) * 0.5
            best = np.maximum(best, np.clip(w - dist + 0.5, 0, 1))
        m[y0:y1, x0:x1] = best
        return m

    def finish(s, name, vignette=0.0, grain=0.03, size=512):
        im = s.img
        if vignette:
            r = np.hypot((s.X - s.w / 2) / (s.w / 2), (s.Y - s.h / 2) / (s.h / 2))
            im = im * (1 - vignette * np.clip(r - 0.5, 0, 1) ** 1.5)[..., None]
        im = im + grain * fnoise(300, 300, 99, (s.h, s.w))[..., None] * 0.3
        k = s.w // size
        im = im.reshape(size, k, size, k, 3).mean((1, 3))
        save(name, im)


def save(name, rgb):
    rgb = np.clip(rgb, 0, 1)[::-1]   # top-down -> blender bottom-up
    n = rgb.shape[0]
    img = bpy.data.images.new(name, n, rgb.shape[1], alpha=False)
    a = np.ones((n, rgb.shape[1], 4), np.float32)
    a[..., :3] = rgb
    img.pixels.foreach_set(a.ravel())
    img.file_format = 'JPEG'
    bpy.context.scene.render.image_settings.file_format = 'JPEG'
    bpy.context.scene.render.image_settings.quality = 90
    img.filepath_raw = os.path.join(OUT, name + '.jpg')
    img.save()
    print('saved', name)


def paper(base=(0.93, 0.88, 0.76), foxing=0.22, seed=0):
    c = Canvas(base)
    n = fnoise(8, 8, seed + 1) * 0.04 + fnoise(120, 120, seed + 2) * 0.015 + fnoise(400, 3, seed + 3) * 0.008
    c.img *= (1 + n)[..., None]
    if foxing:
        f = np.clip(fnoise(22, 22, seed + 5) - 1.1, 0, 1.2) * foxing
        c.img[..., 0] *= 1 - 0.18 * f; c.img[..., 1] *= 1 - 0.3 * f; c.img[..., 2] *= 1 - 0.45 * f
    # darker toward edges (age)
    r = np.hypot((c.X - S / 2) / (S / 2), (c.Y - S / 2) / (S / 2))
    c.img *= (1 - 0.08 * np.clip(r - 0.6, 0, 1))[..., None]
    return c


def scribble(c, x, y, wd, col, rows=1, rowh=34, seed=0, size=11):
    """handwriting-like lines"""
    r = np.random.default_rng(seed)
    for k in range(rows):
        xx = x
        yy = y + k * rowh
        while xx < x + wd - 30:
            wl = r.integers(24, 90)
            pts = []
            for i in range(int(wl / 4)):
                t = i * 4
                pts.append((xx + t, yy + math.sin(t * 0.55 + r.random() * 3) * size * 0.45 * (0.5 + r.random() * 0.5)))
            c.paint(c.stroke(pts, 2.6), col)
            xx += wl + r.integers(14, 24)


def frame_mat(c, col=(0.98, 0.95, 0.88), m=70):
    """mat/border: re-fill border region with paper colour and thin ink line"""
    mask = np.ones((c.h, c.w), np.float32)
    mask[m:-m, m:-m] = 0
    c.paint(mask, col)
    for i, w in enumerate((3,)):
        mm = np.zeros((c.h, c.w), np.float32)
        mm[m - 2:m + w - 2, m - 2:c.w - m + 2] = 1; mm[c.h - m - w + 2:c.h - m + 2, m - 2:c.w - m + 2] = 1
        mm[m - 2:c.h - m + 2, m - 2:m + w - 2] = 1; mm[m - 2:c.h - m + 2, c.w - m - w + 2:c.w - m + 2] = 1
        c.paint(mm * 0.8, (0.35, 0.28, 0.2))


# ---------------------------------------------------------------- 1. fern botanical
def fern(seed=1):
    r = np.random.default_rng(seed)
    c = paper(seed=seed)
    ink = (0.2, 0.28, 0.14)
    for (x0, scale, tilt) in ((430, 1.0, -0.08), (610, 0.78, 0.18)):
        pts = []
        for i in range(60):
            t = i / 59
            pts.append((x0 + math.sin(t * 2.4 + tilt * 9) * 55 * t * scale + tilt * 300 * t, 880 - t * 700 * scale))
        c.paint(c.stroke(pts, 7, 2), (0.3, 0.25, 0.12), wash=0.2)
        for i in range(4, 56):
            t = i / 59
            px, py = pts[i]; qx, qy = pts[i + 1]
            ang = math.atan2(qy - py, qx - px)
            ll = (1 - t ** 1.3) * 190 * scale + 12
            for side in (-1, 1):
                a = ang + side * (1.15 - 0.35 * t)
                dx, dy = math.cos(a), math.sin(a)
                nx, ny = -dy, dx
                m = []
                for k in range(14):
                    u = k / 13
                    m.append((px + dx * ll * u + nx * math.sin(u * math.pi) * ll * 0.12, py + dy * ll * u + ny * math.sin(u * math.pi) * ll * 0.12))
                for k in range(13, -1, -1):
                    u = k / 13
                    m.append((px + dx * ll * u - nx * math.sin(u * math.pi) * ll * 0.12, py + dy * ll * u - ny * math.sin(u * math.pi) * ll * 0.12))
                g = 0.5 + 0.4 * r.random()
                c.paint(c.poly(m), (ink[0] * (1.4 - 0.4 * g), ink[1] * (1.2 + 0.4 * g), ink[2] * 1.2), wash=0.35, edge=0.5, seed=i)
                c.paint(c.stroke([(px, py), (px + dx * ll, py + dy * ll)], 1.4), (0.14, 0.18, 0.08) , )
    scribble(c, 300, 920, 420, (0.25, 0.2, 0.15), seed=seed)
    frame_mat(c)
    c.finish('bd_painting_1', 0.25)


# ---------------------------------------------------------------- 2. wildflowers
def flowers(seed=2):
    r = np.random.default_rng(seed)
    c = paper((0.92, 0.9, 0.8), seed=seed)
    stems = [(300, 0.1, (0.85, 0.35, 0.45)), (480, -0.05, (0.95, 0.85, 0.35)), (640, 0.08, (0.55, 0.5, 0.85)), (780, -0.12, (0.9, 0.55, 0.35))]
    for (x0, tilt, pc) in stems:
        top = 260 + r.integers(0, 120)
        pts = [(x0 + tilt * (880 - y) + math.sin(y * 0.01) * 14, y) for y in np.linspace(880, top, 40)]
        c.paint(c.stroke(pts, 7, 4), (0.28, 0.4, 0.2), wash=0.25)
        for k in range(3):                      # leaves
            t = 0.2 + 0.2 * k
            px, py = pts[int(t * 39)]
            s_ = 1 if k % 2 else -1
            m = [(px, py)]
            for u in np.linspace(0, 1, 12):
                m.append((px + s_ * u * 120, py - u * 60 - math.sin(u * math.pi) * 38))
            for u in np.linspace(1, 0, 12):
                m.append((px + s_ * u * 120, py - u * 60 + math.sin(u * math.pi) * 8))
            c.paint(c.poly(m), (0.3, 0.46, 0.22), wash=0.35, edge=0.5, seed=k)
        hx, hy = pts[-1]
        npet = 9 if x0 != 640 else 6
        for p in range(npet):
            a = p * TAU / npet + r.random() * 0.1
            m = []
            L = 74 if x0 != 640 else 60
            for u in np.linspace(0, 1, 10):
                m.append((hx + math.cos(a) * L * u + math.cos(a + 1.57) * math.sin(u * math.pi) * 17, hy + math.sin(a) * L * u + math.sin(a + 1.57) * math.sin(u * math.pi) * 17))
            for u in np.linspace(1, 0, 10):
                m.append((hx + math.cos(a) * L * u - math.cos(a + 1.57) * math.sin(u * math.pi) * 17, hy + math.sin(a) * L * u - math.sin(a + 1.57) * math.sin(u * math.pi) * 17))
            c.paint(c.poly(m), pc, wash=0.3, edge=0.6, seed=p + x0)
        c.paint(c.ellipse(hx, hy, 17, 17), (0.85, 0.65, 0.15), edge=0.5)
    scribble(c, 330, 925, 360, (0.3, 0.22, 0.18), seed=seed)
    frame_mat(c)
    c.finish('bd_painting_2', 0.2)
TAU = 2 * math.pi


# ---------------------------------------------------------------- 3. landscape
def landscape(seed=3, dusk=False):
    r = np.random.default_rng(seed)
    c = Canvas((0, 0, 0))
    y = c.Y / S
    top = np.array([0.45, 0.62, 0.82]); hor = np.array([0.98, 0.9, 0.7])
    if dusk:
        top = np.array([0.25, 0.3, 0.55]); hor = np.array([0.98, 0.62, 0.4])
    t = np.clip(y / 0.58, 0, 1)[..., None]
    c.img = (top * (1 - t) + hor * t).astype(np.float32)
    # clouds
    cl = np.clip(fnoise(5, 18, seed + 7) - 0.4, 0, 1)
    cl *= np.clip(1 - y / 0.5, 0, 1)
    c.img = c.img * (1 - 0.6 * cl[..., None]) + np.array([1, 0.97, 0.92]) * 0.6 * cl[..., None]
    # sun
    sun = c.ellipse(680, 420, 46, 46)
    c.paint(blur(sun, 38) * 1.2 + sun, (1.0, 0.95, 0.75))
    # mountain layers
    layers = [(0.50, 0.0, (0.55, 0.62, 0.78), 70), (0.58, 1.0, (0.4, 0.5, 0.58), 55), (0.68, 2.0, (0.25, 0.4, 0.34), 45), (0.8, 3.0, (0.18, 0.3, 0.22), 30)]
    for (base, sd, col, amp) in layers:
        xs = np.arange(S)
        prof = base * S + (fnoise(7, 7, seed + int(sd * 11), (1, S))[0] * amp + fnoise(30, 30, seed + 20 + int(sd), (1, S))[0] * amp * 0.25)
        m = (c.Y > prof[None, :]).astype(np.float32)
        haze = (1 - sd / 4)
        col = np.array(col) * (0.8 + 0.2 * (1 - haze)) + np.array([0.85, 0.85, 0.8]) * 0.15 * haze
        c.paint(blur(m, 1.0), col, wash=0.12, seed=int(sd))
    # lake
    lake = (c.Y > 0.76 * S).astype(np.float32)
    refl = c.img[::-1].copy()
    ripple = np.sin(c.Y * 0.4 + fnoise(40, 3, seed + 31) * 4) * 0.04
    c.img = c.img * (1 - lake[..., None]) + (np.roll(refl, 0, 0) * 0.5 + np.array([0.3, 0.45, 0.5]) * 0.5 + ripple[..., None]) * lake[..., None]
    # pines foreground
    for k in range(9):
        x = r.integers(40, S - 40); hgt = r.integers(150, 330); base = 0.76 * S + r.integers(-20, 20)
        for j in range(7):
            u = j / 6
            w = (1 - u) * hgt * 0.28 + 6
            yy = base - hgt * u * 0.8
            c.paint(c.poly([(x - w, yy + 30), (x + w, yy + 30), (x, yy - 38)]), (0.09, 0.2, 0.13), wash=0.2, seed=k * 7 + j)
        c.paint(c.stroke([(x, base), (x, base - 60 + 70)], 9), (0.2, 0.12, 0.08))
    frame_mat(c, m=60)
    c.finish('bd_painting_3' if not dusk else 'bd_painting_4', 0.3)


# ---------------------------------------------------------------- 5. moonlit cabin
def night(seed=5):
    r = np.random.default_rng(seed)
    c = Canvas((0, 0, 0))
    y = (c.Y / S)[..., None]
    c.img = (np.array([0.04, 0.08, 0.2]) * (1 - y) + np.array([0.18, 0.28, 0.45]) * y).astype(np.float32)
    for i in range(160):
        x, yy = r.integers(0, S), r.integers(0, 600)
        c.paint(c.ellipse(x, yy, r.uniform(1, 3), r.uniform(1, 3)), (1, 1, 0.9) if r.random() < 0.8 else (0.9, 0.8, 1))
    moon = c.ellipse(720, 250, 85, 85)
    c.paint(blur(moon, 60) * 0.7, (0.8, 0.85, 1.0))
    c.paint(moon, (0.97, 0.95, 0.85))
    c.paint(c.ellipse(750, 230, 70, 70) * 0.0, (0, 0, 0))
    for (cx, cy, rr) in ((700, 270, 14), (740, 220, 10), (685, 215, 8)):
        c.paint(c.ellipse(cx, cy, rr, rr) * 0.35, (0.75, 0.75, 0.7))
    # hills
    prof = 700 + fnoise(6, 6, seed, (1, S))[0] * 40
    m = (c.Y > prof[None, :]).astype(np.float32)
    c.paint(blur(m, 1), (0.05, 0.09, 0.14))
    # cabin
    c.paint(c.poly([(250, 760), (480, 760), (480, 640), (365, 570), (250, 640)]), (0.06, 0.05, 0.07))
    c.paint(c.poly([(240, 650), (365, 560), (490, 650), (490, 665), (365, 580), (240, 665)]), (0.04, 0.04, 0.06))
    c.paint(c.poly([(310, 700), (360, 700), (360, 740), (310, 740)]), (1.0, 0.8, 0.35))
    c.paint(blur(c.poly([(310, 700), (360, 700), (360, 740), (310, 740)]), 25) * 0.9, (1.0, 0.7, 0.3))
    c.paint(c.poly([(310, 700), (360, 700), (360, 740), (310, 740)]), (1.0, 0.85, 0.45))
    c.paint(c.stroke([(335, 700), (335, 740)], 3), (0.3, 0.2, 0.1)); c.paint(c.stroke([(310, 720), (360, 720)], 3), (0.3, 0.2, 0.1))
    for k in range(10):
        x = r.integers(500, 960); hgt = r.integers(120, 280)
        for j in range(6):
            u = j / 5
            w = (1 - u) * hgt * 0.27 + 5
            yy = 760 - hgt * u * 0.8
            c.paint(c.poly([(x - w, yy + 26), (x + w, yy + 26), (x, yy - 34)]), (0.03, 0.07, 0.09))
    for k in range(5):
        x = r.integers(60, 240); hgt = r.integers(120, 220)
        for j in range(6):
            u = j / 5
            w = (1 - u) * hgt * 0.27 + 5
            yy = 770 - hgt * u * 0.8
            c.paint(c.poly([(x - w, yy + 26), (x + w, yy + 26), (x, yy - 34)]), (0.03, 0.07, 0.09))
    frame_mat(c, col=(0.12, 0.1, 0.09), m=50)
    c.finish('bd_painting_5', 0.2)


# ---------------------------------------------------------------- 6. silhouette cameo
def cameo(seed=6):
    c = paper((0.9, 0.84, 0.7), seed=seed)
    # oval
    ov = c.ellipse(512, 512, 330, 410)
    c.paint(ov, (0.95, 0.91, 0.8), wash=0.1)
    ring = np.clip(ov - c.ellipse(512, 512, 310, 390), 0, 1)
    c.paint(ring, (0.3, 0.24, 0.16))
    # profile polygon (facing right)
    prof = [(470, 780), (470, 700), (455, 650), (470, 620), (440, 580), (430, 520), (440, 470), (455, 410), (485, 360), (540, 330), (600, 345),
            (630, 390), (640, 440), (655, 485), (675, 505), (655, 520), (660, 545), (650, 560), (655, 585), (640, 615), (610, 625), (590, 655),
            (585, 700), (620, 730), (680, 760), (700, 810), (560, 830), (470, 830)]
    sm = []
    for i in range(len(prof)):
        sm.append(prof[i])
    c.paint(blur(c.poly(sm), 1.6), (0.07, 0.06, 0.06))
    # hair bun
    c.paint(c.ellipse(450, 420, 75, 85), (0.07, 0.06, 0.06))
    c.paint(c.ellipse(420, 520, 45, 70), (0.07, 0.06, 0.06))
    # ribbon
    c.paint(c.stroke([(540, 335), (500, 360), (470, 420)], 8), (0.8, 0.75, 0.65))
    # laurel decoration around
    for sgn in (-1, 1):
        for i in range(14):
            t = i / 13
            a = math.radians(100 + t * 150)
            cx = 512 + sgn * math.cos(a) * 345 * -1; cy = 512 + math.sin(a) * 425 - 40
            ang = a + (math.pi / 2) * sgn
            c.paint(c.ellipse(cx, cy, 24, 8, ang + 0.6 * sgn), (0.25, 0.32, 0.2), wash=0.2)
    frame_mat(c, col=(0.96, 0.93, 0.85), m=75)
    c.finish('bd_painting_6', 0.2)


# ---------------------------------------------------------------- 7. cross-stitch sampler
GLY = {
    'H': ["X...X", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    'O': [".XXX.", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    'M': ["X...X", "XX.XX", "X.X.X", "X.X.X", "X...X", "X...X", "X...X"],
    'E': ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "XXXXX"],
    'S': [".XXXX", "X....", "X....", ".XXX.", "....X", "....X", "XXXX."],
    'W': ["X...X", "X...X", "X...X", "X.X.X", "X.X.X", "XX.XX", "X...X"],
    'T': ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "..X.."],
    'A': [".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    'B': ["XXXX.", "X...X", "X...X", "XXXX.", "X...X", "X...X", "XXXX."],
}


def sampler(seed=7):
    c = Canvas((0.9, 0.84, 0.7))
    lin = fnoise(500, 500, seed) * 0.03
    # linen weave
    wv = (np.sin(c.X * 1.6) * np.sin(c.Y * 1.6)) * 0.02
    c.img *= (1 + lin + wv)[..., None]
    cell = 16
    ox, oy = 96, 112

    def st(gx, gy, col):
        x = ox + gx * cell; y = oy + gy * cell
        c.paint(c.stroke([(x + 2, y + 2), (x + cell - 2, y + cell - 2)], 4.2), col)
        c.paint(c.stroke([(x + cell - 2, y + 2), (x + 2, y + cell - 2)], 4.2), col)
    gw, gh = 53, 50
    red = (0.62, 0.18, 0.15); blue = (0.15, 0.25, 0.45); green = (0.2, 0.38, 0.2); gold = (0.75, 0.55, 0.15); brown = (0.35, 0.22, 0.14)
    for gx in range(gw):
        for gy in (0, 1, gh - 2, gh - 1):
            st(gx, gy, red if (gx // 2) % 2 == 0 else blue)
    for gy in range(gh):
        for gx in (0, 1, gw - 2, gw - 1):
            st(gx, gy, red if (gy // 2) % 2 == 0 else blue)
    def word(txt, gx0, gy0, col):
        x = gx0
        for ch in txt:
            if ch == ' ':
                x += 4; continue
            for ry, row in enumerate(GLY[ch]):
                for rx, v in enumerate(row):
                    if v == 'X':
                        st(x + rx, gy0 + ry, col)
            x += 6
    word('HOME', 14, 6, blue)
    word('SWEET', 11, 15, red)
    word('HOME', 14, 24, green)
    # house + tree motif
    house = ["......XX......", ".....XXXX.....", "....XXXXXX....", "...XXXXXXXX...", "..XXXXXXXXXX..", ".XXXXXXXXXXXX.", "..XX..XX.XXX..", "..XX..XX.XXX..", "..XXXXXX.XXX..", "..XXXXXX.XXX.."]
    for ry, row in enumerate(house):
        for rx, v in enumerate(row):
            if v == 'X':
                st(10 + rx, 35 + ry, brown if ry > 4 else red)
    tree = ["...X...", "..XXX..", ".XXXXX.", "..XXX..", ".XXXXX.", "XXXXXXX", "...X...", "...X..."]
    for ry, row in enumerate(tree):
        for rx, v in enumerate(row):
            if v == 'X':
                st(30 + rx, 35 + ry, green if ry < 6 else brown)
    for k in range(3):
        for ry in range(4):
            for rx in range(4):
                if (rx + ry) % 2 == 0:
                    st(39 + k * 4 + rx, 41 + ry, gold if k % 2 else red)
    c.finish('bd_painting_7', 0.15, grain=0.02)


# ---------------------------------------------------------------- 8. old map
def oldmap(seed=8):
    r = np.random.default_rng(seed)
    c = paper((0.9, 0.82, 0.62), foxing=0.4, seed=seed)
    land = fnoise(5, 5, seed + 1) + 0.4 * fnoise(20, 20, seed + 2)
    mask = (land > -0.2).astype(np.float32)
    mask = blur(mask, 1.2)
    c.paint(mask * 0.35, (0.75, 0.65, 0.4))
    edge = np.clip(np.abs(blur(mask, 6) - 0.5) * -1 + 0.5, 0, 1) ** 4
    c.paint(np.clip(edge * 8, 0, 1) * 0.6, (0.3, 0.22, 0.15))
    # contour lines
    for lv in (0.2, 0.7, 1.2):
        cm = np.clip(1 - np.abs(land - lv) * 18, 0, 1)
        c.paint(cm * 0.35, (0.4, 0.3, 0.2))
    # river
    pts = [(120 + t * 800, 80 + t * 860 + math.sin(t * 9) * 80) for t in np.linspace(0, 1, 60)]
    c.paint(c.stroke(pts, 5, 16), (0.35, 0.5, 0.6))
    for k in range(40):
        x, y = r.integers(120, 900), r.integers(120, 900)
        if land[y, x] > 0:
            c.paint(c.poly([(x - 8, y + 10), (x + 8, y + 10), (x, y - 14)]), (0.2, 0.3, 0.18))
    # compass
    cx, cy = 840, 190
    c.paint(c.ellipse(cx, cy, 58, 58) * 0.5, (0.95, 0.9, 0.8)); c.paint(np.clip(c.ellipse(cx, cy, 58, 58) - c.ellipse(cx, cy, 54, 54), 0, 1), (0.3, 0.2, 0.15))
    for a in range(4):
        ang = a * math.pi / 2
        c.paint(c.poly([(cx + math.cos(ang) * 74, cy + math.sin(ang) * 74), (cx + math.cos(ang + 2.4) * 14, cy + math.sin(ang + 2.4) * 14), (cx, cy), (cx + math.cos(ang - 2.4) * 14, cy + math.sin(ang - 2.4) * 14)]), (0.6, 0.2, 0.15) if a == 3 else (0.25, 0.2, 0.15))
    scribble(c, 150, 930, 520, (0.3, 0.22, 0.15), seed=seed)
    frame_mat(c, col=(0.95, 0.9, 0.78), m=60)
    c.finish('bd_painting_8', 0.25)


# ---------------------------------------------------------------- 9. songbird on branch
def bird(seed=9):
    c = paper((0.94, 0.9, 0.8), seed=seed)
    c.paint(c.stroke([(80, 700), (300, 690), (520, 660), (760, 600), (940, 590)], 20, 6), (0.32, 0.22, 0.14), wash=0.4)
    for k in range(7):
        x = 220 + k * 105; y = 690 - k * 14
        m = [(x, y)]
        for u in np.linspace(0, 1, 10):
            m.append((x + u * 90, y + 40 * (-1) ** k * u - math.sin(u * math.pi) * 24))
        for u in np.linspace(1, 0, 10):
            m.append((x + u * 90, y + 40 * (-1) ** k * u + math.sin(u * math.pi) * 24))
        c.paint(c.poly(m), (0.3, 0.45, 0.2), wash=0.3, edge=0.5, seed=k)
    body = c.ellipse(500, 560, 120, 80, -0.3)
    c.paint(body, (0.75, 0.45, 0.2), wash=0.3, edge=0.6)
    c.paint(c.ellipse(560, 580, 85, 55, -0.3) * 0.9, (0.96, 0.85, 0.7), wash=0.2)
    c.paint(c.ellipse(610, 480, 48, 44), (0.45, 0.3, 0.18), wash=0.3, edge=0.5)
    c.paint(c.poly([(645, 480), (700, 495), (645, 505)]), (0.85, 0.65, 0.2))
    c.paint(c.ellipse(625, 470, 7, 7), (0.05, 0.05, 0.05))
    c.paint(c.poly([(400, 540), (250, 610), (240, 590), (380, 520)]), (0.4, 0.28, 0.16), wash=0.3, edge=0.5)
    c.paint(c.ellipse(480, 560, 78, 35, -0.5) * 0.9, (0.55, 0.35, 0.18), wash=0.3, edge=0.5)
    c.paint(c.stroke([(520, 625), (525, 668)], 5), (0.2, 0.14, 0.1)); c.paint(c.stroke([(555, 628), (560, 664)], 5), (0.2, 0.14, 0.1))
    scribble(c, 300, 870, 420, (0.3, 0.22, 0.18), seed=seed)
    frame_mat(c)
    c.finish('bd_painting_9', 0.25)


# ---------------------------------------------------------------- quilt
def quilt():
    N = 512
    nc, nr = 11, 9
    r = np.random.default_rng(21)
    pal = [(0.18, 0.26, 0.45), (0.62, 0.2, 0.18), (0.86, 0.68, 0.28), (0.45, 0.58, 0.42), (0.93, 0.89, 0.78), (0.4, 0.27, 0.18), (0.8, 0.5, 0.5),
           (0.25, 0.5, 0.52), (0.7, 0.55, 0.35), (0.55, 0.62, 0.75)]
    Y, X = np.mgrid[0:N, 0:N].astype(np.float32)
    cw, ch = N / nc, N / nr
    img = np.zeros((N, N, 3), np.float32)
    for j in range(nr):
        for i in range(nc):
            x0, y0 = int(i * cw), int(j * ch)
            x1, y1 = int((i + 1) * cw), int((j + 1) * ch)
            w, h = x1 - x0, y1 - y0
            ly, lx = np.mgrid[0:h, 0:w].astype(np.float32)
            a = pal[r.integers(len(pal))]; b = pal[r.integers(len(pal))]
            kind = r.integers(0, 6)
            border = i in (0, nc - 1) or j in (0, nr - 1)
            if border:
                kind = 0; a = (0.2, 0.28, 0.42) if (i + j) % 2 == 0 else (0.55, 0.22, 0.2)
            blk = np.zeros((h, w, 3), np.float32); blk[:] = a
            if kind == 1:   # diagonal split
                m = ((lx / w + ly / h) > 1.0)
                blk[m] = b
            elif kind == 2:  # stripes
                m = (np.floor(lx / (w / 6)) % 2 == 0)
                blk[m] = b
            elif kind == 3:  # gingham
                m = (np.floor(lx / (w / 6)) % 2 == 0) ^ (np.floor(ly / (h / 6)) % 2 == 0)
                blk[m] = (np.array(a) * 0.55 + np.array(b) * 0.45)
            elif kind == 4:  # dots
                for _ in range(7):
                    cx, cy = r.uniform(0, w), r.uniform(0, h)
                    m = (np.hypot(lx - cx, ly - cy) < 3.2)
                    blk[m] = b
            elif kind == 5:  # centre diamond
                m = (np.abs(lx - w / 2) / (w / 2) + np.abs(ly - h / 2) / (h / 2)) < 0.8
                blk[m] = b
                m2 = (np.abs(lx - w / 2) / (w / 2) + np.abs(ly - h / 2) / (h / 2)) < 0.28
                blk[m2] = a
            # woven texture + stitch shadow near cell edge
            wv = 1 + 0.045 * np.sin(lx * 1.9) * np.sin(ly * 1.9) + 0.03 * (r.random((h, w)) - 0.5)
            ed = np.minimum(np.minimum(lx, w - 1 - lx), np.minimum(ly, h - 1 - ly))
            seam = 1 - 0.28 * np.exp(-ed / 1.8)
            img[y0:y1, x0:x1] = blk * wv[..., None] * seam[..., None]
    img *= (1 + 0.04 * fnoise(8, 8, 3, (N, N)))[..., None]
    save('bd_quilt', img)


if __name__ == '__main__':
    fern(); flowers(); landscape(3); landscape(4, dusk=True); night(); cameo(); sampler(); oldmap(); bird(); quilt()
