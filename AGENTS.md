# AGENTS.md — working guide for SynTag

Guidance for coding agents (and humans) making changes in this repository.

## What this is

A 2013 Django 1.5 + NLTK web service that rewrites sentences with random
WordNet synonyms. Python 2.7-era code. Treat it as a time capsule: prefer
faithful fixes over modernization unless the task says otherwise.

## Commands

```bash
# Run (Python 2.7 era)
pip install -r requirements.txt
python manage.py runserver                       # dev server, port 8000
python manage.py run_gunicorn -b 0.0.0.0:$PORT -w 4 --preload   # prod form

# Regenerate the committed model artifacts (requires local NLTK corpora)
python make_syn.py                               # → syn.pkl, syn_json.pkl
python make-syn-pos-tagger.py                    # → syn-pos-tagger.pkl (+ -bak)

# Test the pipeline end-to-end (server must be running)
curl -X POST -d "sent=The judge delivered the verdict" http://localhost:8000/
curl --get --data-urlencode "tag=The judge delivered the verdict" http://localhost:8000/
curl --get --data-urlencode "syn=quick brown fox" --data "p=n" http://localhost:8000/

# Django's stub test suite (placeholder only, asserts 1+1)
python manage.py test syn
```

## Architecture map

```
word_tools/settings.py   Django 1.5 config; INSTALLED_APPS includes gunicorn
word_tools/urls.py       Routes ^$ → syn.views.home (the only URL)
syn/views.py             @csrf_exempt home(): dispatches on request params
                         sent | tag | syn (+p) → plain-text HttpResponse
syn/syn.py               The whole NLP pipeline (module-level pickle loads):
                         tagged() → filtered_for_syn() → make_sentence()
                         helpers: get_syn_for_word_pair(), tensify()
make_syn.py              Offline: WordNet synsets → dict keyed "word.pos"
                         → syn.pkl (pickle) + syn_json.pkl (JSON values)
make-syn-pos-tagger.py   Offline: RegexpTagger → DefaultTagger('n') →
                         UnigramTagger(Brown+Treebank lookup) →
                         BigramTagger(Brown) → BigramTagger(Treebank) → pickle
corpora/wordnet/         Vendored WordNet 3.0 files (runtime no longer
                         reads them after the dict-only refactor)
syn.pkl / syn-pos-tagger.pkl   Committed artifacts the request path loads
```

Request path loads both pickles once at import time (hence gunicorn
`--preload`: load once, then fork workers).

## Conventions

- Conventional Commits subjects (imperative, <=72 chars) with a body that
  explains why — see `CHANGELOG.md` for the house style after the 2026
  message cleanup.
- Python 2 idioms are intentional (`iteritems`, `cPickle`,
  `request.REQUEST`); don't "fix" them piecemeal — a real port would be its
  own coordinated change.
- POS tag handling maps Penn Treebank tags to three WordNet classes in
  `simple_tags` (`n`, `v`, `a`); interjections (`uh`) count as nouns,
  adverbs are deliberately excluded.
- Generated artifacts (`*.pkl`) are committed on purpose; if you change
  `make_syn.py` or `make-syn-pos-tagger.py`, regenerate and commit the
  pickles in the same change.

## Gotchas

- **Python 2 only.** `print`-era code, `cPickle`, `urlparse`,
  `nltk.EdgeWidget`-era APIs. Do not run with Python 3.
- **`syn/syn.py` loads pickles by relative path** (`open("syn.pkl")`), so
  the working directory must be the repo root — true under `manage.py`, but
  not if you import the module from elsewhere.
- **Known bug: `tensify()` iterates an empty list.** Its loops walk `s_list`
  (initialized empty, never filled from `syn_list`), so tense re-conjugation
  currently returns nothing — `make_sentence`'s `choice()` on the resulting
  empties is why the try/except guard exists. See
  `architectural-diary/decisions/005-tense-preserving-substitution.md`.
- **`syn.json` is an empty leftover file**; the JSON variant that matters is
  `syn_json.pkl`. Nothing reads `syn.json`.
- **`syn/syn.py` had a mid-history SyntaxError window** (2013-03-22, fixed
  same day) — if you check out that day's commits, expect import failures.
- **Secrets hygiene:** `word_tools/settings.py` contains a hardcoded Django
  `SECRET_KEY`, and `make_syn.py` has a commented-out hosted-Redis URL with
  an embedded password. Never copy these values into new code, docs, or
  commits; move them to environment variables if you touch either file.
- **Large binaries are tracked** (~5.7 MB tagger pickle, ~3.9 MB synonym
  pickle, ~25 MB of WordNet text). Avoid `git log --follow` on them and be
  careful with anything that walks full history.
- **Remote `snyk-fix/*` branches** exist (47 of them, automated dependency
  bump attempts). Ignore them; do not delete or merge them.
- **`filtered_for_syn`'s WordNet fallback was removed** in the final
  refactor; unknown words pass through unchanged by design.

## Verifying changes

1. `python manage.py check` (or just start `runserver`) — the module-level
   pickle loads fail loudly if paths/artifacts are broken.
2. Exercise all three params (`sent`, `tag`, `syn` with and without `p`) via
   the curl lines above.
3. If you touched a generator script, regenerate the pickles and confirm the
   endpoints still return output.

## Where to read more

- `CHANGELOG.md` — every commit, newest first, with bullets.
- `architectural-diary/main.md` — index of the design decisions.
- `prompt.md` — a one-shot prompt that recreates this project from scratch.
