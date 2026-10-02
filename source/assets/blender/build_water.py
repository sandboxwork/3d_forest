import sys
sys.path.insert(0, '/shared/river/assets/blender')
from water_common import *
reset_scene()
init_water_mats()
import water_a, water_b
water_a.init_extra_mats()
mat('sepal_green', '#6c9a3a', rough=0.55)
DEFS = water_a.DEFS + water_b.DEFS
run_group('plants_water_edge', DEFS)
