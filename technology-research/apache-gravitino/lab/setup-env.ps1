$ErrorActionPreference = 'Stop'
$envPath = Join-Path $PSScriptRoot '.env'
if (Test-Path -LiteralPath $envPath) {
    Write-Host '.env already exists; keeping existing credentials.'
    exit 0
}
$bytes = New-Object byte[] 24
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
$password = [BitConverter]::ToString($bytes).Replace('-', '').ToLowerInvariant()
[IO.File]::WriteAllLines($envPath, @("POSTGRES_PASSWORD=$password", 'GRAVITINO_PORT=19090'), [Text.UTF8Encoding]::new($false))
Write-Host 'Created .env with a random local password. Keep it private and retain it with your volumes.'
