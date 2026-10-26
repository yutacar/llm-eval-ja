#!/usr/bin/env python3
"""A2 の目隠し評価ページを作る。モデル名を伏せ、問題ごとに A/B の並びをランダムにする。

例:  python3 blind_a2.py ud-iq4_xs deepseek-2.25
     → blind_a2.html をブラウザで開き、全問選んでから「結果を見る」
"""
import base64, html, json, pathlib, random, sys
import tasks_a

HERE = pathlib.Path(__file__).resolve().parent


def main():
    if len(sys.argv) != 3:
        print("使い方: python3 blind_a2.py <ラベル1> <ラベル2>")
        sys.exit(1)
    l1, l2 = sys.argv[1], sys.argv[2]
    rnd = random.Random()
    items, key = [], []
    for wid, kind, prompt in tasks_a.A2:
        outs = []
        for lab in (l1, l2):
            f = HERE / "results" / lab / f"a2_{wid}.json"
            if not f.exists():
                print(f"見つかりません: {f}")
                sys.exit(1)
            outs.append(json.loads(f.read_text())["content"])
        flip = rnd.random() < 0.5
        a, b = (outs[1], outs[0]) if flip else (outs[0], outs[1])
        key.append([l2, l1] if flip else [l1, l2])
        items.append((wid, kind, prompt, a, b))
    enc = base64.b64encode(json.dumps({"key": key, "labels": [l1, l2]}).encode()).decode()
    cards = []
    for n, (wid, kind, prompt, a, b) in enumerate(items):
        cards.append(f"""
<section><h2>{n + 1}. {html.escape(kind)}</h2>
<details><summary>お題を表示</summary><pre class="p">{html.escape(prompt)}</pre></details>
<div class="ab"><div><h3>A</h3><pre>{html.escape(a)}</pre></div><div><h3>B</h3><pre>{html.escape(b)}</pre></div></div>
<div class="pick">良いのは：
<label><input type="radio" name="q{n}" value="0"> A</label>
<label><input type="radio" name="q{n}" value="1"> B</label>
<label><input type="radio" name="q{n}" value="t"> 同じくらい</label></div></section>""")
    page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>A2 目隠し評価</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{{font-family:system-ui,"Noto Sans JP",sans-serif;max-width:1100px;margin:auto;padding:16px;background:#f6f5f2;color:#222}}
section{{background:#fff;border-radius:10px;padding:14px 16px;margin:14px 0;box-shadow:0 1px 3px #0002}}
h2{{margin:0 0 6px;font-size:18px}} h3{{margin:0 0 4px}}
.ab{{display:grid;grid-template-columns:1fr 1fr;gap:12px}} @media(max-width:700px){{.ab{{grid-template-columns:1fr}}}}
pre{{white-space:pre-wrap;font-family:inherit;background:#faf9f6;border:1px solid #ddd;border-radius:6px;padding:10px;margin:0;line-height:1.6}}
pre.p{{background:#eef3f8}} .pick{{margin-top:10px;font-weight:600}} label{{margin-left:14px}}
button{{font-size:16px;padding:10px 20px;border-radius:8px;border:0;background:#2563eb;color:#fff;cursor:pointer}}
#res{{font-size:16px;line-height:1.8}}
</style></head><body>
<h1>A2 日本語の文章：目隠し評価</h1>
<p>どちらのモデルの文章かは伏せてあります。問題ごとに A/B の並びはランダムです。全問選んでから「結果を見る」を押してください。</p>
{''.join(cards)}
<p><button onclick="show()">結果を見る</button></p><div id="res"></div>
<script>
const D=JSON.parse(atob("{enc}"));
function show(){{
  const win={{}};D.labels.forEach(l=>win[l]=0);let tie=0,lines=[],miss=0;
  D.key.forEach((k,i)=>{{
    const c=document.querySelector('input[name=q'+i+']:checked');
    if(!c){{miss++;return;}}
    if(c.value==='t'){{tie++;lines.push((i+1)+'. 同じくらい（A='+k[0]+' / B='+k[1]+'）');}}
    else{{const w=k[+c.value];win[w]++;lines.push((i+1)+'. '+w+' を選択（A='+k[0]+' / B='+k[1]+'）');}}
  }});
  if(miss){{document.getElementById('res').textContent='未回答が '+miss+' 問あります';return;}}
  document.getElementById('res').innerHTML='<h2>結果</h2>'+D.labels.map(l=>l+'： '+win[l]+' 勝').join('<br>')+
    '<br>同じくらい： '+tie+'<br><br>'+lines.join('<br>');
}}
</script></body></html>"""
    out = HERE / "blind_a2.html"
    out.write_text(page)
    print(f"作成: {out}")


if __name__ == "__main__":
    main()
