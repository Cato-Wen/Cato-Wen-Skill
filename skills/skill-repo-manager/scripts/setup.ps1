<#
.SYNOPSIS
    One-click setup for skill-repo-manager on Windows.
    Copies skill-manager.ps1 to persistent location, registers PowerShell alias, and installs daily sync task.
#>
param(
    [switch]$SkipTask,
    [switch]$SkipAlias
)

$ErrorActionPreference = "Stop"

$ManagerDir = Join-Path $env:USERPROFILE ".local\share\skill-manager"
$ScriptSrc  = Join-Path $PSScriptRoot "skill-manager.ps1"
$ScriptDst  = Join-Path $ManagerDir "skill-manager.ps1"

# --- 1. Copy script to persistent location ---
New-Item -ItemType Directory -Path $ManagerDir -Force | Out-Null
Copy-Item -Path $ScriptSrc -Destination $ScriptDst -Force
Write-Host "[OK] skill-manager.ps1 -> $ScriptDst" -ForegroundColor Green

# --- 2. Register PowerShell alias ---
if (-not $SkipAlias) {
    $profilePath = $PROFILE.CurrentUserAllHosts
    $aliasBlock = @'

# Skill Repo Manager
function skill-manager {
    & powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.local\share\skill-manager\skill-manager.ps1" @args
}
'@
    if (-not (Test-Path $profilePath)) {
        New-Item -ItemType File -Path $profilePath -Force | Out-Null
    }
    $content = Get-Content $profilePath -Raw -ErrorAction SilentlyContinue
    if ($content -and $content.Contains("function skill-manager")) {
        Write-Host "[OK] PowerShell alias already exists, skipped" -ForegroundColor Yellow
    } else {
        Add-Content -Path $profilePath -Value $aliasBlock -Encoding UTF8
        Write-Host "[OK] Added 'skill-manager' function to $profilePath" -ForegroundColor Green
    }
}

# --- 3. Install daily sync scheduled task ---
if (-not $SkipTask) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $ScriptDst install-task
}

Write-Host ""
Write-Host "Setup complete. Restart your terminal, then run:" -ForegroundColor Cyan
Write-Host "  skill-manager help" -ForegroundColor White
Write-Host "  skill-manager add https://github.com/kepano/obsidian-skills.git" -ForegroundColor White
Write-Host ""
