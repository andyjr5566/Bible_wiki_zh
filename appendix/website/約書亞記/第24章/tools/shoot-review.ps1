param([string]$OutputDirectory = '.tmp-shots/review', [ValidateSet('all','desk','land','port')][string]$Device = 'all', [switch]$LabelsOnly)
$ErrorActionPreference = 'Stop'
$siteRoot = Split-Path -Parent $PSScriptRoot
$tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
$owned = @()
$previousProfiles = $env:JOS_REVIEW_OWNED_PROFILES
Push-Location $siteRoot
try {
  foreach ($item in @(@{name='desk';port=9374},@{name='land';port=9375},@{name='port';port=9376})) {
    if ($Device -ne 'all' -and $Device -ne $item.name) { continue }
    $probe = [Net.Sockets.TcpClient]::new()
    try {
      if ($probe.ConnectAsync('127.0.0.1', $item.port).Wait(200) -and $probe.Connected) { throw "Port $($item.port) is already in use" }
    } catch [AggregateException] { } finally { $probe.Dispose() }
    $profile = Join-Path $tempRoot ('jos-shoot-review-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $profile | Out-Null
    $process = Start-Process -FilePath 'C:/Program Files/Google/Chrome/Application/chrome.exe' -ArgumentList @(
      '--headless=new','--no-first-run','--no-default-browser-check','--hide-scrollbars','--mute-audio',
      "--remote-debugging-port=$($item.port)","--user-data-dir=$profile",'about:blank'
    ) -WindowStyle Hidden -PassThru
    $owned += @{port=$item.port;path=$profile;process=$process}
  }
  $env:JOS_REVIEW_OWNED_PROFILES = ConvertTo-Json -Compress -InputObject @($owned | ForEach-Object { @{port=$_.port;path=$_.path} })
  if ($LabelsOnly) { & node tools/shoot-review.mjs $OutputDirectory $Device labels }
  else { & node tools/shoot-review.mjs $OutputDirectory $Device }
  if ($LASTEXITCODE -ne 0) { throw "CDP acceptance failed ($LASTEXITCODE)" }
} finally {
  $env:JOS_REVIEW_OWNED_PROFILES = $previousProfiles
  foreach ($item in $owned) {
    if (-not $item.process.HasExited) { Stop-Process -Id $item.process.Id -ErrorAction SilentlyContinue }
    $resolved = [IO.Path]::GetFullPath($item.path)
    if ($resolved.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase) -and (Split-Path -Leaf $resolved).StartsWith('jos-shoot-review-')) {
      Remove-Item -LiteralPath $resolved -Recurse -Force -ErrorAction SilentlyContinue
    }
  }
  Pop-Location
}
