# prompt.md — one-shot recreation prompt for SynTag

Give this entire document to a capable coding agent to recreate the SynTag
service from scratch (excluding this 2026 documentation pass).

---

Recreate **SynTag**, a sentence-synonymizing web service, exactly as
described. It is a Python 2.7-era Django application that POS-tags input
text with a pre-trained NLTK tagger and rewrites the sentence using random
WordNet synonyms for content words. The final request path must be pure
in-memory dictionary lookups — no corpus access at request time.

## Goal

A deployed HTTP service where submitting a sentence returns the same
sentence with nouns, verbs, and adjectives replaced by randomly chosen
WordNet synonyms, with a helper that attempts to preserve verb tense.

## Exact stack

- Python 2.7 idioms (`iteritems`, `cPickle`, `urlparse`, `print` statements
  where natural — this is a faithful 2013 build, not a port).
- Django 1.5 (`word_tools` project; gunicorn in `INSTALLED_APPS`).
- NLTK 2.0.4 (WordNet corpus, Brown + Treebank tagged corpora).
- gunicorn 0.17.2 (via `python manage.py run_gunicorn`), PyYAML 3.10,
  redis client 2.7.2, requests 1.1.0, ipython 0.13.1 — all pinned in
  `requirements.txt`.
- Heroku deployment via `Procfile`
  (`web: python manage.py run_gunicorn -b 0.0.0.0:$PORT -w 4 --preload`).
- WordNet 3.0 database files vendored under `corpora/wordnet/`.

## Build order (phases)

1. **Offline data builders** (run before the web app; artifacts committed):
   - `make_syn.py`: iterate `wn.all_synsets()`; build `syn` dict keyed by
     `<headword>.<pos>` (headword = synset name minus sense number and POS
     suffix, e.g. `verdict.n`), unioning lemma names across synsets sharing
     a key. Keep only entries where `len(lemmas) > 0` and the headword is
     NOT itself in the list. cPickle as `syn.pkl`; also write `syn_json.pkl`
     (same dict, values JSON-encoded). Include (commented out) a block that
     msets the JSON map to a hosted Redis; never enable it.
   - `make-syn-pos-tagger.py`: build a backoff chain — `RegexpTagger`
     (patterns: `.*ing$`→vbg, `.*ed$`→vbd, `.*es$`→vbz, numbers→CD,
     articles→AT, `.*able$`→JJ, `.*ness$`→NN, `.*ly$`→RB, default NN) with
     `DefaultTagger('n')` backoff → `UnigramTagger` over a manual lookup
     dict built from all Brown-tagged words (lowercased), filled with
     Treebank words not already present → `BigramTagger` trained on Brown
     sentences → `BigramTagger` trained on Treebank sentences. cPickle as
     `syn-pos-tagger.pkl` and again as `syn-pos-tagger-bak.pkl`.
2. **Django scaffold**: project `word_tools` (settings/urls/wsgi,
   `manage.py`, `DJANGO_SETTINGS_MODULE=word_tools.settings`), app `syn`
   with empty `models.py` and a stub `tests.py`; single URL `^$` →
   `syn.views.home`.
3. **Pipeline module** `syn/syn.py`: at import time, `cPickle.load`
   `syn.pkl` and `syn-pos-tagger.pkl` from the repo root (relative paths).
4. **HTTP layer** `syn/views.py`: `@csrf_exempt` home view dispatching on
   `request.REQUEST` params (below).
5. **Deploy plumbing**: Procfile, requirements, `*.pyc` and `*.zip`
   gitignored; commit the pickle artifacts and the vendored WordNet files.

## Data model

- `syn.pkl` — dict: `"<headword>.<n|v|a>" -> list[str, ...]` (lemma names,
  WordNet underscores preserved). ~3.9 MB.
- `syn-pos-tagger.pkl` — a pickled five-stage NLTK tagger object. ~5.7 MB.
- In `syn/syn.py`, `simple_tags` maps Penn tags to WordNet classes:
  nouns `nn nns n uh` → `n`; verbs `vb vbd vbg vbn vbp vbz v` → `v`;
  adjectives `jj jjr jjs jjt a` → `a`. Adverbs are deliberately excluded
  (commented out).
- No database is used; `DATABASES['default']['ENGINE']` stays empty.

## APIs by name

`syn/syn.py` (module-level pickle loads; helpers in order of use):

- `tagged(search)` — lowercase, strip chars outside `[A-z0-9; ,.?!]`, split
  on `[.!?]`, `word_tokenize` each sentence, drop empties, return
  `tagger.batch_tag(...)` output.
- `filtered_for_syn(sents, p=1)` — nested comprehension: for each
  (word, pos-lowercased) pair call `get_syn_for_word_pair`.
- `get_syn_for_word_pair(word, pos)` — if pos maps in `simple_tags`: try
  `(word[:-1] + "." + cls)`, then `(word + "." + cls)` in `syn`, routing
  hits through `tensify`; else/miss → `[word]`.
- `tensify(syn_list, pos)` — intended to re-conjugate verb candidates for
  vbd/vbn (add/handle "ed"), vbg ("ing"), vbz ("s"/"es"), using
  `tagger.tag[candidate]` and suffix rules, `else: return syn_list` for
  non-verb positions (branches chained with `elif`). Reproduce the
  faithful-to-original quirk: its loops iterate an empty local `s_list`
  instead of `syn_list`, so it returns empty lists.
- `make_sentence(syn_sents)` — per sentence: `choice()` a candidate for
  each word (first word `.title()`d; wrap `choice` in try/except-pass so
  empty lists — from `tensify` — drop the word), append ".", join, replace
  `_` with space, strip spaces before `[.?,;]`.

`syn/views.py`:

- `home(request)` — `@csrf_exempt`; reads merged GET+POST params:
  - `sent` → `HttpResponse(make_sentence(filtered_for_syn(tagged(sent))))`
  - `tag` → `HttpResponse(tagged(tag))`
  - `syn` → `HttpResponse(filtered_for_syn(tagged(syn), p))` when optional
    `p` present, else one-arg form
  - neither → `HttpResponse(status=404)`

## Design decisions to honor

1. Everything substitutable is precomputed into `syn.pkl`; request path
   never touches WordNet (unknown words pass through unchanged).
2. Only nouns, verbs, adjectives are substituted; interjections count as
   nouns; adverbs never.
3. Tagging by pickled backoff chain, not live training; workers share it
   via gunicorn `--preload` (4 workers).
4. One endpoint, param-routed, CSRF-exempt, plain-text responses.
5. Generated artifacts and the WordNet corpus are committed to the repo.
6. `syn_json.pkl` is written but unused by the service; `syn.json` remains
   an empty tracked file.
7. The `tensify` empty-loop bug and the `choice` guard around it are part
   of the faithful behavior (documented, not fixed, in the original).

## Acceptance criteria

1. `pip install -r requirements.txt && python manage.py runserver` starts
   without errors (on Python 2.7), loading both pickles at import.
2. `POST /` with `sent=The judge delivered the verdict` returns a sentence
   with at least one content word replaced by a WordNet synonym (verbs may
   be dropped given the tensify bug — noun substitution must be visible).
3. `GET /?tag=...` returns tagged token lists; `GET /?syn=...&p=n`
   returns per-word synonym lists filtered to nouns; `p` absent returns
   all classes.
4. A request with none of `sent`/`tag`/`syn` returns 404.
5. Running `make_syn.py` and `make-syn-pos-tagger.py` (with corpora
   present) regenerates both pickles; the service behaves identically
   afterward.
6. `python manage.py run_gunicorn -b 0.0.0.0:$PORT -w 4 --preload` serves
   the same API with one shared preloaded copy of the models.
7. No secrets in source: any Redis URL stays commented out and
   placeholder; a Django `SECRET_KEY` may be present as in the original
   but flag it in the README.
