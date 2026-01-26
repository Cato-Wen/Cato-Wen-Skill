---
name: wonder-context-finder
description: Find relevant Wonder monorepo code based on business requirements. Use when developer asks about MS Cards (MS05-xx, MS06-xx, MS08-xx, MS13-xx, MS15-xx), Jira tickets (MD-XXXXX), business concepts (dormant, 40-model, WSKU, ERP sync, hot hold, pack size, BOM, version, item type), or needs to understand which code implements a requirement. Searches requirement docs, git history, Jira/Confluence, and maps business terms to code locations.
---

# Wonder Business Context Code Finder

Help developers navigate the Wonder monorepo by connecting business requirements to code.

## Quick Reference

**Project**: Wonder monorepo (run skills from project root directory)
**Jira Ticket Format**: `MD-[5-digit number]` (e.g., MD-17329)
**MS Card Format**: `MSxx-yy` (e.g., MS05-16, MS06-01)

## Query Type Identification

When a developer asks about business functionality, identify the query type:

| Query Pattern | Type | Action |
|--------------|------|--------|
| `MS05-xx`, `MS06-xx`, etc. | MS Card | Search `references/ms-cards/index.md` |
| `MD-XXXXX` | Jira Ticket | Run git search + Jira MCP lookup |
| Business term (dormant, WSKU, BOM, etc.) | Concept | Consult `references/domain-glossary.md` |
| Service/module question | Architecture | Consult `references/module-map.md` |

## Workflows

### 1. MS Card Query
```
1. Search references/ms-cards/index.md for card ID
2. Read full card from references/ms-cards/cards/MSxx-yy.md
3. Identify related Jira tickets mentioned
4. Search git for those tickets
5. Present: Card summary, related tickets, affected code files
```

### 2. Jira Ticket Query (MD-XXXXX)
```
1. Search git history (run from project root):
   git log --all --oneline --grep="MD-XXXXX"

2. Get changed files for relevant commits:
   git diff-tree --no-commit-id --name-only -r <commit-hash>

3. Fetch Jira details via MCP:
   mcp__atlassian__getJiraIssue(cloudId="wonder.atlassian.net", issueIdOrKey="MD-XXXXX")

4. Search Confluence:
   mcp__atlassian__search(query="MD-XXXXX")

5. Present: Ticket summary, commits, changed files, related docs
```

### 3. Business Concept Query
```
1. Consult references/domain-glossary.md for term mapping
2. Get code patterns and locations
3. Search codebase (run from project root): rg -i "pattern" backend
4. Reference references/module-map.md for service context
5. Present: Concept explanation, code locations, related services
```

## Domain Quick Reference

### Object Types (NewObjectType enum)
Located: `backend/domain-library/src/main/java/app/internalrecipe/item/innerclassview/NewObjectType.java`

| Type | Description |
|------|-------------|
| MENU | Menu items |
| PACKAGED | Packaged products |
| RECIPE | Recipe items |
| BENCHTOP | Benchtop recipes |
| BY_PRODUCT | By-products |
| HDR_RECIPE | HDR recipes |
| NON_FOOD | Non-food items |
| INGREDIENT | Ingredients |
| ORIGINAL | Original items |
| ORIGINAL_SUBRECIPE | Original subrecipes |
| WSKU | Wonder SKU items |
| HDR_CONSUMABLE_ITEM | HDR consumable items |

### Common Business Terms
See `references/domain-glossary.md` for full mappings:
- **40-Model**: Schedule 40 production model items
- **WSKU**: Wonder SKU - specific item identifier
- **Dormant**: Inactive items pending reactivation
- **ERP Sync**: Enterprise Resource Planning synchronization
- **Hot Hold**: Temperature holding requirements
- **Pack Size**: Product packaging sizes
- **BOM**: Bill of Materials

## Using Atlassian MCP Tools

### Fetch Jira Issue
```
mcp__atlassian__getJiraIssue(
  cloudId="wonder.atlassian.net",
  issueIdOrKey="MD-17329"
)
```

### Search Jira/Confluence
```
mcp__atlassian__search(query="dormant workflow")
```

### Search with JQL
```
mcp__atlassian__searchJiraIssuesUsingJql(
  cloudId="wonder.atlassian.net",
  jql="project = MD AND text ~ 'dormant'"
)
```

## Git Commands for Code Discovery

All commands should be run from the project root directory.

### Search commits by ticket
```bash
git log --all --oneline --grep="MD-17329"
```

### Get files changed in commit
```bash
git diff-tree --no-commit-id --name-only -r <commit-hash>
```

### Search commits by keyword
```bash
git log --all --oneline --grep="dormant"
```

## Reference Files

- **Domain Glossary**: `references/domain-glossary.md` - Business terms to code mappings
- **Module Map**: `references/module-map.md` - Service responsibilities and packages
- **Codebase Overview**: `references/codebase/overview.md` - Project structure summary
- **MS Cards Index**: `references/ms-cards/index.md` - Requirement card summaries
- **Source Documents**: `assets/source-docs/` - Original Word documents for complete MS Card details
  - `034-Master Data V2.0 Use Cases-1.docx`
  - `034-Master Data V2.0 Use Cases-2.docx`
