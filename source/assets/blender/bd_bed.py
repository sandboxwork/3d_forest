"""Bed: carved frame (hand modelled), mattress with piping, proxies for cloth collision. Cloth sims live in bd_bedcloth.py"""
from bd_lib import *
from bd_cloth import box_collider

# local bed frame: x across (+-0.81), y along (head = -y), z up from floor top.
HW = 0.77          # post centre x
HY = 0.97          # post centre y
MAT_TOP = 0.595
MAT_BOT = 0.375
MX, MY = 0.72, 0.95   # mattress half extents


def boolean_diff(bm, cutter_bm):
    me = bpy.data.meshes.new('_c'); cutter_bm.to_mesh(me)
    co = bpy.data.objects.new('_c', me); bpy.context.scene.collection.objects.link(co)
    out = modmesh(bm, [('BOOLEAN', dict(operation='DIFFERENCE', object=co, solver='EXACT'))])
    bpy.data.objects.remove(co); bpy.data.meshes.remove(me)
    return out


def spiral(cx, cz, r0, r1, turns, a0, n=22, sgn=1):
    pts = []
    for i in range(n + 1):
        t = i / n
        a = a0 + sgn * t * turns * TAU
        r = r0 + (r1 - r0) * t
        pts.append((cx + math.cos(a) * r, cz + math.sin(a) * r))
    return pts


def leaf2d(x, z, ang, L=0.035, w=0.012):
    """simple leaf polygon in (x,z)"""
    pts = []
    for u in np.linspace(0, 1, 7):
        pts.append((u * L, math.sin(u * math.pi) * w))
    for u in np.linspace(1, 0, 7)[1:-1]:
        pts.append((u * L, -math.sin(u * math.pi) * w))
    c, s = math.cos(ang), math.sin(ang)
    return [(x + px * c - py * s, z + px * s + py * c) for px, py in pts]


def post(f, x, y, h, head):
    mat = M['wood_oak']
    sq = 1.03 if head else 0.62
    col = (1.0, 0.93, 0.85)
    f.box(mat, (x, y, sq / 2), (0.08, 0.08, sq), bev=0.007, col=col, g=2)
    # chamfer-carved panel on face
    for sx in (-1, 1):
        f.box(mat, (x + sx * 0.0405, y, sq * 0.5 + 0.1), (0.004, 0.05, sq - 0.34), bev=0.0015, col=(0.9, 0.82, 0.74), g=2) if False else None
    if head:
        prof = [(0.036, 1.03), (0.043, 1.045), (0.04, 1.065), (0.026, 1.085), (0.022, 1.11), (0.03, 1.15), (0.037, 1.19), (0.03, 1.225), (0.02, 1.245),
                (0.024, 1.26), (0.033, 1.285), (0.036, 1.31), (0.03, 1.335), (0.016, 1.352), (0.001, 1.36)]
    else:
        prof = [(0.036, 0.62), (0.043, 0.635), (0.04, 0.655), (0.026, 0.675), (0.023, 0.7), (0.033, 0.735), (0.039, 0.76), (0.03, 0.795), (0.02, 0.815),
                (0.03, 0.838), (0.04, 0.868), (0.04, 0.895), (0.03, 0.925), (0.012, 0.945), (0.001, 0.953)]
    f.lathe(mat, (x, y, 0), profile_pts(prof, 3), seg=20, cap=False, col=col)
    # brass bed-bolt caps on the outer face at rail height
    sx = 1 if x > 0 else -1
    f.cyl(M['brass'], (x + sx * 0.0405, y, 0.33), 0.018, 0.006, axis='x', seg=14, bev=0.002)
    f.cyl(M['brass'], (x + sx * 0.0435, y, 0.33), 0.007, 0.004, axis='x', seg=8)
    # foot block / plinth
    f.box(mat, (x, y, 0.025), (0.092, 0.092, 0.05), bev=0.008, col=(0.85, 0.78, 0.7), g=2)


def crest(f, y):
    """pierced, carved headboard crest. Front face toward +y."""
    pts = []
    n = 70
    for i in range(n + 1):
        x = -0.73 + 1.46 * i / n
        u = abs(x) / 0.73
        z = 1.2 + 0.085 * (1 - u ** 2.4) + 0.05 * math.exp(-(x / 0.13) ** 2) + 0.012 * math.cos(x * 30) * (1 - u)
        pts.append((x, z))
    pts += [(0.73, 1.0), (-0.73, 1.0)]
    bm = bmesh.new()
    vb = [bm.verts.new((a, -0.0225, b)) for a, b in pts]
    vt = [bm.verts.new((a, 0.0225, b)) for a, b in pts]
    bm.faces.new(vb[::-1]); bm.faces.new(vt)
    nn = len(pts)
    for i in range(nn):
        j = (i + 1) % nn
        bm.faces.new([vb[i], vb[j], vt[j], vt[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm2 = bmesh.new()
    # piercings: ring of holes
    cut = bmesh.new()
    for k in range(-4, 5):
        if k == 0:
            continue
        x = k * 0.148
        r = 0.03 if abs(k) < 4 else 0.024
        bmesh.ops.create_cone(cut, cap_ends=True, segments=14, radius1=r, radius2=r, depth=0.2,
                              matrix=Matrix.Translation((x, 0, 1.087 + 0.02 * (1 - abs(k) / 5))) @ rotm((90, 0, 0)))
    res = boolean_diff(bm, cut)
    bm.free(); cut.free()
    f.put(M['wood_oak'], res, c=(0, y, 0), col=(1.0, 0.92, 0.84), g=0)
    res.free()
    # carved relief on the front (+y) face
    yy = y + 0.0225
    mat = M['wood_oak']
    cc = (1.1, 1.0, 0.9)
    # central sunburst medallion
    f.lathe(mat, (0, yy, 1.2), [(0.001, 0.012), (0.03, 0.01), (0.056, 0.004), (0.062, 0.0)], r=(-90, 0, 0), seg=28, cap=False, col=cc)
    for k in range(14):
        a = k * TAU / 14
        pl = [(0.065, -0.011), (0.115, -0.003), (0.13, 0.0), (0.115, 0.003), (0.065, 0.011)]
        pl = [(px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a)) for px, py in pl]
        f.prism(mat, [(a_ , b_ ) for a_, b_ in pl], 0.006, c=(0, yy + 0.003, 1.2), plane='xz', bev=0.0012, col=cc, g=0)
    f.lathe(mat, (0, yy + 0.008, 1.2), [(0.001, 0.014), (0.016, 0.01), (0.022, 0.003), (0.001, 0)], r=(-90, 0, 0), seg=14, cap=False, col=(1.15, 1.05, 0.95))
    # flanking scroll vines with leaves (mirrored)
    for sx in (-1, 1):
        for (cx, cz, r0, r1, turns, a0, sg) in ((0.27, 1.17, 0.05, 0.012, 1.3, math.pi * 0.2, -sx), (0.5, 1.2, 0.045, 0.012, 1.2, math.pi * 0.9, sx)):
            pts2 = spiral(sx * cx, cz, r0, r1, turns, a0 if sx > 0 else math.pi - a0, 26, sg)
            tp = [(a_, yy + 0.003, b_) for a_, b_ in pts2[::2]]
            f.tube(mat, tp, [0.0075 * (1 - 0.6 * i / 26) for i in range(0, 27, 2)], seg=5, col=cc)
        # S-curve stem towards the medallion with leaves
        stem = [(sx * (0.14 + 0.2 * t), yy + 0.003, 1.2 + 0.03 * math.sin(t * 6.0)) for t in np.linspace(0, 1, 20)]
        f.tube(mat, stem, 0.0065, seg=6, col=cc)
        for k in range(4):
            tpos = 0.2 + 0.2 * k
            px = sx * (0.14 + 0.2 * tpos); pz = 1.2 + 0.03 * math.sin(tpos * 6.0)
            ang = (0.9 if k % 2 else -0.9) + (math.pi if sx < 0 else 0)
            f.prism(mat, leaf2d(px, pz, ang if sx > 0 else math.pi - ang + math.pi, 0.045, 0.014), 0.006, c=(0, yy + 0.003, 0), plane='xz', bev=0.001, col=cc, g=0)
    # beaded moulding along the crest bottom
    for i in range(17):
        x = -0.69 + 1.38 * i / 16
        f.sphere(mat, (x, yy + 0.002, 1.015), 0.0085, seg=8, col=(1.05, 0.96, 0.88))
    f.box(mat, (0, yy + 0.004, 1.003), (1.46, 0.012, 0.012), bev=0.003, col=(1.05, 0.96, 0.88), g=0)


def fielded_panel(f, cx, cz, w, h, y, face=1, mat=None, col=(1, 0.93, 0.85)):
    mat = mat or M['wood_oak']
    d = 0.016 * face
    f.box(mat, (cx, y, cz), (w, 0.016, h), bev=0.002, col=(0.82, 0.74, 0.66), g=0)
    # moulding frame (4 mitred strips) proud of the panel
    t = 0.022
    for (dx, dz, sw, sh) in ((0, h / 2 - t / 2, w, t), (0, -h / 2 + t / 2, w, t), (-w / 2 + t / 2, 0, t, h - 2 * t), (w / 2 - t / 2, 0, t, h - 2 * t)):
        f.box(mat, (cx + dx, y + 0.014 * face, cz + dz), (sw, 0.012, sh), bev=0.0035, col=col, g=0 if sw > sh else 2)
    # raised bevelled field
    f.box(mat, (cx, y + 0.014 * face, cz), (w - 2 * t - 0.012, 0.012, h - 2 * t - 0.012), bev=0.004, col=(1.08, 1.0, 0.92), g=0)


def build_frame(f):
    mat = M['wood_oak']
    col = (1.0, 0.93, 0.85)
    for sx in (-1, 1):
        post(f, sx * HW, -HY, 1.0, True)
        post(f, sx * HW, HY, 0.6, False)
    # side rails with chamfered top + under-rail
    for sx in (-1, 1):
        f.box(mat, (sx * HW, 0, 0.31), (0.036, 1.86, 0.17), bev=0.005, col=col, g=1)
        f.box(mat, (sx * (HW - 0.025), 0, 0.2), (0.022, 1.7, 0.028), bev=0.003, col=(0.85, 0.78, 0.7), g=1)     # skirt cleat
        f.box(mat, (sx * (HW - 0.03), 0, 0.345), (0.03, 1.84, 0.03), bev=0.003, col=(0.85, 0.78, 0.7), g=1)      # slat ledger
        f.box(mat, (sx * (HW + 0.003), 0, 0.4), (0.044, 1.86, 0.014), bev=0.004, col=(1.08, 1.0, 0.92), g=1)       # top moulding
    # slats (stained darker, with gaps): ARRAY modifier
    unit = bm_box(1.44, 0.085, 0.018)
    bev_bm(unit, 0.003, 1)
    array_put(M['wood_pine'], unit, 15, (0.0, 0.123, 0.0), f._m((0, -0.86, 0.372)), col=(0.78, 0.65, 0.5), g=0)
    unit.free()
    f.box(mat, (0, 0, 0.30), (0.06, 1.8, 0.06), bev=0.004, col=(0.8, 0.72, 0.62), g=1)
    for y in (-0.55, 0.55):
        f.box(mat, (0, y, 0.15), (0.06, 0.06, 0.3), bev=0.004, col=(0.8, 0.72, 0.62), g=2)
    # ---- headboard
    yh = -HY
    f.box(mat, (0, yh, 0.46), (1.46, 0.04, 0.14), bev=0.004, col=col, g=0)
    f.box(mat, (0, yh + 0.026, 0.395), (1.46, 0.012, 0.024), bev=0.004, col=(1.1, 1.0, 0.92), g=0)
    # three fielded panels between stiles
    f.box(mat, (0, yh, 0.76), (1.46, 0.03, 0.46), bev=0.003, col=(0.7, 0.62, 0.55), g=0)
    pw = 0.43
    for k, cx in enumerate((-0.49, 0.0, 0.49)):
        fielded_panel(f, cx, 0.77, pw, 0.4, yh + 0.0, 1)
    for cx in (-0.245, 0.245):
        f.box(mat, (cx, yh + 0.004, 0.77), (0.05, 0.04, 0.46), bev=0.004, col=col, g=2)
    f.box(mat, (0, yh, 0.995), (1.46, 0.045, 0.03), bev=0.004, col=col, g=0)
    crest(f, yh)
    # ---- footboard with turned balusters
    yf = HY
    f.box(mat, (0, yf, 0.405), (1.46, 0.04, 0.1), bev=0.004, col=col, g=0)
    f.box(mat, (0, yf - 0.026, 0.405), (1.46, 0.012, 0.03), bev=0.004, col=(1.1, 1.0, 0.92), g=0)
    f.box(mat, (0, yf, 0.655), (1.46, 0.05, 0.065), bev=0.012, col=col, g=0, seg=3)
    f.box(mat, (0, yf - 0.03, 0.668), (1.46, 0.02, 0.026), bev=0.007, col=(1.1, 1.0, 0.92), g=0)
    bal = [(0.016, 0.455), (0.02, 0.465), (0.015, 0.48), (0.012, 0.50), (0.02, 0.525), (0.025, 0.545), (0.018, 0.57), (0.012, 0.59), (0.017, 0.605), (0.016, 0.62)]
    for i in range(10):
        x = -0.64 + i * (1.28 / 9)
        f.lathe(mat, (x, yf, 0), profile_pts(bal, 3), seg=12, col=col)
    # carved rosettes on the lower foot rail
    for sx in (-1, 1):
        f.lathe(mat, (sx * 0.3, yf - 0.021, 0.405), [(0.001, 0.008), (0.022, 0.006), (0.034, 0.002), (0.036, 0.0)], r=(90, 0, 0), seg=14, cap=False, col=(1.1, 1.0, 0.92))
    f.lathe(mat, (0.0, yf - 0.021, 0.405), [(0.001, 0.012), (0.03, 0.008), (0.05, 0.002), (0.052, 0.0)], r=(90, 0, 0), seg=18, cap=False, col=(1.1, 1.0, 0.92))
    # rail end caps & decorative buttons
    for sx in (-1, 1):
        f.sphere(mat, (sx * 0.72, yf - 0.03, 0.655), 0.014, seg=10, col=(1.1, 1.0, 0.92))


def mattress_bm(lowres=False):
    """rounded, slightly crowned mattress as bmesh in bed-local coords (lowres: visual mesh, mostly hidden under the linens)"""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 2 * MX; v.co.y *= 2 * MY; v.co.z *= (MAT_TOP - MAT_BOT)
    bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:] + bm.faces[:], offset=0.05, segments=2 if lowres else 4, profile=0.5, affect='EDGES', clamp_overlap=True)
    if not lowres:
        split_long_edges(bm, 0.07)
    zc = (MAT_TOP + MAT_BOT) / 2
    h = (MAT_TOP - MAT_BOT) / 2
    for v in bm.verts:
        v.co.z += zc
        if v.co.z > zc + h * 0.6:
            u = max(0.0, 1 - (v.co.x / MX) ** 2); w = max(0.0, 1 - (v.co.y / MY) ** 2)
            v.co.z += 0.016 * (u * w) ** 0.6 + 0.003 * nz(v.co.x, v.co.y, 0, 9, 4)
    return bm


def ticking(p):
    """world-space colour fn is evaluated on LOCAL coords through Fr; we pass local via closure instead (see build_mattress)"""
    return (1, 1, 1)


def build_mattress(f):
    bm = mattress_bm(lowres=True)
    cream = (0.93, 0.9, 0.82); stripe = (0.42, 0.47, 0.6)
    Minv = f.M.inverted()

    def cfn(p):
        q = Minv @ p
        side = abs(q.x) / MX > abs(q.y) / MY
        coord = q.y if side else q.x * 1.3
        edge = (q.z < MAT_TOP - 0.025) and (abs(q.x) > MX - 0.06 or abs(q.y) > MY - 0.06)
        if edge:
            s = int(math.floor(coord / 0.017)) % 4
            c = stripe if s == 0 else cream
            return (c[0] * 0.98, c[1] * 0.98, c[2] * 0.98)
        k = 1 + 0.03 * fbm(q.x, q.y, 0, 20, 2, 2)
        return (cream[0] * k, cream[1] * k, cream[2] * k)
    f.put(M['linen'], bm, c=(0, 0, 0), cfn=cfn, g=1, skip_down=True)
    bm.free()
    # piping around the upper and lower seams (rounded rectangle path)
    def rrect(z, inset=0.0, r=0.06, n=8):
        pts = []
        hx, hy = MX - inset, MY - inset
        for (cx, cy, a0) in ((hx - r, hy - r, 0), (-hx + r, hy - r, 90), (-hx + r, -hy + r, 180), (hx - r, -hy + r, 270)):
            for i in range(n + 1):
                a = math.radians(a0 + 90 * i / n)
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
        return pts
    for z in (MAT_TOP - 0.045, MAT_BOT + 0.045):
        f.tube(M['linen'], rrect(z, -0.002), 0.0075, seg=8, col=(0.96, 0.93, 0.85), closed=True)
    # side stitching line (top seam) – tiny dashes
    pts = rrect(MAT_TOP - 0.03, -0.004)
    # carry handles (cloth tabs)
    for y in (-0.4, 0.4):
        for sx in (-1, 1):
            f.tube(M['linen'], [(sx * (MX + 0.001), y - 0.06, MAT_TOP - 0.11), (sx * (MX + 0.02), y - 0.04, MAT_TOP - 0.115), (sx * (MX + 0.02), y + 0.04, MAT_TOP - 0.115),
                                (sx * (MX + 0.001), y + 0.06, MAT_TOP - 0.11)], 0.006, seg=6, col=(0.4, 0.45, 0.58), flat=(1.0, 2.0))


def proxies():
    """collision proxies in bed-local coordinates (list of bmesh)"""
    out = []
    out.append(mattress_bm())
    b = lambda c, s, bev=0.0: out.append(box_collider(c, s, bev=bev))
    for sx in (-1, 1):
        b((sx * HW, 0, 0.31), (0.036, 1.86, 0.17))
        b((sx * HW, -HY, 0.55), (0.08, 0.08, 1.1))
        b((sx * HW, HY, 0.45), (0.08, 0.08, 0.9))
    b((0, -HY, 0.7), (1.46, 0.05, 0.6))                 # headboard lower
    b((0, -HY, 1.1), (1.46, 0.05, 0.3))
    b((0, HY, 0.655), (1.46, 0.05, 0.065), 0.01)        # foot rail
    b((0, HY, 0.5), (1.46, 0.04, 0.3))                  # foot lower (slightly solid so cloth doesn't poke through balusters)
    b((0, 0, 0.30), (1.5, 1.9, 0.02))                   # slat bed (under mattress)
    # floor
    b((0, 0, -0.05), (4, 5, 0.1))
    return out
