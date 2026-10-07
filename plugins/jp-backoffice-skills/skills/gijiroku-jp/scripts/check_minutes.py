#!/usr/bin/env python3
"""Check the ToDo table of Japanese meeting minutes (議事録).

Usage:
  python3 check_minutes.py minutes.md        # or pipe text on stdin
  python3 check_minutes.py minutes.md --json

Finds the Markdown table under a 「ToDo」/「アクション」/「宿題」 heading and flags
rows whose owner (担当) or deadline (期限) is empty, vague (早めに, なるべく, 近日中,
来週中, 適宜, 随時…) or not a date. 【要確認】 counts as acknowledged, not as an error.
Exit code 1 when there are findings.
"""
import json
import re
import sys

HEADING = re.compile(r"^#{1,6}\s*(ToDo|TODO|アクション(アイテム)?|宿題|タスク)")
VAGUE = re.compile(r"早め|なるべく|近日|今週中|来週中|今月中|来月中|適宜|随時|いずれ|できれば|ASAP|asap|未定")
DATE = re.compile(r"\d{1,4}\s*[/／\-.年]\s*\d{1,2}(\s*[/／\-.月]\s*\d{1,2})?|\d{1,2}\s*月\s*\d{1,2}\s*日")
PENDING = "【要確認】"


def find_todo_table(lines):
    """Return (header cells, [(line_no, cells)]) of the first table after a ToDo heading."""
    in_section, header, rows = False, None, []
    for no, line in enumerate(lines, 1):
        if line.startswith("#"):
            if header:
                break
            in_section = bool(HEADING.match(line))
            continue
        if not in_section or not line.strip().startswith("|"):
            if header and rows:
                break
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = cells
        elif not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            rows.append((no, cells))
    return header, rows


def col(header, *names):
    for i, h in enumerate(header or []):
        if any(n in h for n in names):
            return i
    return None


def check(text):
    header, rows = find_todo_table(text.splitlines())
    if header is None:
        return [{"line": None, "problem": "ToDo の表が見つかりません（「## ToDo」の下に表を置く）"}]
    owner_i, due_i = col(header, "担当"), col(header, "期限", "期日", "締切")
    out = []
    if owner_i is None:
        out.append({"line": None, "problem": "ToDo 表に「担当」列がありません"})
    if due_i is None:
        out.append({"line": None, "problem": "ToDo 表に「期限」列がありません"})
    for no, cells in rows:
        get = lambda i: cells[i] if i is not None and i < len(cells) else ""
        owner, due = get(owner_i), get(due_i)
        if owner_i is not None and not owner:
            out.append({"line": no, "problem": "担当が空です（不明なら【要確認】）"})
        if due_i is None or PENDING in due:
            continue
        if not due:
            out.append({"line": no, "problem": "期限が空です（不明なら【要確認】）"})
        elif VAGUE.search(due):
            out.append({"line": no, "problem": f"期限「{due}」があいまいです。日付にするか【要確認】に"})
        elif not DATE.search(due):
            out.append({"line": no, "problem": f"期限「{due}」が日付として読めません"})
    return out


def main():
    if "-h" in sys.argv or "--help" in sys.argv or (len(sys.argv) == 1 and sys.stdin.isatty()):
        # No file and nothing piped in: show usage instead of waiting on stdin.
        print(__doc__.strip())
        sys.exit(0 if len(sys.argv) > 1 else 2)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    text = open(args[0], encoding="utf-8").read() if args else sys.stdin.read()
    findings = check(text)
    if "--json" in sys.argv:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        for f in findings:
            where = f"{f['line']}行目" if f["line"] else "全体"
            print(f"[todo] {where}: {f['problem']}")
        if not findings:
            print("指摘はありません")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
