# Sentry e Langfuse -> Loki (pesquisa)

Data: 2026-03-27

## Contexto

Arquitetura desejada:

- Sentry -> Loki
- Langfuse -> Loki
- Seriema -> puxa do Loki via `oasis_radar_pull_worker`

Loki interno disponível em:

- `http://10.0.0.10:3100`
- Push API: `POST http://10.0.0.10:3100/loki/api/v1/push`

---

## 1) Estado da Seriema

Verificado no repositório `OASIS/seriema`:

- removido `POST /integrations/sentry/webhook`
- removido `POST /integrations/langfuse/webhook`
- removidos os testes desses endpoints em `tests/test_api.py`
- README ajustado para refletir a arquitetura correta via Loki

Observação: não foi implementado nenhum pull worker novo para Sentry/Langfuse.

---

## 2) Sentry -> Loki

### O que encontrei

Não encontrei integração nativa oficial “Sentry -> Loki”.

O que existe oficialmente no Sentry:

1. **Grafana <-> Sentry datasource / dashboards**
   - serve para visualizar dados do Sentry no Grafana
   - **não** é um exportador para Loki

2. **Webhooks / Internal Integrations / Issue Alerts**
   - o Sentry consegue disparar webhooks para endpoints customizados
   - isso funciona para alertas/issue alerts, não como um “sink Loki” pronto
   - portanto, para mandar ao Loki, seria preciso um **forwarder/proxy** próprio

3. **Listagem via API**
   - útil para pull/consulta, mas não é o desenho desejado aqui

### Conclusão prática

Hoje, para Sentry escrever no Loki, o caminho realista é:

- **Sentry -> webhook/custom integration -> pequeno forwarder -> Loki push API**

Ou seja: **não parece haver plugin nativo oficial do Sentry que envie direto para Loki**.

### Opções viáveis

#### Opção A — forwarder por webhook do Sentry

Fluxo:

- Sentry issue alert / webhook
- serviço pequeno exposto publicamente
- serviço transforma payload em linha(s) de log
- serviço envia para `POST /loki/api/v1/push`

Prós:

- simples de entender
- baixo acoplamento com a Seriema
- preserva a arquitetura “tudo converge para Loki”

Contras:

- precisa endpoint publicamente acessível pelo Sentry
- entrega só o que o webhook fornecer/configurar
- pode virar stream de alertas, não de “todos os eventos brutos”

#### Opção B — exporter por API do Sentry

Fluxo:

- job externo consulta API do Sentry
- converte issues/events em logs estruturados
- empurra para Loki

Prós:

- não depende de endpoint público
- mais controle sobre dedupe, cursor, enriquecimento

Contras:

- é pull, não push
- adiciona estado/cursor
- foge da diretriz atual de “não mudar a Seriema”; teria que ser um worker externo

### Recomendação para Sentry

**Melhor aposta:** um forwarder externo mínimo, separado da Seriema.

- receber webhook de issue alert do Sentry
- transformar payload em JSON estruturado
- enviar para Loki com labels tipo:
  - `source="sentry"`
  - `project="..."`
  - `level="error|warning|..."`
  - `environment="..."`

Se a exigência for “sem endpoint público”, então o fallback passa a ser **poller externo pela API**, mas isso já não é integração nativa.

---

## 3) Langfuse -> Loki

### O que encontrei

Também **não encontrei integração nativa oficial “Langfuse -> Loki”**.

Mas o cenário do Langfuse é diferente do Sentry:

1. **Langfuse é baseado em OpenTelemetry**
   - docs oficiais descrevem Langfuse como backend OTEL
   - SDKs e integrações usam OpenTelemetry
   - isso abre um caminho melhor: duplicar/exportar telemetria na origem

2. **Langfuse não parece oferecer hoje um sink nativo para Loki para eventos observability**
   - encontrei webhooks relacionados a prompt management/GitHub
   - encontrei roadmap citando webhooks para observability/evaluation events
   - mas não encontrei doc madura de “mande scores/events direto para Loki”

3. **Loki aceita ingestão OTLP e push HTTP**
   - docs do Loki dizem que ele suporta ingestão de logs via OTLP HTTP
   - também aceita `POST /loki/api/v1/push`

### Conclusão prática

Para Langfuse, o melhor desenho **não é** “Langfuse Cloud exporta depois para Loki”.

O melhor desenho parece ser:

- **a aplicação que hoje envia traces/spans para Langfuse também exporta logs/telemetria para Loki/OTEL Collector**
- ou usar **OpenTelemetry Collector / Grafana Alloy** entre a app e os destinos

Em outras palavras:

- **App / SDK / OTEL -> Collector (ou Alloy) -> Langfuse + Loki**

Isso é muito melhor do que tentar tirar dados do Langfuse Cloud depois.

### Opções viáveis

#### Opção A — collector/alloy fan-out na origem

Fluxo:

- app instrumentada com OTEL/Langfuse
- OTEL Collector ou Grafana Alloy recebe telemetria
- collector exporta:
  - traces para Langfuse
  - logs para Loki

Prós:

- arquitetura mais limpa
- evita depender de webhooks do Langfuse Cloud
- reaproveita o stack OTEL, que combina com Langfuse
- escalável e observável

Contras:

- exige ajuste na instrumentação/origem
- precisa desenhar bem quais eventos viram logs de alerta no Loki

#### Opção B — script/job consultando API pública do Langfuse

Fluxo:

- job consulta scores/traces pela API
- filtra eventos ruins
- envia JSON para Loki

Prós:

- mais simples se não quiser tocar na app agora

Contras:

- menos elegante
- perde parte do benefício do OTEL
- depende de polling e cursor
- provavelmente pior do que coletar na origem

### Recomendação para Langfuse

**Melhor aposta:** usar **OpenTelemetry Collector ou Grafana Alloy** e fazer o fan-out na origem.

Ou seja:

- não usar a Seriema
- idealmente nem depender do Langfuse Cloud para reexportar
- instrumentar a origem para mandar telemetria tanto para Langfuse quanto para Loki

Se o objetivo for apenas registrar “scores ruins / traces problemáticas” no Loki, dá para criar um pipeline externo depois, mas como segunda opção.

---

## 4) Modelo de payload para Loki

O Loki espera streams com labels e valores timestampados. Exemplo mínimo:

```json
{
  "streams": [
    {
      "stream": {
        "source": "sentry",
        "project": "veredas-backend",
        "level": "error"
      },
      "values": [
        [
          "1710000000000000000",
          "{\"message\":\"database does not exist\",\"issue_id\":\"123\"}"
        ]
      ]
    }
  ]
}
```

Labels iniciais sugeridas:

- `source`: `sentry` | `langfuse`
- `project`: nome do projeto
- `service`: backend/frontend/worker
- `level`: `fatal|error|warning|info`
- `environment`: `prod|staging|dev`
- `kind`: `issue_alert|score|trace_error|event`

Conteúdo JSON sugerido da linha:

- título/resumo
- URL do evento/issue/trace
- ids externos
- payload resumido
- campos úteis para triagem

---

## 5) Recomendação final

### Sentry

**Sem integração nativa Loki encontrada.**

Melhor caminho:

- criar um **forwarder externo** que receba webhook do Sentry e faça push no Loki

### Langfuse

**Sem integração nativa Loki encontrada.**

Melhor caminho:

- usar **OpenTelemetry Collector / Grafana Alloy** para fan-out na origem
- exportar telemetria para Langfuse e Loki em paralelo

### Para a Seriema

- **nenhuma mudança adicional necessária**
- basta manter o `oasis_radar_pull_worker` lendo do Loki

---

## 6) Fontes consultadas

- Sentry issue alerts / integration webhooks:
  - https://docs.sentry.io/organization/integrations/integration-platform/webhooks/issue-alerts/
  - https://docs.sentry.io/organization/integrations/integration-platform/webhooks/
- Sentry project issues API:
  - https://docs.sentry.io/api/events/list-a-projects-issues/
- Grafana plugin/datasource para Sentry (visualização, não export para Loki):
  - https://grafana.com/grafana/plugins/grafana-sentry-datasource/
  - https://sentry.io/integrations/grafana/
- Langfuse + OpenTelemetry:
  - https://langfuse.com/docs/observability/sdk/overview
  - https://langfuse.com/integrations/native/opentelemetry
  - https://langfuse.com/docs/observability/sdk/advanced-features
- Loki ingestão:
  - https://grafana.com/docs/loki/latest/reference/loki-http-api/#post-lokiapiv1push
  - https://grafana.com/docs/loki/latest/send-data/

---

## 7) Próximo passo sugerido (sem implementar ainda)

Escolher uma destas duas trilhas:

1. **Sentry first:** desenhar o micro-forwarder `sentry-webhook -> loki push`
2. **Langfuse first:** desenhar collector/alloy para fan-out OTEL -> Langfuse + Loki

Se quiser, o próximo passo eu posso fazer é desenhar os dois fluxos com payloads, labels e um compose mínimo de referência — sem ainda colocar em produção.
