# EPS Common Pain Productization Scan

## 結論

`RCA / 8D Evidence Case Pack` を主商品にするのは弱い。
理由は、ユーザ指摘の通り、要求データが製品/OEM/診断仕様/案件に強く依存し、スケールしにくいからである。

市場のEPS共通項から見ると、次に残すべき方向はこれ。

> **EPS Diagnostic / Robustness Coverage Benchmark**

これは、個別RCAや8Dを作る商品ではない。
公開市場で繰り返し出るEPS pain familyに対して、対象EPSの既存DTC、freeze frame、extended data、reader、評価/HILS/benchが、どこまで説明・再現・検証できるかをベンチマークする商品である。

RCA/8Dは、このbenchmarkの副次用途に下げる。

## 市場需要

公開EPS caseを見ると、痛みは個別OEM固有ではなく、いくつかの共通familyに集約できる。

代表的な共通family:

| Family | Driver-visible pain | Public signal |
|---|---|---|
| low-speed high effort | 低速時の操舵力増加、assist loss | GM/Saturn IONなどのODI investigation |
| warning plus effort | EPS lamp / MIL / DTCと操舵力増加 | GM、Chrysler TSB/recall |
| intermittent ignition cycle | 再始動で復帰するassist loss | Cadillac/Camaro/Corvette recall |
| voltage / temperature / friction | 低/高電圧、高温、高摩擦など既存DTC文脈 | Ford Fusion/MKZ/Milan ODI investigation |
| stop-start low-speed | 停止後発進や低速旋回でassist loss | Tesla Model 3/Y public recall reports |
| software / failsafe calibration | calibration不備によるfailsafe/assist loss | Acura RDX recall |
| gradual-turn sticking | 緩い旋回中のsticking、assist復帰 | Chrysler Pacifica ODI investigation |
| MDPS / ECU hardware | PCB、short/open、MDPS power pack不具合 | Hyundai/Kia/Mando recalls |

参照:

- NHTSA Electric Power Steering Safety Report: https://www.nhtsa.gov/sites/nhtsa.gov/files/documents/13501_812575_electricpowersteeringreport.pdf
- GM Saturn ION EPS investigation: https://static.nhtsa.gov/odi/inv/2011/INCLA-EA11014-3103.PDF
- Ford Fusion EPAS investigation: https://static.nhtsa.gov/odi/inv/2014/INCLA-PE14030-7526.PDF
- Chrysler Pacifica EPS investigation: https://static.nhtsa.gov/odi/inv/2025/INOA-PE25009-18789.pdf
- Tesla steering assist recall report example: https://www.wardsauto.com/news/archive-auto-tesla-recalls-376k-vehicles-loss-power-steering-assist-nhtsa-modelY-model3/741051/

## 未解決の痛み

ここでの未解決の痛みは、`RCA/8D回答を作ること` ではない。

より上流の痛みはこれ。

> 市場で繰り返し問題化するEPS共通scenarioに対して、サプライヤEPSの既存診断・評価・HILS・readerがどこまで説明できるかを、プログラム横断で比較できない。

この痛みなら、EPSサプライヤ視点に戻せる。

- OEM保証DBを初期前提にしない
- 個別8D様式に依存しない
- 既存診断との差分を確認できる
- 複数プログラム/複数世代に横展開しやすい
- 必要なら顧客品質報告/RCA/8Dにも副次利用できる

## 仮説

新しい仮説は以下。

> EPSサプライヤは、公開市場で繰り返すEPS pain familyをベースに、対象EPSの診断coverage、評価coverage、HILS/bench再現性、reader/readout coverageをベンチマークする短期assessmentを提供できる。

この仮説なら、個別case packよりスケールしやすい。

## 解決策

### Primary Offer

> **EPS Diagnostic / Robustness Coverage Benchmark**

成果物:

| Artifact | 内容 |
|---|---|
| Public EPS pain taxonomy | 公開caseを共通scenario familyに分類 |
| Diagnostic coverage matrix | DTC / freeze frame / extended data / readerが各scenarioを説明できるか |
| Robustness scenario checklist | HILS / bench / vehicle evaluationで再現すべきscenario |
| Existing sufficiency / gap table | 現行診断で足りる、足りない、不要を分ける |
| Program comparison view | 複数EPS program / generation間のcoverage差分 |
| Optional quality attachment | RCA/8D/顧客品質報告に転記できるfact summary |

### Not Core

以下は主商品にしない。

- 個別RCA代行
- 8D自動生成
- ECUログ追加単体
- 故障予測/RUL
- エンドユーザ通知
- OEM fleet analytics

## 買い手/利用者

| Role | 嬉しいこと |
|---|---|
| Diagnostic engineering | 市場で問題化するscenarioに対して、現行DTC/freeze frameが十分か比較できる |
| Validation / HILS / bench | 公開市場痛みを評価scenarioに変換できる |
| Customer quality | 問題化した時に、どのfactが既に説明可能かを把握できる |
| Platform / program management | 複数program間で診断coverageの差を説明できる |

初期buyerは、品質単独よりも `diagnostic engineering + validation + customer quality` の横断に置く方が自然。

## スコア結果

30件の公開caseを代表サンプルとして再分類し、13 familyをスコアリングした。
評価軸は以下。

- commonality: 複数車種/OEM/年式へ横展開しやすいか
- supplier_control: EPSサプライヤ側でデータ/評価/診断を扱えるか
- differentiation: 既存診断や一般8Dとの差分があるか
- scalability: 個別案件で終わらず、program横断で使えるか

上位候補:

| Rank | Family | Candidate | Score | Verdict |
|---:|---|---|---:|---|
| 1 | FAM08 stop-start low-speed | Stop-Start Low-Speed Robustness Benchmark | 17 | Primary |
| 2 | FAM11 software/failsafe calibration | Software/Failsafe Coverage Benchmark | 17 | Primary |
| 3 | FAM02 low-speed high-effort | EPS Diagnostic Coverage Benchmark | 16 | Primary |
| 4 | FAM03 warning plus effort | DTC-to-Driver Symptom Coverage Benchmark | 16 | Primary |
| 5 | FAM12 gradual-turn sticking | Context-Specific EPS Control Coverage Benchmark | 16 | Primary-risky |

下位候補:

| Family | 理由 |
|---|---|
| FAM10 harness/mechanical turn | 機械/ハーネス側の物理原因に寄り、ECU単体では説明しにくい |
| FAM13 mechanical worm gear | ギア固有で、gear maker/program NREに寄りやすい |
| FAM07 road event | 路面/IMU/車両文脈が必要で、OEM依存が強い |

## 事業候補

### 1. EPS Diagnostic Coverage Benchmark

市場で繰り返すEPS scenario familyに対し、対象EPSの既存DTC/freeze frame/extended data/readerで説明できるかを見る。

これは最も自然。
`ログ追加` ではなく、まず既存診断で十分かを明らかにする。

初期demo:

- FAM02 low-speed high-effort
- FAM03 warning plus effort
- FAM05 voltage/temperature/friction

Kill条件:

- 現行診断仕様書を見ると既に十分にcoverageされている
- 診断設計部門が既に同等のcoverage reviewを持っている
- program横断の比較に使えない

### 2. EPS Robustness Scenario Library

市場で問題化しやすいEPS共通scenarioを、HILS/bench/vehicle evaluationの入力に変換する。

これはRCA/8Dより上流で、validationに刺さる可能性がある。

初期demo:

- FAM08 stop-start low-speed
- FAM11 software/failsafe calibration
- FAM12 gradual-turn sticking

Kill条件:

- 既存評価項目と差分がない
- 公開caseから評価条件に落とせない
- 実車/OEM文脈がないと再現不能

### 3. DTC-to-Driver Symptom Coverage Matrix

DTC、warning、freeze frameが、driver-visible painや顧客品質説明にどう接続されるかを整理する。

これはRCA/8Dに近いが、個別caseではなくcoverage matrixにすれば多少スケールする。

Kill条件:

- DTC documentationに既にdriver symptom / context / quality wordingが入っている
- 品質部門が既に運用している
- 顧客品質報告に使えない

## RCA/8D案の扱い

RCA/8Dは主商品から下げる。

修正後の位置づけ:

> Coverage Benchmarkの結果を、必要に応じて顧客品質報告や8D D2-D4に転記できるようにする副次artifact。

これなら、RCA/8Dがドメイン固有でスケールしない問題を少し避けられる。

ただし、RCA/8D用途しか残らないなら、この方向はKillでよい。

## Chain-of-Verification

| Question | Evidence check | Confidence | Impact |
|---|---|---:|---|
| EPS市場に共通pain familyはあるか | NHTSA EPS report、ODI investigations、recall/TSBからloss of assist、warning+effort、low-speed effort、intermittent、software/failsafe、ECU hardwareなどが繰り返し見える。 | High | Keep |
| RCA/8D case packはスケールするか | 要求データがDTC仕様、reader、OEM、案件に強く依存する。 | High | 主商品から下げる |
| EPSサプライヤが主語になれるか | 診断coverage、評価/HILS、calibration/failsafe、DTC semanticsはサプライヤ側の手札。 | Medium-High | Coverage Benchmarkへ修正 |
| 既存診断との差分はあるか | Ford事例などは既に多数のDTC文脈を示す。差分は追加ログではなくcoverage比較/説明可能性に限る。 | Medium | 新規ログ主張を外す |
| 次に何を検証するか | FAM02/FAM03/FAM08/FAM11/FAM12でcoverage matrix sampleを作れば、Proceed/Killできる。 | Medium | 次アクションを明確化 |

## EPSサプライヤとしての結論

### 売るなら

> EPS Diagnostic / Robustness Coverage Benchmark

市場で繰り返すEPS common pain familyに対し、対象EPSの既存診断・評価・HILS・readerがどこまでcoverageできるかを短期assessmentする。

### やる

- 公開caseをscenario family化する
- DTC/freeze frame/extended data/reader coverageを棚卸しする
- HILS/bench/vehicle evaluationで再現すべきscenarioに変換する
- 複数program間でcoverage差分を見る
- 必要に応じて顧客品質/RCA/8D向けfact summaryへ転記する

### やらない

- 個別RCA代行を主商品にする
- 8D自動生成を売る
- 故障予測/RULを主張する
- ECUログ追加を最初から売る
- OEM fleet analyticsを初期前提にする

### 次アクション

次は `FAM08 stop-start low-speed` または `FAM02 low-speed high-effort` のどちらかで、1ページのcoverage benchmark sampleを作る。

サンプルに入れるもの:

- market pain
- driver-visible symptom
- expected EPS facts
- existing DTC/freeze frame/extended data coverage欄
- HILS/bench/vehicle evaluation scenario
- already covered / gap / no action decision
- customer quality/RCAに転記できる副次summary

このsampleが診断設計/評価部門に刺さらなければ、RCA/8D派生も含めてKillでよい。
