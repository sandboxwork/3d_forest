"""Materials for the kitchen/dining bundle.  Texture names refer to the PBR library (tile sizes in meters)."""
from kt_lib import *

# tint colours are multiplied with the albedo map and with the Col vertex colours at runtime
PBR_TINT = {   # fallback colours used ONLY by preview when the pbr_* jpg is missing (never exported)
    'pbr_wood_pine': (0.82, 0.60, 0.36), 'pbr_wood_oak': (0.62, 0.42, 0.24), 'pbr_wood_dark': (0.34, 0.21, 0.12),
    'pbr_wood_floor': (0.60, 0.42, 0.26), 'pbr_plaster': (0.88, 0.84, 0.76), 'pbr_fabric_linen': (0.88, 0.84, 0.74),
    'pbr_fabric_wool': (0.8, 0.76, 0.68), 'pbr_fabric_burlap': (0.78, 0.66, 0.46), 'pbr_leather': (0.5, 0.32, 0.2),
    'pbr_rug_braided': (0.7, 0.55, 0.4), 'pbr_iron': (0.42, 0.42, 0.44), 'pbr_brass_copper': (0.85, 0.55, 0.3),
    'pbr_ceramic': (0.95, 0.94, 0.9), 'pbr_stone_fireplace': (0.5, 0.48, 0.45), 'pbr_paper': (0.93, 0.88, 0.76),
    'pbr_book_cloth': (0.6, 0.4, 0.3), 'pbr_wicker': (0.78, 0.58, 0.32)}
HI_FALLBACK = {'pbr_wood_pine': 'hi_wood', 'pbr_wood_oak': 'hi_wood', 'pbr_wood_dark': 'hi_wood', 'pbr_wood_floor': 'hi_wood',
               'pbr_plaster': 'hi_plaster', 'pbr_fabric_linen': 'hi_weave', 'pbr_fabric_wool': 'hi_knit', 'pbr_fabric_burlap': 'hi_weave',
               'pbr_leather': 'hi_leather', 'pbr_iron': 'hi_metal', 'pbr_brass_copper': 'hi_metal', 'pbr_ceramic': None,
               'pbr_stone_fireplace': 'hi_plaster', 'pbr_paper': None, 'pbr_wicker': 'hi_wicker', 'pbr_book_cloth': 'hi_weave'}


def init_mats():
    def m(name, color='#ffffff', **kw):
        return MAT(name, color, **kw)
    # --- wood (grain along local v)
    m('wood_pine', '#ffffff', tex='pbr_wood_pine', tile=0.6, rough=0.8, sharp=40)
    m('wood_oak', '#ffffff', tex='pbr_wood_oak', tile=0.5, rough=0.7, sharp=40)
    m('wood_dark', '#ffffff', tex='pbr_wood_dark', tile=0.6, rough=0.65, sharp=40)
    # --- metals
    m('iron_cast', '#ffffff', tex='pbr_iron', tile=0.4, rough=0.6, metal=0.95, sharp=42)
    m('iron_black', '#b4b4b8', tex='pbr_iron', tile=0.14, rough=0.55, metal=0.95, sharp=42)
    m('iron_paint', '#34343a', rough=0.42, metal=0.55, sharp=42)
    m('steel', [3.0, 3.0, 3.2], tex='pbr_iron', tile=0.14, rough=0.3, metal=1.0, sharp=40)
    m('tin', [2.2, 2.2, 2.35], tex='pbr_iron', tile=0.2, rough=0.5, metal=1.0, sharp=40)
    m('copper', '#ffd9c8', tex='pbr_brass_copper', tile=0.3, rough=0.4, metal=1.0, sharp=45)
    m('brass', '#ffffb0', tex='pbr_brass_copper', tile=0.3, rough=0.4, metal=1.0, sharp=45)
    # --- ceramics / stone
    m('ceramic', '#ffffff', tex='pbr_ceramic', tile=0.2, rough=0.3, sharp=55)
    m('enamel', '#ffffff', tex='pbr_ceramic', tile=0.2, rough=0.35, sharp=55)
    m('stone', '#ffffff', tex='pbr_stone_fireplace', tile=1.0, rough=0.9, sharp=45)
    m('terracotta', '#e2906a', tex='pbr_ceramic', tile=0.2, rough=0.9, sharp=55)
    # --- fabrics / organic
    m('linen_vc', '#ffffff', tex='pbr_fabric_linen', tile=0.25, rough=1.0, sharp=70, double=True)
    m('wool_vc', '#ffffff', tex='pbr_fabric_wool', tile=0.3, rough=1.0, sharp=70, double=True)
    m('burlap_vc', '#ffffff', tex='pbr_fabric_burlap', tile=0.25, rough=1.0, sharp=70)
    m('leather_vc', '#ffffff', tex='pbr_leather', tile=0.3, rough=0.6, sharp=50)
    m('wicker', '#ffffff', tex='pbr_wicker', tile=0.25, rough=0.9, sharp=70)
    m('paper', '#ffffff', tex='pbr_paper', tile=0.2, rough=0.95, sharp=80, double=True)
    # --- plain (vertex coloured)
    m('rope', '#ffffff', rough=1.0, sharp=70)
    m('straw', '#d9b866', rough=1.0, sharp=80)
    m('food_vc', '#ffffff', rough=0.55, sharp=70)
    m('food_matte', '#ffffff', rough=0.85, sharp=70)
    m('herb_vc', '#ffffff', rough=0.9, sharp=85, double=True)
    m('wax', '#f2e7c6', rough=0.45, sharp=70)
    m('soil', '#3b2a1c', rough=1.0, sharp=70)
    m('glass', '#e9f3f0', tex='pbr_glass_dirty', tile=0.5, rough=0.1, alpha=0.18, double=True, sharp=60)
    m('glass_green', '#a8c9a0', rough=0.06, alpha=0.38, double=True, sharp=60)
    m('liquid', '#b8863a', rough=0.05, alpha=0.7, double=True, sharp=90)
    m('water', '#6f9aa8', rough=0.03, alpha=0.65, double=True, sharp=90)
    m('flame', '#ffcf70', emit='#ff9a30', emit_strength=7.0, rough=0.5, sharp=90)
    m('crust', '#ffffff', tex='kt_crust', tile=0.3, rough=0.8, sharp=70)
    m('crumb', '#ffffff', tex='kt_crumb', tile=0.1, rough=0.95, sharp=70)
    m('cheese', '#ffffff', tex='kt_cheese', tile=0.2, rough=0.6, sharp=60)
    m('label', '#ffffff', tex='kt_labels', tile=1.0, rough=0.8, sharp=70)
    m('ink', '#15161c', rough=0.4, sharp=60)
    return M
