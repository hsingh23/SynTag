# 008 — Rewrite history to repair commit messages (2026)

**When:** 2026-09-08. No original commit; this documentation pass is its
own change on top of the rewritten `master`.

## Context

All 24 original commits carried placeholder messages — "yo" (six times),
"Yolo"/"yolo" (three), "work damit", "maybe this will fix it", "ch ch ch
changes", "Not really fixing issue". The history was archaeologically
interesting but unusable: `git log` told you nothing, and tools that walk
history for context (code review, bisection, AI agents) got noise.

## Decision

Perform a **messages-only** history rewrite on `master`:

1. Analyze every commit (patch + stat) and draft a conventional-commit
   replacement that describes what the change actually did — verified
   against the diffs, including uncomfortable facts (a shipped SyntaxError,
   a decorator applied without its import, a fix that "mitigates but does
   not resolve").
2. Apply with `git filter-branch --msg-filter`, substituting approved
   message files keyed by original SHA; any commit without a replacement
   passes through verbatim.
3. Force-push with `--force-with-lease`.

## Guardrails used

- Tree hashes compared before/after: identical (`92308e63…`), proving
   content, authors, and dates were untouched — only messages (and hence
   commit SHAs) changed.
- A local-only backup branch (`backup/pre-docs-20260908`) preserves the
   original chain for recovery; it was deliberately never pushed.
- Commit count verified unchanged (24).
- The many remote `snyk-fix/*` branches were left untouched; they still
   point at pre-rewrite SHAs and are expected to diverge.

## Consequences

- `git log` is now a readable narrative of the project's two weeks.
- All pre-2026 external references to SynTag commit SHAs (PRs, Snyk
  branches, old links) no longer resolve against `master`.
- Anyone with a pre-rewrite clone must `git fetch && git reset --hard
  origin/master` (after stashing local work).
- This diary, `CHANGELOG.md`, and the analyses behind each message
  constitute the paper trail for what was changed and why.
