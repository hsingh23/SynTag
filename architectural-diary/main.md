# Architectural diary — SynTag

An index of the design decisions behind SynTag, reconstructed in 2026 from
the code and the full commit history (originals: 24 commits by Harsh Singh,
2013-03-11 → 2013-03-24). Each entry records what was decided, when, why,
and what it cost.

The project compresses into two weeks: a scaffolded Django service that
substitutes WordNet synonyms into submitted sentences, deployed to Heroku,
with a heavy offline-precomputation strategy so the request path is pure
dictionary lookups.

## Decisions

| # | Decision | Commits (current SHAs) | Entry |
| --- | --- | --- | --- |
| 001 | Precompute the synonym dictionary into a committed pickle | `3cbe5f1`, `3a4fcd7`, `b591be4` | [decisions/001-precomputed-synonym-dictionary.md](decisions/001-precomputed-synonym-dictionary.md) |
| 002 | Train a five-stage backoff POS tagger offline and pickle it | `3a4fcd7`, `b0746bc` | [decisions/002-backoff-tagger-chain.md](decisions/002-backoff-tagger-chain.md) |
| 003 | One CSRF-exempt endpoint, plain text, param-routed | `3cbe5f1`, `79b30bd`, `a793c08`, `c8d69bd`, `b0746bc` | [decisions/003-http-api-surface.md](decisions/003-http-api-surface.md) |
| 004 | Tune the Heroku/gunicorn process model by trial and error | `75d65f4` … `09ecf9d`, `53e88af` | [decisions/004-heroku-deployment-tuning.md](decisions/004-heroku-deployment-tuning.md) |
| 005 | Preserve verb tense during substitution (tensify) — and its bug | `dbe2f3d`, `d1a1774`, `2a23c63` | [decisions/005-tense-preserving-substitution.md](decisions/005-tense-preserving-substitution.md) |
| 006 | Vendor the WordNet corpus, then stop needing it at runtime | `53e88af`, `b591be4` | [decisions/006-vendored-wordnet-corpus.md](decisions/006-vendored-wordnet-corpus.md) |
| 007 | Commit generated binary artifacts to the repo | `3cbe5f1`, `3a4fcd7`, `9534514` | [decisions/007-committed-binary-artifacts.md](decisions/007-committed-binary-artifacts.md) |
| 008 | Rewrite history to repair commit messages (2026) | — | [decisions/008-history-rewrite-2026.md](decisions/008-history-rewrite-2026.md) |

## Timeline at a glance

- **2013-03-11** — PHP placeholder scaffold (`.htaccess`, empty `index.php`).
- **2013-03-15** — Django 1.5 project scaffolded; synonym pipeline works
  locally; Heroku deploy iteration dominates the day (Procfile rewritten
  six times; CSRF exemption added, then its missing import fixed).
- **2013-03-16/17** — Tagged-text and `syn` endpoints added; `tensify()`
  introduced; the offline generator scripts (`make_syn.py`,
  `make-syn-pos-tagger.py`) finally committed alongside their artifacts.
- **2013-03-18 → 03-22** — Reliability week: the if/elif bug in `tensify`,
  a shipped SyntaxError and its same-day fix, the WordNet corpus vendored
  into the repo for the deploy, worker counts cut for memory.
- **2013-03-23/24** — The dict-only refactor: runtime WordNet removed, the
  request path reduced to `syn.pkl` lookups; empty-list crash guarded.
- **2026-09-08** — Documentation and history-repair pass (this diary,
  README, AGENTS.md, CHANGELOG.md, `prompt.md`; messages-only rewrite).
