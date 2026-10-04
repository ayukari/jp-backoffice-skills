#!/usr/bin/env python3
"""Check a plain-text invoice against the six required items of a qualified invoice (適格請求書).

Usage:
  python3 check_invoice.py invoice.txt     # or pipe text on stdin

Output: JSON with one entry per required item, each with status "OK", "不足" (missing)
or "要確認" (needs a human check), and tax recalculation per rate.

This is a heuristic text check. It flags problems; it does not certify an invoice.
"""
import json
import re
import sys
from decimal import ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP, Decimal

REG_NO = re.compile(r"T\d{13}")
DATE = re.compile(r"(\d{4})\s*[年/\-.]\s*(\d{1,2})\s*[月/\-.]\s*(\d{1,2})")
RECIPIENT = re.compile(r"^(.+?)\s*(御中|様)\s*$", re.M)
ITEM_HEADER = re.compile(r"品目|品名|内容|摘要|項目")
# A per-rate summary line, e.g. "| 10%対象 | 100,000 | 10,000 |" or "8%対象 1,000円 消費税 80円".
RATE_LINE = re.compile(r"(10|8)\s*[%％]\s*対象(?:（軽減税率）|\(軽減税率\))?[^\d\n]*([\d,]+)[^\d\n]+([\d,]+)")
REDUCED_MARK = re.compile(r"※|軽減")


def num(s):
    return int(s.replace(",", ""))


def expected_taxes(base, rate):
    r = Decimal(rate) / 100
    return {int((Decimal(base) * r).quantize(Decimal(1), rounding=m)) for m in (ROUND_FLOOR, ROUND_HALF_UP, ROUND_CEILING)}


def check(text):
    results = {}

    reg = REG_NO.search(text)
    results["1_issuer_and_registration_number"] = {
        "status": "OK" if reg else "不足",
        "detail": f"登録番号 {reg.group()} を検出（発行者名は目視で確認）" if reg else "登録番号（T+13桁）が見つかりません",
    }

    date = DATE.search(text)
    tx = re.search(r"(取引(年月日|日|期間)|納品日|作業期間|対象期間|\d{1,2}\s*月\s*分)", text)
    tx_pending = re.search(r"取引(年月日|日|期間)[^\n]*【要確認】", text)
    if not date:
        status, detail = "不足", "取引年月日が見つかりません"
    elif tx and not tx_pending:
        status, detail = "OK", f"取引日・期間の記載あり（{tx.group()}）"
    else:
        status, detail = "要確認", "請求日はあるが、取引年月日（または取引期間）の記載が見つかりません"
    results["2_transaction_date"] = {"status": status, "detail": detail}

    has_items = bool(ITEM_HEADER.search(text))
    rates_used = sorted({int(m) for m in re.findall(r"(10|8)\s*[%％]", text)})
    reduced_ok = 8 not in rates_used or bool(REDUCED_MARK.search(text))
    results["3_transaction_details"] = {
        "status": "OK" if has_items and reduced_ok else ("不足" if not has_items else "要確認"),
        "detail": ("品目欄あり" if has_items else "品目・内容の欄が見つかりません")
        + ("" if reduced_ok else "／8%品目に「※」などの軽減税率対象の表示がありません"),
    }

    summaries = [(int(m.group(1)), num(m.group(2)), num(m.group(3))) for m in RATE_LINE.finditer(text)]
    tax_checks = []
    for rate, base, tax in summaries:
        ok = tax in expected_taxes(base, rate)
        tax_checks.append({"rate": rate, "base_excl_tax": base, "tax_on_invoice": tax,
                           "tax_expected": sorted(expected_taxes(base, rate)), "ok": ok})
    summarized = {s[0] for s in summaries}
    missing_rates = [r for r in rates_used if r not in summarized]
    results["4_totals_by_rate_and_rate"] = {
        "status": "OK" if summaries and not missing_rates else "不足",
        "detail": "税率ごとの合計あり" if summaries and not missing_rates
        else f"税率ごとの合計がありません: {missing_rates or rates_used or '税率の記載なし'}",
    }
    results["5_tax_by_rate"] = {
        "status": "OK" if tax_checks and all(c["ok"] for c in tax_checks) else ("不足" if not tax_checks else "要確認"),
        "detail": "税額は税率ごとの端数処理1回と一致" if tax_checks and all(c["ok"] for c in tax_checks)
        else ("税率ごとの消費税額が見つかりません" if not tax_checks else "税額が再計算と一致しません（明細ごとの端数処理の可能性）"),
        "checks": tax_checks,
    }

    rec = RECIPIENT.search(text)
    results["6_recipient"] = {
        "status": "OK" if rec else "不足",
        "detail": f"宛名「{rec.group(1).strip('| ')}」を検出" if rec else "宛名（〇〇御中／様）が見つかりません",
    }

    statuses = [v["status"] for v in results.values()]
    overall = "OK" if all(s == "OK" for s in statuses) else ("不足" if "不足" in statuses else "要確認")
    return {"overall": overall, "items": results}


def main():
    text = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    out = check(text)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(0 if out["overall"] == "OK" else 1)


if __name__ == "__main__":
    main()
