"""Bed linens via Blender cloth simulation: bottom sheet, pillows (pressure), patchwork quilt (+puff, stitching, tassels),
turned-down sheet cuff, plus embroidery ribbons projected on the simulated surfaces. All in bed-local coordinates."""
from bd_lib import *
from bd_cloth import *
import bd_bed
import bd_lib

QX, QY = 2.09, 1.665          # quilt size (11 x 9 squares)
NCX, NCY = 11, 9
QS = 5
Q_Y0 = -0.20                  # head edge of the quilt (local y)


def ribbon_bm(surf, polylines, width=0.0026, lift=0.0012, z0=3.0, dash=None):
    """Project 2D (x,y) polylines onto surf (top-down raycast) -> flat ribbon bmesh. dash=(on,off) metres."""
    import bisect
    bm = bmesh.new()
    for pl in polylines:
        pts = [Vector((p[0], p[1], 0)) for p in pl]
        cum = [0.0]
        for a_, b_ in zip(pts[:-1], pts[1:]):
            cum.append(cum[-1] + (b_ - a_).length)
        total = cum[-1]
        if total < 1e-6:
            continue

        def at(s):
            i = min(max(bisect.bisect_right(cum, s) - 1, 0), len(pts) - 2)
            seg = cum[i + 1] - cum[i]
            t = 0 if seg < 1e-9 else (s - cum[i]) / seg
            return pts[i] + (pts[i + 1] - pts[i]) * t
        if dash:
            on, off = dash
            runs = []
            s0 = 0.0
            while s0 < total - 1e-6:
                s1 = min(s0 + on, total)
                runs.append([at(s0), at(s1)])
                s0 += on + off
        else:
            runs = [pts]
        for sg in runs:
            ring = []
            for i, p in enumerate(sg):
                h, n = surf.hit(p.x, p.y, z0)
                if h is None:
                    ring = []
                    break
                t = (sg[min(i + 1, len(sg) - 1)] - sg[max(i - 1, 0)]); t.z = 0
                if t.length < 1e-9:
                    t = Vector((1, 0, 0))
                t.normalize()
                s_ = t.cross(n)
                if s_.length < 1e-6:
                    ring = []
                    break
                s_.normalize()
                base = h + n * lift
                ring.append((bm.verts.new(base - s_ * width / 2), bm.verts.new(base + s_ * width / 2)))
            for (a0, a1), (b0, b1) in zip(ring[:-1], ring[1:]):
                try:
                    bm.faces.new([a0, b0, b1, a1]).smooth = True
                except ValueError:
                    pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for fc in bm.faces:
        if fc.normal.z < 0:
            fc.normal_flip()
    return bm


def ribbon3d(polys, width=0.0026, lift=0.0014, dash=None, normal_fn=None):
    """polys: list of (points[Vector], normals[Vector]) -> flat ribbons following the 3D polyline (e.g. a cloth grid line)."""
    import bisect
    bm = bmesh.new()
    for pts, nrm in polys:
        pts = [Vector(p) for p in pts]; nrm = [Vector(n) for n in nrm]
        cum = [0.0]
        for a_, b_ in zip(pts[:-1], pts[1:]):
            cum.append(cum[-1] + (b_ - a_).length)
        total = cum[-1]
        if total < 1e-6:
            continue

        def at(s):
            i = min(max(bisect.bisect_right(cum, s) - 1, 0), len(pts) - 2)
            seg = cum[i + 1] - cum[i]
            t = 0 if seg < 1e-9 else (s - cum[i]) / seg
            return pts[i] + (pts[i + 1] - pts[i]) * t, (nrm[i] + (nrm[i + 1] - nrm[i]) * t).normalized(), i
        runs = []
        if dash:
            on, off = dash
            s0 = 0.0
            while s0 < total - 1e-6:
                s1 = min(s0 + on, total)
                a_, b_ = at(s0), at(s1)
                runs.append([a_, b_])
                s0 += on + off
        else:
            runs = [[(pts[i], nrm[i], i) for i in range(len(pts))]]
        for sg in runs:
            ring = []
            for i, (p, n, _) in enumerate(sg):
                t = sg[min(i + 1, len(sg) - 1)][0] - sg[max(i - 1, 0)][0]
                s_ = t.cross(n)
                if s_.length < 1e-9:
                    continue
                s_.normalize()
                base = p + n * lift
                ring.append((bm.verts.new(base - s_ * width / 2), bm.verts.new(base + s_ * width / 2)))
            for (a0, a1), (b0, b1) in zip(ring[:-1], ring[1:]):
                try:
                    bm.faces.new([a0, b0, b1, a1]).smooth = True
                except ValueError:
                    pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def sheet_sim():
    nx, ny = 50, 56
    sx, sy = 2.0, 2.2
    yc = 0.08

    def fz(x, y):
        z = 0.675 + 0.012 * math.sin(x * 11 + y * 4) + 0.02 * fbm(x * 1.5, y * 1.5, 1, 2.4, 5, 3)
        return (x, y + yc, z)
    v, fcs, uv = grid(nx, ny, sx, sy, fz)
    cols = bd_bed.proxies()
    res = simulate('bd_sheet', v, fcs, frames=110, colliders=cols, preset='linen', collision_dist=0.006)
    for c in cols:
        c.free()
    return res, fcs, uv


def pillow_shape(sx, sy, sz, n=12, nz_=9, seed=0):
    """closed pillow: rounded flat box (superellipsoid-ish), returns verts, faces (quads) with outward normals"""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=n - 1, use_grid_fill=True)
    for v in bm.verts:
        p = v.co.copy()
        e = 4.0
        L = (abs(p.x) ** e + abs(p.y) ** e + abs(p.z) ** e) ** (1 / e)
        q = p / L if L > 1e-6 else p
        edge = max(abs(q.x), abs(q.y))
        q.z *= 1.0 - 0.62 * edge ** 4
        v.co = Vector((q.x * sx / 2, q.y * sy / 2, q.z * sz / 2))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    verts = np.array([tuple(v.co) for v in bm.verts], np.float32)
    idx = {v: i for i, v in enumerate(bm.verts)}
    faces = [tuple(idx[v] for v in f.verts) for f in bm.faces]
    bm.free()
    return verts, faces


def mesh_volume(v, faces):
    vol = 0.0
    for f in faces:
        for k in range(1, len(f) - 1):
            a, b, c = v[f[0]], v[f[k]], v[f[k + 1]]
            vol += np.dot(a, np.cross(b, c)) / 6.0
    return abs(vol)


def pillows_sim(sheet_v, sheet_f):
    """three pillows resting on the sheet against the headboard. returns list of dicts"""
    specs = [
        dict(name='bd_pillowA', size=(0.64, 0.42, 0.16), pos=(-0.38, -0.66, 0.0), rz=6, tilt=-14),
        dict(name='bd_pillowB', size=(0.64, 0.42, 0.16), pos=(0.38, -0.67, 0.0), rz=-5, tilt=-12),
        dict(name='bd_pillowC', size=(0.42, 0.34, 0.12), pos=(0.1, -0.42, 0.0), rz=-14, tilt=-34),
    ]
    out = []
    cols_base = bd_bed.proxies()
    sheet_col = (sheet_v, sheet_f)
    prev = []
    for sp in specs:
        sx, sy, sz = sp['size']
        v0, fcs = pillow_shape(sx, sy, sz)
        # place: rotate then lift above the sheet
        Mx = Matrix.Translation((sp['pos'][0], sp['pos'][1], 0.0)) @ rotm((0, 0, sp['rz'])) @ rotm((sp['tilt'], 0, 0))
        v1 = np.array([tuple(Mx @ Vector(p)) for p in v0], np.float32)
        S_ = surf_arrays(sheet_v, sheet_f)
        xs_ = np.linspace(v1[:, 0].min(), v1[:, 0].max(), 9); ys_ = np.linspace(v1[:, 1].min(), v1[:, 1].max(), 7)
        zmax = max((S_.z(x_, y_) or 0.0) for x_ in xs_ for y_ in ys_)
        for (pv_, pf_) in prev:
            Sp_ = surf_arrays(pv_, pf_)
            zmax = max([zmax] + [(Sp_.z(x_, y_) or 0.0) for x_ in xs_ for y_ in ys_])
        v1[:, 2] += zmax + 0.016 - v1[:, 2].min()

        def extra(cm):
            s_ = cm.settings
            s_.use_pressure = True
            s_.use_pressure_volume = False
            s_.uniform_pressure_force = 7.0
        cols = [c for c in bd_bed.proxies()] + [sheet_col] + [(p[0], p[1]) for p in prev]
        res = simulate(sp['name'], v1, fcs, frames=70, colliders=cols, preset='pillow', collision_dist=0.006, self_coll=False, extra=extra)
        for c in cols:
            if isinstance(c, bmesh.types.BMesh):
                c.free()
        out.append(dict(name=sp['name'], v=res, f=fcs, spec=sp))
        prev.append((res, fcs))
    return out


def quilt_sim(sheet, pillows):
    nx, ny = NCX * QS, NCY * QS

    def fz(x, y):
        return (x, y + Q_Y0 + QY / 2, 0.84 + 0.01 * math.sin(x * 9) + 0.012 * fbm(x, y, 3, 3, 6, 2))
    v, fcs, uv = grid(nx, ny, QX, QY, fz)
    uv = np.array([(a / QX, b / QY) for a, b in uv], np.float32)
    cols = bd_bed.proxies() + [(sheet[0], sheet[1])] + [(p['v'], p['f']) for p in pillows]
    res = simulate('bd_quilt', v, fcs, frames=130, colliders=cols, preset='quilt', collision_dist=0.008, self_coll=False)
    for c in cols:
        if isinstance(c, bmesh.types.BMesh):
            c.free()
    return res, fcs, uv


def puff_quilt(qv, qf):
    qvv = qv.copy()
    nrm = vertex_normals(qvv, qf)
    nx, ny = NCX * QS, NCY * QS
    for j in range(ny + 1):
        for i in range(nx + 1):
            k = j * (nx + 1) + i
            u = (i / QS) % 1.0; w = (j / QS) % 1.0
            bump = (math.sin(math.pi * u) * math.sin(math.pi * w)) ** 0.7
            if i in (0, nx) or j in (0, ny):
                bump = 0
            border = (i < QS or i > nx - QS or j < QS or j > ny - QS)
            qvv[k] += nrm[k] * bump * (0.006 if border else 0.011) * (1 if nrm[k, 2] > 0 else 0)
    return qvv


def cuff_sim(quilt_v, quilt_f, sheet, pillows):
    """turned-down sheet: strip over the quilt's head edge, rounded fold toward the head. top layer pinned on the quilt."""
    surf = surf_arrays(quilt_v, quilt_f)
    nxq = NCX * QS + 1
    ymin = float(min(quilt_v[i, 1] for i in range(nxq)))
    nx = 40
    W = 2.0
    L_flat = 0.30
    Rr = 0.022
    drop = 0.06
    ys = ymin + 0.045
    prof = []
    n1 = 14; n2 = 6; n3 = 8
    for i in range(n1 + 1):
        prof.append((ys + L_flat - L_flat * i / n1, 0.0))
    for i in range(1, n2 + 1):
        a = math.pi / 2 * i / n2
        prof.append((ys - Rr * math.sin(a), -Rr * (1 - math.cos(a))))
    for i in range(1, n3 + 1):
        prof.append((ys - Rr, -Rr - drop * i / n3))
    ny = len(prof) - 1
    verts, pins = [], []
    xs = [-W / 2 + W * i / nx for i in range(nx + 1)]
    for j, (py, dz) in enumerate(prof):
        for i, x in enumerate(xs):
            yq = max(py, ymin + 0.02)
            z = surf.z(x, yq, 3.0)
            if z is None:
                z = 0.62
            z += 0.0055
            wr = 0.003 * math.sin(x * 15 + j * 0.7) + 0.0025 * nz(x, py, 0, 10, 2)
            if dz >= 0:
                verts.append((x, py, z + wr)); pins.append(j * (nx + 1) + i)
            else:
                verts.append((x, py, z + dz))
    faces = []
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    cum = [0.0]
    for t in range(ny):
        cum.append(cum[-1] + math.hypot(prof[t + 1][0] - prof[t][0], prof[t + 1][1] - prof[t][1]))
    uv = np.array([(xs[k % (nx + 1)] + W / 2, cum[k // (nx + 1)]) for k in range(len(verts))], np.float32)
    verts = np.array(verts, np.float32)
    cols = bd_bed.proxies() + [(sheet[0], sheet[1]), (quilt_v, quilt_f)]
    res = simulate('bd_cuff', verts, faces, pins=pins, frames=50, colliders=cols, preset='linen', collision_dist=0.004, damping_scale=2.0)
    for c in cols:
        if isinstance(c, bmesh.types.BMesh):
            c.free()
    return res, faces, uv


def _cnt(tag):
    out = {}
    for mn, (bm, mat) in bd_lib.ACC.items():
        out[mn] = sum(len(fc.verts) - 2 for fc in bm.faces)
    print('LIN', tag, out)


def build_linens(f, quick=False):
    """run all sims (cached), push meshes into the accumulators. Returns dict with surfaces for placing props."""
    info = {}
    sv, sf, suv = sheet_sim()
    pillows = pillows_sim(sv, sf)
    qv, qf, quv = quilt_sim((sv, sf), pillows)
    qvv = puff_quilt(qv, qf)
    cv, cf, cuv = cuff_sim(qvv, qf, (sv, sf), pillows)

    # ---------------- sheet (linen) : thin solid
    qy_head = float(min(qv[i, 1] for i in range(NCX * QS + 1)))
    bm2 = cloth_to_bm(sv, sf, suv, skip=lambda c: c[1] > qy_head + 0.07 and c[2] > 0.585 and abs(c[0]) < 0.74)
    f.put(M['linen'], bm2, cfn=lambda p: (0.96 + 0.02 * nz(p.x * 3, p.y * 3, p.z * 3), 0.94 + 0.02 * nz(p.x * 3, p.y * 3, p.z * 3), 0.88), skip_down=False)
    bm2.free()

    _cnt('sheet')
    # ---------------- pillows with cases
    case_cols = [(0.96, 0.94, 0.88), (0.96, 0.94, 0.88), (0.74, 0.80, 0.86)]
    pil_surfs = []
    for k, p in enumerate(pillows):
        sx, sy, sz = p['spec']['size']
        v = p['v'].copy()
        fcs = p['f']
        ctr = v.mean(axis=0)
        loc = v - ctr
        n_ = vertex_normals(v, fcs)
        r2 = ((loc[:, 0] / (sx * 0.28)) ** 2 + (loc[:, 1] / (sy * 0.3)) ** 2)
        dent = 0.028 * np.exp(-r2) * np.clip(n_[:, 2], 0, 1) ** 1.5
        for i in range(len(v)):
            wr = 0.004 * nz(v[i, 0], v[i, 1], v[i, 2], 14, k)
            v[i] -= n_[i] * (dent[i] - wr) * (1 if n_[i, 2] > -0.2 else 0)
        uv = np.zeros((len(v), 2), np.float32)
        for i in range(len(v)):
            uv[i] = (v[i, 0] * 1.0 + k * 0.3, v[i, 1] * 1.0 + v[i, 2] * 0.7)
        bm = cloth_to_bm(v, fcs, uv)
        cc = case_cols[k]
        f.put(M['linen'], bm, cfn=lambda p, cc=cc: (cc[0] * (0.97 + 0.03 * nz(p.x * 4, p.y * 4, p.z * 4)), cc[1] * (0.97 + 0.03 * nz(p.x * 4, p.y * 4, p.z * 4)), cc[2]), skip_down=True)
        bm.free()
        ps = surf_arrays(v, fcs)
        pil_surfs.append((ps, v, p['spec']))
        thread = (0.22, 0.34, 0.5) if k == 2 else (0.55, 0.22, 0.2)
        cx, cy = ctr[0], ctr[1]
        rz = math.radians(p['spec']['rz'])

        def Pxy(a, b):
            return (cx + a * math.cos(rz) - b * math.sin(rz), cy + a * math.sin(rz) + b * math.cos(rz))

        def dense(pl, step=0.006):
            out_ = []
            for a, b in zip(pl[:-1], pl[1:]):
                L = math.hypot(b[0] - a[0], b[1] - a[1]); m = max(int(L / step), 1)
                for t in range(m):
                    out_.append((a[0] + (b[0] - a[0]) * t / m, a[1] + (b[1] - a[1]) * t / m))
            out_.append(pl[-1])
            return out_
        inset = 0.045
        hx, hy = sx / 2 - inset, (sy / 2 - inset) * math.cos(math.radians(abs(p['spec']['tilt'])))
        rect = [Pxy(-hx, -hy), Pxy(hx, -hy), Pxy(hx, hy), Pxy(-hx, hy), Pxy(-hx, -hy)]
        rb = ribbon_bm(ps, [dense(rect)], width=0.0028, lift=0.0010, dash=(0.011, 0.005))
        f.put(M['linen'], rb, col=thread, uvs=TEXSC['linen'], skip_down=False); rb.free()
        pl_list = []
        for sg in (-1, 1):
            vine = [(sg * (0.02 + 0.2 * t), 0.025 * math.sin(t * 9.0)) for t in np.linspace(0, 1, 30)]
            vine = [Pxy(a * min(1, sx / 0.6), b) for a, b in vine]
            pl_list.append(vine)
            for t in (0.25, 0.5, 0.8):
                a0 = sg * (0.02 + 0.2 * t); b0 = 0.025 * math.sin(t * 9.0)
                for side in (-1, 1):
                    leaf = [(a0 + sg * 0.01 * u, b0 + side * 0.03 * math.sin(u * math.pi * 0.5) * u) for u in np.linspace(0, 1, 6)]
                    leaf += [(a0 + sg * (0.01 + 0.01 * (1 - u)), b0 + side * (0.03 - 0.01 * u)) for u in np.linspace(0, 1, 4)]
                    pl_list.append([Pxy(a * min(1, sx / 0.6), b) for a, b in leaf])
        for pet in range(8):
            a = pet * TAU / 8
            pts_ = [(0.026 * math.cos(a) * u, 0.026 * math.sin(a) * u) for u in np.linspace(0.15, 1.0, 5)]
            pl_list.append([Pxy(a_, b_) for a_, b_ in pts_])
        pl_list = [dense(pl, 0.006) for pl in pl_list]
        rb = ribbon_bm(ps, pl_list, width=0.0032, lift=0.0011)
        f.put(M['linen'], rb, col=(thread[0] * 0.95, thread[1] * 0.95, thread[2] * 0.95), uvs=TEXSC['linen'], skip_down=False); rb.free()
    info['pillows'] = pil_surfs
    _cnt('pillows')

    # ---------------- quilt: solidify, stitches, tassels
    cw, ch = QX / NCX, QY / NCY
    nx, ny = NCX * QS, NCY * QS
    qb = solid_bm(qvv, qf, quv, 0.014, -1.0, skip_bottom=lambda c: c[2] > 0.585 and abs(c[0]) < 0.74 and c[1] < 0.93)
    f.put(M['quilt'], qb, col=(1.0, 1.0, 1.0), uvs=1.0, skip_down=False)
    qb.free()
    qsurf = surf_arrays(qvv, qf)
    info['quilt_surf'] = qsurf
    # stitches along patch seams (quilting in the ditch) following the cloth grid lines
    qn = vertex_normals(qvv, qf)
    nxq = nx + 1
    polys = []
    for ci in range(1, NCX):
        i = ci * QS
        idx = [j * nxq + i for j in range(ny + 1)]
        polys.append(([qvv[k] for k in idx], [qn[k] for k in idx]))
    for cj in range(1, NCY):
        j = cj * QS
        idx = [j * nxq + i for i in range(nx + 1)]
        polys.append(([qvv[k] for k in idx], [qn[k] for k in idx]))
    # outer binding stitch line, 1 cell-sixth in from the hem
    for (idx) in ([j * nxq + 2 for j in range(ny + 1)], [j * nxq + nx - 2 for j in range(ny + 1)], [(ny - 2) * nxq + i for i in range(nx + 1)]):
        polys.append(([qvv[k] for k in idx], [qn[k] for k in idx]))
    rb = ribbon3d(polys, width=0.0026, lift=0.0016, dash=(0.016, 0.011))
    f.put(M['wool'], rb, col=(0.93, 0.9, 0.82), uvs=TEXSC['wool'], skip_down=False); rb.free()
    # tassels along the free hem (all but the head edge)
    nxq = nx + 1
    hem = []
    for i in range(nx + 1):
        hem.append(Vector(qvv[ny * nxq + i]))             # foot edge
    sidesL = [Vector(qvv[j * nxq]) for j in range(ny, -1, -1)]
    sidesR = [Vector(qvv[j * nxq + nx]) for j in range(0, ny + 1)]
    path = sidesL + hem + sidesR
    # resample along path every ~0.055 m
    acc = 0.0
    pts = []
    for a, b in zip(path[:-1], path[1:]):
        L = (b - a).length
        acc += L
        if acc >= 0.1:
            pts.append(b.copy()); acc = 0.0
    tcols = [(0.62, 0.2, 0.18), (0.86, 0.68, 0.28), (0.18, 0.26, 0.45), (0.93, 0.89, 0.78), (0.45, 0.58, 0.42)]
    for i, p in enumerate(pts):
        if p.z > 0.9 or p.z < 0.15:
            continue
        c = tcols[i % len(tcols)]
        base = Vector((p.x, p.y, p.z - 0.012))
        f.lathe(M['wool'], base + Vector((0, 0, -0.004)), [(0.0005, 0.0), (0.0055, -0.004), (0.0045, -0.012), (0.009, -0.022), (0.0095, -0.04), (0.007, -0.054), (0.0015, -0.058)], seg=6, cap=False, col=c)
    _cnt('quilt+tassels')
    # ---------------- turned-down sheet cuff
    bm2 = cloth_to_bm(cv, cf, cuv)
    f.put(M['linen'], bm2, cfn=lambda p: (0.97, 0.95, 0.9), skip_down=False)
    bm2.free()
    cn = vertex_normals(cv, cf)
    ncx = 40 + 1
    polys = []
    for jr in (2, 3):
        idx = [jr * ncx + i for i in range(ncx)]
        polys.append(([cv[k] for k in idx], [cn[k] for k in idx]))
    rb = ribbon3d(polys, width=0.0025, lift=0.0016, dash=(0.007, 0.003))
    f.put(M['linen'], rb, col=(0.55, 0.22, 0.2), uvs=TEXSC['linen'], skip_down=False); rb.free()
    cs = surf_arrays(cv, cf)
    _cnt('cuff')
    info['cuff_surf'] = cs
    info['qv'] = qvv; info['qf'] = qf
    return info


def folded_blanket(f, qsurf, cx=0.02, cy=0.60):
    """folded wool blanket (4 layers) laid across the foot of the quilt, conformed to the cloth surface, with fringe"""
    rg = random.Random(8)
    w0, d0 = 0.64, 0.40
    zs = []
    for dx in (-w0 / 2, w0 / 2):
        for dy in (-d0 / 2, d0 / 2):
            z = qsurf.z(cx + dx, cy + dy)
            zs.append(z if z is not None else 0.66)
    zc = max(zs)
    tilt_x = math.degrees(math.atan2((zs[2] + zs[3]) / 2 - (zs[0] + zs[1]) / 2, d0)) * 0.5     # across y
    tilt_y = math.degrees(math.atan2((zs[1] + zs[3]) / 2 - (zs[0] + zs[2]) / 2, w0)) * -0.5
    cols = [(0.55, 0.14, 0.12), (0.82, 0.74, 0.55), (0.55, 0.14, 0.12), (0.82, 0.74, 0.55)]
    for k in range(4):
        w = w0 - 0.012 * k
        d = d0 - 0.008 * k
        z = zc + 0.0075 + k * 0.0125
        rz = rg.uniform(-2.5, 2.5)
        Mx = f.M @ Matrix.Translation((cx + rg.uniform(-0.006, 0.006), cy, z)) @ rotm((tilt_x * 0 - 0.0, 0, rz))
        def cfn(p, k=k):
            q = f.M.inverted() @ p
            stripe = abs(abs(q.x - cx) - (w0 / 2 - 0.05)) < 0.012 or abs(abs(q.x - cx) - (w0 / 2 - 0.085)) < 0.006
            c = (0.17, 0.2, 0.3) if stripe else (0.74, 0.62, 0.42) if k % 2 == 0 else (0.62, 0.2, 0.17)
            n = 1 + 0.05 * nz(q.x * 18, q.y * 18, k)
            return (c[0] * n, c[1] * n, c[2] * n)
        box(M['wool'], None, (w, d, 0.0125), Mx=Mx, bev=0.0055, seg=2, cfn=cfn, g=0, skip_down=False)
    # fringe along the free short edge (toward the foot rail)
    for i in range(22):
        x = cx - w0 / 2 + 0.02 + i * (w0 - 0.04) / 21
        box(M['wool'], None, (0.007, 0.03, 0.002), Mx=f.M @ Matrix.Translation((x, cy + d0 / 2 + 0.012, zc + 0.012 + 0.005)) @ rotm((rg.uniform(-18, -8), 0, rg.uniform(-6, 6))), bev=0, col=(0.85, 0.78, 0.6), g=1, skip_down=False)
