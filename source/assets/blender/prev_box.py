import sys
sys.path.insert(0, '/shared/river/assets/blender')
from box_common import *
reset_scene(); init_box_mats()
import box_a
which = sys.argv[sys.argv.index('--')+1]
fn = getattr(box_a, which.rsplit('_',1)[0]); v = which.rsplit('_',1)[1]
rng = np.random.RandomState(5)
ob = fn(v, rng).to_obj(which)
pv = Preview()
sc = pv.sc
import math
tg = Vector((0,0,0.12 if 'bed' not in which else 0.2))
cl = Vector((0.55,-1.0,0.6)) if 'box' in which else (Vector((0.9,-1.4,0.9)) if 'bed' in which else Vector((0.25,-0.45,0.4)))
pv.cam.location = cl
pv.cam.rotation_euler = (tg-cl).to_track_quat('-Z','Y').to_euler()
sc.render.resolution_x, sc.render.resolution_y = 900, 600
sc.render.filepath = f'{PREVIEW_DIR}/box_custom_{which}.png'
bpy.ops.render.render(write_still=True)
