# fallatctl.ps1
# Fallat CrewAI / Earnetics Command Center CLI

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ArgsFromShell
)

# ---------------------------------------
# CONFIG
# ---------------------------------------
# If you ever change the port or host in Docker, update this:
$base = "http://localhost:8000"

# ---------------------------------------
# LOW-LEVEL API HELPERS
# ---------------------------------------
function Invoke-ApiGet {
    param(
        [Parameter(Mandatory = $true)][string]$Path
    )
    try {
        return Invoke-RestMethod -Uri "$base$Path" -Method Get
    } catch {
        Write-Host "GET $Path failed:" -ForegroundColor Red
        Write-Host $_ -ForegroundColor DarkRed
        throw
    }
}

function Invoke-ApiPost {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $false)][object]$BodyObj
    )
    try {
        if ($null -ne $BodyObj) {
            $json = $BodyObj | ConvertTo-Json -Depth 8
            return Invoke-RestMethod -Uri "$base$Path" -Method Post -Body $json -ContentType "application/json"
        } else {
            return Invoke-RestMethod -Uri "$base$Path" -Method Post
        }
    } catch {
        Write-Host "POST $Path failed:" -ForegroundColor Red
        Write-Host $_ -ForegroundColor DarkRed
        throw
    }
}

# ---------------------------------------
# TOP-LEVEL HELP / MENU
# ---------------------------------------
function Show-Menu {
    Write-Host "=== FALLAT CREWAI / EARNETICS COMMAND CENTER ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Core:" -ForegroundColor Yellow
    Write-Host "  status                    - Show overall system health and core status"
    Write-Host "  audit [N]                 - Show last N audit events (default 20)"
    Write-Host ""
    Write-Host "Wealth Engine:" -ForegroundColor Yellow
    Write-Host "  wealth list               - List core wealth plays with IDs"
    Write-Host "  wealth play <play_id>     - Execute a single run of a wealth play"
    Write-Host "  wealth auto <play_id>     - Start autonomous cycle for a wealth play"
    Write-Host "  wealth runs <play_id>     - Show runs for a given play"
    Write-Host "  auto-wealth <play_id>     - Shortcut for 'wealth auto <play_id>'"
    Write-Host ""
    Write-Host "Revenue Loop:" -ForegroundColor Yellow
    Write-Host "  loop run                  - Trigger the main revenue-loop flow once"
    Write-Host "  auto-loop                 - Shortcut for running the main revenue-loop flow"
    Write-Host ""
    Write-Host "Agents:" -ForegroundColor Yellow
    Write-Host "  agents roster             - Show known agents and roles"
    Write-Host "  agents activity           - Show recent agent activity"
    Write-Host ""
    Write-Host "System:" -ForegroundColor Yellow
    Write-Host "  menu                      - Show this menu"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor DarkGray
    Write-Host "  .\fallatctl.ps1 status"
    Write-Host "  .\fallatctl.ps1 wealth list"
    Write-Host "  .\fallatctl.ps1 wealth play rev-03-brand-awareness-engine"
    Write-Host "  .\fallatctl.ps1 auto-wealth rev-03-brand-awareness-engine"
    Write-Host "  .\fallatctl.ps1 auto-loop"
}

# ---------------------------------------
# STATUS / HEALTH
# ---------------------------------------
function Show-Status {
    Write-Host "=== FALLAT CREWAI STATUS ===" -ForegroundColor Cyan

    $health  = Invoke-ApiGet "/health"
    $summary = Invoke-ApiGet "/api/system/summary"
    $wealth  = Invoke-ApiGet "/wealth/status"
    $factory = Invoke-ApiGet "/api/factory/status"

    # --- Core ---
    Write-Host "`n[Core]" -ForegroundColor Yellow
    Write-Host ("  Status     : {0}" -f $summary.status)
    Write-Host ("  Version    : {0}" -f $summary.version)
    Write-Host ("  Started    : {0}" -f $summary.startup_time)

    # --- Health ---
    Write-Host "`n[Health]" -ForegroundColor Yellow
    Write-Host ("  Overall    : {0}" -f $health.status)

    $checks = $health.checks
    if ($checks) {
        foreach ($prop in $checks.PSObject.Properties) {
            $name = $prop.Name
            $val  = $prop.Value
            $ok   = $val.ok
            $msg  = $val.message

            $statusText = if ($ok) { "ok" } else { "error" }
            $line = "  {0,-15} {1}" -f $name, $statusText
            if ($msg) { $line += " ($msg)" }

            if ($ok) {
                Write-Host $line -ForegroundColor Green
            } else {
                Write-Host $line -ForegroundColor Red
            }
        }
    }

    # --- Wealth Engine ---
    Write-Host "`n[Wealth Engine]" -ForegroundColor Yellow
    Write-Host ("  Plays      : Total={0} Active={1} Paused={2}" -f `
        $wealth.total, $wealth.active, $wealth.paused)

    # --- Factory ---
    Write-Host "`n[Factory]" -ForegroundColor Yellow
    Write-Host ("  Running    : {0}" -f $factory.running)
    Write-Host ("  Interval   : {0} seconds" -f $factory.interval_seconds)
    Write-Host ("  Streams    : {0}" -f $factory.streams)
}

# ---------------------------------------
# WEALTH ENGINE
# ---------------------------------------
function Show-WealthPlays {
    $core = Invoke-ApiGet "/wealth/core_plays"
    Write-Host "=== CORE WEALTH PLAYS ===" -ForegroundColor Cyan
    foreach ($p in $core.core_plays) {
        Write-Host ""
        Write-Host ("ID   : {0}" -f $p.id) -ForegroundColor Yellow
        Write-Host ("Name : {0}" -f $p.name)
        Write-Host ("Risk : {0}" -f $p.risk_tier)
        Write-Host ("Tags : {0}" -f ($p.tags -join ", "))
    }
}

function Run-WealthPlay {
    param(
        [Parameter(Mandatory = $true)][string]$PlayId
    )

    Write-Host ("Executing wealth play (single run): {0}" -f $PlayId) -ForegroundColor Cyan

    # Most endpoints you tried accepted an empty body
    $body = @{}
    $result = Invoke-ApiPost "/wealth/plays/$PlayId/execute" $body
    $result | Format-List
}

function Run-WealthAutonomousCycle {
    param(
        [Parameter(Mandatory = $true)][string]$PlayId
    )

    Write-Host ("Starting autonomous cycle for play: {0}" -f $PlayId) -ForegroundColor Cyan

    $body = @{
        play_id = $PlayId
    }

    $result = Invoke-ApiPost "/wealth/autonomous_cycle" $body
    $result | Format-List
}

function Show-WealthRuns {
    param(
        [Parameter(Mandatory = $true)][string]$PlayId
    )

    $runs = Invoke-ApiGet "/wealth/plays/$PlayId/runs"
    Write-Host ("=== RUNS FOR {0} ===" -f $PlayId) -ForegroundColor Cyan
    $runs | Format-List
}

# ---------------------------------------
# REVENUE LOOP
# ---------------------------------------
function Run-RevenueLoop {
    Write-Host "Triggering revenue loop flow: revenue_loop" -ForegroundColor Cyan
    $body = @{ flow_id = "revenue_loop" }
    $result = Invoke-ApiPost "/api/revenue-loop/run" $body
    $result | Format-List
}

# ---------------------------------------
# AGENTS
# ---------------------------------------
function Show-AgentsRoster {
    $res = Invoke-ApiGet "/api/agents/roster"
    Write-Host "=== AGENT ROSTER ===" -ForegroundColor Cyan
    Write-Host ("Totals: Total={0} Active={1}" -f `
        $res.totals.total_agents, $res.totals.active_agents)

    foreach ($a in $res.agents) {
        Write-Host ""
        Write-Host ("Name     : {0}" -f $a.name) -ForegroundColor Yellow
        Write-Host ("Role     : {0}" -f $a.role)
        Write-Host ("Division : {0}" -f $a.division)
        Write-Host ("Status   : {0}" -f $a.status)
    }
}

function Show-AgentsActivity {
    $res = Invoke-ApiGet "/api/agents/activity"
    Write-Host "=== RECENT AGENT ACTIVITY ===" -ForegroundColor Cyan
    foreach ($e in $res.events) {
        Write-Host ""
        Write-Host ("[{0}] {1}" -f $e.timestamp, $e.action) -ForegroundColor Yellow
        Write-Host ("  Agent  : {0}" -f $e.agent)
        Write-Host ("  Status : {0}" -f $e.status)
        if ($e.details) {
            Write-Host ("  Details: {0}" -f $e.details)
        }
    }
}

# ---------------------------------------
# AUDIT
# ---------------------------------------
function Show-AuditEvents {
    param(
        [int]$Limit = 20
    )

    Write-Host ("=== LAST {0} AUDIT EVENTS ===" -f $Limit) -ForegroundColor Cyan

    $url = "$base/api/audit/events?limit=$Limit"

    try {
        $resp = Invoke-RestMethod $url

        if (-not $resp.events) {
            Write-Host "No audit events returned." -ForegroundColor Yellow
            return
        }

        foreach ($evt in $resp.events) {
            $ts     = $evt.timestamp
            $action = $evt.action
            $status = $evt.status
            $agent  = $evt.agent
            Write-Host "[$ts] [$status] [$agent] $action"
        }
    }
    catch {
        Write-Host "Error fetching audit events: $_" -ForegroundColor Red
    }
}

# ---------------------------------------
# INTERACTIVE MAIN MENU (NO ARGS)
# ---------------------------------------
function Show-MainMenu {
    while ($true) {
        Clear-Host
        Write-Host "=== FALLAT CREWAI COMMAND CENTER (CLI) ===" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1) System status"
        Write-Host "2) List wealth plays"
        Write-Host "3) Run wealth play (single execute)"
        Write-Host "4) Start autonomous cycle for a play"
        Write-Host "5) Trigger revenue loop"
        Write-Host "6) Show agents roster"
        Write-Host "7) Show recent agent activity"
        Write-Host "8) Show recent audit events"
        Write-Host "9) Show help menu"
        Write-Host "0) Exit"
        Write-Host ""
        $choice = Read-Host "Choose option"

        switch ($choice) {
            "1" { Show-Status; Pause }
            "2" { Show-WealthPlays; Pause }
            "3" {
                $playId = Read-Host "Enter play_id"
                if ($playId) { Run-WealthPlay -PlayId $playId }
                Pause
            }
            "4" {
                $playId = Read-Host "Enter play_id"
                if ($playId) { Run-WealthAutonomousCycle -PlayId $playId }
                Pause
            }
            "5" { Run-RevenueLoop; Pause }
            "6" { Show-AgentsRoster; Pause }
            "7" { Show-AgentsActivity; Pause }
            "8" { Show-AuditEvents -Limit 20; Pause }
            "9" { Show-Menu; Pause }
            "0" { return }
            default { Write-Host "Invalid choice" -ForegroundColor Red; Start-Sleep -Seconds 1 }
        }
    }
}

# ---------------------------------------
# ENTRYPOINT ROUTING
# ---------------------------------------
if (-not $ArgsFromShell -or $ArgsFromShell.Count -eq 0) {
    Show-MainMenu
    exit 0
}

$cmd = $ArgsFromShell[0].ToLower()

switch ($cmd) {
    "menu"       { Show-Menu }
    "status"     { Show-Status }

    # Wealth group
    "wealth" {
        if ($ArgsFromShell.Count -lt 2) {
            Write-Host "Usage: fallatctl.ps1 wealth <list|play|auto|runs> [play_id]" -ForegroundColor Red
            break
        }
        $sub = $ArgsFromShell[1].ToLower()
        switch ($sub) {
            "list" { Show-WealthPlays }
            "play" {
                if ($ArgsFromShell.Count -lt 3) {
                    Write-Host "Usage: fallatctl.ps1 wealth play <play_id>" -ForegroundColor Red
                    break
                }
                $playId = $ArgsFromShell[2]
                Run-WealthPlay -PlayId $playId
            }
            "auto" {
                if ($ArgsFromShell.Count -lt 3) {
                    Write-Host "Usage: fallatctl.ps1 wealth auto <play_id>" -ForegroundColor Red
                    break
                }
                $playId = $ArgsFromShell[2]
                Run-WealthAutonomousCycle -PlayId $playId
            }
            "runs" {
                if ($ArgsFromShell.Count -lt 3) {
                    Write-Host "Usage: fallatctl.ps1 wealth runs <play_id>" -ForegroundColor Red
                    break
                }
                $playId = $ArgsFromShell[2]
                Show-WealthRuns -PlayId $playId
            }
            default {
                Write-Host "Unknown wealth subcommand" -ForegroundColor Red
            }
        }
    }

    # Shortcut: auto-wealth <play_id>
    "auto-wealth" {
        if ($ArgsFromShell.Count -lt 2) {
            Write-Host "Usage: fallatctl.ps1 auto-wealth <play_id>" -ForegroundColor Red
            break
        }
        $playId = $ArgsFromShell[1]
        Run-WealthAutonomousCycle -PlayId $playId
    }

    # Revenue-loop group
    "loop" {
        if ($ArgsFromShell.Count -lt 2) {
            Write-Host "Usage: fallatctl.ps1 loop run" -ForegroundColor Red
            break
        }
        $sub = $ArgsFromShell[1].ToLower()
        switch ($sub) {
            "run" { Run-RevenueLoop }
            default { Write-Host "Unknown loop subcommand" -ForegroundColor Red }
        }
    }

    # Shortcut: auto-loop
    "auto-loop" {
        Run-RevenueLoop
    }

    # Agents group
    "agents" {
        if ($ArgsFromShell.Count -lt 2) {
            Write-Host "Usage: fallatctl.ps1 agents <roster|activity>" -ForegroundColor Red
            break
        }
        $sub = $ArgsFromShell[1].ToLower()
        switch ($sub) {
            "roster"   { Show-AgentsRoster }
            "activity" { Show-AgentsActivity }
            default    { Write-Host "Unknown agents subcommand" -ForegroundColor Red }
        }
    }

    # Audit
    "audit" {
        $limit = 20
        if ($ArgsFromShell.Count -ge 2) {
            [int]::TryParse($ArgsFromShell[1], [ref]$limit) | Out-Null
        }
        Show-AuditEvents -Limit $limit
    }

    default {
        Write-Host "Unknown command. Try: menu | status | wealth | auto-wealth | loop | auto-loop | agents | audit" -ForegroundColor Red
    }
}
