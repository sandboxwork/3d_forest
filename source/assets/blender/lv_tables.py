"""Coffee table, side table, newspaper, knitting basket."""
from lv_seat import *


def wood_vc(base, amp=0.12, s=7.0, seed=0, axis=0, streak=0.12):
    b = C(base)
    def f(p):
        sc = [0.25, 0.25, 0.25]
        sc[axis] = 0.03
        t = fbm(p.x * sc[0] * 4, p.y * sc[1] * 4, p.z * sc[2] * 4, s, seed, 3)
        t2 = nz(p.x * 90 * (1 if axis != 0 else 0.1), p.y * 90 * (1 if axis != 1 else 0.1), p.z * 90 * (1 if axis != 2 else 0.1), 1.0, seed + 5)
        k = 1 + amp * t + streak * t2
        return (b[0] * k, b[1] * k * (1 + 0.01 * t), b[2] * k * (1 + 0.02 * t))
    return f


def turned_profile_leg(f, x, y, z0, h, r, mat, vc, style='baluster', seg=18):
    s = h
    if style == 'baluster':
        pr = [(r * 0.55, 0.0), (r * 0.6, 0.02 * s), (r * 0.5, 0.06 * s), (r * 0.58, 0.12 * s), (r * 0.82, 0.22 * s), (r * 0.9, 0.3 * s), (r * 0.7, 0.4 * s), (r * 0.48, 0.5 * s),
              (r * 0.62, 0.55 * s), (r * 0.48, 0.6 * s), (r * 0.55, 0.78 * s), (r * 0.75, 0.84 * s), (r * 0.78, 0.9 * s), (r, 0.93 * s), (r, s)]
    else:
        pr = [(r * 0.45, 0.0), (r * 0.55, 0.1 * s), (r * 0.7, 0.5 * s), (r * 0.8, 0.8 * s), (r, 0.84 * s), (r, s)]
    f.lathe(M[mat], (x, y, z0), pr, seg=seg, cfn=vc)


def ring_pull(M0, mat='brass', r=0.014):
    tube(M[mat], [M0 @ V(r * math.cos(a), 0.0, -r * 0.4 + r * math.sin(a)) for a in [i * TAU / 20 + math.pi * 0.55 for i in range(16)]], 0.0018, seg=5, caps=False)
    lathe(M[mat], None, [(0.001, 0.0), (0.01, 0.0), (0.012, 0.002), (0.009, 0.005), (0.004, 0.007), (0.001, 0.0075)], seg=14, M=M0 @ rotm((90, 0, 0)) @ Matrix.Translation((0, 0, -0.0)), cap=False)


def coffee_table(pos, rot=90):
    f = Fr(pos, rot, F_)
    W, D, H = 0.95, 0.52, 0.42
    vc = wood_vc((0.42, 0.26, 0.16), 0.16, 8, 4, axis=0)
    vc2 = wood_vc((0.46, 0.29, 0.18), 0.14, 8, 7, axis=1)
    mat = M['wood_walnut']
    # legs + corner blocks
    for sx in (-1, 1):
        for sy in (-1, 1):
            x = sx * (W / 2 - 0.045); y = sy * (D / 2 - 0.045)
            turned_profile_leg(f, x, y, 0.0, 0.34, 0.026, 'wood_walnut', vc2, 'baluster')
            f.box(mat, (x, y, 0.345), (0.05, 0.05, 0.09), bev=0.003, cfn=vc2, g=2)
            f.cyl(M['brass'], (x, y, 0.0075), 0.0145, 0.015, seg=14)
    # top: plate + ogee edge moulding
    f.box(mat, (0, 0, H - 0.016), (W - 0.018, D - 0.018, 0.03), bev=0.0, cfn=vc, g=0, cuts=4)
    path = rrect(W, D, 0.03, 5)
    moulding(mat, f.M @ Matrix.Translation((0, 0, H - 0.032)), path, [(-0.009, 0.0), (-0.002, 0.0), (0.004, 0.004), (0.0058, 0.011), (0.004, 0.018), (0.0, 0.0225), (-0.004, 0.028), (-0.009, 0.031)], cfn=vc, g=0)
    # oak inlay border + centre line
    moulding(M['wood_oak'], f.M @ Matrix.Translation((0, 0, H + 0.0004)), rrect(W - 0.1, D - 0.1, 0.012, 4), [(0.0, 0.0), (0.0, 0.0012), (0.007, 0.0012), (0.007, 0.0)], col=(0.62, 0.45, 0.28), g=0)
    moulding(M['wood_oak'], f.M @ Matrix.Translation((0, 0, H + 0.0004)), rrect(W - 0.2, D - 0.2, 0.008, 3), [(0.0, 0.0), (0.0, 0.0012), (0.003, 0.0012), (0.003, 0.0)], col=(0.62, 0.45, 0.28), g=0)
    # aprons
    for sy in (-1, 1):
        f.box(mat, (0, sy * (D / 2 - 0.047), H - 0.07), (W - 0.1, 0.016, 0.07), bev=0.0025, cfn=vc, g=0)
        f.tube(mat, [V(-W / 2 + 0.07, sy * (D / 2 - 0.036), H - 0.108), V(W / 2 - 0.07, sy * (D / 2 - 0.036), H - 0.108)], 0.0045, seg=6, col=(0.45, 0.28, 0.17))
    for sx in (-1, 1):
        f.box(mat, (sx * (W / 2 - 0.047), 0, H - 0.07), (0.016, D - 0.1, 0.07), bev=0.0025, cfn=vc2, g=1)
        f.tube(mat, [V(sx * (W / 2 - 0.036), -D / 2 + 0.07, H - 0.108), V(sx * (W / 2 - 0.036), D / 2 - 0.07, H - 0.108)], 0.0045, seg=6, col=(0.45, 0.28, 0.17))
    # drawer on the long side facing +y (towards the sofa-side of the room as placed)
    for sy in (-1,):
        dz = H - 0.07
        f.box(mat, (0, sy * (D / 2 - 0.036), dz), (0.32, 0.006, 0.058), bev=0.0015, cfn=vc, g=0)
        moulding(M['wood_oak'], f.M @ Matrix.Translation((0, sy * (D / 2 - 0.032), dz)) @ rotm((90, 0, 0)), rrect(0.27, 0.042, 0.004, 2), [(0.0, 0.0), (0.0, 0.0012), (0.004, 0.0012), (0.004, 0.0)], col=(0.62, 0.45, 0.28), g=2)
        ring_pull(f.M @ Matrix.Translation((0, sy * (D / 2 - 0.025), dz + 0.0)) @ rotm((0, 0, 0)))
        # keyhole escutcheon
        f.box(M['brass'], (0.1, sy * (D / 2 - 0.0325), dz), (0.012, 0.0015, 0.016), bev=0.0004)
        f.box(M['ink'], (0.1, sy * (D / 2 - 0.0338), dz), (0.003, 0.0005, 0.008), bev=0)
    # lower shelf with moulded edge + turned gallery posts
    f.box(mat, (0, 0, 0.125), (W - 0.1, D - 0.09, 0.02), bev=0.003, cfn=vc, g=0, cuts=3)
    moulding(mat, f.M @ Matrix.Translation((0, 0, 0.115)), rrect(W - 0.1, D - 0.09, 0.015, 4), [(-0.008, 0.0), (-0.001, 0.0), (0.003, 0.005), (0.0015, 0.015), (-0.008, 0.02)], cfn=vc, g=0)
    for sx in (-1, 1):
        for k in range(4):
            y = -D / 2 + 0.16 + k * 0.066
            f.lathe(mat, (sx * (W / 2 - 0.1), y, 0.135), [(0.004, 0.0), (0.006, 0.01), (0.0045, 0.02), (0.007, 0.03), (0.004, 0.045)], seg=8, col=(0.45, 0.28, 0.17))
        f.box(mat, (sx * (W / 2 - 0.1), 0, 0.184), (0.012, D - 0.2, 0.01), bev=0.002, col=(0.45, 0.28, 0.17), g=1)
    collider_f(f, W, D, F_ + H)
    return f


def side_table(pos, r=0.22, h=0.58):
    f = Fr(pos, 0, F_)
    vc = wood_vc((0.55, 0.36, 0.2), 0.15, 8, 21, axis=2)
    mat = M['wood_oak']
    # top: lathe-turned with beaded edge
    pr = [(0.001, h - 0.03), (r - 0.012, h - 0.03), (r - 0.004, h - 0.026), (r, h - 0.02), (r + 0.0015, h - 0.013), (r, h - 0.006), (r - 0.003, h - 0.001), (r - 0.012, h), (0.001, h)]
    f.lathe(mat, (0, 0, 0), pr, seg=40, cfn=vc, cap=False)
    # frieze + beaded ring under top
    f.lathe(mat, (0, 0, 0), [(0.001, h - 0.03), (r * 0.5, h - 0.03), (r * 0.5, h - 0.05), (r * 0.42, h - 0.052), (0.001, h - 0.052)], seg=24, cfn=vc, cap=False)
    # pedestal column
    col = [(0.045, 0.15), (0.05, 0.16), (0.036, 0.2), (0.024, 0.24), (0.02, 0.27), (0.03, 0.29), (0.032, 0.31), (0.02, 0.335), (0.026, 0.37), (0.044, 0.41), (0.05, 0.43), (0.038, 0.45), (0.034, 0.5), (0.04, 0.53), (0.046, h - 0.05)]
    f.lathe(mat, (0, 0, 0), col, seg=24, cfn=vc)
    # three cabriole legs
    for i in range(3):
        a = i * TAU / 3 + 0.5
        pts = []
        N = 12
        for k in range(N + 1):
            t = k / N
            z = 0.2 * (1 - t) + 0.0
            rad_ = 0.035 + 0.13 * (math.sin(t * math.pi * 0.5) ** 1.4) * (1 + 0.1 * t) - 0.02 * t * t
            rad_ = 0.045 + 0.15 * (t ** 0.8) - 0.04 * math.sin(t * math.pi) * 0.5
            pts.append(V(math.cos(a) * rad_, math.sin(a) * rad_, 0.2 * (1 - t) * 1.0 + 0.012 * t))
        rads = [0.022 * (1 - 0.55 * math.sin(min(1, k / N * 1.2) * math.pi * 0.6)) + 0.004 for k in range(N + 1)]
        tube_f(f, M['wood_oak'], pts, rads, 10, (0.55, 0.36, 0.2))
        e = pts[-1]
        f.lathe(M['wood_oak'], (e.x, e.y, 0.0), [(0.001, 0.0), (0.016, 0.0), (0.019, 0.004), (0.014, 0.012), (0.01, 0.02)], seg=10, col=(0.55, 0.36, 0.2))
        f.cyl(M['brass'], (e.x, e.y, 0.005), 0.0165, 0.01, seg=12)
    f.cyl(M['brass'], (0, 0, 0.162), 0.054, 0.012, seg=20)
    # doily (scalloped)
    bm = bmesh.new()
    NA, NR = 40, 5
    ctr = bm.verts.new((0, 0, 0))
    rings = []
    for i in range(1, NR + 1):
        t = i / NR
        row = []
        for j in range(NA):
            a = j / NA * TAU
            Rr = 0.13 * (1 + 0.06 * math.cos(a * 14) * (t ** 3)) * t
            row.append(bm.verts.new((Rr * math.cos(a), Rr * math.sin(a), 0.0012 * math.sin(t * 9) + 0.0006 * t)))
        rings.append(row)
    for j in range(NA):
        k = (j + 1) % NA
        bm.faces.new([ctr, rings[0][j], rings[0][k]])
    for i in range(NR - 1):
        for j in range(NA):
            k = (j + 1) % NA
            bm.faces.new([rings[i][j], rings[i + 1][j], rings[i + 1][k], rings[i][k]])
    def lace(p):
        l = p - f.p(V(0, 0, h))
        rr = math.hypot(l.x, l.y)
        a = math.atan2(l.y, l.x)
        k = 0.9 + 0.12 * (math.sin(rr * 160) > 0.3) + 0.08 * (math.cos(a * 14) * (rr > 0.09) > 0.5)
        return (0.92 * k, 0.9 * k, 0.84 * k)
    put(M['fabric_linen'], bm, Matrix.Translation(f.p(V(0, 0, h + 0.0005))), (1, 1, 1), lace, 2)
    bm.free()
    collider_f(f, 2 * r, 2 * r, F_ + h)
    return f


def newspaper(M0, w=0.26, d=0.38, nsheets=4, seed=2, folded=True):
    """folded newspaper: stacked curved sheets; the top sheet carries the printed texture"""
    rr = random.Random(seed)
    tx = tex_mat('news', 'lv_news', '#e6ddc8', 0.95)
    for k in range(nsheets):
        top = (k == nsheets - 1)
        ph = rr.uniform(0, 6)
        ox = rr.uniform(-0.006, 0.006); oy = rr.uniform(-0.01, 0.01); rz = rr.uniform(-2, 2)
        def zf(x, v, k=k, ph=ph):
            u = x / w
            crease = 0.004 * math.exp(-((u - 0.5) / 0.04) ** 2) if folded else 0
            curl = 0.006 * (abs(u - 0.5) * 2) ** 2.0
            return 0.0007 * k + 0.0012 * k + crease + curl * 0.7 + 0.0012 * math.sin(v * 4 + ph + u * 3)
        bm = page_surface(w, d, zf, 12, 8)
        for v in bm.verts:
            v.co.x -= w / 2
        MM = M0 @ Matrix.Translation((ox, oy, 0.001)) @ rotm((0, 0, rz))
        if top:
            put(tx, bm, MM, (1, 1, 1), uv_abs=True)
        else:
            put(M['paper'], bm, MM, (0.82, 0.8, 0.72), g=2)
        bm.free()
        if not top:
            bm2 = page_surface(w, d, lambda x, v, ph=ph, k=k: zf(x, v, k, ph) - 0.0005, 12, 8, flip=True)
            for v in bm2.verts:
                v.co.x -= w / 2
            put(M['paper'], bm2, MM, (0.8, 0.78, 0.7), g=2)
            bm2.free()


def basket_woven(c, r=0.2, h=0.22, rot=0, seed=1, col=(0.86, 0.66, 0.38), handle=True, lid=False):
    """round wicker basket with real over/under weavers, rim braid, base disc, handle"""
    rr = random.Random(seed)
    p = Vector(c)
    mat = M['wicker']
    n_stk = 20
    base = [V(0, 0, 0.0)]
    # base disc
    lathe(mat, p, [(0.001, 0.0), (r * 0.82, 0.0), (r * 0.84, 0.006), (0.001, 0.008)], seg=24, col=shade(col, 0.8), cap=False)
    nr = 6
    for k in range(nr):
        z = 0.012 + k * (h - 0.03) / (nr - 1)
        t = z / h
        rad = r * (0.85 + 0.15 * (t ** 1.0))
        pts = []
        NS = n_stk * 2
        for i in range(NS):
            a = i / NS * TAU
            ph = (i // 3 + k) % 2
            off = 0.0035 * (1 if ph else -1) * (0.5 + 0.5 * math.cos((i % 3) / 3 * math.pi * 2 + 0.0))
            pts.append(p + V(math.cos(a) * (rad + off), math.sin(a) * (rad + off), z))
        pts.append(pts[0])
        cc = shade(col, 0.85 + 0.25 * rr.random())
        tube(mat, pts, 0.0058, seg=4, col=cc, caps=False)
    # vertical stakes (ribs) visible between weavers
    for i in range(n_stk):
        a = i / n_stk * TAU
        tube(mat, [p + V(math.cos(a) * r * 0.84, math.sin(a) * r * 0.84, 0.004), p + V(math.cos(a) * r * 0.98, math.sin(a) * r * 0.98, h * 0.5), p + V(math.cos(a) * r * 1.0, math.sin(a) * r * 1.0, h)], 0.0035, seg=4, col=shade(col, 0.7), caps=False)
    # rim braid
    for rz, rd in ((h, r * 1.005), (h + 0.006, r * 1.0)):
        pts = [p + V(math.cos(i / 60 * TAU) * (rd + 0.004 * math.sin(i / 60 * TAU * 15)), math.sin(i / 60 * TAU) * (rd + 0.004 * math.sin(i / 60 * TAU * 15)), rz + 0.003 * math.cos(i / 60 * TAU * 15)) for i in range(60)]
        pts.append(pts[0])
        tube(mat, pts, 0.0065, seg=5, col=shade(col, 1.0), caps=False)
    if handle:
        for s_ in (-1, 1):
            pass
        hp = [p + V(-r * 1.0, 0, h * 0.8)] + [p + V(r * math.cos(math.radians(180 - a)) * 1.0, 0, h + 0.17 * math.sin(math.radians(a))) for a in range(0, 181, 15)] + [p + V(r * 1.0, 0, h * 0.8)]
        hp = [p + V(-r * 0.98, 0, h * 0.85)] + [p + V(-r * 0.98 * math.cos(math.radians(a)), 0, h + 0.2 * math.sin(math.radians(a))) for a in range(5, 176, 10)] + [p + V(r * 0.98, 0, h * 0.85)]
        for off in (-0.007, 0.0, 0.007):
            tube(mat, [q + V(0, off, 0) for q in hp], 0.0055, seg=4, col=shade(col, 0.95), caps=False)


def yarn_ball(c, r=0.045, col='#b5562f', seed=1):
    rr = random.Random(seed)
    p = Vector(c)
    cc = C(col)
    axes = []
    for k in range(5):
        a = Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1))).normalized()
        axes.append((a, rr.uniform(34, 52), rr.uniform(0, 6)))
    def disp(q):
        l = q - p
        d = l.length
        ln = l / d
        s = 0.0
        for (a, f_, ph) in axes:
            s += math.sin(ln.dot(a) * f_ + ph)
        return s
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=22, v_segments=14, radius=r)
    for v in bm.verts:
        l = v.co.copy(); ln = l.normalized()
        s = 0.0
        for (a, f_, ph) in axes:
            s += math.sin(ln.dot(a) * f_ + ph)
        v.co = ln * r * (1 + 0.035 * s / 5 * 2)
    put(M['yarn'], bm, Matrix.Translation(p), cc, lambda q: shade(cc, 0.85 + 0.15 * math.sin(disp(q) * 3) + 0.05 * nz(q.x * 90, q.y * 90, q.z * 90)))
    bm.free()


def knitting_basket(c, rot=0):
    p = Vector(c)
    basket_woven(p, 0.19, 0.2, rot, seed=3, handle=True)
    # yarn balls in the basket
    yarn_ball(p + V(0.04, 0.03, 0.2), 0.05, '#b5562f', 1)
    yarn_ball(p + V(-0.06, -0.02, 0.21), 0.045, '#5f7d73', 2)
    yarn_ball(p + V(0.0, -0.075, 0.19), 0.04, '#d0a23e', 3)
    # knit piece draped over the rim
    wd = 0.17
    nx, ns = 10, 26
    bm = bmesh.new()
    Vv = []
    for i in range(nx + 1):
        row = []
        for j in range(ns + 1):
            s = j / ns
            x = -wd / 2 + wd * i / nx
            # path: inside bottom -> up over rim -> outside down
            if s < 0.35:
                yy = -0.17 + s / 0.35 * 0.03 - 0.0; zz = 0.205 - (0.35 - s) / 0.35 * 0.06
                yy = 0.12 - 0.05 * (s / 0.35) - 0.0 ; yy = 0.19 * 0.0 + 0.1 * (1 - s / 0.35) * 0.0
            L = 0.55
            t = s * L
            if t < 0.12:
                yy = -(0.12 - t) * 0.0 + 0.0; yy = 0.04 + 0.0
                yy = 0.12 - t * 0.5 - 0.0
                zz = 0.215 - (0.12 - t) * 0.1
                yy = 0.12 - t * 0.0 - 0.0
                yy = 0.075 + t * 0.37
                zz = 0.215 + 0.0 * t - 0.0
            else:
                u = t - 0.12
                if u < 0.06:
                    ang = u / 0.06 * math.pi / 2
                    yy = 0.12 + 0.0 + 0.0
                    yy = 0.12 + 0.02 * math.sin(ang) * 0 + (0.075 + 0.12 * 0.37 - 0.075 - 0.12 * 0.37)
                    yy = 0.1196 + 0.025 * math.sin(ang)
                    zz = 0.215 + 0.02 * (1 - math.cos(ang)) * 0 + 0.005 * math.sin(ang) + 0.0
                else:
                    yy = 0.1446 + 0.0 + 0.012 * math.sin((u - 0.06) * 7) * 0
                    zz = 0.22 - (u - 0.06) * 0.0 - (u - 0.06)
            ww = 1 + 0.06 * math.sin(s * 9 + i * 0.5)
            row.append(bm.verts.new((x * ww + 0.006 * math.sin(t * 20 + i), yy + 0.004 * math.sin(i * 1.3 + t * 12), max(0.015, zz) + 0.003 * math.sin(i * 2.1))))
        Vv.append(row)
    for i in range(nx):
        for j in range(ns):
            try:
                bm.faces.new([Vv[i][j], Vv[i + 1][j], Vv[i + 1][j + 1], Vv[i][j + 1]])
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    stripe = [C('#b5562f'), C('#e0d2b4'), C('#5f7d73')]
    def kcol(q):
        l = q - p
        k = stripe[int((l.z * 28 + l.y * 4) // 3 % 3)] if False else stripe[int(((0.5 - l.z) * 40) // 4) % 3]
        k2 = 0.85 + 0.15 * math.sin((l.x * 140))
        return (k[0] * k2, k[1] * k2, k[2] * k2)
    bm2 = modbm(bm, [('SOLIDIFY', dict(thickness=0.005, offset=0.0))])
    put(M['yarn'], bm2, Matrix.Translation(p + V(0.0, 0.0, 0.0)) @ rotm((0, 0, 0)), (1, 1, 1), kcol, 2)
    bm2.free()
    # needles
    for (dx, ang, L) in ((-0.03, 14, 0.3), (0.025, -12, 0.3)):
        a0 = p + V(dx, 0.07, 0.19)
        d = V(math.sin(math.radians(ang)) * 0.4, 0.6, 0.8).normalized()
        tube(M['wood_pine'], [a0, a0 + d * L], [0.0035, 0.0028], seg=6, col=(0.82, 0.68, 0.45), caps=True)
        sphere(M['wood_pine'], a0 + d * L, 0.0055, seg=8, rings=5, col=(0.82, 0.68, 0.45))
        tube(M['pewter'], [a0 + d * (-0.0), a0 - d * 0.0 + V(0, 0, 0)], 0.0003, seg=3) if False else None
    # loose yarn strand from ball to piece
    ys = bez(p + V(0.04, 0.0, 0.245), p + V(0.1, 0.1, 0.27), p + V(0.1, 0.2, 0.2), p + V(0.04, 0.17, 0.17), 14)
    tube(M['yarn'], ys, 0.0028, seg=5, col=C('#b5562f'), caps=True)
