"""One-off procedural textures for the kitchen bundle (numpy, saved through bpy).  -> /shared/river/assets/tex/kt_*.jpg (256px)
Run: blender -b --python kt_tex.py"""
import bpy, numpy as np, os
OUT = '/shared/river/assets/tex'
N = 256


def fnoise(su, sv, seed=0, shape=(N, N)):
    r = np.random.default_rng(seed)
    w = r.standard_normal(shape)
    Fq = np.fft.fft2(w)
    fy = np.fft.fftfreq(shape[0])[:, None] * shape[0]
    fx = np.fft.fftfreq(shape[1])[None, :] * shape[1]
    filt = np.exp(-((fx / su) ** 2 + (fy / sv) ** 2))
    a = np.real(np.fft.ifft2(Fq * filt))
    return (a - a.mean()) / (a.std() + 1e-9)


def save(name, rgb):
    rgb = np.clip(rgb, 0, 1)
    img = bpy.data.images.new(name, N, N, alpha=False)
    a = np.ones((N, N, 4), dtype=np.float32)
    a[..., :3] = rgb
    img.pixels.foreach_set(a.ravel())
    img.file_format = 'JPEG'
    bpy.context.scene.render.image_settings.file_format = 'JPEG'
    bpy.context.scene.render.image_settings.quality = 90
    img.filepath_raw = os.path.join(OUT, name + '.jpg')
    img.save()
    print('saved', name)


def srgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])


def crust():
    n1 = fnoise(4, 4, 1); n2 = fnoise(16, 16, 2); n3 = fnoise(70, 70, 3)
    base = np.array([0.66, 0.38, 0.15])
    dark = np.array([0.36, 0.17, 0.06])
    t = np.clip(0.5 + 0.30 * n1 + 0.12 * n2, 0, 1)[..., None]
    col = base * (1 - t) + dark * t
    # blisters (small lighter bumps) and fine cracks
    bl = np.clip((fnoise(34, 34, 5) - 1.0) * 1.2, 0, 1)[..., None]
    col = col * (1 - 0.3 * bl) + np.array([0.82, 0.58, 0.3]) * 0.3 * bl
    ridge = np.abs(fnoise(22, 22, 4))
    crack = np.clip(1 - ridge * 7, 0, 1)[..., None]
    col = col * (1 - 0.45 * crack)
    # soft flour film: broad low-contrast dusting + fine speckle
    film = np.clip((fnoise(6, 6, 7) - 0.2) * 0.7, 0, 1)[..., None] * 0.22
    spk = np.clip((n3 - 1.3) * 1.5, 0, 1)[..., None] * 0.35
    col = col * (1 - film - spk) + np.array([0.93, 0.9, 0.83]) * (film + spk)
    save('kt_crust', col)


def crumb():
    col = np.array([0.93, 0.84, 0.64]) * np.ones((N, N, 1))
    n = fnoise(18, 18, 6)
    pores = np.clip((n - 0.9) * 2.5, 0, 1)[..., None]
    pores2 = np.clip((fnoise(40, 40, 7) - 1.3) * 2.0, 0, 1)[..., None]
    col = col * (1 - 0.45 * pores - 0.3 * pores2)
    col *= (1 + 0.04 * fnoise(60, 60, 8)[..., None])
    save('kt_crumb', col)


def cheese():
    col = np.array([0.93, 0.74, 0.30]) * np.ones((N, N, 1))
    n = fnoise(4, 4, 9)
    col = col * (1 + 0.07 * n[..., None]) + 0.0
    col *= (1 + 0.03 * fnoise(60, 60, 10)[..., None])
    sp = np.clip((fnoise(30, 30, 11) - 1.4) * 2.5, 0, 1)[..., None]
    col = col * (1 - 0.18 * sp)
    save('kt_cheese', col)


def labels():
    cell = 64
    A = np.ones((N, N, 3)) * 0.9
    yy, xx = np.mgrid[0:cell, 0:cell]

    def put(cx, cy, img):
        # image row 0 = bottom in blender; cells indexed from bottom-left
        A[cy * cell:(cy + 1) * cell, cx * cell:(cx + 1) * cell] = img

    def base(c):
        return np.ones((cell, cell, 3)) * srgb(c)

    def rect(img, x0, y0, x1, y1, c):
        img[y0:y1, x0:x1] = srgb(c)

    def frame(img, m, w, c):
        img[m:m + w, m:cell - m] = srgb(c); img[cell - m - w:cell - m, m:cell - m] = srgb(c)
        img[m:cell - m, m:m + w] = srgb(c); img[m:cell - m, cell - m - w:cell - m] = srgb(c)

    def disc(img, cx, cy, r, c):
        mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r
        img[mask] = srgb(c)

    def textbars(img, y0, n, c, x0=10, x1=54, seed=0):
        r = np.random.default_rng(seed)
        for i in range(n):
            y = y0 + i * 4
            x = x0
            while x < x1 - 3:
                w = int(r.integers(3, 9))
                if x + w > x1:
                    w = x1 - x
                img[y:y + 2, x:x + w] = srgb(c)
                x += w + 2
    # row 0: tins
    for i, (b, band, em) in enumerate([('#2f5a3c', '#d9b25a', '#d9b25a'), ('#7a2a25', '#e8d9a8', '#e8d9a8'),
                                        ('#5a3a24', '#e3cfa0', '#e3cfa0'), ('#3b5f8a', '#f0ece0', '#f0ece0')]):
        im = base(b); frame(im, 3, 2, band); rect(im, 3, 20, 61, 24, band); rect(im, 3, 40, 61, 44, band)
        disc(im, 32, 32, 7, em); disc(im, 32, 32, 4, b); textbars(im, 10, 2, em, seed=i); textbars(im, 48, 2, em, seed=i + 9)
        put(i, 0, im)
    # row 1: salt, pepper, jam strawberry, jam plum
    for i, (b, fg) in enumerate([('#e9e6dc', '#2c4a78'), ('#2a2a2e', '#e8e6dc'), ('#efe3c4', '#a02a2a'), ('#efe3c4', '#5a2a58')]):
        im = base(b); frame(im, 4, 2, fg)
        if i >= 2:
            for k in range(5):
                disc(im, 18 + k * 7, 34 + (k % 2) * 5, 4, fg)
            rect(im, 10, 18, 54, 20, fg)
        else:
            disc(im, 32, 32, 12, fg); disc(im, 32, 32, 9, b); disc(im, 32, 32, 4, fg)
        textbars(im, 8, 2, fg, seed=20 + i); textbars(im, 48, 2, fg, seed=30 + i)
        put(i, 1, im)
    # row 2: pickles, honey, flour sack stamp, bean sack stamp
    for i, (b, fg) in enumerate([('#e8e0c0', '#3f6a38'), ('#f0dca0', '#a8721e'), ('#ddd2b4', '#8a2a24'), ('#ddd2b4', '#2a4468')]):
        im = base(b); frame(im, 4, 3, fg); frame(im, 9, 1, fg)
        if i == 2 or i == 3:
            rect(im, 12, 20, 52, 24, fg); rect(im, 12, 40, 52, 44, fg)
            for k in range(7):
                rect(im, 14 + k * 6, 27, 16 + k * 6, 37, fg)
            textbars(im, 49, 1, fg, 12, 52, seed=40 + i)
        else:
            for k in range(6):
                a = k * np.pi / 3
                disc(im, int(32 + 8 * np.cos(a)), int(32 + 8 * np.sin(a)), 4, fg)
            disc(im, 32, 32, 4, b); textbars(im, 10, 2, fg, seed=50 + i); textbars(im, 48, 2, fg, seed=60 + i)
        put(i, 2, im)
    # row 3: spices + kraft + wax paper + plain cream
    for i, c in enumerate(['#8a3b22', '#6a7a3a', '#caa23a']):
        im = base('#e9dfc2'); rect(im, 0, 24, cell, 40, c); textbars(im, 8, 2, '#4a3a2a', seed=70 + i); textbars(im, 48, 2, '#4a3a2a', seed=80 + i)
        put(i, 3, im)
    im = base('#b99a6a'); im *= (1 + 0.05 * fnoise(30, 30, 14, (cell, cell))[..., None]); put(3, 3, im)
    save('kt_labels', A)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    crust(); crumb(); cheese(); labels()
