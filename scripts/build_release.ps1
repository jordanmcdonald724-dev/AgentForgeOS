param(
  [switch]$SkipTests,
  [switch]$SkipFrontend,
  [switch]$SkipBackendBuild,
  [switch]$SkipElectronBuild
)

$ErrorActionPreference = "Stop"

function Run([string]$Cmd, [string]$Cwd = "") {
  Write-Host ("RUN: " + $Cmd)
  if ($Cwd -and $Cwd.Trim().Length -gt 0) { Push-Location $Cwd }
  try {
    Invoke-Expression $Cmd
  } finally {
    if ($Cwd -and $Cwd.Trim().Length -gt 0) { Pop-Location }
  }
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$repoRoot = (Split-Path -Parent $PSScriptRoot)

if (-not $SkipTests) {
  Run "python -m unittest -q" $repoRoot
}

if (-not $SkipFrontend) {
  Run "npm -C frontend run build" $repoRoot
}

if (-not $SkipBackendBuild) {
  Run "python -m PyInstaller backend.spec --distpath dist_backend2 --workpath build_backend2 --noconfirm" $repoRoot
}

if (-not $SkipElectronBuild) {
  Run "npm -C AgentForgeOS-App run build" $repoRoot
}

Write-Host "BUILD RELEASE: DONE"
Write-Host "Next: run release smoke on the generated win-unpacked folder:"
Write-Host "  powershell -ExecutionPolicy Bypass -File .\\scripts\\release_smoke.ps1 -InstallDir \"D:\\AgentForgeOS\\AgentForgeOS-App\" -StartBackend"
Write-Host "  powershell -ExecutionPolicy Bypass -File .\\scripts\\release_smoke.ps1 -InstallDir \"D:\\AgentForgeOS\\AgentForgeOS-App\" -StartApp"
