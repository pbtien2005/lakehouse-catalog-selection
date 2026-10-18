$ErrorActionPreference = 'Stop'
function Invoke-LabDocker {
    & docker @args
    if ($LASTEXITCODE -ne 0) { throw "Docker command failed (exit $LASTEXITCODE)." }
}
Push-Location $PSScriptRoot
try {
    Invoke-LabDocker compose exec -T gravitino python3 /lab/scripts/lab.py bootstrap
    $testName = 'smoke_' + [Guid]::NewGuid().ToString('N').Substring(0, 12)
    Write-Host "Testing disposable table sales.$testName"
    Invoke-LabDocker compose exec -T gravitino python3 /lab/scripts/lab.py smoke-create $testName
    $sql = "INSERT INTO sales.$testName (id,note) VALUES (1,'from native SQL'),(2,'second row'); ALTER TABLE sales.$testName ADD COLUMN native_column TEXT;"
    Invoke-LabDocker compose exec -T postgres psql -X -v ON_ERROR_STOP=1 -U lab -d shop -c $sql
    $count = Invoke-LabDocker compose exec -T postgres psql -X -At -U lab -d shop -c "SELECT count(*) FROM sales.$testName;"
    if ("$count".Trim() -ne '2') { throw 'Native row count must be 2.' }
    Write-Host 'PASS: native PostgreSQL inserted and read 2 rows in the API-created table'
    Invoke-LabDocker compose exec -T gravitino python3 /lab/scripts/lab.py smoke-verify $testName
    $remaining = Invoke-LabDocker compose exec -T postgres psql -X -At -U lab -d shop -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='sales' AND table_name='$testName';"
    if ("$remaining".Trim() -ne '0') { throw 'REST drop did not remove the source table.' }
    Write-Host 'PASS: REST DROP removed the disposable source table'
    Write-Host 'PASS: all integration checks completed'
} finally { Pop-Location }
