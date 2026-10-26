param(
  [string]$Url = 'http://127.0.0.1:4224/',
  [int]$Port = 9557,
  [string]$QuickBeatId = 'beat-06-beyond-river',
  [switch]$QuickMapCheck,
  [switch]$QuickCrowdCheck,
  [switch]$QuickScrollCheck,
  [switch]$QuickFrameCheck,
  [switch]$OnlyFallback
)

$ErrorActionPreference = 'Stop'
$siteRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$runId = Get-Date -Format 'yyyyMMdd-HHmmss'
$outDir = Join-Path $siteRoot ".tmp-shots/final-acceptance-$runId"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$report = [ordered]@{ url = $Url; output = $outDir; viewports = @(); directory = $null; tutorial = $null; interactions = $null; fallbackBeats = 0; scrollSamples = @(); crowd = @(); dialogues = @(); errors = @() }
$report['sha256'] = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $siteRoot 'dist/index.html')).Hash.ToLowerInvariant()
$pf86 = [Environment]::GetEnvironmentVariable('ProgramFiles(x86)')
$chromePath = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "$pf86\Google\Chrome\Application\chrome.exe",
  "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $chromePath) { throw '找不到 Google Chrome。' }
$profile = Join-Path $env:TEMP "jos24-final-$runId"
$chromeArgs = @(
  '--headless=new', '--no-sandbox', '--disable-dev-shm-usage', '--hide-scrollbars', '--enable-webgl', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader',
  '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--disable-backgrounding-occluded-windows',
  "--remote-debugging-port=$Port", "--user-data-dir=$profile", '--no-first-run', '--disable-extensions', 'about:blank'
)
$chromeProc = Start-Process -FilePath $chromePath -ArgumentList $chromeArgs -WindowStyle Hidden -PassThru
$socket = [System.Net.WebSockets.ClientWebSocket]::new()
$script:cdpId = 0
$script:cdpSocket = $socket

function Invoke-Cdp([string]$Method, [hashtable]$Parameters = @{}) {
  $script:cdpId++
  $currentId = $script:cdpId
  $json = @{ id = $currentId; method = $Method; params = $Parameters } | ConvertTo-Json -Compress -Depth 50
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
  $segment = [System.ArraySegment[byte]]::new($bytes)
  $script:cdpSocket.SendAsync($segment, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, [System.Threading.CancellationToken]::None).GetAwaiter().GetResult() | Out-Null
  while ($true) {
    $memory = [System.IO.MemoryStream]::new()
    do {
      $buffer = [byte[]]::new(8192)
      $recvSegment = [System.ArraySegment[byte]]::new($buffer)
      $received = $script:cdpSocket.ReceiveAsync($recvSegment, [System.Threading.CancellationToken]::None).GetAwaiter().GetResult()
      if ($received.MessageType -eq [System.Net.WebSockets.WebSocketMessageType]::Close) { throw 'Chrome CDP WebSocket 已關閉。' }
      $memory.Write($buffer, 0, $received.Count)
    } while (-not $received.EndOfMessage)
    $message = [System.Text.Encoding]::UTF8.GetString($memory.ToArray()) | ConvertFrom-Json
    if ($message.id -ne $currentId) { continue }
    if ($message.error) { throw "CDP $Method 失敗：$($message.error.message)" }
    return $message
  }
}

function Eval-Js([string]$Expression) {
  $reply = Invoke-Cdp 'Runtime.evaluate' @{ expression = $Expression; returnByValue = $true; awaitPromise = $true; userGesture = $true }
  if ($reply.result.exceptionDetails) { throw "JavaScript 評估失敗：$($reply.result.exceptionDetails.text)" }
  return $reply.result.result.value
}

function Wait-Js([string]$Expression, [int]$TimeoutSeconds = 8) {
  $until = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $until) {
    if (Eval-Js $Expression) { return $true }
    Start-Sleep -Milliseconds 100
  }
  return $false
}

function Click-Js([string]$Selector) {
  $literal = ConvertTo-Json -InputObject $Selector -Compress
  return [bool](Eval-Js "(()=>{const e=document.querySelector($literal);if(!e)return false;e.click();return true})()")
}

function Set-Viewport([int]$Width, [int]$Height, [bool]$Mobile) {
  Invoke-Cdp 'Emulation.setDeviceMetricsOverride' @{ width = $Width; height = $Height; deviceScaleFactor = 1; mobile = $Mobile; screenWidth = $Width; screenHeight = $Height } | Out-Null
  Start-Sleep -Milliseconds 300
}

function Capture-Png([string]$Path) {
  $reply = Invoke-Cdp 'Page.captureScreenshot' @{ format = 'png'; fromSurface = $true; captureBeyondViewport = $false }
  [System.IO.File]::WriteAllBytes($Path, [Convert]::FromBase64String($reply.result.data))
}

function Sample-Scroll([int]$Seconds = 9, [int]$IntervalMs = 80) {
  $times = [System.Collections.Generic.List[double]]::new()
  $positions = [System.Collections.Generic.List[double]]::new()
  $watch = [System.Diagnostics.Stopwatch]::StartNew()
  $nextAt = 0.0
  $durationMs = $Seconds * 1000.0
  while ($watch.Elapsed.TotalMilliseconds -lt $durationMs) {
    $waitMs = $nextAt - $watch.Elapsed.TotalMilliseconds
    if ($waitMs -gt 1) { Start-Sleep -Milliseconds ([int]$waitMs) }
    if ($watch.Elapsed.TotalMilliseconds -ge $durationMs) { break }
    $metrics = Invoke-Cdp 'Page.getLayoutMetrics' @{}
    $times.Add($watch.Elapsed.TotalMilliseconds)
    $positions.Add([double]$metrics.result.cssLayoutViewport.pageY)
    $nextAt += $IntervalMs
  }
  $gaps = @()
  for ($i = 1; $i -lt $times.Count; $i++) { $gaps += ($times[$i] - $times[$i - 1]) }
  return [ordered]@{
    count = $positions.Count
    range = if ($positions.Count) { ($positions | Measure-Object -Maximum).Maximum - ($positions | Measure-Object -Minimum).Minimum } else { 0 }
    minIntervalMs = if ($gaps.Count) { [Math]::Round(($gaps | Measure-Object -Minimum).Minimum, 1) } else { 0 }
    maxIntervalMs = if ($gaps.Count) { [Math]::Round(($gaps | Measure-Object -Maximum).Maximum, 1) } else { 0 }
  }
}

function Set-Beat([string]$BeatId, [double]$Progress = 0.48) {
  $idJson = ConvertTo-Json -InputObject $BeatId -Compress
  $expr = "(()=>{const e=document.querySelector('[data-beat-id='+$idJson+']');if(!e)return false;const r=e.getBoundingClientRect();const y=window.scrollY+r.top-window.innerHeight*.36+Math.max(0,r.height-window.innerHeight*.35)*$Progress;window.scrollTo({top:Math.max(0,Math.min(document.documentElement.scrollHeight-window.innerHeight,y)),behavior:'instant'});return true})()"
  if (-not (Eval-Js $expr)) { throw "找不到故事拍：$BeatId" }
  if (-not (Wait-Js "window.__josState?.beat === '$BeatId'" 6)) { throw "捲動後沒有切到故事拍：$BeatId" }
  if (Eval-Js "document.body.classList.contains('jos-in-stations')&&!document.querySelector('.jos-webgl-fallback-on')") {
    $imagesReady = 'Array.from(document.querySelectorAll(".jos-station-composition")).some(n=>n.dataset.ready==="true"&&Array.from(n.querySelectorAll("img")).every(i=>i.complete&&i.naturalWidth>0))'
    if (-not (Wait-Js $imagesReady 20)) { throw "故事拍 $BeatId 的場景圖層沒有完成載入。" }
  }
}

function Click-TocSegment([string]$SegmentId) {
  $ids = @('prologue', 'act-1', 'act-2', 'act-3', 'act-4', 'act-5', 'act-6', 'epilogue')
  $idx = [Array]::IndexOf($ids, $SegmentId)
  if ($idx -lt 0) { throw "未知目錄段落：$SegmentId" }
  if (-not (Click-Js '[data-coach="toc-btn"]')) { throw '找不到頂列目錄按鈕。' }
  if (-not (Click-Js ".jos-toc-item:nth-child($($idx + 1))")) { throw "找不到目錄段落：$SegmentId" }
  if (-not (Wait-Js "window.__josState?.segment === '$SegmentId'" 12)) { throw "目錄點選後沒有到達段落：$SegmentId" }
}

try {
  $version = $null
  $waitUntil = (Get-Date).AddSeconds(20)
  while ((Get-Date) -lt $waitUntil) {
    try { $version = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/json/version" -TimeoutSec 2; break } catch { Start-Sleep -Milliseconds 200 }
  }
  if (-not $version) { throw 'Chrome DevTools 未啟動。' }
  $target = Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:$Port/json/new?about:blank" -TimeoutSec 5
  $socket.ConnectAsync([Uri]$target.webSocketDebuggerUrl, [System.Threading.CancellationToken]::None).GetAwaiter().GetResult()
  Invoke-Cdp 'Page.enable' @{} | Out-Null
  Invoke-Cdp 'Runtime.enable' @{} | Out-Null

  $devices = if ($OnlyFallback) { @() } else { @(
    @{ name = 'desktop'; width = 1440; height = 900; mobile = $false },
    @{ name = 'mobile-landscape'; width = 844; height = 390; mobile = $true }
  ) }
  foreach ($device in $devices) {
    Set-Viewport $device.width $device.height $device.mobile
    Invoke-Cdp 'Page.navigate' @{ url = $Url } | Out-Null
    if (-not (Wait-Js "document.readyState === 'complete' && document.querySelectorAll('[data-beat-id]').length === 36" 30)) { throw "$($device.name) 網頁未完成載入 36 拍。" }
    Eval-Js "localStorage.setItem('jos24-motion-off','0');window.scrollTo({top:0,behavior:'instant'});true" | Out-Null
    Invoke-Cdp 'Page.reload' @{ ignoreCache = $true } | Out-Null
    if (-not (Wait-Js "window.__josState && document.querySelectorAll('[data-beat-id]').length === 36" 30)) { throw "$($device.name) 重新載入失敗。" }
    $scrollWidth = [int](Eval-Js 'document.documentElement.scrollWidth')
    if ($QuickMapCheck) {
      Set-Beat $QuickBeatId 0.48
      $mapState = Eval-Js '({stateSpace:window.__josState.space,stateCue:window.__josState.cue,stateBeat:window.__josState.beat,stateMotionOff:window.__josState.motionOff,bodyClass:document.body.className,station:document.querySelector(".jos-station-player")?.dataset.station,animation:getComputedStyle(document.querySelector(".jos-station-memory-light")).animationName,playState:getComputedStyle(document.querySelector(".jos-station-memory-light")).animationPlayState,opacity:getComputedStyle(document.querySelector(".jos-station-memory-light")).opacity})'
      $quickDir = Join-Path $outDir "map-check-$QuickBeatId"
      New-Item -ItemType Directory -Force -Path $quickDir | Out-Null
      Start-Sleep -Milliseconds 1500
      Capture-Png (Join-Path $quickDir 'map-a.png')
      Start-Sleep -Seconds 1
      Capture-Png (Join-Path $quickDir 'map-b.png')
      $mapAfter = Eval-Js '({animation:getComputedStyle(document.querySelector(".jos-station-memory-light")).animationName,playState:getComputedStyle(document.querySelector(".jos-station-memory-light")).animationPlayState,opacity:getComputedStyle(document.querySelector(".jos-station-memory-light")).opacity,elapsed:document.getAnimations().map(a=>a.currentTime)})'
      $report.mapMotion = [ordered]@{ before = $mapState; after = $mapAfter }
      $report.status = 'DIAGNOSTIC'
      return
    }
    if ($QuickScrollCheck) {
      Set-Beat 'beat-01-prologue' 0.48
      $report.scrollSamples += [ordered]@{ device = 'desktop'; seconds = 9; intervalMs = 80; data = Sample-Scroll 9 80 }
      $report.status = 'DIAGNOSTIC'
      return
    }
    if ($QuickCrowdCheck) {
      $crowdDir = Join-Path $outDir 'crowd-check'
      New-Item -ItemType Directory -Force -Path $crowdDir | Out-Null
      foreach ($p in @(0.08, 0.32, 0.56, 0.80, 0.90, 1.0)) {
        Set-Beat 'beat-28-dismiss' $p
        Start-Sleep -Milliseconds 250
        $crowdState = Eval-Js '({progress:window.__josState.beatProgress,counts:window.__josScene?.cardDiagnostics()})'
        $report.crowd += [ordered]@{ progress = $p; observedProgress = $crowdState.progress; visibleTribes = $crowdState.counts.visibleTribes; visibleWalkingTribes = $crowdState.counts.visibleWalkingTribes; visibleCards = $crowdState.counts.visibleCards }
        Capture-Png (Join-Path $crowdDir ("p-{0:D2}.png" -f [int]($p * 100)))
      }
      $report.status = 'DIAGNOSTIC'
      return
    }
    if ($QuickFrameCheck) {
      Set-Beat $QuickBeatId
      $frameDir = Join-Path $outDir "frame-$($device.name)-$QuickBeatId"
      New-Item -ItemType Directory -Force -Path $frameDir | Out-Null
      Start-Sleep -Milliseconds 1500
      Capture-Png (Join-Path $frameDir 'a.png')
      Start-Sleep -Seconds 1
      Capture-Png (Join-Path $frameDir 'b.png')
      continue
    }
    $report.viewports += [ordered]@{ name = $device.name; width = $device.width; height = $device.height; scrollWidth = $scrollWidth; beatCaptures = 0; pairDiffPass = 0 }
    if ($scrollWidth -ne $device.width) { $report.errors += "$($device.name) 橫向捲動寬度 $scrollWidth，不等於 $($device.width)" }

    $beats = Eval-Js "Array.from(document.querySelectorAll('[data-beat-id]')).map(e=>({id:e.dataset.beatId}))"
    $deviceDir = Join-Path $outDir $device.name
    New-Item -ItemType Directory -Force -Path $deviceDir | Out-Null
    foreach ($beat in $beats) {
      Set-Beat $beat.id
      Start-Sleep -Milliseconds 1500
      $bubbleSample = '(()=>{const e=document.querySelector(".jos-panel-on .jos-bubble");if(!e)return null;const r=e.getBoundingClientRect();return {x:r.x,y:r.y,text:e.textContent,visible:r.width>0&&r.height>0&&getComputedStyle(e).visibility!=="hidden"}})()'
      $bubbleBefore = if ($beat.id.Contains('-family-')) { Eval-Js $bubbleSample } else { $null }
      Capture-Png (Join-Path $deviceDir "$($beat.id)-a.png")
      Start-Sleep -Seconds 1
      Capture-Png (Join-Path $deviceDir "$($beat.id)-b.png")
      if ($beat.id.Contains('-family-')) {
        $bubbleAfter = Eval-Js $bubbleSample
        $report.dialogues += [ordered]@{ device = $device.name; beat = $beat.id; visible = [bool]($bubbleBefore.visible -and $bubbleAfter.visible); dx = [Math]::Abs($bubbleAfter.x - $bubbleBefore.x); dy = [Math]::Abs($bubbleAfter.y - $bubbleBefore.y); sameText = [bool]($bubbleBefore.text -and $bubbleBefore.text -eq $bubbleAfter.text) }
      }
      $report.viewports[-1].beatCaptures++
      Write-Host "[$($device.name)] $($report.viewports[-1].beatCaptures)/36 $($beat.id)"
    }

    Set-Beat 'beat-28-dismiss' 0.36
    Start-Sleep -Milliseconds 500
    $tribeCount = [int](Eval-Js 'window.__josScene?.cardDiagnostics().visibleTribes ?? 0')
    $walkingTribeCount = [int](Eval-Js 'window.__josScene?.cardDiagnostics().visibleWalkingTribes ?? 0')
    $report.crowd += [ordered]@{ device = $device.name; beat = 'beat-28-dismiss'; visibleTribes = $tribeCount; visibleWalkingTribes = $walkingTribeCount }
    if ($tribeCount -lt 12 -or $walkingTribeCount -lt 12) { $report.errors += "$($device.name) 第28拍畫面可見 $tribeCount/12 群，其中行走 $walkingTribeCount/12 群。" }

    if ($device.name -eq 'desktop') {
      Set-Beat 'beat-01-prologue' 0.48
      $sample = Sample-Scroll 9 80
      $report.scrollSamples += [ordered]@{ device = $device.name; seconds = 9; intervalMs = 80; count = $sample.count; range = $sample.range; minIntervalMs = $sample.minIntervalMs; maxIntervalMs = $sample.maxIntervalMs }
      if ($sample.count -lt 100 -or $sample.range -ne 0 -or $sample.maxIntervalMs -gt 100) { $report.errors += "桌機靜止 9 秒捲動取樣異常：$($sample | ConvertTo-Json -Compress)" }
      $before = [double](Eval-Js 'window.scrollY')
      Click-Js '[data-coach="toc-btn"]' | Out-Null
      Click-Js '[data-coach="toc-btn"]' | Out-Null
      $after = [double](Eval-Js 'window.scrollY')
      if ([Math]::Abs($after - $before) -gt 1) { $report.errors += "目錄開關互動改變 scrollY：$before → $after" }
      Set-Beat 'beat-14-three-gods' 0.45
      $beforeMore = [double](Eval-Js 'window.scrollY')
      Click-Js '.jos-panel-on [data-coach="more-btn"]' | Out-Null
      if (-not (Wait-Js 'window.__josState?.moreOpen' 3)) { throw '更多互動未能開啟小卡。' }
      $afterMore = [double](Eval-Js 'window.scrollY')
      Click-Js '.jos-panel-on [data-coach="more-btn"]' | Out-Null
      $report.interactions = [ordered]@{ menuScrollDelta = [Math]::Abs($after - $before); moreScrollDelta = [Math]::Abs($afterMore - $beforeMore) }
      if ([Math]::Abs($afterMore - $beforeMore) -gt 1) { $report.errors += "更多小卡互動改變 scrollY：$beforeMore → $afterMore" }
      foreach ($id in @('prologue', 'act-1', 'act-2', 'act-3', 'act-4', 'act-5', 'act-6', 'epilogue')) {
        Click-TocSegment $id
        Write-Host "[目錄] $id PASS"
      }
      $report.directory = [ordered]@{ clickableSegments = 8; pass = $true }

      Eval-Js "window.scrollTo({top:0,behavior:'instant'});true" | Out-Null
      Start-Sleep -Milliseconds 500
      if (-not (Click-Js '.jos-coach-trigger')) { throw '找不到新手教學按鈕。' }
      Click-TocSegment 'act-1'
      Click-Js '.jos-coach-bar .jos-primary-btn' | Out-Null
      Click-TocSegment 'act-5'
      Click-Js '.jos-coach-bar .jos-primary-btn' | Out-Null
      Set-Beat 'beat-26-raise' 0.35
      $raiseSelector = ConvertTo-Json -InputObject '[data-coach="raise-btn"]' -Compress
      $raiseExpr = "(()=>{const b=document.querySelector($raiseSelector);if(!b)return false;b.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,pointerId:1,buttons:1}));return true})()"
      if (-not (Eval-Js $raiseExpr)) { throw '找不到立石按鈕。' }
      Start-Sleep -Milliseconds 1900
      Eval-Js "document.querySelector($raiseSelector)?.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerId:1,buttons:0}));true" | Out-Null
      if (-not (Wait-Js 'window.__josState?.raiseStone.done' 3)) { Eval-Js "document.querySelector($raiseSelector)?.dispatchEvent(new KeyboardEvent('keydown',{key:' ',bubbles:true,cancelable:true}));true" | Out-Null }
      if (-not (Wait-Js 'window.__josState?.raiseStone.done' 3)) { throw '新手教學未能完成立石互動。' }
      Click-Js '.jos-coach-bar .jos-primary-btn' | Out-Null
      Click-Js '.jos-coach-bar .jos-primary-btn' | Out-Null
      Set-Beat 'beat-14-three-gods' 0.45
      if (-not (Wait-Js 'document.querySelector(".jos-panel-on [data-coach=more-btn]")' 4)) { throw '找不到更多按鈕。' }
      Click-Js '.jos-panel-on [data-coach="more-btn"]' | Out-Null
      if (-not (Wait-Js 'window.__josState?.moreOpen' 3)) { throw '新手教學未能開啟更多小卡。' }
      Click-Js '.jos-coach-bar .jos-primary-btn' | Out-Null
      Click-TocSegment 'act-2'
      if (-not (Eval-Js 'window.__josState?.moreOpen')) { Click-Js '.jos-panel-on [data-coach="more-btn"]' | Out-Null }
      if (-not (Click-Js '.jos-more-card [data-coach="only-i-btn"]')) { throw '找不到只留下神說我開關。' }
      if (-not (Wait-Js 'window.__josState?.onlyI' 3)) { throw '新手教學未能開啟只留下神說我。' }
      Click-Js '.jos-coach-bar .jos-primary-btn' | Out-Null
      Click-Js '.jos-coach-bar .jos-primary-btn' | Out-Null
      if (-not (Click-Js '[data-coach="thread-rail"]')) { throw '找不到事奉線互動。' }
      Click-Js '.jos-coach-bar .jos-primary-btn' | Out-Null
      Click-Js '[data-coach="toc-btn"]' | Out-Null
      if (-not (Click-Js '.jos-toc-popover .jos-secondary-btn')) { throw '找不到前往整理區的目錄按鈕。' }
      if (-not (Wait-Js 'document.querySelector("[data-coach=jump-story-btn]")' 8)) { throw '整理區沒有故事跳轉按鈕。' }
      Click-Js '[data-coach="jump-story-btn"]' | Out-Null
      if (-not (Wait-Js 'window.__josState?.returnSpot' 3)) { throw '整理區跳回故事沒有建立返回書籤。' }
      Click-Js '.jos-coach-bar .jos-primary-btn' | Out-Null
      Click-Js '.jos-return-btn' | Out-Null
      if (-not (Wait-Js '!window.__josState?.returnSpot' 3)) { throw '返回書籤未能完成。' }
      Click-Js '.jos-coach-bar .jos-primary-btn' | Out-Null
      Click-Js '.jos-coach-bar .jos-primary-btn' | Out-Null
      $coachHidden = [bool](Eval-Js 'document.querySelector(".jos-coach-bar")?.classList.contains("jos-coach-hidden")')
      $report.tutorial = [ordered]@{ stages = 3; clickThrough = $coachHidden }
      if (-not $coachHidden) { $report.errors += '三段新手教學沒有完成收合。' }
    }
  }

  if ($QuickFrameCheck) { $report.status = 'DIAGNOSTIC'; return }

  if (-not $OnlyFallback) {
    Set-Viewport 844 390 $true
    Invoke-Cdp 'Page.navigate' @{ url = $Url } | Out-Null
    if (-not (Wait-Js "document.querySelectorAll('[data-beat-id]').length === 36" 20)) { throw '手機橫向重新載入失敗。' }
    $mobileSample = Sample-Scroll 9 80
    $report.scrollSamples += [ordered]@{ device = 'mobile-landscape'; seconds = 9; intervalMs = 80; count = $mobileSample.count; range = $mobileSample.range; minIntervalMs = $mobileSample.minIntervalMs; maxIntervalMs = $mobileSample.maxIntervalMs }
    if ($mobileSample.count -lt 100 -or $mobileSample.range -ne 0 -or $mobileSample.maxIntervalMs -gt 120) { $report.errors += "手機橫向靜止 80ms 捲動取樣異常：$($mobileSample | ConvertTo-Json -Compress)" }

    Set-Viewport 390 844 $true
    Invoke-Cdp 'Page.navigate' @{ url = $Url } | Out-Null
    if (-not (Wait-Js "document.querySelectorAll('[data-beat-id]').length === 36" 20)) { throw '手機直向重新載入失敗。' }
    $portrait = Eval-Js '({width:document.documentElement.scrollWidth,hint:getComputedStyle(document.querySelector(".jos-rotate-hint")).display,text:document.querySelector(".jos-rotate-hint")?.innerText})'
    $report.portrait = $portrait
    if ($portrait.width -ne 390 -or $portrait.hint -eq 'none') { $report.errors += "手機直向轉向提示或捲動寬度錯誤：$($portrait | ConvertTo-Json -Compress)" }
  }

  $inject = "HTMLCanvasElement.prototype.getContext = new Proxy(HTMLCanvasElement.prototype.getContext,{apply(target,thisArg,args){if(['webgl','webgl2','experimental-webgl'].includes(String(args[0]).toLowerCase()))return null;return Reflect.apply(target,thisArg,args)}})"
  Invoke-Cdp 'Page.addScriptToEvaluateOnNewDocument' @{ source = $inject } | Out-Null
  Set-Viewport 1440 900 $false
  Invoke-Cdp 'Page.navigate' @{ url = $Url } | Out-Null
  if (-not (Wait-Js "window.__josScene === null && document.querySelector('.jos-webgl-fallback-on')" 20)) { throw '無 WebGL 模式沒有啟用靜止插圖。' }
  $fallbackDir = Join-Path $outDir 'webgl-off'
  New-Item -ItemType Directory -Force -Path $fallbackDir | Out-Null
  $fallbackBeats = Eval-Js "Array.from(document.querySelectorAll('[data-beat-id]')).map(e=>e.dataset.beatId)"
  foreach ($beatId in $fallbackBeats) {
    Set-Beat $beatId
    Start-Sleep -Milliseconds 500
    $count = [int](Eval-Js "document.querySelector('.jos-fallback-svg')?.querySelectorAll('.jos-fallback-figure').length ?? 0")
    $actualBeat = Eval-Js "document.querySelector('.jos-fallback-svg')?.getAttribute('data-beat')"
    if ($count -lt 1 -or $actualBeat -ne $beatId) { $report.errors += "無 WebGL 靜止剪影缺少：$beatId（圖像 $count 張，畫面拍 $actualBeat）" }
    Capture-Png (Join-Path $fallbackDir "$beatId.png")
    $report.fallbackBeats++
  }
  $report.dialogues | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 (Join-Path $outDir 'dialogues.json')
  $diffText = & python -I (Join-Path $PSScriptRoot 'compare-shot-pairs.py') $outDir
  $diffReport = ($diffText -join [Environment]::NewLine) | ConvertFrom-Json
  foreach ($viewport in $report.viewports) {
    $diff = $diffReport.($viewport.name)
    $viewport.pairDiffPass = $diff.pairs
    $viewport.minChangedPixelsPercent = [Math]::Round($diff.minChangedPixels * 100, 3)
    if (-not $diff.pass) { $report.errors += "$($viewport.name) 截圖差異未達標：$($diff.pairs)/36 拍通過，最低變化 $($viewport.minChangedPixelsPercent)%" }
  }
  if ((Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $siteRoot 'dist/index.html')).Hash.ToLowerInvariant() -ne $report.sha256) { $report.errors += '成品在驗收期間改變。' }
  $report.status = if ($report.errors.Count -eq 0) { 'PASS' } else { 'FAIL' }
} catch {
  $report.status = 'FAIL'
  $report.errors += $_.Exception.Message
  Write-Error $_
} finally {
  try { $socket.Dispose() } catch {}
  try {
    Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($profile) } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
  } catch { try { Stop-Process -Id $chromeProc.Id -Force -ErrorAction SilentlyContinue } catch {} }
  $report | ConvertTo-Json -Depth 20 | Set-Content -Encoding UTF8 (Join-Path $outDir 'report.json')
  $report | ConvertTo-Json -Depth 20 | Write-Output
}
