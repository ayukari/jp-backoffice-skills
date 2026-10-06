import unittest

from check_invoice import check
from invoice_calc import calculate, validate, withholding_tax
from render_invoice import render_html, render_markdown
from test_invoice_calc import BASE

FEE = {"name": "ロゴデザイン料", "qty": 1, "unit_price": 100000, "rate": 10, "withholding": True}


class WithholdingTest(unittest.TestCase):
    def test_rate_thresholds(self):
        self.assertEqual(withholding_tax(100000), 10210)
        self.assertEqual(withholding_tax(1000000), 102100)
        # 1,500,000: 1,000,000 x 10.21% + 500,000 x 20.42% = 102,100 + 102,100
        self.assertEqual(withholding_tax(1500000), 204200)
        # Rounded down: 99,999 x 10.21% = 10,209.89...
        self.assertEqual(withholding_tax(99999), 10209)

    def test_exclusive_uses_amount_before_tax(self):
        c = calculate({**BASE, "items": [FEE]})
        self.assertEqual(c["withholding_base"], 100000)
        self.assertEqual(c["withholding_tax"], 10210)
        self.assertEqual(c["amount_due"], 110000 - 10210)

    def test_inclusive_uses_amount_with_tax(self):
        c = calculate({**BASE, "price_mode": "inclusive", "items": [{**FEE, "unit_price": 110000}]})
        self.assertEqual(c["withholding_base"], 110000)
        self.assertEqual(c["withholding_tax"], 11231)

    def test_only_flagged_items_are_withheld(self):
        c = calculate({**BASE, "items": [FEE, {"name": "印刷代", "qty": 1, "unit_price": 50000, "rate": 10}]})
        self.assertEqual(c["withholding_base"], 100000)
        self.assertEqual(c["amount_due"], 165000 - 10210)

    def test_plain_invoice_has_no_extra_fields(self):
        c = calculate({**BASE, "items": [{**FEE, "withholding": False}]})
        self.assertNotIn("amount_due", c)


class ReimbursementTest(unittest.TestCase):
    def test_added_outside_tax(self):
        c = calculate({**BASE, "items": [FEE], "reimbursements": [{"name": "交通費", "amount": 1200}]})
        self.assertEqual(c["total_tax"], 10000)
        self.assertEqual(c["reimbursements_total"], 1200)
        self.assertEqual(c["amount_due"], 110000 - 10210 + 1200)

    def test_reimbursement_only(self):
        item = {k: v for k, v in FEE.items() if k != "withholding"}
        c = calculate({**BASE, "items": [item], "reimbursements": [{"name": "交通費", "amount": 1200}]})
        self.assertEqual(c["withholding_tax"], 0)
        self.assertEqual(c["amount_due"], 111200)

    def test_invalid_reimbursement(self):
        errors = validate({**BASE, "items": [FEE], "reimbursements": [{"name": "", "amount": -1}]})
        self.assertTrue(any("reimbursements[0]" in e for e in errors))


class RenderExtrasTest(unittest.TestCase):
    INV = {**BASE, "transaction_date": "2026-10-01", "items": [FEE],
           "reimbursements": [{"name": "交通費", "amount": 1200}]}

    def test_markdown_breakdown_and_checker(self):
        md = render_markdown(self.INV, calculate(self.INV))
        self.assertIn("**ご請求金額: 100,990円**", md)
        self.assertIn("| 源泉徴収税額 | -10,210 |", md)
        self.assertIn("| 立替金：交通費（不課税） | 1,200 |", md)
        self.assertEqual(check(md)["overall"], "OK")

    def test_html_breakdown(self):
        out = render_html(self.INV, calculate(self.INV))
        self.assertIn("ご請求金額: 100,990円", out)
        self.assertIn("源泉徴収税額", out)


if __name__ == "__main__":
    unittest.main()
