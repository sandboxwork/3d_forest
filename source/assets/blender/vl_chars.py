"""vl_chars: assemble villagers. Usage: VL=man blender -b --python vl_chars.py"""
import sys, os, collections
sys.path.insert(0, '/shared/river/assets/blender')
from vl_cloth import *
import vl_extras as X

PARTS = ['pelvis', 'torso', 'neck_head', 'jaw', 'arm_l_upper', 'arm_l_lower', 'hand_l', 'arm_r_upper', 'arm_r_lower', 'hand_r',
         'leg_l_upper', 'leg_l_lower', 'foot_l', 'leg_r_upper', 'leg_r_lower', 'foot_r']


def place_head(c, bm):
    bmesh.ops.scale(bm, verts=bm.verts[:], vec=(c.hs, c.hs, c.hs))
    translate(bm, c.head_c)
    return bm


def head_parts(c, B):
    H = make_head(c.F, c.kind == 'child')
    c.head = H
    for k in ('head', 'ears', 'eyes', 'lids'):
        B['neck_head'].append(place_head(c, H[k]))
    B['jaw'].append(place_head(c, H['jaw']))
    # neck
    top = c.head_c + V(0, 0.018 * c.hs, -0.07 * c.hs)
    nb = c.nb
    r = c.neck_r
    mid = nb.lerp(top, 0.5) + V(0, -0.004, 0)
    nk = tube([nb + V(0, 0, -0.03), nb, mid, top], [r * 1.25, r * 1.12, r * 0.98, r * 1.0], [r * 1.2, r * 1.1, r * 1.0, r * 1.05], segs=12, res=2, caps=(True, False))
    B['neck_head'].append(setm(nk, 'skin'))
    c.jaw_pivot = c.head_c + V(0, 0.012 * c.hs, -0.03 * c.hs)


def finish_all(c, B, props=None):
    cfg = c.cfg
    piv = {
        'pelvis': V(0, 0, c.z['hip']),
        'torso': V(0, c.ys(c.z['waist']), c.z['waist']),
        'neck_head': c.nb,
        'jaw': c.jaw_pivot,
    }
    for s in (1, -1):
        t = side_tag(s)
        piv['arm_%s_upper' % t] = c.arms[s]['S']
        piv['arm_%s_lower' % t] = c.arms[s]['E']
        piv['hand_%s' % t] = c.arms[s]['W']
        piv['leg_%s_upper' % t] = c.legs[s]['H']
        piv['leg_%s_lower' % t] = c.legs[s]['K']
        piv['foot_%s' % t] = c.legs[s]['A']
    parent = {'torso': 'pelvis', 'neck_head': 'torso', 'jaw': 'neck_head'}
    for t in 'lr':
        parent['arm_%s_upper' % t] = 'torso'; parent['arm_%s_lower' % t] = 'arm_%s_upper' % t; parent['hand_%s' % t] = 'arm_%s_lower' % t
        parent['leg_%s_upper' % t] = 'pelvis'; parent['leg_%s_lower' % t] = 'leg_%s_upper' % t; parent['foot_%s' % t] = 'leg_%s_lower' % t
    objs = {}
    nmaps = {}
    g = c.head['grid']; g.normal_update()
    nm = {}
    for v in g.verts:
        p = v.co * c.hs + c.head_c
        nm[(round(p.x, 4), round(p.y, 4), round(p.z, 4))] = v.normal.copy()
    nmaps['neck_head'] = nm; nmaps['jaw'] = nm
    for name in PARTS:
        lst = B.get(name, [])
        bm = merge(*lst) if lst else bmesh.new()
        if not lst:
            bmesh.ops.create_cube(bm, size=0.001)
            setm(bm, 'skin')
        objs[name] = finish_part(name, bm, piv[name], objs.get(parent.get(name)), nmap=nmaps.get(name))
    for pname, (bm, pv, par) in (props or {}).items():
        objs[pname] = finish_part(pname, bm, pv, objs[par])
    c.piv = piv
    return objs


def build(cfg, garments):
    reset_scene()
    mk_mats(**cfg.get('mats', {}))
    c = make_ctx(cfg)
    B = collections.defaultdict(list)
    head_parts(c, B)
    c.hf = {}
    for s in (1, -1):
        c.hf[s] = hand_frame(c, s, cfg.get('hand_dir', {}).get(s, c.arms[s]['d2']))
    props = garments(c, B)
    # hands
    for s in (1, -1):
        t = side_tag(s)
        mode = cfg.get('hand_mode', {}).get(s, 'relaxed')
        a = c.arms[s]
        fdir = cfg.get('hand_dir', {}).get(s, a['d2'])
        hb, fr = hand_geom(c, s, a['W'], fdir, mode)
        B['hand_%s' % t].append(hb)
    objs = finish_all(c, B, props)
    return c, objs


def preview(c, objs, path, tag):
    H = c.H
    mid = H * 0.52
    d = H * 1.65
    hc = c.head_c
    views = [((0, -d, mid + 0.1), (0, 0, mid), 50), ((d, 0, mid + 0.1), (0, 0, mid), 50),
             ((d * .72, -d * .72, mid + 0.25), (0, 0, mid), 50), ((-d * .7, d * .7, mid + 0.25), (0, 0, mid), 50),
             ((0.0, -0.75, hc.z), (0, 0, hc.z), 85), ((0.5, -0.75, hc.z + 0.05), (0, 0, hc.z), 85)]
    vl_grid(path, views, res=(520, 620), samples=24, cols=3, tag=tag)


def tris(objs):
    return tri_count(list(objs.values()))
