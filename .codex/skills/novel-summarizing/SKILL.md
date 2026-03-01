---
name: novel-summarizing
description: 生成分层摘要并维护 state：为章节输出 ch-XXX-summary.md，更新 summaries/state.md 的当前态，并同步记录 threads_open/threads_close 以支撑长篇“记忆系统”。用于“写完一章后的收尾闭环、回顾梳理、减少回读正文、为下一章准备最小上下文”等需求。
---

# 摘要与状态维护（novel-summarizing）

## 目标

- 用最小信息保存长篇关键状态，让后续写作不靠“把整书塞进上下文”。
- 让线索与设定变化可追溯：摘要里明确本章发生了什么、谁变了、开了/收了哪些线索。

## 输入（按需）

- 本章正文：`draft/chapters/ch-XXX.md`
- 相关场景卡：`outline/scene-cards/scn-*.md`（若有）
- 现有 state：`summaries/state.md`
- open threads：`continuity/open-threads.md`

## 输出（必须落盘）

- `summaries/chapters/ch-XXX-summary.md`
- `summaries/state.md`

## 最短路径工作流

1. 生成本章摘要（按模板 5~10 条要点）。
2. 提取人物状态变化（用人物 ID 标注，避免同名混乱；人物 ID 使用 `char-中文名`，不要用拼音）。
3. 记录新增/更新设定（只写“发生了什么变化”，细节落 bible）。
4. 列出 `threads_open` / `threads_close`（与 open-threads 表格对账）。
5. 更新 `state.md`：推进章节范围、时间线、地点、POV、主线现状与近期目标。

## 模板

可复制：
- `assets/chapter-summary-template.md`
- `assets/state-template.md`
