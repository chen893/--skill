---
name: novel-analytics
description: 小说数据统计与健康度观察：统计字数/章长分布、更新进度、（可选）POV/角色出场粗略频次，并输出简报，帮助连载控节奏。用于“统计字数、看进度、检查章长是否稳定、做卷末复盘与节奏校正”等需求。
---

# 数据统计（novel-analytics）

## 目标

- 用数据回答“写到哪了、写得稳不稳、章长与节奏有没有飘”。

## 输入

- 章节草稿：`WORKDIR/draft/chapters/ch-*.md`（WORKDIR 为工作区目录名，默认 `novel`）

## 输出

- 统计报告（默认写入）：`WORKDIR/reports/analytics/report-YYYYMMDD.md`

## 最短路径工作流

在项目根目录执行：

```bash
python .codex/skills/novel-analytics/scripts/novel_analytics.py --root .
```

## 注意

- 本统计不做“文学评价”，只给可执行的节奏信号（例如章长波动过大）。
- 若工作区目录名不是 `novel`：运行时加 `--novel-dir WORKDIR`。
