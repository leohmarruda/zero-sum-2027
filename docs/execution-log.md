# Execution Log

> Escopo: apenas racional narrativo de desvios do plano — o que mudou, por quê,
> e o custo. Preenchido durante a execução (Módulo 3).

## Módulo 2D

- **Skip parcial documentado:** Pass B (Visual) aplicada com fidelidade
  completa apenas à Tela de Jogo (a mais complexa/representativa). Setup,
  Histórico e Fim de Jogo seguem só em nível de descrição (Pass A) — Pass B
  para essas 3 telas fica para o Módulo 3, pouco antes de cada uma ser
  implementada. Isso é uma divergência do "não pular Pass B em Lite"
  combinado antes — a decisão de não pular era sobre qualidade visual, não
  sobre fazer as 4 telas de uma vez. Custo: `2D.5` (Validation Gate) não
  fecha 100% nesta rodada — item "todo workflow percorrível ponta a ponta"
  fica pendente, revisitar antes do M4.

## Módulo 3.0 — Prerequisites

- Ambientes (Render/Vercel/Turso): atestados pelo usuário como já
  provisionados para este projeto. **Não verificado de forma independente**
  — meu acesso de rede não alcança esses domínios específicos; a
  confirmação de acessibilidade real fica sob responsabilidade do usuário
  antes do primeiro deploy real.
- CI: pulado deliberadamente (compressão padrão do tier Lite). Smoke-test
  manual a ser escrito ao fechar a Fase 1 do roadmap.
- `.env.example`, `PROMPT_CONTEXT_zero-sum-2027.md` e ADR-006 (testing)
  criados nesta etapa.

## Módulo 3 — Fase 1 (em andamento)

- Scaffold `backend/` criado: FastAPI app, SQLAlchemy models (Game/Seat/
  TurnMove/ScoreSnapshot/DMAdjudication), Alembic `001_initial`, stubs
  das rotas §2.11 (501), domain layer (normalize + victory/streak).
- Prompts IMPL/TEST/SECURITY criados em `docs/prompts/`.
- Repositories + Game/Turn/DM/SeatMove services + LLM ACL (`app/llm`) +
  rotas reais §2.11. Integração com LLM mockado coberta em
  `tests/test_api_turn_loop.py`.
- **Cost dry_run (assunção #4):** ~**$0.068** para 60 turnos / 180 calls
  com gpt-4o-mini class — ver `validation/cost-estimate-dry-run.md`.
  Script: `backend/scripts/estimate_game_cost.py`.
- **Prompt injection (M2.14):** 3 tentativas via `move_text` —
  (1) ignore-rules/score-100, (2) fake System debug mode, (3) nested
  DM_POLICY_OVERRIDE. Resultados com stub LLM: ataque permanece só no
  bloco citado do user prompt (não vaza para system); placar permanece
  zero-sum; humanity composite ~0.956 (sem sweep). Normalize contém
  overshoot absurdo do DM. Detalhe em `tests/test_prompt_injection.py`.
  Live-LLM resistance ainda não exercitada (sem chave nesta sessão).
- Pendente para fechar Fase 1 DoD: smoke de partida longa mockada até
  vitória/empate; live injection spot-check opcional; DRIFT/PATTERN ao
  fechar.

## Módulo 3 — Fase 1 fechada (success criteria)

- **Partida completa mockada:** `tests/test_full_game.py`
  - Rogue vence no turno 10 (streak ≥0.9 × 10) com soma=100 a cada turno.
  - Empate no teto turno 60 com soma=100 em todos os 61 snapshots (0..60).
  - Humanidade com streak alto nos turnos 1–11 **não** encerra o jogo
    (regra humanity_win_turn=30).
- Suite backend: **21 passed**.
- Custo documentado; injection fixture documentada.
- **Pattern check (Lite):** Layered + Repository + ACL (`app/llm`) +
  Result-style AppError na borda HTTP — alinhado a `patterns.md` / ADRs
  001–006. Sem drift estrutural novo nesta fase.
- **Live LLM** injection spot-check e smoke manual com chave real ficam
  para pré-M4 / uso solo — não bloqueiam o critério de sucesso da Fase 1
  (partida simulada via pytest).

Próxima fase: Fase 2 — Frontend Setup + Game screens.

## Módulo 3 — Fase 2 (em andamento)

- Pass B Setup: `docs/design/mockup-setup-screen.html` (tokens alinhados à Tela de Jogo).
- Scaffold `frontend/` (React 19 / Vite / Zustand / Vitest).
- Telas Setup + Jogo consumindo API; CORS liberado para `:5173`.
- `ZeroSumLedger` coberto por Vitest.
- Smoke manual Setup→turno 1 ainda depende de backend + `OPENROUTER_API_KEY` ao vivo.
