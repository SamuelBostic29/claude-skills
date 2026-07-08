---
name: postman
version: 1.0.0
description: |
  Use whenever the user asks about their Postman account or its contents —
  "what Postman workspace am I in", "list my workspaces / collections",
  "dump / pull / show the requests in <collection>", "what environments do I
  have", "what's the value of <variable> in <environment>", or "/postman" —
  or asks to create or update a Postman collection or environment. Drives the
  Postman REST API (api.getpostman.com) over curl with a per-user API key in
  a gitignored home file; reads run freely, writes are drafted and confirmed
  first.
allowed-tools:
  - Read
  - Write
  - AskUserQuestion
  - Bash(grep:*)
  - Bash(sed:*)
  - Bash(head:*)
  - Bash(printf:*)
  - Bash(tr:*)
  - Bash(chmod:*)
  - Bash(curl:*)
---

# Postman: read and write a Postman account over its REST API

You drive the **Postman REST API** (`https://api.getpostman.com`) over curl so the user can see their workspaces, list collections, dump every request in a collection (method, URL, headers, body), and inspect environments without opening the Postman app. Two non-negotiables: **the API key is a secret** — it authenticates the user's whole Postman account, crosses only on curl's `-K -` stdin, and is never echoed, printed, or passed on argv — and **writes are outward-facing**: every create/update to a collection or environment is drafted in full and confirmed before it is sent. Reads are free and need no confirmation.

Auth is one secret: a **per-user Postman API key** in `~/.claude/postman-token.local` — outside any repo, never committed, never echoed, every user has their own. There is no shared credential and **no environment variable**. A fresh user does setup once.

**Every curl in this skill runs through the Bash tool, never PowerShell** — in PowerShell `curl` is an alias for `Invoke-WebRequest` and silently mangles `-H`/`-d`/`-K`. The key is fed to curl on stdin as a config-file directive (`-K -` with a `header = "X-Api-Key: …"` line) so it never lands in argv, process lists, or a command log — reads and writes alike.

## First action on every invocation — the key gate (before you reply or ask anything)

A bare invocation is **not** a cue to ask the user what they want. The instant the skill runs — before any reply, before asking which workspace or collection — check the key, silently:
```bash
TOKEN_FILE="$HOME/.claude/postman-token.local"
T="$(sed -n '/^[[:space:]]*#/d;s/.*"\([^"]*\)".*/\1/p' "$TOKEN_FILE" 2>/dev/null | head -1)"; [ -z "$T" ] && T="$(grep -vE '^[[:space:]]*(#|$)' "$TOKEN_FILE" 2>/dev/null | head -1)"
case "$(printf %s "$T" | tr -d '\r\n')" in ''|'<'*) echo NO_KEY ;; *) echo KEY_OK ;; esac
```
- **`NO_KEY`** → run **Setup** (write the template, `chmod 600`, open the file in the editor), tell the user to paste their key between the quotes and save, then stop. Do **not** ask what they want yet.
- **`KEY_OK`** → proceed. If no workspace/collection/action was named, ask which — otherwise go straight to Steps.

## When to use this skill

- "What workspace am I in", "list my Postman workspaces / collections / environments"
- "Dump / pull / show / export the requests in <collection>", "what endpoints does <collection> hit"
- "What variables are in <environment>", "what's `baseUrl` set to"
- "Create / update a Postman collection or environment" (drafted + confirmed)
- The key isn't set up yet, or a call returns `401` — run Setup to (re)store it.

## When NOT to use this skill

- **Running requests or collections** — this skill reads and edits Postman *data*; it does not execute requests. Use the app, `newman`, or plain curl against the target API instead.
- **The team's API itself** — "call our /orders endpoint" is a request to the real API, not to Postman. Postman is only the store of saved requests.
- **Deleting anything** — deletion is deliberately out of scope (see Rules); point the user to the Postman UI.

## Setup — store the per-user API key (one time, before any call)

Run this once, or whenever a call returns `401`.

1. **Have the user create the key in the browser** (can't be automated): Postman (web or app) → profile avatar → **Settings** → **API keys** → **Generate API key**, name it "Claude", copy it (`PMAK-…`).

2. **Create the key file from a template — the user pastes into the editor window that opens, never into the chat.** With the **`Write`** tool, write exactly this to `$HOME/.claude/postman-token.local` (only if it is absent or a placeholder — never clobber a real key), then `chmod 600` it:
   ```
   # Your personal Postman API key — used only by the postman skill.
   # This file lives outside any repo; it is NEVER committed.
   #   1. Get it:  Postman → profile avatar → Settings → API keys → Generate API key
   #   2. Paste your key between the quotes below, replacing the whole <...>. Keep the quotes. Save.
   #   Example:  POSTMAN_API_KEY="PMAK-63f1...-4a2b..."
   POSTMAN_API_KEY="<PASTE_YOUR_POSTMAN_API_KEY_HERE>"
   ```
   Then open it for the user (`notepad "$TOKEN_FILE"` on Windows, else `${EDITOR:-nano} "$TOKEN_FILE"`); they replace the `<...>` between the quotes and save. **Never** ask them to paste the key into the chat, and never write it from a tool-call argument.

3. **Confirm by calling Postman — prove the key, show the user, never the key.** Define `auth_cfg` (below), then:
   ```bash
   auth_cfg | curl -sS -K - "https://api.getpostman.com/me" | grep -o '"username":"[^"]*"'
   ```
   A username means the key works — report "Connected as <username>". An `error` body means the key was rejected: re-run from step 1.

## Steps (every read/write call)

1. **Resolve the key (silently), else set it up.** `TOKEN_FILE="$HOME/.claude/postman-token.local"`; define the extractor once per shell call — the key crosses only on stdin:
   ```bash
   auth_cfg() { local t; t="$(sed -n '/^[[:space:]]*#/d;s/.*"\([^"]*\)".*/\1/p' "$TOKEN_FILE" | head -1)"; [ -z "$t" ] && t="$(grep -vE '^[[:space:]]*(#|$)' "$TOKEN_FILE" | head -1)"; printf 'header = "X-Api-Key: %s"\n' "$(printf %s "$t" | tr -d '\r\n')"; }
   BASE="https://api.getpostman.com"
   # read:  auth_cfg | curl -sS -K - "$BASE/workspaces"
   ```
   Strip CR/LF (a Windows newline in the header → silent 401). No key → run Setup.

2. **Resolve names to ids before anything else.** The API addresses everything by `id`/`uid`, users speak in names. List first (`/workspaces`, `/collections?workspace=<id>`, `/environments?workspace=<id>`), match the name the user gave case-insensitively; several matches or no match → show the candidates and ask. There is **no "current workspace" endpoint** — when asked "what workspace am I in", list the workspaces and, if more than one, present them and ask which they mean; never guess.

3. **Read freely.** Endpoints, response shapes, and the collection-format item tree are in `references/postman-api.md` — read it before your first call of the session. For a collection dump, fetch `GET /collections/{uid}` **to a scratch file** (`curl -o`) and walk it with the Read tool — collections are routinely hundreds of KB and would flood the transcript if catted.

4. **For a write, draft it and stop for confirmation.** Compose the exact curl (endpoint, method, JSON body) and show it. State precisely what changes (which workspace/collection/environment, what's added or replaced — a `PUT /collections/{uid}` **replaces the whole collection**, so say so). Get an explicit yes via AskUserQuestion before sending. No yes → don't send; offer to revise.

5. **Send the confirmed write** — auth and `Content-Type` both via stdin config:
   ```bash
   { auth_cfg; printf 'header = "Content-Type: application/json"\n'; } \
     | curl -sS -K - -X POST "$BASE/collections?workspace=<id>" -d @payload.json
   ```
   Success returns the created/updated object (`{"collection":{"id","uid","name"}}`); failures return `{"error":{"name","message"}}`.

6. **Report and stop.** Reads → the requested data per Output format. Writes → confirm the result (new uid, updated name). On failure, quote `error.name` + `error.message` and the HTTP status; on `429`, report the rate limit and stop — never retry in a loop. Do not widen into unrequested edits.

## Output format

**Workspace / collection / environment lists** — a table, one row per item: name, type/visibility where present, id (users need the id to disambiguate duplicates).

**Collection dump** — folder structure preserved, one block per request, most-used fields only:
```
# <Collection name> — <n> requests (workspace: <name>)

## <Folder / Sub-folder>
### <Request name>
`<METHOD> <url.raw>`
- Headers: <key: value, comma-joined | —>
- Body (<mode>): <raw body, fenced if multi-line | —>
- Auth: <type | inherited>
```

**Environment variables** — a `key | value | type` table. **Mask any variable whose `type` is `"secret"`** (show `••• (secret)`) and any value that looks like a credential even when typed `default` — name it, don't print it.

**Write (after confirmed send):**
```
postman: <DONE | FAILED> — <action> in <workspace/collection>
  → <result: created collection <uid> | updated environment "<name>">
  [on FAILED] HTTP <code>: <error.name — error.message>
```

## Rules — non-negotiables

- **Key secrecy is absolute.** Never echo, print, or return it — confirm via `/me` username, never the secret; **no `curl -v`, no `set -x`** while it's in scope. Feed it only via the `-K -` stdin `header = "…"` directive (never `-H`/argv), through the **Bash tool, never PowerShell**. Store it nowhere but `~/.claude/postman-token.local` — **never an env var**.
- **Writes drafted + confirmed.** Show the exact request and what it changes; send only on an explicit yes. Flag full-replacement semantics (`PUT`) explicitly in the draft.
- **Deleting isn't part of this skill — on purpose.** It never issues an `-X DELETE` against Postman: deleting a collection, environment, or workspace is destructive and this skill deliberately can't do it. If asked, explain that warmly and point the user to the Postman UI (⋯ menu on the item → Delete), then offer to help with what they actually need.
- **Secrets inside Postman stay masked.** Environment values typed `secret` — and anything that plainly is one — are named, never printed. Dumping a collection never includes resolved variable values, only the `{{placeholders}}` as stored.
- **Never guess an id.** Resolve names via a list call; ambiguity goes to the user, not to the first match.
- **Respect the rate limit.** One `429` → report and stop. The API is capped (~300 req/min, plus plan-level monthly caps) — batch reads via the fewest calls that answer the question.

For the endpoint catalog — workspaces, collections, the v2.1 collection-format item tree (folders nest), environments, writes, and error shapes — read `references/postman-api.md`.
