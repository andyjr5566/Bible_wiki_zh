param([ValidateSet('desktop','mobile')][string]$Device='desktop',[switch]$InteractionsOnly)
$ErrorActionPreference='Stop'
$siteRoot=Split-Path -Parent $PSScriptRoot
$tempRoot=[IO.Path]::GetFullPath((Join-Path $siteRoot '.tmp-shots/act2'))
$profile=Join-Path $tempRoot ('jos-shoot-act2-'+[guid]::NewGuid().ToString('N'))
$port=if($Device -eq 'mobile'){9452}else{9451}
$prior=$env:JOS_CDP_EXTERNAL
$priorInteractions=$env:JOS_ACT2_INTERACTIONS_ONLY
New-Item -ItemType Directory -Path $profile -Force | Out-Null
$process=Start-Process -FilePath 'C:/Program Files/Google/Chrome/Application/chrome.exe' -ArgumentList @('--headless=new','--no-sandbox','--no-first-run','--no-default-browser-check','--hide-scrollbars','--mute-audio','--ignore-gpu-blocklist','--use-angle=d3d11','--enable-gpu-rasterization',"--remote-debugging-port=$port","--user-data-dir=$profile",'about:blank') -WindowStyle Hidden -PassThru
Push-Location $siteRoot
try {
  $env:JOS_CDP_EXTERNAL='1'
  if($InteractionsOnly){$env:JOS_ACT2_INTERACTIONS_ONLY='1'}
  & node tools/shoot-act2.mjs $Device
  if($LASTEXITCODE -ne 0){throw "Act 2 acceptance failed ($LASTEXITCODE)"}
} finally {
  $env:JOS_CDP_EXTERNAL=$prior
  $env:JOS_ACT2_INTERACTIONS_ONLY=$priorInteractions
  if(-not $process.HasExited){Stop-Process -Id $process.Id -ErrorAction SilentlyContinue}
  $resolved=[IO.Path]::GetFullPath($profile)
  if((Split-Path -Parent $resolved) -eq $tempRoot -and (Split-Path -Leaf $resolved).StartsWith('jos-shoot-act2-')) {
    Start-Sleep -Milliseconds 300
    Remove-Item -LiteralPath $resolved -Recurse -Force -ErrorAction SilentlyContinue
  }
  Pop-Location
}
