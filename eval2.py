#!/usr/bin/env python3
"""1日目: A1 長文読解 / A2 日本語の文章 / A4 JSON 抽出 を Strata の API で実行して保存する。

例:  python3 eval2.py --label ud-iq4_xs
     python3 eval2.py --label deepseek-2.25 --tasks a1,a4
結果は results/<label>/ に保存。採点は grade_a.py、A2 の目隠し評価は blind_a2.py。
"""
import argparse, json, os, pathlib, sys, time, urllib.request, urllib.error
import tasks_a

HERE = pathlib.Path(__file__).resolve().parent


def api_key():
    k = os.environ.get("STRATA_BENCH_KEY", "").strip()
    if not k:
        p = pathlib.Path.home() / ".strata_key"
        if p.exists():
            k = p.read_text().strip()
    return k


def chat(url, prompt, max_tokens, budget, temperature, timeout):
    body = {"model": "strata", "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature, "max_tokens": max_tokens, "stream": False}
    if budget > 0:
        body["reasoning_budget_tokens"] = budget
    req = urllib.request.Request(url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    k = api_key()
    if k:
        req.add_header("Authorization", "Bearer " + k)
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        res = json.load(r)
    dt = time.time() - t0
    msg = res["choices"][0]["message"]
    content = msg.get("content") or ""
    if "</think>" in content:                       # 念のため、本文に混ざった思考を落とす
        content = content.split("</think>", 1)[1]
    return {"content": content.strip(), "reasoning_chars": len(msg.get("reasoning_content") or ""),
            "usage": res.get("usage", {}), "seconds": round(dt, 1),
            "finish_reason": res["choices"][0].get("finish_reason")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True, help="結果フォルダの名前（例: ud-iq4_xs, deepseek-2.25）")
    ap.add_argument("--url", default="http://127.0.0.1:8081/v1")
    ap.add_argument("--tasks", default="a1,a2,a4")
    ap.add_argument("--temperature", type=float, default=0.6)
    ap.add_argument("--budget", type=int, default=2048, help="思考の上限トークン（両モデル同じにする）")
    ap.add_argument("--timeout", type=int, default=3600)
    a = ap.parse_args()
    out = HERE / "results" / a.label
    out.mkdir(parents=True, exist_ok=True)
    todo = a.tasks.split(",")
    jobs = []
    if "a1" in todo:
        doc, qs = tasks_a.build_a1()
        jobs.append(("a1", tasks_a.a1_prompt(doc, qs), 1500))
    if "a2" in todo:
        jobs += [(f"a2_{i}", p, 1500) for i, _, p in tasks_a.A2]
    if "a4" in todo:
        jobs += [(f"a4_{i}", tasks_a.a4_prompt(t, k), 800) for i, t, k, _ in tasks_a.A4]
    meta = {"label": a.label, "temperature": a.temperature, "budget": a.budget, "started": time.ctime()}
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    t_all = time.time()
    for n, (name, prompt, mx) in enumerate(jobs, 1):
        f = out / f"{name}.json"
        if f.exists():
            print(f"[{n}/{len(jobs)}] {name}: 済み（やり直すときはファイルを消す）")
            continue
        print(f"[{n}/{len(jobs)}] {name} ...", end=" ", flush=True)
        try:
            r = chat(a.url, prompt, mx + a.budget, a.budget, a.temperature, a.timeout)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print("エラー:", e)
            sys.exit(1)
        f.write_text(json.dumps(r, ensure_ascii=False, indent=1))
        u = r["usage"]
        print(f"{r['seconds']}s  in {u.get('prompt_tokens')} / out {u.get('completion_tokens')}  {r['finish_reason']}")
    print(f"完了: {round((time.time() - t_all) / 60, 1)} 分  → {out}")


if __name__ == "__main__":
    main()
