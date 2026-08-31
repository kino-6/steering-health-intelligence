# 自動チェック — 同じ失敗を繰り返さないための仕組み

**このファイルにあるものは全て、実際に起きた失敗への対策である。**
人間の記憶や、ルール文書を読み直す習慣に依存しない。**コミット時に自動で走る。**

```sh
sh scripts/install_hooks.sh      # 一度だけ。git hookは複製されないため
python3 scripts/check_repo.py    # 手動実行
python3 scripts/check_repo.py --list
```

## 1. コミット前チェック — `scripts/check_repo.py`

`.git/hooks/pre-commit` から自動実行される。**ブロッキング9件、警告1件。**

| チェック | 何を止めるか | 元になった失敗 |
|---|---|---|
| **links** | 壊れた内部リンク | 毎回コミット前に手で確認していた。抜ければ気づかない |
| **dataset coverage** | データセットに未棚卸しの部分が残ったままの解析 | **NASA MOSFETの3つの塊のうち1つだけを見て34本書いた**([docs/199](docs/199_pulse_thermal_results.md))。KAISTは32ファイル中8、3機体中1([docs/201](docs/201_motor_second_fault_and_vibration_results.md), [docs/203](docs/203_cross_machine_replication_results.md)) |
| **derived files** | 生成スクリプトかSOURCES記載を欠く出力表 | 出典表と実体の対応が手作業だった |
| **wording** | [AGENTS.md](AGENTS.md) ルール0 の禁止語 | 個人研究なのに「自社」「見せて反応を得る」を4回書いた。**手作業の一括置換を3回やっても4件残っていた**(2026-08-27に本チェックが検出) |
| **pre-registration order** | 事前登録が結果より後にコミットされること | 事前登録の価値は順序そのもの。gitの履歴だけが後から書き換えられない記録である |
| **correction backlinks** | 訂正された側に前方ポインタが無いこと | 古い文書に着地した読者が、それが覆されたことに気づけない |
| **sheet currency** | EooCシートの行が、訂正された文書だけを出典にしていること | **5行が古いまま「埋まる」と書いてあった**([docs/249](docs/249_eooc_sheet_audit.md))。成果物が根拠より強い主張をしていた |
| **troubles registered** | 訂正・撤回・不成立を宣言した文書が [TROUBLES.md](TROUBLES.md) に載っていないこと | **2026-09-01 ユーザ指摘「正直人間側が指摘できない」。**この検査を入れたら、**登録簿から漏れていた文書が20件**出た。うち6件は同じ型(「無い」と早く言い切る)だった |
| *(警告)* threshold compares | 浮動小数点での閾値判定 | [docs/205](docs/205_sign_free_deviation_results.md): 4点のSpearmanは厳密に4/5だが `0.7999...` で返り、`>= 0.8` が弾いて判定が反転した |

> **警告(threshold compares)の既存スクリプト分は確認済みで、記録済みの判定に影響しない。**
> 該当箇所のρは 1.000 / 0.393 / 0.381 などで、境界0.8から十分離れている。
> **新規のスクリプトでは `lib_discipline.passes()` を使うこと。**

## 2. 取得前の見どころ評価 — [data/dataset_prospect.tsv](data/dataset_prospect.tsv)

**公開データを取得する前に、答えられるかどうかを評価して記録する。**

`check_repo.py` は、ディスク上の全データセットに `decision = acquire` の行があることを要求し、
**行のどの欄が空でも落ちる。**

| 欄 | 何を書くか |
|---|---|
| `question` | このデータで何に答えるのか |
| **`operating_point`** | **試験機が動作点を保持するかランプするか。配布論文・Readmeで確認する** |
| `has_control` | 対照(健全群・分母)があるか |
| `decision` | `acquire` / `decline` |
| `reason` | 判断の根拠。`decline` なら取得しない理由 |

**`operating_point` が最も重要である。**加速試験の多くは劣化を速めるために動作点を意図的に動かし、
**その操作が観測量の最大の変動要因になる。**

**そして「保持」だけでは足りない**([docs/237](docs/237_within_condition_results.md))。
**加速試験では「動作点を保持する」と「現実的な時間で劣化させる」が両立しない。**
NASA IGBTでランプを除いたところ、保持区間は**9〜44分**しかなく、観測量は測定分解能の1刻みも動かなかった。

> **問うべきは「動作点を保持したまま、劣化が進む時間だけ運転された区間があるか」である。**

**ただし、この評価が効くのは配布ページが十分に書いている場合に限る**([docs/237](docs/237_within_condition_results.md))。
NASA IGBTは一覧に1行しかなく、**ランプも保持時間も取得しないと分からなかった。**
**`operating_point` に「不明」と書いて取得するのは正しい使い方である。**空欄にしないことが要件であって、
**必ず判明することを要件にしてはならない。**

**この欄を先に確認していれば、3件の失敗は防げた。**

| データセット | 実際 | いつ気づいたか |
|---|---|---|
| NASA MOSFET | 設定温度を run毎に10°C低下 | **取得の34文書後**([docs/199](docs/199_pulse_thermal_results.md)) |
| インバータPMSM | 正常クラスだけ非定常 | 取得直後([docs/215](docs/215_inverter_dataset_acquisition.md)) |
| NASA IGBT | **供給2.4倍・温度180°C上昇のランプ。論文に記載あり** | 解析後([docs/234](docs/234_igbt_switching_results.md)) |

ディスクは一時 **62 GB** に達した。**展開済みファイルは消す**——スクリプトは必要時にzipから展開する。
現在 **37 GB**。

## 3. データセット棚卸し — `scripts/dataset_coverage.py`

**取得したデータの中身を、ファイル単位ではなくフィールド単位まで列挙する。**

```sh
python3 scripts/dataset_coverage.py
```

- 各データセットを走査し、アーカイブのメンバー、および代表ファイルの**内部構造**(`.mat`のstructフィールド、`.tdms`のグループ/チャネル/プロパティ、CSVの列)を列挙する
- 結果を [data/dataset_coverage.tsv](data/dataset_coverage.tsv) に書き、**既存の判断は保持する**
- 新規項目は `UNREVIEWED` で入り、**残っている限り `check_repo.py` が落ちる**
- 状態は `used` / `unused:<理由>` のいずれか。**理由の無い `unused` も落ちる**

**ツールは `used` しか自動判定しない。**「不要である」という判断は人が明示する。
それを黙って自動化することが、34本の文書が3分の1のデータの上に建った理由そのものだからである。

**実際の効果**: 導入した日に、一度も見ていなかったセンサ設定プロパティを検出した。
確認した結果、感度・レンジ・端子構成は3機体・全セッションで同一であり、
**測定キャンペーン間の段差はゲイン変更ではない**ことが分かった(1.0 kWの2022-03-08のみ電流chに約0.17 AのDCオフセット)。

## 4. 解析時のガード — `scripts/lib_discipline.py`

**同じ計算ミスを二度としないための関数。**新しい解析スクリプトはこれを import する。

| 関数 | 何を防ぐか | 元になった失敗 |
|---|---|---|
| `spearman_exact(x, y)` | 小標本の順位相関を有理数で返す | 4点のSpearmanは 1, 4/5, 3/5, 2/5 しか取らない。floatで比較すると境界を落とす |
| `passes(v, thr, dir)` | 事前登録した閾値との比較 | [docs/205](docs/205_sign_free_deviation_results.md) で判定が反転した |
| `session_key_tdms(path)` | 測定キャンペーンの識別 | セッション段差を**3回**見落とした([docs/162](docs/162_pmsm_model_validation_results.md), [201](docs/201_motor_second_fault_and_vibration_results.md), [203](docs/203_cross_machine_replication_results.md))。日付はメタデータに最初から入っていた |
| `require_same_session(...)` | 基準と評価が別セッションになること | 個体基準だけでは足りない。**同一測定条件**でなければならない |
| `switching_or_linear(v, vsup)` | 観測量の取り違え | [docs/199](docs/199_pulse_thermal_results.md): 能動領域の素子を「オン抵抗」と呼び、導通損の物理でモデルを建てた |

## 5. 報告の型 — `.claude/skills/report/SKILL.md`

`/report` で呼び出す。**結論を先に、作業ではなく変化を、不成立は「誰の何が外れたか」で書く。**
3回「意味がわからない」と指摘された後に作った。自己チェックリスト付き。

## チェックを飛ばす場合

```sh
git commit --no-verify    # 理由をコミットメッセージに書くこと
```

行単位の例外は、その行に `check-repo: allow` と**理由**を書く。
