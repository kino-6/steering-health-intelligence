# RDI006 thermal limit / assist limitation 4列sample

## 結論

このsampleで分かったことは、単純である。

操舵系のDTCを読み、severityやaction planへ変換するだけなら、既存の遠隔診断サービスと大きく変わらない。
EPS/SbWサプライヤの差分が出るのは、同じDTCの裏側にあるassist制限、温度状態、モータ電流、再発counter、software / calibration IDを使って、次に読むべき診断項目や注意文を変えられる場合だけである。

したがって、この仮説はまだ売り物ではない。
ただし、特定OEM programでEPS/SbW固有のDID、freeze frame、extended data、service outcomeが使えるなら、短期の診断コンテンツ支援として試す余地はある。

## 何を判断しているか

ここで判断しているのは、EPS/SbWサプライヤがOEM遠隔診断に対して、部品側の状態説明を追加できるかである。

これは、fleetを直接監視する話ではない。
また、EPSの交換時期を予測する話でもない。
OEMの遠隔診断、fleet service、service engineering、dealer diagnostic supportが既に持っているDTC、severity、action planに対して、EPS/SbW内部データから「何を追加で読むべきか」「何を断定してはいけないか」を渡せるかを見る。

## 1ケースsample

詳細TSVは [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_thermal_limit_sample.tsv](../../../data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_thermal_limit_sample.tsv) に置く。

想定ケース:

> 配送車または低速高操舵が多い車両で、高負荷操舵後にEPS/SbWがassist limitationまたはthermal limitに入った。

これは実EPSデータではない。
公開情報と過去のKill sampleを使った、判断用のproxy sampleである。

| 見方 | 分かること | 限界 |
|---|---|---|
| DTCだけ | 警告、fault code、timestamp、system status | 高負荷操舵、温度、assist制限、再発履歴は分からない |
| 既存remote diagnostics | severity、action plan、service routing、parts preparation | 操舵系内部状態に応じて読み順や注意文が変わるかは未確認 |
| EPS/SbW内部説明 | assist state、thermal state、motor current、software / calibration ID、再発counter | OEM programでdata fieldが出ないと使えない |
| OEM service note | 入庫前の追加確認、DID読み順、注意文、禁止主張 | 運行可否、安全保証、交換判断はOEM/service側 |

## 差分が出る箇所

差分が出る可能性があるのは、以下の4点である。

1. DTCが出た理由を、単なる故障名ではなく「高負荷操舵後の温度制限状態」として説明できる。
2. cool-down後に状態が戻ったか、短時間で再発したかで、次に読むDIDを変えられる。
3. repeated eventの場合に、入庫の有無だけでなく、thermal counter、assist limit duration、motor current、voltage、communication stateの読み順を出せる。
4. software / calibration IDを、状態説明や追加確認項目へつなげられる。

ただし、これはすべて内部データが使える場合の話である。
公開APIのDTC、system status、vehicle healthだけでは、この差分は出しにくい。

## 差分にならない箇所

次の範囲に留まるなら、既存remote diagnosticsとの差分はない。

- DTC descriptionを分かりやすく言い換えるだけ
- severityを付けるだけ
- service centerへ案内するだけ
- action planを一般文で出すだけ
- parts preparationを推測するだけ

Bosch、International、Platform Science、Geotabなどの公開情報を見る限り、このあたりは既存remote diagnosticsがすでに強く扱っている。

## 判定

このsampleの判定は、**条件付きContinue** である。

進めてよい条件:

- EPS/SbW固有DID、freeze frame、extended data、assist state、thermal state、motor current、software / calibration IDの一部をOEM program内で扱える
- 既存remote diagnosticsのaction planに対して、追加DID読み順、注意文、禁止主張を具体的に足せる
- service outcome、再発有無、作業時間、dealer commentの一部が戻る
- サプライヤ説明とOEM action plan、fleet/service decisionの責任境界を分けられる

止める条件:

- 一般DTC APIとsystem statusしか使えない
- 既存remote diagnosticsと同じseverity/action planしか出せない
- 整備結果や再発有無が戻らない
- EPS/SbWサプライヤが運行可否、安全保証、交換時期、root causeを断定する必要がある

## EPSサプライヤとしての言い方

EPS/SbWサプライヤとして言えること:

> 対象programで操舵系内部data fieldを扱える場合、DTC発生時の状態説明、追加DID読み順、注意文、禁止主張をOEM遠隔診断のservice noteへ渡せる可能性がある。

まだ言ってはいけないこと:

> fleetを直接監視できる、走行安全を保証できる、EPS交換時期を予測できる、root causeを断定できる、既存remote diagnosticsを置き換えられる、とは言わない。

次に見る最小項目:

> 実programまたは想定programで、thermal limit / assist limitation時に読めるDID、freeze frame、extended data、software / calibration ID、service outcome欄を列挙する。

## 次アクション

次にやるなら、調査ではなく穴埋め表を作る。

列は以下でよい。

| 項目 | 目的 |
|---|---|
| 読めるdata field | DTC以外に何がnetworkまたはservice toolへ出るか |
| 既存action plan | OEM remote diagnosticsが既に何を言うか |
| 追加できる説明 | EPS/SbWサプライヤが足せる説明は何か |
| service note転記先 | dealer / service engineeringがどこへ書くか |
| 戻るoutcome | 再発、交換、作業時間、commentが戻るか |
| 禁止主張 | 安全保証、交換時期、root cause断定を避けられるか |

この穴埋め表が空欄だらけになるなら、RDI006もStopでよい。

## Sources

- GM Fleet OnStar API Services: https://www.gmfleet.com/software/onstar/api-services
- Smartcar real-time vehicle diagnostics: https://smartcar.com/docs/getting-started/guides/real-time-vehicle-diagnostics
- Smartcar Diagnostic Trouble Codes API: https://smartcar.com/docs/api-reference/get-dtcs
- Smartcar System Status API: https://smartcar.com/docs/api-reference/get-system-status
- High Mobility Car Data API: https://www.high-mobility.com/car-data
- Bosch Cloud and Predictive Diagnostics: https://www.bosch-mobility.com/en/solutions/software-and-services/cloud-and-predictive-diagnostics/
- International Advanced Remote Diagnostics: https://www.international.com/services/my-international/advanced-remote-diagnostics
- Platform Science Remote Diagnostics: https://www.platformscience.com/blog/the-power-of-remote-diagnostics-for-fleet-maintenance
- Geotab Remote Diagnostics: https://www.geotab.com/blog/remote-diagnostics/
- ZF Vehicle Health Monitoring: https://press.zf.com/press/en/releases/release_92162.html
- ASAM SOVD: https://www.asam.net/standards/detail/sovd/
