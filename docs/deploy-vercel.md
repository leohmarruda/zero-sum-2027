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

Python deps: Vercel installs via the backend service `installCommand`
(`pip install -r requirements.txt`). `pyproject.toml` only holds
`[tool.vercel]` / pytest config so it does not steal install from an empty
`[project]` table.

## Local

- API: `http://127.0.0.1:8000/api/...`
- UI: set `VITE_API_BASE=/api` in the **repo-root** `.env` (Vite `envDir`)
- Single env file for backend + frontend: repo-root `.env` only

## Caveats

- Resolve-turn runs 3 LLM calls — may hit serverless timeouts on Hobby.
- Without Turso, game state in `/tmp` is lost between cold starts.
