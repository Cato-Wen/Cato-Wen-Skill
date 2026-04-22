# Cato-Wen-Skill

Agent skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [OpenCode](https://opencode.ai). Install to `~/.claude/skills/` for global availability across all projects.

## Why This Repo

AI coding agents like Claude Code and OpenCode are powerful, but skills (the specialized instructions that guide them) are hard to manage:

- **Scattered across repos** — You find useful skills on GitHub, but each one has a different install method. Some go in `~/.claude/skills/`, some in `~/.opencode/skills/`, some need `pip install`.
- **No shared directory** — Claude Code and OpenCode each look at their own skills folder. Installing a skill for one doesn't make it available to the other.
- **No auto-update** — After cloning a skill repo, you have to remember to `git pull` periodically. In practice, you forget and end up running outdated skills.
- **Windows is second-class** — Most skill repos document Mac/Linux install steps. Windows users have to figure out symlinks, junctions, and Task Scheduler on their own.

This repo provides two things:

1. **`skill-repo-manager`** — a tool that solves all of the above for Windows users.
2. **Wonder Dev Pipeline** — a set of skills for automating Jira-driven development on the Wonder monorepo.

## Skills

### Skill Repo Manager

| | |
|---|---|
| Skill | `skill-repo-manager` |
| Platform | Windows 10/11 |
| Description | Manage Git-based skill repositories on Windows with auto-update |

#### What problems does it solve?

| Problem | Solution |
|---------|----------|
| Installing a skill repo requires multiple manual steps (clone, find SKILL.md, copy to the right place) | `skill-manager add <url>` does it all in one command |
| Claude Code and OpenCode use different skill directories | Installs to `~/.claude/skills/` which both tools can read |
| Skills go stale because you forget to `git pull` | Windows Scheduled Task auto-syncs daily at 09:00 and on every login |
| Symlinks on Windows need admin/Developer Mode | Uses Junction (no admin required, transparent to all programs) |
| Managing 10+ skill repos becomes a mess | Central registry (`repos.json`) tracks all repos; `skill-manager list` shows health status |
| A skill repo adds new skills after you installed it | `sync` auto-detects and links newly added skills |

#### Typical use cases

**Case 1: You found a cool skill repo on GitHub**
```powershell
skill-manager add https://github.com/kepano/obsidian-skills.git
# Done. 5 skills cloned, linked, and will auto-update forever.
```

**Case 2: You use both Claude Code and OpenCode**

No extra config needed. Both read from `~/.claude/skills/`. Install once, available everywhere.

**Case 3: A skill repo author pushes an update**

You do nothing. The scheduled task runs `git pull` daily. Because skills are linked via Junction (not copied), the update is immediately visible.

**Case 4: You want to see what's installed**
```powershell
skill-manager list
# Shows all repos, their skills, link health, and sync task status.
```

Manage multiple Git skill repos from a single command. Clone, link via Windows Junction, and auto-sync daily through Task Scheduler. Works with both Claude Code and OpenCode.

**Features:**
- `skill-manager add <url>` — clone and link a skill repo in one command
- `skill-manager sync` — pull updates for all registered repos
- `skill-manager list` / `remove` — view or uninstall repos
- Daily auto-sync via Windows Scheduled Task (09:00 + on login)
- Supports multi-skill repos (e.g. `kepano/obsidian-skills`) and single-skill repos
- Junction-based linking — `git pull` changes take effect immediately

**Architecture:**

```
~/.local/share/
├── skill-manager/
│   ├── skill-manager.ps1    # Core script
│   ├── repos.json           # Registry of all repos
│   └── sync.log             # Sync history
└── skill-repos/             # All cloned Git repos

~/.claude/skills/             # Shared by Claude Code + OpenCode
    └── <skill>/  ──Junction──>  skill-repos/<repo>/skills/<skill>
```

---

### Wonder Dev Pipeline

A set of skills for automating development workflows on the Wonder monorepo, powered by Jira integration and Core-NG framework conventions.

```
wonder-analyzer  →  wonder-planner  →  wonder-coder  →  wonder-validator
                        wonder-dev (orchestrates all)
                    wonder-context-finder (code lookup)
```

| Skill | Description |
|-------|-------------|
| `wonder-dev` | One-stop workflow: provide a Jira ticket ID (MD-XXXXX) and it runs the full cycle — analyze, plan, code, validate |
| `wonder-analyzer` | Fetch Jira ticket, extract business context, locate related code modules, assess complexity |
| `wonder-planner` | Deep code analysis, identify reusable patterns, design step-by-step implementation plan |
| `wonder-coder` | Execute plan, write production code and tests following Core-NG conventions |
| `wonder-validator` | Run checkstyle, build, tests; auto-fix issues; generate review summary for tech lead |
| `wonder-context-finder` | Map business terms (MS Cards, WSKU, BOM, etc.) to code locations in the monorepo |

## Installation

### Option 1: Using skill-repo-manager (recommended)

If you already have `skill-repo-manager` installed:

```powershell
skill-manager add https://github.com/Cato-Wen/Cato-Wen-Skill.git
```

This clones the repo and links all skills into `~/.claude/skills/` via Junction. Updates are handled automatically by the daily sync task.

### Option 2: Manual

Clone into a local directory and create Junctions manually:

```powershell
git clone https://github.com/Cato-Wen/Cato-Wen-Skill.git "%USERPROFILE%\.local\share\skill-repos\Cato-Wen-Skill"

# Link each skill
cd %USERPROFILE%\.claude\skills
mklink /J skill-repo-manager "%USERPROFILE%\.local\share\skill-repos\Cato-Wen-Skill\skills\skill-repo-manager"
mklink /J wonder-dev "%USERPROFILE%\.local\share\skill-repos\Cato-Wen-Skill\skills\wonder-dev"
# ... repeat for other skills
```

### Option 3: Direct copy

Copy the `skills/` contents directly into `~/.claude/skills/`:

```powershell
xcopy /E /I skills\* "%USERPROFILE%\.claude\skills\"
```

> Note: Direct copy does not support auto-update. You will need to manually pull and copy again to get updates.

## Requirements

- Windows 10/11
- Git
- PowerShell 5.1+
- For Wonder skills: Atlassian MCP tools configured for Jira/Confluence access

## License

MIT
