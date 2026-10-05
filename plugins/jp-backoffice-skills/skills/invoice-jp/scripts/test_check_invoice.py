import unittest

from check_invoice import check
from invoice_calc import calculate
from render_invoice import render_markdown
from test_render_invoice import INV


class CheckInvoiceTest(unittest.TestCase):
    def test_rendered_invoice_passes(self):
        out = check(render_markdown(INV, calculate(INV)))
        self.assertEqual(out["overall"], "OK", out)

    def test_only_issue_date_needs_check(self):
        inv = {k: v for k, v in INV.items() if k != "transaction_date"}
        out = check(render_markdown(inv, calculate(inv)))
        self.assertEqual(out["items"]["2_transaction_date"]["status"], "要確認")

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
取引日 2026年10月1日
品目 作業A 3 333 999 10%
| 10%対象 | 999 | 98 |
"""
        out = check(text)
        self.assertEqual(out["items"]["5_tax_by_rate"]["status"], "要確認")

    def test_cause_calculation_error(self):
        # 3 x 333 = 999: per-rate tax is 99/100, per-line is 99/102, so 98 is a calculation error.
        text = """請求書
株式会社テスト 御中
2026年10月4日
登録番号 T1234567890123
取引日 2026年10月1日
| 品目 | 金額 | 税率 |
| 作業A | 333 | 10% |
| 作業B | 333 | 10% |
| 作業C | 333 | 10% |
| 10%対象 | 999 | 98 |
"""
        c = check(text)["items"]["5_tax_by_rate"]
        self.assertEqual(c["checks"][0]["cause"], "計算誤り")
        self.assertIn("計算誤り", c["detail"])

    def test_cause_per_line_rounding(self):
        # 3 x 105 at 10%: per-rate floor is 31, per-line floor is 10 x 3 = 30.
        text = """請求書
株式会社テスト 御中
2026年10月4日
登録番号 T1234567890123
取引日 2026年10月1日
| 品目 | 金額 | 税率 |
| 部品A | 105 | 10% |
| 部品B | 105 | 10% |
| 部品C | 105 | 10% |
| 10%対象 | 315 | 30 |
"""
        c = check(text)["items"]["5_tax_by_rate"]
        self.assertEqual(c["checks"][0]["cause"], "明細ごとの端数処理")
        self.assertIn("明細ごとに端数処理", c["detail"])

    def test_reduced_rate_without_marker(self):
        text = render_markdown(INV, calculate(INV)).replace(" ※", "").replace("（軽減税率）", "").replace("※は軽減税率（8%）対象品目です。", "")
        out = check(text)
        self.assertEqual(out["items"]["3_transaction_details"]["status"], "要確認")


if __name__ == "__main__":
    unittest.main()
