param(
  [Parameter(Mandatory = $true)]
  [string]$InstallDir,

  [string]$BaseUrl = "",
  [switch]$StartBackend,
  [switch]$StartApp,
  [int]$TimeoutSec = 25
)

$ErrorActionPreference = "Stop"

function Fail([string]$Message) {
  Write-Host $Message
  exit 1
}

function Assert-PathExists([string]$Path, [string]$Label) {
  if (-not (Test-Path -LiteralPath $Path)) {
    Fail ("MISSING: " + $Label + " -> " + $Path)
  }
  Write-Host ("OK: " + $Label + " -> " + $Path)
}

function Resolve-BaseUrl([string]$InstallDir, [string]$BaseUrl) {
  if ($BaseUrl -and $BaseUrl.Trim().Length -gt 0) { return $BaseUrl.Trim().TrimEnd("/") }
  $cfgCandidates = @(
    (Join-Path $InstallDir "resources\\config.json"),
    (Join-Path $InstallDir "resources\\resources\\config.json")
  )
  foreach ($cfgPath in $cfgCandidates) {
    if (Test-Path -LiteralPath $cfgPath) {
      try {
        $cfg = Get-Content -LiteralPath $cfgPath -Raw | ConvertFrom-Json
        $serverHost = $cfg.server.host
        $serverPort = $cfg.server.port
        if ($serverHost -and $serverPort) {
          return ("http://" + $serverHost + ":" + $serverPort)
        }
      } catch {
      }
    }
  }
  return "http://127.0.0.1:8000"
}

function Resolve-WorkspacePath([string]$InstallDir) {
  $cfgCandidates = @(
    (Join-Path $InstallDir "resources\\config.json"),
    (Join-Path $InstallDir "resources\\resources\\config.json")
  )
  foreach ($cfgPath in $cfgCandidates) {
    if (Test-Path -LiteralPath $cfgPath) {
      try {
        $cfg = Get-Content -LiteralPath $cfgPath -Raw | ConvertFrom-Json
        $ws = $cfg.workspace_path
        if ($ws -and $ws.ToString().Trim().Length -gt 0) { return $ws.ToString() }
      } catch {
      }
    }
  }
  $candidates = @(
    (Join-Path $InstallDir "resources\\resources\\workspace"),
    (Join-Path $InstallDir "resources\\workspace"),
    (Join-Path $InstallDir "workspace")
  )
  foreach ($c in $candidates) {
    if (Test-Path -LiteralPath $c) { return $c }
  }
  return $candidates[0]
}

function Wait-HttpOk([string]$Url, [int]$TimeoutSec) {
  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    try {
      $resp = Invoke-RestMethod -Method Get -Uri $Url -TimeoutSec 3
      if ($resp -and $resp.success -eq $true) { return $true }
    } catch {
    }
    Start-Sleep -Milliseconds 350
  }
  return $false
}

function Wait-ElectronBackendPort([int]$TimeoutSec) {
  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    foreach ($p in 8000..8099) {
      try {
        $resp = Invoke-RestMethod -Method Get -Uri ("http://127.0.0.1:" + $p + "/health") -TimeoutSec 1
        if ($resp -and $resp.success -eq $true) { return $p }
      } catch {
      }
    }
    Start-Sleep -Milliseconds 350
  }
  return $null
}

function Get-OpenApiPaths([string]$BaseUrl) {
  try {
    $doc = Invoke-RestMethod -Method Get -Uri ($BaseUrl + "/openapi.json") -TimeoutSec 5
    if ($doc -and $doc.paths) { return $doc.paths.PSObject.Properties.Name }
  } catch {
  }
  return @()
}

function Get-FreePort() {
  $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
  $listener.Start()
  $port = $listener.LocalEndpoint.Port
  $listener.Stop()
  return $port
}

if (-not (Test-Path -LiteralPath $InstallDir)) {
  $repoRoot = (Split-Path -Parent $PSScriptRoot)
  Write-Host ("InstallDir does not exist: " + $InstallDir)
  Write-Host "If you're pointing at an installed build folder, pass the real path (on D: in your case)."
  Write-Host "Detected candidate folders under repo root that contain backend.exe:"
  Get-ChildItem -LiteralPath $repoRoot -Directory | ForEach-Object {
    $be = Join-Path $_.FullName "backend.exe"
    if (Test-Path -LiteralPath $be) { Write-Host (" - " + $_.FullName) }
  }
  exit 1
}

$root = (Resolve-Path -LiteralPath $InstallDir).Path
Write-Host ("InstallDir: " + $root)

function Find-WinUnpackedRoot([string]$Dir) {
  $candidates = Get-ChildItem -LiteralPath $Dir -Recurse -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -ieq "win-unpacked" }
  $valid = @()
  foreach ($c in $candidates) {
    $exe = Join-Path $c.FullName "AgentForgeOS.exe"
    $be1 = Join-Path $c.FullName "backend.exe"
    $be2 = Join-Path $c.FullName "resources\\backend.exe"
    if ((Test-Path -LiteralPath $exe) -and ((Test-Path -LiteralPath $be1) -or (Test-Path -LiteralPath $be2))) {
      $valid += $c
    }
  }
  if ($valid.Count -lt 1) { return $null }
  return ($valid | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
}

$winUnpacked = Find-WinUnpackedRoot -Dir $root
if ($winUnpacked -and ($root -ne $winUnpacked)) {
  Write-Host ("Detected win-unpacked build; using: " + $winUnpacked)
  $root = $winUnpacked
}

$resourcesDir = Join-Path $root "resources"
Assert-PathExists $resourcesDir "resources/"

$backendExeCandidates = @(
  (Join-Path $root "backend.exe"),
  (Join-Path $resourcesDir "backend.exe"),
  (Join-Path $resourcesDir "backend2.exe")
)
$backendExe = $backendExeCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $backendExe) {
  Fail "MISSING: backend executable (expected backend.exe at root or under resources/)"
}
Write-Host ("OK: backend -> " + $backendExe)

$appExeCandidates = Get-ChildItem -LiteralPath $root -Filter "*.exe" -File | Where-Object {
  $_.Name -notin @((Split-Path -Leaf $backendExe), "backend2.exe", "elevate.exe", "Squirrel.exe")
}
if ($appExeCandidates.Count -lt 1) {
  Write-Host "No app .exe found next to backend (this folder may be a packaging workspace)."
  Write-Host "If you're targeting Electron 'win-unpacked', point InstallDir at the win-unpacked folder."
  Fail "MISSING: app executable in InstallDir"
}
$preferredApp = $appExeCandidates | Where-Object { $_.Name -ieq "AgentForgeOS.exe" } | Select-Object -First 1
if (-not $preferredApp) { $preferredApp = $appExeCandidates[0] }
Write-Host ("OK: app executable -> " + $preferredApp.FullName)

$urlBase = Resolve-BaseUrl -InstallDir $root -BaseUrl $BaseUrl
Write-Host ("BaseUrl: " + $urlBase)

$proc = $null
$appProc = $null
$prevPort = $env:AGENTFORGE_PORT
$prevHost = $env:AGENTFORGE_HOST
if ($StartBackend -and $StartApp) {
  Fail "Invalid args: use -StartBackend or -StartApp (not both)"
}
if ($StartBackend) {
  Write-Host "Starting backend..."
  $backendCwd = Split-Path -Parent $backendExe
  if (-not $BaseUrl -or $BaseUrl.Trim().Length -eq 0) {
    $port = Get-FreePort
    $env:AGENTFORGE_HOST = "127.0.0.1"
    $env:AGENTFORGE_PORT = "$port"
    $urlBase = "http://127.0.0.1:$port"
    Write-Host ("BaseUrl (forced for started backend): " + $urlBase)
  }
  $proc = Start-Process -FilePath $backendExe -WorkingDirectory $backendCwd -PassThru -WindowStyle Hidden
  Start-Sleep -Seconds 2
  $proc.Refresh()
  if ($proc.HasExited) {
    Fail ("FAILED: backend process exited immediately (ExitCode=" + $proc.ExitCode + ")")
  }
}
if ($StartApp) {
  Write-Host "Starting app..."
  $appExe = $preferredApp.FullName
  if (-not $BaseUrl -or $BaseUrl.Trim().Length -eq 0) {
    $port = Get-FreePort
    $env:AGENTFORGE_HOST = "127.0.0.1"
    $env:AGENTFORGE_PORT = "$port"
    $urlBase = "http://127.0.0.1:$port"
    Write-Host ("BaseUrl (forced for started app): " + $urlBase)
  }
  $appProc = Start-Process -FilePath $appExe -WorkingDirectory $root -PassThru
}

try {
  $healthOk = Wait-HttpOk -Url ($urlBase + "/api/health") -TimeoutSec $TimeoutSec
  if (-not $healthOk) {
    if ($proc) {
      try {
        $proc.Refresh()
        if ($proc.HasExited) {
          Fail ("FAILED: backend process exited (ExitCode=" + $proc.ExitCode + ")")
        }
      } catch {
      }
    }
    Fail ("FAILED: /api/health not OK within " + $TimeoutSec + "s at " + $urlBase)
  }
  Write-Host "OK: /api/health"

  $wsPath = ""
  $openApiPaths = Get-OpenApiPaths -BaseUrl $urlBase
  if ($openApiPaths.Count -gt 0) {
    if ($openApiPaths -notcontains "/api/system/status") {
      Write-Host "WARN: /api/system/status missing from OpenAPI (backend may be outdated)"
    }
    if ($openApiPaths -notcontains "/api/workspace/status") {
      Write-Host "WARN: /api/workspace/status missing from OpenAPI (backend may be outdated)"
    }
  } else {
    Write-Host "WARN: openapi.json unavailable (skipping route presence checks)"
  }
  try {
    $status = Invoke-RestMethod -Method Get -Uri ($urlBase + "/api/system/status") -TimeoutSec 5
    if ($status -and $status.success -eq $true) {
      Write-Host "OK: /api/system/status"
      $wsPath = $status.data.workspace_path
    }
  } catch {
  }
  if (-not $wsPath) {
    try {
      $w = Invoke-RestMethod -Method Get -Uri ($urlBase + "/api/workspace/status") -TimeoutSec 5
      if ($w -and $w.success -eq $true) {
        Write-Host "OK: /api/workspace/status"
        $wsPath = $w.data.workspace_path
      }
    } catch {
    }
  }
  if (-not $wsPath) {
    $wsPath = Resolve-WorkspacePath -InstallDir $root
    Write-Host ("WARN: workspace path endpoints unavailable; inferring workspace_path -> " + $wsPath)
  }
  if ($wsPath -and (Test-Path -LiteralPath $wsPath)) {
    $required = @("projects", "builds", "deployments", "assets", "temp", "knowledge", "logs", "database", "embeddings")
    foreach ($d in $required) {
      Assert-PathExists (Join-Path $wsPath $d) ("workspace/" + $d)
    }
  } else {
    if (($openApiPaths.Count -gt 0) -and (($openApiPaths -notcontains "/api/system/status") -and ($openApiPaths -notcontains "/api/workspace/status"))) {
      Fail ("MISSING: workspace_path on disk and backend lacks workspace/status routes. Rebuild backend.exe from current source. Expected workspace at: " + $wsPath)
    }
    Fail ("MISSING: workspace_path on disk -> " + $wsPath)
  }

  Write-Host "RELEASE SMOKE: PASS"
  exit 0
} finally {
  if ($proc -and -not $proc.HasExited) {
    try { Stop-Process -Id $proc.Id -Force } catch { }
  }
  if ($appProc -and -not $appProc.HasExited) {
    try { Stop-Process -Id $appProc.Id -Force } catch { }
  }
  if ($StartApp) {
    try {
      Get-Process backend -ErrorAction SilentlyContinue | ForEach-Object {
        try {
          if ($_.Path -and ($_.Path.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase))) {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
          }
        } catch {
        }
      }
    } catch {
    }
  }
  if ($StartBackend) {
    if ($null -ne $prevPort) { $env:AGENTFORGE_PORT = $prevPort } else { Remove-Item Env:\AGENTFORGE_PORT -ErrorAction SilentlyContinue }
    if ($null -ne $prevHost) { $env:AGENTFORGE_HOST = $prevHost } else { Remove-Item Env:\AGENTFORGE_HOST -ErrorAction SilentlyContinue }
  }
}
