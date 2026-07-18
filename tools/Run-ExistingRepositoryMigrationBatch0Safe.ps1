[CmdletBinding()]
param(
    [string]$GitHubRoot = 'I:\ORDER\GitHub',
    [string]$ControlRoot = 'I:\ORDER\MainVault\00_Control',
    [string]$ExpectedOldHead = '05ae228e79cb4d591d0e984387140d08a0cdc08d',
    [string]$ExpectedNewHead = '25cab54a0dea61d9a5e36041c2d6577fb8f2e614',
    [string]$CoreScript = (Join-Path $PSScriptRoot 'Run-ExistingRepositoryMigrationBatch0.ps1'),
    [switch]$LibraryOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function global:ConvertTo-Batch0NativeArgument {
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

function global:Invoke-Batch0NativeProcess {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory
    )

    $StartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $StartInfo.FileName = $FilePath
    $StartInfo.Arguments = (($Arguments | ForEach-Object { ConvertTo-Batch0NativeArgument -Argument $_ }) -join ' ')
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
        $StandardOutputTask = $Process.StandardOutput.ReadToEndAsync()
        $StandardErrorTask = $Process.StandardError.ReadToEndAsync()
        $Process.WaitForExit()
        return [pscustomobject]@{
            ExitCode = $Process.ExitCode
            StdOut = [string]$StandardOutputTask.GetAwaiter().GetResult()
            StdErr = [string]$StandardErrorTask.GetAwaiter().GetResult()
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
$global:Batch0RealGitExecutable = if ($GitCommand.Path) { $GitCommand.Path } else { $GitCommand.Source }

function global:git {
    $NativeArguments = @($args | ForEach-Object { [string]$_ })
    $Result = Invoke-Batch0NativeProcess `
        -FilePath $global:Batch0RealGitExecutable `
        -Arguments $NativeArguments `
        -WorkingDirectory (Get-Location).Path
    $global:LASTEXITCODE = $Result.ExitCode
    if ($Result.StdOut) {
        $Result.StdOut.TrimEnd("`r", "`n")
    }
    if ($Result.StdErr) {
        $Result.StdErr.TrimEnd("`r", "`n")
    }
}

if ($LibraryOnly) {
    return
}
if (-not (Test-Path -LiteralPath $CoreScript)) {
    throw "Batch 0 core script does not exist: $CoreScript"
}

try {
    & $CoreScript `
        -GitHubRoot $GitHubRoot `
        -ControlRoot $ControlRoot `
        -ExpectedOldHead $ExpectedOldHead `
        -ExpectedNewHead $ExpectedNewHead
}
finally {
    Remove-Item Function:\global:git -ErrorAction SilentlyContinue
    Remove-Item Function:\global:ConvertTo-Batch0NativeArgument -ErrorAction SilentlyContinue
    Remove-Item Function:\global:Invoke-Batch0NativeProcess -ErrorAction SilentlyContinue
    Remove-Variable Batch0RealGitExecutable -Scope Global -ErrorAction SilentlyContinue
}
