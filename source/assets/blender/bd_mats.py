"""Materials for the bedroom/entry/decor build. Textured materials use the shared PBR library (pbr_*), tile size in metres.
Base colour of textured materials is white: the runtime multiplies texture x base colour x vertex colour (Col)."""
from bd_lib import *

# fallback preview colours when a pbr texture does not exist yet (preview only)
PREV = {}


def init_mats():
    def m(name, tex=None, tile=None, color='#ffffff', prev=None, **kw):
        MAT(name, color, tex=tex, tile=tile, **kw)
        PREV[name] = prev or color
    m('wood_pine', 'pbr_wood_pine', 0.6, rough=0.62, prev='#d9a96a')
    m('wood_oak', 'pbr_wood_oak', 0.5, rough=0.55, prev='#b98552')
    m('wood_dark', 'pbr_wood_dark', 0.6, rough=0.5, prev='#5a3520')
    m('linen', 'pbr_fabric_linen', 0.25, rough=0.92, double=True, prev='#e6dcc6')
    m('linen_curtain', 'pbr_fabric_linen', 0.25, rough=0.95, double=True, prev='#e0d6bd')
    m('burlap', 'pbr_fabric_burlap', 0.25, rough=1.0, prev='#b99d6b', double=True)
    m('wool', 'pbr_fabric_wool', 0.3, rough=1.0, double=True, prev='#cfc2a4')
    m('leather', 'pbr_leather', 0.3, rough=0.5, double=True, prev='#6a4328')
    m('rug', 'pbr_rug_braided', 0.4, rough=1.0, prev='#a88a5a')
    m('iron', 'pbr_iron', 0.4, rough=0.55, metal=0.65, double=True, prev='#3a3a3d')
    m('brass', 'pbr_brass_copper', 0.3, rough=0.32, metal=0.85, double=True, prev='#d6ab52')
    m('copper', 'pbr_brass_copper', 0.3, color='#ffb48a', rough=0.35, metal=0.85, double=True, prev='#b8602c')
    m('ceramic', 'pbr_ceramic', 0.2, rough=0.22, double=True, prev='#efeae0')
    m('paper', 'pbr_paper', 0.2, rough=0.9, double=True, prev='#efe4c8')
    m('book_cloth', 'pbr_book_cloth', 0.15, rough=0.8, prev='#7a4a3a')
    m('wicker', 'pbr_wicker', 0.3, rough=0.85, double=True, prev='#d8a765')
    m('stone', 'pbr_stone_fireplace', 1.0, rough=0.9, prev='#8a857b')
    m('plaster', 'pbr_plaster', 1.0, rough=0.92, prev='#e6dcc8')
    m('quilt', 'bd_quilt', 1.0, rough=0.95, double=True, prev='#c9a27a')
    # plain / vertex-coloured materials
    m('paint', None, None, rough=0.68, prev='#e4dccb')
    m('wax', None, None, rough=0.45, prev='#f0e6c8')
    m('glass', None, None, rough=0.04, alpha=0.18, double=True, prev='#e6f2f0')
    m('glass_amber', None, None, color='#e0a850', rough=0.06, alpha=0.5, double=True, prev='#e0a850')
    m('mirror', None, None, color='#cfd8da', rough=0.03, metal=0.9, prev='#cfd8da')
    m('flame', None, None, color='#ffcf70', emit='#ff9a30', emit_strength=8.0, rough=0.5, prev='#ffcf70')
    m('bulbglow', None, None, color='#ffe9b0', emit='#ffc860', emit_strength=3.0, rough=0.5, prev='#ffe9b0')
    m('water', None, None, color='#8fb0b8', rough=0.03, alpha=0.6, prev='#8fb0b8')
    m('ink', None, None, color='#15161c', rough=0.3, prev='#15161c')
    m('soil', None, None, color='#3a2a1e', rough=1.0, prev='#3a2a1e')
    m('leaf', None, None, rough=0.55, double=True, prev='#ffffff')
    m('petal', None, None, rough=0.7, double=True, prev='#ffffff')
    m('straw', None, None, color='#d9b866', rough=1.0, prev='#d9b866')
    m('felt', None, None, rough=1.0, prev='#ffffff')
    m('shadeglow', None, None, color='#f3e2bd', emit='#ffc27a', emit_strength=1.2, rough=0.9, double=True, prev='#f3e2bd')
    for i in range(1, 10):
        m('bd_painting_%d' % i, 'bd_painting_%d' % i, 1.0, rough=0.78, prev='#9a8a6a')
