<#
.SYNOPSIS
    Skill 仓库管理器 - 自动克隆、同步、链接 agent skill 仓库到 Claude Code / OpenCode
.DESCRIPTION
    管理多个 Git skill 仓库，通过 Junction 链接到 ~/.claude/skills/
    支持 add / remove / list / sync / install-task / uninstall-task 子命令
.EXAMPLE
    skill-manager add https://github.com/kepano/obsidian-skills.git
    skill-manager sync
    skill-manager list
    skill-manager remove obsidian-skills
    skill-manager install-task   # 注册每日自动同步定时任务
    skill-manager uninstall-task # 移除定时任务
#>

param(
    [Parameter(Position = 0)]
    [ValidateSet("add", "remove", "list", "sync", "install-task", "uninstall-task", "help")]
    [string]$Command = "help",

    [Parameter(Position = 1)]
    [string]$Argument,

    [Parameter()]
    [string]$SkillsSubdir = "skills",

    [Parameter()]
    [switch]$Force,

    [Parameter()]
    [switch]$Quiet
)

# ─── 路径配置 ───
$ManagerDir   = Join-Path $env:USERPROFILE ".local\share\skill-manager"
$ReposDir     = Join-Path $env:USERPROFILE ".local\share\skill-repos"
$ConfigFile   = Join-Path $ManagerDir "repos.json"
$LogFile      = Join-Path $ManagerDir "sync.log"
$SkillTarget  = Join-Path $env:USERPROFILE ".claude\skills"
$TaskName     = "SkillManagerDailySync"

# ─── 工具函数 ───
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp] [$Level] $Message"
    Add-Content -Path $LogFile -Value $line -ErrorAction SilentlyContinue
    if (-not $Quiet) {
        switch ($Level) {
            "ERROR" { Write-Host $line -ForegroundColor Red }
            "WARN"  { Write-Host $line -ForegroundColor Yellow }
            "OK"    { Write-Host $line -ForegroundColor Green }
            default { Write-Host $line }
        }
    }
}

function Load-Config {
    if (-not (Test-Path $ConfigFile)) {
        $default = @{ repos = @() } | ConvertTo-Json -Depth 5
        New-Item -ItemType Directory -Path $ManagerDir -Force | Out-Null
        Set-Content -Path $ConfigFile -Value $default -Encoding UTF8
    }
    return (Get-Content $ConfigFile -Raw | ConvertFrom-Json)
}

function Save-Config {
    param($Config)
    $Config | ConvertTo-Json -Depth 5 | Set-Content -Path $ConfigFile -Encoding UTF8
}

function Get-RepoName {
    param([string]$Url)
    # 从 URL 提取仓库名: https://github.com/user/repo.git -> repo
    $name = ($Url -replace '\.git$', '') -replace '.+/', ''
    return $name
}

function Get-SkillDirs {
    param([string]$RepoPath, [string]$SubDir)
    $skillsRoot = if ($SubDir) { Join-Path $RepoPath $SubDir } else { $RepoPath }
    if (-not (Test-Path $skillsRoot)) { return @() }

    # 查找所有包含 SKILL.md 的目录
    $dirs = Get-ChildItem -Path $skillsRoot -Directory | Where-Object {
        Test-Path (Join-Path $_.FullName "SKILL.md")
    }
    return $dirs
}

# ─── 命令实现 ───

function Invoke-Add {
    param([string]$Url)
    if (-not $Url) {
        Write-Host "用法: skill-manager add <git-repo-url> [-SkillsSubdir <subdir>]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "示例:" -ForegroundColor Cyan
        Write-Host "  skill-manager add https://github.com/kepano/obsidian-skills.git"
        Write-Host "  skill-manager add https://github.com/user/my-skills.git -SkillsSubdir src/skills"
        Write-Host "  skill-manager add https://github.com/user/single-skill.git -SkillsSubdir '.'"
        return
    }

    $config = Load-Config
    $name = Get-RepoName $Url

    # 检查是否已存在
    $existing = $config.repos | Where-Object { $_.name -eq $name }
    if ($existing -and -not $Force) {
        Write-Log "仓库 '$name' 已存在，使用 -Force 强制覆盖" "WARN"
        return
    }

    # 克隆仓库
    $repoPath = Join-Path $ReposDir $name
    New-Item -ItemType Directory -Path $ReposDir -Force | Out-Null

    if (Test-Path $repoPath) {
        Write-Log "更新已有仓库 $name ..." "INFO"
        git -C $repoPath pull --ff-only 2>&1 | ForEach-Object { Write-Log $_ }
    } else {
        Write-Log "克隆仓库 $Url ..." "INFO"
        git clone $Url $repoPath 2>&1 | ForEach-Object { Write-Log $_ }
        if ($LASTEXITCODE -ne 0) {
            Write-Log "克隆失败!" "ERROR"
            return
        }
    }

    # 查找并链接 skills
    $skillDirs = Get-SkillDirs -RepoPath $repoPath -SubDir $SkillsSubdir
    if ($skillDirs.Count -eq 0) {
        Write-Log "警告: 在 $repoPath/$SkillsSubdir 下未找到包含 SKILL.md 的目录" "WARN"
        # 检查根目录是否有 SKILL.md（单 skill 仓库）
        if (Test-Path (Join-Path $repoPath "SKILL.md")) {
            Write-Log "检测到单 skill 仓库，将整个仓库作为一个 skill 链接" "INFO"
            $SkillsSubdir = "."
            $skillDirs = @(Get-Item $repoPath)
        } else {
            Write-Log "也未在仓库根目录找到 SKILL.md，请检查 -SkillsSubdir 参数" "ERROR"
            return
        }
    }

    # 创建 Junctions
    $linkedSkills = @()
    foreach ($dir in $skillDirs) {
        $linkPath = Join-Path $SkillTarget $dir.Name
        if (Test-Path $linkPath) {
            $item = Get-Item $linkPath
            if ($item.Attributes -match 'ReparsePoint') {
                # 已有 junction，先删除
                cmd /c "rmdir `"$linkPath`"" 2>$null
            } else {
                if (-not $Force) {
                    Write-Log "跳过 $($dir.Name): 已存在且非 Junction，使用 -Force 覆盖" "WARN"
                    continue
                }
                Remove-Item -Path $linkPath -Recurse -Force
            }
        }
        cmd /c "mklink /J `"$linkPath`" `"$($dir.FullName)`"" | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Log "  链接: $($dir.Name) -> $($dir.FullName)" "OK"
            $linkedSkills += $dir.Name
        } else {
            Write-Log "  链接失败: $($dir.Name)" "ERROR"
        }
    }

    # 更新配置
    $entry = [PSCustomObject]@{
        name          = $name
        url           = $Url
        skills_subdir = $SkillsSubdir
        enabled       = $true
        skills        = $linkedSkills
        added_at      = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    }

    if ($existing) {
        $config.repos = @($config.repos | Where-Object { $_.name -ne $name }) + $entry
    } else {
        $config.repos = @($config.repos) + $entry
    }
    Save-Config $config

    Write-Log "完成! 已链接 $($linkedSkills.Count) 个 skill: $($linkedSkills -join ', ')" "OK"
}

function Invoke-Remove {
    param([string]$Name)
    if (-not $Name) {
        Write-Host "用法: skill-manager remove <repo-name>" -ForegroundColor Yellow
        return
    }

    $config = Load-Config
    $repo = $config.repos | Where-Object { $_.name -eq $Name }
    if (-not $repo) {
        Write-Log "未找到仓库: $Name" "ERROR"
        return
    }

    # 删除 junctions
    foreach ($skill in $repo.skills) {
        $linkPath = Join-Path $SkillTarget $skill
        if (Test-Path $linkPath) {
            $item = Get-Item $linkPath
            if ($item.Attributes -match 'ReparsePoint') {
                cmd /c "rmdir `"$linkPath`"" 2>$null
                Write-Log "  移除链接: $skill" "OK"
            } else {
                Write-Log "  跳过 $skill (非 Junction，不自动删除)" "WARN"
            }
        }
    }

    # 删除克隆的仓库
    $repoPath = Join-Path $ReposDir $Name
    if (Test-Path $repoPath) {
        Remove-Item -Path $repoPath -Recurse -Force
        Write-Log "  移除仓库目录: $repoPath" "OK"
    }

    # 更新配置
    $config.repos = @($config.repos | Where-Object { $_.name -ne $Name })
    Save-Config $config

    Write-Log "已完全移除 $Name" "OK"
}

function Invoke-List {
    $config = Load-Config
    if ($config.repos.Count -eq 0) {
        Write-Host "当前没有管理任何 skill 仓库" -ForegroundColor Yellow
        Write-Host "使用 'skill-manager add <url>' 添加" -ForegroundColor Cyan
        return
    }

    Write-Host ""
    Write-Host "  Skill 仓库管理器 - 已注册仓库" -ForegroundColor Cyan
    Write-Host "  $('=' * 50)" -ForegroundColor DarkGray

    foreach ($repo in $config.repos) {
        $status = if ($repo.enabled) { "[ON]" } else { "[OFF]" }
        $color = if ($repo.enabled) { "Green" } else { "DarkGray" }
        Write-Host ""
        Write-Host "  $status $($repo.name)" -ForegroundColor $color
        Write-Host "      URL:    $($repo.url)" -ForegroundColor DarkGray
        Write-Host "      子目录: $($repo.skills_subdir)" -ForegroundColor DarkGray
        Write-Host "      添加于: $($repo.added_at)" -ForegroundColor DarkGray

        if ($repo.skills) {
            $skillList = $repo.skills -join ", "
            Write-Host "      Skills: $skillList" -ForegroundColor White
        }

        # 检查链接状态
        $broken = @()
        foreach ($skill in $repo.skills) {
            $linkPath = Join-Path $SkillTarget $skill
            if (-not (Test-Path $linkPath)) {
                $broken += $skill
            }
        }
        if ($broken.Count -gt 0) {
            Write-Host "      断裂:  $($broken -join ', ')" -ForegroundColor Red
        }
    }

    Write-Host ""
    Write-Host "  $('=' * 50)" -ForegroundColor DarkGray

    # 定时任务状态
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($task) {
        Write-Host "  定时任务: 已启用 ($($task.State))" -ForegroundColor Green
    } else {
        Write-Host "  定时任务: 未安装 (运行 'skill-manager install-task' 启用每日自动同步)" -ForegroundColor Yellow
    }
    Write-Host ""
}

function Invoke-Sync {
    Write-Log "========== 开始同步所有 skill 仓库 ==========" "INFO"

    $config = Load-Config
    $totalUpdated = 0
    $totalFailed = 0

    foreach ($repo in $config.repos) {
        if (-not $repo.enabled) {
            Write-Log "跳过已禁用仓库: $($repo.name)" "INFO"
            continue
        }

        $repoPath = Join-Path $ReposDir $repo.name
        if (-not (Test-Path $repoPath)) {
            Write-Log "仓库目录不存在，重新克隆: $($repo.name)" "WARN"
            git clone $repo.url $repoPath 2>&1 | ForEach-Object { Write-Log $_ }
            if ($LASTEXITCODE -ne 0) {
                Write-Log "克隆失败: $($repo.name)" "ERROR"
                $totalFailed++
                continue
            }
        }

        # 记录当前 HEAD
        $oldHead = (git -C $repoPath rev-parse HEAD 2>$null)

        # 拉取更新
        $pullOutput = git -C $repoPath pull --ff-only 2>&1
        $pullOutput | ForEach-Object { Write-Log "  [$($repo.name)] $_" }

        if ($LASTEXITCODE -ne 0) {
            Write-Log "拉取失败: $($repo.name)，尝试 reset" "WARN"
            git -C $repoPath fetch origin 2>&1 | Out-Null
            git -C $repoPath reset --hard origin/main 2>&1 | Out-Null
        }

        $newHead = (git -C $repoPath rev-parse HEAD 2>$null)

        if ($oldHead -ne $newHead) {
            Write-Log "$($repo.name): 已更新 $($oldHead.Substring(0,7)) -> $($newHead.Substring(0,7))" "OK"
            $totalUpdated++

            # 检查是否有新的 skill 需要链接
            $skillDirs = Get-SkillDirs -RepoPath $repoPath -SubDir $repo.skills_subdir
            $newSkills = @()
            foreach ($dir in $skillDirs) {
                $linkPath = Join-Path $SkillTarget $dir.Name
                if (-not (Test-Path $linkPath)) {
                    cmd /c "mklink /J `"$linkPath`" `"$($dir.FullName)`"" | Out-Null
                    Write-Log "  新 skill 已链接: $($dir.Name)" "OK"
                    $newSkills += $dir.Name
                }
            }
            # 更新配置中的 skills 列表
            if ($newSkills.Count -gt 0) {
                $repo.skills = @($repo.skills) + $newSkills | Select-Object -Unique
                Save-Config $config
            }
        } else {
            Write-Log "$($repo.name): 已是最新" "INFO"
        }
    }

    Write-Log "========== 同步完成: $totalUpdated 个更新, $totalFailed 个失败 ==========" "INFO"
}

function Invoke-InstallTask {
    $scriptPath = Join-Path $ManagerDir "skill-manager.ps1"
    $action = New-ScheduledTaskAction `
        -Execute "powershell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`" sync -Quiet"

    # 每天 09:00 运行 + 登录时运行
    $triggerDaily = New-ScheduledTaskTrigger -Daily -At "09:00"
    $triggerLogon = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable

    $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existing) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }

    Register-ScheduledTask `
        -TaskName $TaskName `
        -Description "每日自动同步 Claude/OpenCode agent skill 仓库" `
        -Action $action `
        -Trigger @($triggerDaily, $triggerLogon) `
        -Settings $settings `
        -RunLevel Limited | Out-Null

    Write-Log "定时任务已安装: $TaskName" "OK"
    Write-Log "  触发: 每天 09:00 + 每次登录" "INFO"
    Write-Log "  脚本: $scriptPath" "INFO"
    Write-Log "  日志: $LogFile" "INFO"
}

function Invoke-UninstallTask {
    $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existing) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Log "定时任务已移除: $TaskName" "OK"
    } else {
        Write-Log "定时任务不存在: $TaskName" "WARN"
    }
}

function Invoke-Help {
    Write-Host ""
    Write-Host "  Skill 仓库管理器" -ForegroundColor Cyan
    Write-Host "  管理 Git skill 仓库，自动同步到 Claude Code / OpenCode" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  命令:" -ForegroundColor White
    Write-Host "    add <url>          添加并克隆一个 skill 仓库，自动创建 Junction" -ForegroundColor Gray
    Write-Host "    remove <name>      移除一个 skill 仓库及其所有链接" -ForegroundColor Gray
    Write-Host "    list               列出所有已注册仓库及状态" -ForegroundColor Gray
    Write-Host "    sync               同步所有仓库 (git pull + 链接新 skill)" -ForegroundColor Gray
    Write-Host "    install-task       注册 Windows 定时任务 (每天 + 登录时自动同步)" -ForegroundColor Gray
    Write-Host "    uninstall-task     移除定时任务" -ForegroundColor Gray
    Write-Host "    help               显示此帮助" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  选项:" -ForegroundColor White
    Write-Host "    -SkillsSubdir <dir>  指定仓库中 skill 所在子目录 (默认: skills)" -ForegroundColor Gray
    Write-Host "    -Force               强制覆盖已有 skill" -ForegroundColor Gray
    Write-Host "    -Quiet               静默模式 (仅写日志，不输出到控制台)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  示例:" -ForegroundColor White
    Write-Host "    skill-manager add https://github.com/kepano/obsidian-skills.git" -ForegroundColor DarkCyan
    Write-Host "    skill-manager add https://github.com/user/my-skill.git -SkillsSubdir '.'" -ForegroundColor DarkCyan
    Write-Host "    skill-manager sync" -ForegroundColor DarkCyan
    Write-Host "    skill-manager install-task" -ForegroundColor DarkCyan
    Write-Host ""
    Write-Host "  路径:" -ForegroundColor White
    Write-Host "    配置文件: $ConfigFile" -ForegroundColor DarkGray
    Write-Host "    仓库目录: $ReposDir" -ForegroundColor DarkGray
    Write-Host "    链接目标: $SkillTarget" -ForegroundColor DarkGray
    Write-Host "    同步日志: $LogFile" -ForegroundColor DarkGray
    Write-Host ""
}

# ─── 入口 ───
New-Item -ItemType Directory -Path $ManagerDir -Force | Out-Null
New-Item -ItemType Directory -Path $ReposDir -Force | Out-Null
New-Item -ItemType Directory -Path $SkillTarget -Force | Out-Null

switch ($Command) {
    "add"            { Invoke-Add -Url $Argument }
    "remove"         { Invoke-Remove -Name $Argument }
    "list"           { Invoke-List }
    "sync"           { Invoke-Sync }
    "install-task"   { Invoke-InstallTask }
    "uninstall-task" { Invoke-UninstallTask }
    "help"           { Invoke-Help }
}
