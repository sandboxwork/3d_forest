"""Kitchen counter with butcher-block top, fireclay sink, hand pump, framed doors; counter-top clutter; window-sill herbs."""
from kt_lib import *
from kt_ware import *
from kt_food import *
from kt_pots import *
from kt_dining import plank_bm, board

CX, CW, CD, CH = -2.25, 1.6, 0.6, 0.9
PAINT = {  # vertex-colour tints that turn the warm pine albedo into milk-paint colours
    'sage': (0.3, 0.62, 0.9), 'cream': (0.78, 0.95, 1.12), 'blue': (0.12, 0.38, 0.95), 'red': (0.27, 0.09, 0.14), 'ochre': (0.9, 0.78, 0.4),
    'white': (0.9, 1.1, 1.3), 'teal': (0.2, 0.62, 0.7), 'rose': (0.65, 0.35, 0.4)}


def paint(name, k=1.0, j=0.04):
    c = PAINT[name]
    kk = k * (1 + rnd.uniform(-j, j))
    return (c[0] * kk, c[1] * kk, c[2] * kk)


def bm_merge(dst, src, Mx):
    vm = {v: dst.verts.new(Mx @ v.co) for v in src.verts}
    for f in src.faces:
        try:
            dst.faces.new([vm[v] for v in f.verts])
        except ValueError:
            pass


def strap_hinge(f, p, length=0.11, w=0.016, side=1, mat='iron_black', y_dir=1, vertical=False):
    """flat strap hinge with pointed tip, rivets and a barrel; p = pivot point (local)"""
    pts = [(0, -w / 2), (length * 0.78, -w / 2), (length, 0), (length * 0.78, w / 2), (0, w / 2)]
    bm = _poly_ext(pts, 0.004)
    # orient: strap lies in plane x-z facing +y(local) by default
    Mx = f.M @ Matrix.Translation(p) @ Matrix.Rotation(math.radians(90), 4, 'X')
    if vertical:
        Mx = Mx @ Matrix.Rotation(math.radians(90), 4, 'Z')
    if side < 0:
        Mx = Mx @ Matrix.Rotation(math.pi, 4, 'Z')
    put(mat, bm, Mx @ Matrix.Translation((0, 0, -0.004)))
    bm.free()
    cyl(mat, None, 0.0065, w + 0.004, axis='x' if not vertical else 'z', seg=8, M=Mx @ Matrix.Translation((0, 0, 0.0)) @ (Matrix.Identity(4)) if False else f.M @ Matrix.Translation(p))
    for t in (0.3, 0.55, 0.8):
        q = Vector((t * length * side, 0, 0.0)) if not vertical else Vector((0, 0, t * length * side))
        dome(mat, f.M @ (Vector(p) + q + Vector((0, 0.0045, 0))), f.M.to_3x3() @ Vector((0, 1, 0)), r=0.0035) if False else None


def _poly_ext(pts, thick):
    bm = bmesh.new()
    f = bm.faces.new([bm.verts.new((x, y, 0)) for x, y in pts])
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]:
        v.co.z = thick
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def knob(f, p, mat='wood_dark', r=0.016, col=(1, 1, 1), brass=False):
    prof = [(0.001, 0.0), (0.0075, 0.0), (0.0085, 0.006), (0.006, 0.011), (r * 0.8, 0.016), (r, 0.022), (r * 0.8, 0.028), (r * 0.3, 0.031), (0.001, 0.0315)]
    lathe('brass' if brass else mat, None, prof, 12, M=f.M @ Matrix.Translation(p) @ Matrix.Rotation(math.radians(-90), 4, 'X'), cap=False, col=col)
    cyl('brass', None, r * 1.05, 0.003, axis='y', seg=12, M=f.M @ Matrix.Translation(p + Vector((0, 0.001, 0)))) if brass is False and False else None


def framed_door(f, cx, cz, w, h, y, tint, hinge=1, knob_side=-1, raised=True, bead=True, panel_split=False, mat='wood_pine'):
    """frame-and-panel door in front plane y of frame f (face toward +y local)."""
    t = 0.022
    sw = 0.05
    col = tint
    # frame: stiles + rails
    f.box(mat, (cx - w / 2 + sw / 2, y, cz), (sw, t, h), bev=0.003, seg=2, col=col, g=2, skip_down=False)
    f.box(mat, (cx + w / 2 - sw / 2, y, cz), (sw, t, h), bev=0.003, seg=2, col=col, g=2, skip_down=False)
    f.box(mat, (cx, y, cz + h / 2 - sw / 2), (w - 2 * sw + 0.004, t, sw), bev=0.003, seg=2, col=col, g=0, skip_down=False)
    f.box(mat, (cx, y, cz - h / 2 + sw / 2), (w - 2 * sw + 0.004, t, sw), bev=0.003, seg=2, col=col, g=0, skip_down=False)
    pw, ph = w - 2 * sw + 0.004, h - 2 * sw + 0.004
    # recessed panel with raised field and chamfer
    f.box(mat, (cx, y - 0.004, cz), (pw, 0.01, ph), bev=0.002, col=shade(col, 0.88), g=2, skip_down=False)
    if raised:
        pf = bmesh.new()
        bmesh.ops.create_cube(pf, size=1.0)
        for v in pf.verts:
            v.co.x *= pw - 0.014
            v.co.z *= ph - 0.014
            v.co.y *= 0.01
            if v.co.y > 0:      # chamfer toward the front face
                v.co.x *= 0.82 if abs(v.co.x) > 0 else 1
                v.co.z *= 0.86
        bmesh.ops.recalc_face_normals(pf, faces=pf.faces[:])
        put(mat, pf, f.M @ Matrix.Translation((cx, y + 0.004, cz)), col=shade(col, 1.04), g=2, skip_down=False)
        pf.free()
    if bead:   # small bead moulding inside the frame
        for (dx, dz, sx, sz) in ((0, ph / 2, pw, 0.006), (0, -ph / 2, pw, 0.006), (-pw / 2, 0, 0.006, ph), (pw / 2, 0, 0.006, ph)):
            f.box(mat, (cx + dx, y + 0.0055, cz + dz), (sx, 0.007, sz), bev=0.002, seg=2, col=shade(col, 1.02), skip_down=False)
    # hinges (strap, on hinge side) and knob
    hx = cx + hinge * (w / 2)
    for zz in (cz + h / 2 - 0.1, cz - h / 2 + 0.1):
        bm = _poly_ext([(0, -0.009), (0.095, -0.009), (0.115, 0), (0.095, 0.009), (0, 0.009)], 0.004)
        put('iron_black', bm, f.M @ Matrix.Translation((hx + (-hinge) * 0.0, y + t / 2 + 0.0, zz)) @ Matrix.Rotation(math.radians(90), 4, 'X') @ Matrix.Rotation(math.pi if hinge > 0 else 0, 4, 'Z') @ Matrix.Translation((-0.008 if hinge < 0 else -0.008, 0, 0)) if False else
            f.M @ Matrix.Translation((hx, y + t / 2, zz)) @ Matrix.Rotation(math.radians(-90), 4, 'X') @ Matrix.Rotation(math.pi if hinge < 0 else 0, 4, 'Z') @ Matrix.Translation((-0.1, 0, -0.0)))
        bm.free()
        cyl('iron_black', None, 0.0065, 0.022, axis='z', seg=8, M=f.M @ Matrix.Translation((hx + hinge * 0.0, y + t / 2 + 0.003, zz)))
        for k in range(3):
            dome('iron_black', f.p((hx - hinge * (0.03 + 0.028 * k), y + t / 2 + 0.004, zz)), f.M.to_3x3() @ Vector((0, 1, 0)), r=0.0036)
    kx = cx + knob_side * (w / 2 - 0.035)
    knob(f, Vector((kx, y + t / 2, cz + (0.0 if h < 0.7 else -0.1 * 0))), brass=True, r=0.0125)


def drawer_front(f, cx, cz, w, h, y, tint, mat='wood_pine'):
    t = 0.022
    f.box(mat, (cx, y, cz), (w, t, h), bev=0.003, seg=2, col=tint, g=0, skip_down=False)
    f.box(mat, (cx, y + 0.009, cz), (w - 0.07, 0.007, h - 0.06), bev=0.002, seg=2, col=shade(tint, 1.04), g=0, skip_down=False)
    # bin pull: brass back plate + hanging ring
    f.box('brass', (cx, y + t / 2 + 0.002, cz), (0.07, 0.004, 0.03), bev=0.0015, seg=2)
    f.cyl('brass', (cx, y + t / 2 + 0.008, cz + 0.006), 0.006, 0.01, axis='y', seg=8)
    torus('brass', None, 0.0125, 0.0023, plane='xz', M=f.M @ Matrix.Translation((cx, y + t / 2 + 0.015, cz - 0.004)) @ Matrix.Rotation(math.radians(90), 4, 'X') @ Matrix.Rotation(math.radians(8), 4, 'Y'), seg=12, rseg=5)
    for sx in (-1, 1):
        dome('brass', f.p((cx + sx * 0.028, y + t / 2 + 0.004, cz)), f.M.to_3x3() @ Vector((0, 1, 0)), r=0.0028)


def counter_body(f, tint):
    W, D, H = CW, CD, CH
    t = 0.022
    mat = 'wood_pine'
    # toe-kick plinth
    f.box(mat, (0, -0.02, 0.05), (W - 0.02, D - 0.1, 0.1), bev=0.002, col=shade(tint, 0.55), skip_down=True)
    # carcass sides + back + bottom shelf
    for s in (-1, 1):
        f.box(mat, (s * (W / 2 - t / 2), 0, 0.1 + (H - 0.14) / 2), (t, D, H - 0.14), bev=0.003, seg=2, col=shade(tint, 0.95), g=2, skip_down=False)
    f.box(mat, (0, -D / 2 + 0.01, 0.1 + (H - 0.14) / 2), (W - 2 * t, 0.014, H - 0.14), bev=0, col=shade(tint, 0.8), skip_down=False)
    f.box(mat, (0, 0, 0.12), (W - 2 * t, D - 0.04, 0.02), bev=0.002, col=shade(tint, 0.75), g=0, skip_down=False)
    # face frame: top rail, bottom rail, 4 stiles
    yf = D / 2 - 0.013
    f.box(mat, (0, yf - 0.011, 0.1 + 0.025), (W - 0.004, t, 0.05), bev=0.003, seg=2, col=tint, g=0, skip_down=False)
    f.box(mat, (0, yf - 0.011, H - 0.04 - 0.02), (W - 0.004, t, 0.04), bev=0.003, seg=2, col=tint, g=0, skip_down=False)
    bay = (W - 0.04) / 3
    for i in range(4):
        x = -W / 2 + 0.02 + i * bay
        f.box(mat, (x, yf - 0.011, 0.1 + (H - 0.14) / 2), (0.045 if 0 < i < 3 else 0.035, t, H - 0.14), bev=0.003, seg=2, col=tint, g=2, skip_down=False)
    # skirt trim & cap moulding under the top
    f.box(mat, (0, D / 2 + 0.004, 0.1 - 0.008), (W + 0.012, 0.016, 0.02), bev=0.004, seg=2, col=shade(tint, 1.05), g=0, skip_down=True)
    f.box(mat, (0, D / 2 + 0.002, H - 0.052), (W + 0.012, 0.012, 0.014), bev=0.004, seg=2, col=shade(tint, 1.05), g=0, skip_down=False)
    return bay, yf


def worktop(f, sink_lx):
    """butcher-block strips (individual boards) merged -> Boolean-cut sink opening -> bullnose edges"""
    W, D = CW + 0.04, CD + 0.05
    t = 0.04
    zt = CH - t / 2
    ns = 12
    sw = D / ns
    bm = bmesh.new()
    rr = random.Random(2)
    tints = []
    for i in range(ns):
        y = -D / 2 + (i + 0.5) * sw + 0.015
        pb = plank_bm(W - rr.uniform(0.0, 0.0), sw - 0.0016, t, bev=0.002, seg=1, maxlen=0.15, dent=0.0, seed=i)
        bm_merge(bm, pb, Matrix.Translation((0, y, 0)))
        pb.free()
        tints.append(rr.uniform(0.88, 1.08))
    # sink opening
    cb = cube_bm(0.5, 0.34, 0.2)
    bm = boolean(bm, [(cb, Matrix.Translation((sink_lx, 0.0, 0.0)))])
    cb.free()
    bm = disp(bm, 0.0004, 0.15, 2, direction='Z')
    inv = f.M.inverted()

    def cf(p):
        l = inv @ p
        i = int((l.y + D / 2 - 0.015) / sw)
        k = tints[max(0, min(ns - 1, i))]
        wear = 1 - 0.18 * math.exp(-((l.x - sink_lx) / 0.5) ** 2) * math.exp(-((l.y - 0.1) / 0.15) ** 2)   # darker, worn around the sink
        n = 1 + 0.06 * fbm(l.x * 8, l.y * 8, l.z, 1, 3, 2)
        return (k * wear * n, k * wear * n * 0.97, k * wear * n * 0.93)
    put('wood_oak', bm, f.M @ Matrix.Translation((0, 0.012, zt)), cfn=cf, g=0)
    bm.free()


def sink_basin(f, lx, zt):
    """fireclay basin: bevelled open box + Solidify, rim flange, drain strainer with plug chain"""
    w, d, h = 0.49, 0.33, 0.19
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    top = [fc for fc in bm.faces if fc.normal.z > 0.9]
    bmesh.ops.delete(bm, geom=top, context='FACES')
    for v in bm.verts:
        v.co.x *= w; v.co.y *= d; v.co.z = (v.co.z - 0.5) * h
    bmesh.ops.bevel(bm, geom=[e for e in bm.edges if len(e.link_faces) == 2 or True], offset=0.03, segments=3, affect='EDGES', clamp_overlap=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm = modbm(bm, [('SOLIDIFY', {'thickness': 0.011, 'offset': -1.0})])
    inv = f.M.inverted()
    base = f.M @ Matrix.Translation((lx, 0.0, zt))

    def cf(p):
        l = inv @ p
        z0 = zt - h
        stain = 0.88 + 0.12 * min(1, (l.z - z0) / 0.1)
        k = 1 + 0.05 * fbm(l.x * 30, l.y * 30, l.z * 30, 1, 2, 2)
        drain = math.hypot(l.x - lx, l.y)
        if l.z < z0 + 0.02 and drain < 0.09:
            stain *= 0.85
        return (0.96 * stain * k, 0.95 * stain * k, 0.9 * stain * k)
    put('enamel', bm, base, cfn=cf)
    bm.free()
    # rim flange
    for (dx, dy, sx, sy) in ((0, d / 2 + 0.013, w + 0.056, 0.026), (0, -d / 2 - 0.013, w + 0.056, 0.026), (w / 2 + 0.013, 0, 0.026, d), (-w / 2 - 0.013, 0, 0.026, d)):
        f.box('enamel', (lx + dx, dy, zt + 0.003), (sx, sy, 0.008), bev=0.003, seg=2, col=(0.95, 0.94, 0.9), skip_down=False)
    # drain strainer
    zb = zt - h + 0.011
    f.cyl('brass', (lx, 0.0, zb + 0.003), 0.036, 0.006, seg=16, bev=0.002)
    for k in range(7):
        a = TAU * k / 7
        for rr_ in (0.0, 0.019):
            if rr_ == 0 and k:
                continue
            f.cyl('ink', (lx + rr_ * math.cos(a), rr_ * math.sin(a), zb + 0.0062), 0.0045, 0.0012, seg=6)
    # plug on a chain hanging over the rim
    f.cyl('brass', (lx + 0.18, 0.1, zb + 0.004), 0.022, 0.012, seg=12, bev=0.003)
    p0 = f.p((lx + 0.18, 0.1, zb + 0.01))
    link_chain(p0 + Vector((0, 0, 0.0)), f.p((lx + 0.2, d / 2 + 0.0, zt - 0.02)), r=0.0016, L=0.012, mat='brass', sag=0.01)
    f.box('brass', (lx + 0.2, d / 2 + 0.03, zt + 0.008), (0.012, 0.008, 0.02), bev=0.002)


def hand_pump(f, lx, ly, zt):
    """cast iron hand pump: flange w/ bolts, ringed body, cap, curved spout, pivoting lever with wooden grip, link rod"""
    cf = None
    base = Vector((lx, ly, zt))
    # flange plate with 4 hex bolts
    f.cyl('iron_paint', (lx, ly, zt + 0.006), 0.066, 0.012, seg=16, bev=0.003)
    f.cyl('iron_paint', (lx, ly, zt + 0.0145), 0.052, 0.005, seg=14, bev=0.0015)
    for k in range(4):
        a = TAU * k / 4 + math.pi / 4
        f.cyl('iron_paint', (lx + 0.052 * math.cos(a), ly + 0.052 * math.sin(a), zt + 0.015), 0.0072, 0.007, seg=6)
    # body: ringed column
    prof = [(0.036, 0.0), (0.04, 0.008), (0.034, 0.02), (0.031, 0.05), (0.031, 0.25), (0.036, 0.255), (0.036, 0.262), (0.031, 0.268), (0.031, 0.3), (0.0385, 0.307), (0.0385, 0.315), (0.034, 0.322), (0.026, 0.335), (0.032, 0.34), (0.03, 0.355), (0.02, 0.375), (0.001, 0.385)]
    f.lathe('iron_paint', (lx, ly, zt + 0.0165), prof, seg=18)
    f.cyl('iron_paint', (lx, ly, zt + 0.0165 + 0.15), 0.0345, 0.012, seg=14, bev=0.002)
    # lever fulcrum clevis (two cheek plates normal to y + pin along y); lever runs sideways parallel to the wall
    zf = zt + 0.0165 + 0.345
    for s in (-1, 1):
        f.box('iron_paint', (lx, ly + s * 0.017, zf), (0.07, 0.008, 0.05), bev=0.003, seg=2)
    f.cyl('iron_paint', (lx, ly, zf), 0.0065, 0.05, axis='y', seg=8)
    lev = [Vector((lx, ly + 0.0, zf - 0.04)), Vector((lx, ly + 0.0, zf - 0.01)), Vector((lx, ly, zf)), Vector((lx - 0.15, ly, zf + 0.04)), Vector((lx - 0.3, ly, zf + 0.12)), Vector((lx - 0.38, ly, zf + 0.2))]
    lev = polyline_smooth(lev, 5)
    f.sweep('iron_paint', [(math.cos(TAU * k / 8), math.sin(TAU * k / 8)) for k in range(8)], lev, scale=lambda t: (0.0095 - 0.003 * t, 0.0095 - 0.003 * t))
    f.sweep('wood_dark', [(math.cos(TAU * k / 8), math.sin(TAU * k / 8)) for k in range(8)], lev[-12:], scale=lambda t: (0.012, 0.012), col=(0.5, 0.35, 0.25))
    # pump rod: from the lever's short arm up into the cap
    f.tube('iron_paint', [Vector((lx, ly, zf - 0.04)), Vector((lx, ly, zt + 0.375))], 0.004, seg=6)
    # spout: cast, flared, curving over the basin
    sp = bez((lx, ly + 0.025, zt + 0.205), (lx, ly + 0.1, zt + 0.21), (lx, ly + 0.17, zt + 0.19), (lx, ly + 0.2, zt + 0.12), 12)
    n = len(sp)
    f.sweep('iron_paint', [(math.cos(TAU * k / 10), math.sin(TAU * k / 10)) for k in range(10)], sp, scale=lambda t: (0.021 - 0.009 * t, 0.021 - 0.009 * t), caps=False)
    f.lathe('iron_paint', (lx, ly + 0.2, zt + 0.1), [(0.0125, 0.02), (0.0145, 0.012), (0.0165, 0.0), (0.0135, -0.004), (0.0105, 0.0)], seg=10, cap=False) if False else \
        f.lathe('iron_paint', (lx, ly + 0.2, zt + 0.1), [(0.0115, 0.025), (0.0125, 0.012), (0.0175, 0.0), (0.0145, -0.005), (0.0105, -0.004)], seg=10, cap=False)
    # hanging water bead at the spout tip
    f.sphere('water', (lx, ly + 0.2, zt + 0.087), 0.0035, seg=8, rings=5, sq=(1, 1, 1.4))
    # brass priming cup
    f.lathe('brass', (lx, ly - 0.0, zt + 0.0165 + 0.385), [(0.001, 0), (0.014, 0.0), (0.0125, 0.01), (0.006, 0.02), (0.001, 0.022)], seg=10, cap=False)


def drying_rack(f, lx, ly, zt, rot=0):
    """wooden dish rack: two end frames, dowel slats, plates standing on edge, cups"""
    g = Fr(f.p((lx, ly, 0)) + Vector((0, 0, 0)), f.rot + rot, None)
    g.pos.z = F + zt  # world z of the counter top
    W, D = 0.34, 0.24
    z0 = F + zt
    gz = Fr((g.pos.x, g.pos.y, z0), f.rot + rot)
    for s in (-1, 1):
        gz.box('wood_pine', (0, s * (D / 2 - 0.01), 0.015), (W, 0.022, 0.03), bev=0.003, seg=2, col=(0.85, 0.75, 0.62), g=0)
    for s in (-1, 1):
        gz.box('wood_pine', (s * (W / 2 - 0.011), 0, 0.015), (0.022, D, 0.03), bev=0.003, seg=2, col=(0.85, 0.75, 0.62), g=1)
    # lower slats
    for k in range(9):
        gz.cyl('wood_pine', (-W / 2 + 0.03 + k * (W - 0.06) / 8, 0, 0.034), 0.006, D - 0.03, axis='y', seg=6, col=(0.9, 0.8, 0.68))
    # upright dowels for plates (two rows)
    for k in range(7):
        x = -W / 2 + 0.03 + k * (W - 0.06) / 6
        for sy in (-1, 1):
            gz.cyl('wood_pine', (x, sy * (D / 2 - 0.02), 0.07), 0.0055, 0.1, seg=6, col=(0.9, 0.8, 0.68))
    for sy in (-1, 1):
        gz.cyl('wood_pine', (0, sy * (D / 2 - 0.02), 0.115), 0.0055, W - 0.04, axis='x', seg=6, col=(0.9, 0.8, 0.68))
    # plates standing in the rack
    for k in range(3):
        x = -W / 2 + 0.06 + k * 0.07
        P = gz.p((x, 0, 0.115))
        plate(P, r=0.1, glaze='cream', rim='blue' if k != 1 else 'green', rot=(0, 90, gz.rot + 90), seg=14, lod=1)
    # cup upside down on the end
    P = gz.p((W / 2 - 0.05, 0.0, 0.12))
    mug(P, glaze='blue', r=0.036, h=0.075, rot=(180, 0, 0), seg=12)


def counter(sink_world_x=-2.2):
    f = Fr((CX, WY - CD / 2, F), 180)
    tint = paint('sage')
    bay, yf = counter_body(f, tint)
    lx = -(sink_world_x - CX)    # local x of sink centre (rot 180 mirrors x)
    # doors / drawer fronts
    n = 3
    for i in range(n):
        cx = -CW / 2 + 0.02 + bay * (i + 0.5)
        if i == 1:
            drawer_front(f, cx, CH - 0.04 - 0.08 - 0.02, bay - 0.01, 0.15, yf + 0.0, paint('sage', 1.05))
            framed_door(f, cx, 0.1 + 0.025 + (CH - 0.04 - 0.05 - 0.1 - 0.16) / 2, bay - 0.01, CH - 0.04 - 0.05 - 0.1 - 0.17, yf + 0.0, paint('sage', 0.98), hinge=-1, knob_side=1)
        else:
            framed_door(f, cx, 0.1 + 0.025 + (CH - 0.04 - 0.05 - 0.1 - 0.0) / 2 - 0.0, bay - 0.01, CH - 0.04 - 0.05 - 0.1 - 0.0, yf + 0.0, paint('sage', 1.0 + 0.04 * (i - 1)),
                        hinge=-1 if i == 0 else 1, knob_side=1 if i == 0 else -1)
    worktop(f, lx)
    sink_basin(f, lx, CH)
    hand_pump(f, lx, -CD / 2 + 0.085, CH + 0.02 - 0.02)
    collider_f(f, CW + 0.04, CD + 0.05, F + CH + 0.02)
    interact('sink_pump', (CX, WY - 0.12, F + 1.25), '손 펌프가 달린 싱크대')
    return f


def counter_props():
    f = Fr((CX, WY - CD / 2, F), 180)
    zc = F + CH + 0.02       # worktop surface (world)
    rr = random.Random(4)

    def at(wx, wy, z=None):
        return Vector((wx, wy, zc if z is None else z))
    # ---------- LEFT of the sink: cutting board with knife, veg, mortar and pestle, tea tins, crock
    bx, by = -2.84, 2.82
    cb = Fr((bx, by, zc), 8)
    bm = cube_bm(0.4, 0.26, 0.024, off=(0, 0, 0.012))
    bmesh.ops.bevel(bm, geom=[e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co).z) > 0.01], offset=0.012, segments=3, affect='EDGES')
    bev_bm(bm, 0.0025, 2)
    cbm = cyl_bm(0.008, 0.06, 12)
    bm = boolean(bm, [(cbm, Matrix.Translation((0.17, 0.0, 0.012)))])
    cbm.free()
    for axis in (0, 1):
        es = [e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co)[axis]) > 0.1 and abs((e.verts[0].co - e.verts[1].co)[axis]) > 0.9 * (e.verts[0].co - e.verts[1].co).length]
        if es:
            bmesh.ops.subdivide_edges(bm, edges=es, cuts=3, use_grid_fill=True)
    bm = disp(bm, 0.0006, 0.06, 2, direction='Z')
    # knife cuts and stains as vertex colour
    put('wood_oak', bm, cb.M, col=(0.95, 0.88, 0.76), g=0)
    bm.free()
    zb = zc + 0.024
    # sliced carrots and cucumber rounds, onion rings, whole veg
    for k in range(8):
        slice_disc(cb.p((-0.12 + 0.017 * k + rr.uniform(-0.003, 0.003), -0.02 + 0.012 * math.sin(k * 1.3), 0)) + Vector((0, 0, zb - zc + 0.0 + 0.0)) * 0 + Vector((0, 0, 0)) if False else Vector((cb.p((-0.12 + 0.017 * k, -0.02 + 0.012 * math.sin(k * 1.3), 0)).x, cb.p((-0.12 + 0.017 * k, -0.02 + 0.012 * math.sin(k * 1.3), 0)).y, zb + 0.003 * (k % 2))),
                   0.0125, 0.004, (0.88, 0.32, 0.05), (0.95, 0.55, 0.2), rot=(rr.uniform(-8, 8), rr.uniform(-8, 8), rr.uniform(0, 360)))
    for k in range(6):
        P = cb.p((0.02 + 0.016 * k, 0.07 - 0.01 * (k % 2), 0)); P.z = zb + 0.002 * (k % 3)
        slice_disc(P, 0.016, 0.0035, (0.3, 0.45, 0.2), (0.75, 0.85, 0.55), rot=(rr.uniform(-6, 6), rr.uniform(-6, 6), rr.uniform(0, 360)))
    P = cb.p((-0.07, 0.08, 0)); P.z = zb
    place('food_vc', carrot_bm(0.17, seed=2), P + Vector((0, 0, 0.012)), rot=(90, 0, 200 + 8), scale=1.0)
    P = cb.p((-0.12, -0.08, 0)); P.z = zb
    place('food_vc', onion_bm(3, r=0.034), P, rot=(0, 0, 33))
    P = cb.p((-0.04, -0.09, 0)); P.z = zb
    for k in range(3):
        onion_ring(P + Vector((0.0 + 0.0, 0.0, 0.0017 * k)) + Vector((0.012 * k, 0.003, 0.0)), 0.016 + 0.003 * k, rot=(0, 0, 0))
    P = cb.p((0.1, -0.05, 0)); P.z = zb
    place('food_vc', tomato_bm(4), P, rot=(0, 0, 10))
    knife(cb.p((0.11, 0.08, 0)) + Vector((0, 0, 0)) + Vector((0, 0, zb - cb.pos.z)), rot=cb.rot + 70, L=0.24, hand=0.11) if False else knife(Vector((cb.p((0.1, 0.07, 0)).x, cb.p((0.1, 0.07, 0)).y, zb)), rot=cb.rot + 115, L=0.25, hand=0.115)
    # mortar & pestle
    mortar_pestle(at(-2.66, 3.09), r=0.062, rot=20)
    # crock with wooden utensils
    P = at(-2.97, 3.12)
    prof = [(0.001, 0.0), (0.05, 0.0), (0.056, 0.012), (0.061, 0.07), (0.059, 0.115), (0.064, 0.123), (0.062, 0.128), (0.052, 0.123), (0.05, 0.1), (0.001, 0.1)]
    lathe('ceramic', P, prof, 20, col=G('ochre'), cap=False, cfn=zband_cfn(xf(P), [(0.0, 0.04, G('brown'))], G('ochre'), 0.05, 4), split=('z', [0.04]))
    for k, (ax, ay, ln, kind) in enumerate(((0.02, 0.01, 0.3, 'spoon'), (-0.02, 0.0, 0.28, 'ladle'), (0.0, -0.02, 0.26, 'skim'), (0.025, -0.02, 0.27, 'spoon'), (-0.03, 0.02, 0.25, 'spoon'))):
        Mt = xf(P + Vector((ax, ay, 0.04)), (-8 - 4 * k + (k % 2) * 14, (k - 2) * 7, k * 60))
        if kind == 'spoon':
            wooden_spoon(Mt @ Vector((0, 0, 0)), rot=None, L=ln) if False else None
            sweep('wood_oak', [(math.cos(TAU * j / 6), math.sin(TAU * j / 6)) for j in range(6)], [Mt @ Vector((0, 0, 0)), Mt @ Vector((0, 0, ln))], scale=lambda t: (0.006 + 0.004 * t, 0.0045 + 0.0015 * t) if False else (0.0055 + 0.002 * t, 0.0055 + 0.002 * t))
            sweep('wood_oak', [(math.cos(TAU * j / 8), math.sin(TAU * j / 8)) for j in range(8)], [Mt @ Vector((0, 0, ln)), Mt @ Vector((0, 0, ln + 0.07))], scale=lambda t: (0.013 * (1 - 0.3 * t), 0.0035))
        elif kind == 'ladle':
            sweep('iron_black', [(math.cos(TAU * j / 6), math.sin(TAU * j / 6)) for j in range(6)], [Mt @ Vector((0, 0, 0)), Mt @ Vector((0, 0, ln))], scale=lambda t: (0.004, 0.004))
            lathe('iron_black', None, [(0.001, 0.0), (0.024, 0.006), (0.036, 0.022), (0.034, 0.025), (0.022, 0.012), (0.001, 0.003)], 12, M=Mt @ Matrix.Translation((0, 0, ln)) @ Matrix.Rotation(math.radians(90), 4, 'X'), cap=False)
        else:
            sweep('wood_dark', [(math.cos(TAU * j / 6), math.sin(TAU * j / 6)) for j in range(6)], [Mt @ Vector((0, 0, 0)), Mt @ Vector((0, 0, ln))], scale=lambda t: (0.0065, 0.0065))
            box('wood_dark', None, (0.05, 0.004, 0.06), M=Mt @ Matrix.Translation((0, 0, ln + 0.03)), bev=0.0015, col=(0.7, 0.55, 0.45))
    # tea tins: stack of three with embossed label atlas cells
    tin_cells = [(0, 0), (1, 0), (2, 0), (3, 0)]
    for k, (tx, ty, th, tr, cell) in enumerate(((-3.0, 2.93, 0.14, 0.045, (0, 0)), (-2.92, 2.95, 0.11, 0.04, (1, 0)), (-2.98, 3.03, 0.1, 0.036, (2, 0)))):
        tin_can(at(tx, ty), tr, th, cell, rot=rr.uniform(0, 360))
    # soap + brush by the sink
    box('wax', at(-2.5, 2.74, 0.015) if False else at(-2.5, 2.74) + Vector((0, 0, 0.0)), (0.07, 0.045, 0.03), bev=0.008, seg=2, anchor='b', col=(0.9, 0.84, 0.7), rot=(0, 0, 15))
    scrub_brush(at(-2.46, 2.66), rot=30)
    # ---------- RIGHT of the sink
    # jars at the back
    jar_at(at(-1.86, 3.15), 'pickles', seed=1)
    jar_at(at(-1.75, 3.155), 'jam', seed=2)
    jar_at(at(-1.64, 3.15), 'beans', seed=3, tall=True)
    jar_at(at(-1.53, 3.16), 'flour', seed=4, tall=True)
    # egg bowl
    P = at(-1.8, 2.86)
    bowl(P, r=0.085, h=0.055, glaze='blue', rim='cream', rot=(0, 0, 0), seg=20)
    for k in range(7):
        a = TAU * k / 6 if k < 6 else 0
        r_ = 0.04 if k < 6 else 0.0
        place('food_vc', egg_bm(0.021, col=(0.78, 0.66, 0.5) if k % 3 else (0.45, 0.25, 0.12), seed=k), P + Vector((r_ * math.cos(a), r_ * math.sin(a), 0.016 + (0.02 if k == 6 else 0.0))), rot=(rr.uniform(70, 100), 0, rr.uniform(0, 360)))
    # rolling pin + floured dough ball on a floured patch
    rolling_pin(at(-1.68, 2.72) + Vector((0, 0, 0.0)), rot=4, L=0.3)
    P = at(-1.55, 2.84)
    place('food_matte', lathe_solid_dough(), P, rot=(0, 0, 10), col=(0.95, 0.9, 0.78))
    # balance scale
    balance_scale(at(-1.52, 2.9) + Vector((0, 0, 0.0)), rot=190) if False else None
    # oil lamp (lamp_kit_4) with chimney
    oil_lamp_k(at(-1.52, 2.95), name='lamp_kit_4')
    drying_rack(f, -(-2.2 - CX), 0.0, CH + 0.02)
    return


def lathe_solid_dough():
    bm = lathe_bm([(0.001, 0.0), (0.04, 0.002), (0.06, 0.015), (0.05, 0.03), (0.02, 0.038), (0.001, 0.04)], 12, cap=False)
    for v in bm.verts:
        v.co *= 1 + 0.06 * fbm(v.co.x * 30, v.co.y * 30, v.co.z * 30, 1, 3, 2)
    return bm


def tin_can(P, r, h, cell, rot=0):
    """lidded tea tin: tin body w/ label band (atlas cell), lid with rim and knob"""
    Mx = xf(P, (0, 0, rot))
    lathe('tin', None, [(r * 0.94, 0.0), (r, 0.003), (r, h - 0.02), (r * 0.98, h - 0.018), (r * 0.98, h - 0.014)], 18, M=Mx, cap=True)
    # label wrapped around (atlas cell)
    cu, cv = cell
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    seg = 18
    z0, z1 = h * 0.18, h * 0.78
    for i in range(seg):
        a0, a1 = TAU * i / seg, TAU * (i + 1) / seg
        rr_ = r + 0.0006
        vs = [bm.verts.new((rr_ * math.cos(a0), rr_ * math.sin(a0), z0)), bm.verts.new((rr_ * math.cos(a1), rr_ * math.sin(a1), z0)),
              bm.verts.new((rr_ * math.cos(a1), rr_ * math.sin(a1), z1)), bm.verts.new((rr_ * math.cos(a0), rr_ * math.sin(a0), z1))]
        f_ = bm.faces.new(vs)
        for l, (u, v) in zip(f_.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
            uu = (i + u) / seg
            uu = uu if uu <= 1 else 1
            l[ul].uv = (cu * 0.25 + 0.001 + min(0.248, (min(uu * 1.0, 1.0)) * 0.248), cv * 0.25 + 0.001 + v * 0.248)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    put('label', bm, Mx, uvs=1.0)
    bm.free()
    lathe('tin', None, [(r * 1.02, h - 0.02), (r * 1.03, h - 0.006), (r * 1.0, h), (r * 0.7, h + 0.003), (r * 0.25, h + 0.006), (0.0085, h + 0.008), (0.0085, h + 0.014), (0.001, h + 0.016)], 18, M=Mx, cap=False)


def scrub_brush(P, rot=0):
    Mx = xf(P, (0, 0, rot))
    box('wood_oak', None, (0.09, 0.034, 0.016), M=Mx @ Matrix.Translation((0, 0, 0.008 + 0.008)), bev=0.004, seg=2, col=(0.95, 0.85, 0.7))
    for i in range(14):
        for j in range(3):
            tube('straw', [Mx @ Vector((-0.04 + i * 0.0062, -0.009 + j * 0.009, 0.0)), Mx @ Vector((-0.04 + i * 0.0062, -0.009 + j * 0.009, 0.01))], 0.0016, seg=3, caps=False, col=(0.75, 0.6, 0.35))


def oil_lamp_k(P, name='lamp_kit_4', h=0.2):
    """glass kerosene lamp: brass foot, glass font with oil, burner, tall chimney, flame"""
    Mx = xf(P)
    lathe('brass', None, [(0.001, 0), (0.05, 0), (0.053, 0.006), (0.04, 0.014), (0.02, 0.022), (0.013, 0.03), (0.016, 0.04)], 18, M=Mx, cap=False)
    lathe('glass', None, [(0.016, 0.04), (0.035, 0.052), (0.055, 0.085), (0.056, 0.105), (0.04, 0.128), (0.02, 0.138), (0.018, 0.138), (0.034, 0.126), (0.052, 0.104), (0.05, 0.085), (0.03, 0.055), (0.012, 0.045)], 20, M=Mx, cap=False)
    lathe('liquid', None, [(0.0, 0.07), (0.044, 0.07), (0.046, 0.06), (0.0, 0.052)], 16, M=Mx, cap=False, col=(0.95, 0.85, 0.5))
    lathe('brass', None, [(0.02, 0.136), (0.03, 0.14), (0.034, 0.15), (0.03, 0.158), (0.019, 0.16), (0.019, 0.166)], 14, M=Mx, cap=False)
    # chimney (thin glass flaring tube)
    lathe('glass', None, [(0.017, 0.166), (0.026, 0.19), (0.027, 0.2), (0.017, 0.236), (0.02, 0.29), (0.021, 0.3), (0.0195, 0.3), (0.0185, 0.29), (0.0155, 0.236), (0.025, 0.2), (0.0245, 0.19), (0.015, 0.166)], 16, M=Mx, cap=False)
    box('brass', None, (0.018, 0.003, 0.008), M=Mx @ Matrix.Translation((0.0, 0, 0.166)), bev=0.001)
    cyl('brass', None, 0.0035, 0.012, axis='x', seg=6, M=Mx @ Matrix.Translation((0.032, 0, 0.145)))
    flame_part(P + Vector((0, 0, 0.196)), 2.3, name=name, inten=1.1, dist=5.0)


def jar_at(P, kind, seed=0, tall=False):
    """glass jar with contents; jam has waxed paper cover tied with twine, pickles in brine, beans (geometry-nodes scatter), flour"""
    rr = random.Random(seed)
    r = 0.045 if not tall else 0.04
    h = 0.12 if not tall else 0.17
    Mx = xf(P)
    wall = 0.0028
    prof = [(0.001, 0.0), (r * 0.92, 0.0), (r, 0.004), (r, h * 0.78), (r * 0.9, h * 0.88), (r * 0.62, h * 0.94), (r * 0.6, h * 0.99), (r * 0.64, h), (r * 0.64 - wall, h), (r * 0.6 - wall, h * 0.97), (r * 0.62 - wall, h * 0.93),
            (r * 0.9 - wall, h * 0.87), (r - wall, h * 0.77), (r - wall, 0.007), (0.001, 0.0065)]
    lathe('glass', None, prof, 18, M=Mx, cap=False)
    zc_ = 0.0065
    if kind == 'pickles':
        lathe('liquid', None, [(0.001, zc_), (r - 0.004, zc_), (r - 0.004, h * 0.8), (0.001, h * 0.8)], 16, M=Mx, col=(0.55, 0.62, 0.2), cap=False)
        for k in range(4):
            a = TAU * k / 4 + rr.uniform(-0.3, 0.3)
            c0 = Vector((0.012 * math.cos(a), 0.012 * math.sin(a), 0.015))
            tube('food_vc', [Mx @ (c0 + Vector((0, 0, 0))), Mx @ (c0 + Vector((0.004 * math.cos(a), 0.004 * math.sin(a), 0.07)))], 0.0125, seg=7, col=(0.28, 0.4, 0.12))
        for k in range(3):
            place('herb_vc', leaf_bm(0.03, 0.006, curl=0.3, n=3, col=(0.2, 0.4, 0.1)), P + Vector((0.018 * math.cos(k * 2.1), 0.018 * math.sin(k * 2.1), 0.09)), rot=(rr.uniform(60, 120), 0, rr.uniform(0, 360)))
        lid_screw(Mx, r, h)
        label_on(Mx, r, h, (0, 2))
    elif kind == 'jam':
        lathe('food_vc', None, [(0.001, zc_), (r - 0.004, zc_), (r - 0.004, h * 0.88), (0.001, h * 0.9)], 16, M=Mx, col=(0.42, 0.04, 0.1), cap=False)
        # waxed paper cap pleated around the neck + twine
        paper_cap(Mx, r * 0.66, h * 0.93, seed)
        # sticky jam drip run down the outside of the glass
        tube('food_vc', [Mx @ Vector((r * 0.74, 0.0, h * 0.86)), Mx @ Vector((r * 1.0, 0.0, h * 0.78)), Mx @ Vector((r * 1.003, 0.0, h * 0.5))], [0.0045, 0.003, 0.0022], seg=5, caps=True, col=(0.4, 0.04, 0.09))
        label_on(Mx, r, h, (2, 1))
    elif kind == 'beans':
        lathe('food_vc', None, [(0.001, zc_), (r - 0.004, zc_), (r - 0.004, h * 0.78), (0.001, h * 0.78)], 16, M=Mx, col=(0.35, 0.22, 0.12), cap=False)
        # layer of beans by GN scatter on a disc at the top of the fill
        surf = bmesh.new()
        bmesh.ops.create_circle(surf, cap_ends=True, cap_tris=True, segments=14, radius=r - 0.005)
        vars_ = []
        for j, c in enumerate(((0.62, 0.45, 0.25), (0.75, 0.62, 0.4), (0.5, 0.3, 0.18))):
            bb = sphere_bm(0.0065, 5, 3, (1.4, 0.9, 0.8))
            colorize(bb, lambda p, c=c: c)
            vars_.append({'parts': [(bb, 'food_vc')]})
        outs = gn_scatter(surf, vars_, distance=0.0115, density=9000, seed=seed * 3 + 1, scale=(0.9, 1.1), tilt=0.5, tint=0.1, surf_M=Mx @ Matrix.Translation((0, 0, h * 0.78)))
        for v in vars_:
            for (bb, mn) in v['parts']:
                bb.free()
        surf.free()
        put_outs(outs, Matrix.Identity(4))
        lid_screw(Mx, r, h)
        label_on(Mx, r, h, (1, 2))
    else:   # flour
        lathe('food_matte', None, [(0.001, zc_), (r - 0.004, zc_), (r - 0.004, h * 0.8), (0.001, h * 0.8)], 16, M=Mx, col=(0.93, 0.9, 0.82), cap=False)
        lid_screw(Mx, r, h, cork=True)
        label_on(Mx, r, h, (3, 3) if False else (0, 3))


def lid_screw(Mx, r, h, cork=False):
    if cork:
        lathe('wood_pine', None, [(r * 0.58, h * 0.9), (r * 0.58, h * 1.0), (r * 0.64, h * 1.0), (r * 0.64, h * 1.04), (r * 0.5, h * 1.06), (0.001, h * 1.06)], 14, M=Mx, col=(0.8, 0.65, 0.45), cap=False)
        return
    lathe('tin', None, [(r * 0.66, h * 0.9), (r * 0.7, h * 0.92), (r * 0.7, h * 1.02), (r * 0.68, h * 1.04), (r * 0.5, h * 1.045), (0.001, h * 1.045)], 18, M=Mx, cap=False)
    for k in range(18):   # knurled rim: ridges
        a = TAU * k / 18
        box('tin', None, (0.0022, 0.0022, h * 0.09), M=Mx @ Matrix.Translation((r * 0.705 * math.cos(a), r * 0.705 * math.sin(a), h * 0.97)) @ Matrix.Rotation(a, 4, 'Z'), bev=0)


def label_on(Mx, r, h, cell):
    cu, cv = cell
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    seg = 14
    z0, z1 = h * 0.22, h * 0.62
    ar = math.radians(110)
    for i in range(seg):
        a0, a1 = -ar / 2 + ar * i / seg - math.pi / 2, -ar / 2 + ar * (i + 1) / seg - math.pi / 2
        rr_ = r + 0.0005
        vs = [bm.verts.new((rr_ * math.cos(a0), rr_ * math.sin(a0), z0)), bm.verts.new((rr_ * math.cos(a1), rr_ * math.sin(a1), z0)),
              bm.verts.new((rr_ * math.cos(a1), rr_ * math.sin(a1), z1)), bm.verts.new((rr_ * math.cos(a0), rr_ * math.sin(a0), z1))]
        f_ = bm.faces.new(vs)
        for l, (u, v) in zip(f_.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
            l[ul].uv = (cu * 0.25 + 0.002 + (i + u) / seg * 0.246, cv * 0.25 + 0.002 + v * 0.246)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    put('label', bm, Mx, uvs=1.0)
    bm.free()


def paper_cap(Mx, rneck, zneck, seed=0):
    """greaseproof paper cover: radial pleats folded around the neck, tied with twine"""
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    seg = 36
    rows = 7
    R0 = rneck + 0.0015
    rings = []
    for j in range(rows + 1):
        t = j / rows                   # 0 at top centre, 1 at the skirt hem
        if j == 0:
            rings.append([bm.verts.new((0, 0, zneck + 0.014))])
            continue
        ring = []
        for i in range(seg):
            a = TAU * i / seg
            if t < 0.35:
                rad = R0 * (t / 0.35)
                z = zneck + 0.014 - 0.004 * (t / 0.35) ** 2
            else:
                u = (t - 0.35) / 0.65
                pleat = 0.0065 * math.sin(7 * a + seed) * (0.4 + u)
                rad = R0 * (1.0 + 0.0 * u) + 0.012 * u ** 1.2 + pleat * u
                z = zneck + 0.01 - 0.062 * u ** 0.9 + 0.002 * math.sin(13 * a + 2) * u
            ring.append(bm.verts.new((rad * math.cos(a), rad * math.sin(a), z)))
        rings.append(ring)
    for j in range(rows):
        a, b = rings[j], rings[j + 1]
        for i in range(seg):
            i2 = (i + 1) % seg
            if len(a) == 1:
                f_ = bm.faces.new([a[0], b[i2], b[i]])
            else:
                f_ = bm.faces.new([a[i], a[i2], b[i2], b[i]])
            for l in f_.loops:
                l[ul].uv = (l.vert.co.x * 4, l.vert.co.y * 4 + l.vert.co.z * 2)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    put('paper', bm, Mx, col=(0.96, 0.93, 0.82))
    bm.free()
    # twine wraps and bow
    for k in range(3):
        torus('rope', None, R0 + 0.0035, 0.0013, plane='xy', M=Mx @ Matrix.Translation((0, 0, zneck - 0.004 - k * 0.0035)), seg=18, rseg=4, col=(0.46, 0.34, 0.19))
    for s in (-1, 1):
        tube('rope', [Mx @ Vector((R0 + 0.003, 0, zneck - 0.007)), Mx @ Vector((R0 + 0.014, s * 0.01, zneck - 0.02)), Mx @ Vector((R0 + 0.016, s * 0.016, zneck - 0.038))], 0.0013, seg=4, col=(0.46, 0.34, 0.19))


def build():
    counter()
    counter_props()
