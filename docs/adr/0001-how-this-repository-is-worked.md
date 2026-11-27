# 1. How this repository is worked

- **Status:** Accepted
- **Date:** 2026-11-27
- **Recorded with:** the bootstrap, issue 2. This ADR answers no research issue; it writes
  down the process the repository starts with, so that changing it is a decision too.

## Context

This repository holds a workflow for repositories whose code is mostly written by coding
agents, with one person as the feedback loop. It is worked by that same workflow, taken
from the most developed of the repositories that already run it. Two things follow.

- **An agent reconstructs a procedure from memory unless it is told where the procedure
  is**, and a rule that matters has to hold whether or not it was read.
- **What this repository decides, every repository that takes it inherits**, so a rule
  here is argued once, in writing, and kept free of any one product.

How other repositories take the kit is issue 1's decision, not this one.

## Decisions

### D1. Instruction files are markdown, short, and in one place each

`AGENTS.md` holds invariants and commands and is read by any agent; `CLAUDE.md` imports it
with `@AGENTS.md` and adds only what is specific to Claude Code. Rationale goes in
`README.md`, decisions in `docs/adr/`, procedures in skills, rules for one directory in a
path-scoped rule. Nothing is written in full twice.

`scripts/check_instructions.py` holds the sizes: 200 lines per always-on file and 270 for
the pair, 500 per skill and 200 per rule, 1000 for everything loaded on demand, and prose
wrapped at 90 characters. A line ceiling alone is met by making lines longer; the width
limit closes that.

**Rejected:** XML-structured or YAML rule files — no client reads them as anything but
text, and markdown with frontmatter is what every agent client ships. *Reopens if* a
client defines a structured format it enforces.

### D2. Every change is issue → branch → PR → green → squash merge

One issue per change, groomed before a branch is cut: the original request verbatim, the
scope as found, and a *Done when* that can be checked. Branches are `feat/`, `fix/` or
`chore/`. Commits are one line, `Feat(#n): …`, with the human as the author and no AI
trailer. `.claude/hooks/git_commit_guard.py` refuses anything else, so the rule holds
without being read.

A `bug` starts with a test that fails for the bug's reason, committed with the fix.

**Rejected:** a human review gate. There is one maintainer; a required approval would be
self-approval. *Reopens when* a second person has push access.

### D3. The local checks and the CI job are one list

The `## Tooling` block in `AGENTS.md` and the `check` job in `checks.yml` are compared for
equality, so the checks a session runs before a push are the checks the pipeline confirms.
Gates that read the pull request itself — its closing references and its new packages —
live in their own workflows, because they must re-run when the description is edited.

`pr-closes.yml` grants `issues: read`: without it, GitHub's GraphQL API returns an empty
list of closing references instead of an error, and the gate passes everything.

### D4. A research issue ends in an ADR, and its follow-ups are its children

No implementation starts before its ADR is accepted. Each change the ADR recommends is
filed as a sub-issue of the research issue, which carries ☂️ and closes with its last
child. `scripts/check_issue_umbrellas.py` reports orphans and parents owed a close.

### D5. Parallel sessions do not share a branch

A session that finds another in the checkout works in its own worktree. Issues are claimed
with `scripts/next_issue.py`, which writes the claim as a ref under `refs/claims/` on the
remote, so two sessions cannot take the same issue. A content read in a shared checkout
names a revision, because a peer may have switched the branch underneath it.

### D6. `main` is the only branch, and a release is a tag

`main` takes squash or rebase merges, under a ruleset with no bypass for anyone. Nothing
here is deployed: a repository that takes the kit pins a tag or a commit of `main`, so a
tag is the release and is cut by hand.

**Rejected:** a `production` branch like the repositories that run a host or a device.
There is nothing to promote to; a tag pins exactly one commit, which is what a consumer
needs. *Reopens if* the kit grows something that runs somewhere on its own.

### D7. A package comes in only when it is worth it

The scripts use the standard library only (`AGENTS.md`, architecture rule 2), so a package
can enter only as a development tool. The pull request that adds one carries a
`## Dependency: <name>` section answering six questions: what it replaces, who publishes
it, whether it is maintained, its licence, what it pulls in, and where it runs. A version
bump needs no section. `pr-dependencies.yml` enforces the section.

### D8. Hand-made state is written down as state, and its history apart

If something here is ever done by hand outside the repository, `docs/manual-steps/` holds
how to reproduce it — the commands, one check each, the undo — and what a run printed goes
to a history file beside it. `docs/MANUAL_STEPS.md` indexes them, with a ceiling of 100
lines and 250 per file. `check_instructions.py` holds the ceilings whether or not the
directory exists, because a repository that takes the kit may have one.

### D9. The client's settings are checked, not trusted

`.claude/settings.json` turns off the client's own git instructions and every attribution
key, and sets `autoCompactWindow` to 200000. The attribution keys differ in type — two are
strings, one is a boolean — and a value of the wrong type is discarded without a warning,
so `check_instructions.py` asserts each value and its type. A session ends after a merge
with `/clear`, so the next issue starts inside that window.
