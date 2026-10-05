#!/usr/bin/env python3
"""Lint Japanese business email text for common keigo mistakes.

Usage:
  python3 keigo_lint.py email.txt          # or pipe text on stdin
  python3 keigo_lint.py email.txt --json

Rules live in keigo_rules.json (id, pattern, suggest, why, level).
"させていただく" overuse is counted separately: 3 or more in one email is flagged.
"""
import json
import re
import sys
from pathlib import Path

RULES = json.loads((Path(__file__).parent / "keigo_rules.json").read_text(encoding="utf-8"))
SASETE_LIMIT = 3


def lint(text):
    findings = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for rule in RULES:
            for m in re.finditer(rule["pattern"], line):
                findings.append({"line": lineno, "match": m.group(), "rule": rule["id"], "level": rule["level"],
                                 "suggest": rule["suggest"], "why": rule["why"]})
    count = len(re.findall(r"させていただ", text))
    if count >= SASETE_LIMIT:
        findings.append({"line": None, "match": f"させていただく ×{count}", "rule": "sasete-overuse", "level": "info",
                         "suggest": "一部を「〜いたします」「〜します」に", "why": "多用すると回りくどく読みにくい"})
    return findings


def main():
    if "-h" in sys.argv or "--help" in sys.argv or (len(sys.argv) == 1 and sys.stdin.isatty()):
        # No file and nothing piped in: show usage instead of waiting on stdin.
        print(__doc__.strip())
        sys.exit(0 if len(sys.argv) > 1 else 2)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    text = open(args[0], encoding="utf-8").read() if args else sys.stdin.read()
    findings = lint(text)
    if "--json" in sys.argv:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        for f in findings:
            where = f"{f['line']}行目" if f["line"] else "全体"
            print(f"[{f['level']}] {where}: 「{f['match']}」→ {f['suggest']}（{f['why']}）")
        if not findings:
            print("指摘はありません")
    sys.exit(1 if any(f["level"] == "error" for f in findings) else 0)


if __name__ == "__main__":
    main()
