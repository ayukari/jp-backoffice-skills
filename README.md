# jp-backoffice-skills

[![test](https://github.com/ayukari/jp-backoffice-skills/actions/workflows/test.yml/badge.svg)](https://github.com/ayukari/jp-backoffice-skills/actions/workflows/test.yml)

日本の事務作業向けの [Claude Code](https://code.claude.com) プラグイン（Agent Skills 集）です。
インボイス対応の請求書・敬語メール・稟議書・日報・技術文書の校正・経費帳づくりを、Claude に日本の実務の作法どおりに手伝わせます。

## 入っているスキル

| スキル | できること | スクリプト |
|---|---|---|
| `invoice-jp` | インボイス制度（適格請求書）対応の請求書を作成・点検。6つの必須記載事項をチェックし、消費税は税率ごとに1回だけ端数処理 | 計算・請求書出力（Markdown/HTML）・既存請求書チェッカー |
| `keigo-email` | 相手との関係と目的に合わせたビジネスメールの作成・敬語添削。依頼／催促／お詫びなど8種のテンプレート | 敬語チェッカー（二重敬語・謙譲語の誤用など） |
| `ringi-jp` | 稟議書（社内決裁申請）の作成・添削。結論→費用→効果→比較→リスクの構成 | — |
| `nippo-jp` | 日報・週報の作成と、日報から週報への要約。メモや git log から下書き | — |
| `jp-tech-writing` | README・手順書・技術記事の校正 | 文体混在・表記ゆれ・冗長表現・長文の検出 |
| `expense-ledger-jp` | 明細やレシートから勘定科目つき経費帳CSVを作成。家事按分は勝手に決めず確認 | — |
| `houki-lookup` | 法令の条文を e-Gov 法令API（公式データ）から取得し、原文を引用して説明。取得できなければ記憶で補わない | 法令検索・条文取得（項・号つきテキスト、出典つき） |
| `gijiroku-jp` | 会議メモや文字起こしから、決定事項とToDo（担当・期限）が先に分かる議事録を作成・点検 | ToDo表チェッカー（担当・期限の抜け、「早めに」などのあいまいな期限） |

## インストール

```bash
claude plugin marketplace add ayukari/jp-backoffice-skills
claude plugin install jp-backoffice-skills@jp-backoffice
```

インストール後は、Claude Code にふつうに頼むだけで該当スキルが使われます。

```
山田デザイン（登録番号T1234567890123）から株式会社サンプルへの請求書を作って。
10/1納品、Webデザイン一式10万円（税抜）。支払期限10/31。
```

```
取引先の佐藤さんに、9/30締切だった見積もりの返事を催促するメールを書いて。角が立たないように。
```

## 品質

- スクリプトは単体テスト付きで、push ごとに GitHub Actions で実行しています（5スキル・51件）。
- `evals/` に、スキルごとの評価プロンプト（24件）と期待される振る舞いを置いています。結果は `evals/results/` にあります。同じ24件を `claude plugin eval` でも実行できます（`evals/README.md`）。

## 注意

- 税務・法務の最終判断は、税理士などの専門家や国税庁の公式情報で確認してください。スキルは判断が分かれる点を【要確認】として残します。
- 入力にない事実（金額・日付・按分率など）を推測で埋めないように作っています。

## License

MIT

---

## English

Claude Code plugin with Agent Skills for Japanese back-office work:

| Skill | Purpose |
|---|---|
| `invoice-jp` | Qualified invoices under Japan's invoice system: calculator, renderer, and checker |
| `keigo-email` | Business email in the correct keigo, with templates and a linter |
| `ringi-jp` | Internal approval requests (ringi) |
| `nippo-jp` | Daily and weekly reports |
| `jp-tech-writing` | Japanese technical writing proofreading, with a linter |
| `expense-ledger-jp` | Expense ledger CSV for sole proprietors |
| `houki-lookup` | Japanese law articles from the official e-Gov Law API, quoted with source |
| `gijiroku-jp` | Meeting minutes with decisions and owner/deadline ToDos, with a checker |

Install with `claude plugin marketplace add ayukari/jp-backoffice-skills`, then `claude plugin install jp-backoffice-skills@jp-backoffice`.
