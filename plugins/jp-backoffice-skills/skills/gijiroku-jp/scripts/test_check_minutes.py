import unittest

from check_minutes import check

GOOD = """# 定例 議事録
## 決定事項
1. 公開日を 11/1 に決定。
## ToDo
| # | 内容 | 担当 | 期限 |
|---|---|---|---|
| 1 | 画像を差し替える | 佐藤 | 10/16（金） |
| 2 | フォームのテストを行う | 鈴木 | 【要確認】 |
## 持ち越し・未決事項
- なし
"""


class CheckMinutesTest(unittest.TestCase):
    def test_good_minutes_pass(self):
        self.assertEqual(check(GOOD), [])

    def test_vague_and_missing(self):
        text = GOOD.replace("| 佐藤 | 10/16（金） |", "|  | 来週中 |").replace("| 鈴木 | 【要確認】 |", "| 鈴木 | 早めに |")
        problems = [f["problem"] for f in check(text)]
        self.assertTrue(any("担当が空" in p for p in problems))
        self.assertTrue(any("来週中" in p for p in problems))
        self.assertTrue(any("早めに" in p for p in problems))

    def test_non_date(self):
        text = GOOD.replace("10/16（金）", "次回まで")
        self.assertTrue(any("日付として読めません" in f["problem"] for f in check(text)))

    def test_kanji_date_ok(self):
        self.assertEqual(check(GOOD.replace("10/16（金）", "10月16日")), [])

    def test_no_table(self):
        self.assertIn("表が見つかりません", check("# 議事録\n## 決定事項\n- なし\n")[0]["problem"])

    def test_example_md_output_is_consistent(self):
        # The skill's own example: one ToDo has 【要確認】 (accepted), so no findings.
        import pathlib, re
        ex = (pathlib.Path(__file__).parent.parent / "example.md").read_text(encoding="utf-8")
        block = re.search(r"## 出力（議事録）\s*```markdown\n(.*?)```", ex, re.S).group(1)
        self.assertEqual(check(block), [])


if __name__ == "__main__":
    unittest.main()
