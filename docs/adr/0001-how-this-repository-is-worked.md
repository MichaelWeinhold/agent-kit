# 1. How this repository is worked

- **Status:** Accepted
- **Date:** 2026-11-27

In the context of a workflow kit whose code agents write and one person steers, facing
agents that rebuild a procedure from memory and repositories that inherit every rule, we
decided for short markdown instruction files, one path from issue to squash merge held by
a commit guard and a ruleset, and one list of checks run locally and in CI, and against a
human review gate and a release branch, to achieve rules that hold whether or not an agent
has read them, accepting an issue, a branch and a green pipeline for every change.

## Context

- **The kit is worked by its own workflow**, taken from the most developed of the
  repositories that already run it (issue 2).
- **An agent reconstructs a procedure from memory unless it is told where the procedure
  is**, so a rule that matters is held by a mechanism as well as written down.
- **Every repository that takes the kit inherits what is decided here**, so a rule is
  argued once, in writing, and fits any product (`AGENTS.md`, architecture rule 1).
- **How other repositories take the kit** is issue 1's question.

## Decision

### D1 — Instruction files are markdown, short, and each thing has one home

`AGENTS.md` holds invariants and commands, for any agent. `CLAUDE.md` imports it with
`@AGENTS.md` and adds what is specific to Claude Code. Rationale goes in `README.md`,
decisions in `docs/adr/`, procedures in skills, a rule for one directory in a path-scoped
rule. Each thing is written in full once, and every other mention is a pointer.

`scripts/check_instructions.py` holds the sizes: 200 lines per always-on file and 270 for
the pair, 500 per skill and 200 per rule, 1000 for everything loaded on demand. Prose
wraps at 90 characters, so a line ceiling measures content rather than line length.

### D2 — Every change goes issue → branch → PR → green → squash merge

Each change has its own issue, groomed before a branch is cut: the original request
verbatim, the scope as found, and a *Done when* that can be checked. Branches are `feat/`,
`fix/` or `chore/`. A commit is one line, `Feat(#n): …`, authored by the human alone.
`.claude/hooks/git_commit_guard.py` holds this whether or not it was read.

A `bug` fix starts with a test that fails for the bug's reason, committed with the fix.

### D3 — The local checks and the CI job are one list

The `## Tooling` block in `AGENTS.md` and the `check` job in `checks.yml` are compared for
equality, so the checks a session runs before a push are the checks the pipeline confirms.
Gates that read the pull request itself — its closing references and its new packages —
run in their own workflows, which re-run when the description is edited.

`pr-closes.yml` grants `issues: read`. Without it, GitHub's GraphQL API returns an empty
list of closing references instead of an error, and the gate would pass everything.

### D4 — A research issue ends in an ADR, and its follow-ups are its children

Implementation starts once its ADR is accepted. Each change the ADR recommends is a
sub-issue of the research issue, which carries ☂️ and closes with its last child.
`scripts/check_issue_umbrellas.py` reports orphans and parents owed a close.

### D5 — Each parallel session works on its own branch

A session that finds another in the checkout works in its own worktree. A session claims
its issue with `scripts/next_issue.py`, which writes the claim as a ref under
`refs/claims/` on the remote, so each issue has one holder. A content read in a shared
checkout names a revision, since a peer may switch the branch underneath it.

### D6 — `main` is the one branch, and a release is a tag

`main` takes squash or rebase merges, under a ruleset that binds everyone. Nothing here is
deployed: a repository that takes the kit pins a tag or a commit of `main`, so a tag, cut
by hand, is the release.

### D7 — A package comes in when it is worth it

The scripts use the standard library only (`AGENTS.md`, architecture rule 2), so a package
enters as a development tool. The pull request that adds one carries a
`## Dependency: <name>` section answering six questions: what it replaces, who publishes
it, whether it is maintained, its licence, what it pulls in, and where it runs. A version
bump goes in as it is. `pr-dependencies.yml` enforces the section.

### D8 — Hand-made state is written down as state, with its history beside it

Whatever is done by hand outside the repository is reproducible from `docs/manual-steps/`:
the commands, one check each, and the undo. What a run printed goes to a history file
beside it. `docs/MANUAL_STEPS.md` indexes them within 100 lines, and each file stays
within 250. `check_instructions.py` holds the ceilings whether or not the directory
exists, since a repository that takes the kit may have one.

### D9 — The client's settings are checked, not trusted

`.claude/settings.json` turns off the client's own git instructions and every attribution
key, and sets `autoCompactWindow` to 200000. Two attribution keys are strings and one is a
boolean, and the client discards a value of the wrong type silently, so
`check_instructions.py` asserts each value and its type. A session ends after a merge with
`/clear`, so the next issue starts inside that window.

## Rejected alternatives

| Option | For | Why not | Reopens if |
|---|---|---|---|
| XML-structured or YAML rule files | D1 | clients read them as text; markdown with frontmatter is what every agent client ships | a client defines a structured format it enforces |
| A human review gate | D2 | with one maintainer, a required approval is self-approval | a second person has push access |
| A `production` branch, as repositories that run a host or a device keep | D6 | there is nothing to promote; a tag pins exactly the commit a consumer needs | the kit grows something that runs somewhere on its own |

D3, D4, D5, D7, D8 and D9 weighed no alternative: they record the process the repository
started with.

## Consequences

- **Good:** a rule that matters holds by a hook, a ruleset or a check, whether or not an
  agent has read it.
- **Good:** a repository that takes the kit inherits rules that were argued once, in
  writing.
- **Bad:** every change, a typo included, costs an issue, a branch and a green pipeline.
- **Bad:** the size ceilings force a split before a file feels full.

## Confirmation

- D1, D8, D9: `scripts/check_instructions.py`.
- D2: `.claude/hooks/git_commit_guard.py` and the branch ruleset.
- D3: `scripts/check_instructions.py`, which compares the two lists and the gates'
  permissions.
- D4: `scripts/check_issue_umbrellas.py`.
- D5: `scripts/next_issue.py`, and `feature-lifecycle`, step 2.
- D6: the branch ruleset, as `AGENTS.md`, *How work happens here*, describes it.
- D7: `pr-dependencies.yml`.
