# Changelog

All notable changes to SynTag. Dates reflect original authorship (2013);
formatting and commit messages were cleaned up in 2026 (see the note below).

## Note on rewritten history (2026-09-08)

All 24 commits originally carried throwaway messages ("yo", "Yolo", "work
damit", "maybe this will fix it", ...). On 2026-09-08 the history was
rewritten with `git filter-branch --msg-filter` to replace them with
conventional-commit messages. **Messages only** — every tree, blob, author,
and date is byte-for-byte identical to before; only the commit SHAs changed
(because a commit's hash covers its message). Any SHA quoted in material
older than this change no longer resolves. The analyses behind each new
message are preserved in `architectural-diary/`.

## 2013-03-24

- `2a23c63` — fix: guard make_sentence against empty synonym lists
  - Wrap `choice(a)` in try/except in `make_sentence` so words whose synonym
    list is empty are skipped instead of raising IndexError (500s at request
    time).
  - Change `make_syn.py`'s filter to `len(v) > 0 and headword not in v`,
    keeping only non-empty synsets that don't just contain their own headword.
  - Author noted this mitigates but does not resolve the underlying issue.

## 2013-03-23

- `b591be4` — refactor: replace runtime WordNet lookups with precomputed dict
  - Rewrite `filtered_for_syn` as a comprehension over a new
    `get_syn_for_word_pair` helper that tries a stemmed (`word[:-1]`) key,
    then the exact key, and falls back to `[word]` on a miss.
  - Remove the `wn`/`chain` imports and the unreliable on-the-fly synset
    fallback; also fixes the two-argument call introduced with the `syn`
    endpoint.
  - Fold `do_it_all`'s punctuation cleanup into `make_sentence`, inline the
    pipeline in `views.py`, prune `make_syn.py` output, disable the Redis
    push, write `syn.pkl` + `syn_json.pkl`, and delete `syn.json`'s contents.

## 2013-03-22

- `9534514` — chore: add syn_json.pkl synset-to-JSON-lemma dictionary
  - Commit a pickled dict mapping WordNet synset keys (e.g. `verdict.n`,
    `braid.v`) to JSON-encoded lists of lemma names, presumably for lighter-
    weight or client-side synonym lookup. No code is wired to it yet.
- `b22105b` — fix: remove stray prose line breaking syn.py and handle semicolons
  - Replace an accidentally uncommented comment line (a SyntaxError) in
    `filtered_for_syn`'s KeyError branch with proper comments, keeping the
    WordNet fallback enabled.
  - Extend the space-stripping regex in the sentence cleanup to also remove
    spaces before semicolons.
- `53e88af` — fix: vendor WordNet corpus for deploy and re-enable fallback lookup
  - Commit the WordNet 3.0 flat files under `corpora/wordnet/` so NLTK has
    corpus data on the deployed host, reduce gunicorn workers 8→4 in the
    Procfile, and ignore `*.zip`.
  - Re-enable the `tensify(wn.synsets(...))` fallback in the KeyError branch
    of `filtered_for_syn`.
- `5fd5196` — chore: disable WordNet fallback in filtered_for_syn
  - Comment out the WordNet-synset fallback so unknown words fall through
    rather than receiving substitutes the author considered unreliable.
- `d1a1774` — fix: make tensify tense branches mutually exclusive with elif
  - Change the `vbg` and `vbz` checks in `tensify()` from `if` to `elif` so
    the trailing `else` returns the original list for non-verb positions and
    only one conjugation branch executes.
  - Treat interjections (`uh`) as nouns for substitution purposes.

## 2013-03-18

- `ed7ef7b` — build: add ipython, redis, and requests to requirements.txt
  - Pin `ipython==0.13.1`, `redis==2.7.2`, and `requests==1.1.0` for the
    Redis-backed `make_syn.py`, HTTP testing, and interactive debugging.

## 2013-03-17

- `b0746bc` — feat: rename endpoint params, add syn endpoint, expand tagger rules
  - Rename the home view params `s`→`sent` and `t`→`tag`, and add a `syn`
    param returning `filtered_for_syn(tagged(text))` with an optional `p`
    argument.
  - Extend the tagger builder's regex rules (cardinal numbers, articles,
    `-able`/`-ness`/`-ly`, default NN) and neutralize the plural-noun rule.
  - Remove the duplicate pickles under `syn/`.

## 2013-03-16

- `3a4fcd7` — chore: add syn/tagger generator scripts and generated artifacts
  - Add `make_syn.py` (WordNet lemma map → `syn.pkl`/`syn.json` + optional
    Redis mset) and `make-syn-pos-tagger.py` (Brown/Treebank backoff tagger →
    `syn-pos-tagger.pkl` plus a `-bak` copy).
  - Commit the generated pickle/JSON artifacts, add `*.pyc` to `.gitignore`,
    and untrack the previously committed `.pyc` files.
- `dbe2f3d` — feat: conjugate verb synonyms to match source tense
  - Add `tensify()` to re-conjugate candidate verb synonyms (`vbd`/`vbn` →
    "ed", `vbg` → "ing", `vbz` → "s"/"es") using suffix rules and
    `tagger.tag` lookups, called from `filtered_for_syn`.
  - Narrow noun tags to `nn`/`nns`/`n`, disable adverb substitution, and load
    the pickles from the repo root instead of `syn/`.
- `79b30bd` — feat: add tagged-text endpoint to home view
  - Accept a `t` parameter (GET or POST) in the home view and return
    `syn.tagged` output, alongside the existing `s` handling.
  - Refresh the root-level `syn-pos-tagger.pkl` copy.

## 2013-03-15

- `c8d69bd` — fix: import csrf_exempt for the home view decorator
  - Add the missing `from django.views.decorators.csrf import csrf_exempt`
    import; the decorator had been applied two commits earlier without it,
    raising NameError on every request.
- `09ecf9d` — build: pass --preload as a flag in Procfile
  - Change `--preload True` to bare `--preload`; gunicorn's preload is a
    boolean flag and the extra argument was invalid.
- `a793c08` — fix: exempt home view from CSRF and preload app in gunicorn
  - Apply `@csrf_exempt` to `syn.views.home` so plain POSTs without a CSRF
    token are accepted (the import arrives in a later commit).
  - Move the Procfile to 8 gunicorn workers with preload.
- `ec9c7e4` — build: reduce gunicorn workers to 4 in Procfile
  - Halve the web dyno's worker count, most plausibly to fit memory limits —
    each worker otherwise loads its own copy of the pickled models.
- `ab76652` — build: remove --noreload from Procfile gunicorn command
  - Drop the `--noreload` flag while iterating on getting the dyno to boot.
- `0bb1a37` — build: add gunicorn, nltk, and PyYAML to requirements.txt
  - Pin `gunicorn==0.17.2`, `nltk==2.0.4`, and `PyYAML==3.10` so deploys
    install what the Procfile and the `syn` app actually import.
- `c547c45` — build: simplify Procfile web command
  - Drop the newrelic-admin wrapper and run gunicorn directly.
- `9827da1` — chore: remove obsolete PHP placeholder .htaccess and index.php
  - Delete the PHP-era placeholder files from the initial commit, now that
    the repo hosts a Django app.
- `9734b8d` — style: reindent urlpatterns in word_tools/urls.py
  - Cosmetic re-indentation of the urlpattern entries (plus committed
    bytecode churn); no functional change.
- `75d65f4` — build: add Heroku Procfile and enable gunicorn app
  - Add a Procfile running the web process via newrelic-admin wrapping
    gunicorn bound to `0.0.0.0:$PORT`, and register gunicorn in
    INSTALLED_APPS.
- `3cbe5f1` — feat: scaffold Django project that synonymizes input text
  - Bootstrap a Django 1.5 project (`word_tools`) with a `syn` app that
    POS-tags submitted text with a pickled tagger, maps tags to WordNet POS
    classes, looks up synonyms (precomputed pickle with a `wn.synsets`
    fallback), and rebuilds sentences with random substitutions.
  - Ship `manage.py`, settings/urls/wsgi, a tests stub, and the first
    committed pickled models.
- `d4c057d` — chore: scaffold web root with index.php and disable PHP engine
  - Initial commit: an empty `index.php` placeholder and a `.htaccess`
    turning the PHP engine off for the directory.

## 2026-09-08

- Documentation pass (this change): README, AGENTS.md, this changelog, an
  architectural diary, and a one-shot recreation prompt were added; commit
  messages were rewritten as described in the note above.
