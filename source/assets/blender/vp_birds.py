"""vp_birds: hen / rooster builder (farm birds). build(kind) with kind in ('hen','rooster').
Geometry authored at hen scale in world coords (Z up, beak -Y), painted, then uniformly scaled by K."""
import sys
sys.path.insert(0, '/shared/river/assets/blender')
from birdlib import *
from mathutils.bvhtree import BVHTree

rnd = random.Random(5)


def P(bm, c=(1, 1, 1)):
    if isinstance(c, str):
        c = hex_rgb(c)
    paint(bm, lambda p, n: c)
    return bm


def build(kind):
    ROOS = kind == 'rooster'
    K = 1.30 if ROOS else 1.0
    reset_scene()
    rnd.seed(7 if ROOS else 3)
    random.seed(1)
    # ---------------- materials
    feath = vcol_mat('feather', '#ffffff', rough=0.82)
    eyem = make_mat('eye_amber', '#d98a1c' if not ROOS else '#c85a12', rough=0.1)
    pupm = make_mat('pupil', '#000000', rough=0.1)
    beakm = make_mat('beak_horn', '#c9a24a' if not ROOS else '#b99440', rough=0.4)
    fleshm = vcol_mat('comb_flesh', '#ffffff', rough=0.5)
    legm = vcol_mat('leg_scale', '#ffffff', rough=0.55)
    clawm = make_mat('claw', '#8d7d5a', rough=0.45)

    # ---------------- palette
    if ROOS:
        BODY, BODY2, HACK, HACK2, WING, DARK, BREAST = '#9c3d17', '#7a2a10', '#e0a22c', '#f0c25a', '#8a3414', '#0e2a1e', '#12261c'
        SADDLE = '#e8a830'
    else:
        BODY, BODY2, HACK, HACK2, WING, DARK, BREAST = '#9b6034', '#7a4726', '#8a5028', '#5a3418', '#8a5230', '#2b1a10', '#b7753f'
        SADDLE = '#9b6034'
    COMBC = '#c8161e'

    def spk(p, f=120.0, seed=0):
        return fbm(p, f, 2, seed) * 0.5 + 0.5

    # ---------------- body
    yz = [(-0.135, 0.255), (-0.09, 0.238), (0.0, 0.225), (0.08, 0.238), (0.145, 0.275)]
    if ROOS:
        yz = [(-0.135, 0.265), (-0.09, 0.248), (0.0, 0.230), (0.08, 0.235), (0.15, 0.255)]
    rxs = [0.04, 0.083, 0.097, 0.078, 0.03]
    rzs = [0.06, 0.094, 0.098, 0.082, 0.04]
    if ROOS:
        rxs = [0.04, 0.075, 0.088, 0.07, 0.028]; rzs = [0.06, 0.098, 0.092, 0.075, 0.04]
    bpts = [V(0, y, z) for y, z in yz]
    bb = loft(bpts, rxs, rzs, segs=28, res=4)
    brb = blob(V(0, -0.08, 0.225), (0.074, 0.075, 0.085) if not ROOS else (0.066, 0.075, 0.09))
    rump = blob(V(0, 0.115, 0.262), (0.045, 0.06, 0.05))
    bodybm = fuse(merge(bb, brb, rump), voxel=0.0078, smooth_iter=6, smooth_f=0.5)
    bvh_src = bodybm.copy()
    NECK_B = V(0, -0.095, 0.292) if not ROOS else V(0, -0.095, 0.305)
    HEAD_C = V(0, -0.140, 0.368) if not ROOS else V(0, -0.150, 0.395)

    def bcol(p, n):
        t = spk(p, 80, 2)
        if ROOS:
            c = mixc(BODY, BODY2, t * 0.7)
            c = mixc(c, BREAST, sstep(-0.05, -0.12, p.y) * sstep(0.25, 0.16, p.z) * 0.0 + max(0.0, -n.z * 1.2 - 0.1) * sstep(0.02, -0.07, p.y))
            c = mixc(c, BREAST, sstep(-0.07, -0.12, p.y) * 0.9)
            c = mixc(c, SADDLE, sstep(0.0, 0.07, p.y) * max(0.0, n.z) * 0.8)
        else:
            c = mixc(BODY, BODY2, t * 0.8)
            c = mixc(c, BREAST, sstep(-0.02, -0.11, p.y) * 0.8)
            if spk(p, 220, 5) > 0.66:
                c = mulc(c, 0.55)   # speckles
        if n.z < -0.4:
            c = mixc(c, mulc(c, 0.7), 0.6)
        return c
    # feathers on body: from verts
    bodybm.normal_update()
    vs = list(bodybm.verts)
    rnd.shuffle(vs)
    feats = []
    nf = 480 if not ROOS else 380
    for v in vs[:nf]:
        n = v.normal
        if n.z < -0.55:
            continue
        p = v.co
        d = V(0, 1, -0.25)
        d = (d - n * d.dot(n)).normalized()
        L = rnd.uniform(0.034, 0.046)
        base = p + n * 0.001
        tip = base + d * L + n * 0.0045
        c0 = bcol(p, n)
        edge = mulc(c0, 0.55)
        feats.append(feather(base, tip, 0.0085, (lambda c0, edge: (lambda t, lat: mixc(mixc(c0, edge, sstep(0.75, 1, abs(lat)) * 0.5), mulc(c0, 1.25), 0.25 * (1 - t))))(c0, edge),
                             thick=0.0012, normal=n, bulge=0.4, segs=3, res=1))
    paint(bodybm, bcol)
    bodybm = merge(bodybm, *feats)
    # BVH of the unfeathered body for conforming wing feathers
    bvh = BVHTree.FromBMesh(bvh_src)

    def surf(sx, y, z, lift=0.0):
        hit = bvh.ray_cast(V(sx * 0.5, y, z), V(-sx, 0, 0))
        if hit[0] is None:
            return V(sx * 0.02, y, z), V(sx, 0, 0)
        return hit[0] + hit[1] * lift, hit[1]

    objs_spec = []   # (name, bm, mats, pivot, parent_name)
    objs_spec.append(('body', bodybm, [feath], V(0, 0.0, 0.23), None))

    # ---------------- head (neck + head + comb + wattles + beak upper + eyes + hackle)
    D = (HEAD_C - NECK_B)
    neck_pts = [NECK_B + V(0, 0.03, -0.035), NECK_B, NECK_B.lerp(HEAD_C, 0.5) + V(0, 0.004, 0), HEAD_C + V(0, 0.012, -0.012)]
    nbm = loft(neck_pts, [0.040, 0.038, 0.027, 0.024], [0.045, 0.042, 0.030, 0.026], segs=18, res=5)
    hbm = blob(HEAD_C, (0.025, 0.036, 0.031), rot=(0.15, 0, 0), segs=18, rings=12)
    cheek = [blob(HEAD_C + V(sx * 0.016, -0.012, -0.010), (0.012, 0.018, 0.015)) for sx in (1, -1)]
    headbm = fuse(merge(nbm, hbm, *cheek), voxel=0.0046, smooth_iter=6, smooth_f=0.5)

    def hcol(p, n):
        if p.z > HEAD_C.z - 0.03 and p.y < NECK_B.y + 0.005:
            c = mixc(BODY, HACK, 0.5) if not ROOS else HACK
            c = mixc(c, mixc('#7a2a10', '#d9b060', 0.5), 0.0)
            return mulc(c, 0.7 + 0.5 * spk(p, 200, 4))
        c = mixc(HACK, HACK2, spk(p, 150, 3)) if ROOS else mixc(BODY2, HACK, 0.3 + 0.7 * spk(p, 90, 3))
        # face lightly bare red patch
        fp = sstep(0.01, 0.0, abs(p.x) - 0.018) * sstep(HEAD_C.y + 0.012, HEAD_C.y - 0.02, p.y) * sstep(HEAD_C.z - 0.02, HEAD_C.z + 0.0, p.z)
        c = mixc(c, mixc(COMBC, '#e8a090', 0.35), fp * 0.9)
        return c
    # hackle feathers over neck
    hf = []
    headbm.normal_update()
    hv = list(headbm.verts)
    rnd.shuffle(hv)
    cnt = 0
    for v in hv:
        p = v.co
        if p.z > HEAD_C.z - 0.045:
            continue
        n = v.normal
        d = (NECK_B - HEAD_C).normalized()
        d = (d - n * d.dot(n)).normalized()
        L = rnd.uniform(0.03, 0.04) * (1.5 if ROOS else 1.0)
        base = p + n * 0.002
        tip = base + d * L + n * 0.007
        c0 = hcol(p, n)
        w = 0.0085 if ROOS else 0.011
        hf.append(feather(base, tip, w, (lambda c0: (lambda t, lat: mixc(c0, mixc(HACK2, '#2a1408', 0.5), sstep(0.5, 1, abs(lat)) * 0.25 + 0.12 * t) if not ROOS else mixc(c0, '#f2cf6a', t * 0.4)))(c0),
                          thick=0.001, normal=n, bulge=0.3, segs=4, res=1))
        cnt += 1
        if cnt > (60 if not ROOS else 85):
            break
    paint(headbm, hcol)
    hparts = [headbm] + hf
    # eyes
    for sx in (1, -1):
        c = HEAD_C + V(sx * 0.0215, -0.012, 0.010)
        e = blob(c, (0.0075, 0.0085, 0.0085), segs=12, rings=8); set_mat_index(e, 1); P(e)
        pu = blob(c + V(sx * 0.0045, -0.002, 0.0), (0.0042, 0.0042, 0.0042), segs=10, rings=6); set_mat_index(pu, 2); P(pu)
        hparts += [e, pu]
    # beak upper
    BH = HEAD_C + V(0, -0.030, -0.006)
    bk = loft([BH + V(0, 0.012, 0.002), BH, BH + V(0, -0.012, -0.004), BH + V(0, -0.024, -0.010)], [0.011, 0.0105, 0.0075, 0.0018], [0.011, 0.0100, 0.0070, 0.0022], segs=12, res=4, cap_push=0.4)
    set_mat_index(bk, 3); P(bk); hparts.append(bk)
    # nostrils tiny dark? skip. comb
    cb = []
    if ROOS:
        N = 6
        for i in range(N):
            t = i / (N - 1)
            h = 0.034 * (0.5 + 0.5 * math.sin(math.pi * (0.15 + 0.8 * t))) + 0.005
            cy = HEAD_C.y - 0.020 + t * 0.050
            cz = HEAD_C.z + 0.024 + 0.008 * math.sin(math.pi * t) - 0.01 * t
            b = blob(V(0, cy, cz + h * 0.5), (0.0045, 0.0085, h * 0.6), segs=10, rings=8)
            set_mat_index(b, 4); cb.append(b)
        base_ = blob(V(0, HEAD_C.y + 0.004, HEAD_C.z + 0.024), (0.0065, 0.030, 0.008), segs=12, rings=6); set_mat_index(base_, 4); cb.append(base_)
        for sx in (1, -1):
            w = blob(V(sx * 0.005, HEAD_C.y - 0.036, HEAD_C.z - 0.032), (0.0042, 0.012, 0.026), rot=(0.1, 0, 0), segs=10, rings=8); set_mat_index(w, 4); cb.append(w)
            ear = blob(V(sx * 0.0215, HEAD_C.y + 0.006, HEAD_C.z - 0.012), (0.004, 0.008, 0.011), segs=8, rings=6); set_mat_index(ear, 4); cb.append(ear)
    else:
        for i in range(4):
            t = i / 3
            h = 0.014 * (0.55 + 0.45 * math.sin(math.pi * (0.1 + 0.85 * t)))
            b = blob(V(0, HEAD_C.y - 0.014 + t * 0.026, HEAD_C.z + 0.027 + h * 0.4 - 0.004 * t), (0.003, 0.0058, h * 0.8), segs=8, rings=6)
            set_mat_index(b, 4); cb.append(b)
        base_ = blob(V(0, HEAD_C.y - 0.002, HEAD_C.z + 0.025), (0.0042, 0.018, 0.005), segs=10, rings=6); set_mat_index(base_, 4); cb.append(base_)
        for sx in (1, -1):
            w = blob(V(sx * 0.004, HEAD_C.y - 0.034, HEAD_C.z - 0.020), (0.003, 0.007, 0.012), segs=8, rings=6); set_mat_index(w, 4); cb.append(w)
            ear = blob(V(sx * 0.0215, HEAD_C.y + 0.008, HEAD_C.z - 0.010), (0.0035, 0.006, 0.008), segs=8, rings=6); set_mat_index(ear, 4); cb.append(ear)
    for b in cb:
        P(b, mixc(COMBC, '#7a0a10', 0.0))
        for v in b.verts:
            pass
    hparts += cb
    head_bm = merge(*hparts)
    objs_spec.append(('head', head_bm, [feath, eyem, pupm, beakm, fleshm], NECK_B, 'body'))
    # beak lower
    JH = BH + V(0, 0.010, -0.003)
    jb = loft([JH, JH + V(0, -0.012, -0.001), JH + V(0, -0.022, -0.004)], [0.0075, 0.0058, 0.0016], [0.0045, 0.0036, 0.0012], segs=10, res=4, cap_push=0.4)
    P(jb)
    objs_spec.append(('beak_lower', jb, [beakm], JH, 'head'))

    # ---------------- wings (folded on flank)
    WSH = V(0, -0.035, 0.268)
    for sx, nm in ((1, 'wing_l'), (-1, 'wing_r')):
        fl = []
        shoulder = V(sx * 0.088, -0.035, 0.268)
        # base shape: thin teardrop pad under feathers
        pad_pts = []
        for y, z in [(-0.045, 0.262), (0.0, 0.252), (0.06, 0.243), (0.12, 0.24)]:
            h, nrm = surf(sx, y, z, 0.002)
            pad_pts.append(h)
        padb = loft(pad_pts, [0.002, 0.003, 0.003, 0.0015], [0.034, 0.040, 0.030, 0.014], segs=8, res=3, up=(0, 0, 1))
        P(padb, WING)
        fl.append(padb)

        def wcol(c0, edge, dark=0.0):
            return lambda t, lat: mulc(mixc(mixc(c0, edge, sstep(0.78, 1, abs(lat)) * 0.8), '#e8d0a0' if not ROOS else '#2c1608', sstep(0.82, 1.0, t) * (0.5 if not ROOS else 0.0)), 1 - dark * t)
        # coverts rows
        rows = [(-0.03, 0.272, 0.040, 0), (-0.005, 0.262, 0.044, 1), (0.02, 0.254, 0.046, 2), (0.045, 0.248, 0.046, 3)]
        for (y0, z0, L, row) in rows:
            for k in range(4 if row < 3 else 3):
                zz = z0 - k * 0.025 + rnd.uniform(-0.003, 0.003)
                yy = y0 + k * 0.004 + (row * 0.004)
                base, nrm = surf(sx, yy, zz, 0.003 + 0.002 * row)
                tip_t, tn = surf(sx, yy + L, zz - 0.012, 0.005 + 0.002 * row)
                c0 = mixc(WING, BODY2, rnd.random() * 0.5)
                fl.append(feather(base, tip_t, 0.015, wcol(c0, mulc(c0, 0.5)), thick=0.001, normal=nrm, bulge=0.4, segs=5, res=1))
        # secondaries
        for k in range(8):
            zz = 0.252 - k * 0.0095 - 0.002
            yy = 0.0 + k * 0.012
            base, nrm = surf(sx, yy, 0.255 - 0.018 * (k / 7), 0.007)
            L = 0.115 - k * 0.002
            tip_t, tn = surf(sx, yy + L, 0.228 - 0.012 * (k / 7), 0.010 + 0.0006 * k)
            c0 = mixc(WING, '#c89a60' if not ROOS else '#7a2a10', 0.3 if k % 2 else 0.0)
            fl.append(feather(base, tip_t, 0.0185, wcol(c0, mulc(c0, 0.6), 0.1), thick=0.0012, normal=nrm, bulge=0.35, segs=6, res=2))
        # primaries
        for k in range(8):
            yy = 0.03 + k * 0.011
            base, nrm = surf(sx, yy, 0.248 - k * 0.003, 0.012)
            L = 0.125 + 0.006 * (k % 3 == 0)
            tip_t, tn = surf(sx, yy + L - k * 0.003, 0.220 + k * 0.0005, 0.016 + 0.0012 * k)
            c0 = mixc(WING, DARK if ROOS else '#6a4220', 0.4)
            fl.append(feather(base, tip_t, 0.016, wcol(c0, mulc(c0, 0.6), 0.2), thick=0.0012, normal=nrm, bulge=0.35, segs=6, res=2))
        wbm = merge(*fl)
        objs_spec.append((nm, wbm, [feath], shoulder, 'body'))

    # ---------------- tail
    TP = V(0, 0.140, 0.265)
    tf = []

    def tcol_h(c0, c1, sheen=False):
        def f(t, lat):
            c = mixc(c0, c1, t * 0.7)
            if sheen:
                c = mixc(c, '#1f8a55', sstep(0.2, 0.7, t) * (0.5 + 0.5 * math.sin(t * 9 + lat * 2)) * 0.6)
            return mulc(c, 1 - 0.35 * sstep(0.85, 1.0, abs(lat)))
        return f
    if ROOS:
        # main fan (short upright) + curved sickles
        nmain = 9
        for i in range(nmain):
            a = (i / (nmain - 1) - 0.5) * 2
            for layer in (0, 1):
                yaw = a * 0.50
                L = 0.20 - 0.03 * abs(a) - 0.01 * layer
                d = V(math.sin(yaw), math.cos(yaw) * 0.55, 0.85 - 0.25 * abs(a))
                d.normalize()
                b = TP + V(a * 0.012, 0.0, -0.004 * layer)
                nrm = V(math.cos(yaw), -math.sin(yaw), 0).normalized()
                tf.append(feather(b, b + d * L, 0.032, tcol_h('#0e281c', '#0c1d1a', sheen=True), thick=0.0014, normal=nrm, bulge=0.35, curve=(0, 0.02, 0.0), segs=6, res=2))
        for i in range(7):
            a = (i / 6 - 0.5) * 2
            yaw = a * 0.34
            L = 0.46 - 0.07 * abs(a) - (0.0 if i % 2 else 0.04)
            b = TP + V(a * 0.012, 0.012, 0.012 + 0.01 * (1 - abs(a)))
            tip = b + V(math.sin(yaw) * L * 0.7, L * 0.7, -0.03 - 0.15 * (0.6 + 0.4 * abs(a)) * L / 0.46)
            nrm = V(math.cos(yaw), -math.sin(yaw), 0.0).normalized()
            tf.append(feather(b, tip, 0.036 - 0.004 * abs(a), tcol_h('#0d2a1c', '#0a2018', sheen=True), thick=0.0014, normal=nrm, bulge=0.30, curve=(math.sin(yaw) * 0.04, 0.0, 0.17 * L / 0.46), segs=8, res=3))
        for sx in (1, -1):   # small coverts at tail base
            for k in range(3):
                b = TP + V(sx * (0.012 + 0.01 * k), -0.06 + 0.015 * k, 0.0)
                tip = b + V(sx * 0.03, 0.14, 0.05 - 0.02 * k)
                tf.append(feather(b, tip, 0.020, tcol_h('#d9922a', '#8a3a10'), thick=0.0012, normal=V(1, 0, 0), bulge=0.4, curve=(0, 0, 0.03), segs=5, res=2))
    else:
        nmain = 9
        for i in range(nmain):
            a = (i / (nmain - 1) - 0.5) * 2
            for layer in (0, 1):
                yaw = a * 0.50
                L = 0.15 - 0.022 * abs(a) - 0.008 * layer
                d = V(math.sin(yaw), math.cos(yaw) * 0.55, 0.85 - 0.25 * abs(a)).normalized()
                b = TP + V(a * 0.010, 0.0, -0.004 * layer)
                nrm = V(math.cos(yaw), -math.sin(yaw), 0).normalized()
                tf.append(feather(b, b + d * L, 0.032, tcol_h('#8a5230', '#2b1a10'), thick=0.0013, normal=nrm, bulge=0.4, curve=(0, 0.01, 0.0), segs=6, res=2))
    tailbm = merge(*tf)
    objs_spec.append(('tail', tailbm, [feath], TP, 'body'))

    # ---------------- legs
    LEG_C = '#d6b24a' if not ROOS else '#c9a63e'
    for sx, nm, fn in ((1, 'leg_l', 'foot_l'), (-1, 'leg_r', 'foot_r')):
        hip = V(sx * 0.056, 0.012, 0.160)
        knee = V(sx * 0.060, -0.035, 0.115)
        ank = V(sx * 0.058, -0.010, 0.042)
        thigh = blob(hip + V(-sx * 0.004, 0.0, 0.016), (0.024, 0.034, 0.032), rot=(0.4, 0, 0), segs=14, rings=10)
        paint(thigh, lambda p, n: mixc(BODY2, BODY, 0.4) if True else None)
        tars = loft([knee + V(0, 0.005, 0.0), knee.lerp(ank, 0.5), ank], [0.0105, 0.0085, 0.0095], [0.0085, 0.0075, 0.0085], segs=10, res=5, cap_push=0.3)
        if ROOS:
            sp = loft([knee.lerp(ank, 0.72) + V(sx * -0.006, 0.006, 0), knee.lerp(ank, 0.78) + V(sx * -0.012, 0.016, 0.012)], [0.004, 0.0015], segs=6, res=2, cap_push=1.0)
            tars = merge(tars, sp)
        sf = lambda p, n: mulc(LEG_C, 0.75 + 0.25 * (0.5 + 0.5 * math.sin(p.z * 350)))
        paint(tars, sf)
        lg = merge(thigh, tars)
        objs_spec.append((nm, lg, [legm], hip, 'body'))
        # foot
        toes = []
        for ang, ln, rr in ((0, 0.052, 0.0072), (-0.55, 0.045, 0.0066), (0.55, 0.045, 0.0066), (math.pi, 0.028, 0.0062)):
            dv = V(math.sin(ang) * sx * 0.0 + math.sin(ang) * 0.6 * sx, -math.cos(ang), 0)
            if ang == math.pi:
                dv = V(0, 1, 0)
            dv.normalize()
            b0 = ank + V(0, 0, -0.004)
            tip_ = V(ank.x, ank.y, 0.0075) + dv * ln
            mid = b0.lerp(tip_, 0.45); mid.z = 0.012
            t = loft([b0, mid, tip_], [rr * 1.2, rr, rr * 0.7], [rr, rr * 0.8, rr * 0.6], segs=8, res=3, cap_push=0.4)
            paint(t, sf)
            toes.append(t)
            cl = loft([tip_ - dv * 0.004, tip_ + dv * 0.010 + V(0, 0, -0.004)], [rr * 0.7, 0.0012], segs=6, res=1, cap_push=1.0)
            P(cl, '#8a7a55'); set_mat_index(cl, 1); toes.append(cl)
        footbm = merge(*toes)
        objs_spec.append((fn, footbm, [legm, clawm], ank, nm))

    # ---------------- finalize: scale by K, create parts
    objs = {}
    order = ['body', 'head', 'beak_lower', 'wing_l', 'wing_r', 'tail', 'leg_l', 'foot_l', 'leg_r', 'foot_r']
    spec = {s[0]: s for s in objs_spec}
    for nm in order:
        _, bm, mats, piv, par = spec[nm]
        if nm == 'body':
            fur_noise(bm, amp=0.0012, freq=60, seed=1)
        if K != 1.0:
            for v in bm.verts:
                v.co *= K
        ob = part(nm, bm, mats, piv * K, parent=objs.get(par) if par else None, smooth=True)
        objs[nm] = ob
    bpy.context.view_layer.update()
    return objs, K
