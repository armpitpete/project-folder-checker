[CmdletBinding()]
param(
    [string]$GitHubRoot = 'I:\ORDER\GitHub',
    [string]$ControlRoot = 'I:\ORDER\MainVault\00_Control',
    [string]$ExpectedOldHead = '05ae228e79cb4d591d0e984387140d08a0cdc08d',
    [string]$ExpectedNewHead = '25cab54a0dea61d9a5e36041c2d6577fb8f2e614'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepositoryPath = Join-Path $GitHubRoot 'project-folder-checker'
$AuditRunner = Join-Path $ControlRoot 'Project_Bootstrap\Run-ProjectControlAudit.ps1'
$AuditPath = Join-Path $ControlRoot 'PROJECT_CONTROL_AUDIT.md'
$ExceptionPath = Join-Path $ControlRoot 'PROJECT_CONTROL_EXCEPTIONS.md'
$ResultPath = Join-Path $ControlRoot 'EXISTING_REPOSITORY_MIGRATION_BATCH_0_RESULT.md'
$RegisterPath = Join-Path $ControlRoot 'EXISTING_REPOSITORY_MIGRATION_REGISTER.md'
$ExpectedOrigin = 'https://github.com/armpitpete/project-folder-checker.git'

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [string]$WorkingDirectory = $RepositoryPath
    )

    $Output = & git -C $WorkingDirectory @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed:`n$($Output -join [Environment]::NewLine)"
    }
    return @($Output)
}

function Get-RepositoryHeads {
    param([string]$Root)

    $Heads = @{}
    foreach ($Directory in Get-ChildItem -LiteralPath $Root -Directory) {
        if (-not (Test-Path -LiteralPath (Join-Path $Directory.FullName '.git'))) {
            continue
        }
        $Head = (& git -C $Directory.FullName rev-parse HEAD 2>$null)
        if ($LASTEXITCODE -eq 0 -and $Head) {
            $Heads[$Directory.FullName] = ([string]$Head).Trim()
        }
    }
    return $Heads
}

function Get-AuditCount {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$Classification
    )

    $Pattern = "(?m)^- \*\*$([regex]::Escape($Classification)):\*\* (?<Count>\d+)\s*$"
    $Match = [regex]::Match($Text, $Pattern)
    if (-not $Match.Success) {
        throw "Could not read $Classification count from $AuditPath"
    }
    return [int]$Match.Groups['Count'].Value
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git is required.'
}
if (-not (Test-Path -LiteralPath $RepositoryPath)) {
    throw "Repository path does not exist: $RepositoryPath"
}
if (-not (Test-Path -LiteralPath (Join-Path $RepositoryPath '.git'))) {
    throw "Not a Git worktree: $RepositoryPath"
}
if (-not (Test-Path -LiteralPath $AuditRunner)) {
    throw "Central audit runner does not exist: $AuditRunner"
}
if (-not (Test-Path -LiteralPath $RegisterPath)) {
    throw "Migration register does not exist: $RegisterPath"
}

$BeforeHeads = Get-RepositoryHeads -Root $GitHubRoot
$BeforeStatus = (Invoke-Git -Arguments @('status', '--porcelain=v1', '--untracked-files=all')) -join "`n"
if ($BeforeStatus) {
    throw "project-folder-checker worktree is not clean:`n$BeforeStatus"
}

$Branch = ((Invoke-Git -Arguments @('branch', '--show-current')) -join '').Trim()
if ($Branch -ne 'main') {
    throw "Expected project-folder-checker branch main, found: $Branch"
}

$BeforeHead = ((Invoke-Git -Arguments @('rev-parse', 'HEAD')) -join '').Trim().ToLowerInvariant()
$OldHeadNormalised = $ExpectedOldHead.ToLowerInvariant()
$NewHeadNormalised = $ExpectedNewHead.ToLowerInvariant()
if ($BeforeHead -notin @($OldHeadNormalised, $NewHeadNormalised)) {
    throw "Expected project-folder-checker HEAD $ExpectedOldHead or resumable HEAD $ExpectedNewHead, found $BeforeHead"
}

$Origin = ((Invoke-Git -Arguments @('config', '--get', 'remote.origin.url')) -join '').Trim()
$NormalisedOrigin = $Origin.TrimEnd('/')
if ($NormalisedOrigin.EndsWith('.git', [System.StringComparison]::OrdinalIgnoreCase) -eq $false) {
    $NormalisedOrigin += '.git'
}
if ($NormalisedOrigin -ne $ExpectedOrigin) {
    throw "Expected origin $ExpectedOrigin, found $Origin"
}

Write-Host 'Fetching exact authorised remote main...'
Invoke-Git -Arguments @('fetch', '--no-tags', 'origin', 'main') | Out-Null

$FetchedHead = ((Invoke-Git -Arguments @('rev-parse', 'origin/main')) -join '').Trim().ToLowerInvariant()
if ($FetchedHead -ne $NewHeadNormalised) {
    throw "Remote main moved. Expected $ExpectedNewHead, found $FetchedHead. No merge performed."
}

& git -C $RepositoryPath merge-base --is-ancestor $ExpectedOldHead $ExpectedNewHead
if ($LASTEXITCODE -ne 0) {
    throw 'The authorised update is not a fast-forward.'
}

$FastForwardApplied = $false
if ($BeforeHead -eq $OldHeadNormalised) {
    Write-Host 'Applying fast-forward only...'
    Invoke-Git -Arguments @('merge', '--ff-only', $ExpectedNewHead) | Out-Host
    $FastForwardApplied = $true
}
else {
    Write-Host 'Exact authorised fast-forward is already present; resuming Batch 0 validation.'
}

$AfterHead = ((Invoke-Git -Arguments @('rev-parse', 'HEAD')) -join '').Trim().ToLowerInvariant()
if ($AfterHead -ne $NewHeadNormalised) {
    throw "Fast-forward completed at unexpected HEAD: $AfterHead"
}
$AfterStatus = (Invoke-Git -Arguments @('status', '--porcelain=v1', '--untracked-files=all')) -join "`n"
if ($AfterStatus) {
    throw "project-folder-checker worktree is dirty after fast-forward:`n$AfterStatus"
}

$AfterHeads = Get-RepositoryHeads -Root $GitHubRoot
$UnexpectedHeadChanges = @()
foreach ($Path in $BeforeHeads.Keys) {
    if ($Path -eq $RepositoryPath) {
        continue
    }
    if (-not $AfterHeads.ContainsKey($Path)) {
        $UnexpectedHeadChanges += "$Path disappeared from the repository inventory"
        continue
    }
    if ($BeforeHeads[$Path] -ne $AfterHeads[$Path]) {
        $UnexpectedHeadChanges += "$Path changed from $($BeforeHeads[$Path]) to $($AfterHeads[$Path])"
    }
}
if ($UnexpectedHeadChanges.Count -gt 0) {
    throw "An unauthorised repository HEAD changed:`n$($UnexpectedHeadChanges -join [Environment]::NewLine)"
}

$Generated = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ssK')
$RegisterText = [System.IO.File]::ReadAllText($RegisterPath)
if ($RegisterText -notmatch 'source_audit_sha256: 386E0E2B79D7139D53A59491F96165469866D76F41DF842715176047CBB77844') {
    throw 'Migration register does not carry the authorised source-audit hash.'
}
$RegisterHash = (Get-FileHash -LiteralPath $RegisterPath -Algorithm SHA256).Hash
$ExceptionContent = @"
---
standard: Recursive Project Improvement Standard v1.0
role: project-control-exceptions
generated: $Generated
source_register: I:\ORDER\MainVault\00_Control\EXISTING_REPOSITORY_MIGRATION_REGISTER.md
source_register_sha256: $RegisterHash
source_audit_sha256: 386E0E2B79D7139D53A59491F96165469866D76F41DF842715176047CBB77844
---

# Project Control Exceptions

## External upstream — pewdiepie-archdaemon/odysseus

- Local path: I:\ORDER\GitHub\odysseus
- Remote: https://github.com/pewdiepie-archdaemon/odysseus.git
- Disposition: **EXTERNAL-UPSTREAM EXCEPTION**
- Ownership boundary: the remote is not under the armpitpete account.
- Migration boundary: do not modify, fork, migrate, branch, open a pull request, push, archive, rename or delete it under this programme.
- Audit interpretation: it may remain structurally UNMANAGED in the raw ownership-neutral audit, but it is excluded from the owned-repository migration queue.
- Re-entry gate: a separate explicit decision to adopt an owned fork or obtain upstream authority.

## Stop point

No action beyond this exception record is authorised for pewdiepie-archdaemon/odysseus.
"@
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
if (Test-Path -LiteralPath $ExceptionPath) {
    $ExistingException = [System.IO.File]::ReadAllText($ExceptionPath)
    if ($ExistingException -notmatch 'pewdiepie-archdaemon/odysseus' -or
        $ExistingException -notmatch 'EXTERNAL-UPSTREAM EXCEPTION') {
        throw "Existing exception file is not the authorised Batch 0 record: $ExceptionPath"
    }
    Write-Host "Existing authorised external-upstream exception retained: $ExceptionPath"
}
else {
    [System.IO.File]::WriteAllText($ExceptionPath, $ExceptionContent.TrimStart(), $Utf8NoBom)
    Write-Host "Recorded external-upstream exception: $ExceptionPath"
}

Write-Host 'Running central project-control audit...'
& $AuditRunner -GitHubRoot $GitHubRoot -OutputPath $AuditPath
if ($LASTEXITCODE -notin @(0, 2)) {
    throw "Central audit failed with exit code $LASTEXITCODE"
}
if (-not (Test-Path -LiteralPath $AuditPath)) {
    throw "Central audit did not write: $AuditPath"
}

$AuditText = [System.IO.File]::ReadAllText($AuditPath)
if ($AuditText -notmatch '(?m)^### CONTROLLED — `armpitpete/project-folder-checker`\s*$') {
    throw 'Rerun audit did not classify armpitpete/project-folder-checker as CONTROLLED.'
}
if ($AuditText -notmatch '(?m)^### UNMANAGED — `pewdiepie-archdaemon/odysseus`\s*$') {
    throw 'Rerun audit did not retain the raw structural result for pewdiepie-archdaemon/odysseus.'
}

$Counts = [ordered]@{
    CONTROLLED = Get-AuditCount -Text $AuditText -Classification 'CONTROLLED'
    BOOTSTRAP = Get-AuditCount -Text $AuditText -Classification 'BOOTSTRAP'
    DRIFTED = Get-AuditCount -Text $AuditText -Classification 'DRIFTED'
    UNMANAGED = Get-AuditCount -Text $AuditText -Classification 'UNMANAGED'
    BLOCKED = Get-AuditCount -Text $AuditText -Classification 'BLOCKED'
}

$AuditHash = (Get-FileHash -LiteralPath $AuditPath -Algorithm SHA256).Hash
$ExceptionHash = (Get-FileHash -LiteralPath $ExceptionPath -Algorithm SHA256).Hash
$ResultContent = @"
---
standard: Recursive Project Improvement Standard v1.0
role: existing-repository-migration-batch-result
batch: 0
generated: $Generated
target_repositories_changed: 1
other_repository_heads_changed: 0
---

# Existing-Repository Migration Batch 0 Result

## Authorised change

- Repository: armpitpete/project-folder-checker
- Local path: I:\ORDER\GitHub\project-folder-checker
- Before: $ExpectedOldHead
- After: $ExpectedNewHead
- Method: git merge --ff-only
- Fast-forward applied during this invocation: **$($FastForwardApplied.ToString().ToUpperInvariant())**
- Final branch: main
- Final worktree: **CLEAN**

## External-upstream exception

- Repository: pewdiepie-archdaemon/odysseus
- Disposition: **EXTERNAL-UPSTREAM EXCEPTION**
- Target-repository changes: **0**
- Exception record: $ExceptionPath
- Exception record SHA-256: $ExceptionHash

## Central audit rerun

- Audit: $AuditPath
- Audit SHA-256: $AuditHash
- CONTROLLED: $($Counts.CONTROLLED)
- BOOTSTRAP: $($Counts.BOOTSTRAP)
- DRIFTED: $($Counts.DRIFTED)
- UNMANAGED: $($Counts.UNMANAGED)
- BLOCKED: $($Counts.BLOCKED)
- armpitpete/project-folder-checker: **CONTROLLED**
- pewdiepie-archdaemon/odysseus: raw structural result retained; excluded from the owned migration queue by the exception record.

## Preservation proof

- Other repository HEADs changed: **0**
- No fork, migration, branch, PR, push or file change was made in pewdiepie-archdaemon/odysseus.

## Stop point

Batch 0 is complete. Stop before any other target-repository change.
"@
[System.IO.File]::WriteAllText($ResultPath, $ResultContent.TrimStart(), $Utf8NoBom)

Write-Host ''
Write-Host 'BATCH 0 PASSED'
Write-Host "project-folder-checker: $ExpectedOldHead -> $ExpectedNewHead (fast-forward only)"
Write-Host 'pewdiepie-archdaemon/odysseus: EXTERNAL-UPSTREAM EXCEPTION'
Write-Host "CONTROLLED=$($Counts.CONTROLLED)"
Write-Host "BOOTSTRAP=$($Counts.BOOTSTRAP)"
Write-Host "DRIFTED=$($Counts.DRIFTED)"
Write-Host "UNMANAGED=$($Counts.UNMANAGED)"
Write-Host "BLOCKED=$($Counts.BLOCKED)"
Write-Host 'OTHER_REPOSITORY_HEADS_CHANGED=0'
Write-Host "Result record: $ResultPath"
Write-Warning 'STOP: do not change any other target repository.'
