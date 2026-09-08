# 007 — Commit generated binary artifacts to the repository

**When:** 2013-03-15 onward. Commits: `3cbe5f1`, `3a4fcd7`, `9534514`.

## Context

The service depends on two large derived artifacts — the synonym dictionary
(`syn.pkl`, ~3.9 MB) and the POS tagger (`syn-pos-tagger.pkl`, ~5.7 MB) —
plus, briefly, `syn.json`. Regenerating them requires the Brown and
Treebank corpora, the WordNet database, and several minutes of training.
The deploy target (Heroku) builds from the repo with no other source of
truth.

## Decision

Commit the pickles (and their intermediate `syn_json.pkl` sibling, added
03-22). Treat `make_syn.py` / `make-syn-pos-tagger.py` as provenance, not
as a build step: the repo *is* the artifact store. A `-bak` copy of the
tagger pickle is also tracked. Compiled `.pyc` files, by contrast, were
explicitly untracked and gitignored on 03-16.

## Consequences

**Pros**
- Deploys and clones are self-contained: no corpus downloads, no training,
  reproducible boots on 2013-era infrastructure.
- The exact data the 2013 service served is preserved bit-for-bit — which
  is also why the project still "runs" (on Python 2) today.

**Cons**
- ~15 MB of binaries (plus a duplicate `-bak`) bloats every clone and makes
  history-heavy operations slow; each regeneration is another multi-MB blob.
- Pickles are interpreter- and library-version-bound (cPickle + NLTK 2.0.4
  class layouts); the artifacts double as an implicit version pin.
- Risk surface: a maliciously swapped pickle executes code on load. Fine
  for a personal 2013 project; a real concern for anything revived.

A modern take would store artifacts in release storage (or an LFS layer)
and treat the generator scripts as CI. For a time-capsule repo, the
original choice stands.
