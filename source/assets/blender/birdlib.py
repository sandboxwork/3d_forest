"""birdlib: feather + wing-rig helpers for bird assets (built on animlib). Do not edit animlib."""
import sys
sys.path.insert(0, '/shared/river/assets/blender')
from animlib import *

sub_noise = mnoise


def feather(base, tip, width, colfn, thick=0.0012, normal=(0, 0, 1), bulge=0.35, curve=(0, 0, 0), segs=6, res=2):
    """One flat feather blade base->tip. colfn(t, lateral) -> colour; t = 0..1 along blade, lateral = -1..1."""
    base = V(base); tip = V(tip)
    bm = leaf_shape(base, tip, width, thick, bulge=bulge, segs=segs, curve=curve, res=res, up=normal)
    L = (tip - base).length
    d = (tip - base) / L
    nv = V(normal).normalized()
    side = d.cross(nv).normalized()

    def f(p, n):
        r = p - base
        t = max(0.0, min(1.0, r.dot(d) / L))
        lat = max(-1.0, min(1.0, r.dot(side) / (width + 1e-6)))
        return colfn(t, lat)
    paint(bm, f)
    return bm


def solid(bm, fn):
    paint(bm, fn)
    return bm


def rot_from_euler_deg(ex, ey, ez):
    return Euler((math.radians(ex), math.radians(ey), math.radians(ez)), 'XYZ').to_matrix()


def cyc_fold(span_to, dorsal_to):
    """Rotation taking open-wing frame (span=+X, dorsal=+Z, chord/trailing=+Y) to a folded frame where the
    span axis maps to span_to and the dorsal axis maps to dorsal_to (both Vectors, orthogonal)."""
    s = V(span_to).normalized(); d = V(dorsal_to).normalized()
    # R(X)=s, R(Z)=d, R(Y)=R(Z) x R(X) = d x s
    y = d.cross(s).normalized()
    M = Matrix(((s.x, y.x, d.x), (s.y, y.y, d.y), (s.z, y.z, d.z)))
    return M


class WingRig:
    """Build a wing as parts upper/fore/hand from OPEN-pose geometry (left wing, +X span), then fold by absolute
    segment rotations W_i about joint pivots. Right wing = mirror. Returns part objects and the 'open' rotations
    (quaternions, three.js-compatible via export convention) stored in self.open_rot."""

    def __init__(self):
        self.info = {}

    def make(self, prefix, sgn, bms, pivots, W, body, mats, open_pose_only=False):
        """bms: {'upper','fore','hand'} bmesh in open left-wing coords. pivots: {'upper':S,'fore':E,'hand':Wr} (Vectors).
        W: dict of absolute 3x3 rotations open->folded per segment (for the left wing). sgn=+1 left, -1 right (mirrored).
        mats: material list. Returns list of objects."""
        order = ['upper', 'fore', 'hand']
        objs = []
        Mworld = {}  # 4x4 fold transform applied to geometry (left coordinates)
        prev_M = Matrix.Identity(4)
        parent = body
        rots = {}
        prev_W = Matrix.Identity(3)
        for nm in order:
            P = V(pivots[nm])
            Wi_ = W.get(nm, Matrix.Identity(3))
            R = (prev_W.inverted() @ Wi_).to_4x4()
            prev_W = Wi_
            M = prev_M @ Matrix.Translation(P) @ R @ Matrix.Translation(-P)
            if open_pose_only:
                M = Matrix.Identity(4)
            bm = bms[nm]
            xform(bm, M)
            newp = prev_M @ P if not open_pose_only else P
            # left->right mirror
            if sgn < 0:
                for v in bm.verts:
                    v.co.x = -v.co.x
                bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
                newp = V(-newp.x, newp.y, newp.z)
            ob = part('%s_%s' % (prefix, nm), bm, mats, newp, parent=parent, smooth=getattr(self, 'smooth', True))
            objs.append(ob)
            parent = ob
            # local rotation to go back to open: Rl = Wp * Wi^-1 * Wp^-1 (world axes at rest)
            Wi = W[nm] if nm in W else Matrix.Identity(3)
            # absolute folded rotation of this segment = accumulative of parent M rot? W are absolute, so:
            Rl = Wi.inverted() if nm == 'upper' else (W[order[order.index(nm) - 1]] @ Wi.inverted())
            if sgn < 0:
                Mx = Matrix.Diagonal((-1, 1, 1))
                Rl = Mx @ Rl @ Mx
            rots[nm] = Rl
            prev_M = M
        self.info[prefix] = {k: Rl.to_quaternion() for k, Rl in rots.items()}
        self.objs = getattr(self, 'objs', []) + objs
        return objs


def quat_three(q):
    """Blender quaternion (w,x,y,z) -> three.js [x,y,z,w] after (x,y,z)->(x,z,-y) axis conversion."""
    return [round(q.x, 5), round(q.z, 5), round(-q.y, 5), round(q.w, 5)]


def euler_deg(q):
    e = q.to_euler('XYZ')
    return [round(math.degrees(a), 1) for a in e]


def apply_open(rig):
    """Preview helper: set part rotations to the 'open' pose."""
    for prefix, qs in rig.info.items():
        for seg, q in qs.items():
            ob = bpy.data.objects['%s_%s' % (prefix, seg)]
            ob.rotation_mode = 'QUATERNION'
            ob.rotation_quaternion = q


def wing_meta(rig):
    out = {}
    for prefix, qs in rig.info.items():
        out[prefix] = {seg: {'open_quat_xyzw_three': quat_three(q), 'open_euler_xyz_deg_blender': euler_deg(q)} for seg, q in qs.items()}
    return out


def eye_pair(head_center_fn, pos, r, mats_idx=(1, 3)):
    """Returns list of bmeshes (eyeballs + pupils) for both sides. pos=(x,y,z) for left eye."""
    out = []
    for sx in (1, -1):
        c = V(pos[0] * sx, pos[1], pos[2])
        e = blob(c, (r, r, r), segs=14, rings=10); set_mat_index(e, mats_idx[0])
        # pupil/iris highlight: smaller dark blob on outer/front
        pc = c + V(sx * r * 0.45, -r * 0.45, r * 0.1)
        p = blob(pc, (r * 0.62, r * 0.62, r * 0.62), segs=10, rings=8); set_mat_index(p, mats_idx[1])
        out += [e, p]
    return out


def toe(base, dirv, length, r, curl=0.0):
    d = V(dirv).normalized()
    pts = [base, base + d * length * 0.5 + V(0, 0, curl * 0.3 * length), base + d * length + V(0, 0, curl * length * -1)]
    return loft(pts, [r, r * 0.8, r * 0.5], [r * 0.9, r * 0.7, r * 0.5], segs=6, res=2, up=(0, 0, 1))


def scales_col(base, dark, freq=300.0, amt=0.2, seed=0):
    def f(p, n):
        d = sub_noise.voronoi(p * freq + V(seed, seed, seed))[0][0]
        return mulc(base, 1.0 - amt * min(1.0, d * 1.3))
    return f


def paint(bm, fn, name='Col'):
    """FLOAT_COLOR point-domain paint (no byte re-encoding loss across bmesh<->mesh merges)."""
    bm.normal_update()
    lay = bm.verts.layers.float_color.get(name) or bm.verts.layers.float_color.new(name)
    for v in bm.verts:
        c = fn(v.co.copy(), v.normal.copy())
        if isinstance(c, str):
            c = hex_rgb(c)
        v[lay] = (c[0], c[1], c[2], 1.0)
    return bm


def sstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def fcol(base, edge=None, dark=0.0, edge_amt=0.7):
    edge = edge or base
    def f(t, lat):
        c = mixc(base, edge, sstep(0.72, 1.0, abs(lat)) * edge_amt)
        return mulc(c, 1.0 - dark * t)
    return f


def build_wing_bms(P):
    """Generic open left-wing (+X span, chord +Y, dorsal +Z) parts as bmeshes {'upper','fore','hand'}.
    P keys: S,E,Wr (Vectors); bone (radius scale); n_up, up_len, up_w, up_col(i)->colfn;
    n_sec, sec_len(t), sec_w, sec_col(i,n)->colfn; n_prim, prim_len[list], prim_w, fan(phi0,phi1 deg), prim_col(j,n);
    covers: list of (len, dz, count, width, colfn); thick; hand_len (vector Wr->bone tip)."""
    S, E, Wr = V(P['S']), V(P['E']), V(P['Wr'])
    bone = P.get('bone', 1.0); th = P.get('thick', 0.0012)
    bc = P.get('bone_col', '#6b5a3e')
    up = [loft([S - V(0.004 * bone * 4, 0, 0), S, E], [0.005 * bone * 3, 0.0055 * bone * 3, 0.004 * bone * 3], [0.0045 * bone * 3, 0.005 * bone * 3, 0.0035 * bone * 3], segs=10, res=3)]
    paint(up[0], lambda p, n: hex_rgb(bc))
    nu = P.get('n_up', 9)
    for i in range(nu):
        t = i / max(1, nu - 1)
        b = S.lerp(E, t) + V(0, 0.002, 0.002 + 0.0006 * (i % 3) * bone * 3)
        L = P['up_len'] * (1 - 0.06 * (i % 4))
        up.append(feather(b, b + V(0.004 * bone * 3, L, -0.004 * bone * 3), P['up_w'], P['up_col'](i), thick=th))
    for (ln, dz, cnt, wd, cf) in P.get('up_covers', []):
        for i in range(cnt):
            t = i / max(1, cnt - 1)
            b = S.lerp(E, t) + V(0, -0.002 * bone * 3, dz)
            up.append(feather(b, b + V(0.0, ln, dz * 0.4), wd, cf, thick=th * 0.8))
    fore = [loft([E, E.lerp(Wr, 0.5), Wr], [0.0038 * bone * 3, 0.0035 * bone * 3, 0.003 * bone * 3], [0.0034 * bone * 3] * 3, segs=8, res=3)]
    paint(fore[0], lambda p, n: hex_rgb(bc))
    ns = P['n_sec']
    for i in range(ns):
        t = i / (ns - 1)
        b = E.lerp(Wr, t) + V(0, 0.003 * bone * 3, -0.001 * i * bone * 3)
        L = P['sec_len'](t)
        a = math.radians(-6 + 4 * (1 - t))
        fore.append(feather(b, b + V(math.sin(a) * L, math.cos(a) * L, -0.006 * bone * 3), P['sec_w'], P['sec_col'](i, ns), thick=th))
    for (ln, dz, cnt, wd, cf) in P['covers']:
        for i in range(cnt):
            t = i / max(1, cnt - 1)
            b = E.lerp(Wr, t) + V(0, -0.002 * bone * 3, dz)
            fore.append(feather(b, b + V(0.0, ln, dz * 0.4), wd, cf, thick=th * 0.8))
    hv = V(P.get('hand_len', (Wr - E) * 0.8))
    hand = [loft([Wr, Wr + hv * 0.5, Wr + hv], [0.0042 * bone * 3, 0.0035 * bone * 3, 0.002 * bone * 3], [0.0038 * bone * 3, 0.003 * bone * 3, 0.002 * bone * 3], segs=8, res=3)]
    paint(hand[0], lambda p, n: hex_rgb(bc))
    npr = P['n_prim']
    p0, p1 = P.get('fan', (16, 6))
    for j in range(npr):
        t = j / (npr - 1)
        phi = math.radians(p0 + (p1 - p0) * t)
        L = P['prim_len'][j]
        b = Wr + hv * (0.15 + 0.6 * t) * 0.6 + V(0, 0.003 * bone * 3, -0.0008 * j * bone * 3)
        hand.append(feather(b, b + V(math.cos(phi) * L, math.sin(phi) * L, -0.003 * bone * 3), P['prim_w'], P['prim_col'](j, npr), thick=th, bulge=0.3))
    for i in range(P.get('n_pcov', 6)):
        t = i / 5
        phi = math.radians(p0 * 1.1 - (p0 - p1) * t)
        b = Wr + V(0.003, 0.0, 0.0015 + 0.0005 * i * bone * 3)
        hand.append(feather(b, b + V(math.cos(phi) * P['prim_len'][3] * 0.38, math.sin(phi) * P['prim_len'][3] * 0.38, 0), P['prim_w'] * 0.85, P['pcov_col'](i), thick=th * 0.8))
    return {'upper': merge(*up), 'fore': merge(*fore), 'hand': merge(*hand)}


FOLD_STD = None


def std_fold():
    return {'upper': cyc_fold((0, 1, -0.05), (-1, 0, 0)),
            'fore': cyc_fold((0, -1, -0.10), (1, 0, 0)),
            'hand': cyc_fold((0, 1, -0.22), (-1, 0, 0))}


def fold_quats(W, sgn_list=(1, -1)):
    """Local quaternions to go from OPEN-authored wing to folded pose (for wings authored open)."""
    out = {}
    order = ['upper', 'fore', 'hand']
    for sgn in sgn_list:
        d = {}
        prev = Matrix.Identity(3)
        for nm in order:
            R = prev.inverted() @ W[nm]
            if sgn < 0:
                Mx = Matrix.Diagonal((-1, 1, 1)); R = Mx @ R @ Mx
            d[nm] = R.to_quaternion()
            prev = W[nm]
        out['wing_l' if sgn > 0 else 'wing_r'] = d
    return out


def fold_meta(fq):
    return {k: {s: {'fold_quat_xyzw_three': quat_three(q), 'fold_euler_xyz_deg_blender': euler_deg(q)} for s, q in d.items()} for k, d in fq.items()}


def apply_quats(fq):
    for prefix, qs in fq.items():
        for seg, q in qs.items():
            ob = bpy.data.objects['%s_%s' % (prefix, seg)]
            ob.rotation_mode = 'QUATERNION'
            ob.rotation_quaternion = q
