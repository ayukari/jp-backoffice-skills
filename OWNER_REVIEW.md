# Owner review before v0.1.0

What the repo owner (ayukari) should check before tagging v0.1.0 and sharing the repo publicly. It takes about 20–30 minutes.

## 1. Try it yourself (most important)
- [ ] Install it in your own Claude Code:
  ```bash
  claude plugin marketplace add ayukari/jp-backoffice-skills
  claude plugin install jp-backoffice-skills@jp-backoffice
  ```
- [ ] Ask for one real invoice ("請求書を作って…" with your own details) and check that it is correct.
- [ ] Ask for one email you would actually send and check that it sounds natural.
- [ ] Note anything that felt wrong, and tell Claude in the session.

## 2. Content you are responsible for
- [ ] Nothing in the skills claims to be tax or legal advice. They always point to a 税理士 or NTA sources.
- [ ] The example names (山田デザイン, 株式会社サンプル, `T1234567890123`) are clearly fictional.
- [ ] You are OK with your GitHub name (`ayukari`) as the author and copyright holder (LICENSE, plugin.json).

## 3. Before announcing
- [ ] Repo description and topics, set from GitHub → repo page → ⚙ About. Suggested:
  - Description: `日本の事務作業向け Claude Code スキル集（インボイス請求書・敬語メール・稟議書・日報・技術文書校正・経費帳）`
  - Topics: `claude-code`, `agent-skills`, `claude-code-plugin`, `japanese`, `invoice`, `keigo`
- [ ] Decide where you will share it yourself (e.g. your own X account, or the Zenn article Claude drafts on Day 4). Claude will not post anywhere for you.

## 4. Release
- [ ] Tell Claude "v0.1.0 OK". Claude then removes "unreleased" from CHANGELOG, tags `v0.1.0` and pushes. The GitHub Release page is created by you from the tag, or by Claude if you ask.
