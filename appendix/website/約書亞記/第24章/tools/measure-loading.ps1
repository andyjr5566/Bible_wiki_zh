param([string]$Url = '', [string]$Script = 'tools/measure-loading.mjs')
$ErrorActionPreference = 'Stop'
$siteRoot = Split-Path -Parent $PSScriptRoot
$profile = Join-Path $siteRoot ('.tmp-shots/loading/jos-shoot-loading-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $profile | Out-Null
$process = Start-Process -FilePath 'C:/Program Files/Google/Chrome/Application/chrome.exe' -ArgumentList @('--headless=new','--no-sandbox','--no-first-run','--no-default-browser-check','--hide-scrollbars','--mute-audio','--ignore-gpu-blocklist','--use-angle=d3d11','--disable-background-timer-throttling','--disable-renderer-backgrounding','--remote-debugging-port=9483',"--user-data-dir=$profile",'about:blank') -WindowStyle Hidden -PassThru
$prior = $env:JOS_CDP_EXTERNAL
$priorUrl = $env:JOS_URL
Push-Location $siteRoot
try {
  $env:JOS_CDP_EXTERNAL = '1'
  if ($Url) { $env:JOS_URL = $Url }
  & node $Script
  if ($LASTEXITCODE -ne 0) { throw "Loading checks failed ($LASTEXITCODE)" }
} finally {
  $env:JOS_CDP_EXTERNAL = $prior
  $env:JOS_URL = $priorUrl
  if (-not $process.HasExited) { Stop-Process -Id $process.Id -ErrorAction SilentlyContinue }
  Pop-Location
}
