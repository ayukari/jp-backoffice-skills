import unittest

from check_invoice import check
from invoice_calc import calculate
from render_invoice import render_markdown
from test_render_invoice import INV


class CheckInvoiceTest(unittest.TestCase):
    def test_rendered_invoice_passes(self):
        out = check(render_markdown(INV, calculate(INV)))
        self.assertEqual(out["overall"], "OK", out)

    def test_missing_registration_number(self):
        text = render_markdown(INV, calculate(INV)).replace("T1234567890123", "")
        out = check(text)
        self.assertEqual(out["items"]["1_issuer_and_registration_number"]["status"], "不足")
        self.assertEqual(out["overall"], "不足")

    def test_per_line_rounding_is_flagged(self):
        # 3 x 333 at 10%: correct per-rate tax is 99; 98 would be wrong under any single rounding.
        text = """請求書
株式会社テスト 御中
2026年10月4日
登録番号 T1234567890123
品目 作業A 3 333 999 10%
| 10%対象 | 999 | 98 |
"""
        out = check(text)
        self.assertEqual(out["items"]["5_tax_by_rate"]["status"], "要確認")

    def test_reduced_rate_without_marker(self):
        text = render_markdown(INV, calculate(INV)).replace(" ※", "").replace("（軽減税率）", "").replace("※は軽減税率（8%）対象品目です。", "")
        out = check(text)
        self.assertEqual(out["items"]["3_transaction_details"]["status"], "要確認")


if __name__ == "__main__":
    unittest.main()
