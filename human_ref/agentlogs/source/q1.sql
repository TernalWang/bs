SELECT
  event_time,
  trace_id,
  observation_id,
  seq_no,
  type,
  status,
  model,
  tool_name,
  latency_ms
FROM agent_observations
WHERE biz_date BETWEEN DATE '2026-03-17' AND DATE '2027-03-20'
  AND tenant = 'tenant_001'
  AND type IN ('GENERATION', 'TOOL')
  AND status IN ('ok', 'error')
ORDER BY event_time DESC, seq_no DESC
LIMIT 50;
