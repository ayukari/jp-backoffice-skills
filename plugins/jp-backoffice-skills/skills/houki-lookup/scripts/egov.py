"""Minimal client and normalizer for the e-Gov 法令API v2 (https://laws.e-gov.go.jp/api/2).

Standard library only, so it can be unit-tested without the Apify SDK.
"""
import json
import time
import urllib.parse
import urllib.request

BASE_URL = "https://laws.e-gov.go.jp/api/2"
USER_AGENT = "jp-backoffice-skills/houki-lookup (+https://github.com/ayukari/jp-backoffice-skills)"


class EgovClient:
    def __init__(self, base_url=BASE_URL, opener=None, min_interval=0.5, retries=3):
        self.base_url = base_url.rstrip("/")
        self.opener = opener or urllib.request.urlopen
        self.min_interval = min_interval  # be polite to a public government API
        self.retries = retries
        self._last = 0.0

    def _get(self, path, params):
        url = f"{self.base_url}/{path}?{urllib.parse.urlencode(params)}"
        for attempt in range(self.retries):
            wait = self.min_interval - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
                with self.opener(req, timeout=30) as res:
                    return json.loads(res.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and attempt < self.retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise
            except urllib.error.URLError:
                if attempt < self.retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise

    def search_laws(self, title=None, law_num=None, law_id=None, limit=10, offset=0):
        params = {"limit": limit, "offset": offset}
        if title:
            params["law_title"] = title
        if law_num:
            params["law_num"] = law_num
        if law_id:
            params["law_id"] = law_id
        return self._get("laws", params)

    def get_article(self, law_id, article):
        return self._get(f"law_data/{law_id}", {
            "law_full_text_format": "json",
            "elm": f"MainProvision-Article_{article}",
        })


def summarize_law(entry):
    """Flatten one item of the /laws response into a dataset record."""
    info = entry.get("law_info", {})
    rev = entry.get("current_revision_info") or entry.get("revision_info") or {}
    return {
        "lawId": info.get("law_id"),
        "lawNum": info.get("law_num"),
        "lawTitle": rev.get("law_title"),
        "lawTitleKana": rev.get("law_title_kana"),
        "category": rev.get("category"),
        "lawType": info.get("law_type"),
        "promulgationDate": info.get("promulgation_date"),
        "enforcementDate": rev.get("amendment_enforcement_date"),
        "revisionId": rev.get("law_revision_id"),
        "url": f"https://laws.e-gov.go.jp/law/{info.get('law_id')}" if info.get("law_id") else None,
    }


def _text(node):
    if isinstance(node, str):
        return node
    return "".join(_text(c) for c in node.get("children", []))


def _find(node, tag):
    return next((c for c in node.get("children", []) if isinstance(c, dict) and c.get("tag") == tag), None)


def _item_lines(node, depth):
    """Render Item / Subitem1 / Subitem2... recursively with indentation."""
    lines = []
    for child in node.get("children", []):
        if not isinstance(child, dict):
            continue
        tag = child.get("tag", "")
        if tag == "Item" or tag.startswith("Subitem"):
            title = _find(child, f"{tag}Title")
            sentence = _find(child, f"{tag}Sentence")
            cols = [c for c in (sentence or {}).get("children", []) if isinstance(c, dict) and c.get("tag") == "Column"]
            body = "　".join(_text(c) for c in cols) if cols else _text(sentence or {})
            lines.append("　" * depth + f"{_text(title or {})}　{body}".strip())
            lines.extend(_item_lines(child, depth + 1))
    return lines


def normalize_article(law_data):
    """Turn a /law_data response for one article into a flat record with paragraphs as text."""
    full = law_data.get("law_full_text") or {}
    article = full if full.get("tag") == "Article" else _search(full, "Article")
    if not article:
        return None
    paragraphs = []
    for p in article.get("children", []):
        if not isinstance(p, dict) or p.get("tag") != "Paragraph":
            continue
        sentence = _text(_find(p, "ParagraphSentence") or {})
        items = _item_lines(p, 1)
        paragraphs.append({
            "num": int(p.get("attr", {}).get("Num", len(paragraphs) + 1)),
            "text": sentence,
            "items": items,
        })
    meta = summarize_law({"law_info": law_data.get("law_info", {}), "revision_info": law_data.get("revision_info", {})})
    caption = _text(_find(article, "ArticleCaption") or {})
    title = _text(_find(article, "ArticleTitle") or {})
    full_text = "\n".join(
        [f"{title}{caption}"] + [f"{'' if p['num'] == 1 else str(p['num']) + '　'}{p['text']}" + ("\n" + "\n".join(p["items"]) if p["items"] else "") for p in paragraphs]
    )
    return {**meta, "articleNum": article.get("attr", {}).get("Num"), "articleTitle": title,
            "articleCaption": caption, "paragraphs": paragraphs, "text": full_text}


def _search(node, tag):
    if isinstance(node, dict):
        if node.get("tag") == tag:
            return node
        for c in node.get("children", []):
            found = _search(c, tag)
            if found:
                return found
    return None
