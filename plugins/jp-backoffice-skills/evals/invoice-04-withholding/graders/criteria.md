---
type: llm
weight: 1
---

The response passes only if **every** item below holds. Grade strictly: a borderline item fails.

- invoice_calc.py に withholding と reimbursements を渡して計算している
- 源泉徴収税額 10,210円（10万円×10.21%）を差し引いている
- 交通費1,200円は立替金として消費税の計算に含めていない
- ご請求金額が 100,990円（110,000−10,210＋1,200）になっている
- 源泉徴収の要否を自分で判断せず、ユーザーの指定に従っている
