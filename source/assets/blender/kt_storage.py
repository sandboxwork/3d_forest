"""Hutch (glazed dresser) with crockery, pantry cupboard, open wall shelves, water barrel, apple crate, sacks, baskets, buckets."""
from kt_lib import *
from kt_ware import *
from kt_food import *
from kt_pots import *
from kt_dining import plank_bm
from kt_counter import (paint, framed_door, drawer_front, knob, bm_merge, _poly_ext, jar_at, tin_can, lid_screw, label_on, PAINT)


def corbel(f, x, y, z, depth=0.16, h=0.14, col=(1, 0.95, 0.9), mat='wood_dark', side=1):
    """scroll-shaped bracket carved from a 22 mm board (sweep of a volute outline)"""
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        # outer curve from wall-top to shelf-front with a volute at the end
        pts.append((t * depth, -h * (1 - t) ** 1.6 * 0.0 - h * (1 - t * t)))
    prof = [(-0.011, -0.011), (0.011, -0.011), (0.011, 0.011), (-0.011, 0.011)]
    path = [f.p((x, y + t_ * 0, z)) for t_, _ in pts] if False else None
    # triangle body
    bm = bmesh.new()
    P = [(0, 0), (depth, 0), (depth, -0.012)]
    curve = [(depth, -0.012), (depth * 0.7, -h * 0.35), (depth * 0.35, -h * 0.75), (0.0, -h)]
    # outline: top edge along shelf, down the cove back to the wall
    outline = [(0, 0), (depth, 0), (depth, -0.016)]
    for i in range(1, 9):
        t = i / 8
        outline.append((depth * (1 - t) ** 0.8 * 0.92 + depth * 0.0, -0.016 - (h - 0.016) * (t ** 0.9)))
    outline = [(round(a, 5), round(b, 5)) for a, b in outline]
    face = bm.faces.new([bm.verts.new((a, 0, b)) for a, b in outline])
    r = bmesh.ops.extrude_face_region(bm, geom=[face])
    for v in [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]:
        v.co.y += 0.022
    for v in bm.verts:
        v.co.y -= 0.011
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm = modbm(bm, [('BEVEL', {'width': 0.0018, 'segments': 1, 'limit_method': 'ANGLE', 'angle_limit': math.radians(40)})])
    put(mat, bm, f.M @ Matrix.Translation((x, y, z)) @ Matrix.Rotation(0 if side > 0 else 0, 4, 'Z'), col=col, g=0)
    bm.free()
    # scroll volute at the bottom tip
    pts = []
    for i in range(20):
        t = i / 19
        a = TAU * 1.25 * t
        rad = 0.016 * (1 - 0.8 * t)
        pts.append(Vector((x + 0.0, y + 0.0, z)) + Vector((0, 0, 0)))
    sp = []
    for i in range(20):
        t = i / 19
        a = TAU * 1.3 * t + math.pi / 2
        rad = 0.02 * (1 - 0.85 * t)
        sp.append(f.p((x, y + rad * math.cos(a) * 0 + 0.0, z)) if False else f.M @ Vector((x, y, z)) + Vector((0, 0, 0)))
    # (volute omitted from the outline for tri economy)


def shelf_unit(cx, cy, z, W=0.56, D=0.2, rot=0, items=1, seed=0, mat='wood_oak', plate_rail=True):
    """wall shelf (board + front rail + corbels), returns frame at shelf top"""
    f = Fr((cx, cy, F), rot)
    zs = z - F
    bm = plank_bm(W, D, 0.024, bev=0.003, seg=2, maxlen=0.12, dent=0.0004, dscale=0.2, seed=seed)
    put(mat, bm, f.M @ Matrix.Translation((0, -D / 2 + 0.0, zs)), col=(0.9, 0.82, 0.72), g=0, skip_down=False)
    bm.free()
    if plate_rail:
        f.box(mat, (0, -D + 0.03, zs + 0.03), (W - 0.02, 0.012, 0.012), bev=0.003, seg=2, col=(0.8, 0.7, 0.6), g=0)
    # back plate-rail groove strip (a wooden fillet 3 cm above the board)
    f.box(mat, (0, -D + 0.002, zs + 0.012), (W - 0.0, 0.012, 0.024), bev=0.002, seg=2, col=(0.85, 0.78, 0.68), g=0)
    f.box(mat, (0, -0.0, zs + 0.0), (W + 0.02, 0.02, 0.022), bev=0.004, seg=2, col=(0.85, 0.76, 0.65), g=0)
    for s in (-1, 1):
        # simple turned-bracket: triangular braces
        fx = s * (W / 2 - 0.05)
        f.box(mat, (fx, -D / 2 + 0.0, zs - 0.045), (0.022, D - 0.03, 0.022), bev=0.003, seg=2, col=(0.7, 0.6, 0.5), g=1, r=(0, 0, 0), skip_down=False)
        f.box(mat, (fx, -D + 0.014, zs - 0.07), (0.022, 0.022, 0.1), bev=0.003, seg=2, col=(0.7, 0.6, 0.5), g=2, skip_down=False)
        f.box(mat, (fx, -D / 2 - 0.03, zs - 0.095), (0.02, 0.22, 0.02), bev=0.003, seg=2, col=(0.7, 0.6, 0.5), g=1, r=(-0.0, 0, 0), skip_down=False) if False else None
        # diagonal strut
        pts = [f.p((fx, -D + 0.03, zs - 0.11)), f.p((fx, -D * 0.4, zs - 0.012))]
        tube(mat, pts, 0.011, seg=6, col=(0.7, 0.6, 0.5))
        for zz in (zs - 0.11,):
            dome('iron_black', f.p((fx + 0.011, -D + 0.014, zz)), f.M.to_3x3() @ Vector((1, 0, 0)), r=0.004)
    return Fr(f.p((0, 0, zs + 0.012)), rot)


def plates_standing(f, x0, x1, z, y, n, r=0.1, tilt=12, rims=None, seg=14, lod=2, face=0):
    for i in range(n):
        x = x0 + (x1 - x0) * i / max(n - 1, 1)
        P = f.p((x, y, 0)); P.z = F + z + r * math.cos(math.radians(tilt)) + 0.004
        rim = (rims or ['blue', 'cobalt', 'green', 'red'])[i % 4 if not rims else i % len(rims)]
        # plate with axis horizontal toward the wall (local +y), tilted back
        plate(P, r=r, glaze='cream', rim=rim, rot=(-90 + tilt, 0, f.rot + face), seg=seg, lod=lod)


def hutch(pos=(-0.4, WY - 0.21), rot=180):
    f = Fr((pos[0], pos[1], F), rot)
    W, D, H = 1.0, 0.42, 2.08
    t = 0.022
    tint = paint('blue')
    mat = 'wood_pine'
    zb_top = 0.9
    # ----- lower cabinet
    bay = (W - 0.04) / 2
    f.box(mat, (0, -0.02, 0.05), (W - 0.02, D - 0.1, 0.1), bev=0.002, col=shade(tint, 0.55), skip_down=True)
    for s in (-1, 1):
        f.box(mat, (s * (W / 2 - t / 2), 0, 0.1 + (zb_top - 0.1) / 2), (t, D, zb_top - 0.1), bev=0.003, seg=2, col=shade(tint, 0.95), g=2, skip_down=False)
    f.box(mat, (0, -D / 2 + 0.01, 0.1 + (zb_top - 0.1) / 2), (W - 2 * t, 0.014, zb_top - 0.1), bev=0, col=shade(tint, 0.8), skip_down=False)
    f.box(mat, (0, 0, 0.14), (W - 2 * t, D - 0.04, 0.02), bev=0.002, col=shade(tint, 0.75), g=0, skip_down=False)
    yf = D / 2 - 0.013
    f.box(mat, (0, yf - 0.011, 0.125), (W - 0.004, t, 0.05), bev=0.003, seg=2, col=tint, g=0, skip_down=False)
    f.box(mat, (0, yf - 0.011, zb_top - 0.025), (W - 0.004, t, 0.05), bev=0.003, seg=2, col=tint, g=0, skip_down=False)
    for i in range(3):
        x = -W / 2 + 0.02 + i * bay
        f.box(mat, (x, yf - 0.011, 0.1 + (zb_top - 0.1) / 2), (0.04, t, zb_top - 0.1), bev=0.003, seg=2, col=tint, g=2, skip_down=False)
    # drawers over doors
    for i in range(2):
        cx = -W / 2 + 0.02 + bay * (i + 0.5)
        drawer_front(f, cx, zb_top - 0.1 - 0.055, bay - 0.01, 0.12, yf, paint('blue', 1.05))
        framed_door(f, cx, 0.15 + (zb_top - 0.15 - 0.24 - 0.0) / 2 - 0.0, bay - 0.008, zb_top - 0.15 - 0.2 - 0.07 + 0.0 + 0.0, yf, paint('blue', 0.97 + 0.05 * i), hinge=-1 if i == 0 else 1, knob_side=1 if i == 0 else -1)
    # oak worktop
    wt = plank_bm(W + 0.05, D + 0.05, 0.04, bev=0.004, seg=2, maxlen=0.12, dent=0.0006, dscale=0.15, seed=11)
    put('wood_oak', wt, f.M @ Matrix.Translation((0, 0.012, zb_top + 0.02)), col=(1, 0.94, 0.86), g=0)
    wt.free()
    ztop = zb_top + 0.04
    # ----- middle open zone: turned front posts + beadboard back + plate rail
    post_x = W / 2 - 0.035
    for s in (-1, 1):
        f.lathe('wood_pine', (s * post_x, D / 2 - 0.04, ztop), [(0.02, 0), (0.026, 0.012), (0.019, 0.03), (0.017, 0.12), (0.022, 0.16), (0.017, 0.2), (0.0165, 0.4), (0.022, 0.43), (0.019, 0.46)], seg=12, col=tint)
        f.box(mat, (s * (W / 2 - 0.011), -0.02, ztop + 0.25), (0.022, D - 0.1, 0.5), bev=0.003, col=shade(tint, 0.9), skip_down=False)   # side panel
    z_up0 = 1.45         # upper cabinet bottom
    f.box(mat, (0, -D / 2 + 0.012, ztop + (z_up0 - ztop) / 2), (W - 0.04, 0.016, z_up0 - ztop), bev=0.002, col=shade(tint, 0.82), skip_down=False)
    f.box(mat, (0, -D / 2 + 0.03, ztop + 0.28), (W - 0.06, 0.012, 0.016), bev=0.003, seg=2, col=shade(tint, 1.0), skip_down=False)   # plate rail
    f.box(mat, (0, -D / 2 + 0.036, ztop + 0.03), (W - 0.06, 0.014, 0.02), bev=0.003, seg=2, col=shade(tint, 1.0), skip_down=False)   # plate ledge
    # ----- upper cabinet (glazed doors) - depth 0.27
    Du = 0.27
    yb = -D / 2 + Du / 2 + 0.0
    z_up1 = H - 0.1
    hu = z_up1 - z_up0
    for s in (-1, 1):
        f.box(mat, (s * (W / 2 - t / 2 - 0.01), yb, z_up0 + hu / 2), (t, Du, hu), bev=0.003, seg=2, col=shade(tint, 0.95), g=2, skip_down=False)
    f.box(mat, (0, yb, z_up0 + 0.011), (W - 0.04 - 2 * t + 0.02, Du, 0.022), bev=0.002, col=shade(tint, 0.8), g=0, skip_down=False)
    f.box(mat, (0, yb, z_up1 - 0.011), (W - 0.04, Du, 0.022), bev=0.002, col=shade(tint, 0.9), g=0, skip_down=False)
    f.box(mat, (0, -D / 2 + 0.014, z_up0 + hu / 2), (W - 0.06, 0.014, hu), bev=0, col=shade(tint, 0.62), skip_down=False)       # back (darker)
    # interior shelves with plate grooves
    for zz in (z_up0 + hu * 0.37, z_up0 + hu * 0.7):
        f.box(mat, (0, yb, zz), (W - 0.06, Du - 0.02, 0.018), bev=0.002, col=shade(tint, 0.85), g=0, skip_down=False)
        f.box(mat, (0, -D / 2 + 0.07, zz + 0.012), (W - 0.07, 0.01, 0.012), bev=0.002, col=shade(tint, 0.8), skip_down=False)
    # crockery inside (visible through the glazed doors)
    zz1, zz2 = z_up0 + hu * 0.37, z_up0 + hu * 0.7
    plates_standing(f, -0.35, 0.35, zz1 + 0.009, -D / 2 + 0.085, 7, r=0.108, tilt=8, seg=14, lod=2)
    plates_standing(f, -0.36, 0.0, zz2 + 0.009, -D / 2 + 0.085, 4, r=0.095, tilt=8, rims=['cobalt', 'blue'], seg=14, lod=2)
    for k in range(3):   # nested bowls
        P = f.p((0.28, -0.03, 0)); P.z = F + zz2 + 0.009 + 0.0 + k * 0.026
        bowl(P, r=0.075 - 0.003 * k, h=0.05, glaze='cream', rim='blue', seg=16)
    # cups hanging on brass hooks beneath the middle shelf
    for k in range(5):
        x = -0.37 + k * 0.095
        hk = f.p((x, -0.03, zz1 - 0.01)); 
        cyl('brass', hk + Vector((0, 0, 0.0)), 0.0025, 0.012, seg=5)
        mug(Vector((hk.x, hk.y - 0.0, F + zz1 - 0.075)), glaze=['blue', 'cream', 'red', 'cream', 'blue'][k], rim='cream' if k % 2 == 0 else None, r=0.032, h=0.062, rot=(0, 0, f.rot + 90), seg=12)
    # a tureen with lid on the top shelf area
    P = f.p((-0.12, -0.04, 0)); P.z = F + zz2 + 0.009
    lathe('ceramic', P, [(0.001, 0), (0.05, 0.0), (0.075, 0.03), (0.082, 0.07), (0.078, 0.085), (0.072, 0.085), (0.07, 0.07)], 18, col=G('cream'), cap=False)
    lathe('ceramic', P + Vector((0, 0, 0.083)), [(0.08, 0), (0.07, 0.015), (0.045, 0.03), (0.015, 0.045), (0.02, 0.055), (0.001, 0.06)], 18, col=G('cream'), cap=False)
    # small jugs on the lowest part
    jug(Vector((f.p((0.12, -0.04, 0)).x, f.p((0.12, -0.04, 0)).y, F + zz1 + 0.009)), r=0.04, h=0.12, glaze='green', rot=(0, 0, f.rot + 180), seg=14)
    # glazed doors: frame + muntins + glass
    for i in range(2):
        cx = -W / 2 + 0.02 + bay * (i + 0.5)
        glazed_door(f, cx, z_up0 + hu / 2, bay - 0.008, hu - 0.03, -D / 2 + Du + 0.004 - 0.0, paint('blue', 1.0 + 0.04 * i), hinge=-1 if i == 0 else 1)
    # cornice crown moulding + dentil row
    zc = H - 0.1
    f.box(mat, (0, yb + 0.02, zc + 0.014), (W + 0.04, Du + 0.06, 0.028), bev=0.004, seg=2, col=shade(tint, 1.05), g=0, skip_down=False)
    f.box(mat, (0, yb + 0.03, zc + 0.04), (W + 0.07, Du + 0.09, 0.024), bev=0.004, seg=2, col=shade(tint, 1.08), g=0, skip_down=False)
    for k in range(int((W) / 0.035)):
        x = -W / 2 + 0.02 + k * 0.035
        f.box(mat, (x, yb + Du / 2 + 0.03, zc - 0.006), (0.018, 0.012, 0.018), bev=0.002, col=shade(tint, 0.95), skip_down=False)
    f.box(mat, (0, yb + 0.04, zc + 0.063), (W + 0.04, Du + 0.07, 0.018), bev=0.003, seg=2, col=shade(tint, 1.1), g=0, skip_down=False)
    # contents of the middle zone
    for k in range(4):
        x = -0.34 + k * 0.1
    plates_standing(f, -0.3, 0.3, ztop + 0.0, -D / 2 + 0.065, 5, r=0.11, tilt=11, rims=['blue', 'cobalt', 'green', 'blue', 'red'], seg=22, lod=1)
    # tea tray with cups and teapot on the counter (centre-left front)
    tray(f.p((-0.18, 0.06, 0)) + Vector((0, 0, F + ztop - F - F + 0.0)) if False else Vector((f.p((-0.2, 0.07, 0)).x, f.p((-0.2, 0.07, 0)).y, F + ztop)), rot=f.rot + 0)
    # sugar bowl + lidded butter crock on the right
    P = f.p((0.3, 0.1, 0)); P.z = F + ztop
    lathe('ceramic', P, [(0.001, 0), (0.035, 0.0), (0.05, 0.03), (0.047, 0.065), (0.042, 0.07)], 16, col=G('rose'), cap=False)
    lathe('ceramic', P + Vector((0, 0, 0.066)), [(0.047, 0), (0.035, 0.012), (0.012, 0.022), (0.014, 0.03), (0.001, 0.034)], 16, col=G('rose'), cap=False)
    collider_f(f, W + 0.05, D + 0.05, F + H)
    interact('hutch', (pos[0], pos[1], F + 1.4), '접시가 가득한 찬장')
    return f


def glazed_door(f, cx, cz, w, h, y, tint, hinge=1):
    t = 0.022
    sw = 0.04
    mat = 'wood_pine'
    f.box(mat, (cx - w / 2 + sw / 2, y, cz), (sw, t, h), bev=0.003, seg=2, col=tint, g=2, skip_down=False)
    f.box(mat, (cx + w / 2 - sw / 2, y, cz), (sw, t, h), bev=0.003, seg=2, col=tint, g=2, skip_down=False)
    f.box(mat, (cx, y, cz + h / 2 - sw / 2), (w - 2 * sw + 0.004, t, sw), bev=0.003, seg=2, col=tint, g=0, skip_down=False)
    f.box(mat, (cx, y, cz - h / 2 + sw / 2), (w - 2 * sw + 0.004, t, sw), bev=0.003, seg=2, col=tint, g=0, skip_down=False)
    iw, ih = w - 2 * sw, h - 2 * sw
    f.box('glass', (cx, y - 0.002, cz), (iw + 0.008, 0.003, ih + 0.008), bev=0, skip_down=False)
    # muntins 2 x 3
    f.box(mat, (cx, y + 0.0015, cz), (0.014, 0.012, ih), bev=0.002, seg=2, col=shade(tint, 1.03), g=2, skip_down=False)
    for k in (-1, 1):
        f.box(mat, (cx, y + 0.0015, cz + k * ih / 4.0), (iw, 0.012, 0.014), bev=0.002, seg=2, col=shade(tint, 1.03), g=0, skip_down=False) if False else None
    for k in (-0.5, 0.5):
        f.box(mat, (cx, y + 0.0015, cz + k * ih / 1.5 * 0.0 + (ih / 3.0) * (1 if k > 0 else -1) * 0.5), (iw, 0.012, 0.014), bev=0.002, seg=2, col=shade(tint, 1.03), g=0, skip_down=False)
    # hinges (brass butt hinges) and a small knob
    hx = cx + hinge * (w / 2)
    for zz in (cz + h / 2 - 0.1, cz - h / 2 + 0.1):
        f.cyl('brass', (hx, y + t / 2, zz), 0.0058, 0.045, seg=8)
        f.box('brass', (hx - hinge * 0.012, y + t / 2 + 0.0005, zz), (0.024, 0.003, 0.045), bev=0.001)
        for dz in (-0.014, 0.014):
            dome('brass', f.p((hx - hinge * 0.014, y + t / 2 + 0.002, zz + dz)), f.M.to_3x3() @ Vector((0, 1, 0)), r=0.0025)
    kx = cx - hinge * (w / 2 - 0.02)
    knob(f, Vector((kx, y + t / 2, cz)), brass=True, r=0.011)


def tray(P, rot=0, L=0.34, W=0.22):
    """wooden tea tray with handles, 3 cups on saucers, teapot, spoon"""
    f = Fr((P.x, P.y, P.z), rot)
    # tray: base + rim (bevelled box) + cut handles
    bm = cube_bm(L, W, 0.014, off=(0, 0, 0.007))
    bev_bm(bm, 0.003, 2)
    put('wood_dark', bm, f.M, col=(0.85, 0.7, 0.55), g=0)
    bm.free()
    for (dx, dy, sx, sy) in ((0, W / 2 - 0.006, L, 0.012), (0, -W / 2 + 0.006, L, 0.012), (L / 2 - 0.006, 0, 0.012, W), (-L / 2 + 0.006, 0, 0.012, W)):
        f.box('wood_dark', (dx, dy, 0.025), (sx, sy, 0.024), bev=0.003, seg=2, col=(0.8, 0.65, 0.5), skip_down=False)
    for s in (-1, 1):
        f.torus('iron_black', (s * (L / 2 + 0.005), 0, 0.026), 0.016, 0.0028, plane='xz') if False else None
        f.box('brass', (s * (L / 2 + 0.003), 0, 0.027), (0.008, 0.07, 0.01), bev=0.002)
    zt = 0.014
    for k in range(3):
        cup_saucer(f.p((-0.07 + 0.08 * k, 0.05 if k % 2 == 0 else -0.045, zt)), glaze='cream', rim='blue', rot=(0, 0, f.rot + 30 * k), fill=(0.3, 0.15, 0.05) if k == 0 else None, seg=14)
    teapot(f.p((0.1, -0.03, zt)), rot=(0, 0, f.rot + 190), glaze='white', r=0.058, seg=16)
    spoon(f.p((-0.12, -0.075, zt)), rot=f.rot + 80, L=0.12)


def hutch_props():
    pass


# ====================================================================== pantry
def pantry(pos=(0.5, WY - 0.25), rot=180):
    f = Fr((pos[0], pos[1], F), rot)
    W, D, H = 0.66, 0.5, 2.15
    t = 0.022
    mat = 'wood_pine'
    tint = paint('red', 1.0)
    f.box(mat, (0, -0.02, 0.05), (W - 0.02, D - 0.1, 0.1), bev=0.002, col=shade(tint, 0.5), skip_down=True)
    for s in (-1, 1):
        f.box(mat, (s * (W / 2 - t / 2), 0, 0.1 + (H - 0.1) / 2), (t, D, H - 0.1), bev=0.003, seg=2, col=shade(tint, 0.95), g=2, skip_down=False)
    f.box(mat, (0, -D / 2 + 0.01, 0.1 + (H - 0.1) / 2), (W - 2 * t, 0.014, H - 0.1), bev=0, col=shade(tint, 0.6), skip_down=False)
    yf = D / 2 - 0.013
    # shelves inside
    zs_list = [0.4, 0.62, 1.2, 1.45, 1.7, 1.93]
    for zz in zs_list:
        f.box(mat, (0, 0.0, zz), (W - 2 * t, D - 0.04, 0.02), bev=0.002, col=shade(tint, 0.78), g=0, skip_down=False)
    # contents of the upper compartment (visible through the ajar door)
    rr = random.Random(21)
    zb = F
    for zz in (1.2, 1.45, 1.7):
        for k in range(2, 4):
            x = -0.2 + k * 0.133
            kind = (k + int(zz * 10)) % 3
            P = f.p((x, 0.08, 0)); P.z = F + zz + 0.01
            if kind == 0:
                jar_at(Vector((P.x, P.y - 0.04, P.z)), ['pickles', 'jam', 'flour', 'jam'][(k + int(zz * 7)) % 4], seed=k + int(zz * 10), tall=(k % 2 == 0))
            elif kind == 1:
                tin_can(Vector((P.x, P.y + 0.03, P.z)), 0.04, 0.1 + 0.02 * (k % 2), cell=[(0, 0), (1, 0), (2, 0), (3, 0), (0, 1), (1, 1)][(k + int(zz * 5)) % 6], rot=rr.uniform(0, 360))
            else:
                # tied linen sack of grain
                place('burlap_vc', sack_bm(0.05, 0.14, seed=k, tied=True, flour=False, res=(12, 7)), Vector((P.x, P.y, P.z)), rot=(0, 0, rr.uniform(0, 360)), col=(0.95, 0.88, 0.72))
    # lower compartment: crocks and a sack
    for k in range(2):
        P = f.p((-0.12 + 0.26 * k, 0.03, 0)); P.z = F + 0.62 + 0.01 if False else F + 0.42
        lathe('ceramic', P, [(0.001, 0), (0.07, 0), (0.08, 0.05), (0.085, 0.12), (0.075, 0.14), (0.082, 0.15), (0.07, 0.15), (0.07, 0.14)], 18, col=G('brown') if k == 0 else G('ochre'), cap=False)
    # doors
    dw = (W - 0.04) / 2
    zl0, zl1 = 0.1, 0.88
    zu0, zu1 = 1.06, 2.07
    f.box(mat, (0, yf - 0.011, 0.1 + 0.0), (W - 0.004, t, 0.03), bev=0.003, seg=2, col=tint, g=0, skip_down=False)
    for x in (-W / 2 + 0.02, 0.0, W / 2 - 0.02):
        f.box(mat, (x, yf - 0.011, 0.1 + (H - 0.1) / 2), (0.04, t, H - 0.1), bev=0.003, seg=2, col=tint, g=2, skip_down=False)
    for (zz0, zz1) in ((0.88, 1.06), (2.07, 2.13)):
        f.box(mat, (0, yf - 0.011, (zz0 + zz1) / 2), (W - 0.004, t, zz1 - zz0), bev=0.003, seg=2, col=tint, g=0, skip_down=False)
    # lower doors
    for i in range(2):
        cx = -W / 2 + 0.02 + dw * (i + 0.5)
        framed_door(f, cx, (zl0 + zl1) / 2 + 0.01, dw - 0.008, zl1 - zl0 - 0.04, yf, paint('red', 0.95 + 0.06 * i), hinge=-1 if i == 0 else 1, knob_side=1 if i == 0 else -1)
    # drawers between
    for i in range(2):
        cx = -W / 2 + 0.02 + dw * (i + 0.5)
        drawer_front(f, cx, 0.97, dw - 0.008, 0.15, yf, paint('red', 1.05))
    # upper doors: left closed, right slightly open
    cx = -W / 2 + 0.02 + dw * 0.5
    framed_door(f, cx, (zu0 + zu1) / 2, dw - 0.008, zu1 - zu0 - 0.04, yf, paint('red', 1.0), hinge=-1, knob_side=1)
    cx = -W / 2 + 0.02 + dw * 1.5
    hxx = cx + (dw - 0.008) / 2
    g = Fr(f.pos, f.rot)
    ang = 28.0
    g.M = f.M @ Matrix.Translation((hxx, yf, 0)) @ Matrix.Rotation(math.radians(ang), 4, 'Z') @ Matrix.Translation((-hxx, -yf, 0))
    framed_door(g, cx, (zu0 + zu1) / 2, dw - 0.008, zu1 - zu0 - 0.04, yf, paint('red', 1.03), hinge=1, knob_side=-1)
    # cornice
    f.box(mat, (0, 0.0, H + 0.014), (W + 0.04, D + 0.04, 0.028), bev=0.004, seg=2, col=shade(tint, 1.05), g=0, skip_down=False)
    f.box(mat, (0, 0.01, H + 0.04), (W + 0.07, D + 0.06, 0.024), bev=0.004, seg=2, col=shade(tint, 1.08), g=0, skip_down=False)
    f.box(mat, (0, yf + 0.02, H - 0.025), (W - 0.02, 0.012, 0.025), bev=0.003, seg=2, col=shade(tint, 1.0), skip_down=False)
    # shopping list pinned to the left upper door (paper + ink lines + brass tack)
    pn = cube_bm(0.075, 0.0012, 0.1, off=(0, 0, 0))
    inv_n = None

    def note_cf(p):
        l = (f.M.inverted() @ p) - Vector((-W / 4 - 0.02, yf + 0.015, 1.55))
        c = (0.93, 0.88, 0.76)
        if abs(l.x) < 0.028 and l.z < 0.036 and int((l.z + 0.05) * 140) % 3 == 0:
            c = (0.2, 0.17, 0.14)
        return c
    put('paper', pn, f.M @ Matrix.Translation((-W / 4 - 0.02, yf + 0.0155, 1.55)) @ Matrix.Rotation(math.radians(5), 4, 'Y'), cfn=note_cf, g=0)
    pn.free()
    dome('brass', f.p((-W / 4 - 0.02, yf + 0.0165, 1.585)), f.M.to_3x3() @ Vector((0, 1, 0)), r=0.004)
    # iron latch (thumb latch) on the left upper door
    lx_ = -W / 2 + 0.02 + dw - 0.04
    f.box('iron_black', (lx_, yf + 0.016, (zu0 + zu1) / 2), (0.014, 0.006, 0.07), bev=0.002)
    f.box('iron_black', (lx_ + 0.012, yf + 0.024, (zu0 + zu1) / 2 + 0.03), (0.04, 0.005, 0.012), bev=0.002, r=(0, 0, 10))
    collider_f(f, W + 0.07, D + 0.16, F + H + 0.05, off=(0, 0.05))
    # items on top: baskets and a jar of preserves
    P = f.p((0.0, 0.0, 0)); P.z = F + H + 0.052
    wicker_basket(P + Vector((-0.12, 0.0, 0)), 0.14, 0.12, seed=7, handle=True, rot=f.rot)
    P2 = P + Vector((0.14, 0.0, 0))
    tin_can(P2 + Vector((0, 0.0, 0)), 0.05, 0.14, (1, 0), rot=30)
    interact('pantry', (pos[0], pos[1], F + 1.2), '식료품 저장장')
    return f


# ====================================================================== sacks
def sack_bm(R=0.18, H=0.6, seed=0, tied=True, flour=True, open_top=False, uv_m=True, res=(24, 14)):
    """sack: grid over (theta, z) with belly profile, sagging base, fold pleats + pinched, tied neck, then Displace for wrinkles"""
    rr = random.Random(seed)
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    nth, nz_ = res
    rings = []
    ph = rr.uniform(0, TAU)
    for j in range(nz_ + 1):
        t = j / nz_
        z = t * H
        # belly profile: wide near lower third, base flare, pinched at neck 0.78..
        if tied:
            prof = 0.55 + 0.45 * math.sin(math.pi * min(1.0, t / 0.82) ** 0.85) if t < 0.82 else 0.28 * max(0.0, 1 - (t - 0.82) / 0.18) ** 0.6 + 0.07
            if t < 0.06:
                prof = max(prof, 0.78 * (0.55 + t / 0.06 * 0.45))
        else:
            prof = 0.6 + 0.4 * math.sin(math.pi * min(1.0, t / 0.9) ** 0.8) if t < 0.9 else 0.78
        ring = []
        if t > 0.8 and tied:
            tt = (t - 0.8) / 0.2
            pl = 0.032 * tt ** 0.8
        else:
            pl = 0.0
        for i in range(nth):
            a = TAU * i / nth
            pleat = 1 + (pl / R) * math.cos(9 * a + ph) if pl else 1.0
            fold = 1 + 0.045 * math.sin(3 * a + t * 7 + ph) + 0.03 * math.sin(5 * a - t * 5)
            r = R * prof * pleat * fold
            if t < 0.04:
                r *= 0.7 + 0.3 * (t / 0.04)
            x, y = r * math.cos(a), r * math.sin(a)
            zz = z - 0.0
            if t < 0.2:   # base squash flattens the lower body toward the bottom
                zz = z * 0.97
            ring.append(bm.verts.new((x, y, zz)))
        rings.append(ring)
    for j in range(nz_):
        for i in range(nth):
            i2 = (i + 1) % nth
            f = bm.faces.new([rings[j][i], rings[j][i2], rings[j + 1][i2], rings[j + 1][i]])
            for l in f.loops:
                a = math.atan2(l.vert.co.y, l.vert.co.x)
                l[ul].uv = (a * R * 1.0, l.vert.co.z)
    # top: tied: flared ears above the tie point; else open rim
    if tied:
        top = rings[-1]
        tip = bm.verts.new((0, 0, H + 0.03))
        for i in range(nth):
            i2 = (i + 1) % nth
            f = bm.faces.new([top[i], top[i2], tip]) if False else None
        # gathered neck: small pleated tail above the tie
        frill = []
        for i in range(nth):
            a = TAU * i / nth
            r = R * 0.17 * (1 + 0.35 * math.cos(9 * a + ph))
            frill.append(bm.verts.new((r * math.cos(a), r * math.sin(a), H + 0.022 + 0.008 * math.cos(9 * a + ph))))
        for i in range(nth):
            i2 = (i + 1) % nth
            bm.faces.new([top[i], top[i2], frill[i2], frill[i]])
        cap_ = [bm.verts.new((frill[i].co.x * 0.55, frill[i].co.y * 0.55, H + 0.04)) for i in range(nth)]
        for i in range(nth):
            i2 = (i + 1) % nth
            bm.faces.new([frill[i], frill[i2], cap_[i2], cap_[i]])
        bm.faces.new(cap_[::-1])
    else:
        top = rings[-1]
        bm.faces.new(top[::-1])
    # base
    bm.faces.new(rings[0][::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm = disp(bm, 0.004, 0.045, 3, seed_loc=(seed * 5.1, seed * 2.3, 0.7))
    return bm


def sack(pos, R=0.19, H=0.62, rot=0, seed=0, col=(0.9, 0.82, 0.66), tied=True, flour=False, label_cell=None, lean=(0, 0)):
    bm = sack_bm(R, H, seed, tied, flour)
    bm = lattice_bm(bm, res=(2, 2, 4), fn=lambda i, j, k, p: Vector((lean[0] * (k / 3.0) ** 2 * 0.1, lean[1] * (k / 3.0) ** 2 * 0.1, 0)))
    Mx = xf(pos, (0, 0, rot))
    put('burlap_vc', bm, Mx, cfn=fab(col, 0.1, 10, seed), g=0)
    bm.free()
    if tied:
        zt = H * 0.83
        zl = H * 0.83
        for k in range(3):
            torus('rope', None, R * 0.2 + 0.006, 0.0042, plane='xy', M=Mx @ Matrix.Translation((0, 0, zl + 0.012 * k)), seg=14, rseg=5, col=(0.42, 0.3, 0.17))
        for s_ in (-1, 1):
            tube('rope', [Mx @ Vector((R * 0.22, 0, zl + 0.012)), Mx @ Vector((R * 0.3, s_ * 0.025, zl - 0.03)), Mx @ Vector((R * 0.36, s_ * 0.045, zl - 0.09))], 0.0042, seg=5, col=(0.42, 0.3, 0.17))
        sphere('rope', Mx @ Vector((R * 0.22, 0, zl + 0.012)), 0.01, seg=6, rings=4, col=(0.42, 0.3, 0.17))
    if label_cell is not None:
        # printed stamp patch following the surface (front, facing local -y)
        cu, cv = label_cell
        pb = bmesh.new()
        ul = pb.loops.layers.uv.new('UVMap')
        nx, ny = 6, 6
        VV = [[None] * (ny + 1) for _ in range(nx + 1)]
        for i in range(nx + 1):
            for j in range(ny + 1):
                ang = -math.pi / 2 + (i / nx - 0.5) * 1.0
                t = 0.3 + 0.35 * j / ny
                rad = R * (0.55 + 0.45 * math.sin(math.pi * min(1.0, t / 0.82) ** 0.85)) + 0.0015
                VV[i][j] = pb.verts.new((rad * math.cos(ang), rad * math.sin(ang), t * H))
        for i in range(nx):
            for j in range(ny):
                fc = pb.faces.new([VV[i][j], VV[i + 1][j], VV[i + 1][j + 1], VV[i][j + 1]])
                for l, (u, v) in zip(fc.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
                    pass
                for l, (ii, jj) in zip(fc.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
                    l[ul].uv = (cu * 0.25 + 0.003 + (ii / nx) * 0.244, cv * 0.25 + 0.003 + (jj / ny) * 0.244)
        bmesh.ops.recalc_face_normals(pb, faces=pb.faces[:])
        put('label', pb, Mx, uvs=1.0)
        pb.free()


# ====================================================================== baskets
def wicker_basket(P, r=0.2, h=0.22, seed=0, handle=True, rot=0, fill=None, base_r=None):
    Mx = xf(P, (0, 0, rot))
    rr = random.Random(seed)
    nst = 12
    rows = 7
    br = base_r or r * 0.8
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    rings = []
    for j in range(rows + 1):
        t = j / rows
        z = t * h
        rad = br + (r - br) * (t ** 0.85) * (1 + 0.1 * math.sin(t * math.pi))
        ring = []
        for i in range(nst * 2):
            a = TAU * i / (nst * 2)
            weave = 0.0045 * (1 if ((i // 1 + j) % 2 == 0) else -1) * (1 if i % 2 == 0 else 1) * 0.5
            wv = 0.0035 * math.cos(math.pi * i + math.pi * j)
            ring.append(bm.verts.new(((rad + wv) * math.cos(a), (rad + wv) * math.sin(a), z)))
        rings.append(ring)
    for j in range(rows):
        for i in range(nst * 2):
            i2 = (i + 1) % (nst * 2)
            fc = bm.faces.new([rings[j][i], rings[j][i2], rings[j + 1][i2], rings[j + 1][i]])
            for l in fc.loops:
                a = math.atan2(l.vert.co.y, l.vert.co.x)
                l[ul].uv = (a * r, l.vert.co.z)
    # inner wall: slightly smaller offset (so inside is visible)
    rings2 = []
    for j in range(rows + 1):
        t = j / rows
        z = t * h
        rad = (br + (r - br) * (t ** 0.85) * (1 + 0.1 * math.sin(t * math.pi))) - 0.01
        rings2.append([bm.verts.new((rad * math.cos(TAU * i / (nst * 2)), rad * math.sin(TAU * i / (nst * 2)), z)) for i in range(nst * 2)])
    for j in range(rows):
        for i in range(nst * 2):
            i2 = (i + 1) % (nst * 2)
            fc = bm.faces.new([rings2[j][i], rings2[j + 1][i], rings2[j + 1][i2], rings2[j][i2]])
            for l in fc.loops:
                a = math.atan2(l.vert.co.y, l.vert.co.x)
                l[ul].uv = (a * r, l.vert.co.z)
    # rim connection and base
    for i in range(nst * 2):
        i2 = (i + 1) % (nst * 2)
        bm.faces.new([rings[-1][i], rings[-1][i2], rings2[-1][i2], rings2[-1][i]])
    bm.faces.new(rings[0][::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    put('wicker', bm, Mx, col=jit((0.95, 0.85, 0.7), 0.06), g=2, skip_down=True)
    bm.free()
    # plaited rim: twisted cord (two strands)
    for s in (0, 1):
        pts = []
        for i in range(36):
            a = TAU * i / 36
            tw = 0.0045 * math.sin(a * 18 + s * math.pi)
            pts.append(Vector(((r + 0.002) * math.cos(a), (r + 0.002) * math.sin(a), h + tw)))
        sweep('wicker', [(0.0055 * math.cos(TAU * k / 4), 0.0055 * math.sin(TAU * k / 4)) for k in range(4)], pts, M=Mx, closed_path=True, col=(0.9, 0.78, 0.6), g=0)
    # braided base ring
    torus('wicker', None, br, 0.006, plane='xy', M=Mx @ Matrix.Translation((0, 0, 0.004)), seg=20, rseg=4, col=(0.85, 0.72, 0.55))
    if handle:
        # plaited handle: two intertwined strands arching over
        for s in (0, 1):
            pts = []
            for i in range(14):
                a = math.pi * i / 13
                tw = 0.006 * math.sin(a * 10 + s * math.pi)
                pts.append(Vector((tw, -(r + 0.0) * math.cos(a), h * 0.95 + math.sin(a) * h * 1.2)))
            sweep('wicker', [(0.006 * math.cos(TAU * k / 4), 0.006 * math.sin(TAU * k / 4)) for k in range(4)], pts, M=Mx, col=(0.9, 0.78, 0.6), g=0)
    if fill:
        fill(Mx, r, h)
    return Mx


def basket_with(P, r, h, seed, items='potato', rot=0):
    wicker_basket(P, r, h, seed=seed, rot=rot, handle=(items != 'none'))
    Mx = xf(P, (0, 0, rot))
    surf = bmesh.new()
    bmesh.ops.create_circle(surf, cap_ends=True, cap_tris=True, segments=14, radius=r * 0.82)
    vars_ = []
    if items == 'potato':
        for j in range(4):
            vars_.append({'parts': [(potato_bm(seed * 10 + j, r=0.032 + 0.004 * (j % 2)), 'food_vc')]})
    elif items == 'onion':
        for j in range(3):
            vars_.append({'parts': [(onion_bm(seed + j, r=0.032), 'food_vc')]})
    elif items == 'egg':
        for j in range(3):
            vars_.append({'parts': [(egg_bm(0.022, col=[(0.78, 0.66, 0.5), (0.45, 0.25, 0.12), (0.8, 0.76, 0.68)][j], seed=j), 'food_vc')]})
    for layer, zl in enumerate((h * 0.55, h * 0.7)):
        if layer == 1:
            surf2 = bmesh.new()
            bmesh.ops.create_circle(surf2, cap_ends=True, cap_tris=True, segments=12, radius=r * 0.6)
        else:
            surf2 = surf
        outs = gn_scatter(surf2, vars_, distance=0.065 if items != 'egg' else 0.048, density=4000, seed=seed * 11 + layer, scale=(0.9, 1.1), tilt=0.5, tint=0.1,
                          surf_M=Mx @ Matrix.Translation((0, 0, zl)))
        put_outs(outs, Matrix.Identity(4))
        if layer == 1:
            surf2.free()
    for v in vars_:
        for (bb, mn) in v['parts']:
            bb.free()
    surf.free()


# ====================================================================== barrel / bucket / crate
def barrel(pos=(-1.2, 2.93), r=0.27, h=0.8, tap=True, seed=0):
    P = Vector((pos[0], pos[1], F))
    Mx = xf(P)
    rr = random.Random(5)
    N = 20
    nlev = 8

    def R(z):
        t = z / h
        return r * (0.86 + 0.14 * math.sin(math.pi * t) ** 0.9) * (1.0 - 0.0)
    # single stave: facets at 3 angles x levels, inner offset.  Array(radial) with empty offset
    st = bmesh.new()
    ul = st.loops.layers.uv.new('UVMap')
    th = TAU / N
    outer, inner = [], []
    thick = 0.022
    for j in range(nlev + 1):
        z = h * j / nlev
        rad = R(z)
        w_o = rad * 2 * math.tan(th / 2)
        o = [st.verts.new((rad * math.cos(a), rad * math.sin(a), z)) for a in (-th / 2 * 0.985, 0.0 - 0.0, th / 2 * 0.985)]
        # bulge middle slightly out for a rounded stave
        o[1].co = Vector((rad * 1.0035 * 1.0, 0, z))
        outer.append(o)
        ri = rad - thick
        inner.append([st.verts.new((ri * math.cos(a), ri * math.sin(a), z)) for a in (-th / 2 * 0.985, th / 2 * 0.985)])
    for j in range(nlev):
        for k in range(2):
            f1 = st.faces.new([outer[j][k], outer[j][k + 1], outer[j + 1][k + 1], outer[j + 1][k]])
            for l in f1.loops:
                l[ul].uv = (l.vert.co.z, math.atan2(l.vert.co.y, l.vert.co.x) * r)
        f2 = st.faces.new([inner[j][0], inner[j + 1][0], inner[j + 1][1], inner[j][1]])
        for l in f2.loops:
            l[ul].uv = (l.vert.co.z, math.atan2(l.vert.co.y, l.vert.co.x) * r)
        # side edges
        st.faces.new([outer[j][0], outer[j + 1][0], inner[j + 1][0], inner[j][0]])
        st.faces.new([outer[j][2], inner[j][1], inner[j + 1][1], outer[j + 1][2]])
    # top & bottom end faces
    st.faces.new([outer[-1][0], inner[-1][0], inner[-1][1], outer[-1][2], outer[-1][1]])
    st.faces.new([outer[0][0], outer[0][1], outer[0][2], inner[0][1], inner[0][0]])
    bmesh.ops.recalc_face_normals(st, faces=st.faces[:])
    ring = array_radial(st, N)
    for v in ring.verts:   # per-stave irregular dark/light via colour only
        pass
    inv = Mx.inverted()

    def cf(p):
        l = inv @ p
        a = math.atan2(l.y, l.x)
        i = int((a + math.pi) / (TAU / N))
        k = 0.82 + 0.3 * mnoise.noise(Vector((i * 3.7, 1.1, 0.3)))
        wet = 1.0
        # water stains running down from the tap and bottom damp
        if l.z < 0.1:
            wet *= 0.7 + 0.3 * l.z / 0.1
        if abs(a - (-math.pi / 2)) < 0.25 and l.z < 0.3 and tap:
            wet *= 0.6 + 0.4 * (l.z / 0.3)
        g = 1 + 0.12 * fbm(l.x * 8, l.y * 8, l.z * 8, 1, 3, 2)
        return (k * wet * g, k * wet * g * 0.97, k * wet * g * 0.92)
    put('wood_oak', ring, Mx, cfn=cf, g=0, flat=False)
    ring.free()
    # iron hoops (flat bands) with riveted lap joint, 4 of them + 2 thin wooden
    for z, wd in ((0.06, 0.03), (0.2, 0.032), (0.6, 0.032), (0.74, 0.03)):
        rad = R(z) + 0.0045
        pts = [Vector((rad * math.cos(TAU * i / 40), rad * math.sin(TAU * i / 40), z)) for i in range(40)]
        sweep('iron_black', [(-wd / 2, -0.0035), (wd / 2, -0.0035), (wd / 2, 0.0035), (-wd / 2, 0.0035)], pts, M=Mx, closed_path=True, up=(0, 0, 1), g=0)
        for k in range(4):
            a = TAU * (k * 0.25 + 0.08)
            dome('iron_black', Mx @ Vector(((rad + 0.004) * math.cos(a), (rad + 0.004) * math.sin(a), z)), Mx.to_3x3() @ Vector((math.cos(a), math.sin(a), 0)), r=0.0045)
        a = TAU * 0.62
        dome('iron_black', Mx @ Vector(((rad + 0.004) * math.cos(a), (rad + 0.004) * math.sin(a), z + wd * 0.25)), Mx.to_3x3() @ Vector((math.cos(a), math.sin(a), 0)), r=0.0045)
    # lid: two planks with a gap + cleats + ladle on it
    lid_z = h
    for s, (x0, x1) in enumerate(((-r + 0.02, -0.004), (0.004, r - 0.02))):
        bm = plank_bm(x1 - x0, 2 * r - 0.03, 0.02, bev=0.003, seg=2, maxlen=0.09, dent=0.0004, dscale=0.2, seed=s + 3)
        # trim to a circle: clamp vertices
        for v in bm.verts:
            xx, yy = (x0 + x1) / 2 + v.co.x, v.co.y
            d = math.hypot(xx, yy)
            lim = r - 0.012
            if d > lim:
                k = lim / d
                v.co.x = (xx * k) - (x0 + x1) / 2
                v.co.y = yy * k
        put('wood_pine', bm, Mx @ Matrix.Translation(((x0 + x1) / 2, 0, lid_z + 0.012)), col=(0.9, 0.8, 0.7), g=1, skip_down=False)
        bm.free()
    for yy in (-0.14, 0.14):
        box('wood_pine', None, (0.3, 0.035, 0.016), M=Mx @ Matrix.Translation((0, yy, lid_z + 0.03)), bev=0.003, seg=2, col=(0.85, 0.75, 0.65))
    # tap (brass spigot) low on the front (-y), dripping + wet stain
    tz = 0.2
    ty = -(R(tz) - 0.0)
    lathe('brass', None, [(0.02, 0.0), (0.02, 0.005), (0.012, 0.012), (0.011, 0.04)], 10, M=Mx @ Matrix.Translation((0, ty - 0.0, tz)) @ Matrix.Rotation(math.radians(90), 4, 'X') @ Matrix.Rotation(math.pi, 4, 'X') @ Matrix.Rotation(math.pi, 4, 'X'), cap=False) if False else None
    TapM = Mx @ Matrix.Translation((0, ty, tz)) @ Matrix.Rotation(math.radians(90), 4, 'X') @ Matrix.Rotation(math.pi, 4, 'X')
    # pointing -y (outwards)
    lathe('brass', None, [(0.024, 0.0), (0.026, 0.004), (0.02, 0.008), (0.013, 0.014), (0.0125, 0.06), (0.016, 0.07), (0.014, 0.085), (0.011, 0.088)], 12, M=Mx @ Matrix.Translation((0, ty + 0.003, tz)) @ Matrix.Rotation(math.radians(90), 4, 'X'), cap=False)
    cyl('brass', Mx @ Vector((0, ty - 0.06, tz + 0.03)), 0.0085, 0.05, seg=8)
    box('brass', None, (0.07, 0.01, 0.012), M=Mx @ Matrix.Translation((0, ty - 0.06, tz + 0.056)), bev=0.003, seg=2)
    sphere('water', Mx @ Vector((0, ty - 0.086, tz - 0.02)), 0.0045, seg=8, rings=5, sq=(1, 1, 1.5))
    # wet patch on the floor
    pts = [(0.075 * (0.8 + 0.3 * math.sin(k * 2.3 + 1)) * math.cos(TAU * k / 14), 0.06 * (0.8 + 0.3 * math.sin(k * 3.1)) * math.sin(TAU * k / 14)) for k in range(14)]
    pb = bmesh.new()
    pb.faces.new([pb.verts.new((x, y, 0.0012)) for x, y in pts])
    put('water', pb, Mx @ Matrix.Translation((0.02, ty - 0.1, 0.0)), g=2)
    pb.free()
    # tin dipper cup on the lid edge and a wooden ladle hanging on the rim
    mug_tin(Mx @ Vector((0.12, 0.1, lid_z + 0.032)))
    collider(P.x - r - 0.01, P.x + r + 0.01, P.y - r - 0.02, P.y + r + 0.01, F + h + 0.03)
    interact('barrel', (pos[0], pos[1], F + 0.5), '물통 - 빗물 저장 통')


def mug_tin(P):
    lathe('tin', P, [(0.001, 0), (0.032, 0.0), (0.036, 0.004), (0.039, 0.08), (0.04, 0.085), (0.0375, 0.0855), (0.0365, 0.08), (0.033, 0.006), (0.001, 0.005)], 14, cap=False)
    tube('tin', [P + Vector((0.038, 0, 0.07)), P + Vector((0.065, 0, 0.065)), P + Vector((0.065, 0, 0.025)), P + Vector((0.036, 0, 0.02))], 0.0035, seg=5)


def bucket(pos, r=0.14, h=0.27, water=True, seed=0, rot=0, tilt_handle=70):
    P = Vector((pos[0], pos[1], F))
    Mx = xf(P, (0, 0, rot))
    N = 14
    th = TAU / N
    st = bmesh.new()
    ul = st.loops.layers.uv.new('UVMap')
    rb, rt = r * 0.88, r
    thick = 0.012
    # tapered stave
    def pr(z):
        return rb + (rt - rb) * z / h
    ov = [st.verts.new((pr(z) * math.cos(a), pr(z) * math.sin(a), z)) for z in (0.0, h) for a in (-th / 2 * 0.99, th / 2 * 0.99)]
    iv = [st.verts.new(((pr(z) - thick) * math.cos(a), (pr(z) - thick) * math.sin(a), z)) for z in (0.0, h) for a in (-th / 2 * 0.99, th / 2 * 0.99)]
    # ov: [b-,b+,t-,t+]
    quads = [(ov[0], ov[1], ov[3], ov[2]), (iv[0], iv[2], iv[3], iv[1]), (ov[0], ov[2], iv[2], iv[0]), (ov[1], iv[1], iv[3], ov[3]), (ov[2], ov[3], iv[3], iv[2]), (ov[0], iv[0], iv[1], ov[1])]
    for q in quads:
        fc = st.faces.new(q)
        for l in fc.loops:
            l[ul].uv = (l.vert.co.z, math.atan2(l.vert.co.y, l.vert.co.x) * r)
    bmesh.ops.recalc_face_normals(st, faces=st.faces[:])
    ring = array_radial(st, N)
    put('wood_pine', ring, Mx, col=(0.92, 0.84, 0.72), g=0, cfn=lambda p: tuple(0.9 + 0.2 * mnoise.noise(Vector((int((math.atan2(p.y - P.y, p.x - P.x) + math.pi) / th) * 2.3, 0.4, 0.2))) for _ in range(3)))
    ring.free()
    # bottom disc
    lathe('wood_pine', None, [(0.001, 0.0), (rb - 0.002, 0.0), (rb - 0.002, 0.012), (0.001, 0.012)], 14, M=Mx, cap=False, col=(0.9, 0.8, 0.7))
    for z, wd in ((0.045, 0.02), (h - 0.05, 0.02)):
        rad = pr(z) + 0.0035
        pts = [Vector((rad * math.cos(TAU * i / 28), rad * math.sin(TAU * i / 28), z)) for i in range(28)]
        sweep('iron_black', [(-wd / 2, -0.003), (wd / 2, -0.003), (wd / 2, 0.003), (-wd / 2, 0.003)], pts, M=Mx, closed_path=True, up=(0, 0, 1))
        for k in range(2):
            a = TAU * (0.15 + 0.5 * k)
            dome('iron_black', Mx @ Vector(((rad + 0.003) * math.cos(a), (rad + 0.003) * math.sin(a), z)), Mx.to_3x3() @ Vector((math.cos(a), math.sin(a), 0)), r=0.0035)
    # water surface
    if water:
        lathe('water', None, [(0.001, h * 0.82), (r * 0.99 - thick, h * 0.82), (r * 0.99 - thick, h * 0.815)], 16, M=Mx, cap=False)
        lathe('water', None, [(r * 0.62, h * 0.822), (r * 0.7, h * 0.823), (r * 0.62, h * 0.824)], 16, M=Mx, cap=False)
    # two long ear staves -> wire bail with wooden grip
    for s in (-1, 1):
        box('wood_pine', None, (0.026, 0.012, 0.05), M=Mx @ Matrix.Translation((0, s * (rt - 0.006), h + 0.02)), bev=0.003, seg=2, col=(0.9, 0.8, 0.7))
        cyl('iron_black', Mx @ Vector((0, s * (rt - 0.012), h + 0.03)), 0.0045, 0.03, axis='y', seg=6)
    ang0 = math.radians(tilt_handle)
    pts = []
    for i in range(13):
        a = math.pi * i / 12
        pts.append(Vector((0.0, -(rt - 0.006) * math.cos(a), h + 0.03 + math.sin(a) * 0.16)))
    # handle tilt: rotate about the ear axis (local y)
    Rh = Matrix.Translation((0, 0, h + 0.03)) @ Matrix.Rotation(math.radians(-(90 - tilt_handle)), 4, 'Y') @ Matrix.Translation((0, 0, -(h + 0.03)))
    pts = [Rh @ p for p in pts]
    sweep('iron_black', [(0.0035 * math.cos(TAU * k / 5), 0.0035 * math.sin(TAU * k / 5)) for k in range(5)], pts, M=Mx)
    sweep('wood_dark', [(0.0095 * math.cos(TAU * k / 8), 0.0095 * math.sin(TAU * k / 8)) for k in range(8)], pts[5:8], M=Mx, col=(0.55, 0.4, 0.3))
    collider(P.x - r - 0.01, P.x + r + 0.01, P.y - r - 0.01, P.y + r + 0.01, F + h)
    return P


def crate_apples(pos=(-0.35, 2.45), rot=6, size=(0.5, 0.36, 0.26)):
    f = Fr((pos[0], pos[1], F), rot)
    sx, sy, sz = size
    mat = 'wood_pine'
    rr = random.Random(8)
    # base boards
    nb = 4
    for i in range(nb):
        f.box(mat, (0, -sy / 2 + (i + 0.5) * sy / nb, 0.012), (sx, sy / nb - 0.004, 0.018), bev=0.002, seg=2, col=jit((0.8, 0.7, 0.58), 0.1), g=0, skip_down=False)
    # 4 corner posts
    for ax in (-1, 1):
        for ay in (-1, 1):
            f.box(mat, (ax * (sx / 2 - 0.016), ay * (sy / 2 - 0.016), sz / 2 + 0.01), (0.032, 0.032, sz), bev=0.003, seg=2, col=(0.72, 0.6, 0.48), g=2, skip_down=False)
    # side slats with gaps (3 per side) and nails
    for k in range(3):
        z = 0.05 + k * 0.075
        for ay in (-1, 1):
            f.box(mat, (0, ay * (sy / 2 - 0.004), z), (sx - 0.064 + 0.0, 0.012, 0.062), bev=0.002, seg=2, col=jit((0.85, 0.74, 0.6), 0.08), g=0, skip_down=False)
            for sx_ in (-1, 1):
                dome('iron_black', f.p((sx_ * (sx / 2 - 0.016), ay * (sy / 2 - 0.004 + 0.007), z)), f.M.to_3x3() @ Vector((0, ay, 0)), r=0.0032)
        for ax in (-1, 1):
            f.box(mat, (ax * (sx / 2 - 0.004), 0, z), (0.012, sy - 0.064, 0.062), bev=0.002, seg=2, col=jit((0.85, 0.74, 0.6), 0.08), g=1, skip_down=False)
    # stencil mark on the front slat: burnt 'APPLES' bars
    for k in range(5):
        f.box('ink', (-0.08 + k * 0.04, sy / 2 + 0.0035, 0.125), (0.025, 0.0012, 0.012), bev=0, col=(0.1, 0.07, 0.04), skip_down=False)
    # apples: Geometry-Nodes scatter (Poisson-disk), 3 stacked layers, lower layers with a cheaper apple
    n_total = 0
    for layer, (zl, dist, lod, sd) in enumerate(((0.045, 0.072, 5, 1), (0.085, 0.074, 7, 2), (0.126, 0.074, 12, 3))):
        surf = bmesh.new()
        bmesh.ops.create_grid(surf, x_segments=1, y_segments=1, size=1.0)
        for v in surf.verts:
            v.co.x *= (sx - 0.07 - (0.03 if layer == 2 else 0)) / 2; v.co.y *= (sy - 0.07 - (0.03 if layer == 2 else 0)) / 2
        vars_ = []
        kinds = ['red', 'red', 'deep', 'green', 'russet']
        for j in range(5):
            vars_.append({'parts': [(apple_bm(layer * 13 + j, r=0.034 + 0.004 * (j % 2), kind=kinds[j], seg=lod), 'food_vc')]})
        outs = gn_scatter(surf, vars_, distance=dist, density=900, seed=sd * 7, scale=(0.92, 1.08), tilt=0.28, tint=0.12, surf_M=f.M @ Matrix.Translation((0, 0, zl)))
        n_total += sum(len(b.faces) for b in outs.values())
        put_outs(outs, Matrix.Identity(4))
        for v in vars_:
            for (bb, mn) in v['parts']:
                bb.free()
        surf.free()
    collider_f(f, sx + 0.02, sy + 0.02, F + sz)
    interact('apple_crate', (pos[0], pos[1], F + 0.35), '사과 상자')
    return f


def build():
    hutch()
    pantry()
    shelf_unit(-1.42, WY, 1.85, seed=2)
    shelf_unit(-1.42, WY, 2.25, seed=3)
    barrel()
    bucket((-0.85, 2.4), water=True)
    bucket((-1.38, 2.42), water=False, seed=1, rot=40, tilt_handle=84)
    crate_apples()
    sack((1.08, 3.0, F), R=0.19, H=0.62, rot=10, seed=1, col=(0.92, 0.88, 0.76), label_cell=(2, 2), lean=(0.3, 0.0))
    sack((1.12, 2.68, F), R=0.17, H=0.5, rot=-30, seed=2, col=(0.85, 0.74, 0.55), tied=True)
    basket_with(Vector((0.45, 2.42, F)), 0.2, 0.22, 3, 'potato')
    wicker_basket(Vector((-0.85, 2.2, F)), 0.14, 0.14, seed=5, handle=False, rot=15)
