SELECT
  event_time,
  trace_id,
  observation_id,
  type,
  status,
  payload
FROM agent_observations
WHERE environment = 'prod'
  AND type IN ('GENERATION', 'TOOL', 'RETRIEVAL')
  AND json_extract_string(payload, '$.attr.release_ring') IN ('stable', 'canary')
  AND json_extract_string(payload, '$.attr.retrieval_strategy') IN ('hybrid', 'hybrid_rerank')
  AND json_extract_string(payload, '$.attr.surface') IN ('api', 'workflow_runner')
  AND json_extract_string(payload, '$.attr.prompt_template_version') IN ('pt_2026_03_2', 'pt_2026_04_1', 'pt_2026_04_2')
ORDER BY event_time DESC, trace_id DESC, observation_id DESC
LIMIT 50;
