"""Shared sub-assemblies for village props: barrel, bucket, wheel, hoops, rope helix, shingles, planks."""
from vp_lib import *

PINE_W = H('#aa9f8b')      # weathered pine tint
OAK_W = H('#8f7e68')
OAK_D = H('#5f5242')
GREY_W = H('#928d84')      # grey silvered wood
DARK_W = H('#51473a')
IRON_C = H('#3a3a3e')
ROPE_C = H('#a8895a')
STRAW_C = H('#d9b866')


def FM(M0):
    f = Fr((0, 0, 0))
    f.M = M0
    return f


def stave_vessel_bm(prof, N=10, groove=0.0035, ang0=0.0, uvm=1.0, rings=None, bulge=0.003, cap_bottom=True):
    """vessel of N staves. prof = list of (r,z) bottom->top outer profile (smooth control points, resampled).
    Returns bmesh (local coords, axis z). Each stave: 4 ring verts (seam-inset, edge, mid-bulge, edge)."""
    pr = interp_path([Vector((r, z, 0)) for r, z in prof], 2)
    pts = [(p.x, p.y) for p in pr]
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    offs = [(0.0, -groove), (0.07, 0.0), (0.5, bulge), (0.93, 0.0)]
    rings_ = []
    for (r, z) in pts:
        ring = []
        for s in range(N):
            for (o, dr) in offs:
                a = ang0 + TAU * (s + o) / N
                # flat facets: radius of polygon edge with half-angle pi/N
                local = (o - 0.5) * TAU / N
                rr = r * math.cos(math.pi / N) / math.cos(local) if abs(local) < math.pi / N else r
                rr = max(r * 0.94, min(rr, r)) + dr
                ring.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), z)))
        rings_.append(ring)
    M_ = len(offs) * N
    zs = [z for r, z in pts]
    for k in range(len(pts) - 1):
        for i in range(M_):
            j = (i + 1) % M_
            f = bm.faces.new((rings_[k][i], rings_[k][j], rings_[k + 1][j], rings_[k + 1][i]))
            f.smooth = True
            for l, (kk, ii) in zip(f.loops, ((k, i), (k, i + 1), (k + 1, i + 1), (k + 1, i))):
                circ = TAU * pts[kk][0]
                l[ul].uv = (zs[kk] * uvm, ii / M_ * circ * uvm)
    if cap_bottom:
        f = bm.faces.new(rings_[0][::-1]); f.smooth = False
        for l in f.loops:
            l[ul].uv = (l.vert.co.x, l.vert.co.y)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def hoop(mat, M0, r, z, h=0.03, t=0.006, seg=16, col=IRON_C, cfn=None):
    prof = [(r - 0.004, z - h / 2), (r + t, z - h / 2 + 0.002), (r + t, z + h / 2 - 0.002), (r - 0.004, z + h / 2)]
    lathe(mat, None, prof, seg=seg, cap=False, auto=False, col=col, M=M0, cfn=cfn)


def barrel(M0, r_mid=0.30, r_end=0.25, h=0.85, N=10, open_top=False, cfn_wood=None, hoops=4, col=OAK_W, lid=True, seed=0, hoop_col=IRON_C, hoop_mat='iron_dark'):
    """standard staved barrel centred on local z in [0,h]."""
    cfn_wood = cfn_wood or wood_cfn(col, 0.1, 9, seed, grime_z=0.0)
    prof = [(r_end - 0.012, 0.0), (r_end, 0.012), ((r_end + r_mid) / 2 + 0.005, h * 0.27), (r_mid, h * 0.5), ((r_end + r_mid) / 2 + 0.005, h * 0.73), (r_end, h - 0.012), (r_end - 0.012, h)]
    bm = stave_vessel_bm(prof, N=N, uvm=1 / 0.5)
    put_bm('oak', bm, M=M0, cfn=lambda p, M0=M0, cf=cfn_wood: stave_col(M0.inverted() @ p, cf(p), N))
    # head disc
    if lid:
        if open_top:
            lathe('oak', None, [(r_end - 0.02, h - 0.045), (r_end - 0.02, h - 0.055)], seg=24, M=M0, col=OAK_D, cap=True, auto=False)
            lathe('oak', None, [(r_end - 0.012, h - 0.04), (r_end - 0.012, h), (r_end - 0.03, h)], seg=24, M=M0, col=col, cap=False, auto=False)
            lathe('dark', None, [(0.0, h - 0.07), (r_end - 0.025, h - 0.07)], seg=24, M=M0, col=(0.3, 0.25, 0.2), cap=False, auto=False)
        else:
            lathe('oak', None, [(0.0, h - 0.012), (r_end - 0.01, h - 0.012), (r_end - 0.016, h - 0.002), (r_end - 0.03, h)], seg=28, M=M0, col=col, cap=False, auto=False, cfn=None)
    # hoops (iron or wooden)
    zs = {2: [0.1, h - 0.1], 3: [0.08, h * 0.5, h - 0.08], 4: [0.06, 0.24 * h, h - 0.24 * h, h - 0.06], 5: [0.05, 0.2 * h, 0.5 * h, 0.8 * h, h - 0.05]}[hoops]
    for z in zs:
        t = z / h
        rr = interp_r(prof, z)
        hoop(hoop_mat, M0, rr, z, h=0.036 if z in (zs[0], zs[-1]) else 0.03, col=hoop_col)


def interp_r(prof, z):
    for (r0, z0), (r1, z1) in zip(prof[:-1], prof[1:]):
        if z0 <= z <= z1:
            return r0 + (r1 - r0) * (z - z0) / max(1e-6, z1 - z0)
    return prof[-1][0]


def stave_col(p, base, N):
    a = math.atan2(p.y, p.x) / TAU * N
    fr = a - math.floor(a)
    seam = max(0.0, 1 - min(fr, 1 - fr) / 0.06)
    k = 1 - 0.45 * seam
    # per stave tint
    si = int(math.floor(a)) % N
    t = 1 + 0.12 * math.sin(si * 7.3 + 1.2)
    return (base[0] * k * t, base[1] * k * t, base[2] * k * t)


def bucket(M0, r_top=0.17, r_bot=0.135, h=0.28, N=12, col=OAK_W, hoop_n=2, handle=True, seed=0, water=False):
    prof = [(r_bot - 0.008, 0.0), (r_bot, 0.008), (r_bot + (r_top - r_bot) * 0.5, h * 0.5), (r_top, h - 0.004), (r_top - 0.006, h)]
    bm = stave_vessel_bm(prof, N=N, uvm=1 / 0.5, groove=0.003, bulge=0.002)
    put_bm('oak', bm, M=M0, cfn=lambda p, cf=wood_cfn(col, 0.1, 9, seed, grime_z=0.0): stave_col(M0.inverted() @ p, cf(p), N))
    # inner wall (visible inside)
    lathe('dark', None, [(r_top - 0.012, h), (r_top - 0.014, h * 0.2), (0, h * 0.2)], seg=20, M=M0, col=(0.32, 0.25, 0.18), cap=False, auto=False)
    if water:
        lathe('water', None, [(0, h * 0.62), (r_top - 0.03, h * 0.62)], seg=20, M=M0, cap=False, auto=False, col=(0.35, 0.5, 0.55))
    for z in ([0.05, h - 0.05] if hoop_n == 2 else [0.05, h * 0.5, h - 0.05]):
        hoop('iron_dark', M0, interp_r(prof, z), z, h=0.022, t=0.004, seg=24)
    if handle:
        # rope bail: arc from ear to ear
        pts = [Vector((-r_top, 0, h - 0.03))]
        for i in range(1, 12):
            a = math.pi * i / 12
            pts.append(Vector((-math.cos(a) * r_top * 1.0, 0, h - 0.03 + math.sin(a) * 0.17)))
        pts.append(Vector((r_top, 0, h - 0.03)))
        f = FM(M0)
        f.tube('iron_dark', pts, 0.0045, seg=6, col=IRON_C)
        for sx in (-1, 1):
            f.box('iron_dark', (sx * (r_top + 0.002), 0, h - 0.03), (0.012, 0.03, 0.03), col=IRON_C, bev=0.002)


def rope_helix(M0, R, z0, z1, turns, r=0.012, col=ROPE_C, axis='x', seg=8):
    """rope wound around an axle (axis along local x)"""
    pts = []
    n = int(turns * 14)
    for i in range(n + 1):
        t = i / n
        a = TAU * turns * t
        x = z0 + (z1 - z0) * t
        pts.append(Vector((x, math.cos(a) * R, math.sin(a) * R)))
    f = FM(M0)
    f.tube('rope', pts, r, seg=seg, col=col)


def rope_twist_cfn(base, period=0.03):
    def f(p):
        k = 0.82 + 0.18 * math.sin((p.x + p.y + p.z) / period * TAU)
        return (base[0] * k, base[1] * k, base[2] * k)
    return f


def rope_line(pts, r=0.01, col=ROPE_C, seg=6):
    tube('rope', polyline_smooth(pts, 5), r, seg=seg, col=col, cfn=rope_twist_cfn(col, r * 3))


def plank_row(mat, x0, x1, y, z0, n, hgt, thick, gap=0.006, col=PINE_W, seed=0, g=0, cfn_amp=0.12, bev=0.004, wobble=0.0):
    """vertical row of horizontal planks (boards) along x between x0..x1 at depth y."""
    r = random.Random(seed)
    for i in range(n):
        z = z0 + i * (hgt + gap) + hgt / 2
        c = jitter_col(col, 0.1, r)
        beam(mat, (x0, y + r.uniform(-wobble, wobble), z), (x1, y + r.uniform(-wobble, wobble), z), thick, hgt, bev=bev, col=c,
             cfn=wood_cfn(c, cfn_amp, 8, seed + i, grime_z=0.3), up=(0, 0, 1))


def shingle_panel(mat, A, B, C, D, rows, per_row, w, lth, thick, col=OAK_D, seed=0, tilt=0.12, cfn_seed=0, overhang=0.0):
    """roof shingles over quad A(low-left) B(low-right) C(high-right) D(high-left)... rows from low to high.
    Each shingle is a thin box oriented along the slope."""
    r = random.Random(seed)
    A, B, C, D = [Vector(v) for v in (A, B, C, D)]
    for i in range(rows):
        t = i / max(1, rows - 1)
        lo = A.lerp(D, t); hi = B.lerp(C, t)
        sl = (D - A).normalized()
        slope_up = ((C + D) / 2 - (A + B) / 2)
        for j in range(per_row):
            u = (j + 0.5 + (0.5 if i % 2 else 0.0) + r.uniform(-0.1, 0.1)) / per_row
            if u > 1.02:
                continue
            c = lo.lerp(hi, min(1.0, u))
            # orientation: x along (B-A), y along slope direction
            xdir = (B - A).normalized()
            ydir = slope_up.normalized()
            zdir = xdir.cross(ydir).normalized()
            if zdir.z < 0:
                zdir = -zdir
            ydir2 = zdir.cross(xdir)
            Mx = Matrix(((xdir.x, ydir2.x, zdir.x, 0), (xdir.y, ydir2.y, zdir.y, 0), (xdir.z, ydir2.z, zdir.z, 0), (0, 0, 0, 1)))
            tl = Euler((math.radians(tilt * 20 * (1 + r.uniform(-0.3, 0.3))) + 0.04, 0, math.radians(r.uniform(-2, 2))), 'XYZ').to_matrix().to_4x4()
            cc = jitter_col(col, 0.16, r)
            Mx = Matrix.Translation(c + zdir * (0.004 * (i % 2) + 0.001 * r.random())) @ Mx @ tl
            box(mat, None, (w * r.uniform(0.92, 1.0), lth, thick), M=Mx, bev=0.0, col=cc, g=1, skip_down=False, flat=False)
    # ridge cap handled by caller


def coil_rope(M0, R, r=0.012, turns=3, h=0.0, col=ROPE_C):
    f = FM(M0)
    pts = []
    n = turns * 16
    for i in range(n + 1):
        a = TAU * turns * i / n
        rr = R * (1 - 0.35 * i / n)
        pts.append(Vector((math.cos(a) * rr, math.sin(a) * rr, r + 0.0 + h + r * 1.6 * i / n * 0)))
    f.tube('rope', pts, r, seg=6, col=col)


def wheel(M0, R=0.55, hub_r=0.07, width=0.07, spokes=12, col=OAK_W, tire=True, seed=0, felloe_n=6):
    """cartwheel in local XY plane centred at origin; axle = local Z. Use M0 to orient."""
    f = FM(M0)
    # hub (barrel shape)
    f.lathe('oak', (0, 0, 0), [(0.035, -width * 0.9), (hub_r * 0.9, -width * 0.9), (hub_r, -width * 0.45), (hub_r * 1.05, 0), (hub_r, width * 0.45), (hub_r * 0.9, width * 0.9), (0.035, width * 0.9)],
            seg=16, col=OAK_D, cap=False, auto=False)
    f.lathe('iron_dark', (0, 0, 0), [(0.032, -width * 1.05), (0.045, -width * 1.05), (0.045, width * 1.05), (0.032, width * 1.05)], seg=12, col=IRON_C, cap=True, auto=False)
    f.lathe('iron_dark', (0, 0, 0), [(hub_r * 0.88, -width * 0.88), (hub_r * 0.96, -width * 0.88), (hub_r * 0.96, -width * 0.7), (hub_r * 0.88, -width * 0.7)], seg=16, col=IRON_C, cap=False, auto=False)
    f.lathe('iron_dark', (0, 0, 0), [(hub_r * 0.88, width * 0.88), (hub_r * 0.96, width * 0.88), (hub_r * 0.96, width * 0.7), (hub_r * 0.88, width * 0.7)], seg=16, col=IRON_C, cap=False, auto=False)
    rr = R - 0.045
    for i in range(spokes):
        a = TAU * i / spokes
        d = Vector((math.cos(a), math.sin(a), 0))
        a0 = d * (hub_r * 0.8); a1 = d * (rr + 0.01)
        n_ = Vector((0, 0, 1))
        beam('oak', a0, a1, width * 0.7, width * 0.55, up=(0, 0, 1), bev=0.004, col=jitter_col(col, 0.1), cfn=None) if False else None
        # tapered spoke via tube-ish box: use lathe along d
        Ms = M0 @ Matrix.Translation(a0) @ Matrix.Rotation(a, 4, 'Z') @ Matrix.Rotation(math.pi / 2, 4, 'Y')
        lathe('oak', None, [(0.017, 0), (0.0145, (rr - hub_r) * 0.5), (0.0125, rr - hub_r + 0.01)], seg=8, col=jitter_col(col, 0.1), M=Ms, cap=False, auto=False)
    # felloes: curved segments
    for k in range(felloe_n):
        a0 = TAU * k / felloe_n + 0.015; a1 = TAU * (k + 1) / felloe_n - 0.015
        pts = [Vector((math.cos(a0 + (a1 - a0) * s / 6) * (R - 0.025), math.sin(a0 + (a1 - a0) * s / 6) * (R - 0.025), 0)) for s in range(7)]
        prof = [(-width * 0.5, -0.0235), (width * 0.5, -0.0235), (width * 0.5, 0.0235), (-width * 0.5, 0.0235)]
        # sweep rectangular profile (u along z axis of wheel, v radial)
        f.sweep('oak', [(-0.022, -width * 0.5), (0.022, -width * 0.5), (0.022, width * 0.5), (-0.022, width * 0.5)], pts, up=(0, 0, 1), col=jitter_col(OAK_W, 0.12), caps=True, uvm=2.0)
    if tire:
        f.lathe('iron_dark', (0, 0, 0), [(R - 0.003, -width * 0.52), (R + 0.012, -width * 0.52), (R + 0.012, width * 0.52), (R - 0.003, width * 0.52)], seg=48, col=IRON_C, cap=False, auto=False)
        # axis along local z: lathe axis is z => ring in XY plane. good.
        for i in range(felloe_n):
            a = TAU * (i + 0.5) / felloe_n
            nail(M0 @ Vector((math.cos(a) * (R + 0.012), math.sin(a) * (R + 0.012), width * 0.3)), d=M0.to_3x3() @ Vector((math.cos(a), math.sin(a), 0)), r=0.008)
