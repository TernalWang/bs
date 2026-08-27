SELECT
  trace_id,
  observation_id,
  seq_no,
  type,
  status,
  json_extract_string(payload, '$.attr.request_key') AS request_key,
  json_extract_string(payload, '$.attr.workflow_variant') AS workflow_variant
FROM agent_observations
WHERE tenant = 'tenant_001'
  AND json_extract_string(payload, '$.attr.request_key') = 'req_000001_8cace09f'
  AND json_extract_string(payload, '$.attr.workflow_variant') = 'long_context_replay'
ORDER BY seq_no ASC, observation_id ASC
LIMIT 100;
