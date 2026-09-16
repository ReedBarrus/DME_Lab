param(
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"
$appDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourcePath = Join-Path $appDir "HomeCaptureLauncher.cs"
$buildDir = Join-Path $appDir "build"
$iconPath = Join-Path $buildDir "home_capture.ico"
if (-not $OutputPath) {
    $OutputPath = Join-Path $appDir "Home Capture.exe"
}
$OutputPath = [IO.Path]::GetFullPath($OutputPath)

$compilerCandidates = @(
    (Join-Path $env:WINDIR "Microsoft.NET\Framework64\v4.0.30319\csc.exe"),
    (Join-Path $env:WINDIR "Microsoft.NET\Framework\v4.0.30319\csc.exe")
)
$compiler = $compilerCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $compiler) {
    throw "The Windows .NET Framework C# compiler was not found."
}

New-Item -ItemType Directory -Force -Path $buildDir | Out-Null

Add-Type -AssemblyName System.Drawing
$bitmap = New-Object Drawing.Bitmap 64, 64
$graphics = [Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.Clear([Drawing.Color]::FromArgb(22, 25, 29))
$borderPen = New-Object Drawing.Pen ([Drawing.Color]::FromArgb(184, 224, 218)), 3
$graphics.DrawEllipse($borderPen, 5, 5, 54, 54)
$font = New-Object Drawing.Font "Segoe UI", 31, ([Drawing.FontStyle]::Bold), ([Drawing.GraphicsUnit]::Pixel)
$brush = New-Object Drawing.SolidBrush ([Drawing.Color]::FromArgb(235, 242, 239))
$format = New-Object Drawing.StringFormat
$format.Alignment = [Drawing.StringAlignment]::Center
$format.LineAlignment = [Drawing.StringAlignment]::Center
$graphics.DrawString("H", $font, $brush, (New-Object Drawing.RectangleF 0, 0, 64, 61), $format)
$handle = $bitmap.GetHicon()
$icon = [Drawing.Icon]::FromHandle($handle)
$stream = [IO.File]::Create($iconPath)
try {
    $icon.Save($stream)
} finally {
    $stream.Dispose()
    $icon.Dispose()
    $format.Dispose()
    $brush.Dispose()
    $font.Dispose()
    $borderPen.Dispose()
    $graphics.Dispose()
    $bitmap.Dispose()
}

$compilerArguments = @(
    "/nologo",
    "/target:winexe",
    "/optimize+",
    "/platform:anycpu",
    "/win32icon:$iconPath",
    "/reference:System.dll",
    "/reference:System.Core.dll",
    "/reference:System.Drawing.dll",
    "/reference:System.Windows.Forms.dll",
    "/out:$OutputPath",
    $sourcePath
)

& $compiler $compilerArguments
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $OutputPath)) {
    throw "Home Capture.exe build failed with compiler exit code $LASTEXITCODE."
}

$artifact = Get-Item -LiteralPath $OutputPath
$hash = (Get-FileHash -LiteralPath $OutputPath -Algorithm SHA256).Hash.ToLowerInvariant()
[pscustomobject]@{
    output = $artifact.FullName
    bytes = $artifact.Length
    sha256 = $hash
    compiler = $compiler
    target = "winexe"
} | ConvertTo-Json
