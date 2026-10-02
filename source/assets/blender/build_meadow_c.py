import sys
sys.path.insert(0, '/shared/river/assets/blender')
from meadow_common import *
reset_scene()
init_mats()
import meadow_c
run_group('flowers_meadow', meadow_c.DEFS)
