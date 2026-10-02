"""vl_extras: hair, facial hair, hats, props. Head-local builders (origin = cranium center) are placed with place_head()."""
import sys
sys.path.insert(0, '/shared/river/assets/blender')
from vl_cloth import *


def revolve(profile, segs=24, sx=1.0, sy=1.0, cx=0.0, cy=0.0, closed_top=False, closed_bot=False):
    """profile: list of (r, z) bottom->top. returns bmesh, rings around Z with elliptical scale."""
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        rings.append([bm.verts.new(V(cx + r * sx * math.cos(2 * math.pi * j / segs), cy + r * sy * math.sin(2 * math.pi * j / segs), z)) for j in range(segs)])
    for i in range(len(rings) - 1):
        for j in range(segs):
            j2 = (j + 1) % segs
            try:
                bm.faces.new((rings[i][j], rings[i][j2], rings[i + 1][j2], rings[i + 1][j]))
            except ValueError:
                pass
    if closed_top:
        cen = bm.verts.new(V(cx, cy, profile[-1][1]))
        for j in range(segs):
            bm.faces.new((rings[-1][j], rings[-1][(j + 1) % segs], cen))
    if closed_bot:
        cen = bm.verts.new(V(cx, cy, profile[0][1]))
        for j in range(segs):
            bm.faces.new((rings[0][(j + 1) % segs], rings[0][j], cen))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def _phi(co):
    return math.degrees(math.atan2(abs(co.x), -co.y))


def hair_cap(c, line, thick=0.009, top_extra=0.0, clump=0.5, seed=1, mat='hair', back_extra=0.0, front_part=0.0):
    """Shell of hair over the scalp. line: list of (phi_deg, z) hairline control points (symmetric)."""
    g = c.head['grid'].copy()
    g.normal_update()
    ph = [p for p, z in line]; zs = [z for p, z in line]

    def zl(co):
        return float(np.interp(_phi(co), ph, zs)) + 0.004 * mnoise.noise(V(_phi(co) * 0.11, seed, 0.0)) * (1 if co.z > -0.03 else 0)
    dele = [f for f in g.faces if f.calc_center_median().z < zl(f.calc_center_median()) - 0.002]
    bmesh.ops.delete(g, geom=dele, context='FACES')
    for v in list(g.verts):
        if not v.link_faces:
            g.verts.remove(v)
    bvh = c.head['bvh']
    for v in g.verts:
        if v.is_boundary:
            loc, nrm, idx, dist = bvh.find_nearest(V(v.co.x, v.co.y, zl(v.co)))
            if loc is not None:
                v.co = loc
    smooth_boundary(g, bvh, 2)
    g.normal_update()
    offs = []
    for v in g.verts:
        co = v.co
        dz = co.z - zl(co)
        th = thick * (0.08 + 0.92 * smooth(0.0, 0.03, dz)) + top_extra * smooth(0.02, 0.1, co.z)
        if co.y > 0.02:
            th += back_extra * smooth(0.0, 0.06, co.y)
        th_ = math.atan2(co.y, co.x)
        n1 = mnoise.noise(V(th_ * 6.0, 0.0, seed * 3.1))
        n2 = mnoise.noise(V(th_ * 15.0, co.z * 25, seed * 1.7 + 5))
        n3 = mnoise.noise(V(th_ * 31.0, co.z * 40, seed * 0.7 + 9))
        th *= 1.0 + clump * (0.45 * n1 + 0.35 * n2 + 0.3 * n3)
        offs.append(max(th, 0.0007))
    for v, o in zip(g.verts, offs):
        v.co += v.normal * o
    return setm(g, mat)


def brows(c, sgn_list=(1, -1), width=0.0033, thick=0.0026, arch=0.008, inner=0.011, outer=0.052, z0=0.030, mat='hair', rise=0.0):
    bvh = c.head['bvh']
    out = []
    for sg in sgn_list:
        pts = []
        for t in (0.0, 0.33, 0.66, 1.0):
            x = inner + (outer - inner) * t
            z = z0 + arch * math.sin(math.pi * min(1.0, t * 1.15)) - (0.004 * t ** 2) + rise * t
            hit = bvh.ray_cast(V(sg * x, -0.3, z), V(0, 1, 0))
            y = hit[0].y if hit[0] is not None else -0.09
            pts.append(V(sg * x, y + 0.0004, z))
        w = [width * 0.9, width * 1.15, width * 1.0, width * 0.45]
        bm = loft(pts, w, [thick] * 4, segs=6, res=2, up=(0, -1, 0), cap0=True, cap1=True, cap_push=0.8)
        out.append(setm(bm, mat))
    return merge(*out)


def facial_hair(c, kind='beard', thick=0.011, length=0.0, cheek_z=-0.034, side_z=-0.012, seed=4, mat='hair', mouth_open=True, spread=0.0):
    """Beard + moustache shell (head-local). Returns (head_part_bm, jaw_part_bm)."""
    g = c.head['grid'].copy()
    g.normal_update()
    dele = []
    for f in g.faces:
        p = f.calc_center_median()
        phi = _phi(p)
        keep = False
        if p.y < 0.02 and phi < 97:
            thr = cheek_z if phi < 30 else (cheek_z + (side_z - cheek_z) * smooth(30, 55, phi))
            keep = p.z < thr
            if abs(p.x) < 0.016 and p.z > -0.052:
                keep = False                                   # nose underside stays free
        if keep and mouth_open and abs(p.x) < 0.0165 and Z_SLIT - 0.0115 < p.z < Z_SLIT + 0.0004 and p.y < -0.06:
            keep = False
        if not keep:
            dele.append(f)
    bmesh.ops.delete(g, geom=dele, context='FACES')
    for v in list(g.verts):
        if not v.link_faces:
            g.verts.remove(v)
    g.normal_update()
    bvh = c.head['bvh']
    for v in g.verts:
        if v.is_boundary and v.co.z > cheek_z - 0.03 and v.co.z < cheek_z + 0.03 and abs(v.co.x) > 0.018 and _phi(v.co) < 92:
            ph_ = _phi(v.co)
            thr = cheek_z if ph_ < 30 else (cheek_z + (side_z - cheek_z) * smooth(30, 55, ph_))
            thr += 0.0035 * mnoise.noise(V(ph_ * 0.2, seed, 1.0))
            loc, nrm, idx, dist = bvh.find_nearest(V(v.co.x, v.co.y, thr))
            if loc is not None:
                v.co = loc
    smooth_boundary(g, bvh, 2, 0.5)
    g.normal_update()
    # hop distance from the open boundary -> soft thickness fade
    hop = {v.index: (0 if v.is_boundary else 99) for v in g.verts}
    g.verts.ensure_lookup_table()
    changed = True
    it = 0
    while changed and it < 4:
        changed = False
        it += 1
        for v in g.verts:
            for e in v.link_edges:
                o = e.other_vert(v)
                if hop[o.index] + 1 < hop[v.index]:
                    hop[v.index] = hop[o.index] + 1; changed = True
    offs = []
    for v in g.verts:
        co = v.co
        w = min(1.0, hop[v.index] / 2.0)
        th = thick * (0.55 + 0.6 * smooth(-0.04, -0.11, co.z)) * (0.12 + 0.88 * w)
        th *= 1.0 + 0.45 * mnoise.noise(V(co.x * 80, co.z * 28, seed))
        # moustache droops over the lip: heavier near the philtrum rows
        if -0.07 < co.z < -0.05 and abs(co.x) < 0.03:
            th += 0.004 * smooth(0.03, 0.0, abs(co.x))
        offs.append(max(th, 0.0007))
    for v, o in zip(g.verts, offs):
        v.co += v.normal * o
        if length and v.co.z < -0.085:
            k = smooth(-0.085, -0.115, v.co.z) * (1 - min(1, abs(v.co.x) / 0.07))
            v.co.z -= length * k
            v.co.y -= 0.35 * length * k
    setm(g, mat)
    hd = g.copy(); jw = g.copy()
    hf = [f for f in hd.faces if f.calc_center_median().z < Z_SLIT - 0.0005]
    bmesh.ops.delete(hd, geom=hf, context='FACES')
    jf = [f for f in jw.faces if f.calc_center_median().z >= Z_SLIT - 0.0005]
    bmesh.ops.delete(jw, geom=jf, context='FACES')
    g.free()
    return hd, jw


def smooth_boundary(g, bvh, iters=2, blend=0.55):
    for _ in range(iters):
        newp = {}
        for v in g.verts:
            if not v.is_boundary:
                continue
            nb = [e.other_vert(v) for e in v.link_edges if e.is_boundary]
            if len(nb) != 2:
                continue
            tgt = (nb[0].co + nb[1].co) / 2
            p = v.co.lerp(tgt, blend)
            loc, nrm, idx, dist = bvh.find_nearest(p)
            if loc is not None:
                newp[v.index] = loc
        g.verts.ensure_lookup_table()
        for i, loc in newp.items():
            g.verts[i].co = loc
    return g


def lock(pts, r0, r1, segs=5, res=2, mat='hair'):
    return setm(strand(pts, r0, r1, segs=segs, res=res), mat)


def braid_chain(p0, direction, length, n, r, sway=0.012, mat='hair', taper=0.65, twist_axis=None):
    """3-strand braid look: alternating flattened blobs along a hanging path."""
    out = []
    d = V(direction).normalized()
    for i in range(n):
        t = i / (n - 1)
        pos = p0 + d * length * t
        rr = r * (1.0 - taper * t ** 1.5)
        side = V(1, 0, 0)
        sgn = 1 if i % 2 == 0 else -1
        b = blob(pos + side * sgn * rr * 0.28, (rr * 0.85, rr * 0.8, rr * 1.0 * length / n * 1.25), segs=8, rings=5)
        rot_about(b, 'Y', sgn * 0.5, center=tuple(pos + side * sgn * rr * 0.28))
        out.append(b)
    # tie
    out.append(blob(p0 + d * length, (r * 0.4, r * 0.4, r * 0.5), segs=6, rings=4))
    return setm(merge(*out), mat)


def bun(center, r=0.045, mat='hair', seed=0):
    bm = blob(center, (r, r * 0.95, r * 0.8), segs=14, rings=9)

    def fn(p, n):
        a = math.atan2(p.y - center.y, p.x - center.x)
        return 0.0035 * math.sin(a * 5 + 8 * (p.z - center.z)) + 0.002 * mnoise.noise(p * 90)
    displace(bm, fn)
    return setm(bm, mat)


def lips(c, w=0.0185, up_h=0.0044, lo_h=0.0054, prot=0.0032):
    """Lip tubes (lips material) + mouth line. Returns (head_bm, jaw_bm) in head-local coords."""
    bvh = c.head['bvh']
    xs = [-w, -w * 0.5, 0.0, w * 0.5, w]
    taper = [0.5, 0.92, 1.0, 0.92, 0.5]

    def mk(zc, h, zoff):
        pts = []
        for xx, tp in zip(xs, taper):
            zz = zc + zoff * (1 - tp) * 0.0
            hit = bvh.ray_cast(V(xx, -0.3, zz), V(0, 1, 0))
            y = hit[0].y if hit[0] is not None else -0.08
            pts.append(V(xx, y + 0.0004, zz + 0.0006 * (1 - tp) * (1 if zoff > 0 else -1)))
        bm = loft(pts, [h * t for t in taper], [prot * (0.5 + 0.5 * t) for t in taper], segs=8, res=2, up=(0, -1, 0), cap0=True, cap1=True, cap_push=0.7)
        return setm(bm, 'lips')
    upper = mk(Z_SLIT + up_h * 0.8, up_h, 1)
    lower = mk(Z_SLIT - lo_h * 0.85, lo_h, -1)
    # mouth line
    pts = []
    for xx in xs:
        hit = bvh.ray_cast(V(xx, -0.3, Z_SLIT), V(0, 1, 0))
        y = hit[0].y if hit[0] is not None else -0.08
        pts.append(V(xx, y + 0.0035, Z_SLIT + (0.0008 if abs(xx) > w * 0.8 else 0)))
    line = loft(pts, [0.0006, 0.0008, 0.0008, 0.0008, 0.0006], [0.0006] * 5, segs=4, res=2, up=(0, -1, 0), cap0=True, cap1=True)
    setm(line, 'mouth')
    return merge(upper, line), lower


def fringe(c, n=9, span=0.05, z=0.066, drop=0.02, r=0.0085, seed=3, mat='hair', lift=0.0):
    bvh = c.head['bvh']
    out = []
    for i in range(n):
        x = -span + 2 * span * i / (n - 1)
        hit = bvh.ray_cast(V(x, -0.3, z), V(0, 1, 0))
        y = hit[0].y if hit[0] is not None else -0.085
        j = mnoise.noise(V(i * 2.7, seed, 0))
        pts = [V(x, y + 0.004, z + 0.004), V(x * 1.04 + 0.004 * j, y - 0.010, z - 0.006 + lift), V(x * 1.1 + 0.008 * j, y - 0.014, z - drop * (0.8 + 0.4 * j) + lift * 0.5)]
        out.append(lock(pts, r, 0.0012, segs=5, res=2, mat=mat))
    return merge(*out)


# ------------------------------------------------------------------ hats (head-local)
def flat_cap(c, mat='cloth_alt', size=1.0, seed=3, band=True):
    cap = hair_cap(c, [(0, .047), (45, .040), (90, .030), (125, .018), (180, .012)], thick=0.011, top_extra=0.012, clump=0.0, seed=seed, mat=mat)
    for v in cap.verts:
        v.co.x *= 1.07
        v.co.y = v.co.y * 1.06 - (0.012 if v.co.y < 0 else 0.0) * smooth(0.0, 0.08, v.co.z) + 0.004
        v.co.z += 0.004 * smooth(0.04, 0.12, v.co.z)
    displace(cap, lambda p, n: 0.0022 * mnoise.noise(V(p.x * 55, p.y * 55, p.z * 55)) + 0.0025 * math.sin(math.atan2(p.y, p.x) * 8) * smooth(0.04, 0.12, p.z))
    rim(cap, 0.004)
    out = [cap]
    bill = loft([V(0, -0.088, 0.047), V(0, -0.125, 0.044), V(0, -0.158, 0.034)], [0.038, 0.041, 0.030], [0.0035, 0.0035, 0.0030], segs=10, res=3, up=(0, 0, 1), cap0=True, cap1=True, cap_push=0.5, power=3.0)
    setm(bill, mat)
    out.append(bill)
    btn = blob(V(0.0, 0.0, 0.1455), (0.007, 0.007, 0.005), segs=8, rings=5)
    out.append(setm(btn, mat))
    return merge(*out)


def straw_hat(c, seed=2):
    crown = revolve([(0.098, 0.040), (0.101, 0.065), (0.097, 0.105), (0.082, 0.135), (0.055, 0.152), (0.02, 0.159)], segs=28, sx=1.0, sy=1.12, cy=0.008, closed_top=True)
    displace(crown, lambda p, n: 0.0018 * math.sin(p.z * 220) * 0.5 + 0.0012 * mnoise.noise(p * 90))
    brim = revolve([(0.097, 0.045), (0.15, 0.041), (0.20, 0.030), (0.245, 0.014), (0.255, 0.006)], segs=36, sx=1.0, sy=1.04, cy=0.012)
    displace(brim, lambda p, n: 0.006 * mnoise.noise(V(p.x * 14, p.y * 14, 0)) + 0.0015 * math.sin(math.atan2(p.y, p.x) * 22))
    setm(crown, 'straw'); setm(brim, 'straw')
    band = revolve([(0.1005, 0.044), (0.1045, 0.047), (0.1045, 0.072), (0.1025, 0.075)], segs=28, sx=1.0, sy=1.12, cy=0.008, closed_top=False)
    setm(band, 'cloth_accent')
    hat = merge(crown, brim, band)
    rot_about(hat, 'X', -0.12, center=(0, 0, 0.05))
    translate(hat, V(0, 0, 0.012))
    return hat


def baker_cap(c, seed=5, mat='cloth_main'):
    dome = revolve([(0.100, 0.050), (0.110, 0.080), (0.114, 0.110), (0.108, 0.140), (0.084, 0.163), (0.042, 0.174), (0.0, 0.176)], segs=28, sx=1.0, sy=1.08, cy=0.010, closed_top=True)
    displace(dome, lambda p, n: 0.005 * math.sin(math.atan2(p.y, p.x) * 6 + p.z * 25 + mnoise.noise(p * 12) * 3) * smooth(0.06, 0.13, p.z) + 0.0015 * mnoise.noise(p * 70))
    band = revolve([(0.1005, 0.044), (0.106, 0.049), (0.106, 0.078), (0.102, 0.083)], segs=28, sx=1.0, sy=1.08, cy=0.010)
    return merge(setm(dome, mat), setm(band, mat))


def headscarf(c, mat='cloth_accent', seed=4, front_z=0.074, knot=True):
    sc_ = hair_cap(c, [(0, front_z), (35, front_z - 0.004), (65, 0.050), (90, 0.010), (110, -0.028), (140, -0.065), (180, -0.085)], thick=0.016, top_extra=0.006, clump=0.0, seed=seed, mat=mat)
    displace(sc_, lambda p, n: 0.003 * math.sin(math.atan2(p.y, p.x) * 9 + mnoise.noise(p * 14) * 3) * smooth(0.0, 0.06, p.z) + 0.0015 * mnoise.noise(p * 60))
    rim(sc_, 0.004)
    out = [sc_]
    if knot:
        k = blob(V(0, 0.095, -0.062), (0.026, 0.022, 0.02), segs=10, rings=7)
        out.append(setm(k, mat))
        for sg in (1, -1):
            tail = loft([V(sg * 0.006, 0.100, -0.065), V(sg * 0.026, 0.118, -0.085), V(sg * 0.040, 0.128, -0.125)], [0.014, 0.019, 0.016], [0.004, 0.004, 0.003], segs=8, res=2, up=(0, -1, 0), cap0=True, cap1=True, cap_push=0.4)
            out.append(setm(tail, mat))
    return merge(*out)


# ------------------------------------------------------------------ props (world coords, pivot at the grip)
def cane(c, G, mat='wood'):
    top = G.z + 0.075
    pts = [V(G.x, G.y, 0.0), V(G.x, G.y, G.z * 0.5), V(G.x, G.y, top)]
    shaft = setm(strand(pts, 0.0105, 0.0125, segs=8, res=2, up=(0, -1, 0)), mat)
    crook = [V(G.x, G.y, top - 0.005), V(G.x, G.y - 0.012, top + 0.045), V(G.x, G.y - 0.05, top + 0.075), V(G.x, G.y - 0.095, top + 0.05), V(G.x, G.y - 0.104, top + 0.01)]
    ck = setm(loft(crook, [0.0128, 0.0135, 0.0135, 0.0128, 0.0125], segs=8, res=3, up=(1, 0, 0), cap0=False, cap1=True, cap_push=0.9), mat)
    tip = setm(loft([V(G.x, G.y, 0.0), V(G.x, G.y, 0.035)], [0.0115, 0.0132], segs=8, res=1, up=(0, -1, 0), cap0=True, cap1=False, cap_push=0.4), 'iron')
    return merge(shaft, ck, tip)


def hammer(c, G, handle_len=0.44, below=0.07):
    z0 = G.z - below
    pts = [V(G.x, G.y, z0), V(G.x, G.y, z0 + handle_len * 0.5), V(G.x, G.y, z0 + handle_len)]
    h = setm(strand(pts, 0.0185, 0.0165, segs=8, res=2, up=(0, -1, 0)), 'wood')
    zc = z0 + handle_len + 0.005
    head = box(V(G.x, G.y, zc), (0.050, 0.205, 0.058), bevel=0.007)
    # tapered pein end (front) and flat face (back)
    for v in head.verts:
        if v.co.y < G.y - 0.04:
            v.co.z = zc + (v.co.z - zc) * 0.65
            v.co.x = G.x + (v.co.x - G.x) * 0.75
    eye = blob(V(G.x, G.y, zc), (0.03, 0.03, 0.036), segs=8, rings=6)
    setm(head, 'iron'); setm(eye, 'iron')
    return merge(h, head, eye)


def basket(c, G, side):
    # handle runs along Y through G; basket hangs below, long axis along Y
    rim_z = G.z - 0.105
    cx, cy = G.x, G.y
    prof_ = [(0.55, rim_z - 0.17), (0.86, rim_z - 0.14), (1.0, rim_z - 0.07), (1.04, rim_z - 0.01), (1.0, rim_z)]
    body = revolve(prof_, segs=24, sx=0.095, sy=0.17, cx=cx, cy=cy, closed_bot=True)
    displace(body, lambda p, n: 0.0032 * (math.sin(p.z * 190) * math.sin(math.atan2(p.y - cy, p.x - cx) * 14)))
    setm(body, 'straw')
    rim = revolve([(1.0, rim_z - 0.012), (1.05, rim_z - 0.004), (1.05, rim_z + 0.008), (1.0, rim_z + 0.012)], segs=24, sx=0.095, sy=0.17, cx=cx, cy=cy)
    setm(rim, 'straw')
    arch = loft([V(cx, cy - 0.165, rim_z), V(cx, cy - 0.11, G.z - 0.015), V(cx, cy, G.z + 0.012), V(cx, cy + 0.11, G.z - 0.015), V(cx, cy + 0.165, rim_z)],
                [0.0115] * 5, segs=8, res=3, up=(1, 0, 0), cap0=True, cap1=True, cap_push=0.4)
    setm(arch, 'straw')
    out = [body, rim, arch]
    # loaves
    l1 = blob(V(cx - 0.015, cy + 0.0, rim_z + 0.012), (0.05, 0.135, 0.044), rot=(0.0, 0.0, 0.18), segs=14, rings=8)
    l2 = blob(V(cx + 0.03, cy + 0.0, rim_z + 0.008), (0.042, 0.13, 0.038), rot=(0.0, 0.0, -0.12), segs=14, rings=8)
    for l in (l1, l2):
        displace(l, lambda p, n: 0.003 * mnoise.noise(p * 40))
        out.append(setm(l, 'bread'))
    return merge(*out)


def pitchfork(c, G, above=0.62):
    top = G.z + above
    pts = [V(G.x, G.y, 0.0), V(G.x, G.y, G.z * 0.5), V(G.x, G.y, top)]
    sh = setm(strand(pts, 0.0155, 0.0148, segs=8, res=2, up=(0, -1, 0)), 'wood')
    sock = setm(loft([V(G.x, G.y, top - 0.09), V(G.x, G.y, top + 0.02)], [0.0185, 0.0165], segs=8, res=1, up=(0, -1, 0), cap0=True, cap1=True, cap_push=0.4), 'iron')
    bar = setm(box(V(G.x, G.y, top + 0.03), (0.2, 0.016, 0.022), bevel=0.004), 'iron')
    out = [sh, sock, bar]
    for xo, spread in ((-0.092, -0.025), (0.0, 0.0), (0.092, 0.025)):
        pts = [V(G.x + xo, G.y, top + 0.03), V(G.x + xo + spread * 0.4, G.y, top + 0.13), V(G.x + xo + spread, G.y, top + 0.26), V(G.x + xo + spread * 1.1, G.y, top + 0.32)]
        out.append(setm(strand(pts, 0.0075, 0.0015, segs=6, res=2, up=(0, -1, 0)), 'iron'))
    return merge(*out)


def beard_locks(c, n=5, length=0.05, width=0.03, seed=3, mat='hair', r=0.011, z0=-0.1):
    bvh = c.head['bvh']
    out = []
    for i in range(n):
        t = i / (n - 1)
        x = -width + 2 * width * t
        z = z0 + 0.008 * abs(x) / width
        hit = bvh.ray_cast(V(x, -0.3, z), V(0, 1, 0))
        y = hit[0].y if hit[0] is not None else -0.07
        j = mnoise.noise(V(i * 3.3, seed, 0.5))
        ln = length * (0.7 + 0.5 * (1 - abs(2 * t - 1)) + 0.2 * j)
        pts = [V(x, y + 0.006, z + 0.012), V(x * 1.0, y - 0.004, z - 0.01), V(x * 0.8 + 0.004 * j, y - 0.012, z - ln * 0.55), V(x * 0.55 + 0.006 * j, y - 0.012, z - ln)]
        out.append(lock(pts, r, 0.0018, segs=6, res=2, mat=mat))
    return merge(*out)
