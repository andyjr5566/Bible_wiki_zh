param([ValidateSet('desktop','mobile','extra')][string]$Device = 'desktop', [switch]$All)
$ErrorActionPreference = 'Stop'
$siteRoot = Split-Path -Parent $PSScriptRoot
$tempRoot = [IO.Path]::GetFullPath((Join-Path $siteRoot '.tmp-shots/onevoice'))
$owned = @()
$priorExternal = $env:JOS_CDP_EXTERNAL
Push-Location $siteRoot
try {
  $ports = if ($Device -eq 'desktop') { @(9401) } elseif ($Device -eq 'mobile') { @(9402) } else { @(9421,9422,9423,9424,9426,9427) }
  foreach ($port in $ports) {
    $profile = Join-Path $tempRoot ('jos-shoot-onevoice-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $profile -Force | Out-Null
    $process = Start-Process -FilePath 'C:/Program Files/Google/Chrome/Application/chrome.exe' -ArgumentList @(
      '--headless=new','--no-sandbox','--no-first-run','--no-default-browser-check','--hide-scrollbars','--mute-audio',
      "--remote-debugging-port=$port","--user-data-dir=$profile",'about:blank'
    ) -WindowStyle Hidden -PassThru
    $owned += @{path=$profile;process=$process}
  }
  $env:JOS_CDP_EXTERNAL = '1'
  if ($Device -eq 'extra') { & node tools/shoot-onevoice-extra.mjs }
  elseif ($All) { & node tools/shoot-onevoice.mjs $Device all }
  else { & node tools/shoot-onevoice.mjs $Device }
  if ($LASTEXITCODE -ne 0) { throw "CDP acceptance failed ($LASTEXITCODE)" }
} finally {
  $env:JOS_CDP_EXTERNAL = $priorExternal
  foreach ($item in $owned) {
    if (-not $item.process.HasExited) { Stop-Process -Id $item.process.Id -ErrorAction SilentlyContinue }
    $resolved = [IO.Path]::GetFullPath($item.path)
    if ((Split-Path -Parent $resolved) -eq $tempRoot -and (Split-Path -Leaf $resolved).StartsWith('jos-shoot-onevoice-')) {
      Start-Sleep -Milliseconds 300
      Remove-Item -LiteralPath $resolved -Recurse -Force -ErrorAction SilentlyContinue
    }
  }
  Pop-Location
}
