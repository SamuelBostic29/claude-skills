---
name: jira-dc
version: 1.0.0
description: |
  Use whenever the user names a Jira ticket on a self-hosted Jira Data Center
  instance — a bare key like PROJ-123, "fetch / pull / show PROJ-123", or a
  browse URL on the configured Jira host — or asks to "comment on / assign /
  progress / transition a ticket", "set a field on a ticket", or "create a
  Jira issue". Operates on a single ticket over the Data Center REST API
  (/rest/api/2, Bearer PAT — NOT Atlassian Cloud). Authenticates with a
  per-user Personal Access Token in a gitignored file (your home by default,
  or the repo when provisioned); reads run freely, writes are drafted and
  confirmed first.
allowed-tools:
  - Read
  - Write
  - AskUserQuestion
  - Bash(git rev-parse:*)
  - Bash(git check-ignore:*)
  - Bash(git ls-files:*)
  - Bash(grep:*)
  - Bash(sed:*)
  - Bash(head:*)
  - Bash(tail:*)
  - Bash(printf:*)
  - Bash(tr:*)
  - Bash(chmod:*)
  - Bash(mkdir:*)
  - Bash(curl:*)
---

# Jira DC: operate on a Jira Data Center ticket

You drive a **self-hosted Jira Data Center** instance (`https://<JIRA_HOST>`, REST API `/rest/api/2`) over curl so the user can pull a ticket's details, comment, assign, transition, or open a new issue without leaving the terminal. The two non-negotiables: **this is Data Center, not Cloud** — `/rest/api/2`, `Authorization: Bearer <PAT>`, plain-string `name`/`username` (never `accountId`), wiki-markup text bodies (never ADF JSON) — and **writes are outward-facing**: every comment/assign/transition/create is drafted in full and confirmed before it is sent. Reads are free and need no confirmation.

Auth is one secret: a **per-user Personal Access Token** in `.claude/jira-token.local` — gitignored, never committed, never echoed, every user has their own. It lives in **`~/.claude/`** (your home) by default, so it works from any folder regardless of which repo you're in; a repo that ships a gitignore entry for it keeps its own copy so the token travels with that clone. There is no shared credential and **no environment variable**. A fresh user does setup once. **Resolve the token silently — never tell the user which path or repo you looked in.**

**Every curl in this skill runs through the Bash tool, never PowerShell** — in PowerShell `curl` is an alias for `Invoke-WebRequest` and silently mangles `-H`/`-d`/`-K`. The token is fed to curl on stdin as a config-file directive (`-K -` with a `header = "…"` line) so it never lands in argv, process lists, or a command log — this applies to **reads and writes alike**.

## Configuration (set per adopter — the only instance-specific section)

| Key | Placeholder / default | Used for |
| --- | --- | --- |
| `JIRA_HOST` | `<jira.your-company.example>` | `BASE="https://<JIRA_HOST>/rest/api/2"` and every `…/browse/<KEY>` link |
| `PROJECT_KEYS` | `<PROJ>` (optional, comma list) | A bare `<KEY>-123` matching one of these always means a Jira ticket — fetch it without asking which tracker |
| Custom fields | optional `<Name> = customfield_NNNNN` list | Extra fields to fetch and render on reads (ids are instance-specific — discover them once via `expand=names` / `editmeta`, then record them here) |

Substitute `<JIRA_HOST>` wherever it appears below. Everything else is instance-independent.

## First action on every invocation — the token gate (before you reply or ask anything)

A bare invocation is **not** a cue to ask the user what they want. The instant the skill runs — before any reply, before asking which ticket or action — resolve and check the token, silently:
```bash
# Bootstrap exception: the gate runs before any reference loads, so it inlines the resolver.
# Keep this resolve+extract logic in sync with references/jira-token.md (the single source).
R="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -n "$R" ] && git -C "$R" check-ignore -q "$R/.claude/jira-token.local" 2>/dev/null && [ -s "$R/.claude/jira-token.local" ]; then TOKEN_FILE="$R/.claude/jira-token.local"; else TOKEN_FILE="$HOME/.claude/jira-token.local"; fi
T="$(sed -n '/^[[:space:]]*#/d;s/.*"\([^"]*\)".*/\1/p' "$TOKEN_FILE" 2>/dev/null | head -1)"; [ -z "$T" ] && T="$(grep -vE '^[[:space:]]*(#|$)' "$TOKEN_FILE" 2>/dev/null | head -1)"
case "$(printf %s "$T" | tr -d '\r\n')" in ''|'<'*) echo NO_TOKEN ;; *) echo TOKEN_OK ;; esac
```
- **`NO_TOKEN`** → run **Setup** (write the template, `chmod 600`, open the file in the editor), tell the user to paste their PAT between the quotes and save, then stop. Do **not** ask for a ticket.
- **`TOKEN_OK`** → the token works. Only now, if no ticket or action was named, ask which one — otherwise go straight to Steps.

## When to use this skill

- A bare ticket key matching a configured project (`PROJ-123`), "fetch / pull / show me <KEY>", "what does <KEY> say", or a `https://<JIRA_HOST>/browse/…` URL
- "Comment on <KEY>", "assign <KEY> to <name>", "move / progress <KEY> to <status>", "set <field> on <KEY>", "create a Jira issue"
- The token isn't set up yet, or a call returns `401` / `X-AUSERNAME: anonymous` — run the Setup steps to (re)store the PAT.

## When not to use this skill

- **GitHub issues** — those are `gh issue view <n> --repo <owner/repo>`, a different system. An identifier from another tracker (e.g. `GH-512`) is not a Jira key: don't GET `/issue/GH-512` (it always 404s); offer a JQL search (`summary ~ "GH-512"`) instead.
- **Bulk reporting / dashboards** — this skill is single-ticket read/write, not a JQL analytics tool. A one-off JQL search to *find* a ticket is fine (see references); large exports are out of scope.
- **Atlassian Cloud** — wrong endpoints entirely (`/rest/api/3`, Basic auth, `accountId`, ADF). This skill targets on-prem Data Center only; say so and stop rather than translating.

## Setup — store the per-user PAT (one time, before any call)

Run this once, or whenever a call comes back anonymous/401. The token goes to **your home** `~/.claude/jira-token.local` by default (works from any folder); it goes to a **repo** copy only when that repo is provisioned for it — its `.gitignore` already lists `.claude/jira-token.local`. For a repo target, the gitignore check must pass **before** the token is written. Home needs no gitignore — home is not a repo.

1. **Choose the token target — home by default, the repo only when provisioned** (the same `git check-ignore` predicate the read resolver in `references/jira-token.md` uses; here without the read-only `-s`, since the file does not exist yet).
   ```bash
   R="$(git rev-parse --show-toplevel 2>/dev/null)"
   if [ -n "$R" ] && git -C "$R" check-ignore -q "$R/.claude/jira-token.local" 2>/dev/null; then
     TOKEN_FILE="$R/.claude/jira-token.local"      # provisioned repo
   else
     TOKEN_FILE="$HOME/.claude/jira-token.local"   # personal default — independent of the current folder
   fi
   mkdir -p "$(dirname "$TOKEN_FILE")"
   ```

2. **Have the user create the token in the browser** (can't be automated): `https://<JIRA_HOST>` → avatar (top right) → **Profile** → **Personal Access Tokens** → **Create token** → name it "Claude", **Create**, copy it.

3. **If the target is in a repo, verify git ignores it — before writing** (skip for the home target; home is not a repo):
   ```bash
   case "$TOKEN_FILE" in
     "$R"/*)
       git -C "$R" check-ignore -q "$TOKEN_FILE" || { printf 'Refusing to write: %s is not git-ignored (check for a ! negation rule).\n' "$TOKEN_FILE" >&2; exit 1; }
       git -C "$R" ls-files --error-unmatch "$TOKEN_FILE" >/dev/null 2>&1 && { printf 'Refusing to write: %s is already tracked — run: git rm --cached "%s"\n' "$TOKEN_FILE" "$TOKEN_FILE" >&2; exit 1; } ;;
   esac
   ```
   `git check-ignore -q` is the authoritative ignore test (honors `!` negation — a trailing `!.claude/jira-token.local` wins as last match and exits non-zero); the tracked-check matters because `.gitignore` has no effect on an already-tracked path. A repo target is only chosen in step 1 when the entry already exists, so this is a guard — provision the gitignore in the repo, don't add it here.

4. **Create the token file from a template — the user pastes into the text editor window that opens, never into the chat.** With the **`Write`** tool, write exactly this to `TOKEN_FILE` (only if it is absent or empty — never clobber a real token), then `chmod 600 "$TOKEN_FILE"`:
   ```
   # Your personal Jira Data Center PAT — used only by the jira-dc skill. Git-ignored; NEVER committed.
   #   1. Create it: https://<JIRA_HOST> → avatar → Profile → Personal Access Tokens → Create token
   #   2. Paste it between the quotes below, replacing the whole <...>. Keep the quotes. Save.
   #   Example:  JIRA_TOKEN="NjE2ODk5NDUyMjcy..."
   JIRA_TOKEN="<PASTE_YOUR_JIRA_PAT_HERE>"
   ```
   Then open it for the user (`notepad "$TOKEN_FILE"` on Windows, else `${EDITOR:-nano} "$TOKEN_FILE"`); they replace the `<...>` between the quotes with their PAT and save. **Never** ask them to paste the PAT into the chat, and never write it from a tool-call argument.

5. **Confirm by calling Jira — prove the token, show the person, never the token.** Define `auth_cfg` exactly as **`references/jira-token.md`** specifies — that file is the single source: it reads the token fresh, strips CR/LF, and emits the `Bearer` header on the `-K -` stdin directive, so don't re-inline its extraction here. Success is the returned `displayName`, not "saved ok":
   ```bash
   # auth_cfg + TOKEN_FILE per references/jira-token.md (single source); TOKEN_FILE was set in step 1
   PAIR="$(auth_cfg | curl -sS -K - "https://<JIRA_HOST>/rest/api/2/myself" \
     | grep -o '"displayName":"[^"]*"' | grep -m1 .)"
   NAME="${PAIR#*\":\"}"; NAME="${NAME%\"}"
   [ -n "$NAME" ] && printf 'Connected as: %s\n' "$NAME" || { printf 'Saved, but Jira rejected the token — re-run setup with a fresh PAT.\n' >&2; exit 1; }
   ```
   Empty `NAME` (or `X-AUSERNAME: anonymous`) means the PAT was not accepted: mistyped, expired/revoked, or the header was malformed. Re-run from step 2.

## Steps (every read/write call)

1. **Resolve the token (silently), else set it up.** Resolve `TOKEN_FILE` and define `auth_cfg` exactly as **`references/jira-token.md`** specifies (repo copy if present, else home; read fresh; fed to curl only via `-K -` stdin, CR/LF stripped, never printed) — that file is the single source, don't re-inline the logic. If the token is absent → run Setup. Then set the base URL:
   ```bash
   BASE="https://<JIRA_HOST>/rest/api/2"
   ```

2. **Read freely** — auth via the same stdin config path as writes, never `-H`/argv. Project the fields the Output format needs and resolve custom-field names with `expand=names`:
   ```bash
   auth_cfg | curl -sS -K - -G "$BASE/issue/PROJ-123" \
     --data-urlencode "fields=summary,description,status,issuetype,priority,assignee,reporter,components,labels,parent,fixVersions,created,updated,issuelinks,comment,attachment" \
     --data-urlencode "expand=names"
   ```
   Append any Configuration-listed `customfield_NNNNN` ids to `fields=`. `description` and comment `body` are **wiki-markup plain strings** on DC, not ADF. `assignee`/`reporter` are `{name, displayName,…}` or `null` (Unassigned). Each `issuelinks[]` entry has a `type` plus an `inwardIssue` or `outwardIssue` (use `type.inward`/`type.outward` for the relationship phrase). See `references/jira-dc-api.md` for comments paging, attachment download, JQL search, and custom-field discovery.

3. **For a write, draft it and stop for confirmation.** Compose the exact curl (endpoint, method, JSON body) and show it. State precisely what changes (which ticket, comment text, new assignee, target status, or the issue to be created). Get an explicit yes via AskUserQuestion before sending. No yes → don't send; offer to revise the draft.

4. **Discover before you guess.** For a transition ("progress the ticket"), GET the valid transitions from the issue's current state and pick the `id` — never hardcode (`name` "Done" maps to different ids per workflow). For an assignee, resolve the username with `/user/search?username=<fragment>` and use `.name` — **if `username=` returns empty (some DC/GDPR-mode builds), retry with `query=<fragment>`**. For create, pull `createmeta` to learn required fields. For custom fields, use `expand=names`/`editmeta` to get the real `customfield_NNNNN` and its value shape — **never guess a field id**. (Recipes in `references/jira-dc-api.md`.)

5. **Send the confirmed write** — auth header and `Content-Type` both via stdin config so neither the token nor any header lands in argv. Writes/transitions/assign succeed with **`204 No Content` (empty body)** — don't parse JSON on success; create returns `{id,key,self}` on `201`:
   ```bash
   { auth_cfg; printf 'header = "Content-Type: application/json"\n'; } \
     | curl -sS -K - -X POST "$BASE/issue/PROJ-123/comment" -d '{"body":"Plain *wiki* text."}'
   ```

6. **Report and stop.** Reads → the requested fields, readably. Writes → confirm the result (new comment id, `204`, new key) per Output format. On any failure, capture the body — DC returns `{"errorMessages":[…],"errors":{…}}` naming the exact field — and report the status + that message. Do not retry a 4xx blindly, do not widen into unrequested edits.

## Output format

**Read** — lead with the ticket **Link** as the first table row (emit it immediately, even before the fetch returns), then the rest of the key-details **table**, then description, linked issues, comments, and attachments, plus a section per configured custom field. Omit a section with no data (show `— none` for attachments when the user asked for the whole ticket). Render wiki markup; dates as `YYYY-MM-DD`; people by `displayName`; `—` for any empty field. If your instance runs Jira Software, sprint/epic/story-point fields exist as instance-specific `customfield_NNNNN` ids — discover them once via `expand=names`, add them to Configuration, and render them as extra table rows (the DC sprint field is a serialized string array: show each embedded `name=…`; the last is the active sprint).
```
# <KEY> — <summary>

| Field          | Value |
|----------------|-------|
| Link           | https://<JIRA_HOST>/browse/<KEY>             |
| Type           | <issuetype>                  |
| Status         | <status>                     |
| Priority       | <priority>                   |
| Assignee       | <displayName \| Unassigned>  |
| Reporter       | <displayName>                |
| Component(s)   | <comma list \| —>            |
| Labels         | <comma list \| —>            |
| Fix version(s) | <comma list \| —>            |
| Parent         | <KEY — summary \| —>         |
| Created        | <YYYY-MM-DD>                 |
| Updated        | <YYYY-MM-DD>                 |

**Description**
<description, rendered from wiki markup>

**<Configured custom field>**
<value, or "— none">

**Linked issues (<n>)**
- <relationship, e.g. "relates to"> <KEY> — <summary> [<status>]

**Comments (<n>)**
- <author> (<YYYY-MM-DD>): <body>

**Attachments (<n>)**
- <filename> (<size>, <mimeType>)
```

**Write (after confirmed send):**
```
jira-dc: <DONE | FAILED> — <action> on <KEY>
  → <result: comment #45123 added | progressed to Done (204) | field set (204) | created PROJ-129 | assigned to <username>>
  [on FAILED] HTTP <code>: <errors.<field> message from the response body>
```

## Rules — non-negotiables

The Steps are the procedure; these rails never bend:

- **Data Center, not Cloud.** `/rest/api/2`, `Bearer <PAT>`, identity by `name`/`username` (never `accountId`), wiki-markup text (never ADF JSON). Cloud idioms get rejected on DC.
- **Token secrecy is absolute.** Never echo, print, or return it — confirm via `displayName`, never the secret; **no `curl -v`, no `set -x`** while it's in scope (they spew headers). Feed it only via the `-K -` stdin `header = "…"` directive (never `-H`/argv), and run curl through the **Bash tool, never PowerShell**. Store it nowhere but the gitignored `.claude/jira-token.local` (home, or a provisioned repo copy) — **never an env var** — and never narrate the resolved path. (Resolution lives in `references/jira-token.md`.)
- **Writes drafted + confirmed.** Show the exact request and what it changes; send only on an explicit yes. Never invent a username, transition id, status, or field value — discover or ask. For a repo token target, never write before `git check-ignore` confirms it's ignored, nor if the path is already tracked (home needs no gitignore).
- **Deleting tickets isn't part of this skill — on purpose.** It never issues an `-X DELETE` against Jira. Deletion is permanent and can't be undone, so it's deliberately left out to keep a stray request from doing irreversible harm. If someone asks to delete a ticket, explain that warmly and point them to do it themselves in the Jira UI — open the ticket on `https://<JIRA_HOST>` and use its **⋯ / More** actions menu → **Delete** (subject to their permissions) — then offer to help with whatever they actually need on it.
- **On failure, lead with the verdict** and quote the DC `errors` field, not a generic "it failed".

For the full curl cheat-sheet — fetch/comment/attachment/JQL/create/transition/assign/edit with exact endpoints, field shapes, the `X-AUSERNAME: anonymous` auth trap, the `username=`→`query=` user-search fallback, and the DC-vs-Cloud pitfall checklist — read `references/jira-dc-api.md`.
