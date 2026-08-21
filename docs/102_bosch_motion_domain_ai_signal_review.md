# Bosch Motion Domain AI Signal Review

## 結論

Boschの公開情報は、このRepoの本線を少し強める材料になる。
ただし、強めるのは「AIでEPS故障や交換時期を予測する」方向ではない。

強まるのは、次の仮説である。

> by-wire、車両運動制御、車載コンピュータ、AI活用が進むと、EPSサプライヤは単体部品の説明だけでなく、上位の車両運動制御から来る要求に対して、操舵側で何を受けられるか、何を制限するか、異常時に何を説明できるかを整理する必要が増える。

これは、OEM用途想定をEPS側の確認観点へ翻訳する既存本線の延長である。
ただし、より強く「motion-domain上位制御から操舵アクチュエータへの要求を、EPSサプライヤの製品、診断、安全説明、顧客技術説明へ翻訳する」方向へ寄せる。

ソース別の作業表は [data/bosch_motion_domain_ai_signal_review.tsv](../data/bosch_motion_domain_ai_signal_review.tsv) に置く。

## 何を判断しているか

判断しているのは、BoschがEPS故障予測商品を出したかではない。
また、BoschがQM領域のAIで操舵安全制御を直接行うと公開したかでもない。

判断しているのは、公開情報から次が言えるかである。

> by-wireやmotion-domain制御が進むと、EPSサプライヤ側にも、上位制御、AI活用、安全境界、診断、ソフト更新、サービス説明をつなぐ説明責任が増える可能性がある。

この可能性があるなら、Repoの次の作業は、駐車場や低速操舵の用途翻訳だけでは少し狭い。
「上位motion controllerから来る操舵要求を、EPS側の受け入れ境界、制限境界、診断境界、禁止主張へ翻訳する」方向も検証対象に加える。

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `OEM Usage Translation Rule`
6. `Mandatory Rule Check Before Stop / Kill / Archive`

この文書では、StopやArchiveを出していない。
ただし、方向転換に近い判断を含むため、次を確認する。

- Bosch公開情報を、EPS故障予測や交換時期予測の根拠にしない
- AI、QM、ASILという言葉だけで、steering制御実装を断定しない
- OEMやBoschのplatform事業を、EPSサプライヤ単独の外販商品と混同しない
- EPSサプライヤの成果物へ落ちるかを判断軸にする
- 汎用SDV、汎用AI、汎用domain controllerの話に広げすぎない

## 市場需要

車両がsoftware-definedになり、by-wire、車載コンピュータ、車両運動制御、AI活用が同じ商談や展示で語られるようになると、OEMは単体部品ではなく、車両機能としての説明を求めやすくなる。

操舵に関しては、上位の車両運動制御や自動運転機能から要求が来る。
そのときEPSサプライヤは、操舵アクチュエータとして何を受けられるか、どの条件で制限するか、どの異常時に何を説明できるかを、製品企画、診断企画、安全設計、顧客技術説明の言葉へ落とす必要がある。

## 公開情報から見えること

### 1. Act-by-wire / steer-by-wire は公開展示されている

Bosch Japanは「人とくるまのテクノロジー展 2026 Yokohama」で、ブレーキバイワイヤとステアバイワイヤを含むAct-by-Wireを展示対象にしている。
公開ページでは、ステアバイワイヤについて、機械的接続をなくすこと、カスタマイズやOTA、安全基準への対応に触れている。

出典:

- Bosch Japan, `人とくるまのテクノロジー展 2026 Yokohama`
  <https://corporate.bosch.co.jp/news-and-stories/aee-2026/>

意味:

これは、by-wireが公開営業・展示の前面に出る段階にあることを示す。
ただし、EPS故障予測やAI操舵制御の根拠ではない。

### 2. Vehicle Motion Management は、複数ドメインの統合制御として公開されている

Bosch Mobilityは、Vehicle Motion Managementを、ブレーキ、ステアリング、パワートレイン、シャシーをまたいで車両運動を制御するソフトウェアとして公開している。
またIAA Mobility 2025の公開情報では、by-wireと組み合わせることで、ブレーキやステアリングのアクチュエータを個別に制御する方向を示している。

出典:

- Bosch Mobility, `Vehicle Motion Management`
  <https://www.bosch-mobility.com/en/solutions/software-and-services/vehicle-motion-management/>
- Bosch Mobility / Bosch press release, `IAA Mobility 2025`
  <https://us.bosch-press.com/pressportal/us/en/press-release-28544.html>

意味:

これは、操舵が単体EPSの話だけでなく、vehicle motionの一部として扱われる公開シグナルである。
EPSサプライヤ視点では、上位motion controlから来る要求と、操舵側の制限・診断・説明境界を整理する必要が出やすい。

### 3. Motion integration platform は、ステアリングを含む安全関連・時間制約のあるcross-domain coordinationを示している

Bosch Mobilityは、Motion integration platformを、powertrain、chassis、steeringを含む複数ドメインにまたがるvehicle dynamics functions向けのplatformとして公開している。
公開ページでは、安全関連で時間制約のあるタスクを、中央のvehicle computer上でcoordinationする文脈が出ている。

出典:

- Bosch Mobility, `Motion integration platform`
  <https://www.bosch-mobility.com/en/solutions/vehicle-computer/motion-integration-platform/>

意味:

これは、このRepoにとって一番強い材料である。
EPSサプライヤ側の問いは、「上位motion platformが操舵へ何を要求するか」ではなく、「その要求を受けた操舵側が、どの境界なら説明責任を持てるか」になる。

### 4. AIは公開されているが、操舵故障予測やAI操舵制御とは読まない

BoschはAI in the car、AI cockpit、ADAS、SDV文脈でAI活用を公開している。
またSDV whitepaperでは、AI、cross-domain、ASIL/QMのような語が同じ大きな文脈に出てくる。

出典:

- Bosch Mobility, `AI in the car`
  <https://www.bosch-mobility.com/en/company/current-news/ai-in-the-car/>
- Bosch Mobility, `Collaborating to unlock the full technical potential of software-defined vehicles`
  <https://www.bosch-mobility.com/media/global/mobility-topics/software-defined-vehicle/whitepaper-collaborating-to-unlock-the-full-technical-potential-of-software-defined-vehicles.pdf>

意味:

AI活用の公開シグナルはある。
ただし、ここから「AIがEPS故障予測をする」「QM AIがsteering safety制御を直接担う」とは言わない。
Repoで使うなら、「AIや上位softwareが増えるほど、操舵側が受ける要求、制限、診断、禁止主張を明確にする必要が増える」という推論に留める。

補足:

2026年のBosch / Uptake発表とBosch Predictive Diagnosticsを見ると、fleet / connected vehicle / cloud diagnosticsの文脈では、predictive maintenance、vehicle health、component-specific load and diagnostic featuresが明確に出ている。
この点は [docs/103_bosch_predictive_diagnostics_meaning_review.md](103_bosch_predictive_diagnostics_meaning_review.md) に切り出す。
つまり、`AI cockpit` や `motion integration platform` からEPS故障予測を読むのではなく、`Predictive Diagnostics` と `Cloud and predictive diagnostics` から、steering predictive diagnostics / predictive maintenance / vehicle healthの対象を読む。

## 未解決の痛み

Boschの公開情報を見ると、vehicle motion、by-wire、vehicle computer、AIが同じ大きな方向へ収束しているように見える。
しかし、EPSサプライヤの実務では、それをそのまま「うちもAIを積む」「うちもdomain controllerを売る」とは言えない。

未解決の痛みは、次である。

1. 上位motion controllerから操舵要求が来たとき、EPS側が受ける条件、制限する条件、拒否またはfallbackする条件をどう説明するか
2. AIや最適化が上位にある場合、操舵側の安全境界、診断境界、責任境界をどう説明するか
3. by-wireやmotion-domain文脈で、既存EPS仕様、DTC、freeze frame、software/calibration ID、service noteをどう再整理するか
4. OEM向けに、EPS単体の仕様表ではなく、motion-domainの一部として何を言えるか、何を言ってはいけないかをどう整理するか

## 仮説

Boschの公開シグナルを受けた新しい検証仮説は、次である。

> EPSサプライヤは、上位motion controllerやAI活用を含む車両運動制御の中で、操舵側が受けられる要求、制限する条件、異常時の説明、診断の信用境界を整理する短期assessmentを提供できる可能性がある。

これは、domain controllerやAI制御を作る商品ではない。
また、EPS故障予測でもない。

初期提供物は、次の4点に絞る。

1. 上位motion controllerから操舵側へ来る要求を、EPS側の受け入れ境界へ翻訳する表
2. by-wire / degraded / fallback時に、EPSサプライヤが言えることと言ってはいけないことの表
3. AIや最適化が上位にある場合の、操舵側の安全・診断・顧客説明境界
4. 既存DTC、freeze frame、software/calibration ID、service noteをmotion-domain文脈へ置き直す質問票

## EPSサプライヤとして何ができるか

EPSサプライヤとして売る候補:

> 上位motion controllerやby-wire構成を前提に、操舵アクチュエータ側の受け入れ境界、制限境界、診断境界、禁止主張を整理する短期assessment。

EPSサプライヤとして実施できる候補:

- OEMのmotion-domain architectureを受けたとき、操舵側に必要な確認質問を作る
- 上位要求に対するEPS側の受け入れ、制限、fallback、warning、diagnostic boundaryを自然言語で整理する
- 既存DTC / freeze frame / extended data / software IDを、motion-domain説明でどう使えるか確認する
- AIや上位制御がある場合に、EPSサプライヤが言ってよいことと言ってはいけないことを切る

EPSサプライヤとして言ってはいけないこと:

- BoschがAIでEPS故障予測を公開した
- QM AIがsteering safety controlを直接担うと公開された
- EPSサプライヤ単独でdomain controllerやvehicle motion platformを外販できる
- 公開情報だけで、OEMの安全architectureやdiagnostic designの不足を断定できる

初期対象外:

- 汎用SDV platform
- domain controllerそのもの
- 汎用AI cockpit
- 汎用IDS / CSMS / TARA支援
- EPS故障予測、交換時期予測、保証費削減

## 次に見る最小項目

次に作るなら、`docs/101` の質問票へ、次の別枠を追加する。

1. OEMのmotion-domain architectureを受けたとき、操舵側が受けるrequest typeは何か
2. そのrequestに対して、EPS側が受け入れる条件、制限する条件、拒否する条件、fallbackする条件は何か
3. 上位AIや最適化が関与する場合、EPSサプライヤは何を安全境界として説明できるか
4. 既存DTC / freeze frame / software IDは、motion-domain説明のどこに使えるか
5. これが既存safety case、FMEA、diagnostic specification、RFQ回答の言い換えで終わらないか

## 判定

Proceed候補:

- 製品企画、安全設計、診断企画、顧客技術説明の少なくとも2部署が、motion-domain文脈で具体的な確認質問を出せる
- 上位制御から来る操舵要求に対して、EPS側の受け入れ・制限・fallback・diagnostic boundaryを整理する需要がある
- 既存安全資料や診断仕様の単なる要約ではなく、OEM向け説明やRFQ確認に転記できる

Hold:

- Bosch公開情報は強いが、サプライヤEPSサプライヤの成果物へ落ちる部署がまだ曖昧
- motion-domain architectureの具体入力がないと、質問が一般論で止まる

Stop候補:

- 既存safety case、FMEA、diagnostic specification、RFQ回答と同じ説明にしかならない
- EPSサプライヤではなく、OEM、Boschのようなplatform supplier、domain controller supplierの話に吸収される
- 価値説明に、AI操舵制御、EPS故障予測、保証費削減、安全保証の主張が必要になる

Stop候補と書く場合も、最終Stopではない。
最終判断では、上位ルールに沿ったRule Checkを改めて書く。

## CoVe

| 検証質問 | 回答 | Confidence | 反映 |
|---|---|---:|---|
| Boschはby-wireを公開展示しているか | Yes。Bosch Japan AEE 2026ページでAct-by-Wire、ブレーキバイワイヤ、ステアバイワイヤが出ている。 | High | 公開情報1に反映 |
| Boschはvehicle motionをsteeringを含む統合制御として公開しているか | Yes。Vehicle Motion ManagementとMotion integration platformでsteeringを含むcross-domain文脈が出ている。 | High | 公開情報2、3に反映 |
| BoschがAIでEPS故障予測を公開したと言えるか | No。AI公開情報はあるが、EPS故障予測や交換時期予測とは読めない。 | High | 禁止主張に反映 |
| QM AIがsteering safety controlを担うと公開されたと言えるか | No。AI、ASIL/QMの語は公開資料に出るが、この断定はできない。 | Medium | 禁止主張に反映 |
| EPSサプライヤの業務成果物へ落とせるか | 仮説としては可能。製品企画、安全設計、診断企画、顧客技術説明の確認質問へ落とす必要がある。 | Medium | 次に見る最小項目に反映 |

## EPSサプライヤとしての言い方

言ってよいこと:

> Boschの公開情報では、by-wire、vehicle motion management、vehicle computer、AI活用が同じSDVの文脈で語られている。これは、操舵が単体EPSではなく、上位motion-domain制御の一部として説明される場面が増える可能性を示す。EPSサプライヤとしては、上位制御から来る操舵要求に対して、受け入れ境界、制限境界、fallback、診断、顧客説明をどう整理するかを検証する価値がある。

まだ言ってはいけないこと:

> BoschがAIでEPS故障、残寿命、交換時期、安全性、保証費削減を予測する商品を公開した。

> QM AIがsteering safety controlを直接担うことが確認できた。

> EPSサプライヤ単独で、vehicle motion platformやdomain controllerを外販できる。
