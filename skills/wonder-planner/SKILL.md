---
name: wonder-planner
description: Design implementation plan based on requirement analysis. Use after wonder-analyzer to create detailed step-by-step implementation plan, identify reusable code, and decide execution approach. Pauses for confirmation on complex requirements.
user-invocable: true
---

# Wonder Implementation Planner

Create detailed implementation plans based on requirement analysis.

## Input

Expects output from `wonder-analyzer` or context from previous analysis:
- Ticket summary
- Related modules
- Related code files
- Reusable patterns

## Workflow

### Step 1: Deep Code Analysis

```
1. Read all related_code files identified by analyzer
2. Understand existing patterns:
   - Class structure and naming conventions
   - Method signatures and return types
   - Exception handling patterns
   - Logging patterns
3. Identify integration points:
   - Which methods to modify
   - Which interfaces to extend
   - Which services to inject
```

### Step 2: Identify Reusable Code

Search for reusable components:

```
1. Same module utilities:
   - Helper classes
   - Utility methods
   - Common validators

2. Cross-module patterns:
   - Similar feature implementations
   - Shared libraries in tool/

3. Framework patterns:
   - Core-NG standard patterns
   - Project-specific conventions
```

**Code Reuse Checklist:**
```
□ Check for existing validation logic
□ Check for existing transformation logic
□ Check for existing error handling patterns
□ Check for existing test helpers
□ Check tool/*-library for shared utilities
```

### Step 3: Design Implementation Steps

Create ordered steps following dependency chain:

```
Standard Order (adjust as needed):
1. Interface changes (if new API contract)
2. Domain model changes (if new entities/enums)
3. Service implementation
4. Integration/wiring
5. Unit tests
6. Integration tests (if applicable)
```

For each step, specify:
```yaml
- id: <number>
  action: "new" | "modify"
  file: "<full file path>"
  description: "<what to do>"
  reuse_from: "<source file/pattern>" (optional)
  depends_on: [<step ids>] (optional)
  estimated_lines: <approximate lines to add/change>
```

### Step 4: Determine Execution Mode

**Decision Matrix:**

| Complexity | Confidence | Mode |
|------------|------------|------|
| Simple | High | `auto` - proceed without confirmation |
| Simple | Medium/Low | `confirm_first` - show plan, get approval |
| Medium | High | `confirm_first` - show plan, get approval |
| Medium | Medium/Low | `confirm_first` - ask clarifying questions |
| Complex | Any | `confirm_first` - detailed review required |

**Additional Triggers for Confirmation:**
- Database schema changes
- New external API calls
- Changes to shared interfaces
- Significant architectural decisions
- Multiple valid implementation approaches

### Step 5: Generate Output

```yaml
ticket_id: "MD-XXXXX"
approach: "<high-level approach description>"
execution_mode: "auto" | "confirm_first"

architecture_decisions:
  - decision: "<what was decided>"
    rationale: "<why this approach>"
    alternatives: ["<other options considered>"]

reusable_code:
  - source: "<file path>"
    what: "<what can be reused>"
    how: "<how to apply it>"

steps:
  - id: 1
    action: "modify"
    file: "backend/master-data-interface/src/.../ItemStatus.java"
    description: "Add DORMANT enum value"
    estimated_lines: 5

  - id: 2
    action: "modify"
    file: "backend/master-data-service/src/.../ItemService.java"
    description: "Add checkDormantStatus() method"
    reuse_from: "StatusValidator.java validation pattern"
    depends_on: [1]
    estimated_lines: 25

  - id: 3
    action: "modify"
    file: "backend/master-data-service/src/test/.../ItemServiceTest.java"
    description: "Add unit tests for dormant status check"
    depends_on: [2]
    estimated_lines: 40

code_style_notes:
  - "Use @Nullable annotation for optional parameters"
  - "Follow existing exception handling: throw BadRequestException for validation errors"
  - "Logger format: logger.info(\"action description, field={}\", value)"

questions: []  # Any remaining clarifications needed
```

## Interaction Patterns

### When execution_mode is "auto"
```
Output: "Implementation plan ready. Proceeding with coding..."
Action: Pass plan to wonder-coder
```

### When execution_mode is "confirm_first"
```
Output:
"
## Implementation Plan for MD-XXXXX

**Approach:** <approach description>

**Steps:**
1. [modify] ItemStatus.java - Add DORMANT enum
2. [modify] ItemService.java - Add checkDormantStatus()
3. [modify] ItemServiceTest.java - Add tests

**Reusing from:**
- StatusValidator.java: validation pattern

**Questions:**
- <any clarifications needed>

Proceed with this plan? (yes/no/adjust)
"

Wait for user confirmation before passing to wonder-coder
```

### Handling User Feedback
```
User: "no, also need to add API endpoint"
Action: Revise plan to include API changes, re-present

User: "yes"
Action: Pass plan to wonder-coder

User: "adjust: use different validation approach"
Action: Update plan with user's preference, re-present
```

## Example Output

```yaml
ticket_id: "MD-17329"
approach: "Add dormant status check to ItemService following existing validation patterns"
execution_mode: "confirm_first"

architecture_decisions:
  - decision: "Add method to existing ItemService rather than new service"
    rationale: "Follows existing pattern, minimal change footprint"
    alternatives: ["Create separate DormantStatusService"]

reusable_code:
  - source: "backend/product-catalog-service/src/.../StatusValidator.java"
    what: "Validation method structure and error handling"
    how: "Copy pattern, adapt for dormant-specific logic"

steps:
  - id: 1
    action: "modify"
    file: "backend/master-data-interface/src/main/java/app/masterdata/api/item/ItemStatus.java"
    description: "Add DORMANT to status enum"
    estimated_lines: 3

  - id: 2
    action: "modify"
    file: "backend/master-data-service/src/main/java/app/masterdata/item/service/ItemService.java"
    description: "Add checkDormantStatus(String itemId) method with validation"
    reuse_from: "StatusValidator.java"
    depends_on: [1]
    estimated_lines: 20

  - id: 3
    action: "modify"
    file: "backend/master-data-service/src/test/java/app/masterdata/item/service/ItemServiceTest.java"
    description: "Add tests: testCheckDormantStatus_valid, testCheckDormantStatus_notFound, testCheckDormantStatus_alreadyDormant"
    depends_on: [2]
    estimated_lines: 35

code_style_notes:
  - "Method naming: check<Action>() for validation methods"
  - "Return type: void for validation, throw exception on failure"
  - "Test naming: test<Method>_<scenario>"

questions: []
```

## Next Step

After plan approval, output:
"Plan confirmed. Run /wonder-coder to implement."
