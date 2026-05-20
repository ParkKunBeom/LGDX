$project = Get-ChildItem -LiteralPath $PSScriptRoot -Directory |
  Where-Object { $_.Name -like 'DX_*' } |
  Select-Object -First 1

if (-not $project) {
  throw "DX project folder was not found."
}

$app = Join-Path $project.FullName 'mom-care-app\public\index.html'

if (-not (Test-Path -LiteralPath $app)) {
  throw "Mom Care app index.html was not found: $app"
}

Start-Process -FilePath $app
