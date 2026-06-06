# 公開情報だけで進める5候補の深掘り

## 結論

今すぐ次に進める候補は、5つを横並びで全部進めることではない。

最初に進めるべきなのは、**EPS / steering ECUのソフトウェアとサイバーセキュリティについて、OEMや監査に説明できる設計証拠を作ること**である。

これは、故障予測でも、追加ログでも、RCA/8D資料作成でもない。
EPSサプライヤが持っているECU、診断、ソフトウェア更新、SBOM、脆弱性対応、security access、fail-safe stateを、規制・標準・OEM説明に使える形にする話である。

候補1のサイバーセキュリティと候補2のSBOMは、分けて売るよりも一体で見る方がよい。
サイバー要求、ソフト部品表、脆弱性影響判断、診断アクセス制御、ソフト更新後確認は、同じ相手に同じタイミングで聞かれる可能性が高いからである。

現時点の判断は以下。

| 候補 | 判断 | 理由 |
|---|---|---|
| 1. サイバーセキュリティ設計証拠 | Proceed | 公開規制・標準で需要を説明でき、EPSサプライヤのcomponent境界で成果物を作れる |
| 2. SBOM / 脆弱性対応 | Proceed with 1 | SBOM単体では弱いが、サイバー証拠の中に入れると実務価値が出る |
| 3. SOVD診断コンテンツ | Hold as extension | 標準の方向性は明確だが、OEM診断基盤依存が強い。候補1の診断アクセス設計から派生させる |
| 4. Steer-by-wire設計証拠 | Watch / conditional | 将来性は強い。ただし対象顧客がSbWに向かっている場合だけ短期価値になる |
| 5. 公開市場要求モニタ | Input only | 単体商品にするとまた「こんな事例がある」で止まる。候補1-4の入力に限定する |

## 何を判断しているか

ここで判断しているのは、公開情報だけで、EPSサプライヤが次に具体的な商材またはデモへ進めるかである。

前回までの`Coverage Benchmark`は、対象EPSの実HILS、DTC、freeze frame、既存レビューとの差分が必要だった。
つまり内部資料がないと進まない。

今回は、その反省から、**公開情報自体が市場需要を作っている領域**に寄せる。
規制、標準、業界団体、サプライヤ発表が公開されていれば、少なくとも「なぜ今これを見るのか」は説明できる。

## 公開ソースから分かった需要

### 車両サイバーセキュリティはサプライヤも関係する

NHTSAの2022年版サイバーセキュリティベストプラクティスは、対象を車両メーカーだけに閉じていない。
車両電子システムやソフトウェアを設計・製造する組織、つまりサプライヤも含めている。
さらに、サプライチェーン内の各組織がサイバーセキュリティ上の役割を持つこと、サプライヤに明確な期待を伝えること、ECUごとのハードウェア/ソフトウェア構成を管理することに触れている。

UNECE R155/R156は、車両サイバーセキュリティ管理とソフトウェア更新管理に関する規則である。
UNECEの公開情報では、R155はサイバーセキュリティ管理、R156はソフトウェア更新管理を扱い、メーカーとサプライヤのリスク低減能力や監査に関する論点を含む。

ISO/SAE 21434は、車両のE/Eシステムに対するサイバーセキュリティエンジニアリング標準である。
NHTSA文書もこの標準を参照しており、組織、ライフサイクル、post-productionを含むサイバーセキュリティ活動を扱うものとしている。

このため、候補1は「市場需要あり」と置ける。
ただし、ここで言ってよいのは、認証代行ではなく、**EPS/steering ECUという部品境界で、OEMや監査に出せる設計証拠を作ること**までである。

### SBOMは自動車業界でも実務テーマになっている

Auto-ISACは2025年2月に、自動車向けSBOMの公開レポートを発表している。
同発表では、SBOMをソフトウェア製品の構成要素を示す階層的リストと説明し、自動車業界でソフトウェア製品の透明性、組織内連携、脆弱性管理を助けるものとしている。

NISTも、SBOMはソフトウェア構成の正式な記録であり、脆弱性の特定と修正を速めると説明している。
ただしNISTは、SBOMは既存の脆弱性管理やベンダーリスク評価を置き換えるものではない、とも明記している。

このため、候補2は「SBOMを作る」だけでは弱い。
EPSサプライヤとして価値にするなら、SBOMを以下へ接続する必要がある。

- このソフト部品はEPS ECUのどの機能に関係するか
- 脆弱性が出た場合、診断、ソフト更新、bootloader、通信、security access、fail-safeに影響するか
- OEMから問い合わせが来た時に、影響あり/なし/未確認をどう説明するか

したがって、候補2は候補1に統合して進める。

### SOVDは需要の方向性はあるが、初手の主商品にはしにくい

ASAM SOVDは、ソフトウェア化した車両を診断・通信するAPIであり、HPCだけでなくclassic ECUの診断コンテンツにもアクセスする標準である。
ASAMは、診断の焦点がハード故障の特定からソフトウェア問題の解析へ広がり、ソフトウェア更新プロセスにも診断通信が使われると説明している。

これは、EPS診断コンテンツをSOVD時代にどう見せるか、という問いにはつながる。
ただし、診断APIや車両診断基盤を持つのは多くの場合OEM側である。
EPSサプライヤが初手で主語になれるのは、SOVD基盤を作ることではなく、既存UDS/DTC/DID/freeze frame/software ID/security accessを、次世代診断に載せる前のコンテンツとして整理するところまでである。

したがって、候補3は単独商品ではなく、候補1の診断アクセス設計から派生させる。

### Steer-by-wireは強いが、短期顧客条件がある

ZFは2025年7月に、Mercedes-Benz向けに2026年からsteer-by-wire技術を供給すると発表している。
ZFは、steer-by-wireでは機械的な接続がなくなり、ソフトウェアで操舵比を変えられ、冗長設計により安全を支えると説明している。

Nexteerも2026年4月に、steer-by-wireの量産開始を発表している。
同社は、dual controllers、dual power supplies、multiple communication links、dual actuation pathsなどの多層冗長設計、fault diagnosis、redundancy、safety monitoringを強調している。

HELLAは2023年に、steer-by-wire向けセンサの量産受注を発表している。
同社は、steer-by-wireではステアリングコマンドが電気的に送られ、センサの冗長で高信頼な構成が高い安全要求を満たすと説明している。

つまり、候補4は将来性が強い。
しかし、対象顧客がsteer-by-wire開発を持っていない場合、短期の商材にはならない。
また、具体設計は対象アーキテクチャ依存が強いため、公開情報だけでは「設計証拠の型」までが限界である。

### 公開市場要求モニタは主商品ではない

公開recall、ODI、TSBは、市場で何が問題化しているかを見る材料としては有効である。
Repo内でも、EPS assist loss、警告灯+DTC、software/failsafe、MDPS hardware、worm gearなどの公開caseを整理済みである。

ただし、これ単体では以前止めた`Market Pain Scenario Library`と同じになる。
「こんな事例がある」だけでは、EPSサプライヤの予算や業務成果物に入らない。

このため、候補5は主商品にしない。
候補1-4で扱うべき要求や説明材料を見つけるための入力として扱う。

## スコアリング

| Rank | Candidate | Market demand | Supplier control | Public demo | Differentiation | OEM dependency | Decision |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | Steering ECU software/cyber evidence pack | 5 | 4 | 5 | 4 | 3 | Proceed |
| 2 | EPS ECU SBOM / vulnerability response | 5 | 4 | 5 | 3 | 3 | Proceed with 1 |
| 3 | SOVD diagnostics content design | 4 | 3 | 4 | 3 | 2 | Hold as extension |
| 4 | Steer-by-wire evidence pack | 5 | 3 | 4 | 4 | 2 | Watch / conditional |
| 5 | Public market requirement monitor | 3 | 4 | 5 | 1 | 4 | Input only |

読み方:

- Market demand: 公開情報から需要を説明できるか
- Supplier control: EPSサプライヤ側で成果物を作れるか
- Public demo: 内部資料なしでデモできるか
- Differentiation: 汎用コンサル、汎用ツール、既存業務との差分があるか
- OEM dependency: OEM側データや基盤がなくても初期価値を見せられるか

## 次に作る最小デモ

候補1と2を統合して、以下の1ページサンプルを作る。

> steering ECUの診断アクセス、ソフト更新、SBOM、脆弱性、assist/failsafe state、security accessを対象に、脅威、要求、検証証拠、OEM説明文を対応づける。

最初のデモは、実在製品を扱わない。
公開標準と一般的なsteering ECU構成だけで作る。

デモで見ること:

- 汎用CSMS/TARAの言い換えではなく、steering ECU固有に見えるか
- EPS cybersecurity、software、diagnostics、systems担当が使う成果物に見えるか
- SBOMと脆弱性対応が、単なる部品表ではなくEPS機能影響に接続しているか
- OEM説明文として転記できるか

デモで言ってはいけないこと:

- R155/R156認証を取れる
- ISO/SAE 21434準拠を保証できる
- 車両全体のサイバーリスクを閉じられる
- 対象EPSの既存設計にgapがある
- 事故や故障を予測できる

## サンプル: steering ECU software/cyber evidence pack

| 対象 | 市場/標準側の要求 | steering ECUで見ること | 提供できる証拠 | OEM向けの言い方 |
|---|---|---|---|---|
| 診断アクセス | 診断機能やツールのアクセス管理、不要なdebug accessの抑制 | UDS session、security access、routine control、DID読出し権限 | 診断サービス一覧、権限表、negative test結果 | 対象EPSでは量産診断で許可する操作と禁止する操作を分け、security accessと試験証拠で説明する |
| ソフト更新 | ソフト更新やOTA時の安全、復旧、完全性確認 | bootloader、署名、rollback、calibration ID、post-update check | update sequence、署名検証結果、version map、復旧試験 | 更新後にEPS software/calibration identityと基本状態を確認できる |
| SBOM | ソフト構成管理と脆弱性影響判断 | RTOS、bootloader、crypto、診断スタック、通信スタック、toolchain | SBOM、CVE triage表、影響あり/なし/未確認の判断記録 | 脆弱性が出た場合、どのEPS ECU software componentと機能に関係するかを追跡できる |
| センサ入力 | safety-critical systemへのsensor manipulation risk | torque sensor、angle sensor、redundancy plausibility | sensor plausibility check、fault injection result | センサ入力異常は冗長比較と異常時状態で扱う |
| 通信 | 車内通信のspoofing、replay、segmentation | CAN/Ethernet message、gateway経由診断、actuation command境界 | communication threat list、message authentication要否、network negative test | EPSが受け付ける通信と安全影響を分けて説明する |
| fail-safe / assist state | 攻撃または異常時の安全状態 | assist limitation、limp home、manual steer前提、warning | state transition table、safety concept link、test evidence | サイバー起因の異常でも、EPSがどの状態へ遷移するかを安全設計と紐づけて説明する |

このサンプルが刺さらない場合、候補1も弱い。
具体的には、顧客や社内担当が「これは既存CSMS/TARAや標準帳票に全部ある」と言うなら止める。

## Chain-of-Verification

| 問い | 検証結果 | 確度 | 判断への影響 |
|---|---|---|---|
| 市場需要は公開ソースで説明できるか | NHTSA、UNECE、ISO/SAE、Auto-ISAC、ASAM、ZF/Nexteer/HELLAで説明可能 | High | 需要説明は可能 |
| EPSサプライヤが主語になれるか | NHTSAはsuppliers/manufacturersを対象に含め、サプライチェーンの役割を明記。EPS ECUの診断/更新/ソフト部品はサプライヤ側の知識 | Medium-High | component-levelに限定すれば可能 |
| OEM領域を侵していないか | R155/R156認証、CSMS/SUMS、車両全体診断基盤はOEM領域。ここを代替しない前提に修正 | High | 提供物をcomponent evidenceに限定 |
| SBOM単体で売れるか | NISTもSBOMは既存の脆弱性管理を置き換えないと説明。Auto-ISACも脆弱性管理や組織連携に接続している | High | SBOM単体ではなく候補1へ統合 |
| SOVD単体で売れるか | ASAM SOVDはAPI/車両診断基盤寄り。EPSサプライヤはcontent整理までが自然 | Medium | Hold as extension |
| Steer-by-wireは短期候補か | 公開発表では量産化が進むが、対象顧客のSbWテーマがないと短期価値にならない | Medium | Watch / conditional |
| 公開市場モニタは売れるか | Repoの過去探索で単体scenario libraryは弱い。今回も単体では弱い | High | Input only |

## 参照ソース

- NHTSA, Cybersecurity Best Practices for the Safety of Modern Vehicles, 2022: https://www.nhtsa.gov/document/cybersecurity-best-practices-safety-modern-vehicles-2022
- UNECE, UN Regulation No.155: https://unece.org/transport/documents/2021/03/standards/un-regulation-no-155-cyber-security-and-cyber-security
- UNECE, UN Regulation No.156: https://unece.org/transport/documents/2021/03/standards/un-regulation-no-156-software-update-and-software-update
- ISO, ISO/SAE 21434:2021: https://www.iso.org/cms/%20render/live/en/sites/isoorg/contents/data/standard/07/09/70918.html
- Auto-ISAC, SBOM Informational Report announcement, 2025: https://automotiveisac.com/press-news/auto-isac-issues-software-bill-of-materials-informational-report-nbsp
- NIST, Software Security in Supply Chains: SBOM: https://www.nist.gov/itl/executive-order-14028-improving-nations-cybersecurity/software-supply-chain-security-guidance-20
- ASAM, SOVD: https://www.asam.net/standards/detail/sovd/
- ZF, Steer-by-Wire, 2025: https://press.zf.com/press/en/releases/release_89553.html
- Nexteer, Steer-by-Wire series production, 2026: https://www.nexteer.com/release/nexteer-puts-steer-by-wire-into-series-production/
- FORVIA HELLA, steer-by-wire sensor series production, 2023: https://www.hella.com/en/Newsroom/Press-Releases/2023-05-24-Steering-technology-of-the-future-HELLA-supplies-sensor-technology-for-all-electric-steer-by-wire-931/

## EPSサプライヤとしての次アクション

次にやることは、候補1+2の最小デモを作ることである。

1. 実在製品ではない仮想steering ECU構成を1つ置く
2. 診断アクセス、ソフト更新、SBOM、脆弱性、sensor input、communication、fail-safe stateを対象にする
3. 各対象について、脅威、要求、証拠、OEM説明文を1行にする
4. それを見て、汎用TARAではなくEPSサプライヤ向け成果物に見えるかを判定する

このデモが薄ければ、この方向も止める。
逆に、steering ECU固有の説明材料として見えるなら、次は有償探索候補として残せる。
