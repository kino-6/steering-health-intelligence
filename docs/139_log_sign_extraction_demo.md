# Log Sign Extraction Demo (技術者向け)

## 結論

上位ルール(Personal Public-Only Research Rule)のDemo方針——**公開logから、人間には読み取れない兆候を機械的に読み取り、SOTIFへ部品側として参加できる形を見せる**——を実装した。

- 入力: 公開走行logデータ [commaSteeringControl](https://huggingface.co/datasets/commaai/commaSteeringControl)(comma.ai、MIT license)。Ford Maverick platform、60秒×999セグメント(10Hz)
- 兆候抽出: 残差 `r(t) = 実測横加速度(localizer) − 操舵角由来横加速度(車両モデル)` をセグメント毎に6特徴(応答バイアス / ドリフト / 左右非対称 / 応答遅れ / ゲイン偏差 / 高周波不整合)へ圧縮し、母集団のrobust z-scoreで正規化。**学習モデルなし・決定的・全再現可能**
- 結果: 有効938セグメント中、|z|≥4で146件、≥6で77件、≥8で39件の統計的兆候を検出(最大 z=57 の高周波不整合など)。**raw波形の目視では判別できない**——これが「人間ではわからない兆候」の実体
- 出力: 検出セグメントごとに、SPD payload形式の状態説明(境界明記)+ **SOTIF語彙への機械変換**(`sotif_mapping`: triggering condition候補、EooC仮定発生率の検証インプット)

実行: `python3 scripts/steering_log_sign_extraction.py` / 閲覧: [generated/steering_log_sign_extraction.html](../generated/steering_log_sign_extraction.html) / 数表: [data/steering_log_sign_extraction.tsv](../data/steering_log_sign_extraction.tsv)

## ビジネスモデル内の役割(docs/138)

第1層(状態説明機能つきEPS製品仕様)の**技術的信用**を、内部情報ゼロで示す道具。
「EPS内部信号で同じパイプラインを回せば、docs/122のpayloadがruntimeで出る」という主張の、公開データによるend-to-end実演である。宛先は技術者であり、根拠(式・閾値感度・限界)を本文に埋めた。

## これが「デモ」である理由(docs/132がレポートだった反省)

docs/132は事後整形した静的文書だった。本デモは、**入力データ(公開log)から出力(payload+SOTIF語彙)までがスクリプト1本で機械的に流れる**。誰でも別platformのzipを置き換えて再実行でき、閾値を変えれば検出が変わる。見せているのは結論ではなく仕組みである。
(さらに対話的な形——閾値スライダーで検出が動く等——が必要なら、生成済みの特徴量TSVをJSに載せるだけで拡張できる)

## 何を言っていて、何を言っていないか

言っている:

> 部品側のパイプラインは、runtime logから母集団参照の統計兆候を機械抽出し、原因断定なしの状態説明とSOTIF運用フェーズ監視の言葉に変換できる。

言っていない(HTMLの限界節とpayloadのboundaryに機械的に明記):

> 検出された兆候が故障の前兆である(健全fleetの公開logであり、路面・運転者・積載・センサが交絡)。個車の判定・RUL・原因断定。閾値4が運用値である(閾値感度を併記)。

## Rule Check

1. `Personal Public-Only Research Rule`: 公開データのみ(MIT license)。内部情報への言及なし。宛先は技術者。Demo方針に合致
2. `Market Demand First`: 需要はdocs/126/128で確認済みのSOTIF運用フェーズ監視・EooC仮定検証に接続
3. `Natural Language First`: 兆候の意味を平文で先に説明(応答バイアス等の日本語名)
4. `Steering Predictive Diagnostics Value Rule`: E2E外乱の交絡を明記し、内部重要モジュール単位の観測(EPS内部実装)が本命であることを限界1に明記
5. 禁止主張: payloadのboundaryフィールドで機械的に遮断

## 限界と次の拡張候補

1. 車両個体が区別できないため再発追跡ができない(データ側の制約)
2. 車両モデル誤差・roll簡略化(方法の制約)
3. 拡張候補: 別platformへの横展開(120車種のzipを差し替えるだけ)、EPSファームウェア版数(データに含まれる)でのグループ比較、閾値スライダー付き対話版
