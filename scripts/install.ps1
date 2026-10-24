<#
.SYNOPSIS
    One-command Windows installer for Engram + Karpathy LLM Wiki (Second Brain).
.DESCRIPTION
    1. Initializes your Obsidian Vault from `vault-template/` (if it doesn't already exist).
    2. Runs initial `engram.py sync` and `engram.py lint` to verify 100/100 graph health.
    3. Adds the `engram` CLI shortcut to your PowerShell $PROFILE.
    4. Prints the ready-to-paste MCP server config for Claude Code, Antigravity, Cursor, and Windsurf.
#>
param(
    [string]$BaseDir = "$HOME\obsidian-brain"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$EngineScript = Join-Path $RepoRoot "src\engram.py"
$McpScript = Join-Path $RepoRoot "src\engram_mcp.py"
$VaultPath = Join-Path $BaseDir "Brain"
$DbPath = Join-Path $BaseDir "engram.db"

Write-Host "==> [1/4] Preparing Second Brain directory at: $BaseDir" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $BaseDir | Out-Null

if (-not (Test-Path $VaultPath)) {
    Write-Host "==> Copying starter Obsidian Vault template to: $VaultPath" -ForegroundColor Green
    Copy-Item -Path (Join-Path $RepoRoot "vault-template") -Destination $VaultPath -Recurse -Force
} else {
    Write-Host "==> Existing Obsidian Vault found at $VaultPath (preserved)." -ForegroundColor Yellow
}

$env:ENGRAM_DB_PATH = $DbPath
$env:OBSIDIAN_VAULT_PATH = $VaultPath

Write-Host "==> [2/4] Running initial Delta Sync & FTS5 indexing..." -ForegroundColor Cyan
python $EngineScript sync --sources obsidian

Write-Host "==> [3/4] Running Karpathy LLM Wiki Health Check (lint)..." -ForegroundColor Cyan
python $EngineScript lint --vault $VaultPath

Write-Host "==> [4/4] Registering 'engram' CLI function in PowerShell profile..." -ForegroundColor Cyan
$ProfileDir = Split-Path -Parent $PROFILE
if (-not (Test-Path $ProfileDir)) {
    New-Item -ItemType Directory -Force -Path $ProfileDir | Out-Null
}
if (-not (Test-Path $PROFILE)) {
    New-Item -ItemType File -Force -Path $PROFILE | Out-Null
}
$ProfileContent = Get-Content $PROFILE -Raw -ErrorAction SilentlyContinue
if ($ProfileContent -notmatch "function engram") {
    $Snippet = @"

# --- Engram + Karpathy LLM Wiki Second Brain ---
`$env:ENGRAM_DB_PATH = "$DbPath"
`$env:OBSIDIAN_VAULT_PATH = "$VaultPath"
function engram { python "$EngineScript" @args }
"@
    Add-Content -Path $PROFILE -Value $Snippet -Encoding UTF8
    Write-Host "    Added 'engram' command to $PROFILE" -ForegroundColor Green
} else {
    Write-Host "    'engram' function already exists in $PROFILE" -ForegroundColor Yellow
}

Write-Host "`n✅ Installation Complete! Add this MCP server block to your agent config:" -ForegroundColor Green
$McpJson = @{
    mcpServers = @{
        engram = @{
            command = "python"
            args    = @($McpScript)
            env     = @{
                ENGRAM_DB_PATH      = $DbPath
                OBSIDIAN_VAULT_PATH = $VaultPath
            }
        }
    }
} | ConvertTo-Json -Depth 5
Write-Host $McpJson
