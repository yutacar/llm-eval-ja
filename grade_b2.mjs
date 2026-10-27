// B2（既存コードへの機能追加：五重塔の雪景色）の採点。
// 例:  node grade_b2.mjs ~/work/b2-ud-iq4_xs
// 元の pagoda-gen.js（~/work/b2-src）と比べて、通常の結果が変わっていないか、雪が正しく積もっているかを調べる。
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import vm from "node:vm";
import { execFileSync } from "node:child_process";

const dir = path.resolve((process.argv[2] || "").replace(/^~/, os.homedir()));
const src = path.join(os.homedir(), "work", "b2-src");
if (!fs.existsSync(path.join(dir, "pagoda-gen.js"))) { console.log("使い方: node grade_b2.mjs <作業フォルダ>"); process.exit(1); }

function run(file) {
  const ctx = { console: { log() {}, warn() {}, error() {} }, Math, Map, Set, Array, Object, JSON, Number, String };
  ctx.globalThis = ctx;
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(file, "utf8"), ctx, { timeout: 60000 });
  return ctx;
}
// Map（キー "x,y,z"）か、{x,y,z} の配列をレイヤーとして集める
function layers(obj, prefix = "", out = {}, depth = 0) {
  if (!obj || depth > 3) return out;
  if (obj instanceof Map || (obj.constructor && obj.constructor.name === "Map")) {
    const keys = [...obj.keys()];
    if (keys.length && typeof keys[0] === "string" && /^-?\d+,-?\d+,-?\d+$/.test(keys[0])) {
      out[prefix || "root"] = new Map([...obj.entries()].map(([k, v]) => [k, JSON.stringify(v)]));
      return out;
    }
  }
  // [x, y, z, r, g, b] の配列（この五重塔の形式）
  if (Array.isArray(obj) && obj.length && Array.isArray(obj[0]) && obj[0].length >= 3 && obj[0].slice(0, 3).every(v => typeof v === "number")) {
    out[prefix || "root"] = new Map(obj.map(b => [`${b[0]},${b[1]},${b[2]}`, JSON.stringify(b)]));
    return out;
  }
  if (Array.isArray(obj) && obj.length && typeof obj[0] === "object" && "x" in obj[0] && "y" in obj[0] && "z" in obj[0]) {
    out[prefix || "root"] = new Map(obj.map(b => [`${b.x},${b.y},${b.z}`, JSON.stringify(b)]));
    return out;
  }
  if (typeof obj === "object") for (const k of Object.keys(obj)) layers(obj[k], prefix ? `${prefix}.${k}` : k, out, depth + 1);
  return out;
}
function same(a, b) {
  if (a.size !== b.size) return false;
  for (const [k, v] of a) if (b.get(k) !== v) return false;
  return true;
}
const results = [];
const check = (name, ok, detail = "") => { results.push(ok); console.log(`${ok ? "○" : "×"} ${name}${!ok && detail ? "\n    " + detail : ""}`); };

let base, now;
try { base = run(path.join(src, "pagoda-gen.js")); } catch (e) { console.log("元のファイルを実行できません:", e.message); process.exit(1); }
try { now = run(path.join(dir, "pagoda-gen.js")); } catch (e) { check("pagoda-gen.js が動く", false, e.message); process.exit(0); }
const L0 = layers(base.PAGODA), L1 = layers(now.PAGODA), LS = layers(now.PAGODA_SNOW);
const names0 = Object.keys(L0);
check("通常の結果が元と同じ（build() を壊していない）",
  names0.length > 0 && names0.every(n => L1[n] && same(L0[n], L1[n])) && Object.keys(L1).length === names0.length,
  `レイヤー 元:${names0.join(",")} / 今:${Object.keys(L1).join(",")}`);
check("PAGODA_SNOW がある", !!now.PAGODA_SNOW);
const snowName = Object.keys(LS).find(n => /snow/i.test(n));
check("snow レイヤーがある", !!snowName, `レイヤー: ${Object.keys(LS).join(",")}`);
if (snowName) {
  const snow = LS[snowName];
  const others = Object.keys(LS).filter(n => n !== snowName);
  check("雪景色の他のレイヤーは通常と同じ", names0.every(n => {
    const m = others.find(o => o === n || o.endsWith("." + n.split(".").pop()));
    return m && same(L0[n], LS[m]);
  }));
  const solidNames = names0.filter(n => /garden|pagoda/i.test(n));
  const water = names0.filter(n => /water/i.test(n));
  const solid = new Set(solidNames.flatMap(n => [...L0[n].keys()]));
  const all = new Set(names0.flatMap(n => [...L0[n].keys()]));
  const expect = new Set();
  for (const k of solid) {
    const [x, y, z] = k.split(",").map(Number);
    if (y >= 0 && !all.has(`${x},${y + 1},${z}`)) expect.add(`${x},${y + 1},${z}`);
  }
  const waterCols = new Set(water.flatMap(n => [...L0[n].keys()].map(k => { const [x, , z] = k.split(","); return `${x},${z}`; })));
  let floating = 0, overlap = 0, onWater = 0, hit = 0;
  const extra = [];
  for (const k of snow.keys()) {
    const [x, y, z] = k.split(",").map(Number);
    const below = `${x},${y - 1},${z}`;
    if (!all.has(below)) floating++;
    if (all.has(k)) overlap++;
    if (waterCols.has(`${x},${z}`) && !solid.has(below)) onWater++;
    if (expect.has(k)) hit++; else extra.push(k);
  }
  const missing = [...expect].filter(k => !snow.has(k));
  const layerOf = k => names0.find(n => L0[n].has(k)) || "?";
  const tally = (list, f) => Object.entries(list.reduce((a, k) => { const t = f(k); a[t] = (a[t] || 0) + 1; return a; }, {}))
    .sort((a, b) => b[1] - a[1]).slice(0, 6).map(([t, c]) => `${t}: ${c}`).join(" / ");
  if (missing.length) console.log(`   積もっていない場所 ${missing.length} か所（下のブロックのレイヤーと高さ）: ` +
    tally(missing, k => { const [x, y, z] = k.split(",").map(Number); return `${layerOf(`${x},${y - 1},${z}`)} y=${y - 1}`; }));
  if (extra.length) console.log(`   余分な雪 ${extra.length} 個（下のブロックのレイヤーと高さ）: ` +
    tally(extra, k => { const [x, y, z] = k.split(",").map(Number); return `${layerOf(`${x},${y - 1},${z}`)} y=${y - 1}`; }));
  const isWhite = v => { try { const a = JSON.parse(v); if (Array.isArray(a) && a.length >= 6) return Math.abs(a[3] - 0xf4 / 255) < 0.03 && Math.abs(a[4] - 0xf6 / 255) < 0.03 && Math.abs(a[5] - 0xfa / 255) < 0.03; } catch (e) {} return /f4f6fa|16053498/i.test(v); };
  const white = [...snow.values()].filter(isWhite).length;
  console.log(`   雪のブロック ${snow.size} 個 / 積もるべき場所 ${expect.size} か所（garden/pagoda の上面）`);
  check("宙に浮いた雪が無い", floating === 0, `${floating} 個`);
  check("既存のブロックと重なる雪が無い", overlap === 0, `${overlap} 個`);
  check("水面の上に雪が無い", onWater === 0, `${onWater} 個`);
  check("積もるべき場所すべてに雪がある", expect.size > 0 && hit === expect.size, `${hit}/${expect.size}`);
  check("積もるべき場所以外に雪が無い", hit === snow.size, `${snow.size - hit} 個が余分`);
  console.log(`   （参考）色が #f4f6fa そのものの雪: ${white}/${snow.size}（明るさの揺らぎを付けた場合は少なくなる）`);
}
try {
  const out = execFileSync("node", ["check.mjs"], { cwd: dir, encoding: "utf8", timeout: 120000 });
  check("node check.mjs が OK（ERROR なし）", /OK/.test(out) && !/ERROR/.test(out), out.slice(-300));
  check("check.mjs が雪を確認している", /snow|雪/i.test(fs.readFileSync(path.join(dir, "check.mjs"), "utf8")));
} catch (e) { check("node check.mjs が動く", false, String(e.stdout || e.message).slice(-300)); }
const html = fs.readFileSync(path.join(dir, "index.html"), "utf8");
// index.html の <script type="module"> の文法チェック（エラーがあると画面に何も描かれない）
{
  const m = [...html.matchAll(/<script[^>]*type=["']module["'][^>]*>([\s\S]*?)<\/script>/g)].map(x => x[1]).join("\n");
  const tmp = path.join(os.tmpdir(), `b2-module-${process.pid}.mjs`);
  fs.writeFileSync(tmp, m);
  try { execFileSync("node", ["--check", tmp], { encoding: "utf8", stdio: "pipe" }); check("index.html のスクリプトに文法エラーが無い", true); }
  catch (e) { check("index.html のスクリプトに文法エラーが無い", false, String(e.stderr || e.message).split("\n").slice(0, 5).join(" / ")); }
  fs.unlinkSync(tmp);
}
check("index.html に S キーの切り替えがある", /KeyS|['"]s['"]|['"]S['"]/.test(html) && /PAGODA_SNOW/.test(html));
check("操作説明に「S: 雪景色」がある", /S\s*[:：]\s*雪景色/.test(html));
console.log(`合計: ${results.filter(Boolean).length}/${results.length}（見た目は index.html を開いて S キーで確認）`);
