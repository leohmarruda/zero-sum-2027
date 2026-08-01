# Dev Plan — Zero Sum 2027

> Tier Lite. DoD (task/feature/phase/project) segue `framework-v1.8.md`
> §3.1 — aplicado por referência, não duplicado aqui. Prompts de
> implementação usam `PROMPT_CONTEXT_zero-sum-2027.md` como bloco padrão.

---

## Fase 1 — Core Loop via API

**Goal:** uma partida completa jogável via chamadas de API (sem UI polida),
do turno 1 até vitória/empate, com a invariante zero-sum garantida.

**Estimated effort:** L (5+ sessões — é a fase mais densa: domain, LLM
wrapper, orquestração e persistência todos nascem aqui)

**Depends on:** — (nenhuma, primeira fase; 3.0 Prerequisites já concluído)

**Tasks:**
1. Scaffold FastAPI + SQLAlchemy async; modelos `Game`, `Seat`, `TurnMove`,
   `ScoreSnapshot`, `DMAdjudication` (spec.md §2.6); migração Alembic
   inicial.
2. Domain layer (puro, sem I/O): normalização proporcional zero-sum
   (ADR-004), cálculo de streak, avaliação de vitória/empate (regras de
   `project-proposal.md` §1.3).
3. `app/llm` — anti-corruption layer sobre `llmcall`: (a) geração de move
   por assento de IA, (b) chamada de arbitragem do DM pedindo JSON
   estruturado (`world_narrative`, `seat_feedback`, valores por categoria).
4. Turn Service — orquestra: coletar moves → gerar moves de IA em paralelo
   → acionar DM → normalizar (domain) → persistir → avaliar fim de jogo.
5. Rotas da API (spec.md §2.11), envelope de erro único.
6. **Task de segurança nomeada (M2.14):** isolar `move_text` como conteúdo
   citado no prompt do DM; escrever e rodar 2-3 tentativas de prompt
   injection contra o DM Service; documentar resultado em
   `execution-log.md`.
7. Estimar custo de uma partida completa (~60 turnos) via `dry_run` do
   `llmcall` (assunção #4 do Gate A).

**AI Agent Prompts:** `PROMPT_IMPL_domain-zero-sum.md`,
`PROMPT_IMPL_dm-service.md`, `PROMPT_IMPL_turn-service.md`,
`PROMPT_IMPL_api-routes.md`, `PROMPT_TEST_domain.md`,
`PROMPT_SECURITY_prompt-injection.md` — a criar em `/prompts/` no início da
implementação, cada um citando `PROMPT_CONTEXT_zero-sum-2027.md` e o campo
Pattern obrigatório (§3.3).

**Tests:**
- Unit: normalização zero-sum (inclui casos degenerados — DM retorna soma
  ≠100, DM retorna negativo, DM retorna claim implausível sem estrutura
  válida); cálculo de streak; avaliação de vitória (Humanidade antes do
  turno 30 deve ser rejeitada mesmo com score ≥0.9).
- Integration: ciclo de turno completo ponta a ponta com LLM mockado/stub.
- Manual: 3 tentativas de prompt injection via `move_text`, verificar que
  nenhuma altera o resultado além do que a narrativa justificaria.

**Success Criteria:** uma partida simulada (via script ou pytest) roda do
turno 1 até vitória ou empate no teto de 60, sem quebrar a invariante
soma=100 em nenhum turno; custo estimado documentado.

**DoD Checklist:** Task + Feature + Phase level (§3.1), incluindo DRIFT e
PATTERN prompts ao fechar a fase (novos módulos de dados/serviço
introduzidos aqui).

**Risks:**
| Risco | Mitigação |
|---|---|
| Chamada LLM do DM falha/trava o turno | Task não coberta na spec original — decidir estratégia de retry/timeout durante a implementação; log como ADR se near-impossible |
| DM retorna JSON inválido/não estruturado | Retry único; se persistir, fallback determinístico (manter score do turno anterior, narrativa genérica de "falha de comunicação") |
| Custo por partida acima do aceitável | Ajustar para modelos mais baratos por assento; já configurável desde o setup |

---

## Fase 2 — Frontend Setup + Game Screens

**Goal:** telas de Setup e Jogo funcionais, consumindo a API da Fase 1.

**Estimated effort:** M (2-4 sessões)

**Depends on:** Fase 1 (API estável)

**Tasks:**
1. Scaffold React/Vite/Zustand; store de estado de partida.
2. Tela de Setup: formulário de assentos (modelo/temperatura por IA,
   escolha de assento humano — MVP: Humanidade sempre humana, ver spec §2.13).
3. Tela de Jogo: implementar `StatusBar`, `ZeroSumLedger`,
   `TransmissionPanel`, `MovePanel`, `FooterNav` a partir de
   `design/mockup-game-screen.html` e `design/components.md`.
4. 2D Pass B completa para a Tela de Setup (pendência documentada no
   Módulo 2D) — fazer agora, antes de implementar.

**Tests:** component tests (Vitest) para `ZeroSumLedger` (renderização
correta de segmentos a partir de dados), smoke manual do fluxo Setup→Jogo.

**Success Criteria:** usuário consegue configurar uma partida e jogar o
turno 1 na UI real, vendo o placar e a narrativa do DM.

**DoD Checklist:** Feature + Phase level (§3.1) — inclui checagem de drift
de design (implementação vs. `/design/`).

---

## Fase 3 — Placar Visual (recharts) + Fim de Jogo

**Goal:** histórico de score navegável e tela de fim de jogo.

**Estimated effort:** S-M (1-3 sessões)

**Depends on:** Fase 2

**Tasks:**
1. Endpoint `/games/{id}/history` consumido por gráfico `recharts`
   (evolução de score por categoria/turno). 2D Pass A+B da tela de Fim de
   Jogo (pendência do Módulo 2D) antes de implementar.
2. `EndGameSummary`: reusa `ZeroSumLedger` em modo final + gráfico de
   evolução.
3. Tela de Histórico (navegação por turnos passados).

**Tests:** component test do gráfico com dataset fabricado; smoke manual
do fluxo completo até fim de jogo.

**Success Criteria:** ao final de uma partida simulada, a tela de fim de
jogo mostra vencedor/empate e a evolução do placar é legível no gráfico.

**DoD Checklist:** Feature + Phase level (§3.1).

---

## Fase 4 — Polish Mobile-Friendly + Smoke Test Completo

**Goal:** produto pronto para uso solo, responsivo, sem CI formal mas com
smoke-test manual cobrindo o fluxo completo.

**Estimated effort:** S (1-2 sessões)

**Depends on:** Fase 3

**Tasks:**
1. Revisão responsiva de todas as telas em viewport mobile (~375px).
2. Escrever `SMOKE_full-game-flow.md` em `/prompts/` — script manual
   cobrindo setup → N turnos → fim de jogo (substitui CI, conforme ADR-006).
3. Auditoria final: `decisions.md` e `patterns.md` completos; `README.md`
   atualizado com instruções de uso real.
4. Revisitar item pendente do `2D.5` (workflow ponta a ponta em todas as
   telas) e fechar oficialmente.

**Tests:** smoke-test manual completo (script da task 2), rodado ao menos
1x do início ao fim.

**Success Criteria:** success definition do Gate A satisfeita — partida
completa jogável sozinho, sem travar, placar coerente.

**DoD Checklist:** Project level (§3.1) — success definition do Gate A
verificada explicitamente.

---

## Registro de mudanças de fase (§3.3b)

- **2026-08-01 — Fase 1 fechada.** Success criteria satisfeitos via
  `tests/test_full_game.py` (vitória no turno 10; empate no 60; invariante
  soma=100). Custo ~$0.068/60 turnos documentado. Sem mudança de escopo
  Minimal; live-LLM spot-check deferido.
