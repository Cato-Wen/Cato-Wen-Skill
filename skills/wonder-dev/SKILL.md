---
name: wonder-dev
description: One-stop development workflow for Jira tickets. Provide a ticket ID (MD-XXXXX) and this skill orchestrates the full development cycle: analyze requirements, plan implementation, write code, validate, and generate documentation. Combines wonder-analyzer, wonder-planner, wonder-coder, and wonder-validator into a single automated flow.
user-invocable: true
---

# Wonder Development Workflow

End-to-end development automation for Jira tickets.

## Usage

```
/wonder-dev MD-XXXXX
```

## Workflow Overview

```
+------------------------------------------------------------------+
|                    /wonder-dev MD-XXXXX                          |
+------------------------------------------------------------------+
|  Phase 0: GIT SETUP                                              |
|  +- Check working directory is clean (stash if needed)           |
|  +- Fetch latest from remote                                     |
|  +- Checkout master and pull latest                              |
|  +- Create and checkout new branch: MD-XXXXX (from master)       |
+------------------------------------------------------------------+
|  Phase 1: ANALYZE                                                |
|  +- Fetch Jira ticket details                                    |
|  +- Extract business context                                     |
|  +- Locate related code modules                                  |
|  +- Assess complexity & confidence                               |
+------------------------------------------------------------------+
|  Phase 2: PLAN                                                   |
|  +- Deep code analysis                                           |
|  +- Identify reusable patterns                                   |
|  +- Design implementation steps                                  |
|  +- [CHECKPOINT] Present plan for approval                       |
+------------------------------------------------------------------+
|  Phase 3: CODE                                                   |
|  +- Execute steps in order                                       |
|  +- Write production code                                        |
|  +- Write unit tests                                             |
+------------------------------------------------------------------+
|  Phase 4: VALIDATE                                               |
|  +- Run checkstyle                                               |
|  +- Run build                                                    |
|  +- Run tests                                                    |
|  +- Generate review summary                                      |
+------------------------------------------------------------------+
|  Phase 5: DOCUMENTATION                                          |
|  +- Generate English conversation log                            |
|  +- Generate Chinese conversation log                            |
|  +- Record issues encountered for future optimization            |
+------------------------------------------------------------------+
|  Phase 6: QA TEST DOC                                            |
|  +- Generate concise QA test documentation                       |
|  +- Post as Jira comment (with user confirmation)                |
+------------------------------------------------------------------+
```

## Execution Instructions

When user invokes `/wonder-dev MD-XXXXX`:

### Phase 0: GIT SETUP

**MUST execute this phase FIRST before any other work.**

1. **Check Working Directory Status**
   ```bash
   git status --porcelain
   ```
   - If there are uncommitted changes, ask user how to proceed:
     - `stash` - Stash changes and continue
     - `abort` - Stop workflow, let user handle manually

2. **Fetch Latest from Remote**
   ```bash
   git fetch origin
   ```

3. **Checkout Master and Pull Latest**
   ```bash
   git checkout master
   git pull origin master
   ```

4. **Create New Branch from Master**
   ```bash
   git checkout -b MD-XXXXX
   ```
   - Branch name = ticket number (e.g., `MD-17329`)
   - If branch already exists, ask user:
     - `switch` - Switch to existing branch
     - `recreate` - Delete and recreate from master
     - `abort` - Stop workflow

**Output Phase 0 Summary:**
```
==============================================================
PHASE 0: GIT SETUP COMPLETE
==============================================================
Base Branch: master (pulled latest)
New Branch: MD-XXXXX - Created

Proceeding to Phase 1: Analysis...
==============================================================
```

**Error Handling:**
- If uncommitted changes exist: Ask "Found uncommitted changes. Stash them? (stash/abort)"
- If branch already exists: Ask "Branch MD-XXXXX already exists. (switch/recreate/abort)"
- If pull fails (conflicts): Report error and abort, user must resolve manually

---

### Phase 1: ANALYZE

Execute wonder-analyzer logic:

1. **Fetch Jira Ticket**
   - Use mcp__atlassian__getJiraIssue to get: Title, description, Acceptance Criteria, Linked pages

2. **Extract Business Context**
   - Identify business terms (dormant, WSKU, BOM, etc.)
   - Map terms to code locations
   - Reference domain glossary if available

3. **Locate Related Code**
   - By service domain (recipe -> internal-recipe-service)
   - By API endpoint patterns
   - By data model/entity names
   - By git history (commits mentioning ticket)

4. **Assess Complexity**
   - Simple: 1 module, clear reference, no DB changes
   - Medium: 2-3 modules, partial reference
   - Complex: 4+ modules, no reference, DB migration needed

**Output Phase 1 Summary:**
```
==============================================================
PHASE 1: ANALYSIS COMPLETE
==============================================================
Ticket: MD-XXXXX - <summary>
Complexity: <simple|medium|complex>
Confidence: <high|medium|low>

Related Modules:
  - <module-1> - <reason>
  - <module-2> - <reason>

Key Files:
  - <file-path-1>
  - <file-path-2>

Proceeding to Phase 2: Planning...
==============================================================
```

---

### Phase 2: PLAN

Execute wonder-planner logic:

1. **Deep Code Analysis**
   - Read all related code files
   - Understand existing patterns
   - Identify integration points

2. **Identify Reusable Code**
   - Same module utilities
   - Cross-module patterns
   - Framework conventions

3. **Design Implementation Steps**
   - Standard order: Interface -> Domain model -> Service -> Integration -> Unit tests

4. **CHECKPOINT: Present Plan for Approval**
   - ALWAYS pause here and present the plan to user
   - Wait for explicit approval before proceeding

**Output Phase 2 Summary:**
```
==============================================================
PHASE 2: IMPLEMENTATION PLAN
==============================================================
Approach: <high-level description>

Steps:
  1. [modify] <file> - <description>
  2. [modify] <file> - <description>
  3. [new] <file> - <description>
  ...

Reusing Patterns From:
  - <source-file>: <what to reuse>

==============================================================
CHECKPOINT: Please review the plan above.

Reply with:
  - "proceed" or "yes" - Continue to coding
  - "adjust: <feedback>" - Modify the plan
  - "stop" - Abort the workflow
==============================================================
```

**IMPORTANT**: Do NOT proceed to Phase 3 until user explicitly approves.

---

### Phase 3: CODE (After User Approval)

Execute wonder-coder logic:

1. **Pre-Implementation Setup**
   - Read all files to be modified
   - Read reference files for patterns
   - Note existing code style

2. **Execute Steps In Order**
   - Check dependencies are complete
   - Apply changes following style guide
   - Report progress: "[N/M] <description>"

3. **Write Tests**
   - Happy path
   - Edge cases (null, empty, boundary)
   - Error cases (not found, invalid, conflict)
   - Business rule validation

**Progress Output:**
```
==============================================================
PHASE 3: CODING IN PROGRESS
==============================================================
[1/4] Modified ItemStatus.java - Added DORMANT enum
[2/4] Modified ItemService.java - Added checkDormantStatus()
[3/4] Modified ItemServiceTest.java - Added 3 test cases
[4/4] Complete

Proceeding to Phase 4: Validation...
==============================================================
```

---

### Phase 4: VALIDATE

Execute wonder-validator logic:

1. **Run Checkstyle**
   ```bash
   ./gradlew checkstyleMain checkstyleTest
   ```
   - Auto-fix common issues (imports, whitespace, line length)

2. **Run Build**
   ```bash
   ./gradlew build -x test
   ```

3. **Run Tests**
   ```bash
   ./gradlew :backend:<module>:test
   ```

4. **Generate Review Summary**

**Final Output:**
```
==============================================================
PHASE 4: VALIDATION COMPLETE
==============================================================

## Review Summary: MD-XXXXX

### Files Changed
| File | Type | Lines | Description |
|------|------|-------|-------------|
| ... | ... | ... | ... |

### Validation Results
| Check | Status |
|-------|--------|
| Checkstyle | Pass |
| Build | Pass |
| Tests | Pass (N/N) |

### Review Focus Areas
1. [ ] <area-1>
2. [ ] <area-2>

Proceeding to Phase 5: Documentation...
==============================================================
```

---

### Phase 5: DOCUMENTATION

**MUST execute after Phase 4 completes successfully.**

Generate two conversation log files in `openspec/` directory for future analysis and workflow optimization.

#### 5.1 Generate English Conversation Log

Create file: `openspec/MD-XXXXX-conversation-log.md`

**Required sections (in order):**
1. **Session Information**: Tool version, model, working directory, date, total duration
2. **Phase 0: Git Setup**: All git operations and user interactions
3. **Phase 1: Requirements Analysis**: Ticket details, code exploration, analysis results
4. **Phase 2: Implementation Plan**: The plan and user confirmation
5. **Phase 3: Code Implementation**: Code changes with diff snippets
6. **Phase 4: Validation**: Build/test results and any fixes applied
7. **Issues Encountered** (CRITICAL SECTION): Dedicated section documenting ALL issues encountered during execution - see format in 5.3
8. **Lessons Learned**: Bullet points of insights for future workflow improvement
9. **Final Change List**: Files modified/created with descriptions
10. **Next Steps**: Code review, commit, PR, QA verification

#### 5.2 Generate Chinese Conversation Log

Create file: `openspec/MD-XXXXX-conversation-log-zh.md`

**Required sections (in order):**
1. **会话信息**: 工具版本、模型、工作目录、日期、总耗时
2. **Phase 0: Git 设置**: 所有 git 操作和用户交互
3. **Phase 1: 需求分析**: Ticket 详情、代码探索、分析结果
4. **Phase 2: 实现计划**: 计划内容和用户确认
5. **Phase 3: 代码实现**: 代码变更，包含 diff 片段
6. **Phase 4: 验证**: 构建/测试结果以及应用的修复
7. **执行过程中遇到的问题** (关键章节): 专门记录执行过程中遇到的所有问题 - 格式见 5.3
8. **经验教训**: 用于未来工作流改进的要点
9. **最终变更清单**: 修改/创建的文件及描述
10. **后续步骤**: 代码审核、提交、PR、QA 验证

#### 5.3 Issues Encountered Section (CRITICAL)

This is a **dedicated section** in the conversation log that documents ALL issues encountered during execution. This data is essential for analyzing and optimizing the workflow.

**Section Template (English):**
```markdown
## Issues Encountered

This section documents all issues encountered during execution for future workflow optimization.

| Phase | Issue Type | Description | Resolution | Time Impact |
|-------|------------|-------------|------------|-------------|
| 4 | Environment | JAVA_HOME pointed to JDK 17, project requires JDK 21 | Set JAVA_HOME to JDK 21 path | Medium |
| 4 | Compilation | Wrong import: used recipev2.api instead of internalrecipe.api | Changed import statement | Low |
| 4 | Code Style | Method names used underscores, violating checkstyle rules | Renamed to camelCase | Low |
| 4 | Static Analysis | SpotBugs: needless boolean boxing (true vs Boolean.TRUE) | Used Boolean.TRUE/FALSE | Low |

### Issue Categories
- **Environment**: Java version, JAVA_HOME, PATH, dependencies
- **Code Style**: Checkstyle violations, naming conventions, formatting
- **Static Analysis**: SpotBugs, unused imports, type issues
- **Compilation**: Missing imports, wrong class references, syntax errors
- **Test**: Test failures, mock setup issues, assertion errors
- **Git**: Branch conflicts, merge issues, stash problems
- **External**: Jira API, network issues, timeout

### Lessons Learned
- Always verify JAVA_HOME before running gradle commands
- Use Boolean.TRUE/FALSE instead of primitive true/false for wrapper types
- Follow camelCase naming for test methods (no underscores)
```

**Section Template (Chinese):**
```markdown
## 执行过程中遇到的问题

本节记录执行过程中遇到的所有问题，用于未来工作流优化分析。

| 阶段 | 问题类型 | 问题描述 | 解决方案 | 时间影响 |
|------|----------|----------|----------|----------|
| 4 | 环境问题 | JAVA_HOME 指向 JDK 17，项目需要 JDK 21 | 设置 JAVA_HOME 为 JDK 21 路径 | 中 |
| 4 | 编译问题 | 错误的 import：使用了 recipev2.api 而不是 internalrecipe.api | 修改 import 语句 | 低 |
| 4 | 代码风格 | 方法名使用下划线，违反 checkstyle 规则 | 重命名为 camelCase | 低 |
| 4 | 静态分析 | SpotBugs: 不必要的布尔装箱 (true vs Boolean.TRUE) | 使用 Boolean.TRUE/FALSE | 低 |

### 问题分类
- **环境问题**: Java 版本、JAVA_HOME、PATH、依赖
- **代码风格**: Checkstyle 违规、命名规范、格式
- **静态分析**: SpotBugs、未使用的导入、类型问题
- **编译问题**: 缺少导入、错误的类引用、语法错误
- **测试问题**: 测试失败、Mock 设置问题、断言错误
- **Git 问题**: 分支冲突、合并问题、stash 问题
- **外部问题**: Jira API、网络问题、超时

### 经验教训
- 运行 gradle 命令前始终验证 JAVA_HOME
- 对包装类型使用 Boolean.TRUE/FALSE 而不是原始的 true/false
- 测试方法遵循 camelCase 命名（不使用下划线）
```

**Time Impact levels:**
- **High (高)**: Required multiple attempts or significant debugging (>5 min)
- **Medium (中)**: Required one fix iteration (2-5 min)
- **Low (低)**: Quick fix, pattern already known (<2 min)

**Output Phase 5 Summary:**
```
==============================================================
PHASE 5: DOCUMENTATION COMPLETE
==============================================================
Generated:
  - openspec/MD-XXXXX-conversation-log.md (English)
  - openspec/MD-XXXXX-conversation-log-zh.md (Chinese)

Issues Recorded: <N> issues documented for future optimization

Proceeding to Phase 6: QA Test Doc...
==============================================================
```

---

### Phase 6: QA TEST DOC

**MUST execute after Phase 5 completes.**

Generate a concise QA-friendly test documentation summary and post it as a Jira comment.

#### 6.1 Content Requirements

**CRITICAL RULES:**
- 100% English (NO Chinese characters)
- NO title header (do NOT start with "Test Documentation for MD-XXXXX")
- ONLY TWO SECTIONS: 【What Changed】and【Test Suggestions】
- NO code details (no file names, method names, line numbers, technical implementation)
- QA team does NOT care about code changes - keep it business/feature focused
- Use【】brackets for section titles (NOT bold, NOT markdown headers)
- Use numbered lists (1. 2. 3.) NOT # symbols or bullet points
- Test Suggestions = test scenarios ONLY (NO expected results)
- Test Suggestions = 5-10 items MAX
- Keep ENTIRE comment concise (target 150-300 words TOTAL)

#### 6.2 Output Format

```
【What Changed】
[Business-focused summary describing the feature/fix in 2-3 sentences.
Describe WHAT the system now does, not HOW the code was changed.
Include any user-facing messages or behaviors.]

【Test Suggestions】
1. [Test scenario 1 - action only, NO expected result]
2. [Test scenario 2]
3. [Test scenario 3]
...

(From commits: hash1, hash2)
```

#### 6.3 Example Output

```
【What Changed】
Added validation to block activation of dormant 41* WSKU items. When a 41* item is dormant and its parent 40* item is published and active, the system will block the "Mark as Active for Ordering" action and display error message "Unable to mark {item number} as active. It is dormant."

【Test Suggestions】
1. Mark a dormant 41* item as active for ordering when its parent 40* item is active
2. Mark a dormant 41* item as active for ordering when its parent 40* item is also dormant
3. Mark an active 41* item as active for ordering when its parent 40* item is active
4. Mark an R&D 41* item as active for ordering when its parent 40* item is active
5. Verify the error message displays correctly for dormant items

(From commits: 23a1b73777)
```

#### 6.4 Execution Steps

1. **Get commit hashes** for the current branch:
   ```bash
   git log master..HEAD --oneline
   ```

2. **Analyze changes** from the implementation (use info from Phase 3-4)

3. **Generate summary** following the format above

4. **Present to user for review** before posting

5. **Post to Jira** using mcp__atlassian__addCommentToJiraIssue (after user confirmation)

**Output Phase 6 Summary:**
```
==============================================================
PHASE 6: QA TEST DOC COMPLETE
==============================================================
Generated QA test documentation:
  - 【What Changed】: [brief summary]
  - 【Test Suggestions】: <N> scenarios

Posted to Jira: MD-XXXXX
==============================================================
WORKFLOW COMPLETE

All phases completed successfully.
Code is ready for review and commit.
==============================================================
```

---

## Error Handling

### Phase 1 Errors
- If Jira ticket not found: Ask user to provide ticket details manually
- If no related code found: Ask user for hints about affected modules

### Phase 2 Errors
- If unclear requirements: Present questions and wait for clarification
- Do NOT proceed until clarified

### Phase 3 Errors
- If code conflict or compilation issue: Report the issue, suggest resolution, wait for user decision

### Phase 4 Errors
- If checkstyle fails: Auto-fix if possible, re-run; report unfixable issues
- If build fails: Parse error, suggest fix, apply and re-run
- If tests fail: Categorize (test logic vs implementation bug), fix and re-run

### Phase 5 Errors
- If openspec directory does not exist: Create it automatically
- If file write fails: Report error but do not fail the workflow (documentation is supplementary)

### Phase 6 Errors
- If no commits found on branch: Skip QA doc generation, report to user
- If Jira API fails: Save the generated content locally and report error
- If user declines to post: Save content but do not post to Jira

---

## Quick Reference

### Invoke
```
/wonder-dev MD-17329
```

### Checkpoint Responses
- "yes" / "proceed" -> Continue to next phase
- "adjust: <feedback>" -> Revise plan with feedback
- "stop" / "abort" -> Cancel workflow

### Skip Phases (Advanced)
```
/wonder-dev MD-17329 --skip-analysis    # Start from planning
/wonder-dev MD-17329 --skip-validation  # Skip final validation
/wonder-dev MD-17329 --skip-docs        # Skip documentation generation (Phase 5)
/wonder-dev MD-17329 --skip-qa-doc      # Skip QA test doc generation (Phase 6)
```
