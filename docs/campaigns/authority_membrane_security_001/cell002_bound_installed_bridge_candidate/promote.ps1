$ErrorActionPreference = "Stop"

$ExpectedSourceBridgeSha256 = "5a4c466595ec4820bd8430ee3ee91f5a38437e55bfb48a8a756dfa53c87d7fdb"
$ExpectedAuthorityModuleSha256 = "bfbbb929f0a0b55a745b5095fd2abd16541757b88f3151d69e7e7bb325e57303"
$ExpectedPolicySha256 = "65f2ce8c3ce1cd5147940ff851cb61a9f04b7db220dadb4c77e1d5352e28200b"
$ExpectedCandidateBridgeSha256 = "0f86b8499c269ee42ed50285e4429c504ff5e6f93a6e65836128e98ef9d2bb21"

$TrustRoot = Join-Path $env:USERPROFILE ".dme_lab_bridge"
$InstalledBridge = Join-Path $TrustRoot "bridge.py"
$InstalledAuthorityModule = Join-Path $TrustRoot "local_authority_consumption_v0.py"
$InstalledPolicy = Join-Path $TrustRoot "policy.json"
$CandidateBridge = Join-Path $PSScriptRoot "bridge.py"
$BackupBridge = Join-Path $TrustRoot "bridge.py.pre-cell002-binding-5a4c4665.bak"

function Get-ExactSha256([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required file missing: $Path"
    }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

$SourceBridgeSha256 = Get-ExactSha256 $InstalledBridge
$AuthorityModuleSha256 = Get-ExactSha256 $InstalledAuthorityModule
$PolicySha256 = Get-ExactSha256 $InstalledPolicy
$CandidateBridgeSha256 = Get-ExactSha256 $CandidateBridge

if ($SourceBridgeSha256 -ne $ExpectedSourceBridgeSha256) {
    throw "Installed bridge pre-state hash mismatch: $SourceBridgeSha256"
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

Write-Host "SOURCE OBJECT / HASH"
Write-Host "  $InstalledBridge"
Write-Host "  $SourceBridgeSha256"
Write-Host "COPY / REPLACE"
Write-Host "  backup: $BackupBridge"
Write-Host "  reviewed candidate: $CandidateBridge"

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
