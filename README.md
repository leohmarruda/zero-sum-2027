# [Nome provisório] — Rogue AI Chat Game

> Nome definitivo será escolhido no Módulo 1.5. Este é um título de trabalho.

## Estado do projeto
- **Fase atual:** Módulo 3 — **Fase 2 em andamento** (frontend Setup + Jogo). Fase 1 API concluída.
- **Effort tier (§0.3):** **Lite** — spike single-player, tempo curto, protótipo.
- **Scope tier (§1.6):** Minimal.

## Compressões permitidas (tier Lite)
- Pular 2D Passes B e C (ou documentar o skip em `execution-log.md`)
- Spec de uma página em vez de spec completa
- M5 formal substituído por 3 testes informais
- CI do M3.0 é opcional — smoke test manual no lugar

## Gatilho de upgrade Lite → Standard (§0.3)
Se um segundo consumidor aparecer, uma superfície de UI multiplayer real for
adicionada além do protótipo single-player, o esforço exceder 3 dias, ou dados
de usuário final entrarem em escopo — upgrade para Standard. Registrar o
gatilho aqui quando ocorrer.

## Instalação (backend)

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example .env   # preencher OPENROUTER_API_KEY quando for usar LLM
uvicorn app.main:app --reload
```

Health check: `GET http://127.0.0.1:8000/health`

Testes: `pytest` (domain + API turn loop + full game + cost dry_run + injection)

## Uso

### Backend
```bash
cd backend
uvicorn app.main:app --reload
# POST /games  →  POST /games/{id}/turns/1/moves  →  POST /games/{id}/turns/1/resolve
```

### Frontend
```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```
Abre `http://127.0.0.1:5173` — Setup → Iniciar → jogar turno 1 (API em `:8000`).

Requires `OPENROUTER_API_KEY` in backend `.env` for live LLM calls (tests use a stub).

Install llmcall (sibling repo): `pip install -e ../../llmcall`
