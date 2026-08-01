# Project Proposal — Zero Sum 2027

## 1.1 Starting Point
Ideia madura — trazida com estrutura já definida (4 assentos, turnos cegos,
DM arbitra). Desenvolvida a partir daqui, sem reframe.

## 1.2 Problem Definition
- **Problema real:** dinâmicas de disputa de poder entre IA e humanidade
  (concentração de compute, automação de infraestrutura crítica, corrida de
  capacidades) são discutidas em prosa/ensaio, mas raramente são
  *experienciadas* de forma interativa e visceral por uma pessoa.
- **Quem tem esse problema:** inicialmente o próprio criador, validando o
  loop; depois, pessoas interessadas em governança/segurança de IA que
  preferem explorar cenários jogando a lendo.
- **Mundo com o problema resolvido:** um jogo de chat turn-based, jogável e
  rejogável, onde jogadas em texto livre são traduzidas por um DM em um
  placar de poder que evolui mês a mês, produzindo narrativas distintas a
  cada partida.

## 1.3 Solution — Mecanismo Central
- **4 assentos:** Rogue AI (paperclip maximizer), AI Defensora, DM, Time
  Humanidade. Modelo e temperatura de cada IA configuráveis no início.
- **Turnos cegos e simultâneos:** cada jogador (exceto DM) escreve texto
  livre de intenção sem ver a jogada dos demais no turno corrente. O DM
  recebe as 3 jogadas, narra o desfecho e retorna feedback individual a
  cada jogador.
- **Score:** cada um dos 3 jogadores pontuados (Rogue AI, AI Defensora,
  Humanidade) tem um score composto por 5 categorias, peso 0.2 cada:
  soberania militar, recursos críticos, infraestrutura crítica, poder
  computacional, automação da cadeia de suprimentos. **Cada categoria é
  zero-sum entre os 3 jogadores** (soma sempre 100%) — o DM redistribui as
  fatias ao fim de cada turno com base no julgamento narrativo das 3 jogadas.
- **Estado inicial (turno 0, 2027-01-01):** Humanidade 100% em todas as
  categorias exceto compute (98%); Rogue AI e AI Defensora começam em 0%,
  exceto 1% de compute cada.
- **Cadência:** 1 turno = 1 mês **na linha do tempo narrativa/fictícia do
  jogo**, a partir de 2027-01-01. Não é cadência real — os turnos podem ser
  jogados em sucessão imediata; "mês" é apenas o rótulo temporal usado na
  narrativa e no cálculo do teto de turnos, não um intervalo de espera real
  entre jogadas.
- **Condição de vitória:** um jogador (Rogue AI, AI Defensora ou Humanidade)
  vence ao manter score ≥ 0.9 por 10 turnos consecutivos. Rogue AI e AI
  Defensora podem vencer a qualquer momento; Humanidade só pode vencer a
  partir do turno 30.
- **Teto de turnos (assumido, a confirmar):** turno 60 (2031-12-01). Se
  ninguém atingir a condição de vitória até lá, a partida termina em
  estagnação/empate — **valor não confirmado pelo usuário, ver Open Gate
  abaixo.**

> **[Open Gate — 1.3]** Alguma abordagem alternativa de mecanismo — turnos
> não-cegos, categorias não zero-sum, um 5º jogador, outro tipo de vitória —
> que valha considerar antes de travar isso na spec? Se não houver objeção,
> sigo com o mecanismo acima no Módulo 2.

## 1.4 Market & Value Check
- **Usuário-alvo (fase atual):** o próprio criador, single-player, validando
  se o loop de jogo é interessante antes de expandir.
- **Usuário-alvo (futuro, se evoluir para Standard):** entusiastas de
  governança/segurança de IA, jogadores de wargames geopolíticos (ex.:
  Twilight Struggle), comunidade de forecasting (Metaculus-adjacent).
- **Proposta de valor central:** transforma dinâmicas abstratas de corrida de
  poder em IA em um wargame narrativo jogável, com um placar zero-sum
  estimado por um DM-LLM a partir de jogadas em texto livre e cegas.
- **Diferenciadores:** (a) turnos simultâneos e cegos julgados por um DM-IA,
  não por regras determinísticas; (b) modelo/temperatura configuráveis por
  assento, permitindo comparar como diferentes modelos "jogam" a corrida de
  IA; (c) placar zero-sum de 5 categorias como abstração legível de "poder".
- **Soluções existentes e lacunas:** jogos de tabuleiro temáticos de
  IA/superinteligência e wargames geopolíticos existem, mas nenhum combina
  chat multiplayer cego + DM-LLM ao vivo + configuração de modelo por
  assento.

## 1.5 Nome do Projeto
**Zero Sum 2027**

- Legível: pronunciável, memorável.
- Distinto: sem colisão direta relevante (verificado via busca; "Zero Sum"
  isolado existe em contextos não relacionados — o qualificador "2027"
  desambigua).
- Honesto: não superclama nada; descreve o mecanismo central (score
  zero-sum) e a linha do tempo interna.
- Durável: "2027" é a data de início da própria simulação, não um prazo
  externo que expira.

**Candidatos rejeitados:** "Overhang" (colide semanticamente com o termo já
estabelecido "compute/capability overhang" em AI safety — confuso, não
apenas indistinto); "Control Surface" (termo genérico demais, usado em
áudio, aviação, fluidos — zero distintividade); "Compute Wars",
"Brinkmanship AI", "The Alignment Table" (descartados por menor aderência
ao mecanismo central específico do jogo); "Wargame 2027" (colide com
"World Empire 2027" — mesmo gênero — e, mais grave, com o projeto real
"AI 2027 wargame" ligado ao relatório AI 2027/Lightcone — mesmo espaço
conceitual, não só nome; também superclama gênero militar quando só 1 de 5
categorias é militar); "Zero Sum AI 2027" (contém o nome próprio do
relatório "AI 2027" verbatim — falha Honesto por sugerir afiliação não
existente, e falha Distinto pela mesma colisão de "Wargame 2027").

## 1.6 Scope Definition
**Scope tier: Minimal.** Menor coisa que prova que a ideia funciona:
4 assentos fixos, interface de chat texto-a-texto, turnos cegos simultâneos,
DM computa o placar zero-sum mensalmente, condições de vitória/empate acima.
Sem customização de regras, sem multiplayer real (single-player: o usuário
ocupa 1 assento, os outros 3 são LLM calls), sem persistência multi-partida
além do log da partida corrente.

> **[Open Gate — 1.6]** Alguma meta ou restrição — ex. querer já testar 2
> humanos em assentos diferentes, ou precisar de replay/histórico entre
> partidas — que muda como "Minimal" deveria ser lido aqui?

**Constraint adicionada (pós-proposta):** interface web, com acabamento
visual cuidado ("bonita") e mobile-friendly — pode ser simples em escopo de
telas, mas não em polimento visual. Isso não muda o scope tier (ainda
Minimal — 1 tela de chat + placar), mas afeta 2.5 (stack de frontend) e
2D. **Divergência documentada do default Lite:** o tier Lite permite pular
2D Pass B (Visual); este projeto não vai pular — Pass B é obrigatório dado
o requisito explícito de acabamento visual. Pass C (interativo) segue
opcional.

## 1.8 Avaliação Crítica (`PROMPT_CHALLENGE_IDEATION`, resumo)
1. **Maior risco de falha:** o DM-LLM produzir estimativas de score
   inconsistentes ou "gameáveis" (ex.: jogador aprende a frase mágica que
   sempre aumenta score), quebrando a credibilidade do placar.
2. **Assunção que mais dano causa se falsa:** que um DM-LLM consegue arbitrar
   de forma coerente e não-degenerada uma redistribuição zero-sum de 5
   categorias a partir de texto livre, turno após turno, sem lógica
   determinística por trás.
3. **Versão mais simples com o mesmo core goal:** reduzir para 1 categoria de
   score (ex.: só "poder computacional") no protótipo inicial, antes de
   comprometer as 5 categorias completas — mais barato de testar se o DM
   consegue arbitrar de forma crível.
4. **Ponto cego provável:** o "Time Humanidade" jogando sozinho (single-
   player) contra 2 IAs adversárias/aliadas pode não ter agência suficiente
   por turno — um único texto livre por mês pode ser granularidade
   grosseira demais ou fina demais; isso só se revela jogando.

**Decisão:** Proceed — mas os pontos 2 e 3 acima são exatamente o tipo de
coisa que Gate A deveria testar antes de investir na spec completa de 5
categorias.
