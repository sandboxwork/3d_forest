/* =====================================================================
   10d_village.js — 마을: 건물/소품 배치, 주민(일과·대화), 가축, 굴뚝 연기, 창문 불빛
   모델은 Blender 번들(village_houses, village_props, villager_*, animal_*)에서 온다.
   ===================================================================== */
const Village = (function () {
  const V = { ready: false, enabled: true, buildings: [], people: [], props: [], livestock: [], doors: [], night: 0, t: 0 };
  const R = mulberry32(777001), rr = (a, b) => a + (b - a) * R(), D = Math.PI / 180, TAU2 = Math.PI * 2;
  const rot0 = () => -VILLAGE.rot;
  const faceAng = (f) => rot0() + (f === 'N' ? Math.PI : 0);
  const W2 = (lx, lz) => villageToWorld(lx, lz);
  const planeY = (lx, lz) => villagePlaneH(lx, lz);
  const metaOf = (bundle, part) => { const m = (AssetLib.bundle(bundle) || {}).meta || {}; return (m.parts && m.parts[part]) || m[part] || {}; };
  let scene, group, smokeMesh, promptEl, bubble, bubbleT = 0, talking = null, glowMats = [], flameMats = [], hammerT = 0;

  /* ---------- 페인트 변형 (trim / shutter / door) ---------- */
  const PAL = [
    { trim: [0.92, 0.9, 0.84], shutter: [0.16, 0.36, 0.28], door: [0.5, 0.14, 0.12] },
    { trim: [0.88, 0.86, 0.8], shutter: [0.2, 0.3, 0.5], door: [0.2, 0.34, 0.5] },
    { trim: [0.94, 0.9, 0.8], shutter: [0.5, 0.16, 0.14], door: [0.14, 0.34, 0.3] },
    { trim: [0.82, 0.8, 0.75], shutter: [0.28, 0.2, 0.14], door: [0.3, 0.22, 0.14] },
    { trim: [0.95, 0.93, 0.88], shutter: [0.62, 0.5, 0.2], door: [0.16, 0.3, 0.2] },
    { trim: [0.9, 0.88, 0.82], shutter: [0.3, 0.42, 0.34], door: [0.55, 0.34, 0.12] }
  ];
  const variantCache = new Map();
  function paintVariant(mat, kind, pal) {
    const key = mat.uuid + ':' + pal; let m = variantCache.get(key); if (m) return m;
    m = mat.clone(); const c = PAL[pal % PAL.length][kind]; const mx = Math.max(c[0], c[1], c[2], 0.01);
    m.color.setRGB(Math.pow(c[0], 2.2), Math.pow(c[1], 2.2), Math.pow(c[2], 2.2)); variantCache.set(key, m); return m;
  }
  function recolorBuilding(root, pal) {
    root.traverse((o) => {
      if (!o.isMesh || !o.material) return; const n = o.material.name;
      if (n === 'paint_trim') o.material = paintVariant(o.material, 'trim', pal);
      else if (n === 'paint_shutter') o.material = paintVariant(o.material, 'shutter', pal);
      else if (n === 'paint_door') o.material = paintVariant(o.material, 'door', pal);
    });
  }

  function addBoxesFromMeta(boxes, px, py, pz, th) {
    const c = Math.cos(th), s = Math.sin(th);
    for (const b of boxes || []) {
      const wx = px + b.cx * c + b.cz * s, wz = pz - b.cx * s + b.cz * c;
      Colliders.addBox(wx, wz, b.hx, b.hz, th, py + (b.top === undefined ? 3 : b.top), py + (b.bottom === undefined ? -1 : b.bottom));
    }
  }

  /* ---------- 건물 ---------- */
  function buildHouses() {
    if (!AssetLib.has('village_houses')) return;
    const sh = [];
    for (const slot of VILLAGE_LAYOUT.buildings) {
      const meta = metaOf('village_houses', slot.part);
      let b; try { b = AssetLib.build('village_houses', { only: [slot.part, slot.part + '_smoke'] }); } catch (e) { continue; }
      if (!b.parts[slot.part]) continue;
      const w = W2(slot.lx, slot.lz), y = planeY(slot.lx, slot.lz), th = faceAng(slot.face);
      b.root.position.set(w[0], y, w[1]); b.root.rotation.y = th; recolorBuilding(b.root, slot.pal); group.add(b.root);
      const sm = b.parts[slot.part + '_smoke']; if (sm) sm.visible = false;
      b.meshes.forEach((m) => { if (/glass/i.test(m.material.name)) { m.castShadow = false; m.renderOrder = 4; } if (m.material.name === 'window_glow') { if (!glowMats.includes(m.material)) { glowMats.push(m.material); m.material.emissive = new THREE.Color(1.0, 0.62, 0.26); m.material.emissiveIntensity = 0; } } if (/forge_glow|flame|ember/i.test(m.material.name) && !flameMats.includes(m.material)) flameMats.push(m.material); });
      addBoxesFromMeta(meta.colliders && meta.colliders.length ? meta.colliders : [{ cx: 0, cz: 0, hx: (meta.w || 8) / 2, hz: (meta.d || 7) / 2, top: meta.h_eave || 3.4, bottom: -1 }], w[0], y, w[1], th);
      const door = meta.door || { x: 0, z: (meta.d || 7) / 2 };
      const c = Math.cos(th), s = Math.sin(th), front = (dz) => [w[0] + door.x * c + (door.z + dz) * s, w[1] - door.x * s + (door.z + dz) * c];
      const rec = { part: slot.part, root: b.root, pos: [w[0], y, w[1]], th, meta, role: meta.role || 'home', ko: meta.ko || slot.part, door: front(0), step: front(2.2), lane: front(6.5), lx: slot.lx, lz: slot.lz, smoke: null, windows: meta.windows || [], inhabitants: [] };
      if (sm && meta.smoke !== null) { const p = sm.userData.pivot || [0, 4, 0]; rec.smoke = [w[0] + p[0] * c + p[2] * s, y + p[1], w[1] - p[0] * s + p[2] * c]; }
      else if (meta.chimney) { const p = meta.chimney; rec.smoke = [w[0] + p.x * c + p.z * s, y + p.y, w[1] - p.x * s + p.z * c]; }
      V.buildings.push(rec);
    }
  }

  /* ---------- 굴뚝 연기 (한 번에 그리는 Points) ---------- */
  function buildSmoke() {
    const src = V.buildings.filter((b) => b.smoke); if (!src.length) return;
    const per = 14, N = src.length * per, pos = new Float32Array(N * 3), idx = new Float32Array(N), base = new Float32Array(N * 3);
    src.forEach((b, i) => { for (let k = 0; k < per; k++) { const n = i * per + k; idx[n] = k / per + (i * 0.173 % 1); base.set(b.smoke, n * 3); } });
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('aI', new THREE.BufferAttribute(idx, 1)); g.setAttribute('aBase', new THREE.BufferAttribute(base, 3));
    const m = new THREE.ShaderMaterial({
      uniforms: { uTime: SH.uTime, uWind: SH.uWind, uPix: { value: 1 }, uSunCol: SH.uSunCol, uHorizon: SH.uHorizon },
      vertexShader: `uniform float uTime; uniform vec2 uWind; uniform float uPix; attribute float aI; attribute vec3 aBase; varying float vA; varying float vT;
        void main(){ float t = fract(uTime * 0.08 + aI); vec3 w = aBase + vec3(uWind.x * t * t * 8.0 + sin(aI * 40.0 + uTime * 0.5) * t * 0.7, t * 5.5, uWind.y * t * t * 8.0 + cos(aI * 31.0 + uTime * 0.4) * t * 0.7);
          vec4 mv = viewMatrix * vec4(w, 1.0); gl_Position = projectionMatrix * mv; gl_PointSize = (0.8 + 3.0 * t) * uPix / max(-mv.z, 1.0); vA = (1.0 - t) * smoothstep(0.0, 0.08, t) * 0.24; vT = t; }`,
      fragmentShader: `uniform vec3 uSunCol; uniform vec3 uHorizon; varying float vA; varying float vT;
        void main(){ vec2 p = gl_PointCoord - 0.5; float r = length(p) * 2.0; float a = smoothstep(1.0, 0.1, r); vec3 c = mix(vec3(0.42, 0.40, 0.38), uHorizon, vT * 0.5) * (0.6 + 0.6 * uSunCol); gl_FragColor = vec4(c, a * vA); }`,
      transparent: true, depthWrite: false
    });
    smokeMesh = new THREE.Points(g, m); smokeMesh.frustumCulled = false; smokeMesh.renderOrder = 9; scene.add(smokeMesh);
  }

  /* ---------- 소품 (반복되는 것은 인스턴싱) ---------- */
  const instQueue = new Map();       // name -> [Matrix4]
  const _m = new THREE.Matrix4(), _q = new THREE.Quaternion(), _e = new THREE.Euler(), _p = new THREE.Vector3(), _s = new THREE.Vector3(1, 1, 1);
  function placeProp(name, lx, lz, faceOrRot, opts) {
    opts = opts || {}; const w = W2(lx, lz), y = (opts.y !== undefined ? opts.y : planeY(lx, lz)), th = typeof faceOrRot === 'number' ? faceOrRot : faceAng(faceOrRot || 'S');
    _e.set(opts.tilt || 0, th + (opts.dr || 0), opts.roll || 0); _q.setFromEuler(_e); _p.set(w[0], y, w[1]); _s.setScalar(opts.scale || 1); _m.compose(_p, _q, _s);
    if (!instQueue.has(name)) instQueue.set(name, []); instQueue.get(name).push(_m.clone());
    const meta = metaOf('village_props', name);
    if (opts.collide !== false && meta.colliders) addBoxesFromMeta(meta.colliders.map((b) => b), w[0], y, w[1], th + (opts.dr || 0));
    V.props.push({ name, x: w[0], z: w[1], y, th, lx, lz });
    return { x: w[0], z: w[1], y, th };
  }
  function flushProps() {
    for (const [name, mats] of instQueue) {
      const subs = AssetLib.subsOf('village_props', name); if (!subs.length) continue;
      const B = AssetLib.bundle('village_props'), part = B.parts.find((p) => p.name === name);
      subs.forEach((s, i) => {
        const im = new THREE.InstancedMesh(s.geometry, s.material, mats.length); mats.forEach((m, k) => im.setMatrixAt(k, m)); im.instanceMatrix.needsUpdate = true;
        im.castShadow = !/glass|flame/i.test(part.subs[i].mat); im.receiveShadow = true; im.frustumCulled = false; group.add(im);
        if (/flame/i.test(s.material.name) && !flameMats.includes(s.material)) flameMats.push(s.material);
      });
    }
    instQueue.clear();
  }
  function layoutProps() {
    if (!AssetLib.has('village_props')) return;
    const has = (n) => !!AssetLib.bundle('village_props').parts.find((p) => p.name === n);
    const P = (n, lx, lz, f, o) => { if (has(n)) return placeProp(n, lx, lz, f, o); };
    // 광장: 우물(애니메이션 가능한 부품이 있어 개별 그룹), 노점, 수레, 벤치
    if (has('well_stone')) { const b = AssetLib.build('village_props', { only: ['well_stone', 'well_bucket'] }), w = W2(0, 0); b.root.position.set(w[0], planeY(0, 0), w[1]); b.root.rotation.y = rot0(); group.add(b.root); V.well = b; const mm = metaOf('village_props', 'well_stone'); if (mm.colliders) addBoxesFromMeta(mm.colliders, w[0], planeY(0, 0), w[1], rot0()); else Colliders.addCircle(w[0], w[1], 1.7); }
    P('market_stall_a', -8.5, -7.6, 'S'); P('market_stall_b', 8.5, -7.6, 'S'); P('market_stall_c', -7.5, 7.6, 'N'); P('hay_cart', 8.6, 7.8, rot0() + 0.25);
    P('bench_a', -4.8, -5.6, 'S'); P('bench_a', 4.8, -5.6, 'S'); P('bench_a', -4.5, 5.6, 'N'); P('bench_a', 4.5, 5.6, 'N');
    P('barrel_stack', 11.2, -6.8, 'S'); P('crate_stack', -11.5, 6.8, 'N'); P('barrel_a', 10.2, -7.2, 'S'); P('barrel_a', -10.8, 7.1, 'N');
    // 가로등
    for (let x = -50; x <= 56; x += 12) P('street_lamp', x, (x / 12 | 0) % 2 ? -4.6 : 4.6, 'S', { collide: true });
    // 표지판 (큰길 양끝)
    P('signpost', 58, 4.4, 'S'); P('signpost', -54, -4.4, 'N');
    // 집 앞마당: 울타리, 텃밭, 장작, 빨랫줄, 통, 벤치
    for (const b of V.buildings) {
      const north = b.lz < 0, side = north ? 1 : -1, lane = north ? -7.6 : 7.6;       // 큰길 쪽 앞마당 경계
      const hw = ((b.meta.w || 8) / 2) + 0.6;
      if (b.role === 'home' || b.role === 'work') {
        const nseg = Math.max(2, Math.round(hw * 2 / 2));
        for (let i = 0; i < nseg; i++) { const ox = -hw + (i + 0.5) * (hw * 2 / nseg); if (Math.abs(ox) < 1.6) continue; P('wooden_fence_a', b.lx + ox, lane, 'S', { scale: 1.0 }); }
      }
      if (b.part === 'house_farm') { P('chicken_coop', b.lx + 9.2, b.lz + side * 6.5, north ? 'S' : 'N'); P('garden_plot_a', b.lx - 6, b.lz - side * 8.5, 'S'); P('beehive_stand', b.lx + 12, b.lz - side * 9, 'S'); P('apple_tree_small', b.lx - 11, b.lz - side * 8, 'S', { collide: false }); }
      if (b.part === 'house_cottage_a') { P('garden_plot_a', b.lx + 5, b.lz - side * 8.5, 'S'); P('laundry_line', b.lx - 6.5, b.lz - side * 3, 'S'); P('woodpile_stack', b.lx + 3.6, b.lz - side * 3.6, 'S'); }
      if (b.part === 'house_cottage_b') { P('garden_plot_a', b.lx - 5.5, b.lz - side * 8.5, 'S'); P('dog_house', b.lx + 5.2, b.lz + side * 6.8, 'S'); P('apple_tree_small', b.lx + 6, b.lz - side * 9.5, 'S', { collide: false }); }
      if (b.part === 'house_row') { P('garden_plot_a', b.lx - 4, b.lz - side * 9, 'S'); P('garden_plot_a', b.lx + 4, b.lz - side * 9, 'S'); P('woodpile_stack', b.lx + 8.5, b.lz - side * 3.6, 'S'); }
      if (b.part === 'inn') { P('barrel_stack', b.lx + 7.2, b.lz + side * 5, 'S'); P('bench_a', b.lx + 3.4, b.lz + side * 5.6, 'S'); P('bench_a', b.lx - 3.4, b.lz + side * 5.6, 'S'); P('barrel_a', b.lx - 7, b.lz + side * 5, 'S'); P('water_trough', b.lx + 9.5, b.lz + side * 4, 'S'); }
      if (b.part === 'bakery') { P('crate_stack', b.lx + 5.0, b.lz + side * 5, 'S'); P('bench_a', b.lx - 4.6, b.lz + side * 5.4, 'S'); }
      if (b.part === 'smithy') { P('anvil_block', b.lx + 6.5, b.lz + side * 4.2, 'S'); P('barrel_a', b.lx - 6, b.lz + side * 4.6, 'S'); P('woodpile_stack', b.lx + 7.4, b.lz - side * 3, 'S'); P('water_trough', b.lx - 8.2, b.lz + side * 4.4, 'S'); }
      if (b.part === 'storehouse') { P('crate_stack', b.lx + 4.6, b.lz + side * 4.4, 'S'); P('hay_bale', b.lx - 4.4, b.lz + side * 4.6, 'S'); }
      if (b.part === 'church') { P('bench_a', b.lx - 3.2, b.lz + side * 7.6, 'S'); P('bench_a', b.lx + 3.2, b.lz + side * 7.6, 'S'); }
      if (b.part === 'barn') { for (const [dx, dz] of [[-9, 2], [-10.5, 4.5], [9.5, 3]]) P('hay_stack', b.lx + dx, b.lz + dz, 'S'); P('hay_bale', b.lx + 6.5, b.lz + 8, 'S'); P('hay_bale', b.lx + 7.6, b.lz + 8.6, 'S'); P('water_trough', b.lx + 12, b.lz + 9, 'S'); P('scarecrow', b.lx - 2, b.lz + 22, 'S'); P('garden_plot_a', b.lx + 4, b.lz + 17, 'S'); P('garden_plot_a', b.lx - 6, b.lz + 17, 'S'); P('garden_plot_a', b.lx - 6, b.lz + 21, 'S'); P('garden_plot_a', b.lx + 4, b.lz + 21, 'S'); }
    }
    // 마을 가장자리 과수원
    for (let i = 0; i < 9; i++) { const lx = -48 + (i % 3) * 7 + rr(-1.5, 1.5), lz = 34 + ((i / 3) | 0) * 7 + rr(-1.5, 1.5); P('apple_tree_small', lx, lz, rr(0, TAU2), { collide: false, scale: rr(0.9, 1.15) }); }
    // 호숫가 보트
    if (has('rowboat')) { const q = lakePt(-0.97, 0.15), bx = q[0], bz = q[1], y = Math.max(terrainH(bx, bz), WATER_Y - 0.1) - 0.02; const b = AssetLib.build('village_props', { only: ['rowboat'] }); b.root.position.set(bx, WATER_Y - 0.12 + 0.02, bz); b.root.rotation.y = -1.2; group.add(b.root); V.boat = b.root; }
    flushProps();
  }

  /* ---------- 주민 ---------- */
  const ARCH = { man: 'villager_man', woman: 'villager_woman', elder_m: 'villager_elder_m', elder_f: 'villager_elder_f', boy: 'villager_boy', girl: 'villager_girl', smith: 'villager_smith', baker: 'villager_baker', farmer: 'villager_farmer' };
  const SKINS = [[1.0, 0.86, 0.74], [0.95, 0.78, 0.64], [0.86, 0.66, 0.52], [0.72, 0.52, 0.4], [1.0, 0.9, 0.82]];
  const HAIR = [[0.1, 0.07, 0.05], [0.32, 0.2, 0.1], [0.55, 0.38, 0.18], [0.78, 0.62, 0.36], [0.68, 0.68, 0.66], [0.18, 0.12, 0.08]];
  const CLOTH = [[0.62, 0.28, 0.2], [0.24, 0.38, 0.55], [0.3, 0.5, 0.32], [0.72, 0.62, 0.38], [0.5, 0.3, 0.45], [0.58, 0.54, 0.46], [0.2, 0.26, 0.2], [0.74, 0.44, 0.22]];
  const NAMES = {
    man: ['민준', '도윤', '서진', '지훈', '태양', '하준'], woman: ['서연', '지우', '하은', '수아', '유나', '은서'], elder_m: ['김 영감', '박 노인', '이 어르신'], elder_f: ['정 할머니', '최 할머니', '한 할머니'],
    boy: ['동현', '시우', '이안'], girl: ['소율', '다은', '채원'], smith: ['대장장이 철수'], baker: ['빵집 은영'], farmer: ['농부 만식', '농부 광수']
  };
  const matCache = new Map();
  function personMat(base, key, color) { const k = base.uuid + key; let m = matCache.get(k); if (!m) { m = base.clone(); m.color.setRGB(Math.pow(color[0], 2.2), Math.pow(color[1], 2.2), Math.pow(color[2], 2.2)); if (/^skin/.test(key)) { m.roughness = 0.8; m.envMapIntensity = 0.3; m.color.multiplyScalar(0.8); } else m.envMapIntensity = 0.6; matCache.set(k, m); } return m; }
  class Person {
    constructor(arch, home, opts) {
      this.arch = arch; this.home = home; this.o = opts || {}; const bundle = ARCH[arch];
      this.b = AssetLib.build(bundle); this.p = this.b.parts; this.g = new THREE.Group(); this.g.add(this.b.root); group.add(this.g);
      const sk = SKINS[(R() * SKINS.length) | 0], hr = HAIR[(R() * HAIR.length) | 0], cm = CLOTH[(R() * CLOTH.length) | 0], ca = CLOTH[(R() * CLOTH.length) | 0], cc = CLOTH[(R() * CLOTH.length) | 0];
      const old = /elder/.test(arch); const cmF = arch === 'baker' ? [0.93, 0.91, 0.86] : cm; const hairC = old ? [0.72, 0.72, 0.7] : hr;
      for (const m of this.b.meshes) {
        const n = m.material.name;
        if (n === 'skin') m.material = personMat(m.material, 'skin' + sk, sk); else if (n === 'hair') m.material = personMat(m.material, 'hair' + hairC, hairC);
        else if (n === 'cloth_main') m.material = personMat(m.material, 'cm' + cmF, cmF); else if (n === 'cloth_alt') m.material = personMat(m.material, 'ca' + ca, ca); else if (n === 'cloth_accent') m.material = personMat(m.material, 'cc' + cc, cc);
        m.castShadow = false;
      }
      const nm = NAMES[arch] || ['주민']; this.name = nm[(R() * nm.length) | 0]; this.ko = this.meta().ko || '';
      this.speed = (/elder/.test(arch) ? 0.85 : (/boy|girl/.test(arch) ? 1.5 : 1.25)) * rr(0.92, 1.08); this.phase = R() * 6; this.state = 'idle'; this.timer = rr(1, 6); this.inside = false; this.yaw = 0; this.x = 0; this.z = 0; this.y = 0; this.path = []; this.t = R() * 40;
      this.sit = 0; this.talkT = 0; this.lookT = 0; this.face = null; this.activity = 'idle'; this.workSpot = null; this.sitSpot = null;
      this.hipA = 0.55; this.walkCycle = 1.0; const mt = this.meta(); if (mt.walk) { this.hipA = (mt.walk.hip_swing_deg || 30) * D; }
      if (this.p.tool_hammer) this.p.tool_hammer.visible = true; if (this.p.tool_fork) this.p.tool_fork.visible = true; if (this.p.tool_basket) this.p.tool_basket.visible = true;
      this.restY = this.p.pelvis ? this.p.pelvis.position.y : 0;
    }
    meta() { return (AssetLib.bundle(ARCH[this.arch]) || {}).meta || {}; }
    setPos(x, z, yaw) { this.x = x; this.z = z; this.yaw = yaw || 0; this.y = terrainH(x, z); this.sync(); }
    sync() { this.g.position.set(this.x, this.y, this.z); this.g.rotation.y = this.yaw; }
  }

  function routeTo(from, target, laneSide) {      // 큰길 레인을 따라가는 경로(마을 로컬 좌표)
    const fl = villageToLocal(from[0], from[1]), tl = villageToLocal(target[0], target[1]), pts = [];
    const sgn = (z) => (z < 0 ? -1 : 1), lz0 = 3.4 * sgn(fl[1]) * (Math.abs(fl[1]) > 3.4 ? 1 : (laneSide || 1)), lz1 = 3.4 * sgn(tl[1]);
    const inStreet = (l) => Math.abs(l[1]) < 4.2 && Math.abs(l[0]) < 60;
    if (!inStreet(fl)) pts.push([fl[0] + (0), lz0]);       // 집 앞에서 큰길로 나감
    if (Math.abs(lz0 - lz1) > 0.1 && Math.abs(fl[0] - tl[0]) > 12 && false) pts.push([fl[0], 0]);
    pts.push([tl[0], inStreet(tl) ? tl[1] : lz1]);
    pts.push(tl);
    return pts.map((p) => W2(p[0], p[1]));
  }
  const dialog = {
    common: ['안녕하세요! 이 마을은 처음이세요?', '강가의 오두막에 사는 분이세요? 가끔 연기가 피어오르는 걸 봐요.', '오늘 날씨가 참 좋죠.', '호수에서는 송어랑 잉어가 잘 잡혀요. 낚싯대는 있으세요?', '숲속에는 사슴이 많아요. 조용히 다가가 보세요.', '마을 광장 우물물은 아주 시원해요.'],
    smith: ['쇠는 달궈졌을 때 두드려야 해요. 인생도 마찬가지죠.', '낫이 필요하면 말씀하세요. 튼튼하게 만들어 드릴게요.'],
    baker: ['방금 구운 빵이에요. 냄새 좋죠?', '아침 일찍 일어나 반죽하는 게 제일 힘들어요.'],
    farmer: ['올해는 사과가 풍년이에요.', '비가 좀 와야 할 텐데요. 밭이 말라가요.'],
    elder_m: ['허허, 옛날엔 이 길이 흙탕길이었지.', '젊은이, 서두르지 말게. 숲은 기다려 주니까.'],
    elder_f: ['어서 와요. 요즘 젊은 사람은 통 보기 힘들어요.', '교회 종소리가 들리면 저녁이 된 거예요.'],
    child: ['우와, 처음 보는 사람이다!', '같이 숨바꼭질 할래요?', '강에서 물고기 봤어요! 엄청 컸어요!'],
    evening: ['벌써 해가 지네요. 집에 가야겠어요.', '저녁 먹을 시간이에요. 안녕히 가세요.']
  };
  function pickLine(p) {
    const h = (typeof Atmo !== 'undefined' && Atmo.hour) || 14, pool = [];
    pool.push(...dialog.common);
    if (p.arch === 'smith') pool.push(...dialog.smith, ...dialog.smith); else if (p.arch === 'baker') pool.push(...dialog.baker, ...dialog.baker); else if (p.arch === 'farmer') pool.push(...dialog.farmer, ...dialog.farmer);
    else if (p.arch === 'elder_m') pool.push(...dialog.elder_m, ...dialog.elder_m); else if (p.arch === 'elder_f') pool.push(...dialog.elder_f, ...dialog.elder_f); else if (p.arch === 'boy' || p.arch === 'girl') pool.push(...dialog.child, ...dialog.child, ...dialog.child);
    if (h > 17) pool.push(...dialog.evening, ...dialog.evening, ...dialog.evening);
    return pool[(R() * pool.length) | 0];
  }

  /* ---------- 주민 생성 ---------- */
  function spawnPeople() {
    const need = ['villager_man', 'villager_woman'].some((b) => AssetLib.has(b)); if (!need) return;
    const homes = V.buildings.filter((b) => b.role === 'home' || b.part.startsWith('house_'));
    const byPart = (n) => V.buildings.find((b) => b.part === n);
    const roster = [];
    const add = (arch, home, job) => { if (AssetLib.has(ARCH[arch])) roster.push({ arch, home, job }); };
    const smithy = byPart('smithy'), bakery = byPart('bakery'), inn = byPart('inn'), barn = byPart('barn'), church = byPart('church'), store = byPart('storehouse');
    add('smith', smithy, { kind: 'smithy', b: smithy }); add('man', smithy, { kind: 'smithy', b: smithy });
    add('baker', bakery, { kind: 'bakery', b: bakery }); add('girl', bakery, { kind: 'play' });
    add('woman', inn, { kind: 'inn', b: inn }); add('man', inn, { kind: 'inn', b: inn });
    homes.forEach((h, i) => {
      const k = i % 6;
      if (k === 0) { add('farmer', h, { kind: 'field', b: barn || h }); add('woman', h, { kind: 'home', b: h }); add('boy', h, { kind: 'play' }); }
      else if (k === 1) { add('elder_m', h, { kind: 'sit', b: h }); add('elder_f', h, { kind: 'home', b: h }); }
      else if (k === 2) { add('man', h, { kind: 'field', b: barn || h }); add('woman', h, { kind: 'market', b: h }); add('girl', h, { kind: 'play' }); }
      else if (k === 3) { add('woman', h, { kind: 'market', b: h }); add('man', h, { kind: 'store', b: store || h }); }
      else if (k === 4) { add('elder_f', h, { kind: 'sit', b: h }); add('farmer', h, { kind: 'field', b: barn || h }); }
      else { add('man', h, { kind: 'stroll', b: h }); add('woman', h, { kind: 'stroll', b: h }); add('boy', h, { kind: 'play' }); }
    });
    const max = V.maxPeople || 34;
    for (const r of roster.slice(0, max)) {
      let p; try { p = new Person(r.arch, r.home, r.job); } catch (e) { console.warn('주민 생성 실패', r.arch, e); continue; }
      p.job = r.job; p.setPos(r.home.step[0] + rr(-1.6, 1.6), r.home.step[1] + rr(-1.6, 1.6), rr(0, TAU2)); V.people.push(p);
      r.home.inhabitants.push(p);
    }
  }
  function chooseActivity(p, h) {
    const j = p.job || {}; let w = {};
    if (h >= 17.2) w = { home: 8, stroll: 1 };
    else if (h < 8.4) w = { work: 6, home: 2, stroll: 1 };
    else if (h >= 11.2 && h < 14) w = { square: 4, inn: 3, work: 2, stroll: 2, sit: 2 };
    else w = { work: 6, stroll: 2, square: 1.5, sit: 1, market: 1.2 };
    const kind = j.kind;
    if (kind === 'play') w = h >= 17.2 ? { home: 8 } : { play: 8, square: 2, stroll: 2, home: 0.4 };
    if (kind === 'sit') w = h >= 17.2 ? { home: 8 } : { sit: 7, stroll: 1.5, square: 1.5, home: 1 };
    if (kind === 'home') w = h >= 17.2 ? { home: 8 } : { home: 3, stroll: 2, market: 2, square: 1.5 };
    if (kind === 'market' || kind === 'stroll' || kind === 'store') w = Object.assign({}, w, { market: kind === 'market' ? 4 : 1, stroll: kind === 'stroll' ? 4 : 1 }), w.work = kind === 'store' ? 5 : (w.work || 0) * 0.2;
    let tot = 0; for (const k in w) tot += w[k]; let r = R() * tot, pick = 'stroll'; for (const k in w) { r -= w[k]; if (r <= 0) { pick = k; break; } }
    return pick;
  }
  function startActivity(p, act) {
    p.activity = act; const j = p.job || {}; let tgt = null, dur = rr(14, 40); p.workSpot = null; p.sitSpot = null; p.toHome = false;
    const lanePt = (lx, side) => W2(lx, side * 3.4);
    if (act === 'home') { tgt = p.home.step; p.toHome = true; dur = 60; }
    else if (act === 'work') {
      const b = j.b || p.home; dur = rr(26, 60);
      if (j.kind === 'smithy') { const q = V.props.find((q) => q.name === 'anvil_block'); tgt = q ? [q.x + Math.sin(q.th) * 0.9, q.z + Math.cos(q.th) * 0.9] : b.step; p.workSpot = { type: 'hammer' }; }
      else if (j.kind === 'bakery') { tgt = b.step; p.workSpot = { type: 'knead' }; }
      else if (j.kind === 'inn') { tgt = b.step; p.workSpot = { type: 'sweep' }; }
      else if (j.kind === 'field') { const q = V.props.filter((q) => q.name === 'garden_plot_a'); const pick = q.length ? q[(R() * q.length) | 0] : null; tgt = pick ? [pick.x + Math.sin(pick.th) * 2.2, pick.z + Math.cos(pick.th) * 2.2] : b.step; p.workSpot = { type: 'hoe' }; }
      else { tgt = b.step; p.workSpot = { type: 'idle' }; }
    }
    else if (act === 'square') { const a = rr(0, TAU2), r = rr(2.5, 7.5), w = W2(Math.cos(a) * r, Math.sin(a) * r * 0.55 * 0 + (Math.abs(Math.sin(a)) > 0.5 ? Math.sign(Math.sin(a)) * rr(3, 5) : Math.sin(a) * 3)); tgt = w; p.workSpot = { type: 'chat' }; }
    else if (act === 'market') { const q = V.props.filter((q) => /market_stall|hay_cart/.test(q.name)); const pick = q.length ? q[(R() * q.length) | 0] : null; tgt = pick ? [pick.x + Math.sin(pick.th) * 2.4, pick.z + Math.cos(pick.th) * 2.4] : W2(0, 4); p.workSpot = { type: 'browse' }; }
    else if (act === 'inn') { const inn = V.buildings.find((b) => b.part === 'inn'); tgt = inn ? inn.step : W2(0, 4); p.toHome = false; p.enter = inn; dur = rr(18, 40); }
    else if (act === 'sit') { const q = V.props.filter((q) => q.name === 'bench_a'); const pick = q.length ? q[(R() * q.length) | 0] : null; if (pick) { tgt = [pick.x, pick.z]; p.sitSpot = { x: pick.x, z: pick.z, th: pick.th }; } else tgt = W2(0, 4); }
    else if (act === 'play') { tgt = W2(rr(-40, 40), (R() < 0.5 ? -1 : 1) * rr(4.5, 9)); p.workSpot = { type: 'idle' }; dur = rr(8, 20); }
    else { tgt = W2(rr(-46, 50), (R() < 0.5 ? -1 : 1) * 3.4); dur = rr(10, 22); }
    p.target = tgt; p.path = tgt ? routeTo([p.x, p.z], tgt, p.x > 0 ? 1 : -1) : []; p.actDur = dur; p.actT = 0; p.state = 'walk'; p.inside = false;
    if (p.inside) { p.g.visible = true; }
  }

  function updatePerson(p, dt, px, pz, hour, near) {
    p.t += dt; const pr = p.p;
    if (p.talkT > 0) { p.talkT -= dt; const dx = px - p.x, dz = pz - p.z; p.yaw = angTurn(p.yaw, Math.atan2(dx, dz), 4, dt); if (pr.jaw) pr.jaw.rotation.x = 0.12 + 0.1 * Math.sin(p.t * 14) * (p.talkT > 0.8 ? 1 : 0); }
    else if (pr.jaw) pr.jaw.rotation.x = 0;
    let moving = false;
    if (p.inside) {
      p.actT += dt; if (p.g.visible) p.g.visible = false;
      if (p.actT > p.actDur) { p.inside = false; p.g.visible = true; p.x = (p.enterB || p.home).step[0]; p.z = (p.enterB || p.home).step[1]; chooseNext(p, hour); }
      return;
    }
    if (p.talkT > 0) { poseIdle(p, dt, near); p.sync(); return; }
    if (p.state === 'walk') {
      if (!p.path.length) { p.state = 'act'; p.actT = 0; }
      else {
        const t = p.path[0], dx = t[0] - p.x, dz = t[1] - p.z, d = Math.hypot(dx, dz);
        if (d < 0.5) { p.path.shift(); if (!p.path.length) p.state = 'act'; }
        else { const ty = Math.atan2(dx, dz); p.yaw = angTurn(p.yaw, ty, 5, dt); const sp = p.speed * (angDiffAbs(p.yaw, ty) > 1 ? 0.2 : 1); const nx = p.x + Math.sin(p.yaw) * sp * dt, nz = p.z + Math.cos(p.yaw) * sp * dt; p.x = nx; p.z = nz; moving = true; p.phase += dt * sp * 2.6; }
        p.actT = 0;
      }
      if (p.state === 'act') {
        if (p.toHome || p.enter) { p.inside = true; p.actT = 0; p.actDur = p.toHome ? rr(30, 120) : rr(20, 45); p.enterB = p.enter || null; p.enter = null; p.g.visible = false; return; }
        if (p.sitSpot) { p.yaw = p.sitSpot.th + Math.PI; }
      }
    } else if (p.state === 'act') {
      p.actT += dt; if (p.actT > p.actDur) chooseNext(p, hour);
    }
    // 주위 주민과 어울리기(근처 다른 주민을 바라봄)
    p.y = terrainH(p.x, p.z);
    if (moving) poseWalk(p, dt); else if (p.state === 'act') poseAct(p, dt, near); else poseIdle(p, dt, near);
    p.sync();
  }
  function chooseNext(p, hour) { startActivity(p, chooseActivity(p, hour)); }
  function angTurn(a, b, rate, dt) { let d = (b - a) % TAU2; if (d > Math.PI) d -= TAU2; if (d < -Math.PI) d += TAU2; return a + Math.max(-rate * dt, Math.min(rate * dt, d)); }
  function angDiffAbs(a, b) { let d = (b - a) % TAU2; if (d > Math.PI) d -= TAU2; if (d < -Math.PI) d += TAU2; return Math.abs(d); }
  function resetPose(p) { const pr = p.p; for (const k in pr) { if (pr[k].rotation && !/^tool_/.test(k)) pr[k].rotation.set(0, 0, 0); } if (pr.pelvis) pr.pelvis.position.y = p.restY; }
  function poseWalk(p, dt) {
    const pr = p.p, ph = p.phase, A = p.hipA * (p.speed > 1.4 ? 1.2 : 1), s = Math.sin(ph), c = Math.cos(ph);
    const SG = V.walkSign;       // +1: 양의 X 회전이 다리를 뒤로 보낸다 (확인된 부호)
    if (pr.leg_l_upper) { pr.leg_l_upper.rotation.x = -SG * A * s; pr.leg_r_upper.rotation.x = SG * A * s; }
    if (pr.leg_l_lower) { pr.leg_l_lower.rotation.x = SG * Math.max(0, -c) * A * 1.1 * (s > 0 ? 0.6 : 1) + SG * 0.1; pr.leg_r_lower.rotation.x = SG * Math.max(0, c) * A * 1.1 * (s < 0 ? 0.6 : 1) + SG * 0.1; }
    if (pr.foot_l) { pr.foot_l.rotation.x = -SG * 0.25 * Math.max(0, -c) * 0 - SG * 0.1 * s; pr.foot_r.rotation.x = SG * 0.1 * s; }
    if (pr.arm_l_upper) {
      const holdL = p.arch === 'baker', holdR = p.arch === 'elder_m' || p.arch === 'smith' || p.arch === 'farmer';      // 도구를 든 팔은 거의 고정
      pr.arm_l_upper.rotation.x = SG * A * 0.7 * s * (holdL ? 0.12 : 1); pr.arm_r_upper.rotation.x = -SG * A * 0.7 * s * (holdR ? 0.12 : 1); pr.arm_l_upper.rotation.z = 0.04; pr.arm_r_upper.rotation.z = -0.04;
    }
    if (pr.arm_l_lower) { const hl = p.arch === 'baker' ? 0.2 : 1, hr = (p.arch === 'elder_m' || p.arch === 'smith' || p.arch === 'farmer') ? 0.2 : 1; pr.arm_l_lower.rotation.x = (-SG * 0.25 - SG * 0.2 * Math.max(0, s)) * hl; pr.arm_r_lower.rotation.x = (-SG * 0.25 - SG * 0.2 * Math.max(0, -s)) * hr; }
    if (pr.pelvis) { pr.pelvis.position.y = p.restY + 0.018 * Math.abs(Math.cos(ph)) * (p.speed > 1.4 ? 1.5 : 1) - 0.01; pr.pelvis.rotation.y = 0.07 * s; }
    if (pr.torso) { pr.torso.rotation.y = -0.1 * s; pr.torso.rotation.z = 0.02 * c; }
    if (pr.neck_head) pr.neck_head.rotation.y = 0.04 * s;
    if (p.p.tool_fork && p.job && p.job.kind === 'field') { p.p.tool_fork.visible = true; p.p.tool_fork.rotation.x = 0; }
  }
  function poseIdle(p, dt, near) {
    const pr = p.p, t = p.t, SG = V.walkSign; const br = Math.sin(t * 1.6) * 0.012;
    for (const k of ['leg_l_upper', 'leg_r_upper', 'leg_l_lower', 'leg_r_lower', 'foot_l', 'foot_r']) if (pr[k]) pr[k].rotation.set(0, 0, 0);
    if (pr.arm_l_upper) { pr.arm_l_upper.rotation.set(0.05 * Math.sin(t * 0.8), 0, 0.05 + br); pr.arm_r_upper.rotation.set(-0.05 * Math.sin(t * 0.8), 0, -0.05 - br); pr.arm_l_lower.rotation.set(-SG * 0.12, 0, 0); pr.arm_r_lower.rotation.set(-SG * 0.12, 0, 0); }
    if (pr.pelvis) { pr.pelvis.position.y = p.restY; pr.pelvis.rotation.set(0, 0, 0); }
    if (pr.torso) pr.torso.rotation.set(br * 2, 0.05 * Math.sin(t * 0.5), 0);
    if (pr.neck_head) pr.neck_head.rotation.set(0, 0.35 * Math.sin(t * 0.37) * (Math.sin(t * 0.21) > 0 ? 1 : 0.2), 0);
    if (near && p.talkT <= 0 && near < 8) { const dx = V.px - p.x, dz = V.pz - p.z; const dy = angTurn(p.yaw, Math.atan2(dx, dz), 1.6, dt); p.yaw = dy; }
  }
  function poseAct(p, dt, near) {
    const pr = p.p, t = p.t, SG = V.walkSign, ws = p.workSpot || { type: 'idle' };
    if (p.sitSpot) {                       // 벤치에 앉기
      const k = Math.min(1, p.actT * 1.2); p.sit += (1 - p.sit) * Math.min(1, dt * 5);
      if (pr.pelvis) pr.pelvis.position.y = p.restY - 0.42 * p.sit; if (pr.leg_l_upper) { pr.leg_l_upper.rotation.x = -SG * 1.5 * p.sit; pr.leg_r_upper.rotation.x = -SG * 1.5 * p.sit; pr.leg_l_lower.rotation.x = SG * 1.55 * p.sit; pr.leg_r_lower.rotation.x = SG * 1.55 * p.sit; }
      const bx = p.sitSpot.x + Math.sin(p.sitSpot.th) * 0.0, bz = p.sitSpot.z + Math.cos(p.sitSpot.th) * 0.0; p.x += (bx - p.x) * Math.min(1, dt * 2); p.z += (bz - p.z) * Math.min(1, dt * 2);
      if (pr.arm_l_upper) { pr.arm_l_upper.rotation.x = -SG * 0.4; pr.arm_r_upper.rotation.x = -SG * 0.4; pr.arm_l_lower.rotation.x = -SG * 0.6; pr.arm_r_lower.rotation.x = -SG * 0.6; }
      if (pr.neck_head) pr.neck_head.rotation.y = 0.3 * Math.sin(t * 0.3); return;
    }
    p.sit += (0 - p.sit) * Math.min(1, dt * 5);
    for (const k of ['leg_l_upper', 'leg_r_upper', 'leg_l_lower', 'leg_r_lower', 'foot_l', 'foot_r']) if (pr[k]) pr[k].rotation.set(0, 0, 0);
    if (pr.pelvis) { pr.pelvis.position.y = p.restY; pr.pelvis.rotation.set(0, 0, 0); }
    if (ws.type === 'hammer' && pr.arm_r_upper) {
      if (pr.tool_hammer) pr.tool_hammer.visible = true; const u = (t * 1.4) % 1, sw = u < 0.55 ? u / 0.55 : 1 - (u - 0.55) / 0.12; const hit = Math.max(0, 1 - Math.abs(u - 0.6) * 12);
      pr.arm_r_upper.rotation.x = -SG * (0.4 + 1.9 * Math.max(0, Math.min(1, sw))); pr.arm_r_lower.rotation.x = -SG * (0.8 + 0.5 * sw); pr.arm_l_upper.rotation.x = -SG * 0.5; pr.arm_l_lower.rotation.x = -SG * 0.9;
      if (pr.torso) pr.torso.rotation.x = SG * (0.12 + 0.1 * hit); if (u > 0.58 && u < 0.62 && !p._hit && V.px !== undefined) { p._hit = true; if (Math.hypot(V.px - p.x, V.pz - p.z) < 45) clang(Math.hypot(V.px - p.x, V.pz - p.z)); } if (u < 0.5) p._hit = false;
    } else if (ws.type === 'knead' && pr.arm_l_upper) {
      const k = Math.sin(t * 5) * 0.2; pr.arm_l_upper.rotation.x = -SG * (0.9 + k); pr.arm_r_upper.rotation.x = -SG * (0.9 - k); pr.arm_l_lower.rotation.x = -SG * 0.7; pr.arm_r_lower.rotation.x = -SG * 0.7; if (pr.torso) pr.torso.rotation.x = SG * (0.25 + 0.05 * Math.sin(t * 5));
    } else if (ws.type === 'sweep' && pr.arm_l_upper) {
      const k = Math.sin(t * 2.6) * 0.35; pr.arm_l_upper.rotation.x = -SG * 0.8; pr.arm_r_upper.rotation.x = -SG * 0.8; pr.arm_l_lower.rotation.x = -SG * 0.4; pr.arm_r_lower.rotation.x = -SG * 0.4; if (pr.torso) { pr.torso.rotation.x = SG * 0.2; pr.torso.rotation.y = k; }
    } else if (ws.type === 'hoe' && pr.arm_l_upper) {
      const u = (t * 0.55) % 1, d = Math.sin(Math.PI * u); pr.arm_l_upper.rotation.x = -SG * (0.5 + 1.5 * d); pr.arm_r_upper.rotation.x = -SG * (0.5 + 1.5 * d); pr.arm_l_lower.rotation.x = -SG * 0.5; pr.arm_r_lower.rotation.x = -SG * 0.5; if (pr.torso) pr.torso.rotation.x = SG * (0.15 + 0.5 * d);
    } else if (ws.type === 'chat' || ws.type === 'browse') {
      const gx = Math.sin(t * 1.3) * 0.25; poseIdle(p, dt, near); if (pr.arm_r_upper) { pr.arm_r_upper.rotation.x = -SG * (0.5 + 0.5 * Math.max(0, Math.sin(t * 1.1))); pr.arm_r_lower.rotation.x = -SG * (0.6 + 0.3 * Math.sin(t * 2.3)); }
      if (pr.jaw && ws.type === 'chat' && Math.sin(t * 0.7) > 0.2) pr.jaw.rotation.x = 0.06 + 0.06 * Math.sin(t * 11); if (pr.neck_head) pr.neck_head.rotation.y = gx; return;
    } else poseIdle(p, dt, near);
  }
  let _clangT = 0;
  function clang(d) { const c = Sound.ctx; if (!c || !Sound.master) return; const g0 = 0.18 * Math.max(0.05, 1 - d / 45), t = c.currentTime; if (t - _clangT < 0.08) return; _clangT = t; for (const [f, v] of [[1850, 1], [2900, 0.5], [1200, 0.7]]) { const o = c.createOscillator(), g = c.createGain(); o.type = 'sine'; o.frequency.value = f * (0.97 + Math.random() * 0.06); g.gain.setValueAtTime(g0 * v, t); g.gain.exponentialRampToValueAtTime(0.0005, t + 0.35); o.connect(g); g.connect(Sound.master); o.start(t); o.stop(t + 0.4); } }

  /* ---------- 가축 ---------- */
  function spawnLivestock() {
    if (typeof Fauna === 'undefined' || !Fauna.Quad) return;
    const barn = V.buildings.find((b) => b.part === 'barn'), farm = V.buildings.find((b) => b.part === 'house_farm');
    const field = barn ? W2(barn.lx + 2, barn.lz + 14) : W2(-26, 52);
    const mk = (bundle, n, o, c, rad) => { if (!AssetLib.has(bundle)) return; for (let i = 0; i < n; i++) { try { const a = new Fauna.Quad(bundle, o); const ang = rr(0, TAU2), r = rr(2, rad); a.setPos(c[0] + Math.cos(ang) * r, c[1] + Math.sin(ang) * r, rr(0, TAU2)); a.home = [c[0], c[1]]; a.home.radius = rad + 2; a.state = 'graze'; a.timer = rr(2, 10); a.village = true; V.livestock.push(a); } catch (e) { console.warn('가축 생성 실패', bundle, e); } } };
    const okVill = (x, z) => true;
    mk('animal_cow', 3, { scale: 1, walk: 0.7, run: 3.2, fleeDist: 3, alertDist: 6, stride: 1.4, len: 0.9, roam: 12, grazeNeck: 55, grazeHead: 22, tailSwish: true }, field, 9);
    mk('animal_sheep', 5, { scale: 1, walk: 0.6, run: 3.4, fleeDist: 4, alertDist: 8, stride: 0.9, len: 0.6, roam: 12, grazeNeck: 50, grazeHead: 20 }, (() => { const l = villageToLocal(field[0], field[1]); return W2(l[0] + 12, l[1]); })(), 11);
    if (AssetLib.has('animal_dog')) { for (let i = 0; i < 2; i++) { try { const a = new Fauna.Quad('animal_dog', { scale: 1, walk: 1.1, run: 5.2, fleeDist: 0.1, alertDist: 5, stride: 0.8, len: 0.5, roam: 30, grazeNeck: 40, grazeHead: 25, tailSwish: true }); const c = W2(rr(-30, 30), 6); a.setPos(c[0], c[1], rr(0, TAU2)); a.home = [c[0], c[1]]; a.home.radius = 36; a.state = 'sniff'; a.timer = rr(2, 6); a.village = true; V.livestock.push(a); } catch (e) { } } }
    // 닭: 닭장 주변
    for (const bundle of ['animal_chicken', 'animal_rooster']) {
      if (!AssetLib.has(bundle)) continue; const n = bundle === 'animal_chicken' ? 6 : 1; const coop = V.props.find((q) => q.name === 'chicken_coop') || { x: farm ? farm.pos[0] : field[0], z: farm ? farm.pos[2] : field[1] };
      for (let i = 0; i < n; i++) { try { const c = new Chicken(bundle, coop); V.livestock.push(c); } catch (e) { console.warn('닭 생성 실패', e); } }
    }
    if (AssetLib.has('animal_cat')) { try { const q = V.props.find((p) => p.name === 'bench_a'); const a = new Fauna.Quad('animal_cat', { scale: 1, walk: 0.8, run: 4.5, fleeDist: 3, alertDist: 5, stride: 0.6, len: 0.35, roam: 14, grazeNeck: 35, grazeHead: 15, tailSwish: true }); const c = q ? [q.x, q.z] : W2(6, -6); a.setPos(c[0], c[1], 0); a.home = [c[0], c[1]]; a.home.radius = 16; a.state = 'look'; a.timer = rr(3, 8); V.livestock.push(a); } catch (e) { } }
  }
  class Chicken {
    constructor(bundle, coop) {
      this.bundle = bundle; this.b = AssetLib.build(bundle); this.p = this.b.parts; this.g = new THREE.Group(); this.g.add(this.b.root); group.add(this.g); this.b.meshes.forEach((m) => m.castShadow = false);
      this.home = [coop.x, coop.z]; const a = rr(0, TAU2), r = rr(1.5, 5); this.x = coop.x + Math.cos(a) * r; this.z = coop.z + Math.sin(a) * r; this.yaw = rr(0, TAU2); this.t = R() * 30; this.mode = 'peck'; this.timer = rr(1, 4); this.tx = this.x; this.tz = this.z; this.peck = 0; this.village = true;
    }
    update(dt, px, pz) {
      this.t += dt; this.timer -= dt; const p = this.p, d = Math.hypot(this.x - px, this.z - pz);
      if (d < 3 && this.mode !== 'flee') { this.mode = 'flee'; this.timer = 2; const a = Math.atan2(this.x - px, this.z - pz); this.tx = this.x + Math.sin(a) * 5; this.tz = this.z + Math.cos(a) * 5; }
      if (this.timer < 0) { if (R() < 0.45) { this.mode = 'walk'; const a = rr(0, TAU2), r = rr(1, 5); this.tx = this.home[0] + Math.cos(a) * r; this.tz = this.home[1] + Math.sin(a) * r; this.timer = rr(2, 5); } else { this.mode = 'peck'; this.timer = rr(2, 6); } }
      let sp = 0; if (this.mode === 'walk' || this.mode === 'flee') { const dx = this.tx - this.x, dz = this.tz - this.z, dd = Math.hypot(dx, dz); if (dd > 0.2) { this.yaw = angTurn(this.yaw, Math.atan2(dx, dz), 6, dt); sp = this.mode === 'flee' ? 3.2 : 0.7; this.x += Math.sin(this.yaw) * sp * dt; this.z += Math.cos(this.yaw) * sp * dt; } else this.timer = 0; }
      const ph = this.t * (this.mode === 'flee' ? 16 : 7); if (p.leg_l) { p.leg_l.rotation.x = sp ? 0.7 * Math.sin(ph) : 0; p.leg_r.rotation.x = sp ? -0.7 * Math.sin(ph) : 0; }
      const pk = this.mode === 'peck' ? Math.max(0, Math.sin(this.t * 6)) ** 2 * (Math.sin(this.t * 0.8) > -0.3 ? 1 : 0) : 0; if (p.head) p.head.rotation.x = 0.9 * pk + (sp ? 0.15 * Math.sin(ph * 2) : 0);
      if (this.mode === 'flee') { if (p.wing_l) { p.wing_l.rotation.z = 0.7 * Math.sin(ph * 2); p.wing_r.rotation.z = -0.7 * Math.sin(ph * 2); } } else if (p.wing_l) { p.wing_l.rotation.z = 0; p.wing_r.rotation.z = 0; }
      this.y = terrainH(this.x, this.z); this.g.position.set(this.x, this.y, this.z); this.g.rotation.y = this.yaw;
    }
  }

  /* ---------- 상호작용 ---------- */
  function nearestPerson(px, pz, r) { let best = null, bd = r; for (const p of V.people) { if (p.inside || !p.g.visible) continue; const d = Math.hypot(p.x - px, p.z - pz); if (d < bd) { bd = d; best = p; } } return best; }
  function talk() {
    const hud = document.getElementById('hud'); if (!hud || hud.style.display === 'none') return;
    const p = nearestPerson(Player.pos.x, Player.pos.z, 2.8); if (!p) return;
    p.talkT = 5.5; talking = p; bubble.innerHTML = '<div style="font-size:12px;color:#e8c98a;margin-bottom:3px">' + p.name + (p.ko ? ' · ' + p.ko : '') + '</div><div>' + pickLine(p) + '</div>'; bubble.style.display = 'block'; bubbleT = 5.5;
  }

  V.init = function (sc) {
    scene = sc; group = new THREE.Group(); group.name = 'village'; scene.add(group);
    V.walkSign = 1;
    if (!AssetLib.has('village_houses') && !AssetLib.has('village_props')) return;
    const vm = (AssetLib.bundle('villager_man') || {}).meta; if (vm && vm.walk && vm.walk.sign) V.walkSign = vm.walk.sign;
    buildHouses(); buildSmoke(); layoutProps(); spawnPeople(); spawnLivestock();
    promptEl = document.createElement('div'); promptEl.style.cssText = 'position:fixed;left:50%;bottom:22%;transform:translateX(-50%);padding:7px 14px;border-radius:10px;background:rgba(18,24,20,.72);border:1px solid rgba(255,255,255,.18);color:#f3efe6;font-size:15px;display:none;z-index:8;pointer-events:none'; document.body.appendChild(promptEl);
    bubble = document.createElement('div'); bubble.style.cssText = 'position:fixed;left:50%;top:60%;transform:translateX(-50%);max-width:420px;padding:10px 18px;border-radius:14px;background:rgba(250,246,236,.94);border:1px solid rgba(60,40,20,.4);color:#2a2112;font-size:16px;line-height:1.5;display:none;z-index:8;pointer-events:none;box-shadow:0 8px 28px rgba(0,0,0,.4)'; document.body.appendChild(bubble);
    window.addEventListener('keydown', (e) => { if (e.code === 'KeyE' && !e.repeat) talk(); });
    // 초기 활동 배정(분산 시작)
    const h0 = (typeof Atmo !== 'undefined' && Atmo.hour) || 14; for (const p of V.people) { startActivity(p, chooseActivity(p, h0)); p.actT = rr(0, p.actDur * 0.6); const pt = p.path[p.path.length - 1]; if (pt && R() < 0.7) { p.x = pt[0] + rr(-0.5, 0.5); p.z = pt[1] + rr(-0.5, 0.5); p.path = []; p.state = 'act'; if (p.toHome || p.enter) { p.inside = true; p.actDur = rr(10, 80); p.actT = 0; p.g.visible = false; } } p.y = terrainH(p.x, p.z); p.sync(); }
    group.traverse((o) => { if (o.isMesh || o.isPoints || o.isInstancedMesh) o.layers.set(1); });          // 물 반사 패스에서 제외
    if (smokeMesh) smokeMesh.layers.set(1);
    V.ready = true;
  };
  V.setEnabled = function (on) { V.enabled = !!on; if (group) group.visible = !!on; if (promptEl && !on) promptEl.style.display = 'none'; };
  V.setNight = function (t) { V.night = t; };

  const VIS_PEOPLE = 60;
  V.update = function (dt, camera) {
    if (!V.ready || !V.enabled) return;
    V.t += dt; const px = Player.pos.x, pz = Player.pos.z, hour = (typeof Atmo !== 'undefined' && Atmo.hour) || 14; V.px = px; V.pz = pz;
    const dv = villageDist(px, pz), night = Math.max(V.night, hour > 17.2 ? Math.min(1, (hour - 17.2) / 1.0) : 0);
    // 창문 불빛 / 대장간 불
    for (const m of glowMats) m.emissiveIntensity = 1.6 * night * (dv < 90 ? 1 : 0);
    for (const m of flameMats) m.emissiveIntensity = (1.8 + 0.6 * Math.sin(V.t * 9) * Math.sin(V.t * 5.3)) * (/forge/i.test(m.name) ? 1 : (0.5 + 0.5 * night));
    if (smokeMesh) { smokeMesh.visible = dv < 120; smokeMesh.material.uniforms.uPix.value = innerHeight * Math.min(window.devicePixelRatio || 1, 2) / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2)); }
    group.visible = dv < 150;
    if (dv > 140) { if (promptEl) promptEl.style.display = 'none'; return; }
    for (const p of V.people) {
      const d = Math.hypot(p.x - px, p.z - pz); const vis = d < VIS_PEOPLE;
      if (!vis && !p.inside) { // 멀리 있을 때는 단순 이동만
        p.t += dt; if (p.state === 'walk' && p.path.length) { const t = p.path[0], dx = t[0] - p.x, dz = t[1] - p.z, dd = Math.hypot(dx, dz); if (dd < 0.6) p.path.shift(); else { p.yaw = Math.atan2(dx, dz); p.x += dx / dd * p.speed * dt; p.z += dz / dd * p.speed * dt; } if (!p.path.length) { p.state = 'act'; p.actT = 0; if (p.toHome || p.enter) { p.inside = true; p.actDur = rr(30, 120); p.enterB = p.enter || null; p.enter = null; } } } else { p.actT += dt; if (p.actT > p.actDur) chooseNext(p, hour); }
        p.g.visible = false; continue;
      }
      if (vis) { if (!p.inside) p.g.visible = true; }
      const wasHidden = !p.g.visible && !p.inside; updatePerson(p, dt, px, pz, hour, d);
      const sh = d < 18; if (p._sh !== sh) { p._sh = sh; for (const m of p.b.meshes) m.castShadow = sh; }
      // 플레이어와 겹치면 살짝 밀어내기
      if (!p.inside && d < 0.7) { const nx = (px - p.x) / (d || 1), nz = (pz - p.z) / (d || 1), push = 0.7 - d; Player.pos.x += nx * push; Player.pos.z += nz * push; }
    }
    for (const a of V.livestock) { const d = Math.hypot(a.x - px, a.z - pz); if (d > 90) { a.g.visible = false; continue; } a.g.visible = true; a.update(Math.min(dt, 0.05), px, pz); }
    // 말풍선 / 안내
    if (bubbleT > 0) { bubbleT -= dt; if (bubbleT <= 0 || !talking || Math.hypot(talking.x - px, talking.z - pz) > 6) { bubble.style.display = 'none'; bubbleT = 0; } }
    const np = nearestPerson(px, pz, 2.8), hud = document.getElementById('hud');
    if (np && bubbleT <= 0 && hud && hud.style.display !== 'none') { promptEl.style.display = 'block'; promptEl.textContent = 'E  ' + np.name + '에게 말 걸기'; } else promptEl.style.display = 'none';
  };
  return V;
})();
