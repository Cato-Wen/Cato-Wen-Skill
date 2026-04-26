# BigQuery Agent Log Queries

## Log Tables

Dataset: `wonder-recipe-prod.mongo_batch_recipe_agent`

| Table | Description |
|-------|-------------|
| `agent_conversation_logs` | Full conversation messages between user and agent |
| `agent_invocation_logs` | Individual agent invocation records |
| `agent_session_logs` | Session lifecycle and state changes |

## Common Debug Scenarios

### 1. Find Recent Errors

```sql
-- Recent failed invocations
SELECT
    invocation_id,
    session_id,
    agent_name,
    status,
    error_message,
    timestamp
FROM `wonder-recipe-prod.mongo_batch_recipe_agent.agent_invocation_logs`
WHERE status = 'ERROR'
ORDER BY timestamp DESC
LIMIT 100;
```

### 2. Session Timeline

```sql
-- Complete session history
SELECT
    session_id,
    event_type,
    agent_name,
    status,
    timestamp,
    details
FROM `wonder-recipe-prod.mongo_batch_recipe_agent.agent_session_logs`
WHERE session_id = 'YOUR_SESSION_ID'
ORDER BY timestamp ASC;
```

### 3. Full Conversation

```sql
-- Conversation messages in order
SELECT
    session_id,
    invocation_id,
    role,           -- 'user' or 'model'
    content,
    tool_calls,
    tool_results,
    timestamp
FROM `wonder-recipe-prod.mongo_batch_recipe_agent.agent_conversation_logs`
WHERE session_id = 'YOUR_SESSION_ID'
ORDER BY timestamp ASC;
```

### 4. Tool Execution Analysis

```sql
-- Tool calls and results
SELECT
    invocation_id,
    session_id,
    JSON_EXTRACT_SCALAR(tool_calls, '$.name') as tool_name,
    JSON_EXTRACT_SCALAR(tool_calls, '$.arguments') as tool_args,
    tool_results,
    status,
    timestamp
FROM `wonder-recipe-prod.mongo_batch_recipe_agent.agent_conversation_logs`
WHERE tool_calls IS NOT NULL
  AND session_id = 'YOUR_SESSION_ID'
ORDER BY timestamp;
```

### 5. Error Pattern Analysis

```sql
-- Error frequency by type
SELECT
    error_message,
    agent_name,
    COUNT(*) as error_count,
    MIN(timestamp) as first_occurrence,
    MAX(timestamp) as last_occurrence
FROM `wonder-recipe-prod.mongo_batch_recipe_agent.agent_invocation_logs`
WHERE status = 'ERROR'
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY error_message, agent_name
ORDER BY error_count DESC;
```

### 6. Invocation Performance

```sql
-- Invocation duration analysis
SELECT
    invocation_id,
    session_id,
    agent_name,
    TIMESTAMP_DIFF(end_timestamp, start_timestamp, SECOND) as duration_seconds,
    status,
    start_timestamp
FROM `wonder-recipe-prod.mongo_batch_recipe_agent.agent_invocation_logs`
WHERE start_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
ORDER BY duration_seconds DESC
LIMIT 50;
```

### 7. Session State Changes

```sql
-- Track state changes
SELECT
    session_id,
    timestamp,
    event_type,
    JSON_EXTRACT(state_delta, '$') as state_changes
FROM `wonder-recipe-prod.mongo_batch_recipe_agent.agent_session_logs`
WHERE session_id = 'YOUR_SESSION_ID'
  AND state_delta IS NOT NULL
ORDER BY timestamp;
```

### 8. Agent Transfer Tracking

```sql
-- Track agent transfers in multi-agent systems
SELECT
    invocation_id,
    session_id,
    agent_name as from_agent,
    LEAD(agent_name) OVER (PARTITION BY session_id ORDER BY timestamp) as to_agent,
    timestamp
FROM `wonder-recipe-prod.mongo_batch_recipe_agent.agent_invocation_logs`
WHERE session_id = 'YOUR_SESSION_ID'
ORDER BY timestamp;
```

### 9. Daily Activity Summary

```sql
-- Daily invocation summary
SELECT
    DATE(timestamp) as date,
    agent_name,
    COUNT(*) as total_invocations,
    COUNTIF(status = 'SUCCESS') as successful,
    COUNTIF(status = 'ERROR') as failed,
    ROUND(COUNTIF(status = 'ERROR') * 100.0 / COUNT(*), 2) as error_rate_percent
FROM `wonder-recipe-prod.mongo_batch_recipe_agent.agent_invocation_logs`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY DATE(timestamp), agent_name
ORDER BY date DESC, agent_name;
```

### 10. Find Related Sessions

```sql
-- Find sessions by user or content
SELECT DISTINCT
    session_id,
    MIN(timestamp) as session_start,
    MAX(timestamp) as session_end,
    COUNT(*) as message_count
FROM `wonder-recipe-prod.mongo_batch_recipe_agent.agent_conversation_logs`
WHERE content LIKE '%YOUR_SEARCH_TERM%'
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY session_id
ORDER BY session_start DESC;
```

## Debugging Workflow

1. **Get session_id** from error report or user feedback

2. **Check session lifecycle:**
   ```sql
   SELECT * FROM agent_session_logs WHERE session_id = 'XXX' ORDER BY timestamp;
   ```

3. **Review conversation:**
   ```sql
   SELECT * FROM agent_conversation_logs WHERE session_id = 'XXX' ORDER BY timestamp;
   ```

4. **Check specific invocation errors:**
   ```sql
   SELECT * FROM agent_invocation_logs
   WHERE session_id = 'XXX' AND status = 'ERROR';
   ```

5. **Analyze tool failures:**
   ```sql
   SELECT tool_calls, tool_results, error_message
   FROM agent_conversation_logs
   WHERE session_id = 'XXX' AND tool_results LIKE '%error%';
   ```

## Tips

- Always use `LIMIT` for exploratory queries
- Use `TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL X DAY)` for time ranges
- Export large results to GCS for detailed analysis
- Use `JSON_EXTRACT_SCALAR` for parsing JSON fields
