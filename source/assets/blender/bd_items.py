"""Small props: lamps, flames (lamp_bd_<n> parts), candles, books, glass, bottles, desk items, slippers, boots, umbrellas ..."""
from bd_lib import *
from bd_hw import *

LAMPN = [0]
BOOKCOLS = ['#7a2f2a', '#2f4a63', '#3d5a3a', '#8a6a2e', '#4a2f4f', '#a04b2e', '#2c3f45', '#6b5a3c', '#8c3b3b', '#36506b', '#5d6b3a', '#b08d4a']


def flame(pos, sc=1.0, inten=1.0, dist=5.0, color=(1.0, 0.68, 0.36), light_on=True, name=None):
    LAMPN[0] += 1
    n = name or 'lamp_bd_%d' % LAMPN[0]
    saved = part_begin()
    prof = [(0.0005, -0.013), (0.0045, -0.011), (0.0075, -0.005), (0.0075, 0.003), (0.0055, 0.012), (0.003, 0.022), (0.0012, 0.03), (0.0, 0.034)]
    lathe(M['flame'], pos, [(r * sc, z * sc) for r, z in profile_pts(prof, 2)], seg=10, cap=False)
    part_end(saved, n, pos)
    if light_on:
        light(n, pos, color, inten, dist)
    return n


def glass_tumbler(pos, r=0.032, h=0.095, water=0.7):
    prof = [(r * 0.8, 0.0), (r * 0.82, 0.006), (r * 0.9, h * 0.5), (r, h), (r * 0.94, h), (r * 0.84, h * 0.5), (r * 0.74, 0.008), (0.001, 0.008)]
    lathe(M['glass'], pos, prof, seg=18, cap=False)
    if water:
        wz = h * water
        lathe(M['water'], pos, [(0.001, 0.008), (r * 0.75, 0.008), (r * (0.76 + 0.2 * water), wz), (0.001, wz)], seg=18, cap=False)


def wine_carafe(pos, r=0.05, h=0.2, water=0.55):
    prof = profile_pts([(0.0005, 0.0), (r * 0.9, 0.0), (r, 0.02), (r * 0.98, h * 0.35), (r * 0.7, h * 0.55), (r * 0.36, h * 0.68), (r * 0.3, h * 0.82), (r * 0.42, h * 0.95), (r * 0.46, h)], 3)
    lathe(M['glass'], pos, prof, seg=20, cap=False)
    if water:
        wz = h * water * 0.5
        lathe(M['water'], pos, [(0.001, 0.003), (r * 0.9, 0.003), (r * 0.97, h * 0.3), (r * 0.95, h * 0.35), (0.001, h * 0.35)], seg=20, cap=False)
    lathe(M['glass'], Vector(pos) + Vector((0, 0, h)), profile_pts([(0.0005, 0.0), (r * 0.32, 0.0), (r * 0.46, 0.012), (r * 0.2, 0.02), (r * 0.12, 0.034), (r * 0.18, 0.04), (0.001, 0.043)], 2), seg=14, cap=False)


def candle(pos, h=0.12, r=0.011, lit=True, inten=0.7, dist=4.5, name=None, sc=1.0):
    p = Vector(pos)
    cyl(M['wax'], p + Vector((0, 0, h / 2)), r, h, seg=14, r2=r * 0.97, col=(0.96, 0.92, 0.8))
    # melted top & drips
    lathe(M['wax'], p + Vector((0, 0, h)), [(r * 0.97, 0), (r * 0.9, 0.003), (r * 0.55, 0.0025), (0.002, -0.004)], seg=14, cap=False, col=(0.98, 0.94, 0.82))
    for a, L in ((0.6, 0.03), (2.7, 0.045), (4.5, 0.02)):
        tube(M['wax'], [p + Vector((math.cos(a) * r * 0.97, math.sin(a) * r * 0.97, h - 0.002)), p + Vector((math.cos(a) * r * 1.05, math.sin(a) * r * 1.05, h - L * 0.5)),
                        p + Vector((math.cos(a) * r * 1.06, math.sin(a) * r * 1.06, h - L))], 0.0028, seg=6, col=(0.97, 0.93, 0.8))
    tube(M['ink'], [p + Vector((0, 0, h - 0.002)), p + Vector((0.0015, 0, h + 0.008)), p + Vector((0.004, 0, h + 0.013))], 0.0009, seg=4, col=(0.05, 0.04, 0.03))
    if lit:
        return flame(p + Vector((0.0015, 0, h + 0.026)), sc, inten, dist, name=name)


def chamberstick(pos, lit=True, inten=0.8, dist=5.0, name=None, h=0.075, cl=0.1):
    """enamel/brass chamber candlestick with finger ring"""
    p = Vector(pos)
    prof = profile_pts([(0.0005, 0.0), (0.055, 0.0), (0.062, 0.004), (0.058, 0.009), (0.03, 0.013), (0.015, 0.018), (0.012, 0.03), (0.017, 0.038), (0.012, 0.046), (0.011, 0.058), (0.018, 0.064), (0.0145, 0.068)], 3)
    lathe(M['brass'], p, prof, seg=24, cap=False)
    torus(M['brass'], p + Vector((0.06, 0, 0.008)), 0.022, 0.0045, plane='xz', rot=(0, 0, 0), seg=20, rseg=8, a0=-180 + 20, a1=180 - 20 + 0)
    return candle(p + Vector((0, 0, 0.068)), cl, 0.0105, lit, inten, dist, name)


def oil_lamp(pos, sc=1.0, inten=1.0, dist=6.0, name=None, lit=True, glass_col=(1.0, 0.95, 0.85)):
    """brass-based kerosene lamp with glass font and chimney"""
    p = Vector(pos)
    cyl(M['brass'], p + Vector((0, 0, 0.007)), 0.065, 0.014, seg=28, r2=0.06, bev=0.003)
    lathe(M['brass'], p, profile_pts([(0.0005, 0.0), (0.06, 0.0), (0.066, 0.008), (0.05, 0.02), (0.02, 0.036), (0.015, 0.05), (0.024, 0.062), (0.03, 0.068)], 3), seg=28, cap=False)
    # glass font (clear with oil inside)
    lathe(M['glass'], p + Vector((0, 0, 0.066)), profile_pts([(0.025, 0.0), (0.06, 0.016), (0.075, 0.05), (0.066, 0.092), (0.04, 0.115), (0.025, 0.124)], 4), seg=28, cap=False, col=glass_col)
    lathe(M['glass_amber'], p + Vector((0, 0, 0.07)), profile_pts([(0.001, 0.0), (0.054, 0.014), (0.068, 0.045), (0.06, 0.07), (0.001, 0.07)], 3), seg=24, cap=False, col=(1.0, 0.85, 0.55))
    # collar + burner
    lathe(M['brass'], p + Vector((0, 0, 0.19)), profile_pts([(0.024, 0.0), (0.03, 0.006), (0.03, 0.02), (0.02, 0.03), (0.02, 0.038), (0.026, 0.044), (0.03, 0.05)], 3), seg=20, cap=False)
    # thumb wheel
    cyl(M['brass'], p + Vector((0.034, 0, 0.205)), 0.011, 0.004, axis='x', seg=12)
    # chimney
    lathe(M['glass'], p + Vector((0, 0, 0.236)), profile_pts([(0.028, 0.0), (0.03, 0.014), (0.02, 0.04), (0.017, 0.1), (0.018, 0.16), (0.019, 0.185)], 4), seg=20, cap=False)
    # wick
    box(M['wax'], p + Vector((0, 0, 0.246)), (0.022, 0.003, 0.012), bev=0, col=(0.9, 0.85, 0.7))
    if lit:
        return flame(p + Vector((0, 0, 0.268)), sc * 1.25, inten, dist, name=name)


def table_lamp(pos, inten=1.0, dist=6.0, name=None, col='#5d7a8c', shade_col=(0.95, 0.86, 0.68)):
    """ceramic-based lamp with a glowing linen shade (emissive shade part so it can pulse with the light) -- bulb flame part inside"""
    p = Vector(pos)
    lathe(M['ceramic'], p, profile_pts([(0.0005, 0.0), (0.05, 0.0), (0.06, 0.012), (0.075, 0.07), (0.07, 0.12), (0.05, 0.17), (0.025, 0.2), (0.016, 0.23), (0.014, 0.26)], 4), seg=28, cap=False, col=hex_rgb(col))
    cyl(M['brass'], p + Vector((0, 0, 0.268)), 0.02, 0.016, seg=14, bev=0.003)
    # shade: truncated cone, open
    lathe(M['shadeglow'], p + Vector((0, 0, 0.28)), [(0.07, 0.0), (0.095, 0.0), (0.17, 0.17), (0.165, 0.17), (0.09, 0.012)][::-1], seg=36, cap=False, col=shade_col) if False else None
    sh = [(0.066, 0.0), (0.07, 0.01), (0.115, 0.1), (0.13, 0.17), (0.127, 0.172), (0.11, 0.1), (0.063, 0.01)]
    lathe(M['linen'], p + Vector((0, 0, 0.275)), sh, seg=32, cap=False, col=shade_col)
    tube(M['brass'], arcpts((0, 0, 0), 0.13, 0, 360, 36, 'xy'), 0.0016, seg=4) if False else None
    return flame(p + Vector((0, 0, 0.345)), 0.9, inten, dist, name=name, color=(1.0, 0.76, 0.45))


def book(pos, size, rotz=0, col=None, lean=0, bands=True, tilt=None, spine_out=(0, -1)):
    """standing book. pos = bottom centre. size = (thickness, depth, height). spine faces local -y"""
    w, d, h = size
    c = jit(C(col or rnd.choice(BOOKCOLS)), 0.1)
    Mx = xf(pos, (lean, 0, rotz))
    r = 0.0035
    box(M['book_cloth'], None, (w, d, h), Mx=Mx @ Matrix.Translation((0, 0, h / 2)), bev=0.0025, col=c, g=2)
    box(M['paper'], None, (w - 2 * r - 0.0006, d - 0.006, h - 0.008), Mx=Mx @ Matrix.Translation((0, 0.003, h / 2)), bev=0.0006, col=(0.93, 0.88, 0.76), g=0, skip_down=False)
    if bands:
        for zz in (0.15, 0.85):
            box(M['brass'], None, (w + 0.0012, 0.0015, 0.006), Mx=Mx @ Matrix.Translation((0, -d / 2 - 0.0006, h * zz)), bev=0, col=(0.9, 0.7, 0.35))
        box(M['brass'], None, (w * 0.7, 0.0015, h * 0.12), Mx=Mx @ Matrix.Translation((0, -d / 2 - 0.0006, h * 0.5)), bev=0, col=(0.85, 0.65, 0.3))


def book_flat(pos, size, rotz=0, col=None, ribbon=None):
    """lying book; size=(w along x, d along y, thickness)"""
    w, d, h = size
    c = jit(C(col or rnd.choice(BOOKCOLS)), 0.1)
    Mx = xf(pos, (0, 0, rotz))
    cv = 0.0032
    box(M['book_cloth'], None, (w, d, cv), Mx=Mx @ Matrix.Translation((0, 0, cv / 2)), bev=0.0012, col=c, g=0, skip_down=False)
    box(M['book_cloth'], None, (w, d, cv), Mx=Mx @ Matrix.Translation((0, 0, h - cv / 2)), bev=0.0012, col=c, g=0, skip_down=False)
    box(M['book_cloth'], None, (cv, d, h), Mx=Mx @ Matrix.Translation((-w / 2 + cv / 2, 0, h / 2)), bev=0.0015, col=c, g=1)
    box(M['paper'], None, (w - cv - 0.004, d - 0.006, h - 2 * cv - 0.0006), Mx=Mx @ Matrix.Translation((cv / 2 + 0.001, 0, h / 2)), bev=0.0005, col=(0.93, 0.88, 0.76), g=1, skip_down=False)
    for zz in (0.25, 0.75):
        box(M['brass'], None, (cv * 1.2, 0.012, 0.0015), Mx=Mx @ Matrix.Translation((-w / 2 + cv / 2, 0, h * zz)), bev=0, col=(0.9, 0.7, 0.35)) if False else None
    if ribbon:
        box(M['linen'], None, (0.01, 0.0025, 0.0015), Mx=Mx @ Matrix.Translation((w / 2 + 0.004, d * 0.3, h * 0.5)), bev=0, col=C(ribbon))


def book_open(pos, rotz=0, w=0.15, d=0.21, col='#6b3a2a', lines=True, seed=0):
    """open book with curved page blocks and handwriting-like lines"""
    r_ = random.Random(seed)
    Mx = xf(pos, (0, 0, rotz))
    cv = 0.003
    box(M['book_cloth'], None, (2 * w + 0.008, d + 0.006, cv), Mx=Mx @ Matrix.Translation((0, 0, cv / 2)), bev=0.001, col=C(col), g=0, skip_down=False)
    for s in (-1, 1):
        # curved page block: grid surface with a bow toward the gutter
        bm = bmesh.new()
        ul = bm.loops.layers.uv.new('UVMap')
        n = 10
        rows = []
        for i in range(n + 1):
            u = i / n
            x = s * (0.004 + u * (w - 0.006))
            zt = cv + 0.012 * (0.35 + 0.65 * (1 - abs(1 - u * 1.0))) + 0.006 * (1 - u) ** 2 * 1.0 + 0.004 * (1 - u)
            zt = cv + 0.014 - 0.006 * u + 0.012 * (1 - u) ** 3
            rows.append((x, zt))
        vs = []
        for (x, zt) in rows:
            vs.append((bm.verts.new((x, -d / 2 + 0.004, cv)), bm.verts.new((x, -d / 2 + 0.004, zt)), bm.verts.new((x, d / 2 - 0.004, zt)), bm.verts.new((x, d / 2 - 0.004, cv))))
        for i in range(n):
            a, b = vs[i], vs[i + 1]
            for (p0, p1, q0, q1) in ((a[1], b[1], b[2], a[2]), (a[0], b[0], b[1], a[1]), (a[2], b[2], b[3], a[3])):
                try:
                    f_ = bm.faces.new([p0, p1, q0, q1]); f_.smooth = False
                except ValueError:
                    pass
        # end cap (outer edge)
        a = vs[-1]
        try:
            bm.faces.new([a[0], a[1], a[2], a[3]])
        except ValueError:
            pass
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        for fc in bm.faces:
            for l in fc.loops:
                l[ul].uv = (l.vert.co.x * 5, l.vert.co.y * 5)
        put(M['paper'], bm, Mx, col=(0.94, 0.9, 0.78), uvs=1.0, skip_down=False)
        bm.free()
        if lines:
            for i in range(11):
                L = w * r_.uniform(0.55, 0.78)
                x0 = s * (0.02 + (w - 0.04 - L) * r_.random() * 0.3) if s > 0 else -(0.02 + (w - 0.04 - L) * r_.random() * 0.3)
                xc = x0 + s * L / 2
                u = abs(xc) / w
                zt = cv + 0.014 - 0.006 * u + 0.012 * (1 - u) ** 3 + 0.0004
                box(M['ink'], None, (L, 0.0022, 0.0004), Mx=Mx @ Matrix.Translation((xc, d / 2 - 0.03 - i * 0.0165, zt)), bev=0, col=(0.2, 0.17, 0.15), skip_down=False)


def inkwell(pos):
    p = Vector(pos)
    lathe(M['glass'], p, profile_pts([(0.0005, 0.0), (0.03, 0.0), (0.034, 0.008), (0.032, 0.025), (0.02, 0.034), (0.013, 0.036)], 3), seg=20, cap=False)
    lathe(M['ink'], p, [(0.001, 0.006), (0.026, 0.006), (0.027, 0.02), (0.001, 0.02)], seg=18, cap=False)
    lathe(M['brass'], p + Vector((0, 0, 0.033)), profile_pts([(0.017, 0.0), (0.019, 0.004), (0.018, 0.01), (0.012, 0.014)], 2), seg=14, cap=False)


def feather_quill(pos, rot=0, tilt=-8, L=0.26):
    Mx = xf(pos, (0, 0, rot)) @ rotm((0, tilt, 0))
    # shaft
    pts = [Mx @ Vector((t * L, 0, 0.02 * math.sin(t * 2.4) * 0.3)) for t in np.linspace(0, 1, 8)]
    tube(M['paper'], pts, [0.0017 * (1 - 0.7 * t) + 0.0004 for t in np.linspace(0, 1, 8)], seg=5, col=(0.96, 0.93, 0.85))
    # vanes (two flat polygons with a barb notch)
    for s in (-1, 1):
        poly = []
        for i, t in enumerate(np.linspace(0.18, 0.97, 14)):
            w = 0.022 * math.sin((t - 0.12) / 0.88 * math.pi) ** 0.8 + 0.002
            poly.append((t * L, s * w))
        outline = [(L * 0.18, 0.0)] + poly + [(L * 0.97, 0.0)]
        bm = bmesh.new()
        vv = [bm.verts.new(Mx @ Vector((a_, b_, 0.0006 * s))) for a_, b_ in outline]
        try:
            bm.faces.new(vv)
        except ValueError:
            pass
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        put(M['paper'], bm, Matrix.Identity(4), col=(0.95, 0.94, 0.9) if s > 0 else (0.88, 0.86, 0.8), uvs=2.0, skip_down=False)
        bm.free()


def magnifier(pos, rot=0, tilt=0):
    Mx = xf(pos, (tilt, 0, rot))
    torus(M['brass'], None, 0.04, 0.0025, plane='xy', Mx=Mx @ Matrix.Translation((0, 0, 0.0035)), seg=28, rseg=8)
    lathe(M['glass'], None, [(0.0005, 0.0), (0.038, 0.0), (0.0005, 0.0)], seg=28, cap=False, Mx=Mx @ Matrix.Translation((0, 0, 0.0035)), scale=(1, 1, 1))
    tube(M['brass'], [Mx @ Vector((0.043, 0, 0.0035)), Mx @ Vector((0.075, 0, 0.0035))], 0.0035, seg=8)
    lathe(M['wood_dark'], None, profile_pts([(0.007, 0.0), (0.009, 0.02), (0.0075, 0.06), (0.011, 0.085), (0.0005, 0.09)], 2), seg=10, cap=False, Mx=Mx @ Matrix.Translation((0.075, 0, 0.0035)) @ rotm((0, 90, 0)))


def hairbrush(pos, rot=0):
    Mx = xf(pos, (0, 0, rot))
    pts = [(math.cos(a) * 0.035, math.sin(a) * 0.05 + 0.04) for a in np.linspace(0, TAU, 20, endpoint=False)]
    poly_prism(M['wood_oak'], pts, 0.013, Mx @ Matrix.Translation((0, 0, 0.0)) @ Matrix.Translation((0, 0, 0.0065)), col=(0.9, 0.7, 0.5), bev=0.004, plane='xy', seg=2)
    handle = [Mx @ Vector((0, -0.01 - 0.17 * t, 0.0065 + 0.002 * t)) for t in np.linspace(0, 1, 10)]
    tube(M['wood_oak'], handle, [0.009 + 0.004 * math.sin(math.pi * t) for t in np.linspace(0, 1, 10)], seg=10, col=(0.9, 0.7, 0.5))
    # bristles on top: block + rows of tufts
    for i in range(5):
        for j in range(7):
            x = (i - 2) * 0.012 + (0.006 if j % 2 else 0)
            y = 0.04 + (j - 3) * 0.0125
            if (x / 0.032) ** 2 + ((y - 0.04) / 0.047) ** 2 < 1:
                cyl(M['felt'], Vector(pos) + (xf((0, 0, 0), (0, 0, rot)).to_3x3() @ Vector((x, y, 0.019))), 0.0027, 0.012, seg=5, col=(0.88, 0.8, 0.66))


def perfume_bottle(pos, kind=0, col=(0.7, 0.85, 0.9), h=0.1):
    p = Vector(pos)
    if kind == 0:   # faceted flask with round stopper
        lathe(M['glass'], p, profile_pts([(0.0005, 0.0), (0.03, 0.0), (0.033, 0.004), (0.031, h * 0.6), (0.02, h * 0.72), (0.011, h * 0.78), (0.012, h * 0.85)], 3), seg=8, cap=False, col=col)
        lathe(M['water'], p, [(0.001, 0.004), (0.028, 0.004), (0.028, h * 0.5), (0.001, h * 0.5)], seg=8, cap=False, col=col)
        sphere(M['glass'], p + Vector((0, 0, h * 0.85 + 0.014)), 0.016, seg=14, col=col)
    elif kind == 1:  # tall cylinder with atomizer
        lathe(M['glass'], p, profile_pts([(0.0005, 0.0), (0.022, 0.0), (0.024, 0.003), (0.023, h * 0.8), (0.018, h * 0.88), (0.009, h * 0.9)], 2), seg=18, cap=False, col=col)
        lathe(M['water'], p, [(0.001, 0.004), (0.02, 0.004), (0.02, h * 0.6), (0.001, h * 0.6)], seg=16, cap=False, col=col)
        lathe(M['brass'], p + Vector((0, 0, h * 0.89)), profile_pts([(0.012, 0.0), (0.013, 0.01), (0.008, 0.02), (0.007, 0.03)], 2), seg=12, cap=False)
        sphere(M['wax'], p + Vector((0.026, 0, h * 0.94)), 0.012, seg=12, col=(0.7, 0.35, 0.4))
        tube(M['linen'], [p + Vector((0.0, 0, h * 0.95)), p + Vector((0.016, 0, h * 0.99)), p + Vector((0.024, 0, h * 0.98))], 0.0025, seg=5, col=(0.85, 0.75, 0.5))
    else:           # squat round bottle with cork
        lathe(M['glass'], p, profile_pts([(0.0005, 0.0), (0.035, 0.0), (0.04, 0.02), (0.035, 0.05), (0.013, 0.068), (0.012, 0.09), (0.016, 0.096)], 3), seg=20, cap=False, col=col)
        lathe(M['water'], p, [(0.001, 0.004), (0.034, 0.004), (0.037, 0.03), (0.03, 0.05), (0.001, 0.05)], seg=18, cap=False, col=col)
        cyl(M['wood_pine'], p + Vector((0, 0, 0.1)), 0.0105, 0.018, seg=10, r2=0.0125, col=(0.9, 0.78, 0.55))


def jewelry_box(pos, rot=0, open_lid=0):
    Mx = xf(pos, (0, 0, rot))
    box(M['wood_dark'], None, (0.2, 0.13, 0.065), Mx=Mx @ Matrix.Translation((0, 0, 0.0325)), bev=0.004, col=(0.95, 0.85, 0.78), g=0)
    box(M['wood_oak'], None, (0.17, 0.1, 0.004), Mx=Mx @ Matrix.Translation((0, 0, 0.067)), bev=0.0005, col=(1.1, 1.0, 0.9), g=0)
    box(M['wood_dark'], None, (0.205, 0.135, 0.022), Mx=Mx @ Matrix.Translation((0, 0, 0.076)), bev=0.006, col=(0.95, 0.85, 0.78), g=0, seg=2)
    box(M['wood_oak'], None, (0.15, 0.08, 0.003), Mx=Mx @ Matrix.Translation((0, 0, 0.0875)), bev=0.0005, col=(1.1, 1.0, 0.9), g=0)
    # brass corners, clasp, hinges
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(M['brass'], None, (0.014, 0.014, 0.005), Mx=Mx @ Matrix.Translation((sx * 0.0955, sy * 0.0605, 0.0885)), bev=0.0012)
        box(M['brass'], None, (0.018, 0.003, 0.012), Mx=Mx @ Matrix.Translation((sx * 0.05, -0.0675, 0.06)), bev=0.0006) if False else None
    box(M['brass'], None, (0.022, 0.003, 0.03), Mx=Mx @ Matrix.Translation((0, 0.0685, 0.068)), bev=0.0008)
    box(M['ink'], None, (0.002, 0.0008, 0.008), Mx=Mx @ Matrix.Translation((0, 0.0702, 0.064)), bev=0, col=(0.03, 0.02, 0.02))
    for sx in (-1, 1):
        box(M['brass'], None, (0.022, 0.004, 0.026), Mx=Mx @ Matrix.Translation((sx * 0.055, -0.0665, 0.07)), bev=0.0008)
    # pearl necklace spilling over the front edge
    pts = [Vector(p) for p in catmull([(-0.04, 0.0, 0.0), (-0.02, 0.05, 0.0), (0.0, 0.082, -0.02), (0.02, 0.07, -0.05), (0.03, 0.082, -0.07)], 6)]
    for i, q in enumerate(pts[::2]):
        sphere(M['ceramic'], Mx @ Vector((q.x + 0.02, q.y + 0.0, 0.1 + q.z + 0.0)) if False else Mx @ Vector((q.x + 0.02, q.y, 0.092 + q.z * 0.4)), 0.0042, seg=8, col=(0.98, 0.96, 0.92))


def slippers(pos, rot=0, col='#8a3a3a', lining=(0.9, 0.86, 0.75)):
    """pair of leather slippers with wool lining, left+right, placed as a side-by-side pair"""
    c = C(col)
    for s in (-1, 1):
        Mx = xf(pos, (0, 0, rot)) @ Matrix.Translation((s * 0.055, 0, 0)) @ rotm((0, 0, s * -6))
        # sole
        pts = []
        for a in np.linspace(0, TAU, 24, endpoint=False):
            x = math.cos(a) * 0.04 * (1.0 - 0.15 * math.sin(a) * 1.0)
            y = math.sin(a) * 0.1 + 0.0
            pts.append((x, y))
        poly_prism(M['leather'], pts, 0.008, Mx @ Matrix.Translation((0, 0, 0.004)), col=(0.4, 0.28, 0.2), bev=0.002, plane='xy')
        # upper: toe cap (half dome) + heel counter + wool rim
        sphere(M['leather'], None, 0.04, seg=14, rings=8, sq=(1.0, 1.35, 0.55), Mx=Mx @ Matrix.Translation((0, 0.035, 0.008)), col=c)
        cyl(M['leather'], None, 0.04, 0.045, seg=16, Mx=Mx @ Matrix.Translation((0, -0.05, 0.03)) @ Matrix.Diagonal((1, 1.1, 1, 1)), col=c, cap=False)
        torus(M['wool'], None, 0.033, 0.009, plane='xy', Mx=Mx @ Matrix.Translation((0, -0.055, 0.052)) @ Matrix.Diagonal((1, 1.15, 1, 1)), seg=12, rseg=5, col=lining)
        sphere(M['wool'], None, 0.026, seg=12, rings=6, sq=(1, 1.1, 0.3), Mx=Mx @ Matrix.Translation((0, -0.02, 0.025)), col=lining)


def boot(pos, rot=0, col='#3b2a1f', h=0.28, s=1.0, tilt=None):
    """leather ankle boot: sole + welt + heel, toe cap, ankle shaft with cuff, pull tab. pos = bottom centre, toe toward local -y"""
    c = C(col)
    Mx = xf(pos, tilt if tilt else (0, 0, rot)) if not tilt else xf(pos, (tilt[0], tilt[1], rot))
    Mx = Mx @ Matrix.Diagonal((s, s, s, 1))
    sole = []
    for a in np.linspace(0, TAU, 18, endpoint=False):
        x = math.cos(a) * 0.045
        y = math.sin(a) * 0.14
        if y < 0:
            x *= 0.92 + 0.08 * (1 + y / 0.14)
        sole.append((x, y))
    poly_prism(M['leather'], sole, 0.018, Mx @ Matrix.Translation((0, 0, 0.009)), col=(0.16, 0.11, 0.08), bev=0.004, plane='xy', seg=1)
    sole2 = [(x * 0.97, y * 0.97) for x, y in sole]
    poly_prism(M['leather'], sole2, 0.04, Mx @ Matrix.Translation((0, 0, 0.038)), col=c, bev=0.008, plane='xy', seg=1)
    sphere(M['leather'], None, 0.045, seg=14, rings=7, sq=(1.0, 1.7, 0.9), Mx=Mx @ Matrix.Translation((0, -0.07, 0.05)), col=c)
    # shaft: elliptical tube from the instep up to the cuff
    pts = [Mx @ Vector((0, 0.065 - 0.012 * t, 0.045 + (h - 0.045) * t)) for t in np.linspace(0, 1, 7)]
    rr = [0.051, 0.05, 0.047, 0.045, 0.044, 0.045, 0.047]
    tube(M['leather'], pts, rr, seg=12, col=c, caps=False, flat=(1.0, 1.1))
    # dark lining visible inside the opening
    top_c = Mx @ Vector((0, 0.053, h - 0.02))
    lathe(M['leather'], None, [(0.0005, 0.0), (0.043, 0.0)], seg=10, cap=False, Mx=Mx @ Matrix.Translation((0, 0.053, h - 0.025)) @ Matrix.Diagonal((1, 1.1, 1, 1)), col=(0.08, 0.05, 0.04))
    lathe(M['leather'], None, [(0.0005, 0.0), (0.043, 0.0)], seg=10, cap=False, Mx=Mx @ Matrix.Translation((0, 0.053, h - 0.025)) @ Matrix.Diagonal((1, 1.1, 1, 1)) @ Matrix.Rotation(math.pi, 4, 'X'), col=(0.08, 0.05, 0.04))
    torus(M['leather'], None, 0.046, 0.0045, plane='xy', Mx=Mx @ Matrix.Translation((0, 0.053, h)) @ Matrix.Diagonal((1, 1.1, 1, 1)), seg=14, rseg=5, col=tuple(x * 1.25 for x in c))
    # tongue + 5 brass eyelets on the front seam
    def yfront(t):
        return 0.065 - 0.012 * t - (0.051 - 0.007 * t)
    box(M['leather'], None, (0.04, 0.008, (h - 0.06) * 0.8), Mx=Mx @ Matrix.Translation((0, yfront(0.5) - 0.002, 0.06 + (h - 0.06) * 0.42)), bev=0.002, col=tuple(x * 0.9 for x in c))
    for k in range(5):
        z = 0.08 + k * (h * 0.55) / 5
        t = (z - 0.045) / (h - 0.045)
        for sx in (-1, 1):
            sphere(M['brass'], None, 0.0042, seg=6, rings=3, sq=(1, 0.6, 1), Mx=Mx @ Matrix.Translation((sx * 0.026, yfront(t) + 0.002, z)))
    tube(M['leather'], [Mx @ Vector((0, 0.1, h - 0.03)), Mx @ Vector((0, 0.108, h - 0.01)), Mx @ Vector((0, 0.108, h - 0.04))], 0.004, seg=4, col=tuple(x * 0.9 for x in c), caps=False)
    box(M['leather'], None, (0.07, 0.05, 0.02), Mx=Mx @ Matrix.Translation((0, 0.105, 0.02)), bev=0.004, col=(0.12, 0.08, 0.06))


def lantern(pos, h=0.32, w=0.15, inten=1.4, dist=7.0, name=None, hang=True, chain_to=None):
    """iron lantern: frame, glass panes, candle + flame part, ring handle."""
    p = Vector(pos)
    mat = M['iron']
    hw = w / 2
    cyl(mat, p + Vector((0, 0, 0.012)), hw * 1.05, 0.024, seg=4, r2=hw * 1.05, rot=(0, 0, 45), bev=0.003) if False else box(mat, p + Vector((0, 0, 0.012)), (w * 1.05, w * 1.05, 0.024), bev=0.004, col=(0.8, 0.8, 0.8))
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(mat, p + Vector((sx * hw, sy * hw, h / 2 + 0.01)), (0.012, 0.012, h - 0.02), bev=0.002, col=(0.85, 0.85, 0.85))
    for (cx, cy, sz) in ((0, hw, (w, 0.0012, h - 0.05)), (0, -hw, (w, 0.0012, h - 0.05)), (hw, 0, (0.0012, w, h - 0.05)), (-hw, 0, (0.0012, w, h - 0.05))):
        box(M['glass'], p + Vector((cx, cy, h / 2 + 0.012)), sz, bev=0, skip_down=False)
        # mullion cross
    for (cx, cy, sz) in ((0, hw, (w, 0.004, 0.006)), (0, -hw, (w, 0.004, 0.006)), (hw, 0, (0.004, w, 0.006)), (-hw, 0, (0.004, w, 0.006))):
        box(mat, p + Vector((cx, cy, h * 0.55)), sz, bev=0)
    # roof: pyramid + chimney cap
    lathe(mat, p + Vector((0, 0, h)), [(w * 0.78, 0.0), (w * 0.6, 0.02), (w * 0.2, 0.05), (w * 0.17, 0.06), (w * 0.2, 0.07), (0.001, 0.09)], seg=4, rot=(0, 0, 45), cap=False, col=(0.8, 0.8, 0.8)) if False else None
    lathe(mat, p + Vector((0, 0, h)), profile_pts([(w * 0.72, 0.0), (w * 0.62, 0.015), (w * 0.3, 0.045), (w * 0.17, 0.055), (w * 0.2, 0.065), (w * 0.12, 0.085), (0.001, 0.095)], 3), seg=8, cap=False)
    if hang:
        tube(mat, [p + Vector((-hw * 0.7, 0, h + 0.06)), p + Vector((-hw * 0.3, 0, h + 0.16)), p + Vector((0, 0, h + 0.185)), p + Vector((hw * 0.3, 0, h + 0.16)), p + Vector((hw * 0.7, 0, h + 0.06))], 0.003, seg=6)
        torus(mat, p + Vector((0, 0, h + 0.2)), 0.014, 0.0025, plane='xz', seg=16, rseg=6)
    # candle stub + dish
    cyl(mat, p + Vector((0, 0, 0.03)), 0.04, 0.012, seg=16, bev=0.003)
    return candle(p + Vector((0, 0, 0.036)), 0.09, 0.012, True, inten, dist, name, sc=1.5)


def umbrella(pos, tilt=(0, 8, 0), col=(0.12, 0.13, 0.17), L=0.85, hook=True, ribs=8, tip_down=True):
    """closed umbrella: fluted cloth body, tie strap, bent wood handle. tip_down: pos is the ferrule tip, handle (crook) pointing up"""
    Mx = xf(pos, tilt)
    if tip_down:
        Mx = Mx @ Matrix.Translation((0, 0, L)) @ rotm((180, 0, 0))
    prof = []
    n = 12
    for i in range(n + 1):
        t = i / n
        r = 0.011 + 0.016 * math.sin(math.pi * min(t ** 0.85, 1.0)) * (1.0 - 0.3 * t)
        prof.append((max(r, 0.0015) if t < 1 else 0.0015, 0.14 + (L - 0.2) * t))
    base = []
    segs = 16
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    rings = []
    for (r, z) in prof:
        ring = []
        for k in range(segs):
            a = TAU * k / segs
            fl = 1 + 0.14 * (math.cos(a * ribs / 2) ** 2 - 0.5) * (1 if r > 0.006 else 0)
            ring.append(bm.verts.new((r * fl * math.cos(a), r * fl * math.sin(a), z)))
        rings.append(ring)
    for i in range(len(rings) - 1):
        for k in range(segs):
            k2 = (k + 1) % segs
            try:
                fc = bm.faces.new([rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]]); fc.smooth = True
                for l, (ii, kk) in zip(fc.loops, [(i, k), (i, k + 1), (i + 1, k + 1), (i + 1, k)]):
                    l[ul].uv = (kk / segs, ii / n * 3)
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    put(M['linen'], bm, Mx, col=col, uvs=1.0, skip_down=False)
    bm.free()
    cyl(M['wood_dark'], None, 0.007, 0.16, seg=10, Mx=Mx @ Matrix.Translation((0, 0, 0.1)), col=(0.6, 0.5, 0.45))
    # tie strap with button
    cyl(M['leather'], None, 0.033, 0.03, seg=16, r2=0.033, cap=False, Mx=Mx @ Matrix.Translation((0, 0, L * 0.5)), col=(0.25, 0.18, 0.12)) if False else None
    torus(M['leather'], None, 0.036, 0.004, plane='xy', Mx=Mx @ Matrix.Translation((0, 0, 0.14 + (L - 0.22) * 0.55)), seg=16, rseg=4, col=(0.3, 0.2, 0.13))
    # handle: cane crook
    pts = [Mx @ Vector(q) for q in catmull([(0, 0, 0.14), (0, 0, 0.0), (0, 0, -0.1), (0.03, 0, -0.17), (0.09, 0, -0.18), (0.13, 0, -0.14), (0.125, 0, -0.1)], 5)] if False else None
    hp = [(0, 0, 0.14), (0, 0, 0.06), (0, 0, 0.0)] + [(0.045 * (1 - math.cos(a)), 0, -0.045 * math.sin(a) * 0 + 0.0 + 0.0) for a in []]
    arc = [Mx @ Vector((0.05 - 0.05 * math.cos(a), 0, 0.0 + 0.05 * math.sin(a) * 0 - 0.0)) for a in []]
    pts = [Mx @ Vector(q) for q in [(0, 0, 0.16), (0, 0, 0.0)] + [(0.045 - 0.045 * math.cos(a), 0, -0.045 * math.sin(a)) for a in np.linspace(0, math.pi * 0.95, 8)]]
    tube(M['wood_dark'], pts, 0.009, seg=10, col=(0.5, 0.35, 0.25))
    sphere(M['brass'], None, 0.0105, seg=10, Mx=Mx @ Matrix.Translation((0, 0, 0.0)), col=(1, 1, 1)) if False else None


def keys_ring(pos, rot=0):
    """iron key ring with 3 keys hanging (hang from p downward)"""
    p = Vector(pos)
    torus(M['iron'], p, 0.016, 0.0016, plane='xz', seg=16, rseg=4)
    for i, (L, a) in enumerate(((0.07, 0.2), (0.058, -0.15), (0.05, 0.5))):
        d = Vector((math.sin(a), 0, -math.cos(a)))
        base = p + Vector((0, 0, -0.012)) + Vector((0.004 * i - 0.004, 0, 0))
        tube(M['iron'], [base, base + d * L], 0.0028, seg=6)
        torus(M['iron'], base - d * 0.008 + Vector((0, 0, 0.0)), 0.009, 0.0022, plane='xz', Mx=xf(base - d * 0.008, (0, 0, 0)), seg=12, rseg=5) if False else None
        box(M['iron'], base + d * (L - 0.007), (0.016, 0.003, 0.012), bev=0.0005, rot=(0, math.degrees(a), 0))
        box(M['iron'], base + d * (L - 0.011), (0.008, 0.003, 0.004), bev=0)


def envelope(pos, rot=0, col=(0.94, 0.9, 0.78), seal=True, tilt=0.0):
    Mx = xf(pos, (tilt, 0, rot))
    box(M['paper'], None, (0.15, 0.1, 0.0016), Mx=Mx @ Matrix.Translation((0, 0, 0.0008)), bev=0.0003, col=col, g=0, skip_down=False)
    # flap lines + stamp + address scribble
    box(M['paper'], None, (0.075, 0.0006, 0.0005), Mx=Mx @ Matrix.Translation((0, 0.02, 0.0018)), bev=0, col=(0.8, 0.76, 0.66))
    box(M['wool'], None, (0.017, 0.02, 0.0007), Mx=Mx @ Matrix.Translation((0.056, 0.032, 0.0019)), bev=0, col=(0.7, 0.3, 0.25)) if False else box(M['paper'], None, (0.017, 0.02, 0.0007), Mx=Mx @ Matrix.Translation((0.056, 0.032, 0.0019)), bev=0, col=(0.72, 0.3, 0.25))
    for i in range(3):
        box(M['ink'], None, (0.06 - 0.01 * i, 0.002, 0.0004), Mx=Mx @ Matrix.Translation((-0.012, -0.006 - i * 0.012, 0.0018)), bev=0, col=(0.2, 0.17, 0.2))
    if seal:
        cyl(M['wax'], None, 0.009, 0.002, seg=12, Mx=Mx @ Matrix.Translation((0, 0.0, 0.0025)), col=(0.55, 0.12, 0.1))


def flat_ribbon(mat, pts, width, col, up=(0, 0, 1)):
    """flat strip through pts (3D list) facing up; 2 tris per segment"""
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    ring = []
    for i, p in enumerate(pts):
        t = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
        s_ = t.cross(Vector(up))
        if s_.length < 1e-9:
            continue
        s_.normalize()
        ring.append((bm.verts.new(p - s_ * width / 2), bm.verts.new(p + s_ * width / 2)))
    for (a0, a1), (b0, b1) in zip(ring[:-1], ring[1:]):
        try:
            bm.faces.new([a0, b0, b1, a1])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for fc in bm.faces:
        if fc.normal.z < 0:
            fc.normal_flip()
    put(mat, bm, Matrix.Identity(4), col=col, uvs=1.0, skip_down=False)
    bm.free()


def papers_sheet(pos, rot=0, size=(0.21, 0.297), lines=11, seed=0, curl=0.0, col=(0.95, 0.91, 0.8)):
    """a sheet of paper with handwriting-like ink lines"""
    r_ = random.Random(seed)
    Mx = xf(pos, (0, 0, rot))
    w, d = size
    box(M['paper'], None, (w, d, 0.0008), Mx=Mx @ Matrix.Translation((0, 0, 0.0004)), bev=0.0, col=col, g=0, skip_down=False)
    for i in range(lines):
        L = (w - 0.05) * r_.uniform(0.55, 1.0) if i < lines - 1 else (w - 0.05) * 0.4
        y = d / 2 - 0.035 - i * (d - 0.07) / lines
        pts = [Mx @ Vector((-w / 2 + 0.025 + L * t, y + 0.0028 * math.sin(t * 60 + i * 2.1) * math.sin(t * 13 + i), 0.00085)) for t in np.linspace(0, 1, 12)]
        flat_ribbon(M['ink'], pts, 0.0016, (0.16, 0.13, 0.17))
    pts = [Mx @ Vector((w * 0.12 + 0.03 * t, -d / 2 + 0.03 + 0.008 * math.sin(t * 18) * (1 - t), 0.00085)) for t in np.linspace(0, 1, 14)]
    flat_ribbon(M['ink'], pts, 0.0018, (0.1, 0.09, 0.14))


def paint_quad(Mx, w, h, idx):
    """flat quad with bd_painting_<idx> (UV 0..1), facing local +y of Mx"""
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    vv = [bm.verts.new((-w / 2, 0.0, -h / 2)), bm.verts.new((w / 2, 0.0, -h / 2)), bm.verts.new((w / 2, 0.0, h / 2)), bm.verts.new((-w / 2, 0.0, h / 2))]
    fc = bm.faces.new(vv)
    for l, uv in zip(fc.loops, [(1, 0), (0, 0), (0, 1), (1, 1)]):
        l[ul].uv = uv
    bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    put(M['bd_painting_%d' % idx], bm, Mx, uvs=1.0, skip_down=False)
    bm.free()
