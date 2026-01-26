# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains Claude Code custom skills for automating development workflows on the "Wonder" monorepo. These skills are designed to be installed globally at `~/.claude/skills/` and used across different project directories.

**Usage**: Users should run these skills from within their Wonder project directory. All commands use relative paths assuming the current working directory is the project root.

## Skills Architecture

The skills form a development pipeline that can be run individually or orchestrated together:

```
/wonder-analyzer  →  /wonder-planner  →  /wonder-coder  →  /wonder-validator
       ↓                                                         ↓
  Analyze Jira ticket         Plan → Code → Validate         Generate review summary
  Locate related code
  Assess complexity

                    /wonder-dev (orchestrates all phases)
```

### Skill Definitions

Each skill is defined in `skills/<skill-name>/SKILL.md` with YAML frontmatter:
```yaml
---
name: skill-name
description: When to use this skill
user-invocable: true  # Can be called directly with /skill-name
---
```

### Skill Workflow

1. **wonder-analyzer**: Fetches Jira ticket, extracts business context, locates related code modules, assesses complexity/confidence
2. **wonder-planner**: Deep code analysis, identifies reusable patterns, designs implementation steps, requires user approval checkpoint
3. **wonder-coder**: Executes plan steps, writes code following Core-NG conventions, writes tests
4. **wonder-validator**: Runs checkstyle/build/tests, auto-fixes issues, generates review summary
5. **wonder-dev**: End-to-end orchestration including git branch setup and documentation generation
6. **wonder-context-finder**: Maps business terms (MS Cards, domain concepts) to code locations

## Skill Reference Data

The `wonder-context-finder` skill includes reference documents in its own directory:
- `skills/wonder-context-finder/references/domain-glossary.md` - Business terms to code mappings
- `skills/wonder-context-finder/references/ms-cards/` - MS Card requirement documents

These are skill-bundled resources, not project files.

## Code Conventions (Core-NG Framework)

The skills enforce these patterns when generating code:
- Import order: `core.*`, `app.*`, `java.*`, `javax.*`, `org.*`
- Exceptions: `BadRequestException` (400), `NotFoundException` (404), `ConflictException` (409)
- Logging: `logger.info("action, field={}", value)`
- Test naming: `test<Method>_<scenario>_<expectedResult>`

## Quality Constraints

- Max file length: 450 lines (create new Service class if exceeded)
- Max method length: 50 lines
- Max nested loops: 1 level (use Stream API)
- No database queries in loops

## Atlassian Integration

The skills use Atlassian MCP tools for Jira/Confluence access:
- Jira ticket lookup: `mcp__atlassian__getJiraIssue`
- Unified search: `mcp__atlassian__search`
- JQL queries: `mcp__atlassian__searchJiraIssuesUsingJql`
- Add comments: `mcp__atlassian__addCommentToJiraIssue`