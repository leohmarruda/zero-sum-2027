# Pattern Preference Register

> Copiado do Apêndice A (framework v1.8) no Bootstrap. Ainda não revisado contra
> o stack — stack será decidido no Módulo 2 (Spec). Revisar cada entrada abaixo
> e marcar N/A com nota onde não se aplicar; qualquer desvio conhecido registra
> um ADR em `decisions.md`.
>
> Este arquivo é atualizado sempre que uma decisão de padrão é tomada durante
> o projeto — não apenas no momento da spec.

---

### Application Architecture
**Default:** Layered — Presentation / Service / Repository / Data.
Escalar para Event-driven só se desacoplamento assíncrono for a proposta de
valor central. Escalar para Microservices só se deploy independente for
requisito presente e real.

---

### Module Boundaries
**Default:** Single Responsibility Principle por módulo; Dependency Inversion
para wiring. Lógica de domínio não importa infraestrutura diretamente.

---

### Data Access
**Default:** Repository pattern. Active Record aceitável para CRUD simples
sem lógica de domínio relevante — se escolhido, declarar aqui explicitamente.

---

### API Design (HTTP)
**Default:** REST + OpenAPI spec. Escalar para GraphQL se flexibilidade de
query do cliente for a proposta de valor central. Escalar para gRPC se
enforcement de schema e performance binária forem críticos.

---

### Frontend State Management
**Default:** Local component state → Context API / Zustand → Redux / Jotai.
Começar em local state; subir só quando a complexidade justificar.

---

### Error Handling
**Default:** Typed error returns (Result/Either ou union types) em domínio e
serviço. Exceptions só nas fronteiras de I/O.

---

### Configuration
**Default:** 12-Factor App — config via env vars. `.env.example` commitado
sem valores. Sem config hardcoded. Secrets via GitHub Secrets/Doppler/Infisical.

---

### Async
**Default:** async/await. Event emitters só para fluxos genuinamente
event-driven. Callbacks só ao envolver APIs legadas.

---

### Testing
**Default:** Test pyramid — unit > integration > E2E. AAA structure,
um conceito de asserção por teste.

---

### UI Components
**Default:** Composição sobre herança. Estado co-localizado com o componente
dono. Compound components / render props sobre prop drilling profundo.

---

### External Integrations (Anti-Corruption Layer)
**Default:** Interface de domínio representando o que é necessário do serviço
externo — não o que o serviço externo oferece. Adapter traduz entre os dois.

**Aplicado (Fase 1):** `app/llm` (`LlmCallClient` / `LLMClient` protocol)
isola `llmcall`; serviços e domínio não importam tipos do provider.
Stub injetável via `app.state.llm_client` para testes.

---

### GoF Patterns — usar quando o problema se encaixa

| Pattern | Usar quando |
|---|---|
| Strategy | Mesma operação precisa de múltiplas implementações intercambiáveis (ex.: providers de modelo de IA — relevante aqui, cada jogador-IA pode usar modelo/temperatura diferentes) |
| Observer / Event | Componentes reagem a mudanças de estado sem acoplamento forte; lista de subscribers dinâmica |
| Factory | Criação de objeto complexa, varia por contexto, ou precisa ser testada isoladamente |
| Decorator | Comportamento adicionado sem modificar o objeto original (logging, cache, retry) |
| Command | Operações precisam ser enfileiradas, desfeitas, logadas ou retentadas como objetos de primeira classe |
| Repository | (ver Data Access) |
| Adapter | (ver Anti-Corruption Layer) |

---

### YAGNI

Não construir para requisitos que ainda não existem. Sinal de violação: "quando
eventualmente precisarmos escalar", "caso queiramos adicionar X depois". Qualquer
violação encontrada em review é logada em `execution-log.md` como desvio.

---

### Performance Optimization

**Default:** Medir antes de otimizar. Nenhum cache, denormalização, memoização
ou reestruturação de query sem resultado de profiling, benchmark ou regressão
observada. Trabalho de performance é feito na fase de fechamento (M3.4).
