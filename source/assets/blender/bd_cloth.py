"""Cloth simulation helpers (Blender cloth modifier, stepped frame-by-frame in background mode) with an on-disk cache."""
from bd_lib import *

CACHE = '/tmp/bd_cloth_cache'
os.makedirs(CACHE, exist_ok=True)

PRESETS = {
    # quality, mass, tension, compression, shear, bending, air, tension_damp, bend_damp
    'linen': dict(quality=10, mass=0.25, tension=12, compression=12, shear=8, bending=0.35, air=1.5, tdamp=5, bdamp=0.5),
    'quilt': dict(quality=12, mass=0.9, tension=22, compression=22, shear=16, bending=4.0, air=2.0, tdamp=10, bdamp=1.0),
    'heavy': dict(quality=10, mass=0.6, tension=20, compression=20, shear=15, bending=1.5, air=1.5, tdamp=8, bdamp=1.0),
    'silk': dict(quality=8, mass=0.12, tension=6, compression=6, shear=3, bending=0.05, air=1.5, tdamp=3, bdamp=0.3),
    'curtain': dict(quality=8, mass=0.18, tension=10, compression=10, shear=6, bending=0.08, air=1.2, tdamp=5, bdamp=0.4),
    'wool': dict(quality=10, mass=0.5, tension=18, compression=18, shear=12, bending=1.2, air=1.5, tdamp=8, bdamp=0.8),
    'pillow': dict(quality=8, mass=0.04, tension=40, compression=40, shear=30, bending=1.5, air=1.0, tdamp=10, bdamp=1.0),
    'coat': dict(quality=10, mass=0.6, tension=25, compression=25, shear=20, bending=3.0, air=1.5, tdamp=10, bdamp=1.0),
}


def grid(nx, ny, sx, sy, f=lambda x, y: (x, y, 0.0)):
    """(nx+1)*(ny+1) verts over [-sx/2,sx/2]x[-sy/2,sy/2] (u along x, v along y); f maps (x,y)->3D. returns verts, faces, uv(meters)"""
    verts, uv = [], []
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = -sx / 2 + sx * i / nx; y = -sy / 2 + sy * j / ny
            verts.append(f(x, y)); uv.append((x + sx / 2, y + sy / 2))
    faces = []
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    return np.array(verts, np.float32), faces, np.array(uv, np.float32)


def _collider(name, bm_or_vf):
    if isinstance(bm_or_vf, bmesh.types.BMesh):
        me = bpy.data.meshes.new(name); bm_or_vf.to_mesh(me)
    else:
        v, f = bm_or_vf
        me = bpy.data.meshes.new(name); me.from_pydata([tuple(x) for x in v], [], [tuple(x) for x in f]); me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    cm = ob.modifiers.new('Collision', 'COLLISION')
    cm.settings.thickness_outer = 0.004
    cm.settings.thickness_inner = 0.01
    cm.settings.use_culling = False
    cm.settings.use_normal = False
    cm.settings.cloth_friction = 6.0
    return ob


def simulate(name, verts, faces, pins=None, frames=60, colliders=(), preset='linen', collision_dist=0.006, self_coll=False,
             self_dist=0.004, pin_stiff=1.0, pressure=None, shape_target=None, shape_frames=(1, 30), gravity=None,
             substeps=None, use_cache=True, extra=None, damping_scale=1.0, subframes=None, shrink=None):
    """Run a cloth sim and return final vertex positions (np.float32 Nx3).
    pins: list of vertex indices (pinned to the (optionally shape-key animated) rest position).
    shape_target: np array Nx3 of target positions (pinned verts move from rest to target over shape_frames).
    colliders: list of bmesh or (verts, faces)."""
    cpath = os.path.join(CACHE, name + '.npy')
    if use_cache and os.path.exists(cpath):
        return np.load(cpath)
    sc = bpy.context.scene
    verts = np.asarray(verts, np.float32)
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.update()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    if pins is not None and len(pins):
        vg = ob.vertex_groups.new(name='pin')
        vg.add([int(i) for i in pins], 1.0, 'REPLACE')
    if shape_target is not None:
        ob.shape_key_add(name='Basis')
        sk = ob.shape_key_add(name='Target')
        arr = np.asarray(shape_target, np.float32)
        sk.data.foreach_set('co', arr.ravel())
        sk.value = 0.0
        sk.keyframe_insert('value', frame=shape_frames[0])
        sk.value = 1.0
        sk.keyframe_insert('value', frame=shape_frames[1])
    cols = []
    for k, c in enumerate(colliders):
        cols.append(_collider('col%d' % k, c))
    cm = ob.modifiers.new('Cloth', 'CLOTH')
    P = PRESETS[preset]
    s = cm.settings
    s.quality = P['quality']; s.mass = P['mass']
    s.tension_stiffness = P['tension']; s.compression_stiffness = P['compression']; s.shear_stiffness = P['shear']
    s.bending_stiffness = P['bending']
    s.air_damping = P['air']
    s.tension_damping = P['tdamp'] * damping_scale; s.compression_damping = P['tdamp'] * damping_scale
    s.shear_damping = P['tdamp'] * damping_scale; s.bending_damping = P['bdamp'] * damping_scale
    if pins is not None and len(pins):
        s.vertex_group_mass = 'pin'
        s.pin_stiffness = pin_stiff
    if pressure is not None:
        s.use_pressure = True
        s.uniform_pressure_force = pressure
        s.use_pressure_volume = False
        s.pressure_factor = 1.0
    if shrink is not None:
        s.shrink_min = shrink
    cs = cm.collision_settings
    cs.use_collision = True
    cs.collision_quality = 5
    cs.distance_min = collision_dist
    cs.use_self_collision = self_coll
    cs.self_distance_min = self_dist
    cs.self_friction = 5
    cs.impulse_clamp = 0.0
    if extra:
        extra(cm)
    cm.point_cache.frame_start = 1
    cm.point_cache.frame_end = frames
    sc.frame_start = 1; sc.frame_end = frames
    if gravity is not None:
        sc.gravity = gravity
    sc.frame_set(1)
    for f in range(1, frames + 1):
        sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    out = np.zeros(len(verts) * 3, np.float32)
    ev.data.vertices.foreach_get('co', out)
    out = out.reshape(-1, 3)
    # cleanup
    for c in cols:
        me_c = c.data
        bpy.data.objects.remove(c); bpy.data.meshes.remove(me_c)
    bpy.data.objects.remove(ob); bpy.data.meshes.remove(me)
    sc.frame_set(1)
    if use_cache:
        np.save(cpath, out)
    return out


def box_collider(c, s, rot=None, bev=0.0, Mx=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= s[0]; v.co.y *= s[1]; v.co.z *= s[2]
    if bev > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:] + bm.faces[:], offset=bev, segments=2, profile=0.5, affect='EDGES', clamp_overlap=True)
    bmesh.ops.transform(bm, matrix=Mx if Mx is not None else xf(c, rot), verts=bm.verts)
    return bm


def cyl_collider(c, r, h, axis='z', seg=16, Mx=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=h)
    M0 = {'z': Matrix.Identity(4), 'x': rotm((0, 90, 0)), 'y': rotm((90, 0, 0))}[axis]
    bmesh.ops.transform(bm, matrix=(Mx if Mx is not None else xf(c)) @ M0, verts=bm.verts)
    return bm


def mesh_to_obj_list(verts, faces, name='cloth'):
    return mesh_obj_from_arrays(name, verts, faces)


def solidify_np(verts, faces, thickness, offset=-1.0):
    """apply Blender Solidify modifier to arrays -> (verts, faces) numpy/list via temp object (keeps ordering of the original verts first)"""
    me = bpy.data.meshes.new('_sol'); me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces]); me.update()
    ob = bpy.data.objects.new('_sol', me); bpy.context.scene.collection.objects.link(ob)
    m = ob.modifiers.new('S', 'SOLIDIFY'); m.thickness = thickness; m.offset = offset; m.use_even_offset = True
    m.nonmanifold_thickness_mode = 'CONSTRAINTS'
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); ev = ob.evaluated_get(dg)
    me2 = bpy.data.meshes.new_from_object(ev, depsgraph=dg)
    v = np.zeros(len(me2.vertices) * 3, np.float32); me2.vertices.foreach_get('co', v)
    f = [tuple(p.vertices) for p in me2.polygons]
    bpy.data.objects.remove(ob); bpy.data.meshes.remove(me); bpy.data.meshes.remove(me2)
    return v.reshape(-1, 3), f


def cloth_to_bm(verts, faces, uv, col=(1, 1, 1), cfn=None, skip=None):
    """arrays -> bmesh with UV layer (uv given per original vertex, in whatever units put() expects) for put()."""
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    vs = [bm.verts.new(tuple(v)) for v in verts]
    for f in faces:
        if skip is not None and skip(np.mean([verts[i] for i in f], axis=0)):
            continue
        try:
            nf = bm.faces.new([vs[i] for i in f])
        except ValueError:
            continue
        nf.smooth = True
        for l, i in zip(nf.loops, f):
            l[ul].uv = tuple(uv[i])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def smooth_np(verts, faces, iters=1, lam=0.3):
    n = len(verts)
    nb = [set() for _ in range(n)]
    for f in faces:
        for a in range(len(f)):
            nb[f[a]].add(f[(a + 1) % len(f)]); nb[f[a]].add(f[(a - 1) % len(f)])
    v = verts.copy()
    for _ in range(iters):
        nv = v.copy()
        for i in range(n):
            if nb[i]:
                nv[i] = v[i] + lam * (np.mean([v[j] for j in nb[i]], axis=0) - v[i])
        v = nv
    return v


def vertex_normals(verts, faces):
    n = np.zeros_like(verts)
    for f in faces:
        p = verts[list(f)]
        fn = np.cross(p[1] - p[0], p[2] - p[0]) if len(f) >= 3 else np.zeros(3)
        if len(f) == 4:
            fn = np.cross(p[2] - p[0], p[3] - p[1])
        for i in f:
            n[i] += fn
    l = np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    return n / l


def solid_bm(verts, faces, uv, thick, offset=-1.0, smooth_n=1, skip_bottom=None):
    """robust cloth thickness: duplicate the surface along (smoothed) vertex normals, close the boundary with rim quads.
    offset=-1 -> thickness grows against the normal (top surface stays put); +1 -> along the normal; 0 -> centred."""
    verts = np.asarray(verts, np.float32)
    n = vertex_normals(verts, faces)
    if offset != 0.0 and n[:, 2].mean() < 0:
        faces = [tuple(reversed(f)) for f in faces]
        n = vertex_normals(verts, faces)
    for _ in range(smooth_n):
        nn = n.copy()
        for f in faces:
            idx = list(f)
            m = n[idx].mean(axis=0)
            for i in idx:
                nn[i] += m * 0.25
        l = np.linalg.norm(nn, axis=1, keepdims=True) + 1e-9
        n = nn / l
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    top_off = {-1.0: 0.0, 1.0: thick, 0.0: thick / 2}[offset]
    bot_off = top_off - thick
    vt = [bm.verts.new(tuple(verts[i] + n[i] * top_off)) for i in range(len(verts))]
    vb = [bm.verts.new(tuple(verts[i] + n[i] * bot_off)) for i in range(len(verts))]
    edge_count = {}
    for f in faces:
        try:
            fc = bm.faces.new([vt[i] for i in f]); fc.smooth = True
            for l, i in zip(fc.loops, f):
                l[ul].uv = tuple(uv[i])
            if skip_bottom is None or not skip_bottom(verts[list(f)].mean(axis=0)):
                fb = bm.faces.new([vb[i] for i in reversed(f)]); fb.smooth = True
                for l, i in zip(fb.loops, reversed(f)):
                    l[ul].uv = tuple(uv[i])
        except ValueError:
            pass
        for k in range(len(f)):
            e = (f[k], f[(k + 1) % len(f)])
            key = tuple(sorted(e))
            edge_count.setdefault(key, []).append(e)
    for key, lst in edge_count.items():
        if len(lst) == 1:
            a, b = lst[0]
            try:
                fc = bm.faces.new([vt[a], vb[a], vb[b], vt[b]])
                fc.smooth = False
                for l, uvv in zip(fc.loops, [(uv[b][0], 0), (uv[b][0], thick), (uv[a][0], thick), (uv[a][0], 0)]):
                    l[ul].uv = uvv
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm
