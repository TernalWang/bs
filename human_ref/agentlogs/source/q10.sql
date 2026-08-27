SELECT
  json_extract_string(payload, '$.provider.stop_reason') AS stop_reason,
  json_extract_string(payload, '$.provider.cache_hit') AS cache_hit,
  count(*) AS observations,
  avg(latency_ms) AS avg_latency_ms
FROM agent_observations
WHERE type = 'GENERATION'
GROUP BY 1, 2
ORDER BY observations DESC, avg_latency_ms DESC, stop_reason ASC, cache_hit ASC
LIMIT 50;
