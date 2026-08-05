$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$executable = Join-Path $projectRoot "dist\SwordPhantasia.exe"

Push-Location $projectRoot
try {
    python -m PyInstaller --noconfirm --clean main.spec
    if (-not (Test-Path -LiteralPath $executable)) {
        throw "PyInstaller completed without producing $executable"
    }
    $sizeMb = [math]::Round((Get-Item -LiteralPath $executable).Length / 1MB, 1)
    Write-Host "Built Sword Phantasia: $executable ($sizeMb MB)"
}
finally {
    Pop-Location
}
