$ErrorActionPreference = 'Stop'
$envPath = Join-Path $PSScriptRoot '.env'
if (Test-Path -LiteralPath $envPath) {
    Write-Host '.env already exists; keeping existing credentials.'
    exit 0
}
function New-LabPassword {
    $bytes = New-Object byte[] 24
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    return [BitConverter]::ToString($bytes).Replace('-', '').ToLowerInvariant()
}
$lines = @(
    'MINIO_ROOT_USER=nessielab'
    ('MINIO_ROOT_PASSWORD=' + (New-LabPassword))
    ('POSTGRES_PASSWORD=' + (New-LabPassword))
)
[IO.File]::WriteAllLines($envPath, $lines, [Text.UTF8Encoding]::new($false))
Write-Host 'Generated local credentials in .env (do not commit this file).'
