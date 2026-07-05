$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$LogDir = Join-Path $RepoRoot "data\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$Stamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LogFile = Join-Path $LogDir "daily-update-$Stamp.log"

Set-Location $RepoRoot
if (-not $env:AGENT_REACH_TIMEOUT_SECONDS) {
  $env:AGENT_REACH_TIMEOUT_SECONDS = "30"
}

"[$(Get-Date -Format o)] Starting IslandEdge daily update in $RepoRoot" |
  Tee-Object -FilePath $LogFile

& python scripts\run_daily_pipeline.py --target-date yesterday --reddit-max-queries 16 --twitter-max-queries 12 *>&1 |
  Tee-Object -FilePath $LogFile -Append

$ExitCode = $LASTEXITCODE
"[$(Get-Date -Format o)] IslandEdge daily update finished with exit code $ExitCode" |
  Tee-Object -FilePath $LogFile -Append
exit $ExitCode
