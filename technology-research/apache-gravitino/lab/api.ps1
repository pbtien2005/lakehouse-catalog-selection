param(
    [Parameter(Mandatory=$true)][ValidateSet('GET','POST','PUT','PATCH','DELETE')][string]$Method,
    [Parameter(Mandatory=$true)][string]$Path,
    [string]$BodyFile
)
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $dockerArgs = @('compose', 'exec', '-T', 'gravitino', 'python3', '/lab/scripts/lab.py', 'api', $Method, $Path)
    if ($BodyFile) {
        # Payload paths are relative to the lab and are read inside its read-only mount.
        if ($BodyFile -notmatch '^payloads/[a-z0-9-]+\.json$') {
            throw 'Use a path such as payloads/create-table.json'
        }
        $dockerArgs += "/lab/$BodyFile"
    }
    & docker @dockerArgs
    if ($LASTEXITCODE -ne 0) { throw 'Gravitino API command failed.' }
} finally { Pop-Location }
