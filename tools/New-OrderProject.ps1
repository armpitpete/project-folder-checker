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
    [string]$Template = 'armpitpete/project-template',
    [string]$GitHubRoot = 'I:\ORDER\GitHub',
    [string]$AuditOutput = 'I:\ORDER\MainVault\00_Control\PROJECT_CONTROL_AUDIT.md'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Require-Command {
    param([Parameter(Mandatory = $true)][string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command is unavailable: $Name"
    }
}

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [string]$FailureMessage = 'Command failed.'
    )
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$FailureMessage Exit code: $LASTEXITCODE"
    }
}

function Resolve-Python {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @{ Command = 'py'; Prefix = @('-3') }
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @{ Command = 'python'; Prefix = @() }
    }
    throw 'Python 3 is required but neither py nor python is available.'
}

function Invoke-Python {
    param(
        [Parameter(Mandatory = $true)][hashtable]$Python,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [string]$FailureMessage = 'Python command failed.'
    )
    $AllArguments = @($Python.Prefix) + $Arguments
    Invoke-Checked -Command $Python.Command -Arguments $AllArguments -FailureMessage $FailureMessage
}

Require-Command -Name 'gh'
Require-Command -Name 'git'
$Python = Resolve-Python

if ($Template -ne 'armpitpete/project-template') {
    throw "Refusing non-authoritative template: $Template"
}

Invoke-Checked -Command 'gh' -Arguments @('auth', 'status') `
    -FailureMessage 'GitHub CLI is not authenticated.'

$TemplateIsTemplate = (& gh api "repos/$Template" --jq '.is_template').Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Could not inspect authoritative template repository: $Template"
}
if ($TemplateIsTemplate -ne 'true') {
    throw "Authoritative repository is not enabled as a GitHub template: $Template"
}

$FullRepository = "$Owner/$RepositoryName"
$TargetDirectory = Join-Path $GitHubRoot $RepositoryName

if (-not (Test-Path $GitHubRoot)) {
    New-Item -ItemType Directory -Force -Path $GitHubRoot | Out-Null
}
if (Test-Path $TargetDirectory) {
    throw "Local target already exists: $TargetDirectory"
}

& gh repo view $FullRepository --json nameWithOwner *> $null
if ($LASTEXITCODE -eq 0) {
    throw "Remote repository already exists: $FullRepository"
}

$VisibilityFlag = if ($Visibility -eq 'private') { '--private' } else { '--public' }
$RemoteCreated = $false

try {
    Push-Location $GitHubRoot
    try {
        Invoke-Checked -Command 'gh' -Arguments @(
            'repo', 'create', $FullRepository,
            '--template', $Template,
            $VisibilityFlag,
            '--clone'
        ) -FailureMessage 'Repository creation from the mandatory template failed.'
        $RemoteCreated = $true
    }
    finally {
        Pop-Location
    }

    if (-not (Test-Path (Join-Path $TargetDirectory '.git'))) {
        throw "Repository was not cloned into the required location: $TargetDirectory"
    }

    Push-Location $TargetDirectory
    try {
        $Origin = (& git remote get-url origin).Trim()
        if ($LASTEXITCODE -ne 0 -or $Origin -notmatch [regex]::Escape("$Owner/$RepositoryName")) {
            throw "Cloned origin does not match $FullRepository. Found: $Origin"
        }

        Invoke-Python -Python $Python -Arguments @(
            'scripts\initialise_project.py',
            '--repository', $FullRepository,
            '--project-name', $ProjectName,
            '--project-type', $ProjectType
        ) -FailureMessage 'Template initialization failed.'

        Invoke-Python -Python $Python -Arguments @(
            'scripts\validate_project_control.py',
            '--repository', $FullRepository
        ) -FailureMessage 'Generated repository validation failed before commit.'

        $ExpectedChanges = @(
            'STATUS.md',
            'docs/authority/AUTHORITY.md'
        ) | Sort-Object

        $ActualChanges = @(
            & git status --porcelain=v1 --untracked-files=all |
                ForEach-Object {
                    if ($_.Length -ge 4) { $_.Substring(3).Trim() }
                } |
                Where-Object { $_ } |
                Sort-Object
        )

        if (Compare-Object -ReferenceObject $ExpectedChanges -DifferenceObject $ActualChanges) {
            throw (
                "Initialization changed files outside the exact contract.`n" +
                "Expected: $($ExpectedChanges -join ', ')`n" +
                "Actual: $($ActualChanges -join ', ')"
            )
        }

        Invoke-Checked -Command 'git' -Arguments @(
            'add', '--', 'STATUS.md', 'docs/authority/AUTHORITY.md'
        ) -FailureMessage 'Failed to stage initialized authority files.'

        Invoke-Checked -Command 'git' -Arguments @('diff', '--cached', '--check') `
            -FailureMessage 'Staged initialization diff failed git diff --check.'

        Invoke-Checked -Command 'git' -Arguments @(
            'commit', '-m', 'Initialise project authority'
        ) -FailureMessage 'Failed to commit initialized authority state.'

        Invoke-Checked -Command 'git' -Arguments @('push', 'origin', 'main') `
            -FailureMessage 'Failed to push initialized authority state.'

        Invoke-Python -Python $Python -Arguments @(
            'scripts\validate_project_control.py',
            '--repository', $FullRepository
        ) -FailureMessage 'Generated repository validation failed after push.'

        $Dirty = (& git status --porcelain=v1 --untracked-files=all)
        if ($LASTEXITCODE -ne 0) {
            throw 'Could not verify final working-tree state.'
        }
        if ($Dirty) {
            throw "Generated repository is not clean after push:`n$($Dirty -join "`n")"
        }

        $Head = (& git rev-parse HEAD).Trim()
        if ($LASTEXITCODE -ne 0) {
            throw 'Could not resolve generated repository head.'
        }
    }
    finally {
        Pop-Location
    }

    $AuditRunner = Join-Path $PSScriptRoot 'Run-ProjectControlAudit.ps1'
    if (Test-Path $AuditRunner) {
        & $AuditRunner -GitHubRoot $GitHubRoot -OutputPath $AuditOutput
        if ($LASTEXITCODE -notin @(0, 2)) {
            throw 'Repository was created, but the cross-project audit failed.'
        }
    }

    Write-Host ''
    Write-Host 'PROJECT CREATED AND CONTROLLED'
    Write-Host "Repository: $FullRepository"
    Write-Host "Local path: $TargetDirectory"
    Write-Host "Head: $Head"
    Write-Host 'State: BOOTSTRAP'
    Write-Host 'Next bounded gate: assess and inventory source material without modifying it.'
}
catch {
    Write-Error $_
    if ($RemoteCreated) {
        Write-Warning 'The remote repository and local clone have been preserved for diagnosis.'
        Write-Warning "Automatic deletion is prohibited: $FullRepository"
    }
    throw
}
