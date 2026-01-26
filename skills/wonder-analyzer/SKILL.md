---
name: wonder-analyzer
description: Analyze Jira requirements and locate relevant code. Use when starting a new development task with a Jira ticket ID (MD-XXXXX). Fetches ticket details, extracts business context, and identifies related code modules, existing implementations, and reusable patterns.
user-invocable: true
---

# Wonder Requirement Analyzer

Analyze Jira tickets and locate relevant code for implementation.

## Input

Jira Ticket ID: `MD-XXXXX` (e.g., MD-17329)

## Workflow

### Step 1: Fetch Jira Ticket

```
1. Use Atlassian MCP to get ticket details:
   - Title and description
   - Acceptance Criteria (AC)
   - Linked Confluence pages
   - Related/linked tickets

2. If MCP unavailable, ask user to paste ticket content
```

### Step 2: Extract Business Context

```
1. Identify business terms from ticket (dormant, hot hold, BOM, WSKU, etc.)
2. Search local docs for context:
   - skills/wonder-analyzer/glossary.md (bundled with this skill)
   - docs/business/*.md (if exists in project)
3. Use wonder-context-finder skill references if available
4. Note: Local docs may be outdated - always verify against code
```

### Step 3: Locate Related Code

Use multiple strategies based on requirement type:

**Strategy A: By Service Domain**
```
Requirement mentions → Service module
- recipe/menu → backend/internal-recipe-service, backend/recipe-service-v2
- product/catalog → backend/product-catalog-*
- master data/item → backend/master-data-*
- sync/migration → backend/*-migration
```

**Strategy B: By API Endpoint**
```bash
# Search for API patterns (run from project root)
rg -i "endpoint|path|route" backend --glob "*.java" | grep -i "<keyword>"
```

**Strategy C: By Data Model**
```bash
# Find entity/domain classes (run from project root)
rg -l "class.*<EntityName>" backend --glob "*.java"
```

**Strategy D: By Similar Feature**
```bash
# Search for similar implementations (run from project root)
git log --all --oneline --grep="<similar-feature>"
```

### Step 4: Assess Complexity

| Factor | Simple | Medium | Complex |
|--------|--------|--------|---------|
| Modules affected | 1 | 2-3 | 4+ |
| Has clear reference | Yes | Partial | No |
| DB changes needed | No | Schema only | Migration |
| New API needed | No | Extend existing | New endpoint |

**Confidence Assessment:**
- HIGH: Clear requirements + existing patterns to follow
- MEDIUM: Some ambiguity but solvable
- LOW: Unclear requirements or significant architectural decisions

### Step 5: Generate Output

Output format:
```yaml
ticket_id: "MD-XXXXX"
ticket_summary: "<one-line summary>"
complexity: "simple|medium|complex"
confidence: "high|medium|low"
execution_mode: "auto|confirm_first"

business_context:
  terms:
    - term: "<business term>"
      definition: "<what it means>"
      code_location: "<where in code>"

related_modules:
  - module: "<module path>"
    reason: "<why relevant>"

related_code:
  - path: "<file path>"
    purpose: "<what this file does>"
    relevance: "<how it relates to the requirement>"

reusable_patterns:
  - path: "<file path>"
    pattern: "<what can be reused>"
    usage: "<how to apply it>"

questions: []  # List any clarification questions
```

## Decision Logic for Execution Mode

```
IF confidence == "high" AND complexity == "simple":
    execution_mode = "auto"
ELSE IF confidence == "low" OR has_questions:
    execution_mode = "confirm_first"
    # Present analysis and wait for user confirmation
ELSE:
    execution_mode = "confirm_first"
```

## Example Usage

User: `/wonder-analyzer MD-17329`

Output:
```yaml
ticket_id: "MD-17329"
ticket_summary: "Add dormant status check for items"
complexity: "medium"
confidence: "high"
execution_mode: "auto"

business_context:
  terms:
    - term: "dormant"
      definition: "Items inactive for extended period"
      code_location: "ItemStatus enum in master-data-interface"

related_modules:
  - module: "backend/master-data-interface"
    reason: "Status enum definitions"
  - module: "backend/master-data-service"
    reason: "Item business logic"

related_code:
  - path: "backend/master-data-service/src/.../ItemService.java"
    purpose: "Core item operations"
    relevance: "Add dormant check method here"

reusable_patterns:
  - path: "backend/product-catalog-service/src/.../StatusValidator.java"
    pattern: "Status validation pattern"
    usage: "Follow same structure for dormant validation"

questions: []
```

## Next Step

After analysis, suggest:
- If `execution_mode: "auto"` → "Ready to proceed. Run /wonder-planner to create implementation plan."
- If `execution_mode: "confirm_first"` → Present findings and ask user to confirm or clarify before proceeding.
