# Jira Data Center REST API — curl cheat-sheet

Layer-3 reference for the `jira-dc` skill. Every command targets **self-hosted Jira Data Center**
(`https://<JIRA_HOST>` — substitute your Configuration value; REST API **v2**) and authenticates
with a **per-user Personal Access Token** read from the gitignored `.claude/jira-token.local`.
This is **not** Atlassian Cloud — see the pitfall checklist at the bottom before reaching for any
Cloud snippet.

## Prelude — define these once per call

The token is fed to curl **only** via a `-K -` config-file directive on stdin, so it never enters
argv / the process list / a command log. Define a `BASE` and an `auth_cfg` emitter and reuse them:

```bash
BASE="https://<JIRA_HOST>/rest/api/2"
# TOKEN_FILE + auth_cfg: resolve per references/jira-token.md (repo copy else home; -K - stdin only)
auth_cfg() { local t; t="$(sed -n '/^[[:space:]]*#/d;s/.*"\([^"]*\)".*/\1/p' "$TOKEN_FILE" | head -1)"; [ -z "$t" ] && t="$(grep -vE '^[[:space:]]*(#|$)' "$TOKEN_FILE" | head -1)"; printf 'header = "Authorization: Bearer %s"\n' "$(printf %s "$t" | tr -d '\r\n')"; }
# writes add a second header line:
json_cfg() { auth_cfg; printf 'header = "Content-Type: application/json"\n'; }
```

- Read auth:  `auth_cfg | curl -sS -K - ...`
- Write auth: `json_cfg | curl -sS -K - -X POST/PUT ...`
- Use `-G --data-urlencode "k=v"` for query params so JQL / fragments are encoded safely.
- Append `-w '\n%{http_code}\n'` when you need the status (e.g. to tell `204` from a body) and
  `-D -` (dump headers) when you need to read `X-AUSERNAME` to diagnose an auth failure.

---

## 1. Identity / token check (whoami)

```bash
auth_cfg | curl -sS -K - "$BASE/myself"
```
Returns `{ "name": "<username>", "displayName": "...", "emailAddress": "..." }`. This is the only
"does my token work" probe — use it in Setup and whenever a call comes back empty/401.

## 2. Fetch an issue

```bash
auth_cfg | curl -sS -K - -G "$BASE/issue/PROJ-123" \
  --data-urlencode "fields=summary,description,status,issuetype,priority,assignee,reporter,components,labels,parent,fixVersions,created,updated,issuelinks,comment,attachment" \
  --data-urlencode "expand=names"
```
- `fields=` keeps the payload small; `*all` returns everything (large). Append any
  Configuration-listed `customfield_NNNNN` ids you want rendered.
- `expand=names` adds a top-level `names` map so you can label every `customfield_NNNNN` — this is
  how you discover instance-specific ids (sprint, epic link, story points, team fields) in the
  first place.
- `expand=renderedFields` returns wiki markup pre-rendered to HTML if you'd rather not parse markup.
- If the instance runs Jira Software: the **sprint** custom field is a serialized GreenHopper
  string array on DC (e.g. `["…[id=…,state=CLOSED,name=Sprint 23,…]"]`) — parse `name=` out of each
  entry; the last is the active sprint. The **epic link** field is an issue key string — render as
  `…/browse/<key>`. **Story points** is a number. Their `customfield_NNNNN` ids vary per instance.
- Subtasks carry `fields.parent.{key,fields.summary}`. `assignee`/`reporter` are
  `{name,displayName}` or `null`. `components`/`fixVersions` are `[{name,…}]`.
- `issuelinks[]`: each is `{ type:{name,inward,outward}, inwardIssue|outwardIssue:{key,fields:{summary,status}} }`.
  Render with the direction phrase — `type.inward` for an `inwardIssue`, `type.outward` for an
  `outwardIssue` (e.g. "relates to PROJ-131"). The SKILL.md Output format defines the layout.

## 3. Comments

Embedded when you request `fields=comment` (see §2): `fields.comment.comments[]` →
`{ id, author.displayName, created, updated, body }`. `body` is **wiki markup**, not ADF.

Paginated (long threads):
```bash
auth_cfg | curl -sS -K - -G "$BASE/issue/PROJ-123/comment" \
  --data-urlencode "startAt=0" --data-urlencode "maxResults=50" --data-urlencode "orderBy=created"
```
Response: `{ startAt, maxResults, total, comments[] }` — loop `startAt += maxResults` until `startAt + maxResults >= total`.

## 4. Attachments

Each `fields.attachment[]` entry has `{ filename, size, mimeType, created, author, content }` where
`content` is an absolute download URL on the same host. Download with the same auth, then Read it:
```bash
auth_cfg | curl -sS -K - -L -o "/tmp/jira-attachments/<filename>" "<content-url>"
```
- `mkdir -p /tmp/jira-attachments` first. These are throwaway files in the OS temp area, so no cleanup is needed on the happy path.
- `-L` follows the redirect DC issues to the file store. Read JSON/text/CSV/images/PDF with the Read tool; note-and-skip binaries.

## 5. JQL search (find a ticket)

```bash
auth_cfg | curl -sS -K - -G "$BASE/search" \
  --data-urlencode "jql=project = PROJ AND assignee = currentUser() AND resolution = Unresolved ORDER BY updated DESC" \
  --data-urlencode "fields=summary,status,assignee" \
  --data-urlencode "startAt=0" --data-urlencode "maxResults=50"
```
Response: `{ startAt, maxResults, total, issues[] }` — page the same way as comments.
Useful JQL:
- My open work: `assignee = currentUser() AND resolution = Unresolved ORDER BY updated DESC`
- Map an external ref to Jira: `project = PROJ AND summary ~ "GH-512"`
- Current sprint: `project = PROJ AND sprint in openSprints()`

`text ~` / `summary ~` is a fuzzy contains; quote multi-word phrases. A malformed JQL returns `400`
with the parse error in `errorMessages`.

## 6. Create an issue

Discover required fields first (projects vary):
```bash
auth_cfg | curl -sS -K - -G "$BASE/issue/createmeta" \
  --data-urlencode "projectKeys=PROJ" \
  --data-urlencode "expand=projects.issuetypes.fields"
```
Look for fields with `"required": true`. Then create:
```bash
json_cfg | curl -sS -K - -X POST "$BASE/issue" -d '{
  "fields": {
    "project":   { "key": "PROJ" },
    "issuetype": { "name": "Story" },
    "summary":   "Short title",
    "description": "Body in *wiki* markup.",
    "priority":  { "name": "Medium" }
  }
}'
```
- Sub-task: add `"parent": { "key": "PROJ-123" }` and use `"issuetype": { "name": "Sub-task" }`.
- Success is **`201`** with `{ "id", "key", "self" }` — report the key + `https://<JIRA_HOST>/browse/<key>`.
- The request **body goes in argv** via `-d '...'`, never on stdin: stdin is already consumed by
  the `-K -` auth config, so `-d @-` / a heredoc would clobber it. A body is not secret (only the
  *token* must stay out of argv), so this is fine. Use `\n` inside JSON strings for line breaks:
  `-d '{"fields":{"summary":"Title","description":"line 1\nline 2"}}'`. If a value contains a single
  quote, escape it `'\''` (or assemble the JSON so it doesn't).

## 7. Transition (move status)

Get the valid transitions **from the current state** (ids differ per workflow/state):
```bash
auth_cfg | curl -sS -K - "$BASE/issue/PROJ-123/transitions"        # add ?expand=transitions.fields if the screen requires fields
```
Returns `transitions[] = { id, name, to.name }`. Pick the `id` whose `name`/`to.name` matches, then:
```bash
json_cfg | curl -sS -K - -X POST "$BASE/issue/PROJ-123/transitions" -d '{ "transition": { "id": "41" } }'
```
- Success is **`204`** (empty body). If the transition screen requires fields, include `"fields": {...}` (or `"update": {...}`) in the body — `400` lists which.

## 8. Assign

Resolve the username (DC identifies users by `name`, **not** `accountId`):
```bash
auth_cfg | curl -sS -K - -G "$BASE/user/search" --data-urlencode "username=<fragment>"
# Some DC builds (user-privacy/GDPR mode) ignore username= — if empty, retry:
auth_cfg | curl -sS -K - -G "$BASE/user/search" --data-urlencode "query=<fragment>"
```
Returns `[ { name, displayName, emailAddress, active } ]` — take `.name`. Then:
```bash
json_cfg | curl -sS -K - -X PUT "$BASE/issue/PROJ-123/assignee" -d '{ "name": "<username>" }'
```
- Success is **`204`**. `{ "name": null }` unassigns; `{ "name": "-1" }` sets project-default assignee.

## 9. Edit fields

Simple set (overwrites the field):
```bash
json_cfg | curl -sS -K - -X PUT "$BASE/issue/PROJ-123" -d '{
  "fields": { "summary": "New title", "description": "New *wiki* body.", "priority": { "name": "High" } }
}'
```
Add/remove without clobbering (labels, fix versions, components):
```bash
json_cfg | curl -sS -K - -X PUT "$BASE/issue/PROJ-123" -d '{
  "update": { "labels": [ { "add": "regression" }, { "remove": "stale" } ] }
}'
```
- Success is **`204`**. Send only the fields you're changing.
- **Custom fields — discover, never guess.** Get the real id + value shape first:
  ```bash
  auth_cfg | curl -sS -K - "$BASE/issue/PROJ-123/editmeta"
  ```
  `fields.customfield_NNNNN` carries `{ name, schema, allowedValues }`. Value shape by type:
  text/textarea → `"customfield_NNNNN": "value"` (wiki markup, `\n` for line breaks);
  single-select → `{ "value": "Option" }` (or `{ "id": "…" }`);
  multi-select → `[ { "value": "A" }, { "value": "B" } ]`; user → `{ "name": "username" }`;
  number → `12`. Custom-field ids are **global** per DC instance but differ **between** instances —
  discover once via `editmeta`/`expand=names`, record the ids you use in the skill's Configuration,
  and confirm with `editmeta` before a write (a field is writable only where it's on the edit screen).

---

## 10. Errors and the anonymous trap

- **Empty result or `X-AUSERNAME: anonymous`** (seen via `-D -`) → the Bearer header didn't apply.
  Causes: token mistyped/expired/revoked, a stray `\r\n` in the token file (Setup strips it), or the
  header passed as a bare line instead of the `header = "…"` config directive. Re-run Setup.
- **`401` / `403`** → token missing, expired, revoked, or lacks permission for that project/action.
- **`404`** → issue/endpoint not found. An external ref like `GH-###` will always 404 as an issue key.
- **`400`** → bad payload. The body is `{ "errorMessages": [...], "errors": { "<field>": "..." } }` —
  report the exact field message, don't retry blindly.
- Always quote the DC `errors` field back to the user rather than a generic failure note.

## 11. Data Center vs Cloud — the pitfall checklist

| Concern            | Data Center (this skill)                            | Cloud (do NOT use here)                |
|--------------------|-----------------------------------------------------|-----------------------------------------|
| API version        | `/rest/api/2`                                       | `/rest/api/3`                          |
| Auth               | `Authorization: Bearer <PAT>`                       | Basic with email + API token           |
| User identity      | `name` / `username`                                 | `accountId`                            |
| Text bodies        | wiki markup (plain string)                          | ADF (JSON document)                    |
| User search param  | `username=` (fallback `query=`)                     | `query=` only                          |
| Field discovery    | `createmeta` / `editmeta` (available)               | createmeta deprecated/split            |

If a snippet from the internet uses `/api/3`, `accountId`, an ADF `{type:"doc",...}` body, or
Basic auth, it's a Cloud snippet — translate it to the left column before running it.
