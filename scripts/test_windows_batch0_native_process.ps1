Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. .\tools\Run-ExistingRepositoryMigrationBatch0Safe.ps1 -LibraryOnly

$PowerShellExecutable = (Get-Process -Id $PID).Path
$WorkingDirectory = (Get-Location).Path

$Success = Invoke-Batch0NativeProcess `
    -FilePath $PowerShellExecutable `
    -Arguments @(
        '-NoProfile',
        '-Command',
        '[Console]::Out.WriteLine("stdout-success"); [Console]::Error.WriteLine("stderr-success"); exit 0'
    ) `
    -WorkingDirectory $WorkingDirectory

if ($Success.ExitCode -ne 0) {
    throw "Expected success exit 0, found $($Success.ExitCode)."
}
if ($Success.StdOut.Trim() -ne 'stdout-success') {
    throw "Expected captured stdout-success, found: $($Success.StdOut)"
}
if ($Success.StdErr.Trim() -ne 'stderr-success') {
    throw "Expected captured stderr-success, found: $($Success.StdErr)"
}

$Failure = Invoke-Batch0NativeProcess `
    -FilePath $PowerShellExecutable `
    -Arguments @(
        '-NoProfile',
        '-Command',
        '[Console]::Error.WriteLine("stderr-failure"); exit 7'
    ) `
    -WorkingDirectory $WorkingDirectory

if ($Failure.ExitCode -ne 7) {
    throw "Expected failure exit 7, found $($Failure.ExitCode)."
}
if ($Failure.StdErr.Trim() -ne 'stderr-failure') {
    throw "Expected captured stderr-failure, found: $($Failure.StdErr)"
}

Write-Host 'PASS: Batch 0 native process wrapper captures successful stderr without PowerShell NativeCommandError termination.'
