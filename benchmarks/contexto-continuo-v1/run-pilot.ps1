param([string]$Pilot = "artifacts/contexto-continuo-v1/piloto")
$ErrorActionPreference = "Stop"
& .\.venv\Scripts\python.exe -m research_benchmarks.continuous check $Pilot
if ($LASTEXITCODE -ne 0) { throw "El piloto no supera la comprobación local." }
$command = Get-Content -LiteralPath (Join-Path $Pilot "command.json") -Raw | ConvertFrom-Json
$program = $command[0]
$runArgs = @($command | Select-Object -Skip 1)
& $program @runArgs
exit $LASTEXITCODE
