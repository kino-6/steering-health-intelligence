# Steering Predictive Diagnostics Screening Plan

## 結論

次に実施することは、操舵系で `predictive diagnostics / predictive maintenance / vehicle health` と呼べる対象が本当にあるかを、短いscreeningで確認することである。

ここで作るのは、外販商品ではない。
EPSサプライヤが、Bosch型の予測ビジネスに対して操舵系のどの知識を出せるかを見極めるための作業計画である。

自然言語で言うと、次の確認である。

> 操舵系について、どの状態なら予測診断の対象にでき、どの整備行動やvehicle health説明へつながり、どこから先は残寿命、交換時期、安全保証、原因断定と言ってはいけないかを切る。

## 使う公式ソース

Bosch側の前提は、次の公式ソースに固定する。

1. Bosch Mobility, `Cloud and predictive diagnostics`
   <https://www.bosch-mobility.com/en/solutions/software-and-services/cloud-and-predictive-diagnostics/>
2. Bosch Mobility, `Predictive Diagnostics`
   <https://www.bosch-mobility.com/en/solutions/diagnostics/predictive-diagnostics/>
3. Bosch Mobility, `Data-driven intelligence`
   <https://www.bosch-mobility.com/en/solutions/software-and-services/data-driven-intelligence/>
4. Bosch Media Service US, `Bosch strengthens U.S. mobility services portfolio`, 2026-03-19
   <https://us.bosch-press.com/pressportal/us/en/press-release-30080.html>
5. Bosch Mobility, `Vehicle connectivity services for commercial vehicle`
   <https://www.bosch-mobility.com/en/solutions/connectivity/vehicle-connectivity-services-cv/>
6. Bosch Mobility, `Fleet maintenance and repair`
   <https://www.bosch-mobility.com/en/mobility-topics/fleet-solutions/maintenance-and-repair/>
7. Bosch Mobility, `Battery in the cloud insights`
   <https://www.bosch-mobility.com/en/solutions/software-and-services/battery-in-the-cloud/battery-in-the-cloud-insights/>
8. Bosch Mobility, `Brake pad wear sensor`
   <https://www.bosch-mobility.com/en/solutions/sensors/brake-pad-wear-sensor/>
9. Bosch Mobility, `Lifecycle powertrain services`
   <https://www.bosch-mobility.com/en/solutions/software-and-services/lifecycle-powertrain-services/>

Repo内の前提資料は、次を使う。

1. [docs/103_bosch_predictive_diagnostics_meaning_review.md](103_bosch_predictive_diagnostics_meaning_review.md)
2. [docs/104_steering_predictive_state_candidate_scan.md](104_steering_predictive_state_candidate_scan.md)
3. [docs/105_bosch_predictive_business_analysis.md](105_bosch_predictive_business_analysis.md)
4. [data/bosch_predictive_business_analysis.tsv](../data/bosch_predictive_business_analysis.tsv)
5. [data/steering_predictive_state_candidates.tsv](../data/steering_predictive_state_candidates.tsv)

## 判断したいこと

今回のscreeningで判断したいことは、次である。

1. 操舵系でpredictive diagnosticsの対象にできるstateがあるか
2. そのstateは、predictive maintenance actionへつながるか
3. vehicle health outputとして、サービス現場やOEMに説明できるか
4. Boschが言うremaining lifetime、replacement date、failure predictionへ進める条件があるか
5. EPSサプライヤ単独で言ってよいことと、OEM/fleet/platformなしでは言ってはいけないことを切れるか

## Phase 1: Bosch型予測ビジネスの要求を作業項目へ変換する

### Task 1: Boschの予測語を作業要求へ分解する

目的:

Bosch公式情報に出ている `predictive diagnostics`、`predictive maintenance`、`vehicle health`、`remaining lifetime`、`maintenance forecast`、`recommended replacement date` を、操舵系screeningで確認できる作業要求へ変換する。

Acceptance criteria:

- Bosch公式ソースごとに、入力、処理、出力、業務actionを1行で整理する
- 操舵系へ転用できる要求と、転用してはいけない要求を分ける
- `data/bosch_predictive_business_analysis.tsv` のBBA001-BBA010と対応づける

Verification:

- TSV列数が崩れていない
- 各行に公式URLが入っている
- Boschが公開していない操舵系RULを主張していない

Expected output:

- `data/steering_predictive_diagnostics_screening_requirements.tsv`

## Phase 2: 操舵系predictive state候補を再整理する

### Task 2: 既存候補をBosch型の出力へ並べ替える

目的:

既存の操舵系predictive state候補を、単なる故障モードやDTC候補ではなく、Bosch型の業務出力に接続できるかで並べ替える。

Acceptance criteria:

- 各stateについて、何を予測診断の対象にするのかを自然言語で書く
- 各stateについて、maintenance action、vehicle health output、diagnostic triage、quality/warranty investigationのどこへ接続できるかを書く
- 各stateについて、remaining lifetime / replacement date / failure predictionと言ってよいかを分ける

Verification:

- `docs/104` の候補と矛盾しない
- Boschの予測語を避けるための曖昧な言い換えを使わない
- EPS内部状態が公開されていないことだけをKill理由にしない

Expected output:

- `docs/107_steering_predictive_diagnostics_state_screening.md`
- `data/steering_predictive_diagnostics_state_screening.tsv`

## Phase 3: 必要データと権限境界を切る

### Task 3: 各stateに必要なデータを分類する

目的:

操舵系predictive stateごとに、必要なデータを、EPSサプライヤが定義できるもの、OEM/fleet/platformが必要なもの、公開情報では確認できないものへ分ける。

Acceptance criteria:

- DTC、freeze frame、extended data、limit state、温度、電源、通信context、修理結果feedbackのどれが必要かを書く
- 各データについて、EPSサプライヤが持てるか、OEM/fleet/platform依存かを明記する
- feedback loopなしで言えることと、feedback loopがないと言えないことを分ける

Verification:

- 内部事実が見えないことだけで候補全体を落とす旧ロジックに戻っていない
- 内部事実不足は、過剰主張を禁止する境界として扱っている
- OEM保証DBやfleet dataを前提にしすぎていない

Expected output:

- `data/steering_predictive_diagnostics_data_boundary.tsv`

## Phase 4: 業務成果物へ転記できるかを見る

### Task 4: EPSサプライヤ内の部署別に使い道を切る

目的:

操舵系predictive diagnosticsが、EPSサプライヤ内のどの部署の成果物へ転記できるかを見る。

Acceptance criteria:

- 診断企画、製品企画、品質改善、評価企画、顧客技術説明、service / aftermarket連携の6部署で確認する
- 各部署について、具体的な成果物名、使うstate、使う理由、言ってはいけないことを書く
- 少なくとも2部署で具体用途が出るかを判定する

Verification:

- 汎用テレマティクス、一般的な路面分類、ADAS、IDSと区別できている
- 既存DTC表や既存service manualの言い換えだけになっていない
- EPSサプライヤの主語で結論が書かれている

Expected output:

- `docs/110_steering_predictive_diagnostics_supplier_workflow_fit.md`
- `data/steering_predictive_diagnostics_supplier_workflow_fit.tsv`

## Phase 5: Proceed / Hold / Stopを決める

### Task 5: Screening結果を最終判断にする

目的:

操舵系predictive diagnosticsを、次の調査へ進めるか、保留するか、止めるかを判断する。

Acceptance criteria:

- Market demand、未解決の痛み、仮説、解決策、買い手 / 利用者、初期提供物、検証方法、Kill条件の順で書く
- EPSサプライヤとして売る、実施する、言ってはいけないことを明記する
- Proceed / Hold / Stopの条件を観測可能な形で書く
- Stop / Kill / Archiveを書く場合はRule Checkを本文に明示する

Verification:

- AGENTS.mdのRule Checkを満たしている
- Bosch公式ソースURLが本文または参照表に残っている
- 旧テーマのEPS交換時期予測SaaSへ戻っていない

Expected output:

- `docs/111_steering_predictive_diagnostics_screening_decision.md`
- `data/steering_predictive_diagnostics_screening_decision.tsv`

## Current File Numbering

実行中にProceed候補の深掘りを追加したため、計画時点の想定番号から一部ずれている。

現在の対応は次である。

| Phase | 内容 | Current output |
|---|---|---|
| Phase 1 | Bosch型予測ビジネス要求を操舵系screening要求へ変換 | `data/steering_predictive_diagnostics_screening_requirements.tsv` |
| Phase 2 | 操舵系predictive state候補を再整理 | `docs/107_steering_predictive_diagnostics_state_screening.md`, `data/steering_predictive_diagnostics_state_screening.tsv` |
| Proceed deep dive | Proceed候補を深掘り | `docs/108_steering_predictive_diagnostics_proceed_deep_dive.md`, `data/steering_predictive_diagnostics_proceed_deep_dive.tsv` |
| Phase 3 | 必要データと権限境界を切る | `docs/109_steering_predictive_diagnostics_data_boundary.md`, `data/steering_predictive_diagnostics_data_boundary.tsv` |
| Phase 4 | EPSサプライヤ内の部署別に使い道を切る | `docs/110_steering_predictive_diagnostics_supplier_workflow_fit.md`, `data/steering_predictive_diagnostics_supplier_workflow_fit.tsv` |
| Phase 5 | Proceed / Hold / Stopを決める | `docs/111_steering_predictive_diagnostics_screening_decision.md`, `data/steering_predictive_diagnostics_screening_decision.tsv` |

## Checkpoint

Phase 1-3が終わった時点で一度止める。

その時点で見ること:

1. steering predictive stateが3件以上残るか
2. そのうち2件以上がmaintenance actionまたはvehicle health outputへ接続できるか
3. remaining lifetimeやreplacement dateを言えないstateでも、診断企画または品質改善に使えるか
4. Bosch型platformを自前で作る話に逸れていないか

ここでstateが残らなければ、Phase 4-5へ行かずにHold / Stop候補として整理する。

## Proceed条件

次の条件を満たすなら、次段階へ進める。

1. 操舵系predictive stateが3件以上残る
2. 少なくとも2件が、predictive maintenance action、vehicle health output、diagnostic triage、quality/warranty investigationのいずれかへ接続できる
3. 少なくとも2部署で、既存成果物へ転記できる使い道が出る
4. Bosch公式情報の予測語と、操舵系の説明が対応している
5. 過剰主張なしで価値説明できる

## Hold条件

次の場合はHoldにする。

1. steering predictive stateはあるが、整備actionやvehicle health outputへの接続が弱い
2. 必要データがOEM/fleet/platformに依存し、EPSサプライヤ単独の成果物が薄い
3. 既存DTC表、service manual、品質分類との違いがまだ言えない
4. remaining lifetimeやreplacement dateを言うにはfeedback loopが必要だが、その入手経路が未確認である

## Stop条件

次の場合はStopにする。

1. 操舵系predictive stateが既存DTCやservice manualの言い換えにしかならない
2. EPSサプライヤ内の成果物へ転記できない
3. 価値説明に、未確認のremaining lifetime、replacement date、安全保証、root cause、保証費削減が必要になる
4. Bosch型platformやOEM/fleet dataがないと成立せず、EPSサプライヤの手札が残らない
5. 汎用テレマティクス、ADAS、IDS、路面分類と区別できない

Stopを書く場合は、必ずRule Checkを本文に入れる。

## 最初に実施する作業

最初の1回では、Phase 1とPhase 2まで実施するのがよい。

理由:

Boschの予測ビジネスを操舵系の作業要求へ翻訳し、その要求に対して既存のsteering predictive state候補が残るかを見れば、次にデータ境界や部署別転記へ進む価値があるか分かるためである。
