"""Individually modelled books + the tall bookshelf."""
from lv_tables import *

BOOK_PAL = [
    ('#7a2f2a', 'leather'), ('#2f4a63', 'cloth'), ('#3d5a3a', 'cloth'), ('#8a6a2e', 'leather'), ('#4a2f4f', 'cloth'), ('#a04b2e', 'leather'),
    ('#2c3f45', 'cloth'), ('#6b5a3c', 'leather'), ('#8c3b3b', 'cloth'), ('#36506b', 'cloth'), ('#5d6b3a', 'cloth'), ('#b08d4a', 'cloth'),
    ('#4b3a2c', 'leather'), ('#7b4b62', 'cloth'), ('#c2b090', 'paper'), ('#2e2e38', 'leather'), ('#9a5b3a', 'leather'), ('#3e6a66', 'cloth'),
    ('#5a2a22', 'leather'), ('#d4c8a8', 'paper'), ('#1f2f4a', 'cloth'), ('#6a3a2a', 'leather'), ('#4a5a30', 'cloth'), ('#8b7a5a', 'cloth'),
]
BOOK_N = [0]


def book_cover_bm(w, d, h, tc, rs):
    """C-shaped cover prism along z (spine at +y)."""
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    outer = [(-w / 2, -d / 2), (-w / 2, d / 2 - rs)]
    for i in range(1, 5):
        a = math.pi - math.pi * i / 5
        outer.append((w / 2 * math.cos(a), d / 2 - rs + rs * math.sin(a) * 1.0))
    outer += [(w / 2, d / 2 - rs), (w / 2, -d / 2)]
    inner = [(w / 2 - tc, -d / 2), (w / 2 - tc, d / 2 - rs - 0.0004)]
    for i in range(1, 5):
        a = i * math.pi / 5
        inner.append(((w / 2 - tc) * math.cos(a), d / 2 - rs - 0.0004 + (rs - tc * 0.8) * math.sin(a)))
    inner += [(-w / 2 + tc, d / 2 - rs - 0.0004), (-w / 2 + tc, -d / 2)]
    loop = outer + inner
    n = len(loop)
    b = [bm.verts.new((x, y, 0)) for (x, y) in loop]
    t = [bm.verts.new((x, y, h)) for (x, y) in loop]
    # perimeter distance for uv
    dist = [0.0]
    for i in range(1, n + 1):
        x0, y0 = loop[(i - 1) % n]; x1, y1 = loop[i % n]
        dist.append(dist[-1] + math.hypot(x1 - x0, y1 - y0))
    for i in range(n):
        j = (i + 1) % n
        try:
            f = bm.faces.new([b[i], b[j], t[j], t[i]])
        except ValueError:
            continue
        f.smooth = True
        for l, uv in zip(f.loops, [(dist[i], 0), (dist[i + 1], 0), (dist[i + 1], h), (dist[i], h)]):
            l[ul].uv = uv
    try:
        bm.faces.new(b[::-1])
        bm.faces.new(t)
    except ValueError:
        pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def spine_strip(mat, M0, w, d, rs, z, hh, frac, col, off=0.0005, skirt=False, n=4):
    """curved ribbon hugging the rounded spine: decal (off ~0.5mm) or raised band (off ~1.2mm + side skirts)."""
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    xs = [(-0.5 + i / n) * w * frac for i in range(n + 1)]
    def yy(x, o):
        k = clamp(x / (w / 2), -1.0, 1.0)
        return d / 2 - rs + rs * math.sqrt(max(0.0, 1 - k * k)) + o
    bot = [bm.verts.new((x, yy(x, off), z - hh / 2)) for x in xs]
    top = [bm.verts.new((x, yy(x, off), z + hh / 2)) for x in xs]
    for i in range(n):
        f = bm.faces.new([bot[i], top[i], top[i + 1], bot[i + 1]])
        f.smooth = True
        for l, uv in zip(f.loops, [(i / n, 0), (i / n, 1), ((i + 1) / n, 1), ((i + 1) / n, 0)]):
            l[ul].uv = (uv[0] * w, uv[1] * hh)
    if skirt:
        b0 = [bm.verts.new((x, yy(x, -0.0005), z - hh / 2)) for x in xs]
        t0 = [bm.verts.new((x, yy(x, -0.0005), z + hh / 2)) for x in xs]
        for i in range(n):
            bm.faces.new([bot[i + 1], b0[i + 1], b0[i], bot[i]])
            bm.faces.new([top[i], t0[i], t0[i + 1], top[i + 1]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    put(mat, bm, M0, col, None, 1, uv_abs=True)
    bm.free()


def book(M0, w, d, h, col, kind='cloth', rr=None, title=True, seed=0, worn=0.0):
    """closed book with spine at local +y, origin bottom centre. M0 world matrix."""
    rr = rr or random.Random(seed)
    BOOK_N[0] += 1
    c = C(col)
    tc = 0.0022 if d > 0.12 else 0.0014
    rs = min(0.010, w * 0.42)
    mat = M['leather'] if kind == 'leather' else (M['paper'] if kind == 'paper' else M['book_cloth'])
    cm = (0.92 + 0.14 * rr.random())
    Mi = M0.inverted()
    sd = rr.random() * 20

    def ccf(p):
        lp = Mi @ p
        e = min(lp.z, h - lp.z) / max(h, 0.01)
        edge = 1.0 + 0.22 * worn * math.exp(-e * 60) + 0.12 * worn * math.exp(-(lp.y - d / 2 + rs) ** 2 * 3000)
        k = cm * edge * (1 + 0.07 * nz(lp.x * 60, lp.y * 30, lp.z * 20, 1.0, int(sd)))
        return (c[0] * k, c[1] * k, c[2] * k)
    bm = book_cover_bm(w, d, h, tc, rs)
    put(mat, bm, M0, c, ccf, 2)
    bm.free()
    # page block (cream, inset)
    pw = w - 2 * tc - 0.0008
    pd = d - 0.005 - rs
    hh = h - 0.004
    pc = (0.86, 0.82, 0.7) if kind != 'paper' else (0.9, 0.86, 0.76)
    box(M['paper'], None, (pw, pd, hh), M=M0 @ Matrix.Translation((0, -d / 2 + 0.003 + pd / 2, 0.002 + hh / 2)), bev=0.0, col=pc, cfn=lambda p: shade(pc, 0.95 + 0.08 * nz(p.x * 300, p.y * 300, p.z * 300)))
    if kind == 'paper' or w < 0.009:
        return
    ys = d / 2 + 0.0004
    gil = (1, 1, 1)
    # spine decoration
    if kind == 'leather' and h > 0.15 and w > 0.018:
        nb = rr.choice([3, 4, 5]) if h > 0.22 else 3
        zs = [h * (0.1 + 0.8 * (i + 0.5) / nb) for i in range(nb)]
        zs = [0.0, ] + zs if False else zs
        band_c = shade(c, 1.12)
        bz = []
        for i in range(nb + 1):
            z = h * (0.08 + 0.84 * i / nb)
            bz.append(z)
            spine_strip(mat, M0, w, d, rs, z, 0.0034, 1.0, band_c, off=0.0011, skirt=True)
            spine_strip(M['gilt'], M0, w, d, rs, z + 0.0034, 0.0008, 0.84, gil, off=0.0006)
        # title label between bands 1-2
        if title and nb >= 3:
            z0 = bz[1]; z1 = bz[2]
            lh = (z1 - z0) - 0.01
            lc = shade(C(rr.choice(['#6a1f1a', '#1c2d3a', '#14301f', '#24201c'])), 1.0)
            spine_strip(mat, M0, w, d, rs, (z0 + z1) / 2, lh, 0.8, lc, off=0.0008)
            for k in range(2):
                tw_ = (0.5 - 0.12 * k) * (0.7 + 0.3 * rr.random())
                spine_strip(M['gilt'], M0, w, d, rs, (z0 + z1) / 2 + (0.5 - k) * lh * 0.35, 0.0018, tw_, gil, off=0.0013, n=2)
        # fleurons
        for i in range(nb):
            if i == 1 and title:
                continue
            z = (bz[i] + bz[i + 1]) / 2
            spine_strip(M['gilt'], M0, w, d, rs, z, 0.0026, 0.26, gil, off=0.0006, n=2)
    else:
        # cloth: gilt lines near head/tail + paper label
        for z in (h * 0.07, h * 0.93):
            spine_strip(M['gilt'], M0, w, d, rs, z, 0.0012, 0.86, gil, off=0.0006)
        if title:
            lh = min(0.07, h * 0.3)
            zc = h * (0.55 + 0.25 * rr.random())
            lc = (0.88, 0.82, 0.66) if rr.random() < 0.6 else shade(c, 0.5)
            spine_strip(M['paper'], M0, w, d, rs, zc, lh, 0.8, lc, off=0.0007)
            tcol = (0.12, 0.1, 0.09) if lc[0] > 0.6 else (0.95, 0.8, 0.45)
            for k in range(2 if lh > 0.04 else 1):
                tw_ = w * (0.55 - 0.15 * k) * (0.7 + 0.3 * rr.random())
                spine_strip(M['ink'] if lc[0] > 0.6 else M['gilt'], M0, w, d, rs, zc + (0.25 - 0.5 * k) * lh * 0.5, 0.0017, tw_ / w, tcol, off=0.0011, n=2)
        # embossed raised bands on thick cloth spines
        if w > 0.03:
            spine_strip(mat, M0, w, d, rs, h * 0.2, 0.002, 1.0, shade(c, 1.1), off=0.0008, skirt=True)
            spine_strip(mat, M0, w, d, rs, h * 0.8, 0.002, 1.0, shade(c, 1.1), off=0.0008, skirt=True)


def book_flat_stack(base, n, rr, W0=0.22, maxh=0.3, rot=0.0, cols=None):
    """horizontal stack of books, spines facing +y.  base = world matrix at stack centre bottom."""
    z = 0.0
    tops = []
    for k in range(n):
        h = rr.uniform(0.17, min(0.28, W0 + 0.05))
        w = rr.uniform(0.02, 0.05)
        d = rr.uniform(0.14, 0.21)
        col, kind = rr.choice(BOOK_PAL)
        if cols:
            col = cols[k % len(cols)]
        off = rr.uniform(-0.012, 0.012)
        rz = rr.uniform(-5, 5) + rot
        # flat: local z (height) along x, local x (thickness) vertical (-z)
        Mb = base @ Matrix.Translation((off, rr.uniform(-0.008, 0.008), z + w)) @ rotm((0, 0, rz)) @ rotm((0, 90, 0)) @ Matrix.Translation((0, 0, -h / 2))
        book(Mb, w, d, h, col, kind, rr, worn=0.7)
        z += w + 0.001
    return z


def bookshelf(pos, rot, W=1.3, D=0.32, H=2.2, seed=5):
    rr = random.Random(seed)
    f = Fr(pos, rot, F_)
    mat = M['wood_dark']
    vc = wood_vc((0.38, 0.24, 0.15), 0.18, 7, 31, axis=2)
    vch = wood_vc((0.4, 0.26, 0.16), 0.18, 7, 33, axis=0)
    t = 0.022
    # sides with face frame
    for s in (-1, 1):
        f.box(mat, (s * (W / 2 - t / 2), 0, H / 2), (t, D, H), bev=0.0035, cfn=vc, g=2, cuts=3)
        f.box(mat, (s * (W / 2 - 0.02), D / 2 - 0.006, H / 2 - 0.05), (0.04, 0.012, H - 0.12), bev=0.0025, cfn=vc, g=2)
        f.tube(mat, [V(s * (W / 2 - 0.037), D / 2 + 0.001, 0.13), V(s * (W / 2 - 0.037), D / 2 + 0.001, H - 0.17)], 0.0035, seg=6, col=(0.36, 0.22, 0.14))
    # back boards (vertical planks with V-groove)
    nb = 9
    bwid = (W - 2 * t) / nb
    for i in range(nb):
        f.box(M['wood_walnut'], (-W / 2 + t + bwid * (i + 0.5), -D / 2 + 0.008, H / 2), (bwid - 0.0015, 0.014, H - 0.02), bev=0.0015, cfn=wood_vc((0.3, 0.19, 0.12), 0.2, 7, 40 + i, axis=2), g=2)
    # top: cornice crown moulding + top slab
    f.box(mat, (0, 0, H - 0.02), (W + 0.02, D, 0.04), bev=0.003, cfn=vch, g=0, cuts=3)
    moulding(mat, f.M @ Matrix.Translation((0, 0, H - 0.075)), rrect(W + 0.045, D + 0.045, 0.004, 1),
             [(-0.02, 0.0), (-0.004, 0.0), (0.0, 0.006), (0.006, 0.012), (0.012, 0.016), (0.019, 0.02), (0.022, 0.03), (0.022, 0.041), (0.012, 0.047), (-0.004, 0.047), (-0.02, 0.05)], cfn=vch, g=0)
    f.box(mat, (0, D / 2 - 0.03, H - 0.035), (W - 0.06, 0.012, 0.045), bev=0.002, cfn=vch, g=0)
    # dentils under crown
    # dentils: ARRAY modifier over a single block
    db = bmesh.new()
    bmesh.ops.create_cube(db, size=1.0)
    for v in db.verts:
        v.co = Vector((v.co.x * 0.015, v.co.y * 0.012, v.co.z * 0.014))
    db = modbm(db, [('ARRAY', dict(count=int((W - 0.1) / 0.03), relative_offset_displace=(2.0, 0, 0), use_relative_offset=True))])
    put(mat, db, f.M @ Matrix.Translation((-W / 2 + 0.06, D / 2 + 0.012, H - 0.088)), (0.42, 0.27, 0.17), None, 0)
    db.free()
    # plinth with moulding
    f.box(mat, (0, D / 2 - 0.015, 0.06), (W, 0.03, 0.11), bev=0.003, cfn=vch, g=0)
    moulding(mat, f.M @ Matrix.Translation((0, 0, 0.1)), rrect(W + 0.03, D + 0.03, 0.004, 1), [(-0.015, 0.0), (0.0, 0.0), (0.006, 0.005), (0.009, 0.014), (0.002, 0.02), (-0.015, 0.022)], cfn=vch, g=0)
    f.box(mat, (0, 0.0, 0.03), (W - 2 * t, D - 0.03, 0.04), bev=0.003, col=(0.4, 0.25, 0.16), g=0)
    # bracket feet
    for s in (-1, 1):
        f.box(mat, (s * (W / 2 - 0.05), D / 2 - 0.02, 0.012), (0.12, 0.05, 0.024), bev=0.003, col=(0.4, 0.25, 0.16))
    levels = [0.12, 0.47, 0.81, 1.15, 1.49, 1.83]
    tops = levels[1:] + [H - 0.04]
    for i, z in enumerate(levels):
        if i > 0:
            f.box(mat, (0, -0.005, z - 0.011), (W - 2 * t, D - 0.03, 0.022), bev=0.002, cfn=vch, g=0, cuts=3)
            f.box(mat, (0, D / 2 - 0.0225, z - 0.011), (W - 2 * t, 0.012, 0.03), bev=0.003, cfn=vch, g=0)
            f.tube(mat, [V(-W / 2 + t, D / 2 - 0.014, z + 0.001), V(W / 2 - t, D / 2 - 0.014, z + 0.001)], 0.0032, seg=6, col=(0.4, 0.25, 0.16))
            for s in (-1, 1):
                for yy in (-D / 2 + 0.05, D / 2 - 0.05):
                    f.cyl(M['brass'], (s * (W / 2 - t - 0.003), yy, z - 0.03), 0.0035, 0.007, axis='x', seg=6)
    # ---------------------------------------------------------------- contents
    nbooks = 0
    curios = ['jar', 'frame', 'globe', 'vase', 'candle', 'bird', 'plant', 'bowl', 'shells', 'bottle', 'box']
    shelf_plan = {0: 'folio', 1: 'mix', 2: 'mix', 3: 'curio', 4: 'mix', 5: 'mix'}
    for i, z in enumerate(levels):
        zb = z
        clear = tops[i] - z - 0.03
        x = -W / 2 + t + 0.004
        x_end = W / 2 - t - 0.004
        mode = shelf_plan[i]
        used_curio = 0
        guard = 0
        while x < x_end - 0.03 and guard < 60:
            guard += 1
            roll = rr.random()
            room_left = x_end - x
            if mode == 'curio' and used_curio < 2 and roll < 0.22 and room_left > 0.22:
                used_curio += 1
                kind = rr.choice(curios)
                x += place_curio(f, kind, x, zb, clear, rr, i)
                continue
            if roll < 0.07 and room_left > 0.3 and mode != 'folio':
                # horizontal stack with an object on top
                n = rr.randint(2, 5)
                zz_top = book_flat_stack(f.M @ Matrix.Translation((x + 0.14, rr.uniform(-0.01, 0.01), zb)), n, rr, rot=rr.uniform(-4, 4) + 0)
                nbooks += n
                if zz_top < clear - 0.1:
                    ok = rr.choice(['jar', 'bird', 'candle', 'shells'])
                    place_curio(f, ok, x + 0.06, zb + zz_top, clear - zz_top, rr, i, cx_off=0.04)
                x += 0.31
                continue
            nrun = rr.randint(10, 24) if mode != 'folio' else rr.randint(3, 6)
            lean_end = rr.random() < 0.4 and room_left > 0.3
            set_h = rr.uniform(0.2, min(0.31, clear - 0.012)) if mode != 'folio' else rr.uniform(0.28, clear - 0.01)
            set_d = rr.uniform(0.17, 0.25)
            col0, kind0 = rr.choice(BOOK_PAL)
            same = rr.random() < 0.35
            run_x0 = x
            run_h = 0.0
            for k in range(nrun):
                w = rr.uniform(0.010, 0.030) if mode != 'folio' else rr.uniform(0.035, 0.06)
                if x + w > x_end - (0.1 if (lean_end and k == nrun - 1) else 0.0):
                    break
                h = clamp(set_h * rr.uniform(0.85, 1.07), 0.15, clear - 0.012)
                d = clamp(set_d * rr.uniform(0.88, 1.08), 0.14, 0.27)
                col, kind = (col0, kind0) if same and rr.random() < 0.8 else rr.choice(BOOK_PAL)
                col = jit(C(col), 0.1)
                yfront = D / 2 - 0.012 - rr.uniform(0.0, 0.02)
                Mb = f.M @ Matrix.Translation((x + w / 2, yfront - d / 2, zb)) @ rotm((0, 0, rr.uniform(-1.2, 1.2)))
                # occasionally a book slightly pulled out / tilted
                if rr.random() < 0.05:
                    Mb = Mb @ rotm((rr.uniform(-2, 2), 0, 0)) @ Matrix.Translation((0, 0.012, 0))
                book(Mb, w, d, h, col, kind, rr, title=(w > 0.019), worn=rr.uniform(0.2, 1.0))
                nbooks += 1
                run_h = max(run_h, h)
                x += w + 0.0008
            # flat books laid on top of a short run
            if run_h > 0 and clear - run_h > 0.05 and (x - run_x0) > 0.12 and rr.random() < 0.6:
                nfl = rr.randint(1, 2)
                book_flat_stack(f.M @ Matrix.Translation(((run_x0 + x) / 2, rr.uniform(-0.01, 0.01), zb + run_h)), nfl, rr, W0=0.2, rot=rr.uniform(-5, 5))
                nbooks += nfl
            if lean_end:
                # books leaning against the last upright book
                nl = rr.randint(1, 3)
                ang = rr.uniform(9, 24)
                for k in range(nl):
                    w = rr.uniform(0.022, 0.04); h = clamp(set_h * rr.uniform(0.9, 1.03), 0.16, clear - 0.015); d = clamp(set_d, 0.14, 0.26)
                    col, kind = rr.choice(BOOK_PAL)
                    yfront = D / 2 - 0.014
                    Mb = f.M @ Matrix.Translation((x + 0.0, yfront - d / 2, zb)) @ rotm((0, -ang, 0)) @ Matrix.Translation((w / 2 + 0.0, 0, 0))
                    # pivot at bottom-left corner
                    Mb = f.M @ Matrix.Translation((x + w * math.cos(math.radians(ang)) * 0.0, yfront - d / 2, zb)) @ rotm((0, -ang, 0)) @ Matrix.Translation((w / 2, 0, 0))
                    book(Mb, w, d, h, jit(C(col), 0.1), kind, rr, title=True, worn=0.8)
                    nbooks += 1
                    x += w * 0.95 / max(1, nl) * 0.0 + (h * math.sin(math.radians(ang)) + w) / nl * 0.9
            x += rr.uniform(0.0, 0.02)
    # items on top of the bookcase
    place_curio(f, 'vase', -0.42, H + 0.0, 0.3, rr, 6, ztop=True)
    place_curio(f, 'frame', -0.05, H + 0.0, 0.3, rr, 6, ztop=True)
    place_curio(f, 'jar', 0.3, H + 0.0, 0.3, rr, 6, ztop=True)
    zz = book_flat_stack(f.M @ Matrix.Translation((0.5, -0.02, H)), 4, rr, rot=8)
    collider_f(f, W, D + 0.05, F_ + H)
    return f, nbooks


def place_curio(f, kind, x, zb, clear, rr, shelf, cx_off=0.0, ztop=False):
    """returns consumed width"""
    zbase = zb
    y = 0.02
    q = f.p(V(x + 0.07 + cx_off, y, 0.0))
    q.z = F_ + zbase + 0.0 + (0.0 if not ztop else 0.0)
    if ztop:
        q = f.p(V(x, y, 0.0)); q.z = F_ + zb
    w = 0.14
    r_ = f.rot
    if kind == 'jar':
        col = rr.choice([(0.85, 0.5, 0.2), (0.6, 0.15, 0.1), (0.4, 0.6, 0.2), (0.8, 0.7, 0.3)])
        jar(q, r=0.045, h=min(0.16, clear - 0.04), content=(0.75, col), lidcol=(0.75, 0.6, 0.3))
        w = 0.12
    elif kind == 'frame':
        photo_frame(q, r_, w=0.13, h=0.17, tilt=10, seed=rr.randint(0, 99), fcol=rr.choice([(0.55, 0.38, 0.25), (0.8, 0.65, 0.35), (0.35, 0.25, 0.2)]), fmat='wood_dark')
        w = 0.15
    elif kind == 'globe':
        if clear > 0.25:
            globe(q, 0.06 if clear > 0.28 else 0.05)
        else:
            bowl(q, 0.07, 0.04)
        w = 0.17
    elif kind == 'vase':
        vase_dried(q, h=min(0.17, clear * 0.42), r=0.042, seed=rr.randint(0, 99), vcol=rr.choice(['#b5562f', '#3e6a66', '#d9c7a0', '#4a5f8a']), stems=9 if not ztop else 14)
        w = 0.16
    elif kind == 'candle':
        candlestick(q, h=0.12, kind='brass', cl=0.1, lit=False, wax=True, seed=rr.randint(0, 99))
        w = 0.12
    elif kind == 'bird':
        figurine_bird(q, r_ + rr.uniform(-20, 20), col=rr.choice(['#c8b080', '#8aa0b0', '#b07050']))
        w = 0.1
    elif kind == 'plant':
        bowl(q, 0.055, 0.075, mat='terracotta', col=(0.85, 0.5, 0.35))
        for k in range(10):
            a = rr.uniform(0, TAU)
            tube(M['foliage'], [q + V(0, 0, 0.07), q + V(math.cos(a) * 0.04, math.sin(a) * 0.04, 0.12 + rr.random() * 0.03), q + V(math.cos(a) * 0.09, math.sin(a) * 0.09, 0.09 + rr.random() * 0.05)], 0.0018, 4, col=(0.25, 0.45, 0.2), caps=False)
            lathe(M['foliage'], q + V(math.cos(a) * 0.09, math.sin(a) * 0.09, 0.09), [(0.001, 0), (0.012, 0.008), (0.001, 0.028)], seg=4, cap=False, col=(0.22, 0.45, 0.18), rot=(80, 0, math.degrees(a)))
        w = 0.14
    elif kind == 'bowl':
        bowl(q, 0.075, 0.045, col=C(rr.choice(['#4e7299', '#b5562f', '#d9c7a0'])))
        for k in range(5):
            sphere(M['foliage'], q + V(rr.uniform(-0.03, 0.03), rr.uniform(-0.03, 0.03), 0.032), 0.012, seg=6, rings=4, col=(0.5, 0.35, 0.2))
        w = 0.18
    elif kind == 'shells':
        for k in range(3):
            lathe(M['ceramic'], q + V(0.03 * k - 0.03, rr.uniform(-0.02, 0.02), 0.0), [(0.001, 0), (0.025, 0.0), (0.03, 0.012), (0.016, 0.026), (0.001, 0.03)], seg=12, cap=False, col=(0.95, 0.88, 0.8), rot=(0, 0, rr.uniform(0, 360)), scale=(1, 0.8, 0.9))
        w = 0.12
    elif kind == 'bottle':
        bottle(q, r=0.03, h=min(0.22, clear - 0.03), col=(0.35, 0.18, 0.08))
        w = 0.1
    elif kind == 'box':
        box(M['wood_oak'], None, (0.13, 0.1, 0.07), M=Matrix.Translation(q + V(0, 0, 0.035)) @ rotm((0, 0, r_ + rr.uniform(-10, 10))), bev=0.003, col=(0.6, 0.4, 0.25))
        box(M['brass'], None, (0.02, 0.003, 0.014), M=Matrix.Translation(q + V(0, 0, 0.056)) @ rotm((0, 0, r_ + 0)) @ Matrix.Translation((0, 0.05, 0)), bev=0.0006)
        w = 0.15
    return w
