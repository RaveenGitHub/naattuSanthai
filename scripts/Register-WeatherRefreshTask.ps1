param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$TaskName = "NaattuSanthai-IMD-Weather-Refresh",
    [ValidateRange(0, 23)]
    [int]$Hour = 6,
    [ValidateRange(0, 59)]
    [int]$Minute = 0
)

$ErrorActionPreference = "Stop"
$resolvedRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$pythonPath = Join-Path $resolvedRoot ".venv\Scripts\python.exe"
$envPath = Join-Path $resolvedRoot ".env"

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Project virtual environment not found at $pythonPath. Install project dependencies first."
}

if (-not (Test-Path -LiteralPath $envPath)) {
    throw "Create $envPath and configure IMD_API_KEY and IMD_API_TOKEN before registering the refresh task."
}

$configuredCredentials = @{}
foreach ($line in Get-Content -LiteralPath $envPath) {
    if ($line -match '^\s*(IMD_API_KEY|IMD_API_TOKEN)\s*=\s*(.*?)\s*$') {
        $value = $Matches[2].Trim('"').Trim("'")
        if ($value) {
            $configuredCredentials[$Matches[1]] = $true
        }
    }
}

if (-not $configuredCredentials.ContainsKey("IMD_API_KEY") -or -not $configuredCredentials.ContainsKey("IMD_API_TOKEN")) {
    throw "$envPath must contain non-empty IMD_API_KEY and IMD_API_TOKEN values."
}

$action = New-ScheduledTaskAction `
    -Execute $pythonPath `
    -Argument "-m digital_farming.weather_refresh" `
    -WorkingDirectory $resolvedRoot
$runAt = (Get-Date).Date.AddHours($Hour).AddMinutes($Minute)
$trigger = New-ScheduledTaskTrigger -Daily -At $runAt
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew `
    -RestartCount 2 `
    -RestartInterval (New-TimeSpan -Minutes 15) `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
$principal = New-ScheduledTaskPrincipal `
    -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Fetch and validate official IMD forecasts for the configured Tamil Nadu city catalog." `
    -Force | Out-Null

Write-Output "Registered '$TaskName' to run daily at $($runAt.ToString('HH:mm')) for the current user."
