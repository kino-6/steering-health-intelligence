# 159. 公開データセット棚卸しの更新(2026-08-22)

## 判断

**前回の棚卸しは、探す軸を1つ落としていた。車両レベル(CAN / OBD / 操舵角)しか見ておらず、部品レベル(モータ駆動系)を見ていなかった。**

その結果、**実故障ラベル付きデータを2件、見落としていた**。うち1件は本Repoの中心仮説を実測で扱える性質を持つ。

| 判定 | 内容 |
|---|---|
| 操舵系/EPS固有の実故障データ | **依然として0件**。この点で [docs/144](144_synthetic_sensitivity_results.md) の「実故障の公開波形は存在しない」は維持 |
| モータ/駆動層の実故障データ | **存在した(新規2件)**。前回の棚卸しの対象外だった |
| Kill記録の扱い | [data/llm_kill_knowledge_base.tsv](../data/llm_kill_knowledge_base.tsv) の「Kaggle as EPS field failure prediction」Kill は**維持**。ただしこれは「EPS市場故障予測にKaggleを使う」仮説のKillであり、**データ在庫の再確認を禁じるものではない** |

更新: [data/public_steering_dataset_inventory.tsv](../data/public_steering_dataset_inventory.tsv)(DS011〜DS014を追加)

## 新規: DS011 — KAIST PMSM 固定子故障データセット(最重要)

- 出典: Data in Brief (2023)、[Mendeley Data 10.17632/rgn5brrgrn.5](https://data.mendeley.com/datasets/rgn5brrgrn/5)
- ライセンス: **CC BY 4.0**(帰属のみ。商用可)
- 内容: 三相PMSM **1.0 / 1.5 / 3.0 kW** の3機。**正常 / 巻線間短絡(inter-turn) / コイル間短絡(inter-coil)**
- **severityが連続値(0.00%、5.70% …)で8段階**
- 計測: 電流 100 kHz、振動 25.6 kHz

**なぜ重要か。**

1. **EPSの操舵アシストモータと同型・同出力帯である。** EPSは三相PMSMで概ね0.5〜1.5 kW。ベンチ機だが機種が対応する
2. **劣化が段階的に振られた実データである。** 本Repoの中心仮説は「故障判定に至らない小さな兆候に情報が乗る」であり、これまでその検証は
   合成注入([docs/144](144_synthetic_sensitivity_results.md))と、**車検の目視観察**([docs/150](150_advisory_precedence_verification.md))でしか行えなかった。
   **実部品・実故障・段階的severity**という組み合わせは初めてである
3. ライセンスが CC BY 4.0 で制約がない

## 新規: DS012 — インバータ駆動PMSM 故障診断データセット

- 出典: Data in Brief (2025)、[Zenodo 10.5281/zenodo.14482932](https://doi.org/10.5281/zenodo.14482932)
- ライセンス: **CC BY-NC(非商用限定)** — **本Repoは事業仮説研究なので、この制約は必ず意識すること**
- 内容: 9条件(F0正常 / F1-F5 スイッチ開放・短絡 / F6-F8 過熱)、8センサ(相電流A/B、DCバス電圧・電流、ハーフブリッジ温度3点、ドライバ電圧)
- 10 Hz、10,892サンプル。15V・6000rpm の小型ベンチ機
- 著者自身が限界を明記: フィルタなし、10 Hzでは高速過渡を捉えられない、Arduinoベースの制約

電源・熱contextはSPD008 payloadの対象と重なるが、**出力帯がEPSと異なり、10 Hzでは電流signatureの解析に足りない**。DS011に劣る。

## 新規: DS013 / DS014(手順と参考)

- **DS013**: [PHM公開劣化データセット総覧(arXiv 2403.13694)](https://arxiv.org/pdf/2403.13694)。**次回の棚卸しはまずここを見る。** 個別検索より体系的
- **DS014**: [SCANIA Component X(arXiv 2401.15199)](https://arxiv.org/pdf/2401.15199)。実車部品の劣化時系列をOEMが公開した先例。商用車・非操舵だが、「OEMが運用データを出す」事例として記録

## この更新が変えること / 変えないこと

**変えない**:

- [docs/143](143_recall_detection_results_v2.md) の故障予測Kill。DS011は個車のRUL予測を可能にしない
- [docs/144](144_synthetic_sensitivity_results.md) の限界1「実故障の波形とは異なる」。DS011は**操舵系としての**実故障ではない——トルクセンサ、操舵角、アシスト制御ループ、車両が無く、本Repoの標的故障族(断続的アシスト喪失)を含まない
- 本Repoの結論([docs/145](145_final_conclusions_and_interpretations.md)、[docs/146](146_business_framework_and_roadmap.md))

**変える**:

- **理想回路モデルの循環問題が、一部だが断てる。** 自作モデルの波形で自作検出器を検証すると循環する([docs/158](158_sotif_eooc_monitor_demo.md))。
  しかしDS011があれば、**モデルが生成する巻線故障のsignatureを、実測の段階的severityデータと突き合わせられる**。
  モデル全体の妥当性は保証されないが、少なくとも1つの故障モードについて「モデルが実測に似ているか」を外部基準で問える
- 「実故障データは公開されていない」という言い方は**不正確になった**。正しくは「**操舵系としての**実故障データは公開されていない。モータ/駆動層にはある」

## 手順の是正

前回の棚卸しが軸を落とした原因は、**検索語が用途(steering / EPS / 車両)に閉じていた**ことである。部品(PMSM / インバータ / 巻線)で引けば出た。

以後の棚卸しは次の2軸で行う。

1. **用途軸**: steering / EPS / chassis / vehicle
2. **部品軸**: PMSM / BLDC / inverter / torque sensor / winding / bearing

加えて、DS013のような**総覧論文を起点にする**。個別検索は取りこぼす。

## Rule Check

- 公開情報のみ。ライセンスを各件で確認し、CC BY-NC(DS012)の商用制約を明記した
- Kill記録([data/llm_kill_knowledge_base.tsv](../data/llm_kill_knowledge_base.tsv))を**仮説のKillとデータ在庫の不在に分離**した。前者は維持、後者は更新した
- 「実故障データがない」という過去の言い方が不正確になったことを明記した
- DS011を過大評価していない。操舵系としての検証にはならないことを、変えないこと側に書いた
