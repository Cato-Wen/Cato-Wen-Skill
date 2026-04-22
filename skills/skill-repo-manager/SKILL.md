---
name: skill-repo-manager
description: Manage Git-based agent skill repositories on Windows with auto-update. Use when the user wants to install, update, remove, or sync skill repos for Claude Code or OpenCode. Handles git clone, Windows Junction linking to ~/.claude/skills/, scheduled daily sync via Task Scheduler, and supports both multi-skill repos (like kepano/obsidian-skills) and single-skill repos. Triggers on "install skill repo", "add skills from GitHub", "auto-update skills", "sync skills", "manage skill repos".
---

# Skill Repo Manager

Manage Git-based skill repositories on Windows. Clone repos, link skills into `~/.claude/skills/` via Junction, and auto-sync daily.

## Architecture

```
~/.local/share/
├── skill-manager/
│   ├── skill-manager.ps1    # Core script
│   ├── repos.json           # Registry of all repos
│   └── sync.log             # Sync history
└── skill-repos/             # All cloned Git repos
    └── <repo-name>/

~/.claude/skills/             # Shared by Claude Code + OpenCode
    └── <skill-name>/  --Junction-->  skill-repos/<repo>/skills/<skill>
```

## Prerequisites

- Windows 10/11
- Git installed and in PATH
- PowerShell 5.1+

## First-time Setup

Run the setup script bundled with this skill:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts/setup.ps1"
```

The path above is relative to this skill's directory. Resolve the absolute path before execution.

Setup performs three actions:
1. Copy `skill-manager.ps1` to `~/.local/share/skill-manager/`
2. Add `skill-manager` function to PowerShell profile
3. Register `SkillManagerDailySync` scheduled task (daily 09:00 + on login)

After setup, instruct the user to restart their terminal.

## Commands

### Add a skill repo

```powershell
# Multi-skill repo (skills in a "skills/" subdirectory)
skill-manager add https://github.com/kepano/obsidian-skills.git

# Custom subdirectory
skill-manager add https://github.com/user/repo.git -SkillsSubdir src/skills

# Single-skill repo (SKILL.md at repo root)
skill-manager add https://github.com/user/my-skill.git -SkillsSubdir "."
```

What `add` does:
1. `git clone` to `~/.local/share/skill-repos/<name>/`
2. Scan for directories containing `SKILL.md`
3. Create Windows Junction for each skill in `~/.claude/skills/`
4. Save repo metadata to `repos.json`

### Sync all repos

```powershell
skill-manager sync
```

Run `git pull` on every registered repo. Auto-create Junctions for any newly added skills.

### List registered repos

```powershell
skill-manager list
```

### Remove a repo

```powershell
skill-manager remove <repo-name>
```

Remove all Junctions, delete the cloned repo, and unregister from config.

### Manage scheduled task

```powershell
skill-manager install-task     # Register daily auto-sync
skill-manager uninstall-task   # Remove scheduled task
```

## Auto-Update Details

The scheduled task `SkillManagerDailySync` runs `skill-manager sync -Quiet`:
- Trigger: Daily at 09:00 + every Windows login
- Runs only when network is available
- Runs on battery power
- Catches up missed runs after sleep/shutdown
- Log: `~/.local/share/skill-manager/sync.log`

Junction links mean `git pull` changes are immediately visible without copying.

## Key Design Decisions

- **Junction over Symlink**: No admin privileges or Developer Mode required on Windows.
- **`~/.claude/skills/` as target**: Claude Code's global skill directory. OpenCode shares it.
- **Git clone as source**: Full repo enables `git pull`, `git log`, offline access.
- **Single-skill detection**: When no `skills/` subdirectory is found, auto-checks repo root for `SKILL.md`.

## Flags

| Flag | Description |
|------|-------------|
| `-SkillsSubdir <dir>` | Subdirectory containing skills (default: `skills`) |
| `-Force` | Overwrite existing non-Junction directories |
| `-Quiet` | Suppress console output, log only |
