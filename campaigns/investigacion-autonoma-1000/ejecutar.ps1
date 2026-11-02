param(
    [string]$Output
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$python = Join-Path $repoRoot '.venv/Scripts/python.exe'
if (-not $Output) {
    $Output = Join-Path $repoRoot 'artifacts/investigacion-autonoma-1000'
}
$Output = [System.IO.Path]::GetFullPath($Output)
if (Test-Path -LiteralPath $Output) {
    throw "El destino debe ser nuevo: $Output"
}
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "No se encuentra el interprete del laboratorio: $python"
}
$mandate = Join-Path $PSScriptRoot 'mandato.md'
$message = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'peticion.md') -Raw -Encoding utf8
if ([string]::IsNullOrWhiteSpace($message)) { throw 'La peticion esta vacia.' }

# Explicit profile and timeouts apply only to this invocation; .env is untouched.
$settings = @{
    LLM_PLANNER_PROVIDER = 'openai'
    LLM_PLANNER_MODEL = 'gpt-6-luna'
    LLM_PLANNER_REASONING_EFFORT = 'medium'
    LLM_PLANNER_MAX_OUTPUT_TOKENS = '16000'
    LLM_TIMEOUT_SECONDS = '180'
    LLM_CALL_BUDGET_SECONDS = '180'
    PYTHONIOENCODING = 'utf-8'
}
$previous = @{}
foreach ($name in $settings.Keys) {
    $previous[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
}
Push-Location $repoRoot
try {
    foreach ($name in $settings.Keys) {
        [Environment]::SetEnvironmentVariable($name, $settings[$name], 'Process')
    }
    & $python -m research_agent $message `
        --experiment $Output --new --run-name investigacion-autonoma-1000 `
        --mandate $mandate --continuous --python `
        --max-calls 1000 --max-total-calls 1000 --max-tools 2000 --timeout-seconds 300 `
        --context-bytes 524288 --consolidation-bytes 262144
    $runExitCode = $LASTEXITCODE
}
finally {
    foreach ($name in $settings.Keys) {
        [Environment]::SetEnvironmentVariable($name, $previous[$name], 'Process')
    }
    Pop-Location
}
exit $runExitCode
