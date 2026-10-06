#!/usr/bin/env python3
"""Look up Japanese laws and article text from the official e-Gov 法令API v2.

Usage:
  python3 law_lookup.py --title 消費税法                      # find laws (metadata)
  python3 law_lookup.py --title 消費税法 --article 57の4       # one article as text
  python3 law_lookup.py --law-id 363AC0000000108 --article 第三十条 --json

Article numbers accept 30, 第30条, 57の4, 第57条の4, 57_4, 第三十条, 第五十七条の四.
With --title, an exact title match is used for --article; otherwise the first hit.
Exit codes: 0 ok, 1 not found / API error (never fill in text from memory), 2 usage.
"""
import argparse
import json
import re
import sys

from egov import EgovClient, normalize_article, summarize_law

KANJI_DIGITS = {"〇": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
KANJI_UNITS = {"十": 10, "百": 100, "千": 1000}


def kanji_to_int(s):
    """'三十' -> 30, '五十七' -> 57, '百二' -> 102. Plain digits pass through."""
    if s.isdigit():
        return int(s)
    total, cur = 0, 0
    for ch in s:
        if ch in KANJI_DIGITS:
            cur = KANJI_DIGITS[ch]
        elif ch in KANJI_UNITS:
            total += (cur or 1) * KANJI_UNITS[ch]
            cur = 0
        else:
            raise ValueError(s)
    return total + cur


def normalize_article_num(s):
    """'第57条の4' / '57の4' / '57_4' / '第五十七条の四' -> '57_4'."""
    s = s.strip().translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    num = r"([0-9〇一二三四五六七八九十百千]+)"
    m = re.fullmatch(rf"第?{num}条?(?:の{num})*", s) or re.fullmatch(r"(\d+)(?:_(\d+))*", s)
    if not m:
        raise ValueError(f"条番号を解釈できません: {s}")
    parts = re.findall(r"[0-9〇一二三四五六七八九十百千]+", s)
    return "_".join(str(kanji_to_int(p)) for p in parts)


def pick_law(laws, title):
    exact = [l for l in laws if l.get("lawTitle") == title]
    return (exact or laws or [None])[0]


def main(argv=None, client=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(__doc__.strip())
        return 2
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("--title")
    p.add_argument("--law-id")
    p.add_argument("--article")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    if not a.title and not a.law_id:
        print("--title か --law-id を指定してください", file=sys.stderr)
        return 2
    client = client or EgovClient()
    try:
        # For an article lookup, fetch more candidates so an exact title match isn't cut off
        # (e.g. 「民法」 also matches 民法施行法 and others).
        limit = 50 if a.article else max(1, min(a.limit, 50))
        res = client.search_laws(title=a.title, law_id=a.law_id, limit=limit)
        laws = [summarize_law(x) for x in res.get("laws", [])]
        if not laws:
            print("該当する法令が見つかりません（記憶で補わないこと）", file=sys.stderr)
            return 1
        if not a.article:
            out = laws
            text = "\n".join(f"{l['lawTitle']}（{l['lawNum']}）施行日 {l['enforcementDate']} {l['url']}" for l in laws)
        else:
            law = pick_law(laws, a.title)
            rec = normalize_article(client.get_article(law["lawId"], normalize_article_num(a.article)))
            if not rec:
                print("条文が見つかりません（記憶で補わないこと）", file=sys.stderr)
                return 1
            out = rec
            text = f"{rec['text']}\n\n出典: {rec['lawTitle']}（{rec['lawNum']}）施行日 {rec['enforcementDate']} {rec['url']}"
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    except Exception as e:  # network/API errors: report, never improvise the text
        print(f"e-Gov 法令API に接続できませんでした: {e}（記憶で条文を補わないこと）", file=sys.stderr)
        return 1
    print(json.dumps(out, ensure_ascii=False, indent=2) if a.json else text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
