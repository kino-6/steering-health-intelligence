# 出荷前品質スクリーニング proxy demo

## 結論

Bosch Production Line Performance型の考え方を、EPSサプライヤの出荷前品質に読み替えた小型デモを作った。

これはKaggle実データではない。
Kaggleから得られた「部品ID、ライン、ステーション、測定値、時刻、希少なfailラベル」という構造を、EPS製造・EOL検査に近い形で再現したsynthetic proxyである。

今回の目的は、モデル精度を競うことではない。
見るべきことは、次の3点である。

1. 後工程でfail/retest/holdになりそうな個体を上位リストに集められるか
2. 上位リストが、再検査、保留、工程確認という現場アクションに翻訳できるか
3. どの工程グループや測定グループを疑うべきか説明できるか

結果として、proxyでは上位5%の個体を見ることで、全fail/retest候補の17.5%を拾った。
全体fail率0.9%に対して、上位5%のfail/retest率は3.5倍である。
完璧な検出ではないが、「全件を同じ目で見る」より、先に見るべき個体を作るデモにはなっている。

## 何を作ったか

追加した生成物:

- `generated/pre_shipment_quality_screening_proxy.html`
- `data/pre_shipment_quality_proxy_summary.tsv`
- `data/pre_shipment_quality_proxy_top_units.tsv`
- `data/pre_shipment_quality_proxy_station_signals.tsv`
- `scripts/generate_pre_shipment_quality_proxy_demo.py`

HTMLはブラウザで見られる。
TSVは、上位リスク個体、捕捉率、工程グループ説明を後で比較できるように残した。

## デモの前提

このデモは、以下を模擬している。

| Bosch型の要素 | EPS製造・EOL検査への読み替え |
|---|---|
| Unit ID | EPS個体ID |
| Line | 生産ライン |
| Station | calibration、functional、acoustic、electrical、EOLなど |
| Numeric measurement | torque bias、current margin、noise、CAN response、EOL reserve |
| Date / order | 時刻、lot、連続生産順 |
| Response | fail / retest / holdに相当するラベル |

意図的にfail/retest候補を少なくした。
量産品質では不良は少数派であり、単純な正解率では価値を見誤るためである。

## 結果

| risk bucket | units reviewed | fail/retest caught | capture rate | precision | lift vs random |
|---|---:|---:|---:|---:|---:|
| top 1% | 60 | 2 | 3.5% | 3.3% | 3.5x |
| top 5% | 300 | 10 | 17.5% | 3.3% | 3.5x |
| top 10% | 600 | 14 | 24.6% | 2.3% | 2.5x |
| top 20% | 1200 | 19 | 33.3% | 1.6% | 1.7x |
| overall | 6000 | 57 | 100% | 0.9% | 1.0x |

読み方:

- 上位5%だけを先に見ると、fail/retest候補の17.5%を拾える
- 上位5%のfail/retest率は全体平均の3.5倍
- ただし上位リストにもpass個体は多い
- したがって、出力は「不良断定」ではなく「再検査・保留・工程確認の優先順位」である

## 工程グループ説明

proxyで強く出た信号は以下。

| signal group | lift vs overall | 現場での読み方 |
|---|---:|---|
| line L2 drift window | 3.2x | L2の時刻、lot、設備ドリフトを工程確認 |
| EOL reserve low | 2.8x | EOL reserve低下個体を保留/再検査候補へ |
| functional current margin low | 2.6x | 機能検査の電流余裕低下を再検査条件へ |

ここで重要なのは、root causeを断定していないこと。
「L2が悪い」「EOL reserveが原因」とは言わない。
現場に渡すなら、工程確認、再検査、保留判定の候補として扱う。

## EPSサプライヤとしての価値

このデモが示せた価値は、次である。

> 工程・検査・EOLデータをつなぐと、希少なfail/retest候補を全件同じ目で見るより先に拾える可能性がある。

これは出荷後の予知保全ではない。
出荷前の品質予兆検知である。

使う部署:

- 製造品質
- 工場品質保証
- EOL検査
- 工程設計

業務で変わる可能性があること:

- 再検査すべき個体の優先順位
- 保留すべき個体の説明
- 工程確認すべきライン、ステーション、時刻帯
- 管理項目候補の洗い出し

## まだ言ってはいけないこと

このデモから、次は言えない。

- EPSの出荷後故障予測ができる
- EOL検査を省略できる
- 保証費を下げられる
- root causeを断定できる
- 既存SPC / MES / BIより優れている
- 実EPS工程で同じ捕捉率が出る

## CoVe

| 検証質問 | 回答 | Confidence | 反映 |
|---|---|---|---|
| Kaggle実データを使ったか | いいえ。Kaggle課題構造を再現したsynthetic proxyである | High | HTMLと本文に明記 |
| 出荷後故障予測に戻っていないか | 戻っていない。fail/retest/hold候補の出荷前スクリーニングに限定 | High | 禁止主張に明記 |
| 数字は過大主張ではないか | proxy上の数字であり、実EPS性能ではない | High | 実EPSで同じ捕捉率が出るとは言わない |
| 現場アクションに翻訳できるか | 再検査、保留、工程確認の候補までは翻訳できた | Medium | 次の実証条件に置く |
| 既存工程管理との差分は出たか | 個体単位の上位リストと工程グループ説明は出た。ただし既存SPC/MES/BIで同等ならKill | Medium | Kill条件に残す |

## 次アクション

次に進めるなら、2つある。

1. Bosch実データまたは公開Kaggle APIを使える環境で同じ形式を再実行する
2. EPS実データを使わない方針のままなら、デモを営業資料ではなく「内部検討用の型」として扱い、必要データ項目だけを定義する

現行方針では、次は2が自然である。

必要データ項目:

- 個体ID
- 工程名
- 測定名
- 測定値
- 設備/治具
- lot
- 時刻
- software/calibration
- EOL pass/fail
- retest/hold/scrap/再調整ラベル

Kill条件:

> これらのデータが取れない、または取れても再検査・保留・工程確認に使えないなら、この方向は止める。
