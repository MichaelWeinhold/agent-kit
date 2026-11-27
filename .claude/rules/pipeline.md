---
paths:
  - ".github/workflows/**"
---

# The pipeline

The `check` job in `checks.yml` runs exactly the `## Tooling` block of `AGENTS.md`, in
that order, after its `uv sync --locked`. `scripts/check_instructions.py` compares the two
lists for **equality**, so add a flag on both sides or neither. → ADR 0001, D3.

**Never skip a check, mark it `continue-on-error`, or make it conditional on the changed
paths.**

## What the job stands on is pinned

- **`runs-on: ubuntu-24.04`, never a `-latest` label.** Take a new image in a pull
  request.
- **Pin every action to a commit SHA with the version in a trailing comment.**
  Dependabot's `github-actions` ecosystem bumps both.
- **`uv sync --locked`, never a bare `uv sync`**, so a missing relock reddens a pull
  request.

The `secrets` job pipes `git ls-files` through `git check-ignore`. **Never give it a list
of its own**; `.gitignore` is the single statement of what must never be tracked.

## One file, two entry points

The checks live in **one** `workflow_call` workflow, `checks.yml`, which the entry points
call rather than copy:

| Workflow | Trigger | What it does |
|---|---|---|
| `pr.yml` | PR into `main` | The checks. This is the green light on a PR. |
| `main.yml` | push to `main` | The checks. **Never publishes anything.** |

Two more workflow files are **not** entry points:

| Workflow | Trigger | What it does |
|---|---|---|
| `pr-closes.yml` | PR into `main`, including on `edited` | One gate on the PR's closing references. Calls nothing. |
| `pr-dependencies.yml` | PR into `main`, including on `edited` | One gate: each package new in `pyproject.toml` has its `## Dependency:` section in the PR body. Calls nothing. → ADR 0001, D7. |

**Adding a check means editing `checks.yml` and the `## Tooling` block in `AGENTS.md`, in
the same commit.**

Two kinds of check stay out of the `check` job:

- **A check that needs the network or a credential.** `scripts/check_issue_umbrellas.py`
  runs on demand. → ADR 0001, D4.
- **A gate that reads the pull request itself.** `pr-closes.yml` and `pr-dependencies.yml`
  keep their own file, trigger and `concurrency` group: `checks.yml` also runs where no PR
  body exists. → ADR 0001, D3.

## Releases

A release is a tag on `main`, cut by hand; nothing in the pipeline publishes or tags.
→ ADR 0001, D6.

## Adding a check that touches history

**Never add a check that grades commits already on `main`.** A check scoped to the
commits in a PR is fine.

A check that grades files as they are now is fine **if the change that adds it also
brings those files into shape** — fix first, then check.

## What is deliberately not checked

Adherence: nothing here claims to measure it. A rule that is violated and matters becomes
a hook or a setting, never a better sentence.
