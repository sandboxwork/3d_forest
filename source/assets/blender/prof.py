import sys; sys.path.insert(0,'/shared/river/assets/blender')
from int_scene import *
from int_decor import *
import int_scene, int_decor, int_lib
reset_scene()
import functools
stats={}
def count():
    return sum(len(v[0].verts) for v in int_lib.ACC.values())
def wrap(mod,name):
    fn=getattr(mod,name)
    @functools.wraps(fn)
    def w(*a,**k):
        c0=count(); r=fn(*a,**k); stats[name]=stats.get(name,0)+count()-c0; return r
    setattr(mod,name,w)
names=['sofa','armchair','bed','bedside','wardrobe','dresser','desk','trunk','rocking_chair','dining_chair','dining_table','coffee_table','side_table','bookshelf','fireplace_set','log_basket','clock_longcase','cookstove','kitchen_counter','hutch','pantry','wall_shelf','pot_rack','coat','umbrella_stand','wood_stack','braided_rug','rect_rug','sheepskin','curtain','picture','antlers','rod_rack','crane_kettle','tea_set','runner','barrel','bucket','basket','crate','herb_bundle','braid','heap_apples','vase_flowers','candle_holder','oil_lamp','lantern','mug','plate','jar','boot','slippers','book','book_flat','book_open','teapot','kettle','pot','pan','hanging_hook_row','mirror_oval','flame','photo_frame','frame_picture','sack','loaf','utensil_crock','paper_stack','towel_fold','cutting_board','bowl','apple','onion','garlic','carrot','reading_glasses']
for n in names:
    for m in (int_scene,int_decor):
        if hasattr(m,n): wrap(m,n)
# also wrap in furn modules namespaces used inside
import int_furn1,int_furn2,int_furn3,int_items
for n in names:
    for m in (int_furn1,int_furn2,int_furn3,int_items):
        if hasattr(m,n) and getattr(getattr(m,n),'__wrapped__',None) is None: wrap(m,n)
build_all(); decorate()
for k,v in sorted(stats.items(), key=lambda x:-x[1])[:40]: print(k,v)
print(count())
