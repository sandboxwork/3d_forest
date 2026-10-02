"""Soft contact-shadow / soot / stain decals (stacked translucent layers) - supplements the baked vertex AO where the receiver
(floor, plaster wall) belongs to another bundle."""
from kt_lib import *


def init_decal_mats():
    MAT('shadow', '#000000', rough=1.0, alpha=0.055, double=True, sharp=90)
    MAT('soot', '#140d08', rough=1.0, alpha=0.07, double=True, sharp=90)
    MAT('damp', '#201810', rough=0.4, alpha=0.1, double=True, sharp=90)


def rrect(cx, cy, hx, hy, rad, rot=0.0, n=4, z=0.0):
    rad = min(rad, hx, hy)
    pts = []
    corners = [(hx - rad, hy - rad, 0), (-hx + rad, hy - rad, 90), (-hx + rad, -hy + rad, 180), (hx - rad, -hy + rad, 270)]
    for (ox, oy, a0) in corners:
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((ox + rad * math.cos(a), oy + rad * math.sin(a)))
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]


def soft_shadow(cx, cy, hx, hy, rot=0.0, spread=0.12, layers=4, z=None, mat='shadow', rad=None):
    """floor shadow: nested rounded rects growing outward (each translucent) -> stepped soft falloff"""
    z0 = F + 0.0035 if z is None else z
    bm = bmesh.new()
    cl = bm.loops.layers.float_color.new('Col')
    ul = bm.loops.layers.uv.new('UVMap')
    for k in range(layers):
        g = spread * (k + 0.3) / layers
        pts = rrect(cx, cy, hx + g, hy + g, rad if rad else 0.04 + g, rot, 4)
        f = bm.faces.new([bm.verts.new((x, y, z0 + 0.0008 * k)) for x, y in pts])
        for l in f.loops:
            l[cl] = (1, 1, 1, 1)
            l[ul].uv = (0, 0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:
        if f.normal.z < 0:
            f.normal_flip()
    put(mat, bm, Matrix.Identity(4), g=2, flat=True)
    bm.free()


def wall_soot(cx, z0, z1, w=0.5, y=WY + 0.031, layers=4):
    """vertical soot smear on the back wall above/behind the stove pipe; faces -y"""
    bm = bmesh.new()
    cl = bm.loops.layers.float_color.new('Col')
    ul = bm.loops.layers.uv.new('UVMap')
    for k in range(layers):
        t = (k + 1) / layers
        hw = w * 0.5 * (0.45 + 0.55 * t)
        top = z0 + (z1 - z0) * (0.5 + 0.5 * t)
        pts = []
        n = 14
        for i in range(n + 1):
            a = math.pi * i / n
            pts.append((cx + hw * math.cos(a) * (1 - 0.15 * math.sin(a)), top + (top - z0) * 0.0 + hw * 1.6 * math.sin(a) * 0.6))
        pts += [(cx - hw * 1.2, z0), (cx + hw * 1.2, z0)]
        f = bm.faces.new([bm.verts.new((x, y - 0.0008 * k, z)) for x, z in pts])
        for l in f.loops:
            l[cl] = (1, 1, 1, 1)
            l[ul].uv = (0, 0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:
        if f.normal.y > 0:
            f.normal_flip()
    put('soot', bm, Matrix.Identity(4), flat=True)
    bm.free()


def build():
    init_decal_mats()
    # stove: footprint of hearth
    soft_shadow(-3.5, 2.835, 0.5, 0.45, spread=0.16, layers=5)
    # counter, hutch, pantry, barrel, sacks
    soft_shadow(-2.25, 2.93, 0.82, 0.32, spread=0.12)
    soft_shadow(-0.4, 3.0, 0.52, 0.24, spread=0.12)
    soft_shadow(0.5, 2.98, 0.35, 0.28, spread=0.12)
    soft_shadow(-1.2, 2.93, 0.29, 0.29, spread=0.12, rad=0.29)
    soft_shadow(1.08, 3.0, 0.2, 0.2, spread=0.1, rad=0.2)
    soft_shadow(1.12, 2.68, 0.18, 0.18, spread=0.1, rad=0.18)
    soft_shadow(-0.35, 2.45, 0.27, 0.2, rot=6, spread=0.1)
    soft_shadow(0.45, 2.42, 0.21, 0.21, spread=0.09, rad=0.21)
    soft_shadow(-0.85, 2.4, 0.15, 0.15, spread=0.08, rad=0.15)
    soft_shadow(-0.85, 2.2, 0.15, 0.15, spread=0.08, rad=0.15)
    soft_shadow(-3.55, 2.2, 0.32, 0.17, spread=0.1)
    # dining: under the table (broad, dark) and chairs
    soft_shadow(-3.0, -2.6, 0.62, 0.38, spread=0.22, layers=5)
    for (x, y, r) in ((-3.35, -1.85, 0), (-2.65, -1.85, 0), (-4.0, -2.6, 90), (-2.0, -2.6, 90)):
        soft_shadow(x, y, 0.21, 0.21, rot=r, spread=0.1, layers=3)
    # soot smear above the stove and a damp patch below the pump / barrel tap handled in storage
    wall_soot(-3.55, 1.25, 2.3, w=0.62)
