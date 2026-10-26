param(
    [ValidateSet('preview','final')][string]$mode = 'final',
    [int]$samples = 32
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Set-Location -LiteralPath $root
$blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
if (-not (Test-Path -LiteralPath $blender)) { throw "Blender 5.2 not found: $blender" }
$w = 4096; $h = 2048
if ($mode -eq 'preview') { $w = 1024; $h = 512; $samples = [Math]::Min($samples, 12) }
$base = Join-Path $root 'lab\renders\shechem'
$work = Join-Path $base "_work\$mode"
$out = $base
if ($mode -eq 'preview') { $out = Join-Path $base '_work\previews' }
New-Item -ItemType Directory -Force -Path $work,$out | Out-Null
Write-Output "START Shechem $mode $w x $h"
& $blender -b --factory-startup --gpu-backend vulkan --python-exit-code 1 --python (Join-Path $PSScriptRoot 'shechem_panorama.py') -- --out $work --w $w --h $h --samples $samples
if ($LASTEXITCODE -ne 0) { throw 'Blender panorama render failed.' }
& python -I (Join-Path $PSScriptRoot 'shechem_panorama_post.py') --work $work --out $out --w $w --h $h
if ($LASTEXITCODE -ne 0) { throw 'Panorama postprocess or line check failed.' }
Write-Output "DONE Shechem $mode -> $out"
