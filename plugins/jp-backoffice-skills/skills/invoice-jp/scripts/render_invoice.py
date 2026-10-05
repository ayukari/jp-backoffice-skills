#!/usr/bin/env python3
"""Render a qualified invoice (適格請求書) as Markdown or HTML.

Usage:
  python3 render_invoice.py invoice.json            # Markdown
  python3 render_invoice.py invoice.json --html     # HTML

Input JSON is the same as invoice_calc.py, plus optional fields:
  "transaction_date" (取引年月日) or "period": {"from": ..., "to": ...} (取引期間),
  "invoice_number", "due_date", "bank" (振込先), "notes".
"date" is the invoice issue date (請求日). The transaction date is a required item of a
qualified invoice; if neither transaction_date nor period is given, it is printed as 【要確認】.
"""
import html
import json
import sys
from datetime import date

from invoice_calc import calculate, validate


def yen(n):
    return f"{n:,}"


def jp_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.year}年{d.month}月{d.day}日"


def transaction_label(inv):
    if inv.get("period"):
        return f"{jp_date(inv['period']['from'])}〜{jp_date(inv['period']['to'])}"
    if inv.get("transaction_date"):
        return jp_date(inv["transaction_date"])
    return "【要確認】"


def item_rows(inv):
    rows = []
    for item in inv["items"]:
        qty = item.get("qty", 1)
        amount = int(item["unit_price"] * qty)
        name = item["name"] + (" ※" if item["rate"] == 8 else "")
        rows.append((name, qty, yen(item["unit_price"]), yen(amount), f"{item['rate']}%"))
    return rows


def render_markdown(inv, calc):
    mode = "税込" if inv.get("price_mode") == "inclusive" else "税抜"
    lines = ["# 請求書", ""]
    meta = f"請求日: {jp_date(inv['date'])}"
    if inv.get("invoice_number"):
        meta += f"　　請求番号: {inv['invoice_number']}"
    lines += [meta, f"取引年月日: {transaction_label(inv)}", "", f"{inv['recipient']} 御中", ""]
    lines += [f"発行者: {inv['issuer']['name']}（登録番号: {inv['issuer']['registration_number']}）", ""]
    lines += [f"**ご請求金額（税込）: {yen(calc['total_incl_tax'])}円**", ""]
    lines += [f"| 品目 | 数量 | 単価（{mode}） | 金額（{mode}） | 税率 |", "|---|---:|---:|---:|---:|"]
    lines += [f"| {n} | {q} | {u} | {a} | {r} |" for n, q, u, a, r in item_rows(inv)]
    lines += ["", "| 税率 | 対象額（税抜） | 消費税額 | 合計（税込） |", "|---|---:|---:|---:|"]
    for s in calc["by_rate"]:
        label = f"{s['rate']}%対象" + ("（軽減税率）" if s["reduced"] else "")
        lines.append(f"| {label} | {yen(s['subtotal_excl_tax'])} | {yen(s['tax'])} | {yen(s['subtotal_incl_tax'])} |")
    if any(s["reduced"] for s in calc["by_rate"]):
        lines += ["", "※は軽減税率（8%）対象品目です。"]
    if inv.get("due_date"):
        lines += ["", f"お支払期限: {jp_date(inv['due_date'])}"]
    if inv.get("bank"):
        lines += [f"お振込先: {inv['bank']}"]
    if inv.get("notes"):
        lines += ["", f"備考: {inv['notes']}"]
    return "\n".join(lines) + "\n"


def render_html(inv, calc):
    e = html.escape
    rows = "".join(
        f"<tr><td>{e(n)}</td><td class=n>{q}</td><td class=n>{u}</td><td class=n>{a}</td><td class=n>{r}</td></tr>"
        for n, q, u, a, r in item_rows(inv)
    )
    tax_rows = "".join(
        f"<tr><td>{s['rate']}%対象{'（軽減税率）' if s['reduced'] else ''}</td>"
        f"<td class=n>{yen(s['subtotal_excl_tax'])}</td><td class=n>{yen(s['tax'])}</td>"
        f"<td class=n>{yen(s['subtotal_incl_tax'])}</td></tr>"
        for s in calc["by_rate"]
    )
    extra = ""
    if any(s["reduced"] for s in calc["by_rate"]):
        extra += "<p>※は軽減税率（8%）対象品目です。</p>"
    if inv.get("due_date"):
        extra += f"<p>お支払期限: {jp_date(inv['due_date'])}</p>"
    if inv.get("bank"):
        extra += f"<p>お振込先: {e(inv['bank'])}</p>"
    if inv.get("notes"):
        extra += f"<p>備考: {e(inv['notes'])}</p>"
    number = f"　請求番号: {e(inv['invoice_number'])}" if inv.get("invoice_number") else ""
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><title>請求書</title>
<style>body{{font-family:sans-serif;max-width:720px;margin:2em auto}}table{{border-collapse:collapse;width:100%;margin:1em 0}}
td,th{{border:1px solid #999;padding:4px 8px}}.n{{text-align:right}}.total{{font-size:1.3em;font-weight:bold}}</style></head>
<body><h1>請求書</h1>
<p>請求日: {jp_date(inv['date'])}{number}</p>
<p>取引年月日: {transaction_label(inv)}</p>
<p>{e(inv['recipient'])} 御中</p>
<p>発行者: {e(inv['issuer']['name'])}（登録番号: {e(inv['issuer']['registration_number'])}）</p>
<p class=total>ご請求金額（税込）: {yen(calc['total_incl_tax'])}円</p>
<table><tr><th>品目</th><th>数量</th><th>単価</th><th>金額</th><th>税率</th></tr>{rows}</table>
<table><tr><th>税率</th><th>対象額（税抜）</th><th>消費税額</th><th>合計（税込）</th></tr>{tax_rows}</table>
{extra}</body></html>
"""


def main():
    if "-h" in sys.argv or "--help" in sys.argv or (len(sys.argv) == 1 and sys.stdin.isatty()):
        # No file and nothing piped in: show usage instead of waiting on stdin.
        print(__doc__.strip())
        sys.exit(0 if len(sys.argv) > 1 else 2)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    inv = json.load(open(args[0]) if args else sys.stdin)
    errors = validate(inv)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)
    calc = calculate(inv)
    print(render_html(inv, calc) if "--html" in sys.argv else render_markdown(inv, calc), end="")


if __name__ == "__main__":
    main()
