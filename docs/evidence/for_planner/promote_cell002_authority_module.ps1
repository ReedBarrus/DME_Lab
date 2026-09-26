param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$Source = Join-Path $RepoRoot "src\runtime\local_authority_consumption_v0.py"
$TrustRoot = Join-Path $env:USERPROFILE ".dme_lab_bridge"
$Destination = Join-Path $TrustRoot "local_authority_consumption_v0.py"
$StateDir = Join-Path $TrustRoot "authority_state_v0"

Write-Host "=== DME CELL 002 PROMOTION ==="
Write-Host ""
Write-Host "SOURCE OBJECT:"
Write-Host "  local_authority_consumption_v0.py"
Write-Host "SOURCE LOCATION:"
Write-Host "  $Source"
Write-Host ""
Write-Host "TRANSFORMATION:"
Write-Host "  Copy exact candidate module bytes into local trust-root namespace."
Write-Host ""
Write-Host "DESTINATION OBJECT:"
Write-Host "  local_authority_consumption_v0.py"
Write-Host "DESTINATION LOCATION:"
Write-Host "  $Destination"
Write-Host ""
Write-Host "POLICY CHANGE: NONE"
Write-Host "BRIDGE CHANGE: NONE"
Write-Host ""

if (-not (Test-Path $Source -PathType Leaf)) {
    throw "SOURCE MISSING: $Source"
}

if (-not (Test-Path $TrustRoot -PathType Container)) {
    throw "TRUST ROOT MISSING: $TrustRoot"
}

$sourceHash = (Get-FileHash $Source -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Host "Source SHA256:      $sourceHash"

if (Test-Path $Destination -PathType Leaf) {
    $backup = "$Destination.pre-cell002.bak"
    Copy-Item -LiteralPath $Destination -Destination $backup -Force
    Write-Host "Existing destination backed up to:"
    Write-Host "  $backup"
}

Copy-Item -LiteralPath $Source -Destination $Destination -Force
New-Item -ItemType Directory -Path $StateDir -Force | Out-Null

$destHash = (Get-FileHash $Destination -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Host "Destination SHA256: $destHash"

if ($sourceHash -ne $destHash) {
    throw "PROMOTION FAILED: source/destination SHA256 mismatch"
}

Write-Host ""
Write-Host "POST-STATE:"
Write-Host "  trust-root authority module exists"
Write-Host "  source SHA == destination SHA"
Write-Host "  authority_state_v0 directory exists"
Write-Host "  bridge.py unchanged"
Write-Host "  policy.json unchanged"
Write-Host ""
Write-Host "PROMOTION RESULT: PASS"
Write-Host ""
Write-Host "IMPORTANT:"
Write-Host "  This promotes the Cell 002 authority module into the trust root."
Write-Host "  It does NOT yet bind bridge.py to consume authority before invocation."
