// check.mjs - pagoda-gen.js の数値チェック (node check.mjs)
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const src = readFileSync(new URL('./pagoda-gen.js', import.meta.url), 'utf8');
const ctx = vm.createContext({ console });
vm.runInContext(src, ctx, { timeout: 180000 });
const P = ctx.PAGODA;
if (!P) { console.log('ERROR pagoda-gen.js が globalThis.PAGODA を作らない'); process.exit(1); }

const errors = [];
function err(msg) {
  if (errors.length < 30) console.log('ERROR ' + msg);
  errors.push(msg);
}

// ---------- 合計 ----------
console.log('総ブロック数: ' + P.stats.total + '  (目安 約7万)');
console.log('  garden: ' + P.stats.garden + '  pagoda: ' + P.stats.pagoda + ' (目安 約3.2千)  water: ' + P.stats.water);
const sum = P.stats.garden + P.stats.pagoda + P.stats.water;
if (sum !== P.stats.total) err('stats.total が実数と一致しない (' + P.stats.total + ' != ' + sum + ')');

// ---------- 塔の y ごとの範囲 ----------
const byY = new Map();
for (const b of P.pagoda) {
  let o = byY.get(b[1]);
  if (!o) { o = { minX: b[0], maxX: b[0], minZ: b[2], maxZ: b[2] }; byY.set(b[1], o); }
  o.minX = Math.min(o.minX, b[0]); o.maxX = Math.max(o.maxX, b[0]);
  o.minZ = Math.min(o.minZ, b[2]); o.maxZ = Math.max(o.maxZ, b[2]);
}
console.log('--- 塔の y ごとの範囲 ---');
const ys = [...byY.keys()].sort((a, b) => a - b);
for (const y of ys) {
  const o = byY.get(y);
  console.log('y=' + y + ': x ' + o.minX + '..' + o.maxX + ', z ' + o.minZ + '..' + o.maxZ + (y < 3 ? ' (基壇)' : ''));
  if (y >= 3 && (o.minX !== -o.maxX || o.minZ !== -o.maxZ)) {
    err('y=' + y + ' 中心ずれ (x ' + o.minX + '..' + o.maxX + ', z ' + o.minZ + '..' + o.maxZ + ')');
  }
}

// ---------- 各層の軸部・屋根の幅 ----------
const RS = [4, 4, 3, 3, 2], RR = [9, 8, 7, 6, 5];
console.log('--- 各層の幅 ---');
// 屋根の広さは四隅の反り（rr+1 に出る軒先色のブロック）を除いて測る
for (let s = 0; s < 5; s++) {
  const y0 = 3 + s * 6, yr = y0 + 4, rr = RR[s];
  const shaft = byY.get(y0 + 1);
  const sw = shaft ? shaft.maxX - shaft.minX + 1 : -1, swz = shaft ? shaft.maxZ - shaft.minZ + 1 : -1;
  let minX = Infinity, maxX = -Infinity, minZ = Infinity, maxZ = -Infinity;
  for (const b of P.pagoda) {
    if (b[1] !== yr) continue;
    if (Math.abs(b[0]) > rr || Math.abs(b[2]) > rr) continue;   // 四隅の反りを除外
    minX = Math.min(minX, b[0]); maxX = Math.max(maxX, b[0]);
    minZ = Math.min(minZ, b[2]); maxZ = Math.max(maxZ, b[2]);
  }
  const rw = maxX - minX + 1, rwz = maxZ - minZ + 1;
  console.log((s + 1) + '層: 軸部 ' + sw + 'x' + swz + ' (必要 ' + (RS[s] * 2 + 1) + ')  屋根 ' + rw + 'x' + rwz + ' (必要 ' + (RR[s] * 2 + 1) + '、四隅の反りは除く)');
  if (sw !== RS[s] * 2 + 1 || swz !== RS[s] * 2 + 1) err((s + 1) + '層 軸部の幅が不一致');
  if (rw !== RR[s] * 2 + 1 || rwz !== RR[s] * 2 + 1) err((s + 1) + '層 屋根の幅が不一致');
}

// ---------- 最上部 ----------
const top = ys.length ? ys[ys.length - 1] : -1;
console.log('塔の最上部 y: ' + top);
if (top !== 46) err('塔の最上部が y=46 でない (' + top + ')');
if (P.pagodaTop !== 46) err('pagodaTop が 46 でない');

// ---------- 宙に浮いた塔のブロック ----------
const pset = new Set();
for (const b of P.pagoda) pset.add(b[0] + ',' + b[1] + ',' + b[2]);
const NB = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]];
let floats = 0;
for (const b of P.pagoda) {
  if (!NB.some(d => pset.has((b[0] + d[0]) + ',' + (b[1] + d[1]) + ',' + (b[2] + d[2])))) {
    err('宙に浮いたブロック: ' + b[0] + ',' + b[1] + ',' + b[2]);
    floats++;
  }
}

// ---------- 地面 y=0 の穴 ----------
const gset = new Set();
for (const b of P.garden) if (b[1] === 0) gset.add(b[0] + ',' + b[2]);
let holes = 0;
for (let x = -110; x <= 110; x++) {
  for (let z = -110; z <= 110; z++) {
    if (Math.hypot(x, z) > 110) continue;
    const e = Math.pow((x - 22) / 9, 2) + Math.pow((z - 12) / 7, 2);
    if (e <= 1) continue; // 池
    if (!gset.has(x + ',' + z)) { err('地面の穴: ' + x + ',' + z); holes++; }
  }
}

// ---------- 結果 ----------
if (errors.length === 0) {
  console.log('OK');
} else {
  if (errors.length > 30) console.log('...以下も同じ ERROR が ' + (errors.length - 30) + ' 件');
  console.log('ERROR ' + errors.length + ' 件');
  process.exit(1);
}
