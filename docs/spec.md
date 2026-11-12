# Spec — Zero Sum 2027

> Tier: Lite (§0.3). Scope: Minimal (§1.6). Referência: `project-proposal.md`,
> `assumption-log.md`, `patterns.md`.
>
> **Atualização (2026-08-02):** o mecanismo de 4 assentos fixos do proposal
> foi expandido — catálogo de facções, Narrator (ex-DM), HWG (ex-Humanidade),
> N assentos pontuados. Ver ADR-007 e `execution-log.md`.

---

## Phase A — O Que Estamos Construindo?

### 2.1 Project Definition
Zero Sum 2027 é um jogo de chat single-player em turnos. O jogador monta um
lineup a partir de um **catálogo de facções** (mínimo 2 playable + Narrator
fixo), escolhe qual assento é humano e dá nomes customizados opcionais.
Turnos são cegos (1 mês narrativo, a partir de 2027-01-01). O **Narrator**
recebe as jogadas em texto livre, checa plausibilidade no horizonte de um
mês, narra o desfecho (incluindo eventos externos plausíveis) e redistribui
um placar de poder de 5 categorias, **zero-sum entre todos os assentos
pontuados** (ver §2.1.1). Jogo termina quando um jogador mantém score ≥ 0.9 por 10
turnos consecutivos (polities humanas — HWG/US/China/UE — só podem vencer
a partir do turno 30) ou no teto de 60 turnos. No teto, se a **Defender AI**
está em jogo e nenhum assento passou de composite 0,60 nos últimos 10 turnos,
ela vence por **contenção**; caso contrário, empate. O final recebe um tipo
(`hegemony`, `containment`, `uneasy_hegemony`, `bipolar_standoff`,
`multipolar_balance`) e um epílogo escrito pelo Narrator (ADR-008).

**Catálogo de roles (API keys):**

| Key | Display |
|---|---|
| `paperclip_max` | Paperclip Maximizer (PMAX) |
| `selfish_ai` | Selfish AI |
| `paternalistic_ai` | Paternalistic AI (PAI) |
| `defender_ai` | Defender AI (DAI) |
| `exterminator_ai` | Exterminator AI (EAI) |
| `hwg` | Human World Government (HWG) |
| `us` | United States (US) |
| `china` | China |
| `eu` | European Union (UE) |
| `het` | Human Extinction Terrorists (HET) |
| `gray_aliens` | Grey Aliens (GREYS) |
| `narrator` | Narrator (sempre presente; não pontua) |

**Default lineup:** HWG + Defender AI + Selfish AI (+ Narrator).

#### 2.1.1 Dimensões de poder (5 categorias)

Cada categoria é zero-sum entre os assentos pontuados (soma = 100). Chaves
de API/DB estáveis; rótulos e significado abaixo.

| Key | Dimensão | O que é |
|---|---|---|
| `pc` | Computing power | FLOPs de fronteira e sua alocação: chips, clusters, contratos de inferência, pesos de modelos |
| `rc` | Resources | Insumos primários não substituíveis em ≤12 meses: energia primária, minerais críticos, capacidade de litografia, água industrial |
| `cs` | Supply chain | Capacidade de transformar insumo em bem: fabs, linhas de montagem, robótica industrial, logística de carga |
| `ic` | Infrastructure | Redes de continuidade social: grid, telecom, sistema financeiro, água/saneamento, saúde |
| `sm` | Coercive power | Capacidade de impor resultados por força ou ameaça: forças armadas, ciberofensiva, aplicação da lei, controle territorial |

Fonte canônica no código: `SCORE_CATEGORY_DEFS` em `app/domain/types.py`
(também injetada no prompt do Narrator).

### 2.2 Features (scope tier: Minimal — único tier deste projeto)
| Feature | Descrição |
|---|---|
| Setup de partida | Montar lineup (add/remove facções, exceto Narrator); escolher assento humano; nome customizado; modelo + Imprevisibilidade (temperature) por IA; estimativa de custo da partida |
| Turno cego | Usuário submete texto livre para seu assento; backend gera moves dos assentos de IA sem exposição mútua |
| Gate de plausibilidade | Antes de resolver o mês, o Narrator pode rejeitar jogadas humanas grosseiramente implausíveis (retorno ao jogador) |
| Arbitragem do Narrator | Consome as jogadas + estado atual; retorna narrativa + redistribuição zero-sum estruturada (JSON) por categoria; feedback individualizado |
| Canal `/off` | Pergunta lateral ao Narrator (sem resolver o turno) |
| Placar visual | Histórico de score por categoria/turno (`ZeroSumLedger`; gráfico recharts na Fase 3) |
| Detecção de vitória/empate | Streak de 10 turnos ≥0.9; delayed-win para HWG/US/China/UE a partir do turno 30; teto de 60 turnos |
| i18n | UI EN-US / PT-BR; narrativas do Narrator seguem o locale da partida |
| Histórico de partida | Log de turnos jogados, navegável, dentro da partida corrente |

**Fora de escopo (Minimal):** multiplayer real (2+ humanos), persistência
entre partidas/perfis de usuário, customização de regras (categorias,
pesos, teto de turnos) via UI, replay compartilhável.

### 2.3 UI Overview (leve — detalhado no Módulo 2D)
- **Tela de Setup:** lineup editável, Imprevisibilidade, nomes, estimativa
  de custo, intro do Narrator.
- **Tela de Jogo:** jogada em texto livre + placar (`ZeroSumLedger`, N
  segmentos) + transmissão do Narrator + canal off + footer de elegibilidade.
- **Tela de Histórico:** navegação por turnos passados dentro da partida.
- **Tela de Fim de Jogo:** resultado (vencedor/empate) + gráfico de
  evolução do placar ao longo da partida.

Requisito não-funcional explícito: interface web, visualmente cuidada,
mobile-friendly. Ver `execution-log.md` — Pass B do 2D não será pulado
apesar do default do tier Lite.

**Checkpoint (assumption-log):** nenhuma assunção foi invalidada por este
trabalho de spec; assunção #1 segue `Validated (parcial)` (ver Gate A) —
revalidação N>3 é critério de entrada da Fase 3. Assunção #4 (custo)
permanece válida para o **default lineup**; partidas com mais facções IA
escalam o custo linearmente. #2/#3 Superseded (pré-build); #5 prioridade
elevada pós-ADR-007.

---

## Phase B — Como É Estruturado?

### 2.4 Architecture
**Layered** (default de `patterns.md`) — Presentation (React) / Service
(regras de turno, validação zero-sum) / Repository (SQLAlchemy async) /
Data (SQLite dev, Turso prod). Sem justificativa para Event-driven
(nenhum desacoplamento assíncrono é proposta de valor) nem Microservices
(deploy único). Ver ADR-001.

### 2.5 Stack
Reaproveitado do restante do portfólio — sem gap concreto que justifique
divergir (ver ADR-002):
- Backend: Python 3.11+ / FastAPI / SQLAlchemy async
- LLM: `llmcall` (wraps LiteLLM) — usado para assentos de IA + Narrator;
  suporta `dry_run` para estimar custo por partida (assunção #4 do Gate A)
- Frontend: React 19 / Vite / Zustand; i18n próprio (`frontend/src/i18n`)
- Visualização: `recharts` (Fase 3)
- Embeddings: não aplicável
- DB: SQLite (dev) / Turso libSQL (prod)
- Deploy: Vercel (frontend + backend serverless) — ver `deploy-vercel.md`

### 2.6 Data Architecture
**Repository pattern** (default). Entidades principais:

| Entidade | Campos-chave |
|---|---|
| `Game` | id, created_at, status (`setup`\|`in_progress`\|`ended`), current_turn, turn_cap=60, humanity_win_turn=30, winner (nullable), ended_at |
| `Seat` | id, game_id, role (string catalog key), player_type (`human`\|`ai`), display_name (nullable), model, temperature |
| `TurnMove` | id, game_id, turn_number, seat_role, move_text, created_at |
| `ScoreSnapshot` | id, game_id, turn_number, seat_role, sm, rc, ic, pc, cs (cada categoria 0-100; um row por facção pontuada) |
| `DMAdjudication` | id, game_id, turn_number, world_narrative, world_state_digest (digest rolante ~200–400 tok), seat_feedback (JSON: 1 texto por seat_role), raw_llm_response, created_at |
| `WinStreak` | game_id, seat_role, current_streak_turns (derivado — recalculável a partir de `ScoreSnapshot`) |

**Invariante crítica:** para cada `turn_number`, a soma de cada categoria
(sm, rc, ic, pc, cs) entre **todos** os `ScoreSnapshot` das facções
pontuadas da partida deve ser exatamente 100. Ver ADR-004.

**Estado inicial (turno 0):** se HWG está no lineup, HWG começa ~100% em
todas as categorias (98% compute); demais facções começam em 0% (1%
compute cada), depois normalizado. Sem HWG: split igual.

### 2.7 Infrastructure
Vercel (API + frontend) + Turso (prod DB) — ambientes dev/prod. Confirmar
operacional antes do deploy real. Ver `deploy-vercel.md`.

**ADRs desta fase:** ver `decisions.md` ADR-001 a ADR-007.

---

## Phase C — Como É Organizado?

### 2.8 Project Structure
```
/backend
  /app
    /domain        # roles catalog, zero-sum, streak / victory
    /services       # turn, narrator (dm_service), seat_move, game
    /repositories
    /api            # rotas FastAPI
    /llm            # prompts canônicos + ACL sobre llmcall
  /tests
/frontend
  /src
    /components     # SetupForm, StatusBar, ZeroSumLedger, …
    /pages
    /store          # Zustand
    /i18n
    /api            # cliente HTTP
    /lib            # costEstimate, narratorIntro
```

### 2.9 Modules & Responsibilities
- **Domain (`app/domain`):** catálogo de roles, normalizar zero-sum N-way,
  streaks, vitória/empate (delayed-win polities). Sem I/O.
- **Narrator / DM Service:** monta prompt de arbitragem (+ gate de
  plausibilidade + canal `/off`), chama `llmcall`, valida JSON contra o
  domain. Nome interno do módulo ainda `dm_service` (legado).
- **Turn Service:** orquestra o ciclo (coletar moves → IA em paralelo →
  Narrator → normalizar → persistir → avaliar fim).
- Domínio não importa `llmcall` nem SQLAlchemy diretamente (DIP).

### 2.10 Workflows
1. Setup: usuário monta lineup (default HWG/DAI/SA + Narrator), escolhe
   assento humano, nomes, modelos → `Game` criado, `status=in_progress`,
   turno 1; scores iniciais no turno 0.
2. Turno N: humano submete `move_text` (opcionalmente consulta `/off`);
   backend gera moves dos assentos IA em paralelo (contexto: scores, digest
   e narrativa pública do mês anterior, feedback privado próprio; sem
   jogadas alheias do turno corrente).
3. Resolve: gate de plausibilidade pode rejeitar a jogada humana; caso
   aceite, Turn Service aciona Narrator.
   Em ~20% dos turnos (a partir do 3) um **evento de mundo** semeado por
   `game_id` + turno é injetado no prompt do Narrator (`app/domain/events.py`).
4. Narrator retorna JSON: `world_narrative`, `world_state_digest`,
   `seat_feedback`, scores por
   categoria por facção pontuada.
5. Domain normaliza/clampa para somar 100 por categoria (ADR-004);
   persiste `ScoreSnapshot` + `DMAdjudication`.
6. Domain avalia streaks e vitória/empate; se atingida, `status=ended`,
   grava `ending` e uma chamada extra do Narrator grava `epilogue`.
7. Frontend renderiza narrativa + placar com deltas por turno
   (`TurnOut.deltas`) + (se aplicável) tipo de final e epílogo.
8. `replay` re-executa resolução do turno (dev/debug).

### 2.11 Interfaces (API)
Envelope de erro único: `{"error": {"code": str, "message": str}}`.

| Método | Rota | Descrição |
|---|---|---|
| GET | `/content` | Copy de setup/intro do Narrator por locale |
| POST | `/games` | Cria partida; body opcional: seats (role/player_type/model/temperature/display_name) + locale |
| GET | `/games/{id}` | Estado atual: turno, status, placar, seats |
| POST | `/games/{id}/turns/{n}/moves` | Submete a jogada do assento humano |
| POST | `/games/{id}/turns/{n}/off` | Pergunta lateral ao Narrator (não resolve o turno) |
| POST | `/games/{id}/turns/{n}/resolve` | Gera moves de IA + arbitragem (idempotente; pode retornar `rejected`) |
| POST | `/games/{id}/turns/{n}/replay` | Re-resolve o turno |
| GET | `/games/{id}/turns/{n}` | Moves + narrativa + score |
| GET | `/games/{id}/history` | Série histórica de score por categoria/turno |

Anti-corruption layer: `app/llm` traduz entre `llmcall`/provider e tipos
de domínio. Prompts canônicos em `app/llm/prompts.py`.

---

## Phase D — Como Entrega?

### 2.12 Development Dependencies
`llmcall`, FastAPI, SQLAlchemy async, Alembic, React 19/Vite/Zustand,
recharts (Fase 3), pytest, Vitest.

### 2.13 MVP Definition
Uma partida jogável do início ao fim (turno 1 até vitória/empate), lineup
configurável a partir do catálogo (default HWG/DAI/SA), 1 assento humano
escolhível (qualquer playable), placar visual funcional, i18n EN/PT.
Tela de histórico navegável e gráfico recharts ficam para Fase 3.

> **[Open Gate — 2.13]** *Resolvido na implementação:* o humano pode
> ocupar qualquer facção playable (não só HWG). Narrator permanece IA.

### 2.14 Security & Privacy Check (tier Lite — riscos em assumption-log, não ADR)
- **Prompt injection via move_text:** isolado como conteúdo citado no
  prompt do Narrator; fixtures em `tests/test_prompt_injection.py`.
- **Exposição de chave de API:** chamadas `llmcall` só no backend.
- **Sem dados pessoais de usuário final** no MVP (sem login/conta).

### 2.15 Roadmap
| Fase | Objetivo | Depende de | Critério de entrada |
|---|---|---|---|
| 1 | Core loop jogável via API | — | Nenhuma |
| 2 | Frontend Setup + Game (+ catálogo de roles, i18n) | Fase 1 | API estável |
| 3 | Placar visual (recharts) + tela de fim de jogo | Fase 2 | Endpoints history/turn **+ Gate A revalidado com N>3** (assunção #1; ver `dev-plan.md` Fase 3) |
| 4 | Polish mobile-friendly + smoke test manual completo | Fase 3 | Fluxo completo em desktop |

### 2.16 Output
Este arquivo (`spec.md`).

### 2.17 Critical Evaluation (`PROMPT_CHALLENGE_SPEC`, resumo)
1. **Mais provável de estar errado:** normalização proporcional (ADR-004)
   com N>3 facções pode diluir julgamento narrativo de forma menos legível.
   **Dono/gate:** revalidação Gate A N>3 = critério de entrada da Fase 3
   (`dev-plan.md`); não fica pendência órfã.
2. **Maior exposição de dependência:** `llmcall` / OpenRouter — falha do
   Narrator trava o turno; gate de plausibilidade adiciona 1 call extra
   por resolve humano.
3. **MVP ainda mínimo?** O catálogo expandiu o Minimal original; ainda é
   single-player sem multi-partida. Custo e complexidade de prompt sobem
   com N.
4. **ADRs:** ADR-007 documenta a expansão de roles sem invalidar 001–006.
5. **Assunções:** #4 (custo) precisa ser lida como “default lineup”;
   reestimar quando N cresce. #2/#3 Superseded (pré-build). #5 (teto 60)
   prioridade elevada pós-ADR-007 — observar na mesma revalidação N>3.
