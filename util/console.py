"""Windows 主控台 UTF-8 保險絲。

本庫所有 CLI 輸出含中文與 emoji；Windows 上 stdout/stderr 預設 cp1252，
print 會 UnicodeEncodeError（管線重導向下也一樣）。每個 CLI 入口在
argparse 之前呼叫 utf8_stdio()，不必依賴外部 PYTHONUTF8 環境變數。
"""
import sys


def utf8_stdio():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
