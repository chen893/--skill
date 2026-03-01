---
name: novel-scene-planning
description: 生成与维护场景卡（scene cards）：把大纲拆成可执行的章内场景（Goal/Conflict/Outcome/Beats/伏笔/连续性约束），并在 frontmatter 标注 chapter/time/location/pov 与 threads_open/threads_close。用于“拆章、做分镜、规划本章怎么写、设计章末钩子/爽点、把接下来 1~3 章拆成可写的场景卡”等需求。
---

# 场景卡规划（novel-scene-planning）

## 目标

- 把“写一章”拆成可执行的场景卡，降低日更写崩概率。
- 场景卡必须能被 `novel-chapter-drafting` 直接拿来写正文。

## 最短路径工作流

1. 读取输入（按需）：
   - `outline/master-outline.md`
   - `outline/arcs/*`
   - `summaries/state.md`
   - `continuity/open-threads.md`
2. 为目标章节创建/更新场景卡：`outline/scene-cards/scn-*.md`
3. 如涉及新线索：在场景卡 frontmatter 的 `threads_open/threads_close` 标出 `thr-*`（并提醒章后用 `novel-thread-tracking` 对账）。

## 输出要求（必须落盘）

- `outline/scene-cards/scn-*.md`
- 场景卡里必须包含：Goal / Conflict / Outcome / Beats / 伏笔信息 / 连续性约束

## 模板

复制 `assets/scene-card-template.md` 作为起点，然后填空即可。

## 注意

- 不要把场景卡写成“正文草稿”，它只负责可执行的计划。
- 连续性约束要写清：时间、地点、能力边界、已承诺的线索（thr-*）等。
- 实体引用（地点/人物 POV 等）使用 `char-中文名`、`loc-中文名` 这类中文 ID，禁止用拼音做 ID。
