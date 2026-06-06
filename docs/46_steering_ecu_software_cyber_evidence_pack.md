# Steering ECU Software / Cyber Evidence Pack

## 結論

候補1+2は、単なるサイバー調査やSBOM作成として売ると弱い。
しかし、**EPS / steering ECUサプライヤがOEMや監査に説明するための部品単位の証拠セット**として切れば、探索価値がある。

売り物の中心は、以下である。

> steering ECUの診断アクセス、ソフト更新、SBOM、脆弱性影響判断、security access、fail-safe stateを、OEM説明・設計レビュー・監査回答に転記できる形へ整理する。

これはR155/R156認証、ISO/SAE 21434準拠保証、OEMのCSMS/SUMS代行ではない。
EPSサプライヤが自分の部品境界で説明できる材料を作る。

## 誰が嬉しいか

初期の利用者は、EPSのサイバーセキュリティ担当だけではない。
実際には、以下の横断業務に刺さる可能性がある。

| Role | 困っていること | このpackで渡すもの |
|---|---|---|
| EPS cybersecurity | TARAや要求はあるが、steering ECU固有の証拠に落ちていない | steering ECUのasset、attack surface、要求、試験証拠の対応表 |
| EPS software / release | ソフト更新、calibration ID、rollback、post-update確認を説明したい | software update evidence checklist |
| Diagnostics | 診断サービス、DID、routine、security accessの安全影響を説明したい | diagnostic access exposure table |
| Supplier quality / OEM response | OEMからSBOM、CVE、脆弱性影響の問い合わせが来る | SBOM-to-function impact mapとCVE triage response |
| Systems / safety | cyber異常時にEPSがどの状態へ遷移するかを説明したい | fail-safe / assist-state evidence map |

## なぜEPSサプライヤが主語になれるか

OEMが車両全体のCSMS、SUMS、型式認可、診断基盤を持つ。
ここは初期対象外に置く。

一方で、EPSサプライヤは以下を持つ。

- steering ECUのsoftware / calibration identity
- bootloader、diagnostic stack、communication stack、crypto libraryなどのソフト部品情報
- UDS session、DID、routine control、security accessの実装
- torque / angle sensor inputと冗長性の扱い
- assist limitation、warning、fail-safe / limp-home stateの設計意図
- component-level test evidence

つまり、車両全体のサイバーリスクは閉じられないが、**steering ECUとして何を持ち、何を許し、異常時にどう振る舞うか**は説明できる。

## 初期商品案

### 1. Fixed-scope assessment

2週間程度の固定スコープで、対象steering ECUの既存資料を軽く棚卸しし、OEM説明に使える証拠の過不足を整理する。

入力:

- 診断サービス一覧
- software / calibration version管理資料
- SBOMまたはソフト部品表
- security access / session設計
- software update手順
- fail-safe / assist stateの概要

出力:

- steering ECU asset and attack-surface map
- diagnostic access exposure table
- software update evidence checklist
- SBOM-to-EPS-function impact map
- CVE triage response template
- fail-safe / assist-state evidence map
- OEM response one-pager

この案は、内部資料を使う場合の有償assessmentに近い。
ただし、`Coverage Benchmark` と違い、公開規制・標準側の需要が先にあり、故障予測や市場不具合解析を主張しない。

### 2. Public-demo starter kit

内部資料を使わず、仮想steering ECU構成で成果物の形だけを見せる。

入力:

- 公開標準・公開ガイダンス
- 一般的なsteering ECU構成
- 仮想SBOM
- 仮想診断サービス

出力:

- デモ用evidence matrix
- デモ用SBOM impact table
- デモ用CVE triage row
- デモ用OEM response page

この案は、売る前の見せ方を作るためのもの。
まずはこちらから始める。

## 最小デモ

今回作った最小デモは、実在製品ではなく仮想steering ECUを置く。
目的は、汎用TARAや汎用SBOMの言い換えではなく、EPSサプライヤの業務成果物に見えるかを確認することである。

仮想構成:

- dual torque sensor input
- steering angle input
- motor control MCU
- bootloader
- UDS diagnostics
- security access
- software / calibration ID
- RTOS
- crypto library
- CAN communication stack
- assist limitation / fail-safe state

見る対象:

| 対象 | 見る問い | 成果物 |
|---|---|---|
| 診断アクセス | 量産診断で何を許し、何を拒否するか | service exposure table |
| ソフト更新 | 更新の正当性、復旧、post-update確認を説明できるか | update evidence checklist |
| SBOM | ソフト部品がEPS機能と紐づいているか | SBOM-to-function map |
| CVE triage | 脆弱性がEPS機能に影響するかを説明できるか | CVE impact decision row |
| sensor input | 異常入力やmanipulationに対して安全状態を説明できるか | sensor cyber-safety row |
| communication | どの通信がEPS挙動に影響するかを分類できるか | communication boundary table |
| fail-safe state | 異常時にどのassist stateへ遷移するかを説明できるか | assist-state evidence map |

## サンプルCVE triage

| Component | 仮想脆弱性 | EPS機能影響 | 判断 | OEM回答 |
|---|---|---|---|---|
| crypto library | 署名検証に影響する可能性 | bootloader / software update | 要確認 | EPS update pathで該当API利用有無を確認中。利用ありの場合は署名検証試験を再実施する |
| CAN stack | malformed frame処理に影響する可能性 | in-vehicle communication | 影響ありの可能性 | EPSが受信する安全影響messageを特定し、negative testとgateway前提を確認する |
| diagnostic stack | security access bypassの可能性 | UDS diagnostics | 影響大 | production session、routine control、DID access、seed/key handlingを確認し、修正またはaccess制限を提示する |
| logging utility | debug log formatting issue | production EPS function | 影響なし候補 | production buildにdebug utilityが含まれるかを確認し、含まれない場合は影響なしとして記録する |
| RTOS scheduler | task starvation issue | motor control / monitoring | 要確認 | watchdog、monitoring task、assist state transitionへの影響を確認する |

この表の価値は、CVEを当てることではない。
OEMから聞かれた時に、`影響あり`、`影響なし`、`未確認`、`確認中` をEPS機能と証拠に紐づけて答えることである。

## ビジネスモデル

最初はSaaSにしない方がよい。
理由は、顧客ごとのCSMS/SUMS、SBOM形式、OEM回答様式、診断資料、toolchainが違うためである。

初期は以下が現実的である。

| Model | 内容 | 向き不向き |
|---|---|---|
| Fixed-fee assessment | 2週間程度で既存資料を棚卸しし、証拠mapとgapを返す | 初回案件化しやすい。人手依存 |
| RFQ / audit response support | OEMからのサイバー/SBOM要求に対する回答資料を作る | トリガが明確。案件依存 |
| Template + workshop | steering ECU向けテンプレートを渡し、半日-2日で埋め方を支援 | 軽く始めやすい。単価は低め |
| Per-program NRE | 量産program向けに証拠体系を整備する | 収益性はあるが、内部資料が必要 |
| Tool化 / SaaS | SBOMとCVE triageを継続運用する | 将来候補。初期は汎用ツールとの差分が弱い |

## 何が既存業務と違う可能性があるか

既存業務:

- CSMS / TARA
- ISO/SAE 21434 work products
- SBOM生成
- CVE管理
- UDS診断仕様
- software update仕様
- functional safety safety case

このpackが違う可能性:

- それらを個別資料のままにせず、steering ECUのOEM説明文へつなぐ
- SBOMを部品表で終わらせず、EPS機能影響へつなぐ
- diagnostic accessを単なるUDS一覧でなく、安全影響と禁止操作へつなぐ
- fail-safe stateを安全設計だけでなくcyber abnormal conditionへの説明に使う
- OEM問い合わせに対して、確認済み、未確認、推定禁止を分ける

## Kill条件

以下なら、この方向は止める。

- 既存CSMS/TARAにsteering ECU固有のasset、threat、requirement、test evidence、OEM回答文が既にある
- 既存SBOM/CVE運用に、EPS機能影響、release ID、software/calibration ID、影響判断履歴が既に含まれている
- 診断アクセス、software update、security accessの資料はOEM指定様式で完全に固定され、サプライヤ側に提案余地がない
- EPS cybersecurity / software / diagnostics / systemsのどの部門にも利用先がない
- デモを見ても、汎用CSMS/TARAや汎用SBOMツールとの差分が説明できない

## Proceed条件

以下なら、次に進む。

- EPS cybersecurity担当が、OEM回答や監査準備に転記できると言う
- software / release担当が、update evidenceとsoftware/calibration ID整理に使えると言う
- diagnostics担当が、security accessやroutine/DIDの安全影響整理に使えると言う
- supplier qualityやsales engineeringが、RFQやOEM問い合わせ回答の材料として使えると言う
- 既存資料はあるが、部門ごとに散っていて、OEM向けの1枚説明に落ちていない

## EPSサプライヤとしての言い方

言えること:

> EPS / steering ECUのソフトウェア構成、診断アクセス、ソフト更新、脆弱性影響、異常時状態を、OEM説明や監査で使える部品単位の証拠に整理する。

言ってはいけないこと:

- 車両全体のサイバーセキュリティを保証する
- R155/R156やISO/SAE 21434の認証を代行する
- SBOMを作れば安全になる
- 脆弱性件数が少なければ安全である
- EPS故障や事故を予測する

## 次アクション

次は、今回の仮想デモをHTMLか1ページ資料にして、以下の観点で見る。

1. 1ページで価値が伝わるか
2. 汎用サイバー資料ではなく、steering ECU向けに見えるか
3. SBOMとCVE triageがEPS機能影響に接続しているか
4. OEM回答に転記できる言葉になっているか
5. 既存業務の焼き直しに見えないか

ここで弱ければ止める。
強ければ、次は有償assessmentの提案書に落とす。
