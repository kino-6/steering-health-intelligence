# Low-speed high-steering-demand proxy Phase 2

## 結論

commaSteeringControlの `CHRYSLER_PACIFICA_2018` を使い、低速かつ操舵要求が高い代表windowを抽出できた。

ただし、これはEPS故障、劣化兆候、DTC不足を示すものではない。公開走行データで言えるのは、NHTSA等でdriver-visible painとして頻出する「低速で操舵力が重い/assist lossが問題になりやすい」文脈に対して、正常走行データ上のproxy windowを作れる、というところまで。

## 生成物

| File | 内容 |
|---|---|
| `scripts/extract_low_speed_high_steering_proxy.py` | commaSteeringControl車種別zipからproxy windowを抽出するスクリプト |
| `data/low_speed_high_steering_proxy_summary.tsv` | 入力、閾値、走査件数、候補window件数の要約 |
| `data/low_speed_high_steering_proxy_windows.tsv` | 上位12件の代表window |
| `data/low_speed_high_steering_proxy_timeseries.tsv` | 上位5件のwindow時系列 |
| `generated/low_speed_high_steering_proxy.html` | ブラウザで見られる可視化 |

## 使用データ

- Dataset: [commaai/commaSteeringControl](https://huggingface.co/datasets/commaai/commaSteeringControl)
- Vehicle zip: Hugging Face上の `data/CHRYSLER_PACIFICA_2018.zip`
  - 実行時は `/tmp/CHRYSLER_PACIFICA_2018.zip` に取得した。zip本体は大きいためRepoには入れない。
- Dataset description上の主な信号:
  - `vEgo`: 車速
  - `steerFiltered`: 正規化・rate limitedされた操舵トルク入力
  - `latActive`: openpilotの横制御有効状態
  - `steeringPressed`: ドライバーがステアリングを押している状態
  - `steeringAngleDeg`, `latAccelDesired`, `latAccelSteeringAngle`

## 抽出条件

```text
vEgo <= 8.0 m/s
abs(steerFiltered) >= 0.25
latActive == True
steeringPressed == False
duration >= 1.0 s
```

この条件は「低速・操舵要求高めの正常走行文脈」を拾うためのもの。故障検知条件ではない。

## 結果

| Metric | Value |
|---|---:|
| CSV segments scanned | 3,489 |
| Samples scanned | 2,091,708 |
| Low-speed samples | 87,334 |
| Low-speed high-demand samples | 8,412 |
| Candidate windows | 231 |

上位windowでは、`vEgo` が概ね4.3-7.2 m/s、`abs(steerFiltered)` の最大が0.44-1.00程度の低速・高操舵要求文脈が取れている。

## Chain-of-Verification

| 検証質問 | 確認結果 | Confidence | 修正 |
|---|---|---:|---|
| commaSteeringControlは公開・非gatedで取得できるか | Hugging Face API上で `private=false`, `gated=false` を確認。車種別zipが公開されている。 | High | 実データ抽出に進めた |
| このデータにEPS故障ラベルやDTCはあるか | README記載の列は車速、操舵角、操舵トルク入力、横加速度、EPS firmware version等。故障ラベルやDTCはない。 | High | 故障予測とは言わない |
| `steerFiltered`を操舵負荷そのものと呼べるか | READMEでは正規化・rate limitedされた操舵トルク入力と説明される。EPS内部電流や機械負荷ではない。 | High | 「操舵要求proxy」に限定 |
| Pacifica 2018のproxyをNHTSAのPacifica EPS案件と直結できるか | NHTSA側の公開案件はdriver-visible pain文脈であり、このzipは正常走行データ。個別不具合との対応はない。 | High | 「同一車種系の文脈例」以上にしない |
| EPSサプライヤにとって何が嬉しいか | 公開データだけでは商品価値証明はできない。ただし、低速・高操舵要求の再現windowを使って、評価シナリオ/デモ/追加証跡仮説を具体化できる。 | Medium | 次アクションを評価シナリオ化に寄せる |

## 何が言えるか

- 公開データだけでも、低速・高操舵要求の代表windowは抽出できる。
- `generated/low_speed_high_steering_proxy.html` により、抽象論ではなく時系列として議論できる。
- NHTSA pain taxonomyで出てくる `low_speed_high_effort` を、正常走行proxyとして再現する入口にはなる。

## 何は言えないか

- EPS劣化兆候は言えない。
- assist lossの予兆は言えない。
- DTC / freeze frame / extended dataの不足証明は言えない。
- OEM保証DBや返却品解析に対する価値は、このデモだけでは証明できない。

## 次アクション

1. `low_speed_high_steering_proxy_windows.tsv` の上位windowを、公開EPS pain taxonomyの `low_speed_high_effort`, `gradual_turn_sticking_oversteer`, `stop_start_low_speed_context` と対応付ける。
2. 同じスクリプトを2-3車種に適用し、車種差・EPS firmware version差がproxy scoreに出るかを見る。
3. 低速・高操舵要求windowに対して、ECUサプライヤが追加で見たい内部信号を列挙する。
4. その内部信号が既存DTC/freeze frame/extended dataで残るか、残らないならNVM内の最小追加証跡候補に落とす。

ここまで進めて初めて、「ただの公開データ可視化」から「EPSサプライヤが評価・診断仕様を考えるための材料」に近づく。
