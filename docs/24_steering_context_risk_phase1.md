# 24. Steering Context Risk Explorer: Phase 1 Static Report

## Purpose

`docs/23_public_proxy_demo_plan.md` のPhase 1として、ダウンロード不要の静的分析を実施した。

Input:

- `data/eps_public_market_pain_cases.tsv`
- `data/public_steering_dataset_inventory.tsv`

Outputs:

- `data/steering_context_risk_phase1_summary.tsv`
- `generated/steering_context_risk_explorer_phase1.html`

## Conclusion

公開ケースだけで言える結論:

> EPS assist loss / increased steering effort は、driver-visible painとして繰り返し現れる。特に、低速時の操舵努力増加、警告表示、断続的assist loss、ignition-cycle単位の回復、gradual turn中のsticking / sudden assist returnが目立つ。

公開ケースだけでは言えない結論:

> EPS故障予測、DTC / freeze frame不足、返却品解析価値、サプライヤ内部の診断証跡価値は証明できない。

したがって、Phase 1の価値は次に限定する。

> ドライバーが痛みを感じるEPS文脈を整理し、公開steering datasetでproxy表示できる候補を選ぶ。

## Market Pain Map

### Strongest proxy feature hints

| Proxy feature hint | Count | Interpretation |
|---|---:|---|
| intermittent_ignition_cycle | 8 | assist lossがignition cycle中続き、restartで戻る可能性があるパターン |
| warning_plus_low_speed_effort | 4 | warning / MIL / chime と低速時の操舵努力増加が結びつくパターン |
| low_speed_high_effort | 4 | 低速時にmanual steering effortが大きくなるパターン |
| voltage_temperature_friction_context | 3 | Ford investigationで、既存DTC文脈にvoltage / temperature / frictionが含まれる |
| rough_road_pothole_context | 2 | rough road / pothole後のassist loss文脈 |
| stop_start_low_speed_context | 2 | stop後、再発進時にassist lossが顕在化する文脈 |
| gradual_turn_sticking_oversteer | 2 | gradual turnでsticking感やassist急復帰が起きる文脈 |

### Source distribution

| Source type | Count | Usefulness |
|---|---:|---|
| NHTSA ODI investigation | 10 | complaints, population, crash allegations, warranty claimsなどの濃い材料がある |
| NHTSA recall bulletin | 6 | remedyと症状記述がある |
| NHTSA recall FAQ | 6 | driver-facingな説明が拾いやすい |
| NHTSA recall acknowledgement | 5 | affected populationとdefect summaryが拾える |
| WardsAuto / NHTSA-based report | 2 | NHTSA由来情報の補助。primary sourceではない |

## What This Suggests

### 1. Low-speed high effort is the first demo axis

公開ケースでは、assist loss時に低速で操舵努力が増えるという説明が繰り返し出る。

Proxy demoでは、次を最初に見るべき。

- speedが低い
- steering angle / steerFilteredが大きい
- steering rateが高い
- maneuverが連続する

This does not prove:

- EPSが壊れている
- assist currentが不足している
- DTCが出る

It only shows:

- assist lossが起きた場合に、ドライバー負担が大きそうな文脈

### 2. Intermittent / ignition-cycle behavior is a strong public narrative

GM/Cadillac/Chevrolet系の公開ケースでは、assist lossがignition cycle中継続し、restart後に戻る可能性がある、という文脈が複数回出る。

Proxy demoでは、実故障を扱えないため、以下のような表示に留める。

- event window
- recovered / not observed placeholder
- missing EPS-local evidence

This does not prove:

- restartで本当に回復する原因
- ECU内部イベントの種類
- NTF価値

### 3. Existing EPS diagnostics already include useful context

Ford Fusion / MKZ / Milan investigationでは、DTC例としてlow/high voltage、PSCM temperature、internal system fault、high frictionなどが出ている。

これは重要。

> voltage / temperature / friction contextは新規価値ではなく、既存診断にも含まれ得る。

したがってデモでは、`新しい診断を発明した` ではなく、

> 公開データでは見えないEPS-local evidenceとして、既存診断やDTC文脈が必要になる

と示すのが正しい。

### 4. Public data can create a boundary demo

Phase 1で一番価値があるのは、予測ではなく境界の可視化。

| Question | Public data can show | Still missing |
|---|---|---|
| Where would assist loss hurt? | low-speed / high steering demand / gradual-turn contexts | driver torque / EPS assist current |
| Did the driver see a warning? | public case text sometimes says yes | actual DTC / warning log |
| Was EPS failing? | no | EPS fault label / return-part analysis |
| Is it OEM-buyable? | no | OEM value / feature adoption evidence |

## Recommended Static Demo

`generated/steering_context_risk_explorer_phase1.html` should be treated as a static Phase 1 artifact.

It shows:

- public case count
- top proxy feature hints
- source type distribution
- strongest driver pain categories
- evidence gap overlay
- what the demo does not prove

It does not:

- run a predictive model
- download public steering datasets
- infer EPS failures
- claim direct OEM demand

## Next Action

Proceed only if Phase 1 is considered useful.

If yes:

1. Download or sample `commaSteeringControl`
2. Compute low-speed high steering demand windows
3. Visualize steering demand vs speed
4. Add an explicit `missing EPS-local evidence` overlay

If no:

Stop this direction before building a dataset notebook.
