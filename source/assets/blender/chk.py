import sys; sys.path.insert(0,'/shared/river/assets/blender')
from int_scene import *
from int_decor import decorate
reset_scene(); build_all(); decorate()
objs=finalize()+int_lib.PARTS
bad={}
tot=0
for o in objs:
    bm=bmesh.new(); bm.from_mesh(o.data); bm.normal_update()
    seen=set()
    for v0 in bm.verts:
        if v0 in seen: continue
        isl=[]; st=[v0]; seen.add(v0)
        while st:
            v=st.pop(); isl.append(v)
            for e in v.link_edges:
                w=e.other_vert(v)
                if w not in seen: seen.add(w); st.append(w)
        faces=set(f for v in isl for f in v.link_faces)
        if len(faces)<6: continue
        cen=sum((v.co for v in isl),Vector())/len(isl)
        neg=0; pos=0
        for f in faces:
            d=f.calc_center_median()-cen
            if f.normal.dot(d)<0: neg+=1
            else: pos+=1
        tot+=1
        if neg>pos*1.5:
            key=o.name
            bad.setdefault(key,[]).append((round(cen.x,2),round(cen.y,2),round(cen.z,2),neg,pos))
print('islands',tot)
for k,v in bad.items():
    print(k,len(v),v[:6])
print('--- planar checks (normal toward room centre)')
for o in objs:
    if o.name in ('static_canvas_vc','static_paper','static_curtain_vc','static_mirror','static_paint_vc'):
        bm=bmesh.new(); bm.from_mesh(o.data); bm.normal_update()
        seen=set(); n_bad=0; n_all=0
        for v0 in bm.verts:
            if v0 in seen: continue
            isl=[]; st=[v0]; seen.add(v0)
            while st:
                v=st.pop(); isl.append(v)
                for e in v.link_edges:
                    w=e.other_vert(v)
                    if w not in seen: seen.add(w); st.append(w)
            faces=set(f for v in isl for f in v.link_faces)
            cen=sum((v.co for v in isl),Vector())/len(isl)
            nm=sum((f.normal for f in faces),Vector())
            to=Vector((0.0 if cen.x<1.5 or True else 0,0,1.7))-cen
            to=Vector((-cen.x*0.3 + (0 if abs(cen.x)<4 else 0), -cen.y*0.3, 0))
            if nm.length<0.5*len(faces)*0.0+1e-6: continue
            n_all+=1
            if nm.dot(Vector((-cen.x, -cen.y, 0)))<0 and o.name!='static_curtain_vc': n_bad+=1; print(o.name,[round(c,2) for c in cen],[round(c,2) for c in nm.normalized()])
        print(o.name,n_all,'bad',n_bad)
