# jp-backoffice-skills

> 🚧 **開発中 (v0.1.0 準備中)** — スキルの追加・評価を進めています。

日本の事務作業向けの [Claude Code](https://code.claude.com) / Agent Skills 集です。

| スキル | できること |
|---|---|
| `invoice-jp` | インボイス制度（適格請求書）対応の請求書作成・点検。税率ごとに1回の端数処理を行う計算スクリプト付き |
| `keigo-email` | 相手との関係と目的に合わせたビジネスメールの作成・敬語添削 |
| `ringi-jp` | 稟議書（社内決裁申請）の作成・添削。結論→費用→効果→比較→リスクの構成 |
| `expense-ledger-jp` | 明細やレシートから勘定科目つき経費帳CSVを作成 |

準備中：日報・週報（`nippo-jp`）、日本語技術文書の校正（`jp-tech-writing`）

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
