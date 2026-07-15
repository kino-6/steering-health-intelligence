# SPD Unverified Delta Check

## 結論

これまで「未検証」のまま残っていた2つのデルタ(差分)主張を、公開情報でファクトチェックした。

1. **SPD008の既存monitor比優位性**([docs/117](117_steering_predictive_diagnostics_spd008_vs_spd002_decision.md) で「SPD008優位だが未検証」)
2. **汎用テレマティクス / 路面分類 / ADAS / IDSとのデルタ**([docs/98](98_business_model_mainline_after_correction.md) でKill条件に接続された未検証項目)

結果は次である。

| デルタ主張 | 検証結果 | SPDへの影響 |
|---|---|---|
| 既存monitorではDTC未満contextが残らない | **部分的に否定**。AUTOSAR標準はpending / testFailed段階のsnapshot格納、デバウンスカウンタ不揮発保存を持つ。ただしデバウンス閾値未満のevent(testFailedに至らない短いdipや散発timeout)は標準の枠組みの外 | 価値主張を「新しい検知能力」から「component boundaryでの状態説明設計(設定・trigger設計の選択)」へ言い直す。docs/123の質問シートは「残せるか」でなく「残しているか」を聞く形に修正済み |
| 汎用テレマティクスでは電源contextが見えない | **部分的に否定**。fleet telematicsは12V電圧監視、低電圧アラート、バッテリー健全性通知を標準機能として持つ | 車両レベルの電圧監視はEPSの差分にならない。差分は、EPSコネクタ点での観測、assist limitationとの同時性、telematicsのサンプリングでは見えない短時間dip classに限定して主張する |
| IDSは通信異常を扱わない | **否定**。AUTOSAR IdsMがsecurity eventの収集・保存・cloud送信まで規格化済み | communication input validityの価値は「機能可用性の状態説明」に限定して初めて差分になる。docs/124のHold理由に追加済み |

いずれもSPD008をKillする結果ではない。
しかし、「既存では残らない / 見えない」という言い方は今後使わない。
正しい言い方は、「**既存の仕組みで残せるのに、機能影響との同時性を説明する形では設定・設計されていないことが多い領域を、EPSサプライヤが自分のcomponent boundaryで設計できる**」である。

詳細表は [data/steering_predictive_diagnostics_unverified_delta_check.tsv](../data/steering_predictive_diagnostics_unverified_delta_check.tsv) に置く。

## 何を判断しているか

判断しているのは、SPD008(および比較対象のSPD002)の価値主張が、既存技術・既存商品と区別できるかである。

これは [AGENTS.md](../AGENTS.md) の `Mandatory Rule Check Before Stop / Kill / Archive` が要求する判断軸そのものである。

> 汎用テレマティクス、路面分類、ADAS、IDSと区別できるか

区別できなければ docs/98 のKill条件に接続する。
区別できるなら、その区別の言い方を固定し、以後のドキュメントで使う。

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Steering Predictive Diagnostics Value Rule`
6. `Mandatory Rule Check Before Stop / Kill / Archive`

確認結果:

- 今回の判定変更(価値主張の言い直し)はKillではないが、判断軸の修正を含むためRule Checkを明示した
- Kill条件の判定を「内部事実が見えないから」ではなく「既存技術・既存商品と区別できるか」で行っている
- 公開情報(AUTOSAR仕様、telematics商品情報)を、商品価値の証明ではなく、既存業務重複の確認に使っている
- 修正後の価値主張も、EPS RUL、交換時期、安全保証、root cause、保証費削減を含まない
- 修正後の価値主張は、EPSサプライヤが自分で設計できる範囲(component boundary)に閉じている

## 検証1: 既存monitor比優位性

### 確認した事実

AUTOSARのDiagnostic Event Manager(Dem)仕様では:

- snapshot record / extended data recordの格納トリガは、record番号ごとに testFailed / pending / confirmed のstatus遷移から設定できる
- extended dataにはoccurrence counter、aging counter、最終発生時刻などを含められる
- デバウンスカウンタの不揮発保存(シャットダウン時保存)が標準機能として存在する

つまり、「DTC確定前のcontextは既存の仕組みでは残せない」は誤りである。
残せる。残していないとすれば、それは対象programの設定・設計の選択である。

### 残る本物の差分

一方で、次は標準の枠組みの外にあり、ここがSPD008の差分候補の中心である。

1. **デバウンス閾値未満のevent**: testFailedに至らない短い電圧dipや散発的timeoutは、Demのevent処理に入らず、どこにも残らない
2. **機能影響との同時性のfield設計**: voltage contextとassist mode / limit stateを同一recordまたは共通時刻基準で残すかは、DTC設計の目的(故障確定の証拠)には含まれないことが多い
3. **DTC未満eventのkey cycle横断の再発管理**: occurrence counterはevent(testFailed以上)を数える。閾値未満の繰り返しは数えられない

### 判定

SPD008は続ける。ただし価値主張を言い直す。

言ってよい形:

> 既存の診断標準は、DTC未満のcontextを残す設定余地を持っている。しかし、故障確定の証拠として設計されているため、機能影響(assist limitation / fallback)との同時性や、閾値未満eventの再発は残らない設計が多い。EPSサプライヤは、この穴を自分のcomponent boundaryで設計し、原因断定なしの状態説明として提供できる。

もう使わない形:

> 既存monitorではDTC未満のcontextは残らない。

## 検証2: 汎用テレマティクスとのデルタ

### 確認した事実

fleet telematics(例: Geotab)は、12V電圧の監視、低電圧閾値でのアラート(例: 9V未満通知)、バッテリー健全性の通知を標準機能として持つ。
車両レベルの電源監視は、既に商品化された領域である。

### 残る本物の差分

1. **観測点**: telematicsはOBDポートまたは自デバイスの給電点で電圧を見る。EPSはEPS自身のコネクタ点で、大電流アシスト動作中の電圧を見る
2. **同時性**: telematicsは「車両の電圧が下がった」ことは言えるが、「操舵アシストが制限された瞬間にEPS入力電圧がどうだったか」は言えない
3. **時間分解能**: アシスト過渡で問題になる短時間のdipは、telematicsのサンプリング・通知設計の対象外

### 判定

デルタは主張できる。ただし観測点・同時性・時間分解能の3点に限定して言う。
「テレマティクスでは電源が見えない」とは言わない。

## 検証3: IDSとのデルタ

### 確認した事実

AUTOSAR IdsM(R20-11以降)は、BSWモジュールやSWCが報告するon-board security eventの収集、filter chainによる選別、qualified security eventのECU内保存またはIdsRを介したcloud(VSOC)送信までを規格化している。
通信異常をsecurity eventとして扱う標準経路は既に存在する。

### 残る本物の差分

IdsMの目的はsecurity(侵入検知、VSOC報告)である。
EPSのcommunication input validityで見たいのは、操舵機能の可用性(なぜfallbackに入ったか)であり、出力の宛先も言葉も違う。

ただし、対象programがメッセージ異常をSEv(security event)として定義している場合、収集経路が物理的に重複し得る。
この場合、EPS側は「security判定はIdsMの領域、機能可用性の説明はEPS componentの領域」という役割分担を明文化できなければHoldである。
この条件は [docs/124](124_steering_predictive_diagnostics_comm_input_validity_case.md) のDecision Gateに追加済みである。

### 判定

デルタは主張できる。ただし「securityではなく機能可用性」という目的の区別で言い、IdsMの代替・重複に見える形を避ける。

## ADAS / 路面分類とのデルタについて

docs/98のKill条件はADAS / 路面分類も挙げていた。
SPD008の対象(power monitor、communication input validity)はEPS内部モジュールの観測であり、路面や運転行動の推定を含まないため、この2つとは入力も出力も重ならない。
これは調査ではなく定義の確認で足りるため、本ドキュメントでは判定のみ記す: **重複なし**。
ただし、将来SPD008の対象をE2E方向(路面exposure等)へ広げる場合は、この判定は無効になり再検証が要る。

## SPD002 reference demoの扱い(凍結の明文化)

[docs/114](114_steering_predictive_diagnostics_spd_final_conclusions.md) でProceed(demo)指定されたSPD002の1ケース診断読み順は、docs/116作成後、進めていない。

これは放置ではなく、意図的な凍結として扱う。

理由:

1. [docs/119](119_steering_predictive_diagnostics_viewpoint_correction.md) の観点補正で、診断読み順artifactは副次artifactに格下げされた
2. SPD002の読み順demoは、service manual要約に近づくリスクが docs/114 / docs/117 で指摘済み
3. 現在の判定待ち事項(docs/123の照合)が終わるまで、副次artifactに工数を割かない

再開条件:

- docs/123の照合でpower monitorがProceedになり、固定スコープassessmentの構成要素として診断読み順が必要になった場合
- または、SPD008がHold / Stopに落ち、実証しやすさ優先でSPD002へ本線を移す判断をした場合

## 次の作業

1. [docs/123](123_steering_predictive_diagnostics_power_monitor_program_question_sheet.md) の質問シートを対象programで回答する(最優先、変わらず)
2. 以後のSPDドキュメントでは、本ドキュメントで言い直した価値主張の形を使う
3. README現在地の次アクション記述を更新する(実施済み)

## Sources

- [AUTOSAR SWS Diagnostic Event Manager (R20-11)](https://www.autosar.org/fileadmin/standards/R20-11/CP/AUTOSAR_SWS_DiagnosticEventManager.pdf): snapshot / extended data格納トリガ(testFailed / pending / confirmed)、デバウンスカウンタ、occurrence / aging counter
- [AUTOSAR SRS Diagnostic (FO R1.1.0)](https://www.autosar.org/fileadmin/standards/R17-03_R1.1.0/FO/AUTOSAR_SRS_Diagnostic.pdf): 診断要求仕様
- [AUTOSAR SWS Intrusion Detection System Manager (R24-11)](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_IntrusionDetectionSystemManager.pdf): security event収集、qualified security eventの保存・送信
- [AUTOSAR PRS Intrusion Detection System (FO R20-11)](https://www.autosar.org/fileadmin/standards/R20-11/FO/AUTOSAR_PRS_IntrusionDetectionSystem.pdf): IDSプロトコル
- [Geotab vehicle telematics](https://www.geotab.com/vehicle-telematics/): fleet telematicsの車両データ監視範囲
- [Geotab Engine Faults / battery monitoring支援情報](https://support.geotab.com/mygeotab/doc/engine-faults-cheat): 低電圧アラート、バッテリー監視の既存機能
