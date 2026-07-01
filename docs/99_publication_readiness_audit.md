# Publication Readiness Audit

Date: 2026-07-01

## 結論

このRepoは、秘密情報の直接漏洩という観点では、公開しても大きな問題は見つからなかった。

ただし、公開すると次は見える。

1. EPSサプライヤ向け事業仮説、失敗判断、再開条件、調査過程
2. 公開企業名、公開データセット名、公開URLに基づく市場調査メモ
3. Git履歴上のcommit author名とメールアドレス
4. Codex / AGENTS / skill運用のルール

したがって、判断は次である。

> 事業仮説と思考過程を公開してよいなら、公開可能。秘密鍵、API token、`.env`、個人連絡先、非公開顧客資料の混入は今回のスキャンでは見つからなかった。

## 確認したこと

### Secrets

以下を検索した。

- API key
- token
- password
- bearer
- authorization
- private key
- `BEGIN RSA`
- `BEGIN OPENSSH`
- `BEGIN PRIVATE`
- `OPENAI_API_KEY`
- `DATABASE_URL`
- `github_pat_`
- `ghp_`
- `sk-proj`
- `AKIA`

結果:

- 実秘密値は見つからなかった
- `authorization`、`security access`、`token` は、Smartcar、Kaggle、診断security accessなどの一般説明として出ているだけだった
- Git履歴に対しても同じ検索を実施し、実秘密値は見つからなかった

### Env / Key Files

以下を検索した。

- `.env*`
- `*secret*`
- `*credential*`
- `*key*`
- `*.pem`
- `*.p12`
- `*.pfx`

結果:

- 該当ファイルは見つからなかった

### Personal Information

本文中のメールアドレス、電話番号、住所形式を検索した。

結果:

- Repo本文からメールアドレスや電話番号は見つからなかった
- Git履歴のauthorとして以下は見える
  - `kino <personal Gmail address>`
  - `kino-6 <67919233+kino-6@users.noreply.github.com>`

公開時に個人メールを見せたくない場合は、履歴書き換えまたは公開前に別Repoへsquash importする。

### Confidential / Internal Terms

以下のような語を検索した。

- `社外秘`
- `機密`
- `confidential`
- `internal only`
- `NDA`
- `非公開`
- `private`
- `proprietary`

結果:

- 実際の社外秘資料や非公開顧客資料らしい本文は見つからなかった
- `内部資料を使わない`、`非公開確認しない`、`公開情報だけ` というルール説明が多く出ている
- これはむしろ、非公開資料を使っていないことを示す文脈である

### Commercial Sensitivity

公開すると、秘密情報ではないが、次の戦略情報は見える。

- どの事業仮説を試したか
- どの仮説を外販困難と判断したか
- EPSサプライヤ視点の売れる / 売れない判断
- Kaggle / public proxy方向の最新本線
- LLM運用上の上位ルールと失敗補正

これは情報漏洩というより、事業上の見せ方の問題である。
この思考過程を公開してよいなら問題は小さい。
見せたくないなら、公開用READMEと公開用docsを別に切る方がよい。

### Copyright / Source Use

Repo内の調査は、公開URLや公開データセットへのリンク、短い要約、判断表が中心である。
今回の簡易監査では、記事全文や有料資料の丸写しらしい大きなファイルは見つからなかった。

ただし、全ファイルを著作権観点で逐語照合したわけではない。
公開前に安全側へ寄せるなら、長い引用がないかだけ追加確認する。

### Repository Size / Binary Risk

Repo size:

- 全体: 約6.9 MB
- `.git`: 約4.6 MB
- `data`: 約840 KB
- `docs`: 約1.1 MB
- `generated`: 約180 KB
- `scripts`: 約72 KB

大きなバイナリ、データダンプ、秘密ファイルの混入は見当たらない。

## 公開前に決めること

### そのまま公開してよい場合

以下を許容できるなら、そのまま公開してよい。

1. 事業仮説と検討過程が見える
2. Git履歴に個人Gmail authorが残る
3. AGENTS.mdにLLM運用ルールと事業判断ルールが見える
4. 失敗・撤回・補正のログも見える

### 公開前に整える場合

より見せ方を整えるなら、次を行う。

1. commit authorの個人メールを隠すため、履歴を書き換えるか、公開用Repoへsquash importする
2. `AGENTS.md` を公開用に短くするか、開発運用ルールを残すか決める
3. `docs/95` 以前の補正前判断が誤読されないよう、READMEの推奨読書順をさらに強める
4. 事業仮説を見せたくない場合は、`docs/archive` を非公開側に残し、公開Repoは成果物だけにする

## 今回の判定

公開可否:

> 条件付きで公開可能。

条件:

1. 事業仮説、失敗ログ、LLM運用ルールを公開してよい
2. Git履歴の個人メール表示を許容する、または公開前に履歴を整理する
3. 公開直前にもう一度、未コミットファイルも含めてsecret scanを実施する

今回のスキャン結果だけで見ると、公開を止めるほどの秘密情報混入は見つからない。
