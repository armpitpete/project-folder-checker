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
$ExpectedOrigin = 'https://github.com/armpitpete/project-folder-checker.git'

function ConvertTo-NativeArgument {
    param([AllowEmptyString()][string]$Argument)

    if ($null -eq $Argument -or $Argument.Length -eq 0) {
        return '""'
    }
    if ($Argument -notmatch '[\s"]') {
        return $Argument
    }

    $Builder = New-Object System.Text.StringBuilder
    [void]$Builder.Append([char]34)
    $Backslashes = 0
    foreach ($Character in $Argument.ToCharArray()) {
        if ($Character -eq [char]92) {
            $Backslashes++
            continue
        }
        if ($Character -eq [char]34) {
            if ($Backslashes -gt 0) {
                [void]$Builder.Append([char]92, ($Backslashes * 2))
            }
            [void]$Builder.Append([char]92)
            [void]$Builder.Append([char]34)
            $Backslashes = 0
            continue
        }
        if ($Backslashes -gt 0) {
            [void]$Builder.Append([char]92, $Backslashes)
            $Backslashes = 0
        }
        [void]$Builder.Append($Character)
    }
    if ($Backslashes -gt 0) {
        [void]$Builder.Append([char]92, ($Backslashes * 2))
    }
    [void]$Builder.Append([char]34)
    return $Builder.ToString()
}

function Invoke-NativeProcess {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory
    )

    $StartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $StartInfo.FileName = $FilePath
    $StartInfo.Arguments = (($Arguments | ForEach-Object { ConvertTo-NativeArgument -Argument $_ }) -join ' ')
    $StartInfo.WorkingDirectory = $WorkingDirectory
    $StartInfo.UseShellExecute = $false
    $StartInfo.RedirectStandardOutput = $true
    $StartInfo.RedirectStandardError = $true
    $StartInfo.CreateNoWindow = $true
    $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    $StartInfo.StandardOutputEncoding = $Utf8NoBom
    $StartInfo.StandardErrorEncoding = $Utf8NoBom

    $Process = New-Object System.Diagnostics.Process
    $Process.StartInfo = $StartInfo
    try {
        if (-not $Process.Start()) {
            throw "Could not start native process: $FilePath"
        }
        $StdOutTask = $Process.StandardOutput.ReadToEndAsync()
        $StdErrTask = $Process.StandardError.ReadToEndAsync()
        $Process.WaitForExit()
        return [pscustomobject]@{
            ExitCode = $Process.ExitCode
            StdOut = [string]$StdOutTask.GetAwaiter().GetResult()
            StdErr = [string]$StdErrTask.GetAwaiter().GetResult()
        }
    }
    finally {
        $Process.Dispose()
    }
}

$GitCommand = Get-Command git.exe -ErrorAction SilentlyContinue
if ($null -eq $GitCommand) {
    $GitCommand = Get-Command git -CommandType Application -ErrorAction SilentlyContinue
}
if ($null -eq $GitCommand) {
    throw 'Git executable is required.'
}
$GitExecutable = if ($GitCommand.Path) { $GitCommand.Path } else { $GitCommand.Source }

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [string]$WorkingDirectory = $RepositoryPath,
        [switch]$AllowNonZero
    )

    $NativeArguments = @('-C', $WorkingDirectory) + $Arguments
    $Result = Invoke-NativeProcess -FilePath $GitExecutable -Arguments $NativeArguments -WorkingDirectory $WorkingDirectory
    if (-not $AllowNonZero -and $Result.ExitCode -ne 0) {
        throw "git $($Arguments -join ' ') failed with exit $($Result.ExitCode):`n$($Result.StdErr)$($Result.StdOut)"
    }
    return $Result
}

function Get-RepositoryHeads {
    param([string]$Root)

    $Heads = @{}
    foreach ($Directory in Get-ChildItem -LiteralPath $Root -Directory) {
        if (-not (Test-Path -LiteralPath (Join-Path $Directory.FullName '.git'))) {
            continue
        }
        $Result = Invoke-Git -Arguments @('rev-parse', 'HEAD') -WorkingDirectory $Directory.FullName -AllowNonZero
        if ($Result.ExitCode -eq 0 -and $Result.StdOut.Trim()) {
            $Heads[$Directory.FullName] = $Result.StdOut.Trim().ToLowerInvariant()
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

foreach ($RequiredPath in @($RepositoryPath, $AuditRunner, $ExceptionPath)) {
    if (-not (Test-Path -LiteralPath $RequiredPath)) {
        throw "Required Batch 0 path does not exist: $RequiredPath"
    }
}

$BeforeHeads = Get-RepositoryHeads -Root $GitHubRoot

$Branch = (Invoke-Git -Arguments @('branch', '--show-current')).StdOut.Trim()
if ($Branch -ne 'main') {
    throw "Expected project-folder-checker branch main, found: $Branch"
}

$Head = (Invoke-Git -Arguments @('rev-parse', 'HEAD')).StdOut.Trim().ToLowerInvariant()
if ($Head -ne $ExpectedNewHead.ToLowerInvariant()) {
    throw "Expected completed Batch 0 head $ExpectedNewHead, found: $Head"
}

$Status = (Invoke-Git -Arguments @('status', '--porcelain=v1', '--untracked-files=all')).StdOut.Trim()
if ($Status) {
    throw "project-folder-checker worktree is not clean:`n$Status"
}

$Origin = (Invoke-Git -Arguments @('config', '--get', 'remote.origin.url')).StdOut.Trim()
$NormalisedOrigin = $Origin.TrimEnd('/')
if (-not $NormalisedOrigin.EndsWith('.git', [System.StringComparison]::OrdinalIgnoreCase)) {
    $NormalisedOrigin += '.git'
}
if ($NormalisedOrigin -ne $ExpectedOrigin) {
    throw "Expected origin $ExpectedOrigin, found: $Origin"
}

$RemoteTrackingHead = (Invoke-Git -Arguments @('rev-parse', 'origin/main')).StdOut.Trim().ToLowerInvariant()
if ($RemoteTrackingHead -ne $ExpectedNewHead.ToLowerInvariant()) {
    throw "Expected origin/main $ExpectedNewHead, found: $RemoteTrackingHead"
}

$Ancestor = Invoke-Git -Arguments @('merge-base', '--is-ancestor', $ExpectedOldHead, $ExpectedNewHead) -AllowNonZero
if ($Ancestor.ExitCode -ne 0) {
    throw 'The authorised old head is not an ancestor of the authorised new head.'
}

$ExceptionText = [System.IO.File]::ReadAllText($ExceptionPath)
if ($ExceptionText -notmatch 'pewdiepie-archdaemon/odysseus' -or
    $ExceptionText -notmatch 'EXTERNAL-UPSTREAM EXCEPTION') {
    throw "The external-upstream exception record is missing or invalid: $ExceptionPath"
}

Write-Host 'Rerunning central project-control audit for Batch 0 completion...'
& $AuditRunner -GitHubRoot $GitHubRoot -OutputPath $AuditPath
if ($LASTEXITCODE -notin @(0, 2)) {
    throw "Central audit failed with exit code $LASTEXITCODE"
}
if (-not (Test-Path -LiteralPath $AuditPath)) {
    throw "Central audit did not write: $AuditPath"
}

$AuditText = [System.IO.File]::ReadAllText($AuditPath)

# ASCII-only table matching avoids Windows PowerShell 5.1 source-decoding problems
# with the non-ASCII dash used in the Findings headings.
$ControlledRow = '(?m)^\| CONTROLLED \| `armpitpete/project-folder-checker` \|'
if ($AuditText -notmatch $ControlledRow) {
    throw 'Rerun audit table did not classify armpitpete/project-folder-checker as CONTROLLED.'
}
$ExternalRow = '(?m)^\| UNMANAGED \| `pewdiepie-archdaemon/odysseus` \|'
if ($AuditText -notmatch $ExternalRow) {
    throw 'Rerun audit table did not retain pewdiepie-archdaemon/odysseus as structurally UNMANAGED.'
}

$Counts = [ordered]@{
    CONTROLLED = Get-AuditCount -Text $AuditText -Classification 'CONTROLLED'
    BOOTSTRAP = Get-AuditCount -Text $AuditText -Classification 'BOOTSTRAP'
    DRIFTED = Get-AuditCount -Text $AuditText -Classification 'DRIFTED'
    UNMANAGED = Get-AuditCount -Text $AuditText -Classification 'UNMANAGED'
    BLOCKED = Get-AuditCount -Text $AuditText -Classification 'BLOCKED'
}

$AfterHeads = Get-RepositoryHeads -Root $GitHubRoot
$UnexpectedHeadChanges = @()
foreach ($Path in $BeforeHeads.Keys) {
    if (-not $AfterHeads.ContainsKey($Path)) {
        $UnexpectedHeadChanges += "$Path disappeared from the repository inventory"
        continue
    }
    if ($BeforeHeads[$Path] -ne $AfterHeads[$Path]) {
        $UnexpectedHeadChanges += "$Path changed from $($BeforeHeads[$Path]) to $($AfterHeads[$Path])"
    }
}
if ($UnexpectedHeadChanges.Count -gt 0) {
    throw "A repository HEAD changed during Batch 0 completion validation:`n$($UnexpectedHeadChanges -join [Environment]::NewLine)"
}

$Generated = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ssK')
$AuditHash = (Get-FileHash -LiteralPath $AuditPath -Algorithm SHA256).Hash
$ExceptionHash = (Get-FileHash -LiteralPath $ExceptionPath -Algorithm SHA256).Hash
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

$ResultContent = @"
---
standard: Recursive Project Improvement Standard v1.0
role: existing-repository-migration-batch-result
batch: 0
generated: $Generated
target_repositories_changed: 1
other_repository_heads_changed: 0
completion_mode: resumed-after-proof-parser-failure
---

# Existing-Repository Migration Batch 0 Result

## Authorised local synchronisation

- Repository: armpitpete/project-folder-checker
- Local path: I:\ORDER\GitHub\project-folder-checker
- Authorised old head: $ExpectedOldHead
- Final head: $ExpectedNewHead
- Branch: main
- Worktree: CLEAN
- Fast-forward relationship: VERIFIED
- Completion mode: resumed after the original runner completed the fast-forward, exception record and audit but failed its non-ASCII heading assertion.

## External-upstream exception

- Repository: pewdiepie-archdaemon/odysseus
- Disposition: EXTERNAL-UPSTREAM EXCEPTION
- Target-repository changes: 0
- Exception record: $ExceptionPath
- Exception record SHA-256: $ExceptionHash

## Central audit

- Audit: $AuditPath
- Audit SHA-256: $AuditHash
- CONTROLLED: $($Counts.CONTROLLED)
- BOOTSTRAP: $($Counts.BOOTSTRAP)
- DRIFTED: $($Counts.DRIFTED)
- UNMANAGED: $($Counts.UNMANAGED)
- BLOCKED: $($Counts.BLOCKED)
- armpitpete/project-folder-checker: CONTROLLED
- pewdiepie-archdaemon/odysseus: structurally UNMANAGED and excluded from the owned migration queue by the central exception record.

## Preservation proof

- Repository HEADs changed during this completion invocation: 0
- No additional target-repository change was made.
- No modification, fork, migration, branch, pull request, push, archive, rename or deletion was performed for pewdiepie-archdaemon/odysseus.

## Stop point

Batch 0 is complete. Stop before any Batch 1 or other target-repository action.
"@

[System.IO.File]::WriteAllText($ResultPath, $ResultContent.TrimStart(), $Utf8NoBom)

Write-Host ''
Write-Host 'BATCH 0 PASSED'
Write-Host "project-folder-checker: $ExpectedNewHead (CONTROLLED)"
Write-Host 'pewdiepie-archdaemon/odysseus: EXTERNAL-UPSTREAM EXCEPTION'
Write-Host "CONTROLLED=$($Counts.CONTROLLED)"
Write-Host "BOOTSTRAP=$($Counts.BOOTSTRAP)"
Write-Host "DRIFTED=$($Counts.DRIFTED)"
Write-Host "UNMANAGED=$($Counts.UNMANAGED)"
Write-Host "BLOCKED=$($Counts.BLOCKED)"
Write-Host 'OTHER_REPOSITORY_HEADS_CHANGED=0'
Write-Host "Result: $ResultPath"
Write-Warning 'STOP: Batch 0 is complete. No Batch 1 action is authorised.'
