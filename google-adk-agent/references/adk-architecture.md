# Google ADK Java Architecture

## Overview

ADK (Agent Development Kit) is a code-first Java toolkit for building AI agents with Google's Gemini models.

## Core Components

### 1. LlmAgent

The primary agent class for LLM-based interactions.

**Key Properties:**
- `name` - Unique identifier
- `description` - Agent purpose description
- `model` - LLM model (e.g., "gemini-2.0-flash")
- `instruction` - System prompt
- `tools` - Available tools/functions
- `subAgents` - Child agents for multi-agent systems

**Builder Pattern:**
```java
LlmAgent agent = LlmAgent.builder()
    .name("agent_name")
    .description("What this agent does")
    .model("gemini-2.0-flash")
    .instruction("System instructions here")
    .tools(tool1, tool2)
    .subAgents(childAgent1, childAgent2)
    .maxSteps(10)  // Optional: limit iterations
    .build();
```

**Callbacks:**
- `beforeModelCallback` - Before LLM call
- `afterModelCallback` - After LLM response
- `onModelErrorCallback` - On LLM error
- `beforeToolCallback` - Before tool execution
- `afterToolCallback` - After tool execution
- `onToolErrorCallback` - On tool error

### 2. Runner

Executes agents and manages sessions.

```java
Runner runner = Runner.builder()
    .agent(rootAgent)
    .appName("my-application")
    .sessionService(sessionService)      // Optional
    .artifactService(artifactService)    // Optional
    .memoryService(memoryService)        // Optional
    .plugins(plugin1, plugin2)           // Optional
    .build();

// Run async
Flowable<Event> events = runner.runAsync(userId, sessionId, userMessage, runConfig);
```

**Services:**
- `SessionService` - Manages conversation sessions
- `ArtifactService` - Handles file/blob storage
- `MemoryService` - Long-term memory storage

### 3. Session & Events

**Session Structure:**
```java
Session session = sessionService.createSession(appName, userId, state, sessionId);
// Contains: events, state, userId, id, appName
```

**Event Types:**
- User message events (author="user")
- Model response events (author="model" or agent name)
- Tool call events
- Error events

### 4. Tools

**FunctionTool - Custom Functions:**
```java
public class MyTools {
    @Schema(name = "tool_name", description = "Tool description")
    public static Map<String, Object> myTool(
        @Schema(name = "param1", description = "Parameter description") String param1,
        @Schema(name = "param2", description = "Optional param", optional = true) Integer param2
    ) {
        return Map.of("result", "value");
    }
}

FunctionTool tool = FunctionTool.create(MyTools.class, "myTool");
```

**Built-in Tools:**
- `GoogleSearchTool` - Web search
- `GoogleMapsTool` - Maps API
- `UrlContextTool` - URL content fetching
- `LoadMemoryTool` - Memory retrieval
- `LoadArtifactsTool` - Artifact loading

**Toolsets:**
- `BaseToolset` - Group multiple tools
- MCP tools via `McpTool` / `McpToolset`

### 5. Multi-Agent Systems

**Hierarchical Agents:**
```java
LlmAgent childAgent = LlmAgent.builder()
    .name("specialist")
    .description("Handles specific tasks")
    .model("gemini-2.0-flash")
    .instruction("Specialist instructions")
    .disallowTransferToParent(false)  // Allow returning to parent
    .build();

LlmAgent rootAgent = LlmAgent.builder()
    .name("coordinator")
    .description("Routes to specialists")
    .model("gemini-2.0-flash")
    .instruction("Route requests appropriately")
    .subAgents(childAgent)
    .build();
```

**Agent Types:**
- `LlmAgent` - LLM-based agent
- `SequentialAgent` - Run agents in sequence
- `ParallelAgent` - Run agents in parallel
- `LoopAgent` - Iterative agent execution

### 6. Flows

Internal execution flows:
- `SingleFlow` - Single agent without transfers
- `AutoFlow` - Automatic agent transfer handling

## Execution Model

```
User Message
    ↓
Runner.runAsync()
    ↓
Session.appendEvent(userMessage)
    ↓
Agent.runAsync(invocationContext)
    ↓
┌─────────────────────────────┐
│  LLM Flow Loop              │
│  1. Build LLM request       │
│  2. Call beforeModelCallback│
│  3. Send to LLM             │
│  4. Call afterModelCallback │
│  5. Process tool calls      │
│     - beforeToolCallback    │
│     - Execute tool          │
│     - afterToolCallback     │
│  6. Repeat or return        │
└─────────────────────────────┘
    ↓
Emit Events → Session.appendEvent()
    ↓
Return Flowable<Event>
```

## Key Interfaces

### InvocationContext

Contains all context for an agent invocation:
- `session` - Current session
- `agent` - Executing agent
- `invocationId` - Unique invocation ID
- `runConfig` - Execution configuration
- `userContent` - User's message

### ToolContext

Passed to tool functions:
- `invocationContext` - Parent context
- `functionCallId` - Tool call ID
- Session state access

### RunConfig

Execution configuration:
- `autoCreateSession` - Auto-create missing sessions
- `saveInputBlobsAsArtifacts` - Save blobs to artifacts
- `responseModalities` - Output modalities (TEXT, AUDIO)

## Source Code Reference

Key files in `C:\adk-java\core\src\main\java\com\google\adk\`:

| Path | Description |
|------|-------------|
| `agents/LlmAgent.java` | Main agent implementation |
| `agents/BaseAgent.java` | Agent base class |
| `agents/InvocationContext.java` | Invocation context |
| `runner/Runner.java` | Agent runner |
| `tools/FunctionTool.java` | Function tool |
| `tools/BaseTool.java` | Tool base class |
| `sessions/Session.java` | Session model |
| `sessions/BaseSessionService.java` | Session service interface |
| `events/Event.java` | Event model |
| `flows/llmflows/AutoFlow.java` | Auto flow implementation |
