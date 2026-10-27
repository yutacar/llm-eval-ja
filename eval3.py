#!/usr/bin/env python3
"""第3回: A3 推論 / A5 知らないことへの対応 / A6 長文読解・難 / A7 指示追従 / A8 ツール呼び出し を実行して保存する。

例:  python3 eval3.py --label ud-iq4_xs
     python3 eval3.py --label deepseek-2.25 --tasks a3,a5
結果は results3/<label>/ に保存。採点は grade_c.py。
"""
import argparse, json, pathlib, sys, time, urllib.error, urllib.request
import tasks_c
from eval2 import api_key

HERE = pathlib.Path(__file__).resolve().parent


def post(url, body, timeout):
    req = urllib.request.Request(url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    k = api_key()
    if k:
        req.add_header("Authorization", "Bearer " + k)
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        res = json.load(r)
    dt = time.time() - t0
    ch = res["choices"][0]
    msg = ch["message"]
    content = msg.get("content") or ""
    if "</think>" in content:
        content = content.split("</think>", 1)[1]
    calls = []
    for tc in msg.get("tool_calls") or []:
        fn = tc.get("function", {})
        args = fn.get("arguments")
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                args = {"_raw": args}
        calls.append({"name": fn.get("name"), "arguments": args})
    return {"content": content.strip(), "tool_calls": calls, "reasoning_chars": len(msg.get("reasoning_content") or ""),
            "usage": res.get("usage", {}), "seconds": round(dt, 1), "finish_reason": ch.get("finish_reason")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--url", default="http://127.0.0.1:8081/v1")
    ap.add_argument("--tasks", default="a3,a5,a6,a7,a8")
    ap.add_argument("--temperature", type=float, default=0.6)
    ap.add_argument("--budget", type=int, default=2048, help="思考の上限（A3 だけは 4096 で固定）")
    ap.add_argument("--repeat", type=int, default=2, help="A3 の繰り返し回数")
    ap.add_argument("--timeout", type=int, default=3600)
    a = ap.parse_args()
    out = HERE / "results3" / a.label
    out.mkdir(parents=True, exist_ok=True)
    todo = a.tasks.split(",")

    def user(p):
        return [{"role": "user", "content": p}]

    jobs = []   # (name, messages, max_tokens, budget, tools)
    if "a3" in todo:
        for rep in range(1, a.repeat + 1):
            jobs += [(f"a3_{i}_{rep}", user(tasks_c.a3_prompt(q)), 1500, 4096, None) for i, q, _ in tasks_c.A3]
    if "a5" in todo:
        jobs += [(f"a5_{i}", user(p), 1200, a.budget, None) for i, _, p in tasks_c.A5]
    if "a6" in todo:
        doc, qs = tasks_c.build_a6()
        jobs.append(("a6", user(tasks_a_prompt(doc, qs)), 1500, a.budget, None))
    if "a7" in todo:
        jobs += [(f"a7_{i}", user(p), 1000, a.budget, None) for i, p in tasks_c.A7]
    if "a8" in todo:
        jobs += [(f"a8_{i}", [{"role": "system", "content": tasks_c.A8_SYSTEM}, {"role": "user", "content": p}],
                  800, a.budget, tasks_c.A8_TOOLS) for i, p, _ in tasks_c.A8]
    (out / "meta.json").write_text(json.dumps({"label": a.label, "temperature": a.temperature, "budget": a.budget,
                                               "started": time.ctime()}, ensure_ascii=False, indent=1))
    t_all = time.time()
    for n, (name, msgs, mx, budget, tools) in enumerate(jobs, 1):
        f = out / f"{name}.json"
        if f.exists():
            print(f"[{n}/{len(jobs)}] {name}: 済み")
            continue
        print(f"[{n}/{len(jobs)}] {name} ...", end=" ", flush=True)
        body = {"model": "strata", "messages": msgs, "temperature": a.temperature, "max_tokens": mx + budget,
                "stream": False, "reasoning_budget_tokens": budget}
        if tools:
            body["tools"] = tools
        try:
            r = post(a.url, body, a.timeout)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print("エラー:", e)
            sys.exit(1)
        f.write_text(json.dumps(r, ensure_ascii=False, indent=1))
        u = r["usage"]
        print(f"{r['seconds']}s  in {u.get('prompt_tokens')} / out {u.get('completion_tokens')}  {r['finish_reason']}"
              + (f"  tools {[c['name'] for c in r['tool_calls']]}" if tools else ""))
    print(f"完了: {round((time.time() - t_all) / 60, 1)} 分  → {out}")


def tasks_a_prompt(doc, qs):
    import tasks_a
    return tasks_a.a1_prompt(doc, qs)


if __name__ == "__main__":
    main()
