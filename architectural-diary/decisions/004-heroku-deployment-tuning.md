# 004 — Tune the Heroku/gunicorn process model by trial and error

**When:** 2013-03-15 (six Procfile revisions in one day), revisited
2013-03-22. Commits: `75d65f4`, `c547c45`, `ab76652`, `ec9c7e4`,
`a793c08`, `09ecf9d`, then `53e88af`.

## Context

The app targets Heroku: a `Procfile` names the web process, and the platform
injects `PORT`. The project loads two big pickles at import time (~10 MB
together, ~50x that in resident RAM once Python and NLTK are in), which made
worker count and preload semantics the dominant deploy variables.

## Decision (as it settled)

`web: python manage.py run_gunicorn -b 0.0.0.0:$PORT -w 4 --preload` —
four workers, application preloaded once before forking so the pickles are
loaded a single time and shared copy-on-write.

The path there, all on 2013-03-15, is visible in history:

1. `75d65f4` — first Procfile: `newrelic-admin run-program ... -w 8` plus
   gunicorn registered in `INSTALLED_APPS`.
2. `c547c45` — drop the newrelic wrapper (no credentials/config for it).
3. `ab76652` — drop `--noreload`.
4. `ec9c7e4` — workers 8 → 4 (memory pressure: each non-preloading worker
   would load the pickles itself).
5. `a793c08` — workers back to 8, add `--preload True` to share the load.
6. `09ecf9d` — `--preload True` → `--preload` (the "True" was a spurious
   positional argument that broke the command).
7. `53e88af` (03-22) — settle on `-w 4 --preload`, halving again alongside
   the day's corpus-vendoring memory needs.

## Consequences

- Preload is the load-bearing choice: it converts per-worker model loading
  into a one-time boot cost, which is exactly right for immutable pickled
  data.
- The six-iterations-in-a-day pattern (all originally messaged "yo") shows
  the debugging loop was push-and-watch-the-dyno, not local reproduction.
- `manage.py run_gunicorn` (gunicorn's Django command from that era,
  enabled via `INSTALLED_APPS`) no longer exists in modern gunicorn.
