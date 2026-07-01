# S2E001 Diagnostic Evidence Review Template

## 結論

`S2E001 low_speed_high_effort` の現時点の結論は **Hold**。

理由は、公開データだけでは「既存DTC / freeze frame / extended dataで足りない」と断定できないから。
今回のテンプレートは、ユーザに内部資料を要求するためのものではない。
この仮説をこれ以上Proceed扱いしないための判定ゲートである。

つまり、続きは以下のどちらか。

| 選択肢 | 判断 |
|---|---|
| 内部DTC仕様・freeze frame・extended dataを確認できる | `data/s2e001_diagnostic_evidence_review_template.tsv` を埋めてProceed / Kill / Holdを判定する |
| 内部仕様を確認できない | S2E001は事業仮説としてはHold。公開データ分析を増やしても価値証明には進まない |

したがって、現時点での結論は:

> S2E001は、公開データ上の評価シナリオとしては使えるが、EPSサプライヤ向けの追加証跡商品としては未成立。

## 今回の位置づけ

前回のgap checkでは、候補を3つまで絞った。

| Candidate | 内容 | 価値が出る条件 |
|---|---|---|
| A | Demand-to-output margin snapshot | assist command / motor current / current tracking errorが現行snapshotに無い |
| B | Limit / derating reason snapshot | current limit / thermal / voltage limitation / assist limitation reasonが現行DTCに残らない |
| C | Pre-event scalar summary | DTC発火前1-3秒のsummaryが既存event memoryに無い |

今回のテンプレートは、これらをDTC / event familyごとに判定する。

## 生成物

| File | 内容 |
|---|---|
| `data/s2e001_diagnostic_evidence_review_template.tsv` | 内部DTC仕様を入れてCandidate A/B/Cの必要性を判定するテンプレート |
| `generated/s2e001_diagnostic_evidence_review_template.html` | レビュー手順と判定ルールのHTMLビュー |

## 入力する情報

各DTCまたはevent familyについて、最低限以下を埋める。

これは「この資料を必ず集めるべき」という意味ではない。
集められないなら、S2E001はその時点でHoldまたはKillに寄せる。

| 入力項目 | 目的 |
|---|---|
| `dtc_or_event_family` | assist loss、current limit、voltage、thermal、torque sensorなどの対象分類 |
| `trigger_or_symptom` | DTC発火条件または顧客症状 |
| `current_freeze_frame_fields` | 現行freeze frameで残る項目 |
| `current_extended_data_fields` | 現行extended dataで残る項目 |
| `supplier_reader_available` | 返却品解析時にサプライヤが読めるか |
| `candidate_a/b/c` | 不足/十分/不要/要確認の判定 |
| `nvm_feasibility` | 追加保存がNVM制約に収まるか |
| `oem_boundary_risk` | OEM承認や責任表現上のリスク |
| `report_wording_status` | 顧客品質報告で事実表現として使えるか |

## 判定ルール

最初のデフォルト判定は **Hold**。
Proceedは例外扱いにする。

### Kill

以下のどれかに当てはまるならKill。

- 現行freeze frame / extended dataでCandidate A/B/C相当が既に残る
- サプライヤの返却品解析readerで読めない
- NVM容量/書換頻度に収まらない
- OEM説明で使えない内部実装依存値しか残せない
- 顧客品質報告で原因断定に見えてリスクが高い

### Proceed

以下をすべて満たす場合だけProceed。

- 現行診断ではCandidate A/B/Cのどれかが明確に不足
- 追加する値はscalar summaryで済む
- 返却品解析readerで読める
- NVM制約内に収まる
- 顧客品質報告では「観測事実」として表現できる
- OEMデータや保証DBなしでもサプライヤ内部レビューに使える

### Hold

以下の場合はHold。

- 内部仕様が未確認
- DTCごとに差が大きく、一般化できない
- 市場painとの接続はあるが、対象EPSの過去案件に出ていない
- NVM制約や読出権限が未確認

## レビュー対象の優先順

### REV001 assist_loss_or_assist_limited

最優先。

ここで既存診断が十分なら、`S2E001` 全体はかなり弱くなる。

見る項目:

- speed / steering angle
- assist command
- motor current
- current limit
- voltage
- thermal
- assist state
- pre-event summary有無

### REV002 current_limit_or_motor_current_tracking

Candidate Aの価値判定に直結する。

見る項目:

- assist command
- actual motor current
- current tracking error
- current limit flag

### REV006 assist_mode_transition_or_failsafe

一過性・再現不能・復帰edgeに接続する。

見る項目:

- assist mode
- fail-safe state
- enable / disable edge
- last state transition reason

### REV009 nvm_budget_and_write_policy

Candidate Cを殺すか残すかを決める。

見る項目:

- 1イベントあたり保存可能byte
- 保存件数
- debounce
- write trigger
- retention / aging policy

## 期待される出力

テンプレートを埋めた後、以下のどれかに落とす。

| 出力 | 意味 |
|---|---|
| Existing sufficient | 現行診断で十分。追加提案なし |
| Candidate A only | Demand-to-output marginだけ不足 |
| Candidate B only | Limit / derating reasonだけ不足 |
| Candidate C only | Pre-event scalar summaryだけ不足 |
| A+B / A+C / B+C | 複数不足。ただしNVM制約で1-3個に絞る |
| OEM-dependent | OEM診断仕様/サービスツール/保証DBが必要 |
| Supplier-readout blocked | ECUに残せてもサプライヤが読めない |
| Kill | 価値なし、または実装/運用リスクが大きい |

## Chain-of-Verification

| 検証質問 | 確認結果 | Confidence | 修正 |
|---|---|---:|---|
| このテンプレートだけでProceed判断できるか | できない。内部DTC仕様を入力して初めて判定できる。 | High | `TO_FILL` / `TO_CHECK` を明示 |
| 追加証跡を前提にしていないか | Kill条件を先に置き、既存で十分なら終了する構造にした。 | High | 判定ルールをKill / Proceed / Holdに分けた |
| OEM領分に踏み込みすぎていないか | reader availability、OEM boundary risk、report wording statusを判定列に入れた。 | Medium | サプライヤ単独で読めない場合はblocked |
| NVM現実性を見ているか | REV009でNVM容量/書換頻度を独立レビュー対象にした。 | Medium | Candidate CはここでKillされやすいと明記 |
| 顧客品質報告の表現リスクを見ているか | REV010で観測事実/未確認/推定の分離を要求した。 | Medium | 原因断定ではなくfact summaryに限定 |

## 次に本当に必要なもの

ここから先は、公開データを増やすより内部仕様が必要。
これは「内部資料を出してほしい」という依頼ではない。
この方向性が成立するかどうかの判定条件である。

内部仕様が無い場合の結論:

> S2E001は公開デモ/評価シナリオとして止める。追加証跡ビジネス仮説としては進めない。

最小セット:

1. assist loss / assist limited系DTCのfreeze frame項目
2. current limit / current tracking系DTCのextended data項目
3. assist mode / failsafe transitionのevent memory有無
4. 返却品解析readerで読めるDID一覧
5. NVM保存制約

これが無いと、S2E001は永遠に仮説のままになる。
