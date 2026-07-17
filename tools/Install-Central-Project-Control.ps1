[CmdletBinding()]
param(
    [string]$TargetDirectory = 'I:\ORDER\MainVault\00_Control\Project_Bootstrap'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepositoryRoot = Split-Path -Parent $PSScriptRoot
$Sources = [ordered]@{
    'New-OrderProject.ps1' = Join-Path $PSScriptRoot 'New-OrderProject.ps1'
    'Run-ProjectControlAudit.ps1' = Join-Path $PSScriptRoot 'Run-ProjectControlAudit.ps1'
    'Prove-Central-Project-Control.ps1' = Join-Path $PSScriptRoot 'Prove-Central-Project-Control.ps1'
    'audit_project_controls.py' = Join-Path $RepositoryRoot 'scripts\audit_project_controls.py'
}

New-Item -ItemType Directory -Force -Path $TargetDirectory | Out-Null

foreach ($File in $Sources.Keys) {
    $Source = $Sources[$File]
    $Target = Join-Path $TargetDirectory $File
    if (-not (Test-Path $Source)) {
        throw "Required installation source is missing: $Source"
    }
    if (Test-Path $Target) {
        $Timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
        Copy-Item $Target "$Target.backup-$Timestamp"
    }
    Copy-Item $Source $Target -Force
    $Expected = (Get-FileHash $Source -Algorithm SHA256).Hash
    $Actual = (Get-FileHash $Target -Algorithm SHA256).Hash
    if ($Expected -ne $Actual) {
        throw "SHA-256 verification failed for $File"
    }
    Write-Host "Installed: $Target"
    Write-Host "SHA-256: $Actual"
}

Write-Host ''
Write-Host 'Central project-control enforcement installed.'
Write-Host "Create projects with: $TargetDirectory\New-OrderProject.ps1"
Write-Host "Run audits with: $TargetDirectory\Run-ProjectControlAudit.ps1"
Write-Host "Run the disposable proof with: $TargetDirectory\Prove-Central-Project-Control.ps1"
