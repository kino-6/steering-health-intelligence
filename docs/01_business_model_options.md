# 01. Business Model Options

会話中で検討したビジネスモデル案を整理する。

## Option A: End-user Fault Warning

### Concept

ユーザに対して「EPS / ECUが故障しそうです」「点検してください」と通知する。

### Evaluation

これは弱い。

### Reasons

- ECUはメンテナンスフリー前提の商品である
- 誤警告が入庫・保証要求・不安につながる
- 操舵系は安全クリティカルで、ユーザ通知の責任が重い
- メーカーから見ると、メンテコストやクレームを増やす機能に見えやすい

### Conclusion

初期ターゲットにはしない。

---

## Option B: Fleet Predictive Maintenance

### Concept

物流・バス・タクシー・レンタカーなどのfleet向けに、EPS / ステアリング系の予兆診断を提供する。

### Evaluation

EPS単体では弱い。

### Reasons

- フリートにとってEPS故障は頻度が低い
- フリートが日常的に困るのは、タイヤ、バッテリ、ブレーキ、パワートレイン、燃費、稼働率など
- EPSは壊れた時の影響は大きいが、単独で月額課金を正当化するには頻度が低い
- 一般テレマティクスではEPS内部の深い診断値を取れないことが多い

### Conclusion

Vehicle Health Management の1項目としてはあり得るが、EPS単体サービスとしては弱い。

---

## Option C: OEM Market Quality Monitoring

### Concept

OEMが自社販売車両群を巨大fleetとして見て、操舵系の安全・品質リスクを内々に監視する。

### Evaluation

コンセプトとしては強いが、ECUサプライヤ単独では難しい。

### Reasons

- OEMはDTC、入庫、保証、苦情、OTA、車両仕様情報を持つ可能性がある
- EPS / ステアリング系は低頻度でも重大リスクになり得る
- リコール・サービスキャンペーン対象の絞り込みに価値がある
- ただし、これを実現するにはOEM側の市場データ・品質基盤が必要
- サプライヤ側から「OEM市場全体をRisk Triageできます」と言うのは背伸びしすぎ

### Conclusion

将来拡張としては有望。  
ただし、サプライヤ発の初期提案としては、OEMのRisk Triageに使える診断根拠を提供する形が現実的。

---

## Option D: OTA / ADAS Safety Monitoring

### Concept

OTA後やADAS作動時に、操舵系の異常傾向や可用性を監視する。

### Evaluation

面白いがOEM依存が強い。

### Reasons

- OTA履歴、配信対象、更新時期はOEM側情報
- ADAS作動状態や車両統合制御はOEMまたはシステム統合側に依存
- ECUサプライヤ側だけでは、全体可用性や市場影響を判断しにくい

### Conclusion

「将来的にOEM側データと組み合わせれば活用可能」と位置づける。  
初期提案の主役にはしない。

---

## Option E: Diagnostic Evidence Package

### Concept

操舵ECU内部の診断根拠を標準化し、市場不具合解析時の原因候補分類・初動解析・品質説明を支援する。

### Evaluation

現時点で最も現実的。

### Reasons

- ECUサプライヤが責任を持てる範囲に収まる
- DTCだけでは不足する内部状態を補完できる
- 返却品解析や不具合解析時に有用
- OEM / Tier1間の原因切り分けを早められる
- 将来的な市場傾向分析やRisk Triageの材料になる

### Conclusion

現時点の本命案。

---

## Option F: Development / HILS Quality AI

### Concept

市場投入前のHILS、ベンチ、実車評価ログ、不具合票を解析して品質リスクを見つける。

### Evaluation

技術的には現実的だが、当初の市場ビジネスモデルとは別物。

### Reasons

- データ入手性は高い
- すぐに価値を出しやすい
- ただし、Vehicle Health Management 市場というより開発品質AIである

### Conclusion

別プロジェクトとしては有望。  
本テーマでは補助的な検証手段として扱う。
