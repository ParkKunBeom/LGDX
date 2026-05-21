$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$publicRoot = Join-Path $root "public"
$dataRoot = Join-Path $root "backend-data"
$storePath = Join-Path $dataRoot "store.json"
$port = 5173
$prefix = "http://localhost:$port/"

function Ensure-Store {
  if (-not (Test-Path -LiteralPath $dataRoot)) {
    New-Item -ItemType Directory -Path $dataRoot | Out-Null
  }
  if (-not (Test-Path -LiteralPath $storePath)) {
    @{
      diaries = @()
      communityPosts = @()
      subscriptions = @()
      applianceLogs = @()
      assessments = @()
    } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $storePath -Encoding UTF8
  }
}

function Read-Store {
  Ensure-Store
  return Get-Content -LiteralPath $storePath -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Write-Store($store) {
  $store | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $storePath -Encoding UTF8
}

function Send-Text($context, [int]$status, [string]$contentType, [string]$body) {
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
  $context.Response.StatusCode = $status
  $context.Response.ContentType = $contentType
  $context.Response.ContentLength64 = $bytes.Length
  $context.Response.OutputStream.Write($bytes, 0, $bytes.Length)
  $context.Response.OutputStream.Close()
}

function Send-Json($context, [int]$status, $body) {
  Send-Text $context $status "application/json; charset=utf-8" ($body | ConvertTo-Json -Depth 12)
}

function Read-Body($request) {
  $reader = New-Object System.IO.StreamReader($request.InputStream, $request.ContentEncoding)
  $raw = $reader.ReadToEnd()
  if ([string]::IsNullOrWhiteSpace($raw)) {
    return @{}
  }
  return $raw | ConvertFrom-Json
}

function Body-Value($body, [string]$name, $fallback) {
  if ($null -eq $body) {
    return $fallback
  }
  $property = $body.PSObject.Properties[$name]
  if ($null -eq $property -or $null -eq $property.Value -or [string]::IsNullOrWhiteSpace([string]$property.Value)) {
    return $fallback
  }
  return $property.Value
}

function Routine($symptom) {
  $routines = @{
    sleep = @{
      title = "sleep care routine"
      food = "Avoid caffeine in the evening and choose a light snack."
      action = "Dim lights before sleep and reduce phone use."
      mind = "Try five minutes of slow breathing."
      appliances = @("AC sleep mode", "air purifier quiet mode", "mood light 30 percent")
    }
    heat = @{
      title = "cool comfort routine"
      food = "Drink water and choose water rich fruit."
      action = "Wear breathable clothes and check heat alerts."
      mind = "Sit and breathe slowly for three minutes."
      appliances = @("AC dry mode", "circulator low", "washer maternity course")
    }
    swelling = @{
      title = "swelling relief routine"
      food = "Keep protein and water intake steady."
      action = "Raise legs and avoid standing too long."
      mind = "Record body changes without blame."
      appliances = @("massage chair low", "air purifier auto", "dryer low temperature")
    }
    nausea = @{
      title = "nausea relief routine"
      food = "Eat small portions and avoid greasy smells."
      action = "Ventilate the kitchen first."
      mind = "Contact a clinician if nausea is severe."
      appliances = @("hood ventilation", "air purifier high", "fresh food reminder")
    }
    anxiety = @{
      title = "mental care routine"
      food = "Keep meal intervals steady and drink warm water."
      action = "Share feelings with the guardian."
      mind = "Name the emotion and try slow breathing."
      appliances = @("warm mood light", "speaker meditation", "air purifier sleep mode")
    }
  }
  if (-not $routines.ContainsKey($symptom)) {
    $symptom = "sleep"
  }
  return $routines[$symptom]
}

function Assessment($body) {
  $week = [Math]::Min(42, [Math]::Max(1, [int](Body-Value $body "week" 24)))
  $stress = [Math]::Min(10, [Math]::Max(1, [int](Body-Value $body "stress" 5)))
  $symptom = [string](Body-Value $body "symptom" "sleep")
  $routine = Routine $symptom
  $riskLevel = "calm"
  $riskLabel = "calm"
  $riskMessage = "This looks manageable with a daily care routine."
  if ($stress -ge 8) {
    $riskLevel = "risk"
    $riskLabel = "risk"
    $riskMessage = "Stress is high. Consider medical consultation if symptoms feel serious."
  } elseif ($stress -ge 6) {
    $riskLevel = "watch"
    $riskLabel = "watch"
    $riskMessage = "Monitor today condition and share it with the guardian."
  }
  if ($week -lt 14) {
    $trimester = "early"
  } elseif ($week -lt 28) {
    $trimester = "middle"
  } else {
    $trimester = "late"
  }
  return @{
    id = "assessment-$([DateTimeOffset]::Now.ToUnixTimeMilliseconds())"
    week = $week
    trimester = $trimester
    symptom = $symptom
    stress = $stress
    risk = @{
      level = $riskLevel
      label = $riskLabel
      message = $riskMessage
      redFlags = @()
    }
    recommendation = @{
      title = "$week week $($routine.title)"
      food = $routine.food
      action = $routine.action
      mind = $routine.mind
      appliances = $routine.appliances
      evidencePolicy = "This app suggests lifestyle care, not diagnosis."
    }
    createdAt = (Get-Date).ToString("o")
  }
}

function Handle-Api($context) {
  $request = $context.Request
  $path = $request.Url.AbsolutePath
  $method = $request.HttpMethod
  $store = Read-Store

  if ($method -eq "GET" -and $path -eq "/api/health") {
    Send-Json $context 200 @{ ok = $true; service = "ThinQ Mom Care Backend"; runtime = "PowerShell" }
    return
  }
  if ($method -eq "POST" -and $path -eq "/api/assessments") {
    $item = Assessment (Read-Body $request)
    $store.assessments = @($item) + @($store.assessments)
    Write-Store $store
    Send-Json $context 201 $item
    return
  }
  if ($method -eq "GET" -and $path -eq "/api/recommendations") {
    Send-Json $context 200 (Assessment @{ symptom = $request.QueryString["symptom"]; week = $request.QueryString["week"]; stress = 5 })
    return
  }
  if ($method -eq "GET" -and $path -eq "/api/guardian/tasks") {
    Send-Json $context 200 @{ tasks = @("Listen first.", "Check appointments and meals.", "Take over heavy chores.", "Verify community information.") }
    return
  }
  if ($method -eq "GET" -and $path -eq "/api/diaries") {
    Send-Json $context 200 @{ diaries = @($store.diaries) }
    return
  }
  if ($method -eq "POST" -and $path -eq "/api/diaries") {
    $body = Read-Body $request
    $entry = @{
      id = "diary-$([DateTimeOffset]::Now.ToUnixTimeMilliseconds())"
      mood = [string](Body-Value $body "mood" "record")
      text = [string](Body-Value $body "text" "empty")
      shared = [bool](Body-Value $body "shared" $false)
      createdAt = (Get-Date).ToString("o")
    }
    $store.diaries = @($entry) + @($store.diaries)
    Write-Store $store
    Send-Json $context 201 $entry
    return
  }
  if ($method -eq "GET" -and $path -eq "/api/community/posts") {
    Send-Json $context 200 @{ posts = @($store.communityPosts) }
    return
  }
  if ($method -eq "POST" -and $path -eq "/api/appliances/control") {
    $body = Read-Body $request
    $log = @{
      id = "appliance-$([DateTimeOffset]::Now.ToUnixTimeMilliseconds())"
      device = [string](Body-Value $body "device" "ThinQ device")
      command = [string](Body-Value $body "command" "simulate")
      status = "simulated"
      createdAt = (Get-Date).ToString("o")
    }
    $store.applianceLogs = @($log) + @($store.applianceLogs)
    Write-Store $store
    Send-Json $context 200 $log
    return
  }
  if ($method -eq "POST" -and $path -eq "/api/subscriptions") {
    $subscription = @{ id = "subscription-$([DateTimeOffset]::Now.ToUnixTimeMilliseconds())"; plan = "ad-free"; price = 3900; status = "active" }
    $store.subscriptions = @($subscription) + @($store.subscriptions)
    Write-Store $store
    Send-Json $context 201 $subscription
    return
  }
  if ($method -eq "GET" -and $path -eq "/api/trust/sources") {
    Send-Json $context 200 @{
      sources = @(
        @{ name = "KDCA"; type = "public"; useCase = "health rules" },
        @{ name = "MOHW"; type = "public"; useCase = "pregnancy support policy" },
        @{ name = "Korean Society of Obstetrics and Gynecology"; type = "medical"; useCase = "clinical basis" },
        @{ name = "WHO"; type = "global"; useCase = "pregnancy health" }
      )
      answerRules = @("No weak-source information.", "No diagnosis.", "Guide risk symptoms to medical consultation.", "Review reported community posts.")
    }
    return
  }
  Send-Json $context 404 @{ error = "API route not found" }
}

function Serve-Static($context) {
  $path = [System.Uri]::UnescapeDataString($context.Request.Url.AbsolutePath)
  if ($path -eq "/") {
    $path = "/index.html"
  }
  $relative = $path.TrimStart("/") -replace "/", [System.IO.Path]::DirectorySeparatorChar
  $filePath = Join-Path $publicRoot $relative
  if (-not (Test-Path -LiteralPath $filePath)) {
    $filePath = Join-Path $publicRoot "index.html"
  }
  $extension = [System.IO.Path]::GetExtension($filePath)
  $contentType = switch ($extension) {
    ".html" { "text/html; charset=utf-8" }
    ".css" { "text/css; charset=utf-8" }
    ".js" { "text/javascript; charset=utf-8" }
    default { "application/octet-stream" }
  }
  $bytes = [System.IO.File]::ReadAllBytes($filePath)
  $context.Response.StatusCode = 200
  $context.Response.ContentType = $contentType
  $context.Response.ContentLength64 = $bytes.Length
  $context.Response.OutputStream.Write($bytes, 0, $bytes.Length)
  $context.Response.OutputStream.Close()
}

Ensure-Store
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add($prefix)
try {
  $listener.Start()
} catch {
  Write-Host "Port 5173 is unavailable. Open http://localhost:5173 if the server is already running."
  Start-Process "http://localhost:5173"
  Read-Host "Press Enter to exit"
  exit
}
Write-Host "ThinQ Mom Care app: http://localhost:$port"
Write-Host "API health check: http://localhost:$port/api/health"
Start-Process "http://localhost:$port"
try {
  while ($listener.IsListening) {
    $context = $listener.GetContext()
    try {
      if ($context.Request.Url.AbsolutePath.StartsWith("/api/")) {
        Handle-Api $context
      } else {
        Serve-Static $context
      }
    } catch {
      Send-Json $context 500 @{ error = $_.Exception.Message }
    }
  }
} finally {
  $listener.Stop()
}
