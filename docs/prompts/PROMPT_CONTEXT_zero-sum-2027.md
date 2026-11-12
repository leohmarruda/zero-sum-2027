# PROMPT_CONTEXT_zero-sum-2027.md

> Bloco de contexto padrão — colar no topo de todo prompt IMPL/TEST/REFACTOR.
> Revisado e atualizado a cada fechamento de fase (Phase-level DoD, §3.1).

**Projeto:** Zero Sum 2027 — jogo de chat single-player em turnos. Lineup
configurável a partir de um catálogo de facções (default: HWG + Defender AI
+ Selfish AI) + **Narrator** fixo (não pontua). Turnos cegos e simultâneos;
o Narrator checa plausibilidade, narra o desfecho e redistribui um placar
zero-sum de 5 categorias (`pc` computing power, `rc` resources, `cs` supply
chain, `ic` infrastructure, `sm` coercive power — defs em
`app/domain/types.py`), sempre somando 100% entre **todas** as facções
pontuadas da partida.
1 turno = 1 mês narrativo, a partir de 2027-01-01. Vitória: score ≥0.9 por
10 turnos consecutivos (HWG/US/China/UE só a partir do turno 30); teto de
60 turnos, empate se ninguém vencer até lá.

**Roles (API keys):** `paperclip_max`, `selfish_ai`, `paternalistic_ai`,
`defender_ai`, `exterminator_ai`, `hwg`, `us`, `china`, `eu`, `het`,
`gray_aliens`, `narrator`. Display names e prompts em `app/llm/prompts.py`
/ `app/domain/roles.py`. Seat opcional `display_name`.

**Stack:** Python 3.11+ / FastAPI / SQLAlchemy async · `llmcall` (LiteLLM/
OpenRouter) · React 19/Vite/Zustand · i18n EN-US/PT-BR · recharts · SQLite
(dev) / Turso (prod) · Vercel.

**Arquitetura:** Layered (Presentation/Service/Repository/Data). Domain
layer não importa infraestrutura diretamente (DIP). Anti-corruption layer
em `app/llm` traduz entre `llmcall`/provider e os tipos de domínio.
Serviço de arbitragem ainda nomeado `dm_service` (legado).

**Resumo do pattern register:** ver `patterns.md` — Repository para dados,
Result/Either para erros em domínio/serviço, exceptions só em fronteiras de
I/O, 12-Factor config, async/await.

**Invariante crítica:** toda `ScoreSnapshot` de um turno deve somar
exatamente 100 por categoria entre **todas** as facções pontuadas
(ADR-004 — normalização proporcional no domain layer, nunca confiar
cegamente na saída bruta do LLM).

**Fase atual:** Módulo 3, **Fase 2 em andamento** (frontend Setup/Jogo +
catálogo de roles / i18n / gate de plausibilidade). Fase 1 (API core loop)
concluída; migração `002_roles_expand`.

**Decisões arquiteturais recentes:** ADR-001 (Layered) · ADR-002 (stack)
· ADR-003 (persistência single-game) · ADR-004 (normalização zero-sum) ·
ADR-005 (tooling UI) · ADR-006 (testing) · ADR-007 (catálogo N-seat +
Narrator/HWG).
