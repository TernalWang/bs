SELECT
  event_time,
  trace_id,
  observation_id,
  type,
  status,
  input,
  output,
  contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'unable to open') AS phrase_match,
  (
    CASE WHEN contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'unable') THEN 1 ELSE 0 END +
    CASE WHEN contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'open') THEN 1 ELSE 0 END
  ) AS text_score
FROM agent_observations
WHERE tenant = 'tenant_001'
  AND contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'unable')
  AND contains(lower(concat_ws(' ', coalesce(input, ''), coalesce(output, ''))), 'open')
ORDER BY phrase_match DESC, text_score DESC, event_time DESC, trace_id DESC, observation_id DESC
LIMIT 50;
