/* =====================================================================
   09b_flora.js — Blender 야생화/수변식물/버섯: 군락 배치 + 거리별 LOD 인스턴싱 + 바람 흔들림
   서식지(meadow/path/forest_edge/garden/water_edge/wet/shade)는 번들 메타의 habitat 을 따른다.
   ===================================================================== */
const Flora = (function () {
  const R = mulberry32(31337), rr = (a, b) => a + (b - a) * R(), TAU2 = Math.PI * 2;
  const F = { slots: new Map(), inst: [], species: {}, ready: false, scale: 1, last: [1e9, 1e9], timer: 0, bundles: [] };
  const _m = new THREE.Matrix4(), _q = new THREE.Quaternion(), _e = new THREE.Euler(), _p = new THREE.Vector3(), _s = new THREE.Vector3();

  const WIND_VERT = `
    vec3 ip = instanceMatrix[3].xyz; float hh = max(position.y, 0.0);
    float gst = gustAt(ip);
    float bend = (0.055 * gst + 0.018 * sin(uTime * 2.6 + ip.x * 2.7 + ip.z * 1.9 + hh * 3.0)) * hh * hh;
    transformed.x += uWind.x * bend; transformed.z += uWind.y * bend;`;
  function floraMaterial(bundle, mname, sub) {
    const base = AssetLib.material(bundle, mname, sub);
    const key = bundle + '/flora/' + mname + (sub && sub.col ? '/vc' : '');
    if (F.mats && F.mats.has(key)) return F.mats.get(key);
    const m = base.clone(); m.name = mname; m.side = THREE.DoubleSide;
    { const c = m.color, mx = Math.max(c.r, c.g, c.b); if (mname === 'impostor') c.setScalar(0.42); else if (mx > 0.3) c.multiplyScalar(0.3 / mx); m.envMapIntensity = 0.7; m.roughness = Math.max(m.roughness, 0.6); }
    m.onBeforeCompile = function (shader) {
      applyShared(shader);
      shader.vertexShader = shader.vertexShader.replace('#include <common>', '#include <common>\n' + GLSL_WIND_FN).replace('#include <begin_vertex>', '#include <begin_vertex>\n' + WIND_VERT);
    };
    m.customProgramCacheKey = function () { return 'flora_wind_' + (m.vertexColors ? 'vc' : 'n'); };
    (F.mats = F.mats || new Map()).set(key, m); return m;
  }

  function habitatOf(x, z) {
    const h = terrainH(x, z), rx = riverX(z), hw = riverHalfW(z), dr = Math.abs(x - rx);
    const lk = lakeT(x, z);
    if (h < WATER_Y - 0.12) return (dr < hw * 1.05 || lk < 1.0) ? 'water' : null;
    if ((dr < hw * 1.7 || lk < 1.75) && h < WATER_Y + 0.75) return 'water_edge';
    if (inHouseBox(x, z, 0) || inVillage(x, z, 1)) return null;
    // 앞마당(집 로컬 좌표): 정원
    const c = Math.cos(HOUSE.rot), s = Math.sin(HOUSE.rot), dx = x - HOUSE.x, dz = z - HOUSE.z, lx = c * dx - s * dz, lz = s * dx + c * dz;
    if (Math.abs(lx) < 15 && lz > 4.2 && lz < 12.5) return 'garden';
    if (Math.abs(x) > HALF - 6 || Math.abs(z) > HALF - 6) return null;
    const sl = Math.hypot(terrainH(x + 1.4, z) - terrainH(x - 1.4, z), terrainH(x, z + 1.4) - terrainH(x, z - 1.4)) / 2.8;
    if (sl > 0.5 || h > 70) return null;
    const pa = pathAt(x, z); if (pa > 0.7) return null; if (pa > 0.22) return 'path';
    const f = forestField(x, z); if (f > 0.68) return 'shade'; if (f > 0.36) return 'forest_edge';
    return 'meadow';
  }
  const ELIGIBLE = {
    meadow: ['meadow'], path: ['path', 'meadow'], forest_edge: ['forest_edge', 'meadow', 'shade'], shade: ['shade', 'forest_edge', 'forest'],
    garden: ['garden', 'meadow'], water_edge: ['water_edge', 'wet'], water: ['water_lily'], wet: ['wet']
  };

  F.init = function (scene) {
    F.scene = scene;
    const names = ['flowers_meadow', 'plants_water_edge'].filter((n) => AssetLib.has(n));
    if (!names.length) return;
    const defs = [];
    for (const bn of names) {
      const B = AssetLib.bundle(bn), meta = B.meta || {}, have = new Set(B.parts.map((p) => p.name));
      for (const sp in (meta.species || {})) {
        const S = meta.species[sp];
        const variants = (S.variants || []).filter((v) => have.has(sp + '_' + v));
        // 버섯은 버섯끼리 meta.species 에 없을 수 있어 prefix 탐색
        if (!variants.length) continue;
        const hab = /lilypad|waterlily/.test(sp) ? 'water_lily' : (/mushroom/.test(sp) ? 'forest' : S.habitat || 'meadow');
        defs.push({ bundle: bn, sp, ko: S.ko, hab, weight: S.weight === undefined ? 0.5 : S.weight, variants, lod1: variants.every((v) => have.has(sp + '_' + v + '_lod1')), lod2: variants.every((v) => have.has(sp + '_' + v + '_lod2')) });
      }
      // meta.species 에 없는 버섯 등 추가
      const seen = new Set(defs.filter((d) => d.bundle === bn).map((d) => d.sp));
      const groups = {};
      for (const p of B.parts) { const m = /^(.*)_([a-d])$/.exec(p.name); if (m && !seen.has(m[1])) (groups[m[1]] = groups[m[1]] || []).push(m[2]); }
      for (const sp in groups) defs.push({ bundle: bn, sp, ko: sp, hab: /mushroom/.test(sp) ? 'forest' : 'meadow', weight: 0.4, variants: groups[sp], lod1: false, lod2: false });
    }
    F.defs = defs; F.species = Object.fromEntries(defs.map((d) => [d.sp, d]));
    // 군락 생성
    const spawnC = [HOUSE.x + 6, HOUSE.z + 8];
    const byHab = {}; for (const d of defs) for (const tag of [d.hab, d.hab === 'wet' ? 'water_edge' : null].filter(Boolean)) (byHab[tag] = byHab[tag] || []).push(d);
    const K = 70;
    for (const d of defs) {
      const isTall = /sunflower|cosmos|lupine|foxglove|reed|cattail|queen/.test(d.sp);
      const nc = Math.max(3, Math.round(d.weight * K * (/grass_tuft|sedge|clover_white/.test(d.sp) ? 1.4 : 1) * (d.hab === 'garden' ? 0.55 : 1) * (/sunflower/.test(d.sp) ? 0.45 : 1)));
      for (let c = 0; c < nc; c++) {
        let cx = 0, cz = 0, ok = false;
        const near = R() < 0.55 || d.hab === 'garden';
        for (let t = 0; t < 90 && !ok; t++) {
          if (d.hab === 'water_lily') { if (R() < 0.45) { const q = lakePt(rr(-0.8, 0.8), rr(-0.8, 0.8)); cx = q[0]; cz = q[1]; } else { const z = rr(-180, 180), hw = riverHalfW(z); cx = riverX(z) + rr(-0.85, 0.85) * hw; cz = z; } }
          else if (d.hab === 'water_edge' || d.hab === 'wet') { if (R() < 0.5) { const an = R() * TAU2, rf = rr(0.95, 1.5), q = lakePt(Math.cos(an) * rf, Math.sin(an) * rf); cx = q[0]; cz = q[1]; } else { const z = rr(-180, 180), hw = riverHalfW(z), sd = R() < 0.5 ? -1 : 1; cx = riverX(z) + sd * hw * rr(0.85, 1.6); cz = z; } }
          else if (d.hab === 'garden') { const a = rr(-12, 12), b = rr(4.6, 12); const cs = Math.cos(HOUSE.rot), sn = Math.sin(HOUSE.rot); cx = HOUSE.x + cs * a + sn * b; cz = HOUSE.z - sn * a + cs * b; }
          else if (near) { const a = R() * TAU2, r = Math.sqrt(R()) * 120; cx = spawnC[0] + Math.cos(a) * r; cz = spawnC[1] + Math.sin(a) * r; }
          else { cx = rr(-HALF + 8, HALF - 8); cz = rr(-HALF + 8, HALF - 8); }
          const hb = habitatOf(cx, cz);
          if (hb && (ELIGIBLE[hb] || []).includes(d.hab)) ok = true;
        }
        if (!ok) continue;
        const cnt = d.hab === 'water_lily' ? (3 + (R() * 6 | 0)) : Math.round((isTall ? 5 : 10) + R() * (isTall ? 8 : 22)) * (d.hab === 'garden' ? 1.2 : 1), rad = d.hab === 'water_lily' ? 2.5 : rr(1.2, isTall ? 2.6 : 3.8);
        for (let i = 0; i < cnt; i++) {
          const a = R() * TAU2, r = Math.sqrt(R()) * rad, x = cx + Math.cos(a) * r, z = cz + Math.sin(a) * r;
          const hb = habitatOf(x, z); if (!hb || !(ELIGIBLE[hb] || []).includes(d.hab)) continue;
          const v = d.variants[(R() * d.variants.length) | 0], sc = rr(0.8, 1.25) * (d.hab === 'water_lily' ? rr(0.9, 1.4) : (d.hab === 'meadow' || d.hab === 'path' || d.hab === 'forest_edge' ? 1.55 : 1));
          const y = d.hab === 'water_lily' ? WATER_Y + 0.012 : terrainH(x, z) - 0.02;
          _e.set(d.hab === 'water_lily' ? 0 : rr(-0.08, 0.08), R() * TAU2, d.hab === 'water_lily' ? 0 : rr(-0.08, 0.08)); _q.setFromEuler(_e); _p.set(x, y, z); _s.setScalar(sc);
          _m.compose(_p, _q, _s);
          const inst = { x, z, d, v, m: new Float32Array(_m.elements), tint: 0.85 + R() * 0.3, tint2: 0.9 + R() * 0.2, part: d.sp + '_' + v };
          F.inst.push(inst);
        }
      }
    }
    // 군락 사이에 흩어진 단독 개체 (초원이 듬성하지 않도록)
    const scat = defs.filter((d) => d.hab === 'meadow' || d.hab === 'path' || d.hab === 'forest_edge');
    const wsum = scat.reduce((s, d) => s + d.weight, 0);
    for (let i = 0; i < 90000; i++) {
      const near = R() < 0.72, a = R() * TAU2, r = Math.sqrt(R()) * 135;
      const x = near ? spawnC[0] + Math.cos(a) * r : rr(-HALF + 8, HALF - 8), z = near ? spawnC[1] + Math.sin(a) * r : rr(-HALF + 8, HALF - 8);
      const hb = habitatOf(x, z); if (!hb) continue;
      let w = R() * wsum, d = null; for (const q of scat) { w -= q.weight; if (w <= 0) { d = q; break; } } if (!d) d = scat[0];
      if (!(ELIGIBLE[hb] || []).includes(d.hab)) continue;
      const v = d.variants[(R() * d.variants.length) | 0], sc = rr(0.9, 1.4) * 1.55, y = terrainH(x, z) - 0.02;
      _e.set(rr(-0.08, 0.08), R() * TAU2, rr(-0.08, 0.08)); _q.setFromEuler(_e); _p.set(x, y, z); _s.setScalar(sc); _m.compose(_p, _q, _s);
      F.inst.push({ x, z, d, v, m: new Float32Array(_m.elements), tint: 0.85 + R() * 0.3, tint2: 0.9 + R() * 0.2, part: d.sp + '_' + v });
    }
    // 슬롯(부품별 InstancedMesh) 생성: 각 인스턴스가 쓰는 (부품, LOD) 별 최대 개수
    const need = new Map();
    for (const it of F.inst) { const k0 = it.d.bundle + '|' + it.part, k1 = k0 + '_lod1', k2 = k0 + '_lod2'; need.set(k0, (need.get(k0) || 0) + 1); if (it.d.lod1) need.set(k1, (need.get(k1) || 0) + 1); if (it.d.lod2) need.set(k2, (need.get(k2) || 0) + 1); }
    for (const [k, cap] of need) {
      const [bn, pn] = k.split('|'), subs = AssetLib.subsOf(bn, pn); if (!subs.length) continue;
      const meshes = subs.map((s, i) => {
        const B = AssetLib.bundle(bn), part = B.parts.find((q) => q.name === pn), sub = part.subs[i];
        const mesh = new THREE.InstancedMesh(s.geometry, floraMaterial(bn, sub.mat, sub), cap);
        mesh.count = 0; mesh.frustumCulled = false; mesh.castShadow = false; mesh.receiveShadow = true; mesh.layers.set(1);
        mesh.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(cap * 3), 3); scene.add(mesh); return mesh;
      });
      F.slots.set(k, { meshes, n: 0, cap, tris: AssetLib.bundle(bn).parts.find((q) => q.name === pn).subs.reduce((a, s) => a + s.tris, 0) });
    }
    for (const it of F.inst) { it.s0 = F.slots.get(it.d.bundle + '|' + it.part); it.s1 = it.d.lod1 ? F.slots.get(it.d.bundle + '|' + it.part + '_lod1') : null; it.s2 = it.d.lod2 ? F.slots.get(it.d.bundle + '|' + it.part + '_lod2') : null; }
    F.ready = true; F.timer = 99;
  };

  F.setQuality = function (q) { F.scale = [0.55, 0.8, 1.0, 1.3][q] || 1; F.timer = 99; };

  F.enabled = true;
  F.setEnabled = function (on) { F.enabled = !!on; if (!on) for (const s of F.slots.values()) for (const m of s.meshes) { m.visible = false; m.count = 0; } else F.timer = 99; };
  F.update = function (dt, camera) {
    if (!F.ready || !F.enabled) return;
    F.timer += dt; const cx = camera.position.x, cz = camera.position.z;
    const fw = F._fw || (F._fw = new THREE.Vector3()); camera.getWorldDirection(fw); let fx = fw.x, fz = fw.z; const fl = Math.hypot(fx, fz) || 1; fx /= fl; fz /= fl;
    const turned = F.lastDir ? (fx * F.lastDir[0] + fz * F.lastDir[1] < 0.94) : true;           // 시야 방향이 약 20° 이상 바뀌면 갱신
    if (F.timer < 0.45 && !turned && Math.hypot(cx - F.last[0], cz - F.last[1]) < 3) return;
    if (F.timer < 0.12) return;                                                                   // 과도한 연속 갱신 방지
    F.timer = 0; F.last[0] = cx; F.last[1] = cz; F.lastDir = [fx, fz];
    for (const s of F.slots.values()) s.n = 0;
    const sc = F.scale, r1 = 75 * sc, r1s = r1 * r1, cand = F.cand || (F.cand = []); cand.length = 0;
    const halfH = Math.atan(Math.tan(camera.fov * Math.PI / 360) * camera.aspect) + 0.5, COSV = Math.cos(Math.min(halfH, 2.6)), nearS = 64;
    for (const it of F.inst) {
      const dx = it.x - cx, dz = it.z - cz, d2 = dx * dx + dz * dz;
      if (d2 >= r1s * (it.d.hab === 'water_lily' ? 1.6 : 1)) continue;
      if (d2 > nearS) { const dl = Math.sqrt(d2); if ((dx * fx + dz * fz) / dl < COSV) continue; }     // 시야 원뿔 밖(뒤쪽 포함)은 제외, 8m 이내는 항상 포함
      it.d2 = d2; cand.push(it);
    }
    cand.sort((a, b) => a.d2 - b.d2);
    let b0 = F.budget0 * sc, b1 = F.budget1 * sc, b2 = F.budget2 * sc;
    const R0 = 9 * sc, R1 = 30 * sc, R0s = R0 * R0, R1s = R1 * R1, R2s = (52 * sc) * (52 * sc);
    const take = (slot, which) => { if (!slot || slot.n >= slot.cap) return null; const c = slot.tris; if (which === 0) { if (b0 < c) return null; b0 -= c; } else if (which === 1) { if (b1 < c) return null; b1 -= c; } else { if (b2 < c) return null; b2 -= c; } return slot; };
    for (const it of cand) {
      let slot = null; const d2 = it.d2;
      if (!it.s1 && !it.s2) { if (d2 < R2s * 0.6) slot = take(it.s0, d2 < R0s ? 0 : 1); }
      else if (d2 < R0s) slot = take(it.s0, 0) || take(it.s1, 1) || take(it.s2, 2);
      else if (d2 < R1s) slot = take(it.s1, 1) || take(it.s2, 2);
      else if (d2 < R2s) slot = take(it.s2, 2) || (it.s2 ? null : take(it.s1, 1));
      if (!slot) continue;
      const i = slot.n++;
      for (const mesh of slot.meshes) {
        mesh.instanceMatrix.array.set(it.m, i * 16);
        const ca = mesh.instanceColor.array, lk = slot === it.s2 ? 0.72 : 1; ca[i * 3] = it.tint * lk; ca[i * 3 + 1] = it.tint2 * lk; ca[i * 3 + 2] = it.tint * lk;
      }
    }
    for (const s of F.slots.values()) for (const mesh of s.meshes) { mesh.count = s.n; mesh.instanceMatrix.needsUpdate = true; mesh.instanceColor.needsUpdate = true; mesh.visible = s.n > 0; }
  };
  F.budget0 = 260000; F.budget1 = 320000; F.budget2 = 420000;
  return F;
})();
