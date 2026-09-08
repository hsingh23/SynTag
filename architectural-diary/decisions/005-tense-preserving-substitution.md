# 005 — Preserve verb tense during substitution (tensify), and its bug

**When:** 2016-03-16 introduced as "context syn"; control-flow fixed
2013-03-22; downstream guarded 2013-03-24. Commits: `dbe2f3d`, `d1a1774`,
`2a23c63`.

## Context

Synonym substitution is grammatically jarring for verbs: swapping "delivered"
for "handed over" is fine, but swapping it for an uninflected lemma
("hand over") or the wrong tense ("hands over") breaks the sentence. The
pickled dictionary stores lemmas, so something must re-inflect them.

## Decision

Add `tensify(syn_list, pos)` to `syn/syn.py` and route verb lookups through
it from `filtered_for_syn`. For each target tense it tries, per candidate:

- exact match — re-tag the candidate with `tagger.tag[candidate]` and keep
  it if the tag equals the target tense;
- morphology rules — strip/rename suffixes (`-ing` ↔ `-ed`, `-s`/`-es`
  handling for vbz, `+ed`/`+ing`/`+es` for bare forms);
- a `real_word()` validation hook, short-circuited with `if True or`.

Only nouns (`nn`, `nns`, `n`, later `uh`), verbs, and adjectives are
substituted at all; adverb handling exists in commented-out form.

## The bug

Every loop in `tensify` iterates `s_list` — a local list initialized empty
and never populated from the `syn_list` argument (`for word, tag in ((a,
tagger.tag[a]) for a in s_list)`). The function therefore always returns an
empty list, and `make_sentence` later hits empty candidates when choosing.
History shows the response was palliative, not curative:

- `d1a1774` (03-22) fixed the adjacent `if`/`if`/`else` chain to `elif` so
  the branches are mutually exclusive and non-verb positions return the
  input unchanged — necessary, but the loops still walk an empty list.
- `2a23c63` (03-24) wrapped `choice(a)` in try/except so the empties only
  silently drop the word. The commit's own message admits: "Not really
  fixing issue."

## Consequences

- As shipped, verb candidates are effectively discarded by `tensify` and
  the word is dropped from the output sentence; the service "works" because
  failures are swallowed.
- The fix is one line per loop (`for a in syn_list`), which makes this a
  good first contribution for anyone reviving the project.
- `real_word()` is referenced but never defined; it survives only because
  `if True or` short-circuits.
- `tagger.tag[a]` assumes every candidate is a known key of the unigram
  model — another latent KeyError once the loops are actually fed.
