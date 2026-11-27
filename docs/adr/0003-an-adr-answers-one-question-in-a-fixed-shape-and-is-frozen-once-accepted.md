# 3. An ADR answers one question, in a fixed shape, and is frozen once accepted

- **Status:** Proposed
- **Date:** 2026-11-27
- **Issue:** #5

## Context

Nothing defines what an ADR here looks like, so each copies the last. ADR 0001 and ADR
0002 already differ in header (`Recorded with:` against `Issue:`), heading (`Decisions`
against `Decision`) and where rejected alternatives sit; six of 0001's nine decisions name
none. In the base repository the kit was taken from, the drift went further: accepted ADRs
amended in place up to eight times, statuses such as "D2 and D4 superseded, D6 amended",
and records of up to 226 lines that read as a current spec rather than a decision.

Agents read these records more often than the operator, and every rule cites `ADR n, Dm`.

What practice agrees on, as of November 2026:

- **Short, one decision per file, numbered, markdown beside the code** — Nygard, Fowler,
  MADR 4, AWS, Microsoft, Google Cloud.
- **Append-only**: a changed decision is a new record superseding the old, linked both
  ways — AWS, Microsoft, Fowler. The UK GDS framework (2025) alone asks for updates.
- **A fixed status** (MADR, AWS); **the options weighed** (MADR, Microsoft, Google);
  **what triggers a re-evaluation** (Fowler); **how compliance is confirmed** (MADR 4).
- **For agents**: an entry point in `AGENTS.md`, an index, and a status that is a field,
  not prose (Netflix, QCon SF 2026). In controlled trials, agents follow repository
  precedent over their defaults, and a rule the harness loads over code examples — 117 of
  120 joint successes against 0 of 120 (Zhu et al., 2026).

## Decision

### D1 — One template: MADR's core, in this repository's terms

Every ADR is `docs/adr/NNNN-<slug>.md`, with these parts in this order:

| Part | Holds | Required |
|---|---|---|
| `# N. <title>` | the decision as a statement, not a topic | always |
| header | `Status`, `Date`, `Issue`; `Supersedes`, `Superseded in part` when they apply | always |
| `## Context` | the problem, its forces, what was found | always |
| `## Decision` | `### D1 — …` onward, each opening with its decision in one sentence | always |
| `## Rejected alternatives` | each option, why not, and **Reopens if** | always |
| `## Consequences` | what gets better and what gets worse | always |
| `## Confirmation` | per decision, what holds it or which file states it | always |
| `## Follow-ups` | the changes filed as sub-issues | research |
| `## Sources` | what was read, linked | research |

The header stays bulleted bold fields, not YAML: frontmatter holds only a field a client
reads (`.claude/rules/instruction-files.md`), and `check_issue_umbrellas.py` parses
`- **Issue:** #<n>`. `docs/adr/template.md` holds the skeleton.

### D2 — An ADR answers one question; D1…Dn are the parts of its answer

A research issue that holds independent questions gets one ADR each. D-numbers stay, so
rules keep citing `ADR n, Dm`. A part that could be superseded while the rest stands
belongs in its own ADR.

### D3 — An accepted ADR is frozen

After acceptance an ADR changes only in its header, a broken link or a typo. A changed
decision is a new ADR with `Supersedes: ADR n`, or `ADR n, Dm` for one part. The old one's
status becomes `Superseded by ADR m`; for one part, its header gains
`Superseded in part: Dm by ADR m` and that part's heading the same note. No "Amended by"
paragraphs: how something works *now* belongs in `README.md` or the instruction files.

### D4 — Status is a fixed value, and acceptance is the operator's commit

The values are `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR NNNN`.
An ADR is written `Proposed` on its pull request and becomes `Accepted` or `Rejected` only
when the operator says so, by a commit on that pull request setting the value and `Date`;
then it merges. A rejected ADR merges too, so its reasoning stays in the log. `main` never
holds a `Proposed` ADR. `Date` is the last status change.

### D5 — An ADR fits in 150 lines

Everything above `## Sources` fits in 150 lines at 90 characters, about three pages.
Fowler asks for "a single page", Microsoft for "pithy"; an agent reads the record whole.
One that does not fit holds more than one question (D2).

### D6 — An index, written by hand and checked

`docs/adr/README.md` lists each ADR's number, title and status, one line each, checked
against the files as `docs/MANUAL_STEPS.md` is. `AGENTS.md` sends an agent there first.

### D7 — A script holds the shape, a pull-request gate holds the freezing

`scripts/check_adrs.py` joins the local checks: file name, header fields and values, parts
in order, the ceiling, the index. A pull-request gate fails while an ADR in the diff is
`Proposed`, and when an accepted ADR on the base branch changes outside its header.

### D8 — A rule an agent must follow is in an instruction file; the ADR holds why

A directive lives in `AGENTS.md`, a skill or a path rule, with `→ ADR n, Dm`, and never
only in an ADR; `## Confirmation` names where. The trials above are why: an agent follows
a rule its harness loads, not one in a file it might open.

### D9 — ADR 0002 takes the shape before acceptance; ADR 0001 is reshaped once

ADR 0002 is still `Proposed`, so it is rewritten before the operator decides on it. ADR
0001 is reshaped once, in the pull request that brings in `check_adrs.py`, with nothing it
decides changed; a decision that weighed no alternative says so rather than invent one.

## Rejected alternatives

- **MADR 4 verbatim** — its YAML front matter breaks the instruction-file rule and the
  audit's header, and pros and cons per option double the length without saying when to
  reconsider. **Reopens if** a tool the kit adopts reads that front matter.
- **Nygard's five parts** — no alternatives and no confirmation. **Reopens** never.
- **Structured records (YADR)** — rules here are markdown (ADR 0001, D1). **Reopens if** a
  client or harness consumes them.
- **Living records, updated in place**, as GDS asks — what turned the base's ADRs into
  specs. **Reopens if** a supersession chain passes three hops.
- **One decision per file, no D-numbers** — every rule cites `ADR n, Dm`. **Reopens if**
  an ADR collects two `Superseded in part` lines.
- **Decisions in commit trailers** (Lore) — a commit here is one line, and the proposal is
  untested. **Reopens if** a study shows agents use them.
- **A generated index** (adr-tools, Log4brains) — a tool outside `git` and `gh`.
  **Reopens if** the log passes 50 records.
- **`Proposed` as a pull-request state only** — an agent reading a branch has to see that
  the ADR is not in force. **Reopens** never.
- **A confidence field** (Microsoft, Fowler) — the *Reopens if* clause already says when
  to look again. **Reopens if** the operator accepts a decision as a guess.
- **"AI usage notes"** (Netflix) — D8 puts the directive where the harness loads it.
  **Reopens if** agents act on an ADR's wording over the rule that cites it.

## Consequences

- An agent finds an ADR's decision, status and reopen condition by position.
- A changed decision costs a new ADR, not a paragraph; the log grows and stays true.
- Two more checks, and an ADR pull request stays red until the operator decides.

## Confirmation

- D1, D5, D6: `scripts/check_adrs.py`, in the `## Tooling` block and the `check` job.
- D3, D4: the pull-request gate of D7, required by the ruleset.
- D2, D8: by reading — `AGENTS.md`, *Where a new rule goes*, and `grooming-an-issue`.
- D9: the two pull requests it names.

## Follow-ups

Filed as sub-issues of issue 5 once this ADR is accepted:

1. `docs/adr/template.md` and `docs/adr/README.md`; `AGENTS.md`, `grooming-an-issue` and
   `feature-lifecycle` point at them and name the statuses (D1, D4, D6, D8).
2. `scripts/check_adrs.py` with tests, in the local checks and `checks.yml`, with ADR 0001
   reshaped in the same pull request (D1, D5, D6, D7, D9).
3. The pull-request gate for `Proposed` and frozen ADRs, required by the ruleset (D7).
4. ADR 0002 rewritten into the shape, on issue 1's pull request (D9).

## Sources

Read on 2026-11-27.

- M. Fowler, [Architecture Decision Record](https://www.martinfowler.com/bliki/ArchitectureDecisionRecord.html),
  2026-03-24.
- [MADR](https://adr.github.io/madr/) 4.0.0, 2024-09-17, and its
  [develop template](https://raw.githubusercontent.com/adr/madr/develop/template/adr-template.md).
- [ADR templates](https://adr.github.io/adr-templates): Nygard, MADR, Y-statements.
- AWS Prescriptive Guidance, [ADR process](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html)
  and [best practices](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/best-practices.html).
- Microsoft, [Architecture decision record](https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record),
  2026-04-10.
- Google Cloud, [Architecture decision records](https://docs.cloud.google.com/architecture/architecture-decision-records).
- UK GDS, [Architectural decision record framework](https://www.gov.uk/government/publications/architectural-decision-record-framework/architectural-decision-record-framework),
  2025-11-04.
- InfoQ, [Netflix at QCon SF 2026: retrofitting the SDLC for AI coding agents](https://www.infoq.com/news/2026/11/netflix-sdlc-ai-coding-agents/),
  2026-11-23.
- Zhu et al., [Precedent or Intent? What coding agents follow when evolving existing code](https://arxiv.org/abs/2610.38244),
  2026-10-28.
- Stetsenko, [Lore: git commit messages as a knowledge protocol for coding agents](https://arxiv.org/abs/2603.15566),
  2026-03-16.
- N. Jain, [ADRs for AI coding agents](https://dev.to/naman_here/adrs-for-ai-coding-agents-how-to-make-every-agent-read-architecture-decisions-3he4),
  a vendor's post, read for its practice.
