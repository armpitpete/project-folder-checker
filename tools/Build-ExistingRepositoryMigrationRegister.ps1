[CmdletBinding()]
param(
    [string]$AuditPath = 'I:\ORDER\MainVault\00_Control\PROJECT_CONTROL_AUDIT.md',
    [string]$ActiveWorkPath = 'I:\ORDER\MainVault\00_Control\ACTIVE_WORK.md',
    [string]$OutputPath = 'I:\ORDER\MainVault\00_Control\EXISTING_REPOSITORY_MIGRATION_REGISTER.md',
    [int]$ExpectedCount = 19
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-Python {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @{ Command = 'py'; Prefix = @('-3') }
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @{ Command = 'python'; Prefix = @() }
    }
    throw 'Python 3 is required but neither py nor python is available.'
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git is required.'
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw 'GitHub CLI is required.'
}

& gh auth status
if ($LASTEXITCODE -ne 0) {
    throw 'GitHub CLI is not authenticated.'
}

$Script = Join-Path $PSScriptRoot '..\scripts\build_existing_repository_migration_register.py'
$Script = (Resolve-Path $Script).Path
$Python = Resolve-Python
$Arguments = @($Python.Prefix) + @(
    $Script,
    '--audit', $AuditPath,
    '--active-work', $ActiveWorkPath,
    '--output', $OutputPath,
    '--expected-count', $ExpectedCount
)

& $Python.Command @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "Migration-register import failed with exit code $LASTEXITCODE"
}
if (-not (Test-Path $OutputPath)) {
    throw "Migration register was not written: $OutputPath"
}

Write-Host ''
Write-Host 'MIGRATION REGISTER IMPORTED'
Write-Host "Output: $OutputPath"
Write-Host 'Target repositories changed: 0'
Write-Warning 'STOP: do not change any target repository.'
