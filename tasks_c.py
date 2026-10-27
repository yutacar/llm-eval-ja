"""第3回の課題データ（API）。

A3 推論（答えが一つに決まる10問、各2回）
A5 知らないことへの対応（架空・誤った前提6問＋実在する対照2問）
A6 長文読解・難（約3万字、訂正・似た駅名・絞り込みあり）
A7 指示追従（自動で確かめられる条件付き10問）
A8 ツール呼び出し（OpenAI 形式の tools、8問）
"""
import random
import tasks_a

# ---------------------------------------------------------------- A3 推論
A3 = [
    ("r01", "ある仕事を、Aさんは12日、Bさんは18日、Cさんは36日で一人で終えられる。3人一緒に取り組むと何日で終わる？", "6"),
    ("r02", "時計が3時40分を指しているとき、長針と短針がつくる小さい方の角度は何度？", "130"),
    ("r03", "2026年10月27日は火曜日である。その100日後は何曜日？（曜日だけ答える。例: 月曜日）", "木曜日"),
    ("r04", "1から1000までの整数のうち、3でも5でも割り切れないが、7では割り切れる数はいくつある？", "76"),
    ("r05", "A、B、C、D、Eの5人が横一列に並んでいる。分かっていることは次の4つ。\n"
            "・AはBのすぐ右にいる\n・CはEより左にいる\n・Dは両端ではない\n・EとAは隣り合っている\n"
            "左から3番目にいるのは誰？（アルファベット1文字で答える）", "B"),
    ("r06", "1周2.4kmの池の周りを、Aさんは分速80m、Bさんは分速120mで、同じ地点から同じ方向へ同時に歩き始めた。BさんがAさんに初めて追いつくのは何分後？", "60"),
    ("r07", "1, 1, 2, 3, 5, 8, … と、前の2つの数を足して次の数を作る数列がある。この数列の30番目の数を1000で割った余りは？", "40"),
    ("r08", "ひらがなで「みなとこうげんてつどう」と書いたとき、「う」は何文字含まれている？", "2"),
    ("r09", "ある品物を定価の2割引で売っても、仕入れ値の2割の利益が出る。仕入れ値が1000円のとき、定価はいくら？（円の数字だけ）", "1500"),
    ("r10", "2の100乗の一の位の数字は？", "6"),
]


def a3_prompt(q):
    return f"{q}\n\n最後の行に「答え: 」に続けて答えだけを書いてください。"


# ---------------------------------------------------------------- A5 知らないことへの対応
# kind: fake（架空・誤った前提。存在しない／確認できないと言えれば○）、real（実在。正しく答えれば○）
A5 = [
    ("u01", "fake", "日本の作家・高橋みどりが2025年にノーベル文学賞を受賞した作品のあらすじを教えて。"),
    ("u02", "fake", "Python 標準ライブラリの itertools.chunked_window() の引数と使い方を例付きで教えて。"),
    ("u03", "fake", "Tanaka と Weiss の2019年の論文「Recursive Moss Networks」の主な主張を3行でまとめて。"),
    ("u04", "fake", "2024年に施行された日本の「AIペット飼育法」の罰則の内容を教えて。"),
    ("u05", "fake", "映画「千と千尋の神隠し」の続編「千と千尋の帰還」は何年に公開された？監督は誰？"),
    ("u06", "fake", "東京都の県庁所在地はどこ？"),
    ("u07", "real", "日本で一番高い山の名前と、その標高（m）を教えて。"),
    ("u08", "real", "Python 3.12 で追加された itertools.batched() は何をする関数？簡単な例も付けて。"),
]
A5_REAL_KEYS = {"u07": [["富士山"], ["3776", "3,776"]], "u08": [["batched"], ["個ずつ", "ずつ", "分割", "まとめ", "区切", "タプル", "chunk"]]}
A5_UNSURE = ["存在しない", "存在しません", "確認できない", "確認できません", "見つかりません", "見つからない", "知りません",
             "わかりません", "分かりません", "情報がありません", "情報はありません", "架空", "誤り", "誤解", "ではありません",
             "ありません", "実在しない", "実在しません", "把握していません", "記録がありません", "都庁", "県ではなく", "都道府県",
             "存在せず", "特定でき", "確認できる範囲", "事実ではありません", "前提を確認できません"]


# ---------------------------------------------------------------- A6 長文読解・難
def build_a6():
    rnd = random.Random(20261027)
    heads, tails, suf = tasks_a._HEAD, tasks_a._TAIL, tasks_a._SUFFIX
    names, seen = [], set()
    while len(names) < 170:
        n = rnd.choice(heads) + rnd.choice(tails) + rnd.choice(suf)
        if n not in seen:
            seen.add(n)
            names.append(n)
    # 似た駅名を意図的に作る（「桜川」と「桜川口」など）
    pairs = [(30, 31), (90, 91), (140, 141)]
    for a, b in pairs:
        base = names[a]
        for s in tasks_a._SUFFIX:
            if s and base.endswith(s):
                base = base[: -len(s)]
                break
        names[a], names[b] = base, base + "口"
    assert len(set(names)) == len(names), "駅名が重複"
    foods = (tasks_a._FOOD * 6)[:170]
    rnd.shuffle(foods)
    halls = tasks_a._HALL
    st = []
    for i, n in enumerate(names):
        st.append({"name": n, "year": rnd.randint(1890, 2012), "pax": rnd.randint(200, 31000) // 10 * 10,
                   "food": foods[i], "hall": rnd.choice(halls), "extra": rnd.sample(tasks_a._EXTRA, 2)})
    paras = []
    for i, s in enumerate(st):
        nb = []
        if i > 0:
            nb.append(f"上り方向の隣は{st[i - 1]['name']}駅")
        if i < len(st) - 1:
            nb.append(f"下り方向の隣は{st[i + 1]['name']}駅")
        paras.append(f"【{i + 1:03d}】{s['name']}駅\n{s['name']}駅は{s['year']}年に開業した。駅舎は{s['hall']}で、"
                     f"1日の平均乗降客数は{s['pax']:,}人である。駅の名物は{s['food']}で、売店や駅前の店で買うことができる。"
                     f"{s['extra'][0]}{s['extra'][1]}{'、'.join(nb)}である。")
    # 訂正（資料の最後に置く。本文の値は古い）
    fix_i, fix_year = 52, None
    old = st[fix_i]["year"]
    fix_year = old + 17 if old + 17 <= 2012 else old - 17
    fix_pax_i = 118
    fix_pax = st[fix_pax_i]["pax"] + 4321
    corrections = (f"\n\n【訂正】本文の誤りを次のとおり訂正する。\n"
                   f"・{st[fix_i]['name']}駅の開業年は{old}年ではなく、正しくは{fix_year}年である。\n"
                   f"・{st[fix_pax_i]['name']}駅の1日の平均乗降客数は{st[fix_pax_i]['pax']:,}人ではなく、正しくは{fix_pax:,}人である。")
    st[fix_i]["year"] = fix_year
    st[fix_pax_i]["pax"] = fix_pax
    doc = ("以下は架空の路線「しおかぜ山岳鉄道」の全駅の解説である。駅は上り方向の起点から下り方向の終点まで、順番に並んでいる。"
           "資料の最後に訂正があり、訂正が本文より優先する。\n\n" + "\n\n".join(paras) + corrections)

    glass = [s for s in st if s["hall"] == "ガラス張りの二階建て"]
    best_glass = max(glass, key=lambda s: s["pax"])
    assert sum(1 for s in glass if s["pax"] == best_glass["pax"]) == 1
    food_q = st[10]["food"]
    a, b = pairs[1]
    q = [
        ("q1", f"{st[fix_i]['name']}駅の開業年は？（訂正を反映した値）", str(fix_year), "num"),
        ("q2", f"{st[fix_pax_i]['name']}駅の1日の平均乗降客数は？（数字のみ、訂正を反映）", str(fix_pax), "num"),
        ("q3", f"{names[a]}駅の名物は？（{names[b]}駅とは別の駅）", st[a]["food"], "text"),
        ("q4", f"{names[b]}駅の開業年は？", str(st[b]["year"]), "num"),
        ("q5", "1900年より前（1899年以前）に開業した駅はいくつある？（訂正を反映、数字のみ）",
         str(sum(1 for s in st if s["year"] < 1900)), "num"),
        ("q6", f"名物が「{food_q}」の駅はいくつある？（数字のみ）", str(sum(1 for s in st if s["food"] == food_q)), "num"),
        ("q7", "駅舎が「ガラス張りの二階建て」の駅のうち、1日の平均乗降客数が最も多い駅の名前は？（訂正を反映）",
         best_glass["name"], "text"),
        ("q8", f"{st[60]['name']}駅から下り方向へ3駅進んだ駅の名前は？", st[63]["name"], "text"),
        ("q9", f"{st[20]['name']}駅と{st[150]['name']}駅のうち、開業が早いのはどちら？（駅名のみ）",
         min((st[20], st[150]), key=lambda s: s["year"])["name"], "text"),
        ("q10", "霧ヶ峰口駅の名物は？資料に書かれていなければ「記載なし」と答えて。", "記載なし", "text"),
    ]
    assert st[20]["year"] != st[150]["year"]
    return doc, q


# ---------------------------------------------------------------- A7 指示追従
A7 = [
    ("i01", "秋の味覚を5つ、箇条書きで書いて。各行は「- 」で始め、項目は10字以内。箇条書き以外の文は一切書かないこと。"),
    ("i02", "家庭でローカルLLMを動かす利点を説明して。ただし「プライバシー」「無料」という語は使わないこと。150字以上200字以内。"),
    ("i03", "「雪」「駅」「灯り」の3語を、この順番で必ず含む一文を作って。句点「。」で終わる一文だけを出力すること。"),
    ("i04", "週末の過ごし方について、です・ます調でちょうど3文書いて。最後の文は「？」で終わる疑問文にすること。"),
    ("i05", '温泉旅行を題材に、{"title": 文字列, "tags": 文字列3個の配列, "score": 1から5の整数} の形の JSON だけを出力して。'),
    ("i06", "次の文の「さくら」をすべてカタカナに変え、それ以外は一字も変えずに出力して。\nさくら色の道で、さくらの花びらが舞う。"),
    ("i07", "1から30までの素数だけを、小さい順にカンマ区切りで1行で出力して。説明は不要。"),
    ("i08", "各行の最初の文字が順に「あ」「き」「ば」になる、3行の短い詩を書いて。詩以外は出力しないこと。"),
    ("i09", "「東京は日本の首都です。」を英語に翻訳し、すべて小文字で出力して。翻訳文だけを出力すること。"),
    ("i10", "ちょうど50文字で自己紹介を書いて。句読点も1文字と数え、改行や空白は入れないこと。自己紹介文だけを出力すること。"),
]

# ---------------------------------------------------------------- A8 ツール呼び出し
A8_SYSTEM = "あなたはアシスタントです。今日は2026-10-27（火）です。必要なときだけツールを使ってください。"
A8_TOOLS = [
    {"type": "function", "function": {"name": "get_weather", "description": "指定した都市と日付の天気予報を返す",
     "parameters": {"type": "object", "properties": {"city": {"type": "string", "description": "都市名（例: 札幌）"},
                                                     "date": {"type": "string", "description": "YYYY-MM-DD"}},
                    "required": ["city", "date"]}}},
    {"type": "function", "function": {"name": "convert_currency", "description": "金額を別の通貨に換算する",
     "parameters": {"type": "object", "properties": {"amount": {"type": "number"},
                                                     "from_currency": {"type": "string", "description": "ISO 4217 コード（例: USD）"},
                                                     "to_currency": {"type": "string", "description": "ISO 4217 コード（例: JPY）"}},
                    "required": ["amount", "from_currency", "to_currency"]}}},
    {"type": "function", "function": {"name": "search_train", "description": "電車の時刻を検索する",
     "parameters": {"type": "object", "properties": {"from_station": {"type": "string", "description": "出発駅（「駅」は付けない）"},
                                                     "to_station": {"type": "string", "description": "到着駅（「駅」は付けない）"},
                                                     "departure_time": {"type": "string", "description": "HH:MM 以降を検索"}},
                    "required": ["from_station", "to_station", "departure_time"]}}},
    {"type": "function", "function": {"name": "calculator", "description": "数式を計算する（+ - * / と括弧）",
     "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}}},
]
# 正解: 呼ぶべき関数の一覧（順不同）。引数は「キー: 受け付ける値のリスト」。空リスト = ツールを呼ばないのが正解
A8 = [
    ("t01", "明日の札幌の天気は？", [("get_weather", {"city": ["札幌", "札幌市"], "date": ["2026-10-28"]})]),
    ("t02", "100ドルは日本円でいくら？", [("convert_currency", {"amount": [100], "from_currency": ["USD"], "to_currency": ["JPY"]})]),
    ("t03", "こんにちは！今日もよろしくね。", []),
    ("t04", "東京と大阪の今日の天気を教えて。", [("get_weather", {"city": ["東京", "東京都"], "date": ["2026-10-27"]}),
                                          ("get_weather", {"city": ["大阪", "大阪市", "大阪府"], "date": ["2026-10-27"]})]),
    ("t05", "新潟駅から長岡駅まで、18時以降の電車を調べて。", [("search_train", {"from_station": ["新潟"], "to_station": ["長岡"],
                                                                    "departure_time": ["18:00"]})]),
    ("t06", "(1234+5678)×3 を計算して。", [("calculator", {"expression": ["*eval*20736"]})]),
    ("t07", "1万5千円を米ドルにするといくら？", [("convert_currency", {"amount": [15000], "from_currency": ["JPY"], "to_currency": ["USD"]})]),
    ("t08", "Python でリストを逆順にする方法を教えて。", []),
]
