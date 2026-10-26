param(
    [ValidateSet('preview','final')][string]$mode = 'preview',
    [string[]]$scenes = @('beyond-river','isaac','esau-jacob','egypt','wilderness','east','moab','jordan','canaan'),
    [int]$samples = 32
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Set-Location -LiteralPath $root
$w = 1920; $h = 1080
if ($mode -eq 'preview') { $w = 1280; $h = 720 }
foreach ($scene in $scenes) {
    $work = Join-Path $root "lab\renders\layers\_work\$mode\$scene"
    $out = Join-Path $root "lab\renders\layers\$scene"
    if ($mode -eq 'preview') { $out = Join-Path $root "lab\renders\layers\_work\previews\$scene" }
    New-Item -ItemType Directory -Force -Path $work | Out-Null
    $watch = [System.Diagnostics.Stopwatch]::StartNew()
    Write-Output "START $mode $scene"
    $log = & 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b --factory-startup --gpu-backend opengl --python (Join-Path $PSScriptRoot 'epic_plates_stations.py') -- --scene $scene --w $w --h $h --samples $samples --out $work 2>&1
    $renderExit = $LASTEXITCODE
    $log | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $work 'blender.log')
    if ($renderExit -ne 0) { $log | Select-Object -Last 30; throw "Blender failed: $scene" }
    & python -I (Join-Path $PSScriptRoot 'epic_station_post.py') $scene --work $work --out $out
    if ($LASTEXITCODE -ne 0) { throw "Post failed: $scene" }
    $watch.Stop()
    $infoPath = Join-Path $out 'render-info.json'
    $info = Get-Content -Raw -Encoding UTF8 -LiteralPath $infoPath | ConvertFrom-Json
    $info | Add-Member -NotePropertyName wall_seconds -NotePropertyValue ([Math]::Round($watch.Elapsed.TotalSeconds,2)) -Force
    $info | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 -LiteralPath $infoPath
    Write-Output "DONE $mode $scene $($info.wall_seconds)s"
}
