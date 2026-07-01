# Steering ECU Software / Cyber Demo

## 結論

候補1+2を進めるため、仮想steering ECUを使った最小デモを作った。

このデモで見せたいことは、SBOMやTARAをただ並べることではない。
EPSサプライヤが、OEMから聞かれたときに、**どのソフト部品がどのEPS機能に触れるか、どの診断操作が安全影響を持つか、更新後に何を確認できるか**を説明できる状態にすることである。

## デモの構成

今回追加したTSVは以下。

| File | 役割 |
|---|---|
| `data/steering_ecu_software_cyber_offer_model.tsv` | 商品案、買い手、トリガ、収益モデル、Kill条件 |
| `data/steering_ecu_software_cyber_work_products.tsv` | 有償assessmentで作る成果物一覧 |
| `data/steering_ecu_cve_triage_demo.tsv` | 仮想CVEをEPS機能影響へつなぐデモ |

## 何を売るか

最初に売るなら、SaaSではなく固定スコープのassessmentである。

> 2週間程度で、対象steering ECUの診断アクセス、ソフト更新、SBOM、脆弱性影響、fail-safe stateを棚卸しし、OEM説明に使える証拠mapと回答テンプレートへ落とす。

初期成果物:

- steering ECU asset and attack-surface map
- diagnostic access exposure table
- software update evidence checklist
- SBOM-to-EPS-function map
- CVE triage response template
- fail-safe / assist-state evidence map
- OEM response one-pager

## CVE triageデモの読み方

`data/steering_ecu_cve_triage_demo.tsv` は、仮想CVEを使っている。
目的は、特定CVEの事実確認ではなく、回答の型を見ることである。

悪い回答:

> このCVEは関係ありません。

良い回答:

> affected componentがproduction EPS binaryに含まれるか、該当APIをbootloader/update pathで使っているか、該当するnegative testがあるかを確認し、影響あり/なし/未確認を分ける。

この違いが価値である。

## 既存業務との差分

既存のCSMS、TARA、SBOM、CVE管理、UDS仕様は既にある可能性が高い。
したがって、この方向の差分は、存在しない資料を新しく発明することではない。

差分候補は以下である。

- SBOMをEPS機能影響とrelease IDへ接続する
- diagnostic accessを安全影響と禁止操作へ接続する
- software updateをsoftware/calibration identityとpost-update stateへ接続する
- cyber abnormal conditionをassist limitation / fail-safe stateへ接続する
- OEM回答に転記できる自然言語へ落とす

## 判定

現時点では、探索継続でよい。
理由は、公開規制・標準で市場需要を説明でき、仮想デモでもsteering ECU固有の成果物に落ちているためである。

ただし、まだ「売れる」とは言わない。
次に確認すべきは、既存CSMS/TARA/SBOM/CVE運用との差分である。

Proceed条件:

- EPS cybersecurity / software / diagnosticsのいずれかが、既存資料よりOEM回答に使いやすいと言う
- SBOM-to-function mapが、既存SBOM運用にない視点だと確認できる
- diagnostic access exposure tableが、既存UDS仕様より説明に使いやすい

Kill条件:

- 既存CSMS/TARA/SBOM/CVE運用に同じ成果物が既にある
- OEM指定様式に完全に吸収され、サプライヤ側で提案余地がない
- EPS機能影響へ接続できず、汎用サイバー資料に見える

## 次に作るもの

次は、これを1ページHTMLまたは提案書にする。
そのときの見出しは、商品名ではなく以下がよい。

> OEMからのサイバー/SBOM問い合わせに、steering ECUの部品境界で答えるための証拠整理

この言い方なら、過剰に大きな主張をせず、EPSサプライヤの実務に戻せる。
