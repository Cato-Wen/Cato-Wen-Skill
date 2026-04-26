---
name: google-adk-agent
description: |
  Google ADK (Agent Development Kit) Java agent development and production debugging toolkit.
  Use when: (1) Developing new agents with Google ADK Java, (2) Debugging production agent issues,
  (3) Querying agent logs from BigQuery, (4) Understanding ADK architecture and patterns,
  (5) Troubleshooting agent sessions, invocations, or conversations. Triggers on "ADK", "agent debug",
  "agent logs", "BigQuery agent", "session logs", "invocation logs", "conversation logs".
---

# Google ADK Agent Development & Debugging

This skill provides guidance for developing and debugging AI agents built with Google ADK (Agent Development Kit) Java.

## Resources

- **ADK Java Source**: `C:\adk-java` - Local ADK Java SDK source code
- **Official Docs**: https://adk.dev/ | https://google.github.io/adk-docs
- **GitHub**: https://github.com/google/adk-java
- **Getting Started**: https://adk.dev/get-started/java/

## Quick Reference

### Core ADK Components

| Component | Class | Purpose |
|-----------|-------|---------|
| Agent | `LlmAgent` | LLM-based agent with tools and instructions |
| Runner | `Runner` | Executes agents with session management |
| Tool | `FunctionTool` | Custom function calling tool |
| Session | `Session` | Conversation state and history |
| Event | `Event` | Agent execution events |

### Basic Agent Creation

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.runner.Runner;

LlmAgent agent = LlmAgent.builder()
    .name("my_agent")
    .description("Agent description")
    .model("gemini-2.0-flash")
    .instruction("You are a helpful assistant.")
    .tools(myTool1, myTool2)
    .build();

Runner runner = Runner.builder()
    .agent(agent)
    .appName("my-app")
    .build();
```

### Creating Custom Tools

```java
import com.google.adk.tools.FunctionTool;
import com.google.adk.tools.Annotations.Schema;

public class MyTools {
    @Schema(name = "search_database", description = "Search the database")
    public static Map<String, Object> searchDatabase(
        @Schema(name = "query", description = "Search query") String query
    ) {
        // Implementation
        return Map.of("result", results);
    }
}

// Register tool
FunctionTool tool = FunctionTool.create(MyTools.class, "searchDatabase");
```

## Production Debugging

### BigQuery Log Tables

Agent logs are stored in BigQuery at `wonder-recipe-prod.mongo_batch_recipe_agent`:

| Table | Purpose |
|-------|---------|
| `agent_conversation_logs` | Full conversation history |
| `agent_invocation_logs` | Individual agent invocations |
| `agent_session_logs` | Session lifecycle events |

### Common Debug Queries

See [references/bigquery-queries.md](references/bigquery-queries.md) for detailed query examples.

**Quick queries:**

```sql
-- Recent errors
SELECT * FROM `wonder-recipe-prod.mongo_batch_recipe_agent.agent_invocation_logs`
WHERE status = 'ERROR'
ORDER BY timestamp DESC LIMIT 100;

-- Session timeline
SELECT * FROM `wonder-recipe-prod.mongo_batch_recipe_agent.agent_session_logs`
WHERE session_id = 'YOUR_SESSION_ID'
ORDER BY timestamp;

-- Conversation history
SELECT * FROM `wonder-recipe-prod.mongo_batch_recipe_agent.agent_conversation_logs`
WHERE session_id = 'YOUR_SESSION_ID'
ORDER BY timestamp;
```

## Debugging Workflow

1. **Identify the issue**: Get session_id or invocation_id from error reports
2. **Query session logs**: Check session lifecycle and state
3. **Query invocation logs**: Find specific invocation errors
4. **Query conversation logs**: Review full conversation context
5. **Analyze tool calls**: Check tool execution results
6. **Review source code**: Reference local ADK source at `C:\adk-java`

## Key Files in ADK Source

For deeper investigation, reference these key source files:

- `C:\adk-java\core\src\main\java\com\google\adk\agents\LlmAgent.java` - Agent implementation
- `C:\adk-java\core\src\main\java\com\google\adk\runner\Runner.java` - Runner implementation
- `C:\adk-java\core\src\main\java\com\google\adk\tools\FunctionTool.java` - Tool implementation
- `C:\adk-java\core\src\main\java\com\google\adk\sessions\` - Session management
- `C:\adk-java\core\src\main\java\com\google\adk\events\Event.java` - Event model

## References

- [ADK Java Architecture](references/adk-architecture.md) - Detailed architecture guide
- [BigQuery Queries](references/bigquery-queries.md) - Debug query templates
- [Common Issues](references/common-issues.md) - Troubleshooting guide
