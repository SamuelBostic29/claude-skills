---
name: py-env
version: 1.0.0
description: |
  Bootstrap or diagnose ONE service's Python environment in the Data Plane
  Transaction Hub repo (txservices, search, mulesoft/Rx). Use when asked to
  "set up python" for a DPTH service, when /run's preflight refuses to start
  one (missing conda env, missing uv, missing .env keys), or when a DPTH
  service hits ModuleNotFoundError / wrong-interpreter errors. Diagnoses
  first, fixes only what failed, and guides .env creation — it never invents
  secret values.
allowed-tools:
  - Read
  - Glob
  - Grep
  - AskUserQuestion
  - Write
  - Bash(conda:*)
  - Bash(uv:*)
  - Bash(python:*)
  - Bash(az:*)
  - Bash(curl:*)
---

# Py-env: bootstrap or diagnose one DPTH service's Python environment

A .NET developer needs a working Python environment for one service in the Data Plane Transaction Hub repo and has likely never used conda, pip, or uv. Your job is the **doctor pattern**: diagnose everything read-only first, report what's broken, then fix only what failed — one service per invocation. The classic failure mode here is cargo-cult repair: reinstalling everything blindly, recreating healthy environments, or — the cardinal sin — fabricating placeholder values into `.env` so the service "starts" and then fails opaquely against Azure.

The acceptance test is `/run`'s preflight (`~/.claude/commands/run.md`, Step 4P): when py-env is done, `/run <service>` must get past preflight. `/run` deliberately refuses to create environments — py-env is the thing that creates them.

## When to use this skill

- "/py-env <service>", "set up python for txservices / search / rx"
- `/run` preflight stopped a DPTH service: missing conda env, missing uv, missing `.env`, empty required keys
- `ModuleNotFoundError`, `conda: command not found`, or wrong-Python-version errors while working in DPTH

## When NOT to use this skill

- **Starting or restarting a service** — use `/run` / `/rebuild`; py-env only makes the environment runnable.
- **Running tests or lint** — use `/py-check`.
- **Python repos other than DPTH** — the service matrix below is DPTH-specific; say so and help ad-hoc instead.
- **Dependency upgrades or lockfile changes** — py-env repairs the *environment*, never the project's dependency declarations.

## The service matrix

Repo root: `C:\Users\Samuel.Bostic\Documents\Paradigm\Repos\Backend\Data Plane Transaction Hub`

| Service | Aliases | Manager | Python | Install deps | `.env` location |
|---|---|---|---|---|---|
| txservices | tx, transaction services | conda env `txservices` | 3.10+ | `conda run -n txservices pip install -r txservices/apis/requirements.txt` | `txservices\apis\.env` |
| search | keyword search | conda env `search` | 3.10+ | `conda run -n search pip install -r search/apis/requirements.txt` | `search\apis\.env` |
| mulesoft (Rx Services) | rx, rxservices | uv (`uv.lock`, `.python-version` = 3.13) | 3.13 | `uv sync` from `mulesoft\` | `mulesoft\.env` |

Required `.env` keys (must exist with non-empty values):

- **txservices:** `COSMOSDB_ENDPOINT`, `COSMOSDB_KEY`, `COSMOSDB_DATABASE`, `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- **search:** `COSMOSDB_ENDPOINT`, `COSMOSDB_KEY`, `COSMOSDB_DATABASE`, `REDIS_HOST`, `REDIS_PASSWORD`
- **mulesoft:** no fixed list — pydantic-settings validates at startup and reports missing fields loudly; py-env only ensures the file exists.

These match `envManager` / `requiredEnvVars` in `~/.claude/service-aliases.json` — if that file and this matrix disagree, the aliases file wins and this matrix needs updating.

## Steps

1. **Identify the service.** From the argument or conversation: txservices, search, or mulesoft. Exactly one per invocation. Ambiguous or absent → AskUserQuestion and stop. (quotation-agentic-ai is out of scope — Poetry/AKS; say so if asked.)

2. **Diagnose — read-only, no mutations.** Use the Bash tool (git-bash); call native exes directly, never via `cmd.exe /c`. Batch into as few calls as possible:
   - Tooling: `conda --version` / `uv --version` (whichever the service needs).
   - Env exists: conda — `conda env list | grep -i <envName>`; uv — `.venv` dir under `mulesoft\`.
   - Interpreter: `conda run -n <envName> python --version` meets the matrix's floor.
   - Deps: probe imports, e.g. `conda run -n <envName> python -c "import flask, azure.cosmos, redis"`. For uv, skip the probe — `uv sync` in step 4 is the idempotent check-and-fix.
   - `.env`: file exists at the matrix path; every required key matches `^KEY=.` (non-empty). **Read key names only — never print secret values into the conversation.**

3. **Report the diagnosis.** Output the table from **Output format** below. Everything PASS → say the environment is healthy, suggest `/run <service>`, and stop.

4. **Fix only what failed, in dependency order.** Confirm via AskUserQuestion before installing *software* (conda/uv themselves); env creation and dep installs inside an already-confirmed manager proceed without re-asking.
   - **conda missing:** user-scope Miniconda (this machine has no admin rights — anything UAC fails): download `https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe` with curl, run with `/InstallationType=JustMe /S /D=%USERPROFILE%\Miniconda3`, then use its full path until the shell picks up PATH.
   - **uv missing:** standalone user-scope installer (installs to `%LOCALAPPDATA%`): `curl -LsSf https://astral.sh/uv/install.ps1 | powershell -NoProfile -Command -` — or tell the user to run `! powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"` if piping misbehaves.
   - **conda env missing:** `conda create -n <envName> python=3.10 -y`, then the matrix's dep install.
   - **Deps missing/broken (conda):** re-run the matrix's `pip install -r ...` — idempotent.
   - **uv env missing/broken:** `uv sync` from `mulesoft\` — creates `.venv`, installs Python 3.13 and locked deps. First run is slow; that's normal.
   - **`.env` missing or keys empty:** list exactly which keys are needed. Values come from the user or from `az` with their go-ahead — `az cosmosdb keys list --name <account> --resource-group <rg> --query primaryMasterKey -o tsv`, `az redis list-keys --name <account> --resource-group <rg> --query primaryKey -o tsv` (endpoints/hosts from the Azure portal or a teammate's `.env`; see `txservices/LOCAL_DEVELOPMENT.md`). Write the file with the Write tool. If the user can't supply a value, leave the key absent and say the service can't start until it's filled — **stop rather than fabricate**.

5. **Re-verify.** Re-run only the probes that failed in step 2. Report the updated table.

6. **Stop.** Done = every row PASS (or `.env` rows explicitly blocked on values only the user can get). Suggest `/run <service>`. Do not start the service yourself.

## Output format

```
py-env: <service> — <HEALTHY | N issues found | FIXED | BLOCKED on .env values>

| Check                  | Result | Detail / fix applied            |
|------------------------|--------|---------------------------------|
| conda/uv installed     | PASS   | conda 24.x                      |
| env exists             | FIXED  | created conda env `search`      |
| interpreter version    | PASS   | 3.10.14 (needs 3.10+)           |
| dependencies           | FIXED  | pip install -r ... (42 pkgs)    |
| .env present + keys    | FAIL   | missing: REDIS_PASSWORD         |

Next: <"/run <service>" | "fill REDIS_PASSWORD in search\apis\.env — fetch with: az redis list-keys ...">
```

## Rules

### What to do

- **One service per invocation.** A second service is a second `/py-env` run.
- **Diagnose before touching anything.** Every fix maps to a named FAIL row.
- **User-scope installers only.** No admin on this machine — Miniconda `JustMe`, uv to `%LOCALAPPDATA%`. If something demands elevation, stop and say so.
- **Idempotent fixes.** `pip install -r`, `uv sync`, `conda create` only when absent — safe to re-run.
- **Secrets flow one way: user/az → `.env`.** Confirm before running `az`; never echo secret values back into the conversation beyond writing the file.

### What NOT to do

- **NEVER invent or placeholder a secret value in `.env`.** A fake `COSMOSDB_KEY` produces auth failures far more confusing than a missing one. Stop and ask.
- **Don't nuke healthy state.** No `conda env remove` / deleting `.venv` unless the user explicitly asks for a from-scratch rebuild.
- **Don't edit `requirements.txt`, `pyproject.toml`, or `uv.lock`.** Environment doctor, not dependency manager — mismatches there are a code change for the team, not a local fix.
- **Don't touch the other services' envs or `.env` files.** Surgical, like `/stop`'s state handling.

### Format discipline

- Diagnosis table first, fixes second, `Next:` line last. No setup narration between Bash calls.
- When healthy on arrival, the entire output is the table plus the `Next:` line.
