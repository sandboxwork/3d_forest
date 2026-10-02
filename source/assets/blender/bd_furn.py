"""Hand-modelled furniture: wardrobe, dresser(+mirror), bedside tables, desk+chair, trunk, rocking chair, washstand, shelf."""
from bd_lib import *
from bd_hw import *
from bd_bed import fielded_panel, spiral, leaf2d, boolean_diff
import bd_garment as G
from bd_cloth import *


def ogee_foot_poly(w=0.15, h=0.13):
    """bracket foot silhouette (x along face, z up)"""
    pts = [(0, h), (w, h), (w, h * 0.84)]
    for i in range(1, 9):
        t = i / 8
        # S-curve down to the toe
        pts.append((w - 0.02 - (w - 0.035) * (0.5 - 0.5 * math.cos(math.pi * t)) * 0.6 - 0.0, h * 0.84 * (1 - t) ** 1.15))
    pts += [(0.0, 0.0), (0.0, h * 0.5)]
    return pts


def bracket_foot(f, x, y, mat, col, sx, sy, w=0.15, h=0.13):
    """ogee bracket foot at corner (x,y); sx,sy = corner signs. two mitred brackets"""
    poly = ogee_foot_poly(w, h)
    f.prism(mat, [(x - sx * a, b) for a, b in poly], 0.028, c=(0, y - sy * 0.014, 0), plane='xz', col=col, bev=0.002)
    f.prism(mat, [(y - sy * a, b) for a, b in poly], 0.028, c=(x - sx * 0.014, 0, 0), plane='yz', col=col, bev=0.002)


def door_leaf(f, hinge, hs, dw, dh, theta, mat, col, lock=False, knob_side=-1, inner=True):
    """paneled, carved wardrobe door. hinge = local (x,y,z_bottom) of the hinge axis in wardrobe frame f; hs=+1 hinge at +x edge.
    theta: opening angle deg (outward). Built in a rotated frame."""
    rot = f.rot + (-theta if hs > 0 else theta)
    origin = f.p(hinge)
    fd = Fr(origin, rot, origin.z)
    X = lambda x: -hs * x          # x measured from the hinge edge toward the free edge
    t = 0.027
    sw = 0.072
    # stiles
    fd.box(mat, (X(sw / 2), 0, dh / 2), (sw, t, dh), bev=0.004, col=col, g=2)
    fd.box(mat, (X(dw - sw / 2), 0, dh / 2), (sw, t, dh), bev=0.004, col=col, g=2)
    # rails
    zmid = dh * 0.36
    for (zc, rh) in ((0.05, 0.1), (zmid, 0.085), (dh - 0.055, 0.11)):
        fd.box(mat, (X(dw / 2), 0, zc), (dw - 2 * sw + 0.004, t, rh), bev=0.004, col=col, g=0)
    # lower raised panel
    pw = dw - 2 * sw - 0.03
    lh = zmid - 0.1 - 0.045
    fd.box(mat, (X(dw / 2), -0.002, 0.1 + 0.0 + (zmid - 0.0425 - 0.1) / 2 + 0.0425 - 0.0425), (pw + 0.02, 0.012, zmid - 0.0425 - 0.1 - 0.0), bev=0.002, col=(0.7, 0.62, 0.56), g=0)
    zl = 0.1 + (zmid - 0.0425 - 0.1) / 2
    fielded_panel(fd, X(dw / 2), zl, pw, zmid - 0.0425 - 0.1 - 0.012, 0.0, 1, mat=mat, col=col)
    # upper arched panel
    za = zmid + 0.0425 + 0.0
    zb = dh - 0.11 - 0.0
    arch_r = pw / 2
    pts = []
    pts.append((X(dw / 2) - hs * 0 + pw / 2, za)); pts.append((X(dw / 2) - pw / 2, za))
    x0 = X(dw / 2)
    pts = [(x0 + pw / 2, za), (x0 + pw / 2, zb - arch_r * 0.55)]
    for i in range(1, 17):
        a = math.pi * i / 16
        pts.append((x0 + math.cos(a) * pw / 2, zb - arch_r * 0.55 + math.sin(a) * arch_r * 0.55))
    pts.append((x0 - pw / 2, za))
    # back (recessed) board
    fd.prism(mat, [(x_, z_) for x_, z_ in pts], 0.012, c=(0, -0.002, 0), plane='xz', col=(0.7, 0.62, 0.56), g=0)
    # raised moulding frame (bead following the arch) + inner panel
    inner_pts = []
    ip = 0.03
    ph = zb - arch_r * 0.55
    inner_pts = [(x0 + pw / 2 - ip, za + ip), (x0 + pw / 2 - ip, ph)]
    for i in range(1, 17):
        a = math.pi * i / 16
        inner_pts.append((x0 + math.cos(a) * (pw / 2 - ip), ph + math.sin(a) * (arch_r * 0.55 - ip * 0.6)))
    inner_pts.append((x0 - pw / 2 + ip, za + ip))
    fd.prism(mat, inner_pts, 0.012, c=(0, 0.008, 0), plane='xz', col=(1.08, 1.0, 0.92), bev=0.004, g=0)
    fd.tube(mat, [Vector((px, 0.016, pz)) for px, pz in inner_pts + [inner_pts[0]]], 0.0035, seg=6, col=(1.12, 1.04, 0.95))
    # carved ornament: rosette + scrolls + leaves + pendant bell chain
    cz = ph + 0.02
    oy = 0.0215
    cc = (1.12, 1.03, 0.94)
    fd.lathe(mat, (x0, oy, cz), [(0.001, 0.012), (0.026, 0.009), (0.045, 0.003), (0.05, 0.0)], r=(-90, 0, 0), seg=24, cap=False, col=cc)
    for k in range(8):
        a = k * TAU / 8
        pl = [(0.052, -0.009), (0.09, -0.002), (0.1, 0.0), (0.09, 0.002), (0.052, 0.009)]
        pl = [(x0 + px * math.cos(a) - py * math.sin(a), cz + px * math.sin(a) + py * math.cos(a)) for px, py in pl]
        fd.prism(mat, pl, 0.005, c=(0, oy + 0.002, 0), plane='xz', bev=0.001, col=cc, g=0)
    fd.sphere(mat, (x0, oy + 0.009, cz), 0.014, seg=10, sq=(1, 0.55, 1), col=(1.18, 1.08, 1.0))
    for s in (-1, 1):
        sp = spiral(x0 + s * 0.14, cz + 0.01, 0.045, 0.01, 1.25, math.pi * (0.1 if s > 0 else 0.9), 24, -s)
        fd.tube(mat, [Vector((a_, oy + 0.003, b_)) for a_, b_ in sp], [0.0065 * (1 - 0.6 * i / 24) for i in range(25)], seg=6, col=cc)
        for k, tt in enumerate((0.45,)):
            fd.prism(mat, leaf2d(x0 + s * (0.1 + 0.07 * tt), cz - 0.05 * (1 - tt) - 0.01, (-0.7 if k else 0.7) + (0 if s > 0 else math.pi * 0), 0.04, 0.012), 0.005,
                     c=(0, oy + 0.003, 0), plane='xz', bev=0.0008, col=cc, g=0)
    # pendant bell-flower chain (husks) down the lower centre
    for k in range(5):
        zz = cz - 0.1 - k * 0.032
        fd.sphere(mat, (x0, oy + 0.004, zz), 0.0105 - 0.0012 * k, seg=8, sq=(1, 0.5, 1.3), col=cc)
    # swag of carved beads at the top of the inner arch
    for k in range(5):
        a = math.pi * (k + 0.5) / 5
        fd.sphere(mat, (x0 + math.cos(a) * (pw / 2 - 0.012), 0.0215, ph + math.sin(a) * (arch_r * 0.55 - 0.012 * 0.6)), 0.0042, seg=6, rings=4, col=cc)
    # back skin of door (inside face)
    if inner:
        fd.box(mat, (X(dw / 2), -0.0155, dh / 2), (dw - 0.02, 0.004, dh - 0.02), bev=0.001, col=(0.75, 0.66, 0.58), g=2, skip_down=False)
    # hinges: three barrel hinges on the front edge
    for zz in (0.16, dh * 0.5, dh - 0.16):
        hinge_butt(fd, (X(0.0), 0.0165, zz), h=0.075, w=0.04, face=1, mat=M['brass'])
    # knob & lock plate at the free edge
    kx = X(dw - 0.038)
    if lock:
        escutcheon(fd, (kx, 0.0135, dh * 0.5 - 0.1), h=0.065, w=0.034, face=1)
    knob(fd, (kx, 0.0135, dh * 0.5 + 0.02), axis='y', r=0.022, sign=1)
    return fd


def cornice(f, W, D, H):
    mat = M['wood_dark']
    col = (1.0, 0.93, 0.87)
    zc = H - 0.2
    # frieze
    f.box(mat, (0, 0.0, zc + 0.03), (W + 0.02, D + 0.02, 0.06), bev=0.004, col=col, g=0)
    # ogee crown (profile in y,z extruded along x), front + both sides via three prisms (mitred roughly)
    prof = [(0.0, 0.0), (0.012, 0.0), (0.03, 0.012), (0.043, 0.03), (0.056, 0.048), (0.06, 0.07), (0.06, 0.08), (0.0, 0.08)]
    # front
    f.prism(mat, [(y_ + D / 2 + 0.0, z_ + zc + 0.06) for y_, z_ in prof], W + 0.02 + 0.12, plane='yz', col=col, g=0, skip_down=False)
    # sides
    for sx in (-1, 1):
        pass
    f.box(mat, (0, 0, H - 0.01), (W + 0.12, D + 0.12, 0.02), bev=0.004, col=col, g=0, skip_down=False)
    # side crown strips
    for sx in (-1, 1):
        f.prism(mat, [(y_ , z_ + zc + 0.06) for y_, z_ in [(0.0, 0.0), (0.012, 0.0), (0.03, 0.012), (0.043, 0.03), (0.056, 0.048), (0.06, 0.07), (0.06, 0.08), (0.0, 0.08)]], 0.001, c=(0, 0, 0), plane='yz') if False else None
        # drop strip on side
        pr = [(y_, z_) for y_, z_ in [(0.0, 0.0), (0.012, 0.0), (0.03, 0.012), (0.043, 0.03), (0.056, 0.048), (0.06, 0.07), (0.06, 0.08), (0.0, 0.08)]]
        # side profile lies in the x-direction depth; build as prism in xz-plane extruded along y
        f.prism(mat, [(sx * (W / 2 + 0.01 + dx), zc + 0.06 + z_) for dx, z_ in prof], D + 0.02 + 0.12, c=(0, 0, 0), plane='xz', col=col, g=1, skip_down=False)
    # dentils: ARRAY modifier of one small block along the frieze
    unit = bm_box(0.017, 0.016, 0.018)
    bev_bm(unit, 0.0015, 1)
    array_put(mat, unit, int((W + 0.0) / 0.034), (0.034, 0.0, 0.0), f._m((-W / 2 + 0.02, D / 2 + 0.014, zc + 0.062)), col=(0.95, 0.88, 0.8), g=2)
    unit.free()
    # central carved crest (pediment) with scrolls
    cx = 0.0
    zb = H
    crest = [(-0.2, 0.0), (-0.2, 0.018), (-0.12, 0.04), (-0.06, 0.075), (0.0, 0.1), (0.06, 0.075), (0.12, 0.04), (0.2, 0.018), (0.2, 0.0)]
    cp = [(a, zb + b) for a, b in catmull(crest, 3)] if False else [(a, zb + b) for a, b in crest]
    f.prism(mat, cp, 0.03, c=(0, D / 2 + 0.02, 0), plane='xz', col=col, bev=0.003, g=0)
    f.sphere(mat, (0, D / 2 + 0.038, zb + 0.045), 0.026, seg=14, sq=(1, 0.4, 1), col=(1.15, 1.05, 0.97))
    for s in (-1, 1):
        sp = spiral(s * 0.095, zb + 0.032, 0.026, 0.007, 1.1, math.pi * (0.2 if s > 0 else 0.8), 18, -s)
        f.tube(mat, [Vector((a_, D / 2 + 0.037, b_)) for a_, b_ in sp], 0.0045, seg=6, col=(1.12, 1.03, 0.95))
    # base of crest: finial urns at corners
    for sx in (-1, 1):
        f.lathe(mat, (sx * (W / 2 + 0.04), D / 2 + 0.03, H), profile_pts([(0.02, 0), (0.026, 0.01), (0.015, 0.022), (0.022, 0.036), (0.028, 0.05), (0.015, 0.068), (0.001, 0.078)], 3), seg=14, col=col, cap=False)


def wardrobe(pos, rot, W=1.18, D=0.56, H=2.08, build_clothes=True):
    f = Fr(pos, rot, F)
    mat = M['wood_dark']
    col = (1.0, 0.93, 0.86)
    colp = (0.8, 0.72, 0.64)
    # feet + plinth
    for sx in (-1, 1):
        for sy in (-1, 1):
            bracket_foot(f, sx * W / 2, sy * D / 2, mat, col, sx, sy)
    f.box(mat, (0, 0, 0.145), (W + 0.012, D + 0.012, 0.05), bev=0.006, col=col, g=0)
    f.box(mat, (0, 0.0, 0.185), (W + 0.036, D + 0.036, 0.03), bev=0.01, col=(1.05, 0.97, 0.9), g=0)
    # carcass: sides (fielded panels), back, top
    sidew = 0.024
    H0, H1 = 0.17, H - 0.26
    for sx in (-1, 1):
        f.box(mat, (sx * (W / 2 - sidew / 2), 0, (H0 + H1) / 2), (sidew, D, H1 - H0), bev=0.003, col=colp, g=2)
        fs = Fr(f.p((sx * (W / 2 - 0.0), 0, 0)), f.rot + (-90 if sx > 0 else 90), None)
        # side frame (outward = fs local +y)
        fs.box(mat, (0, 0.004, (H0 + H1) / 2), (D - 0.01, 0.01, H1 - H0), bev=0.002, col=col, g=2)
        for (cz, hh) in ((H0 + 0.37, 0.5), (H0 + 1.0, 0.9)):
            fielded_panel(fs, 0.0, cz, D - 0.15, hh, 0.006 + 0.004, 1, mat=mat, col=col)
    f.box(mat, (0, -D / 2 + 0.012, (H0 + H1) / 2), (W - 0.04, 0.02, H1 - H0), bev=0.002, col=(0.7, 0.62, 0.55), g=2)
    f.box(mat, (0, 0, H1 + 0.012), (W + 0.012, D + 0.012, 0.025), bev=0.004, col=col, g=0)
    f.box(mat, (0, 0, 0.19), (W - 0.04, D - 0.04, 0.02), bev=0.002, col=colp, g=0)
    # interior: divider, shelves, rod
    zbot_i, ztop_i = 0.40, H1 - 0.03
    f.box(mat, (0, -0.02, (zbot_i + ztop_i) / 2), (0.022, D - 0.06, ztop_i - zbot_i), bev=0.002, col=colp, g=2)
    f.box(mat, (0, 0, zbot_i - 0.01), (W - 0.05, D - 0.04, 0.02), bev=0.002, col=colp, g=0)
    f.box(mat, (-W / 4 + 0.01, -0.02, 1.35), (W / 2 - 0.06, D - 0.07, 0.02), bev=0.002, col=colp, g=0)
    f.box(mat, (W / 4 - 0.01, -0.02, 1.62), (W / 2 - 0.06, D - 0.07, 0.02), bev=0.002, col=colp, g=0)
    rodz = 1.52
    f.cyl(M['brass'], (W / 4 - 0.01, 0.0, rodz), 0.0075, W / 2 - 0.06, axis='x', seg=12)
    for sx in (0.011 + 0.0, W / 2 - 0.035):
        f.box(M['brass'], (sx if sx < 0.1 else sx, 0.0, rodz + 0.0), (0.006, 0.03, 0.03), bev=0.001) if False else None
    for x in (0.03, W / 2 - 0.035):
        f.cyl(M['brass'], (x, 0.0, rodz), 0.016, 0.01, axis='x', seg=12, bev=0.002)
    # drawer under the doors
    yf = D / 2
    f.box(mat, (0, yf - 0.012, 0.31), (W - 0.05, 0.026, 0.19), bev=0.004, col=col, g=0)
    f.box(mat, (0, yf + 0.003, 0.31), (W - 0.12, 0.012, 0.12), bev=0.004, col=(1.07, 1.0, 0.92), g=0)
    fielded_panel(f, 0, 0.31, W - 0.12, 0.12, yf + 0.0, 1, mat=mat, col=col) if False else None
    for sx in (-1, 1):
        drop_pull(f, (sx * 0.25, yf + 0.011, 0.31), face=1, w=0.075)
        escutcheon(f, (sx * 0.5, yf + 0.014, 0.31), h=0.04, w=0.022, face=1)
    # door stop frame (face frame) around the door opening
    f.box(mat, (0, yf - 0.008, zbot_i - 0.008), (W - 0.03, 0.03, 0.02), bev=0.003, col=col, g=0)
    # doors
    dw = (W - 0.05) / 2 - 0.004
    dh = (H - 0.26) - 0.40 - 0.02
    # viewer-left door (local +x side) ajar
    hinge_open = (W / 2 - 0.022, yf + 0.0, 0.41)
    hinge_closed = (-(W / 2 - 0.022), yf + 0.0, 0.41)
    door_leaf(f, hinge_open, +1, dw, dh, 34, mat, col, lock=False)
    door_leaf(f, hinge_closed, -1, dw, dh, 0, mat, col, lock=True)
    cornice(f, W, D, H)
    # clothes inside the open compartment
    if build_clothes:
        wardrobe_clothes(f, W, D, rodz)
    collider_f(f, W + 0.12, D + 0.1, F + H + 0.02, name='wardrobe')
    return f


def wardrobe_clothes(f, W, D, rodz):
    """hanging clothes (cloth sim) in the right-hand (local +x) compartment. garment shoulder lines along local y."""
    specs = [
        dict(name='wc_dress', x=0.12, hang=0.95, sh=0.16, hem=1.55, hb=0.06, col=(0.84, 0.8, 0.7), mat='linen', phase=0.2),
        dict(name='wc_shirt', x=0.205, hang=0.62, sh=0.17, hem=1.12, hb=0.055, col=(0.55, 0.62, 0.72), mat='linen', phase=0.6),
        dict(name='wc_coat', x=0.30, hang=1.0, sh=0.185, hem=1.22, hb=0.075, col=(0.36, 0.28, 0.2), mat='wool', phase=1.0),
        dict(name='wc_jacket', x=0.395, hang=0.72, sh=0.18, hem=1.12, hb=0.07, col=(0.3, 0.38, 0.3), mat='wool', phase=1.6),
        dict(name='wc_dress2', x=0.475, hang=0.88, sh=0.15, hem=1.45, hb=0.055, col=(0.62, 0.3, 0.28), mat='linen', phase=2.2),
    ]
    for sp in specs:
        # garment frame: origin at hanger hook, shoulder line along wardrobe-local y => rotate frame by 90 deg
        pos = f.p((sp['x'], 0.0, rodz - 0.0))
        fg = Fr(pos, f.rot + 90, pos.z)
        # body: body_sim builds with shoulders along x, front +y of the garment frame
        g = body_sim_flat(sp)
        G.put_garment(fg, g, M[sp['mat']], cfn=fab(sp['col'], 0.08, 14, hash(sp['name']) % 7))
        G.hanger(fg, (0, 0, 0.0), sh_w=sp['sh'] * 1.02)
        # sleeves hang beside the body at the shoulder ends
        sls = []
        for side in (-1, 1):
            sl = G.sleeve_sim(sp['name'] + ('_sl%d' % side), side, g['v'], g['f'], sh_w=sp['sh'] * 1.0, length=sp['hang'] * 0.55, r0=0.042, r1=0.032)
            G.put_garment(fg, sl, M[sp['mat']], cfn=fab(sp['col'], 0.08, 14, hash(sp['name']) % 7 + 3))
            sls.append(sl)
        G.details(fg, g, sls, M[sp['mat']], sp['col'], pockets=(sp['mat'] == 'wool'))
        G.buttons(fg, g, 4 if sp['mat'] == 'wool' else 5, x=0.0, z0=0.12, z1=sp['hang'] * 0.55, col=(0.15, 0.1, 0.07) if sp['mat'] == 'wool' else (0.92, 0.88, 0.78))
    # folded linens + hat box on the top shelf of the left compartment (seen through the closed door? not visible) -> on the right top shelf
    for k in range(4):
        cc = [(0.93, 0.9, 0.82), (0.6, 0.68, 0.76), (0.86, 0.8, 0.66), (0.93, 0.9, 0.82)][k]
        soft_box(M['linen'], f._m((W / 4 - 0.01, -0.05, 1.63 + 0.034 + k * 0.047)), (0.34 - 0.008 * k, 0.28, 0.046), col=cc, disp=0.003)


def body_sim_flat(sp):
    return G.body_sim(sp['name'], 'x', hang_h=sp['hang'], sh_w=sp['sh'], hem_scale=sp['hem'], phase=sp['phase'], amp=0.10, hb=sp['hb'])
