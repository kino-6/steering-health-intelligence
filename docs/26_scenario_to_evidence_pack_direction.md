# Scenario-to-Evidence Pack Direction

## 結論

Phase 2の `low-speed high-steering-demand proxy` は、それ単体では商品にならない。

方向性として筋があるのは、公開市場文脈と公開走行windowを使って、EPSサプライヤが次に見るべき内部信号と診断証跡を決めること。

提案名:

> EPS Scenario-to-Evidence Pack

これは故障予測器ではない。
市場で揉めやすいdriver-visible painを、評価シナリオ、内部信号、既存診断との差分、次の検証項目へ変換する設計支援パックである。

## なぜこの方向か

ユーザ指摘の通り、前回のHTMLは「データ分析しただけ」だった。

そこから得られる実務上の使い道は、次の1つに絞るべき。

> 市場で問題になりやすい操舵文脈を、EPSサプライヤがサプライヤ内評価・診断設計で扱える形に変換する。

これなら、OEMの保証DBやfleet dataを初期前提にしない。
また、既存DTC / freeze frame / extended dataを否定せず、むしろ「既存診断で足りるか」をレビューする入口になる。

## 作ったもの

| File | 内容 |
|---|---|
| `data/eps_scenario_to_evidence_pack.tsv` | 市場文脈、公開proxy window、評価シナリオ、内部信号、既存診断との差分、kill criterionを整理 |
| `generated/eps_scenario_to_evidence_pack.html` | 意思決定用のHTMLビュー |

## 方向性の型

```text
Public market pain
  -> public proxy window
  -> EPS supplier evaluation scenario
  -> supplier internal signals to check
  -> existing diagnostic overlap
  -> missing evidence hypothesis
  -> next test / kill criterion
```

この型にすると、議論が以下のように変わる。

| 弱い言い方 | 強い言い方 |
|---|---|
| 低速高操舵のwindowを検出しました | 低速高操舵でassist余裕が詰まる文脈を、HILS/bench評価と診断snapshot棚卸しに使います |
| 劣化兆候を見ます | 劣化は言わず、assist command/current/voltage/thermal/current limitが既存診断で説明できるかを見ます |
| 市場不具合を予測します | 市場で揉めやすい文脈を評価シナリオ化し、既存診断で説明可能かを確認します |
| 8D回答を支援します | 顧客品質報告や返却品解析で使う事実整理の材料を増やします |

## 優先シナリオ

### 1. low_speed_high_effort

最初に進めるならこれ。

理由:

- NHTSA公開事例でdriver-visible painとして分かりやすい
- commaSteeringControlで代表windowを抽出済み
- EPSサプライヤ内部信号に落としやすい
- 既存DTC / freeze frame / extended dataとの差分レビューに接続しやすい

見るべき内部信号:

- assist command
- motor current
- current limit
- torque sensor value / residual
- steering angle
- vehicle speed
- battery voltage
- EPS thermal state
- assist mode / state

評価すべき問い:

> このwindowでassist余裕が詰まった場合、現行DTC / freeze frame / extended dataだけで顧客品質説明に足るか。

### 2. gradual_turn_sticking_oversteer

次点で強い。

理由:

- Pacifica公開調査の文脈と今回の車種が近い
- driver painが具体的で、単なる「重い」より解析論点が立ちやすい
- 一過性/再現不能/assist復帰エッジというNTF寄りの課題に接続しやすい

ただし、公開走行データだけではassist disruptionは見えない。
価値は、内部のcontrol state transitionやassist enable/disable edgeを保存できるかに依存する。

### 3. warning_plus_low_speed_effort

DTCや警告灯と近いため、既存診断との重なりが大きい。

ここでの論点は「新しい診断を作る」ではなく、

> DTCに添える操舵文脈snapshotが顧客品質説明に効くか。

現行freeze frameで十分なら、この案はkillする。

## 今回あえて下げるシナリオ

### stop_start_low_speed_context

市場文脈は強いが、今回のPhase 2抽出では停止直後windowを十分に取れていない。
次にやるなら、0-5 m/sの抽出条件で再走査するか、別公開データに切り替える。

### rough_road_pothole_context

市場文脈はあるが、commaSteeringControlだけでは路面荒れを識別できない。
IMU / road conditionつき公開データが必要。

### MDPS power pack / ECU hardware

サプライヤ視点には近いが、走行window分析ではなくbench / EOL / return-part evidenceの文脈。
別トラックとして扱うべき。

## Chain-of-Verification

| 検証質問 | 確認結果 | Confidence | 修正 |
|---|---|---:|---|
| これは故障予測と言えるか | commaSteeringControlに故障ラベルやDTCはない。言えない。 | High | 「故障予測」ではなく「評価/診断設計支援」に修正 |
| EPSサプライヤ単独で始められるか | 公開市場文脈と公開windowでシナリオ仮説は作れる。内部信号棚卸しはサプライヤ側で始められる。 | Medium | OEMデータは初期前提にしない |
| 既存診断の言い換えではないか | DTC/freeze frame/extended dataは既存。価値は「既存で足りるかをシナリオ別にレビューすること」に置く。 | High | 追加証跡ありきにしない |
| 低速高操舵windowは市場痛みと直結するか | 直結はしない。正常走行proxyであり、driver pain文脈の評価入口に留まる。 | High | public_data_supportとcannot-proveを分離 |
| 次に何を判断できるか | どのシナリオを評価/診断設計レビューに進めるか、どのシナリオを後回し/killするか。 | Medium | priorityとkill criterionをTSVに追加 |

## 次にやるべきこと

20-50件の内部NTF/返却品ケースが無い前提なら、次は以下の順が良い。

1. `S2E001 low_speed_high_effort` を1件だけ選ぶ。
2. 上位window `LSHSD-001 / 003 / 005` を評価シナリオに変換する。
3. 対象EPSの現行DTC / freeze frame / extended data項目を棚卸しする。
4. `assist command / motor current / current limit / voltage / thermal / assist state` が残っているかを見る。
5. 残っていれば、この方向は「既存診断で十分」としてkillする。
6. 残っていなければ、NVM制約内で1-3個だけ追加候補を出す。

この判断まで行くと、ようやく「データ分析」ではなく「EPSサプライヤ向けの診断証跡設計レビュー」になる。
