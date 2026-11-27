# AGENTS.md

Rules for any coding agent working in this repository. Every line is an
instruction; the reasoning is in `README.md` and `docs/adr/`.

## Where a new rule goes

Classify it before writing it. Nothing is stated in full in two places; the
second place gets a pointer. How it is worded → `.claude/rules/instruction-files.md`.

| It is… | It goes in |
|---|---|
| an invariant, a command, or anything that constrains a change | this file |
| rationale, narrative, or anything explaining *why* | `README.md` |
| a decision, what was rejected, and what would reopen it | `docs/adr/` |
| a multi-step procedure | `.claude/skills/<name>/SKILL.md` |
| true only inside one directory | `.claude/rules/<name>.md`, with `paths:` |
| something that must hold whatever an agent decides | `.claude/settings.json` or `.claude/hooks/` |

A security invariant stays in this file **unscoped**, even when a directory
would fit — it must not depend on a glob matching.

`.claude/settings.json` is the **only** settings file. A second one a client
writes for itself is folded in or deleted, never left as a truth nobody sees.
→ `CLAUDE.md`, *What Claude Code loads on its own*.

## What this is

The shared agent workflow — instruction-file rules, skills, the commit guard, the guard
scripts and the PR gates — worked in this repository by that same workflow, and taken by
other repositories as a pinned copy. → README; issue 1 for the plan.

## Read before changing anything

**Read `docs/adr/` for any decision you are about to revisit.** It records what
was rejected and the condition that would reopen it.

**Start a research issue's implementation only after its ADR is accepted.**

## Architecture rules

The numbers are stable: cite them, and keep them consecutive when one is added.

1. **Name no repository that takes the kit, its product, its host or its owner's
   details.** This repository is public; a shared file is written for any repository.
2. **Write every script in Python 3.12's standard library, with no runtime package.** A
   repository that takes the kit needs only `uv` and Python to run it.
3. **Shell out only to `git` and `gh`**, each named once in a module constant.
4. **Keep a script's exit codes to `0` clean, `1` problems found, `2` could not run**,
   and print problems to stderr.

## Tooling

Python 3.12 and `uv` — never pip or poetry. `ruff` for lint and format, `mypy`
strict, `pytest`.

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy scripts tests .claude/hooks
uv run pytest
uv run python scripts/check_instructions.py
```

## How work happens here

**Read the procedure before doing the thing — never reconstruct it from memory.**

| Procedure | Read it |
|---|---|
| `.claude/skills/feature-lifecycle/SKILL.md` | before starting any feature, fix or chore; before every commit; before reporting anything finished |
| `.claude/skills/picking-the-next-issue/SKILL.md` | when told to pick the next issue, before choosing one |
| `.claude/skills/grooming-an-issue/SKILL.md` | when an issue number or a description is handed over, before a branch is cut |

These are mechanisms, and hold whether or not a procedure is read:

- The branch ruleset blocks a merge until `checks / check`, `checks / secrets`,
  `closing-references` and `dependencies` are green on an up-to-date branch, and
  permits no direct push, force push or deletion on `main`.
- `main` takes **squash or rebase** merges only.
- `.claude/hooks/git_commit_guard.py` refuses a commit on `main`, a branch named none of
  `feat/`, `fix/` and `chore/`, or a branch this session did not switch to; a message
  with a body; a malformed prefix; and any AI author, co-author or session trailer.

**Work in a tree no other session is holding.** Another session already in this
checkout means a `git worktree` instead. → ADR 0001, D5.

**Run the checks above locally before every push**; CI confirms a green result, never
discovers it. **Never merge a PR whose pipeline has not finished, and never bypass the
ruleset.** There is no human review gate here: green means merge, not green means fix it.

**Add a package only when it is worth it.** The PR that adds one answers ADR 0001, D7's
six questions in a `## Dependency: <name>` section per package; a version bump needs none.

## Code style

- **Write raw code.** No inline comments, no docstrings, no block comments.
- **Type strictly, with no half measures.** `mypy` runs `strict` and
  `warn_unreachable`.
- **Never write `Any` in our own code** — ruff's `ANN401` makes it an error.
- **Take `gh` and `git` output in as `object`** and narrow it with `isinstance`; a
  payload of the wrong shape exits `2`, never a guess.

## Testing

**Never let a test reach GitHub.** → `.claude/rules/testing.md`.

## Secrets

**Never commit `.env` or a credential file.** `checks / secrets` fails the build if one
is tracked.
