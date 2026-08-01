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
