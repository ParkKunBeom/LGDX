$app = Join-Path $PSScriptRoot 'public\index.html'

if (-not (Test-Path -LiteralPath $app)) {
  throw "Mom Care app index.html was not found: $app"
}

Start-Process -FilePath $app
