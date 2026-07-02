# SPD002 One-Case Diagnostic Reading Order

## 結論

SPD002は、最初の実証demoとして作る価値がある。

ただし、価値は「低/高電圧または過温度からEPS交換時期を予測すること」ではない。
価値は、reduced assistが出たときに、DTCだけでEPS内部故障へ短絡せず、電圧、温度、assist mode、key cycle、再発、repair feedback requirementをどの順番で読むべきかを1枚にできるかである。

今回の1ケース整理では、既存service manualの「電源と温度を確認」の言い換えで終わらせないために、8つの読み順へ分けた。

1. event summary
2. DTC status
3. voltage context
4. temperature context
5. assist mode and limit state
6. key cycle and recurrence
7. repair feedback requirement
8. final explanation

一定の結論としては、SPD002は **Proceed to demo** である。
ただし、本命候補ではなく、固定スコープassessmentが既存資料の要約を超えるかを試す実証用である。

詳細表は [data/steering_predictive_diagnostics_spd002_one_case_reading_order.tsv](../data/steering_predictive_diagnostics_spd002_one_case_reading_order.tsv) に置く。

## 何を判断しているか

判断しているのは、低/高電圧または過温度によるreduced assistの1ケースについて、EPSサプライヤが診断読み順と説明境界を作れるかである。

ここでいう1ケースは、特定実車のRCAではない。
「reduced assistが出たとき、どの情報をどの順に読むべきか」を示すsampleである。

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

この文書では、Hold / Stop境界を明示するため、次を確認する。

- 市場需要は、reduced assist eventをEPS内部故障と短絡せず、診断、service、顧客説明、品質feedbackの行動を決めたいことである
- Boschの `predictive diagnostics / predictive maintenance / vehicle health` は正面から扱う
- EPS交換時期、RUL、安全保証、root cause、保証費削減へ戻さない
- 電圧・温度・assist modeを、原因断定ではなく診断読み順と説明境界に使う
- repair feedbackがないことは、交換時期や原因断定へ進めない境界として扱う
- EPSサプライヤとしての手札を、assist limitの意味、DTC/freeze frame/extended data、説明境界、feedback requirementへ限定する

## Market Demand

reduced assistが出ると、service、顧客技術説明、品質改善では次を早く決めたい。

1. EPSを疑う前に、電源や温度contextをどこまで読むべきか
2. DTCがcurrentかhistoryかをどう解釈するか
3. 一時的eventか、key cycleをまたぐ再発か
4. 冷却や電源確認後に復帰したか
5. 交換判断や品質feedbackに必要なrepair feedbackは何か

この需要に対して、EPSサプライヤは診断読み順を作れる可能性がある。

## Unresolved Pain

既存service manualやDTC表は、電源、温度、DTC説明を個別に書くことはできる。
しかし、DTC、電圧、温度、assist mode、key cycle、repair feedbackをどの順番で読むべきかが弱いと、EPS内部故障、電源context、熱保護、一時event、再発patternが混ざる。

SPD002のdemoは、この混ざりを減らすための読み順sampleである。

## Hypothesis

低/高電圧または過温度によるreduced assistについて、event summaryからfinal explanationまでを1枚に整理できれば、診断企画、service / aftermarket、顧客技術説明へ転記できる。

この仮説は、交換時期予測ではない。
価値は、EPS交換判断の前に読むべきcontextと、言ってはいけないことを明確にすることである。

## Assumed Case

想定case:

> 走行中または低速取り回し中にSteering Assist Reduced相当の表示が出た。DTCはhistoryまたはcurrentとして残る可能性がある。event近傍で電圧dipまたは過温度に近い状態があった可能性がある。入庫時には復帰しているかもしれない。

このcaseで、EPSサプライヤは原因断定をしない。
見るのは、読み順と説明境界である。

## Diagnostic Reading Order

### 1. Event Summary

最初に、何が起きたかを固定する。

読むもの:

- warning / message
- reduced assist flag
- assist mode
- key cycle
- timestamp
- vehicle state

判断:

- warning有無だけでEPS交換へ進まない
- assist availability eventとして扱う

### 2. DTC Status

次に、DTCがcurrentかhistoryか、関連DTCがあるかを見る。

読むもの:

- EPS DTC
- current / history status
- aging
- occurrence counter
- related power / thermal / communication DTC

判断:

- DTCは入口であり、原因断定ではない
- DTC code descriptionの転記で終わらせない

### 3. Voltage Context

電源contextを読む。

読むもの:

- ECU supply voltage
- DC bus voltage
- min / max voltage
- voltage dip duration
- reset counter
- key cycle

判断:

- voltage dipやnear-resetがあれば、EPS component judgment前に電源系確認が必要
- ただし、電源が原因、EPSは問題なし、とは断定しない

### 4. Temperature Context

温度contextを読む。

読むもの:

- motor temperature
- inverter temperature
- ECU temperature
- estimated winding temperature
- thermal margin
- over-temperature DTC
- ambient proxy

判断:

- thermal protectionか、異常温度上昇か、復帰確認が必要かを分ける
- 温度履歴だけで寿命や交換時期を言わない

### 5. Assist Mode and Limit State

操舵側の制限状態を読む。

読むもの:

- assist mode
- limit state
- derating reason
- command / actual assist proxy
- fallback state

判断:

- 電圧/温度contextとassist stateを対応づける
- assist limitがあるだけで故障確定とは言わない

### 6. Key Cycle and Recurrence

一回限りか、再発かを見る。

読むもの:

- key cycle count
- occurrence counter
- recurrence interval
- current / history transition
- clear history

判断:

- 一時eventと再発patternを分ける
- 再発があるだけで交換時期が近いとは言わない

### 7. Repair Feedback Requirement

何がないと次に進めないかを明示する。

必要なfeedback:

- power system repair result
- cooling / recovery result
- replacement result
- no-trouble-found
- recurrence after repair

判断:

- repair feedbackなしでは、maintenance forecast、root cause、交換時期へ進めない

### 8. Final Explanation

最後に、service / 顧客 / 品質へ転記できる言い方にする。

言ってよいこと:

> reduced assist eventは、DTCだけでなく、電源・温度context、assist mode、key cycle、再発有無、repair feedback requirementを合わせて読む必要がある。

まだ言ってはいけないこと:

> このeventからEPSのRUL、交換日、安全保証、root causeが分かる。

## Proceed / Hold / Stop

Proceed条件:

- DTC単体よりも、電圧、温度、assist mode、key cycle、repair feedback requirementを読む順番が具体化する
- 診断企画、service / aftermarket、顧客技術説明の少なくとも2つに転記できる
- 交換時期予測ではなく、診断読み順として価値が残る

Hold条件:

- 既存service manualの「電源と温度を確認」の言い換えに留まる
- 電圧、温度、assist modeのどれかが診断情報に残らない
- 説明が一般免責文だけになる

Stop境界:

- 電圧、温度、assist modeが残らず、説明境界も作れない
- RUL、交換日、安全保証を言わないと価値説明できない

## Required Conclusion Fields

| Field | Content |
|---|---|
| Market demand | reduced assist eventをEPS内部故障と短絡せず、診断、service、顧客説明、品質feedbackの行動を決めたい |
| Unresolved pain | DTC、電圧、温度、assist mode、key cycle、repair feedbackの読む順番が弱いと、原因断定や誤交換に寄る |
| Hypothesis | 1ケースの診断読み順を作れば、既存DTC表やservice manualを超える説明境界が作れる |
| Solution / artifact | one-case diagnostic reading order |
| Buyer / user | 診断企画、service / aftermarket、顧客技術説明 |
| Why EPS supplier can play | assist limit、reduced assist、DTC/freeze frame/extended dataの意味を説明できる |
| Proceed condition | 読む順番が具体化し、2部署以上に転記できる |
| Hold condition | 「電源と温度を確認」の言い換え、または説明が一般論に留まる |
| Stop / Kill boundary | 電圧、温度、assist modeが残らず、説明境界も作れない |
| What not to claim | RUL、交換日、安全保証、root cause、保証費削減 |
| Next action | SPD008と比較し、どちらを本線候補にするか判断する |
| Confidence | Medium-High |

## Deepened Weak Points

### 既存service manualとの差分

差分は、単に「電源と温度を確認」と書くことではない。
event summary、DTC status、voltage、temperature、assist mode、key cycle、repair feedback requirementを、読む順番としてつなげることにある。

この順番が作れないなら、SPD002はHoldでよい。

### 診断情報に残る項目

SPD002は、電圧、温度、assist modeが診断情報に残らない場合に弱い。
その場合、service noteや顧客説明に転記できる情報が薄くなる。

### Service Noteへの転記

service noteへ転記できる最低条件は、次である。

1. DTC statusをcurrent/historyで分ける
2. voltage dipまたはnear-reset contextを見る
3. thermal marginまたはover-temp contextを見る
4. assist mode / limit stateを見る
5. key cycle recurrenceを見る
6. repair feedback requirementを返す

### 交換時期予測へ戻らない境界

SPD002で言えるのは、読み順と説明境界である。
電圧、温度、reduced assist履歴だけでは、RUL、交換日、安全保証、root causeは言えない。

## EPSサプライヤとしての言い方

言ってよいこと:

> reduced assist eventでは、DTCだけでなく、電源・温度context、assist mode、key cycle、repair feedback requirementを順番に読む必要がある。EPSサプライヤは、この読み順と説明境界を定義できる。

まだ言ってはいけないこと:

> reduced assist eventからEPS交換時期、RUL、安全保証、root cause、保証費削減が分かる。
