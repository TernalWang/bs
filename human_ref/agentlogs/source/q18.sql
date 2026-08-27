SELECT
  json_extract_string(payload, '$.attr.prompt_template_version') AS prompt_template_version,
  count(*) AS observations,
  count(DISTINCT trace_id) AS traces,
  avg(latency_ms) AS avg_latency_ms,
  sum(total_cost) AS total_cost
FROM agent_observations
WHERE type IN ('GENERATION', 'REASONING', 'TOOL')
GROUP BY 1
ORDER BY observations DESC, total_cost DESC, prompt_template_version ASC
LIMIT 20;
