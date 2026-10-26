param([ValidateSet('desktop','mobile')][string]$Device='desktop')
$ErrorActionPreference='Stop'
$siteRoot=Split-Path -Parent $PSScriptRoot
$shotRoot=[IO.Path]::GetFullPath((Join-Path $siteRoot '.tmp-shots/shechem-env'))
$profile=Join-Path $shotRoot ('jos-shoot-env-'+[guid]::NewGuid().ToString('N'))
$port=if($Device -eq 'mobile'){9462}else{9461}
$prior=$env:JOS_CDP_EXTERNAL
New-Item -ItemType Directory -Path $profile -Force | Out-Null
$process=Start-Process -FilePath 'C:/Program Files/Google/Chrome/Application/chrome.exe' -ArgumentList @('--headless=new','--no-sandbox','--no-first-run','--no-default-browser-check','--hide-scrollbars','--mute-audio','--ignore-gpu-blocklist','--use-angle=d3d11',"--remote-debugging-port=$port","--user-data-dir=$profile",'about:blank') -WindowStyle Hidden -PassThru
Push-Location $siteRoot
try {
  $env:JOS_CDP_EXTERNAL='1'
  & node tools/shoot-shechem-env.mjs $Device
  if($LASTEXITCODE -ne 0){throw "Scene acceptance failed ($LASTEXITCODE)"}
} finally {
  $env:JOS_CDP_EXTERNAL=$prior
  if(-not $process.HasExited){Stop-Process -Id $process.Id -ErrorAction SilentlyContinue}
  $resolved=[IO.Path]::GetFullPath($profile)
  if((Split-Path -Parent $resolved) -eq $shotRoot -and (Split-Path -Leaf $resolved).StartsWith('jos-shoot-env-')){
    Start-Sleep -Milliseconds 300
    Remove-Item -LiteralPath $resolved -Recurse -Force -ErrorAction SilentlyContinue
  }
  Pop-Location
}
