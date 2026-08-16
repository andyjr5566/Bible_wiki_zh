# Prompt 讀取回執：創世記 第27章

## manual/entry_batch_1.prompt.md
- 引句：你是聖經研經資料整理員，並且輸出以繁體中文為主。任務：一次為以下 1 個 link_folder 條目各填一份 entry_content payload。
- 引句：status 一律 formal。accumulations 是「物件陣列」，每項含 book、chapter、summary、relation 四欄，且至少含本章（創世記 第27章）一筆、同章只給一筆。
- 引句：【輸出】只輸出一個 YAML 陣列（每個元素以 - 開頭），不要任何說明文字。欄位定義見 payload 欄位：name, type, secondary_types, aliases, status, definition, development, accumulations, related_entries, sources, created_from, category, trigger_sources, current_data, pending。詳見 _config/schemas/entry_content.schema.json。
