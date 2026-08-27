SELECT
  trace_id,
  min(event_time) AS started_at,
  count(*) AS observation_count,
  sum(CASE WHEN status <> 'ok' THEN 1 ELSE 0 END) AS failure_count,
  sum(total_cost) AS total_cost,
  sum(latency_ms) AS total_latency_ms
FROM agent_observations
WHERE biz_date BETWEEN DATE '2026-03-17' AND DATE '2027-03-20'
GROUP BY trace_id
ORDER BY total_cost DESC, total_latency_ms DESC, trace_id ASC
LIMIT 50;
