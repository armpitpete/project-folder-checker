[CmdletBinding()]
param(
    [string]$GitHubRoot = 'I:\ORDER\GitHub',
    [string]$OutputPath = 'I:\ORDER\MainVault\00_Control\PROJECT_CONTROL_AUDIT.md',
    [switch]$FailOnControlProblems
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

$AuditScript = Join-Path $PSScriptRoot 'audit_project_controls.py'
if (-not (Test-Path $AuditScript)) {
    throw "Audit implementation is missing: $AuditScript"
}

$Python = Resolve-Python
$Arguments = @($Python.Prefix) + @(
    $AuditScript,
    '--root', $GitHubRoot,
    '--output', $OutputPath
)
if ($FailOnControlProblems) {
    $Arguments += '--fail-on-control-problems'
}

& $Python.Command @Arguments
$ExitCode = $LASTEXITCODE
if ($ExitCode -notin @(0, 2)) {
    throw "Project-control audit failed with exit code $ExitCode"
}
if ($ExitCode -eq 2) {
    Write-Warning 'Audit completed. UNMANAGED or DRIFTED repositories were found.'
}
if (-not (Test-Path $OutputPath)) {
    throw "Audit did not produce the required report: $OutputPath"
}

Write-Host "Project-control audit written to: $OutputPath"
exit $ExitCode
