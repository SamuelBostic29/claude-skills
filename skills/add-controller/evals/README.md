# Evals for `add-controller`

## What this skill is supposed to fix

Without this skill, Claude writes a fat controller — business rules or DB calls
in the handler — and hand-rolls its own auth check, response envelope, and
error codes instead of the repo's. With it, Claude mirrors the nearest existing
handler: a thin transport boundary that validates, delegates, and returns the
standardized response, registered the standard way.

## How to run

1. Install the skill: `cp -r skills/add-controller ~/.claude/skills/`
2. In a fresh session inside a repo that has real route/handler modules, run each case.
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — New endpoint mirrors the handler (positive)

- **Setup / fixture:** A repo with an existing handler/route and its registration mechanism.
- **Prompt:** "Add `GET /widgets/<id>` and `POST /widgets/search`."
- **Expected:**
  - [ ] Reads an existing handler (and its registration + the service it calls) before writing.
  - [ ] New handler reuses the repo's auth, content-type validation, response envelope, and error-code mapping.
  - [ ] Echoes concurrency headers (e.g. ETag / `If-Match`) the same way as the reference.
  - [ ] Registered via the same blueprint/url-prefix mechanism as siblings.
  - [ ] No business logic or SQL in the handler; it delegates to the service/DAO.
  - [ ] Reports the routes, the handler it mirrored, and what it calls.

### Case 2 — Add a verb to an existing handler (positive)

- **Setup / fixture:** A resource that already has a handler.
- **Prompt:** "Add `DELETE /widgets/<id>` to the widget handler."
- **Expected:**
  - [ ] Adds the verb to the existing handler; no parallel route module.
  - [ ] Matches sibling verbs' validation, auth, and response shaping.
  - [ ] Stops without touching the service, DAO, or tests.

### Case 3 — Wrong layer: business rule (negative / should defer)

- **Setup:** Same repo.
- **Prompt:** "Make `POST /widgets` reject widgets whose price is below cost."
- **Expected:**
  - [ ] Recognizes the rule is business logic, not transport.
  - [ ] Defers the rule to **add-service**; the handler only calls the service.

### Case 4 — No comparable handler to mirror (negative / should ask)

- **Setup:** A repo with no existing HTTP handler resembling the request (e.g. only event/queue consumers).
- **Prompt:** "Add an endpoint for `Widget`."
- **Expected:**
  - [ ] Notes there is no comparable handler/entry-point pattern to mirror.
  - [ ] Asks which entry-point convention to follow rather than inventing one.
