param(
  [string]$RepoPath = "D:\\AgentForgeOS"
)

$ErrorActionPreference = "Stop"

$gitDir = Join-Path $RepoPath ".git"
if (-not (Test-Path -LiteralPath $gitDir)) {
  Write-Host ("MISSING: .git directory at " + $gitDir)
  exit 1
}

$lockFiles = @(
  (Join-Path $gitDir "index.lock"),
  (Join-Path $gitDir "HEAD.lock"),
  (Join-Path $gitDir "packed-refs.lock")
)

$removed = 0
foreach ($lf in $lockFiles) {
  if (Test-Path -LiteralPath $lf) {
    try {
      Remove-Item -LiteralPath $lf -Force
      Write-Host ("REMOVED: " + $lf)
      $removed += 1
    } catch {
      Write-Host ("FAILED: could not remove " + $lf)
      Write-Host ($_.Exception.Message)
      exit 1
    }
  }
}

if ($removed -eq 0) {
  Write-Host "OK: no git lock files found"
} else {
  Write-Host ("OK: removed " + $removed + " lock file(s)")
}

