# Best 5 Business Model Candidates

`business_model_feasibility_100.tsv` の100案から、ECUメーカー起点での成立性、EPSへの付加価値、OEMデータ非依存、初期PoC容易性を重視してBest5を選んだ。

## Selection Criteria

重視した評価軸:

- ECUメーカーが自ECU内部信号・診断設計・NVM・開発評価ログで始められる
- OEM fleet data / warranty DB / complaint DBを初期前提にしない
- EPS system / gear supplierに対して付加価値として説明できる
- 「ログ追加」ではなく、health-ready EPSとして差別化できる
- HILS / bench / durability logでデモしやすい
- 将来的にOEM VHM / connected diagnosticsへ拡張できる

## Best 5

| Rank | ID | Candidate | Why it is strong |
|---:|---|---|---|
| 1 | BMFE020 | Health-ready EPS Feature Bundle | Core機能をひとまとまりのEPS付加価値として売れる。ECUメーカー起点で成立し、OEMデータを初期前提にしない。 |
| 2 | BMFE001 | EPS Health Indicator Set Licensing | 指標定義と実装仕様をIP化しやすい。EPSメーカー / ギアメーカーがOEM提案に使いやすい。 |
| 3 | BMFE031 | Offline Health Indicator Analyzer | HILS / benchログで即デモできる。最初のPoCとして現実的で、指標の妥当性検証に使える。 |
| 4 | BMFE041 | Return-part Health Summary Reader | 返却品NVMからhealth summaryを読むため、OEM市場データなしでも価値を出しやすい。保証解析に近い。 |
| 5 | BMFE096 | Co-development with Gear Maker | ユーザ仮説に最も近い。ギア摩擦・ラック負荷proxyを、ギアメーカーと共同開発する形にできる。 |

## Candidate 1: Health-ready EPS Feature Bundle

### Summary

EPS Health Indicator Set、Health Summary DID、NVM evidence、indicator dictionary、false-positive policyをまとめた量産向けfeature bundle。

### Buyer

- Primary: EPS system / gear supplier
- Gatekeeper: Vehicle OEM

### Revenue Model

- per-program NRE
- unit price uplift
- optional indicator calibration service

### Why This Is Best

- 単一機能ではなく、EPS自体の付加価値として見せられる
- ECUメーカーが責任を持てるCoreに収まる
- 将来OEM VHMやconnected diagnosticsへ拡張できる
- 量産仕様に落としやすい

### Main Risk

範囲が広く、初期合意が難しい。最初はStarter Kitとして小さく切るべき。

## Candidate 2: EPS Health Indicator Set Licensing

### Summary

assist current / load proxy、sensor drift、current tracking、thermal stress、power stress、assist limitationなどのhealth indicatorを定義し、実装仕様・辞書・解釈注意とセットでライセンスする。

### Buyer

- EPS system supplier
- ECU platform owner
- diagnostic engineering team

### Revenue Model

- NRE
- IP license
- per-program reuse fee

### Why This Is Strong

- 「何を取るべきか」が商品になる
- OEMデータ不要で始められる
- ECU内部信号の知見を差別化にできる
- 複数車種やEPS variantへ横展開できる

### Main Risk

指標の独自性と物理的意味を示せないと、単なる信号リストに見える。

## Candidate 3: Offline Health Indicator Analyzer

### Summary

HILS / bench / durability log / fault injection logからhealth indicatorを計算し、normal / watch / check recommended のようなsummaryを出すデモ兼検証ツール。

### Buyer

- EPS development team
- validation team
- ECU supplier internal sponsor

### Revenue Model

- internal tool
- PoC package
- validation NRE

### Why This Is Strong

- すぐデモできる
- 量産connected dataが不要
- 指標の妥当性を早期検証できる
- Project CharterのPhase 1に直結する

### Main Risk

量産収益そのものではなく、PoC / validation止まりになる可能性がある。

## Candidate 4: Return-part Health Summary Reader

### Summary

返却品NVMから、熱、電源、アシスト制限、センサ冗長差、電流追従、一時異常復帰などの履歴を読み、health summaryとして出す。

### Buyer

- EPS quality team
- return-part analysis team
- warranty investigation team

### Revenue Model

- tool license
- NRE
- diagnostic feature package

### Why This Is Strong

- OEM fleet data不要で成立する
- 返却品解析という既存業務に接続できる
- No Trouble Foundや再現困難案件にも効く
- NVM evidence mapと相性が良い

### Main Risk

返却品解析用途だけだと、市場規模が限定される。

## Candidate 5: Co-development with Gear Maker

### Summary

EPS system / gear supplierと共同で、gear friction、rack load、harsh usage、end-stop stressなどのmechanical health proxyを開発する。

### Buyer

- EPS gear supplier
- EPS system supplier

### Revenue Model

- co-development NRE
- algorithm license
- future feature package

### Why This Is Strong

- EPSへの付加価値として一番筋が良い
- ECUメーカー単独では見えにくい機械劣化知識を、ギアメーカーと組み合わせられる
- OEMに対して「health-ready EPS」として差別化しやすい

### Main Risk

正規化が難しい。タイヤ、路面、アライメント、運転癖などの影響を受けるため、いきなり故障予測にしない。

## Recommended First Move

最初の実行案:

> BMFE098 Health Indicator Starter Kit を入口にして、BMFE031 Offline Health Indicator Analyzerでデモし、成功した指標をBMFE020 Health-ready EPS Feature Bundleへ拡張する。

Starter Kitの最小構成:

- current tracking warning count
- torque sensor redundancy delta
- steering angle sensor redundancy delta
- thermal derating accumulation
- low voltage stress history
- assist limitation recurrence

Demo:

- HILS / bench / sample logを入力
- health indicatorを計算
- health summaryを出力
- indicator dictionaryで解釈を説明

## Best Current Pitch

> EPSメーカー / ギアメーカー向けに、OEMデータを初期前提とせず、ECU内部信号・NVM・開発評価ログから始められるHealth Indicator Starter Kitを提供する。まずHILS / benchログで劣化兆候と誤検知要因を検証し、量産向けHealth-ready EPS Feature Bundleへ拡張する。
