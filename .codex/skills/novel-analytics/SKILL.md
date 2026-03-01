---
name: novel-analytics
description: 小说数据统计与健康度观察：统计字数/章长分布、更新进度、（可选）POV/角色出场粗略频次，并输出简报，帮助连载控节奏。用于“统计字数、看进度、检查章长是否稳定、做卷末复盘与节奏校正”等需求。
---

# 数据统计（novel-analytics）

## 目标

- 用数据回答“写到哪了、写得稳不稳、章长与节奏有没有飘”。

## 输入

- 章节草稿：`draft/chapters/ch-*.md`

## 输出

- 统计报告（默认写入）：`reports/analytics/report-YYYYMMDD.md`

## 最短路径工作流

在项目根目录执行：

```bash
python .codex/skills/novel-analytics/scripts/novel_analytics.py --root .
```

常用参数：

- 按卷统计：`--volume vol-01`（从 `outline/volumes/vol-01.md` 读取 `range`）
- 按章节范围：`--ch-from 1 --ch-to 80`

## 注意

- 本统计不做“文学评价”，只给可执行的节奏信号（例如章长波动过大）。
- 若你在工作区根目录内运行：通常加 `--novel-dir .`。
