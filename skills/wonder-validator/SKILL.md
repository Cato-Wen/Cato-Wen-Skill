---
name: wonder-validator
description: Validate code quality and generate review summary. Use after wonder-coder to run checkstyle, build, and tests. Generates a comprehensive review summary for the tech lead to review.
user-invocable: true
---

# Wonder Code Validator

Validate implemented code and generate review summary.

## Input

Expects context from `wonder-coder`:
- List of modified/created files
- Ticket ID
- Implementation summary

Or can be run standalone on current changes.

## Workflow

### Step 1: Identify Changed Files

```bash
# Get list of changed files (run from project root)
git status --porcelain

# Or if files known from previous step, use those
```

### Step 2: Run Checkstyle

```bash
# Run checkstyle for affected modules
./gradlew checkstyleMain checkstyleTest

# Or for specific module
./gradlew :backend:<module-name>:checkstyleMain
```

**On Checkstyle Failure:**
```
1. Parse error output to identify issues
2. Auto-fix common issues:
   - Missing whitespace
   - Line length
   - Import order
   - Trailing whitespace
3. Re-run checkstyle
4. If still failing, report unfixable issues
```

**Common Checkstyle Fixes:**
```java
// Line too long (>120 chars) - break at logical points
String longMessage = "This is a very long message that needs to "
    + "be broken into multiple lines";

// Import order - follow project convention
import core.*;
import app.*;
import java.*;

// Missing whitespace
if (condition) {  // NOT: if(condition){
    doSomething();
}
```

### Step 3: Run Build

```bash
# Build without tests first (faster feedback)
./gradlew build -x test

# Or for specific module
./gradlew :backend:<module-name>:build -x test
```

**On Build Failure:**
```
1. Parse compiler errors
2. Common fixes:
   - Missing imports
   - Type mismatches
   - Missing method implementations
3. Apply fixes and re-run
4. If unfixable, report with context
```

### Step 4: Run Tests

```bash
# Run tests for affected module
./gradlew :backend:<module-name>:test

# Run specific test class
./gradlew :backend:<module-name>:test --tests "*ItemServiceTest"
```

**On Test Failure:**
```
1. Parse test output for failure details
2. Categorize failure:
   - Test logic error → fix test
   - Implementation bug → fix implementation
   - Environment issue → report
3. Apply fix and re-run
4. If unfixable, report with details
```

### Step 5: Generate Review Summary

Output a comprehensive review summary:

```markdown
## Review Summary: MD-XXXXX

### Overview
- **Ticket**: MD-XXXXX - <ticket summary>
- **Modules**: <affected modules>
- **Files Changed**: <count>

### File Changes

| File | Type | Lines +/- | Description |
|------|------|-----------|-------------|
| ItemStatus.java | Modified | +3/-0 | Added DORMANT enum |
| ItemService.java | Modified | +22/-0 | Added checkDormantStatus() |
| ItemServiceTest.java | Modified | +38/-0 | Added 3 test cases |

### Key Implementation Details

**1. ItemStatus.java**
- Added `DORMANT` to status enum
- No breaking changes to existing code

**2. ItemService.java**
- New method: `checkDormantStatus(String itemId)`
- Validation: null check, existence check, status check
- Exceptions: BadRequestException, NotFoundException, ConflictException
- Pattern: Follows StatusValidator.java style

**3. ItemServiceTest.java**
- Test cases added:
  - `testCheckDormantStatus_validItem` - happy path
  - `testCheckDormantStatus_notFound` - error case
  - `testCheckDormantStatus_alreadyDormant` - conflict case

### Validation Results

| Check | Status | Details |
|-------|--------|---------|
| Checkstyle | ✅ Pass | No violations |
| Build | ✅ Pass | Compiled successfully |
| Unit Tests | ✅ Pass | 3/3 tests passed |

### Review Recommendations

**Suggested Focus Areas:**
1. [ ] Verify dormant status logic matches business requirements
2. [ ] Check exception messages are clear for API consumers
3. [ ] Confirm test coverage is sufficient

**Potential Concerns:**
- None identified

### Code Quality Notes

- ✅ Follows existing code patterns
- ✅ Uses project conventions for naming
- ✅ Proper exception handling
- ✅ Adequate test coverage
- ✅ No new dependencies added
```

## Validation Result Handling

### All Checks Pass
```
✅ All validations passed!

Review Summary generated above.
Ready for code review.
```

### Some Checks Fail (Auto-fixed)
```
⚠️ Issues found and auto-fixed:

Checkstyle:
- Fixed import order in ItemService.java
- Fixed line length in ItemServiceTest.java

Re-running validation...

✅ All validations now pass!
```

### Some Checks Fail (Cannot Auto-fix)
```
❌ Validation failed:

Build Error:
- ItemService.java:45 - cannot find symbol: class ItemStatus
- Likely cause: Missing import or enum not yet committed

Recommended Action:
1. Check if ItemStatus.java changes are saved
2. Verify import statement exists
3. Re-run /wonder-validator

Would you like me to investigate and fix?
```

## Standalone Usage

Can be run without prior skills to validate any current changes:

```
User: /wonder-validator

Output:
1. Detects changed files via git status
2. Runs all validation steps
3. Generates summary of current changes
```

## Module Detection

Automatically detect affected modules from changed files:

```
Changed file path → Module mapping:
backend/master-data-service/... → :backend:master-data-service
backend/master-data-interface/... → :backend:master-data-interface
frontend/recipe-site/... → :frontend:recipe-site
```

## Commands Reference

```bash
# Full build
./gradlew build

# Build specific module
./gradlew :backend:master-data-service:build

# Checkstyle
./gradlew checkstyleMain checkstyleTest

# Tests
./gradlew test
./gradlew :backend:master-data-service:test

# Single test class
./gradlew :backend:master-data-service:test --tests "*ItemServiceTest"

# Clean build
./gradlew clean build
```

## Output Format

Final output structure:

```yaml
validation_complete: true
ticket_id: "MD-XXXXX"

checks:
  checkstyle:
    status: "pass" | "fail" | "fixed"
    issues_found: <number>
    issues_fixed: <number>
    remaining_issues: []

  build:
    status: "pass" | "fail" | "fixed"
    errors: []

  tests:
    status: "pass" | "fail"
    total: <number>
    passed: <number>
    failed: <number>
    failed_tests: []

files_summary:
  total_changed: <number>
  lines_added: <number>
  lines_removed: <number>

review_summary: |
  <markdown review summary>

ready_for_review: true | false
blockers: []  # Any issues preventing review
```

## Next Step

After successful validation:
"Validation complete. Code is ready for your review.

Review the summary above and check the implementation.
When satisfied, you can commit the changes."
