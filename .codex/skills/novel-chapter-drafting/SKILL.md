---
name: novel-chapter-drafting
description: 根据场景卡与当前状态写章节正文：在不回读整书的前提下，优先读取 state+bible+scene-card+相关摘要，产出可连载的章节草稿并落到 novel/draft/chapters/。用于“写/续写/扩写一章、日更、把场景卡写成正文、补充某段剧情并保持一致性与章末钩子”等需求。
---

# 章节写作（novel-chapter-drafting）

## 目标

- 用最小上下文写出“可发布的连载章节草稿”。
- 明确哪里是 canon、哪里是叙事：写正文不等于改设定。

## 输入（优先读取顺序）

1. `novel/summaries/state.md`
2. 本章 `novel/outline/scene-cards/scn-*.md`
3. 相关 `novel/bible/**`（人物/地点/体系/名词）
4. 上一章与相关章摘要 `novel/summaries/chapters/*`
5. 仅在必要时精准回读 `novel/draft/chapters/*`（引用原句/核对冲突）

## 输出（必须落盘）

- `novel/draft/chapters/ch-XXX.md`

## 最短路径工作流（写一章）

1. 确认本章目标：从场景卡提取 Goal/Conflict/Outcome/Beats。
2. 设定“章内节奏”：
   - 开场 10% 快速入戏（冲突/信息增量）
   - 中段升级代价（让推进有重量）
   - 末段落钩子（推动下一章的阅读动机）
3. 严守连续性约束：时间/地点/能力边界/已埋线索（thr-*）。
4. 写出正文（可先粗后细）：先把剧情推进写完整，再润色语气与细节。
5. 若写作中出现“必须新增/改设定”才能成立：暂停正文输出，改为调用 `novel-bible-managing`（必要时登记 decision log），再回来续写。

## 写完后的闭环提醒（DoD）

写完本章后，通常需要继续调用：
- `novel-summarizing`：写章节摘要 + 更新 state
- `novel-thread-tracking`：对账 open threads（新增/回收）
- `novel-continuity-checking`：每 1~3 章做一次 P0/P1/P2 检查（可选但推荐）

