# 公開情報だけで次に探索する候補

## 結論

`Coverage Benchmark` は、対象EPSの内部資料を見ない限り、既存診断や既存評価との差分を示せない。
したがって、公開情報だけで次を探すなら、故障予測、追加ログ、RCA/8D資料作成からいったん離れる。

次に見るべきは、**公開されている規制・標準・業界動向そのものが、EPSサプライヤ側の作業を増やしている領域**である。

現時点で最も探索価値が高いのは、以下である。

> EPS / steering ECU 向けのサイバーセキュリティ・ソフトウェア更新・SBOM対応を、ステアリング固有の設計証拠に落とす商品。

これは「車両全体のサイバー対応を代行する」話ではない。
EPSサプライヤが持つECU、診断、ソフト更新、フェールセーフ、冗長化、サプライチェーン部品に対して、OEMや監査で説明できる材料を作る話である。

公開情報だけで需要を説明しやすい点が、これまでの故障予測・Evidence Pack・Coverage Benchmarkと違う。

## なぜ方向転換するか

これまでの探索で分かったことは次の通り。

- 市場ではEPSのassist loss、低速高操舵、警告灯+DTC、software/failsafeなどの痛みは繰り返し出ている
- しかし、そこから「対象EPSの診断が足りない」「追加ログを売れる」とは言えない
- 既存DTC、freeze frame、extended data、HILS、review会議体との差分確認には内部資料が必要になる
- 内部資料を使わない前提では、公開データ分析を増やしても事業判断は進まない

一方で、サイバーセキュリティ、ソフトウェア更新、SBOM、SOVD、steer-by-wireは、公開規制・公開標準・公開サプライヤ発表だけで「市場側から要求が増えている」ことを示しやすい。
そのため、次の探索対象として筋がよい。

## 候補1: EPS / steering ECU のサイバーセキュリティ設計証拠パック

市場需要:

車両はソフトウェア化・接続化しており、OEMは車両型式認可や監査に向けて、サイバーセキュリティ管理、脅威分析、リスク管理、サプライヤ管理の証拠を求められる。
UNECE R155は車両サイバーセキュリティ、R156はソフトウェア更新管理を扱う。
NHTSAも車両サイバーセキュリティのベストプラクティスを更新しており、ISO/SAE 21434は車両E/Eシステムのライフサイクル全体に対するサイバーセキュリティ工程を定義している。

未解決の痛み:

汎用のCSMS/TARAツールは存在する。
しかしEPS/steering ECUでは、診断サービス、ソフト更新、トルクセンサ、モータ制御、フェールセーフ、assist制限、冗長電源/通信など、ステアリング固有の安全影響を持つ。
この部分を一般論ではなく、ステアリングECUの設計レビューやOEM説明に使える形に落とす必要がある。

仮説:

EPSサプライヤ向けに、ステアリングECUの脅威分析、セキュリティ要求、更新時リスク、診断アクセス制御、検証証拠のひな形を作れば、規制・監査・OEM要求への対応工数を下げられる。

初期提供物:

- ステアリングECUの資産/攻撃面リスト
- UDS/SOVD診断アクセス、ソフト更新、DID/readout、security accessの脅威チェックリスト
- EPS機能安全への影響を含むTARAひな形
- OEMへ出すサプライヤ回答用の説明テンプレート
- サイバー要求とテスト証拠の対応表

EPSサプライヤとしてできること:

EPS ECUの機能、診断、更新、フェールセーフ、制御境界を知っているため、車両全体ではなくコンポーネント単位の証拠を作れる。
OEMの保証DBや市場故障データは不要で、公開標準とサプライヤ側の設計知識から初期デモが作れる。

言ってはいけないこと:

- R155/R156認証そのものを取れる
- 車両全体のサイバーリスクを閉じられる
- OEMのCSMS/SUMSを代替できる

Kill条件:

既存のサプライヤ内CSMS/TARA運用で、ステアリングECU固有の資産、脅威、要求、テスト証拠が既に十分に整備されているなら止める。
また、OEMが完全に指定した様式以外を受け付けないなら、独立商品としては弱い。

## 候補2: EPS ECU 向けSBOM / 脆弱性対応パック

市場需要:

Auto-ISACは2025年に自動車向けSBOMの情報レポートを公開している。
NHTSAもSBOMを使ったサイバーセキュリティ強化に触れており、CISAやNISTもSBOMをソフトウェアサプライチェーン管理の基礎として扱っている。

未解決の痛み:

SBOMは「部品表を出す」だけでは価値にならない。
EPS ECUでは、OS、RTOS、bootloader、暗号ライブラリ、診断スタック、通信スタック、コンパイラ/ツールチェーン由来部品などが、どの機能や安全影響に接続するかを説明する必要がある。

仮説:

EPSサプライヤ向けに、SBOMを作るだけでなく、脆弱性が出たときに「このEPS ECUで実際に影響があるか」「更新・診断・通信・フェールセーフのどこを見るか」を判断する仕組みにすると価値が出る。

初期提供物:

- steering ECU firmware向けSBOM項目テンプレート
- 部品/ライブラリ/ツールチェーンとEPS機能影響の対応表
- CVE triageの判断フロー
- OEM問い合わせ回答テンプレート
- SBOM更新履歴とソフトウェアリリースの対応表

EPSサプライヤとしてできること:

サプライヤECUに入るソフトウェア部品とリリース単位を知っているのはサプライヤ側である。
OEM側の車両データなしでも、部品表、脆弱性、影響有無、対応ステータスを説明できる。

言ってはいけないこと:

- SBOMがあれば安全になる
- CVE件数が少なければリスクが低い
- 汎用SBOMツールだけでOEM説明が完結する

Kill条件:

対象EPSが外部/OSS/third-party部品をほとんど使わず、既存の企業セキュリティ部門がSBOMと脆弱性回答を十分に運用しているなら、単独商品としては弱い。

## 候補3: SOVD / 次世代診断に向けたEPS診断コンテンツ設計

市場需要:

ASAM SOVDは、ソフトウェア化した車両に対する診断APIを定義し、HPCやclassic ECUの診断コンテンツへ一貫してアクセスすることを狙っている。
診断はハード故障の読み出しだけでなく、ソフトウェア問題や動的に変わる車両構成の解析へ広がっている。

未解決の痛み:

EPSサプライヤは、既存UDS/DTC/DIDをそのまま持つだけでは、次世代診断APIで何を見せるべきか、何を見せてはいけないか、どの権限で読ませるかを説明しにくい。

仮説:

EPS向けに、DTC、DID、freeze frame、extended data、software/calibration ID、assist/failsafe state、security accessを、SOVD時代の診断コンテンツとして整理するパックに価値がある。

初期提供物:

- 既存UDS項目からSOVD風リソースへの対応表
- steering ECUで公開すべき状態、制限すべき状態、OEM依存に置く状態の分類
- diagnostic securityとservice/readout権限の設計メモ
- ソフト更新後の確認項目テンプレート

EPSサプライヤとしてできること:

EPS ECUが持つ診断情報の意味と制約を知っているため、OEM診断基盤に載せる前のコンテンツ整理を作れる。

言ってはいけないこと:

- OEMの診断プラットフォームを所有できる
- SOVD対応だけで故障解析価値が出る
- 既存UDS/DTCの不足を公開情報だけで断定できる

Kill条件:

OEMが診断コンテンツを完全指定し、サプライヤ側で提案余地がないなら止める。
また、SOVD採用時期が遠く、既存UDS運用の改善にもつながらないなら優先度を下げる。

## 候補4: Steer-by-wire 移行に向けた安全・サイバー・冗長化の設計証拠

市場需要:

steer-by-wireは量産導入が進み始めている。
ZFは欧州市場での量産導入を発表し、Nexteerも2026年にsteer-by-wireの量産開始を発表している。
HELLAもsteer-by-wire向けセンサの量産受注を発表している。
steer-by-wireでは機械的な直結が消えるため、冗長センサ、冗長電源、通信、fail-operational、driver feedback、サイバーセキュリティがより重要になる。

未解決の痛み:

従来EPSの「assistが落ちてもmanual steerは残る」という前提から、steer-by-wireでは「電子制御で操舵可能性を維持する」前提へ変わる。
そのため、設計証拠、故障時状態、冗長系診断、ソフト更新時の安全確認、攻撃面の説明が重くなる。

仮説:

EPSサプライヤが、steer-by-wire移行前の開発チーム向けに、安全・サイバー・冗長化の最小設計証拠を整理するパックを作れば、従来EPSからの移行検討に使える。

初期提供物:

- steer-by-wire向けの冗長要素チェックリスト
- 故障時に維持すべき操舵可能性の説明テンプレート
- センサ/電源/通信/actuator/feedback motorの故障シナリオ表
- サイバー攻撃面と安全影響の対応表
- 従来EPSとの差分説明資料

EPSサプライヤとしてできること:

ステアリング制御、actuator、センサ、フェールセーフ、ASIL D相当の開発文脈を扱う立場にあるため、車両全体ではなくsteering system単位の証拠を作れる。

言ってはいけないこと:

- steer-by-wire安全性を公開情報だけで証明できる
- 特定OEMの量産設計にそのまま適用できる
- 規格認証やASIL認証を代行できる

Kill条件:

対象顧客がsteer-by-wireに近い開発テーマを持っていないなら短期商品にはならない。
また、公開情報だけでは一般論で止まり、対象アーキテクチャを見ないと進めない場合は、公開デモまでに留める。

## 候補5: 公開recall / ODI / TSBから作るEPSサプライヤ向け市場要求モニタ

市場需要:

NHTSAなどの公開資料には、EPS assist loss、警告灯、DTC、software/failsafe、MDPS/ECU hardware、steer-by-wire関連の社会的関心が継続的に出る。
サプライヤ側の営業、先行開発、品質、設計は、これをRFQ、設計レビュー、競合比較、規制対応の入口として使える可能性がある。

未解決の痛み:

ただし、これは単体では弱い。
「こんな事例がある」で終わると、過去に止めたMarket Pain Scenario Libraryと同じになる。

仮説:

公開市場モニタは、候補1-4の入力として使うなら価値がある。
つまり、サイバー、SBOM、SOVD、steer-by-wire設計証拠へつなぐための市場要求トリガとして位置づける。

初期提供物:

- monthly/quarterlyの公開recall/ODI/TSB update
- EPS pain familyの更新
- どの規制/標準/設計証拠に影響するかの注釈
- RFQ/設計レビューで使える質問文

EPSサプライヤとしてできること:

公開情報をサプライヤ内の先行開発・品質・営業に翻訳することはできる。
ただし、これ自体を主商品にはしない方がよい。

Kill条件:

候補1-4の具体成果物につながらず、公開事例の要約だけで終わるなら止める。

## 優先順位

| Rank | 候補 | 判断 | 理由 |
|---:|---|---|---|
| 1 | EPS / steering ECU サイバーセキュリティ設計証拠パック | Explore first | 公開規制・標準が需要を作っており、EPSサプライヤ固有の知識に落とせる |
| 2 | EPS ECU SBOM / 脆弱性対応パック | Explore first | 公開需要が強く、OEMデータなしでデモできる。ただし汎用ツールとの差分確認が必要 |
| 3 | SOVD / 次世代診断コンテンツ設計 | Explore second | EPS診断知識を使えるが、OEM診断基盤依存がある |
| 4 | Steer-by-wire安全・サイバー・冗長化設計証拠 | Watch / Explore selectively | 将来性は高いが、対象顧客がSbWに向かっていないと短期売上化しにくい |
| 5 | 公開市場要求モニタ | Use as input only | 単体商品は弱い。候補1-4の材料として使う |

## Chain-of-Verification

検証した問い:

1. この候補は市場需要から始まっているか。
2. 内部資料なしでも、需要と初期デモを作れるか。
3. EPSサプライヤが主語になれるか。
4. OEM領域を代替すると言っていないか。
5. 既存プレイヤーや既存業務の焼き直しにならないか。

修正した点:

- 故障予測、RUL、劣化兆候通知は戻さない
- `Coverage Benchmark` は内部資料がないと進めないため、今回の主候補から外す
- 公開recall/ODI/TSBモニタは単体商品ではなく、規制・標準対応商品の入力に下げる
- サイバー/ソフト更新/SBOM/SOVD/SbWは、車両全体ではなくsteering ECU / EPS supplier component boundaryに限定する

## 参照した公開情報

- UNECE, UN Regulation No.155 / No.156 overview and entry into force: https://unece.org/sustainable-development/press/three-landmark-un-vehicle-regulations-enter-force
- UNECE, UN Regulation No.156: https://unece.org/transport/documents/2021/03/standards/un-regulation-no-156-software-update-and-software-update
- NHTSA, Cybersecurity Best Practices for the Safety of Modern Vehicles, 2022: https://www.nhtsa.gov/document/cybersecurity-best-practices-safety-modern-vehicles-2022
- ISO, ISO/SAE 21434:2021 Road vehicles — Cybersecurity engineering: https://www.iso.org/cms/%20render/live/en/sites/isoorg/contents/data/standard/07/09/70918.html
- Auto-ISAC, SBOM Informational Report announcement, 2025: https://automotiveisac.com/press-news/auto-isac-issues-software-bill-of-materials-informational-report-nbsp
- NHTSA, Vehicle Cybersecurity / SBOM remarks: https://www.nhtsa.gov/speeches-presentations/sae-nhtsa-vehicle-cybersecurity-workshop-remarks
- CISA, SBOM FAQ: https://www.cisa.gov/resources-tools/resources/sbom-faq
- NIST, Software supply chain security guidance / SBOM: https://www.nist.gov/itl/executive-order-14028-improving-nations-cybersecurity/software-supply-chain-security-guidance-20
- ASAM, SOVD: https://www.asam.net/standards/detail/sovd/
- ZF, steer-by-wire European series production announcement: https://press.zf.com/press/en/releases/release_89553.html
- Nexteer, steer-by-wire series production announcement: https://www.nexteer.com/release/nexteer-puts-steer-by-wire-into-series-production/
- FORVIA HELLA, steer-by-wire sensor production orders: https://www.hella.com/en/Newsroom/Press-Releases/2023-05-24-Steering-technology-of-the-future-HELLA-supplies-sensor-technology-for-all-electric-steer-by-wire-931/

## EPSサプライヤとしての次アクション

次にやるなら、候補1を1つだけ具体化する。

公開情報だけで、以下を1ページに落とす。

> steering ECUの診断アクセス、ソフト更新、assist/failsafe state、calibration ID、security accessを対象に、脅威、要求、検証証拠、OEM説明文を対応づける。

これで、単なる市場調査ではなく、EPSサプライヤが実務で使える成果物になるかを見る。
