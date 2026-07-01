# 19. Market Research: EPS Event Context Memory

## Purpose

前回の結論では、`EPS / ECU embedded evidence` という言い方が抽象的すぎた。

ここでは、EPSサプライヤ視点に戻し、次の問いだけを見る。

> EPS ECUに小さな状況証拠を残すことは、市場で誰のどんな痛みに刺さるのか。

このメモでは、これを仮に `EPS Event Context Memory` と呼ぶ。

## Short Conclusion

現時点の結論:

> 市場が直接買っているのは「EPSの劣化兆候」ではなく、保証解析、No Trouble Found、返却品解析、supplier quality、顧客品質報告、原因調査の業務改善である。

したがって、`EPS Event Context Memory` は単独商品では弱い。

追加の現実確認:

> ECU内に証跡を残すこと自体は新しくない。DTC、freeze frame / snapshot、extended data、event memory、occurrence counter、aging counter、NvM保存、UDS ReadDTCInformation、AUTOSAR DEMなどは既存診断の範囲にある。

そのため、`EPS Event Context Memory` を「内蔵証跡を実装する新機能」として語るのは筋が悪い。
価値があるとすれば、既存診断データを、EPSサプライヤの返却品解析、NTF、顧客品質報告、D2 / D4向けの事実整理に使えるように設計・棚卸し・改善提案することに限られる。

ただし、次の形なら筋が残る。

> DTCだけでは説明できない市場不具合・返却品・NTF案件に対して、既存診断データと追加候補を棚卸しし、品質保証チームの初動判断、OEM説明、顧客品質報告、原因調査を支援する。

つまり売り物は「故障予測」ではなく、以下に近い。

- EPS Field Event Evidence Set
- EPS Return-Part Context Memory
- EPS Warranty Investigation Evidence
- EPS Customer Quality Evidence Payload

## Market Signals

### 1. NTF and returned parts are a real pain

AIAGのWarranty Key Termsでは、NTFは交換された部品・システム・モジュールに対して、十分な不具合再現や診断データが得られない場合に付く扱いとして整理されている。

Ubiquiti / Continentalのwarranty analytics資料でも、明らかに怪しい部品が交換されてもroot causeが解けず、返却品プログラムでNTFになる問題が説明されている。

Implication:

EPSサプライヤにとって一番自然な価値は、`故障予測` ではなく、`返却品が正常に見えるときに車両上で何が起きていたかを少しでも説明する` こと。

### 2. Warranty analytics vendors sell data unification and root-cause support

AWMは、field claims、returned parts、dealer narratives、vehicle diagnosticsを使ったwarranty data analysisやNTF investigationを打ち出している。

Ubiquitiの資料では、claims、narratives、returned part analysisなど複数データを統合し、root causeやearly warningに使う流れが示されている。

Implication:

EPS ECUの中だけで完結する価値は小さい。
しかし、warranty analytics workflowに入る追加データとしてなら価値が出る。

### 3. Supplier quality / 8D / SCAR tools already have buyer budget

Suppliosはsupplier claims、CAPA、8D、SCAR、CoQ / CoPQ、supplier chargebackを扱っている。
RcallsもAutomotive向けにsupplier quality、defect tracking、root cause、CAPA、OEM claims managementを打ち出している。

Implication:

品質部門は「証拠をそろえて、原因仮説と是正処置を通す」業務に予算を持っている。
ただし、`8D回答を自動化する` という言い方は危ない。
EPS Event Context Memoryは、原因を断定するものではなく、顧客品質報告、返却品解析報告、NTF調査メモ、D2 / D4向けの事実整理に入る証拠材料として定義するのが現実的。

### 4. Remote diagnostics is a channel, not the core buyer pain

Connected vehicle / remote diagnostics / OTA系の市場は大きいが、EPSサプライヤ起点ではOEM platform依存が強い。

Implication:

OTAやクラウドを前提にしない。
まずは、返却品解析やOEM回答時に診断ツール・サービスツール・開発者ツールで読める小さな証跡として考える。

### 5. Case-level missing evidence was not visible from market research

市場調査から見えたのは、NTF、返却品解析、warranty analytics、supplier qualityに痛みがあるという業務レベルの事実である。

一方で、次は公開情報からは見えなかった。

- EPS返却品で実際に多いNTFパターン
- DTCだけで解析不能だった実例
- freeze frame / extended dataに何が入っていて、何が足りないか
- 電源、熱、センサ、制御努力、使用条件、一過性異常のどれが本当に効くか
- NVM制約内で何を残すと解析価値が最大か

ここは外部市場調査ではなく、EPSサプライヤ内部の過去案件レビューが必要。

## Who Cares

### Stronger buyers

| Buyer / user | Why they care | What EPS evidence helps with |
|---|---|---|
| EPS supplier warranty team | NTF、保証費、返却品解析に困る | DTCだけでは不足する発生時文脈を補う |
| EPS supplier customer quality team | OEMへの顧客品質報告・原因調査説明が必要 | 初動仮説、調査方針、確認済み事実・未確認事項を整理する |
| EPS diagnostic engineering | DTC / freeze frame / extended dataの仕様責任を持つ | 量産診断仕様を市場解析に使える形へ改善する |
| EPS supplier recovery / commercial quality | chargebackや責任分界の説明が必要 | 「部品単体不良か、周辺条件か」の議論材料を増やす |

### Weaker buyers

| Buyer / user | Why weak |
|---|---|
| EPS development evaluation team | 開発時は外付け計測、HILS、ベンチログの方が強い |
| Gear / rack design team | ECU信号だけでは機械要因を分離しにくい |
| OEM fleet analytics team | 初期から狙うにはOEMデータ依存が大きい |
| End user / dealer | 誤通知責任、説明責任、サービス運用が重い |

## What The Product Actually Is

`EPS Event Context Memory` は、劣化判定器ではない。

量産ECU内に、次のような低容量の状況証拠を残す仕組みである。

| Evidence | Example | Why useful |
|---|---|---|
| Event snapshot | latest relevant event, ignition cycle, mileage bucket | いつ・どんな状況で起きたかの足場 |
| Voltage context | min voltage, low-voltage count, reset / brownout context | 電源起因・周辺条件の切り分け |
| Thermal context | thermal derating count, max temperature bucket | 熱ストレスや保護制御の履歴 |
| Control effort context | current tracking warning, assist limitation, torque/current mismatch bucket | 制御が苦しかった状況の証拠 |
| Sensor plausibility context | torque sensor delta, angle sensor delta, intermittent plausibility warning | 一時的なセンサ違和感の履歴 |
| Missing-data marker | overwritten, not captured, low confidence | 証拠の限界を明示する |

ポイントは、原因を断定しないこと。

出力するのは次の粒度に抑える。

- `部品単体不良の証拠あり`
- `電源・熱・周辺条件の影響を疑う`
- `再現待ち・追加調査が必要`
- `DTCは弱いが、過去に制御努力が増えた証跡あり`
- `証拠不足のため断定不可`

## Why This Is Different From Just More Logs

単にログを増やすだけなら付加価値は弱い。

また、DTC、freeze frame、extended data、event memoryは既存診断に含まれるため、`内蔵証跡` というだけでは新規性がない。

差分を作るなら、次の3つを設計支援として持つこと。

1. Warranty / NTF / 顧客品質報告で読む前提の項目だけを残す
2. 断定ではなく、調査方針と説明材料に変換する
3. NVM制約を前提に、少数の高価値カウンタとイベントスナップショットに絞る

つまり、`データ量` ではなく `品質保証で使える証拠設計` が価値。

ただし、この価値はOEM領分に半分入る。
OEMの診断仕様、サービスツール、保証DB、市場品質ワークフローをサプライヤ単独で変えることはできない。
サプライヤ側の現実的な持ち物は、過去案件から作った不足証跡仮説、現行診断データの棚卸し、NVM制約内の最小追加案、顧客品質報告に使う事実整理テンプレートである。

## Business Model Fit

### Best near-term package

> EPS Warranty Evidence Option

内容:

- NVM event context design
- Diagnostic readout definition
- Evidence summary format
- Customer quality / D2-D4 fact summary template
- Validation plan for returned-part / NTF cases

買い方:

- EPSソフト・診断仕様のNRE
- OEM向け品質改善提案の一部
- 次世代EPS platformの診断オプション
- 保証費・NTF低減プロジェクトのPoC

### Not recommended as first product

- 個車別の故障予測サービス
- End-user向け劣化通知
- OTA前提のクラウド診断サービス
- 外付け開発モニタ代替

## Validation Questions

この仮説はまだ市場調査ベースで、成立性は以下に依存する。

1. EPS返却品でNTFや再現不能はどれくらいあるか
2. そのうちDTC / freeze frame不足が原因で解析が止まる割合はどれくらいか
3. OEMへの顧客品質報告や原因調査で、EPSサプライヤが追加証拠を求められる頻度はどれくらいか
4. 現行ECUのNVMで、何バイト程度なら現実的に確保できるか
5. 読み出し経路は、工場、ディーラー、返却品解析、開発ツールのどれが現実的か
6. 証拠が増えることで、保証費、解析工数、回答リードタイム、chargebackのどれが減るか
7. OEMに聞く前に、サプライヤ側で20-50件の返却品・NTF・再現不能案件を分類できるか

## Research Verdict

筋は、前の `劣化兆候` より良い。

ただし、強い事業にするには言い方を絞るべき。

悪い言い方:

> EPSの劣化兆候を予測して通知します。

良い言い方:

> EPS市場不具合・返却品・NTF案件で、DTCだけでは説明できない発生時文脈を既存診断データと追加候補から整理し、品質保証チームの顧客品質報告と原因調査を支援します。

最初に作るべきデモ:

> DTCだけの返却品解析 vs 不足証跡仮説と追加証跡候補ありの返却品解析

このデモで示すべき差分:

- 初動仮説が立つか
- 調査すべき方向が絞れるか
- 顧客品質報告に使えるか
- `断定不可` を正直に言えるか
- 追加取得すべきデータが明確になるか

## Boundary After Reality Check

OEMに丸投げする順番は悪い。

悪い順番:

> OEMに何が欲しいか聞く -> 言われたものを検討する

良い順番:

> 自社のNTF / 返却品で困った事例を整理する -> 足りない証跡を仮説化する -> 最小実装案を作る -> OEMに「この証跡があるとこのケースの説明が改善するが、診断仕様に入れる価値はあるか」と聞く

つまり、ヒアリングの目的はニーズ探索ではなく、サプライヤ側で作った仮説の検証にする。

## Sources

- AIAG, `Automotive Warranty Management Key Terms`: https://aiag.org/docs/default-source/quality/aiag-cqi-14-warranty-key-terms.pdf
- AIAG, `Global Automotive Warranty Report`: https://www.aiag.org/docs/default-source/Quality-/global_auto_wrnty_rpt.pdf
- AIAG blog, `Addressing No Trouble Found via Data Analysis`: https://blog.aiag.org/addressing-no-trouble-found-via-data-analysis
- AWM Warranty Data Analysis: https://www.awm-warranty-management.com/services/warranty-data-analysis/
- Ubiquiti / Continental, `Warranty Data Analytics`: https://www.ubiquiti.com/ubiquiti-cd-visible/ContiCorp_Ubq_Paper_WCM09.pdf
- Supplios Supplier Quality: https://www.supplios.com/features/supplier-quality
- Rcalls Automotive: https://www.rcalls.com/automotive/
- CLEPA Warranty Guidelines: https://www.clepa.eu/insights-updates/publications/warranty-guidelines/
- AUTOSAR Diagnostic Event Manager: https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticEventManager.pdf
- UDS ReadDTCInformation overview: https://uds.readthedocs.io/en/stable/pages/knowledge_base/service.html
