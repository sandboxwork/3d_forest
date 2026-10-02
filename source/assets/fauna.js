/* =====================================================================
   09_fauna.js — Blender 로 만든 야생동물/물고기: 사슴, 토끼, 여우, 다람쥐, 새, 오리, 왜가리, 매, 송어, 잉어, 개구리, 잠자리
   리지드 부품 애니메이션(피벗 회전). 지형/강/나무 충돌을 따라 배회하고 플레이어를 피한다.
   ===================================================================== */
const Fauna = (function () {
  const R = mulberry32(90210), rr = (a, b) => a + (b - a) * R(), D = Math.PI / 180, TAU2 = Math.PI * 2;
  const QI = new THREE.Quaternion(), _q = new THREE.Quaternion(), _q2 = new THREE.Quaternion(), _e = new THREE.Euler(), _zAx = new THREE.Vector3(0, 0, 1);
  const list = [], F = { list, scene: null, t: 0, ready: false };
  const fwdAng = (yaw) => [Math.sin(yaw), Math.cos(yaw)];
  const angDiff = (a, b) => { let d = (b - a) % TAU2; if (d > Math.PI) d -= TAU2; if (d < -Math.PI) d += TAU2; return d; };
  const turnTo = (yaw, target, rate, dt) => { const d = angDiff(yaw, target); return yaw + clamp(d, -rate * dt, rate * dt); };
  const slopeAt = (x, z) => { const e = 1.4; return Math.hypot(terrainH(x + e, z) - terrainH(x - e, z), terrainH(x, z + e) - terrainH(x, z - e)) / (2 * e); };
  const okLand = (x, z, m) => Math.abs(x) < HALF - 8 && Math.abs(z) < HALF - 8 && terrainH(x, z) > WATER_Y + (m === undefined ? 0.35 : m) && slopeAt(x, z) < 0.5 && !inHouseBox(x, z, 3) && !inVillage(x, z, 3);
  const _near = [];
  function blockedByTree(x, z, r) { Colliders.circlesNear(x, z, _near); for (const o of _near) if (Math.hypot(x - o.x, z - o.z) < o.r + r) return true; return false; }
  function pickLand(cx, cz, rad, tries) {
    for (let i = 0; i < (tries || 60); i++) {
      const a = R() * TAU2, d = Math.sqrt(R()) * rad, x = cx + Math.cos(a) * d, z = cz + Math.sin(a) * d;
      if (okLand(x, z) && !blockedByTree(x, z, 0.6)) return [x, z];
    }
    return null;
  }
  function depthOf(part) { let d = 0; while (part.parent && part.parent.userData && part.parent.userData.spec) { d++; part = part.parent; } return d; }
  function findLegs(p) {
    const L = {};
    for (const k in p) { const m = /^leg_([fh])([lr])_/.exec(k); if (m) { const id = m[1] + m[2]; (L[id] = L[id] || []).push(p[k]); } }
    for (const id in L) L[id].sort((a, b) => depthOf(a) - depthOf(b));
    return L;
  }
  function setRot(part, x, y, z) { if (part) part.rotation.set(x || 0, y || 0, z || 0); }
  const fmt = (o) => o;

  /* ---------- 공통 베이스 ---------- */
  class Animal {
    constructor(bundle, scale) {
      const b = AssetLib.build(bundle); this.bundle = bundle; this.b = b; this.p = b.parts; this.meta = b.meta;
      this.g = new THREE.Group(); this.g.add(b.root); if (scale) this.g.scale.setScalar(scale);
      this.x = 0; this.z = 0; this.y = 0; this.yaw = 0; this.t = R() * 50; this.state = 'idle'; this.timer = 0; this.far = false;
      this.g.rotation.order = 'YXZ'; this.g.userData.animal = this; F.scene.add(this.g); list.push(this);
      this.meshes = b.meshes; this.shadowCap = /^(deer|stag)$/.test(bundle); this._sh = false;
      for (const m of this.meshes) { m.layers.set(1); m.castShadow = false; }       // 반사 패스 제외, 그림자는 가까운 사슴만
    }
    setPos(x, z, yaw) { this.x = x; this.z = z; if (yaw !== undefined) this.yaw = yaw; this.syncGround(); }
    syncGround() { this.y = terrainH(this.x, this.z); this.g.position.set(this.x, this.y, this.z); this.g.rotation.y = this.yaw; }
    tilt(len) {
      const s = fwdAng(this.yaw), hf = terrainH(this.x + s[0] * len, this.z + s[1] * len), hb = terrainH(this.x - s[0] * len, this.z - s[1] * len);
      const hl = terrainH(this.x + s[1] * len * 0.5, this.z - s[0] * len * 0.5), hr = terrainH(this.x - s[1] * len * 0.5, this.z + s[0] * len * 0.5);
      const tp = -Math.atan2(hf - hb, 2 * len), tr = Math.atan2(hl - hr, len);
      this.g.rotation.x += (tp - this.g.rotation.x) * 0.25; this.g.rotation.z += (tr * 0.6 - this.g.rotation.z) * 0.25;
    }
    distTo(px, pz) { return Math.hypot(this.x - px, this.z - pz); }
    awayYaw(px, pz) { return Math.atan2(this.x - px, this.z - pz); }
  }

  /* ---------- 네발짐승: 사슴/수사슴/여우 ---------- */
  class Quad extends Animal {
    constructor(bundle, o) {
      super(bundle, o.scale); this.o = o; this.legs = findLegs(this.p); this.gz = 0; this.al = 0; this.phase = R();
      this.home = [0, 0]; this.home.radius = o.roam || 40; this.target = null; this.speed = 0; this.flee = false;
    }
    gait(ph, sp) {
      const A = lerp(12, 28, sp) * D, offs = { hl: 0, fl: 0.25, hr: 0.5, fr: 0.75 }, o = this.o;
      for (const id in this.legs) {
        const s = this.legs[id], c = ph + offs[id], sn = Math.sin(c * TAU2), lift = Math.max(0, -Math.cos(c * TAU2)) * sp;
        const fore = id[0] === 'f';
        if (s[0]) s[0].rotation.x = A * sn * (fore ? 1 : 0.9);
        if (s[1]) s[1].rotation.x = fore ? (o.flexF || 50) * D * lift : -(o.flexH || 55) * D * lift;
        if (s[2]) s[2].rotation.x = fore ? -0.35 * s[1].rotation.x : -0.35 * s[1].rotation.x;
      }
      const body = this.p.body; if (body) body.position.y = body.userData.rest.y + 0.012 * Math.sin(ph * TAU2 * 2) * sp;
      if (this.p.tail && o.tailSwish) this.p.tail.rotation.y = 0.25 * Math.sin(ph * TAU2);
    }
    pose(dt) {
      const o = this.o, p = this.p, k = Math.min(1, dt * 4);
      const gt = this.state === 'graze' ? 1 : 0, at = (this.state === 'look' || this.state === 'sniff') ? 1 : 0;
      this.gz += (gt - this.gz) * k; this.al += (at - this.al) * k;
      const gzN = o.grazeNeck === undefined ? 62 : o.grazeNeck, gzH = o.grazeHead === undefined ? 25 : o.grazeHead;
      if (p.neck) p.neck.rotation.x = (this.gz * gzN - this.al * 8 + 2 * Math.sin(this.t * 0.9)) * D;
      if (p.head) p.head.rotation.x = (this.gz * gzH - this.al * 5) * D + (p.neck ? 0 : this.gz * 0.5);
      if (p.head) p.head.rotation.y = this.al * 0.35 * Math.sin(this.t * 0.7) + (this.state === 'look' ? 0.25 * Math.sin(this.t * 1.6) : 0);
      if (p.jaw) p.jaw.rotation.x = this.gz * (2 + 6 * (0.5 + 0.5 * Math.sin(this.t * 9))) * D + (this.state === 'sniff' ? 0.05 * Math.sin(this.t * 25) : 0);
      const fl = (Math.sin(this.t * 1.3) > 0.97) ? 18 : 0, fr = (Math.sin(this.t * 1.1 + 2) > 0.97) ? 18 : 0;
      if (p.ear_l) p.ear_l.rotation.z = (fl + this.al * 20) * D * 1; if (p.ear_r) p.ear_r.rotation.z = -(fr + this.al * 20) * D;
      if (p.tail && !o.tailSwish) p.tail.rotation.x = 0.1 * Math.sin(this.t * 2.2) - 0.1;
    }
    update(dt, px, pz) {
      this.t += dt; this.timer -= dt; const o = this.o, d = this.distTo(px, pz);
      let want = 0, speed = 0;
      if (d < o.fleeDist && this.state !== 'flee') { this.state = 'flee'; this.timer = rr(4, 8); this.yawT = this.awayYaw(px, pz) + rr(-0.5, 0.5); }
      if (this.state === 'flee') {
        speed = o.run; want = 1; this.yawT = this.awayYaw(px, pz) + 0.4 * Math.sin(this.t * 0.7);
        if (this.timer < 0 && d > o.fleeDist * 2.2) { this.state = 'look'; this.timer = rr(3, 6); }
      } else if (this.state === 'walk') {
        speed = o.walk; want = 0.55;
        if (!this.target || Math.hypot(this.target[0] - this.x, this.target[1] - this.z) < 1.5 || this.timer < 0) { this.state = R() < 0.25 ? 'look' : 'graze'; this.timer = rr(6, 14); }
        else this.yawT = Math.atan2(this.target[0] - this.x, this.target[1] - this.z);
      } else {
        speed = 0; want = 0;
        if (d < o.alertDist && this.state === 'graze') { this.state = 'look'; this.timer = rr(3, 6); }
        if (this.state === 'look' && d < o.alertDist) this.yawT = Math.atan2(px - this.x, pz - this.z);
        if (this.timer < 0) {
          const home = this.home, t = pickLand(home[0], home[1], home.radius, 30);
          if (t && R() < 0.85) { this.target = t; this.state = 'walk'; this.timer = rr(10, 20); } else { this.state = R() < 0.6 ? 'graze' : 'look'; this.timer = rr(5, 12); }
        }
      }
      this.sp = this.sp || 0; this.sp += (speed - this.sp) * Math.min(1, dt * 3);
      if (this.yawT !== undefined && this.sp > 0.05) this.yaw = turnTo(this.yaw, this.yawT, this.state === 'flee' ? 2.6 : 1.4, dt);
      else if (this.yawT !== undefined && this.state === 'look') this.yaw = turnTo(this.yaw, this.yawT, 0.8, dt);
      if (this.sp > 0.02) {
        const s = fwdAng(this.yaw), nx = this.x + s[0] * this.sp * dt, nz = this.z + s[1] * this.sp * dt;
        if (okLand(nx, nz, 0.25) && !blockedByTree(nx, nz, 0.5)) { this.x = nx; this.z = nz; }
        else { this.yawT = this.yaw + (R() < 0.5 ? 1 : -1) * rr(1.2, 2.4); if (this.state === 'walk') this.target = pickLand(this.home[0], this.home[1], this.home.radius, 20); this.sp *= 0.5; }
      }
      this.phase += dt * this.sp / (o.stride || 1.3);
      this.gait(this.phase, clamp(this.sp / o.run, 0, 1));
      this.pose(dt); this.syncGround(); this.tilt(o.len || 0.7);
    }
  }

  /* ---------- 토끼/다람쥐: 깡충 ---------- */
  class Hopper extends Animal {
    constructor(bundle, o) { super(bundle, o.scale); this.o = o; this.legs = {}; this.h = 0; this.hopping = false; this.hopDir = 0; this.home = [0, 0]; this.nextHop = rr(1, 4); }
    update(dt, px, pz) {
      this.t += dt; const o = this.o, p = this.p, d = this.distTo(px, pz);
      if (this.hopping) {
        this.h += dt / (o.hopT);
        const s = fwdAng(this.yaw), v = o.hopDist / o.hopT * (this.fleeing ? 1.5 : 1);
        const nx = this.x + s[0] * v * dt, nz = this.z + s[1] * v * dt;
        if (okLand(nx, nz, 0.2) && !blockedByTree(nx, nz, 0.25)) { this.x = nx; this.z = nz; } else this.yaw += 1.4;
        if (this.h >= 1) { this.h = 0; this.nextHopCount--; if (this.nextHopCount <= 0) { this.hopping = false; this.fleeing = false; this.nextHop = rr(o.restMin, o.restMax); } }
      } else {
        this.nextHop -= dt;
        if (d < o.fleeDist && !this.fleeing) { this.fleeing = true; this.hopping = true; this.nextHopCount = 4 + (R() * 4 | 0); this.yaw = this.awayYaw(px, pz) + rr(-0.6, 0.6); this.h = 0; }
        else if (this.nextHop < 0) {
          this.hopping = true; this.nextHopCount = 1 + (R() * 3 | 0); this.h = 0;
          const tgt = Math.atan2(this.home[0] - this.x, this.home[1] - this.z), far = this.distTo(this.home[0], this.home[1]) > (o.roam || 14);
          this.yaw = far ? tgt + rr(-0.6, 0.6) : this.yaw + rr(-2.2, 2.2);
        }
      }
      if (this.fleeing && this.hopping && this.h < 0.02 && this.nextHopCount > 0) this.yaw = turnTo(this.yaw, this.awayYaw(px, pz), 1.2, 0.3);
      // 포즈
      const e = this.hopping ? Math.sin(Math.PI * this.h) : 0, arc = this.hopping ? 4 * this.h * (1 - this.h) : 0;
      const g = this.g; g.userData.lift = arc * o.arc;
      const pitch = this.hopping ? (this.h < 0.5 ? -0.35 * e : 0.45 * e) : 0;
      if (p.body) { p.body.rotation.x = pitch * 0.5; p.body.position.y = p.body.userData.rest.y + arc * o.arc; }
      for (const k in p) {
        const m = /^leg_h([lr])_(thigh|upper)$/.exec(k);
        if (m) p[k].rotation.x = -o.hindExt * D * e;
        else if (/^leg_h[lr]_lower$/.test(k)) p[k].rotation.x = o.hindLow * D * e;
        else if (/^leg_h[lr]_(foot)$/.test(k)) p[k].rotation.x = -40 * D * e;
        else if (/^leg_f[lr]_upper$/.test(k)) p[k].rotation.x = 22 * D * e;
        else if (/^leg_f[lr]_lower$/.test(k)) p[k].rotation.x = -18 * D * e;
      }
      if (p.ear_l) p.ear_l.rotation.z = (Math.sin(this.t * 0.9 + 1) > 0.96 ? 14 : 0) * D - 4 * D * e;
      if (p.ear_r) p.ear_r.rotation.z = -(Math.sin(this.t * 0.8) > 0.96 ? 14 : 0) * D + 4 * D * e;
      if (p.jaw) p.jaw.rotation.x = this.hopping ? 0 : (0.03 + 0.03 * Math.sin(this.t * 14)) * (Math.sin(this.t * 0.5) > 0 ? 1 : 0.2);
      if (p.tail && o.tailFlick) p.tail.rotation.x = 0.25 * Math.sin(this.t * 2.5) - 0.1;
      this.syncGround(); this.tilt(0.25);
    }
  }

  /* ---------- 날개 도우미 ---------- */
  function wingSet(a) {
    const p = a.p, m = a.meta, res = { segs: [], flapBase: [] };
    const mk = (side, seg, openQ) => ({ part: p['wing_' + side + '_' + seg], side, seg, open: openQ ? new THREE.Quaternion(...openQ) : null });
    const pose = m.wing_open_pose || m.wing_fold_pose;
    for (const side of ['l', 'r']) for (const seg of ['upper', 'fore', 'hand']) {
      const pp = pose && pose['wing_' + side] && pose['wing_' + side][seg];
      const key = m.wing_open_pose ? 'open_quat_xyzw_three' : 'fold_quat_xyzw_three';
      res.segs.push(mk(side, seg, pp ? pp[key] : null));
    }
    res.spreadRest = !m.wing_open_pose;      // hawk: identity == spread, pose gives FOLD
    return res;
  }
  function setWings(ws, open, flap) {
    for (const s of ws.segs) {
      if (!s.part) continue;
      const t = ws.spreadRest ? 1 - open : open;
      _q.identity(); if (s.open) _q.slerp(s.open, t);
      const lag = s.seg === 'upper' ? 1 : s.seg === 'fore' ? 0.7 : 0.45;
      const ang = flap * lag * (s.side === 'l' ? 1 : -1);
      _q2.setFromAxisAngle(_zAx, ang); s.part.quaternion.copy(_q2).multiply(_q);
    }
  }

  /* ---------- 작은 새: 지상 탐색 + 짧은 비행 ---------- */
  class Songbird extends Animal {
    constructor(bundle, o) { super(bundle, o.scale); this.o = o; this.ws = wingSet(this); this.mode = 'perch'; this.fl = 0; this.home = [0, 0]; this.pitch = 0; this.flyT = 0; setWings(this.ws, 0, 0); this.hopT = 0; this.restT = rr(1, 4); this.lift = 0; }
    update(dt, px, pz) {
      this.t += dt; const o = this.o, p = this.p, d = this.distTo(px, pz), s = fwdAng(this.yaw);
      if (this.mode === 'perch') {
        this.restT -= dt;
        if (d < o.fleeDist) this.startFly(pickLand(px + (this.x - px) * 6, pz + (this.z - pz) * 6, 18, 30) || pickLand(this.home[0], this.home[1], 40));
        else if (this.restT < 0) {
          if (R() < 0.12) this.startFly(pickLand(this.home[0], this.home[1], 35));
          else { this.hopT = 0.22; this.yaw += rr(-1.5, 1.5); this.restT = rr(0.8, 3.5); }
        }
        if (this.hopT > 0) { this.hopT -= dt; const s2 = fwdAng(this.yaw), nx = this.x + s2[0] * 0.25 * dt / 0.22, nz = this.z + s2[1] * 0.25 * dt / 0.22; if (okLand(nx, nz, 0.3)) { this.x = nx; this.z = nz; } this.lift = 0.03 * Math.sin(Math.PI * clamp(this.hopT / 0.22, 0, 1)); } else this.lift = 0;
        if (p.head) { p.head.rotation.y = 0.7 * Math.sin(this.t * 0.9) * (Math.sin(this.t * 0.37) > 0.3 ? 1 : 0.15); p.head.rotation.x = 0.3 * Math.max(0, Math.sin(this.t * 0.61)); }
        if (p.tail) p.tail.rotation.x = 0.12 * Math.sin(this.t * 3.1) * (Math.sin(this.t * 0.4) > 0.6 ? 1 : 0.2);
        setWings(this.ws, 0, 0); this.pitch *= 0.9;
        this.y = (this.perchY !== undefined ? this.perchY : terrainH(this.x, this.z)) + this.lift; this.g.position.set(this.x, this.y, this.z); this.g.rotation.set(this.pitch, this.yaw, 0);
      } else {
        this.fl += dt / this.flDur; const u = clamp(this.fl, 0, 1);
        this.x = lerp(this.x0, this.x1, u); this.z = lerp(this.z0, this.z1, u);
        const gy = lerp(this.y0, this.y1, u), hh = Math.sin(Math.PI * u) * this.arcH;
        this.y = Math.max(gy + hh, terrainH(this.x, this.z) + 0.05);
        const open = smoothstep(0, 0.12, u) * smoothstep(1, 0.88, u), flap = Math.sin(this.t * 34) * 0.85;
        setWings(this.ws, open, flap * open);
        this.pitch = -0.35 * Math.cos(Math.PI * u); this.g.position.set(this.x, this.y, this.z); this.g.rotation.set(this.pitch, this.yaw, 0.12 * Math.sin(this.t * 6));
        if (this.fl >= 1) { this.mode = 'perch'; this.restT = rr(2, 5); this.home = [this.x, this.z]; }
      }
    }
    startFly(tgt) {
      if (!tgt) { this.restT = 2; return; }
      this.mode = 'fly'; this.fl = 0; this.x0 = this.x; this.z0 = this.z; this.y0 = this.perchY !== undefined ? this.perchY : terrainH(this.x, this.z); this.perchY = undefined; this.x1 = tgt[0]; this.z1 = tgt[1]; this.y1 = terrainH(tgt[0], tgt[1]);
      const L = Math.hypot(this.x1 - this.x0, this.z1 - this.z0); this.flDur = Math.max(1.2, L / 7); this.arcH = Math.min(6, 1.5 + L * 0.12); this.yaw = Math.atan2(this.x1 - this.x0, this.z1 - this.z0);
    }
  }

  /* ---------- 하늘을 나는 새 (매, 작은 새 무리) ---------- */
  class Soarer extends Animal {
    constructor(bundle, o) {
      super(bundle, o.scale); this.o = o; this.ws = wingSet(this); this.cx = o.cx; this.cz = o.cz; this.rad = o.rad; this.alt = o.alt; this.ang = R() * TAU2; this.dir = o.dir || 1;
      this.phase = R() * 10; this.flapMode = o.flap; this.mode = 'soar';
    }
    update(dt) {
      this.t += dt; const o = this.o;
      this.ang += this.dir * dt * o.speed / this.rad;
      this.x = this.cx + Math.cos(this.ang) * this.rad * (1 + 0.15 * Math.sin(this.t * 0.11)); this.z = this.cz + Math.sin(this.ang) * this.rad;
      const alt = this.alt + (o.bob || 6) * Math.sin(this.t * 0.25 + this.phase);
      this.y = terrainH(this.x, this.z) * 0.3 + alt;
      const tx = -Math.sin(this.ang) * this.dir, tz = Math.cos(this.ang) * this.dir; this.yaw = Math.atan2(tx, tz);
      const flapOn = this.flapMode && Math.sin(this.t * 0.35 + this.phase) > 0.2;
      const fl = flapOn ? Math.sin(this.t * o.flapHz) * 0.7 : 0.08 * Math.sin(this.t * 0.8);
      setWings(this.ws, 1, fl);
      this.g.position.set(this.x, this.y, this.z); this.g.rotation.set(0.05 * Math.sin(this.t * 0.6) - (flapOn ? 0.08 : 0), this.yaw, -this.dir * 0.3 + 0.05 * Math.sin(this.t * 0.9));
      if (this.p.tail) this.p.tail.rotation.x = 0.1 * Math.sin(this.t * 0.7);
    }
  }

  /* ---------- 오리: 강 위를 떠다님 ---------- */
  class Duck extends Animal {
    constructor(o) { super('duck', o.scale); this.o = o; this.zs = o.z; this.off = o.off; this.dir = o.dir; this.leader = o.leader; this.ws = wingSet(this); setWings(this.ws, 0, 0); this.spd = 0.55; this.restT = 0; this.preen = 0; this.bobP = R() * 6; }
    update(dt, px, pz) {
      this.t += dt;
      const L = this.leader || this;
      if (!this.leader) {
        this.zs += this.dir * this.spd * dt * (0.6 + 0.4 * Math.sin(this.t * 0.15));
        if (this.zs > 170) this.dir = -1; else if (this.zs < -170) this.dir = 1;
        this.off += 0.02 * Math.sin(this.t * 0.2) * dt * 10; this.off = clamp(this.off, -0.55, 0.55);
      } else {
        const ox = this.fx, oz = this.fz; // 리더 뒤쪽 편대
        this.zs += (L.zs - this.dir * 1.2 * this.slot - this.zs) * dt * 0.6; this.dir = L.dir; this.off += (L.off + 0.2 * this.side - this.off) * dt * 0.4;
      }
      const zz = this.zs, hw = riverHalfW(zz), cx = riverX(zz) + this.off * hw * 0.9;
      const nx = cx, nz = zz, dx = nx - this.x, dz = nz - this.z;
      const tgtYaw = Math.atan2(riverDX(zz) * this.dir, this.dir);
      this.yaw = turnTo(this.yaw, tgtYaw, 1.2, dt); this.x = nx; this.z = nz;
      this.y = WATER_Y + 0.02 + 0.012 * Math.sin(this.t * 1.7 + this.bobP);
      const p = this.p; this.preen -= dt;
      if (p.head) p.head.rotation.x = 0.3 * Math.max(0, Math.sin(this.t * 0.23)) ;
      if (p.neck) p.neck.rotation.x = -0.05 + 0.4 * Math.max(0, Math.sin(this.t * 0.23 + 0.3));
      if (p.leg_l) { p.leg_l.rotation.x = 0.5 * Math.sin(this.t * 3); p.leg_r.rotation.x = -0.5 * Math.sin(this.t * 3); }
      this.g.position.set(this.x, this.y, this.z); this.g.rotation.set(0.02 * Math.sin(this.t * 1.3), this.yaw, 0.035 * Math.sin(this.t * 1.1 + this.bobP));
    }
  }

  /* ---------- 왜가리: 여울에 서서 사냥 ---------- */
  class Heron extends Animal {
    constructor(o) { super('heron', o.scale); this.o = o; this.ws = wingSet(this); setWings(this.ws, 0, 0); this.mode = 'stand'; this.s = 0; this.strike = 0; this.next = rr(6, 12); this.site = null; this.pickSite(); }
    pickSite() {
      for (let i = 0; i < 80; i++) {
        const z = rr(-150, 150), hw = riverHalfW(z), side = R() < 0.5 ? -1 : 1, x = riverX(z) + side * hw * rr(0.75, 1.05), h = terrainH(x, z);
        if (h < WATER_Y - 0.1 && h > WATER_Y - 0.45 && !inHouseBox(x, z, 6) && !inVillage(x, z, 6)) { this.setPos(x, z, Math.atan2(riverX(z) - x, 0) > 0 ? Math.PI / 2 : -Math.PI / 2); this.yaw = rr(0, TAU2); this.y = WATER_Y; return; }
      }
      this.setPos(riverX(0) + 6, 0, 0);
    }
    update(dt, px, pz) {
      this.t += dt; const d = this.distTo(px, pz), p = this.p;
      if (this.mode === 'stand') {
        this.next -= dt;
        if (d < 18) { this.mode = 'fly'; this.s = 0; this.x0 = this.x; this.z0 = this.z; this.ang = this.awayYaw(px, pz); }
        if (this.next < 0 && this.strike <= 0) { this.strike = 1.2; this.next = rr(6, 16); }
        if (this.strike > 0) this.strike -= dt;
        const k = this.strike > 0 ? Math.sin(Math.PI * clamp(1 - this.strike / 1.2, 0, 1)) : 0;
        if (p.neck_1) p.neck_1.rotation.x = -20 * D * k; if (p.neck_2) p.neck_2.rotation.x = 30 * D * k; if (p.neck_3) p.neck_3.rotation.x = -40 * D * k + 0.05 * Math.sin(this.t * 0.4);
        if (p.head) p.head.rotation.x = 10 * D * k; setWings(this.ws, 0, 0);
        this.y = WATER_Y - 0.12; this.g.position.set(this.x, this.y, this.z); this.g.rotation.set(0, this.yaw + 0.1 * Math.sin(this.t * 0.17), 0);
      } else {
        this.s += dt; const u = this.s;
        const sp = 3 + Math.min(u, 4) * 1.6, s = fwdAng(this.ang); this.x += s[0] * sp * dt; this.z += s[1] * sp * dt;
        this.y = Math.max(terrainH(this.x, this.z) + 1.5, this.y + 1.6 * dt * (u < 4 ? 1 : 0.2));
        setWings(this.ws, smoothstep(0, 0.8, u), Math.sin(this.t * 9) * 0.65);
        if (p.neck_1) p.neck_1.rotation.x = 0.4; if (p.neck_3) p.neck_3.rotation.x = -0.3;
        this.yaw = turnTo(this.yaw, this.ang, 2, dt); this.g.position.set(this.x, this.y, this.z); this.g.rotation.set(-0.15, this.yaw, 0.05 * Math.sin(this.t * 4.5));
        if (u > 14 || this.distTo(px, pz) > 140) { this.mode = 'stand'; if (p.neck_1) p.neck_1.rotation.x = 0; if (p.neck_3) p.neck_3.rotation.x = 0; this.pickSite(); this.next = rr(8, 14); }
      }
    }
  }

  /* ---------- 물고기 ---------- */
  class Fish extends Animal {
    constructor(bundle, o) {
      super(bundle, o.scale); this.o = o; this.zs = o.z; this.off = o.off; this.dir = R() < 0.5 ? 1 : -1; this.dep = o.dep; this.spd = o.spd; this.ph = R() * 10; this.leader = o.leader; this.tgtOff = this.off;
      this.len = this.meta.body_length_m || 0.3; this.sw = (this.meta.animation && this.meta.animation.tail_swing_deg || 28) * D; this.hz = (this.meta.animation && this.meta.animation.tail_hz || 2.5);
      this.fx = 0; this.fz = 0;
    }
    update(dt, px, pz) {
      this.t += dt;
      if (this.leader) { const L = this.leader; this.zs += (L.zs + this.ox - this.zs) * dt * 0.8; this.off += (L.off + this.oo - this.off) * dt * 0.8; this.dir = L.dir; this.dep += (L.dep + this.od - this.dep) * dt * 0.5; }
      else {
        this.zs += this.dir * this.spd * dt; this.off += (this.tgtOff - this.off) * dt * 0.3;
        if (R() < dt * 0.25) this.tgtOff = rr(-0.6, 0.6);
        if (R() < dt * 0.05) this.dir = -this.dir;
        if (this.zs > 175) this.dir = -1; else if (this.zs < -175) this.dir = 1;
        if (R() < dt * 0.2) this.dep = rr(0.25, 0.8);
        const dd = Math.hypot(this.x - px, this.z - pz); if (dd < 4) { this.zs += this.dir * this.spd * 3 * dt; }
      }
      const hw = riverHalfW(this.zs), nx = riverX(this.zs) + this.off * hw * 0.85, nz = this.zs;
      const floor = terrainH(nx, nz), maxD = WATER_Y - floor - 0.1;
      const tgtYaw = Math.atan2(riverDX(this.zs) * this.dir + (this.tgtOff - this.off) * 0.3, this.dir);
      this.yaw = turnTo(this.yaw, tgtYaw, 2.0, dt); this.x = nx; this.z = nz;
      this.y = WATER_Y - clamp(this.dep, 0.12, Math.max(0.12, maxD)) + 0.03 * Math.sin(this.t * 0.8 + this.ph);
      const ph = this.t * TAU2 * this.hz * (0.8 + this.spd) + this.ph, p = this.p;
      if (p.tail) p.tail.rotation.y = this.sw * Math.sin(ph);
      this.g.position.set(this.x, this.y, this.z); this.g.rotation.set(0, this.yaw + 0.12 * Math.sin(ph - 0.6), 0);
      for (const k in p) if (/fin_pectoral_l/.test(k)) p[k].rotation.z = 0.35 * Math.sin(ph * 0.5); else if (/fin_pectoral_r/.test(k)) p[k].rotation.z = -0.35 * Math.sin(ph * 0.5);
    }
  }

  /* ---------- 호수 물고기 / 오리 ---------- */
  const lakeFish = []; F.lakeFish = lakeFish;
  const lakeWP = (rf) => lakePt(rr(-rf, rf), rr(-rf, rf));
  class LakeFish extends Fish {
    constructor(bundle, o) {
      super(bundle, o); this.wp = lakePt(0, 0); this.gone = 0; this.att = null; this.species = bundle; this.dd = rr(0.35, 1.1);
      const p = lakeWP(0.7); this.x = p[0]; this.z = p[1]; this.pickWP(); lakeFish.push(this);
    }
    pickWP() { for (let i = 0; i < 20; i++) { const p = lakeWP(0.8); if (lakeT(p[0], p[1]) < 0.8) { this.wp = p; return; } } this.wp = lakePt(0, 0); }
    update(dt) {
      this.t += dt;
      if (this.gone > 0) { this.gone -= dt; this.g.visible = false; if (this.gone <= 0) { const p = lakeWP(0.6); this.x = p[0]; this.z = p[1]; this.pickWP(); } return; }
      let sp = this.spd * 0.7 + 0.15;
      if (this.att) { this.wp = [this.att.x + Math.sin(this.t * 1.7 + this.ph) * 0.5, this.att.z + Math.cos(this.t * 1.3 + this.ph) * 0.5]; sp = 1.1; this.att.age = (this.att.age || 0) + dt; }
      const dx = this.wp[0] - this.x, dz = this.wp[1] - this.z, d = Math.hypot(dx, dz);
      if (d < 1.0 && !this.att) this.pickWP();
      this.yaw = turnTo(this.yaw, Math.atan2(dx, dz), 2.2, dt);
      const s = fwdAng(this.yaw), nx = this.x + s[0] * sp * dt, nz = this.z + s[1] * sp * dt;
      if (lakeT(nx, nz) < 0.92) { this.x = nx; this.z = nz; } else { this.pickWP(); this.yaw += 1.5 * dt; }
      const depth = -terrainH(this.x, this.z);
      this.y = WATER_Y - clamp(this.dd, 0.18, Math.max(0.2, depth - 0.12)) + 0.02 * Math.sin(this.t * 0.9 + this.ph);
      const ph = this.t * TAU2 * this.hz * (0.6 + sp) + this.ph, p = this.p;
      if (p.tail) p.tail.rotation.y = this.sw * Math.sin(ph);
      this.g.position.set(this.x, this.y, this.z); this.g.rotation.set(0, this.yaw + 0.12 * Math.sin(ph - 0.6), 0);
      for (const k in p) if (/fin_pectoral_l/.test(k)) p[k].rotation.z = 0.35 * Math.sin(ph * 0.5); else if (/fin_pectoral_r/.test(k)) p[k].rotation.z = -0.35 * Math.sin(ph * 0.5);
    }
    hook() { this.gone = 28; this.att = null; }
  }
  class LakeDuck extends Duck {
    constructor(o) { super({ scale: 1, z: 0, off: 0, dir: 1 }); this.wp = lakePt(0, 0); const p = lakeWP(0.5); this.x = p[0]; this.z = p[1]; this.pick(); }
    pick() { for (let i = 0; i < 20; i++) { const p = lakeWP(0.7); if (lakeT(p[0], p[1]) < 0.7) { this.wp = p; return; } } }
    update(dt) {
      this.t += dt; const dx = this.wp[0] - this.x, dz = this.wp[1] - this.z, d = Math.hypot(dx, dz);
      if (d < 0.8) { this.pick(); }
      this.yaw = turnTo(this.yaw, Math.atan2(dx, dz), 0.9, dt); const s = fwdAng(this.yaw), sp = 0.45;
      const nx = this.x + s[0] * sp * dt, nz = this.z + s[1] * sp * dt; if (lakeT(nx, nz) < 0.85) { this.x = nx; this.z = nz; } else this.pick();
      this.y = WATER_Y + 0.02 + 0.012 * Math.sin(this.t * 1.7 + this.bobP); const p = this.p;
      if (p.neck) p.neck.rotation.x = -0.05 + 0.4 * Math.max(0, Math.sin(this.t * 0.23 + this.bobP));
      if (p.leg_l) { p.leg_l.rotation.x = 0.5 * Math.sin(this.t * 3); p.leg_r.rotation.x = -0.5 * Math.sin(this.t * 3); }
      this.g.position.set(this.x, this.y, this.z); this.g.rotation.set(0.02 * Math.sin(this.t * 1.3), this.yaw, 0.035 * Math.sin(this.t * 1.1 + this.bobP));
    }
  }
  F.nearestFish = function (x, z, r) {
    let best = null, bd = r;
    for (const f of lakeFish) { if (f.gone > 0 || f.species === 'minnow') continue; const d = Math.hypot(f.x - x, f.z - z); if (d < bd) { bd = d; best = f; } }
    return best;
  };
  F.fishTypes = { trout: { ko: '송어', cm: 35 }, carp: { ko: '잉어', cm: 48 }, minnow: { ko: '피라미', cm: 8 } };

  /* ---------- 개구리 ---------- */
  class Frog extends Animal {
    constructor(o) { super('frog', o.scale); this.o = o; this.hop = -1; this.wait = rr(3, 10); this.inWater = false; }
    update(dt, px, pz) {
      this.t += dt; const p = this.p, d = this.distTo(px, pz);
      if (this.hop < 0) {
        this.wait -= dt;
        if (d < 3.2 || this.wait < 0) {
          this.hop = 0; const riverC = riverX(this.z), toW = Math.atan2(riverC - this.x, 0);
          this.yaw = d < 3.2 ? (Math.atan2(riverC - this.x, (riverC - this.x) > 0 ? 0.001 : -0.001) + rr(-0.4, 0.4)) : this.yaw + rr(-1.5, 1.5);
          if (d < 3.2) this.yaw = Math.atan2(riverC - this.x, -(this.z - pz) * 0.1 + rr(-2, 2));
        }
        if (p.throat) p.throat.scale.set(1, 1 + 0.15 * (0.5 + 0.5 * Math.sin(this.t * 4.5)), 1 + 0.25 * (0.5 + 0.5 * Math.sin(this.t * 4.5)));
        this.lift = 0;
      } else {
        this.hop += dt / 0.5; const e = Math.sin(Math.PI * clamp(this.hop, 0, 1)), s = fwdAng(this.yaw), v = 0.5 / 0.5;
        const nx = this.x + s[0] * v * dt, nz = this.z + s[1] * v * dt;
        if (terrainH(nx, nz) > WATER_Y - 0.25 && Math.abs(nx) < HALF - 8) { this.x = nx; this.z = nz; }
        this.lift = 0.12 * 4 * clamp(this.hop, 0, 1) * (1 - clamp(this.hop, 0, 1));
        for (const k in p) { if (/^leg_h[lr]_upper$/.test(k)) p[k].rotation.x = 55 * D * e; else if (/^leg_h[lr]_lower$/.test(k)) p[k].rotation.x = -85 * D * e; else if (/^leg_h[lr]_foot$/.test(k)) p[k].rotation.x = 45 * D * e; }
        if (this.hop >= 1) { this.hop = -1; this.wait = rr(4, 14); for (const k in p) if (/^leg_/.test(k)) p[k].rotation.x = 0; }
      }
      this.y = Math.max(terrainH(this.x, this.z), WATER_Y - 0.15) + this.lift; this.g.position.set(this.x, this.y, this.z); this.g.rotation.set(0, this.yaw, 0);
      this.g.visible = !this.far && terrainH(this.x, this.z) > WATER_Y - 0.12;
    }
  }

  /* ---------- 잠자리 ---------- */
  class Dragonfly extends Animal {
    constructor(o) { super('dragonfly', o.scale); this.o = o; this.zs = o.z; this.off = o.off; this.h = o.h; this.ph = R() * 10; this.tx = 0; this.tz = 0; this.vx = 0; this.vz = 0; this.setPos(riverX(this.zs), this.zs, 0); this.tgt = [this.x, this.z]; this.next = 0; }
    update(dt) {
      this.t += dt; this.next -= dt;
      if (this.next < 0) { const z = this.zs + rr(-14, 14), hw = riverHalfW(z); this.tgt = [riverX(z) + rr(-1.1, 1.1) * hw, z]; this.zs = z; this.next = rr(0.8, 3.5); this.hv = rr(0.6, 1.8); }
      const dx = this.tgt[0] - this.x, dz = this.tgt[1] - this.z, d = Math.hypot(dx, dz) + 1e-4, sp = Math.min(3.5, d * 2.5);
      this.x += dx / d * sp * dt; this.z += dz / d * sp * dt;
      if (d > 0.4) this.yaw = turnTo(this.yaw, Math.atan2(dx, dz), 5, dt);
      this.y = WATER_Y + (this.hv || this.h) + 0.03 * Math.sin(this.t * 3 + this.ph);
      const fl = 35 * D * Math.sin(this.t * 60 + this.ph), p = this.p;
      if (p.wing_fl) { p.wing_fl.rotation.z = fl; p.wing_fr.rotation.z = -fl; p.wing_hl.rotation.z = -fl * 0.8; p.wing_hr.rotation.z = fl * 0.8; }
      if (p.abdomen) p.abdomen.rotation.x = 6 * D * Math.sin(this.t * 4);
      this.g.position.set(this.x, this.y, this.z); this.g.rotation.set(0.1 * (sp / 3.5), this.yaw, 0);
    }
  }

  /* ---------- 초기 배치 ---------- */
  F.Quad = Quad; F.Animal = Animal;
  F.init = function (scene, spawn) {
    F.scene = scene;
    if (!AssetLib.has('deer')) return;
    const add = (fn) => { try { return fn(); } catch (e) { console.warn('동물 생성 실패', e); } };
    const near = (cx, cz, r) => pickLand(cx, cz, r, 200) || pickLand(cx, cz, r * 2, 200);
    const sx = spawn.x, sz = spawn.z, hx = HOUSE.x, hz = HOUSE.z;
    // 사슴 무리 (초원 2곳)
    const herds = [[hx - 10, hz + 70, 30], [hx + 60, hz - 55, 35], [hx - 70, hz - 60, 30]];
    herds.forEach((h, hi) => {
      const home = near(h[0], h[1], 16); if (!home) return;
      const n = hi === 0 ? 4 : 3;
      for (let i = 0; i < n; i++) add(() => {
        const stag = i === 0 && hi !== 2;
        const a = new Quad(stag && AssetLib.has('stag') ? 'stag' : 'deer', { scale: stag ? 1.0 : rr(0.95, 1.08), walk: 1.1, run: 6.2, fleeDist: 16, alertDist: 32, stride: 1.25, len: 0.8, roam: h[2], tailSwish: false });
        const pt = pickLand(home[0], home[1], 8) || home; a.setPos(pt[0], pt[1], rr(0, TAU2)); a.home = [home[0], home[1]]; a.home.radius = h[2]; a.state = 'graze'; a.timer = rr(2, 10); return a;
      });
    });
    // 토끼 (집 주변 초원)
    for (let i = 0; i < 9; i++) add(() => {
      const c = near(hx + rr(-40, 40), hz + rr(-40, 40), 25); if (!c) return;
      const a = new Hopper('rabbit', { scale: 1, hopT: 0.5, hopDist: 0.45, arc: 0.17, hindExt: 55, hindLow: 50, fleeDist: 9, restMin: 2, restMax: 9, roam: 12, tailFlick: false });
      a.setPos(c[0], c[1], rr(0, TAU2)); a.home = [c[0], c[1]]; return a;
    });
    // 여우
    for (let i = 0; i < 2; i++) add(() => {
      const c = near(hx + rr(-90, 90), hz + rr(-90, 90), 30); if (!c) return;
      const a = new Quad('fox', { scale: 1, walk: 0.9, run: 6.0, fleeDist: 14, alertDist: 26, stride: 0.8, len: 0.5, roam: 50, grazeNeck: 30, grazeHead: 25, flexF: 55, flexH: 50, tailSwish: true });
      a.setPos(c[0], c[1], rr(0, TAU2)); a.home = [c[0], c[1]]; a.home.radius = 50; a.state = 'sniff'; a.timer = rr(2, 6); return a;
    });
    // 다람쥐
    for (let i = 0; i < 4; i++) add(() => {
      const c = near(hx + rr(-55, 55), hz + rr(-55, 55), 20); if (!c) return;
      const a = new Hopper('squirrel', { scale: 1, hopT: 0.32, hopDist: 0.45, arc: 0.13, hindExt: 45, hindLow: 40, fleeDist: 7, restMin: 1, restMax: 5, roam: 8, tailFlick: true });
      a.setPos(c[0], c[1], rr(0, TAU2)); a.home = [c[0], c[1]]; return a;
    });
    // 작은 새(지상) 와 비행 무리
    if (AssetLib.has('songbird')) {
      for (let i = 0; i < 9; i++) add(() => {
        const c = near(hx + rr(-45, 45), hz + rr(-45, 45), 25); if (!c) return;
        const a = new Songbird('songbird', { scale: 1, fleeDist: 5 }); a.setPos(c[0], c[1], rr(0, TAU2)); a.home = [c[0], c[1]]; return a;
      });
      for (let i = 0; i < 4; i++) add(() => { const a = new Soarer('songbird', { scale: 1, cx: hx + rr(-30, 30), cz: hz + rr(-30, 30), rad: rr(12, 30), alt: rr(9, 18), speed: rr(5, 7), flap: true, flapHz: 38, bob: 2, dir: R() < 0.5 ? 1 : -1 }); return a; });
    }
    if (AssetLib.has('kingfisher')) add(() => {
      const a = new Songbird('kingfisher', { scale: 1, fleeDist: 6 });
      const pz = House.pier ? House.pier.z : hz, px = House.pier ? House.pier.x1 - 1.5 : hx + 50;
      a.setPos(px, pz + 0.7, 0); a.y = (House.pier ? House.pier.top : 0.6) + 0.55; a.perchY = a.y; a.home = [px, pz]; return a;
    });
    // 매
    if (AssetLib.has('hawk')) for (let i = 0; i < 2; i++) add(() => new Soarer('hawk', { scale: 1.0, cx: hx + rr(-60, 60), cz: hz + rr(-60, 60), rad: rr(70, 130), alt: rr(75, 110), speed: rr(9, 12), flap: i === 1, flapHz: 6, bob: 8, dir: i ? -1 : 1 }));
    // 오리, 왜가리, 물고기, 개구리, 잠자리
    if (AssetLib.has('duck')) {
      const z0 = rr(-60, 60), lead = add(() => new Duck({ scale: 1, z: z0, off: rr(-0.3, 0.3), dir: R() < 0.5 ? 1 : -1 }));
      if (lead) for (let i = 1; i < 5; i++) add(() => { const d = new Duck({ scale: 1, z: z0 - i * 1.2, off: lead.off, dir: lead.dir, leader: lead }); d.slot = i; d.side = i % 2 ? 1 : -1; return d; });
      add(() => new Duck({ scale: 1, z: rr(-150, 150), off: rr(-0.4, 0.4), dir: R() < 0.5 ? 1 : -1 }));
    }
    if (AssetLib.has('heron')) add(() => new Heron({ scale: 1 }));
    if (AssetLib.has('trout')) for (let i = 0; i < 12; i++) add(() => new Fish('trout', { scale: 1, z: rr(-160, 160), off: rr(-0.6, 0.6), dep: rr(0.25, 0.7), spd: rr(0.4, 0.9) }));
    if (AssetLib.has('carp')) for (let i = 0; i < 6; i++) add(() => new Fish('carp', { scale: 1, z: rr(-160, 160), off: rr(-0.6, 0.6), dep: rr(0.3, 0.8), spd: rr(0.25, 0.5) }));
    if (AssetLib.has('minnow')) for (let s = 0; s < 4; s++) {
      const L = add(() => new Fish('minnow', { scale: 1, z: rr(-150, 150), off: rr(-0.5, 0.5), dep: rr(0.2, 0.5), spd: rr(0.5, 0.9) }));
      if (L) for (let i = 0; i < 14; i++) add(() => { const f = new Fish('minnow', { scale: rr(0.85, 1.15), z: L.zs, off: L.off, dep: L.dep, spd: L.spd, leader: L }); f.ox = rr(-0.8, 0.8); f.oo = rr(-0.08, 0.08); f.od = rr(-0.12, 0.12); return f; });
    }
    if (AssetLib.has('trout')) for (let i = 0; i < 5; i++) add(() => new LakeFish('trout', { scale: 1, z: 0, off: 0, dep: 0.5, spd: rr(0.3, 0.7) }));
    if (AssetLib.has('carp')) for (let i = 0; i < 4; i++) add(() => new LakeFish('carp', { scale: 1, z: 0, off: 0, dep: 0.6, spd: rr(0.2, 0.45) }));
    if (AssetLib.has('minnow')) for (let i = 0; i < 12; i++) add(() => new LakeFish('minnow', { scale: rr(0.9, 1.2), z: 0, off: 0, dep: 0.3, spd: rr(0.5, 0.9) }));
    if (AssetLib.has('duck')) for (let i = 0; i < 3; i++) add(() => new LakeDuck({}));
    if (AssetLib.has('frog')) for (let i = 0; i < 6; i++) add(() => {
      for (let t = 0; t < 60; t++) { const z = rr(-150, 150), hw = riverHalfW(z), side = R() < 0.5 ? -1 : 1, x = riverX(z) + side * hw * rr(1.05, 1.5); if (terrainH(x, z) > WATER_Y + 0.05 && terrainH(x, z) < WATER_Y + 0.6 && !inHouseBox(x, z, 4) && !inVillage(x, z, 4)) { const a = new Frog({ scale: 1 }); a.setPos(x, z, rr(0, TAU2)); return a; } }
    });
    if (AssetLib.has('dragonfly')) for (let i = 0; i < 6; i++) add(() => new Dragonfly({ scale: 1, z: rr(-120, 120), off: 0, h: rr(0.5, 1.6) }));
    F.ready = true;
  };

  const VIS = { deer: 115, stag: 115, fox: 75, rabbit: 42, squirrel: 38, songbird: 34, kingfisher: 38, duck: 75, heron: 100, hawk: 650, trout: 30, carp: 34, minnow: 28, frog: 28, dragonfly: 36 };
  F.enabled = true;
  F.setEnabled = function (on) { F.enabled = !!on; if (!on) for (const a of list) a.g.visible = false; };
  F.update = function (dt, camera) {
    if (!F.ready || !F.enabled) return;
    F.t += dt; const px = camera.position.x, pz = camera.position.z, vs = F.visScale || 1;
    for (const a of list) {
      if (a.village) continue;
      const d = Math.hypot(a.x - px, a.z - pz), lim = (VIS[a.bundle] || 80) * vs, far = d > lim;
      a.far = far;
      if (far) { a.g.visible = false; if (a instanceof Soarer) { a.update(Math.min(dt, 0.05), px, pz); a.g.visible = false; } else if (d < 260 || a instanceof Fish || a instanceof Duck) a.update(Math.min(dt, 0.05), px, pz), a.g.visible = false; continue; }
      a.g.visible = true; a.update(Math.min(dt, 0.05), px, pz);
      if (a.shadowCap) { const want = d < 45; if (want !== a._sh) { a._sh = want; for (const m of a.meshes) m.castShadow = want; } }
    }
  };
  /* 디버그: 정적 포즈 지정 (부호/방향 검증용) */
  F.pose = function (a, pose, k) {
    k = k === undefined ? 0.5 : k; a.update = function () { };
    if (a instanceof Quad) { if (pose === 'graze') { a.state = 'graze'; a.gz = 1; } else if (pose === 'look') { a.state = 'look'; a.al = 1; } a.gait(0.12, pose === 'idle' ? 0 : (pose === 'run' ? 1 : 0.6)); a.pose(0.001); if (pose === 'graze') { a.gz = 1; a.pose(0.001); } }
    else if (a instanceof Hopper) { a.hopping = pose === 'hop'; a.h = k; a.nextHop = 99; a.nextHopCount = 9; Hopper.prototype.update.call(a, 0.0001, 1e6, 1e6); }
    else if (a.ws) { setWings(a.ws, pose === 'fold' ? 0 : 1, pose === 'flapup' ? -0.8 : (pose === 'flapdown' ? 0.8 : 0)); if (a.p.neck_1 && pose === 'strike') { a.p.neck_1.rotation.x = -20 * D; a.p.neck_2.rotation.x = 30 * D; a.p.neck_3.rotation.x = -40 * D; a.p.head.rotation.x = 10 * D; } }
    else if (a instanceof Fish) { if (a.p.tail) a.p.tail.rotation.y = a.sw * (k > 0.5 ? 1 : -1); }
    else if (a instanceof Frog) { a.hop = k; const e = Math.sin(Math.PI * k); for (const n in a.p) { if (/^leg_h[lr]_upper$/.test(n)) a.p[n].rotation.x = 55 * D * e; else if (/^leg_h[lr]_lower$/.test(n)) a.p[n].rotation.x = -85 * D * e; else if (/^leg_h[lr]_foot$/.test(n)) a.p[n].rotation.x = 45 * D * e; } }
    else if (a instanceof Dragonfly) { const p = a.p, fl = 35 * D * (k > 0.5 ? 1 : -1); p.wing_fl.rotation.z = fl; p.wing_fr.rotation.z = -fl; p.wing_hl.rotation.z = -fl * 0.8; p.wing_hr.rotation.z = fl * 0.8; }
  };
  /* 디버그: 카메라 앞에 동물 한 마리 놓기 */
  F.show = function (name, camera, dist) {
    const a = list.find((q) => q.bundle === name); if (!a) return null;
    const s = fwdAng(camera.rotation.y + Math.PI); a.x = camera.position.x + s[0] * -(dist || 4); a.z = camera.position.z + s[1] * -(dist || 4); a.syncGround(); return a;
  };
  return F;
})();
