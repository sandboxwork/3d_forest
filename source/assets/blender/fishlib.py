import sys
sys.path.insert(0, '/shared/river/assets/blender')
from animlib import *


def stations_loft(st, segs=40, res=12, power=2.0):
    pts = [V(0, s[0], s[3]) for s in st]
    return loft(pts, [s[1] for s in st], [s[2] for s in st], segs=segs, res=res, power=power, cap_push=0.9)


def fin_fan(ra, rb, da, db, Lfn, cols=12, rows=5, nrm=None, ridge=0.0006, rays=None, sag=0.0):
    """Fan-shaped membrane fin. ra/rb root line endpoints, da/db ray direction at ends, Lfn(u)->length.
    Ridges (fin rays) displaced along nrm. Returns bmesh (single sheet, use double-sided material)."""
    ra, rb, da, db = V(ra), V(rb), V(da), V(db)
    if nrm is None:
        nrm = (rb - ra).cross((da + db)); 
    nrm = V(nrm).normalized()
    rays = rays or cols
    n = cols * 2
    bm = bmesh.new()
    grid = []
    for i in range(n + 1):
        u = i / n
        root = ra.lerp(rb, u)
        d = da.lerp(db, u).normalized()
        L = Lfn(u)
        row = []
        ridge_v = math.cos(u * rays * math.pi * 2) * 0.5 + 0.5
        for j in range(rows + 1):
            v = j / rows
            p = root + d * (L * v)
            p += nrm * (ridge * ridge_v * (0.3 + 0.7 * v) + sag * v * v)
            row.append(bm.verts.new(p))
        grid.append(row)
    for i in range(n):
        for j in range(rows):
            bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm
