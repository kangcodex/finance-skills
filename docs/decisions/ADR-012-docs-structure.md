# ADR-012: Documentation artifacts live in `docs/`; tracking is local markdown for now

## Status
Accepted

## Date
2026-07-28

## Context
The user wants ideation output as ADRs, issues, PRDs in `docs/`. The `finance-skills/` repo is at `/Users/kangxunwong/Hobby/Coding/CustomSkills/finance-skills/` and has `docs/{api,decisions,design,ORCHESTRATION.md}`.

The question: where do issues and PRDs live in this repo, and how do they relate to GitHub Issues if/when the project gets one?

## Decision

| Artifact | Location | Format | Why |
|----------|----------|--------|-----|
| ADRs (architectural decisions) | `docs/decisions/ADR-NNN-*.md` | Existing format (per `ADR-001` and `ADR-002`) | Already established. |
| Design docs (architecture, risk) | `docs/design/*.md` | Free-form markdown with headers + diagrams | Co-located with related ADRs. |
| Orchestration / playbook | `docs/ORCHESTRATION.md` (extend existing) | Single file, sections per skill | Already exists. |
| PRDs (one per skill) | `docs/prds/<skill-name>.md` | Standard PRD template (see below) | Each skill is its own shippable unit. |
| Issues | `docs/issues/` as markdown files (`<NNN>-<slug>.md`) | Numbered, status header | Until the project gets a real tracker, file-as-issue. |
| Decision→issue links | Frontmatter in each issue file (`related-adrs: [ADR-NNN, ...]`) | YAML | Traceability. |

**No GitHub Issues dependency** for v1. The user can copy `docs/issues/*.md` to GitHub Issues when ready; the format is intentionally close.

**File-as-issue template** (`docs/issues/000-template.md`):
```markdown
---
id: NNN
title: <short>
status: open | in-progress | blocked | done
related-adrs: [ADR-NNN, ...]
related-prds: [<skill-name>]
created: 2026-07-28
---

# NNN: <title>

## Context
<why this is an issue>

## Acceptance criteria
- [ ] <verifiable>
- [ ] <verifiable>

## Notes
<freeform>
```

## Consequences
Positive:
- Zero tool dependency. `git diff docs/` is the entire history of decisions and work.
- Existing ADR format preserved.
- Easy to migrate to GitHub Issues / Linear / Jira later by copying the files.
- The user can read the whole state of the project in one tree.

Negative:
- No automation around issues (no `/board`, no assignees, no due dates beyond what's in the file). Fine for one person.
- Risk of staleness — `docs/issues/` is not auto-closed. Mitigation: a quarterly prune step (not yet built).

## Alternatives considered
- **GitHub Issues from the start.** Rejected: requires a GitHub repo, and the user hasn't set one up. Easy to do later.
- **Linear / Jira.** Rejected: same reason.
- **Single `TODO.md` at root.** Rejected: doesn't scale; can't link from ADRs.

## See also
- ADR-001 and ADR-002 — the remaining finance-skill architecture decisions.
