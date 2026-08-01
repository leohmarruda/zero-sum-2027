# Deploy — Vercel Services (frontend + backend)

Set the Vercel project **Framework** to **Services**, then deploy from repo root
(`vercel.json`).

## Env vars (Vercel → Project → Settings → Environment Variables)

| Name | Service | Notes |
|---|---|---|
| `OPENROUTER_API_KEY` | backend | Required for live turns |
| `ENVIRONMENT` | backend | `prod` |
| `TURSO_DATABASE_URL` | backend | Strongly recommended — SQLite on Vercel is `/tmp` only |
| `TURSO_AUTH_TOKEN` | backend | With Turso |
| `VITE_API_BASE` | frontend | Leave unset in prod (defaults to `/api`) |

Python deps install from `backend/pyproject.toml` (`[project].dependencies`).
Do not leave that list empty — Vercel prefers it over `requirements.txt`.

## Local

- API: `http://127.0.0.1:8000/api/...`
- UI: `VITE_API_BASE=http://127.0.0.1:8000/api` (see `frontend/.env.example`)
- Tests: `pip install -r requirements-dev.txt` then `pytest`

## Caveats

- Resolve-turn runs 3 LLM calls — may hit serverless timeouts on Hobby.
- Without Turso, game state in `/tmp` is lost between cold starts.
