import unittest

from keigo_lint import lint


def rules(text):
    return [f["rule"] for f in lint(text)]


class KeigoLintTest(unittest.TestCase):
    def test_double_keigo(self):
        self.assertIn("ossharareru", rules("部長がおっしゃられた件ですが"))
        self.assertIn("goran-ninararemasu", rules("資料はご覧になられましたか。"))

    def test_humble_used_for_other_party(self):
        self.assertIn("haiken-sareru", rules("資料を拝見されましたか"))
        self.assertIn("mairareru", rules("何時に参られますか"))

    def test_clean_email_has_no_errors(self):
        text = "いつもお世話になっております。\n資料をご確認いただけますでしょうか。\n承知しました。"
        self.assertEqual([f for f in lint(text) if f["level"] == "error"], [])

    def test_sasete_overuse(self):
        text = "送付させていただきます。確認させていただきます。連絡させていただきます。"
        self.assertIn("sasete-overuse", rules(text))
        self.assertNotIn("sasete-overuse", rules("送付させていただきます。"))

    def test_line_numbers(self):
        f = lint("一行目\nご苦労様です")[0]
        self.assertEqual((f["line"], f["rule"]), (2, "gokurousama"))


if __name__ == "__main__":
    unittest.main()
