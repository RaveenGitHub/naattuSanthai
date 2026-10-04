param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$TaskName = "NaattuSanthai-Scheme-Raw-Refresh"
)

$ErrorActionPreference = "Stop"
$resolvedRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$pythonPath = Join-Path $resolvedRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Project virtual environment is missing. Install dependencies first."
}
Push-Location -LiteralPath $resolvedRoot
try {
    & $pythonPath -m digital_farming.scheme_refresh --check
    if ($LASTEXITCODE -ne 0) {
        throw "Configure at least one valid official scheme JSON feed before task registration."
    }
} finally {
    Pop-Location
}
$action = New-ScheduledTaskAction -Execute $pythonPath `
    -Argument "-m digital_farming.scheme_refresh" -WorkingDirectory $resolvedRoot
$triggers = @(
    (New-ScheduledTaskTrigger -Daily -At (Get-Date).Date),
    (New-ScheduledTaskTrigger -Daily -At (Get-Date).Date.AddHours(12))
)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable `
    -MultipleInstances IgnoreNew -RestartCount 2 `
    -RestartInterval (New-TimeSpan -Minutes 15) `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
$principal = New-ScheduledTaskPrincipal `
    -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) `
    -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $triggers `
    -Settings $settings -Principal $principal `
    -Description "Preserve official scheme JSON records for validation; no automatic publication." `
    -Force | Out-Null
Write-Output "Registered '$TaskName' at midnight and noon in Windows local time; current user must be signed in."
