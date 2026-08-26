SELECT
  json_extract_string(payload, '$.attr.release_ring') AS release_ring,
  json_extract_string(payload, '$.attr.customer_tier') AS customer_tier,
  json_extract_string(payload, '$.attr.retrieval_strategy') AS retrieval_strategy,
  count(*) AS observations,
  avg(latency_ms) AS avg_latency_ms,
  sum(total_cost) AS total_cost
FROM agent_observations
GROUP BY 1, 2, 3
ORDER BY observations DESC, total_cost DESC,
  release_ring ASC, customer_tier ASC, retrieval_strategy ASC
LIMIT 50;
