/* =====================================================================
   09c_village_core.js — 마을 부지/배치(순수 데이터+지형 함수). 모델이 없어도 지형 평탄화와 길은 적용된다.
   로컬 좌표: +x = 큰길 방향(오두막 쪽), +z = 길의 남쪽(왼쪽).  world = V + R(rot)·(lx,lz)
   ===================================================================== */
const VILLAGE = { x: -105, z: 55, rot: 0, hx: 56, z0: -38, z1: 48, blend: 22, y: 0, plane: [0, 0, 0] };
VILLAGE.rot = Math.atan2(-6 - VILLAGE.z, -38 - VILLAGE.x) * 0 + Math.atan2(HOUSE.z - VILLAGE.z, HOUSE.x - VILLAGE.x);   // 오두막을 향하도록
VILLAGE.c = Math.cos(VILLAGE.rot); VILLAGE.s = Math.sin(VILLAGE.rot);
function villageToWorld(lx, lz) { return [VILLAGE.x + VILLAGE.c * lx - VILLAGE.s * lz, VILLAGE.z + VILLAGE.s * lx + VILLAGE.c * lz]; }
function villageToLocal(x, z) { const dx = x - VILLAGE.x, dz = z - VILLAGE.z; return [VILLAGE.c * dx + VILLAGE.s * dz, -VILLAGE.s * dx + VILLAGE.c * dz]; }
(function fitPlane() {            // 원래 지형에 최소제곱 평면을 맞춰서 흙 이동을 최소화
  let n = 0, sx = 0, sz = 0, sy = 0, sxx = 0, szz = 0, sxy = 0, szy = 0, sxz = 0;
  for (let a = -VILLAGE.hx; a <= VILLAGE.hx; a += 6) for (let b = VILLAGE.z0; b <= VILLAGE.z1; b += 6) {
    const w = villageToWorld(a, b), h = baseH(w[0], w[1]); n++; sx += a; sz += b; sy += h; sxx += a * a; szz += b * b; sxy += a * h; szy += b * h; sxz += a * b;
  }
  // 정규방정식(3x3) 풀이: h = p0 + p1*a + p2*b
  const M = [[n, sx, sz], [sx, sxx, sxz], [sz, sxz, szz]], Y = [sy, sxy, szy];
  const det = (m) => m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
  const D = det(M), col = (k) => M.map((r, i) => r.map((v, j) => (j === k ? Y[i] : v)));
  VILLAGE.plane = [det(col(0)) / D, det(col(1)) / D, det(col(2)) / D];
  VILLAGE.y = VILLAGE.plane[0];
})();
function villagePlaneH(lx, lz) { return VILLAGE.plane[0] + VILLAGE.plane[1] * lx + VILLAGE.plane[2] * lz; }
/* 둥근 사각형 거리(안쪽 0, 바깥 양수) */
function villageDist(x, z) {
  const l = villageToLocal(x, z), dx = Math.max(Math.abs(l[0]) - VILLAGE.hx, 0), cz = (VILLAGE.z0 + VILLAGE.z1) / 2, hz = (VILLAGE.z1 - VILLAGE.z0) / 2, dz = Math.max(Math.abs(l[1] - cz) - hz, 0);
  return Math.hypot(dx, dz);
}
function inVillage(x, z, m) { return villageDist(x, z) < (m || 0) + 2; }
/* terrainH 에서 호출: 마을 안은 평면, 가장자리는 부드럽게 원래 지형으로 */
function villageBlendH(h, x, z) {
  const d = villageDist(x, z); if (d >= VILLAGE.blend) return h;
  const l = villageToLocal(x, z), hp = villagePlaneH(l[0], l[1]), t = smoothstep(VILLAGE.blend, 0, d);
  return h * (1 - t) + hp * t;
}

/* ---------- 배치 ---------- */
const VILLAGE_LAYOUT = (function () {
  // 건물 슬롯: [부품, lx, lz, 향(길 쪽으로 문이 향하도록), 색 팔레트 번호]
  const B = [];
  const N = -15.5, S = 15.5;           // 길 양쪽 줄 중심 z (북 = -z)
  const add = (part, lx, lz, face, pal) => B.push({ part, lx, lz, face, pal, w: 0, d: 0 });
  // 북쪽 줄 (문은 +z, 길 쪽)
  add('house_cottage_b', -40, N, 'S', 0); add('inn', -22, N - 1.5, 'S', 1); add('bakery', -3, N, 'S', 2); add('smithy', 15, N - 0.5, 'S', 3); add('house_cottage_a', 32, N, 'S', 4); add('house_cottage_b', 46, N, 'S', 2);
  // 남쪽 줄 (문은 -z)
  add('house_farm', -44, S + 0.5, 'N', 5); add('house_row', -24, S, 'N', 0); add('house_cottage_a', -6, S, 'N', 3); add('storehouse', 9, S, 'N', 1); add('house_cottage_b', 26, S, 'N', 5); add('house_cottage_a', 42, S, 'N', 1);
  // 교회: 광장 북쪽 샛길 끝(문 +z)
  add('church', 4, -34, 'S', 0);
  // 헛간: 남쪽 들판
  add('barn', -28, 38, 'N', 0);
  return { buildings: B, street: { x0: -56, x1: 60, w: 6.5 }, square: { r: 10 } };
})();
/* 길 스탬프용 점들 (buildWorldData 에서 PATHS 로 사용): 마을 큰길 + 교회 샛길 + 헛간 길 + 오두막 연결길 */
const VILLAGE_PATHS = (function () {
  const W = (pts) => pts.map((p) => villageToWorld(p[0], p[1]));
  const main = W([[-58, 0], [-30, 0], [0, 0], [30, 0], [62, 0]]);
  const church = W([[4, -3], [4, -20], [4, -28]]);
  const barn = W([[-28, 3], [-28, 20], [-28, 33]]);
  const plaza = W([[-12, 0], [12, 0]]);
  const linkW = [HOUSE.x - 8.5, HOUSE.z + 1.5];
  const toCabin = [villageToWorld(62, 0), [villageToWorld(62, 0)[0] * 0.5 + linkW[0] * 0.5 + 3, villageToWorld(62, 0)[1] * 0.5 + linkW[1] * 0.5 - 6], linkW];
  main.r = 3.6; church.r = 2.4; barn.r = 2.4; toCabin.r = 2.6;
  return { main, church, barn, plaza, toCabin, all: [main, church, barn, toCabin] };
})();
