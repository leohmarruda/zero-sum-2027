# Assumption Log — Zero Sum 2027

**Success definition:** Um usuário consegue jogar uma partida completa
(turno 1 até vitória de algum jogador ou empate no teto de turnos) sozinho,
ocupando 1 assento playable, com os demais assentos IA + Narrator rodados
por LLM calls, sem travar, e o histórico de score resultante é
internamente coerente com as jogadas narradas (não contraditório, não
aleatório). Default lineup: HWG + Defender AI + Selfish AI (+ Narrator).

| # | Assumption | Why it matters | How to test cheaply | Status |
|---|---|---|---|---|
| 1 | Um Narrator-LLM consegue estimar de forma consistente uma redistribuição zero-sum de 5 categorias (soma 100%) a partir de N textos livres por turno, sem lógica determinística | Se falhar, o placar vira ruído e o jogo perde a espinha mecânica | Rodar 5-10 turnos manuais (fora do app, direto no chat) com jogadas fabricadas e verificar se a redistribuição é plausível e resiste a jogadas adversariais óbvias | **Validated (parcial)** — Gate A feito com 3 facções; ver `/validation/gate-a-dm-arbitration-test.md`. **Revalidar N>3 = critério de entrada da Fase 3** (`dev-plan.md`). |
| 2 | O placar zero-sum de 1 categoria (compute) já é suficiente para produzir tensão jogável, antes de comprometer as 5 categorias completas | Reduz custo de construir e testar o protótipo; se falhar, todas as 5 categorias precisam entrar desde o início | Prototipar só com compute como score único por 10 turnos e avaliar se já é interessante | **Superseded** — teste pré-build nunca rodado; o build já entrou com as 5 categorias (domain + Gate A). Caminho 1-categoria abandonado. |
| 3 | Turnos cegos simultâneos (1 texto livre por mês, sem ver os outros) dão agência suficiente ao jogador humano | Se a granularidade for grosseira/fina demais, a experiência solo trava ou fica enfadonha | Jogar manualmente 5 turnos como HWG contra 2 IAs e avaliar a sensação de agência | **Superseded** — teste pré-build nunca rodado; o build já lockou turnos cegos como mecânica core. Qualidade de agência ainda é sensação empírica, mas não é mais gate pré-build. |
| 4 | É viável e barato rodar as LLM calls do default lineup (2 seats IA + Narrator; + gate de plausibilidade no resolve humano) por turno via `llmcall` | Se o custo por partida for alto, compromete iteração rápida no protótipo | Estimar custo de ~30-60 turnos com modelos econômicos via `dry_run` | **Validated (default lineup + digest)** — ~$0.076–0.077 / 60 turnos gpt-4o-mini class com `world_state_digest` rolante (ver `validation/cost-estimate-dry-run.md`). Histórico bruto seria O(T²) (`--compare --late-turn 55`). |
| 5 | Teto de 60 turnos é razoável para permitir vitória de polities humanas (só liberada no turno 30) sem alongar demais o protótipo | **Prioridade elevada pós-ADR-007:** com N>3 facções, a fatia por assento dilui e delayed-win (turno 30) pode nunca materializar antes do teto — se o teto for baixo demais, HWG/US/China/UE não têm chance real; se alto demais, partidas de teste ficam longas | Rodar 1 partida completa simulada (idealmente N>3) e observar se o teto é atingido de forma razoável | **Untested — high priority** |
| 6 | **[Risco de segurança, M2.14 — tier Lite]** `move_text` do jogador humano pode conter prompt injection direcionado ao Narrator | Quebra a integridade do placar se o Narrator obedecer instruções embutidas na jogada | Isolar `move_text` como conteúdo citado; fixtures de injection no M3 | **Validated (fixture)** — `tests/test_prompt_injection.py`; live-LLM spot-check ainda recomendado antes do M4 |

## Riskiest assumption
A primeira linha (Narrator-LLM arbitrar redistribuição zero-sum de forma
consistente, agora com N variável) é a que mais mata o projeto se for
falsa — é o gargalo mecânico central. Próximo gate: revalidar com N>3
antes da Fase 3. Em paralelo, #5 (teto de 60) subiu de prioridade após
ADR-007: sem evidência de que delayed-win seats ainda vencem sob diluição.
