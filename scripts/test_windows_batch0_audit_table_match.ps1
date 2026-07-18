Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$AuditText = @'
## Repository results

| Classification | Repository | Declared status | Work blocked | Validator |
|---|---|---|---|---|
| CONTROLLED | `armpitpete/project-folder-checker` | AUTHORITATIVE | NO | pass |
| UNMANAGED | `pewdiepie-archdaemon/odysseus` | - | YES | not run |

## Findings
'@

$ControlledRow = '(?m)^\| CONTROLLED \| `armpitpete/project-folder-checker` \|'
if ($AuditText -notmatch $ControlledRow) {
    throw 'ASCII-only CONTROLLED table match failed.'
}

$ExternalRow = '(?m)^\| UNMANAGED \| `pewdiepie-archdaemon/odysseus` \|'
if ($AuditText -notmatch $ExternalRow) {
    throw 'ASCII-only external-upstream table match failed.'
}

$Bytes = [System.IO.File]::ReadAllBytes((Resolve-Path '.\tools\Run-ExistingRepositoryMigrationBatch0Resume.ps1'))
if ($Bytes | Where-Object { $_ -gt 127 }) {
    throw 'Resume-only Batch 0 script must remain ASCII-only for Windows PowerShell 5.1.'
}

Write-Host 'PASS: Batch 0 resume audit matching is ASCII-only and Windows PowerShell 5.1 safe.'
