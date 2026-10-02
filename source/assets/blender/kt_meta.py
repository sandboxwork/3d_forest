"""meta: extra colliders, interactables, lights"""
from kt_lib import *


def build():
    # colliders (tight AABBs, bottom = floor top 0.30)
    collider(1.08 - 0.2, 1.08 + 0.2, 3.0 - 0.2, 3.0 + 0.2, F + 0.66)         # flour sack
    collider(1.12 - 0.19, 1.12 + 0.19, 2.68 - 0.19, 2.68 + 0.19, F + 0.56)     # potato sack
    collider(0.45 - 0.22, 0.45 + 0.22, 2.42 - 0.22, 2.42 + 0.22, F + 0.24)     # potato basket
    collider(-0.85 - 0.16, -0.85 + 0.16, 2.2 - 0.16, 2.2 + 0.16, F + 0.15)     # small basket
    I = interact
    I('stove_kettle', (-3.62, 2.845, F + 1.05), '김이 나는 구리 주전자')
    I('flour_sack', (1.08, 3.0, F + 0.6), '밀가루 포대')
    I('potato_sack', (1.12, 2.68, F + 0.5), '감자 자루')
    I('hanging_herbs', (-0.55, 2.4, 2.65), '천장에 매달린 말린 허브')
    I('onion_braid', (0.55, 2.0, 2.6), '양파 엮음')
    I('garlic_braid', (-1.65, 2.7, 2.65), '마늘 엮음')
    I('pot_rack', (-2.2, 2.86, 2.35), '구리 냄비 걸이')
    I('table_bread', (-2.72, -2.9, F + 0.9), '식탁 위 갓 구운 빵')
    I('table_candle', (-3.3, -2.56, F + 1.0), '식탁 위 촛불')
    I('table_lantern', (-3.0, -2.6, 2.45), '식탁 위 매달린 램프')
    I('tea_tray', (-0.6, 2.95, F + 1.0), '찻잔이 놓인 쟁반')
    I('herb_pots', (-2.55, 3.2, 1.55), '창가의 허브 화분')
    I('broom', (1.32, 2.4, 1.1), '벽에 걸린 빗자루')
    I('apron', (1.33, 1.95, 1.5), '벽에 걸린 앞치마')
    I('tea_towel', (-3.24, 3.0, 1.35), '난로 앞 행주')
    I('water_bucket', (-0.85, 2.4, F + 0.3), '물 양동이')
    I('mortar', (-2.66, 3.09, F + 1.0), '절구와 공이')
    I('pickle_jars', (-1.75, 3.14, F + 1.05), '잼과 절임 병')
    I('egg_bowl', (-1.78, 2.86, F + 0.98), '달걀 그릇')
    I('wood_stack', (-3.55, 2.2, F + 0.3), '난로 옆 장작')
    I('wall_shelves', (-1.42, 3.1, 2.1), '접시와 찻잔이 놓인 선반')
    I('dining_chairs', (-3.0, -1.85, F + 0.8), '짚으로 엮은 식탁 의자')
    # warm glow from the stove fire box (static point light, no animated part)
    light('stove_glow', (-3.5, 2.55, F + 0.55), (1.0, 0.45, 0.15), 0.35, 2.2)
