/* =====================================================================
   10_cabin.js — Blender 로 만든 통나무 오두막(외관+실내 가구)으로 기존 House 를 교체
   문 여닫기(E), 실내 조명/벽난로 불꽃, 충돌 박스, 창가 화분, 앞마당 울타리
   ===================================================================== */
(function () {
  const oldInit = House.init;
  const INTERIOR_ONLY = /^(floor_planks|wainscot|plaster_wall|ceiling_planks|timber_beam|soot|charred_wood|hearth_stone|stone_fireplace|fire_embers)$/;

  House.init = function (scene) {
    if (!AssetLib.has('house_shell')) return oldInit.call(this, scene);
    this.cabin = true;
    const shell = AssetLib.build('house_shell'), meta = shell.meta || {};
    const zoneNames = ['house_int_living', 'house_int_kitchen', 'house_int_bedroom'].filter((n) => AssetLib.has(n));
    if (!zoneNames.length && AssetLib.has('house_interior')) zoneNames.push('house_interior');
    const zones = zoneNames.map((n) => AssetLib.build(n, { shadow: false }));
    const interRoot = new THREE.Group(); interRoot.name = 'interior'; this.group.add(shell.root); this.group.add(interRoot); this.interRoot = interRoot;
    for (const z of zones) interRoot.add(z.root);
    this.group.position.set(HOUSE.x, HOUSE.y, HOUSE.z); this.group.rotation.y = HOUSE.rot; scene.add(this.group);
    const interMeshes = []; zones.forEach((z) => interMeshes.push(...z.meshes));
    for (const m of shell.meshes) {
      const mat = m.material;
      if (INTERIOR_ONLY.test(mat.name)) mat.envMapIntensity = 0.22;
      if (/glass/i.test(mat.name)) { m.castShadow = false; m.renderOrder = 5; this.glass = mat; mat.emissive = new THREE.Color(1.0, 0.62, 0.25); mat.emissiveIntensity = 0; }
    }
    for (const m of interMeshes) { m.material.envMapIntensity = Math.min(m.material.envMapIntensity === undefined ? 1 : m.material.envMapIntensity, 0.3); m.castShadow = false; }
    // 구조 실내 마감에 PBR 텍스처 적용 (UV 1단위 = 1m 가정, 타일 크기만큼 반복)
    const SHELL_TEX = { floor_planks: ['pbr_wood_floor', 1.0, [0.78, 0.7, 0.62], 0.8, Math.PI / 2], plaster_wall: ['pbr_plaster', 1.0, [0.95, 0.93, 0.9], 0.45], wainscot: ['pbr_wood_pine', 0.6, [0.72, 0.62, 0.52], 0.7], ceiling_planks: ['pbr_wood_pine', 0.6, [0.62, 0.52, 0.42], 0.7], timber_beam: ['pbr_wood_dark', 0.6, [1, 1, 1], 0.8], stone_fireplace: ['pbr_stone_fireplace', 1.0, [1, 1, 1], 0.9], hearth_stone: ['pbr_stone_fireplace', 1.0, [1, 1, 1], 0.9] };
    for (const m of shell.meshes) {
      const sp = SHELL_TEX[m.material.name]; if (!sp || m.material._pbr) continue;
      const t = AssetLib.texture(sp[0]); if (!t || !t.set || !t.set.map) continue;
      const mat = m.material; mat._pbr = true;
      for (const k of ['map', 'normalMap', 'roughnessMap']) { const tx = t.set[k]; if (tx) { tx.repeat.set(1 / sp[1], 1 / sp[1]); if (sp[4]) { tx.center.set(0.5, 0.5); tx.rotation = sp[4]; } } }
      mat.map = t.set.map; mat.normalMap = t.set.normalMap; mat.roughnessMap = t.set.roughnessMap; mat.roughness = 1;
      mat.color.setRGB(sp[2][0], sp[2][1], sp[2][2]); if (mat.normalMap) mat.normalScale.set(sp[3], sp[3]); mat.needsUpdate = true;
    }
    this.inter = { emissiveIntensity: 0 };
    const zparts = {}; zones.forEach((z) => Object.assign(zparts, z.parts));
    this.parts = Object.assign({}, shell.parts, zparts);
    // 충돌 박스 (하우스 로컬 → 월드 회전 박스)
    for (const c of (meta.colliders || [])) this.addBox(c.cx, c.cz, c.hx, c.hz, c.top, c.bottom);
    const im = { colliders: [], lights: [], interactables: [] };
    zones.forEach((z) => { const zm = z.meta || {}; for (const k in im) im[k].push(...(zm[k] || [])); });
    for (const c of im.colliders) this.addBox(c.cx, c.cz, c.hx, c.hz, c.top === undefined ? 1.0 : c.top, c.bottom === undefined ? 0.3 : c.bottom);
    // 흔들리는 부품(커튼/추)
    this.sway = [];
    for (const k in zparts) if (/^curtain_/.test(k)) this.sway.push({ part: zparts[k], kind: 'curtain', ph: Math.random() * 6 }); else if (k === 'clock_pendulum') this.sway.push({ part: zparts[k], kind: 'pendulum', ph: 0 });
    // 문
    this.doors = [];
    for (const d of (meta.doors || [])) {
      const part = this.parts[d.name]; if (!part) continue;
      const gap = d.name === 'door_front' ? { cx: 0, cz: 3.5, hx: 0.5, hz: 0.12 } : { cx: 1.525, cz: 0.4, hx: 0.1, hz: 0.47 };
      const w = this.toWorld(gap.cx, gap.cz);
      Colliders.addBox(w[0], w[1], gap.hx, gap.hz, HOUSE.rot + (d.name === 'door_front' ? 0 : 0), HOUSE.y + 2.4, HOUSE.y + 0.3);
      const box = Colliders.boxes[Colliders.boxes.length - 1];
      const ip = this.toWorld(d.interactPos[0], d.interactPos[1]);
      this.doors.push({ name: d.name, part, open: 0, target: 0, angle: d.openAngle, box, ix: ip[0], iz: ip[1] });
    }
    // 창 덧문은 열린 상태 그대로 둔다. 실내 조명
    this.lights = []; this.fire = null;
    const addLight = (pos, color, inten, dist, kind) => {
      const l = new THREE.PointLight(new THREE.Color(color[0], color[1], color[2]), 0, dist, 2);
      l.position.set(pos[0], pos[1], pos[2]); this.group.add(l); this.lights.push({ l, base: inten, kind });
      return l;
    };
    const fp = (meta.fireEmbers && meta.fireEmbers.pos) || [-4.1, 0.5, 0];
    this.fire = addLight([fp[0] + 0.5, fp[1] + 0.35, fp[2]], [1.0, 0.52, 0.2], 3.2, 11, 'fire');
    const pool = (im.lights || []).filter((q) => q.pos), chosen = [];
    while (chosen.length < 4 && pool.length) {            // 서로 멀리 떨어진 조명 위주로 선택(점광원 수 제한)
      let best = 0, bd = -1;
      pool.forEach((q, i) => { let d = 1e9; for (const o of chosen) d = Math.min(d, Math.hypot(q.pos[0] - o.pos[0], q.pos[2] - o.pos[2])); if (!chosen.length) d = -Math.hypot(q.pos[0] + 1, q.pos[2]); if (d > bd) { bd = d; best = i; } });
      chosen.push(pool.splice(best, 1)[0]);
    }
    for (const q of chosen) addLight(q.pos, q.color || [1, 0.78, 0.45], Math.min(q.intensity || 1.4, 2.2) * 0.9, Math.min(q.distance || 6.5, 8), 'lamp');
    // 벽난로 불씨 재질(깜빡임)
    this.embers = null;
    for (const m of shell.meshes) if (/ember/i.test(m.material.name)) this.embers = m.material;
    for (const m of interMeshes) if (/flame/i.test(m.material.name)) { (this.flames = this.flames || []).push(m.material); }
    this.night = 0; this.indoor = 0; this.t = 0;
    // 앞마당 울타리 + 우물/부두
    this.buildFence(scene);
    // 창가 화분
    if (AssetLib.has('flower_box')) {
      for (const sx of [-2.9, 2.9]) {
        const fb = AssetLib.build('flower_box', { only: ['flower_box_' + (sx < 0 ? 'a' : 'b')] });
        const part = fb.root.children[0]; if (part) { fb.root.position.set(sx, 1.43 - 0.06, 3.5 + 0.2); fb.root.rotation.y = 0; this.group.add(fb.root); }
      }
    }
    if (AssetLib.has('flower_box')) {
      for (const [px, pz, v] of [[-1.65, 3.95, 'a'], [1.65, 3.95, 'b'], [-1.9, 5.45, 'b']]) {
        const fp = AssetLib.build('flower_box', { only: ['flower_pot_' + v] }); fp.root.position.set(px, 0.52, pz); fp.root.rotation.y = px * 1.3; this.group.add(fp.root);
      }
    }
    const sp = this.toWorld(0, 3.5 + 6.5); this.spawn = { x: sp[0], z: sp[1], yaw: -Math.PI / 2 };
    this.buildWell(scene); this.buildPier(scene);
    // 상호작용 안내
    const pr = document.createElement('div'); pr.id = 'prompt'; pr.style.cssText = 'position:fixed;left:50%;bottom:18%;transform:translateX(-50%);padding:8px 16px;border-radius:10px;background:rgba(18,24,20,.72);border:1px solid rgba(255,255,255,.18);color:#f3efe6;font-size:15px;display:none;z-index:8;pointer-events:none';
    document.body.appendChild(pr); this.promptEl = pr;
    window.addEventListener('keydown', (e) => { if (e.code === 'KeyE' && document.getElementById('hud').style.display !== 'none') this.interact(); });
    this.smokeLocal = [-4.8, 7.4];
  };

  House.buildFence = function (scene) {
    const dark = texMat(TexLib.planks(true), [0.55, 0.42, 0.34], 'fencewood'), wall = texMat(TexLib.planks(false), [1.0, 0.92, 0.85], 'fenceboard');
    const Md = new Merger(), Mw = new Merger();
    const fence = (x0, z0, x1, z1) => {
      const len = Math.hypot(x1 - x0, z1 - z0), n = Math.max(1, Math.round(len / 2.2)), ang = Math.atan2(-(z1 - z0), x1 - x0);
      for (let i = 0; i <= n; i++) { const t = i / n, x = lerp(x0, x1, t), z = lerp(z0, z1, t); Md.add(boxGeo(0.14, 1.15, 0.14, 1.1), M4(x, 0.5, z)); }
      const mx = (x0 + x1) / 2, mz = (z0 + z1) / 2;
      for (const y of [0.45, 0.85]) Md.add(boxGeo(len, 0.09, 0.05, 1.1), M4(mx, y, mz, 0, ang, 0));
      const cnt = Math.round(len / 0.32);
      for (let i = 0; i < cnt; i++) { const t = (i + 0.5) / cnt, x = lerp(x0, x1, t), z = lerp(z0, z1, t); Mw.add(boxGeo(0.09, 0.85 + (i % 3) * 0.02, 0.03, 1.1), M4(x, 0.44, z, 0, ang, 0)); }
      this.addBox(mx, mz, Math.abs(Math.cos(ang)) * len / 2 + 0.1, Math.abs(Math.sin(ang)) * len / 2 + 0.1, 1.1, -0.2);
    };
    const FZ = 11.5, FX = 8;
    fence(-FX, FZ, -1.6, FZ); fence(1.6, FZ, FX, FZ); fence(-FX, FZ, -FX, 1); fence(FX, FZ, FX, 1);
    for (const sx of [-1, 1]) Md.add(boxGeo(0.2, 1.4, 0.2, 1.1), M4(sx * 1.6, 0.6, FZ));
    for (const [M, m] of [[Md, dark], [Mw, wall]]) { const mesh = new THREE.Mesh(M.build(), m); mesh.castShadow = mesh.receiveShadow = true; this.group.add(mesh); }
  };

  House.interact = function () {
    const p = Player.pos; let best = null, bd = 2.6;
    for (const d of this.doors) { const k = Math.hypot(p.x - d.ix, p.z - d.iz); if (k < bd) { bd = k; best = d; } }
    if (best) { best.target = best.target ? 0 : 1; Sound.jump && Sound.step && Sound.step('wood', 1.5, 0); }
  };

  House.update = function (dt, camera) {
    if (!this.cabin) return;
    this.t += dt; const p = Player.pos;
    // 문 애니메이션
    let near = null, bd = 2.6;
    for (const d of this.doors) {
      d.open += (d.target - d.open) * Math.min(1, dt * 4.5); const ph = d.open * d.open * (3 - 2 * d.open);
      d.part.rotation.y = d.angle * ph; d.box.off = d.open > 0.35;
      const k = Math.hypot(p.x - d.ix, p.z - d.iz); if (k < bd) { bd = k; near = d; }
    }
    if (this.promptEl) { if (near && document.getElementById('hud').style.display !== 'none') { this.promptEl.style.display = 'block'; this.promptEl.textContent = 'E  ' + (near.target ? '문 닫기' : '문 열기'); } else this.promptEl.style.display = 'none'; }
    // 실내 여부 (집 로컬 좌표)
    const c = Math.cos(HOUSE.rot), s = Math.sin(HOUSE.rot), dx = p.x - HOUSE.x, dz = p.z - HOUSE.z, lx = c * dx - s * dz, lz = s * dx + c * dz;
    const inside = Math.abs(lx) < 4.3 && Math.abs(lz) < 3.3 && p.y < HOUSE.y + 1.5;
    this.indoor += ((inside ? 1 : 0) - this.indoor) * Math.min(1, dt * 3);
    const near2 = Math.hypot(dx, dz) < 40;
    if (this.interRoot) this.interRoot.visible = Math.hypot(dx, dz) < 48;
    const lamp = near2 ? Math.max(this.night, this.indoor * 0.55 + 0.12) : 0, fl = 0.85 + 0.15 * Math.sin(this.t * 11) * Math.sin(this.t * 7.3 + 1) + 0.06 * Math.sin(this.t * 23);
    for (const q of this.lights) q.l.intensity = near2 ? q.base * (q.kind === 'fire' ? fl * (0.75 + 0.25 * this.indoor + 0.5 * this.night) : lamp) : 0;
    if (this.sway) for (const s of this.sway) { if (s.kind === 'pendulum') s.part.rotation.z = 0.12 * Math.sin(this.t * 3.1); else s.part.rotation.z = 0.012 * Math.sin(this.t * 0.9 + s.ph) + 0.006 * Math.sin(this.t * 2.3 + s.ph * 2); }
    if (this.embers) { this.embers.emissiveIntensity = (1.4 + 0.5 * Math.sin(this.t * 3.1) + 0.3 * Math.sin(this.t * 9)) ; }
    if (this.flames) for (const m of this.flames) m.emissiveIntensity = (2.2 + 0.4 * Math.sin(this.t * 13)) * (0.25 + 0.75 * Math.max(lamp, 0.25));
  };

  House.setLamps = function (on) {
    this.lampsOn = !!on;
    for (const q of (this.lights || [])) q.l.visible = this.lampsOn;
  };

  House.setNight = function (t) {
    this.night = t;
    if (typeof Village !== 'undefined' && Village.setNight) Village.setNight(t);
    if (this.glass) { this.glass.opacity = 0.25 + 0.15 * t; this.glass.emissiveIntensity = 0.9 * t; }
  };
})();
