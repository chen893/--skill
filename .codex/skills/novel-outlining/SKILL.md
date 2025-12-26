---
name: novel-outlining
description: 产出并维护小说大纲：总纲（主线/支线/主题承诺/终局）、分卷规划、人物弧（arc-*）与章节推进节拍建议。用于用户提出“做大纲/拆分卷章/规划主线支线/设置反转与钩子/确定终局与主题承诺”等需求，或写作中期需要校正节奏与方向时。
---

# 小说大纲规划（novel-outlining）

## 目标

- 把“长期方向”落到 `novel/outline/`，避免连载写着写着漂移。
- 把“承诺-回收”和“节奏节点”显式化，便于后续场景卡与写章执行。

## 最短路径工作流

1. 读取约束与现状（按需）：
   - `novel/config/novel.yaml`
   - `novel/bible/style-guide.md`
   - `novel/summaries/state.md`（若已有）
   - `novel/decisions/decision-log.md`（若已有）
2. 输出总纲：`novel/outline/master-outline.md`（用模板快速落盘）。
3. 按主线/人物弧拆 `novel/outline/arcs/arc-*.md`（每条弧写“起点→转折→代价→终局”）。
4. 给出接下来 3~10 章的“章节推进要点”（不写场景卡细节；细节交给 `novel-scene-planning`）。

## 输出要求（必须落盘）

- `novel/outline/master-outline.md`
- `novel/outline/arcs/arc-*.md`（如适用）
- 如出现“必须新增/修改设定”才能成立：列出需要调用 `novel-bible-managing` 的条目清单

## 写作约束（写大纲时就要想清楚）

- 每卷要有明确的“卷目标、卷代价、卷终局、卷钩子”。
- 主线承诺必须能回收（否则烂尾风险上升）。
- 避免“无限加设定”：任何新体系规则都要写代价与边界（并落 bible）。

## 模板

可复制：
- `assets/master-outline-template.md`
- `assets/arc-template.md`

