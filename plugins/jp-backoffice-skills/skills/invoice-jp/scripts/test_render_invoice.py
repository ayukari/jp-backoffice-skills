import unittest

from invoice_calc import calculate
from render_invoice import render_html, render_markdown

INV = {
    "issuer": {"name": "山田デザイン", "registration_number": "T1234567890123"},
    "recipient": "株式会社サンプル",
    "date": "2026-10-04",
    "transaction_date": "2026-10-01",
    "invoice_number": "INV-001",
    "due_date": "2026-10-31",
    "items": [
        {"name": "Webデザイン", "qty": 1, "unit_price": 100000, "rate": 10},
        {"name": "差し入れ菓子", "qty": 2, "unit_price": 500, "rate": 8},
    ],
}


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.calc = calculate(INV)

    def test_markdown_has_required_items(self):
        md = render_markdown(INV, self.calc)
        for needle in ["T1234567890123", "株式会社サンプル 御中", "2026年10月4日",
                       "差し入れ菓子 ※", "8%対象（軽減税率）", "10%対象", "110,000", "1,080",
                       "ご請求金額（税込）: 111,080円", "お支払期限: 2026年10月31日",
                       "取引年月日: 2026年10月1日"]:
            self.assertIn(needle, md)

    def test_missing_transaction_date_is_flagged(self):
        inv = {k: v for k, v in INV.items() if k != "transaction_date"}
        self.assertIn("取引年月日: 【要確認】", render_markdown(inv, calculate(inv)))

    def test_period(self):
        inv = {**INV, "period": {"from": "2026-09-01", "to": "2026-09-30"}}
        self.assertIn("取引年月日: 2026年9月1日〜2026年9月30日", render_markdown(inv, calculate(inv)))

    def test_html_escapes_input(self):
        inv = {**INV, "recipient": "<script>x</script>"}
        out = render_html(inv, calculate(inv))
        self.assertNotIn("<script>x", out)
        self.assertIn("&lt;script&gt;", out)


if __name__ == "__main__":
    unittest.main()
