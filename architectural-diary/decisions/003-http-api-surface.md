# 003 — One CSRF-exempt endpoint, plain text, param-routed

**When:** 2013-03-15 → 2013-03-17. Commits: `3cbe5f1`, `79b30bd`,
`a793c08`, `c8d69bd`, `b0746bc`.

## Context

The service needs an HTTP surface, but in 2013 the fastest path for a
personal tool was not a REST API with serializers — it was one Django view
that sniffed request parameters. Clients were curl and quick scripts, none
of which wanted to perform Django's CSRF dance.

## Decision

`word_tools/urls.py` routes exactly one pattern (`^$`) to
`syn.views.home`, decorated `@csrf_exempt`. The view reads the merged
GET+POST mapping (`request.REQUEST`) and dispatches on the first
recognized parameter name:

- `sent` → full pipeline: `make_sentence(filtered_for_syn(tagged(s)))`
- `tag` → just `tagged(s)` (added 03-16)
- `syn` (+ optional `p`) → `filtered_for_syn(tagged(s), p)` (added 03-17,
  with the param rename `s`→`sent`, `t`→`tag`)
- anything else → 404 with empty body.

Responses are plain `HttpResponse` text — the tagged form is Python's repr
of nested lists, the synonym form likewise; no JSON despite `json.dumps`
having been imported early on.

## Consequences

- Extremely low ceremony: no templates, no static files, no client contract
  beyond "name your parameter".
- CSRF exemption is fine for a read-only text toy; it would be a finding in
  anything stateful.
- The CSRF story had a rocky start: `@csrf_exempt` was applied on 03-15
  (`a793c08`) *without* its import, so every request NameError'd until the
  import landed hours later (`c8d69bd`) — a two-commit bug preserved in
  history.
- Parameter names are the API; the 03-17 rename (`s`→`sent`, `t`→`tag`)
  was a silent breaking change for any existing client.
- `request.REQUEST` is gone in modern Django; a port would need to read
  `request.GET`/`request.POST` explicitly.
