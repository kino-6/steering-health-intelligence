# FAM08 Stop-Start Low-Speed Coverage Benchmark Sample

## 結論

このsampleは、`EPS Diagnostic / Robustness Coverage Benchmark` がビジネス価値を持つかを最短で確認するための1ページ相当の叩き台である。

狙いは、Tesla固有のリコール解析ではない。
公開市場で見えた `停止後発進/低速時のassist loss` というdriver-visible painを、EPSサプライヤが持つ診断・評価・HILS/benchのcoverage reviewへ変換できるかを見る。

このsampleを診断設計/評価/HILS担当に見せて、次のどちらかを判定する。

- Proceed: program review、diagnostic design review、HILS test planningに使える
- Kill: 既存HILS test plan、DTC仕様、safety caseの言い換えでしかない

## 市場需要

公開市場では、低速時または停止後発進時に操舵assistを失うと、driver-visible painが大きくなる。
NHTSA 25V092の公開recall文脈では、電子power steering assistのPCBが過負荷状態になり、車両が停止して再加速した時にassist lossが起こり得ると説明されている。

参照:

- NHTSA recall acknowledgement 25V092: https://static.nhtsa.gov/odi/rcl/2025/RCAK-25V092-7349.pdf
- NHTSA Part 573 Safety Recall Report 25V092: https://static.nhtsa.gov/odi/rcl/2025/RCLRPT-25V092-6812.PDF
- AP News summary of the recall: https://apnews.com/article/cbed013def930add1bf27897ddc92103

## 未解決の痛み

EPSサプライヤ側の未解決痛みは、`このcaseのroot causeを当てること` ではない。

より実務的な問いはこれ。

> サプライヤEPSの既存DTC、freeze frame、extended data、reader、HILS/bench評価は、停止後発進/低速操舵中のassist lossという市場painを説明・再現・判定できるか。

ここに答えられるなら、validation planning、diagnostic design review、software/calibration release gateに接続できる。

## 仮説

`FAM08 stop-start low-speed` は、個別RCAよりもcoverage benchmarkに向く。

理由:

- driver-visible painが明確
- stop-to-launch、低速、操舵入力、assist demandに分解しやすい
- EPSサプライヤのbench/HILSで再現しやすい可能性がある
- power transient、motor drive、assist state、software/calibration、DTC/freeze frameへ接続できる
- 複数program / generationで同じchecklistを再利用できる可能性がある

## 1-page Coverage Benchmark

| Review item | Expected EPS facts | Supplier-owned source to check | Coverage question | HILS / bench scenario | Decision |
|---|---|---|---|---|---|
| Market pain | loss of assist after stop-to-launch | Public recall wording; internal complaint taxonomy | Reusable EPS scenarioとして扱えるか | stop-to-launch + steering input | Proceed / Hold / Kill |
| Scenario state | vehicle speed, standstill, launch, steering angle, driver torque/assist request | Vehicle CAN, EPS state, HILS plant model | steady low-speedだけでなく停止後発進を評価しているか | standstill -> steering input -> launch -> low-speed turn | Already covered / Gap |
| Power transient | battery voltage, EPS supply rails, motor driver DC link, reset/brownout/overvoltage flag | freeze frame, extended data, power-stage monitor, HILS power supply script | assist loss時点の電源/過電圧/reset文脈を説明できるか | assist demand中にvoltage disturbanceを注入 | Covered / Snapshot gap |
| Motor drive | assist command, actual motor current, current limit, current tracking error, inverter fault | motor control signals, DTC extended data, calibration monitors | assistが要求されたのか、制限されたのか、出せなかったのかを説明できるか | low-speed steering assist demand + motor driver stress | Covered / Need command-vs-current |
| Control state | assist enabled/disabled, derating, failsafe, fault latch, occurrence counter | EPS state machine, DEM/event memory, NvM counters, reader | final DTCだけでなく状態遷移を見られるか | repeated stop-launch near assist/failsafe boundary | Covered / Need scalar transition fact |
| Calibration | software version, calibration ID, parameter set, update/remedy version | DID, release notes, production traceability | field/returned unitをcalibration behaviorへ紐づけられるか | old/new calibration comparison | Covered / Version mapping gap |
| Diagnostic snapshot | DTC, pending DTC, freeze frame timestamp, speed, angle, voltage, current, thermal, assist state | DTC spec, freeze frame definition, extended data, reader | 既存診断だけでFAM08を説明できるか | trigger fault/DTC in FAM08 scenario | Already sufficient / Gap / No action |
| Validation evidence | test case ID, pass/fail, injected condition, expected DTC/state, measured response | HILS test plan, bench scripts, report template | FAM08がnamed test caseになっているか | automated HILS stop-launch steering assist robustness | New test / Existing duplicate |
| Program comparison | same fact list across Program A/B/C | platform diagnostic spec, program DTC list, HILS library | 複数programに横展開できるか | apply checklist to two generations | Reusable / Bespoke |
| Quality summary | confirmed, unconfirmed, do-not-infer, next checks | coverage review result, customer quality template | root cause断定なしに品質説明へ副次利用できるか | summarize benchmark result | Downstream only |

TSV版:

- [data/fam08_stop_start_low_speed_coverage_benchmark_sample.tsv](../data/fam08_stop_start_low_speed_coverage_benchmark_sample.tsv)

## 初期提供物

P0 sampleとしては、以下を1枚で提示する。

| Deliverable | 内容 |
|---|---|
| Market pain summary | stop-to-launch / low-speed assist lossの公開市場文脈 |
| Expected EPS fact list | speed、standstill、launch、steering input、assist command/current、voltage、motor drive、failsafe、calibration |
| Coverage matrix | DTC / freeze frame / extended data / reader / HILSでcoverできるか |
| Scenario skeleton | HILS/benchで実行するstop-launch steering assist robustness test |
| Decision row | already covered / gap / no action |
| Kill check | 既存HILS planやDTC仕様と差分があるか |

## 買い手/利用者

| Role | 何が嬉しいか |
|---|---|
| Validation / HILS | 公開市場painをnamed test caseへ変換できる |
| Diagnostic engineering | 既存DTC/freeze frameで説明できる範囲と不足を確認できる |
| Motor control / calibration | stop-to-launch時のassist deliveryやfailsafe境界をrelease gateで確認できる |
| Program / platform lead | 複数program間でcoverage差分を比較できる |
| Customer quality | 問題発生時に説明できるfactと推定禁止を把握できる |

## 検証方法

診断設計/評価/HILS担当に、このsampleを見せて次の5問を確認する。

1. このscenarioは既存HILS/bench/vehicle evaluationにありますか。
2. 既存DTC/freeze frame/extended dataで、stop-to-launch時のassist lossを説明できますか。
3. assist command、actual current、current limit、power transient、failsafe stateのうち、どれが既に読めますか。
4. このcoverage matrixはprogram reviewやrelease gateに貼れますか。
5. 複数programに同じchecklistを使えますか。

## Kill条件

以下なら、この方向はKillまたは大幅修正する。

| Kill condition | 理由 |
|---|---|
| 既存HILS test planに同等scenarioとcoverage判断がある | 新規価値がない |
| DTC/freeze frame仕様書の焼き直しでしかない | 診断設計の既存業務をなぞっているだけ |
| 公開caseから評価条件へ落ちていない | 市場pain-to-coverage変換になっていない |
| programごとに完全に作り直しになる | スケールしない |
| RCA/8D転記以外の価値がない | 旧仮説へ戻っている |
| 高レート波形やOEM fleet dataが必須 | EPSサプライヤ単独の初期商品として重い |

## Chain-of-Verification

| Question | Evidence check | Confidence | Impact |
|---|---|---:|---|
| FAM08は市場painとして成立するか | NHTSA 25V092の公開recall文脈で、停止後再加速時のpower steering assist lossが示されている。 | High | Keep |
| EPSサプライヤが主語になれるか | power transient、motor drive、assist state、calibration、DTC/freeze frame、HILS/benchはサプライヤ側の手札に近い。 | Medium | Keep, but internal review required |
| ビジネス価値は証明済みか | まだ未証明。sampleを実務担当に見せて既存HILS planとの差分を確認する必要がある。 | Low | P0 sample止まり |
| 既存診断の言い換えではないか | そのリスクは高い。`already covered / gap / no action` 判定を必須にする。 | High | Add kill criteria |
| RCA/8Dへ戻っていないか | Quality summaryはdownstream onlyに限定した。 | High | Keep downstream only |

## EPSサプライヤとしての結論

このsampleで売ろうとしているものは、`故障予測` でも `追加ログ` でも `RCA代行` でもない。

売れる可能性があるとすれば、これ。

> 停止後発進/低速操舵中のassist lossという市場painに対して、サプライヤEPSの既存診断・reader・HILS/bench評価がどこまでcoverageしているかを、program横断で見えるようにする短期assessment。

次の判断は明確。

- 診断/評価/HILS担当が使えると言うなら、FAM02/FAM11にも展開する
- 既存レビューと同じと言うなら、Coverage Benchmark仮説はKill寄り
