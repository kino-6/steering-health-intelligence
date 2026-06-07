# SbW 1ケースsample: 冗長低下時に何を説明できるか

## 結論

このsampleで見たいのは、Steer-by-wire向けの新しい安全分析ではない。

見るのは、既存の安全・サイバー・診断・software update成果物を使って、OEMへ次の1文を説明できるかである。

> road wheel actuator側の冗長低下を検知した場合、操舵機能はどの状態に落ち、運転者には何が見え、診断では何が読め、サプライヤは何を断定してはいけないか。

これが既存safety caseだけで自然に出るなら、この方向は弱い。
逆に、資料はあるが部署ごとに分断されていて、この1文を作るのに手間がかかるなら、狭いassessmentとして価値が残る。

## Scenario

| Field | Sample |
|---|---|
| abnormal condition | road wheel actuator redundancy degraded |
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

- SbWでは、異常時状態が運転者表示、drive torque、診断、software/calibration IDにまたがる
- EPSサプライヤが説明できるのは、部品境界内の状態、検知、診断、制限動作までである
- OEM向け回答は、安全資料、診断仕様、cyber/security access、software update確認をまたぐ

分からないこと:

- 実際の対象EPSで同じDTC / DID / freeze frameがあるか
- 既存safety caseに同等のOEM回答文が既にあるか
- OEMがこの説明をサプライヤに求めるか
- この整理に予算がつくか

## Proceed / Kill

Proceed寄り:

- 既存資料はあるが、safety、cyber、diagnostic、software updateの説明が分断されている
- OEM design reviewやRFQで、冗長低下時の残存機能・診断・driver-visible behaviorを聞かれている
- diagnostic contentをSOVD / UDSでどう見せるか未整理

Kill:

- 既存safety caseから、この1ページと同等の説明が既に出せる
- diagnostic contentやsoftware/calibration IDと接続しない
- OEM質問がなく、社内の整理だけで終わる
- 汎用ISO 26262説明に見える

## EPSサプライヤとしての使い方

このsampleを、最初の商材デモとして使わない。
使い方は、社内のsystems、functional safety、diagnostic、cyber、software update、customer interfaceの各担当に見せて、次を聞くこと。

> この1ページは、既存資料からすぐ作れますか。それとも、資料はあるが部署をまたいで集めないと作れませんか。

前者ならKill。
後者なら、短期assessmentとして残す。
