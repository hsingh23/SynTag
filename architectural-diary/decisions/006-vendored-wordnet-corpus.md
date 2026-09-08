# 006 — Vendor the WordNet corpus, then stop needing it at runtime

**When:** 2013-03-22 vendored; 2013-03-23 made unnecessary. Commits:
`53e88af`, `b591be4`.

## Context

On 03-22 the request path still contained a WordNet fallback: when a word
was missing from `syn.pkl`, it called `wn.synsets(word, pos)` live. That
requires the WordNet database files wherever the app runs. Heroku dynos
have no `nltk_data`; the standard fix (`nltk.download()`) needs network
access and a writable home at boot. The commit message — "maybe this will
fix it" — captures the debugging mood.

## Decision (two-step)

1. **Vendor** (`53e88af`): commit the WordNet 3.0 database flat files
   (`data.*`, `index.*`, `*.exc`, `cntlist.rev`, `lexnames` — ~155k lines)
   under `corpora/wordnet/` so the deployed app always finds them, and cut
   gunicorn workers 8 → 4 to offset the slug's memory cost. The same commit
   accidentally uncommented a prose line in `syn/syn.py` (SyntaxError),
   fixed nine minutes later in the next commit (`b22105b`).
2. **Eliminate** (`b591be4`, the next day): the dict-only refactor removed
   the runtime `wn` import and the fallback entirely — unknown words simply
   pass through. With the request path pure-dict, the vendored corpus
   became dead weight that was left in place anyway.

## Consequences

- Request handling no longer touches the filesystem beyond the two pickles;
  boot is deterministic regardless of the host's NLTK setup.
- The repo permanently carries ~25 MB of corpus text that nothing imports —
  harmless but misleading to readers (README/AGENTS.md call this out).
- The enable/disable/enable/disable sequence of the fallback across
  03-22 (`5fd5196` disable, `53e88af` re-enable, `b591be4` remove) shows a
  real evaluation happening: the author judged the on-the-fly synset unions
  "unreliable in a funny way" (their comment, preserved in the code) and
  ultimately chose coverage-loss over noise.
