param([switch]$Baseline)
$ErrorActionPreference = 'Stop'
$siteRoot = Split-Path -Parent $PSScriptRoot
$tempRoot = [IO.Path]::GetFullPath((Join-Path $siteRoot '.tmp-shots/fix1'))
$owned = @()
Push-Location $siteRoot
try {
  foreach ($port in @(9394,9395)) {
    $profile = Join-Path $tempRoot ('jos-shoot-fix1-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $profile | Out-Null
    $process = Start-Process -FilePath 'C:/Program Files/Google/Chrome/Application/chrome.exe' -ArgumentList @(
      '--headless=new','--no-sandbox','--no-first-run','--no-default-browser-check','--hide-scrollbars','--mute-audio',
      "--remote-debugging-port=$port","--user-data-dir=$profile",'about:blank'
    ) -WindowStyle Hidden -PassThru
    $owned += @{path=$profile;process=$process}
  }
  Write-Output 'Chrome started; connecting CDP.'
  if ($Baseline) { & node tools/shoot-fix1.mjs baseline }
  else { & node tools/shoot-fix1.mjs }
  if ($LASTEXITCODE -ne 0) { throw "CDP acceptance failed ($LASTEXITCODE)" }
} finally {
  foreach ($item in $owned) {
    if (-not $item.process.HasExited) { Stop-Process -Id $item.process.Id -ErrorAction SilentlyContinue }
    $resolved = [IO.Path]::GetFullPath($item.path)
    if ($resolved.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase) -and (Split-Path -Leaf $resolved).StartsWith('jos-shoot-fix1-')) {
      Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($resolved) } | ForEach-Object {
        Stop-Process -Id $_.ProcessId -ErrorAction SilentlyContinue
      }
      Start-Sleep -Milliseconds 300
      Remove-Item -LiteralPath $resolved -Recurse -Force -ErrorAction SilentlyContinue
    }
  }
  Pop-Location
}
