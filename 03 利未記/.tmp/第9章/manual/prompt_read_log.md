# Prompt 讀取回執：利未記 第9章

## manual/entry_batch_1.prompt.md
- 引句：你是聖經研經資料整理員，並且輸出以繁體中文為主。任務：一次為以下 1 個 link_folder 條目各填一份 entry_content payload
- 引句：所有 commentary 敘述仍必須忠於上述已全文閱讀來源；不得以摘要或關鍵字 grep 取代全文閱讀
- 引句：definition 裡的希伯來字母寫法／音譯同樣必須出現在上述來源中，來源沒給就不要寫
- 引句：status 一律 formal。accumulations 是「物件陣列」，每項含 book、chapter、summary、relation 四欄

## manual/chapter_content.prompt.md
- 引句：依本章段落結構分成至少 3 個小節，每小節以「### 標題（vX-Y）」開頭
- 引句：各家彼此矛盾時要並陳，不要壓平成單一說法
- 引句：STEP 的詞形、Strong、morphology、context gloss 或 lexicon 義域請明標為 STEP語言資料，不要寫成某位註釋家的觀點
- 引句：不要寫「參考資料」清單——程式會自動附上來源 URL
