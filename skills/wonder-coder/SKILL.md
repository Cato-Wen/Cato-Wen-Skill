---
name: wonder-coder
description: Write code and tests following the implementation plan. Use after wonder-planner to implement code changes, following existing patterns and style conventions. Generates production-ready code with proper tests.
user-invocable: true
---

# Wonder Code Writer

Implement code changes following the approved plan.

## Input

Expects implementation plan from `wonder-planner`:
- Ordered steps with file paths
- Reusable code references
- Code style notes
- Dependencies between steps

## Workflow

### Step 1: Pre-Implementation Setup

```
1. Read all files that will be modified
2. Read all reuse_from reference files
3. Note existing code style:
   - Import organization
   - Indentation (spaces/tabs)
   - Brace style
   - Comment style
   - Annotation usage
```

### Step 2: Execute Steps in Order

For each step in the plan:

```
1. Check dependencies are complete
2. Read current file content (if modifying)
3. Apply changes following style guide
4. Report progress: "Step N/M: <description>"
```

**For "modify" actions:**
```
1. Locate insertion/modification point
2. Match surrounding code style exactly
3. Add minimal necessary changes
4. Preserve existing functionality
```

**For "new" actions:**
```
1. Follow project file structure conventions
2. Copy structure from similar existing files
3. Include standard header/imports
4. Add proper package declaration
```

### Step 3: Code Style Alignment

**Naming Conventions (Core-NG / Wonder):**
```java
// Classes: PascalCase
public class ItemService { }

// Methods: camelCase, verb-first
public void checkDormantStatus(String itemId) { }
public Item getItemById(String id) { }
public List<Item> findItemsByStatus(ItemStatus status) { }

// Constants: UPPER_SNAKE_CASE
public static final String DEFAULT_STATUS = "ACTIVE";

// Variables: camelCase
private final ItemRepository itemRepository;
```

**Import Organization:**
```java
// Standard order in Wonder project:
import core.*;                    // Core-NG framework
import app.*;                     // Application packages
import java.*;                    // Java standard
import javax.*;                   // Java extensions
import org.*;                     // Third-party
```

**Exception Handling:**
```java
// Use Core-NG exceptions
throw new BadRequestException("message");      // 400
throw new NotFoundException("message");        // 404
throw new ConflictException("message");        // 409

// Include context in message
throw new NotFoundException("item not found, id=" + itemId);
```

**Logging:**
```java
// Use Core-NG logger
private final Logger logger = LoggerFactory.getLogger(ItemService.class);

// Log format: action, field=value
logger.info("check dormant status, itemId={}", itemId);
logger.warn("item already dormant, itemId={}, currentStatus={}", itemId, status);
```

**Annotations:**
```java
// Nullable parameters
public void process(@Nullable String optionalParam) { }

// Inject dependencies
@Inject
ItemRepository itemRepository;

// API endpoints (for WebService)
@Path("/items/:id/dormant")
@PUT
public void markDormant(@PathParam("id") String id) { }
```

### Step 4: Write Tests

**Test Structure:**
```java
class ItemServiceTest {
    @BeforeEach
    void setup() {
        // Initialize mocks and test instance
    }

    @Test
    void checkDormantStatus_validItem_returnsTrue() {
        // Given
        // When
        // Then
    }

    @Test
    void checkDormantStatus_itemNotFound_throwsNotFoundException() {
        // Given
        // When & Then
        assertThrows(NotFoundException.class, () -> {
            service.checkDormantStatus("non-existent");
        });
    }
}
```

**Test Naming Convention:**
```
test<MethodName>_<Scenario>_<ExpectedResult>

Examples:
- testCheckDormantStatus_validItem_returnsTrue
- testCheckDormantStatus_nullId_throwsBadRequest
- testCheckDormantStatus_alreadyDormant_throwsConflict
```

**Test Coverage Goals:**
```
□ Happy path (normal successful case)
□ Edge cases (null, empty, boundary values)
□ Error cases (not found, invalid input, conflict)
□ Business rule validation
```

### Step 5: Progress Tracking

Report after each step:
```
[1/4] Modified ItemStatus.java - Added DORMANT enum (+3 lines)
[2/4] Modified ItemService.java - Added checkDormantStatus() (+22 lines)
[3/4] Modified ItemServiceTest.java - Added 3 test cases (+38 lines)
[4/4] Complete
```

### Step 6: Generate Output

```yaml
implementation_complete: true
ticket_id: "MD-XXXXX"

files_created:
  - path: "<full path>"
    lines_added: <number>
    description: "<what was created>"

files_modified:
  - path: "<full path>"
    lines_added: <number>
    lines_removed: <number>
    changes:
      - "<brief description of change 1>"
      - "<brief description of change 2>"

tests_written:
  - file: "<test file path>"
    test_cases:
      - name: "testCheckDormantStatus_validItem"
        type: "happy_path"
      - name: "testCheckDormantStatus_notFound"
        type: "error_case"

issues_encountered: []  # Any problems found during implementation

notes:
  - "<any implementation notes for reviewer>"
```

## Code Quality Checklist

Before completion, verify:

```
□ No hardcoded values (use constants or config)
□ No unused imports
□ No unused variables
□ Proper null handling
□ Proper exception handling
□ Logging at appropriate levels
□ Tests cover main scenarios
□ Code matches existing style
□ No new dependencies added (unless discussed)
```

## Example Implementation

**Step: Add enum value**
```java
// Before
public enum ItemStatus {
    ACTIVE,
    INACTIVE
}

// After
public enum ItemStatus {
    ACTIVE,
    INACTIVE,
    DORMANT
}
```

**Step: Add service method**
```java
// Following existing pattern from StatusValidator
public void checkDormantStatus(String itemId) {
    if (itemId == null) {
        throw new BadRequestException("itemId is required");
    }

    Item item = itemRepository.get(itemId)
        .orElseThrow(() -> new NotFoundException("item not found, id=" + itemId));

    if (item.status == ItemStatus.DORMANT) {
        throw new ConflictException("item already dormant, id=" + itemId);
    }

    logger.info("dormant status check passed, itemId={}", itemId);
}
```

**Step: Add test**
```java
@Test
void checkDormantStatus_validItem_noException() {
    // Given
    Item item = new Item();
    item.id = "test-id";
    item.status = ItemStatus.ACTIVE;
    when(itemRepository.get("test-id")).thenReturn(Optional.of(item));

    // When & Then - no exception thrown
    assertDoesNotThrow(() -> service.checkDormantStatus("test-id"));
}

@Test
void checkDormantStatus_itemNotFound_throwsNotFoundException() {
    // Given
    when(itemRepository.get("non-existent")).thenReturn(Optional.empty());

    // When & Then
    NotFoundException ex = assertThrows(NotFoundException.class,
        () -> service.checkDormantStatus("non-existent"));
    assertTrue(ex.getMessage().contains("item not found"));
}
```

## Error Handling

If implementation encounters issues:

```yaml
issues_encountered:
  - step: 2
    issue: "Method signature conflict with existing overload"
    resolution: "Renamed parameter to avoid conflict"

  - step: 3
    issue: "Missing test dependency for mocking"
    resolution: "Used existing mock framework already in project"
```

## Next Step

After implementation, output:
"Implementation complete. Run /wonder-validator to verify build and tests."
