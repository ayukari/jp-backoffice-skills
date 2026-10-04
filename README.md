# jp-backoffice-skills

> 🚧 **開発中 (v0.1.0 準備中)** — スキルの追加・評価を進めています。

日本の事務作業向けの [Claude Code](https://code.claude.com) / Agent Skills 集です。

| スキル | できること |
|---|---|
| `invoice-jp` | インボイス制度（適格請求書）対応の請求書作成・点検。税率ごとに1回だけ端数処理する計算スクリプトと、既存請求書のチェッカー付き |
| `keigo-email` | 相手との関係と目的に合わせたビジネスメールの作成・敬語添削 |
| `ringi-jp` | 稟議書（社内決裁申請）の作成・添削。結論→費用→効果→比較→リスクの構成 |
| `nippo-jp` | 日報・週報の作成と、日報から週報への要約。メモや git log から下書き |
| `jp-tech-writing` | 日本語の技術文書（README・手順書・技術記事）の校正。文体混在・表記ゆれ・冗長表現を検出するスクリプト付き |
| `expense-ledger-jp` | 明細やレシートから勘定科目つき経費帳CSVを作成 |



## インストール

```bash
claude plugin marketplace add ayukari/jp-backoffice-skills
claude plugin install jp-backoffice-skills@jp-backoffice
```

## 注意

税務・法務の最終判断は、税理士・専門家や国税庁などの公式情報で確認してください。

## License

MIT

---

*English:* Agent Skills for Japanese back-office work (qualified invoices under Japan's invoice system, keigo business email, expense ledgers). Work in progress.
