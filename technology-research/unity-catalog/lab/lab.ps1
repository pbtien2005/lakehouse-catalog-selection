param(
    [ValidateSet('up','demo','inspect','verify','snapshot','shell','files','logs','stop','down','status')]
    [string]$Action = 'status'
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Push-Location $PSScriptRoot
try {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw 'Install Docker Desktop with Linux containers first.'
    }
    & docker info --format '{{.OSType}}'
    if ($LASTEXITCODE -ne 0) { throw 'Docker daemon unavailable. Start Docker Desktop (Linux containers), then retry.' }

    switch ($Action) {
        'up' {
            & docker compose up -d uc
            if ($LASTEXITCODE -ne 0) { throw 'Compose startup failed.' }
            $ready = $false
            for ($i = 0; $i -lt 60; $i++) {
                try {
                    $null = Invoke-RestMethod 'http://127.0.0.1:18080/api/2.1/unity-catalog/catalogs' -TimeoutSec 5
                    $ready = $true
                    break
                } catch { Start-Sleep -Seconds 2 }
            }
            if (-not $ready) { throw 'UC did not become ready. Run ./lab.ps1 logs.' }
            Write-Host 'UC ready on http://127.0.0.1:18080. Next: ./lab.ps1 demo'
        }
        'logs' { & docker compose logs --tail 150 uc }
        'status' { & docker compose ps -a }
        'stop' { & docker compose stop }
        'down' { & docker compose down }
        'files' { & docker compose exec uc find /lab-data -maxdepth 7 -type f }
        default { & docker compose run --rm spark $Action }
    }
    if ($LASTEXITCODE -ne 0) { throw "Lab command failed: $Action (exit $LASTEXITCODE)" }
} finally { Pop-Location }
