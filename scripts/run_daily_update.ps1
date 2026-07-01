$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$LogDir = Join-Path $RepoRoot "data\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$Stamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LogFile = Join-Path $LogDir "daily-update-$Stamp.log"

Set-Location $RepoRoot

& python scripts\run_daily_pipeline.py --target-date yesterday --twitter-max-queries 12 *>&1 |
  Tee-Object -FilePath $LogFile
