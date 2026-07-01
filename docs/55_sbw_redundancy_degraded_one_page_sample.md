# 車輪を動かす側の1ケースsample: 冗長低下時に何を説明できるか

## 結論

このsampleで見たいのは、Steer-by-wire向けの新しい安全分析ではない。

見るのは、既存の安全・サイバー・診断・software update成果物を使って、OEMへ次の1文を説明できるかである。

> 車輪を動かす側の冗長系が一部落ちた場合、操舵機能はどの状態に落ち、運転者には何が見え、診断では何が読め、サプライヤは何を断定してはいけないか。

これが公開情報だけでは汎用安全説明にしか見えないなら、この方向は弱い。
現行方針では、既存safety caseや部署内資料を要求して差分を確認しに行かない。

## Scenario

| Field | Sample |
|---|---|
| abnormal condition | 車輪を動かす側の冗長系が一部落ちた |
| assumed trigger | actuator position sensor disagreement、motor phase current abnormal、local inverter diagnostic、communication timeoutのいずれか |
| driver-visible behavior | warning、chime、pull over request、drive torque reduction |
| remaining steering capability | degraded steering available。条件によってlow-speed maneuvering onlyへ落とす |
| supplier-owned evidence | actuator status、sensor agreement、motor current / voltage、ECU reset / brownout、communication state、software/calibration ID |
| diagnostic content | DTC、redundancy degraded status DID、freeze frame、extended data、security accessで読める範囲 |
| linked safety/cyber source | FMEA row、safety mechanism ID、TARA row、security access policy、post-update check |
| OEM answer | 冗長低下を検知し、残存操舵能力を制限し、運転者へ退避を促す。診断では状態と周辺条件を読める。ただし原因断定は分解・追加解析まで行わない |
| do-not-claim | root cause断定、保証費削減、field failure prediction、vehicle-level safety approval |

## この1ページで分かること

分かること:

- 機械的なつながりをなくす操舵では、異常時状態が運転者表示、駆動力制限、診断、ソフト番号や設定値にまたがる
- EPSサプライヤが説明できるのは、部品境界内の状態、検知、診断、制限動作までである
- OEM向け回答は、安全資料、診断仕様、cyber/security access、software update確認をまたぐ

分からないこと:

- 実際の対象EPSで同じDTC / DID / freeze frameがあるか
- 既存safety caseに同等のOEM回答文が既にあるか
- OEMがこの説明をサプライヤに求めるか
- この整理に予算がつくか

## Proceed / Kill

探索継続寄り:

- 公開情報だけで、冗長低下時の残存機能・診断・driver-visible behaviorが1つのsampleに接続できる
- 公開RFQ/RFI、公開標準、公開診断動向に接続できる
- 既存R79/ISO 26262説明との差分が自然言語で説明できる

Kill:

- 公開情報だけでは、この1ページが汎用安全説明にしかならない
- diagnostic contentやsoftware/calibration IDと公開情報上で接続しない
- 公開OEM質問、公開RFQ/RFI、公開標準に接続できない
- 汎用ISO 26262説明に見える

## EPSサプライヤとしての使い方

このsampleを、最初の商材デモとして使わない。
使い方は、公開情報ベースの探索継続/Stop判断に限定する。

> この1ページは、公開情報だけでEPSサプライヤの独自判断になっていますか。それとも、汎用安全説明を言い換えただけですか。

後者ならKill。
