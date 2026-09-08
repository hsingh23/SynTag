# 002 — Train a five-stage backoff POS tagger offline and pickle it

**When:** 2013-03-16 (builder script committed), rules expanded 2013-03-17.
Commits: `3a4fcd7`, `b0746bc`.

## Context

Substitution quality depends on knowing each word's part of speech. NLTK
can tag with a simple regex or n-gram tagger, but training a bigram tagger
over Brown and Treebank takes minutes and lots of RAM — unacceptable inside
a web worker, and it would be repeated in every gunicorn worker.

## Decision

`make-syn-pos-tagger.py` trains one composite tagger as a chain of
backoffs, then cPickles it (twice: `syn-pos-tagger.pkl` and a `-bak` copy,
~5.7 MB each):

1. `RegexpTagger` — suffix patterns (`-ing` → vbg, `-ed` → vbd, `-able` →
   JJ, `-ness` → NN, `-ly` → RB, numbers → CD, articles → AT, default NN),
   itself backed by `DefaultTagger('n')`.
2. `UnigramTagger(model=lookup)` — a hand-built lexicon from every
   Brown-tagged word, extended with Treebank words not already present.
3. `BigramTagger` trained on Brown sentences.
4. `BigramTagger` trained on Treebank sentences.

Later, when the request path only needed Penn tags, the trained tagger's
regex rule for plural nouns (`.*s$`) was neutralized to an empty tag — the
unigram/bigram stages cover plurals better than the regex did.

## Consequences

- Tagging at request time is a pure in-memory chain walk; the ~5.7 MB model
  is memory-heavy but shared across workers via gunicorn `--preload`.
- Training cost is paid once per regeneration, not per deploy boot.
- The pickled tagger is NLTK-2.0.4-specific — it embeds that library's
  class layout and cannot be unpickled reliably under a different NLTK.
- Storing a `-bak` copy doubles the committed binary weight for little
  benefit (see [007-committed-binary-artifacts.md](007-committed-binary-artifacts.md)).
- The tagger emits Penn tags, which `syn/syn.py` then collapses to three
  WordNet classes (`n`, `v`, `a`) — the mapping lives in `simple_tags`,
  where adverbs are deliberately excluded and interjections (`uh`) are
  folded into nouns.
