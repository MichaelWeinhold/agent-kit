# agent-kit

One agent workflow, kept in one place: the instruction-file rules, the skills that walk a
change from issue to merge, the commit guard, the guard scripts and the pull-request gates.
Each repository that uses it takes a **pinned, checked copy**, so an improvement lands once
and reaches every repository as a reviewed pull request, and a copy edited in place is
caught instead of drifting.

**Status:** bootstrapping. This repository is worked by its own workflow; how other
repositories take it is being decided in [issue 1](../../issues/1).

## What is in it

| Path | What it is |
|---|---|
| `AGENTS.md`, `CLAUDE.md` | the rules for any agent, and the Claude Code specifics |
| `.claude/skills/` | `feature-lifecycle`, `grooming-an-issue`, `picking-the-next-issue` |
| `.claude/rules/` | how instruction text is written; the pipeline; the tests |
| `.claude/hooks/git_commit_guard.py` | refuses a commit on `main`, on a stray branch, with a body or with an AI trailer |
| `scripts/check_instructions.py` | sizes, widths, frontmatter, settings, and the local-checks / CI parity |
| `scripts/check_pr_closes.py` | a PR closes only its own issue, and never a research issue |
| `scripts/check_dependencies.py` | a PR that adds a package explains it |
| `scripts/check_issue_umbrellas.py` | research issues, their children, and ☂️ |
| `scripts/next_issue.py` | parallel sessions claim issues without colliding |
| `.github/workflows/` | one reusable `checks.yml`, its entry points, and the two PR gates |

## Why it is shaped this way

**The rules live in the clone.** Any agent reads markdown files it finds in the
repository; a rule that only one client loads from somewhere else is a rule the other
agents never see. That is also why a copy has to be *checked*: a copy is what every tool
can read, and a check is what keeps it from drifting.

**What must hold is a mechanism, not a sentence.** The commit guard, the rulesets and the
PR gates hold whether or not an instruction was read. Instruction text says what to do;
the mechanisms make the important parts impossible to skip.

**Decisions are written down with what would reopen them.** `docs/adr/` records each
decision, the alternatives it rejected, and the condition under which each one should be
looked at again.

## Development

```bash
uv sync
uv run pytest
```

The full list of checks is the `## Tooling` block in `AGENTS.md`, and CI runs exactly that
list.

## Licence

MIT — see `LICENSE`.
