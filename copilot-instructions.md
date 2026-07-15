# Hermes Scripture 專案 Agent 指令

## 終端機執行規則

本專案的 Python 腳本（`util/run_chapter.py`、`util/build_link_index.py`、
`util/verify_links.py`、`util/validate_knowledge_base.py`、`util/link_quality_check.py`）
執行時間可能長達數分鐘，但都是一次性命令（one-shot），**不是**需要持續運行的服務。

執行這些腳本時，**必須使用 `mode=sync`**（同步模式），讓 Agent 等待命令完成後
取得完整輸出，**禁止使用 `mode=async`**（背景模式）。

背景模式會導致 Agent 反覆呼叫 API 輪詢狀態，浪費 token 且拖慢流程。
同步模式一次等待到底，取得完整輸出，效率最高。

## 章節製作流程

執行 `run_chapter.py` 時，使用同步模式：
```
python util/run_chapter.py <書卷> <章節>
```

完成後依序執行驗證鏈（全部同步）：
1. `python util/build_link_index.py`
2. `python util/validate_knowledge_base.py`
3. `python util/link_quality_check.py`
4. `python util/verify_links.py`