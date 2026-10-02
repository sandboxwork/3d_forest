"""Hardware & small hand-modelled details: hinges, keyholes, knobs, pulls, nail heads, rivets, chipped paint, moulding."""
from bd_lib import *


def hinge_butt(f, c, h=0.07, w=0.045, face=1, axis_z=True, mat=None):
    """barrel hinge: two leaves + knuckle barrel + pin caps. c = knuckle centre (local). Leaves open flat along +/-x. face=+1: on +y face."""
    mat = mat or M['iron']
    x, y, z = c
    f.cyl(mat, (x, y, z), 0.0065, h, seg=10)
    for k in range(3):
        f.cyl(mat, (x, y, z - h / 2 + h * (k + 0.5) / 3), 0.0072, h / 3 - 0.0016, seg=10, bev=0.001)
    for s in (-1, 1):
        f.box(mat, (x + s * w / 2, y, z), (w, 0.0035, h * 0.92), bev=0.0008)
        for dz in (-0.02, 0.02):
            f.cyl(mat, (x + s * (w - 0.009), y + face * 0.002, z + dz), 0.0034, 0.003, axis='y', seg=8)


def strap_hinge(f, x0, x1, y, z, mat=None, thick=0.004, w=0.03):
    mat = mat or M['iron']
    f.box(mat, ((x0 + x1) / 2, y, z), (abs(x1 - x0), thick, w), bev=0.0008)
    # taper tip
    f.prism(mat, [(x1, w / 2), (x1 + 0.03 * (1 if x1 > x0 else -1), 0.0), (x1, -w / 2)], thick, c=(0, y, z), plane='xz')
    for t in (0.2, 0.5, 0.8):
        f.sphere(mat, (x0 + (x1 - x0) * t, y + thick / 2, z), 0.0042, seg=8, sq=(1, 0.5, 1))
    f.cyl(mat, (x0, y, z), 0.008, w * 1.15, seg=10)


def knob(f, c, axis='y', r=0.02, mat=None, sign=1):
    """turned brass knob on a rosette, pointing along +/-axis"""
    mat = mat or M['brass']
    R = {'y': (-90 * sign, 0, 0), 'x': (0, 90 * sign, 0), 'z': (0, 0, 0)}[axis]
    prof = profile_pts([(0.001, 0), (r * 1.15, 0.0), (r * 1.2, 0.002), (r * 0.5, 0.006), (r * 0.3, 0.014), (r * 0.8, 0.024), (r * 0.95, 0.032), (r * 0.7, 0.04), (0.001, 0.043)], 2)
    f.lathe(mat, c, prof, r=R, seg=16, cap=False)


def escutcheon(f, c, h=0.06, w=0.032, face=1, mat=None):
    """shield-shaped brass keyhole plate with an actual keyhole (dark). face=+1 -> faces +y."""
    mat = mat or M['brass']
    x, y, z = c
    arc = [(math.cos(a) * w / 2, h / 2 - w / 2 + math.sin(a) * w / 2) for a in np.linspace(0, math.pi, 7)]
    poly = arc + [(-w * 0.3, -h * 0.25), (-w * 0.2, -h / 2), (w * 0.2, -h / 2), (w * 0.3, -h * 0.25)]
    f.prism(mat, poly, 0.004, c=(x, y + face * 0.002, z), plane='xz', bev=0.0008, skip_down=False)
    cy_ = h / 2 - w / 2
    f.prism(mat, [(px * 0.78, (py - cy_) * 0.78 + cy_ * 0.78) for px, py in poly], 0.0016, c=(x, y + face * 0.0045, z), plane='xz', col=(1.15, 1.1, 1.0), skip_down=False)
    f.cyl(M['ink'], (x, y + face * 0.0058, z + 0.008), 0.0042, 0.001, axis='y', seg=10, col=(0.03, 0.025, 0.02))
    f.box(M['ink'], (x, y + face * 0.0058, z - 0.004), (0.0032, 0.001, 0.016), bev=0, col=(0.03, 0.025, 0.02))


def drop_pull(f, c, face=1, mat=None, w=0.07):
    """bail pull: two posts + curved handle on a backplate"""
    mat = mat or M['brass']
    x, y, z = c
    f.cyl(mat, (x, y + face * 0.002, z), 0.02, 0.004, axis='y', seg=14, bev=0.001)
    pts = [(x - w / 2, y + face * 0.006, z), (x - w / 2, y + face * 0.02, z), (x - w * 0.35, y + face * 0.03, z - 0.003), (x, y + face * 0.033, z - 0.004),
           (x + w * 0.35, y + face * 0.03, z - 0.003), (x + w / 2, y + face * 0.02, z), (x + w / 2, y + face * 0.006, z)]
    f.tube(mat, [Vector(p) for p in catmull(pts, 3)], 0.0045, seg=8)
    for s in (-1, 1):
        f.sphere(mat, (x + s * w / 2, y + face * 0.005, z), 0.0075, seg=10, sq=(1, 0.5, 1))


def ring_pull(f, c, face=1, mat=None, r=0.022):
    mat = mat or M['brass']
    x, y, z = c
    f.cyl(mat, (x, y + face * 0.002, z + r * 0.6), 0.015, 0.004, axis='y', seg=12, bev=0.001)
    f.sphere(mat, (x, y + face * 0.008, z + r * 0.6), 0.006, seg=8)
    f.torus(mat, (x, y + face * 0.012, z - r * 0.15 + r * 0.6), r, 0.0028, plane='xz', seg=22, rseg=6, a0=-20 if False else 0, a1=360)


def nail_row(f, pts, r=0.0035, mat=None, axis='y', sq=0.5):
    mat = mat or M['iron']
    for p in pts:
        f.sphere(mat, p, r, seg=8, rings=4, sq=(1, sq, 1) if axis == 'y' else (sq, 1, 1) if axis == 'x' else (1, 1, sq))


def chips(f, region_fn, n, size=(0.006, 0.018), mat=None, normal='y', col=(0.78, 0.6, 0.38), seed=3, lift=0.0007):
    """chipped paint: tiny irregular patches of the underlying wood colour. region_fn() -> (local point, normal axis letter+sign)"""
    mat = mat or M['wood_pine']
    r = random.Random(seed)
    for _ in range(n):
        p, nax = region_fn(r)
        s = r.uniform(*size)
        pts = []
        k = r.randint(5, 7)
        for i in range(k):
            a = TAU * i / k
            rr = s * r.uniform(0.45, 1.0)
            pts.append((math.cos(a) * rr * r.uniform(1.0, 1.9), math.sin(a) * rr))
        pl = {'y': 'xz', 'x': 'yz', 'z': 'xy'}[nax[0]]
        sg = 1 if nax[1] == '+' else -1
        pos = list(p)
        ax = 'xyz'.index(nax[0])
        pos[ax] += sg * lift
        f.prism(mat, pts, 0.0008, c=tuple(pos), plane=pl, col=jit(col, 0.15), skip_down=False, g=0)


def moulding_profile(kind='ogee', d=0.03, h=0.03):
    if kind == 'ogee':
        return [(0, 0), (d * 0.1, 0), (d * 0.3, h * 0.15), (d * 0.45, h * 0.45), (d * 0.7, h * 0.7), (d, h * 0.85), (d, h), (0, h)]
    if kind == 'cove':
        pts = [(0, 0)]
        for i in range(1, 8):
            a = math.pi / 2 * i / 7
            pts.append((d * (1 - math.cos(a)), h * math.sin(a)))
        pts += [(d, h), (0, h)]
        return pts
    if kind == 'round':
        pts = [(0, 0)]
        for i in range(0, 8):
            a = -math.pi / 2 + math.pi * i / 7
            pts.append((d * 0.5 + d * 0.5 * math.cos(a) * 0 + d * 0.5 * (math.cos(a)), h * 0.5 + h * 0.5 * math.sin(a)))
        return pts
    return [(0, 0), (d, 0), (d, h), (0, h)]


def run_moulding(f, a, b, prof, z, mat, col=(1, 1, 1), plane='x', front=True):
    """extrude a (depth,height) profile along local x from a to b at height z, depth growing toward +y (front=True) of the point (y given in prof)"""
    pass
