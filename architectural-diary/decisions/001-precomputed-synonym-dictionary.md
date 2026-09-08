# 001 — Precompute the synonym dictionary into a committed pickle

**When:** 2013-03-15 (initial form) → 2013-03-16 (generator script) →
2013-03-23 (final form). Commits: `3cbe5f1`, `3a4fcd7`, `b591be4`.

## Context

The service's core operation is "given `word` + POS class, list candidate
synonyms". WordNet can answer this at runtime via `wn.synsets(word, pos)`,
but that requires the corpus to be installed and parses database files on
every lookup — slow and fragile on a small 2013 Heroku dyno shared with the
web server.

## Decision

Build the entire mapping offline in `make_syn.py`: iterate
`wn.all_synsets()`, key by `<headword>.<pos>` (e.g. `verdict.n`), union the
lemma names of all synsets sharing a key, filter out entries that are empty
or contain only the headword itself, and cPickle the result as `syn.pkl`.
The request path (`syn/syn.py`) then does plain dict lookups with a stemmed
retry (`word[:-1] + "." + pos` before `word + "." + pos`) and returns
`[word]` on a miss.

A parallel `syn_json.pkl` (same dict, JSON-encoded values) was added on
03-22 — presumably for a lighter-weight consumer — but nothing in the repo
reads it. An earlier `syn.json` variant was emptied/deleted along the way
(the empty file is still tracked).

An optional push of the whole map into a hosted Redis (mset of the JSON
values) exists commented-out in `make_syn.py`; it was never enabled and was
explicitly skipped in the final refactor.

## Consequences

- Request-time synonym lookup is a dict hit: no corpus, no WordNet import,
  no exception paths beyond KeyError.
- The dictionary is only as fresh as the last regeneration; changing
  filtering rules requires rebuilding `syn.pkl` (~3.9 MB).
- `make_syn.py` embeds a hosted-Redis URL with a password in a comment —
  a hygiene problem flagged again in AGENTS.md.
- The final filter (`len(v) > 0 and headword not in v`) means singleton
  synsets whose only lemma is the headword are dropped — correct, since
  they can never produce a substitution.

## Related

- [002-backoff-tagger-chain.md](002-backoff-tagger-chain.md) — the other
  precomputed artifact.
- [006-vendored-wordnet-corpus.md](006-vendored-wordnet-corpus.md) — what
  happened when the runtime briefly *did* need the corpus.
