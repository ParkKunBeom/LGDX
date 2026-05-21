$project = Get-ChildItem -LiteralPath $PSScriptRoot -Directory |
  Where-Object { $_.Name -like 'DX_*' } |
  Select-Object -First 1

if (-not $project) {
  throw "DX project folder was not found."
}

$appDir = Join-Path $project.FullName 'mom-care-app'
$server = Join-Path $appDir 'server.mjs'

if (-not (Test-Path -LiteralPath $server)) {
  throw "Mom Care backend server was not found: $server"
}

try {
  Invoke-WebRequest -Uri 'http://localhost:5173/api/health' -UseBasicParsing -TimeoutSec 1 | Out-Null
} catch {
  Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$appDir'; node server.mjs"
  Start-Sleep -Seconds 2
}

Start-Process 'http://localhost:5173'
