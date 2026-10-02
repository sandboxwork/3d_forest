"""Procedural tileable textures for house_interior (pure numpy, saved via bpy). Output: /shared/river/assets/tex/hi_*.jpg"""
import bpy, numpy as np, os
OUT = '/shared/river/assets/tex'
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)
N = 256


def fnoise(su, sv, seed=0, shape=(N, N)):
    """tileable noise via FFT filtering; su/sv = cutoff (cycles per tile) along u(x)/v(y)"""
    r = np.random.default_rng(seed)
    w = r.standard_normal(shape)
    F = np.fft.fft2(w)
    fy = np.fft.fftfreq(shape[0])[:, None] * shape[0]
    fx = np.fft.fftfreq(shape[1])[None, :] * shape[1]
    filt = np.exp(-((fx / su) ** 2 + (fy / sv) ** 2))
    a = np.real(np.fft.ifft2(F * filt))
    a = (a - a.mean()) / (a.std() + 1e-9)
    return a


def save(name, rgb):
    rgb = np.clip(rgb, 0, 1)
    img = bpy.data.images.new(name, N, N, alpha=False)
    a = np.ones((N, N, 4), dtype=np.float32)
    a[..., :3] = rgb
    # blender image origin bottom-left; flipY false in three => keep as is (tileable anyway)
    img.pixels.foreach_set(a.ravel())
    img.file_format = 'JPEG'
    scn = bpy.context.scene
    scn.render.image_settings.file_format = 'JPEG'
    scn.render.image_settings.quality = 88
    img.filepath_raw = os.path.join(OUT, name + '.jpg')
    img.save()
    print('saved', name)


# wood: grain runs along v (image y). Stretch: low frequency along v, high along u.
def wood():
    warp = fnoise(6, 2, 1)
    rings = fnoise(10, 1.2, 2)
    x = np.linspace(0, 1, N, endpoint=False)[None, :] * np.ones((N, 1))
    t = x * 7 + warp * 0.35 + rings * 0.5
    g = 0.5 + 0.5 * np.sin(t * 2 * np.pi)
    g = g ** 2.2
    fine = fnoise(90, 1.5, 3)           # fine fibres
    pores = fnoise(120, 10, 4)
    v = 0.80 - 0.16 * g + 0.045 * fine + 0.02 * pores
    # board seams every 0.5 tile along u
    col = np.stack([v * 1.0, v * 0.93, v * 0.83], -1)
    col = col / col.mean() * 0.80
    save('hi_wood', col)
    save('hi_paint', 0.9 + (col - col.mean()) * 0.3)


def weave():
    x = np.arange(N)[None, :] * np.ones((N, 1)); y = np.arange(N)[:, None] * np.ones((1, N))
    p = 8
    a = np.sin(x / p * np.pi * 2) ; b = np.sin(y / p * np.pi * 2)
    over = ((x // (p / 2)).astype(int) + (y // (p / 2)).astype(int)) % 2
    v = np.where(over == 0, 0.5 + 0.5 * a, 0.5 + 0.5 * b)
    v = 0.78 + 0.10 * (v - 0.5) * 2 + 0.05 * fnoise(60, 60, 5) + 0.03 * fnoise(8, 8, 6)
    save('hi_weave', np.stack([v, v, v * 0.98], -1))


def knit():
    x = np.arange(N)[None, :] * np.ones((N, 1)); y = np.arange(N)[:, None] * np.ones((1, N))
    pw, ph = 10.0, 12.0
    u = (x % pw) / pw; w = (y % ph) / ph
    # V-shaped knit stitches
    s = np.abs(u - 0.5) * 2
    k = np.sin((w + s * 0.5) * np.pi * 2) * 0.5 + 0.5
    v = 0.62 + 0.3 * k * (1 - s * 0.3) + 0.04 * fnoise(80, 80, 7)
    save('hi_knit', np.stack([v, v, v], -1))


def leather():
    n1 = fnoise(45, 45, 8); n2 = fnoise(20, 20, 9)
    cells = np.abs(n1)
    v = 0.70 + 0.12 * (cells - 0.6) + 0.06 * n2
    save('hi_leather', np.stack([v, v * 0.98, v * 0.95], -1))


def wicker():
    x = np.arange(N)[None, :] * np.ones((N, 1)); y = np.arange(N)[:, None] * np.ones((1, N))
    p = 16
    cx = (x // p).astype(int); cy = (y // p).astype(int)
    horiz = ((cx + cy) % 2 == 0)
    fx = (x % p) / p; fy = (y % p) / p
    strand = np.where(horiz, np.sin(fy * np.pi), np.sin(fx * np.pi))
    along = np.where(horiz, fx, fy)
    v = 0.45 + 0.42 * strand ** 0.6 + 0.06 * fnoise(100, 6, 10) + 0.06 * np.sin(along * 40)
    v = np.clip(v, 0.15, 1)
    save('hi_wicker', np.stack([v, v * 0.92, v * 0.78], -1))


def plaster():
    v = 0.82 + 0.06 * fnoise(30, 30, 11) + 0.03 * fnoise(90, 90, 12)
    save('hi_plaster', np.stack([v, v, v * 0.97], -1))


def metal():
    v = 0.72 + 0.10 * fnoise(60, 60, 13) + 0.12 * fnoise(250, 2, 14) * 0.4 + 0.08 * fnoise(8, 8, 15)
    save('hi_metal', np.stack([v, v, v], -1))


for f in (wood, weave, knit, leather, wicker, plaster, metal):
    f()
