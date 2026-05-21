param(
    [string]$Text = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $ScriptDir
$ModelPath = Join-Path $Root "models\diary_emotion_nb_model.json"
$LabelMapPath = Join-Path $Root "data\processed\label_map.json"

function Normalize-Text {
    param([string]$Value)
    return (($Value.Trim().ToLower() -split "\s+") -join " ")
}

function Add-Feature {
    param(
        [hashtable]$Features,
        [string]$Key,
        [int]$Count = 1
    )
    if ($Features.ContainsKey($Key)) {
        $Features[$Key] += $Count
    } else {
        $Features[$Key] = $Count
    }
}

function Extract-Features {
    param([string]$Value)

    $normalized = Normalize-Text $Value
    $compact = $normalized.Replace(" ", "")
    $features = @{}

    foreach ($token in ($normalized -split " ")) {
        if ($token.Length -ge 2) {
            Add-Feature $features "w:$token"
        }
    }

    foreach ($n in @(2, 3)) {
        if ($compact.Length -ge $n) {
            for ($i = 0; $i -le $compact.Length - $n; $i++) {
                Add-Feature $features "c${n}:$($compact.Substring($i, $n))"
            }
        }
    }

    return $features
}

function Get-JsonPropertyValue {
    param(
        [object]$Object,
        [string]$Name,
        [object]$DefaultValue = $null
    )

    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $DefaultValue
    }
    return $property.Value
}

function Predict-Emotion {
    param(
        [object]$Model,
        [string]$Value
    )

    $features = Extract-Features $Value
    $vocabulary = @{}
    foreach ($feature in $Model.vocabulary) {
        $vocabulary[$feature] = $true
    }

    $scores = @{}
    foreach ($label in $Model.labels) {
        $prior = [double](Get-JsonPropertyValue $Model.priors $label 0)
        $featureCounts = Get-JsonPropertyValue $Model.feature_counts $label
        $featureTotal = [double](Get-JsonPropertyValue $Model.feature_totals $label 0)
        $denominator = $featureTotal + $Model.vocabulary.Count
        $evidence = 0.0
        $evidenceCount = 0

        foreach ($feature in $features.Keys) {
            if ($vocabulary.ContainsKey($feature)) {
                $featureCount = [double](Get-JsonPropertyValue $featureCounts $feature 0)
                $count = [int]$features[$feature]
                $evidence += [Math]::Log(($featureCount + 1) / $denominator) * $count
                $evidenceCount += $count
            }
        }

        $score = $prior
        if ($evidenceCount -gt 0) {
            $score += $evidence / $evidenceCount
        }
        $scores[$label] = $score
    }

    $maxScore = ($scores.Values | Measure-Object -Maximum).Maximum
    $expScores = @{}
    $total = 0.0
    foreach ($label in $scores.Keys) {
        $value = [Math]::Exp($scores[$label] - $maxScore)
        $expScores[$label] = $value
        $total += $value
    }

    $probabilities = @{}
    foreach ($label in $expScores.Keys) {
        $probabilities[$label] = $expScores[$label] / $total
    }

    $best = $probabilities.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1
    return @{
        Prediction = $best.Key
        Probabilities = $probabilities
    }
}

if (-not (Test-Path $ModelPath)) {
    throw "Model file not found: $ModelPath"
}

if ([string]::IsNullOrWhiteSpace($Text)) {
    $Text = Read-Host "Diary text"
}

if ([string]::IsNullOrWhiteSpace($Text)) {
    Write-Host "No text entered."
    exit 1
}

$model = Get-Content -LiteralPath $ModelPath -Raw -Encoding UTF8 | ConvertFrom-Json
$labelMap = Get-Content -LiteralPath $LabelMapPath -Raw -Encoding UTF8 | ConvertFrom-Json
$predictionResult = Predict-Emotion $model $Text
$probabilities = $predictionResult.Probabilities
$prediction = $predictionResult.Prediction

$ranking = $probabilities.GetEnumerator() |
    Sort-Object Value -Descending |
    ForEach-Object {
        [ordered]@{
            emotion = $_.Key
            probability = [Math]::Round([double]$_.Value, 4)
        }
    }

$result = [ordered]@{
    input = $Text
    main_emotion = $prediction
    confidence = [Math]::Round([double]$probabilities[$prediction], 4)
    description = (Get-JsonPropertyValue $labelMap.description $prediction "")
    ranking = @($ranking)
}

$result | ConvertTo-Json -Depth 6
