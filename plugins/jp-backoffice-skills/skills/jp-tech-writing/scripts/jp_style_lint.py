#!/usr/bin/env python3
"""Lint Japanese technical writing for common readability problems.

Usage:
  python3 jp_style_lint.py doc.md            # or pipe text on stdin
  python3 jp_style_lint.py doc.md --json

Checks:
  long-sentence   sentence longer than 100 characters
  many-commas     4 or more 「、」 in one sentence
  mixed-style     both です/ます and だ/である sentence endings in one document
  redundant       冗長表現 (することができる, という形, etc.)
  hyogen-yure     表記ゆれ (same word written two ways in one document)
  double-ga       the particle が appearing twice in one clause, before the first 「、」

Fenced code blocks and inline code are ignored.
"""
import json
import re
import sys

MAX_LEN = 100
MAX_COMMAS = 4

REDUNDANT = [
    (r"することができ(る|ます)", "できる／できます"),
    (r"することが可能", "できる"),
    (r"を行う|を行います", "〜する（例：設定を行う→設定する）"),
    (r"という(形|風|感じ)で", "（削れることが多い）"),
    (r"となっております", "です"),
    (r"させていただ", "します／いたします"),
    (r"のほう(が|を|は)", "（「ほう」を削れないか確認）"),
    (r"ことになります", "です／ます"),
    (r"一番最初|一番最後", "最初／最後"),
    (r"まず最初に", "まず／最初に"),
]

# Pairs of variants; if both forms appear, it is a 表記ゆれ.
YURE = [
    ("サーバー", "サーバ"), ("ユーザー", "ユーザ"), ("コンピューター", "コンピュータ"),
    ("インターフェース", "インタフェース"), ("出来る", "できる"), ("下さい", "ください"),
    ("事が", "ことが"), ("時に", "ときに"), ("全て", "すべて"), ("予め", "あらかじめ"),
    ("Github", "GitHub"), ("Javascript", "JavaScript"), ("Typescript", "TypeScript"),
]

DESU_MASU = re.compile(r"(です|ます|でした|ました|ません|でしょう)$")
DA_DEARU = re.compile(r"(である|だ|だった|ではない|であった)$")


def strip_code(text):
    text = re.sub(r"```.*?```", lambda m: "\n" * m.group().count("\n"), text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


def sentences(text):
    for lineno, line in enumerate(text.splitlines(), 1):
        body = line.strip()
        if not body or body.startswith(("#", "|", ">", "-", "*", "1.", "http")) and not body.endswith("。"):
            continue
        body = re.sub(r"^[-*]\s+|^\d+\.\s+", "", body)
        for s in re.split(r"(?<=[。！？])", body):
            s = s.strip()
            if s:
                yield lineno, s


def lint(text):
    text = strip_code(text)
    out = []
    styles = {"desu": [], "da": []}
    for lineno, s in sentences(text):
        core = s.rstrip("。！？」）)")
        if len(s) > MAX_LEN:
            out.append({"line": lineno, "rule": "long-sentence", "detail": f"{len(s)}文字", "text": s[:40] + "…"})
        if s.count("、") >= MAX_COMMAS:
            out.append({"line": lineno, "rule": "many-commas", "detail": f"読点{s.count('、')}個", "text": s[:40] + "…"})
        first_clause = re.sub(r"「[^」]*」", "", s).split("、")[0]
        if len(re.findall(r"[^\s]が", first_clause)) >= 2 and not re.search(r"ながら|ところが|だが|ですが|しかしが", first_clause):
            out.append({"line": lineno, "rule": "double-ga", "detail": "「が」が2回", "text": first_clause[:40]})
        if s.endswith("。"):
            if DESU_MASU.search(core):
                styles["desu"].append(lineno)
            elif DA_DEARU.search(core):
                styles["da"].append(lineno)
    if styles["desu"] and styles["da"]:
        minority = min(styles.items(), key=lambda kv: len(kv[1]))
        out.append({"line": minority[1][0], "rule": "mixed-style",
                    "detail": f"です・ます{len(styles['desu'])}文／だ・である{len(styles['da'])}文が混在（少ない方: {minority[1][:5]}行目）",
                    "text": ""})
    for lineno, line in enumerate(text.splitlines(), 1):
        for pat, sug in REDUNDANT:
            for m in re.finditer(pat, line):
                out.append({"line": lineno, "rule": "redundant", "detail": f"→ {sug}", "text": m.group()})
    for a, b in YURE:
        if a in text and b in text.replace(a, ""):
            out.append({"line": None, "rule": "hyogen-yure", "detail": f"「{a}」と「{b}」が混在", "text": ""})
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    text = open(args[0], encoding="utf-8").read() if args else sys.stdin.read()
    findings = lint(text)
    if "--json" in sys.argv:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        for f in findings:
            where = f"{f['line']}行目" if f["line"] else "全体"
            print(f"[{f['rule']}] {where}: {f['text']} {f['detail']}".rstrip())
        if not findings:
            print("指摘はありません")


if __name__ == "__main__":
    main()
