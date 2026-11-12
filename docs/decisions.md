# Architecture Decision Records

---

ADR-000
Decision:          adr-tools (markdown puro, arquivos em `decisions.md`)
Context:           Tier Lite, protótipo single-player, desenvolvedor solo.
                    Não há necessidade real de revisar histórico de ADR via UI.
Pattern baseline:  N/A
Alternatives:      Log4brains (UI navegável, setup adicional)
Rationale:         Zero overhead de setup; adequado ao ritmo de um spike Lite.
Reversibility:     Easy
Consequences:      ADRs vivem como entradas markdown neste arquivo, sem
                    ferramenta a instalar ou manter.

---

ADR-001
Decision:          Arquitetura Layered (Presentation / Service / Repository / Data)
Context:           Módulo 2, Fase B. Jogo turn-based, sem requisito de
                    desacoplamento assíncrono nem deploy independente.
Pattern baseline:  Application Architecture (patterns.md, default)
Alternatives:      Event-driven, Microservices
Rationale:         Nenhum dos dois requisitos de escalada (desacoplamento
                    async como proposta de valor central; deploy
                    independente presente e real) se aplica.
Reversibility:     Costly
Consequences:      Estrutura de pastas e fluxo de dados seguem o padrão
                    Layered já usado nos outros projetos do portfólio.

---

ADR-002
Decision:          Reaproveitar o stack do portfólio: Python/FastAPI/
                    SQLAlchemy async + llmcall + React 18/Vite/Zustand +
                    recharts (novo) + SQLite dev/Turso prod + Render/Vercel
Context:           "É um jogo" sugeria evolução para game engine
                    (Phaser/Pixi/Godot); análise mostrou que o jogo é
                    turn-based sem loop de física/frame, portanto não há
                    gap real que justifique divergir do stack existente.
Pattern baseline:  N/A (stack, não pattern estrutural)
Alternatives:      Phaser/PixiJS (renderização em tempo real, descartado
                    por YAGNI — sem requisito de física/animação contínua)
Rationale:         Divergir sem um gap concreto viola o próprio
                    patterns.md ("preferimos controle" não é um gap).
                    recharts cobre a única necessidade nova real
                    (visualização de série temporal de score).
Reversibility:     Costly
Consequences:      Zero custo de aprendizado de ferramenta nova; reuso de
                    llmcall com suporte a dry_run para estimar custo por
                    partida (assunção #4 do Gate A).

---

ADR-003
Decision:          Persistência única por partida no MVP (sem perfis/
                    contas de usuário, sem partidas entre sessões
                    persistidas além da corrente)
Context:           Scope tier Minimal — menor coisa que prova a ideia.
Pattern baseline:  N/A
Alternatives:      Persistência multi-partida com histórico de usuário
Rationale:         Fora de escopo do Minimal (ver spec.md secao 2.2);
                    adiado para um eventual scope Full.
Reversibility:     Easy
Consequences:      Schema já suporta múltiplas Game rows (não é
                    tecnicamente limitado), mas UI/API não expõem listagem
                    entre partidas no MVP.

---

ADR-004
Decision:          Extração de score via JSON estruturado no prompt do DM,
                    com normalização/clamp obrigatória no domain layer para
                    garantir soma = 100 por categoria
Context:           LLMs não garantem aritmética exata; a invariante
                    zero-sum (soma 100 por categoria) é crítica para o
                    mecanismo central do jogo (ver spec.md secao 2.6).
Pattern baseline:  Anti-Corruption Layer (patterns.md) — o domínio nunca
                    confia diretamente na saída bruta do LLM.
Alternatives:      Confiar cegamente na saída do LLM (rejeitado — risco
                    alto de quebrar a invariante, especialmente sob prompt
                    injection); recalcular do zero via lógica determinística
                    (rejeitado — mata o mecanismo central "DM julga
                    narrativamente", que é a proposta de valor)
Rationale:         Normalização proporcional (reescalar as 3 respostas do
                    LLM para somar exatamente 100, preservando a proporção
                    relativa que o DM propôs) preserva o julgamento
                    narrativo do DM e garante a invariante técnica.
Reversibility:     Costly
Consequences:      Todo turno registra tanto a resposta bruta do LLM
                    (raw_llm_response) quanto o valor normalizado
                    persistido — permite auditar quando/quanto a
                    normalização corrigiu o DM.

---

ADR-005
Decision:          Claude/Canvas (HTML gerado diretamente) como ferramenta
                    de UI design para o Módulo 2D
Context:           Iteração single-screen, sem necessidade de handoff para
                    designer, saída HTML já é próxima do que o frontend
                    React vai implementar.
Pattern baseline:  N/A
Alternatives:      Stitch (Google Labs), Figma + plugins de IA, Penpot
Rationale:         Menor fricção para um desenvolvedor solo em tier Lite;
                    Figma teria piso de habilidade mais alto sem ganho real
                    aqui (sem colaboração de design a coordenar).
Reversibility:     Easy
Consequences:      Mockups vivem como arquivos .html versionados em
                    /design/, não em um arquivo Figma externo.

---

ADR-006
Decision:          pytest (backend) + Vitest (frontend) como frameworks de
                    teste; CI substituído por smoke-test manual (compressão
                    padrão do tier Lite)
Context:           Módulo 3.0 Prerequisites. Sem infraestrutura de teste
                    prévia específica a este projeto; sem constraint de CI
                    herdado de outro lugar.
Pattern baseline:  Testing (patterns.md, default: pyramid unit>integration>E2E)
Alternatives:      Jest (frontend) — descartado, Vitest é o default do
                    portfólio; GitHub Actions CI agora — descartado, tier
                    Lite permite substituir por smoke-test manual
Rationale:         Segue o default do restante do portfólio; CI completo
                    adiado para não gastar tempo de setup antes do core
                    loop estar validado como divertido/funcional.
Reversibility:     Easy
Consequences:      `execution-log.md` registra a ausência de CI como
                    compressão deliberada, não esquecimento; smoke-test
                    script manual a ser escrito ao final da Fase 1.

---

ADR-007
Decision:          Catálogo de facções N-seat; DM→Narrator; Humanidade→HWG;
                    roles como VARCHAR; `display_name` opcional; delayed-win
                    para polities humanas (HWG/US/China/UE)
Context:           Fase 2. O Minimal original (4 assentos fixos: Rogue /
                    Defensora / DM / Humanidade) ficou curto para o wargame
                    geopolítico pretendido. Usuário pediu lineup editável,
                    nomes customizados, e reframe do árbitro (Narrator
                    checa plausibilidade + eventos externos) e da facção
                    humana (Human World Government).
Pattern baseline:  Domain catalog (`app/domain/roles.py`) + ACL de prompts
                    (`app/llm/prompts.py`); normalização N-way (ADR-004)
Alternatives:      Manter 4 assentos fixos (rejeitado — pedido explícito);
                    enum SQL rígido por role (rejeitado — migrações a cada
                    facção nova); pesos de score por facção (adiado)
Rationale:         Catálogo aberto com Narrator fora do placar preserva a
                    invariante zero-sum e permite default jogável
                    (HWG/DAI/SA) sem travar experimentação. VARCHAR +
                    migration `002_roles_expand` evita churn de enum.
Reversibility:     Costly (API keys e prompts já espalhados; downgrade
                    recria enums antigos e perde dados locais)
Consequences:      Spec/PROMPT_CONTEXT/assumption-log atualizados; custo
                    por partida escala com N seats IA; Gate A de arbitragem
                    foi validado com 3 facções — **revalidar N>3 é critério
                    de entrada da Fase 3** (`dev-plan.md`); serviço ainda
                    chamado `dm_service` / tabela `dm_adjudications`
                    (renome cosmético adiado).

---

---

ADR-008
Decision:          Camada de profundidade de jogo: AIs veem o mundo público;
                    deltas por turno; interdependência de categorias (prompt);
                    eventos de mundo semeados; epílogo + tipo de final;
                    vitória de contenção da Defender AI
Context:           Revisão de design pós-ADR-007 para tornar partidas de 60
                    turnos mais interessantes sem trair a proposta (chat
                    turn-based, jogadas em texto livre, Narrator julga
                    narrativamente, placar zero-sum de 5 categorias, turnos
                    cegos, custo ~US$0,08/partida).
Pattern baseline:  Funções puras em `app/domain/` (`events.py`,
                    `transfers.py`, `endings.py`) + texto no ACL de prompts
                    (`app/llm/prompts.py`); sem novas chamadas LLM por turno.
Alternatives:      Teto de variação por turno (adiado — "momentum"); fog of
                    war ligado a information control (adiado — exige
                    filtragem server-side de moves/feedback); scoring
                    determinístico (rejeitado — ver ADR-004); eventos
                    gerados por LLM (rejeitado — custo e não-reprodutível).
Rationale:         (1) Seats IA recebem digest + narrativa pública do mês
                    anterior (nunca as jogadas do turno corrente).
                    (2) `deltas` = score[t] − score[t−1], calculado no
                    backend e exibido no ledger; Narrator é instruído a
                    nomear transferências públicas. (3) Interdependência
                    (cs/rc→pc, pc→sm, ic base de tudo, sm custa legitimidade)
                    é regra de prompt, não código. (4) Evento = f(game_id,
                    turno): ~20% dos turnos a partir do 3, nunca em turnos
                    consecutivos, baralho de 12; replay/rewind reproduz os
                    mesmos eventos; nada persistido. (5) 1 chamada extra no
                    fim gera epílogo; `games.ending` + `games.epilogue`
                    (migration `004_ending_epilogue`). (6) Contenção: se
                    defender_ai está em jogo e nenhum assento passa de
                    composite 0,60 nos últimos 10 turnos, ela vence no teto
                    (em vez de empate), inclusive quando controlada por IA.
Reversibility:     Easy (regras e prompts); migration 004 é reversível.
Consequences:      Empate no teto ficou raro quando há Defender AI e o poder
                    está distribuído — testes `test_draw_at_cap` /
                    `test_full_game_draw_at_turn_cap` atualizados. Teto 0,60
                    é palpite, a calibrar com partidas reais. Segue aberto:
                    teto de momentum e fog of war.
