# 08. OTA / Connected Health Market Direction

## Question

近年の車両はOTAやConnected Vehicle化が進むため、EPSからの診断・兆候通知を見る機会が増えるのではないか。
その接点を使って、故障や劣化兆候をOEM / EPSシステムサプライヤ向けに出す事業は成り立つか。

## Short Answer

この文書は、OTAを主価値として扱うものではない。

本件の主価値は、EPSそのものに故障可能性・劣化兆候・予測用データ材料を持たせることである。
OTAやremote diagnosticsは、そのEPS health indicatorを読むチャネルの一つにすぎない。

したがって、正しい位置づけは以下である。

> EPS Health Intelligenceを主商品とし、OTA / connected vehicle / service diagnostics / return-part analysisを読み出し・利用チャネルとして扱う。

## Market Trend Signals

### 1. OTA is becoming a lifecycle operation, not a one-off feature

OEMは車両販売後もソフトウェアを更新し続ける方向に進んでいる。

Hyundai Motor Groupは、2025年までに全車種がOTAソフトウェア更新を受けられるようにする方針を公表している。
GMもUltifiのようなvehicle software platformを通じて、OTA更新、クラウドサービス、継続的な機能追加を前提にした車両アーキテクチャを打ち出している。

この流れから、OTAはinfotainmentだけでなく、車両制御・診断・設定・データ収集と結びつく。

Implication for this repo:

- EPS health indicatorは、単独アプリではなくOTA / connected platformの1機能として置く方が自然。
- EPS更新時だけでなく、任意のOTAキャンペーン前後や定期remote diagnostics時にEPS状態を読む発想が使える。

### 2. Regulation pushes safe, traceable software update management

UNECE R156は、車両ソフトウェア更新に対してSoftware Update Management Systemを求める。
公開資料やOTAベンダーの説明では、更新の安全性、トレーサビリティ、適合性、ロールバック、更新前後の状態確認が重要テーマになっている。

Implication for this repo:

- EPSのような安全関連ECUは、OTA前後のhealth check対象になりやすい。
- `Can update proceed?` と `Did update affect EPS behavior?` という問いに答えるデータは価値がある。
- 故障予測よりも、`pre-update health gate` と `post-update regression monitor` の方が導入先が明確。

### 3. Remote diagnostics is being standardized for SDV

ASAM SOVDは、software-based vehicles向けに診断APIを定義し、proximity、remote、in-vehicleの3シナリオを対象にしている。
ISO 17978-3:2026も、HPCとlegacy ECUの診断、fault entry、environment data、measurement、identification、software update strategyへのアクセスを扱う。

Implication for this repo:

- EPS health indicatorは、独自ログではなくremote diagnostics / SOVD / UDSの世界に接続できる形で設計すべき。
- signal listより先に、バックエンドが読むhealth summary APIやdiagnostic DIDの形を考える価値がある。
- `DTC + environment data + health indicator + version/calibration` の組み合わせが重要。

### 4. OTA vendors already combine update management, diagnostics, and data collection

Sonatus、Sibros、Excelforeなどは、OTA更新だけでなく、remote diagnostics、dynamic vehicle data collection、predictive maintenance、health monitoring、campaign traceabilityを打ち出している。

これは、OEM側の需要が「更新を配る」だけではなく、以下に広がっていることを示す。

- update campaignを成功させたい
- update前に車両状態を確認したい
- update後の不具合を早く検知したい
- ECUや車両データを動的に収集したい
- warranty / service costを下げたい
- remote fixやservice triggerにつなげたい

Implication for this repo:

- EPS側はOTAプラットフォームと競合しない。
- EPS固有のhealth feature packageとして、OTA / diagnostics platformに載るデータと判定ロジックを提供する。
- 価値はクラウド基盤ではなく、EPS専門の兆候指標と解釈ロジック。

### 5. EPS is becoming more safety-critical in ADAS / automation / steer-by-wire context

EPSはすでにADASの基盤機能であり、steer-by-wireや高可用EPSではさらに安全・可用性の重要度が上がる。
サプライヤ資料でも、高可用EPS、冗長センサ、冗長ECU、冗長電源・通信などが訴求されている。

Implication for this repo:

- EPSのhealth telemetryは、単なる保全ではなく、ADAS / automated driving / steer-by-wireの可用性説明に接続し得る。
- ただし、ADAS可用性保証そのものをサプライヤ単独で主張するのは危険。
- `EPS-side health evidence for connected operation` に留める方がよい。

## Demand Hypotheses

### H1. OTA Pre-update EPS Health Gate

OTA実行前に、EPSが更新に適した状態かを確認する。

Demand owner:

- OEM OTA operations
- OEM software update governance
- EPS system owner
- safety / compliance team

Possible outputs:

- update allowed
- update deferred due to EPS DTC
- update deferred due to low voltage / unstable power history
- update deferred due to assist limitation history
- additional diagnostics recommended

Value:

- OTA失敗や更新後トラブルの低減
- 安全関連ECU更新時の説明性
- R156 / SUMS運用でのトレーサビリティ

### H2. Post-update EPS Regression Monitor

OTA後に、EPS関連の異常兆候が増えていないかを見る。

Demand owner:

- OEM software quality
- OEM market quality
- EPS system supplier
- calibration team

Possible outputs:

- no EPS-related regression signal
- current tracking warning increased after update
- sensor redundancy warning increased after update
- assist limitation events increased after update
- software / calibration cohort check recommended

Value:

- OTA後の市場不具合検知
- update rollback / campaign pause判断の補助
- software version / calibration差分の影響確認

### H3. Connected EPS Degradation Indicators

故障断定ではなく、EPSシステムの劣化・負荷兆候を低頻度に収集する。

Demand owner:

- EPS gear / system supplier
- OEM market quality
- OEM service engineering
- fleet / commercial OEM

Possible indicators:

- same-condition assist current increase
- friction / load proxy trend
- torque sensor zero drift / redundancy drift
- steering angle sensor redundancy drift
- high-load steering event accumulation
- end-stop / curb-hit-like event accumulation
- thermal derating frequency
- low-voltage assist limitation frequency

Value:

- 故障予測に必要なデータセット構築
- ロット / 地域 / 車種 / calibration別の兆候偏り検出
- 返却品解析前の市場兆候把握

### H4. EPS Supplier Feedback Loop

OEMが持つconnected dataから、EPSシステムサプライヤへ兆候サマリを返す。

Demand owner:

- EPS system supplier
- OEM supplier quality
- OEM purchasing / quality

Possible outputs:

- anonymized cohort health report
- vehicle model / region / lot trend
- calibration version comparison
- suspected mechanical load trend
- event rate trend by EPS variant

Value:

- EPS supplierが市場データを直接持てない問題を緩和
- 次期設計 / diagnostic design / calibration改善に使える
- サプライヤ契約に含められる可能性

## Channel Role of OTA / Connected Diagnostics

現時点で一番よい候補は、OTA専用商品ではない。

> EPS Health Intelligence Package

One-line:

> EPS内部信号から故障可能性・劣化兆候・予測用データ材料を作り、OTA / remote diagnostics / service / return-part analysisなど複数チャネルで利用可能にする。

What it includes:

- degradation indicator definitions
- prognostic data package
- EPS health summary DID / API design
- service / return-part analysis view
- optional pre-update / post-update check view
- low-bandwidth event counters
- version / calibration / production metadata
- interpretation guide
- false-positive / non-goal policy

## How OTA Helps Without Becoming the Main Product

OTA / connected operationは、EPS health indicatorを市場で読むための便利な接点である。
しかし、OTAそのものを売るわけではない。

| Main value | Channel / use |
|---|---|
| EPS劣化兆候 | OTA / remote diagnosticsで定期読出し |
| 故障予測用データ材料 | OEM cloudやVHMで蓄積 |
| 返却品解析用の使用履歴 | サービス入庫や返却時に読出し |
| 更新前後のEPS状態 | OTA時の追加ユースケース |
| EPSメーカーへの市場feedback | OEMから集計・匿名化して返す |

## Key Constraints

この方向でも、制約は重い。

- EPS自体のOTA頻度はinfotainmentやADASより低い可能性がある
- OTA接点があっても、EPS内部データを自由にクラウド送信できるとは限らない
- OEMがconnected dataの所有者であり、サプライヤ単独で直接サービス化しにくい
- 劣化兆候はタイヤ、路面、アライメント、温度、運転癖に強く影響される
- 故障教師データは少ない
- 安全関連の誤通知・過通知は責任問題になる
- データプライバシー、通信量、診断セキュリティの制約がある

## Positioning Guardrails

Avoid:

- 個車に「EPSが故障します」と通知する
- EPS単体で故障予測精度を売る
- サプライヤ単独でOEM fleetを監視できると言う
- OTA後の安全性を保証すると言う
- リコールや保証判断を自動化すると言う

Prefer:

- EPS-side health indicators
- connected diagnostics-ready evidence
- pre-update health gate support
- post-update EPS regression monitoring
- degradation signal collection for OEM / supplier engineering review
- low-bandwidth health summary

## Source Notes

- UNECE R156 establishes software update management requirements for vehicle manufacturers and supports the need for safe, traceable software update operation.
- ASAM SOVD and ISO 17978 show that diagnostics are moving toward remote, in-vehicle, service-oriented APIs for software-defined vehicles.
- OEM announcements from Hyundai and GM show OTA moving from niche feature to lifecycle software platform.
- OTA / SDV vendors such as Sonatus, Sibros, and Excelfore position OTA together with diagnostics, data collection, health monitoring, predictive maintenance, and campaign traceability.
- EPS / steer-by-wire supplier materials and research show rising importance of safety, availability, redundancy, sensor health, motor current behavior, and anomaly detection in steering systems.

References:

- UNECE R156: https://unece.org/transport/documents/2021/03/standards/un-regulation-no-156-software-update-and-software-update
- UNECE R156 PDF: https://unece.org/sites/default/files/2024-03/R156e%20%282%29.pdf
- ASAM SOVD: https://www.asam.net/standards/detail/sovd/
- ISO 17978-3:2026 SOVD API: https://www.iso.org/standard/86587.html
- ISO 17978-1:2026 SOVD principles: https://www.iso.org/standard/85133.html
- Hyundai SDV / OTA roadmap: https://www.hyundai.news/uk/articles/press-releases/hyundai-announces-future-roadmap-for-software-defined-vehicles.html
- GM Ultifi: https://news.gm.ca/en/home/newsroom.detail.html/Pages/news/ca/en/2021/Sep/0929-ultifi.html
- Sonatus Updater: https://www.sonatus.com/products/updater/
- Sonatus Collector AI: https://www.sonatus.com/products/collector/
- Sibros Predictive Maintenance: https://sibros.tech/products/fleets/predictive-maintenance
- Excelfore Diagnostics: https://excelfore.com/diagnostics
- Nexteer High Availability EPS: https://www.nexteer.com/high-availability-eps-2/
- EPS anomaly detection research: https://pmc.ncbi.nlm.nih.gov/articles/PMC9699008/
