import sys, importlib
sys.path.insert(0, '/shared/river/assets/blender')
from meadow_common import *
reset_scene()
init_mats()
DEFS = []
for modname in ['meadow_a', 'meadow_b', 'meadow_c']:
    try:
        m = importlib.import_module(modname)
        DEFS += m.DEFS
    except Exception as e:
        print('SKIP', modname, e)
run_group('flowers_meadow', DEFS)
