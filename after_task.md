worker 開工前，這一章的 .tmp/第x章/ 要備齊四樣，缺一它就會靜默失效或半途卡住：

檔案	誰產的	狀態要求
raw_data/{source}_{book}_{chapter} ×4	crawl_bible_text.py	四來源都爬到，source_manifest 標 OK
.tmp/第x章/source_manifest.md	build_source_manifest.py {書名} X	不可手寫；標「缺檔」要先補爬
.tmp/第x章/link_candidates.yaml	你判斷定稿	候選名無斜線、type 是 link_folder/ 真實資料夾
.tmp/第x章/candidate_similarity.md	semantic_lookup.py --candidates {書名} X	候選定稿後才跑，是最後一道事前攔截
一行驗證交接包完整（缺哪步它會指回哪裡）：


python util/check_chapter_files.py {書名} {X}
注意：如果它回報缺 candidates 或 similarity，代表前置包沒備齊——這是你的判斷工作，worker 不該自己補候選（會犯方向書列的斜線名／亂造分類那些靜默坑）。

Worker 起手 prompt（可直接貼，換 {書名}/{X}）

你要接手【{書名} 第{X}章】的知識連結流程。link_candidates.yaml 已由上游判斷定稿，
你的任務是走 agent_start_prompt.md 的步驟3–8 把這章做完並驗證通過，不要重做候選。

治理規範：完整讀 C:\Obsidian\Hermes\scripture\agent_start_prompt.md，一切照它走；
所有輸出用繁體中文（英文來源 KC/BH 要譯不要貼原文）。

前置狀態（已備好，不要重做，也不要動 link_candidates.yaml）：
  raw_data 四來源、.tmp/第{X}章/{source_manifest.md, link_candidates.yaml, candidate_similarity.md}

開工前先驗前置包：python util/check_chapter_files.py {書名} {X}
  ——若它說缺 candidates/similarity，代表前置包沒備齊，停下回報上游，不要自己補候選。

步驟3–4：
  python util/build_link_index.py
  python util/run_chapter.py {書名} {X}
  python util/link_updates.py prepare {書名} {X}
  → 回經文與四來源原文填 link_updates.yaml 的 summary/relation（繁中）
  python util/link_updates.py apply {書名} {X} --dry-run
  python util/link_updates.py apply {書名} {X}      （重跑須 0 變更）

步驟6 勘誤複核（閘門全過≠內容忠實，commit 前必做）：
  逐條把「本章整理、新建條目、B類累積」回四來源核對，抓四類錯——
  來源誤植、全稱詞/方向性誤讀、腦補的經文交叉引註、查無出處的格言式總結句。
  source of truth 是 .tmp 裡的 yaml（chapter_content.yaml / entry_content/*.yaml），
  不是渲染出的 .md；改 yaml 後重跑 run_chapter 讓 render 帶出。
  改 entry_content 會連帶作廢並重生 chapter_content——本章整理要重查一遍。
  解經爭議類條目只能陳述四來源實際立場，不可自編解經史/學者/教父。

步驟7–8 收尾（全 PASS 才 commit）：
  python util/build_fhl_maps.py
  python util/check_existing_links.py 【{序號 書名}】/第{X}章.md --missing
  python util/build_link_index.py
  python util/build_embedding_index.py
  python util/validate_knowledge_base.py
  python util/link_quality_check.py {書名}
  python util/verify_links.py {書名}          ← 離線掃描（不需開 Obsidian）；用 Obsidian 解析規則（確切檔名、不認 alias）抓 broken，逮得到 [[按手]] 這類 alias 漏網之魚
  python util/audit_knowledge_base.py --check-due
  python util/check_chapter_files.py {書名} {X}
  commit 前跑 git status，把它列的「本章待 git add」新建 link_folder/**.md 一併加入；
  一章一 commit，訊息寫清楚本章做了什麼；不要 git add 整個 link_folder。
