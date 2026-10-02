"""Hanging garments (cloth-simulated): tube-bodied coats/dresses/shirts pinned at shoulder, sleeves, hoods, scarves, towels."""
from bd_lib import *
from bd_cloth import *

# garment frame: origin at the hook/hanger top centre, -z down. x = shoulder line, y = front (+y toward the viewer in wardrobe frame).


def tube_grid(n_ring, rows, ring_fn, phase=0.0, wave=0.0):
    """rows list of t in [0,1]; ring_fn(t) -> (cx,cy,z,a,b,amp) ; returns verts (rows*n_ring), faces, uv(m), top ring ids"""
    V_, uv = [], []
    zs = []
    for ri, t in enumerate(rows):
        cx, cy, z, a, b, amp = ring_fn(t)
        zs.append(z)
        circ = 0.0
        for k in range(n_ring):
            th = TAU * k / n_ring + phase
            fold = 1 + amp * (math.sin(th * 7 + 0.7) * 0.6 + math.sin(th * 11 + 2.1) * 0.4) * t
            zz = z + wave * (t ** 3) * (0.6 * math.sin(2 * th + phase * 2) + 0.4 * math.sin(3 * th + 1.0) + 0.35 * math.sin(th))
            V_.append((cx + a * fold * math.cos(th), cy + b * fold * math.sin(th), zz))
            uv.append((k / n_ring * TAU * 0.5 * (a + b), -z))
    faces = []
    for ri in range(len(rows) - 1):
        for k in range(n_ring):
            k2 = (k + 1) % n_ring
            faces.append((ri * n_ring + k, ri * n_ring + k2, (ri + 1) * n_ring + k2, (ri + 1) * n_ring + k))
    # outward normals: ring ccw viewed from top, rows going down -> faces (k,k2,next k2,next k) normal points inward; flip
    faces = [tuple(reversed(f)) for f in faces]
    # cap the top ring (shoulder / sleeve head) with a fan so no interior is visible
    ci = len(V_)
    V_.append(tuple(np.mean(np.array(V_[:n_ring]), axis=0)))
    uv.append((0.0, 0.0))
    for k in range(n_ring):
        faces.append((ci, k, (k + 1) % n_ring))
    return np.array(V_, np.float32), faces, np.array(uv, np.float32), list(range(n_ring)) + [ci]


def uv_cyl(v, faces):
    return None


def body_sim(name, kind, hang_h=0.9, sh_w=0.2, hem_scale=1.35, phase=0.0, seed=0, extra_colliders=(), frames=45, preset='coat', amp=0.12, hb=0.08, wave=0.03):
    """main body tube. returns dict(v,f,uv,pins,kind)"""
    n_ring = 18
    nrows = 17
    rows = [i / (nrows - 1) for i in range(nrows)]

    def ring_fn(t):
        # shoulder slope: top ring is flatter, widen to hem
        top_a, top_b = sh_w * 0.95, 0.045
        hem_a, hem_b = sh_w * hem_scale * 1.05, hb
        s = t ** 0.85
        a = top_a + (hem_a - top_a) * s
        b = top_b + (hem_b - top_b) * (t ** 0.6)
        return (0.0, 0.0, -hang_h * t - 0.035 * (1 - t) * 0, a, b, amp)
    v, f, uv, top = tube_grid(n_ring, rows, ring_fn, phase, wave=wave)
    # drop shoulder slope: top ring z follows hanger slope
    for k in top[:-1]:
        v[k, 2] = -0.075 * abs(v[k, 0]) / (sh_w * 0.95)
    v[top[-1]] = v[top[:-1]].mean(axis=0)
    res = simulate(name, v, f, pins=top, frames=frames, colliders=list(extra_colliders), preset=preset, collision_dist=0.008, damping_scale=2.0)
    return dict(v=res, f=f, uv=uv, pins=top, kind=kind)


def sleeve_sim(name, side, body_v, body_f, sh_w=0.2, length=0.55, r0=0.05, r1=0.038, frames=40):
    n_ring, nrows = 10, 11
    rows = [i / (nrows - 1) for i in range(nrows)]
    ang = math.radians(8) * side

    def ring_fn(t):
        return (side * (sh_w * 0.95 + r0 + 0.014 + math.sin(ang) * length * t), 0.0, -0.075 - math.cos(ang) * length * t, r0 + (r1 - r0) * t, (r0 + (r1 - r0) * t) * 0.9, 0.1)
    v, f, uv, top = tube_grid(n_ring, rows, ring_fn, 0.3)
    res = simulate(name, v, f, pins=top, frames=frames, colliders=[(body_v, body_f)], preset='coat', collision_dist=0.006, damping_scale=2.0)
    return dict(v=res, f=f, uv=uv, pins=top, kind='sleeve')


def put_garment(frame, g, mat, cfn=None, col=(1, 1, 1), solid=0.0):
    bm = solid_bm(g['v'], g['f'], g['uv'], solid, 1.0) if solid else cloth_to_bm(g['v'], g['f'], g['uv'])
    frame.put(mat, bm, cfn=cfn, col=col, skip_down=False)
    bm.free()


def hanger(frame, c, mat_wood=None, sh_w=0.2):
    """wooden coat hanger: shaped shoulders bar + brass hook. c = hook top centre (local)."""
    mat = mat_wood or M['wood_dark']
    x, y, z = c
    pts = [(x - sh_w, y, z - 0.075), (x - sh_w * 0.5, y, z - 0.036), (x, y, z - 0.02), (x + sh_w * 0.5, y, z - 0.036), (x + sh_w, y, z - 0.075)]
    frame.tube(mat, [Vector(p) for p in catmull(pts, 3)], 0.0075, seg=6, flat=(1.0, 0.7))
    frame.tube(M['brass'], [Vector(p) for p in catmull([(x, y, z - 0.02), (x, y, z + 0.02), (x + 0.02, y, z + 0.052), (x + 0.005, y, z + 0.068), (x - 0.01, y, z + 0.055)], 2)], 0.0022, seg=5)


def buttons(frame, g, n, x=0.0, y_front=1.0, mat=None, col=(0.9, 0.85, 0.7), r=0.009, z0=0.1, z1=0.6):
    """sew buttons along the front centre line of a body tube, following the sim mesh (nearest ring vertex facing +y)"""
    mat = mat or M['wood_dark']
    v = g['v']
    n_ring = 18
    nrows = len(v) // n_ring
    for i in range(n):
        zt = -(z0 + (z1 - z0) * i / max(n - 1, 1))
        # find row nearest z
        best = min(range(nrows), key=lambda r: abs(v[r * n_ring:(r + 1) * n_ring, 2].mean() - zt))
        ring = v[best * n_ring:(best + 1) * n_ring]
        k = int(np.argmax(ring[:, 1] - 0.0 * abs(ring[:, 0] - x)))   # most +y vertex
        # prefer verts close to x
        cand = [(kk, ring[kk]) for kk in range(n_ring) if ring[kk][1] > 0]
        kk, p = min(cand, key=lambda t: abs(t[1][0] - x)) if cand else (k, ring[k])
        frame.cyl(mat, (p[0], p[1] + r * 0.4, p[2]), r, r * 0.55, axis='y', seg=10, col=col, bev=0.001)
        f2 = frame


def details(fg, g, sleeves, mat, col, pockets=True):
    """coat details following the simulated mesh: hip pocket flaps, sleeve cuffs, collar roll"""
    v = g['v']
    n_ring = 18
    nrows = len(v) // n_ring
    nrm = vertex_normals(v, g['f'])
    dark = tuple(c * 0.82 for c in col)
    if pockets:
        row = int(nrows * 0.62)
        for sgn in (-1, 1):
            # ring vertex closest to the front-left/right hip (theta = 90deg +- 38deg)
            th = math.radians(90 + sgn * 38)
            k = int(round((th % TAU) / TAU * n_ring)) % n_ring
            idx = row * n_ring + k
            p = Vector(v[idx]); n = Vector(nrm[idx])
            phi = math.degrees(math.atan2(-n.x, n.y))
            fg.box(mat, tuple(p + n * 0.007), (0.085, 0.012, 0.03), r=(0, 0, phi), bev=0.003, col=dark, g=0)
            fg.box(mat, tuple(p + n * 0.004 + Vector((0, 0, 0.0))), (0.09, 0.006, 0.07), r=(0, 0, phi), bev=0.002, col=tuple(c * 0.9 for c in dark), g=0)
    for sl in sleeves:
        sv = sl['v']
        nr = 10
        last = [Vector(sv[len(sv) - 1 - nr + i]) for i in range(nr)]
        fg.tube(mat, last + [last[0]], 0.0075, seg=5, col=dark, closed=False, caps=False)


