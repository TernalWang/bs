SELECT
  json_extract_string(payload, '$.attr.workflow_variant') AS workflow_variant,
  json_extract_string(payload, '$.attr.policy_pack') AS policy_pack,
  count(*) AS observations,
  count(DISTINCT tenant) AS tenants,
  avg(latency_ms) AS avg_latency_ms,
  sum(total_cost) AS total_cost
FROM agent_observations
WHERE type IN ('GENERATION', 'TOOL', 'RETRIEVAL', 'REASONING')
GROUP BY 1, 2
ORDER BY observations DESC, total_cost DESC, workflow_variant ASC, policy_pack ASC
LIMIT 20;
