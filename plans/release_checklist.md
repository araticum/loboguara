# Release Checklist

## Antes do Deploy

- [ ] `alembic upgrade head` aplica sem erro no ambiente alvo.
- [ ] `GET /health` responde `200`.
- [ ] `GET /metrics/sla` e `GET /metrics/queues` retornam payloads válidos.
- [ ] Fila `dispatch`, `voice`, `telegram`, `email`, `escalation` e `DLQ` estão com backlog esperado.
- [ ] `SERIEMA_ADMIN_TOKEN` e `VOICE_WEBHOOK_SECRET` estão configurados quando exigido.

## Durante o Deploy

- [ ] Monitorar logs de `FAILED`, `ESCALATED` e `ACK_RECEIVED`.
- [ ] Confirmar que workers sobem com `beat_schedule` ativo.
- [ ] Validar replay DLQ em modo `dry-run` antes de replay real.

## Depois do Deploy

- [ ] Validar ingestao de evento de teste fim a fim.
- [ ] Confirmar que callback autenticado de voz funciona.
- [ ] Verificar dashboards do Metabase nas views `v_incident_sla`, `v_channel_delivery` e `v_ops_summary_24h`.
- [ ] Revisar backlog da DLQ e repetir replay apenas se for seguro.

## Rollback

- [ ] Reverter a ultima migration se o problema estiver no schema.
- [ ] Desabilitar consumidores de worker antes de corrigir dados corrompidos.
- [ ] Preservar a DLQ para analise antes de qualquer limpeza.
