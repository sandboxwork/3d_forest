"""Helpers/materials for the water-edge plants bundle."""
from flora_lib import *


def init_water_mats():
    mat('w_stem', '#7aa23f', rough=0.6, sss=0.1)
    mat('w_leaf', '#5e9a34', rough=0.5, sss=0.15)
    mat('w_leaf_dark', '#3f7a2a', rough=0.45)
    mat('w_leaf_glossy', '#3e8030', rough=0.3, sss=0.1)
    mat('w_grass', '#6aa03a', rough=0.55, sss=0.15)
    mat('w_grass_dry', '#b9a866', rough=0.65)
    mat('w_seed', '#b59a52', rough=0.7)
    mat('cattail_brown', '#5a3418', rough=0.8)
    mat('cattail_spike', '#b8a04e', rough=0.75)
    mat('reed_stem', '#b8a866', rough=0.6)
    mat('reed_plume', '#b8967a', rough=0.75)
    mat('iris_petal', '#f8d21c', rough=0.5, sss=0.25)
    mat('iris_style', '#f8dc50', rough=0.5, sss=0.25)
    mat('iris_bud', '#9ab64a', rough=0.5)
    mat('lilypad', '#418236', rough=0.3, sss=0.05)
    mat('lily_white', '#fffdf6', rough=0.5, sss=0.3)
    mat('lily_pink', '#f6b2cc', rough=0.5, sss=0.3)
    mat('lily_stamen', '#f6d020', rough=0.6)
    mat('marigold_petal', '#ffd414', rough=0.22, sss=0.2)
    mat('fern_frond', '#6ea83a', rough=0.5, sss=0.2)
    mat('fern_rachis', '#8a9a4a', rough=0.6)
    mat('horsetail_stem', '#8ab060', rough=0.55)
    mat('horsetail_node', '#4a3a28', rough=0.7)
    mat('horsetail_cone', '#8a6a48', rough=0.7)
    mat('mush_white', '#f2eee2', rough=0.6)
    mat('mush_red', '#d4281a', rough=0.35)
    mat('mush_brown', '#7a4a24', rough=0.45)
    mat('mush_pore', '#d6c87a', rough=0.75)
    mat('mush_stem_cream', '#f0e4c8', rough=0.65)
    mat('mush_chant', '#eaa418', rough=0.5, sss=0.25)
    mat('mush_honey', '#c59858', rough=0.55)
    mat('mush_honey_stem', '#b89a68', rough=0.65)


TAPER = lambda u: np.clip(1 - u ** 2.3, 0, 1)
TAPER_SOFT = lambda u: np.clip(1 - u ** 3.2, 0, 1) * (0.75 + 0.25 * np.minimum(1, u * 8))


def blade_at(g, m, patch, pos, az, elev, yawroll=0.0):
    radial = np.array([math.cos(az), math.sin(az), 0.0]); Z = np.array([0, 0, 1.0])
    ydir = math.cos(elev) * radial + math.sin(elev) * Z
    nrm = -math.sin(elev) * radial + math.cos(elev) * Z
    M = orient(np.asarray(pos, float), ydir, nrm)
    if yawroll:
        M = M @ Ry(yawroll)
    g.add(m, patch, M)


def grass_blade(L, W, rng, bend=(-1.3, -0.5), cols=None, fold=0.35, twist=(-0.6, 0.6), nu=6, widthfn=TAPER_SOFT, side=0.0):
    cols = cols or [(0, '#3a6a24'), (0.45, '#5f9a35'), (1, '#8fae48')]
    return blade(L, W, nu=nu, nv=2, widthfn=widthfn, bend=bend, fold=fold, twist=twist, cols=cols, mid=0.25, side=side, lod=False)
