# Cyber / SBOM Kill後の次探索方針

## 結論

`Steering ECU Software / Cyber Evidence Pack` は、広い商品としてはKillする。
残す場合も、steering ECU固有のOEM問い合わせ回答に既存成果物を翻訳する短期支援だけであり、次の主探索にはしない。

次に掘る方向は以下の3つに切り替える。

1. **Steer-by-wire向けの安全・冗長・サイバー設計証拠**
2. **SOVD / 次世代診断コンテンツ設計**
3. **公開recall / ODI / TSB市場要求モニタ**

ただし、3つを同じ強さで進めない。

最優先は1である。
2は1や既存診断から派生するextensionとして扱う。
3は単体商品ではなく、1と2の市場入力として使う。

## なぜ切り替えるか

Cyber / SBOM方向では、市場需要は確認できた。
しかし、TARA、SBOM、CVE管理、ISO/SAE 21434、UN R155/R156対応は既存プレイヤーが厚く、広い商品としては差別化が弱い。

したがって、次は以下の条件を満たす方向に寄せる。

- EPS / steeringサプライヤの主語に戻せる
- 汎用ツールや汎用規格支援の言い換えになりにくい
- 公開情報で市場変化を説明できる
- ただし、内部資料なしで過剰主張しない

この条件に最も近いのが、steer-by-wireである。

## 次候補1: Steer-by-wire向けの安全・冗長・サイバー設計証拠

### 市場需要

steer-by-wireは、機械的な操舵連結をなくし、電子制御で操舵を成立させる方向である。
公開情報では、ZF、Nexteer、HELLAなどが量産・受注・センサ技術を発表している。

従来EPSでは、assistが落ちても機械的操舵が残る前提があった。
steer-by-wireでは、冗長センサ、冗長電源、冗長通信、actuator、feedback、fault handling、fail-operational、cyber abnormal conditionの説明責任が重くなる。

### 未解決の痛み

ISO 26262や既存safety caseはある。
しかし、steer-by-wireでは以下を横断して説明する必要がある。

- 冗長系がどの故障をどこまで吸収するか
- single point faultやlatent faultをどのように扱うか
- cyber異常やsoftware update後に操舵可用性をどう説明するか
- driver feedbackやfallback stateをどう説明するか
- supplier component boundaryで何を説明し、OEM vehicle boundaryへ何を渡すか

### 仮説

EPS / steeringサプライヤ向けに、steer-by-wire移行時の安全・冗長・サイバー説明を、OEM設計レビューやRFQ回答に使える部品境界の証拠mapへ落とす支援は探索価値がある。

### 初期検証

まず公開情報だけで以下を作る。

- 従来EPSとsteer-by-wireの説明責任差分
- steer-by-wire component boundary map
- redundancy / fault handling / cyber-safety evidence checklist
- 既存ISO 26262 / SOTIF / cyber / safety caseとの重複Kill表

### Kill条件

- 既存ISO 26262 / SOTIF / cyber / safety caseで同じことを既にやっている
- 対象顧客にsteer-by-wire開発テーマがない
- 公開情報だけでは一般論で止まり、steeringサプライヤ固有の問いに落ちない
- OEM vehicle-level設計に依存しすぎ、component supplierの手札が残らない

## 次候補2: SOVD / 次世代診断コンテンツ設計

### 市場需要

Software-defined vehicleでは、診断がECU単体のDTC読出しから、API化されたサービス診断へ移りつつある。
ASAM SOVDは、HPCだけでなくclassic ECU診断コンテンツへのアクセスも含む。

### 未解決の痛み

EPSサプライヤは、UDS、DTC、DID、freeze frame、extended data、security access、software/calibration IDを持つ。
しかし、次世代診断基盤に対して、どの情報をどの粒度で見せるか、何を制限するか、どう権限管理するかはOEM基盤依存が強い。

### 仮説

SOVD基盤そのものを売るのではなく、EPS診断コンテンツをSOVD時代に載せるためのcontent mapやexposure policyを作るなら、狭い価値がある可能性がある。

### 初期検証

- UDS/DTC/DID/freeze frameをSOVD風resourceへ変換する公開デモ
- EPSで公開すべき情報、制限すべき情報、OEM依存に置く情報の分類
- cyber/SBOM方向と同じく、既存診断仕様やOEM診断基盤と被るかのKill表

### Kill条件

- OEMが診断コンテンツを完全指定し、サプライヤ提案余地がない
- SOVD採用時期が遠く、現行UDS改善にもつながらない
- 既存ODX/diagnostic authoring toolingで同じことをやっている

## 次候補3: 公開recall / ODI / TSB市場要求モニタ

### 市場需要

公開recall、ODI、TSBには、EPS assist loss、警告灯+DTC、software/failsafe、MDPS hardware、worm gear、steer-by-wire関連の市場シグナルが出る。

### 未解決の痛み

ただし、公開事例を集めるだけでは商品にならない。
過去の探索でも、Market Pain Scenario Library単体は弱いと判断した。

### 仮説

市場要求モニタは、単体商品ではなく、次候補1と2に入力する。

使い方:

- steer-by-wireで何を説明すべきかの市場トリガ
- SOVD診断コンテンツで何を見せるべきかの市場トリガ
- RFQ / design reviewで聞かれそうな質問生成

### Kill条件

- 事例紹介だけで終わる
- steer-by-wireやSOVDの設計証拠へ接続できない
- サプライヤの設計、診断、品質、営業のどの業務にも転記できない

## 優先順位

| Rank | Candidate | Next action | Position |
|---:|---|---|---|
| 1 | Steer-by-wire safety / redundancy / cyber evidence | 最初に深掘り | Primary |
| 2 | SOVD / next-generation diagnostics content design | 1の後、または並行で軽く確認 | Extension |
| 3 | Public recall / ODI / TSB market requirement monitor | 1と2の入力に限定 | Input only |

## 次アクション

次にやるべきことは、Steer-by-wire方向のKill-first検証である。

最初から商品名を作らない。
まず以下を確認する。

1. 既存ISO 26262 / SOTIF / cyber / safety caseに飲まれないか
2. steeringサプライヤがcomponent boundaryで説明できる領域があるか
3. 公開情報だけで、従来EPSとの差分を自然言語で説明できるか
4. OEM vehicle-level設計に依存しすぎないか
5. 1ページデモにしたとき、汎用安全資料ではなくsteer-by-wire固有に見えるか

ここで差分が見えなければ、Steer-by-wire方向もKillする。
