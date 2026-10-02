/* =====================================================================
   10c_minimap.js — 원형 미니맵: 지형/물/길/숲 음영 지도 + 집·호수·부두·동물·플레이어 방향
   M 켜기/끄기 · N 시점 고정/회전 · -/= 확대·축소
   ===================================================================== */
const Minimap = (function () {
  const M = { ready: false, visible: true, rotate: true, zoom: 1, enabled: true };
  const VIEW = [70, 110, 180, 330];          // 지도 지름(미터)
  const SIZE = 196;
  let base, cv, ctx, dpr = 1;
  try { const sv = JSON.parse(localStorage.getItem('riverside_forest_minimap') || 'null'); if (sv) { M.visible = sv.visible !== false; M.rotate = sv.rotate !== false; M.zoom = Math.min(3, Math.max(0, sv.zoom === undefined ? 1 : sv.zoom)); } } catch (e) { }
  const save = () => { try { localStorage.setItem('riverside_forest_minimap', JSON.stringify({ visible: M.visible, rotate: M.rotate, zoom: M.zoom })); } catch (e) { } };
  const hudOn = () => { const h = document.getElementById('hud'); return h && h.style.display !== 'none'; };

  function buildBase() {
    const N = TEX_N, H = World.height, K = World.mask;
    base = document.createElement('canvas'); base.width = N; base.height = N;
    const bc = base.getContext('2d'), img = bc.createImageData(N, N), d = img.data;
    const hAt = (i, j) => H[(Math.min(N - 1, Math.max(0, j)) * N + Math.min(N - 1, Math.max(0, i))) * 4];
    for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
      const h = hAt(i, j), k = (j * N + i) * 4;
      const gx = hAt(i + 1, j) - hAt(i - 1, j), gz = hAt(i, j + 1) - hAt(i, j - 1);
      const shade = Math.min(1.35, Math.max(0.6, 1 - (gx * 0.55 + gz * 0.55) * 0.5));        // 북서쪽 광원
      const path = K[k] / 255, bank = K[k + 1] / 255, forest = K[k + 3] / 255;
      let r, g, b;
      if (h < WATER_Y) { const t = Math.min(1, -h / 2.2); r = 70 - 40 * t; g = 135 - 55 * t; b = 175 - 40 * t; }
      else {
        r = 150 - 100 * forest; g = 178 - 70 * forest; b = 92 - 44 * forest;                 // 초원 → 숲
        const alt = Math.min(1, Math.max(0, (h - 40) / 90)); r += (128 - r) * alt; g += (126 - g) * alt; b += (118 - b) * alt;   // 고지대 바위
        const snow = Math.min(1, Math.max(0, (h - 200) / 80)); r += (240 - r) * snow; g += (242 - g) * snow; b += (246 - b) * snow;
        if (bank > 0.15) { const q = Math.min(1, bank * 1.3); r += (214 - r) * q; g += (196 - g) * q; b += (150 - b) * q; }
        if (path > 0.25) { const q = Math.min(1, path * 1.2); r += (200 - r) * q; g += (172 - g) * q; b += (120 - b) * q; }
        r *= shade; g *= shade; b *= shade;
      }
      d[k] = Math.min(255, r); d[k + 1] = Math.min(255, g); d[k + 2] = Math.min(255, b); d[k + 3] = 255;
    }
    bc.putImageData(img, 0, 0);
    // 정적 지물: 집, 부두
    const px = (x) => (x + HALF) * N / WORLD, s = N / WORLD;
    bc.save(); bc.translate(px(HOUSE.x), px(HOUSE.z)); bc.rotate(-HOUSE.rot);
    bc.fillStyle = '#8a4b2d'; bc.fillRect(-4.6 * s, -3.6 * s, 9.2 * s, 7.2 * s); bc.fillStyle = '#d8b48a'; bc.fillRect(-4.6 * s, -0.3 * s, 9.2 * s, 0.6 * s);
    bc.strokeStyle = '#3a2412'; bc.lineWidth = 0.6; bc.strokeRect(-4.6 * s, -3.6 * s, 9.2 * s, 7.2 * s); bc.restore();
    if (House.pier) { bc.fillStyle = '#7b5636'; bc.fillRect(px(House.pier.x0), px(House.pier.z) - 0.9 * s, (House.pier.x1 - House.pier.x0) * s, 1.8 * s); }
  }

  M.init = function () {
    if (typeof World === 'undefined' || !World.height) return;
    buildBase();
    dpr = Math.min(2, window.devicePixelRatio || 1);
    cv = document.createElement('canvas'); cv.width = SIZE * dpr; cv.height = SIZE * dpr;
    cv.style.cssText = 'position:fixed;top:14px;right:14px;width:' + SIZE + 'px;height:' + SIZE + 'px;border-radius:50%;z-index:7;pointer-events:none;display:none;box-shadow:0 6px 24px rgba(0,0,0,.55),0 0 0 3px rgba(243,239,230,.85),0 0 0 5px rgba(20,28,22,.7)';
    document.body.appendChild(cv); ctx = cv.getContext('2d'); ctx.scale(dpr, dpr);
    window.addEventListener('keydown', (e) => {
      if (!hudOn()) return;
      if (e.code === 'KeyM') { M.visible = !M.visible; save(); }
      else if (e.code === 'KeyN') { M.rotate = !M.rotate; save(); }
      else if (e.code === 'Minus' || e.code === 'NumpadSubtract') { M.zoom = Math.min(3, M.zoom + 1); save(); }
      else if (e.code === 'Equal' || e.code === 'NumpadAdd') { M.zoom = Math.max(0, M.zoom - 1); save(); }
    });
    M.ready = true;
  };
  M.setEnabled = function (on) { M.enabled = !!on; if (cv && !on) cv.style.display = 'none'; };

  function label(text, x, y) {
    ctx.font = '600 10.5px system-ui,"Noto Sans KR","Malgun Gothic",sans-serif'; ctx.textAlign = 'center'; ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(15,22,16,.85)'; ctx.strokeText(text, x, y); ctx.fillStyle = '#f3efe6'; ctx.fillText(text, x, y);
  }

  M.update = function (dt, camera) {
    if (!M.ready) return;
    const show = M.enabled && M.visible && hudOn();
    cv.style.display = show ? 'block' : 'none'; if (!show) return;
    const P = Player.pos, yaw = Player.yaw, a = M.rotate ? yaw : 0, mPerPx = VIEW[M.zoom] / SIZE, s = 1 / mPerPx, C = SIZE / 2, ppm = TEX_N / WORLD;
    ctx.clearRect(0, 0, SIZE, SIZE); ctx.save(); ctx.beginPath(); ctx.arc(C, C, C, 0, Math.PI * 2); ctx.clip();
    ctx.fillStyle = '#4c5f40'; ctx.fillRect(0, 0, SIZE, SIZE);
    ctx.save(); ctx.translate(C, C); ctx.rotate(a); ctx.scale(s / ppm, s / ppm); ctx.translate(-(P.x + HALF) * ppm, -(P.z + HALF) * ppm);
    ctx.imageSmoothingEnabled = true; ctx.drawImage(base, 0, 0); ctx.restore();
    // 월드 -> 미니맵 화면
    const ca = Math.cos(a), sa = Math.sin(a), toS = (x, z) => { const dx = (x - P.x) * s, dz = (z - P.z) * s; return [C + dx * ca - dz * sa, C + dx * sa + dz * ca]; };
    // 호수/집/부두 이름
    const lb = toS(LAKE.x, LAKE.z); if (Math.hypot(lb[0] - C, lb[1] - C) < C - 18) label('호수', lb[0], lb[1] + 4);
    const hb = toS(HOUSE.x, HOUSE.z); if (Math.hypot(hb[0] - C, hb[1] - C) < C - 18) label('오두막', hb[0], hb[1] - 9);
    if (House.pier) { const pb = toS((House.pier.x0 + House.pier.x1) / 2, House.pier.z); if (Math.hypot(pb[0] - C, pb[1] - C) < C - 18) label('부두', pb[0], pb[1] - 7); }
    // 동물 (가까운 것만)
    if (Fauna && Fauna.list && Fauna.enabled !== false) {
      const lim = (VIEW[M.zoom] / 2) * 0.98;
      for (const an of Fauna.list) {
        if (!an.g.visible || /trout|carp|minnow|dragonfly/.test(an.bundle)) continue;
        const dx = an.x - P.x, dz = an.z - P.z; if (dx * dx + dz * dz > lim * lim) continue;
        const q = toS(an.x, an.z), big = /deer|stag/.test(an.bundle);
        ctx.beginPath(); ctx.arc(q[0], q[1], big ? 3.2 : 2.2, 0, Math.PI * 2);
        ctx.fillStyle = big ? '#c97b3c' : (/fox/.test(an.bundle) ? '#e0541f' : (/duck|heron|hawk|songbird|kingfisher/.test(an.bundle) ? '#f1e6a8' : '#d8d2c2')); ctx.fill(); ctx.lineWidth = 1; ctx.strokeStyle = 'rgba(20,24,18,.8)'; ctx.stroke();
      }
    }
    // 마을: 이름 + 주민 점
    if (typeof Village !== 'undefined' && Village.ready && Village.enabled) {
      const vb = toS(VILLAGE.x + VILLAGE.c * 0, VILLAGE.z + VILLAGE.s * 0); if (Math.hypot(vb[0] - C, vb[1] - C) < C - 18) label('마을', vb[0], vb[1] - 4);
      const lim2 = (VIEW[M.zoom] / 2) * 0.98;
      for (const b of Village.buildings) { const dx = b.pos[0] - P.x, dz = b.pos[2] - P.z; if (dx * dx + dz * dz > lim2 * lim2) continue; const q = toS(b.pos[0], b.pos[2]); ctx.fillStyle = b.part === 'church' ? '#e8e0d0' : '#9a5a38'; ctx.fillRect(q[0] - 2.2, q[1] - 2.2, 4.4, 4.4); }
      for (const pe of Village.people) { if (pe.inside) continue; const dx = pe.x - P.x, dz = pe.z - P.z; if (dx * dx + dz * dz > lim2 * lim2) continue; const q = toS(pe.x, pe.z); ctx.beginPath(); ctx.arc(q[0], q[1], 1.8, 0, Math.PI * 2); ctx.fillStyle = '#6fb6ff'; ctx.fill(); }
    }
    // 낚시 찌
    if (Fishing && Fishing.state && (Fishing.state === 'wait' || Fishing.state === 'bite' || Fishing.state === 'reel') && Fishing.target) { const q = toS(Fishing.target[0], Fishing.target[1]); ctx.beginPath(); ctx.arc(q[0], q[1], 2.6, 0, Math.PI * 2); ctx.fillStyle = '#e03a2e'; ctx.fill(); }
    ctx.restore();
    // 북쪽 표시
    const nx = C + Math.sin(a) * (C - 11), ny = C - Math.cos(a) * (C - 11);
    ctx.font = '700 12px system-ui,sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(15,22,16,.9)'; ctx.strokeText('N', nx, ny); ctx.fillStyle = '#ff8d6a'; ctx.fillText('N', nx, ny); ctx.textBaseline = 'alphabetic';
    // 시야 부채꼴 + 플레이어 화살표
    const fov = (camera.fov || 70) * Math.PI / 180 * 0.5, hr = M.rotate ? 0 : -yaw;
    ctx.save(); ctx.translate(C, C); ctx.rotate(hr);
    const g = ctx.createRadialGradient(0, 0, 0, 0, 0, 52); g.addColorStop(0, 'rgba(255,255,255,.38)'); g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(0, 0); ctx.arc(0, 0, 52, -Math.PI / 2 - fov * 1.35, -Math.PI / 2 + fov * 1.35); ctx.closePath(); ctx.fill();
    ctx.beginPath(); ctx.moveTo(0, -8); ctx.lineTo(5.5, 6); ctx.lineTo(0, 3); ctx.lineTo(-5.5, 6); ctx.closePath(); ctx.fillStyle = '#ffffff'; ctx.fill(); ctx.lineWidth = 1.6; ctx.strokeStyle = '#1b2a22'; ctx.stroke(); ctx.restore();
    // 축척 막대 (20m)
    const bar = 20 * s; ctx.fillStyle = 'rgba(15,22,16,.7)'; ctx.fillRect(C - bar / 2 - 2, SIZE - 22, bar + 4, 12); ctx.fillStyle = '#f3efe6'; ctx.font = '600 9px system-ui,sans-serif'; ctx.textAlign = 'center'; ctx.fillText('20m', C, SIZE - 13);
    ctx.fillRect(C - bar / 2, SIZE - 11, bar, 1.5);
  };
  return M;
})();
