param([string]$script, [string]$argline = "")
# usage: powershell -File scripts\blender\run_blender.ps1 scripts\blender\epic_cover.py "--w 1280 --h 720 --out x.png"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $root
$rest = @()
if ($argline -ne "") { $rest = $argline -split " " }
$log = & "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python $script -- @rest 2>&1
$log | Select-Object -Last 40 | ForEach-Object { "$_" }
