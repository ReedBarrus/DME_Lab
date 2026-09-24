$ErrorActionPreference = "Stop"

$ExpectedInstalledBridgePrestateSha256 = "0f86b8499c269ee42ed50285e4429c504ff5e6f93a6e65836128e98ef9d2bb21"
$ExpectedAuthorityModuleSha256 = "bfbbb929f0a0b55a745b5095fd2abd16541757b88f3151d69e7e7bb325e57303"
$ExpectedPolicySha256 = "65f2ce8c3ce1cd5147940ff851cb61a9f04b7db220dadb4c77e1d5352e28200b"
$ExpectedCandidateBridgeSha256 = "98a380044712bfd04e4f64c1a1982dbb0662aa3f646beda3dfdc882ab7ef8918"

$TrustRoot = Join-Path $env:USERPROFILE ".dme_lab_bridge"
$InstalledBridge = Join-Path $TrustRoot "bridge.py"
$InstalledAuthorityModule = Join-Path $TrustRoot "local_authority_consumption_v0.py"
$InstalledPolicy = Join-Path $TrustRoot "policy.json"
$CandidateBridge = Join-Path $PSScriptRoot "bridge.py"
$BackupBridge = Join-Path $TrustRoot "bridge.py.pre-cell003-git-blob-0f86b849.bak"

function Get-ExactSha256([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required file missing: $Path"
    }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

$InstalledBridgePrestateSha256 = Get-ExactSha256 $InstalledBridge
$AuthorityModuleSha256 = Get-ExactSha256 $InstalledAuthorityModule
$PolicySha256 = Get-ExactSha256 $InstalledPolicy
$CandidateBridgeSha256 = Get-ExactSha256 $CandidateBridge

if ($InstalledBridgePrestateSha256 -ne $ExpectedInstalledBridgePrestateSha256) {
    throw "Installed bridge pre-state hash mismatch: $InstalledBridgePrestateSha256"
}
if ($AuthorityModuleSha256 -ne $ExpectedAuthorityModuleSha256) {
    throw "Installed authority-module hash mismatch: $AuthorityModuleSha256"
}
if ($PolicySha256 -ne $ExpectedPolicySha256) {
    throw "Installed policy hash mismatch: $PolicySha256"
}
if ($CandidateBridgeSha256 -ne $ExpectedCandidateBridgeSha256) {
    throw "Candidate bridge hash mismatch: $CandidateBridgeSha256"
}
if (Test-Path -LiteralPath $BackupBridge) {
    throw "Refusing to overwrite existing backup: $BackupBridge"
}

Write-Host "CELL 003 TRUST-ROOT PROMOTION"
Write-Host "SOURCE INSTALLED OBJECT / HASH"
Write-Host "  $InstalledBridge"
Write-Host "  $InstalledBridgePrestateSha256"
Write-Host "REVIEWED CANDIDATE / HASH"
Write-Host "  $CandidateBridge"
Write-Host "  $CandidateBridgeSha256"
Write-Host "BACKUP"
Write-Host "  $BackupBridge"
Write-Host ""
Write-Host "COPY SCOPE"
Write-Host "  bridge.py ONLY"
Write-Host "  authority module: UNCHANGED"
Write-Host "  policy: UNCHANGED"
Write-Host ""

Copy-Item -LiteralPath $InstalledBridge -Destination $BackupBridge
Copy-Item -LiteralPath $CandidateBridge -Destination $InstalledBridge -Force

$DestinationBridgeSha256 = Get-ExactSha256 $InstalledBridge
$AuthorityModuleAfterSha256 = Get-ExactSha256 $InstalledAuthorityModule
$PolicyAfterSha256 = Get-ExactSha256 $InstalledPolicy

if ($DestinationBridgeSha256 -ne $ExpectedCandidateBridgeSha256) {
    throw "Destination bridge verification failed: $DestinationBridgeSha256"
}
if ($AuthorityModuleAfterSha256 -ne $ExpectedAuthorityModuleSha256) {
    throw "Authority module changed during promotion"
}
if ($PolicyAfterSha256 -ne $ExpectedPolicySha256) {
    throw "Policy changed during promotion"
}

Write-Host "DESTINATION OBJECT / HASH"
Write-Host "  $InstalledBridge"
Write-Host "  $DestinationBridgeSha256"
Write-Host "AUTHORITY MODULE UNCHANGED / HASH"
Write-Host "  $InstalledAuthorityModule"
Write-Host "  $AuthorityModuleAfterSha256"
Write-Host "POLICY UNCHANGED / HASH"
Write-Host "  $InstalledPolicy"
Write-Host "  $PolicyAfterSha256"
Write-Host "PROMOTION RESULT: PASS"
Write-Host "INSTALLED STANDING: V0.1 CAPABLE / NOT YET CELL003 PRESSURE-QUALIFIED"
