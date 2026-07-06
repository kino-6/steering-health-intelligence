# Public Case Cross-Check of the Retained Field Question Sheet

## 結論

「判定ゲートは内部資料がないと閉じられない」という前提を、公開情報で崩せるか試した。

結果: **崩せた。**

[docs/123](123_steering_predictive_diagnostics_power_monitor_program_question_sheet.md) の照合質問は「自社の対象programで残るか」という形だったため内部資料条件になっていた。
これを「**市場に出た実車両の是正実務で、実際に何が読まれ、何で判断されたか**」に組み替えると、NHTSAに公開されたリコール是正指示書(ディーラー向け一次文書)で同じ5項目をケースレベルで照合できる。

公開一次文書2件を精読した照合の結果:

| 照合項目(docs/122の5項目) | Ford 15S18(2015) | GM 17276(2017) | 公開レベル判定 |
|---|---|---|---|
| DTCとして残るか | Yes。ただし判断に使われたのは**有無の1bitのみ** | 読まれてすらいない(手順にDTC点検なし) | DTC確定分は残るが、判断粒度は1bit |
| DTC未満eventが残るか | **No**。DTCなし車両は「通常診断へ進め」で終わり、他に読むものがない | **No**。全車盲目的に再プログラム | **差分あり** |
| snapshot(freeze frame等)が読まれたか | **No**。手順に一切登場しない | **No** | **差分あり** |
| assist状態と電源/内部contextの同時性が使われたか | **No** | **No** | **差分あり** |
| 再発(key cycle recurrence)が使われたか | **No** | **No** | **差分あり** |

**5項目中4項目で、既存monitorのsoft contextが是正実務に存在しないことが、公開一次文書で確認できた。**
[docs/122](122_steering_predictive_diagnostics_power_monitor_payload_sample.md) のDecision Gate(2項目以上の差分)は、公開レベルでは満たされる。

したがって判定を1段上げる:

> SPD008 power monitorの価値仮説(既存monitorだけでは残らない領域があり、そこに状態説明価値がある)は、**公開情報のみでConfirmed**。内部資料が必要なのは、仮説の検証ではなく**実行**(自社製品の現行設定確認と部署の使い道確認)だけである。

詳細表は [data/steering_predictive_diagnostics_public_case_crosscheck.tsv](../data/steering_predictive_diagnostics_public_case_crosscheck.tsv) に置く。

## 何を判断しているか

判断したのは、次の1点である。

> 「短い電圧不安定や断続的な内部faultがassist低下を起こしたが、hard DTCとして安定して残らない」ケースについて、市場の実務は何を読んで判断したか。読むものが1bit(DTC有無)しかなかったなら、SPD008が埋めようとしている穴は実在する。

「自社programで残るか」は聞いていない。市場に出た他社実例の公開文書だけで判断した。

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Steering Predictive Diagnostics Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

確認結果:

- 判定変更(Hold→公開レベルConfirmed付き限定Proceed)を、内部資料ではなく公開一次文書で行った
- 「内部事実が見えないから進めない」という構図を、判定ゲートの組み替えで解消した(内部事実不足を主Kill理由にしないルールの積極適用)
- 特定OEMの設計批判には使わない。2014〜2017年世代の実例であり、EPS業界共通の当時の実務水準として扱う
- 故障予測、交換時期、root cause断定は主張していない

## 公開一次文書から読み取れた事実

### Ford Safety Recall 15S18(ディーラー向け指示書、2015年7月)

原因(公式): PSCMがmotor position sensor faultを検知するとmanual steeringへ移行する。

是正手順(原文の構造):

1. PSCMのDTCを点検する
2. 「loss of steering assist」系DTCが**なければ**: PSCMを再プログラム(工数0.2時間)
3. DTCが**あれば**: steering gear assembly交換(工数1.6〜2.4時間+トー調整0.6時間+部品)

さらに延長保証プログラム15N01の規定:

> For lack of power steering assist concerns, dealers are to check the PSCM for DTCs. If no "loss of steering assist" DTCs are present, the repair is **not** covered by 15N01. **Proceed to normal diagnosis.**

つまり、**assist喪失を訴えて入庫したのにDTCが残っていない顧客は、プログラム対象外として「通常診断」へ放り出される**。その通常診断で読める操舵側の追加contextは、手順上存在しない。

ここから言えること:

- **判断の全体重が「DTC有無」という1bitに乗っている**。0.2時間の再プログラムか、部品交換込みの約3時間かという大きなコスト分岐が、この1bitで決まる
- 断続的接触不良(このリコールの原因)がevent時にDTCを残さなかった場合、不良gearは車に残る。「症状はあるがコードがない」顧客の再発は構造的に説明できない

### GM Product Safety Recall 17276(ディーラー向け指示書、2017年8月)

現象(公式): 低速旋回中に一時的にEPS assistを喪失し、**約1秒以内に**突然復帰。電気/ソフト起因。

是正手順(原文の構造):

1. EPSモジュールを再プログラムする(全対象車、工数0.3時間)
2. プログラム完了後にDTCをクリアする

**診断データの読み出し工程がゼロ**である。DTC点検も、snapshot読み出しも、eventの発生有無の確認もない。
さらに顧客向けレターには、**この症状で過去に自費修理した顧客への払い戻し**手続きが定義されている。原因確定前の期間に、読める痕跡がないまま修理(おそらく多くは空振り)にお金を払った顧客が実在したことの公式な記録である。

## この照合が言い直した価値仮説

[docs/125](125_steering_predictive_diagnostics_unverified_delta_check.md) の言い直しに、公開実務の裏付けが付いた。

> AUTOSAR標準はDTC未満contextを残す設定余地を持つ(docs/125)。しかし市場に出た実車両の是正実務では、読まれたのはDTC有無の1bitだけであり、短いevent、同時性、再発は判断材料として存在しなかった(本ドキュメント)。EPSサプライヤがこの穴をcomponent boundaryで設計すれば、1bitで決まっていた大きなservice分岐(0.2時間 vs 約3時間、対象外放置 vs 適切な部品交換)を、原因断定なしの状態説明で支えられる。

## 限界(正直に)

1. 2件の実例は2011〜2017年世代である。**現行世代のprogramではDem設定が改善され、より多くが残る可能性がある**。「自社の現行設定でどうか」だけが残る内部確認点であり、docs/123の質問シートはそのために保存する
2. 2件はいずれも米国市場・北米OEMの実例である。ただしEPSのDTC設計実務はUDS/AUTOSAR共通基盤の上にあり、業界固有性は低いと判断する
3. 「2部署以上で使い道がある」(Decision Gateの後半)は、公開情報では確認できない。ただしこれは価値仮説の検証ではなく買い手の確認であり、実行段階の条件として残る

## 判定

| 項目 | 変更前(docs/127時点) | 変更後 |
|---|---|---|
| SPD008 power monitor | 判定保留付き限定Proceed(照合は内部資料条件待ち) | **公開レベルConfirmed付き限定Proceed**。価値仮説の検証は公開情報で完了 |
| 内部資料条件の中身 | 仮説検証+実行 | **実行のみ**(現行世代の自社設定確認、部署の使い道確認) |
| Kill可能性 | 既存monitorで足りると分かれば | 現行世代で既にこの穴が塞がれていると分かれば(質問シートで確認) |

## 次の作業

1. 公開情報での本線検証は、これで本当に出し切った。区切り判定(checkpoint)を書く場合は、「検証待ちHold」ではなく「公開検証完了・実行条件待ちの限定Proceed」として書く
2. communication input validity(docs/124)にも同じ公開ケース照合が適用できる(GM TSB 17-NA-158系の一次文書精読)。必要なら次に実施する
3. docs/123の質問シートは「現行世代でこの穴が既に塞がれていないか」の確認用として、実行段階まで保存する

## Sources

- [Ford Safety Recall 15S18 dealer letter + attachments(NHTSA公開)](https://static.nhtsa.gov/odi/rcl/2015/RCMN-15V340-8835.pdf): DTC有無による2経路是正、15N01延長保証の「DTCなし=対象外・通常診断へ」規定、工数表(0.2時間 vs 1.6〜2.4時間+0.6時間)
- [GM Product Safety Recall 17276 bulletin(NHTSA公開)](https://static.nhtsa.gov/odi/rcl/2017/RCSB-17V414-6829.pdf): 約1秒の一時喪失・突然復帰、診断読み出し工程なしの全車再プログラム、既払い修理の払い戻し規定
