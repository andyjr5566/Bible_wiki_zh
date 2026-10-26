param([ValidateSet('opening','speed')][string]$Suite='opening')
$ErrorActionPreference='Stop'
$siteRoot=Split-Path -Parent $PSScriptRoot
$cases=if($Suite -eq 'opening'){@('desktop normal','mobile normal','desktop slow','mobile slow')}else{@('desktop','mobile')}
$prior=$env:JOS_CDP_EXTERNAL
Push-Location $siteRoot
try {
  foreach($case in $cases){
    $profile=Join-Path $siteRoot ('.tmp-shots/regress/profile-'+[guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Force -Path $profile | Out-Null
    if(Get-NetTCPConnection -LocalPort 9484 -State Listen -ErrorAction SilentlyContinue){throw 'Port 9484 is already in use; finish the other regression run first.'}
    $browser=Start-Process -FilePath 'C:/Program Files/Google/Chrome/Application/chrome.exe' -ArgumentList @('--headless=new','--no-sandbox','--no-first-run','--no-default-browser-check','--hide-scrollbars','--mute-audio','--ignore-gpu-blocklist','--use-angle=d3d11','--disable-background-timer-throttling','--disable-renderer-backgrounding','--remote-debugging-port=9484',"--user-data-dir=$profile",'about:blank') -WindowStyle Hidden -PassThru
    try {
      $env:JOS_CDP_EXTERNAL='1'
      $nodeScript=if($Suite -eq 'opening'){'tools/regress-opening.mjs'}else{'tools/accept-speed.mjs'}
      & node $nodeScript @($case.Split(' '))
      if($LASTEXITCODE -ne 0){throw "Regression failed: $Suite $case"}
    } finally {
      if(-not $browser.HasExited){Stop-Process -Id $browser.Id -ErrorAction SilentlyContinue}
      $resolved=[IO.Path]::GetFullPath($profile)
      $expected=[IO.Path]::GetFullPath((Join-Path $siteRoot '.tmp-shots/regress'))
      if((Split-Path -Parent $resolved) -eq $expected -and (Split-Path -Leaf $resolved).StartsWith('profile-')){
        Remove-Item -LiteralPath $resolved -Recurse -Force -ErrorAction SilentlyContinue
      }
    }
  }
} finally { $env:JOS_CDP_EXTERNAL=$prior; Pop-Location }
