$root = (Resolve-Path -LiteralPath 'link_folder').Path
$pattern = '(?m)^(?:\s*-?\s*raw_data\s*[\uFF1A:].*|\s*-\s*\u4F86\u6E90\s*[\uFF1A:]\s*\u898B\u672C\u689D\u76EE\u300C\u4F86\u6E90\u4F9D\u64DA\u300D\s*|\s*-\s*(?:\u89F8\u767C\u4F86\u6E90|\u4F86\u6E90\u6A94\u6848)(?:\s*[\uFF1A:].*)?\s*)(?:\r?\n|$)'

$filesChanged = 0
$linesRemoved = 0

Get-ChildItem -LiteralPath $root -Recurse -File -Filter '*.md' | ForEach-Object {
    $path = $_.FullName
    if (-not $path.StartsWith(
        $root + [IO.Path]::DirectorySeparatorChar,
        [StringComparison]::OrdinalIgnoreCase
    )) {
        throw "Path escaped link_folder: $path"
    }
    $text = [IO.File]::ReadAllText($path)
    $count = [regex]::Matches($text, $pattern).Count
    if ($count -gt 0) {
        $updated = [regex]::Replace($text, $pattern, '')
        [IO.File]::WriteAllText($path, $updated, [Text.UTF8Encoding]::new($false))
        $filesChanged++
        $linesRemoved += $count
    }
}

"FILES_CHANGED=$filesChanged"
"LINES_REMOVED=$linesRemoved"
