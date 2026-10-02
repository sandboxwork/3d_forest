import sys
sys.path.insert(0, '/shared/river/assets/blender')
from box_common import *
reset_scene()
init_box_mats()
import box_a
run_group('flower_box', box_a.DEFS)
