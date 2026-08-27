SELECT
  event_time,
  trace_id,
  observation_id,
  type,
  status,
  json_extract_string(payload, '$.attr.release_ring') AS release_ring,
  json_extract_string(payload, '$.attr.customer_tier') AS customer_tier,
  json_extract_string(payload, '$.attr.traffic_cluster') AS traffic_cluster
FROM agent_observations
WHERE tenant = 'tenant_001'
  AND environment = 'prod'
  AND type IN ('GENERATION', 'TOOL', 'RETRIEVAL')
  AND json_extract_string(payload, '$.attr.release_ring') = 'stable'
  AND json_extract_string(payload, '$.attr.customer_tier') = 'pro'
  AND json_extract_string(payload, '$.attr.traffic_cluster') = 'cluster_d'
ORDER BY event_time DESC, trace_id DESC, observation_id DESC
LIMIT 50;
