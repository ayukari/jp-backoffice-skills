# Changelog

## [Unreleased]

### Fixed
- `invoice-jp` checker: a tax mismatch is no longer always blamed on per-line rounding. It now says per-line rounding **or a calculation error**, since some mismatches (e.g. 999 yen at 10% shown as 98) fit no rounding method.

## [0.1.0] - 2026-10-05

### Added
- `invoice-jp`: qualified-invoice calculator (one rounding per tax rate), Markdown/HTML renderer with 取引年月日 or 取引期間, and a text invoice checker for the 6 required items.
- `keigo-email`: keigo linter (JSON rules) and 8 purpose templates.
- `ringi-jp`: 稟議書 structure, review mode, and a worked example.
- `nippo-jp`: daily and weekly report formats and a weekly summary mode.
- `jp-tech-writing`: style linter (mixed style, 表記ゆれ, preferred forms, redundant phrases, long sentences, double が).
- `expense-ledger-jp`: expense ledger CSV format, account title guide, and CSV parsing notes.
- 18 evals (3 per skill) and GitHub Actions CI for script tests.

### Notes
- Bundled scripts are referenced as `${CLAUDE_SKILL_DIR}/scripts/...` so they work from any working directory.
