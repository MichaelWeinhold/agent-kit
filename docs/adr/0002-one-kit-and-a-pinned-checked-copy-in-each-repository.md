# 2. One kit, and a pinned, checked copy of it in each repository

- **Status:** Proposed
- **Date:** 2026-11-27
- **Issue:** #1

## Context

Three repositories run one workflow, built up over several hundred issues in the most
developed of them and copied into the other two in November 2026. Read on 2026-11-27, the
copies have drifted in both directions (issue 1, *Scope, as found*): a skill is behind the
base, a guard script differs by 44 lines per copy, a workflow pin is *ahead* of the base,
and the same rule cites different ADRs in different repositories. No copy is wrong on
purpose; each was improved where the work happened and the improvement stopped there.

Three smaller repositories have a `CLAUDE.md` only.

What the existing workflow already holds, and this decision has to keep:

- **A rule lives in the clone.** Any agent reads the markdown it finds there, and
  `CLAUDE.md` says never to write a rule that only works when one client loads it.
- **What must hold is a mechanism** — the commit guard, the rulesets, the PR gates — and
  the `## Tooling` block equals the CI `check` job.
- **Everything is reproducible from the repository's tip**, with versions pinned and
  Dependabot moving the pins.

## Decision

### D1 — The kit's own files are the payload, named in a manifest

This repository is worked by the shared workflow (ADR 0001), so its own skills, rules,
hook and guard scripts are the shared files. `agent-kit.toml` lists each shared path and
where it lands in a consumer. Anything not in the manifest stays here.

A shared file is written for any repository (`AGENTS.md`, architecture rule 1). Where it
needs a fact only the consumer has — its check list, its history directories, its
dependency manifests, its protected branches — it points at the consumer's `AGENTS.md` or
reads the consumer's `[tool.agent-kit]` table in `pyproject.toml`. It never holds the fact.

### D2 — A consumer holds a pinned copy, and a lock that records it

`scripts/agent_kit.py sync <consumer>`, run from a clean checkout of a tag here, writes
every shared file into the consumer and writes `agent-kit.lock`: the tag, its commit, and
each file's SHA-256. The change reaches the consumer as an ordinary pull request there, so
the consumer's own pipeline judges it.

`scripts/agent_kit.py` is itself a shared file, so every consumer carries the version of
the checker that matches its lock.

### D3 — Drift is a failing check, not a review comment

`uv run python scripts/agent_kit.py check` compares each locked file with its hash and
fails on an edited, missing or unlisted shared file. It needs no network, so it joins the
consumer's `## Tooling` block and its `check` job, and a session sees the failure before
CI does. An improvement found in a consumer is made here and synced back; the check makes
that the only way.

### D4 — PR gates are reusable workflows; the kit's version is one pin

`closing-references` and `dependencies` become `workflow_call` workflows here. A consumer
keeps a caller of a few lines, which `sync` writes with the locked commit, and which is
**not** a shared file. The action pins inside the gates live here, so Dependabot bumps
them once. The consumer's Dependabot ignores `MichaelWeinhold/agent-kit`, because `sync`
moves that pin together with the lock; two movers would disagree.

`checks.yml` stays the consumer's own, since its steps are the consumer's check list.

### D5 — The kit's ADRs travel with the copy

The ADRs that shared files cite are shared too, landing under `docs/agent-kit/adr/`. A
shared file cites them as `kit ADR <n>, D<m>`, so a consumer's own ADR numbering is never
borrowed. The base's process ADRs are ported here, product-free, and the base's copies
are marked superseded by the kit's.

### D6 — What stays in each repository

The `## Tooling` block and its `checks.yml`; the product's ADRs, architecture rules and
README; skills for its own host, device or cloud project; path-scoped rules about its own
code; its `.claude/settings.json`, which the instruction check still asserts.

### D7 — An update reaches every consumer as one pull request each

A release is a tag here (ADR 0001, D6). A skill here walks the rollout: for each local
checkout that holds an `agent-kit.lock`, cut a `chore/` branch, `sync`, run its checks,
and open the pull request. Consumers are found by their lock, so this public repository
names none of them.

### D8 — User-level client configuration is out of scope

The kit writes only inside a consumer's repository, never to a user's home directory.

### D9 — A repository adopts the kit, or stays light

A repository the operator still works on takes the kit through D2. One that is archived or
barely touched gets an `AGENTS.md` and a `CLAUDE.md` that is `@AGENTS.md`, and nothing
else. Which is which is the operator's call, asked per repository.

## Follow-ups

Filed as children of issue 1 once this ADR is accepted:

1. `agent-kit.toml`, `agent_kit.py sync` and `check`, with their tests.
2. The two gates as reusable workflows, and the caller `sync` writes.
3. The shared files read the consumer's facts from `[tool.agent-kit]` and `AGENTS.md`
   (D1): history directories, dependency manifests, protected branches, check names.
4. Port the base's process ADRs here, product-free (D5).
5. The base takes the kit — first, as the most developed copy.
6. The two other workflow repositories take the kit.
7. The light setup for the repositories the operator names (D9).
8. The rollout skill and the first tag (D7).

## Consequences

- An improvement to the workflow is one PR here and one generated PR per consumer, instead
  of one PR in whichever repository it was found in.
- A shared file can no longer be fixed in place in a consumer; the check refuses it. A
  real emergency fix is still possible — sync from a kit branch — and has to be followed
  by the kit PR.
- Every consumer carries a few hundred more lines it did not write, which its own checks
  measure like any other file.

## Alternatives considered

**A Claude Code plugin marketplace.** The kit as a plugin, enabled per repository in
`.claude/settings.json`. Rejected: the skills are not in the clone, so another agent never
sees them and `check_instructions.py` cannot measure them; only one client loads them; a
plugin cannot ship the guard scripts and workflows the pipeline needs; and per-repository
auto-install is unreliable enough that each clone would need a manual step. **Reopens
if** a plugin can be vendored into the clone at a pinned version and every agent client
reads that format.

**A git submodule.** Rejected: every clone, worktree and CI run has to fetch it, a
worktree created by the client does not initialise it, and a submodule's files can still
be edited in place without anything failing. **Reopens if** CI has to test a consumer
against an unreleased kit.

**Symlinks into a local checkout of the kit.** Rejected: CI and a fresh clone have no such
checkout, and the link pins nothing. **Reopens** never for files CI reads.

**A generator such as rulesync, or a third-party sync tool.** Rejected for now: it would
own the manifest, the lock and the check, which are a few hundred lines of standard-library
Python here, and it would enter as a package to argue under ADR 0001, D7. **Reopens if**
the consumers span several agent clients whose formats a generator already maps.

**Copies without a check** — today's state. Rejected: issue 1 measured where it leads.

**One monorepo for all projects.** Rejected: the repositories differ in visibility — one
is public — in language and in where they run. **Reopens** never on this ground alone.
