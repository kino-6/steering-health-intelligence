# Communication Input Validity Public Case Cross-Check

## 結論

[docs/129](129_steering_predictive_diagnostics_public_case_crosscheck.md) と同じ手法(公開一次文書によるケースレベル照合)を、第二候補のcommunication input validity([docs/124](124_steering_predictive_diagnostics_comm_input_validity_case.md))に適用した。

結果、判定を1段上げる:

> Communication input validityの判定を、**条件付きHold(Proceed寄り)から、公開レベルConfirmed付き限定Proceedへ引き上げる**。
> ただし順位は第二候補のまま。IdsMとの役割分担と部署の使い道確認は、power monitorと同じく実行段階の内部条件として残る。

根拠はGM TSB 17-NA-158の原文である。
このTSBは、EPSが依存する外部signal(CAN経由の冷却水温)が無効になった結果、操舵警告が出て、**直らないのにsteering gearが交換され続けた**ことをOEM自身が公式に記録している。

さらに副産物として、Ford SSM 49530(2021年F-150)の原文から、**2021年世代のprogramでもpower contextの誤帰属が続いている**ことが確認できた。これは docs/129 の限界1(「現行世代では改善済みかもしれない」)を部分的に反証し、power monitor側の判定も補強する。

詳細表は [data/steering_predictive_diagnostics_comm_validity_public_crosscheck.tsv](../data/steering_predictive_diagnostics_comm_validity_public_crosscheck.tsv) に置く。

## 何を判断しているか

docs/124の照合項目(依存signalのvalidity、fallback近接、既存DTCで足りるか)を、「サプライヤprogramでどうか」ではなく「市場に出た実車両の実務でどうだったか」で判定した。

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Steering Predictive Diagnostics Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

確認結果:

- 判定変更(Hold→限定Proceed)を公開一次文書で行った
- 特定OEMの設計批判には使わない。業界共通の実務水準として扱う
- 外部ECU原因断定、security代替、故障予測は主張していない
- IdsM役割分担という残Hold条件を消していない

## 公開一次文書から読み取れた事実

### GM TSB 17-NA-158(2017年5月、Cadillac XT5 / GMC Acadia)

原文の構造(要点):

1. 症状: 走行約20分後に「Steering Assist Reduced, Drive With Care」表示。DTCは**P0128(ECM側: 冷却水温がサーモスタット調整温度に達しない)とU0401(steering gear側: 通信data無効)**の2つ
2. 原因: **ECMからの無効な冷却水温signal**。EPSは低温時のグリス硬化を補償するため冷却水温を参照しており、CAN上の値が無効になったのでこの補償機能が停止した
3. 公式の警告: **「DTC U0401:71でpower steering gearを交換してはならない」「技術者は、steering gearが既に交換済みの車両を見つけることがある」「この交換では問題は直らない」**
4. 正しい手順: まずP0128(ECM側)を診断せよ。それが解決したらsteering gear側のU0401をクリアできる

### ここから言えること(docs/124の照合)

| docs/124の照合項目 | 公開実務での事実 | 判定 |
|---|---|---|
| invalid value DTCは残るか | **残った**(U0401:71がsteering gearに保存) | 保持はされていた |
| 残ったDTCで正しい切り分けができたか | **できなかった**。codeが保存された部品(steering gear)が犯人に見え、無駄な交換が繰り返された | **説明の穴を確認** |
| 依存signalと機能影響の関係が説明されたか | 機械には残っていない。**人間が書いたTSBが2017年5月に出て初めて説明された** | **差分あり** |
| fallback/機能低下との近接が読めたか | 読めない。P0128(ECM)とU0401(gear)を人間が結びつける必要があった | **差分あり** |
| 再発contextが使われたか | 使われていない(20分走行ごとに再現する症状にもかかわらず) | **差分あり** |

### 最も重要な発見: TSBはSPD008 payloadの「人間が後から書いた版」である

TSB 17-NA-158の内容を分解すると、[docs/122](122_steering_predictive_diagnostics_power_monitor_payload_sample.md) のminimum payloadと同じfieldになる。

| SPD008 payload field | TSB 17-NA-158が書いた内容 |
|---|---|
| observed_context | EPSが受信した冷却水温signalが無効になった |
| relation_to_function | 低温補償機能が停止し、assist低下と表示が出た |
| boundary | **操舵系の故障ではない。gearを交換するな** |
| recommended_read | まずECM側のP0128を診断せよ |

つまり、SPD008が提案しているのは新しい種類の情報ではない。
**OEMが問題発生から数千台の誤交換の後に人手で書いたservice文書を、部品側がruntimeで、機械的に、原因断定なしの状態説明として最初から出せるようにすること**である。
価値の形は公開文書そのものが証明している。

### 副産物: Ford SSM 49530(2021年F-150) — 現行世代でも誤帰属は続く

原文の構造(全文が短い):

1. 症状: 始動時にassist喪失+「Steering Assist Fault」表示。**PSCMにU3000:96とU3001:68**(component internal failure系のcode)
2. 原因: **始動時にバッテリー電圧が8V未満に低下したこと**
3. 公式の指示: **PSCM交換は不要**。電圧が12V以上に戻り、専用リセット(通常のDTC消去では消えない)を実行すれば復帰する
4. 再発したら「通常診断へ」

ここから言えること:

- **電源context(始動時電圧dip)が、部品内部故障に見えるcode(U3000:96)として保存された**。読み手には「PSCMの内部故障」に見える——誤帰属の構造がcode設計に埋まっている
- Fordは人間向けSSMで「これは電圧が原因、モジュールを交換するな」と説明する必要があった。**2021年世代でも、power contextの機械的な状態説明は存在しなかった**
- これは docs/129 の限界1「現行世代では改善済みかもしれない」への部分的な反証である(1程式の実例だが、2021年MYで同型の穴が公式記録された)

## 判定

| Sample | 変更前 | 変更後 |
|---|---|---|
| Communication input validity | 条件付きHold(Proceed寄り) | **公開レベルConfirmed付き限定Proceed(第二候補)**。残る内部条件: IdsM役割分担、部署の使い道 |
| Power monitor(補強) | 公開レベルConfirmed付き限定Proceed(実例は2011-2017世代という限界付き) | 同判定。**2021年世代の実例(SSM 49530)で限界1を部分的に解消** |

なお、docs/124のHold理由だった「依存signalの定義がOEM側に寄る」も、この照合で軽くなった。
GMケースの依存signal(冷却水温)は、EPS自身の機能(グリス硬化補償)が要求する入力であり、**EPSサプライヤが自分の機能仕様として定義できる依存**だった。依存signal listの起点は、OEMのnetwork設計ではなくEPSの機能設計に置ける。

## 限界(正直に)

1. GMケースはinvalid signalがhard DTC(P0128/U0401)として残った例である。docs/124が想定する「hard DTCに至らない断続的な揺らぎ」そのものの公開実例は、まだ複合的(苦情レベルでは多数あるが一次文書での確認はこれから)
2. IdsMとの役割分担は公開情報では判定できない(program依存)
3. 2件とも北米OEMの実例。ただしU-code/CAN validityの実務はUDS/AUTOSAR共通基盤上にある

## 次の作業

1. SPD008の2サンプルとも「公開レベルConfirmed付き限定Proceed」となった。区切り判定を書く場合の判定文はこれを使う
2. 残る内部条件(実行のみ): 現行サプライヤ設定の確認(docs/123質問シート)、IdsM役割分担、2部署以上の使い道、SOTIF KQ1
3. 公開側の残作業は「hard DTC未満の断続的揺らぎ」の一次文書実例の追加確認のみ(優先度低。苦情データの傍証はdocs/127で確認済み)

## Sources

- [GM Service Bulletin 17-NA-158(NHTSA公開原文)](https://static.nhtsa.gov/odi/tsbs/2017/MC-10137654-9999.pdf): 無効な冷却水温signalによるSteering Assist Reduced、U0401:71でのgear交換禁止、誤交換の公式記録
- [Ford SSM 49530(NHTSA公開原文)](https://static.nhtsa.gov/odi/tsbs/2021/MC-10187919-0001.pdf): 2021 F-150、始動時電圧8V未満によるU3000:96/U3001:68、PSCM交換不要、専用リセット手順
- [Ford SSM 50484(後続SSM、NHTSA公開)](https://static.nhtsa.gov/odi/tsbs/2022/MC-10208112-0001.pdf): 同型事象の継続
