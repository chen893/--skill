---
name: novel-continuity-checking
description: 连续性与一致性检查：核对时间线、地理移动、年龄季节昼夜、能力边界、人物关系、专名统一与线索回收逻辑，输出 P0/P1/P2 问题清单与最小修复策略。用于“查错/对账/发现设定冲突/担心吃书/每 1~3 章例行 QA/卷末大修前复检”等需求。
---

# 连续性检查（novel-continuity-checking）

## 目标

- 把“可能穿帮的点”在早期打掉，避免长篇后期一炸一大片。
- 只输出问题清单与修复策略；正文修改通常交给 `novel-editing` 执行。

## 输入（按需读取）

- `continuity/timeline.md`
- `continuity/constraints.md`
- `continuity/open-threads.md`
- `continuity/issues.md`
- 若检查范围包含“整卷”：再读
  - `outline/volumes/vol-XX.md`
  - `outline/volumes/vol-XX-beat-sheet.md`
- 相关 `bible/**`
- 目标章节：优先读摘要，必要时精准回读正文

## 输出（必须落盘）

- `reports/continuity/report-YYYYMMDD.md`
- 必要时更新：`continuity/issues.md`（把冲突变成可追踪待办）

## 最短路径工作流

1. 明确检查范围（章节/卷/某条弧）。
2. 先查硬约束（constraints、体系规则、人物底线），再查时间线与线索对账。
   - 若是卷末复检：对照卷规划里承诺的 `threads_close` 与 open-threads 实际状态，防止“该收不收/提前泄底/回收不呼应”
3. 分级输出问题：
   - P0：不修必穿帮（时间线不可能、能力边界破坏、人物动机反转无铺垫）
   - P1：建议修（节奏拖沓、信息重复、专名不统一）
   - P2：记录即可（未来可能用到的风险点）
4. 给出“最小改动方案”：优先改正文；如必须改 canon，写明需要更新哪些 bible，并建议走 `novel-retcon-managing`。

## 模板

复制 `assets/continuity-report-template.md` 作为报告起点。
