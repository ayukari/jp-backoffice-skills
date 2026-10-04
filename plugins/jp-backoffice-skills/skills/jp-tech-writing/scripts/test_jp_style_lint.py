import unittest

from jp_style_lint import lint


def rules(text):
    return [f["rule"] for f in lint(text)]


class StyleLintTest(unittest.TestCase):
    def test_redundant(self):
        self.assertIn("redundant", rules("設定を変更することができます。"))

    def test_mixed_style(self):
        text = "これはペンです。あれは本である。それも本です。"
        self.assertIn("mixed-style", rules(text))
        self.assertNotIn("mixed-style", rules("これはペンです。あれは本です。"))

    def test_hyogen_yure(self):
        self.assertIn("hyogen-yure", rules("サーバーを起動します。次にサーバを止めます。"))
        self.assertNotIn("hyogen-yure", rules("サーバーを起動します。次にサーバーを止めます。"))

    def test_plain_form_mixed_with_polite(self):
        self.assertIn("mixed-style", rules("サーバーを監視します。ユーザーは状態を見ることができる。"))
        self.assertNotIn("mixed-style", rules("設定を開きます。保存してください。"))

    def test_preferred_form_alone(self):
        self.assertIn("preferred-form", rules("ユーザが使います。"))
        self.assertIn("preferred-form", rules("見ることが出来ます。"))
        self.assertNotIn("preferred-form", rules("ユーザーが使います。サーバーです。"))

    def test_long_sentence_and_commas(self):
        long = "これは" + "とても" * 40 + "長い文です。"
        self.assertIn("long-sentence", rules(long))
        self.assertIn("many-commas", rules("まず、次に、さらに、そして、最後に終わります。"))

    def test_code_is_ignored(self):
        text = "```\nすることができる\n```\n`サーバ` の説明です。サーバーです。"
        self.assertEqual(rules(text), [])

    def test_double_ga(self):
        self.assertIn("double-ga", rules("私がこの機能が好きです。"))
        self.assertNotIn("double-ga", rules("知りたいのは「何が必要か」です。"))


if __name__ == "__main__":
    unittest.main()
