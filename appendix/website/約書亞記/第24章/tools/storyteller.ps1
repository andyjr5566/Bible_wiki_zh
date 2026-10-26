param([ValidateSet('before','after','notes')][string]$Phase='after')
$ErrorActionPreference='Stop'
$siteRoot=Split-Path -Parent $PSScriptRoot
$shotRoot=[IO.Path]::GetFullPath((Join-Path $siteRoot '.tmp-shots/storyteller'))
$profile=Join-Path $shotRoot ('jos-shoot-story-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $profile -Force | Out-Null
$process=Start-Process -FilePath 'C:/Program Files/Google/Chrome/Application/chrome.exe' -ArgumentList @('--headless=new','--no-sandbox','--no-first-run','--no-default-browser-check','--hide-scrollbars','--mute-audio','--ignore-gpu-blocklist','--use-angle=d3d11','--disable-background-timer-throttling','--disable-renderer-backgrounding','--remote-debugging-port=9471',"--user-data-dir=$profile",'about:blank') -WindowStyle Hidden -PassThru
$prior=$env:JOS_CDP_EXTERNAL
Push-Location $siteRoot
try {
  $env:JOS_CDP_EXTERNAL='1'
  if($Phase -eq 'before'){ & node tools/measure-storyteller-before.mjs }
  elseif($Phase -eq 'notes'){ & node tools/check-storyteller-notes.mjs }
  else { & node tools/accept-storyteller.mjs }
  if($LASTEXITCODE -ne 0){throw "Story acceptance failed ($LASTEXITCODE)"}
} finally {
  $env:JOS_CDP_EXTERNAL=$prior
  if(-not $process.HasExited){Stop-Process -Id $process.Id -ErrorAction SilentlyContinue}
  $resolved=[IO.Path]::GetFullPath($profile)
  if((Split-Path -Parent $resolved) -eq $shotRoot -and (Split-Path -Leaf $resolved).StartsWith('jos-shoot-story-')){
    Start-Sleep -Milliseconds 300
    Remove-Item -LiteralPath $resolved -Recurse -Force -ErrorAction SilentlyContinue
  }
  Pop-Location
}
