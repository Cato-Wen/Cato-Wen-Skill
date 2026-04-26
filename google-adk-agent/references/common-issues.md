# Common ADK Agent Issues & Solutions

## Tool Issues

### 1. Tool Not Being Called

**Symptoms:** LLM generates text instead of calling the expected tool.

**Causes & Solutions:**

1. **Poor tool description**
   ```java
   // Bad - vague description
   @Schema(name = "search", description = "Search")

   // Good - clear, specific description
   @Schema(name = "search_recipes", description = "Search for recipes by name, ingredients, or cuisine type. Returns matching recipe details.")
   ```

2. **Missing parameter descriptions**
   ```java
   // Bad
   public static Map<String, Object> search(String query) { ... }

   // Good
   public static Map<String, Object> search(
       @Schema(name = "query", description = "Search query for recipe name or ingredients") String query
   ) { ... }
   ```

3. **Tool name conflicts** - Ensure unique tool names across all registered tools.

### 2. Tool Parameter Parsing Errors

**Symptoms:** `IllegalArgumentException` or parameter not found errors.

**Causes & Solutions:**

1. **Missing `-parameters` compiler flag**
   ```gradle
   // build.gradle
   compileJava {
       options.compilerArgs << '-parameters'
   }
   ```

2. **Missing @Schema annotation**
   ```java
   // Always annotate parameters
   public static Map<String, Object> myTool(
       @Schema(name = "param_name", description = "...") String param
   ) { ... }
   ```

3. **Type mismatch** - LLM may send numbers as strings or vice versa
   ```java
   // Handle type conversion gracefully
   Integer count = args.get("count") instanceof String
       ? Integer.parseInt((String) args.get("count"))
       : (Integer) args.get("count");
   ```

### 3. Tool Returns Empty/Null

**Symptoms:** Tool executes but agent doesn't see results.

**Solution:** Always return a Map with results:
```java
// Bad
return null;

// Good
return Map.of("status", "success", "result", actualResult);

// For empty results
return Map.of("status", "no_results", "message", "No matching items found");
```

## Session Issues

### 4. Session Not Found

**Symptoms:** `IllegalArgumentException: Session not found`

**Solutions:**

1. **Enable auto-create:**
   ```java
   RunConfig config = RunConfig.builder()
       .autoCreateSession(true)
       .build();
   ```

2. **Create session explicitly:**
   ```java
   Session session = sessionService.createSession(appName, userId, null, sessionId)
       .blockingGet();
   ```

### 5. State Not Persisting

**Symptoms:** Session state lost between invocations.

**Solutions:**

1. **Use stateDelta correctly:**
   ```java
   Map<String, Object> stateDelta = new HashMap<>();
   stateDelta.put("key", "value");
   runner.runAsync(userId, sessionId, message, runConfig, stateDelta);
   ```

2. **Check SessionService implementation** - InMemorySessionService doesn't persist across restarts.

### 6. Conversation History Missing

**Symptoms:** Agent doesn't remember previous messages.

**Solutions:**

1. **Check session ID consistency** - Same session ID must be used.

2. **Verify includeContents setting:**
   ```java
   LlmAgent agent = LlmAgent.builder()
       .includeContents(LlmAgent.IncludeContents.DEFAULT)  // Not NONE
       .build();
   ```

## Agent Issues

### 7. Agent Transfer Loops

**Symptoms:** Agents transfer back and forth indefinitely.

**Solutions:**

1. **Set maxSteps:**
   ```java
   LlmAgent agent = LlmAgent.builder()
       .maxSteps(10)
       .build();
   ```

2. **Improve agent instructions** - Be explicit about when to transfer.

3. **Use disallowTransferToParent/Peers:**
   ```java
   LlmAgent specialist = LlmAgent.builder()
       .disallowTransferToPeers(true)
       .build();
   ```

### 8. Model Not Found

**Symptoms:** `IllegalStateException: No model found for agent`

**Solutions:**

1. **Set model on agent:**
   ```java
   LlmAgent agent = LlmAgent.builder()
       .model("gemini-2.0-flash")
       .build();
   ```

2. **Parent agent must have model** for sub-agents to inherit.

### 9. Callback Errors

**Symptoms:** Callbacks not executing or throwing errors.

**Debug approach:**
```java
LlmAgent agent = LlmAgent.builder()
    .beforeModelCallbackSync((context, request) -> {
        System.out.println("Before model: " + request);
        return Optional.empty();  // Continue normally
    })
    .afterModelCallbackSync((context, response) -> {
        System.out.println("After model: " + response);
        return Optional.empty();
    })
    .onModelErrorCallbackSync((context, request, error) -> {
        System.err.println("Model error: " + error.getMessage());
        return Optional.empty();
    })
    .build();
```

## Performance Issues

### 10. Slow Response Times

**Causes & Solutions:**

1. **Too many tools** - Reduce to essential tools only.

2. **Large conversation history:**
   ```java
   // Enable event compaction
   App app = App.builder()
       .rootAgent(agent)
       .eventsCompactionConfig(EventsCompactionConfig.builder()
           .compactionInterval(10)
           .build())
       .build();
   ```

3. **Synchronous tool calls** - Use async patterns:
   ```java
   public static Single<Map<String, Object>> asyncTool(...) {
       return Single.fromCallable(() -> {
           // Long-running operation
           return Map.of("result", value);
       }).subscribeOn(Schedulers.io());
   }
   ```

### 11. Memory Issues

**Symptoms:** OutOfMemoryError with large sessions.

**Solutions:**

1. **Use external session service** instead of InMemorySessionService.

2. **Enable event compaction** (see above).

3. **Limit artifact storage size.**

## Debugging Tips

### Enable Detailed Logging

```java
// Add to your logging configuration
<logger name="com.google.adk" level="DEBUG"/>
```

### Use LoggingPlugin

```java
Runner runner = Runner.builder()
    .agent(agent)
    .appName("my-app")
    .plugins(new LoggingPlugin())
    .build();
```

### Trace Invocations

```java
runner.runAsync(userId, sessionId, message, runConfig)
    .doOnNext(event -> {
        System.out.println("Event: " + event.author() + " - " + event.id());
        event.content().ifPresent(c -> System.out.println("Content: " + c));
    })
    .subscribe();
```

### Check BigQuery Logs

For production issues, always check:
1. `agent_session_logs` - Session lifecycle
2. `agent_invocation_logs` - Error details
3. `agent_conversation_logs` - Full conversation context

See [bigquery-queries.md](bigquery-queries.md) for query templates.
