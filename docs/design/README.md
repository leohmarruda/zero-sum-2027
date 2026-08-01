# Módulo 2D — UI Design & Prototyping — Zero Sum 2027

## 2D.1 Tooling Choice
**Claude / Canvas (geração direta de HTML)** — ADR-005 em `decisions.md`.
Escolhido por iteração rápida single-screen e saída HTML funcional, sem
necessidade de handoff para um time de design.

## 2D.2 Design Phases — status
- **Pass A (Estrutura):** completa para as 4 telas, em nível de descrição
  (ver `spec.md` §2.3). Não redesenhada como wireframe separado — dado o
  tier Lite e a velocidade pedida, a descrição textual + o mockup de alta
  fidelidade da tela principal cobrem a mesma decisão de navegação/hierarquia.
- **Pass B (Visual):** completa para **Tela de Jogo**
  (`mockup-game-screen.html`) e **Tela de Setup**
  (`mockup-setup-screen.html`, Pass B feita no início da Fase 2).
  Histórico e Fim de Jogo ainda pendentes (Fase 3).
- **Pass C (Interativo):** pulada nesta rodada — opcional em Lite. O
  mockup atual é estático (sem clique real). Retestar necessidade após a
  Fase 1 do roadmap (core loop via API).

## 2D.4 Component Inventory
Ver `components.md`.

## 2D.5 Validation Gate
- [x] Toda feature Minimal (spec §2.2) tem superfície de UI correspondente
      *ao menos em descrição* — ver §2.3
- [ ] **Não atendido ainda:** nem todo workflow de §2.10 pode ser percorrido
      ponta a ponta no protótipo — só a Tela de Jogo tem fidelidade
      suficiente para isso. Decisão explícita: aceitável para Lite, revisar
      antes do M4 (Review).
- [x] Inventário de componentes completo e consistente para a tela mockada
- [x] Acessibilidade básica confirmada na tela mockada (contraste, foco,
      responsivo mobile) — ver `components.md`
- [x] Nenhuma decisão de design contradiz `spec.md` ou `decisions.md`
- [ ] Validação com pessoa não envolvida — não aplicável ainda (protótipo
      não funcional, só visual)

## 2D.6 Spec Sync
Nenhuma divergência entre o mockup e `spec.md` §2.2/2.3/2.10 — o ledger
zero-sum, a transmissão do DM com feedback individualizado, e o campo de
jogada em texto livre mapeiam diretamente para os itens já descritos na
spec. Nenhum ADR novo necessário por divergência de design.

## 2D.8 Critical Evaluation (`PROMPT_CHALLENGE_DESIGN`, resumo)
1. **Onde os defaults da ferramenta de IA guiaram o design em vez da
   intenção declarada?** Nenhum default genérico foi aceito sem
   questionamento — a estética de "sala de situação" foi derivada do tema
   do jogo, não de um template. O maior risco de "default" era o par
   preto+acento único (clichê de IA); mitigado com 3 cores de facção
   semanticamente ligadas ao mecanismo.
2. **É implementável dado o stack de `spec.md` §2.5?** Sim — CSS puro +
   fontes web, nada que exija biblioteca fora do já decidido. O
   `ZeroSumLedger` mapeia 1:1 para dados já modelados em `ScoreSnapshot`.
3. **Menos telas?** Não — as 4 já são o mínimo (Setup, Jogo, Histórico, Fim
   de Jogo); nenhuma é dispensável para o MVP definido em §2.13.
4. **Tela em que o design está menos confiante:** Fim de Jogo — ainda não
   mockada; a decisão de reusar `ZeroSumLedger` em "modo final" é uma
   hipótese, não testada visualmente ainda.

## 2D.7 Output
`mockup-game-screen.html`, `mockup-setup-screen.html`, `components.md`,
este README. Design tokens documentados em `components.md` (CSS variables
nos mockups).
