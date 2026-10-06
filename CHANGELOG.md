# Changelog

## [0.2.0] - 2026-10-06

### Added
- Evals as `claude plugin eval` cases in `plugins/jp-backoffice-skills/evals/` (21 cases, one per prompt in `evals/evals.json`). See `evals/README.md`; use `--judge-model sonnet` for the Japanese checklists.
- New skill `houki-lookup`: fetch Japanese law articles from the official e-Gov 法令API v2 and quote them with source (law number, enforcement date, URL). Accepts 30 / 第30条 / 57の4 / 第五十七条の四, prefers an exact title match, and never fills in text from memory when a lookup fails (exit 1). Stdlib only; 6 tests run against recorded API responses; 2 evals.
- `invoice-jp`: 源泉徴収 (withholding) for fee lines marked `"withholding": true` (10.21% up to 1,000,000 yen, 20.42% above, rounded down) and 立替金 (reimbursements, outside consumption tax). The calculator returns `withholding_tax`, `reimbursements_total` and `amount_due`, and the renderer shows a breakdown. Whether withholding applies is left to the user. 10 new unit tests and 1 new eval (invoice-04-withholding).

## [0.1.1] - 2026-10-06

### Fixed
- `invoice-jp` checker: when the tax doesn't match, it now reads the item lines and names the cause: **per-line rounding** (it matches the per-line total) or a **calculation error** (no rounding method fits). Adds `tax_if_rounded_per_line` and `cause` to each check.
- All bundled scripts: `--help` / `-h` prints usage, and running with no file and no piped input prints usage (exit 2) instead of waiting on stdin.
- `jp-tech-writing` linter: 時に / 事が / 出来 are no longer flagged inside ordinary compound words (同時に, 実行時に, 仕事が, 記事が, 出来事, 出来高).

## [0.1.0] - 2026-10-05

### Added
- `invoice-jp`: qualified-invoice calculator (one rounding per tax rate), Markdown/HTML renderer with 取引年月日 or 取引期間, and a text invoice checker for the 6 required items. 10 new unit tests and 1 new eval (invoice-04-withholding).
- `keigo-email`: keigo linter (JSON rules) and 8 purpose templates.
- `ringi-jp`: 稟議書 structure, review mode, and a worked example.
- `nippo-jp`: daily and weekly report formats and a weekly summary mode.
- `jp-tech-writing`: style linter (mixed style, 表記ゆれ, preferred forms, redundant phrases, long sentences, double が).
- `expense-ledger-jp`: expense ledger CSV format, account title guide, and CSV parsing notes.
- 18 evals (3 per skill) and GitHub Actions CI for script tests.

### Notes
- Bundled scripts are referenced as `${CLAUDE_SKILL_DIR}/scripts/...` so they work from any working directory.
