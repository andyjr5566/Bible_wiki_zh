#!/usr/bin/env python3
"""Smoke test：用申命記經文當「新章候選」，量 embedding 檢索與 reranker 的參數。

Gold set 的每一筆是「申命記的一段條例 → 已存在於創／出／利／民 的正確條目」。
候選名刻意用申命記的措詞，與目標條目名不同字面——這正是字面比對抓不到、
只有語義層能救的情形（新章開發時每個自建條目都是這種情形）。

只印彙總，不印逐筆原始資料。
"""
import sys, statistics as st
from pathlib import Path
ROOT = Path(__file__).resolve()
sys.path.insert(0, r"c:\Obsidian\Hermes\scripture\util")

from semantic_lookup import SemanticIndex, candidate_query_text, entry_rerank_document
from model_client import rerank_documents

# (候選名（申命記措詞）, 分類, evidence（申命記經文／脈絡）, 正確目標條目)
GOLD = [
 ("見證人先下手用石頭打死", "背景",
  "申17:7「見證人要先下手，然後眾民也下手，將他治死」；申13:6-10 引誘人去事奉別神的，要用石頭打死他。",
  "石刑"),
 ("不可有占卜的交鬼的行巫術的", "主題",
  "申18:10-11「你們中間不可有人使兒女經火，也不可有占卜的、觀兆的、用法術的、行邪術的、用迷術的、交鬼的、行巫術的、過陰的」。",
  "不可偏向交鬼行巫術的"),
 ("兩三個人的口作見證才可定案", "背景",
  "申19:15「人無論犯甚麼罪，都不可憑一個人的口作見證，總要憑兩三個人的口作見證才可定案」；申19:16-19 作假見證的要反坐；申25:2-3 責打以四十下為限。",
  "以色列刑罰的節制與程序保障"),
 ("收割時遺落的禾捆要留給寄居的孤兒寡婦", "主題",
  "申24:19「你在田間收割莊稼，若忘下一捆，不可回去再取，要留給寄居的與孤兒寡婦」；打橄欖樹、摘葡萄也不可再打枝、再摘。",
  "田角拾穗顧念窮人的條例"),
 ("囊中不可有一大一小兩樣的法碼", "主題",
  "申25:13-16「你囊中不可有一大一小兩樣的法碼，你家裡不可有一大一小兩樣的升斗……行非義之事的人都是耶和華你神所憎惡的」。",
  "公道天平法碼升斗"),
 ("不可用牛驢同耕也不可穿羊毛細麻混紡的衣服", "主題",
  "申22:9-11「不可把兩樣種子種在你的葡萄園裡……不可並用牛、驢耕地。不可穿羊毛、細麻兩樣攙雜料做的衣服」。",
  "不可使異類混雜（牲畜種子衣料）"),
 ("不可為死人用刀劃身也不可將額上剃光", "主題",
  "申14:1「你們是耶和華你們神的兒女。不可為死人用刀劃身，也不可將額上剃光」。",
  "不可效法外邦喪儀習俗（剃髮劃身刺花紋）"),
 ("血是生命不可將生命與肉同吃", "神學",
  "申12:23「只是你要心意堅定，不可吃血，因為血是生命；不可將血、就是生命與肉同吃」。",
  "血的尊重"),
 ("要憐愛寄居的因為你們在埃及地也作過寄居的", "主題",
  "申10:19「所以你們要憐愛寄居的，因為你們在埃及地也作過寄居的」。",
  "善待寄居的外人愛他如己"),
 ("以色列的女子中不可有妓女", "主題",
  "申23:17「以色列的女子中不可有妓女；以色列的男子中不可有孌童」。",
  "不可辱沒女兒使她為娼妓"),
 ("當照耶和華所吩咐的孝敬父母使你得福", "神學",
  "申5:16「當照耶和華你神所吩咐的孝敬父母，使你得福，並使你的日子在耶和華你神所賜你的地上得以長久」。",
  "當孝敬父母"),
 ("設立審判官不可屈枉正直不可看人的外貌", "主題",
  "申16:18-20「要在耶和華你神所賜的各城裡，按著各支派設立審判官和官長……不可屈枉正直；不可看人的外貌，也不可受賄賂」。",
  "審判不可行不義按公義審判"),
 ("將兒女用火焚燒獻與他們的神", "主題",
  "申12:31「他們向他們的神行了耶和華所憎嫌所恨惡的一切事，甚至將自己的兒女用火焚燒，獻與他們的神」。",
  "不可使兒女經火歸摩洛"),
 ("頑梗悖逆不聽從父母的兒子", "神學",
  "申21:18-21「人若有頑梗悖逆的兒子，不聽從父母的話……本城的眾人就要用石頭將他打死」。",
  "咒罵父母"),
 ("使瞎子走差路的必受咒詛", "主題",
  "申27:18「使瞎子走差路的，必受咒詛」；申27:16 輕慢父母的必受咒詛。",
  "不可咒罵聾子絆倒瞎子"),
]

idx = SemanticIndex.load()
title_of = [e["title"] for e in idx.entries]

DEPTHS = [5, 10, 20, 30]
queries = [candidate_query_text({"name": n, "suggested_type": t, "evidence": ev}) for n, t, ev, _ in GOLD]
res, _ = idx.query_vectors(queries, top=max(DEPTHS), return_matrix=True)

rank_of, sim_gold, sim_top1, gold_is_top1 = [], [], [], 0
for (n, t, ev, gold), hits in zip(GOLD, res):
    titles = [h[0] for h in hits]
    r = titles.index(gold) + 1 if gold in titles else None
    rank_of.append(r)
    sim_top1.append(hits[0][1])
    sim_gold.append(hits[titles.index(gold)][1] if r else None)
    if r == 1:
        gold_is_top1 += 1

print("=== 第一階段：embedding 檢索 ===")
print(f"gold set {len(GOLD)} 筆（申命記措詞 → 創/出/利/民 既有條目）")
for d in DEPTHS:
    hit = sum(1 for r in rank_of if r and r <= d)
    print(f"  recall@{d:<2} = {hit}/{len(GOLD)}  ({hit/len(GOLD):.0%})")
found = [r for r in rank_of if r]
print(f"  gold 進 top-1：{gold_is_top1}/{len(GOLD)}；找到的名次中位數 {st.median(found):.0f}，最差 {max(found)}")
miss = [GOLD[i][3] for i, r in enumerate(rank_of) if not r]
if miss:
    print(f"  top-{max(DEPTHS)} 內完全找不到：{miss}")

g = [s for s in sim_gold if s is not None]
neg = []
for (n, t, ev, gold), hits in zip(GOLD, res):
    neg += [h[1] for h in hits[:10] if h[0] != gold]
print(f"  相似度：gold 中位數 {st.median(g):.3f}（{min(g):.3f}–{max(g):.3f}）"
      f"｜非 gold 近鄰中位數 {st.median(neg):.3f}（上四分位 {st.quantiles(neg, n=4)[2]:.3f}）")
for thr in (0.55, 0.60, 0.65, 0.70):
    tp = sum(1 for s in g if s >= thr)
    fp = sum(1 for s in neg if s >= thr)
    print(f"    門檻 {thr}: 抓到 gold {tp}/{len(g)}，同時標出 {fp} 個非 gold 近鄰")

print("\n=== 第二階段：reranker ===")
rg, rtop, rmargin, rrank = [], [], [], []
for (n, t, ev, gold), hits in zip(GOLD, res):
    deep = hits[:20]
    docs = [entry_rerank_document(ti, e) for ti, s, e in deep]
    try:
        rr = rerank_documents(queries[GOLD.index((n, t, ev, gold))], docs, task="rerank")
    except Exception as exc:
        print("  rerank 失敗：", exc); break
    order = [deep[i["index"]][0] for i in rr]
    scores = [i["relevance_score"] for i in rr]
    rtop.append(scores[0])
    rmargin.append(scores[0] - scores[1] if len(scores) > 1 else 0.0)
    if gold in order:
        k = order.index(gold)
        rg.append(scores[k]); rrank.append(k + 1)
    else:
        rg.append(None); rrank.append(None)

ok = [i for i, s in enumerate(rg) if s is not None]
r1 = sum(1 for i in ok if rrank[i] == 1)
print(f"  gold 被重排到 top-1：{r1}/{len(ok)}（檢索階段是 {gold_is_top1}/{len(GOLD)}）")
gs = [rg[i] for i in ok]
ns = [rtop[i] for i in ok if rrank[i] != 1]
print(f"  gold 分數：中位數 {st.median(gs):.3f}（{min(gs):.3f}–{max(gs):.3f}）")
if ns:
    print(f"  gold 未奪冠時的 top-1 分數：中位數 {st.median(ns):.3f}（{min(ns):.3f}–{max(ns):.3f}）")
print(f"  Top1-Top2 margin：中位數 {st.median(rmargin):.3f}（{min(rmargin):.3f}–{max(rmargin):.3f}）")
gold_at1 = [rtop[i] for i in ok if rrank[i] == 1]
if gold_at1:
    print(f"  gold 奪冠時的分數：中位數 {st.median(gold_at1):.3f}，最低 {min(gold_at1):.3f}")
