$ErrorActionPreference = 'Stop'
$envPath = Join-Path $PSScriptRoot '.env'
if (Test-Path -LiteralPath $envPath) {
    Write-Host '.env already exists; left unchanged.'
    exit 0
}
$pgPassword = [guid]::NewGuid().ToString('N')
$storagePassword = [guid]::NewGuid().ToString('N')
@(
    "POSTGRES_PASSWORD=$pgPassword"
    'MINIO_ROOT_USER=labadmin'
    "MINIO_ROOT_PASSWORD=$storagePassword"
) | Set-Content -LiteralPath $envPath -Encoding ascii
Write-Host 'Created local .env with random lab passwords.'
