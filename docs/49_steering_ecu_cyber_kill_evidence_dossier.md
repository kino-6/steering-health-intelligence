# Steering ECU Cyber / SBOM 方向のKill判断用証拠

## 結論

この方向は、**広い商品としてはKillしてよい**。

Killする対象は以下である。

- TARAを作る商品
- SBOMを作る商品
- CVE / vulnerability managementをする商品
- ISO/SAE 21434やUN R155/R156対応を支援する汎用商品
- TARA、SBOM、CVE、software updateを統合管理するツール

理由は単純で、ここは既存プレイヤーがすでに厚い。
ETAS、Ansys、Siemens、ThreatZなどが、同じ領域をすでにツール・サービスとして提供している。
EPSサプライヤが新しく外から持ち込むには、差別化が弱い。

ただし、完全Killではなく、**1つだけ狭い残し方**がある。

> 既存のCSMS、TARA、SBOM、CVE管理、診断仕様、software update資料、安全設計を、steering ECU固有のOEM問い合わせ回答へ翻訳する短期支援。

これは商品開発ではなく、最後の存在確認である。
この存在確認でも差分が見えなければ、この方向は完全Killでよい。

## 判断を分ける

| 対象 | 判断 | 理由 |
|---|---|---|
| 汎用TARA / attack-surface整理 | Kill | 既存ツール・既存サービスがある |
| SBOM生成 / SBOM管理 | Kill | 自動車向けSBOM管理やOEM/Tier-1交換まで既存プレイヤーがいる |
| CVE / vulnerability monitoring | Kill | 脆弱性管理、SBOM連携、compliance workflowが既存領域 |
| ISO/SAE 21434 / UN R155/R156対応支援 | Kill as standalone | 既存コンサル・ツールが多い |
| steering ECU固有のOEM回答翻訳 | Hold, one last check | 汎用成果物が診断、更新、assist/fail-safe説明に落ちていない場合だけ価値が残る |

## 市場需要はある

ここは否定しない。
車両サイバー、SBOM、ソフト更新、脆弱性管理の需要自体はある。

根拠:

- NHTSAの車両サイバーセキュリティBest Practicesは、車両メーカーだけでなく、車両電子システムやソフトウェアを設計・製造する組織、サプライヤを対象に含めている
- NHTSAは、ソフトウェア資産、サプライヤ提供ソフト、vendor-specific codeのinventory管理にも触れている
- ISO/SAE 21434は、車両E/Eシステムのサイバーセキュリティエンジニアリング標準である
- Auto-ISACは2025年に自動車向けSBOM情報レポートを出し、SBOMを透明性、組織連携、脆弱性管理の助けとして説明している
- NISTは、SBOMをソフトウェア部品の正式な記録とし、脆弱性の特定・修正を速める材料と説明している

したがって、「市場需要がない」からKillするのではない。
**需要はあるが、既存プレイヤーが強く、EPSサプライヤ向け新規商品として差分が弱い**からKill寄りである。

## Kill証拠: 既存プレイヤーが厚い

| 領域 | 公開証拠 | Killに効く理由 |
|---|---|---|
| TARA / attack surface | ETAS ESCRYPT CycurRISKは、ISO/SAE 21434とUN R155に沿ったTARA、attack surface、attack tree、damage scenario、再利用可能な知識、TARA serviceを提供している | TARA作成やattack-surface整理は既に商品化済み |
| TARA + SBOM + vulnerability | Ansys Medini Cybersecurity SEは、自動TARA、vulnerability management、SBOM、ISO/SAE 21434 compliance workflow、HW/SW BOMとTARA modelのlinkageを訴求している | 前回案の「SBOMを機能影響へ接続する」方向も既存ツールに近い |
| SBOM / compliance | Siemens Sigridは、自動車向けにSBOM管理、静的解析、Polarion連携、ISO/SAE 21434、UN R155/R156対応を訴求している | SBOM生成・管理・規制対応の横断は既に汎用ツール化されている |
| SBOM exchange / CVE monitoring | ThreatZ / Uraeusは、TARA、SBOM、CVE monitoring、OEM/Tier-1 SBOM exchange、R156 update traceability、Supplier Portalを訴求している | OEM/Tier-1間のSBOM交換やCVE impactも既存商品がある |

ここまで揃うと、`Steering ECU Software / Cyber Evidence Pack` を広く売るのは危ない。
名前をEPS向けにしても、中身がTARA/SBOM/CVE管理なら既存商品の言い換えになる。

## まだ残るかもしれない狭い隙間

残る可能性があるのは、ツールではなく「翻訳」である。

既存ツールは、TARA、SBOM、CVE、compliance workflowを持っている。
しかし、実際のOEM問い合わせでは、以下のような部品固有の回答が必要になる可能性がある。

| OEMの問い | 既存ツールだけでは足りないかもしれない点 | EPSサプライヤが答える余地 |
|---|---|---|
| このCVEはEPSに影響するか | SBOM上は部品が見えても、EPSの診断・更新・assist stateへの影響が一目で分からない場合がある | bootloader、diagnostic stack、CAN stack、software/calibration ID、assist/fail-safe stateへ接続する |
| diagnostic securityは安全か | TARA上のthreatだけでは、どのroutine/DID/sessionが安全影響を持つか分かりにくい場合がある | 診断serviceを許可操作、禁止操作、安全影響、negative testへ分ける |
| update後にEPSの状態をどう確認するか | SUMSやupdate flowはあっても、steering ECUのpost-update state確認が別資料になっている場合がある | software/calibration ID、post-update check、fail-safe stateを1枚にする |
| cyber異常時にEPSはどう振る舞うか | cyber caseとsafety caseが分断している場合がある | assist limitation、warning、limp-home/manual steer前提へ接続する |

ただし、これも「あり得る」だけである。
公開情報だけでは、この隙間が本当に対象EPSサプライヤにあるか分からない。

## Kill判断のための最小証拠集め

次の5項目だけ確認すればよい。
中身の詳細資料は不要で、存在確認だけで足りる。

| ID | 確認すること | Yesなら | Noなら |
|---|---|---|---|
| KQ1 | steering ECU固有のOEM cyber/SBOM/CVE問い合わせが実際に来ているか | 残余価値の可能性あり | Kill寄り |
| KQ2 | 既存CVE回答にEPS機能影響、release ID、software/calibration IDが入っているか | Kill寄り | 残余価値の可能性あり |
| KQ3 | 診断security資料にroutine/DID/sessionの安全影響と禁止操作が入っているか | Kill寄り | 残余価値の可能性あり |
| KQ4 | cyber abnormal conditionとassist/fail-safe stateが紐づく表があるか | Kill寄り | 残余価値の可能性あり |
| KQ5 | OEM回答用の1枚資料、またはRFQ/監査回答templateが既にあるか | Kill寄り | 残余価値の可能性あり |

判断:

- KQ1がNoなら、そもそも需要トリガが弱いのでKill
- KQ2-KQ5のうち3つ以上がYesなら、既存業務で足りている可能性が高くKill
- KQ2-KQ5のうち2つ以上がNoで、かつKQ1がYesなら、短期回答支援だけ残す

## 現時点の推奨

公開証拠だけで判断するなら、以下。

> 汎用商品としてはKill。
> steering ECU固有のOEM問い合わせ回答支援としてだけ、最後の5項目確認を許す。
> その確認で明確な不足が見えなければ完全Kill。

つまり、開発や営業資料作成には進まない。
次にやるのは、商品化ではなくKill確認である。

## 参照ソース

- NHTSA, Cybersecurity Best Practices for the Safety of Modern Vehicles, 2022: https://www.nhtsa.gov/document/cybersecurity-best-practices-safety-modern-vehicles-2022
- ISO, ISO/SAE 21434:2021 Road vehicles — Cybersecurity engineering: https://www.iso.org/standard/70918.html
- Auto-ISAC, SBOM Informational Report announcement, 2025: https://automotiveisac.com/press-news/auto-isac-issues-software-bill-of-materials-informational-report-nbsp
- NIST, Software Security in Supply Chains: SBOM: https://www.nist.gov/itl/executive-order-14028-improving-nations-cybersecurity/software-supply-chain-security-guidance-20
- ETAS ESCRYPT CycurRISK: https://www.etas.com/ww/en/products-services/cybersecurity-products/escrypt-cycurrisk/
- Ansys Medini Cybersecurity SE: https://www.ansys.com/products/safety-analysis/ansys-medini-analyze-for-cybersecurity
- Siemens Sigrid Compliance & Cybersecurity for Automotive: https://www.siemens.com/en-us/products/sig-software-improvement-group-sigrid-compliance-cybersecurity-for-automotive/
- ThreatZ Automotive SBOM Management: https://uraeus.io/automotive-sbom/
