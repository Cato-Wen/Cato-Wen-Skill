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

- **ADK Java Source**: `${ADK_JAVA_HOME}` - Local ADK Java SDK source code (set this env var to your local clone of `google/adk-java`)
- **Official Docs**: https://adk.dev/ | https://google.github.io/adk-docs
- **GitHub**: https://github.com/google/adk-java
- **Getting Started**: https://adk.dev/get-started/java/

### Setup: Configure ADK_JAVA_HOME

This skill references the local ADK Java source. Configure the `ADK_JAVA_HOME` environment variable to point at your clone:

```powershell
# Windows (PowerShell, persistent for current user)
[Environment]::SetEnvironmentVariable("ADK_JAVA_HOME", "C:\adk-java", "User")
```

```bash
# macOS / Linux (add to ~/.bashrc or ~/.zshrc)
export ADK_JAVA_HOME="$HOME/code/adk-java"
```

If you don't have the source yet:
```bash
git clone https://github.com/google/adk-java.git "$ADK_JAVA_HOME"
```

When this skill mentions a path like `${ADK_JAVA_HOME}/core/src/main/java/...`, substitute the env var with your actual local path before opening the file.

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
6. **Review source code**: Reference local ADK source at `${ADK_JAVA_HOME}`

## Critical: Always Read ADK Source Code First

**IMPORTANT**: When analyzing or fixing ADK-related bugs, ALWAYS read the ADK source code BEFORE making conclusions or implementing fixes.

### Bug Analysis Methodology

1. **Read logs to identify symptoms** - Note error messages, stack traces, timing
2. **Read ADK source code to understand mechanism** - Don't guess, understand how the component actually works
3. **Verify with multiple log samples** - One log sample is not enough; use multiple samples to confirm patterns
4. **Don't assume correlation = causation** - Multiple errors in same log may be independent issues

### Bug Fixing Methodology

1. **Read ADK source to find framework-provided solutions** - ADK often provides configurations, interfaces, or patterns for common scenarios
2. **Avoid implementing custom solutions** - Check if the framework already handles your use case
3. **Understand component lifecycle** - Know how components are created, used, and cleaned up
4. **Follow ADK's design patterns** - Use the framework the way it was designed to be used

### Common Pitfalls to Avoid

| Pitfall | Why It's Wrong | What To Do Instead |
|---------|----------------|---------------------|
| Guessing causation from logs | Multiple errors may be unrelated | Read source code to understand actual mechanism |
| Implementing manual workarounds | Framework may already have a solution | Check ADK source for existing patterns |
| Reading only one log sample | Could be coincidental or edge case | Verify patterns across multiple samples |
| Skipping source code review | Miss understanding of how things actually work | Always read relevant source files first |

### Key Source Files by Issue Type

| Issue Type | Files to Read |
|------------|---------------|
| MCP/Tool issues | `McpToolset.java`, `McpTool.java`, `McpSessionManager.java`, `BaseToolset.java` |
| Agent lifecycle | `LlmAgent.java`, `BaseAgent.java` |
| Session issues | `Session.java`, `InMemorySessionService.java` |
| Callback issues | Callback interfaces in `com.google.adk.agents` |
| Model/LLM issues | `Gemini.java`, `Claude.java`, `BaseLlmFlow.java` |

### Pre-Analysis Checklist

Before analyzing any ADK bug:
- [ ] Collect multiple log samples showing the issue
- [ ] Identify the ADK components involved
- [ ] Read the relevant ADK source files at `${ADK_JAVA_HOME}`
- [ ] Understand the component lifecycle and dependencies
- [ ] Check if ADK provides configuration or patterns for this scenario

## Key Files in ADK Source

For deeper investigation, reference these key source files:

- `${ADK_JAVA_HOME}/core/src/main/java/com/google/adk/agents/LlmAgent.java` - Agent implementation
- `${ADK_JAVA_HOME}/core/src/main/java/com/google/adk/runner/Runner.java` - Runner implementation
- `${ADK_JAVA_HOME}/core/src/main/java/com/google/adk/tools/FunctionTool.java` - Tool implementation
- `${ADK_JAVA_HOME}/core/src/main/java/com/google/adk/sessions/` - Session management
- `${ADK_JAVA_HOME}/core/src/main/java/com/google/adk/events/Event.java` - Event model

## References

- [ADK Java Architecture](references/adk-architecture.md) - Detailed architecture guide
- [BigQuery Queries](references/bigquery-queries.md) - Debug query templates
- [Common Issues](references/common-issues.md) - Troubleshooting guide
