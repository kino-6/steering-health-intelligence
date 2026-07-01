# Steering ECU Software / Cyber Evidence Pack の価値確認

## 結論

ユーザの直感どおり、**この方向はかなり既存業務・既存ツールと被る**。

TARA、SBOM、脆弱性管理、ISO/SAE 21434、UN R155/R156対応は、すでに自動車サイバー領域の主要テーマであり、既存ツールやサービスも多い。
したがって、`SBOMを作る`、`TARAを作る`、`脆弱性を管理する` を売り物にすると、ほぼ筋が悪い。

現時点で残る可能性があるのは、かなり狭い。

> EPS / steering ECUサプライヤの既存CSMS、TARA、SBOM、診断仕様、更新仕様、安全設計を、OEMからの具体質問に答えられるsteering ECU固有の説明へ束ねること。

つまり、主商品ではなく、**RFQ / 監査 / OEM問い合わせの回答支援**に近い。
これも、既存部署がすでに同じことをやっているならKillでよい。

## 何を試したか

今回試したのは、前回作った成果物が既存業務と本当に違うかである。

見た対象:

- TARA
- SBOM
- vulnerability management
- diagnostic access
- software update evidence
- fail-safe / assist-state evidence
- OEM response one-pager

評価観点:

1. 既存ツールや既存業務がすでにカバーしていないか
2. EPSサプライヤ固有の価値が残るか
3. 有償サービスとして買う人がいるか
4. 内部資料なしでも価値を示せるか
5. Killすべき条件が具体的か

## 公開情報で見えた既存プレイヤー

公開情報だけでも、既存プレイヤーの厚さはかなり見える。

| 既存例 | 公開情報から見える内容 | このRepoへの示唆 |
|---|---|---|
| ETAS ESCRYPT CycurRISK | ISO/SAE 21434とUN R155に準拠したTARAツール。attack surface、attack tree、damage scenario、再利用可能な知識、TARA serviceを提供 | TARAやattack-surface整理は既存領域 |
| Ansys Medini Cybersecurity SE | 自動TARA、vulnerability management、SBOM、ISO/SAE 21434 compliance workflow、HW/SW BOMとTARA modelのlinkageを提供 | SBOM-to-TARAや脆弱性管理も既存領域 |
| Siemens Sigrid | Automotive向けにSBOM管理、静的解析、Polarion連携、ISO/SAE 21434、UN R155/R156対応を訴求 | SBOM生成・管理は汎用ツールで既に強い |
| ThreatZ / Uraeus | TARA、SBOM、CVE monitoring、OEM/Tier-1 SBOM exchange、R156 update traceability、Supplier Portalを訴求 | OEM/Tier-1間のSBOM交換やCVE impactも既存商品がある |

このため、前回案のうち以下は差別化になりにくい。

- TARAそのもの
- SBOM生成
- CVE monitoring
- vulnerability management workflow
- ISO/SAE 21434 / R155 compliance report
- TARAとSBOMのlinkage
- OEM/Tier-1 SBOM exchange portal

ここを主商品にすると、既存ツールの劣化版になりやすい。

## 残る価値候補

残るとすれば、以下だけである。

> 汎用CSMS/TARA/SBOMの成果物を、steering ECUの診断・更新・assist state・fail-safe・security accessに引き寄せて、OEM回答文にすること。

これはツールではなく、翻訳・整理・回答支援である。

例:

| OEMから聞かれる問い | 汎用成果物だけだと弱い点 | steering ECU固有に落とすと残る可能性 |
|---|---|---|
| このCVEはEPSに影響するか | SBOM上は部品が見えるが、EPS機能影響が見えない | bootloader、診断stack、CAN stack、assist/fail-safe stateへの接続を示す |
| diagnostic securityは安全か | UDS service listだけでは安全影響が分かりにくい | routine / DID / security accessを、許可操作・禁止操作・安全影響で分ける |
| update後にEPSは正しい状態か | update手順だけではsteering ECU状態が見えない | software/calibration ID、post-update check、fail-safe stateを整理する |
| cyber異常時のEPS挙動は何か | TARA上のdamage scenarioだけでは実装状態が見えない | assist limitation、warning、limp-home、manual steer前提へ接続する |

ただし、これも新規性は弱い。
既存のcybersecurity case、safety case、diagnostic specification、software release checklistに同じ内容があるなら不要である。

## 価値判定

| 判定項目 | 結果 |
|---|---|
| 市場需要 | ある。規制・標準・SBOM・脆弱性対応は明確に存在する |
| 既存プレイヤー | 強い。汎用TARA/SBOM/CVE管理はすでに厚い |
| EPSサプライヤが主語になれるか | component-level説明なら可能 |
| 独立商品としての強さ | 弱い |
| 固定スコープassessmentとしての可能性 | 条件付きであり |
| 内部資料なしで価値検証できるか | デモ形状は作れるが、既存業務との差分は検証できない |
| 現時点判断 | Hold寄り。次の1回で差分が見えなければKill |

## 今の正しい言い方

悪い言い方:

> EPS向けSBOM / cyber evidence packを売る。

良い言い方:

> 既存のCSMS、TARA、SBOM、CVE管理、診断仕様、更新仕様、安全設計がある前提で、それらをOEMからのsteering ECU固有質問に答えられる形へ束ねる余地があるかを確認する。

さらに短く言うなら、

> サイバー/SBOMを作る話ではなく、既にあるサイバー/SBOM成果物を、EPSの診断・更新・fail-safe説明へ翻訳する話。

## 次に見る最小項目

内部資料を使わずに進めるなら、ここで止めてもよい。
価値の有無は、結局、対象サプライヤの既存CSMS/TARA/SBOM/CVE運用との差分で決まる。

どうしても次を見るなら、内部資料の中身ではなく、以下の「存在確認」だけで足りる。

| 最小確認 | 聞く相手 | Yesなら |
|---|---|---|
| steering ECU固有のOEM cyber/SBOM質問が実際に来ているか | Sales engineering / supplier quality / cybersecurity | 来ていないならKill寄り |
| 既存CVE回答にEPS機能影響、release ID、software/calibration IDが入っているか | Cybersecurity / software release | 入っているならKill |
| 診断security tableにroutine/DIDの安全影響と禁止操作が入っているか | Diagnostics | 入っているならKill |
| cyber abnormal conditionとassist/fail-safe stateが紐づいているか | Systems / safety / cybersecurity | 紐づいているならKill |
| OEM回答用の1枚資料が既にあるか | Supplier quality / sales engineering | あるならKill |

この5点のうち2つ以上で明確な不足がないと、この方向は有償化しにくい。

## 判定ルール

Proceed:

- OEMからsteering ECU固有のcyber/SBOM問い合わせが実際に来ている
- 既存SBOM/CVE管理はあるが、EPS機能影響やOEM回答文に落ちていない
- 診断securityやsoftware updateの資料はあるが、監査/RFQ回答に転記しにくい
- cybersecurity、software、diagnostics、supplier qualityの複数部署にまたがり、回答作成が手作業になっている

Kill:

- 既存CSMS/TARA/SBOM/CVE管理で同じことをやっている
- 既存ツールがTARA、SBOM、CVE、OEM回答まで十分に接続している
- EPS固有の質問がほとんど来ていない
- OEM指定様式が強く、サプライヤ側で提案や追加整理を入れる余地がない
- 成果物が汎用サイバー資料に見える

## 参照ソース

- ETAS ESCRYPT CycurRISK: https://www.etas.com/ww/en/products-services/cybersecurity-products/escrypt-cycurrisk/
- Ansys Medini Cybersecurity SE: https://www.ansys.com/products/safety-analysis/ansys-medini-analyze-for-cybersecurity
- Siemens Sigrid Compliance & Cybersecurity for Automotive: https://www.siemens.com/en-us/products/sig-software-improvement-group-sigrid-compliance-cybersecurity-for-automotive/
- ThreatZ Automotive SBOM Management: https://uraeus.io/automotive-sbom/

## EPSサプライヤとしての現時点結論

この方向は、**かなりKill寄りのHold**である。

理由は、既存プレイヤーと既存業務が強すぎるため。
ただし、steering ECU固有のOEM問い合わせ回答に既存成果物を束ねる用途だけは、まだ少し残る。

次にやるなら、商品開発ではなく、5項目の存在確認をする。
そこで差分が見えなければ、この方向も止める。
