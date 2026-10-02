"""vh_parts: building components (walls, windows, doors, roofs, chimneys, props)."""
from vh_lib import *
import vh_lib

Z0 = 0.35          # plinth top / wall bottom
SZ0 = 0.30         # siding start (aligned to 0.15 m texture grooves)


def frames(W, D, cx=0.0, cy=0.0):
    return dict(
        F=Fr((cx, cy - D / 2, 0), (1, 0, 0), (0, -1, 0)),
        B=Fr((cx, cy + D / 2, 0), (-1, 0, 0), (0, 1, 0)),
        R=Fr((cx + W / 2, cy, 0), (0, 1, 0), (1, 0, 0)),
        L=Fr((cx - W / 2, cy, 0), (0, -1, 0), (-1, 0, 0)))


def win_hole(uc, zc, w, h): return (uc - w / 2, uc + w / 2, zc - h / 2, zc + h / 2)


# ------------------------------------------------------------------ foundation
PAL_STONE = [(c[0] * 1.3, c[1] * 1.28, c[2] * 1.22) for c in [(1, 1, 1), (0.88, 0.86, 0.8), (1.06, 1.0, 0.94), (0.78, 0.76, 0.72), (1.0, 0.93, 0.84), (0.93, 0.95, 0.92)]]


def plinth(W, D, ztop=Z0, zbot=-0.5, out=0.1, mat='stone_foundation', skip=(), hs=(0.2, 0.3), gaps=()):
    """stone plinth ring around the footprint (outer face of wall at +-W/2, +-D/2)."""
    box('mortar', -W / 2 - out + 0.04, W / 2 + out - 0.04, -D / 2 - out + 0.04, D / 2 + out - 0.04, zbot, ztop - 0.03)
    fr = frames(W, D)
    for key, ext in (('F', W / 2 + out + 0.02), ('B', W / 2 + out + 0.02), ('R', D / 2 + out - 0.1), ('L', D / 2 + out - 0.1)):
        if key in skip: continue
        masonry(fr[key], mat, -ext, ext, zbot + 0.05, ztop, -0.08, out, pal=PAL_STONE, hs=hs, ws=(0.4, 0.8), gap=0.016, m=1,
                k=0.6, noise=0.09, rough=0.02, holes=gaps if key == 'F' else ())
    # cap course (flat slabs, slightly proud)
    for key, ext in (('F', W / 2 + out), ('B', W / 2 + out), ('R', D / 2 + out), ('L', D / 2 + out)):
        if key in skip: continue


# ------------------------------------------------------------------ walls
def wall_cols(u0, u1, holes):
    pts = sorted({u0, u1} | {min(max(h[0], u0), u1) for h in holes} | {min(max(h[1], u0), u1) for h in holes})
    return [(a, b) for a, b in zip(pts[:-1], pts[1:]) if b - a > 1e-3]


def core(F, u0, u1, z0, z1, holes=(), mat='mortar', n0=-0.23, n1=-0.03, col=(1, 1, 1), sub=None, cj=0.0):
    for (a, b) in wall_cols(u0, u1, holes):
        for (c, d) in free_z(a, b, z0, z1, holes):
            F.box(mat, a, b, n0, n1, c, d, col=col, sub=sub, cj=cj)


def siding(F, u0, u1, z0, z1, holes=(), rangefn=None, mat='siding_wood', pitch=0.15, h=0.165, tcol=(1, 1, 1)):
    nrows = int((z1 - z0 - 0.02) / pitch) + 1
    for r in range(nrows):
        zb = z0 + r * pitch
        zt = min(zb + h, z1)
        if zt - zb < 0.04: break
        a, b = rangefn(zb, zt) if rangefn else (u0, u1)
        if b - a < 0.05: continue
        for (p, q) in free_intervals(a, b, zb, zt, holes):
            u = p
            for w in split_widths(q - p, 1.1, 2.4):
                pts = [(-0.03, zb), (0.0, zb), (0.0, zb + 0.012), (-0.022, zt), (-0.03, zt)]
                c = tint(tcol[0], tcol[1], tcol[2], 0.14)
                F.prism(mat, pts, u, u + w - 0.0025, col=c, cj=0.05, caps=(False, False))
                u += w


def vboards(F, u0, u1, z0, z1, holes=(), topfn=None, mat='siding_dark', bw=0.2, batten=True, tcol=(1, 1, 1), n0=-0.04):
    u = u0
    while u < u1 - 0.02:
        w = min(bw, u1 - u)
        ua, ub = u + 0.003, u + w - 0.003
        zt = min(z1, topfn((ua + ub) / 2)) if topfn else z1
        for (c, d) in free_z(ua, ub, z0, zt, holes):
            col = tint(tcol[0], tcol[1], tcol[2], 0.14)
            F.box(mat, ua, ub, n0, 0.0, c, d, col=col, cj=0.05, n=(1, 1, max(1, int((d - c) / 1.2))), skip=('bottom',))
            if batten and w > bw * 0.9:
                F.box(mat, ub - 0.026, ub + 0.026, 0.0, 0.016, c, d, col=tint(tcol[0] * 0.92, tcol[1] * 0.92, tcol[2] * 0.92, 0.1), skip=('bottom',))
        u += w


def plaster_wall(F, u0, u1, z0, z1, holes=(), col=(1, 1, 1), sub=0.6, rangefn=None, topfn=None):
    for (a, b) in wall_cols(u0, u1, holes):
        for (c, d) in free_z(a, b, z0, z1, holes):
            F.box('plaster', a, b, -0.2, 0.0, c, d, sub=sub, cj=0.05, freq=1.3, col=col)


def stone_wall(F, u0, u1, z0, z1, holes=(), mat='stone_wall', rangefn=None, pal=None, hs=(0.2, 0.3), ws=(0.3, 0.62), thick=0.24, dk=1.0):
    core(F, u0, u1, z0, z1, holes, 'mortar', -thick, -0.06, col=(0.9, 0.9, 0.9))
    masonry(F, mat, u0, u1, z0, z1, -0.14, 0.02, holes=holes, hs=hs, ws=ws, pal=pal or PAL_STONE, gap=0.016, m=1, k=0.6, noise=0.08,
            rough=0.025, rangefn=rangefn, dk=dk)


def halftimber(F, u0, u1, z0, z1, holes=(), spacing=1.6, rails=(), braces=True, post_w=0.12, mat='timber_dark', rangefn=None, depth=0.045, jit=True, topfn=None):
    """timber frame overlay on a plaster wall (proud by depth). rails: list of z (centres)."""
    zs = [z0 + 0.0] + ([z1] if not topfn else []) + list(rails)
    if topfn:
        kest = topfn(0.0) - topfn(1.0)
    for zr in sorted(set(zs)):
        rh = 0.14
        zc0 = max(z0, zr - rh / 2) if zr > z0 else z0
        zc1 = min(z1, zr + rh / 2) if zr < z1 else z1
        a, b = rangefn(zc0, zc1) if rangefn else (u0, u1)
        if topfn:
            lim = (topfn(0.0) - zc1) / kest
            a, b = max(a, -lim), min(b, lim)
        for (p, q) in free_intervals(a, b, zc0, zc1, holes):
            F.box(mat, p, q, -0.02, depth, zc0, zc1, n=(max(1, int((q - p) / 1.0)), 1, 1), cj=0.1, freq=1.3, seed=zr * 3)
    nposts = max(1, int(round((u1 - u0) / spacing)))
    us = [u0 + (u1 - u0) * i / nposts for i in range(nposts + 1)]
    for u in us:
        a, b = u - post_w / 2, u + post_w / 2
        a = max(a, u0); b = min(b, u1)
        for (c, d) in free_z(a, b, z0, z1, holes):
            top = d
            if topfn:
                top = min(d, topfn(u))
                if top - c < 0.1: continue
            elif rangefn:
                ra, rb = rangefn(c, d)
                if u < ra - 0.02 or u > rb + 0.02: continue
            F.box(mat, a, b, -0.02, depth, c, top, n=(1, 1, max(1, int((d - c) / 1.0))), cj=0.1, freq=1.1, seed=u * 5)
    if braces:
        for i in range(nposts):
            ua, ub = us[i] + post_w / 2, us[i + 1] - post_w / 2
            zb0, zb1 = z0 + 0.07, z1 - 0.07
            # one diagonal per bay (alternating), skipped if it hits an opening
            hit = False
            for (a, b, c, d) in holes:
                if b > ua and a < ub and d > zb0 and c < zb1:
                    hit = True
            if rangefn:
                ra, rb = rangefn(z0, z1)
                if ua < ra or ub > rb: hit = True
            if hit: continue
            pa = F.P(ua, -0.02, zb0 if i % 2 == 0 else zb1)
            pb = F.P(ub, -0.02, zb1 if i % 2 == 0 else zb0)
            dv = pb - pa
            L = dv.length
            perp = dv.cross(F.N).normalized()
            obox(mat, pa - perp * 0.055, dv, F.N, perp, L, depth + 0.02, 0.11, cj=0.1)


def corner_posts(W, D, z0, z1, mat='paint_trim', sz=0.17, proud=0.03):
    for sx in (-1, 1):
        for sy in (-1, 1):
            x0, x1 = (W / 2 - sz + proud, W / 2 + proud) if sx > 0 else (-W / 2 - proud, -W / 2 + sz - proud)
            y0, y1 = (D / 2 - sz + proud, D / 2 + proud) if sy > 0 else (-D / 2 - proud, -D / 2 + sz - proud)
            box(mat, x0, x1, y0, y1, z0, z1, n=(1, 1, max(1, int((z1 - z0) / 1.0))), cj=0.04)


def quoins(W, D, z0, z1, mat='stone_wall', sz=0.46, th=0.27, out=0.025):
    """alternating corner blocks."""
    for sx in (-1, 1):
        for sy in (-1, 1):
            z = z0
            i = 0
            while z < z1 - 0.05:
                h = rng.uniform(0.22, 0.3)
                h = min(h, z1 - z)
                long_x = (i % 2 == 0)
                lx, ly = (sz, th) if long_x else (th, sz)
                cx = sx * (W / 2 - lx / 2 + out)
                cy = sy * (D / 2 - ly / 2 + out)
                rbox(mat, (cx, cy, z + h / 2), (lx - 0.015, ly - 0.015, h - 0.014), col=rng.choice(PAL_STONE), m=1, k=0.6, noise=0.05)
                z += h; i += 1


def tri_core(F, half, z0, z1, holes=(), mat='mortar', n0=-0.2, n1=-0.03, step=0.25, col=(1, 1, 1)):
    """solid triangle core built from horizontal bands (so holes can be cut)."""
    K = (z1 - z0) / half
    z = z0
    while z < z1 - 0.01:
        zt = min(z + step, z1)
        hw = (z1 - zt) / K    # width at band top (never pokes through the roof)
        for (a, b) in free_intervals(-hw, hw, z, zt, holes):
            F.box(mat, a, b, n0, n1, z, zt, col=col)
        z = zt


def gable_fill(F, half, z0, z1, style='lap', holes=(), mat=None, col=(1, 1, 1), n_out=0.0):
    """triangle from z0 (width +-half) to z1 apex, on frame F centred on u=0."""
    K = (z1 - z0) / half

    def hw(zb, zt):
        z = (zb + zt) / 2
        return -((z1 - z) / K - 0.02), ((z1 - z) / K - 0.02)

    if style == 'lap':
        tri_core(F, half, z0, z1, holes)
        siding(F, -half, half, z0, z1 - 0.02, holes, rangefn=hw, mat=mat or 'siding_wood', tcol=col)
    elif style == 'board':
        tri_core(F, half, z0, z1, holes)
        vboards(F, -half + 0.02, half - 0.02, z0, z1, holes, topfn=lambda u: z1 - K * abs(u) - 0.03, mat=mat or 'siding_dark', tcol=col)
    elif style == 'plaster':
        tri_core(F, half, z0, z1, holes, mat='plaster', n0=-0.2, n1=0.0, step=0.4, col=col)
    elif style == 'stone':
        tri_core(F, half, z0, z1, holes, n0=-0.24, n1=-0.06)
        masonry(F, mat or 'stone_wall', -half, half, z0, z1, -0.14, 0.02, holes=holes, hs=(0.2, 0.3), ws=(0.3, 0.6), pal=PAL_STONE, gap=0.016, m=1, k=0.6,
                rangefn=hw)


# ------------------------------------------------------------------ windows
def casing(F, a, b, zb, zt, wd=0.085, th=0.022, mat='paint_trim'):
    F.box(mat, a - wd, a, 0, th, zb, zt)
    F.box(mat, b, b + wd, 0, th, zb, zt)
    F.box(mat, a - wd, b + wd, 0, th, zt, zt + wd)
    F.box(mat, a - wd - 0.02, b + wd + 0.02, 0, th + 0.012, zt + wd, zt + wd + 0.025)


def window(F, uc, zc, w, h, rows=3, cols=1, shutters=True, flowerbox=False, casing_w=0.09, sill=True, glow=True,
           shutter_mat='paint_shutter', register=True, shutter_closed=False, lintel=None):
    a, b = uc - w / 2, uc + w / 2
    c, d = zc - h / 2, zc + h / 2
    ia, ib, ic, id_ = a + 0.02, b - 0.02, c + 0.02, d - 0.02
    n0, n1 = -0.17, -0.12
    T = 'paint_trim'
    # reveal lining
    F.box(T, a, a + 0.02, -0.19, 0.0, c, d)
    F.box(T, b - 0.02, b, -0.19, 0.0, c, d)
    F.box(T, a + 0.02, b - 0.02, -0.19, 0.0, d - 0.02, d)
    F.box(T, a + 0.02, b - 0.02, -0.19, 0.0, c, c + 0.02)
    # frame + casements
    ncase = 2 if w > 0.75 else 1
    edges = [ia + (ib - ia) * i / ncase for i in range(ncase + 1)]
    for k in range(ncase):
        sa, sb = edges[k], edges[k + 1]
        st = 0.04
        F.box(T, sa, sa + st, n0, n1, ic, id_)
        F.box(T, sb - st, sb, n0, n1, ic, id_)
        F.box(T, sa + st, sb - st, n0, n1, ic, ic + 0.05)
        F.box(T, sa + st, sb - st, n0, n1, id_ - 0.045, id_)
        # glazing bars
        for j in range(1, cols + 1):
            uu = sa + (sb - sa) * j / (cols + 1)
            F.box(T, uu - 0.009, uu + 0.009, n0 + 0.012, n1 - 0.012, ic, id_)
    for j in range(1, rows):
        zz = ic + (id_ - ic) * j / rows
        F.box(T, ia, ib, n0 + 0.012, n1 - 0.012, zz - 0.009, zz + 0.009)
    # sash handle
    # glass + glow
    F.box('glass', ia + 0.035, ib - 0.035, -0.153, -0.147, ic + 0.035, id_ - 0.035)
    if glow:
        F.box('window_glow', a + 0.02, b - 0.02, -0.19, -0.178, c + 0.02, d - 0.02)
    # exterior casing, drip cap, sill, apron
    cw = casing_w
    casing(F, a, b, c, d, wd=cw, th=0.024)
    if sill:
        F.prism(T, [(-0.03, c - 0.05), (0.11, c - 0.05), (0.11, c - 0.035), (0.0, c + 0.005), (-0.03, c + 0.005)], a - 0.08, b + 0.08)
    if lintel:
        F.box(lintel, a - cw - 0.1, b + cw + 0.1, -0.02, 0.07, d + cw + 0.03, d + cw + 0.2, cj=0.1)
    if shutters:
        sw = (b - a) / 2 - 0.0
        sw = min(0.58, max(0.3, sw))
        zz0, zz1 = c - 0.03, d + 0.03
        if shutter_closed:
            shutter_leaf(F, a - 0.0, +1, zz0, zz1, (b - a) / 2, shutter_mat)
            shutter_leaf(F, b + 0.0, -1, zz0, zz1, (b - a) / 2, shutter_mat)
        else:
            shutter_leaf(F, a - cw - 0.01, -1, zz0, zz1, sw, shutter_mat)
            shutter_leaf(F, b + cw + 0.01, +1, zz0, zz1, sw, shutter_mat)
    if flowerbox:
        flower_box(F, uc, c, min(w + 0.2, 1.3))
    if register:
        reg_window(F, uc, zc)


def shutter_leaf(F, hinge_u, dirn, z0, z1, wid, mat='paint_shutter'):
    ua, ub = sorted((hinge_u, hinge_u + dirn * wid))
    zm = (z0 + z1) / 2
    st = 0.06
    P = mat
    F.box(P, ua, ua + st, 0.0, 0.028, z0, z1)
    F.box(P, ub - st, ub, 0.0, 0.028, z0, z1)
    F.box(P, ua + st, ub - st, 0.0, 0.028, z0, z0 + 0.08)
    F.box(P, ua + st, ub - st, 0.0, 0.028, z1 - 0.08, z1)
    F.box(P, ua + st, ub - st, 0.0, 0.028, zm - 0.035, zm + 0.035)
    for (f0, f1) in ((z0 + 0.08, zm - 0.035), (zm + 0.035, z1 - 0.08)):
        nL = max(2, int((f1 - f0) / 0.07))
        for i in range(nL):
            zb = f0 + i * (f1 - f0) / nL
            F.prism(P, [(0.004, zb), (0.026, zb + 0.035), (0.026, zb + 0.05)], ua + st - 0.003, ub - st + 0.003,
                    col=tint(1, 1, 1, 0.05), caps=(False, False))
    he = hinge_u
    for zz in (z0 + 0.18, z1 - 0.18):
        uu0, uu1 = (he, he + dirn * 0.28)
        F.box('iron', min(uu0, uu1), max(uu0, uu1), 0.028, 0.034, zz - 0.02, zz + 0.02)


def plant_cluster(cx, cy, z, wdt, dpt, nflow=12, flowcols=None, leaf=0.06, nleaf=8, trail=None):
    flowcols = flowcols or [(0.9, 0.12, 0.1), (0.95, 0.35, 0.45), (0.98, 0.95, 0.9)]
    for i in range(nleaf):
        p = (cx + rng.uniform(-wdt / 2, wdt / 2), cy + rng.uniform(-dpt / 2, dpt / 2), z + leaf * rng.uniform(0.5, 1.2))
        blob('foliage', p, leaf * rng.uniform(0.8, 1.3), col=tint(0.8, 1.0, 0.75, 0.25), rows=2, segs=5, squash=0.75)
    fc = rng.choice(flowcols)
    for i in range(nflow):
        if rng.random() < 0.3: fc = rng.choice(flowcols)
        p = (cx + rng.uniform(-wdt / 2, wdt / 2), cy + rng.uniform(-dpt / 2, dpt / 2), z + leaf * rng.uniform(1.4, 2.2))
        blob('flowers', p, leaf * rng.uniform(0.38, 0.55), col=tint(fc[0], fc[1], fc[2], 0.12), rows=2, segs=5, squash=0.8, jit=0.1)


def flower_box(F, uc, c, wb=1.12, flowcols=None):
    z1 = c - 0.15; z0 = z1 - 0.22
    u0, u1 = uc - wb / 2, uc + wb / 2
    n0, n1 = 0.035, 0.26
    P = 'paint_shutter'
    F.box(P, u0, u1, n1 - 0.02, n1, z0, z1, cj=0.03)
    F.box(P, u0, u1, n0, n0 + 0.02, z0, z1)
    F.box(P, u0, u0 + 0.02, n0, n1, z0, z1)
    F.box(P, u1 - 0.02, u1, n0, n1, z0, z1)
    F.box(P, u0, u1, n0, n1, z0, z0 + 0.02)
    F.box('soil', u0 + 0.02, u1 - 0.02, n0 + 0.02, n1 - 0.02, z0 + 0.02, z1 - 0.04, col=(0.8, 0.8, 0.8), cj=0.15, skip=('bottom',))
    for su in (-0.4 * wb, 0.4 * wb):
        F.prism('iron', [(0.0, z0 - 0.16), (0.0, z0), (0.235, z0)], uc + su - 0.012, uc + su + 0.012)
    # plants (placed in world space)
    p = F.P(uc, (n0 + n1) / 2, z1 - 0.04)
    nflow = int(wb * 9)
    fc = flowcols or [(0.9, 0.12, 0.1), (0.95, 0.35, 0.45), (0.98, 0.95, 0.9)]
    for i in range(nflow // 3 + 2):
        t = rng.uniform(-wb / 2 + 0.06, wb / 2 - 0.06)
        q = F.P(uc + t, rng.uniform(n0 + 0.05, n1 - 0.05), z1 + rng.uniform(0.0, 0.05))
        blob('foliage', q, rng.uniform(0.05, 0.08), col=tint(0.8, 1.0, 0.75, 0.25), rows=2, segs=5, squash=0.8)
    for i in range(nflow):
        t = rng.uniform(-wb / 2 + 0.05, wb / 2 - 0.05)
        q = F.P(uc + t, rng.uniform(n0 + 0.04, n1 - 0.04), z1 + rng.uniform(0.07, 0.13))
        cc = rng.choice(fc)
        blob('flowers', q, rng.uniform(0.025, 0.04), col=tint(cc[0], cc[1], cc[2], 0.1), rows=2, segs=5, squash=0.8, jit=0.1)
    for i in range(2):   # trailing leaves over front
        t = rng.uniform(-wb / 2 + 0.1, wb / 2 - 0.1)
        q = F.P(uc + t, n1 + 0.02, z1 - rng.uniform(0.02, 0.1))
        blob('foliage', q, 0.04, col=tint(0.8, 1.0, 0.75, 0.2), rows=2, segs=5, squash=1.5)


# ------------------------------------------------------------------ doors
def door(F, uc, w, h, mat='paint_door', z0=Z0, style='ledged', frame_mat='paint_trim', lintel=None, hardware=True, glazed=False,
         step=True, reveal=True):
    ua, ub = uc - w / 2, uc + w / 2
    z1 = z0 + h
    nb0, nb1 = -0.165, -0.115
    T = frame_mat
    if reveal:
        F.box('timber_dark', ua, ua + 0.03, -0.2, 0.0, z0, z1)
        F.box('timber_dark', ub - 0.03, ub, -0.2, 0.0, z0, z1)
        F.box('timber_dark', ua, ub, -0.2, 0.0, z1 - 0.03, z1)
    # planks
    npl = max(3, int(round(w / 0.13)))
    pw = w / npl
    for i in range(npl):
        pa = ua + 0.03 + (w - 0.06) * i / npl
        pb = pa + (w - 0.06) / npl - 0.003
        c = tint(1, 1, 1, 0.07)
        if glazed and 1 <= i <= npl - 2:
            F.box(mat, pa, pb, nb0, nb1, z0 + 0.02, z0 + h * 0.52, col=c, cj=0.04, n=(1, 1, 3))
            F.box(mat, pa, pb, nb0, nb1, z0 + h * 0.84, z1 - 0.03, col=c, cj=0.04)
        else:
            F.box(mat, pa, pb, nb0, nb1, z0 + 0.02, z1 - 0.03, col=c, cj=0.04, n=(1, 1, 5))
    if glazed:
        gu0, gu1 = ua + 0.03 + (w - 0.06) / npl, ub - 0.03 - (w - 0.06) / npl
        gz0, gz1 = z0 + h * 0.52, z0 + h * 0.84
        for (a0, a1, b0, b1) in ((gu0 - 0.03, gu0, gz0 - 0.03, gz1 + 0.03), (gu1, gu1 + 0.03, gz0 - 0.03, gz1 + 0.03),
                                 (gu0, gu1, gz0 - 0.03, gz0), (gu0, gu1, gz1, gz1 + 0.03)):
            F.box('door_wood', a0, a1, -0.175, -0.105, b0, b1)
        F.box('door_wood', (gu0 + gu1) / 2 - 0.006, (gu0 + gu1) / 2 + 0.006, -0.15, -0.13, gz0, gz1)
        F.box('glass', gu0, gu1, -0.143, -0.137, gz0, gz1)
        F.box('window_glow', gu0, gu1, -0.125, -0.115, gz0, gz1)
    # inside ledges + brace
    for zz in (z0 + 0.25, z1 - 0.3):
        F.box('door_wood', ua + 0.03, ub - 0.03, -0.197, -0.165, zz, zz + 0.13)
    a = F.P(ua + 0.06, -0.197, z0 + 0.3); bpt = F.P(ub - 0.06, -0.197, z1 - 0.25)
    dv = bpt - a
    perp = dv.cross(F.N).normalized()
    obox('door_wood', a - perp * 0.05, dv, F.N, perp, dv.length, 0.036, 0.10)
    # frame: casing + lintel + threshold
    casing(F, ua, ub, z0, z1, wd=0.1, th=0.026, mat=T)
    if lintel:
        F.box(lintel, ua - 0.2, ub + 0.2, -0.02, 0.1, z1 + 0.12, z1 + 0.34, cj=0.1)
    if hardware:
        # long strap hinges (tapered)
        for zz in (z0 + 0.3, z1 - 0.32):
            F.prism('iron', [(nb1, zz - 0.03), (nb1 + 0.01, zz - 0.026), (nb1 + 0.01, zz + 0.026), (nb1, zz + 0.03)], ua + 0.02, ua + 0.02 + w * 0.5,
                    caps=(False, True), s1=1.0)
            F.box('iron', ua + 0.02 + w * 0.5, ua + 0.02 + w * 0.5 + 0.04, nb1, nb1 + 0.008, zz - 0.015, zz + 0.015)
            cyl('iron', F.P(ua + 0.035, -0.13, zz - 0.06), F.P(ua + 0.035, -0.13, zz + 0.06), 0.012, segs=6)
            for k in range(3):
                nailhead('iron', *F.P(ua + 0.1 + k * w * 0.15, nb1 + 0.01, zz), s=0.016) if False else None
        # latch plate + ring handle
        hz = z0 + h * 0.46
        hu = ub - 0.14
        F.box('iron', hu - 0.045, hu + 0.045, nb1, nb1 + 0.01, hz - 0.1, hz + 0.1)
        ring(F, hu, nb1 + 0.012, hz, 0.045, 0.007)
        F.box('iron', hu - 0.07, hu + 0.07, nb1 + 0.01, nb1 + 0.024, hz + 0.1, hz + 0.115)
    if step:
        for k, (dn, hh, ww) in enumerate(((0.38, 0.17, 0.0), (0.74, 0.0, 0.2))):
            pass
        door_step(F, uc, w + 0.5, 0.45, Z0 - 0.17, mat='stone_foundation')


def door_step(F, uc, w, depth, ztop, mat='stone_foundation', two=True):
    # slab step
    c = F.P(uc, depth / 2 + 0.01, ztop - 0.12)
    sx = abs(F.U.x) * w + abs(F.N.x) * depth
    sy = abs(F.U.y) * w + abs(F.N.y) * depth
    rbox(mat, c, (sx, sy, 0.26), col=(1.02, 1.0, 0.95), m=1, k=0.6, noise=0.03)
    if two:
        c2 = F.P(uc, depth + 0.2, ztop - 0.27)
        sx = abs(F.U.x) * (w - 0.3) + abs(F.N.x) * 0.42
        sy = abs(F.U.y) * (w - 0.3) + abs(F.N.y) * 0.42
        rbox(mat, c2, (sx, sy, 0.3), col=(0.95, 0.93, 0.88), m=1, k=0.6, noise=0.03)


def ring(F, u, n, z, R, r, mat='iron', segs=10):
    pts = [F.P(u + R * math.cos(2 * math.pi * i / segs), n, z + R * math.sin(2 * math.pi * i / segs)) for i in range(segs)]
    tube(mat, pts, r, segs=5, closed=True, pn=F.N)


def tube(mat, pts, r, segs=6, closed=False, pn=(0, -1, 0), col=(1, 1, 1), cj=0.0, caps=True):
    """tube along a polyline lying (roughly) in a plane with normal pn."""
    bm = B(mat); setbm(bm)
    P = [V3(p) for p in pts]
    n = len(P)
    pn = V3(pn).normalized()
    rings = []
    for i in range(n):
        if closed:
            T = (P[(i + 1) % n] - P[i - 1])
        else:
            T = (P[min(i + 1, n - 1)] - P[max(i - 1, 0)])
        T.normalize()
        a = pn.cross(T)
        if a.length < 1e-4: a = V3((1, 0, 0))
        a.normalize()
        bq = T.cross(a).normalized()
        rings.append([bm.verts.new(P[i] + (a * math.cos(2 * math.pi * k / segs) + bq * math.sin(2 * math.pi * k / segs)) * r) for k in range(segs)])
    fs = []
    cen = sum(P, V3()) / n
    last = n if closed else n - 1
    for i in range(last):
        j = (i + 1) % n
        cc = (P[i] + P[j]) / 2
        for k in range(segs):
            k2 = (k + 1) % segs
            f = bm.faces.new([rings[i][k], rings[i][k2], rings[j][k2], rings[j][k]])
            f.normal_update()
            mid = f.calc_center_median()
            if f.normal.dot(mid - cc) < 0: f.normal_flip()
            fs.append(f)
    if not closed and caps:
        for ring_, e in ((rings[0], P[0]), (rings[-1], P[-1])):
            f = bm.faces.new(ring_)
            f.normal_update()
            if f.normal.dot(f.calc_center_median() - cen) < 0: f.normal_flip()
            fs.append(f)
    paint(fs, col, cj)


# ------------------------------------------------------------------ roofs
def shingles(E, ex, d, nn, slen, wfn, exp=0.14, Ls=0.34, wr=(0.17, 0.3), mat='roof_shingle', tilt=0.0, colk=1.0, full=False):
    """courses of overlapping shingles: one tilted top quad per shingle + one front-edge strip per course."""
    p = -0.045
    E = V3(E); ex = V3(ex); d = V3(d); nn = V3(nn)
    bm = B(mat); setbm(bm)
    cl = bm.loops.layers.float_color['Col']
    while p < slen - 0.04:
        xa, xb = wfn(p)
        xa2, xb2 = wfn(min(p + Ls, slen))
        xa = max(xa, xa2); xb = min(xb, xb2)
        x = xa - rng.uniform(0.0, wr[1])
        rowk = rng.uniform(0.95, 1.05) * colk
        b0 = 0.004
        tb = 0.027

        def Pt(xx, pp, off): return E + ex * xx + d * pp + nn * off

        # front-edge strip of this course
        if xb - xa > 0.05:
            q = [Pt(xa, p, b0), Pt(xb, p, b0), Pt(xb, p, b0 + tb), Pt(xa, p, b0 + tb)]
            vs = [bm.verts.new(v) for v in q]
            f = addface(bm, vs, (q[0] + q[2]) / 2 + d * 0.1)
            kk = rowk * 0.55
            for l in f.loops:
                l[cl] = (kk * 0.95, kk * 0.9, kk * 0.85, 1.0)
        while x < xb:
            w = rng.uniform(*wr)
            x0 = max(x, xa); x1 = min(x + w - 0.006, xb)
            x += w
            if x1 - x0 < 0.04: continue
            pj = p + rng.uniform(-0.007, 0.007)
            p1 = min(pj + Ls, slen + 0.05)
            th = 0.004
            q = [Pt(x0, pj, b0 + tb), Pt(x1, pj, b0 + tb), Pt(x1, p1, b0 + th), Pt(x0, p1, b0 + th)]
            vs = [bm.verts.new(v) for v in q]
            f = addface(bm, vs, (q[0] + q[2]) / 2 - nn * 0.1)
            k = rowk * (1 + rng.uniform(-0.18, 0.18))
            c = (k * rng.uniform(0.92, 1.06), k * rng.uniform(0.9, 1.04), k * rng.uniform(0.85, 1.05))
            for l in f.loops:
                t = (l.vert.co - (E + ex * x0 + d * pj)).dot(d) / max(Ls, 1e-3)
                g = 1.0 - 0.28 * max(0.0, min(1.0, t))
                l[cl] = (c[0] * g, c[1] * g, c[2] * g, 1.0)
        p += exp


def roof_plane(xa, xb, lo, hi, exp=0.14, Ls=0.34, wr=(0.17, 0.3), mat='roof_shingle', deck_t=0.1, fascia=True, barge=(True, True),
               rafters=True, wfn=None, colk=1.0, rafter_sp=0.6, rafter_from=None, soffit=False):
    """one roof plane extruded along x. lo/hi: (y,z) of the surface at low (eave tip) and high edge."""
    ylo, zlo = lo; yhi, zhi = hi
    dy, dz = yhi - ylo, zhi - zlo
    L = math.hypot(dy, dz)
    d = V3((0, dy / L, dz / L))
    sg = 1.0 if dy > 0 else -1.0
    nn = V3((0, -dz / L * sg, dy / L * sg))
    if nn.z < 0: nn = -nn
    E = V3((0, ylo, zlo))
    # deck slab
    pts = [(ylo - nn.y * deck_t, zlo - nn.z * deck_t), (yhi - nn.y * deck_t, zhi - nn.z * deck_t), (yhi, zhi), (ylo, zlo)]
    prism(mat='roof_deck', pts=pts, O=(xa, 0, 0), A=V3((0, 1, 0)), Bv=V3((0, 0, 1)), U=V3((1, 0, 0)), L=xb - xa, col=(0.8, 0.8, 0.8))
    wf = wfn or (lambda p: (xa, xb))
    shingles(E + V3((0, 0, 0)), V3((1, 0, 0)), d, nn, L, wf, exp=exp, Ls=Ls, wr=wr, mat=mat, colk=colk)
    if fascia:
        obox('paint_trim', E + d * (-0.03) + nn * (-0.16) + V3((xa - 0.03, 0, 0)), V3((1, 0, 0)), d, nn, xb - xa + 0.06, 0.03, 0.23)
    for i, x in enumerate((xa - 0.03, xb)):
        if barge[i]:
            obox('paint_trim', E + d * (-0.03) + nn * (-0.15) + V3((x, 0, 0)), V3((1, 0, 0)), d, nn, 0.03, L + 0.03, 0.2)
    if rafters:
        x = (rafter_from if rafter_from is not None else xa + 0.4)
        while x < xb - 0.3:
            obox('timber_dark', E + nn * (-0.225) + V3((x - 0.04, 0, 0)), V3((1, 0, 0)), d, nn, 0.08, 0.55 * 1.0, 0.12, cj=0.06)
            x += rafter_sp
    return L, d, nn


def gable_roof(xa, xb, ye, ze, K, oy=0.5, exp=0.14, Ls=0.34, wr=(0.17, 0.3), mat='roof_shingle', sides=(-1, 1), gutters=(),
               rafters=True, colk=1.0, ridge=True, rafter_sp=0.6, barge=True, ridge_col=(1, 1, 1), gaps=()):
    """ridge along x; wall plane |y|=ye with top plate at ze. returns (zridge, zs fn)."""
    zr = ze + K * ye + 0.14
    zs = lambda y: zr - K * abs(y)
    yo = ye + oy
    for s in sides:
        roof_plane(xa, xb, (s * yo, zs(yo)), (0, zr), exp=exp, Ls=Ls, wr=wr, mat=mat, colk=colk, rafters=rafters, rafter_sp=rafter_sp,
                   barge=(barge, barge))
    if ridge:
        w = 0.28
        zl = zr - K * w
        prism('timber_beam', [(-w, zl), (w, zl), (w, zl + 0.045), (0, zr + 0.07), (-w, zl + 0.045)], (xa - 0.02, 0, 0), V3((0, 1, 0)), V3((0, 0, 1)), V3((1, 0, 0)),
              xb - xa + 0.04, col=ridge_col, cj=0.1)
    for s in gutters:
        segs_ = [(xa + 0.1, xb - 0.1)]
        for (ga, gb) in (gaps if s < 0 else ()):
            nsg = []
            for (p0, p1) in segs_:
                if gb <= p0 or ga >= p1: nsg.append((p0, p1)); continue
                if ga > p0: nsg.append((p0, ga))
                if gb < p1: nsg.append((gb, p1))
            segs_ = nsg
        for (p0, p1) in segs_:
            gutter(p0, p1, s * (yo + 0.03), zs(yo), K, s)
    return zr, zs


def gutter(xa, xb, y, zeave, K, s, r=0.065):
    """half-round zinc gutter at eave tip (y absolute, s = side sign)."""
    ca = 1 / math.sqrt(1 + K * K)
    semi = [(r * math.cos(t), r * math.sin(t)) for t in [math.pi + math.pi * i / 10 for i in range(11)]]
    cy = y + s * (r * 0.9)
    cz = zeave - 0.09
    pts = [(cy + s * a, cz + b) for (a, b) in semi]
    prism('zinc', pts, (xa, 0, 0), V3((0, 1, 0)), V3((0, 0, 1)), V3((1, 0, 0)), xb - xa)
    x = xa + 0.3
    while x < xb:
        prism('iron', [(cy + s * a * 1.1, cz + b * 1.1 - 0.004) for (a, b) in semi], (x - 0.012, 0, 0), V3((0, 1, 0)), V3((0, 0, 1)), V3((1, 0, 0)), 0.024)
        x += 0.9


def downspout(x, yg, zg, yw, s=1, r=0.036):
    """yg: y of the gutter, zg: gutter bottom, yw: y of the wall-side pipe, s: side sign."""
    ztop = zg - 0.02
    zk = ztop - abs(yg - yw) * 1.2
    cyl('zinc', (x, yg, ztop + 0.05), (x, yg, ztop - 0.04), 0.06, segs=10, s1=0.7)
    cyl('zinc', (x, yg, ztop - 0.04), (x, yw, zk), r, segs=10)
    cyl('zinc', (x, yw, zk), (x, yw, 0.5), r, segs=10)
    cyl('zinc', (x, yw, 0.5), (x, yw + s * 0.18, 0.3), r, segs=10)
    for zz in (zk - 0.3, (zk + 0.5) / 2, 0.8):
        box('iron', x - 0.02, x + 0.02, yw - 0.045 * s - 0.0, yw + 0.045 * s, zz, zz + 0.03)
    rbox('stone_foundation', (x, yw + s * 0.42, 0.0), (0.46, 0.5, 0.12), m=1, k=0.6, col=(0.9, 0.9, 0.85))


def hip_cap(p0, p1, w=0.1, mat='timber_dark'):
    p0 = V3(p0); p1 = V3(p1)
    cyl(mat, p0, p1, w * 0.6, segs=5, caps=(True, True))


def pyramid_roof(cx, cy, half_x, half_y, zb, zt, exp=0.15, Ls=0.34, wr=(0.17, 0.3), mat='roof_shingle', colk=1.0, overhang=0.0, deck_t=0.07):
    """4-sided pyramid (square-ish); base at zb on rectangle half_x/half_y, apex zt."""
    apex = V3((cx, cy, zt))
    for k in range(4):
        rot = k * math.pi / 2
        hxk, hyk = (half_x, half_y) if k % 2 == 0 else (half_y, half_x)
        # build for the -y face, then rotate
        with placed((cx, cy, 0), rot):
            hw = hxk + overhang
            ylo = -(hyk + overhang)
            run = hyk + overhang
            zlo = zb - (zt - zb) / hyk * overhang
            rise = zt - zlo
            L = math.hypot(run, rise)
            d = V3((0, run / L, rise / L)); nn = V3((0, -rise / L, run / L))
            E = V3((0, ylo, zlo))
            # deck: trapezoid-ish solid built as hexa with apex collapsed
            hwa = 0.02
            pts = [E + V3((-hw, 0, 0)), E + V3((hw, 0, 0)), V3((hwa, 0, zt)) , V3((-hwa, 0, zt))]
            o = nn * (-deck_t)
            hexa('roof_deck', [pts[0] + o, pts[1] + o, pts[2] + o, pts[3] + o, pts[0], pts[1], pts[2], pts[3]], (0.8, 0.8, 0.8), skip=())
            shingles(E, V3((1, 0, 0)), d, nn, L, lambda p, hw=hw, L=L: (-hw * (1 - p / L) * 0.97, hw * (1 - p / L) * 0.97), exp=exp, Ls=Ls, wr=wr, mat=mat, colk=colk)
    # hip caps
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        zlo = zb - (zt - zb) / half_y * overhang
        p0 = V3((cx + sx * (half_x + overhang), cy + sy * (half_y + overhang), zlo + 0.02))
        hip_cap(p0, apex + V3((0, 0, -0.02)), 0.09)


# ------------------------------------------------------------------ dormer
def dormer(yf, uc, w, zs, K, K2=0.8, hgt=1.35, window_w=0.8, window_h=0.95, ov=0.2, front_mat='siding_wood', shutters=False, col=(1, 1, 1),
           style='lap', flowerbox=False, opening=False):
    """front dormer (front wall plane at y=-yf, centred x=uc) standing on a main roof with slope K / surface fn zs(y)."""
    yf0 = yf
    zmain = zs(0.0)

    def zd_for(yf_, K2_):
        return zs(yf_) + hgt + K2_ * (w / 2 + ov) - 0.02
    K2e = K2
    while zd_for(yf, K2e) > zmain - 0.25 and K2e > 0.58:
        K2e -= 0.04
    while zd_for(yf, K2e) > zmain - 0.25 and yf < yf0 + 1.6:
        yf += 0.1
    K2 = K2e
    F = Fr((uc, -yf, 0), (1, 0, 0), (0, -1, 0))
    zb = zs(yf)
    he = zb + hgt
    z0w = zb - 0.25
    back = (he + 0.1 - zb) / K
    ya, ub = -w / 2, w / 2
    for su in (-1, 1):
        x = uc + su * w / 2
        xa_, xb_ = (x - 0.1, x) if su < 0 else (x, x + 0.1)
        pts = [(-yf, z0w), (-yf, he), (-(yf - back), he), (-(yf - back), zs(yf - back) - 0.25)]
        prism(front_mat if style == 'lap' else 'plaster', pts, (xa_, 0, 0), V3((0, 1, 0)), V3((0, 0, 1)), V3((1, 0, 0)), xb_ - xa_, recalc=True, col=col)
    wc = zb + 0.15 + window_h / 2
    hole = win_hole(0, wc, window_w, window_h)
    # local frame centred on dormer
    core(F, -w / 2, w / 2, z0w, he, [hole], 'mortar', -0.2, -0.03)
    if style == 'lap':
        siding(F, -w / 2, w / 2, z0w + 0.02, he, [hole], mat=front_mat, tcol=col)
    else:
        plaster_wall(F, -w / 2, w / 2, z0w + 0.02, he, [hole], col=col)
    zr_d = he + K2 * (w / 2 + ov) - 0.02
    gable_fill(F, w / 2, he, zr_d - 0.13, style='lap' if style == 'lap' else 'plaster', mat=front_mat, col=col)
    F.box('paint_trim', -w / 2 - 0.02, w / 2 + 0.02, 0, 0.03, he - 0.02, he + 0.04)
    if opening:
        F.box('soot', -window_w / 2, window_w / 2, -0.6, -0.1, wc - window_h / 2, wc + window_h / 2)
        F.box('paint_trim', -window_w / 2 - 0.1, window_w / 2 + 0.1, -0.06, 0.05, wc + window_h / 2, wc + window_h / 2 + 0.1)
        F.box('paint_trim', -window_w / 2 - 0.1, -window_w / 2, -0.06, 0.05, wc - window_h / 2, wc + window_h / 2)
        F.box('paint_trim', window_w / 2, window_w / 2 + 0.1, -0.06, 0.05, wc - window_h / 2, wc + window_h / 2)
    else:
        window(F, 0, wc, window_w, window_h, rows=2, cols=1, shutters=shutters, flowerbox=flowerbox)
    # roof (two planes), built in a rotated local frame: local x' -> world +y, local y' -> world -x
    yfront = -(yf + ov + 0.1)
    back_r = (zr_d + 0.1 - zb) / K
    yback = -(yf - back_r)
    with placed((uc, 0, 0), math.pi / 2):
        for side in (-1, 1):
            roof_plane(yfront, yback, (side * (w / 2 + ov), he - 0.02), (0, zr_d), exp=0.12, Ls=0.28, wr=(0.14, 0.24), rafters=False, barge=(True, False))
        prism('timber_beam', [(-0.16, zr_d - K2 * 0.16), (0.16, zr_d - K2 * 0.16), (0.16, zr_d - K2 * 0.16 + 0.04), (0, zr_d + 0.07), (-0.16, zr_d - K2 * 0.16 + 0.04)],
              (yfront - 0.02, 0, 0), V3((0, 1, 0)), V3((0, 0, 1)), V3((1, 0, 0)), yback - yfront + 0.02)
    return F


# ------------------------------------------------------------------ chimney
def brick_face(F, u0, u1, z0, z1, n_depth=0.012, pal=None, brick=(0.25, 0.085), gap=0.01, sub=0):
    pal = pal or [(1.0, 0.82, 0.72), (0.9, 0.68, 0.56), (1.1, 0.95, 0.85), (0.78, 0.55, 0.45), (1.0, 0.75, 0.6)]
    bl, bh = brick
    names = {(0, -1): 'front', (0, 1): 'back', (1, 0): 'right', (-1, 0): 'left'}
    keep = names[(round(F.N.x), round(F.N.y))]
    skp = tuple(x for x in ('bottom', 'front', 'back', 'left', 'right') if x != keep)
    nrow = max(1, int((z1 - z0) / (bh + gap)))
    for r in range(nrow):
        zb = z0 + r * (bh + gap)
        off = (bl / 2 + gap / 2) if r % 2 else 0.0
        u = u0 - off
        while u < u1:
            a = max(u, u0); b = min(u + bl, u1)
            u += bl + gap
            if b - a < 0.02: continue
            c = rng.choice(pal)
            k = 1 + rng.uniform(-0.1, 0.1)
            F.box('brick', a, b, -0.006, n_depth, zb, zb + bh, col=(c[0] * k, c[1] * k, c[2] * k), skip=skp)


def chimney(cx, cy, w, d, zb, zt, kind='brick', name=None, pots=1, cap_h=0.0, register=True, flash_z=None, grow=0.0, cap=True):
    """rectangular stack centred (cx,cy), size w(x) x d(y), from zb to zt (top of cap)."""
    hx, hy = w / 2, d / 2
    mat = 'brick' if kind == 'brick' else 'stone_chimney'
    ztop_shaft = zt - 0.42
    box('mortar', cx - hx + 0.02, cx + hx - 0.02, cy - hy + 0.02, cy + hy - 0.02, zb, ztop_shaft)
    fr = [Fr((cx, cy - hy, 0), (1, 0, 0), (0, -1, 0)), Fr((cx, cy + hy, 0), (-1, 0, 0), (0, 1, 0)),
          Fr((cx + hx, cy, 0), (0, 1, 0), (1, 0, 0)), Fr((cx - hx, cy, 0), (0, -1, 0), (-1, 0, 0))]
    ext = [hx, hx, hy, hy]
    for F, e in zip(fr, ext):
        if kind == 'brick':
            brick_face(F, -e, e, zb, ztop_shaft)
        else:
            masonry(F, mat, -e, e, zb, ztop_shaft, -0.15, 0.0, pal=PAL_STONE, hs=(0.13, 0.3), ws=(0.2, 0.55), m=1, k=0.6, noise=0.1, rough=0.02)
    if not cap:
        box('stone_chimney', cx - hx - 0.04, cx + hx + 0.04, cy - hy - 0.04, cy + hy + 0.04, ztop_shaft, zt, n=(3, 3, 1), cj=0.08)
        box('stone_chimney', cx - hx - 0.07, cx + hx + 0.07, cy - hy - 0.07, cy + hy + 0.07, zt - 0.05, zt, n=(3, 3, 1), cj=0.08)
        return V3((cx, cy, zt))
    # corbelled cap: 3 stepped courses
    zc = ztop_shaft
    for i, (g, h) in enumerate(((0.04, 0.09), (0.07, 0.09), (0.09, 0.09))):
        box(mat if kind != 'brick' else 'brick', cx - hx - g, cx + hx + g, cy - hy - g, cy + hy + g, zc, zc + h, col=(0.85, 0.65, 0.55) if kind == 'brick' else (1, 1, 1), cj=0.06, n=(2, 2, 1))
        zc += h
    # stone cap slab ring + flue opening
    g = 0.09
    ztp = zc + 0.06
    ring_w = 0.1
    for (x0, x1, y0, y1) in ((cx - hx - g, cx + hx + g, cy - hy - g, cy - hy - g + ring_w + 0.06), (cx - hx - g, cx + hx + g, cy + hy + g - ring_w - 0.06, cy + hy + g),
                             (cx - hx - g, cx - hx - g + ring_w + 0.06, cy - hy - g + ring_w + 0.06, cy + hy + g - ring_w - 0.06),
                             (cx + hx + g - ring_w - 0.06, cx + hx + g, cy - hy - g + ring_w + 0.06, cy + hy + g - ring_w - 0.06)):
        box('stone_chimney', x0, x1, y0, y1, zc, ztp, cj=0.08)
    box('soot', cx - hx - g + ring_w + 0.06, cx + hx + g - ring_w - 0.06, cy - hy - g + ring_w + 0.06, cy + hy + g - ring_w - 0.06, zc - 0.02, ztp - 0.04, skip=('bottom',))
    # clay pots for wider stacks
    if pots >= 1 and w > 0.9:
        for sx in (-1, 1):
            lathe('brick', (cx + sx * hx * 0.5, cy, ztp), [(0, 0.1), (0.2, 0.09), (0.26, 0.11)], segs=8, col=(0.9, 0.55, 0.4))
    if register:
        p = reg_chimney(cx, cy, ztp)
        return p
    return V3((cx, cy, ztp))


def flashing(cx, cy, w, d, z, mat='zinc'):
    g = 0.07
    box(mat, cx - w / 2 - g, cx + w / 2 + g, cy - d / 2 - g, cy + d / 2 + g, z, z + 0.04)


# ------------------------------------------------------------------ props
def barrel(x, y, z=0.0, r=0.3, h=0.8, mat='barrel_wood', open_top=False):
    prof = [(0, 0.82 * r), (0.06 * h, 0.92 * r), (0.5 * h, r), (0.94 * h, 0.92 * r), (h, 0.82 * r)]
    lathe(mat, (x, y, z), prof, segs=14, col=tint(1, 1, 1, 0.1), cj=0.08)
    for t in (0.12, 0.32, 0.68, 0.88):
        zz = z + t * h
        rr = r * (0.82 + 0.18 * (1 - abs(t - 0.5) * 2) ** 0.7) + 0.012 if False else None
    for t, rr in ((0.1, 0.915), (0.3, 0.985), (0.7, 0.985), (0.9, 0.915)):
        lathe('iron', (x, y, z + t * h - 0.018), [(0, r * rr + 0.012), (0.036, r * rr + 0.012)], segs=14)
    # top lid detail
    lathe('endgrain', (x, y, z + h - 0.01), [(0, 0.72 * r), (0.012, 0.72 * r)], segs=14, col=(0.8, 0.7, 0.55))


def crate(x, y, z=0.0, sx=0.5, sy=0.4, sz=0.35, rot=0.0):
    with placed((x, y, z), rot):
        T = 'timber_beam'
        n = max(2, int(sz / 0.09))
        for i in range(n):
            za, zb = i * sz / n + 0.005, (i + 1) * sz / n - 0.005
            c = tint(1, 1, 1, 0.12)
            box(T, -sx / 2, sx / 2, -sy / 2, sy / 2, za, zb, col=c, cj=0.05, skip=('bottom',) if i else ())
        for (a, b) in ((-sx / 2 - 0.012, -sx / 2 + 0.04), (sx / 2 - 0.04, sx / 2 + 0.012)):
            box('timber_dark', a, b, -sy / 2 - 0.012, sy / 2 + 0.012, 0.0, sz)
        for (a, b) in ((-sy / 2 - 0.012, -sy / 2 + 0.04), (sy / 2 - 0.04, sy / 2 + 0.012)):
            box('timber_dark', -sx / 2 - 0.012, sx / 2 + 0.012, a, b, 0.0, sz)


def sack(x, y, z=0.0, s=1.0, col=(1, 1, 1), rot=0.0):
    prof = [(0, 0.1), (0.04, 0.17), (0.14, 0.2), (0.27, 0.17), (0.35, 0.09), (0.39, 0.05), (0.43, 0.09), (0.45, 0.05)]
    prof = [(a * s, b * s) for a, b in prof]
    fs = lathe('sack', (x, y, z), prof, segs=9, col=tint(col[0], col[1], col[2], 0.1), cj=0.1)
    for f in fs:
        for l in f.verts:
            l.co.x += (nz3(l.co, 6.0, x) * 0.018) * s
            l.co.y += (nz3(l.co, 6.0, y + 3) * 0.018) * s


def bench(x, y, z=0.0, L=1.6, rot=0.0, seat_h=0.46, D=0.34, back=False):
    with placed((x, y, z), rot):
        for k in range(2):
            box('timber_beam', -L / 2, L / 2, -D / 2 + k * D / 2, -D / 2 + (k + 1) * D / 2 - 0.008, seat_h - 0.045, seat_h, col=tint(1, 1, 1, 0.1), n=(4, 1, 1), cj=0.06)
        for sx in (-1, 1):
            xx = sx * (L / 2 - 0.2)
            box('timber_dark', xx - 0.04, xx + 0.04, -D / 2 + 0.03, D / 2 - 0.03, 0.0, seat_h - 0.045)
            if back:
                box('timber_dark', xx - 0.03, xx + 0.03, D / 2 - 0.05, D / 2 - 0.01, seat_h, seat_h + 0.45)
        if back:
            for k in range(2):
                box('timber_beam', -L / 2, L / 2, D / 2 - 0.03, D / 2 - 0.012, seat_h + 0.18 + k * 0.14, seat_h + 0.30 + k * 0.14)
        box('timber_dark', -L / 2 + 0.25, L / 2 - 0.25, -0.03, 0.03, seat_h - 0.2, seat_h - 0.15)


def table(x, y, z=0.0, sx=1.4, sy=0.7, h=0.78, rot=0.0):
    with placed((x, y, z), rot):
        for k in range(4):
            box('timber_beam', -sx / 2, sx / 2, -sy / 2 + k * sy / 4, -sy / 2 + (k + 1) * sy / 4 - 0.006, h - 0.04, h, col=tint(1, 1, 1, 0.1), n=(4, 1, 1), cj=0.06)
        for ax in (-1, 1):
            for ay in (-1, 1):
                box('timber_dark', ax * (sx / 2 - 0.1) - 0.04, ax * (sx / 2 - 0.1) + 0.04, ay * (sy / 2 - 0.08) - 0.04, ay * (sy / 2 - 0.08) + 0.04, 0, h - 0.04)
        box('timber_dark', -sx / 2 + 0.1, sx / 2 - 0.1, -0.02, 0.02, 0.25, 0.3)


def lantern(F, u, n, z, bracket=True, glow=True, hang=0.28):
    """wall lantern on an iron bracket projecting from frame F."""
    # bracket arm (horizontal) + diagonal brace + scroll
    F.box('iron', u - 0.012, u + 0.012, 0.0, 0.34, z + hang - 0.015, z + hang + 0.015)
    F.prism('iron', [(0.0, z + hang - 0.3), (0.0, z + hang - 0.26), (0.3, z + hang - 0.015), (0.3, z + hang + 0.0)], u - 0.01, u + 0.01) if False else None
    cp = [F.P(u, 0.02, z + hang - 0.28), F.P(u, 0.2, z + hang - 0.1), F.P(u, 0.32, z + hang)]
    tube('iron', cp, 0.009, segs=5, pn=F.U)
    F.box('iron', u - 0.03, u + 0.03, -0.01, 0.015, z + hang - 0.32, z + hang + 0.05)
    c = F.P(u, 0.34, z + hang - 0.02)
    cyl('iron', c, c + V3((0, 0, -0.06)), 0.006, segs=4)
    zb = c.z - 0.06
    # lantern body
    bw = 0.075
    box('iron', c.x - bw, c.x + bw, c.y - bw, c.y + bw, zb - 0.015, zb)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box('iron', c.x + sx * bw - 0.007, c.x + sx * bw + 0.007, c.y + sy * bw - 0.007, c.y + sy * bw + 0.007, zb, zb + 0.2)
    if glow:
        box('lantern_glow', c.x - bw + 0.01, c.x + bw - 0.01, c.y - bw + 0.01, c.y + bw - 0.01, zb + 0.015, zb + 0.185)
    hexa('iron', [(c.x - bw - 0.015, c.y - bw - 0.015, zb + 0.2), (c.x + bw + 0.015, c.y - bw - 0.015, zb + 0.2), (c.x + bw + 0.015, c.y + bw + 0.015, zb + 0.2),
                  (c.x - bw - 0.015, c.y + bw + 0.015, zb + 0.2), (c.x - 0.02, c.y - 0.02, zb + 0.27), (c.x + 0.02, c.y - 0.02, zb + 0.27),
                  (c.x + 0.02, c.y + 0.02, zb + 0.27), (c.x - 0.02, c.y + 0.02, zb + 0.27)])
    ring_pts = [c + V3((0.0, 0.0, 0.0))]
    return c


def hanging_sign(F, u, z, board_w=0.75, board_h=0.55, arm=1.0, emblem=None, board_mat='timber_beam', border='paint_trim', drop=0.3):
    """iron bracket from wall at height z, board hanging by two chains. emblem(F, ucenter, n, zc) draws the symbol."""
    zt = z
    F.box('iron', u - 0.025, u + 0.025, -0.01, 0.02, zt - 0.1, zt + 0.12)           # wall plate
    F.box('iron', u - 0.016, u + 0.016, 0.0, arm, zt - 0.016, zt + 0.016)           # arm
    cp = [F.P(u, 0.02, zt - 0.5), F.P(u, 0.25, zt - 0.28), F.P(u, 0.55, zt - 0.1), F.P(u, 0.8, zt - 0.02), F.P(u, arm * 0.92, zt - 0.016)]
    tube('iron', cp, 0.011, segs=5, pn=F.U)
    # scroll curl at the end of the arm
    cu = [F.P(u, arm + 0.1 * math.sin(t) , zt + 0.1 * (1 - math.cos(t)) , ) if False else F.P(u, arm - 0.06 + 0.07 * math.sin(t), zt + 0.07 * (1 - math.cos(t)) - 0.0) for t in [i * 0.5 for i in range(9)]]
    tube('iron', cu, 0.008, segs=4, pn=F.U)
    n_b = arm * 0.62
    ub0, ub1 = u - board_w / 2, u + board_w / 2
    zb1 = zt - drop
    zb0 = zb1 - board_h
    for cu_ in (ub0 + 0.08, ub1 - 0.08):
        # chain links
        k = 0
        z = zt - 0.02
        while z > zb1 + 0.01:
            p0 = F.P(cu_, n_b, z); p1 = F.P(cu_, n_b, z - 0.03)
            if k % 2 == 0:
                box('iron', *(lambda a, b: (a.x - 0.007, a.x + 0.007, a.y - 0.007, a.y + 0.007, p1.z, p0.z))(p0, p1))
            else:
                box('iron', p0.x - 0.007, p0.x + 0.007, p0.y - 0.007, p0.y + 0.007, p1.z, p0.z)
            z -= 0.028; k += 1
    # board (double sided)
    F.box(board_mat, ub0, ub1, n_b - 0.03, n_b + 0.03, zb0, zb1, cj=0.06, n=(3, 1, 3))
    for (a0, a1, b0, b1) in ((ub0, ub1, zb1 - 0.04, zb1), (ub0, ub1, zb0, zb0 + 0.04)):
        F.box(border, a0, a1, n_b - 0.036, n_b + 0.036, b0, b1)
    for (a0, a1) in ((ub0, ub0 + 0.04), (ub1 - 0.04, ub1)):
        F.box(border, a0, a1, n_b - 0.036, n_b + 0.036, zb0, zb1)
    if emblem:
        emblem(F, u, n_b, (zb0 + zb1) / 2, board_w, board_h)


def woodpile(x, y, rot, L, H, depth=0.45, z0=0.0, rows_seed=0):
    """stack of split logs along local x (length L), against a wall at local y=0 (stack extends +y)."""
    with placed((x, y, z0), rot):
        z = 0.07
        row = 0
        while z < H:
            xx = -L / 2 + 0.06 + (0.07 if row % 2 else 0.0)
            while True:
                r = rng.uniform(0.055, 0.082)
                if xx + r > L / 2 - 0.04: break
                zc = z + r * 0.4 + rng.uniform(-0.005, 0.01)
                ln = depth * rng.uniform(0.9, 1.0)
                log_axis((xx, 0.0, zc), (xx, ln, zc), r, segs=5, col=tint(1, 1, 1, 0.12))
                xx += 2 * r + 0.006
            z += 0.15
            row += 1


def log_axis(p0, p1, r, segs=7, col=(1, 1, 1), jit=0.12, capboth=False):
    p0 = V3(p0); p1 = V3(p1)
    ax = (p1 - p0); ax.normalize()
    t = V3((0, 0, 1)) if abs(ax.z) < 0.9 else V3((1, 0, 0))
    e1 = ax.cross(t).normalized(); e2 = ax.cross(e1).normalized()
    angs = [2 * math.pi * i / segs for i in range(segs)]
    rj = [1 + jit * (rng.random() - .5) for _ in angs]
    bb = B('bark'); ba = B('endgrain')
    setbm(bb)
    o0 = [bb.verts.new(p0 + (e1 * math.cos(a) + e2 * math.sin(a)) * r * rj[i]) for i, a in enumerate(angs)]
    o1 = [bb.verts.new(p1 + (e1 * math.cos(a) + e2 * math.sin(a)) * r * rj[i]) for i, a in enumerate(angs)]
    cen = (p0 + p1) / 2
    fs = [addface(bb, [o0[i], o0[(i + 1) % segs], o1[(i + 1) % segs], o1[i]], cen) for i in range(segs)]
    paint(fs, col, 0.12)
    setbm(ba)
    for base, flag in ((p1, True), (p0, capboth)):
        if not flag and base is p0: continue
        rs = [ba.verts.new(base + (e1 * math.cos(a) + e2 * math.sin(a)) * r * rj[i] * 0.97) for i, a in enumerate(angs)]
        f = addface(ba, rs, cen)
        c = rng.uniform(0.8, 1.05)
        paint([f], (col[0] * c, col[1] * c * 0.95, col[2] * c * 0.85), 0.15)


def ladder(x, y, z0, z1, rot, lean=0.28, wdt=0.42, mat='timber_beam'):
    with placed((x, y, z0), rot):
        H = z1 - z0
        L = math.hypot(H, lean)
        for sx in (-1, 1):
            cyl(mat, (sx * wdt / 2, 0, 0), (sx * wdt / 2, lean, H), 0.026, segs=5)
        n = int(L / 0.3)
        for i in range(1, n):
            t = i / n
            cyl(mat, (-wdt / 2, lean * t, H * t), (wdt / 2, lean * t, H * t), 0.016, segs=5)


def bucket(x, y, z=0.0, r=0.14, h=0.26):
    lathe('barrel_wood', (x, y, z), [(0, 0.8 * r), (0.04, 0.82 * r), (h, r)], segs=10)
    lathe('iron', (x, y, z + 0.05), [(0, 0.86 * r + 0.006), (0.02, 0.86 * r + 0.006)], segs=10)
    lathe('iron', (x, y, z + h - 0.06), [(0, 0.99 * r + 0.006), (0.02, 0.99 * r + 0.006)], segs=10)
    lathe('soil', (x, y, z + h - 0.03), [(0, 0.9 * r), (0.01, 0.9 * r)], segs=10)


def pot(x, y, z=0.0, r=0.16, h=0.3, flowers=True):
    lathe('door_blue', (x, y, z), [(0, 0.6 * r), (0.04 * h, 0.75 * r), (0.7 * h, r), (h, 1.0 * r)], segs=10, col=(1.2, 1.1, 1.0))
    lathe('soil', (x, y, z + h - 0.03), [(0, 0.9 * r), (0.01, 0.9 * r)], segs=10)
    if flowers:
        plant_cluster(x, y, z + h - 0.02, r * 1.3, r * 1.3, nflow=8, leaf=0.07, nleaf=6)


def stump(x, y, r=0.22, h=0.42):
    lathe('bark', (x, y, -0.02), [(0, r), (h * 0.5, r * 0.97), (h, r * 0.95)], segs=10, col=tint(1, 1, 1, 0.1), cj=0.1, cap_bottom=False)
    lathe('endgrain', (x, y, h - 0.025), [(0, r * 0.94), (0.01, r * 0.94)], segs=10, col=(0.9, 0.78, 0.6), cj=0.1)


def stone_steps(F, uc, w, nsteps=2, rise=0.17, tread=0.34, mat='stone_foundation', ztop=Z0):
    for i in range(nsteps):
        top = ztop - rise * (i + 1) + 0.0
        depth = tread * (nsteps - i) + 0.05
        c = F.P(uc, depth / 2 - 0.0 + 0.0, (top - 0.3) / 2 + 0.0)
        # blocks from -0.3 to top, depth growing as we go down
    for i in range(nsteps):
        top = ztop - rise * i
        d = 0.08 + tread * (i + 1)
        sx = abs(F.U.x) * w + abs(F.N.x) * d
        sy = abs(F.U.y) * w + abs(F.N.y) * d
        c = F.P(uc, d / 2 + 0.0, (top - 0.4) / 2)
        rbox(mat, (c.x, c.y, (top - 0.4) / 2 + 0.0), (sx, sy, top + 0.4), col=tint(1, 1, 1, 0.08), m=1, k=0.6, noise=0.03) if False else None
        rbox(mat, (c.x, c.y, top - 0.15), (sx, sy, 0.3 + 0.0), col=tint(1, 1, 1, 0.08), m=1, k=0.6, noise=0.03)


def hood(F, uc, wd, z, depth=0.95, rise=0.4):
    """small shed roof (door hood) on knee braces. z = height of the wall-side roof surface."""
    sg = F.N.y
    y0 = F.O.y
    pa = F.P(uc - wd / 2, 0, 0); pb = F.P(uc + wd / 2, 0, 0)
    xa, xb = min(pa.x, pb.x), max(pa.x, pb.x)
    roof_plane(xa, xb, (y0 + sg * depth, z - rise), (y0 - sg * 0.05, z), exp=0.12, Ls=0.28, wr=(0.14, 0.24), rafters=False)
    for u in (uc - wd / 2 + 0.15, uc + wd / 2 - 0.15):
        a = F.P(u, 0.04, z - 0.75); b = F.P(u, depth - 0.18, z - rise * (depth - 0.18) / depth - 0.14)
        c = F.P(u, 0.04, z - 0.2)
        cyl('timber_dark', a, b, 0.035, segs=5)
        cyl('timber_dark', c, b, 0.025, segs=5)
        F.box('timber_dark', u - 0.05, u + 0.05, 0, 0.05, z - 0.8, z - 0.1)
    zb = z - rise * (depth - 0.16) / depth - 0.2
    F.box('timber_beam', uc - wd / 2 + 0.05, uc + wd / 2 - 0.05, depth - 0.2, depth - 0.12, zb, zb + 0.1, n=(4, 1, 1), cj=0.1)


def turned_post(x, y, z0, ztop, mat='paint_trim', plinth=0.12):
    box(mat, x - 0.075, x + 0.075, y - 0.075, y + 0.075, z0, z0 + plinth)
    box(mat, x - 0.062, x + 0.062, y - 0.062, y + 0.062, z0 + plinth, z0 + plinth + 0.05)
    H = ztop - 0.1 - (z0 + plinth + 0.05)
    prof = [(0.0, 0.048), (0.03 * H, 0.052), (0.05 * H, 0.038), (0.30 * H, 0.04), (0.36 * H, 0.056), (0.42 * H, 0.04),
            (0.84 * H, 0.04), (0.9 * H, 0.054), (0.94 * H, 0.04), (1.0 * H, 0.05)]
    lathe(mat, (x, y, z0 + plinth + 0.05), prof, segs=12)
    box(mat, x - 0.07, x + 0.07, y - 0.07, y + 0.07, ztop - 0.1, ztop)


def porch(xc, wd, depth, y_wall, zdeck=0.45, zr_wall=2.85, zr_front=2.5, opening=0.0, rails=True, bench_side=0, steps_w=1.5):
    """front porch (faces -y). y_wall = y of wall plane (negative)."""
    x0, x1 = xc - wd / 2, xc + wd / 2
    yf = y_wall - depth
    # deck boards along x
    y = yf
    while y < y_wall - 0.01:
        w = min(0.138, y_wall - y)
        box('deck_planks', x0, x1, y + 0.003, y + w - 0.003, zdeck - 0.03, zdeck, col=tint(1, 1, 1, 0.14), n=(max(1, int(wd / 1.5)), 1, 1), cj=0.08, seed=y * 7, skip=('bottom',))
        y += w
    box('soot', x0 + 0.02, x1 - 0.02, yf + 0.02, y_wall, 0.0, zdeck - 0.03, skip=('bottom',))
    # skirt boards
    xx = x0
    while xx < x1 - 0.05:
        box('timber_dark', xx, xx + 0.108, yf - 0.05, yf - 0.005, 0.03, zdeck - 0.03, col=tint(1, 1, 1, 0.14), cj=0.04)
        xx += 0.12
    for sx in (x0, x1 - 0.05):
        yy = yf
        while yy < y_wall - 0.05:
            box('timber_dark', sx, sx + 0.05, yy, yy + 0.108, 0.03, zdeck - 0.03, col=tint(1, 1, 1, 0.14), cj=0.04)
            yy += 0.12
    # steps
    for i in range(2):
        top = zdeck - 0.17 * (i + 1) + 0.0
        dy = 0.3 * (i + 1)
        box('timber_dark', xc - steps_w / 2 + 0.02, xc + steps_w / 2 - 0.02, yf - dy + 0.03, yf - 0.0, 0.0, top - 0.035)
        box('deck_planks', xc - steps_w / 2, xc + steps_w / 2, yf - dy - 0.0, yf - dy + 0.3 - 0.01, top - 0.035, top, col=tint(1, 1, 1, 0.1), n=(4, 1, 1), cj=0.06)
    # posts, beam, roof
    zl = lambda yy: zr_wall + (zr_front - zr_wall) * (y_wall - yy) / (depth + 0.3)
    yp = yf + 0.12
    ztop = zl(yp) - 0.14
    for sx in (x0 + 0.12, x1 - 0.12):
        turned_post(sx, yp, zdeck, ztop)
    box('timber_beam', x0 - 0.02, x1 + 0.02, yp - 0.1, yp + 0.1, ztop, ztop + 0.14, n=(max(2, int(wd / 0.5)), 1, 1), cj=0.12)
    roof_plane(x0 - 0.25, x1 + 0.25, (yf - 0.3, zr_front), (y_wall + 0.06, zr_wall), exp=0.135, Ls=0.3, wr=(0.15, 0.26), rafters=False)
    # rafters visible under the roof
    x = x0 - 0.1
    while x < x1 + 0.2:
        yb = y_wall
        a = V3((x, yb, zr_wall - 0.12)); b = V3((x, yf - 0.28, zr_front - 0.12))
        d = b - a
        perp = V3((1, 0, 0))
        obox('timber_dark', a - V3((0.035, 0, 0)) + V3((0, 0, -0.06)), V3((1, 0, 0)), d, V3((0, 0, 1)), 0.07, d.length, 0.01) if False else None
        x += 0.5
    # side rails + front rails
    z0 = zdeck
    def rail_y(x, ya, yb):
        box('paint_trim', x - 0.032, x + 0.032, ya, yb, z0 + 0.92, z0 + 0.99)
        box('paint_trim', x - 0.022, x + 0.022, ya, yb, z0 + 0.12, z0 + 0.17)
        yy = ya + 0.09
        while yy < yb - 0.05:
            box('paint_trim', x - 0.016, x + 0.016, yy - 0.016, yy + 0.016, z0 + 0.17, z0 + 0.92)
            yy += 0.115
    def rail_x(y, xa, xb):
        box('paint_trim', xa, xb, y - 0.032, y + 0.032, z0 + 0.92, z0 + 0.99)
        box('paint_trim', xa, xb, y - 0.022, y + 0.022, z0 + 0.12, z0 + 0.17)
        xx = xa + 0.09
        while xx < xb - 0.05:
            box('paint_trim', xx - 0.016, xx + 0.016, y - 0.016, y + 0.016, z0 + 0.17, z0 + 0.92)
            xx += 0.115
    if rails:
        for sx in (x0 + 0.12, x1 - 0.12):
            rail_y(sx, yp + 0.07, y_wall - 0.04)
        h = steps_w / 2
        rail_x(yp, x0 + 0.19, xc - h)
        rail_x(yp, xc + h, x1 - 0.19)
    return ztop


def garden_bed(x0, x1, y0, y1, plants='cabbage', ring='stone_foundation'):
    tk = 0.2
    box('soil', x0, x1, y0, y1, 0.0, 0.17, n=(5, 5, 1), cj=0.2, freq=6.0, skip=('bottom',),
        post=lambda v, i, j, k: setattr(v, 'co', v.co + V3((0, 0, 0.03 * nz3(v.co, 9.0) + 0.02))) if k == 1 else None, col=(0.8, 0.8, 0.8))

    def line(xa_, ya_, xb_, yb_):
        L = math.hypot(xb_ - xa_, yb_ - ya_)
        ux, uy = (xb_ - xa_) / L, (yb_ - ya_) / L
        t = 0.0
        for w in split_widths(L, 0.26, 0.42):
            cx, cy = xa_ + ux * (t + w / 2), ya_ + uy * (t + w / 2)
            h = rng.uniform(0.17, 0.25)
            size = (abs(ux) * (w - 0.015) + abs(uy) * tk, abs(uy) * (w - 0.015) + abs(ux) * tk, h)
            rbox(ring, (cx, cy, h / 2 - 0.03), size, col=rng.choice(PAL_STONE), m=1, k=0.6, noise=0.1)
            t += w
    line(x0 - tk / 2, y0 - tk, x0 - tk / 2, y1 + tk)
    line(x1 + tk / 2, y0 - tk, x1 + tk / 2, y1 + tk)
    line(x0, y0 - tk / 2, x1, y0 - tk / 2)
    line(x0, y1 + tk / 2, x1, y1 + tk / 2)
    nx = max(2, int((x1 - x0) / 0.5)); ny = max(2, int((y1 - y0) / 0.5))
    for i in range(nx):
        for j in range(ny):
            cx = x0 + (i + 0.5 + rng.uniform(-0.1, 0.1)) * (x1 - x0) / nx
            cy = y0 + (j + 0.5 + rng.uniform(-0.1, 0.1)) * (y1 - y0) / ny
            if plants == 'cabbage' and (i + j) % 3 != 2:
                r = rng.uniform(0.11, 0.16)
                blob('foliage', (cx, cy, 0.2 + r * 0.3), r, col=tint(0.85, 1.05, 0.8, 0.2), rows=3, segs=7, squash=0.7, jit=0.25)
                blob('foliage', (cx, cy, 0.2 + r * 0.55), r * 0.6, col=tint(1.0, 1.2, 0.9, 0.1), rows=2, segs=6, squash=0.8)
            else:
                plant_cluster(cx, cy, 0.17, 0.3, 0.3, nflow=6, leaf=0.07, nleaf=5, flowcols=[(0.95, 0.85, 0.2), (0.95, 0.5, 0.15), (0.9, 0.9, 0.95)])


def roof_fn(ze, K, ye):
    zr = ze + K * ye + 0.14
    return zr, (lambda y: zr - K * abs(y))


def double_door_extras(F, uc, w, z0, h):
    F.box('soot', uc - 0.006, uc + 0.006, -0.17, -0.11, z0 + 0.03, z0 + h - 0.03)
    ring(F, uc - 0.14, -0.1, z0 + h * 0.46, 0.045, 0.007)


def well(x, y, r=0.8, h=0.9):
    n = 11
    for i in range(n):
        a = 2 * math.pi * i / n
        rbox('stone_wall', (x + r * math.cos(a), y + r * math.sin(a), h / 2 - 0.05), (2 * math.pi * r / n * 1.02, 0.34, h * rng.uniform(0.95, 1.05)),
             col=rng.choice(PAL_STONE), m=1, k=0.6, noise=0.06, rot=a + math.pi / 2)
    lathe('soot', (x, y, h * 0.35), [(0, r - 0.15), (0.005, r - 0.15)], segs=16)
    lathe('glass', (x, y, h * 0.38), [(0, r - 0.17), (0.005, r - 0.17)], segs=16) if False else None
    for sx in (-1, 1):
        box('timber_dark', x + sx * (r + 0.12) - 0.07, x + sx * (r + 0.12) + 0.07, y - 0.07, y + 0.07, 0.0, 2.2, n=(1, 1, 3), cj=0.1)
    with placed((0, y, 0)):
        gable_roof(x - r - 0.55, x + r + 0.55, 0.62, 2.0, 0.9, oy=0.18, rafters=False, wr=(0.14, 0.24), exp=0.12, Ls=0.28, barge=True)
    cyl('timber_beam', (x - r - 0.12, y, 1.45), (x + r + 0.12, y, 1.45), 0.065, segs=8)
    cyl('iron', (x + r + 0.12, y, 1.45), (x + r + 0.32, y, 1.45), 0.012, segs=5)
    cyl('iron', (x + r + 0.32, y, 1.45), (x + r + 0.32, y + 0.2, 1.45), 0.012, segs=5)
    cyl('iron', (x + r + 0.32, y + 0.2, 1.45), (x + r + 0.32, y + 0.2, 1.3), 0.015, segs=5)
    cyl('rope', (x, y, 1.45), (x, y, 0.95), 0.008, segs=4)
    bucket(x, y, 0.62, r=0.14, h=0.26)
    cyl('rope', (x, y, 1.45), (x, y, 0.9), 0.01, segs=4)


def haystack(x, y, r=1.0, h=1.6):
    fs = lathe('hay', (x, y, -0.02), [(0, r), (h * 0.15, r * 0.98), (h * 0.45, r * 0.8), (h * 0.75, r * 0.45), (h, 0.05)], segs=14, col=(1, 1, 1), cj=0.2, cap_bottom=False)
    for f in fs:
        for v in f.verts:
            v.co.x += nz3(v.co, 3.0, x) * 0.05; v.co.y += nz3(v.co, 3.0, y + 5) * 0.05
    for i in range(30):
        a = rng.uniform(0, 6.28); zz = rng.uniform(0.1, h * 0.7)
        rr = r * (1 - zz / h * 0.93)
        p = V3((x + (rr + 0.02) * math.cos(a), y + (rr + 0.02) * math.sin(a), zz))
        d = V3((math.cos(a) * 0.6, math.sin(a) * 0.6, rng.uniform(-0.3, 0.2)))
        cyl('hay', p, p + d.normalized() * rng.uniform(0.12, 0.28), 0.006, segs=3, col=tint(1.05, 1.0, 0.8, 0.1), caps=(False, False))


def hay_bale(x, y, z=0.0, sx=0.9, sy=0.45, sz=0.4, rot=0.0):
    with placed((x, y, z), rot):
        box('hay', -sx / 2, sx / 2, -sy / 2, sy / 2, 0, sz, n=(4, 2, 2), cj=0.12, col=tint(1, 1, 0.9, 0.1),
            post=lambda v, i, j, k: setattr(v, 'co', v.co + V3((0.015 * nz3(v.co, 8.0), 0.015 * nz3(v.co, 8.0, 2), 0.015 * nz3(v.co, 8.0, 5)))))
        for u in (-0.2 * sx, 0.2 * sx):
            box('rope', u - 0.01, u + 0.01, -sy / 2 - 0.006, sy / 2 + 0.006, -0.005, sz + 0.006, skip=())
        for i in range(12):
            px = rng.uniform(-sx / 2, sx / 2); pz = rng.uniform(0.05, sz)
            cyl('hay', (px, -sy / 2, pz), (px + rng.uniform(-0.05, 0.05), -sy / 2 - rng.uniform(0.05, 0.12), pz + rng.uniform(-0.05, 0.03)), 0.005, segs=3, caps=(False, False))


def trough(x, y, L=1.8, rot=0.0):
    with placed((x, y, 0), rot):
        for sx in (-1, 1):
            box('stone_wall', sx * L / 2 - 0.12, sx * L / 2 + 0.12, -0.3, 0.3, 0.0, 0.5, col=(1.2, 1.15, 1.05), n=(1, 2, 2), cj=0.08)
        for sy in (-1, 1):
            box('stone_wall', -L / 2, L / 2, sy * 0.3 - 0.07 if sy < 0 else 0.23, sy * 0.3 + 0.07 if sy > 0 else -0.23, 0.0, 0.5, col=(1.15, 1.1, 1.0), n=(4, 1, 2), cj=0.08)
        box('glass', -L / 2 + 0.12, L / 2 - 0.12, -0.22, 0.22, 0.32, 0.325)
        box('soot', -L / 2 + 0.12, L / 2 - 0.12, -0.22, 0.22, 0.05, 0.32, skip=('top',))


def milk_can(x, y, z=0.0, s=1.0):
    lathe('zinc', (x, y, z), [(0, 0.1 * s), (0.02 * s, 0.14 * s), (0.28 * s, 0.14 * s), (0.34 * s, 0.1 * s), (0.4 * s, 0.075 * s), (0.44 * s, 0.085 * s)], segs=10)
    lathe('zinc', (x, y, z + 0.43 * s), [(0, 0.1 * s), (0.02 * s, 0.1 * s)], segs=10)
    box('iron', x + 0.12 * s, x + 0.15 * s, y - 0.04, y + 0.04, z + 0.28 * s, z + 0.4 * s)


def bush(x, y, r=0.6, h=None, flowers=False):
    h = h or r * 1.2
    for i in range(int(6 + r * 10)):
        a = rng.uniform(0, 6.28); d = rng.uniform(0, r * 0.7)
        z = rng.uniform(0.15, h * 0.9)
        rr = r * rng.uniform(0.35, 0.55)
        blob('foliage', (x + d * math.cos(a), y + d * math.sin(a), z), rr, col=tint(0.7 + rng.random() * 0.3, 0.95, 0.7, 0.2), rows=3, segs=7, squash=0.85, jit=0.3)
    if flowers:
        for i in range(10):
            a = rng.uniform(0, 6.28); d = rng.uniform(0.2, r * 0.9)
            blob('flowers', (x + d * math.cos(a), y + d * math.sin(a), rng.uniform(0.3, h)), 0.04, col=tint(0.95, 0.85, 0.9, 0.2), rows=2, segs=5)


def arch_pts(w, zspring, n=8):
    """left curve of an equilateral pointed arch from (-w/2,zspring) to the apex (0, zspring+0.866w), as (du, z)."""
    pts = []
    for i in range(n + 1):
        a = math.pi - (math.pi / 3) * i / n
        pts.append((w / 2 + w * math.cos(a), zspring + w * math.sin(a)))
    return pts


def arch_z(u, w, zspring):
    if abs(u) > w / 2: return zspring
    cu = (w / 2) if u <= 0 else (-w / 2)
    return zspring + math.sqrt(max(0.0, w * w - (u - cu) ** 2))


def arch_surround(F, uc, w, z0, zspring, ring_w=0.17, out=0.05, mat='stone_wall', dk=1.35):
    """wall infill (spandrels), voussoir ring and jambs around a pointed-arch opening centred on u=uc."""
    L = arch_pts(w, zspring)
    zt = L[-1][1]
    left = [(uc + a, z) for a, z in L]
    right = [(uc - a, z) for a, z in reversed(L)]
    F.poly(mat, [(uc - w / 2, zspring)] + left[1:] + [(uc - w / 2, zt + 0.0)], -0.26, 0.0, col=(dk * 0.9,) * 3, cj=0.06)
    F.poly(mat, [(uc + w / 2, zspring)] + [(uc - a, z) for a, z in L][1:] + [(uc + w / 2, zt)], -0.26, 0.0, col=(dk * 0.9,) * 3, cj=0.06)
    # voussoirs
    for side in (-1, 1):
        arc = [(uc + side * a, z) for a, z in L]
        cen = (uc + side * w / 2, zspring)
        for i in range(len(arc) - 1):
            p0, p1 = arc[i], arc[i + 1]
            def outer(p):
                dx, dz = p[0] - cen[0], p[1] - cen[1]
                l = math.hypot(dx, dz)
                return (p[0] + dx / l * ring_w, p[1] + dz / l * ring_w)
            q0, q1 = outer(p0), outer(p1)
            k = dk * rng.uniform(0.92, 1.12)
            F.poly(mat, [p0, p1, q1, q0] if side < 0 else [p1, p0, q0, q1], -0.2, out, col=(k, k * 0.98, k * 0.94), cj=0.04)
    # jambs
    z = z0
    i = 0
    while z < zspring - 0.05:
        h = min(rng.uniform(0.28, 0.4), zspring - z)
        long_ = (i % 2 == 0)
        ww = ring_w + (0.1 if long_ else 0.0)
        for side in (-1, 1):
            ua, ub = (uc + side * w / 2, uc + side * (w / 2 + ww))
            F.box(mat, min(ua, ub), max(ua, ub), -0.2, out, z, z + h - 0.01, col=(dk * rng.uniform(0.95, 1.1),) * 3, cj=0.05)
        z += h; i += 1


def arch_outline(F, uc, w, z0, zspring, inset=0.0):
    L = arch_pts(w - 2 * inset, zspring)
    left = [(uc + a, z) for a, z in L]
    right = [(uc - a, z) for a, z in reversed(L)]
    return [(uc - w / 2 + inset, z0 + inset)] + left + right[1:] + [(uc + w / 2 - inset, z0 + inset)]


def lancet(F, uc, w, z0, zspring, bars=True, sill=True):
    arch_surround(F, uc, w, z0, zspring)
    out = arch_outline(F, uc, w, z0, zspring, inset=0.0)
    F.poly('window_glow', out, -0.19, -0.178)
    F.poly('glass', arch_outline(F, uc, w, z0, zspring, inset=0.05), -0.131, -0.125)
    ztop = zspring + 0.866 * w
    # stone mullion + leading bars
    F.box('stone_wall', uc - 0.025, uc + 0.025, -0.16, -0.08, z0, ztop - 0.25, col=(1.3, 1.3, 1.25))
    nbar = int((zspring - z0) / 0.4)
    for i in range(1, nbar + 1):
        zz = z0 + i * 0.4
        F.box('iron', uc - w / 2 + 0.04, uc + w / 2 - 0.04, -0.13, -0.1, zz - 0.007, zz + 0.007)
    if sill:
        F.prism('stone_wall', [(-0.02, z0 - 0.1), (0.1, z0 - 0.1), (0.1, z0 - 0.06), (0.0, z0 - 0.0), (-0.02, z0 - 0.0)], uc - w / 2 - 0.12, uc + w / 2 + 0.12, col=(1.35, 1.3, 1.25))
    reg_window(F, uc, (z0 + ztop) / 2)


def round_window(F, uc, zc, r, glass=True):
    n = 16
    for q in range(4):
        sx = 1 if q in (0, 3) else -1
        sz = 1 if q < 2 else -1
        pts = [(uc + sx * r, zc + sz * r)]
        a0 = 0.0
        arcp = []
        for i in range(0, 5):
            a = (math.pi / 2) * i / 4
            arcp.append((uc + sx * r * math.cos(a), zc + sz * r * math.sin(a)))
        F.poly('stone_wall', pts + arcp, -0.26, 0.0, col=(1.2, 1.2, 1.2), cj=0.06)
    ring = [(uc + r * math.cos(2 * math.pi * i / n), zc + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    F.poly('window_glow', ring, -0.19, -0.178)
    F.poly('glass', [(uc + (r - 0.05) * math.cos(2 * math.pi * i / n), zc + (r - 0.05) * math.sin(2 * math.pi * i / n)) for i in range(n)], -0.131, -0.125)
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        r1 = r + 0.15
        k = rng.uniform(1.25, 1.5)
        F.poly('stone_wall', [(uc + r * math.cos(a0), zc + r * math.sin(a0)), (uc + r * math.cos(a1), zc + r * math.sin(a1)), (uc + r1 * math.cos(a1), zc + r1 * math.sin(a1)), (uc + r1 * math.cos(a0), zc + r1 * math.sin(a0))],
               -0.2, 0.05, col=(k, k * 0.98, k * 0.94), cj=0.04)
    for i in range(4):
        a = i * math.pi / 4
        F.box('iron', uc - 0.01, uc + 0.01, -0.13, -0.1, zc - r + 0.05, zc + r - 0.05) if i == 0 else None
    F.box('iron', uc - r + 0.05, uc + r - 0.05, -0.13, -0.1, zc - 0.007, zc + 0.007)
    reg_window(F, uc, zc)


def fence(x0, x1, y, gaps=(), h=0.92, pitch=0.15, mat='paint_trim', rot_front=True):
    """picket fence along x at y; front faces -y. gaps: list of (xa, xb) openings."""
    F = Fr((0, y, 0), (1, 0, 0), (0, -1, 0))
    pts = [(-0.035, 0.0), (0.035, 0.0), (0.035, h - 0.08), (0.0, h), (-0.035, h - 0.08)]
    x = x0
    posts = [x0, x1] + [g for gg in gaps for g in gg]
    while x < x1:
        if not any(a < x < b for a, b in gaps):
            hh = rng.uniform(-0.015, 0.0)
            F.poly(mat, [(x + a, b + hh if b > 0.5 else b) for a, b in pts], -0.0, 0.022, col=tint(1, 1, 1, 0.05))
        x += pitch
    # rails
    xs = sorted([x0] + [g for gg in gaps for g in gg] + [x1])
    segs_ = []
    cur = x0
    for (a, b) in sorted(gaps):
        if a > cur: segs_.append((cur, a))
        cur = b
    if cur < x1: segs_.append((cur, x1))
    for (a, b) in segs_:
        for zz in (0.22, h - 0.25):
            F.box(mat, a, b, 0.022, 0.05, zz, zz + 0.07)
    for xp in posts:
        F.box(mat, xp - 0.05, xp + 0.05, -0.03, 0.07, 0.0, h + 0.06, col=tint(1, 1, 1, 0.05))
        F.box(mat, xp - 0.06, xp + 0.06, -0.04, 0.08, h + 0.06, h + 0.09)


def hay_heap(F, u0, u1, z0, z1, n0=-0.5, n1=-0.1, nstrand=60):
    nrm = F.N

    def post(v, i, j, k):
        d = (v.co - F.O).dot(nrm)
        if d > n1 - 0.02:
            v.co += nrm * (0.2 * max(0.0, nz3(v.co, 3.2) + 0.9)) + V3((0, 0, 0.12 * nz3(v.co, 4.1, 2.0)))
    F.box('hay', u0, u1, n0, n1, z0, z1, n=(7, 2, 4), cj=0.18, col=(1.0, 0.95, 0.75), post=post)
    for i in range(nstrand):
        p = F.P(rng.uniform(u0, u1), n1 + rng.uniform(0.0, 0.25), rng.uniform(z0 + 0.05, z1 - 0.02))
        d = nrm * rng.uniform(0.12, 0.3) + V3((rng.uniform(-0.12, 0.12), 0, rng.uniform(-0.15, 0.1)))
        cyl('hay', p, p + d, 0.005, segs=3, caps=(False, False), col=tint(1.1, 1.0, 0.7, 0.12))


def wheel(x, y, z, r=0.5, rot=0.0, spokes=8):
    """cart wheel in the local x-z plane, axle along local y."""
    with placed((x, y, z), rot):
        wc = V3((0, 0, 0))
        tube('iron', [wc + V3((r * math.cos(t), 0.0, r * math.sin(t))) for t in [i * 2 * math.pi / 20 for i in range(20)]], 0.017, segs=5, closed=True, pn=(0, 1, 0))
        tube('timber_dark', [wc + V3(((r - 0.06) * math.cos(t), 0.0, (r - 0.06) * math.sin(t))) for t in [i * 2 * math.pi / 14 for i in range(14)]], 0.034, segs=5, closed=True, pn=(0, 1, 0))
        for k in range(spokes):
            a = k * 2 * math.pi / spokes
            cyl('timber_dark', wc, wc + V3(((r - 0.06) * math.cos(a), 0, (r - 0.06) * math.sin(a))), 0.02, segs=5)
        cyl('timber_dark', wc + V3((0, -0.06, 0)), wc + V3((0, 0.06, 0)), 0.06, segs=8)


def handcart(x, y, rot=0.0):
    with placed((x, y, 0), rot):
        z0 = 0.5
        # bed
        for k in range(4):
            box('timber_beam', -0.55, 0.55, -0.4 + k * 0.2, -0.4 + (k + 1) * 0.2 - 0.008, z0, z0 + 0.04, n=(3, 1, 1), cj=0.08)
        for sy in (-1, 1):
            for j in range(2):
                box('timber_beam', -0.55, 0.55, sy * 0.4 - 0.02 if sy < 0 else 0.38, sy * 0.4 + 0.02 if sy > 0 else -0.38, z0 + 0.04 + j * 0.13, z0 + 0.04 + (j + 1) * 0.13 - 0.01, n=(3, 1, 1), cj=0.08)
        box('timber_beam', -0.56, -0.5, -0.4, 0.4, z0 + 0.04, z0 + 0.3, n=(1, 3, 2), cj=0.08)
        box('timber_dark', -0.5, 0.5, -0.45, 0.45, z0 - 0.06, z0, n=(3, 3, 1), cj=0.1)
        for sy in (-1, 1):
            cyl('timber_dark', (0.5, sy * 0.3, z0 - 0.02), (1.5, sy * 0.28, z0 + 0.35), 0.025, segs=5)
        cyl('timber_dark', (1.5, -0.28, z0 + 0.35), (1.5, 0.28, z0 + 0.35), 0.022, segs=5)
        cyl('iron', (0.0, -0.5, 0.42), (0.0, 0.5, 0.42), 0.015, segs=5)
        for sy in (-1, 1):
            wheel(0.0, sy * 0.52, 0.45, 0.45, 0.0, spokes=8)
        for sx in (-1, 1):
            cyl('timber_dark', (sx * 0.4, -0.3, 0.0), (sx * 0.4, -0.3, z0 - 0.06), 0.03, segs=5) if False else None
        # sacks in the bed
        sack(-0.15, 0.0, z0 + 0.04, 1.0, col=(1.1, 1.05, 0.95))
        sack(0.25, 0.1, z0 + 0.04, 0.9, col=(1.0, 0.95, 0.9))
