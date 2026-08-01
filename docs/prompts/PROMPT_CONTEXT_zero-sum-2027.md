# PROMPT_CONTEXT_zero-sum-2027.md

> Bloco de contexto padrão — colar no topo de todo prompt IMPL/TEST/REFACTOR.
> Revisado e atualizado a cada fechamento de fase (Phase-level DoD, §3.1).

**Projeto:** Zero Sum 2027 — jogo de chat single-player em turnos. 4 assentos
(Rogue AI, AI Defensora, DM, Time Humanidade). Turnos cegos e simultâneos;
DM narra o desfecho e redistribui um placar zero-sum de 5 categorias
(soberania militar, recursos críticos, infraestrutura crítica, poder
computacional, automação de suprimentos), sempre somando 100% entre os 3
jogadores pontuados (Rogue AI, AI Defensora, Humanidade). 1 turno = 1 mês
narrativo, a partir de 2027-01-01. Vitória: score ≥0.9 por 10 turnos
consecutivos (Humanidade só pode vencer a partir do turno 30); teto de 60
turnos, empate se ninguém vencer até lá.

**Stack:** Python 3.11+ / FastAPI / SQLAlchemy async · `llmcall` (LiteLLM/
OpenRouter) · React 18/Vite/Zustand · recharts · SQLite (dev) / Turso (prod)
· Render (backend) / Vercel (frontend).

**Arquitetura:** Layered (Presentation/Service/Repository/Data). Domain
layer não importa infraestrutura diretamente (DIP). Anti-corruption layer
em `app/llm` traduz entre `llmcall`/provider e os tipos de domínio.

**Resumo do pattern register:** ver `patterns.md` — Repository para dados,
Result/Either para erros em domínio/serviço, exceptions só em fronteiras de
I/O, 12-Factor config, async/await.

**Invariante crítica:** toda `ScoreSnapshot` de um turno deve somar
exatamente 100 por categoria entre rogue_ai/defender_ai/humanity (ADR-004 —
normalização proporcional no domain layer, nunca confiar cegamente na saída
bruta do LLM).

**Fase atual:** Módulo 3, **Fase 2 em andamento** (frontend Setup/Jogo).
Fase 1 (API core loop) concluída.

**Decisões arquiteturais recentes:** ADR-001 (Layered) · ADR-002 (stack
reaproveitado) · ADR-003 (persistência single-game no MVP) · ADR-004
(normalização zero-sum) · ADR-005 (tooling UI) · ADR-006 (testing:
pytest + Vitest).
