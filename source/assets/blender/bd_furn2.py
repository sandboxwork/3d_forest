"""Dresser with swing mirror, bedside tables, desk + chair."""
from bd_lib import *
from bd_hw import *
from bd_bed import fielded_panel, spiral, leaf2d, boolean_diff
from bd_furn import bracket_foot, ogee_foot_poly
import bd_items as I

CREAM = (0.93, 0.89, 0.8)


def drawer_front(f, cx, cz, w, h, y, mat, col, pull='ring', n_pull=2, key=False, pull_mat=None):
    """painted drawer front with applied bead moulding and brass fittings. y = face plane (front)."""
    f.box(mat, (cx, y - 0.008, cz), (w, 0.02, h), bev=0.003, col=col, g=0)
    f.box(mat, (cx, y + 0.0012, cz), (w - 0.05, 0.004, h - 0.045), bev=0.0015, col=mulc(col, (0.97, 0.97, 0.97)), g=0)
    # bead moulding around the field
    hw, hh = (w - 0.036) / 2, (h - 0.03) / 2
    pts = [Vector((cx - hw, y + 0.003, cz - hh)), Vector((cx + hw, y + 0.003, cz - hh)), Vector((cx + hw, y + 0.003, cz + hh)), Vector((cx - hw, y + 0.003, cz + hh))]
    f.tube(mat, pts + [pts[0]], 0.0024, seg=6, col=mulc(col, (1.02, 1.02, 1.0)), caps=False)
    if pull == 'ring':
        xs = [cx - w * 0.26, cx + w * 0.26] if n_pull == 2 else [cx]
        for x in xs:
            ring_pull(f, (x, y + 0.002, cz + 0.0), face=1)
    elif pull == 'knob':
        xs = [cx - w * 0.3, cx + w * 0.3] if n_pull == 2 else [cx]
        for x in xs:
            knob(f, (x, y + 0.002, cz), axis='y', r=0.015, sign=1)
    if key:
        escutcheon(f, (cx, y + 0.003, cz + h * 0.12), h=0.042, w=0.022, face=1)


def drawer_box(f, cx, cz, w, h, d, y_front, mat, col, linens=True):
    """pulled-out drawer carcass: sides, back, bottom, dovetail pins, folded cloth inside"""
    t = 0.012
    yb = y_front - d
    f.box(M['wood_pine'], (cx - w / 2 + 0.03, (y_front + yb) / 2 - 0.01, cz - h / 2 + 0.1 * h), (t, d, h * 0.8), bev=0.0015, col=(1, 0.95, 0.88), g=1)
    f.box(M['wood_pine'], (cx + w / 2 - 0.03, (y_front + yb) / 2 - 0.01, cz - h / 2 + 0.1 * h), (t, d, h * 0.8), bev=0.0015, col=(1, 0.95, 0.88), g=1)
    f.box(M['wood_pine'], (cx, yb, cz - h / 2 + 0.1 * h), (w - 0.06, t, h * 0.8), bev=0.0015, col=(1, 0.95, 0.88), g=0)
    f.box(M['wood_pine'], (cx, (y_front + yb) / 2 - 0.01, cz - h / 2 + 0.04), (w - 0.05, d, 0.008), bev=0.001, col=(0.9, 0.82, 0.72), g=0)
    # dovetail pins on the front corners
    for sx in (-1, 1):
        for k in range(3):
            f.box(M['wood_pine'], (cx + sx * (w / 2 - 0.0285), y_front - 0.012, cz - h / 2 + 0.05 + k * 0.025), (0.006, 0.009, 0.012), bev=0.0005, col=(0.8, 0.7, 0.58))
    if linens:
        for k, cc in enumerate([(0.93, 0.9, 0.8), (0.74, 0.8, 0.86), (0.9, 0.82, 0.7)]):
            f.box(M['linen'], (cx + 0.02 * (k - 1), y_front - d / 2 - 0.01, cz - h / 2 + 0.05 + k * 0.034), (w - 0.1, d - 0.12, 0.035), bev=0.012, seg=3, col=cc, g=0)


def swing_mirror(f, z0, W=0.62, Hh=0.72, tilt=6):
    mat = M['wood_oak']
    col = (0.92, 0.78, 0.62)
    xp = W / 2 + 0.05
    y0 = -0.10
    # posts
    for sx in (-1, 1):
        f.lathe(mat, (sx * xp, y0, z0), profile_pts([(0.0005, 0.0), (0.03, 0.0), (0.034, 0.012), (0.024, 0.03), (0.02, 0.1), (0.026, 0.2), (0.02, 0.34), (0.017, 0.5), (0.02, 0.62), (0.03, 0.7), (0.022, 0.74), (0.012, 0.78), (0.0005, 0.8)], 3),
                seg=16, col=col, cap=False)
        f.sphere(M['brass'], (sx * xp, y0, z0 + 0.8), 0.012, seg=10)
    # base cross-bar
    f.box(mat, (0, y0, z0 + 0.015), (2 * xp, 0.05, 0.03), bev=0.006, col=col, g=0)
    # frame (tilted about the pivot screws)
    zc = z0 + 0.43
    fr = Fr(f.p((0, y0 + 0.0, zc)), f.rot, None)
    # tilt about x through the pivot: build via transformed frames
    Mt = f.M @ Matrix.Translation((0, y0, zc - f.pos.z + f.pos.z * 0)) if False else None
    ff = Fr(f.p((0, y0 + 0.015, zc)), f.rot, None)
    ft = Fr(ff.pos, f.rot, None)
    # apply rotation by composing: use a rotated frame matrix
    ft.M = ff.M @ rotm((-tilt, 0, 0))
    pts = []
    n = 24
    for i in range(n + 1):
        a = math.pi * i / n
        pts.append((math.cos(a) * W / 2, Hh * 0.28 + math.sin(a) * W / 2 * 0.9))
    outline = [(W / 2, -Hh * 0.5), (W / 2, Hh * 0.28)] + pts[1:-1] + [(-W / 2, Hh * 0.28), (-W / 2, -Hh * 0.5)]
    ft.prism(mat, outline, 0.028, c=(0, 0, 0), plane='xz', col=col, bev=0.006, seg=2)
    inner = [(x * 0.82 if abs(x) > 0.001 else x, (z + 0.0) * 0.86 - 0.0) for x, z in outline]
    # glass panel with bevelled edge (chamfer via bevel on the prism)
    gl = [(x * (1 - 0.085 / (W / 2)), z * (1 - 0.0) if z < 0 else (Hh * 0.28 + (z - Hh * 0.28) * (1 - 0.085 / (W / 2)))) for x, z in outline]
    gl = [(x, (z + Hh * 0.5) * 0.9 - Hh * 0.5 + 0.0) for x, z in gl]
    ft.prism(M['mirror'], gl, 0.006, c=(0, 0.0165, 0.0), plane='xz', col=(0.9, 0.95, 0.96), bev=0.0025, seg=1)
    ft.prism(M['wood_dark'], [(x * 0.95, z * 0.97) for x, z in outline], 0.004, c=(0, -0.016, 0), plane='xz', col=(0.6, 0.5, 0.42), skip_down=False)
    # carved crest on the arch
    ft.sphere(mat, (0, 0.016, Hh * 0.28 + W / 2 * 0.9 + 0.005), 0.02, seg=10, sq=(1, 0.5, 1.3), col=(1.1, 1.0, 0.9))
    for sx in (-1, 1):
        ft.cyl(M['brass'], (sx * (W / 2 + 0.012), 0.0, 0.0), 0.011, 0.014, axis='x', seg=10, bev=0.002)
        ft.sphere(M['brass'], (sx * (W / 2 + 0.03), 0.0, 0.0), 0.012, seg=10)


def dresser(pos, rot, W=1.0, D=0.48, H=0.9, items=True):
    f = Fr(pos, rot, F)
    mat = M['paint']
    col = CREAM
    mat_t = M['wood_oak']
    colw = (1.0, 0.93, 0.85)
    # bracket feet
    for sx in (-1, 1):
        for sy in (-1, 1):
            bracket_foot(f, sx * (W / 2 - 0.005), sy * (D / 2 - 0.005), mat, col, sx, sy, 0.11, 0.1)
    f.box(mat, (0, 0, 0.115), (W + 0.002, D + 0.002, 0.03), bev=0.004, col=col, g=0)
    f.box(mat, (0, 0.0, 0.14), (W + 0.02, D + 0.02, 0.022), bev=0.007, col=mulc(col, (1.02, 1.02, 1.0)), g=0)
    zt = H - 0.036
    # carcass shell + dark recess behind fronts
    for sx in (-1, 1):
        f.box(mat, (sx * (W / 2 - 0.011), -0.01, (0.155 + zt) / 2), (0.022, D - 0.02, zt - 0.155), bev=0.002, col=col, g=2)
        fs = Fr(f.p((sx * W / 2, 0, 0)), f.rot + (-90 if sx > 0 else 90), None)
        fielded_panel(fs, 0.0, 0.5, D - 0.12, 0.55, 0.002, 1, mat=mat, col=col)
    f.box(mat, (0, -D / 2 + 0.01, (0.155 + zt) / 2), (W - 0.04, 0.02, zt - 0.155), bev=0.002, col=col, g=0)
    f.box(mat, (0, 0.0, 0.155 + 0.005), (W - 0.04, D - 0.04, 0.012), bev=0.002, col=col, g=0)
    yfp = D / 2 - 0.004        # drawer face plane
    f.box(mat, (0, yfp - 0.03, (0.155 + zt) / 2), (W - 0.03, 0.01, zt - 0.155), bev=0, col=(0.16, 0.13, 0.1), g=2)   # dark recess behind drawer gaps
    # drawers (z zones)
    gap = 0.007
    z = 0.168
    zones = [(0.19, 'long'), (0.19, 'long'), (0.185, 'long'), (0.14, 'split')]
    z_cursor = 0.165
    drawers = []
    for hgt, kind in zones:
        drawers.append((z_cursor + hgt / 2, hgt, kind))
        z_cursor += hgt + gap
    free_top = zt - 0.005 - z_cursor + gap
    # stretch last row to meet the top rail
    zl = drawers[-1]
    drawers[-1] = (zl[0] + free_top / 2, zl[1] + free_top, zl[2])
    for i, (cz, hh, kind) in enumerate(drawers):
        if kind == 'long':
            if i == 1:
                # ajar drawer: front pulled 0.08 forward with box and linens
                drawer_front(f, 0, cz, W - 0.045, hh - gap, yfp + 0.085, mat, col, pull='ring', key=True)
                drawer_box(f, 0, cz, W - 0.045, hh - gap, 0.4, yfp + 0.085 - 0.016, mat, col)
            else:
                drawer_front(f, 0, cz, W - 0.045, hh - gap, yfp, mat, col, pull='ring', key=True)
        else:
            dw = (W - 0.045 - gap) / 2
            for sx in (-1, 1):
                drawer_front(f, sx * (dw / 2 + gap / 2), cz, dw, hh - gap, yfp, mat, col, pull='knob', n_pull=2 if False else 1)
    # top: oak with ogee front edge, stringing inlay
    f.box(mat_t, (0, 0.005, H - 0.018), (W + 0.05, D + 0.04, 0.036), bev=0.012, seg=3, col=colw, g=0)
    f.box(M['wood_dark'], (0, 0.005, H + 0.0004), (W - 0.06, 0.004, 0.0008), bev=0, col=(0.7, 0.55, 0.45)) if False else None
    for (cx, cy, sx_, sy_) in ((0, D / 2 - 0.035, W - 0.1, 0.004), (0, -D / 2 + 0.05, W - 0.1, 0.004), (-W / 2 + 0.05, 0.0, 0.004, D - 0.1), (W / 2 - 0.05, 0.0, 0.004, D - 0.1)):
        f.box(M['wood_dark'], (cx, cy, H + 0.0006), (sx_, sy_, 0.0012), bev=0, col=(0.8, 0.65, 0.5), skip_down=False)
    # chipped paint on edges
    def region(r):
        side = r.choice(['front_edge', 'corner', 'drawer_top'])
        if side == 'front_edge':
            return (r.uniform(-W / 2 + 0.03, W / 2 - 0.03), yfp + 0.001, r.choice([0.155 + 0.01, 0.16, zt - 0.012])), 'y+'
        if side == 'corner':
            sx = r.choice([-1, 1])
            return (sx * (W / 2 + 0.0005), r.uniform(D / 2 - 0.05, D / 2 - 0.005), r.uniform(0.15, 0.8)), 'x+' if sx > 0 else 'x-'
        return (r.uniform(-W / 2 + 0.04, W / 2 - 0.04), yfp + 0.0015, r.choice(drawers)[0] + r.choice([-1, 1]) * r.choice(drawers)[1] * 0.45), 'y+'
    chips(f, region, 46, size=(0.0045, 0.014), mat=M['wood_pine'], col=(0.74, 0.58, 0.38), seed=5)
    collider_f(f, W + 0.06, D + 0.07, F + H + 0.02, name='dresser')
    # swing mirror at the back of the dresser top
    swing_mirror(f, H, 0.58, 0.7, tilt=5)
    if items:
        dresser_items(f, W, D, H)
    return f


def dresser_items(f, W, D, H):
    z = H + 0.002
    # brass tray with perfume bottles
    cx, cy = -0.08, 0.0
    prof = [(0.0005, 0.0), (0.14, 0.0), (0.15, 0.004), (0.152, 0.018), (0.146, 0.018), (0.144, 0.006), (0.0005, 0.006)]
    f.lathe(M['brass'], (cx, cy, z), prof, seg=36, cap=False, scale=(1.0, 0.68, 1.0))
    p0 = f.p((cx, cy, z + 0.006))
    I.perfume_bottle(f.p((cx - 0.06, cy + 0.0, z + 0.006)), 0, (0.6, 0.78, 0.9), 0.1)
    I.perfume_bottle(f.p((cx + 0.02, cy - 0.025, z + 0.006)), 1, (0.9, 0.75, 0.85), 0.12)
    I.perfume_bottle(f.p((cx + 0.08, cy + 0.03, z + 0.006)), 2, (0.78, 0.9, 0.7), 0.1)
    # jewelry box
    I.jewelry_box(f.p((0.22, 0.03, z)), f.rot + 8)
    # hairbrush + comb + hand mirror laying in front
    I.hairbrush(f.p((0.4, 0.14, z)), f.rot + 100)
    # hand mirror
    hm = f.p((0.3, -0.14, z))
    Mx = xf(hm, (0, 0, f.rot + 30))
    torus(M['brass'], None, 0.045, 0.004, plane='xy', Mx=Mx @ Matrix.Translation((0, 0, 0.006)), seg=24, rseg=6)
    lathe(M['mirror'], None, [(0.0005, 0.0), (0.043, 0.0), (0.0005, 0.0)], seg=24, cap=False, Mx=Mx @ Matrix.Translation((0, 0, 0.0075)))
    tube(M['brass'], [Mx @ Vector((0.045, 0, 0.006)), Mx @ Vector((0.14, 0, 0.007))], 0.006, seg=8, caps=True)
    # chamberstick (lit) + framed photo + small vase of dried flowers
    I.chamberstick(f.p((-0.36, -0.13, z)), lit=True, inten=0.7, dist=4.5)
    # standing photo frame
    fp = f.p((0.45, -0.05, z))
    Mx = xf(fp, (0, 0, f.rot + 20)) @ rotm((-12, 0, 0))
    box(M['wood_dark'], None, (0.11, 0.012, 0.15), Mx=Mx @ Matrix.Translation((0, 0, 0.075)), bev=0.0025, col=(0.8, 0.7, 0.6))
    I.paint_quad(Mx @ Matrix.Translation((0, 0.0066, 0.075)), 0.08, 0.11, 6)
    # folded linen cloths at the right end
    for k, cc in enumerate([(0.93, 0.9, 0.82), (0.7, 0.78, 0.86), (0.9, 0.84, 0.7)]):
        soft_box(M['linen'], f._m((-0.38, 0.09, z + 0.013 + k * 0.026), (0, 0, 4 * (k - 1))), (0.2 - 0.01 * k, 0.15, 0.028), col=cc, disp=0.002)
    # lace doily under the jewelry box
    f.cyl(M['linen'], (0.22, 0.03, z + 0.0005), 0.1, 0.001, seg=24, col=(0.97, 0.95, 0.9))
    f.torus(M['linen'], (0.22, 0.03, z + 0.001), 0.1, 0.0016, plane='xy', seg=36, rseg=4, col=(0.95, 0.92, 0.85))


def bedside(pos, rot, side=1, W=0.44, D=0.38, H=0.62, items=True):
    f = Fr(pos, rot, F)
    mat = M['wood_oak']
    col = (1.0, 0.93, 0.86) if side > 0 else (0.95, 0.86, 0.78)
    # tapered legs with turned cuffs
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (W / 2 - 0.022), sy * (D / 2 - 0.022)
            bm = bm_box(0.034, 0.034, H - 0.1)
            for v in bm.verts:
                k = 1 - 0.28 * (0.5 - v.co.z / (H - 0.1))
                v.co.x *= k; v.co.y *= k
                v.co.z += (H - 0.1) / 2
            f.put(mat, bm, c=(x, y, 0.0), col=col, g=2)
            bm.free()
            f.lathe(mat, (x, y, 0.0), profile_pts([(0.0005, 0), (0.014, 0.0), (0.016, 0.015), (0.011, 0.03), (0.012, 0.06)], 2), seg=12, col=col, cap=False)
    # apron + drawer + shelf + top
    zt = H - 0.025
    f.box(mat, (0, -D / 2 + 0.02, H - 0.1), (W - 0.04, 0.018, 0.12), bev=0.002, col=col, g=0)
    for sx in (-1, 1):
        f.box(mat, (sx * (W / 2 - 0.022), 0, H - 0.1), (0.018, D - 0.04, 0.12), bev=0.002, col=col, g=1)
    f.box(mat, (0, 0, 0.21), (W - 0.04, D - 0.04, 0.018), bev=0.003, col=col, g=0)
    # shelf gallery rail (small turned spindles)
    for i in range(9):
        x = -W / 2 + 0.06 + i * (W - 0.12) / 8
        f.lathe(mat, (x, D / 2 - 0.025, 0.219), profile_pts([(0.0005, 0), (0.007, 0.0), (0.0055, 0.012), (0.0075, 0.024), (0.0045, 0.036), (0.0005, 0.04)], 2), seg=8, col=col, cap=False)
    f.box(mat, (0, D / 2 - 0.025, 0.264), (W - 0.04, 0.012, 0.012), bev=0.002, col=col, g=0)
    # drawer
    yfp = D / 2 - 0.018
    f.box(mat, (0, yfp, H - 0.105), (W - 0.06, 0.02, 0.1), bev=0.003, col=col, g=0)
    f.box(mat, (0, yfp + 0.0105, H - 0.105), (W - 0.12, 0.004, 0.056), bev=0.0015, col=(1.06, 0.98, 0.9), g=0)
    f.tube(mat, [Vector(p) for p in [(-W / 2 + 0.07, yfp + 0.012, H - 0.145), (W / 2 - 0.07, yfp + 0.012, H - 0.145), (W / 2 - 0.07, yfp + 0.012, H - 0.065), (-W / 2 + 0.07, yfp + 0.012, H - 0.065), (-W / 2 + 0.07, yfp + 0.012, H - 0.145)]], 0.0022, seg=5, col=(1.08, 1.0, 0.92), caps=False)
    knob(f, (0, yfp + 0.012, H - 0.105), axis='y', r=0.016, sign=1)
    escutcheon(f, (0.0, yfp + 0.012, H - 0.145 + 0.012), h=0.03, w=0.016, face=1) if False else None
    # top with moulded edge
    f.box(mat, (0, 0, H - 0.012), (W + 0.04, D + 0.04, 0.026), bev=0.01, seg=3, col=(1.05, 0.97, 0.9), g=0)
    f.box(M['wood_dark'], (0, 0, H + 0.0006), (W - 0.04, D - 0.04, 0.0012), bev=0, col=(0.8, 0.65, 0.5)) if False else None
    collider_f(f, W + 0.05, D + 0.05, F + H + 0.01, name='bedside_left' if side > 0 else 'bedside_right')
    if items:
        bedside_items(f, side, W, D, H)
    return f


def bedside_items(f, side, W, D, H):
    z = H + 0.0
    if side > 0:
        # left (x=1.97): oil lamp, book stack + ribbon, water carafe + glass, doily
        f.cyl(M['linen'], (0.0, 0.0, z + 0.0005), 0.11, 0.001, seg=24, col=(0.97, 0.95, 0.9))
        I.oil_lamp(f.p((-0.01, -0.03, z + 0.001)), sc=1.0, inten=1.0, dist=6.0)
        I.book_flat(f.p((0.12, 0.05, z)), (0.16, 0.11, 0.028), rotz=f.rot + 12, col='#6b3a2a', ribbon='#8c2b2b')
        I.book_flat(f.p((0.12, 0.05, z + 0.028)), (0.14, 0.1, 0.02), rotz=f.rot - 8, col='#2f4a63')
        I.wine_carafe(f.p((-0.14, 0.09, z)), 0.045, 0.19, 0.5)
        I.glass_tumbler(f.p((-0.14, 0.09, z + 0.19)), 0.036, 0.06, 0.0) if False else None
        I.glass_tumbler(f.p((-0.07, 0.12, z)), 0.03, 0.09, 0.65)
        # spectacles
        reading = f.p((0.15, -0.09, z + 0.0))
        torus(M['brass'], reading + Vector((0, 0, 0.012)), 0.014, 0.0009, plane='xz', Mx=xf(reading + Vector((-0.016, 0, 0.012)), (0, 0, f.rot + 20)), seg=14, rseg=3) if False else None
    else:
        # right: candle on chamberstick, small stack, glasses, matchbox, little bell, tray
        f.cyl(M['linen'], (0.0, -0.01, z + 0.0005), 0.11, 0.001, seg=24, col=(0.95, 0.92, 0.86))
        I.chamberstick(f.p((0.0, -0.02, z + 0.001)), lit=True, inten=0.9, dist=5.0, cl=0.13)
        I.book_flat(f.p((-0.12, 0.07, z)), (0.18, 0.12, 0.026), rotz=f.rot - 15, col='#3d5a3a')
        I.book_flat(f.p((-0.12, 0.07, z + 0.026)), (0.15, 0.105, 0.022), rotz=f.rot + 10, col='#8a6a2e')
        I.book_flat(f.p((-0.12, 0.07, z + 0.048)), (0.13, 0.095, 0.02), rotz=f.rot - 4, col='#7a2f2a')
        # matchbox
        box(M['paper'], f.p((0.12, 0.09, z + 0.007)), (0.052, 0.034, 0.014), rot=(0, 0, f.rot + 25), bev=0.001, col=(0.8, 0.55, 0.3), g=0)
        box(M['paper'], f.p((0.12, 0.09, z + 0.0145)), (0.04, 0.026, 0.001), rot=(0, 0, f.rot + 25), bev=0, col=(0.95, 0.85, 0.65), skip_down=False)
        # brass bell
        p = f.p((0.14, -0.08, z))
        lathe(M['brass'], p, profile_pts([(0.0005, 0.0), (0.028, 0.0), (0.03, 0.006), (0.024, 0.03), (0.015, 0.05), (0.008, 0.062), (0.0005, 0.066)], 3), seg=18, cap=False)
        tube(M['brass'], [p + Vector((0, 0, 0.065)), p + Vector((0, 0.006, 0.075)), p + Vector((0, 0.0, 0.082))], 0.003, seg=6)
        I.glass_tumbler(f.p((-0.14, -0.1, z)), 0.03, 0.09, 0.0)


# ---------------------------------------------------------------- desk + chair
def desk(pos, rot, W=1.15, D=0.6, H=0.76, items=True):
    f = Fr(pos, rot, F)
    mat = M['wood_oak']
    col = (1.0, 0.93, 0.86)
    colp = (0.86, 0.78, 0.68)
    # top slab with moulded edge
    f.box(mat, (0, 0, H - 0.0225), (W + 0.04, D + 0.04, 0.045), bev=0.012, seg=3, col=col, g=0)
    # leather inlay with gilt border
    lw, ld = W - 0.16, D - 0.14
    f.box(M['leather'], (0, 0.0, H + 0.0006), (lw, ld, 0.0016), bev=0.0004, col=(0.22, 0.34, 0.26), g=0, skip_down=False)
    for (cx, cy, sx_, sy_) in ((0, ld / 2 - 0.012, lw - 0.03, 0.003), (0, -ld / 2 + 0.012, lw - 0.03, 0.003), (-lw / 2 + 0.012, 0.0, 0.003, ld - 0.03), (lw / 2 - 0.012, 0.0, 0.003, ld - 0.03)):
        f.box(M['brass'], (cx, cy, H + 0.0016), (sx_, sy_, 0.0008), bev=0, col=(1.0, 0.85, 0.5), skip_down=False)
        f.box(M['brass'], (cx, cy, H + 0.0016), (sx_ + 0.0 if sx_ > 0.01 else sx_, sy_, 0.0008), bev=0, col=(1.0, 0.85, 0.5), skip_down=False) if False else None
    # corner fleurons
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.sphere(M['brass'], (sx * (lw / 2 - 0.02), sy * (ld / 2 - 0.02), H + 0.0016), 0.007, seg=8, sq=(1, 1, 0.2), col=(1.0, 0.85, 0.5))
    # left pedestal with three drawers
    px = -W / 2 + 0.22
    f.box(mat, (px, 0, (H - 0.045 + 0.08) / 2), (0.42, D - 0.04, H - 0.045 - 0.08), bev=0.003, col=colp, g=2)
    f.box(mat, (px, 0, 0.04), (0.44, D - 0.02, 0.08), bev=0.006, col=col, g=0)
    zs = [(0.64, 0.17), (0.455, 0.17), (0.27, 0.17)]
    yfp = D / 2 - 0.02
    for (zc, hh) in zs:
        f.box(mat, (px, yfp, zc), (0.38, 0.02, hh - 0.01), bev=0.003, col=col, g=0)
        f.box(mat, (px, yfp + 0.0105, zc), (0.31, 0.004, hh - 0.06), bev=0.0015, col=(1.07, 0.99, 0.91), g=0)
        # cup pull: backplate + cup
        f.cyl(M['brass'], (px, yfp + 0.012, zc + 0.02), 0.014, 0.003, axis='y', seg=12)
        f.lathe(M['brass'], (px, yfp + 0.013, zc - 0.012), profile_pts([(0.0005, 0.0), (0.016, 0.0), (0.017, 0.004), (0.015, 0.012), (0.0005, 0.016)], 2), r=(-90, 0, 0), seg=14, cap=False, scale=(1.4, 1.0, 1.0)) if False else None
        drop_pull(f, (px, yfp + 0.012, zc), face=1, w=0.075)
        escutcheon(f, (px, yfp + 0.012, zc + 0.045), h=0.032, w=0.018, face=1)
    # centre apron drawer
    f.box(mat, (0.12, yfp, H - 0.085), (W - 0.5, 0.02, 0.09), bev=0.003, col=col, g=0)
    f.box(mat, (0.12, yfp + 0.0105, H - 0.085), (W - 0.58, 0.004, 0.05), bev=0.0015, col=(1.07, 0.99, 0.91), g=0)
    knob(f, (0.12 - 0.12, yfp + 0.012, H - 0.085), axis='y', r=0.014, sign=1)
    knob(f, (0.12 + 0.12, yfp + 0.012, H - 0.085), axis='y', r=0.014, sign=1)
    escutcheon(f, (0.12, yfp + 0.012, H - 0.085), h=0.034, w=0.018, face=1)
    # turned legs on the right, back panel (kneehole)
    for sy in (-1, 1):
        lx, ly = W / 2 - 0.05, sy * (D / 2 - 0.05)
        f.lathe(mat, (lx, ly, 0.0), profile_pts([(0.0005, 0), (0.02, 0.0), (0.024, 0.02), (0.017, 0.05), (0.02, 0.1), (0.026, 0.16), (0.017, 0.25), (0.019, 0.4), (0.024, 0.5), (0.03, 0.6), (0.036, 0.68), (0.036, H - 0.045)], 3), seg=16, col=col, cap=True)
    f.box(mat, (W / 2 - 0.05, 0, H - 0.09), (0.02, D - 0.1, 0.09), bev=0.003, col=colp, g=1)
    f.box(mat, (0.0, -D / 2 + 0.02, 0.4), (W - 0.3, 0.014, 0.58), bev=0.002, col=(0.8, 0.72, 0.62), g=0)
    f.box(mat, (0.12, -D / 2 + 0.04, H - 0.09), (W - 0.55, 0.02, 0.08), bev=0.003, col=colp, g=0)
    # stretcher between right legs
    f.cyl(mat, (W / 2 - 0.05, 0, 0.17), 0.011, D - 0.1, axis='y', seg=10, col=colp)
    collider_f(f, W + 0.05, D + 0.05, F + H + 0.01, name='desk')
    # pigeonhole organiser at the back of the top
    organiser(f, H, W, D)
    if items:
        desk_items(f, H, W, D)
    return f


def organiser(f, H, W, D):
    mat = M['wood_dark']
    col = (1.0, 0.93, 0.86)
    ow, oh, od = 0.5, 0.2, 0.17
    cx, cy = 0.12, -D / 2 + od / 2 + 0.03
    z0 = H + 0.0
    f.box(mat, (cx, cy, z0 + oh - 0.006), (ow + 0.02, od + 0.01, 0.014), bev=0.003, col=col, g=0)
    f.box(mat, (cx, cy, z0 + 0.006), (ow, od, 0.012), bev=0.002, col=col, g=0)
    for sx in (-1, 1):
        f.box(mat, (cx + sx * (ow / 2 - 0.006), cy, z0 + oh / 2), (0.012, od, oh), bev=0.002, col=col, g=2)
    f.box(mat, (cx, cy - od / 2 + 0.004, z0 + oh / 2), (ow, 0.008, oh), bev=0.0015, col=(0.7, 0.62, 0.54), g=0)
    # shelf + dividers
    f.box(mat, (cx, cy, z0 + oh * 0.5), (ow, od - 0.01, 0.008), bev=0.0015, col=col, g=0)
    for k in range(-2, 3):
        if k == 0:
            continue
        f.box(mat, (cx + k * ow / 6, cy, z0 + oh * 0.75), (0.006, od - 0.01, oh * 0.5), bev=0.001, col=col, g=2)
    # three tiny drawers below with brass knobs
    for k in (-1, 0, 1):
        x = cx + k * (ow - 0.02) / 3
        f.box(mat, (x, cy + od / 2 - 0.004, z0 + oh * 0.25 + 0.003), (ow / 3 - 0.012, 0.012, oh * 0.4), bev=0.002, col=(1.05, 0.97, 0.9), g=0)
        knob(f, (x, cy + od / 2 + 0.002, z0 + oh * 0.25 + 0.003), axis='y', r=0.009, sign=1)
    # letters in the slots
    for k in (-2, 2, 3):
        x = cx + (k - 0.5) * ow / 6 + 0.0
        for j in range(2):
            f.box(M['paper'], (x + 0.004 * j, cy + 0.01, z0 + oh * 0.76 + 0.01 * j), (0.07, 0.006, 0.09), rot=(0, 3 * j, 6 * (j - 0.5)), bev=0.0004, col=(0.93, 0.88, 0.75), g=2)
    # finials
    for sx in (-1, 1):
        f.sphere(mat, (cx + sx * (ow / 2 - 0.006), cy + od / 2 - 0.01, z0 + oh + 0.008), 0.011, seg=10, col=col)


def desk_items(f, H, W, D):
    z = H + 0.0022
    # blotter + papers
    I.papers_sheet(f.p((-0.12, 0.02, z)), f.rot + 8, (0.21, 0.297), 12, seed=1)
    I.papers_sheet(f.p((-0.14, 0.05, z + 0.0012)), f.rot - 12, (0.2, 0.28), 10, seed=2)
    I.papers_sheet(f.p((-0.09, 0.0, z + 0.0024)), f.rot + 3, (0.2, 0.28), 7, seed=3)
    I.envelope(f.p((0.2, 0.12, z)), f.rot + 38)
    I.envelope(f.p((0.24, 0.1, z + 0.002)), f.rot + 12, seal=False)
    # inkwell + quill
    I.inkwell(f.p((0.31, 0.02, z)))
    I.feather_quill(f.p((0.31, 0.02, z + 0.038)), f.rot - 150, tilt=-12, L=0.25)
    # books: stack + open book
    I.book_flat(f.p((-0.38 + 0.0, -0.14, z)), (0.22, 0.16, 0.03), rotz=f.rot + 4, col='#7a2f2a', ribbon='#c9a24a')
    I.book_flat(f.p((-0.38, -0.14, z + 0.03)), (0.2, 0.15, 0.026), rotz=f.rot - 7, col='#2f4a63')
    I.book_flat(f.p((-0.38, -0.14, z + 0.056)), (0.19, 0.14, 0.022), rotz=f.rot + 9, col='#3d5a3a')
    I.book_open(f.p((0.0, 0.18, z)), f.rot + 6, w=0.12, d=0.17, col='#4a2f4f', seed=4)
    # magnifier on the open book
    I.magnifier(f.p((0.05, 0.19, z + 0.018)), f.rot + 30)
    # desk lamp (oil lamp) at right-back corner
    I.oil_lamp(f.p((0.45, -0.18, z)), sc=1.0, inten=1.2, dist=6.0)
    # pen tray with pens + sealing wax stick
    f.box(M['brass'], (0.26, -0.12, z + 0.004), (0.17, 0.05, 0.008), bev=0.003, col=(1.0, 0.9, 0.7))
    for k, c in enumerate(((0.1, 0.1, 0.1), (0.5, 0.1, 0.1))):
        f.cyl(M['wood_dark'], (0.26 + (k - 0.5) * 0.04, -0.12, z + 0.012), 0.0035, 0.15, axis='x', seg=6, col=c, rot=(0, 0, 4 * k))
    f.cyl(M['wax'], (0.28, -0.1, z + 0.012), 0.0045, 0.09, axis='x', seg=6, col=(0.6, 0.1, 0.1), rot=(0, 0, 25))


def desk_chair(pos, rot):
    """Windsor-style desk chair with saddle seat, splayed turned legs, bow back and spindles."""
    f = Fr(pos, rot, F)
    mat = M['wood_dark']
    col = (1.0, 0.93, 0.86)
    SH = 0.46
    # saddle seat: lathe of an oval dish
    prof = profile_pts([(0.0005, -0.012), (0.12, -0.016), (0.19, -0.008), (0.21, 0.01), (0.215, 0.026), (0.2, 0.034), (0.0005, 0.0)], 3)
    f.lathe(mat, (0, 0.0, SH - 0.034), [(r, z) for r, z in prof], seg=28, cap=False, col=col, scale=(1.0, 0.95, 1.0))
    f.box(mat, (0, 0.0, SH - 0.044), (0.3, 0.3, 0.02), bev=0.005, col=col)
    # legs: splayed, turned
    legs = [(-0.16, -0.14), (0.16, -0.14), (-0.17, 0.15), (0.17, 0.15)]
    for (x, y) in legs:
        sx = -1 if x < 0 else 1
        sy = -1 if y < 0 else 1
        sp = Vector((sx * 0.05, sy * 0.05, -1)).normalized()
        base = Vector((x, y, SH - 0.04))
        pts = [base + sp * t for t in np.linspace(0, SH - 0.04 + 0.0, 1)] if False else None
        f.lathe(mat, (x + sx * 0.0, y, 0.0), [], seg=8) if False else None
        # approximated by tube with taper & rings
        top = Vector((x, y, SH - 0.04))
        bot = Vector((x + sx * 0.06, y + sy * 0.05, 0.0))
        path = [top + (bot - top) * t for t in np.linspace(0, 1, 12)]
        rr = [0.019, 0.019, 0.025, 0.02, 0.016, 0.014, 0.019, 0.022, 0.017, 0.014, 0.013, 0.012]
        f.tube(mat, path, rr, seg=10, col=col)
    # stretchers (H-shape)
    for (a, b) in (((-0.1, -0.1, 0.17), (-0.1, 0.1, 0.17)), ((0.1, -0.1, 0.17), (0.1, 0.1, 0.17))):
        f.tube(mat, [Vector(a), Vector(b)], 0.0085, seg=8, col=col)
    f.tube(mat, [Vector((-0.1, 0.0, 0.17)), Vector((0.1, 0.0, 0.17))], 0.0085, seg=8, col=col)
    # back: bow + spindles
    bow = []
    n = 16
    for i in range(n + 1):
        a = math.pi * i / n
        bow.append(Vector((math.cos(a) * 0.17, -0.15 - 0.03 * math.sin(a) - 0.0, SH + 0.28 + 0.07 * math.sin(a))))
    # rail at the top
    f.tube(mat, [Vector((-0.175, -0.145 - 0.02 * (1 - abs(x) / 0.175), SH + 0.34)) for x in np.linspace(-0.175, 0.175, 12)], 0.0155, seg=10, col=col, flat=(1.0, 0.9))
    for sx in (-1, 1):
        f.tube(mat, [Vector((sx * 0.17, -0.14, SH - 0.03)), Vector((sx * 0.172, -0.15, SH + 0.15)), Vector((sx * 0.17, -0.16, SH + 0.34))], 0.0145, seg=10, col=col)
    for i in range(5):
        x = -0.1 + i * 0.05
        f.tube(mat, [Vector((x, -0.14, SH - 0.03)), Vector((x, -0.15, SH + 0.15)), Vector((x, -0.16 - 0.015 * (1 - abs(x) / 0.17), SH + 0.34))], 0.0085, seg=8, col=col)
    # cushion (leather pad, tied)
    soft_box(M['leather'], f._m((0, 0.01, SH + 0.014)), (0.34, 0.33, 0.032), col=(0.5, 0.35, 0.25), disp=0.0015)
    f.cyl(M['brass'], (0, 0.01, SH + 0.025), 0.007, 0.004, seg=8)
    collider_f(f, 0.5, 0.5, F + 0.5, name='desk_chair')
    return f
