# Component Inventory — Zero Sum 2027

> Referência para Módulo 3 (implementação). Layout estruturado em
> `mockup-game-screen.html` (Pass A+B combinados, ver `execution-log.md`).
> Atualizado 2026-08-02: Narrator, HWG, N facções, i18n, Imprevisibilidade.

## Design tokens (ver mockup para valores completos)
- Cor: fundo grafite-azulado, painéis em 2 níveis, cores por facção
  (CSS classes em `ROLE_CSS` / SetupForm), âmbar para alertas do Narrator.
- Tipo: IBM Plex Mono (headers, dados, timestamps) + IBM Plex Sans (corpo).
- Radius: 4-6px. Sem sombras pesadas.

## Componentes e estados

| Componente | Estados | Notas |
|---|---|---|
| `StatusBar` | em andamento / vitória / empate | wordmark + turno/data + pill de status + toggle EN/PT |
| `ZeroSumLedger` | 1 linha por categoria; N segmentos (1 por facção pontuada); segmento <~5% omite label interno | componente de assinatura — reutilizado em Histórico e Fim de Jogo |
| `TransmissionPanel` | com feedback individualizado / sem feedback (turno 0) / intro do Narrator | borda esquerda âmbar; copy i18n |
| `MovePanel` | vazio / digitando / enviado / rejeitado (plausibilidade) / turno encerrado | limite de caracteres; canal `/off` |
| `SubmitButton` | default / hover / disabled (aguardando resolução) | |
| `FooterNav` | padrão / oculto (fim de jogo) | contagem regressiva até elegibilidade delayed-win (some após turno 30) |
| `EndGameSummary` *(Fase 3)* | vitória (por facção) / empate | reusa `ZeroSumLedger` + gráfico (recharts) |
| `SetupForm` | defaults / editing / submitting / modal de nome | lineup add/remove (Narrator fixo); assento humano escolhível; Imprevisibilidade; estimativa USD; intro |

## Acessibilidade (checado no mockup)
- Contraste: texto `--text` (#E7E4DA) sobre `--bg`/`--bg-panel` > 4.5:1.
- Foco visível no `textarea` (outline 2px).
- Alvos de toque: botão de submit ≥ 44px de altura efetiva em mobile
  (a validar na implementação real, não apenas no mockup estático).
- Modal de nome customizado: `Escape` fecha; foco inicial no input.
