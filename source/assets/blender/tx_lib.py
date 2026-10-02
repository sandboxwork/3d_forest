"""Shared helpers for the tx_* PBR texture library (numpy, tileable by construction; saved through bpy as JPEG).
Convention: arrays are (H,W[,3]) with row 0 = TOP of the image. Normal maps are OpenGL (green = up in image)."""
import bpy, numpy as np, os
f32 = np.float32
OUT = '/shared/river/assets/tex'
os.makedirs(OUT, exist_ok=True)


def grid(N):
    y, x = np.mgrid[0:N, 0:N]
    return x.astype(f32), y.astype(f32)


def noise(N, seed, cx, cy=None, hp=0.0, ang=0.0):
    """Tileable gaussian-filtered noise, unit std. cx/cy = lowpass cutoff (cycles/tile) along the filter's u/v axes
    (rotated by ang radians). hp>0 also removes frequencies below hp*cutoff."""
    cy = cx if cy is None else cy
    r = np.random.default_rng(seed)
    F = np.fft.fft2(r.standard_normal((N, N)))
    fy = np.fft.fftfreq(N)[:, None] * N
    fx = np.fft.fftfreq(N)[None, :] * N
    if ang:
        c, s = np.cos(ang), np.sin(ang)
        fu = fx * c + fy * s
        fv = -fx * s + fy * c
    else:
        fu, fv = fx, fy
    q = (fu / cx) ** 2 + (fv / cy) ** 2
    filt = np.exp(-q)
    if hp > 0:
        filt = filt * (1 - np.exp(-q / (hp * hp)))
    a = np.real(np.fft.ifft2(F * filt)).astype(f32)
    return (a - a.mean()) / (a.std() + 1e-9)


def fbm(N, seed, base, octs=5, gain=0.55, ar=1.0):
    t = np.zeros((N, N), f32)
    amp = 1.0
    tot = 0
    for i in range(octs):
        t += amp * noise(N, seed + 31 * i, base * 2 ** i, base * 2 ** i * ar)
        tot += amp
        amp *= gain
    return t / tot * 1.6


def sstep(a, b, x):
    t = np.clip((x - a) / (b - a + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


def mix(c0, c1, t):
    c0 = np.asarray(c0, f32)
    c1 = np.asarray(c1, f32)
    t = np.asarray(t, f32)[..., None]
    return c0 * (1 - t) + c1 * t


def vor(N, gx, gy, seed, x=None, y=None, jit=1.0, sx=1.0, sy=1.0):
    """Tileable jittered-grid voronoi. Returns d1, d2 (pixels), rid (random 0..1 per nearest cell), cx, cy (nearest point, px, unwrapped)."""
    if x is None:
        x, y = grid(N)
    x = np.mod(x, N)
    y = np.mod(y, N)
    r = np.random.default_rng(seed)
    jx = (0.5 + (r.random((gy, gx)) - 0.5) * jit).astype(f32)
    jy = (0.5 + (r.random((gy, gx)) - 0.5) * jit).astype(f32)
    rid_t = r.random((gy, gx)).astype(f32)
    cw, ch = N / gx, N / gy
    ci = np.floor(x / cw).astype(int)
    cj = np.floor(y / ch).astype(int)
    d1 = np.full(x.shape, 1e9, f32)
    d2 = np.full(x.shape, 1e9, f32)
    rid = np.zeros(x.shape, f32)
    px1 = np.zeros(x.shape, f32)
    py1 = np.zeros(x.shape, f32)
    for dy in (-2, -1, 0, 1, 2):
        for dx in (-2, -1, 0, 1, 2):
            ii = ci + dx
            jj = cj + dy
            iw = np.mod(ii, gx)
            jw = np.mod(jj, gy)
            ppx = (ii + jx[jw, iw]) * cw
            ppy = (jj + jy[jw, iw]) * ch
            d = np.sqrt(((x - ppx) * sx) ** 2 + ((y - ppy) * sy) ** 2)
            closer = d < d1
            second = (~closer) & (d < d2)
            d2 = np.where(closer, d1, np.where(second, d, d2))
            rid = np.where(closer, rid_t[jw, iw], rid)
            px1 = np.where(closer, ppx, px1)
            py1 = np.where(closer, ppy, py1)
            d1 = np.where(closer, d, d1)
    return d1, d2, rid, px1, py1


def normal_from_height(h, k):
    """Tangent-space OpenGL normal from a (periodic) height field. k = slope gain (height units per pixel)."""
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5
    gy_down = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 0.5
    nx = -gx * k
    ny = gy_down * k  # image row increases downward; green=up => +dh/d(row)
    nz = np.ones_like(h)
    L = np.sqrt(nx * nx + ny * ny + nz * nz)
    return np.stack([nx / L, ny / L, nz / L], -1) * 0.5 + 0.5


def down2(a):
    return 0.25 * (a[0::2, 0::2] + a[1::2, 0::2] + a[0::2, 1::2] + a[1::2, 1::2])


def save(name, albedo, normal, rough, size=512, quality=85):
    """albedo (N,N,3) sRGB 0..1 ; normal (N,N,3) encoded 0..1 ; rough (N,N) 0..1 -> tex/<name>.jpg,_n,_r"""
    albedo = np.clip(albedo, 0, 1).astype(f32)
    normal = np.clip(normal, 0, 1).astype(f32)
    rough = np.clip(rough, 0, 1).astype(f32)
    N = albedo.shape[0]
    if size < N:
        while albedo.shape[0] > size:
            albedo = down2(albedo)
            rough = down2(rough)
            n = down2(normal * 2 - 1)
            n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9
            normal = n * 0.5 + 0.5
    for suffix, arr in (('', albedo), ('_n', normal), ('_r', np.repeat(rough[..., None], 3, -1))):
        M = arr.shape[0]
        img = bpy.data.images.new(name + suffix, M, M, alpha=False)
        img.colorspace_settings.name = 'Non-Color'   # write values verbatim
        a = np.ones((M, M, 4), f32)
        a[..., :3] = arr[::-1]
        img.pixels.foreach_set(a.ravel())
        scn = bpy.context.scene
        scn.render.image_settings.file_format = 'JPEG'
        scn.render.image_settings.quality = quality
        scn.render.image_settings.color_mode = 'RGB'
        img.filepath_raw = os.path.join(OUT, name + suffix + '.jpg')
        img.file_format = 'JPEG'
        img.save()
        bpy.data.images.remove(img)
    print('saved', name, albedo.shape[0])
