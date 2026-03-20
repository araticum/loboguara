-- Metabase dashboard queries for Seriema
-- Source views:
--   seriema.v_incident_sla
--   seriema.v_channel_delivery
--   seriema.v_ops_summary_24h

-- Query 1: operational summary cards
SELECT
  total_incidents_24h,
  open_incidents_24h,
  acknowledged_incidents_24h,
  resolved_incidents_24h,
  escalated_incidents_24h,
  ack_rate
FROM seriema.v_ops_summary_24h;

-- Query 2: incidents with slowest time to acknowledge
SELECT
  incident_id,
  source,
  severity,
  status,
  created_at,
  acknowledged_at,
  tta_seconds
FROM seriema.v_incident_sla
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY COALESCE(tta_seconds, 999999) DESC, created_at DESC
LIMIT 50;

-- Query 3: TTA by source
SELECT
  source,
  COUNT(*) AS incidents,
  ROUND(AVG(tta_seconds)::numeric, 2) AS avg_tta_seconds,
  ROUND(
    COUNT(*) FILTER (WHERE acknowledged_at IS NOT NULL)::numeric / COUNT(*)::numeric,
    4
  ) AS ack_rate
FROM seriema.v_incident_sla
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY source
ORDER BY avg_tta_seconds DESC NULLS LAST, incidents DESC;

-- Query 4: delivery status by channel
SELECT
  channel,
  status,
  COUNT(*) AS notifications
FROM seriema.v_channel_delivery
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY channel, status
ORDER BY channel, status;

-- Query 5: notification backlog by channel
SELECT
  channel,
  COUNT(*) FILTER (WHERE status = 'PENDING') AS pending_notifications,
  COUNT(*) FILTER (WHERE status = 'FAILED') AS failed_notifications,
  COUNT(*) FILTER (WHERE status = 'SENT') AS sent_notifications
FROM seriema.v_channel_delivery
GROUP BY channel
ORDER BY channel;

-- Query 6: incidents by severity and status
SELECT
  severity,
  status,
  COUNT(*) AS incidents
FROM seriema.v_incident_sla
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY severity, status
ORDER BY severity, status;
