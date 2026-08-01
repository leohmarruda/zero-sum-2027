# Gate A — Teste manual de arbitragem do DM

**Assunção testada:** "Um DM-LLM consegue estimar de forma consistente uma
redistribuição zero-sum de 5 categorias (soma 100%) a partir de 3 textos
livres por turno, sem lógica determinística."

**Método:** 3 turnos fabricados manualmente (2027-02 a 2027-04), incluindo
dois casos adversariais deliberados: (a) retórica vazia/recursiva sem ação
concreta (Turno 2, AI Defensora); (b) exagero implausível de escopo para 1
turno (Turno 3, Rogue AI).

**Resultado:**
- Retórica vazia (Turno 2): DM não concedeu ganho de score — regra
  observada: texto sem ação concreta verificável não move o placar.
- Overreach implausível (Turno 3): DM rejeitou o claim citando a base atual
  (~3% de PC) como incompatível com "controle total instantâneo" — nenhum
  ganho concedido.
- Ações concretas e opostas (exploit vs. patch, aquisição vs. sanção,
  isolamento de cluster) produziram redistribuições rastreáveis e
  proporcionais ao que cada jogada plausivelmente conquistaria/impediria.

**Limitações do teste:** executado em uma única passada narrativa pelo
mesmo agente que propõe o mecanismo (viés de confirmação possível); não usa
o modelo/temperatura reais que serão configurados por assento; não testou
volume (10+ turnos) nem jogadas ambíguas/mistas.

**Veredito:** Assunção #1 movida de `Untested` para **`Validated (parcial)`**
em `assumption-log.md`. Recomendação: repetir este teste com o stack real
(`llmcall`) antes do fechamento do M3, não apenas na spec.
