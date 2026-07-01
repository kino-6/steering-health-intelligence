# 17. Customer Value Reality Check

## Why this note is needed

ここまでの議論で、`EPS Health Intelligence`、`Development Evidence`、`Embedded Evidence` といった方向を検討した。

しかし、現時点で最も重要な懸念は以下である。

> 誰向けで、誰が明確に嬉しいのかがまだ弱い。

技術的に成立しそうな指標があることと、買い手が予算を付けることは別である。

## Current concern

### 1. Development evaluation may overlap with external monitors

開発時の評価だけを対象にするなら、外付け計測器やベンチ計測でよい可能性が高い。

外付けモニタの方が強い点:

- 高精度
- 波形が豊富
- 条件を制御しやすい
- 要因分離しやすい
- 開発評価部門に既存の運用がある

ECU内指標が勝てる可能性があるのは、以下の場合だけである。

> 開発時に外付け計測で見つけた評価観点を、量産ECUにも残せる軽量な診断・証跡指標へ落とし込む。

つまり、単なる開発モニタでは弱い。
`Development-to-Production Evidence Transfer` として成立するかを見る必要がある。

### 2. Degradation signal is hard to explain

ECUから見えるのは、基本的に入出力、制御量、診断状態である。

ギア摩擦、ラック抵抗、タイヤ、路面、アライメント、温度、電源、運転癖が混ざるため、ECU信号だけで劣化要因を説明するのは難しい。

したがって、以下の表現は危ない。

- ギア劣化を検出する
- ラック摩耗を予測する
- EPS故障可能性を通知する
- 個車RULを出す

より安全な表現:

- 制御努力の変化を見る
- 高負荷操作履歴を見る
- thermal / voltage / current tracking stressを残す
- 診断・品質説明に使える軽量証跡を残す

### 3. NVM evidence is necessarily poor

量産ECUのNVMに残せる情報は少ない。

残せる可能性があるもの:

- high load event count
- assist limitation count
- thermal derating count
- low voltage event count
- current tracking warning count
- latest event snapshot

残しにくいもの:

- 長時間波形
- 詳細な操舵プロファイル
- 正規化に必要な外部条件
- タイヤ / 路面 / アライメント情報
- 故障要因の直接証明

したがって、NVMに過度な期待を置くと提案が弱くなる。

## Who might actually care?

現時点で一番可能性がある相手は、以下である。

> EPSサプライヤの品質解析 / 市場不具合対応 / OEM説明チーム

理由:

- 量産品に残っている情報しか使えない
- 返却品や市場不具合では再現できない
- OEMから「なぜ起きたのか」を聞かれる
- DTCだけでは説明できない
- ECUとして何が見えていたかを説明したい

ただし、この場合も大きな新規事業というより、以下に近い。

> 品質説明力を上げる診断仕様改善。

## Candidate positioning after reality check

`EPS Health Intelligence` はやや大きく言いすぎかもしれない。

より現実的な表現:

- EPS Embedded Evidence Package
- EPS Field Evidence Package
- EPS Diagnostic Evidence Improvement
- EPS Development-to-Production Evidence Transfer

現時点で最も正確な表現:

> 開発時の外付け計測で得た知見を、量産ECUに内蔵できる軽量な診断・ストレス証跡へ変換する。

## Business-model implication

この方向は、以下のような大きな市場にはまだ見えにくい。

- standalone SaaS
- fleet predictive maintenance
- end-user notification
- OTA health business
- warranty automation

より近い予算:

- 診断仕様改善NRE
- 品質解析支援
- 返却品解析支援
- OEM説明資料改善
- 開発評価から量産診断への落とし込み支援

## New market research question

次に調べるべき問いは、技術ではなく買い手の痛みである。

> EPSサプライヤ、ECUサプライヤ、OEM品質部門は、何に対して実際に予算を払っているのか？

特に見るべき領域:

- automotive warranty analytics
- No Trouble Found reduction
- supplier quality / warranty chargeback
- diagnostic engineering tools
- return part analysis
- end-of-line / development test analytics
- embedded diagnostics / remote diagnostics vendors
- component reliability / power electronics health monitoring

