---
name: novel-thread-tracking
description: 线索/伏笔/承诺追踪：维护 open threads 表格（thr-*），登记首次出现卷/章节、状态、预计回收卷/窗口与回收卷/章节，并与章节摘要 threads_open/threads_close 对账。用于“挖坑/填坑、伏笔管理、承诺回收窗口安排、检查是否漏回收或提前泄底”等需求，尤其适合连载日更。
---

# 线索追踪（novel-thread-tracking）

## 目标

- 把“作者对读者的承诺”显式化：可追踪、可对账、可回收。
- 防止长篇常见事故：忘坑、烂尾、提前泄底、回收时对不上原伏笔。

## 权威文件

- `continuity/open-threads.md`：线索表格（权威源）
- `summaries/chapters/ch-XXX-summary.md`：每章 threads_open/threads_close（对账源）

## 最短路径工作流

1. 读取本章摘要的 `threads_open/threads_close`。
2. 更新 `open-threads.md` 表格：
   - 新线索：补全 `thread_id/title/type/首次出现卷/首次出现/预计回收卷/预计回收窗口/依赖`
   - 回收线索：填 `回收卷/回收章节`，把 `状态` 改为 `closed`
3. 对账规则：摘要里出现的 thr-* 必须在表格里可查；表格里状态变更必须能定位到章节。
4. 不确定/冲突：写 TODO 并同步到 `continuity/issues.md`。

## 模板

如缺少 `open-threads.md`，复制 `assets/open-threads-template.md` 到 `continuity/open-threads.md`。

## 注意

- `预计回收窗口` 用于节奏管理，不是硬承诺；但要尽量兑现，否则读者信任会下降。
- 回收时尽量呼应原伏笔的“暗示方式”，避免强行圆。
