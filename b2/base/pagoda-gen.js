// pagoda-gen.js - "five-story pagoda garden" voxel generation (no three.js / DOM)
(function () {
'use strict';

// ---------- rng: mulberry32(5052025) ----------
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    var t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
var rnd = mulberry32(5052025);

// ---------- hash / noise ----------
function hash2(x, z) {
  var h = Math.imul(x | 0, 374761393) ^ Math.imul(z | 0, 668265263) ^ 0x9E3779B9;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}
function sstep(t) { return t * t * (3 - 2 * t); }
function vnoise(x, z) {
  var xi = Math.floor(x), zi = Math.floor(z);
  var u = sstep(x - xi), v = sstep(z - zi);
  var a = hash2(xi, zi), b = hash2(xi + 1, zi), c = hash2(xi, zi + 1), d = hash2(xi + 1, zi + 1);
  return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
}
function fbm(x, z) {
  return vnoise(x, z) * 0.6 + vnoise(2.1 * x, 2.1 * z) * 0.3 + vnoise(4.3 * x, 4.3 * z) * 0.1;
}

// ---------- colors ----------
function hex(h) {
  return [parseInt(h.slice(1, 3), 16) / 255, parseInt(h.slice(3, 5), 16) / 255, parseInt(h.slice(5, 7), 16) / 255];
}
var C = {
  koke: ['#3d6630', '#48743a', '#557f43', '#34592b'].map(hex),
  shirasu: hex('#d8d2c4'), samon: hex('#c6bfaf'),
  ishi: hex('#9f9a8e'), ishiD: hex('#7d786d'),
  shu: hex('#c8402a'), shuD: hex('#9e2f1f'),
  kabe: hex('#f0e8d8'),
  renji: hex('#3e7656'), renjiD: hex('#2a4f3a'),
  toko: hex('#5b3a24'),
  kawara: hex('#39404d'), kinoki: hex('#4b5464'),
  kin: hex('#d9a441'), kinD: hex('#b07f2a'),
  trunk: hex('#5e3f28'),
  matsu: ['#2c5134', '#335c3a', '#274a2f'].map(hex),
  momiji: ['#c23a1e', '#d85520', '#e2762a', '#a22a1c'].map(hex),
  sakura: ['#f2a7bf', '#ea8eab', '#ffc6d6', '#f6b6c9'].map(hex),
  pondbed: hex('#34444a'), water: hex('#2f74a3'), dirt: hex('#4a3b2c'),
  bridge: hex('#8a5a3a'), fire: hex('#ffd27a'),
  mtA: hex('#40594a'), mtB: hex('#6f7c8e')
};

// ---------- placement ----------
var JITTER = 0.1;
var g = new Map(), p = new Map(), w = new Map();
function put(map, x, y, z, col) {
  var j = 1 + (rnd() - 0.5) * JITTER;
  map.set(x + ',' + y + ',' + z, [col[0] * j, col[1] * j, col[2] * j]);
}
function parseKey(k) {
  var i = k.split(',');
  return [+i[0], +i[1], +i[2]];
}
function toList(map) {
  var out = [];
  map.forEach(function (col, k) {
    var c = parseKey(k);
    out.push([c[0], c[1], c[2], col[0], col[1], col[2]]);
  });
  return out;
}

// ---------- ground ----------
var x, z, i, dx, dz, y;
for (x = -110; x <= 110; x++) {
  for (z = -110; z <= 110; z++) {
    var r = Math.hypot(x, z);
    if (r > 110) continue;
    var e = Math.pow((x - 22) / 9, 2) + Math.pow((z - 12) / 7, 2);
    if (e <= 1) {
      put(g, x, -2, z, C.pondbed);
      put(w, x, -0.35, z, C.water);
      continue;
    }
    var col;
    if (e <= 1.32) {
      col = hash2(x + 7, z - 11) < 0.5 ? C.ishi : C.ishiD;   // pond edge stone
    } else if (Math.max(Math.abs(x), Math.abs(z)) <= 14) {
      col = (Math.abs(x) % 3 === 0) ? C.samon : C.shirasu;   // raked sand garden
    } else if (Math.abs(x) <= 2 && z > 14 && z <= 48) {
      col = C.shirasu;                                        // approach path
    } else {
      var fi = Math.floor(fbm(0.12 * x, 0.12 * z) * 4);
      if (fi < 0) fi = 0; if (fi > 3) fi = 3;
      col = C.koke[fi];
    }
    put(g, x, 0, z, col);
    if (r <= 50) put(g, x, -1, z, C.dirt);
  }
}

// ---------- stepping stones ----------
var SEKI = [[13, 6], [31, 17], [28, 5], [15, 18], [24, 19]];
for (i = 0; i < SEKI.length; i++) {
  put(g, SEKI[i][0], 1, SEKI[i][1], C.ishi);
  put(g, SEKI[i][0] + 1, 1, SEKI[i][1], C.ishi);
  if (i % 2 === 0) put(g, SEKI[i][0], 2, SEKI[i][1], C.ishi);
}
for (z = 16; z <= 46; z += 3) {
  if (z % 2 !== 0) { put(g, -1, 1, z, C.ishi); put(g, 0, 1, z, C.ishi); }
  else { put(g, 0, 1, z, C.ishi); put(g, 1, 1, z, C.ishi); }
}

// ---------- red drum bridge ----------
for (x = 12; x <= 32; x++) {
  var t = (x - 12) / 20;
  var yb = Math.round(1 + 3.6 * Math.sin(Math.PI * t));
  for (z = 11; z <= 13; z++) put(g, x, yb, z, C.bridge);
  if ((x - 12) % 5 === 0 && t > 0.04 && t < 0.96) {
    for (y = 1; y <= yb - 1; y++) put(g, x, y, 12, C.shuD);
  }
  put(g, x, yb + 1, 10, C.shu);
  put(g, x, yb + 1, 14, C.shu);
  if ((x - 12) % 4 === 0) { put(g, x, yb + 2, 10, C.shu); put(g, x, yb + 2, 14, C.shu); }
  if (x === 12 || x === 32) { put(g, x, 3, 10, C.kin); put(g, x, 3, 14, C.kin); }
}

// ---------- stone lanterns ----------
function lantern(lx, lz) {
  var d1, d2;
  for (d1 = -1; d1 <= 1; d1++) for (d2 = -1; d2 <= 1; d2++) put(g, lx + d1, 1, lz + d2, C.ishiD);
  put(g, lx, 2, lz, C.ishi); put(g, lx, 3, lz, C.ishi);
  for (d1 = -1; d1 <= 1; d1++) for (d2 = -1; d2 <= 1; d2++) put(g, lx + d1, 4, lz + d2, C.ishi);
  put(g, lx, 5, lz, C.fire);
  put(g, lx - 1, 5, lz - 1, C.ishi); put(g, lx + 1, 5, lz - 1, C.ishi);
  put(g, lx - 1, 5, lz + 1, C.ishi); put(g, lx + 1, 5, lz + 1, C.ishi);
  for (d1 = -2; d1 <= 2; d1++) for (d2 = -2; d2 <= 2; d2++) put(g, lx + d1, 6, lz + d2, C.ishiD);
  for (d1 = -1; d1 <= 1; d1++) for (d2 = -1; d2 <= 1; d2++) put(g, lx + d1, 7, lz + d2, C.ishi);
  put(g, lx, 8, lz, C.ishi);
}
lantern(-6, 18); lantern(10, 20); lantern(-17, -9);

// ---------- trees ----------
function inBridge(bx, bz) { return bx >= 4 && bx <= 40 && Math.abs(bz - 12) < 9; }
function pick(pal, bx, by, bz) {
  var n = pal.length;
  return pal[Math.floor(hash2(bx * 31 + by * 7, bz * 17 - by * 5) * n) % n];
}
function tree(x0, z0, h, kind) {
  if (inBridge(x0, z0)) return;
  var yy;
  for (yy = 1; yy <= h; yy++) put(g, x0, yy, z0, C.trunk);
  var d2v;
  if (kind === 'matsu') {
    put(g, x0 + 1, h + 1, z0, C.trunk);
    var tiers = [[3.4, h, 0], [2.6, h + 2, 1], [1.6, h + 3, 0]];
    for (var ti = 0; ti < tiers.length; ti++) {
      var rad = tiers[ti][0], ty = tiers[ti][1], cx = x0 + tiers[ti][2];
      var R = Math.ceil(rad) + 1;
      for (d2v = -R; d2v <= R; d2v++) for (var dz2 = -R; dz2 <= R; dz2++) {
        var lim = rad * rad + (vnoise(cx + d2v, z0 + dz2 + 3 * ty) - 0.5) * 3;
        if (d2v * d2v + dz2 * dz2 <= lim) put(g, cx + d2v, ty, z0 + dz2, pick(C.matsu, cx + d2v, ty, z0 + dz2));
      }
    }
  } else {
    var pal = (kind === 'momiji') ? C.momiji : C.sakura;
    var cy = h + 2, R2 = 2.8;
    for (dx = -4; dx <= 4; dx++) for (var dy = -4; dy <= 4; dy++) for (dz = -4; dz <= 4; dz++) {
      d2v = dx * dx + dz * dz + Math.pow(dy * 1.3, 2);
      var lim2 = R2 * R2 + (vnoise(x0 + dx, z0 + dz + 5 * (cy + dy)) - 0.5) * 3;
      if (d2v <= lim2) put(g, x0 + dx, cy + dy, z0 + dz, pick(pal, x0 + dx, cy + dy, z0 + dz));
    }
  }
}
[[-18, 22], [-26, -4], [38, 30], [6, -24], [30, -14], [-34, 30]].forEach(function (tt) { tree(tt[0], tt[1], 4, 'momiji'); });
[[-30, 12, 5], [-10, 34, 4], [16, -32, 5], [40, -2, 4]].forEach(function (tt) { tree(tt[0], tt[1], tt[2], 'matsu'); });
[[-22, 32], [22, 32], [-30, -22], [-6, -30]].forEach(function (tt) { tree(tt[0], tt[1], 4, 'sakura'); });

// ---------- distant mountains ----------
var H = {};
for (x = -112; x <= 112; x++) for (z = -112; z <= 112; z++) {
  var mr = Math.hypot(x, z);
  if (mr < 90 || mr > 110) continue;
  var rise = Math.min(1, (mr - 88) / 8);
  H[x + ',' + z] = Math.max(1, Math.round((3 + fbm(0.045 * x + 7, 0.045 * z + 3) * 14) * rise));
}
Object.keys(H).forEach(function (k) {
  var cc = parseKey(k), mx = cc[0], mz = cc[1], mh = H[k];
  var nb = [[mx + 1, mz], [mx - 1, mz], [mx, mz + 1], [mx, mz - 1]];
  for (var my = 0; my <= mh; my++) {
    if (my !== 0 && my !== mh) {
      var inner = true;
      for (var ni = 0; ni < 4; ni++) {
        var hn = H[nb[ni][0] + ',' + nb[ni][1]];
        if (hn === undefined || hn < my) { inner = false; break; }
      }
      if (inner) continue;
    }
    var f = (my / mh) * 0.8;
    put(g, mx, my, mz, [
      C.mtA[0] + (C.mtB[0] - C.mtA[0]) * f,
      C.mtA[1] + (C.mtB[1] - C.mtA[1]) * f,
      C.mtA[2] + (C.mtB[2] - C.mtA[2]) * f
    ]);
  }
});

// ---------- five-story pagoda ----------
function sq(map, sy, r, col) {
  for (var bx = -r; bx <= r; bx++) for (var bz = -r; bz <= r; bz++) put(map, bx, sy, bz, col);
}
sq(p, 1, 8, C.ishi);           // base platform
sq(p, 2, 7, C.ishi);
for (x = -2; x <= 2; x++) put(p, x, 1, 9, C.ishiD);   // front steps

var RS = [4, 4, 3, 3, 2], RR = [9, 8, 7, 6, 5];
for (var s = 0; s < 5; s++) {
  var rs = RS[s], rr = RR[s], y0 = 3 + s * 6;
  // shaft (outer wall only)
  for (var k = 0; k <= 3; k++) {
    var wy = y0 + k;
    for (dx = -rs; dx <= rs; dx++) for (dz = -rs; dz <= rs; dz++) {
      if (Math.max(Math.abs(dx), Math.abs(dz)) !== rs) continue;
      var wcol;
      if (k === 0) wcol = C.shu;                       // naga-nuki
      else if (k === 3) wcol = C.toko;                 // tokoyaku
      else {
        var along = (Math.abs(dx) === rs) ? dz : dx;
        if (Math.abs(dx) === rs && Math.abs(dz) === rs) wcol = C.shu;          // sumi-bashira
        else if (rs >= 3 && Math.abs(along) === rs - 1) wcol = C.shu;          // waki-bashira
        else if (Math.abs(along) <= 1) wcol = (k === 1 && along === 0) ? C.renjiD : C.renji;
        else wcol = C.kabe;
      }
      put(p, dx, wy, dz, wcol);
    }
  }
  // tokoyaku overhang ring at y0+3
  for (dx = -rs - 1; dx <= rs + 1; dx++) for (dz = -rs - 1; dz <= rs + 1; dz++) {
    if (Math.max(Math.abs(dx), Math.abs(dz)) === rs + 1) put(p, dx, y0 + 3, dz, C.toko);
  }
  // roof
  var yr = y0 + 4;
  sq(p, yr, rr, C.kawara);
  for (dx = -rr; dx <= rr; dx++) for (dz = -rr; dz <= rr; dz++) {
    if (Math.max(Math.abs(dx), Math.abs(dz)) === rr) put(p, dx, yr, dz, C.kinoki);
  }
  var rUpper = Math.max(rs + 1, Math.round((rr + rs) / 2));
  sq(p, yr + 1, rUpper, C.kawara);
  // corner upturn
  [[1, 1], [1, -1], [-1, 1], [-1, -1]].forEach(function (sc) {
    var sx = sc[0], sz = sc[1];
    put(p, sx * (rr + 1), yr, sz * rr, C.kinoki);
    put(p, sx * rr, yr, sz * (rr + 1), C.kinoki);
    put(p, sx * (rr + 1), yr, sz * (rr + 1), C.kinoki);
    put(p, sx * (rr + 1), yr + 1, sz * (rr + 1), C.kinoki);   // rests on block below
  });
}
// sōrin
sq(p, 33, 1, C.kinD);                                        // roban
for (y = 34; y <= 45; y++) put(p, 0, y, 0, C.kin);           // shinbashira
[35, 37, 39, 41, 43].forEach(function (ry) {                 // kurin
  put(p, 1, ry, 0, C.kin); put(p, -1, ry, 0, C.kin);
  put(p, 0, ry, 1, C.kin); put(p, 0, ry, -1, C.kin);
});
// sōren: four corner horns at y=44, tied to the shinbashira by same-level cross blocks
put(p, 1, 44, 1, C.kinD); put(p, 1, 44, -1, C.kinD);
put(p, -1, 44, 1, C.kinD); put(p, -1, 44, -1, C.kinD);
put(p, 1, 44, 0, C.kinD); put(p, -1, 44, 0, C.kinD);
put(p, 0, 44, 1, C.kinD); put(p, 0, 44, -1, C.kinD);
put(p, 0, 46, 0, C.kin);                                     // hōju

// ---------- output ----------
function build() {
  var garden = toList(g), pagoda = toList(p), water = toList(w);
  return {
    garden: garden,
    pagoda: pagoda,
    water: water,
    pagodaTop: 46,
    stats: {
      garden: garden.length,
      pagoda: pagoda.length,
      water: water.length,
      total: garden.length + pagoda.length + water.length
    }
  };
}
globalThis.PAGODA = build();
})();
