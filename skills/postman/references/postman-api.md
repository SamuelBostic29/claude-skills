# Postman REST API — endpoint catalog and response shapes

Read this before the session's first call. Base URL `https://api.getpostman.com`; every call
authenticates with the `X-Api-Key` header fed via `-K -` stdin (see SKILL.md — never argv).
All responses are JSON. Errors come back as `{"error":{"name":"…","message":"…"}}` with a
matching HTTP status (`401` bad key, `404` bad id/uid, `429` rate-limited).

**id vs uid:** most objects carry both. `id` is the bare object id; `uid` is `{ownerId}-{id}`.
Item endpoints (`/collections/{uid}`, `/environments/{uid}`) want the **uid** — always use the
`uid` field from a list response and you can't get it wrong.

## Identity

```
GET /me
```
→ `{"user":{"id":…,"username":"…","email":"…","fullName":"…"}}` (plans also return `operations`
usage/limits). Use it to confirm a key after setup — report the username, never the key.

## Workspaces

```
GET /workspaces                      # every workspace the key can see
GET /workspaces/{id}                 # one workspace, with its contents
```
- List → `{"workspaces":[{"id","name","type","visibility"}]}` — `type` is `personal` | `team`
  (older API versions may say `individual`); `visibility` is `personal` | `private` | `team` | `public`.
- Single → adds the contents as arrays of `{id, uid, name}`: `collections`, `environments`,
  `mocks`, `monitors`, `apis`. This is the cheapest way to enumerate what's *in* a workspace.
- There is **no "current workspace"** — "current" is app-UI state the API doesn't expose. List
  and let the user pick.

## Collections

```
GET /collections                     # every collection the key can see (all workspaces)
GET /collections?workspace={id}      # scoped to one workspace
GET /collections/{uid}               # the full collection — the request dump
```
- List → `{"collections":[{"id","uid","name","owner","createdAt","updatedAt","isPublic","fork"?}]}`.
- Full collection → `{"collection":{"info":{…},"item":[…],"variable":[…],"auth":{…},"event":[…]}}`
  in **Collection Format v2.1**. Fetch it with `curl -o <scratch>/collection.json` and walk the
  file with Read — big collections flood the transcript otherwise.

### Walking the v2.1 item tree

`item` is a recursive array. Each entry is either a **folder** or a **request**:

- **Folder** — has `item` (nested array), no `request`: `{"name":"…","item":[…],"description"?}`.
  Folders nest arbitrarily; carry the path (`Folder / Subfolder`) as you recurse.
- **Request** — has `request`:
  ```json
  {
    "name": "Get order by id",
    "request": {
      "method": "GET",
      "url": {"raw": "{{baseUrl}}/orders/:id", "host": […], "path": […], "query": [{"key","value"}], "variable": [{"key","value"}]},
      "header": [{"key": "Accept", "value": "application/json", "disabled"?}],
      "body":   {"mode": "raw|urlencoded|formdata|graphql|file", "raw": "…", "urlencoded": […], "formdata": […], "options": {…}},
      "auth":   {"type": "bearer|basic|apikey|…", "<type>": […]},
      "description": "…"
    },
    "response": [ /* saved example responses — usually skip in a dump */ ]
  }
  ```
  Quirks: `url` may be a plain **string** instead of the object (old exports) — handle both via
  `url.raw // url`. `body` is absent on GETs. Skip `header`/`body` entries with `"disabled": true`.
  `{{variables}}` in urls/headers are placeholders resolved by environments at runtime — report
  them verbatim, never resolve them.
- Collection-level `variable` (`[{key,value}]`) and `auth` apply to every request that doesn't
  override them — report collection `auth.type` once and mark requests without their own auth
  as `inherited`.

## Environments

```
GET /environments                    # every environment the key can see
GET /environments?workspace={id}     # scoped
GET /environments/{uid}              # the variables
```
- List → `{"environments":[{"id","uid","name","owner"}]}`.
- Single → `{"environment":{"name","values":[{"key","value","type","enabled"}]}}` — `type` is
  `default` or **`secret`**; secret values often come back masked by the API but treat them as
  live either way: name them, never print them (SKILL.md rule).

## Writes (drafted + confirmed first — see SKILL.md step 4)

```
POST /collections?workspace={id}     # create — body {"collection":{ info, item, … }} (v2.1)
PUT  /collections/{uid}              # REPLACE the whole collection — never a partial patch
POST /environments?workspace={id}    # create — body {"environment":{"name","values":[…]}}
PUT  /environments/{uid}             # REPLACE the whole environment
```
- `info` on create needs `name` and
  `"schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"`.
- **`PUT` is full replacement.** To change one request, GET the collection, edit the JSON in the
  scratch file, and PUT the whole document back — and say exactly that in the draft, since a
  malformed PUT can clobber the collection. Send bodies with `-d @file.json`, never inline JSON
  on argv for anything non-trivial.
- Success: `200`/`201` echoing `{"collection":{"id","uid","name"}}` (or `environment`).
- There are `DELETE` endpoints; **this skill never calls them** (SKILL.md rule).

## Rate limits

~300 requests/min per key, plus plan-level monthly call caps on free plans. Every response
carries `X-RateLimit-Remaining`; a `429` body names the limit. One `429` → report and stop.
