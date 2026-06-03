param(
    [int]$Users = 0,
    [string]$LoadSteps = "",
    [string]$BaseUrl = "http://localhost:8000",
    [string]$FrontendUrl = "http://localhost:5173"
)

$ErrorActionPreference = "Stop"

if ($Users -lt 1 -or $Users -gt 100) {
    $rawUsers = Read-Host "Введите количество ботов от 1 до 100"
    if (-not [int]::TryParse($rawUsers, [ref]$Users)) {
        throw "Количество ботов должно быть числом"
    }
}

if ($Users -lt 1 -or $Users -gt 100) {
    throw "Количество ботов должно быть от 1 до 100"
}

if ([string]::IsNullOrWhiteSpace($LoadSteps)) {
    $LoadSteps = Read-Host "Серия нагрузок через запятую, например 1,10,50,100. Enter = только $Users"
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$runner = Join-Path $scriptDir "run_quality_suite.py"

$argsList = @(
    $runner,
    "--users", $Users,
    "--base-url", $BaseUrl,
    "--frontend-url", $FrontendUrl
)

if (-not [string]::IsNullOrWhiteSpace($LoadSteps)) {
    $argsList += @("--load-steps", $LoadSteps)
}

Set-Location $projectRoot
python @argsList
