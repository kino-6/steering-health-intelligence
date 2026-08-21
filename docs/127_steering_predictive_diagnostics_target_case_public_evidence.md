# Target Case Public Evidence Check

## 結論

SPD008のターゲットケース「**permanent DTCが残らない、断続的なassist低下**」は、公開情報(NHTSAリコール文書、ODI調査、TSB、公開整備情報)で**実在が確認できた**。

最も強い証拠は、Ford EPASリコール15V-340の是正手順そのものである。
ディーラーはまずPSCM(操舵制御モジュール)のDTCを点検し、**DTCがあれば steering gear交換、DTCがなければソフト更新のみ**、という2経路の是正が公式に定義されている。
つまり「症状(断続的なassist喪失)は起きたが、故障コードが残っていない車両」という母集団が、リコール是正の設計に組み込まれるほど大量に、公式に存在した。

さらに、通信入力妥当性(docs/124)側にも公開実例があった。
GMのTSB 17-NA-158は、「Steering Assist Reduced」警告の原因が操舵系ではなく、**ECMからの無効な冷却水温signal**だったと明記している。外部signalのvalidity起因で操舵側警告が出て、serviceが混乱するという docs/124 の想定は、公開TSBで裏付けられた。

この確認により、SPD008の市場需要側は公開情報だけで1段補強された。
判定ゲート(docs/122)そのものは内部資料条件のまま変わらない。

詳細表は [data/steering_predictive_diagnostics_target_case_public_evidence.tsv](../data/steering_predictive_diagnostics_target_case_public_evidence.tsv) に置く。

## 何を判断しているか

判断しているのは、次の1点である。

> SPD008が価値仮説の対象にしている「故障コードが残らない機能低下」は、実際の市場で起きているのか。それとも、既存のDTC設計で実務上は足りていて、想定ケースが机上の空論なのか。

これは [docs/123](123_steering_predictive_diagnostics_power_monitor_program_question_sheet.md) で内部資料条件に置いた判定ゲートとは独立に、公開情報だけで確認できる市場需要側の検証である。

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Steering Predictive Diagnostics Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

確認結果:

- 市場需要(故障コードなしの機能低下が実在し、切り分けに困っている)を、公開一次情報(リコール文書、TSB)で確認している
- 公開事例は市場需要と痛みの実在を示す材料であり、SPD008の商品価値の証明には使わない
- 内部資料は使っていない
- 特定OEM・特定車種の設計優劣の断定には使わない(禁止主張に準じる扱い)
- 故障予測、交換時期、root cause断定は主張していない

## 公開証拠

### 証拠1: Ford EPASリコール15V-340(2015) — 「DTCなし」経路が是正手順に公式に存在する

- 対象: Ford Fusion / Lincoln MKZ等のEPAS(電動パワーステアリング)
- 原因(公式): steering gear motor内のribbon cable pinずれとconformal coat汚染による**断続的な電気接続不良**。motor position sensor signalが失われ得る
- 是正手順(公式): PSCMのDTCを点検し、(1) loss of steering assist系DTCがあればsteering gear交換、(2) **DTCがなければPSCMソフト更新のみ**
- SPDへの意味: 「症状はあったがDTCが残っていない」車両群が公式是正の1経路になるほど存在した。DTCの有無がservice判断を分岐させる実務が、公開文書で確認できる

### 証拠2: GMリコール17V-414 / 18V-586(2017-2018) — 短時間の喪失と突然の復帰

- 対象: Silverado / Sierra / Tahoe / Suburban / Escalade等
- 現象(公式): **低速旋回中に一時的にEPS assistを喪失し、約1秒以内に突然復帰する**。電気/ソフト起因
- SPDへの意味: [docs/121](121_steering_predictive_diagnostics_power_monitor_case.md) のケース定義(低速取り回し中の一時的assist limitation、短時間の不安定)とほぼ同型の現象が、リコール規模で公式に記述されている

### 証拠3: GM TSB 17-NA-158 — 外部signal validity起因の操舵警告(docs/124の実例)

- 現象: 「Steering Assist Reduced, Drive With Care」警告
- 原因(TSB): 操舵系の故障ではなく、**ECMからの無効な冷却水温signal**
- SPDへの意味: EPSが依存する外部signalのvalidity起因で操舵側警告が出る事例が公開TSBに存在する。「操舵の警告=操舵の故障」とservice側が短絡する痛み(docs/124のMarket Demand 3)の実例

### 証拠4: 公開整備情報 — PSCMの電圧感受性とservice混乱

- 公開整備情報では、「Steering Assist Reduced」系警告の頻出原因として低いバッテリー電圧・オルタネータ劣化が繰り返し挙げられ、PSCMが電圧変動に敏感であることが常識として流通している
- SPDへの意味: reduced assistの近傍で電源contextを確認したいという診断価値(docs/121)は、aftermarket側でも既に痛みとして認知されている。ただしこれは二次情報であり、confidenceは中

### 証拠5: Tesla EA24001 / リコール25V-092(2024-2025) — 電源contextと操舵制御の公式接続

- 現象: 2023 Model 3 / Yの電動パワステ喪失
- 原因(公式): **過電圧条件が操舵制御ユニット基板の部品に過大ストレスを与える**。OTAソフト是正でODI調査クローズ
- SPDへの意味: 電源contextが操舵機能可用性に直結する因果が、最新のODI調査・リコールで公式に確認されている。power monitorという対象選定の妥当性を補強する

### 証拠6: Ram ProMaster ODI調査(2023-) — 断続的なEPS失陥の継続発生

- 現象: 2022-2023 ProMasterのpower steering assistの断続的または完全な失陥。EPS制御モジュールコネクタへの水侵入の指摘を含む
- SPDへの意味: 断続的なassist失陥は現行世代でも発生し続けており、過去世代固有の問題ではない

## 判定

ターゲットケースの実在: **確認できた(Confirmed)**

- 「DTCが残らない症状群」の存在は、リコール是正手順という最も硬い公開一次情報で確認できた(証拠1)
- 「短時間の喪失・復帰」「低速旋回中」というケース定義の形も公式文書と一致した(証拠2)
- 電源context(証拠4、5)と依存signal validity(証拠3)という2サンプルの選定も、それぞれ公開実例を持つ

ただし、次の限界を明記する。

1. 公開事例が示すのは**痛みの実在**であり、SPD008 payloadの**商品価値の証明ではない**。「その状態説明に金を払う部署がいるか」は判定ゲート(内部資料条件)のまま
2. 証拠1、2、5はいずれも「最終的に原因が特定されリコールに至った」ケースである。SPD008が狙う「原因未確定段階の状態説明」の価値は、リコールに至る前の切り分け期間の短縮として説明する必要がある
3. 特定OEMの設計優劣の話ではない。EPS共通のpain familyとして扱う

## EPSサプライヤとしての言い方

言ってよいこと:

> 公開されたリコール是正手順やTSBには、「症状はあるがDTCが残っていない」経路や、外部signal起因の操舵警告が公式に存在する。EPS共通の実務として、DTC未満の機能影響contextを部品側で説明できる価値の需要は実在する。

言ってはいけないこと:

> このリコールはSPD008があれば防げた。

> 特定OEMの診断設計が劣っている。

> EPSの故障を予測できる。root causeを断定できる。

## 次の作業

1. 公開情報のみで進められるSPD本線の検証は、本ドキュメントでほぼ出し切った。以後のSPD本線は、内部資料条件(docs/123の照合、docs/126のKQ1/KQ2)が満たされるまで**実施条件待ち**に置く
2. ついで観測として、SOTIF運用フェーズ要求が部品サプライヤへ降り始めているかの公開動向(docs/126)を、他の公開情報確認の機会に見る
3. 本ドキュメントの証拠1〜6は、将来のサプライヤ内提案時に「市場需要の公開裏付け」として docs/122 payload とセットで使う

## Sources

- [Ford Part 573 Safety Recall Report 15V-340](https://static.nhtsa.gov/odi/rcl/2015/RCLRPT-15V340-7526.PDF): EPAS断続接続不良、DTC有無による2経路是正
- [Ford Safety Recall 15S18 dealer bulletin](https://static.nhtsa.gov/odi/rcl/2015/RCMN-15V340-8835.pdf): 是正手順詳細
- [Ford PE14-030 (2010 Fusion EPS) ODI resume](https://static.nhtsa.gov/odi/inv/2014/INCLA-PE14030-7526.PDF): 先行するODI調査
- [GM Product Safety Recall 17276 (17V-414) Loss of Steering Assist](https://static.nhtsa.gov/odi/rcl/2017/RCSB-17V414-6829.pdf): 低速旋回中の一時喪失・約1秒での突然復帰
- [GM Product Safety Recall 18289 (18V-586) Loss of Steering Assist](https://static.nhtsa.gov/odi/rcl/2018/RCSB-18V586-2540.pdf): 同型の後続リコール
- [GM TSB 17-NA-158 解説(oards.com)](https://oards.com/steering-assist-is-reduced-drive-with-care-message/): ECMからの無効な冷却水温signalによるSteering Assist Reduced警告(二次情報)
- [NHTSA closes Tesla power-steering investigation EA24001(The EV Report)](https://theevreport.com/nhtsa-closes-tesla-power-steering-investigation): 過電圧条件による操舵制御ユニット過大ストレス、OTA是正(二次情報)
- [Ram ProMaster power steering ODI調査報道(autoevolution)](https://www.autoevolution.com/news/nhtsa-investigates-ram-promaster-vans-over-power-steering-assist-system-failure-allegations-266649.html): 断続的EPS失陥の継続発生(二次情報)
- [FCA recall 16V-167 dealer document](https://static.nhtsa.gov/odi/rcl/2016/RCRIT-16V167-0768.pdf): EPS基板汚染による断続的または恒久的なassist喪失
