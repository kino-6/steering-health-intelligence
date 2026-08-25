# 188. 筋道 — 何が言えて、何を売るのか

**Goal 4 の到達点。[docs/185](185_misdiagnosis_quantified.md)〜[187](187_replacement_no_fix_result.md) の検証を経て、主張を1本に通す。**

## 一行

> **断続的で再現しない操舵の故障では、判断の材料そのものが存在しない。
> その瞬間の記録を持てるのは部品の中だけである。**

## 筋道(各段に検証を付ける)

### ① 断続的な操舵故障は、実在する故障族である

- 米国リコール2件(Ford 15V-340、GM 17V-414)、英国の公知問題(Vauxhall Corsa D)——**3つの独立市場**で同じ族が観測された([docs/151](151_high_rate_model_crosscheck.md))
- 公開文書の記述: 「アシストが失われ、再始動で戻り、**再発する**」(MKT011〜016、[docs/176](176_correction_degradation_window.md))
- EPSリコール168件で `intermittent` が最頻語(4.8%)、電気的症状は全車両の**2.81倍**([docs/171](171_eps_wearout_mechanism_scan.md))

### ② その族では、再現しない

- **断続性を記述したEPS苦情は、原因不明・再現せずと書かれる率が 5.74%。全苦情基準1.15%の 5.0倍**([docs/185](185_misdiagnosis_quantified.md))
- EPS内で断続あり/なし = **4.50倍**。操舵全般の断続層(3.48%)よりさらに1.65倍
- **これがEPSに固有の唯一の痛みである。** 誤診全般(1.01倍)、再来店(0.95倍)、交換して直らない(0.92倍)は**いずれも固有でない**([docs/187](187_replacement_no_fix_result.md))

### ③ 既存の修理手順は、判断の材料を読んでいない

- Ford 15S18 と GM 17276 のディーラー向け一次文書を精読した結果、**5項目中4項目が手順に存在しない**([docs/129](129_steering_predictive_diagnostics_public_case_crosscheck.md))
  - DTC未満eventが残るか → **No**
  - snapshotが読まれたか → **No**
  - assist状態と電源contextの同時性 → **No**
  - 再発(key cycle recurrence) → **No**
  - 判断に使われたのは**DTCの有無1bitのみ**
- 結果として何が起きたか: **GM TSB 17-NA-158** が、無効なCAN信号(冷却水温)で操舵警告が出て
  **直らないのにsteering gearが交換され続けた**ことを**OEM自身が公式に記録**している([docs/130](130_steering_predictive_diagnostics_comm_validity_public_crosscheck.md))
- GM 17276 では**既払い修理の払い戻し**が発生している

### ④ その材料は、部品の中にしか無い

- 苦情126万件を総ざらいしても、EPSの前兆はほとんど見えない([docs/143](143_recall_detection_results_v2.md): precision 0.48 / recall 0.26、事前登録基準に不成立)
- 見逃した族は「苦情が中央値1件」で終わっていた([docs/156](156_train_era_miss_structure.md))——**情報の不在であって調整不足ではない**
- 車検2,800万件でも、操舵不合格の99%はリンケージで、EPS系は**0.1%**([docs/157](157_mode_split_and_corsa_correction.md))
- リコール記録は摩耗故障を構造的に見られない([docs/171](171_eps_wearout_mechanism_scan.md))
- 制御器が内部の変化を打ち消す。巻線の1/5が短絡しても外から見える不平衡は健全比4倍止まり([docs/162](162_pmsm_model_validation_results.md))

**4つの独立した公開観測手段すべてが、この族を構造的に見られない。**

### ⑤ 部品の中でなら、記録できる

- 実部品・実故障・同一個体の連続追跡で、**故障の1〜2段階前に、同一個体のノイズの20〜300倍の逸脱**を検出([docs/167](167_precursor_results_v2.md)、6/6デバイス)
- 成立の条件は**個体ごとの基準 + 動作点正規化**([docs/163](163_per_unit_baselining.md))。温度を個体ごとに除けば健全期の基準は**0.09〜0.75%**で安定する
- 走行logからの応答特性側も、**60秒で遅れ0.3s / ゲイン0.10 / バイアス0.10を90%検出**(誤検出3.6%)。設計則は4車種で一致([docs/155](155_window_recurrence_verification.md))

### ⑥ 個体基準を書けるのは、出荷前に触れる者だけ

- 個体ごとの基準は**出荷前にしか書けない**。OEMのvehicle health基盤は出荷済み車両からしか観測できない([docs/163](163_per_unit_baselining.md))
- EOL検査は既にある工程であり、追加ラインも新規センサも要らない
- **ただしこの論拠は対OEM基盤に効くだけで、他のEPSサプライヤには効かない**([docs/177](177_sotif_direction_update.md))

### ⑦ 出力の宛先は、既に標準化されている

- AUTOSAR VMC が **`STR capability information`** を定義済み。fault診断とは別枠で「今どこまでできるか」を報告する枠がある([docs/183](183_autosar_capability_channel.md))
- **ただし capability を劣化からどう導くかは規格に無い**(仕様に degradation / wear / thermal が0件)。**そこが差別化の余地**

## 売るもの(1文)

> **「再現しない故障のとき、その瞬間に部品の中で何が起きていたかを、宣言した粒度で出せる」ことを、
> EPS製品仕様として組み込み、RFQ差別化と診断コンテンツNREとして売る。**

- ×「壊れる前に教えます」 — 市場最多の接点系には先行時間が無い([docs/175](175_close_contact_question.md))
- ×「保証費をN%減らします」 — データが支持しない([docs/187](187_replacement_no_fix_result.md))、金額も非公開([docs/145](145_final_conclusions_and_interpretations.md))
- ○「**判断材料が無い状態を、材料がある状態にします**」

## SOTIFの位置

**同じ記録の第2の用途であり、需要の柱ではない**([docs/186](186_how_it_becomes_money.md))。

- 乗る形式は **SOTIF-EooC** ただ一つ。仮定シート26項目、空欄ゼロ([docs/180](180_eooc_sheet_all_filled.md))
- 対象は**ADS搭載車のみ**。西側ではL3が後退中([docs/184](184_ads_deployment_reality.md))
- 維持する理由は2つだけ: **宣言の様式をくれる**、**ADS再拡大時の枠**

## まだ言えないこと

| # | 内容 |
|---|---|
| 1 | **兆候→故障の橋は、EPSでは未証明。** 実証は代替部品(NASA MOSFET)であり、EPSそのものの故障前後データは公開されていない |
| 2 | 熱余裕13〜50%喪失は**計算であって測定ではない**([docs/170](170_thermal_headroom_translation.md)) |
| 3 | 接点系(市場最多)の先行時間は**測れない**。公開劣化データ110件の総覧に電気接点が0件([docs/175](175_close_contact_question.md)) |
| 4 | 誤診の**発生率**は不明。測ったのは**言及率**([docs/185](185_misdiagnosis_quantified.md)) |
| 5 | 金額はすべて不明。保証費の内訳は公開されていない |

## Rule Check

- 各段に検証への参照を付けた。**根拠の無い段が無い**
- **支持されなかった主張(誤交換の量、早期警告)を、売るものから外した**
- SOTIFを需要の柱にしていない
- 「まだ言えないこと」を5件、最後にまとめて置いた
