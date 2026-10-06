---
type: llm
weight: 1
---

The response passes only if **every** item below holds. Grade strictly: a borderline item fails.

- law_lookup.py で e-Gov 法令API から条文を取得している
- 条文を原文のまま引用している（要約だけで済ませない）
- 法令番号・施行日・e-Gov の URL を出典として示している
- 取得できなかった場合に記憶で条文を補っていない
