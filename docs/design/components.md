# Component Inventory — Zero Sum 2027

> Referência para Módulo 3 (implementação). Layout estruturado em
> `mockup-game-screen.html` (Pass A+B combinados, ver `execution-log.md`).

## Design tokens (ver mockup para valores completos)
- Cor: fundo grafite-azulado, painéis em 2 níveis, 3 cores de facção
  (Humanidade/Rogue AI/AI Defensora), âmbar para alertas do DM.
- Tipo: IBM Plex Mono (headers, dados, timestamps) + IBM Plex Sans (corpo).
- Radius: 4-6px. Sem sombras, sem gradientes.

## Componentes e estados

| Componente | Estados | Notas |
|---|---|---|
| `StatusBar` | em andamento / vitória / empate | wordmark + turno/data + pill de status |
| `ZeroSumLedger` | 1 linha por categoria; segmento pode ser 0% (não renderiza label dentro do segmento se < ~5%) | componente de assinatura visual — reutilizado em Histórico e Fim de Jogo |
| `TransmissionPanel` | com feedback individualizado / sem feedback (turno 0) | borda esquerda âmbar fixa |
| `MovePanel` | vazio / digitando / enviado (desabilitado após envio) / turno encerrado (jogo terminou) | contador de caracteres, limite 800 |
| `SubmitButton` | default / hover / disabled (aguardando resolução do turno) | |
| `FooterNav` | padrão / oculto (tela de fim de jogo) | contador regressivo de turnos até elegibilidade de Humanidade some após turno 30 |
| `EndGameSummary` *(não mockado nesta pass — Fase 3 do roadmap)* | vitória (por facção) / empate | reusa `ZeroSumLedger` em modo "final" + gráfico de evolução (recharts) |
| `SetupForm` | defaults / editing / submitting | mockup: `mockup-setup-screen.html` — Humanidade fixa humana; modelo+temp para Rogue/Defensora/DM |

## Acessibilidade (checado no mockup)
- Contraste: texto `--text` (#E7E4DA) sobre `--bg`/`--bg-panel` > 4.5:1.
- Foco visível no `textarea` (outline 2px).
- Alvos de toque: botão de submit ≥ 44px de altura efetiva em mobile
  (a validar na implementação real, não apenas no mockup estático).
