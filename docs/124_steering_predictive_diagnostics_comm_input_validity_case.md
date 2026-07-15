# Communication Input Validity Predictive Value Case

## 結論

communication input validityで見るべき1ケースは、**EPSが依存する外部signalのintermittent invalid / timeout / alive counter増加が、steering fallback contextの近傍で繰り返すが、hard communication DTCが安定して残らないケース**である。

現時点の結論は、**条件付きHold(Proceed寄り)を維持** である。
[docs/120](120_steering_predictive_diagnostics_spd008_predictive_value_check.md) の第二検証候補としての位置づけは変えない。

power monitorとの違いとして、Hold理由を1つ追加した。
公開されているAUTOSAR標準を確認した結果、通信異常の収集・持ち出しには既にIdsM(Intrusion Detection System Manager)という標準の仕組みがあり、security eventとしてECU内保存またはcloud側(VSOC)への送信までが規格化されている。
対象programがメッセージ異常をsecurity eventとして扱っている場合、EPS側で似た収集を作ると重複に見えるリスクがある。
このケースの価値は、securityの異常検知ではなく、**操舵機能の可用性(fallback)をEPS component boundaryから説明すること**に限定して初めて差分になる。

詳細表は [data/steering_predictive_diagnostics_comm_input_validity_case.tsv](../data/steering_predictive_diagnostics_comm_input_validity_case.tsv) に置く。

## 何を判断しているか

この1ケースでは、次を判断している。

1. 既存monitor(timeout DTC、bus-off、invalid value DTC、E2E保護status、IdsM)で残る情報は何か
2. 既存monitorでは残らない可能性があるsoft context(hard DTC未満の揺らぎとfallback近接)は何か
3. そのsoft contextを、EPSサプライヤが自分のcomponent boundary内で定義できるか(OEM architecture依存をどこで切るか)
4. vehicle health向けのdependency context観測として、原因断定なしに状態説明へ変換できるか
5. どこからが外部ECU原因断定、network調査、security監視の領域に見えるため禁止か

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Steering Predictive Diagnostics Value Rule`
6. `Mandatory Rule Check Before Stop / Kill / Archive`

確認結果:

- 市場需要は、故障確定前または原因未確定の段階で、操舵機能の依存contextを早く知りたいことである
- EPS製品全体E2Eではなく、communication input validityという内部重要モジュール単位に限定している
- 診断読み順、追加ログ、品質feedback、顧客説明を最終目的にしていない
- 外部ECU原因、network原因を断定しない
- 既存monitor(IdsMを含む)で十分ならHoldまたはStopにする
- IdsMの存在は主Kill理由ではなく、価値説明を「security検知」から「機能可用性の状態説明」へ限定する境界として扱う

## Market Demand

市場需要は、外部ECUやnetworkの犯人探しをEPS側でやることではない。

実務で困るのは、次のような場面である。

1. 操舵の警告表示やfallback動作が一時的に出たが、hard communication DTCが安定して残らず、EPS内部故障と外部signal起因の切り分けに時間がかかる
2. by-wire / motion-domain化で操舵機能の外部signal依存が増え、「EPSが何を受け取り、どう判断してfallbackに入ったか」を後から説明する要求が増える
3. サービス側が、操舵クレームをEPS交換で処理してしまい、依存signal起因の再発が止まらない
4. vehicle health基盤へ、操舵componentから見たdependency contextを渡したいが、security IDSの出力とは別の、機能可用性の言葉が要る

この需要に対してEPSサプライヤが持てる手札は、EPSが受信する依存signalのvalidity判定、timeout / alive counter、E2E保護の結果、fallback state遷移、steering messageの整合である。
いずれもEPS componentの入力境界での観測であり、busやnetwork全体の監視ではない。

## Case Definition

想定する1ケースは次である。

> 走行中、EPSが依存する外部signal(例: 車速)のvalidityが断続的に崩れる、またはtimeout / alive counter異常が散発する。EPSはその都度fallback contextに入る、または近づく。同じkey cycleまたは近いkey cycleで再発する。ただし、hard communication DTCとして安定して残らず、bus-offにも至らない。

このケースで見るのは、外部ECUやnetworkの原因ではない。
見るのは、EPS componentが観測した依存signal validityと、操舵機能のfallback availabilityの関係である。

## Existing Monitor Comparison

| Item | 既存monitorで残る可能性 | 既存monitorでは残らない可能性 | SPD008で見る意味 |
|---|---|---|---|
| timeout DTC | timeout閾値を超えて確定すれば残る | 閾値未満の散発的timeoutは残らない可能性 | DTC未満の揺らぎを状態説明へ使えるか |
| bus-off / error counter | bus-off成立で残る | error counter増加のみの区間は残らない可能性 | hard fault未満のbus品質contextを見られるか |
| invalid value DTC | invalid判定が確定すれば残る | intermittent invalidが確定に至らず消える可能性 | 断続的invalidの繰り返しを扱えるか |
| E2E保護status | E2E失敗が閾値超えでevent化されれば残る | E2E失敗率の変動そのものは残らない可能性 | 入力品質の揺らぎを近接contextにできるか |
| fallback state | DTCやeventに紐づけば残る | signal validityとの同時性までは残らない可能性 | dependency contextとfallbackの近接を説明できるか |
| IdsM security event | メッセージ異常がsecurity eventとして定義されていれば収集・保存・送信まで規格化済み | securityの言葉で残り、操舵機能の可用性文脈では残らない | securityではなく機能可用性の説明として差分を出せるか |
| key cycle recurrence | DTC履歴で一部残る可能性 | DTC未満の揺らぎの再発頻度は残らない可能性 | 繰り返しを状態説明として扱えるか |

power monitorと同じく、AUTOSAR Demのsnapshot / extended data格納トリガはpending / testFailed段階でも設定できるため、「残せない」ではなく「対象programの設定で残しているか」が正しい質問である。
照合質問の形式は [docs/123](123_steering_predictive_diagnostics_power_monitor_program_question_sheet.md) と同じ型を使う(TSVに含めた)。

## Minimum Vehicle Health Payload

既存monitorだけでは不足がある場合、vehicle health向けの最小payloadは次に限定する。

| Field | Example value | Purpose |
|---|---|---|
| component | steering / EPS | どの部品側観測かを示す |
| observed_context | intermittent dependency-signal validity instability observed by EPS | EPSが観測したcontextを示す |
| dependency_signal_class | vehicle speed class / yaw class / gear class など、EPS入力境界での分類名 | 依存signalを外部ECU名でなくEPS入力として示す |
| relation_to_function | entered or approached steering fallback context | 機能状態との近接を示す |
| monitor_status | below hard communication DTC threshold / no stable DTC | hard fault確定ではないことを示す |
| recurrence | same key cycle / recent key cycles / unknown | 繰り返しか一過性かを示す |
| retained_fields | validity status, timeout / alive counter, E2E result class, fallback state, key cycle | 判断に使った項目を明示する |
| confidence | low / medium | 断定しないための信頼度表現 |
| recommended_read | EPS DTC status, dependency validity context, fallback state, recurrence | 次に読む順序を示す |
| boundary | not external ECU root cause, not network diagnosis, not security detection, not replacement timing | 禁止主張を明示する |

vehicle health向けの状態説明文は、[docs/120](120_steering_predictive_diagnostics_spd008_predictive_value_check.md) の文を維持する。

> Steering function entered or approached fallback context while EPS-observed dependency signal validity was unstable. This is a steering-side dependency observation, not an external ECU root cause decision.

日本語では次である。

> EPSが観測した依存signalのvalidityが不安定な近傍で、操舵機能がfallback contextに入った、または近づいた。これは操舵側から見た依存関係の状態説明であり、外部ECU原因の断定ではない。

## Business Value Check

| Value type | 判断 |
|---|---|
| 製品価値 | 可能性あり。by-wire / motion-domain時代に、操舵機能の外部依存の扱いをcomponent boundaryとして説明できる |
| 診断価値 | 可能性あり。操舵クレームをEPS内部故障へ短絡する前に、依存signal validityとfallback stateを読む順番を作れる |
| 品質改善価値 | 可能性あり。dependency instabilityの再発patternとEPS交換の空振り(NTF)傾向を突き合わせられる |
| 顧客技術説明価値 | 可能性あり。EPS単独故障にも外部ECU原因にも短絡しない説明を持てる |
| vehicle health contribution | 中から強。ただしsecurity IDSの出力とは別枠の、機能可用性contextとしてだけ渡す |

## Decision Gate

Proceed(固定スコープassessmentとして):

- EPSサプライヤが、依存signal class、validity判定、timeout / alive counter、E2E結果、fallback stateを自製品仕様として定義できる(OEM資料なしで書ける)
- 照合質問の結果、hard DTC未満の揺らぎとfallback近接が既存設定では残らない項目が2つ以上ある
- 対象programでメッセージ異常のIdsM収集と重複しない(またはsecurity / availabilityの役割分担を文章で切れる)
- 診断企画、品質改善、顧客技術説明のうち2部署以上で使い道がある

Hold(現状):

- 依存signal listやfallback定義がOEM programごとに変わり、EPS標準仕様として一般化できるか未確認
- IdsMとの役割分担を対象program単位でしか決められない
- power monitorの照合(docs/123)が先に走っており、同じ照合をこちらで並走させるリソース判断が未了

Stop:

- EPS入力境界の観測だけでは、fallback近接の説明が成立しない(network全体のデータが必須になる)
- 価値説明に、外部ECU root cause、network診断、security監視の代替、交換時期、安全保証が必要になる
- IdsM / 既存communication DTCで同じ状態説明が十分にできる

## What Not To Claim

まだ言ってはいけないこと:

> 外部ECUが原因だと分かる。

> networkの品質を診断できる。

> securityの侵入検知ができる / IDSを代替する。

> EPSが悪くないと断定できる。

> EPS交換時期が分かる。安全保証ができる。保証費削減につながる。

## 次の作業

1. power monitorの照合(docs/123)の判定が先。その結果でsheet形式の有効性を確認する
2. 有効なら、TSVに含めた照合質問のprogram固有欄を、communication input validityについても回答してもらう
3. IdsMとの役割分担(security event / availability context)を対象program単位で1段落で書けるか確認する
4. 書けなければHold維持。書ければ固定スコープassessmentの第二項目として扱う

## Sources

既存の仕組みに関する一般論は次の公開情報による。

- [AUTOSAR SWS Intrusion Detection System Manager (R24-11)](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_IntrusionDetectionSystemManager.pdf): security eventの収集、filter、qualified security eventの保存・送信
- [AUTOSAR PRS Intrusion Detection System (FO R20-11)](https://www.autosar.org/fileadmin/standards/R20-11/FO/AUTOSAR_PRS_IntrusionDetectionSystem.pdf): IDSプロトコル
- [AUTOSAR SWS Diagnostic Event Manager (R20-11)](https://www.autosar.org/fileadmin/standards/R20-11/CP/AUTOSAR_SWS_DiagnosticEventManager.pdf): snapshot / extended data格納トリガ、デバウンス、event memory
