# 18. Market Research: Customer Pain and Buyer Reality

## Purpose

前回までの議論で、`EPS Health Intelligence` や `Embedded Evidence` は技術的にはあり得るが、誰が明確に嬉しいのかが弱いことが分かった。

そのため、今回は市場で実際に予算が付きそうな痛みを調べ直した。

## Short Conclusion

現時点の結論:

> 市場が明確に買っているのは、単体のECU health indicatorではなく、warranty analytics、No Trouble Found削減、supplier quality、8D / RCA、supplier recovery、return-part analysisのワークフローである。

したがって、EPS / ECU証跡を主商品として売るのはまだ弱い。

より現実的には、以下の位置づけがよい。

> EPS / ECU embedded evidenceは、warranty / supplier quality / NTF / 8D root cause analysisを支える証拠部品である。

## What Buyers Appear to Pay For

### 1. Warranty analytics and early warning

AWM、Ubiquiti、Consline CIMS、Nihilentなどは、保証データ、修理データ、部品返却、サービス、DTC、ディーラーナラティブを集約して、保証費・市場品質・早期警告・root cause analysisに使う文脈を打ち出している。

ここでの買い手:

- OEM warranty
- supplier warranty / recovery
- market quality
- product quality
- supplier quality

痛み:

- データが散在している
- NTFが多い
- 原因解析に時間がかかる
- サプライヤ責任分界やrecoveryが難しい
- 保証費の増加要因を早く知りたい

Implication:

ECU証跡は、この市場でいう「vehicle diagnostics / part intelligence / returned part evidence」の一部として価値がある。
単体で売るより、warranty analytics / supplier quality workflowに接続する方が筋が良い。

### 2. No Trouble Found and returned part evidence

AIAGやCLEPA系の資料では、No Trouble Foundや保証部品解析、タイムリーな診断データ、サプライヤへの情報共有が重要課題として出てくる。

痛み:

- 返却品が正常に見える
- 車両側で何が起きたか分からない
- in-vehicle diagnostic systemやpart intelligenceが不十分
- サプライヤがroot cause analysisするためのデータが足りない

Implication:

この文脈では、EPS embedded evidenceはかなり自然。
ただし、価値は「劣化予測」ではなく、NTF / returned part / warranty investigationの証拠補強である。

### 3. Supplier quality / SCAR / 8D / CAPA

Supplios、Rcalls、Lunatec、8D支援サービス、CAPA Engineなどは、supplier quality、8D、SCAR、root cause、corrective action、effectiveness verificationを支援している。

痛み:

- 8DやSCAR対応が重い
- root causeが弱いと顧客に通らない
- evidenceが不足する
- corrective actionの妥当性を説明しにくい
- supplier chargeback / penalty / recoveryが絡む

Implication:

EPS / ECU証跡は、8D / SCAR / CAPAのD4 root cause analysisやevidence packageに入る材料として価値がある。
つまり「ECU health商品」ではなく、「supplier quality evidence generator」として再配置できる。

### 4. Remote diagnostics / connected vehicle platforms

Sibros、Excelfore、Bytebeam、Carota、ElectRay、ACTIA、Upstreamなどは、remote diagnostics、OTA、vehicle data collection、early detection、component behavior monitoringを打ち出している。

痛み:

- 車両からデータを集めたい
- DTCやtelemetryから不具合を早期検出したい
- campaignやquality issueを早く検知したい
- cloud側でroot causeやfleet trendを見たい

Implication:

ここは将来の出口としては大きいが、OEM platform依存が強い。
ECUサプライヤ起点では、まずplatformに載せる「良いhealth payload / evidence payload」を作る立場が現実的。

## Reframed Business Direction

これまでの案を、市場調査後に並べ替える。

### Weak as a standalone business

- EPS劣化兆候通知
- EPS個車故障予測
- EPS単体VHM service
- 開発用外付けモニタ代替
- ECU内stress counter単体販売

### Stronger as evidence ingredient

- Returned part evidence payload
- NTF reduction evidence
- Warranty investigation evidence
- Supplier quality / 8D evidence package
- Diagnostic data payload for warranty analytics

### Best current framing

> EPS Embedded Evidence Package for Warranty / Supplier Quality Investigation

またはさらに一般化して:

> ECU Embedded Evidence for Supplier Quality and Warranty Analytics

ただし、ユーザ前提がEPSサプライヤであるなら、まずは以下が自然。

> EPS Embedded Evidence Package

One-line:

> EPS ECUに、DTCだけでは不足する最小限の使用・制御・電源・熱・一時異常証跡を残し、NTF、返却品解析、OEM説明、8D / root cause analysisを支援する。

## Who Is Happy?

最も明確に嬉しい人:

| Role | Why they care |
|---|---|
| EPS supplier warranty / quality team | 返却品やNTFで説明材料が増える |
| EPS supplier customer quality / OEM response team | OEM向け8D / RCA / 品質説明に使える |
| EPS diagnostic engineering | 量産診断仕様の説明力を上げられる |
| OEM warranty / market quality | サプライヤからより良い証拠付き回答が来る |
| supplier recovery / chargeback teams | 証拠の質が上がる可能性がある |

弱い相手:

| Role | Why weak |
|---|---|
| EPS development team | 外付け計測やベンチログで足りる可能性が高い |
| gear / rack design team | ECU信号だけでは要因分離が難しい |
| end user | 通知責任が重い |
| fleet operator | EPS単体の頻度価値が低い |

## Revised Recommendation

次のステップは、`health indicator` の技術案をさらに増やすことではない。

先に以下を確認すべき。

1. EPSサプライヤの品質・保証・OEM対応部門は、NTFや返却品解析で何に困っているか
2. OEMから求められる8D / RCA / warranty reportに、どんな証拠が足りないか
3. DTC / Freeze Frame / Extended Data / NVMで、どこまで補えるか
4. その証拠に対して、NREや診断仕様改善として予算が付くか

技術デモをするなら、開発A/B比較ではなく、以下がよい。

> DTCだけの返却品解析 vs Embedded Evidenceありの返却品解析

Demo scenario:

```text
input:
  DTC snapshot
  low voltage count
  assist limitation count
  thermal derating count
  current tracking warning count
  latest event snapshot

output:
  evidence summary
  likely investigation path
  missing data
  8D / RCA evidence paragraph
```

## Source Notes

- AIAG warranty materials explicitly identify NTF and timelier diagnostic data for supplier root cause analysis as important issues.
- AWM positions warranty analytics around field claims, returned parts, NTF investigation, dealer narratives, and vehicle diagnostics.
- Ubiquiti positions automotive quality analytics around repair, sensor, service, warranty, and part return records.
- Consline CIMS frames warranty/recourse cases as fragmented data that can become strategic product-quality knowledge.
- Supplier quality tools such as Supplios, Rcalls, Lunatec, and CAPA/8D support products show that buyers pay for root cause, evidence, corrective action, and supplier response workflows.
- Remote diagnostics vendors show a future channel, but OEM platform dependence remains high.
