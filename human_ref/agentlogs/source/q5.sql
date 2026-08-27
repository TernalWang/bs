SELECT
  event_time,
  trace_id,
  observation_id,
  tool_name,
  latency_ms,
  (
    CASE WHEN contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'unable') THEN 1 ELSE 0 END +
    CASE WHEN contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'open') THEN 1 ELSE 0 END
  ) AS text_score,
  payload
FROM agent_observations
WHERE type = 'TOOL'
  AND status = 'error'
  AND tenant = 'tenant_001'
  AND app = 'app_001'
  AND contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'unable')
  AND contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'open')
ORDER BY text_score DESC, latency_ms DESC, event_time DESC
LIMIT 50;
