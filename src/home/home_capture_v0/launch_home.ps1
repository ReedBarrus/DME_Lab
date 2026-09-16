param(
    [switch]$Lan,
    [switch]$NoOpen,
    [int]$Port = 8765,
    [string]$DataDir = ""
)

$ErrorActionPreference = "Stop"
$appDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$serverPath = Join-Path $appDir "server.py"
if (-not $DataDir) {
    $DataDir = Join-Path $appDir "data"
}
$DataDir = [System.IO.Path]::GetFullPath($DataDir)
$logsDir = Join-Path $DataDir "logs"
$healthUrl = "http://127.0.0.1:$Port/api/health"
$appUrl = "http://127.0.0.1:$Port/"
$requiredMode = if ($Lan) { "lan" } else { "desktop" }

function Show-HomeError([string]$Message) {
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show(
        $Message,
        "Home Capture could not start",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    ) | Out-Null
}

function Get-HomeHealth {
    try {
        $health = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 1
        if ($health.service -eq "home_capture_v0" -and $health.status -eq "operational") {
            return $health
        }
    } catch {
        return $null
    }
    return $null
}

function Open-HomeWindow {
    if ($NoOpen) { return }
    $browserCandidates = @(
        "$env:ProgramFiles (x86)\Microsoft\Edge\Application\msedge.exe",
        "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
        "$env:LOCALAPPDATA\Microsoft\Edge\Application\msedge.exe",
        "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
        "$env:ProgramFiles (x86)\Google\Chrome\Application\chrome.exe"
    )
    foreach ($candidate in $browserCandidates) {
        if (Test-Path -LiteralPath $candidate) {
            Start-Process -FilePath $candidate -ArgumentList @("--app=$appUrl", "--new-window") | Out-Null
            return
        }
    }
    Start-Process $appUrl | Out-Null
}

try {
    $existing = Get-HomeHealth
    if ($existing) {
        if ($Lan -and $existing.access_mode -ne "lan") {
            Show-HomeError "Home is already running in desktop-only mode. Close its Python process before starting trusted-LAN mode. No duplicate server was started."
            exit 2
        }
        Open-HomeWindow
        exit 0
    }

    $pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue | Select-Object -First 1
    $pythonArguments = @()
    if (-not $pythonCommand) {
        $pythonCommand = Get-Command py.exe -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($pythonCommand) { $pythonArguments += "-3" }
    }
    if (-not $pythonCommand) {
        Show-HomeError "Python 3 was not found. Install Python 3, then launch Home Capture again."
        exit 3
    }

    New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
    $stdoutPath = Join-Path $logsDir "server.stdout.log"
    $stderrPath = Join-Path $logsDir "server.stderr.log"
    $hostValue = if ($Lan) { "0.0.0.0" } else { "127.0.0.1" }
    $pythonArguments += @(
        $serverPath,
        "--host", $hostValue,
        "--port", $Port,
        "--data-dir", $DataDir,
        "--access-mode", $requiredMode
    )

    $process = Start-Process -FilePath $pythonCommand.Source `
        -ArgumentList $pythonArguments `
        -WorkingDirectory $appDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath `
        -PassThru

    $health = $null
    for ($attempt = 0; $attempt -lt 80; $attempt++) {
        Start-Sleep -Milliseconds 250
        $health = Get-HomeHealth
        if ($health) { break }
        if ($process.HasExited) { break }
    }
    if (-not $health) {
        $details = ""
        if (Test-Path -LiteralPath $stderrPath) {
            $details = (Get-Content -LiteralPath $stderrPath -Raw -ErrorAction SilentlyContinue).Trim()
        }
        if ($details.Length -gt 700) { $details = $details.Substring(0, 700) }
        Show-HomeError "The Home service did not become operational.`n`n$details`n`nLog: $stderrPath"
        exit 4
    }

    Open-HomeWindow
    exit 0
} catch {
    Show-HomeError "Home startup failed: $($_.Exception.Message)"
    exit 5
}
