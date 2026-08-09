[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9][a-z0-9.-]*$')]
    [string]$RepositoryName,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$ProjectName,

    [Parameter(Mandatory = $true)]
    [ValidateSet('story', 'language', 'product', 'hardware', 'research', 'system', 'other')]
    [string]$ProjectType,

    [ValidateSet('private', 'public')]
    [string]$Visibility = 'private',

    [string]$Owner = 'armpitpete',
    [string]$GitHubRoot = 'I:\ORDER\GitHub',
    [string]$AuditOutput = 'I:\ORDER\MainVault\00_Control\PROJECT_CONTROL_AUDIT.md'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$LegacyCreator = Join-Path $PSScriptRoot 'New-OrderProject.ps1'
$StatusConsumer = Join-Path (Split-Path $PSScriptRoot -Parent) 'scripts\project_status_v2.py'

if (-not (Test-Path $LegacyCreator)) { throw "Missing creator: $LegacyCreator" }
if (-not (Test-Path $StatusConsumer)) { throw "Missing Project Status v2 consumer: $StatusConsumer" }

& $LegacyCreator `
    -RepositoryName $RepositoryName `
    -ProjectName $ProjectName `
    -ProjectType $ProjectType `
    -Visibility $Visibility `
    -Owner $Owner `
    -GitHubRoot $GitHubRoot `
    -AuditOutput $AuditOutput

$TargetDirectory = Join-Path $GitHubRoot $RepositoryName
if (-not (Test-Path (Join-Path $TargetDirectory '.git'))) {
    throw "Generated repository is unavailable: $TargetDirectory"
}

$PythonCommand = if (Get-Command py -ErrorAction SilentlyContinue) { 'py' } elseif (Get-Command python -ErrorAction SilentlyContinue) { 'python' } else { throw 'Python 3 is required.' }
$PythonPrefix = if ($PythonCommand -eq 'py') { @('-3') } else { @() }

Push-Location $TargetDirectory
try {
    if (Test-Path 'project-status.json') {
        throw 'Refusing to overwrite an existing project-status.json.'
    }

    & $PythonCommand @PythonPrefix $StatusConsumer `
        --repository "$Owner/$RepositoryName" `
        --project-name $ProjectName `
        --output project-status.json
    if ($LASTEXITCODE -ne 0) { throw 'Project Status v2 generation failed.' }

    & $PythonCommand @PythonPrefix $StatusConsumer `
        --repository "$Owner/$RepositoryName" `
        --project-name $ProjectName `
        --output project-status.json `
        --validate-only
    if ($LASTEXITCODE -ne 0) { throw 'Generated Project Status v2 validation failed.' }

    $Changed = @(& git status --porcelain=v1 --untracked-files=all)
    if ($LASTEXITCODE -ne 0 -or $Changed.Count -ne 1 -or $Changed[0] -notmatch 'project-status\.json$') {
        throw "Project Status integration changed unexpected files: $($Changed -join ', ')"
    }

    & git add -- project-status.json
    if ($LASTEXITCODE -ne 0) { throw 'Could not stage project-status.json.' }
    & git diff --cached --check
    if ($LASTEXITCODE -ne 0) { throw 'Project Status diff failed git diff --check.' }
    & git commit -m 'Add initial evidence-bound project status'
    if ($LASTEXITCODE -ne 0) { throw 'Could not commit project-status.json.' }
    & git push origin main
    if ($LASTEXITCODE -ne 0) { throw 'Could not push project-status.json.' }

    $Dirty = @(& git status --porcelain=v1 --untracked-files=all)
    if ($Dirty) { throw "Generated repository is dirty after status push: $($Dirty -join ', ')" }
}
finally {
    Pop-Location
}

Write-Host 'PROJECT STATUS V2 INTEGRATED'
Write-Host 'Evidence state: INSUFFICIENT until direct project-specific evidence is recorded.'
