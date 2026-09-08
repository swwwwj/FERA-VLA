param(
    [Parameter(Mandatory=$true)][string]$RemoteHost,
    [Parameter(Mandatory=$true)][string]$RemotePath,
    [string]$GitProxy = ""
)
$ErrorActionPreference = "Stop"
# Authentication is supplied by the caller's SSH config/agent/askpass environment.
if ($RemoteHost -notmatch '^[a-zA-Z0-9@._-]+$' -or $RemotePath -notmatch '^/[a-zA-Z0-9/_-]+$') {
    throw "Unsupported SSH host/path characters"
}
function Assert-Exit { if ($LASTEXITCODE -ne 0) { throw "Command failed: $LASTEXITCODE" } }
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    $dirty = git status --porcelain
    Assert-Exit
    if ($dirty) { throw "Local changes present; commit or preserve them before synchronization" }
    $bundleName = "fera-" + [guid]::NewGuid().ToString("N") + ".bundle"
    $bundle = Join-Path $env:TEMP $bundleName
    # Remote author commits first. Export Git history, not a destructive directory mirror.
    $remoteCommand = 'cd {0} && test -z "$(git status --porcelain)" && git bundle create /tmp/{1} main' -f $RemotePath, $bundleName
    ssh $RemoteHost $remoteCommand
    Assert-Exit
    scp "${RemoteHost}:/tmp/$bundleName" $bundle
    Assert-Exit
    git bundle verify $bundle
    Assert-Exit
    git fetch $bundle main
    Assert-Exit
    git merge --ff-only FETCH_HEAD
    Assert-Exit
    $gitArgs = @()
    if ($GitProxy) { $gitArgs += @("-c","http.proxy=$GitProxy") }
    & git @gitArgs push origin main
    Assert-Exit
    git rev-parse HEAD
} finally { Pop-Location }
