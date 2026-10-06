# Evals

`evals.json` lists 3 realistic prompts per skill, each with a checklist of expected behavior.

How to run: start Claude Code with this plugin installed, give it each prompt in a fresh session, and check the response against `expected`. Record the result in `results/YYYY-MM-DD.md`, marking each checklist item as pass or fail.

## Automated runs with `claude plugin eval`

The same 19 evals also live as `claude plugin eval` cases in `plugins/jp-backoffice-skills/evals/<id>/`. Each case has `prompt.md` and `graders/criteria.md`, an LLM-judged checklist. Run them from the repo root:

```bash
claude plugin eval ./plugins/jp-backoffice-skills --allow-tools Bash Write --judge-model sonnet
claude plugin eval ./plugins/jp-backoffice-skills --tag invoice-jp --runs 1     # one skill, one run
```

- Skills that run scripts need `--allow-tools Bash Write`. Without it, the agent answers without the script.
- **Use `--judge-model sonnet`.** On 2026-10-06, the default judge (haiku) failed a correct Japanese answer to `invoice-02-missing-info` 3/3. Sonnet passed the same kind of answer 3/3 on a re-run. The checklists are in Japanese and need a stronger judge.
- By default each case runs 3 times and also runs a no-plugin baseline, so a full run costs real usage. Filter with `--case` / `--tag` while iterating.
