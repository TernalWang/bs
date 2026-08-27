SELECT
  trace_id,
  seq_no,
  type,
  status,
  model,
  tool_name,
  input,
  output
FROM agent_observations
WHERE trace_id = 'trace_033053_6ef70596'
ORDER BY seq_no ASC;
