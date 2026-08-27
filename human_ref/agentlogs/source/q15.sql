SELECT
  event_time,
  trace_id,
  observation_id,
  type,
  status,
  tool_name,
  latency_ms
FROM agent_observations
WHERE tenant = 'tenant_001'
  AND type IN ('GENERATION', 'TOOL', 'RETRIEVAL', 'EVENT')
  AND (
    contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'transient upstream failure')
    OR contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'retry budget depleted')
    OR contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'connector timeout')
  )
ORDER BY latency_ms DESC, event_time DESC, trace_id DESC, observation_id DESC
LIMIT 50;
