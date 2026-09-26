param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$DistPath = Join-Path $RepoRoot "dist\cockpit"
$WorkPath = Join-Path $RepoRoot "build\cockpit_pyinstaller"
$Exe = Join-Path $DistPath "DME Cockpit.exe"

Push-Location $RepoRoot
try {
    & $Python -m PyInstaller --version *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller is not installed for '$Python'. Install it explicitly with: $Python -m pip install pyinstaller"
    }

    New-Item -ItemType Directory -Force -Path $DistPath | Out-Null
    New-Item -ItemType Directory -Force -Path $WorkPath | Out-Null

    if (Test-Path $Exe) {
        try {
            $Probe = [System.IO.File]::Open(
                $Exe,
                [System.IO.FileMode]::Open,
                [System.IO.FileAccess]::ReadWrite,
                [System.IO.FileShare]::None
            )
            $Probe.Dispose()
        }
        catch {
            throw "DME Cockpit.exe is currently in use. Close the running Cockpit before rebuilding: $Exe"
        }
    }

    & $Python -m PyInstaller `
        --noconfirm `
        --clean `
        --onefile `
        --windowed `
        --name "DME Cockpit" `
        --distpath $DistPath `
        --workpath $WorkPath `
        --specpath $WorkPath `
        --paths $RepoRoot `
        --collect-submodules src.cockpit `
        "src\cockpit\desktop_launcher.py"

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }

    if (-not (Test-Path $Exe)) {
        throw "Expected executable was not produced: $Exe"
    }

    Write-Host ""
    Write-Host "Built:"
    Write-Host "  $Exe"
    Write-Host ""
    Write-Host "First launch will locate DME_Lab from --repo, DME_LAB_REPO, saved config, or a folder picker."
    Write-Host "After the repository is remembered, the executable can be pinned to the Windows taskbar."
}
finally {
    Pop-Location
}
