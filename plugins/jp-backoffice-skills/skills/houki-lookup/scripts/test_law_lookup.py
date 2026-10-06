import contextlib
import io
import json
import unittest
from pathlib import Path

from law_lookup import main, normalize_article_num, pick_law

FIX = Path(__file__).parent / "fixtures"


class FakeClient:
    """Serves recorded e-Gov responses, so tests never hit the public API."""
    def __init__(self, fail=False):
        self.fail = fail
        self.calls = []

    def search_laws(self, **kw):
        if self.fail:
            raise OSError("network down")
        self.calls.append(("search", kw))
        return json.loads((FIX / "laws_shohizei.json").read_text(encoding="utf-8"))

    def get_article(self, law_id, article):
        self.calls.append(("article", law_id, article))
        return json.loads((FIX / "law_data_shohizei_art30.json").read_text(encoding="utf-8"))


def run(argv, client):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(argv, client)
    return code, out.getvalue(), err.getvalue()


class LawLookupTest(unittest.TestCase):
    def test_article_numbers(self):
        for s, want in [("30", "30"), ("第30条", "30"), ("第57条の4", "57_4"), ("57_4", "57_4"),
                        ("第三十条", "30"), ("第五十七条の四", "57_4"), ("第３０条", "30")]:
            self.assertEqual(normalize_article_num(s), want, s)
        with self.assertRaises(ValueError):
            normalize_article_num("附則")

    def test_exact_title_is_preferred(self):
        laws = [{"lawTitle": "消費税法施行令"}, {"lawTitle": "消費税法"}]
        self.assertEqual(pick_law(laws, "消費税法")["lawTitle"], "消費税法")

    def test_article_text_with_source(self):
        c = FakeClient()
        code, out, _ = run(["--title", "消費税法", "--article", "第三十条"], c)
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("第三十条（仕入れに係る消費税額の控除）"))
        self.assertIn("出典: 消費税法（昭和六十三年法律第百八号）", out)
        self.assertIn(("article", "363AC0000000108", "30"), c.calls)
        self.assertEqual(c.calls[0][1]["limit"], 50)  # wide search so the exact title is found

    def test_search_only_lists_laws(self):
        code, out, _ = run(["--title", "消費税法"], FakeClient())
        self.assertEqual(code, 0)
        self.assertIn("消費税法（昭和六十三年法律第百八号）", out)

    def test_network_error_never_improvises(self):
        code, out, err = run(["--title", "消費税法", "--article", "30"], FakeClient(fail=True))
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("記憶で条文を補わないこと", err)

    def test_usage(self):
        code, out, _ = run([], FakeClient())
        self.assertEqual(code, 2)
        self.assertIn("Usage", out)


if __name__ == "__main__":
    unittest.main()
