# 212. 断続故障はどんな条件で起きると報告されているか — 事前登録

**結果を1つも見る前に書き、単独でコミットする。**

## なぜこれをやるか

[docs/188](188_the_line.md) の売り物は一文である。

> **再現しない故障のとき、その瞬間に部品の中で何が起きていたかを、宣言した粒度で出せる。**

**「その瞬間を捕まえる」ためには、いつ記録を始めるかを決めなければならない。**
これが最初の設計問題であり、**本研究はまだ何も答えを持っていない。**

一方、[docs/185](185_misdiagnosis_quantified.md) / [docs/187](187_replacement_no_fix_result.md) は
NHTSA苦情本文を使ったが、**特定の語の出現率を数えただけ**である
(`intermittent`、`no fault found`、`replaced ... still`)。
**故障が「どんな条件で起きたか」は一度も読んでいない。**

苦情本文は約1.5 GB、EPS系の苦情は8,005件ある([docs/187](187_replacement_no_fix_result.md))。
**そこに書かれている発生条件が、トリガ設計の唯一の公開証拠である。**

## 何を取り出すか(実行前に固定)

対象: NHTSA FLAT_CMPL のうち、部品名に操舵系を含み、**かつ**本文が断続を示す語を含む苦情。
断続を示す語は [docs/187](187_replacement_no_fix_result.md) で固定済みのものを流用する:
`intermittent(ly)` / `comes and goes` / `on and off` / `sporadic` / `randomly` / `at times`。**変更しない。**

各苦情本文から、以下の条件カテゴリの言及を数える。**語のリストをここで確定する。**

| カテゴリ | 判定語 |
|---|---|
| **速度: 低速・駐車** | parking, low speed, slow speed, backing, reverse, u-turn, stop light, standstill |
| **速度: 高速** | highway, freeway, high speed, interstate, merging |
| **温度: 冷間** | cold, cold start, morning, first start, winter, freezing |
| **温度: 高温** | hot, heat, summer, after driving, warmed up, long drive |
| **始動時** | start up, starting the, ignition, turn the key, first start |
| **路面・振動** | bump, pothole, rough road, railroad, uneven |
| **操舵中** | turning, while turning, cornering, curve, lock to lock |
| **雨・湿気** | rain, wet, humid, moisture, car wash, puddle |
| **持続時間: 瞬間** | momentar, a second, briefly, instant, split second |
| **持続時間: 再始動で復帰** | restart, turn off and, cycle the ignition, reset itself |

**同じ苦情が複数のカテゴリに入ってよい。**単位は苦情(ODINO)であり行ではない
([docs/187](187_replacement_no_fix_result.md) で修正したOR集約の誤りを繰り返さない)。

## 比較の基準

**言及率だけでは意味を持たない。**「多くの苦情が bump と書いている」は、
bump という語が苦情一般に多いだけかもしれない。したがって:

```
lift = P(カテゴリC | 操舵系 かつ 断続) / P(カテゴリC | 全苦情)
```

**全苦情を分母にした持ち上がりで見る。**

## 判定基準(いま固定する)

| # | 基準 | 閾値 |
|---|---|---|
| **T1** | 各カテゴリの件数・率・lift を報告 | **閾値なし。n も併記** |
| **T2 トリガ候補** | lift ≥ 2.0 かつ 件数 ≥ 100 のカテゴリ | **満たすカテゴリを「トリガ候補」と呼ぶ。1つも無ければ「無い」と書く** |
| **T3** | 断続語を含む操舵系苦情の総数 | **報告のみ** |

- **これは言及率であって発生率ではない。**[docs/189](189_five_limits_tested.md) ④ で確定した限界を繰り返す。
  **「lift 3倍」は「3倍起きやすい」ではなく「3倍書かれやすい」である**
- 件数が100に届かないカテゴリは**倍率を語らない**
- **v2は作らない**

## 事前に認めておくこと

- **消費者の自己申告である。**販売店の診断結果でも計測でもない
- **書かれやすさの偏りがある。**印象に残る条件(高速道路、雨)は書かれやすい可能性がある
- **語の一致は文脈を見ない。**"not on the highway" も highway として数える。
  **否定形の除去はしない**(実装が恣意的になるため)。この誤差を認めたうえで使う
- **これはトリガ設計の入力であって、トリガそのものではない。**
  条件が分かっても、ECUがその条件を検出できるかは別問題である
- **米国市場のデータである**

## Rule Check

- **語のリストを実行前に全部書いた。**結果を見てカテゴリを足さない
- **言及率であって発生率でないことを、判定基準の中に書いた**
- 否定形を除去しないと決め、**その誤差を先に認めた**
- 「条件が分かる」と「ECUが検出できる」を分けた

出典: NHTSA FLAT_CMPL (S2/S3/S6, 米国連邦政府の著作物・パブリックドメイン)
