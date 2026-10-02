/* =====================================================================
   06b_assetlib.js — Blender 번들(JSON) 디코더: 부품 계층(피벗), 재질, 지오메트리 캐시
   window.ASSET_BUNDLES / window.ASSET_TEX 는 build_assets.py 가 인라인으로 주입한다.
   ===================================================================== */
const AssetLib = {
  _geo: new Map(), _mat: new Map(), _tex: new Map(), _builtin: new Map(),
  async unpack() {
    const P = window.ASSET_PACK || {};
    for (const n of Object.keys(P)) {
      const bin = atob(P[n]), u8 = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
      const ds = new DecompressionStream('gzip'), w = ds.writable.getWriter(); w.write(u8); w.close();
      const txt = await new Response(ds.readable).text(); window.ASSET_BUNDLES[n] = JSON.parse(txt); delete P[n];
      await new Promise((r) => setTimeout(r, 0));
    }
  },
  has(name) { return !!(window.ASSET_BUNDLES && window.ASSET_BUNDLES[name]); },
  bundle(name) { return window.ASSET_BUNDLES && window.ASSET_BUNDLES[name]; },
  _dec(s, T) { const bin = atob(s), u8 = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i); return new T(u8.buffer); },
  geometry(bname, sub, key) {
    let g = this._geo.get(key); if (g) return g;
    g = new THREE.BufferGeometry();
    const pq = this._dec(sub.pos, Int16Array), pc = sub.pq, pf = new Float32Array(pq.length);
    for (let i = 0; i < pq.length; i += 3) { pf[i] = pq[i] / 32767 * pc[3] + pc[0]; pf[i + 1] = pq[i + 1] / 32767 * pc[4] + pc[1]; pf[i + 2] = pq[i + 2] / 32767 * pc[5] + pc[2]; }
    g.setAttribute('position', new THREE.BufferAttribute(pf, 3));
    g.setAttribute('normal', new THREE.BufferAttribute(this._dec(sub.nrm, Int8Array), 3, true));
    if (sub.uq) { const uq = this._dec(sub.uv, Uint16Array), uf = new Float32Array(uq.length), q = sub.uq; for (let i = 0; i < uq.length; i += 2) { uf[i] = uq[i] / 65535 * q[2] + q[0]; uf[i + 1] = uq[i + 1] / 65535 * q[3] + q[1]; } g.setAttribute('uv', new THREE.BufferAttribute(uf, 2)); }
    else g.setAttribute('uv', new THREE.BufferAttribute(this._dec(sub.uv, Float32Array), 2));
    if (sub.col) { const cq = this._dec(sub.col, Uint8Array), cf = new Float32Array(cq.length); for (let i = 0; i < cq.length; i++) cf[i] = cq[i] / 255 * sub.cs; g.setAttribute('color', new THREE.BufferAttribute(cf, 3)); }
    g.setIndex(new THREE.BufferAttribute(this._dec(sub.idx, sub.idx16 ? Uint16Array : Uint32Array), 1));
    g.computeBoundingSphere(); g.computeBoundingBox();
    this._geo.set(key, g); return g;
  },
  texture(name) {
    if (!name) return null;
    if (this._tex.has(name)) return this._tex.get(name);
    let t = null;
    const bi = { planks: () => TexLib.planks(false), planksV: () => TexLib.planks(true), stone: () => TexLib.stone(), shingles: () => TexLib.shingles(), bark: () => TexLib.bark('oak') };
    if (bi[name]) { if (!this._builtin.has(name)) this._builtin.set(name, bi[name]()); t = { set: this._builtin.get(name) }; }
    else if (window.ASSET_TEX && window.ASSET_TEX[name]) {
      const load = (key, srgb) => {
        const src = window.ASSET_TEX[key]; if (!src) return null;
        const img = new Image(), tex = new THREE.Texture(img); img.onload = () => { tex.needsUpdate = true; }; img.src = src;
        tex.wrapS = tex.wrapT = THREE.RepeatWrapping; tex.anisotropy = MAX_ANISO.v; tex.flipY = true; if (srgb) tex.encoding = THREE.sRGBEncoding; return tex;
      };
      t = { set: { map: load(name, true), normalMap: load(name + '_n', false), roughnessMap: load(name + '_r', false) } };
    }
    this._tex.set(name, t); return t;
  },
  material(bname, mname, sub) {
    const key = bname + '/' + mname + (sub && sub.col ? '/vc' : '');
    let m = this._mat.get(key); if (m) return m;
    const d = (this.bundle(bname).mats[mname]) || { color: [0.7, 0.7, 0.7], rough: 0.7, metal: 0, alpha: 1, tex: '' };
    const p = { color: new THREE.Color(d.color[0], d.color[1], d.color[2]), roughness: d.rough, metalness: d.metal, vertexColors: !!(sub && sub.col) };
    if (d.double) p.side = THREE.DoubleSide;
    if (d.alpha < 0.999) { p.transparent = true; p.opacity = d.alpha; p.depthWrite = false; }
    if (d.emit) { p.emissive = new THREE.Color(d.emit[0], d.emit[1], d.emit[2]); p.emissiveIntensity = d.emitStrength; }
    const t = this.texture(d.tex);
    if (t && t.set) { p.map = t.set.map; p.normalMap = t.set.normalMap; p.roughnessMap = t.set.roughnessMap; p.roughness = t.set.roughnessMap ? 1 : d.rough; }
    m = new THREE.MeshStandardMaterial(p); m.name = mname;
    if (m.normalMap) { const ns = /fabric|knit|weave|wool|burlap|linen|rug|wicker/.test(d.tex) ? 0.45 : 1.1; m.normalScale.set(ns, ns); }
    patchMaterial(m, function () { });
    this._mat.set(key, m); return m;
  },
  /* 부품 계층을 THREE.Group 트리로 만든다. 각 부품 Group 은 피벗 위치에 놓이고 지오메트리는 피벗 기준 로컬.
     opts: { only:[부품명], exclude:/정규식/, shadow:true, shared:true(지오메트리 공유) } */
  build(bname, opts) {
    opts = opts || {};
    const B = this.bundle(bname); if (!B) throw new Error('에셋 번들 없음: ' + bname);
    const root = new THREE.Group(), parts = {}, meshes = [];
    const list = B.parts.filter((p) => (!opts.only || opts.only.includes(p.name)) && (!opts.exclude || !opts.exclude.test(p.name)));
    for (const p of list) {
      const g = new THREE.Group(); g.name = p.name; g.userData.pivot = p.pivot;
      p.subs.forEach((s, i) => {
        const geo = this.geometry(bname, s, bname + '/' + p.name + '/' + i);
        const mesh = new THREE.Mesh(geo, this.material(bname, s.mat, s));
        mesh.castShadow = opts.shadow !== false && !(s.mat && /glass|flame|ember/i.test(s.mat));
        mesh.receiveShadow = true; g.add(mesh); meshes.push(mesh);
      });
      parts[p.name] = g; g.userData.spec = p;
    }
    for (const p of list) {
      const g = parts[p.name], par = p.parent && parts[p.parent];
      if (par) { const pp = par.userData.pivot; g.position.set(p.pivot[0] - pp[0], p.pivot[1] - pp[1], p.pivot[2] - pp[2]); par.add(g); }
      else { g.position.set(p.pivot[0], p.pivot[1], p.pivot[2]); root.add(g); }
      g.userData.rest = { x: g.position.x, y: g.position.y, z: g.position.z };
    }
    return { root, parts, meshes, meta: B.meta || {} };
  },
  /* 단일 부품(하위 메쉬들)을 InstancedMesh 용으로 돌려준다: [{geometry, material}] */
  subsOf(bname, partName) {
    const B = this.bundle(bname), p = B.parts.find((q) => q.name === partName); if (!p) return [];
    return p.subs.map((s, i) => ({ geometry: this.geometry(bname, s, bname + '/' + p.name + '/' + i), material: this.material(bname, s.mat, s) }));
  }
};
