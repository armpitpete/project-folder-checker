[CmdletBinding()]
param(
    [string]$RepositoryName = 'project-control-disposable-proof-20260717',
    [string]$GitHubRoot = 'I:\ORDER\GitHub',
    [string]$AuditOutput = 'I:\ORDER\MainVault\00_Control\PROJECT_CONTROL_AUDIT.md',
    [string]$ProofRecord = 'I:\ORDER\MainVault\00_Control\Project_Bootstrap\DISPOSABLE_PROOF.md'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Creator = Join-Path $PSScriptRoot 'New-OrderProject.ps1'
$AuditRunner = Join-Path $PSScriptRoot 'Run-ProjectControlAudit.ps1'
if (-not (Test-Path $Creator)) {
    throw "Project creator is missing: $Creator"
}
if (-not (Test-Path $AuditRunner)) {
    throw "Audit runner is missing: $AuditRunner"
}

& $Creator `
    -RepositoryName $RepositoryName `
    -ProjectName 'Project Control Disposable Proof' `
    -ProjectType 'system' `
    -Visibility 'private' `
    -GitHubRoot $GitHubRoot `
    -AuditOutput $AuditOutput
if ($LASTEXITCODE -ne 0) {
    throw 'Disposable project creation failed.'
}

$RepositoryPath = Join-Path $GitHubRoot $RepositoryName
if (-not (Test-Path (Join-Path $RepositoryPath '.git'))) {
    throw "Disposable repository clone is missing: $RepositoryPath"
}

& $AuditRunner -GitHubRoot $GitHubRoot -OutputPath $AuditOutput
if ($LASTEXITCODE -notin @(0, 2)) {
    throw 'Cross-project audit failed after disposable proof creation.'
}

$AuditText = Get-Content -Raw -Path $AuditOutput
$ExpectedRepository = "armpitpete/$RepositoryName"
$EscapedRepository = [regex]::Escape($ExpectedRepository)
if ($AuditText -notmatch "\|\s*BOOTSTRAP\s*\|\s*``$EscapedRepository``") {
    throw "Audit did not classify $ExpectedRepository as BOOTSTRAP."
}

Push-Location $RepositoryPath
try {
    $Head = (& git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not resolve disposable proof head.'
    }
    $Remote = (& git remote get-url origin).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not resolve disposable proof origin.'
    }
    $Dirty = (& git status --porcelain=v1 --untracked-files=all)
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not verify disposable proof worktree.'
    }
    if ($Dirty) {
        throw 'Disposable proof worktree is not clean.'
    }
}
finally {
    Pop-Location
}

$Now = Get-Date -Format 'yyyy-MM-ddTHH:mm:ssK'
$Record = @"
---
standard: Recursive Project Improvement Standard v1.0
role: disposable-project-control-proof
generated: $Now
repository: $ExpectedRepository
head: $Head
classification: BOOTSTRAP
deletion_authorised: false
---

# Disposable Project-Control Proof

## Result

- Repository created only from `armpitpete/project-template`.
- Clone created at `$RepositoryPath`.
- Template initializer completed.
- Project-control validator passed before commit and after push.
- Initialised authority state committed and pushed.
- Cross-project audit classified the repository as `BOOTSTRAP`.
- Working tree is clean.

## Exact identity

- Repository: `$ExpectedRepository`
- Origin: `$Remote`
- Head: `$Head`
- Audit: `$AuditOutput`

## Stop point

Stop before deleting the disposable repository.

Deletion requires a separate explicit authority.
"@

$ProofDirectory = Split-Path -Parent $ProofRecord
New-Item -ItemType Directory -Force -Path $ProofDirectory | Out-Null
$Record | Set-Content -Path $ProofRecord -Encoding UTF8

Write-Host ''
Write-Host 'DISPOSABLE PROOF PASSED'
Write-Host "Repository: $ExpectedRepository"
Write-Host "Head: $Head"
Write-Host "Proof record: $ProofRecord"
Write-Warning 'STOP: do not delete the disposable repository without separate explicit authority.'
