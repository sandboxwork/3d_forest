"""Build /shared/river/assets/out/house_interior.json + .meta.json
Run: ~/.cache/motion-video-deps/blender/bin/blender -b --python house_interior.py
(modules: int_lib, int_mats, int_items, int_furn1/2/3, int_scene, int_decor; textures: gen_tex_interior.py)"""
import sys
sys.path.insert(0, '/shared/river/assets/blender')
from int_scene import *
from int_decor import decorate
reset_scene()
build_all()
decorate()
print(export_all()[1])
