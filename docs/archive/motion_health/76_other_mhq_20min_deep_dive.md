# MHQ002 / 004 / 006 / 007 / 008 / 009 / 010 20分深掘り

## 結論

MHQ001を閉じた後に残るMHQを見ても、外販テーマとしての判断は変わらない。

市場側の需要はある。
fleet operator、OEM fleet service、remote diagnostics platformは、車両停止、予定外入庫、診断時間、部品準備、整備優先度に困っている。
また、操舵系を単体で見るより、ブレーキ、足回り、タイヤ、駆動系、通信と一緒に見る方が、公開情報上の市場signalには合う。

ただし、それはEPS/SbWサプライヤが公開情報だけで外販商品を作れる、という意味ではない。
むしろ、他MHQを深掘りしたことで、外販Stop判断は補強された。

理由は3つである。

1. 買い手はfleet / OEM service / remote diagnostics platform側に見える
2. 価値ある出力は既存remote diagnosticsがかなり扱っている
3. EPS/SbWサプライヤ固有の価値は、内部data field、service outcome、特定programがある場合だけ証明できる

したがって、MHQ002 / 004 / 006 / 007 / 008 / 009 / 010は、MHQ001を復活させる材料ではなく、Archive判断の補強材料として扱う。

## Item Conclusions

| Item | Conclusion | Confidence | Evidence | Weak point | Next action |
|---|---|---|---|---|---|
| MHQ002 | 外販買い手はfleet operator、OEM fleet service、remote diagnostics platformが先に見える。EPS/SbWサプライヤは直接売り手ではなく特定program内のdomain contributor | Medium-High for fleet/OEM buyer, Low for supplier-direct buyer | International、Geotab、Bosch、ZF、Platform Science | EPS/SbWサプライヤ単独の予算主体性が見えない | 外販buyerは置かない。再開時だけOEM program内利用者へ限定 |
| MHQ004 | 運行可否、入庫優先度、診断時間短縮、部品準備は市場側で強い。ただし既存remote diagnosticsが同じ出力を扱う | High for workflow, Low-Medium for supplier gap | Bosch、International、Geotab、ZF | steering-specific outputが既存診断を超える証拠がない | 再開時の評価軸としてだけ残す |
| MHQ006 | SbW冗長低下は安全上重要。ただし整備判断商品ではなく、安全設計・認証・診断業務に見える | Medium for safety relevance, Low for maintenance offer | NHTSA SbW safety assessment、Piher、Bosch fail-operational EPS既存調査 | fleet maintenance offerではなく安全説明で終わる | 特定programでdegraded stateがservice decisionへ転記される場合だけ再開 |
| MHQ007 | motion/chassis healthとして束ねる方向は正しい。ただしその分、EPS単独外販ではなくOEM/Tier1/platform領域に寄る | High for bundle direction, Low for EPS-only offer | Nexteer MotionIQ/Health、Nexteer VHM、ZF chassis health、3rd Eye | bundle化するとEPS/SbWサプライヤ単独offerではない | 知見として残し、supplier-owned contributionだけ再開条件にする |
| MHQ008 | 実使用条件を品質・開発へ戻す価値はある。ただし外販商品ではなくOEM partnershipまたはsupplier internal loop | Medium-High for quality value, Low for public-only offer | Nexteer actual lifecycle conditions、ZF non-personalized data / cloud exchange | service outcomeと内部品質課題に接続しないと価値証明不可 | 特定OEM programのquality / product engineering向け短期支援だけ |
| MHQ009 | 初期デモは外販を進めるデモではなくKill確認sampleが正しい | Medium | docs/75、final kill-check sample | 公開情報だけでは実EPS不足や既存診断不足を証明できない | Archive evidenceとして残す |
| MHQ010 | 新テーマはKill条件を満たしている | Medium-High | docs/70-75、MHQ003/005、今回の他MHQ深掘り | 市場需要自体は存在するため知見廃棄ではない | 外販テーマとしてArchive |

## Deepened Points

### MHQ002: 買い手はEPS/SbWサプライヤではない

買い手として強く見えるのは、fleet operator、OEM fleet service、remote diagnostics platformである。
Internationalは、fault code、severity、action plan、dealer parts inventory、service center mapping、API connectionをfleet向けに出している。
Geotabも、fleet managerがactive diagnostic faultsやcritical engine dataを使って修理優先度を決める文脈を説明している。
Boschは、logistics companiesやmobility service providers向けにfleet health、risk / criticality、recommended next stepを提示している。

これらは、市場需要の存在を支持する。
しかし、EPS/SbWサプライヤが直接売れることは支持しない。

EPS/SbWサプライヤに残る立場は、直接買い手ではなく、特定OEM programの中で操舵系の意味づけを提供するdomain contributorである。

### MHQ004: 出力は正しいが、既存playerがすでに扱う

「交換時期」ではなく、「次の運行に出す」「先に入庫」「次回点検まで様子見」「部品準備」「診断時間短縮」へ落とす方向は正しい。

ただし、Boschはrisk / criticality assessmentとrecommended next stepを出している。
Internationalはseverity rating、action plan、parts inventoryまで扱っている。
Geotabはactive diagnostic faultsとcritical engine dataから修理優先度を決める文脈を持つ。

つまり、MHQ004は市場workflowとしては強いが、EPS/SbWサプライヤ外販テーマを救わない。
差分を出すには、操舵系固有のDID読み順、assist state、thermal derate、software / calibration ID、SbW degraded stateが、既存remote diagnosticsでは出せない判断に変わる必要がある。
これは公開情報だけでは証明できない。

### MHQ006: SbW冗長低下は安全論点であり、整備商品ではない

SbWや高可用操舵では、冗長系、fail-safe、warning、DTC coverageは重要である。
NHTSAのgeneric SbW safety assessmentも、functional safety requirementsやDTC coverageを扱っている。
Piherの公開説明でも、fail-safe modeやwarning systemが出てくる。

しかし、これは整備判断商品の需要証明ではない。
公開情報上は、安全設計、認証、診断設計、顧客説明の範囲に見える。

したがって、MHQ006は外販テーマとしてはStopである。
再開するなら、特定programで「このdegraded stateは次の運行に出してよいか」というservice decisionへ実際に転記される場合だけである。

### MHQ007: bundle方向は正しいが、EPS単独価値は薄まる

操舵系だけでなく、ブレーキ、足回り、タイヤ、駆動系、通信と一緒に見る方向は、市場signalとしてはかなり正しい。
Nexteer MotionIQ/Healthはsteering、chassis components、tiresをまとめている。
ZFはchassisやdrive trainのtechnical conditionを扱い、fleet operatorやshared mobility providerをbenefit先に置いている。
Nexteer VHMもfleet downtimeやtire lifecycle dataを説明している。

ただし、bundle化すればするほど、EPS/SbWサプライヤ単独の外販offerではなくなる。
OEM、広いTier1、fleet platform、remote diagnostics platformの領域になる。

したがって、MHQ007は「方向性として正しいが、外販Stopを覆さない」と読む。

### MHQ008: 実使用条件からの製品改善は価値あり。ただし外販ではない

Nexteerは、actual lifecycle conditionsからOEMやsupplierのproduct quality / development insightを得ると説明している。
ZFも、non-personalized dataを使い、OEM cloudとZF cloudのデータ交換を説明している。

これは価値がある。
しかし、外販商品というより、OEM partnershipまたはsupplier internal quality / product engineering loopである。
整備履歴、交換結果、再発有無、作業時間、内部品質課題に接続しなければ、価値は証明できない。

また、ここで保証費削減やroot cause断定を言うと、旧テーマの危ない主張に戻る。

### MHQ009 / MHQ010: デモとKill条件

初期デモは、外販を進めるためではなく、Kill確認sampleとして作るのが正しい。
docs/75では、高負荷操舵でthermal limitまたはassist limitationに入った仮想ケースを、DTCだけ、既存remote diagnostics、supplier domain triageの3列で比較した。

このsampleで見えたのは、supplier差分がありうるとしても、内部data fieldとservice outcomeがないと証明できない、ということだった。

よってMHQ010は、外販テーマとしてのKill条件を満たしている。

## What Changed

前回まで:

> MHQ001はStop / Archive。ほかのMHQは未処理。

今回:

> ほかのMHQを見ても、外販Stop判断は変わらない。むしろ補強される。

変わった点:

- MHQ002により、買い手はEPS/SbWサプライヤ直接ではなくfleet / OEM service / platform側と整理した
- MHQ004により、価値ある出力は正しいが既存remote diagnosticsが強いと整理した
- MHQ006により、SbW degraded stateは安全・診断業務であり、整備判断商品ではないと整理した
- MHQ007により、bundle方向は正しいがEPS単独外販ではないと整理した
- MHQ008により、品質改善価値は内部loopまたはOEM partnershipとして残すと整理した
- MHQ009 / 010により、デモはProceed用ではなくKill確認用と整理した

## Market Demand First

| Field | 内容 |
|---|---|
| Market demand | Fleet / OEM service / remote diagnosticsでは、車両停止、予定外入庫、診断時間、部品準備、修理優先度の需要がある。 |
| Evidence signal | Bosch、International、Geotab、ZF、Nexteer、Platform Scienceがfleet maintenance、remote diagnostics、vehicle health、chassis / motion healthを説明している。 |
| Hypothesis | EPS/SbWサプライヤが価値を出すには、操舵系状態量を既存remote diagnosticsでは出せない運行・整備判断へ翻訳する必要がある。 |
| Solution | 外販商品化はしない。特定OEM programで再開する場合だけ、supplier-owned dataとservice decisionの接続を確認する。 |
| Buyer / user | 外販では置かない。再開時だけOEM fleet service、remote diagnostics、supplier diagnostics / service engineering / field quality。 |
| Initial artifact | docs/75のKill確認sampleと今回のitem conclusion tableをArchive evidenceにする。 |
| Validation method | 再開時は実DTC/DID/freeze frame/service outcomeを使い、既存remote diagnosticsとの差分を1ケースで確認する。 |
| Kill criteria | data access不可、service outcome不可、既存remote diagnosticsで十分、bundle化してsupplier単独価値が消える、交換時期予測に戻る。 |

## EPS Supplier Lens

EPS/SbWサプライヤとして売るか:

> 売らない。MHQ002/004/006/007/008/009/010を見ても、外販offerとして成立する材料は出ない。

EPS/SbWサプライヤとして実施できること:

> 特定OEM programで、操舵系状態量、既存診断仕様、service decision、顧客説明をつなぐ短期支援だけ。

EPS/SbWサプライヤとして言ってはいけないこと:

> EPS交換時期が分かる、既存remote diagnosticsを置き換える、fleet downtimeを削減できる、root causeを断定できる、安全機能を代替できる、とは言わない。

初期対象外:

> OEM fleet platform、汎用remote diagnostics、service network運営、fleet全体監視、driver behavior、engine diagnostics、tire-only analytics。

次に見せる部署:

> business developmentではなく、diagnostic engineering、service engineering、field quality、customer technical interfaceへ、Archive判断と再開条件として共有する。

## Still Weak

弱いまま残る点はあるが、外販Stop判断を覆す弱さではない。

- 特定OEM programの内部データがあれば、supplier domain triageの価値は変わる可能性がある
- NexteerやZF型のsupplier health offeringは存在するため、完全に市場がないとは言わない
- motion/chassis bundleとしての市場はあるが、それはEPS単独外販ではない

## Stop / Continue Judgment

これ以上、公開情報ベースで他MHQを広げる価値は低い。

MHQ001は閉じる。
他MHQも、外販テーマを復活させる材料ではなく、Archive判断の補強材料として扱う。

再開条件は1つだけである。

> 特定OEM programで、EPS/SbW固有のDTC/DID/freeze frame/service outcomeに触れ、既存remote diagnosticsでは出せない操舵系判断があると確認できること。

## Sources

- Nexteer MotionIQ software suite: https://www.nexteer.com/release/nexteer-unveils-its-motioniq-software-suite-for-intelligent-motion-control/
- Nexteer Vehicle Health Management: https://www.nexteer.com/software/vehicle-health-management/
- ZF Vehicle Health Monitoring: https://press.zf.com/press/en/releases/release_92162.html
- ZF Fleet Management Solutions: https://www.zf.com/products/en/cv/ind/news/maximize_profitability__minimize_tco_with_zf_s_connectivity_solutions/uptime_fms.html
- Bosch Cloud and Predictive Diagnostics: https://www.bosch-mobility.com/en/solutions/software-and-services/cloud-and-predictive-diagnostics/
- International Advanced Remote Diagnostics: https://www.international.com/services/my-international/advanced-remote-diagnostics
- Geotab Fleet Maintenance: https://www.geotab.com/fleet-management-solutions/fleet-maintenance/
- Platform Science Remote Diagnostics: https://www.platformscience.com/blog/the-power-of-remote-diagnostics-for-fleet-maintenance
- NHTSA Generic Steer-by-Wire Safety Assessment: https://www.nhtsa.gov/sites/nhtsa.gov/files/documents/13502_812576_steerbywire.pdf
- Piher steer-by-wire redundancy: https://www.piher.net/news/steer-by-wire-ensuring-redundancy/
