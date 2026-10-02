/* =====================================================================
   10b_fishing.js — 낚시: R 낚싯대 꺼내기/넣기, 클릭 = 던지기 / 입질에 챔질 / 줄 감기
   호수(와 강)의 물이 충분히 깊은 곳에 던지면 근처 호수 물고기가 찌로 모여들고, 입질 후 챔질하면 잡는다.
   ===================================================================== */
const Fishing = (function () {
  const F = { equipped: false, state: 'stowed', ready: false, caught: { trout: 0, carp: 0, minnow: 0 }, enabled: true };
  const R = mulberry32(4242), rr = (a, b) => a + (b - a) * R();
  let scene, cam, rod, tipObj, bobber, line, lineGeo, rippleMat, card, msg, hint, held = null;
  const ripples = [], V = new THREE.Vector3(), V2 = new THREE.Vector3(), tipW = new THREE.Vector3(), bobW = new THREE.Vector3(), fw = new THREE.Vector3();
  const S = { t: 0, timer: 0, biteT: 0, target: [0, 0], start: new THREE.Vector3(), fish: null, species: null, cm: 0, reelT: 0, reelTot: 2, hasFish: false, msgT: 0, tick: 0, rippleT: 0, cardT: 0, endPos: new THREE.Vector3() };
  const INFO = { trout: { ko: '송어', cm: 35 }, carp: { ko: '잉어', cm: 48 }, minnow: { ko: '피라미', cm: 8 } };
  try { const sv = JSON.parse(localStorage.getItem('riverside_forest_fish') || 'null'); if (sv) Object.assign(F.caught, sv); } catch (e) { }
  const save = () => { try { localStorage.setItem('riverside_forest_fish', JSON.stringify(F.caught)); } catch (e) { } };
  const hudOn = () => { const h = document.getElementById('hud'); return h && h.style.display !== 'none'; };

  /* ---------- 소리 (Web Audio 합성) ---------- */
  function burst(freq, dur, gain, q) {
    const c = Sound.ctx; if (!c || !Sound.noiseBuf || !Sound.master) return;
    const s = c.createBufferSource(); s.buffer = Sound.noiseBuf; const f = c.createBiquadFilter(); f.type = 'bandpass'; f.frequency.value = freq; f.Q.value = q || 0.8;
    const g = c.createGain(), t = c.currentTime; g.gain.setValueAtTime(gain, t); g.gain.exponentialRampToValueAtTime(0.001, t + dur);
    s.connect(f); f.connect(g); g.connect(Sound.master); s.start(t, Math.random() * 2); s.stop(t + dur + 0.05);
  }
  function tone(f0, f1, dur, gain, type) {
    const c = Sound.ctx; if (!c || !Sound.master) return;
    const o = c.createOscillator(), g = c.createGain(), t = c.currentTime; o.type = type || 'sine'; o.frequency.setValueAtTime(f0, t); o.frequency.exponentialRampToValueAtTime(Math.max(20, f1), t + dur);
    g.gain.setValueAtTime(gain, t); g.gain.exponentialRampToValueAtTime(0.001, t + dur); o.connect(g); g.connect(Sound.master); o.start(t); o.stop(t + dur + 0.02);
  }
  const sfx = {
    cast() { burst(1800, 0.35, 0.10, 0.6); },
    splash() { burst(700, 0.45, 0.28, 0.5); burst(2400, 0.25, 0.10, 1.0); },
    plop() { tone(520, 180, 0.12, 0.18); burst(900, 0.10, 0.10, 1.2); },
    tick() { burst(3200, 0.03, 0.06, 4); },
    catchOk() { tone(523, 523, 0.14, 0.12, 'triangle'); setTimeout(() => tone(784, 784, 0.22, 0.12, 'triangle'), 130); },
    miss() { tone(300, 140, 0.35, 0.10, 'sawtooth'); }
  };

  /* ---------- 모델 ---------- */
  function build() {
    const wood = new THREE.MeshStandardMaterial({ color: 0x5a3b22, roughness: 0.7 }), blank = new THREE.MeshStandardMaterial({ color: 0x1d1d1d, roughness: 0.4, metalness: 0.2 });
    const iron = new THREE.MeshStandardMaterial({ color: 0x3a3a3c, roughness: 0.45, metalness: 0.8 }), cork = new THREE.MeshStandardMaterial({ color: 0xb08a55, roughness: 0.9 });
    rod = new THREE.Group(); const body = new THREE.Group(); rod.add(body);
    const bg = new THREE.CylinderGeometry(0.0022, 0.0075, 1.9, 8); bg.translate(0, 0.95, 0); body.add(new THREE.Mesh(bg, blank));
    const hg = new THREE.CylinderGeometry(0.017, 0.015, 0.24, 10); hg.translate(0, -0.1, 0); body.add(new THREE.Mesh(hg, cork));
    const rg = new THREE.CylinderGeometry(0.03, 0.03, 0.03, 16); rg.rotateZ(Math.PI / 2); const reel = new THREE.Mesh(rg, iron); reel.position.set(0.04, 0.06, 0); body.add(reel);
    const hd = new THREE.CylinderGeometry(0.004, 0.004, 0.07, 6); hd.rotateX(Math.PI / 2); const crank = new THREE.Mesh(hd, iron); crank.position.set(0.07, 0.06, 0.03); body.add(crank);
    for (let i = 1; i <= 5; i++) { const g = new THREE.TorusGeometry(0.008 - i * 0.0007, 0.0007, 4, 10); const r = new THREE.Mesh(g, iron); r.position.set(0, 0.28 + i * 0.33, 0); r.rotation.x = Math.PI / 2; body.add(r); }
    tipObj = new THREE.Object3D(); tipObj.position.set(0, 1.9, 0); body.add(tipObj);
    body.rotation.set(-1.2, -0.10, -0.05); rod.userData.body = body; rod.position.set(0.30, -0.30, -0.5); rod.visible = false;
    rod.traverse((o) => { if (o.isMesh) { o.castShadow = false; o.frustumCulled = false; } });
    cam.add(rod);
    // 찌
    bobber = new THREE.Group();
    const red = new THREE.Mesh(new THREE.SphereGeometry(0.034, 14, 10), new THREE.MeshStandardMaterial({ color: 0xd8322a, roughness: 0.4 })); red.scale.set(1, 1.25, 1); red.position.y = 0.02; bobber.add(red);
    const wh = new THREE.Mesh(new THREE.CylinderGeometry(0.007, 0.007, 0.11, 8), new THREE.MeshStandardMaterial({ color: 0xf2efe6, roughness: 0.5 })); wh.position.y = 0.1; bobber.add(wh);
    const tp = new THREE.Mesh(new THREE.CylinderGeometry(0.0075, 0.0075, 0.03, 8), new THREE.MeshStandardMaterial({ color: 0xd8322a, roughness: 0.5 })); tp.position.y = 0.17; bobber.add(tp);
    bobber.visible = false; scene.add(bobber);
    // 줄
    const N = 18; lineGeo = new THREE.BufferGeometry(); lineGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(N * 3), 3));
    line = new THREE.Line(lineGeo, new THREE.LineBasicMaterial({ color: 0xeeeeee, transparent: true, opacity: 0.7, fog: false })); line.frustumCulled = false; line.visible = false; scene.add(line);
    // 물결 고리
    rippleMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.0, depthWrite: false, side: THREE.DoubleSide, fog: false });
    for (let i = 0; i < 5; i++) { const m = new THREE.Mesh(new THREE.RingGeometry(0.15, 0.2, 40), rippleMat.clone()); m.rotation.x = -Math.PI / 2; m.visible = false; m.renderOrder = 6; scene.add(m); ripples.push({ m, age: 9, life: 1.2, size: 1 }); }
    // UI
    const css = 'position:fixed;left:50%;transform:translateX(-50%);color:#f3efe6;z-index:8;pointer-events:none;display:none;text-align:center;font-family:inherit;';
    msg = document.createElement('div'); msg.style.cssText = css + 'bottom:26%;padding:8px 18px;border-radius:10px;background:rgba(18,24,20,.72);border:1px solid rgba(255,255,255,.18);font-size:16px'; document.body.appendChild(msg);
    hint = document.createElement('div'); hint.style.cssText = css + 'bottom:11%;padding:5px 12px;border-radius:8px;background:rgba(18,24,20,.55);font-size:13px;color:#d6d0c0'; document.body.appendChild(hint);
    card = document.createElement('div'); card.style.cssText = css + 'top:16%;padding:16px 28px;border-radius:16px;background:rgba(18,24,20,.82);border:1px solid rgba(232,201,138,.5);box-shadow:0 12px 40px rgba(0,0,0,.5);min-width:240px'; document.body.appendChild(card);
  }

  function ripple(x, z, size, life) {
    let r = ripples.find((q) => q.age >= q.life) || ripples[0];
    r.age = 0; r.life = life || 1.3; r.size = size || 1; r.m.position.set(x, WATER_Y + 0.012, z); r.m.visible = true;
  }
  const say = (txt, t) => { msg.textContent = txt; msg.style.display = 'block'; S.msgT = t === undefined ? 2.2 : t; };
  const nobody = () => { S.fish = null; };

  /* ---------- 동작 ---------- */
  function aimTarget() {
    cam.getWorldDirection(fw); const cx = cam.position.x, cz = cam.position.z, hl = Math.hypot(fw.x, fw.z) || 1;
    let d = 11;
    if (fw.y < -0.04) { const t = (WATER_Y - cam.position.y) / fw.y; d = t * hl; }
    d = clamp(d, 5, 17); return [cx + fw.x / hl * d, cz + fw.z / hl * d];
  }
  function cast() {
    const tg = aimTarget(), depth = -terrainH(tg[0], tg[1]);
    if (depth < 0.45) { say('물이 너무 얕거나 물이 아니에요. 더 깊은 곳을 보고 던져 보세요.', 2.6); return; }
    S.target = tg; F.target = tg; tipObj.getWorldPosition(S.start); S.t = 0; S.state = 'casting'; F.state = 'casting'; bobber.visible = true; line.visible = true; sfx.cast();
    S.fish = Fauna && Fauna.nearestFish ? Fauna.nearestFish(tg[0], tg[1], 18) : null;
    say('', 0); msg.style.display = 'none';
  }
  function startBite() {
    F.state = 'bite'; S.biteT = 1.5; S.tick = 0; sfx.plop(); ripple(S.target[0], S.target[1], 1.2, 0.9); say('입질이다!  지금 클릭!', 1.6);
    if (!S.fish) { const r = R(); S.species = r < 0.5 ? 'trout' : (r < 0.8 ? 'carp' : 'minnow'); } else S.species = S.fish.species;
  }
  function startReel(withFish) {
    F.state = 'reel'; S.hasFish = withFish; S.reelT = 0;
    bobW.set(S.target[0], WATER_Y, S.target[1]); S.endPos.copy(cam.position); S.endPos.y = WATER_Y;
    const dist = Math.hypot(S.target[0] - cam.position.x, S.target[1] - cam.position.z); S.reelTot = clamp(dist / 2.4, 1.6, 6.5);
    if (withFish) say('감는 중… 물고기가 버티고 있다!', 3);
  }
  function finishReel() {
    nobody2(); bobber.visible = false; line.visible = false;
    if (S.hasFish) {
      const sp = S.species, info = INFO[sp], cm = Math.round(info.cm * rr(0.7, 1.35));
      if (S.fish && S.fish.hook) S.fish.hook();
      F.caught[sp] = (F.caught[sp] || 0) + 1; save(); sfx.catchOk(); showCatch(sp, cm);
    } else { F.state = 'ready'; say('아무것도 잡지 못했다.', 1.8); }
    S.fish = null;
  }
  function nobody2() { if (S.fish) S.fish.att = null; }
  function showCatch(sp, cm) {
    F.state = 'catch'; S.cardT = 3.8;
    const total = F.caught.trout + F.caught.carp + F.caught.minnow;
    card.innerHTML = '<div style="font-size:13px;color:#e8c98a;letter-spacing:.08em">낚았다!</div><div style="font-size:30px;font-weight:700;margin:4px 0">' + INFO[sp].ko + ' ' + cm + 'cm</div><div style="font-size:13px;color:#cfc9b8">잡은 물고기 ' + total + '마리 · 송어 ' + F.caught.trout + ' · 잉어 ' + F.caught.carp + ' · 피라미 ' + F.caught.minnow + '</div>';
    card.style.display = 'block';
    try {
      if (held) { cam.remove(held.root); held = null; }
      const m = AssetLib.build(sp); const k = sp === 'minnow' ? 3.2 : (sp === 'trout' ? 1.5 : 1.2);
      m.root.scale.setScalar(k); m.root.position.set(0.0, -0.1, -0.85); m.root.rotation.set(0, Math.PI / 2, 0.25); cam.add(m.root); held = { root: m.root, parts: m.parts, t: 0 };
    } catch (e) { }
  }
  function action() {
    if (!F.equipped || !hudOn()) return;
    if (F.state === 'ready') cast();
    else if (F.state === 'wait') { nobody2(); startReel(false); }
    else if (F.state === 'bite') startReel(true);
  }
  function toggle() {
    if (!hudOn()) return;
    if (F.state === 'wait' || F.state === 'bite' || F.state === 'reel' || F.state === 'casting') { nobody2(); bobber.visible = false; line.visible = false; F.state = 'ready'; }
    F.equipped = !F.equipped; F.state = F.equipped ? 'ready' : 'stowed'; rod.visible = F.equipped;
    if (F.equipped) say('낚싯대를 꺼냈다.  클릭: 던지기 · R: 넣기', 2.4); else msg.style.display = 'none';
  }

  F.init = function (sc, camera) {
    scene = sc; cam = camera; if (!cam.parent) scene.add(cam);
    build();
    window.addEventListener('keydown', (e) => { if (e.code === 'KeyR' && !e.repeat) toggle(); if (e.code === 'KeyG') action(); });
    window.addEventListener('mousedown', (e) => { if (e.button === 0) action(); });
    F.ready = true;
  };
  F.setEnabled = function (on) { F.enabled = !!on; if (!on && F.equipped) toggle(); };

  F.update = function (dt, camera) {
    if (!F.ready) return;
    S.t += dt;
    const vis = F.equipped && hudOn(); rod.visible = vis;
    // 물결 고리
    for (const r of ripples) { if (r.age < r.life) { r.age += dt; const u = r.age / r.life; r.m.scale.setScalar((0.25 + u * 4.5) * r.size); r.m.material.opacity = 0.55 * (1 - u) * (1 - u); if (r.age >= r.life) r.m.visible = false; } }
    // 메시지/카드 타이머
    if (S.msgT > 0) { S.msgT -= dt; if (S.msgT <= 0 && F.state !== 'bite') msg.style.display = 'none'; }
    if (S.cardT > 0) { S.cardT -= dt; if (S.cardT <= 0) { card.style.display = 'none'; if (held) { cam.remove(held.root); held = null; } if (F.state === 'catch') F.state = 'ready'; } }
    if (held) { held.t += dt; held.root.rotation.y = Math.PI / 2 + 0.25 * Math.sin(held.t * 1.5); held.root.rotation.z = 0.25 + 0.06 * Math.sin(held.t * 5); const tl = held.parts.tail; if (tl) tl.rotation.y = 0.5 * Math.sin(held.t * 12); }
    // 힌트
    const dl = Math.hypot(camera.position.x - LAKE.x, camera.position.z - LAKE.z);
    if (!F.equipped && dl < 34 && hudOn()) { hint.textContent = 'R  낚싯대 꺼내기'; hint.style.display = 'block'; }
    else if (F.equipped && hudOn() && (F.state === 'ready')) { hint.textContent = '클릭  던지기   ·   R  낚싯대 넣기'; hint.style.display = 'block'; }
    else if (F.equipped && hudOn() && F.state === 'wait') { hint.textContent = '찌를 지켜보세요…   (클릭: 줄 감기)'; hint.style.display = 'block'; }
    else hint.style.display = 'none';
    if (!F.equipped) return;
    // 낚싯대 흔들림
    const body = rod.userData.body; let swing = 0;
    tipObj.getWorldPosition(tipW);
    const st = F.state;
    if (st === 'casting') {
      S.t0 = (S.t0 === undefined || S.lastState !== 'casting') ? S.t : S.t0; const u = clamp((S.t - S.t0) / 0.75, 0, 1);
      S.start.copy(tipW); bobW.set(lerp(S.start.x, S.target[0], u), lerp(S.start.y, WATER_Y, u) + Math.sin(Math.PI * u) * 3.2, lerp(S.start.z, S.target[1], u));
      swing = u < 0.25 ? -(u / 0.25) * 0.5 : -0.5 + ((u - 0.25) / 0.75) * 0.75;
      if (u >= 1) { F.state = 'wait'; S.timer = rr(3.5, 8.5); S.fish && (S.fish.att = { x: S.target[0], z: S.target[1], age: 0 }); sfx.splash(); ripple(S.target[0], S.target[1], 1.8, 1.6); bobW.set(S.target[0], WATER_Y, S.target[1]); S.rippleT = 0; }
    } else if (st === 'wait') {
      S.timer -= dt; const near = S.fish ? Math.hypot(S.fish.x - S.target[0], S.fish.z - S.target[1]) : 99;
      const nib = near < 2.2 ? 1 : 0; S.rippleT -= dt;
      bobW.y = WATER_Y + 0.012 * Math.sin(S.t * 2.3) - nib * 0.02 * Math.max(0, Math.sin(S.t * 9)) * (Math.sin(S.t * 0.8) > 0.4 ? 1 : 0);
      if (S.rippleT <= 0) { S.rippleT = nib ? rr(0.9, 1.6) : rr(3, 5); ripple(S.target[0], S.target[1], nib ? 0.8 : 0.5, 1.4); }
      swing = 0.02 * Math.sin(S.t * 1.6);
      if (S.timer <= 0 && (!S.fish || near < 1.4 || S.timer < -9)) startBite();
      if (Math.hypot(camera.position.x - S.target[0], camera.position.z - S.target[1]) > 28) { nobody2(); F.state = 'ready'; bobber.visible = false; line.visible = false; say('줄이 너무 멀어져 감았다.', 2); }
    } else if (st === 'bite') {
      S.biteT -= dt; S.rippleT -= dt; bobW.y = WATER_Y - 0.05 - 0.025 * Math.abs(Math.sin(S.t * 22));
      if (S.rippleT <= 0) { S.rippleT = 0.3; ripple(S.target[0], S.target[1], 1.0, 0.8); }
      swing = 0.05 * Math.sin(S.t * 24);
      if (S.biteT <= 0) { nobody2(); if (S.fish) { S.fish.att = null; } F.state = 'ready'; bobber.visible = false; line.visible = false; say('놓쳤다… 물고기가 달아났다.', 2.2); sfx.miss(); }
    } else if (st === 'reel') {
      S.reelT += dt; const u = clamp(S.reelT / S.reelTot, 0, 1);
      const px = lerp(S.target[0], camera.position.x, u * 0.93), pz = lerp(S.target[1], camera.position.z, u * 0.93);
      const th = Math.max(WATER_Y, terrainH(px, pz));
      const jit = S.hasFish ? 0.35 * (1 - u) : 0;
      bobW.set(px + Math.sin(S.t * 13) * jit, th + 0.015 + (th > WATER_Y + 0.05 ? 0.02 : 0), pz + Math.cos(S.t * 11) * jit);
      S.rippleT -= dt; if (S.rippleT <= 0 && th <= WATER_Y + 0.02) { S.rippleT = S.hasFish ? 0.22 : 0.4; ripple(bobW.x, bobW.z, S.hasFish ? 0.9 : 0.6, 0.8); }
      S.tick -= dt; if (S.tick <= 0) { S.tick = 0.11; sfx.tick(); }
      swing = S.hasFish ? 0.10 * Math.sin(S.t * 14) + 0.12 : 0.04 * Math.sin(S.t * 10);
      if (u >= 1) finishReel();
    }
    S.lastState = st;
    body.rotation.x = -1.2 + swing;
    // 찌/줄 갱신
    if (bobber.visible) {
      bobber.position.copy(bobW);
      V.copy(tipW); V2.copy(bobW); const n = lineGeo.attributes.position.count, dist = V.distanceTo(V2);
      const sag = (F.state === 'wait' || F.state === 'bite') ? Math.min(0.5, dist * 0.04) : (F.state === 'reel' ? 0.08 : 0.15);
      const arr = lineGeo.attributes.position.array;
      for (let i = 0; i < n; i++) { const u = i / (n - 1); arr[i * 3] = lerp(V.x, V2.x, u); arr[i * 3 + 1] = lerp(V.y, V2.y + 0.1, u) - 4 * u * (1 - u) * sag; arr[i * 3 + 2] = lerp(V.z, V2.z, u); }
      lineGeo.attributes.position.needsUpdate = true;
    }
  };
  return F;
})();
