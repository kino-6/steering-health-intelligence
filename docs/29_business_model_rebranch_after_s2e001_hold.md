# Business Model Rebranch After S2E001 Hold

## 結論

S2E001がHoldになっても、ビジネスモデル探索は止まらない。

止めるべきなのは、

> 公開データだけを根拠に、ECUへ追加証跡を入れる商品を売ること。

次に進めるべきなのは、

> 公開市場文脈を使って、EPSサプライヤの評価、設計レビュー、RFQ、顧客品質説明を支援するビジネスモデル。

現時点の推奨は、以下の組み合わせ。

> **EPS Market Pain Scenario Library + Diagnostic Evidence Design Review Workshop**

これは「故障予測」でも「追加ログ商品」でもない。
市場で揉めやすい操舵文脈を、評価シナリオ、設計レビュー論点、顧客説明材料に変換するサービス/パックである。

## なぜ再分岐するか

S2E001で分かったこと:

- low-speed high-steering-demand proxyは作れる
- しかし、それだけではEPS追加証跡商品の価値は証明できない
- 既存DTC / freeze frame / extended dataで十分かどうかは公開データでは分からない
- 内部仕様が確認できない場合、追加証跡商品としてはHold

したがって、次の問いは変えるべき。

| 悪い問い | 良い問い |
|---|---|
| どんな証跡をECUに追加するか | 内部データが無くても売れる価値は何か |
| S2E001をどうProceedさせるか | S2E001のHoldを踏まえて、どのビジネスモデルなら成立するか |
| low-speed high-demandを検出できるか | 市場痛みを評価/設計/品質の意思決定に変換できるか |

## 作ったもの

| File | 内容 |
|---|---|
| `data/business_model_rebranch_after_s2e001_hold.tsv` | S2E001 Hold後のビジネスモデル再分岐表 |
| `generated/business_model_rebranch_after_s2e001_hold.html` | 再分岐の意思決定ビュー |

## 推奨Top 5

### 1. EPS Market Pain Scenario Library

公開NHTSA / recall / ODI / public CANから、EPSで揉めやすいdriver-visible painを評価シナリオ化する。

売り先:

- EPS設計
- 評価/validation
- 品質保証
- 営業技術

売るもの:

- 市場pain scenario card
- 代表proxy window
- 評価条件
- 診断設計レビュー論点
- RFQ/DRBFM/FMEAで使う説明材料

強い理由:

- 内部DTC仕様がなくても始められる
- S2E001を「商品」ではなく「評価シナリオ」として再利用できる
- 公開情報だけでも一定の成果物を作れる

Kill条件:

- 既存FMEA/DRBFM/評価シナリオと差分がない
- 設計/評価/品質の誰も使わない

### 2. RFQ / Design Review Evidence Pack

OEM向けRFQや設計レビューで、

> このEPSは、市場で揉めやすい操舵文脈をどう評価し、どう診断説明するか

を示すパック。

強い理由:

- 追加証跡が未成立でも、提案資料として価値がある
- EPSサプライヤの営業技術/先行開発に近い
- 「health-ready」より「diagnostic explainability / scenario readiness」の方が通りやすい

Kill条件:

- OEM/社内レビューで資料用途がない
- 単なる調査レポートで終わる

### 3. Diagnostic Evidence Design Review Workshop

既存DTC / freeze frame / extended dataが、市場痛み文脈を説明できるかを短期レビューする。

強い理由:

- S2E001のHoldをそのまま商品導線にできる
- 内部仕様がある顧客なら、2-4 week workshopとして成立し得る
- Proceed / Kill / Holdを出すこと自体が成果物になる

Kill条件:

- 顧客がDTC仕様を持ち込めない
- 設計レビューより実装機能を求めている

### 4. Public NTF / Warranty Risk Intelligence

公開不具合・リコール・調査文書から、NTF化しやすい症状/文脈を分類する。

強い理由:

- 内部案件が無くても、外部市場の痛みからレビュー論点を作れる
- warranty / supplier quality / customer qualityに接続しやすい

弱い理由:

- 公開情報だけでは対象EPSの保証費削減は証明できない
- 有料化するには、定期更新や顧客固有レビューが必要

### 5. Evaluation Scenario Generator

公開走行データから、低速高操舵、緩旋回、停止発進、路面外乱などの評価windowを抽出し、HILS/bench入力に近づける。

強い理由:

- すでにPhase 2で低速高操舵windowを抽出できている
- 評価/validation部門に接続しやすい

弱い理由:

- 既存評価シナリオ資産との差分が必要
- EPS fault reproductionとは言えない

## 再分類

### 今すぐ探索できる

| ID | Model | 理由 |
|---|---|---|
| BMR001 | EPS Market Pain Scenario Library | 公開データだけで初期成果物が作れる |
| BMR002 | RFQ / Design Review Evidence Pack | 内部仕様なしでも説明資料として作れる |
| BMR003 | Diagnostic Evidence Design Review Workshop | 内部仕様がある顧客には有料レビュー化できる |
| BMR004 | Public NTF / Warranty Risk Intelligence | 市場痛みの継続調査として成立し得る |
| BMR005 | Evaluation Scenario Generator | 既にproxy抽出スクリプトがある |

### 内部データがあれば探索できる

| ID | Model | 理由 |
|---|---|---|
| BMR006 | EPS Diagnostic Evidence Gap Assessment | DTC仕様があればProceed/Kill判定可能 |
| BMR007 | Customer Quality Fact Summary Generator | 実際のDTC/NVM/解析結果が必要 |
| BMR008 | Return-part Evidence Reader Readiness Review | reader/DID/ODX情報が必要 |
| BMR009 | NVM Evidence Budget Review | NVM制約が必要 |

### 今は追わない

| ID | Model | 理由 |
|---|---|---|
| BMR010 | OEM Warranty Correlation Analytics | OEM保証DB依存が強い |
| BMR011 | Remote EPS Health Payload Integration | OEM connected platform依存が強い |
| BMR012 | ECU Embedded Low-Speed High-Steering Event Add-on | S2E001がHold。内部仕様不足確認まで売らない |

## Chain-of-Verification

| 検証質問 | 確認結果 | Confidence | 修正 |
|---|---|---:|---|
| S2E001 Holdでプロジェクト全体が止まるか | 止まらない。止まるのは追加証跡商品としてのS2E001。 | High | ビジネスモデルを再分岐 |
| 内部データなしで売れるものはあるか | 公開市場文脈を使うscenario library、RFQ pack、評価シナリオ生成は作れる。 | Medium | 「診断不足の断定」は避ける |
| 既存Best5をそのまま進めてよいか | Health indicator / evidence add-on寄りの案はS2E001 Holdで弱くなる。 | High | Top案をscenario / review / RFQ支援に入れ替え |
| OEM依存案を初期に追うべきか | 保証DB、サービスツール、connected platform依存が強い。 | High | Optional extensionへ下げる |
| 次のデモは何か | 追加証跡デモではなく、scenario card / RFQ page / workshop agendaが良い。 | Medium | 次成果物を営業・設計レビュー寄りに変更 |

## 次に実施すること

次は `BMR001 EPS Market Pain Scenario Library` を3枚だけ作る。

対象:

1. low_speed_high_effort
2. gradual_turn_sticking_oversteer
3. warning_plus_low_speed_effort

各scenario cardに入れるもの:

- market pain
- public source
- representative public proxy window
- evaluation scenario
- design review question
- diagnostic evidence question
- RFQ/design review wording
- what not to claim

これなら、内部DTC仕様が無くても前に進める。
