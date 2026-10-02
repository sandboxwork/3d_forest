"""Materials for the living zone. UV unit == one texture tile (tsc = 1/tile_size_m); uvscale stays 1.0."""
from lv_lib import *

M = {}
MATS = M
TILE = {'pbr_wood_floor': 1.0, 'pbr_wood_pine': 0.6, 'pbr_wood_oak': 0.5, 'pbr_wood_dark': 0.6, 'pbr_plaster': 1.0,
        'pbr_fabric_linen': 0.25, 'pbr_fabric_wool': 0.3, 'pbr_fabric_burlap': 0.25, 'pbr_leather': 0.3,
        'pbr_rug_braided': 0.4, 'pbr_iron': 0.4, 'pbr_brass_copper': 0.3, 'pbr_ceramic': 0.2, 'pbr_stone_fireplace': 1.0,
        'pbr_paper': 0.2, 'pbr_book_cloth': 0.15, 'pbr_wicker': 0.3}


def tex_mean(tex):
    p = '/shared/river/assets/tex/%s.jpg' % tex
    if not os.path.exists(p):
        return None
    im = bpy.data.images.load(p)
    w, h = im.size
    a = np.array(im.pixels[:], dtype=np.float32).reshape(h * w, im.channels)[:, :3]
    lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    bpy.data.images.remove(im)
    return lin.mean(0)


TARGET = {'wood_oak': (0.45, 0.28, 0.15), 'wood_dark': (0.36, 0.22, 0.13), 'wood_walnut': (0.32, 0.19, 0.11), 'wood_pine': (0.6, 0.45, 0.28),
          'wood_painted': (0.85, 0.82, 0.72), 'endgrain': (0.62, 0.46, 0.28), 'fabric_linen': (0.7, 0.62, 0.48), 'fabric_wool': (0.7, 0.62, 0.48),
          'curtain': (0.75, 0.68, 0.52), 'burlap': (0.45, 0.35, 0.2), 'yarn': (0.7, 0.6, 0.45), 'felt': (0.7, 0.6, 0.45), 'leather': (0.25, 0.15, 0.09),
          'book_cloth': (0.3, 0.1, 0.1), 'paper': (0.85, 0.8, 0.65), 'wicker': (0.75, 0.55, 0.3), 'terracotta': (0.7, 0.3, 0.18), 'ceramic': (0.9, 0.88, 0.8),
          'iron_black': (0.1, 0.1, 0.11), 'iron_cast': (0.08, 0.08, 0.09), 'brass': (0.8, 0.52, 0.14)}
FACTOR = {'wood_oak': 0.42, 'wood_dark': 0.34, 'wood_walnut': 0.2, 'wood_pine': 0.5, 'wood_painted': 0.8, 'endgrain': 0.55, 'fabric_linen': 0.72,
          'fabric_wool': 0.72, 'curtain': 0.78, 'burlap': 0.6, 'yarn': 0.72, 'felt': 0.72, 'leather': 0.62, 'book_cloth': 0.62, 'paper': 0.85, 'wicker': 0.45,
          'terracotta': 0.62, 'ceramic': 1.0, 'iron_black': 0.25, 'iron_cast': 0.14, 'brass': 1.0}
NORMALIZE = ['wood_oak', 'wood_dark', 'wood_walnut', 'wood_pine', 'wood_painted', 'endgrain', 'fabric_linen', 'fabric_wool', 'curtain', 'burlap', 'yarn', 'felt',
             'leather', 'book_cloth', 'paper', 'wicker', 'terracotta', 'ceramic', 'iron_black', 'iron_cast', 'brass']


def init_mats():
    def m(name, color='#ffffff', tex=None, **kw):
        tsc = 1.0 / TILE[tex] if tex in TILE else 1.0
        M[name] = MAT(name, color, tex=tex, tsc=tsc, **kw)
    # woods: colour carried by vertex colours; base is a neutral warm tint
    m('wood_oak', '#f2dcc0', 'pbr_wood_oak', rough=0.5)
    m('wood_dark', '#e8c9a8', 'pbr_wood_dark', rough=0.45)
    m('wood_walnut', '#d9b494', 'pbr_wood_oak', rough=0.5)
    m('wood_pine', '#f5e2c4', 'pbr_wood_pine', rough=0.6)
    m('wood_painted', '#ffffff', 'pbr_wood_pine', rough=0.7)
    m('fabric_linen', '#ffffff', 'pbr_fabric_linen', rough=0.95)
    m('fabric_wool', '#ffffff', 'pbr_fabric_wool', rough=1.0)
    m('curtain', '#ffffff', 'pbr_fabric_linen', rough=0.95, double=True)
    m('burlap', '#ffffff', 'pbr_fabric_burlap', rough=1.0)
    m('leather', '#ffffff', 'pbr_leather', rough=0.55)
    m('book_cloth', '#ffffff', 'pbr_book_cloth', rough=0.85)
    m('rug_braided', '#ffffff', 'pbr_rug_braided', rough=1.0)
    m('iron_black', '#6a6a70', 'pbr_iron', rough=0.5, metal=0.6)
    m('iron_cast', '#505056', 'pbr_iron', rough=0.62, metal=0.55)
    m('brass', '#f0c060', 'pbr_brass_copper', rough=0.3, metal=0.85)
    m('copper', '#e0804a', 'pbr_brass_copper', rough=0.33, metal=0.8)
    m('pewter', '#b8b8bc', None, rough=0.38, metal=0.75)
    m('ceramic', '#ffffff', 'pbr_ceramic', rough=0.22)
    m('terracotta', '#d8825a', 'pbr_ceramic', rough=0.8)
    m('paper', '#f4ead0', 'pbr_paper', rough=0.9)
    m('wicker', '#f0c890', 'pbr_wicker', rough=0.85)
    m('bark', '#ffffff', 'bark', rough=0.95)
    m('endgrain', '#ead2a8', 'pbr_wood_pine', rough=0.8)
    # un-textured
    m('glass', '#e6f2f0', rough=0.04, alpha=0.18, double=True)
    m('glass_amber', '#e8b058', rough=0.06, alpha=0.5, double=True)
    m('flame', '#ffcf70', emit='#ff9a30', emit_strength=7.0, rough=0.5)
    m('wax', '#f0e6c8', rough=0.45)
    m('fur', '#ffffff', rough=1.0, double=True)
    m('yarn', '#ffffff', 'pbr_fabric_wool', rough=1.0)
    m('ink', '#16161c', rough=0.35)
    m('gilt', '#e8c070', rough=0.28, metal=0.9)
    m('tea', '#5a2f12', rough=0.05)
    m('felt', '#ffffff', 'pbr_fabric_wool', rough=1.0)
    m('foliage', '#ffffff', rough=0.9, double=True)
    m('photo', '#ffffff', rough=0.85, double=True)
    m('contact_shadow', '#000000', rough=1.0, alpha=0.11)
    # texture-aware vertex colours: final colour = texture * (target / texture mean)  (texture keeps only the detail/luminance variation)
    VCNORM.clear(); VCDEFAULT.clear(); VCMULT.clear()
    means = {}
    for name in NORMALIZE:
        tx = M[name].get('tex', '')
        if not tx:
            continue
        if tx not in means:
            means[tx] = tex_mean(tx)
        mn = means[tx]
        if mn is None:
            continue
        mn = np.maximum(mn, 0.02)
        VCDEFAULT[name] = TARGET[name]
        if name == 'brass':
            VCMULT.add(name)
        fk = FACTOR.get(name, 1.0)
        VCNORM[name] = ((fk / mn[0], fk / mn[1], fk / mn[2]), 8.0)
        b = M[name].node_tree.nodes.get('Principled BSDF')
        b.inputs['Base Color'].default_value = (1, 1, 1, 1)
        M[name]['rgb'] = [1.0, 1.0, 1.0]
    return M


def painting_mat(n):
    nm = 'lv_painting_%d' % n
    if nm not in M:
        M[nm] = MAT(nm, '#ffffff', tex=nm, tsc=1.0, rough=0.7)
    return M[nm]


def tex_mat(name, tex, color='#ffffff', rough=0.9, double=False):
    if name not in M:
        M[name] = MAT(name, color, tex=tex, tsc=1.0, rough=rough, double=double)
    return M[name]
