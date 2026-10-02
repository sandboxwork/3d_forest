"""vl_lib: core helpers for the villager characters (materials, finishing, head/face construction).
Authoring: Z-up, front = -Y, left = +X, meters.  Parts are built in WORLD coordinates and finished with
finish_part() which moves the origin to the pivot and parents it.
"""
import sys
sys.path.insert(0, '/shared/river/assets/blender')
from animlib import *
from mathutils.bvhtree import BVHTree
import bmesh

# ------------------------------------------------------------------ materials
MATN = ['skin', 'lips', 'mouth', 'teeth', 'hair', 'cloth_main', 'cloth_alt', 'cloth_accent', 'shoes',
        'eye_white', 'iris', 'pupil', 'metal', 'leather', 'wood', 'straw', 'brass', 'bread', 'iron']
MI = {n: i for i, n in enumerate(MATN)}
MATS = {}
TILES = {}   # material index -> uv tile size (m)
STATE = {}


def mk_mats(skin='#d8a27f', hair='#5b3f2a', main='#c9c0a8', alt='#7d6a55', acc='#a04a3c',
            main_tex=('pbr_fabric_linen', 0.25), alt_tex=('pbr_fabric_wool', 0.3), iris='#4d6f8f'):
    spec = {
        'skin': dict(color=skin, rough=0.55),
        'lips': dict(color='#b36657', rough=0.5),
        'mouth': dict(color='#3a1512', rough=0.7),
        'teeth': dict(color='#e8e0d0', rough=0.35),
        'hair': dict(color=hair, rough=0.65),
        'cloth_main': dict(color=main, rough=0.92, tex=main_tex),
        'cloth_alt': dict(color=alt, rough=0.95, tex=alt_tex),
        'cloth_accent': dict(color=acc, rough=0.9, tex=('pbr_fabric_linen', 0.25)),
        'shoes': dict(color='#5a3d28', rough=0.65, tex=('pbr_leather', 0.3)),
        'eye_white': dict(color='#ece8e0', rough=0.12),
        'iris': dict(color=iris, rough=0.15),
        'pupil': dict(color='#050505', rough=0.1),
        'metal': dict(color='#6b6e72', rough=0.45, metal=0.9),
        'leather': dict(color='#6a4630', rough=0.7, tex=('pbr_leather', 0.3)),
        'wood': dict(color='#8a6a45', rough=0.75, tex=('pbr_wood_oak', 0.5)),
        'straw': dict(color='#d3b46a', rough=0.9, tex=('pbr_wicker', 0.2)),
        'brass': dict(color='#b08d3c', rough=0.35, metal=0.9),
        'bread': dict(color='#b47f3e', rough=0.85),
        'iron': dict(color='#3b3d40', rough=0.5, metal=0.85, tex=('pbr_iron', 0.4)),
    }
    for n in MATN:
        s = spec[n]
        t = s.get('tex')
        m = vcol_mat(n, s['color'], rough=s['rough'], metal=s.get('metal', 0.0), tex=(t[0] if t else None), uvscale=1.0)
        if n in ('cloth_main', 'cloth_alt', 'cloth_accent', 'straw', 'leather'):
            m['double'] = True
        MATS[n] = m
        TILES[MI[n]] = t[1] if t else 1.0
    return MATS


def setm(bm, name):
    for f in bm.faces:
        f.material_index = MI[name]
    return bm


def M(bm, name):
    return setm(bm, name)


def smooth(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def g2(x, z, x0, z0, sx, sz):
    return math.exp(-(((x - x0) / sx) ** 2 + ((z - z0) / sz) ** 2))


def noise3(p, f=1.0, seed=0):
    return mnoise.noise(V(p) * f + V((seed * 7.7, seed * 3.1, seed * 1.3)))


# --------------------------------------------------------------- vertex color / finishing
def std_color(p, n, mi):
    """Neutral (luminance) variation for recolorable materials; skin & eyes stay white."""
    name = MATN[mi]
    if name in ('skin', 'lips', 'mouth', 'teeth', 'eye_white', 'iris', 'pupil', 'metal', 'brass', 'iron'):
        return (1, 1, 1)
    k = 0.88 + 0.12 * (noise3(p, 9, 1) * 0.5 + 0.5) + 0.06 * noise3(p, 55, 2)
    if name == 'hair':
        hc = STATE.get('head_c', V(0, 0, 0))
        az = math.atan2(p.y - hc.y, p.x - hc.x)
        st = abs(noise3(V(az * 9.0, (p.z - hc.z) * 7.0, 0.3), 1, 3))
        k = 0.66 + 0.34 * (1 - st) ** 0.7 + 0.10 * noise3(p, 90, 4) - 0.1 * smooth(0.04, 0.12, p.z - hc.z)
        if p.z - hc.z < -0.03 and p.y < hc.y:      # beard: vertical strands
            st2 = abs(noise3(V(p.x * 150, p.y * 40, p.z * 16), 1, 6))
            k = 0.62 + 0.38 * (1 - st2) ** 0.8 + 0.08 * noise3(p, 120, 8)
    elif name == 'shoes':
        k = 0.85 + 0.15 * (noise3(p, 30, 5) * 0.5 + 0.5)
        if p.z < 0.022:
            k *= 0.6
    elif name in ('cloth_main', 'cloth_alt', 'cloth_accent'):
        # dust / wear toward the ground and slight vertical stripes of wear
        k *= 1.0 - 0.28 * smooth(0.5, 0.0, p.z) * (0.6 + 0.4 * (noise3(p, 8, 7) * 0.5 + 0.5))
    k = max(0.45, min(1.0, k))
    return (k, k * 0.985, k * 0.96)


def uv_project(bm):
    uvl = bm.loops.layers.uv.get('UVMap') or bm.loops.layers.uv.new('UVMap')
    bm.normal_update()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        tile = TILES.get(f.material_index, 1.0)
        for l in f.loops:
            p = l.vert.co
            if ax == 0:
                u, v = p.y, p.z
            elif ax == 1:
                u, v = p.x, p.z
            else:
                u, v = p.x, p.y
            l[uvl].uv = (u / tile, v / tile)


def paint_mat(bm, colorfn=None):
    bm.normal_update()
    lay = bm.verts.layers.color.get('Col') or bm.verts.layers.color.new('Col')
    fn = colorfn or std_color
    for v in bm.verts:
        mi = v.link_faces[0].material_index if v.link_faces else 0
        c = fn(v.co.copy(), v.normal.copy(), mi)
        v[lay] = (c[0], c[1], c[2], 1.0)


def finish_part(name, bm, pivot, parent=None, colorfn=None, nmap=None):
    uv_project(bm)
    paint_mat(bm, colorfn)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    for n in MATN:
        ob.data.materials.append(MATS[n])
    for p in me.polygons:
        p.use_smooth = True
    if nmap:
        vn = []
        for v in me.vertices:
            k = (round(v.co.x, 4), round(v.co.y, 4), round(v.co.z, 4))
            n = nmap.get(k)
            vn.append(tuple(n) if n is not None else tuple(v.normal))
        try:
            me.normals_split_custom_set_from_vertices(vn)
        except Exception as ex:
            print('custom normals failed', ex)
    bpy.context.view_layer.update()
    set_origin(ob, pivot)
    if parent is not None:
        set_parent(ob, parent)
    return ob


def displace(bm, fn):
    bm.normal_update()
    offs = [fn(v.co.copy(), v.normal.copy()) for v in bm.verts]
    for v, o in zip(bm.verts, offs):
        v.co += v.normal * o
    return bm


def translate(bm, vec):
    bmesh.ops.translate(bm, verts=bm.verts[:], vec=vec)
    return bm


def scale_about(bm, s, center=(0, 0, 0)):
    bmesh.ops.scale(bm, verts=bm.verts[:], vec=(s, s, s), space=Matrix.Translation(-V(center)) if False else Matrix.Identity(4))
    return bm


def rot_about(bm, axis, ang, center=(0, 0, 0)):
    bmesh.ops.rotate(bm, verts=bm.verts[:], cent=center, matrix=Matrix.Rotation(ang, 3, axis))
    return bm


def tube(pts, rw, rd=None, segs=12, res=3, caps=(True, True), power=2.0, cap_push=0.9):
    return fix_outward(loft(pts, rw, rd, segs=segs, res=res, up=(0, -1, 0), cap0=caps[0], cap1=caps[1], power=power, cap_push=cap_push))


def add_hem(bm, ring_start, segs, thick=0.004, liner=0.02, end=True):
    """Fold the open edge ring (verts ring_start..ring_start+segs) inward: thin rim + liner wall. Returns bm."""
    bm.verts.ensure_lookup_table()
    ring = [bm.verts[ring_start + j] for j in range(segs)]
    cen = sum((v.co for v in ring), V(0, 0, 0)) / segs
    # direction of the tube at this end, from neighbouring ring
    nxt = [bm.verts[ring_start + (-segs if end else segs) + j] for j in range(segs)]
    cen2 = sum((v.co for v in nxt), V(0, 0, 0)) / segs
    d = (cen - cen2).normalized()  # pointing out of the tube at this end
    r2 = []
    r3 = []
    for v in ring:
        rad = v.co - cen
        rad = rad - d * rad.dot(d)
        rn = rad.normalized()
        a = bm.verts.new(v.co + d * 0.0015 - rn * thick * 0.5)
        b = bm.verts.new(v.co - rn * thick - d * 0.0005)
        c = bm.verts.new(v.co - rn * thick - d * liner)
        r2.append((a, b, c))
    for j in range(segs):
        j2 = (j + 1) % segs
        v0, v1 = ring[j], ring[j2]
        a0, b0, c0 = r2[j]
        a1, b1, c1 = r2[j2]
        try:
            bm.faces.new((v0, v1, a1, a0))
            bm.faces.new((a0, a1, b1, b0))
            bm.faces.new((b0, b1, c1, c0))
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def fix_outward(bm):
    cen = sum((v.co for v in bm.verts), V(0, 0, 0)) / max(1, len(bm.verts))
    bm.normal_update()
    sc_ = 0.0
    for f in bm.faces:
        sc_ += f.normal.dot(f.calc_center_median() - cen) * f.calc_area()
    if sc_ < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    return bm


def cloth_tube(pts, rw, rd=None, segs=14, res=3, hem0=False, hem1=False, thick=0.004, liner=0.02, caps=(False, False), power=2.0, pre=None):
    n = len(pts)
    rd = rw if rd is None else rd
    bm = loft(pts, rw, rd, segs=segs, res=res, up=(0, -1, 0), cap0=caps[0], cap1=caps[1], power=power, cap_push=0.5)
    m = (n - 1) * res + 1
    if pre is not None:
        pre(bm)
    if hem0:
        add_hem(bm, 0, segs, thick, liner, end=False)
    if hem1:
        add_hem(bm, (m - 1) * segs, segs, thick, liner, end=True)
    return fix_outward(bm)


def box(center, size, rot=(0, 0, 0), bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]; v.co.y *= size[1]; v.co.z *= size[2]
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=bevel, segments=1, affect='EDGES')
    if any(rot):
        bmesh.ops.rotate(bm, verts=bm.verts[:], cent=(0, 0, 0), matrix=Matrix.Rotation(rot[2], 3, 'Z') @ Matrix.Rotation(rot[1], 3, 'Y') @ Matrix.Rotation(rot[0], 3, 'X'))
    bmesh.ops.translate(bm, verts=bm.verts[:], vec=center)
    return bm


def strand(pts, r0, r1, segs=5, res=2, up=(0, -1, 0)):
    """Tapered hair strand / rope: radius r0 at start to r1 at end."""
    n = len(pts)
    rr = [r0 + (r1 - r0) * (i / (n - 1)) ** 0.8 for i in range(n)]
    return loft(pts, rr, rr, segs=segs, res=res, up=up, cap0=False, cap1=True, cap_push=1.0)


# ------------------------------------------------------------------ HEAD / FACE
ROWS_Z = [0.118, 0.113, 0.105, 0.094, 0.080, 0.065, 0.051, 0.040, 0.030, 0.022, 0.014, 0.006, -0.002, -0.010, -0.018, -0.026,
          -0.034, -0.042, -0.049, -0.056, -0.062, -0.068, -0.0735, -0.079, -0.085, -0.091, -0.097, -0.103, -0.109, -0.1155]
Z_SLIT = -0.0735
_half = [4, 8, 12, 16, 20, 25, 30, 36, 42, 48, 55, 63, 72, 82, 92, 98, 110, 130, 150, 170]
COLS_DEG = [0] + _half + [180] + [-a for a in reversed(_half)]  # 0..180..-170 (periodic, -180 == 180)
JAW_PHI = 98.0


def head_point(z, phi, F):
    top = z >= 0
    Hz = F['Ht'] if top else F['Hb']
    zeta = max(-1.0, min(1.0, z / Hz))
    n = 2.55 if top else F['nlow']
    rho = (1 - abs(zeta) ** n) ** (1 / n)
    s, c = math.sin(phi), math.cos(phi)
    x = F['W'] * rho * s
    D = F['Df'] if c > 0 else F['Db']
    y = -D * rho * c
    t = max(0.0, min(1.0, -z / 0.115))
    x *= 1 - F['jaw'] * t ** 2
    zz = z
    if z < -0.045:
        zz += 0.04 * smooth(-0.02, 0.07, y) * smooth(-0.045, -0.1, z)
    fw = smooth(0.12, 0.5, c)
    ax = abs(x)
    dy = 0.0
    # --- face relief (dy<0 = forward)
    dy -= 0.0035 * g2(x, zz, 0, 0.052, 0.04, 0.02)                                     # forehead
    dy -= 0.0065 * F['brow'] * (g2(ax, zz, 0.027, 0.027, 0.026, 0.0072) + 0.5 * g2(x, zz, 0, 0.026, 0.01, 0.008))
    dy += 0.0085 * g2(ax, zz, F['eye_x'], F['eye_z'], 0.0185, 0.0125)                   # sockets
    dy -= 0.005 * F['cheek'] * g2(ax, zz, 0.05, -0.016, 0.02, 0.016)                    # cheekbones
    dy -= 0.004 * F['cheek'] * g2(ax, zz, 0.04, -0.05, 0.02, 0.015)                     # cheek flesh
    dy += F['age'] * 0.0045 * g2(ax, zz, 0.043, -0.062, 0.015, 0.015)                   # hollow cheeks
    # nose
    nz = [-0.054, -0.049, -0.044, -0.039, -0.034, -0.027, -0.017, -0.006, 0.005, 0.014, 0.024]
    npf = [0.0, 0.006, 0.015, 0.023, 0.026, 0.023, 0.018, 0.0135, 0.0095, 0.006, 0.0]
    nsx = [0.007, 0.010, 0.011, 0.009, 0.0075, 0.0065, 0.006, 0.006, 0.0065, 0.007, 0.008]
    P = float(np.interp(zz, nz, npf)); SX = float(np.interp(zz, nz, nsx)) * F['nose_w']
    dy -= P * F['nose'] * math.exp(-(x / SX) ** 2)
    dy -= 0.007 * F['nose'] * g2(ax, zz, 0.0145 * F['nose_w'], -0.043, 0.005, 0.006)  # alae
    dy += 0.0035 * g2(ax, zz, 0.008, -0.0495, 0.0035, 0.004)                            # nostril dimples
    # lips
    dy -= 0.0072 * F['lip'] * g2(x, zz, 0, -0.0655, 0.017, 0.0068)
    dy -= 0.0085 * F['lip'] * g2(x, zz, 0, -0.0805, 0.016, 0.0072)
    dy += 0.0038 * g2(x, zz, 0, Z_SLIT, 0.021, 0.0028)                                  # slit
    dy += 0.002 * g2(x, zz, 0, -0.0585, 0.004, 0.005)                                   # philtrum
    dy += 0.0035 * g2(x, zz, 0, -0.0915, 0.02, 0.004)                                   # mentolabial groove
    dy -= 0.011 * F['chin'] * g2(x, zz, 0, -0.103, 0.017, 0.012)                       # chin
    y += dy * fw
    return V(x, y, zz)


def build_head_grid(F):
    bm = bmesh.new()
    rows = ROWS_Z
    cols = [math.radians(a) for a in COLS_DEG]
    nc = len(cols)
    vrows = []
    for ri, z in enumerate(rows):
        if ri == 0 or ri == len(rows) - 1:
            v = bm.verts.new(head_point(z if ri == 0 else rows[-1], 0.0, F) * 1.0)
            if ri == len(rows) - 1:
                v.co = head_point(rows[-1] + 0.0003, 0.0, F)
                v.co.x = 0; v.co.y += 0.0
            else:
                v.co = V(0, 0.0, F['Ht'])
            vrows.append([v] * nc)
        else:
            vrows.append([bm.verts.new(head_point(z, ph, F)) for ph in cols])
    for ri in range(len(rows) - 1):
        for ci in range(nc):
            c2 = (ci + 1) % nc
            a, b = vrows[ri][ci], vrows[ri][c2]
            c, d = vrows[ri + 1][c2], vrows[ri + 1][ci]
            vs = [a, b, c, d]
            uniq = []
            for v in vs:
                if v not in uniq:
                    uniq.append(v)
            if len(uniq) < 3:
                continue
            try:
                # orientation: columns increase phi (x = sin phi): looking from outside need ordering a,d,c,b
                bm.faces.new(uniq)
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def _orient(uniq, vs):
    # triangle at a pole; vs = [a,b,c,d] with duplicates
    return uniq[::-1]


def face_azimuth_deg(co):
    return math.degrees(math.atan2(abs(co.x), -co.y))


def make_head(F, child=False):
    """Returns dict of bmeshes in head-local coords (origin = cranium center, front = -Y)."""
    grid = build_head_grid(F)
    out = {}
    # ---- BVH of the skin before splitting
    bvh = BVHTree.FromBMesh(grid)
    out['bvh'] = bvh
    out['grid'] = grid.copy()
    # ---- split into head and jaw at the slit row
    jaw = grid.copy()
    head = grid
    jaw_faces = []
    for f in head.faces:
        c = f.calc_center_median()
        is_jaw = c.z < Z_SLIT - 0.0005 and face_azimuth_deg(c) < JAW_PHI + 0.5
        jaw_faces.append(is_jaw)
    # head: delete jaw faces
    hf = [f for f, j in zip(head.faces, jaw_faces) if j]
    bmesh.ops.delete(head, geom=hf, context='FACES')
    jf = [f for f, j in zip(jaw.faces, jaw_faces) if not j]
    bmesh.ops.delete(jaw, geom=jf, context='FACES')
    for b in (head, jaw):
        old_faces = set(b.faces)
        bn = [e for e in b.edges if e.is_boundary]
        r = bmesh.ops.extrude_edge_only(b, edges=bn)
        nv = [g for g in r['geom'] if isinstance(g, bmesh.types.BMVert)]
        cen = V(0, 0.004, -0.05)
        for v in nv:
            v.co = cen + (v.co - cen) * 0.5
        bn2 = [e for e in b.edges if e.is_boundary]
        try:
            bmesh.ops.triangle_fill(b, use_beauty=True, edges=bn2)
        except Exception as ex:
            print('fill fail', ex)
        bmesh.ops.recalc_face_normals(b, faces=b.faces[:])
        for f in b.faces:
            if f not in old_faces:
                f.material_index = MI['mouth']
    # materials: skin + lips + nostrils
    for b, is_jaw in ((head, False), (jaw, True)):
        for f in b.faces:
            if f.material_index == MI['mouth']:
                continue
            c = f.calc_center_median()
            f.material_index = MI['skin']
    out['head'] = head
    out['jaw'] = jaw
    # ---- eyes
    R = 0.0134
    eyes = bmesh.new(); lids = bmesh.new()
    for sgn in (1, -1):
        ex = sgn * F['eye_x']
        hit = bvh.ray_cast(V(ex, -0.3, F['eye_z']), V(0, 1, 0))
        ys = hit[0].y if hit[0] is not None else -0.085
        cen = V(ex, ys + 0.0068, F['eye_z'])
        eb = bmesh.new()
        bmesh.ops.create_uvsphere(eb, u_segments=14, v_segments=10, radius=R)
        bmesh.ops.rotate(eb, verts=eb.verts[:], cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'))
        front = V(0, -1, 0)
        setm(eb, 'eye_white')
        # smooth circular iris + pupil caps (own geometry => round edges)
        cap = bmesh.new()
        segs_c = 20
        cv = cap.verts.new(V(0, -R * 1.022, 0))
        r1 = [cap.verts.new(V(R * math.sin(math.radians(12)) * math.cos(2 * math.pi * j / segs_c), -R * math.cos(math.radians(12)) * 1.02, R * math.sin(math.radians(12)) * math.sin(2 * math.pi * j / segs_c))) for j in range(segs_c)]
        r2 = [cap.verts.new(V(R * math.sin(math.radians(31)) * math.cos(2 * math.pi * j / segs_c), -R * math.cos(math.radians(31)) * 1.012, R * math.sin(math.radians(31)) * math.sin(2 * math.pi * j / segs_c))) for j in range(segs_c)]
        for j in range(segs_c):
            j2 = (j + 1) % segs_c
            f1 = cap.faces.new((cv, r1[j2], r1[j]))
            f1.material_index = MI['pupil']
            f2 = cap.faces.new((r1[j], r1[j2], r2[j2], r2[j]))
            f2.material_index = MI['iris']
        bmesh.ops.recalc_face_normals(cap, faces=cap.faces[:])
        # make sure caps face forward (-Y)
        if sum(f.normal.dot(front) for f in cap.faces) < 0:
            bmesh.ops.reverse_faces(cap, faces=cap.faces[:])
        eb = merge(eb, cap)
        translate(eb, cen)
        eyes = merge(eyes, eb) if len(eyes.verts) else eb
        # eyelids : two shells (upper / lower) cut exactly at almond shaped margins
        zc, zu, zl_ = 0.0004, 0.0066, -0.0058
        xr = 0.0128
        for kind in ('up', 'lo'):
            lb = bmesh.new()
            bmesh.ops.create_uvsphere(lb, u_segments=24, v_segments=14, radius=R * 1.13)
            bmesh.ops.rotate(lb, verts=lb.verts[:], cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'))
            dele = [f for f in lb.faces if f.calc_center_median().normalized().dot(front) < math.cos(math.radians(80))]
            bmesh.ops.delete(lb, geom=dele, context='FACES')
            if kind == 'up':
                bmesh.ops.bisect_plane(lb, geom=lb.verts[:] + lb.edges[:] + lb.faces[:], plane_co=(0, 0, zc + 0.0030), plane_no=(0, 0, 1), clear_inner=True)
            else:
                bmesh.ops.bisect_plane(lb, geom=lb.verts[:] + lb.edges[:] + lb.faces[:], plane_co=(0, 0, zc - 0.0030), plane_no=(0, 0, -1), clear_inner=True)
            lb.normal_update()
            for v in lb.verts:
                if v.is_boundary and abs(v.co.z - (zc + (0.0030 if kind == 'up' else -0.0030))) < 0.0006:
                    k = max(0.0, 1 - (v.co.x / xr) ** 2) ** 0.7
                    v.co.z = zc + ((zu - zc) if kind == 'up' else (zl_ - zc)) * k
            translate(lb, cen)
            setm(lb, 'skin')
            lids = merge(lids, lb) if len(lids.verts) else lb
    out['eyes'] = eyes
    out['lids'] = lids
    # ---- ears
    ears = bmesh.new()
    for sgn in (1, -1):
        hit = bvh.ray_cast(V(sgn * 0.3, F['ear_y'], F['ear_z']), V(-sgn, 0, 0))
        xs = hit[0].x if hit[0] is not None else sgn * 0.075
        rx_, ry_, rz_ = 0.0085 * F['ear'], 0.0145 * F['ear'], 0.0275 * F['ear']
        eb = bmesh.new()
        bmesh.ops.create_uvsphere(eb, u_segments=10, v_segments=8, radius=1.0)
        for v in eb.verts:
            u = v.co.copy()
            dent = 0.0
            if u.x * sgn > 0:
                dent = 0.62 * math.exp(-((u.y * 1.15) ** 2 + ((u.z + 0.05) * 1.6) ** 2)) * (u.x * sgn)
            v.co = V(u.x * rx_ * (1 - dent * 1.1), u.y * ry_, u.z * rz_)
            # rim: widen top to a curved shape
        bmesh.ops.rotate(eb, verts=eb.verts[:], cent=(0, 0, 0), matrix=Matrix.Rotation(sgn * math.radians(-24), 3, 'Z'))
        translate(eb, V(xs + sgn * 0.0025, F['ear_y'], F['ear_z']))
        ears = merge(ears, eb) if len(ears.verts) else eb
    setm(ears, 'skin')
    out['ears'] = ears
    return out


def default_face(**kw):
    F = dict(W=0.081, Df=0.091, Db=0.104, Ht=0.118, Hb=0.1155, nlow=3.5, jaw=0.30, brow=1.0, nose=1.0, nose_w=1.0,
             lip=1.0, chin=1.0, cheek=1.0, age=0.0, eye_x=0.032, eye_z=0.0, ear=1.0, ear_y=0.012, ear_z=-0.012)
    F.update(kw)
    return F


# ------------------------------------------------------------------ preview (private temp dir)
TMP = '/tmp/claude-1001/-shared-river/130188aa-f801-4c92-8245-c0871f14c147/scratchpad'


def vl_grid(path, views, res=(480, 480), samples=24, cols=2, sun=3.2, ground=True, tag='x'):
    sc = bpy.context.scene
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    b = w.node_tree.nodes['Background']; b.inputs[0].default_value = (0.62, 0.7, 0.82, 1); b.inputs[1].default_value = 0.9
    sd = bpy.data.lights.new('sun', 'SUN'); sd.energy = sun
    so = bpy.data.objects.new('sun', sd); so.rotation_euler = (math.radians(55), 0, math.radians(-30))
    sc.collection.objects.link(so)
    sd2 = bpy.data.lights.new('fill', 'SUN'); sd2.energy = 1.0
    so2 = bpy.data.objects.new('fill', sd2); so2.rotation_euler = (math.radians(70), 0, math.radians(140))
    sc.collection.objects.link(so2)
    if ground:
        bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
        g = bpy.context.object; g.name = '_ground'
        g.data.materials.append(make_mat('_groundmat', '#6b7a45', rough=0.95))
    cam = bpy.data.cameras.new('cam')
    co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co)
    sc.camera = co
    sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.device = 'CPU'
    sc.cycles.use_denoising = False
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.image_settings.file_format = 'PNG'
    tiles = []
    for i, v in enumerate(views):
        loc = v[0]; tg = v[1]; ln = v[2] if len(v) > 2 else 50
        cam.lens = ln
        co.location = loc
        co.rotation_euler = (V(tg) - V(loc)).to_track_quat('-Z', 'Y').to_euler()
        fp = '%s/_vl_%s_%d.png' % (TMP, tag, i)
        sc.render.filepath = fp
        bpy.ops.render.render(write_still=True)
        im = bpy.data.images.load(fp)
        a = np.array(im.pixels[:], dtype=np.float32).reshape(res[1], res[0], 4)
        tiles.append(a); bpy.data.images.remove(im)
    rows = (len(tiles) + cols - 1) // cols
    H, W = res[1], res[0]
    canvas = np.ones((rows * H, cols * W, 4), dtype=np.float32)
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        canvas[(rows - 1 - r) * H:(rows - r) * H, c * W:(c + 1) * W] = t
    im = bpy.data.images.new('grid', cols * W, rows * H)
    im.pixels = canvas.ravel().tolist()
    im.filepath_raw = path; im.file_format = 'PNG'; im.save()
    return path


def ribbon(pts, width, th=0.004, axis=(1, 0, 0), widths=None):
    """Flat strap along pts (width direction = axis), solidified. Returns bmesh."""
    bm = bmesh.new()
    ax = V(axis)
    pts = interp_path([V(p) for p in pts], 3)
    rows = []
    for i, p in enumerate(pts):
        w = width if widths is None else widths[min(len(widths) - 1, int(i * len(widths) / len(pts)))]
        rows.append((bm.verts.new(p - ax * w / 2), bm.verts.new(p + ax * w / 2)))
    for i in range(len(rows) - 1):
        try:
            bm.faces.new((rows[i][0], rows[i][1], rows[i + 1][1], rows[i + 1][0]))
        except ValueError:
            pass
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=th)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def rim(bm, th=0.004):
    """Give open boundary edges visible thickness (cheap alternative to solidify): extrude boundary inward."""
    bm.normal_update()
    be = [e for e in bm.edges if e.is_boundary]
    if not be:
        return bm
    nrm = {}
    for e in be:
        for v in e.verts:
            nrm[v.index] = v.normal.copy()
    bm.verts.ensure_lookup_table()
    pos2n = {(round(v.co.x, 5), round(v.co.y, 5), round(v.co.z, 5)): nrm[v.index] for v in bm.verts if v.index in nrm}
    r = bmesh.ops.extrude_edge_only(bm, edges=be)
    for g in r['geom']:
        if isinstance(g, bmesh.types.BMVert):
            k = (round(g.co.x, 5), round(g.co.y, 5), round(g.co.z, 5))
            n = pos2n.get(k)
            if n is not None:
                g.co -= n * th
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm
