# SynTag

SynTag is a small natural-language web service that takes a sentence, tags
each word with its part of speech, and rewrites the sentence by substituting
a randomly chosen WordNet synonym for every noun, verb, and adjective —
attempting to preserve verb tense in the process. It was built in March 2013
as a Django app deployed to Heroku, and is preserved here as-is.

The result reads like a mad-libbed paraphrase of the input: *"The judge
delivered the verdict"* becomes something like *"The jurist delivered the
finding"*.

## Features

- **Sentence synonymization** — POST a sentence, get back the same sentence
  with content words swapped for random WordNet synonyms.
- **POS tagging endpoint** — get the tokenized, tagged form of a sentence
  using a pre-trained NLTK backoff tagger (regex → default → unigram →
  Brown bigram → Treebank bigram).
- **Synonym lookup endpoint** — get the raw candidate-synonym lists per word,
  optionally filtered by part of speech.
- **Tense-aware verb substitution** — a `tensify()` helper re-conjugates
  candidate verbs to match the original's tense (see the diary for its known
  bug).
- **Precomputed, pickled data** — everything the request path needs ships in
  two pickle files (`syn.pkl`, `syn-pos-tagger.pkl`); no corpus access or
  model training happens at request time.

## Stack

| Component | Version (pinned in `requirements.txt`) |
| --- | --- |
| Python | 2.7-era code (`iteritems`, `cPickle`, `request.REQUEST`) |
| Django | 1.5 |
| NLTK | 2.0.4 |
| gunicorn | 0.17.2 |
| PyYAML | 3.10 |
| redis (client) | 2.7.2 |
| requests | 1.1.0 |
| ipython | 0.13.1 |
| WordNet | 3.0 flat files, vendored under `corpora/wordnet/` |

## Quickstart

The code targets Python 2.7 (2013); on a modern machine use a Python 2
interpreter or a container image of the era.

```bash
pip install -r requirements.txt   # Django 1.5, nltk 2.0.4, ...
python manage.py runserver        # dev server on http://127.0.0.1:8000
```

The two pickle artifacts (`syn.pkl`, `syn-pos-tagger.pkl`) are committed, so
no build step is required to run the service. To regenerate them (requires
the NLTK corpora to be available locally):

```bash
python make_syn.py              # WordNet → syn.pkl + syn_json.pkl
python make-syn-pos-tagger.py   # Brown/Treebank → syn-pos-tagger.pkl (+ -bak)
```

Production (as deployed on Heroku):

```bash
foreman start                   # runs: python manage.py run_gunicorn -b 0.0.0.0:$PORT -w 4 --preload
```

## HTTP API

A single endpoint (`/`, `syn.views.home`) routes on request parameters —
GET or POST, CSRF-exempt, plain-text responses, 404 when no recognized
parameter is present:

| Param | Extra param | Returns |
| --- | --- | --- |
| `sent` | — | The sentence rewritten with random synonyms |
| `tag` | — | The tokenized, POS-tagged form of the text |
| `syn` | optional `p` | Per-word synonym candidate lists (optionally POS-filtered) |

```bash
curl -X POST -d "sent=The judge delivered the verdict" http://localhost:8000/
curl --get --data-urlencode "tag=The judge delivered the verdict" http://localhost:8000/
curl --get --data-urlencode "syn=The judge delivered the verdict" --data "p=v" http://localhost:8000/
```

## How it works

1. `syn.views.home` reads `sent`/`tag`/`syn` from the request.
2. `syn.syn.tagged()` lowercases and strips the input, splits it into
   sentences, tokenizes, and runs the pickled backoff tagger.
3. `filtered_for_syn()` maps Penn Treebank tags onto three WordNet POS
   classes (`n`, `v`, `a`) and looks up each word's synonym candidates in
   `syn.pkl` (keyed `word.pos`, with a stemmed retry).
4. `make_sentence()` picks one candidate per word at random, capitalizes the
   first word, and cleans up punctuation spacing.

## Repository structure

```
manage.py                  Django entry point (settings: word_tools.settings)
Procfile                   Heroku web process (gunicorn)
requirements.txt           Pinned 2013-era dependencies
make_syn.py                Builds syn.pkl / syn_json.pkl from WordNet
make-syn-pos-tagger.py     Trains and pickles the POS tagger chain
syn/                       Django app: views.py (HTTP), syn.py (pipeline)
word_tools/                Django project: settings, urls, wsgi
corpora/wordnet/           Vendored WordNet 3.0 database files
syn.pkl                    Precomputed synonym dict (synset key → lemmas)
syn_json.pkl               Same data with JSON-encoded values
syn-pos-tagger.pkl         Pickled NLTK tagger (plus -bak copy)
syn.json                   Empty leftover file
```

## Environment

The app itself reads no configuration from the environment. The process
model expects `PORT` to be provided by the host (Heroku convention, used by
the Procfile). `make_syn.py` contains a commented-out block intended to push
the synonym map to a hosted Redis; if you re-enable it, put the connection
details in a `REDIS_URL`-style variable instead of editing the source.

## Status

This is a 2013 time-capsule project, kept for reference. It will not run
unmodified on Python 3. GitHub reports Dependabot alerts against the pinned
2013 dependencies — expected for unmaintained versions of Django, requests,
and friends; see the repo's Security tab. See `CHANGELOG.md` for the full
history and `architectural-diary/` for the design decisions.
