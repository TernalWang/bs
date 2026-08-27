SELECT
  count(*) AS observations,
  count(DISTINCT trace_id) AS traces,
  max(event_time) AS last_event_time
FROM agent_observations
WHERE biz_date BETWEEN DATE '2026-03-17' AND DATE '2027-03-20'
  AND tenant = 'tenant_001'
  AND type IN ('GENERATION', 'TOOL', 'RETRIEVAL', 'EVENT')
  AND (
    contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'timeout awaiting headers')
    OR contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'retry budget depleted')
    OR contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'transient upstream failure')
  );
