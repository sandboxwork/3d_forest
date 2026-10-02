"""Generic deer.py-style quadruped builder for farm mammals (cow, sheep, dog, cat).
cfg dict -> parts body/neck/head/jaw/ear_l/ear_r/(horn_l/horn_r)/tail/leg_{fl,fr,hl,hr}_{upper,lower,hoof|paw}"""
import sys
sys.path.insert(0, '/shared/river/assets/blender')
from animlib import *


def sstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def build(cfg):
    reset_scene()
    random.seed(cfg.get('seed', 3))
    nm = cfg['name']; k = cfg['k']
    fur = vcol_mat(nm + '_fur', '#ffffff', rough=cfg.get('rough', 0.92))
    hoofm = make_mat(nm + '_hoof', cfg['hoof_col'], rough=0.5)
    eyem = make_mat(nm + '_eye', cfg.get('eye_col', '#1d0f07'), rough=0.05)
    pupilm = make_mat(nm + '_pupil', '#050403', rough=0.1)
    nosem = make_mat(nm + '_nose', cfg['nose_col'], rough=0.25)
    mats_extra = {}
    coat = cfg['coat']

    def fin(name, bm, mats, pivot, parent=None, colorfn=None, noise=None):
        if noise:
            fur_noise(bm, **noise)
        if colorfn:
            paint(bm, colorfn)
            lay = bm.verts.layers.color.get('Col')
            for f in bm.faces:
                if f.material_index > 0 and len(mats) > 1:
                    for v in f.verts:
                        v[lay] = (1, 1, 1, 1)
        return part(name, bm, mats, pivot, parent=parent)

    # ---------------- body
    b = cfg['body']
    pts = [V(0, y, z) for y, z in zip(b['ys'], b['zc'])]
    bl = [loft(pts, b['rx'], b['rz'], segs=b.get('segs', 36), res=4)]
    for (c, r, rot) in b.get('blobs', []):
        for sx in ((1, -1) if c[0] != 0 else (1,)):
            bl.append(blob(V(c[0] * sx, c[1], c[2]), r, rot=(rot[0], rot[1], rot[2] * sx)))
    bm = merge(*bl)
    bm = fuse(bm, voxel=b['voxel'], smooth_iter=b.get('smooth', 10))
    if cfg.get('post_body'):
        bm = cfg['post_body'](bm)
    body_ob = fin('body', bm, [fur], V(0, 0, b['pivz']), colorfn=coat, noise=b.get('noise'))

    # ---------------- neck
    n = cfg['neck']
    nb = loft([V(*p) for p in n['pts']], n['rx'], n['rz'], segs=28, res=6)
    if n.get('blobs'):
        nbl = [nb] + [blob(V(*c), r, rot=rot) for (c, r, rot) in n['blobs']]
        nb = fuse(merge(*nbl), voxel=n['voxel'], smooth_iter=6)
    if cfg.get('post_neck'):
        nb = cfg['post_neck'](nb)
    neck_ob = fin('neck', nb, [fur], V(*n['pivot']), parent=body_ob, colorfn=cfg.get('neckcol', coat), noise=n.get('noise'))

    # ---------------- head
    h = cfg['head']
    P0 = V(*h['P0']); D = V(*h['D']).normalized(); U = V(0, D.z, -D.y).normalized()

    def hp(t, u=0.0, x=0.0):
        return P0 + D * t + U * u + V(x, 0, 0)

    ts = h['ts']; ups = h.get('ups', [0] * len(ts))
    hb = loft([hp(t, u) for t, u in zip(ts, ups)], h['rx'], h['rz'], segs=h.get('segs', 24), res=6)
    hl = [hb]
    for (t, u, x, r, rot) in h.get('blobs', []):
        for sx in (1, -1):
            hl.append(blob(hp(t, u, x * sx), r, rot=(rot[0], rot[1], rot[2] * sx)))
    hb = fuse(merge(*hl), voxel=h['voxel'], smooth_iter=6, smooth_f=0.5)
    extra = []
    nt, nu, nrx, nry, nrz = h['nose']
    nz = blob(hp(nt, nu), (nrx, nry, nrz), rot=(0.3, 0, 0), segs=14, rings=10); set_mat_index(nz, 2); extra.append(nz)
    for sx in (1, -1):
        tn, un, xn, rn = h['nostril']
        nn = blob(hp(tn, un, xn * sx), (rn, rn * 1.4, rn * 0.9), rot=(0.3, 0, sx * 0.3), segs=8, rings=6); set_mat_index(nn, 3); extra.append(nn)
        et, eu, ex, er = h['eye']
        ec = hp(et, eu, ex * sx)
        eb = blob(ec, (er * 0.9, er, er), segs=14, rings=10); set_mat_index(eb, 1); extra.append(eb)
        pr = h.get('pupil', (0.5, 0.9, 0.5))
        pb = blob(ec + V(sx * er * 0.62, -er * 0.35, 0), (er * pr[0] * 0.45, er * pr[1] * 0.55, er * pr[2] * 0.55), segs=10, rings=8); set_mat_index(pb, 3); extra.append(pb)
    hb = merge(hb, *extra)
    hcol = cfg['headcol']

    def headcol(p, n_):
        q = (p - P0).dot(D); uu = (p - P0).dot(U)
        return hcol(p, n_, q, uu)

    head_ob = fin('head', hb, [fur, eyem, nosem, pupilm], P0, parent=neck_ob, colorfn=headcol, noise=dict(amp=0.0008 * k, freq=70 / k, seed=4))

    # extras on head (whiskers etc.)
    if cfg.get('head_extra'):
        mats2, bm2, col2 = cfg['head_extra'](hp, D, U)
        whm = make_mat(nm + '_whisk', '#e8e2d6', rough=0.5)
        # merge into head by building a separate small object then join
        me = bpy.data.meshes.new('hx'); bm2.to_mesh(me); bm2.free()
        ob2 = bpy.data.objects.new('hx', me); bpy.context.scene.collection.objects.link(ob2)
        ob2.data.materials.append(whm)
        # append material to head & join
        head_ob.data.materials.append(whm)
        for p in ob2.data.polygons:
            p.material_index = len(head_ob.data.materials) - 1
        lay = ob2.data.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
        for i in range(len(ob2.data.vertices)):
            lay.data[i].color = (1, 1, 1, 1)
        bpy.ops.object.select_all(action='DESELECT')
        head_ob.select_set(True); ob2.select_set(True)
        bpy.context.view_layer.objects.active = head_ob
        bpy.ops.object.join()
        head_ob = bpy.context.view_layer.objects.active

    # ---------------- jaw
    j = cfg['jaw']
    JH = hp(j['t'], j['u'])
    jpts = [JH + D * t + U * (j.get('droop', -0.002) * k * t / 0.05) for t in j['ts']]
    jb = loft(jpts, j['rx'], j['rz'], segs=16, res=5)
    jcol = cfg['jawcol']
    jaw_ob = fin('jaw', jb, [fur], JH, parent=head_ob, colorfn=lambda p, n_: jcol(p, n_, (p - P0).dot(D), (p - P0).dot(U)))

    # ---------------- ears
    ear_obs = []
    e = cfg['ear']
    for sx, enm in ((1, 'ear_l'), (-1, 'ear_r')):
        base = hp(*e['base'][:2], e['base'][2] * sx)
        tip = base + V(e['tip'][0] * sx, e['tip'][1], e['tip'][2])
        nrm = V(e['nrm'][0] * sx, e['nrm'][1], e['nrm'][2])
        cv = e.get('curve', (0, 0, 0))
        eb_ = leaf_shape(base, tip, e['w'], e['th'], bulge=e.get('bulge', 0.45), segs=12, curve=(cv[0] * sx, cv[1], cv[2]), res=4, up=nrm)
        ecol = cfg['earcol']
        ear_obs.append(fin(enm, eb_, [fur], base, parent=head_ob,
                           colorfn=lambda p, n_, nrm=nrm, base=base, tip=tip: ecol(p, n_, n_.dot(nrm) >= 0, (p - base).length / (tip - base).length)))

    # ---------------- horns
    horn_obs = []
    if cfg.get('horn'):
        hr = cfg['horn']
        hm = make_mat(nm + '_horn', hr['col'], rough=0.45)
        for sx, hn in ((1, 'horn_l'), (-1, 'horn_r')):
            b0 = hp(*hr['base'][:2], hr['base'][2] * sx)
            hpts = [b0 + V(p[0] * sx, p[1], p[2]) for p in hr['pts']]
            hbm = loft(hpts, hr['r'], segs=12, res=6, cap_push=0.9)
            hcl = hr['colfn']
            horn_obs.append(fin(hn, hbm, [hm], b0, parent=head_ob, colorfn=lambda p, n_, b0=b0: hcl(p, n_, (p - b0).length)))

    # ---------------- tail
    t_ = cfg['tail']
    tpts = [V(*p) for p in t_['pts']]
    tb = loft(tpts, t_['rx'], t_['rz'], segs=14, res=4)
    for (c, r, rot) in t_.get('blobs', []):
        tb = merge(tb, blob(V(*c), r, rot=rot, segs=12, rings=8))
    if cfg.get('post_tail'):
        tb = cfg['post_tail'](tb)
    tail_ob = fin('tail', tb, [fur], tpts[0], parent=body_ob, colorfn=cfg.get('tailcol', coat))

    # ---------------- legs
    leg_objs = []
    L = cfg['legs']
    paw = cfg.get('foot') == 'paw'

    def leg(prefix, sx, J, hind):
        hip, knee, fet, toe = J['hip'], J['knee'], J['fet'], J['toe']
        mid = J.get('mid')

        def m(v):
            return V(v[0] * sx, v[1], v[2])
        up_pts = [m(hip)] + ([m(mid)] if mid else [m(tuple((a + c) / 2 for a, c in zip(hip, knee)))]) + [m(knee)]
        ub = loft(up_pts, J['ur'][0], J['ur'][1], segs=18, res=6, up=(0, -1, 0))
        uo = fin(prefix + '_upper', ub, [fur], m(hip), parent=body_ob, colorfn=coat, noise=dict(amp=0.0012 * k, freq=40 / k, seed=5))
        lr = J['lr']
        lp = [m(knee), m(tuple((a + c) / 2 for a, c in zip(knee, fet))), m(fet), m(fet) + V(0, -0.012 * k, -0.045 * k * (0.4 if paw else 1))]
        lb = loft(lp, list(lr[0]) + [lr[0][2] * 0.85], list(lr[1]) + [lr[1][2] * 0.85], segs=14, res=6, up=(0, -1, 0))
        kn = blob(m(knee), (lr[0][0] * 1.15, lr[1][0] * 1.2, 0.03 * k), segs=12, rings=8)
        lb = merge(lb, kn)
        lo = fin(prefix + '_lower', lb, [fur], m(knee), parent=uo, colorfn=coat)
        if not paw:
            hr_ = J['hoof']
            hpp = [m(fet) + V(0, -0.008 * k, -0.038 * k), m(toe) + V(0, 0, 0.022 * k), m(toe)]
            hbm = loft(hpp, hr_[:3], hr_[3:], segs=12, res=4, up=(0, -1, 0), power=2.4, cap_push=0.25)
            for dx in (-1, 1):
                hbm = merge(hbm, blob(m(fet) + V(dx * 0.012 * k, 0.02 * k, -0.03 * k), (0.008 * k, 0.012 * k, 0.012 * k), segs=8, rings=6))
            ho = fin(prefix + '_hoof', hbm, [hoofm], m(fet), parent=lo)
        else:
            pr = J['paw']   # (rx, ry, rz)
            c = m(fet) + V(0, -pr[1] * 0.55, -(m(fet).z - pr[2]) * 0.0 - (m(fet).z - pr[2] * 0.9))
            hbm = blob(c, pr, segs=14, rings=10)
            hbm = merge(hbm, loft([m(fet) + V(0, 0, 0.0), c + V(0, pr[1] * 0.4, 0.0)], [pr[0] * 0.75, pr[0] * 0.9], [pr[0] * 0.75, pr[2] * 0.9], segs=10, res=2))
            # toe grooves: 3 tiny toe bumps at front
            for dx in (-0.55, 0, 0.55):
                hbm = merge(hbm, blob(c + V(dx * pr[0] * sx * 0.9, -pr[1] * 0.78, -pr[2] * 0.25), (pr[0] * 0.38, pr[1] * 0.32, pr[2] * 0.7), segs=8, rings=6))
            pcol = cfg['pawcol']
            ho = fin(prefix + '_paw', hbm, [fur], m(fet), parent=lo, colorfn=pcol)
        leg_objs.extend([uo, lo, ho])

    for sx, side in ((1, 'l'), (-1, 'r')):
        leg('leg_f' + side, sx, L['front'], False)
        leg('leg_h' + side, sx, L['hind'], True)

    allparts = [body_ob, neck_ob, head_ob, jaw_ob, tail_ob] + ear_obs + horn_obs + leg_objs
    return dict(parts=allparts, body=body_ob, neck=neck_ob, head=head_ob, jaw=jaw_ob, tail=tail_ob, ears=ear_obs, horns=horn_obs, legs=leg_objs)


def make_meta(cfg, species, hs, length, head_alert, cycle=(1.3, 0.7), swing=None, graze=None, extra_parts=None, idle=None):
    foot = 'paw' if cfg.get('foot') == 'paw' else 'hoof'
    legs = {l: ['upper', 'lower', foot] for l in ('leg_fl', 'leg_fr', 'leg_hl', 'leg_hr')}
    hier_head = ['jaw', 'ear_l', 'ear_r'] + (['horn_l', 'horn_r'] if cfg.get('horn') else [])
    meta = {
        'species': species, 'forward': '-Y blender (+Z three.js)',
        'scale_hint_m': {'shoulder_height': hs, 'length': length, 'head_height_alert': head_alert},
        'parts': {'root': 'body', 'neck': 'neck', 'head': 'head', 'jaw': 'jaw', 'ears': ['ear_l', 'ear_r'], 'tail': 'tail',
                  'horns': ['horn_l', 'horn_r'] if cfg.get('horn') else [], 'left_is': '+X blender (+X three.js)'},
        'hierarchy': {'body': ['neck', 'tail', 'leg_*_upper'], 'neck': ['head'], 'head': hier_head,
                      'leg_xx_upper': ['leg_xx_lower'], 'leg_xx_lower': ['leg_xx_' + foot]},
        'gait': {'walk_cycle_s': cycle[0], 'trot_cycle_s': cycle[1], 'legs': legs,
                 'walk_order': ['leg_hl', 'leg_fl', 'leg_hr', 'leg_fr'],
                 'phase_offsets': {'leg_hl': 0.0, 'leg_fl': 0.25, 'leg_hr': 0.5, 'leg_fr': 0.75},
                 'rotation_axis': 'X (positive X rotation swings the lower end of a limb backward (+Y), i.e. foot goes back)',
                 'swing_deg': swing or {'upper': [-28, 28], 'lower_fore': [0, 55], 'lower_hind': [-60, 10], foot: [-15, 20]},
                 'note': 'Forelegs: carpus flexion = +X rot of lower (foot goes back/up). Hind: hock flexion = -X rot of lower in swing; upper swings +/-X about hip. Same convention as deer.json.'},
        'idle': idle or {'head_bob_deg': 4, 'ear_flick_deg': 15, 'tail_flick_deg': 12, 'breath': 'scale body Y 1.0..1.012 at 0.3 Hz'},
        'grazing_pose': graze or {'neck_rot_x_deg': 45, 'head_rot_x_deg': 15, 'jaw_chew_deg': [0, 8],
                                  'note': 'positive X rotation about pivot pitches the free end downward (nose goes down)'},
        'alert_pose': {'neck_rot_x_deg': -8, 'head_rot_x_deg': -5, 'ears_out_deg': 15},
        'pivots': 'each part origin = joint; see bundle parts[].pivot (three.js coords)',
    }
    if extra_parts:
        meta.update(extra_parts)
    return meta


def finish(cfg, res, name, meta, views, target):
    parts = res['parts']
    print(export_bundle(OUT_DIR + '/animal_%s.json' % name, parts, meta))
    write_meta('animal_%s' % name, meta)
    print('tris', tri_count(parts))
    if os.environ.get('PREVIEW', '1') == '1':
        preview_grid(PREVIEW_DIR + '/vp_animal_%s.png' % name, views, target=target)
