SELECT
  json_extract_string(payload, '$.attr.deployment_channel') AS deployment_channel,
  json_extract_string(payload, '$.attr.release_ring') AS release_ring,
  count(*) AS incident_observations,
  count(DISTINCT trace_id) AS incident_traces,
  avg(latency_ms) AS avg_latency_ms
FROM agent_observations
WHERE type IN ('GENERATION', 'TOOL', 'RETRIEVAL', 'EVENT')
  AND (
    contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'error')
    OR contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'timeout')
    OR contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'retry')
  )
GROUP BY 1, 2
ORDER BY incident_observations DESC, incident_traces DESC, deployment_channel ASC, release_ring ASC
LIMIT 20;
