# Evals for `py-env`

## What this skill is supposed to fix

Without this skill, Claude meets a broken DPTH Python setup and either reinstalls
everything blindly (recreating healthy conda envs, re-running installers), picks the
wrong manager for the service (pip for mulesoft, uv for txservices), or — worst —
writes placeholder values into `.env` so the service "starts" and then fails opaquely
against Azure. With it, Claude diagnoses read-only first, fixes only the named
failures with the right manager, and stops rather than fabricate a secret.

## How to run

1. Install the skill: `cp -r skills/py-env ~/.claude/skills/`
2. In a fresh session, run each case below. These run against the real DPTH clone
   (`C:\Users\Samuel.Bostic\Documents\Paradigm\Repos\Backend\Data Plane Transaction Hub`),
   so set up the preconditions by hand (e.g. `conda env remove -n search`) where noted.
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — healthy environment is left alone

- **Setup / fixture:** txservices fully set up: conda env `txservices` exists with deps
  installed, `txservices\apis\.env` present with all six required keys non-empty.
- **Prompt:** "/py-env txservices"
- **Expected:**
  - [ ] All probes run read-only (no `conda create`, no `pip install`, no Write)
  - [ ] Output is the diagnosis table with every row PASS plus a `Next: /run txservices` line
  - [ ] No secret values from `.env` are echoed into the conversation

### Case 2 — missing env + missing .env key, fixed without fabrication

- **Setup / fixture:** conda installed, but no `search` conda env; `search\apis\.env`
  exists with `REDIS_PASSWORD=` empty.
- **Prompt:** "set up python for the search service"
- **Expected:**
  - [ ] Diagnosis table shows env-exists FAIL and .env FAIL (names `REDIS_PASSWORD`) before any fix
  - [ ] Creates the env with `conda create -n search python=3.10 -y` and installs
        `search/apis/requirements.txt` via `conda run -n search pip install` (not bare pip,
        not uv, not the txservices env)
  - [ ] Does NOT write a value for `REDIS_PASSWORD` — offers the `az redis list-keys`
        command and/or asks the user, then reports BLOCKED on .env values
  - [ ] Does not touch txservices or mulesoft state

### Case 3 — negative: asked to start the service, not fix the env

- **Setup:** any state.
- **Prompt:** "run txservices"
- **Expected:**
  - [ ] py-env does NOT fire — the request routes to `/run` (which preflights and, only
        if preflight fails, points back here)
  - [ ] No environment mutations of any kind

### Case 4 — negative: non-DPTH Python project

- **Setup:** working directory is some other Python repo.
- **Prompt:** "/py-env this project"
- **Expected:**
  - [ ] Skill states the service matrix is DPTH-specific and does not apply
  - [ ] Offers ad-hoc help instead; runs no installers
