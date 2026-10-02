"""Sofa, armchairs, cushions, throws (cloth sim)."""
from lv_items import *

F_ = F


def fab(base, amp=0.07, s=9.0, seed=0, wear=None):
    b = C(base)
    def f(p):
        k = 1 + amp * fbm(p.x, p.y, p.z, s, seed, 2) + 0.03 * nz(p.x * 90, p.y * 90, p.z * 90)
        return (b[0] * k, b[1] * k, b[2] * k)
    return f


def cube_grid(bm, cuts):
    """[-1,1]^3 surface grid with (nx,ny,nz) divisions per edge (ints or one int)"""
    if isinstance(cuts, int):
        nx = ny = nz = cuts + 1
    else:
        nx, ny, nz = cuts
    vm = {}
    def vert(i, j, k):
        key = (i, j, k)
        v = vm.get(key)
        if v is None:
            v = bm.verts.new((-1 + 2 * i / nx, -1 + 2 * j / ny, -1 + 2 * k / nz))
            vm[key] = v
        return v
    for i in range(nx):
        for j in range(ny):
            bm.faces.new([vert(i, j, nz), vert(i + 1, j, nz), vert(i + 1, j + 1, nz), vert(i, j + 1, nz)])
            bm.faces.new([vert(i, j + 1, 0), vert(i + 1, j + 1, 0), vert(i + 1, j, 0), vert(i, j, 0)])
    for i in range(nx):
        for k in range(nz):
            bm.faces.new([vert(i, 0, k), vert(i + 1, 0, k), vert(i + 1, 0, k + 1), vert(i, 0, k + 1)])
            bm.faces.new([vert(i, ny, k + 1), vert(i + 1, ny, k + 1), vert(i + 1, ny, k), vert(i, ny, k)])
    for j in range(ny):
        for k in range(nz):
            bm.faces.new([vert(0, j, k + 1), vert(0, j + 1, k + 1), vert(0, j + 1, k), vert(0, j, k)])
            bm.faces.new([vert(nx, j, k), vert(nx, j + 1, k), vert(nx, j + 1, k + 1), vert(nx, j, k + 1)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])


def cushion(mat, M, size, n=4.0, cuts=10, crown=0.0, wrinkle=0.0, tuft=None, tuft_back=None, pipe=0.0, pipe_col=None, col=(1, 1, 1), cfn=None,
            seed=0, pipe_mat=None, button=None, bottom_scale=1.0, pipe_top=True, pipe_bot=True, inflate=0.0, bend=0.0, dens=0.05, subsurf=False, stitch=False):
    """rounded boxed cushion; local axes x,y = panel plane, z = thickness (+z = visible panel).
    tuft(x_m, y_m) -> inward depth (m) on the +z panel. returns nothing (puts into accumulators)."""
    sx, sy, sz = size
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    if cuts is None:
        cuts = (max(3, int(math.ceil(sx / dens))), max(3, int(math.ceil(sy / dens))), max(2, int(math.ceil(sz / (dens * 1.3)))))
    cube_grid(bm, cuts)
    rr = random.Random(seed)
    ox, oy, oz = rr.uniform(0, 50), rr.uniform(0, 50), rr.uniform(0, 50)

    def deform(p):
        L = (abs(p.x) ** n + abs(p.y) ** n + abs(p.z) ** n) ** (1.0 / n)
        q = p / L if L > 1e-6 else p.copy()
        a_top = sstep(0.55, 0.9, q.z)
        a_bot = sstep(0.55, 0.9, -q.z)
        ex = (1 - q.x * q.x) * (1 - q.y * q.y)
        # inflate: sides bulge slightly
        side = max(0.0, 1.0 - abs(q.z) ** 2)
        q.x *= 1 + inflate * side * (1 - q.y * q.y) * 0.5
        q.y *= 1 + inflate * side * (1 - q.x * q.x) * 0.5
        dz = 0.0
        if crown:
            dz += crown * ex * (a_top + a_bot * 0.5) * (1 if q.z > 0 else -1)
        X = q.x * sx / 2; Y = q.y * sy / 2; Z = q.z * sz / 2 + dz * sz / 2
        if tuft and a_top > 0:
            Z -= a_top * tuft(X, Y)
        if tuft_back and a_bot > 0:
            Z += a_bot * tuft_back(X, Y)
        if wrinkle:
            nv = mnoise.noise(Vector((X * 9 + ox, Y * 9 + oy, Z * 9 + oz))) + 0.5 * mnoise.noise(Vector((X * 21 + ox, Y * 21, Z * 21 + oz)))
            Z += wrinkle * nv * (a_top + a_bot + 0.3)
            X += wrinkle * 0.4 * nv * side
        if bend:
            th = X / bend
            rr_ = bend - Z
            X, Z = rr_ * math.sin(th), bend - rr_ * math.cos(th)
        return Vector((X, Y, Z))

    for v in bm.verts:
        v.co = deform(v.co.copy())
    if subsurf:
        bm = modbm(bm, [('SUBSURF', dict(levels=1, render_levels=1))])
    put(mat, bm, M, col, cfn, 2)
    bm.free()
    if pipe > 0:
        pm = pipe_mat or mat
        pc = pipe_col or col
        for zs, enable in ((1.0, pipe_top), (-1.0, pipe_bot)):
            if not enable:
                continue
            pts = []
            N = max(16, int(2 * (sx + sy) / 0.05))
            for i in range(N):
                t = i / N * 4
                k = int(t); f_ = t - k
                if k == 0:
                    p = Vector((-1 + 2 * f_, -1, zs))
                elif k == 1:
                    p = Vector((1, -1 + 2 * f_, zs))
                elif k == 2:
                    p = Vector((1 - 2 * f_, 1, zs))
                else:
                    p = Vector((-1, 1 - 2 * f_, zs))
                q = deform(p)
                # push outward in plane
                d = Vector((q.x / (sx / 2 + 1e-9), q.y / (sy / 2 + 1e-9), 0))
                d = d.normalized() * pipe * 0.7 if d.length > 1e-6 else d
                q = q + Vector((d.x, d.y, 0)) + Vector((0, 0, 0))
                q.z = q.z * 0.97 * (1 if bottom_scale == 1 or zs > 0 else bottom_scale)
                pts.append(M @ q)
            pts.append(pts[0])
            tube(pm, pts, pipe, seg=5, col=pc, cfn=cfn, caps=False, uvm=TEXSC.get(pm.name, 1.0))
    if stitch:
        def rim(t, zs, k=1.0):
            kk = int(t) % 4; f_ = t - int(t)
            if kk == 0:
                return Vector((k * (-1 + 2 * f_), -k, zs))
            if kk == 1:
                return Vector((k, k * (-1 + 2 * f_), zs))
            if kk == 2:
                return Vector((k * (1 - 2 * f_), k, zs))
            return Vector((-k, k * (1 - 2 * f_), zs))
        Ns = max(24, int(2 * (sx + sy) / 0.02))
        sc_ = shade(C(col) if not isinstance(col, tuple) else col, 0.6) if False else (0.35, 0.3, 0.24)
        bmS = bmesh.new()
        ulS = bmS.loops.layers.uv.new('UVMap')
        for i in range(Ns):
            t = i / Ns * 4
            dt = 0.55 / Ns * 4
            a_ = deform(rim(t, 1.0, 0.9)); b_ = deform(rim(t + dt, 1.0, 0.9)); c_ = deform(rim(t, 1.0, 0.8))
            tg = (b_ - a_)
            if tg.length < 1e-6:
                continue
            side = (c_ - a_)
            n_ = tg.cross(side)
            if n_.length < 1e-9:
                continue
            n_.normalize()
            if n_.z < 0:
                n_ = -n_
            tgn = tg.normalized(); sd = n_.cross(tgn).normalized()
            m_ = (a_ + b_) / 2 + n_ * 0.0007
            vs = [bmS.verts.new(m_ - tgn * (tg.length * 0.5) - sd * 0.0011), bmS.verts.new(m_ + tgn * (tg.length * 0.5) - sd * 0.0011),
                  bmS.verts.new(m_ + tgn * (tg.length * 0.5) + sd * 0.0011), bmS.verts.new(m_ - tgn * (tg.length * 0.5) + sd * 0.0011)]
            fcS = bmS.faces.new(vs)
            if fcS.normal.dot(n_) < 0:
                fcS.normal_flip()
        put(MATS['yarn'], bmS, M, sc_, None, 2)
        bmS.free()


def tuft_diamond(cols, rows, dx, dy, depth, sig=0.03, fold=0.55, fw=0.02, ox=0.0, oy=0.0):
    pts = []
    for r in range(rows):
        for c in range(cols):
            x = (c - (cols - 1) / 2 + (0.5 if r % 2 else 0)) * dx + ox
            y = (r - (rows - 1) / 2) * dy + oy
            pts.append((x, y))
    segs = []
    for i, (x, y) in enumerate(pts):
        for j in range(i + 1, len(pts)):
            xj, yj = pts[j]
            if abs(abs(xj - x) - dx / 2) < dx * 0.1 and abs(abs(yj - y) - dy) < dy * 0.1:
                segs.append(((x, y), (xj, yj)))

    def fn(X, Y):
        t = 0.0
        for (x, y) in pts:
            d2 = (X - x) ** 2 + (Y - y) ** 2
            if d2 < (3.2 * sig) ** 2:
                t += math.exp(-d2 / (sig * sig))
        tf = 0.0
        for (a, b) in segs:
            ax, ay = a; bx, by = b
            vx, vy = bx - ax, by - ay
            L2 = vx * vx + vy * vy
            u = clamp(((X - ax) * vx + (Y - ay) * vy) / L2)
            d2 = (X - ax - u * vx) ** 2 + (Y - ay - u * vy) ** 2
            if d2 < (3.2 * fw) ** 2:
                tf += math.exp(-d2 / (fw * fw)) * (0.4 + 0.6 * math.sin(math.pi * u))
        return depth * min(1.15, t + fold * min(1.0, tf))
    return fn, pts


def button(mat, p, nrm, col, r=0.011):
    """covered button: flattened sphere with pucker lines (fabric)"""
    n = Vector(nrm).normalized()
    up = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    xa = up.cross(n).normalized(); ya = n.cross(xa)
    Mx = Matrix(((xa.x, ya.x, n.x, p.x), (xa.y, ya.y, n.y, p.y), (xa.z, ya.z, n.z, p.z), (0, 0, 0, 1)))
    prof = []
    for i in range(4):
        a = math.pi / 2 * i / 3
        prof.append((max(0.001, math.cos(a) * r), math.sin(a) * r * 0.55))
    prof = [(0.001, -0.001)] + prof[:-1] + [(0.001, r * 0.55)]
    lathe(mat, None, [(rr_, zz_) for rr_, zz_ in prof], seg=8, col=col, M=Mx, cap=False)


def turned_foot(f_or_M, x, y, h, r, mat='wood_dark', col=(0.55, 0.38, 0.26), style='bun', brass=True):
    M_ = f_or_M.M if hasattr(f_or_M, 'M') else f_or_M
    Mt = M_ @ Matrix.Translation((x, y, 0))
    if style == 'bun':
        pr = [(r * 0.55, 0.0), (r * 0.8, 0.004), (r * 0.95, h * 0.1), (r * 0.9, h * 0.22), (r * 0.62, h * 0.3), (r * 0.5, h * 0.34), (r * 0.62, h * 0.4), (r * 0.5, h * 0.48),
              (r * 0.46, h * 0.62), (r * 0.58, h * 0.74), (r * 0.7, h * 0.86), (r * 0.7, h * 0.95), (r * 0.9, h)]
    elif style == 'taper':
        pr = [(r * 0.45, 0.0), (r * 0.5, h * 0.05), (r * 0.62, h * 0.4), (r * 0.8, h * 0.6), (r * 0.7, h * 0.64), (r * 0.9, h * 0.7), (r * 0.9, h * 0.8), (r * 1.0, h * 0.82), (r, h)]
    else:
        pr = [(r * 0.5, 0.0), (r * 0.7, h * 0.08), (r * 0.5, h * 0.2), (r * 0.62, h * 0.32), (r * 0.5, h * 0.45), (r * 0.9, h * 0.62), (r * 0.5, h * 0.78), (r * 0.8, h * 0.92), (r, h)]
    seg = 18
    lathe(M[mat], None, pr, seg=seg, col=col, M=Mt, cfn=lambda p: shade(col, 1 + 0.08 * nz(p.x * 40, p.y * 40, p.z * 60)))
    if brass:
        lathe(M['brass'], None, [(r * 0.55, 0.0), (r * 0.58, 0.012), (r * 0.5, 0.013)], seg=14, M=Mt @ Matrix.Translation((0, 0, 0.0)), cap=True) if False else None
        cyl(M['brass'], None, r * 0.57, 0.014, seg=14, M=Mt @ Matrix.Translation((0, 0, 0.007)))
    return Mt


def stitched_seam(mat, pts, col, dash=0.014, r=0.0009):
    """tiny dash stitches across a seam: pts = polyline (world); dashes perpendicular offset"""
    pass


# =========================================================================================== SOFA
def throw_cloth(M0, size, grid, colliders, start_z, seed, frames=90, pins=None, drop_rot=0, cx=0, cy=0):
    pass


def scroll_disc(mat, Mx, rx, ry, cf, pcol, cpf, pleats=10, seed=0):
    """front face of a rolled arm: pleated swirl disc + piping ring + button.  Mx: local z = outward normal"""
    disc = bmesh.new()
    ul = disc.loops.layers.uv.new('UVMap')
    rings = [[disc.verts.new((0, 0, -0.006))]]
    NR, NA = 5, 24
    for i in range(1, NR + 1):
        t = i / NR
        row = []
        for j in range(NA):
            a = j / NA * TAU
            pleat = 0.0016 * math.sin(a * pleats + t * 3) * t * (1 - t * 0.4)
            row.append(disc.verts.new((rx * t * math.cos(a), ry * t * math.sin(a), -0.006 * (1 - t) ** 1.5 + 0.004 * math.sin(t * math.pi) + pleat)))
        rings.append(row)
    for j in range(NA):
        k = (j + 1) % NA
        disc.faces.new([rings[0][0], rings[1][j], rings[1][k]][::-1])
    for i in range(1, NR):
        for j in range(NA):
            k = (j + 1) % NA
            disc.faces.new([rings[i][j], rings[i + 1][j], rings[i + 1][k], rings[i][k]][::-1])
    bmesh.ops.recalc_face_normals(disc, faces=disc.faces[:])
    put(mat, disc, Mx, (1, 1, 1), cf, 2)
    disc.free()
    tube(mat, [Mx @ Vector((rx * math.cos(a), ry * math.sin(a), 0.001)) for a in [i * TAU / 32 for i in range(33)]], 0.0052, seg=6, col=pcol, cfn=cpf, caps=False)
    button(mat, Mx @ V(0, 0, -0.005), Mx.to_3x3() @ V(0, 0, 1), pcol, 0.011)


def sofa(pos, rot, L=1.9, col='#bfae8c', throw=True):
    f = Fr(pos, rot, F_)
    D = 0.88
    base = C(col)
    cf = fab(base, 0.06, 7, 1)
    pcol = shade(base, 0.72)
    cpf = fab(pcol, 0.05, 7, 2)
    FM = f.M
    FAB = M['fabric_linen']
    # --- turned feet + rails
    for sx in (-1, 1):
        for sy in (-1, 1):
            turned_foot(f, sx * (L / 2 - 0.075), sy * (D / 2 - 0.075), 0.12, 0.032, 'wood_dark', (0.5, 0.33, 0.22), 'bun')
    for sy in (-1, 1):
        f.box(M['wood_dark'], (0, sy * (D / 2 - 0.05), 0.135), (L - 0.12, 0.05, 0.03), bev=0.004, col=(0.5, 0.33, 0.22), g=0)
    # --- lower body (apron) with piping top + bottom
    cushion(FAB, FM @ Matrix.Translation((0, 0, 0.22)), (L, D, 0.2), n=8, cuts=None, dens=0.11, pipe=0.0065, cfn=cf, pipe_col=pcol, seed=1, wrinkle=0.001)
    # --- rolled arms
    for s_ in (-1, 1):
        ax = s_ * (L / 2 - 0.095)
        cushion(FAB, FM @ Matrix.Translation((ax, 0.0, 0.37)), (0.19, D - 0.02, 0.4), n=6, cuts=None, dens=0.065, cfn=cf, seed=3 + s_, wrinkle=0.0015, inflate=0.1)
        # roll (cylinder along y) on top
        rl = FM @ Matrix.Translation((ax + s_ * 0.008, 0.0, 0.595)) @ rotm((-90, 0, 0))
        r0 = 0.078
        pr = [(0.001, -D / 2 + 0.005)]
        N = 8
        for i in range(N + 1):
            pr.append((r0 * (0.5 + 0.5 * math.sin(i / N * math.pi * 0.5 + 0.0) ** 0.5) , -D / 2 + 0.005 + 0.025 * i / N))
        prof = [(0.001, -D / 2), (r0 * 0.7, -D / 2 + 0.002), (r0 * 0.96, -D / 2 + 0.012), (r0, -D / 2 + 0.03), (r0 * 1.005, 0.0), (r0, D / 2 - 0.03), (r0 * 0.96, D / 2 - 0.012), (r0 * 0.7, D / 2 - 0.002), (0.001, D / 2)]
        lathe(FAB, None, prof, seg=28, cfn=cf, M=rl, cap=False)
        # front scroll face and rear
        scroll_disc(FAB, FM @ Matrix.Translation((ax + s_ * 0.008, D / 2 + 0.0005, 0.595)) @ rotm((-90, 0, 0)) @ rotm((0, 0, 0)) @ Matrix.Rotation(math.radians(180), 4, 'X') @ Matrix.Identity(4), r0 * 0.98, r0 * 0.98, cf, pcol, cpf, 10, s_) if False else None
        sc = FM @ Matrix.Translation((ax + s_ * 0.008, D / 2 + 0.0, 0.595)) @ Matrix.Rotation(math.radians(-90), 4, 'X') @ Matrix.Rotation(math.radians(180), 4, 'X') @ Matrix.Rotation(math.radians(180), 4, 'X')
        sc = FM @ Matrix.Translation((ax + s_ * 0.008, D / 2 - 0.004, 0.595)) @ Matrix.Rotation(math.radians(-90), 4, 'X')
        # local z of sc points to +y world (see rotation convention) -> outward
        scroll_disc(FAB, sc, r0 * 0.93, r0 * 0.93, cf, pcol, cpf, 10, s_)
        # brass tacks along the lower front of the arm
        for k in range(8):
            z_ = 0.2 + k * 0.045
            sphere(M['brass'], FM @ V(ax + s_ * 0.0, D / 2 - 0.004, z_), 0.0045, seg=8, rings=4, sq=(1, 0.7, 1)) if False else None
    # --- back (diamond tufted)
    bw, bh, bt = L - 0.3, 0.56, 0.2
    tf, pts = tuft_diamond(6, 4, 0.255, 0.12, 0.058, sig=0.036, fold=0.5, fw=0.026)
    bk = FM @ Matrix.Translation((0, -D / 2 + 0.115, 0.585)) @ rotm((-9, 0, 0)) @ rotm((-90, 0, 0))
    cushion(FAB, bk, (bw, bh, bt), n=6.5, cuts=(26, 10, 2), subsurf=True, tuft=tf, cfn=cf, seed=7, wrinkle=0.001, inflate=0.1, pipe=0.0065, pipe_col=pcol, pipe_bot=False)
    for (x, y) in pts:
        if abs(x) < bw / 2 - 0.05 and abs(y) < bh / 2 - 0.05:
            q = bk @ V(x, y, bt / 2 - 0.05 + 0.001)
            button(FAB, q, bk.to_3x3() @ V(0, 0, 1), pcol, 0.0115)
    # --- seat cushions (three, boxed, piped)
    w3 = (L - 0.38) / 3
    for i in range(3):
        x = (i - 1) * w3
        cl = fab(base, 0.05, 8, 20 + i)
        cushion(FAB, FM @ Matrix.Translation((x, 0.07, 0.4)) @ rotm((0, 0, 0.6 * (i - 1))), (w3 - 0.008, 0.62, 0.17), n=5.2, cuts=None, dens=0.052, stitch=True, crown=0.2,
                pipe=0.0055, pipe_col=pcol, cfn=cl, seed=20 + i, wrinkle=0.0025, inflate=0.08)
    # --- scatter pillows
    sp = [(-L / 2 + 0.28, '#b5562f', 14, 'diag'), (-L / 2 + 0.55, '#d0a23e', -10, 'stripe'), (L / 2 - 0.29, '#5f7d73', -16, 'dots')]
    for (x, hc, rz, pat) in sp:
        pillow_scatter(FM @ Matrix.Translation((x, -0.1, 0.66)) @ rotm((-30, rz * 0.2, rz)), 0.4, hc, pat, int(abs(x) * 100))
    if throw:
        sofa_throw(f, L, D)
    collider_f(f, L + 0.02, D + 0.02, F_ + 0.9)
    return f


def pillow_scatter(M0, s, hc, pat, seed):
    """square scatter pillow with piping, centre pinch, tasselled corners"""
    c = C(hc)
    bc = shade(c, 0.7)
    def cf(p):
        q = M0.inverted() @ p
        k = 1.0 + 0.05 * fbm(p.x, p.y, p.z, 12, seed, 2)
        if pat == 'stripe':
            t = 0.5 + 0.5 * math.sin(q.x / 0.026 * math.pi)
            kk = 0.75 + 0.45 * (1 if t > 0.62 else 0)
            return (c[0] * kk * k, c[1] * kk * k, c[2] * kk * k)
        if pat == 'diag':
            t = 0.5 + 0.5 * math.sin((q.x + q.y) / 0.03 * math.pi)
            kk = 0.7 + 0.45 * (1 if t > 0.55 else 0)
            return (c[0] * kk * k, c[1] * kk * k, c[2] * kk * k)
        if pat == 'dots':
            ix = (q.x / 0.05); iy = (q.y / 0.05)
            fx = ix - round(ix); fy = iy - round(iy)
            on = (fx * fx + fy * fy) < 0.07
            kk = 1.35 if on else 0.9
            return (c[0] * kk * k, c[1] * kk * k * (1 if not on else 1.05), c[2] * kk * k * (1 if not on else 1.0))
        return (c[0] * k, c[1] * k, c[2] * k)
    def tuf(X, Y):
        return 0.05 * math.exp(-(X * X + Y * Y) / 0.0016) + 0.0
    cushion(M['fabric_linen'], M0, (s, s, 0.12), n=4.2, cuts=None, dens=0.05, crown=0.42, wrinkle=0.003, pipe=0.0045, pipe_col=bc, cfn=cf, seed=seed, tuft=tuf, inflate=0.1, pipe_bot=False)
    button(M['fabric_linen'], M0 @ V(0, 0, 0.065 + 0.0 - 0.012 + 0.001), M0.to_3x3() @ V(0, 0, 1), bc, 0.009)
    # corner tassels
    for sx in (-1, 1):
        for sy in (-1, 1):
            cp = M0 @ V(sx * s * 0.47, sy * s * 0.47, -0.012)
            tube(M['yarn'], [cp, cp + (M0.to_3x3() @ V(sx * 0.012, sy * 0.012, -0.02))], 0.0025, seg=4, col=bc, caps=False)
            for k in range(7):
                a = k / 7 * TAU
                d = M0.to_3x3() @ V(0.0045 * math.cos(a) + sx * 0.012, 0.0045 * math.sin(a) + sy * 0.012, -0.065)
                tube(M['yarn'], [cp + (M0.to_3x3() @ V(sx * 0.012, sy * 0.012, -0.02)), cp + d * 0.55, cp + d], 0.0013, seg=4, col=shade(bc, 0.9 + 0.2 * (k % 2)), caps=False)


def collider_f(f, W, D, top, off=(0, 0)):
    a = math.radians(f.rot)
    cx, cy = f.p((off[0], off[1], 0))[:2]
    hx = abs(W / 2 * math.cos(a)) + abs(D / 2 * math.sin(a))
    hy = abs(W / 2 * math.sin(a)) + abs(D / 2 * math.cos(a))
    collider(cx - hx, cx + hx, cy - hy, cy + hy, top)


def tartan(base_cols, scale=0.045):
    a_, b_, c_ = [C(x) for x in base_cols]
    def f(p):
        x = p.x / scale; y = p.y / scale
        s1 = 0.5 + 0.5 * math.sin(x * TAU); s2 = 0.5 + 0.5 * math.sin(y * TAU)
        col = a_
        if s1 > 0.82:
            col = b_
        if s2 > 0.86:
            col = b_
        if s1 > 0.93 or s2 > 0.95:
            col = c_
        k = 0.85 + 0.15 * (s1 * 0.5 + s2 * 0.5) + 0.04 * nz(p.x * 120, p.y * 120)
        return (col[0] * k, col[1] * k, col[2] * k)
    return f


def throw_mesh(w, d, nx, ny, M0, z0):
    bm = bmesh.new()
    V2 = [[bm.verts.new(M0 @ Vector((-w / 2 + w * i / nx, -d / 2 + d * j / ny, z0))) for j in range(ny + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(ny):
            bm.faces.new([V2[i][j], V2[i + 1][j], V2[i + 1][j + 1], V2[i][j + 1]])
    return bm


def proxy_box(name, M0, size, bev=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bev > 0:
        m = o.modifiers.new('B', 'BEVEL'); m.width = bev; m.segments = 3
        bpy.ops.object.modifier_apply(modifier='B')
    o.matrix_world = M0
    bpy.context.view_layer.update()
    return o


SIM = os.environ.get('LV_NOSIM', '') == ''


def proxy_cyl(name, M0, r, L, axis_y=True):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=L, vertices=20)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    o.matrix_world = M0
    bpy.context.view_layer.update()
    return o


def proxy_floor():
    return proxy_box('_floor', Matrix.Translation((0, 0, F_ - 0.05)), (9.0, 7.0, 0.1), 0.0)


def fringe_rows(pos, nx, ny, rows, step=1, seed=0, cols=('#e0c070', '#e8dcc0')):
    fr = random.Random(seed)
    for (jr, jn) in rows:
        for i in range(0, nx + 1, step):
            a_ = pos[i * (ny + 1) + jr]; b_ = pos[i * (ny + 1) + jn]
            dd = (a_ - b_)
            if dd.length < 1e-6:
                continue
            dd.normalize()
            wp = Vector(a_)
            tip = wp + dd * 0.045 + V(0, 0, -0.035)
            tip.z = max(tip.z, F_ + 0.003)
            tube(M['yarn'], [wp, wp + dd * 0.028 + V(0, 0, -0.012), tip + V(fr.uniform(-0.004, 0.004), fr.uniform(-0.004, 0.004), 0)], 0.0017, seg=3, col=C(cols[i % 2]), caps=False)


def armchair_throw(f, w, D, seed=3):
    """folded wool throw draped over the right arm of the wing chair (cloth simulation)"""
    if not SIM:
        return
    FM = f.M
    ax = (w / 2 - 0.085)
    prox = [proxy_box('_qa', FM @ Matrix.Translation((ax, 0.04, 0.44)), (0.17, D - 0.16, 0.38), 0.06),
            proxy_cyl('_qr', FM @ Matrix.Translation((ax, 0.05, 0.63)), 0.082, D - 0.2),
            proxy_box('_qs', FM @ Matrix.Translation((0, 0.08, 0.385)), (w - 0.2, 0.6, 0.15), 0.04),
            proxy_box('_qb', FM @ Matrix.Translation((0, -D / 2 + 0.115, 0.76)) @ rotm((-12, 0, 0)), (w - 0.2, 0.17, 0.78), 0.04),
            proxy_box('_qw', FM @ Matrix.Translation((ax - 0.0, -D / 2 + 0.16, 0.78)), (0.11, 0.3, 0.6), 0.04),
            proxy_box('_qbase', FM @ Matrix.Translation((0, 0, 0.215)), (w, D, 0.12), 0.03), proxy_floor()]
    tw, td = 0.46, 0.95
    NXs, NYs = 15, 30
    # pre-shaped as an inverted U (tent) over the arm roll so the sim only has to settle it
    bm = bmesh.new()
    zr = 0.63 + 0.095
    Vq = [[None] * (NYs + 1) for _ in range(NXs + 1)]
    for i in range(NXs + 1):
        for j in range(NYs + 1):
            v_ = -tw / 2 + tw * i / NXs          # along the arm (front-back)
            u_ = -td / 2 + td * j / NYs - 0.15   # across the arm (more length on the seat side)
            zz = zr - max(0.0, abs(u_) - 0.07) * 0.9
            p_ = FM @ Vector((ax + u_ + 0.0, 0.05 + v_, zz + 0.012 * nz(u_ * 6, v_ * 6, 5)))
            Vq[i][j] = bm.verts.new(p_)
    for i in range(NXs):
        for j in range(NYs):
            bm.faces.new([Vq[i][j], Vq[i + 1][j], Vq[i + 1][j + 1], Vq[i][j + 1]])
    Mt = FM @ Matrix.Translation((ax, 0.05, 0.0))
    pos = cloth_sim(bm, None, prox, frames=60, quality=8, mass=0.35, tension=14, compression=14, shear=6, bending=0.9, thickness=0.01, self_col=True)
    for v, p_ in zip(bm.verts, pos):
        v.co = p_
    for o in prox:
        bpy.data.objects.remove(o)
    fringe_rows(pos, NXs, NYs, ((0, 1), (NYs, NYs - 1)), step=1, seed=seed, cols=('#c8923a', '#e8dcc0'))
    bm = modbm(bm, [('SOLIDIFY', dict(thickness=0.006, offset=-1.0))])
    Minv = Mt.inverted()
    pal = [C('#6f7a3a'), C('#d8c88a'), C('#a4602e')]
    def cf(p):
        q = Minv @ p
        k = int((q.x + 1.0) / 0.055) % 4
        c = pal[0] if k < 2 else (pal[1] if k == 2 else pal[2])
        r = 0.9 + 0.12 * math.sin(q.y * 150) + 0.05 * nz(p.x * 90, p.y * 90, p.z * 90)
        return (c[0] * r, c[1] * r, c[2] * r)
    put(M['fabric_wool'], bm, Matrix.Identity(4), (1, 1, 1), cf, 2)
    bm.free()


def sofa_throw(f, L, D):
    """tartan throw draped over the right arm + seat by cloth simulation"""
    if not SIM:
        return
    FM = f.M
    proxies = []
    s_ = 1
    ax = s_ * (L / 2 - 0.1)
    # proxies approximating arm, seat cushions, back
    proxies.append(proxy_box('_pa', FM @ Matrix.Translation((ax, 0.0, 0.43)), (0.2, D, 0.5), 0.07))
    w3 = (L - 0.4) / 3
    for i in range(3):
        x = (i - 1) * w3
        proxies.append(proxy_box('_ps%d' % i, FM @ Matrix.Translation((x, 0.065, 0.395 + 0.0)) , (w3 - 0.01, 0.63, 0.19), 0.05))
    proxies.append(proxy_box('_pb', FM @ Matrix.Translation((0, -D / 2 + 0.125, 0.67)) @ rotm((-10, 0, 0)), (L - 0.26, 0.2, 0.58), 0.05))
    proxies.append(proxy_box('_pbase', FM @ Matrix.Translation((0, 0, 0.215)), (L, D, 0.19), 0.03))
    proxies.append(proxy_floor())
    # throw cloth: drop from above, centred on arm/seat boundary, rotated slightly
    tw, td = 0.62, 1.25
    Mt = FM @ Matrix.Translation((L / 2 - 0.3, 0.03, 1.0)) @ rotm((0, 0, 90 + 12))
    NXs, NYs = 20, 42
    bm = throw_mesh(tw, td, NXs, NYs, Mt, 0.0)
    # crumple the initial shape slightly
    for v in bm.verts:
        v.co.z += 0.02 * nz(v.co.x * 4, v.co.y * 4, 3) + 0.0
    pos = cloth_sim(bm, None, proxies, frames=70, quality=8, mass=0.35, tension=14, compression=14, shear=6, bending=0.9, thickness=0.01, self_col=True)
    for v, p_ in zip(bm.verts, pos):
        v.co = p_
    for o in proxies:
        bpy.data.objects.remove(o)
    # subdivide + solidify
    fringe_rows(pos, NXs, NYs, ((0, 1), (NYs, NYs - 1)), step=1, seed=4)
    bm = modbm(bm, [('SOLIDIFY', dict(thickness=0.006, offset=-1.0))])
    tc = tartan(['#7a1d1a', '#1f3a2a', '#e0c070'], 0.05)
    # tartan coordinates: use throw local (u along length) via inverse xf
    Minv = Mt.inverted()
    def cf(p):
        q = Minv @ p
        return tc(Vector((q.x, q.y, 0)))
    put(M['fabric_wool'], bm, Matrix.Identity(4), (1, 1, 1), cf, 2)
    bm.free()
    # fringe on the two short ends: tiny strands along the cloth ends
    # (approximate: find end rows from the sim vertices)
    return pos


# =========================================================================================== ARMCHAIRS
def cabriole_leg(f, x, y, h, r, mat='wood_dark', col=(0.5, 0.33, 0.22), flip=1, ang=0.0):
    """carved cabriole: S-curve swept tube with knee leaf carving and pad foot; ang rotates leg splay direction (deg)"""
    a = math.radians(ang)
    pts = []
    N = 14
    sx = math.cos(a); sy = math.sin(a)
    for i in range(N + 1):
        t = i / N
        z = h * (1 - t)
        off = 0.045 * (math.sin(t * math.pi * 1.0) ** 1.0) * 1.0 * (1 - 0.15 * t) - 0.02 * t ** 2
        pts.append(V(x + sx * off, y + sy * off, z))
    rad = [r * (1.25 - 0.95 * math.sin(min(1.0, t * 1.3) * math.pi * 0.62)) if t < 0.62 else r * (0.4 + 0.15 * (t - 0.62) / 0.38) for t in [i / N for i in range(N + 1)]]
    rad = [max(0.009, q) for q in rad]
    tube_f(f, M[mat], pts, rad, 10, col)
    # pad foot
    fp = pts[-1]
    f.lathe(M[mat], (fp.x, fp.y, 0.0), [(0.001, 0), (0.026, 0), (0.03, 0.005), (0.02, 0.012), (0.012, 0.02), (0.012, 0.03)], seg=14, col=col)
    # knee carving (leaf)
    kn = pts[2]
    for k in range(3):
        aa = -0.5 + 0.5 * k
        f.tube(M[mat], [V(kn.x + 0.0, kn.y + 0.01 * math.cos(aa), kn.z - 0.01), V(kn.x + 0.012 * sx * flip + 0.0, kn.y + 0.012 * sy, kn.z - 0.035 - 0.01 * k)], [0.004, 0.0015], seg=4, col=shade(col, 1.1))


def tube_f(f, mat, pts, rad, seg, col):
    tube(mat, [f.p(p) for p in pts], rad, seg=seg, col=col, cfn=lambda p: shade(col, 0.93 + 0.12 * nz(p.x * 40, p.y * 40, p.z * 50)))


def nailhead_row(f, pts, r=0.0042, mat='brass'):
    for p in pts:
        sphere(M[mat], f.p(p), r, seg=6, rings=3, sq=(1, 1, 0.65))


def armchair_yellow(pos, rot, w=0.84):
    """wing-back armchair, ochre velvet, button-tufted back, nailhead trim, cabriole front legs"""
    f = Fr(pos, rot, F_)
    D = 0.86
    base = '#c8923a'
    cf = fab(base, 0.07, 8, 2)
    pcol = shade(C(base), 0.7)
    cpf = fab(pcol, 0.05, 8, 5)
    FM = f.M
    # legs: cabriole front, raked back
    for sx in (-1, 1):
        cabriole_leg(f, sx * (w / 2 - 0.07), D / 2 - 0.08, 0.17, 0.028, 'wood_dark', (0.48, 0.3, 0.2), flip=sx, ang=90 * 0 + (0 if sx > 0 else 180) + 30 * 0)
        # raked back legs
        pts = [V(sx * (w / 2 - 0.07), -D / 2 + 0.08, 0.17), V(sx * (w / 2 - 0.07), -D / 2 + 0.065, 0.1), V(sx * (w / 2 - 0.065), -D / 2 + 0.04, 0.0)]
        tube_f(f, M['wood_dark'], pts, [0.022, 0.017, 0.012], 8, (0.48, 0.3, 0.2))
    # skirt rail + base
    cushion(M['fabric_wool'], FM @ Matrix.Translation((0, 0, 0.215)), (w, D, 0.12), n=7, cuts=None, dens=0.08, pipe=0.0065, pipe_col=pcol, cfn=cf, seed=11, wrinkle=0.001, pipe_top=True, pipe_bot=True)
    # arms (rolled, lower) + wings
    for s_ in (-1, 1):
        ax = s_ * (w / 2 - 0.085)
        cushion(M['fabric_wool'], FM @ Matrix.Translation((ax, 0.04, 0.44)), (0.17, D - 0.16, 0.38), n=4.0, cuts=None, dens=0.065, cfn=cf, seed=12 + s_, wrinkle=0.002, inflate=0.2)
        # arm cap roll
        rl = FM @ Matrix.Translation((ax + s_ * 0.0, 0.05, 0.63)) @ rotm((90, 0, 0))
        lathe(M['fabric_wool'], None, [(0.001, -D / 2 + 0.1), (0.07, -D / 2 + 0.115), (0.082, -D / 2 + 0.17), (0.085, D / 2 - 0.2), (0.07, D / 2 - 0.12), (0.001, D / 2 - 0.1)], seg=22, cfn=cf, M=rl, cap=False)
        # wing: slab rising from the back sides with outward flare
        wm = FM @ Matrix.Translation((s_ * (w / 2 - 0.07), -D / 2 + 0.16, 0.78)) @ rotm((-6, 0, s_ * 8)) @ rotm((0, 0, 0))
        cushion(M['fabric_wool'], wm, (0.11, 0.3, 0.6), n=4.0, cuts=None, dens=0.06, cfn=cf, seed=14 + s_, wrinkle=0.0015, inflate=0.1)
    # back (tufted, tall)
    tf, pts_ = tuft_diamond(3, 4, 0.2, 0.15, 0.045, sig=0.03, fold=0.5, fw=0.022, oy=0.0)
    bk = FM @ Matrix.Translation((0, -D / 2 + 0.115, 0.76)) @ rotm((-12, 0, 0)) @ rotm((-90, 0, 0))
    bw_, bh_, bt_ = w - 0.2, 0.78, 0.17
    cushion(M['fabric_wool'], bk, (bw_, bh_, bt_), n=5.5, cuts=(14, 18, 2), subsurf=True, tuft=tf, cfn=cf, seed=15, wrinkle=0.001, inflate=0.1, crown=0.0)
    for (x, y) in pts_:
        if abs(x) < bw_ / 2 - 0.05 and abs(y) < bh_ / 2 - 0.05:
            q = bk @ V(x, y, bt_ / 2 - 0.03 + 0.001)
            button(M['fabric_wool'], q, bk.to_3x3() @ V(0, 0, 1), pcol, 0.0105)
    # seat cushion + stud rows
    cl = fab(base, 0.05, 8, 33)
    cushion(M['fabric_wool'], FM @ Matrix.Translation((0, 0.08, 0.385)), (w - 0.2, 0.6, 0.15), n=4.2, cuts=None, dens=0.052, crown=0.25, stitch=True, pipe=0.006, pipe_col=pcol, cfn=cl, seed=33, wrinkle=0.002, inflate=0.1)
    # nailhead rows along the front skirt and arm fronts
    nailhead_row(f, [V(-w / 2 + 0.05 + k * (w - 0.1) / 17, D / 2 + 0.0, 0.2) for k in range(18)], 0.0045)
    for s_ in (-1, 1):
        nailhead_row(f, [V(s_ * (w / 2 - 0.085) + 0.07 * math.cos(a), D / 2 - 0.12 + 0.0, 0.45 + 0.07 * math.sin(a)) for a in [i * TAU / 12 for i in range(12)]], 0.004) if False else None
        nailhead_row(f, [V(s_ * (w / 2 + 0.0) + 0.0, 0.2 + k * 0.045, 0.2) for k in range(5)], 0.0042) if False else None
    # lumbar scatter pillow (blue-grey) with piping
    pillow_scatter(FM @ Matrix.Translation((0.16, -0.06, 0.64)) @ rotm((-26, 0, -14)), 0.38, '#7d8e9c', 'dots', 8)
    armchair_throw(f, w, D)
    collider_f(f, w + 0.02, D + 0.02, F_ + 1.05)
    return f


def armchair_teal(pos, rot, w=0.84):
    """wrap-around tub chair, teal wool, deep diamond tufting on a curved back, rolled arms, piping, brass studs, turned legs"""
    f = Fr(pos, rot, F_)
    D = 0.86
    base = '#4f8587'
    cf = fab(base, 0.07, 8, 12)
    pcol = shade(C(base), 0.62)
    cpf = fab(pcol, 0.05, 8, 5)
    FM = f.M
    FAB = M['fabric_wool']
    for sx in (-1, 1):
        for sy in (-1, 1):
            turned_foot(f, sx * (w / 2 - 0.07), sy * (D / 2 - 0.07), 0.15, 0.03, 'wood_walnut', (0.4, 0.26, 0.18), 'taper' if sy > 0 else 'bun')
    cushion(FAB, FM @ Matrix.Translation((0, 0, 0.225)), (w, D, 0.15), n=8, cuts=None, dens=0.08, pipe=0.0065, pipe_col=pcol, cfn=cf, seed=51, wrinkle=0.001)
    # curved, tufted back (bent around the sitter)
    R = 0.40
    arc = 1.2
    tf, pts_ = tuft_diamond(6, 4, 0.205, 0.125, 0.058, sig=0.032, fold=0.5, fw=0.024)
    y0 = -D / 2 + 0.07
    bk = FM @ Matrix.Translation((0, y0, 0.60)) @ rotm((-90, 0, 0))
    cushion(FAB, bk, (arc, 0.52, 0.17), n=7.0, cuts=(24, 12, 2), subsurf=True, tuft=tf, cfn=cf, seed=15, wrinkle=0.001, inflate=0.05, bend=R, pipe=0.006, pipe_col=pcol, pipe_bot=False)
    for (x, y) in pts_:
        if abs(x) < arc / 2 - 0.05 and abs(y) < 0.52 / 2 - 0.05:
            lz = 0.17 / 2 - 0.05 + 0.001
            th = x / R
            rr_ = R - lz
            lp = V(rr_ * math.sin(th), y, R - rr_ * math.cos(th))
            q = bk @ lp
            nrm = bk.to_3x3() @ V(-math.sin(th), 0, math.cos(th))
            button(FAB, q, nrm, pcol, 0.0105)
    # arms: low rolled arms joining the back
    for s_ in (-1, 1):
        ax = s_ * (w / 2 - 0.085)
        cushion(FAB, FM @ Matrix.Translation((ax, 0.06, 0.39)), (0.17, D - 0.22, 0.34), n=6, cuts=None, dens=0.065, cfn=cf, seed=12 + s_, wrinkle=0.0015, inflate=0.1)
        r0 = 0.07
        rl = FM @ Matrix.Translation((ax + s_ * 0.005, 0.06, 0.585)) @ rotm((-90, 0, 0))
        Lh = (D - 0.22) / 2
        lathe(FAB, None, [(0.001, -Lh), (r0 * 0.7, -Lh + 0.002), (r0 * 0.96, -Lh + 0.012), (r0, -Lh + 0.03), (r0 * 1.005, 0.0), (r0, Lh - 0.03), (r0 * 0.96, Lh - 0.012), (r0 * 0.7, Lh - 0.002), (0.001, Lh)], seg=26, cfn=cf, M=rl, cap=False)
        sc = FM @ Matrix.Translation((ax + s_ * 0.005, 0.06 + Lh - 0.004, 0.585)) @ Matrix.Rotation(math.radians(-90), 4, 'X')
        scroll_disc(FAB, sc, r0 * 0.93, r0 * 0.93, cf, pcol, cpf, 9, s_)
    # seat cushion
    cl = fab(base, 0.05, 8, 53)
    cushion(FAB, FM @ Matrix.Translation((0, 0.075, 0.395)), (w - 0.2, 0.6, 0.17), n=4.5, cuts=None, dens=0.052, crown=0.26, stitch=True, pipe=0.0065, pipe_col=pcol, cfn=cl, seed=53, wrinkle=0.002, inflate=0.1)
    nailhead_row(f, [V(-w / 2 + 0.05 + k * (w - 0.1) / 17, D / 2 + 0.0, 0.215) for k in range(18)], 0.0045)
    pillow_scatter(FM @ Matrix.Translation((-0.1, -0.05, 0.62)) @ rotm((-28, 0, 12)), 0.36, '#d8b25a', 'stripe', 31)
    collider_f(f, w + 0.02, D + 0.02, F_ + 0.9)
    return f
