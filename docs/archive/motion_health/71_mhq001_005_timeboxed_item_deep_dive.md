# MHQ001-MHQ005 10分Goal深掘りメモ

## 結論

10分Goalの結論は、前回の全体結論をitem別に分解すると次である。

1. 操舵系理由の運行停止・予定外入庫は、fleet一般の痛みとしては支持される。ただし操舵系固有ではまだPartial。
2. 買い手はfleet operator、OEM fleet service、remote diagnostics platformが先に見える。EPS/SbWサプライヤ直接販売はまだ弱い。
3. EPS/SbWサプライヤのデータアクセスは最大Kill gate。実使用データloopの公開例はあるが、DTC/DID、整備履歴、交換結果までは未確認。
4. 価値ある出力は、交換時期ではなく、運行可否、入庫優先度、診断優先度、部品準備でよい。これは強い。
5. Raw DTCだけでは粗い可能性はある。ただし既存remote diagnosticsがすでにrisk、criticality、repair priorityを扱っており、こことの差分が必要。

したがって、次に深掘るべきは `MHQ003` と `MHQ005` である。
`MHQ001` はsource数を増やして操舵系/chassis明示件数を数える。
`MHQ002` は買い手を直接買い手とサプライヤ内利用者に分ければ少し整理できる。
`MHQ004` は仮説の芯として採用してよい。

## Item Conclusions

詳細TSVは [data/archive/motion_health/motion_health_mhq001_005_item_conclusions.tsv](../../../data/archive/motion_health/motion_health_mhq001_005_item_conclusions.tsv) に置いた。

| Item | Conclusion | Confidence | Weak point | Next action |
|---|---|---|---|---|
| MHQ001 | Fleet一般のdowntime painは強い。操舵系固有ではNexteerが直接signal | Medium | steering-specific downtime frequencyがない | 20-50 source分類でsteering/chassis明示件数を数える |
| MHQ002 | 買い手はfleet/OEM service/remote diagnosticsが先。supplier directは弱い | Medium | EPS/SbW supplier側の予算が見えない | direct buyerとinternal userを分ける |
| MHQ003 | 最大Kill gate。actual lifecycle dataの公開例はあるが、DTC/DID/整備履歴/交換結果は不明 | Low to Medium | data rightsとdata fieldが見えない | data-rights mapを作る |
| MHQ004 | 交換時期ではなく運行/入庫/診断/部品準備が価値 | High | steering-specific output例が薄い | 1ケースsampleへ進める |
| MHQ005 | Raw DTCだけでは粗いが、既存remote diagnosticsが強い | Medium | supplier固有差分がまだ弱い | 操舵系domain knowledgeの差分を列挙する |

## Deepened Points

### MHQ003: データアクセス

Nexteer MotionIQ/Healthは、匿名化された実使用条件データをOEMとサプライヤの品質・開発insightに使うと説明している。
これは、サプライヤが実使用データloopへ入る公開例としては強い。

ただし、ここで言えるのはまだ「actual lifecycle conditionsを匿名化して使える場合がある」までである。
EPS固有DTC、DID、freeze frame、整備履歴、交換結果、再発有無、作業時間へアクセスできるとは言えない。

このため、次に必要なのはdata-rights mapである。

| Data | 初期見立て | 判断 |
|---|---|---|
| vehicle health summary | OEM/fleet/platform経由で共有される可能性あり | 使える可能性 |
| anonymized lifecycle conditions | Nexteer signalあり | 使える可能性 |
| EPS DTC / DID / freeze frame | OEM診断仕様・gateway・権限に依存 | 未確認 |
| service history / replacement result | fleet / dealer / OEM service領域 | 最大の壁 |
| supplier bench / HILS / durability knowledge | supplier側で持てる | 使える |

MHQ003の結論は、**ProceedでもKillでもなく、次の検証で最初に潰すべき門** である。

### MHQ005: 既存remote diagnosticsとの差分

Bosch cloud diagnosticsは、故障内容の説明、エラーコード、risk / criticality assessment、次ステップ推奨を説明している。
Geotabは大量のfault codeを理解し、repair priorityへ変換する価値を説明している。
PitstopやTeltonikaも、DTCのseverity、prioritized fault codes、action planningに近い領域を扱う。

つまり、`DTCを優先度に変換する` だけでは、既存remote diagnosticsに飲まれる。

EPS/SbWサプライヤ側に残る可能性がある差分は、以下に限定される。

- assist state、limit state、thermal derate、motor current、voltage、communication stateの意味づけ
- software / calibration IDと症状・診断判断の接続
- SbW redundancy degraded / fallback stateを運行可否へ翻訳すること
- どのDIDを先に読むべきかのsteering domain triage
- bench / HILS / durability knowledgeから、fleet側に言ってよいこと・言ってはいけないことを切ること

MHQ005の結論は、**raw DTC不足は支持されるが、汎用remote diagnosticsとの差分はまだ未証明** である。

## Market Demand First

| Field | 内容 |
|---|---|
| Market demand | 自動運転・商用車両群では、車両停止、予定外入庫、診断時間、部品待ちが運行効率を落とす。 |
| Unresolved pain | 操舵系/chassis系の状態が、運行可否や点検優先度へ十分に翻訳されているかは未確認。 |
| Hypothesis | EPS/SbWサプライヤのdomain knowledgeを、fleet/OEM serviceの運行・整備判断へ翻訳できれば価値がある。 |
| Solution | 20-50 source分類、data-rights map、1ケースの運行可否/入庫優先度sample。 |
| Buyer / user | OEM fleet service、remote diagnostics、fleet maintenance、supplier diagnostics / service engineering。 |
| Initial artifact | item conclusion table、data-rights map、steering domain triage sample。 |
| Validation method | steering/chassis明示source件数、data field access、既存remote diagnosticsとの差分を確認する。 |
| Kill criteria | data access不可、既存remote diagnosticsで十分、steering/chassis painが出ない、交換時期予測に戻る。 |

## EPS Supplier Lens

EPS/SbWサプライヤとして売るか:

> まだ売らない。

EPS/SbWサプライヤとして実施できること:

> Data-rights mapを作り、EPS/SbW側で持てるDTC/DID/状態量と、OEM/fleet/service側に依存する履歴・交換結果を分ける。

言ってはいけないこと:

> EPS交換時期を正確に予測できる、保証費を削減できる、root causeを断定できる、安全機能を予測で代替できる、とは言わない。

次に見せる部署:

> diagnostic engineering、service engineering、quality / field quality、customer technical interface。

## Stop / Continue Judgment

この10分Goalでは、Skillの早期停止条件は満たした。

- 各itemの結論、confidence、weak point、next actionを明示した
- 弱いitemとしてMHQ003とMHQ005を深掘りした
- 次に作るべきartifactがdata-rights mapとsteering domain triage sampleへ絞れた

継続するなら、次Goalは `20-50 source分類` ではなく、まず `MHQ003 data-rights map` がよい。
データアクセスが崩れると、新テーマ全体が旧テーマと同じ理由で止まるためである。

## Sources

- Nexteer MotionIQ/Health: https://www.nexteer.com/release/nexteer-unveils-its-motioniq-software-suite-for-intelligent-motion-control/
- Nexteer MotionIQ blog: https://www.nexteer.com/blog/motioniq-software-suite-precision-speed-and-quality-for-software-defined-chassis-development/
- Nexteer Software: https://www.nexteer.com/software/
- Bosch cloud and predictive diagnostics: https://www.bosch-mobility.com/en/solutions/software-and-services/cloud-and-predictive-diagnostics/
- Geotab remote diagnostics: https://www.geotab.com/blog/remote-diagnostics/
- Pitstop prioritized fault codes: https://pitstopconnect.com/2022/08/15/prioritized-fault-codes-to-simplify-truck-maintenance/
- Teltonika remote DTC reading: https://www.teltonika-gps.com/use-cases/logistics-and-delivery-services/remote-dtc-reading-for-proactive-heavy-fleet-maintenance
